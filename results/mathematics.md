# What we found, and how much of it is proved

2026-08-22, executing `docs/last-orders.md` A2.6. Written for someone who has
just arrived, in plain terms, and who wants to know what this project found
besides the numbers.

`results/confidence.md` is the companion to this file and answers the other
question: **how far can the values of A006770 be trusted, and why.** Read that
one if the sequence is what you came for. This one is about everything else.

**On trust.** Every claim below says which of three things it is: a **theorem**
(proved, and where the proof is), a **certificate** (an exact computation a
reader can re-run in integer arithmetic), or a **measurement** (a number that
came out of a computation, with the honest error). Nothing here is asserted at
a level it has not earned, and where a claim was withdrawn or corrected, the
correction is in the file next to it.

---

## 1. The problem

A *polyplet* — also called a polyking or a king animal — is a set of cells on a
square grid that hangs together when cells touching only at a corner count as
joined. Count them by number of cells, treating shapes that differ by a
translation as the same and shapes that differ by a rotation or reflection as
different, and you get OEIS
[A006770](https://oeis.org/A006770): 1, 4, 20, 110, 638, 3832, ...

The literature had reached n = 18. This project reached **n = 41**.

Nobody knows a formula. What is known is that the counts grow like `λⁿ` for
some constant λ, times a slowly varying factor, and almost all the mathematics
below is about the structure that surrounds that fact.

## 2. The one theorem a reader should take away

Sort the animals by the **height of their bounding box** as well as by size,
giving a triangle `T(n,H)`. Look along a diagonal — fix `k` and vary `n`, with
`H = n − k`. Then:

> **The diagonal law.** For every fixed `k` and every `n ≥ 2k+1`,
> `T(n, n−k) = P_k(n) · 3^(n−1−3k)`, where `P_k` is a polynomial of degree `k`.
> The onset `n ≥ 2k+1` is sharp.

This is a **theorem**, not a fit: `docs/proofs/diagonal-law.md`, with the shape,
the onset, and the integrality proved. It holds on every *row-local* lattice,
not just the king lattice — square, hex, king and beyond
(`docs/proofs/universal-diagonal-law.md`) — with the `3` replaced by the size of
the local neighbourhood.

Its consequence is what made the frontier reachable. A whole diagonal of the
triangle is `k+1` numbers. Determine those and you never compute that diagonal
again.

Sitting behind it is the **grand form** (`docs/proofs/grand-form.md`,
Lean-complete against standard axioms): each level carries **exactly two new
constants** on top of the levels below it. Two independent equations pin a
level. That is the fact everything in §4 rests on.

## 3. The growth constant, and an honest gap

    6.543  ≤  λ  ≤  9.3154          both ends machine-checkable in exact arithmetic
                λ ≈ 7.110(1)         four independent methods agree

The lower bound is a **certificate**: the height-17 strip's growth constant,
verified by an integer computation anyone can re-run
(`results/strip-mu-certificates.md`). The upper bound is a **certificate** too,
an exact rational convolution bound (`docs/proofs/polyplet-upper-bound.md`).
The middle is a **measurement**.

**The bracket is embarrassingly wide and we know why the upper half is stuck.**
The methods that produce upper bounds all encode an animal by what it looks
like within a fixed radius. We measured where the over-count lives and it is
*diffuse* and *grows with n* — the signature of a constraint no fixed radius
can see, namely that distant parts of the shape have to connect. So that whole
class of method floors strictly above λ. This is a real barrier rather than a
tuning failure, and `docs/open-problem-lambda-bracket.md` frames it as an open
problem rather than pretending otherwise.

The complementary asymmetry is the cleanest way to say what is hard here: the
strip ladder enforces connectivity **exactly** but only within a bounded height,
and converges from below; the certificate method has unbounded reach but
**relaxed** connectivity, and floors from above. Connectivity *and* unbounded
extent is what neither achieves.

**New, 2026-08-22:** λ is **not** a function of how many neighbours a cell has.
Two lattices with the same coordination number 8 — the king lattice, and one
whose neighbours are the four orthogonal steps of length 1 and 2 — have
λ = 7.11 and λ ≈ 8.97. Local cycle structure moves it 26%
(`results/lambda-atlas-probe.md`).

## 4. Counting from short cells instead of tall ones

This is the project's own idea and the one that reached n = 41.

Computing the triangle's **tall** cells is what costs. For row 40 the two
tallest cells were three-quarters of the processor time and took the disk
requirement from 69 GB to 363 GB.

The diagonal law is *false* below its onset — but not by an arbitrary amount.
The error has structure, and we computed it exactly: at depth 1 the generating
function is algebraic (an irreducible quartic), from which the rate 9, the
exponent `−1/2` and the amplitude `√6/(27√π)` all follow; the same closure holds
at depths 2, 3 and 4. All of that is **derived**, not fitted
(`paper/L8-below-onset.tex`, `results/onset-defect-law.md`).

Knowing the error exactly turns a cheap short cell into a valid equation for the
same polynomial. Since a level needs only two equations, **the tall cells stop
being necessary**. That is Undertow, and a(41) was computed without ever
sweeping the two tall poles.

**It has been checked against somebody else's answers.** Run on the square
lattice, where the counts are published, the below-onset fit equals the
classical one and reproduces the tall cell it was denied, at every level tested
(`results/undertow-square-validation.md`). That is the only check in this whole
construction that crosses out of the project, and it passes.

## 5. Arithmetic and analysis

- **The sequence is not D-finite** — it satisfies no linear ODE with polynomial
  coefficients. This is an **unconditional theorem** about the anisotropic
  generating function (`results/anisotropic-not-dfinite.md`), proved by an
  arithmetic obstruction rather than by a failed search.
- **A cubic governs the triangle mod 3.** `W³ = W² + t`
  (`results/ternary-spine.md`).
- **The exponent θ = −1**, measured to `−1.000(1)` by differential approximants
  on 40 terms. New on 2026-08-22: the *same code* on the square lattice's 70
  published terms gives `−0.9995` against the king's `−0.9997`, and recovers the
  published square growth constant to six digits — so the universality
  prediction is tested here rather than quoted, and the method is anchored to an
  outside number (`results/theta-universality.md`).
- **A denominator law**, proved: `ĉ_k = v₅(odd‼ ≤ k) + [k ≡ 1 mod 10]`.

## 6. Things we tried that did not work

This section is not decoration. A repository that only records successes is
less useful than one that records where the walls are, and several of these
took real effort.

- **Compressing the transfer matrix by rank** loses, and not for the reason the
  first analysis gave. The compressed operator is extremely sparse — 425× at
  height 8 — but its *dimension* grows faster than the thing it would replace
  and was already larger at height 4 (`results/skeletonkey-cell-sparsity.md`).
- **Tracking the complement's connectivity instead of the animal's** is worse
  at every block count, by exactly the factor `b`
  (`results/dual-connectivity-blockcount.md`).
- **A bijection to a decorated polyomino class** is *correct* and buys nothing.
  A bijection restates a counting problem rather than reducing one; the image
  carries identical information and pays the same cost
  (`results/skeletonkey-l3-3-fattening.md`). This kill generalised into a triage
  test the project now applies to every candidate.
- **The finite-size fit that would give a central charge** cannot be done from
  the strip data we have, and — corrected 2026-08-22 — the reason is that the
  correction series has not converged, not that a logarithmic term is required
  (`results/strip-fss-lambda-sensitivity.md`).
- Four algorithmic levers were measured dead against a single wall: tracking
  connectivity is intrinsically what costs, and no re-encoding of it has helped.

`docs/lastditch-ideas.md` §6–§7 and `docs/skeletonkey-reprompt.md` hold the full
inventory, each entry with the counterexample or the arithmetic that killed it.

## 7. What is open

- **The gap between 6.543 and 9.3154.** The estimate 7.110 is nailed; the
  *proof* is not close. `docs/open-problem-lambda-bracket.md`.
- **An explicit basis for the characteristic-2 rank collapse.** The collapse is
  real and large. Nobody has a basis, and without one it is not constructive.
  This is the single largest open technical question here.
- **Depths beyond 4** of the below-onset defect, which would extend §4's reach.
- **The maximum number of holes** an n-cell polyplet can have —
  0, 0, 0, 1, 1, 2, 2, 3, 4 — no closed form, and specific to this lattice,
  since four cells can enclose a hole here where the square lattice needs eight.

## 8. Where to look next

| you want | read |
|---|---|
| how far a(n) can be trusted | `results/confidence.md` |
| which cell of the triangle rests on what | `results/provenance-table.md` |
| the proofs | `docs/proofs/` |
| the papers | `paper/README.md` |
| what was tried and failed | `docs/lastditch-ideas.md`, `docs/skeletonkey-reprompt.md` |
| what this reproduces that it did not produce | `docs/external-anchors.md` |
| the running state of the work | `HANDOFF.md` |
