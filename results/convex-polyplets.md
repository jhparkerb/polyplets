# Convex polyplets — SEE docs/proofs/convex-mirage.md (prior, deeper)

**Entry point, 2026-08-05:** the convex/directed family as a whole is indexed
by `results/middle-kingdom.md` (the 5x4 grid, the novel cells, the b-files and
the staged OEIS comments). This note holds the convex-polyplet derivations and
measurements the campaign's Phases 1a, 1b and 2 produced; read the index first.

Date: 2026-07-10. **Integration correction:** convex polyplets were already
investigated, more thoroughly, in **`docs/proofs/convex-mirage.md`** ("Convex
Mirage"). This note re-derived a subset of that and is retained only for the few
additive pieces below. The primary source is convex-mirage.

## What convex-mirage already established (the real result)

- **Convex polyplet** = HV-convex king animal (every row and column a single
  contiguous run; king-connected). Same object.
- Sequence by area, **38 terms**: 1, 4, 16, 61, 221, 766, 2566, 8390, 26982,
  85834, 271174, 853111, … (via a ROW transfer matrix, state
  `(left-phase, right-phase, width)`).
- Growth **μ ≈ 3.129**.
- **The finding:** convex polyplets by area are **empirically non-D-finite**
  (holdout-validated P-recurrence guesser fails; the convex-polyomino control
  failing is the discriminator). "Convex" is a *perimeter* tractability lever,
  not an *area* one — hence "Mirage."

## What THIS session actually added (the only additive bits)

- An **independent brute-force cross-check** of the first 10 terms
  (`experiments/convex_polyplets.py` here is a Redelmeier-growth + HV-convex
  filter, reproducing A006770 through n=10 and the convex counts 1,4,16,…,85834).
  NOTE: this brute version is inferior to convex-mirage's transfer matrix (it caps
  ~n=10; **it does NOT reach 38 terms** — convex-mirage's "reproduce with
  convex_polyplets.py 38" now needs the transfer-matrix version restored, which
  was lost before this session).
- Sonnet lit/OEIS check: NOT in OEIS; no king convex enumeration in the
  literature (all classical convex work is edge-connected). Classical anchors:
  Bender 2.30914 (convex polyominoes by area), Temperley column-convex 3.2056.
- Framing as a λ lower bound: μ≈3.129 is a valid but WEAK lower bound on
  λ_polyplet (~7.11), far below the banked directed/multi-directed 5.828/6.475
  (results/directed-king-animals.md) — which in turn sit inside the rigorous
  two-sided bracket, 6.543 ≤ λ ≤ 9.3154 as of 2026-07-31 (lower: certified strip
  ladder, results/strip-mu-certificates.md; upper: ../docs/proofs/polyplet-upper-bound.md).
  So convex is NOT useful as a bound.

## Status

Convex polyplets are a real, novel-to-OEIS sequence but a documented tractability
mirage (non-D-finite by area). If submitted (OEIS Candidate C, deferred), use
convex-mirage's 38 terms + the non-D-finite finding, not this note's 10.
**TODO CLOSED 2026-07-13:** the transfer-matrix tool is restored as
`experiments/convex_tm.py` (row intervals, unimodal-envelope phase automaton,
unique parse); regenerates all 38 terms, first 20 matching convex-mirage's
reference exactly; mu = 3.12894 confirmed. Structural note: the unbounded
interval width is the same mechanism behind the all-pairs cluster family's
non-C-finiteness (results/defect-gas.md, 2026-07-13) -- one phenomenon, two
guises.

**Perimeter counting (2026-07-13, `experiments/convex_perimeter.py`):** the
mirage refines cleanly. By SEMIPERIMETER (= box W+H; for convex animals the
edge-perimeter is 2(W+H)), king convex polyplets are **D-finite**: series
1, 2, 9, 36, 154, 668, 2916, 12740, ... with a holdout-verified P-recurrence
(order 5, degree 2, fitted s<=25 predicting 8 later terms, s<=36); the
polyomino control reproduces A005436 exactly and its recurrence at (2,4)
calibrates the guesser. Perimeter growth ratio ~4.13 and falling. So:
**area wild (non-D-finite), perimeter tame (D-finite) — for both families**;
convexity is a perimeter lever for king animals exactly as for polyominoes.
The perimeter sequence is a second OEIS-eligible novel sequence.


## K2: column-convex polyplets SOLVED — and already known (2026-07-14)

Temperley method (catalytic last-column height; king-touch gives h+h'+1
placements) closes to a 2x2 linear system:
GF = x(1-x)^3/(1-7x+13x^2-10x^3+2x^4), growth 4.64468... (quartic root).
Brute-validated n<=8. **Rediscovery: this is OEIS A187077** (row-convex
polyplets, transpose-equivalent), same GF verbatim. Not submittable, but
the pipeline (functional equation -> GF -> brute -> OEIS) is now validated
end-to-end as the template for the kernel-method items (K1, K3).
Tool: `experiments/colconvex_king.py`.


## A187077 provenance check (2026-07-14)

Worry raised and settled by measurement. Our column-convex GF agrees with
(1) our functional equation, (2) our independent brute force (which also
reproduces A006770 n<=8 as control), and (3) Bevan's 23 published terms.
The OEIS entry's comment "Equivalent to a sequence of row-convex polyhexes
(A059716)" is measurably WRONG in its plain reading: brute-forcing the hex
lattice (control: all polyhexes == A001207 exactly) gives row-convex
polyhexes == A059716 == 1,3,11,42,162,... != A187077 == 1,4,18,83,385,...
Structural reason: a king row-interval has h+h'+1 placements against the
next row; a hex brick-row has h+h'. The entry contains no derivation, so
our Temperley derivation may be the only explicit one on record; a
correction comment + derivation would be the valuable OEIS contribution
here (jasonp's call).

**Draft correction comment (staged 2026-08-05, jasonp's call):**

> The comment "Equivalent to a sequence of row-convex polyhexes (A059716)" is
> not correct in its plain reading. Row-convex polyhexes are counted by
> A059716 itself, 1, 3, 11, 42, 162, ..., while this sequence is 1, 4, 18,
> 83, 385, ..., so the two agree only at the first term, and their generating
> functions differ. Checked by direct enumeration on both lattices, with all
> fixed polyhexes reproducing A001207 as a control. The two classes are
> analogous but not equinumerous, and one placement is the whole difference:
> a row of length h admits h + h' + 1 positions for a length-h' row beside it
> on the king lattice, against h + h' on the hexagonal lattice. What this
> sequence counts is row-convex polyplets -- king-lattice animals (sets of
> cells of Z^2 joined by edge or corner contact, counted up to translation)
> in which every row is a single contiguous run. Column-convex polyplets are
> the transpose and give the same counts. Verified for n <= 14 by direct
> enumeration.

**Draft Formula-section line (same edit, the entry carries no derivation):**

> The g.f. follows from Temperley's method with the height of the last column
> as catalytic variable (working with the transposed, column-convex form).
> Writing F(x,q) for the sum of x^cells * q^(height of the last column), the
> h + h' + 1 placement rule gives F(x,q) = t/(1-t) + A*t*(2-t)/(1-t)^2 +
> B*t/(1-t) with t = q*x, A = F(x,1), B = F_q(x,1); the two equations
> obtained at q = 1 solve to A(x) = x*(1-x)^3/(1 - 7x + 13x^2 - 10x^3 + 2x^4).

Prior text for both edits, written 2026-07-14, is in
`oeis/draft-comments-subfamilies.txt`; the versions above are the current
ones. The "n <= 14" bound is the brute-force grid pass
(`results/mk_grid20_n14.txt`, column-convex column: 1, 4, 18, 83, 385, 1788,
8305, 38575, 179170, 832189, 3865253, 17952864, 83385309, 387298083), which
agrees termwise with the GF above; the GF separately reproduces all 23 terms
the entry carries. Also relevant to the entry, from
`results/middle-kingdom-phase3.md`: every column-convex king animal is
multi-directed (Proposition 5), so A187077 is simultaneously the
multi-directed x column-convex cell of the grid.

## Extended to n=500 (2026-08-05, docs/middle-kingdom-plan.md Phase 1a)

`experiments/convex_tm.py`'s inner `dl` loop was a per-offset loop doing a
full O(N) vector add for each of O(w) offsets, all landing on one of at
most 4 `(left-phase, right-phase)` targets -- a box-convolution collapsible
to O(1) sub-intervals (min/max clipping to the 4 targets) each contributing
one scaled add. That change alone (N^5 -> N^4 per the plan's own estimate)
reproduces all 128 prior MEASURED terms byte-for-byte, including the n=128
spot value, in 8.3s (was 110.7s) -- but n=200 still took 47.9s and n=500
extrapolates to ~30 min, over the 10-minute laptop budget, so per the plan's
fallback it was also ported to C++/GMP: `cpp/convex_area_tm.cpp` ->
`build/convex_area_tm`, same DP verbatim (states, transitions, the same
box-collapse) on `mpz_class`. Verified identical to the Python port at
n=128 and n=200.

| n | tool | wall_s | peak_rss_mb |
|---|---|---|---|
| 100 | convex_tm.py (prefix-sum) | 3.07 | 17.2 |
| 128 | convex_tm.py (prefix-sum) | 8.31 | — |
| 200 | convex_tm.py (prefix-sum) | 47.92 | 23.3 |
| 128 | convex_area_tm (C++/GMP) | 0.30 | 6.6 |
| 200 | convex_area_tm (C++/GMP) | 1.65 | 14.2 |
| 500 | convex_area_tm (C++/GMP) | 75.6 | 108.4 |

500 terms in `results/convex_area_terms_n500.txt` (`n value` per line).
Ratio at n=496..500: 3.128943269730886 flat to 16 digits -- confirms
mu=3.12894 (Phase 2's "8+ significant figures" target is a differential-
approximant job on this series, not done here). Reproduce:
`make build/convex_area_tm && build/convex_area_tm 500`.

## Extended to s=200 (2026-08-05, docs/middle-kingdom-plan.md Phase 1b)

Same treatment on `experiments/convex_perimeter.py`'s `count_by_box`, but the
box-by-box DP stores exact column boundaries `(l, r)` (needed for future
transitions), not a phase-relative delta -- so, unlike Phase 1a, distinct `rp`
values can't be *merged* into one scaled count. What DOES collapse: the O(W)
inner `rp` loop, for a fixed `lp`, adds the *same* `v` to every `rp` in a
contiguous range -- a textbook range-update, done as a 1D difference array per
`(lp, npl, tLp, npr, tRp)` bucket, marked in O(1) per `lp` and materialized
with one O(W) prefix-sum sweep per bucket after all source states are
processed (the `lp` loop itself stays explicit, so this is ~S^6 -> ~S^5, not
the ~S^5 -> ~S^4 Phase 1a got). Verified against the original nested-loop
version at Smax in {12, 20, 30} (exact match, both king and the A005436
polyomino control) before porting; the C++/GMP port (`cpp/convex_perim_tm.cpp`
-> `build/convex_perim_tm`) matched the Python port exactly at Smax=30, both
series (king: 1,2,9,...,189738142469481640; control: A005436 through the same
range).

| s | tool | wall_s | peak_rss_mb |
|---|---|---|---|
| 36 | convex_perimeter.py (orig) | 10.26 | — |
| 36 | convex_perimeter.py (rp-collapsed) | 1.44 | — |
| 60 | convex_perimeter.py (rp-collapsed) | 21.8 | — |
| 60 | convex_perim_tm (C++/GMP) | 2.44 | 6.3 |
| 100 | convex_perim_tm (C++/GMP) | 34.0 | 78.6 |
| 200 | convex_perim_tm (C++/GMP) | 1246.4 | 345.5 |

199 terms (s=2..200) in `results/convex_perim_terms_s200.txt` (`s value` per
line). **Acceptance held on the strong holdout**: the banked order-5 degree-2
P-recurrence, fitted on the first 22 rows only (s<=~24) via
`experiments/convex_perimeter.py`'s `find_prec`, predicts every one of the
remaining 172 rows correctly out to s=200 -- a much stronger holdout than the
original s<=36 check (`find_prec(pk, 5, 2)` returns non-None on the full
199-term series, and `find_prec` always trains on the first `unknowns +
train_extra` rows regardless of series length, so this genuinely re-uses the
s<=22 fit, not a refit). Ratio still falling at s=200: 4.02172 (s=199->200),
consistent with "~4.13 and falling." Reproduce: `make build/convex_perim_tm
&& build/convex_perim_tm 200 1`.

## The perimeter lever survives directedness -- and the GF is algebraic (2026-08-05, followups Phase 2b)

`docs/middle-kingdom-followups-plan.md` Phase 2b, on the sibling series
`results/mk_dir4_perim_terms_s200.txt` (199 terms, s = 2..200) that Phase 2a
generated and validated: **(dir4, HV-convex) king animals by semiperimeter**,
i.e. the half-plane-4-cone-directed subpopulation of the series above. The
question was whether "area wild, perimeter tame" is a property of HV-convexity
itself or an accident of the unrestricted class. It is the former, and the
answer is sharper than D-finite.

**Verdict: algebraic.** The generating function `F(t) = sum_s a(s) t^s`
satisfies `sum_{j=0..4} q_j(t) F^j = 0` with `deg q_j <= 22`. The box `(4,22)`
has **nullity exactly 1** on 200 rows at both of `prec_guess`'s primes, so the
relation is unique up to scale, and it was then recovered **exactly over Q**
(`experiments/dir4_perim_find_alg.py`, exact-Fraction elimination, no modular
step): fitted on the first 119 rows, it annihilates all 81 later rows, and
re-substituted into the integer series it annihilates **all 200 rows over Z**,
0 failures. The primitive integer form, low degree first, is

```
q_0 = 9t^4 -120t^5 +676t^6 -2140t^7 +4283t^8 -5576t^9 +4198t^10 -906t^11
      -1270t^12 +1350t^13 -96t^14 +364t^15 +888t^16 +526t^17 +349t^18
      +246t^19 +98t^20 +16t^21 +t^22
q_1 = -30t^3 +482t^4 -3174t^5 +11056t^6 -21912t^7 +24026t^8 -9132t^9
      -11860t^10 +13626t^11 +492t^12 -2894t^13 +6540t^14 +8332t^15 +7390t^16
      +6696t^17 +4312t^18 +1616t^19 +314t^20 +24t^21
q_2 = 37t^2 -700t^3 +5389t^4 -21320t^5 +44037t^6 -37722t^7 -13978t^8
      +48384t^9 -20464t^10 -33324t^11 +20515t^12 +32808t^13 +26909t^14
      +36302t^15 +40156t^16 +26936t^17 +10841t^18 +2516t^19 +286t^20 +8t^21
q_3 = -20t +438t^2 -3916t^3 +17882t^4 -40900t^5 +28522t^6 +51028t^7
      -69112t^8 -44984t^9 +48224t^10 +20452t^11 -21166t^12 +31956t^13
      +110234t^14 +124676t^15 +81772t^16 +34364t^17 +9190t^18 +1424t^19
      +96t^20
q_4 = 4 -100t +1029t^2 -5446t^3 +14407t^4 -10250t^5 -32039t^6 +43974t^7
      +65620t^8 -55556t^9 -141788t^10 -55634t^11 +115295t^12 +212542t^13
      +190333t^14 +112426t^15 +46834t^16 +13732t^17 +2689t^18 +312t^19
      +16t^20
```

Coefficients of five digits, not the sixty-digit integers a rank defect
absorbed from 199 large terms would produce, are themselves evidence: the
`(19,3)` P-recurrence below, which is a *non-minimal* description of the same
object, has coefficients of ~60 digits.

**The box is minimal in both directions.** `(4,21)` is EXCLUDED, and so is
every algebraic degree below 4 as far as 199 terms reach: degree 3 to t-degree
48, degree 2 to 65, degree 1 (i.e. rational) to 98.

**P-recurrence, same verdict from the other tool.** The plan's named tool,
`experiments/convex_perimeter.py`'s `find_prec`, finds an exact rational
P-recurrence in the box `(J, D) = (19, 3)`, 80 unknowns, **trained on the
first 84 rows and predicting all 96 remaining rows** -- the Phase 1b holdout
discipline verbatim, and a re-substitution check over Q gives 0 failures on
all 180 rows (`experiments/dir4_perim_find_prec.py`,
`results/dir4_perim_find_prec.log`). `prec_guess` puts nullity 1 there on both
primes and on a 20-row skip, so the recurrence holds from the start and
eventually. Neighbouring boxes `(19,2)` and `(18,3)` are EXCLUDED, so `(19,3)`
is minimal on the frontier. The frontier itself -- the smallest order at which
each degree stops being EXCLUDED, everything below and left of it excluded --
is `(27,2) (19,3) (17,4) (15,5) (15,6) (14,7) (14,8) (13,9) (13,10) (13,11)
(13,12)`; degrees 0 and 1 are excluded as far as 199 terms reach (order 70 and
65).

**Note what this does NOT say.** The identity is verified on the 199 terms in
hand -- exactly, over Z, with 81 of them (algebraic) and 96 of them
(P-recurrence) never seen by the fit. It is not a proof that the relation
continues past s = 200. The cheapest strengthening available is an
out-of-sample enumerator run: `build/convex_perim_tm 206 1 dir4` at an
estimated ~21 min from Phase 2a's measured 1072.7 s at s = 200 and the DP's
~S^5 cost, giving six terms predicted before they were computed. Not run here.

### The controls, all four arms plus two more

A positive verdict needs the opposite discipline from
`tests/gate_convex_dfinite.py`'s negative one: there, the risk is an
underpowered guesser; here, it is a guesser that says CANDIDATE to anything.
Both risks are covered.

| arm | what it is | must be | is |
|---|---|---|---|
| prec + | unrestricted HV-convex by semiperimeter, banked (5,2) recurrence | CANDIDATE | nullity 1, predicts all 172 held-out rows |
| prec - | same series, box (2,1) | EXCLUDED | rank 6 of 6 |
| alg + | A005436, algebraic by Delest-Viennot, box (2,8) | CANDIDATE | nullity 1, holds on all 69 held-out rows |
| alg - | same series, box (2,4) | EXCLUDED | rank 15 of 15 |
| **null** | **199 terms of the by-area king series** -- same length, rigorously non-D-finite (EXCLUDED at (24,24) on 700 terms) | EXCLUDED in every box where dir4 is a candidate | EXCLUDED, nullity 0, at every box tested here -- both modes, all five scripts |
| **power** | the unrestricted (D-finite) series in the very boxes that decide dir4 | CANDIDATE | CANDIDATE with the holdout fully passing at every box that contains its own order-5 operator; EXCLUDED only at `(2,62)`, whose order 2 is below 5 |

The null control is the arm that matters for a positive claim, and it is why
the high-order candidates could be trusted at all: `(17,9)`, `(30,4)`,
`(48,2)` and the rest come back EXCLUDED with nullity 0 on a series of
identical length and comparable term size, so a 199-term matrix of that shape
does not manufacture rank defects.

The **nullity law** is the internal consistency check. A genuine minimal
`(K0, L0)` relation forces nullity `(K-K0+1)(L-L0+1)` as the box opens, since
`F^i t^j P` all lie in the larger box. Measured against predicted for
`(K0, L0) = (4, 22)`, over the whole decidable region:

```
        L=20  21  22  23  24  25  26  27  28        L=20  21  22  23  24  25  26  27  28
  K=3      0   0   0   0   0   0   0   0   0   K=3     0   0   0   0   0   0   0   0   0
  K=4      0   0   1   2   3   4   5   6   7   K=4     0   0   1   2   3   4   5   6   7
  K=5      0   0   2   4   6   8  10  12  14   K=5     0   0   2   4   6   8  10  12  14
  K=6      0   0   3   6   9  12  15  18   -   K=6     0   0   3   6   9  12  15  18   -
  K=7      0   0   4   8   -   -   -   -   -   K=7     0   0   4   8   -   -   -   -   -
     measured (dir4)                                predicted by (4,22)
```

Cell for cell. The same grid on the null control is all zeros.

### The unrestricted series is algebraic too, at degree 2

Measured in this phase as the contrast, and it strengthens rather than
replaces the banked "D-finite, order 5 degree 2" above: the unrestricted
HV-convex-king-by-semiperimeter GF satisfies a **quadratic**, minimal box
`(2, 9)`, nullity 1, fitted on 34 rows and holding on all 166 later ones,
0 failures over Z:

```
q_0 = 2t^2 -21t^3 +88t^4 -196t^5 +242t^6 -119t^7 +72t^8 +16t^9
q_1 = -4t +52t^2 -252t^3 +554t^4 -520t^5 +96t^6 +128t^7
q_2 = 2 -31t +176t^2 -416t^3 +256t^4 +256t^5
```

`(2,8)` is EXCLUDED, and rational is excluded to t-degree 98. So the two
classes sit one step apart in the same hierarchy: **HV-convex quadratic,
(dir4, HV-convex) quartic** -- the 4-cone restriction raises the algebraic
degree from 2 to 4 and the t-degree from 9 to 22, and does not leave the
algebraic class. This is the same shape of answer
`docs/proofs/convex-mirage.md` gives for why perimeter is the tractable
statistic ("the classical solvability is by perimeter").

### Why this is the interesting way for it to land

By **area**, the 4-cone restriction changes nothing about tractability:
(dir4, HV-convex) by area is not D-finite at order <= 24 / degree <= 24 and
not algebraic at degree <= 20 / t-degree <= 20 on 700 terms, exactly like the
unrestricted series (`results/middle-kingdom-phase3.md`). By
**semiperimeter**, both are algebraic. The wild/tame split is therefore a
property of the statistic crossed with HV-convexity, and it is robust to a
directedness constraint that is strong enough to cut the population to ~1% by
s = 200 (`results/mk-dir4-perimeter.md`) and to change the subdominant
singularity (0.8037 against 0.4810, Table B of the followups plan). A
constraint that moves the second singularity and the amplitude, and leaves the
GF class alone.

Pinned by `make gate-dir4-perim-alg` (`tests/gate_dir4_perim_alg.py`, 3.4 s):
the quartic coefficient for coefficient, its minimality both ways, the nullity
law at four boxes, the null control, the A005436 control, and the degree-2
result for the unrestricted series. RED-first: flipping one coefficient of
`q_0` turns it RED on that arm alone.

Reproduce (every step is seconds; nothing here needed more than 3.5 s wall or
21 MB RSS):

```
make build/prec_guess
scripts/dir4_perim_dfinite_sweep.sh        # 40 boxes, both modes, 4 control arms
scripts/dir4_perim_dfinite_nullcontrol.sh  # the same boxes on the null control
scripts/dir4_perim_boundary_scan.sh        # the exclusion frontier, with holdouts
scripts/dir4_perim_minimal_box.sh          # minimal boxes, second prime, skip rows
scripts/dir4_perim_nullity_grid.sh         # the nullity law, measured vs predicted
python3 experiments/dir4_perim_find_alg.py 4 22    # the quartic, exact over Q
python3 experiments/dir4_perim_find_prec.py 19 3   # the P-recurrence, exact over Q
make gate-dir4-perim-alg
```

Logs: `results/dir4_perim_dfinite.log`, `results/dir4_perim_nullcontrol.log`,
`results/dir4_perim_boundary.log`, `results/dir4_perim_minimal_box.log`,
`results/dir4_perim_nullity_grid.log`, `results/dir4_perim_nullity_ladder.log`,
`results/dir4_perim_find_alg.log`, `results/dir4_perim_find_prec.log`,
`results/hv_perim_find_alg.log`.

## Non-D-finite at order<=24, degree<=24; mu to 199 digits (2026-08-05, Phase 2a/2b)

`docs/middle-kingdom-plan.md` Phase 2a/2b. The banked verdict
(`docs/proofs/convex-mirage.md`) was "no P-recurrence of order <= 6, degree
<= 5" on 38 terms, for the king series and for the classical
convex-polyomino-by-area control. Both are now excluded at **order <= 24,
degree <= 24 on 700 terms**, and separately shown to satisfy no low-degree
algebraic equation. The growth constants are pinned to 199 and 121 digits
respectively, `theta = 0` is measured rather than assumed, and neither mu is
algebraic in the searched box.

### The control, generated here

The control is HV-convex **polyominoes** by area: 1, 2, 6, 19, 59, 176, 502,
1374, 3630, 9312, 23320, 57279, 138536, 331032, ... = **A067675** (fixed
convex polyominoes by cell count; identified by web search -- oeis.org itself
returns HTTP 403 to this environment, so the entry's term count was not read
and no b-file was consulted). 38 terms cannot support an order-20 ansatz, so
the control was regenerated locally to the same length as the king series.

Adjacency is the only difference and it is a two-line change in
`cpp/convex_area_tm.cpp`, now switchable: `build/convex_area_tm N [king]`,
king default 1. Writing `dl = l' - l` for the horizontal shift of the new row
onto a bottom row of width `w`, king reach (`l' <= r+1`, `r' >= l-1`) is
`dl` in `[-wp, w]`; edge adjacency needs a shared column (`l' <= r`,
`r' >= l`), i.e. `dl` in `[-wp+1, w-1]`. Same states, same phases, same
box collapse. The bound was not guessed -- it is the same rule
`cpp/convex_perim_tm.cpp` already used for its own king=0 control
(`min(W-1, king ? r+1 : r)` / `kingOff = king ? l-1 : l`), and it reproduces
all 14 known control terms. (The `king=False` mode that
`docs/proofs/convex-mirage.md` attributes to
`experiments/convex_polyplets.py` went with the transfer matrix that file lost
in 2026-07; what is there now is the brute-force cross-check. `king=0` on
`build/convex_area_tm` is its replacement.)

| series | file | wall_s | peak_rss_mb |
|---|---|---|---|
| king, n=700 | `results/convex_area_terms_n700_king.txt` | 484.5 | 271.9 |
| control (A067675), n=700 | `results/convex_area_terms_n700_poly.txt` | 409.9 | 225.6 |

Run concurrently on gympie. The king file's first 500 lines are byte-identical
to the banked `results/convex_area_terms_n500.txt`.

### What "exclude order<=20, degree<=20" required testing: one box, not 441

`build/prec_guess` (`cpp/prec_guess.cpp`) tests the ansatz

```
sum_{i=0..J} p_i(n) a(n+i) = 0,   deg p_i <= D
```

by building the integer matrix with rows indexed by `n` and columns by
`(i, d)`, entry `n^d a(n+i)`, and taking its rank mod a prime.

Two things make this a one-shot test rather than a 21x21 sweep:

- **The boxes nest.** A solution with `J' <= J` and `D' <= D` is a solution of
  the `(J, D)` ansatz with the unused `p_i` set to zero. Excluding the maximal
  box excludes every box inside it. So `(20, 20)` alone settles order <= 20 and
  degree <= 20; `(24, 24)` was run too and settles the larger claim.
- **Full column rank mod p is a proof over Q.** The entries are integers. Full
  column rank mod `p` means some maximal minor is nonzero mod `p`, hence
  nonzero over Q, hence the only rational solution is trivial. Rank can drop
  mod p, never rise, so this direction is rigorous. (A rank *defect* mod p
  would only be a candidate -- that is the branch that gets the holdout and the
  second prime.)

Because a full-rank verdict uses every row, no train/test split is needed for
it; the holdout numbers below are reported anyway, since they are what
distinguishes a real find from an overfit when the rank *is* deficient.

Results, `p = 2^61-1` unless noted (`prec` = P-recurrence, `alg` =
`sum_j q_j(t) F(t)^j = 0`, `deg q_j <= L`):

| series | mode | box | unknowns | rows | rank | verdict |
|---|---|---|---|---|---|---|
| king | prec | (20,20) | 441 | 680 | 441 | EXCLUDED |
| king | prec | (24,24) | 625 | 676 | 625 | EXCLUDED |
| king | prec | (20,20), skip 50 rows | 441 | 630 | 441 | EXCLUDED |
| king | prec | (20,20), second prime | 441 | 680 | 441 | EXCLUDED |
| king | alg | (20,20) | 441 | 701 | 441 | EXCLUDED |
| king | alg | (24,24) | 625 | 701 | 625 | EXCLUDED |
| control | prec | (20,20) | 441 | 680 | 441 | EXCLUDED |
| control | prec | (24,24) | 625 | 676 | 625 | EXCLUDED |
| control | prec | (20,20), skip 50 rows | 441 | 630 | 441 | EXCLUDED |
| control | prec | (20,20), second prime | 441 | 680 | 441 | EXCLUDED |
| control | alg | (20,20) | 441 | 701 | 441 | EXCLUDED |
| control | alg | (24,24) | 625 | 701 | 625 | EXCLUDED |

`(25,25)` is the first box 700 terms cannot decide (676 unknowns, 675 rows) --
that is where the term count, not the method, runs out.

The `skip` rows exist because a P-recurrence can fail at the very start of a
series; dropping the first 50 rows tests "holds eventually" rather than "holds
from n=1". Same verdict.

Algebraicity was tested separately even though algebraic => D-finite. The
implication only rules out algebraic functions whose induced ODE fits inside
the box already excluded; a degree-24 algebraic function can induce a much
larger one. Excluded in its own right, so **non-algebraic** is now supported
two ways.

### The guesser is powered -- the four controls that say so

A negative from a guesser means nothing without a positive control, and this
is the same trap convex-mirage's original 38-term result was careful about.
`make gate-convex-dfinite` (`tests/gate_convex_dfinite.py`, ~4 s) is RED-first
on all four arms:

| arm | series | box | must be | is |
|---|---|---|---|---|
| prec + | HV-convex by semiperimeter (banked order-5 degree-2 recurrence) | (5,2) | CANDIDATE | nullity 1, predicts all 172 held-out rows |
| prec - | same series | (2,1) | EXCLUDED | rank 6 of 6 |
| alg + | A005436, algebraic by Delest-Viennot | (2,8) | CANDIDATE | nullity 1, holds on all 69 held-out rows |
| alg - | same series | (2,4) | EXCLUDED | rank 15 of 15 |

So the tool finds a P-recurrence when one exists, finds an algebraic equation
when one exists, and refuses both when the box is too small. The A005436
control series is `results/a005436_perim_s100.txt`, generated by
`build/convex_perim_tm 100 0`.

The 500-term file also reproduces the banked (6,5) exclusion for the king
series directly, so the old result is contained in the new one rather than
merely consistent with it.

### mu, theta, and the amplitude

`experiments/convex_growth.py <terms_file>`. The discriminator is the ratio of
successive differences of `r_n = a(n+1)/a(n)`: a constant below 1 means the
correction to pure exponential growth is *geometric* (isolated subdominant
singularity, no power-law factor); drift toward 1 would mean a branch point
and `theta != 0`. Measured, over the last five n of each 700-term series:

| series | d_n/d_(n-1) | reading |
|---|---|---|
| king | 0.48100879371, constant to all 12 printed digits | geometric |
| control | 0.625135968591, constant to all 12 printed digits | geometric |

The direct probe agrees: `n (r_n/mu - 1)`, which tends to `theta` under a
power law, is at the `1e-216` (king) and `1e-137` (control) level -- i.e.
zero. **`theta = 0` for both**; no power-law correction, and nothing
resembling a stretched exponential. The asymptotic form is

```
a(n) = C mu^n (1 + O(rho^n)),   rho = 0.481008794 (king), 0.625135969 (control)
```

Trusted digits are measured, not asserted: the whole pipeline is rerun on the
series truncated by 30 terms, and the reported figure is the minimum over
{raw tail vs short, Aitken vs short, Aitken vs Richardson} minus a 2-digit
guard.

**mu, convex polyplets (HV-convex king animals) by area -- 199 trusted digits:**

```
3.128943269730886252277447995387754160532091221904394134964974649949244385837182
5761582306328816478323463483522101893703960816757649304814623377841406484754329
8805623983850111109827008627878918922549
```

**mu, convex polyominoes by area (A067675) -- 121 trusted digits:**

```
2.309138593330494731098720305017212531911814472581628401694402900284456440748316
842717281615774412174374610237798122137142
```

The control's value is an external check on the whole apparatus: Bender's
published constant for convex polyominoes by area is 2.30914, and the
non-king transfer matrix plus this extrapolation reproduce it and extend it by
116 digits.

Amplitudes, stable to all 40 printed digits between n=699 and n=700:

```
C_king    = 0.9744522131350046491513294208602433274254
C_control = 2.919598509713607055384709515651335685915
```

### Is mu algebraic? Not in the searched box

PSLQ on `(1, mu, ..., mu^d)`, run at the trusted precision only. A hit is
reported REJECTED-ARTIFACT unless `(d+1) log10(height)` is below half the
trusted digit count -- PSLQ always returns *something* once the unknowns can
absorb the input precision, and the degree-6 "relation" with height ~7e11 that
137 digits produced is exactly that artifact.

| mu | precision fed | degree <= | height <= | result |
|---|---|---|---|---|
| king | 199 | 20 | 1e8 | none at any degree |
| king | 199 | 30 | 1e6 | none at any degree |
| king | 199 | 12 | 1e15 | none at any degree |
| king | 137 (500-term series) | 20 | 1e5 | none at any degree |
| control | 121 | 12 | 1e8 | none at any degree |
| control | 121 | 20 | 1e4 | none at any degree |
| control | 121 | 20 | 1e8 | hits at degree 15-20, all REJECTED-ARTIFACT (capacity 125-142 vs 121 trusted) |

The control's boxes are narrower only because it has 121 trusted digits to the
king series' 199; the last row shows what happens when the box outgrows the
precision, and is the reason the capacity test is in the script.

So: **no integer polynomial with mu_king as a root exists with degree <= 20
and coefficients below 1e8, nor degree <= 30 below 1e6, nor degree <= 12 below
1e15** (and for mu_control, degree <= 12 below 1e8 or degree <= 20 below 1e4).
That is the falsifiable statement; a closed form for
mu, if one exists, lies outside those boxes. Combined with the D-finite and
algebraic exclusions for the series itself, the Convex Mirage verdict stands
and is now an order of magnitude stronger in every direction.

Reproduce:

```
make build/convex_area_tm build/prec_guess
build/convex_area_tm 700 1 > /dev/null   # king,    ~8 min
build/convex_area_tm 700 0 > /dev/null   # control, ~7 min
build/prec_guess prec results/convex_area_terms_n700_king.txt 24 24
build/prec_guess alg  results/convex_area_terms_n700_king.txt 24 24
python3 experiments/convex_growth.py results/convex_area_terms_n700_king.txt \
        --prec 500 --algdeg 20 --maxcoeff 100000000
make gate-convex-dfinite
```

### A worked rejection: the cubic 3219x^3 - 7630x^2 - 18493x + 33955

Offered mid-session (Wolfram|Alpha, fed the then-published ~16-digit mu). Its
nearest root is

```
3.12894326973088625330312785623831607097
mu = 3.12894326973088625227744799538775416053
```

— agreement to **18 digits, disagreement at the 19th**, so it is not mu. It is
also inside the PSLQ box already searched (degree 3, height 3.4e4, well under
degree <= 20 / height <= 1e8), which is why that search returned nothing at
degree 3.

This is the capacity artifact in its natural habitat rather than a contrived
one: a degree-3 relation with height ~3e4 can absorb about `4 x log10(3.4e4)`
= 18 digits of input, so *any* 16-to-18-digit decimal admits such a cubic. The
number of digits fed to an integer-relation search is the whole ballgame, and
this is exactly why the growth script refuses to report a hit unless
`(d+1) log10(height)` sits well below the trusted digit count. Anyone with a
16-digit mu and a cubic solver will find this polynomial; it means nothing.

## Ghost Ship import: the box statistic derived, and the area q-series (2026-08-17)

Salvage from the Ghost Ship experiment (`results/ghostship/`), which ran 14
unattended sessions against a sandbox cut at `74b2c20` — i.e. blind to
everything on this page dated 2026-08-05 or later. Value triage in
`results/ghostship/VALUE-TRIAGE.md`; what follows is the part that survived
it. Receipts are in-tree at
`results/ghostship/grading/run-record/sandbox/` (abbreviated `GS/` below);
that tree is committed, so every path here resolves.

**Read the "already banked" list first.** The loop, working from the cut,
independently produced the s=2..200 semiperimeter series and its degree-2
algebraicity — both of which this page has carried since 2026-08-05 (§"Extended
to s=200", §"The unrestricted series is algebraic too"). Its 200 terms match
`results/convex_perim_terms_s200.txt` exactly, all 199 shared entries. That is
a re-derivation of banked work; it fell outside Ghost Ship's re-derivation
metric only because the sealed denominator was scoped to the 21 files inside
the slice, not to the repo. Nothing below claims those two results.

### New here: the bivariate box GF, derived rather than fitted

The banked result is a quadratic satisfied by the univariate GF, obtained by
box-fitting in `(2,9)`. The loop derived the **bivariate** object from an
explicit 4-phase catalytic functional equation by the kernel method, with no
fitting anywhere in the final chain:

    F(x,y) = Sum_{w,h} f(w,h) x^w y^h
           = -(M + 2x^2 y^2 (1+x+y)^2 sqrt(D)) / (2 K D^2)
      D = (1-x-y)^2 - 4xy,  K = x + y + xy

`f(w,h)` = translation classes with bounding box exactly w x h. The king
modification is absorbed entirely by the kernel `K = x+y+xy` and the weight
`(1+x+y)^2` — that is the structural content, and it is what the box-fit could
not see. Derivation: `GS/docs/proofs/convex-box-kernel.md`. Note:
`GS/results/convex-box.md`.

Specialising, the univariate closed form solves the banked quadratic:

    F(t) = [t^2(2 - 10t + 14t^2 - 5t^3 - 4t^4) - t^3 (1+2t)^2 sqrt(1-4t)]
           / ((2+t)(1-4t)^2)

**Verified independently 2026-08-17**: re-implemented from this expression
alone in exact `Fraction` arithmetic (radical series built from Catalan
numbers, none of the loop's code), it reproduces all 200 terms of
`GS/king_semiperim_200.txt` and hence all 199 of
`results/convex_perim_terms_s200.txt`. The discriminant factors as
`4t^6 (1-4t)^5 (1+2t)^4`, so `sqrt(1-4t)` is the only radical — the same
radicand as classical convex polyominoes.

Asymptotics: `a(s) ~ (s/128) 4^s`, next order `-(1/64)(2s+1)C(2s,s)`. This is
**term-for-term the shape of A005436's exact formula**
`(2n+3)4^(n-4) - 4(n-3)C(2n-7,n-4)`, i.e. king-adjacency convex animals and
classical convex polyominoes agree in leading amplitude and in the form of the
correction. Measured ratio king/A005436: 1.2440 (s=8), 1.0990 (20), 1.0450
(40), 1.0207 (80), 1.0076 (201) — tending to 1 roughly as 1 + 1.5/s. The
ratio's limit is measured, not proved.

### New here: fixed-height structure

- `f(w,h)` is polynomial in `w` of degree `2h-2` for all `w >= 1`:
  `f(w,2) = 2w^2 - 1`, `f(w,3) = w^4 + (2/3)w^3 - (1/2)w^2 - (13/6)w + 2`;
  h = 4, 5 banked. Receipt `GS/out_row_polynomials.txt`.
- Fixed-height **area** GFs are rational with cyclotomic denominators:
  `A_2 = q^2(3-q)/(1-q)^3`, `A_3 = q^3(7+2q+3q^2-4q^3+2q^4)/((1-q)^4(1-q^3))`,
  `A_4` denominator `(1-q)^4(1-q^3)^2(1-q^4)`. Slices sum to the banked area
  sequence for n <= 12. Receipts `GS/out_area_fixed_height.txt`,
  `GS/out_area_slices_check.txt`. Mechanism proved in
  `GS/docs/proofs/convex-area-q-temperley.md`.
- Row-GF numerators satisfy `N_h(1) = A153337`, proved at GF level, plus
  halving identities at `x = -1`. `GS/docs/proofs/row-gf-specializations.md`.

### New here: the area GF as an explicit q-series, and certified constants

This page banks `mu = 3.128943269730886...` to 199 **trusted** digits from
series ratios. The loop replaced trust with a certificate:

    a(n) ~ A mu^n,  mu = 1/q_c,  q_c the smallest positive zero of
    K(q) = Sum_m (-1)^m (2 - q^m) q^{m(m+1)/2} / (q;q)_m^2

    mu = 3.128943269730886252277447995387754160532...
    A  = 0.974452213135004649151329420860243327425...

both to 44+ digits by exact-rational interval arithmetic, with a simple-pole
certificate. Control values reproduce the published Kotesovec/Klarner-Rivest
digits at certified precision. Receipts `GS/out_s10_certify_amplitude.txt`,
`GS/results/convex-area-asymptotics.md`. The area GF itself is a finite
combination of four q-adically convergent q-series from the q-deformed
functional equation, with 50-term predictions checked against an independent
transfer matrix and control mode hitting A067675/A067676 b-files 50/50; 60
exact terms in `GS/out_s05_terms60.txt`.

### New here: two OEIS identifications on the directed-convex subfamily

`a_dir(s) = A014300(s-1)` (nodes of odd outdegree in ordered rooted trees) and
`d(n,n) = A112029(n-1) = Sum_k C(n-1+k,k)^2`. Both verified against b-files by
the loop and re-checked 2026-08-17: neither entry carries any polyomino,
convex, king or polyplet interpretation, so both are comment-grade. Note
`GS/results/directed-convex-king.md`.

Sequences absent from OEIS as of 2026-08-17 (searched here, control query
`1,2,7,28,120,528,2344,10416,46160` hits A005436 exactly, so the search finds
real hits): the semiperimeter series above; the twist `2,5,20,81,344`; the
60-term area series; directed-convex king by area `1,3,10,33,107,342`.

### Lead, not result: non-D-finiteness of the area GF

`K(q)` has >= 40 located real zeros in (0,1) accumulating at q = 1 under
`K(e^-eps) ~ 2 . 3^(1/4) sqrt(eps/2pi) cos(V/eps - pi/12)` with
`V = 2 Cl_2(pi/3)`, the Gieseking constant; `F(1,1,q)` has poles at these
zeros (residues nonzero at the first four), and a D-finite GF has finitely
many singularities. Firm numerically. Two named gaps before this is more than
a lead: a rigorous steepest-descent/Stokes treatment of the oscillation law
near q = 1, and nonvanishing of the residue at infinitely many zeros.
`GS/results/K-oscillation-gieseking.md`.

### Do not re-derive: the area-moment limit law

The loop spent its three costliest sessions deriving
`c_r = (r!)^2 / 2^(r+7)`, hence `E[area^r]/s^(2r) -> (r!)^2/((2r+1)! 2^r)`,
i.e. `area/s^2 -> U(1-U)/2`. **This is published.** Richard,
*Limit distributions and scaling functions*, arXiv:0704.0716, Table 1 and the
accompanying remark: convex polygons carry the rectangles area limit law
`beta_{1,1/2}`. What survives the collision is narrow but real — area-moment
GF algebraicity for **every** r via the same kernel
(`GS/docs/proofs/area-moment-kernel.md`), and the explicit statement that king
and polyomino give the identical law. Enting & Guttmann, "Area-weighted
moments of convex polygons on the square lattice", J. Phys. A 22 (1989), is
linked from A005436 and covers this ground for the control family; read it
before any further work on moments here.

### New 2026-08-18: the Prony spectrum is the reciprocal zero set of K

The salvage identified `mu = 1/q_1` with `q_1` the smallest positive zero of the
Temperley denominator `K(q)`. L7 measures the next three exponentials of the
same series by Prony's method, with no kernel input at all. They are the next
three zeros, sign included:

| Prony (L7, measured) | zero of K | 1/q |
|---|---|---|
| `lambda_1 = 3.12894326973088...` | `q_1 = 0.3195967180593874655186029` | `3.128943269730886252277448` |
| `lambda_2 = 1.50504922775900...` | `q_2 = 0.6644300940833578091864194` | `1.505049227759003934665694` |
| `lambda_3 = 1.28433727098118...` | `q_3 = 0.7786116798090276393820133` | `1.284337270981181428551058` |
| `lambda_4 = -1.25776216033063...` | `q_4 = -0.795062875589391242237668` | `-1.257762160330635483241742` |

Agreement is to every digit L7 prints (14; `lambda_1` to 39). `lambda_4` is
negative and can only come from a **negative** zero, which the salvage's
positive-axis scan never looked for; it is there, at `q = -0.7950628755894`.
So the measured exponential spectrum of the unrestricted and staircase series
is `1/zeros(K)` as a set with multiplicity of sign, not merely in its first two
members. Script: `experiments/convex_kernel_zeros.py` (mpmath, 60 dps, sign
changes on a grid then bisected; both signs scanned).

Consequence for L7: the subdominant rate `rho = lambda_2/lambda_1 = q_1/q_2 =
0.481008794` stops being a measured decimal and becomes a ratio of two kernel
zeros. It does not prove the sharp asymptotic — that still needs the analytic
bookkeeping named in L5's Open Problem on the zeros of K.

**Open, and the natural next test:** the descending half's spectrum
(`2.51457964, 1.43040460, 1.24846593, 1.17441805`) is *not* in the list above.
The meromorphic structure has a second pole family, at the zeros of the 2x2
determinant `det` of the s04 solution, and whether `nu = 2.5145796` is
`1/(smallest zero of det)` is untested. If it is, both halves of L7's
interleaving have one mechanism.
