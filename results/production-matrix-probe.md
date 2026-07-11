# Production-matrix probe of T(n,H)  (the Riordan / Stieltjes test, run for real)

Date: 2026-07-10. `experiments/production_matrix_probe.py` on the banked triangle
(`results/ns_a36/perheight/h{H}.out`, 18×18 block). Directly computes the
production matrix `P = L⁻¹L̄` (L = the T(n,H) triangle, L̄ = L shifted up one row)
and inspects it for Riordan / banded / polynomial structure. This is the explicit
version of the local-recurrence probes in [[boundary-push-recurrence]] — a
constant-but-dense `P` is a slightly different object than the bounded-shift
recurrences tested there, so it was worth computing outright.

## Result

- **Not Riordan.** 89 Toeplitz violations of 289 (`P[m,H] ≠ P[m−1,H−1]`); columns
  are not shifts of one another. (Consistent with the Atom Ledger: columns of L
  factor as `q_H q_{H−1} q_{H−2}`, not `g·f^H`.)
- **Not banded.** Every row `m` has support `H ∈ [2, m+1]` — a dense back-reference
  to column 2. So there is no finite production rule; a finite/banded constant `P`
  would be a constant-coefficient 2D recurrence, which does not exist.
- **BUT the band near the diagonal is eventually-Toeplitz** (constant diagonals):

  | offset `H−m` | constant | stabilizes by row |
  |---|---|---|
  | +1 (superdiag) | `3` (exact) | m=1 |
  | 0 | `25/9` | m=3 |
  | −1 | `208/243` | m=5 |
  | −2 | `1483/6561` | m=7 |
  | −3 | `6896/59049` | m=9 |
  | −4 | `130208/4782969` | m=11 |

  Offset `−k` settles at row `≈ 2k+3`, matching the diagonal closed-form order
  `2k+1`. Denominators are powers of 3 — the `3ⁿ` diagonal structure.

## Band-constant denominators: 3^{3k+2} (verified k=0..6)

The settled band constant `c_k` at offset `−k` has natural (unreduced) denominator
`3^{3k+2}` — verified by `experiments/band_constants_3adic.py` (`c_k·3^{3k+2} ∈ ℤ`
for k=0..6):

| k | 0 | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|---|
| natural denom | 3² | 3⁵ | 3⁸ | 3¹¹ | 3¹⁴ | 3¹⁷ | 3²⁰ |
| reduced denom | 3² | 3⁵ | 3⁸ | 3¹⁰ | 3¹⁴ | 3¹⁷ | 3¹⁹ |

Reduction eats one factor of 3 exactly at `k=3,6` (`k≡0 mod 3`), where the natural
numerator has `v₃=1` (`20688=3·6896`, `36500568=3·12166856`). `3^{3k+2}` is the
clean invariant; the reduced denominators understate the regularity.

NB: these `c_k` are the *production-matrix* band constants, NOT the a26–a30
diagonal polynomials `P_k` (`T(n,n−k)=poly₂ₖ(n)·3ⁿ`). **Checked**
(`experiments/Pk_denominator_check.py`): `P_k` denominators do NOT follow
`3^{3k+2}` and from k=2 up are **not even pure powers of 3** (they carry other
primes — the factorial-type denominators of a degree-`2k` fit). `P_k` common
denoms: `3¹, 3⁴, 3⁷·2, …`. So `3^{3k+2}` is a fact about `P`'s band only; the
diagonal closed forms live on their own mixed denominators. (The fit also
re-confirms `P_k` is exactly degree `2k`: matches all data past the single
`n=k+1` boundary transient.)

## Diagonal vs band: shared 3-adic slope (the intrinsic invariant)

The monomial-basis `P_k` denominators (above) are contaminated by factorial /
Vandermonde interpolation denominators (non-3 primes AND fake 3-adic jumps). The
**Newton (finite-difference) basis** removes that — `Delta^j P_k` are differences
of pure-3-power values, no factorials — giving the intrinsic 3-adic content
(`experiments/Pk_newton_3adic.py`):

| k | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|---|
| `v₃(P_k)` Newton | 1 | 4 | 7 | 10 | 13 | 16 | 19 | 22 | 25 |

**`v₃(P_k) = 3k+1` exactly, pure 3-powers, flat +3 differences, NO anomaly at
k≡0 mod 3** (the apparent monomial anomalies at k=3,6 were interpolation noise).

So the two objects share a 3-adic slope and differ by one tripling:

- band constant: natural denom `3^{3k+2}`
- diagonal `P_k` (Newton): `3^{3k+1}`
- `3^{3k+2} = 3 · 3^{3k+1}` — the band is the diagonal's valuation **plus one
  factor of 3 = the de-tripling factor** (`L̄ = 3D·L'̄ ⇒ P = 3P'`). The band and
  diagonal 3-adic structures are the same law offset by that single tripling.

## Interpretation

`P` separates cleanly into the two halves we already knew:

- **Eventually-constant band = the diagonal closed forms** (`T(n,n−k)=poly₂ₖ(n)·3ⁿ`).
  The superdiagonal `3` is the king-chain identity `T(n+1,n+1)=3·T(n,n)`; the band
  constants are the settled bulk's production rule = the diagonals we already
  exploit (a26–a30 plan). Surviving, usable structure.
- **Never-truncating tail to column 2, entries exploding in 3-powers = the atom
  obstruction** ("each new height a new atom") made concrete. This is why no
  finite production rule / Riordan shortcut exists.

## Conclusion

Running the production-matrix / Riordan approach on `T(n,H)` for real reproduces
the established picture: partial (diagonal) structure yes — and we use it — but no
global production rule and no Riordan row-sum shortcut for `a(n)`. Blocked by the
same atom/connectivity wall as [[boundary-push-recurrence]] (not 2D-holonomic) and
the non-D-finiteness of `a(n)`. No new lever; a clean concrete confirmation.
See also [[algorithmic-levers-dead-connectivity-wall]].
