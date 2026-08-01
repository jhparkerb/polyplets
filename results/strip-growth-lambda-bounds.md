# Strip growth constants mu_H — a rigorous lower-bound ladder for lambda

Date: 2026-07-10. Shaken loose while exploring T(n,H). `mu_H` = dominant
eigenvalue of the height-H strip transfer matrix = top root of atom `q_H` =
`1/(smallest positive root of Q_H)` from the banked fixed-height GFs
(`results/fixed_height_gfs.txt`). Computed exactly (mpmath) in
`experiments/mu_H_from_atoms.py`.

## The numbers (exact strip growth constants, H<=13)

| H | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| mu_H | 2.4142 | 3.4437 | 4.1823 | 4.7178 | 5.1153 | 5.4178 | 5.6534 | 5.8405 | 5.9917 | 6.1158 | 6.2191 | 6.3061 | 6.3800 |

H<=11 from fixed-height GF roots; **H=12,13 newly computed by power iteration on
the strip transfer matrix** (`cpp/strip_mu.cpp`, `build/strip_mu`; validated: it
reproduces the GF-root mu_H exactly for H<=11). Increment ratios climb 0.72→0.84
(power-law decay, not geometric).

## Why this matters

**1. Rigorous, exact, monotone lower bounds on lambda.** Each strip grows strictly
slower than the plane, so `mu_H < lambda` rigorously, with `mu_H -> lambda`. Each
`mu_H` is an algebraic number (top root of `q_H`) — no numerical caveat, unlike
the multi-directed 6.475. Extrapolating the increments, `mu_H` crosses **6.475
around H~16** and reaches **~6.6 by H~18-20** — which would be the **best rigorous
lower bound on lambda we have**, beating both Bacher bounds (directed 5.828,
multi-directed 6.475), our own, and improvable with H.

> These `mu_H` bounds squeeze lambda from BELOW. The complementary rigorous UPPER
> bound is **lambda <= 9.3153** (Bui-style finite-type convolution certificate,
> exact rational arithmetic), giving the two-sided bracket
> **6.543 <= lambda <= 9.3153** (updated 2026-07-31: the lower end is now the
> certified ladder's mu_17, not Bacher's 5.828 — see the addendum below and
> `strip-mu-certificates.md`; both ends are machine-checkable in exact
> arithmetic). Derivation: [../docs/proofs/polyplet-upper-bound.md](../docs/proofs/polyplet-upper-bound.md).

   Current certified ladder tops at mu_17 >= 6.543 (`strip-mu-certificates.md`,
   addendum 2026-07-31) — the 6.475 crossover is passed.

> **Certificate grade, H<=11.** The `mu_H` below are floating-point power-iteration
> values. `cpp/strip_mu_cert.cpp` upgrades them to exact rationals verified in
> integer arithmetic (Collatz-Wielandt on the transfer operator at a rational x),
> with a per-H receipt in `results/strip_mu_certificates.log`. Done for H<=11;
> H=14 scheduled. Method, receipts and honest scope:
> [strip-mu-certificates.md](strip-mu-certificates.md).

**2. Independent lambda estimate (delivered, H<=13).** Sliding 3-point power-law
fit `mu_H = lambda - c*H^{-p}` (`experiments/lambda_from_mu.py`) gives lambda
estimates marching monotonically down as the center H rises:
`9.54, 8.41, 7.92, 7.66, 7.50, 7.40, 7.33, 7.29` (center H=5..12), with the
exponent `p -> ~1` (a 1/H finite-size correction). Converging straight toward the
`a(n)`-ratio value **~7.11** — a structurally **independent** second determination
(strip spectra vs row-sum ratios) corroborating the paper's single fit. Not yet
sharper than 7.11 (H<=13 too small; estimate still ~7.29 at H=12), but the
convergence is clean and monotone. This is the bankable paper result.

## Why it's cheap (the lever)

Higher `mu_H` needs neither enumeration nor the full atom — only the **dominant
eigenvalue** of the height-H strip transfer matrix, by **power iteration** on the
(sparse, structured) matrix `strip_tm.cpp` already builds. No counting, no
Berlekamp-Massey, no CRT. Power iteration to H~18-20 is far cheaper than the
counts and gives:
- the record rigorous lower bound on lambda (exact-ish, ~6.6+), and
- an independent finite-size lambda estimate for the paper.

## Caveat / honest state

- The count-ratio route to mu_H (T(n,H)/T(n-1,H)) is badly under-converged for
  H>~6 (at n=36, H=18 the ratio is 7.63 > lambda). Must use the eigenvalue /
  GF-root route, not count ratios. (`experiments/strip_growth_extrapolation.py`
  documents the under-convergence.)
- Extrapolation quality: full Richardson (1/H^2) gives 7.41, local two-point gives
  6.64-6.71 — they disagree, so higher-order corrections matter; H<=11 is too few
  for a controlled lambda estimate. The rigorous *lower bound* use needs no
  extrapolation and is immediately valid.

## Engine status & next

- **Done:** `cpp/strip_mu.cpp` — power iteration on the all-column strip transfer
  matrix, warm-started bisection. Reached H=13 (7.7 min; H=11:10s, H=12:67s,
  H=13:465s). Cost ~6x/H and edge memory ~states*2^H blow up, so this engine tops
  out ~H=13-14.
- **Rigorous-bound status:** mu_13 = 6.306 is a valid rigorous lower bound on
  lambda but still BELOW the multi-directed 6.475. Beating 6.475 needs mu_16
  (~6.5), i.e. H=16 — out of reach for the all-column engine.
- **Cell-at-a-time engine BUILT + VALIDATED** (`cpp/strip_mu_kink.cpp`): reuses
  the production `kinkStageTransition` (core/kink.h); one matvec = a column sweep
  (seed -> H per-cell stage transitions, weight x^placed, states merge ->
  finalize), `O(H*states)`, no 2^H, no edge storage. Reproduces mu_H exactly
  through H=11 (5.99…, 6.11…). Also `cpp/strip_mu8.cpp` (whole-column via the
  tma viable-mask kernel) validates but hits the same 2^H edge wall as strip_mu.
- **Indexed-array rewrite DONE** (`cpp/strip_mu_fast.cpp` + `cpp/strip_stage_ops.h`,
  `make build/strip_mu_fast`, gate `make gate-strip-fast`): the per-stage state
  graph is enumerated once and frozen into two int32 successor arrays per stage,
  so a matvec is a flat scatter instead of a hash-map rebuild. Measured **211x** at
  H=11 (107.5s -> 0.51s) and **231x** on the certificate path at H=12 (393.5s ->
  1.7s), with `mu_H` and state counts identical to the map engine for every H both
  can run, and every published certificate H<=12 re-verifying (PASS at the
  certified numerator, FAIL at numerator+1). Full note, cost model and RED-first
  gate: [strip-mu-fast.md](strip-mu-fast.md).
- **Reach, measured through H=16.** Table build and matvec throughput are measured
  at every H up to 16 (`--ops`, `--bench`): `sum|S_r|` grows a steady 2.95x/H to
  71.3M at H=16, the frozen tables are 564 MB, the build peaks at 4.9 GB, and the
  per-stage-state cost barely moves (0.89 -> 0.95 ns) — no cache cliff. Projected
  single-core wall: **H=14 16s / H=15 52s / H=16 ~3 min** for the float solve, and
  **~18s / ~58s / ~3.4 min** for the full certificate. The paragraph this replaces
  projected ~12h for the H=16 float solve. H>=13 solves are not run here; the
  numbers are wall-clock arithmetic over measured throughputs, for the
  orchestrator to schedule.
- **Where that lands the bound:** the ladder's own increments put `mu_16` at ~6.5,
  the first term to beat the multi-directed 6.475. H=14 is banked
  (**mu_14 = 6.3800344**, `results/strip_mu_H14.log`, 4851s on the map engine) and
  is still below it. What was "another build increment" is now an hours-free job.

## Chan–Rechnitzer 2018 read (2026-08-01): wrong direction, right machinery

`papers/chan_rechnitzer_2018_upper_bounds_growth_rates_corner_transfer_matrices.pdf`
(Linear Algebra Appl. 555 (2018) 139–156). Pulled as the most promising lead for
improving the loose half of our bracket, `lambda <= 9.3153`. **It cannot do that,
and the reason is worth recording because it is the connectivity wall again, from
a new angle.**

Their method: Calkin–Wilf's transfer-matrix eigenvalue upper bound
(`kappa^{2p} <= Lambda_o(2p)`, `Lambda_o(m)` the dominant eigenvalue of the
transfer matrix with *cylindrical* boundary conditions) combined with the
Collatz–Wielandt formula, the approximate eigenvector supplied by Baxter's corner
transfer matrix ansatz plus Nishino–Okunishi CTMRG. Applied to hard squares and
four other models, extending the rigorously known digits by 4–6.

**Why it does not transport.** They state four conditions for the method to apply.
Two of them fail for polyplets, and both fail on connectivity:

| condition | polyplets |
|---|---|
| transfer matrix from a **local face weight** `omega` (needed for the CTM formalism) | **fails** — connectivity is not a local face weight; our states carry component signatures precisely because it cannot be expressed locally |
| `V` **symmetric** (needed for the Calkin–Wilf bound itself) | **fails** — the signature transfer is directional; union-find merges are not reversible |
| non-negative | holds trivially |
| irreducible | holds — and by *our* argument: any state reaches the single-cell state through a spanning column. They use the identical empty-column trick |

Underneath the checklist is a normalization mismatch that no amount of
engineering fixes. `kappa` is a **per-site** growth rate for a lattice-gas model on
`N` sites; cylindrical boundary conditions over-count per site, which is exactly
what makes `Lambda_o(m)` an upper bound. `lambda` is a **per-cell** growth rate for
connected clusters, and confining animals to a cylinder of circumference `m`
strictly *loses* animals — it is our `mu_m`, a lower bound converging up. The
cylinder trick has no upper-bounding analogue for a connected family.

**So: the 9.3153 upper bound is not improvable by this route.** That is now two
independent method-classes floored above `lambda` for the same reason (this, and
the Bui-style convolution certificate whose over-count is diffuse and non-local —
`docs/certificate-squeeze-plan.md` P3). Treat the upper end as hard.

**What IS transferable, in the other direction.** Their engineering is that the
transfer matrix and the trial vector are both used *implicitly*: each component of
`psi` and `V psi` is computed independently and discarded, so the memory cost is
the tiny `F` matrices rather than the vector. That is what buys polynomial memory
and lets them run far larger `m` than direct methods. **Our ladder stopped at
H = 17 (6,536,381 states, 11.8 GB) for exactly the reason their method removes.**
Since we already use the *lower* half of Collatz–Wielandt for the `mu_H`
certificates, the architecture — never materialize the matrix or the vector,
generate components on demand from a compact representation — applies to us
unchanged.

The catch: their *ansatz* for `psi` comes from CTM formalism, which needs the
locality condition we fail. We would need our own compact representation of a
trial vector over connectivity-signature states, and connectivity is the thing
that makes those states non-local, so there is real reason to doubt a factored
form exists. **Unexplored, not endorsed.** If it worked, the prize is concrete:
the rungs gain ~0.05 each, so pushing H = 17 -> ~25 would move the certified floor
from 6.543 toward ~6.9 against `lambda ~ 7.111` — the bracket's lower end is the
half that is still moving.

### Oh cluster ruled out (2026-08-01)

Three papers checked, `papers/oh_*.pdf`: state matrix recursion + monomer–dimer
(Discrete Math. 342 (2019)), quantum knot mosaics (Topology Appl. 210 (2016)),
independent vertex sets in grid graphs (LAA 510 (2016)). **All three fail on both
counts identified above, so nothing here moves either end of the bracket.**

- **Per-site normalization, again.** Oh's constants are per-area: the knot mosaic
  constant is `delta = lim D_n^(1/n^2)`, the monomer–dimer and independent-set
  rates are per-site on an `m x n` lattice. Same mismatch as `kappa` vs `lambda`.
- **Local constraints, again.** The word "connected" in "suitably connected"
  mosaics is misleading and worth naming so nobody re-reads this hoping: a mosaic
  is suitably connected iff *any two tiles adjacent in a row or column have or
  lack connection points simultaneously on their common edge*. That is pure local
  edge-matching between neighbours — not global connectivity of a cluster. It is
  exactly the kind of compatibility rule a transfer matrix handles trivially, and
  it is why the method works there and not here.

No new engine idea either: the three-stage shape (convert to a mosaic system,
state-matrix recursion, analyze the matrix) is what our own stage-operator strip
kernel already does.

### The implicit-trial-vector thread: measured, and RULED OUT (2026-08-01)

Two measurements, one of which is a new structural fact worth keeping
independently of the verdict.

**1. Our frontier connectivity patterns are exactly NON-CROSSING** (new).
`experiments/strip_state_count_model.py` models an `S_0` state as: choose an
occupancy of the `H` rows (king adjacency forces each maximal vertical run into
one component), then partition the runs. Against the banked `S_0` counts:

| H | actual | runs x Catalan | runs x Bell |
|---|---|---|---|
| 9 | 2187 | 2188 | 2243 |
| 12 | 41834 | 41835 | 46905 |
| 16 | 2356778 | 2356779 | 3365627 |

**`actual = NC - 1` exactly at every H = 9..16** (the one is the separately-held
empty seed). The Bell column diverges immediately. So crossings never occur,
despite king diagonals crossing geometrically — and the reason is a one-liner:
a crossing needs edges `(r,c)-(r+1,c+1)` and `(r+1,c)-(r,c+1)`, which requires
all four cells occupied, and then `(r,c)`,`(r+1,c)` are vertically adjacent, so
the two "crossing" components were the same component all along. **The Temperley–
Lieb / loop-model structure is therefore available to us**, which is the
precondition a tensor-network trial vector would need. Banked as a fact; it is
also the honest answer to "is the king frontier planar", which was open.

**2. The precondition is met and the thread is still dead, because I had the
bottleneck wrong.** Chan–Rechnitzer's implicit-vector trick saves the memory of
`psi`. Our `psi` was never the constraint: at H = 17 it is ~18M entries, ~144 MB.
What binds is the **frozen transition tables** (8 bytes per stage-state over
`sum|S_r|`) and the **build transient** (~8.8x the table). Extrapolating the
measured 2.95x/H:

| H | `sum\|S_r\|` | table | build RSS | float matvec | exact sweep |
|---|---|---|---|---|---|
| 18 | 6.2e8 | 4.9 GB | ~43 GB | 0.6 s | 5 s |
| 19 | 1.8e9 | 14.5 GB | ~127 GB | 1.7 s | 14 s |
| 20 | 5.4e9 | 42.7 GB | ~374 GB | 5.1 s | 42 s |

Making the *tables* implicit instead — recomputing transitions per column — is
precisely what the old map engine did, and the frozen-table rewrite bought
**211x** for exactly that (`strip-mu-fast.md`). Trading it back puts time into
the wall immediately. So there is no version of the Chan–Rechnitzer trick that
helps here: the memory it saves is not the memory we are short of.

**What is actually reachable, with no new method at all:** H = 18 wants ~43 GB of
build transient and a 5-second exact sweep — a big-RAM box today, existing engine,
one command. That lands `mu_18 ~ 6.59`. H = 19 at ~127 GB is marginal; H = 20 at
~374 GB is out.

**Recommendation: don't.** 6.543 -> 6.59 against `lambda ~ 7.111` does not
shorten the paper's sentence, it only edits a numeral in it, and the rung
increments (~0.05) mean the ladder cannot approach `lambda` at any H we can
build. The bracket is what it is. Recorded so the next person costs it in
minutes instead of re-deriving the table.

### Bevan–Brignall–Elvey Price–Pantone 2020, read (2026-08-01)

`papers/bevan_brignall_pantone_2020_av1324_growth_rate_bounds.pdf`, EJC 88 (2020)
103115. The last candidate that was not disqualified on sight — Av(1324)'s growth
rate is per-object-size like `lambda`, not per-site, and permutation classes carry
no locality constraint, so neither reason that killed Chan–Rechnitzer and the Oh
cluster applies.

**Their upper bound (Theorem 8, `gr(Av(1324)) <= 27/2`) is an injection into a
labelled simpler class.** They map `Av_n(1324) -> {o,*}^n x D_n`: greedily grid the
avoider in a descending `Av(213)`/`Av(132)` staircase, record one bit per point for
which cell it landed in, and push the points into a two-cell "domino". The bit
string lets you invert, so the map injects, and
`gr <= 2 x gr(D) = 2 x 27/4 = 13.5`.

**Verdict: the technique is generic, we are already inside it, and the part that
made it win is an ingredient we do not have.** "Injectively encode each object as
(bounded-alphabet label per element) x (member of a countable simpler class)" is
exactly the family our own bounds live in — the crude king-Eden `5^5/4^4 = 12.2`
and the Bui-style convolution `9.3153` are both over-counts of this shape. BBP's
improvement came entirely from a bespoke structure theorem (Av(1324) sits inside an
infinite staircase grid class) that let them take the simpler class to be something
as small as dominoes. **There is no proposed structure theorem of that kind for
polyplets, and nothing in this paper suggests one.** So this is a different sort of
negative from the previous three: not "the method cannot apply", but "the method
applies and we have no ingredient to feed it". If a structural characterisation of
polyplets inside a smaller analyzable family ever turns up, this is the template to
reach for.

**Useful by-product — a calibration point for the paper.** Their rigorous bracket
after decades of attention by many authors is `10.271 <= gr <= 13.5` around a
numerical `mu ~ 11.60`: a ratio of **1.31**. Ours is `6.543 <= lambda <= 9.3153`
around `7.111`: a ratio of **1.42**. A far more heavily studied problem, with a
genuine structure theorem behind its bounds, lands in the same place. This is worth
citing next to the paper's "the gap reflects a structural limit" sentence — it says
the width of our bracket is normal for the genre, not a sign we stopped early.
