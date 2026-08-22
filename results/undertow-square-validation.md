# Undertow validated on the square lattice, against counts we did not produce

2026-08-22, executing `docs/last-orders.md` C1.3 / A1.4. Desk work on banked
square-lattice data and an OEIS b-file; no compute job. Probe:
`experiments/undertow_square.py`, three RED controls green.

## Why this matters more than its size

`docs/lastditch-ideas.md` §1b names the square lattice as "the one validation
channel this project structurally lacks above n = 20": every other second
source in the tree re-counts the same objects with different code, so a shared
*conceptual* error would survive all of them. The square lattice's counts are
published by other people.

Undertow is the method that produced a(41) and took row 40 off its two tallest
poles. Until now nothing outside this project had ever tested it.

## The claim, stripped of king machinery

    a cell BELOW the diagonal law's onset, corrected by a known defect, is as
    good an equation for P_k as a cell above it

On the square lattice `b = |D| = 1`, so the king's `3^(n−1−3k)` factor is 1 and
the law is a plain polynomial: `T_sq(n, n−k) = P_k(n)` for `n ≥ 2k+1`, degree k.
`results/onset-defect-law.md` records the depth-1 defect, measured ab initio on
`results/bbox_square4_n21.txt`: `T_sq(2k,k) − P_k(2k) = +1, −1, +1, −1, +1`,
i.e. `D_1(k) = (−1)^(k+1)`.

Per level, two fits of the same polynomial:

- **classical** — the `k+1` in-onset cells at `n = 2k+1 … 3k+1`;
- **Undertow** — drop the **tallest** of those and use the depth-1 cell at
  `n = 2k` instead.

## Result

| k | fits agree | tallest cell, predicted from below onset | holds |
|---|---|---|---|
| 1 | yes | 8 | yes |
| 2 | yes | 121 | yes |
| 3 | yes | 2,110 | yes |
| 4 | yes | 39,183 | yes |
| 5 | yes | 752,927 | yes |
| 6 | yes | 14,780,288 | yes |

At every level the two fits are **equal as polynomials**, and the Undertow fit
**reproduces the cell it was denied**, exactly, in integer arithmetic. The
height saved is 1 per level — `J = 1`, because depth 1 is the only square
defect derived.

**The external control.** All 21 rows of the square triangle sum to A001168
exactly, and A001168 comes from the OEIS b-file (with a(57)–a(70) due to
Barequet and Ben-Shachar, 2024). So the data the fit runs on is anchored to
published counts before any fitting happens.

## RED controls

- perturbing one input cell by 1 breaks the classical/Undertow agreement — so
  the test can detect an error;
- **the wrong depth-1 defect sign breaks the fit** — so the agreement is
  carrying the defect, not surviving it;
- the row-sum control fails against a deliberately perturbed A001168.

## What this establishes, and what it does not

**Establishes.** The mechanism is lattice-independent, and it is right. A
below-onset cell plus its defect is a valid equation for the diagonal
polynomial on a lattice where the answers were published before this project
existed. That is now true of Undertow in general and not only of the king case
where every check is internal.

**Does not establish.** That the *king* `D_j` are right — those are separate
derivations, and this validates the frame they plug into rather than their
values. Nor does it reach the n = 56 headline §1b hoped for: that still needs
square below-onset cells at H ≤ 28, and `results/bbox_square4_n21.txt` stops at
n = 21.

**The saving is 1 height, not the king's 2–3.** Only depth 1 is derived for the
square lattice. Depths 2–4 exist king-only (Severance W3), and the parametric
master (`results/skeletonkey-parametric-master.md`) removed the ledger's
king-only blocker but nobody has run the square legs. That is the next step if
this channel is wanted deeper, and it is a derivation rather than machine time.

## Honest limits

- Six levels, k = 1..6, and the tallest cell involved has height 13. The king
  case runs to k = 21. Small-k agreement is real evidence for a mechanism and
  weak evidence about large-k behaviour.
- `D_1(k) = (−1)^(k+1)` is read off five measured values in
  `onset-defect-law.md` and extended to k = 6 by the obvious pattern; the k = 6
  row of this table is therefore also a (passing) test of that extension.
- Nothing here touches the *grand form* — the claim that a level carries
  exactly two new constants — which is what lets the king pin use two equations
  rather than k+1. The square test fits all k+1 coefficients directly. So this
  validates "below-onset cells are valid equations" and not "two of them
  suffice".

## Reproduce

    python3 experiments/undertow_square.py

Instant. Inputs `results/bbox_square4_n21.txt` (banked) and
`results/b001168_external.txt` (OEIS, read-only fetch).
