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
