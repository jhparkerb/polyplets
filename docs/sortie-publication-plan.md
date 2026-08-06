# Sortie — the publication push

2026-08-06. The campaign that takes everything worth publishing out of the
repo and into the world. Successor in the Outworks / Middle Kingdom line;
unlike those, its deliverables are papers, notes and OEIS entries, not commits.

Revision history of the plan itself: a first version framed this as one paper
plus the a(40) report. That was wrong about the count — widening the frame past
"work done last week" pulls in two already-finished deliverables. A second
version enumerated twelve units. This version consolidates those twelve into
**three papers plus two non-paper releases**, which is the shape jasonp asked
for.

---

## 1. The rule

jasonp's constraint, stated 2026-08-06, and the organising principle of
everything below:

> I can't let you write papers for me where the math is something I can
> understand and vet. I'm happy (ish) to publish LLM-authored results *if*
> they're beyond my understanding *and* we're *sure* they're correct *and*
> they're clearly marked as such.

Clarified in the same conversation to the **narrow reading**, which is the one
in force: **jasonp writes all of the prose.** Where a result is past his
vetting, the publication is a short note in his words stating the theorem,
naming what certifies it, and telling the reader how to run the check — with
the Lean development or the certificate as a cited artifact. Claude does not
author paper prose.

### What Claude may do

Everything that is not authoring prose or supplying the endorsement: the
novelty sweep, the Lean development, regenerating and re-verifying every
number, LaTeX scaffolding, tables and figures, the Provenance table,
reproduction recipes, and checking drafts against the repo.

### Warrant tiers

What makes a claim safe to publish, strongest first:

1. **jasonp-vetted.** He read the proof and believes it.
2. **Lean kernel.** Sorry-free, axiom footprint printed and guarded
   (`Grand/Audit.lean`'s `#print axioms` discipline). Belief is not involved.
3. **Exact-arithmetic certificate.** Machine-checkable in integer or modular
   arithmetic by a short independent checker — the Bui convolution
   certificate, the Collatz–Wielandt rational bounds, the mod-p gcd
   certificates. Weaker than Lean only in that the *checker* is unverified;
   the *arithmetic* is exact.
4. **Reproducible measurement.** A number produced by code, with a RED
   control, a gate, and an independent second source. Publishable as a
   measurement, never as a theorem.

**The gate: a claim jasonp has not vetted ships only at tier 2 or 3.** Tier 4
material appears as data and as explicitly-labelled conjecture, never as a
result. Below tier 4, it does not appear.

### Marking

Every paper carrying tier-2/3 material gets a **Provenance** section: a table
mapping each numbered result to its warrant tier and its origin, plus the repo
revision and the Lean build receipt. One table, no hedging in the body text,
not buried in acknowledgements.

---

## 2. The three papers

### Paper 1 — Fixed polyplets to n = 40: enumeration, validation, and structure

**Entirely tier 1. Gated on nothing. Can start immediately.**

The record and the engine in one paper, per the genre's convention (Redelmeier,
Jensen): the record alone is a number, the engine alone has no punchline.

Contents:

- a(40) = 56749893611764175164545926946127 and the T(n,H) triangle.
  `paper/technical-report.tex` is the existing draft and is jasonp's words.
- **The engine.** The unwritten half, and the part with no authorship problem
  at all: utilization was the lever, not cores (19.8% → the fix); work-stealing
  beat LPT; CRT counter-shaping settled on u32/31-bit interleave; the zstd
  frontier format; the tmpfs win to a34 and its OOM failure at a35; PGO no-go
  because the workload is branch-mispredict-bound; disk-bound scaling at
  ~4.4×/term; the kink-carry NW-carry kernel. Sources: `results/perf-outcomes.md`,
  `results/utilization-fix-and-ceiling.md`, `results/scheduling.md`,
  `results/crt-counter-shaping.md`, `results/kink-carry.md` (the base change
  that takes ~4.4×/term down to ~2.5×), `results/second-wind.md`,
  `results/terminal-velocity.md` (the PGO no-go and the branch-mispredict
  profile behind it). Assembled with the numbers re-checked in
  `docs/paper1-engine-chapter.md`.
- **Validation architecture** — the current biggest hole (`§Reproducibility` is
  empty). Every production run re-derives all smaller terms; Redelmeier
  confirms to n = 22; an independent strip transfer-matrix engine sharing no
  enumeration code confirms T(n,H) for H ≤ 14 across all n ≤ 40 (469 cells, 0
  mismatches); the three-tier system (computed twice / computed once / composed
  with pinned formulas). Sources: `paper/technical-report-gaps.md` item 1,
  `results/strip-engine.md`, `HANDOFF.md`.
- **Component stratification** (`results/component-stratification.md`), because
  C(n,1) = C(n,n) = A001168 via the 45°-sublattice bijection and the peak at
  c ≈ n/2 is the *mechanism* behind λ ≈ 7.11 ≫ 4.06 — the natural "what does
  this population look like" section straight after the count.
- **Maximum enclosed hole area**, M(n) = ⌊((n−2)²+4)/8⌋, riding with the hole
  table already in the report. **Unconditional as of 2026-08-06**, and **not
  ours**: both halves are the grid isoperimetric inequality (Sieben 2008,
  Altshuler et al. 2006), so it goes in as a cited corollary plus our n ≤ 17
  enumeration — `results/maxhole-proof.md`. The hole-fill bijection is three
  sentences and rides along with it.
- The differential-approximant growth estimate λ = 7.110(1), θ = −1.000(1)
  (`results/series-analysis-da.md`) as a paragraph, replacing the current stub.

### Paper 2 — The structure of the polyplet height triangle

**Mixed tiers 1 and 2/3. Gated on novelty N5, N6.**

The unit that consolidates best, because it has an arc that runs from what
jasonp derived by hand to what only the kernel vouches for:

1. **The hand-derived diagonals.** T(n,n−1) = 5(5n−9)3^{n−4} and
   T(n,n−2) = ½(625n²−2459n+1134)·3^{n−7} (`docs/proofs/T-n-nm1.md`,
   `T-n-nm2-and-general.md`). Tier 1.
2. **The defect gas** — where the 25 comes from (25 = 16 + 9, domino joiner
   plus split joiner), and why the same bookkeeping generates every P_k
   (`results/defect-gas.md`). Tier 1, and it makes the hand derivation the
   k = 1 case of a machine.
3. **The universal diagonal law.** For every row-local lattice,
   `T(H+k,H) = q_k(H)·b^H` for all H ≥ k+1, deg q_k ≤ k
   (`docs/proofs/universal-diagonal-law.md`). Lean carries the abstract shape
   engine plus square (b=1), hex (b=2) and king (b=3) instances, sorry-free,
   axiom footprint guarded so a `native_decide` cannot leak into the proof
   cone. **Tier 2** — stated by jasonp, certified by the artifact.
   The grand form (`docs/proofs/grand-form.md`) is its companion.
4. **The arithmetic of the triangle.** The ternary spine: the triangle mod 3 is
   governed by the single cubic W³ = W² + t over 𝔽₃, with a base-3
   digit-product formula (`results/ternary-spine.md`). And the Smith normal
   form: every invariant factor a pure power of 3, exactly ⌈(N−1)/3⌉ nontrivial
   ones (`results/triangle-snf.md`). Two independent statements that the
   triangle's entire integer content lives at the prime 3.
5. **The capstone negative.** The anisotropic GF F(x,y) = Σ_H G_H(x) y^H,
   assembled from these same fixed-height denominators, is not D-finite —
   quantified, not asymptotic, via certified new-root contents deg ψ_H = 1, 2,
   4, 9, 29, 68, 181, 462, 1254, 3289 and the pole argument
   (`results/anisotropic-not-dfinite.md`). **Tier 3**, mod p = 2⁶¹−1 with
   preserved degrees.

### Paper 3 — Growth constants of king animals and their subclasses

**Mixed. Gated on novelty N1–N4.** (Lean P1 was a gate until B1; Proposition 6
no longer needs a formal warrant to ship, so P1 is now a nice-to-have.)

One subject, four answers:

- **6.543 ≤ λ ≤ 9.3153**, both ends machine-checkable in exact arithmetic. The
  upper end is the notable half — per `docs/proofs/polyplet-upper-bound.md`
  there was **no published upper bound on λ_polyplet at all** before it — and
  it is in Lean (`Upper/Certificate.lean` + `BuiData`), tier 2. The lower end
  is the certified strip ladder µ₁₇, exact rational Collatz–Wielandt with a
  per-H receipt, tier 3.
- **3 + 2√2 exactly** for directed king animals (Bacher; reproduced here
  against A047781 as a formula-side validation hook).
- **µ = 3.128943269730886…** for every class between staircase and HV-convex,
  by Proposition 6 (`results/hv-growth-sandwich.md`). B1 (§3) settled its tier:
  the proof is now elementary and **tier 1 once jasonp has read it**.
- **The grid collapses** — eight of twelve open cells fall onto the unfiltered
  row, each by one lemma about the column-bottom profile
  (`results/middle-kingdom-phase3.md` Props 1/2/3/5). Tier 1, jasonp-vettable,
  and they explain why the constants coincide.

The five novel sequences and the non-D-finite exclusion boxes ship inside this
paper as **data and labelled measurement**, never as results.

**The one un-consolidation worth considering.** The λ bracket is plausibly the
single most citable line in the repo, and inside Paper 3 it arrives on page 7
as one of four results. If it should land rather than merely appear, pull it
out as a two-page standalone note and let Paper 3 cite it. jasonp's call.

### Not papers

- **The Lean development** (`polyplets/`, ~21k lines, sorry-free) as an
  archived artifact release, cited by Papers 2 and 3.
- **The OEIS wave**, §5.

---

## 3. Where the rule actually bites — and B1

Paper 1: no constraint. Paper 2: the tier-2/3 items are *statements plus
citations*, a page or two of jasonp's writing each, not mathematics he must
reproduce. **Paper 3, Proposition 6, is the only place the rule genuinely
bites** — a growth-constant squeeze presented as "see the formalization" is a
harder sell to a referee than a formalized lattice theorem is, so that result
probably wants a real proof on the page.

**B1 dissolves the problem. Done 2026-08-06.**

`M(i)M(j) ≤ M(i+j)` is a theorem, not a measurement: the column-join with
`d = max(0, h − h')` stays in the class, and at fixed `(i, j)` it is injective
on the nose, because column areas are positive, so the prefix of columns of
total area exactly `i` is unique and no split index has to be carried, exactly
as `Growth.lean:608 a_supermul` argues for λ. `hv-growth-sandwich.md`'s Lemma 3
is rewritten; the factor `(i+j)` and the Barequet–Ben-Shachar–Osegueda
quasi-super-multiplicativity citation are both gone. Fekete then gives
`µ = sup_n M(n)^(1/n)`, so every banked term is a rigorous lower bound:
`µ ≥ M(700)^(1/700) = 3.1234045…`, exact arithmetic on a banked integer.

Checked by `experiments/staircase_supermul.py` and pinned by
`make gate-middle-kingdom`: brute force over `(h, d)` reproduces `M(1..12)`,
every join over `i+j ≤ 12` lands in the class and injects, the inequality has
zero violations over all `i+j ≤ 700` (up from the 300 measured earlier), and
three RED controls fail as required — the `d = 0` join leaves the class, the
area-`(i+1)` cut fails to invert, and the stacks `P(n)` are *not*
supermultiplicative, so the series check is not vacuous.

Proposition 6 is therefore three elementary steps:

1. the column-join is injective at fixed (i,j), so Fekete gives the staircase
   limit (mathlib `Subadditive`, exactly as `negLogA_subadditive` /
   `lambda_tendsto` already do) — **done**;
2. the outer blocks are stacks, sub-exponential by an elementary split at √n:
   with `s = ⌈√n⌉`, the parts `≤ s` are fixed by `s` multiplicities in `[0,n]`
   and the parts `> s` number at most `⌊n/(s+1)⌋`, so
   `p(n) ≤ (n+1)^(2√n+2)` and `P(n) ≤ (n+1)^(4√n+6)`. No Hardy–Ramanujan; the
   squeeze only needs `P(n)^(1/n) → 1` — **done**;
3. squeeze.

No analytic machinery, just an injection, Fekete, and a counting bound. Both
owed pieces are now in `results/hv-growth-sandwich.md`. Subject to jasonp
reading Lemmas 2 and 3 and
Proposition 6 and believing them, **Proposition 6 is tier 1** and Paper 3 is as
unconstrained as Paper 1. The fallbacks (Lean warrant, or shipping Paper 3 on
the bracket, the directed constant and the grid collapses alone) are not
needed.

**Status 2026-08-06: the reading gate is still open.** jasonp follows the
argument's shape — the orientation section now at the head of
`results/hv-growth-sandwich.md` §The proof was written for that, and Lemmas 2
and 3 were re-proved in the same register — but has not vetted the two lemmas
themselves. Until he does, tier 1 is *eligible*, not held, and P1's Lean warrant
stays live rather than nice-to-have. Cost estimate for P1 in `HANDOFF.md`
(session 2026-08-06): Lemma 3 alone ≈400 lines and no new mathematics; Lemma 2
≈600–900 with no mathlib support for unimodal compositions; all of
Proposition 6 ≈3000–4500, mostly the geometric layer B3.

---

## 4. The Lean push

Lean is not polish here — it is the mechanism that makes unvetted results
publishable at all. Priority is "what does this unlock".

**P1 — Proposition 6.**

- **B1** (§3) first, on paper, no compute. **Done 2026-08-06** — and it lands
  as a one-line consequence for Lean too: `M(i)M(j) ≤ M(i+j)` feeds mathlib's
  `Subadditive` through the same `negLogA` idiom `Growth.lean` already uses, so
  B4's Fekete half is a transcription rather than a proof.
- **B2.** Lemma 2 the cheap way: parts ≤ √n contribute ≤ (n+1)^√n, parts > √n
  number at most √n and contribute ≤ (n+1)^√n ⇒ p(n) ≤ (n+1)^(2√n).
  **Done 2026-08-06 on paper** (`results/hv-growth-sandwich.md` Lemma 2,
  pinned by `make gate-middle-kingdom`); what is left of B2 is transcribing it
  into Lean, where the objects are `Nat.Partition` and a counting injection,
  with no analysis in sight.
- **B3.** Definitions — column-convex, HV-convex, staircase, the two cones, in
  the `Defs.lean` idiom. The real cost centre: a new geometric layer, not a
  reuse of the diagonal machinery.
- **B4.** The squeeze, short once B1–B3 land.

**P2 — the eight collapse propositions.** Nearly free once B3 exists, and they
promote the grid from a table to a theorem. Optional under the gate (they are
tier 1 already) — do them because they are cheap.

**P3 — the A001523 identification** (monotone-height block ↔ weakly unimodal
composition). Nice-to-have; not load-bearing if B2 lands.

**P4 — a Lean rung on the λ ladder.** Optional. The lower bound already has a
tier-3 warrant, which the gate accepts, and Lean-checking the H=17 transfer
matrix is a bad trade. If both ends in Lean is wanted for symmetry, formalise a
small rung (H = 10 or 12, ≈ 6.0–6.2) and say plainly that the sharp 6.543 is
machine-checked outside Lean.

**Explicitly not Lean targets.** The non-D-finite and non-algebraic exclusion
boxes, the amplitude-ratio formula, Conjecture 8, any trusted-digit claim.
Formalising these would formalise the wrong object.

---

## 5. Novelty due diligence

Papers 2 and 3 are blocked on this; it costs no compute; a novelty miss on a
published paper is public. Standing caution: "no OEIS match on nine terms" is
weak evidence when the class was defined here — the risk is that someone
counted the same objects under another name.

**Swept 2026-08-06, all six. Verdicts in `results/novelty-sortie.md`; neither
paper is blocked, and N3 is a real collision that changes what may be claimed.**

| # | question | blocks | verdict |
|---|---|---|---|
| N1 | Is the staircase-squeeze argument folklore in the polyomino literature? | Paper 3 | not found as a theorem; its **conclusion is classical** for the square lattice by area (Bender 2.30914… = the measured parallelogram constant), and after N3 its ingredients are published too. Claim the king theorem, not the technique |
| N2 | Has anyone enumerated HV-convex *king* animals under another name? | Paper 3 | **no.** Not in OEIS, and convexity never meets the king lattice in the literature searched |
| N3 | Does the block factorisation of an HV-convex transfer operator appear in the column-convex literature? | Paper 3 | **YES.** Gouyou-Beauchamps & Leroux 2004 §2.3 decompose convex polyominoes by the growth phases of both profiles, with `H00`/`H22` stacks and `H02 = Pa = H20` staircases. Cite at Lemma 1, Lemma 2 and Prop 9; Props 6, 7, 10, 11 survive intact |
| N4 | Is there a published upper bound on λ_polyplet? Any strip ladder beating Bacher's 6.475? | Paper 3 | **no** to both. The whole upper-bound line is square/hypercubic/polyiamond/polycube; the king lattice is absent, including from Kim–Pinna 2025 |
| N5 | Is a universal (lattice-class) diagonal law already in print? | Paper 2 | **no** for height diagonals; the polycube **dimension**-defect line (Barequet–Barequet–Rote 2010, Barequet–Shalah 2015/2017) is the same statement shape one parameter over, and should be cited as precedent |
| N6 | Does the quantified ψ-degree argument collide with Rechnitzer's own Haruspicy program? | Paper 2 | **no.** Haruspicy is bond animals and SAPs; directed *site* animals are solved, which is why it never turns our way. The one shared step was credited 2026-08-01 |

Method: the citation neighbourhoods of the Bacher, Bousquet-Mélou, Rechnitzer
and Barequet papers already in `papers/`, plus targeted searches. Un-findable
papers go to `papers/MISSING.md` per standing practice.

---

## 6. OEIS

Behind the viva (`docs/viva-*.md`, bar 80) and jasonp's button. Ordered so the
riskiest submission is last:

1. **A222205 b-file**, 23 → 200 terms. Pure extension, no novelty claim;
   calibrates the editors.
2. **The five comments and corrections** — A018902 (first lattice-animal
   interpretation, explaining the entry's own INVERT-of-A007052 formula),
   A187077 (the A059716 comment is wrong, measured with a control, plus the
   missing derivation), A055834, A007052, A225114. Highest value per word in
   the campaign, and all jasonp-vettable.
3. **The five new sequences**, after N1–N3 return.
4. **Candidates A and B** (`results/oeis-candidates.md`: the T(n,H) height
   triangle, the C(n,c) component triangle). Still owe a Superseeker pass.

---

## 7. What does not ship

- **The v5 denominator law.** Self-demoted 2026-07-31 — correct, proved, and a
  fact about our choice of basis rather than about polyplets.
- **Minimum site perimeter.** It is A235382; someone else's theorem, correctly
  identified.
- **The ν exponent.** Already self-narrowed: 0.6407 is what universality
  assigns to polyplets anyway, so it is evidence for nothing.
- **The height-distribution limit shape.** A measurement, and a limit-shape
  claim off n ≤ 40 is thin.
- **The central-charge finite-size fit.** The ladder is not analytic in 1/H at
  H ≤ 17; the negative is banked and stops there.
- **The hex diagonal law** as a separate item — subsumed by the universal law.
- **Exclusion boxes as theorems.** They ship as measurements inside Paper 3.
- **`results/beyond-polyplets.md`.** An inventory with novelty unchecked on
  every item, by its own header.

---

## 8. Order of operations

1. ~~**B1**, and B2's paper half with it (§3)~~ — **done 2026-08-06**.
   Proposition 6 is elementary end to end and tier-1-eligible, so Paper 3 is
   shaped like Paper 1: jasonp's to write, nothing owed on the proof side.
2. **Paper 1** — jasonp's to write, gated on nothing, can run in parallel with
   everything below. Start with `§Reproducibility` and the engine chapter.
3. **Novelty sweep N1–N6** — no compute, gates Papers 2 and 3.
4. **Paper 2 write-up** if N5/N6 return clean — the Lean is already done.
5. **Lean P1 B2–B4, then P2** — the Paper 3 campaign, shaped by B1's answer.
6. **Paper 3 write-up**, with or without the λ bracket pulled out as a note.
7. **Lean artifact release**, cited by Papers 2 and 3.
8. **OEIS waves 1–4** per §6, behind the viva.
