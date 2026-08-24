# The push gates: what they cost, and what moved to a deep tier

Profiled 2026-08-24 because a `git push` had grown to 312 s on gympie.
`scripts/profile_gates.sh` times the pre-push hook's two commands as the hook
runs them, then re-times every individual target serially so the parallel
critical path can be named rather than guessed. All per-target numbers below
are dalby, serial, warm.

## What the profile found

Not what the comments claimed. Three of the four most expensive gates were
paying, on every push, to re-derive something settled:

| gate | before | what the time was |
|---|---|---|
| `gate-severance-w1` | 536.5 s | a level-6 Python DP holdout, recomputed each run |
| `gate-perimeter-min` | 418.4 s | one `perimeter_min` command, run twice |
| `gate-tma` | 325.3 s | check M proving a fold symmetry by enumerating to n=14 |
| `gate-severance-w2` | 173.4 s | the sympy kernel derivation, re-derived each run |
| `gate-g2` | 138.1 s | three `--holes` runs at n=11 |
| `gate-s2` | 85.8 s | `count_symmetry` on square8 n=9, 10.5M canon calls |
| `gate-modp` | 73.8 s | seven square8 sweeps at n=12 (plus a `c++ -O3` per run) |
| `gate-p-paper-verifier` | 71.2 s | 200 verifier subprocesses at 0.33 s each |

Two of the headline comments were wrong by two orders of magnitude.
`gate-perimeter-min` said "~2 s" — that was its three census cross-checks,
which really are ~1 s together. Its actual cost was check E's W=13 case:
`perimeter_min square4 999 6 --only 13 13 0` at 198.55 s, and the RED control
that followed it re-ran the identical command (199.56 s) to compare the same
row against a different radius. 415 s of 417 s, in one command and its echo.

`gate_tma.py`'s own comment priced checks M and N at 391 s of 429 s and was
right, but what M was proving — that the R1 vertical-mirror fold is a symmetry
of the column step — is a property of ~40 lines of `signature.h` and
`transition_square8.h`, not of the polyplet counts.

## The push tier / deep tier split

`$(GATE_DEEP)` is empty by default and `--deep` under `make gates-deep`. A gate
takes it when it banks or bounds something; each such recipe says what `--deep`
restores. `make gates-deep` is the whole suite at full size: run it before a
release, and whenever the code under a banked or size-limited check changes.

Nothing was deleted. Every comparison the suite made before, it still makes.
What moved is *re-derivation*: a number that has not changed since it was
derived is read from a bank on the push and re-derived in the deep tier.

- **`gate-sig-fold`** (new, `tests/sig_fold_unit.cpp`) settles the R1 fold
  exhaustively over every canonical signature at H≤6 — reflection is an
  involution, `foldSig` picks the orbit representative, the completion bound and
  the closing predicate are mirror-invariant, the column step commutes with
  reflection, and the engine's whole per-state keep-set corresponds under it for
  every size budget. Three mutant folds are RED controls. 0.89 s.
  It also replaces `experiments/r1_sym_fold_check.py`, which `signature.h` still
  cites as the fold's validation and which was deleted in `91bdcdc`.
- **`gate-tma`** check M drops to n=12 — enough for the part a unit test cannot
  reach, that the *sweep* applies the fold correctly.
- **`gate-severance-w1`** reads banked DP values for the level-6 holdout, and
  runs the DP live on a level-3 composition every push so a broken DP is still
  caught. Both cross-checks the bank claims (against `TWO_ROW_INTERIOR`, and
  against the single-row closed form) are asserted every run.
- **`gate-severance-w2`** keeps `--selftest` on the push — banked Φ checked
  against the gap-walk series rebuilt from an independent enumeration through
  x^80, with a perturbed candidate as the RED control — and defers only the
  sympy derivation, which was 550 s of its 583 s under cProfile.
- **`gate-g2`** hole checks at n=9: they assert identities, and A389193 is
  0,0,0,0,0,0,4,41,272, so n=9 has holey animals at three sizes.
- **`gate-s2`** stops one term short on square8, the lattice where each further
  term costs ~4x.
- **`gate-modp`** at n=11: a(11) = 39,299,408 keeps the primes four orders below
  the count and seven below their product, so the CRT recombination stays real.
- **`gate-perimeter-min`** keeps check E at W=11 (16.8 s, the same second-source
  statement) and the RED control reuses the row check E just computed.
- **`build/tma_modp_test`** is a make target; `gate_modp.py` used to shell out to
  `c++ -O3` on every single run.

## What was left alone

`gate-p-paper-verifier` (71 s) is 200 verifier runs at 0.33 s of real work each
— measured: the bare interpreter is 0.01 s, so it is not startup. Perturbing
every numeric literal is what makes it a *coverage* statement, and sampling
would let coverage drop silently. It is the clearest candidate for gating a
gate on its inputs (`paper/technical-report.tex` is read-only and changes
rarely), which is a separate decision.

`gate-subgroup`, `gate-sym`, `gate-king-grid`, `gate-symtm` (41/30/29/19 s) are
doing real, non-redundant work at moderate cost.

The suite is still run serially per gate and in one `make gates` invocation.
Making tests faster by running more of them at once was considered and rejected.

## Instrumenting the machine that runs it

The first round of cuts was ranked off a dalby profile and moved gympie's
`make gates` from 80 s to 79 s. The dalby ranking does not transfer:
`gate-symtm` was 18.9 s serial on dalby and **68 s** on gympie under `-j10`, the
single largest contributor to the push, and nothing in the dalby numbers said
so. Two further rounds of inference moved `gate-tma` by nothing.

Only the hook executes on gympie, so the hook is what reports. Three levels, all
permanent:

- `.githooks/pre-push` prints its own split (`ns-gate-fast Ns, gates Ns`) and
  keeps it in `build/pre-push.log`.
- `make gates` and `make ns-gate-fast` print `gate-time Ns <target>` per gate,
  and a red run prints the eight slowest.
- `Gate.check` prints the seconds that produced each check line — a gate is a
  straight-line chain of engine runs scored in printed order, so the gap between
  check lines is the work behind the second one.

Between them they named, in one push each, what three rounds of inference had
missed:

| check | gympie | gate |
|---|---|---|
| `grid n=12 runs under 10 minutes` | 22.7 s | `gate-king-grid` |
| `90-degree rotation vs oracle, n<=8` | 21.2 s | `gate-sym` |
| `N smoke square8 H12 N14 dense baseline` | 16.0 s | `gate-tma` |
| `mdir n=12 runs under 10 minutes` | 10.1 s | `gate-multidirected` |

## Input gating, opt-in

`ns-gate-go` was 16 s of a 47 s push, serially, on every push including
documentation-only ones — and `go test ./orchestrator/... ./verify/...` reads Go
packages and nothing else in this tree.

The default is unchanged: every gate runs, every time. A gate is skipped only if
it is DECLARED (`DEPS_<gate>` in the Makefile) with the full set of things it
reads, and its stamp is newer than all of them. Undeclared is the safe state, so
forgetting to declare a gate costs time, not coverage — the opposite of the
failure this repo has had twice, where a curated allowlist quietly stopped
running something.

Declaring one wrong is caught two ways: `gate_makefile_wiring` requires a
declared gate's own script to be among its deps (RED 10), so editing a gate
always re-runs it; and a dep that has gone missing makes the gate run rather
than skip. `make gates-force` ignores every stamp, `gates-deep` implies it, and
the hook forces on a new ref.

Also fixed while here: the hook's `docs_only` test counted every `.txt` as
prose, while gates read `results/holes_n14.txt`, `results/siteperim_*.txt` and
`fixtures/b*.txt` as data — so editing a gate's own fixture skipped the gate
that checks it.

## What it netted

Measured on gympie by the hook itself:

| | before | after |
|---|---|---|
| green `git push`, code | 312 s | 18 s |
| green `git push`, docs only | — | 9 s |
| `make gates` (−j10) | 250+ s | 8 s |
| `make ns-gate-fast` (serial) | — | 8 s |
| `make gates` serial sum, dalby | 2016 s | 436 s and lower since |

Three things account for it, in order of how much they gave:

1. **Gates that re-derived settled facts** stopped doing so on the push, and
   `make gates-deep` re-derives them. `gate-severance-w1` 536.5 → 1.5 s,
   `gate-severance-w2` 173.4 → 12 s, `gate-tma` 325.3 → 21 s.
2. **Gates that ran the same command twice.** `gate-perimeter-min` was one
   `perimeter_min square4 999 6 --only 13 13 0` at 198.55 s, plus a RED control
   that re-ran the identical command (199.56 s) to compare the same row against
   a different radius: 415 of its 417 s. `gate_tma` checks H and I likewise.
3. **Gates whose inputs had not changed** stopped running at all — 15 of them
   on a typical push.

`gate-sig-fold` is the one addition: 0.9 s, and it settles a statement that used
to cost 391 s to make.

Nothing about what the suite checks changed. `make gates-deep` restores every
size, every re-derivation, and ignores every stamp; it has been run green on
dalby.

## What is left

`make gates` is 8 s and bounded by `gate-perimeter-defect` (8 s), which is
undeclared and so runs every time. `ns-gate-fast` is 8 s. Both can go lower by
declaring more gates, one at a time, each declaration being a small piece of
careful reading that the import lint checks half of.

`gate-p-paper-verifier` is 200 verifier runs at 0.32 s of real work each. It is
declared, so it only runs when the paper or the verifier changes — but when it
does run it is 8 s even at 8-way concurrency, and sampling the literals is not
available: the statement is coverage, and a sample lets coverage drop silently.
