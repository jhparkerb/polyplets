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
Current rigorous interval: **[6.54, 9.355]** (see the upper-bound section below for the 15.83 ->
10.354 -> 9.355 progression). The lower bound climbs toward lambda with each new
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

## Prior qualitative handle: Mertens-Lautenbacher 1991, p.670
Their introduction DOES reference the growth constant: "The time required for a complete
enumeration of lattice animals up to a size s grows roughly like ~ lambda^s, where lambda is
somewhat below the coordination number of the lattice." For the king lattice the coordination
number z = 8 (the 8 king-moves), so this is a QUALITATIVE statement lambda < ~8. Our 7.12-7.15
(= 0.89*z) is consistent and makes it QUANTITATIVE. So the literature had a qualitative handle
(lambda ~ somewhat below 8) -- we are not "first to consider lambda," only first to pin a number
+ a rigorous bracket. Caveats: it's a timing heuristic, and lambda < z is NOT rigorous (square:
lambda=4.06 > z=4, slightly above; holds for triangular 5.18<6 and king 7.1<8). Notably this
heuristic (~8) is far closer to the truth than our rigorous UPPER bound (15.83) -- underscoring
that the upper side is loose and a real upper-bound method landing near ~8 would be the new win.

## Upper bound tightened (2026-06-22): 15.83 -> 10.354 -> 9.355
| Year | Upper  | method |
|------|--------|--------|
| 2026 | 15.83  | ancestor-exclusion (floor ~15.56) |
| 2026 | 12.207 | uniform twig (1+x)^5 = 3125/256 (closed form) |
| 2026 | 10.354 | directional twig = depth-1 ancestor-exclusion (Eden/Klarner-Rivest/Barequet-Shalah); VERIFIED |
| 2026 | **9.355** | **ITERATED (depth-5) ancestor-exclusion**; VERIFIED -- experiments/lambda_upper_bound_iterated.py |
Rigorous interval now **[6.54, 9.355]** (was [6.54, 10.354]).

**Iterated ancestor-exclusion (2026-06-22 eve).** The depth-1 directional twig (10.354) generalizes:
a BFS-tree cell C can discover neighbor q only if NO proper ancestor of C is adjacent-or-equal to q
(an ancestor has smaller BFS depth, so reaches q first). Tracking the last d discoverer-directions
as the cell type and excluding child-slots adjacent to ANY of the d ancestors gives a monotone,
rigorously-valid tightening sequence (we only ever drop provably-impossible children):
king 10.354 (d1) -> 9.482 (d2,d3) -> 9.399 (d4) -> **9.355 (d5)**. VALIDATED on the square lattice
anchor: depth-1 = Eden 27/4 = 6.7500 exactly, decreasing 6.75 -> 5.219 -> 5.163 with depth (stays
above the true 4.0626; remains above Klarner-Rivest's stronger 4.649, since pure ancestor-exclusion
is weaker than KR's empty-cell method). The bound PLATEAUS ~9.3 -- so reaching the ~8 heuristic needs
a stronger refinement (propagating known-EMPTY frontier cells, not just occupied ancestors), not more
depth. Self-checking script with the square anchor; runs on ayr (8^d types, king to d5 = 32768).
