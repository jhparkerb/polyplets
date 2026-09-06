# Rook Parity — the banked goal

Banked 2026-08-13, after the four-round triangle campaign failed
(`docs/triangle-postmortem.md`). This file is the goal, its bar, its test, and
the doors closed on the way to it. It is not a brief.

## The goal

> Reduce the base of the exponential running time of polyplet counting to **rook
> parity: c ≤ √3 ≈ 1.73** in `O*(c^n)` — the proven base of the polyomino state
> of the art, pinned as of 2026-08-13. Constant-factor and polynomial-factor
> improvements, however large, are out of scope. **Test: a(40) recomputed end to
> end by the new method**, using no anchor cells or intermediate values from the
> banked run.

The term of art is *reducing the base of the exponential* (Fomin–Kratsch
`O*(c^n)`: polynomial factors suppressed, only `c` counts). Avoid "exponential
speedup" (imports the class-change meaning), "asymptotic improvement" and
"better upper bound" (satisfiable by a polynomial shave), "subexponential
algorithm" (asks for `c^{o(n)}`, a class change — as opposed to subexponential
*overhead* in a reduction, which is fine), and "improved bounds on the growth
constant" (Barequet–Rote–Shalah's phrase for λ itself, a different quantity).

## Why the pin is 1.73

Three candidate pins; this is a charter choice, not a fact.

| pin | meaning | verdict |
|---|---|---|
| 2.67 = √λ_king | the first draft | **desk-refuted**: the incumbent is already below it |
| 2.01 = √λ_rook | "as cheap as polyominoes", mis-derived | nobody's cost; a waypoint at best |
| **√3 ≈ 1.73** | the rook method's proven base | **chosen** — literal reading, and the tower's best case |
| < 1.73 | beating Jensen from the king side | only ever write this knowingly |

- **The incumbent's measured base is ~2.42–2.5, not √λ.** `results/kink-carry.md:46-49`:
  per-term growth ~4.4× = state growth (~2.42) × masks growth (~1.8); kink carry
  deletes the masks exponential, so "b ≈ 4.4 → b ≈ 2.5". a(40) was produced by
  that kernel (`results/ns_a40/PROVENANCE.md:132`). Against the rigorous sandwich
  6.543 ≤ λ ≤ 9.3154, √λ ∈ [2.558, 3.052] — so under every admissible λ the
  shipped engine is already under √λ_king. A bar of 2.67 is unfailable by vacuity.
- **√λ_rook = 2.015 is not what polyomino counting costs either.** Proven
  `O(n^{5/2}·√3^n)` — Barequet–Moffie 2007,
  `papers/barequet_moffie_2007_jensen_complexity.pdf`. Empirical with pruning
  ≈1.41^n, and the current record is n = 70 (Barequet–Ben-Shachar, ALENEX'24 /
  Algorithmica 2026, `papers/counting_polyominoes_revisited.pdf`) — both per
  goal-review's reading of those PDFs, not independently re-checked here.
- Neither method costs √λ^n. **The king/rook gap is height-cap geometry on a
  shared Motzkin cut vocabulary, not the scalar λ.** Rook gets the bbox theorem;
  king does not.

**Second half of the bar, because the repo contradicts itself about its own
base.** Three in-repo statements imply 2.42, 1.61 and 1.73 for the same engine
(`kink-carry.md:46`, `kink-carry.md:69`, `ns_a40/PROVENANCE.md:19,25`). So the
bar also carries a measured clause: fitted per-term cost ratio over n = 24..30
strictly below the incumbent's measured curve on the same window. Threshold to
be set by the base anatomy audit, not before.

## The route: the P_k tower, not transport

Real sweeps at n = 40 were H3–H21; H22–40 came from wired `P_k` closed forms,
k ≤ 18 (`ns_a40/PROVENANCE.md:25`). Phases B and C — H=20 and H=21 solo — were
**84% of the a(40) cpu** (1,116,858 + 3,329,644 of 5,318,465 s). Those are
k = 20 and k = 19.

So: **kink sweep H ≤ 19** (Phase A, 6.3 h on dalby) **+ ab-initio P_k to k = 19
+ the closed depth-1 correction at k = 20** recomputes a(40) end to end with no
anchor cells and no re-run of the expensive band. Composite base ≈ max(√3, √g),
where `g` is the ab-initio P_k cost growth: **g ≲ 3 is parity; g < 5.9 still
beats the incumbent.**

Measured blocker: ab-initio P_k stops at k = 9 (53 GB peak, 66 min, 16 threads,
dalby); k = 10 "scales past dalby's 125 GB… extending needs a state-space
reduction, not more cores" (`results/severance-w1-anchor-cut.md` §Ceiling).

## Out of scope as a mission: king→rook transport

- The transport literature is **directed-only** — Gouyou-Beauchamps–Viennot 1988,
  Bousquet-Mélou–Rechnitzer 2002, Bacher 2015 — because directedness is exactly
  what makes connectivity local.
- Every in-repo localization probe is measured dead: 45° rotation falsified
  (commit `210fb0b`, "correct king diag TM base ~4.52 (worse), 2.04 was a
  phantom"), strong-product factoring negative, MPS χ ~ λ^(H/4), mod-p Hankel no
  collapse.
- **Arithmetic kill for the obvious bijection family**: a reduction with linear
  size blowup β beats the incumbent only for β < ln 2.42 / ln 1.73 = 1.61.
  King-cell → 2×2 block is β = 4; diagonal-splice is β ≥ 2.

Survives as one adversary lane: state precisely what a size-preserving king→rook
reduction must do to the Motzkin cut information, or exhibit the obstruction.
Either outcome is a negative-map entry.

## What transfers between lattices, and what doesn't

- **Vocabulary and kernel mechanics transfer.** Kink carry is the proof — a port
  of the rook literature's cell-at-a-time kernel, and the project's one banked
  base change (`results/kink-carry.md`).
- **Geometry-level moves are connectivity-rule-dependent.** The one published
  rook base-relevant improvement since 2001 is Barequet–Ben-Shachar's 45°-rotated
  bounding boxes — the exact move this repo measured and falsified on king
  (`210fb0b`). Improves rook, worsens king.
- Rook is a cheap **ground-truth** source (`cpp/g2_redelmeier.cpp:85-93`,
  `--rook-bishop`: rook-connected polyplets ARE polyominoes, cross-checked
  against A001168) but **not** a method testbed — there is no rook transfer
  matrix in-tree, and building one is days.

## Gates

Each gate is the whole method executing its whole pipeline at a smaller row —
not cell-by-cell coverage.

0. **Pre-artifact: measure `g`.** Desk and small compute, decides the route
   before any engine exists. g ≫ 6 kills the tower.
1. **a(30) end to end**, exact match against the banked value, **plus the fitted
   per-term ratio over n = 24..30** below the incumbent's curve. Slope, not wall
   time — a method can match every value and still carry the incumbent's base,
   and wall-clock comparisons drown in constant factors.
   **Asymmetric RED control, mandatory**: run with the NW stencil dropped and
   require failure. Symmetric checks pass a broken engine — the DP's structural
   invariants both pass while [q¹] is wrong without the NW stencil, and rook and
   king closures reach identical state sets at every measured H ≤ 8.
2. **a(34)** against the telemetried a(34) run — first comparison against real
   per-height numbers rather than a fit.
3. **a(40)**, per the goal statement.

## First questions, one desk-only day, no fleet compute

1. **Base anatomy audit** from existing run logs. Chartering "beat X" before
   measuring X is round 2 of the campaign again.
2. **P_k tower feasibility**: is there a state-space reduction past k = 10, and
   what is `g`. Check `docs/middle-kingdom-plan.md` for overlap before calling
   anything new.
3. **Rook Hankel ranks at small H** — the one place rook data changes a king
   decision. The single measured crack below Motzkin
   (`results/triangle-r3-involution.md` §2: char-2 ~0.44·2^H against mod-p
   2.5–2.8×/height vs ~3× states) is king-only, basis not constructed, unverified
   past H ≈ 10.

Controls from the postmortem apply from hour zero: adversary on the brief with
kill authority, `INSTRUMENTS.md` from the first dispatch, no PROVED/GREEN/VERIFIED
token quotable without an adjacent in-tree `.log` path, write-ahead to disk for
every agent including the lead.

## Corrections this goal rests on

- `results/finite-lattice-crossover.md` claims the transpose cap `min(H,W) ≤ n/2`
  applies to king animals. **It does not** — a diagonal staircase has
  min(H,W) = n. Quote that file only for its FLM-doesn't-stack conclusion; its
  "√λ diagonal sweep is essentially optimal, remaining speed is engineering"
  rests on the floors package, two-thirds of which `results/r4/r4-floors.md`
  found over-applied or false as stated.
- The polyomino record in project docs is stale at n = 56; it is n = 70.

## The honest frame

The base has moved twice on record — kink carry 4.4 → ~2.5, and Barequet–Ben-Shachar
56 → 70 terms — both by pricing a design choice nobody had priced. The proven
Motzkin exponent of the straight-cut vocabulary has never moved, on any lattice,
by anyone. Parity means matching it, not breaking it.


## Closed, 2026-09-06 (consolidation wave 1)

Round 1 ran 2026-08-16..17 and closed the goal as not well-formed: the rook
Hankel ranks at small $H$ gave $b = 1.7266$, and both the $P_k$-tower route and
the transport route were shown dead by the adversary lanes. The round's
working records, `results/rook1/` (eight files), `docs/rook1-brief.md`,
`docs/rook-parity-bar.md` and `docs/rook-parity-team-process.md`, were deleted
with their history in the consolidation of 2026-09-06; read them with
`git show e5e7870:<path>`. This file is the record.
