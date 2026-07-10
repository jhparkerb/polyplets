# a(35) two-media plan: the tall height in RAM, the rest on disk

> **⚠ FAILED FOR a(35) — RAM CEILING (2026-07-09). DO NOT RE-RUN ON THE 125 GB BOX.**
> The launch OOM'd. a(35)'s tallest real height **H19 does not fit in RAM**: its
> mid-stage frontier hit **89 M records / 82 GB of tmpfs at column 2 alone**
> (still climbing — peak is mid-sweep), vs a34's H18 at 11.5 M / ~40 GB. That's
> ~8× per height increment, not the ~2× extrapolated below. H19's working set is
> ~150–200 GB, far over the box's 125 GB, so with swap removed the OOM killer
> took the jobs **and the tmux server**.
>
> **Corrected scope:** the two-media/tmpfs win is real and measured **up to a34**
> (4.6×, 48 min) — but only because a34's tall height fits RAM. It has a hard
> ceiling at ~a34 on a 125 GB box. **a(35)'s critical-path height is intrinsically
> disk-bound here; a(35) = ~16 h on NVMe (single-run).** Reviving tmpfs for a35+
> needs a ~200 GB+ RAM machine, not just a bigger tmpfs. The a34 result and
> reasoning below stand; the a(35) projection does not.

**Status:** a34 measured (4.6×); a(35) FAILED (RAM ceiling, above).

## The finding

a(35) (and a34) run **disk-bound** — 60–69% iowait, both NVMes in the md3
RAID1 mirror at ~93% util writing ~780 MB/s, with the spill dir *empty*. The
cost is not spill thrash; it is the kink kernel's structure: **H+1 ≈ 19
barriered rounds per column, each materializing the full frontier** (map
outputs, then merged outputs) to the run-dir, read back by the next round.

That rewrite loop is the real cost — but it is **not redundant work that can be
removed**:

- Each stage round is a genuine **all-to-all shuffle**. `canonMixed` does a
  global first-occurrence relabel every stage, so output keys are uncorrelated
  with input keys. We already proved this shuffle is **not partition-
  preservable** (a banded/local encoding can't exist — the relabeling expands),
  so it can't be localized to avoid the redistribution.
- The per-stage **dedup (merge) is load-bearing**: each `kinkStageTransition`
  can split a record into successors, and the merge sums duplicates back down.
  Skip it or do it less often and the frontier count explodes between merges.
- The record encoding is already near its information floor (~110 B vs ~130 B
  deployed).

So the number of shuffles (H), the volume per shuffle (N records), and the
record size are all pinned by the algorithm. The **only free variable is where
each shuffle materializes: disk or RAM.** Putting it in RAM via a single fused
in-memory process was already measured and rejected (shared-allocator
contention, ~15–24 effective cores vs ~35 for the multi-process/file path).
That leaves **tmpfs** — RAM-backed files keep the multi-process design (no
allocator penalty) while paying RAM latency instead of NVMe-mirror latency for
each unavoidable shuffle. tmpfs is not a workaround for the rewrite loop; it is
the fix for it.

## Measured evidence (a34, dalby, 2026-07-09)

**The cost is concentrated in the single tallest height.** Per-height wall of
the banked a34 run (13,300 s total):

| height | wall_s | % |
|---|---|---|
| H18 | 9,336 | 70% |
| H17 | 2,376 | 18% |
| H16 | 722 | 5% |
| H15–H3 | ~870 | ~7% |

H18 alone is 70% of the run; H18+H17 is 88%.

**Isolating the tall height on NVMe does *not* help** — it is disk-bound on its
own, because one height's 19-rounds-per-column churn already saturates the
mirror:

- H18 alone, run-dir on NVMe: **63% iowait**, col 3 = 612 s vs 719 s contended
  (~1.2×). Contention between heights was never the cause; the I/O intensity of
  a single height is.

**Isolating the tall height on tmpfs eliminates the wait:**

- H18 alone, run-dir on `/dev/shm`: **iowait 0%**, and per-column 4.5–5.6× on
  the expensive columns (col 4: 928 s → 166 s = 5.6×; col 3: 719 s → 148 s =
  4.9×; col 8: 674 s → 151 s = 4.5×).
- **H18 total: 9,336 s → 2,262 s = 4.13×.** Per-height output **byte-identical
  to the banked `h18.out`** (`H18_BYTE_IDENTICAL PASS`) — running the height in
  isolation on a different medium does not change the result.
- Footprint: H18-alone peaks ~40 GB — fits `/dev/shm`'s 63 GB.
- Once disk-free, H18-alone is **compute-bound** during the expensive columns
  (**89% user CPU, 0% idle, 0% iowait**) — removing the I/O wait converted it
  straight into useful compute. (A single mid-barrier sample can read ~idle,
  but the wall-dominating columns are CPU-bound.)

## The architecture: split by height AND by medium, run concurrently

Two `orchestrate` processes on one box:

- **Job A — the tall height(s):** `--heights <top>`, run-dir on **tmpfs**.
  Disk-free → the 70% critical path runs ~3–5× faster. Needs few cores.
- **Job B — the rest:** `--heights <rest>`, run-dir on **NVMe**. Gets the bulk
  of the cores, which Job A leaves idle.

Run them **concurrently, not sequentially.** They complement rather than
contend: Job A, once disk-free, is **CPU-bound** and touches no disk; Job B is
**disk-bound** on NVMe and its worker threads spend most of their time waiting
on I/O, releasing CPU. Co-scheduling a CPU-bound and an I/O-bound job is the
classic way to fill a box — A uses the cores B isn't using while B waits on the
disk A isn't using. Total wall ≈ `max(A, B)` instead of `A + B`. Heights are
independent, so the per-height outputs simply `combine` at the end —
byte-identical to a single run (the kink kernel already supports `--heights`
subsets for the multi-machine split; this is a run-orchestration change,
**no kernel change**).

Why concurrent beats sequential here: sequential would give up the co-schedule
entirely (A finishes, *then* B), serializing ~5×-faster-A after B instead of
hiding B's disk waits behind A's compute.

## a(35) execution

The tallest real-swept height for maxn=35 is ~**H19**; footprint ~2× a34's H18
≈ **~76 GB**, which is over `/dev/shm`'s 63 GB. So a(35)'s Job A needs a
**root-mounted tmpfs**, e.g. (jasonp runs this):

```
sudo mount -t tmpfs -o size=90G tmpfs /mnt/polytmp && sudo chown jasonp /mnt/polytmp
```

90 GB tmpfs + the Job-B workers must stay under the box's 125 GB RAM — Job B is
on NVMe, so its RAM is just worker heaps (kink is RAM-light), leaving ample
headroom. Then:

```
# Job A: tall height in RAM
orchestrate --maxn 35 --heights 19 --kernel kink --counter u128 \
  --cores C1 --ram 1073741824 --run-dir /mnt/polytmp --spill-dir /mnt/polytmp/spill \
  --per-height-out runs/ns_a35/perheight ...

# Job B: the rest on NVMe (concurrent)
orchestrate --maxn 35 --heights 3-18 --kernel kink --counter u128 \
  --cores C2 --ram 1073741824 --overlap-heights 16 --run-dir runs/ns_a35/nvme \
  --spill-dir runs/ns_a35/nvme/spill --per-height-out runs/ns_a35/perheight ...

combine -in runs/ns_a35/perheight -maxn 35 -out a_n.txt   # after both finish
```

**Measured win (a34 two-media calibration, 2026-07-09):**

Running H18 on `/dev/shm` concurrently with H3–H17 on NVMe, both `--cores 80`:

- **Total wall 2,883 s vs 13,300 s single-run = 4.6×** (a34: 3.70 h → 48 min).
- Job A and Job B **both finished at 2,883 s** — near-perfect balance with no
  core-split tuning; the OS co-scheduled the oversubscribed pair. Job B (NVMe)
  is the limiter; Job A (H18/tmpfs, 2,262 s solo) fits inside it under sharing.
- **All 16 real heights byte-identical to banked** (`TWO_MEDIA_CORRECT PASS`).
- CPU over the run: **75% busy (61% user + 14% sys), iowait 10%, idle 15%** —
  vs the single run's ~15% busy / ~60% iowait. The co-schedule fills the box:
  with H18 off the disk, Job B's own contention drops, so it beats the estimate.

Extrapolated to a(35) (single-run ~16 h): **~3.5 h**, i.e. an overnight becomes
an afternoon. The tall height is an even larger share at a35, so if anything the
ratio holds or improves — pinned only by Job B's wall, which the a34 run shows
co-schedules well. If Job B's tall members (H17/H16) also go on tmpfs, both jobs
become compute-bound and it drops further. Bonus regardless: the tmpfs portion
escapes the RAID1 mirror's pure-waste double-write of ephemeral scratch.

## Remaining before an a(35) launch

1. ~~**Core split C1/C2.**~~ RESOLVED by the a34 calibration: both jobs at
   `--cores 80` (oversubscribed) balanced to finish at the same instant; the
   CPU-bound/I/O-bound pair co-schedules itself. Use `--cores 80` for both.
2. ~~**Concurrent-orchestrate coordination.**~~ CONFIRMED: two processes wrote
   distinct `--heights` (H18 vs H3–17) to a shared `--per-height-out` with no
   collision, all outputs byte-identical.
3. **Root tmpfs mount** — the one blocker. a34's tall height fit `/dev/shm`
   (~40 GB); a(35)'s H19 (~76 GB) needs a root-mounted ~90 GB tmpfs (command
   above). jasonp runs it.
4. **Optional: second height on tmpfs.** The top two heights are 88%. If the
   ~90 GB tmpfs holds both H19 and H18 footprints, put both in RAM to push
   lower; otherwise just the tallest (already a 4.6× win at a34).
5. **Resume safety.** Each job checkpoints/resumes independently (mid-column
   over-count bug fixed, `dd91550`); a crash costs one job. Job A lives in RAM,
   so it's lost on a *reboot* — fine for a ~3.5 h same-day run; don't rely on
   tmpfs surviving a power event.

## What this does NOT do

It does not reduce the algorithm's work — the H×N shuffles still happen. It
relocates the unavoidable ones into RAM for the height that dominates the wall.
The only deeper win would be stateful workers exchanging shuffle data over
pipes/sockets (a Spark-style engine, never touching a filesystem) — a real
rearchitecture, out of scope at project close.
