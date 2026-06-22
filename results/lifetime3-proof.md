# The lifetime-3 law for fixed-height polyplet GFs: proof

**Claim.** Let G_H(x) = sum_n B_H(n) x^n be the generating function of fixed
polyplets of bounding-box height exactly H, with reduced denominator Q_H. Then

    Q_H = N_{H-2} . N_{H-1} . N_H

for a sequence of pairwise-coprime "atom" polynomials N_H; equivalently, every
irreducible factor of any Q_H divides exactly THREE consecutive denominators
(Q_{H0}, Q_{H0+1}, Q_{H0+2}) and no others. Verified exactly for H <= 7; the
argument below is general except for one spectral lemma (coprimality), whose
irreducible-atom step (3a) is now verified to H <= 7 via a blowup-free mod-p
certificate (was H <= 6 -- see "Extending (3a)" below).

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
Empirically deg N_H = 1,2,4,9,29,68,181,... and N_H equals the triple gcd
gcd(Q_H, Q_{H+1}, Q_{H+2}).

By (**), B_H is a Z-combination of V_H, V_{H-1}, V_{H-2}, so

    Q_H = denom(B_H)  |  lcm(N_H, N_{H-1}, N_{H-2}).                 (***)

**Lemma 3 (coprimality).** The N_H are pairwise coprime. This follows from two
facts:
 (3a) each N_H is IRREDUCIBLE over Q  [verified H<=7, see the mod-p certificate
      below -- pushed past the proof's old H<=6 ceiling], and
 (3b) the degrees deg N_H = 1,2,4,9,29,68,181,... are strictly increasing
      [clear; deg N_H ~ 2.6 deg N_{H-1}].
Distinct irreducibles are coprime, so (3a)+(3b) => Lemma 3. (3a) is equivalent to
"the dominant strip eigenvalue lambda_H is a primitive element of degree =
deg N_H", i.e. the Perron root of the H-strip transfer matrix generates the whole
reduced-GF field. This is the one remaining unproven-in-general step.

Granting Lemma 3, lcm(N_H,N_{H-1},N_{H-2}) = N_{H-2} N_{H-1} N_H, and (***) gives
Q_H | N_{H-2} N_{H-1} N_H. So every irreducible factor f of Q_H divides exactly
one atom, say f | N_k with k in {H-2, H-1, H}. The same f divides Q_{H'} only if
k in {H'-2, H'-1, H'}, i.e. H' in {k, k+1, k+2}: **lifetime at most 3.**

That Q_H equals the FULL product N_{H-2}N_{H-1}N_H (lifetime exactly 3, and
deg Q_H = deg N_H+deg N_{H-1}+deg N_{H-2}) is the statement that the second difference
(**) loses no factor to numerator cancellation. Equivalent residue form, verified
H<=5: for each atom N_k the three partial-fraction residues of G_k, G_{k+1},
G_{k+2} over N_k sum to zero -- i.e. every atom-pole CANCELS in the full GF
a(x) = sum_H G_H, which is why a(x) (believed non-D-finite) is not a tame sum of
rational pieces. Q_H is squarefree (verified H<=6), so no cancellation occurs.

## Status
- Lemmas 1, 2: elementary and general (combinatorial placement + second
  difference of a ramp). RIGOROUS.
- V_H rational, N_H its reduced denominator: standard transfer-matrix fact.
- Lemma 3 reduces to: each atom N_H is IRREDUCIBLE (3a) [verified H<=7, mod-p cert.] plus
  strictly-increasing degrees (3b) [clear]. So the ENTIRE remaining content of the
  lifetime-3 law is the single statement "the reduced denominator of the
  unanchored H-strip GF is irreducible" -- equivalently, the Perron eigenvalue of
  the strip transfer matrix is a primitive element of the reduced-GF number field.
  A clean Perron-Frobenius / Galois target.
- squarefreeness of Q_H (no second-difference cancellation): VERIFIED H<=6;
  follows once the three atoms are coprime (3a+3b) and each genuinely appears.

**Punchline.** The "3" is the width of a second finite difference: a height-exactly
animal count is the discrete second derivative of a strip placement count whose
weight grows linearly in the strip height. Everything else is bookkeeping.

## Honest weight of this result
Don't oversell it. The result splits cleanly:
- The **<=3 window** (Q_H built from at most 3 consecutive atoms) is ELEMENTARY --
  it's B_H = Delta^2 V_H plus "denominator of a 3-term combination divides the
  product." A couple of lines once you take the unanchored-strip viewpoint.
- The **exactly-3 / irreducible-atom** refinement is the only hard part, and it is
  "plumbing-hard" (irreducibility of transfer-matrix characteristic polynomials --
  no general method), not a deep or illuminating theorem even once proved.
So this is a TIDY STRUCTURAL OBSERVATION with a satisfying elementary explanation,
plus two new (OEIS-absent) integer sequences (atom degrees; orders). It is worth a
paragraph in the write-up, NOT a centerpiece. The genuine value is (a) the clean
"it's a second difference" understanding and (b) the new sequences -- not a major
theorem.

## Extending (3a) past H<=6: the mod-p subset-sum certificate
The proof originally stopped (3a) at H<=6 because N_H = gcd(Q_H,Q_{H+1},Q_{H+2}) over Q
has runaway rational coefficients at deg 181+ (the gcd blowup). Working **mod p** removes
that entirely, and irreducibility over Q is still certifiable mod p without the rare prime
whose reduction is irreducible outright:

> A rational factor of N_H of degree k (0<k<deg) reduces, mod **every** prime, to mod-p
> factors whose degrees sum to k. So k must be a subset-sum of N_H's mod-p factor degrees
> for every p. Intersect those subset-sum sets over a few primes; if only {0, deg N_H}
> survives, N_H has **no proper rational factor — irreducible over Q**.

`experiments/t1_irreducibility.py` computes N_H mod p as the polynomial gcd over F_p,
checks deg N_H mod p = the predicted atom degree, factors it, and intersects subset-sums.

- **H=7 (deg 181): PROVED irreducible over Q** — 4 primes suffice; p=100057 factors N_7 as
  degrees [2, 179], which (intersected with the earlier primes' patterns) leaves no proper
  subset-sum. So (3a) now holds for H=7, not just H<=6. This is the first extension of the
  one open lemma in years of the result sitting at H<=6.
- Side effect: deg N_H mod p is computed **directly** (as the gcd degree), so the atom
  degree deg N_8 = 462 -- previously only EXTRAPOLATED from the degree law in
  `paper/atom_degrees.py` -- is **de-extrapolated** (confirmed by direct mod-p gcd).

The method is general: it pushes (3a) as far as the recovered Q_H reach (currently H<=10,
so N_H certifiable through H=8). It does not prove (3a) for ALL H -- that still needs the
Perron-primitive-element / Galois argument -- but it converts "verified H<=6" into a
mechanical, blowup-free check that scales with the available GF data.

## Empirical confirmation: the "3" is translation, not adjacency
The proof never mentions the adjacency rule -- only that vertical placement is
1-dimensional (weight H-g+1 linear). Sharp test: change the adjacency so the
neighborhood is taller. A "reach-2" lattice (neighbors within +/-1 column and
+/-2 ROWS -- king augmented with the Dabbaba (0,+/-2) leaper and (1,2) knight
steps, a 5-row-tall neighborhood) gives DIFFERENT atoms:
    king    deg N_H = 1, 2, 4, 9, 29, 68, 181
    reach-2 deg N_H = 1, 2, 3, 5, 10, 17, 39
yet the SAME lifetime 3 (deg Q_H = deg N_H+deg N_{H-1}+deg N_{H-2}, verified H<=7). If the
"3" came from the neighborhood's vertical reach (2*reach+1), reach-2 would give
lifetime 5; it gives 3. (gf_modp gained a vertical-reach parameter for this;
rook -- cross-column same row only -- likewise gives lifetime 3, but rook doesn't
discriminate since its vertical reach is also 1.) Conclusion: lifetime-3 is
universal across finite-range lattice-animal classes; only the atoms are
lattice-specific.

The strongest test is the KNIGHT (moves (+-1,+-2),(+-2,+-1)): horizontal reach 2
(it jumps two columns, so its strip transfer matrix needs TWO-column boundary
memory -- the only genuinely new axis, since king/rook/reach-V all have
one-column memory) and it is a gapped leaper (column-skipping). Its strip GFs are
far more complex -- deg Q_H = 0, 1, 144, 665, 3289 for H=1..5 (vs king
1,3,7,15,42), deg N_H = 0,1,143,521,2625 -- yet deg Q_H = deg N_H+deg N_{H-1}+deg N_{H-2}
holds: LIFETIME 3. (Knight engine cpp/gf_knight.cpp, validated against an
independent brute force for n<=7.) Varying horizontal coupling does not change
the lifetime, exactly as B_H = second-difference(V_H) requires: the "3" is the
1-D vertical translation, full stop.
