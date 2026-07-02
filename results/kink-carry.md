# Kink Carry: cell-at-a-time king TM beats whole-column by an exponential factor

**2026-07-02.** `experiments/kink_tm/kink_tm.cpp`. The central find of the
Shaving Lambda research round.

## The idea

The production engine transfers a WHOLE COLUMN per step because king adjacency
needs the old NW cell that a cell-at-a-time boundary has already overwritten
(`core/transition.h` header comment — the only place the choice was ever
recorded; no design doc priced the alternative). Every published
polyomino/FLM transfer matrix (Jensen 2001 → Barequet–Ben-Shachar 2024) moves
the boundary ONE CELL at a time instead: per-state fan-out 2 (cell empty /
occupied), intermediate mixed boundaries canonicalized and merged after every
cell. The fix for the king NW problem is one extra byte of state: **carry the
single overwritten cell across the kink** (state = mixed boundary + carry
label + touch flags; the carry participates in the connectivity partition and
is stranding-checked as it drops off).

Whole-column pays `Σ_states viableMasks(state)` per column — masks/state was
measured ~1.4k at H=12 and grows exponentially with H. Kink-carry pays
`~2 × intermediateStates × H` per column, and intermediate states are a
**flat 3.6×** the column frontier (measured constant across H=4..14).

## Measured (serial, gympie; identical per-n counts at every size = gate)

| H | maxn | column-sweep time | kink time | **ratio** | col records | kink transitions | interm/frontier |
|---|---|---|---|---|---|---|---|
| 8  | 15 | 0.13s   | 0.04s  | **3.5×**  | 813K | 314K | 3.63 |
| 10 | 18 | 4.5s    | 0.41s  | **11.1×** | 19.8M | 3.1M | 3.63 |
| 12 | 22 | 175s    | 6.0s   | **29.2×** | 627M | 32.6M | 3.62 |
| 14 | 26 | (~5000s est) | **95s** | ~55× (extrap) | — | 326M | 3.60 |

Ratio grows ~2.7× per +2H — it is the masks-per-state exponential being
deleted. Extrapolated to H16 (the height that is 68–91% of every recent
record run): **~150–200× on map compute**.

**Production-data validation:** T(20..22,12) at maxn=22 and T(24..26,14) at
maxn=26 match `results/ns_a27/perheight/h{12,14}.out` exactly — the kink TM is
an INDEPENDENT transition implementation (per-cell union-find + carry
stranding vs per-column union-find), validated against the production engine.
H=14/maxn=26, a full production-shape height, ran in **95 s on one core**.

## Why this is a base change, not a constant

Per-term compute growth of the current engine is ~4.4× = state growth (~2.42)
× masks-per-state growth (~1.8). Kink-carry's per-state work is `2·H·3.6`
— polynomial in H — so per-term compute growth drops to **~the state growth
itself, ~2.5×**. In b^n terms: b ≈ 4.4 → b ≈ 2.5.

Second, independent win: **the shuffle collapses.** Intermediate stages live
in RAM (3.6× frontier); only end-of-column states leave a worker. Per-column
record volume drops from `Σ masks` (627M at H12; the 126 GB spill peak at
a27 H16) to ~frontier-sized (~1000× less). Combined with the P_k treadmill
capping top heights at H16–18, the whole computation becomes RAM-resident
(D_16 ≈ 2.1M states measured at a27; D_18 ≈ 13M extrapolated) — the
sort/spill/merge machinery and its zstd pipeline become unnecessary for
frontier terms.

Bonus: an engine built on this kernel doubles as the **independent
reimplementation** that the a(23)-validation plan says is the only closure
for the shared-enumeration-bug gap ([[a23-readiness-and-validation]]).

## Rough reach implication

a29's dominant H16 ≈ 10^6 cpu-s whole-column → ~10^3–10^4 cpu-s kink (one
core, minutes-to-hours). a(30)–a(33) each drop from days to hours on dalby;
the practical ceiling moves out several terms (new wall = frontier RAM at
D_H ~ 2.6^H with H ≈ n/2 − const, plus u128 row bandwidth).

## Caveats / open engineering questions

- Serial probe only; parallelization needs per-stage sharding (H barriers per
  column instead of 1, but per-stage volume is tiny) OR per-worker private
  stage DPs over sharded sources (loses cross-shard intermediate merging —
  bounded duplication, needs measurement).
- Probe stores full count rows (maxn+1 u64); production wants ranged rows +
  u128. Constant-factor bookkeeping, no blocker visible.
- The 3.6× intermediate factor was measured at n/H ≈ 1.8; re-measure at other
  budget ratios before trusting it universally.
- Correctness bar for any record run: gate a(1..18) vs known + full a(20)
  --compare byte-match + a21-27 vs banked results, per standing rules.
