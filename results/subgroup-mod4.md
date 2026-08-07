# Subgroup census: a(n) mod 4, and a parity bit on every triangle cell

2026-08-07, gympie. Executes idea 1 of `results/unexplored-avenues.md`, which
is now marked EXECUTED there (and has one of its two claimed payoffs struck —
see the correction at the end of this file).

**Headline: 820 cells of the a(40) triangle, 0 parity mismatches, covering
100% of a(40)'s mass — including the 43.84% band that had no second source at
all.** Plus `a(n) mod 4` confirmed independently at every n ≤ 40, and a free
mod-8 cross-check of the banked symmetry corpus at n ≤ 32.

## What was missing, and why it is a different object

Burnside's lemma counts D4 *orbits*, and it needs the per-ELEMENT fixed-point
counts `Fix(g)` — which `results/sym_counts.txt` has banked for weeks. The
orbit-SIZE distribution needs per-SUBGROUP invariant counts `I(H)`: the number
of fixed animals invariant under *every* element of a subgroup `H <= D4`.
Those are not the same thing, and none were banked. `I(D2ax)` is fixed by both
axis mirrors; `Fix(h)` is fixed by one. The gate has a control for exactly
this confusion — substituting `Fix(h)` for `I(D2ax)` must break the
congruence, and it does, first at n=3.

With `F(H)` for "stabiliser exactly H" (so `I(H) = sum over K >= H of F(K)`):

```
n1 = F(D4) = I(D4)
2 n2 = I(C4) + I(D2ax) + I(D2diag) - 3 I(D4)
==>  a(n) = I(C4) + I(D2ax) + I(D2diag) - 2 I(D4)          (mod 4)
```

Every input is a quotient-domain family of size ~lambda^(n/4). That is the
whole point: a(40) cost 100+ core-days on an 80-core box, and its mod-4
residue costs 45 minutes on a laptop by an unrelated algorithm.

## The sharper form: one bit per CELL, not two per row

Found while implementing, and it is the part that actually addresses the
provenance gap. **D2ax = {e, h, v, r180} is exactly the height-preserving
subgroup of D4** — r90, r270 and both diagonal mirrors swap height with width.
So D2ax acts on the animals of each fixed height separately, orbit sizes there
divide 4, and

```
T(n,H) = I_H(D2ax)   (mod 2)
```

is one independent bit per triangle CELL. Two bits on a row total constrain
only the sum; one bit per cell localises the check to a height band, which is
what `ns_a40/PROVENANCE.md` asks for.

## Results

`scripts/subgroup_mod4.sh 40 8`, `build/symcount_fast` at rev `16236db`,
2026-08-07 14:19–15:04 EDT, 8 threads, peak RSS 4.6 MB.

| type | I(H) at n=40 | wall |
|---|---|---|
| `c4` = `<r90>` | 16671983 | 7.3 min |
| `d2ax` = {e,h,v,r180} | 123753061 | 15.0 min |
| `d2diag` = {e,d,ad,r180} | 108831725 | 8.2 min |
| `d4` = full group | 10379 | instant |

**Regression against prior compute:** the `c4` column recomputes, by the
subgroup CLI path, what the sym34 farm banked as `r90`. Identical on all rows
n ≤ 33.

**mod 4: 40 rows, 40 comparable, 0 mismatches.** a(40) = 3 mod 4 both ways.

**The triangle, per height band** (bands and mass shares are
`ns_a40/PROVENANCE.md`'s own "Corroboration by mass" partition, so this table
answers that one directly):

| band | cells | share of a(40) | parity mismatches | what it had before |
|---|---|---|---|---|
| H1-10 | 355 | 7.52% | 0 | decorrelated fixed-height GFs |
| H11-14 | 114 | 37.49% | 0 | strip TM (shares `core/transition.h`) |
| **H15-19** | **120** | **43.84%** | **0** | **none available** |
| H20 | 21 | 4.16% | 0 | byte-identical re-sweep |
| H21 | 20 | 2.84% | 0 | real sweep, P_19's fit point |
| H22-40 | 190 | 4.14% | 0 | closed forms, no holdout possible |
| **TOTAL** | **820** | **100.00%** | **0** | |

The two rows that matter are H15-19, which the ledger records as having no
corroboration of any kind, and H22-40, whose closed-form cells no later sweep
can ever hold out because the sequence closes at a(40).

## The mod-8 by-product, and the error it caught

Every `I(C4)` and `I(D4)` term cancels at the next level, and the two order-2
mirror CLASSES each contribute twice — {e,h} with {e,v}, {e,d} with {e,ad}:

```
a(n) = Fix(r180) + 2 Fix(h) + 2 Fix(d) - 2 I(D2ax) - 2 I(D2diag)   (mod 8)
```

Everything but the last two terms is already banked, so this costs nothing and
cross-validates the whole sym32/33/34 corpus against the b-file. It stops at
n=32 because `Fix(d)` is the 24h/126GB wall of `results/related-seqs-n33.md`.
**33 rows, 0 mismatches.**

It earned its keep immediately: the first version shipped with both factors of
2 dropped and failed on 21 of 33 rows. The algebra was wrong, not the data.
The mod-4 line had a gate and was right; the mod-8 line had none and was not.
Both are now in `gate-subgroup`, the second with a control that fails if the
coefficient slips back to 1.

## Honest limits

- **Two bits, not a proof.** A wrong a(40) survives this iff its error is
  0 mod 4 — three residue classes out of four are excluded, not all of them.
  Per cell it is one bit, so one class in two.
- **Independence is structural, not total.** `symcount_fast` is an orbit-graph
  Redelmeier over a quotient domain; a(40) came from the column engine. They
  share no code path, no state representation and no domain. They do share the
  king-adjacency definition — as any two correct programs must.
- **The congruence is elementary.** It is Burnside read backwards, and it is
  probably folklore. Nothing in OEIS's A006770 or A001168 comments mentions
  parity or congruences, and nothing in the 72-paper local corpus does either,
  but absence of the word is weaker than absence of the idea. **Novelty is not
  claimed.** The deliverable is the validation, not a theorem.

## Correction to idea 1 as written

`results/unexplored-avenues.md` idea 1 claimed a second payoff: that these
inputs would unstrand A030222/A030233/A030234/A030235/A194596 at n=32-34.
**They do not.** Burnside needs per-element `Fix(g)` —
`free_num = fixed + 2 Fix(r90) + Fix(r180) + 2 Fix(h) + 2 Fix(d)`
(`tests/common.py:132`) — and the binding input is `Fix(d)`, exactly the
lambda^(n/2) blocker. Subgroup-invariant counts do not feed Burnside at all.
That bullet is struck in the source file with this reason.

## Artifacts

- `results/subgroup_counts.txt` — I(H) for the four subgroups, n ≤ 40
- `results/subgroup_d2ax_byheight.txt` — I_H(D2ax) as "n H count", 630 rows
- `results/subgroup_mod4_verdict.txt` — the assembler's full output
- `results/subgroup_mod4_20260807.log` — the run log, and note it is the
  **pre-fix** run: its last line still reads
  `mod 8: 33 rows predicted, MISMATCH [...]`, 21 of 33 rows. That is the
  dropped-factor-of-2 error above being caught, not a live failure. The
  corrected result is `subgroup_mod4_verdict.txt`, written two minutes later,
  and the log is kept as the receipt rather than overwritten
- `scripts/subgroup_mod4.sh`, `experiments/subgroup_mod4.py`,
  `tests/gate_subgroup.py` (13 checks, 5 of them controls)

## What one bit means, stated properly

Per cell it is literally one bit: an engine error of size `delta` in `T(n,H)`
is caught iff `delta` is odd. For a single corrupted cell that is 50%.

But single-cell errors are not this project's failure mode. The Zero Harvest
incident in `ns_a40/PROVENANCE.md` zeroed an entire `h20.out` row -- 20 cells
at once. A dropped shard, an off-by-one in a column loop, a resume seeded from
the wrong table, an overflow: every one of them corrupts many cells together,
and 820 independent bits catch a k-cell corruption with probability
`1 - 2^-k`. For that h20 row, `1 - 2^-20`.

So: **worst case one bit, against an adversary corrupting exactly one cell and
choosing a delta that preserves its parity; against every failure mode that
has actually occurred here, effectively certain.**

## Per-cell mod 4: why it is NOT being bought at n=40

The refinement `T(n,H) = I_H(<h>) + I_H(<v>) + I_H(C2) - 2 I_H(D2ax) (mod 4)`
is real -- verified cell by cell against the production triangle -- and the
`--byheight` modes for `symtm` hmirror and r180 are built and regression-clean
(`results/percell-mod4.md`). It is not being pushed to n=40, for three
measured reasons.

**1. `I_H(<v>)` has no bounded-height route.** Transposing sends a v-symmetric
animal of height H to an h-symmetric one of WIDTH H whose own height is
unbounded, so it needs every strip up to n. A `--maxwidth` brake was added and
is not enough: width 8 across all 40 strips still ran past 2 minutes. The
bounded-height route is a NEW vmirror sweep mode -- sweep the left half of a
height-H strip and glue at the middle, the right half being the left
column-reversed -- which is a `sweepR180`-sized piece of glue logic, not a
patch.

**2. r180's cost peaks exactly on the band that needs it.**
`results/symtm_strip_profile_n40.txt`, N=40, 8 threads, 120s cap per strip:

```
hmirror   H=5:0   H=10:0    H=15:3     H=19:51    H=20:33   H=25..40: >120
r180      H=5:0   H=10:15   H=15:>120  H=19:>120  H=20..30: >120
          H=34:7  H=38:0    H=40:0
```

r180's expensive strips are the MIDDLE ones. The transpose restriction forces
W >= H, so as H approaches n every column is pinned to a single cell and the
strip collapses -- which is why H=34..40 are seconds while H=15..19 are past
the cap. "Cover H<=19 using only the cheap short strips" does not survive
contact with this curve: H=15..19 IS the peak.

**3. The bit it buys is the one least worth having.** Two bits per cell moves
the single-cell adversarial case from 1/2 to 3/4 and adds essentially nothing
against systematic corruption, which 820 bits already catch with probability
indistinguishable from 1. And it would be bought with a fresh transfer-matrix
mode whose own correctness then becomes the thing being trusted --
`symcount_fast` has been gated against the brute oracle since June and
reproduces the sym34 farm's r90 identically on all 33 rows; a new vmirror
sweep would have none of that history. A checker with a bug that happens to
agree is worse than no checker.

## Why this band will never get better than bits

The strip engine is the only thing that could second-source H15-19 with real
VALUES rather than bits, and it cannot reach them. Its wall grows ~6x per
height: H=14 took 8.6h on dalby (`results/strip-engine.md`), putting H=15 at
~52h and H=19 at ~7.6 years, and its state packing caps out anyway ("State
packed 4 bits/row -> H<=15 cap"). The parity bit in this file is, realistically,
the only independent evidence 43.84% of a(40) will ever carry.
