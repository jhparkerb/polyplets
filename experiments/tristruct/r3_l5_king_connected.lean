/- R3 L5: definition-level formalisation of T(n,H).

   T(n,H) = number of king-connected n-cell subsets of Z^2 with bounding-box
   height exactly H, counted up to translation.

   Encoding of "up to translation": normalize min-x = 0, min-y = 0. Height
   exactly H then means: all cells have y < H and some cell has y = H-1.
   A king-connected set of n cells has width <= n (a king path from a min-x
   cell to a max-x cell changes x by at most 1 per step, so every column
   between the extremes is occupied), so the domain [0,n) x [0,H) loses
   nothing. Hence

     T(n,H) = #{ s in powersetCard n (range n x range H) :
                 s touches column 0, s touches row 0, s touches row H-1,
                 and the king graph induced on s is connected }.

   Connectivity is STATED, not implemented: (kingGraph s).Connected is
   Mathlib's SimpleGraph.Connected, and its decision procedure is Mathlib's
   generic decidable-reachability instance for finite graphs
   (Mathlib/Combinatorics/SimpleGraph/Connectivity/Finite.lean:56-65),
   written and verified by the Mathlib community. Nothing in this file
   implements a connectivity algorithm, a frontier, or component labels.

   Run:  cd polyplets && ~/.elan/bin/lake env lean <this file>
-/
import Mathlib

namespace R3L5

abbrev Cell := ℕ × ℕ

/-- King (Chebyshev-distance-1) adjacency on cells. -/
def kingAdj (p q : Cell) : Prop :=
  p ≠ q ∧ p.1 ≤ q.1 + 1 ∧ q.1 ≤ p.1 + 1 ∧ p.2 ≤ q.2 + 1 ∧ q.2 ≤ p.2 + 1

instance (p q : Cell) : Decidable (kingAdj p q) := by
  unfold kingAdj; infer_instance

/-- The king graph induced on a finite cell set `s`. -/
def kingGraph (s : Finset Cell) : SimpleGraph {x // x ∈ s} where
  Adj a b := kingAdj a.1 b.1
  symm := ⟨fun _ _ h => ⟨h.1.symm, h.2.2.1, h.2.1, h.2.2.2.2, h.2.2.2.1⟩⟩
  loopless := ⟨fun _ h => h.1 rfl⟩

instance (s : Finset Cell) : DecidableRel (kingGraph s).Adj :=
  fun a b => inferInstanceAs (Decidable (kingAdj a.1 b.1))

/-- Normalized king animal of height exactly H inside its domain box:
    touches column 0 (min-x = 0), row 0 (min-y = 0), row H-1 (height H),
    and is king-connected. Cardinality and the box bounds are enforced by
    the domain in `T` below. -/
def isAnimal (H : ℕ) (s : Finset Cell) : Prop :=
  (∃ p ∈ s, p.1 = 0) ∧ (∃ p ∈ s, p.2 = 0) ∧ (∃ p ∈ s, p.2 = H - 1) ∧
  (kingGraph s).Connected

instance (H : ℕ) : DecidablePred (isAnimal H) := fun s => by
  unfold isAnimal; infer_instance

/-- The triangle cell T(n,H), by definition. -/
def T (n H : ℕ) : ℕ :=
  ((((Finset.range n) ×ˢ (Finset.range H)).powersetCard n).filter
    (isAnimal H)).card

/- Evaluation table with per-cell wall time, compared by hand against the
   banked triangle (experiments/tristruct/triangle.py). -/
#eval show IO Unit from do
  let banked : List (ℕ × ℕ × ℕ) :=
    [(1,1,1),
     (2,1,1),(2,2,3),
     (3,1,1),(3,2,10),(3,3,9),
     (4,1,1),(4,2,27),(4,3,55),(4,4,27),
     (5,1,1),(5,2,68),(5,3,248),(5,4,240),(5,5,81),
     (6,1,1),(6,2,167),(6,3,996),(6,4,1480),(6,5,945),(6,6,243),
     (7,2,406),(7,3,3775)]
  let mut bad := 0
  for (n, H, want) in banked do
    let t0 ← IO.monoMsNow
    let v := T n H
    let ok := v == want          -- scrutinized below, forcing v before t1
    if !ok then bad := bad + 1
    let t1 ← IO.monoMsNow
    IO.println s!"T({n},{H}) = {v}  banked {want}  {if ok then "OK" else "MISMATCH"}  [{t1-t0} ms]"
  if bad == 0 then
    IO.println "ALL BANKED VALUES REPRODUCED"
  else
    IO.println s!"{bad} MISMATCHES"

/- Theorem pins by `native_decide` (compiled evaluation; adds the compiler
   to the trusted base — the leaf standard this project already uses).
   Kernel `decide` was tried on `T 2 2 = 3` and abandoned at 15 CPU-min /
   5.8 GB: Mathlib's connectivity instance routes through Quotient.fintype
   machinery the kernel cannot reduce at any useful size. -/

example : T 2 2 = 3 := by native_decide

example : T 6 4 = 1480 := by native_decide

end R3L5
