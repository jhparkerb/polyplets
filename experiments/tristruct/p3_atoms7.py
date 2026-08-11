"""p3_atoms7.py -- Proposer 3: the height-7 strip atom q_7, ab initio.

Extends the atom-degree sequence 1, 2, 4, 9, 29, 68 (Superseeker-checked as
novel; banked only up to measured degree 68) by one term, with exact
coefficients. Same pipeline as p3_atoms.py: own strip TM -> exact bignum
series -> Berlekamp-Massey mod 8 ~60-bit primes -> CRT lift -> exact
certification over Z on every available instance.

NLONG=420 columns needs LIMB large enough for the counts (~mu^420; S_6(160)
has 114 digits => ~0.72 digits/n, so S_7(420) ~ 310 digits ~ 1030 bits);
LIMB is raised to 1280 before calling strip_series (the limb-overflow
assertion in p3_striptm.strip_series still guards it).

Output: appends "7 deg c0 ..." to data/p3_atoms_q.txt (rewrites the file
with H=1..7) and writes data/p3_striptm_S7.txt (exact S_7(n), n <= NLONG).
Run from experiments/tristruct/:  python3 p3_atoms7.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import p3_striptm  # noqa: E402
from p3_atoms import (berlekamp_massey, crt_lift, gen_primes,  # noqa: E402
                      check_recurrence, polygcd_modp, deriv)

NLONG = 420
NPRIMES = 8


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    p3_striptm.LIMB = 1280
    primes = gen_primes(NPRIMES)
    S7, ns = p3_striptm.strip_series(7, NLONG)
    print("H=7  states=%d  S_7(%d) has %d digits"
          % (ns, NLONG, len(str(S7[NLONG]))))
    sys.stdout.flush()

    seq = S7[1:]
    polys = [berlekamp_massey(seq, p) for p in primes]
    degs = {len(c) - 1 for c in polys}
    assert len(degs) == 1, "degree disagrees across primes: %s" % degs
    d = degs.pop()
    print("BM degree (all %d primes agree): %d" % (NPRIMES, d))
    assert 2 * d + 20 <= NLONG, "NLONG too small for degree %d" % d
    coeffs = [crt_lift([polys[k][j] for k in range(NPRIMES)], primes)
              for j in range(d + 1)]
    ninst = check_recurrence(coeffs, seq, 0)
    print("q_7: degree %d, exact-certified over Z on %d instances "
          "(n in [%d,%d]); max |coeff| has %d digits"
          % (d, ninst, d + 1, NLONG, max(len(str(abs(c))) for c in coeffs)))

    # squarefree + coprime to q_1..q_6
    p0 = primes[0]
    g = polygcd_modp(coeffs, deriv(coeffs), p0)
    print("gcd(q_7, q_7') mod p: degree %d %s"
          % (len(g) - 1, "SQUAREFREE" if len(g) == 1 else "NOT SQUAREFREE"))
    qs = {}
    with open(os.path.join(here, "data", "p3_atoms_q.txt")) as f:
        for line in f:
            parts = line.split()
            qs[int(parts[0])] = [int(x) for x in parts[2:]]
    for H in sorted(qs):
        if H >= 7:
            continue
        g = polygcd_modp(coeffs, qs[H], p0)
        assert len(g) == 1, "q_7 shares a factor with q_%d" % H
    print("q_7 coprime to q_1..q_6")

    qs[7] = coeffs
    with open(os.path.join(here, "data", "p3_atoms_q.txt"), "w") as f:
        for H in sorted(qs):
            f.write("%d %d %s\n" % (H, len(qs[H]) - 1,
                                    " ".join(map(str, qs[H]))))
    with open(os.path.join(here, "data", "p3_striptm_S7.txt"), "w") as f:
        for n in range(1, NLONG + 1):
            f.write("%d %d\n" % (n, S7[n]))
    print("atom degrees now: %s"
          % " ".join("%d:%d" % (H, len(qs[H]) - 1) for H in sorted(qs)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
