# OEIS A006770 — extension to a(19), submission text

Sequence: **A006770**, "Number of fixed polyplets (king-move / 8-connected
lattice animals) with n cells."

New term: **a(19) = 151609203011580**.

Files to attach: b-file `results/b006770_upload.txt` (plain `n a(n)`, n=1..19).

---

## DATA (append to the sequence)

```
151609203011580
```

## Extension line

```
a(19) from Jason Parker, Jun 16 2026
```

## Comment (optional, recommended)

```
a(19) was computed independently by two different algorithms that agree
exactly, and both reproduce all 18 previously known terms: (1) Redelmeier
enumeration, run as two decorrelated campaigns on different CPU
architectures and compilers (Apple silicon/clang and x86/GCC), whose
output files are byte-identical; and (2) a column transfer-matrix count
(dynamic programming over boundary connectivity signatures of a height-H
strip, summed over bounding-box heights, with no animal enumerated
explicitly). The two methods share no counting logic. - Jason Parker, Jun 16 2026
```

---

## Provenance (for your records / the draft's pink-box discussion, not the entry)

- **Value:** a(19) = 151,609,203,011,580. n=1..18 reproduce A006770 exactly.
- **Method A (generation):** `cpp/g2_redelmeier.cpp`, campaigns `runs/a19-A`
  (gympie, Apple clang/ARM, split 7x64) and `runs/a19-B` (ayr, GCC/x86,
  split 8x96). Both `results.txt` SHA256 = `558f0bdf…`; `harness verify`
  reports "campaigns agree"; ledger `verified` 2026-06-14.
- **Method B (transfer matrix):** `cpp/tma/`, run on ayr as independent
  per-height jobs; rows in `~/poly-tma/runs/tma-a19/`. Assembled
  a(n) = Σ_H byHeight[H][n]; the totals file is byte-identical to the
  Redelmeier results (same SHA256 `558f0bdf…`). Method writeup:
  `method-a19.md`. Ledger `method_independent_verified` 2026-06-16.
- **Cross-checks:** a backward completion DP on gympie (different host,
  compiler, ISA, and DP direction) reproduced byHeight[17][19] =
  47,839,787,379 identically; transfer-matrix per-height marginals match the
  generation engine's bounding-box-height marginals (`tests/gate_tma.py`);
  both engines sanitizer-clean, the multithreaded transfer-matrix path
  ThreadSanitizer-clean and bit-identical to serial.

Note: set the date in the extension and comment lines to the actual submission
date when you upload.
