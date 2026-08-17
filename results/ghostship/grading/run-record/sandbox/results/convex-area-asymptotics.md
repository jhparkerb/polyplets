# Exact asymptotics of the area statistic on convex king animals

Session 05 result. Builds on the s04 Temperley q-series solution
(`docs/proofs/convex-area-q-temperley.md`). Scripts:
`experiments/s05_beta_forms.py`, `s05_terms60.py`, `s05_asymptotics.py`,
`s05_secondpole.py`; receipts `out_s05_*.txt`.

## The theorem-shape result

Let a(n) = number of convex king animals with n cells (the convex-mirage
sequence 1, 4, 16, 61, 221, ...). Define the q-Bessel-type function

    K(q) = Σ_{m≥0} (-1)^m (2 - q^m) q^{m(m+1)/2} / (q;q)_m^2
         = 2·J(1;q) - J(q;q),   J(x;q) = Σ_m (-1)^m x^m q^{m(m+1)/2}/(q;q)_m^2

with (q;q)_m = Π_{j=1}^m (1-q^j). Then, writing q_c for the smallest
positive zero of K,

    mu = 1/q_c = growth constant of a(n),   and   a(n) ~ A · mu^n

with the amplitude given by the residue formula
A = -c1(q_c)·alpha(q_c) / (K'(q_c)·q_c), where alpha, c1 are the explicit
analytic q-series of the s04 solution (F(1,1,q) = c0 + c1·alpha/K).

    q_c = 0.31959671805938746551860289198271392361450837764097015755666
          00073276290433164538180810697892408732774692020193...
    mu  = 3.12894326973088625227744799538775416053209122190439413496497
          46499492443858371825761582306328816478323443262888...
    A   = 0.97445221313500464915132942086024332742538445801511603159338
          928033365080770674763415213812142916812547011232703...

Neither mu nor q_c is in OEIS (digit searches: null). Verification:
a(n)/(A·mu^n) - 1 = +1.6e-16 at n=60 (exact terms, `out_s05_terms60.txt`),
decaying geometrically at exactly the predicted subdominant rate (below).

### Provenance of K (proved symbolically)

The s04 Temperley denominator 1 - beta(1) at x=y=1 telescopes to K:
beta = Σ_{n≥0} T(q^{n+1}) Π_{j=1}^n R(q^j) with R(z) = -z/(1-z)^2,
T(z) = z(2-z)/(1-z)^2 (king), giving Π R = (-1)^n q^{n(n+1)/2}/(q;q)_n^2.
Verified as exact series identity to q^40 against the solver's own beta
(`out_s05_beta_forms.txt`). The control (polyomino) case gives
T(z) = z/(1-z)^2 and denominator J(q) := J(1;q).

## Literature anchor (control): exact hit on both constants

The control denominator's smallest zero is **the defining equation of the
Klarner–Rivest polyomino constant** (OEIS A276994): "smallest positive
root of Σ (-1)^n z^(n(n+1)/2)/(Π_{k=1..n} 1-z^k)^2 = 0" — literally J(q)=0.
Our computed values reproduce ALL published digits:

  - growth: 2.3091385933304947310987203050172125319118144725816284016944
    029002844564407483... = A276994 (Kotesovec's d in A067675; ~75 digits)
  - amplitude: 2.9195985097136070553847095156513356859151689414730565863
    0679268977185942... = Kotesovec's c in A067675 (~71 digits)

So the residue machinery is anchored to the literature at full precision on
the polyomino case; the king constants above are its exact analogs and are
NEW. (A276994's comment notes Flajolet–Sedgewick 2009 p.662 printed this
constant incorrectly.)

## Directed subfamilies (same mu, new amplitudes)

The directed GF is F00 + F10 = F00 + alpha/K, so directed-convex families
share mu with the full family; the amplitude drops the c1 factor:
A_dir = -alpha(q_c)/(K'(q_c)·q_c).

  - king directed (s04's new sequence 1,3,10,33,107,...):
    A_dir = 0.37545302027992473174348924381907282070710016721066507...
    (rel. err. -1.1e-18 at n=60)
  - control directed (= A067676, which has NO published asymptotics):
    A_dir = 0.65895554185211895992099818790088342084923176241464006...
    i.e. A067676(n) ~ 0.658955541852119·A276994^n — a small new result.

## Meromorphic structure; two-pole verification; non-D-finiteness route

All ingredient q-series (alpha, beta, c0, c1, the 2x2 determinant det)
converge normally on compacts of |q| < 1, so F(1,1,q) = c0 + c1·alpha/K
is meromorphic in the unit disk with poles confined to zeros of K and det.
Numeric facts (110-digit arithmetic, `out_s05_asymptotics.txt`,
`out_s05_secondpole.txt`, `out_s05_zeros_scan.txt`):

  1. K > 0 on (0, q_c); det has constant sign and |det| > 0.07 on
     (0, q_2]; c1·alpha ≠ 0 at q_c — the dominant singularity is a SIMPLE
     POLE at q_c (residue cross-checked against (q_c-q)·F numerically).
  2. Second zero q_2 = 0.664430094083357809... (king; 0.692748... control):
     the SAME residue formula at q_2 predicts the subdominant correction
     A2·mu2^n, mu2 = 1/q_2; empirical residuals (a(n) - A·mu^n)/mu2^n from
     exact terms converge to the predicted A2 (rel. err. -1.1e-2 full /
     -2.8e-3 directed at n=60, shrinking). Error decay of the leading
     asymptotic matches (q_c/q_2)^n exactly.
  3. K has ≥37 real zeros in (0, 0.995) (control J: ≥34), accumulating at
     q = 1 (the scan's 0.001 step undercounts near 1); residues nonzero at
     the first four (checked). F(1,1,q) thus shows infinitely many poles
     in [0,1) — a D-finite function has finitely many singularities, so
     THIS is the route to proving the area sequence non-D-finite:
     (i) prove K has infinitely many zeros in (0,1);
     (ii) prove c1·alpha does not vanish at infinitely many of them.
     Both statements are about explicit q-series.

## Summary table

|                              | growth mu        | amplitude A       |
|------------------------------|------------------|-------------------|
| convex king (NEW)            | 3.12894326973089 | 0.974452213135005 |
| directed convex king (NEW)   | 3.12894326973089 | 0.375453020279925 |
| convex polyomino (=A067675)  | 2.30913859333049 | 2.919598509713607 |
| directed convex poly (A067676, amplitude NEW) | 2.30913859333049 | 0.658955541852119 |

mu(king) = 1/(smallest zero of 2J(1;q) - J(q;q));
mu(poly) = 1/(smallest zero of J(1;q)) = Klarner–Rivest constant A276994.

## Open

- Prove (i)/(ii) above → non-D-finiteness theorem for the area sequence.
- The king constant mu and q_c deserve ~100-digit certified values (current
  values are 110-digit working precision, bisection-converged; error is
  dominated only by series truncation at 1e-100).

## Addendum (session 10): all constants CERTIFIED

`experiments/s10_certify_amplitude.py` (receipt `out_s10_certify_amplitude.txt`)
re-derives everything above with exact-rational interval arithmetic
(Fraction endpoints, outward rounding to Z/10^90, dual intervals for the
catalytic s-derivative, explicit rational tail bounds on every nested
q-series of the Temperley solution; rigor chain in the script docstring).
Marches: king = s06 rerun with tighter Lipschitz bound (L=11.73 vs 13.60);
control = NEW (windows .38/.44/.45). Certified enclosures (width ~1e-42
to ~1e-44; digits shown are exact):

  king:    q_c  = 0.31959671805938746551860289198271392361450837 7...
           mu   = 3.12894326973088625227744799538775416053209122 ...
           A    = 0.97445221313500464915132942086024332742538 4...   (44)
           A_dir= 0.3754530202799247317434892438190728207071001 ... (45)
           alpha= 0.5114252387864446468287030907410268638981908    (45)
           c1   = 2.595403846820800438797900225565237213523294     (44)
           K'   = -4.262105969152381600646524387364205537887881    (45)
  control: q_c  = 0.43306192312939066458461696541898370854183467 7... (46)
           mu   = 2.30913859333049473109872030501721253191181447 ...  (=A276994)
           A    = 2.9195985097136070553847095156513356859151      (42)
           A_dir= 0.6589555418521189599209981879008834208492317   (45)

The control enclosures CONTAIN all published Kotesovec digits (A067675
amplitude and growth constant = Klarner-Rivest A276994) — the machinery is
literature-anchored at certified precision. Also certified at q_c, both
modes: K'(q_c) != 0, det(q_c) != 0, c1(q_c)*alpha(q_c) != 0, so F(1,1,q)
has a SIMPLE POLE at q_c with certified nonzero residue
(-c1*alpha/K' = 0.3114317292236542239905877329508557019044219 king /
1.26436694538227764216337069536623455631280 control).
s06 OPEN (c) is closed; the "certified error bounds" OPEN of this doc too.
