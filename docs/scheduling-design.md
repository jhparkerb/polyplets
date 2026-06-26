# Distributed scheduling design — a(N) transfer-matrix sweeps

Working design record for organizing the per-height column sweeps across cores and
machines, for a(22) and especially a(24)+. Captures what survived, what we cut and WHY
(so we stop re-litigating), and the open empirical questions.

## The problem
Minimize **makespan** of the ~N per-height sweeps. Jobs are **geometric** in cost
(~2.4×/height, ~4.3×/N), so a handful dominate; **RAM is the binding constraint** (it
OOM-kills, as it did on 2026-06-25); each job has config knobs — threads T, merge-batch B,
inter-height concurrency K — trading cores↔RAM↔speed.

## The unifying model: a work-unit queue
A priority queue/heap of work units, popped by boxes/cores as they free up.
- The inter-machine strategies (static cost-balanced plan / meet-in-the-middle / shared
  claim registry) are just **different pop-orders on the same queue** — they collapse to one
  mechanism.
- Intra-box, work-stealing is the same thing: pop balanced leaves off a local queue.
- **Granularity reality:** within a column, the leaves (hash shards / state-chunks) are
  independent and balance freely. But columns are **sequential** (col c+1 needs all of col c
  merged → a barrier), and the accumulating frontier **lives on the box running that height**.
  So a *height is sticky* — it's the coarse cross-box atom that can't be freely re-popped
  mid-stream. Decompose freely WITHIN a column and ACROSS heights; the height is the sticky unit.

## Survivors
- **Work-unit queue** (handout) — unifies static-plan / meet-middle / claim-registry.
- **Intra-box engine: I3 work-stealing pool + I7 shared lock-free concurrent hash table.**
  I7 (one shared table, atomic CAS insert + atomic/fine-locked count accumulate) is the
  candidate to *replace* the batched merge: RAM of the mutex version (one copy, no per-thread
  duplication, no OOM) AND scaling of the lock-free version (per-slot atomics, no global lock).
- **Sticky-height residual: M4 checkpoint-migration, M5 distributed single-height sweep** —
  the only tools for cross-box imbalance once a heavy height is the coarse atom.
- **I2 inter-height concurrency** — the RAM↔utilization knob; partly obviated if I7+I3
  saturate a single height.
- **Cost model** — predicts cost(H,N) and RAM(H,N,config); the foundation for the queue's
  priorities and for honest ETAs.

## Excluded — do not re-litigate
| id | idea | status | reason |
|----|------|--------|--------|
| I4 | pipeline the column barrier | **DROP** | hi effort + hi race-risk; conflicts with M4 AND M5; and I7 shrinks the merge phase it was trying to hide |
| M6 | role-specialized pipeline | **DROP** | subsumed by the queue — "roles" are just capability tags on work units |
| I6 | GPU / SIMD / new decomposition axis | **DEFER** | research-grade effort; forecloses M4+M5 (heterogeneous state can't migrate or distribute). Trigger to revisit: single-box CPU genuinely exhausted AND I7+I3 exhausted |
| I5 | NUMA-affine sharding | **DEFER** | constant-factor, multi-socket only; the heavy compute lives on single-node dalby, so it'd only help ayr. Trigger: a multi-socket box becomes the workhorse |

Consolidated: M1+M2+M3 → "the work-unit queue"; I1+I3 → "the work-stealing pool."

## Reuse (frontier + cells-remaining) — limited, mostly already captured
- *Within a sweep:* one height-H pass already yields B_H(n) for all n≤N. Maximal; done.
- *Generating function:* compute-once-all-n, but the recurrence order explodes (5005 at H=10),
  so it only pays for **H≤9** (which we have).
- *Across terms:* foiled — the size-pruning that makes a sweep tractable is **N-specific**
  (a(N) discards exactly the states a(N+1) needs), and the frontier grows geometrically, so
  a(N) gives almost no head start on a(N+1). The transition *rule* is reused; the *states* aren't.
- *Lifetime-3 GF factor-sharing across consecutive heights:* a hint of deeper structural reuse,
  but exploiting it at the DP level is a research thread, not a near-term lever.

## Open empirical questions (resolve before committing build effort)
1. **I7 hot-slot contention** — prototype the concurrent map, run a heavy column, measure
   atomic-add contention on hot output states. Low → I7 replaces the batched merge outright.
2. **M4 cross-arch checkpoint portability** — write a height's checkpoint on dalby (aarch64),
   resume on ayr (x86-64), demand byte-identical. Decides whether migration is cheap or needs
   an arch-portable serialization first.
3. **Cost-model calibration** — predict each a(21) height's wall + peak RAM, compare as they
   land; trust the planner once it's within ~±30%.

## Unexplored axes (negative space, 2026-06-25) — candidates, not yet scored
1. **Do less work, not just spread it** — state compression (sparse counts rows, packed
   signatures) + more symmetry reduction. Directly attacks RAM (the binding constraint);
   orthogonal to all scheduling. Never touched.
2. **Out-of-core / spill to disk** — stop assuming a column fits RAM (ROADMAP #20, dropped off
   the critical path). The real answer for a(24)+; pairs with M5 as the two ways past the RAM wall.
3. **Sort-based transition engine** — represent a column as a sorted stream, transition by
   sort+merge instead of hashing. External-memory-native (mergesort streams), contention-free,
   distributes cleanly. A whole alternative architecture.
4. **Adaptive per-column config** — the optimal (T, B, K) varies across a height's columns
   (small/cheap early, RAM-tight at the peak). We use a fixed per-height config; never per-phase.
5. **Elastic / opportunistic resources** — cloud burst for the pole, availability-aware scaling.
   We've assumed three fixed boxes.
6. **Verification as a continuous parallel pipeline** — validate partial results as they land
   (GF columns, triangle row-sums, a mod-p shadow) to catch a bad sweep days early, instead of
   only gating at the end.
7. **GF-recovery for the mid-heavy notch columns via mod-p** — fills whole height-columns for
   all n at once (vs per-cell sweeps); concrete bridge to the triangle work.
8. **Meta: are we over-computing?** — minimal-path question for the paper/OEIS goal vs the full
   triangle + holes + GFs we're generating.

## Strategic staging — the RAM cliff sets the agenda (2026-06-25)
Pole-sweep RAM, from the measured ~580 B/state (source+dest, no per-thread duplication — i.e.
the lean I7 engine) and the 2.41×/N pole law:

| term | pole states | lean sweep RAM | single box (dalby 122 GB)? |
|------|------------:|---------------:|----------------------------|
| a(22) | 6.9×10⁷ | ~40 GB | fits easily (current engine) |
| a(23) | 1.7×10⁸ | ~96 GB | fits **only with I7** (lean); batched engine ~150 GB → OOM |
| a(24) | 4.0×10⁸ | ~232 GB | does **not** fit any single box |

**The cliff is a(24), not a(23).** Decision (jasonp):
- **a(22):** current engine.
- **a(23):** I7 is what makes it RAM-resident at all (lean single shared table), MAXJOBS=1.
  **Use a(23) as the TESTBED for the new architecture** — prove the sort/stream engine,
  out-of-core, distribution, and compression on a job that still *fits*, so failures are cheap.
  Do NOT squeeze the current engine over an epic, hope-for-the-best a(24)+ run. "Probably more
  than I7 will be required" — a(23) is where we trial the a(24)/a(25) ideas.
- **a(24)+:** the sort/stream restructure is mandatory; storage backend becomes a deployment
  choice. Compression slides every row rightward.

## One bet, not four
#2 (disk-spill), #3 (sort engine), #5 (cloud Redis/Bigtable), and M5 (distributed) all require
the SAME thing: restructure the column transition from random find-or-insert into **batched /
sequential / sort** operations. Once that's done, the storage backend is a swappable deployment
choice (local disk · cloud KV · sharded across machines). The access-pattern restructure — not
the backend — is the actual bet; per-state random ops over disk OR network are equally fatal.

## Literature anchors (papers/refs-transfer-matrix.md, saved 2026-06-25)
- **Motzkin-path boundary encoding = Jensen's thesis** — the concrete instance of compression
  #1: encode boundary connectivity as a Motzkin-like string (count ~ Motzkin numbers).
- **Barequet & Ben-Shachar, ALENEX 2024:** fixed-polyomino record **n=70** via a **45°-rotated**
  transfer matrix on only **32 GB RAM**. OPEN QUESTION: does the 45°-rotation transfer to
  KING-polyplets? Earlier "diagonal deflation" said no (king diagonals span n×n) — RE-DERIVE,
  don't trust the note, given the size of this win.
- **Calibration:** ordinary polyominoes hit the RAM wall ~n=60 on 512 GB *with* Motzkin
  compression → RAM is the universal frontier constraint (validates the whole framing).

## #7 status: DORMANT — lit-checked, do not revive without new evidence
Meet-in-the-middle transfer matrix gives no speedup here (the seam = the peak frontier, not a
small matching key; it holds ~2× peak RAM; plus connectivity-closure at the seam). The lit
search found no MITM-TM for polyominoes, and the SOTA (Jensen → Barequet, n=70) is
one-directional under extreme optimization pressure — strong negative evidence.
