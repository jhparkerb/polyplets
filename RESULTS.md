# Results registry

A curated record of every count this project has *produced* (not just
reproduced), what each one depends on, and the concrete basis for trusting it.
The machine-level run provenance (binary hashes, parameters, host, git commit)
lives in `ledger/ledger.jsonl`; this file is the human-readable layer that
explains each result and its confidence.

## Confidence tiers

- **reproduces** — matches an already-published OEIS sequence over its known
  range. Not a new claim; it is *evidence the method is correct*.
- **computed** — a new value from a method that reproduces all prior published
  terms, but produced by a single computation one (or more) steps beyond the
  last externally checkable term. Trustworthy, not yet bulletproof.
- **candidate** — a new value not yet independently reproduced; awaiting a
  second, decorrelated computation.
- **confirmed** — independently reproduced by a decorrelated computation
  (different decomposition / compiler / ISA / algorithm) *and* consistent with
  external truth on the overlap range. The bar for OEIS submission.

A result is only **submitted** to OEIS once it is **confirmed** and the
agreement is recorded in the ledger.

---

## R1 — Fixed polyplets, a(19) of A006770

**Value:** a(19) = 151,609,203,011,580
**Status:** **confirmed** (two decorrelated Redelmeier campaigns agree
bit-for-bit, *and* an algorithm-independent column transfer-matrix recount
reproduces the same value — see "The algorithm-independent confirmation" below)

**What it is:** the number of fixed (translation-distinct) king-move animals
of 19 cells — the first term past the previous record of n=18.

**Depends on:**
- the generation engine `cpp/g2_redelmeier.cpp` (Redelmeier enumeration),
- the campaign harness `harness/` (split into 64 workers, merged),
- nothing external beyond the lattice definition (it is a from-scratch count).

**How computed:** campaign "a19-A" on gympie (Apple Silicon / Apple clang),
split 7×64, `runs/a19-A/`. Ledger: `campaign_complete` entry for a19-A.

**Why we trust it so far:**
- the engine reproduces **all 18 previously known terms** of A006770 exactly
  (`tests/gate_g2.py`), so any error would have to be invisible ≤18 and appear
  only at 19;
- the engine is sanitizer-clean and was adversarially reviewed (no bug found);
- `tests/audit_results.py` re-checked the campaign's `results.txt` against the
  published b-file on n≤18 (all match) and the growth ratio a(19)/a(18)=6.7468
  continues the monotone climb toward the growth constant.

**The confirmation (done 2026-06-14):**
- campaign "a19-B" on **ayr** (x86 / GCC, split 8×96) — different ISA,
  compiler, hardware, *and* decomposition — completed 96/96. Its `results.txt`
  is **byte-identical** to a19-A (SHA256 `558f0bdf…` on both), so a(19) and all
  n≤18 agree bit-for-bit. `harness verify -a runs/a19-A -b runs/a19-B` →
  "campaigns agree"; ledger `verified` event 2026-06-14T16:43:33Z. Integer-only
  arithmetic ⇒ a shared hardware/compiler/scheduling fault could not have
  produced identical wrong digits.
- consistent with external truth: n≤18 == A006770 (the published range,
  including Fixed(18)=22,471,158,811,164).

**The algorithm-independent confirmation (done 2026-06-16):**
- both Redelmeier campaigns run the **same generation algorithm**, so the one
  failure mode they cannot catch is a shared algorithmic bug invisible at n≤18.
  That guard is now closed: the **column transfer-matrix engine** (`cpp/tma/`),
  a completely different counting method — dynamic programming over boundary
  signatures, no animal ever generated — independently recounted the whole
  sequence on **ayr** (x86 / GCC) and assembles to a(n) = Σ_H byHeight[H][n] =
  **151,609,203,011,580** at n=19, with n≤18 byte-identical to A006770. Method
  documented in `method-a19.md`; engine math/feasibility in
  `results/tma_state_growth.md`.
- The recount was run as independent per-height jobs (heights 17/18/19 the long
  poles); per-height rows in `~/poly-tma/runs/tma-a19/` on ayr. Two further
  cross-checks passed: a **backward** completion DP on gympie (Apple
  clang/ARM — different host, compiler, ISA, *and* DP direction) reproduced
  byHeight[17][19] = 47,839,787,379 identically to ayr's forward count; and the
  transfer-matrix per-height marginals match the generation engine's
  bounding-box-height marginals (`tests/gate_tma.py`).
- Net: a(19) is now backed by **two independent algorithms** (Redelmeier
  generation and transfer-matrix counting) agreeing exactly, each reproducing
  all 18 prior published terms. A shared algorithmic error would have to corrupt
  two methods that share no counting logic in the identical way — not credible.

---

## R4 — Fixed polyplets, a(20) of A006770

**Value:** a(20) = 1,025,573,519,362,016
**Status:** **candidate** (single-method assembly; awaiting full ISA-decorrelated
reproduction — see "Remaining" below)

**What it is:** the number of fixed (translation-distinct) king-move animals of
20 cells — the next term past the now-confirmed a(19) (R1).

**Depends on:**
- the column transfer-matrix engine `cpp/tma/` (`build/tma`), the same
  algorithm-independent method that confirmed R1 — no animal ever generated;
- per-height jobs `runs/a20/h<H>.out` (`"n count"` = byHeight[H][n]);
- assembly a(n) = Σ_H byHeight[H][n] over H=1..20.

**How computed:** heights 1–18 and 20 on **gympie** (Apple clang / ARM);
height 19 (the heaviest, peak_states 23,975,127) on **ayr** (x86 / GCC),
harvested to `runs/a20/h19.ayr.out` (byHeight[19][20] = 19,586,258,055).
Assembled on gympie 2026-06-20.

**Why we trust it so far:**
- the assembly reproduces **all 18 published terms** of A006770 exactly
  (n≤18 == `fixtures/b006770.txt`) *and* the confirmed a(19) =
  151,609,203,011,580 — a low value would have flagged an inadmissible
  size-budget prune, so the prune is admissible;
- arbitrary-precision (Python) re-sum confirms the value exactly;
- **independent GF cross-check (2026-06-20):** the recovered rational
  generating functions G_H(x)=P_H(x)/Q_H(x) for heights H=1..10
  (`results/fixed_height_gfs.txt`, recovered on ayr by mod-p transfer matrix +
  Berlekamp–Massey + CRT — a different downstream from explicit enumeration)
  expand to series that match the gympie `byHeight[H][n]` columns **exactly for
  all n≤20**. Heights 11–20 have no GF in that file and are not GF-checked.

**Remaining for "confirmed":**
- **DONE (2026-06-21): height 19 is cross-ISA confirmed.** Gympie's own
  height-19 recount (clang/ARM, ~24.5 h) finished and is **byte-identical to ayr's
  (x86/GCC)** — both byHeight[19][20] = 19,586,258,055 (peak_states 23,975,127).
- heights 11–18 and 20 still rest on a single method/machine (gympie); the
  ISA-decorrelated reproduction of those heights is **running on ayr now**
  (`a20cross`). a(20) is confirmed once it lands and matches. Not submitted until then.

---

## R2 — Free polyplets, Free(18) and Free(19) of A030222

**Value:** Free(18) = 2,808,898,025,438; **Free(19) = 18,951,156,321,090**
**Status:** **confirmed** (2026-06-20) — the symmetric counts are now
ISA-decorrelated (ayr x86/GCC byte-matches gympie clang/ARM for n≤20; see
Reproduction below), resting on confirmed Fixed(18) (b-file) and Fixed(19) (R1,
dual-method). Both Free(18) and Free(19) are confirmed new terms.
**Extension (2026-06-20, candidate):** Free(20) = 128,196,711,128,365 — assembled
by Burnside from the n=20 symmetry counts (r90=1630, r180=69,068,156,
axis=26,676,346, diag=23,620,398; `runs/sym20/`) and the **candidate** Fixed(20);
inherits Fixed(20)'s tier (candidate until that confirms). Formula self-tested
against the confirmed n=19 row; integral; symmetric correction +21,208,113.

**What it is:** the number of king-move animals counted up to rotation and
reflection — A030222, which ended at n=17 (since 2002). Free(18) and Free(19)
are both new terms.

**Depends on:**
- the fixed counts Fixed(18) = 22,471,158,811,164 (published A006770) and
  Fixed(19) = 151,609,203,011,580 (this work, R1, dual-method confirmed);
- the symmetric counts at n=18,19 from `cpp/sym/symcount_fast` (animals with
  90°/180° rotation or axis/diagonal mirror symmetry);
- Burnside assembly `tests/common.py:free_and_one_sided` via
  `sym/free_polyplets.py`.

**How computed:** `sym/free_polyplets.py 19 151609203011580`; data in
`results/free_onesided_polyplets.txt`.

**Why we trust it:**
- the symmetric counter reproduces the brute-force oracle's per-symmetry
  counts (`oracle/g1_naive.py:count_symmetry`) for every symmetry type at n≤8,
  and the C++ counter matches the independent Python implementation at n≤11
  (`tests/gate_sym.py`: oracle ← Python ← C++);
- assembled through Burnside, the free counts **reproduce A030222 exactly for
  all n≤17** — the entire published range — so the method is validated against
  external truth right up to the terms before these;
- sanity: Free(18) is within ~3.2×10⁶ of Fixed(18)/8 and Free(19) within
  ~5.9×10⁶ of Fixed(19)/8 (the expected tiny positive symmetric correction);
  ratios stay monotone (≈ growth constant).

**Reproduction so far / what would make it "confirmed":**
- DONE (2026-06-18): the symmetric counts at n=19 are reproduced by an
  *independent Python reimplementation* (`sym/symcount.py`) matching the C++
  `symcount_fast` for all four types — r180=10,178,520, axis=9,765,524,
  diag=8,923,786, r90=none (19≢0,1 mod 4). A different-language reimplementation
  agreeing catches implementation/algorithmic bugs a recompile would not, so
  this is a real upgrade over a single engine.
- DONE (2026-06-20): the hardware/ISA-decorrelated run completed (ahead of the
  ~June 27 estimate). ayr's x86/GCC `symcount_fast` reproduces all four symmetric
  counts **byte-identical** to gympie's clang/ARM build for every n≤20
  (`runs/sym20/{r90,r180,hmirror,dmirror}.out`, diffed). With Fixed already
  confirmed, **Free(18), Free(19) and OneSided(18), OneSided(19) are now fully
  confirmed**; only Free(20)/OneSided(20) remain candidate, through the candidate
  Fixed(20).

---

## R3 — One-sided polyplets, size 18–19 (and the whole sequence)

**Value:** OneSided(18) = 5,617,792,259,411; **OneSided(19) = 37,902,303,297,525**
(full table n=1..19 in `results/free_onesided_polyplets.txt`)
**Status:** **computed** — note: **no OEIS sequence for one-sided polyplets
exists**, so the *entire* sequence n≥1 is new (the n≤17 values have no external
sequence to match, only internal consistency).
**Extension (2026-06-20, candidate):** OneSided(20) = 256,393,397,108,358 — same
Burnside pipeline (rotations only), rests on candidate Fixed(20); integral and
satisfies Free(20) ≤ OneSided(20) ≤ 2·Free(20).

**Depends on / how computed:** same pipeline as R2 (Burnside, but with only the
rotation terms: OneSided = (Fixed + 2·R90 + R180)/4).

**Why we trust it:** the same symmetric counters validated in R2 — now
ISA-decorrelated (ayr x86/GCC == gympie clang/ARM, n≤20); every value is integral
(the /4 divides cleanly, a necessary condition) and satisfies
Free ≤ OneSided ≤ 2·Free. Still weaker than R2 (no external sequence anchors it),
so ideally cross-check a few small terms by exhaustive enumeration before
submitting a new sequence. OneSided(18), OneSided(19) inherit the confirmed Fixed
and ISA-confirmed symcounts; OneSided(20) stays candidate via Fixed(20).

---

## R5 — Hole-stratified polyplet counts, n=18 (#28; novel sequences)

**Value:** the joint (size, #holes) distribution of fixed polyplets through n=18
(`results/holes_n18.txt`). Headline new columns at n=18: **hole-free
A_0(18) = 16,503,616,943,998** and **one-hole A_1(18) = 4,970,078,092,354**; the
full table runs k = 0..10 holes (the maximum is 10 holes at n=18).

**Status:** **computed**, strongly validated; single-engine for n=15–18 (the flood
oracle caps at n=14), so an ISA-decorrelated or independent-method rerun of
n=15–18 would upgrade those specific terms. Every row total is externally anchored
(below).

**What it is:** B(n, k) = the number of fixed (translation-distinct) n-cell
king-move animals with exactly k enclosed holes, in the **primary
4-connected-background convention** (bounded background regions = the Jordan dual;
the `g2 --holes` / OEIS-A389193 convention). The k=0 column is the hole-free
(simply-connected) polyplets and k=1 the one-hole polyplets — both **absent from
OEIS**, as are the higher by-#holes columns. The per-animal flood capped these at
n=14; the transfer matrix removes that cap.

**Depends on:**
- the column transfer matrix carrying the hole count *inside* the sweep via the
  Euler characteristic (holes = 1 − χ for a connected animal; χ accumulates by
  local 2×2 bit-quad increments) — `cpp/tma/euler.h`, `cpp/tma/sweep8_holes.h`
  (`build/tma_holes square8 N --holes`), isolated from and not touching the a(n)
  counting path;
- the n≤14 per-animal flood oracle `results/holes_n14.txt` (#24) for validation.

**How computed:** `tma_holes square8 18 --holes` on **ayr** (x86 / GCC) —
44 h single-core, exit 0, peak RSS 74.6 GB.

**Why we trust it:**
- **sum-invariant:** Σ_k B(n,k) == A006770 a(n) for every n≤18 — each row sums to
  the published (and for a(19), confirmed) fixed-polyplet total, so a miscounted
  column would break the row sum. At n=18 the rows sum to a(18) =
  22,471,158,811,164 exactly;
- **vs an independent algorithm:** byte-identical to the flood oracle
  `results/holes_n14.txt` for all n≤14 (including the max-hole shapes) — flood-fill
  per animal, a different method than the Euler accounting;
- **vs the generator:** == `g2 --holes` for n≤11;
- the Euler/hole accounting is unit-tested (`make gate-euler`: 191k random images +
  the diamond/ring/pinch battery) and regression-checked in `gate-tma` against the
  saved hole oracle — now byte-identical under the engine's MT, checkpoint, and
  reserve paths (gate checks H–L).

**Remaining for "confirmed":** n=15–18 rest on the single transfer-matrix engine
(the flood can't reach there). A decorrelated rerun — a different build/ISA, or the
full n=19 run that re-derives n≤18 as a prefix — would confirm those terms. That
next run is now ~10× faster and resumable on the MT/checkpoint/reserve engine.

---

## Validation reproduced (evidence, not new results)

- Free polyplets n≤17 == A030222 (all 17 published terms) — `tests/gate_sym.py`.
- Fixed polyplets n≤18 == A006770 — `tests/gate_g2.py`.
- Fixed polyominoes n≤70 prefix, polyhexes n≤46 — gates against pinned b-files.
These are why we believe the engines; the new results above inherit that trust
up to their last externally checkable term.
