# r4-spinproj — INV-8 at m=18..21, priced on tonight's measurement

Round 4 scout, 2026-08-13. Governed by `docs/triangle-round4.md`. I ran no
compute; every number below is read off logs already on disk, or derived from
them by arithmetic shown in full.

**Verdict in one line: m=18..21 costs 2.61 thread-hours and 7.12 GiB on one
core, it fits with a factor of 17 in hand on the smaller box, and the cost
question is closed — what is left is that H=17..21 has no B1 oracle at all, so
the run's correctness evidence is 41 nontrivial cells checked against the very
production sweep it exists to confirm, plus a fail-closed guard set.**

---

## 0. The measured record, verbatim

Source: dalby, read-only ssh.
`~/src/pm-b1-perf/experiments/tristruct/r4_spin_m16.log`,
`~/src/pm-b1-perf/results/r4/spin_m16.txt.metrics`,
`~/src/pm-b1-perf/experiments/tristruct/r4_spin_gates.log`.

Run: `build/r4_spin_engine --m 1..16 --cols 41 --nmax 40 --mod 4 --dense-rank
--oracle .../cutcount_b1/rows --out results/r4/spin_m16.txt --report-rss`,
single thread, `mutant=none`, `inject=no`.
Result: `compared=640 mismatch=0 compared_hlen=520 mismatch_hlen=0
structural_checks=1280 structural_failures=0`, `wall_s=88.6 cpu_s=88.5
peak_rss_mb=90.7`, sha256 `578c940c…c5a626`. **All MEASURED.**

| m | states | transitions | wall_s | peak_rss_mb | ns/transition | bytes/state |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 7 | 283 | 0.000031 | 2.61 | 108.41 | — |
| 2 | 17 | 1,850 | 0.000093 | 2.61 | 50.31 | — |
| 3 | 41 | 7,027 | 0.000321 | 2.61 | 45.61 | — |
| 4 | 99 | 23,268 | 0.001516 | 2.61 | 65.17 | — |
| 5 | 239 | 71,327 | 0.003060 | 2.61 | 42.90 | — |
| 6 | 577 | 208,806 | 0.008478 | 2.61 | 40.60 | — |
| 7 | 1,393 | 592,463 | 0.021186 | 2.61 | 35.76 | — |
| 8 | 3,363 | 1,643,656 | 0.048418 | 2.61 | 29.46 | — |
| 9 | 8,119 | 4,483,139 | 0.132128 | 2.61 | 29.47 | — |
| 10 | 19,601 | 12,066,578 | 0.364574 | 3.23 | 30.21 | 173.03 |
| 11 | 47,321 | 32,132,939 | 0.448719 | 3.86 | **13.9645** | 85.52 |
| 12 | 114,243 | 84,822,380 | 1.183978 | 5.07 | **13.9583** | 46.50 |
| 13 | 275,807 | 222,274,183 | 3.109166 | 9.07 | **13.9880** | 34.48 |
| 14 | 665,857 | 578,853,630 | 8.143911 | 17.59 | **14.0690** | 27.69 |
| 15 | 1,607,521 | 1,499,443,687 | 20.950115 | 38.68 | **13.9719** | 25.23 |
| 16 | 3,880,899 | 3,866,148,368 | 54.012634 | 90.69 | **13.9707** | 24.50 |

`wall_s` is per-m, not cumulative: the sixteen values sum to 88.36 s against a
total of 88.6 s, and the running `elapsed_s` heartbeats track the partial sums.

The break at m=10→11 is the `--verify-rank` auto default, which is on for m ≤ 10
and off above (`r4_spin_engine.cpp:678`). **m=11..16 is the production regime**
and is the only part of the table that should be extrapolated from.

`ns_per_slot_op` is also emitted (0.3407 at m=16) and is not quoted here except
to note it is a units artifact: the cost model's "slot-op" charges 41 operations
per transition and this kernel does two (`r4-spinbuild.md` §1.4).

---

## 1. The projection

### 1.1 States — EXACT, not fitted

`states(m) = 7, 17, 41, 99, 239, 577, 1393, 3363, 8119, 19601, 47321, 114243,
275807, 665857, 1607521, 3880899` satisfies `s(m) = 2·s(m−1) + s(m−2)` at
**fourteen out of fourteen** consecutive checks with **zero residual** — these
are integers and the recurrence reproduces each one exactly, e.g.
`2×1,607,521 + 665,857 = 3,880,899`.

This is the companion Pell sequence `t_{m+1}` (`triangle-r3-spin.md` §1), which
the engine's dense index space is by construction: it ranks over
`L_{m+1} = {s ∈ {E,A,B}^{m+1} : no adjacent clash}`, `|L_{m+1}| = t_{m+1}`
(`r4-spinbuild.md` §1.3). The measurement therefore **confirms a count that was
already derived and brute-force verified independently** (`r3_spin_counts.py`,
all 3^m strings at m ≤ 12), rather than supplying a fit. Ratio → 1+√2 =
2.41421356.

| m | states | basis |
|---:|---:|---|
| 17 | 9,369,319 | **MEASURED-EQUIVALENT** — closed form, 15 confirmations |
| 18 | 22,619,537 | same |
| 19 | 54,608,393 | same |
| 20 | 131,836,323 | same |
| 21 | 318,281,039 | same |

These are `t_18 … t_22` and match `triangle-r3-spin.md` §1's banked table
digit for digit.

### 1.2 Transitions — an exact linear law, residual < 0.001%

Transitions per state, m=11..16:

| m | transitions/state | Δ from previous |
|---:|---:|---:|
| 11 | 679.042 | — |
| 12 | 742.473 | 63.431 |
| 13 | 805.905 | 63.432 |
| 14 | 869.336 | 63.431 |
| 15 | 932.768 | 63.432 |
| 16 | 996.199 | 63.431 |

**Five consecutive second-differences, all 63.431 to five significant figures.**
This is not a growth ratio fitted to noisy data; it is an arithmetic identity of
the sweep structure showing through (41 columns × m stages × a live-branch
fraction converging to 63.4314/41 = 1.54711). Taking the law from the m=16
anchor:

    transitions(m) = states(m) × (63.4314·m − 18.703)

Residuals against all six measured points: **≤ 0.001% at every point** (679.042
predicted 679.042; 742.473 → 742.474; 805.905 → 805.905; 869.336 → 869.337;
932.768 → 932.768; 996.199 → 996.199).

| m | c(m) = 63.4314m − 18.703 | transitions | basis |
|---:|---:|---:|---|
| 17 | 1,059.63 | 9.9280e9 | EXTRAPOLATED, 1 step |
| 18 | 1,123.06 | 2.5403e10 | EXTRAPOLATED, 2 steps |
| 19 | 1,186.49 | 6.4793e10 | EXTRAPOLATED, 3 steps |
| 20 | 1,249.93 | 1.64785e11 | EXTRAPOLATED, 4 steps |
| 21 | 1,313.36 | 4.18016e11 | EXTRAPOLATED, 5 steps |

The extrapolation is a straight line five steps past six collinear points. The
independent bound: writing `c(m) = 41·m·b(m)`, `b` is monotone increasing with
decaying increments (1.5055, 1.5091, 1.5120, 1.5145, 1.5167, 1.5186) and is
bounded above by 3 trivially and by ~1.53 by continuation, which brackets
transitions(21) in [4.162e11, 4.192e11] — **under 1% either way.** Transitions
are effectively pinned.

### 1.3 Wall — the one genuinely extrapolated quantity

`ns_per_transition` is **flat at 13.97 ± 0.05 over m=11..16**: 13.9645, 13.9583,
13.9880, 14.0690, 13.9719, 13.9707. Spread 0.79%, no trend.

What that flatness spans is the point. At m=11 each buffer is
47,321 × 12 B = 568 KB and the pair fits in L2. At m=16 each buffer is
46.6 MB and the pair is 93 MB, far past any L3 on this box. **The per-transition
cost is unchanged across a 164x growth of the working set, from cache-resident
to deep DRAM, to within 0.8%.** This kernel is not memory-latency-bound — which
directly refutes `r4-spinbuild.md` §4.2's stated worry that write locality
"is what will set the constant". Measured: it does not.

Projected at 13.9707 ns/transition (the m=16 value):

| m | wall_s | wall | basis |
|---:|---:|---|---|
| 17 | 138.7 | 2.3 min | EXTRAPOLATED |
| 18 | 354.9 | 5.9 min | EXTRAPOLATED |
| 19 | 905.2 | 15.1 min | EXTRAPOLATED |
| 20 | 2,302.2 | 38.4 min | EXTRAPOLATED |
| 21 | 5,840.0 | 1.622 h | EXTRAPOLATED |
| **18..21** | **9,402.2** | **2.612 thread-hours** | |
| **17..21** | **9,540.9** | **2.650 thread-hours** | |
| **1..21** | **9,629.5** | **2.675 thread-hours** | |

**Where the fit is interpolation and where it is extrapolation.** States: neither
— closed form, confirmed at 15 points. Transitions: extrapolation of a line five
steps past six collinear points, self-bounded to ±1%. Wall: the only real
extrapolation, and it is of a *constant*, not a trend — the claim is that
13.97 ns/transition survives a further 82x of working set (93 MB → 7.6 GB). The
mechanism supporting that is the 164x of working set it has already survived
unchanged. **The honest risk is TLB and page-walk pressure at 7.6 GB with 4 KB
pages, which is the one effect that grows past where the data reaches.**

Degradation bracket, all EXTRAPOLATED:

| ns/transition | m=18..21 wall | comment |
|---:|---:|---|
| 13.97 | 2.61 h | measured constant holds — the central case |
| 20 | 3.74 h | 43% degradation |
| 28 | 5.23 h | 2x, roughly the verify-rank-on regime's cost |
| 42 | 7.84 h | 3x |
| 70 | 13.1 h | 5x; still inside `r4-adv-cost.md` §2's upper bracket |

**Nothing in this table changes the go/no-go.**

### 1.4 RAM — from this kernel's own bytes/state

`bytes_per_state` is emitted per m and converges from above: 46.50 (m=12),
34.48, 27.69, 25.23, **24.50 (m=16)**. It is a total-RSS figure, so it carries
the 2.61 MB process baseline; removing it gives
`(90.691406 − 2.609375) MiB / 3,880,899 = 23.80 B/state` at m=16, converging on
the design's 24 B (two 12-byte buffers, `r4-spinbuild.md` §1.3). I project at
**24.0 B/state**, the higher of measured-asymptote and design.

The buffers are released between m values and m increases monotonically, so each
row's peak is that m's own — **confirmed by measurement**: if earlier m's were
retained, bytes/state would not be falling toward 24.

| m | peak RSS | vs ayr 78 GiB | vs dalby 126 GiB | basis |
|---:|---:|---:|---:|---|
| 17 | 217 MiB | 0.27% | 0.17% | EXTRAPOLATED from 23.80 B/state MEASURED |
| 18 | 520 MiB | 0.65% | 0.40% | same |
| 19 | 1.22 GiB | 1.6% | 0.97% | same |
| 20 | 2.95 GiB | 3.8% | 2.3% | same |
| 21 | **7.12 GiB** | **9.1%** | **5.6%** | same |

Sequential in one process, the whole m=1..21 run peaks at m=21's 7.12 GiB. Four
concurrent processes for m=18..21 would peak at 11.8 GiB combined (15.1% of ayr,
9.4% of dalby) and finish in max-wall 1.62 h.

Even at a pessimistic flat 40 B/state — 67% above anything measured — m=21 is
11.9 GiB, still 15% of ayr.

### 1.5 The repricing, decomposed

| source | m=18..21 | vs measured |
|---|---:|---:|
| `triangle-r3-spin.md` §4 (filed) | 22.6 thread-days = 542.4 h | **208x over** |
| `r4-adv-cost.md` §2 bracket | 6.6 – 33 h | 2.5x – 13x over |
| **this projection** | **2.61 h** | — |

The 208x decomposes exactly: **117x** on the constant (the model's 41 slot-ops ×
40 ns = 1,640 ns/transition against 13.97 measured) and **1.78x** on the op count
(the model's `123·m·W(m)` charges all three branches over the W-census; the
engine iterates `t_{m+1}` and counts only surviving transitions). 117 × 1.78 =
208. The m=1..16 sweep's own 207x overprice against the same model is the same
two factors, which is why the numbers agree.

`r4-adv-cost.md` §2 caught the units error and was still 2.5–13x pessimistic,
because it re-priced against the model's transition count rather than the
kernel's. That is a note about how far a corrected model still misses, not a
criticism of the correction — the direction it gave was right.

---

## 2. Go / no-go

**GO. It fits trivially, and saying otherwise would be dressing up a cheap route
as a marginal one.**

- **Wall**: 2.675 thread-hours for the *whole* of m=1..21, single thread. The
  extra m=1..16 regression costs 88.6 s, 0.9% of the run — take it.
- **RAM**: 7.12 GiB peak, 5.6% of dalby, 9.1% of ayr.
- **Cores**: 1. No threading needed, so GATE 5's unvalidated atomic-deposit path
  need never be exercised in production.
- **Disk**: output ~840 A-rows + 840 T-rows ≈ 60 KB, plus a `.metrics` file.
  Nothing.

**The single number that decides it: there isn't one, and that is the finding.**
Both axes clear by more than an order of magnitude and the third (cores) is 1.
The route is not cost-constrained at any m in range; if it were pushed, the
binding wall is `kMaxStates = 2^34`, which m=21's 2^28.25 clears by 54x, and the
first m that would actually strain dalby's RAM is **m=26** (t_27 = 1.05e10
states × 24 B = 235 GiB). The decision this projection was supposed to inform
has moved: it is no longer about cost, it is entirely about §3.

**Recommended shape**: one process, `--m 1..21 --threads 1`, on dalby (same box
as the measurement, so the 640-cell H≤16 block is byte-comparable against
`spin_m16.txt`), and the identical command on ayr in parallel for a cross-ISA
`cmp`. 2.7 h each. See §6.

---

## 3. The gate battery, and what m=17..21 is actually validated by

This is the part the dispatch asked me to be honest about, and the honest answer
is worse than it looks in one respect and better in another.

### 3.1 There is no oracle above H=16. None.

`ls ~/src/polyominoes/results/cutcount_b1/rows/` on dalby:
`C1.out … C16.out`. Sixteen files. **MEASURED.**

So a `--m 17..21` run compares **zero** cells at the heights it exists to
compute. The 640-cell `compared=640 mismatch=0` line that a `--m 1..21` run
would still print covers H=1..16 only, and it exercises no code path unique to
m > 16. It is a build-and-environment regression, and calling it more than that
would be false.

The round-4 brief has B1 H=17..19 as the next rung. **If that lands, it gives
three consecutive fresh oracle heights immediately below the target** — the
single most valuable dependency this route has. It still would not oracle H=20
or H=21.

### 3.2 Above m=16 the engine runs with strictly fewer self-checks

- `--verify-rank` auto-default is **off** above m=10 (`r4_spin_engine.cpp:678`).
  This is the check that cross-validates every incrementally computed
  destination rank against a from-scratch rank — i.e. the O(1) rank arithmetic
  of `r4-spinbuild.md` §1.2, whose `h[][][]` tables grow with m, and which is
  the single most m-dependent piece of the kernel.
- `verify_language` runs when `len <= 17 || verify_rank == 1`
  (`r4_spin_engine.cpp:662`), i.e. **off above m=16** unless forced.

So the production run, as the gate sequence currently stands, would turn off the
two checks that most directly guard the code that changes with m, at exactly the
m values that have never executed. That is backwards, and it is cheap to fix.

**The verify-rank tax is affordable.** m=9,10 (verify on) measure 29.47 and
30.21 ns/transition against 13.97 with it off — a step of ~2.1x that coincides
exactly with the flag's default boundary. Attributing the whole step to
verify-rank is **inference, not measurement** (small-m effects are confounded),
and settling it costs under ten seconds: run m=13 with `--verify-rank 1` and
compare against the banked 3.109 s. If the tax is 2.1x, forcing verification on
for the *entire* m=1..21 run costs **5.6 thread-hours instead of 2.7** — which
at this scale is not a tradeoff. **Recommendation: force `--verify-rank 1`
throughout the production run**, contingent on the ten-second measurement.

### 3.3 What remains live at all m

Genuinely structural, no oracle required, all fail-closed
(`r4-spinbuild.md` §2): `dst >= rk.total` on every computed destination rank
(exit 78); the carry invariant "stage 0 of a column can only be live with
u[0]=E" (exit 78); `Ranker::build`'s runtime table-overflow guard (exit 78);
`kMaxStates = 2^34` (exit 78); `std::vector::assign` throwing rather than
truncating. Plus the in-run w-stability and parity bookkeeping checks — which
round 3 **measured** to be blind to stencil errors and which therefore gate
arithmetic, never correctness.

### 3.4 The evidence that is actually worth something — and it was overlooked

The B1 oracle is not the only comparison available at H=20 and H=21. The banked
triangle has them:

    results/ns_a40/perheight/h20.out   T(n,20) for n=1..40
    results/ns_a40/perheight/h21.out   T(n,21) for n=1..40

and `triangle.py:_provenance` returns **`real-sweep` for all 3 ≤ H ≤ 21**, so
every one of those 80 cells is production-sweep output, not a closed form.
Nonzero from n=20 (H=20) and n=21 (H=21): **41 nontrivial cells, 39 of them
below the frontier.** MEASURED (files read; `h20.out` line 20 is 1,162,261,467 =
3^19, parity 1).

Two things follow, and the second is the one I did not expect to find.

1. **The run yields 41 nontrivial agreement tests at the two target heights, not
   two.** Against an engine bug that corrupts cells unpredictably, 39
   sub-frontier cells at exactly the heights in question is real coverage. A
   bug that corrupts n=40 while leaving n=20..39 intact is a narrow failure mode
   and would be a spectacular finding in itself.

2. **Comparing against T bypasses the common-mode that the B1 gate structurally
   could not see.** `r4-spinbuild.md` §3(j): the engine computes
   `N_H = A_H − 2A_{H−1} + A_{H−2}` and the B1 oracle supplies `C_H` from which
   the engine takes *the same second difference* — "a misconception in the extent
   accounting hits both sides identically, and the oracle cannot detect it." The
   banked triangle supplies `T(n,H)` **directly**, per height, with no second
   difference taken by us. The extent-accounting layer that the 640-cell gate is
   blind to is therefore testable — and testable **right now, at zero compute**,
   because `spin_m16.txt` already contains 640 `T H=… n=… par=…` rows. See
   R4-SPINPROJ-1.

This is not independence. The banked triangle is the thing INV-8 exists to
confirm, and 39 of the 41 cells are checks of the engine against the claim, not
of the claim against the engine. But that is exactly the right ordering: **you
validate the new engine on the cells you already know, then read the two you
don't.**

### 3.5 The battery, in order

| # | check | cost | what a failure means |
|---|---|---|---|
| P0 | Compare existing `spin_m16.txt` 640 T-rows against `h1..h16.out` | seconds, no compute job | closes §3(j) common-mode retroactively for H≤16; a mismatch is a bug certificate against B1 or the sweep |
| P1 | `--m 13 --verify-rank 1`, compare wall against banked 3.109 s | < 10 s | fixes the tax figure so P3's flag choice is measured |
| P2 | `--m 1..18 --verify-rank 1` short run, watch for exit 77/78 | ~13 min at 2.1x | first execution of any m>16 path, with the rank check on |
| P3 | **production** `--m 1..21 --threads 1 --verify-rank 1`, dalby AND ayr | 5.6 h each, parallel | the run |
| P4 | `cmp` the two output files; both against the binary's own sha256 | seconds | cross-ISA byte identity kills miscompile/UB classes; **not** a check of the mathematics |
| P5 | Compare all 840 T-rows against the banked triangle: 640 at H≤16, 120 at H=17..19, 80 at H=20..21 | seconds | the verdict |

P4 is the cheapest independence evidence available and the output file was
deliberately designed for it (`r4-spinbuild.md` §5.10). It should not be
optional at these heights.

---

## 4. What the two bits are worth

`experiments/tristruct/r3_spin_pipeline.log` §6, MEASURED:

    banked T(40,20) mod 2 = 1 (provenance real-sweep)
    banked T(40,21) mod 2 = 1 (provenance real-sweep)

**Stated flatly: as two bits, this is weak evidence.** A wrong engine that
corrupts both target bits independently at random passes with probability 1/4.
Two bits of agreement is two bits. Anyone presenting "we confirmed both cells"
as though it were a strong test is overclaiming, and a referee is entitled to
say so.

**The route's actual value is the 41 cells, not the 2.** Agreement across 39
nontrivial sub-frontier cells at H=20 and H=21, plus the 640 at H≤16, is what
makes the two frontier bits credible; without them the frontier bits are a coin
flip that landed the right way. The deliverable is therefore *"the H=20 and H=21
rows of the parity triangle, reproduced by a rule class that never decides
connectivity"* — with the two n=40 cells as the two members of that row nobody
had a second source for.

**The prior.** My honest number, ASSERTED as a judgement:

- P(all 41 cells agree) ≈ 0.85–0.9. The mass of the residual is not "the
  production sweep is wrong at H=20/21" — it is "the engine's never-executed
  m>16 paths produce something detectably wrong", which the 39 sub-frontier
  cells catch and which is a *good* outcome because it is localized.
- P(the two frontier bits disagree while all 39 sub-frontier cells agree) —
  the scenario that would overturn part of a(40) — I put well under 0.02. This
  is a confirmation route and it should look like one.
- Cells covered: H=20 is 4.16% of a(40) and H=21 is 2.84%, **7.00% together**
  (per the round-4 dispatch), at the two heights where the partition ladder is
  priced out — 68.1 GiB sole-tenant at H=20 and 215.8 GiB at H=21 per ADV-4.

**What a referee gets.** Not "two bits confirmed". This: *7.00% of a(40), at the
two heights no other route reaches, has its parity reproduced end-to-end by an
independent rule class that never decides connectivity, on two ISAs, with 39
below-frontier cells at the same heights and 640 cells below H=17 reproduced in
the same binary and the same run.* That is a real sentence, and it costs 5.6
core-hours on each of two machines. The thing that would make it a much stronger
sentence — B1 rows at H=17, 18, 19 — is already the round's next rung, and this
run should be scheduled so its output can be re-compared when they land.

**Disagreement would be enormous** and the pattern localizes it immediately:
mismatch across all n ≥ 20 points at the engine; mismatch at scattered n points
at a rank/carry fault; mismatch at n=40 alone points at the frontier cell of the
production sweep and is the highest-value outcome the round could produce.

---

## 5. Job request

    job id:            R4-SPINPROJ-JOB-1
    measures:          T(n,20) and T(n,21) mod 2 for all n <= 40, plus
                       T(n,H) mod 2 for H=1..19, from the spin-basis parity
                       engine; and this kernel's ns_per_transition and
                       bytes_per_state at m=17..21, which retire the
                       extrapolation in section 1.3.
    decides:           whether T(40,20) mod 2 = 1 and T(40,21) mod 2 = 1 are
                       confirmed by a second rule class.
                       Branch A, all 41 nontrivial H=20/21 cells agree and the
                       640 H<=16 cells agree: 7.00% of a(40) gains a second
                       source at the two heights no other route reaches; the
                       INV-8 row closes GREEN.
                       Branch B, sub-frontier cells disagree: bug certificate
                       against the engine's m>16 paths, localized by the (H,n)
                       pattern; INV-8 reopens at the rank/carry layer.
                       Branch C, the two n=40 cells disagree while n<=39 agree:
                       escalate immediately; this is a challenge to the
                       production sweep at the frontier.
    command:           build/r4_spin_engine --m 1..21 --cols 41 --nmax 40 \
                         --mod 4 --dense-rank --threads 1 --verify-rank 1 \
                         --oracle <repo>/results/cutcount_b1/rows \
                         --out results/r4/spin_m21.txt --report-rss
                       Run the identical command on dalby and on ayr, then
                       cmp the two results/r4/spin_m21.txt files.
    script:            experiments/tristruct/r4_spin_engine.cpp (built;
                       dalby binary sha256 f77099038908fa80…e49c902)
    wall estimate:     2.675 thread-hours with --verify-rank 0;
                       5.6 thread-hours with --verify-rank 1.
                       Basis: MEASURED ns_per_transition = 13.9707 flat over
                       m=11..16 on dalby (spread 0.79% across a 164x growth of
                       working set), times an EXTRAPOLATED transition count
                       from a linear law with residual < 0.001% at six points.
                       The verify-rank multiplier 2.1x is EXTRAPOLATED from the
                       m=9,10 vs m=11+ step and must be settled by
                       R4-SPINPROJ-JOB-0 first. Degradation bracket 2.6 h to
                       13 h at 1x to 5x the measured constant.
                       Recommend dispatch with a hard timeout at 3x = 17 h.
    RAM estimate:      7.12 GiB peak, at m=21, single process.
                       Basis: MEASURED 23.80 B/state at m=16 (RSS minus the
                       2.61 MB baseline, over 3,880,899 states), projected at
                       24.0 B/state against an EXACT state count of
                       318,281,039. 9.1% of ayr, 5.6% of dalby. At a
                       pessimistic 40 B/state it is 11.9 GiB.
    disk estimate:     working set nil (no spill, no checkpoint);
                       artifact ~60 KB output + ~2 KB .metrics per box.
    cores:             1. Do not use --threads > 1: the atomic-deposit path
                       has never passed GATE 5 and the run does not need it.
                       Parallelism is across the two boxes.
    interruptible:     No checkpointing. A kill loses the run; worst case is
                       the 1.6 h m=21 stage. Restart is a full re-run, or
                       --m 19..21 (120 cells, H=19..21) at 2.6 h if only the
                       target heights are wanted. Nothing is corrupted by a
                       kill: the output file is written at the end.
    RED control:       Two, both already measured and both cheap to re-run at
                       n<=7 against this binary: --mutant drop-nw must flip
                       exactly 12 of the 28 H<=n cells and --mutant rook
                       exactly 4 (r4_spin_gates.log, GATE 1, MEASURED
                       2026-08-13). If the production binary does not
                       reproduce 12/12/4, it is not the gated binary.
                       Additionally the run must reject a corrupted oracle:
                       the 640-cell H<=16 block must come back
                       mismatch=0, and a nonzero mismatch blocks the H>=17
                       cells from being read at all.
    closes:            r4-spinbuild.md NOT ESTABLISHED items: "no wall, RSS or
                       ns/op figure for this kernel exists" above m=16, and
                       "no m > 16 path has been exercised even on paper".
                       Does NOT close section 3(a) — the kink-vs-column
                       equivalence stays argued, not proved.

    job id:            R4-SPINPROJ-JOB-0   (prerequisite, ten seconds)
    measures:          the --verify-rank tax, as ns_per_transition at m=13
                       with the flag forced on.
    decides:           whether JOB-1 runs with --verify-rank 1 (if the tax is
                       <= 3x) or 0 (if it is worse). This is the only
                       correctness lever the m>16 range has.
    command:           build/r4_spin_engine --m 13 --cols 41 --nmax 40 --mod 4 \
                         --dense-rank --threads 1 --verify-rank 1 \
                         --oracle <repo>/results/cutcount_b1/rows \
                         --out results/r4/spin_vr13.txt --report-rss
    script:            same binary
    wall estimate:     3.1 s at 1x, ~7 s at the expected 2.1x. MEASURED base
                       (m=13 wall_s=3.109166), EXTRAPOLATED multiplier.
    RAM estimate:      9.1 MB. MEASURED (m=13 peak_rss_mb=9.07).
    disk estimate:     nil.
    cores:             1.
    interruptible:     trivially.
    RED control:       must still report compared=40 mismatch=0 for H=13; a
                       verify-rank run that changes any output value is a bug
                       in the verifier, not in the kernel.
    closes:            the inference in section 3.2.

---

## 6. NOT ESTABLISHED

- **`ns_per_transition` above m=16.** The projection rests on a constant
  measured over m=11..16 and assumed to hold 82x further out in working set.
  The mechanism argument (164x already survived, not memory-bound) is strong but
  it is an argument. Nothing between 93 MB and 7.6 GB has been measured.
- **The `--verify-rank` 2.1x multiplier** is inferred from the m=9,10 vs m=11+
  step coinciding with the flag's default boundary. Confounded with small-m
  effects. JOB-0 settles it.
- **No B1 oracle exists at H=17..21**, and none is projected by this file. I did
  not estimate when the B1 ladder reaches H=17..19.
- **I did not verify that `--m 17..21` alone reports H=19..21** rather than some
  other set; the reasoning is `r4-spinbuild.md` §3(e)'s "every (H,n) whose three
  strip heights were run", applied to the range. The recommended command is
  `--m 1..21`, for which the cell set is not in doubt.
- **The banked-triangle comparison is not implemented anywhere.** No script
  compares `spin_*.txt` T-rows against `results/ns_a40/perheight/h*.out`.
  R4-SPINPROJ-1 files it; it does not exist yet.
- **The 41-cell figure counts nonzero banked cells** (n ≥ 20 at H=20, n ≥ 21 at
  H=21) read off the two `.out` files. I did not check every intervening cell is
  nonzero; I checked the onset (`h20.out`: n=19 → 0, n=20 → 1,162,261,467).
- **The priors in §4 are ASSERTED judgements**, not derived from any error model.
- I did not read `r4_a_modp_bpw.log`. `r4-adv-cost.md` §2 already extracted the
  same-box cross-kernel comparison from it (703 ns/transition for B1 `--modp`),
  and my projection needs no cross-kernel anchor — it has this kernel's own.
- Nothing here says the engine is correct. §3 is the argument that it is
  under-checked at exactly the m values that matter, and §3.5 is what to do
  about it.
