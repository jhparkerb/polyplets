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
**Status:** **candidate** (one independent confirmation in progress)

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

**What is still pending before "confirmed":**
- campaign "a19-B" on **ayr** (x86 / GCC, split 8×96) — different ISA,
  compiler, *and* decomposition — then `harness verify a19-A a19-B`. (In
  progress.) Integer-only arithmetic ⇒ the two must agree bit-for-bit.
- not done, noted honestly: a fully algorithm-independent equality check (the
  transfer-matrix engine reaching n=19) — the dual campaigns share the
  generation *algorithm*, so they catch decomposition/compiler/hardware faults
  but not an algorithm bug. At n≥19 there is no external anchor, so this and
  the Burnside congruence (below) are the only independent checks.

---

## R2 — Free polyplets, Free(18) of A030222

**Value:** Free(18) = 2,808,898,025,438
**Status:** **computed** (validated method; second run recommended before submit)

**What it is:** the number of king-move animals of 18 cells counted up to
rotation and reflection — the first new term of A030222 since 2002 (it ended
at n=17).

**Depends on:**
- the published fixed count Fixed(18) = 22,471,158,811,164 (OEIS A006770,
  external) — **NOT** on our a(19) candidate;
- the symmetric counts at n=18 from `cpp/sym/symcount_fast` (animals with
  90°/180° rotation or axis/diagonal mirror symmetry);
- Burnside assembly `tests/common.py:free_and_one_sided` via
  `sym/free_polyplets.py`.

**How computed:** `sym/free_polyplets.py 18`; data in
`results/free_onesided_polyplets.txt`.

**Why we trust it:**
- the symmetric counter reproduces the brute-force oracle's per-symmetry
  counts (`oracle/g1_naive.py:count_symmetry`) for every symmetry type at n≤8,
  and the C++ counter matches the independent Python implementation at n≤11
  (`tests/gate_sym.py`: oracle ← Python ← C++);
- assembled through Burnside, the free counts **reproduce A030222 exactly for
  all n≤17** — the entire published range — so the method is validated against
  external truth right up to the term before this one;
- sanity: Free(18)/Free(17) = 6.727 (monotone, ≈ growth constant), and
  Free(18) is within ~3.2×10⁶ of Fixed(18)/8 (the expected tiny symmetric
  correction).

**What would make it "confirmed":**
- a second, decorrelated run of the symmetric counts (e.g. the x86/GCC build on
  ayr) — cheap (minutes); the symmetric counters are √-rare so they reach n=18
  in seconds. Recommended before OEIS submission.

---

## R3 — One-sided polyplets, size 18 (and the whole sequence)

**Value:** OneSided(18) = 5,617,792,259,411 (full table n=1..18 in
`results/free_onesided_polyplets.txt`)
**Status:** **computed** — note: **no OEIS sequence for one-sided polyplets
exists**, so the *entire* sequence n≥1 is new (the n≤17 values have no external
sequence to match, only internal consistency).

**Depends on / how computed:** same pipeline as R2 (Burnside, but with only the
rotation terms: OneSided = (Fixed + 2·R90 + R180)/4).

**Why we trust it:** the same symmetric counters validated in R2; every value
is integral (the /4 divides cleanly, a necessary condition) and satisfies
Free ≤ OneSided ≤ 2·Free. Weaker than R2 (no external sequence anchors it), so
treat as **computed** pending an independent re-run, and ideally cross-check a
few small terms by exhaustive enumeration before submitting a new sequence.

---

## Validation reproduced (evidence, not new results)

- Free polyplets n≤17 == A030222 (all 17 published terms) — `tests/gate_sym.py`.
- Fixed polyplets n≤18 == A006770 — `tests/gate_g2.py`.
- Fixed polyominoes n≤70 prefix, polyhexes n≤46 — gates against pinned b-files.
These are why we believe the engines; the new results above inherit that trust
up to their last externally checkable term.
