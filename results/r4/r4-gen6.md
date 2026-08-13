# r4-gen6 — manufacturing an oracle above H = 16

GENERATOR, round 4. Replacement for `r4-gen4`. Angle assigned by the lead:
**the campaign's sharpest admitted weakness is that it has no oracle above
H = 16 — manufacture one.**

Rows are appended to `results/r4/queue.md` as `R4-G61 .. R4-G6nn`. Nothing here
re-files an `R4-G*`, `R4-G2-*`, `R4-G3-*` or `R4-G4*` row; where I would have,
I file the successor or the kill and cite the row.

**Headline, and it is a refutation of the premise I was given:** an
incumbent-free oracle above H = 16 already exists in this repository, it is
Lean-verified, it costs 26 ms, and I ran it tonight against
`results/triangle.txt`: **142 near-diagonal cells, H = 4..37, zero
mismatches**, including all twenty at H = 17..21 and the top-right corner
T(40,37).

---

## §1 — The oracle, run tonight

### 1.1 What it is

`docs/proofs/diagonal-law.md` Step 2 proves an exact chain identity for
king animals read row by row: walk rows (one cell) cut the animal, clusters
(maximal runs of rows with ≥ 2 cells) are finite local objects, and the
generating function factors. `polyplets/Polyplets/Weights.lean` turns the
cluster weights into named Lean theorems over an ab initio definition of the
objects:

    V  1 1 = 25    Vt 1 1 = 5
    V  1 2 = 49    Vt 1 2 = 7
    V  2 2 = 339   Vt 2 2 = 66
    V  1 3 = 81    Vt 1 3 = 9
    V  2 3 = 1860  Vt 2 3 = 307      (Weights3.lean)
    V  3 3 = 4778  Vt 3 3 = 919      (Weights3Heavy.lean)

`V(ℓ,j)` is the aggregated interior weight of all surplus-`j` clusters with `ℓ`
rows; `Vt(ℓ,j)` the edge weight. The same file carries the recursion as a
checked theorem (`d_rec_check_k2_H4`, `d_rec_check_k1_H3`), and Weights.lean's
own worked line is `1019 = 3·136 + 25·5 + 49·3 + 339·1`.

Reconstructed from those two theorems, with `d(k,H)` = animals of height `H`
and surplus `k = n − H` whose top row is a walk row:

    d(k,0) = [k = 0],   d(0,H) = 3^(H-1)
    d(k,H) = 3·d(k,H−1) + Σ_{ℓ,j ≤ k} W(ℓ,j) · d(k−j, H−1−ℓ)
             where W = V(ℓ,j) when H−1−ℓ ≥ 1,  W = Vt(ℓ,j) when H−1−ℓ = 0
                                                (bottom edge, no cell below)

    T(H+k, H) = d(k,H) + Σ_{ℓ,j ≤ k} Vt(ℓ,j) · d(k−j, H−ℓ)        [H ≥ 4]

The `H ≥ 4` guard is because the *pure* weights `W^p` (animal = one cluster, no
walk row at all) are not in the aggregated table; the pure term fires only when
`H − ℓ = 0`, i.e. `H ≤ 3` at `ℓ ≤ 3`. Above H = 3 it is inert, so the
restriction costs nothing at the heights that matter.

### 1.2 The run — MEASURED, tonight, sub-second desk arithmetic

Exact integer arithmetic against `results/triangle.txt` (assembled from the
a(40) production run, `results/ns_a40/perheight`). Committed as
`experiments/tristruct/r4_gen6_weight_oracle.py`, log alongside:
**142 of 142 cells match, zero mismatches, 26 ms wall** — every cell with
`k = 0..3` and `4 ≤ H ≤ 37`, which is the whole near-diagonal of the table
from H = 4 up to the top-right corner T(40,37). The twenty at the band's
heights:

| k | H | n | ab initio T(H+k,H) | vs banked |
|--:|--:|--:|---|---|
| 0 | 17 | 17 | 43,046,721 | match |
| 0 | 18 | 18 | 129,140,163 | match |
| 0 | 19 | 19 | 387,420,489 | match |
| 0 | 20 | 20 | 1,162,261,467 | match |
| 0 | 21 | 21 | 3,486,784,401 | match |
| 1 | 17 | 18 | 1,937,102,445 | match |
| 1 | 18 | 19 | 6,170,030,010 | match |
| 1 | 19 | 20 | 19,586,258,055 | match |
| 1 | 20 | 21 | 61,987,278,240 | match |
| 1 | 21 | 22 | 195,647,346,945 | match |
| 2 | 17 | 19 | **47,839,787,379** | match |
| 2 | 18 | 20 | **160,989,953,571** | match |
| 2 | 19 | 21 | **538,370,990,640** | match |
| 2 | 20 | 22 | **1,790,284,428,576** | match |
| 2 | 21 | 23 | **5,923,271,856,321** | match |
| 3 | 17 | 20 | **860,061,675,780** | match |
| 3 | 18 | 21 | **3,044,407,243,896** | match |
| 3 | 19 | 22 | **10,682,543,902,131** | match |
| 3 | 20 | 23 | **37,190,476,076,922** | match |
| 3 | 21 | 24 | **128,559,328,810,578** | match |

The ten bolded cells (`k = 2, 3`) are the genuinely new ones. `k = 0` and
`k = 1` were already enforced by the assembler — `results/triangle.txt`'s own
header says it checks `T(n,n) = 3^(n−1)` and `T(n,n−1) = (25n−45)·3^(n−4)` —
so those five-plus-five are re-confirmation, not new information.
**Ten cells at H = 17..21 were checked by nothing before tonight.**

### 1.3 Why this is incumbent-free, stated precisely

The value chain is: `diagonal-law.md` (proved theorem, chain identity) +
`grand-form.md` (proved theorem, exact resummation) + six Lean-checked integer
constants + `3^(H−1)`. No transfer matrix, no B1, no strip engine, no spin
engine, no fitted polynomial, no line of Go or C++ from the production tree.

The residual common mode is the one the campaign has already named and cannot
remove by any method (`R4-G2-18`, `R4-G3-19`): both sides assume the same
definition of king adjacency. Weights.lean defines it independently in
`Compute.lean`, so even that is two *statements* of one definition rather than
one implementation used twice.

**Caveat, and it is the weakest link:** the Lean weight values are
`native_decide`, not kernel `decide` — the extended trusted base that
`R4-G3-16` closed as insufficient for the (b)→(c) bridge. They are separately
cross-checked by direct enumeration (`results/defect-gas.md`: "validated
against all 21 enumerated weights") and by `experiments/cluster_weight_dp.py`.
See `R4-G613` for the one gap in that cross-check that is *not* covered.

### 1.4 What r4-spinproj §3.1 and R4-G2-19 should now say

`r4-spinproj.md` §3.1: "there is no oracle above H=16, none." **False as
written.** `R4-G2-19`: "every incumbent-free oracle in this campaign runs at
small H." **False as written**, and it was false before I ran anything —
`experiments/grand_form_check.py` line 233 loops `for H in range(k+1, 20)`
against `results/ns_a36/perheight/h{H}.out`, so a committed, ab-initio,
Lean-weight check has been validating T(H+k,H) at **H = 17, 18, 19** for
k ≤ 3 since 2026-07-21. What is true is the weaker and still-serious claim:
**no oracle above H = 16 reaches large n.** See §3.

Two arbitrary constants are all that stood between that checker and the top of
the band: `KMAX = 3` (line 27) and the literal `20` in `range(1, 20)` /
`range(k+1, 20)`. Neither is a limit of the mathematics. See `R4-G62`.

---

## §2 — How far the oracle reaches, and what it costs

### 2.1 Reach in k, from the banked weight measurements

`results/defect-gas.md` §"The weight DP, k ≤ 5 ab initio" measured the cost of
producing the weight tier itself (`experiments/cluster_weight_dp.py`, Python):

| surplus tier k | cost to produce the weights | basis |
|---|---|---|
| ≤ 3 | already Lean theorems, zero | `Weights*.lean` |
| ≤ 5 | already tabulated (`KNOWN_WEIGHTS`, 31 types), ms | MEASURED, defect-gas |
| 6 | > 530 s, killed incomplete | MEASURED, defect-gas |
| ~7 | hours (Python) | EXTRAPOLATED, defect-gas' own verdict |
| ~9–10 | C++ rewrite plus effort | EXTRAPOLATED, defect-gas' own verdict |
| 17 | ~10^17 s — **dead, priced and killed** | defect-gas, "P₁₇ from the gas is DEAD" |

The reach in `k` is a property of the cluster catalogue only. **It does not
depend on H at all** — that is the whole point of the instrument, and it is why
it is the one thing in the campaign that gets *more* valuable as H rises.

### 2.2 The band, cell by cell

The band is H = 17..21 at n = H..40: **110 cells**.

| instrument | cells it reaches, H = 17..21 | cost |
|---|---|---|
| assembler identities (k = 0,1) | 10 | free, already done |
| **Lean weights j ≤ 3 (k ≤ 3)** | **20** | **free, done tonight** |
| `KNOWN_WEIGHTS` k ≤ 5 | 30 | ms, needs a driver (`R4-G63`) |
| weight DP to k ≤ 7 | 40 | hours of Python |
| C++ weight DP to k ≤ 9 | 50 | a real build |
| everything else incumbent-free | **0** | — |

So **30 of 110 band cells are free today**, 40 for an afternoon, and the
remaining 60 — every cell with n ≥ H + 8, which is where all of the count
lives — are reachable by nothing incumbent-free at any price this project has
found. **T(40,17) … T(40,21) remain untouched by this and by everything else.**

### 2.3 The n = 40 corner nobody costed

`k = n − H` at n = 40 means H = 40 − k. So the same oracle reaches, exactly and
ab initio, **six cells of row 40**:

| H | k | T(40,H) |
|--:|--:|---|
| 40 | 0 | 4,052,555,153,018,976,267 |
| 39 | 1 | 143,340,376,708,634,160,555 |
| 38 | 2 | 2,509,287,671,955,797,860,401 |
| 37 | 3 | 28,988,633,422,018,953,978,570 |
| 36 | 4 | 248,639,909,528,376,343,574,055 |
| 35 | 5 | 1,688,999,770,099,402,820,172,396 |

H = 40..37 is free right now (Lean j ≤ 3) — **and the run in §1.2 has already
done it**: the 142-cell sweep includes T(40,37), T(39,36), T(38,35) and every
other `k ≤ 3` cell up to the corner, all matching. H = 36, 35 needs the k ≤ 5
driver; H = 34, 33 needs the hours-of-Python tier.

Their share of a(40) is **0.0000%** to four decimals (0.0016% even at k ≤ 9) —
I am not going to dress that up. The value is not share, it is **coverage of a
path with zero coverage**: `R4-G3-09` established that H = 22..40 at n = 40 is
produced by *evaluating wired P_k*, never counted, and `R4-G42` established
that this 4.14% block has no confirmation of any kind. Six of its nineteen
cells become exactly confirmed, at n = 40, by a route that shares no code with
the evaluator. That is the first test of the closed-form injection arithmetic
at production n. See `R4-G616`.

---

## §3 — What the oracle catches, adversarially

This is the section that decides whether the instrument is worth advertising.
An oracle that cannot see the error class it is sold against buys false
confidence, so here is the honest matrix. "Near-diagonal" means the cells of
§1.2 and §2.2: H = 17..21, surplus k ≤ 5, counts ≤ 3×10^16.

| error class | does the near-diagonal oracle at H = 17..21 expose it? |
|---|---|
| **Height mis-attribution** — a swept animal landing in `h{H±1}.out` | **YES, decisively.** This is `R4-G3-06` (its RANK 1: "nothing anywhere tests which height a swept animal was attributed to") and `R4-G45` ("corroborated only at n ≤ 12"). A ±1 attribution slip at H = 17..21 moves values by factors of ~3 to ~30 and cannot cancel: the oracle is per-cell and exact. **These two rows are closed at H = 17..21 for n ≤ H+3 by tonight's run**, and for n ≤ H+5 by `R4-G63`. |
| **H-indexed stencil or guard error** — `R4-G2-19`'s named blind spot | **PARTLY.** The oracle runs at the real H, so anything keyed on the height index is exercised. But near-diagonal animals are almost all walk rows: they hammer the three diagonal/vertical king steps and touch dense-row adjacency only inside clusters of ≤ 5 surplus cells. A stencil bug in, say, the 4-cells-in-a-row case is invisible here. |
| **State-space truncation that bites above some H** | **PARTLY.** A height-H near-diagonal animal still spans up to H columns (see `R4-G68`), so the column sweep's full-height frontier is exercised — but only at *low occupancy*. Truncation triggered by dense frontiers is invisible. |
| **Rank/carry error at high m** | **NO.** Counts here top out at 1.3×10^14 (H=21, k=3); the band's real cells run to 10^30. Nothing about wide-integer handling is tested. |
| **Shard-cut duplication at n = 40** (`R4-G3-10` RANK 2) | **NO.** Wrong n. |
| **Combine/harvest path errors** | **NO** — and they are already covered by `R4-G3-01`/`R4-G3-02`. |
| **The closed-form injection evaluator at n = 40** | **YES for k ≤ 5**, and nothing else tests it at all (§2.3). An error in the *evaluation code* is likely k-uniform and would be caught; an error in the *coefficients* of P_10..P_18 would not. |
| **The B1 rule at H = 17, 18, 19** | **YES**, once the ladder lands — free acceptance test, available before the run. See `R4-G611`. |
| **The spin engine at H = 20, 21** | **YES** — the only oracle those two heights will ever have before INV-8 is trusted. See `R4-G612`. |

Summary in one line: **the instrument buys height coverage and buys zero size
coverage.** It closes the campaign's RANK 1 open item at the heights that
matter and leaves the bulk of T(40,17..21) exactly as unconfirmed as it was.

---

## §4 — The other routes, priced and mostly killed

### 4.1 Direct enumeration by size — the wall, MEASURED off the triangle

Row sums of `results/triangle.txt`, with the plan's own tree factor
(`docs/redelmeier-tall-plan.md` §5: "whole-row enumeration cost ≈ 1.17·a(n)"):

| n | a(n) | whole-row cost, objects |
|--:|---|---|
| 18 | 2.247e13 | 2.6e13 |
| 19 | 1.516e14 | 1.8e14 |
| 20 | 1.026e15 | 1.2e15 |
| 21 | 6.954e15 | 8.1e15 |
| 22 | 4.726e16 | 5.5e16 — **ran** (`results/redelmeier_row22`) |
| 23 | 3.217e17 | 3.8e17 |

The plan's banked fleet budget is ~10^16 objects per fleet-week, and n = 22 was
actually done. So the whole-row wall sits at **n = 22, already spent**, and
n = 23 is ~7× beyond it. Height-restricted `--height H` (the plan's §1) prunes
to roughly the near-diagonal count itself, so its wall is where T(H+k,H)
crosses ~10^15–10^16: at H = 21 that is k = 3 (1.3e14, hours) to k = 4
(2.2e15, a fleet-day), and k = 5 (3.3e16) is out.

**Which kills the plan's own target list.** `docs/redelmeier-tall-plan.md` §4
names five targets — T(28,28), T(25,24), T(23,21), T(21,18), T(20,16) — at
k = 0, 1, 2, 3, 4. Every one of them is inside the ab initio weight oracle,
which produces them in milliseconds instead of fleet-days, exactly, with a
proof attached. Three of them (T(23,21), T(21,18), plus k=2 at H=17..21) I
computed tonight. See `R4-G66`.

### 4.2 The width-limited / transposed strip route — DEAD, and the reason is
worth keeping

The tempting inference, and I spent real effort on it before killing it: an
animal of height H = n − k has k spare cells, so it should be narrow, so the
row-sweep transfer matrix on a strip of width ≤ k+1 should make the band's
heights the cheap axis. **False for king adjacency.** T(n,n) = 3^(n−1) counts
staircases: n cells, height n, and width up to n, because each successive row
may step left, straight, or right. The bound `W ≤ n − H + 1` is a *rook*
theorem (a rook-connected animal spanning H rows and W columns needs
H + W − 1 cells); king adjacency has no such constraint, only `max(H,W) ≤ n`.
So the strip engine transposed does not reach high H, and the H≤14 strip second
source cannot be re-pointed at the band. See `R4-G68`.

### 4.3 The row-22 histogram that was thrown away

`results/redelmeier_row22/combined.txt` is two columns, `n count`. The g2 tool
has `--per-box` (emits `n w h count`) and `docs/terminal-velocity.md` line 88
records a gate that compares the aggregate path against per-box row sums — so
the machinery existed and ran, and the height-resolved histogram of the a(22)
whole-row enumeration was discarded. Recovering it means re-running a
5.5e16-object job. See `R4-G67`.

---

## §5 — Rows

Filed to `results/r4/queue.md` as `R4-G61 … R4-G620`.

`R4-G61 … R4-G620`, twenty rows: the flagship and its run (`R4-G61`), the
checker that was already doing it (`R4-G62`), one job request (`R4-G63`), the
coverage map (`R4-G64`), the adversarial matrix (`R4-G65`), three kills filed
with their kills (`R4-G66`, `R4-G68`, and the bounded half of `R4-G69`), the
standing gate (`R4-G610`), two pre-registrations (`R4-G611`, `R4-G612`), the
weak link (`R4-G613`), the stencil retarget (`R4-G614`), the discipline row
against my own flagship (`R4-G615`), row 40 (`R4-G616`), and four broadening
rows (`R4-G617` … `R4-G620`).

### Job request G6-JOB-1 (row `R4-G63`)

- **What:** emit the aggregated interior/edge cluster weights `V(ℓ,j)`,
  `Vt(ℓ,j)` for `j = 4, 5` by summing `KNOWN_WEIGHTS` in
  `experiments/cluster_weight_dp.py` over types with `ℓ` rows and surplus `j`,
  then re-run `experiments/tristruct/r4_gen6_weight_oracle.py` with `V`/`VT`
  extended and `KMAX = 5`.
- **Where:** gympie. It is milliseconds and touches nothing.
- **Cost:** MEASURED-adjacent — `results/defect-gas.md` records the k ≤ 5 tier
  (31 types) as already tabulated and `check_grand_form()` as running "in ms".
  If `KNOWN_WEIGHTS` turns out to hold only interior weights, the boundary
  tier needs `boundary()` (line 131) run at `j = 4, 5`: defect-gas measured the
  full-tier DP at k=4 = 3.1 s, k=5 = 65 s. Worst case ~70 s.
- **Guard, and it is required, not optional (`R4-G613`):** assert
  `V(2,3) == 930 + 930 == 1860`, `V(3,3) == 4778`, `V(1,j) == (2j+1)^2` before
  trusting any j = 4, 5 value. The three Lean values must fall out of the
  aggregation, or the aggregation is wrong.
- **Decision it changes:** whether `R4-G3-06` (height attribution, its own
  RANK 1) and `R4-G45` close at `n ≤ H+3` or `n ≤ H+5` for H = 17..21, and
  whether T(40,36) and T(40,35) join the six confirmed row-40 cells.
- **Failure mode to watch:** a mismatch at `k = 4, 5` against
  `results/triangle.txt` is a **finding**, not a bug in the driver. Stop and
  report; do not tune the weights toward the banked value.
