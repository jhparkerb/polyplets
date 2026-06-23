# Verification: hole-free growth gap lambda_0 < lambda (polyplets) and the square-lattice contrast

Date: 2026-06-22. Status: analysis on EXISTING data only (no compute jobs launched).
Triggered by the "VERIFY before using" flag on the 2026-06-22 hunt
(docs/research-log-2026-06-22.md, "three fresh hunts").

## TL;DR verdict

1. **lambda_0 < lambda for polyplets: SUPPORTED.** The hole-free fraction
   A_0(n)/a(n) genuinely decays exponentially with base ~0.977 over n=4..18, and
   successive-ratio extrapolation gives a persistent gap: lambda ~ 7.09-7.10 vs
   lambda_0 ~ 6.93-6.94 (ratio lambda_0/lambda ~ 0.977). The gap is robust to the
   extrapolation window. The hole-free subclass really does grow strictly slower.

2. **The "0.978^n exponential, decisive over sub-exponential" claim: MOSTLY RIGHT,
   but slightly overstated.** Exponential (base 0.9783) clearly beats pure-power and
   stretched-exponential fits (RMS 1.1e-3 vs 1.6e-2 vs 8.6e-3 in log R). However the
   exponential residuals show a systematic *arch*, and a geometric x power model
   R ~ n^0.016 * 0.9768^n fits 3x better (RMS 3.8e-4). The power correction exponent
   is tiny (theta ~ 0.016 ~ 0), so the decay is genuinely exponential-dominated --
   but the clean "decisive exponential" RMS comparison in the log understates the
   residual structure. Bottom line: base ~0.977, exponential is the right model.

3. **The square-lattice CONTRAST: FALSE.** This is the headline correction. The hunt
   framed lambda_0 < lambda as "OPPOSITE the square lattice (where the simply-connected
   subclass shares lambda, sub-exponential decay)." The data flatly contradicts this.
   For ordinary square polyominoes the hole-free fraction A006724(n)/A001168(n) ALSO
   decays exponentially, with base ~0.977 -- *the same behavior, the same base* as the
   king lattice. There is no contrast. The interesting framing ("opposite the square
   lattice") evaporates: both lattices behave identically at finite n.

## Data and provenance

Total fixed polyplets a(n) = A006770 (king-move animals), n=1..19:
- Source: results/b006770.txt. n<=18 are published terms; n=19 = 151609203011580 new,
  two-algorithm confirmed (method-a19.md).
- 1, 4, 20, 110, 638, 3832, 23592, 147941, 940982, 6053180, 39299408, 257105146,
  1692931066, 11208974860, 74570549714, 498174818986, 3340366308393, 22471158811164,
  151609203011580.

Hole-free A_0(n) (4-connected-background "Jordan dual" convention), n=1..18:
- Source: oeis/draft-A0-holefree.txt (== results/holes.md "4-bg" line, ==
  results/holes_n18.txt and holes_n18.dalby.txt column-0). Exact via column transfer
  matrix, validated byte-identical to per-animal flood for n<=14, and n=15..18
  reproduced on a second CPU architecture (clang/ARM vs gcc/x86).
- 1, 4, 20, 109, 622, 3664, 22094, 135609, 843941, 5310754, 33724862, 215793158,
  1389673091, 8998648488, 58548155506, 382526638033, 2508473632910, 16503616943998.

Convention note (matters): a(n)=A006770 uses 8-connected (king) FOREGROUND adjacency;
the hole-free count uses 4-connected BACKGROUND (Jordan-dual) for what counts as a hole.
The draft-A0 %C confirms the universe is the same A006770 (A_0 = A006770 minus the holed
count, smallest holed polyplet = 4-cell diamond, so A_0(4)=109). So A_0(n)/a(n) is a
well-posed fraction of the SAME object set. (There is also an 8-bg variant 1,4,20,110,
638,... that equals A006770 for longer; it is not what the lambda_0 claim used. Using it
would only strengthen "no contrast", since it tracks A006770 even more closely.)

## Polyplet ratio analysis

A_0(n)/a(n) and the per-step decay base R(n)/R(n-1):

```
 n   a(n)             A0(n)            A0/a       R(n)/R(n-1)
 4   110              109              0.990909   0.990909
 6   3832             3664             0.956159   0.980754
 8   147941           135609           0.916642   0.978792
10   6053180          5310754          0.877349   0.978232
12   257105146        215793158        0.839319   0.978054
14   11208974860      8998648488       0.802807   0.977998
15   74570549714      58548155506      0.785138   0.977990   <- minimum
16   498174818986     382526638033     0.767856   0.977989
17   3340366308393    2508473632910    0.750958   0.977993
18   22471158811164   16503616943998   0.734436   0.977999
```

Note the base R(n)/R(n-1) bottoms out at n=15-16 (~0.97799) and ticks back UP -- the
signature of a sub-exponential (power) correction on top of pure geometric decay, NOT a
clean constant. Magnitude of the wobble is tiny (~1e-5), so the geometric base ~0.978 is
solid; the "pure geometric" reading is an idealization.

Decay-model fits (log R on n=5..18):
- exponential   R ~ 0.97829^n          RMS(logR) = 1.14e-3   (arched residuals)
- power         R ~ n^-0.225           RMS(logR) = 1.63e-2
- stretched .5  R ~ exp(-0.143 sqrt n)  RMS(logR) = 8.58e-3
- geo x power   R ~ n^0.016 * 0.97681^n RMS(logR) = 3.76e-4  (best; theta~0, so ~geometric)

So: exponential is decisively the right family (consistent with the hunt), base ~0.977.

Growth-constant extrapolation (1/n linear fit on a(n)/a(n-1) and A0(n)/A0(n-1)):
```
 tail from   lambda    lambda_0   gap     lambda_0/lambda
 n=8         7.0921    6.9309     0.161   0.97727
 n=11        7.0964    6.9383     0.158   0.97773
 n=14        7.0989    6.9422     0.157   0.97793
```
Neither series has converged (both successive ratios still climbing at n=18: a-ratio
6.727, A0-ratio 6.579), so the absolute numbers are soft -- but the GAP and the ratio
lambda_0/lambda ~ 0.977 are stable across windows and consistent with the direct R(n)
base. lambda ~ 7.09-7.10 here is a bit below the project's headline lambda ~ 7.13
(GF-pole methods push it up), but lambda_0 < lambda holds regardless.

## Square-lattice check (the shaky premise) -- CONTRAST IS FALSE

Ordinary square polyominoes, OEIS data:
- all fixed: A001168 (in repo, results/king_not_rook.py): 1,2,6,19,63,216,760,2725,
  9910,36446,135268,505861,1903890,7204874,27394666,104592937,400795844,1540820542,...
- hole-free (simply-connected) fixed: A006724: 1,2,6,19,63,216,756,2684,9618,34843,
  126905,463600,1701384,6276971,23234271,86246558,320817767,1195779728,...
  (smallest holed square polyomino is the 7-cell ring, so they first differ at n=7:
  756 vs 760.)

```
 n   all(A001168)   holefree(A006724)  hf/all    R(n)/R(n-1)
 7   760            756                0.994737  0.994737
10   36446          34843              0.956017  0.985042
12   505861         463600             0.916457  0.976852
14   7204874        6276971            0.871212  0.974907
16   104592937      86246558           0.824593  0.972246
18   1540820542     1195779728         0.776067  0.969536
```

Decay-model fit for the square lattice (log R on n=7..18):
- exponential  base 0.97724  RMS(logR) = 1.07e-2  (same arched residual)
- power        p = 0.2646    RMS(logR) = 2.09e-2

The square lattice's hole-free fraction decays exponentially with base ~0.977 -- to
two decimals the SAME base as the king lattice (~0.978). Far from being "shared lambda
/ sub-exponential decay," the square hole-free subclass has a growth constant strictly
below the Klarner constant by the same multiplicative factor. Implied square lambda_0 ~
0.977 * 4.0626 ~ 3.97 < 4.0626.

This makes physical sense and is the expected behavior: forbidding holes is an
exponentially-costly constraint (each unit of area carries an independent ~constant
probability of enclosing a hole as n grows), so on ANY 2D lattice the hole-free fraction
should decay geometrically and lambda_0 < lambda. The king and square lattices are not
opposite; they agree.

Where did the "square lattice shares lambda" premise come from? Likely a confusion with
a different, true statement: the *perimeter/area exponents* (theta, the universality
class) are shared between hole-free and all polyominoes, and self-avoiding POLYGONS
(which bound simply-connected regions) share the SAP growth constant with polyominoes in
some asymptotic senses. But the COUNT of hole-free polyominoes as a fraction of all
polyominoes is not constant and not sub-exponentially decaying -- it decays
geometrically, just like the king case. Klarner (papers/klarner.pdf) defines t*(n)
(simply-connected free animals) and only states the trivial bound; he makes no
equal-growth-rate claim. No paper in papers/ asserts equal hole-free growth.

## Verdict

| claim | verdict |
|-------|---------|
| lambda_0 < lambda for polyplets | SUPPORTED (gap ~0.16 in lambda, ratio ~0.977, robust) |
| A_0/a decays ~exponentially, base ~0.978 | SUPPORTED (best-fit base 0.977-0.978; "decisive over sub-exp" slightly overstated -- there is a small power correction, theta~0.016) |
| decay is PURELY geometric (constant base) | OVERSTATED -- base wobbles ~1e-5, min at n=15-16 then rises; tiny power correction present |
| "OPPOSITE the square lattice" / square hole-free shares lambda | **FALSE** -- square hole-free fraction decays exponentially with the SAME base ~0.977; no contrast exists |

Recommendation: keep "lambda_0 < lambda for polyplets, hole-free fraction decays like
~0.977^n" -- it is real and quantitatively supported. DROP the square-lattice-contrast
framing entirely; if anything the headline is "hole-free animals grow exponentially
slower on BOTH the king and square lattices, by nearly the same factor (~0.977)" -- a
universality-flavored *agreement*, not a contrast.
