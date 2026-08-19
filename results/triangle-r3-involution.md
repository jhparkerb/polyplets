# Involution hunt — queue rows L4-3, LEAD-2 (and the L4-4 desk survey)

> Some files cited below were filed on the unmerged branch `triangle-structure` and the unmerged branch `half-measure` and never reached this one: `git show <branch>:<path>`.

2026-08-12, gympie. Wave-3 queue-dispatched scout, round 3, per
`docs/triangle-round3-brief.md`, scored under
`docs/skeptical-reader-standard.md`. No blind list — the rows came from
`results/triangle-r3-queue.md` and are already on the record. Script:
`experiments/tristruct/r3_inv_candidates.py` (+ `.log`), pure Python, exact
integers, 2.2 s total wall, animals self-grown (no banked data read during
derivation; A006770 asserted as the grower's regression, per-height groups
formed by measured bounding box).

**Verdict in one line: every animal-level cell-move involution tested fails
involutivity, for one nameable family-level reason — move-validity is a
global (connectivity) predicate, so first-site keying is unstable under its
own move — and the non-group involutions that DO beat the group ceiling
exist but live on extended objects (subset, coloring), which is exactly the
cancellation family L6 has already costed as its survivors. L4-3 closes
negative; LEAD-2 closes by merger into L6-1/L6-2, with one new referee-facing
gift: the bijective (sign-reversing-involution) reading of L6's identity.**

## Disclosure block (mapped to phase 1 per the brief)

    claim:                             closure of queue rows L4-3 and LEAD-2: no
                                       animal-level involution survives mechanical
                                       test; the surviving non-group involution
                                       class is L6's cancellation family, priced
                                       in results/triangle-r3-l6-wildcard.md
    share of a(40) reached:            0% as delivered (closure, no route of my
                                       own; the merged route's reach — 48.00%,
                                       H=15..20, 50.84% with H=21 at phase 2 —
                                       is priced and claimed in L6's file, not here)
    bits against enumeration error:    0 (nothing proposed beyond the merger)
    bits against formula-chain error:  0   conditional on: nothing
    rule independence:                 the tested family needs no cut (whole-animal
                                       rules; both ticket levels would clear
                                       trivially) — moot, since none survives
    derivation independence:           animals self-grown; banked triangle read
                                       only for the band parity table below,
                                       after all candidate tests had run
    input footprint:                   7 banked cells read (T(40,15..21), for the
                                       parity screen), max n = 40; 0 consumed by
                                       any derivation
    checker:                           the probe itself: r3_inv_candidates.py,
                                       2.2 s laptop, RED control = a deliberately
                                       broken shift rule that must FAIL (it does;
                                       see log) plus the forced-parity assertion
                                       |Fix| == T (mod 2) on every passing rule
    sensitivity:                       the RED rule and the parity assertion are
                                       the battery; the parity check also caught
                                       a real rule bug (C4 at n=1, below)
    prior-work grep:                   git log --all --oneline --name-only --
                                       'results/*.md' 'docs/*.md' 'docs/**/*.md'
                                       | grep -iE 'involut|franklin|sign-revers|
                                       matching|pfaffian|determinant|parity';
                                       plus working-tree grep for sign-reversing/
                                       franklin/pfaffian. Hits: triangle-hunt-
                                       klein-parity.md (round 1, GROUP involution),
                                       matching-pair-convention.md (perimeter,
                                       unrelated), and the queue itself. No prior
                                       non-group involution work on any branch.

## Entry ticket

An involution defined on whole fixed (n,H) animals has no cut, no frontier,
no labels: king-connectedness enters only through the validity check of the
move, evaluated on the complete object by BFS. Such a rule would clear
level 1 and level 2 trivially — that is precisely why the row was worth
dispatching — and I say so and mean it. The finding is that no tested rule
of this class IS an involution; the ticket never gets presented. The
extended-object survivor's ticket is argued and cleared in L6's file.

## The forced-parity lemma, stated once (it reframes the independence question)

If σ is any involution on the fixed (n,H) animals, then T(n,H) ≡ |Fix(σ)|
(mod 2) — for every correct σ, whatever its rule. So two correct involutions
can never *disagree*: the brief's test (b) "check it disagrees somewhere" is
vacuous for correct rules. Independence of a parity bit lives entirely in
the RULE CLASS that computes |Fix(σ)| — a disagreement, if one ever showed
up, would be a bug certificate for one of the two computations, which is
exactly what a second route is for. Corollary used below as a screen: any
rule whose fixed set is provably empty on a class is dead a priori wherever
T is odd, and the band is mostly odd — T(40,H) mod 2 for H = 15..21 is
(1,0,0,1,1,1,1), all seven cells `'real-sweep'` by
`triangle.provenance(40,H)` (loader run 2026-08-12). So "every animal
admits a move" rules — tempting, since every n ≥ 2 animal has ≥ 2 non-cut
cells (`results/move-graph-connectivity.md`) — can never be involutions on
the odd cells.

## The candidate table

Tested mechanically on ALL fixed king animals, n ≤ 7 (176,411 animals,
grower regression against A006770 exact), every (n,H) class separately.
"wd" = image stays a valid animal of the same (n,H); "inv" = σ(σ(A)) = A.
RED control (a broken max-cell shift rule) fails as required; the harness's
forced-parity assertion holds on every passing class.

| rule | wd | inv | fixed set | verdict |
|---|---|---|---|---|
| C1 v-mirror (group baseline) | yes | yes | v-symmetric classes; parity ≡ T on all 22 classes | PASS — group, sanity anchor only |
| C2 first-site 2×2 diagonal slide, global validity | yes | **no** (first fail n=4; e.g. 63/996 pairs broken at n=6 H=3) | — | FAIL |
| C2L same slide, candidacy decided locally | **no** (230/3775 leave the class at n=7 H=3) | no | — | FAIL, both horns |
| C7 first-site diagonal-pair swap | yes | **no** (from n=3) | — | FAIL |
| C3 top/bottom-row Franklin (lex-smaller row moves to the far side) | yes | **no** (from n=3 H=3) | — | FAIL |
| C5 extremal-cell reflection through the box centre | yes | **no** (from n=3 H=2) | — | FAIL |
| C4 first horizontal 1-slide | **no** (n=1: the move is a translation, i.e. the identity on translation classes — caught by the parity assertion, not by inspection) | no | — | FAIL |

Minimal counterexample for C2, the family's failure in miniature (n=4, H=2):

    A: ###      B: ##.      C: #..
       ..#         .##         ###

A's first switchable site slides the top-right cell down; but the move
CREATES an earlier switchable site in B, so σ(B) fires there instead and
lands on C ≠ A.

## The obstruction, named (this is the closure of L4-3)

For a site-keyed toggle σ to be an involution, the key must satisfy
key(σ(A)) = key(A). The key must select only valid moves (else
well-definedness fails — C2L's horn), and validity of a cell move is
connectivity of the result, a global predicate: toggling cells at {p,q}
changes which moves at OTHER sites are valid. So the first-valid-site key is
not a function of move-invariant data, and it drifts — C2's horn, the
counterexample above. The two horns are jointly exhaustive for this family:
candidacy is either validity-aware (unstable key) or validity-blind (invalid
images). Franklin's original escapes because partition parts are
order-independent — moving the smallest part cannot change which part is
smallest-but-one — i.e. move-validity there is monotone in a statistic the
move preserves. King-animal rows/cells interact through connectivity and
have no such monotone statistic; that is the fact about the family, not the
instance.

Two escapes, and both are real:

1. **Make validity automatic.** Toggle something that can never break the
   constraint. That forces the toggled data OFF the cell set — onto a
   decoration — and the canonical decoration is a component-constant
   coloring of an ARBITRARY subset S: toggling the color of a non-anchor
   component of S is well-defined and self-inverse because the key (the
   component structure of S) is untouched by the toggle. Fixed points =
   connected S with the trivial coloring, so #pairs ≡ T (mod 2), and the
   pair count is a purely local DP. This is precisely the sign-reversing
   involution behind Σ_S q^(c(S)) — i.e. **the involution row, pursued to
   its end, rederives L6's cancellation family** (survivors L6-1/L6-2,
   costed in `results/triangle-r3-l6-wildcard.md`; the family was held on
   the `second-source` branch as B1). LEAD-2's answer is therefore YES —
   non-group involutions outside the group ceiling exist, they give
   T ≡ M mod 2^m per cell (L6's partition-basis residue ladder is the
   computable form), and they are already priced. What this file adds for
   phase 2: the bijective reading is a three-line, referee-facing proof of
   what the DP counts, strengthening the level-1 story L6 argues
   algebraically.
2. **Restrict to strata where validity is locally decidable.** On
   column-convex/HV-convex subclasses (the Middle Kingdom poly-time tier)
   a move's validity is a local test, so a site-keyed involution can have a
   stable key there. Filed as an open row (INV-3); it yields stratum
   parities, not T, unless the non-convex remainder gets its own counter.

## Fixed-set computability — why even a passing local rule buys nothing

Had any first-site rule passed, its fixed set is the animals with NO
qualifying site — a local-pattern-avoidance class. Those are
full-dimensional (the probe's fixed fractions sit at 60–80% and do not
collapse with n) and countable only by a strip transfer matrix, i.e. the
frontier rule class this round exists to escape: the parity bit would be
computable at n=40 only by the method it was meant to check. A Franklin-type
collapse (polynomially small fixed sets, forced staircases) is what to want,
and nothing in the tested family shows a trace of it. The only known
small-fixed-set involutions on these objects remain the group ones —
λ^(n/2)-sized at best, priced out by L4's answer-size floor
(`results/triangle-r3-l4-quotient.md`).

## Independence verdict against the banked D2ax bit

By the forced-parity lemma the residue of any correct involution equals the
banked bit's value on every cell — necessarily, not suspiciously. The tested
candidates' fixed SETS differ from the D2ax-symmetric sets almost everywhere
(the probe tags the coincidences; e.g. C1's fixed sets differ from D2ax's on
every class with H ≥ 3, same parity throughout), so a surviving non-group
involution would have been a genuinely different quantity carrying the same
residue — a new route, never a new value. That is the correct honest framing
of what LEAD-2's prize was: rule-class diversity, which the merger into
L6-1/L6-2 delivers, plus the mod-2^m extension that a single parity bit
cannot.

## L4-4 desk survey — determinant/Pfaffian over GF(2), half a page, no code

The honest prior was no, and the survey confirms it, with one precision.
Pfaffian/determinant counting (Kasteleyn; Valiant's matchgates/holographic
algorithms) expresses constraints that factor over edges/vertices of a
planar or bounded-genus incidence structure — perfect matchings, ice-type
configurations, local tensor contractions. Connectivity of an induced cell
set is not such a constraint: it is a global monotone property, and no
determinant formulation for counting *connected* induced subgraphs (even
mod 2) is known in the literature this project has touched; the second-source
lane B file (`git show second-source:results/second-source-candidates-B.md`,
row K2) already records that rank/representative-set determinant machinery
is sound for existence, unsound for exact counting, and that its *counting*
variant (BCKN, arXiv:1211.1505 — determinants over the cut space) "IS
candidate B1", i.e. collapses into the cancellation DP the project now
holds. The one true "parity is easier" phenomenon available here is not
Pfaffian at all: it is the cancellation identity itself (disconnected
subsets cancel mod 2^m in the colored count), which needs no determinant
and is already L6's survivor. Remaining Pfaffian-proper hope would need the
king graph planar (it is not) and the object edge-local (it is not).
Answer: **no determinant/Pfaffian route distinct from the already-held
cancellation family; L4-4 closes into it.** One live successor filed:
whether BCKN-style GF(2) cut-space bases can COMPRESS the cancellation DP's
partition state (row INV-4) — that is a basis question inside the held
family, not a new formulation, and it is the only determinant-shaped idea
with a mechanism.

## Queue rows filed

Appended to `results/triangle-r3-queue.md`: INV-1 (closes L4-3, the
two-horn obstruction), INV-2 (closes LEAD-2 by merger into L6-1/L6-2, with
the bijective-proof gift), INV-3 (OPEN: site-keyed involutions on convexity
strata, where validity is local), INV-4 (OPEN: GF(2) cut-space basis
compression of the cancellation DP's partition state — the one idea here
that could move L6-1's RAM ceiling at H=21), INV-5 (closes L4-4 per the
survey above).

## NOT ESTABLISHED

- The two-horn obstruction is measured (four families, 176k animals,
  n ≤ 7) and argued, not proved as a theorem quantified over all site-keyed
  rules. What would establish it: a formal statement that any involution
  whose key is computable from A alone and whose moves preserve (n,H) must
  have key(σ(A)) = key(A), plus a proof that validity-aware keys cannot
  satisfy this on a class containing the counterexample pair above. The
  measured universality (every family, same failure signature) is the
  evidence offered.
- Whether the fixed sets of the FAILED rules are TM-countable was asserted
  from their measured non-collapsing fractions, not from a constructed
  transfer matrix.
- Citations from memory in the L4-4 survey (Kasteleyn; Valiant holographic
  algorithms) are named as background, not load-bearing; every load-bearing
  claim there is sourced to the second-source branch file or to L6's
  verified-this-session citations (arXiv:1103.0534, arXiv:1211.1505).
  Nothing was added to `papers/MISSING.md` because no unobtainable paper is
  relied on.
- Whether an involution with a Franklin-type polynomially-small fixed set
  exists for king animals: open in principle; nothing tested or found points
  toward one, and INV-3 is the only surviving direction with a mechanism.

## Artifacts

- `experiments/tristruct/r3_inv_candidates.py` + `r3_inv_candidates.log` —
  the probe: grower (A006770-regressed), seven rules, RED control,
  forced-parity assertion, per-(n,H) verdicts with drawn counterexamples

---

## Appended 2026-08-12 evening — INV-4 measured: characteristic-2 rank collapse, dispatch report

Lead-dispatched follow-up on INV-4. Probe:
`experiments/tristruct/r3_inv_rank_probe.py` + `.log` (gympie, 51 s total,
exact arithmetic; automaton rebuilt from the definition, census regressed
against Motzkin(H+1)−1 at every H, functional cross-checked against
brute-force enumeration at H ≤ 3, RED control = corrupted stencil must
miscount vs brute force — it does).

### 1. Does the rank-based technique apply?

Split the question, because "rank-based" names two different things in BCKN.

**Representative sets proper: no.** Bodlaender–Cygan–Kratsch–Nederlof,
"Solving weighted and counting variants of connectivity problems
parameterized by treewidth deterministically in single exponential time"
(arXiv:1211.1505; Inform. & Comput. 243 (2015)) keeps a small set of
representative partial solutions — sound for existence/optimization; their
own counting variant is the determinant/cut algebra, which on this problem
IS the cancellation family (second-source B-file, row K2: "that algebra is
candidate B1"). Nothing to transfer: the transfer target already exists and
is L6-1.

**Generic linear compression: yes, and it is basis-independent.** The
minimal dimension of ANY field-linear realization of the strip functional —
partition basis, coincidence basis, spin basis, anything — is the Hankel
rank of the functional itself (A-S1's frame, second-source
`results/scaling-exploration-A.md`). So the independence adversary's pending
question (coincidence vs connectivity partitions) is orthogonal here: the
floor and any headroom below it apply to B1 and the incumbent identically,
whatever the isomorphism verdict. A-S1 measured that rank mod p = 2³¹−1
(no collapse worth having: rank/states ≈ 1/4.8 at H = 10, growth ≈
2.79×/height, non-constructive). **The INV-4-specific gap was
characteristic 2 — the CKN phenomenon (Cygan–Kratsch–Nederlof, "Fast
Hamiltonicity checking via bases of perfect matchings", arXiv:1211.1506:
matchings-connectivity matrix has rank ≤ 2^(t/2−1) over GF(2), with an
EXPLICIT factorization). Measured today: the collapse is real here too.**

### 2. Measured ranks (observability closure = exact Hankel rank; the
automaton is deterministic so reachability is full)

| H | states (=Motzkin(H+1)−1) | rank GF(2), x=1 | rank GF(2^16), graded, 2 random t | A-S1 mod-p (quoted, not recomputed) |
|---|---|---|---|---|
| 4 | 20 | 6 | 6, 6 | 6 |
| 5 | 50 | 15 | 15, 15 | 17 |
| 6 | 126 | 27 | 27, 27 | 35 |
| 7 | 322 | 58 | 58, 58 | 88 |
| 8 | 834 | 112 | 112, 112 | 204 |
| 9 | 2187 | 229 | 229, 229 | 501 |

Two facts jump out. Grading is free in char 2 (GF(2^16) graded rank equals
the ungraded GF(2) rank at every point — six for six). And the char-2 rank
tracks **0.42–0.45 · 2^H** (27/64 = 0.42, 58/128 = 0.45, 112/256 = 0.44,
229/512 = 0.45) where the mod-p rank grows ≈ 2.5–2.8×/height. This is the
CKN signature: a ~2^H-dimensional char-2 structure under a
Motzkin/Bell-sized state space.

### 3. Exact numbers at H = 21, before and after

Before (exact, closed forms, computed in the probe):

    incumbent column states  Motzkin(22)−1              =   400,763,222
    B1 column-cut states     Σ_k C(22,2k)·Bell(k)       =   941,574,417
      (L6's window projection for the same engine: ~1.54e9)
    q=2 spin basis, naive    3^21                       = 10,460,353,203
    q=2 spin basis, VALID    (runs monochromatic, exact) =   131,836,323   (H-orientation)
                                                           54,608,393     (W-orientation, cut 20)

After, mod 2 only (extrapolated from six measured points on the 0.44·2^H
law): **≈ 0.9–1.3 × 10⁶** at H = 21 (0.44·2²¹ = 9.2e5; growth-2.05 fit
1.3e6). Against the floors: L3-1's spatial Motzkin floor at H = 21 is
M(11)–M(12) = 5,798–15,511 — the compressed dimension sits ~10² above it, no
violation; A-S1's mod-p temporal floor extrapolates to ~1×10⁸ — the char-2
number sits 100× BELOW that, which is legal because it is a different
field, and is precisely the collapse. Compression ratio vs B1's state space:
**~10³**.

### 4. RAM and wall shape — with the honest conditional stated first

**The rank is a floor and an existence statement, not yet an algorithm.**
My probe computes the compressed space by observability closure, which
costs more than counting does — at H = 21 that route is absurd. An
algorithmic win needs an EXPLICIT basis with explicit transitions, which is
exactly what CKN have for matchings (their factorization is constructive)
and what nobody has here yet: NOT ESTABLISHED, and it is the entire
remaining question of this row. Conditional on such a basis: dimension
~10⁶ × 41-bit payload ≈ **megabytes**, dense-transition wall ~10¹²–10¹³
bit-ops ≈ **laptop hours**, for T(40,21) mod 2. That would be a fifth rule
class at the band's hardest cell for pocket change — IF the basis is found.

**The unconditional, immediately usable part** is the valid-coloring count:
L6-2's spin-basis backstop was priced off 3^20 ≈ 3.5e9 states / ~18 GB
per buffer / fleet-days. The monochromatic-run constraint is exact and
free, and the true reachable count is 54,608,393 (cut 20) — **64× less: ~0.3
GB per buffer, single-box, wall dropping from fleet-days toward
single-day scale.** That repricing stands on a closed-form state count, not
an extrapolation, and upgrades the H = 20..21 mod-2 backstop regardless of
what happens to the basis question.

### 5. Does the compressed representation keep the residue/CRT layer? No.

The collapse is a characteristic-2 phenomenon: mod p the measured ranks
(A-S1) show no comparable drop and their floor is non-constructive at
~10⁸ dimension for H = 21. The CRT ladder (8-bit primes, L6-1) stays in the
partition basis at its priced 160 GB for H = 21. What char-2 compression
buys, if the basis lands, is the parity bit only — L6-2's territory,
upgraded. Whether anything survives over Z/4 (the 5-coloring identity gives
a Z/4 realization; Hankel theory over Z/4 is murkier than over a field) is
unmeasured — filed as a row.

### NOT ESTABLISHED (this section)

- An explicit basis/factorization realizing the GF(2) rank — the
  constructive step. CKN's matchings basis is the precedent, not a proof it
  exists here. Without it, INV-4 changes no phase-2 pricing except the
  valid-coloring repricing of L6-2, which is unconditional.
- The 0.44·2^H law beyond H = 9 (six points, clean, but extrapolated ×2¹²
  to H = 21). Next cheap point: H = 10 GF(2)-only, ~tens of minutes, not run
  (gympie job discipline; it would firm the law, not change the verdict).
- A-S1's mod-p numbers are quoted from the branch file, not recomputed
  (probe script named there: scripts/probe_hankel_rank2.py).
