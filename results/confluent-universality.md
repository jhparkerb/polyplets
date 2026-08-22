# The confluent exponent, king against square — and what 40 terms cannot do

2026-08-22, executing `docs/time-at-the-bar.md` A1.5. Probe:
`experiments/confluent_universality.py`, five RED controls green, run on ayr.
Desk work on banked and published series; no compute budget.

## The answer in one line

**On the king lattice the correction-to-scaling exponent comes out at
Δ ≈ 0.58–0.63 from 40 terms. On the square lattice 40 terms do not determine
it at all — the same fit gives anything from 0.10 to 0.74 depending on where
the window starts.** So the matched-length comparison A1.5 asked for cannot be
made. What can be said is weaker and still worth having: given its own 70
published terms the square converges to 0.590, inside the king's range, and the
convergence is monotone.

## Two corrections before the numbers

**A1.5's premise was wrong, and the item is better without it.** It says
`results/series-analysis-da.md` "already fits a confluent term on the king side
(Δ₁ = 1/2)". That file says the opposite at line 60: *"The DA does not
independently pin Δ₁ (that needs sub-dominant-singularity analysis); it is
consistent with the paper's Δ₁ = 1/2 picture, not an independent test of it."*
The 1/2 is the literature's ratio-method value, quoted. There was no banked king
Δ₁ to compare a square one against, so this measures both from scratch, which is
the only version of the comparison that means anything.

**The first version of this script was wrong and its own control caught it.**
The textbook ansatz is `a(n) = B λⁿ n^θ (1 + c n^(-Δ))`; the first version
planted that and fitted the *linearised* log, and the exactness control returned
0.290 and 0.860 for planted 0.5 and 1.0 — a bias the size of the effect. The
ansatz is now `exp(c n^(-Δ))`, which agrees to first order, differs inside the
next correction the model does not carry either way, and makes the solve exact
for its own form. Planted 0.5 and 1.0 now return 0.500 and 1.010.

## Method

`a(n) = B λⁿ n^θ exp(c n^(-Δ))` is nonlinear in Δ and exactly linear in
`(ln B, ln λ, θ, c)` once Δ is fixed. So Δ goes on a grid of 0.005 from 0.10 to
3.0, least squares solves the other four at each point, and the Δ with the
smallest residual wins. One script, one grid, the same 40 terms on each lattice.

## The measurement

Matched length, window from n = 8:

| | terms | Δ | λ | θ | residual |
|---|---|---|---|---|---|
| king | 40 | 0.575 | 7.11075 | −1.0159 | 7.4e−12 |
| square | 40 | 0.360 | 4.06392 | −1.0676 | 2.4e−09 |

Window sensitivity, which is the honest error bar:

| window starts at | king Δ | square Δ |
|---|---|---|
| n = 6 | 0.610 | 0.100 |
| n = 8 | 0.575 | 0.360 |
| n = 10 | 0.585 | 0.550 |
| n = 12 | 0.600 | 0.660 |
| n = 15 | 0.625 | 0.735 |
| **spread** | **0.58 .. 0.63** | **0.10 .. 0.74** |

The square at its own full length, as a convergence check:

| N | 50 | 60 | 70 |
|---|---|---|---|
| Δ | 0.475 | 0.545 | **0.590** |
| λ | 4.06332 | 4.06304 | 4.06290 |
| θ | −1.0358 | −1.0235 | −1.0174 |

## What that means, and what it does not

**The square at 40 terms is not a measurement.** A quantity that moves from
0.10 to 0.735 as the window start moves five places is unresolved, and the
right report is "cannot tell". The king, over the same five windows, moves by
0.05. That asymmetry is not surprising — the square series has a smaller λ and
smaller terms, so 40 of them carry less information — but it means the specific
test A1.5 proposed, *matched length*, returns nothing.

**The residual valley is not the error bar, and the first run of this said it
was.** At the n = 8 window the king's within-2×-residual interval is
[0.57, 0.58], and the window sweep puts the answer at 0.625. The valley measures
how sharply the grid resolves Δ *at one fixed window*; the window start is a
free parameter nobody has pinned, so its spread is the uncertainty. The first
run reported "the intervals DO NOT overlap" on the strength of the valley, which
was an artifact of an error bar three times too small. Corrected before anything
was concluded from it.

**Nothing here measures Δ₁.** The script calibrates itself by planting a known
Δ under a second, unmodelled correction of realistic size, and the recovered
value is biased:

    planted   0.25   0.50   0.75   1.00   1.50   2.00
    king      0.95   0.84   0.98   1.18   1.62   2.00
    square    0.94   0.86   0.99   1.16   1.62   1.96

Two things follow. The map is **not monotone below about 0.75** — 0.25 lands
above 0.50 on both lattices — so in exactly the range the real answers fall in,
a recovered number cannot be inverted to a Δ at all. And the bias depends on the
amplitude and sign of what the ansatz does not model: the calibration planted
`c > 0` and both real series fit `c < 0`, so the table above is not even the
right bias for them. **A recovered 0.6 is not evidence that Δ₁ = 0.6, and it is
not evidence against Δ₁ = 1/2.**

**What survives.** The two lattices are consistent, and the square walks toward
the king as terms are added rather than away from it — 0.475, 0.545, 0.590
against the king's 0.58–0.63. That is one more thing that would have to be a
coincidence if the two lattices were in different classes. It is a great deal
weaker than the leading-exponent test in `results/theta-universality.md`, which
had an external anchor under it; this has none, because nobody has published a
Δ₁ for either lattice that this could be checked against.

**Free corroboration, unasked for.** The fit is a different method from the
differential approximants, and it recovers λ_king = 7.1106–7.1108 against the
banked 7.110(1), and λ_square = 4.06290 at N = 70 against the published
4.0625696. θ comes back at −1.01 to −1.02 on the king and −1.017 on the square
at full length. Nothing new, but it is a third route to those two numbers and it
agrees.

## The sentence that does not get shorter

A1.5 expected to shorten the θ paragraph in `results/mathematics.md` §5, "which
currently rests the universality claim on one exponent". It still rests on one
exponent, and it should. A second exponent that 40 terms cannot resolve on one
of the two lattices does not strengthen the claim, and writing it up as though
it did would be the failure class `docs/project-postmortem.md` names. The
paragraph is unchanged; this file is the record of the test and of why its
result is not quotable there.

What A1.5 got right is that the answer might be "both fits are too loose to
distinguish". It is half that: the king's is tight, the square's is not.

## What would change it

More square terms would not help — it already has 70 and 0.590 is what they
give. What would help is a second correction in the ansatz, which needs enough
terms to fit five parameters, or sub-dominant-singularity analysis, which is the
route `results/series-analysis-da.md:60` names for pinning Δ₁ properly and which
this project has not built. Neither is an afternoon.

## Reproduce

    python3 experiments/confluent_universality.py            # controls + both lattices
    python3 experiments/confluent_universality.py --selftest # controls only

Seconds, a few MB, ayr or dalby. Inputs: `results/b006770_upload.txt` (banked,
gated) and `results/b001168_external.txt` (OEIS, head-checked by a RED control).
