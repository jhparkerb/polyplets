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
> **Each idea below (and the 3 open empirical questions above) now has a kill-test +
> improvement-ladder playbook in `docs/frontier/` — see `docs/frontier/README.md` for the
> verdict-lean table and the cheapest-and-decisive do-first ordering (2026-06-26).**

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
9. **`__uint128_t` counters — CRT-free exact counting to ~a(48).** a(n) overflows u64 at a(26)
   (a(25)≈1.5e19 < 2^64 < a(26)≈1e20) but doesn't reach 2^128≈3.4e38 until ~a(48). So a 128-bit
   counter gives EXACT counts, NO CRT, in a SINGLE enumeration pass, across the whole reachable
   frontier. Cheap on all our boxes: `__uint128_t` is double-width arithmetic, not bignum — add
   = 2 instrs (add+adc), multiply uses the native 64×64→128 widening mul (x86 MUL/MULX, ARM64
   MUL+UMULH); the only missing hardware op is 128÷64 division, which counting never does.
   THE CONTEST (worth a head-to-head when we pass a(25)): u128 single-counter vs the SETTLED
   interleaved-31-bit-CRT (crt-counter-shaping.md, which already pays enumeration once with k
   small counters). Roughly a wash on speed; u128 wins on SIMPLICITY — no CRT lift, no prime
   pool, no composite-prime footgun ("2147483479 is composite and silently corrupts"), exact
   integer falls straight out. Tangential: for GF recovery, 128-bit only buys 63-bit CRT primes
   (~half the prime count), NOT a single prime — H=10 coeffs are ~2^1300, need full bignum.

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
  transfer matrix on only **32 GB RAM**. **RESOLVED 2026-06-26 — NO-GO for king-polyplets, with
  numbers** (experiments/phase01_width_probe.cpp, the frontier-revision-plan §0.1 GO/NO-GO):
    - Redelmeier-enumerated every king-polyplet, measured the worst-case swept width of our
      column+transpose sweep `max min(H,W)` vs B-BS's 45° rotation `max min(Dmain,Danti)`.
      **Both = n exactly, every n** (n=1..13, perfectly regular) — the rotation gives ZERO
      worst-case improvement; it's *worse* on the mean (rotated-width mean 6.74 vs 5.20 at n=11,
      gap widening) because king diagonals blow the rotated bbox to ~2n wide (Dmn/Dan=21 vs H/W=11).
    - **Structural reason** (now concrete, not a cached dismissal): at every n there are
      king-polyplets that are width-n in BOTH boxes — the down-right staircase (H=W=n) saturates
      the upright box, an X-shape saturates the rotated one. B-BS wins for ORDINARY polyominoes
      precisely because their diagonals aren't edge-connected, so no such staircase exists.
      King-connectivity is exactly what defeats the rotation.
    - Caveat / only-remaining-out: worst-case width = peak frontier *size*, not the distinct
      *state*-count (the 2.44 base). But both worst-case (n=n, tied) AND mean (rotation worse)
      point the same way, so the state-count can't plausibly rescue it. The 2.76-vs-3.22 middle-cut
      proxy that once leaned the other way was occupancy-only and is superseded by this. **Retired.**
    - **REOPENED 2026-06-26 — retirement was premature, by our own caveat.** We retired on worst-case
      *width* while flagging that the real cost is the distinct *state*-count, "which can't plausibly
      rescue it" — but we never measured it. We did now (`experiments/phase02_statecount_probe.cpp`):
      the diagonal cut's distinct-partition base is **~2.04 vs the column's ~2.42** at equal width over
      king-polyplets n≤12 — the "middle-cut proxy that leaned the other way" was pointing at something
      real. A state-count *signal*, not yet a built TM; a correct king diagonal transfer matrix
      (Σ==a(n), real peak-state base) is under adversarial confirmation (`docs/frontier/NEXT-SYSTEM.md`).
      If confirmed it bends the growth exponent — the one lever that moves the feasibility ceiling.
      Do NOT cite this as a settled NO-GO.
    - The 4-direction *routing* idea (max4 = `max min(H,W,Dmain,Danti)`, grows ~n−2) is a DIFFERENT
      thing — it needs per-animal direction choice, not a single TM — and stays out of scope.
- **Calibration:** ordinary polyominoes hit the RAM wall ~n=60 on 512 GB *with* Motzkin
  compression → RAM is the universal frontier constraint (validates the whole framing).

## #7 status: DORMANT — lit-checked, do not revive without new evidence
Meet-in-the-middle transfer matrix gives no speedup here (the seam = the peak frontier, not a
small matching key; it holds ~2× peak RAM; plus connectivity-closure at the seam). The lit
search found no MITM-TM for polyominoes, and the SOTA (Jensen → Barequet, n=70) is
one-directional under extreme optimization pressure — strong negative evidence.
