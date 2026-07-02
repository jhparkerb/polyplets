#!/usr/bin/env python3
"""Calibration step for the P_9 derivation.

Reconstruct P_k(n) for k=3,4,5,6 from the log S(y) = log A(y) + n*B(y)
series in docs/proofs/T-n-nm2-and-general.md Section 2, and check the
result matches the hardcoded closed forms in orchestrator/sweep.go
diagonalCell (cases 3-6) EXACTLY, as integers, before trusting the same
machinery for k=9 (where only a_1..a_6, b_1..b_6 are known).

If this calibration does not reproduce the known polynomials exactly,
the whole P_9 partial-derivation approach is unsound and must not be used.
"""
from fractions import Fraction as F
import sympy as sp

y, n = sp.symbols("y n")

# From docs/proofs/T-n-nm2-and-general.md Section 2 table:
# coeff of y^k in log S = a_k + n*b_k
a = {
    1: F(-45),
    2: F(-891, 2),
    3: F(-10350),
    4: F(-846963, 4),
    5: F(-3781134),
    6: F(-119091015),
}
b = {
    1: F(25),
    2: F(-209, 2),
    3: F(4474, 3),
    4: F(-22701, 4),
    5: F(16144),
    6: F(15126941, 3),
}

MAXK = 6  # only a_1..a_6, b_1..b_6 are solid ground truth for calibration

logA = sum(sp.Rational(a[j].numerator, a[j].denominator) * y**j for j in range(1, MAXK + 1))
Bser = sum(sp.Rational(b[j].numerator, b[j].denominator) * y**j for j in range(1, MAXK + 1))

A = sp.series(sp.exp(logA), y, 0, MAXK + 1).removeO()
S = sp.series(A * sp.exp(n * Bser), y, 0, MAXK + 1).removeO()
S = sp.expand(S)

# Hardcoded closed forms from orchestrator/sweep.go diagonalCell (the
# polynomial P_k(n) BEFORE multiplying by pow3(n-1-3k) -- i.e. the bracketed
# numerator/denominator part of each `case k:` line).
Pk_known = {
    3: (15625 * n**3 - 100050 * n**2 + 122213 * n - 32940) / sp.Integer(6),
    4: (390625 * n**4 - 3596250 * n**3 + 8099843 * n**2 - 6462882 * n + 1752840) / sp.Integer(24),
    5: (9765625 * n**5 - 120546875 * n**4 + 425836625 * n**3 - 650171245 * n**2 + 422003550 * n + 76975920) / sp.Integer(120),
    6: (244140625 * n**6 - 3861328125 * n**5 + 19486496875 * n**4 - 47366857935 * n**3 + 55373728180 * n**2 + 946828380 * n - 32099353920) / sp.Integer(720),
}

print("Calibration: reconstruct P_k(n) from log S = log A(y) + n B(y), k=3..6")
print("=" * 70)
all_ok = True
for k in (3, 4, 5, 6):
    Pk_derived = sp.expand(S.coeff(y, k))
    Pk_ref = sp.expand(Pk_known[k])
    diff = sp.simplify(Pk_derived - Pk_ref)
    ok = diff == 0
    all_ok &= ok
    print(f"\nk={k}:")
    print(f"  derived : {Pk_derived}")
    print(f"  ref     : {Pk_ref}")
    print(f"  match   : {ok}")

print()
print("=" * 70)
print(f"ALL CALIBRATIONS MATCH: {all_ok}")
