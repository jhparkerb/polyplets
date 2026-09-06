#!/usr/bin/env python3
"""Gate NO-COPYRIGHT-PDFS: no copyrighted PDF is tracked in this repo.

`literature/` is the literature library --- other people's work, read locally, and
the top line of `.gitignore` says "copyrighted papers stay local, never pushed".
That rule was enforced by nothing.  The closest thing to a check was a `say`
line in `scripts/clean_clone_check.sh`, a one-shot runner `make` never touches,
which printed the count and set no exit code; a `git add -f` of a PDF would sit
tracked until someone ran that script by hand and then read the line.  This is
the publication-blocking invariant of the three, so it gets a gate.

The check: `git ls-files` names no `.pdf` anywhere in the tree except the
manuscripts this project writes, which are gitignored anyway (`paper/*.pdf`
is a build output of `make -C paper`).  Any tracked PDF fails.

Two RED controls, both of which must fire: a synthetic tracked PDF must be
reported, and a query that comes back empty because the git call failed --- as
opposed to because the tree is clean --- must fail rather than pass vacuously.

Usage: python3 tests/gate_no_copyright_pdfs.py [--verbose]
"""
import argparse
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def tracked_files(root=ROOT):
    """Every tracked path.  Raises if git cannot answer -- see the vacuity control."""
    out = subprocess.run(["git", "-C", root, "ls-files"],
                         capture_output=True, text=True, check=True).stdout
    paths = out.split()
    if not paths:
        raise RuntimeError("git ls-files returned nothing at all")
    return paths


def offenders(paths):
    """Tracked PDFs.  Every one is a defect: ours are build outputs, theirs are
    copyrighted."""
    return sorted(p for p in paths if p.lower().endswith(".pdf"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    try:
        paths = tracked_files()
    except (subprocess.CalledProcessError, RuntimeError) as e:
        print("GATE NO-COPYRIGHT-PDFS: RED -- cannot list tracked files: %s" % e)
        return 1

    bad = offenders(paths)
    print("%d tracked files, %d of them PDFs" % (len(paths), len(bad)))
    if args.verbose:
        print("  literature/ tracked text files: %s"
              % " ".join(p for p in paths if p.startswith("literature/")))

    # RED control 1: a tracked PDF must be reported.
    if offenders(paths + ["literature/someone_elses_2019_paper.pdf"]) != \
            ["literature/someone_elses_2019_paper.pdf"]:
        print("GATE NO-COPYRIGHT-PDFS: RED CONTROL DID NOT FIRE -- a tracked "
              "PDF was not reported; the check is vacuous")
        return 1
    # RED control 2: no answer from git must raise rather than read as a clean
    # tree.  A gate whose evidence went missing has stopped checking.
    with tempfile.TemporaryDirectory() as d:
        try:
            tracked_files(d)
            print("GATE NO-COPYRIGHT-PDFS: RED CONTROL DID NOT FIRE -- listing "
                  "a non-repository succeeded; an empty answer would pass as a "
                  "clean tree")
            return 1
        except (subprocess.CalledProcessError, RuntimeError):
            pass
    print("RED  a tracked PDF is reported, and a failed git query is not "
          "read as a clean tree  OK")

    if bad:
        print("\nGATE NO-COPYRIGHT-PDFS: FAILED -- %d PDF(s) are tracked:"
              % len(bad))
        for p in bad:
            print("  %s" % p)
        print("\nPDFs in literature/ are other people's copyrighted work and must "
              "stay local; PDFs in paper/ are build outputs of `make -C paper`. "
              "Either way: `git rm --cached <path>`.")
        return 1

    print("\nGATE NO-COPYRIGHT-PDFS: GREEN")
    return 0


if __name__ == "__main__":
    sys.exit(main())
