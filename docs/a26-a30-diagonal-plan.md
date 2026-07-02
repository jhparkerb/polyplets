# a(26)-a(30) via diagonal closed forms — plan and current knowledge

**Status 2026-07-01.** a(25) verification in progress (Job 1 running on ayr).
This doc captures the P_9/P_10/P_11 derivation results and the staged plan to
push to a(30), triggered by: if a(30) is feasible within a week, the project
deadline gets extended.

## Closed-form diagonal state

`T(n, n-k) = P_k(n) * 3^(n-1-3k)` (or, for `n < 3k+1`, divide instead of
multiply — see "engineering prerequisites" below).

- **P_0..P_8**: wired in `orchestrator/sweep.go` `diagonalCell`, in production
  since a(24)/a(25).
- **P_9**: fully derived and validated (`scripts/derive_p9.py`,
  `scripts/derive_p9_calibrate.py`). 6 of 10 coefficients (n^9..n^4) came from
  existing `a_1..a_6, b_1..b_6` theory alone (docs/proofs/T-n-nm2-and-general.md),
  zero new data. Remaining 4 solved from 4 of 7 real points (n=19-22); held out
  3 (n=23-25), all matched exactly. Leading coeff `25^9/9!` emerged
  independently (not assumed, unlike P8's original pinning).
- **P_10**: fully derived and validated (`scripts/derive_p10.py`). First
  recovered `b7 = -687296991/7` exactly from P_9's n^3 coefficient (which
  depends on b7 alone) — no new data. With b7 known, 7 of 11 coefficients
  clean; remaining 4 solved from 4 of 5 *structurally valid* real points
  (n≥2k+1=21; n=21-24), held out n=25, matched exactly. Leading coeff
  `25^10/10!` confirmed independently.
- **P_11**: partially pinned (`scripts/derive_p11_sizing.py`). 7 of 12
  coefficients clean from theory. Remaining 5 need 9 unknown symbols total;
  only 3 structurally-valid real diagonal-11 points exist today (n=23,24,25;
  the threshold is n≥23). Short by 2 equations — but those 2 fall out for
  free as T(26,15) (from a26's own real sweep) and T(27,16) (from a27's).
  **P_11 closes automatically once a26 and a27 are computed, no dedicated
  verification run needed.**
- **P_12, P_13**: not derived. Likely the same circular pattern (need that
  term's own real data) — treat as opportunistic, not schedule-critical.

Full current coefficient tables (exact rationals + integer-numerator Horner
form) are reproducible via `scripts/show_p9_p10_p11.py`.

**Sanity/consistency check:** the leading coefficient `25^k/k!` came out
independently correct for k=9, 10, 11 — three consecutive confirmations of the
conjecture, not assumptions.

## Engineering prerequisites (blocking)

1. **BUGS-OF-SHAME A2**: `orchestrator/runref.go` `resultPipelineMaxN` hard-caps
   `maxn≤25` (uint64 triangle overflow guard). Widen to `big.Int` — nothing
   past a25 runs at all without this.
2. **True `n≥2k+1` threshold in `diagonalCell`**: current dispatch guard
   (`orchestrator/sweep.go` ~line 251/395) requires `maxn≥3k+1`, purely because
   the `pow3(n-1-3k)` call can't handle negative exponents. The real validity
   bound is `n≥2k+1` (confirmed empirically for P9 at n=19 and P10 at n=21).
   Without fixing this, P9/P10/P11 can't fire until maxn reaches 28/31/34 —
   useless for a26-a28. Needs a division-capable path for `e<0`.
3. **Wire P9 (case 9), P10 (case 10) into `diagonalCell`**, extend guard to
   `k≤10`. Direct port of the integer-numerator Horner form already derived,
   same style as existing case 7/8.
4. **u128 counter** for all a26+ runs (u64 overflows past a25; u128 already
   exists, exact to ~a48).
5. Each newly-wired Pk gets the same red-first validation discipline before a
   record run trusts it (standing quality-gate rule) — the held-out-point
   checks already built into the derivation scripts are the first pass.

## Cost model (measured, not modeled)

Pulled real `cost_profile.tsv` cpu-second data from the actual a23/a24/a25
dalby runs (not the abstract a(21) frontier-profile model).

- a25's real-sweep total (H3-16) = **632,815 cpu-s**, 91% of which is H15+H16
  alone (H16 = 68%, H15 = 23%).
- Internal ladder ratios within a25 (bending down near the boundary, i.e. the
  closer to the closed-diagonal region, the milder the marginal growth):
  H13→14 = 3.86x, H14→15 = 3.39x, H15→16 = 3.01x.
- Cross-term at a *fixed* top height: a24 and a25 both naturally real-swept
  only to H16 (K=8's floor stayed flat since maxn and K grew in lockstep when
  P8 got pinned). a24 H16 = 285,979 cpu-s, a25 H16 = 431,956 cpu-s →
  **1.51x for "+1 to maxn, same top-H tier."** Much cheaper than opening a
  new tier (~3x).

## Staged plan to a(30)

| term | top real H | Pk source | est. cpu-s | est. wall @ 80 cores | byproduct banked |
|---|---|---|---|---|---|
| a26 | 15 | P9+P10 | ~303K | ~1.1h | T(26,15) → P11 |
| a27 | 16 | P9+P10 (P11 not ready) | ~1.44M | ~5.0h | T(27,16) → P11 closes |
| a28 | 16 | P9+P10+P11 (pinned right after a27) | ~2.18M | ~7.6h | T(28,16) → sizes P12 |
| a29 | 17 if P12 not ready | P9-P11 | ~6-7M (extrapolated) | ~1 day | feeds P12/P13 |
| a30 | 18 if P12/P13 not ready | P9-P11 static | ~20-30M (extrapolated, wide uncertainty) | ~1-4 days | — |

Total critical path estimate: **~2-6 days** of dalby wall-clock, sequential.
a29/a30 figures are 2-3 compounded extrapolations off one clean measurement
each — re-measure the actual ladder as each term lands rather than trusting
the projection blindly.

## Open items / risks

- P12/P13 may not close before a29/a30 need to run (same circular-data pattern
  as P11) — opportunistic, not load-bearing.
- Cross-machine split (#32 lever, designs/09) unexplored for this plan; could
  shrink wall-time further if usable.
- cpu-s→wall-time assumes ideal 80-core scaling; real merge-barrier/straggler/
  spill overhead (documented elsewhere) will erode this somewhat.
- No jobs launched yet — this is the plan only, pending go-ahead per the
  beg-and-agree rule (each real term is a >1h job).
