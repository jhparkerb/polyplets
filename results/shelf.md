# Shelved ideas (deliberately not pursued yet)

## Formal (Lean) verification of the counts
A stray idea worth keeping: instead of *computing* a(19), write a *verifiable
checker* that *confirms* a count — the SAT/DRAT paradigm applied to enumeration.

The honest landscape (from the 2026-06-18 discussion):
- **No compact witness for a bare count.** The natural certificate is the
  transfer-matrix DP table itself: `(boundary_state, n) -> count`. A verified
  checker confirms every entry satisfies its one-step recurrence from trusted
  local transition rules, the base cases, and the final sum. Checking is linear
  in table size; the trusted core shrinks to (a) transition rules match the
  king-polyplet definition, (b) bignum arithmetic. This is DRAT-for-DP.
- **Can't run a(19) in Lean's kernel** (1.5e14 ops); extracted verified code
  still pays full multi-day runtime.

Three escalating targets:
1. **Lean-verify the small-height transfer matrices + recurrences** (H <= ~5-6).
   Bounded, weeks not months. a(19) = sum over heights; this formally certifies
   the easy slices and the machinery. *Best near-term artifact for the paper.*
2. **Lean-verify the DP-table checker** (DRAT analog). Certify whatever table you
   can afford to produce.
3. **Lean-prove the Redelmeier bijection** ("each translation class visited
   exactly once"). Deepest; certifies the workhorse. Months.

Status: SHELVED at user's request 2026-06-18. Pick up at target #1 if revisited.

### Lean-verifying the fixed-height GFs (2026-06-18, now that we HAVE them)
A GF is a far better Lean target than a bare count: "G_H(x)=P_H(x)/Q_H(x)" is a
closed-form forall-n claim with real structure, not an opaque number. Sketch:
1. Define B_H(n) via the column transfer matrix T_H (concrete finite integer
   matrix over boundary states); B_H(n) = u^T T_H^n v.
2. Cayley-Hamilton (in Mathlib: `aeval M (charpoly M) = 0`) => B_H satisfies the
   linear recurrence whose coefficients are charpoly(T_H). Denominator ~ free.
   Numerator from finitely many initial conditions. Mathlib also has
   LinearRecurrence / PowerSeries / RatFunc.

Feasible shape:
- **General theorem (all H):** "fixed-height rows are C-finite, recurrence =
  charpoly of the transfer matrix." Elegant; covers H=8 structurally WITHOUT
  computing anything large (specific Q_8 = charpoly of the explicit matrix,
  computed/trusted outside Lean).
- **Specific GFs in-kernel:** only H<=4 (maybe 5 via native_decide). H>=6 hits a
  wall -- charpoly of a ~D_H x D_H matrix (D_8=1604, coeffs ~1e55) is ~n^4 and
  far past kernel reduction.

*** BIG ASTERISK (jasonp, 2026-06-18) ***: feasibility here is about the MATH being
tractable, NOT about it being a small job. Actually doing it is a major
undertaking. The real cost is the definitional bijection -- formalizing "fixed
polyplet of height H" and PROVING the transfer matrix counts it (the
"definitions are the hard part" lesson, [[shelf]] reading below). That's
months-scale Lean work by someone fluent in Mathlib, and it's the bulk of the
effort; the Cayley-Hamilton step is the easy 10%. Do not enter lightly.

## Counting tiling polyplets (within a(n))
Do polyplets that aren't polyominoes tile the plane? Yes, infinitely many: any
*purely diagonal* polyplet is a polyomino in disguise (the 45-deg sublattice map
sends king-diagonal adjacency to rook adjacency) and tiles iff its parent does;
the diamond (plus minus centre) is the 2x2 square in disguise. Figure:
results/diag_domino_tiling.png (the corner-joined domino tiling by translation).

The richer open question: a *genuinely two-coloured* polyplet (spans both colour
classes, so really uses corner adjacency) carrying a 4-hole, that tiles only with
rotation/reflection -- a copy snaking a cell into the hole through the diagonal
pinch. Corner adjacency is exactly what makes holey tiles pluggable (a polyomino
can't: a lone cell reaching a rook-enclosed hole through a diagonal would be
disconnected). Almost certainly uncatalogued.

Feasibility of counting tiling polyplets in a(19) (2026-06-18 analysis):
- Scope to DECIDABLE classes: translation-only (Beauquier-Nivat, O(perimeter))
  and isohedral (Conway criterion, O(perimeter^2) naive / quasilinear hard).
  "All tilers" (incl. anisohedral) has no known efficient single-tile test.
- Generation floor: ~10 ns/tile/core (measured at a(19), 80-way, hours).
- **Translation tilers in a(19): ~6-7 days at 80-way** (linear BN test riding on
  generation). Feasible; the natural deliverable. Conway type gives the
  translation-only vs rotation-required split for free.
- **Full isohedral in a(19): NOT head-on** (~1+ yr from the perimeter^2 factor);
  needs O(p) prefilter + quasilinear (Langerman-Winslow) to reach weeks, or stop
  at n<=~16-17. Holey tilers fall back to bounded patch search (small subset).
- Lever, as always, is algorithm choice; perimeter^2 in Conway is the gate.

### Relevant reading
- Ilin & Nugent, "Sorries Are Not the Hard Part: An Expert-Review Case Study of
  a Semi-Autonomous Formalization," arXiv:2606.13925. Thesis: getting a Lean
  proof to compile (no `sorry`) is easy; the hard part is choosing definitions
  and designing reusable APIs that survive expert review. "Agents adapt well to
  local, mechanically-checkable feedback but are weak at choosing definitions
  and designing APIs." Direct lesson for us: in any polyplet formalization the
  value and the difficulty live in `def Polyplet` / `def hole` / the transfer-
  matrix API, NOT in closing the count. Keep definitional choices human-gated.
  Live precedent: the 2026-06-18 hole-convention decision (4-bg vs 8-bg) was
  exactly a "definition choice" that mechanical checks could not settle.
