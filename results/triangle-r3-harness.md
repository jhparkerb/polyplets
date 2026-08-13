# Round-3 harness pack — prior-work index, row-40 exposure re-measured, what the engines share

2026-08-12. Harness deliverable for `docs/triangle-round3-brief.md`, scored
under `docs/skeptical-reader-standard.md`. Everything below is measured from
the working tree, the git history, or the banked file — nothing is recalled
from memory or copied from another brief's summary. This file proposes no
routes and evaluates no lane.

Throwaway script: `experiments/tristruct/r3_harness_exposure.py` (Part 2).

---

## PART 1 — Mechanical prior-work index

### Commands run

```
ls results/*.md ; find docs -name '*.md'          # working tree
git log --all --oneline --name-only -- 'results/*.md' 'docs/**/*.md'
git log --all --oneline --name-only -- 'docs/*.md'   # supplement, see below
git show <last-commit>:<path>                      # title of each off-tree hit
git show <last-commit>^:<path>                     # fallback when <last-commit> is the deletion
```

**Process finding (mechanical, before any table):** the standard's prescribed
pathspec `'docs/**/*.md'` does NOT match top-level `docs/*.md` files in git's
default pathspec matching — the `**` needs an intermediate `/`. The
supplementary `'docs/*.md'` sweep found **30 additional historical files**,
including `docs/second-source-team-brief.md` — the very file the standard
cites by commit (`2b3115b`). Any lane running only the prescribed command
will miss the second-source brief and its critique. (`'results/*.md'` has the
opposite behaviour: it also matches `results/<dir>/<file>.md`, which is why
subdirectory PROVENANCE/RESULT files appear below.)

Flag legend (relevance to round 3): **IND** = independent-determination
attempt or artifact; **CONN** = connectivity-rule discussion;
**TECH** = enumeration technology; **CLOSED** = closed door named by the
brief or by the file's own verdict; **—** = not relevant to this round.
Lane pointers (L1..L6) added where a title matches a lane's named inputs.
Subjects are the files' own `#` titles, trimmed.

### A. On-branch `results/*.md` (working tree, `triangle-structure`)

| path | subject (file's own title) | flag |
|---|---|---|
| results/a34-utilization-postmortem.md | a(34) core-utilization postmortem | — |
| results/allpairs-kernel.md | K1: all-pairs weight constant via the gap walk | — |
| results/anisotropic-not-dfinite.md | height-anisotropic GF: quantified non-D-finiteness | CLOSED |
| results/band-structure-probes.md | three structural probes of the uncovered middle band (all NEGATIVE) | CLOSED |
| results/beyond-polyplets.md | what this repo's machinery can be pointed at | — |
| results/boundary-push-recurrence.md | intrinsic complexity of the T(n,H) slicings | CLOSED |
| results/boundary-push-tensornetwork.md | can an MPS compress the frontier? (measured wall; brief cites) | CLOSED |
| results/bridge-credit-closed.md | band-decomposition route to a lambda upper bound is closed | — |
| results/completion-oracle.md | completion-prune headroom vs true optimum | TECH |
| results/completion-pruning-audit.md | completion-pruning audit | TECH |
| results/component-stratification.md | component-count stratification of polyplets | TECH, L1 |
| results/concatenation-upper-bound.md | concatenation route to lambda upper bound closed | — |
| results/converse-sweep.md | exact counterexample hunts for open universal claims | — |
| results/convex-anisotropic.md | haruspicy on convex polyplets by area | — |
| results/convex-polyplets.md | convex polyplets (see docs/proofs/convex-mirage.md) | — |
| results/countable-subpopulations-criterion.md | when is a sub-population countable (not just enumerable)? | TECH |
| results/crt-counter-shaping.md | shaping CRT-based counting: prime size & counter width | TECH |
| results/dalby-perf-audit.md | dalby performance audit | — |
| results/defect-gas.md | defect gas: mechanism of the diagonal cumulant law | CLOSED, L2 |
| results/depth-tower-bivariate-dead-end.md | bivariate depth GF: no closed form | CLOSED |
| results/diagonal-closed-forms.md | anti-diagonal closed forms (P_k) | TECH |
| results/diagonal-law-below-onset.md | diagonal law below onset: exactness stops | CLOSED |
| results/directed-cone-anchor.md | enumerate+filter pipeline against a closed form | IND |
| results/directed-king-animals.md | directed & multi-directed king animals | — |
| results/discarded-term.md | the discarded term, identified | — |
| results/dm-diagonal-recon.md | toward proving the dm-mirror diagonal law | — |
| results/dmirror-diagonals.md | dmirror strip diagonals are quasi-polynomial | — |
| results/fanin-tax.md | dalby paying ~75% of worker CPU to open files | — |
| results/finite-lattice-crossover.md | finite-lattice method crossover (NEGATIVE: does not stack) | CLOSED, TECH |
| results/gf-head-check.md | banked fixed-height GFs vs the exact triangle | TECH |
| results/height-distribution-collapse.md | universal limit shape of the height distribution | — |
| results/hex-diagonal-law.md | diagonal law is universal: polyhexes | — |
| results/hole-fill-interior-cell-identity.md | hole-fill / interior-cell identity | TECH, L3 |
| results/hole-free-growth-constant.md | hole-free growth constant λ₀ | TECH, L3 |
| results/hv-growth-sandwich.md | (dir4, HV-convex) growth constant, proved | — |
| results/isotropic-dfinite-boxes.md | A006770 P-recurrence and algebraic exclusion boxes | CLOSED |
| results/joint-box-probe.md | joint box table B(n,W,H) probe | — |
| results/k8-pinning.md | pinning the k=8 height-diagonal | — |
| results/king-subfamilies.md | solvable-subfamily sweep of the king lattice | TECH |
| results/kink-carry-optionA-barrier-overhead.md | kink-carry option A barrier overhead | — |
| results/kink-carry-optionA-volume.md | kink-carry option A merge-barrier volume | — |
| results/kink-carry-shard-duplication.md | kink-carry shard duplication curve | — |
| results/kink-carry.md | cell-at-a-time king TM beats whole-column | TECH, CONN |
| results/kink-resume-sigterm-bug.md | kink resume bug (FIXED) | — |
| results/map-body-profile.md | where the enumeration CPU goes | — |
| results/map-profile.md | map profile (Quarry Survey) | — |
| results/matching-pair-convention.md | matching-pair convention, pinned | — |
| results/maxhole-proof.md | toward M(n) proof | — |
| results/merge-ledger.md | merge ledger results | — |
| results/middle-kingdom-grid.md | Middle Kingdom classification grid | TECH |
| results/middle-kingdom-phase3.md | Middle Kingdom empty grid cells | TECH |
| results/middle-kingdom.md | poly-time tier of king-animal subclasses | TECH |
| results/min-site-perimeter.md | minimum site perimeter | — |
| results/mk-dir4-perimeter.md | (dir4, HV-convex) by semiperimeter | — |
| results/move-graph-connectivity.md | single-cell-move graph is connected n<=10 | — |
| results/multi-directed.md | multi-directed king animals, Bacher's definition | — |
| results/notary-depth1-lean.md | depth-1 closure in Lean | — |
| results/novelty-sortie.md | sortie novelty sweep | — |
| results/nu-exponent.md | where a(n)'s mass sits + extent exponent | — |
| results/oeis-candidates.md | OEIS candidates, staged | — |
| results/onset-defect-crossover.md | near-onset layer width | CLOSED |
| results/onset-defect-depth1-closed.md | depth-1 defect closed | CLOSED |
| results/onset-defect-depths234.md | depths 2,3,4 closed | CLOSED |
| results/onset-defect-law.md | diagonal law's error term | CLOSED |
| results/open-conjectures.md | open conjectures & theorems-to-prove | — |
| results/overcommit-hydra.md | four a(40) OOM deaths in one day | — |
| results/overlap-kink-design-sketch.md | overlap + kink steal fix sketch | — |
| results/percell-mod4.md | per-cell mod 4: the algebra, checked on 528 cells | IND, CONN, L4 |
| results/perf-outcomes.md | engine performance pass outcomes | — |
| results/perimeter-both-ends.md | both ends of the perimeter table | — |
| results/perimeter-defect-diagonals.md | perimeter grading quasi-polynomial | — |
| results/polyiamond-diagonal-law.md | diagonal law on polyiamonds | — |
| results/polyplet-zoo.md | polyplet zoo | — |
| results/production-matrix-probe.md | Riordan / Stieltjes test, run for real | CLOSED |
| results/related-seqs-n24.md / -n32.md / -n33.md | related sequences extensions | — |
| results/resource-asks.md | what a small breakthrough would cost | — |
| results/rook-bishop-edge-distribution.md | rook/diagonal edge-count distribution (RETIRED) | — |
| results/scheduling.md | scheduling / utilization outcomes | — |
| results/second-wind.md | a(37) feasibility push | — |
| results/series-analysis-da.md | differential-approximant series analysis | — |
| results/severance-w1-anchor-cut.md | P_k ab initio for k<=9 | TECH |
| results/slope-growth-saddle.md | slope-s slice growth constants | — |
| results/slope-slicings.md | slope-s slicings: no law off the diagonal (NEGATIVE) | CLOSED |
| results/steal-tail-h18.md | H18 map straggler tail | — |
| results/stretched-exponential-test.md | no stretched exponential | — |
| results/strip-engine.md | independent strip TM engine — second source for T(n,H) | IND, CONN |
| results/strip-growth-lambda-bounds.md | mu_H rigorous lower-bound ladder | TECH |
| results/strip-mu-certificates.md | certified mu_H exact rational bounds | TECH |
| results/strip-mu-engine-resumption.md | mu_H engine resumption dossier | — |
| results/strip-mu-fast.md | indexed-array strip engine | TECH |
| results/strip-spectrum-defect-rate.md | defect rate not in the strip spectrum (NEGATIVE) | CLOSED |
| results/sub-record-interrupt-design.md | sub-record interrupt (WRONG TARGET) | — |
| results/subgroup-mod4.md | subgroup census: a(n) mod 4, parity bit on every cell | IND, L4 |
| results/terminal-velocity.md | g2 kernel shakeout ledger | TECH |
| results/ternary-spine.md | closed-form mod-3 law for the height triangle | TECH |
| results/triangle-combinations.md | alternative slicings and combinations | CLOSED |
| results/triangle-hunt-atoms-ab-initio.md | strip atoms computed ab initio | CLOSED (round 1) |
| results/triangle-hunt-congruence.md | round-1 proposer 2 summary | CLOSED (round 1) |
| results/triangle-hunt-cross-lattice.md | cross-lattice falsification verdicts | CLOSED (round 1) |
| results/triangle-hunt-enumerator-crosscheck.md | four independent enumerators reproduce the triangle (n<=12) | IND |
| results/triangle-hunt-klein-parity.md | proved forced parity T(n,H) even for n odd, H even | CLOSED (round 1) |
| results/triangle-hunt-proof-first.md | round-1 proof-first summary | CLOSED (round 1) |
| results/triangle-hunt-refutation-*.md (4 files) | round-1 refuter verdicts | CLOSED (round 1) |
| results/triangle-hunt-slices.md | round-1 slice recurrences | CLOSED (round 1) |
| results/triangle-hunt-sym-diagonals.md | symmetry-refined triangle I(n,H) structure | L4 |
| results/triangle-hunt-synthesis.md | round-1 synthesis and ranked verdict | CLOSED (round 1) |
| results/triangle-r2-d3-audit.md | adversary audit of the d=3 proof | CLOSED (round 2) |
| results/triangle-r2-d3-proof.md | d=3 sleeve unit formula proved | CLOSED (round 2) |
| results/triangle-r2-extension-scout.md | what the tower method reaches past d=7 | CLOSED (round 2) |
| results/triangle-r2-tower-mod81.md | mod-81 master equation | CLOSED (round 2) |
| results/triangle-snf.md | Smith normal form is all 3-powers | TECH |
| results/triangle-structure.md | Atom Ledger: dependency structure of T(n,H) | TECH |
| results/unexplored-avenues.md | IDEAS ONLY, nothing banked | — |
| results/utilization-fix-and-ceiling.md | utilization ceiling | — |
| results/v5-denominator-law.md | v5 denominator law, proved | — |

Subdirectory files matched by `'results/*.md'`:

| path | subject | flag |
|---|---|---|
| results/ns_a20..ns_a40/PROVENANCE.md (21 files) | per-term run provenance; ns_a40 = the banked a(40) run | IND-context |
| results/ns_a23/, ns_a24/, ns_a25/RESULT.md | per-term results | — |
| results/redelmeier_row20/RESULT.md | whole-row Redelmeier confirmation n<=20 (build/g2, 0 mismatch) | IND |
| results/redelmeier_row22/PROVENANCE.md | whole-row Redelmeier confirmation, frontier 20→22 | IND |
| results/dalby-run-telemetry-202606/README.md | run telemetry | — |

### B. On-branch `docs/**/*.md` (working tree)

| path | subject | flag |
|---|---|---|
| docs/skeptical-reader-standard.md | the scoring standard (this round's) | standard |
| docs/triangle-round3-brief.md | this round's brief | brief |
| docs/triangle-structure-team-brief.md | round-1 brief | CLOSED (round 1) |
| docs/triangle-structure-round2-brief.md | round-2 brief | CLOSED (round 2) |
| docs/triangle-structure-d9-d12-plan.md | tower d=9..12 plan (shelved by the R3 brief) | CLOSED |
| docs/redelmeier-tall-plan.md | plan: height-restricted Redelmeier for independent T(n,H) confirmation | IND, CONN |
| docs/provenance-tables.md | warrant tiers, three papers | standard |
| docs/certificate-squeeze-plan.md | Bui's full multi-type + certificate machinery | TECH, IND |
| docs/engine-design.md | production polyplet enumerator design | CONN, TECH |
| docs/formats.md | data formats | TECH |
| docs/dmirror-design.md | dmirror TM design (last symtm mode) | L4 |
| docs/observability.md | observability & provenance | — |
| docs/engineering-standards.md | catching regressions fast | — |
| docs/glossary.md | glossary | — |
| docs/job-checklist.md | job-start checklist | — |
| docs/lessons-learned.md | project lessons | — |
| docs/leiden-declaration.md | cached declaration copy | — |
| docs/oeis-ai-policy.md | OEIS policy notes | — |
| docs/onset-defect-*.md (3 files) | defect campaign handoff/plans | CLOSED |
| docs/severance-w4-scoping.md | W4 scoping | CLOSED |
| docs/middle-kingdom-plan.md, -followups-plan.md | poly-time tier campaign | TECH |
| docs/open-problem-lambda-bracket.md | connectivity wall on λ's upper bound | CONN |
| docs/lean-*.md (5 files) | Lean environment/artifact/audit/briefs | — |
| docs/notary-*.md (5 files) | Notary Lean campaign | — |
| docs/paper1-engine-chapter.md, paper1-reproducibility.md | paper source material | — |
| docs/publication-split.md | which papers are whose | — |
| docs/sortie-publication-plan.md | publication push | — |
| docs/perimeter-*.md (2 files) | perimeter campaigns | — |
| docs/a35-two-media-plan.md | a(35) two-media plan | — |
| docs/even-keel-*.md (3), full-utilization-redesign.md, utilization-bottleneck-log.md, terminal-velocity-plan.md | engine utilization plans | — |
| docs/drill1-counting.md, drill2-tiers.md | counting arguments; tiers and validation architecture | TECH |
| docs/viva-exam.md, viva-state.md, viva-reserve.md | LOCAL-ONLY viva files (viva-reserve.md unreadable: permission denied) | — |
| docs/proofs/diagonal-law.md | diagonal law is a theorem | CLOSED |
| docs/proofs/universal-diagonal-law.md | universal diagonal law | CLOSED |
| docs/proofs/T-n-nm1.md, T-n-nm2-and-general.md | height-diagonal proofs | TECH |
| docs/proofs/grand-form.md | grand form theorem | — |
| docs/proofs/convex-mirage.md, dm-diagonal-law.md, polyplet-upper-bound.md | other proofs | — |
| docs/reviews/outworks-adversarial.md | Outworks Lean audit | — |
| docs/reviews/l-trim/* (17 files), docs/reviews/llm-tics/* (6 files) | paper-trim and tic reviews | — |

### C. Off-branch / deleted files (the cross-branch sweep's whole point)

Live only in history or on another branch. `git show <commit>:<path>` to read.

**Branch `second-source` (not merged; tip includes 2b3115b, 8051fef, a6b8f6a, 5793ddf, 95685b8, 6e48c5d) — the round-1 process finding was that files from this line were cited but unread; every R3 lane should know these exist:**

| path | subject | flag |
|---|---|---|
| docs/second-source-team-brief.md | a genuinely independent second count of T(n,H) — the ruling the R3 brief quotes | CONN, IND |
| docs/second-source-brief-critique.md | critique of the "second algorithm" brief | CONN |
| docs/scaling-exploration-brief.md | scaling, not speed: exploration brief | — |
| results/second-source-candidates.md | merged findings of the three-lane sweep | IND, CONN |
| results/second-source-candidates-A.md | lane A: enumeration & statistical mechanics | IND |
| results/second-source-candidates-B.md | lane B: model counting / parameterised algorithms | IND, L5 |
| results/second-source-candidates-C.md | lane C: the coverage map | IND |
| results/second-source-and-scaling-onepager.md | one-pager | IND |
| results/king-column-motzkin.md | king column TM has Motzkin(H+1)−1 states | CONN, TECH |
| results/mertens-1990-perimeter-crosscheck.md | external definition anchors: Mertens 1990 + OEIS A286139 | IND |
| results/scaling-exploration.md, -A, -B, -C | scaling exploration lanes + merge | TECH |

**Other explore/perf branches (alive at their tips):**

| path | branch | subject | flag |
|---|---|---|---|
| docs/diamond-optimality.md | explore/theorem-diamond | max-hole optimum theorem | — |
| docs/hole-gf-order-law.md | explore/conjecture-hole-order | k-hole GF order law | — |
| docs/lambda-bound.md | explore/theorem-lambda-bound | rigorous λ upper bound | — |
| docs/symmetry-maxhole.md | explore/theorem-sym-maxhole | maxhole by symmetry | — |
| docs/t1-general-case.md | explore/theorem-t1-irreducibility | N_H irreducibility | — |
| docs/total-hole-area.md | explore/theorem-multihole | total enclosed area | — |
| docs/out-of-core-phase4.md | explore/reach-blocked-store | out-of-core column sweep | — |
| docs/ranged-row-r2.md | explore/reach-ranged-row | ranged counts-row | — |
| docs/perf/windowed-row.md | perf/windowed-counts-row | windowed counts-row | — |
| results/knight-animals.md | explore/seq-knight | polyknights counts | — |

**Deleted from master history (titles from the pre-deletion commit):** the
bulk are engine/perf docs deleted in the 78602f8 spring clean
(docs/frontier/* 18 files, docs/next-system/* 17 files, docs/perf/* 3 files,
docs/a2x launch/forecast plans 11 files, docs/layout.md,
docs/scheduling-design.md, docs/state-store-compression.md,
docs/spring-clean-deferred.md, docs/research-log-2026-06-22.md,
docs/new-directions-2026-06-22.md) and early results deleted in 91bdcdc
(complexity, fixed_height_gf, growth_analysis, growth-and-structure, holes,
lambda-bounds-timeline, lambda0-verification, lifetime3-proof,
modp_recover_profile, perimeter, reach_projection, sample_stats,
scaling_study, scaling, shelf, tma_state_growth, related-seqs-n23 in
ce45983). Flagged — except:

| path | deleted in | subject | flag |
|---|---|---|---|
| docs/confirmation-status.md | 78602f8 | A006770 confirmation status (no-gaps audit 2026-06-29) | IND-context |
| docs/s2-symmetric-enumerator.md | 78602f8 | the efficient symmetric enumerator (symcount origin) | L4 |
| docs/frontier/06-continuous-verification.md | 78602f8 | verification as a continuous parallel pipeline | TECH |
| docs/frontier/07-gf-recovery-notch-modp.md | 78602f8 | GF-recovery for notch columns via mod-p | TECH |
| results/complexity.md | 91bdcdc | Redelmeier generation vs column transfer matrix | TECH |
| results/mutation_testing.md | 91bdcdc | fault-injection / mutation testing of the cross-checks | TECH |
| results/site_perimeter.md | 91bdcdc | site-perimeter — FIRST cross-SOURCE validation | IND-context |

---

## PART 2 — Row-40 exposure, re-measured from the banked file

Recomputed 2026-08-12 by `experiments/tristruct/r3_harness_exposure.py` via
`Triangle.load()` (full load-time validation passed: per-height files
complete, row-sum identity a(n) = Σ_H T(n,H) for all n, structural zeros,
anchors T(40,40)=3^39 and T(40,39)=955·3^36). Exact integer arithmetic; the
loader re-verified Σ_H T(40,H) == a(40).

a(40) = 56749893611764175164545926946127

| band | exact sum of T(40,H) | share (4 dp) |
|---|---|---|
| H ≤ 2 | 1746860020068408 | 0.0000% (exact: 1746860020068408/a(40) ≈ 3.08e-15 %) |
| H = 3..14 | 25543501899880260848936969967574 | 45.0107% |
| H = 15..19 | 24880953615663697394106156499679 | 43.8432% |
| H = 15..21 | 28854180854910456675604906033933 | 50.8445% |
| H ≥ 22 | 2352210856973455893144030876212 | 4.1449% |
| (H ≤ 14, for reference) | 25543501899880262595796990035982 | 45.0107% |

All shares are exact rationals over a(40); numerators above are the exact
band sums.

**Check against `docs/skeptical-reader-standard.md` (45.01 / 50.84 / 43.84 /
4.14 / <0.01): all five still hold.** No drift; the brief's numbers stand.

Per-cell, n = 40, H = 15..21, provenance string quoted from
`tri.provenance(40,H)`:

| H | T(40,H) exact | share | provenance (loader) |
|---|---|---|---|
| 15 | 6374412577120147022430261962743 | 11.2325% | `'real-sweep'` |
| 16 | 5908452097354911220916654388822 | 10.4114% | `'real-sweep'` |
| 17 | 5140790021321717364748374654418 | 9.0587% | `'real-sweep'` |
| 18 | 4209726451267585301668763319533 | 7.4180% | `'real-sweep'` |
| 19 | 3247572468599336484342102174163 | 5.7226% | `'real-sweep'` |
| 20 | 2359769260803281210360136128699 | 4.1582% | `'real-sweep'` |
| 21 | 1613457978443478071138613405555 | 2.8431% | `'real-sweep'` |

Caveat every lane should carry: the loader's `provenance()` is a wired
classification by H (`experiments/tristruct/triangle.py:53-58` — H in 3..21 →
`"real-sweep"`, H ≥ 22 → `"closed-form-Pk"`, else `"closed-form-lowstrip"`),
documented from `results/ns_a40/PROVENANCE.md` ("Real sweeps H3-H21;
H22-H40 via wired P_k closed forms"; H21 "the tallest real sweep of the
whole project", 36.4 h). It is the banked run's declared provenance, not an
independent audit of it.

---

## PART 3 — What the production engines actually share

Terminology, fixed from the code so every lane means the same thing:

- **The production engine** is the ns system: Go orchestrator
  (`orchestrator/sweep.go`) driving C++ kernels. It has **two kernels**:
  the **kink-carry kernel** (`core/kink.h`, `core/kink_column.h`) — the
  production kernel — and the **whole-column kernel**
  (`core/mapreduce.h` + `core/transition.h`) — "the independent whole-column
  reference kernel kept as the correctness oracle"
  (`orchestrator/sweep.go:354-358`). The banked a(40) was swept by the kink
  kernel: `scripts/dalby_term.sh:2` ("compute a(N) dalby-solo on the kink
  kernel"), `--kernel kink` at `scripts/dalby_term.sh:235` (all three phases
  route through `run_phase`), and the same flag is present in the at-run
  revisions (`git show 38956525:scripts/dalby_term.sh`,
  `git show 801afd59:scripts/dalby_term.sh`, 2 hits each).
- **The second source** is the strip transfer-matrix engine
  (`cpp/strip_tm.cpp`), independently written, H ≤ 14 at n ≤ 40, 469 cells,
  0 mismatch (`results/strip-engine.md`). The second-source ruling
  (`git show 2b3115b:docs/second-source-team-brief.md`) holds it to be a
  consistency check, not verification, because its rule is the same class.
- H ≤ 2 rows are never swept at all: analytic closed forms in
  `orchestrator/sweep.go:1944` (`lowHeightRow`, H=1 and H=2 only).

### Where king-adjacency is defined

- **Whole-column kernel:** `core/transition.h:49-56`. Within the new column,
  vertical adjacency `r ~ r+1` (line 51); across the cut, a new cell at row
  r unions with old-column labels at rows `rr = r-1, r, r+1` (lines 52-56).
  The 3-row stencil IS the king-adjacency definition across the cut (edge or
  corner: W, NW, SW).
- **Kink-carry kernel:** `core/kink.h:114-117`. One cell placed per stage;
  its neighbours are N (new cell at r−1, line 114), W (old cell at r,
  pre-overwrite, line 115), NW (the carried overwritten cell, `s.b[H+2]`,
  line 116), SW (old cell at r+1, line 117). Same stencil, cell-at-a-time,
  with the NW cell explicitly carried because the sweep overwrote it.
- **Strip engine:** `cpp/strip_tm.cpp:92-111`. Vertical unions among new
  cells (93-96); cross-column unions over `rr = r-1, r, r+1` (100-110).
  Independently written, same stencil.
- **symcount_fast:** `cpp/sym/symcount_fast.cpp:329-330` — explicit offset
  tables `KDX[8]={1,1,1,0,0,-1,-1,-1}`, `KDY[8]={1,0,-1,1,-1,1,0,-1}`; used
  to build the orbit-graph adjacency (187-193) and in the connectivity BFS
  (218-219).
- **g2 Redelmeier** (`cpp/g2_redelmeier.cpp:35-41`, offset table `kSquare8`):
  the oracle `core/transition.h:14` names for gate validation. Included for
  completeness: it enumerates connected animals by rooted growth and never
  evaluates connectivity as a predicate.

### How connectivity is decided, engine by engine

**Whole-column kernel** (`core/transition.h` `stepColumnSquare8`, driven by
`core/mapreduce.h` `map_shard`):

- Frontier state: `Sig` = one byte per row of the current boundary column,
  b[r] = component label (0 = empty), plus touch-top b[H] and touch-bottom
  b[H+1] flags (`transition.h:68-74`); ranged count-vector per state
  (`RunRecord`).
- Union-find: `s8::find`/`s8::unite` (`transition.h:24-31`), slots = new
  rows 0..H−1 and old labels H+L (`transition.h:44-48`); unions per the
  stencil above.
- Old-vs-new comparison: an old component whose root gains no new cell is
  **stranded** → `Outcome::Dead`, the state is discarded
  (`transition.h:59-65`). The mask generator `forEachViableMask` pre-prunes
  exactly the stranded masks but "step() still re-checks, so it stays the
  authority" (`transition.h:78-85`).
- Completion: at column start, `Classifier::complete` (`core/mapreduce.h:73`)
  accepts a state iff its labels form **exactly one component** and both
  touch flags are set (`core/classifier.h:44-48`); its counts then flow into
  the T(n,H) row.

**Kink-carry kernel** (`core/kink.h`, `core/kink_column.h`):

- Frontier state: mixed-state `Sig`, keyLen H+4 — b[0..H) mixed
  new/old-column labels, touch flags b[H], b[H+1], **carry byte b[H+2]**
  (the overwritten NW cell's label), placed-any bit b[H+3]
  (`kink.h:9-18`).
- Union-find: the SAME `s8::find` from `core/transition.h` (included at
  `kink.h:51`; used at `kink.h:110,120,123-124`), run per stage over the
  new cell's N/W/NW/SW neighbour labels.
- Stranding: when the carry drops off, its component must still appear in
  the boundary or the new carry, else the state dies
  (`kink.h:138-140` via `labelInMixedState`, `kink.h:79-83`); re-checked at
  column finalize (`kink_column.h:88-92`).
- Completion: harvest happens at column START in `kinkSeedStage0`
  (`kink_column.h:46-52`), calling the same `Classifier::complete` — i.e.
  the same one-component + both-touch-flags predicate
  (`core/classifier.h:44-48`).

**Strip engine** (`cpp/strip_tm.cpp`):

- Frontier state: one packed u64, 4 bits per row = component label
  (`strip_tm.cpp:12-14,70`).
- Union-find: its own local implementation (`strip_tm.cpp:79-85`), tokens =
  new rows 0..H−1 and prev labels H+1..H+8 (line 78).
- Old-vs-new comparison: counts distinct previous labels, tracks which are
  touched by a new cell; `if (ntouch < nprev) return false; // a component
  was buried` (`strip_tm.cpp:87-112`).
- Completion: a state is closable iff its labels form exactly one component
  (`strip_tm.cpp:140-143`); T(n,H) recovered by the exact second difference
  in H (`strip_tm.cpp:6-9`), not touch flags.

**symtm** (`cpp/sym/symtm.cpp` — symmetry-refined triangle inputs
`I_H(⟨h⟩)`, `I_H(⟨v⟩)`, `I_H(C2)` via `--byheight`):

- Holds a strip frontier: `DB = unordered_map<Sig, vector<u64>>`
  (`symtm.cpp:86`), and calls the shared `stepColumnSquare8` itself
  (`#include "core/transition.h"` at `symtm.cpp:71`; calls at
  `symtm.cpp:255` and `symtm.cpp:579`, instantiated at u64 masks,
  POLY_SIGMAX=70). Completion = `closable()`: exactly one label plus both
  touch flags (`symtm.cpp:87-92`). **symtm is inside the shared rule class
  by literal shared source.**

**symcount_fast** (`cpp/sym/symcount_fast.cpp` — the mod-2 route's
`I_H(D2ax)`):

- No frontier, no labels, no union-find. Redelmeier-style DFS over the
  ORBIT GRAPH (nodes = orbits of cells under the symmetry group,
  header lines 4-10; orbit construction 146-175; orbit adjacency 179-194).
- Connectivity is decided per emitted candidate by a **BFS over the lifted
  cell set** using the KDX/KDY stencil, accepting iff every present cell is
  reached from the first (`symcount_fast.cpp:197-228`, `reachedCnt == n` at
  line 227).
- `results/percell-mod4.md:88-91` ("symtm holds a strip frontier;
  symcount_fast is a DFS over a quotient domain — 3.9 GB here against 4.6 MB
  there") is **verified against the code**. The two do share the KDX/KDY-vs-
  stencil notion of king adjacency; they share no connectivity mechanism.

### Genuinely common vs merely looks common

Literally shared source:

- `core/transition.h` is compiled into the whole-column kernel
  (`core/mapreduce.h:85`), the kink kernel (`core/kink.h:51` include;
  `s8::find` reuse), symtm (`symtm.cpp:71,255,579`), and the older tma
  sweeps (`cpp/tma/*.h`) and strip_mu tools (`cpp/strip_mu8.cpp`). One
  header, one union-find, one stranding rule, one 3-row stencil.
- `core/classifier.h`'s completion predicate serves both production kernels
  (`mapreduce.h:73`, `kink_column.h:52`).
- The kink kernel is NOT an independent recount of the column kernel:
  different boundary granularity, same primitive ops, same authority header.

Shared algorithm without shared source:

- `cpp/strip_tm.cpp` re-implements the identical rule schema — union-find of
  new cells against previous-column labels, 3-row cross-cut stencil,
  buried-component death, one-component closability — with zero shared
  lines. Its header says so itself: "shares no enumeration with the kink
  NW-carry kernel" (`strip_tm.cpp:16-17`), which is true at the source level
  and is exactly what the 2b3115b ruling says is insufficient.

Shared assumption only (weakest tier):

- symcount_fast and g2 share the 8-neighbour adjacency definition (offset
  tables) with everything above, and nothing else: no frontier, no labels,
  no cut. g2-based whole-row Redelmeier confirmations exist for n ≤ 22
  (`results/redelmeier_row20/RESULT.md`, `results/redelmeier_row22/PROVENANCE.md`);
  symcount_fast reaches row 40 only on the symmetry-refined counts (mod-2
  route, `results/subgroup-mod4.md`).

### The hypothesised shared misconception, stated precisely

For the banked H=15..21 cells and any same-class recount to agree while both
are wrong, the error must live in the rule schema all frontier implementations
share, not in any one implementation. In code terms, one of these three
shared propositions would have to be false:

1. **The cross-cut stencil is complete.** A new cell at column c, row r can
   be king-adjacent to swept cells only via the previous column's rows
   r−1, r, r+1 (`core/transition.h:52-56`; `core/kink.h:114-117` as
   N/W/NW/SW with the NW cell carried in b[H+2]; `cpp/strip_tm.cpp:100-110`).
2. **The label partition is a sufficient statistic.** The component labels of
   the boundary column exactly capture which swept cells are mutually
   connected, so unioning labels is equivalent to unioning the underlying
   cell sets, and a stranded old component (no new neighbour) can never
   reconnect (`core/transition.h:59-65`; `core/kink.h:138-140`,
   `core/kink_column.h:88-92`; `cpp/strip_tm.cpp:112`).
3. **The completion predicate is the definition.** A state whose labels form
   exactly one component, meeting each engine's height-exactness accounting
   (touch flags at `core/classifier.h:48` and `cpp/sym/symtm.cpp:91`;
   second-difference recovery at `cpp/strip_tm.cpp:6-9`), corresponds
   one-to-one with completed king-connected animals of height exactly H.

Any misconception expressible at this level — a wrong or incomplete stencil,
a case where the partition-of-the-boundary abstraction loses a reconnection
or manufactures one, or a completion predicate that miscounts an edge class —
reproduces identically in every independently-written engine of the class,
because each engine is a faithful implementation of the same three
propositions. Agreement between the kink kernel, the column kernel, symtm,
and strip_tm tests the implementations, not the propositions. That is the
one-sentence objection of `2b3115b`, grounded: the smallest statement is
**"union-find over previous-column component labels with stranded-component
death and a one-component completion predicate correctly counts exactly the
king-connected n-cell sets of height exactly H" — every engine that has
touched the H=15..21 band at n=40 assumes it; symcount_fast (BFS on the
lifted set, no cut) and g2 (rooted growth, no predicate) are the only
counters in the repo that do not, and neither has reached those cells.**

### NOT ESTABLISHED

- Whether the phase A/B/C binaries on dalby were built exactly from revs
  `38956525`/`801afd59` (PROVENANCE.md asserts it; the run logs and
  `rundir_size.log` are banked, but I did not attempt a binary-provenance
  audit — establishing it would mean checking the banked run.log headers
  under `results/ns_a40/` recheck artifacts against those revs).
- Whether `cpp/strip_tm.cpp` and the production kernels share any transitive
  third input (e.g. a common table). From reading the includes they do not —
  strip_tm.cpp includes only the standard library — but I did not build and
  audit the link line.
- `docs/viva-reserve.md`: unreadable (permission denied); indexed by name
  only.

## Appendix — harness-held ideas

None. No route ideas occurred during this work that are not already in the
brief's lane descriptions.
