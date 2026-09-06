> **NOTE: authored by Claude at jasonp's direction, 2026-08-18.** The record of
> the literature-priority passes over the nine L papers, run under the standing
> rule adopted 2026-08-17 (Ghost Ship Layer 3: a result was derived at length
> and found afterwards to be published). One section per paper: what was
> searched, what was found, what changed in the paper.

# Literature-priority passes, L1–L9

**Method.** Web search over the combinatorics and statistical-mechanics
literature, following named authors and citation chains rather than keyword
alone; full text pulled where free. This is a search, not a proof of absence,
and the sections below say which searches were run so the next pass starts
after this one rather than before it. Anything unobtainable goes to
`literature/MISSING.md`.

**Headline: three real collisions, two of them on load-bearing statements.**

| paper | verdict | action |
|---|---|---|
| L9 | **collision, at the level of the whole statement** | reframed; novelty claim withdrawn entirely |
| L6 | **collision on the structural theorem and on the defect identity** | attributed; claims narrowed to the king column |
| L5 | **antecedent found for the kernel method** | Bousquet-Mélou–Fédou cited; the earlier Richard collision stands |
| L7 | no new collision | the L5 attributions carry over |
| L2 | no collision; one method-adjacent body of work | Rowland–Yassawi cited, with why it does not apply |
| L8 | no collision found | recorded; the paper still claims nothing |
| L1, L3, L4 | no collision on the new material | recorded |

## L9 — the cut-count identity. COLLISION, and a large one.

Searched: connected-subgraph counting by transfer matrix with `q^{components}`
weights; Fortuin–Kasteleyn random-cluster versus Potts spin representation;
Blöte–Nightingale transfer matrices; Hoshen–Kopelman cluster labelling;
Jensen's polyomino algorithm and the Barequet-group complexity analyses of it.

**Finding.** The identity is an instance of the Fortuin–Kasteleyn/Potts
correspondence. The random-cluster partition function is
`Z = Σ_g v^{bonds} q^{clusters}`, and counting connected subgraphs is its
`q → 0`, `v = 1` content; the standard device for evaluating `q^{c}` without
tracking connectivity is exactly the **spin representation** — colour the
components, count colourings — which is what our model does, scan order and
all. The unsigned ancestor of the scan-order labelling is Hoshen–Kopelman
(1976). The connectivity-tracking method our engine is an alternative to is
Jensen's signature algorithm.

Read against that, the telescoping in §Proof is the FK↔spin equivalence
executed cell by cell: each component contributes `b` reuse terms and one
`(q − b)` birth term, summing to `q`. That is not a new theorem.

**What survives.** The window-bounded scan-order *form* of it: that a window of
`H+1` cells suffices under king adjacency (our Lemma 1), and that the resulting
rule is exactly what one particular engine implements. That is
implementation-grade, and the paper now says so in the abstract rather than in
a novelty section at the back.

**Action taken.** Abstract, introduction and novelty section rewritten; the
identity is presented as the specialization it is, with the FK/Potts and
Hoshen–Kopelman references in place. The paper is kept because the *proof of
the specific rule*, with its window and liveness convention, is what licenses
the second source, and nothing published states that rule.

## L6 — perimeter gradings. COLLISION on the structure, as suspected, and worse than recorded.

Searched: Asinowski–Barequet–Zheng and Barequet–Magal on fixed perimeter
defect; the polycube generalisation; minimal-perimeter animals and the
constant-isomer conjecture. **The Asinowski slides were obtained in full text
this pass** (`mat.univie.ac.at/~slc/wpapers/s79vortrag/asinowski.pdf`), where
the repository previously held only the fact of their existence.

**Findings, three of them.**

1. **The defect identity is theirs.** Their Proposition is `k = e + 2f` with
   `e` the total excess of perimeter cells and `f` the circuit rank. Our
   `k = 2c + t` — the identity L6's ledger calls proved and load-bearing, and
   which licenses the enumeration prune — is that statement with `c = f` and
   `t = e`. Independently derived here for the king lattice; published for the
   square one.
2. **The structural theorem is theirs.** "For each fixed `k`, the generating
   function of `(A(n, 2n+2−k))` is rational, and more precisely its denominator
   is a product of cyclotomic polynomials" — stated for polyominoes and, they
   note, with the same main result in `d` dimensions for polycubes. L6's
   cyclotomic-denominator framing is therefore the king analogue of a published
   theorem, not an observation of ours.
3. **Their small cases match ours.** `A(n, 2n+2) = 1` for `n ≥ 2` and
   `A(n, 2n+1) = 4(n−2)` for `n ≥ 3` are the square-lattice `k = 0, 1` rows.

**What survives.** The king column throughout; the onset formula
`k(k+1)/2 + 3`; the two-lattice universality of period, degree, onset and
leading coefficient, now tested through `k = 6`; the coefficient triangle and
its one-diagonal-deep lattice independence; and the whole minimum end. None of
those appear in the slides. The minimal-perimeter literature that does exist
(constant-isomer, square and hexagonal) is structural — inflation of
minimal-perimeter animals — and does not count by perimeter the way §min does.

**Action taken.** Attribution paragraph promoted out of §Novelty into the
statement of the defect identity and into the cyclotomic section; the ledger
now records the identity as *theirs, re-derived here for king*; the novelty
section rewritten around the three findings above.

## L5 and L7 — convex polyplets. One antecedent, and the earlier collision stands.

Searched: Bousquet-Mélou and Fédou on the convex-polyomino `q`-differential
system; the festoon approach; Klarner–Rivest and Bender constants; `q`-Bessel
zero literature; Kotesovec's constants for A067675/A067676.

**Finding.** Bousquet-Mélou and Fédou, *The generating function of convex
polyominoes: the resolution of a q-differential system*, Discrete Math. 137
(1995) 53–75, is the classical antecedent of §Kernel: the same shape of object,
solved for the square lattice by a `q`-differential system, with the
Klarner–Rivest function as the denominator whose smallest positive zero gives
the growth constant. Our kernel `K` is the king analogue, and the control arm
of our own pipeline reproduces their constants — which is the anchor, and is
also the reason the antecedent must be cited rather than merely noted.

No separate collision was found for the certified-interval treatment of the
constants, for the negative zero at `q = −0.795`, or for the identification of
the measured Prony spectrum with `1/zeros(K)`.

The area-moment collision found on 2026-08-17 (Richard, arXiv:0704.0716;
Enting–Guttmann 1989) is unchanged and remains cited in three places.

**Action taken.** Bousquet-Mélou–Fédou cited in §Kernel and in related work.

## L2 — the mod-3 arithmetic. No collision; one adjacent method.

Searched: congruences modulo powers of 3 for combinatorial sequences;
Krattenthaler–Müller's method for mod-`3^k` behaviour of recursive sequences;
Rowland–Yassawi automatic congruences for diagonals of rational functions;
Smith normal form of combinatorial triangles; base-3 digit-product formulas.

**Finding.** Rowland–Yassawi (J. Théor. Nombres Bordeaux 27 (2015) 245–288) is
the closest machinery: for a sequence whose generating function is the diagonal
of a rational power series, they compute a finite automaton modulo `p^α`. It
does not apply here, and the reason is a result of ours — companion paper L4
proves the height generating function is not D-finite, so it is not such a
diagonal. That is worth a sentence in L2 precisely because a reader who knows
that literature will ask.

No collision on the spine cubic, the digit product, or the all-3-powers Smith
normal form.

**Action taken.** A related-work paragraph in L2 naming both and saying why
neither applies.

## L8 — below the onset. No collision found.

Searched: corrections and error terms to fixed-height / bounding-box animal
formulas; asymptotics of defects below a formula's threshold; algebraic
generating functions for leading coefficients of such families; polyomino
enumeration by bounding box.

Nothing close. That is a weak negative — the object is defined relative to our
own diagonal law, so a collision would have to be with a paper that had that
law first, and companion paper L1's sweeps cover that. The paper continues to
claim nothing.

## L1, L3, L4 — the new material only.

Their N1–N6 sweeps stand for the material they covered. This pass looked only
at what postdates those sweeps.

- **L3's BFS-frame encoding** (the repaired proof of the `5^5/4^4` bound). No
  collision found on the king constant. Adjacent and worth watching: the
  Barequet-group improved upper bounds for polyominoes and polycubes, a 2025
  convolutional approach to bounding polyomino counts, and a 2025 short proof
  of a polyiamond bound. All are square-lattice or polyiamond and none states a
  king number.
- **L1** — the below-onset link is L8's material and is covered above.
- **L4** — unchanged since its sweep; nothing re-searched.

## What the next pass should do differently

Two of the three collisions were found by pulling **full text of a source we
already knew about** rather than by a new search. The slides had been sitting in
`literature/MISSING.md` as unobtainable; they were free. Before the next round of
keyword searching, re-try every entry in that file.

## ABZ full text — obtained the same day, and it answers the question the slides left open

The paywalled Asinowski–Barequet–Zheng paper the L6 pass wanted is free: the
ANALCO 2018 polycube companion, "Polycubes with small perimeter defect,"
Proc. ANALCO 2018, 93–100. Filed in `literature/`. It carries the proofs the slides
only stated.

**What the proof actually is.** For a polycube `P` in `Z^d` under face
connectivity: `p = 6n − e − 2|E|` counting the two ways perimeter is lost,
giving `p <= 4n+2` and `k = e + 2r` with `r` the circuit rank (their
Proposition 2.1 — our `k = 2c + t`). Rationality (their Theorem 3.1) is proved
by *cut shrinking*: a `j`-orthogonal cut is a maximal run of grid slices whose
projection is a set of pairwise non-adjacent cells with no common neighbours;
deleting a cut's slices and regluing preserves the defect, cuts are pairwise
independent, so every polycube shrinks to a unique reduced one. A pattern class
is a fibre of that map, its generating function is `x^b` times a product of
`1/(1−x^s)` (s = number of ports of a cut), hence cyclotomic. Finiteness of the
class count comes from bounding three kinds of special cell — excess cells,
L-cells, and degree-1 cells — each against `k = e + 2r`, with the degree-1
bound `|V_1| <= 4|V_{>=3}| + 2` coming from the handshake inequality at maximum
degree 6.

**Verdict for L6: the king column is a separate derivation, not a corollary.**
Every mechanical step above is stated in face-adjacency terms — the perimeter
accounting `6n − e − 2|E|`, the L-cell definition ("occupied neighbours that
are not opposite"), the non-adjacency condition defining a cut, and the
handshake bound at max degree 6. None of it is stated lattice-generically, and
king adjacency breaks the cut condition in particular. The *shape* of the
argument plainly transports; the theorem does not. So L6's king results are not
inside their framework, while our square-lattice statements remain their
theorem re-derived.

**They conjecture what we measured.** Their §4 conjectures that for any `d` and
fixed `k` the highest-degree factor of the characteristic polynomial is
`(x−1)^{k+1}`, so that the count is asymptotically `γ n^k`. Our table in
`results/perimeter.md` has exactly `Φ₁^{k+1}` and degree `k`
for every `k <= 6` on **both** lattices. That reframes the degree row: for the
square lattice it is evidence for a published conjecture rather than an
observation of ours, and for king it is evidence for the same conjecture on a
lattice their framework does not reach. L6 should say so.

**Also settled by the same paper:** their `B(n,d,0) = d` and
`B(n,d,1) = d(d−1)(n−2)/2`, and the observation that a pattern of defect `k`
spans at most `k+1` dimensions.

**Not done here, and open for his call:** the L6 edits implied by the two
paragraphs above — citing the ANALCO paper rather than the slides, and
restating the degree row as a conjecture-confirmation.
