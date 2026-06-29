# a(23) launch checklist

Per `docs/job-checklist.md`. Staged 2026-06-29. **Not launched** — gated on the
a(20) validation landing (correctness gate + cost calibration) and an explicit go.

**Shape: a disjoint height-split across dalby + ayr** (a(n)=Σ_H T(n,H)), via
`scripts/ns_heightsplit.sh` on each host with non-overlapping `--heights`, then
`build/ns/combine --require-cover --compare`. Disjoint = no duplicated work, min
wall (frontier rule); cross-ISA byte-validation is deferred until we have a number.
Wall ≈ **max(dalby subset, ayr subset)**, so a balanced split roughly halves the
whole-dalby time.

## 1. Predicted cost — **calibrate from the a(20) validation, do not launch blind**

The a(20) validation finishing on dalby is a *clean fixed-binary* run; its
per-height `cost_profile.tsv` + measured RAM are the calibration point.

- **Wall:** ~4.4×/term (`memory: reach-scaling-and-resourcing`). a(20)→a(23) is 3
  terms ⇒ ~85× clean a(20) on one host; the split cuts that toward ~½ if balanced.
  Fill `clean_a20_wall` from the log; expect **a couple of days** post-split.
  (The 35.8 h a(21) figure is NOT a basis — it brute-forced H21, the A1 incident.)
- **Peak RAM (per host):** disk/spill-bound, scales slower than compute. The split
  is sized so each host's *tallest assigned swept height* fits its RAM — see §2.
- **Peak disk:** a(21) ~15 GB spill whole; per-host subsets less, but **provision
  ≥200 GB free** on each spill volume and re-estimate from a(20) spill × growth.

→ Before launch: read the a(20) `cost_profile.tsv` + RAM, set the height boundary
(§2), write measured numbers here, then proceed.

## 2. Fit the budget — height assignment

The proven diagonals (k≤4) inject the **top 5 heights H=19..23** with no sweep, so
the expensive *swept* heights are the mid-tall band (~H=13..18); the tallest swept
height sets a host's RAM peak.

- **ayr (78 GB / 32 core):** the **low/mid heights that fit 78 GB** — tentatively
  `--heights 1-12` (cheap individually but many; real aggregate work). Confirm the
  largest assigned height's frontier fits from the a(20) per-height RAM.
- **dalby (128 GB / 80 core):** the **tall swept heights + the formula heights** —
  tentatively `--heights 13-23`. H=19..23 are near-free (injected); H=13..18 are
  the cost.
- Boundary is **calibration-driven**: pick it to (a) keep ayr's tallest height
  under ~70 GB and (b) balance wall between the hosts, from the a(20) profile.
- `--require-cover` at combine asserts 1..23 covered exactly once (no gap, no
  overlap).

## 3. Saved, self-describing in-repo scripts

`scripts/ns_heightsplit.sh` (generic, now carries optional `STEAL_GRAIN`). Exact
invocations (REF_PROFILE = a(20) `profile.tsv` to drive the live ETA):

```
# dalby (native build):
scripts/ns_heightsplit.sh 23 13-23 80 4 ~/runs/ns_a23 4 ~/runs/ns_a20/profile.tsv 0.05
# ayr (cross-compiled orchestrate — see §4):
scripts/ns_heightsplit.sh 23 1-12  30 1 ~/runs/ns_a23 4 ~/runs/ns_a20/profile.tsv 0.05
# combine on one host after both finish:
rsync -a dalby:~/runs/ns_a23/perheight/ ~/runs/ns_a23/all/
rsync -a ayr:~/runs/ns_a23/perheight/   ~/runs/ns_a23/all/
build/ns/combine --in ~/runs/ns_a23/all --maxn 23 --require-cover --compare
```

Run each in a tmux window of that host's single session, foreground + tee'd, with
a `tail --pid <orchestrate-pid>` waiter.

## 4. Provenance + observability — clean, current rev on BOTH hosts

- Binary must be **clean** (no `-dirty`) and **contain diagonals (k≤4) +
  work-stealing + A1 fix** on each host. The **A1 incident** precedent: a
  clean-but-*stale* binary silently ran the old brute-force path.
- **dalby:** `git pull && make build/ns/orchestrate build/ns/map_worker
  build/ns/merge_worker`; read `--version`, confirm GIT_REV == HEAD.
- **ayr (`memory: ayr-newengine-crosscompile`):** Go 1.19.8 is too old — build
  `orchestrate` on **gympie** (`CGO_ENABLED=0 GOOS=linux GOARCH=amd64`) and copy
  it over; build the C++ workers (`map_worker`,`merge_worker`) **native on ayr**.
  Re-read the deployed `--version` after copying (stale-binary tell: nlwp=1).
- `--per-height-out` captures every row for validation; binary emits
  start/heartbeat/done + self-computed ETA to the log.

## 5. Recoverable

- Each host checkpoints its own subset (`--checkpoint POLYCKPT
  --checkpoint-every 900`); resume by re-running its `ns_heightsplit.sh` line (it
  resumes from POLYCKPT). A kill costs one column on one host.
- `ns_heightsplit.sh` keeps `--overlap-heights` at the default 1 — overlap>1 would
  disable mid-run checkpointing, unaffordable for a multi-day run.

## 6. Recorded — purpose legible at a glance

HANDOFF on launch, one line per host: *"dalby: a(23) heights 13-23 (rev <X>), tmux
`<sess>:a23`, waiter <id>; ayr: a(23) heights 1-12 (rev <X>), tmux `<sess>:a23`,
waiter <id>. a(21)/a(22) free byproducts. Tier: computed, pending certification."*
Update `results/ns_a23/PROVENANCE.md` on combine.

## Validation plan (a(23) has no oracle)

- `combine --compare` byte-checks the **a(1)…a(21) prefix** against
  `fixtures/b006770.txt`; a(22), a(23) are the new outputs.
- a(22)/a(23) growth ratios inside the [3.9, 7.2] band; ladder-consistency.
- Novel high heights are single-source (same caveat as a(21)): **computed,
  pending mod-p shadow or independent reimplementation** before OEIS-final.
