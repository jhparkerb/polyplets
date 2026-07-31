# Certificate Squeeze — plan for Bui's full multi-type + certificate machinery

**Goal:** tighten the rigorous polyplet upper bound below the banked λ ≤ 9.31, using the
full apparatus of Bui's papers (engineered multi-type inequality systems + exact rational
certificates). Target λ ≤ 8.5; stretch λ ≤ 8.1 (the rook-gap analogy: Bui's method leaves
~14% on polyominoes, 4.63 vs 4.06; matching that here gives 7.11 × 1.14 ≈ 8.1).

**Status: EXECUTED 2026-07-11 through Phase 2. Phases 1–2 done; Phase 3 NOT pursued
(measured negative — see verdict).**
- **Phase 1 DONE:** exact rational certificate, λ ≤ 9.3153 proved in Fraction arithmetic
  (`experiments/king_certificate.py`, RD=3, x=2147/20000, 5930 rationals). The banked
  bound is now machine-checkable, no floats in the chain.
- **Phase 2 DONE:** slack audit (`experiments/king_slack.py`). Verdict: the over-count is
  diffuse (max 1.22, median 1.14, none >1.5), COMPOUNDING (+0.022/term — grows with n, so
  non-local), and the anchor G8 is asymptotically clean (growth=λ). The growth-with-n is
  the distant-overlap / connectivity-wall signature: finite-type convolution methods floor
  ABOVE λ and cannot reach it. Lever 4 (per-type tuning) dead (no concentrated target);
  lever 1 (multi-cell casing) only relocates the over-count (= king_derive, already ≈12.5).
- **Phase 3 NOT pursued:** required-cell types (lever 2) hit the same wall; best case ~8.1
  (polyomino method's gap), and king slack grows where rook's saturates, so 8-connectivity
  is worse — 8.1 is optimistic. Multi-session + papers + invalid-bound risk for ≤1 term,
  never λ. **Banked λ ≤ 9.3153 (exact) is the result.** Detail: docs/proofs/polyplet-upper-bound.md.

--- ORIGINAL PLAN BELOW (kept for the record) ---

Estimated effort: 2–4 focused sessions. Phase 1 is cheap and independently valuable;
do it even if the rest is abandoned.

## Banked context (do not re-derive)

- Rigorous sandwich today: **6.543 ≤ λ ≤ 9.31** (numerical λ ≈ 7.11; lower side
  upgraded 2026-07-31 to the certified strip ladder μ₁₇, `results/strip-mu-certificates.md`).
- λ ≤ 9.31 comes from the single-cell-split system in `experiments/king_bui.py`
  (RD=3, 5930 types). Proof narrative: `docs/proofs/polyplet-upper-bound.md`.
  Commit `d5addbb`.
- Both levers of THAT decomposition are measured dead — don't retry them:
  - split-window RD saturates ~9.3 (RD=1/2/3 → 10.354/9.402/9.306);
  - cell-choice (which free cell to case on) is a NULL lever: ll/hr/diag/orth
    orderings give the identical closure and identical bound (spectral property
    of the closed system). `DORDER=` env in king_bui.py.
- Validated tooling that reproduces Bui's published results (trust it):
  - `experiments/kernel_bound.py`, `kernel_system.py` — polyiamond λ_T ≤ 3.6108;
  - `experiments/certificate_bound.py` — rook 6-type system → 4.63, exact
    certificate x = 100/463 verified in rational arithmetic.
- Brute-force ground truth: `experiments/king_types.py` — `all_polyplets(nmax)`
  (reproduces A006770), `type_count(lv, forbid=(), require=())`. Supports
  **required** cells already, not just forbidden — Phase 3 needs this.
- The 15-class exact leaf/cut decomposition (`experiments/king_derive.py`) is verified
  correct but plateaued at ~12.5 **because its split-off types lacked context**. The fix
  that got 9.31 was giving the split piece full knowledge of the forbidden cells around
  the cut (`d_type` in king_bui.py). The unexplored hybrid — exact multi-cell partition
  *plus* context-rich split types — is Phase 3's core idea.

## Source material

Bui's two papers (NOT in papers/ yet — fetch from arXiv in Phase 0, they're open access):
- arXiv:2510.06806 — polyiamonds, λ_T ≤ 3.6108. The kernel/convolution-system method.
- arXiv:2511.00461 — polyominoes ≤ 4.63. The engineered multi-type system + certificate.

Download both to `papers/` and add to `papers/INDEX.txt`. Extract, precisely:
1. The exact rules by which Bui *generates* inequalities (what casing steps are allowed,
   when a step is an equality vs an over-count, how required-cell types enter).
2. The certificate format and verification condition he uses.
3. How he *chose* his 6 polyomino types — the engineering heuristic, not just the result.

## Phase 1 — exact rational certificate for the existing 9.31 (cheap, do first)

The current bound is numerical bisection on the monotone iteration. Upgrade it to a
machine-checkable proof:

- Certificate condition: a vector u > 0 with F_x(u) ≤ u componentwise (where F_x is the
  system map: `u_T ← x` for base types, `u_T ← u_{T'} + u_{T'}·u_D` otherwise, all
  scaled at x) proves the iteration from 0 is bounded at x, hence λ ≤ 1/x.
- Recipe: run float iteration at x slightly inside the bisection value; rationalize u
  with `Fraction.limit_denominator` (small denominators); verify F_x(u) ≤ u exactly with
  `fractions.Fraction`; if a component fails, bump u there and re-verify. Follow the
  pattern already working in `certificate_bound.py` (rook x=100/463).
- Deliverable: `experiments/king_certificate.py` printing the rational x*, the
  certificate vector (or a file of it — 5930 entries), and an exact PASS. Update the
  proof doc: the bound becomes "verified by exact arithmetic," no floats in the chain.
- This makes 9.31 publishable-grade regardless of whether Phases 2–4 succeed.

## Phase 2 — slack audit: find where the 31% lives (measurement before design)

Per `measure-dont-reason`: before engineering tighter types, measure which recurrences
are loose.

- For each type T in the RD=2 system (185 types — brute-verifiable), compute
  `slack(T,n) = rhs(T,n) / tc[T][n]` at n = 8, 9 from brute-force counts
  (rhs as in king_bui.py's verification block).
- Rank types by slack. Questions to answer:
  - Is looseness concentrated (a few types ≫1) or diffuse (everything ~1.1)?
  - Is the d-occupied convolution the loose half, or the type-context itself?
  - Does slack correlate with |T| (few forbidden cells = early casing steps)?
- Also measure the *base-fact* slack: G8(n) / A(n) (we bound G8; A ≤ G8 ≤ n·A). If G8's
  growth visibly exceeds A's in the data, a better anchor type is worth a look.
- Deliverable: a table in the proof doc + a decision: which ≤10 types to hand-engineer.
- **Kill criterion:** if slack is diffuse (no recurrence worse than ~1.2 and slack flat
  in n), the over-count is intrinsic to single-cut convolution and Phase 3 must use
  multi-cell exact partitions or nothing will move. If Phase 3's prototype (below) then
  fails to beat 9.31 on its first honest measurement, stop and keep 9.31.

## Phase 3 — engineered multi-type system (the research core)

Levers, in order of expected value:

1. **Multi-cell exact casing.** Instead of casing one free cell (empty | occupied-split),
   case the joint pattern of *all* free neighbours of c exactly (2^k patterns, each an
   exact type equality), and only convolve at genuine articulation structure — i.e.,
   king_derive.py's exact leaf/cut analysis but with king_bui.py's context-rich
   `d_type` split pieces. The 15-class enumeration + connectivity casework is already
   verified; reuse it, don't rewrite.
2. **Required-cell types.** Bui's polyomino system uses types with occupied cells
   required, giving inequalities that *subtract* structure instead of only forgetting
   it. `type_count(..., require=)` already supports verification. Every new inequality
   must still be verified as a valid over-count (or exact) against brute force n ≤ 9 —
   same red-first discipline as king_bui.py.
3. **Adaptive context.** Deepen the window (RD=3–4) only on the types Phase 2 ranked
   loose, keep RD=2 elsewhere — keeps the closure small enough to iterate.
4. **Hand-engineering the worst ≤10 types** following whatever heuristic Phase 0
   extracted from Bui's own 6-type polyomino choice.

Prototype cheaply: implement lever 1 alone at RD=2, measure the bound. If it doesn't
beat 9.31, the connectivity over-count isn't where the slack is — reassess against the
Phase 2 table before touching levers 2–4.

## Phase 4 — certificate at scale + gates

- Re-run the Phase 1 certificate machinery on the final system (may be 10^4–10^5 types;
  the indexed-array iteration in king_bui.py handles 5930 in seconds — profile before
  optimizing, and it's fine to leave a long iteration running per
  small-samples-then-final-confirmation practice).
- Gates before banking:
  - every inequality verified as over-count/exact vs brute force n ≤ 9;
  - exact rational certificate PASS;
  - sanity reproduction: the same pipeline pointed at the rook lattice must reproduce
    ≤ 4.63-ish (this catch caught the invalid tree-encoding bound before — keep it);
  - bound must beat 9.31, else keep 9.31 and record the negative result by name.
- Deliverables: `experiments/king_multitype.py`, certificate file, proof-doc section,
  memory update (supersede the "not pursued" note in the polyplet-upper-bound memory),
  commit.

## Non-goals

- No compute jobs on ayr/dalby — this is all laptop-scale Python/rational arithmetic.
- No new lower-bound work (directed-king bounds are banked, one-way inequality).
- Don't chase below ~8.1 — that's the method's demonstrated gap on polyominoes; getting
  under it is a different research program (transfer-matrix–assisted bounds), out of
  scope.
