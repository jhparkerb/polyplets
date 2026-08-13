# R3 lane L5 — connectivity as a constraint, not an algorithm

2026-08-12. Lane deliverable for `docs/triangle-round3-brief.md`, scored under
`docs/skeptical-reader-standard.md`. Blind list pre-registered first at
`results/triangle-r3-blind-l5.md` (10 families, filed 18:20 EDT before any
work). Scripts: `experiments/tristruct/r3_l5_king_connected.lean`,
`r3_l5_king.lp`, `r3_l5_cnf_encode.py`; logs alongside.

**First line, per the brief: the lane's routes clear level 1 (semantic
independence) in full; level 2 is cleared by the Lean route, argued and
partially cleared by the ASP/CNF routes, and does not reach n = 40 in any
case. The cost verdict is NO — no generic third-party counter reaches
H = 15..21 at n = 40, even modulo a small prime — anchored on measurements
below and on the prior kill banked on the `second-source` branch.**

## Disclosure block (mapped to phase 1 per the brief)

    claim:  T(n,H) formalised three ways with connectivity stated in the
            encoding, evaluated by third-party machinery; banked values
            reproduced at small n; no route reaches the band
    share of a(40) reached:            0% at phase 2 as a count route
            (bands: none at n=40; the formalisation re-derives n<=7 cells,
            provenance 'real-sweep' per triangle.provenance — H=3..7 — and
            the H<=2 'closed-form-lowstrip' cells)
    bits against enumeration error:    0 at n=40 (nothing here counts the
            band); at n<=6 the Lean route independently recounts all 23
            banked cells it touched (exact match = full confirmation of
            those cells, which were already Redelmeier-confirmed)
    bits against formula-chain error:  0   conditional on: n/a (no formula
            chain touched)
    rule independence:                 YES at the definition level; see
            entry-ticket paragraph (level 1 all routes; level 2 Lean fully,
            ASP/CNF argued)
    derivation independence:           the encodings read only the lattice
            definition; banked cells were used solely as the post-hoc
            comparison target
    input footprint:                   23 banked cells consumed for
            comparison, max n = 7; zero banked cells in any derivation
    checker:                           phase-2 artifact would be: (a) the
            Lean file itself — a one-screen definition a referee reads plus
            a kernel/native evaluation they re-run in minutes at n<=6; it
            exists today and ran; (b) for reach, none — no route survives
            costing
    sensitivity:                       deferred to phase 2 per the brief;
            note the CNF self-test already includes a per-subset
            disagreement assertion over 74,388 subsets (RED-style: any
            encoding/BFS mismatch aborts)
    prior-work grep:                   commands + findings in §Prior work

## Entry ticket — where is king-connectedness decided?

**Level 1 — cleared by construction, all three routes.** Connectedness is
*defined*, not computed, in each encoding: in Lean as
`(kingGraph s).Connected` (Mathlib's `SimpleGraph.Connected`, a Prop); in ASP
as the stable-model least fixed point of `reach/2`; in CNF as
root-reachability unrolled to n−1 steps with biconditionally-defined
auxiliaries. The machinery that *decides* the stated predicate is third-party
in each case: Mathlib's decidable-reachability instance
(`Mathlib/Combinatorics/SimpleGraph/Connectivity/Finite.lean:56-65`), clasp's
unfounded-set check, a #SAT counter's clause propagation. The engines'
hypothesised misconception — the harness pack's three shared propositions
(cross-cut stencil completeness, label-partition sufficiency, completion
predicate) — cannot reproduce in a one-screen definition that contains no
cut, no labels, and no completion predicate.

**Level 2 — where the decision actually happens at run time, route by
route.**

- **Lean:** Mathlib decides `Connected` by generic reachability over the
  whole vertex set at once — no sweep order, no frontier, no cut. Failure
  mode if wrong: a bug in Mathlib's `DecidableRel G.Reachable` instance,
  i.e. a generic finite-graph reachability error that would break Mathlib's
  own test surface, not a king-lattice-specific rule. Disjoint from all
  three shared propositions. **Level 2: cleared.** (Same independence class
  as `symcount_fast`'s BFS — but here the decision procedure is not even
  project-authored.)
- **ASP:** connectivity is decided by clasp's unfounded-set machinery
  rejecting circular `reach` justifications. Failure mode if wrong:
  unfounded-set admission — a disconnected set passing because a `reach`
  cycle justified itself. That is a defect class of stable-model semantics
  implementations, exercised by every inductive-definition ASP program ever
  run; disjoint from frontier label-partition modes. What is honestly
  shared: my 15-line encoding could itself be wrong (wrong adjacency arith,
  wrong root rule) — but that text is the deliverable and is hand-checkable.
  **Level 2: argued, with the caveat that the grounder materialises the full
  reach relation — global, not cut-shaped.**
- **CNF/#SAT:** the *encoding's* failure modes are named and specific:
  unrolling depth < eccentricity (undercount), broken root-prefix chain
  (multiplicity error), cardinality-ladder bug. All are global-witness
  errors, disjoint from the three propositions. The *counter*, however,
  decomposes on separators of the CNF's primal graph, and its component
  cache across a width-H cut is bounded below by the number of frontier
  behaviours ([BCMS16], banked in `second-source:results/`
  `second-source-candidates-B.md` kill K5). That is a partition DP by
  another name — but with the crucial asymmetry the brief's ruling turns
  on: the decomposition is a *performance* mechanism whose correctness is
  problem-agnostic; the connectivity semantics live entirely in the
  clauses. A counter whose caching were wrong miscounts standard
  benchmarks, not specifically king animals. **Level 2: partially cleared —
  the run-time decision structure is frontier-shaped, the rule deciding
  connectivity is not.** Ranked below the Lean route accordingly.

## The formalisation (deliverable 1)

`experiments/tristruct/r3_l5_king_connected.lean` — the primary,
*evaluated* formalisation. One screen:

- `kingAdj p q` := p ≠ q ∧ Chebyshev distance ≤ 1 (four ℕ inequalities);
- `kingGraph s` := the `SimpleGraph` induced on a `Finset` of cells;
- `isAnimal H s` := touches column 0 ∧ touches row 0 ∧ touches row H−1 ∧
  `(kingGraph s).Connected`;
- `T n H` := card of the `isAnimal` filter over all n-subsets of the box
  [0,n) × [0,H).

"Up to translation" is encoded as min-x = 0, min-y = 0, max-y = H−1; the
domain box [0,n) × [0,H) loses nothing because a king-connected n-cell set
has width ≤ n (a king path from a min-x cell to a max-x cell changes x by at
most 1 per step, so every intermediate column is occupied — stated in the
file header; hand-checkable). Nothing in the file implements a connectivity
algorithm: the decision procedure is Mathlib's, `Connectivity/Finite.lean`
lines 56–65, community-written and reviewed.

Secondary formalisations of the same object, same normalization:

- `r3_l5_king.lp` — 15 lines of ASP; `clingo r3_l5_king.lp -c n=5 -c h=3
  -q 0` would print `Models : 248`. **clingo is not installed on gympie;
  MacPorts has it: `sudo port install clingo`.** Third-party evaluation is
  therefore NOT ESTABLISHED pending that install; the encoding text is the
  deliverable.
- `r3_l5_cnf_encode.py --emit n H` — DIMACS CNF whose *raw* model count
  equals T(n,H) (every auxiliary biconditionally defined, hence functionally
  determined: no projection support needed). The target-size instances are
  writable today: n=40 H=15 → 118,920 vars / 483,248 clauses; n=40 H=21 →
  167,160 vars / 682,244 clauses, emitted in seconds. **No exact #SAT
  counter exists on gympie or in MacPorts** (checked by `port search`:
  ganak, sharpsat, dsharp, cachet, gpmc, approxmc absent; the `c2d` port is
  an unrelated Apple II disk tool) — matching probe P1 on the
  `second-source` branch, which found all ten candidate binaries absent.
  A counter would have to be built from upstream source: jasonp's call,
  exactly as lane B's B2 flagged it in July.

## Validation at small n (deliverable 2)

- **Lean, third-party evaluation:** all 23 banked cells with n ≤ 7 that were
  attempted — every (n,H) for n ≤ 6 plus T(7,2), T(7,3) — reproduced
  exactly (`ALL BANKED VALUES REPRODUCED`,
  `experiments/tristruct/r3_l5_king_connected.log`). Theorem pins: LEAN_PINS.
- **CNF, semantic self-test (my own evaluation, labeled as such):** for all
  74,388 n-subsets over every (n,H) with n ≤ 5, the CNF's forced total
  assignment agrees with a BFS reference subset-by-subset, and the resulting
  counts match all 14 banked cells (`r3_l5_cnf_selftest.log`, 27 s). This
  certifies the encoding text is faithful; it is not a third-party count.
- **ASP:** validated by inspection only; NOT ESTABLISHED until clingo runs.

A formalisation disagreeing with the banked triangle at small n was the
lane's tripwire; none fired.

## Cost (deliverable 3) — the honest no

Three independent ways to price it, each anchored on something measured:

1. **The Lean route** enumerates the domain: cost ∝ Σ_H C(nH, n).
   Measured: LEAN_COST_MEASURED. At n = 40: log₁₀ C(600,40) = 62.6
   (H = 15), 68.6 (H = 21). Dead by ~57 orders of magnitude regardless of
   per-subset cost.
2. **Enumeration-based counting** (clingo `-q 0`, or any tool that visits
   models): cost ≥ number of models. The band sum is
   Σ_{H=15..21} T(40,H) ≈ 2.9 × 10³¹; at 10⁹ models/s that is
   9.1 × 10¹⁴ years. Dead from the banked magnitudes alone, before any
   grounding cost. Small-n solver constants are NOT ESTABLISHED (no
   clingo), and cannot change this verdict.
3. **Component-caching #SAT counters** — the only generic family that in
   principle beats model enumeration — are killed by the banked prior:
   `second-source` lane B's K5 cites [BCMS16] (dec-DNNF size across a
   width-H cut ≥ number of frontier behaviours), so the counter re-pays at
   least the production frontier's state budget *through CNF overhead*, for
   no reach. The same wall the brief states as the second entry ticket
   (χ ~ λ^(H/4), `results/boundary-push-tensornetwork.md`) — paid in the
   cache instead of the frontier.

**Modulo a small prime:** no help. Exact model counters count in bignum
integers; none of these tools has a mod-p mode, and the cost driver
(models visited / cache entries) is unchanged by reducing the answer.

**Verdict: does any such tool reach n = 40 at H = 15..21? No.** The
formalisation is the lane's value, exactly as the brief predicted: a
definition-level witness that the engines count what we say they count,
checkable by a referee in an afternoon (the skeptical reader can re-run the
Lean file at n ≤ 6 on a laptop; the standard's reader-cannot-rerun bar is
met at small n and unreachable at 40 by anything in this lane).

## Prior work (novelty greps, commands shown)

```
git log --all --oneline --name-only -- 'results/*.md' 'docs/*.md' 'docs/**/*.md'
  # 1538 path lines; includes the corrected top-level docs/*.md term
for b in $(git branch -a --format='%(refname:short)'); do
  git grep -il 'clingo\|answer set\|MiniZinc\|Courcelle\|MONA\|model count\|#SAT\|sharpSAT\|ganak\|d-DNNF\|Graphillion\|ZDD' \
    $b -- 'results/*.md' 'docs/*.md' 'docs/**/*.md'; done | sort -u
git show second-source:results/second-source-candidates-B.md   # read in full
git show second-source:results/second-source-candidates.md     # kill table
git show master:results/polyplet-zoo.md                        # kill line 70
```

Findings, and what is therefore *not* claimed as new here:

- **#SAT counters as a reach instrument: previously killed** (K5,
  `second-source:results/second-source-candidates-B.md`, with [BCMS16] and
  probe P1). Cited above, not re-derived; this lane adds the concrete
  encoding, its self-test, and the target-size instance measurements.
- **Certified knowledge compilation (d-DNNF + CPOG with the Lean-verified
  checker of Bryant–Nawrocki–Avigad–Heule, SAT 2023): previously proposed as
  B2** on the same branch — "cannot be killed cheaply", measurement plan
  gated on jasonp approving third-party code into `build/`. That is this
  lane's strongest phase-2 shape for *certainty* (tier-3 certificates on
  small cells, never reach), and the credit is lane B's. My CNF encoder is
  exactly the "definitional CNF generator" half of B2's trusted base.
- **ZDD/frontier libraries (Graphillion/TdZdd): previously killed** (K1:
  the mate array is the frontier partition — the incumbent's rule
  compressed). Pre-registered on my blind list with the same expectation;
  not pursued.
- **ASP** appears once in project history, in a kill-list line of
  `master:results/polyplet-zoo.md` ("#SAT/ASP/ZDD/... all separately
  killed, see this session's transcript") — a verdict banked without an
  artifact. The encoding here is the first ASP artifact in the repo; the
  kill verdict for *reach* is confirmed independently (cost item 2), so
  polyplet-zoo's line stands, now with evidence attached.
- **CP/MiniZinc, MSO/Courcelle (MONA, Sequoia, D-FLAT), and
  proof-assistant-as-counter appear nowhere in history** (greps above):
  the Lean formalisation route is new to the project. MiniZinc/Gecode are
  in MacPorts but were not pursued: solution *counting* there is
  enumeration-based, killed by cost item 2 identically to ASP; MSO tools
  decompose on tree/path decompositions, killed identically to cost item 3.
  Both were pre-registered (blind list items 2, 4) and are closed by
  argument + the enumeration bound rather than by measurement — marked so.

## NOT ESTABLISHED

- Third-party evaluation of the ASP encoding: needs `sudo port install
  clingo` (jasonp's call). One minute of laptop time at n ≤ 6 would
  establish it; the expected output for (5,3) is `Models : 248`.
- Third-party evaluation of the CNF encoding: needs an exact #SAT counter
  built from upstream source (none in MacPorts) — the same toolchain
  decision B2 already put on jasonp's desk in July.
- Small-n scaling constants of clingo/#SAT solvers on these encodings
  (blocked on the above). Neither can alter the reach verdict, which rests
  on model-count and cache lower bounds, not constants.
- The width ≤ n normalization argument and the translation-class bijection
  are stated in the Lean file's header as hand-checkable comments, not
  proved in Lean. Proving them in Lean (a `T n H = (translation classes)`
  theorem) is the natural hardening step if this formalisation is ever
  promoted to a cited artifact.

---

## Hardening addendum — restart agent, 2026-08-12 evening

The lane was restarted after the first L5 agent was terminated for launching
Lean jobs on gympie. Everything above stands unchanged. This addendum is the
interrupted hardening, done entirely at the desk under
`docs/r3-job-dispatch.md`: nothing below was compiled or executed.

### Process record: the killed runs and the truncated log

- The `LEAN_PINS` and `LEAN_COST_MEASURED` placeholders above are left
  unfilled deliberately. The runs that would have filled them were killed
  mid-flight by the lead on gympie; those numbers are UNMEASURED and are not
  reconstructed here.
- `experiments/tristruct/r3_l5_king_connected.log` is now **0 bytes**
  (mtime 19:04) — a killed relaunch truncated it after the deliverable was
  filed. The completed first run's verdict (all attempted banked cells
  reproduced, `ALL BANKED VALUES REPRODUCED`) stands as filed at the time;
  its **per-cell wall times are lost** and every timing derived from them
  below is flagged accordingly. Job L5-JOB-1 (end of this addendum)
  regenerates the log on a citable box.

### The two hand-checked claims, now written as Lean proofs

New file: `experiments/tristruct/r3_l5_normalization.lean` —
**WRITTEN BUT NOT COMPILED** (Lean is banned on gympie this round; the file
has never been elaborated). Check command, for ayr/dalby or any machine with
the pinned toolchain:

    cd <repo>/polyplets && ~/.elan/bin/lake env lean \
      ../experiments/tristruct/r3_l5_normalization.lean

Expected on success: no output, exit 0 (proofs only — no #eval, no pins).

The file re-states the plane objects honestly — `Finset (ℤ × ℤ)`, no box,
genuine translations, a real `Setoid` quotient — and carries a verbatim copy
of the original definitions (marked `BEGIN COPY`/`END COPY`, with the exact
`diff` command a referee runs to confirm the copy is byte-identical to
`r3_l5_king_connected.lean:30-62`).

**Claim 1 — width <= n (the domain box loses nothing).** Proved via a
discrete intermediate-value theorem along a king walk:

- `walk_hits_column` — the x-coordinate moves by at most 1 per step of a
  `SimpleGraph.Walk`, so every intermediate column is visited (induction on
  the walk; the case split is closed by `omega`);
- `width_lt_of_normalized` — if a cell had x >= n, columns 0..n would all be
  occupied — n+1 distinct columns from n cells, contradiction by
  `Finset.card_image_le`;
- `rows_of_normalized`, `normalized_in_box` — same for rows; packaged box
  membership;
- `mem_counted_iff_normalized_animal` — the sets `T n H` counts are EXACTLY
  the box shadows of normalized plane animals (both directions).

**Claim 2 — the translation-class bijection.** Proved as a transversal
argument:

- `existsUnique_normalizing_translate` — every plane animal has exactly one
  normalizing translate (existence via `Finset.exists_min_image`; uniqueness
  because normalization pins both minima);
- `T_eq_card_normalized` — T(n,H) = #(normalized plane animals), via an
  explicit `Equiv` built from `toZ`/`toN` round-trips;
- `T_eq_card_translationClasses` — **the headline**:
  `T n H = Nat.card (Quotient (animalSetoid n H))`, the number of
  translation classes of king-connected n-cell subsets of ℤ² with
  bounding-box height exactly H.

**Neither claim resisted.** Both are complete written proofs; no step is
missing, conditional, or hand-waved. What remains is mechanical compile risk,
enumerated in the file header as six named fragile points (identifier drift:
`SimpleGraph.connected_iff`, `add_neg_cancel`, `Int.toNat_natCast`; rcases on
a `Quotient`; `omega`'s diet — every projection-of-mk goal is pre-reduced by
an explicit `show` so omega only ever sees linear ℤ/ℕ arithmetic, `toNat`,
and casts; the `Setoid` is declared an instance so `Quotient.exact/sound`
resolve). Each has a stated local repair. A failed compile names one lemma;
it does not disturb the mathematics.

Design note a referee will ask about: connectivity in the plane definition is
again Mathlib's `SimpleGraph.Connected`; the only project-authored
connectivity content in the whole file is graph homomorphisms whose
adjacency-preservation obligations are closed by `omega`. The lane's level-1
story is preserved: the theorems relate two *definitions*, neither of which
implements a connectivity algorithm.

### Referee recipe (standalone — laptop, no project machines, no trust)

**Toolchain.** elan (the standard Lean version manager), toolchain
`leanprover/lean4:v4.31.0`, Mathlib at tag `v4.31.0` (commit
`fabf563a7c95a166b8d7b6efca11c8b4dc9d911f` — the pin in
`polyplets/lake-manifest.json`). Setup from nothing:

    # install elan (leanprover's installer), then:
    lake +leanprover/lean4:v4.31.0 new kingcheck math
    cd kingcheck
    # in lakefile.toml, set the mathlib require to rev = "v4.31.0"
    lake update
    lake exe cache get     # compiled mathlib; ~5-6 GB disk, ~10-20 min (ASSERTED)

**Run.**

    lake env lean /path/to/r3_l5_king_connected.lean

**Expected output.** 22 lines of the form

    T(5,3) = 248  banked 248  OK  [<t> ms]

(one per cell, all `OK`), then the line `ALL BANKED VALUES REPRODUCED`;
exit 0. The two `example ... := by native_decide` pins print nothing — their
success is the clean exit. **Wall clock:** minutes to tens of minutes for
everything through T(7,3) on a 2024 laptop — UNMEASURED (the measured log was
truncated; the completed run is bracketed under ~20 min on an M4 Pro by file
mtimes). The first `import Mathlib` costs 1-3 minutes of that (ASSERTED).

**What failure looks like.** Semantic failure: `MISMATCH` on a cell line and
a final `N MISMATCHES` (exit still 0 — the #eval table reports, the pins
gate). Environment failure: Lean errors mentioning unknown identifiers or
toolchain versions — wrong mathlib pin, not a result. Cost wall: a hang on a
large cell is the C(nH,n) growth, not a fault.

**RED controls — corrupt, run, watch it notice.** Three one-line
corruptions, one per trust surface:

1. *Data:* change `(5,3,248)` to `(5,3,249)` in the banked table. Expect
   `T(5,3) = 248  banked 249  MISMATCH` and `1 MISMATCHES`.
2. *Definition:* in `kingAdj`, change `p.2 ≤ q.2 + 1` to `p.2 ≤ q.2`
   (silently drops neighbours). Expect widespread `MISMATCH` — the counts
   move, the banked column does not.
3. *Pin:* change `example : T 6 4 = 1480` to `= 1481`. Expect a
   `native_decide` failure: nonzero exit, error naming the example.

**Trusted base**, stated once: Lean kernel + the Lean compiler
(`native_decide` / compiled `#eval`) + Mathlib's decidable-connectivity
instance (`Mathlib/Combinatorics/SimpleGraph/Connectivity/Finite.lean`),
community-written. Kernel-only `decide` is infeasible even at T(2,2)
(measured above: abandoned at 15 CPU-min / 5.8 GB).

**The hardening file** (`r3_l5_normalization.lean`): same invocation;
expected NO output and exit 0. Its RED: corrupt any theorem *statement*
(e.g. `H - 1` → `H - 2` in `rows_of_normalized`) and elaboration must fail.
Until job L5-JOB-1 is green this file is source, not a result.

### Reach, as a design answer

**The box cannot shrink.** Width ≤ n is *sharp*: a staircase animal attains
width n at every H ≤ n, so [0,n) × [0,H) is already the tight per-(n,H)
domain — there is no smaller box to buy. The 10^62.6 domain at (40,15) is
the tight figure, not a naive one, and no native_decide leaf changes it.
The strengthening that WOULD shrink cost is structured enumeration
(Redelmeier-style growth inside Lean) — which is project-authored
connectivity-adjacent code and forfeits the lane's premise. Not proposed.

**Largest definition-lockable n**, all-subsets evaluation, per-cell
`native_decide` leaves. Exact subset counts (the cost driver, machine-free):
row-n full lock is dominated by its largest cell C(nH,n):

| row | dominant cell | subsets | verdict |
|---|---|---|---|
| 6 | C(36,6) | 1.9e6 | done (completed run) |
| 7 | C(49,7) | 8.6e7 | ~30x the whole completed run — single-core hours to ~a day (EXTRAPOLATED from the mtime-bracket rate, which is itself UNMEASURED) |
| 8 | C(64,8) | 4.4e9 | ~1600x — fleet-days with per-cell parallelism (EXTRAPOLATED) |
| 9 | C(81,9) | 2.6e11 | ~60x row 8 — fleet-months; out |
| 40 | C(600,40) | 10^62.6 | out by ~57 orders; the band is untouchable by this artifact, full stop |

Expected ceiling: **full-row definition lock at n = 8, n = 9 out**, versus
the four-enumerator crosscheck at n ≤ 12. Whether extending the witness from
n = 6/7 toward 8 is worth fleet-days is jasonp's trade; per the standard's
ranking (checker cost first, reach not a criterion) the value density is at
SMALL n, so this addendum does not request that run — only the compile job
below, whose rerun step yields the first MEASURED subsets/s anchor and would
firm this table for free.

### JOB REQUEST

    job id:            L5-JOB-1
    measures:          (a) elaboration verdict of r3_l5_normalization.lean —
                       claims 1+2 compile clean, or the failing lemma named;
                       (b) fresh r3_l5_king_connected.lean run: banked-value
                       verdict + per-cell walls on a citable box (replaces
                       the truncated log); (c) RED-mutant verdict
    decides:           whether the deliverable's two hand-checked claims are
                       reported as COMPILED THEOREMS (upgrading synthesis
                       ledger item 4's normalization caveat) or as written
                       source plus a repair list; also converts the reach
                       table's rate from mtime-bracket to MEASURED
    command:           sh experiments/tristruct/r3_l5_lean_check.sh <repo>
    script:            experiments/tristruct/r3_l5_lean_check.sh (written,
                       fail-closed: empty-log gate, banked-line grep, RED
                       mutant must print '1 MISMATCHES')
    wall estimate:     step 1: 5-15 min ASSERTED (import-dominated; fails
                       fast on a broken tactic). step 2: <= 1 h EXTRAPOLATED
                       from the gympie mtime bracket (~20 min there,
                       2.8e6 subsets). step 3 ~ step 2. Total <= 2.5 h.
    RAM estimate:      <= 8 GB peak ASSERTED (kernel-decide experiment
                       measured 5.8 GB; ordinary elaboration sits lower)
    disk estimate:     logs ~KB. If the target lacks the mathlib cache:
                       one-time `lake exe cache get`, ~5-6 GB ASSERTED.
                       Note elan + v4.31.0 toolchain must exist on the
                       target (user-level install, no sudo); unverified on
                       ayr/dalby.
    cores:             1 (single-file elaboration)
    interruptible:     yes — stateless, rerunnable, nothing lost on kill
    RED control:       in-script: mutated banked constant (5,3,248)->(5,3,249)
                       must yield exactly '1 MISMATCHES' (grep fail-closed);
                       gate A fails on ANY elaborator output
    closes:            NOT ESTABLISHED item "width <= n normalization and
                       translation-class bijection ... not proved in Lean"
                       (source written; compile pending this job), and the
                       truncated-log gap recorded above

### Queue rows filed today

L5-6 (JOB-REQUESTED, this job), L5-7 (reach-design fact). See
`results/triangle-r3-queue.md`.
