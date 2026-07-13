# K1: the all-pairs weight constant via the gap walk (kernel program)

2026-07-14. `experiments/allpairs_kernel.py`. Closes the "what generalizes
(2s+1)^2" question in its correct form.

## The exact reformulation (part 1, validated)

All-pairs cluster weights W(2^l) = weighted paths of a two-class gap walk:
state (g, c), g = gap between the pair's cells, c = J (one component) or
P (two pending). Transitions enumerated exactly; reproduces count_stack
for l <= 8. Structure: P-bulk = (1,2,3,2,1) walk on steps -2..+2 (mass 9);
J-class adds constant-weight (8) long jumps to (g', P) -- one new cell
lands near the block, the far cell goes pending -- and weight-8 resets to
(1, J). Ends: J pays g+3 (g<=2) / 6 (g>=3); P finishable only at g <= 2.

## The constant (part 2)

Dominant eigenvalue of the exact truncated operator (truncation error ~
kappa^gmax, verified 1e-10 -> 1e-37 across gmax = 30..140):

  rho = 14.4087139862703658381480400778825365989...   (37 digits)

**Spectral structure verified:** the eigenvector is a localized kappa-mode,
f(g) ~ kappa^g with kappa = 0.4210895797931588..., satisfying the bulk
kernel relation rho = kappa^2 + 2 kappa + 3 + 2/kappa + 1/kappa^2 (residual
4e-17, at the kappa-extraction precision); the P-component has the predicted
constant plateau 8 S_J/(rho - 9). Since rho = 14.41 > 9 = bulk mass, the
growth is a boundary-localized eigenvalue, not essential spectrum -- WHY the
family is not C-finite yet has a clean constant.

**Algebraicity status:** the finite boundary system + the quartic tail
relation imply rho IS algebraic, but PSLQ refutes every candidate of degree
<= 10 with coefficients <= 1e10 (two seemingly-good fits at lower precision
were exposed as noise by pushing truncation: a degree-4 candidate's residual
jumped to 3e-12). The exact minimal polynomial would come from eliminating
the ~15-unknown boundary system against the quartic -- documented route,
not executed; expected degree ~20+, large coefficients.

## Verdict

Single-row weights: (2s+1)^2 exactly (proved). Multi-row: no closed form,
no C-finite recurrence; the correct invariant is the walk's localized
eigenvalue rho = 14.4087139862703658... with kappa = 0.42109 decay. Open
(low value): the exact elimination for rho's minimal polynomial.
