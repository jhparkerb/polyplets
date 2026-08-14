# Clean Room — the depth-j identity, re-derived independently

2026-08-14. Standing condition on the anchor cut: cells pinned through it
count as shored up only once the depth-`j` identity for `D_j(k)` has been
re-derived by someone who has not read `experiments/severance_w3_depths.py`.
This note records that re-derivation, the one defect it had, and what it does
and does not establish.

## Result

An independent derivation reaches the same family bound and the same numbers.
Seventeen cells agree exactly **past the range the shipped gate covers**,
where nothing can be fitted:

| depth | holdout cells (k ≥ 20) | count |
| ----- | ---------------------- | ----- |
| j = 2 | k = 20..25             | 6     |
| j = 3 | k = 20, 22..25         | 5     |
| j = 4 | k = 20..25             | 6     |

`D_3(21)` is deliberately **excluded**: I quoted the incumbent's value for
that cell to the deriver while diagnosing a mismatch, so it is contaminated
and cannot count as independent. It agrees, but that agreement proves nothing.

Across both comparisons the two sides agree on every shared cell: 47 at
j = 2, 3 and 22 at j = 4, 69 in all, of which 18 sit at `k >= 20`. Zero
mismatches. The 17 above is 18 less the one contaminated cell.

## The clean room

`git archive HEAD` into `~/tmp/cleanroom-depthj` on ayr, then **physical
deletion** of every file that prices or states the depth-j family class —
not an honour-system blocklist. Removed: `experiments/severance_w3_{depths,
gate,modp}.py`, `experiments/severance_w4_field.py`,
`experiments/depth_swap_anchors.py`, `cpp/severance_w3_families.cpp`, both
cached family tables, `results/onset-defect-depths234.md`,
`results/depth-swap-anchors.md`, `results/anchor-cut-map.md`,
`results/report-claims-after-anchor-cut.md`,
`results/depth-tower-bivariate-dead-end.md`,
`docs/proofs/depth-swap-residual.md`, `docs/onset-defect-severance-plan.md`,
`docs/motley-plan.md`, `docs/severance-w4-scoping.md`, `HANDOFF.md`,
`polyplets/Polyplets/DepthAssembly.lean`, and `results/rook1/` (R1-E leaked
the whole family class in passing). Section 6 of
`results/onset-defect-depth1-closed.md` was replaced in place with an
explicit redaction marker.

Cluster **excess** was deliberately left in: it is project-wide vocabulary
from `docs/proofs/T-n-nm2-and-general.md`, not a depth-j hint.

Provenance by `git bundle` — bundle fetched into the real repository on ayr
and dalby, checked out as worktrees, binaries stamping `GIT_REV` — so the
tree under test is verifiably rev `74bf988b` and not a hand-assembled copy.

## The independent route

Substituting `z = 1/u`, `Y = y/u` turns the Step-4 numerator into

    sum_{t>=0} r_{2k+1-t} u^t = [Y^k] (u-3)^(k+1) { P~ + B~ T~ / (u - 3 - S~) }

with every cluster type weighted `Y^surplus · u^excess`. Reducing mod `u^j`
kills every cluster of excess ≥ j, so **depth j draws only on families of
total excess ≤ j−1** — the incumbent's bound, reached without its script. At
`u = 0` the expression collapses to the public depth-1 identity
`D_1(k) = [y^k](P̂ − B²/(3+S))`.

The assembler (`experiments/assemble_below.py` in the clean-room tree) is
fail-closed on that collapse: it asserts the public depth-1 numerators
4, 80, 1753, 40928, 987355 over `3^(k+1)` before emitting any value.

## The defect, and how it surfaced

First comparison returned **FAIL**: j = 2 exact everywhere, j = 3 exact
through k = 20 and diverging from k = 21, same denominators, discrepancy
growing. Run to ground from both ends rather than adjudicated.

- **Incumbent side — cap-stable.** Re-run at K = 27, its k = 21..25 values at
  j = 3 are identical to the K = 25 run. Its agreement is not an artefact of
  its own truncation bound. (A spurious `diff` disagreement between the two
  was CRLF line endings introduced through ssh, not content.)
- **Challenger side — a bad guard, conceded.** A "bridging" prune dropped
  frontier states whose inter-block clearance exceeded a claimed
  future-reduction capacity, on the claim that a row of size `s` reduces
  `clearance_need` by at most `2s`. With the prune disabled, only the one-4
  series changes, and it changes first at `l = 19`, i.e. **k = 21** — exactly
  the mismatch onset.

The incumbent was the correct side. The corrected challenger reproduces it.

**The guard is wrong but not yet localized.** `experiments/prune_probe.py`
tests the stated per-row claim directly, and over its sample the claim
*holds*: max observed reduction 2, 4, 6 for `s` = 2, 3, 4 against caps of
4, 6, 8. So the per-row bound is not the defect — or at least is not violated
on the 2- and 3-block frontiers with gaps ≤ 14 that the probe enumerates,
which is well short of the L = 23 frontiers where the series actually moves.
What is established is only that the prune changes answers and the no-prune
series is the correct one. The mechanism — a cap violated on richer
frontiers, or a sound cap applied unsoundly in the clearance accounting —
is **open**. The prune is disabled, so nothing downstream depends on
resolving it.

**Span convergence, measured not assumed.** The deriver left four one-4
caches with no record of which flags produced which. Re-run with explicit
flags: `--noprune` (183 s, 715 MB) and `--noprune --spanx=16` (494 s,
1.49 GB) at L = 23 both produce md5 `c301504aa6dfae5b27daebb749405788`,
matching three of the four caches. The fourth was the pruned run.

## What the disagreement did and did not touch

Nothing the a(40) claim rests on. The anchor cut pins level `k` only to
`H_max + J − 2 = 19 + 3 − 2 = 20`, and both sides are exact at `k ≤ 20`. The
divergence region matters for the J = 5 extension, not for banked terms.

## Depth 4 needed the incumbent's ceiling lifted

`D_series(4, K)` is nearly free once the excess-3 family table is on disk
(0.04 s at K = 25) — the cost is entirely the table, and `_load_table()`
accepts any `..._K<Kt>_e3.txt` with `Kt >= K`. Only `K19_e3` was cached, so
the incumbent could not reach past k = 19 at j = 4 and the first j = 4
comparison came back **VACUOUS** by the comparator's own rule. Building
`results/severance_w3_families_K25_e3.txt` (44:17 wall, 2.89 GB, 16 threads
on a contended ayr) lifted the ceiling; the new table agrees with `K19_e3` on
all 76 overlapping cells.

## Method notes

- The comparator (`compare.py`) is fail-closed in two directions: any
  mismatch fails, **and** a run that compares no cell at `k ≥ 20` fails as
  VACUOUS, since anything at `k ≤ 19` is already covered by the shipped gate.
  A RED selftest perturbs one candidate value and must fail; it did, on every
  invocation reported here.
- The j = 4 challenger values were assembled by me from the deriver's cached
  family series using the deriver's own unmodified assembler, after its agent
  ended without running that step. Nothing was tuned.
- **Provenance gap, stated openly.** Only one-4 — the family that carried the
  defect — was re-run with explicit flags. The other three excess-3 families
  feeding j = 4 (one-5, 4+3, 3+3+3) still rest on the deriver's `*_loose.json`
  caches, whose invocation flags were not recorded. Re-running them was
  started and then **abandoned on cost**: one-5 measures 8391 s / 17.0 GB and
  4+3 measures 6792 s / 31.4 GB, so six runs including the `--spanx=16`
  variants would have been a 15-hour job, and the span-extended 4+3 would have
  threatened ayr's RAM. The correctness of those series is carried by the
  comparison itself — j = 4 agrees with the incumbent on 6 holdout cells —
  not by their flag provenance.

## Measured costs

C++ builder `build/severance_w3_families families K EMAX THREADS`:

| K  | emax | threads | machine        | wall    | peak RSS |
| -- | ---- | ------- | -------------- | ------- | -------- |
| 16 | 4    | 4       | dalby (quiet)  | 47:09   | 4.49 GB  |
| 16 | 4    | 8       | dalby (quiet)  | 40:33   | 4.73 GB  |
| 16 | 4    | 16      | dalby (quiet)  | 38:09   | 5.13 GB  |
| 17 | 4    | 16      | dalby (quiet)  | 60:33   | 7.35 GB  |
| 18 | 4    | 16      | dalby (quiet)  | 92:28   | 9.30 GB  |
| 25 | 3    | 16      | ayr (contended)| 44:17   | 2.89 GB  |

Two things follow. **Excess is the expensive axis, not K** — K = 19/e = 3 is
146 s where K = 16/e = 4 is 38 minutes.

And **there is no thread win**: quadrupling threads from 4 to 16 buys 19% of
wall, so the builder is heavily serial-bound. Peak RSS is nearly *flat* in
thread count (4.49 → 5.13 GB), which says the footprint is the family tables
rather than per-thread state — so no thread choice will shrink the memory
bill, and the K = 21 RSS estimate holds whatever count is used. Tables were
byte-identical across all three thread counts, which is a free correctness
check on the builder's parallelism.

This does not reproduce the older `K=16, e=4` reference of 18 min / 2.2 GB on
8 cores; dalby measures 40:33 / 4.73 GB at 8 threads. That reference's machine
is unrecorded and it should not be used for planning.

Extrapolating the e = 4 series (wall ratio 1.59 then 1.53 per K step) puts
**K = 21 at roughly 5–6 h and 14–19 GB**. That is a beg-and-agree job, not a
free one.

The clean room's per-family Python builder is **not** a cheaper route to the
excess-4 families J = 5 needs. Its own excess-3 costs, on ayr:

| family    | L  | wall   | peak RSS |
| --------- | -- | ------ | -------- |
| (4)       | 23 | 183 s  | 0.72 GB  |
| (4) sx16  | 23 | 494 s  | 1.49 GB  |
| (3,3,3)   | 22 | 506 s  | 0.89 GB  |
| (3,4)     | 22 | 6792 s | 31.4 GB  |
| (5)       | 22 | 8391 s | 17.0 GB  |

The single-block families are cheap and the mixed ones are not: 4+3 alone
costs nearly two hours and 31 GB at excess 3. The five excess-4 families
— `(6)`, `(3,5)`, `(4,4)`, `(3,3,4)`, `(3,3,3,3)` — would be worse on both
axes. The C++ table at K = 21 / emax = 4, at ~5–6 h and 14–19 GB for
everything at once, is the cheaper door.
