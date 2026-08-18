# GRANDFORM-PLAN — Lean formalization of the grand-form theorem

2026-07-21. Master plan for formalizing `docs/proofs/grand-form.md` in Lean 4,
executed by **Opus agents** (one per task brief, `polyplets/briefs/GF*.md` ---
the briefs were deleted at project close and are in git history; the Lean
files they produced are the authoritative statement),
orchestrated from a supervising session. Every mathematical claim below is
**pre-validated numerically** by `experiments/staircase_check.py` (ALL CHECKS
PASS, 2026-07-21) — agents formalize, they do not need to re-derive.

## Goal and payoff

Formalize the grand form via the **staircase architecture** (below), yielding:

1. `grand_form` (UNCONDITIONAL, standard axioms): existence of rational
   cumulant sequences a, b with
   `3^(3k+1) · T(n, n−k) = expCoeff a b k n · 3^n` for all k, n ≥ 2k+1 —
   the Lean grand-form theorem proper.
2. `P<k>_grand` for k = 1..16 — **shipped at k = 1..18**, extended at the
   a(40) close (`c54ce70`, 2026-07-29), the plan's original k ≤ 16 target
   having been set when the triangle stopped at n = 36
   (conditional-on-banked-REAL): the *production*
   polynomials of `orchestrator/sweep.go` pinned for all n ≥ 2k+1, with
   hypotheses = **2 real-swept cells per level** (H ≤ 18 as planned, H ≤ 20
   as shipped; 30 anchors at k = 18). This RETIRES the PREDICTED tier of
   `Pin.lean` (k = 12..16) and
   also removes Pin's reliance on wired cells at k = 10, 11 (its current
   hypotheses include formula-generated cells like `T 31 20`).
3. Corollaries: leading coefficient `25^k/k!` and `deg P_k = k` for all k
   (closing `Shape.lean`'s deferred stretch goal), unconditional modulo the
   single native_decide `V_1_1`.

## The staircase architecture (what replaces the paper's GF apparatus)

The paper proof (Weierstrass root/cofactor, unit-inverse polynomiality,
tail-kill, Lagrange lemma) collapses, in sequence form, to:

- **ν fixed point** (root series, = z* of the paper): ν₀ = 1/3 and
  `eps m = 3·ν m + Σ_{ℓ∈Icc 1 m} (v_ℓ ∗ ν^{∗(ℓ+1)}) m`,
  where `v_ℓ (j) = if ℓ ≤ j then V ℓ j else 0` and ∗ is sequence convolution.
  This is a well-founded recursion (RHS reads ν only below m).
- **μ** (= 1/z*): defined NON-recursively from ν:
  `mu m := 3·eps m + Σ_{ℓ∈Icc 1 m} (v_ℓ ∗ ν^{∗ℓ}) m`; then `mu ∗ ν = eps`
  follows directly from ν's defining recursion.
- **μ-recursion** (the core theorem, from `Peel.d_rec` alone):
  `d k (H+1) = Σ_{i≤k} mu i · d (k−i) H` for H ≥ k+1.
  One strong induction on H; no power series, no polynomials, no analysis.
- **Staircase** (through `Peel.c_ident`):
  `T(H+1+k, H+1) = Σ_{i≤k} mu i · T(H+(k−i), H)` for H ≥ k+1.
- **Pinning** (per level k, strong induction on k then n): μ_k's numeric
  value is solved from ONE real cell `T(2k+2, k+2)` (the level base is
  `T(2k+1, k+1)`); the level then propagates to all n ≥ 2k+1 by the
  staircase + a per-k polynomial identity
  `P_k(x+1) = Σ_i mu_i·3^(2i−1)·P_{k−i}(x−i)` proved by `ring`/`norm_num`.
- **Exp form** (abstract): W fixed point `1 = Σ_i m_i y^i W^{i+1}`
  (m_i = μ_i·3^(2i−1)), b := −log W, a := level-solved from T abstractly;
  expCoeff via the derivative recursion. Same uniqueness induction ⇒
  `grand_form` with NO banked hypotheses.

## Pre-validated facts (agents may rely on these being true)

From `experiments/staircase_check.py` (exact rational arithmetic):

- The staircase holds at **all 170** real banked instances (k ≤ 16, H ≤ 18);
  154 of these are beyond the 16 solving equations. (At the a(40) close the
  fail-closed generator `scripts/gen_grand_pin.py` raised this to **209**
  real instances at k ≤ 18, H ≤ 20 — 191 beyond the 18 solving equations —
  and aborts if the count or any instance disagrees. `staircase_check.py`,
  the exploratory twin quoted in this section, still runs at KMAX = 16.)
- Onset is sharp: the staircase FAILS at H = k for all 16 levels.
- μ₁..μ₃ from the weight-side fixed point (Lean-verified V values) equal
  μ₁..μ₃ solved from data. μ₁ = 25/3, μ₂ = 833/27, μ₃ = 32708/243.
- The P-staircase polynomial identity holds for production P₁..P₁₆ (and,
  as shipped, P₁..P₁₈ — `gen_grand_pin.py --kmax 18`).
- Anchors `T(2k+1, k+1)`, `T(2k+2, k+2)` match production values, all levels.
- W/b/a reproduce `scripts/derive_pk_fast.py`'s constants exactly
  (b₁ = 25, a₁ = −45, b₂ = −209/2, a₁₆ = −48607562060310698638155/16) and
  `leading coeff of P_k = b₁^k/k! = 25^k/k!` for k ≤ 16 (k ≤ 18 as shipped).

Exact μ table (denominators are powers of 3; μ₁₅'s exponent 27 is correct,
not a typo — the pattern is not strictly increasing):

```
mu_0=3            mu_1=25/3^1        mu_2=833/3^3        mu_3=32708/3^5
mu_4=1426141/3^7  mu_5=66608903/3^9  mu_6=1088429260/3^10
mu_7=55307294057/3^12              mu_8=2888944079197/3^14
mu_9=462665755865681/3^17          mu_10=25137023928857275/3^19
mu_11=1385671259198548241/3^21     mu_12=77319304617990777833/3^23
mu_13=4359188101895471675368/3^25  mu_14=247962796972892838442550/3^27
mu_15=1579369285225243887580357/3^27
mu_16=91152817549031658600141506/3^29
```

The generator (`scripts/gen_grand_pin.py`, GF-5) recomputes everything
fail-closed from `results/triangle.txt`; the table above is for eyeballing.

## Task DAG

```
GF-1 Series ──► GF-2 Mu ──► GF-3 MuRec ──► GF-4 Staircase ──► GF-5 PinGrand ──► GF-7 Integration
                                                          └──► GF-6 ExpForm+Lead ─┘
```

| Task | File(s) produced | Size | Model | Brief |
|---|---|---|---|---|
| GF-1 | `Polyplets/Grand/Series.lean` | S | opus | `briefs/GF1-series.md` |
| GF-2 | `Polyplets/Grand/Mu.lean` | M | opus | `briefs/GF2-mu.md` |
| GF-3 | `Polyplets/Grand/MuRec.lean` | **L (hardest)** | opus | `briefs/GF3-murec.md` |
| GF-4 | `Polyplets/Grand/Staircase.lean` | M | opus | `briefs/GF4-staircase.md` |
| GF-5 | `scripts/gen_grand_pin.py` + `Polyplets/Grand/PinGrand.lean` | L | opus | `briefs/GF5-pingrand.md` |
| GF-6 | `Polyplets/Grand/ExpForm.lean`, `Polyplets/Grand/Lead.lean` | L | opus | `briefs/GF6-expform.md` |
| GF-7 | root imports, PROOF-STATUS, audit | S | opus | `briefs/GF7-integration.md` |

Sequential spine GF-1→2→3→4→5→7; GF-6 can run in parallel with GF-5 (both
depend only on GF-4). GF-5's generator half can be written any time (it is
pure Python against `results/triangle.txt` + `pin-data.md`).

## Shared conventions (every agent MUST follow)

- **Repo/branch**: work in `~/src/polyominoes` on branch `lean-grandform`
  (create from master if absent). Commit per completed unit with prefix
  `lean-gf:`; NEVER push; never touch files outside `polyplets/` and
  `scripts/gen_grand_pin.py`; never edit a file that has a `.swp` sibling.
- **Build**: `cd polyplets && lake build` (mathlib cache is already fetched;
  on a fresh state `lake exe cache get` first). Toolchain is pinned
  (`leanprover/lean4:v4.31.0`, mathlib `v4.31.0`) — NEVER bump it.
- **Module layout**: new files under `polyplets/Polyplets/Grand/`, namespace
  `Polyplets` (matching existing files; do NOT open a `Grand` namespace).
  Each file starts with the standard copyright header (copy from `Pin.lean`)
  and a `/-! # ... -/` module doc. Import minimally.
- **Done = green**: `lake build Polyplets.Grand.<X>` succeeds with ZERO
  `sorry` and no new axioms (only `propext, Classical.choice, Quot.sound`,
  plus `Lean.ofReduceBool` exactly where a brief says native_decide is
  allowed). Check with `#print axioms <main theorem>` in a trailing
  `Sanity`-style section or via the audit in GF-7.
- **Style**: mirror the house style of `Shape.lean`/`Pin.lean` (docstrings on
  every theorem, `omega` for index arithmetic, `exact_mod_cast` at the ℕ→ℚ
  boundary, `norm_num` guards for literals). Linters are on
  (`mathlibStandardSet`); keep them green.
- **Do not re-prove what exists**: `d_rec`, `c_ident` (`Peel.lean`),
  `shape_d`, `shape`, `shape_production`, `T_diag_pow` (`Shape.lean`),
  `V_1_1 … Vt_2_2` (`Weights.lean`), j=3 weights (`Weights3.lean`,
  `Weights3Heavy.lean`), `P1_closed`/`P2_closed`/`P3_pinned`, `horner`,
  `prodPoly`, `pin` (`Pin.lean`). Read them first.
- **Oracles**: `experiments/staircase_check.py` and
  `experiments/grand_form_check.py` are the numeric ground truth. If a Lean
  statement seems numerically wrong, run the oracle before touching the
  statement; if oracle and brief disagree, STOP and report (do not "fix" the
  math silently).
- **Reporting**: final agent message must state: files written, build status,
  axiom audit of the main results, any deviations from the brief and why.

## Escalation & review protocol (orchestrator side)

- Orchestrator (Fable, the supervising session) reviews GF-3's statement
  set BEFORE the agent starts proving (it is the mathematical heart), and
  reviews each merge into `lean-grandform`.
- If an agent fails to close a lemma after two focused attempts, it must
  STOP and report the exact goal state — the orchestrator unsticks it
  (this is the only intended Fable involvement beyond planning/review).
- Merge `lean-grandform` → master at three milestones: after GF-4 (core
  theorem), after GF-5 (payoff), after GF-7 (complete). jasonp's standing
  instruction: merge before starting unrelated new commits.

## Verification gates (cumulative)

- G1 (after GF-2): `mu 1 = 25/3` and `mu 2 = 833/27` proved by `norm_num`
  from `V_1_1`, `V_1_2`, `V_2_2` — unconditional.
- G2 (after GF-3): recursion smoke tests, e.g.
  `(d 1 3 : ℚ) = mu 0 * d 1 2 + mu 1 * d 0 2` follows from `d_mu_rec` and
  equals `40 = 3·5 + (25/3)·3` by the banked native_decide values.
- G3 (after GF-4): `(T 4 3 : ℚ) = mu 0 * T 3 2 + mu 1 * T 2 2`
  (= 3·10 + (25/3)·3 = 55) via `T_staircase`.
- G4 (after GF-5): `#print axioms P16_grand_of_banked` shows standard axioms
  only; hypothesis list contains ONLY cells with H ≤ 18.
- G5 (after GF-6): `#print axioms grand_form` standard only;
  `#print axioms lead_coeff_25` standard + `Lean.ofReduceBool` (from V_1_1).
- G6 (GF-7): full `lake build` green; `rg -n "sorry" Polyplets/` empty;
  PROOF-STATUS updated; `python3 experiments/staircase_check.py` still passes.

## Why this is faithful to the paper theorem (for reviewers)

`grand-form.md` proves T(H+k,H) = [y^k](C·μ^H) (one geometric mode, sharp
onset H ≥ k+1). The μ-recursion is the coefficient-level restatement of
"multiplication by μ advances H", and the ν fixed point is the root equation
1 − S(y, z*) = 0 in disguise (evaluate S at z = ν and divide the paper's
Step-1 by hand). The staircase is the c_ident-transported version, and the
W fixed point is the diagonal Lagrange lemma's `ŵ = yφ(ŵ)` resummed. The
sequence forms avoid every ring-of-power-series obligation; all validity
ranges were checked on banked data (170/170).

## What NOT to do

- Do not formalize via `Mathlib.RingTheory.PowerSeries` — the sequence
  route is strictly simpler and was chosen deliberately.
- Do not attempt weight enumerations beyond what exists (V/Vt at j ≥ 4 are
  infeasible; the architecture never needs them numerically).
- Do not weaken statements to make proofs easier (e.g. onset H ≥ k+2):
  the sharp onset H ≥ k+1 is required — the k=16 pinning uses H = 17, 18.
- Do not restate hypotheses with wired cells (H ≥ 19 for the relevant n);
  GF-5's generator enforces H ≤ 18 fail-closed.
