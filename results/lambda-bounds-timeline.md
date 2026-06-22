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
