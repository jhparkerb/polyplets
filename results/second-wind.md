# Second Wind — a(37) feasibility push (branch `second-wind`, 2026-07-22)

Goal: improve the transfer-matrix engine until a(37) is comfortably feasible
on the hardware at hand. Context at start: jasonp travelling with gympie;
ayr unreachable for the duration; dalby reachable but ssh-agent not
forwarded into the session (deploy/benchmark there deferred to a
documented checklist, below).

## What landed (two commits + this record)

### 1. P_17 wired (`977f86a`) — a(37)'s top real height drops to H19

`scripts/derive_pk_fast.py 17`: shared symbols pinned by the validated
P_9..P_16 fits; only a17,b17 fit, from T(35,18) + T(36,19) — the two
smallest in-onset points (onset n≥2k+1=35). Leading coeff 25^17/17! and
k!-integrality confirmed. Wired as `diagCoeffTable[17]` +
`diagonalStripValid` k≤17, gated red-first by `diag_p17_test.go`.

**Correction to HANDOFF's earlier parenthetical** ("fit T(34,17)+T(35,18),
holdout T(36,19)"): T(34,17) is the n=2k **out-of-onset** point and was
checked to NOT lie on P_17 — sharp onset, consistent with every lower k.
It is neither a fit point nor a holdout. Consequently P_17 has **no
independent holdout until a(37) sweeps H20 real** (the strict route's
purpose, unchanged); its certification meanwhile rests on the proven grand
form, the same footing every P_k's *shape* now has.

### 2. Block-buffered run-file I/O (`912e071`) — 3.4x wall / 3.8x cpu at gympie scale

Profiling the persistent workers (macOS `sample`, H15/maxn30 bench, 10
cores) found ~90% of map/merge **busy** samples inside stdio:
`RunFileReader::next` issued one locked `fread` per FIELD — worst case one
per varint BYTE (~120 calls/record) — and `RunFileWriter::append` one
`fwrite` per field. The kink transition itself was ~5% of busy time.

Fix (byte-format identical, all internal to `core/runfile.h`): writer
assembles each record in a stack buffer and emits once into a 256KB block
buffer (one `fwrite` per block; flushed before `finalize`'s fseek and on
destruct); reader serves plain reads from a 256KB block buffer (CRC folded
at consumption; trailer read unfolded; buffer dropped on `seekToKey`) and
compressed reads from a decompressed block buffer (killing the per-byte
`ZSTD_decompressStream` calls too).

Measured (`scripts/gympie_bench_phase.sh`, H15/maxn30, 10 cores, production
flags): **wall 335.1s → 99.8s (3.36x), cpu 2899 → 764 cpu-s (3.8x)**.
Validation: full `make ns-gates` green (spill-zstd, resume-boundaries,
parallel, verify corruption-detection, ASan) + a fresh full a(20) run
`combine --compare` PASS (runs/second_wind_a20).

Post-fix profile is balanced (reader ~303 / writer ~293 / transition ~150 /
sort+moves ~250 samples; per-unit file opens now barely visible) — no
dominant slice left; further map-side micro-optimization parked.

## a(37) cost with this branch (prediction, to be re-measured on dalby)

Basis: a(36) H19 pole = 11810.4s = 3.28h on dalby (varint engine,
pre-buffered-I/O), whole-height eff cores ~33.7/80. At fixed H the frontier
is nearly flat per term (a35-plan); a37-H19 adds one count entry per window
and one column → ~+10% pre-buffered ≈ **3.4–3.7h pole**.

The gympie 3.4x does NOT transfer 1:1 to dalby (glibc stdio locking is
cheaper than macOS's; the pole also has disk-write and straggler-tail
components the fix doesn't touch). Honest range: **1.5–3x on the pole** →

- **Trusted route** (P17 wired, real H3–H19, `dalby_term.sh 37`):
  pole **~1.2–2.5h**, low heights overlapped ≈ free → wall ≈ pole.
- **Strict route** (adds real H20 = the P17 certification point):
  `--max-diag-k 16` (new flag, gated by `maxdiagk_test.go`) forces the
  H20 strip back to a real column sweep despite P17 being wired; the swept
  T(37,20) is then compared against the P_17 closed form as its first
  independent holdout. H20 ≈ 2.1–2.2x H19 ≈ 7–8h pre-buffered →
  **~2.5–5h** with the I/O win.

Either route is comfortably inside a day on dalby alone; both are cheaper
than a(36)'s actual run was. ayr is not needed (dalby_term.sh is
dalby-solo by design); gympie can rerun small-n validation independently.

## dalby deployment checklist (blocked only on ssh-agent access)

1. `git push` the branch; on dalby: fetch, checkout `second-wind`,
   `make -j ns-gates && make install` (rebuild-remote rule — a stale
   binary silently ignores all of this).
2. Re-run the standard bench A/B: `scripts/bench_util.sh buffered-h15 30 15`
   vs the recorded post-Even-Keel baseline 140.9s (docs/
   full-utilization-redesign.md D5) → pins the real dalby I/O-win factor.
3. `scripts/dalby_term.sh 37` (tmux window, foreground, per job checklist);
   its built-in validation covers b-file n≤20 + banked chain to a(36).
   Strict-route H20, if chosen, per the H20 note above.

## Considered and NOT done (with reasons — don't re-pitch)

- **Resurrect kink-sharded / redesign branch**: measured dead and
  deliberately deleted on master 2026-07-09 (S^0.7–0.8 duplication,
  unstealable shards); Even Keel (balanced cuts) is already in master and
  in the a(36) baseline. All three "unmerged perf branches" in MEMORY
  (`tm-hotpath-optim`, `redesign`, `kink-carry`) turned out ALREADY merged
  or superseded — memory notes were stale.
- **Sub-record interrupt / more steal tuning**: three scheduler fixes
  measured zero effect on the dominant column; tail effectively
  unsplittable (results/utilization-fix-and-ceiling.md).
- **4-bit sig pack**: post-varint the key is ~20% of record bytes and spills
  are zstd'd anyway; ~10% bytes for real format risk. Parked.
- **Sort/dedup micro-opts**: post-buffering profile shows no dominant
  slice; terminal-sort investigation already banked. Parked.
- **tmpfs two-media revival**: varint (−60% writes) plausibly shrinks the
  H19 working set from a35's ~150–200GB to ~60–80GB, which would fit
  dalby's 125GB RAM and re-enable the measured ~4x pole trick — but the
  a35 attempt OOM'd and killed the tmux server, so this stays OPTIONAL:
  measure the a37-H19 run-dir footprint (du during the NVMe run) before
  ever trying it. The NVMe route is already feasible without it.
- **New algorithms / fresh axes**: the design space is measured-closed
  (connectivity wall; docs/full-utilization-redesign.md Part 4 coverage
  proof; algorithmic-levers-dead memory). Remaining speed is engineering,
  which is what this branch shipped.
