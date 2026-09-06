# The publication record

This file records how the project's results were prepared for release: the
release strategy, the warrant given to each result in each paper, the
standards a reviewer and a skeptical reader are held to, the audits of the
main report and of the machine-written papers, the literature searches and
their verdicts, the removals made before release, one corrected literature
fact, and a plain summary of what is proved. State as of 2026-09-06: the
repository is public; the report is `paper/technical-report.tex`,
approved; the OEIS is not to be contacted, and every OEIS item below is
staged only. Grades follow `results/confidence.md`: a theorem is proved and
its proof is named; a certificate is an exact computation a reader can re-run
in integer or rational arithmetic; a measurement is a number that came out of
a program, with its control and its limits.

## What is in here, and what kind of thing each section is

Five of these are **decisions** and bind: the release and its shape, warrant
tiers, the skeptical-reader standard, removals before publication, and the
OEIS policy. The rest are **dated record**: audits, novelty searches and
findings, true as of the date each carries.

| section | decision or record |
|---|---|
| The release and its shape; warrant tiers; the skeptical-reader standard; removals before publication; OEIS policy and staging | decisions |
| Reviewer expertise; defending a(40); the acceptance queue; the two audits; novelty searches N1-N6; the square-lattice record; formalization tooling; what was found and how much is proved | record, dated |

## The release and its shape

**The venue** (jasonp, 2026-08-18) is a public git repository with its code,
results and PDFs, plus staged OEIS material. There is no referee. A visitor
clones, runs one command, and decides within minutes whether the numbers are
real, so the repository is the publication and the manuscripts are
attachments.

**Authorship.** jasonp's constraint of 2026-08-06:

> I can't let you write papers for me where the math is something I can
> understand and vet. I'm happy (ish) to publish LLM-authored results *if*
> they're beyond my understanding *and* we're *sure* they're correct *and*
> they're clearly marked as such.

The first reading, that he writes all prose and any result past his vetting
ships as a statement plus a citation to its Lean development or certificate,
was replaced on 2026-08-07 by the authorship split of
`docs/publication-split.md`: P papers are his prose throughout, L papers are
machine-written end to end, and page 1 of every paper says which. The warrant
tiers below survive from the first reading as the vocabulary of the provenance
tables. Under either reading the machine does the novelty searches, the Lean
development, the regeneration of every number, LaTeX scaffolding, tables,
figures, provenance tables and reproduction recipes, and checks drafts against
the repository; it authors no P prose and supplies no endorsement.

**The four tracks of 2026-08-18.** The front door (a clean-clone run, one
per-entry provenance table, a fail-closed check of the OEIS files, a README
opening with the claim and the reproduce command) is done; the acceptance
queue below holds the receipts. The coloring program at height 18 closed a(n)
under a second connectivity rule for n ≤ 35; height 19 under the same design
was priced and not run, and was reached by the Nmax-41 run of 2026-08-20/21
(`results/second-sources.md`). The L papers, nine by 2026-08-18, contracted to
six on 2026-08-23 (`docs/l-papers-record.md`; `paper/README.md` is the
current list), every ledger reading "human verification: none" under a draft
banner. The report was written after the provenance table existed.

**The three-paper plan of 2026-08-06**, whose numbering and OEIS order
`docs/publication-split.md` superseded, is what the provenance tables are
keyed to: Paper 1, fixed polyplets to n = 40 (a(40) and the triangle T(n,H),
the engine, the validation architecture, component stratification, the
maximum hole area as a cited corollary, the growth estimate); Paper 2, the
structure of the height triangle (the hand-derived diagonals, the defect gas,
the universal diagonal formula, the mod-3 arithmetic, non-D-finiteness as the
capstone); Paper 3, growth constants of king animals and their subclasses (the
bracket, the directed constant, Proposition 6, the grid collapse, the five
novel sequences and the exclusion boxes as labeled measurement only). Not
papers: the Lean development as an archived artifact, and the OEIS material.

**Proposition 6 and its warrant.** It was the one place the first rule bit,
since a growth-constant squeeze presented as "see the formalization" is a
harder sell than a formalized lattice theorem. It dissolved on 2026-08-06 when
Lemma 3 became a theorem: the column-join with d = max(0, h − h′) stays in the
staircase class and at fixed (i, j) is injective, because column areas are
positive, so the prefix of columns of total area exactly i is unique and no
split index is carried. Hence M(i)M(j) ≤ M(i+j), Fekete gives
µ = sup_n M(n)^(1/n), and every recorded term is a rigorous lower bound. Lemma
2 became elementary the same day: with s = ⌈√n⌉ the parts ≤ s of a partition
are fixed by s multiplicities in [0, n] and the parts > s number at most
⌊n/(s+1)⌋, so p(n) ≤ (n+1)^(2√n+2) and the stack count satisfies
P(n) ≤ (n+1)^(4√n+6); the squeeze needs only P(n)^(1/n) → 1. Proposition 6 is
an injection, Fekete, and a counting bound. `experiments/staircase_supermul.py`
under `make gate-middle-kingdom` reproduces M(1..12) by brute force over
(h, d), confirms every join over i+j ≤ 12 lands in the class and injects, finds
zero violations of the inequality over all i+j ≤ 700, and carries three
controls that must fail (the d = 0 join leaves the class, the area-(i+1) cut
fails to invert, the stacks P(n) are not supermultiplicative). The Lean
transcription followed (Paper 3, row 4). Planned and unbuilt in Lean: the
geometric layer (column-convex, HV-convex, staircase, the two cones), the
squeeze, the eight collapse propositions, the A001523 identification. Not
Lean targets, since they would formalize the wrong object: the exclusion
boxes, the amplitude-ratio formula, Conjecture 8, any trusted-digit claim.

**What does not ship as a result.** The v5 denominator formula, correct and
proved but a fact about the chosen basis (`results/arithmetic-structure.md`);
minimum site perimeter, which is A235382, someone else's theorem; the ν
exponent, since 0.6407 is what universality assigns to polyplets anyway; the
height-distribution limit shape, thin at n ≤ 40; the central-charge
finite-size fit, the strip ladder μ_H not being analytic in 1/H at H ≤ 17
(`results/growth-constant.md`); the hex diagonal formula, subsumed by the
universal one; exclusion boxes as theorems; the inventory of families beyond
polyplets, novelty unchecked on every item.

## Warrant tiers and the provenance tables

Every paper carrying tier-2 or tier-3 material gets one table mapping each
numbered result to its warrant tier and origin, plus the repository revision
and the Lean build receipt: one table, no hedging in the body.

| tier | warrant | meaning |
|---|---|---|
| 1 | jasonp-vetted | he read the proof and believes it |
| 2 | Lean-checked proof | sorry-free, axiom footprint printed and guarded (`polyplets/Polyplets/Grand/Audit.lean`, `polyplets/Polyplets/AuditOutworks.lean`) |
| 3 | exact-arithmetic certificate | machine-checkable in integer or modular arithmetic by a short independent checker; the checker unverified, the arithmetic exact |
| 4 | reproducible measurement | code, a control that must fail, a gate, an independent second computation; a measurement, never a theorem |

A claim jasonp has not vetted ships only at tier 2 or 3; tier 4 appears as
data and labeled conjecture; below tier 4 nothing appears. Common to the three
tables, as of 2026-08-06:

    repository revision   679800c
    Lean build receipt    polyplets/build-receipt-2026-08-06.log
                          lean v4.31.0, mathlib v4.31.0, 8621 targets current,
                          0 sorries, 143 audited theorems: 95 standard-axioms-only,
                          48 with named native_decide leaves, no sorryAx,
                          no anonymous ofReduceBool

### Paper 1, fixed polyplets to n = 40

Tier 4 is the subject: a record enumeration is a measurement, and each row
shows its control, gate and second computation.

| # | result | tier | origin | check |
|---|---|---|---|---|
| 1 | a(23)–a(40), a(40) = 56749893611764175164545926946127 | 4 | `results/ns_a40/`, `results/b006770_upload.txt` | `experiments/paper1_reproducibility_check.py` check A: per-height rows sum to the term |
| 2 | the triangle T(n,H), n ≤ 40 | 4 | `results/ns_a40/perheight/` | checks A, B, D, E |
| 3 | second-algorithm confirmation, n ≤ 22 | 4 | `results/redelmeier_row22/` | check C, with a control that flips one digit and must fail |
| 4 | strip transfer matrix agrees at H ≤ 14 for every n ≤ 40: 469 entries, 0 mismatches | 4 | `results/second-sources.md`, `results/strip_C14_n40_run.log` | check D recomputes 469 from the entry set |
| 5 | T(n,n) = 3^(n−1) | 1 | hand derivation; Lean `T_king` | check B, 40 entries |
| 6 | T(n,n−1) = 5(5n−9)3^(n−4) | 1 | `docs/proofs/T-n-nm1.md` | check B, 37 entries |
| 7 | T(n,n−2) = ½(625n²−2459n+1134)3^(n−7) | 1 | `docs/proofs/T-n-nm2-and-general.md` | check B, 36 entries |
| 8 | λ ≥ a(40)^(1/40) = 6.2208413587750324 | 2 | Lean `a_supermul`, `lambda_gt_of_banked`, standard axioms | `lake build`; guarded in `polyplets/Polyplets/AuditOutworks.lean` |
| 9 | component stratification, C(n,1) = C(n,n) = A001168 | 1 | `results/subclasses.md`, the 45-degree sublattice bijection | brute force n ≤ 14 |
| 10 | λ = 7.110(1), θ = −1.000(1) | 4 | `results/growth-constant.md` | differential approximants on 40 terms; an estimate |
| 11a | M_single(n) = ⌊((n−2)²+4)/8⌋, one hole | 1, not ours | Sieben 2008 Theorem 4.1, σ(e) = ⌊e²/8 − e/2 + 1⌋, verbatim; the (I′)/(II′)/moat-cycle chain in `results/subclasses.md` is an independent reproof | `experiments/maxhole_sieben_check.py` (with a control that must fail); `experiments/maxhole_moat_check.py` (3,927 animals); `experiments/maxhole_box_construction.py` (n ≤ 60) |
| 11b | M(n) = ⌊((n−2)²+4)/8⌋, all holes | 1, not ours | proved 2026-08-06 by the union argument: the minimum holds for any finite subset of Z² (Wang & Wang 1977; the Z² count in Altshuler et al. 2006), applied to the union of the holes | same script: the two closed forms agree at every k ≤ 200,000, and no subset with two or more components (k ≤ 10) beats it |
| 12 | the hole-fill bijection | 1 | `results/subclasses.md` | exact, three sentences |

Rows 11a and 11b are theorems of the isoperimetry literature and ship with
citations; the project's part is the question and the enumeration. The Lean
conditionality (`MoatBound`) is a formalization gap, not a mathematical one.

### Paper 2, the structure of the height triangle

| # | result | tier | origin | check |
|---|---|---|---|---|
| 1 | the hand-derived diagonals T(n,n−1), T(n,n−2) | 1 | `docs/proofs/T-n-nm1.md`, `docs/proofs/T-n-nm2-and-general.md` | as Paper 1 rows 6–7 |
| 2 | the defect gas: 25 = 16 + 9, and the same bookkeeping generates every P_k | 1 | `results/diagonal-formula.md` | the note's derivation |
| 3 | the universal diagonal formula: T(H+k,H) = q_k(H)·b^H for every row-local lattice, deg q_k ≤ k, H ≥ k+1 | 2 | `docs/proofs/universal-diagonal-law.md`; Lean `universal_shape_d`, `universal_shape`, `universal_shape_production`, `universal_production_int_all`, standard axioms | `lake build --no-build`; the four names guarded |
| 4 | the lattice instances (king b = 3, hex b = 2, square b = 1) | 2 | Lean `king_P1_*`, `hex_P1_*`, `square_P1_*` | named native leaves, two triangle entries per lattice; the table must say so |
| 5 | the grand form | 2 | `docs/proofs/grand-form.md`; Lean `grand_form`, `grand_form_prod`, standard axioms | guarded |
| 6 | P_k determined to k ≤ 18 from production data | 2 | Lean `P18_grand_of_banked`, `P18_grand_prod` | named leaves: the chunked weight cards |
| 7 | the ternary spine: the triangle mod 3 is governed by W³ = W² + t | 1/4 | `results/arithmetic-structure.md`; the formula and its consequences down the levels proved, the "bonus depth" section measured | `experiments/ternary_spine.py`, 15 of 15, with a 342-entry check |
| 8 | Smith normal form: all invariant factors powers of 3, ⌈(N−1)/3⌉ nontrivial | 1/4 | `results/arithmetic-structure.md`; the 3-power containment and (A1b), (A2), (B) proved, the rest conjectural | sympy SNF on the recorded triangle, N = 4..14 |
| 9 | the anisotropic generating function is not D-finite, certified degrees deg ψ_H = 1, 2, 4, 9, 29, 68, 181, 462, 1254, 3289 | 3 | `results/anisotropic-not-dfinite.md`, mod p = 2⁶¹−1 with preserved degrees | the note's exact-arithmetic checker |

Rows 7 and 8 are written with the split visible, the proved core as a result
and the measured remainder as data. Row 9's step 1 is Bousquet-Mélou &
Rechnitzer 2002 Lemma 9, cited as theirs.

### Paper 3, growth constants of king animals and their subclasses

| # | result | tier | origin | check |
|---|---|---|---|---|
| 1 | λ ≤ 9.3154 | 2 | `docs/proofs/polyplet-upper-bound.md`; Lean `certSum_le`, `lambda_le_of_buiSystem`, `RatCert.lambda_le` (standard axioms), `lambda_le_of_bui_rd3` | `lake build`; the concrete certificate depends on the named leaf `buiRD3_valid` |
| 2 | λ ≥ 6.543 | 3 | the certified strip ladder μ_17, exact rational Collatz–Wielandt with a per-H receipt, `results/growth-constant.md` | `make gate-strip-fast`: the exact routine must pass the certified numerator and fail numerator+1; `make gate-strip-cert`, the checker's must-fail-first self-test |
| 3 | µ = 3.128943269730886… for every class between staircase and HV-convex (Proposition 6) | 1 | `results/subclasses.md`, Lemmas 1–3 and the squeeze | `make gate-middle-kingdom` |
| 4 | M(i)M(j) ≤ M(i+j), and µ ≥ M(700)^(1/700) = 3.1234045… | 1, machine-checked | Lean `M_supermul`, `M_tendsto`, `M_le_mu_pow`, `mu_gt_of_banked` in `polyplets/Polyplets/StairGrowth.lean`, standard axioms, guarded | `lake build` proves the inequality for all i, j; `experiments/staircase_supermul.py` checks 700 terms with three must-fail controls; the floor is conditional on the recorded M(700) |
| 5 | 3 + 2√2 for directed king animals | 1 | Bacher 2013, reproduced against A047781 | `make gate-king-grid` |
| 6 | eight of twelve grid cells collapse onto the unfiltered row | 1 | `results/subclasses.md`, Propositions 1, 2, 3, 5 of the phase-3 note | brute-force grid n ≤ 14, `make gate-middle-kingdom` |
| 7 | ν = 2.5145796438787291885… is the growth rate of an explicitly counted half of the 4-cone series | 1/4 | Lemma 4 and Proposition 7 (rates proved); the 153 and 242 trusted digits measured | `experiments/descent_block_oracle.py`, three must-fail controls |
| 8 | the amplitude ratio r = (1/2)(w4·φ)/(w·φ), 251 trusted digits | 4, conditional | Propositions 9–11, conditional on the two amplitudes existing | `experiments/amplitude_feed_vectors.py`; the gate reproduces Table B's 54 digits |
| 9 | Conjecture 8, sharp asymptotics for the two halves | conjecture | same note | labeled as a conjecture or not at all |
| 10 | the five novel sequences; the non-D-finite exclusion boxes | 4 | `results/oeis-candidates.md`, `results/subclasses.md` | data and labeled measurement |

The phase-block decomposition under rows 3 and 7 is Gouyou-Beauchamps &
Leroux's (FPSAC 2004, §2.3; N3 below) and belongs in the body. Row 3's
conclusion has a classical square-lattice analog: Bender 1974 against the
parallelogram subclass, measured at 2.309138593330495 by
`experiments/square_staircase_area.py`. What must survive any compression of
these tables is the tier column and the split-tier rows (Paper 2 rows 7 and 8,
Paper 3 rows 7 and 8), where a reader could otherwise take a measurement for
a theorem.

## Reviewer expertise, by claim tier

Asked 2026-08-17. a(40) needs almost no mathematics and a systems reviewer;
the rest splits into three pools no one person covers.

- **Tier 0, a(40) and the enumeration record.** The mathematics is a
  one-sentence definition; the weight is on transfer-matrix enumeration as
  engineering: checkpoint and resume semantics, CRT residue recombination,
  and whether the validation chain closes (the b-file to n ≤ 20, the chain
  a(21)–a(39), the strip transfer matrix, the mod-4 and mod-8 congruences, the
  P_k confirmations on withheld entries). The Zero Harvest bug, a resume bug
  and not a math error, is what a real reviewer here catches. Bar:
  undergraduate combinatorics plus serious software-review skill.
- **Tier 1, the closed forms and diagonal structure.** P_k, the diagonal
  formula, the grand form, the cut-count identity
  Σ_configs Π_births (q − b) = q^{c(S)}, the k!·P_k ∈ Z[n] divisibility, the v5
  denominator formula, the mod-3 cubic: finite algebra over Z[q] and Q[n] a
  first-year graduate student verifies by hand or with a computer algebra
  system, several Lean-formalized. Bar: graduate-level; this is where
  machine-checkability buys something.
- **Tier 2, the asymptotic and analytic claims.** The bracket is mechanically
  tier 1, but judging its interest needs the growth-constant literature
  (Klarner, Barequet–Ben-Shachar, Madras). Non-D-finiteness needs holonomy
  machinery (Flajolet–Sedgewick, Bousquet-Mélou). The below-onset defect
  formula, the Ridgeline amplitudes, the grand-form saddle μ₂ = 42.39460 and
  α = 50/81 need singularity analysis and the saddle-point method, with four
  unproved singularity-form assumptions named in the Ridgeline note that a
  reviewer must judge from experience. The perimeter tip factor, Andrews's
  φ₂, an eta quotient, needs q-series and modular forms. Bar: a research
  mathematician active in analytic combinatorics, plausibly two.
- **Tier 3, priority.** Ghost Ship Layer 3 was correct, internally verified,
  and already in Richard arXiv:0704.0716; only a literature pass catches that,
  now standing practice on any result called new.

The practical composite is three reviewers: a computational person for a(40),
an analytic combinatorialist, and a literature pass. The headline claim is the
easiest to assess and the most corroborated; the claims needing the scarcest
reviewers carry the named unproved assumptions.

## The skeptical-reader standard

The standing standard for work meant to raise a reader's confidence in a(40).
Two rounds had produced work correct, novel, and worth nothing to that reader:
a proved theorem containing no entry of row 40, and a strip-transfer-matrix
agreement on 469 entries, a consistency check rather than a verification.

**The reader** wants the count to be wrong and is competent enough to find
out. They grant exact arithmetic, running code, honest authors and truthful
logs. They refuse to grant: the connectivity rule (both production engines
decide king-connectivity by union-find over a frontier against the previous
column's labels, so a shared misconception passes through both as agreement,
and different code, author, language, machine, instruction set or modulus is
no answer); agreement between things sharing an input (two computations
consuming the same recorded entries corroborate the transcription); a
relation fitted where it is checked; a claim about an entry whose provenance
was assumed. They cannot re-run the enumeration: row 40's height-21 phase
alone cost 36.4 h on 32 cores with a 363 GB disk peak, and Redelmeier stops at
n = 22 (about 10¹³ years of fleet time at n = 40). A check they cannot execute
is a claim.

**The exposure map**, in entries and never shares of the term, since a term
is wrong if any one entry is wrong (the share column was removed 2026-08-18).
Row 40 by provenance class, `experiments/tristruct/triangle.py`, August 2026:

| band | entries in row 40 | provenance then |
|---|---|---|
| H ≤ 14 | 14 | enumerated; strip-transfer-matrix confirmed, 0 mismatch |
| H = 15…21 | 7 | enumerated once, in the single production run |
| H = 15…19 | 5 | the unconfirmed block inside that band |
| H ≥ 22 | 19 | composed from the closed forms P_k, never enumerated |
| H ≤ 2 | 2 | the engine's analytic low-strip rows, never enumerated |

The second row was the mission; the coloring program has since confirmed
H ≤ 19, and `results/provenance-table.md` and `results/residual-cells.md` hold
the current state. An idea states in its first line which entries it reaches
and by which provenance class, quoting the loader.

**The currency.** Bits are log₂ of the a-priori probability that a wrong count
passes; a congruence mod m gives log₂(m) bits against whatever produced the
number it tests. Two counts always: bits against enumeration error over
entries actually enumerated, and bits against formula-chain error conditional
on a stated hypothesis; never-enumerated entries give 0 for the first, in the
first line. Correlated evidence does not sum: claims evaluating the same one
or two polynomials at nearby points are one claim's worth. Congruences are
calibrated against the empirical base rate over the region, fitted forms by
perturbation; perturbing an entry to see whether a congruence still holds is
vacuous.

**Four independence axes**, one line each: rule independence (name the
failure mode the idea would show if wrong and argue it is disjoint from
union-find's); derivation independence (did the derivation read recorded
data, or only the lattice definition and self-enumerated entries); input
footprint (how many recorded entries, and the largest n); checker cost (an
afternoon on a laptop from the recorded file and the checker alone). The
deliverable is a short independent checker in exact integer or modular
arithmetic, readable in one sitting, run in minutes, with a control that
fails on corrupted data: warrant tier 3, the highest without a proof; the
corruption battery and its false-pass rate ship with it. Every candidate
opens with a disclosure block: claim; entries reached with bands and
provenance; both bit counts with the condition; the four axes; input
footprint; checker path, runtime and control; sensitivity; the prior-work
search commands, including cross-branch.

**Automatic zero**, each of which cost a real round: novelty claimed without
the cross-branch search
(`git log --all --oneline --name-only -- 'results/*.md' 'docs/*.md' 'docs/**/*.md'`,
then `git show <commit>:<path>` on the hits; measured 2026-08-12, `docs/**/*.md`
alone matched 251 historical paths and missed 30 top-level files, both terms
510); fitted on every available entry instead of a subset held out by n; a
consistency check presented as verification (strip recomputation, mod-p or
CRT arithmetic, in-flight redundancy, anything sharing the frontier rule); one
bit count; provenance assumed; "the pattern holds on more entries". Ranking:
bits against enumeration error, then proof-backed over fitted, then checker
cost. Reach is not a criterion: re-verifying confirmed entries by a
rule-independent route outranks extending a shared-rule method to new entries.

## Defending a(40): the reproducibility material

Every number here was regenerated 2026-09-05 by
`experiments/paper1_reproducibility_check.py` (checks A–F, 0.1 s) from the
recorded artifacts; the provenance counts come from
`scripts/provenance_table.py --check`, run by `make gate-provenance`. The claim:
a(40) = 56749893611764175164545926946127 is correct, and so is the triangle it
was summed from, where no reader can re-run the computation;
a(41) = 393811462683918679824582849262105 rests on the same defenses with one
stated gap.

**Defense 1, every production run re-derives everything below it.** Each
maxn = N run recomputes the whole triangle and equals every prior term through
n = N−1. a(1)–a(18) match what the OEIS serves for A006770 (checked live
2026-07-30 and 2026-09-05; the site's b-file is synthesized from the DATA
field). All 40 per-height rows sum to the recorded terms (check A); the a(41)
run agrees with the recorded triangle on 760 entries at n ≤ 40
(`results/a41/PROVENANCE.md`; the assembler refuses the n = 41 row otherwise).

**Defense 2, Redelmeier, a second algorithm, to n = 22.** A three-machine,
three-architecture fleet run (24000 disjoint shards, about 120 h wall per
box, completed 2026-07-16) reproduced every row n ≤ 22 exactly. One counter
grows cell sets, the other advances a column frontier; they share no counting
logic. Check C recomputes `results/redelmeier_row22/combined.txt` against the
recorded terms with a control that flips one digit and must fail;
`make gate-g2` runs the engine against the oracle on every push, and since
2026-09-05 its rook/bishop and transpose checks fail on empty output rather
than passing vacuously. Redelmeier's cost is proportional to object count, so
whole-term second enumeration ends at n = 22.

**Defense 3, the strip transfer matrix, an independent computation per
entry.** A strip engine advances column by column through a height-H strip
carrying a king-connectivity partition state, computes
C_H(n) = Σ_{h≤H} (H−h+1) T(n,h), and recovers the triangle by the exact second
difference in H, sharing no enumeration code, frontier or state encoding with
the production engine. Result: 469 entries, 0 mismatches, H ≤ 14 for every
n ≤ 40 (dalby, 2026-07-30, about 8.6 h, revision 5239e73,
`results/strip_C14_n40_run.log`); check D recomputes 469 as
|{(n,H) : 1 ≤ H ≤ min(14,n), n ≤ 40}|. The strip engine decides connectivity by
the same union-find rule as the repository's reference oracle, so a shared
misconception about king-connectivity would survive it; the disjoint axes are
boundary granularity, accounting layer, count representation and
orchestration.

**Defense 4, the coloring program (Motley), a different counting rule.**
`cpp/motley_par.cpp` (the exact source of the Nmax-40 rows is
`results/cutcount_b1/cutcount_b1.cpp.59e90660`) never decides connectivity: it
computes A_n(q) = Σ_S q^{c(S)} over n-cell subsets weighted by component count,
by a frontier dynamic program over color-coincidence partitions in Z[q]/(q²),
and reads the connected count off a coefficient; the identity making this the
cut-count is proved in `docs/proofs/cutcount-identity.md`. It shares no code
with either engine above.

| run | reach | agreement |
|---|---|---|
| Nmax 40, `results/cutcount_b1/rows/` | H ≤ 18 | 567 entries equal the triangle; C_18 reconstructed by CRT from four primes with the fifth held out and predicted at every n (`make gate-cutcount-assembly`) |
| Nmax 41, `results/cutcount_b1/rows41/`, dalby 2026-08-20/21, about 22 h, nine 16-bit primes per height | H ≤ 19 | 589 entries with n ≤ 40 equal the triangle; the 19 entries at n = 41 equal the production engine's enumeration (`results/a41/`); the withheld prime predicts every entry at all 19 heights, 779 entries, from the 171 residue rows in `results/cutcount_b1/residues41/` (check F; `make gate-cutcount-assembly`; `make gate-motley-crt`) |

What this settles, in the words of `docs/audits/AUDIT-2026-09-02.md` (M2): for n ≤ 35
every entry is direct from the coloring program or on a formula diagonal whose
two anchors are its entries, two programs sharing no code; for a(36)–a(39)
every entry is direct or determined from its entries and ab-initio constants,
so no part depends on the original program, though "two programs sharing no
code" applies to the direct entries only; for rows 40 and 41, 19 enumerated
heights are two-program with no shared code, and heights 20 and up are one
formula strategy determined from the program's data, sharing the depth tables
D_j(20..21) with the original route. The reach credited to the program is
derived from its recorded rows and verified against the triangle by
`scripts/provenance_table.py`. Independence analysis:
`results/cutcount_b1/PROVENANCE.md`.

**Defense 5, the diagonal closed forms, withheld entries, and Undertow.** The
tall heights are composed from the closed forms P_k, k = n − H ≤ 19, whose
shape is a theorem (`docs/proofs/diagonal-law.md`, Lean-complete): degree k,
leading coefficient 25^k/k!, onset n ≥ 2k+1 (the onset is the least n from
which the formula holds), two free constants per level. Entries withheld from
the fit and enumerated later: P_15 against T(33,18), P_16 against T(35,19),
P_17 against T(37,20), P_18 against T(39,21), the last from the a(40) run's
height-21 phase; `make ns-gate-diag-pins` re-checks every composed P_k against
every enumerated entry at or above onset and re-interpolates levels k ≤ 10
from enumerated data alone. Undertow determines the same constants from short
entries: below onset an entry obeys
T(2k+1−j, k+1−j) = P_k(2k+1−j)·3^{−(k+j)} + D_j(k) with D_j computed ab initio
from cluster-weight families (D_2, D_3 computed twice, Python against C++, to
k = 22), so two depths determine a level from entries far below its onset.

| check | result |
|---|---|
| all 18 composed levels k = 2..19 re-derived from below-onset entries, `experiments/undertow_pin.py --verify --jmax=5` | 160 depth pairs at depths ≤ 5, 0 wrong |
| recorded entries predicted from shorter ones, `--audit --jmax=5` | 342 entries, 0 wrong |
| a(41) level 20 | six depth pairs, five independent checks |
| a(41) level 21 through T(38,17), T(39,18), T(40,19), `make gate-undertow-pairs` (2026-09-05) | three depth pairs at depth 5, two independent checks |

This is the first check of any kind P_18 and P_19 have had beyond their own
fit points. Until 2026-09-05 level 21 rested on one pair, and the 3-power
congruence gate cited for it tests integrality only: an error of 9 in one
table entry moves a(41) by 9 and passes (measured; that gate's first must-fail
control). The three closed-form diagonals (Paper 1 rows 5–7) hold on every
recorded entry in range, with a control perturbing each leading coefficient
that must break the fit (check B).

**Coverage, in entries.** A share of a(n) carries no decision and is not
reported (ruling of 2026-08-18; the 2026-08-06 version of this material
tabulated shares, withdrawn). Over the 820 entries of the n ≤ 40 triangle, all
counts gated:

| what | entries | source |
|---|---|---|
| recomputed exactly by at least one independent computation (Redelmeier n ≤ 22; fixed-height generating functions H ≤ 10; recurrences H ≤ 4; strip H ≤ 14; coloring H ≤ 19; a composed P_k on an enumerated entry) | 628 | provenance table, tiers B G R S M P |
| strip engine alone | 469 | check D |
| the 2026-08-06 "honest" rule, R ∪ S ∪ (P ∩ {H ≤ 21}) | 592 | check D |
| no exact recount: composed P_k above H = 21, the formula validated on withheld entries elsewhere | 189 | tier F |
| no exact recount and no closed form: T(39,20), T(40,20), T(40,21) | 3 | tier C only |
| of the 192 above, reproduced by the formula block determined from the coloring program's data (tier U) | 192 | `experiments/undertow_ri.py`, agreeing with the recorded triangle at every one |

The three entries of the fifth row were each computed by one enumeration,
checked by the mod-4 subgroup congruence and reproduced by the formula block,
never enumerated twice (the 2026-08-06 version listed 11, when the coloring
program reached H ≤ 16). Per row (check E; H ≤ 21 enumerated in the a(40) run;
k ≤ 10 is where the diagonal audit shows the level fixed by enumerated data
alone):

| n | enumerated, H ≤ 21 | composed P_k, k ≤ 10 | composed P_k, k > 10 |
|---|---|---|---|
| 29–32 | 21 | 8, 9, 10, 11 | 0 |
| 33 | 21 | 11 | 1 |
| 35 | 21 | 11 | 3 |
| 37 | 21 | 11 | 5 |
| 40 | 21 | 11 | 8 |

Row 40: 19 entries direct from the coloring program (H ≤ 19); 21 from the
formula block fitted to its data, of which three, T(40,20), T(40,21),
T(40,22), still rest on the original program's connectivity rule under the
anchor criterion of `results/residual-cells.md`.

**What the report must not claim.** Not that the strip engine is a fully
independent implementation; the coloring program crosses the connectivity
rule. Not that a(23)–a(40) are confirmed by two algorithms as whole terms; the
two-algorithm frontier is n = 22, and what can be said is that every entry of
every row n ≤ 39 is direct from the coloring program or a formula determined
from its data, while rows 40 and 41 are 19 enumerated heights two-program and
the rest one formula strategy. Not that every recorded entry has a second
computation: T(39,20), T(40,20), T(40,21) are enumerated once. Not that a(41)
carries a(40)'s validation: its 19 lowest heights are two-engine; height 20
was enumerated 2026-09-05 (dalby, 9.6 h, 76 cores, `results/a41/h20.out`) and
equals the formula prediction, one enumeration and one prediction; heights
21–41 are the formula (`paper/technical-report-gaps.md` B5 has jasonp's
asterisk decision). Not that the formula block's agreement with itself is
independent: the two fits of levels 20–21 share D_j(20..21) and the grand
form. Not that the strip check could go further on this hardware: C_14
measured about 38 GB, C_15 would need over 200 GB, the coloring program at
H = 20 hits the same wall, and H = 21 does not fit in RAM at any design
(`results/second-sources.md`). P_19's two fit points, T(39,20) and T(40,21),
carry no withheld enumeration; the superseded machine-written report graded
a(39) and a(40) one step below a(23)–a(38) for that reason, with the
vocabulary T1 = a(1)–a(22), T2 = a(23)–a(38), T2⁻ = a(39) and a(40), whose top
enumerated strata sit on the never-withheld k = 19 diagonal (that manuscript
was deleted 2026-09-06; `results/confidence.md` now orders the terms). The
Undertow re-derivation of P_19 from short entries is a consistency check, not
an independent confirmation.

The section's suggested shape: the claim; the five defenses in order, the
coloring program with its own paragraph; the coverage table with the three
once-enumerated entries named; the limits above in the section, not a
footnote; the confidence ordering; the recipes.

## The acceptance queue

Scope set by jasonp on 2026-08-17: things the machine can execute, ranked by
how much they help a(21)–a(40), the triangle and the λ bracket survive
scrutiny. All six closed by 2026-08-19.

**1. The coloring program at height 18, then 19.** Height 18 (Confetti) went
green 2026-08-19 08:58 EDT:

| quantity | value |
|---|---|
| passes | five sequential single-core passes |
| wall | 399,700 s (4.63 days) |
| peak RSS | 65.9 GB |
| frontier | 72,487,711 states |
| withheld prime | 2147483563, predicting 40 of 40 residues from the CRT reconstruction |
| T(n,18) against the recorded triangle | 23 entries, n = 18..40, 0 mismatch; the assembly re-derived from the recorded rows after the harvest |

The entries carrying only the mod-4 congruence dropped to 6
<!--q:congruence_only.count@18=6-->, retiring (36,18), (37,18), (38,18), (39,18), (40,18) and leaving (38,19),
(39,19), (39,20), (40,19), (40,20), (40,21)
<!--q:congruence_only.cells@18=(38,19),(39,19),(39,20),(40,19),(40,20),(40,21)-->; a(n) was closed under a second
connectivity rule for n ≤ 35. Height 19 under the same design (Ticker Tape)
was priced at about 197 GB against dalby's 125 and about 26 days, not
recommended; it would have retired (38,19), (39,19), (40,19). The Nmax-41 run
of 2026-08-21 reached H ≤ 19 by another route, leaving (39,20), (40,20),
(40,21); `scripts/provenance_table.py` now derives the program's reach from its
recorded rows. The band "9 → 7 → 5 entries" for row 40 is a different
quantity, the rule-independence band under the anchor rule;
`results/residual-cells.md` generates and checks both as Q1 and Q2.

**2. Fresh-clone reproducibility on a clean box.** Done 2026-08-18 on ayr.
`scripts/clean_clone_check.sh` clones from a bundle, runs every phase a reader
would run, and records an exit code per phase. Final run, revision 0171909:

| phase | wall |
|---|---|
| `make` (the gate suite; there is no separate build step) | 404 s |
| `make ns-gates` | 769 s |
| the superseded report's checker with `ALLOW_PARTIAL=1` (425 of 428; checker deleted 2026-09-06) | 902 s |
| `python3 paper/verify_l_papers.py` (336 checks, 23 must-fail controls) | under 1 s |
| `python3 paper/verify_technical_report.py` (781 checks) | under 1 s |
| `make -C paper` (11 PDFs) | 13 s |
| `scripts/term.sh 26`, giving a(26) = 102607513847014153892 | 23 s |

Four things were broken and fixed: the citations gate scoped its history class
to `git log --all`, so it passed on gympie's 50 local refs and failed with 65
dangling citations in a clone of master, every one into the campaign branches
`triangle-structure` or `half-measure`, not on origin; four translation units
did not compile under GCC (a compound literal in `strip_mu_kink`, the rest
`-Werror` warnings clang does not raise); `scripts/term.sh` began with
`cd ~/src/polyominoes`; `make -C paper` died on a TeX Live without `lmodern`.
Known rather than fixed: the superseded checker exited 1 on a clone without
`ALLOW_PARTIAL=1` because three checks read run output under `runs/sym32`; and
whether the two branches are published is jasonp's call.

**3. One provenance table per entry.** Done (commit b705687):
`results/provenance-table.md`, generated by `scripts/provenance_table.py` and
gated by `make gate-provenance`, which fails if any coverage figure drifts
from the note publishing it. The accounting had been spread across five files,
which already caused the confusion between strip coverage and withheld
entries.

**4. The OEIS files checked against primary data.** Done (commit 47dbd97):
`scripts/bfile_gate.py`, run as `make gate-bfiles`, re-derives every staged
term from recorded data, fail-closed.

**5. The λ bracket's two ends.** Done 2026-08-19.
`scripts/lambda_cert_reproduce.sh` rebuilt `strip_mu_cert` from a fresh clone
on ayr and re-derived the H ≤ 11 ladder and H = 17, diffing every rational
against the primary log, fail-closed: eleven of eleven reproduced,
`mu_17 >= 6543/1000 PASS` among them (`results/strip_mu_certificates_ayr.log`);
`attempts`, `states` and `min_ratio` agree exactly and `mu_float` to all ten
printed digits; H = 17 cost 4559 s on ayr against 772.7 s on gympie.
`paper/L3-lambda-bounds.tex` states 9.3154 in ten places and mentions 9.3153
only in a footnote forbidding it (the certificate proves 20000/2147 = 9.31532…,
so truncating would claim 3.2e-5 more than it gives) and in the exact
expansion inside the proof.

**6. Adversarial re-read of the report.** Done (commit caffcc1); the findings
are the next section, applied by jasonp alone.

Below the line by his criterion, open but not making a(40) more believable:
the Exact Change basis test at H = 13, the Ridgeline depth-amplitude family,
the below-onset constants, Lean formalization of the cut-count identity.

## Audit of the main report, 2026-08-18

Three passes over `paper/technical-report.tex`; nothing in it was changed.

**Mechanical: clean.** `paper/verify_technical_report.py`: 781 checks, 0
failures. Spot checks outside the verifier, all holding: free/a = 0.125000 at
n = 32 to six places, and the one-sided count approaches a(n)/4; hole rows sum
to a(n) (n = 4: 109 + 1 = 110); T(n,n−1) = (25n−45)·3^(n−4) gives T(5,4) = 240
and T(6,5) = 945; the enclosure claims are sharp (a one-cell hole needs its
four orthogonal neighbors, which are king-connected, so 4 cells suffice; two
one-cell holes at (0,0) and (1,1) are enclosed by exactly 6 cells, matching
the hole table's n = 6, k = 2 entry of 2); "terms 1–18 match A006770" is
correct for the entry as imported 2026-06-19, which ends at a(18), while
`oeis/A006770.txt` shows a(19) as the staged addition.

**The T(n,n−1) derivation holds.** Interior placements 16(n−3) and
(4·1 + 1·5)(n−3) = 9(n−3), so 25(n−3)·3^(n−4); boundary 2·5·3^(n−3) = 30·3^(n−4);
25(n−3) + 30 = 25n − 45. The 25 is the pair weight of L1's proof.

**"P_k can be fixed after computing the 3k-th row" is right and looks wrong.**
A blind degree-k fit needs k+1 values at or above onset, rows 2k+1 … 3k+1; the
figure is correct because the previous sentence supplies 25^k/k!, after which
k values and row 3k suffice. L1's corollary does better: any two values at or
above onset determine a level once the levels below are known.

**"λ ≈ 7.11, checkable from Table 1" is the loose claim.** The table gives

    a(40)^(1/40)   = 6.2208      (the Fekete floor, not λ)
    a(40)/a(39)    = 6.9352
    a(39)/a(38)    = 6.9308

and 7.11 is an extrapolation of the ratio sequence; one Richardson-style step
on the last two ratios gives 7.112. The honest sentence names the operation.

**The provenance sentence understates the work in both directions.** The
abstract said 23 ≤ n ≤ 35 were computed twice on different machines and
a(36)–a(40) once. Every run recomputes the whole triangle to its own n, so
a(36) was computed five times, a(37) four, a(38) three, a(39) twice, and only
a(40) once, not as replay (a(28)'s run was ayr-solo on x86 and re-enumerated
H3–H15 where a(24) had been produced on dalby, aarch64). But "twice" in the
strong sense did not happen for 23–35 either: the same engine and
connectivity rule, tall bands from closed forms. The accurate sentence: every
term through a(39) is recomputed by at least one later run, across two
machines and two instruction sets, by one engine and one connectivity rule;
a(40) alone was computed once.

**Literature.** The enumeration collides with nothing by construction;
Mertens (1990) and Redelmeier are the prior art. The gap then was the empty
Reproducibility section, since written.

**Collisions as support.** Each published result the machinery reproduced is
an external validation: the cut-count rule is the Fortuin–Kasteleyn/Potts spin
representation while the production engine tracks connectivity through
frontier signatures in the Jensen tradition, the two classical
representations of one partition function, so their independence is a fact
from the literature; the perimeter-defect identity k = 2c + t is
Asinowski–Barequet–Zheng's k = e + 2f, so an enumeration leaning on it cites
rather than justifies, and their framework (a rational generating function per
defect with cyclotomic denominator) is the route to proving the interpolated
king perimeter results; Richard's rectangles area law was re-derived unawares,
the control arm reproduces Klarner–Rivest and Bender constants to certified
precision, and Bousquet-Mélou–Fédou's solved square case stands behind the
king version. The list became `docs/external-anchors.md`.

## Proof audit of the L papers

The priority passes (`docs/l-papers-record.md`,
`docs/l-papers-record.md`) asked whether each result is new; this
audit asked whether it is right, prompted by L3, whose Proposition 6 carried a
false proof through a five-phase trim, a tic pass and a coinage pass, all of
which read prose rather than arguments. Method: re-derive the step that could
silently fail (injectivity of an encoding, exhaustiveness of a case split, a
threshold, a hidden hypothesis) and, where brute force is cheap, check against
enumerated data with controls that must fire. Paper numbers predate the
2026-08-23 contraction: L2 is now Part II of L1, L7 inside L5, L10 inside L8,
L9 withdrawn.

**L9, fixed.** The final step was printed as
Σ_φ w(φ) = Π_i (b_i + (q − b_i)) = q^m, wrong as written because b_φ(v_i)
depends on the choices at v_1..v_{i−1}, so there is no fixed b_i; the source
proof in `docs/proofs/cutcount-identity.md` uses downward induction on a
history for that reason. The conclusion is unaffected; replaced by the
induction.

**L3, the repaired proof re-derived, holds.** For u with parent d, N(u) ∩ N(d)
has 4 cells for orthogonal d (u = (0,0), d = (1,0): (0,±1) and (1,±1)) and 2
for diagonal d (u = (0,0), d = (1,1): (0,1) and (1,0)), so frames carry
8−1−4 = 3 or 8−1−2 = 5 slots. Bounding every frame by the 5-slot alphabet
(1+x)^5 is a valid over-count and the root's 8-slot frame is one constant
factor. The injectivity the broken proof lacked is supplied by the replay
decoder, machine-verified over every animal with n ≤ 8.

**L7, Lemma T against enumerated data, holds, slack measured.**
`experiments/l7_lemma_audit.py` on dalby, two independent block oracles (DFS
and DP agree through n = 16), the per-h split summing back to T(n):

| step | statement | verdict |
|---|---|---|
| (i) | T(n) ≥ 2T(n−1) | holds, n ≤ 16 |
| (ii) | T_h(n) ≤ 2T(n−h) | holds |
| (iii) | T_h(n) ≤ T_1(n + h(h−1)/2) | holds |
| (iv) | T_1(i)T_1(j) ≤ T_1(i+j) | holds |
| (v) | T(n) ≤ 4 max_{h≤3} T_h(n) | holds |
| (vi) | T(n) ≤ 4T_1(n+3) | holds |

The bite: min T(n)/T(n−1) = 2.515 against the required 2;
min T_1(i+j)/(T_1(i)T_1(j)) = 2.000 against the required 1;
max T(n)/T_1(n+3) = 0.119 against the allowed 4. Steps (i) and (iv) have about
a factor of 2 to spare and (vi) a factor of 34, so the checks confirm the
steps against gross mis-statement, not their constants. Two of five controls
did not fire, reported by the script as checks with no bite.

**L5 and L7, the phase decomposition and mirror equality, hold.** Enumerating
unrestricted HV-convex polyplets by phase path to n = 13: no animal visits both
middle phases (the class is identically zero, used by both papers without
stating, so total = via(1,0) + via(0,1) + neither exactly); the mirror
equality A_(1,0)(n) = A_(0,1)(n) holds termwise for every n ≤ 13 (at n = 13,
1333383 each of 2677214); the remainder is 1, 2, 4, 9, 21, 50, 118, 270, 598,
1280, 2652, 5335, 10448, ratios declining from 2.381 to 1.958 over n = 6..13,
0.39% of the class at n = 13, consistent with the sub-exponential stack bound
and too short to be decisive alone.

**L4, the extraction recurrence was mis-indexed, fixed.** Theorem 6 wrote
Σ_{δ≤σ} c_δ(x,H) G_{H−δ}(x) = 0 with no lower bound on δ and argued at
x = 1/μ_{H_0} that every δ ≥ 1 term refers to a lower height while the δ = 0
term has the pole. With p_i = Σ_j p_ij(x) y^j, the coefficient of y^H in
p_i ∂_y^i F sits at height H + i − j, so greater heights occur whenever i > j;
the smallest counterexample, ∂_y F = 0, extracts to (H+1) G_{H+1} = 0 with no
term of height H, and slices of greater height do not converge at 1/μ_{H_0}.
Repair: put m := max{i − j : p_ij ≠ 0} ≤ r, let c(x,H) be the coefficient of
the top slice G_{H+m}, and instance at H = H_0 − m (legal for H_0 ≥ r), which
puts G_{H_0} on top with every other term strictly below. Then c ≠ 0 by
construction (some p_{i,i−m} survives and the falling factorials (H+m)_(i)
have distinct degrees in H), the recursion through δ = 1, 2, … is unnecessary,
and the conclusion reads: at most r exceptional heights among H ≥ r. Both
effective tables survive unchanged against the ψ-degrees 1, 2, 4, 9, 29, 68,
181, 462, 1254, 3289.

**L4, "boxes from monotonicity and irreducibility alone", overclaim, fixed.**
Both families read ψ_H off the recorded G_H; the second needs irreducibility
certificates on top, which is why its table is the weaker. Retitled: the first
extends the theorem to all roots of ψ_{H_0}, the second uses it at the
dominant root only.

**L4, the rest, holds.** Lemma 3 (μ_H an algebraic integer with house μ_H):
Fatou gives Q_H(0) = 1, the reversal is monic and integral, every root of the
reversal has modulus at most μ_H, and the minimal polynomial divides it. Lemma
4 (strict monotonicity): G_H = C_H − 2C_{H−1} + C_{H−2} with
ν_H > ν_{H−1} > ν_{H−2}, so the pole at 1/ν_H is not cancelled. Lemma 5
(Northcott) and the exclusion-box arithmetic hold.

**L2, the unconditional half, holds.** Proposition 1 (Pólya integrality): the
window [2k+1, 3k+1] is exactly k+1 consecutive integers, on which 3^{3k+1−n}
has a nonnegative exponent while Theorem A is in force (n ≥ 2k+1); the two
ranges meet exactly. Proposition 2 needs P_0(0) = 1, and P_0 is constant
because T(n,n) = b^{n−1} counts walks. The mod-3 theorems are conditional on
congruences checked to k ≤ 17 and were not re-derived.

**L1, Theorem B, the one L1 declares unformalized, holds.** The valuation
bound v_p(Ŵ_c) = (2k_c − l_c − 1) v_p(b) + v_p(W_c) ≥ (k_c − 1) v_p(b) needs
k_c ≥ l_c and v_p(W_c) ≥ 0, which holds because W_c is a count; the case
k_c = 1, l_c = 0 gives 2 − 0 − 1 = 1, so ≥ v_p(b) ≥ 1, and the exception is
exactly (1,1). Uniqueness of the survivor: every row of a cluster has size ≥ 2
and length ≥ 1, so surplus 1 forces one row of two cells, the surviving weight
is one cluster type's W_c, and w := W_pair mod p is a single scalar; k_c ≥ 1
for every cluster, so no negative power of b appears.

**L8, a citation gap, fixed.** It cited no source and said "singularity
analysis gives the constants"; it now names Flajolet–Sedgewick, the
square-root branch point pointed at Theorem VII.8.

Not audited: L6 (its one proposition labeled a sketch, attributed to
Asinowski, Barequet and Zheng for the square lattice, and exercised by the
enumerator's brute-force gate; its k = 6 claims re-derived from census data in
`paper/verify_l_papers.py`) and L8's below-onset statements (each labeled
derived, measured or assumed, with four named assumptions). The pattern: both
defects, L3's false proof and L9's false factorization, are steps that look
like bookkeeping; neither changes a stated result; prose review and numerical
agreement miss them, both papers' numbers being right; re-deriving the step
finds them.

## Novelty searches, N1–N6

Run 2026-08-06, gating Papers 2 and 3. Method: the citation neighborhoods of
the Bacher, Bousquet-Mélou, Rechnitzer and Barequet papers in `literature/`, then
targeted searches, then the source read rather than the snippet; every verdict
rests on a PDF held locally or a measurement in this repository. "No OEIS
match on nine terms" is weak evidence when the class was defined here.
Unobtainable papers go to `literature/MISSING.md`.

| # | question | verdict |
|---|---|---|
| N1 | is the staircase squeeze folklore? | not found as a theorem; its conclusion is classical for square-lattice polyominoes by area, and its ingredients are in the N3 paper |
| N2 | HV-convex king animals under another name? | no: not in the OEIS, not in the literature searched |
| N3 | the block factorization in the column-convex literature? | yes, a collision: Gouyou-Beauchamps & Leroux 2004 §2.3 |
| N4 | a published upper bound on λ for polyplets? anything past Bacher's 6.475 below? | no on both |
| N5 | a universal (lattice-class) diagonal formula in print? | no, but a strong analog in the polycube dimension-defect line |
| N6 | a collision with Rechnitzer's Haruspicy? | no: different object, and the shared step was already credited |

**N3.** Gouyou-Beauchamps & Leroux, "Enumeration of symmetry classes of convex
polyominoes on the honeycomb lattice", FPSAC 2004, arXiv:math/0403168, §2.3:
any convex polyomino decomposes into blocks by the growth phases of its upper
and lower profiles; a column's state is a pair (i, j) with i, j ∈ {0, 1, 2};
transitions from 1 to 0 and from 2 to 1 or 0 are impossible; a block H_ij is a
maximal run of columns in one state. H00 and H22 are stack polyominoes (Lemma
2's outer blocks); H01, H10, H12, H21 are equinumerous by reflection
(Proposition 9's argument); the middle blocks are staircases, H02 = Pa = H20,
with Pa by area being A006958. So Lemma 1's shape in the HV-convex king note is
prior art twenty-two years old. Its ancestry: the square-lattice companion
(Leroux, Rassart & Robitaille, Adv. Appl. Math. 21 (1998) 343–380), read
properly after a first mistaken report of a text-free scan, uses
Temperley–Bousquet-Mélou strata (directed convex polyominoes from
Bousquet-Mélou 1996 Theorem 3.4, Burnside for the classes), not phase blocks;
the FPSAC'04 French abstract is the same paper; Denise, Dürr &
Ibn-Majdoub-Hassani FPSAC'97, recovered from the Wayback Machine, uses strata
column by column; Ibn-Majdoub-Hassani's 1996 Orsay thesis was not obtained
(`literature/MISSING.md`) and is unlikely, unchecked, to hold the phase blocks. So
2004 is the earliest source. What survives as the project's: the class is
HV-convex king animals, whose middle-block weight min(h,h′) + 1 against the
square lattice's min(h,h′) is the whole difference between µ = 3.1289… and
2.3091…; Proposition 6 is a statement about all intermediate classes; and the
operator-level reading (block-triangularity, the 4-cone floor rewriting exactly
one copy of min(h,h′)+1) with the phase split of the series, ν = 2.5145…, and
the amplitude identity r = (1/2)(w4·φ)/(w·φ). Actions: cite at Lemma 1, at
Lemma 2's stack identification and at Proposition 9; present nothing of the
decomposition as new; keep Propositions 6, 7, 10, 11.

**N1.** The conclusion is classical for square-lattice polyominoes by area:
Bender (1974) has convex polyominoes growing at 2.30914…, the staircase
(parallelogram) subclass is A006958, and a 400-term exact dynamic program
(`experiments/square_staircase_area.py`) gives its ratio as 2.309138593330495
at n = 200, 300 and 400, identical to 16 digits, so the subclass carries the
superclass's full growth as Proposition 6 says for the king lattice. No source
states that every class between staircase and HV-convex shares a growth
constant, nor the squeeze. Nearest: Barequet, Ben-Shachar & Osegueda, Comput.
Geom. 98 (2021) 101790, §3, states the lower half as a remark (a
concatenation-closed subfamily's constant is a lower bound) without the upper
half; Kim & Pinna, arXiv:2509.04568 (September 2025), builds constants for walk
and surface classes by concatenation, with no convex subclasses and no king
lattice. Present Proposition 6 as the king-lattice theorem, note the
square-lattice conclusion is implicit in the solved models, and claim no
technique.

**N2.** The OEIS lookup on 1, 4, 16, 61, 221, 766, 2566, 8390, 26982 returns no
match (`experiments/oeis_lookup.py`, read-only, 2026-08-06); searches for king,
8-connected or next-nearest-neighbor convex enumeration return the
ordinary-polyomino literature only. King animals appear in the enumeration
literature only as whole families: Mertens, J. Stat. Phys. 58 (1990) 1095,
perimeter polynomials for the square lattice with next nearest neighbors to
s = 13; Bacher (2013), the directed and multi-directed cases.

**N4.** No published upper bound on λ for polyplets, and nothing beating
Bacher's 6.475 below. The upper-bound literature (Klarner–Rivest,
Barequet–Shalah, Barequet–Ben-Shachar, Kim–Pinna 2025) is square, hypercubic,
polyiamond and polycube; the king lattice is absent, including from the 2025
concatenation paper. Percolation-side sources give perimeter polynomials and
cluster statistics, not bounds. The 9.3154 certificate has no competitor
because there is no prior bound.

**N5.** Not found for lattice-animal height triangles. Closest, with the
defect in dimension: Barequet, Barequet & Rote, Combinatorica 30 (2010)
257–275 (for fixed n the polycube count is a polynomial in d); Barequet &
Shalah, SoCG 2015 and European J. Combin. 63 (2017) 146–163, Theorem 1,
DX(n,n−k) = [2^{n−k}/(k−1)!]·n^{n−2k−1}·(n−k)·P_{3k−4}(n) with P monic of
degree exactly 3k−4, whose stated payoff, extrapolation from 3k−3 known
values, is the P_k protocol and the strongest argument that fitting with a
proved degree bound is standard. They lack the sharp onset (n ≥ 2k+1, failure
at n = 2k verified on all recorded data) and work in one lattice family. From
Asinowski et al. (2012, the explicit k = 3 case): "diagonal formulae" is their
term; the shape was predicted by Peard & Gaunt, J. Phys. A 28 (1995)
6109–6124, eq. (2.15), with Luther & Mertens supplying h_k for k ≤ 7 and
Barequet–Shalah proving it in 2017, so the earliest occurrence is 1995; their
conjecture that h_k has leading coefficient 2^{k−1}/(k−1)! rhymes with
25^k/k!, the shared content being an explicit exponential-over-factorial
leading coefficient (monic versus not is a normalization), while the project's
comes with a mechanism (25 = 16 + 9 is the two-cell cluster weight, k! is
unordered defects). BBR 2010 Theorem 12 derives the ratio limit from Madras
1999, the citation the project uses for a(n+1)/a(n) → λ. A re-run on the
field's own key found two more families: Barequet & Magal, Comput. Geom. 108
(2022/23) 101919, a perimeter-defect algorithm to k ≤ 5 (not held;
`literature/MISSING.md`); and OEIS A308359 (R. J. Mathar, 2019), fixed polyominoes
by bounding-box width, the transposed square T(n,H), with T(n,n−1) = 4n−8 for
n ≥ 3 known and T(n,n−2) = 8n²−51n+86 for n ≥ 5 an open conjecture that
Theorem A settles (`docs/proofs/universal-diagonal-law.md`,
`experiments/oeis_a308359_check.py`). What Paper 2 may claim: the phenomenon
(fix a defect, get a polynomial times an exponential with degree governed by
the defect) has at least four instances and is not new; what survives, in
decreasing confidence, is the universal theorem (one proof for every row-local
lattice, b = |D| entering as b^H), the sharp onset (failure at n = 2k as a
non-cancellation; A308359's n ≥ 5 is 2k+1 at k = 2, read off data), the first
closed forms for king animals by height with coefficients from a finite
cluster table rather than a fit, and a settled conjecture in someone else's
triangle. Not the project's: the statement shape, the term, and the
prove-the-degree-then-interpolate protocol.

**N6.** Haruspicy 1 (Rechnitzer, Adv. Appl. Math. 30 (2003) 228–257) proves
the cyclotomic-denominator structure for bond animals; Haruspicy 2
(math/0406450) non-D-finiteness for self-avoiding polygons; Haruspicy 3
(math/0408054) for directed bond animals, recording that directed site animals
are solved, which is why the program never turns this way. This object is site
animals by height and the argument is arithmetic (Northcott on the degree of
one distinguished pole) where theirs is topological (accumulation of the pole
set). The shared ingredient, extracting the y-coefficients of the ODE to get a
linear recurrence, Bousquet-Mélou & Rechnitzer 2002 Lemma 9, was credited in
`results/anisotropic-not-dfinite.md` on 2026-08-01.

Neither paper was blocked; two PDFs were added to `literature/` and two references
to `literature/MISSING.md`. The later per-paper passes (the L9 identity is the
FK/Potts correspondence; L6's defect identity and cyclotomic theorem are
Asinowski–Barequet–Zheng's; Bousquet-Mélou–Fédou is L5's antecedent;
Baxter–Guttmann and Jensen–Guttmann are Undertow's near neighbor) are in
`docs/l-papers-record.md` and `docs/l-papers-record.md`.

## The square-lattice record is n = 70, not n = 56

Checked 2026-08-23. The number entered the tree as "Jensen 2003, n = 56",
correct about one computation, and was re-quoted as the literature record,
which moves.

| quantity | reach | source |
|---|---|---|
| fixed square polyominoes, totals | n = 70 | OEIS A001168 b-file, contributed by Barequet and Ben-Shachar, a(0)..a(56) credited to Jensen; last line `70 18500792645885711270652890811942343400814` |
| the same, independently | n = 59 | Shirakawa, Enumeration of Polyominoes up to Size N=59, arXiv:2510.22446, October 2025 |
| the square bounding-box triangle | not published at any n | the project's own, `results/bbox_square4_n21.txt`, stops at n = 21 |
| perimeter-graded square counts | not to the order the project needs | |

What moved is the totals; every use the project has wants the triangle by
height or a perimeter grading, and neither is published. Six places quoted 56
and no conclusion moved: the square headline needing entries below onset at
H ≤ 28 is no closer, that being triangle data; the bijection-fattening kill
(a(40) needs polyominoes of at least 160 cells) stands, 160 being more than
twice 70 and the closing objection being the bijection test; the Sykes–Essam
kill stands, needing perimeter-graded data to order about 200
(`results/closed-doors.md`). The guard: quote the record from one place that
says when it was last checked.

## Removals before publication, 2026-08-22

The rule: never cut evidence, never cut a closed door; everything removed was
a duplicate, a stray, or an output nothing reads, and empty stderr files were
kept because a clean stderr is a finding. Recover any with
`git log --diff-filter=D -- <path>` and `git show`.

| removed | size | why |
|---|---|---|
| a file of 10,000 uniform random 19-cell specimens | 2.5 MB, 120,248 lines | cited by nothing; regenerable from its header (seed 0x13) |
| the k = 7 perimeter-defect calibration runs | 891 KB, 36 files | the census was priced at 76–179 days on the 76-way pool and declined; conclusions in `results/perimeter.md` |
| the remains of the ayr power cut of 2026-08-07 | 3 files | the lesson is in the project retrospective (removed from the repository) |
| six stray empty files under `experiments/tristruct/` and `results/` | 0 bytes each | empty where their siblings are not |
| three k = 5 perimeter-defect censuses | 256 KB, 17,557 lines | exact subsets of the k = 6 censuses by `comm -23`; their `.log` run records kept |
| sixteen gate-suite console logs of 2026-08-05..07 | 324 KB | read by no document |

Kept: `results/dalby-run-telemetry-202606/` (217 files, provenance of the
a(35) and holes runs; thinning is jasonp's call); `experiments/tristruct/`
(170 files; a decision about apparatus); the Ghost Ship sandbox, an input
slice frozen at 74b2c20 plus the experiment's output, of whose 278 tracked
files 257 were sandbox-only, 9 shadowed a live file and differed, and 12 were
identical to a live file but were 12 of the 21 files in a pre-registered
published slice, so deleting them would falsify the record; the n = 70 k = 5
censuses `results/perimdefect_square8_n70_k5.txt` and
`results/perimdefect_square4_n70_k5.txt`, which appear as reproduction commands
in the perimeter notes and in the docstrings of
`experiments/perimeter_defect_gf.py` and `experiments/perimeter_max_structure.py`,
a recorded command being the provenance of the result under it. Corrections in
the same pass: `scripts/run_full_make.sh` had predicted 5–10 minutes from logs
of which fifteen recorded no wall time and one recorded 10m47s, and now quotes
the measurement; `results/dalby-perf-audit.png`, cited by nothing, matches the
audit's own probe (maxn = 24, heights 1–15, revision 5fadde3) and is embedded
in the engine record; the OEIS check the spread-8 growth probe asked for was
run (absent at three query widths, the square and king rows returning A001168
and A006770 as controls); the depth-5 price of "~16 h / ~103 GB" or
"~51 GB / ~23 h" stood unmarked in eight tracked files against the measured
3.1–6.7 h and 8.5–16.1 GB, and all eight now carry the correction beside the
old number.

## OEIS: policy and staging

Nothing has been submitted, and as of 2026-09-06 the OEIS is not to be
contacted; `oeis/` and `oeis/wave2/` are staged only. The lineup and the
rule that an entry may cite a P paper as warrant and never an L paper are in
`docs/publication-split.md` §4. Policy research of 2026-07-05: October 2023, a
blanket ban approved two days after A361990's ChatGPT credit; 16 April 2026,
softened to accountability, every sequence needing a human author responsible
for the correctness of any content a language model produced. Still
prohibited: AI text in pink-box replies; AI as author; AI-generated full
comment text; any AI-generated program the submitter does not understand; bulk
submissions. Accepted precedents: A361990 (Israel, 2023: a ChatGPT-suggested
idea, human Maple and independent Python); A384729 (Kleinwaks, June 2025: all
code written by the model with significant prompting, disclosed in-entry, a
human-defended bound). Rejected after April 2026, from recycled drafts:
A396919 (hidden zero-width characters, formula errors, obsequious replies;
3 July 2026); A396591 (approved, then reverted as clearly AI-generated);
A396876 (the author dodged "how much is AI-generated?"); A396748 (AI text in
pink boxes alone); A394641 (AI-sounding prose from a translation tool). The
control, A396719: the question answered precisely (AI solely as a coding
assistant, all mathematics derived and verified by the submitter), three
siblings approved, the one rejection being table format. Adopted for the
staged batch: the one-paragraph answer in jasonp's words, stating exactly what
the machine did and what he verified; every comment line jasonp-authored, the
machine checking meaning only; pink-box replies his alone; no program text in
the entries; six related extensions in one batch is normal practice.

## Formalization tooling considered, 2026-09-04

Anthropic's Lean proof of Fermat's Last Theorem by the Frey-curve and
modularity-lifting route, on the Prove2Me workspace (arXiv 2608.28433): about
13 million lines, 30,300 theorems (29,500 in the final cone), 60,475 modules,
no sorry, the three standard axioms, about 11 days and about 6 billion output
tokens, reviewed afterward by Kevin Buzzard. Decision: take the architecture,
join no platform, start no formalization. Worth adopting at no exposure:
statements in one module and each proof in its own, so a failed attempt
rebuilds one leaf; a generated declaration index over `polyplets/Polyplets/`
(77 files) and the imported Mathlib declarations, which
`docs/lean-environment.md` §4 hand-codes as recipes; immutable statements read
against the source by jasonp and then frozen, since the expensive failure is a
statement quietly weakened until it goes through. Not at face value: the
server verification is the same Lean check as `lake build` plus the axiom
guards, adding provenance not correctness; automated faithfulness auditing
runs at about 43% accuracy by the paper's figure. The work it would serve,
formalizing Lemmas 1–5 and the main identity of
`docs/proofs/cutcount-identity.md` and the follow-on that the window dynamic
program realizes the sum, is open since 2026-08-14 and unstarted; this
structure moves its cost by perhaps a third. Not doing: an account, an API
key, a proposal, any upload, a second subscription, an agent fan-out.

## What was found, and how much of it is proved

A polyplet (polyking, king animal) is a set of cells on the square grid that
hangs together when cells touching only at a corner count as joined. Counted
by cell number up to translation, the sequence is OEIS A006770: 1, 4, 20, 110,
638, 3832, …. The literature had reached n = 18; this project reached n = 41.
No formula is known; the counts grow like λ^n times a slowly varying factor.

**The theorem to take away.** With H the height of the bounding box and
T(n,H) the triangle:

> For every fixed k and every n ≥ 2k+1, T(n, n−k) = P_k(n)·3^(n−1−3k), where
> P_k is a polynomial of degree k. The onset n ≥ 2k+1 is sharp.

`docs/proofs/diagonal-law.md` has the shape, the onset and the integrality;
sharpness (failure at n = 2k for every k) was closed 2026-09-05 by reducing
the depth-1 defect's derived quartic mod 3 (`results/below-onset.md`), resting
on that note's identity (II), derived but not yet written up standalone. It
holds on every row-local lattice with 3 replaced by the local neighborhood
size (`docs/proofs/universal-diagonal-law.md`). Behind it the grand form
(`docs/proofs/grand-form.md`, Lean-complete against standard axioms) gives
exactly two new constants per level, so two independent equations determine
a level.

**The growth constant.**

    6.543 ≤ λ ≤ 9.3154     both ends machine-checkable in exact arithmetic
    λ ≈ 7.110(1)           the estimate, four methods agreeing

Lower bound the certified height-17 strip constant, upper bound an exact
rational convolution certificate, middle a measurement
(`results/growth-constant.md`, `docs/proofs/polyplet-upper-bound.md`). The
upper half is stuck for a known reason: every upper-bound method encodes an
animal by what it looks like within a fixed radius, and the measured
over-count is diffuse and grows with n, the signature of the constraint that
distant parts must connect. The strip ladder μ_H enforces connectivity exactly
within a bounded height and converges from below; the certificate has
unbounded reach, relaxed connectivity, and floors from above. λ is not a
function of coordination number: the king lattice and the lattice whose
neighbors are the orthogonal steps of length 1 and 2 both have eight neighbors
and λ ≈ 7.11 against λ ≈ 8.97, 26% from local cycle structure.

**Counting from short entries instead of tall ones.** For row 40 the two
tallest entries took three-quarters of the processor time and the disk from
69 GB to 363 GB. Below its onset the diagonal formula is off by a structured
amount, computed exactly: at depth 1 the generating function is an irreducible
quartic, giving rate 9, exponent −1/2 and amplitude √6/(27√π); the same
closure holds at depths 2, 3 and 4, all derived (`paper/L8-below-onset.tex`,
`results/below-onset.md`). Knowing the error exactly turns a short entry into
a valid equation for the same polynomial, so the tall entries stop being
necessary; that is Undertow, and a(41) was computed without enumerating the
two tallest heights. On the square lattice, where the counts are published,
the below-onset fit equals the classical one and reproduces the tall entry it
was denied at every level tested (`results/undertow.md`), the one check that
crosses out of the project.

**Arithmetic and analysis.** The anisotropic generating function is not
D-finite, an unconditional theorem by an arithmetic obstruction
(`results/anisotropic-not-dfinite.md`). The triangle mod 3 is governed by
W³ = W² + t (`results/arithmetic-structure.md`). θ = −1 is measured as
−1.000(1) by differential approximants on 40 terms; the same code on the
square lattice's 70 published terms gives −0.9995 against the king's −0.9997
and recovers the published square growth constant to six digits
(`results/growth-constant.md`). The denominator formula
ĉ_k = v₅(odd‼ ≤ k) + [k ≡ 1 mod 10] is proved.

**Doors that closed** (`results/closed-doors.md`, each with its
counterexample): compressing the transfer matrix by rank loses, the compressed
operator being 425 times sparser at height 8 but larger in dimension already
at height 4; tracking the complement's connectivity is worse at every block
count by exactly the factor b; a bijection to a decorated polyomino class is
correct and buys nothing, the image carrying identical information at the
same cost, which became the project's triage test; the finite-size fit for a
central charge cannot be done from the strip data because the correction
series has not converged, not because a logarithmic term is required; four
algorithmic levers measured dead against one wall, that tracking connectivity
is what costs.

## Open problems

- The gap between 6.543 and 9.3154; the estimate 7.110 is firm, the proof not
  close (`results/growth-constant.md`).
- An explicit basis for the characteristic-2 rank collapse, real and large but
  not constructive without one; the largest open technical question.
- Depths beyond 4 of the below-onset defect, which would extend Undertow.
- The maximum number of holes of an n-cell polyplet: 0, 0, 0, 1, 1, 2, 2, 3, 4,
  no closed form, specific to this lattice since four cells enclose a hole
  here where the square lattice needs eight.
- Lean formalization of the cut-count identity and of the claim that the
  window dynamic program realizes the sum, unstarted; the Lean geometric layer
  for Proposition 6, the eight collapse propositions and the A001523
  identification, unbuilt.
- The novelty negative for Undertow's near neighbor is five web queries and
  should be re-run against a citation database before any submission.
- The L papers' ledgers read "human verification: none"; the reading is
  jasonp's.
- Whether the campaign branches `triangle-structure` and `half-measure`, into
  which 65 citations point, are published.

## Reproduce

    scripts/clean_clone_check.sh                          # fresh clone, every phase, exit code per phase
    make gates                                            # every gate
    make gate-g2                                          # Redelmeier against the oracle and fixtures
    make gate-kink-oracle                                 # the production routine against the published a(1..18)
    make gate-cutcount-assembly                           # the coloring program's rows assemble to the triangle
    make gate-motley-crt                                  # C_18 and C_19 reconstructed from residue rows
    make gate-provenance                                  # the per-entry source table and its counts
    make gate-residual-cells                              # every restatement of the residual figures
    make gate-undertow-pairs                              # a(41)'s level 21 three ways at depth 5
    make gate-undertow-congruence                         # the 3-power congruences on the unrecorded defects
    make ns-gate-diag-pins                                # every composed P_k against every enumerated entry at or above onset
    make gate-bfiles                                      # every staged OEIS term re-derived from recorded data
    make gate-strip-fast; make gate-strip-cert            # the lower bound's certificates; the checker's self-test
    make gate-middle-kingdom; make gate-king-grid         # Proposition 6's ingredients; the directed constant
    scripts/lambda_cert_reproduce.sh                      # the H<=11 ladder and H=17 from a fresh build
    python3 scripts/provenance_table.py --check
    python3 experiments/paper1_reproducibility_check.py   # checks A-F
    python3 paper/verify_technical_report.py              # 781 checks
    python3 paper/verify_l_papers.py                      # L1, L3, L4, L6
    python3 experiments/undertow_pin.py --verify --jmax=5
    python3 experiments/undertow_pin.py --audit --jmax=5
    python3 experiments/undertow_ri.py
    python3 experiments/staircase_supermul.py
    python3 experiments/l7_lemma_audit.py
    python3 experiments/square_staircase_area.py --nmax 400
    python3 experiments/oeis_lookup.py 1,4,16,61,221,766,2566,8390,26982
    python3 experiments/oeis_a308359_check.py
    python3 experiments/ternary_spine.py
    pdftotext literature/gouyou-beauchamps_leroux_2004_convex_polyominoes_honeycomb.pdf - \
      | sed -n '/Growth phases of convex polyominoes/,/H00 and H22/p'
    git log --diff-filter=D -- <path>                     # find a removed file's commit

## Sources

- `docs/publication-strategy-2026-08-18.md` (deleted 2026-09-06; its content is above)
- `docs/sortie-publication-plan.md` (deleted 2026-09-06; its content is above)
- `docs/provenance-tables.md` (deleted 2026-09-06; its content is above)
- `docs/reviewer-expertise-tiers.md` (deleted 2026-09-06; its content is above)
- `docs/skeptical-reader-standard.md` (deleted 2026-09-06; its content is above)
- `docs/main-paper-audit-2026-08-18.md` (deleted 2026-09-06; its content is above)
- `docs/prove2me-note.md` (deleted 2026-09-06; its content is above)
- `docs/oeis-ai-policy.md` (deleted 2026-09-06; its content is above)
- `docs/acceptance-queue.md` (deleted 2026-09-06; its content is above)
- `docs/paper1-reproducibility.md` (deleted 2026-09-06; its content is above)
- `results/removals-2026-08-22.md` (deleted 2026-09-06; its content is above)
- `results/novelty-sortie.md` (deleted 2026-09-06; its content is above)
- `results/l-paper-proof-audit.md` (deleted 2026-09-06; its content is above)
- `results/literature-record-56-corrected.md` (deleted 2026-09-06; its content is above)
- `results/mathematics.md` (deleted 2026-09-06; its content is above)
