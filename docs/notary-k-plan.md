# Notary piece K: the kernel method at all orders, in Lean

2026-08-09. Companion to `docs/notary-kernel-scoping.md` (piece K's pricing)
and `docs/notary-lean-plan.md` (campaign conventions). Target head theorem:

    Φ(x, N(x)) = 0   exactly, in ℚ⟦x⟧,

for the walk series `N` whose truncations `DepthOneSeries.nSeries` already
pins to the banked defect at `k ≤ 19` and annihilates mod `x^61`. With T and
B closed, this upgrades every campaign constant from "branch data of a pinned
curve" to "derived from the walk, end to end".

## 0. Measurement basis

`experiments/notary_k_measure.py` (log `build/notary_k_measure.log`,
2026-08-09, 79 s) verified numerically every statement class below, before
any skeleton was written:

- **m1** the closed-form transition rows (generic `g ≥ 3` both classes, four
  boundary rows with uniform tails, start vectors) against
  `depth1_gap_walk.transitions`, `g ≤ 29`, `gp ≤ 60`;
- **m2** J-support `≤ 2m + 2` and P-tail constancy from `g ≥ 2m + 3`
  (interior start is tight at `2m + 3`, bare start reaches `2m + 2`);
- **m3** the two master double-series identities (§2) coefficient-wise,
  `u`-orders `≤ 44`, `y`-orders `< 14`, both starts;
- **m4** the square-root recursions for `A`, `B`, the shifted-series roots
  `u₁`, `u₂`, their kernel identities to `s`-order 51, and agreement with
  the sympy roots;
- **m5** the cleared 6×6 system (§3): the walk's own series satisfy it
  (both starts, `s`-order 28), the sympy closed forms satisfy it exactly,
  and both determinants have **valuation 12 with leading coefficient −16**
  — the uniqueness certificate is one rational number;
- **m6** transcription sizes: every closed-form component is ≤ 235 chars
  with per-component `s`-poles of order ≤ 4 that cancel in the basis
  combination; all polynomial denominators are units in ℚ⟦s⟧;
- **m7** the elimination identity `Ψ(T) = 0` in the algebra
  `ℚ(s)[A,B]/(A²−AA, B²−BB)` (the future `ring` lemma), the `y`-form
  quartic `cY₀..cY₄` (≤ 115 chars each), its numeric annihilation of `F₁`
  to `s`-order 41, and the exact lift `Σ cYₖ(3x)((W−1)/3)^k = (1/3)·Φ(x,W)`
  against the banked `PHI_COEFFS`.

## 1. Architecture in one paragraph

Everything lives in `ℚ⟦s⟧` (`y = s²`); no topology, no complex analysis.
The walk's exact (uncapped) values exist by piece T's cone lemma
(`GapWalkTrunc.iter_agree`); its per-gap generating series `ĵ_g`, `p̂_g` are
even series, and locally finite sums (`val ≥ g` per term) are defined
coefficient-wise by a small bespoke library — not Mathlib topology. The two
master identities (§2) hold per column by the closed-form rows; evaluating
the `u`-columns against the kernel roots `u₁, u₂ ∈ s·ℚ⟦s⟧` telescopes them
into six closing equations per start vector — with the P-side equations
*cleared* of `D′(uᵢ)` denominators, so every equation is polynomial in the
generators. The transcribed sympy solution satisfies the same affine system
(pure `ring` over `A² = (1−3s)(1+s)`, `B² = (1+3s)(1−s)`); the difference is
killed by Cramer (`Matrix.adjugate_mul`) in the domain ℚ⟦s⟧, using
`coeff 12 (det M) = −16 ≠ 0`. The assembly `F₁ = P̂ − B²/(3+S)` and the
degree-4 norm identity `Ψ(T) = 0` then annihilate `F₁` by the `y`-form
quartic; the substitution `x ↦ s²/3` (`rescale` + `expand`, injective)
carries this to `Φ(x, N(x)) = 0`.

## 2. The two master identities

With `D(u) = u² − y(1+u+u²)²`, `J₃ = J − j₁u − j₂u²`, `P₃ = P − p₂u²`:

    D·J₃ = u²·Q,            Q = J0 − j₁u − j₂u² + y·R_J          (J-master)
    D·(P₃ − 2J₃) = u²·(P0 − p₂u² − 2J₃ + y·R_P)                  (P-master)

as identities per `u`-column with ℚ⟦s⟧-coefficients (`R_J`, `R_P` as in
`experiments/severance_w2_kernel.py`; the `1/(1−u)` tails of `R_P` and `P0`
are geometric columns). Verified coefficient-wise (m3). At `u = uᵢ`,
`D(uᵢ) = 0` kills the left sides; the derivative of the J-master gives
`D′(uᵢ)·J₃(uᵢ) = uᵢ²·Q′(uᵢ)`, which clears `J₃(uᵢ)` from the P-side. The
six closing equations per start are then

    (1),(2)  Q(uᵢ) = 0
    (3)      j₁ = [u¹]J0 + y(j₃ + c₁)
    (4)      Jm·(1 − 9y) = Q(1)        [proved as a column *sum*, not u = 1]
    (5),(6)  D′(uᵢ)·(P0(uᵢ) − p₂uᵢ² + y·R_P(uᵢ)) − 2uᵢ²·Q′(uᵢ) = 0

— (4) never substitutes `u = 1` (not a legal series substitution): it is the
`g ≥ 3` column-sum of the step recurrence, finite per order by J-support.

## 3. Modules and waves

One agent per module, statements pre-verified, gate RED first, as in T/B.

**Wave K-α (independent, 3 agents in parallel):**

- `GapWalkRowVals.lean` — the closed-form rows: generic `g ≥ 3` values for
  both classes (bulk `(1,2,3,2,1)`, J-background `8/2/8/12`, fold-downs at
  `gp ≤ 2`), the four boundary rows (heads + uniform tails, symbolic `gp`),
  start-vector values, and `stepMul g c 1 false = 0`. Counting analogue of
  `GapWalkRows` (values, not vanishing): filter-length = explicit count via
  `omega`-driven interval case analysis. ~25 lemmas.
- `KernelSeriesLib.lean` — the locally-finite-sum library over
  `PowerSeries ℚ`: `lfsum F := mk (fun n => Σ_{g ≤ n} coeff n (F g))` with
  hypothesis `∀ g n, n < g → coeff n (F g) = 0`; linearity, fixed-factor
  pull-through, shift/reindex, finite-support collapse; plus the
  truncation homomorphism (`trunc`-lists vs `tmul`/`tinvAux` of
  `GapWalkBridge`) that the det certificate consumes.
- `KernelRoots.lean` — `A`, `B` by coefficient recursion (`A² = 1−2s−3s²`,
  `B² = 1+2s−3s²`, constant term 1), `u₁ = ((1−s)−A)/2s`,
  `u₂ = (−(1+s)+B)/2s` as shifted series with defining relations
  `2s·u₁ = (1−s) − A` etc., kernel identities `uᵢ² = y(1+uᵢ+uᵢ²)²`,
  positivity of valuation, `(1−uᵢ)` units, `D′(uᵢ)` and its valuation-1
  normal form.

**Wave K-β (2 agents):**

- `GapWalkExact.lean` — exact walk values `jE`/`pE` per start (stable caps
  via `iter_agree`), the exact step recurrence as a finite sum over the
  closed-form rows, J-support `≤ 2m+2`, P-tail constancy from `2m+3`,
  `pE m 1 = 0`, and the end-functional bridge: `qEndF`/`bareEndF` of the
  iterates as linear reads of `jE`/`pE` — the walk-emitted numbers.
- `GapWalkColumns.lean` — the column series `ĵ_g`, `p̂_g`, tail series, and
  `Jm` as elements of ℚ⟦s⟧ (even, `y = s²`); the two master identities of
  §2 per `u`-column, from the exact recurrence.

**Wave K-γ (1 agent, after α+β):**

- `GapWalkClosing.lean` — `J₃(uᵢ)`, `P₃(uᵢ)` via `lfsum`; the telescoping;
  the six closing equations per start as ℚ⟦s⟧ identities; equation (4) as
  the column sum; the emitted-family series `S`, `B`, `P̂` in terms of the
  six unknowns (end-functional bridge).

  *Telescoping design (worked out 2026-08-10, before the skeleton):*
  transport the K-β column identities through `expand 2` (`X ↦ X²`, an
  algebra map: identities map to identities, `ĵ_g := expand 2 (jY F g)`).
  For a root `u` define the evaluated series by `lfsum` over cutoff
  columns (`if g < 3 then 0 else ĵ_g` etc.; `LocFin` from
  `constantCoeff u = 0` via `coeff_pow_eq_zero`). The master identity
  evaluated at `u` — `D(u)·J₃(u) = u²·Q(u)` — is proved columnwise: write
  `D(u)·J₃(u) − u²·Q(u)` as one `lfsum` over target powers `n` (shift
  algebra: `lfsum_mul_left` for the five kernel multiples, `lfsum_shift`
  to reindex), whose `n`-th family member is exactly the transported
  column identity at `n` (generic for `n ≥ 7`, the four exceptional
  columns for `n = 3..6`, zero below) — so the family is zero pointwise
  and the lfsum vanishes. Then `D(u) = 0` (kernel identity) and `u² ≠ 0`
  (domain; `coeff 1 u = 1`) give `Q(u) = 0`: equations (1), (2). The
  P-side runs the same route on `f_g = p̂_g − 2ĵ_g` with two extras: the
  constant tails `C pt` collapse by a geometric lemma
  (`(lfsum fun g => u^g) · (1−u) = 1`, provable by `lfsum_shift`
  telescoping; `(1−u)⁻¹` units from `KernelRoots`), and instead of
  dividing by the valuation-1 series `D′(u)` the equations stay in the
  cleared form (5), (6). Equation (3) is the transported `u³` column
  verbatim; equation (4) is the columnwise sum of the generic identities
  over `3 ≤ g ≤ 2m+2` per coefficient (window sum `= 9` inside, boundary
  corrections at the window edges die by `J`-support). The six equations'
  target forms are `equations_cleared` of
  `experiments/notary_k_measure.py` (m5: walk satisfies them, s-order 28,
  both starts); `P0(u) = C p02·u² + C pt·u³·(1−u)⁻¹` uniformly covers
  both starts.

**Wave K-δ (3 agents, sequential dependencies inside the wave):**

*Architecture refinement (worked out 2026-08-10, before the generator):*
the closed-form entries have per-component `s`-poles (m6), so they are
not definable componentwise as series. Instead the generator emits, per
start and per entry `k`: a shift `e_k ≤ 4`, a common unit denominator
`d_k(s)`, and numerator polynomials `N_{k,i}(s)`, defining the *regular*
series `ŷ_k := (Σ_i N_{k,i}·basisᵢ)·(d_k)⁻¹` (basis `1, A, B, AB`); the
transcription theorem is `X^{e_k}·d_k·x_k = ŷ_k` — poles never appear.
The six γ equations are cleared to polynomial rows by the *defining
relations* instead of substitution: multiply row (1) by `(2X)⁴` and
rewrite every `(2X·u₁)^j` by `u1_def` (`2X·u₁ = 1−X−A`); rows (5),(6)
additionally clear the geometric `w`-factors by `(1−uᵢ)` via
`one_sub_u1_mul_w1`; the generator computes each clearing monomial and
the `linear_combination` cofactors (from `u1_def`/`u2_def`, the two
square relations, and the `w` identities). Uniqueness stays as planned
(truncL det certificate at coeff 12 = −16, `Matrix.adjugate_mul` in the
domain, on the *cleared* system so entries are polynomial in
`X, A, B`); the Ψ/quartic step runs on the closed forms with `s`-powers
cleared by the generator (multiply through by the max shift), sizes
staying m7-scale.

*Full δ chain (settled 2026-08-10, stage-1 generator data in
`build/notary_kdelta_data.json`, verified — entries ≤ 235 chars, shifts
≤ 4, unit denominators, lift ratio exactly 1/3):*
1. **Cleared rows for the walk** — from the γ equations by
   `(2X)^deg`-clearing (rewrite `((2X)·u₁)^j` via `u1_def`, powers `j ≤ 8`
   as squared/cubed congruences of it) and one `(1−uᵢ)` factor for the
   `w`-rows via `one_sub_uᵢ_mul_wᵢ`. Generator emits the row polynomials
   `M_{rc}, R_r ∈ ℚ[X,A,B]`, numerically verified; the agent proves each
   row from the γ equation by `rw`/`linear_combination` — no generator
   cofactor certificates needed.
2. **The closed forms as series** — `x̂_c := (divX)^[e_c] (num_c) · d_c⁻¹`
   where `num_c = Σᵢ N_{c,i}·basisᵢ` (regular; `divX` iterated `e_c ≤ 4`
   times). Transcription lemma `X^{e_c}·d_c·x̂_c = num_c` needs only the
   finite certificate `coeff n (num_c) = 0` for `n < e_c` (A/B coefficient
   literals). `M·x̂ = R` rows: multiply row `r` by `X^E·D`
   (`E = max e_c`, `D = lcm d_c`) so it becomes a generator-verified
   `ring` identity in `ℚ[X,A,B]` mod the two square relations; divide the
   unit/`X`-powers back out (domain).
3. **Uniqueness, abstract** — `M·(x_walk − x̂) = 0`, so
   `det M · (x_walk − x̂) = adj M ⬝ (M ⬝ (x_walk − x̂)) = 0`
   (`Matrix.adjugate_mul` — never expanded); `coeff 12 (det M) = −16 ≠ 0`
   via the `truncL` list certificate (entries truncated through the A/B
   literals; Leibniz over 720 permutations in list arithmetic,
   `norm_num`-evaluated, never `native_decide`); domain ⇒
   `x_walk = x̂` componentwise.
4. **Φ** — walk `F₁` (γ's `qSeries`/`bSeries` bridge) equals the
   closed-form `F₁`; the `Ψ`→`cY` quartic annihilates it (`ring`
   identity on the stage-1 `n0..n3`/`den` data, `s`-powers cleared);
   lift `x ↦ s²/3` by `expand 2 ∘ rescale (1/3)` against the banked
   `PHI_COEFFS` with the verified scale `1/3`; head theorem
   `Φ(x, N(x)) = 0`.

- `DepthOneKernelSol.lean` — the transcribed closed forms (12 entries ×
  4 components, ≤ 235 chars each, per-entry `s`-pole cleared by an explicit
  shift), and `M·X̂ = R` for both starts: each row multiplied through by the
  exact `s`-power and units that make it a polynomial identity in
  `ℚ[s, A, B]` mod the two square relations — `linear_combination`/`ring`.
  Statements generated and numerically verified by a committed generator
  script before the skeleton lands. May split into `...SolInt.lean` /
  `...SolBare.lean` if build times demand.
- `DepthOneKernelUnique.lean` — `coeff 12 (det M) = −16` (finite rational
  arithmetic through the truncation homomorphism; `A`-coefficients to order
  12 as lemma literals), `det M ≠ 0`, Cramer via `Matrix.adjugate_mul` in
  the domain ℚ⟦s⟧: **the walk's six series are the closed forms** — twice.
- `DepthOneKernelPhi.lean` — `F₁ = P̂ − B²/(3+S)` (unit `3+S`), the norm
  identity `Ψ(T) = 0`, the `y`-form quartic `cY₀..cY₄` annihilating `F₁`,
  the lift to `Φ(x, N(x)) = 0`, and the corollary re-deriving
  `DepthOneSeries.phi_annihilates`.
  **Quartic (measured, `experiments/notary_kdelta_gen6.py`):** the whole
  `y`-form quartic collapses to a *single scalar* elimination identity
  `Ψ(numTuple) = 0` in `ℚ⟦s⟧` mod `A²=AA, B²=BB` (`numTuple = n0 + n1 A +
  n2 B + n3 A B`, `d = numTuple − n0`): `(d² + Pq)² = 4 AA (d n1 + n2 n3
  BB)²`, one `linear_combination` over `Kernel.A_sq/B_sq`, cofactors cA
  17872 / cB 8122 chars — the same one-shot regime as `Sol`/`Unique`
  (heartbeats 16M, `maxRecDepth 8000`; cert in `build/notary_kdelta_phi_cert.txt`).
  **Lift — design pivot (`PowerSeries.rescale` does NOT exist in this
  Mathlib):** do the `x ↦ 3x` scaling coefficient-wise exactly as
  `DepthOneSeries.nSeries` already does (`N` coeff `k = 3^(k+1)·[y^k]F₁ +
  [k=0]`), *not* via `rescale`. `phiF1` (the `s`-tuple, `den/n0..n3`) is
  **even in `s`** (`n0, den, n3` even; `n1,n2` mirror-paired through
  `A↔B` under `s ↦ −s`), so `phiF1 = e2 (F1y)` for the exact `y`-series
  `F1y := mk (fun k => coeff (2k) phiF1)` — an evenness sub-lemma is owed.
  Head `N := mk (fun k => 3^(k+1)·coeff k F1y + if k=0 then 1 else 0)`;
  `Φ(x,N) = Σ_k phiC_k·N^k = 0` transported from the `y`-quartic by the
  lift `ring` identity `3·Σ cY_k(3x)((W−1)/3)^k = Σ phiC_k W^k` (verified
  in gen6); corollary re-derives `phi_annihilates` via `truncL` to the
  list model.  `e2 = expand 2` and `truncL_mul/_mk/_getD` are the bridge.

## 4. Gate and axioms

`gate-notary` extends by each landed module (sorry/axiom grep + build).
Target axiom footprint: standard axioms only for every walk-side module
(K-α through K-γ); `native_decide` is permitted only where the existing
modules already use it (none planned; the det certificate is designed to
land with `decide`/`norm_num` on order-12 literals) — if an agent cannot
avoid it, that is a statement-design failure to bring back, not a license.

## 5. Order of battle

1. Fable: this plan, wave K-α skeletons (numerically pre-verified
   statements), RED gate, agent briefs. Commit.
2. Wave K-α: 3 agents in parallel, then `make gate-notary`.
3. Fable: K-β skeletons against K-α's landed API; 2 agents.
4. Fable: K-γ skeleton (the telescoping statements are the one place the
   summability library and the roots meet — drafted in full, not sketched);
   1 agent.
5. Fable: generator script for K-δ (X̂ literals, cleared-row identities,
   det tuple, `cY` literals; each emitted statement re-verified
   numerically), then the three K-δ skeletons; agents in dependency order.
6. Every wave ends `make gate-notary`; full `make` once per code-touching
   session. Waves respect the 3-hour usage window; no ETAs are quoted
   because none have a measured basis.

## Execution status

- 2026-08-09: plan written; measurement m1–m7 all pass
  (`build/notary_k_measure.log`).
- 2026-08-09: wave K-α complete — `GapWalkRowVals`, `KernelSeries`,
  `KernelRoots` all proved, zero sorries, standard axioms only, both
  `#guard_msgs` audits green per module. One statement fix during the wave,
  made by the author not the agents: `lfsum_of_support_lt` gained its missing
  `LocFin F` hypothesis after the KernelSeries agent produced a counterexample
  to the stated form and correctly left it sorried. No other statement
  changed. `make gate-notary` green; full `make` green
  (`build/make-full-notary-K-alpha.log`).
- 2026-08-10: wave K-β opened — skeletons `GapWalkExact.lean`,
  `GapWalkColumns.lean` committed RED, every statement numerically
  pre-verified (`experiments/notary_kbeta_statements.py` b1–b6,
  `build/notary_kbeta_statements.log`). Two design deviations from the
  wave-β paragraph above: (1) the m2 P-tail-constancy lemma is dropped — no
  downstream statement consumes it (the geometric tail columns of the
  master identities carry the start-data constant `pt`, not walk values;
  the closing equations read the tails through `(1−uᵢ)⁻¹`, provided by
  `KernelRoots`); (2) the column series and master identities live in the
  `y`-variable `ℚ⟦X⟧` — the `s`-variable versions are one `expand 2`
  transport, deferred to wave K-γ where the roots live. Because Columns
  imports Exact and the RED audit guards block dependent elaboration, the
  two agents run sequentially: Exact first, Columns once Exact is green.
- 2026-08-10: wave K-β complete — `GapWalkExact` (12 sorries) and
  `GapWalkColumns` (11 sorries) both proved, zero statement changes
  (verified by diff: imports, private helpers, proof bodies only), audit
  guards green, standard axioms only. `make gate-notary` green.
- 2026-08-10: wave K-δ generator complete (stages 1+2,
  `experiments/notary_kdelta_gen.py` / `notary_kdelta_gen2.py`, data in
  `build/notary_kdelta_data*.json`, both ALL PASS): pole-free closed forms
  verified against the walk; Ψ and the quartic re-verified, lift ratio
  exactly 1/3; the cleared polynomial system emitted (row entries ≤ 53
  chars — far below the m6 worst case), the walk satisfying it
  numerically and the closed forms satisfying it *exactly* in the tuple
  algebra; cleared-det certificates: valuation 22 / lead −16 (interior),
  valuation 18 / lead −16 (bare); divX low-coefficient guards pass.
- 2026-08-10: wave K-γ complete — `GapWalkClosing` (24 sorries) proved
  across three agent rounds (the third unblocked by the coordinator's
  diagnosis: the `−2·J₃` right-side term of the P-master is a shifted
  lfsum family, not a finite polynomial). All six closing equations of
  the cleared system are now theorems of the walk at the kernel roots,
  both starts, generic in the start package; statements untouched
  throughout; audit guards green, standard axioms only. `make
  gate-notary` green.
- 2026-08-10: wave K-δ `DepthOneKernelSol` complete — the twelve cleared
  num-form row identities proved by emitted `linear_combination`
  certificates over `Kernel.A_sq`/`B_sq` (generator
  `experiments/notary_kdelta_gen3.py`, all re-verified as free-polynomial
  identities before emission); zero agent rounds, statements untouched.
- 2026-08-10: wave K-δ `DepthOneKernelUnique` complete (0 sorries,
  standard axioms, `make gate-notary` green). The 6×6 cleared system is
  expanded by a new private `det_fin_six` (Mathlib `det_fin_three`
  pattern, no det lemmas on the large entries), matched to the
  pre-verified `detTup` combination, its coeff pinned (valuation 22 int /
  18 bare, coeff −64 after row-1/2 doubling), non-vanishing established,
  and the six walk unknowns solved by adjugate uniqueness and transcribed
  to `X^e · den · unknown = num`, both starts. Only `Phi` remains.
- 2026-08-10: wave K-δ `DepthOneKernelPhi` COMPLETE, **piece K done
  (option A)**. `phi_annihilates_exact : PhiOp Nexact = 0` — the exact
  `Φ(x, N(x)) = 0` in `ℚ⟦x⟧` at all orders, standard axioms, no
  `native_decide` — is proved. Two generated certificates carry it:
  `quartic_tuple` (the scalar quartic, 26k `linear_combination`) and
  `quartic_cleared` (the cleared annihilation, 41k, `gen7`; the degree-40
  factor `g` is not needed in Lean by the domain argument). `phiF1_even`
  went in via a from-scratch `X ↦ −X` involution swapping `A`, `B`; the
  lift is coefficient-level (no `rescale`) through a `×3` ring hom.
  **Scope boundary:** the walk↔closed-form bridge `truncL 61 Nexact =
  nSeries 60` is identity (II) = **piece D**, not provable in K (the
  existing `walkFamilies`↔value links are `native_decide` at finite order
  only). So `phi_annihilates_of_exact` re-derives
  `DepthOneSeries.phi_annihilates` taking that bridge as an *explicit
  hypothesis* `hbridge`; no bare `sorry`. Remaining to fully close: wire
  the module into `gate-notary`/`Polyplets.lean`, add the axiom audits,
  `make gate-notary` + full `make`, results doc.
