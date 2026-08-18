# k=7 defect census: measured price

Calibration `scripts/dalby_perimeter_defect_k7_calib.sh`, dalby, 12 single
cores alongside Confetti, binary `git=6473890c`. Finished 2026-08-18T23:53Z.
Single-core wall, seconds:

| lattice | k | n=30 | n=34 | n=38 |
|---|---|---|---|---|
| square4 | 6 | 76 | 225 | 578 |
| square4 | 7 | 601 | 2150 | 6510 |
| square8 | 6 | 254 | 691 | 1665 |
| square8 | 7 | 2528 | 8077 | 22386 |

The `k = 6` cells are controls: recorded 254 / 692 / 1666 s for square8, so the
calibration reproduces the census timings to under 0.1%.

## Exponent

Local slopes `d log t / d log n` are flat across both intervals, so a single
power law fits over 30--38:

| lattice | k=6 | k=7 |
|---|---|---|
| square4 | 8.58 | 10.08 |
| square8 | 7.95 | 9.23 |

The pool script's `n^7.9` model is right for square8 at `k = 6` and wrong
everywhere else; it carried no `k` dependence, which is where the 23x miss on
the k=6 census came from. Each step in `k` costs about `n^1.3` (king) to
`n^1.5` (square) on top.

## k=7 : k=6 ratio

At fixed `n` the ratio is not constant --- it grows as `n^(e7 - e6)`:

| lattice | n=30 | n=34 | n=38 |
|---|---|---|---|
| square4 | 7.9 | 9.6 | 11.3 |
| square8 | 10.0 | 11.7 | 13.4 |

Extrapolated to the k=6 census `n = 78`: 25x (square4), 29x (square8).

## Price of the census

Against the measured k=6 census (42 h king, 23 h square at 76-way, `n <= 78`),
extrapolating with the fitted exponent:

| n_max | square4 | square8 |
|---|---|---|
| 78 | 32 d | 59 d |
| 82 | 53 d | 93 d |
| 85 | 76 d | 130 d |
| 88 | 107 d | 179 d |

`n = 78` is the floor and it is not the target: the k=7 fit wants ~44
coefficients on an onset of 31, against k=6's 32 on 24, so the honest range is
`n = 85`--`88` --- **two to six months of the 76-way pool per lattice**. Both
lattices, at the range the fit needs, is on the order of half a year of the
fleet.

Result tier: planning input, not a paper number. The census remains
unapproved and unlaunched.
