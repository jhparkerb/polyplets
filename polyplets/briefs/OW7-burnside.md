# OW-7 "Eightfold Count" — `Polyplets/Symmetry.lean`: the Burnside apparatus

Read first: `polyplets/OUTWORKS-PLAN.md`; `Polyplets/Sequence.lean` (OW-1,
PREREQUISITE — consumes `IsCanonicalAnimal`, `a`, `canonicalAnimal_finite`);
paper §7 (read-only) for the identity set; `scripts/derive_related.py`
(the combiner these identities mirror). Mathlib ingredient (verified in
the pinned tree): Burnside's lemma is
`MulAction.sum_card_fixedBy_eq_card_orbits_mul_card_group`
(`Mathlib/GroupTheory/GroupAction/Quotient.lean:270`,
hypotheses `[Fintype α] [∀ a, Fintype (fixedBy β a)]` — plan for `Fintype`
bridges from the ncard world). Size M.

Everything §7 publishes (five OEIS companion sequences) rests on:

```
Free      = (Fixed + 2·R90 + R180 + 2·H + 2·D) / 8      (A030222)
OneSided  = (Fixed + 2·R90 + R180) / 4                   (A030233)
Bilateral = (H + D) / 2                                  (A030234)
```

plus `R90 = 0` unless n ≡ 0, 1 (mod 4), and the /8, /4, /2 integralities.
None of it is formalized; the mathematical content is finite group theory.

## The action (design pinned)

D₄ as the 8 linear maps of `ℤ × ℤ` (explicit: id, three rotations, four
reflections — an inductive `D4` with a `toFun : D4 → ℤ × ℤ → ℤ × ℤ`, group
structure by `decide`-friendly case tables, or `Equiv.Perm`-style;
hand-rolled 8-element group + `Group D4` instance is the least friction —
multiplication table by `decide` after `Fintype D4`).

Action on canonical animals: apply the point map, then re-anchor:

```lean
def reanchor (S : Finset (ℤ × ℤ)) : Finset (ℤ × ℤ) := …  -- min x = min y = 0
instance : MulAction D4 {S : Finset (ℤ × ℤ) // IsCanonicalAnimal n S} where
  smul g S := ⟨reanchor (S.val.image g.toFun), …⟩
```

Action laws: `reanchor (image g (reanchor T)) = reanchor (image g T)` —
image-of-translate = translate-of-image, and reanchor kills translations;
prove the translation toolkit once (share with OW-2's needs if it lands
first — check `Growth.lean` for `reanchorY` and generalize rather than
duplicate). `IsCanonicalAnimal` is preserved: card and connectivity under
a lattice isometry (kingAdj is D₄-invariant: `|Δx|, |Δy| ≤ 1` symmetric
under swap/negate — `omega`/`decide` per generator).

`Fintype` on the subtype: from `canonicalAnimal_finite` via
`Set.Finite.fintype` (noncomputable instance is fine — Burnside is a
cardinality statement, not a computation).

## Deliverables

```lean
noncomputable def R90 (n : ℕ) : ℕ := …   -- card of fixedBy (rot 90)
noncomputable def R180 (n : ℕ) : ℕ := …
noncomputable def Hm (n : ℕ) : ℕ := …    -- horizontal-axis mirror
noncomputable def Dm (n : ℕ) : ℕ := …    -- diagonal mirror
noncomputable def Free (n : ℕ) : ℕ := …      -- D₄-orbit count
noncomputable def OneSided (n : ℕ) : ℕ := …  -- C₄-orbit count (rotation subgroup)
noncomputable def Bilateral (n : ℕ) : ℕ := … -- orbits containing a mirror-fixed rep

theorem free_eq (n : ℕ) (hn : 1 ≤ n) :
    8 * Free n = a n + 2 * R90 n + R180 n + 2 * Hm n + 2 * Dm n
theorem oneSided_eq (n : ℕ) (hn : 1 ≤ n) :
    4 * OneSided n = a n + 2 * R90 n + R180 n
theorem bilateral_eq (n : ℕ) (hn : 1 ≤ n) :
    2 * Bilateral n = Hm n + Dm n
theorem r90_vanish (n : ℕ) (h : ¬ (n % 4 = 0 ∨ n % 4 = 1)) : R90 n = 0
-- integrality corollaries are the equations themselves (LHS = 8·ℕ etc.)
```

## Proof routes

1. **`free_eq` / `oneSided_eq`** — Burnside over D₄ resp. its rotation
   subgroup. The 8 fixed-point counts collapse:
   - `fixedBy g = fixedBy g⁻¹` as SETS (g•S = S ↔ g⁻¹•S = S) — handles
     rot90/rot270.
   - h-mirror vs v-mirror and d-mirror vs anti-d-mirror: EQUINUMEROUS via
     conjugation — `S ↦ r90 • S` is a bijection `fixedBy h ≃ fixedBy v`
     (fixedBy of conjugate elements; Mathlib may have
     `MulAction.fixedBy_conjugate`-style lemmas — grep; else 5 lines).
   - identity: `fixedBy 1 = everything`, card = `a n` (the subtype card
     equals the set ncard — bridge lemma).
2. **`bilateral_eq`** — double count `Σ_{g reflection} |fixedBy g| =
   2·Hm + 2·Dm` against the orbit stratification. Per orbit O with
   stabilizer conjugacy class St (constant along O): contribution
   `|O| · |St ∩ reflections| = (8 / |St|) · r`. Case-enumerate the
   subgroups of D₄ containing a reflection (by `decide` on the 8-element
   group): every case with r ≥ 1 gives `(8/|St|)·r = 4`. Hence
   Σ = 4·#(orbits with a reflection-fixed member) = 4·Bilateral.
   Mathlib pieces: orbit-stabilizer
   (`MulAction.card_orbit_mul_card_stabilizer_eq_card_group`), stabilizers
   along an orbit are conjugate (`MulAction.stabilizer_smul_eq_stabilizer_map_conj`).
   This is the fiddliest deliverable — do it LAST.
3. **`r90_vanish`** — fully algebraic, no case split on rotation centres:
   if `rot90 • S = S` then `ρS = S + t` for some translation t (unfold
   reanchor). Define the affine map `σ p := ρ p + t` on ℤ²; then
   `σ(S) = S` and — the key, purely linear fact —
   `σ⁴ = id` (because `ρ⁴ = id` and `(ρ³ + ρ² + ρ + 1) t = 0` since
   `ρ² = −1` for the quarter turn: `ρ³+ρ²+ρ+1 = (ρ+1)(ρ²+1) = 0`).
   ⟨σ⟩-orbits on S have card ∈ {1, 2, 4}; card-1 means σp = p —
   `(1 − ρ)` is injective on ℤ² (det = 2 ≠ 0) so AT MOST ONE fixed point;
   card-2 means σ²p = p, σp ≠ p — but `σ²q = ρ²q + (ρt + t) = −q + c`
   has at most one solution (`2q = c`), and a 2-orbit would need two
   distinct σ²-fixed points: none. So n = 4·(#4-orbits) + (0 or 1) ⇒
   n mod 4 ∈ {0, 1}. Formalize the orbit partition concretely (partition
   S by the σ-orbit as a Finset quotient, or induct: repeatedly remove a
   full orbit) — pick whichever you can drive; the removal induction on
   `S.card` is probably least machinery.
4. **Anchors** (native_decide, values verified against
   `results/sym_counts.txt` and `results/related-seqs-n24.md`): computable
   twins via `Compute.lean`'s pattern (filter the box enumeration by the
   fixedness predicate — `Tc`-style; decidable since everything is finite):
   `R90: 1↦1, 4↦2, 5↦2 (2,3 ↦ 0)`; `R180: 1..6 ↦ 1,4,4,22,22,132`;
   `Hm: 1..6 ↦ 1,2,4,10,22,58`; `Dm: 1..6 ↦ 1,2,4,10,22,56`;
   derived spot checks (via the equations + `a` anchors):
   `Free 4 = 22`, `OneSided 4 = 34`, `Bilateral 4 = 10`.

## Notes

- Keep every count `noncomputable def` + computable twin + equality
  lemma, mirroring the `T`/`Tc` house pattern.
- The mirror conventions must match the engine's (h-mirror = y-negation
  = axis-parallel, d-mirror = swap): pin them to match
  `results/sym_counts.txt`'s meanings (r90/r180/hmirror/dmirror) and say
  so in docstrings; the anchor values will catch a convention slip.
- Orbit counting: `MulAction.orbitRel.Quotient`; card via the Fintype on
  the quotient (decidable eq on Finsets is fine).

## Done criteria

`lake build` green, no `sorry`; `#print axioms free_eq / bilateral_eq /
r90_vanish` = standard three (guarded); anchors carry `Lean.ofReduceBool`
exactly. Commit `lean-ow: Symmetry — Burnside identities, R90 vanishing,
bilateral half-sum`.
