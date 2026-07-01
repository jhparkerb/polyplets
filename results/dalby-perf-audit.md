# dalby performance audit — collection plan + findings

Skeptical pass: is there more performance on the table, from "is this the right
design" down to "what microarchitecture is this." Run on dalby (the actual a(24)/
a(25) production box), with system-level instrumentation alongside a real,
production-shaped job — not just our own application telemetry.

## Layer 0 — design (already investigated; not re-litigated here)

Column-sweep transfer-matrix, map/merge per column, all-to-all merge (forces
fan-in to a bounded efficient width — designs/06,09,10), height-diagonal
injection (k≤7, the dominant cost-reduction lever), overlap+steal (this
session). Locality/partition-preserving alternatives were investigated and
rejected (merge-shuffle-ranking-locality memory: a banded/local encoding can't
exist without expansion). No new design-level lever surfaced; flagged here only
to confirm the audit didn't skip this layer.

## Hardware facts (gathered before running anything)

- **dalby is aarch64, ARM Neoverse-N1** (not x86 — invalidates any x86-specific
  assumption, e.g. the deferred CRC32C work's SSE4.2 path is dead code here;
  only the ARM ACLE `__crc32cd` path applies).
- Single socket, single NUMA node, 80 cores, **1 thread/core (no SMT)** — rules
  out NUMA-locality and hyperthread-oversubscription concerns entirely.
- CPU max 3.0 GHz, min 1.0 GHz, governor **schedutil** (load-following).
- Disk: two real datacenter NVMe (Samsung MZQL2960HCJR), mirrored via mdadm
  **RAID1** (not network storage) — write IOPS/bandwidth capped near single-disk
  pace (RAID1 duplicates writes), reads can stripe ~2x.
- 125 GB RAM, 122 GB free at rest.
- No cgroup CPU quota found; PSI (pressure stall info) available — modern kernel.
- **Compiler gotcha (separate finding, not perf-motivated):** Makefile says
  `CXX ?= c++` (→ clang 19.1.7 on this box), but GNU Make's *built-in* default
  `CXX=g++` wins over `?=` (a `?=` assignment never overrides an already-set
  Make variable, and built-ins count). So Linux boxes have been silently
  building with **GCC 15.2.0**, not Clang — different from gympie (macOS,
  Apple Clang), where this session's microbenchmarks (sigCmp, combine, stride)
  were run. Worth a deliberate, explicit compiler choice in the Makefile.
- No `-march`/`-mcpu` tuning flag anywhere — generic aarch64 codegen on a known,
  specific microarchitecture.

## Collection plan

**Pre-run (one-time, cheap):**
1. Compiler × `-mcpu` A/B (g++/clang++ × generic/-mcpu=native) on a real
   representative sweep (maxn=18, byte-exact `--compare`) — decide what to
   deploy for the main run.
2. Confirm clean, current rev deployed (job-checklist gate).

**During the main run (sampled concurrently, not after):**
- `vmstat 2` — run queue length, context switches, user/sys/idle/iowait %,
  page faults.
- `iostat -xz 2` — per-device throughput, IOPS, %util, await (the two NVMe +
  the md3 RAID1 device).
- `mpstat -P ALL 2` — per-core utilization breakdown (confirm even spread,
  no systematically idle cores).
- `pidstat -h 2` filtered to map_worker/merge_worker/orchestrate — per-process
  CPU%, context switches (voluntary vs involuntary — involuntary = preemption
  pressure), minor/major page faults.
- `perf stat -a` over representative windows — IPC, cache-miss rate, branch
  mispredict rate (system-wide, since workers are many short-lived processes;
  per-process `perf stat -p` is impractical at this process-per-unit scale).
- `/proc/pressure/{cpu,io,memory}` sampled — direct stall-time signal, the
  cleanest "is something hidden throttling us" check.
- Our own app telemetry: `event=column`/`event=heartbeat`/`event=steal` lines
  (already instrumented) — cross-reference timing against the system samples.

**Post-run:**
- Correlate phases (map-heavy vs merge-heavy vs spill-heavy columns, from our
  own telemetry) against the system-level traces — does iowait spike exactly
  during spill? Does run-queue length match core count during map? Any
  unexplained idle or stall not accounted for by our own model?

## Findings — probe run (maxn=24, heights 1-15, 2026-06-30)

Real production-shaped run: `scripts/perf_audit_run.sh`, rev `5fadde3`, dalby,
`--cores 80 --ram 1073741824 --unit-mult 4 --overlap-heights 15 --steal-grain
0.05`. **rc=0, wall=2283.3s (~38min)**, peak RSS 614MB, H15 the swept peak
(heights 1-14 finish fast, H15 dominates: cum_wall_s 7307→9057 of the 9057s
total cumulative-column-wall). Predicted ~30-40min from the maxn=22 calibration
— matched.

**Aggregate utilization: 79.3%** (cpu_s=144,889.6 / (wall=2283.3s × 80 cores)).
Cross-checked two independent ways — engine's own cpu_s/wall_s, and `mpstat`'s
mean idle% across all 1141 samples (20.1% idle → 79.9% busy). They agree. This
matches the launch plan's own prediction ("~80%, the endgame solo tail,
expected, bounded, not a problem") — confirmed empirically, not just asserted.

**Where the 20% idle lives: almost entirely in H15's tail, not spread evenly.**
mpstat idle% median across the whole run is 0.14% (cores busy nearly 100% of
the time for most samples) but p75 is 23.3% — a skewed distribution, not a
steady drag. The idle mass concentrates in H15's last ~10 columns (col 15-24),
where `map_units` falls below the 80-core pool (col=21: 92 units, col=22: 32,
col=23: 9, col=24: 0) as the frontier collapses toward the closed-form
boundary. This is structural, not a scheduling bug: there just isn't enough
independent work left to fill 80 cores once the frontier is down to dozens of
states. Matches the documented "solo tail" pattern — nothing new here, but now
measured directly rather than inferred from a(20).

**No disk pressure, no memory pressure.** `iostat` shows essentially zero
device activity for the whole run (occasional <103 IOPS writes, almost
certainly per-height/checkpoint output, not spill — RSS never came close to
the 1GiB `--ram` budget). `/proc/pressure/io` and `/proc/pressure/memory` were
**zero for every single sample** of the run (0/1141 nonzero blocks). `/proc/
pressure/cpu` (the "some" stall, i.e. runnable-but-not-running threads) was
nonzero in 576/1141 samples, peaking at avg10=4.9% — consistent with mild,
expected oversubscription pressure during the busy columns (unit_mult=4 means
more runnable work than 80 cores at peak), not a real bottleneck. This rules
out the disk and memory layers entirely for this run shape.

**Process-per-unit churn is real but cheap, and not disk-backed.** 10,365
distinct `map_worker` PIDs appeared in the 2s-sampled `pidstat` log (process
exec/exit churn from the process-per-unit design). Minor page faults averaged
~2024/s per sampled process-row (cheap: page-table setup, zero-fill, no I/O);
**major page faults averaged 0.003/s — essentially zero**, confirming the
process churn is not paying any real disk cost (binaries stay warm in page
cache; consistent with the zero iostat finding above). Involuntary context
switches averaged ~31/s per process — minor scheduler contention from 80
saturated cores, nothing alarming. **Conclusion: the process-per-unit
architecture's fork/exec overhead is not a hidden cost here** — it shows up as
minor-fault/scheduling noise, not as disk I/O or major stalls.

**Compiler/microarchitecture A/B (pre-run, see commit history): Clang base
beats GCC base by ~5%** (75.4s vs 78.9s mean, maxn=18 byte-exact A/B, 3 reps
each); **`-mcpu=native` was a wash-to-slightly-negative for both compilers** —
counter to the initial hypothesis, confirmed by measurement. Deployed
clang-base for this run. No further microarchitecture lever surfaced: dalby is
Neoverse-N1, no SMT, no NUMA, single socket — none of the usual x86-style
levers (NUMA pinning, hyperthread packing, turbostat C-state chasing) apply
here at all.

**Instrumentation gap — found, not fixed: `perf stat` hardware-counter
sampling produced zero data for the whole run** (`perf_stat.log` is empty
despite the pre-run access probe succeeding). Root cause: the sampling loop
used `timeout 30 perf stat -a ... -- sleep 30` — zero margin between the
timeout and the sleep duration. `perf`'s own startup/report overhead pushes
total wall past 30s, so `timeout` SIGTERMs it before it can print, **every
single iteration, silently** (the `|| true` swallowed the failure). This is a
script bug in `perf_audit_run.sh`, not a system limitation — confirmed `perf
stat -a` itself works fine standalone, both before and after the run. IPC /
cache-miss / branch-mispredict rates for the real workload remain
unmeasured this round; worth a `timeout 35`-style margin fix if a future
audit wants that data, but not worth re-running this probe solely to collect
it given everything else converged cleanly.

## Bottom line

No new performance lever found at the OS/hardware/microarchitecture layers.
The system-level traces **confirm** rather than contradict the existing
application-level model: utilization (79.3%) matches the engine's own
accounting exactly, the idle time is concentrated exactly where the "solo
tail" theory predicts (H15's shrinking last columns), disk and memory are
complete non-issues, and process-per-unit churn costs are real but cheap
(minor faults, not major). The compiler choice (Clang over GCC, no
`-mcpu` win) was the one genuine, measured finding from this audit, already
deployed. The Makefile `CXX ?= c++` / GNU Make built-in `CXX=g++` gotcha
(flagged in Hardware facts above) remains open — a repo-wide toolchain
decision for the user, not bundled into this probe's scope.
