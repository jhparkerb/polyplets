# Frontier SVD / MPS feasibility probe

**Status: feasibility probe complete. Verdict: NEGATIVE — the wall is real.**

## The question

The diagonal transfer-matrix engine stores the frontier at each column as an
explicit dictionary of `{signature -> count}` entries (≈ the peak-states figure,
empirically ~2^H–3^(H/2)). Each signature lives on a 1-D chain of `H` boundary
sites (`cpp/tma/signature.h`: `H` boundary labels + 2 touch flags). If we treat
the count vector `psi(sig)` as a tensor over those `H` sites and take an SVD
across a cut, the singular-value spectrum is the exact Schmidt spectrum of the
frontier at that cut. If it decays fast, an MPS with small bond dimension `chi`
stores the frontier in `H·chi^2` space instead of the exponential dictionary — an
exponential→polynomial win. If it decays slowly, the frontier is genuinely
high-entanglement and no MPS helps. **We measure which.**

## The tensor and the cut

`psi` is a vector indexed by signature. A signature is the byte string
`b[0..H-1]` (boundary component labels, 0 = empty) plus `b[H], b[H+1]` (touched-
top / touched-bottom flags). We reshape `psi` into a matrix by splitting the
byte string at a boundary cut position `c`:

```
M[L, R] = psi( bytes[0:c]  ++  bytes[c:H] ++ flags )
          L = bytes[0:c]            (left block, rows)
          R = bytes[c:H] ++ flags   (right block, cols)
```

`sig <-> (L, R)` is a bijection (it is just splitting the string), so this is the
exact tensor-train / MPS reshape at the cut. We densify `M` over the *distinct*
left- and right-substrings that actually occur (both are small: partitions of ≤c
sites). `rank(M)` is then the **exact MPS bond dimension** required at that cut,
and the singular-value decay says how far lossy truncation can shrink it.

Caveat (noted, does not change verdict): signatures are globally canonicalized
(`canonicalizeSig`), so a component label carries which side it first appeared
on. This can only *inflate* the apparent rank, so our `chi` is a conservative
(upper-bound) estimate of the true physical bond dimension — good enough to kill
the idea, not to resurrect it.

## Why exact integer counts, NOT mod p

The prompt suggested mod-p counts. **We deliberately did not use them.** SVD
measures singular-value *decay*, a real/Euclidean-geometry notion. Reducing
counts mod p replaces each amplitude with an essentially uniform random residue
in `[0,p)`, which destroys the decay and inflates every matrix to (near) full
numerical rank. Mod-p would only give the GF(p) rank (a lower bound on `chi`),
never the compressibility we are testing. So the dumper emits **exact u64
counts**; at these `H`/`maxn` the partial-animal totals fit u64 comfortably.

## The metric and decision rule

- `chi_eff(epsilon) = #{ sigma_i : sigma_i > epsilon·sigma_max }` at
  `epsilon = 1e-3, 1e-6, 1e-9`.
- MPS storage cost model: `H·chi_eff^2`, compared against the explicit frontier
  size `N = len(psi)`.
- **Decision rule:** MPS is worth pursuing only if `chi_eff` at an
  exact-counting-relevant tolerance stays *polynomial* in `H` while `N` grows
  exponentially, i.e. `N / (H·chi_eff^2)` grows with `H`. If `chi_eff` tracks the
  full rank and grows exponentially (so `H·chi_eff^2 >= N`), the frontier is
  volume-law entangled and the wall is confirmed.

## How the frontier is dumped

`experiments/frontier_svd/dump_frontier.cpp` — standalone, includes the engine
headers READ-ONLY (`signature.h`, `statedb.h`, `transition_square8.h`) and drives
the production step kernel `stepColumnSquare8` / `forEachViableMask` /
`completionLowerBound` directly. It runs its own serial exact-count sweep (a copy
of the serial loop in `cpp/tma/sweep8_modp.h`, minus the mod-p reduction, minus
the R1 fold) and dumps `{signature bytes, total count}` at a chosen column. It
links nothing in production and touches no `runs/` state. Build:

```
c++ -std=c++20 -O3 -Icpp/tma experiments/frontier_svd/dump_frontier.cpp -o build/frontier_dump
./build/frontier_dump <H> <maxn> <col|-1=peak> <out.txt>
```

`experiments/frontier_svd/svd_probe.py <frontier files...>` reads the dumps,
builds `M` at several cuts, runs `numpy.linalg.svd`, and reports rank, `chi_eff`,
and the spectrum.

## Measured result (central cut c = H/2, exact integer counts)

| H  | frontier N | exact rank | chi(1e-3) | chi(1e-6) | chi(1e-9) | MPS H·chi²(1e-6) | N / MPS |
|----|-----------:|-----------:|----------:|----------:|----------:|-----------------:|--------:|
| 8  |      1,604 |         21 |        13 |        21 |        21 |            3,528 |    0.45 |
| 10 |     11,005 |         51 |        20 |        50 |        51 |           25,000 |    0.44 |
| 12 |     68,343 |        127 |        42 |       122 |       127 |          178,608 |    0.38 |
| 14 |    161,357 |        298 |        49 |       211 |       286 |          623,294 |    0.26 |

(H=14 dumped at a slightly budget-pruned plateau column, so its rank is a mild
under-count; the trend is unaffected.)

**Central-cut exact rank: 21 → 51 → 127 → 298**, a steady ×≈2.4 per +2 in H, i.e.
`chi ~ 2.4^(H/2) ~ 1.55^H` — exponential. `chi_eff(1e-6)` tracks the full rank.
The Schmidt spectrum decays only ~polynomially (at H=14 the 24th singular value
is still 7e-3·sigma_max; no gap). `N / (H·chi_eff^2)` *decreases* with H
(0.45 → 0.26): the MPS footprint already **exceeds** the explicit dictionary and
the gap widens.

## Verdict

**MPS/tensor-network compression of the frontier is NOT feasible. The
3^(H/2) wall is real.** The frontier is near-maximally (volume-law) entangled
across the boundary mid-cut: the bond dimension needed for an *exact* MPS grows
exponentially in H (~1.55^H), the singular values do not decay fast enough for
lossy truncation to help at any counting-relevant tolerance, and `H·chi²` is
already larger than the explicit `{signature -> count}` dictionary it would
replace. This is the physics one expects — the boundary partition encodes king-
graph connectivity that genuinely links the two halves — and it matches the
project's standing "the wall is real" note. No MPS follow-up is warranted.
