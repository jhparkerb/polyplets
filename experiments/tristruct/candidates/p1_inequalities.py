"""Proposer 1 (proof-first): PROVED two-term cell inequality.

    T(n,H) >= 3*T(n-1,H-1) + T(n-1,H)   for 2 <= H <= n-1,
    with equality T(n,n) = 3*T(n-1,n-1) on the pure-walk column.

Proof (from the definition; no banked data): two injections with disjoint
images. (i) Walk-cap: to an (n-1)-cell height-(H-1) animal add a single cell
in a new top row at offset delta in {-1,0,+1} of the LEFTMOST top-row cell;
the result determines (animal, delta) uniquely (its top row is a single
cell; delete it, read the offset), so this is injective from 3 disjoint
copies; every image has top row = exactly one cell. (ii) Grow-right: to an
(n-1)-cell height-H animal add a cell immediately right of the top row's
rightmost cell; delete-the-top-right-cell inverts it; every image has >= 2
cells in its top row. Images of (i) and (ii) are disjoint by top-row size.

Verified on own enumeration (p1_ineq_check.py): 0 violations, equalities
exactly the H=n column, n <= 13 (later n <= 15).

Submitted for the record: as a one-sided bound this is VALUE-INSENSITIVE by
the harness's tautology guard (a +1 perturbation still passes), which is the
correct verdict on its checking power (near-zero bits against realistic
errors). Its worth is as a proved, zero-input structural fact -- and it is
asymptotically TIGHT on the k=1 diagonal (ratio 1.06 at (13,12), decreasing),
so it is not vacuous.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from schema import Candidate


def _check(params, n, H, value, ctx):
    lo = 3 * ctx.cell(n - 1, H - 1) + (ctx.cell(n - 1, H) if H <= n - 1 else 0)
    if H == n:
        return value == lo  # equality on the pure-walk column (proved)
    return value >= lo


CANDIDATES = [
    Candidate(
        id="p1-two-term-lower-bound",
        proposer="p1-proof-first",
        statement=("PROVED: T(n,H) >= 3T(n-1,H-1) + T(n-1,H) for "
                   "2<=H<=n-1; equality 3T(n-1,n-1) at H=n"),
        tier="softer", kind="boolean", scope="cell",
        region=lambda n, H: 2 <= H <= n and n >= 2,
        n_params=0, check=_check,
        input_footprint=("prediction consumes the two cells of row n-1 it "
                         "bounds from; derivation consumed nothing banked"),
        derivation_independence=("proved from the lattice definition alone; "
                                 "validated on own enumeration n <= 13"),
        rule_independence=("proof uses only king adjacency as defined; "
                           "own-code validation (p1_enum.cpp)"),
    ),
]
