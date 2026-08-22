# Coordination number does not set lambda: two q=8 lattices, 26% apart

2026-08-22, executing `docs/last-orders.md` C1.1 — the cheap half of
`results/unexplored-avenues.md` idea 4 (the lambda atlas). Brute force to
n = 9; no compute job. Probe: `experiments/lambda_atlas_probe.py`, five RED
controls green.

## The question idea 4 posed, and the answer

> is lambda a function of coordination number, or does local cycle structure
> move it?

**Local cycle structure moves it, and by a lot.** Two lattices with the *same*
coordination number q = 8:

| lattice | q | triangles per site | λ |
|---|---|---|---|
| king — `(±1,0),(0,±1)` + four diagonals | 8 | 12 | **7.1102** (known) |
| spread-8 — `(±1,0),(0,±1),(±2,0),(0,±2)` | 8 | **6** | **≈ 8.97** |

A 26% difference at identical q. Coordination number is not the parameter.

Idea 4 stated its prediction before measuring — "spread-8 should land noticeably
above king's 7.11, toward the tree bound, because clustering suppresses lambda"
— and that is **confirmed in direction**: spread-8 lands above king by 1.86,
which is 18% of the way from king to the q = 8 tree bound
`(q−1)^(q−1)/(q−2)^(q−2) = 17.65`.

## Why the number is trustworthy despite nine terms

The estimator is a 1/n-corrected ratio extrapolation on nine terms, which on its
own would be worth little. What makes it usable is that **two of the three
lattices have known λ**, so the estimator's bias is measured rather than
assumed:

| lattice | 9-term estimate | known λ | ratio |
|---|---|---|---|
| square | 3.9949 | 4.0626 | 0.9833 |
| king | 6.9885 | 7.1102 | 0.9829 |

The two biases agree to **0.04%**. Applying the same correction to spread-8's
raw 8.8222 gives **8.974**, and the calibration's own spread bounds that to
about ±0.01 — far tighter than the 1.86 gap being claimed.

The fitted correction exponents agree too: θ = −0.717, −0.719, −0.702 across the
three lattices, so the estimator is behaving identically on all of them, which
is the assumption the calibration rests on.

## Counts

    square    1, 2, 6, 19, 63, 216, 760, 2725, 9910          (A001168)
    king      1, 4, 20, 110, 638, 3832, 23592, 147941, 940982 (A006770)
    spread-8  1, 4, 24, 164, 1200, 9126, 71296, 567706, 4586448

The spread-8 sequence is not in the repo, and **the OEIS check was run on
2026-08-22: it is not in OEIS either.** Three query widths — all nine terms,
the middle five `24, 164, 1200, 9126, 71296`, and the tail four `1200, 9126,
71296, 567706` — each return no results. Controls in the same session: the
square and king rows above return A001168 and A006770, so the search was
working and the absence is an absence.

Nine terms of a sequence nobody has entered. What to do with it is
`docs/time-at-the-bar.md` B7's question, not this file's.

## RED controls

- square and king reproduce A001168 and A006770 exactly, so the enumerator is
  the right enumerator;
- spread-8 and king have the **same coordination number 8** — without this the
  comparison is not controlled;
- spread-8 is **not** king: 6 triangles per site against 12, which is the whole
  point of the design;
- the two q = 8 lattices give different counts from n = 3 on.

## What this does and does not deliver

**Delivers.** Idea 4's headline question, answered, with a controlled pair and
a calibrated estimator, for the cost of an afternoon's brute force. It also
makes two of this project's universal theorems less vacuous by exhibiting a
third instance of the row-local class they quantify over.

**Does not deliver.** The atlas itself. Idea 4 wants *certified two-sided
brackets* — the strip ladder with exact Collatz–Wielandt certificates on each
lattice — and none of that is here. λ ≈ 8.97 for spread-8 is a calibrated
estimate, not a bound of any kind, and the calibration rests on two points.

**The remaining work is a compute item and is priced, not launched.** Certified
brackets need `cpp/strip_mu_cert.cpp` made lattice-parametric and then run per
lattice per height; `results/strip-growth-lambda-bounds.md` measures H = 18 on
the king lattice at tens of minutes and tens of GB, and a spread-8 strip has a
different (probably larger) frontier because the neighbourhood reaches two rows.
That is a beg-and-agree decision, and this file exists so that the decision can
be made against a measured motivation rather than a hunch.

**Sentence that gets shorter: still none in the polyplets papers.** Idea 4
ranked itself last for exactly that reason and it was right. What changed is
that it is no longer speculative — the interesting fact is in hand, and it is
the kind of fact a separate short paper is made of.

## Reproduce

    python3 experiments/lambda_atlas_probe.py --nmax 9

About twelve minutes, dominated by spread-8's n = 9 level (4.6M animals).
`--nmax 10` is roughly eight times that and would tighten the calibration.
