---
# Frontier idea oq2 — M4 cross-arch checkpoint portability
*Source: docs/scheduling-design.md §"Open empirical questions" #2 (and §Survivors: M4 checkpoint-migration, M5 distributed single-height sweep). Related: cpp/tma/checkpoint.h (the format under test), tests/gate_tma.py M/O/P (byte-identical resume gate), docs/frontier/03-sort-transition-engine.md + 02-out-of-core-spill.md ("one bet" — M5 distribution rides the same restructure).*

## Idea
A height's intra-height checkpoint (checkpoint.h: header + nEntries·(Sig+counts-row) + accumulator + crc32) written on one box can be loaded and resumed on a DIFFERENT architecture. That single property unlocks **M4 migration** (move the sticky pole from box to box) and **M5 distributed single-height sweep** (ship state over the network). Attacks the **cross-box imbalance** of the sticky-height atom — the one lever the single-box engine cannot touch once a heavy height dominates the makespan.

## Why it might matter here
The height is the **coarse cross-box atom** (scheduling-design §"unifying model": columns are sequential, the frontier lives on the box running that height). Once the pole H=N−1 dominates (~2.4×/height geometric), the only way to rebalance gympie/ayr/dalby is to move or split THAT height — M4/M5. Both are gated on this one fact: is the on-disk state arch-portable? checkpoint.h *claims* logical-set portability (read via `for_each`, MT re-routes by `hashSig & (S-1)`), but the format is little-endian-stamped (`byteorder=1`, L120) and never tested across a real endian/layout/struct-padding boundary. dalby (aarch64) and ayr (x86-64) are the exact pair that proves or breaks it.

## Kill-test — quickest path to INFEASIBLE
**Question it answers:** does a checkpoint written on dalby (aarch64) resume on ayr (x86-64) to a BYTE-IDENTICAL final count vs a same-box run?
**Setup:** pick a small/cheap height so the round-trip is minutes, not days (e.g. `tma square8 14 --only-height 13 --checkpoint DIR`, TMA_CKPT_SECS small so it actually writes). On dalby: run to a mid-height checkpoint, kill via the existing `TMA_CKPT_KILL_AT_COL` hook (checkpoint.h L206). `scp` DIR/ckpt to ayr. On ayr: resume from the copied ckpt to completion. Baseline: a full same-box run on each. (Rebuild on each box first — stale-binary footgun, per the rebuild-remote rule.)
**Measure:** the resumed-on-ayr final accumulator vs (a) the same-box ayr run and (b) the dalby same-box run — demand all three byte-identical. Also: does `tmaCkptLoad` even return `Loaded` (not `Refuse`) across the arch boundary?
**NO-GO (for cheap migration) if:** resume returns `Refuse`/fails to load, OR the final count differs by a single bit. That means the serialization is endian/layout/Sig-byte-order/hash-order dependent and an arch-portable format must be built FIRST — which moves the M4/M5 effort estimate up (a new bet, not a free reuse).

## Substantial-improvement ladder (must clear ALL)
- **C1 — byte-identical cross-arch resume** — dalby-written ckpt resumed on ayr equals the same-box count to the bit (the gate's M/O/P invariant, now across ISAs). The decisive pass.
- **C2 — checkpoint write+read cost <~ a few % of the height's wall** — time a save+load cycle vs the height's total; cheap enough to checkpoint at the production cadence without taxing the sweep.
- **C3 — format stable enough to ship over the network** — same ckpt file resumes correctly after an scp round-trip with no fixups (no host-local pointers/paths in the payload); this is the property M5 (distributed sweep) needs, beyond M4's local copy.
*Per-idea bar:* unlocks cross-box migration/distribution of the sticky pole — the ONLY lever for the a(24)+ imbalance the single-box engine can't address. A pass means M4 is cheap (copy+resume); a fail re-prices M4/M5 to include an arch-portable serialization.

## Composition / foreclosures
- **Gates M4 AND M5** — both sit in §Survivors; neither proceeds at its current estimate until this passes.
- **Composes with the "one bet"** (scheduling-design §"One bet"): M5's distribution rides the SAME sequential/sort/batched restructure as out-of-core (02) and the sort engine (03) — a portable checkpoint is the wire format that restructure ships. Build the portable format once, it serves migration, distribution, and disk-spill.
- **Forecloses I6** (GPU/SIMD/new decomposition, §Excluded DEFER): heterogeneous on-device state can't migrate or distribute, so I6 and M4/M5 are mutually exclusive — confirming portability strengthens the case to keep state CPU-homogeneous.
- **Independent of** compression (01) and verification (06): they observe/shrink state; this moves it.

## If it passes: effort & where it lands
**S to run the kill-test** (a small two-box round-trip, mostly scp + two resumes) — **ESTIMATE**. If it PASSES: M4 migration is a thin driver wrapper around the existing checkpoint.h (S–M ESTIMATE) and M5 becomes a real candidate. If it FAILS: an arch-portable serialization (fixed-endian Sig + canonicalized row order) is a prerequisite (M ESTIMATE) that re-prices both. Engine: cpp/tma/checkpoint.h, tests/gate_tma.py (add a cross-arch resume case). ROADMAP: §Survivors M4/M5; informs #32 (meet-in-the-middle scheduling) by making the pole movable. **Effort is a t-shirt size, not a wall-clock — no ETA fabricated.**
---
