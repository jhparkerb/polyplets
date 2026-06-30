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
