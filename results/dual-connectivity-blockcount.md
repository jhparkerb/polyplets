# The dual-connectivity TM has no small-b regime, and the kill was understated

2026-08-22, executing `docs/last-orders.md` C2.2. Desk arithmetic; no compute
job. Probe: `experiments/dual_connectivity_blockcount.py`, five RED controls
green.

## Two results

**The variation is dead.** The dual's per-block-pattern cost is `b·Cat(b)` and
the incumbent's is `Cat(b)`, so the ratio is **exactly b, at every block
count**. It is not worse than the incumbent only at `b ≤ 1`, which is 0.0001%
of the frontier at H = 21. A hybrid that carries the dual where b is small has
no regime to live in — there is no b at which the dual wins, only one at which
it ties.

**The banked kill compared against the wrong baseline, in the conservative
direction.** `docs/lastditch-ideas.md` §6 puts `b·Cat(b) = 11,440` against
`Bell(b) = 4,140` at b = 8, a factor of 2.8. But the incumbent does not pay
`Bell(b)` per block pattern. It pays `Cat(b) = 1,430`, and the true factor at
b = 8 is **8**.

That is checkable to the digit rather than argued:

    sum_b C(H+1, 2b) * Cat(b)  =  Motzkin(H+1)
    Motzkin(22) - 1            =  400,763,222

which is exactly the banked H = 21 column-state count that
`docs/skeletonkey-reprompt.md` quotes for the incumbent. The identity holds at
every H tested (5, 10, 21) and is one of the five RED controls.

## The frontier's block-count distribution

Binary strings of length H with exactly b maximal runs of 1s number
`C(H+1, 2b)`, and the state count in each class is that times `Cat(b)`. At
H = 21:

| b | patterns | Cat(b) | incumbent states | dual states | ratio |
|---|---|---|---|---|---|
| 3 | 74,613 | 5 | 373,065 | 1,119,195 | 3× |
| 5 | 646,646 | 42 | 27,159,132 | 135,795,660 | 5× |
| 6 | 646,646 | 132 | 85,357,272 | 512,143,632 | 6× |
| 7 | 319,770 | 429 | 137,181,330 | 960,269,310 | 7× |
| 8 | 74,613 | 1,430 | 106,696,590 | 853,572,720 | 8× |
| 9 | 7,315 | 4,862 | 35,565,530 | 320,089,770 | 9× |

Cumulative share of the frontier:

| b ≤ | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
|---|---|---|---|---|---|---|---|
| share | 0.10% | 1.21% | 7.99% | 29.29% | 63.52% | 90.14% | 99.02% |

The mass sits at **b = 6–8**, i.e. around H/3, exactly where the dual is 6–8×
worse. The small-b tail the hybrid would have exploited is empty: b ≤ 3 is one
part in a thousand.

Totals at H = 21:

    incumbent   sum C*Cat(b)    =   400,763,223   ( = Motzkin(22) )
    dual        sum C*b*Cat(b)  = 2,840,372,305   ( = 7.1x )
    Bell        sum C*Bell(b)   =   941,574,417   ( = 2.3x )

The middle row is the honest number for the dual. The bottom row shows what
`Bell(b)` actually is here — an intermediate quantity 2.3× the incumbent, not
the incumbent's own cost.

## What this changes

**The closed door stays closed, and closes harder.** §6's conclusion — "the
dual is *worse*, and the reason is the reason connectivity is the wall" — is
right. Its supporting comparison should read `b·Cat(b)` against `Cat(b)`, a
factor of b, rather than `b·Cat(b)` against `Bell(b)`, a factor of 2.8 at the
one block count quoted. Correcting it makes the kill stronger and makes it
uniform in b instead of holding only "at the block counts that dominate".

**The variation C2.2 proposed is answered and needs no further work.** It asked
for the block-count distribution "over a real frontier, which is banked data".
The distribution is `C(H+1,2b)·Cat(b)`, it sums to the banked state count
exactly, and it kills the hybrid without any measurement of a running job.

## Honest limits

- This counts **states**, which is what the closed door counts. It is not a
  measurement of per-state work, and a method with more states but a cheaper
  inner loop is not excluded by this arithmetic alone. The dual's inner loop
  has no reason to be cheaper — it carries a component count the incumbent does
  not — but that is an argument, not the measurement above.
- `Cat(b)` being the incumbent's per-pattern cost is established here by the
  Motzkin identity matching the banked total, not by reading the engine. The
  match is exact at H = 21 and the identity is standard, so this is strong, but
  it is inference from an aggregate rather than from `core/kink_column.h`.
- Nothing here bears on the *other* half of §6's kill, the doomed-configuration
  prune that forces the count to be carried at all. That argument is
  independent and untouched.

## Reproduce

    python3 experiments/dual_connectivity_blockcount.py --height 21

Instant. The five RED controls: run-count classes must partition all `2^H`
subsets; `sum C(H+1,2b)Cat(b)` must equal `Motzkin(H+1)` at H = 5, 10 and 21;
and `Motzkin(22)-1` must equal the banked 400,763,222.
