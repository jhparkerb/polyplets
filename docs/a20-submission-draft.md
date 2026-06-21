# a(20) submission draft — GATED, DO NOT SUBMIT UNTIL CONFIRMED

**Status as of 2026-06-20: a(20) is a CANDIDATE (RESULTS.md R4).** This file is
staged so submission is instant once confirmed; it must NOT be acted on until:

1. ayr's all-x86/GCC assembly of a(20) (run `a20cross`, heights 1–18,20 + the
   already-done h19) matches the gympie candidate **1,025,573,519,362,016**
   byte-for-byte, AND
2. gympie's own height-19 recount (PID 85504) byte-matches ayr's
   byHeight[19][20] = 19,586,258,055.

When both hold, RESULTS.md R4 flips to **confirmed**, the ledger gets a
`method_independent_verified` / `verified` event, and only then does the b-file
line below go live.

## b006770 b-file — line to append (after `19 151609203011580`)

```
20 1025573519362016
```

## OEIS comment / submission note (A006770)

> a(20) = 1025573519362016 computed by an algorithm-independent column
> transfer-matrix method (dynamic programming over boundary signatures; no
> animal enumerated), assembled as a(n) = Sum_{H>=1} B_H(n) where B_H(n) counts
> fixed n-cell king-move animals of bounding-box height exactly H. Verified
> against the published terms n<=18 and against the dual-method-confirmed
> a(19) = 151609203011580. Cross-ISA reproduced on independent x86/GCC and
> ARM/clang builds; heights 1–10 additionally cross-checked against recovered
> rational fixed-height generating functions.

## Companion shape sequences at n=20 — candidate b-file lines (also gated)

All four are **candidates**: they assemble by Burnside from the n=20 symmetry
counts (r90=1630, r180=69,068,156, axis H=26,676,346, diag D=23,620,398;
`runs/sym20/`) and the candidate Fixed(20), so they inherit its tier. They go
live only when Fixed(20) confirms **and** the symmetry counts are cross-ISA
reproduced on ayr (the `symcheck` run — once it byte-matches gympie's n≤20
symmetry counts). All five extend **existing** OEIS entries (one-sided is
A030233, not a new sequence):

| sequence | what | b-file line to append (after n=19) |
|----------|------|-------------------------------------|
| A006770 | fixed       | `20 1025573519362016` |
| A030222 | free        | `20 128196711128365` |
| A030233 | one-sided   | `20 256393397108358` |
| A030234 | bilaterally symmetric = ½(H+D) | `20 25148372` |
| A030235 | asymmetric = Free − ½(H+D)      | `20 128196685979993` |

Internal consistency (necessary conditions, all hold): every value integral;
Free ≤ OneSided ≤ 2·Free; bilateral + asymmetric = Free; Burnside formula
self-tested against the confirmed n=19 row.

## Promotion checklist (when the gates clear)

1. Append the five b-file lines above to their `oeis/` b-files / `%S%T%U` data.
2. Add `a(20) from _[submitter]_, 2026` to each `%E` line.
3. Flip RESULTS.md R2/R3/R4 to confirmed; ledger `verified` events.
4. Add a(20) to the paper abstract + Table~\ref{tab:terms} + growth-ratio line,
   and to `verify_claims.py`.
