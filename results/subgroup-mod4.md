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
- `results/subgroup_mod4_20260807.log` — the run log
- `scripts/subgroup_mod4.sh`, `experiments/subgroup_mod4.py`,
  `tests/gate_subgroup.py` (13 checks, 5 of them controls)

## Next

Per-cell **mod 4** instead of per-cell parity:
`T(n,H) = I_H(<h>) + I_H(<v>) + I_H(C2) - 2 I_H(D2ax) (mod 4)`. Those three
inputs are lambda^(n/2) families, out of reach for explicit enumeration, but
`symtm` is a transfer matrix whose cost is states x columns. Its hmirror mode
already sweeps one exact-height strip at a time, and recording the width at
harvest yields `I_H(<v>)` from the same run by transposition. Its r180 mode
needs more care: the transpose restriction harvests strip H only for W >= H
with weight 2 when W > H, so the strip label is NOT the height. Covering
H <= 19 at n=40 needs only strips H <= 19, the cheap end of that engine.
