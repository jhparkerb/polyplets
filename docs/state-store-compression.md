# State-store memory — getting the transfer matrix under the RAM wall (recasts #20)

> **Status (2026-06-21): a design + decision record, NOT a results log.**
> *Implemented & gate-verified:* `--reserve` pre-sizing (B5), load-factor 0.85 (A3).
> *Measured:* the byte budget. *Cited:* the symmetry fold (C7). *Ruled out:*
> auto-`kmax`. **Everything else — ranged row, u32, chunked drain — is projected and
> UNBUILT.** The headline "≈2.2× / a(22) → ~45 GB" rests on the ranged-row factor,
> which is still **unmeasured** (the `--profile-rows` measurement is queued). Trust
> the per-lever status tags, not the projected numbers.

**Thesis:** the RAM wall (reach.md: a(22) ≈ 97 GB > ayr's 78 GB) is best attacked
by shrinking the in-RAM state store, not by building the out-of-core backend
(deferred to a(23)+, where it's unavoidable). The footprint factors as

    RSS  ≈  bytes/state  ×  live states  ×  structural multipliers

and there are levers on **all three axes — not just byte packing.** This file was
packing-only; updated 2026-06-21 with the reserve lever (landed), a symmetry lever
(cited), structural ideas, and one dropped idea.

## Where the RAM goes

The hot store is `FlatDB` in `cpp/tma/statedb.h`: open-addressing, three flat
arrays, grows by doubling at load factor 0.85 (A3, landed). Per-state bytes at maxn=22:

| component | bytes | share |
|---|---|---|
| `vals` — counts row, `(maxn+1)` × u64 | 184 | **85%** |
| `keys` — `Sig` (`unsigned char b[32]`, `SIGMAX=32`) | 32 | 15% |
| `used` flag | 1 | <1% |
| raw subtotal | 217 | |

Confirms the ~270–310 B/state measured from live RSS (gympie height-19: 6.45 GB /
23.98 M states). **The counts row dominates** — each state stores a full u64 count
for *every* cell-count n=0…maxn, because the sweep produces byHeight[H][·] for all
n in one pass.

But bytes/state is only one axis. Two **structural multipliers** sit on top:

- **Doubling-grow transient.** `grow()` moves the old arrays aside and allocates
  the new 2× arrays *before* freeing the old, so the rehash momentarily holds ~3×
  the pre-grow `vals`. The heavy height's final grow is ~1.5× the steady
  allocation — typically the RSS high-water.
- **Double buffer.** Each column holds `db` *and* `next` at once → ~2× a single
  layer; at the peak column both are ~peak.

So `RSS ≈ bytes/state × peak-states × (~2× double-buffer) × (grow transient/slack)`.

## A. Bytes per state — PACKING levers

1. **Ranged counts row — the main byte win (×1.5–2.5 on the row).**
   The size-budget prune guarantees only a contiguous sub-range `[lo…hi]` of n is
   reachable at any state (depth-d state has ≥ d cells and must still reach maxn).
   Store `(lo, len, u64[len])` instead of dense `[0…maxn]`. Pure drop-in behind
   FlatDB's `slot`/`for_each`/`addCounts` — the file's own comment names it THE
   designed-to-be-replaced component. Size it via the measurement below.
2. **u32 counts for mod-p runs — clean ×2 on the row.** The hole/GF mod-p engine
   reduces counts mod p < 2³¹, so the row fits `u32`. Template the counts type.
   Doesn't help *exact* a(n) (counts reach ~10¹⁶), but the hole work is RAM-relevant.
3. **Load factor 0.7 → 0.85 — LANDED.** Bumped in `FlatDB` and `HoleDB` (slot +
   reserve thresholds); steady slack ~1.43× → ~1.18×, byte-identical (gate green).
   Mostly matters for the default path; runs that pass `--reserve` (B5) control the
   slack directly anyway.
4. **Shrink `Sig` to the run's height — minor (~4%).** `SIGMAX=32` covers H≤30; a
   height-22 run needs ~24 B. `hashSig`/`memcmp` assume `SIGMAX` → templated-width
   change, low priority. (A compact crossing-partition encoding could do better,
   but keys are only 15%.)

## B. Structural multipliers — NON-PACKING

5. **Reserve / pre-size — LANDED (commit d043cc1).** `--reserve N` pre-sizes the
   store (and each MT shard to its share) to ~N states, skipping every doubling
   rehash → **no grow transient, slack you choose, and faster (no rehashing).** Gate
   check K, byte-identical. Attacks the grow-transient multiplier directly; pass the
   calibrated `peak_states`. This is the first axis-B win and partly banks lever A3.
6. **Chunked store / incremental drain — the untapped ~2× (NEW, high ceiling).**
   The double-buffer 2× is treated as fundamental, but it isn't. If the store were a
   list of fixed-size blocks instead of one flat array, `db` could be drained
   block-by-block — freeing each db block once its successors land in `next` — so
   mass moves db→next and the peak is ~1×+overhead instead of 2×. Open-addressing in
   one array can't do this (clearing slots doesn't return the array). It needs a
   blocked structure — **and that same blocked, hash-partitioned structure IS the
   out-of-core seam.** So this isn't a detour from the deferred backend; it's the
   in-RAM half of it, delivering ~2× before any disk. Real redesign, biggest
   structural ceiling.

## C. Fewer live states — NON-PACKING

7. **Vertical-flip symmetry fold — ~2× on the state COUNT (stacks with packing).**
   The strip's top↔bottom reflection commutes with the column transition, so
   mirror-image signatures complete in the same number of ways and can be merged.
   **Standard technique**, primary source in `papers/`: Barequet & Ben-Shachar,
   *"Counting Polyominoes, Revisited"* (2024, DOI 10.21203/rs.3.rs-4304962/v1) §4.2 —
   merging mirror signatures *"effectively halv[es] the number of signatures before
   starting to process the next column."* (Also Jensen, ICCS 2003,
   `papers/jensen_counting_polyominoes_parallel.pdf`.) Parity wrinkle: per-column
   signature merge for **odd**-height strips; mirror-box pairing (process one box,
   double the count) for **even**. Cuts the COUNT, so it multiplies with every byte
   lever — highest ceiling. Correctness-critical (self-symmetric signatures counted
   once, paired twice); gate byte-identical is mandatory.

**Dropped — auto-bounding `kmax` for the holes path.** Investigated 2026-06-21,
abandoned. The idea: shrink the holes dimension from `maxn` to ~max-realizable
holes. But a one-colour checkerboard is king-connected and seals every interior
opposite-colour cell into a 4-bg hole, so **max holes grows ~linearly, approaching
n** (data: 9 holes at n=16, and 9 > n/2). `kmax=maxn` is already near-right;
tightening it saves ~nothing and risks silently dropping real animals via `hdrop`.
The holes-dimension win is the ranged row instead (below).

## Holes-specific: the (size, #holes) table is 2D-sparse

The holes store carries a `(maxn+1)×(Kmax+1)` table per signature, but a partial
state of size s has nonzero entries only for sizes ≥ s and holes ≤ ~s — an
upper-triangular wedge. So the ranged row applied to the holes table (range *both*
axes, or a sparse per-state wedge) is a **bigger** win than for the a(n) path. This
is where the hole runs (exact n=18/19, mod-p GFs) reclaim their RAM.

## Combined projection (updated)

- **Landed:** reserve removes the grow transient (~1.2–1.5× off the peak) and tightens
  slack — partly banking the old load-factor lever.
- **Remaining packing:** ranged row (×1.5–2.5 on vals, the main byte lever) + u32
  (mod-p) + Sig-shrink (minor).
- **Structural bets:** chunked drain (~2× from the double-buffer; also the out-of-core
  seam) and symmetry fold (~2× on count) — higher ceiling, higher risk.
- Exact a(22): ranged (~1.8×) alone → ~45 GB, inside 78 GB; reserve adds headroom. The
  structural bets are what push a(23) (~95–110 GB after ranged) toward fitting too —
  the first term where they pay for themselves.

## The measurement (queued — needs a core window)

Before committing to the ranged row, size its payoff: instrument one sweep to
histogram the live count-row width `hi-lo+1` at the peak height, weighted by state:
- a `--profile-rows` flag that, in `for_each` at the peak layer, accumulates a
  histogram of `[minSizeRow … maxSizeRow]` width (opt-in, does not alter counts);
- run `tma square8 16 --only-height 16 --profile-rows` (fits a core or two; the
  distribution shape is N-stable);
- expected: mean width ≪ maxn ⇒ ranged row ≈ (maxn / mean-width)× on `vals`.

**Status: queued for the next free gympie core window.** Paper design until then.

## Out-of-core, if/when a(23) is a goal (the deferred backend)

Not now. When needed: **external hash-partitioned aggregation**, not mmap. Emit
`(successor-sig, count-row)` records, partition by `hash(sig)` into K buckets each
sized to RAM, aggregate bucket-by-bucket — sequential I/O. The **blocked store of
B6 is the precursor**: it delivers the in-RAM 2× and is the same seam this needs.
mmap-the-hash is a correctness fallback only.

## Implementation order (post-a(20)-confirmation; gates must stay byte-identical)

1. ~~Load factor 0.7→0.85~~ — **LANDED (A3); reserve (B5) also landed.**
2. Measurement (`--profile-rows`) → size the ranged row.
3. Ranged counts row behind the FlatDB interface (the big byte win) + the 2D-sparse
   holes variant.
4. u32 counts for the mod-p path (helps hole runs).
5. THEN weigh the structural bets: symmetry fold (~2× count, cited) and/or the
   chunked/blocked store (~2× double-buffer + out-of-core seam).
6. `make gates` byte-identical after each (gate-g2, gate-tma vs A006770 n≤18, a(19),
   the hole oracle, and the new MT/checkpoint/reserve checks).
