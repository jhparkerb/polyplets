#!/usr/bin/env python3
"""Assemble free / one-sided polyplet counts from fixed + symmetric counts.

Free(n)      = (Fixed + 2*R90 + R180 + 2*H + 2*D) / 8
One-sided(n) = (Fixed + 2*R90 + R180) / 4

Fixed comes from A006770 (b-file, known to 18); the four symmetric counts come
from the validated C++ counter (build/symcount_fast). Verifies Free against
A030222 on the overlap (n<=17) before reporting any new term, so a wrong
symmetric count or a wrong Fixed(19) candidate is caught against external
truth.

Usage: free_polyplets.py MAXN [n=FIXED ...]
  Extra fixed terms beyond the b-file (which ends at n=18), given as "n=value"
  pairs -- e.g. "19=151609203011580 20=1025573519362016" to fold in the
  a(19)/a(20) candidates so Free/One-sided can be formed there. A bare value is
  back-compat for n=19.
"""

import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
import obs  # shared observability/provenance runtime (docs/observability.md)
sys.path.insert(0, os.path.join(ROOT, "tests"))
from common import free_and_one_sided, read_bfile  # noqa: E402

FAST = os.path.join(ROOT, "build", "symcount_fast")
TYPES = ["r90", "r180", "hmirror", "dmirror"]


def _parse_counts(text):
    d = {}
    for line in text.splitlines():
        p = line.split()
        if len(p) == 2 and p[0].lstrip("-").isdigit():   # skip any comment/banner
            d[int(p[0])] = int(p[1])
    return d


def sym_counts(t, maxn):
    out = subprocess.run([FAST, t, str(maxn)], capture_output=True, text=True,
                         check=True).stdout
    return _parse_counts(out)


def sym_counts_from_dir(t, d):
    """Read a symmetry type's counts from a prior run's <type>.out (e.g. the
    cross-ISA-confirmed runs/sym20/), instead of recomputing via symcount_fast."""
    with open(os.path.join(d, f"{t}.out")) as f:
        return _parse_counts(f.read())


def main():
    maxn = int(sys.argv[1])
    fixed = read_bfile("b006770.txt")          # known fixed counts a(n), n <= 18
    from_dir = None
    rest = sys.argv[2:]
    if "--from-dir" in rest:                    # read counts from prior .out files
        j = rest.index("--from-dir")
        from_dir = rest[j + 1]
        rest = rest[:j] + rest[j + 2:]
    for a in rest:                              # fold in candidates beyond the b-file
        if "=" in a:
            n_, v_ = a.split("=", 1)
            fixed[int(n_)] = int(v_)
        else:
            fixed[19] = int(a)                 # bare value = a(19), back-compat
    free_known = read_bfile("b030222.txt")

    sys.stdout.write(obs.file_header("free_polyplets", f"free-N{maxn}", __file__))
    mism = 0
    with obs.Reporter(f"free-N{maxn}", script=__file__, total=len(TYPES)) as rep:
        sym = {}
        for i, t in enumerate(TYPES):           # the C++ counter is the long pole
            sym[t] = (sym_counts_from_dir(t, from_dir) if from_dir
                      else sym_counts(t, maxn))
            rep.beat(done=i + 1, force=True, type=t,
                     src=("file" if from_dir else "cpp"))

        def g(t, n):
            return sym[t].get(n, 0)

        print(f"{'n':>3} {'free':>22} {'one-sided':>22}  note")
        for n in range(1, maxn + 1):
            if n not in fixed:
                continue
            free, one = free_and_one_sided(
                fixed[n], g("r90", n), g("r180", n), g("hmirror", n), g("dmirror", n))
            note = ""
            if n in free_known:
                if free == free_known[n]:
                    note = "ok vs A030222"
                else:
                    note = f"!!! A030222 says {free_known[n]}"
                    mism += 1
            else:
                note = "NEW TERM"
            print(f"{n:>3} {free:>22} {one:>22}  {note}")
        # the cross-check against external truth (A030222) is the headline result;
        # surface its pass/fail on the done line, not just buried in the table.
        rep.done(result=("ok" if mism == 0 else "MISMATCH"), mismatches=mism)


if __name__ == "__main__":
    sys.exit(main())
