# When is a polyplet sub-population countable (not just enumerable)?

Date: 2026-07-10. Companion to [[algorithmic-levers-dead-connectivity-wall]] and
results/directed-king-animals.md. The question: given an attribute (invariant)
of polyplets, does conditioning on it give a sub-population we can *count*
(closed form / rational-or-algebraic GF / polynomial cost) rather than
*enumerate* fully?

## The criterion

A sub-population is countable-not-enumerable **iff conditioning on the attribute
makes the connectivity constraint one-dimensional.** Connectivity is the wall
(same wall as the finite-lattice / MPS / holonomic negatives); an attribute
buys a counting shortcut only if it collapses that 2D constraint to a 1D
layer/heap recursion. This is a severe filter.

## What passes (and it's exactly the classical exactly-solved subclasses)

- **Directedness** — forward cone ⇒ heaps of pieces ⇒ algebraic GF. Done
  (Bacher; results/directed-king-animals.md). Also multi-directed.
- **Convexity family** — row-/column-/HV-convex, stacks, staircases, bargraphs.
  Every row and column a contiguous run ⇒ the shape is a 1D profile evolution ⇒
  algebraic/rational GFs.
- **Bounded height/width** — fixed `H` ⇒ rational GF in `n` (our `T(n,H)` atoms,
  `results/fixed_height_gfs.txt`). Closed form, but cost exponential in `H`.

## What does NOT pass (stays enumeration-hard)

Holes, edge-connected-component count, perimeter, symmetry class, coloring/parity,
edge/corner-contact counts. None change the dimensionality of connectivity;
conditioning on them leaves the full 2D-hard problem restricted to a subset.
(We still *stratify* by these via enumeration — `T(n,H)`, A0/A1 holes,
companions — but that is enumeration, not a counting shortcut.)

## Why none of them help count a(n)

Even the solvable subclasses are strict subsets that do **not** compose back to
the total: directed ↛ undirected, convex ↛ all. Same non-reduction as the
directed/undirected inequality. So every countable sub-population is a
side-quest — a standalone result, a rigorous bound, or a validation anchor —
never a lever on `a(n)`.

## Parked lead (2026-07-10) — separating invariants

Distinct from *covering* (partitioning) attributes: is there a small set of
attributes whose joint value **pins a polyplet uniquely** (no two distinct shapes
collide)? A "separating"/complete-invariant set, not just a partition. None of the
standard attributes come close alone. Flagged interesting by jasonp, deferred.

## Open nugget

**HV-convex polyplets.** Classical convex *polyominoes* are algebraic
(Delest–Viennot by perimeter, Bousquet–Mélou by area). The king version is
strictly larger — an HV-convex set can be king-connected by a pure diagonal join
without being edge-connected, e.g. `{(1,1),(2,2)}` — so it is a new family,
plausibly still algebraic, and possibly unpublished (as Bacher's directed-king
count was until 2013). Worth a literature check + a small GF derivation if we
want another standalone king result / bound. Not a lever on `a(n)`.
