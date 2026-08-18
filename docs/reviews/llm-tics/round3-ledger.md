> **NOTE: authored by Claude at jasonp's direction, 2026-08-18.** Round 3 of the
> LLM-tic sweep, at the same bar as round 2: **log every candidate, including
> the ones kept**. Round 2's catalog (`catalog.md`) is the rulebook; the
> measurement is `density.py`, extended this round to cover L7, L8 and L9.

# Round 3: the sweep over the new prose

Round 2 swept L1–L6. Everything written since — L5's kernel and moments
sections, L6's k=6 verdict and attributions, L7's spectrum section, and the
whole of L8 and L9 — had never been swept, and it showed.

## Measured before and after

Constructions per 1000 prose words. P-control is jasonp's own prose
(`technical-report.tex`, `polyplets-report.tex`).

| paper | cleft before | cleft after | punch before | punch after |
|---|---|---|---|---|
| L5 | 1.26 | 1.26 | 0.76 | 0.76 |
| L6 | 0.51 | 0.25 | 1.01 | 1.02 |
| L7 | 2.19 | 1.82 | 0.36 | **0.00** |
| L8 | 2.50 | **0.00** | 3.33 | 2.09 |
| L9 | 3.59 | 0.90 | 2.24 | 1.36 |
| **L overall** | 1.21 | **0.74** | 1.31 | 1.11 |
| P-control | 0.13 | — | 0.40 | — |

The new papers were the worst in the corpus on both counts when they landed.
L8's cleft density is now zero and L7's punch density is zero; the corpus ratio
against the human control fell from 9.2x to 5.7x on cleft.

## Fixed

**A. "X is what Y" (cleft).** The dominant tic in the new prose, 14 instances.

| where | was | now |
|---|---|---|
| L9 abstract | "the specialisation is what a second enumeration source rests on" | "a second enumeration source rests on the specialisation" |
| L9 abstract | "What the identity licenses is the point" | "Its use is the point." |
| L9 abstract | "Independence of method is what a count with no closed form can otherwise never have" | "A count with no closed form has no other route to independence of method" |
| L9 intro | "What this paper adds is a proof for one particular rule" | "This paper adds a proof for one particular rule" |
| L9 model | "which is what allows colours to be reused" | "which allows colours to be reused" |
| L9 novelty | "which is what makes an independent second source worth having in the first place" | "which is why an independent second source is worth having at all" |
| L9 novelty | "it is what removes the hypothesis" | "it removes the hypothesis" |
| L9 identity | "\S Novelty says what it is" | "\S Novelty names it" |
| L8 ridge | "$118/27$ is what the measurement returns when" | "The measurement returns $118/27$ when" |
| L8 novelty | "which is what companion paper L1's searches cover" | "which companion paper L1's searches cover" |
| L8 depth1 | "That the object is algebraic is what the earlier null results were missing" | "The earlier null results missed that the object is algebraic" |
| L8 frame | "This is what makes the rest computable" | "The rest is computable because of this" |
| L5 ×3, L7 ×4 | pre-existing "is what" from round 2, missed then | plain forms |

**B. Rhetorical inversion and punch closers.**

- L8: "Sharpness is usually where a result stops. Here it is where this paper
  starts." -> "...This paper starts there." The inversion is the banned
  closer form, one sentence early.
- L8: "What it buys is not brevity. It says what the depth variable *is*: ...
  Depth is a coupling constant." -> one sentence, no three-beat build.
- L9: "Connectivity is never tested. It is recovered from cancellation." ->
  semicolon, one sentence.
- L9: "The proof is five lemmas." -> "The proof runs in five lemmas."
- L9: "This half is proved: it is Lemma 1." -> "Lemma 1 proves this half."

**C. "The honest X" as a framing device.** Four instances in two days, which is
a habit rather than a word choice.

- L6 §k6 "The honest summary of what k=6 did to this paper" -> "What k=6 did to
  this paper".
- L6 §novelty "The honest shape of the contribution" -> "What the contribution
  is".
- L8 §crossover "The honest summary is that the resummation..." -> the sentence
  itself.
- L9 §novelty "So the honest summary is a narrow one" -> "The summary is a
  narrow one".

**D. Editorializing and decoration.**

- L8: "it is worth being explicit about the direction of the evidence" -> "The
  direction of the evidence is the part to keep in view".
- L8: "That is a *weak* negative and is worth saying why" -> "That negative is
  *weak*, for a stateable reason".
- L8: "the flat mode is the honest critical mode" -> "the critical mode".
  ("honest" was doing nothing; it came from the source note's voice.)
- L5: "which is the strongest cross-check in this paper: two methods sharing no
  machinery --- one series extrapolation, one interval-arithmetic certificate
  --- and no disagreement" -> the superlative and the paired-dash aside both
  go; the two methods are named in plain apposition.
- L6: "unweakened and now tested one row further" -> "now tested one row
  further".
- L6: "Item 2 is the one that costs something, and it costs less than item 3
  failing would have" -> "Item 2 costs less than item 3 failing would have".
- L7: "What this does *not* do is prove Conjecture 1" -> "This does *not*
  prove Conjecture 1".
- L5: "What survives the collision is narrow and stated as such" -> "What
  survives is narrow".

## Logged and KEPT, with reasons

- **"measured, not proved" and its family**, throughout. Contrastive negation
  that the authorship split requires; round 2 ruled these load-bearing and the
  ruling stands.
- **L8's short declaratives** "The derivation of $\alpha$ is conditional.",
  "Convergence is not proved.", "Nothing here is called new." Each is a warning
  the ledger requires, and shortening a warning is not a tic.
- **L6's paired-dash asides** (density 3.05/1k, the corpus high). Read one by
  one, they carry mathematics — "$\Phi_2$ enters the $n^3$ coefficient,
  $\Phi_3$ only the constant", "through $n = 70$ for $k \le 5$, $n = 78$ for
  $k = 6$" — not rhythm. Kept, and flagged here so the next round does not have
  to re-decide it.
- **L9's "the mathematics is classical; the specific rule is proved here"** —
  reads as balanced rhetoric and is the paper's actual disposition after the
  collision. Kept.
- **"is exactly"** where it means exactness ("$k = 2c + t$ is exactly their
  $k = e + 2f$", "an exponential enhancement per unit chain length is exactly a
  square-root branch point"). Kept; these are claims of identity, not
  intensifiers.

## What this round says about the process

The prose written in a day scores three to nine times the human control on the
same constructions the campaign already ruled on. The rules did not fail; they
were not applied, because the sweep is a separate pass and the new text
postdated it. Cheapest fix available: run `density.py` before committing new
paper prose, not in a campaign afterwards.
