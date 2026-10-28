# The push gates: the two tiers and what they cost

The pre-push hook runs two commands, `make ns-gate-fast` and `make gates`.
`scripts/profile_gates.sh` times them as the hook runs them, then re-times
every individual target serially so the parallel critical path can be named.
Per-target numbers below are serial, warm, on the 80-core ARM server unless
marked as the laptop.

## The push tier and the deep tier

`$(GATE_DEEP)` is empty by default and `--deep` under `make gates-deep`. A gate
takes it when it stores a derived value or limits a size; each such recipe says
what `--deep` restores. `make gates-deep` is the whole suite at full size: run
it before a release, and whenever the code under a stored or size-limited check
changes.

Every comparison the suite makes in the deep tier it also makes on the push.
What differs is re-derivation: a number that has not changed since it was
derived is read from a stored value on the push and re-derived in the deep tier.

- `gate-sig-fold` (`tests/sig_fold_unit.cpp`) settles the R1 fold exhaustively
  over every canonical signature at H≤6: reflection is an involution, `foldSig`
  picks the orbit representative, the completion bound and the closing
  predicate are mirror-invariant, the column step commutes with reflection, and
  the engine's whole per-state keep-set corresponds under it for every size
  budget. Three mutant folds are controls that must fail. 0.89 s.
- `gate-tma` check M runs at n=12 on the push, enough for the part a unit test
  cannot reach, that the sweep applies the fold correctly. The full check (M
  and N at 391 s of the gate's 429 s) is deep-tier.
- `gate-cluster-weights` reads stored DP values for the level-6 holdout, and runs
  the DP live on a level-3 composition every push so a broken DP is still
  caught. Both cross-checks the stored values claim (against `TWO_ROW_INTERIOR`,
  and against the single-row closed form) are asserted every run. The live
  level-6 DP is deep-tier.
- `gate-depth1-kernel` keeps `--selftest` on the push (stored Φ checked against
  the gap-walk series rebuilt from an independent enumeration through x^80,
  with a perturbed candidate as the control that must fail) and defers only the
  sympy derivation, which is 550 s of its 583 s under cProfile.
- `gate-g2` hole checks at n=9 on the push: they assert identities, and
  A389193 is 0,0,0,0,0,0,4,41,272, so n=9 has holey animals at three sizes.
  Deep tier: three `--holes` runs at n=11.
- `gate-s2` stops one term short on square8 (n=9 in deep tier, 10.5M canon
  calls), the lattice where each further term costs ~4x.
- `gate-modp` at n=11 on the push: a(11) = 39,299,408 keeps the primes four
  orders below the count and seven below their product, so the CRT
  recombination stays real. Deep tier: seven square8 sweeps at n=12.
- `gate-perimeter-min` keeps check E at W=11 (16.8 s, the same second-source
  statement) and its failing control reuses the row check E just computed.
  Deep tier: W=13, `perimeter_min square4 999 6 --only 13 13 0` at 198.55 s,
  with the control re-running the identical command (199.56 s) against a
  different radius.
- `build/tma_modp_test` is a make target rather than a `c++ -O3` shelled out
  by `gate_modp.py` on every run.

Deep-tier costs of the gates that take `--deep`:

| gate | deep tier | push tier |
|---|---|---|
| `gate-cluster-weights` | 536.5 s | 1.5 s |
| `gate-perimeter-min` | 418.4 s | 16.8 s |
| `gate-tma` | 325.3 s | 21 s |
| `gate-depth1-kernel` | 173.4 s | 12 s |
| `gate-g2` | 138.1 s | |
| `gate-s2` | 85.8 s | |
| `gate-modp` | 73.8 s | |

## Gates that run at full size in both tiers

`gate-p-paper-verifier` (71 s) is 200 verifier runs at 0.33 s of real work
each (the bare interpreter is 0.01 s, so it is not startup). Perturbing every
numeric literal is what makes it a coverage statement, and sampling would let
coverage drop silently. It is a candidate for input gating
(`paper/technical-report.tex` changes rarely).

`gate-subgroup`, `gate-sym`, `gate-king-grid`, `gate-symtm` (41/30/29/19 s) do
non-redundant work at moderate cost.

The suite runs serially per gate in one `make gates` invocation.

## Timing on the machine that runs the hook

Serial timings on the server do not predict the laptop's `-j10` critical path:
`gate-symtm` is 18.9 s serial on the server and 68 s on the laptop under
`-j10`, the single largest contributor to the push. Only the hook executes on
the laptop, so the hook is what reports, at three levels:

- `.githooks/pre-push` prints its own split (`ns-gate-fast Ns, gates Ns`) and
  keeps it in `build/pre-push.log`.
- `make gates` and `make ns-gate-fast` print `gate-time Ns <target>` per gate,
  and a failing run prints the eight slowest.
- `Gate.check` prints the seconds that produced each check line. A gate is a
  straight-line chain of engine runs scored in printed order, so the gap
  between check lines is the work behind the second one.

The costliest individual checks on the laptop:

| check | laptop | gate |
|---|---|---|
| `grid n=12 runs under 10 minutes` | 22.7 s | `gate-king-grid` |
| `90-degree rotation vs oracle, n<=8` | 21.2 s | `gate-sym` |
| `N smoke square8 H12 N14 dense baseline` | 16.0 s | `gate-tma` |
| `mdir n=12 runs under 10 minutes` | 10.1 s | `gate-multidirected` |

## Input gating, opt-in

The default is that every gate runs, every time. A gate is skipped only if it
is declared (`DEPS_<gate>` in the Makefile) with the full set of things it
reads, and its stamp is newer than all of them. Undeclared is the safe state,
so forgetting to declare a gate costs time, not coverage. (`ns-gate-go` is 16 s
of a 47 s push run serially, and `go test ./orchestrator/... ./verify/...`
reads Go packages and nothing else in this tree.)

Declaring one wrong is caught two ways: `gate_makefile_wiring` requires a
declared gate's own script to be among its deps, so editing a gate always
re-runs it; and a dep that has gone missing makes the gate run rather than
skip. `make gates-force` ignores every stamp, and the hook forces on a new ref.
`gates-deep` keeps separate stamps (`build/stamps/<gate>.deep`), so a deep
pass skips what an earlier deep pass already ran on the same inputs;
`make gates-deep FORCE_GATES=1` runs all of it. Bare `make` is `gates`.

The hook's `docs_only` test treats `.txt` under `results/` and `fixtures/` as
data, not prose: gates read `results/holes_n14.txt`, `results/siteperim_*.txt`
and `fixtures/b*.txt`, so editing a gate's fixture runs the gate that checks it.

Four C++ binaries (`build/ns/map_worker`, `merge_worker`, `driver0`,
`gate_holes`) must not be `.PHONY`: a gate whose declared input is the binary
it runs can never skip if the binary is rebuilt on every invocation.

## Cost of a push

Measured on the laptop by the hook itself:

| | full re-derivation | push tier with input gating |
|---|---|---|
| green `git push`, code | 312 s | 9 s |
| green `git push`, docs only | — | 3 s |
| `make gates` (−j10) | 250+ s | 7 s |
| `make ns-gate-fast` (serial) | — | 1 s |
| `make gates` serial sum, server | 2016 s | 436 s and lower since |

`make gates` is bounded by the gates that are still undeclared,
`gate-perimeter-defect` foremost. Each further declaration is a small piece of
careful reading; the import half of it is checked mechanically, the data half
is not.
