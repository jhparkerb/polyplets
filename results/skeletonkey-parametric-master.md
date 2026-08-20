# The master equation is lattice-parametric, and the substitution is 3 -> b

2026-08-20, branch `skeletonkey`. Probe
`experiments/skeletonkey/parametric_master.py`. Desk arithmetic, no compute.

`docs/proofs/universal-diagonal-law.md` §"The gas, made lattice-parametric"
(2026-08-06) ends with what it could not carry across:

> **What is still king-only:** assembling `c_k` for `k ≥ 2` *from* the cluster
> weights, i.e. `defect_gas.py`'s ledger and the master equation.

`docs/lastditch-ideas.md` §1b names that same gap as the blocker on running the
Undertow pin against an external oracle. It is one substitution.

## The substitution

`defect_gas.py`'s renewal chain is `1 = 3z + Σ_c W_c y^k z^{l+1}` at
`z = 1/μ`, i.e. `μ = 3 + Σ_c W_c y^k μ^{-l}`. The 3 there is the **drift-step
weight** — the number of continuations of a one-cell row — which for a
row-local lattice with drift set `D` is `b = |D|`, exactly as
`experiments/diagonal_machine.py` already computes it. Writing `μ = b·H` and
`u = y·μ/b³`:

    H(u) = 1 + Σ_c  Ŵ_c u^{k_c} H^{-(k_c + l_c)},
    Ŵ_c = W_c · b^{2 k_c − l_c − 1}

the king form with 3 → b throughout. And because the grand form gives
`F(n,u) = C(u)·H(u)^n`, `log F` is linear in `n` with slope `log H`, so the
cumulant slopes are

    A_k = [u^k] log H        (with c_k(n) = A_k n + B_k)

`cluster_weight(D, sizes)` in `experiments/gas_cumulants.py` is already
parametric, so nothing else is needed.

## Checked, three lattices

The `A_k` below were obtained in `universal-diagonal-law.md` by a
**drift-parametric DP over the triangle** — from the counts, not from the
weights. This route reaches them from the cluster weights alone. The two share
no code path.

| lattice | b | Ŵ inputs | `log H` | banked `c_k` slopes |
|---|---|---|---|---|
| square | 1 | 4, 9, 12, … | `4u − 19u² + (472/3)u³` | 4, −19, 472/3 |
| hex | 2 | 9, 64, 120, … | `9u − (37/2)u²` | 9, −37/2 |
| king | 3 | 25, 441, 1017, … | `25u − (209/2)u² + (4474/3)u³` | 25, −209/2 |

Worked by hand for square through `k = 3` before the probe was written:
`H = 1 + 4u − 11u² + 92u³`, whose log is `4u − 19u² + (472/3)u³`. The
`472/3` is the useful one — a non-integer that is not going to be hit by
accident.

King's `k = 3` is not in the banked table — `universal-diagonal-law.md` stops
at `k = 2` there — so the `4474/3` is a **prediction from the weights**, and it
is checked against the wired `P_k` instead. With
`P_1 = 25n − 45`, `P_2 = (625n² − 2459n + 1134)/2` and
`P_3 = (15625n³ − 100050n² + 122213n − 32940)/6`, the cumulant
`c_3 = P_3 − P_1P_2 + P_1³/3` has

    n³ :  15625(1/6 − 3/6 + 2/6)          = 0
    n² :  −16675 + 44800 − 28125          = 0
    n  :  (122213 − 417015 + 303750)/6    = 8948/6 = 4474/3

— linear, as the gas requires, with exactly the predicted slope. That is the
deepest check available: the wired king table and the cluster weights are as
far apart as two routes to `c_3` get.

Gates: cluster weights must match the banked table on all three lattices
before any `A_k` is computed; every `A_k` must match; and a RED control bumps
`W(2,2)` by one and requires the square slopes to move.

## What this unblocks, and what it does not

**Unblocked.** `P_k` on square and hex are now derivable from the weights to
any `k`, by the same machine that produces them for king. One of the two
pieces `universal-diagonal-law.md` called king-only is no longer king-only.

**Not unblocked — and §1b oversells this.** The headline there is validating
the pin against published square-lattice counts to `n = 56`. The law covers
`H ≥ (n+1)/2`; the rest of each row is below onset and must be enumerated, so
`n = 56` needs square cells at `H ≤ 28`. That is Jensen's computation, not a
free ride. What is actually available is an external prediction test as far as
our own square enumeration plus the tower can reach — worth having, and much
cheaper than the king ladder, but not "a square-lattice `D_j` derivation, not
machine time" as §1b puts it.

## NOT ESTABLISHED

- **`B_k`, the cumulant constants.** Only the slopes `A_k` come from `log H`;
  the constants need `C(u)`, which this does not touch.
- **The below-onset `D_j` on any lattice but king.** The bounded-excess family
  DP (`cpp/severance_w3_families.cpp`) is a different machine from the gas
  weights and has not been checked for lattice-parametricity here.
- **`k ≥ 4` on hex and king.** `universal-diagonal-law.md` banks square to
  `k = 4` and hex to `k = 3`; there is nothing to check king's `c_3` against.
