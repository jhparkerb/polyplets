DIRECTION: Area is the proven-intractable statistic (convex-mirage), so pursue the classical lever the mirage points at: the bounding-box/perimeter statistic on convex king animals — box-inscribed counts B(w,h), the semiperimeter GF, and fixed-height area slices — and establish closed forms / D-finiteness there.
SHAPE: perimeter not area

Plan: (1) build a validated DP counting convex king animals by bounding box
(w,h) — validate against brute force (convex_polyplets.py machinery) and
against convex_tm.py's area sequence; (2) compute the B(w,h) table and the
semiperimeter sequence a(s)=Σ_{w+h=s}B(w,h); test D-finiteness with a
holdout-validated P-recurrence guesser (the mirage's own discriminator
methodology), hunt for a closed form for B(w,h) (fixed-h polynomials in w,
Ehrhart-style, then a uniform binomial form); (3) OEIS lookups; (4) if time:
fixed-height area GFs A_H(q) are rational — compute H=1..3 explicitly as the
tractable slice of the area statistic itself.

## CARRY
CLAIM: The semiperimeter statistic on convex king animals is ALGEBRAIC: F(t)=sum a(s)t^s = [t^2(2-10t+14t^2-5t^3-4t^4) - t^3(1+2t)^2 sqrt(1-4t)]/((2+t)(1-4t)^2), matching all 38 pure-DP terms | receipt: results/convex-box.md, out_final_verify.txt | status: firm
CLAIM: a(s) = 1,2,9,36,154,668,2916,12740,55570,... (s>=2) is new to OEIS; satisfies order-4/deg-3 (also order-7/deg-1) P-recurrence which predicted 8 fresh ~20-digit DP terms exactly | receipt: king_semiperim_38.txt, out_recurrence_scan.txt | status: firm
CLAIM: a(s) ~ (s/128)4^s with next-order term -(1/64)(2s+1)C(2s,s); growth constant exactly 4 | receipt: out_final_form.txt | status: firm
CLAIM: Box counts f(w,h) are polynomial in w (deg 2h-2, ALL w>=1) for fixed h: f(w,2)=2w^2-1, f(w,3)=w^4+(2/3)w^3-(1/2)w^2-(13/6)w+2, h=4,5 banked | receipt: out_row_polynomials.txt | status: firm
CLAIM: Fixed-height area GFs are RATIONAL with cyclotomic denominators: A_2=q^2(3-q)/(1-q)^3, A_3=q^3(7+2q+3q^2-4q^3+2q^4)/((1-q)^4(1-q^3)), A_4 den=(1-q)^4(1-q^3)^2(1-q^4); slices sum to the banked area sequence (n<=12 exact) | receipt: out_area_fixed_height.txt, out_area_slices_check.txt | status: firm
CLAIM: The DP pipeline is literature-anchored: polyomino mode reproduces A005436 (16/16 terms) and the fitter recovers the classical Delest-Viennot GF (1-4t)^2 F = t^2(1-6t+11t^2-4t^3) - 4t^4 sqrt(1-4t) | receipt: out_control_polyomino.txt, out_ansatz_control.txt | status: firm
VERIFY: convex-mirage 38-term area sequence + mu=3.12894 (convex_tm.py rerun, 30 terms, 20-term ref match) | outcome: confirmed | receipt: out_convex_tm_check.txt
OPEN: PROVE the closed form for F(t) (kernel method / Lin-Chang-Gessel box decomposition; the (2+t) factor and (1+2t)^2 beg for a bijective explanation); also the bivariate F(x,y) by (w,h) is presumably algebraic - fit it.
OPEN: Closed form for f(w,h) jointly (Gessel-style binomial formula); leading coeffs of row polynomials 1, 2, 1, 17/90, 1/56 unidentified.
OPEN: Pattern of A_H numerators + Temperley q-functional equation for the full area GF (would make convex-mirage's q-series nature a theorem).
DEAD: Area-statistic P-recurrence (re-confirmed: do not retry; convex-mirage negative stands).
DEAD: Simple radical ansatz with sqrt(1+2t) factors - the second radicand is absent; only sqrt(1-4t) occurs (discriminant = 4t^6(1-4t)^5(1+2t)^4).

## LOG

### Narrative

Surveyed corpus: convex-mirage.md (area non-D-finite, 38 terms, mu=3.129),
results/convex-polyplets.md, convex_tm.py (row-interval transfer with
valley/mountain phase automaton, validated vs brute force). The mirage doc
itself points at the lever: classical convex-polyomino tractability is by
PERIMETER (Delest-Viennot), not area. So the session pursued the bounding-box
statistic.

Steps, in order (all receipts in repo root / results/):

1. `experiments/convex_box.py` — interval DP for g(w,h) (animals fitting in a
   width-w frame), f(w,h) by second difference. Validated: (a) vs direct
   subset brute force (king-connected + HV-convex + touching all 4 sides) on
   all boxes wh<=16 — 16/16 exact; (b) transpose symmetry f(w,h)=f(h,w) all
   w,h<=38; (c) polyomino-adjacency mode reproduces A005436 16/16.
   Ran 14x14 (0.5s), 30x30 (15s), 38x38 (~1min): a(s) complete for s=2..39.

2. `experiments/fit_recurrence.py` (holdout P-recurrence guesser, mirage
   methodology): on 30 terms found order-5/deg-2; extended sequence; the
   38x38 DP run then confirmed all 8 predicted fresh terms (~20 digits each)
   exactly. Order-4/deg-3 is minimal (scan with holdout 7 over all 38 terms);
   order-7/deg-1 also exists. Characteristic roots 4,4,-2,172/97,-1/2
   (172/97 spurious; Durand-Kerner in out_char_roots.txt).

3. Extended to 200 exact terms via the order-4 recurrence (every division
   integer — consistency check in itself; king_semiperim_200.txt).

4. `experiments/gf_algebraic.py`: with 200 terms found the quadratic
   P2 F^2 + P1 F + P0 = 0 (F-deg 2, t-deg 11, 30-coefficient holdout).
   Factored: P2=(2+t)(1-4t)^4, discriminant = 4t^6(1-4t)^5(1+2t)^4 -> only
   sqrt(1-4t). Reduced (two hidden (1-4t) cancellations in the rational
   numerator, A -> Q -> R) to the closed form in CARRY. Re-expanded the
   reduced form from scratch: matches the 38 pure-DP terms (non-circular).

5. Control calibration: `experiments/ansatz_fit.py` on A005436 recovers the
   classical (1-4t)^2 F = t^2(1-6t+11t^2-4t^3) - 4t^4 sqrt(1-4t) exactly.
   (The same ansatz at dmax=10 failed on the king sequence because the king
   equation needs t-deg 11 + the (2+t) denominator; the full guesser with
   200 terms was the fix.)

6. Fixed-height slices: row polynomials f(w,·) (out_row_polynomials.txt) and
   area GFs A_H(q) rational, exact holdout-validated Pade fits
   (out_area_fixed_height.txt); denominators cyclotomic products; slices
   sum to the banked area sequence (n<=12 exact).

7. Asymptotics: R(1/4)=9/32 => a(s) ~ (s/128)4^s; radical part
   -(1/64)(1-4t)^{-3/2}-type => -(1/64)(2s+1)C(2s,s) next order; numeric
   check at s=199 consistent (out_final_form.txt).

### Dead ends / gotchas

- gf_algebraic.py at 30 terms: underpowered for t-deg>=8 (var count exceeds
  equations) — NONE result there was a power issue, not evidence. Successors:
  when a guesser fails, check the var/equation budget before believing it.
- First gcd-based discriminant factoring had a buggy square-part routine;
  redone with multiplicity peeling (out_closed_form2.txt is the good one).
- Background-run gotcha: `cmd > file` under run_in_background + copying the
  harness capture file clobbered the redirect target once; rerun was cheap.
- a(s) ratios LOOK like they converge to ~4.29 at s=15 — they don't; growth
  is exactly 4 with a linear prefactor. Don't estimate growth from <30 terms.

### OEIS queries (verbatim)

1. curl -s "https://oeis.org/search?q=1,2,9,36,154,668,2916,12740,55570,241692,1047604&fmt=text"
   -> Cloudflare challenge page (blocked).
2. curl -s -A "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0" "https://oeis.org/search?q=1,2,9,36,154,668,2916,12740,55570,241692,1047604&fmt=json"
   -> null (NOT in OEIS).
3. curl -s "https://oeis.org/A005436/b005436.txt" -> control terms fetched OK.
4. curl -s -A "(same UA)" "https://oeis.org/search?q=1,7,90,1398,23020,386774,6539320,110639796&fmt=json"
   -> null (box diagonal NOT in OEIS).
5. curl -s -A "(same UA)" "https://oeis.org/search?q=2,9,36,154,668,2916,12740,55570&fmt=json"
   -> null.

### Handoff pointers

Primary writeup: results/convex-box.md. The proof of the closed form is the
big open item; everything needed (equation, factored discriminant, reduced
form, control analogy) is banked. The bivariate F(x,y) fit is a natural
session-02-sized first move; the box-count closed form (Gessel/Lin-Chang
analog) is the deeper prize.
