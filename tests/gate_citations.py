#!/usr/bin/env python3
"""Gate CITATIONS: every repo path a document cites must exist.

Written 2026-08-06 after two citation defects in two days. One was a paper
mis-read (a 1998 PDF written off as a scan without opening it); the other was
`results/beyond-polyplets.md` citing `results/cloud-investigation-2026-07-07.md`,
a file that has never existed in this repo -- the name belongs to an entry in
Claude's memory directory, and `docs/utilization-bottleneck-log.md` cites it
correctly as `[[cloud-investigation-2026-07-07]] in memory`. A memory note is
not a repo artifact and cannot be cited by a paper. The same sweep turned up
`results/pgo-no-go` and `results/reach-scaling-and-resourcing.md`, two more
memory names written as paths.

The check: pull every backticked repo-ish path out of every tracked markdown
file and classify it.

  exists     on disk now -- fine
  template   contains a placeholder ({}, <>, *, ?, $, :) -- not a citation
  exempt     the citing line marks it (deleted / removed / planned / TODO /
             deliverable / never existed / in memory), so the text already
             tells the reader not to look for it
  history    gone from the tree but present in git history -- reported, and
             allowed: the repo deletes scaffolding on purpose, and
             `git show <rev>^:path` is a legitimate citation
  MISSING    none of the above -- FAILS the gate

MISSING is the class that catches a name that never existed, which is what a
memory-name-as-path always is.

RED control: a synthetic document citing `results/definitely-not-here.md` must
land in MISSING, and one citing it on a line that says "deleted" must not.

Usage: python3 tests/gate_citations.py [--verbose]
"""
import argparse
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Top-level directories that make a backticked token a repo path rather than
# prose. `runs/` and `build/` are deliberate omissions: they are run outputs,
# not artifacts, and citing them is not a claim that they are in the tree.
TOP = ("results", "docs", "experiments", "scripts", "tests", "cpp", "core",
       "polyplets", "papers", "paper", "oeis", "go", "orchestrator")
PATH_RE = re.compile(r"`((?:" + "|".join(TOP) + r")/[^`\s]+)`")
PLACEHOLDER = set("{}<>*?$:")
EXEMPT_WORDS = ("deleted", "removed", "planned", "todo", "deliverable",
                "never existed", "no such file", "in memory", "not a path",
                "since removed", "to be written")
EPHEMERAL_RE = re.compile(r"^(runs|build)/|^results/(ns_a\d+|redelmeier_)")


# results/ghostship/ is a frozen record of a DIFFERENT filesystem: the sandbox
# the unattended run worked in, plus the grading files that quote its paths.
# Its citations are correct about that tree and wrong about this one, and the
# record must not be edited to make a gate happy -- that is what makes it a
# record.  Excluded by scope, not by exemption markers.
EXCLUDED_TREES = ("results/ghostship/",)


def tracked_markdown():
    out = subprocess.run(["git", "-C", ROOT, "ls-files", "*.md"],
                         capture_output=True, text=True, check=True).stdout
    return [f for f in out.split()
            if not f.startswith(EXCLUDED_TREES)]


def history_paths():
    out = subprocess.run(["git", "-C", ROOT, "log", "--all", "--pretty=format:",
                          "--name-only"], capture_output=True, text=True,
                         check=True).stdout
    return set(out.split())


def _paragraph_exempt(lines):
    """Which lines sit in a paragraph carrying an exemption marker.

    Per-line would be too strict: prose wraps, and a citation's marker often
    lands on the line above or below it. A paragraph is a run of lines between
    blank ones, which is the unit a reader takes the marker to govern.
    """
    flags = [False] * len(lines)
    start = 0
    for i in range(len(lines) + 1):
        if i == len(lines) or not lines[i].strip():
            block = " ".join(lines[start:i]).lower()
            if any(w in block for w in EXEMPT_WORDS):
                for j in range(start, i):
                    flags[j] = True
            start = i + 1
    return flags


def classify(text, hist, source="<doc>"):
    """Classify every path citation in `text`. Returns {class: [(source, line, path)]}."""
    out = {k: [] for k in ("exists", "template", "exempt", "history", "MISSING")}
    lines = text.split("\n")
    exempt_flags = _paragraph_exempt(lines)
    for lineno, line in enumerate(lines, 1):
        exempt_line = exempt_flags[lineno - 1]
        for m in PATH_RE.finditer(line):
            p = m.group(1).rstrip(".,;:)")
            rec = (source, lineno, p)
            if any(c in p for c in PLACEHOLDER):
                out["template"].append(rec)
            elif os.path.exists(os.path.join(ROOT, p)):
                out["exists"].append(rec)
            elif exempt_line:
                out["exempt"].append(rec)
            elif (p.rstrip("/") in hist
                  or any(h.startswith(p.rstrip("/") + "/") for h in hist)
                  or EPHEMERAL_RE.match(p)):
                out["history"].append(rec)
            else:
                out["MISSING"].append(rec)
    return out


def merge(dst, src):
    for k, v in src.items():
        dst[k].extend(v)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--verbose", action="store_true",
                    help="list the history-only citations too")
    args = ap.parse_args()

    hist = history_paths()
    totals = {k: [] for k in ("exists", "template", "exempt", "history", "MISSING")}
    files = tracked_markdown()
    # A tracked file missing from the working tree is a deletion that has not
    # been committed.  That is a legitimate state to be in and an illegitimate
    # state to crash on: the gate reports it and fails, rather than dying with a
    # traceback that hides every finding after it.  (Before this, one uncommitted
    # deletion masked nine real dangling citations for as long as it sat there.)
    absent = []
    for f in files:
        path = os.path.join(ROOT, f)
        if not os.path.exists(path):
            absent.append(f)
            continue
        with open(path, errors="replace") as fh:
            merge(totals, classify(fh.read(), hist, f))

    n = sum(len(v) for v in totals.values())
    print(f"{n} path citations across {len(files) - len(absent)} tracked "
          f"markdown files")
    if absent:
        print(f"  {len(absent)} tracked file(s) missing from the working tree "
              f"(uncommitted deletion?):")
        for f in absent:
            print(f"    {f}")
    for k in ("exists", "template", "exempt", "history", "MISSING"):
        print(f"  {k:9s} {len(totals[k])}")

    if args.verbose and totals["history"]:
        print("\nhistory-only (allowed; cite with a rev if a reader needs it):")
        for src, line, p in sorted(set(totals["history"])):
            print(f"  {p}  <- {src}:{line}")

    # RED control: the classifier must catch a bogus path, and must respect the
    # exemption. Run on synthetic text so it cannot be satisfied by the tree.
    red = classify("see `results/definitely-not-here.md` for the argument\n",
                   hist, "<red>")
    green = classify("see `results/definitely-not-here.md` (deleted) for it\n",
                     hist, "<red>")
    wrapped = classify("the probe was deleted in the tidy;\n"
                       "see `results/definitely-not-here.md` for what it did\n",
                       hist, "<red>")
    split = classify("deleted things live here\n\n"
                     "see `results/definitely-not-here.md` for the argument\n",
                     hist, "<red>")
    if (len(red["MISSING"]) != 1 or green["MISSING"] or wrapped["MISSING"]
            or len(split["MISSING"]) != 1):
        print("\nRED CONTROL FAILED: the classifier no longer detects a bogus "
              "path, no longer honours the exemption, or lets an exemption leak "
              "across a paragraph break")
        return 1
    print("\nRED  a bogus path is caught; the same path is exempt when its own "
          "paragraph says 'deleted', and the exemption does not leak across a "
          "blank line  OK")

    if totals["MISSING"]:
        print(f"\nGATE CITATIONS: RED -- {len(totals['MISSING'])} citation(s) "
              f"point at paths that have never existed:")
        for src, line, p in sorted(set(totals["MISSING"])):
            print(f"  {src}:{line}  ->  {p}")
        print("\nFix the path, or mark the line (deleted / planned / in memory) "
              "if the reader is meant to know it is not there.")
    if absent:
        print("\nGATE CITATIONS: RED -- a tracked file is not in the working "
              "tree; commit the deletion or restore the file.")
    if totals["MISSING"] or absent:
        return 1

    print("\nGATE CITATIONS: GREEN")
    return 0


if __name__ == "__main__":
    sys.exit(main())
