# r4-floors — adversarial audit of the three floors

Standing question: is each floor a theorem, and does it say what it is used to
say? Verdicts and the failing step, per floor. Filed incrementally.

## Floor 2 (information, L3-1) — VERDICT: THEOREM (narrow) but OVER-APPLIED

### What is stated

`results/triangle-r3-synthesis.md:201`:

> **Information floor** (L3-1). Any straight-cut method in any vocabulary must
> transmit at least Motzkin(H/2+1) quantities across the cut — the banked SVD
> ranks *are* Motzkin numbers.

and `:215-222`, "The cut is an information floor … That single fact explains why
three lanes hit the same wall and **prunes the remaining search space to no-cut
methods and cancellation**."

### Finding 2A — the floor's own number is ~2.6e4 times BELOW the incumbent's
### cost, so it excludes nothing in the affordable region

Desk arithmetic on Motzkin numbers (verified this session):

| quantity | H=21 value |
|---|---|
| L3-1 floor, M(H/2+1) = M(11)..M(12) | 5,798 .. 15,511 |
| incumbent column states, M(22)−1 | 400,763,222 |
| ratio | **25,837x** |

A cut method that transmitted 15,511 quantities per cut at H=21 would be an
enormous win, not a wall. **L3-1 therefore cannot, on its own, close any cut
method.** The gap between the floor and the incumbent's cost is exactly the room
a better cut vocabulary would live in, and the floor says nothing about it.

This is not a hypothetical gap. `results/triangle-r3-involution.md:320-330`
already exhibits an object inside it: the char-2 compressed dimension at H=21 is
~0.9–1.3e6, which the involution lane itself scores as "~10² above [the L3-1
floor], no violation" and ~10³ below B1's state space. A cut-crossing
representation 400x smaller than the incumbent, fully compliant with the
information floor, is on disk in this repo. The synthesis's pruning claim
("prunes the remaining search space to no-cut methods and cancellation") does not
follow from L3-1 and is contradicted by a sibling lane's own number.

### Finding 2B — the measured object is not the object the floor names

The banked ranks come from `results/boundary-push-tensornetwork.md`: "We MEASURED
the rank by dumping the real frontier count-vector and taking the SVD across the
balanced central cut" — i.e. the **Schmidt rank of one frontier count-vector**,
at one sweep position and one n, reshaped across a cut of the H *frontier sites*.
That is exactly the minimal bond dimension for an MPS factorization of that
vector: a genuine theorem, about MPS compression of the incumbent's own frontier.

It is not the rank of the counting problem's left-cells x right-cells matrix
across a spatial cut of the lattice. The bipartition differs (top half of a
frontier vs left half of a lattice), the object differs (a data vector at fixed
n vs the bilinear form of the whole count), and the quantifier "any method in any
vocabulary" is licensed only for the latter. As stated, L3-1 is a bound on
methods that (i) sweep in the incumbent's direction, (ii) form the incumbent's
frontier count-vector, and (iii) factorize it linearly along the frontier. It is
silent on methods that never form that vector — which is the whole no-cut class
it is being used to *define the complement of*.

### Finding 2C — the Motzkin identification is 3 confirming points and one
### unresolved miss, but it is not numerology

M(H/2+1) is a structural **upper** bound on that rank: the rank cannot exceed the
number of distinct half-frontier signatures, and a height-H/2 half-frontier has
M(H/2+1)−1 nonempty states plus empty, by the banked theorem
(`git show second-source:results/king-column-motzkin.md`, Lemmas 1–2, proved and
machine-verified three ways). So the identification has a reason, and the
load-bearing content of the *floor* direction is the measured **attainment** of
that upper bound (linear independence of the half-states) at H=8/10/12 only.
H=14 measured 298 against M(8)=323. `results/triangle-r3-l3-contour.md:250-252`
concedes: "I did not re-dump at a peak column to confirm it closes to 323."
Attainment is MEASURED-PATTERN at three points, NOT ESTABLISHED in general and
NOT ESTABLISHED at the one H where it was tested and missed.

## Floor 1 (state, L1-6) — VERDICT: OVER-APPLIED, and FALSE as literally stated

### What is stated

`results/triangle-r3-synthesis.md:198`:

> **State floor** (L1-6). Any frontier vocabulary pays at least the cell
> frontier's state count; coarser objects do not help, because piece identity
> refines rather than abstracts.

Queue row L1-6 (`results/triangle-r3-queue.md:60`) goes further: "any strip-cut
vocabulary pays >= Motzkin; the search space for a smaller state space is exactly
the no-cut / implicit methods".

### Finding 1A — refuted by a sibling lane's measurement, same round

"Any frontier vocabulary" cannot mean *any*, because linear realizations of the
same column functional are measured, in this repo, at strictly fewer dimensions
than the cell frontier's state count. `results/triangle-r3-involution.md:284-300`,
observability closure = exact Hankel rank:

| H | cell states M(H+1)−1 | rank GF(2) | A-S1 rank mod p=2^31−1 |
|---|---|---|---|
| 7 | 322 | 58 | 88 |
| 8 | 834 | 112 | 204 |
| 9 | 2187 | 229 | 501 |

Both columns are below the cell frontier at every measured H, and the char-2
column diverges downward (0.44·2^H against Motzkin's ~3^H): ~1e6 against
4.0e8 at H=21, a factor ~400. The involution lane states the governing principle
itself (`:277-281`): "The minimal dimension of ANY field-linear realization of
the strip functional — partition basis, coincidence basis, spin basis, anything —
is the Hankel rank of the functional itself."

So the honest scope of floor 1 is **combinatorial vocabularies whose states are
objects placed on the frontier**, not "any frontier vocabulary". Linear /
weighted-automaton realizations are exactly a frontier vocabulary and they pay
less. The standing caveat that rescues the *practical* conclusion is a different
one, and it is the one that should be quoted instead: the low-rank basis is an
existence statement with no explicit basis (`triangle-r3-synthesis.md:225-228`,
"a rank is an existence statement and the explicit basis — which CKN have for
matchings — does not exist here").

### Finding 1B — even restricted to combinatorial vocabularies, it is one
### instance generalized

What L1 measured (`results/triangle-r3-l1-corner-gluing.md:73-102`) is one
coarsening: rook-piece corner-gluing assembly, cell vs piece closure at H=2..9,
piece/cell rising 1.00 -> 2.72. Validated (banked T(n,H) reproduced H<=6, RED
control), and the cell column independently reproduces M(H+1)−1. The measurement
is sound and I am not disputing it.

The *reason* given (`:103-106`) is also specific to that coarsening: "the rook
partition refines the king partition … piece identity is extra information on top
of the king labels". That argues about rook pieces. It is not an argument about
an arbitrary quotient of the frontier alphabet.

What a helping coarsening would have to be: a partition of the reachable state
set that is a **congruence** for the column transfer map and for the final
readout — i.e. merging two states that are Nerode-indistinguishable. The general
claim is therefore equivalent to: *the M(H+1)−1 reachable states are pairwise
Nerode-distinguishable*, so the incumbent's automaton is state-minimal. That
would be a theorem covering every deterministic column-sweep vocabulary at once,
and it is the right form of floor 1.

**Nobody has proved it, and nobody appears to have asked.** Grep for
`Nerode|distinguishab|minimal automaton|state-minimal` over `results/` and
`docs/` returns no hit in a state-count context. NOT ESTABLISHED. This is the
cheapest missing brick in the whole floor structure: pairwise distinguishability
at small H is a desk computation on the existing closure code, and a proof at
general H likely follows the same rails-and-spurs witness that
`king-column-motzkin.md` Lemma 2 already builds.
