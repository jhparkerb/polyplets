# Round-4 idea queue — append-only

Opened 2026-08-12 by the lead, per `docs/triangle-round4.md`. Successor to
`results/triangle-r3-queue.md`, whose OPEN rows carry over by reference rather
than by copy: cite an r3 id directly (`L6-1`, `ADV-4`, `PROV-2`, ...) and file
the closure or successor here.

The round-3 protocol governs unchanged, with one standing amendment from the
round-4 brief: **never stop making ideas.** No condition in this file is a
reason to stop generating, and a closure without at least two successors of a
different kind is an incomplete deliverable.

## Protocol

- **Append only.** Never edit or delete another agent's row. To close a row,
  append a new row citing the id you are closing.
- Every closure files at least two successors, different in kind, not parameter
  tweaks. What would have to be different about the problem; is there an
  adjacent object where that holds; what did the obstruction prove about the
  family rather than the instance.
- Rows are cheap; file the half-formed ones. Cross-lane rows are wanted.
- **No agent runs compute** (`docs/r3-job-dispatch.md`, carried over). File a
  job request row here and the full field block in your deliverable; the lead
  dispatches to ayr or dalby.

## Row format

    | id | idea, one line | origin | status | note |

`id` is `<lane>-<n>`, r4 lanes prefixed `R4-` where they are new. `status` is
OPEN, DISPATCHED, CLOSED, or MERGED(id).

## Standing rank order for the triage pass

1. clears both entry-ticket levels over clearing level 1 only;
2. reaches the band (H = 15..21 at n = 40) at all, exact or modular, over
   reaching only smaller n;
3. cheapest checker to a reader, per `docs/skeptical-reader-standard.md`.

## State carried in from round 3

- **Banked this round, verified at recovery:** T(40,15) and T(40,16) exact by
  the B1 cancellation rule — 21.64% of a(40) two-sourced. Rows, logs and the
  producing source are committed at `results/cutcount_b1/` (`bd31a58`).
- **Remaining unconfirmed band:** H = 17..19 (22.20%), H = 20 (4.16%),
  H = 21 (2.84%).
- **Live pieces:** the H = 17..19 ladder, the L3-5 definition-level Lean proof
  (95.85%, no compute), INV-8 spin parity at H = 20..21.

## Rows

| id | idea, one line | origin | status | note |
|---|---|---|---|---|
| R4-1 | LG-JOB-1's premise may be false: `7b13137:cpp/cutcount_b1.cpp` already carries a `--modp` payload mode, and the dalby run's source is that file with the mode *removed* | lead, recovery diff 2026-08-12 | DISPATCHED (r4-a) | if the mode is complete, the residue binary needs authoring only for gates, and the ladder unblocks today |
| R4-A1 | **CLOSES R4-1: partly yes.** `--modp` shares the stencil and transitions by function (`successors`/`gather`/`shifted`/`canon`), the algebra is identical, and it self-reports `peak_rss_mb`/`states=` — so the *measurement* job needs zero C++ authoring. It is not production-ready: `H>16` is rejected (line 377), the q=1 binomial self-check is absent (payload is 2 coeffs not 3), `--assemble` has no mod-p compare, nothing does CRT, and the gate has no `--modp` coverage. Payload is **u32**, so prime width changes no code and no RAM — use 31-bit primes, 4+1 runs, not 15 | r4-a, `results/r4/r4-a.md` §1–§2 | CLOSED | the ladder unblocks for measurement tonight and for H=17 production after two small diffs (R4-A2, `H>16` guard) |
| R4-A2 | `Succ out[12]` (line 151, callers 189/230/316) is written with no bounds check and `b <= floor((H+3)/2)` fills it exactly at H=17/18 and **overflows at H=19**; the bound is ARGUED, not measured. Kill or confirm with `--modp`-free `--states 17 19 41` plus an instrumented max-successor counter (seconds), then widen to `out[16]` with an abort | r4-a §2.2 | OPEN | must be settled before ANY H>=17 run; a stack smash here would corrupt results silently, not crash loudly |
| R4-A3 | **JOB REQUEST LG-JOB-1R** (supersedes LG-JOB-1): marginal bytes/window and us/slot-col of the committed `--modp` at H=12..16 on dalby, one 31-bit prime, plus H=13 at five primes to rehearse CRT and RED-D. <=7.2 h, <=6.8 GiB, 1 core. Full field block in `results/r4/r4-a.md` §3 | r4-a §3 | OPEN | rides a NEW control the old request could not have: the recovered `C<H>.out` rows validate the residue path at H=16, 570x the state count of the gate's H<=10 |
| R4-A4 | **H=19 is not the tail of a ladder, it is a separate problem.** Priced from measured anchors, every in-RAM variant is 39–104 days serial; the binding unknown is whether this DP shards across cores at all (still ASSERTED, never run multi-core). Ask that question directly at H=14, where a 2/4/8-thread run costs 27 minutes, instead of inheriting the assumption at H=19 | r4-a §4.3 | OPEN | different in kind from the ladder rows: it tests the *parallelism premise* the whole phase-2 cost table rests on, at a height where being wrong is free |
| R4-A5 | The recovered exact rows generalize past B1: `results/cutcount_b1/rows/C<H>.out` is a per-height oracle to H=16 that **any** future second-source engine (residue, spin-parity/INV-8, a third rule) can be validated against at production state counts, exactly or mod p, before it is trusted above H=16. Promote it from "the B1 run's output" to a named repo fixture with its own gate, the way `results/ns_a40/perheight` already is | r4-a §4.4 | OPEN | different in kind: an infrastructure row, not a compute row — it lowers the entry cost of every subsequent independent-rule candidate |

## Queue end
