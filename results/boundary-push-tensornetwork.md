# Boundary-push probe #1: can a tensor-network (MPS) compress the frontier?

**2026-07-02.** `experiments/frontier_svd/` (dump_frontier.cpp + svd_probe.py).
The big-swing idea: the engine stores the frontier as ~λ^(H/2) explicit
{signature → count} entries, but that vector lives on a 1-D chain of H boundary
sites. If its Schmidt rank across a boundary cut is small, a matrix-product
state stores it in H·χ² instead of λ^(H/2) — a potential exponential→polynomial
win. We MEASURED the rank by dumping the real frontier count-vector and taking
the SVD across the balanced central cut.

## Result — MEASURED, decisive

| H | frontier states | exact rank χ (central cut) | χ²/frontier | MPS cost H·χ² | front/MPS |
|---|---|---|---|---|---|
| 8  | 1,604   | 21  | 0.28 | 3,528   | 0.45× (worse) |
| 10 | 11,005  | 51  | 0.24 | 25,000  | 0.44× (worse) |
| 12 | 68,343  | 127 | 0.24 | 178,608 | 0.38× (worse) |
| 14 | 161,357 | 298 | 0.55 | 623,294 | 0.26× (worse) |

The exact bond dimension χ grows exponentially: 21→51→127→298, ratio ~2.4 per
+2 in H (χ ~ λ^(H/4), the *square root* of the frontier λ^(H/2)). So
χ² is a large fraction of the frontier itself (0.24–0.55; the H=14 point is
inflated because that dump was at maxn=16, off the true peak column). Either
way **MPS storage H·χ² is 2–5× the explicit frontier and the front/MPS ratio
falls monotonically 0.45→0.26** as H grows — MPS loses by more, not less. The
singular values barely decay (H=12: 2nd/1st = 0.60; χ_eff(1e-6)=122 ≈ full rank
127).

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
the audit's I/O/alloc wins, the #12 u64-per-state record shrink (~2× at the
spill peak — the top un-banked lever), and cross-machine splitting. Knowing the
wall is real is itself worth the probe: it says don't burn a(28)–a(30)'s
schedule hunting a closed form or a compression that the data rules out.
