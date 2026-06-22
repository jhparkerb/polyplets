# Research log — 2026-06-22 (autonomous push, 08:00–20:00)

Goal: find new theorems / conjectures / **code**, refute-then-prove each, and for code
try to show it can't work before implementing + small-scale testing. **Primary focus:
reach — compute more a(n) terms on current hardware.** Secondary: new non-trivial
sequences. Branches per topic (`explore/<topic>`), merge as needed. Machines: gympie +
ayr spare cores (do NOT disturb the a(20) recount on ayr; dalby is on CADO, off-limits).

Status key: ☐ idea · ⚔ refute-attempted · ✓ survived refute · ✗ refuted/dead ·
🔬 implemented+tested · ★ merge-worthy.

---

## Engine facts (the surface these ideas act on)
- `cpp/tma/statedb.h`: `FlatDB` = open hash map, `Sig` keys + one flat `vals` array of
  `cap × stride` **u64**, `stride = maxn+1` (the counts-by-size row). Footprint ≈
  `states × (stride·8 + SIGMAX)` bytes. Measured earlier: row ≈ 84% of footprint, Sig ≈ 16%.
- Peak boundary-state count grows ≈ **×2.42 / term**; ≈300 B/state. So a *k×* memory
  cut buys ≈ `log k / log 2.42` ≈ `1.07·log2(k)` extra terms.
  (2× → +0.78 term, 4× → +1.55, 8× → +2.3.)
- Reach today: a(20)~16GB (done), a(21)~35–40GB, a(22)~90GB, a(23)~230GB.

## REACH ideas (primary)
- **R1 — symmetry fold (top–bottom reflection).** Store only canonical `min(Sig, R·Sig)`;
  `count(Sig)=count(R·Sig)` by the strip's vertical mirror. ~2× memory at ~1× compute.
  Refute/derivation + test below.
- **R2 — ranged/sparse counts-row.** Store only the nonzero window `[lo,hi]` of each row
  (offset+len) instead of full `maxn+1`. Win size = (row width)/(support width) at the
  peak — **measure first**; could be the biggest win or a dud.
- **R3 — mod-p u32 + CRT for full a(n).** Counts mod p in u32 (half the row), 2–3 primes,
  CRT. ~1.7× memory at 2–3× compute. Trades the resource we have (time) for the one we
  lack (RAM) — ideal for a memory-bound, time-rich push. Simplest to prototype.
- **R4 — out-of-core / disk-backed store.** Unbounded reach, slow. Last resort.
- **R5 — compose R1×R3 (×R2).** ~3.4× (R1·R3) → +1.3 terms; with R2 potentially +2.

## NEW-SEQUENCE ideas (secondary)
- **S1 — hole × symmetry cross-stratification** (T(n,k) split by D4 class).
- **S2 — polyplets by perimeter** (king and/or rook perimeter); `sweep8_perim.h` exists.
- **S3 — corner-pinch / contact-type counts** (cf. A397092).
- **S4 — convex subclasses** (row/col/diagonally-convex polyplets; some already in OEIS).
- **S5 — full sequences for the knight / reach-2 lattices** (engines exist: `gf_knight.cpp`).

## THEOREM / CONJECTURE ideas
- **T1 — lifetime-3 exactness** (atom coprimality / Q_H squarefree, H>7). Hard.
- **T2 — the c_H(k+1) hole-GF order law.**
- **T3 — diamond exact-optimality** M(4r)=2r²−2r+1 for all r (we have asymptotic via Strang).
- **T4 — rigorous λ upper bound for polyplets** (king growth constant) via a twig/Catalan
  recurrence adapted to 8-connectivity. (Just assigned.)
- **T5 — exact M(n) for all n.**

---

## Worklog (newest first)
(entries appended as ideas are attempted)
