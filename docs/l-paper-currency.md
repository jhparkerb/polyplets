> **SUPERSEDED 2026-08-23 by `docs/l-corpus-contraction.md`.** This file
> describes nine manuscripts. Four of them no longer exist as manuscripts: L2
> went into L1, L7 into L5, L10 into L8, and L9 was withdrawn to
> `docs/proofs/cutcount-identity.md`. The one place this file is now actively
> wrong is its L8/L10 paragraph, which records the 08-22 decision as settling
> the application into a separate paper; jasonp's clarification on 08-23 is that
> "absorb" meant L10 becomes part of L8, and it now is. Everything else here is
> still readable as the currency ledger it was, against the merged papers.

# What the nine L papers would need to absorb

2026-08-22, executing `docs/last-orders.md` A2.4 and A2.5. **An inventory, not
an edit.** The L papers are machine-writable, but the readability campaign
(`docs/reviews/llm-tics/`) runs round by round gated on jasonp's say-so, so
nothing here touches a `.tex` file. This is the list of what has moved since
each paper was drafted, so that one decision can be taken across all nine
rather than nine decisions taken piecemeal.

All nine were drafted on or before 2026-08-18. Everything below postdates that.

## The short version

**Four of the nine are unaffected**: L2 (ternary spine), L5 (convex polyplets),
L6 (perimeter gradings), L9 (cut-count identity). Nothing since 08-18 touches
their subjects.

**Five have something to absorb**, and only one of the five is substantial.

## L8 — below the onset. The substantial one. **DECIDED AND DONE 2026-08-22.**

jasonp's decision, taken 2026-08-22: **absorb.** All three items below are now
in `paper/L8-below-onset.tex` — the external check as its own section, and the
two corrections as a remark in the frame section headed "what the k+1 integers
do not buy". The paper went 8pp to 9pp, its verification ledger carries the
square-lattice entry with its limit, and its novelty section records that the
new section postdates the 2026-08-18 pass and has not been swept. Item 1's
"whether it joins L8 or stands separately" was settled the other way in the same
sitting: the application is `paper/L10-undertow.tex`, a separate paper, which
now cites L8 for the validation rather than carrying it.

Three things, in decreasing order of importance.

1. **The application is missing entirely.** L8 has the defect mathematics and
   nothing has the fact that those defects let a level be pinned from
   below-onset cells, which is what produced a(41). See
   `docs/undertow-chapter.md` — that material has no home, and whether it joins
   L8 or stands separately is a decision, not an edit.
2. **It has been validated outside the project** since L8 was drafted.
   `results/undertow-square-validation.md`: on the square lattice, where the
   counts are published, the below-onset fit equals the classical one and
   reproduces the tall cell it was denied, at every level tested. A paper about
   below-onset structure that omits its only external check is weaker than the
   work.
3. **Two corrections that a referee would find.** `docs/lastditch-ideas.md`
   §1a: each below-onset cell brings one equation *and* one unknown `D_j(k)`,
   so solving a whole column is a reformulation rather than extra redundancy —
   an earlier reading had it the other way. And §5: fitting a P-finite
   recurrence for `D_j` needs ~180 values of `k` where ~15 exist.

## L3 — the λ bracket. Less than `last-orders.md` A2.5 claimed.

**A2.5 overstated this and is corrected here.** It said L3 "does not develop the
barrier as the standalone negative the open-problem doc describes". L3 does
develop it: its *What that rules out* paragraph argues that multi-cell casing
only relocates the over-count, that required-cell types cannot forbid distant
overlaps, and — the load-bearing sentence — that "the king slack *grows* with
`n` where the rook method's saturates, which says eight-connectivity is
genuinely worse". It also closes the independent quasi-submultiplicativity
route on the same wall.

What is genuinely absent is smaller: the **general** statement. L3 argues the
barrier for the king lattice and for the specific methods it examines;
`docs/open-problem-lambda-bracket.md` states it as a property of the *method
class* — finite-type convolution bounds cannot reach λ, because slack that grows
with `n` is the signature of a non-local over-count and no finite window sees a
non-local constraint. Promoting the king-specific argument to the class-level
one is a paragraph, and it is the kind of negative result that survives having
no referee.

Two smaller items:

- `results/lambda-atlas-probe.md`: λ is not a function of coordination number.
  Two lattices at q = 8 give 7.11 and ≈8.97. L3's framing of what λ depends on
  can now cite a controlled pair rather than an intuition.
- `results/strip-fss-lambda-sensitivity.md`: if L3 quotes the strip ladder's
  non-convergence, the *inference* that a logarithmic term is required is
  withdrawn — the closure stands, the mechanism does not.

## L1 — the diagonal law. One extension.

`results/skeletonkey-parametric-master.md`: the master equation is parametric in
`b = |D|`, so the ledger that assembles the constants is no longer king-only —
the substitution is `b` for the 3 in the renewal chain, and the k = 4 leg agrees
with the wired king table by two routes sharing no code. L1 proves the law for
every row-local lattice; it can now say the *constants* are computable there
too, and `results/lambda-atlas-probe.md` exhibits a third instance of the class
L1 quantifies over, which makes the theorem less vacuous.

## L4 — not D-finite. One adjacent anchor.

`results/theta-universality.md` is not about D-finiteness, but it puts the
project's series-analysis machinery on an external footing for the first time —
the same code reproduces the published square-lattice growth constant to six
digits. L4 leans on that machinery's credibility; a one-line cross-reference
costs nothing.

## L7 — the subdominant amplitude. One correction, if it quotes the ladder.

Same as L3's second smaller item: `results/strip-fss-lambda-sensitivity.md`
withdraws the "term between 1/H and 1/H², most likely logarithmic" inference
while leaving the closure of the central-charge fit intact. L7 measures
exponentials of the same series by Prony's method and does not obviously depend
on the ladder, so this may be a no-op — worth one grep before assuming so.

## The decision this inventory is for

Three options, taken once across all nine:

- **absorb** — revise each paper to current state before release;
- **footnote** — add a dated "what has moved since drafting" note to each
  affected paper, pointing at the results files;
- **leave** — ship them as of their drafting date, which the loud draft banners
  already announce.

**Leave is defensible** and is what the banners are for. What is not defensible
is L8 shipping without either the application or the external validation, since
those are the two things that make its subject matter more than a curiosity.

## What this inventory does not cover

The per-result verification ledgers ("human verification: none") and the
per-paper bylines. Both are in `PRE-LANDING.md` as jasonp's decisions and are
deliberately not repeated here.
