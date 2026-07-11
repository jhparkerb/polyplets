# Plan: height-restricted Redelmeier for independent T(n,H) confirmation

Goal: confirm specific triangle cells T(n,H) by direct enumeration, with a
correctness case and a test suite that stand **without reference to any
TM-computed value** (so the confirmation is non-circular). Then compute the five
highest-value targets.

---

## 1. Code change (single change to `build/g2` / `cpp/g2_redelmeier.cpp`)

Add one option: **`--height H`** — restrict enumeration to animals whose final
bounding-box height (extent along the scan/primary axis) is exactly `H`.

Redelmeier fixes the scan-minimal cell at the origin, so every cell has primary-
axis coordinate `y ≥ 0` and `minY = 0`; thus `height = maxY + 1`, and `maxY` is
non-decreasing as cells are added. During growth, for a partial animal of size
`s` with current `maxY = m` (so `h = m+1`) targeting final size `N`:

    prune (do not recurse) iff   h > H   OR   (N - s) < (H - h)

- `h > H`: overshoot; height can never decrease. Dead.
- `(N - s) < (H - h)`: too few cells left to reach height `H` (each added cell
  raises `maxY` by at most 1). Dead.

No other code changes. `--per-box` (emits `n w h count`) already yields the
`h`-resolved histogram; `--split S K IDX` already partitions the subtree search.
`T(N,H)` is read off as the `n==N, h==H` entry (summed over `w`).

Two pre-flight confirmations required before trusting output:
- (a) `--per-box`'s `h` is the same axis the prune tracks (`maxY`), i.e. the
  scan-primary axis. Verify against source; align the prune to that axis.
- (b) `--height` composes with `--split` and `--per-box` (all three on).

---

## 2. Correctness argument (to be written into the source header + this doc)

**Base.** g2 counts each fixed animal exactly once (scan-minimal cell at origin,
growth restricted to cells `≥` origin; the untried/tried discipline forbids
duplicates). Established, gate-covered (`gate-g2`). The `--height` change only
deletes whole subtrees; it cannot introduce duplicates.

**Lemma (height monotonicity).** For every animal, `minY = 0` (origin is the
scan-minimum, so no cell has `y < 0`). Hence `height = maxY + 1`, and since
adding a cell never removes one, `maxY` — and therefore height — is
non-decreasing along any growth path.

**Theorem.** With `--height H` and target size `N`, the surviving leaves at
`size = N, h = H` are exactly the set `S = {fixed animals of N cells, height
exactly H}`; so their count equals `T(N,H)`.

*Lossless (no target dropped).* Let `A ∈ S` and let `P` be any Redelmeier prefix
of `A` (size `s`, `maxY = m`, `h = m+1`). By the Lemma `maxY(P) ≤ maxY(A) = H-1`,
so `h(P) ≤ H` — the overshoot test never fires. `A` reaches height `H` using its
`N - s` post-`P` cells, each lifting `maxY` by `≤ 1`, so `N - s ≥ (H-1) - maxY(P)
= H - h(P)` — the too-short test never fires. Thus no prefix of `A` is pruned, so
`A` is enumerated.

*Exact (nothing extra).* The prune deletes a subtree only when **every**
completion has height `≠ H` (overshoot stays `> H`; too-short can never reach
`H`). So no animal outside `S` is counted at `n==N, h==H`.

∎  (Depends only on scan-min canonicity + height monotonicity — no reference to
any prior T(n,H) value.)

---

## 3. Test suite — none of these reference a TM-computed value

Add `gate-g2-height` (Makefile), built on three mutually independent anchors.

**T1 — prune is exactly the identity on the target axis (g2 vs itself).**
For `n = 1..14` and every `H ≤ n`: the full `--per-box` run's `h==H` histogram
(over `w`) must equal the `--height H --per-box` run. Exercises the prune as a
lossless/exact filter using only g2 against its own unrestricted output. Compare
the full `(w,h)` histogram, not just the scalar count, so a "drop one / add one"
prune bug cannot hide.

**T2 — independent third implementation.**
For `n = 1..11`, every `H`: `--height H` must match a from-scratch enumerator
that shares no code with g2 — the canonical-set (frozenset, translate-to-origin,
dedup) brute force in `experiments/` (extended to bin by height). Different
algorithm (explicit set dedup vs untried-list growth), so agreement is not
self-referential.

**T3 — closed-form anchors provable with no computation.**
- `--height n` at each `n = 1..20` must equal `3^(n-1)` (height-`n`, `n`-cell
  animals are one cell per row with `|Δcol| ≤ 1`, translation-fixed → `3^{n-1}`).
- `--height 1` must equal `1` for all `n` (single contiguous row).
These are mathematical facts, independent of every engine.

**T4 — split consistency.**
`--height H --split S K IDX` summed over `IDX = 0..K-1` equals the unsplit
`--height H`, for a few `(n,H,K)`. Self-contained parallel-correctness check.

Pass condition: T1–T4 all green. Only then is the enumerator trusted; the
confirmation runs in §4 are the first and only place a TM value is compared.

---

## 4. Compute the five highest-value targets

One independent, self-contained diagonal per `k = n−H`; each is the deepest-`n`
feasible cell on its diagonal, and each pins the corresponding closed form.

| target      | k | value to reproduce        | pins |
|-------------|---|---------------------------|------|
| T(28,28)    | 0 | 7626247014595529          | 3^{n-1} identity |
| T(25,24)    | 1 | 6067157998917             | P₁ |
| T(23,21)    | 2 | 5923...  (T(23,21))       | P₂ |
| T(21,18)    | 3 | 3044...  (T(21,18))       | P₃ |
| T(20,16)    | 4 | 3357...  (T(20,16))       | P₄ |

(Exact values pulled from `results/ns_a36/perheight/` at run time and written
into each target's record.)

Procedure per target cell `T(N,H)`:
1. `build/g2 square8 N --height H --per-box --split S K IDX` across dalby cores,
   `IDX = 0..K-1`; sum the `n==N, h==H` entries. Record each worker's output and
   the sum under `results/redelmeier_tall/T_<N>_<H>/` with g2's baked provenance
   (rev, host, wall) — one directory per cell, self-describing.
2. **Cross-check = the payoff:** compare the enumerated `T(N,H)` to the banked
   triangle value. Match ⇒ that cell is now two-source (TM + independent
   enumeration) at `n > 19`. Mismatch ⇒ a real finding; stop and investigate
   (do not "fix" toward the TM value).
3. `k=0` T(28,28) doubles as an end-to-end check of T3's identity at `n` beyond
   the test range.

Order: run `k=4→0` (or all under `--split` concurrently); each cell is
independent, so partial completion still yields banked results. Deliverable: a
`results/redelmeier_tall/SUMMARY.md` table of cell / enumerated / banked / verdict.

---

## 5. Whole-row confirmation vs single cells — what actually benefits

The §4 tall cells confirm individual diagonals. A *full row* n confirms every
T(n,H) at once (run g2 unrestricted to that n; no `--height` needed), which is
strictly more valuable per term — but only where the whole row is enumerable.
Whole-row enumeration cost ≈ 1.17·a(n); with the fleet-week budget (~10^16
objects) that caps the fully-confirmable frontier at **n=21** (a(21)≈6.95e15),
and one row deeper the confirmable mass falls off a cliff (n=22 edges only,
~a(22)=4.7e16 > budget). Redelmeier already has n≤19 two-algorithm; so the only
whole rows in reach are **20 and 21**, and they are the highest-value runs
available:

**Full row 20 (~1 day, full fleet):**
- **a(20):** single-algorithm → two-algorithm confirmed (own provenance stops the
  two-algorithm line at n=19; this moves it to 20).
- **A030233 / A030222 / A194596 at n=20:** these inherit confirmation status from
  the fixed count; their symmetric parts are already Redelmeier-enumerated to
  n=24, so confirming F(20) upgrades all three related sequences to two-algorithm
  at 20.
- **P₀…P₆:** row 20 supplies independent (non-TM) held-out values T(20,20−k) for
  the diagonals whose polynomial regime reaches n=20 (3k+1 ≤ 20). Every P_k is
  currently fit to TM output; this is the first outside check on the derivation
  method — indirect confidence in the deployed P₁₆.
- A full-row third witness on the H≤14 cells the strip TM already confirms at 20.

**Full row 21 (~1 week, full fleet — 7×):**
- All of the above at n=21 → frontier moves to 21: exactly **one more sequence
  term** (a(21)) and the related seqs at 21.
- **Same P₀…P₆** — the diagonal threshold does not advance (3·7+1 = 22 > 21), so
  no new closed form is confirmed.
- 7× the compute for that single extra term.

**Neither** reaches the deployed P₁₆/P₁₇ (polynomial regime n≥33, cells 10^25+)
nor the single-source gap (n≥32). The entire benefit is sequence-frontier
extension plus re-confirmation of the low diagonals.

**Decision:** row 20 is the efficient buy — two-algorithm frontier at 20 for
a(n) and all three related sequences, plus an independent check on P₀…P₆, in a
day. Row 21 costs 7× for a lone extra term with no new structural coverage; do it
only if the 21st term specifically wants independent standing. Both dominate the
§4 tall-cell singles on confidence-per-object, so prefer whole-row 20 first;
fall back to §4 singles only for cells above the whole-row frontier.

---

## Sequence

1. Implement `--height`; §1 pre-flight (a),(b).
2. Write §3 tests; wire `gate-g2-height`; go green (this is the correctness
   proof-in-code, no TM values touched).
3. Commit; build native on dalby.
4. **Whole row 20 first** (§5, unrestricted g2 to n=20, `--split`): the
   highest-value confirmation — two-algorithm frontier → 20 for a(n) and the
   three related seqs, independent P₀…P₆. Row 21 optional (7× for +1 term).
5. Run §4 tall-cell targets under `--split` only for cells above the whole-row
   frontier; populate `results/redelmeier_tall/`.
6. `SUMMARY.md`: rows/cells confirmed, enumerated vs banked, verdicts, and the
   two-algorithm frontier the run establishes.
