# Terminal Velocity — g2 kernel shakeout for whole-row a(21) < 24h on dalby

> **UPDATE 2026-07-11:** the kernel optimization (2.06×) put a(22) in fleet reach, so
> execution went straight to the **a(22)** whole-row run (which subsumes a(21) as an
> inner row) — see `results/terminal-velocity.md`. The a(21)-specific goal/§7 launch
> below is superseded by that a(22) run; two-algorithm frontier moves 20 → 22.

Goal: independent whole-row Redelmeier confirmation of **a(21) = 6,954,084,405,510,437**
(two-algorithm frontier 20 → 21) in **< 24h wall on dalby alone**. Requires a
**≥ 2.25× kernel speedup**; target **2.5×+** for margin. Everything below is
measured-baseline math, ranked levers with correctness arguments, a strict bench
protocol, validation gates, and the launch procedure. Execute in order; every
lever is measure-gated (keep only what wins ≥3% on the target machine).

Context docs: `docs/redelmeier-tall-plan.md` (§5 whole-row rationale),
`results/redelmeier_row20/RESULT.md` (baseline run), `docs/job-checklist.md`
(consult before ANY launch).

---

## 0. Measured baseline (row 20, dalby, 2026-07-10, rev 7eab237)

| quantity | value | source |
|---|---|---|
| wall | 28,684 s (7.97 h) | `results/redelmeier_row20/driver.log` |
| total CPU | 2,204,116 core-s | sum of 800 shard `wall_s=` obs lines |
| utilization | **96.1%** (of 28684 s × 80 cores) | derived |
| shard wall_s | mean 2755 / p99 3092 / max 3188 | shard logs |
| full-cost nodes (size ≤ 19) | Σa(1..19) = 1.780067e14 | `combined.txt` |
| per-node cost | **12.38 ns = 37.1 cycles** @ 3.0 GHz | derived |

Row-21 projection at current speed: full-cost nodes = Σa(1..20) = 1.203580e15
(ratio **6.7614×**) → 1.490e7 core-s → **53.8 h** at 96.1% util. Speedup → wall:

    2.0× → 26.7h   2.25× → 23.7h   2.5× → 21.3h   3.0× → 17.8h

**Two structural facts drive the whole plan:**
1. Utilization is already 96.1% — scheduling is NOT the lever; the per-node
   kernel is. (§5 shaves the remaining ~3 points, that's all it can give.)
2. For N=21, **85.2% of all full-cost nodes sit at size 20** — the
   terminal-batch level (`size+1 == maxn`), the cheapest level to specialize.
   And 85.2% of the *remaining* interior nodes sit at size 19. The bottom two
   levels are essentially the entire run.

Machine: dalby = 80× Neoverse-N1 (Ampere Altra, aarch64, no SMT, single socket,
64 KB L1d/core, 1 MB L2/core), gcc 15.2, `perf` installed,
`kernel.perf_event_paranoid=0` already set. RAM is a non-issue (~3 MB/worker).

**Installs:** none needed — dalby has clang too (confirmed by jasonp 2026-07-11).

**Scope updates (jasonp, 2026-07-11):**
- **Fleet approved for a(21):** ayr (32 cores) and gympie (10 perf cores) join
  dalby (80) for the row-21 run — §7 uses all three, not fallback-only.
- **Deliverable addition:** when optimization is done, explicitly report where
  the whole-row reach frontier lands — if a(22)+ becomes computable in a
  reasonable fleet budget, say so with measured numbers (§8).

---

## 1. Phase P0 — profile first (½ h, no approval needed)

Confirm the cost breakdown before touching code. On dalby (build first:
`git pull && make build/g2 build/g2_asan`):

```
cd ~/src/polyominoes
perf stat -e cycles,instructions,branches,branch-misses,L1-dcache-loads,L1-dcache-load-misses \
    build/g2 square8 15 > /dev/null
perf record -o build/g2_n15.perf.data -- build/g2 square8 15 > /dev/null
perf report -i build/g2_n15.perf.data --stdio | head -40
perf annotate -i build/g2_n15.perf.data --stdio 2>/dev/null | head -120
```

N=15 runs ~2.7 min single-core — the right size for iteration. Record in the
results doc (§8): IPC, branch-miss %, and the hot-instruction picture inside
`searchT`. **Hypothesis to confirm:** the kernel is branch-miss-bound (the 8
`if (!st[j2])` probes at `cpp/g2_redelmeier.cpp:495` are ~50/50 coin flips;
~11-cycle flush each on N1 explains most of the 37 cycles/node). If the profile
says something else (e.g. the `memcpy` at :440, or the recursion overhead),
re-rank §4 accordingly — but implement L1 regardless; its win is structural
(work elimination), not microarchitectural.

---

## 2. Bench protocol (applies to every lever)

- **Machine:** dalby only, idle (check `uptime`; nothing else of ours running).
  Never bench on the mac (wrong ISA) — memory `verify-on-clean-target-env`.
- **Iterate:** `time build/g2 square8 15 > /dev/null` (~160 s now). Take best
  of 3. **Confirm:** `square8 16` (~18 min now) once per *kept* lever.
- **Keep rule:** a lever stays only if N=16 improves ≥3% over the previous
  kept build AND `make gate-g2` passes AND the ASan/UBSan build (`build/g2_asan`)
  is clean at gate depths. Otherwise revert it and log the number anyway.
- Log every A/B (lever, N, seconds, speedup vs baseline) in the results doc as
  you go — dead ends included, named (memory `name-tasks-and-threads`).
- The aggregate (no `--per-box`) instantiation is the production path for the
  row-21 run; that's the one being tuned. Gates still exercise per-box/split/
  analysis paths — they must stay correct but need not get faster.
- After each remote edit: rebuild ON dalby before benching (memory
  `rebuild-remote-after-engine-edit`; the `git=` hash in g2's obs `event=start`
  line must match your commit).

---

## 3. The kernel today (orientation for the implementer)

`cpp/g2_redelmeier.cpp`, all action in `searchT` (:437-541):

- One invocation handles a whole sibling group: memcpy the parent's untried
  list (:440), pop cells one at a time (:453), place, count (`bs[size]+=1`),
  probe `DEG=8` neighbours with conditional mark+push (:493-499), then either
  **terminal-batch** (`size+1 == maxn`: count all children at once, :509-525)
  or recurse; finally unmark own fresh cells (:532) and unplace.
- Run-constant modes are template params; the production instantiation for the
  row run is `DEG=8, PERBOX=false, NEEDS=false, SPLIT=true`. `TRACKBOX` is
  false there, so no bbox work — already compiled out.
- `status` values are only ever 0/1 (border, placed, tried, and listed cells
  are all folded into 1). This fact powers L1/L2 below.
- Buffer: `untried[kMaxUntried]`, kMaxUntried = 40*8+8 = 328 ints.

Node costs today (blended 37 cy): a **size-20 node** (85.2% of N=21 work) does
pop + count + 8 branchy probe/mark/push + batch-add + unmark-walk. A **size ≤ 19
node** additionally pays recursion (call + memcpy of up to ~170 ints).

---

## 4. Phase P1 — ranked levers

Implement in this order; re-profile after L1+L2 land.

### L1 — terminal level becomes pure counting (the big one; est ~2-2.4× alone)

At a size-20 node under `!PERBOX && !NEEDS`, nothing downstream ever reads the
marks or the pushed cells: the batch counts children and the unmark walk
immediately erases the marks. The 8 probed cells are pairwise distinct (8
distinct offsets from one center), so no dedup-marking is needed within the
probe. Since `st[] ∈ {0,1}`, the child count is just `numUntried + (8 − Σ st)`:

```cpp
// inside the `descend && size < maxn` block, BEFORE the probe loop:
if constexpr (!PERBOX && !NEEDS) {
  bool canBatch = true;
  if constexpr (SPLIT) canBatch = (splitS < maxn);
  if (canBatch && size + 1 == maxn) {
    int stale = 0;
    for (int k = 0; k < DEG; ++k) stale += st[j + djp[k]];   // pure loads
    bs[maxn] += static_cast<u64>(numUntried + DEG - stale);
    goto unplace;   // or restructure: skip probe loop, batch, unmark entirely
  }
}
```

Replaces (per size-20 node): 8 branches + up to 8 stores + push writes + batch
add + unmark loop → **8 byte loads + adds, zero stores, zero branches** on data.
Correctness argument (put it in the source comment): (i) offsets distinct ⇒ the
8 probed cells distinct ⇒ Σ(1−st) = #fresh with no marking needed; (ii) old code
computed `newCount = numUntried + #fresh` then `bs[maxn] += newCount` — identical
value; (iii) no marks are made, so nothing to unmark, and parent state is
untouched (tried-rule marks on `j` itself were set when `j` entered a list and
are unaffected). The `PERBOX` terminal batch (:514-521) keeps the existing loop
(it needs each child's coordinates). Keep the existing `SPLIT && splitS == maxn`
guard semantics exactly (we run S ≪ 21, but the gate tests S at the boundary).

### L2 — branchless probe at interior levels (est 1.2-1.5× on the remaining 15%)

```cpp
for (int k = 0; k < DEG; ++k) {
  const int j2 = j + djp[k];
  const int fresh = 1 - st[j2];   // st is 0/1
  untried[newCount] = j2;         // unconditional; slot only claimed if fresh
  newCount += fresh;
  st[j2] = 1;                     // idempotent: already-1 cells stay 1, correctly
}
```

Eight unpredictable branches per interior node become straight-line code.
Correctness: marking an already-1 cell 1 is a no-op (border/placed/tried cells
must stay 1; the unmark walk touches only `untried[numUntried..newCount)`, which
records exactly the fresh cells). The dead store at `untried[newCount]` when
stale needs one slot of slack — kMaxUntried already carries +8; assert/ASan
confirms (§6). Note L1 removes this loop from the dominant level; L2 is for the
size ≤ 19 levels that recurse.

### L3 — compile-time grid stride (small, ~free to try)

`gridW = 2*maxn+3` is runtime, so `dj[k]` are runtime values loaded through
`djp`. Fix the stride at a constant 128 (grid becomes 128 × (maxn+3) ≈ 5.5 KB,
still trivially L1-resident) and make the per-lattice offsets `constexpr`
template parameters: every `j + djp[k]` folds into an immediate-offset load.
Touches `cellIndex` (:261), `init` (:272-287), and the dispatch to pass offsets
as template args. Verify no `allowed()`/border assumptions depend on the exact
width (they don't — border ring logic is coordinate-based).

### L4 — u16 untried entries (only if profile shows memcpy matters post-L1)

Max cell index = 128×43 = 5504 < 65536 ⇒ `uint16_t` untried entries halve the
per-recursion memcpy and buffer footprint. Mechanical; measure.

### L5 — fuse the size-19 level (only if still short of 2.25× after L1-L4)

After L1, size-19 nodes are 85% of what's left. Each still pays call + memcpy
to process its children. Fusing (`size+2 == maxn`: iterate children inline —
mark j's fresh cells as now, but handle each child with the L1 pure-count
instead of recursing) removes the memcpy/call for that level. More invasive;
sketch it, gate it, measure it. Skip if L1-L4 already clear 2.5×.

### L6 — compiler sweep (cheap, do last on the final kernel)

1. `-mcpu=neoverse-n1` (or `-mcpu=native`) added to the g2 build flags — measure.
2. gcc PGO: `-fprofile-generate` → run `square8 15` → `-fprofile-use`. Note:
   the PGO-no-go memory (`pgo-no-go-dalby`) is about the TM engine's viableRec,
   a different binary; and after L1/L2 the branch profile here is transformed.
   One cheap measurement settles it.
3. clang A/B if installed (see installs list). Keep whichever binary wins N=16;
   record compiler+flags in the results doc and pin them in the Makefile g2 rule
   (guard aarch64-only flags the way RESTRICT_FLAG is guarded).

**Do NOT spend time on:** NEON vectorization of the probe (8 scattered byte
loads across 3 rows — poor fit, high risk), rewriting to Mertens-style linked
lists (whole-kernel rewrite; only revisit if L1-L5 measurably fail to reach
2.25×), threads inside g2 (the shard model is already at 96%).

---

## 5. Phase P2 — scheduling polish (30 min)

- **K=2400, S=12** for the row-21 run (vs 800/10 at row 20). Finer shards cut
  the straggler tail (row 20: max/mean = 1.157) and give ~1h progress
  granularity. Cost check (do the arithmetic in the results doc): every worker
  walks the size<S tree; Σa(1..11) ≈ 5e7 nodes ≈ 0.6 s/worker — negligible
  ×2400. Subtrees per shard ≈ a(12)/2400 ≈ 1e5 → tight balance.
- **Driver ETA line** (memory `surface-job-etas`): after each shard completes,
  `scripts/g2_wholerow.sh` should append to driver.log:
  `done=D/K elapsed=Es eta=(E/D)*(K-D)s` (trivial edit near the launch loop;
  works because shards are near-uniform). Keep per-shard obs lines as-is.
- Keep JOBS=80. No nice/taskset needed (single-socket, no SMT, box is ours).

---

## 6. Phase P3 — validation ladder (gates before any long run)

Standards: `docs/engineering-standards.md`; quality gates run via pre-push hook.

1. **`make gate-g2` green** after every lever (checks A fixtures, B per-box vs
   oracle, C split-sum invariance, D ASan agreement). Note check A covers
   square8 only to n=11 — small-n; that's why steps 3-5 exist.
2. **Extend the gate for the new terminal paths** (add to `tests/gate_g2.py`):
   - New-vs-old cross-check: full `--per-box` histogram AND aggregate output of
     the new binary vs rev-7eab237 behaviour for n ≤ 13, all three lattices —
     in practice, assert new aggregate == new per-box row-sums == b-file, and
     split boundary AT maxn (`--split S=maxn`) still exact (exercises the
     canBatch guard).
   - ASan depth bump so the L2 unconditional-store slack is actually exercised
     at a size where untried lists get long (square8 n=12 asan is cheap).
3. **Row 18 smoke on dalby** (~4 min wall on 80 cores at 2.5×):
   `scripts/g2_wholerow.sh 18 12 400 80` — combined must match banked rows 1-18.
4. **Row 19 scale gate** (~25 min wall at 2.5×): same, K=800. Exact match
   required vs banked (`results/b006770_upload.txt`). This exercises the L1
   terminal path at level 19 and the full shard machinery at scale.
5. **Row 20 re-run with the FINAL binary+flags** (~3.2h wall at 2.5×) —
   **[ASK JASONP — >1h job]**. Must reproduce a(20)=1025573519362016 and all
   inner rows. This is the `validate-at-scale-before-record` gate: it exercises
   the new terminal level at 20, i.e., the exact code path that will produce
   the a(21) number one level deeper. Also directly measures the true speedup
   → recompute the row-21 ETA from it (nodes ratio 6.7614× minus the terminal/
   interior mix shift; just scale measured core-s by Σa(1..20)/Σa(1..19) with
   the new per-level costs, or simply by 6.76 for a conservative bound).

A mismatch at ANY step: stop, investigate, never "fix toward" the expected
value (tall-plan §4 rule). The inner rows 1..20 of the eventual row-21 run
re-validate everything except the terminal level — which is exactly why step 5
is non-negotiable.

---

## 7. Phase P4 — the a(21) launch **[ASK JASONP — explicit beg-and-agree]**

Pre-launch: `docs/job-checklist.md` top to bottom. Quote the measured row-20
re-run speedup and the derived ETA in the ask.

```
# dalby, inside the existing tmux session 0, NEW WINDOW named g2_a21, FOREGROUND:
cd ~/src/polyominoes
scripts/g2_wholerow.sh 21 12 2400 80 2>&1 | tee runs/g2row_N21.launch.log
```

(The script self-logs to `runs/g2row_N21/driver.log`, writes driver.pid, is
per-shard resumable, and now emits ETA lines. Wait with
`tail --pid $(cat runs/g2row_N21/driver.pid) -f runs/g2row_N21/driver.log`.)

**Fleet mode (approved):** ayr (32 cores) and gympie (10 perf cores, HARD cap,
efficiency cores off-limits) join dalby. Mechanics:
- Add `FROM TO` args to `scripts/g2_wholerow.sh` so each box runs a disjoint
  shard IDX range of the SAME (N=21, S=12, K=2400) split; a combine-only mode
  then sums w*.out pulled from all three boxes. Split-sum invariance (gate C)
  makes this exact regardless of which box ran which shard.
- Build native on each box with that box's best §4-L6 compiler/flags (ayr:
  plain g++, no Go involvement; gympie: clang/macOS, `gtail` for waiting).
- Allocate IDX ranges ∝ cores × measured single-core N=16 seconds per box
  (calibrate first — per-core speed differs across N1/x86/Apple; a static
  range split with wrong ratios idles the fast box at the end).
- One tmux session per machine, job windows foreground with tee, per standards.
- ayr budget: ~3 MB/shard × 32 ≈ 100 MB — trivially inside 78 GB/32-core.

Expected: at 2.5× kernel, dalby-only ≈ 21.3h; with ayr+gympie (+~40-50%
effective cores) ≈ **14-15h**. At 2.25×, dalby-only ≈ 23.7h, fleet ≈ ~16h.
RAM/disk: no concern anywhere (w*.out are tiny).

**Acceptance:**
1. All 2400 shards `.done`; driver combined without missing-shard error.
2. Rows n=1..20 of `combined.txt` match banked exactly (script §6-style diff).
3. Row 21 == **6954084405510437** (banked TM value, `results/ns_a21/`).

**Banking:** `results/redelmeier_row21/` (combined.txt, driver.log, RESULT.md
with cost/util/speedup table and the lever ledger), update
`results/redelmeier_row20/RESULT.md`'s frontier note, HANDOFF.md frontier
(two-algorithm → 21; A030233/A030222/A194596 inherit at 21), and the
`redelmeier-tall-plan.md` §5 decision entry. Commit per repo standards.

---

## 8. Results doc + running ledger

Create `results/terminal-velocity.md` at P0 and append as you go: profile
findings, every lever A/B (kept AND rejected, with numbers), final compiler/
flags, gate evidence, row-19/20 validation walls, final row-21 cost. This doc
is the postmortem-grade record; the plan file stays as-written.

## 9. Fallbacks if the kernel stalls short of 2.25×

In order of preference — all are jasonp's call, present with measured numbers:
1. **Accept the miss** ("as close as possible"): e.g. 2.0× → 26.7h.
2. **Add ayr (32 cores) and/or gympie (10 perf cores)** as extra shard-range
   workers (g2 builds native everywhere, no deps; ayr: use ~/go/bin-first PATH
   irrelevant here, plain g++; respect ayr 78GB/32-core budget — trivially fits;
   gympie hard cap 10 cores). +42 cores ≈ 1.5× fleet-wide — but this leaves
   "on dalby" and duplicates the size<S walk per extra worker (still negligible).
   Shard split: give dalby IDX 0..K_d-1 etc. via three g2_wholerow invocations
   with disjoint IDX ranges (needs a small script tweak: FROM/TO args).
3. **L5 fusion** if it was skipped, then re-measure before resorting to (2).

## 10. Risk register

- **L2 buffer slack**: unconditional store writes one past the claimed region.
  kMaxUntried has +8 slack; add a static_assert + the ASan gate at n=12.
- **Terminal-path bugs invisible to inner rows**: mitigated by §6 steps 3-5
  (terminal level exercised at 18/19/20 against banked values).
- **`goto unplace` structure in L1**: if it fights the template structure,
  restructure as an if/else around the probe block instead — no control-flow
  cleverness; the compiler does fine either way. Keep the diff reviewable.
- **Neoverse-N1 quirk**: no turbo; all-core = 3.0 GHz sustained, so single-core
  bench numbers translate directly to 80-core walls (row 20 confirmed this).
- **Do not restart a healthy run** to deploy a mid-run optimization
  (memory `a21-run-do-not-restart`): once row 21 launches, improvements wait.
