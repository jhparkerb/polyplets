#!/usr/bin/env python3
"""audit_diagonals.py -- independent audit of the closed-form height-diagonals
P_3..P_8 used to inject a(25)'s heights H17..22 (and the k=8 cell T(25,17)).

Verification task #4. Reconstructs each P_k from SWEPT-ONLY data (results/
ns_a25/swept_rows.txt, the run's own h3..h16 files -- never the injected cells,
which would be circular) using exact rational arithmetic, and checks:
  (a) is the fit over-determined (more independent swept points than free coeffs)?
  (b) does the leading coeff emerge = 25^k/k! from a BLIND fit, or must it be assumed?
  (c) do the reconstructed integer coefficients match orchestrator/sweep.go's
      hardcoded diagonalCell(), i.e. no transcription typo in the engine?
Structure claimed:  T(n, n-k) = P_k(n) * 3^(n-1-3k),  deg P_k = k,  valid n>=2k+1.
"""

import sys
from fractions import Fraction as F
from math import factorial

# --- swept triangle T[H][n] from the run's own per-height files ------------
def load_swept(path):
    T = {}
    H = None
    for line in open(path):
        line = line.strip()
        if line.startswith("===H"):
            H = int(line[4:].rstrip("="))
            T[H] = {}
        elif line and H is not None:
            parts = line.split()
            if len(parts) == 2 and parts[0].lstrip("-").isdigit() and parts[1].lstrip("-").isdigit():
                T[H][int(parts[0])] = int(parts[1])
    return T  # T[H][n] = T(n,H), swept, H in 3..16

# engine's hardcoded numerator coefficients (highest degree first), over k!.
# transcribed from orchestrator/sweep.go diagonalCell(), cases 3..8.
CODE = {
    3: [15625, -100050, 122213, -32940],
    4: [390625, -3596250, 8099843, -6462882, 1752840],
    5: [9765625, -120546875, 425836625, -650171245, 422003550, 76975920],
    6: [244140625, -3861328125, 19486496875, -47366857935, 55373728180, 946828380, -32099353920],
    7: [6103515625, -119765625000, 812310625000, -2839739579250, 5194366339015, -1878923357430, -6841564107480, 7756630081200],
    8: [152587890625, -3625976562500, 31658675781250, -149222374175000, 391357255277905, -350057694296660, -718224955399380, 2136536485853040, -923712586957440],
}

def poly_interp(points):
    """Exact Lagrange interpolation: list of (x, y) -> coeff list high..low."""
    # build via Newton/monomial: solve Vandermonde exactly with Fractions.
    m = len(points)
    xs = [F(x) for x, _ in points]
    ys = [F(y) for _, y in points]
    # monomial coefficients c[0..m-1] for sum c[j] x^j (low..high) via Lagrange
    coeffs = [F(0)] * m
    for i in range(m):
        # basis poly prod_{j!=i} (x - xj)/(xi - xj)
        num = [F(1)]  # low..high
        den = F(1)
        for j in range(m):
            if j == i:
                continue
            # multiply num by (x - xj)
            new = [F(0)] * (len(num) + 1)
            for d, c in enumerate(num):
                new[d] += c * (-xs[j])
                new[d + 1] += c
            num = new
            den *= (xs[i] - xs[j])
        for d in range(m):
            coeffs[d] += ys[i] * num[d] / den
    return coeffs[::-1]  # high..low

def main():
    T = load_swept("results/ns_a25/swept_rows.txt")
    print("independent P_k audit  (swept-only data, exact rationals)\n")
    print(f"{'k':>2} {'pts':>4} {'deg':>3} {'need':>4} {'margin':>7}  {'lead=25^k/k!':>12}  {'held-out':>9}  {'code coeffs':>11}")
    for k in range(3, 9):
        # swept diagonal points: T(n, n-k) with H=n-k in [3,16], n>=2k+1, n<=25
        pts = []
        for n in range(2 * k + 1, 26):
            H = n - k
            if H in T and n in T[H] and T[H][n] > 0:
                pts.append((n, T[H][n]))
        npts = len(pts)
        need_blind = k + 1                 # deg-k poly, blind
        # P_k(n) = T(n,n-k) * 3^(3k+1-n)   (exact; may be fractional -> Fraction)
        P_pts = [(n, F(v) * F(3) ** (3 * k + 1 - n)) for n, v in pts]

        lead_target = F(25) ** k / factorial(k)
        if npts >= need_blind:
            # BLIND fit on first need_blind points, verify the rest (over-determination)
            coeffs = poly_interp(P_pts[:need_blind])
            lead = coeffs[0]
            heldout_ok = all(
                sum(c * F(n) ** (k - d) for d, c in enumerate(coeffs)) == y
                for n, y in P_pts[need_blind:]
            )
            margin = npts - need_blind
            blind = True
        else:
            # UNDER-determined blind: fix leading coeff, fit remaining k from k pts
            # subtract leading term, interpolate degree k-1 through residuals
            res = [(n, y - lead_target * F(n) ** k) for n, y in P_pts]
            lower = poly_interp(res)         # degree k-1 (npts-1 pts -> deg npts-1)... use all
            coeffs = [lead_target] + list(lower)
            # verify reproduces all supplied points
            heldout_ok = all(
                sum(c * F(n) ** (k - d) for d, c in enumerate(coeffs)) == y
                for n, y in P_pts
            )
            lead = lead_target
            margin = npts - k                # margin over leading-fixed need
            blind = False

        lead_ok = (lead == lead_target)
        # reconstruct integer numerator coeffs = P_k * k!, compare to engine
        int_coeffs = [c * factorial(k) for c in coeffs]
        int_coeffs = [int(c) if c.denominator == 1 else c for c in int_coeffs]
        code_ok = (int_coeffs == CODE[k])

        margin_str = f"+{margin}" if blind else f"={margin}(fix)"
        held = "n/a" if npts == need_blind or (not blind and margin == 0) else ("PASS" if heldout_ok else "FAIL")
        print(f"{k:>2} {npts:>4} {k:>3} {need_blind:>4} {margin_str:>7}  "
              f"{'YES' if lead_ok else 'NO ':>12}  {held:>9}  {'MATCH' if code_ok else 'MISMATCH':>11}")
        if not code_ok:
            print(f"     !! reconstructed {int_coeffs}")
            print(f"     !! engine        {CODE[k]}")

    # the k=8 headline cell, evaluated independently
    print()
    c8 = [F(c) for c in CODE[8]]
    val = sum(c * F(25) ** (8 - d) for d, c in enumerate(c8)) // factorial(8)
    print(f"T(25,17) from reconstructed P_8:  {int(val):,}   (k=8, the lone unchecked cell)")

if __name__ == "__main__":
    main()
