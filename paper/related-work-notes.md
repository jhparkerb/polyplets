# Related work / attribution notes (for the eventual related-work pass)

Purpose: make sure we credit prior work and do NOT claim as ours anything that is
classical. Verdict up front: **the transfer-matrix machinery, the C-finiteness of
fixed-height rows, and the rational generating functions are all classical.** Our
only genuine new contributions are the specific *values* a(19) of A006770 and its
companions Free(19)/OneSided(19) — not the methods or the structural observations.

## What is classical (must cite, must NOT claim)

**Transfer-matrix method ⇒ rational GF / C-finite (the textbook fact).**
- R. P. Stanley, *Enumerative Combinatorics*, Vol. 1 — §4.7 "The Transfer-Matrix
  Method" (and §4.1, the basic theorem on rational generating functions). The
  closed form a(n) = Σ Pᵢ(n)·γᵢⁿ over roots γᵢ of det(xI − A) is exactly the
  C-finite statement. Any bounded-width/height counting that proceeds
  column-by-column has a rational GF. *This is the source for everything we said
  about fixed-height rows being C-finite.*
  (https://www.cambridge.org/core/books/enumerative-combinatorics — verify the
  exact §/edition at submission.)

**Polyominoes via transfer matrix specifically.**
- D. A. Klarner and R. L. Rivest, "A procedure for improving the upper bound for
  the number of n-ominoes," Canad. J. Math. 25 (1973). The "twig"/transfer-matrix
  construction, two-variable rational GFs, bounding Klarner's constant ≤ 2+2√2.
- I. Jensen and A. J. Guttmann, "Statistics of lattice animals (polyominoes) and
  polygons," J. Phys. A 33 (2000) — arXiv cond-mat/0007238; and I. Jensen,
  "Enumerations of lattice animals and trees," J. Stat. Phys. 102 (2001) — arXiv
  cond-mat/0007239; and I. Jensen, "Counting polyominoes: a parallel
  implementation for cluster computing," ICCS 2003, LNCS 2659. The finite-lattice
  / transfer-matrix method with *pruning* (the modern engine that pushed polyomino
  counts to n≈46 and τ≈4.0625). Our square-8 column transfer matrix is this method
  applied to king adjacency.

**Exactly-solved restricted classes (context for "slice it and it's solvable").**
- Bousquet-Mélou et al., "Exactly solved models of polyominoes and polygons" —
  arXiv 0811.4415. Convex / directed / column-convex polyominoes have
  algebraic/D-finite GFs.
- King lattice specifically: "Directed and multi-directed animals on the king's
  lattice," arXiv 1301.1365 — but that is the *directed* (restricted, solvable)
  model, not the general polyplet count. No catalogued *fixed-height polyplet* GFs
  were found, but the phenomenon is generic to the transfer-matrix method, so it is
  still not claimable as novel.

## What is partly proven / partly open (state carefully)

"The polyomino/animal GF is not nice" — be precise:
- PROVEN (anisotropic): A. Rechnitzer, "Haruspicy 2: the anisotropic generating
  function of self-avoiding polygons is not D-finite," arXiv math/0406450; and
  "Haruspicy 3: the directed bond-animal generating function is not D-finite,"
  arXiv math/0408054. (Dense singularities on the unit circle.)
- OPEN (isotropic): the ordinary (isotropic) polyomino GF being non-D-finite is
  still a conjecture; passing from anisotropic to isotropic is hard. So write
  "believed not D-finite," not "proven."

## What IS ours
- The value a(19) = 151,609,203,011,580 (A006770), computed and confirmed.
- Free(19) = 18,951,156,321,090 (A030222) and OneSided(19) = 37,902,303,297,525.
- The specific verification protocol (two independent algorithms + the cross-check
  battery). The *protocol* is engineering, not mathematics; novelty is the values.

## Framing rule for the paper
Present the transfer matrix as "the standard finite-lattice / transfer-matrix
method [Stanley §4.7; Klarner–Rivest 1973; Jensen–Guttmann]," adapted to king
adjacency. If we include any fixed-height recurrences/closed forms, frame them as
"as the transfer-matrix method guarantees, each fixed-height row is C-finite; we
exhibit the low-order ones as an internal consistency check" — with citations, and
NEVER as a discovery. The 3^(H-1) diagonal is an elementary count; state it as
such.
