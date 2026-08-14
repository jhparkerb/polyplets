# R1-E progress

ABOUT TO: step 1 — read docs/proofs/grand-form.md for what a wired P_k closed form consumes
DONE: step 1 -> P_k(n) = [y^k]exp(Σ(a_j+b_j n)y^j); two constants per level; production levels k≤18 pinned from TWO real-swept cells per level (H≤20), NOT from ab-initio weights; ab-initio = cluster weights of surplus ≤ j
ABOUT TO: step 2 — read orchestrator/sweep.go diagCoeffTable + consumers; and results/ns_a40/PROVENANCE.md band structure
DONE: step 2 (sweep.go half) -> diagCoeffTable j=1..19; j>=11 each pinned by theory (shared symbols from lower levels) + exactly TWO fresh real-swept cells (a_j,b_j); consumers evaluate the polynomial at n, nothing else
DONE: step 4 (read early, severance + depth records) -> depths j=2,3,4 closed ab initio from excess<=j-1 families, NO triangle data, NO wired P_k; verified exact k<=19; family table e=3 K=19 = 146 s C++ (results/severance_w3_families_K19_e3.txt); bivariate G dead but fixed-depth slices individually exact; "rows 34-40 out of reach (need P_19+ pinning data at n>=41)" is the severance-map statement to test
ABOUT TO: step 3 — PROVENANCE.md band structure at n=40, and depth1-closed identity direction (T below onset = P_k extension - defect)
DONE: step 3 -> PROVENANCE: real sweeps H3-21, wired k<=18 for H>=22; Phase A (H1-19 + wired) 6.3h vs B+C (H20,H21 solo) = 84% cpu. depth1-closed: D_1(k) = T(2k,k) - law; below-onset column k IS k+1 integers (coeffs of D(z)), depth j = [z^{k+1-j}]D(z); D_1 exact to k=200 in 42s, needs NO P_k. Pinning argument complete: every (a_k,b_k) for k<=20 is pinnable from H<=19 sweep cells (in-onset for k<=17, depth<=4 below-onset + closed D_j for k=18,19,20). Full weight DP consumed NOWHERE. Counter-sting also found: remaining exponential = the sweep itself = incumbent's base.
ABOUT TO: step 5 — read queue.md head for format, then file R1-E.md verdict + successor rows, close B1
DONE: step 5 -> results/rook1/R1-E.md filed (verdict: bounded-depth slices suffice, full weight DP consumed nowhere; no parity rescue — remaining exponential is the sweep's b); queue rows E0 (closes B1), E1, E2, E3 appended
ABOUT TO: run ./scripts/check_receipts.sh
DONE: check_receipts.sh -> exit 0 (self-test OK, 22 files, gate green). R1-E filed complete; B1 closed; reporting to lead and stopping.
