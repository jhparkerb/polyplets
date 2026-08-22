# King and square animals share theta, measured by one method at one length

2026-08-22, executing `docs/last-orders.md` C3.1, which is
`results/unexplored-avenues.md` idea 6.2 — the half of the Parisi–Sourlas item
that survived 6.1's closure because it does not run through the strip ladder.
Desk work on banked and published series; no compute job. Probe:
`experiments/theta_universality.py`, four RED controls green.

## The answer in one line

**θ_king = −0.9997 and θ_square = −0.9995 at matched length (N = 40), a
difference of 2·10⁻⁴.** Universality predicts they are equal. They are, to the
resolution the method has.

## Why this needed doing at all

`results/series-analysis-da.md` pins θ_king = −1.000(1) from 40 terms and notes
that "universality predicts θ = −1". That is a prediction quoted from the
literature and confirmed on one lattice. Idea 6.2's point is that the same
prediction is *testable* here: if king and square are in the same class their
exponents must agree, and this project can measure both.

The test has to control for the method. A θ that is fitted with different code,
a different approximant spectrum, or a different number of terms on each
lattice can agree for reasons that have nothing to do with universality. So:
**one script, one spectrum of 42 first-order inhomogeneous differential
approximants, the same 40 terms on each side.**

| | series | terms | λ | θ | approximants |
|---|---|---|---|---|---|
| king | A006770 (banked) | 40 | 7.1102 | **−0.9997** | 42 |
| square | A001168 (OEIS) | 40 | 4.0626 | **−0.9995** | 42 |

## The square series is an external oracle, and it reproduces a published lambda

A001168 is enumerated to n = 70 in the b-file, with a(57)–a(70) due to Barequet
and Ben-Shachar (2024) — work entirely outside this project. Run at full
length the same spectrum gives:

| N | 40 | 50 | 60 | 70 |
|---|---|---|---|---|
| λ | 4.06256 | 4.06257 | 4.06257 | 4.06257 |
| θ | −0.99945 | −0.99974 | −0.99987 | −0.99988 |

**λ = 4.06257 against the published estimate for fixed polyominoes, ≈4.0625696.**
Six digits, from code written for a different lattice and never tuned to this
one. That is a Tier-1 external anchor in the sense of
`docs/external-anchors.md`: a number this machinery reproduces that it did not
produce. It also means the king θ rests on a method that has now been checked
against somebody else's series, which it had not been.

θ converges monotonically toward −1 as terms are added — −0.99945 at 40 terms
to −0.99988 at 70 — which is what a true value of exactly −1 with a finite-size
bias looks like, and is a second reason to read the king's −0.9997 at 40 terms
as −1 rather than as a measured deviation.

## Anchoring

θ must not depend on the rescaling constant the series is divided by before the
linear solve:

    king    lambda0 = 6.8, 7.0, 7.11, 7.3  ->  theta = -0.9997 throughout
    square  lambda0 = 3.8, 3.95, 4.06      ->  theta = -0.9999 throughout

Both lattices degrade at the top of their anchor range (king at 7.5 gives
−0.9848, square at 4.2 and 4.4 give −0.994) — the expected conditioning
failure when the rescaled series is no longer O(n^θ), and visible as one rather
than silently averaged in.

## RED controls

All four fire, and the first two are the ones that matter:

- a synthetic series with **θ = −0.5** is reported as **−0.5000**, at both the
  king and the square scaling. The method is not printing the universal value;
- a synthetic series at the square λ with θ = −1 is recovered as
  (4.0600, −1.0000), so a null result on real square data could not have been
  blamed on the scaling being wrong for that lattice;
- a b-file whose head is not `1, 2, 6, 19, 63, 216` is refused rather than
  analysed.

## What this does and does not establish

**Establishes.** The two lattices' exponents agree to 2·10⁻⁴ under one method
at one length, and the method reproduces an externally published λ to six
digits. The universality prediction is confirmed rather than assumed, on this
project's own data, which is what idea 6.2 asked for.

**Does not establish.** That θ is exactly −1, or that either lattice is in the
Yang–Lee class. Agreement between two lattices is consistent with universality
and does not derive it; the Parisi–Sourlas dimensional-reduction argument is
still not in this repo and is not tested here. Nor does it rescue 6.1: no
central charge is readable, for the separate reason in
`results/strip-fss-lambda-sensitivity.md`.

**Sentence that gets shorter.** `results/series-analysis-da.md`'s θ paragraph
currently reports a fitted exponent and quotes universality as the reason that
number is expected. It can now report the exponent *and* the test, with the
square lattice as the control.

## Reproduce

    python3 experiments/theta_universality.py

Instant. Input series: `results/b006770_upload.txt` (banked, gated) and
`results/b001168_external.txt` (OEIS b-file, fetched read-only, head-checked by
the third RED control).
