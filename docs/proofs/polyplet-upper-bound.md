# Upper bound on the polyplet growth constant λ

2026-07-11. There is currently NO published or project upper bound on
λ_polyplet (only lower: 6.475 multi-directed, 5.828 directed; estimate ~7.11).
This note: a clean crude bound, and the design + crux for a tight one.

## Crude rigorous bound: λ ≤ 5⁵/4⁴ = 3125/256 ≈ 12.2

Redelmeier-canonical-scan decision-tree count. Scan cells row-major (top→bottom,
left→right); grow the animal by an include/exclude decision on each cell that
enters the "untried" frontier.

- When a cell is **included**, only its king-neighbours *ahead* in scan order —
  `E, SW, S, SE` (**≤ 4**) — newly enter the frontier; the other four
  (`W, NW, N, NE`) are already behind. So building an n-cell animal considers
  (included + rejected) `≤ 5n` cells total.
- The animal is exactly *which* n of those ≤5n considered cells were included:
  `a(n) ≤ C(5n, n)`. Hence `λ ≤ lim C(5n,n)^{1/n} = 5⁵/4⁴ ≈ 12.2`. ∎

Rigorous, no machinery. With overlap accounting (many "ahead" neighbours are
already on the frontier ⇒ effective forward branching < 4) this improves toward
~9–10, but that is where the easy argument tops out — far from the true ~7.11.

**NB — the tempting "≤ 8" is FALSE.** Encoding by spanning-tree parent-direction
(≤8/cell ⇒ λ≤8) is not an injection: for ordinary polyominoes the same argument
would give λ≤4, but λ_poly ≈ 4.06 > 4. The parent-direction string doesn't
reconstruct the animal. No "≤ coordination number" freebie.

## Toward a tight bound (b): relaxed-connectivity cross-section transfer matrix

Mechanism (Klarner–Rivest "twig" family): bound a(n) by a *superset* counted by a
transfer matrix on column cross-sections, with connectivity **relaxed** so it
over-counts; the dominant eigenvalue is then `≥ λ` and decreases toward it as the
relaxation tightens.

What we can build cheaply, and why it's NOT yet a valid bound:
- Drop the connectivity ("no buried component") check from the strip engine
  (`strip_mu`/`tma stepColumnSquare8`) ⇒ count column-sequences that are only
  *king-compatible* consecutively (no global-connectivity enforcement). This
  over-counts connected animals — good. Call its height-H growth `ν_H`.
- **But `ν_H` is height-H-limited, so it is NOT an upper bound on λ.** It misses
  tall animals: e.g. `ν_1 = 1` (height-1 = horizontal bars only) ≪ λ. Height
  limitation under-counts, relaxation over-counts, and they don't cleanly cancel.

**The crux (the real work).** A valid λ upper bound needs a bounded cross-section
that does NOT cap the animal's extent — the Klarner–Rivest move: bound width `w`
classes with a two-variable (area, height) GF where the unbounded column-height
is controlled analytically, not by truncation. Porting that to king adjacency
(diagonal column coupling, corner seams) is the genuine research. The strip
kernels give the relaxed transfer operator for free; the missing piece is the
height-handling that makes the eigenvalue a plane bound rather than a strip one.

**Status:** crude λ ≤ 12.2 is a real, first-of-its-kind bound (bankable). The
tight version is open research — the dual of this session's μ_H lower-bound
ladder (μ_H ≤ λ from below; a relaxed cross-section ν_w ≥ λ from above would
bracket it). See results/strip-growth-lambda-bounds.md.

## PLAN: bound λ, simply then tightly

Common invariant: every ν produced must stay ABOVE the true growth (sanity: >
observed a(n)/a(n-1) ≈ 6.9, and > μ_13 = 6.306). A bound is VALID iff it counts a
superset of all polyplets. Refinements form a monotone decreasing sequence
ν ↘ λ.

### Stage 0 — crude counting (DONE, rigorous): λ ≤ 12.2
The `C(5n,n)` argument above. No machinery. Bankable now.

### Stage 1 — optimize the crude count (simple, valid, plateaus ~9–10)
Tighten the "≤4 forward cells per inclusion." Track a SMALL local frontier state
(the previous row's occupancy in a sliding window) in a transfer matrix, and
count include/exclude decisions weighted by the ACTUAL forward-branching that the
local state allows (many "ahead" king-neighbours are already on the frontier, so
add 0 new). Dominant eigenvalue at spectral-radius-1 = ν₁.
- **Valid because:** partial (windowed) frontier info can only OVER-estimate the
  available extensions ⇒ over-counts the Redelmeier growth paths ⇒ ν₁ ≥ λ.
- **Expected:** ν₁ ≈ 9–10 (perimeter is Θ(n), so this family plateaus there — it
  cannot reach ~7.11). Effort: small; reuses nothing exotic.
- **Lemma to pin:** "windowed branching ≥ true branching" (the validity core).

### Stage 2 — cross-section transfer matrix, unbounded height (tight, research)
The Klarner–Rivest twig move: bound width-`w` classes with a transfer matrix on
column cross-sections, RELAXING global connectivity to an over-count, and control
the UNBOUNDED column height analytically (two-variable area/height GF, kernel
method) rather than truncating — the truncation is exactly what made the strip
`ν_H` invalid above. Widen `w` ⇒ ν_w ↘ λ.
- **Reuses:** the `tma`/`strip_mu` king cross-section transfer kernels (frontier
  connectivity partition); the upper-bound version swaps exact connectivity for a
  bounded-rank relaxation and extracts the top eigenvalue.
- **King-specific crux (the real work):** the diagonal column coupling and
  corner seams in the relaxed connectivity, and the height-GF that keeps the
  cross-section bounded without capping extent. This is the piece NOT yet pinned
  — a valid finite construction for king adjacency has to be derived (port
  Klarner–Rivest / Barequet–Shalah, whose published work skips the king lattice).
- **Expected:** ν_w decreasing; realistically reaches ~7.5–8 at feasible widths
  (like the μ_H lower side plateaus below λ). A genuine bracket
  `6.5 ≲ λ ≲ 8`, tightening both ways with compute.

### Stage 3 — the paper story
`μ_H ≤ λ ≤ ν_w`, both from the SAME cross-section machinery (one relaxes toward
connectivity from a subset, one from a superset). First rigorous two-sided
bracket on the polyplet growth constant; upper side is novel to the literature.

### Honesty flags
- Stage 1's validity lemma is stated, not yet proven — pin it before quoting ν₁.
- Stage 2's valid finite construction for KING adjacency is the open crux; the
  plan is a roadmap, not a proof. Don't quote a Stage-2 number until the
  construction is derived and it clears the "> a(n) ratios" sanity gate.
