# Directed & multi-directed king animals — exact results, λ lower bounds

Date: 2026-07-10. Source: Axel Bacher, "Directed and multi-directed animals in
the king's lattice," arXiv:1301.1365 (v3, 2015). Facts below verified against
the paper + OEIS; the directed GF coefficients independently re-derived here.

## Directed king animals (exact)

- Count: `d(n) = 1, 4, 19, 96, 501, 2668, 14407, 78592, …` = OEIS **A047781**.
- GF: `D(t) = ¼·((1+t)/√(1−6t+t²) − 1)`.
- Growth constant: **exactly `3 + 2√2 ≈ 5.8284`** (singularities `t = 3 ± 2√2`;
  `√(1−6t+t²)` is the Schröder kernel).
- Half-animals (left width 0) = small Schröder **A001003** (1,1,3,11,45,197).
- Forward cone = upper half-plane five directions `{W, NW, N, NE, E}`; horizontal
  W/E count as forward. Source = leftmost-bottommost cell (canonical; a property
  of the animal, no source-choice double count). Counted up to translation.

**Independent re-derivation (this note):** `1/√(1−6t+t²) = Σ Pₙ(3) tⁿ`
(Legendre at 3) `= 1+3t+13t²+63t³+321t⁴+1683t⁵+…`; `×(1+t)`, `−1`, `÷4`
→ `t+4t²+19t³+96t⁴+501t⁵` = A047781. ✓

## Multi-directed king animals

- GF `M(t)` not D-finite. Two distinct singularities (don't conflate):
  - `ρ_B ≈ 0.16346` = pole of the *intermediate* series B, the root of
    `ρ³ − 7ρ² − 5ρ + 1 = 0` (Bacher Lemma 11). `1/ρ_B ≈ 6.118` — NOT the
    growth constant.
  - `ρ_M ≈ 0.15444` = radius of `M`, defined transcendentally by `B(ρ_M)=1`
    (Theorem 10); no algebraic minimal polynomial (B is a non-D-finite sum).
- Growth constant `μ = 1/ρ_M ≈ 6.4752` (Bacher Corollary 12). Determined
  **numerically**, not algebraically — carries that caveat as a rigorous bound.

## The payoff: rigorous lower bounds on the polyplet growth constant

`λ_polyplet ≈ 7.1` is only a heuristic (ratio) estimate; no closed form is known.
Directed ⊆ multi-directed ⊆ connected polyplets gives `μ_dir ≤ μ_multi ≤ λ`:

| bound | value | form | note |
|---|---|---|---|
| directed (lower) | 5.8284 | `3+2√2` (exact algebraic) | fully rigorous |
| **multi-directed (lower)** | **6.4752** | `1/ρ_M`, `B(ρ_M)=1` | tighter, but numerical |
| polyplet λ | ~7.11 | unknown | heuristic only |
| **Bui certificate (upper)** | **9.3153** | `20000/2147`, exact cert | fully rigorous |

These are the first *rigorous* statements we have about `λ_polyplet`. Together with
the **upper** bound they bracket it two-sided: **`5.8284 ≤ λ ≤ 9.3153`**, both sides
rigorous (the upper side machine-verified in exact rational arithmetic). The upper
bound is derived by a Bui-style finite-type convolution certificate — see
[../docs/proofs/polyplet-upper-bound.md](../docs/proofs/polyplet-upper-bound.md).

## Trilogy (context)

Half-animals are **Motzkin / Catalan / small-Schröder** on the **square /
triangular / king** lattices; directed growth **3 / 4 / 3+2√2**. Polyplets are
the Schröder corner. All three share `μⁿ n^(−1/2)` universality.

## Directed vs undirected: no reduction, only inequality

No known exact reduction or bijection undirected↔directed on any lattice (its
existence would solve the open undirected problem). The reason directed is
solvable is our own connectivity wall from the solvable side: **directedness
linearizes connectivity** — a forward cone imposes a layer order, collapsing the
global 2D connectivity constraint into local layer-to-layer compatibility (1D
transfer matrix / Viennot heaps of pieces / Dhar hard-particle gas → algebraic
GF). Undirected animals have no such order; connectivity stays 2D-hard; GF not
D-finite. Directedness *is* discarding the hard part. See
[[algorithmic-levers-dead-connectivity-wall]].

## Validation hook — BUILT 2026-07-31: [directed-cone-anchor.md](directed-cone-anchor.md)

Directedness is a local O(cells) property: bottom-up forward-reachability from
the leftmost-bottommost cell in cone `{W,NW,N,NE,E}`. Filtering the fixed-polyplet
enumerator by it must reproduce A047781 — an independent **closed-form** anchor
(checkable to any n, unlike the strip-TM and g2 enumeration second-sources).
Gotcha: the bottom row must be a single contiguous run; disjoint bottom runs that
link only higher up are *multi*-directed (A-not-yet-in-OEIS), not directed.

**Done.** Enumerate+filter = A047781 for n ≤ 15, direct cone growth for n ≤ 17,
zero mismatches against the closed form; RED controls (4-step cone → A055834,
diverging 18 vs 19 at n=3; bottom-row rule waived → 20 vs 19 at n=3) confirm the
filter discriminates. The bottom-row gotcha turns out to be a *consequence* of
the cone, not an extra rule. Tools `cpp/directed_cone_anchor.cpp` +
`experiments/directed_cone_anchor.py`.
