# Lean formalization status — `T(n, n-k)` diagonal closed forms

Formalizing the diagonal closed forms for fixed polyplets (A006770) in Lean 4 +
mathlib. Branch `lean-diagonal-proofs`. Paper proofs live in
`docs/proofs/T-n-nm1.md` (k=1) and `docs/proofs/T-n-nm2-and-general.md` (k=2 +
general sketch).

Build: `cd polyplets && lake build`. Green = only the intended `sorry`s below.

## Definitions (`Polyplets/Defs.lean`) — DONE

- `kingAdj`, `KingConnected` (path via `Relation.ReflTransGen` staying in the set).
- `IsCanonical n H S`: `n` cells, king-connected, origin-anchored
  (`min x = min y = 0`), `max y = H-1`.
- `T n H := {S | IsCanonical n H S}.ncard`.
- Validated by `Sanity.lean`: `T 1 1 = 1` (fully proved).

## Target theorems (`Polyplets/Diagonal.lean`)

- `T_n_nm1`: `T n (n-1) = (25n-45)·3^(n-4)` over ℚ.
  The ℚ/`zpow` bridge is **proved**; the ℕ-count `hcount` is `sorry` — its goal
  is now a concrete `Finset.card` (via `T_eq_toFinset_card`), reduced to the
  offset-chain count (step (e) below).
- `T_n_nm2`: `T n (n-2) = ½(625n²-2459n+1134)·3^(n-7)` — full `sorry`.

## Infrastructure proved (all sorry-free)

### `Polyplets/Finite.lean` — step (a)
- `exists_proj_eq_of_cross` — king paths don't skip a 1-Lipschitz coordinate
  value; `exists_x_eq_of_cross` / `exists_y_eq_of_cross` specializations.
- `exists_adj_cross_of_reflTransGen` — returns the whole boundary-crossing edge.
- `canonical_x_le` — uniform width bound `p.1 ≤ n-1`.
- `canonical_finite` — the canonical family is finite (⊆ powerset of the box).
- `T_eq_toFinset_card` — `T` is a genuine `Finset.card`.

### `Polyplets/RowProfile.lean` — steps (b), (c-fwd), (d-prep)
- `canonical_row_occupied`, `canonical_rows_image`, `canonical_rows_card` — the
  occupied rows are exactly `[0,H-1]`, count `H`.
- `canonical_card_eq_row_sum`, `canonical_fiber_nonempty` — fiberwise cell count.
- `exists_unique_of_sum_eq_one` — ℕ sum = 1 ⇒ unique nonzero term.
- `row_profile_one_doubled` — **(b)**: for `H=n-1`, exactly one row is doubled,
  the rest singletons.
- `canonical_consecutive_rows_linked` — **(c) forward**: connectivity ⇒ each
  consecutive occupied row pair is directly king-linked.
- `row_profile_doubled_cells` — **(d)/(e) prep**: the doubled row's two cells as
  an ordered pair `c1.1 < c2.1`, the only cells on that row.
- `neighbor_off_row_of_gap` — **(d) local**: gap ≥ 2 ⇒ a doubled cell's
  neighbours are off-row (in `y0 ± 1`).

## Remaining work (hard)

1. **(c) reverse** — per-row links ⇒ `KingConnected`. Needed to *construct*
   canonical sets in the (e) bijection. Requires assembling a path from the
   consecutive-row links (all rows occupied).
2. **(d) gap ≤ 2 disconnection** — `docs/proofs/T-n-nm1.md` §3. `neighbor_off_row_of_gap`
   gives the local confinement; the global step is: if gap ≥ 3, the up-chain
   (rows > y0) and down-chain (rows < y0) each reach row y0 only through one of
   the two doubled cells (a king step can't jump from row y0+1 to y0-1), and with
   gap ≥ 3 no single neighbour bridges both ⇒ two components. Needs the
   up/down-chain connectivity structure + a cut/component argument.
3. **(e) offset-chain count** — `docs/proofs/T-n-nm1.md` §4-5. The big one: a
   bijection from canonical sets to (doubled-row position × gap × free 3-chain of
   inter-row offsets) with the gadget multiplicities (16, 9, 4, 1), giving
   `(16+9)(n-3)·3^(n-4) + (4+1)·2·3·3^(n-4) = (25n-45)·3^(n-4)`. This is what
   closes `hcount`.

`T_n_nm2` (k=2) reuses the same architecture with a two-defect row profile
(one triple row or two doubled rows).
