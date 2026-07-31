# mu_H strip-growth engine — resumption dossier

Date: 2026-07-10. Detailed enough to resume cold. Goal, current state, engine
inventory, the exact design of the unfinished fast engine, validation, and the
rigor path. Companion: results/strip-growth-lambda-bounds.md (the numbers/claims).

## Goal

`mu_H` = dominant strip growth constant of height-H polyplets = 1/x*, where x* is
the radius of convergence of the height-H strip = the x at which the king
connectivity transfer matrix M(x) has spectral radius 1. `mu_H < lambda` strictly,
`mu_H -> lambda`. Two payoffs:
1. **Rigorous lower bound on lambda**, improving with H. mu_13=6.306 (below the
   multi-directed 6.475). Extrapolated mu_16~6.50 BEATS 6.475; mu_18~6.59,
   mu_20~6.66 → best rigorous lower bound on lambda, ours, and certifiable
   (Collatz-Wielandt, below). Complementary rigorous UPPER bound lambda <= 9.3153
   (exact certificate) brackets it: 6.543 <= lambda <= 9.3153 as of 2026-07-31
   (certified mu_17; was 5.828 from the directed closed form). See
   [../docs/proofs/polyplet-upper-bound.md](../docs/proofs/polyplet-upper-bound.md).
2. **Independent lambda estimate**: finite-size extrapolation mu_H -> lambda
   corroborates the a(n)-ratio 7.111 from a different direction. Delivered at
   H<=13 (converging monotone to ~7.11); higher H sharpens it.

Decision 2026-07-10 (jasonp): SKIP the fast engine for now, bank. May resume.

## Exact ladder (validated, reproduce these)

| H | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| mu_H | 2.4142136 | 3.4437184 | 4.1823214 | 4.7178013 | 5.1153245 | 5.4178476 | 5.6533728 | 5.8404579 | 5.9916958 | 6.1158416 | 6.2191246 | 6.3060713 | 6.3800344 |

H<=11 independently cross-checked against fixed-height GF roots
(1/smallest positive root of Q_H, `results/fixed_height_gfs.txt`,
`experiments/mu_H_from_atoms.py`). H=14 **done: mu_14 = 6.3800344**
(`results/strip_mu_H14.log`, 4851s).

Extrapolation: `experiments/lambda_from_mu.py` (update the `mu` dict with new
points). Sliding 3-point power-law fit `mu_H = lambda - c*H^{-p}` gave lambda
estimates 9.54,8.41,7.92,7.66,7.50,7.40,7.33,7.29 (center H=5..12), p -> ~1.

## Engine inventory

- **`cpp/strip_mu.cpp`** (`build/strip_mu`): all-column power iteration, u64 4-bit
  state, brute 1..2^H mask loop, CSR edge storage. Validated. Caps ~H=13
  (H=13: 465s; edges ~states*2^H blow up RAM by H=14).
- **`cpp/strip_mu8.cpp`**: whole-column via the tma `stepColumnSquare8` +
  viable-mask enumerator. Validated (same mu_H). Same 2^H edge wall — viable
  masks don't help without an area budget (low-component states still have ~2^H
  successors). No gain over strip_mu.
- **`cpp/strip_mu_kink.cpp`** (`build/strip_mu_kink`): **THE cell-at-a-time engine.
  Correct, validated** (reproduces mu_H exactly to H=11). Reuses the production
  `kinkStageTransition` (core/kink.h) — the three functions canonMixed,
  labelInMixedState, kinkStageTransition are copied verbatim (single source of
  truth). One M(x)*w matvec = a column sweep: seed -> H per-cell stage transitions
  (weight x^placed, states MERGE in an unordered_map) -> finalize. O(H*states),
  no 2^H, no edge storage. **Limitation: unordered_map-bound** (H=11: 100s,
  ~3.4x/H -> H=16 ~12h). Correctness done; only speed is missing.

## The unfinished fast engine (indexed-array rewrite of strip_mu_kink)

Same logic, hash maps replaced by integer-indexed dense arrays + sparse per-stage
operators. This is the whole remaining task.

**State spaces.** Boundary states `B` (Sig H+2, flags b[H],b[H+1] zeroed for the
"<=H" transfer matrix). Per-stage mixed states `S_0..S_H` (Sig H+4: +carry b[H+2]
+placed b[H+3]).

**Construction (one BFS closure over boundary states):**
- `bidx: Sig->int` for B; `midx[r]: Sig->int` for S_r (r=0..H).
- Seed: boundary b -> S_0 mixed (copy, carry=0, placed=0), 1:1.
- Stage op T_r (r=0..H-1): for each m in S_r, `kinkStageTransition(m,H,r,ms=0,
  maxn=BIG,emit)` -> up to 2 successors (m',shift in {0,1}); index m' in S_{r+1};
  record sparse edge (midx[r][m] -> midx[r+1][m'], shift). (<=2 edges per src.)
- Finalize: for each m in S_H: if !m.b[H+3] skip (empty column = completion);
  outgoing=m.b[H+2]; t=m; t.b[H+2]=t.b[H+3]=0; if outgoing && !labelInMixedState(
  t,H,outgoing) skip; canonicalizeSig(t.b,H); t.b[H]=t.b[H+1]=0; -> boundary;
  record edge (midx[H][m] -> bidx[boundary]).
- Closure: new boundaries from finalize -> new seeds -> propagate; BFS to fixed
  point. (Bootstrap by seeding the empty Sig to get the single-column boundaries.)

**Matvec M(x)*wb (dense arrays, all sparse ops):**
- v0[midx0(b)] = wb[bidx(b)]  (seed, 1:1)
- for r=0..H-1: v_{r+1}[dst] += x^shift * v_r[src]   over T_r edges
- wb'[bidx(bnd)] += v_H[src]   over finalize edges

**Root find:** secant on rho(x)-1 (rho = dominant eigenvalue via warm-started
power iteration on wb), ~6 evals not 55. mu_H = 1/x*.

**Cost estimate (H=16):** |B|~2M, sum|S_r|~20-40M, edges ~2x that (~few 100MB as
int arrays), matvec ~ H*sum|S_r| ~ 1e8-1e9 flops; ~30 matvecs (secant+warm) ->
seconds-to-minutes. H=16-20 feasible.

## Rigor: certified lower bound (Collatz-Wielandt)

Power iteration gives a numerical mu_H (same status as Bacher's 6.475). To make it
a CERTIFIED rigorous bound: for a positive vector v, `min_i (M(x)v)_i / v_i <=
rho(M(x)) <= max_i (M(x)v)_i / v_i`. Use the min-ratio (a guaranteed LOWER bound
on rho) with the converged eigenvector: find an x where the CW lower bound on
rho(M(x)) is >= 1; then rho >= 1 at that x, so x >= true radius, so
mu_H = 1/radius >= 1/x — a rigorous lower bound on mu_H, hence on lambda.
(Pin the inequality directions carefully at implementation; do exact rational or
interval arithmetic on the final min-ratio for a fully certified digit.)

## Validation procedure

Any rewrite MUST reproduce the exact ladder above (mu_2..mu_13) to ~7 digits
before trusting new H. `build/strip_mu_kink 2 13` is the slow-but-correct
reference; diff against it.

## Expected outcomes if resumed

- mu_16 ~ 6.50 -> beats 6.475 (best rigorous lambda lower bound, ours, certifiable).
- mu_18-20 ~ 6.6 -> lambda >= ~6.6 rigorously.
- Sharper independent lambda estimate (two methods agree near 7.11).
- Ceiling: bound never tight (~6.6 vs true ~7.11); estimate gains corroboration
  not many digits; does NOT advance a(n) reach. (Why it was deprioritized.)
