# This tree is a 2026-07-12 snapshot. Do not read it as current.

Added 2026-08-22 (`docs/last-orders.md` B1). It alters nothing else in this
directory — the slice itself is frozen on purpose and is evidence.

## What this directory is

A mechanically derived slice of the repository at commit `74b2c20`
(2026-07-12), built for the Ghost Ship experiment and specified in
`results/ghostship/SANDBOX.md`. It is deliberately old: it is what the
experiment's subject was given, and changing it would destroy the record of
what that was.

`tests/gate_citations.py` exempts `results/ghostship/**` for the same reason —
it "is a frozen record of a DIFFERENT filesystem". A consequence of that
exemption is that nothing in the gate suite will ever tell you a file in here
disagrees with the live tree.

## The specific traps

Three files here shadow live files under `docs/proofs/` and differ from them.
The live version is authoritative in every case.

| file | this snapshot says | the live tree says |
|---|---|---|
| `docs/proofs/polyplet-upper-bound.md` | **λ ≤ 9.3153**, bracket `5.828 ≤ λ ≤ 9.3153` | **λ ≤ 9.3154**, bracket `6.543 ≤ λ ≤ 9.3154` |
| `docs/proofs/diagonal-law.md` | integrality stated in the monomial basis | Newton (binomial) basis, and 28 lines more |
| `docs/proofs/convex-mirage.md` | series to n=38, exclusion at lower order | strengthened 2026-08-05: both series to n=700, excluded at order ≤ 24 |

**The λ one matters most.** `9.3154` is the correct value and the project has a
standing rule not to round it back to `9.3153`. A grep across the whole tree
returns both; this file is the reason.

## The other eight files under `docs/proofs/` here

`area-moment-kernel.md`, `area-moments-method.md`, `convex-area-q-temperley.md`,
`convex-box-kernel.md` and `row-gf-specializations.md` are **not** snapshot
copies — they are the experiment's own output, written 2026-08-15 inside the
sandbox, and they never existed on master. They have been triaged
(`results/ghostship/VALUE-TRIAGE.md`) and what survived was imported in
`a4c8085`; `results/convex-polyplets.md` cites them with an explicit `GS/`
prefix precisely to mark them as living here and not in the live tree.

So: nothing in this directory is lost work needing recovery. It is an input
slice plus an output record, both intentionally preserved.
