# Coin Flip is exactly one bit, and that is a theorem

Instruments: `experiments/tristruct/r3_char_landscape.py` (sweep),
`r3_char_landscape_certify.py` (certificate), logs `cl_h*.log`. Run
2026-08-14. Companion to `results/coin-lift-g2.md`, which killed Coin Lift by
measuring the lift to Z/4 and Z/8.

G2 asked whether the characteristic-2 collapse survives lifting, and it does
not. The natural follow-up is wider and is what this settles: **is there any
other field, ring, weighting, or auxiliary object that collapses the strip
functional the way GF(2) does?** No. The landscape of every such method is
indexed by a single parameter, and that parameter has been swept exhaustively.

## The object

At height H the strip automaton has states = king-connectivity partitions of a
column, alphabet = the 2^H - 1 nonempty column fills, and
f(w) = [the placed cells form exactly one king-connected component]. It is
deterministic. Let M be its observability matrix over Z: rows the reachable
states, columns the distinct residuals `a o delta_w`. Determinism makes every
residual a 0/1 vector, so there are finitely many, and they generate the
Hankel column module. Write r = rank_Q(M), d_p = r - rank_{F_p}(M), and N for
the number of distinct residuals — so **rank_Q <= N**, and N is computed, not
estimated.

Any strip method that multiplies a state vector by one matrix per column and
reads a scalar at the end — that is, any weighted automaton over a ring — is
covered below. That class contains Coin Flip, Coin Roll, Biased Coin Flip,
Coin Lift, every cut-and-count variant with any auxiliary group, and the
incumbent and Motley themselves.

## Four theorems

**T1 — extension fields buy nothing.** For any field F, rank_F(M) depends only
on char F. M has entries in the prime field; rank is the vanishing pattern of
minors; minors lie in the prime field. So GF(2^k) on this matrix *is* GF(2).
Biased Coin Flip's GF(2^k) buys a false-pass probability of 40/2^k and not one
dimension of compression, and it never could.

**T2 — multiplicative grading is exactly rank-preserving.** The area-graded
Hankel entry is `t^|u| f(uv) t^|v|`, so the graded matrix is `D M D'` with D,
D' invertible diagonal. Same rank over any ring in which t is a unit. Two
consequences, one good and one closing: **Coin Roll is free by theorem** — the
area grading that gives every n in one run costs exactly zero dimensions, not
"zero as far as H = 9 measured" — and **no weighting of that shape can ever
help**, so there is nothing to search for there.

**T3 — the whole landscape is indexed by the characteristic.** Let R be any
commutative ring with 1 != 0 and let f have an R-linear realization of
dimension D (any weighted automaton: initial vector, one matrix per symbol,
final vector). Take a maximal ideal m of R. Reducing every entry gives a
realization of dimension D over the field R/m, and Hankel rank over a field is
a floor on realization dimension. So

    D  >=  rank over the prime field of R/m  >=  min over primes p of rank_{F_p}(M)

using T1 for the second step, and rank_{F_p} <= rank_Q to fold in
characteristic 0. **The only thing that can vary is the characteristic.** No
cleverness in choosing the ring, the auxiliary group, the weighting or the
encoding escapes this — cut-and-count with a group G is an F_p-linear
realization whenever p divides |G|, and it lands in the same bound.

**T4 — only finitely many characteristics can matter, and the bound is
explicit.** If rank_{F_p} = r - d_p then at least d_p invariant factors of M
are divisible by p, so p^{d_p} divides the r-th determinantal divisor D_r.
D_r divides every nonzero r x r minor, and Hadamard bounds any such minor of a
0/1 matrix with columns of length r by r^{r/2}. With r <= N,

    d_p * ln p  <=  (N/2) * ln N  =:  B          for every prime p         (*)

Distinct primes are coprime, so `prod_p p^{d_p}` divides D_r and (*) holds in
its sum form as well — `sum_p d_p ln p <= B`, over every prime at once. B is a
single number per height and every drop anywhere in the landscape is paid for
out of it; the sum form is what makes the pinning below valid. Two uses: a
prime that matches characteristic 2 needs
d_p >= d_2, hence **ln p <= B / d_2** — an explicit bound below which every
prime can simply be tested; and (*) also **pins rank_Q** rather than assuming
some large prime is generic, since a true rank exceeding the observed maximum
by 1 would have to drop at every prime tested, costing sum(ln p) > B.

## The sweep, certified

Every prime below the T4 bound tested by direct computation; everything above
excluded by (*). The certifier refuses to print a verdict unless consistency,
pinning, and completeness all close — it voided its first H = 6 run for an
untested-prime gap of exactly this kind.

| H | states | N | B | rank_Q (pinned) | primes tested | T4 cutoff | every drop, over all primes |
|---|---|---|---|---|---|---|---|
| 6 | 126 | 45 | 85.6 | 35 | 4,642 | 44,633 | p=2: −8 (22.9%). **Nothing else, anywhere.** |
| 7 | 322 | 103 | 238.7 | 88 | 417 | 2,853 | p=2: −30 (34.1%); p=3: −1 (1.1%) |
| 8 | 834 | 241 | 660.9 | 204 | 217 | 1,318 | p=2: −92 (45.1%); p=3: −3 (1.5%) |
| 9 | 2,187 | 577 | 1,834.2 | 501 | 196 | 849 | p=2: −272 (54.3%); p=3: −13 (2.6%) |

Read the H = 6 row carefully: **p = 2 is the only prime in the entire universe
that drops the rank at all.** Not the only one below some cutoff — the only
one, with 4,642 primes measured and the infinitely many above 44,633 excluded
by the bound. From H = 7 on, exactly one other prime moves at all, p = 3, and
it never exceeds 2.6% against characteristic 2's 54.3%.

The trend across the four heights is the one that matters for extrapolation:
characteristic 2's share of the rank *grows* — 22.9%, 34.1%, 45.1%, 54.3% —
while p = 3's stays pinned near a couple of percent, and the cutoff below
which any competitor must live *falls*, 44,633 → 2,853 → 1,318 → 849. The gap
is widening in the direction that closes the question, not opening it.

## What this settles

- **Coin Flip cannot be extended.** Any commutative-ring-linear strip method
  has dimension at least min_p rank_{F_p}(M), the minimum is attained at
  p = 2, and every other characteristic sits at or within a hair of rank_Q.
  There is no second collapse to find, at any prime, in any extension field,
  under any grading, with any auxiliary group.
- **One deterministic bit is the whole prize, and it is optimal.** Not "the
  best we found" — the unique minimiser of a bound that every method in the
  class obeys.
- **Coin Roll's freeness is upgraded from measurement to theorem** (T2).
- **Biased Coin Flip's GF(2^k) is confirmed to buy only probability** (T1).
- `docs/coin-lift-plan.md` §4's separate lead survives untouched and is
  sharpened: the mod-p rank at H = 21 is a ~17x floor below the incumbent that
  **nothing constructs**, and T3 now says that floor is the *best* any
  ring-linear method can do in characteristic 0 — it does not say anything
  attains it.

## What it does not settle — scope, stated plainly

- **Non-linear methods are untouched.** The floor is about weighted automata;
  a method that is not a per-column linear map is outside it.
- **A different functional is untouched.** This is about f = "exactly one
  king-connected component" on the strip automaton. A decomposition that
  counts something else and assembles a(n) differently is not bounded here.
- **Non-commutative R is not claimed.** T3's reduction wants a maximal ideal
  with a field quotient. Matrix-ring quotients are not covered; I did not
  chase it because no proposal on the table needs it.
- **The certificates are per height, H <= 9.** T1–T3 are height-independent;
  T4's bound and the sweep are computed per height, and the higher the height
  the *tighter* the bound gets (44,633 → 2,853 → 1,318 → 849 across
  H = 6..9),
  because d_2 grows faster than B. The pattern is one-directional, but H = 10
  and up are unswept, and no claim is made for them beyond T1–T3.
