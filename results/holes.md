# Hole-stratified polyplet counts (by-hole-count and hole-free)

New sub-sequences of A006770: fixed king polyplets of n cells classified by their
number of enclosed holes. Produced by `build/g2 square8 N --holes` (4-connected
background) and `--holes8` (8-connected background). Output lines: `n holes count`.

## What a "hole" is, and the convention question
A hole is a bounded connected component of the empty complement. The foreground
(the polyplet) is 8-connected (king). The *background* connectivity is a genuine
modelling choice that changes the counts, so we compute both:

- **4-bg (`--holes`)** — 4-connected enclosed empty regions. This is the Jordan
  dual of an 8-connected foreground (Rosenfeld's digital-topology pairing: pair
  8-connectivity with 4-connectivity or you get the connectivity paradox where a
  diagonal pinch is simultaneously a wall and a passage). It is ALSO the same
  hole definition OEIS already uses for polyominoes (A389193 counts 4-connected
  holes). Recommended primary convention.
- **8-bg (`--holes8`)** — 8-connected enclosed empty regions (same adjacency as
  the foreground). First hole only appears at n=8 (the 3x3 ring); under 4-bg the
  first hole appears at n=4 (the diamond = plus minus its centre).

Decision (2026-06-18): compute and keep BOTH; submit nothing without explicit
go-ahead. See [[shelf]] for the related Lean-verification thread.

## Validation (why we trust these are right, not just "novel")
1. **Sum invariant.** For every n, the per-hole counts sum to A006770 (the
   validated total). Confirmed n<=12 for both conventions (a(12)=257105146).
   So we partition exactly the right set; the only possible error is
   misclassification, not miscounting.
2. **Two independent implementations.** The C++ `--holes`/`--holes8` tables are
   byte-identical to a from-scratch Python enumerator (different generation: BFS
   + frozenset dedup vs Redelmeier; different flood: deque BFS vs stack DFS)
   through n=7.
3. **Convention validated against known answers.** Running the identical flood on
   *polyominoes* (`build/g2 square4 N --holes`) reproduces published sequences
   exactly: hole-free -> A006724 (fixed self-avoiding polygons = simply-connected
   fixed polyominoes); with-holes -> A389193 (fixed polyominoes with holes,
   4,41,272,1516,7708,37024 at n=7..12). This pins the flood logic and the
   4-connected-hole definition to OEIS's own convention.

These checks are folded into `tests/gate_g2.py` (check H).

## The sequences (n = 1 ..)

### 4-bg (Jordan dual; recommended) -- not in OEIS
- hole-free: 1, 4, 20, 109, 622, 3664, 22094, 135609, 843941, 5310754,
  33724862, 215793158
- with >=1 hole: 1 (n=4), 16, 168, 1498, 12332, 97041, 742426, 5574546,
  41311988 (n=12)
- exactly 1 hole: 1 (n=4), 16, 166, 1456, 11788, 91300, 688034, 5091820,
  37209939 (n=12)
- first multi-hole: 2 holes first at n=6 (count 2); 3 holes first at n=8 (count 6)

### 8-bg (same adjacency as foreground) -- not in OEIS
- hole-free: 1, 4, 20, 110, 638, 3832, 23592, 147940, 940966, 6053002,
  39297724, 257090547
- with >=1 hole: 1 (n=8), 16, 178, 1684, 14599 (n=12)

Novelty: OEIS returns no results for any of the above (checked 2026-06-18); the
query path was sanity-checked to find A006770/A389193 correctly.

## Transfer-matrix method (#28) — removes the n=14 cap
As of 2026-06-18 the 4-bg (primary) counts are also produced *inside* the column
transfer matrix via the Euler characteristic (`tma square8 N --holes`), with no
per-animal flood — so they reach the bare count's n instead of capping at 14.
Mechanism + correctness in `cpp/tma/euler.h` and `cpp/tma/sweep8_holes.h`;
validation: byte-identical to the `g2 --holes` flood above for n≤11 and to
`results/holes_n14.txt` for n≤14 (including the maximum-hole rows), sum-invariant
== A006770 for n≤12. The 8-bg companion is NOT yet in the transfer matrix (it
needs the animal's 4-adjacency component count) and stays on the flood for now.
See `plan-transfer-matrix-holes.md` and ROADMAP #28 for the remaining work
(n≥15 production run, the bivariate hole GFs, gate integration).

## Cost
Per-animal flood is O(bbox area), so this caps below the bare-count reach.
Throughput (gympie, single-thread, concurrent with other jobs): n=10 ~3s,
n=11 ~21s, n=12 ~147s (~6.6x/step). n=14 ~1.7h. Extension to n=14 (4-bg) under
way in tmux window `holes14`.
