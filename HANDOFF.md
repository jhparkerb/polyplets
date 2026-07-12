# HANDOFF — live state (updated 2026-07-11)

Live state only. Completed compute sessions (a(35), Even Keel, the utilization
redesign/deployment passes, the 2026-07-07 M(17)/dmirror/related-seqs jobs, the
terminal-sort investigation) are banked in `results/*.md`, `MEMORY.md`, and git
history — not repeated here. Read this file, then `MEMORY.md`'s index.

## Frontier
- **a(36) = 24629107617723857143962968288** banked+validated, `results/ns_a36/`
  (varint engine, dalby H19 long pole 3.28h). a(1)…a(36) all banked under
  `results/ns_a{n}/`; a(1)-a(20) match the b-file, a(21)+ chain-match each prior term.
- **P17 derivable+validatable** (fit real T(34,17)+T(35,18), holdout real T(36,19));
  wiring it makes a(37)'s top real height H19. **Atom Ledger** banked
  (`results/triangle-structure.md`): triangle dependency structure fully mapped,
  root-separation theorem proves no bounded-depth cross-column relation.
- **a(20) two-algorithm CONFIRMED 2026-07-11** (Redelmeier `build/g2` rev 7eab237 vs
  the TM engine): whole row n≤20 matches banked exactly, 0 mismatches. Banked
  `results/redelmeier_row20/`. Two-algorithm frontier now **20**.
- **Terminal Velocity — a(22) whole-row fleet run LAUNCHED 2026-07-11 13:41, ~3.9d
  (ETA ~2026-07-15).** g2 kernel **2.06× faster** (rev 7eab237→HEAD): L1 terminal
  pure-count (85% of nodes → branchless load+sum), L3 compile-time neighbour offsets,
  L4 u16 untried, clang++ build (Makefile G2CXX); L2/gcc-PGO/-mcpu measured
  neutral-or-worse, dropped. Ledger `results/terminal-velocity.md`.
  - **Run:** tmux window `0:g2_a22` per box, resumable, `runs/g2row_N22/`. a(22)
    subsumes a(21) (inner row 21), so this one run banks BOTH. **REBALANCED 16:40**
    (single-core bench over-predicted all-core; ayr 2990WX split-NUMA is slow all-core
    — see [[fleet-benchmark-allcore]]): now **dalby [0,14300)/80w, ayr [14300,19460)/32w,
    gympie [19460,24000)/10w**, all finish ~129h ≈ **5.4 days (~2026-07-17)**.
  - **Validation (complete):** gate-g2 green incl. new pure-count check I; row-18 AND
    row-19 fleet runs match banked exactly across all 3 ISAs (pure-count validated at
    n=18,19; the path is n-independent). Fleet per-core 1.0/1.28/3.0 (dalby/ayr/gympie).
  - **On completion:** `scripts/g2_fleet_gather.sh 22 24000`, verify rows 1..22 vs
    banked: **row 21 == 6954084405510437, row 22 == 47255332844367680** (both already
    known from the TM engine; this is the independent Redelmeier two-algorithm
    confirmation, not a first computation). Moves the two-algorithm confirmation
    frontier 20 → **22** (subsumes 21). a(23) ~27d (impractical).
  - **Monitor:** poll driver.log for `progress=/eta=` lines; robust poll-waiter
    (NOT tail --pid — it dropped once on row-19). Resume: re-run the launch script.

## Rigorous λ bounds (NEW 2026-07-11)
- **Two-sided rigorous bracket 5.828 ≤ λ ≤ 9.3153**, numerical λ≈7.111 inside.
  Lower: directed/multi-directed king animals (3+2√2 exact, 6.475 Bacher). Upper
  (first ever, ours): Bui-style finite-type convolution certificate, `x=2147/20000`,
  machine-verified in exact rational arithmetic.
- Derivation `docs/proofs/polyplet-upper-bound.md`; certificate `experiments/king_certificate.py`.
  **Certificate Squeeze** (docs/certificate-squeeze-plan.md): P1 (exact cert) + P2 (slack
  audit) done; **P3 not pursued** — the over-count is the connectivity wall (diffuse,
  compounding, non-local), floors this method class above λ. Paper paragraph + `bui2025`
  bib entry landed in `paper/polyplets-report.tex`.

## OEIS submission — gated on jasonp's viva
Batch staged and checklist-clean (`oeis/README.md` checklist; b-files
`results/b*_upload.txt` for all six sequences — A006770+A030233 to a(33), the four
D-dependent to n=32; a(34)+ staged as conjectured comments). **Submission is jasonp's,
gated on his own readiness process** (OEIS AI policy makes the author personally
responsible; `docs/oeis-ai-policy.md`).
- **Viva** (local-only, git-excluded: docs/viva-exam.md, viva-reserve.md [chmod 000],
  viva-state.md, drill{1,2}-*.md): first exam 56.5/100 vs bar ≥80. Drills 1 & 2 graded;
  cold retake variants (V8/V12/V13, V18/V19/V20) still pending after a spacing gap.
  Full state: docs/viva-state.md.
- Before submit: jasonp rewrites all staged %C in his own words (Claude meaning-checks
  only); signature dates → actual submission day; pink-box replies jasonp's alone.

## Paper (`paper/polyplets-report.tex`)
Computational-report form, five external review rounds + self-check. Growth §3 confluent
3-param fit (Δ₁=1/2, λ≈7.111). Now includes the rigorous **upper-bound** paragraph
(above). `paper/verify_claims.py` — 397+ checks GREEN (parses tables from the .tex).
Compiles clean (no undefined refs/citations). **Final read-through DONE 2026-07-13**;
now includes the diagonal-law THEOREM (thm:diaglaw), the spine-cubic subsection
(sec:spine), the single-hole max-hole THEOREM (thm:diamond, multi-hole reduced to
peeling as conjecture+open problem), k<=16 corrections, a(36) cost profile.
verify_claims 406/406 (adds: proof checker, ab-initio grand form, (2s+1)^2,
spine digit-product on all in-band cells).

## Open threads
- **Lean proof** (branch `lean-diagonal-proofs`, `polyplets/PROOF-STATUS.md`):
  (a) finiteness, (b) row profile, (c-fwd), (d-local) done+green; remain (c-rev),
  (d-global gap≤2), (e) offset-chain count.
- **Unmerged engine branches — jasonp's call whether/when** (engine work deprioritized
  per the close target): `tm-hotpath-optim` (RunRecord shrink + pmr allocator, real
  4.47% dalby win, gates+ASan clean); `redesign` / kink-sharded (K-shard private-sweep
  kernel, opt-in `--kernel kink-sharded`, real 4.93x at H14/maxn26, still not the default
  and not head-to-head'd at dominant-height scale).
- **steal-tail diagnostic** (`results/steal-tail-h18.md`): banked, not deployed.
- **a(37) costed, on the shelf (2026-07-12):** with the varint engine, ~3.5h wall
  (~170 core-h, dalby H19 pole 3.4h + ayr H<=18, RAM ~400MB) if P17 is wired as
  certified via the banked T(36,19) holdout (its fit uses the out-of-onset n=34
  point); **~10h wall on the strict paper convention** (sweep H20 real ~9.8h pole
  => certifies P17 unambiguously, retires a(36)'s T2-, ends the banked range
  certified at an odd frontier per the frontier-parity law in
  results/ternary-spine.md). Boxes busy with a(22) until ~07-17. jasonp's call.
  **P17-from-the-gas MEASURED DEAD 2026-07-13** (results/defect-gas.md): weight-DP
  cost ~20x/k, k=17 ~10^17s; the strict H20 sweep is the only certification route.
- **Ternary Spine (2026-07-12, BANKED):** the height triangle mod 3 is governed by
  the spine cubic **W³ = W² + t** over 𝔽₃ — digit-product law, first-nonzero-per-
  column ≡ 1, and the **SNF count ⌈(N−1)/3⌉ PROVED** modulo the diagonal law + a
  3-item ladder. `results/ternary-spine.md`, `experiments/ternary_spine.py` (15/15).
  **Ladder RETIRED as empirical input 2026-07-12** by the defect gas (below).
  Open: individual SNF exponents. Candidate paper paragraph — jasonp's call.
- **Defect gas / MASTER EQUATION (2026-07-12, BANKED):** `results/defect-gas.md`,
  `experiments/defect_gas.py` (row model + `master`/`ladder` checks). The diagonal
  law's H is the grand-partition factor of a 1D cluster gas; exact chain identity
  (40/40 vs banked triangle incl. boundaries); master equation
  H = 1 + Σ Ŵ_c u^k H^-(k+ℓ) exact through u³; valuation lemma (k ≥ ℓ) ⟹
  **spine cubic H³=H²+u DERIVED mod 3**, mod-9 lift derived, finite mod-27
  equation matches all 18 coefficients; (⋆a) G≡1 mod 9 derived via boundary
  weights (single-row boundary weight 2s+1 — entry×exit factorization of
  (2s+1)²); **(⋆c) PROVED 2026-07-13** (H(u³) ≡ H²+25u−3u²−3uW mod 9, from the
  mod-9 cubic alone) — the whole ladder is now symbolic, zero empirical input.
  Open: two-row closed form.
- **DIAGONAL LAW SHAPE PROVED (2026-07-12):** `docs/proofs/diagonal-law.md`,
  checker `experiments/diagonal_law_proof_check.py` (all green, k ≤ 3 exact).
  Separation lemma (walk rows are cuts) + exact chain identity + row bound
  (ℓ ≤ k) + partial fractions ⟹ T(n,n−k) = P_k(n)·3^{n−1−3k} for n ≥ 2k+1
  with deg P_k ≤ k and **P_k integer-valued** (new, was only observed). Onset
  matches observation exactly. Downstream: Ternary Spine / SNF / P_k machinery
  conditionality collapses to the finitely many enumerated cluster weights.
  Open: onset sharpness for general k (non-cancellation); monomial integer
  coefficients of P_k (values proved, coefficients observed).
- **Max-hole theorem M(n)=round((n−2)²/8) — STAGED for later examination**
  (`results/maxhole-proof.md`, figs `results/figs/maxhole_{ring,seal}.svg`, checker
  `experiments/maxhole_proof_check.py`). Near-complete proof: construction = diagonal
  diamond ring (done for n≡0 mod 4); upper bound reduced to **one open lemma (II')
  n≥ha+hm+2** (a closed king-curve enclosing an ha×hm diagonal region needs ≥ha+hm+2
  cells). (I') + single-hole reduction + arithmetic in hand; both lemmas verified on
  ~2400 single-hole polyplets (0 violations, tight on diamonds). Partial (II'):
  foreground provably extends 1 step beyond the hole on all 4 sides; the sum (vs max)
  needs a winding/Jordan-curve argument. Also open: clean elongated-diamond family for
  n≢0 mod 4. Jasonp to examine the (II') winding argument. Session-research thread;
  companions this session: [[hole-free-growth-constant]], [[height-distribution-collapse]],
  results/series-analysis-da.md (θ=−1).

- **dm-mirror law proof program STARTED (2026-07-13):** `results/dm-diagonal-recon.md`,
  `experiments/dm_sym_enum.py` (validated vs banked law). d(S,S)=2 PROVED
  (permutation skeleton: monotone king permutations). Two-family dichotomy
  refuted (anti-excursion family = the known parity anomaly); proof frame =
  monotone phases + reversal clusters, program steps 1-4 in the recon doc.
  Prize: retires the paper's last conjectural law + the T3 caveat.

- **Kernel/haruspicy/ACSV program (2026-07-14, in flight):** order K2 -> H1 ->
  ACSV -> K1 -> H2 -> K3. K2 DONE (Temperley on column-convex polyplets =
  rediscovery of A187077, pipeline validated; results/convex-polyplets.md).
  H1 DONE (results/anisotropic-not-dfinite.md): pole-argument theorem
  excludes y-ODEs for the height-anisotropic GF in quantified (order,
  x-degree) boxes (up to r<=5 & D<=28 ... r=0 & D<=3288), from mod-p-certified
  new-root contents psi_H (deg 1..3289, squarefree, lowest terms, H<=10);
  full non-D-finiteness conditional on deg psi -> infinity. H=11 banked GF
  found anomalous (validated=False, shares no roots with Q9Q10) — needs
  re-recovery before any use. ACSV (added):
  saddle-point on the grand form G(y)H(y)^n to prove the height-distribution
  collapse profile on the tall flank. Then K1 (kernel on all-pairs gap walk,
  exact ~14.41), H2 (haruspicy on convex-by-area), K3 (exact convex mu,
  q-series). Garnish when idle: Sheffer/Riordan convolution identities for
  P_k as new cross-checks; p=2 spine considered-and-declined (3-powers are
  units mod 2, no collapse).

## Remaining work ledger
1. **Paper final read-through.**
2. **Viva cold retakes**, then %C authorship pass (jasonp's own words), then jasonp submits.
3. **Lessons-learned document** (jasonp + Claude) — jasonp's explicit ask; after compute
   and paper, BEFORE submitting. The six postmortem failure classes as day-one practices
   are captured in MEMORY.md ([[next-project-practice]]).

## Starting a fresh session from here
Read this file, then `MEMORY.md`'s index (auto-loaded) for standing practices. No open
thread needs immediate action; pacing is jasonp's (viva retakes, whether to merge the
unmerged engine branches, whether to revisit a(37)+ compute given the reach ceiling).
