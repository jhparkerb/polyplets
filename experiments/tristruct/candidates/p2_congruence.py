"""Proposer 2 (congruence/valuation/symmetry) candidates.

C1 -- PROVED forced-parity congruence on the {n odd, H even} region.

Theorem (proved from the lattice definition alone, no banked input):
for H even and n odd, T(n,H) is even.

Proof sketch (full statement in results/arithmetic-structure.md):
top-bottom reflection about the bounding-box horizontal midline is an
involution on the translation classes counted by T(n,H) (it preserves cell
count and box height). Its non-fixed points pair up, so T(n,H) is congruent
mod 2 to the number of tb-invariant animals. A tb-invariant animal with H
even has every column invariant under a fixed-point-free row reflection, so
every column has even size and n is even. Hence for n odd there are no fixed
points and T(n,H) is even.

This is NOT the ternary spine (mod 3), not the diagonal law, and not the
subgroup-census identity T = I_H(D2ax) mod 2 (results/symmetry-classes.md) --
that banked identity equates two computed quantities; this candidate needs
no computed input at all: the predicted residue is the constant 0, from a
proof. The sweep could not find it for a structural reason: it tests
whole-column residue patterns and has no hypothesis class for a region /
parity-class statement, so a claim over {n odd, H even} across all columns
at once is outside its search space by construction. (Some even-H columns
ARE periodic mod 2 -- H=4 period 4, found and culled by the sweep; H=6 and
H=8 period 8; see triangle-hunt-refutation-symmetry.md section 4.)

Honest a(40) accounting: row 40 has n even, so this region contains NO row-40
cell. Bits of independent check on a(40): ZERO. The value is 190 theorem-grade
parity bits on the n <= 39 triangle (1 bit per cell, log2(2), independent per
cell only against independent per-cell corruption; a systematic even-delta
corruption is invisible to any parity statement).
"""
from schema import Candidate

CANDIDATES = [
    Candidate(
        id="p2-c1-forced-parity-nodd-Heven",
        proposer="p2-congruence",
        statement=("T(n,H) == 0 (mod 2) whenever n is odd and H is even "
                   "(proved: tb-flip pairing; tb-invariance forces even n "
                   "when H is even)"),
        tier="C",
        kind="congruence",
        modulus=2,
        scope="cell",
        region=lambda n, H: (H is not None and n % 2 == 1 and H % 2 == 0
                             and H <= n),
        n_params=0,
        fit=None,
        predict=lambda params, n, H, ctx: 0,
        input_footprint=("derivation: none (proof from the definition; "
                         "sanity-checked on self-enumerated cells n<=13 from "
                         "p2_enum --sym, own connectivity rule). prediction: "
                         "consumes no banked cells (constant residue)."),
        derivation_independence=("blind: proof from the lattice definition; "
                                 "no banked data touched in derivation"),
        rule_independence=("rule-free: the statement is a theorem about king "
                           "connectivity itself; verified consistent with my "
                           "own enumerator (independent rule), not the "
                           "engines'"),
        bits_claimed=1.0,
        bits_justification=("congruence mod 2 = log2(2) = 1 bit per covered "
                            "cell; 190 cells in-region for n<=39; ZERO cells "
                            "in row 40 (n=40 is even) so 0 bits on a(40)"),
    ),
]
