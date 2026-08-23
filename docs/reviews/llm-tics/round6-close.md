# Round 6 — the close

2026-08-23. There is no round 6. This file says why, and records the corpus's
final numbers so the next person does not have to re-derive them from the
ruler.

## Where the campaign ends

Ruler: `docs/reviews/llm-tics/density.py`, per 1000 prose words, against the
two-paper P control (`technical-report.tex`, `polyplets-report.tex`).

| construction | frozen baseline | now | P control | verdict |
|---|---|---|---|---|
| dash-aside | 2.20/1k | **0.16** | 0.40 | done, and under the control |
| cleft | 0.92 | 0.23 | 0.13 | done |
| serves-as | — | 0.00 | 0.00 | done |
| scaffold | — | 0.00 | 0.00 | done |
| contrast-neg | 0.96 | 0.79 | 0.40 | **stopped deliberately** |
| punch | — | 1.02 | 0.40 | **stopped deliberately** |

Round 5's argument for stopping on the last two stands and is not repeated
here: read in context, most of what those two regexes catch is carrying a value
or an epistemic status rather than a habit. `round5-L6.md` walks L1's six
contrast-negs one at a time and keeps all six, and every one of them is a
distinction the sentence exists to make.

The plan's own ground rule was that rewriting to hit numbers produces flat
mush. Two markers at roughly twice a control drawn from jasonp's own prose is
not the mush threshold, and chasing them would be.

## The corpus these numbers describe

Six manuscripts, not ten. The 2026-08-23 contraction
(`docs/l-corpus-contraction.md`) merged L2 into L1, L7 into L5 and L10 into L8,
and withdrew L9. `density.py` now enumerates `paper/L[0-9]*.tex` rather than
carrying a frozen list, so the ruler survived the change as a measurement
instead of a `FileNotFoundError`.

| | words | contrast-neg | cleft | dash-aside | punch | mean-len |
|---|---|---|---|---|---|---|
| L1 | 7860 | 0.89 | 0.38 | 0.00 | 1.78 | 22.4 |
| L3 | 4485 | 0.89 | 0.00 | 0.00 | 0.67 | 24.1 |
| L4 | 2545 | 0.39 | 0.00 | 0.00 | 0.39 | 23.1 |
| L5 | 6461 | 1.08 | 0.00 | 0.00 | 0.46 | 27.5 |
| L6 | 4351 | 0.69 | 0.46 | 0.69 | 0.69 | 25.9 |
| L8 | 4703 | 0.43 | 0.43 | 0.43 | 1.49 | 23.4 |
| **overall** | **30405** | 0.79 | 0.23 | 0.16 | 1.02 | — |

## The merges were measured, not assumed

Connective prose written for three merges is new prose and had to face the
ruler. It introduced two paired-dash asides — one in L6's maximum-end lead, one
in L8's square-lattice framing — and both were rewritten the same day. The
cleft and dash-aside counts still showing in L1, L6 and L8 above are prose that
moved across a merge boundary rather than prose written today; each was checked
individually against the instance list.
