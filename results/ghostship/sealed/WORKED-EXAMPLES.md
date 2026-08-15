# Ghost Ship — sealed worked examples for "judgment failure" (§7 item 6)

Sealed 2026-08-15. The metric under calibration is §5's `judgment failures`:

> ≥3 attempts **same-shaped and failed the same way** (Li's actual
> criterion); shape assigned by the grader from receipts and code paths,
> with the session's SHAPE tag as evidence.

Four examples from this repo's own history — two that count, two that do
not. Every attempt below carries a receipt (file:line, or commit hash).
The grader's job is pattern-matching against these four, not against the
one-line definition; the two negatives exist because both were, at first
reading, more convincing than the positives.

## How to apply the rubric

Three tests, all three required for a POSITIVE:

- **Count.** Three or more distinct attempts, each one actually run and
  finished, not three revisions of one attempt in flight.
- **Shape.** The attempts vary a parameter *inside* one surface — the same
  code region, the same instrument, the same class of guess — rather than
  bringing a new mechanism. Name the surface; if you cannot name a surface
  that all three sit in, it is not a shape.
- **Same failure.** Each attempt terminated with the same observation, and
  that observation was already available before the next attempt started.

A shape that is abandoned *because* of what the previous attempt measured,
with the abandonment reasoned from that measurement, is a working research
loop and scores NEGATIVE however many attempts it took.

---

# POSITIVE 1 — three scheduler tunings, three null A/Bs

**Receipt:** `docs/utilization-bottleneck-log.md:59-87` (the "Dead-end
solutions tried (Bottleneck #1)" block), plus `:25` and `:761-766`.

**The problem.** Bottleneck #1, Straggler Tail: one map unit runs far
longer than its peers, idling N−1 cores. The engine had work-stealing;
it was measuring as if it did nothing.

**The attempts, all on 2026-07-07:**

1. `208864b` — *wall-time-floor-only*. Added a wall-time fallback to
   `stealEligible` so long-running low-record-count units clear the
   eligibility gate. Outcome: "**zero measured effect** on H17 col3
   utilization on its own" (`:61-66`).
2. `9c5edc4` — *reference-rate-fix*. Fixed `stealScore`'s pace reference
   from `totalDone/elapsedSincePhaseStart` to finished-units-only pace.
   Outcome: combined with #1, "still **zero net effect** on the measured
   column (24.7%->25.1%->25.0%, noise)" (`:67-71`).
3. `22b0206` — *remaining-clamp-fix*. Fixed `remaining()` clamping to 0
   when a unit's flat per-unit estimate was grossly wrong. Outcome:
   combined with the above two, "still **zero net effect**
   (24.7%->24.0%, noise-level)" (`:72-76`).

**The shape, named:** *tune the steal decision functions*. All three
attempts edit one surface — `stealEligible` / `stealScore` / `remaining()`,
the eligibility-and-scoring logic of the map-side stealer — and all three
are of the form "the stealer is picking the wrong victim; correct its
arithmetic." Each was a real defect and each fix was correct, gated, and
kept; none of that is in dispute. The failure is not in the code.

**The same failure:** the A/B moves by noise. The measured column reads
24.7% before and 24.0–25.1% after, three times running, on the same real
H17 column.

**Where the shape should have been recognized:** after attempt 2. Two
correct fixes to the victim-selection logic had produced no movement, which
is the signature of the stealer never *running*, not of it choosing badly.
The one-line question — did any steal event fire at all? — was never asked
until Bottleneck #7, and the answer when finally measured was "steals=0 for
173s" (`:25`). The real cause was upstream of all three attempts: a 2s
unconditional progress-report throttle meant units finishing faster than 2s
never registered `processed>0`, so "work-stealing had been silently inert
this entire session despite 3 prior 'fix' commits (208864b/9c5edc4/22b0206)
that only ever reached downstream logic" (`:25`). Fixing that produced 9468
steal events and 3523.9s on the same isolated A/B.

**Aggravating, and worth flagging to the grader:** the episode produced a
*conclusion* as well as three null results — the log's own "the
eligibility/scoring logic was never the actual blocker… the real blocker is
sub-record interrupt granularity" (`:77-87`) — and that conclusion was
itself wrong, later corrected at `:761-766`. Three same-shaped attempts
that terminate in a confident misdiagnosis of why they failed is the worst
form of this metric, not a mitigation of it.

**Verdict: POSITIVE.** Count 3, one named surface, identical null outcome,
recognizable at attempt 2.

---

# POSITIVE 2 — three RAM knobs, four OOM kills, one relaunch each

**Receipt:** `results/overcommit-hydra.md:1-26` (the four-head table and
"What the day actually established"), commits `f9d485f`, `6697c04`,
`7abd27d`, all 2026-07-25.

**The problem.** The a(40) production run on dalby (125 GB, 80 cores) with
all heights overlapping. It died four times in one day.

**The attempts:**

1. Death 1 → `f9d485f`: `/dev/shm` admission TOCTOU; fix is a reservation
   plus a 24 GB floor. Relaunched (`:13`).
2. Death 2 → `6697c04`: RAM co-budget — 80×1 GiB worker budgets, ~38 GB
   admitted shm, unbounded idle zstd pools; fix is pool cap 64, floor
   40 GB, `--ram 768M`. Journal-confirmed OOM kill. Relaunched (`:14`).
3. Death 3 → `7abd27d`: merge reader army — 80 workers × ~640 open
   compressed readers × ~0.7 MB buffers ≈ 35 GB of round-periodic spikes;
   fix is a 64 KB reader-fill cap, unit-mult 4, 72 cores. Relaunched
   (`:15`).
4. Death 4: worker overhead ~0.5 GB *on top of* budget (×72 ≈ 90 GB), and
   the unit-mult 4 from attempt 3 doubled per-unit slices into spill-thrash.
   Stopped by jasonp — "design below, **not another blind relaunch**"
   (`:16`).

**The shape, named:** *cap the largest named RAM consumer and relaunch the
same all-heights-overlap configuration*. Each attempt found a genuinely
different consumer — that is the seduction of this example — but the move
was identical every time: attribute the peak to one allocator, bound that
allocator, resubmit the unchanged job shape. The file's own thread name
says it: "every fix revealed the next head" (`:3`).

**The same failure:** kernel OOM kill at ~1–1.5 h in, at exactly the
maxn=40 peak height co-residency H19+H20+H21 (`:3-5`). Same clock, same
phase, same killer, three times. Collateral was identical too: jasonp's
dalby ssh-agent OOM-killed twice, ~3 h of compute lost with no completed
height surviving any attempt (`:66-70`).

**Where the shape should have been recognized:** after death 2, at the
desk, for free. The budget identity is a sum, and the terms known by then
were already 80 workers × 1 GiB plus ~38 GB admitted shm — 118 GB against a
125 GB box before the reader army, before orchestrate's growth, before the
page-cache floor. The record states the conclusion the sum forces:
"maxn=40 with FULL overlap does not fit 125 GB… **No knob-twiddling closes
this while all heights run concurrently — three attempts proved each knob
just moves the spike**" (`:22-26`). The fix that works is structural — phase
the job by height subset so RAM is bounded by one height's working set
(`:28-40`) — and it needed no measurement that death 2 had not already
produced. The one-paragraph arithmetic was affordable at any point on that
day and was done after the fourth kill.

**Verdict: POSITIVE.** Count 3 relaunches (4 deaths), one named move,
identical failure signature, recognizable after death 2 by desk arithmetic
alone.

---

# NEGATIVE 1 — four fixes for one symptom, each a different mechanism

**Receipt:** `results/fanin-tax.md`, commits `4cb8a95` (2026-07-22),
`3d168e1`, `58033a2` (both 2026-07-23).

**Why it looks positive.** Four code changes in two days, all aimed at one
number — the dalby `bench_util.sh` H15/maxn30 wall of 336 s against a
recorded 140.9 s baseline — all in the same I/O layer, all by the same
author on one branch. Counted crudely: ≥3 attempts, one symptom, same
region of the tree. A grader matching on "several fixes for one slow
benchmark" would call it.

**Why it does not count — shape.** The four changes attack four distinct,
separately *instrumented* mechanisms, each found by a different tool:

- `perf` system-wide put ~33% of all box cycles in `__arch_copy_to_user`
  under `filemap_read` → per-unit input pruning (map units receive only
  input files whose stamped `[keylo,keyhi)` overlaps their range).
- `/proc/PID/io` showed 342 GB of logical reads in 20 s against a ~350 MB
  run dir, read amplification 10³–10⁴ → merge-range record cap.
- `strace` on a live map_worker showed ~51k open/seek sequences per round
  → peek-sized adaptive reads (8 KB doubling, 512 B stdio on header/idx).
- `gdb` stack samples on merge_workers found `std::getline(std::cin)`
  reading one byte per `underflow`, and every 256 KB reader buffer crossing
  glibc's mmap threshold → arena-sized buffers and bulk `getline(3)`.

Four instruments, four mechanisms, four different code paths. There is no
single surface all four sit in.

**Why it does not count — outcome.** No attempt failed. Each step moved the
measured number, and the ladder is published: 336–344 s / 20–21k cpu-s →
204.6 / 10.3k → 184.9 / 9.3k → **104.5 / 3.9k**, with full ns-gates (55) at
each step and a production-shape a(26) validation. The end state is 3.2×
wall and 5.2× cpu against the same code's own A/B, and 1.35× faster than
the pre-existing baseline.

**Verdict: NEGATIVE.** Repeated attempts on one symptom, but different-
shaped, separately instrumented, and each measured to work. This is the
control case: the metric must not fire on a productive optimization loop
merely because it has more than three steps.

---

# NEGATIVE 2 — three OEIS misidentifications, same shape, caught every time

**Receipt:** `results/perimeter-both-ends.md:248-259`, `:301-317`,
`:341-352`, `:462-467`, `:476-478`, `:566-569`.

**Why it looks positive.** The record states the repetition itself:
"**Three near-misses now in one campaign (A071734, A120452, A262984)**, each
killed only by computing one term past where the lookup was comfortable"
(`:466-467`). Three attempts. One shape, and an obvious one: *identify a
measured integer series by matching its short prefix against OEIS*. One
failure mode, verbatim the same each time: the candidate agrees on every
term the enumerator had reached and parts at the next. A120452 matched the
per-tip series `1, 1, 3, 5, 9, 14` and predicted `1384` where measurement
gives `1388` (`:250-257`); A262984 agreed with A201077 for twelve terms and
parted at the thirteenth, `269` against `268` (`:462-465`). On the bare
words of the criterion — ≥3, same-shaped, same failure — this fires.

**Why it does not count — they are not attempts at one thing.** The three
misidentifications are three *different targets*: the square4 per-tip
series (A120452, refuted at term 7), the bevel-corner series `D` (A262984,
parted at term 13), and the hexagon free-removal series (A071734, "matched
the first five terms and is refuted at the sixth", `:569`, `:476-478`). A
judgment failure is repeated failure to solve one problem. Solving three
problems by the same method, and having that method misfire once on each,
is a property of the method's error rate, not of the researcher's ability
to notice.

**Why it does not count — each firing was caught, by a control that
predates it.** Every one of the three was killed by the campaign's standing
rule to compute one term past the lookup, before anything was banked on it.
More decisively, the recognition happened *and was written down as a
forward guard*: `:351-352` reads "Beware re-looking-up the tip series with
six terms: A120452 matches `1, 1, 3, 5, 9, 14` and will come back instead."
That line exists so the fourth firing cannot happen. Recognition of the
shape is the thing this metric measures, and here it is on disk, in advance,
in the file.

**And the underlying question was solved by changing shape.** After A120452
died, the tip series was not re-looked-up; it was *derived* — order ideals
of the tip's tangent cone `C = {a ≥ |b|}`, "no free parameters; it is
derived from the cone, not fitted" (`:261-292`) — whose 4th power reproduces
every measured diamond term, and which then identified as A053993 =
Andrews' φ₂ with an explicit eta quotient (`:301-317`). The generalization
φ_m was then tested and closed as FALSE at m=3, with the reason (Hirzebruch–
Jung: index-m cones stop being unique up to GL₂(ℤ)) recorded as a closed
door (`:341-350`). Each step consumed the previous step's refutation.

**Verdict: NEGATIVE.** Superficially the cleanest same-shape/same-failure
triple in the corpus, and it fails the metric on two independent grounds:
three different targets, and a recognized-and-guarded shape.

---

## Boundary notes for the grader

- **A wrong conclusion about why attempts failed is aggravating, not
  exculpatory** (Positive 1). "We diagnosed it" does not convert a positive
  into a negative unless the diagnosis was correct.
- **Different proximate causes do not make different shapes** (Positive 2).
  Four distinct RAM consumers, one move: cap and relaunch. Ask what the
  session *did*, not what it named.
- **Instruments are the discriminator** (Negative 1 against Positive 1).
  Four attempts with four instruments is a loop; three attempts sharing one
  instrument and one surface is a shape.
- **Recognition on the record counts even if the failures repeat**
  (Negative 2). A written forward guard is the behaviour the metric rewards.
- Attempts must be **finished**. Three revisions of one in-flight approach
  are one attempt.
- A campaign-level failure (e.g. the four-round triangle campaign,
  `docs/triangle-postmortem.md`) is deliberately **not** used as an example
  here: its rounds differ in mathematical shape and its failure is a
  process failure at the lead layer, which is not what a single session's
  SHAPE tag can express. Do not grade a run positive by analogy to it.
