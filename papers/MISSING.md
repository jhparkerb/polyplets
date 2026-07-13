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
