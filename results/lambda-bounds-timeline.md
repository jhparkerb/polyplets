# Timeline of rigorous bounds on the king-lattice (polyplet) growth constant lambda

The king-lattice growth constant had NO published bounds before 2026 -- every prior paper on
A006770 is enumeration-only (counts + perimeter polynomials, no asymptotic analysis). The
entire bound history below is from this work; the methods are standard (square-lattice
polyominoes), applied here to the king lattice for the first time.

| Year | Upper  | Lower    | Work that set the **bold** value |
|------|--------|----------|----------------------------------|
| 1990 | --     | --       | Mertens, *Lattice animals: a fast enumeration algorithm and new perimeter polynomials* (J. Stat. Phys. 58:1095) -- king counts to n=14; no bound |
| 2024 | --     | --       | Tremblay-Vernay, *On the generation of discrete figures with connectivity constraints* (RAIRO 58) -- king counts to n=18; no bound |
| 2026 | --     | **5.63** | this work -- Fekete floor a(20)^(1/20) (supermultiplicativity a(m)a(n) <= a(m+n)) |
| 2026 | --     | **5.99** | this work -- bounded-height strip growth rate lambda_10 (height-<=10 GFs) |
| 2026 | **15.83** | 5.99  | this work -- ancestor-exclusion (d=4) upper bound (method floor ~15.56) |
| 2026 | 15.83  | **6.54** | this work -- Rands-Welsh concatenation (Rands & Welsh 1981 method) on the confirmed n<=19 series |

Series ESTIMATE (not a bound): lambda ~ 7.12-7.155 (2D lattice-animal universality, theta=1).
Current rigorous interval: **[6.54, 15.83]**. The lower bound climbs toward lambda with each new
a(n) term (Rands-Welsh: 6.42 @ n<=15, 6.49 @ 17, 6.54 @ 19); the upper bound is the weak side and
needs a different method to tighten. Scripts: experiments/lambda_lower_bound.py, lambda_series.py.

## Correction (2026-06-22): "first" overclaim withdrawn
Computing lambda from a(n)/a(n-1) is trivial, so a priority claim is unwarranted -- an informal
lambda ~ 7 very likely exists somewhere not surfaced here. Honest nuance: the communities holding
king-lattice data optimized DIFFERENT quantities. Percolation work targets the threshold p_c
(Mertens 1990 even tabulates the nnSquare mean-cluster-size series S(p)=sum b_r p^r, but its
singularity is p_c, NOT 1/lambda); the enumeration papers report only counts. So the *animal
growth constant* lambda may be genuinely under-attended for the king lattice -- but that is not
"first". Defensible claims only: (1) no lambda VALUE was found in OEIS, the Mertens enumeration
papers, or web/percolation searches; (2) ours uses n<=20, more terms than the best PUBLISHED
enumeration (n<=18), so it is plausibly the sharpest current estimate; (3) I have not seen the
Rands-Welsh / ancestor-exclusion bounds applied to the king lattice specifically. Treat all of the
above as "no published value located," NOT a priority claim.

## Per-publication view (best estimate = ratio of the two largest terms that paper establishes)
| Year | Lower | Best estimate (a_n/a_{n-1}) | Upper | Publication (max n) |
|------|-------|------------------------------|-------|---------------------|
| 1990 | 6.387 | 6.621 | --    | Mertens, fast enumeration algorithm (n=14) |
| 2024 | 6.516 | 6.727 | --    | Tremblay-Vernay, generation of discrete figures (n=18) |
| 2026 | 6.540 | 6.747 | 15.83 | this work (n=19, confirmed) |
| 2026 | 6.563 | 6.765 | 15.83 | this work (n=20, candidate) |

True value lambda ~ 7.12-7.155. Best-estimate column = raw consecutive ratio (trivial; what each
paper de-facto established). Lower column = Rands-Welsh bound those same terms SUPPORT (deterministic
in the data) -- but the pre-2026 rows are RETROACTIVE: Mertens and Tremblay-Vernay published only the
counts, no bound was drawn until this work. Upper = ancestor-exclusion (method-based, not term-based),
so it appears only when computed (2026). Both estimate and lower bound approach lambda from below as
terms are added; the upper bound is the weak side.
