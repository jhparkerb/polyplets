# The hole-fill / interior-cell identity (structural, not a compute lever)

2026-07-07. Ties together three things from one evening's session: the
hole-fill bijection, the perimeter/interior-cell bracket, and the
cut-vertex/block-cut-tree measurement from earlier (see this session's
transcript; no prior file for the block-cut-tree numbers specifically).

## The bijection (exact, provable — not measured)

For an n-cell polyplet b with exactly one hole of area 1 at position x:
T = b ∪ {x} is, by construction, an (n+1)-cell hole-free polyplet, and
b = T \ {x} exactly. So b ↔ (T, x) is an exact bijection between
{n-cell, 1-hole, area-1 polyplets} and {(T, x) : T hole-free size n+1,
x an interior cell of T whose removal keeps T\{x} connected}. No
existence question here — it's definitional once "fill the hole" is
spelled out. What is NOT one-to-one is the forgetful map (T,x) -> T:
a single T can have several valid x (multiple interior, non-cut-vertex
cells), so T -> b is many-valued, not injective.

## The perimeter/interior-cell bracket (exact, provable)

Let d(c) = 4 - rook-degree(c) (exposed edges), P = sum_c d(c) the
edge-perimeter, I = #{c : d(c)=0} the interior-cell count. Since every
non-interior cell has d(c) in {1,2,3,4}:

    n - P <= I <= n - P/4

Checked against 2000 real n=12 samples (`build/tma_sample`): holds with
zero violations (must, it's exact arithmetic from the definitions), and
empirically the UPPER bound is tight for real (mostly spindly) large
polyplets (mean slack 2.73 cells) while the lower bound is nearly
useless for this population (mean slack 25 cells) -- consistent with
large polyplets having very few true interior cells.

## The combined identity

An interior cell only yields a valid b when removed if it is ALSO not a
cut vertex (removing it must keep T\{x} connected). So:

    1-hole-area-1(n) = sum over T (hole-free, size n+1) of
                       #{interior cells of T that are not cut vertices}

Exact, not a bound. Connects: perimeter (bounds candidate count from
above), block-cut-tree structure (which candidates actually survive).

## Why this is structure, not a lever (the honest part)

Directionality only runs one way: filling a hole (small-with-hole ->
big-hole-free) is a clean, always-defined map; the reverse (remove an
interior region) requires ALREADY knowing T's interior-cell set and
cut-vertex set, which is exactly the kind of per-shape structural
information the production engines don't track and that the session's
earlier probe flagged as hard to make cheap (cut-vertex status depends
on connectivity resolved arbitrarily later in a column sweep, not
locally at the frontier). So this identity always expresses a SMALLER
quantity (n-cell, k missing cells) in terms of an ALREADY-COMPUTED
BIGGER one (hole-free, size n+k) -- never the reverse. Generalizing to
multi-cell holes (k separate area-1 holes, or one connected area-k
hole, all mapping into the same hole-free(n+k) target) enriches the
combinatorics (a whole partition-indexed family of hole-shape counts,
all summing against interior-REGION removals of total area k) but does
not change this directionality. There is no version of this identity
that gets you from smaller, cheaper data to a bigger, not-yet-computed
count -- which is the direction that would actually matter for pushing
the frontier further.

Real, correct, worth keeping -- and explicitly not a compute lever.
