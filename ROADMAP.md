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
DONE since: (iv) fast hole check folded into `gate_tma.py` (check H, square8 n≤11
vs the flood oracle); (iii) deliverable (b) the **bivariate hole GFs** —
recovered as exact rational G_{H,k}(x) for fixed (height, #holes). Two paths,
both in the tree: `gf/hole_recover.py` (u64, single-height via the new
`--holes --only-height H`; reaches ~n=36 before u64 wrap) and the **mod-p holes
engine** `gf/hole_modp_recover.py` (#5b — `sweep8_holes.h` `--modp P` carries the
*validated* Euler/hole accounting with counts reduced mod p, no overflow → many
terms; BM-mod-p + CRT, full-GF validated vs a fresh prime). RAM is bounded by
`--hdrop` (drop partial states whose hole count exceeds kmax — exact for all
k≤kmax since holes only seal, never reopen), making memory O(D_H·N·kmax), linear
in N: ~30 MB even at N=2700, so the wall is the engine's N≤4096 cap + time (∝N²),
not RAM. Recovered + validated to `results/hole_gfs.txt`: H=3 k=0..48, H=4 k=0..13,
H=5 k=0..3, **H=6 k=0..6** (76 GFs so far); **H=7 k=0..2 running** (N=3400). Order
law order(H,k) = c_H·(k+1), c = 6,20,68,185,537 for H=3..7 — clean per-hole order
increment. Feasibility frontier (N≤4096): H=6 reaches k≤10, H=7 k≤2, H=8 k=0 only,
H≥9 blocked (order(9,0) needs N≈9000).
REMAINING for #28: (i) n≥15 production run for the new hole terms — **the n=18
exact hole count is RUNNING on ayr now** (`tma_holes square8 18 --holes`); full
n=19 (~60–75 GB) fits ayr's 78 GB directly (no #20 needed); (ii) companion 8-bg
convention (needs a 4-adjacency component tally — deferred); (iii) **H=8 k=0 hole
GF — SUSPENDED mid-run, awaiting CONT** (the 14 stopped `--only-height 8 --holes
--modp` mod-p sweeps on gympie; jasonp resumes them when h19 frees the cores;
`python3 gf/hole_modp_recover.py 8 8 3400 0 30`, appends).
NOTE: `build/tma_holes` is the current holes+modp engine (built from live source);
production `build/tma` is still the OLD pre-holes binary running a(20) — rebuild
(`make build/tma`) once it frees.

**#25 — OEIS submission prep.**
CORRECTION (verified against mathworld.wolfram.com/Polyplet.html): the polyplet
*shape* counts already exist in OEIS — free A030222, fixed A006770, **one-sided
A030233** (our 1,2,6,34,166,991,… matches exactly — the earlier "no OEIS sequence
exists" note was WRONG; we'd only cross-checked one-sided against A030222), plus
bilaterally-symmetric A030234 and asymmetric A030235. So for all of these our
contribution is **extended b-file terms** (n=18,19), NOT new sequences — and our
symmetric counts must be cross-checked against A030234/A030235 before claiming
anything. The genuinely NEW sequences are only: the hole-stratified counts (4-/8-
conn, hole-free and by-count), the hole GFs, and the lifetime-3 byproducts (atom
degrees 1,2,4,9,29,68,…; orders 1,3,7,15,42,…). Draft b-files/descriptions/cross-
refs accordingly; includes novelty re-checks and provenance. **Nothing is
submitted without explicit signed orders (24-h cooling-off).** Convergence point
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
method on a different architecture (cross-ISA decorrelation). **a(20) =
1,025,573,519,362,016 is assembled as a candidate** (RESULTS.md R4, 2026-06-20):
n≤18 == published, a(19) reproduced, height-19 already cross-ISA on ayr, and a
fixed-height-GF series cross-check passes for heights 1–10. Remaining for
confirmed: gympie's own height-19 byte check (running) + ISA-decorrelated rerun
of heights 11–18,20 — **that rerun is IN PROGRESS on ayr now** (`a20cross`
driver, all-x86/GCC reassembly; assemble + compare to 1,025,573,519,362,016 on
completion). **ayr available 2026-06-20** (freed early; was ~June 27); dalby
off-limits.
→ Produces more terms (extended b-files); feeds #25 and #17.

**#19 — Benchmark engines + reach projection. DONE (2026-06-20).**
Measured the diagonal RAM driver (tallest strip) from two terms (a19, a20):
peak_states grows ×2.42/term, ≈270–320 B/state. Projection in `reach.md`:
**a(21) fits ayr's 78 GB (~35–41 GB, no backend); a(22) is the first term that
requires the out-of-core store (#20) at ~85–100 GB.** Separately the hole-GF wall
is recurrence order ∝ height (a time limit, not RAM).
→ Pins #20's trigger to a(22); informs #21, #28.

**#20 — Past the RAM wall: COMPRESSION FIRST, out-of-core deferred.**
The transfer matrix is RAM-bound (reach.md: a(22) ≈ 97 GB > ayr 78 GB). **Recast
2026-06-20** (`docs/state-store-compression.md`): the byte teardown shows the
per-state **counts row is 85%** of the footprint (a full u64 per cell-count
n=0…maxn). Compressing it — **ranged counts row** (exploit the size-budget prune;
×1.5–2.5), load factor 0.7→0.85 (~12%), u32 counts for mod-p runs — stacks to
≈2.2×, which drops a(22) to ~45 GB and **likely removes the need for the
out-of-core store entirely for a(22)**. Compression also buys headroom + speed for
the hole runs now. The true out-of-core backend (external hash-partitioned
aggregation, NOT mmap) is deferred to **a(23)+**, where it's unavoidable. Next
concrete step: an instrumented count-row-width measurement, queued for the next
free gympie core window. All edits post-a(20)-confirmation; gates stay
byte-identical.
→ Compression unlocks a(22) on ayr; out-of-core only for a(23)+.

**#17 — Paper + public repo drop (LAST).**
Fold everything into the write-up: a(19) + free/one-sided, hole sequences, the
fixed-height GFs and lifetime-3 (honestly weighted — see results/lifetime3-proof.md),
the growth estimate, and the sampling/scaling portrait; then the GitHub drop.
Strictly after the OEIS drafts (#25), since the paper references those entries.

**#29 — Venue: NOT JIS (decided 2026-06-19).** We are not submitting to the Journal
of Integer Sequences. JIS forbids LLM-written prose ("the actual English words"),
which would force a from-scratch human rewrite of the Claude-drafted text; not worth
it. The paper stays an **arXiv (math.CO/math.HO) preprint + the public repo**, where
the AI-drafted text and the Author's-note AI credit are fine as-is. The OEIS entries
themselves remain the canonical record of the new sequences (still gated on sign-off,
#25). No JIS-specific conformance (12pt/jis.bst/human rewrite) needed. The bilateral
identity proof added for the JIS angle stays in the paper regardless — it's a real
result. This closes the venue fork.

## Dependency graph

```
LEGEND:  A --> B  = A feeds / enables B          ((ayr)) = needs ayr (AVAILABLE NOW)

  -- start-now on gympie ------------------------------------------+
  |  #27 sampling-scaling --------------------------------------+  |
  |  #28 holes (bivariate hole-GFs, small H) --+               |  |
  |  #19 benchmark/reach --> #20 out-of-core --+               |  |
  +---------------------------------------------+--------------+--+
                                                |              |
            #20 (RAM wall) -- a(22)+ only, off critical path   |
                                                               |
   ((ayr NOW)) --> #21 extend a(20)+, cross-ISA --> more terms |
   ((ayr NOW)) --> #28 full n=19 holes (fits 78 GB directly)   |
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
- **ayr is the multiplier now, not #20.** As of 2026-06-20 ayr (78 GB) is
  available, so the heavy compute (#21 cross-ISA a(20)+, full-n=19 #28) runs on
  ayr directly. **#20 (out-of-core) drops off the critical path** — needed only
  for a(22)+ beyond 78 GB. #19's reach projection still informs *when* a(22)+
  forces #20, but no longer gates the current terms.
- **Heavy compute is live on ayr:** #21's all-x86 a(20) reassembly (`a20cross`)
  and #28(i)'s n=18 exact hole count are both running; #28(iii)'s H=8 hole GF is
  suspended on gympie awaiting CONT. gympie also runs the light independent work
  (#27 sampling-scaling, small-H hole GFs).
- **#25 is the convergence point** — it consumes hole sequences (#28),
  atom-degree/order sequences (#26, done), and extended b-files (#21); then
  everything plus #27's scaling flows into **#17, strictly last.**
- **Critical path to publication:** (ayr, now) #21/#28 → #25 → #17, with #27 and
  the gympie-side hole prototype running in parallel. #19 → #20 is a parallel
  side-track for the a(22)+ frontier, no longer blocking.
