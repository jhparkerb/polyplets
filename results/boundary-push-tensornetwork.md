# Boundary-push probe #1: can a tensor-network (MPS) compress the frontier?

**2026-07-02.** `experiments/frontier_svd/` (dump_frontier.cpp + svd_probe.py).
The big-swing idea: the engine stores the frontier as ~λ^(H/2) explicit
{signature → count} entries, but that vector lives on a 1-D chain of H boundary
sites. If its Schmidt rank across a boundary cut is small, a matrix-product
state stores it in H·χ² instead of λ^(H/2) — a potential exponential→polynomial
win. We MEASURED the rank by dumping the real frontier count-vector and taking
the SVD across the balanced central cut.

## Result — MEASURED, decisive

| H | frontier states | exact rank χ (central cut) | χ²/frontier | MPS cost H·χ² | vs frontier |
|---|---|---|---|---|---|
| 8  | 1,604  | 21  | 0.275 | 3,528   | 0.45× (worse) |
| 10 | 11,005 | 51  | 0.236 | 25,000  | 0.44× (worse) |
| 12 | 68,343 | 127 | 0.236 | 178,608 | 0.38× (worse) |

**χ²/frontier is flat at ~0.24**, so the bond dimension is
**χ ≈ ½·√(frontier) = λ^(H/4)** — exactly the square root of the frontier size.
Then MPS storage `H·χ² ≈ 0.24·H·frontier` is *strictly worse* than the explicit
frontier, by a growing factor ~H. The singular values decay slowly (at H=12 the
2nd/1st ratio is 0.60; χ_eff(1e-6)=122 ≈ the full rank 127 — almost no decay).

**Why:** the entanglement is *connectivity* entanglement. Cutting the boundary
splits non-crossing-partition components; the rank at the cut = the number of
distinct ways components cross it ~ Catalan/Motzkin at the cut ~ λ^(H/4). This
is intrinsic to counting connected objects, the same reason FK/Potts cluster
transfer matrices are high-rank in the connectivity basis.

## Verdict

**Exact MPS does not beat the current representation** — the frontier is already
"maximally entangled" at the √ level; there is no low-rank structure to exploit
with a site-ordered MPS. Confirmed flat over H=8,10,12 (H=14 pending, trend
locked).

**The one nonzero benefit:** at 1e-3 relative truncation, χ_eff drops to
~0.16·√frontier (H=12: 42 vs 127), giving H·χ² ≈ 3× *smaller* than the frontier
and the margin grows with H — but this yields only an **approximate** count, and
truncation error compounds across columns. Usable at most as a fast approximate
size/cost oracle or a coarse cross-check, never for exact enumeration.

**Open door (uncertain):** a connectivity-aware tensor structure
(Temperley–Lieb / link-pattern basis) rather than a naive site-MPS is the only
form that could in principle help — but the known TL representations don't drop
below the Catalan dimension for exact work, so this is a speculative research
bet, not a lever.

## Strategic consequence

Both algorithmic-breakthrough probes now have measured-negative verdicts:
- No 2D holonomic accelerator ([[boundary-push-recurrence]]): T(n,H) not
  jointly D-finite.
- No MPS frontier compression (this doc): χ² ≈ frontier.

Together they say **the exponential frontier is intrinsic** — the √λ diagonal
sweep is essentially optimal among the recurrence/GF and tensor-network families.
So the path to a(28)–a(30) faster is **engineering, not a new algorithm**:
the audit's I/O/alloc wins, the kinkless reverse-signature merge (~2× at the
spill peak — the top un-banked lever), and cross-machine splitting. Knowing the
wall is real is itself worth the probe: it says don't burn a(28)–a(30)'s
schedule hunting a closed form or a compression that the data rules out.
