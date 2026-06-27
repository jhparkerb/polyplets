# 05 — deferred / closed work (decisions, 2026-06-27)

Investigated the remaining off-critical-path items while the a(21) probe ran.
Recording the decisions and the evidence so these aren't silently skipped.

## M5.5 — GF recovery (Counter<ModP> + residue classifier): DEFERRED

Not building now. Evidence:

- **No new classifier is needed.** `ClassifyTriangle` already does
  `out.row[n] += rec.counts[i]` for any `Word` (core/classifier.h:50-53). A GF /
  residue classifier is just the triangle classifier over a modular `Word`. So
  the only real deliverable is a `Counter<ModP>` word type.
- **A modular counter has no near-term payoff.** Through a(25) counts fit u64,
  through ~a(48) they fit u128 (core/counter.h:6,22-23) — *exactly*. When the
  exact count fits, its residue mod p is trivially derived from it; ModP only
  earns its keep once exact counts overflow the word (≈a(48) with u128). The
  project's own settled analysis already concluded ModP/CRT counters are a **net
  loss below a(26)** ([[crt-counter-shaping-settled]], results/crt-counter-shaping.md).
- **Full GF reconstruction is separately dormant.** Berlekamp-Massey recovery of
  the fixed-height rational GFs is marked infeasible for H≥10 in
  docs/frontier/07-gf-recovery-notch-modp.md (2r sweeps × prime pool ≫ direct
  notch cells); viable only H≤9, already recovered.
- **Plus integration cost:** a struct `Word` collides with the integral-assuming
  serialization in core/runfile.h.

Revisit when the frontier nears a(48) (u128 overflow) or fixed-height GF research
revives for H≤9 as an independent low-n cross-check. Until then it's effort for
zero current payoff.

## #30 — OAMap<V> unification (FlatDB/FlatDB32/HoleDB/PerimDB): MOOT

These types live entirely in `cpp/tma/` (statedb.h, sweep8_*.h) — the **old
engine**, unused by the new engine (core/, orchestrator/, worker/). With the old
engine being retired (dalby cut over; ayr finishing its last heights), unifying
its data structures is a refactor of code we're decommissioning. No payoff.
Revisit only if the old engine is kept as a long-term maintained oracle.

## #33 — an_fold_parallel.sh kill trap: MOOT

Also old-engine: `an_fold_parallel.sh` is the old split-sweep driver. It has one
run left (ayr H17/H18) and we won't launch it again. Adding a child-reaping trap
now means churning a driver mid-run for an engine we're retiring — exactly the
kind of no-value churn to avoid. Closed.

## Net

The off-critical-path backlog is empty of high-value building: M5.5 is net-loss
until ~a(48), #30/#33 are old-engine cleanups for a retiring engine. The one
useful safe improvement found and done was baking the git rev into the Go
orchestrate binary (provenance for the a(21) run). The critical path remains:
probe → a(21) launch → validate, gated on the probe.
