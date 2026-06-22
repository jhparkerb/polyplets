# T1, the general case: is N_H irreducible for *all* H?

The lifetime-3 law (`results/lifetime3-proof.md`) is rigorous except for one lemma, (3a):
**each atom N_H is irreducible over Q.** Verified now to H<=8 (mod-p subset-sum certificate),
but a proof for all H is open. This note pins down exactly what must be shown, reframes it
as a single clean conjecture, gathers Frobenius evidence, and assesses the attack routes.

## The precise target, and a structural reduction
N_H is the reduced denominator of the unanchored H-row strip GF
`V_H(x) = u^T (I - x T_H)^{-1} v`, where T_H is the (nonnegative) H-strip column-transfer
matrix. After cancellation, `N_H(x) = prod_{mu observable} (1 - mu x)` over the **observable
+ controllable** eigenvalues mu of T_H (those with `u^T P_mu v != 0`), and it is squarefree
(verified H<=10). Its roots are the `1/mu`. Therefore:

> **N_H is irreducible over Q  <=>  Galois acts transitively on the observable spectrum**
> (the observable eigenvalues of T_H are mutually conjugate, forming one orbit of size
> deg N_H).

Equivalently (Perron-Frobenius gives a real simple dominant root lambda_H): N_H is
irreducible iff **the strip Perron eigenvalue lambda_H is a primitive element** of the
reduced-GF number field, `[Q(lambda_H):Q] = deg N_H`.

## The clean sharper conjecture
The natural strengthening -- and the one the data supports -- is maximal symmetry:

> **Conjecture (G_H).** `Gal(N_H / Q) = S_{deg N_H}`, the full symmetric group.

G_H implies (3a) (transitive => irreducible) and is *cleaner* than bare irreducibility: it
says the atoms are as "generic" as a polynomial of that degree can be, which is what one
expects of a combinatorial transfer matrix carrying no extra algebraic structure (no
self-reciprocality, no cyclotomic/Chebyshev factor, no CM). It is testable by Chebotarev:
mod p, the factor-degree partition of N_H is the cycle type of Frobenius_p (Dedekind), so
sampling primes samples conjugacy classes of Gal. Under S_d one predicts
- irreducible reductions (a d-cycle) at density 1/d,
- a linear factor (>=1 fixed point) at density 1 - 1/e ~ 0.632,
- both permutation parities present  <=>  disc(N_H) not a square  <=>  Gal not subset A_d.

### Frobenius evidence (`experiments/t1_galois.py`, all mod p -- no rational blowup)

| H | deg d | #primes | irreducible (pred 1/d) | fixed-pt (pred .632) | odd-perm (pred .5) | verdict |
|---|------:|--------:|------------------------|----------------------|--------------------|---------|
| 3 |     4 |     600 | 0.210 (0.250)          | 0.670 (.632)         | 0.478              | S_4  ✓ |
| 4 |     9 |     600 | 0.118 (0.111)          | 0.612 (.632)         | 0.462              | S_9  ✓ |
| 5 |    29 |     300 | 0.047 (0.034)          | 0.627 (.632)         | 0.493              | S_29 ✓ |
| 6 |    68 |      80 | 0.0125 (0.015)         | 0.625 (.632)         | 0.475              | S_68 ✓ |
| 7 |   181 |      40 | 0.000 (0.006)          | 0.725 (.632)         | 0.550              | consistent* |

All three S_d signatures match for H=3..6. H=7 is consistent within its small sample:
irreducible density 1/181 predicts ~0.2 hits in 40 primes, so seeing 0 is unremarkable, and
the 0.725 fixed-point rate is noise around 0.632 at n=40. The **fixed-point rate locking
onto 1 - 1/e and the odd-permutation rate onto 1/2** (so disc not square, Gal not in A_d)
are the sharpest S_d fingerprints, and they hold across every H tested. So G_H is strongly
supported: (3a) -- and with it the whole exactly-3 law -- is a corollary of a clean,
well-evidenced symmetric-group conjecture rather than an isolated irreducibility claim.

## Attack routes for a general proof, and the obstruction
1. **Large-Galois-group structural argument.** Show T_H's observable characteristic
   polynomial must have Galois group S_d. No general method exists for transfer-matrix
   char polys; one would need to exhibit, *uniformly in H*, primes realizing a d-cycle and
   a transposition (a p-cycle + a transposition generate S_d when d is prime -- and 181 is
   prime), but the transposition class has density `~1/binomial(d,2)`, astronomically rare
   to hit by sampling. So the S_d route is provable in principle but not by computation.
2. **p-adic / Newton-polygon.** Find, for each H, a prime at which N_H is Eisenstein-like
   or has a Newton polygon forcing irreducibility. Transfer-matrix polynomials rarely carry
   such structure, and "for each H" needs a uniform construction, not luck.
3. **Induction on H via the strip recursion.** B_H = V_H - 2 V_{H-1} + V_{H-2} couples three
   consecutive strips; if T_H had a block structure over T_{H-1} making the *new* atom's
   eigenvalues a single conjugacy class, irreducibility would be inductive. This is the only
   route that uses the problem's own structure rather than generic polynomial theory -- the
   most promising, and the least explored. The obstruction: there is no evident reason the
   "genuinely new at height H" eigenvalues are conjugate to each other and to nothing older.

## Honest status
- (3a) and squarefreeness are now *mechanized* and verified to the edge of the recovered GF
  data (H<=8 / H<=10), blowup-free.
- The general statement is genuinely open and research-grade. The cleanest formulation is
  the conjecture G_H (Gal = S_d); the evidence below is consistent with it. A proof is not
  in reach by computation (the certifying Frobenius classes are too rare) and needs either a
  structural large-Galois theorem or the strip-recursion induction -- neither available.
- Per the result's own "honest weight" note: this is a tidy structural fact, worth a
  paragraph, not a centerpiece. The right write-up states lifetime-3 with (3a) verified
  H<=8 and flagged as conjecturally-G_H for all H, and moves on.
