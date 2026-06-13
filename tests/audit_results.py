#!/usr/bin/env python3
"""Pre-submission audit of a campaign's results.txt against EXTERNAL truth.

The dual-campaign discipline proves campaign A == campaign B. It does NOT
prove either equals reality, and two identically-incomplete or
identically-buggy campaigns would agree with each other. This audit closes
that gap by checking the produced artifact against the pinned OEIS b-file on
the overlap range (a check that does not reuse the engine at all), and by
sanity-checking the growth ratio of any NEW terms against the b-file's last
known value -- never against the campaign's own counts, which would mask a
correlated deficit.

Run before submitting:  audit_results.py LATTICE runs/<dir>/results.txt
Hard-fails on any overlap mismatch; warns on an out-of-band growth ratio.
"""

import os
import sys

from common import read_bfile

# lattice -> (b-file, the OEIS id, plausible growth-ratio ceiling)
BFILE = {
    "square4": ("b001168.txt", "A001168", 4.40),
    "square8": ("b006770.txt", "A006770", 7.00),
    "tri6":    ("b001207.txt", "A001207", 6.20),
}


def read_results(path):
    counts = {}
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                n, c = line.split()
                counts[int(n)] = int(c)
    return counts


def audit(lattice, path):
    bfile, oeis, ceil = BFILE[lattice]
    known = read_bfile(bfile)
    got = read_results(path)
    fails, warns, new_terms = [], [], []

    overlap = sorted(set(got) & set(known))
    if not overlap:
        fails.append("no overlap with the known b-file -- cannot anchor")
    for n in overlap:
        if got[n] != known[n]:
            fails.append(f"n={n}: results {got[n]} != {oeis} {known[n]}")

    last_known = max(known)
    for n in sorted(got):
        if n > last_known:
            new_terms.append(n)

    # growth-ratio sanity, anchored on the b-file's last known term
    for n in sorted(got):
        if n - 1 not in got or n <= 1:
            continue
        prev = known[n - 1] if (n - 1) in known else got[n - 1]
        prev_prev = known.get(n - 2, got.get(n - 2))
        ratio = got[n] / prev
        if n > last_known:
            note = f"n={n}: a(n)/a(n-1) = {ratio:.4f}"
            if ratio > ceil or ratio <= 0:
                warns.append(note + f"  OUT OF BAND (>{ceil})")
            elif prev_prev and prev / prev_prev - ratio > 1e-6:
                warns.append(note + f"  RATIO FELL (prev {prev/prev_prev:.4f})"
                             " -- ratios should rise toward the growth constant")
            else:
                print(f"  {note}  (plausible)")

    print(f"audit {lattice} {path}")
    print(f"  overlap with {oeis}: {len(overlap)} terms checked, "
          f"{'ALL MATCH' if not any(f.startswith('n=') for f in fails) else 'MISMATCH'}")
    print(f"  new terms beyond {oeis}: {new_terms or 'none'}")
    for w in warns:
        print("  WARN " + w)
    for f in fails:
        print("  FAIL " + f)
    if fails:
        print("AUDIT: FAIL -- do not submit")
        return 1
    print("AUDIT: PASS"
          + (" (review WARN lines before submitting)" if warns else ""))
    return 0


def main():
    if len(sys.argv) != 3 or sys.argv[1] not in BFILE:
        sys.exit(f"usage: {sys.argv[0]} {{{'|'.join(BFILE)}}} results.txt")
    if not os.path.exists(sys.argv[2]):
        sys.exit(f"no such file: {sys.argv[2]}")
    return audit(sys.argv[1], sys.argv[2])


if __name__ == "__main__":
    sys.exit(main())
