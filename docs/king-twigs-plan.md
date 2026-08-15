# King twigs — checking the twig-ladder upper bound

> **CLOSED 2026-08-14, closed door.** Level-1 king number = 5⁵/4⁴ = 12.207
> exactly (≥ the ~10.5 kill line below); the KR deferral mechanism is
> structurally blocked on king adjacency, and Phase 0's re-derivation found
> the crude-bound baseline proof broken (repaired). Verdict, receipts and
> the block argument: `results/king-twigs-l1.md`. Phases 2b/3 never run.

*Thread name: **king twigs**. Written 2026-08-13, out of the reading pass over
Klarner–Rivest 1973 and Barequet–Shalah 2019/2022
(`papers/klarner_rivest_1973_upper_bound.pdf`,
`papers/barequet_shalah_2019_improved_upper_bounds.pdf`).*

## Goal

Decide whether the Klarner–Rivest / Barequet–Shalah **twig method** beats our
standing polyplet upper bound **λ ≤ 20000/2147 ≈ 9.3154** (Bui-style
convolution certificate, `docs/proofs/polyplet-upper-bound.md`). The twig
route is a *different* method and has never been tried on king adjacency.
If the level-1 number lands under 9.3154, upgrade it to a certificate at the
`strip-mu-certificates.md` grade; if not, file the number as a closed door.

## Why it might work (and honest odds)

For polyominoes, the level-1 twig bound cut the Eden-style baseline from
6.75 to 2+2√2 ≈ 4.8284 (−28.5%), purely because the twig context pins
already-scanned neighbours and shrinks the per-cell alphabet. Our king
Eden-style baseline is 5⁵/4⁴ ≈ 12.207 (the "crude decision-tree bound" in
`docs/proofs/polyplet-upper-bound.md`). The same proportional cut would land
near **8.7 < 9.3154**. That proportion is an extrapolation, not a theorem —
the king 3×3 neighbourhood overlaps itself more strongly than the square's,
which could push either way. Treat this as a coin-flip worth one afternoon.

Two free design facts from the reading pass:

- Any complete king twig set has **more than λ ≥ 6.543 twigs, so ≥ 7**
  (the square lattice's set of 5 is provably optimal there by the same
  counting argument, BS §2).
- Everything below the twig-design layer is lattice-generic: the ∗
  composition operator, the weight bookkeeping, the x^n y^n injection, the
  diagonal extraction. Only the twig set itself is square-specific. Their
  code is public (github.com/mshalah/polyominoes_polycubes_upperbounds).

## Warnings carried in (do not rediscover these)

- **KR's published 4.6496 is unreproduced.** BS Appendix A shows KR's
  condition (∗) *as stated* is incorrect — its second clause drops twigs and
  the method stops bounding anything. Use **clause 1 only**; cite 4.5252
  (BS) / 4.5238 (Bui 2511.00461) as the standing square bounds, never 4.6496.
- BS Appendix B's W₄ prints a lone negative coefficient (−124x⁵y⁴) —
  near-certainly a sign typo. Re-derive every polynomial; lift none.
- Their λ₃ ≤ 9.3835 (polycubes) is numerically adjacent to our λ ≤ 9.3154
  (polyplets). Different lattice, coincidence — label both wherever they
  co-occur.
- Their degree-indexed theorem is a dead end here: instantiating at d=4
  (degree 8) gives 15.13, worse than the crude 12.207. Degree alone does not
  drive the bound; the context does.

## Phase 0 — pin the formalism (gympie, under an hour)

1. Re-derive the king Eden baseline 5⁵/4⁴ from our own notes and confirm
   the forward-neighbour count under the scan order (4 of the 8: E, NE, N,
   NW when scanning rows bottom-up, left-to-right).
2. From KR §2 and BS §§2–3, write out: the twig definition, the
   polyomino → twig-sequence injection and its weight identity (weight
   x^(cells−1)y^(black), sequence weight x^n y^n), the GF x/(1−ΣW(ℓ)),
   and condition (∗) **clause 1**.

Exit: a one-page formalism note at the top of the eventual results file,
with every object defined for king adjacency — no analogy left implicit.

## Phase 1 — design the king twig set (the real work)

1. Fix the canonical scan order and the known-empty context when a cell
   opens: the four backward king neighbours (W, SW, S, SE) are known
   states. This is the exact king analogue of the L-context.
2. Derive the complete twig set: seed cell + admissible patterns over the
   four forward neighbours, closed under the "every cell but the seed is
   opened exactly once" invariant. Expect ≥ 7 twigs; if a candidate set has
   ≤ 6, it is incomplete — find the missing case before proceeding.
3. Prove the injection for this set (the generic KR proof should transfer;
   write it out, don't wave at it).
4. Compute W(x,y) = Σ twig weights by hand AND by a 20-line enumeration
   script; they must agree.

Exit: the twig set, its W(x,y), and the injection proof.

## Phase 2 — the level-1 number (the afternoon this plan exists for)

1. Extract the growth bound from x/(1−W) by the BS Appendix D diagonal
   method (discriminant in s of the normalised denominator, largest real
   root, bound = 1/root). Port from Maple to exact-rational arithmetic —
   sympy via MacPorts py-sympy if present (ask before installing), else a
   small gmpxx root-isolation routine next to `cpp/strip_mu_cert.cpp`.
2. **RED-first gate before reading the king number:** the identical
   pipeline, fed the square lattice's 5 twigs, must reproduce 2+2√2 =
   4.82842712… to 8+ digits. A pipeline that has not passed this gate has
   produced no king number.
3. Read the king level-1 bound. Three outcomes:
   - **< 9.3154**: proceed to Phase 2b.
   - **9.3154 ≤ bound < ~10.5**: level 1 loses but the C_i ladder might
     still win (their level-1→C₂₁ gains were ~7%). Cost it in Phase 3
     before deciding; do not launch anything.
   - **≥ ~10.5**: closed door. File the number and stop.

### Phase 2b — certificate (only if level 1 wins)

Upgrade to the banked grade: an exact rational x* with the bound verified
in integer arithmetic (the `strip_mu_cert` pattern — Collatz-Wielandt there,
polynomial sign checks here), receipt logged, and
`results/king-twigs-l1.md` written with the twig set, W(x,y), the square
RED gate transcript, and the certificate. Update the sandwich in
`results/strip-growth-lambda-bounds.md` and the memory entry (9.3154 → new
value) in the same commit.

## Phase 3 — the C_i ladder (compute; separate explicit go)

Not part of the afternoon. If Phase 2 lands in the middle band:

1. Port the ∗ operator (clause 1 only). Weights accumulate on the fly —
   C_i is never stored (BS Step 4), so this is compute-bound, memory-free,
   embarrassingly parallel.
2. **Two-source gate:** for i ≤ 3, an independent brute-force enumeration
   of twig sequences must reproduce Σw exactly before any big-i number is
   trusted.
3. Measure, don't project: time i ≤ 10 single-core on ayr. Their per-level
   cost grew ~4.4×; ours should grow ~λ_king ≈ 6.7× and the twig set is
   bigger, so expect a steeper wall. Bring the measured curve and a
   core-hour budget to jasonp before any run over an hour (frontier rules).
   For calibration: their C₂₁ was ~2,800 core-hours for the last 0.9% of
   the bound.

## Cross-references

`docs/proofs/polyplet-upper-bound.md` (the incumbent certificate),
`results/strip-growth-lambda-bounds.md` (the sandwich and its history),
`results/strip-mu-certificates.md` (the certificate grade to match),
`papers/klarner_rivest_1973_upper_bound.pdf`,
`papers/barequet_shalah_2019_improved_upper_bounds.pdf`,
`papers/bui_2025_convolutional_upper_bound.pdf` (the incumbent's method),
`cpp/kingperim.cpp` / `cpp/kinginflate.cpp` (unrelated deliverables of the
same reading pass, kept for the minimal-perimeter thread).
