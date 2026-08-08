# Coinage candidates (mechanical cut)

From the 11,475 tuples in `L-novel-ngrams.md`, four mechanical filters, no judgement:

1. drop any tuple containing a function word (the, of, in, we, that, ...);
2. drop any tuple containing a finite verb or discourse word (gives, shows, rather, ...);
3. drop any tuple containing a one-letter token (`\S`/`\ref` debris);
4. drop a bigram wholly absorbed by a trigram of equal count (keep the maximal phrase);
5. keep only what is repeated (count >= 2) or contains a hyphenated compound —
   a coinage is either reused or built.

353 tuples, 3.1% of the full list. Count, papers, tuple.

```
 11 L1,L2,L3,L5,L7       king animals
  7 L1                   row-local lattice
  6 L1,L2                diagonal law
  6 L2                   digit product
  6 L7                   stack bound
  6 L1                   walk cell
  5 L6                   square lattice's
  4 L2                   activation law
  4 L1                   cluster weights
  4 L5,L7                conjectured continued fraction
  4 L5,L7                diagonal blocks
  4 L1,L2                enumerated triangle
  4 L3,L4                king adjacency
  4 L2                   last nonzero
  4 L4                   many heights
  4 L5,L7                mirror equality
  4 L5                   staircase animals
  4 L1,L3                standard axioms
  4 L5,L7                trusted digits
  4 L1                   walk row
  3 L2                   along rows
  3 L1,L4,L5             arithmetic obstruction
  3 L1                   chain identity
  3 L1,L2                cluster types
  3 L5,L7                convex king animals
  3 L1                   degree bound
  3 L5,L7                different route
  3 L3,L5                enumerated term
  3 L3                   exact rational
  3 L2                   explicit exponent
  3 L7                   four-cone class
  3 L4,L5                full column
  3 L1,L2                height triangle
  3 L2,L5                hv-convex king
  3 L1                   in-onset values
  3 L1,L3                king case
  3 L5,L7                middle blocks
  3 L5,L7                middle kernel
  3 L5,L7                monotone-height blocks
  3 L2                   nontrivial invariant
  3 L6                   onset law
  3 L1,L6                polynomial times exponential
  3 L5,L7                positive control
  3 L3                   rational vector
  3 L5,L7                sharp asymptotic
  3 L4                   signature digraph
  3 L2                   sleeve zeros
  3 L4                   slice growth
  3 L7                   subdominant exponential
  3 L5,L7                three-block factorisation
  3 L1,L2                universal spine
  3 L1                   window size
  2 L3                   actually certified
  2 L2                   adic levels
  2 L1                   adjacency changes
  2 L3                   against brute force
  2 L3                   against brute-force
  2 L7                   amplitude ratio
  2 L7                   argument available
  2 L6                   balanced box
  2 L3,L4                banked fixed-height generating
  2 L3                   bit accumulators
  2 L5,L7                bits monotone
  2 L1                   cells occupying
  2 L3                   certified ladder
  2 L3,L4                certified two-sided
  2 L3                   certified value
  2 L4                   citing articles
  2 L2                   cluster decomposition
  2 L6                   coefficient triangle
  2 L6                   coloured partition
  2 L3,L4                column-signature transfer matrix
  2 L4                   computed modulo
  2 L3                   computed vector
  2 L1                   conclusion nevertheless
  2 L5,L7                concrete route
  2 L7                   continues past
  2 L6                   convergence rule
  2 L3                   convolution system
  2 L3,L6                corner cell
  2 L2                   cubic lifts
  2 L1                   degenerate branch
  2 L4                   degree comparison
  2 L2,L6                degree exactly
  2 L2                   diagonal polynomials
  2 L6                   diagonal sticks
  2 L6                   diamond tip
  2 L5,L7                earlier step
  2 L2                   echelon position
  2 L7                   error terms
  2 L3                   exact integer
  2 L7                   extra exponential
  2 L5                   extreme blocks
  2 L3                   finite integer
  2 L4                   finitely many heights
  2 L3                   first candidate
  2 L3                   float value
  2 L3                   flooring loss
  2 L3                   forbid distant
  2 L2                   forced deficit
  2 L5,L7                four-cone floor
  2 L3                   generic twig decomposition
  2 L1,L2                height exactly
  2 L6                   height grading
  2 L4,L6                height slice
  2 L1,L6                height-diagonal law
  2 L6                   hull factorisation
  2 L3                   identical argument
  2 L2                   in-regime cell
  2 L2                   individual exponents
  2 L1,L2                integer values
  2 L5                   intermediate class
  2 L1                   interval step
  2 L4                   irreducibility certificates
  2 L5                   king animal
  2 L1,L6                king column
  2 L5,L6                king generating
  2 L5                   king series
  2 L1,L2                king-animal height triangle
  2 L5,L7                kurkov's conjectured continued
  2 L3                   larger window
  2 L2                   last nonzero entry
  2 L3                   last place
  2 L1,L4                lattice-animal height generating
  2 L4,L5                looked like
  2 L6                   maximum end
  2 L5,L6                measured against predicted
  2 L3                   median slack
  2 L6                   minimum end
  2 L3                   multi-neighbour cases
  2 L5,L7                negative controls
  2 L4                   new-root content
  2 L2                   nontrivial invariant factors
  2 L5                   null control
  2 L2                   odd spine
  2 L5,L7                operator level
  2 L1                   pair row
  2 L1,L2                pair weight
  2 L5,L7                paper claims
  2 L5,L7                paper proof
  2 L1                   parametric computation
  2 L1                   part contributes
  2 L6                   perimeter defect
  2 L6                   perimeter grading
  2 L5                   perimeter series
  2 L1                   periodic form
  2 L1                   periodic law
  2 L5,L7                phase bits
  2 L1,L6                polynomial part
  2 L3,L4                polyplet growth constant
  2 L4                   preserved degrees
  2 L1,L2                prime dividing
  2 L1                   printed triangle
  2 L5,L7                proof-relevant item
  2 L1                   rational constants
  2 L3                   rigorous knowledge
  2 L3,L6                rook lattice
  2 L1,L6                row index
  2 L5                   row widths
  2 L1                   row-local lattices
  2 L3                   rung buys
  2 L4                   shared opening
  2 L1                   single enumerable constant
  2 L4,L6                single height
  2 L1                   single walk
  2 L4                   single-cell state
  2 L2                   single-defect weight
  2 L6,L7                six-term prefix
  2 L4                   slice growth constants
  2 L2                   spine cell
  2 L2                   spine cubic
  2 L5                   square-lattice companion
  2 L6                   stabilisation onset
  2 L5,L7                staircase animal
  2 L4,L7                strictly decreases
  2 L3,L4                strip growth constants
  2 L1,L6                surplus-budgeted row transfer
  2 L1,L2                triangle cells
  2 L7                   unknown degree
  2 L3                   upper certificate
  2 L2                   valuation lemma
  2 L3                   value near
  2 L2                   vanishes modulo
  2 L3                   vector width
  2 L5,L7                vertical mirror
  2 L1                   walk rows
  2 L1                   weight table
  2 L5                   zero failures
  2 L4                   zero hits
  1 L5                   algebraic implies d-finite
  1 L1                   all-pairs weight family
  1 L3                   all-zero vector satisfies
  1 L3                   already-adjacent cells
  1 L3                   badly under-converged
  1 L3                   becoming lossy re-marks
  1 L6                   bounding-box height
  1 L6                   brute-force census cell
  1 L1                   brute-force control
  1 L6                   brute-force cross-checks
  1 L3                   bui's richer multi-type
  1 L5                   by-area generating function
  1 L5                   by-area king series
  1 L1                   cell up-down domino
  1 L3                   certified two-sided bound
  1 L7                   coefficient-level argument cannot
  1 L5                   column-convex king animals
  1 L5                   column-convex polyplets
  1 L1                   compiled-evaluation leaf
  1 L3                   compiled-evaluation surface
  1 L7                   constant-coefficient recurrence
  1 L3                   convolution-certificate method
  1 L1                   cross-family row-sum
  1 L4                   d-finiteness directly
  1 L6                   different sub-leading coefficients
  1 L3                   distant-overlap signature
  1 L3                   eight-neighbour connectivity
  1 L3                   eight-neighbour penalty
  1 L1                   enumerated in-onset values
  1 L4                   exact-coefficient evaluation
  1 L3                   far-reach split
  1 L3                   few-bit increase
  1 L3                   finite-size correction
  1 L3                   finite-state valid bound
  1 L6                   first in-regime point
  1 L4                   fixed-height generating functions
  1 L7                   four-cone class differs
  1 L5                   four-cone condition
  1 L7                   four-cone floor bites
  1 L5                   four-cone floor rewrites
  1 L7                   four-cone series
  1 L7                   four-cone-directed animals directly
  1 L5                   four-cone-directed subclass shares
  1 L3                   four-decimal form
  1 L6                   free-removal factor
  1 L6                   free-removal term
  1 L3                   frozen-successor-array kernel roughly
  1 L4                   full-text search within
  1 L3                   functional-equation trick
  1 L1                   general row-local lattice
  1 L3                   genuinely-empty cells
  1 L2                   growth-constant upper bound
  1 L4                   height-anisotropic generating function
  1 L5                   height-anisotropic king generating
  1 L1                   held-out values past
  1 L5                   hence sub-exponential
  1 L7                   hv-convex animals
  1 L5                   hv-convex king animal
  1 L5                   hv-convex king animals
  1 L5                   hv-convex ones
  1 L5                   hv-convex series
  1 L3                   in-edge-reachable boundary
  1 L1                   in-onset value
  1 L2                   in-regime cell modulo
  1 L6                   independent brute-force census
  1 L1                   independent king-only weight
  1 L3                   independently banked fixed-height
  1 L1                   integer-valuedness plus
  1 L6                   king-connected ones
  1 L1                   king-only reconstruction
  1 L1                   king-only weight table
  1 L2                   last-nonzero residue
  1 L6                   lattice's min-end ladder
  1 L2                   lattice's single-defect weight
  1 L6                   lattice-aligned special case
  1 L4                   lattice-animal family admitting
  1 L3                   local two-point fit
  1 L3                   lossy linear re-marks
  1 L4                   lowest-terms denominator
  1 L3                   measurement against brute-force
  1 L5                   merely d-finite
  1 L3                   multi-cell exact casing
  1 L4                   multi-prime subset-sum-intersection certificates
  1 L1                   multi-row cluster weights
  1 L6                   near-floor king slices
  1 L3                   newly-exposed neighbours
  1 L1                   newton-basis form implicit
  1 L6                   non-attained columns
  1 L4                   nonempty-column invariant
  1 L3                   older hash-map
  1 L1                   optional bottom-edge cluster
  1 L1                   optional top-edge cluster
  1 L3                   osegueda's quasi-submultiplicativity
  1 L3                   over-counts against brute
  1 L3                   parent-direction string
  1 L6                   partial-fraction basis
  1 L6                   per-box free-removal
  1 L6                   per-hull factor
  1 L1                   per-lattice instance
  1 L1                   per-order agreement
  1 L1                   per-period drift
  1 L2                   per-row transfer series
  1 L3                   per-term inequality
  1 L6                   per-tip series
  1 L3                   per-type tuning
  1 L6                   perimeter-preserving removal
  1 L6                   perimeter-preserving removals form
  1 L4                   positive-real point
  1 L3                   power-iteration search
  1 L5                   power-law factor
  1 L1                   power-series ring involved
  1 L6                   pre-onset holdouts
  1 L7                   prefix-sum recurrences
  1 L6                   prime-power periodicity costs
  1 L3                   production column-sweep kernel
  1 L7                   rank-one residue
  1 L6                   re-verified against
  1 L3                   re-verified last
  1 L6                   redelmeier depth-first search
  1 L1                   relevant all-pairs weight
  1 L2                   remaining in-regime cell
  1 L3                   required-cell types
  1 L3                   richer multi-type systems
  1 L1                   right-hand side vanish
  1 L3                   rook six-type bound
  1 L3                   row-sum ratios share
  1 L6                   row-transfer approach
  1 L4                   self-contained relative
  1 L3                   simple finite-state valid
  1 L6                   single-cell row
  1 L2                   single-defect species
  1 L4                   single-prime certificates
  1 L1                   six-neighbour object
  1 L6                   six-neighbour triangular
  1 L7                   six-term prefix collides
  1 L5                   sixty-digit integers
  1 L3                   sliding three-point power-law
  1 L1                   solid-pair contribution
  1 L3                   spanning-tree parent directions
  1 L3                   split-off type
  1 L6                   square lattice's min-end
  1 L5                   square-lattice analogue
  1 L6                   square-lattice artefact
  1 L6                   square-lattice column
  1 L1                   square-lattice instance
  1 L7                   sub-exponential bound
  1 L6                   successive prime-power periodicity
  1 L2                   three-line cancellation
  1 L3                   three-point power-law fit
  1 L1                   translation-invariant symmetric adjacency
  1 L2                   two-cell row
  1 L5                   two-digit guard
  1 L3                   two-sided collatz wielandt
  1 L6                   two-spare-points-per-class bar
  1 L1                   up-down domino chains
  1 L3                   useful cross-check
  1 L3                   valid over-counts against
  1 L3                   valid split over-count
  1 L3                   verified valid over-count
  1 L3                   warm-started bisection
  1 L1                   within-row offsets
  1 L2                   witt-vector tower begun
  1 L3                   would-be repair
  1 L4                   zero-counting argument
```

