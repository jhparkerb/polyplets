# What the L-paper verifier actually reads

2026-08-23. `tests/l_paper_coverage_audit.py`, the P-paper coverage
measurement (`results/p-paper-verifier-coverage.md`) pointed at the L corpus.
Method: perturb the last digit of every numeric literal in a COPY of the
`.tex` and re-run `paper/verify_l_papers.py`. A literal whose perturbation
still passes is one the paper prints and no check reads.

It matters more here than on the P side. There the question was how much of one
guarded manuscript is guarded. Here **every one of the six manuscripts carries
a disclosure block reading "human verification: none"**, and only four of them
have any checks at all, so an unguarded literal has nothing else standing
behind it.

## The answer

| paper | pages | literals | guarded | unguarded |
|---|---|---|---|---|
| `L1-diagonal-law.tex` | 23 | 51 | 4 | **47** |
| `L3-lambda-bounds.tex` | 13 | 152 | 50 | 102 |
| `L4-not-dfinite.tex` | 10 | 22 | **17** | 5 |
| `L5-convex-polyplets.tex` | 21 | 144 | **0** | 144 |
| `L6-perimeter-gradings.tex` | 14 | 93 | 3 | 90 |
| `L8-below-onset.tex` | 15 | 69 | **0** | 69 |
| **corpus** | 96 | **531** | **74** | **457** |

74 of 531. For comparison, the technical report is 293 of 294
(`results/p-paper-verifier-coverage.md`). The whole sweep is **80 seconds** on one
core, because `verify_l_papers.py` runs in 0.16 s and needs no subprocess cache.

## The measurement is not vacuous

74 literals did go red, which is what shows the harness detects a wrong number
at all, and the ones that went red are the right ones:

- **L3's two headline constants**, `6.543` and `9.3154`, are both guarded, as is
  every rung of the certified ladder in both its printed precisions and the
  certificate `x = 2147/20000`.
- **L4's ψ-degree boxes** `181/180`, `462/461`, `1254/1253`, `3289/3288` are
  guarded on both sides of each pair, which is what puts the exclusion under
  test rather than the number.
- **L6's min-end constants** `187`, `470`, `1106` are guarded by
  `check_l6_min_end`'s sequence test.

The green control runs before every sweep: if the unmutated copy does not pass
on the box, the run exits 2 rather than reporting a wall of false "guarded".

## Two extractor changes from the P side, both widening

The P sweep is `[0-9]{4,}` with a lookbehind rejecting a leading `.`, which on
this corpus would have been nearly blind.

1. **Decimals count as one literal.** Without this the sweep cannot see `6.543`
   or `9.3154` — L3's entire result.
2. **The integer floor is 3 digits, not 4.** L6's min-end constants are
   `1, 6, 22, 68, 187, 470, 1106`; the floor is where those stop being noise.

Also: `96{,}065` is one literal and not the fragment `065`, and `R{0.56\textwidth}`
is a column width rather than a claim. Both were false positives the first run
produced and both are handled in the extractor.

## What is unguarded, by paper

**L5 (144 of 144) and L8 (69 of 69) have no verifier at all.** Not one number
either paper prints is read by any check. What that leaves unread includes:

- L5: `μ = 3.128943269730886…` and its 199-digit extension, `ν = 2.5145796…`,
  the 44-digit certified interval, the amplitude ratio `r` to 251 digits, every
  PSLQ box, and the whole four-block transfer table.
- L8: every entry of the `θ_j = j − 3/2` table with its error bars, the rate `9`
  at each depth, the derived constant `0.005138939956706…`, the amplitude
  ratios `1, 1, 3/2, 5/2, 4.370843, 7.866341, 14.441622`, the competing `118/27`
  the paper argues against, and the `57`-order fit with `144` holdout orders.

**L1 (47 of 51)** — the six L1 checks guard four numbers. The closed-form table
`tab:machine`, which is the paper's own tabulated output, is not read; neither
is the A308359 quadratic's coefficient set, which sits below the 3-digit floor.

**L6 (90 of 93)** — the two L6 checks reach the min-end sequence and the k = 6
division test, and nothing in the coefficient triangle, `tab:maxend`, or the
recentred basis.

**L3 (102 of 152)** — the best-covered of the four with checks. The unguarded
half is the over-count audit (`median slack 1.144`, `maximum 1.222`), the
window-lever table, and the `G_8(n)/a(n)` anchor row.

## What this is not

It is not a claim that any of the 457 is wrong. `verify_l_papers.py`'s 336
checks are green and the banked results behind the papers are checked
elsewhere. What is unmeasured is the link from that data to what these
manuscripts print — and on this corpus, unlike the P corpus, there is no human
reader standing behind the link either.

The audit is deliberately **not a gate**. Wiring it as one would demand that
every literal in six papers be guarded before any of them can change, which is
a bar the corpus does not meet and was never asked to meet. Its job is to say
where the exposure is.
