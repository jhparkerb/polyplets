# The matching-pair convention, pinned — and idea 2 had it backwards

2026-08-07, gympie. Step 0 of idea 2 of `results/unexplored-avenues.md`
(polyominoes and polyplets as a percolation matching pair). The plan singles
out one convention detail as deciding whether the whole idea works —

> "in each matching identity each cluster's boundary is measured in the *other*
> lattice — a polyomino's perimeter w.r.t. the king neighbourhood, a polyplet's
> w.r.t. the rook neighbourhood. **Get this wrong and nothing will check out.**"

— so it was worth measuring before building anything on it.

**It is wrong. The perimeter is same-lattice. What crosses is the
CONNECTIVITY, not the perimeter.** The good news is that this makes the plan's
"testable today, before any new compute" claim *more* true than it thought: the
repo's existing `--siteperim` data is already in the correct convention.

## What was measured

Every one of the 65535 non-empty subsets of a 4x4 box, checking the two Euler
identities the matching pair rests on
(`experiments/matching_pair_euler.py`):

```
box 4x4: 65535 non-empty subsets

  C_4(S) - H_8(S) == V - E_4 + Q       : 65535/65535 ALL HOLD
  C_8(S) - H_4(S) == V - E_8 + T - Q   : 65535/65535 ALL HOLD

  cross-pairings (what the plan's convention would need):
    C_4 - H_4 == V - E_4 + Q      : 57144/65535
    C_8 - H_8 == V - E_8 + T - Q  : 57144/65535
```

`V = |S|`, `E_4`/`E_8` = adjacent pairs under rook/king, `Q` = 2x2 blocks
wholly inside `S`, `T` = king 3-cliques, `C_a` = a-connected components of `S`,
`H_a` = *bounded* a-components of the complement.

The matched pairings hold universally; the cross-pairings fail on 8391 subsets,
12.8% of the census. The pairing is **foreground a-connectivity against
background (matching-a)-connectivity**.

## Why the perimeter is same-lattice

Once the pairing above is pinned the rest is one line. A set `C` of occupied
sites is a *maximal* a-connected cluster exactly when every site a-adjacent to
`C` is vacant. So its weight in the cluster generating function is

```
p^|C| q^(t_a(C)),     t_a = the a-site-perimeter, SAME lattice
```

There is no route by which the other lattice's perimeter enters a single
cluster's weight. What is cross-lattice is which *pair* of series get related:
occupied-king clusters against vacant-rook clusters. The plan almost certainly
collapsed those two facts into one.

**The repo was already right.** `cpp/g2_redelmeier.cpp --siteperim` computes
"the number of distinct EMPTY king-(8-)adjacent cells of the animal — the
percolation perimeter for the king/nnSquare lattice", cross-checked against
Mertens 1990 Table IVB. King animals, king perimeter. Nothing needs recomputing
on the polyplet side.

## The inhomogeneous term, derived

Both Euler expressions are *local*, which is what makes the matching relation's
inhomogeneous term a polynomial rather than a series. Per site of `Z^2` there
are 2 rook edge-classes, 4 king edge-classes, 1 2x2 block, and 4 king triangles
(three mutually king-adjacent cells must lie in a 2x2 box, which holds
`C(4,3) = 4` of them, and a triangle determines its box uniquely). Taking
densities:

```
chi_4 density = p - 2p^2 + p^4
chi_8 density = p - 4p^2 + 4p^3 - p^4
```

Both vanish at `p = 1` (the full plane is one component with no holes, so zero
per site) and both go to `p` as `p -> 0` (isolated cells, each of Euler
characteristic 1). Since `chi_8 = (king clusters) - (bounded rook components of
the vacant set)` per site, and the unbounded vacant component contributes zero
density:

```
K_8(p) - K_4(1-p) = p - 4p^2 + 4p^3 - p^4
```

with `K_a(x)` the mean number of a-clusters per site at occupation density `x`.
That is the Sykes-Essam relation for this matching pair, in the convention just
pinned.

## The next step, and the obstacle it hits

Testing that relation against banked data means expanding both sides in `p`:

```
K_8(p)    = sum over king animals  g_{n,t} p^n (1-p)^t
K_4(1-p)  = sum over rook animals  g_{n,t} (1-p)^n p^t
```

The two sides are **graded by different quantities**. The king side is graded
by size `n`, which is what every enumeration in this repo produces. The rook
side contributes `p^t`, so getting it right to order `p^N` needs every rook
animal of site-perimeter `t <= N` at *unbounded* size — a finite set for each
`N` (site-perimeter `t` bounds the size by `O(t^2)`), but graded by perimeter,
which is not how anything here is enumerated.

That is the real cost of idea 2, and the plan does not mention it. It is not
"no new compute": it is a perimeter-graded enumeration on the polyomino side.

## Honest limits

- 4x4 exhaustive is a small box. The identities being checked are *exact and
  local*, so a universal pass over all 65535 subsets is strong evidence for a
  local formula rather than a sample — but it is not a proof, and the step from
  the exact identity to the *density* form assumes translation invariance with
  no boundary.
- The relation as written needs care at and above `p_c`, where an infinite
  cluster exists and the "bounded components" bookkeeping changes. Nothing here
  addresses that.
- **Novelty: none, and none is claimed.** The two Euler formulas are standard
  digital topology and the Sykes-Essam relation is 1964. What is new here is
  only that the repo's convention was checked rather than assumed.
- **Sentence that gets shorter: still none**, exactly as idea 2 itself says.
  This step cost twenty minutes and removes a wrong premise; it does not make
  the rest of idea 2 cheap.

## Artifacts

- `experiments/matching_pair_euler.py` — the probe, runs in ~3 min on 4x4
