# The q->1- oscillation of K(q): figure-eight knot volume as phase constant,
# certified q_c/mu, and the corrected zero census
### (session 06)

K(q) = sum_{m>=0} (-1)^m (2-q^m) q^{m(m+1)/2}/(q;q)_m^2 is the s05 Temperley
denominator for convex king animals by area (mu = 1/q_c, q_c its smallest
positive zero); J(q) = sum (-1)^m q^{m(m+1)/2}/(q;q)_m^2 is the control
(convex polyominoes; Klarner-Rivest A276994).

## 1. Certified enclosure of q_c and mu (receipt: out_s06_certify_qc.txt)

Exact-rational (Fraction) certification chain, no floating point anywhere:
alternating-series bracketing of K (terms decrease from m=1 for q <= 0.34,
by a monotone ratio bound), the analytic bound K >= (1-4q+2q^2)/(1-q)^2 > 0
on (0, 29/100], a certified Lipschitz bound L = 13.603 >= sup|K'| on
[0.29, 0.33] (termwise sup bounds + tail majorization), and a 270-step
Lipschitz march that certifies K > 0 on (0, a_f], then K(b_f) < 0:

    q_c in (a_f, b_f],  b_f - a_f = 4e-46,  and q_c is the SMALLEST
    positive zero of K.

    q_c = 0.319596718059387465518602891982713923614508377[387..787]
    mu  = 1/q_c = 3.12894326973088625227744799538775416053209122[0468..4384]

45 digits of q_c and 44 digits of mu are now certified (s05's banked 40-digit
values confirmed in full). This resolves the enclosure part of s05 OPEN (c);
the amplitude constants remain uncertified.

## 2. Closed-form oscillation law (receipt: out_s06_saddle.txt)

Saddle-point analysis of K(e^-eps): with u = m*eps the summand is
h~(u) (eps/2pi) e^{g(u)/eps} (1+O(eps)), g(u) = -u^2/2 - 2Li2(e^-u) + pi^2/3,
using (q;q)_m = (q;q)_inf/(q^{m+1};q)_inf, the modular asymptotics of
(q;q)_inf, and the Euler-Maclaurin half-term (factor 1/(1-e^-u)). The
alternating sign is the Poisson mode e^{i pi m}; the saddle equation
g'(u) = -i pi, i.e. u + 2 log(1 - e^-u) = i pi, EXPONENTIATES ALGEBRAICALLY:
(1-w)^2 = -w for w = e^-u, so w^2 - w + 1 = 0 and

    w = e^{+-i pi/3}   (primitive 6th roots of unity),  u* = i pi/3.

All saddle data are closed-form:  g''(u*) = i sqrt(3);
G := g(u*) + i pi u* = 2i Cl2(pi/3) is PURE IMAGINARY, where Cl2 is the
Clausen function. Hence |K| neither grows nor decays exponentially, and

    K(e^-eps) = 2 * 3^{1/4} sqrt(eps/2pi) cos( V/eps - pi/12 ) (1 + O(eps)),
    J(e^-eps) = 2 * 3^{-1/4} sqrt(eps/2pi) cos( V/eps - pi/4 ) (1 + O(eps)),

    V = 2 Cl2(pi/3) = 2.02988321281930725004240510854904057188...
      = the hyperbolic volume of the figure-eight knot complement
        (= 2 x Gieseking's constant; OEIS A091518, A143298 -- both verified
        digit-for-digit against b-files, 51 digits).

Validation against adaptive-precision Decimal evaluations (precision
~0.86/eps + 60 digits, needed since the sum cancels from e^{1.97/eps} down
to O(sqrt(eps))):
  * zero law: o_k := V/(pi eps_k) - k -> 7/12 (king; Richardson-extrapolated
    o_inf = 0.5833346 vs 7/12 = 0.5833333) and -> 3/4 (control; o_inf =
    0.75000004), zeros bisected to 30+ digits for k = 5..60 and spot-checked
    at k = 94; drift o_k - o_inf = O(eps) with coefficient ~ -0.0026 (king).
  * amplitude law: at predicted extrema, K/(3^{1/4} sqrt(eps/2pi)) -> 2 with
    (ratio-2)/eps -> -1/3 exactly (king); control converges at rate O(eps^2).
    (The overall factor 2 = both conjugate saddles per mode; fixed
    empirically, the lone piece of the prefactor not yet derived.)

Consequences:
  * K and J have zeros accumulating at q = 1- with eps_k ~ V/(pi k),
    i.e. 1 - q_k ~ V/(pi k): the s05 "infinitely many singularities"
    program now has an explicit, quantitative mechanism with closed-form
    constants shared by king and control (universality of the class;
    only amplitude 3^{+-1/4} and phase offset differ).
  * The appearance of the figure-eight knot volume comes from the saddle at
    a 6th root of unity -- the same Li2(e^{i pi/3}) evaluation that gives
    V(4_1) = 2 Cl2(pi/3) in hyperbolic geometry, and strongly suggests these
    Temperley denominators are quantum-modular-type objects (Kashaev-style
    asymptotics). Left open for a successor.

## 3. Corrected census of K's real zeros (receipt: out_s06_saddle.txt, end)

Mapping s05's 37 banked zeros through the law (k_est = V/(pi eps) - 7/12):
banked #3..#25 are true indices 2..24 (consecutive; lattice residuals
< 0.001). Banked #26..#32 are genuine but non-consecutive: true indices
27, 28, 29, 34, 37, 40, 43 -- s05's scan missed 12 zeros in between.
Banked #33..#37 are OFF-LATTICE (residuals 0.06..0.44): artifacts of s05's
fixed 110-digit precision, which falls below the ~0.86/eps digits that the
catastrophic cancellation demands for q > 0.986. Freshly located true zeros
at k = 46, 57, 63, 78, 94 (q up to 0.99319...) sit on the law to 5 decimals.
s05's claim ">= 37 real zeros in (0, 0.995)" stands (the law predicts ~128
there, and >= 40 distinct genuine zeros are now explicitly located); only
the last five banked LOCATIONS are corrected.

## OEIS (queries logged in reports/session-06.md)

Search API is Cloudflare-blocked (both attempted queries); b-file fetches
work. A143298 (Gieseking) and A091518 (fig-8 volume) confirmed against the
computed constants to 51 digits. q_c, mu, and the amplitude constants were
OEIS-checked by s05 (absent).
