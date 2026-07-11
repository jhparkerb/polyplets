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

### Stage 1 — optimize the crude count: NO simple valid improvement (checked 2026-07-11)
Attempted: encode each animal by its Redelmeier growth TREE (each cell has ≤4
forward king-neighbours ⇒ ≤4-ary tree, n nodes) ⇒ `λ ≤ 4⁴/3³ = 256/27 ≈ 9.48`.
**INVALID.** Rook sanity check kills it: the same argument gives ordinary
polyominoes `λ_poly ≤ 4`, but `λ_poly ≈ 4.06 > 4`. The growth tree is a SPANNING
tree — it drops the animal's cycles, so animal→tree is NOT injective and
`a(n) ≤ #trees` does not follow. Only the full decision SEQUENCE (records the
exclude decisions on already-adjacent cells = the cycles) is injective, and that
IS the `C(5n,n)` count → 12.2. So 12.2 is the clean crude ceiling; the tree
shortcut is a mirage.

The would-be fix — a transfer matrix on the generation QUEUE state — fails
because that state is unbounded (queue length ∝ perimeter ∝ n). So there is NO
simple finite-state valid bound between 12.2 and the real method. Stage 1
collapses into Stage 2: the unbounded dimension is exactly what Klarner–Rivest's
functional-equation trick exists to handle. (Lesson banked; sanity-check every
candidate bound against the rook analog before quoting it.)

### Method (corrected 2026-07-11 from the KR/Barequet-Shalah/Bui literature)
NOT a column cross-section transfer matrix (my earlier guess). The real method is
the **twig / BFS-spanning-tree encoding**:
- Encode each animal by a canonical BFS from its corner cell → a unique sequence
  of local "twigs" (the occupancy pattern of the newly-exposed neighbours at each
  discovery step) from a finite alphabet. animal → sequence is INJECTIVE; not
  every formal sequence is a valid animal ⇒ counting all formal sequences
  over-counts. Unbounded size is handled by a geometric series (algebraic GF),
  and the bound is the **diagonal of a 2-variable rational GF** `x/(1 − y·A(x))`
  where `A(x)` sums the twig-alphabet weights.
- **Eden level (= our Stage 0, now explained):** alphabet = all occupancy
  patterns of the `K` newly-exposed neighbours ⇒ `A(x)=(1+x)^K`, diagonal
  `~ C(Kn,n)` ⇒ `λ ≤ K^K/(K−1)^{K−1}`. Rook `K=3 → 6.75`; **king `K=5 → 12.2`**
  — identical to our `C(5n,n)`. Good cross-check.

### Stage 2 — tighten via context (the real work), TWO templates
Both reduce the effective alphabet by exploiting that king diagonal coupling
already DETERMINES some newly-exposed neighbours from earlier BFS steps, so fewer
free bits per twig ⇒ smaller `A(x)` ⇒ smaller diagonal growth ⇒ tighter bound.

- **(A) Klarner–Rivest "L-context" + cut hierarchy.** Reduces rook 6.75 → 4.83 →
  (cut C_10) 4.65; Barequet–Shalah pushed to C_21 → 4.5252. Bound via the
  discriminant/Sylvester determinant of the GF denominator. Heavy (millions–
  trillions of twigs), computer search.
- **(B) Bui's convolution-certificate method (RECOMMENDED port, arXiv:2510.06806).**
  A small system of convolution GF inequalities over a handful of local
  forbidden/free neighbourhood shapes ⇒ a single algebraic **kernel equation**;
  the bound is proved by exhibiting a positive rational certificate satisfying the
  inequality system — verifiable by ARITHMETIC, no residue calculus, no
  high-degree root-finding. Polyiamond example: `z/x = 1+z+z²+z³` ⇒ root of
  `2z³+z²−1` ⇒ `λ_T = 1+2z+3z² ≤ 3.6108`. Explicitly designed to be
  lattice-agnostic ("applies elsewhere").

**The load-bearing crux (NOT yet derived — do carefully, sanity-gate it):** the
king-adjacency version of the "which neighbours are already determined at each BFS
step" geometric lemma. King BFS discovers a cell whose already-visited context
includes cells diagonal to *two* earlier cells — so the context window is a
`3×3`-minus-centre-ish shape, not the rook L-tromino. Getting this case analysis
right is the whole game (and where the Stage-1 tree bound went wrong). Derive the
king twig alphabet / Bui neighbourhood shapes from it, write the king kernel
equation, extract the bound. **Do NOT quote a number until it clears the rook
sanity gate AND stays above our a(n) ratios (~6.9) and μ_13=6.306.**

**Expected:** each context refinement drops the bound below 12.2 toward λ;
realistically lands ~8–9 for modest context, tighter with the cut hierarchy /
larger certificates (dalby-scale for the big ones). Gap vs the published
polyhex/king absence: there is NO published king or polyhex upper bound, so any
result here is novel.

### Machinery status (2026-07-11) — VALIDATED, king derivation is the only gap
The extraction pipeline is built and validated on two lattices:
- `experiments/kernel_bound.py`, `kernel_system.py` — single-kernel & full-system
  singularity extraction; reproduce polyiamond `λ_T ≤ 3.6108`.
- `experiments/certificate_bound.py` — Bui's monotone-iteration finder AND exact
  rational certificate checker; reproduce the rook 6-type `λ₂ ≤ 4.63` (finder
  4.6287; Bui's certificate x=100/463 verified exactly). **This is the tool to
  reuse for king** — swap in the king twig system, run the finder, then harden to
  an exact rational certificate.

**The ONE remaining step — the king twig system** (careful; no published number
to check against, so validity is on us):
1. King BFS closure lemma: which of the 8 neighbours are already-determined at a
   discovery step (rook's is "left + 3-below" = the L; king's is larger, includes
   diagonals shared by two earlier cells). → the king forbidden-shape alphabet.
2. King neighbourhood types (expect MORE than 6; diagonal occupancy doubles local
   state) and their convolution inequalities — the cut/allocate step MUST stay an
   over-count under corner (diagonal) seams, else it under-counts and the bound is
   INVALID. Expect triple convolutions `Σ_{i+j+k}` (Bui's §4 already needs them).
3. Feed the system to `certificate_bound.py`; SANITY-GATE: the result must be
   `> a(n) ratios (~6.9)` and `> μ_13 = 6.306`, and an analogous rook re-derivation
   must reproduce a TRUE polyomino bound (≥ 4.06). Only then quote a number.

Rook 6-type system (the literal port template) is in
`experiments/certificate_bound.py::rook_step`.

### King derivation attempt (2026-07-11) — machinery works, generic decomposition too loose
Built and VERIFIED against brute force (`experiments/king_types.py`,
`king_derive.py`, `king_bound.py`, `king_bound2.py`):
- Enumerator reproduces A006770; base fact `A(n) ≤ G8(n) ≤ n·A(n)` holds
  (`G8` = marked-cell type, forbid {W,SW,S,SE}), so `λ = growth(G8)`.
- The G8 corner cell decomposes into **12 leaf cases + 3 cut cases** (the cuts are
  exactly the NW-stranding shapes, verified — see the cut/leaf SVGs). Every leaf
  reduction (`case_count(n) ≤ reduced_type(n−1)`) and every cut convolution
  (`cut(n) ≤ Σ piece1(i)·piece2(j)`) is a numerically-verified valid over-count.
- Auto-closure: 24 types (R=1) / 28 (with required-cell tracking). All recurrences
  verified valid over-counts.

**BUT the bound is ~12.5 — WORSE than the crude 12.2, and MEASURED not to improve
with more context:**

| approach | types | bound |
|---|---|---|
| generic twig, R=1 | 28 | 12.50 |
| generic twig, R=1 + required-tracking | 28 | 13.00 |
| generic twig, R=2 | 8740 | 12.5382 |

R=2 closes fast (8740 types, ~1s; `experiments/king_bound_fast.py`); window size
is NOT the lever for the *generic* decomposition. The looseness was the
**case-routing**: routing multi-neighbour cases as lossy linear re-marks instead
of convolutions.

### BREAKTHROUGH (2026-07-11): Bui mechanism ported → λ ≤ 10.35, verified
`experiments/king_bui.py`. Case ONE free cell `d` at a time:
`φ_T = φ_{T'} + φ_{T'}·φ_D` where `T' = T+{d forbidden}` and `D` = `d`'s split-off
type. The `d`-empty branch is an EXACT partition (`{type-T, d empty} = type-T'`);
the `d`-occupied branch is a valid split over-count. The key fix over the generic
version: (1) multi-neighbour cases stay CONVOLUTIONS (preserve both pieces), not
lossy re-marks; (2) the split-off type `D` knows that ALL of `c`'s other
neighbours go to the c-side, so they're empty in the `d`-piece.
- All recurrences verified valid over-counts against brute force (RD<=2); larger
  RD valid by construction (more genuinely-empty cells in the split type = tighter,
  still an over-count).
- **Bound tightens with the split-window RD:**

  | RD (split window) | types | λ ≤ |
  |---|---|---|
  | 1 | 21 | 10.354 |
  | 2 | 185 | 9.402 |
  | 3 | … | (sweeping) |

- So the earlier "can't beat 12.2 generically" was right about the *generic*
  route, but the Bui-faithful route (correct case-routing + split types) DOES beat
  it and keeps improving with context. Target ~7.11 from above; realistic landing
  ~8 for feasible RD. First-ever polyplet upper bound below the crude bound.

**Verdict:** the verification harness is banked and reusable (any proposed king
system can be checked against ground truth in seconds). The crude `λ ≤ 12.2`
stands as the first upper bound. A *tight* bound (below 12.2, toward ~8–9) requires
hand-engineering the king analog of Bui's 6-type system — a real derivation, not
yet done. This is where the upper-bound effort actually is.

### Stage 3 — the paper story
`μ_H ≤ λ ≤ ν_w`, both from the SAME cross-section machinery (one relaxes toward
connectivity from a subset, one from a superset). First rigorous two-sided
bracket on the polyplet growth constant; upper side is novel to the literature.

### Honesty flags
- Stage 1's validity lemma is stated, not yet proven — pin it before quoting ν₁.
- Stage 2's valid finite construction for KING adjacency is the open crux; the
  plan is a roadmap, not a proof. Don't quote a Stage-2 number until the
  construction is derived and it clears the "> a(n) ratios" sanity gate.
