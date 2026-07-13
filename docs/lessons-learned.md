# Lessons learned — the polyplets project (jasonp + Claude)

Drafted 2026-07-15 by Claude per jasonp's standing ask; sections marked
[JP] are jasonp's to write. Companion: the six postmortem failure classes
are already distilled as day-one practices in the project memory
([[next-project-practice]]); this document is the narrative and evidence
behind them, plus everything learned since.

## 1. The six failure classes as day-one practices (from the postmortem)

1. **Lab/pub repo split** — exploratory junk and publishable artifacts in
   one tree cost real cleanup time. Next project: two repos or a strict
   lab/ subtree from day one.
2. **Machinery, not advice** — every process rule that mattered became a
   script, a gate, or a checker; the ones that stayed prose got violated.
3. **Provenance + expiry** — every banked number carries its engine rev,
   machine, and validation; anything without provenance rotted (see the
   H=11 incident, §4).
4. **Result store first** — results/*.md as the single source of truth,
   written at the moment of the result, saved this project repeatedly
   (integration corrections were caught because prior work was findable).
5. **Close designed at start** — the close target existed only from
   mid-project; the tail would have been shorter with it from day one.
6. **Collaboration contract** — the working agreements (§6) took months
   of friction to converge; write them down at the start next time.

## 2. Verification culture: what actually caught errors

- **Holdout discipline everywhere.** Every fitted object (P_k, dm
  quasi-polynomials, GF recoveries, recurrences) was pinned on the fewest
  admissible points and *required* to predict the rest. This caught: the
  spurious order-7 "recurrence" for the all-pairs weights (refuted at
  l=16 by a non-integer prediction), and two spurious PSLQ minimal
  polynomials (killed by precision escalation: a degree-4 candidate's
  residual jumped 15 orders of magnitude at higher truncation).
- **Control calibration.** A test is only as good as its power, and the
  power must be demonstrated on a known case. The convex-perimeter
  D-finiteness guesser initially FAILED its own control (A005436, known
  algebraic); fixing the test until the control passed is what made the
  king-convex result trustworthy. Same pattern: the Convex Mirage's
  non-D-finiteness test is credible because the known-non-D-finite
  control also fails it.
- **Two-algorithm agreement as the gold tier**, decorrelation as silver,
  and *never* silently mixing the tiers (the paper's T1/T2/T2-/T3 system).
- **The master equation as a bug detector.** Cluster-weight enumeration
  windows were wrong three separate times; twice the error was caught not
  by inspection but because a DOWNSTREAM exact identity missed by a tiny
  integer (h3 off by 18 => W(2,2,2) off by exactly 2). Exact overdetermined
  cross-checks find bugs that eyeballs cannot.
- **mod-p certificates.** Squarefreeness, coprimality, and irreducibility
  of huge polynomials were certified cheaply mod one or two primes
  (rigorous in one direction). Multi-prime subset-sum intersection
  certified irreducibility of a degree-462 polynomial in seconds.

## 3. Bestiary of computational bugs (each with its tell and its rule)

- **Window/truncation bugs (x3).** Enumeration windows that were "surely
  wide enough" were not, three times. Tell: downstream identity off by a
  small integer. Rule: windows must have a PROOF (spread < cell count),
  or the result gets a widening-stability check.
- **Float rot (x2).** Big-integer polynomial coefficients silently
  overflowed float evaluation, producing a wrong "root" that briefly
  faked a monotonicity violation in the strip growth constants. Tell: a
  jump in a sequence that theory says is smooth. Rule: exact or mpmath
  arithmetic for anything feeding a conclusion; floats only for display.
- **PSLQ/lattice-fit noise.** An integer-relation fit that consumes as
  many digits as the input provides is a coin flip. Rule: information
  budget check (coefficient digits x degree << reliable digits), then
  re-verify at higher precision before believing.
- **Premature commit (x2, same day).** Committing before the checker ran;
  both times the checker failed seconds later and the commit needed
  amending. Rule: the assert runs BEFORE git commit, mechanically.
- **Stale artifacts that look like data.** A validated=False GF (H=11)
  sat in a results file and was nearly consumed by an analysis sweep; its
  root structure was anomalous (shares no roots with neighbors),
  flagged only because the sweep checked a structural invariant. Rule:
  unvalidated artifacts live in a quarantine namespace, not beside
  validated ones.
- **External data is data too.** A published OEIS comment (A187077
  "equivalent to row-convex polyhexes") was measurably wrong; we caught
  it because we treat every cross-reference as a checkable claim. Rule:
  cite it, then check it.

## 4. Research-process lessons

- **Measure, don't reason** paid for itself dozens of times: the P17-from-
  the-gas shortcut was killed by a 3-point timing extrapolation instead
  of a week of theory; the "insight in the box table?" question was
  answered by an afternoon probe with a pre-registered verdict.
- **Grep before claiming new** (and OEIS-lookup before claiming new):
  convex polyplets were re-derived in ignorance of the deeper banked
  investigation once; the Temperley GF was re-derived before checking
  OEIS once. Both cost hours; the lookup costs seconds.
- **Negative results are banked results.** The measured dead-ends
  (MPS rank, banded encodings, bounded-depth recurrences, P17-from-gas,
  root recycling in the convex family) each prevented at least one
  future re-investigation, and two of them (root separation, its convex
  counterpart) turned into load-bearing ingredients of theorems.
- **Name things.** Convex Mirage, Ternary Spine, Kink Carry, Atom Ledger:
  named results get remembered, cross-referenced, and not re-derived.
- **The best tool transfers.** The single biggest scientific yield came
  from taking one proof template (walk + clusters + partial fractions)
  and pushing it through every object in sight: the height law, the
  hole-graded law, the hex/square/polyiamond laws, the dm law. When a
  proof works, immediately ask what else it proves.

## 5. Operations (pointers, details in memory + docs)

- Fleet sizing from ALL-CORE benchmarks, never single-core; rebalance
  mid-run by contiguous ID ranges. RAM budget is (total x margin)/cores.
- One tmux session per machine, jobs as foreground windows with tee'd
  logs; heartbeat lines with progress= and eta=; no nohup, no /tmp, no
  stdin heredoc jobs; no pattern-kill, ever.
- Observability standard (docs/observability.md) implemented as shared
  machinery (obs.py / cpp/obs.h) across every engine.
- Job-start checklist (docs/job-checklist.md) before ANY compute launch.

## 6. Collaboration contract (as converged; write down on day one next time)

- Direct answers in the asked format first; no adjacent offers.
- Match verbosity; never restate the human's point back.
- Small samples before full runs; no >1h job without explicit agreement;
  once a frontier job is healthy, only correctness restarts it.
- Autonomy within a turn, menus at decision points ("what's next" gets
  options, not action).
- Externally visible actions (OEIS, email, publication) are the human's
  exclusively; the assistant preps, the human pushes the button.
- All authorship representations (OEIS %C, paper authorship note) are the
  human's own words; the assistant meaning-checks only.

## 7. [JP] jasonp's sections — to write

- [JP] What the project was for, and whether it delivered that.
- [JP] What I would do differently (human side).
- [JP] The viva experience: did the self-certification bar work?
- [JP] Cost/benefit of the hardware-months and the AI collaboration.
- [JP] Anything the assistant's account above gets wrong or misses.
