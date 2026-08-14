# R1-A — base anatomy audit: the incumbent's per-n cost, measured

Filed 2026-08-13. Scout, desk-only, existing logs and banked records only.
Fit script + log: `experiments/rook1/rook1_R1-A_basefit.py`,
`experiments/rook1/rook1_R1-A_basefit.log` (pure stdlib; every constant in it
carries its source path; the cpu sums are awk-sums of the `cpu_s` column of the
named `cost_profile*.tsv`, re-derivation one-liner at the top of the log).

Headline: **b = 1.7266 = √2.9813** — the incumbent as operated is already at
rook parity on its own trajectory, and **K3's contingency fires** (§4). The
2.42 / 1.61 / 1.73 contradiction resolves as: 1.73 is the cost base, 1.61 is
the state (RAM) base, 2.42–2.5 is a pre-kink number wrongly promoted into a
kink-engine cost claim (§2).

## §1 The fit — what quantity, what window, what came out

**Quantity fitted: total cpu-seconds per end-to-end maxn=N production run**
(real sweeps + closed-form injection + combine), from banked
`cost_profile*.tsv` sums and PROVENANCE cpu lines. Not wall (machine- and
core-count-confounded), not states (a different quantity — that confusion is
the K1 contradiction, §2). All fits are least-squares on ln(cpu) vs n;
re-run: `python3 experiments/rook1/rook1_R1-A_basefit.py`.

### 1a. The chartered window n = 24..30 — the shipped engine has no curve there

| n | total cpu-s | top real H | engine | machine | source |
|---|---|---|---|---|---|
| 24 | not recorded | 16 | column | dalby | `results/ns_a24/RESULT.md` (wall 4870.3 s × 80c, H16 only; H1-15 reused from the perf-audit probe) |
| 25 | not recorded | 16 | column | ayr 30c | `results/ns_a25/RESULT.md` (wall 45841.5 s) |
| 26 | 259,913 | 15 | column | dalby | `results/ns_a26/cost_profile.tsv` |
| 27 | 848,671 (dalby part only) | 16 | column | dalby H16 + ayr H3-15 (ayr cpu not recorded) | `results/ns_a27/cost_profile_dalby.tsv` |
| 28 | 353,202 | 15 | column | ayr 32c | `results/ns_a28/PROVENANCE.md` |
| 29 | 1,960,647 | 16 | column | dalby | `results/ns_a29/PROVENANCE.md` |
| 30 | 79,445 | 17 | **kink** | dalby | `results/ns_a30/cost_profile_dalby.tsv` |

The window as chartered cannot be fitted for the shipped (kink) engine from
existing logs: **the kink kernel entered production at a(30)**
(`results/ns_a30/PROVENANCE.md`), so the window holds exactly one kink point.
n = 24..29 measure the retired whole-column engine, on two machines, with two
terms lacking cpu records entirely. A single-engine, single-machine fit inside
the window: column dalby a26→a29, ratio 7.543 over 3n ⇒ **1.961/n** (MEASURED,
two points, no residuals possible — that is the *old* engine's base on the
dH/dn = 1/3 trajectory those runs happened to take). The incumbent's window
curve is **NOT ESTABLISHED in-tree**; job request A1-JOB-1 (§5) exists to
create it, ~2 h of dalby, before any challenger is measured against gate 1.

### 1b. The shipped engine's own ladder, n = 30..40 (kink, dalby, one config family)

MEASURED, 9 points (a35, a36 excluded — two-machine splits, cross-ISA
cpu-seconds not commensurable): 79,445 / 161,215 / 176,298 / 192,745 /
210,666 / 580,223 / 1,783,598 / 2,070,672 / 5,318,465 cpu-s for
n = 30,31,32,33,34,37,38,39,40 (sources per row in the script).

Least-squares slope: **per-n ratio 1.4595**, residuals ±0.5 in ln (×0.56 to
×1.65) — the residuals are *structured*, not noise: every positive excursion is
a top-height-advance year, every negative drift a fence year. Adjacent measured
ratios (same machine, MEASURED):

| step | ratio | top real H |
|---|---|---|
| a30→a31 | 2.029 | 17→18 |
| a31→a32→a33→a34 | 1.094, 1.093, 1.093 | 18 (P13, P14, P15 wired — fence years) |
| a34→a37 | 1.402/n | 18→19 |
| a37→a38 | 3.074 | 19→20 |
| a38→a39 | 1.161 | 20 (P18 wired — fence year) |
| a39→a40 | 2.568 | 20→21 |

So the incumbent's per-n cost is **bimodal**: ×2.0–3.1 in a year the top real
height advances, ×1.09–1.16 in a year the P_k fence advances instead. The
1.4595 aggregate slope is a *transient* — the fence advanced 6 diagonals in 10
terms over this band (k 12→18), faster than the treadmill can sustain (§2,
1.73 entry). Do not register 1.4595 as anyone's base.

### 1c. The two components, measured separately

- **Cost per unit height** (the exponential): per-height cpu ratios at fixed n,
  kink dalby — H16/H15 = 1.96–2.13, H17/H16 = 2.26–2.43, H18/H17 = 2.60–2.73
  (a30..a34 profiles), and at the frontier **H21/H20 = 2.9813** = phase C /
  phase B = 3,329,644 / 1,116,858 (`results/ns_a40/PROVENANCE.md`). The ratio
  **rises with H** through the whole measured range; 2.9813 is the last and
  largest measured value. (PROVENANCE's "~2.7× per-column cost" is the same
  quantity from within-phase column profiles — consistent, slightly lower.)
- **Fixed-H per-n growth** (the polynomial): ×1.03–1.10 per n at H = 16,17,18
  (script §Fixed-H). This is the O*-suppressed factor; it is what fence years
  cost.

## §2 Reconciliation of the three in-repo base claims (queue row K1)

Starting from R1-K's pinning (`results/rook1/R1-K.md` §1d), verdict per claim:

| claim | asserts | verdict |
|---|---|---|
| `results/kink-carry.md:46` — per-n ~4.4 = states 2.42 × masks 1.8; post-kink "b ≈ 2.5" | per-n cost base of the kink engine | **WRONG as a kink cost claim.** 2.42 is the *pre-kink column engine's* state growth measured along the kink-carry benchmark diagonal (n/H ≈ 1.8, dH/dn ≈ 0.55). The post-kink "b ≈ 2.5" was an extrapolated assertion, never re-measured — and it is refuted twice by data that already existed: (i) kink-carry's own benchmark row (kink times 0.04/0.41/6.0/95 s at n = 15/18/22/26) gives 1.96–2.17/n on that same diagonal, not 2.5; (ii) the production ladder the kernel then ran (§1b) shows 1.09–3.07/n bimodal, aggregate ~1.46, on the treadmill trajectory. A state-growth number from one engine and one trajectory was promoted into a cost claim about another engine on another trajectory. |
| `results/kink-carry.md:69` — D_H ~ 2.6^H, H ≈ n/2 ⇒ per-n 1.61 | frontier **states** per height | **Correct law, different quantity.** It is the RAM-reach base (D_16 ≈ 2.1M states, MEASURED at a27), not the cost base: cpu per height (2.6→2.98, §1c) exceeds state growth per height because work per state and column count grow too. 1.61 is a per-n bound on *memory*, and a lower bound on cost. Nobody's per-n cost is 1.61. |
| `results/ns_a40/PROVENANCE.md:16,19` — phase C / phase B = 2.9813 per height; line 20's ~2.7 | production **cpu** per unit height at the frontier | **This is the cost measurement, and its per-n conversion is the engine's base.** Per-n requires dH_top/dn. As operated, top real height advanced 4 in 10 terms (17→21, §1b) — sustained by wiring one *fitted* P_k per new diagonal. The treadmill's self-consistent steady rate is dH/dn = 1/2: each new P_k needs 2 real fit cells at its diagonal, and each run's top sweep yields 1 (e.g. H21 at a40 is P_19's second fit point, `results/ns_a40/PROVENANCE.md` §Notes). Hence **b = 2.9813^(1/2) = 1.7266**. |

**Which is the engine's per-n cost base: b = 1.7266**, the square root of the
measured frontier per-height cpu ratio, on the treadmill trajectory the
pipeline actually runs. Two conditions attach, and both are load-bearing:

1. **The treadmill is fitted, not ab initio.** dH/dn = 1/2 holds only while a
   new P_k can be wired per 2 terms, and every wired P_k past k = 9 is a
   2-point fit to the engine's own output, holdout-validated but not
   independently derived (`results/ns_a40/PROVENANCE.md` §Reproduction note).
   Frozen fence (no new P_k) means dH/dn → 1 and the per-n base is the
   per-height ratio itself, **~2.98**. That is the honest spread: 1.73 with
   the treadmill, 2.98 without it. The goal's ab-initio requirement is
   exactly the demand that this 1.73 stop being conditional.
2. **The per-height ratio is still rising** at the last measured height
   (2.60 → 2.73 → 2.9813 across H18..H21, §1c). √2.9813 = 1.7266 < √3 =
   1.7321 by 0.3%; if the ratio crosses 3 at larger H, b crosses parity from
   below. Whether it converges (state growth 2.6^H × polynomial ⇒ limit ≈
   2.6, b → 1.61) or drifts past 3 is not decidable from existing logs — 
   successor row A2.

## §3 Proposed measured-clause threshold (clause 1 of docs/rook-parity-bar.md)

**Threshold: a challenger's fitted per-term cost ratio over n = 24..30 must be
strictly below 1.7266** (exactly: below √(3,329,644/1,116,858), the incumbent's
measured frontier base, anchor `results/ns_a40/PROVENANCE.md:16,19`).

Fit protocol, stated so it can be re-run identically on the challenger: total
cpu-seconds for each end-to-end maxn=N run, N = 24..30, all seven points, one
machine, one build; least-squares slope of ln(cpu) vs N; threshold applies to
e^slope; residuals reported per point. Cpu-seconds, never wall; end-to-end,
never per-height cherry-picks.

Registration notes, for the lead:

- 1.7266 is the *asymptotic measured* base, deliberately not the in-band 1.4595
  (transient fence catch-up, §1b) and not the old engine's 1.961 (§1a). It is
  also the challenger-*hardest* defensible reading below 2.98; registering the
  frozen-fence 2.98 would let a challenger "win" while losing to the pipeline
  as actually operated.
- **The clause now conflicts with the goal's pin, and that is a finding, not a
  drafting slip**: a method whose base is exactly √3 = 1.7321 — the goal's
  stated target — fits *above* 1.7266 and fails this clause. With b at parity,
  "strictly below the incumbent" is strictly stronger than "c ≤ √3".
  Whether the bar keeps the strict clause (demand: beat the incumbent) or
  relaxes the pin to it (demand: match √3) is jasonp's ruling to make — queue
  row A4. I propose the number; I do not resolve the conflict.
- The incumbent's own curve on the window should exist before any challenger
  is measured: job request A1-JOB-1 (§5) produces it for ~2 h of dalby and
  either confirms 1.7266 on-window or replaces it with the same protocol's
  measured value, today, before any challenger exists.

## §4 K3 — the contingency fired

Stated plainly, as chartered: **the shipped engine is already at rook parity
on its own operating trajectory.** b = 1.7266 < √3 = 1.7321. Every measured
reading of the ladder (aggregate 1.46; treadmill-sustained 1.73) is at or
below the pin; only the frozen-fence reading (2.98) is above it, and the
pipeline does not operate frozen. Consequences:

- **The goal's weight moves to gate 1's measured clause and to the ab-initio
  requirement.** What the incumbent lacks is not the base — it is that its
  base rests on fitted P_k. A challenger's value is *unconditional* parity.
- **b² = 2.9813, and the pre-registered threshold table partially collapses.**
  The brief's middle band "3 < g < b²" is **empty** (b² < 3), and the bands
  "g ≤ 3" (parity) and "g ≥ b²" (kill) overlap on [2.9813, 3]. The partition
  needs re-registering by the lead as: g < 2.9813 ⇒ route survives and is at
  parity iff g ≤ 3 — effectively **survive iff g < 2.9813** — before R1-B's
  verdict is cited in the bar file (queue row A3). Under either reading the
  outcome is unchanged in fact: R1-B's measured lower bound g ≥ 8.15
  (`results/rook1/R1-B.md` §2) exceeds every boundary in play; the tower
  route's kill is *a fortiori* under my b.

## §5 Job request A1-JOB-1 — incumbent calibration curve on the window

    job id:            A1-JOB-1
    measures:          total cpu-seconds per end-to-end kink run, maxn = 24..30,
                       dalby, one build, production fence policy (top real
                       height N-13, as scripts/dalby_term.sh's own policy
                       states in its header); the seven-point ln-fit slope per
                       §3's protocol
    decides:           whether the registered measured-clause threshold stays
                       1.7266 (anchor: a40 phases) or is replaced by the
                       on-window measured slope under the identical protocol.
                       Branch A: on-window slope within [1.60, 1.80] ->
                       threshold confirmed/replaced by it, same clause text.
                       Branch B: outside that band -> the window and the
                       frontier disagree; the bar must name which trajectory
                       it prices, and R1-A's §2 conditions get a measured
                       test instead of an argument.
    command:           for N in 24 25 26 27 28 29 30; do scripts/dalby_term.sh $N; done
                       (each run's cost_profile tsv is the artifact; exact
                       invocation and any fence-cap flag pinned by the lead at
                       dispatch after checking dalby_term.sh's PHASE_DIAG_CAP
                       against wired P_k at HEAD — the required shape is top
                       real height = N-13 at every N, verified in the log)
    script:            scripts/dalby_term.sh (exists, production driver);
                       fit afterwards via experiments/rook1/rook1_R1-A_basefit.py
                       pattern on the new tsvs
    wall estimate:     ~2 h total on 80 cores: MEASURED anchor a30 = 3711 s
                       wall (results/ns_a30/PROVENANCE.md), EXTRAPOLATED down
                       6 terms at measured ~1/2 per term, summed geometric
                       ~2x the a30 point
    RAM estimate:      < 8 GB peak (kink rss_max ~76 MB at a30, ~6.4 GB at
                       a34 H18 peak; MEASURED, results/ns_a3{0,4}/PROVENANCE.md)
    disk estimate:     small; kink runs are RAM-resident at these heights,
                       artifacts are tsv + perheight files, < 1 GB
    cores:             80 (dalby), per-worker RAM per the budget rule
    interruptible:     yes; dalby_term.sh N --resume, checkpoint at height
                       boundaries (header, gated by overlap_resume_test.go)
    RED control:       every run's a(N) must byte-match the banked value
                       (fixtures/b006770.txt for N <= 20 chain, banked
                       results/ns_aN otherwise) — dalby_term.sh's own validate
                       block enforces this and fails closed on a gap
    closes:            §1a NOT ESTABLISHED (the incumbent's on-window curve)

## §6 Successor queue rows filed

A1 (JOB-REQUESTED, the calibration job above), A2 (per-height-ratio
convergence — does R(H) cross 3), A3 (re-register the collapsed threshold
partition), A4 (goal-pin vs measured-clause conflict, jasonp ruling) — all in
`results/rook1/queue.md`, formats per its head. A2–A4 are different in kind
from the closed question (a measurement trend, a registration defect, a
charter conflict — not window tweaks).
