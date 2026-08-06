# A006770 (isotropic polyplets): P-recurrence and algebraic exclusion boxes on 40 terms

2026-08-05, banking Phase 0 of `docs/middle-kingdom-followups-plan.md`. All
boxes below were re-run from scratch for this file (`build/prec_guess`,
input `results/b006770_upload.txt`, all 40 banked terms of A006770, prime
`2^61-1`) and every verdict matches the reference table measured earlier the
same session (`git=54440c2-dirty`).

## Method

`build/prec_guess` (`cpp/prec_guess.cpp`) tests two ansatze against a term
series by building an integer matrix and computing its rank mod a prime.
`prec` mode tests a P-recurrence `sum_{i=0..J} p_i(n) a(n+i) = 0` with
`deg p_i <= D`; `alg` mode tests an algebraic relation
`sum_{j=0..K} q_j(t) F(t)^j = 0` with `deg q_j <= L` for the generating
function `F(t) = sum a(n) t^n`. Two facts make one run per box decisive
rather than a sweep:

- **The boxes nest.** A solution with smaller `(J,D)` (resp. `(K,L)`) is also
  a solution of any larger box containing it (pad the unused coefficients
  with zero), so excluding the maximal box excludes every box nested inside
  it.
- **Full column rank mod p is a proof over Q.** The matrix has integer
  entries; full rank mod a prime means some maximal minor is nonzero mod
  that prime, hence nonzero over Q, hence the only rational solution is
  trivial. Rank can only drop under reduction mod p, never rise, so a
  full-rank verdict mod p is rigorous, not a numerical hint. A rank
  *defect* mod p is only a candidate (needs holdout + a second prime); this
  session hit none.

Both points are argued in full in `cpp/prec_guess.cpp`'s header comment and
exercised at larger scale in `results/convex-polyplets.md`'s "Non-D-finite
at order<=24, degree<=24" section (700-term HV-convex-by-area series, same
tool).

## The boxes (40 terms, prime `2^61-1`)

| box (J,D) | `prec` verdict | `alg` verdict |
|---|---|---|
| (4,5) | EXCLUDED | EXCLUDED |
| (5,4) | EXCLUDED | EXCLUDED |
| (4,6) | EXCLUDED | EXCLUDED |
| (3,7) | EXCLUDED | EXCLUDED |
| (3,8) | EXCLUDED | EXCLUDED |
| (2,11) | EXCLUDED | EXCLUDED |
| (6,3) | EXCLUDED | EXCLUDED |
| (7,3) | EXCLUDED | EXCLUDED |
| (5,5) | INCONCLUSIVE (35 rows ≤ 36 unknowns) | EXCLUDED |
| (6,4) | INCONCLUSIVE (34 rows ≤ 35 unknowns) | — |

Reproduce (each box takes well under a second):

```
make build/prec_guess
build/prec_guess prec results/b006770_upload.txt 4  5
build/prec_guess prec results/b006770_upload.txt 5  4
build/prec_guess prec results/b006770_upload.txt 4  6
build/prec_guess prec results/b006770_upload.txt 3  7
build/prec_guess prec results/b006770_upload.txt 3  8
build/prec_guess prec results/b006770_upload.txt 2 11
build/prec_guess prec results/b006770_upload.txt 6  3
build/prec_guess prec results/b006770_upload.txt 7  3
build/prec_guess prec results/b006770_upload.txt 5  5
build/prec_guess prec results/b006770_upload.txt 6  4
build/prec_guess alg  results/b006770_upload.txt 4  5
build/prec_guess alg  results/b006770_upload.txt 5  4
build/prec_guess alg  results/b006770_upload.txt 4  6
build/prec_guess alg  results/b006770_upload.txt 3  7
build/prec_guess alg  results/b006770_upload.txt 3  8
build/prec_guess alg  results/b006770_upload.txt 2 11
build/prec_guess alg  results/b006770_upload.txt 6  3
build/prec_guess alg  results/b006770_upload.txt 7  3
build/prec_guess alg  results/b006770_upload.txt 5  5
```

## Honest scope

These are exclusions, not a non-D-finiteness proof. 40 terms is short: the
largest box any pair here decides is around order 7 / degree 3 or order 3 /
degree 8 (`unknowns = (J+1)(D+1)`, and rows run out once unknowns approach
the term count), and two of the ten boxes above are already INCONCLUSIVE
rather than EXCLUDED because rows ≤ unknowns. A finite-box exclusion is
evidence against a *small* P-recurrence or algebraic relation; it says
nothing about a large one, and it is not a proof that the isotropic
polyplet generating function fails to be D-finite.

That larger claim is exactly the open half of the anisotropic/isotropic
split: `paper/related-work-notes.md:51` records it as "OPEN (isotropic):
the ordinary (isotropic) polyomino GF being non-D-finite is still a
conjecture; passing from anisotropic to isotropic is hard. So write
'believed not D-finite,' not 'proven.'" `paper/polyplets-report.tex:878`
(`\subsection{The by-height generating function is not D-finite}`) proves
non-D-finiteness of the *anisotropic* by-height GF `F(x,y) = sum T(n,H)
x^n y^H`; that theorem is about a different, two-variable object and this
note's boxes do not touch it, do not extend it, and are not a step toward
proving the isotropic conjecture. They are a (small, rigorous) data point
consistent with the belief, nothing more.
