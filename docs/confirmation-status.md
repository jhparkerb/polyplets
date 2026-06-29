# A006770 confirmation status (no-gaps audit, 2026-06-29)

"Independently confirmed" = **two algorithms that share no counting logic agree**
(the project's standard, oeis/submission-a19.md), OR a **mathematical proof** of
the value. A reimplementation of the same algorithm, or the same algorithm on a
second ISA (cross-ISA), catches code/hardware bugs but **not** algorithm-logic
bugs — so it is *not* independent confirmation.

| n | a(n) | independent? | basis |
|---|---|---|---|
| 1–18 | (published) | **YES** | OEIS-published; decades of independent confirmation (Redelmeier + others) |
| 19 | 151,609,203,011,580 | **YES** (strongest) | two share-no-logic algorithms agree: Redelmeier generation (`cpp/g2_redelmeier.cpp`, 2 decorrelated campaigns `runs/a19-A/B`) **and** column transfer-matrix (`cpp/tma/`); same SHA256; ledger `method_independent_verified` 2026-06-16 (oeis/submission-a19.md) |
| 20 | 1,025,573,519,362,016 | **NO — gap** | column-TM only; cross-ISA (x86+arm) reproduced; checked vs known n≤18 and confirmed a(19). Same algorithm → not algorithm-independent. Submission draft is **GATED "DO NOT SUBMIT UNTIL CONFIRMED"** (docs/a20-submission-draft.md) |
| 21 | 6,954,084,405,510,437 | **NO — gap** | new-engine column-TM only; novel high heights h18–h21 are single-source (dalby); h1–h17 byte-identical ayr/dalby (same algorithm, 2 runs → determinism only) |

## Per-cell confirmation by proof (independent of any computation)

Specific T(n,H) cells are confirmed **for all n** by proof, the strongest kind:

- `T(n,1) = 1`, `T(n,2)` recurrence — proven (C2).
- `T(n,n) = 3^(n-1)` — proven (A1).
- `T(n,n-1) = (25n-45)·3^(n-4)` — proven this session (C1); **proof re-review pending** (docs/proofs/T-n-nm1.md).

So for a(21), the H=1, H=2, H=20, H=21 contributions are proof-confirmed; the gap
is the single-algorithm interior **h3–h19**. Same for any a(n): the four extreme
heights are free *and* certified; the middle band is what an independent run must
cover.

## Gaps and how to close them

- **Smallest unconfirmed term: a(20).** Independent confirmation = run **Method A
  (Redelmeier, `cpp/g2_redelmeier.cpp`)**, which exists in master, supports
  `--per-box` (counts by bounding box → cross-checks every T(n,H) cell, not just
  the total) and `--split S K IDX` (deterministic parallel workers). a(21) is the
  next.
- Redelmeier is **O(a(n))** (no √λ win), so cost scales with the answer:
  a(20) ≈ a(19)×6.8, a(21) ≈ a(19)×46. Multi-day at this scale — **benchmark a
  small n first** to pin the rate (job-checklist item 1) before committing.

## Provenance nits to reconcile

- `fixtures/b006770.txt` calls a(19) "cross-ISA + transfer-matrix" — **incomplete**;
  the authoritative record (oeis/submission-a19.md) is two-algorithm. `results/b006770.txt`
  is right but cites a **missing `method-a19.md`**. Reconcile both to the submission.
- `fixtures/` extends to n=20, `results/` stops at n=19, and **neither lists a(21)** —
  intentional: a(20)/a(21) are not yet confirmed, so they're correctly *not* in a
  publishable b-file.
