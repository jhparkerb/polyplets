DIRECTION: push the singular structure of the area-moment hierarchy on three fronts: (i) registered-prediction extension of the c_r=(r!)^2/2^(r+7) law from moment level 8 to 12 via the s09 slice engine, (ii) bivariate B_2/B_3 extraction to test s10's factorization conjecture B_r = Delta*x^2y^2*(1+x+y)*C_r, (iii) a delta-Laurent local engine at the quadruple collision to exhibit the blow-up recursion (s09 OPEN 1).
SHAPE: singular expansion engineering

Plan: (1) copy s09_slice_moments.py to s11_slice_r12.py with output names changed (never clobber predecessor receipts), run MAXR=12 NU=380 in background — the script's own MATCH/MISMATCH logic tests the prediction below. (2) Extend the validated r<=4 moment DP to a full WBOX x WBOX bivariate table, fit A_r + B_r*sqrt(Delta) = M_r * K^(r+1) Delta^(2r+2) for r=2 (and 3 if affordable) mod two primes, CRT-lift, then EXACT multivariate division tests over Z: Delta | B_r, then B_r/(Delta*x^2y^2*(1+x+y)) polynomial [king] resp. /(Delta*4x^2y^2) [control]. (3) Implement Laurent-series-in-delta coefficients (slice x=1/4, y=y(delta) with Delta=delta^2, so sqrt(Delta)=delta is RATIONAL and the whole recursion lives in one power-series ring) under the s09 FRat chassis; extract local profiles of the three phases at the collision point s*=2 and machine-check the local transfer that must produce c_r/c_{r-1}=r^2/2.

REGISTERED PREDICTIONS (written before any run):
  P1: c_r = (r!)^2/2^(r+7) and cQ_r = 0 for r = 9,10,11,12, king AND control, with the slice denominator law Kx^(r+1)Dx^(2r+2) continuing to hold with nontrivial surplus.
  P2: Delta | B_2 exactly over Z, and B_2 = Delta*x^2y^2*(1+x+y)*C_2 with C_2 a symmetric integer polynomial [king]; B_2^ctrl = Delta*4x^2y^2*E_2 [control]. Same shape at r=3.

## CARRY
(to be filled as results land)

## LOG

Session start. Read all ten CARRY sections. Chose the three-front plan above.
Front 1 receipts will be out_s11_slice_r12.txt / out_s11_slice_PQ_r12.json;
front 2 receipts out_s11_bivar_Br*.txt/.json; front 3 receipts
out_s11_delta_local*.txt.
