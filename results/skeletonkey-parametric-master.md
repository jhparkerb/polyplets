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
the pin against published square-lattice counts, which reach `n = 70` and not
the `n = 56` this file first said (`results/literature-record-56-corrected.md`). The law covers
`H ≥ (n+1)/2`; the rest of each row is below onset and must be enumerated, so
`n = 56` needs square cells at `H ≤ 28`. That is somebody's enumeration, not a
free ride. What is actually available is an external prediction test as far as
our own square enumeration plus the tower can reach — worth having, and much
cheaper than the king ladder, but not "a square-lattice `D_j` derivation, not
machine time" as §1b puts it.

## The wired route, and 171 cancellations — added 2026-08-20

Gate K above checks king `A_3` against the **wired** `P_k` rather than against
a banked `A_k`. That construction was written for `k = 3`, but nothing in it is
specific to `k = 3`: it runs at every `k` the wired diagonal table reaches,
which is `k ≤ 19`, and it computes no cluster weight at all. `--wired-only` is that half
on its own, and it returns in under a second.

Two things fall out of running it.

**The two grand-form constants per level, for king, to `k = 19`.** `c_k(n) =
A_k n + B_k`:

| k | A_k | B_k |
|---|---|---|
| 1 | 25 | −45 |
| 2 | −209/2 | −891/2 |
| 3 | 4474/3 | −10350 |
| 4 | −22701/4 | −846963/4 |
| 5 | 16144 | −3781134 |
| 6 | 15126941/3 | −119091015 |
| 7 | −687296991/7 | −14478715359/7 |
| 8 | 16995497259/8 | −422154856107/8 |
| 9 | −74756868461/9 | −1487291768649 |
| 10 | 987107242503/5 | −157865366062953/5 |
| 11 | −167395577383614/11 | −5691866601417228/11 |
| 12 | 2763085221702553/2 | −70608382970548959/2 |
| 13 | −720698320820505951/13 | 725307892812247635/13 |
| 14 | 23806059560272857169/14 | −336304442725786678509/14 |
| 15 | −493233295413187159171/15 | −211243195829544461505 |
| 16 | 4737043349049134006715/16 | −48607562060310698638155/16 |
| 17 | 166978491890346163441779/17 | −7614668303432519358253869/17 |
| 18 | −8798698594866651300807629/18 | 1842210899412762378532347/2 |
| 19 | 215000982004527315731741127/19 | −3197921036512955745255968241/19 |

`k·A_k` is an integer at every one of the nineteen orders. The sign of `A_k`
alternates except between `k = 5, 6` and between `k = 16, 17`; both are stated
as properties of the table, with no explanation offered.

**171 coefficient cancellations, as an audit of the table.** `c_k` is assembled
from `P_1 … P_k`, of degrees `1 … k`, so it is generically degree `k` in `n`.
The gas requires it to be linear, which is `k − 1` vanishing coefficients at
order `k` and `Σ_{k ≤ 19} (k−1) = 171` in all. All 171 hold.

That is a consistency check between two things established separately:
extensivity `c_k = A_k n + B_k` is a consequence of the grand form (proved,
Lean-complete, `docs/proofs/grand-form.md`), while the wired `P_k` were fitted
from swept cells. `experiments/gas_cumulants.py` already tests linearity, but
it builds `P_k` from the drift-parametric DP and can only afford `k ≤ 2` for
king (`KMAX` in that file). Off the wired table the same test reaches `k = 19`.

**RED, and the scope.** Adding 1 to `P_19`'s `n²` coefficient breaks linearity,
so the audit has teeth. It does not have total teeth, and the second control
says so rather than leaving it to be assumed: a perturbation of `P_k`'s
**constant** term enters `c_k` as a constant, and one of its `n¹` term enters
as a slope, so neither can ever disturb linearity — the run asserts this by
bumping `P_19`'s constant term and requiring that nothing breaks. The audit
therefore pins the `n² … n^k` coefficients of each `P_k`, `k − 1` of its `k + 1`
coefficients, and says nothing whatever about the other two.

**What this does for `k = 4`.** King `A_4 = −22701/4` was a target, not a
prediction: the `K = 4` run of the weights route had to reproduce it, from
cluster weights that share no code with the wired table. Hex had no wired
table, so hex `A_4 = 3915/4` was a prediction with nothing to land on — see
the second route below.

### The `k = 4` run: the two routes agree (2026-08-20)

The king leg finished. From the cluster weights alone,

    king  b = 3   A_k = 25, −209/2, 4474/3, −22701/4

and the fourth entry is the wired table's number, to the fraction. Two routes
that share no code — one summing cluster weights over the gas, one reading the
production `P_k` table — land on `−22701/4`.

Two further checks came out of the same run:

    gate K   wired P_1..P_3 give c_3 = 4474/3 n − 10350; the slope is A_3
             from the weights
    RED      moving W(2,2) from 12 to 13 moves square A_k to
             4, −18, 388/3, −1014 — the fit does depend on the weights

The four-row king clusters are what cost: `(2,2,2,2) = 68314` took 6621 s,
against `(2,3,2) = 18308` and `(2,2,3) = (3,2,2) = 13459`. Nine cumulant
slopes were reproduced from the weights alone.

### Hex `A_4`: the second route agrees (2026-09-05)

The missing hex table was built rather than waited for.
`experiments/hex_diag_deep.py` re-runs `hex_gas.py`'s row-transfer DP with the
surplus budget raised from 2 to 6 — the old transition step takes every subset
of a window and does not finish at budget 4, so the new row is generated left
to right with two exact prunes — and it produces `T_hex(n, n−k)` for `k ≤ 6`,
`H ≤ 20`, in 19 s. The cells are banked in `results/hex_diagonal_cells.txt`.
Fitting `T_hex(n, n−k) = P_k(n)·2^(n−1−3k)` on them gives `P_1 … P_6` with 72
holdout cells all exact, and the cumulants `c_k = A_k n + B_k` come out linear
as the gas requires:

| k | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| `A_k` | 9 | −37/2 | 32 | **3915/4** | −103671/5 | 968878/3 |

`A_4 = 3915/4` — the weights-route number, to the fraction. The two routes
share no code: one sums cluster weights over the gas, the other fits a
polynomial to an enumerated triangle. `A_1`, `A_2`, `A_3` and `P_3` reproduce
the drift-parametric DP of `docs/proofs/universal-diagonal-law.md`, which is
the control that the fit is reading the same object. `A_5` and `A_6` are new,
and are targets the weights route can now be run against.

## The below-onset `D_1` is parametric too (2026-09-05)

`experiments/depth1_parametric.py`. `results/onset-defect-depth1-closed.md`
closes depth 1 on king; every piece of it is written for king adjacency. Taking
the drift set `D` as the parameter (square `{0}`, hex `{−1,0}`, king `{−1,0,1}`)
moves the whole construction across.

**Derived.** The gap walk's generic row is counting, not fitting. A new pair at
gap `gp` far from the old pair has `2|D ∪ (D−gp)|` placements, of which
`2|D ∩ (D−gp)|` leave the pair joined; near the old gap the two ends can touch
different old cells, which happens with the autocorrelation weight `k_d` of `D`,
and those were already counted once, so class P loses `2k_d` where J gains
`k_d`. The bulk block is therefore the autocorrelation of `D`, i.e. the kernel
is `u^(b−1) − y·(1 + u + … + u^(b−1))²`, and the *only* rows that are not this
template are the finitely many gaps `g < b`: two for king, one for hex, none at
all for square. The assembly identity (II) is the same substitution as this
file's: `D_1(k) = [y^k]( P̂ − B²/(b + S) )`, with `b` where the king note has 3.
The script checks the template against the enumerated table on all three
lattices and refuses a non-interval drift set.

**Square, derived.** With `b = 1` the walk closes on two states — the J-mass at
gap 1 triples each row, and no P-state ever returns — so
`S = 4y/(1−3y)`, `B = (1−y)/(1−3y)`, `P̂ = y/(1−3y)`, and

    F_1 = P̂ − B²/(1+S) = −1/(1+y),   hence   D_1(k) = (−1)^(k+1),  k ≥ 1.

`results/undertow-square-validation.md` had this from five measured values plus
the obvious pattern; it is now a consequence of the identity, for every `k`.

**Hex, derived.** With `b = 2` the kernel `u − y(1+u)²` has one small root
`u₁ = (1−A)/(1+A)`, `A = √(1−4y)`, and the closure has four unknowns —
J-mass at gaps 1 and 2, total J-mass at gaps ≥ 2, and P-mass at gap 2, P-mass
at gap 1 being identically zero. Solving it gives `F_1` in `Q(A)`, so `F_1` is
quadratic over `Q(y)` where king's is quartic. In the king normalisation
`y = bx`, `N = b·F_1(bx) + 1`:

    Φ_hex(x, W) = (8x−1)(8x²−9x+3)·W² − (2x−1)(8x−1)·W + x

with branch point `x = 1/8 = 1/b³` against king's `1/27`. `N_k = 2^(k+1) D_1(k)`
is integral — `1, 7, 45, 303, 2133, 15447, 113869, …`, not in OEIS (2026-09-05)
— and `Φ_hex` annihilates it through `x^25`.

**Hex onset sharpness, proved.** `Φ_hex ≡ (W+1)((1+x)W + x)` in `F_2[x, W]`.
`F_2[[x]]` is a domain, `N(0) = 0` kills the first factor, so `(1+x)N̄ = x` and
`N_k` is odd for every `k ≥ 1`. Hence `D_1(k) ≠ 0` and the hex onset
`n ≥ 2k+1` is sharp — the same argument, and the same shape of factorisation,
as the king mod-3 proof of `onset-defect-depth1-closed.md` §3. On the square
lattice `N(x) = x/(1+x)` outright, which is what both of the others reduce to
mod `b`.

**Checked.** The parametric walk reproduces `experiments/depth1_gap_walk.py` for
king at `k ≤ 20`; the square closed form against the enumerated walk to `k = 25`;
the hex closed form against the walk to `k = 25` and against
`T_hex(2k,k) − P_k(2k)/2^(k+1)` from the enumerated triangle at `k ≤ 6`. RED:
`b → b+1` breaks all three lattices, a perturbed `N_3` is not annihilated, and
the template is refused by a non-interval `D`.

## NOT ESTABLISHED

- **`B_k` from the weights.** Only the slopes `A_k` come from `log H`; the
  constants need `C(u)`, which this does not touch. The `B_k` tabulated above
  come from the wired `P_k` instead, so they exist for king only and carry no
  cross-route agreement — the weights route has never produced one.
- **Depth `j ≥ 2` on any lattice but king.** Depth 1 is now parametric, but the
  bounded-excess family DP (`cpp/severance_w3_families.cpp`) that supplies
  `D_2` and below is a different machine from the gap walk, and remains
  king-only in both its Python original and its C++ port. The square targets
  `−4, 8, −3, 10, −1` of `results/undertow-square-depth2.md` are still
  unclaimed.
- **The `A_k` beyond the enumeration.** Hex now has a table to `k = 6` and the
  weights route has been run to `k = 4`; `A_5` and `A_6` are one-route numbers
  the other way round, waiting on a `K = 5` weights run.
