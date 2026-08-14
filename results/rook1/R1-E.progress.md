# R1-E progress

ABOUT TO: step 1 — read docs/proofs/grand-form.md for what a wired P_k closed form consumes
DONE: step 1 -> P_k(n) = [y^k]exp(Σ(a_j+b_j n)y^j); two constants per level; production levels k≤18 pinned from TWO real-swept cells per level (H≤20), NOT from ab-initio weights; ab-initio = cluster weights of surplus ≤ j
ABOUT TO: step 2 — read orchestrator/sweep.go diagCoeffTable + consumers; and results/ns_a40/PROVENANCE.md band structure
DONE: step 2 (sweep.go half) -> diagCoeffTable j=1..19; j>=11 each pinned by theory (shared symbols from lower levels) + exactly TWO fresh real-swept cells (a_j,b_j); consumers evaluate the polynomial at n, nothing else
DONE: step 4 (read early, severance + depth records) -> depths j=2,3,4 closed ab initio from excess<=j-1 families, NO triangle data, NO wired P_k; verified exact k<=19; family table e=3 K=19 = 146 s C++ (results/severance_w3_families_K19_e3.txt); bivariate G dead but fixed-depth slices individually exact; "rows 34-40 out of reach (need P_19+ pinning data at n>=41)" is the severance-map statement to test
ABOUT TO: step 3 — PROVENANCE.md band structure at n=40, and depth1-closed identity direction (T below onset = P_k extension - defect)
