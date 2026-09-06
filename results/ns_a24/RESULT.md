# a(24) — fixed polyplets (king-move animals), 2026-07-01

Computed on **dalby only**, reusing already-swept work rather than following
`docs/a24-launch-plan.md`'s original 3-box split:

- **H1-15**: reused byte-exact from the 2026-06-30 perf-audit probe
  (`scripts/perf_audit_run.sh`, rev `5fadde3`) — that run's `--heights 1-15`
  completed all 15 heights as a real (not throwaway) byproduct.
- **H16**: freshly swept this run (`scripts/dalby_a24_h16.sh`), rev `5fadde3`
  built with clang-19 (the audit's ~5% win). **80 cores, 1 GiB/worker RAM,
  unit-mult=4, steal-grain=0.05.**
- **H1,2,17-24**: closed-form (k≤7 diagonal injection, already validated
  through a(23)), recomputed fresh in this run for a cross-check: H1,H2
  matched the reused probe values byte-for-byte.

No ayr needed: with H1-15 already in hand, H16 alone is the wall-clock floor
regardless of how many machines are thrown at the rest, so a second box would
only add combine-coordination risk for no wall-clock benefit.

## Run stats (H16 sweep only)

**rc=0, wall=4870.3s (~81 min)** — well under the ~2.35h (141 min) predicted
from `docs/a24-launch-plan.md`'s core-hour estimate. Peak RSS 628.8 MB.

## The term

```
a(24) = 2,194,666,793,369,310,473      (new)
```

Growth ratio trend (smoothly increasing toward λ≈7.1, as expected for finite
n): a(22)/a(21) = 6.7953, a(23)/a(22) = 6.8087, **a(24)/a(23) = 6.8210**.

## Validation

- **a(1)-a(23) reproduce exactly** — full regression against every prior
  known/recorded value (`build/ns/combine --compare`; `fixtures/b006770.txt`
  only extends to a(20), so a(21)-a(23) show as "known=0 FAIL" in the compare
  tool's output — expected, not a real failure; verified by hand against
  `results/ns_a23/RESULT.md`'s recorded values instead).
- **T(24,16) = 42,594,477,635,772,598** — this run's headline new cell.
  **Matches the pre-a(24) falsifiable k=8 prediction from
  `results/diagonal-formula.md` exactly** (the sum-of-roots extrapolation of the
  P₈ pattern, made before this run existed). Strong independent confirmation
  that the leading-coefficient conjecture (`[n^8]P_8 = 25^8/8!`) and the
  quadratic sum-of-roots pattern both extend correctly to k=8.

## P₈ pinned

With T(24,16) in hand, P₈ (`T(n,n-8) = P_8(n)·3^(n-25)`) is now **fully
determined** from 8 real points (n=17..24, no shortcut needed) — see
`scripts/pin_diagonal_k8_final.py`, which fits P₈ with the leading coefficient
fixed by the confirmed conjecture and verifies the fit reproduces all 8
defining points exactly (including a direct Horner re-evaluation cross-check,
not just the linear-algebra residual).

Wired into `orchestrator/sweep.go` `diagonalCell` case 8 (big.Int Horner path,
same pattern as case 7 — the coefficients overflow int64 at the n they're
used at). The strip-dispatch guard (`k>=2 && k<=8`) now allows k=8, unlocking
a(25) to inject H17-24 via closed form and sweep only H≤16 (peak swept H16
instead of H17 — the ~2.4× dominant-height saving behind the a(24)→a(25)
ladder). Regression-pinned in `orchestrator/heightnm2_test.go`
(`TestHeightNm2Formula`), including a genuine extrapolation check at n=25
(T(25,17), unconfirmed until a(25) itself sweeps H=17 — same status k=7's
a(24) prediction had until this run).

## Files

- `results/ns_a24/triangle.txt` — assembled T(n,H), n=1..24.
- `results/ns_a24/a_n.txt` — a(1)..a(24).
- Provenance: dalby, rev `5fadde3` (H16 sweep + fresh closed-form heights),
  rev `5fadde3` (reused H1-15 probe). Both at the same commit.
