"""candidates/p3_columns.py -- Proposer 3 (slice recurrences).

Three candidates, all parameter-free (n_params = 0, no fit callable): every
number they use was computed ab initio by Proposer 3's own strip transfer
matrix (p3_striptm.py / p3_atoms.py), written from the lattice definition
only and cross-checked against Proposer 3's independent Redelmeier
enumerator on all cells n <= 12. No banked triangle data entered the
derivation.

  p3-col5-tm-value / p3-col6-tm-value
      T(n,H) for H = 5, 6 equals the ab-initio TM value (table
      data/p3_striptm_T.txt, T = S_H - 2 S_{H-1} + S_{H-2}).
      Columns H <= 4 are deliberately NOT claimed: known.py's
      column-C-finite predicate already covers them (would be
      KNOWN-COINCIDENT), and H <= 2 is the engine's own closed form.
      Post-refutation classification (results/triangle-hunt-refutation-
      columns.md, accepted): INDEPENDENT RECOMPUTATION, Tier B-equivalent
      scope, not a relation -- these recompute rather than predict; the
      tier field below is scope, not a prediction claim.

  p3-q5-strip-recurrence
      The weighted column combination C_5(n) = sum_{h<=5} (6-h) T(n,h)
      satisfies the exact order-29 constant-coefficient recurrence q_5
      computed ab initio (data/p3_atoms_q.txt), for all n >= 30. This is
      IN-GRID: the analogous statement for the T(n,5) column itself has
      minimal order 42 (q_5*q_4*q_3) with first valid instance n = 47 > 40,
      so it predicts nothing -- the C-combination is the only way the
      order-29 atom touches testable cells. Banked results fitted atoms only
      up to q_4 (results/triangle-structure.md: "H>=5 not pinnable from 35
      rows"); q_5 exists in this repo only as a measured degree, never as
      coefficients, and never enters any banked relation.

Run:  python3 verify.py candidates/p3_columns.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from schema import Candidate  # noqa: E402

_HERE = os.path.dirname(os.path.abspath(__file__))
_TBL = os.path.join(_HERE, os.pardir, "data", "p3_striptm_T.txt")
_QF = os.path.join(_HERE, os.pardir, "data", "p3_atoms_q.txt")

_table = None
_q5 = None


def _load_table():
    global _table
    if _table is None:
        _table = {}
        with open(_TBL) as f:
            for line in f:
                n, h, v = line.split()
                _table[(int(n), int(h))] = int(v)
    return _table


def _load_q5():
    global _q5
    if _q5 is None:
        with open(_QF) as f:
            for line in f:
                parts = line.split()
                if int(parts[0]) == 5:
                    assert int(parts[1]) == 29
                    _q5 = [int(x) for x in parts[2:]]
    return _q5


def _tm_predict(params, n, H, ctx):
    # pure table lookup of the ab-initio TM value; ctx never touched
    return _load_table()[(n, H)]


def _c5(n, t_n5, ctx):
    """C_5(n) using the passed target value for T(n,5) and ctx (same-row
    H' != 5 reads are legal for boolean kind) for the rest."""
    return t_n5 + sum((6 - h) * ctx.cell(n, h) for h in range(1, 5))


def _q5_check(params, n, H, value, ctx):
    q = _load_q5()
    s = _c5(n, value, ctx)
    for j in range(1, 30):
        m = n - j
        cm = sum((6 - h) * ctx.cell(m, h) for h in range(1, 6))
        s += q[j] * cm
    return s == 0


_INDEP = dict(
    input_footprint="zero banked cells in the derivation; predictions are "
                    "pure ab-initio TM output (value candidates) or consume "
                    "banked columns h<=5 of the 29 preceding rows "
                    "(q5 recurrence check)",
    derivation_independence="derivation-blind: strip TM written from the "
                            "lattice definition (p3_striptm.py), atoms from "
                            "Berlekamp-Massey + CRT + exact certification "
                            "over Z on the TM's own sequence (p3_atoms.py); "
                            "cross-checked only against p3_enum_out.txt, "
                            "Proposer 3's own enumerator, n<=12",
    rule_independence="authorship/code-lineage independence only, per the "
                      "second-source ruling (docs/second-source-team-brief"
                      ".md, branch second-source, 2b3115b): the algorithm "
                      "(union-find over |dy|<=1 cross-column adjacency, "
                      "stranded-component death) is the SAME IDEA as "
                      "core/transition.h and the kink kernel, so agreement "
                      "checks transcription/overflow/sharding, not the "
                      "shared connectivity rule; the rule itself is tested "
                      "independently only to n=12 by the four-enumerator "
                      "crosscheck. No repo kernel was consulted",
)


CANDIDATES = [
    Candidate(
        id="p3-col5-tm-value",
        proposer="p3-slices",
        statement="T(n,5) = S_5(n) - 2 S_4(n) + S_3(n) from the ab-initio "
                  "strip TM, all n (order-42 rational column, atoms "
                  "q_5 q_4 q_3 = 29+9+4)",
        tier="B", kind="value",
        region=lambda n, H: H == 5,
        n_params=0, predict=_tm_predict,
        bits_claimed=30.0,
        bits_justification="exact 10-20 digit integer match per cell against "
                           "an independently computed value; any wrong digit "
                           "fails; 30 bits/cell is a conservative cap, not "
                           "log2 of the value size",
        **_INDEP),
    Candidate(
        id="p3-col6-tm-value",
        proposer="p3-slices",
        statement="T(n,6) = S_6(n) - 2 S_5(n) + S_4(n) from the ab-initio "
                  "strip TM, all n (order-106 rational column, atoms "
                  "q_6 q_5 q_4 = 68+29+9)",
        tier="B", kind="value",
        region=lambda n, H: H == 6,
        n_params=0, predict=_tm_predict,
        bits_claimed=30.0,
        bits_justification="exact 10-20 digit integer match per cell against "
                           "an independently computed value; any wrong digit "
                           "fails; 30 bits/cell is a conservative cap",
        **_INDEP),
    Candidate(
        id="p3-q5-strip-recurrence",
        proposer="p3-slices",
        statement="C_5(n) = sum_{h<=5} (6-h) T(n,h) satisfies the exact "
                  "order-29 recurrence q_5 (ab initio, "
                  "data/p3_atoms_q.txt) for all n >= 30; linear with unit "
                  "coefficient in the target T(n,5), so any wrong target "
                  "fails given correct inputs",
        tier="B", kind="boolean",
        region=lambda n, H: H == 5 and n >= 30,
        n_params=0, check=_q5_check,
        bits_claimed=30.0,
        bits_justification="the check is linear in T(n,5) with coefficient "
                           "1: conditional on the consumed cells (columns "
                           "h<=5, rows n-29..n-1, plus same-row h<5) being "
                           "correct, a wrong T(n,5) passes with probability "
                           "0; 30 bits/cell is a conservative cap "
                           "acknowledging correlated-input failure modes",
        **_INDEP),
]
