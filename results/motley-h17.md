# Motley rung 1 (Half Measure) — H = 17, GREEN

Run 2026-08-14 on dalby, `docs/motley-plan.md` §"Rung 1". Runner
`scripts/dalby_motley_h17.sh`; row, log and oracle copy under
`~/var/motley-h17`; the row banked here as
`results/cutcount_b1/rows/C17.out`.

**GREEN.** T(n,17) = C_17(n) − 2 C_16(n) + C_15(n), assembled from this run's
C_17 and step 0's C_15/C_16, matches the incumbent's banked triangle
(`results/triangle.txt`) at **all 24 cells n = 17..40, 0 mismatch**.

**Product: a(n) is closed rule-independently for all n ≤ 33** (n = 2H − 1 at
H = 17), by the colour-symmetrized cancellation rule — no union-find verdict,
no stranded-component death, no completion predicate — on a payload the
banked reference cannot reach.

## Provenance

| | |
|---|---|
| binary | `~/src/pm-halfmeasure/build/cutcount_b1`, stamp `git=4df3fec9`, no `-dirty` |
| binary sha256 | `dd1732399703d5aa...` |
| gate | `gate-cutcount-b1` GREEN on this build |
| oracle for the rows | byte-identical to banked C rows at H = 12..16 (`scripts/hm_byte_oracle.sh`) |
| oracle for the product | incumbent triangle, independently computed |
| inputs C_15, C_16 | step-0 rows that reproduced the banked ladder byte-for-byte (`results/motley-step0.md`) |

The first launch attempt (06:24) was refused by the previous binary
`b9d725be` — `limits: H<=16` — which is how the three hard-coded height caps
and the latent H = 18 fan-out overflow were found and fixed (`4df3fec9`);
the run proper started 06:32.

## Cost, measured — the numbers the rest of the ladder rests on

| quantity | H = 16 (u128) | H = 17 | ratio | ladder constant |
|---|---|---|---|---|
| wall | 12,231 s | 39,117 s (10.9 h) | x3.198 | x3.209 |
| peak RSS | 32.06 GB | 95.0 GB | x2.963 | x2.984 |
| census | 7,832,667 | 23,681,423 | x3.023 | x2.984 |

Predicted 91 GB / 7–10 h; measured 95.0 GB / 10.9 h — inside the ±20% band
the census-ratio extrapolation carries. **The kill condition
(`docs/motley-plan.md`: measured windows departing the census ratio by more
than 20% stops the ladder before Confetti) does not fire.** The H = 18 and
H = 19 RAM projections for Confetti and Ticker Tape now rest on a measured
point above the banked ladder rather than on extrapolation alone.

## Checks

1. Engine self-checks per height: `q0_zero=OK q1eval_binomial=OK (n=1..40)`,
   plus the `fits_pay` bound (exit 2 before writing a wrapped row). These are
   arithmetic checks only, not connectivity checks
   (`docs/motley-plan.md` §"What the in-engine self-checks do not check").
2. The connectivity check is external and decisive: the 24-cell comparison
   against the incumbent's independently computed T(n,17).
3. The assembly used only step-0 rows for C_15/C_16 — rows that reproduced
   the banked ladder byte-for-byte under the committed, gated engine.
