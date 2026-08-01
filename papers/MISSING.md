# MISSING — citations we want but couldn't pull full text for

Papers we reference but do **not** have a local copy of and could not access a free
version of online. For university-library lookup. Add to this list any time a paper
can't be found; remove (and drop the PDF in `papers/`) once obtained.

Format: `Author(s), "Title," Venue Vol (Year) pages. DOI/ID. — why we want it. [priority]`

## High priority

_(none outstanding — Barequet–Moffie 2007 and Mertens 1990 obtained 2026-06-25)_

## Medium priority (the bounding-box / finite-lattice lineage we descend from)

- A. R. Conway, "Enumerating 2D percolation series by the finite-lattice method: theory,"
  J. Phys. A 28 (1995) 335–349. DOI 10.1088/0305-4470/28/2/011. — FLM theory (bounding-box
  Möbius decomposition = the architecture our 4-direction split sits inside). **[med]**
- A. R. Conway & A. J. Guttmann, "On two-dimensional percolation," J. Phys. A 28 (1995)
  891–904. DOI 10.1088/0305-4470/28/4/015. **[med]**
- I. G. Enting, "Generating functions for enumerating self-avoiding rings on the square
  lattice," J. Phys. A 13 (1980) 3713. — origin of the finite-lattice method. **[med]**
- G. Aleksandrowicz & G. Barequet, "Counting d-dimensional polycubes and nonrectangular
  planar polyominoes," IJCGA (2006); and "Counting polycubes without the dimensionality
  curse," Discrete Math. 309 (2009). DOI 10.1016/j.disc.2009.01.022. — canonical generalized-
  Redelmeier; generalizes by DIMENSION not adjacency (confirm they don't touch king). **[med]**

## Check for a free version FIRST (may not actually be missing)

- H. Tremblay & J. Vernay, "On the generation of discrete figures with connectivity
  constraints," RAIRO-Theor. Inf. Appl. 58 (2024) Art. 16. DOI 10.1051/ita/2024013.
  — **the source of the current world-record a(18) for A006770.** RAIRO-ITA is usually OPEN
  ACCESS — try rairo-ita.org directly before the library. Code: github.com/J-Vernay/discrete-figures.
- G. Barequet, M. Moffie, A. Ribó, G. Rote, "Counting polyominoes on twisted cylinders,"
  (venue uncertain — INTEGERS / Electronic J.? ~2006). — the cleanest "width W alone bounds
  TM cost" realization; want exact venue + free version.

## Obtained 2026-08-01 from jasonp's lattice-animal searches — all in papers/
Six papers, all now held. First-pass dispositions below; **one is worth
following up and it is not the one first flagged.**

- **G. Barequet, G. Ben-Shachar, M. C. Osegueda, "Concatenation arguments and
  their applications to polyominoes and polycubes," Comput. Geom. 98 (2021)
  101790.** Flagged sight-unseen as an attack on C2 (log-convexity) on the
  guess that concatenation supplies the missing injection. **Read: it does
  not.** The method is Fekete on quasi sub-/super-multiplicative sequences
  (Z(m+n) >= P(m+n)Z(m)Z(n)), which bounds *growth constants*, not
  log-convexity — a different inequality from a(n)^2 < a(n-1)a(n+1). C2 is
  unmoved and its "no clean injection is known" stands.
  **What it does bear on is the lambda bracket.** The super-multiplicative
  direction is already banked and superseded (Fekete gives
  lambda >= a(40)^(1/40) ~ 6.22, commit 8ae1462; the certified ladder's 6.543
  beats it). The open direction is **quasi-sub-multiplicativity, which yields
  UPPER bounds** — and our upper end, 9.3153, is the loose half of the
  bracket. Whether king animals admit a concatenation-based sub-multiplicative
  bound below 9.3153 is a live question that would shorten a sentence in the
  paper. Not attempted. **[the one worth a look]**
  **LOOKED, 2026-08-01 — CLOSED, no gain** (`results/concatenation-upper-bound.md`,
  `experiments/concatenation_bound_check.py`). Priced first: with `a(40)` banked,
  a degree-2 `P` would give `lambda <= 7.745` (degree 3 gives 8.642; degree 4
  gives 9.642 and helps nothing), and the measured `a(m+n)/(a(m)a(n))` grows
  linearly in `m+n`, so 40 terms refute nothing. Then the proof: BBO's
  lexicographic split shatters a king comb into `~n/4` components (measured), so
  the reassembly code is `n^Theta(n)`, not polynomial; the centroid/spanning-tree
  split that keeps both sides connected cannot prescribe the halves to within the
  `O(1)` that Theorem 1(a)/(b) needs. Decisive: the same lemma for ordinary
  polyominoes would give `lambda_poly <= 4.3828`, beating Barequet-Shalah's
  4.5252 from published terms alone — it is a known-hard target, not an oversight.
- **G. Aleksandrowicz & G. Barequet, "Counting polycubes without the
  dimensionality curse," Discrete Math. 309 (2009).** The [med] want above is
  **CLOSED**: its open question was "confirm they don't touch king," and they
  do not — the algorithm is face-adjacency hypercubic throughout (each cell
  has 2d neighbours). Generalization is by dimension, not by adjacency, as
  suspected.
- **T. Mansour & R. Rastegar, "Enumeration of various animals on the
  triangular lattice," European J. Combin. 94 (2021) 103294** (also arXiv
  2011.05318). Baryiamonds, column-convex and convex polyiamonds by perimeter.
  Bears on the universality work's open item (polyiamonds, which need row
  conventions) and on the parked convex side quest.
- **L. L. Liu & Y. Wang, "On the log-convexity of combinatorial sequences,"
  Adv. Appl. Math. 39 (2007) 453-476** (also arXiv math/0602672). Held; the
  abstract-level read stands — closure operations plus three-term recurrences,
  and a(n) satisfies no known recurrence. Reading it would confirm the
  negative and sharpen *why* C2 is hard, which is worth a line in
  open-conjectures.md if anyone does it.
- **D. Gouyou-Beauchamps & G. Viennot, "Equivalence of the two-dimensional
  directed animal problem to a one-dimensional path problem," Adv. Appl. Math.
  9 (1988) 334-357.** Context for the directed-animal lineage behind the
  Bacher comparison bound and behind BM-R's heaps.
- **M. Bousquet-Melou, "q-Enumeration de polyominos convexes," JCTA 64 (1993)
  265-288.** For the convex side quest if revived.

Still un-obtained from that search, low value, not chased: Duchi-Rinaldi-
Schaeffer (Z-convex, 2008), Delest column-convex GFs (JCTA 1988),
Dubernard & Dutour (1996), Feretic & Svrtan (1996), Bousquet-Melou "New
enumerative results on two-dimensional directed animals" (1998).

## Notes
- arXiv-available (NOT missing): Jensen cond-mat/0007239 & 0007238, Conway 1610.09806,
  Jensen math/0506317, Guttmann-Jensen cond-mat/0603833, Clisby-Jensen 1111.5877,
  Barequet-Shalah 1906.11447, Shirakawa 2510.22446, Bui 2511.00461 & 2412.20143,
  Foster-Pinettes cond-mat/0210548, BM-Linusson-Nevo math/0701890, BM-Brak 0811.4415.
- In papers/: Jensen 2001, Jensen 2003 (ICCS), Barequet–Ben-Shachar 2024
  (counting_polyominoes_revisited.pdf), Vöge–Guttmann 2003,
  **barequet_moffie_2007_jensen_complexity.pdf, mertens_1990_lattice_animals.pdf,
  read_1962_cell_growth.pdf, klarner_rivest_1973_upper_bound.pdf,
  klarner_1967_cell_growth_problems.pdf** (added 2026-06-25).
- Also filed 2026-06-25: Mertens & Lautenbacher, "Counting Lattice Animals: A Parallel
  Attack," J. Stat. Phys. 66 (1992) 669 → mertens_lautenbacher_1991_parallel.pdf.

## Northcott + monotonicity => anisotropic non-D-finiteness (2026-07-15)
Need a literature check before claiming novelty: does the argument
"y-slices rational/integer, strip growth constants strictly increasing and
bounded => slice degrees unbounded by Northcott => two-variable GF not
D-finite" appear anywhere? Closest known: A. Rechnitzer, "Haruspicy and
anisotropic generating functions" (Adv. Appl. Math. 2003); "...2: bond
animals" (2006); "...3: SAPs" (JCTA 2006). Also check: J. Bell / S. Gerhold
/ M. Mezzarobba-adjacent non-D-finiteness criteria; Guttmann's solvability
tests; Bousquet-Melou anisotropic surveys. If truly absent, this is a
publishable stand-alone note.

**PARTIALLY DISCHARGED 2026-08-01 — and the target paper changed.** The
D-finiteness *test* the Haruspicy papers use is not in Haruspicy 1. Both
Haruspicy 2 (Theorem 15) and Haruspicy 3 (Theorem 5) attribute it verbatim
to **Bousquet-Melou & Rechnitzer, "Lattice animals and heaps of dimers,"
Discrete Math. 258 (2002) 235-274, Lemma 9** — which is free from
labri.fr/perso/bousquet and is now in `papers/` along with both Haruspicy
papers (arXiv math/0406450, math/0408054). Side-by-side comparison against
our dominant-pole dichotomy: `results/anisotropic-not-dfinite.md`. Summary:
the opening move (extract y-coefficients from the ODE to get a linear
recurrence with polynomial coefficients) is **shared and is theirs, 2002**;
everything after diverges — their conclusion is topological (finitely many
limit points of the whole pole set, via an asymptotic-in-n argument on the
leading coefficient), ours is arithmetic and effective (a degree bound on
one distinguished pole per slice, giving explicit (r,D) exclusion boxes).
Northcott appears in neither.

**REMAINING LEADS SWEPT 2026-08-01 — item now CLOSED.** The other names in
the original list were checked and none collides:

- **Bell, Gerhold, Klazar & Luca**, "Non-holonomicity of sequences defined
  via elementary functions," Ann. Comb. (2008), arXiv math/0605142 (saved to
  `papers/`). Method is **analytic** -- counting zeros of elementary and
  analytic functions -- and the class is sequences obtained by evaluating an
  elementary function at positive integers. T(n,H) is not of that form.
- **Gerhold**, "On some non-holonomic sequences," Electron. J. Combin. 11
  (2004): same analytic family.
- **Bell, Hu & Satriano**, "Height gap conjectures, D-finiteness, and weak
  dynamical Mordell-Lang," arXiv 2003.01255. The one paper found that pairs
  **heights with D-finiteness** -- but in arithmetic dynamics, bounding
  h(f(Phi^n(x))) along orbits of rational maps, with D-finite coefficient
  growth as an application. Different configuration entirely; not slice
  growth constants. Closest arithmetic-flavoured relative located, and not a
  collision.
- **Guttmann**, "Indicators of solvability for lattice models," Discrete
  Math. 217 (2000) 167-189: the programmatic source of the anisotropic-GF
  solvability test that Rechnitzer's programme answers, not a theorem in our
  configuration.
- Also noted: the classical arithmetic constraint (D-finite + integer
  coefficients + K rho^n n^alpha ==> alpha rational), used for quarter-plane
  excursions. Arithmetic, but about one sequence's asymptotic exponent, not
  a family of algebraic degrees.

**Verdict.** Every non-D-finiteness method located in this literature is
either topological (BM-R pole accumulation) or analytic (Klazar divergence;
BGKL zero-counting). Northcott-on-slice-growth-constants was not found.
Absence still cannot be established by search, so the paper now claims the
argument with that qualification stated explicitly rather than resting on
it -- see `paper/polyplets-report.tex`, "Relation to existing work", which
also records the ceiling (our method cannot reach D_A-finiteness).

Optional, not needed for the claim as now scoped: MathSciNet's citation
graph on BM-R 2002 (weekday guest pass, Pitt Hillman or CMU Hunt), or
asking Rechnitzer (UBC) directly. Both jasonp's call.

## STANDING NEXT ACTION: crawl the citation graph (jasonp, 2026-08-01)
**Nothing obtained so far has been forward-searched.** Every paper in this
session was found by keyword or by following references *backwards*; we have
never asked "who cites this?" for any of them. That is the one search
direction that could still surface a collision, because a 2026 paper reusing
BM-R's Lemma 9 with an arithmetic endgame would be invisible to every probe
run so far.

Do this when idle. Priority order, forward citations of:
1. **Bousquet-Melou & Rechnitzer 2002** (the criterion itself) — highest yield;
   anyone building on the non-D-finiteness test lands here.
2. **Haruspicy 2 and 3** — the programme's visible face.
3. **Chan & Rechnitzer 2018** — anyone extending CTM growth-rate bounds; would
   also catch a workaround for the locality/symmetry conditions we fail.
4. **Bevan-Brignall-Elvey Price-Pantone 2020** — anyone porting the
   inject-into-a-labelled-simpler-class template outside permutation classes.

Tooling: MathSciNet is the right instrument and needs a weekday walk-in guest
pass (Pitt Hillman or CMU Hunt, read-only — see the notes above). Google
Scholar's "Cited by" is the free approximation and can be done from the desk.

**Haruspicy 1 OBTAINED 2026-08-01** (jasonp, ScienceDirect) →
`papers/rechnitzer_2003_haruspicy1_anisotropic_gf.pdf`. Confirms the reading
above from the source: its content is the combinatorial section/density
machinery (coefficient of y^n rational, numerator degree <= denominator
degree, denominator a product of cyclotomic polynomials, plus a tight
multiplicative upper bound), not a D-finiteness test. Also filed from the
same issue: `klazar_2003_non_p_recursiveness_matchings.pdf` (Haruspicy 2's
reference [13], adjacent prior art on non-P-recursiveness).
