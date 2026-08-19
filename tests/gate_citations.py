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
  history    gone from the tree but present in the history of the CHECKED-OUT
             branch -- reported, and allowed: the repo deletes scaffolding on
             purpose, and `git show <rev>^:path` is a legitimate citation
  branch     absent from this branch's history, and the citing file declares
             ("unmerged branch `X`") that it lives on another one -- allowed,
             and the claim is VERIFIED when ref X is present locally
  MISSING    none of the above -- FAILS the gate

The history class is deliberately scoped to HEAD and not to `--all`. Until
2026-08-18 it used every local ref, which made the verdict depend on which
branches the checker's clone happened to have: 65 citations across 25 campaign
records resolved on gympie's 50 local refs and dangled in a clone of master,
which is what a reader gets.

MISSING is the class that catches a name that never existed, which is what a
memory-name-as-path always is.

RED control: a synthetic document citing `results/definitely-not-here.md` must
land in MISSING, and one citing it on a line that says "deleted" must not. A
second control covers the branch class: a file declaring a branch that does not
carry the cited path must not thereby exempt it, when that branch is present.

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
# A campaign record whose sibling deliverables were filed on a branch that never
# merged declares that branch once, at the top of the file, and the declaration
# governs the whole file: `unmerged branch `triangle-structure``. It is an
# exemption with a checkable claim attached -- see branch_carries().
BRANCH_DIRECTIVE_RE = re.compile(r"unmerged branch `([A-Za-z0-9._/-]+)`")
# Trees a CLONE legitimately does not have.  Until 2026-08-18 this list was
# tuned on a working tree, where untracked leftovers made citations look live;
# in a clean clone -- which is what a reader gets -- 101 citations pointed at
# nothing.  papers/ is the gitignored literature library (copyrighted PDFs stay
# local, and paper/README.md says so); polyplets/.lake/ is vendored Mathlib that
# `lake build` fetches.  Both are correct citations into a working copy and are
# not repo content.
EPHEMERAL_RE = re.compile(r"^(runs|build)/|^results/(ns_a\d+|redelmeier_)"
                          r"|^papers/|^polyplets/\.lake/")


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


def history_paths(rev="HEAD"):
    """Every path that has ever existed in `rev`'s history."""
    out = subprocess.run(["git", "-C", ROOT, "log", rev, "--pretty=format:",
                          "--name-only"], capture_output=True, text=True,
                         check=True).stdout
    return set(out.split())


_BRANCH_CACHE = {}


def branch_carries(ref, path):
    """Does `ref` carry `path` in its history?  None if the ref is not here.

    A clone of the published branch will not have the campaign branches, and a
    declaration cannot be verified against a ref that is absent -- so the gate
    reports "unverified" rather than failing on it. Where the ref IS present the
    claim is checked, and a declaration naming a branch that does not carry the
    path is a harder failure than the dangling citation it was meant to excuse.
    """
    if ref not in _BRANCH_CACHE:
        # A clone gets the branch as origin/<name>, not <name>, and rev-parse
        # does not DWIM from one to the other -- so try both before concluding
        # the ref is absent.
        _BRANCH_CACHE[ref] = None
        for cand in (ref, "origin/" + ref):
            if subprocess.run(["git", "-C", ROOT, "rev-parse", "--verify",
                               "--quiet", cand + "^{commit}"],
                              capture_output=True, text=True).returncode == 0:
                _BRANCH_CACHE[ref] = history_paths(cand)
                break
    paths = _BRANCH_CACHE[ref]
    return None if paths is None else path in paths


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


CLASSES = ("exists", "template", "exempt", "history", "branch", "MISSING")


def classify(text, hist, source="<doc>"):
    """Classify every path citation in `text`. Returns {class: [(source, line, path)]}.

    `false_claim` is not a class of citation but a defect in the file's own
    branch declaration, carried alongside so the caller can fail on it.
    """
    out = {k: [] for k in CLASSES}
    out["false_claim"] = []
    lines = text.split("\n")
    exempt_flags = _paragraph_exempt(lines)
    declared = BRANCH_DIRECTIVE_RE.findall(text)
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
            elif declared:
                carried = [branch_carries(r, p) for r in declared]
                if any(c is True for c in carried):
                    out["branch"].append(rec)
                elif all(c is None for c in carried):
                    out["branch"].append(rec)          # ref absent: unverifiable
                else:
                    out["false_claim"].append(rec + (tuple(declared),))
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
    totals = {k: [] for k in CLASSES}
    totals["false_claim"] = []
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

    n = sum(len(totals[k]) for k in CLASSES) + len(totals["false_claim"])
    print(f"{n} path citations across {len(files) - len(absent)} tracked "
          f"markdown files")
    if absent:
        print(f"  {len(absent)} tracked file(s) missing from the working tree "
              f"(uncommitted deletion?):")
        for f in absent:
            print(f"    {f}")
    for k in CLASSES:
        print(f"  {k:9s} {len(totals[k])}")

    if totals["branch"]:
        srcs = sorted({src for src, _, _ in totals["branch"]})
        print(f"\n  {len(totals['branch'])} citation(s) in {len(srcs)} file(s) "
              f"declared to live on an unmerged branch; a reader who clones "
              f"only the published branch cannot follow them.")

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

    # RED control 2: a declaration must not exempt a path the named ref lacks.
    # Uses HEAD, which exists everywhere and provably does not carry the bogus
    # path, so the control is real on any clone.
    liar = classify("this record cites `results/definitely-not-here.md`, and its\n"
                    "siblings live on unmerged branch `HEAD`\n",
                    hist, "<red2>")
    if len(liar["false_claim"]) != 1:
        print("\nRED CONTROL FAILED: a branch declaration now exempts a path "
              "that the branch it names does not carry")
        return 1
    print("RED  a branch declaration does not exempt a path its own branch "
          "lacks  OK")

    if totals["false_claim"]:
        print(f"\nGATE CITATIONS: RED -- {len(totals['false_claim'])} "
              f"citation(s) sit under a branch declaration that does not carry "
              f"them:")
        for src, line, p_, decl in sorted(set(totals["false_claim"])):
            print(f"  {src}:{line}  ->  {p_}   declared on {', '.join(decl)}")

    if totals["MISSING"]:
        print(f"\nGATE CITATIONS: RED -- {len(totals['MISSING'])} citation(s) "
              f"point at paths that have never existed:")
        for src, line, p in sorted(set(totals["MISSING"])):
            print(f"  {src}:{line}  ->  {p}")
        print("\nFix the path; or mark the line (deleted / planned / in memory) "
              "if the reader is meant to know it is not there; or, if the file "
              "is a campaign record whose siblings were filed on a branch that "
              "never merged, declare that branch once at the top of it: "
              "unmerged branch `the-branch-name`.")
    if absent:
        print("\nGATE CITATIONS: RED -- a tracked file is not in the working "
              "tree; commit the deletion or restore the file.")
    if totals["MISSING"] or absent or totals["false_claim"]:
        return 1

    print("\nGATE CITATIONS: GREEN")
    return 0


if __name__ == "__main__":
    sys.exit(main())
