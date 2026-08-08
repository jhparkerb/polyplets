# Sortie novelty sweep — N1..N6

2026-08-06. `docs/sortie-publication-plan.md` §5: the six questions that gate
Papers 2 and 3. No compute beyond two laptop-second probes. Method as the plan
specifies: the local `papers/` neighbourhood first, then targeted searches, then
read the source rather than the snippet — every verdict below rests on a PDF now
held locally or on a measurement in this repo, not on a search result summary.

**Headline: one real collision, N3.** The phase-block decomposition of Lemma 1
is published, for convex polyominoes on the square and honeycomb lattices, by
Gouyou-Beauchamps & Leroux. It does not touch any of Paper 3's results, but it
changes what may be called new, and it wants citing in three places.

| # | question | verdict |
|---|---|---|
| N1 | is the staircase squeeze folklore? | **not found as a theorem**, but its conclusion is classical for square-lattice polyominoes by area, and its ingredients are all in the N3 paper |
| N2 | HV-convex *king* animals under another name? | **no** — not in OEIS, not in the literature searched |
| N3 | block factorisation in the column-convex literature? | **YES — collision.** Gouyou-Beauchamps & Leroux 2004 §2.3 |
| N4 | published upper bound on λ_polyplet? anything past Bacher's 6.475? | **no** on both |
| N5 | universal (lattice-class) diagonal law in print? | **no**, but a strong analogue exists in the polycube dimension-defect line |
| N6 | collision with Rechnitzer's Haruspicy? | **no** — different object, and the shared step was already credited |

---

## N3 — the collision, stated plainly

**Gouyou-Beauchamps & Leroux, "Enumeration of symmetry classes of convex
polyominoes on the honeycomb lattice", FPSAC 2004 / arXiv:math/0403168**, §2.3
"Growth phases of convex polyominoes", now in
`papers/gouyou-beauchamps_leroux_2004_convex_polyominoes_honeycomb.pdf`:

> Any convex polyomino can be decomposed into blocks according to the growth
> phases, from left to right, of its upper and lower profiles. […] The state in
> which a column lies is described by an ordered pair (i, j), i, j = 0, 1, 2;
> the first component corresponds to the upper profile and the second, to the
> lower profile. […] the transitions from the state 1 to the state 0 and from
> the state 2 to the state 1 or 0 are impossible. Now, a block H_ij is
> characterized by a maximal sequence of consecutive columns which are in the
> state (i, j).

Then, in the same section:

- `H00` and `H22` "are in fact **stack polyominoes**" — our Lemma 2's outer
  blocks, identified the same way;
- `H01, H10, H12, H21` "are in bijection with each other by horizontal and
  vertical reflections and are thus **equinumerous**" — the reflection argument
  of our Proposition 9;
- the middle blocks are **staircase polyominoes**, `H02 = Pa = H20`, and they
  record that Pa by area is A006958 with a q-Bessel-quotient generating series.

So the shape of `results/hv-growth-sandwich.md`'s Lemma 1 — column states as a
pair of monotone phase bits, blocks as maximal runs, transitions one-way, outer
blocks stacks, middle block staircase — is **published prior art**, for convex
polyominoes on the honeycomb lattice, twenty-two years ago. §2.3 cites nobody
for the decomposition, and the square-lattice companion (Leroux, Rassart &
Robitaille, *Adv. Appl. Math.* 21 (1998) 343–380,
`papers/leroux_rassart_robitaille_1998_convex_polyominoes_symmetry_classes.pdf`)
does not contain it, so 2004 is the earliest source this sweep can point at.

**The 1998 companion, read (correction, same day).** This note first said the
Leroux–Rassart–Robitaille scan had no text layer. Wrong: it extracts cleanly
(63 KB, Type 1 fonts, dvips), and an empty grep for the 2004 paper's vocabulary
was mistaken for a broken scan. Read properly, it does **not** carry the
growth-phase decomposition. Its route is Temperley–Bousquet-Mélou: convex
polyominoes are assembled from partitions, stacks, the new shifted stacks, and
directed convex polyominoes, the last quoted from Bousquet-Mélou 1996 Theorem
3.4 as a ratio of q-Bessel-type series (their Proposition 4), and Burnside then
gives the symmetry classes. So the N3 collision rests on the **2004 paper
alone**; the 1998 paper is the square-lattice ancestor for the building blocks
(stacks, directed convex), not for the phase blocks. In the 2004 paper §2.3
carries no citation for the decomposition itself.

**Chasing the decomposition's own ancestry (2026-08-06).** §2.3 cites nobody
for it, so the fifteen references of the 2004 paper were read and the three
plausible earlier homes chased down:

- **[3] Gouyou-Beauchamps & Leroux, FPSAC'04** is the French extended abstract
  of this same paper ("this is the full version of a paper presented at the
  FPSAC Conference in Vancouver"), not an earlier source.
- **[8] Leroux, Rassart & Robitaille 1998** — read, see the correction above.
  Temperley–Bousquet-Mélou strata, not phase blocks. The 2004 introduction
  credits it only for the orbit/Burnside approach.
- **[2] Denise, Dürr & Ibn-Majdoub-Hassani, FPSAC'97**, the obvious candidate
  because random generation needs a constructive decomposition — recovered from
  the Wayback Machine (the fpsac.org copy is gone) and now in `papers/`. It
  says outright: "En utilisant la technique de « décomposition par strates »",
  the Temperley technique "largement développée par Bousquet-Mélou". Column at
  a time, not phase blocks.
- **[6] Ibn-Majdoub-Hassani, PhD thesis, Orsay 1996** — the one item not
  obtained (`papers/MISSING.md`). It is the source for the C-convex hexagonal
  class itself, and its co-author's 1997 paper uses strata, so it is unlikely
  to hold the phase blocks; unlikely is not checked.

On that evidence Gouyou-Beauchamps & Leroux 2004 is the earliest source for the
decomposition, and citing it is right.

**What survives as ours.** Their decomposition drives exact generating series
for a solvable family. Ours is applied to a family with no exact solution, and
what is done with it is different:

1. the class is **HV-convex king animals**, not convex polyominoes: columns are
   intervals with king adjacency, and the middle-block kernel is
   `min(h,h') + 1`, the square lattice's `min(h,h')` plus one — which is the
   whole of the difference between µ = 3.1289… and the square analogue's
   2.3091…;
2. **Proposition 6** — every class between staircase and HV-convex has growth
   constant µ — is a statement about all intermediate classes, which an exact
   solution of two particular classes does not give;
3. the **operator-level** reading (block-triangularity, the 4-cone floor
   rewriting exactly one of the two copies of `min(h,h')+1`) and everything it
   buys: the phase split of the series, ν = 2.5145…, the amplitude identity
   `r = (1/2)(w4·φ)/(w·φ)`.

**Actions.** Cite Gouyou-Beauchamps–Leroux at Lemma 1, at Lemma 2's stack
identification, and at Proposition 9; drop any wording that presents the
decomposition as new; keep Propositions 6, 7, 10, 11 as ours.

---

## N1 — is the squeeze folklore?

Two things are true at once.

**The conclusion is classical for square-lattice polyominoes by area.** Bender
(1974) has convex polyominoes by area growing at 2.30914…; the staircase
(parallelogram) subclass is A006958, and measured here on a 400-term exact DP
(`experiments/square_staircase_area.py`) its ratio is flat at

    2.309138593330495     (n = 200, 300, 400 — identical to 16 digits)

so the subclass carries the full exponential growth of the superclass, exactly
as Proposition 6 says for the king lattice. Anyone who wanted this for the
square lattice could have read it off the two solved models.

**The theorem is not folklore as far as this sweep can see.** No source found
states "every class between staircase and HV-convex has the same growth
constant", nor the squeeze that proves it, nor its area analogue for any
lattice. The nearest published relatives:

- Barequet, Ben-Shachar & Osegueda, *Concatenation arguments…*, Comput. Geom.
  98 (2021) 101790, §3, states the **lower** half as a remark: "one can
  identify a family F, a subset of animals on the original lattice, which is
  closed under concatenation. Clearly […] if the family F has a growth constant
  λ_F of its own, then λ_Z ≥ λ_F." The matching upper half — the block
  factorisation that shows the superclass exceeds the subclass only
  sub-exponentially — is not there.
- Kim & Pinna, arXiv:2509.04568 (Sep 2025), builds growth constants for walk and
  surface classes by van Rensburg–Whittington concatenation; no convex
  subclasses, no king lattice.

**Reading for the paper.** Present Proposition 6 as the king-lattice theorem it
is, note that the square-lattice conclusion is implicit in the solved models,
and do not claim the technique itself is new — the ingredients are standard,
and after N3 the decomposition is demonstrably not ours.

## N2 — HV-convex king animals under another name?

Not found. OEIS lookup on the by-area series `1, 4, 16, 61, 221, 766, 2566,
8390, 26982` returns NO MATCH (`experiments/oeis_lookup.py`, read-only,
2026-08-06). Searches for king/8-connected/next-nearest-neighbour convex
enumeration return the ordinary-polyomino convexity literature only. The one
place king animals appear in the enumeration literature is as **whole**
families: Mertens, *J. Stat. Phys.* 58 (1990) 1095 computes perimeter
polynomials for "the square lattice with next nearest neighbors" to s = 13
(`papers/mertens_1990_lattice_animals.pdf`), and Bacher (2013) solves the
directed and multi-directed cases. No convexity constraint anywhere on the king
lattice.

## N4 — a published upper bound on λ_polyplet?

None found, and nothing beating Bacher's 6.475 as a lower bound. The
upper-bound literature — Klarner–Rivest, Barequet–Shalah, Barequet–Ben-Shachar,
Kim–Pinna 2025 — is square lattice, hypercubic, polyiamond and polycube; the
king lattice is absent from all of it, including the 2025 concatenation paper
that would have been the natural place. This reconfirms
`docs/proofs/polyplet-upper-bound.md`'s standing claim rather than adding to
it: the 9.3154 certificate has no competitor because there is no incumbent.

Also checked: percolation-side sources for the king lattice (the
next-nearest-neighbour square lattice) give perimeter polynomials and cluster
statistics, not growth-constant bounds.

## N5 — a universal diagonal law in print?

Not found for lattice-animal height triangles. `results/diagonal-closed-forms.md`
already recorded "no prior published literature on T(n,n−k) closed forms for
lattice animals" (2026-07-10); this sweep adds the family that comes closest,
which is a different defect parameter in the same spirit:

- Barequet, Barequet & Rote, "Formulae and growth rates of high-dimensional
  polycubes", *Combinatorica* 30 (2010) 257–275: for fixed n, the number of
  polycubes is a polynomial in the dimension d.
- Barequet & Shalah, "Counting n-cell polycubes proper in n−k dimensions"
  (SoCG 2015; *European J. Combin.* 63 (2017) 146–163): for **general** k the
  formula has the proved shape `2^{n−2k+1} n^{n−2k−1} (n−k) h_k(n)` with `h_k`
  polynomial.

That is the same phenomenon as ours — fix the defect, get polynomial ×
exponential, with the polynomial's degree governed by the defect — with the
defect measured in **dimension** rather than in **height**, on one lattice
family rather than on a class of lattices. Our Theorem A quantifies over every
row-local lattice and is proved once for all of them, which theirs is not; but
Paper 2 should cite this line as the precedent for the shape of the statement
rather than presenting the phenomenon as unheard-of.

**Both papers obtained and read 2026-08-06** (`papers/barequet_barequet_rote_2010_*`,
`barequet_shalah_2017_*`, plus `asinowski_etal_2012_*` for the explicit k=3 case).
Read from the sources, the parallel is closer than the abstracts suggested:

- **Barequet–Shalah Theorem 1** is `DX(n,n−k) = [2^{n−k}/(k−1)!]·n^{n−2k−1}·(n−k)
  ·P_{3k−4}(n)` with `P` **monic of degree exactly 3k−4** — a degree previously
  conjectured and proved there for the first time. Compare our `deg P_k ≤ k`.
- Their stated payoff is the same as ours: *"DX(n,n−k) can be extrapolated from
  3k−3 known values"* — prove the degree, then fit from finitely many rows. That
  is exactly the P_k protocol, and it is the strongest argument that our
  fit-with-a-proved-degree-bound practice is standard rather than suspect.
- What they do not have is our **sharp onset** (n ≥ 2k+1, failure at n=2k verified
  on all banked data), and they work in one lattice family where Theorem A is
  proved for every row-local lattice at once.
- BBR 2010 Theorem 8 is the dimension-polynomial statement; their Theorem 12
  derives the ratio limit **from Madras 1999**, the same citation we now use for
  `a(n+1)/a(n) → λ`. The polycube line already leans on it.

Three things from Asinowski et al. that Paper 2 should take on board:

- **"Diagonal formulae" is their term too.** They write "so-called *diagonal
  formulae*, that is, formulae for DX(n, n−k)". Our naming for T(n, n−k) is not
  idiosyncratic; use the established phrase and cite the line.
- **The shape was predicted before it was proved, in statistical physics.**
  Peard & Gaunt (J. Phys. A 28 (1995) 6109–6124, p. 6113 eq. (2.15)) predicted
  `DX(n,n−k) = 2^{n−2k+1} n^{n−2k−1} g_k(n)` with `g_k` polynomial; Luther &
  Mertens supplied explicit `h_k` for k ≤ 7; Barequet–Shalah proved it in 2017.
  A conjecture-then-proof arc for exactly our statement shape, and the earliest
  occurrence is 1995, not 2010.
- **They have a leading-coefficient law too, and ours rhymes with it.** Their
  refined conjecture, from inspecting the fitted polynomials, is that `h_k`'s
  leading coefficient is `2^{k−1}/(k−1)!`. Ours (`docs/proofs/diagonal-law.md`)
  is `25^k/k!`. Same phenomenon — an explicit exponential-over-factorial leading
  coefficient for the defect polynomial — on the dimension defect rather than
  the height defect. Theirs was found by inspection and then proved; ours comes
  with a mechanism (`results/defect-gas.md`: 25 = 16 + 9 is the two-cell cluster
  weight, the k! is unordered defects). Caveat on the parallel: monic-versus-not
  is a normalisation choice, so the shared content is *that* there is an explicit
  exponential-over-factorial leading coefficient, not that the constants match.

### N5 RE-RUN 2026-08-06 with the field's own search key — two more families

The earlier sweep was run without knowing that this literature calls these
objects **"diagonal formulae"**. Re-running on that phrase plus bounding
box/perimeter found two families the first pass missed. Neither collides with
our theorem, but both are prior art for the *shape*, and one of them is the
same triangle we compute.

- **Barequet & Magal, "Automatic generation of formulae for polyominoes with a
  fixed perimeter defect," Comput. Geom. 108 (2022/23) 101919.** A third defect
  parameter — perimeter — with an algorithm that enumerates reduced polyominoes
  of a given defect and emits closed formulae and generating functions, k ≤ 5
  (previously k ≤ 3). Not held; ScienceDirect, and no free copy on the author's
  own publication page. Added to `papers/MISSING.md`.
- **OEIS A308359** (R. J. Mathar, 2019): fixed polyominoes by bounding-box
  width, height free — **our T(n,H) transposed**, for the square lattice. It has
  `T(n,n−1) = 4n−8` (n ≥ 3) as known and `T(n,n−2) = 8n²−51n+86` (n ≥ 5) as an
  open conjecture. So the height/width defect diagonal for polyominoes is not
  unheard-of; it is a seven-year-old OEIS entry.
  **And our Theorem A settles the conjecture** — see the corollary in
  `docs/proofs/universal-diagonal-law.md` and
  `experiments/oeis_a308359_check.py`.

### What Paper 2 may claim, after all of this

The *phenomenon* — fix a defect, get a polynomial times an exponential, degree
governed by the defect — is established, named, and has at least four instances
in print or in OEIS: dimension (Peard–Gaunt 1995 → Barequet–Shalah 2017),
perimeter (Barequet–Magal 2022), bounding box for square polyominoes (A308359,
partly conjectural), and ours. **Paper 2 must not present the phenomenon as
new.** What survives, in decreasing order of confidence:

1. **The universal theorem.** One proof covering every row-local lattice at
   once, with b = |D| the drift count entering as b^H. Every published instance
   is one lattice family. This is the contribution.
2. **The sharp onset.** n ≥ 2k+1, with failure at n = 2k as a non-cancellation.
   No onset statement was found on any of the other three; A308359's "n ≥ 5"
   is 2k+1 at k=2, read off data rather than derived.
3. **The first closed forms for king animals by height**, and the machinery
   (`results/defect-gas.md`, `docs/proofs/grand-form.md`) that produces the
   coefficients from a finite cluster table rather than by fitting.
4. **A settled conjecture in someone else's triangle** as evidence that 1 and 2
   are worth having.

Not ours, and to be cited rather than claimed: the statement shape, the term
"diagonal formulae", and the prove-the-degree-then-interpolate protocol, whose
payoff Barequet–Shalah state explicitly ("can be extrapolated from 3k−3 known
values").

## N6 — collision with Haruspicy?

No. Read from the local PDFs rather than from abstracts online:

- Haruspicy 1 (Rechnitzer, *Adv. Appl. Math.* 30 (2003) 228–257) proves the
  cyclotomic-denominator structure for **bond** animals.
- Haruspicy 2 (math/0406450) proves non-D-finiteness for **self-avoiding
  polygons**, square and hypercubic.
- Haruspicy 3 (math/0408054) proves it for **directed bond animals**, and its
  abstract records that directed **site** animals are solved — which is why the
  programme never turns toward our object.

Our object is site animals (king) by height, and the argument is arithmetic
(Northcott on the degree of one distinguished pole) where theirs is topological
(accumulation of the whole pole set). The one shared ingredient — extracting
the y-coefficients of the ODE to get a linear recurrence, Bousquet-Mélou &
Rechnitzer 2002 Lemma 9 — was already identified and credited in
`results/anisotropic-not-dfinite.md` (2026-08-01, "Prior art, read and
compared"). Nothing to add and nothing to retract.

---

## What this changes in the plan

- **Paper 3** is not blocked. Proposition 6, the µ identification, the λ
  bracket, the directed constant and the grid collapses all stand. The
  write-up must credit Gouyou-Beauchamps–Leroux for the decomposition and
  present the square-lattice version of Proposition 6's conclusion as known.
- **Paper 2** is not blocked. Cite the polycube dimension-defect line as the
  precedent for the shape of the diagonal law.
- Two PDFs added to `papers/`; two references added to `papers/MISSING.md`.

## Reproduce

```
python3 experiments/square_staircase_area.py --nmax 400   # the 2.3091385933 probe
python3 experiments/oeis_lookup.py 1,4,16,61,221,766,2566,8390,26982
pdftotext papers/gouyou-beauchamps_leroux_2004_convex_polyominoes_honeycomb.pdf - \
  | sed -n '/Growth phases of convex polyominoes/,/H00 and H22/p'
```
