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

## The mechanism (part 2)

> **Scope narrowed 2026-07-31.** This section used to lead with `rho` quoted
> to 37 digits. Those digits certified nothing anyone can use: `rho` is the
> dominant eigenvalue of an operator this project defined, it appears in no
> other context, and it has no known minimal polynomial — so the precision
> only sharpened a question we cannot answer. The **mechanism** below is the
> result; the constant is its residue, and two significant figures is the
> honest size for it. The full expansion remains reproducible from
> `experiments/allpairs_kernel.py` at any `gmax` if a use for it ever appears.

Dominant eigenvalue of the exact truncated operator (truncation error ~
kappa^gmax, stable across gmax = 30..140):

  rho ~= 14.41,  with decay rate kappa ~= 0.421

**Spectral structure verified — this is the finding.** The eigenvector is a
localized kappa-mode, f(g) ~ kappa^g, satisfying the bulk kernel relation
rho = kappa^2 + 2 kappa + 3 + 2/kappa + 1/kappa^2; the P-component has the
predicted constant plateau 8 S_J/(rho - 9). Since rho > 9 = bulk mass, the
growth is a **boundary-localized eigenvalue, not essential spectrum** — which
is WHY the all-pairs family has a clean growth constant and yet no C-finite
recurrence. That statement is basis-independent and consequential; the
decimal expansion is neither.

**Algebraicity status (closed door).** The finite boundary system + the
quartic tail relation imply rho IS algebraic, but PSLQ refutes every
candidate of degree <= 10 with coefficients <= 1e10 — and two seemingly-good
low-precision fits were exposed as truncation noise, which is the cautionary
half of this note. The exact minimal polynomial would come from eliminating
the ~15-unknown boundary system against the quartic: documented route, not
executed, expected degree ~20+ with large coefficients. **Not worth doing.**

## Verdict

Single-row weights: (2s+1)^2 exactly (proved). Multi-row: no closed form and
no C-finite recurrence, because the growth constant is a boundary-localized
eigenvalue of the gap walk rather than bulk spectrum. That is the whole
claim.
