# Beyond polyplets — what this repo's machinery can be pointed at

2026-08-04. Written at jasonp's request: not "what else is there to ask about
polyplets" (that is `unexplored-avenues.md`) but **what non-polyplet questions
the assets in this repo can be brought to bear on**. An inventory of
retargetable machinery, ranked by how far each item already is from the king
lattice.

> ## READ THIS FIRST — status of everything below
>
> **This is an inventory, not a set of results.**
>
> - **Novelty is UNCHECKED on every item.** Several of these targets are
>   certainly worked over by other people; nothing here may be described as
>   new to anyone outside this file until it has been grepped against the
>   literature and OEIS.
> - **"Retargetable" is a reading of the code, not a port.** Nothing below has
>   been run on a non-king problem except where explicitly marked ALREADY RUN.
> - **No competitiveness is claimed.** That the repo owns a certified-bracket
>   pipeline does not mean its bracket would beat the specialists' on their
>   own lattice. Where I can name the incumbent I have.
> - **Costs are unestimated.** No compute is requested or authorised.
> - The project closes at a(40); everything here is downstream of that.
>
> Standing filter (MEMORY.md, claim-pruning) does not apply cleanly here —
> none of these shorten a sentence in the polyplets paper, by construction.
> They are exports, not internal work. That is the honest framing: every item
> below is new-paper-sized or nothing.

---

# A. Already lattice-generic — needs only a new instance

## A1. The universal diagonal law, on lattices not yet instanced

`docs/proofs/universal-diagonal-law.md` is stated for the whole **row-local**
class: translation-invariant symmetric adjacency inside `|dy| <= 1`, within-row
adjacency containing `|dx| = 1`, up-offset set `D` finite and nonempty, drift
count `b = |D|`. The theorem is `T(H+k, H) = q_k(H) * b^H` for all `H >= k+1`.

**ALREADY RUN on three lattices:** square `b=1`
(`experiments/universal_law_check.py`), hex/brick `b=2`
(`experiments/hex_gas.py`, `results/hex-diagonal-law.md`), king `b=3`
(`experiments/diagonal_law_proof_check.py`). Lean carries the abstraction plus
all three instances: `polyplets/Polyplets/Universal/{AbstractShape,Square,Hex,
King}.lean`.

**Not yet instanced:** triangular lattice; the spread-8 neighbourhood
`{(±1,0),(0,±1),(±2,0),(0,±2)}`; any `|dx| <= 2` within-row lattice; directed
and anisotropic variants.

The most obvious untaken target is **polyominoes themselves**: the square case
is proved and checked, but the repo has never derived the A001168 near-diagonal
closed forms `P_k` the way it did for king. Same peeling recursion, same
partial-fraction argument, and the modular spine transfers too — the valuation
lemma is recorded as lattice-independent, and the same cubic `W^3 = W^2 + u`
appeared mod 3 for king and mod 2 for hex. Triangular would give a third prime.

## A2. The symmetry-companion machine, for any polyform family

`cpp/sym/symtm.cpp` computes per-element `Fix(g)` by transfer matrix;
`scripts/derive_related.py` is the Burnside combiner; `results/sym_counts.txt`
is the banked format. The pipeline takes a lattice family with a dihedral
action and returns free / one-sided / bilateral / asymmetric companions. None of
that is king-specific. The polyform zoo (polyhexes, polyiamonds, polyabolos,
and the neighbourhood-variant families) is the obvious import list.

See also `unexplored-avenues.md` idea 1 for the orbit-size distribution — the
subgroup-invariant counts `I(D4)`, `I(C4)`, `I(D2ax)`, `I(D2diag)` that the
`Fix(g)` bank does *not* contain. That gap is the same on every lattice.

---

# B. Combinatorics-generic — nothing to do with animals

## B1. Certified spectral-radius bounds in exact integer arithmetic

`cpp/strip_mu_cert.cpp` (+ `results/strip-mu-certificates.md`,
`make gate-strip-cert`) checks a Collatz-Wielandt certificate: a nonnegative
nonzero integer vector `v` and rational `x` with `(M(x) v)_i >= v_i`
componentwise, verified in integers. The argument needs neither positivity of
`v` nor irreducibility of `M`. **Nothing in that is polyplet-shaped** — the
input is a nonnegative matrix with entries monotone in a parameter.

The question it answers generically: *certified lower bound on the growth
rate / entropy of a transfer-matrix-defined class, as an artifact a reader can
re-check rather than a power iteration they must trust.* Candidate importers:

- **constrained-coding capacity** — 2D run-length-limited codes, the hard-square
  entropy constant and its relatives;
- **subshifts of finite type** — entropy bounds with a finite receipt;
- growth rates of regular/context-free languages and of automatic sequences.

The complementary upper half is `experiments/certificate_bound.py`: the
Bui-style monotone-iteration bound with exact rational final certificate.
**ALREADY RUN on a non-king lattice** — its validation target is the published
rook/polyomino six-type system reproducing `lambda_2 <= 4.63` with Bui's own
certificate. The Lean side is `polyplets/Polyplets/Upper/` (`Certificate.lean`,
`BuiData*`, `BuiRD*`).

Taken together the two halves are a reusable recipe for a **machine-checkable
two-sided bracket on a growth constant**. `unexplored-avenues.md` idea 4 already
notes that certified two-sided brackets appear not to exist for more than one or
two lattices; the same scarcity holds outside animals.

## B2. Mechanized non-D-finiteness from computed strips

`experiments/anisotropic_dfinite.py` + `results/anisotropic-not-dfinite.md`
implement a Rechnitzer-style haruspicy theorem as a **finite certificate**:
new-root content `psi_H = Q_H / gcd(Q_H, Q_1...Q_{H-1})`, certified squarefree,
in lowest terms, coprime to every earlier denominator, all mod `p = 2^61 - 1`
(gcd = 1 mod p with preserved degrees is rigorous over Q). The output is an
explicit exclusion table over (order `r`, x-degree `D`), plus the conditional
full statement if `deg psi_H -> infinity`.

**The input is only "a sequence of rational GFs indexed by a width parameter."**
Anything with computable strip generating functions qualifies:

- self-avoiding walks and polygons by width;
- directed animals, column-convex and staircase-convex families;
- bond/site percolation strip GFs;
- dimer and tiling models with a defect line;
- Motzkin/heap models with a bounded-height parameter.

This is the item I would guess has the widest reach outside this project: most
such families have a folklore "not expected to be D-finite" sentence and no
certificate behind it.

## B3. `Northcott.lean` — a standalone number-theory file

`polyplets/Polyplets/Northcott.lean` says so itself: *"Nothing here mentions
animals; the file is the project's reusable number-theory shim."* It proves
that a house bound `B` forces `M(minpoly) <= (max 1 B)^deg`, hence finiteness of
algebraic integers at bounded degree and bounded house, hence the downstream
form — pairwise distinct algebraic integers with a uniform house bound have
unbounded degree. Mathlib-adjacent, independent of everything else here.

---

# C. Infrastructure, retargetable to any frontier computation

## C1. The kink-carry engine behind the `libenum` seam

`docs/engine-design.md` states the load-bearing property outright: the column
step is a map + reduce-by-key whose reduce (`addCounts`) is commutative and
associative, so the result is independent of how states are sharded, ordered or
batched — and the MT engine is bit-identical to serial. The Go orchestrator
(work-stealing scheduler, budget governor, wall-cadence checkpoint, spill/merge
store, telemetry, manifest) sits above a seam and knows nothing about kings.

King-specific: the transition kernel (`stepColumnSquare8`, `forEachViableMask`,
the closure and prune tests). Generic, built and validated: connectivity-tracking
frontier signatures with canonicalization, external sort-merge over spilled
sorted runs, CRT mod-p counting with the u32/31-bit interleave
(`results/crt-counter-shaping.md`), checkpoint/resume, cross-architecture
recount verification (`verify/`).

Retargets, all needing a new kernel and nothing else structural: SAW/SAP series
extension, percolation cluster series, Potts/Ising strip partition-function
series, dimer and tiling counts, spanning forests on wide strips.

## C2. The measured infrastructure findings

`results/a34-utilization-postmortem.md`, `results/utilization-fix-and-ceiling.md`,
`results/scheduling.md` (LPT rejected, work-stealing adopted),
`results/perf-outcomes.md`, `docs/utilization-bottleneck-log.md`, the tmpfs
crossover (4.6x to a34, OOM at a35), `results/pgo-no-go` (branch-mispredict
bound), `results/crt-counter-shaping.md`.

These answer a question no combinatorics paper asks: *how do you saturate a
small heterogeneous non-cloud fleet on a disk-bound out-of-core enumeration?*
`results/cloud-investigation-2026-07-07.md` adds the negative half — utilization
at 19.8%, not core count, was the lever. Audience: anyone attempting a record
enumeration on home hardware.

## C3. Verification methodology as the deliverable

The confidence-tier system (T1 / T2 / T2- / T3, with the tier attached to each
number and never silently), red-first fail-closed gates (`make gates`,
`docs/engineering-standards.md`), per-term `results/ns_a*/PROVENANCE.md`
ledgers, `obs.py` + `docs/observability.md`, `docs/job-checklist.md`,
`papers/MISSING.md` practice, `paper/verify_claims.py` as a self-contained
re-checker of the report's numerics.

**ALREADY EXPORTED once:** `docs/observability.md` is maintained identically in
the `../oeis` sibling repo, which adopted it wholesale.

The general question: *how should a computational-mathematics claim that cannot
be practically reproduced by a reader be graded, provenance-stamped and
published?* Applicable to record primes, Busy Beaver values, endgame tablebases,
any OEIS extension of a hard sequence.

A separable sub-answer: the **pinned-computed-table-into-Lean** pattern —
fail-closed generated pin data (`scripts/gen_pin.py`, `scripts/gen_grand_pin.py`,
`scripts/extract_pin_data.py`), `#guard_msgs`-enforced axiom footprints,
`ComputeBridge.lean` closing the definitional gap with in-tree `native_decide`
theorems rather than out-of-file prose. That is a reusable answer to "how do you
keep a computer-assisted proof auditable when part of it is a large computed
table."

---

# D. Adjacent fields the existing data already touches

## D1. Statistical physics

Two threads carried over from `unexplored-avenues.md` (ideas 2 and 6), listed
here because their *audience* is not combinatorial:

- **Percolation.** King is the matching lattice of Z^2 for site percolation
  (`p_c` values sum to 1). Perimeter-refined counts plus the Sykes-Essam
  identity yield `p_c` directly, testable against the known 0.40725. The
  convention caveat in idea 2 governs.
- **Universality.** Finite-size scaling of the certified `mu_H` ladder against
  the Yang-Lee / Parisi-Sourlas prediction, and the prediction that king and
  square sit in the same class. Data already on disk; the certificates bracket
  rather than pin, so the fit must propagate brackets.

## D2. The repo as primary source on AI-assisted research

A timestamped, near-complete record of amateur mathematics conducted with an LLM
collaborator: three standing audits (`AUDIT-2026-06-28`, `-07-13`, `-07-30`),
`docs/lessons-learned.md`, `docs/reviews/`, the closed-door notes, the
hostile-witness protocol (`docs/lean-hostile-witness.md`), the viva gate, the
tier discipline, and the README's authorship note on the division of labor.
Includes the failures: rejected schedulers, dead algorithmic levers, a resume
bug found by a red test, a Lean bridge that was prose until an audit caught it.

Requires no compute. Publishing any of it is jasonp's call and involves the
usual caveat that the local-only viva docs never leave the machine.

---

# Ranked, cheapest first

1. **B2** — retarget the `psi_H` non-D-finiteness certificate at a published
   strip-GF family (SAW by width is the obvious first). Pure scripting over
   someone else's data; no enumeration needed.
2. **B1** — certify a hard-square-type entropy bound with the existing
   Collatz-Wielandt checker. The checker is built and gated; the work is
   building `M(x)` for the new constraint.
3. **A1** — square-lattice `P_k` diagonals from the universal law. Brute force
   to n ~ 14 plus the existing fit machinery; the theorem is already proved and
   the square case already machine-checked, so this is derivation, not research.
4. **C3 / D2** — write-ups, no compute, but new-paper-sized and gated on the
   project actually closing.
5. **C1** — a real port. Only worth it with a specific target series and someone
   who wants it.

Everything else here is either a research programme (B1 beyond a first
instance, D1) or contingent on someone else's interest (A2, B3, C2).

---

# Provenance

Written 2026-08-04 in one session from direct inspection of: `README.md`,
`docs/proofs/universal-diagonal-law.md`, `docs/engine-design.md`,
`docs/observability.md`, `obs.py`, `results/anisotropic-not-dfinite.md`,
`results/hex-diagonal-law.md`, `results/strip-growth-lambda-bounds.md`,
`results/strip-mu-certificates.md`, `experiments/universal_law_check.py`,
`experiments/certificate_bound.py`, `polyplets/Polyplets/Northcott.lean`,
`polyplets/PROOF-STATUS.md`, and directory listings of `cpp/`, `scripts/`,
`experiments/`, `polyplets/Polyplets/`, `verify/`.

No code was run and no measurement was taken for this file. The ALREADY RUN
markers cite runs banked by earlier work, not runs made for this note.

Companion: `unexplored-avenues.md` (same disclaimer regime), which covers the
directions that stay inside the polyplet problem.
