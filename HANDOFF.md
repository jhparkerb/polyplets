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
- **a(22) REDELMEIER CONFIRMATION COMPLETE 2026-07-16**
  (results/redelmeier_row22/): fleet run finished cleanly on all three
  boxes (~119h dalby / 116h ayr / 122h gympie, 5% spread — rebalance held);
  all 24,000 shards gathered+combined; **every row n=1..22 matches banked
  exactly** (row 21 = 6954084405510437, row 22 = 47255332844367680).
  **Two-algorithm frontier now 22.** Boxes ALL FREE. Unblocked, jasonp's
  call: a(37) (~3.5h trusted-P17 / ~10h strict) and the H=11 GF
  re-recovery. Run history in results/terminal-velocity.md + provenance.

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
Compiles clean (no undefined refs/citations). **FULLY CURRENT as of 2026-07-15**:
second wave landed (sec:universal — lattice-universality of law+spine incl.
w-counterexamples and polyiamond extension; hole-graded diagonal-law paragraph
in sec:holes; deficit-2 proof note in sec:spine; abstract/contributions
updated); verify_claims **412/412** (now runs hex/universal/holefree/
hole-strata/deficit2 checkers). Earlier: **final read-through DONE 2026-07-13**;
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
  **Deficit-2 law PROVED 2026-07-15** (experiments/deficit2_proof.py):
  T(3m+2,2m+1) == 2 mod 3 for all m, via Lagrange-Buermann diagonal ->
  rational identity on the mod-27 master curve -> exact polynomial division
  (E monic in H, remainder 0). Row-reading picture fully theorem-grade; the
  LB-to-curve-division method is reusable for any linear-family congruence.
  Onset sharpness (general k) attempted, remains OPEN: leading coefficient
  = signed composition of the (non-C-finite) all-pairs family — sign-definite
  after (-1)^k twist on data, no proof.
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

- **dm-mirror law PROVED (shape) 2026-07-15** (docs/proofs/dm-diagonal-law.md):
  segment grammar (<=2k+1 perfect diag/anti segments, reversal lemma tight) +
  turn-orbit cost + type finiteness + one-parameter Ehrhart (period 2, coeffs
  {1,2}) + telescoping rank bound => d(S,S+k) per-parity polynomial deg <= k
  past an effective onset; poles only at +-1. NOT proved: sharp onset
  2k+2/2k+3, multiplicity split (k+1,k) — data-grade, like king sharpness.
  Referee pressure point: Lemma 5 (rank/telescoping). Paper updated in 5
  places (abstract/intro/contributions/T3 tier/dmdiag section; T3
  degree-transition failure mode eliminated, onset-shift mode remains,
  bounded); verify_claims 407/407, compiles clean. Program history: `results/dm-diagonal-recon.md`,
  `experiments/dm_sym_enum.py` (validated vs banked law). d(S,S)=2 PROVED
  (permutation skeleton: monotone king permutations). Two-family dichotomy
  refuted (anti-excursion family = the known parity anomaly); proof frame =
  monotone phases + reversal clusters, program steps 1-4 in the recon doc.
  Prize: retires the paper's last conjectural law + the T3 caveat.

- **Kernel/haruspicy/ACSV program (2026-07-14, in flight):** order K2 -> H1 ->
  ACSV -> K1 -> H2 -> K3. K2 DONE (Temperley on column-convex polyplets =
  rediscovery of A187077, pipeline validated; results/convex-polyplets.md).
  H1 DONE + UNCONDITIONALIZATION PUSH 2026-07-15 (results/anisotropic-not-dfinite.md):
  dominant-pole dichotomy theorem (y-D-finite => deg_Q(mu_H) <= D for all but
  r heights); strip growth constants proven strictly monotone (PF route,
  verified exactly H<=10); atoms psi_1..psi_8 CERTIFIED IRREDUCIBLE (degrees
  1..462, multi-prime subset-sum certificates) => deg_Q(mu_H) = atom degree;
  residual conjecture PROVED 2026-07-15 via Northcott finiteness (bounded
  degree + bounded house + infinitude of distinct mu_H = contradiction):
  **THEOREM: the height-anisotropic polyplet GF is NOT D-finite,
  unconditional** — proof template lattice-universal (polyominoes by height
  etc.); literature check flagged in papers/MISSING.md before claiming
  novelty externally. Candidate paper paragraph — jasonp's call. Also: pole-argument theorem
  excludes y-ODEs for the height-anisotropic GF in quantified (order,
  x-degree) boxes (up to r<=5 & D<=28 ... r=0 & D<=3288), from mod-p-certified
  new-root contents psi_H (deg 1..3289, squarefree, lowest terms, H<=10);
  full non-D-finiteness conditional on deg psi -> infinity. H=11 banked GF
  found anomalous (validated=False, shares no roots with Q9Q10) — needs
  re-recovery before any use. ACSV DONE
  (appendix of results/height-distribution-collapse.md): tall-flank rate
  function psi(alpha) = (1-3a)ln3 + Legendre(ln H); saddle reproduces exact
  T(36,36-k) to ~1-3% for k=3..14, breaks at the alpha->1/2 band edge as
  expected; experiments/flank_saddle.py. K1 DONE
  (results/allpairs-kernel.md): gap-walk reformulation exact (l<=8); constant
  rho = 14.40871398627036583814804007788... (37 digits), localized kappa-mode
  (kappa=0.42109, kernel relation verified), P-plateau confirmed; algebraic
  but no low-degree form (PSLQ excludes deg<=10, coeffs<=1e10; two spurious
  fits exposed); exact elimination documented, not executed (low value).
  H2 DONE (results/convex-anisotropic.md): convex strip GFs recovered
  exactly H<=7 (orders 1,3,7,14,25,36,53); finding = root RECYCLING (psi
  degrees 1,2,3,5,7,6,8), opposite of the full family's separation -- weak
  exclusion boxes only, Mirage unstrengthened, but sharpens that the H1
  mechanism is special to the unrestricted family. K3 (exact convex mu,
  q-series week-class) PARKED -- last open item of the program. Garnish when idle: Sheffer/Riordan convolution identities for
  P_k as new cross-checks; p=2 spine considered-and-declined (3-powers are
  units mod 2, no collapse).

- **UNIVERSALITY (2026-07-15): the diagonal law holds on the hex lattice**
  (results/hex-diagonal-law.md, experiments/hex_gas.py): T_hex(n,n-k) =
  P_k(n)*2^(n-1-3k), P_1 = 9n-15 (11 holdouts), same onset; single-row
  weights (s+1)^2, gap pairs impossible; **dyadic spine = the SAME cubic
  H^3 = H^2 + u over F_2** with G = 1 + uH^-3. Lattice picks the prime
  (drift count) and density (contacts^2); the curve is invariant. **UNIVERSAL THEOREM
  PROVED 2026-07-15** (docs/proofs/universal-diagonal-law.md): for every
  row-local lattice (|dy|<=1 adjacency, drift count b = |D|), T(H+k,H) =
  q_k(H) b^H from H >= k+1 with integer-valued P_k (Theorem A), and mod any
  prime p | b the spine is H^3 = H^2 + wu with w = W_pair mod p (Theorem B:
  the curve is lattice-invariant; the lattice picks the prime and scaling).
  Instances machine-checked: square b=1 (poly diagonals, density 4,
  experiments/universal_law_check.py), hex b=2, king b=3 -- all with w=1.
  Open: is w always a unit (or ever 0)? polyiamonds (needs row conventions).
  Paper's not-D-finite theorem landed (thm:notdfinite, verify_claims 407/407).

- **Lessons-learned DRAFTED 2026-07-15** (docs/lessons-learned.md): six failure
  classes, verification war stories, bug bestiary, process/ops/collaboration
  lessons; sections marked [JP] are jasonp's to write.
- **EVERYTHING ELSE BLOCKED OR COMPLETE (2026-07-15).** Blocked on time/boxes:
  a(22) (~07-16; then gather+bank, frontier->22), H=11 GF re-recovery, a(37)
  decision. Blocked on jasonp: viva -> OEIS batch + 3 comment drafts,
  [JP] lessons sections, Northcott literature check (papers/MISSING.md),
  paper scoping sign-off. Blocked on hard math (obstructions documented):
  onset sharpness (king+dm), dm Lemma-5 hardening + multiplicity split,
  max-hole peeling, SNF exponents, K3 exact convex mu, periodic-lattice
  formalization.

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
