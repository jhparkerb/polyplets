# a(35) two-media plan: the tall height in RAM, the rest on disk

**Status:** proposed, backed by an a34 measurement (2026-07-09). Needs a root
tmpfs mount and a short core-split calibration before an a(35) launch.

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

Projected win: the tall height (70% of the wall) drops **4.13×** (measured on
a34's H18: 9,336 s → 2,262 s), so it stops being the bottleneck. Job B (the
remaining heights on NVMe) becomes the new limiter. Two-media total ≈
`max(Job A, Job B)`:

- **a34 sanity check:** Job A (H18) = 2,262 s measured. Job B (H3–H17) was
  ~3,965 s of column-wall in the contended run; alone on NVMe it's the limiter
  at very roughly ~3.5–4 k s. So a34 two-media ≈ **~4,000 s vs 13,300 s ≈ 3.3×.**
- **a(35):** the ~70% tall height (~11 h contended) → ~2.7 h on tmpfs; Job B
  (~30%, NVMe, disk-bound among itself) becomes the limiter. Expect a(35) to
  land **~5–8 h vs ~16 h**, pinned by Job B's wall (calibrate — see below).

If Job B's footprint also fits the tmpfs (or a second one), putting it in RAM
too makes *both* jobs compute-bound and pushes the total lower still. Bonus
regardless: the tmpfs portion escapes the RAID1 mirror's pure-waste
double-write of ephemeral scratch.

## To pin before launch (short calibrations, no full runs)

1. **Core split C1/C2.** Job A is idle-heavy (~20 cores likely enough); give the
   rest to Job B. Measure the split that balances the A and B walls.
2. **Does H18 (a35's second height, 18%) also want tmpfs?** The top two heights
   are 88%. If the ~90 GB tmpfs can hold both tall heights' footprints, put both
   in RAM; otherwise just the tallest.
3. **Concurrent-orchestrate coordination.** Two processes writing distinct
   `--heights` to a shared `--per-height-out` (disjoint files) — confirm no
   collision; else separate dirs + combine both.
4. **Resume safety across two jobs.** Each job is independently checkpoint/
   resumable (the mid-column over-count bug is fixed, commit `dd91550`); a
   crash costs one job, not both. Job A on tmpfs is lost on a *reboot* (RAM) —
   acceptable for a same-day run, but don't rely on tmpfs surviving a power event.
5. **Root tmpfs mount** — jasonp, one command above.

## What this does NOT do

It does not reduce the algorithm's work — the H×N shuffles still happen. It
relocates the unavoidable ones into RAM for the height that dominates the wall.
The only deeper win would be stateful workers exchanging shuffle data over
pipes/sockets (a Spark-style engine, never touching a filesystem) — a real
rearchitecture, out of scope at project close.
