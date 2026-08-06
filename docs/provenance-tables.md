# Provenance tables — the three papers

2026-08-06, sortie plan §1 "Marking": every paper carrying tier-2/3 material
gets one table mapping each numbered result to its warrant tier and its origin,
plus the repo revision and the Lean build receipt. One table, no hedging in the
body, not buried in acknowledgements.

**Tiers** (plan §1, strongest first):

1. **jasonp-vetted** — he read the proof and believes it.
2. **Lean kernel** — sorry-free, axiom footprint printed and guarded.
3. **Exact-arithmetic certificate** — machine-checkable in integer or modular
   arithmetic by a short independent checker.
4. **Reproducible measurement** — code, a RED control, a gate, and an
   independent second source. Publishable as a measurement, never as a
   theorem.

**The gate:** a claim jasonp has not vetted ships only at tier 2 or 3. Tier 4
material appears as data and as explicitly-labelled conjecture, never as a
result.

Common to all three tables:

    repo revision      679800c   (2026-08-06)
    Lean build receipt polyplets/build-receipt-2026-08-06.log
                       rev 679800c, lean v4.31.0, mathlib v4.31.0,
                       8621 targets current, 0 sorries,
                       143 audited theorems: 95 standard-axioms-only,
                       48 with named native_decide leaves, no sorryAx,
                       no anonymous ofReduceBool

---

## Paper 1 — Fixed polyplets to n = 40

Tier 4 is the paper's subject, not a weakness: a record enumeration is a
measurement. What the table has to show is that each measurement carries its
control, its gate and its second source.

| # | result | tier | origin | how a reader checks it |
|---|---|---|---|---|
| 1 | a(23)–a(40), a(40) = 56749893611764175164545926946127 | 4 | `results/ns_a40/`, `results/b006770_upload.txt` | `experiments/paper1_reproducibility_check.py` check A; per-height rows sum to the term |
| 2 | the T(n,H) triangle, n ≤ 40 | 4 | `results/ns_a40/perheight/` | same script, checks A/B/D/E |
| 3 | second-algorithm confirmation, n ≤ 22 | 4 | `results/redelmeier_row22/` | check C, with a RED control |
| 4 | strip transfer matrix confirms H ≤ 14 at every n ≤ 40 — 469 cells, 0 mismatch | 4 | `results/strip-engine.md`, `results/strip_C14_n40_run.log` | check D recomputes 469 from the cell set |
| 5 | T(n,n) = 3^(n−1) | 1 | hand derivation; also `Universal.T_king` in Lean | check B, 40 cells |
| 6 | T(n,n−1) = 5(5n−9)3^(n−4) | 1 | `docs/proofs/T-n-nm1.md` | check B, 37 cells |
| 7 | T(n,n−2) = ½(625n²−2459n+1134)3^(n−7) | 1 | `docs/proofs/T-n-nm2-and-general.md` | check B, 36 cells |
| 8 | λ ≥ a(40)^(1/40) = 6.2208413587750324 | 2 | Lean `a_supermul` → `lambda_gt_of_banked` (standard axioms only) | `lake build`; the guard is in `AuditOutworks.lean` |
| 9 | component stratification, C(n,1) = C(n,n) = A001168 | 1 | `results/component-stratification.md`, the 45°-sublattice bijection | brute force n ≤ 14 in that note |
| 10 | λ = 7.110(1), θ = −1.000(1) | 4 | `results/series-analysis-da.md` | differential approximants on the 40 terms; label as an estimate |
| 11a | M_single(n) = ⌊((n−2)²+4)/8⌋, one hole | 1, **not ours** | **Sieben 2008 Thm 4.1** (σ(e) = ⌊e²/8 − e/2 + 1⌋) verbatim, not even inverted — `results/maxhole-proof.md` §The literature. Our (I')/(II')/moat-cycle chain is an independent reproof | `experiments/maxhole_sieben_check.py` (the identification, with a RED control); `maxhole_moat_check.py` (3,927 animals), `maxhole_box_construction.py` (n ≤ 60) |
| 11b | M(n) = ⌊((n−2)²+4)/8⌋, all holes | 1, **not ours** | **PROVED 2026-08-06** — `results/maxhole-proof.md` §The union argument: the minimum holds for an arbitrary finite subset of ℤ² (**Wang & Wang 1977**, ℤ² count explicit in **Altshuler et al. 2006**), so applying it to the union of all the holes is three lines. The overlap count is dissolved, not answered | same script: the two closed forms agree at every k ≤ 200,000, and no ≥2-component subset (k ≤ 10) beats it |
| 12 | the hole-fill bijection | 1 | `results/hole-fill-interior-cell-identity.md` | exact, three sentences |

Rows 11a and 11b are both theorems as of 2026-08-06, and both belong to the
isoperimetry literature: they ship **with citations, not as new results**. What
is ours there is the question and the enumeration. The Lean file's
conditionality (`MoatBound`) is a formalization gap, not a mathematical one.
Rows 1–4 are the
tier-4 core and are covered in detail by `docs/paper1-reproducibility.md`,
including the coverage figures (57.2% / 72.2% / 95.4%) and the mass split
(95.9% of a(40) enumerated, 4.1% composed from held-out closed forms).

## Paper 2 — The structure of the polyplet height triangle

| # | result | tier | origin | how a reader checks it |
|---|---|---|---|---|
| 1 | the hand-derived diagonals T(n,n−1), T(n,n−2) | 1 | `docs/proofs/T-n-nm1.md`, `T-n-nm2-and-general.md` | as Paper 1 rows 6–7 |
| 2 | the defect gas: 25 = 16 + 9, and the same bookkeeping generates every P_k | 1 | `results/defect-gas.md` | the note's own derivation |
| 3 | universal diagonal law: T(H+k,H) = q_k(H)·b^H for every row-local lattice, deg q_k ≤ k, H ≥ k+1 | **2** | `docs/proofs/universal-diagonal-law.md`; Lean `Universal.universal_shape_d`, `universal_shape`, `universal_shape_production`, `universal_production_int_all` — **standard axioms only** | `lake build --no-build`; the four names are guarded |
| 4 | the three lattice instances (king b=3, hex b=2, square b=1) | 2 | Lean `king_P1_*`, `hex_P1_*`, `square_P1_*` | same; these carry **named native leaves** — two triangle cells per lattice — and the table should say so |
| 5 | the grand form | 2 | `docs/proofs/grand-form.md`; Lean `grand_form`, `grand_form_prod` — standard axioms only | guarded |
| 6 | P_k pinned to k ≤ 18 from production data | 2 | Lean `P18_grand_of_banked`, `P18_grand_prod` | named leaves: the chunked weight cards |
| 7 | ternary spine: the triangle mod 3 is governed by W³ = W² + t | 1/4 | `results/ternary-spine.md` — the law and its ladder consequences are proved; the "bonus depth" section is explicitly measured-not-proved | `experiments/ternary_spine.py`, 15/15 including a 342-cell mass check |
| 8 | Smith normal form: all invariant factors are 3-powers, ⌈(N−1)/3⌉ nontrivial | 1/4 | `results/triangle-snf.md` — the 3-power containment and (A1b), (A2), (B) are proved; the remainder is flagged conjectural in that note | sympy SNF on the banked triangle, N = 4..14 |
| 9 | the anisotropic GF is not D-finite, with certified degrees deg ψ_H = 1, 2, 4, 9, 29, 68, 181, 462, 1254, 3289 | **3** | `results/anisotropic-not-dfinite.md`, mod p = 2⁶¹−1 with preserved degrees | the note's own exact-arithmetic checker |

Rows 7 and 8 are split-tier and must be written with the split visible: the
proved core as a result, the measured remainder as data. Row 9 is the paper's
one tier-3 headline; its step 1 is Bousquet-Mélou & Rechnitzer 2002 Lemma 9 and
must be cited as theirs (that credit is already in the source note).

## Paper 3 — Growth constants of king animals and their subclasses

| # | result | tier | origin | how a reader checks it |
|---|---|---|---|---|
| 1 | λ ≤ 9.3153 | **2** | `docs/proofs/polyplet-upper-bound.md`; Lean `BuiSystem.certSum_le`, `lambda_le_of_buiSystem`, `RatCert.lambda_le` (standard axioms) + `lambda_le_of_bui_rd3` | `lake build`; the concrete certificate depends on the named leaf `buiRD3_valid` |
| 2 | λ ≥ 6.543 | **3** | certified strip ladder µ₁₇, exact rational Collatz–Wielandt with a per-H receipt (`results/strip-mu-certificates.md`) | `make gate-strip-fast` runs the engine against the published certificates — the exact kernel must PASS the certified numerator and FAIL numerator+1; `make gate-strip-cert` is the checker's own RED-first self-test |
| 3 | µ = 3.128943269730886… for every class between staircase and HV-convex (Proposition 6) | **1** | `results/hv-growth-sandwich.md`, Lemmas 1–3 + the squeeze | elementary: an injection, Fekete, a stack bound. `make gate-middle-kingdom` pins the ingredients |
| 4 | M(i)M(j) ≤ M(i+j), and µ ≥ M(700)^(1/700) = 3.1234045… | 1 | Lemma 3, sortie B1; **machine-checked** — Lean `Stair.M_supermul`, `Stair.M_tendsto`, `Stair.M_le_mu_pow`, `Stair.mu_gt_of_banked` (`polyplets/Polyplets/StairGrowth.lean`, standard axioms, guarded) | `lake build` proves the inequality for all i, j; `experiments/staircase_supermul.py` checks 700 terms with three RED controls. The floor is conditional on the banked `M 700` as a hypothesis |
| 5 | 3 + 2√2 for directed king animals | 1 | Bacher 2013, reproduced here against A047781 | `make gate-king-grid` |
| 6 | eight of twelve grid cells collapse onto the unfiltered row | 1 | `results/middle-kingdom-phase3.md` Props 1/2/3/5 | brute-force grid n ≤ 14, `make gate-middle-kingdom` |
| 7 | ν = 2.5145796438787291885… is the growth rate of an explicitly counted half of the 4-cone series | 1/4 | `results/hv-growth-sandwich.md` Lemma 4, Proposition 7 (rates **proved**); the 153/242 trusted digits are measured | `experiments/descent_block_oracle.py`, three RED controls |
| 8 | the amplitude ratio r = (1/2)(w4·φ)/(w·φ), 251 trusted digits | 4, conditional | Propositions 9–11, conditional on the two amplitudes existing | `experiments/amplitude_feed_vectors.py`; gate reproduces Table B's 54 digits |
| 9 | Conjecture 8 (sharp asymptotics for the two halves) | conjecture | same note | ships labelled as a conjecture or not at all |
| 10 | the five novel sequences; the non-D-finite exclusion boxes | 4 | `results/oeis-candidates.md`, `results/convex-polyplets.md` | ship as data and labelled measurement, never as results |

**Attribution note that belongs in Paper 3's body, not only here:** the
phase-block decomposition underlying rows 3 and 7 is Gouyou-Beauchamps &
Leroux's, for convex polyominoes (FPSAC 2004, §2.3) —
`results/novelty-sortie.md` N3. Row 3's conclusion also has a classical
square-lattice analogue (Bender 1974 against the parallelogram subclass,
measured at 2.309138593330495 in `experiments/square_staircase_area.py`).

---

## Using these tables

They are content, not layout: each paper's table should be typeset in its own
style, and the "how a reader checks it" column can become a single
Reproducibility pointer if the paper carries one. What must survive
compression is the tier column and the split-tier rows — Paper 2 rows 7 and 8,
Paper 3 rows 7 and 8 — because those are the places where a reader could
otherwise read a measurement as a theorem.
