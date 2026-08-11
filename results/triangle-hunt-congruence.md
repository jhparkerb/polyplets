# Triangle hunt, Proposer 2 (congruence / valuation / symmetry): ranked summary

2026-08-11. Wave 1 of `docs/triangle-structure-team-brief.md`. *Positive*
detail lives in `results/triangle-hunt-klein-parity.md` and
`results/triangle-hunt-sym-diagonals.md`; this file ranks everything and
records the negatives and the prior-work boundary so nobody re-mines it.

## Ranked survivors

1. **C1 — proved forced parity** (`triangle-hunt-klein-parity.md`).
   T(n,H) ≡ 0 (mod 2) for n odd, H even. Proved blind from the definition
   (tb-flip pairing). Verifier: **SURVIVES, 135/135 holdout (81
   real-sweep), 190 cells total**. Tier C by kind — but **0 bits on a(40)**
   (row 40 is even-n; no covered cell there). Its value is theorem-grade
   parity on 190 cells of n ≤ 39 and the exact-zero-set observation
   I(n,H) = 0 iff {n odd, H even} on all 820 cells.
2. **Symmetric-triangle diagonals** (`triangle-hunt-sym-diagonals.md`).
   I(n,n−k) is eventually quasi-polynomial of degree ⌊k/2⌋, with **no
   3-power prefactor** (contrast the diagonal law): k ≤ 2 blind
   (fit self-enumerated n ≤ 14, banked 15..40 pure holdout, 26+13+26
   exact hits), k = 3..5 fit banked n ≤ 22 / holdout 23..40 (9+18+9 hits;
   k=5 is a labelled manual override of the support rule). k = 0,1 proved
   outright. Refuter B verified the whole surface by independent recount
   and corrected the printed k=4 form to m = ⌈n/2⌉ (transcription error;
   correction noted in the file).
3. **Symmetric-triangle column recurrences** (same file). I(n,3) =
   2I(n−2,3) − I(n−8,3) and an order-5 recurrence for I(·,4)'s even
   subsequence, fit n ≤ 22, **18/18 and 9/9 holdout including the n = 40
   terms** — the row-40 parity-check inputs I(40,3), I(40,4) become
   two-source. Mechanistically expected to be C-finite (palindromic TM);
   the content is the small order and the verified extrapolation.

Honest a(40) bottom line for this whole class: **no new direct bits.**
The per-cell parity bit at n = 40 was already banked
(`results/subgroup-mod4.md`, 820 cells, 0 mismatches) before this hunt
started; items 2–3 harden its inputs, item 1 replaces engine agreement
with a proof on a sub-region that excludes row 40.

## The prior-work boundary (mapped so it stays closed)

My assigned "Burnside cross-links" scope turned out to be **largely banked
prior work**, found by grep before proposing (the brief's rule):

- T(n,H) ≡ I_H(D2ax) (mod 2): banked and checked on all 820 cells incl.
  row 40 — `results/subgroup-mod4.md`.
- Per-cell mod-4 refinement: verified n ≤ 32, **explicitly declined at
  n = 40** for three measured reasons (`results/percell-mod4.md`,
  `subgroup-mod4.md` §"why it is NOT being bought") — not re-pitched.
- Rowsum mod 4 at every n ≤ 40 and mod 8 at n ≤ 32 (Fix(d) wall):
  banked, same files.
- Free/one-sided Burnside integralities mod 4/8 on a(n): asserted by
  `scripts/derive_related.py` on every run — restatements.
- Everything mod 3: `results/ternary-spine.md`, `results/triangle-snf.md`.
- Alternating row sums and row-polynomial special points:
  `results/triangle-combinations.md` §2–3 — no recurrence, oscillation
  analyzed; not re-probed (but see V4 below for the residue angle it
  left open — negative anyway).

My independent confirmations along the way (worth keeping, not claiming):
Klein per-cell identity, forced zeros, and cross-lineage agreement of
`p2_enum --sym` vs `symcount_fast` byheight (105/105 cells n ≤ 14) vs the
sym34 farm totals (`experiments/tristruct/p2_measure.py`, all 7
measurements PASS) — a fifth independent implementation agreeing on the
symmetric counts.

## Negatives (probed and barren — do not re-probe)

`experiments/tristruct/p2_valuation_probe.py` (exact, whole banked
triangle):

- **V1** v_p(a(n)) for p = 2,3,5,7, n ≤ 40: scattered, no periodicity, no
  monotone or digit pattern (sequences printed in the script output;
  v_2 ranges 0..6 with no visible law).
- **V2** v_3(T(n,H)) off the diagonal-law region (k > 13): 254/351 cells
  have v_3 = 0; the 12 cells with v_3 ≥ 3 are scattered across bands with
  no common slice, row, or residue structure.
- **V3** v_2(T(n,H)) whole triangle: the valuation histogram decays
  roughly geometrically (as independent-ish 2-adic digits would); 15
  cells with v_2 ≥ 6. The three v_2 = 10 cells are (15,4), (31,14),
  (39,14) — two share column 14, noted as a curiosity only; no relation
  fits them and n = 23..39 column-14 valuations in between are small.
- **V4** F_n(−1) = Σ(−1)^H T(n,H) mod 4 and mod 8: residues irregular,
  no period ≤ length/2, no parity-class structure.
- **V5** coordinate-dependent moduli: T(n,H) ≡ 0 mod n on 69/819 cells,
  mod H on 131/780 — both near chance for divisor-sized moduli; no
  forced classes.
- **Symmetric-triangle columns H = 5..12**: no C-finite recurrence of
  order ≤ 12 fits n ≤ 22 (`p2_symcol_rec.py`); symmetric-triangle
  diagonals k ≥ 6: onset past usable fit depth, undetermined.
- **Blind-protocol limit**: self-enumeration reach n = 14 (3m42s;
  each +1 costs ~7x) caps blind diagonal fits at k ≤ 2.

Ledger observation, NOT a candidate (refuter B's side finding, §4 of
`results/triangle-hunt-refutation-symmetry.md`; re-verified here): T(n,6)
and T(n,8) are genuinely periodic mod 2 with period 8 on all n ≤ 40, and
T(n,4) has period 4 (the sweep found that one and culled it
KNOWN-COINCIDENT). H = 10 is the first aperiodic-mod-2 even column.
Presumably low-strip closed-form parity; recorded so nobody rediscovers
the H=6/H=8 periodicity as a finding — the sweep missed them only through
its 2p+4 support rule.

Not probed (out of budget, stated so nobody assumes it was): p-adic
structure of T along columns for p ≥ 5 beyond the sweep's fixed-modulus
battery; congruences tying ≥ 3 cells across different rows mod m
(no mechanism candidate found to aim it).

## Rule/lineage summary for refuters

Self-enumerated data: `p2_enum.cpp` (own recursion, own normalization,
own symmetry tests; crosschecked 0-mismatch to n = 12 against all four
proposers' enumerators, `results/triangle-hunt-enumerator-crosscheck.md`).
Banked inputs consumed: the T triangle (via the harness, peek-guarded),
`results/subgroup_d2ax_byheight.txt`, `runs/sym34/{hmirror,r180}.out`.
No engine kernel read; no floats anywhere.
