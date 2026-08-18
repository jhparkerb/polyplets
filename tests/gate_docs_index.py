#!/usr/bin/env python3
"""Gate DOCS-INDEX: `docs/README.md` names every file in `docs/`.

Written 2026-08-18 with the index itself, during the close-out markdown sweep.
An index that silently rots is worse than no index: a reader who finds one file
missing from it stops trusting the other ninety-six. `gate_citations.py` already
catches the other direction (an index entry pointing at a file that is gone), so
this gate only has to close the completeness side.

The check: every tracked `docs/**/*.md` except the index is covered, where
covered means the index cites either

  the file          `docs/proofs/diagonal-law.md`
  its directory     `docs/reviews/l-trim/`   (covers all 17 phase files)

Directory coverage is deliberate. Listing seventeen l-trim phase files by name
would make the index unreadable and would not tell a reader anything the one
directory line does not.

RED control: a synthetic docs file that the index does not name must FAIL, and
naming its directory must make it pass.

Usage: python3 tests/gate_docs_index.py [--verbose]
"""
import argparse
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX = "docs/README.md"


def tracked_docs():
    out = subprocess.run(["git", "-C", ROOT, "ls-files", "docs/*.md",
                          "docs/**/*.md"],
                         capture_output=True, text=True, check=True).stdout
    return sorted(f for f in out.split() if f != INDEX)


def uncovered(paths, index_text):
    """Paths the index names neither directly nor by their directory."""
    missing = []
    for p in paths:
        if p in index_text:
            continue
        parent = os.path.dirname(p) + "/"
        if parent != "docs/" and parent in index_text:
            continue
        missing.append(p)
    return missing


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    index_path = os.path.join(ROOT, INDEX)
    if not os.path.exists(index_path):
        print(f"GATE DOCS-INDEX: RED -- {INDEX} does not exist")
        return 1
    index_text = open(index_path, encoding="utf-8").read()

    docs = tracked_docs()
    missing = uncovered(docs, index_text)

    print(f"{len(docs)} tracked files under docs/, {len(docs) - len(missing)} "
          f"named by {INDEX}")
    if args.verbose:
        for p in docs:
            print(f"  {'MISSING' if p in missing else 'ok     '}  {p}")

    # RED control: the gate must fail an unnamed file, and pass it once its
    # directory is named.  Run against the real index text so a rewrite that
    # accidentally matches everything (say, a stray `docs/`) is caught too.
    red = uncovered(["docs/synthetic/not-in-the-index.md"], index_text)
    if red != ["docs/synthetic/not-in-the-index.md"]:
        print("GATE DOCS-INDEX: RED CONTROL DID NOT FIRE -- an unnamed file "
              "was reported as covered; the check is vacuous")
        return 1
    if uncovered(["docs/synthetic/not-in-the-index.md"],
                 index_text + "\n`docs/synthetic/`\n"):
        print("GATE DOCS-INDEX: RED CONTROL DID NOT FIRE -- naming the "
              "directory did not cover the file")
        return 1
    print("RED  an unnamed docs file fails, and naming its directory "
          "covers it  OK")

    if missing:
        print(f"\nGATE DOCS-INDEX: FAILED -- {len(missing)} file(s) under "
              f"docs/ are not named in {INDEX}:")
        for p in missing:
            print(f"  {p}")
        print(f"\nAdd each to the right group in {INDEX}, or name its "
              f"directory if the group is a whole tree.")
        return 1

    print("\nGATE DOCS-INDEX: GREEN")
    return 0


if __name__ == "__main__":
    sys.exit(main())
