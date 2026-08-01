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

**Still open, and unresolvable by search:** whether the
Northcott-on-growth-constants endgame appears elsewhere. Absence cannot be
established from a database; the two remaining levers are (a) MathSciNet's
citation graph on BM-R 2002 and the Haruspicy papers -- a weekday walk-in at
Pitt Hillman or CMU Hunt, guest pass, read-only -- and (b) asking Rechnitzer
(UBC) directly. jasonp's call; external contact is his alone.

**Still wanted:** Haruspicy 1 itself (Adv. Appl. Math. 30 (2003) 228-257,
Elsevier, no arXiv preprint found). It supplies the combinatorial
section/density machinery behind Haruspicy 2's Theorem 1, not the test, so
it is no longer blocking anything. **[low]**
