# Round-1 instruments — one line each, and the receipt that proves it ran

Opened 2026-08-13 by the lead, before the first spawn, per
`docs/rook-parity-team-process.md`. Round 4 of the triangle campaign opened its
instruments table mid-round, after the drift it was written to catch.

**Rule: an instrument with no in-tree receipt path in this table is `WRITTEN,
UNRUN`, and no file may describe it otherwise — including the lead's.** Status
is quotable only as a copy of a row here. `make gate-receipts` enforces the rule
mechanically over everything under `results/rook1/` and over
`docs/rook1-brief.md`; it checks that a receipt exists, not that it says what
the claim says. Reading the receipt is the numbers adversary's job.

Logs live in `results/rook1/logs/`.

| instrument | what it establishes | status | receipt |
|---|---|---|---|
| receipts gate | a planted claim (no receipt / absent file / remote path) is rejected; a real receipt is accepted | **RUN** | `results/rook1/logs/receipts_gate_selftest.log` |

Round 1 is desk-only: no engine, no fleet compute, no gate-1 work. Any lane that
wants a job files a request and the lead dispatches it; the row lands here with
an in-tree artifact path or it is not DONE.
