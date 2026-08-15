# King twigs, level 1: 5⁵/4⁴ exactly — closed door

2026-08-14. Executes Phases 0–2 of `docs/king-twigs-plan.md`. Verdict by the
plan's own pre-registered criterion (level-1 number ≥ ~10.5 ⇒ closed door):
**the king level-1 twig bound is λ ≤ 5⁵/4⁴ = 3125/256 ≈ 12.2070 — identical
to the crude decision-tree constant — and the mechanism that let twigs beat
Eden on the square lattice is structurally blocked on king adjacency.** The
incumbent certificate λ ≤ 9.3154 is untouched and unthreatened from this
direction. Harness: `experiments/kingtwigs/l1_schemes.py` (run on dalby,
12.7 s, transcript at the end; every number below is printed by it).

Two findings worth more than the headline verdict:

1. **The banked crude-bound proof was broken** (now repaired in
   `docs/proofs/polyplet-upper-bound.md`). Its decision tree grows the
   frontier only by scan-*ahead* neighbours of included cells, so re-entrant
   animals — a cell attached only from below-behind, e.g. the hook
   `{(0,3),(0,2),(0,1),(0,0),(1,0),(2,0),(3,0),(3,1)}` — never enter the
   frontier at all: the map animal → decision string is undefined on them.
   Measured: 2 of 20 animals missed at n = 3, growing to **96,065 of
   147,941 at n = 8** (65%). The *constant* 5⁵/4⁴ survives because the twig
   scheme below proves it soundly; the doc's argument did not.
2. **Why Klarner–Rivest cannot transfer.** KR/BS gain over Eden by
   *deferral*: a twig refrains from encoding a cell c when a cell b it just
   opened will encode c later — sound because on the square lattice c is
   diagonal from u, hence **outside N(u)**, hence a normal forward slot of
   b. On the king lattice every cell u would want to defer is one of u's own
   neighbours, so c ∈ N(u) ∩ N(b) — exactly b's *shared* set, the cells
   excluded from b's slot frame because "the parent already handled them."
   Deferral and the shared-set exclusion are mutually exclusive; you cannot
   have both, and each alone caps at 12.207 or worse. The harness
   demonstrates the collision mechanically: the deferral variant loses the
   3-cell animal `{(0,0),(0,−1),(−1,−1)}` (nobody ever opens the S cell).

## Phase 0 — formalism (king instantiation)

Scan order: top→bottom, left→right; key(x,y) = (−y, x). Root = scan-min
cell. Processing: FIFO queue of opened cells from the root. Parent direction
of an opened cell = direction back to its opener. **Frame** of a processed
cell u with parent d: N(u) minus {d} minus the shared set N(u) ∩ N(d).
Shared sets: 4 cells for an orthogonal parent (e.g. d = W shares NW, SW, N,
S), 2 for a diagonal parent (d = SW shares W, S). So frames have **3 slots
(orthogonal parent) or 5 slots (diagonal parent)**; the diagonal slot graph
is always a 5-path with one chord (p1–p3), verified for all 8 parent
directions. The root's frame is all 8 directions (a one-letter constant
factor in the GF, immaterial to growth).

**Letter** (twig) of a processed cell = the mask of frame slots it *newly
opens* (in-P, not yet opened). Orthogonal-frame letters embed in the 5-bit
space with two pad positions. Weight x^(opens)·y per letter; an n-cell
animal maps to n letters with total weight xⁿ⁻¹yⁿ (root cell supplies the
leading x) — Klarner–Rivest's Corollary 2.2 verbatim. The injection is
proved by exhibiting the decoder (replay), and the coverage argument is an
induction: N(u) = {parent} ∪ shared ∪ frame; parent is opened, frame is u's
job, and shared ⊆ N(parent(u)) recurses to the root, whose frame is
everything. The induction **requires** that every processed cell opens all
its unopened in-P frame cells — the clause deferral breaks.

Level-1 bound extraction: with h(x) = Σ_letters x^(opens),
a(n) ≤ [xⁿ⁻¹] h(x)ⁿ·O(1) ≤ h(b)ⁿ/bⁿ⁻¹ for every b > 0, so
λ ≤ min_b h(b)/b, certified at rational b in exact arithmetic (`Fraction`).
Gate: the same extractor fed KR's square Σw/y = 1+2x+2x² reproduces
2+2√2 = 4.8284271247 to 8+ digits.

## Phase 1 — the king twig set (scheme D0)

The complete set: all newly-opened masks over the 3/5-slot frames — 8 + 32
geometric twigs before orientation-merging; as weighted letters, the
alphabet census over all animals n ≤ 8 is exactly **(1+x)⁵**
(1, 5, 10, 10, 5, 1 letters at opens 0..5). The plan's "expect ≥ 7 twigs"
counting bound is comfortably satisfied. Machine-verified over all 171,138
king animals n ≤ 8 (enumeration cross-checked against A006770):
decode∘encode = id, codes pairwise distinct, weight identity exact. RED
control: the same harness with one slot silently dropped from the diagonal
frames is caught immediately.

## Phase 2 — the level-1 number

    h(x) = (1+x)⁵,  min_b h(b)/b at b = 1/4:  λ ≤ 4·(5/4)⁵ = 3125/256
                                                = 12.20703125  (exact)

Square controls in the identical pipeline: square D0 gives (1+x)³ and
27/4 = 6.75 (Eden), and the KR extractor gate passes (above).

12.207 ≥ 10.5 ⇒ **closed door** by the plan's outcome table. For
calibration of what remained even optimistically: a perfect 4-slot design
would give min_b (1+b)⁴/b = 256/27 ≈ 9.481, still above the incumbent
9.3154 — so beating the certificate needed *both* a slot reduction *and*
KR-style letter-killing, and the letter-killing is the blocked mechanism.
The C_i composition ladder (Phase 3) would need to recover ~24% from
12.207; BS's square ladder recovered 6.3% total at ~2,800 core-hours for
its last 0.9%. Dead by budget; Phase 3 is not costed further.

## What is and is not closed

- Closed: level-1 twig bounds built from first-order contexts (frames
  determined by the parent direction inside N(u)), with or without
  deferral. The cap is 12.207 and the deferral route is impossible.
- Not explored: genuinely second-order twig geometries (letters that
  pre-encode distance-2 cells, the analogue of KR's c-cell). No mechanism
  survived first-order analysis that would let one approach 9.3154, but
  no impossibility is proved there. Anyone reopening this starts at the
  shared-set collision above, not at the plan's 8.7 extrapolation — that
  extrapolation die is now known to have been cast from a broken baseline
  proof and a mechanism that does not transfer.
- KR's published square 4.6496 remains unreproduced (BS Appendix A);
  nothing here relies on it. Standing square numbers: 4.5252 (BS), 4.5238
  (Bui 2511.00461).

## Receipts

`experiments/kingtwigs/l1_schemes.py 8` on dalby, 2026-08-14, 12.7 s, all
checks PASS, OVERALL GREEN:

```
king counts = A006770[1..8]                                PASS
square counts = A001168[1..9]                              PASS
unreachable animals by n: {3: 2, 4: 25, 5: 225, 6: 1788, 7: 13344, 8: 96065}
hand witness (re-entrant hook) is missed                   PASS
scheme misses animals from n=3 on (proof broken)           PASS
diagonal frames have 5 slots / orthogonal 3                PASS
all diagonal slot graphs are path+chord(1,3)               PASS
D0: round-trip, distinct codes, weight identity            PASS
D0 alphabet census = (1+x)^5                               PASS
D0 certified lambda <= 12.207031250 (rational b)           PASS
D1 deferral fails coverage (witness {(0,0),(0,-1),(-1,-1)}) PASS
RED control: slot-dropped scheme caught                    PASS
square D0 alphabet (1+x)^3, bound 6.750000000              PASS
extractor gate: KR -> 4.8284271247                         PASS
```

(ayr was unreachable at run time — no route to host — so the run went to
dalby beside Confetti; single core, ~13 s, trivial RSS.)
