# Middle Kingdom Phase 3 — the empty grid cells (2026-08-05)

`docs/middle-kingdom-plan.md` Phase 3: fill the grid's empty cells, each with
an enumeration path validated against Phase 0's brute-force table, terms, a
growth constant, a GF class where tractable, and a novelty check.

Twelve cells were open: the plan's nine (`dir5`/`dir4`/`ctrlB` ×
column-convex/HV-convex/staircase) plus the three of the multi-directed row,
which Phase 1c established is a fifth directedness value the 16-cell grid had
no slot for (`results/multi-directed.md`).

**Result: eight of the twelve collapse onto a cell of the unfiltered row, with
proofs, and three of the remaining four are new sequences.** The one that is
not is A018902, which acquires a lattice-animal interpretation it did not have.
Every collapse is now a proposition below, not an observation: on a
column-convex animal each directedness predicate reduces to a condition on the
bottom profile alone, and the collapses fall out of that in one line each.

## The grid after Phase 3

Rows are directedness, columns convexity. **Bold** = new here.

| | none | column-convex | HV-convex | staircase |
|---|---|---|---|---|
| **none** | A006770 | A187077 | NOVEL (convex polyplets) | A225114 |
| **dir5** (5-cone) | A047781 | **NOVEL** | = (none, HV) | = A225114 |
| **dir4** (4-cone) | A055834 | **A018902** | **NOVEL** | = A225114 |
| **ctrlB** (bottom row waived) | control-B seq. | **NOVEL** | = (none, HV) | = A225114 |
| **multi-directed** | **A222205** (was labelled novel; see below) | = A187077 | = (none, HV) | = A225114 |

Growth constants of the four cells that needed work, with the unfiltered
column-convex cell as the calibration:

| cell | first terms | µ | GF class |
|---|---|---|---|
| (none, col-convex) = A187077 | 1, 4, 18, 83, 385, 1788 | 4.644680109386463104 (root of x⁴−7x³+13x²−10x+2) | rational (published) |
| (dir5, col-convex) | 1, 4, 17, 71, 289, 1149 | **2+√2** exactly, with a **double** pole | rational, denominator (1−x)(1−4x+2x²)² |
| (dir4, col-convex) = A018902 | 1, 4, 17, 73, 314, 1351 | **(5+√13)/2** = 4.302775637731994647 | rational, x(1−x)/(1−5x+3x²) |
| (ctrlB, col-convex) | 1, 4, 18, 79, 339, 1423 | 3.811527945110 (12 digits) | **not** D-finite in the boxes below |
| (dir4, HV-convex) | 1, 4, 15, 53, 177, 567 | 3.128943269730886252277 = the unrestricted HV-convex constant (49 digits checked) | **not** D-finite in the boxes below |

## Why the collapses happen

Throughout, a column-convex king animal is a sequence of nonempty column
intervals `[b(j), t(j)]`, `j = 1..k`, on a contiguous run of columns, with
consecutive columns king-adjacent. Adjacency is exactly
`d(j) := b(j+1) − b(j) ∈ [−h(j+1), h(j)]`, giving `h(j) + h(j+1) + 1`
placements of a height-`h(j+1)` column against a height-`h(j)` one.

**Lemma A (a column is reached iff its bottom is).** Neither forward cone
contains a southward step: `{W, NW, N, NE, E}` and `{N, NE, E, SE}` both move
strictly up or stay level. Inside one column of a column-convex animal, then,
reachability only climbs, so the reached part of a column is an up-set
`[r(j), t(j)]`, and the animal is directed iff `r(j) = b(j)` for every `j`.
From a fully reached column `j`, the bottom cell of the next column is
enterable
- (5-cone, either direction) iff `b(j±1) ≥ b(j)`: entry at height `b(j±1)`
  needs `b(j±1)` or `b(j±1)−1` occupied in column `j`, and `b(j±1) ≤ t(j)+1`
  is king-adjacency, which always holds;
- (4-cone, rightward only) iff `b(j+1) ≥ b(j) − 1`: the SE step buys exactly
  one row of descent.

**Proposition 1 (dir5).** A column-convex king animal is Bacher-5-cone
directed iff `b` is *valley-unimodal* (nonincreasing, then nondecreasing).
Forward: the source is the leftmost cell of the bottom row, which sits on the
unique local-minimum plateau; propagate right and left by Lemma A. Backward:
let `P` be any local-minimum plateau at height `v` other than the global one.
Every cone step into `P`'s bottom row starts at height `v` or `v−1` in the
column immediately left or right of `P`, and both of those columns have bottom
strictly above `v`, so no such cell exists; nothing inside `P` at height `v`
can be reached from inside `P` either, because that row is where the flood
would have to start. So `P`'s bottom row is unreachable and the animal is not
directed.

**Proposition 2 (dir4).** A column-convex king animal is half-plane-4-cone
directed iff `b(j+1) ≥ b(j) − 1` for every `j`. The source is the bottom of
the leftmost column and propagation is rightward only, so Lemma A applies
column by column with no case analysis.

**Proposition 3 (ctrlB).** A column-convex king animal passes the bottom-row-
waived predicate iff every local minimum of `b` equals `min b`. The sources
are the bottoms of the columns attaining `min b`; from those, Lemma A reaches
exactly the columns joined to a source by a monotone run of `b`, which is every
column iff no local minimum sits above the global one.

**Corollary 4 (HV-convexity contains directedness).** Row-convexity forces `b`
valley-unimodal: if `b(j−1) > b(j) < b(j+1)`, the row `y = b(j) − 1` is
occupied in columns `j−1` and `j+1` (king-adjacency gives `b(j) ≤ t(j±1)+1`)
and empty in column `j`, a gap. Dually `t` is peak-unimodal, and the converse
holds too, so **HV-convex = column-convex + `b` valley-unimodal + `t`
peak-unimodal.** With Proposition 1 this says HV-convex ⊂ dir5 outright.
Staircase (bottoms and tops nondecreasing) is inside HV-convex, and also
satisfies Proposition 2's condition trivially. Since dir5 ⊆ ctrlB always
(same cone, larger source set) and dir5 ⊂ multi-directed (Bacher: one source,
no keystone), five collapses follow at once:

    (dir5, HV) = (ctrlB, HV) = (mdir, HV) = (none, HV)      [the novel convex-polyplet series]
    (dir5, stair) = (dir4, stair) = (ctrlB, stair) = (mdir, stair) = A225114

**Proposition 5 (every column-convex king animal is multi-directed).**
Bacher's Definition 2 asks (1) every cell reachable from some source, where
sources are the local minima of `b`, and (2) every keystone (local maximum of
`b`) reachable from a source strictly left and one strictly right. For (1),
every column reaches a local minimum of `b` by a monotone run, and Lemma A
propagates the bottom back along it. For (2), the keystone at the leftmost
column of a local-maximum plateau is reached from the nearest source on its
left along the ascending run, and from the nearest source on its right along
the run that descends to it, whose last leg is a sequence of W steps across the
plateau at the keystone's own height. The blocking rule ("no other keystone at the keystone's
height") never bites: keystone marks sit at their own column bottoms, which
are strictly lower on both runs, and the plateau's other columns carry no mark
because the leftmost column takes it. Hence the entire multi-directed row of
the grid equals the unfiltered row, cell for cell.

All eight collapses are confirmed independently by brute force to n = 14
(`build/directed_cone_anchor grid 14 8`, the mdir row added in Phase 3;
`results/mk_grid20_n14.txt`), and are gate-checked with the four cells that
must *not* collapse alongside them (`make gate-king-grid`).

## The four cells that needed real work

`cpp/middle_kingdom_tm.cpp` (`build/middle_kingdom_tm`) counts bottom profiles
directly: state (column height, unimodality phases), or (column height, height
above the running minimum, phase) for `ctrlB`, where the predicate is about
absolute height and the profile steps cannot be aggregated. It reproduces the
Phase 0 brute-force table for all six column-convex cells to n = 14, and its
`hv` mode reproduces all 700 terms of the independent ROW transfer matrix
`build/convex_area_tm` (`make gate-middle-kingdom`).

### (dir5, column-convex): novel, rational, growth 2+√2 with an extra factor n

1, 4, 17, 71, 289, 1149, 4481, 17209, 65281, 245169, 913153, 3377505,
12418561, 45428161 (700 terms: `results/mk_ccdir5_terms_n700.txt`).

Valley-unimodal profiles split into a nonincreasing run and a nondecreasing
one. Each run's transfer operator has rank 1 (`d ≤ 0` admits `h(j+1)+1`
placements, `d ≥ 0` admits `h(j)+1`), and both runs turn out to have the *same*
ratio `p(x) = (2x−x²)/(1−x)²`, so the two geometric series multiply and the
pole is double:

    F(x) = x(1 − 5x + 9x² − 6x³ + 2x⁴) / [ (1−x)(1 − 4x + 2x²)² ]
    a(n) = 9a(n−1) − 28a(n−2) + 36a(n−3) − 20a(n−4) + 4a(n−5),  n > 5
    a(n) ~ C·n·(2+√2)ⁿ,   C = 0.10370…   (measured a(n)/(n µⁿ): 0.103899 at n=300, 0.1037013 at n=700)

`1 − 4x + 2x²` is A007052's denominator: the single-run subclass (bottoms
nondecreasing, no cone filter) is exactly A007052, `x(1−x)/(1−4x+2x²)`, which
is Phase 0's Finding 1. So the whole cell has A007052's growth constant with a
polynomial factor on top, the signature of gluing two A007052-like halves at
the valley. Both the recurrence and the numerator were checked against all 700
terms.

**Novelty: no OEIS match** on 1,4,17,71,289,1149,4481,17209,65281 or on the
6-term prefix (`experiments/oeis_lookup.py`, 2026-08-05). No hit in the
literature pass either: directed column-convex *animals* are enumerated on the
square lattice, and Bacher's king-lattice work carries no convexity axis.

### (dir4, column-convex): A018902, a known sequence with a new meaning

1, 4, 17, 73, 314, 1351, 5813, 25012, 107621, 463069, 1992482, 8573203,
36888569, 158723236 (`results/mk_ccdir4_terms_n700.txt`).

Proposition 2's condition `d ≥ −1` makes the placement count `h(j) + 2`,
independent of the new column's height, so the transfer operator has rank 1
and

    F(x) = x(1−x)/(1 − 5x + 3x²),   a(n) = 5a(n−1) − 3a(n−2),   µ = (5+√13)/2.

This is **A018902** (offset 0, g.f. `(1−x)/(1−5x+3x²)`), matched termwise to
n = 20 against the entry's own data. The entry's formula section already says
A018902 is the INVERT transform of A007052, and the animals explain why: cut
the profile at every descent (each is by exactly one row) and the pieces are
bottoms-nondecreasing column-convex animals, i.e. A007052 objects, so the
class is a sequence of them. A018902's existing comments are compositions,
closed walks on K₂, Pisot sequences and words; there is no lattice-animal
reading, which makes this the third comment-grade interpretation in the same
family as A055834 and A007052 (`results/king-subfamilies.md`).

Draft comment, staged, jasonp's call:

> a(n) is the number of column-convex polyplets with n+1 cells (column-convex
> king-lattice animals: sets of cells of Z² whose columns are each a contiguous
> run, connected under king moves, counted up to translation) that are directed
> in the four-step cone {N, NE, E, SE} from the bottom cell of the leftmost
> column. Equivalently, those whose column-bottom profile never drops by more
> than one row from one column to the next; cutting the profile at each drop
> gives the INVERT relation to A007052 above a combinatorial meaning, A007052
> being the same class with the profile nondecreasing. Verified for n <= 19.
> Cf. A007052, A187077, A055834, A006770.

### (ctrlB, column-convex): novel, and the only column-convex cell with no closed form

1, 4, 18, 79, 339, 1423, 5872, 23909, 96336, 384934, 1527712, 6029421,
23686066, 92685759 (250 terms: `results/mk_ccctrlb_terms_n250.txt`).

"Every local minimum of `b` at the global minimum" is not a local rule on the
profile steps, so the transfer matrix has to carry the height above the running
minimum, and the state count is O(n²) rather than O(n). Cost measured on
gympie: n = 150 in 5.3 s / 194 MB, n = 250 in 66.3 s / 938 MB. Those two fix
the scaling at O(n^4.95) in time and O(n^3.2) in memory, which puts n = 400 at
about 11 minutes and 4 GB.

- µ = 3.811527945110 (quoting 12 digits: the conservative floor from the
  raw-ratio cross-check at N vs N−60 is 10, the Aitken cross-check is 40, and
  the ratio's own increment at n = 250 is 5e−14 under a geometric correction).
  θ = 0. That correction has ratio 0.895759813791, and
  `µ × 0.895759813791 = 3.41421356237` = **2+√2** to twelve digits: the
  subdominant singularity of this cell is the dominant singularity of the
  (dir5, column-convex) cell above it, as the inclusion dir5 ⊂ ctrlB predicts.
- **Not rational**: no constant-coefficient recurrence of order ≤ 12
  (`prec_guess prec … 12 0`, EXCLUDED, rank 13 of 13).
- **Not D-finite** in order ≤ 12 / degree ≤ 12, nor order ≤ 14 / degree ≤ 8.
- **Not algebraic** in degree ≤ 8 / t-degree ≤ 14, nor degree ≤ 6 / t-degree ≤ 20.
- µ itself: PSLQ finds no integer relation of degree ≤ 4 at height ≤ 10⁵, and
  the degree 5–8 hits fail the capacity test, so no minimal polynomial of that
  size.

**Novelty: no OEIS match** on nine terms or on the six-term prefix.

The caveat that keeps this honest: `ctrlB` is not a natural class, it is the
RED control that turned out to be its own sequence (`results/directed-cone-anchor.md`,
`results/multi-directed.md`). Its interest is that column-convexity reduces the
other four directedness predicates to *rational* generating functions and does
not do that here: this is the only cell of the column-convex column with no
closed form.

### (dir4, HV-convex): novel, same growth constant as unrestricted HV-convex

1, 4, 15, 53, 177, 567, 1767, 5417, 16465, 49897, 151288, 459836, 1402387,
4292477 (700 terms: `results/mk_hvdir4_terms_n700.txt`).

HV-convexity is `b` valley-unimodal and `t` peak-unimodal (Corollary 4);
Proposition 2 adds `d ≥ −1`, which only bites on the descending part of `b`.

- µ = 3.128943269730886252277447995387754160532091221904, which agrees with
  the unrestricted HV-convex-by-area constant (Phase 2b, 199 digits,
  `results/convex-polyplets.md`) in **every one of the 49 significant digits
  measured here** (`convex_growth.py` trusted-digit count 51, of which 49 are
  significant digits of µ). The discriminator `d_n/d_(n-1)`
  (`convex_growth.py`) is **0.803651401483** for dir4 against **0.481008794**
  for unrestricted HV-convex, both flat to all digits printed and both
  confirming `theta = 0` (geometric correction, no branch point) on their own
  series. **Read those two rates with the correction of 2026-08-06 below**: the
  diagnostic reports the largest correction present, not the whole spectrum,
  and the 4-cone series turns out to carry 0.481008794 as well — behind an
  extra exponential at 0.803651401483 = 2.5145796…/µ that the restriction
  creates. The restriction changes the amplitude too, C = 0.45030318571234118235
  against 0.97445221313500464915. The ratio of the two series,
  `a_dir4(n)/a_HV(n)`, converges to that amplitude ratio; extrapolated
  directly (`experiments/ratio_amplitude.py`, Aitken on the ratio sequence
  itself, cross-checked n=600 vs n=700) it is **54 trusted digits**:
  0.462109049209942440035662387700305832841163439729980425 — so a fixed
  46.2109049...% of HV-convex king animals are 4-cone directed in the limit.
  PSLQ on that constant at the trusted 54 digits finds **no integer relation
  in any in-capacity box** (degree ≤ 12 at height ≤ 1e2, ≤ 5 at 1e4, ≤ 3 at
  1e6, ≤ 2 at 1e8): the amplitude ratio has no small algebraic form. The
  bijection is ruled out, but not by "different subdominant singularities" —
  that reading of Table B is wrong. It is ruled out because the 4-cone class
  splits into a half growing at µ and a half growing at 2.5145796… with no
  counterpart on the unrestricted side (`results/hv-growth-sandwich.md`,
  Proposition 7), and because the amplitude ratio has no small algebraic form.
- **Not D-finite** at order ≤ 24 / degree ≤ 24 and **not algebraic** at
  degree ≤ 20 / t-degree ≤ 20, the same boxes Phase 2a cleared for the
  unrestricted series. The 4-cone restriction does not simplify the Mirage.

**Novelty: no OEIS match** on nine terms or on the six-term prefix.

## One correction to the record: the multi-directed row is A222205

`results/multi-directed.md` had to leave its novelty check open because
oeis.org answered 403; that was a User-Agent problem, and
`experiments/oeis_lookup.py` gets through. Multi-directed king animals are
**A222205**, "Number of multi-directed animals with n vertices" (Sloane, Feb
2013, entered from the same Bacher paper Phase 1c pinned the definition from).
All 23 of the entry's terms match ours exactly. The plan's grid table called
that row NOVEL; corrected there and in `results/multi-directed.md`.

What survives is not the novelty but the extension: the entry has 23 terms, no
b-file, no growth constant, and a formula line that only points at Bacher's
Theorem 9. We have 200 terms and µ to twelve digits. That is b-file and
comment material for Phase 4, not a new sequence.

The three other unfiltered "novel" labels were re-checked at the same time and
all hold: HV-convex by area (1,4,16,61,221,766,2566,8390), HV-convex by
semiperimeter (1,2,9,36,154,668,2916,12740) and control B unfiltered
(1,4,20,106,576,3179,17736,99748) all return NO MATCH.

## The kill criterion did not fire

The plan's rule: stop if the first three cells attempted all land on existing
OEIS entries. In the plan's stated order,

1. multi-directed × column-convex → A187077, an existing entry (Proposition 5);
2. directed × HV-convex → the already-banked novel convex-polyplet series
   (Corollary 4), not an OEIS entry;
3. half-plane × column-convex → A018902, an existing entry.

Two of three, not three of three, so the phase continued to the cells that
Findings 1 and 2 of `results/middle-kingdom-grid.md` had left genuinely open.
That was the right call: two of the three remaining cells are new sequences,
and the third ((ctrlB, column-convex)) is the only non-D-finite cell in the
column-convex column.

The banked meta-finding (`results/king-subfamilies.md`: classical restrictions
collapse king animals into known territory) survives Phase 3, sharpened. It is
not that the restricted classes are uninteresting, it is that **convexity
subsumes directedness**: HV-convexity implies 5-cone directedness, staircase
implies both cones, and column-convexity implies multi-directedness. Eight of
the twelve cells collapse for that reason alone.

## Tools, gates, provenance

| file | role |
|---|---|
| `cpp/middle_kingdom_tm.cpp` → `build/middle_kingdom_tm` | column transfer matrix, modes `cc ccmono ccdir5 ccdir4 ccctrlb hv hvdir4` + RED controls `ccdir4bad ccctrlbbad` |
| `cpp/directed_cone_anchor.cpp` mode `grid` | extended from 16 to 20 cells (the `mdir` row) |
| `tests/gate_middle_kingdom.py` (`make gate-middle-kingdom`) | GREEN 2026-08-05 |
| `tests/gate_king_grid.py` (`make gate-king-grid`) | GREEN, now with the eight collapses and the four non-collapses |
| `experiments/oeis_lookup.py` | read-only OEIS novelty check (oeis.org 403s some clients; a plain UA gets through) |
| `experiments/convex_growth.py` | growth constants; gained `--trust` and a leading-zero fix in the PSLQ path |
| `experiments/ratio_amplitude.py` | amplitude ratio of two series sharing a dominant singularity, Aitken + trusted digits + explicit PSLQ boxes (Phase 0, `docs/middle-kingdom-followups-plan.md`) |

Reproduce (all on a laptop, gympie, `git=54440c2-dirty`, 2026-08-05):

```
make build/middle_kingdom_tm build/directed_cone_anchor
make gate-middle-kingdom gate-king-grid                       # 20 s
build/middle_kingdom_tm ccdir5 700 > results/mk_ccdir5_terms_n700.txt      # 2.9 s
build/middle_kingdom_tm ccctrlb 250 > results/mk_ccctrlb_terms_n250.txt    # 66 s, 938 MB
build/directed_cone_anchor grid 14 8 > results/mk_grid20_n14.txt           # 512 s wall / 3673 s cpu, 8 threads
python3 experiments/convex_growth.py results/mk_ccdir5_terms_n700.txt
python3 experiments/oeis_lookup.py 1,4,17,71,289,1149,4481,17209,65281
python3 experiments/convex_growth.py results/mk_hvdir4_terms_n700.txt --prec 500 --algdeg 20 --maxcoeff 100000000
python3 experiments/convex_growth.py results/convex_area_terms_n700_king.txt --prec 500 --algdeg 20 --maxcoeff 100000000
python3 experiments/ratio_amplitude.py results/mk_hvdir4_terms_n700.txt results/convex_area_terms_n700_king.txt \
        --prec 500 --window 60 --drop 100                     # amplitude ratio, 54 trusted digits, PSLQ negative
```

Series files: `results/mk_{cc,ccdir5,ccdir4,hvdir4}_terms_n700.txt`,
`results/mk_ccctrlb_terms_n250.txt`, grid `results/mk_grid20_n14.txt`.

## Open

- No proof that (ctrlB, column-convex) and (dir4, HV-convex) are non-D-finite;
  both are exclusions in a box, like the unrestricted HV-convex verdict they
  sit beside.
- (ctrlB, column-convex)'s box is the smaller of the two only because its
  series is 250 terms rather than 700. Extending it to n = 400 (measured cost
  above: about 11 minutes and 4 GB, single core) would carry the exclusion to
  roughly order <= 16 / degree <= 16 and add a few digits to µ. Not run; no
  current claim needs it.
- ~~(dir4, HV-convex) sharing the unrestricted constant to 49 digits looks like
  a theorem waiting.~~ **CLOSED 2026-08-05** (`results/hv-growth-sandwich.md`,
  followups Phase 1). It is a theorem, and it is not a bijection. Proposition 6:
  every class between staircase and HV-convex has growth constant µ, so the
  4-cone condition was never special. The proof factors an HV-convex animal by
  its two unimodality phases into three blocks, shows the two outer blocks are
  stacks (A001523, sub-exponential) and that the middle block is a staircase
  animal, and squeezes. A225114 therefore has growth constant µ as well,
  measured here to 204 digits. The two series' *subdominant* behaviour is
  explained by the same factorisation, settled 2026-08-06: **Table B's numbers
  are right and the plan's reading of them is wrong.** Splitting the 4-cone
  series by whether an animal's unimodality-phase path visits `(0,1)` gives
  `D = D_asc + D_desc` (engine mode `hvdir4asc` and the difference), and
  `D_asc` — 4-cone-directed animals, counted not extrapolated — has
  `d_n/d_(n−1) = 0.48100879371`, the same rate as HV-convex, trusted to 76
  digits as `λ_2/λ_1` of that series' spectrum. So the restricted series does not *lack* the shared 0.4810; it
  carries an extra exponential in front of it at 2.51457964387872918851…, the
  growth constant of the truncated descending block, and `d_n/d_(n−1)` only
  ever reports the largest correction present. **Proved:**
  `lim D_asc(n)^(1/n) = µ` and `lim D_desc(n)^(1/n) = 2.5145796…`
  (Proposition 7). **Conjectured, measured to 76 and 64 trusted digits:** the
  sharp asymptotics that turn those rates into Table B's diagnostic
  (Conjecture 8). Corroboration: the two halves' exponential spectra, read by
  Prony at 1500 digits, are disjoint and interleave to give the whole series'
  — `λ_1(D_desc)` matches the block's to 226 bearable digits and
  `λ_2(D_asc)` the staircase's to 76, with negative controls at 0–1 digits.
  **The amplitude ratio, 2026-08-06:** no closed form, but it now has an
  explicit expression. Both amplitudes are residues of the same staircase
  resolvent, and the block algebra writes the two feed vectors down, so
  `r = (1/2)(w4·φ)/(w·φ)` — a ratio of two `q`-series at `q = 1/µ`, contracted
  against the staircase operator's Perron eigenvector `φ`, which is itself the
  bounded solution of `φ(h) = (2 − x^{h−1})φ(h−1) − φ(h−2)` (Propositions
  9–11 of `results/hv-growth-sandwich.md`; conditional only on the two
  amplitudes existing, which is weaker than Conjecture 8). The identity and the
  re-measured split series agree to 293 digits, taking the ratio from Table B's
  54 trusted digits to 251, and PSLQ is negative in every enlarged box —
  degree ≤ 45 at height ≤ 1e2 through degree ≤ 2 at 1e40, and over `Q(µ)` up to
  `µ`-degree 5 / `r`-degree 6. By-product: `µ` now comes out of the same
  recurrence by shooting, 987 digits in 1.6 s with no series at all.
- The A018902 comment is drafted, not submitted; submission is jasonp's call,
  gated on the viva.
- Nothing outstanding on the twelve cells themselves.
