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

**Corrected 2026-08-22.** This section said "three files"; a byte-level
comparison of all 278 tracked files here against the live tree gives **nine**
that shadow a live file and differ from it, not three. The three under
`docs/proofs/` are tabulated below because they are the ones where the
disagreement is a *claim*; the other six differ because the live file simply
moved on, and are listed after the table. The same comparison found 12 files
that are byte-identical to their live counterparts today — those are the
pre-registered input slice, they are **not** duplication to be cleaned up, and
removing them would break `results/ghostship/SANDBOX.md`'s published 21-file
`git archive` command and its "zero dangling references" property. Their
identity to the live tree is today's coincidence, not a property of the record.

The live version is authoritative in every case.

| file | this snapshot says | the live tree says |
|---|---|---|
| `docs/proofs/polyplet-upper-bound.md` | **λ ≤ 9.3153**, bracket `5.828 ≤ λ ≤ 9.3153` | **λ ≤ 9.3154**, bracket `6.543 ≤ λ ≤ 9.3154` |
| `docs/proofs/diagonal-law.md` | integrality stated in the monomial basis | Newton (binomial) basis, and 28 lines more |
| `docs/proofs/convex-mirage.md` | series to n=38, exclusion at lower order | strengthened 2026-08-05: both series to n=700, excluded at order ≤ 24 |

**The λ one matters most.** `9.3154` is the correct value and the project has a
standing rule not to round it back to `9.3153`. A grep across the whole tree
returns both; this file is the reason.

The other six that differ from live are not claim-level traps, but a grep will
still return two versions of each:

    experiments/cluster_weight_dp.py
    experiments/convex_tm.py
    results/convex-polyplets.md
    results/defect-gas.md
    results/directed-king-animals.md
    results/strip-growth-lambda-bounds.md

The twelve that are byte-identical as of 2026-08-22 — `certificate_bound.py`,
`convex_polyplets.py`, `defect_gas.py`, `diagonal_law_proof_check.py`,
`holefree_gas.py`, `kernel_bound.py`, `king_bound_fast.py`, `king_bui.py`,
`king_certificate.py`, `king_slack.py`, `king_types.py` and `spine_deeper.py`,
all under `experiments/` — will start returning two versions the moment any of
them is edited on master. That is expected and is not a defect in this slice.

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
