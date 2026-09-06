# The growth constant λ of polyplets

A polyplet (king animal) is a finite set of cells of the square lattice,
connected through shared edges or corners, counted up to translation; a(n) is
the number with n cells (OEIS A006770). The growth constant is
λ = lim a(n)^(1/n). It exists by Fekete's lemma applied to
a(m)a(n) ≤ a(m+n), which is proved in Lean 4 (`polyplets/PROOF-STATUS.md`).
This file holds everything the project established about λ and the
asymptotic form of a(n): a proved two-sided bracket 6.543 ≤ λ ≤ 9.3154, both
ends exact rational certificates; the strip growth constants μ_H for
H ≤ 17, certified; a measured estimate λ = 7.110(1) with the exponents
θ = −1.000(1) and ν_eff = 0.676 at n = 40; and the routes to a better upper
bound that were tried and closed, each with the obstruction that closed it.
Grades are stated at each result: proved (a theorem or an exact arithmetic
check), measured (a computation whose output is a number with the script
that produced it), or conjectured.

## Definitions

- T(n,H) is the number of polyplets with n cells whose bounding box has
  height exactly H (the triangle, `results/triangle.txt`); T_{≤H}(n) is the
  sum over heights ≤ H.
- μ_H = lim T_{≤H}(n)^(1/n) is the strip growth constant. The height-≤H
  polyplets are counted by a finite transfer matrix on column signatures, so
  μ_H is the reciprocal of the radius of convergence of a rational generating
  function and is an algebraic number: 1/(smallest positive root of Q_H) for
  the fixed-height generating functions in `results/fixed_height_gfs.txt`.
  The sequence μ_H is strictly increasing and μ_H ≤ λ.
- M(x) is the height-≤H king connectivity transfer operator with entries
  x^(cells placed); ρ(M(x)) is its spectral radius; μ_H = 1/x* where
  ρ(M(x*)) = 1.
- The asymptotic form assumed throughout is a(n) ~ B λ^n n^θ (1 + c n^(−Δ)).
  θ is the leading exponent, Δ (also Δ₁) the confluent correction exponent.
- ν is the extent exponent: the mean bounding-box height of an n-cell
  polyplet grows as n^ν.
- The "connectivity wall" names one obstruction met on every route to a
  tighter upper bound: an encoding that reads only a bounded window admits
  formal objects whose distant parts fail to connect or overlap, and that
  over-count cannot be seen, or paid for, locally.

## The bracket

**Theorem (proved).** 6543/1000 ≤ λ ≤ 20000/2147, that is
6.543 ≤ λ ≤ 9.3154.

The lower end is the certified μ_17 of the strip ladder below (2026-07-31,
gympie, receipts in `results/strip_mu_certificates.log`). The upper end is an
exact rational super-solution of a 5930-component convolution system in the
style of Bui, x = 2147/20000, every inequality checked in exact rational
arithmetic; the derivation, the elementary bound λ ≤ 5⁵/4⁴, the false starts
and the slack audit are in `docs/proofs/polyplet-upper-bound.md`, and the
scheme is formalized in Lean with one named `native_decide` leaf
(`polyplets/PROOF-STATUS.md`). The decimal 9.3154 rounds 9.31532… away from
the truth; the form 9.3153 that stood until 2026-08-07 claimed 3.2e−5 more
than the certificate gives and was corrected across the tree.

The state of rigorous knowledge, with grades:

| bound | value | grade | source |
|---|---|---|---|
| directed king animals | λ ≥ 3+2√2 ≈ 5.828 | closed form | Bacher |
| multi-directed king animals | λ ≥ 6.4752 | numerical | Bacher; extended to 6.475196280297 in `results/subclasses.md` (planned) |
| Fekete floor from a(40) | λ ≥ a(40)^(1/40) = 6.2208 | proved | the enumerated term |
| strip ladder, H = 17 | λ ≥ 6.543 | exact rational certificate | this file |
| estimate | λ ≈ 7.110(1) | measured | this file |
| convolution certificate | λ ≤ 9.3154 | exact rational certificate | `docs/proofs/polyplet-upper-bound.md` |
| elementary counting | λ ≤ 5⁵/4⁴ ≈ 12.207 | proved | `docs/proofs/polyplet-upper-bound.md` |

For scale, the rigorous bracket on the growth rate of 1324-avoiding
permutations after decades of work is 10.271 ≤ gr ≤ 13.5 around a numerical
11.60 (Bevan, Brignall, Elvey Price and Pantone, EJC 88 (2020) 103115), a
ratio of 1.31. This bracket's ratio is 9.3154/6.543 = 1.42.

## The strip growth constants μ_H

Values from power iteration on M(x), double precision, printed to seven
decimals (measured; H ≤ 14 by the hash-map engines, H = 15..17 by the
search phase of `cpp/strip_mu_cert.cpp` on the frozen tables, all on
gympie, 2026-07-10 and 2026-07-31):

| H | μ_H | H | μ_H | H | μ_H | H | μ_H |
|---|---|---|---|---|---|---|---|
| 2 | 2.4142136 | 6 | 5.1153245 | 10 | 5.9916958 | 14 | 6.3800344 |
| 3 | 3.4437184 | 7 | 5.4178476 | 11 | 6.1158416 | 15 | 6.4435408 |
| 4 | 4.1823214 | 8 | 5.6533728 | 12 | 6.2191246 | 16 | 6.4985245 |
| 5 | 4.7178013 | 9 | 5.8404579 | 13 | 6.3060713 | 17 | 6.5464870 |

Checks on these values:

- μ_2 = 1 + √2 exactly, an anchor independent of every program.
- For H ≤ 11 the values agree with the roots of the fixed-height generating
  functions recomputed at 200 digits to 9–10 significant digits, every digit
  the certificate receipts record (`experiments/mu_H_precision_audit.py`).
  The root computation in `experiments/mu_H_from_atoms.py` loses about 42
  digits to cancellation at H = 11, so it confirms every root at doubled
  working precision and reports the digits confirmed.
- The ratio of consecutive increments climbs from 0.72 to 0.84 over H ≤ 14, a
  power-law approach rather than a geometric one.
- The count-ratio route T(n,H)/T(n−1,H) is badly under-converged for H above
  about 6; at n = 36, H = 18 that ratio is 7.63, above λ
  (`experiments/strip_growth_extrapolation.py`). Only the eigenvalue or
  generating-function route gives μ_H.

**The boundary states are non-crossing (measured, 2026-08-01).**
`experiments/strip_state_count_model.py` models a boundary state as an
occupancy of the H rows, each maximal vertical run in one component, plus a
partition of the runs. Against the enumerated boundary-state counts:

| H | actual | runs × Catalan | runs × Bell |
|---|---|---|---|
| 9 | 2187 | 2188 | 2243 |
| 12 | 41834 | 41835 | 46905 |
| 16 | 2356778 | 2356779 | 3365627 |

The count equals the non-crossing model minus one (the separately held empty
seed) at every H from 9 to 16. The reason is elementary: a crossing needs
the edges (r,c)–(r+1,c+1) and (r+1,c)–(r,c+1), so all four cells are
occupied, and then (r,c) and (r+1,c) are vertically adjacent and the two
components were one. The Temperley–Lieb structure is therefore available on
the king frontier.

## The certificates

The floating-point μ_H are outputs of a bisection over a power iteration and
cannot be audited after the fact. A **certificate** for the rational
r = num/den at height H is a nonnegative, nonzero integer vector v indexed by
the states of M together with the verified statement that
M(den/num) v ≥ v holds componentwise in exact integer arithmetic. Three facts
make a certificate a bound on λ.

1. **Collatz–Wielandt, lower half.** If A is a nonnegative square matrix and
   v ≥ 0, v ≠ 0, satisfy Av ≥ v componentwise, then ρ(A) ≥ 1. A is monotone
   on the nonnegative orthant, so A^k v ≥ v for all k; any i with v_i > 0
   gives ‖A^k‖_∞ ≥ v_i/‖v‖_∞, hence ρ(A) = lim ‖A^k‖^(1/k) ≥ 1. Neither
   positivity of v nor irreducibility of A is needed (Horn and Johnson,
   Matrix Analysis, ch. 8; Berman and Plemmons, ch. 2). The upper half of the
   two-sided formula is never used.
2. **Monotonicity in x.** The entries of M(x) are nonnegative and increasing
   in x, and ρ is monotone in the entries, so ρ(M(x)) ≥ 1 implies x ≥ x* and
   μ_H = 1/x* ≥ 1/x.
3. **Containment.** T_{≤H}(n) ≤ a(n) for every n, so μ_H ≤ λ.

An exactly checked M(den/num) v ≥ v therefore certifies λ ≥ μ_H ≥ num/den.

**Theorem (proved).** The following values are certified. In particular
μ_17 ≥ 6.543 and λ ≥ 6.543.

| H | certified μ_H ≥ | num / den | states | μ_H (float) | digits / vbits | range bits | tries | wall (s) |
|---|---|---|---|---|---|---|---|---|
| 2 | 2.4142135 | 24142135 / 10⁷ | 3 | 2.414213562 | 7 / 96 | 1.3 | 1 | 0.0 |
| 3 | 3.4437183 | 34437183 / 10⁷ | 8 | 3.443718375 | 7 / 96 | 3.6 | 1 | 0.0 |
| 4 | 4.1823214 | 41823214 / 10⁷ | 20 | 4.182321413 | 7 / 96 | 5.9 | 1 | 0.0 |
| 5 | 4.7178012 | 47178012 / 10⁷ | 50 | 4.717801291 | 7 / 96 | 12.2 | 1 | 0.0 |
| 6 | 5.1153244 | 51153244 / 10⁷ | 126 | 5.115324460 | 7 / 96 | 15.8 | 1 | 0.0 |
| 7 | 5.4178476 | 54178476 / 10⁷ | 322 | 5.417847610 | 7 / 96 | 20.6 | 1 | 0.0 |
| 8 | 5.6533727 | 56533727 / 10⁷ | 834 | 5.653372762 | 7 / 96 | 24.1 | 1 | 0.0 |
| 9 | 5.8404579 | 58404579 / 10⁷ | 2187 | 5.840457941 | 7 / 96 | 39.7 | 1 | 0.1 |
| 10 | 5.9916957 | 59916957 / 10⁷ | 5797 | 5.991695792 | 7 / 96 | 44.8 | 1 | 0.2 |
| 11 | 6.1158416 | 61158416 / 10⁷ | 15510 | 6.115841628 | 7 / 96 | 52.5 | 1 | 0.5 |
| 12 | 6.2191246 | 62191246 / 10⁷ | 41834 | 6.219124621 | 7 / 96 | 57.5 | 1 | 1.7 |
| 13 | 6.3060712 | 63060712 / 10⁷ | 113633 | 6.306071285 | 7 / 96 | 80.6 | 1 | 5.4 |
| 14 | 6.3800149 | 63800149 / 10⁷ | 310571 | 6.380034445 | 7 / 96 | 87.4 | 18 | 18.3 |
| 15 | 6.443532 | 6443532 / 10⁶ | 853466 | 6.443540832 | 6 / 100 | 97.8 | 8 | 57.7 |
| 16 | 6.4984 | 64984 / 10⁴ | 2356778 | 6.498524533 | 4 / 106 | 104.3 | 3 | 225.0 |
| 17 | **6.543** | 6543 / 10³ | 6536381 | 6.546486999 | 3 / 110 | 134.8 | 6 | 772.7 |

Every row is a receipt in `results/strip_mu_certificates.log` (git revision
900b4ff, host gympie, 2026-07-31), one line each with vector checksum,
precision fields and wall time; "states" is the in-edge-reachable boundary
count, "tries" the number of candidate numerators before one passed, and the
float column the value the search phase proposed, used nowhere in the proof.
H = 12, 13 and 14 were certified twice, first by the hash-map binary
(revision 4ab40fa, walls 393.5 s, 1469.8 s and 5832.8 s) and again by the
frozen-table binary at the walls shown; same numerator, same state count,
same minimum ratio to all nine printed digits. H = 2..11 were likewise first
certified by the hash-map binary (revision ce506bc; H = 11 took 120.9 s).
H = 16 was first certified at six digits as 6.468300 in 32 tries; the
four-digit run in the table is the stronger bound.

The certified value is a floor. At H = 2 it reads 2.4142135 where μ_2 is
2.4142136 to seven places. From H = 14 upward it falls short of the float
value for the precision reason below; at H = 17 it concedes about 0.0035.
Clamping can only lower a certified value, never falsify one.

**The tool** (`cpp/strip_mu_cert.cpp`, `make build/strip_mu_cert`) has two
phases. Phase 1 is a warm-started bisection on x for ρ(M(x)) = 1 in double
precision using the cell-at-a-time column pass of `cpp/strip_stage_ops.h`;
it proposes a candidate x and a candidate vector and enters the proof
nowhere. Phase 2 scales the vector to integers with the largest entry at
2^vbits, sets num = floor(μ_float · den), and checks M(den/num) v ≥ v in
`unsigned __int128`. If a state fails, the tool searches for the largest
numerator that passes; the check is monotone in the numerator, so it
brackets by doubling and bisects in about 2·log₂(gap) passes, re-verifying
the winner last. One fixed vector serves the whole search. A failure is
never absorbed into a tolerance. Three properties make phase 2 sound:

- Every rounding is downward. Each of the H stages is a nonnegative linear
  map, and the "cell placed" branch contributes floor(val · den/num) ≤ val · x,
  so the computed vector is componentwise at most the true M(x) v. The "no
  cell" branch has weight 1 and is copied exactly.
- Restriction is safe. Only the finite support S of the converged eigenvector
  is held; mass leaving S is dropped. That certifies the principal submatrix
  M_S, and ρ(M_S) ≤ ρ(M). Entries that quantize to zero are harmless because
  Collatz–Wielandt needs only v ≥ 0, v ≠ 0.
- Overflow is loud. Every multiply and add is guarded against 2^126; a trip
  is a FAIL naming the state. The vector width is auto-sized to
  126 − ceil(digits · log₂ 10) − 6 and a larger explicit value is refused.
  Measured headroom at H ≤ 11: the largest value held is 96.7 bits against a
  96-bit vector ceiling, so merges add 0.7 bits.

**Self-tests** (`./build/strip_mu_cert --selftest`, `make gate-strip-cert`,
also in `make gates`). The checker must be able to say no, so the gate makes
it:

- A. μ_2 = 1 + √2, so 24142/10000 must pass. It does.
- B. 24143/10000 exceeds μ_2, so it must fail. It does, naming the state and
  printing lhs < rhs in full integers.
- C. One entry of a passing vector multiplied by 2^30 must be rejected. It is.
- D. The all-zero vector satisfies Av ≥ v vacuously and would certify every
  rational; it must be refused. It is.

Out-of-range H or a vector width above the arithmetic's headroom exits 2 with
the valid range printed.

**The precision budget** is the binding constraint at large H, not time and
not convergence. The eigenvector's dynamic range in bits is the "range bits"
column above: 24.1 at H = 8, 52.5 at H = 11, 80.6 at H = 13, 87.4 at H = 14,
97.8 at H = 15, 104.3 at H = 16, 134.8 at H = 17, against a vector ceiling of
96 bits at seven decimal digits. Entries whose true scale sits below the
quantization floor are clamped to 1, and no few-bit increase reaches them:
widths 96 and 100 gave identical certified numerators at H = 16, and so did
an added eigenvector polish phase (kept; it is the right stopping rule and
costs little). The lever that works is fewer decimal digits, since a smaller
denominator frees accumulator headroom: digits 6, 4 and 3 buy widths 100,
106 and 110. At H = 15 and 16 that lifts the whole eigenvector above the
floor and the certificate lands within one unit in the last place of the
float. At H = 17 the range of 134.8 bits is above the cap at every digits
setting (digits 1 reaches about 116), so part of the tail is clamped; the
0.0035 conceded would need at least 192-bit accumulators. An earlier claim
that the width exceeded the range at every height is refuted by the H = 17
receipt; it holds through H = 16.

Two measurements of the flooring loss:

- H = 10 with the width forced to 55 bits (smallest entry about 2^10 instead
  of 2^51): the first candidate fails at four states with minimum ratio
  0.99994, one unit in the last place, so the loss is O(1) and not O(H). The
  search then certifies 59916466/10⁷ in 20 passes, at a wall
  indistinguishable from the full-precision run.
- H = 14 at digits 6 certifies 6.380033 in 3 tries (width 100), and at digits
  5 certifies 6.38003 on the first candidate (width 103); both are stronger
  than the seven-digit 6.3800149 (adoption cross-check logged to scratch;
  the published receipt is the seven-digit one). Whichever digits setting is
  used, one setting per run keeps receipts comparable.

**Scope.** What is certified is μ_H ≥ num/den given that M(x) is the strip
transfer operator. The operator is trusted, not certified: it is the
production kink transition of `core/kink.h`, exercised by
`make ns-gate-kink` and `ns-gate-kink-column`, and the μ_H it produces agree
with the fixed-height generating-function roots for H ≤ 11 to every digit
recorded. The certificates do not rest on that agreement. The vector
checksums (SHA-256 over states sorted by raw signature bytes, each followed
by its 16-byte little-endian value) differ between the hash-map and
frozen-table binaries for H ≥ 3 because the float phase sums in index order
rather than hash order, so the last ulp of a few quantized entries differs;
at H = 3 the two binaries give identical checksums at widths 20 through 50
and diverge only at 96. A re-verification must use the vector from the same
run.

**Cost and ceiling (measured through H = 17, projected beyond).** Wall grows
about 3.5× per height step (225 s at H = 16, 773 s at H = 17) and the
build-phase peak RSS reached 11.8 GB at H = 17. Two projections for H = 18
from different bases agree within a factor of 1.5: table-throughput
arithmetic in `experiments/strip_fss.py` gives build RSS about 43 GB, float
solve about 29 min, certificate about 32 min; the measured end-to-end wall
growth gives about 45 min and 35 GB or more. Extrapolating the tables at the
measured 2.95× per height:

| H | Σ_r |S_r| | table | build RSS | float matvec | exact pass |
|---|---|---|---|---|---|
| 18 | 6.2e8 | 4.9 GB | ~43 GB | 0.6 s | 5 s |
| 19 | 1.8e9 | 14.5 GB | ~127 GB | 1.7 s | 14 s |
| 20 | 5.4e9 | 42.7 GB | ~374 GB | 5.1 s | 42 s |

Each height step buys about +0.05 toward λ ≈ 7.11 (μ_16 to μ_17 was
+0.048), so no reachable H brings the ladder near λ. H = 18 would give
μ_18 ≈ 6.59. It has not been run; it is a compute decision for jasonp, not a
laptop job.

## The engines

Four programs compute μ_H; the last is the one in use.

- `cpp/strip_mu.cpp` (`build/strip_mu`): power iteration on the all-column
  transfer matrix, CSR edges, warm-started bisection. Validated to H = 13
  (H = 11 10 s, H = 12 67 s, H = 13 465 s). Edge memory grows as
  states × 2^H, so it stops at H = 13 or 14.
- `cpp/strip_mu8.cpp`: whole-column transitions through the viable-mask
  enumerator of the counting engine. Same μ_H, same 2^H edge wall.
- `cpp/strip_mu_kink.cpp` (`build/strip_mu_kink`): one application of M(x)
  is one pass over a column, cell by cell, through the kink transition of
  `core/kink.h`, with intermediate states merged in a hash map. O(H · states),
  no 2^H, no edge storage. Reproduces μ_H to every printed digit through
  H = 11. Hash-map bound, about 3.4× per height; H = 14 took 4851 s
  (`results/strip_mu_H14.log`). Kept in the tree as the cross-check.
- `cpp/strip_mu_fast.cpp` with `cpp/strip_stage_ops.h`
  (`build/strip_mu_fast`, `make gate-strip-fast`): the per-stage state graph
  is enumerated once by layered breadth-first search and frozen into two
  int32 successor arrays per stage (the "no cell" and "cell placed"
  successors, or −1 where the transition suppresses one) plus a finalize
  array from the last stage back to boundary states. One application of M(x)
  is then H flat scatter passes and one finalize pass. `applyOps` is
  templated on the value type and a weight policy, so the float power
  iteration and the certificate's exact check drive the same frozen operator
  over the same state set; an overflow makes it return false, which the
  caller treats as a failed certificate. The enumerator's state store is a
  packed open-addressing interner at about 60 bytes per state, against about
  165 for an `unordered_map` (measured at H = 14: 530 MB against 1.36 GB).

Where the hash-map engine's time went (measured with `sample` and a direct
instrumented A/B, gympie):

| H | emits per state | full pass | transition only | map share | ns per emit |
|---|---|---|---|---|---|
| 10 | 1.96 | 0.356 s | 0.222 s | 37.7% | 83.9 |
| 11 | 1.96 | 0.568 s | 0.359 s | 36.8% | 90.5 |

The map is 37% and the other 63% is union-find, canonicalization and bucket
walks that recompute a fixed graph on every pass. Per-emit cost is flat in H,
so the 3.4× per height was state growth.

Old against new, same box, single core, μ_H and state counts identical to
every printed digit:

| H | states | μ_H | `strip_mu_kink` | `strip_mu_fast` | speedup |
|---|---|---|---|---|---|
| 9 | 2187 | 5.8404579 | 8.7 s | 0.05 s | 174× |
| 10 | 5797 | 5.9916958 | 29.8 s | 0.16 s | 186× |
| 11 | 15510 | 6.1158416 | 107.5 s | 0.51 s | 211× |
| 12 | 41834 | 6.2191246 | not run | 1.7 s | |

On the certificate path (`strip_mu_fast --verify` runs the identical
arithmetic): H = 11 120.9 s to 0.5 s, H = 12 393.5 s to 1.7 s, H = 13
1469.8 s to 5.6 s. Every certificate H = 2..12 re-verifies, passing at the
certified numerator and failing at numerator + 1, with the range and
accumulator bits reproduced exactly and the minimum ratio to 8–9 digits.

Cost model, measured with `--bench` at a fixed x (no cache cliff: the
per-stage-state cost moves from 0.89 to 0.95 ns while the tables grow from
7.5 MB to 564 MB):

| H | states | Σ_r \|S_r\| | table | build | build RSS | float ns/state | exact ns/state | float matvec | exact pass |
|---|---|---|---|---|---|---|---|---|---|
| 9 | 2187 | 36,575 | 0.3 MB | 0.0 s | | 0.80 | 7.46 | | |
| 10 | 5797 | 108,182 | 0.9 MB | 0.0 s | | 0.87 | 7.29 | | |
| 11 | 15510 | 319,492 | 2.6 MB | 0.1 s | 17 MB | 0.86 | 7.24 | 0.0003 s | 0.002 s |
| 12 | 41834 | 942,747 | 7.5 MB | 0.2 s | 45 MB | 0.89 | 7.46 | 0.0008 s | 0.007 s |
| 13 | 113633 | 2,780,660 | 22.2 MB | 0.5 s | | 0.86 | 7.44 | 0.0024 s | 0.021 s |
| 14 | 310571 | 8,200,480 | 65.1 MB | 1.8 s | 530 MB | 0.85 | 7.54 | 0.0070 s | 0.062 s |
| 15 | 853466 | 24,185,132 | 191.6 MB | 6.5 s | 1.36 GB | 0.87 | 7.64 | 0.0210 s | 0.185 s |
| 16 | 2356778 | 71,339,063 | 563.9 MB | 23.2 s | 4.94 GB | 0.95 | 7.86 | 0.0680 s | 0.561 s |

Σ_r |S_r| grows 2.95× per height (2.950, 2.949, 2.949, 2.950, 2.950 across
H = 11..16) and the boundary count 2.71×. Build RSS is a transient; after
enumeration about 0.7 GB stays live at H = 16. Applications per solve are
1311, 1471, 1627, 1755 at H = 9..12, about +140 per height; that count is
the one fitted quantity in the projections. The int32 indices cap a stage at
2^31 states; the largest stage at H = 16 is about 5.2M, so the cap is near
H = 25.

The gate (`make gate-strip-fast`, about 10 s) checks: μ_2 = 1 + √2; boundary
counts 3, 8, 20, 50, 126, 322, 834 at H = 2..8; dropping the heaviest "cell
placed" edge (by mass under the converged eigenvector) at each of the first
three stages moves μ_6; dropping one finalize edge moves μ_6 (5.0687009
against 5.1153245); the exact check passes μ_2 ≥ 2.4142135 and fails
≥ 2.4142136; the all-zero vector is refused. `tests/gate_strip_fast.py` then
compares the two engines at H = 2..8 and brackets every certificate H = 2..8.
Reverting one line of the copied kink transition makes the gate fail: the
state counts become 4, 13, 39, 124, 394, 1283, 4250 and every μ_H moves.

**The implicit-vector idea does not help.** Chan and Rechnitzer (Linear
Algebra Appl. 555 (2018) 139–156) run far larger transfer matrices by never
materializing the vector: each component of ψ and Vψ is generated on demand
from a corner-transfer-matrix ansatz. The memory that saves is not the
memory this ladder is short of. At H = 17 the vector is about 18M entries,
144 MB; what binds is the frozen tables (8 bytes per stage-state over
Σ_r |S_r|) and the build transient (about 8.8× the table). Making the tables
implicit, recomputing transitions per column, is what the hash-map engine
did, and the frozen tables bought 211× for exactly that. Their ansatz also
needs a local face weight, which connectivity is not. A compact trial vector
over connectivity-signature states would be needed instead; the non-crossing
fact above is its precondition, and no such vector has been proposed.

## The upper bound and the routes that are closed

The derivation of λ ≤ 9.3154 and of the elementary λ ≤ 5⁵/4⁴ is in
`docs/proofs/polyplet-upper-bound.md`: the BFS-frame proof of the elementary
bound (repaired 2026-08-14; the earlier decision-string proof missed 2 of 20
animals at n = 3 and 96,065 of 147,941 at n = 8); the two shortcuts that give
λ ≤ 8 and λ ≤ 256/27 and are non-injective, caught because the same argument
proves λ_polyomino ≤ 4; the generic twig decomposition at 12.50, 13.00 and
12.5382; the Bui-style single-cell split whose window lever gives 10.354,
9.402 and 9.306 at windows 1, 2, 3 and whose cell-choice lever has no effect;
the certificate x = 2147/20000; and the slack audit of the window-2 system
against brute-force counts, median 1.144, maximum 1.222, growing by about
+0.022 per term from n = 7 to 8, which is the signature of a non-local
over-count. The routes below were tried afterward and each is closed.

### Twigs at level 1 give exactly 5⁵/4⁴ (proved, 2026-08-14)

`experiments/kingtwigs/l1_schemes.py` with argument 8 on dalby, 12.7 s, all
checks pass.
The king instantiation of the Klarner–Rivest twig formalism: scan order
top-to-bottom then left-to-right, root the scan-minimal cell, process opened
cells FIFO. The frame of a processed cell u with parent d is N(u) minus {d}
minus the shared set N(u) ∩ N(d); shared sets have 4 cells for an orthogonal
parent and 2 for a diagonal one, so frames have 3 or 5 slots, and the
diagonal slot graph is always a 5-path with the chord (1,3). A letter is the
mask of frame slots u newly opens, weight x^opens · y; an n-cell animal maps
injectively to n letters of total weight x^(n−1) y^n. Over all 171,138 king
animals with n ≤ 8: decode∘encode is the identity, codes are pairwise
distinct, the weight identity holds, and the alphabet census is exactly
(1+x)⁵. With h(x) = (1+x)⁵, a(n) ≤ [x^(n−1)] h(x)^n · O(1), so
λ ≤ min_b h(b)/b = 4·(5/4)⁵ = 3125/256 = 12.20703125 at b = 1/4, certified
at rational b in exact arithmetic. Controls: the square lattice in the same
pipeline gives (1+x)³ and 27/4 = 6.75 (Eden), and the extractor fed
Klarner–Rivest's square alphabet 1 + 2x + 2x² reproduces 2 + 2√2 =
4.8284271247; a slot silently dropped from the diagonal frames is caught.

Why Klarner–Rivest's improvement does not transfer: twigs beat Eden on the
square lattice by deferral, a cell u not encoding a neighbor c that a cell b
it just opened will encode later, which is sound there because c is diagonal
from u and so outside N(u). On the king lattice every cell u would defer is
one of u's own neighbors, so c ∈ N(u) ∩ N(b), the shared set that b's frame
excludes. Deferral and the shared-set exclusion are mutually exclusive; the
deferral variant loses the 3-cell animal {(0,0),(0,−1),(−1,−1)}. A perfect
4-slot design would give 256/27 ≈ 9.481, still above 9.3154, so beating the
certificate needed both a slot reduction and the blocked mechanism. The
composition hierarchy would need to recover about 24% from 12.207; Barequet
and Shalah's square hierarchy recovered 6.3% in total at about 2,800
core-hours for its last 0.9%. Not explored: second-order twig geometries
(letters that pre-encode distance-2 cells); no impossibility is proved there.
Standing square numbers: 4.5252 (Barequet–Shalah), 4.5238 (Bui,
arXiv 2511.00461); Klarner–Rivest's published 4.6496 is unreproduced.

### Concatenation (quasi-submultiplicativity) cannot be pushed (2026-08-01)

Barequet, Ben-Shachar and Osegueda (Comput. Geom. 98 (2021) 101790),
Theorem 1(a): if Z(2n) ≤ c₁ n^c₂ Z(n)² for all n then
μ ≤ (c₁ (2n)^c₂ Z(n))^(1/n) for every n. Their lower-bound half is
superseded here (Fekete gives 6.2208, the ladder 6.543). Pricing the upper
half at n = 40 with F = c₁ (2n)^c₂ (`experiments/concatenation_bound_check.py`):

| F at n = 40 | consequence |
|---|---|
| F < 7.54 | refuted: the bound would fall below the certified 6.543 |
| F < 210.5 | refuted against λ ≈ 7.111 (numerical only) |
| F < 1.03e7 | beats 9.3154 |

| deg P | F | bound on λ | |
|---|---|---|---|
| 0 | 1.0 | 6.2212 | refuted |
| 1 | 80.2 | 6.9414 | refuted numerically |
| 2 | 6413 | 7.7451 | useful; the degree of their convex-polyomino P |
| 3 | 5.13e5 | 8.6418 | useful |
| 4 | 4.10e7 | 9.6423 | no gain |

The ratio the lemma must dominate, on the enumerated terms, is linear in
m + n and matches the θ = −1 form to about 2%:

| m+n | argmax | a(m+n)/(a(m)a(n)) | mn/C(m+n) predicted |
|---|---|---|---|
| 10 | (5,5) | 14.87 | 13.16 |
| 20 | (10,10) | 27.99 | 26.31 |
| 30 | (15,15) | 41.00 | 39.47 |
| 40 | (20,20) | 53.95 | 52.63 |

The relation is consistent with every term; it is the proof that is missing.
Their Theorem 8 splits a convex polyomino at lexicographic rank m and
convexity bounds the debris to two components per side. For king animals the
same split shatters a comb (spine at x = 0, teeth every third row):

| k | cells | worst number of components |
|---|---|---|
| 2 | 10 | 3 |
| 8 | 34 | 9 |
| 16 | 66 | 17 |

About n/4 pieces, each needing its own vertical offset, is n^Θ(n) codes, not
a polynomial. The split that keeps both sides connected, a centroid edge of a
spanning tree, cannot prescribe the two sizes to within O(1), which Theorem
1(a) and 1(b) require; approximate splits give only
a(n) ≤ K n² Σ a(m) a(n−m), which any sequence with a(n) ~ C λ^n/n satisfies.
Transfer argument: the same lemma at degree 2 for polyominoes would give
λ_poly ≤ (1.002 · 112² · A(56))^(1/56) = 4.3828 from A(56)^(1/56) = 3.7031,
beating the record 4.5252 by pure arithmetic, so it does not sit unclaimed.
The split does port to convex polyplets (`results/subclasses.md`, planned),
bounding a subclass constant only.

### Band decomposition with bridge credit is unsound (2026-08-07)

The sketch: cut an animal into horizontal bands of height H, encode each
band as its left-to-right component shapes and gap lengths, charge each gap
to the cells bridging it in an adjacent band (at most two gaps per cell, so
gap entropy is about 4^n), and credit the bridging run's shape against the
μ_H^g paid for it. `experiments/band_charge_probe.py` with argument 8 (about
40 s) over all 147,941 fixed king animals at n = 8:

| H | distinct codes | collisions | worst class |
|---|---|---|---|
| 1 | 5597 | 142344 | 2187 |
| 2 | 34798 | 113143 | 45 |
| 3 | 61018 | 86923 | 15 |
| 4 | 87663 | 60278 | 8 |
| 5 | 117456 | 30485 | 6 |

The encoding is not injective from n = 2: the three 2-cell animals all read
as two bands of one single-cell component with no gaps. The charging claim
does hold everywhere measured (max Σ gaps 12, 6, 6, 5, 3 against 2n = 16 at
H = 1..5), and structurally must, since a cell has exactly two adjacent
bands. What the code omits is the horizontal alignment of consecutive bands,
which is exactly the vertical-join multiplicity c(H) that candidate (1) of
the open problem below must bound; the sketch assumes c(H) = 1. On animals
with no gaps its own accounting reads a(n) ≤ μ_H^n, hence λ ≤ μ_17 = 6.543,
which contradicts μ_17 < λ. For H ≥ 3 the components of a band are not even
ordered along x (308, 750 and 332 x-overlapping adjacent pairs at
H = 3, 4, 5 at n = 8). The vertical-join question itself is not refuted.

### Literature routes checked and ruled out (2026-08-01)

- Chan and Rechnitzer's corner-transfer-matrix upper bounds need a transfer
  matrix built from a local face weight and a symmetric V; connectivity is
  not a local face weight, and the signature transfer is directional. Beneath
  that, their κ is a per-site rate for a lattice gas on a cylinder, which
  over-counts per site; λ is a per-cell rate for connected clusters, and a
  cylinder of circumference m loses animals, which is μ_m from below.
- Oh's state-matrix recursions (Discrete Math. 342 (2019); Topology Appl.
  210 (2016); LAA 510 (2016)) fail on the same two counts: per-area
  normalization, and "suitably connected" mosaics meaning local edge
  matching between neighbors, not global connectivity.
- Bevan, Brignall, Elvey Price and Pantone bound gr(Av(1324)) ≤ 27/2 by
  injecting into (bounded label per element) × (a countable simpler class).
  The elementary and convolution bounds here are already of that shape; the
  improvement there came from a structure theorem (Av(1324) inside an
  infinite staircase grid class) with no proposed analogue for polyplets.

## The estimate λ ≈ 7.110 and the exponents

### Differential approximants: λ = 7.110(1), θ = −1.000(1) (measured)

`experiments/series_da.py` on `results/b006770_upload.txt` (2026-07-11 on 36
terms, 2026-07-31 on the final 40). The generating function is fitted to a
first-order ODE Q₀ f + Q₁ f′ = P over a spectrum of polynomial degrees; the
dominant singularity x_c is a root of Q₁, λ = 1/x_c, and with
g = Q₀(x_c)/Q₁′(x_c) the exponent is θ = g − 1. Universality predicts θ = −1,
a logarithmic dominant singularity. Calibration on synthetic
a_n = round(n^θ λ^n) recovers (7.11, −1.0), (7.11, −0.5) and (4.06, −1.0)
exactly, so the method is neither biased toward −1 nor anchored to the
rescaling constant.

| terms | λ | θ | approximants |
|---|---|---|---|
| 36 | 7.1102 | −0.9996 | 42 |
| 40 | 7.1102 | −0.9997 | 42 |

λ is unchanged at N = 28, 32, 36, 40; θ runs −0.9993, −0.9993, −0.9996,
−0.9997. λ_median = 7.1102 for rescaling constants 6.8, 7.0, 7.11, 7.3, and
breaks only at 7.5 (spurious 7.6214). The fourth digit of λ is beyond what
40 terms resolve. The earlier ratio method with a confluent term (Δ₁ = 1/2
assumed) gave λ ≈ 7.111 and θ ≈ −1.02 to −1.03; the approximants absorb the
correction into the ODE and land on −1.000. They do not determine Δ₁; that
needs sub-dominant-singularity analysis.

Independent corroboration: `experiments/convex_growth.py` run on
`results/b006770_upload.txt`, a tool built for series with geometric
corrections (θ = 0) and carrying no θ ansatz, reports the discriminator d_n/d_(n−1) drifting 0.94519 → 0.95062
over n = 35..39 instead of settling, reports 0 trusted digits, and gives an
untrusted μ = 7.1058 (2026-08-05). A tool with no ansatz for θ detects that
the series is not in the θ = 0 regime.

### No stretched exponential (measured, 2026-08-07, gympie)

Conway, Guttmann and Zinn-Justin (Adv. Appl. Math. 96 (2018) 312–333) found
1324-avoiders obey B μ^n μ₁^√n n^g with μ₁ = 0.0400(5); differential
approximants are blind to that factor. `experiments/stretched_exponential_fit.py`
(about 20 s) fits ln a(n) = ln B + n ln λ + √n ln μ₁ + θ ln n on sliding
4-point windows in 60-digit arithmetic, with one Richardson step assuming
f(n) = f_∞ − A/n. Controls: exact-form data recovers the planted μ₁ to 55
digits; planted under a confluent correction 1 + 1/n:

| planted μ₁ | Richardson recovers | θ recovers |
|---|---|---|
| 1.00 | 0.9693 | −1.0093 |
| 0.99 | 0.9596 | −1.0093 |
| 0.95 | 0.9209 | −1.0093 |

The bias is about −0.031 and near-constant; a 1% planted difference
separates by 0.0097. On the real series:

| window | λ | μ₁ | θ |
|---|---|---|---|
| [4,7] | 7.3369778 | 0.67550778 | −0.638431 |
| [12,15] | 7.1452384 | 0.90090285 | −0.836469 |
| [20,23] | 7.1275277 | 0.93817343 | −0.878024 |
| [28,31] | 7.1206429 | 0.95646126 | −0.902173 |
| [36,39] | 7.1171873 | 0.96719872 | −0.918238 |
| [37,40] | 7.1168808 | 0.96822628 | −0.919874 |

Richardson on the top two windows: λ → 7.1053868, μ₁ → 1.0067597,
θ → −0.981231. μ₁ sits above even the zero-correction calibration point and
far above the 0.99 signature (0.96 under either calibration), so a stretched
exponential a hundred times weaker than the 1324 one would have shown and
does not. θ → −0.981 from an ansatz free to blame μ₁ corroborates
θ = −1.000(1). λ → 7.1054 is low by 0.005 and is cruder than the four
methods behind 7.110(1); read as consistent, not competing. Limits: one
Richardson step, one planted correction structure in the controls.

### θ is the same on the king and square lattices (measured, 2026-08-22)

`experiments/theta_universality.py`: one script, one spectrum of 42
first-order inhomogeneous differential approximants, 40 terms on each side.
Inputs `results/b006770_upload.txt` and `results/b001168_external.txt` (OEIS
b-file for A001168, head-checked by a negative control).

| lattice | terms | λ | θ |
|---|---|---|---|
| king (A006770) | 40 | 7.1102 | −0.9997 |
| square (A001168) | 40 | 4.0626 | −0.9995 |

The square series at its full published length (a(57)–a(70) due to Barequet
and Ben-Shachar, 2024):

| N | 40 | 50 | 60 | 70 |
|---|---|---|---|---|
| λ | 4.06256 | 4.06257 | 4.06257 | 4.06257 |
| θ | −0.99945 | −0.99974 | −0.99987 | −0.99988 |

λ = 4.06257 against the published 4.0625696 for fixed polyominoes is an
external anchor in the sense of `docs/external-anchors.md`: six digits from
code written for another lattice. θ converges monotonically toward −1 as
terms are added. Rescaling independence: king θ = −0.9997 at 6.8, 7.0,
7.11, 7.3; square θ = −0.9999 at 3.8, 3.95, 4.06; both degrade at the top
of their range (king 7.5 gives −0.9848; square 4.2 and 4.4 give −0.994).
Controls: a synthetic θ = −0.5 series reads −0.5000 at both scalings; a
synthetic square-λ series with θ = −1 reads (4.0600, −1.0000). What this
establishes is agreement to 2e−4 under one method at one length, not that θ
is exactly −1 nor which universality class either lattice is in.

### The confluent exponent Δ is not resolved at 40 terms (measured, 2026-08-22, ayr)

`experiments/confluent_universality.py`: the ansatz
a(n) = B λ^n n^θ exp(c n^(−Δ)) is linear in (ln B, ln λ, θ, c) once Δ is
fixed, so Δ runs on a grid of 0.005 from 0.10 to 3.0 and the least-squares
residual picks it. (A first version fitted the linearized 1 + c n^(−Δ) and
its own control returned 0.290 and 0.860 for planted 0.5 and 1.0; the
exp form returns 0.500 and 1.010.)

| | terms | Δ | λ | θ | residual |
|---|---|---|---|---|---|
| king | 40 | 0.575 | 7.11075 | −1.0159 | 7.4e−12 |
| square | 40 | 0.360 | 4.06392 | −1.0676 | 2.4e−09 |

| window starts at | king Δ | square Δ |
|---|---|---|
| n = 6 | 0.610 | 0.100 |
| n = 8 | 0.575 | 0.360 |
| n = 10 | 0.585 | 0.550 |
| n = 12 | 0.600 | 0.660 |
| n = 15 | 0.625 | 0.735 |

| square, N | 50 | 60 | 70 |
|---|---|---|---|
| Δ | 0.475 | 0.545 | 0.590 |
| λ | 4.06332 | 4.06304 | 4.06290 |
| θ | −1.0358 | −1.0235 | −1.0174 |

The window spread, not the residual valley, is the error bar: king
0.58–0.63, square 0.10–0.74 at 40 terms, so the matched-length comparison
returns nothing for the square. With its own 70 terms the square converges
monotonically to 0.590, inside the king's range. Neither number measures Δ₁:
planting a known Δ under a second, unmodeled correction recovers

| planted | 0.25 | 0.50 | 0.75 | 1.00 | 1.50 | 2.00 |
|---|---|---|---|---|---|---|
| king | 0.95 | 0.84 | 0.98 | 1.18 | 1.62 | 2.00 |
| square | 0.94 | 0.86 | 0.99 | 1.16 | 1.62 | 1.96 |

which is not monotone below about 0.75, so a recovered 0.6 cannot be
inverted to a Δ; and the calibration planted c > 0 where both real series
fit c < 0. A recovered 0.6 is evidence neither for Δ₁ = 0.6 nor against
Δ₁ = 1/2. The same fit returns λ_king = 7.1106–7.1108, λ_square = 4.06290 at
N = 70, and θ from −1.01 to −1.02, a third route to those numbers. Pinning
Δ₁ needs a second correction term with enough terms for five parameters, or
sub-dominant-singularity analysis; neither is built.

### Extrapolating the strip ladder to λ (measured)

A sliding three-point power-law fit μ_H = λ − c H^(−p)
(`experiments/lambda_from_mu.py`) gives λ estimates marching down as the
center rises: 9.54, 8.41, 7.92, 7.66, 7.50, 7.40, 7.33, 7.29 for centers
H = 5..12, with p → about 1. Strip spectra and row-sum ratios share no data
and no algorithm, so this corroborates 7.11 independently, though at H ≤ 13
it is not sharper. On H ≤ 11, full Richardson in 1/H² gives 7.41 and a local
two-point fit 6.64–6.71, so higher-order corrections matter.

`experiments/strip_fss.py` (2026-08-05) solves ln μ_H = ln λ − a/H − b/H²
exactly on consecutive triples of the seven-decimal ladder:

| triple | λ | a | b |
|---|---|---|---|
| [11,12,13] | 7.29817 | 1.65351 | 3.19705 |
| [13,14,15] | 7.25820 | 1.51121 | 4.11872 |
| [15,16,17] | 7.22999 | 1.39472 | 4.99006 |

(The script computes a = 1.65350, b = 3.19710 for the first triple, agreeing
with `numpy` and 50-digit `mpmath`; the table's last digits are display
rounding from the tool that first produced it and lie 10–25× below the
noise floor next.) Perturbing each μ_H in a triple by one unit in its
seventh decimal over all sign combinations gives spreads of λ 6.8e−5 to
1.1e−4, a 2.2e−4 to 5.0e−4, b 1.3e−3 to 4.0e−3; λ keeps 5–6 significant
figures, a 3–4, b 3. Against that floor, b climbs by +0.92 and +0.87 across
the triples (220–700× the floor) and λ drifts −0.020 then −0.014 per height
step (120–290× the floor), overshooting the differential-approximant 7.1102
by +0.120 at the top triple. The surface term H(ln λ − ln μ_H) at λ = 7.1102
is still falling at H = 17 by 0.035053 per step, and its increments shrink
6.52% per step where a clean 1/H² correction predicts (16/17)² ≈ 11.42%; at
λ = 7.111 the figures are 0.034940 and 6.54%. A third ansatz
ln μ_H = ln λ − a/H − c ln(H)/H² gives λ = 7.21575, 7.19121, 7.17462 on the
same triples (a = 1.10866, 0.99219, 0.90289; c = 3.25956, 3.62540, 3.92824),
halving the overshoot; three parameters on three points is an exact solve
and proves nothing about the correction's form.

The 2026-08-05 reading of these numbers was that a term between 1/H and
1/H², most likely logarithmic, is required. The 2026-08-22 analysis below
withdraws that inference, and the record holds the later reading; the
practical conclusion of both, that no 1/H² coefficient and hence no central
charge is readable from this ladder at H ≤ 17, stands.

`experiments/strip_fss_lambda_sensitivity.py` (2026-08-22, three negative
controls): the surface-term diagnostic feeds λ in as a constant, and an
error δ in ln λ adds H·δ to the surface term, so every increment picks up a
constant +δ that never decays. The increment ratio at H = 17, solved exactly
for the exponent q in S(H) = S_∞ + c H^(−q):

| λ fed in | dS(17) | ratio | shrink | q |
|---|---|---|---|---|
| 7.1102 | −0.035053 | 0.934769 | 6.52% | +0.078 |
| 7.111 | −0.034940 | 0.934572 | 6.54% | +0.082 |
| clean 1/H² | | 0.882353 | 11.76% | 1 |

(The asymptotic shortcut ((H−1)/H)^(q+1) reads q = 1.065 off an exactly-1/H²
ladder; the first control caught it.) The λ that makes the ladder look
clean at H = 17 is λ* = 7.2300; the two values tested differ by 8e−4, 150×
too small a range to see it. Over all 27 last-digit perturbations of
μ_15..μ_17, λ* stays within [7.229932, 7.230046]. λ*(H), the λ at which
height H's increment ratio equals the clean prediction, tends to λ for any
expansion whose leading correction is a/H:

| H | 7 | 9 | 11 | 13 | 15 | 17 |
|---|---|---|---|---|---|---|
| λ*(H) | 7.6044 | 7.4502 | 7.3574 | 7.2982 | 7.2582 | 7.2300 |

Monotone, decrements decaying as H^(−2.73); summing the tail gives
λ*(∞) = 7.1026, offset −0.0076 from 7.1102. The same extrapolator on two
synthetic ladders built at λ = 7.1102, one analytic (a/H + b/H² + c/H³ at
the fitted coefficients) and one with a genuine a/H + c ln H/H², returns
7.1095 and 7.1097, so its control accuracy is 7e−4 and the real ladder's
residual is ten times that. The raw diagnostic on the same three ladders
gives λ*(17) = 7.1211, 7.1647 and 7.2300 (offsets +0.011, +0.055, +0.120):
the real ladder's offset is twice the log-term synthetic's, yet all three
extrapolate to within 0.008 of the truth, so the offset measures how slowly
the correction series converges, not its form. The direct test, with λ held
at 7.1102 and ln μ_H = ln λ − Σ c_j/H^j fitted on a window:

| window | terms | rms residual | worst | λ if fitted instead |
|---|---|---|---|---|
| H ≥ 2 | 3 | 6.4e−3 | 1.3e−2 | 7.4178 |
| H ≥ 8 | 3 | 1.3e−4 | 2.1e−4 | 7.2088 |
| H ≥ 10 | 4 | 2.9e−6 | 4.1e−6 | 7.1556 |
| H ≥ 12 | 4 | 4.4e−7 | 6.6e−7 | 7.1487 |

The ladder's truncation floor is about 1.5e−8 in ln μ, so a four-term
analytic expansion at λ = 7.1102 describes H ≥ 12 to within 30× the floor
and nothing is left for a log term to explain. With λ free it comes out
7.15–7.25, drifting down as the window rises and terms are added, never
reaching 7.1102: the upward bias of a slowly converging asymptotic series on
a fitted leading constant. Not established: that there is no log term; a
small-amplitude one fits as well. Established: the ladder at H ≤ 17 cannot
tell them apart, and the fitted λ is still biased about +0.04 high at the
best window. The H ≥ 12 fit has six points against four coefficients.
Everything here takes λ = 7.1102(1) from the differential approximants as
given. Nothing here bears on the certified lower bound.

## Where a(n)'s weight sits: the height distribution

Data: the full triangle T(n,H), all H, n ≤ 40 (`results/triangle.txt`,
`results/ns_a40/perheight/`; the n ≤ 36 data in `results/ns_a36/perheight/`
reproduces every earlier number). Scripts `experiments/nu_exponent.py`,
`experiments/height_collapse.py`, `experiments/flank_saddle.py` (2026-07-10,
2026-07-11, refreshed on the final data 2026-07-31).

**The typical height grows sublinearly (measured).** The mean bounding-box
height weighted by T(n,H) divided by n falls monotonically:
0.745 at n = 4, 0.488 at n = 18, 0.392 at n = 36, 0.379 at n = 40, with
mean height 15.17 and mode 14 at n = 40. (An earlier H ≤ 18 slice gave
0.375 at n = 36 because 9.5% of that row's weight sits above H = 18;
`python3 experiments/nu_exponent.py 18` reproduces the slice.) Neither fixed
small height nor n/2.

**The extent exponent is not determined by n ≤ 40 (measured).** Four-step
local slopes d log⟨H⟩ / d log n:

| n | 12 | 16 | 20 | 24 | 28 | 32 | 36 | 40 |
|---|---|---|---|---|---|---|---|---|
| ν_eff | 0.7124 | 0.7007 | 0.6932 | 0.6879 | 0.6838 | 0.6806 | 0.6779 | 0.6757 |

Consecutive-n slopes run 0.744 at n = 5 to 0.675 at n = 40; the full-range
log-log fit over n = 4..40 gives 0.7009, dominated by small n. The drift per
four terms is shrinking (0.0027 over 32→36, 0.0022 over 36→40), consistent
with a slow confluent correction. The standard 2D lattice-animal value is
0.6407; the measured 0.676 is about 5% off, drifting the right way, with no
error bar, and no more terms are coming. Decision 2026-07-31: ν is not to be
used as evidence for or against universality; θ carries that point.

**The height distribution has a limit shape (measured).** Scaling each row
by its own mean and plotting ⟨H⟩ P_n(H) against H/⟨H⟩ collapses the rows,
and the collapse tightens with n (relative variance across a window):

| n window | 8,12,16,20 | 16,20,24,28 | 24,28,32,36 | 28,32,36,40 |
|---|---|---|---|---|
| relative variance | 0.1905 | 0.1008 | 0.0645 | 0.0384 |

| n | 12 | 20 | 28 | 36 | 40 |
|---|---|---|---|---|---|
| std/mean of H/⟨H⟩ | 0.2335 | 0.2295 | 0.2274 | 0.2261 | 0.2255 |
| skew | +0.249 | +0.311 | +0.337 | +0.351 | +0.356 |

The limit shape has coefficient of variation about 0.225, right skew about
0.36 (a longer tail toward tall shapes), and peaks near H/⟨H⟩ = 0.95. An
exponent collapse against H/n^ν prefers ν_eff ≈ 0.71 at these n, so the
shape statement is the robust one and the exponent is finite-size
renormalized.

**The tall flank is a large-deviation rate from the grand form
(semi-analytic).** For H = (1−α)n with α < 1/2, the diagonal formula's grand
form G(y) H(y)^n (`docs/proofs/grand-form.md`) gives by steepest descent

(1/n) ln T(n,(1−α)n) → ψ(α) = (1−3α) ln 3 + min_{y>0} [ln H(y) − α ln y],

the Legendre transform of ln H. The saddle-point value with Gaussian
prefactor against the exact entries T(40, 40−k) (`experiments/flank_saddle.py`,
18-term series for H):

| k | 3 | 8 | 12 | 15 | 17 | 18 | 19 |
|---|---|---|---|---|---|---|---|
| saddle / exact | 1.0279 | 1.0103 | 1.0077 | 1.0101 | 1.0187 | 1.0307 | 1.0611 |

Within 2% to k = 17 and 3.1% to k = 18, failing at k = 20 = n/2, one past
the formula's reach k_max(40) = 19, where G(y*) changes sign. At n = 36 the
ratio bottomed at 1.0091 (k = 10–11) and passed 2% by k = 15; the agreement
window widens with n as a genuine saddle asymptotic should. The rate
function is exact modulo the coefficients of H, theorems to k = 5 and fixed
from data to k = 17.

## Coordination number does not set λ (measured, 2026-08-22)

The short-rook lattice has neighborhood (±1,0), (0,±1), (±2,0), (0,±2): the
wazir plus the dabbaba, a rook that moves one or two squares. It has the
king's coordination number 8 with 6 triangles per site against the king's
12. `experiments/lambda_atlas_probe.py` with `--nmax 9` (about 12 minutes,
five negative controls) enumerates fixed animals to n = 9:

    square      1, 2, 6, 19, 63, 216, 760, 2725, 9910                (A001168)
    king        1, 4, 20, 110, 638, 3832, 23592, 147941, 940982      (A006770)
    short rook  1, 4, 24, 164, 1200, 9126, 71296, 567706, 4586448

A 1/n-corrected ratio extrapolation on nine terms is calibrated on the two
lattices with known λ:

| lattice | 9-term estimate | known λ | ratio |
|---|---|---|---|
| square | 3.9949 | 4.0626 | 0.9833 |
| king | 6.9885 | 7.1102 | 0.9829 |

The biases agree to 0.04%, and the fitted correction exponents are −0.717,
−0.719, −0.702 on the three lattices. Applying the correction to the short
rook's raw 8.8222 gives λ ≈ 8.974, about ±0.01 from the calibration spread:
26% above the king at the same coordination number, 18% of the way from the
king to the q = 8 tree bound (q−1)^(q−1)/(q−2)^(q−2) = 17.65. Local cycle
structure moves λ; coordination number is not the parameter. This is a
calibrated estimate, not a bound. The short-rook sequence was not in OEIS on
2026-08-22 (three query widths returned nothing; the square and king rows
returned A001168 and A006770 in the same session).

## Open problems

1. **Bring the upper bound below 8, or 7.5.** Every finite-window method
   floors strictly above λ: the certificate's slack is diffuse and grows
   with n, the window and cell-choice levers are exhausted, twig deferral is
   blocked, the concatenation split shatters, and the band code omits the
   join. The strip ladder enforces full connectivity within bounded height
   and converges from below; the twig methods have unbounded extent and
   relaxed connectivity and floor from above; connectivity with unbounded
   extent is what neither achieves. Candidate directions, none tried to a
   conclusion: (1) strip decomposition with a bound c(H) on the vertical-join
   multiplicity per column such that μ_H · c(H) ↓ λ, the crux being whether
   a tall bridge between strips is local; (2) a connectivity-witnessed
   certificate, a non-local decoration made local by a potential or flow
   argument; (3) a different invariant, perimeter or interface entropy, or a
   cluster-expansion bound; (4) accept the asymmetry. Machinery for any
   concrete alphabet: `experiments/certificate_bound.py`,
   `experiments/kernel_system.py`, `experiments/king_bound_R.py`; every
   candidate must first pass its rook analogue and stay above μ_13 = 6.306
   and the observed ratios near 6.9.
2. **Certify further heights.** H = 18 needs at least 192-bit accumulators
   to harvest the clamped tail, about 35–43 GB of transient memory and tens
   of minutes; each step buys about +0.05; the cost grows about 3.5× per
   step. H = 19 at about 127 GB is marginal and H = 20 at about 374 GB is
   out. Second-order twig geometries are unexplored, and a compact trial
   vector over connectivity signatures for an implicit-vector engine is
   unproposed.
3. **Δ₁ is unmeasured** on both lattices; the literature's 1/2 is a
   ratio-method value. **ν is unresolved** at 0.676 against 0.6407.
4. **Certified brackets on other lattices** (the short rook, and a λ atlas
   over neighborhoods) need `cpp/strip_mu_cert.cpp` made lattice-parametric;
   a short-rook strip reaches two rows and has a larger frontier. Nine terms
   of the short-rook sequence are unsubmitted.

## Reproduce

    make build/strip_mu_cert
    ./build/strip_mu_cert --selftest                       # the four self-tests; make gate-strip-cert
    ./build/strip_mu_cert 2 17                             # the certified ladder; receipts append to results/strip_mu_certificates.log
    scripts/run_strip_mu_cert_h14.sh                       # the H=14 runner (hash-map budget in its header)
    make build/strip_mu_fast && make gate-strip-fast       # the frozen-table engine and its gate, ~10 s
    ./build/strip_mu_fast 2 12                             # the ladder to H=12, ~4 s
    ./build/strip_mu_fast --verify 12 62191246 10000000    # re-check one certificate
    ./build/strip_mu_fast --ops 12 16                      # table sizes and memory
    ./build/strip_mu_fast --bench 14 16 --iters 20         # throughput
    ./build/strip_mu_kink 2 13                             # the hash-map reference
    python3 experiments/mu_H_precision_audit.py            # mu_H against the fixed-height GF roots
    python3 experiments/mu_H_from_atoms.py
    python3 experiments/strip_state_count_model.py         # non-crossing boundary states
    python3 experiments/lambda_from_mu.py                  # sliding power-law fit
    python3 experiments/strip_fss.py                       # two-parameter triples, surface term, H>=18 cost
    python3 experiments/strip_fss_lambda_sensitivity.py    # lambda*, synthetic controls, four-term fit
    python3 experiments/series_da.py                       # differential approximants, 40 terms
    python3 experiments/stretched_exponential_fit.py       # mu_1 test, ~20 s
    python3 experiments/theta_universality.py              # king against square
    python3 experiments/confluent_universality.py          # Delta on both lattices (--selftest for controls only)
    python3 experiments/convex_growth.py results/b006770_upload.txt
    python3 experiments/kingtwigs/l1_schemes.py 8          # level-1 twigs, ~13 s
    python3 experiments/concatenation_bound_check.py       # the F table and the comb
    python3 experiments/band_charge_probe.py 8             # band decomposition, ~40 s
    python3 experiments/nu_exponent.py                     # mean height and nu_eff (argument 18 for the old slice)
    python3 experiments/height_collapse.py                 # the collapse and moments
    python3 experiments/flank_saddle.py                    # the tall flank at n=40
    python3 experiments/lambda_atlas_probe.py --nmax 9     # the short rook, ~12 min

The upper-bound scripts are listed in `docs/proofs/polyplet-upper-bound.md`;
`paper/L3-lambda-bounds.tex` is the paper on the bracket and
`paper/verify_l_papers.py` checks its printed numbers.

## Sources

- `results/strip-growth-lambda-bounds.md` (deleted 2026-09-06; its content is above)
- `results/strip-mu-certificates.md` (deleted 2026-09-06; its content is above)
- `results/strip-mu-fast.md` (deleted 2026-09-06; its content is above)
- `results/strip-mu-engine-resumption.md` (deleted 2026-09-06; its content is above)
- `results/strip-fss-lambda-sensitivity.md` (deleted 2026-09-06; its content is above)
- `results/series-analysis-da.md` (deleted 2026-09-06; its content is above)
- `results/theta-universality.md` (deleted 2026-09-06; its content is above)
- `results/confluent-universality.md` (deleted 2026-09-06; its content is above)
- `results/stretched-exponential-test.md` (deleted 2026-09-06; its content is above)
- `results/concatenation-upper-bound.md` (deleted 2026-09-06; its content is above)
- `results/bridge-credit-closed.md` (deleted 2026-09-06; its content is above)
- `results/king-twigs-l1.md` (deleted 2026-09-06; its content is above)
- `results/lambda-atlas-probe.md` (deleted 2026-09-06; its content is above)
- `results/nu-exponent.md` (deleted 2026-09-06; its content is above)
- `results/height-distribution-collapse.md` (deleted 2026-09-06; its content is above)
- `docs/open-problem-lambda-bracket.md` (deleted 2026-09-06; its content is above)
