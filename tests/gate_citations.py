#!/usr/bin/env python3
"""Gate CITATIONS: every repo path a document cites must exist.

Written 2026-08-06 after two citation defects in two days. One was a paper
mis-read (a 1998 PDF written off as a scan without opening it); the other was
`results/subclasses.md` citing `results/cloud-investigation-2026-07-07.md`,
a file that has never existed in this repo -- the name belongs to an entry in
Claude's memory directory, and `docs/engine-record.md` cites it
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

The second check is on markdown LINKS -- `[text](path)` -- and is stricter than
the one on backticked paths: a link is clickable, so a reader who follows one
to a file that is not there gets nothing at all, and no exemption word on the
line changes that.  There is no history class for a link either; a deleted file
is a fine thing to name in prose and a broken thing to link to.  Added
2026-09-06, when README.md's own "why believe the number" paragraph linked
`docs/engine-record.md`, merged into `docs/engine-record.md` a commit
earlier -- the front door's first outbound link, and the backtick check passed
it as history.

RED control: a synthetic document citing `results/definitely-not-here.md` must
land in MISSING, and one citing it on a line that says "deleted" must not. A
second control covers the branch class: a file declaring a branch that does not
carry the cited path must not thereby exempt it, when that branch is present.

The third check is on SOURCE files -- module docstrings and Lean headers cite
documents, and the consolidation left 588 of those pointing at merged-away
records.  Same rule as the prose check: repoint it, or say deleted.

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
# \s+ rather than a literal space: prose wraps, and the first file to use
# this (the project handoff file (removed)) wrapped between "branch" and the name.
BRANCH_DIRECTIVE_RE = re.compile(r"unmerged branch\s+`([A-Za-z0-9._/-]+)`")
# Trees a CLONE legitimately does not have.  Until 2026-08-18 this list was
# tuned on a working tree, where untracked leftovers made citations look live;
# in a clean clone -- which is what a reader gets -- 101 citations pointed at
# nothing.  literature/ is the gitignored literature library (copyrighted PDFs stay
# local, and paper/README.md says so); polyplets/.lake/ is vendored Mathlib that
# `lake build` fetches.  Both are correct citations into a working copy and are
# not repo content.
EPHEMERAL_RE = re.compile(r"^(runs|build)/|^results/(ns_a\d+|redelmeier_)"
                          r"|^literature/|^polyplets/\.lake/")


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


# (branch, path) pairs recorded from a tree that had the campaign refs. A clone
# has the declarations and not the branches, so without this the declaration
# would exempt anything at all in a declaring file -- fail-open in exactly the
# environment the gate exists to protect. Regenerate with --write-manifest from
# a tree that has the refs; the gate diffs it against them when they are there.
MANIFEST_PATH = os.path.join(ROOT, "tests", "unmerged_branch_paths.txt")


def read_manifest():
    out = set()
    if os.path.exists(MANIFEST_PATH):
        with open(MANIFEST_PATH) as fh:
            for line in fh:
                line = line.split("#", 1)[0].strip()
                if line:
                    ref, path = line.split(None, 1)
                    out.add((ref, path))
    return out


MANIFEST = read_manifest()

_BRANCH_CACHE = {}


def ref_paths(ref):
    """Every path in `ref`'s history, or None if this tree has no such ref.

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
    return _BRANCH_CACHE[ref]


def branch_carries(ref, path):
    """True/False if `ref` is here and does/does not carry `path`; None if not."""
    paths = ref_paths(ref)
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


def classify(text, hist, source="<doc>", declared=None):
    """Classify every path citation in `text`. Returns {class: [(source, line, path)]}.

    `false_claim` is not a class of citation but a defect in the file's own
    branch declaration, carried alongside so the caller can fail on it.
    """
    out = {k: [] for k in CLASSES}
    out["false_claim"] = []
    lines = text.split("\n")
    exempt_flags = _paragraph_exempt(lines)
    if declared is None:
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
                elif any((r, p) in MANIFEST for r in declared):
                    # Ref absent -- the reader's case. The manifest, written
                    # from a tree that HAD the refs, is what stands in for
                    # them, so a path nobody ever recorded still fails.
                    out["branch"].append(rec)
                else:
                    # Either a declared ref is here and does not carry the path,
                    # or none is here and the manifest has never seen it. Both
                    # are a declaration that does not cover what it claims.
                    out["false_claim"].append(rec + (tuple(declared),))
            else:
                out["MISSING"].append(rec)
    return out


# Source files cite documents too -- a module docstring or a Lean header saying
# where the argument it implements is written down. The consolidation of
# 2026-09-06 left 588 of those pointing at merged-away records, which is the
# same dead end as a bad citation in prose and is not covered by the markdown
# sweep above. Same exemption rule: a line that says the file is deleted is
# telling the reader the truth and passes.
SOURCE_EXTS = (".py", ".go", ".sh", ".cpp", ".h", ".lean")
# Paths the gates themselves name on purpose: the RED controls need a path that
# has never existed, and the docstrings that explain them quote the incident
# names. Listing them here keeps the check fail-closed everywhere else.
SYNTHETIC = frozenset((
    "results/definitely-not-here.md", "docs/synthetic/not-in-the-index.md",
    "results/cloud-investigation-2026-07-07.md",
    "results/reach-scaling-and-resourcing.md", "results/pgo-no-go.md",
))


def tracked_sources():
    out = subprocess.run(["git", "-C", ROOT, "ls-files"],
                         capture_output=True, text=True, check=True).stdout
    return [f for f in out.split() if f.endswith(SOURCE_EXTS)
            and not f.startswith(EXCLUDED_TREES)]


def dead_source_citations(text, source):
    """Documents a source file names that are not in the tree and not marked."""
    out = []
    for lineno, line in enumerate(text.split("\n"), 1):
        low = line.lower()
        if "deleted" in low or "removed" in low or "planned" in low:
            continue
        for m in SOURCE_PATH_RE.finditer(line):
            p = m.group(1).rstrip(".,;:)")
            if p in SYNTHETIC or os.path.exists(os.path.join(ROOT, p)):
                continue
            out.append((source, lineno, p))
    return out


SOURCE_PATH_RE = re.compile(r"\b((?:" + "|".join(TOP) + r")/[A-Za-z0-9_./-]+\.md)")

LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")


def dead_links(text, source):
    """Markdown links in `source` whose target is not in the working tree.

    Relative to the citing file, the way a reader's browser resolves it.
    External schemes and same-file anchors are not ours to check; the
    ephemeral trees are the ones a clone legitimately lacks.
    """
    out = []
    base = os.path.dirname(source)
    # Math in these documents is full of things a link regex reads as one --
    # `[the bulk](G*u^m)`, `O(f\u03c6^k)` -- so a target only counts as a path
    # when it is spelled like one: ASCII word characters, dots, dashes and
    # slashes, with at least one dot or slash in it.
    pathish = re.compile(r"^[A-Za-z0-9_./-]+$")
    for lineno, line in enumerate(text.split("\n"), 1):
        for m in LINK_RE.finditer(line):
            target = m.group(1).split("#", 1)[0]
            if not target or "://" in target or target.startswith("mailto:"):
                continue
            if not pathish.match(target) or not re.search(r"[./]", target):
                continue
            rel = os.path.normpath(os.path.join(base, target))
            if EPHEMERAL_RE.match(rel) or os.path.exists(os.path.join(ROOT, rel)):
                continue
            out.append((source, lineno, target))
    return out


def merge(dst, src):
    for k, v in src.items():
        dst[k].extend(v)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--verbose", action="store_true",
                    help="list the history-only citations too")
    ap.add_argument("--write-manifest", action="store_true",
                    help="rewrite tests/unmerged_branch_paths.txt from the "
                         "campaign refs in THIS tree (needs them present)")
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
    absent, decls, broken_links = [], {}, []
    for f in files:
        path = os.path.join(ROOT, f)
        if not os.path.exists(path):
            absent.append(f)
            continue
        with open(path, errors="replace") as fh:
            text = fh.read()
        decls[f] = BRANCH_DIRECTIVE_RE.findall(text)
        merge(totals, classify(text, hist, f, decls[f]))
        broken_links.extend(dead_links(text, f))

    dead_src = []
    for f in tracked_sources():
        path = os.path.join(ROOT, f)
        if not os.path.exists(path):
            continue
        with open(path, errors="replace") as fh:
            dead_src.extend(dead_source_citations(fh.read(), f))

    n = sum(len(v) for v in totals.values())
    print(f"{n} path citations across {len(files) - len(absent)} tracked "
          f"markdown files")
    if absent:
        print(f"  {len(absent)} tracked file(s) missing from the working tree "
              f"(uncommitted deletion?):")
        for f in absent:
            print(f"    {f}")
    for k in CLASSES:
        print(f"  {k:9s} {len(totals[k])}")
    print(f"  {len(broken_links)} broken markdown link(s)")
    print(f"  {len(dead_src)} source file(s) citation(s) to a document that is "
          f"gone and unmarked")

    # What the branch class resolved through refs that are actually here. This
    # is the manifest's content, and comparing it to the file on disk is the
    # same regenerate-and-diff shape as gate-provenance.
    present_refs = {r for refs in decls.values() for r in refs
                    if ref_paths(r) is not None}
    resolved = {(r, p_) for src, _, p_ in totals["branch"]
                for r in decls.get(src, ())
                if r in present_refs and branch_carries(r, p_)}

    if args.write_manifest:
        if not present_refs:
            print("--write-manifest needs the campaign refs, and this tree has "
                  "none of the ones the records declare")
            return 1
        with open(MANIFEST_PATH, "w") as out:
            out.write("# (branch, path) pairs behind every 'unmerged branch' "
                      "declaration in this tree.\n"
                      "# Written by tests/gate_citations.py --write-manifest "
                      "from a tree that HAS those refs;\n"
                      "# it is what a clone, which does not, checks the "
                      "declarations against.\n")
            for ref, p_ in sorted(resolved):
                out.write(f"{ref} {p_}\n")
        print(f"wrote {MANIFEST_PATH} ({len(resolved)} pairs)")
        return 0

    manifest_drift = []
    if present_refs:
        for_present = {(r, p_) for (r, p_) in MANIFEST if r in present_refs}
        for pair in sorted(resolved - for_present):
            manifest_drift.append(("not in the manifest", pair))
        for pair in sorted(for_present - resolved):
            manifest_drift.append(("in the manifest, cited by nothing", pair))

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

    # RED control 4: a link to a file that is not here must be caught, and
    # neither an exemption word on the line nor the file's presence in history
    # may excuse it -- both excuse a backticked path and neither un-breaks a
    # link. Synthetic text, so the tree cannot satisfy it.
    link_red = dead_links("see [the sweep](results/definitely-not-here.md) "
                          "(deleted) for it\n", "<red4>")
    link_ok = dead_links("see [the gate](tests/gate_citations.py), "
                         "[OEIS](https://oeis.org/A006770) and the bulk term "
                         "[G](G*u^m)\n", "<red4>")
    if len(link_red) != 1 or link_ok:
        print("\nRED CONTROL FAILED: a markdown link to a file that is not "
              "here is no longer caught, or a live link is now flagged")
        return 1
    print("RED  a link to a file that is not here is caught even when the line "
          "says 'deleted'; live links, external links and math that reads as a "
          "link are not  OK")

    # RED control 5: a source file citing a document that is not here fails,
    # and the same line passes once it says the document was deleted.
    # Assembled at runtime rather than written out, so this gate's own source
    # does not contain the bogus path it is checking for.
    bogus = "results/" + "no-such-record-red5" + ".md"
    src_red = dead_source_citations(f"# see {bogus}\n", "<red5>")
    src_ok = dead_source_citations(f"# see {bogus} (deleted)\n", "<red5>")
    if len(src_red) != 1 or src_ok:
        print("\nRED CONTROL FAILED: a source file citing a document that is "
              "gone is no longer caught, or the deleted marker no longer "
              "excuses one")
        return 1
    print("RED  a source file citing a document that is gone is caught, and "
          "the same line passes once it says deleted  OK")

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

    # RED control 3: the reader's case. The named ref is not in this tree at all
    # (no clone has it), so the manifest is the only thing standing behind the
    # declaration -- and a path the manifest has never seen must still fail.
    # Without this the declaration would exempt anything in a declaring file.
    absent_ref = classify("this record cites `results/definitely-not-here.md`, "
                          "and its siblings\nlive on unmerged branch "
                          "`no-such-branch-red-control`\n", hist, "<red3>")
    if len(absent_ref["false_claim"]) != 1:
        print("\nRED CONTROL FAILED: a declaration naming a branch this tree "
              "does not have now exempts a path the manifest has never seen")
        return 1
    print("RED  a declaration for an absent branch does not exempt a path the "
          "manifest has never seen  OK")

    if manifest_drift:
        print(f"\nGATE CITATIONS: RED -- tests/unmerged_branch_paths.txt is "
              f"{len(manifest_drift)} row(s) out of step with the refs in this "
              f"tree; rerun with --write-manifest:")
        for why, (ref, p_) in manifest_drift:
            print(f"  {ref} {p_}   {why}")

    if totals["false_claim"]:
        print(f"\nGATE CITATIONS: RED -- {len(totals['false_claim'])} "
              f"citation(s) sit under a branch declaration that does not carry "
              f"them:")
        for src, line, p_, decl in sorted(set(totals["false_claim"])):
            print(f"  {src}:{line}  ->  {p_}   declared on {', '.join(decl)}")

    if broken_links:
        print(f"\nGATE CITATIONS: RED -- {len(broken_links)} markdown link(s) "
              f"point at a file that is not in the tree; a reader who clicks "
              f"gets nothing:")
        for src, line, t in sorted(set(broken_links)):
            print(f"  {src}:{line}  ->  {t}")
        print("\nRepoint the link at what absorbed the file, or unlink it and "
              "name the file in prose (that the backtick check will pass as "
              "history).")

    if dead_src:
        print(f"\nGATE CITATIONS: RED -- {len(dead_src)} citation(s) in source "
              f"files point at a document that is not in the tree:")
        for src, line, p in sorted(set(dead_src)):
            print(f"  {src}:{line}  ->  {p}")
        print("\nRepoint at whatever absorbed it, or say '(deleted)' on the "
              "line so the reader does not go looking.")

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
    if (totals["MISSING"] or absent or totals["false_claim"]
            or manifest_drift or broken_links or dead_src):
        return 1

    print("\nGATE CITATIONS: GREEN")
    return 0


if __name__ == "__main__":
    sys.exit(main())
