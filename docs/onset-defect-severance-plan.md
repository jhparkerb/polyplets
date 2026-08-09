# Severance: freeing the middle-band formulas from the sweep

> **CAMPAIGN COMPLETE, 2026-08-09, same day.** W1: P_k ab initio k ≤ 9
> (results/severance-w1-anchor-cut.md; k=10 = memory wall). W2: Φ derived
> by kernel method, scale 1 (experiments/severance_w2_kernel.py). W3:
> depths 2–4 closed exactly (results/onset-defect-depths234.md; family
> class corrected to excess ≤ j−1). W4: surplus-4 Lean enumeration
> measured infeasible (docs/severance-w4-scoping.md); the two feasible
> slices landed — GapWalk.lean (walk table + l ≤ 6 weights, decide, no
> native_decide axiom) and DepthAssembly.lean (identities (C)/(D),
> 36 theorems D_j(k) j ≤ 4, k ≤ 8). All gates re-run by the manager.
> Net: rows n ≤ 24 two-source end-to-end; rows 25–33 formula-covered
> except the 2-anchor-cells-per-level, k = 10..18; rows 34–40 out of
> reach. Nothing committed or pushed.

2026-08-09. Plan authored in-session (Fable); agents execute, they do not
design. Campaign name for commits and task labels: **Severance** — cutting the
formulas that cover the middle band loose from the engine code that produced
the T(n,H) numbers they were derived from.

## 1. The circularity being severed

The certification story for the middle band (results/onset-defect-depth1-closed.md,
docs/onset-defect-handoff.md) currently rests on two engine-sourced residues:

1. **The P_k anchors.** Each diagonal polynomial P_k is pinned from two swept
   cells per level (k ≤ 18, Lean grand form supplies the shape). Those 2×18
   integers come from the production sweep — the code under test.
2. **Φ is fitted, not derived.** The depth-1 algebraic minimal polynomial
   passed 144 orders of holdout, but its coefficients were solved from series
   data, and that series was validated against banked cells.

The gap-walk families themselves are independent enumerations. Close these two
residues and the formulas owe the sweep nothing; then rows n ≤ 33 of T(n,·)
(and hence a(33)) become verifiable end-to-end from proof + strip engine +
gap walk, three sources sharing no code.

## 2. Ground rules

- **Fable manages, Opus executes, every task sits behind a fail-closed gate**
  (Opus trust rule of 2026-08-07: Opus only where a wrong answer cannot pass).
  A gate is a shipped script in `experiments/` (or `lake build` for Lean) that
  exits non-zero on any mismatch. No judgment calls delegated.
- Opus runs at **effort=low**. Every deliverable is machine-checked; the agent
  is a typist for algebra and code, not a referee.
- Fable writes each brief in-session, reads **gate output only**, never agent
  transcripts. Verdicts are "gate green" / "gate red", nothing softer.
- Sonnet is deliberately not used: the gates make Opus safe, and Sonnet
  re-failing symbolic algebra costs more than Opus passing once.
- Compute jobs follow docs/job-checklist.md; anything possibly >5 min runs in
  tmux; nothing >1 hr without explicit agreement (frontier rules).
- Numbers cited in any resulting write-up must be printed by a shipped script
  (standing instruction, docs/onset-defect-handoff.md §5).

## 3. Workstreams

### W1 — anchor-cut: ab-initio cluster weights to k ≈ 9–10

**Goal.** Derive P_k from cluster weights alone, removing the swept anchor
cells for as many levels as compute honestly allows.

**Brief (Opus).** Port the full-tier cluster-weight DP
(`experiments/cluster_weight_dp.py` is the spec; `results/defect-gas.md`
records the pathologies to avoid — solve μ order-by-order, never mix the
u-series H with the y-series chain μ) to C++ in the repo build tree. Push
levels upward from the current reach.

**Gate** (new script `experiments/severance_w1_gate.py`, RED-first):
1. C++ output must reproduce the Lean-pinned weights j ≤ 3 exactly
   (Weights.lean / Weights3.lean values).
2. Must reproduce every value in `cluster_weight_dp.py::KNOWN_WEIGHTS`.
3. P_k assembled from the weights must equal the wired `diagCoeffTable`
   (orchestrator/sweep.go) coefficient-for-coefficient at every level
   reached. Agreement is the severance; disagreement is a bug either way.

**Price.** Measured Python cost ≈20×/level (k=4: 3.1 s, k=5: 65 s, k=6
killed >530 s — defect-gas.md:242). C++ ~100× buys k ≈ 9–10. k=8 is
minutes, k=9 ~1 hr (ask before launching), k=10 is a beg-and-agree.
**Do not** pitch k ≥ 11; the route to P_17 is priced out and stays out.

**Deliverable.** Anchors severed for k ≤ K₁ (target 9); note in
results/ recording exactly which levels are ab initio vs still anchored.

### W2 — kernel-cut: derive Φ from the two-class gap walk

**Goal.** Turn the fitted quartic Φ(x,W) into a theorem via the kernel method
on the walk's functional equation, removing the fitted-not-derived caveat.

**Brief (Opus).** From `experiments/depth1_gap_walk.py::transitions` (the
two-class walk: state (gap g, class J/P), bulk kernel (1,2,3,2,1)), write the
functional equation for the walk generating function, then eliminate the
catalytic variable (kernel method / resultants — mechanical symbolic algebra,
sympy or pari). The localized eigenvalue ρ ≈ 14.41 must cancel via the
rank-one residue identity already verified numerically; its survival in any
candidate is an instant fail.

**Gate** (new script `experiments/severance_w2_gate.py`):
candidate minimal polynomial must match the fitted Φ (PHI_COEFFS in
`experiments/depth1_recurrence.py`) coefficient-for-coefficient, and
annihilate the series through order 200. Exact match or discard — no
"close" results accepted, no partial credit.

**Price.** Desk work; agent-hours, zero machine time. May take several
attempts; each attempt is cheap and the gate is absolute.

**Deliverable.** Derivation written into
results/onset-defect-depth1-closed.md §3 (status flipped from fitted to
derived), or a documented dead end with the specific obstruction.

### W3 — depth-cut: close depths j = 2, 3, 4

**Goal.** Extend the depth-1 closure down three more lines, which is exactly
what row-33 coverage needs (deepest depth at the H=15 seam of row 33 is 4).

**Brief (Opus).** Per §6 of results/onset-defect-depth1-closed.md: depth j
admits stacks that are all-2 except j−1 rows of 3; enumerate the new weight
families (j=2 first: single-3-row stacks), extend the gap-walk identity, and
compute D_j(k) exactly.

**Gate.** Extended identity must reproduce every banked below-onset cell at
that depth exactly (the banked triangle via `slope2_law_vs_truth.py::read_tri`
— note the data-format warnings in the handoff §3). Additionally: recovered
asymptotics must match the measured θ_j = j−3/2 and the amplitude family
(supported j ≤ 4, onset-defect-law.md §2) — a free consistency check, not
the gate.

**Sequencing.** Starts only after W2 lands or dead-ends, since it reuses the
kernel machinery and a derived Φ makes each depth cheaper.

**Deliverable.** results/onset-defect-depths234.md; depth-j identities with
the same evidence tier as depth 1.

### W4 — Lean-cut: formalize the severed chain

**Goal.** Push the human-checked pieces into Lean so the middle-band story
matches the right sub-triangle's evidence tier.

**Brief (Opus).** Fable authors the statement skeletons in-session (statements
are judgment; proofs are labor). Opus fills proofs. Scope, in order of value:
(1) W1's weight values at the new levels (extending Weights3Heavy.lean's
pattern), (2) the gap-walk identity, (3) W2's kernel derivation if it landed.

**Gate.** `lake build` green, with the statement files diffed against the
Fable-authored skeletons (agents must not weaken a statement to make it
provable — the diff check is the fail-closed part).

**Sequencing.** Last; queues behind whichever of W1–W3 produce material.

## 4. Waves and cost controls

- **Wave 1:** W1 + W2 in parallel (independent; one compute-flavoured, one
  desk-flavoured — they don't contend for cores).
- **Wave 2:** W3, then W4.
- Respect the 3-hour usage window when fanning out: launch W1 and W2 as the
  only wave-1 runners; nothing queues behind them until one finishes.
- All agent runs at effort=low. Escalate a single task to default effort only
  after two gate-red attempts, and note the escalation in the task log.
- Fable's context is reserved for briefs, gate design, and the final write-up.

## 5. Exit criteria

Severance is complete for row n when every cell T(n,H) is covered by at least
one of: strip engine (H ≤ 14, already done for all n ≤ 40), ab-initio P_k
(k = n−H ≤ K₁ from W1, or Lean-anchored shape with the anchor caveat stated),
below-onset depth formula (j = n−2H+1 ≤ 4 from W3). The write-up must state,
per row, which cells remain anchored to swept integers and which are fully
free — no blended claims.

Realistic landing: rows fully free through n ≈ 15 + K₁ with W1+W3 alone
(K₁ = 9 → row 24); rows n ≤ 33 free-modulo-anchors (2 cells per level,
k ≤ 18) with the anchor set explicitly listed. W2 and W4 upgrade the
evidence tier without changing the coverage map.
