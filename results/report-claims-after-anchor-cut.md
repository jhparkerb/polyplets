# Report claims the anchor cut makes wrong

2026-08-14. `paper/polyplets-report.tex` only — `paper/technical-report.tex`
carries no tier apparatus and is unaffected. **Nothing here has been edited.**
The manuscript is jasonp's prose; this is the list, for his decision, of what
the anchor cut (`results/anchor-cut-map.md`) falsifies or improves.

All of it is contingent on the two conditions the map states: the depth-`j`
identity re-derived independently of `experiments/severance_w3_depths.py`, and
Motley's own rows as the inputs. Until both, this list is what *will* change,
not what has.

## 1. The one factual error — line 528

> "$P_{19}$, fitted from exactly these two cells, has no independent holdout,
> **nor ever will**, the sequence closing at $a(40)$"

The "nor ever will" is false, and not marginally: `mu_19` — hence `P_19` — pins
from columns 18 and 19 at depth 2 below the staircase's onset, so `T(39,20)`
and `T(40,21)` stop being fit points and become **predictions**. The depth-3,
4 and 5 instances are then exactly the independent holdouts the sentence says
cannot exist. Depths 3, 4 and 5 are all validated
(`experiments/depth_swap_anchors.py`, guards 13 and 14).

The clause's premise — that a holdout must come from a *later* term, so a
sequence closing at $a(40)$ can never supply one — is what fails. The holdout
comes from a *shallower* column instead.

## 2. The tier that exists only because of that claim — lines 150–152

> "\tiertwominus{} & \tiertwo{} *minus* the held-out diagonal check. Covers
> $a(39)$ and $a(40)$, whose top real-swept strata lie on the one diagonal that
> no holdout can ever certify."

`\tiertwominus{}` is defined by the absence of a holdout for diagonal $k=19$.
That absence is what the cut removes, so on the report's own criterion
$a(39)$ and $a(40)$ move to `\tiertwo{}` and the tier has no members. Whether
to retire the macro or keep it defined and unused is jasonp's call.

Knock-on: line 197 (`$a(39)$--$a(40)$ \tiertwominus{}`) and line 525 (the grade
attaching to $a(39)$, $a(40)$).

## 3. The paragraph that argues the grade — lines 521–533

The ladder $P_{15}\to T(33,18)$, ..., $P_{18}\to T(39,21)$ is right and stays.
What changes is the sentence after it: the ladder no longer stops at $P_{18}$,
because $P_{19}$ and $P_{20}$ are pinnable and their onset cells are then
predicted rather than fitted. "What lacks certification is the cells, not the
code" is no longer the situation for those cells.

## 4. The T1 boundary — lines 140–143, 196, 286

> "\tierone{} ... Covers $a(1)$--$a(22)$"

With Motley's banked, gated $H\le16$ rows plus the cut, rows 17..34 reproduce
against the banked triangle (171 cells, 0 mismatches), by an algorithm that
never decides connectivity. Each Motley rung adds two more terms.

**This one needs a ruling rather than an edit.** `\tierone{}` is defined as
*two algorithms sharing no counting logic* agreeing. Motley-plus-the-cut is an
enumerating engine composed with a proved formula, not a second enumeration:
the swept cells are Motley's, the cells above the guard are derived. That is
strictly stronger than `\tiertwo{}`'s "one counting algorithm, decorrelated"
and weaker than two independent whole-row enumerations. It may want its own
tier, or an explicit widening of `\tierone{}`; the report should not quietly
absorb it into either.

## 5. Not a claim, but it dates the paper — line 477

> "transfer-matrix values are single-algorithm (\tiertwo{})"

True at the time of writing. Once Motley's rungs land, the range where this
holds shrinks by two terms per rung, and after Ticker Tape it is empty.
