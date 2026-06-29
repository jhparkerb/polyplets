# a(23) launch checklist

Per `docs/job-checklist.md`. Staged 2026-06-29. **Not launched** — gated on the
a(20) validation landing (correctness gate + cost calibration) and an explicit go.
Launch script: `scripts/dalby_ns_a23.sh`.

## 1. Predicted cost — **calibrate from the a(20) validation, do not launch blind**

The a(20) validation now finishing on dalby is a *clean fixed-binary* run, so its
wall/RAM/disk are the calibration point a(23) extrapolates from.

- **Wall:** compute model is ~4.4×/term (`memory: reach-scaling-and-resourcing`).
  a(20)→a(23) is 3 terms ⇒ **~85× the clean a(20) wall.** Fill `clean_a20_wall`
  from the validation log; expect a(23) on the order of **several days**. (The
  35.8 h a(21) figure is NOT a basis — it brute-forced H21, the A1 incident.)
- **Peak RAM:** engine is disk/spill-bound, RAM scales slower than compute. a(21)
  peaked ~80 GB; budget **~120 GB** for a(23) and confirm against the a(20)
  validation's measured peak. dalby = 128 GB ⇒ thin headroom; tune `RAM_SPILL`
  down if it crowds.
- **Peak disk:** a(21) ~15 GB spill; a(23) is much larger — **provision ≥300 GB
  free** on the spill volume and re-estimate from a(20) spill × growth.

→ Before launch: read the a(20) validation log, write the three measured numbers
here, recompute, and only then proceed.

## 2. Fit the budget

- **Target: dalby** (128 GB / 80 core) — the only home box that fits; gympie
  (24 GB) and ayr (78 GB) are too small for a(23)'s RAM/disk.
- Sum against PEAK of what's already on dalby. The a(20) validation must be
  **done** (it's the gate) before a(23) takes the box — they do not co-reside.
- Disk headroom is the real constraint here, not cores — verify free space on the
  spill volume before launch.

## 3. Saved, self-describing in-repo script

`scripts/dalby_ns_a23.sh` — committed, header states purpose / machine / cost /
resume / kill. No `/tmp`, no heredoc, no one-liner.

## 4. Provenance + observability — clean, current rev

- Binary `build/ns/orchestrate` MUST be **clean** (no `-dirty`) and **contain the
  diagonal injection (k≤4) + work-stealing + A1 fix.** After confirming HEAD, on
  dalby: `git pull && make build/ns/orchestrate build/ns/map_worker
  build/ns/merge_worker`, then read `--version` and confirm GIT_REV == HEAD.
- The **A1 incident** is the precedent: a clean-but-*stale* binary silently ran
  the old brute-force path. A clean stamp that doesn't match HEAD-with-the-fixes
  is the same failure in a clean suit.
- `--per-height-out` captures every h<H>.out for post-hoc validation; the binary
  emits start/heartbeat/done with a self-computed ETA to `run.log`.

## 5. Recoverable

- `--checkpoint POLYCKPT --checkpoint-every 900`; resume via `RESUME=1
  scripts/dalby_ns_a23.sh`. A kill or lost conflict costs one column, not the run.
- `--overlap-heights 1` deliberately: >1 disables mid-run checkpointing, which a
  multi-day run cannot afford.

## 6. Recorded — purpose legible at a glance

Add to HANDOFF on launch: *"dalby: a(23) frontier run (maxn=23, rev <X>), tmux
`<session>:a23`, waiter <id>. a(21)/a(22) free byproducts. Result tier: computed,
pending independent certification."* Update PROVENANCE on completion.

## Validation plan for the result (a(23) has no oracle)

- a(1)…a(21) recomputed in the same sweep must match known values exactly
  (per-height files vs `results/ns_a21/`).
- a(22), a(23) growth ratios inside the [3.9, 7.2] band; ladder-consistency.
- Novel high heights are single-source — same caveat as a(21): **computed,
  pending mod-p shadow or independent reimplementation** before OEIS-final.

## Open decisions for launch time

- **Whole-dalby vs height-split (dalby+ayr).** Script is whole-dalby (simple,
  recoverable). A `--heights` split (`scripts/ns_heightsplit.sh`) could cut wall
  but adds coordination and complicates resume — decide based on the calibrated
  wall (a multi-day estimate may justify the split).
- **`RAM_SPILL` tuning** from the a(20) validation peak RAM.
