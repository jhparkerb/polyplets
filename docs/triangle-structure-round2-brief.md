# Round-2 brief — prove the sleeve unit formulas

2026-08-11. Supersedes `docs/triangle-structure-team-brief.md` for all
further work on the T(n,H) triangle. That brief is executed; its round is
committed at `aa2b1eb` and synthesized in `results/triangle-hunt-synthesis.md`.
Read the synthesis before anything here.

---

## Why this brief exists, and why it is not another hunt

Round 1 asked for relations that check a(40) without re-running the engines.
It found none, and — more usefully — it found out **why**, in a form sharp
enough to redirect the work:

> **The fittable region and the checkable region are disjoint.**

Two independent results establish it.

- **Frame exhaustion.** Below onset, each cell carries a fresh R_k
  coefficient visible at that cell alone, so the diagonal law's shape theorem
  imposes no relation among open residues. Every periodicity-class hypothesis
  over that region came back machine-BARREN, and the 97-ansatz algebraic
  search returned an empty kernel — a genuine exclusion for its box, since a
  true equation inside the box would fit any truncation.
- **Provenance geometry.** The deficit families are the one cross-k structure
  that survived. But a *fitted* family needs d ≤ 6 (d=7 has 3 fit cells,
  d ≥ 8 at most 2), and every fittable line's law-free cells sit at
  H = 2k+1−d ≥ 22 — wired-P_k territory. The 27 **enumerated** law-free
  sleeve cells all have d ≥ 8. Fitting can never reach them.

So more mining cannot work, and the machine already swept the low-order space
(920 hypotheses, three testable directions, full negative recorded). What
remains is the route that carries no fit region at all:

> **A proved unit formula. Prove it at d = 3..7 where the pattern is visible,
> then push the same machinery to d = 8..19, which land on enumerated cells.**

That is the whole mission. If it succeeds, the H = 15..19 block — 43.84% of
a(40), resting on a single production sweep — becomes checkable against
statements that never consumed it. If it fails, we will know which tower level
it failed at, which is itself worth having.

---

## The object

Write **family_d(k) = (n, H) = (3k+1−d, 2k+1−d)**. The diagonal index is k and
the exponent is e = n−1−3k = **−d**, so every deficit family lies below onset
by construction with

    T(n, H) = P_k(n) / 3^d .

Measured residues mod 3 along k (`results/triangle-hunt-synthesis.md`,
negative 5; reached independently by four agents):

| d | 1 | 2 | 3 | 4 | 5 | 6 | 7 | ≥8 |
|---|---|---|---|---|---|---|---|----|
| cycle | (1,1,1) | (2,2,2) | (2,0,1) | (2,2,2) | (2,2,2) | (2,1,1) | (2,2,1) | none |

d = 1 is the spine's T3 and is proved. d = 2 is proved
(`experiments/deficit2_proof.py`). **d = 3..7 are open and are the target.**
The break at d = 8 is clean and unexplained — explaining it is a legitimate
secondary outcome.

The sharpest single statement, and the recommended entry point because it is
verified on **enumerated** cells rather than formula cells:

> **v₃(P_k(3k−2)) > 3 ⟺ k ≡ 1 (mod 3)**, exceptionless through k = 11
> (values 7, 4, 4 at k = 4, 7, 10, all real-sweep; 3 everywhere else).

That is the d=3 family's zero structure in valuation form.

## The named route

`docs/proofs/diagonal-law.md` Step 4 gives [y^k]F = R_k(z)/(1−3z)^(k+1) with
R_k ∈ ℤ[z], deg ≤ 2k+1. The proved d=1,2 cases went by
Lagrange–Bürmann to a master curve; `experiments/deficit2_proof.py` is
explicitly flagged reusable for (n,k)-linear families. The obstruction is
known and quantified: the method needs the **mod-3^(d+2) master equation**,
and `results/defect-gas.md` stopped at the explicit **mod-27** one. Each
further level costs one boundary-cluster weight extension.

So the work is: extend the tower one level, prove d=3, and see whether the
method's cost per level is constant or grows. That answer determines whether
d = 8..19 is reachable, and it is the go/no-go for the whole mission.

---

## Team shape — smaller, and weighted the other way

Round 1 ran seven agents: one harness, four proposers, two refuters. The
refuters produced the round's sharpest results (the disjointness geometry, the
luck calibration, two independent recomputations, and every substantive
correction); the four parallel proposers overlapped heavily. Weight
accordingly.

**Four agents, sequential where the work is sequential.**

1. **Tower builder (1).** Derive the mod-81 master equation from the defect-gas
   decomposition, extending `results/defect-gas.md`'s mod-27 result by one
   level. Report the cost of the level honestly — this is the load-bearing
   measurement for everything downstream. Desk work; no fitting.
2. **Prover (1).** With the mod-81 equation, run the Lagrange–Bürmann
   argument for d = 3. A proof, or a specific named obstruction. Do not
   settle for "the pattern holds on more cells" — that is round 1's output
   and it is already banked.
3. **Adversary (1), fixed, reads both.** Default verdict "the proof has a
   gap". Audit the derivation line by line the way round 1's refuters audited
   the parity theorem and the two-term inequality — both of which survived,
   so this is not a formality but it is also not hopeless. Specifically check
   every step where a 3-adic valuation is claimed, and every place the
   argument assumes the d=1,2 structure transfers.
4. **Extension scout (1), only if 1–3 succeed.** Determine whether the proved
   method reaches d = 8..19. If yes, that is the first real check on the
   enumerated H = 15..19 cells and the project's remaining exposure closes.
   If no, name the level it dies at.

If step 1 shows the per-level cost grows, **stop and report**. That is a
complete answer to the mission and is worth more than a partial tower.

---

## Rules carried forward, with the round-1 fixes folded in

Everything in the round-1 brief's rules of engagement still applies (exact
integer arithmetic, named scripts under `experiments/`, no stdin, no /tmp, no
binaries outside `build/`, do not edit `paper/technical-report.tex`, do not
commit `docs/viva-*.md`). Plus these, each earned by a round-1 failure:

**1. Sweep the branches before claiming novelty.** Three files cited by the
round-1 brief live on branch `second-source`, including
`docs/second-source-team-brief.md` — the ruling the team was judged by. Two
agents rediscovered its central conclusion unaided. Before any novelty claim:

    git log --all --oneline --name-only -- 'results/*.md' 'docs/**/*.md'

and grep the off-branch hits with `git show <commit>:<path>`. A grep of the
working tree alone is **not** a novelty check.

**2. Provenance is a first-class field, and the harness's answer wins.**
Round 1's costliest error was agents writing "real-sweep" for cells the loader
correctly flagged `closed-form-Pk`. Any claim about a cell must quote
`triangle.py`'s `provenance(n,H)`, not an assumption. The rule of thumb that
would have prevented it: **H ≥ 22 is wired P_k for every n**; H = 3..21 is
real sweep; H ≤ 2 is the engine's closed-form low strip.

**3. Report two bit-counts, never one.** Round 1 showed a claim can have real
teeth against formula-chain error and *zero* teeth against enumeration error,
because the cells were never counted. State both:

    bits against enumeration error   (the mission's number)
    bits against formula-chain error (conditional, and say on what)

If the cells in question were never enumerated, the first number is 0. Say so
in the first line of the claim, not in a caveat at the bottom.

**4. Match the calibration instrument to the hypothesis class.** A
perturbation study is *vacuous* for a congruence — perturbing a cell changes
its residue, so it fails by definition and "0 false passes" measures nothing.
For congruences use the empirical base rate over the law-free cells. For
fitted forms use perturbation. Do not copy the previous report's method.

**5. Correlated evidence is not independent evidence.** Round 1's four
deficit families' law-free hits all evaluate the same one or two polynomials
(P_14/P_15) at nearby points: ≈5 conditional bits on **one object**, not four
braces. Before summing bits across claims, check whether they touch the same
underlying quantity.

**6. Prior work index up front.** The round-1 list omitted
`results/subgroup-mod4.md` and `results/percell-mod4.md`, which had already
banked most of one proposer's assignment. Whoever writes the next brief builds
the index mechanically from `results/*.md` titles first, and does not hand-curate
from memory.

---

## What is settled and must not be re-opened

Re-deriving any of these scores zero:

- The four Wave-0 sweep survivors are restatements of the banked H ≤ 4 column
  recurrences (confirmed three ways). Column unipotency mod 2 is an H ≤ 4
  accident — q_5 mod 2 is not unipotent.
- Recurrence-form column structure predicts nothing in-grid above H = 4;
  onsets are n = 43 (H=5) and n = 107 (H=6).
- Only directions (0,1), (−1,1), (−1,2) have slices spanning fit and holdout.
  Arbitrary slopes are untestable, not merely unmotivated.
- Strip-TM recomputation is a consistency check, not verification
  (`git show 2b3115b:docs/second-source-team-brief.md`). Coverage is not the
  bottleneck; the connectivity rule is.
- The bivariate GF is not D-finite (unconditional theorem). No global
  P-recurrence in (n,H).
- The mod-3 open region is not algebraic inside a spine-sized box.

## Deliverables

One markdown file under `results/` per proved statement or named obstruction,
carrying the two bit-counts of rule 3. Negative results get written down: a
tower level whose cost is prohibitive is a real finding and closes the mission
honestly. One ranked summary at the end.

Success is a **proof**, or a **specific named obstruction with the level it
dies at**. "The pattern holds on more cells" is not a deliverable — round 1
already produced that, and round 1's own geometry shows where it stops.
