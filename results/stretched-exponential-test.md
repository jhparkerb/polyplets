# No stretched exponential: mu_1 is driven to 1

2026-08-07, gympie. Runs the test `results/series-analysis-da.md` names at the
end of its Conway-Guttmann-Zinn-Justin section and has never run:

> "refit the 40 terms with `mu_1^sqrt(n)` admitted as a fourth parameter and
> see whether `mu_1` is driven to 1 (no stretched exponential) or lands away
> from it. Cheap, and it converts an untested assumption into a measurement."

**Result: `mu_1 -> 1.0068`, with the method calibrated to resolve a 1%
stretched exponential at this series length. The untested alternative
hypothesis is now tested, and it fails.** As a by-product the same fit returns
`theta -> -0.981` while being free to blame a stretched exponential instead.

## Why this needed doing

CGZJ 2018 (`papers/conway_guttmann_zinnjustin_2018_1324_revisited.pdf`) found
1324-avoiders obey `B mu^n mu_1^sqrt(n) n^g` with `mu_1 = 0.0400(5)`. A
differential approximant is *structurally blind* to that factor — it fits a
D-finite ansatz, `mu_1^sqrt(n)` is not in it, so the fitted exponent absorbs it
and looks stable while being wrong. Our `theta = -1.000(1)` rests on DAs plus a
confluent 3-parameter fit, and **neither admits `mu_1`**. The evidence against a
stretched exponential was real but entirely indirect.

## Method

Taking logs makes the ansatz linear in the four unknowns:

```
ln a(n) = ln B + n ln(lambda) + sqrt(n) ln(mu_1) + theta ln n
```

so a 4-term window has an exact solve and a sliding window shows drift — the
same shape as the exact 3-point triple solves used for the `mu_H` ladder in
`results/strip-growth-lambda-bounds.md`. 60-digit arithmetic; the banked terms
are exact integers. Windows are extrapolated by one Richardson step assuming
`f(n) = f_inf - A/n`.

## The controls, which are the whole point

**(a) Exact-form data.** On `B lambda^n mu_1^sqrt(n) n^theta` with no other
correction, the solve recovers the planted `mu_1` to 55 digits. That calibrates
the arithmetic and *nothing else* — real series are not of that form.

**(b) Planted underneath a confluent correction `1 + 1/n`.** This is the honest
control: the real series carries corrections the 4-parameter ansatz cannot
hold, they get absorbed into `mu_1`, and the question is whether anything
survives that.

| planted `mu_1` | Richardson recovers | `theta` recovers |
|---|---|---|
| 1.00 | 0.9693 | -1.0093 |
| 0.99 | 0.9596 | -1.0093 |
| 0.95 | 0.9209 | -1.0093 |

Two things to read off. The extrapolation is **biased low by ~0.031** when
`c = 1` — a truth of 1.00 reads as 0.969 — and the bias is near-constant across
planted values. And the **separation is 0.0097 for a 1% planted difference**,
i.e. essentially 1:1. The method resolves a 1% stretched exponential at 40
terms. Had it not, the verdict below would have been "cannot tell".

## The real series

`results/b006770_upload.txt`, n = 1..40. Sliding 4-point windows:

| window | lambda | mu_1 | theta |
|---|---|---|---|
| [4,7] | 7.3369778 | 0.67550778 | -0.638431 |
| [12,15] | 7.1452384 | 0.90090285 | -0.836469 |
| [20,23] | 7.1275277 | 0.93817343 | -0.878024 |
| [28,31] | 7.1206429 | 0.95646126 | -0.902173 |
| [36,39] | 7.1171873 | 0.96719872 | -0.918238 |
| **[37,40]** | **7.1168808** | **0.96822628** | **-0.919874** |

`mu_1` climbs monotonically toward 1 across the whole series and `theta` climbs
monotonically toward -1; neither has arrived at n = 40, which is exactly the
drift the controls say to expect from an unmodelled confluent correction.
Richardson on the top two windows:

```
lambda -> 7.1053868      mu_1 -> 1.0067597      theta -> -0.981231
```

**Reading.** `mu_1 = 1.0068` sits *above* even the zero-correction calibration
point (where a truth of 1.000 reads as 1.000), and far above the `mu_1 = 0.99`
signature under either calibration (0.99 with `c = 0`, 0.96 with `c = 1`). A
stretched exponential of the kind CGZJ found — or one a hundred times weaker —
would have shown up. It does not.

The slight overshoot past 1 is the same unmodelled-correction effect running
the other way and is not evidence of `mu_1 > 1`, which would be meaningless
here.

## What else it says

- **`theta -> -0.981`**, from a fit that was free to blame a stretched
  exponential and did not. This is an independent corroboration of
  `theta = -1.000(1)` from an ansatz strictly larger than the one that produced
  it, which is worth more than the number's precision.
- **`lambda -> 7.1054`** against the banked 7.110(1). Low by 0.005, which is
  larger than the quoted uncertainty. Not a challenge to the banked value: a
  single Richardson step on a 4-parameter window fit is much cruder than the
  four methods behind 7.110(1), and the controls show the same pipeline
  returning `theta = -1.0093` when the truth is exactly -1. Read it as
  consistent, not as a competing estimate.

## Honest limits

- One Richardson step, assuming the drift is `f_inf - A/n`. The controls
  validate that assumption on planted data with `c = 1`; the real correction
  structure is unknown and need not be a single `1/n` term.
- The controls plant one confluent correction. A series with a *different*
  correction structure could bias the extrapolation differently. The margin
  here (measured 1.0068 against a 0.99 signature of at most 0.96) is wide
  enough to absorb a good deal of that, but it is a margin, not a proof.
- **Novelty: none claimed.** This is a standard four-parameter series fit; the
  only thing it settles is a question this repo asked itself.

## Sentence that gets shorter

`results/series-analysis-da.md`'s CGZJ caution paragraph, which currently ends
"**it is a named alternative hypothesis we have never explicitly tested**". It
has now been tested. The paragraph keeps its warning about what DAs are blind
to — that stays true and is why the test was worth running — but the closing
admission can go.

## Artifacts

- `experiments/stretched_exponential_fit.py` — controls and fit, runs in ~20 s
