# Upper bound on the polyplet growth constant λ

> **OUTCOME (achieved below): λ ≤ 9.3154, PROVED** (exact rational Bui
> convolution certificate; see the BREAKTHROUGH + Certificate-Squeeze sections).
> The two-sided rigorous bracket is **6.543 ≤ λ ≤ 9.3154** (lower side upgraded
> 2026-07-31 to the certified strip ladder μ₁₇, `results/growth-constant.md`;
> at this doc's writing it was 5.828). The intro/plan/crux/
> "Verdict" text below is the ORIGINAL pre-breakthrough scaffolding, kept as the
> derivation record — it says "not yet done"; it was done later in this same doc.

> **CORRECTION 2026-08-07, repo-wide: the headline decimal was 9.3153 and is now
> 9.3154.** Nothing about the certificate changed and nothing downstream depended
> on the difference; the digit was simply rounded the wrong way. What the
> certificate proves is `λ ≤ 20000/2147 = 9.3153237…`. Rounding that to four
> places *to nearest* gives 9.3153 — which is BELOW the true value, so
> "λ ≤ 9.3153" asserts 3.2e-5 more than was ever proved. An upper bound has to
> round away from the truth, so the four-decimal form is **9.3154**.
>
> Swept across 32 files (docs, results, experiments, `polyplets/` comments,
> and the manuscripts of the day). Where the number appears as an *approximation*
> rather than a bound it now reads 9.31532, so that no bare "9.3153" is left in
> the tree to be quoted as the bound. The Lean statements were already exact
> (`lambda ≤ 20000/2147`) and only their comments moved. Receipts and logs were
> not touched — they record what a run printed.
>
> Prefer the rational `20000/2147` to any decimal in code; a live threshold in
> `experiments/concatenation_bound_check.py` now uses it, since rounding UP there
> would make a rival bound look useful when it is not. Caught by
> `paper/verify_l_papers.py`, which keeps a RED control that rejects the
> truncated form.

2026-07-11. (Original intro:) There was no published or project upper bound on
λ_polyplet (only lower: 6.475 multi-directed, 5.828 directed; estimate ~7.11).
This note: a clean crude bound, and the design + crux for a tight one.

## Crude rigorous bound: λ ≤ 5⁵/4⁴ = 3125/256 ≈ 12.2

**Proof REPAIRED 2026-08-14** (king-twigs round, `results/growth-constant.md`,
harness `experiments/kingtwigs/l1_schemes.py`). The original argument below
is broken; the constant survives by a sound BFS-frame derivation.

*The broken version (kept as a warning):* "scan row-major; when a cell is
included, only its king-neighbors ahead in scan order (E, SW, S, SE, ≤ 4)
newly enter the frontier — the other four are already behind — so
a(n) ≤ C(5n, n)." The parenthetical is false: *behind* does not mean
*already considered*. A re-entrant animal whose cell attaches only from
below-behind — witness the hook
`{(0,3),(0,2),(0,1),(0,0),(1,0),(2,0),(3,0),(3,1)}`, where `(3,1)` is an
ahead-neighbor of no included cell — never enters the frontier, so the map
animal → decision string is undefined on it. Measured: the scheme misses 2
of 20 animals at n = 3 and 96,065 of 147,941 at n = 8.

*The sound derivation of the same constant:* process opened cells FIFO from
the scan-min root (BFS). A processed cell u with parent d encodes, as one
letter, which cells of its **frame** — N(u) minus {d} minus the shared set
N(u) ∩ N(d) — it newly opens. Shared sets have 4 cells for orthogonal d and
2 for diagonal d, so frames have 3 or 5 slots; coverage holds because
N(u) = {parent} ∪ shared ∪ frame and shared ⊆ N(parent(u)) recurses to the
root (whose frame is all 8). Each n-cell animal maps injectively (replay
decoder) to n letters of total weight xⁿ⁻¹yⁿ; the letter alphabet is the
5-bit mask family with Σ x^(opens) = (1+x)⁵, so
`a(n) ≤ [xⁿ⁻¹] (1+x)^{5n}·O(1)` and `λ ≤ min_b (1+b)⁵/b = 5⁵/4⁴` at
b = 1/4. ∎  Machine-verified (round-trip, distinctness, weight identity,
alphabet census) over all animals n ≤ 8, with a RED slot-dropping control.

The "overlap accounting improves toward ~9–10" remark previously here is
withdrawn: the improvement it gestured at is the Klarner–Rivest deferral
mechanism, and that is structurally blocked on king adjacency (a deferred
cell always lands in the child's shared set) — see
`results/growth-constant.md`, which closes the twig route at exactly 5⁵/4⁴.

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
bracket it). See results/growth-constant.md.

## PLAN: bound λ, simply then tightly

Common invariant: every ν produced must stay ABOVE the true growth (sanity: >
observed a(n)/a(n-1) ≈ 6.9, and > μ_13 = 6.306). A bound is VALID iff it counts a
superset of all polyplets. Refinements form a monotone decreasing sequence
ν ↘ λ.

### Stage 0 — crude counting (DONE, rigorous): λ ≤ 12.2
The `C(5n,n)` argument above. No machinery. Bankable now.

### Stage 1 — optimize the crude count: NO simple valid improvement (checked 2026-07-11)
Attempted: encode each animal by its Redelmeier growth TREE (each cell has ≤4
forward king-neighbors ⇒ ≤4-ary tree, n nodes) ⇒ `λ ≤ 4⁴/3³ = 256/27 ≈ 9.48`.
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
  of local "twigs" (the occupancy pattern of the newly-exposed neighbors at each
  discovery step) from a finite alphabet. animal → sequence is INJECTIVE; not
  every formal sequence is a valid animal ⇒ counting all formal sequences
  over-counts. Unbounded size is handled by a geometric series (algebraic GF),
  and the bound is the **diagonal of a 2-variable rational GF** `x/(1 − y·A(x))`
  where `A(x)` sums the twig-alphabet weights.
- **Eden level (= our Stage 0, now explained):** alphabet = all occupancy
  patterns of the `K` newly-exposed neighbors ⇒ `A(x)=(1+x)^K`, diagonal
  `~ C(Kn,n)` ⇒ `λ ≤ K^K/(K−1)^{K−1}`. Rook `K=3 → 6.75`; **king `K=5 → 12.2`**
  — identical to our `C(5n,n)`. Good cross-check.

### Stage 2 — tighten via context (the real work), TWO templates
Both reduce the effective alphabet by exploiting that king diagonal coupling
already DETERMINES some newly-exposed neighbors from earlier BFS steps, so fewer
free bits per twig ⇒ smaller `A(x)` ⇒ smaller diagonal growth ⇒ tighter bound.

- **(A) Klarner–Rivest "L-context" + cut hierarchy.** Reduces rook 6.75 → 4.83 →
  (cut C_10) 4.65; Barequet–Shalah pushed to C_21 → 4.5252. Bound via the
  discriminant/Sylvester determinant of the GF denominator. Heavy (millions–
  trillions of twigs), computer search.
- **(B) Bui's convolution-certificate method (RECOMMENDED port, arXiv:2510.06806).**
  A small system of convolution GF inequalities over a handful of local
  forbidden/free neighborhood shapes ⇒ a single algebraic **kernel equation**;
  the bound is proved by exhibiting a positive rational certificate satisfying the
  inequality system — verifiable by ARITHMETIC, no residue calculus, no
  high-degree root-finding. Polyiamond example: `z/x = 1+z+z²+z³` ⇒ root of
  `2z³+z²−1` ⇒ `λ_T = 1+2z+3z² ≤ 3.6108`. Explicitly designed to be
  lattice-agnostic ("applies elsewhere").

**The load-bearing crux (NOT yet derived — do carefully, sanity-gate it):** the
king-adjacency version of the "which neighbors are already determined at each BFS
step" geometric lemma. King BFS discovers a cell whose already-visited context
includes cells diagonal to *two* earlier cells — so the context window is a
`3×3`-minus-center-ish shape, not the rook L-tromino. Getting this case analysis
right is the whole game (and where the Stage-1 tree bound went wrong). Derive the
king twig alphabet / Bui neighborhood shapes from it, write the king kernel
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
1. King BFS closure lemma: which of the 8 neighbors are already-determined at a
   discovery step (rook's is "left + 3-below" = the L; king's is larger, includes
   diagonals shared by two earlier cells). → the king forbidden-shape alphabet.
2. King neighborhood types (expect MORE than 6; diagonal occupancy doubles local
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
**case-routing**: routing multi-neighbor cases as lossy linear re-marks instead
of convolutions.

### BREAKTHROUGH (2026-07-11): Bui mechanism ported → λ ≤ 10.35, verified
`experiments/king_bui.py`. Case ONE free cell `d` at a time:
`φ_T = φ_{T'} + φ_{T'}·φ_D` where `T' = T+{d forbidden}` and `D` = `d`'s split-off
type. The `d`-empty branch is an EXACT partition (`{type-T, d empty} = type-T'`);
the `d`-occupied branch is a valid split over-count. The key fix over the generic
version: (1) multi-neighbor cases stay CONVOLUTIONS (preserve both pieces), not
lossy re-marks; (2) the split-off type `D` knows that ALL of `c`'s other
neighbors go to the c-side, so they're empty in the `d`-piece.
- All recurrences verified valid over-counts against brute force (RD<=2); larger
  RD valid by construction (more genuinely-empty cells in the split type = tighter,
  still an over-count).
- **Bound tightens with the split-window RD:**

  | RD (split window) | types | λ ≤ |
  |---|---|---|
  | 1 | 21 | 10.354 |
  | 2 | 185 | 9.402 |
  | 3 | 5930 | 9.306 |

  Window lever SATURATES at ~9.3 (RD=2→3 moved only 0.096). Best banked: **λ ≤ 9.31**.

  Both levers of this decomposition are now measured and exhausted:
  - **window (RD):** saturates ~9.3.
  - **cell-choice** (which free cell `d` to case on): NO EFFECT. ll / hr / diag / orth
    orderings all give the identical 185-type closure and identical 9.4022 at RD=2 —
    the closure saturates to the same set regardless of casing order, and the bound is a
    spectral property of the closed system. Not a lever here (unlike in Bui's richer
    multi-type systems). See `DORDER=` env in experiments/king_bui.py.

  λ ≤ 9.31 is the floor of this single-cell-split decomposition. Going lower (toward the
  polyomino-method-analogous ~8) would require Bui's full multi-type-with-certificate
  apparatus — substantially more machinery, diminishing returns. The 8-neighbor
  connectivity makes the convolution over-count looser than the 4-neighbor rook case
  (there the same method leaves ~14%: 4.63 vs true 4.06; here ~31%: 9.31 vs true 7.11).

  #### EXACT rational certificate (Certificate Squeeze, Phase 1)
  The 9.31 bound is now machine-checkable, not just numerical bisection.
  `experiments/king_certificate.py` finds a rational super-solution u > 0 with
  u_T ≥ F_x(u)_T for every type T (F_x = the system map at x); by monotonicity u
  dominates every iterate, so the iteration is bounded at x and **λ ≤ 1/x** rigorously.
  RD=3: x = 2147/20000, a 5930-component certificate (max denominator 10⁶), all
  inequalities verified in exact `fractions.Fraction` arithmetic →
  **λ ≤ 9.3154, PROVED (no floats in the chain).** (The tiny gap 9.3154 vs the
  numerical 9.306 is a deliberate 0.1% safety margin `eps` so the super-solution has
  room; shrink `eps` to tighten toward 9.306 at the cost of larger fixpoint values.)
  RD=2 cross-check: x = 106251/10⁶ → λ ≤ 9.4117, PASS.

  #### Slack audit (Certificate Squeeze, Phase 2) — where the 31% lives
  `experiments/king_slack.py` measures slack(T,n) = rhs(T,n)/true_count(T,n) for every
  recurrence in the RD=2 system, against brute-force A006770 counts. Findings:
  - **Diffuse, not concentrated.** Over 152 recurrences: max slack 1.222, median 1.144,
    min 1.000; nothing above 1.5, only 4 above 1.2. The loosest are the far-reach split
    (D) types (|T|≈10, window distance-2). No small set of "bad" types to hand-engineer —
    fixing the top-4 barely moves the bound. **Lever 4 (per-type tuning) is dead.**
  - **Grows with n:** slack@8−slack@7 ≈ +0.022/term (median). A purely *local* over-count
    would be CONSTANT in n; growth means the over-count **accumulates with animal size** —
    a global effect. This is the distant-overlap signature: in φ_{T'}·φ_D the d-piece and
    c-side may wrap around and collide arbitrarily far from the cut, and no finite window
    can forbid it. Same **connectivity wall** that saturated the RD lever (and every prior
    algorithmic lever in this project).
  - **Anchor is clean.** Base fact G8(n)/A(n) = 1.0,1.0,1.1,1.23,1.36,1.50,1.63 (n=1..7):
    grows, but only as the polynomial prefactor allowed by G8 ≤ n·A, so growth(G8)=λ
    exactly. The anchor leaks no exponential — all exponential looseness is the convolution.

  **Phase 3 verdict (measured, not reasoned).** The over-count is intrinsic to finite-type
  convolution: diffuse, compounding, non-local. Multi-cell exact casing (lever 1) only
  RELOCATES it — that is precisely the `king_derive.py` leaf/cut structure, already
  measured at ≈12.5 (worse). Required-cell types (lever 2) can make cuts LOCALLY exact but
  cannot forbid distant overlaps, so they hit the same wall; best case is the polyomino
  method's demonstrated gap (~14% ⇒ ~8.1), and the king slack GROWING with n (vs the rook
  method's saturating slack) says 8-connectivity is genuinely worse — 8.1 is optimistic,
  not guaranteed. Reaching ~8 would need the full hand-engineered required-cell apparatus
  (needs Bui's papers, multi-session, real invalid-bound risk) for at most ~1 term and
  never λ. **Recommendation: bank the exact λ ≤ 9.3154; do not sink multi-session effort
  into Phase 3.** The connectivity wall is a hard floor for this method class.

- So the earlier "can't beat 12.2 generically" was right about the *generic*
  route, but the Bui-faithful route (correct case-routing + split types) DOES beat
  it and keeps improving with context. Target ~7.11 from above; realistic landing
  ~8 for feasible RD. First-ever polyplet upper bound below the crude bound.

- **Concatenation route also closed (2026-08-01, `results/growth-constant.md`).**
  Barequet–Ben-Shachar–Osegueda's quasi sub-multiplicativity gives an upper bound
  from a single term: with `a(40)` banked, a degree-2 `P` would yield λ ≤ 7.745
  (degree 4 already yields nothing). But their lexicographic split shatters a king
  comb into ~n/4 components (measured), so the reassembly code is `n^Θ(n)`; the
  connected (centroid) split cannot prescribe halves to within `O(1)`. Same
  connectivity wall as Phase 3. Transfer check: the missing lemma would also beat
  the polyomino record 4.5252 → 4.3828 from published terms, so it is known-hard.

**Verdict (updated):** the tight bound WAS derived — the king analog of Bui's
system was hand-engineered and certificate-verified to **λ ≤ 9.3154** (see the
BREAKTHROUGH + Certificate-Squeeze sections above). The verification harness is
banked and reusable. (Original pre-breakthrough verdict: "crude 12.2 stands; a
tight bound is not yet done" — superseded.)

### Stage 3 — the paper story
`μ_H ≤ λ ≤ ν_w`, both from the SAME cross-section machinery (one relaxes toward
connectivity from a subset, one from a superset). First rigorous two-sided
bracket on the polyplet growth constant; upper side is novel to the literature.

### Honesty flags
- Stage 1's validity lemma is stated, not yet proven — pin it before quoting ν₁.
- Stage 2's valid finite construction for KING adjacency is the open crux; the
  plan is a roadmap, not a proof. Don't quote a Stage-2 number until the
  construction is derived and it clears the "> a(n) ratios" sanity gate.
