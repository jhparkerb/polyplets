# The defect rate is not in the strip spectrum (NEGATIVE, and the premise was wrong)

2026-08-09. Plan **Spectral Edge** of `docs/onset-defect-plans.md`,
`experiments/spectral_edge.py`. Abandoned under its own clause, with two things
worth keeping.

## 1. The premise contained a framing error

The plan asked whether the row-transfer operator shows a continuum edge at
`3² = 9`, following `results/onset-defect-law.md` §4's reading of the defect rate
as the square of the thin-diagonal growth.

On the depth-j line `n = 2k+1−j`, so `9^k = 3^(n+j−1)`. **Per cell the defect rate
is 3 — the thin-diagonal rate itself, not its square.** The two readings are the
same measured fact in different variables, and no data we can reach separates
them, because `n` and `2k` differ by a constant on every line with a clean rate.

The squared reading also concealed an impossibility: `9` exceeds every `μ_H`,
which climb to λ = 7.11, so no eigenvalue could ever sit there. `3` can. §4 of
`onset-defect-law.md` has been rewritten accordingly, and the question tested here
became: is there anything at **3**?

## 2. The spectrum is directly available, and the control fixes its usable range

`G_H(x) = P_H(x)/Q_H(x)` has poles at 1/eigenvalue, so the reciprocal roots of
`Q_H` (`results/fixed_height_gfs.txt`) are the strip spectrum outright — no new
machinery, contrary to what the plan assumed.

Control: the dominant reciprocal root must reproduce the known `μ_H`.

| H | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|
| order | 3 | 7 | 15 | 42 | 106 | 278 | 711 |
| dominant | 2.414214 | 3.443718 | 4.182321 | 4.717801 | 5.115324 | 5.417609 | **13.666** |
| known | 2.414214 (1+√2) | 3.4437 | | | | | |

Exact at H = 2, 3 and monotone increasing through H = 7. **At H = 8 it returns
13.67**, which is above λ and therefore impossible — float root-finding on a
degree-711 integer polynomial has broken down. So the control works, and it caps
the usable range at H ≤ 7.

## 3. Nothing at 3

| band | 2.5–2.9 | 2.9–3.1 | 3.1–3.5 |
|---|---|---|---|
| H=5 (42 roots) | 0 | 0 | 1 |
| H=6 (106) | 2 | 0 | 0 |
| H=7 (278) | 4 | 0 | 2 |

Within 2% of 3: **zero eigenvalues at every H ≤ 7**. Exactly, `Q_H(1/3) ≠ 0` for
all H ≤ 8 (checked in rationals), so 3 is not an eigenvalue of any strip.

## Verdict

No support for a spectral origin of the defect rate. Two reasons not to push
harder, both structural rather than a matter of effort:

- The usable range is H ≤ 7, giving 278 eigenvalues at best. A "continuum edge"
  is an H → ∞ statement; 278 points across six heights cannot exhibit one, and
  the plan's own clause said to abandon rather than run on faith.
- More fundamentally, the strip operator governs growth in n at **fixed H**,
  while the defect lives on lines where n and H grow together. It is probably the
  wrong object for this question regardless of range.

What survives is the corrected framing, which is worth more than the test was:
the defect grows at exactly the thin-diagonal rate per cell, so
`D_j(k) ≈ C_j·3^(j−1)·3^n·k^(j−3/2)` — the error of the diagonal law is, at every
fixed depth, the count of thin animals times a power of k.

## Limits

- Float root extraction; verified against exact `μ_2 = 1+√2` and against `μ_3`,
  and rejected at H = 8 by its own control. H ≥ 9 would need exact or
  high-precision root-finding, which was not attempted.
- The "nothing at 3" result is a statement about H ≤ 7 only.
