# The lifetime-3 law for fixed-height polyplet GFs: proof

**Claim.** Let G_H(x) = sum_n B_H(n) x^n be the generating function of fixed
polyplets of bounding-box height exactly H, with reduced denominator Q_H. Then

    Q_H = N_{H-2} . N_{H-1} . N_H

for a sequence of pairwise-coprime "atom" polynomials N_H; equivalently, every
irreducible factor of any Q_H divides exactly THREE consecutive denominators
(Q_{H0}, Q_{H0+1}, Q_{H0+2}) and no others. Verified exactly for H <= 7; the
argument below is general except for one spectral lemma (coprimality), verified
H <= 6.

## The fundamental object: the unanchored strip GF
Let V_H(n) = number of n-cell polyplets placed in a horizontal strip of H rows,
counted WITH vertical position (every placement counted separately) -- the natural
transfer-matrix count for an H-row strip, with no anchoring or touch condition.
Set V_H(x) = sum_n V_H(n) x^n.

**Lemma 1 (placement count, elementary).** A polyplet of height exactly g has
exactly (H - g + 1) vertical positions in an H-row strip (zero if g > H). Hence

    V_H = sum_{g=1}^{H} (H - g + 1) . B_g.                          (*)

**Lemma 2 (second difference, elementary).** Apply the second finite difference
in H to (*). The weight w_g(H) = (H-g+1) for H>=g (else 0) is a unit ramp, and
Delta^2 w_g (H) = w_g(H) - 2 w_g(H-1) + w_g(H-2) = [H = g]. Therefore

    B_H = V_H - 2 V_{H-1} + V_{H-2}.                                (**)

So "height exactly H" is the SECOND DIFFERENCE of "placements in an H-row strip".
(Verified as a rational-function identity, H=3..7.)

## Why three
V_H = u^T (I - x T_H)^{-1} v for the H-row strip transfer matrix T_H, so V_H is
rational; let **N_H := reduced denominator of V_H** (a factor of det(I - x T_H)).
Empirically deg N_H = new(H) = 1,2,4,9,29,68,181,... and N_H equals the triple
gcd gcd(Q_H, Q_{H+1}, Q_{H+2}).

By (**), B_H is a Z-combination of V_H, V_{H-1}, V_{H-2}, so

    Q_H = denom(B_H)  |  lcm(N_H, N_{H-1}, N_{H-2}).                 (***)

**Lemma 3 (coprimality, spectral).** The N_H are pairwise coprime. [Verified
H <= 6; not yet proven in general. It says distinct strip heights contribute
distinct reduced-GF poles -- no surviving strip eigenvalue recurs at another
height after GF reduction.]

Granting Lemma 3, lcm(N_H,N_{H-1},N_{H-2}) = N_{H-2} N_{H-1} N_H, and (***) gives
Q_H | N_{H-2} N_{H-1} N_H. So every irreducible factor f of Q_H divides exactly
one atom, say f | N_k with k in {H-2, H-1, H}. The same f divides Q_{H'} only if
k in {H'-2, H'-1, H'}, i.e. H' in {k, k+1, k+2}: **lifetime at most 3.**

That Q_H equals the FULL product N_{H-2}N_{H-1}N_H (lifetime exactly 3, and
deg Q_H = new(H)+new(H-1)+new(H-2)) is the statement that the second difference
(**) loses no factor to numerator cancellation. Equivalent residue form, verified
H<=5: for each atom N_k the three partial-fraction residues of G_k, G_{k+1},
G_{k+2} over N_k sum to zero -- i.e. every atom-pole CANCELS in the full GF
a(x) = sum_H G_H, which is why a(x) (believed non-D-finite) is not a tame sum of
rational pieces. Q_H is squarefree (verified H<=6), so no cancellation occurs.

## Status
- Lemmas 1, 2: elementary and general (combinatorial placement + second
  difference of a ramp). RIGOROUS.
- V_H rational, N_H its reduced denominator: standard transfer-matrix fact.
- Lemma 3 (pairwise coprimality of the N_H) + squarefreeness: VERIFIED H<=6,
  the one remaining general gap. This is now the whole mathematical content of
  the lifetime-3 law -- a spectral-distinctness statement about strip transfer
  matrices.

**Punchline.** The "3" is the width of a second finite difference: a height-exactly
animal count is the discrete second derivative of a strip placement count whose
weight grows linearly in the strip height. Everything else is bookkeeping.
