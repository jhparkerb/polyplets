# A1.2 asked a question the tree had already answered — and here is what is actually open

2026-08-22, executing `docs/time-at-the-bar.md` A1.2. Re-run on ayr:
`experiments/tristruct/exactchange_minauto.py`, brute anchors green.

## The answer in one line

**A1.2's proposal — "redo probe 1 with N-keys as the labels" — is a re-pitch:
`results/exactchange-probes.md` §6 did exactly that on 2026-08-14, proved the
"if" direction and measured the "only if" exactly at H = 4..10, and §6 closes
with "Layer 1 of the basis hunt is closed."** What is open is layer 2, and §8
already names a sharper construction than the one A1.2 proposes.

This is the standing filter from `docs/skeletonkey-reprompt.md` doing its job on
the round's own file: grep the tree before calling anything new.

## Where A1.2 went wrong, in detail

A1.2 sets two files side by side and reads a gap between them:

> `results/skeletonkey-nfamily-merge.md` supplies a fourth candidate key that
> those three lacked … Redoing probe 1 with N-keys as the labels … asks the one
> question the three failed keys could not: is φ describable on a labelling that
> is already known to be a congruence?

Three things are wrong with that.

**The two files are about the same object and already say so.** The merge file's
opening is a reconciliation: it names `exactchange-probes.md` §6, says its own
merged column "reproduces Exact Change's own numbers at every height it
measured, including the 8,539 its `minauto` run banked at H = 12", and its
contribution is that the merge is *characteristic-free* rather than a GF(2)
fact. The class counts `8, 19, 43, 101, 239, …` are the same sequence in both
files because they are the same congruence.

**The question has a one-line answer, and it is trivially yes.** The N-key is
the Nerode congruence. φ(s) is the coordinate vector of s's Hankel row. Equal
Nerode class ⟹ equal Hankel row ⟹ equal φ. So φ factors through the N-key by
construction, and no computation was ever needed to establish it. The number
that looks like a tension — 8,539 classes against rank 1,818 at H = 12 — is not
one: a rank is the dimension of the span of the distinct rows, and it is always
at most their number.

**The table in A1.2 that reads as a negative is arithmetic.** It shows the
class/rank ratio diverging (1.33 → 4.70 at H = 12) and concludes "the merge is
not the collapse and increasingly is not". True, and it was never claimed to be:
`2.48^H` classes against `(4/9)·2^H` rank is exactly what §1 and §6 already
record separately.

## What is actually open: layer 2

`exactchange-probes.md` §8 states the live construction, and it is better than
the doubling schema A1.2 proposes. With `V_low` the span of rows avoiding the
top boundary row and `V_int` those avoiding both:

    dim V_int = 2^(H−2)                    exactly, H = 4..10
    dim V_low = (2^H − (−1)^H)/3 = J(H)    Jacobsthal, A001045
    r(H) − dim V_low = r(H−2)              arithmetically

telescoping to `r(H) = Σ_k J(H−2k)`, which is Barry's formula on the A034299
entry. **A1.2's `r(H) = 2r(H−1) ± ⌊(H+1)/2⌋` is the same sequence's other
recurrence** — a valid restatement, but the filtration is the one with a
subspace attached to each term, which is what a basis construction needs.

§8's own review is explicit about what is missing, and it is not a computation:

- **L1** `dim V_int = 2^(H−2)` — unproved
- **L2** `dim V_low = J(H)` — unproved
- **L3** an explicit isomorphism `V_H / V_low ≅ V_{H−2}`-pullback — unproved,
  and the review finding is that *only* `dim V_low` is a new measurement; the
  quotient identity is a subtraction with no map exhibited.

**L3 is the item.** Until a map is exhibited, "the recurrence is a construction"
is a hope about a subtraction.

## What this round did add: H = 12, and the gap §7 named

§7 records that the minimized automaton's ranks agree with A034299 and with the
independently-computed partition-automaton ranks "at every H ≤ 11
(two-implementation agreement; **H = 12 pending**, H = 13 would be minauto-only
and needs a second source before it counts)".

H = 12 was run:

| H | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | **12** |
|---|---|---|---|---|---|---|---|---|---|
| min states | 8 | 19 | 43 | 101 | 239 | 575 | 1,399 | 3,441 | **8,539** |
| rank | 6 | 15 | 27 | 58 | 112 | 229 | 453 | 912 | **1,818** |
| A034299 | 6 | 15 | 27 | 58 | 112 | 229 | 453 | 912 | **1,818** |

All OK, brute-force anchors at H ≤ 3 green (`H=2 W=3: 27`, `H=3 W=3: 286`,
`H=3 W=4: 1906`). **The pending cell is closed**: two-implementation agreement
now runs to H = 12, since the partition automaton had already banked 1,818
there. Cost on ayr: build 148.5 s, rank 874.7 s, ~17 min, 3.9 GB.

That is nine consecutive terms matching a four-term linear recurrence, still an
identification rather than a proof, and nothing here leans on it past the
measured range.

## H = 13 is the legitimacy test and is not launched

A034299 predicts `r(13) = 3643`. Extrapolating this run's ratios (rank ~8× per
height) puts it near **2 hours**, and it would be **minauto-only** — §7 says
plainly that needs a second source before it counts. It is over the one-hour bar
and it is jasonp's call, not a thing to slip in.

## What A1.2's "sentence that gets shorter" actually needs

A1.2 aimed at `results/mathematics.md` §7's "Nobody has a basis, and without one
it is not constructive". That sentence is unchanged and correctly so. The thing
that would change it is L3 — an explicit map, not another rank ladder — and no
amount of GF(2) linear algebra on 8,539 states produces one.

## Reproduce

    python3 experiments/tristruct/exactchange_minauto.py 12    # ayr, ~17 min, 3.9 GB
    python3 experiments/tristruct/exactchange_minauto.py 11    # ~2 min
