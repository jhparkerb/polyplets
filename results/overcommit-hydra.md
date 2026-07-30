# Overcommit Hydra — four a(40) OOM deaths in one day (2026-07-25)

Thread name: **Overcommit Hydra** — every fix revealed the next head. All
four deaths at ~1-1.5h in, at maxn=40's peak height co-residency
(H19+H20+H21 rounds overlapping). Kernel OOM killer each time
(journal-confirmed on #2; killed the tmux server AND jasonp's ssh-agent
twice). Box: dalby, 125GB RAM, 80 cores.

## The four heads (each measured, each fixed or exposed)

| # | proximate cause | evidence | fix (commit) |
|---|---|---|---|
| 1 | /dev/shm admission TOCTOU: N concurrent rounds each passed a point-in-time statfs check | tmux+agent dead, RAM scrubbed | reservation + 24GB floor (f9d485f) |
| 2 | RAM co-budget: 80x1GiB worker budgets + ~38GB admitted shm + UNBOUNDED idle zstd pools (80 workers x ~640 readers x ~200KB) | journal oom-kill; 270 fallbacks logged = reserver working | pool cap 64, floor 40GB, --ram 768M (6697c04) |
| 3 | merge reader army: 80 workers x ~640 open compressed readers x ~0.7MB grown buffers = ~35GB round-periodic spikes | mem.log: used 95->126.6GB swings, shm only 3-10GB | 64KB reader-fill cap, unit-mult 4, 72 cores (7abd27d) |
| 4 | worker OVERHEAD ~0.5GB each ON TOP of budget (x72 = ~90GB) + unit-mult 4 DOUBLED per-unit slices -> spill-thrash (processed=0 heartbeats) + orchestrate RSS growing 2.8->4.4GB in minutes | mem.log v2 top-proc: map_worker 1.25GB, orchestrate 4.4GB | STOPPED per jasonp — design below, not another blind relaunch |

## What the day actually established

- The levers (frontier zstd + tmpfs map outputs) are correct and validated
  at scale — a(39): 11.1h vs a(38)'s 15.8h one term lower, chain-exact.
- maxn=40 with FULL overlap does not fit 125GB. The budget identity:
  workers x (spill budget + ~0.5GB overhead) + shm + reader army +
  orchestrate(grows!) + page cache floor. At 72-80 workers the first term
  alone is 90-120GB. No knob-twiddling closes this while all heights run
  concurrently — three attempts proved each knob just moves the spike.

## The design that fits (tomorrow's plan): PHASE the job

The engine already supports height subsets (--heights, used for the
a(36) ayr/dalby split). Replace one all-heights run with sequential
phases in dalby_term.sh for N>=40:

  Phase A: --heights 3..19  (cheap, high overlap fine, 80 cores, 1GiB)
  Phase B: --heights 20     (solo, ~48-64 cores, 1GiB budgets)
  Phase C: --heights 21     (solo, ~48 cores x 1.5GB RSS ≈ 72GB — safe
                             by construction; pole is disk-bound at
                             eff_cores ~14, so fewer cores cost little)

Single-height phases bound RAM at ONE height's working set — the
co-residency spike ceases to exist structurally. Cost: lose overlap's
merge/map interleave hiding (~+20-40% wall on the cheap phases, ~nothing
on the pole, which dominates). Combine/validation unchanged (perheight
accumulates across phases; resume per phase).

Open items for the implementation pass:
- ~~orchestrate's RSS growth (4.4GB and climbing when killed)~~ **CLOSED
  2026-07-30 (AUDIT-2026-07-30 O6).** Verdict: **no leak.** The suspected
  per-round accumulation is not there — telemetry is streamed to disk
  rather than retained, and every pool (bounds, cuts, worker/zstd
  contexts) is capped. The mechanism is GOGC without a ceiling:
  cmd/orchestrate sets GOGC=1000 to stop the ~8000 pointless GC cycles
  the default caused, but GOGC is a *ratio*, so the heap is allowed to
  reach ~11x live before a collection — a tens-of-MB live heap becomes
  GBs of RSS with nothing wrong. Fix: keep GOGC=1000, add
  `debug.SetMemoryLimit` (default 4 GiB, `POLY_GO_MEMLIMIT_GB` override,
  0 = off) so the ratio has a bound. Go's soft limit makes the collector
  work harder near the limit rather than failing, so an under-sized limit
  costs CPU, never correctness. Gated by `orchestrator/gomemlimit_test.go`.
- Worker overhead audit: what is the ~0.5GB non-budget RSS per worker?
  (arena retention, zstd contexts, reader buffers, request scratch.)
- Restore --ram 1GiB + unit-mult 8 for the phased config (the 768M +
  unit-mult-4 combination thrashed: bigger slices, smaller budgets).

## Collateral damage log

- jasonp's dalby ssh-agent OOM-killed twice (re-add needed after #2 and
  again after... check before next github pull; bundles work meanwhile).
- ~3h of a(40) compute lost across four attempts (height-boundary
  checkpoints; no completed height survived any attempt).
- a(40) run dir + checkpoint preserved; resume remains valid.
