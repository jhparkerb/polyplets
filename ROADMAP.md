# Polyplets project — open threads and dependencies

Status snapshot of the remaining work, what each thread produces, and how they
depend on each other. (Done feeders: #18 perimeter cross-check, #22 mutation
testing, #23 growth λ/θ, #26 fixed-height GFs + the lifetime-3 / atom analysis.)

## The threads

**#24 — Hole-stratified counts (in progress).**
Classify polyplets by number of enclosed holes (hole-free, by-#holes), in both
background conventions (4-connected = topological dual, primary; 8-connected =
companion). Exact and validated to n=14 via the generator's per-animal flood
fill; cross-checked against A006724/A389193 on polyominoes. All four sequences are
absent from OEIS. Capped at n=14 because the flood is O(bbox) per animal × a(n).
→ Feeds #28 (which removes the cap) and #25.

**#28 — Deeper holes + hole generating functions.**
Carry hole count *inside* the column transfer matrix via the Euler characteristic
(holes = 1 − χ for a connected animal; χ accumulates by local 2×2 bit-quad
increments — a function of the column pair, so it fits the whole-column sweep).
Two deliverables from one build: (a) the hole-stratified counts extended to n=19
(matching the main count's reach), and (b) marking holes with q gives the
bivariate G_H(x,q), whose [q^k] slices are *rational GFs for every fixed
(height, #holes)* — closed forms valid for all n. The small-/mid-H bivariate GFs
run on gympie now; full n=19 stratification is ~60–75 GB (ayr-scale). Must be
cross-validated against the n≤14 flood data; the bit-quad/border accounting is the
correctness risk.
→ Produces hole sequences (to n=19) and hole GFs; feeds #25 and #17.

**Status (2026-06-18): primary deliverable (a) built + validated; design proven.**
The Euler/hole accounting is isolated and unit-tested in `cpp/tma/euler.h`
(+ `tests/euler_unit.cpp`, `make gate-euler` — 191k random images + the
diamond/ring/pinch battery). Convention pinned: PRIMARY = 4-bg holes via the
8-fg Euler number (the −2·QD branch; my first plan draft had the sign backwards).
The sweep `cpp/tma/sweep8_holes.h` mirrors `sweep8_perim.h` (own state store,
reuses the validated transition/prune, **does not touch the a(n) path**); driver
flag `tma square8 N --holes [--per-height] [--kmax K]` (default kmax=maxn, safe).
VALIDATED: byte-identical to `g2 --holes` (n≤11) and to the saved flood
`results/holes_n14.txt` (n≤14, incl. the max-hole animals: 6-in-12, 7-in-14);
sum-invariant = A006770 (n≤12); per-height sums to flat. The flood's n≤14 cap is
removed in principle (the engine reaches past it; a clean n≥15 production run is
still pending — it's slow single-threaded under the a(20) contention, tune --kmax
down to ~10 and thread it). Full design + file-by-file map in
`plan-transfer-matrix-holes.md`.
REMAINING for #28: (i) n≥15 production run for the new hole terms (big n=19 still
ayr/#20, ~60–75 GB); (ii) companion 8-bg convention (needs a 4-adjacency
component tally — deferred); (iii) deliverable (b) the bivariate hole GFs via
`--holes --per-height` slices → `gf/recover.py`; (iv) fold a fast hole check into
`gate_tma.py`. NOTE: the live `build/tma` is the OLD pre-holes binary still
running a(20) — rebuild (`make build/tma`) to get `--holes` once a(20) frees it,
or use a separate build; `build/tma_holes` was the throwaway test binary.

**#25 — OEIS submission prep.**
Draft b-files + descriptions + cross-references for the new sequences: OneSided
polyplets (no OEIS sequence exists), the hole sequences (4-/8-conn, hole-free and
by-count), and the lifetime-3 byproducts (atom degrees 1,2,4,9,29,68,…; orders
1,3,7,15,42,…). Includes novelty re-checks and provenance. **Nothing is submitted
without explicit signed orders (24-h cooling-off).** This is the convergence point
where the other threads' new sequences land.
→ Feeds #17.

**#27 — Cross-n sampling / scaling study.**
The uniform sampler gives the *typical* structure at one size (n=19: sparse,
branchy, ~10 rook-pieces, 28% holed). This thread draws uniform samples at several
sizes and measures how that structure *scales*: radius-of-gyration size exponent,
decay of the rook-connected fraction, growth of hole density. Independent,
gympie-friendly, runnable now.
→ Feeds #17 (the scaling section).

**#21 — Extend + reproduce all three sequences.**
Push a(20)+ for fixed/free/one-sided polyplets and confirm each with a second
method on a different architecture (cross-ISA decorrelation). a(20) is partway
done (single-method candidate). The cross-ISA reproduction is the remaining
confidence step. **Needs ayr (busy until ~June 27); dalby off-limits.**
→ Produces more terms (extended b-files); feeds #25 and #17.

**#19 — Benchmark engines + reach projection.**
Measure each engine's real throughput/memory and project how far each can push
(a(n) and the GF heights) on available hardware. Largely characterized already
(complexity.md, scaling.md); the open piece is a clean defensible projection.
→ Decides whether #20 is worth building; informs #21, #28.

**#20 — Out-of-core transfer-matrix backend.**
The transfer matrix is RAM-bound (≈12.5 GB at a(19)). An on-disk/mmap state store
breaks that wall, unlocking a(22)+ and relieving the memory pressure of full-n=19
hole stratification. The designed-to-be-replaced state store makes this a
drop-in. Premature until #19 says it's worth it.
→ Enables deeper #21 and the RAM-heavy half of #28.

**#17 — Paper + public repo drop (LAST).**
Fold everything into the write-up: a(19) + free/one-sided, hole sequences, the
fixed-height GFs and lifetime-3 (honestly weighted — see results/lifetime3-proof.md),
the growth estimate, and the sampling/scaling portrait; then the GitHub drop.
Strictly after the OEIS drafts (#25), since the paper references those entries.

## Dependency graph

```
LEGEND:  A --> B  = A feeds / enables B          ((ayr)) = needs ayr (~Jun 27)

  -- start-now on gympie ------------------------------------------+
  |  #27 sampling-scaling --------------------------------------+  |
  |  #28 holes (bivariate hole-GFs, small H) --+               |  |
  |  #19 benchmark/reach --> #20 out-of-core --+               |  |
  +---------------------------------------------+--------------+--+
                                                |              |
            #20 (RAM wall broken) --------------+              |
                                                v              |
   ((ayr)) --> #21 extend a(20)+, cross-ISA --> more terms     |
   ((ayr)) --> #28 full n=19 holes  <----------+               |
                          |                                    |
   #24 holes (done<=14) --+                                    |
                          v                                    |
             hole seqs + hole GFs ------+                      |
   #26 GFs (done) --> atom-degree/order -+                     |
   #21 --> extended b-files -------------+--> #25 OEIS draft    |
                                         |          |          |
                                         +----------+          |
                                                    v          v
                                              #17 PAPER  <-----+   (LAST)
```

## Leverage points & critical path
- **#19 → #20** decides the out-of-core build; **#20 is the multiplier** — it
  unlocks both deeper a(n) (#21) and the RAM for full n=19 holes (#28).
- **ayr (~June 27)** gates the heavy compute (#21 cross-ISA + a(20)+, full-n=19
  #28). Until then, gympie runs the light independent work: **#27**, the **small-H
  hole-GF prototype** (#28's gympie half), and **#19**.
- **#25 is the convergence point** — it consumes hole sequences (#28),
  atom-degree/order sequences (#26, done), and extended b-files (#21); then
  everything plus #27's scaling flows into **#17, strictly last.**
- **Critical path to publication:** #19 → #20 → (ayr) #21/#28 → #25 → #17, with
  #27 and the gympie-side hole prototype running in parallel throughout.
