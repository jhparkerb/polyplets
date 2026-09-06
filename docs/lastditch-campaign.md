# Last ditch — the campaign record

2026-08-20, branch `lastditch`. The brief was one push for a breakthrough that
either confirms a(40) by a second algorithm or reaches past n = 40. This is
what happened, what it rests on, and what is still open. Entry point for
anyone picking it up cold.

**If you only read one file, read `results/confidence.md`** — the plain-terms
statement of how far each value can be trusted and why. This one is the
campaign record behind it.

## The two headline results

**a(41) = 393811462683918679824582849262105.** The first term of A006770 past
a(40). Heights 1..20 are enumerated -- 1..19 in the campaign itself (4.72 h on
40 cores, run-dir under 100 GB) and height 20 in the 9.6-hour sweep that landed
2026-09-05 and agreed with what the tower had predicted for it; heights 21..41
come from the diagonal tower. The classical route needed H = 21 at Nmax 41,
i.e. a(40)'s two tall phases — 9.6 h/48c and 36.4 h/32c with a 363.4 GB disk
peak. Neither was run. `results/a41/PROVENANCE.md`.

**a(n) is rule-independent for every n <= 39**, up from n <= 35, and a(40) is
short exactly one cell, `T(40,19)`. `results/undertow.md`.

Neither needed a new counting algorithm. Both came from noticing that
`results/second-sources.md` §1 was buying the wrong anchors.

## Undertow, in one paragraph

The grand form (`docs/proofs/grand-form.md`, Lean-complete) makes level `k` of
the diagonal tower carry exactly two new constants, so **any** two independent
linear equations pin it. The closure plan pinned each level from its two
cheapest *in-onset* cells — which are the two **tallest** cells on its
diagonal, and which is why row 40 needed H = 21. But Severance W3's ab-initio
`D_j(k)` makes every **below-onset** cell an equation too:

    T(2k+1-j, k+1-j) = P_k(2k+1-j) * 3^(2k-3k-j) + D_j(k)

and that cell sits `j` rows *shorter*. Sweep ceiling `(n+2)/2 -> (n-3)/2`.
No new theorem: the content is the choice of anchors, and two pieces of
machinery built for different purposes composing.

## What each artifact is

| file | what |
|---|---|
| `results/undertow.md` | the result, its checks, and its corrections |
| `results/undertow-picture.md` | the figures; regenerate with `scripts/undertow_picture.py` |
| `results/a41/` | the term, its provenance, the 19 swept rows |
| `results/motley-par/` | the parallel engine's record and receipts |
| `results/undertow.md` | three measured ladders + the methodology note |
| `docs/lastditch-ideas.md` | the candidate list, **including the closed doors** |
| `docs/five-terms-plan.md` | a(41)-a(45) from one sweep; proposed, not launched |
| `docs/undertow-review-brief.md` | the review brief, committed before any lane ran |
| `results/undertow-review-{A,B,C}.md` | the three Fable lanes |
| `results/undertow-review-queue.md` | the append-only queue and the lead's triage |

Code: `experiments/undertow_pin.py` (verify / audit / predict / emit),
`undertow_ri.py` (the rule-independent tower), `undertow_a41.py` (the
assembler), `lane_b_a41_recount.py` (an independent second implementation),
`undertow_congruence_gate.py` and `severance_w3_depth5_gate.py` (two gates),
`cpp/motley_par.cpp`, `tests/gate_motley_par.py`.

## What the review changed

Three Fable lanes audited it. **No circularity anywhere** — but three figures
the lead reported were inflated, and are corrected in place:

- "342 cells re-derived from shorter cells" is **189 enumerated** plus 153
  formula-vs-formula identities. The a(40) run *injected* its H >= 22 cells
  from `diagCoeffTable` rather than enumerating them
  (`results/ns_a40/PROVENANCE.md`: "Real sweeps H3-H21; H22-H40 via wired P_k
  closed forms"), so scoring a wired tower against them is guaranteed.
- "100 depth pairs" is 100 *pairs*; pairs share cells, so **~36** independent
  checks.
- a(39)/a(38)/a(37) "reassembled from short sweeps" contain **no Undertow at
  all** — the pin loop is empty at those n — and consume wired constants
  fitted to cells above their own stated cap.
- The `--predict` "`T(40,21)` match" is by construction and worth zero.

**What survives, and is the real result:** the audit's 189 enumerated cells
include `T(39,20)` and `T(40,21)` predicted from H <= 17 pins. Every level up
to 17 already had a holdout; **18 and 19 never did.** That is the first
independent cross-check wired `P_19` has ever had.

## The residual, named exactly

After the review's S-A4, `D_2` and `D_3` are two-source through k = 22
(pure-Python family DP against the C++ tables, re-verified by the lead with
the tables hidden). The entire non-two-source content of a(41)'s tower half is:

- **nine numbers** — the e=3 rows at k = 20, 21, 22 of
  `results/severance_w3_families_K22_e3.txt`, one C++ run, no overlap with the
  K=19 table, no Python check;
- **two cells** — `T(40,19)` and `T(39,18)`, level 21's single pin pair.

  (Corrected 2026-09-05, AUDIT-2026-09-02 M1: **three** integers, not nine —
  `sig`, `bb`, `pp` at e = 3, k = 21. The k = 22 row is truncated away by
  `D_series(4, 21)` and the k = 20 row is pinned by level 20's pair agreement.
  And the single pin pair is now three at depth 5, gated by
  `make gate-undertow-pairs`; `results/a41/PROVENANCE.md`.)

`experiments/undertow_congruence_gate.py` (in `GATE_TARGETS`) narrowed it
further: integrality of each below-onset cell forces a congruence on its
defect mod `3^(k+j)`, which gives `D_1(21)` its first check of any kind and
catches `D_4(21)` **transitively** through the pin it feeds. The last
uncovered degree of freedom is the *integer part* of the single-source
constants.

## The decision that follows

Lane B: every tower statement about `T(40,19)` contains `D_3(21)`, so two
tower routes agreeing checks the pinning cells and never the shared machinery.
**Only enumeration crosses assumption families.** Hence Motley `C_19` — not
depth 5, which buys agreement inside the same machinery even though it is now
priced at an affordable ~8.5-16 GB (corrected 2026-08-22 from the ~51 GB this
line asserted, `results/undertow.md`).

## Closed doors — with counterexamples, so they are not re-pitched

- **Dual-connectivity TM** (track the complement's 4-connectivity, planar
  hence non-crossing, recover components from `C = χ + holes`). The
  doomed-configuration prune forces you to carry the component count, and
  `b·Cat(b)` exceeds `Bell(b)` where it matters — 11,440 vs 4,140 at b = 8.
- **Per-level span cap in the family DP.** 9x faster, 5x smaller, and it
  **undercounts** (333 vs 339 at `(e,k) = (0,2)`, K = 9). A prefix's span is
  bounded by the *final* cluster's cell count, not its own: two 2-cell rows
  `{0,3}` over `{1,2}` are connected with span 3, and the first row alone
  spans 3 with two cells.
- **Depths 8-9**, and with them the route to a tower pinned entirely from
  strip-confirmed `H <= 14` cells. Dead on a measured ~6x per excess.
- **Strict freedom from fitting.** `(a_k,b_k)` is *equivalent* to the
  surplus-<=k cluster weights, which are connected-animal counts of the same
  species; every known route carries the frontier connectivity partition, ~20x
  per level. Family-level, not instance-level. `results/undertow.md`.

## What was open at the campaign's end, and what became of it

Two of the four have since run; the entries say which, and with what result.

- **The Motley ladder at Nmax 41** — DONE. `scripts/motley_ladder.sh` finished 2026-08-21: nine primes, peak 61.6 GB (`results/second-sources.md`, `results/cutcount_b1/rows41/README.md`).
  Heights 1..19, nine 16-bit primes, ~59 GB at the top height, ~25 h. It buys
  BOTH a(40)'s last cell and a(41) entire: `T(n,H) = C_H - 2C_{H-1} + C_{H-2}`
  needs every `C_H` at the same Nmax, and every banked Motley row stops at
  n = 40, so a(41) has no second rule under it until this finishes. An earlier
  launch of the same run at Nmax 40 would have bought only the first and was
  killed for it. Its gate went green first: the release path reproduces a
  banked H = 18 residue row byte for byte.
- **H = 20 sweep at Nmax 41** — DONE. (`scripts/dalby_a41_h20.sh`) — makes level 21's
  *output* a holdout against an enumeration. **~11 h / ~190 GB**; the 20-30 h
  / 450 GB this tree asserted before anything was measured is corrected in the
  script header. **RAN 2026-09-05: 9.63 h on 76 cores, rc = 0; the swept
  `T(41,20)` equals the tower's prediction** (`results/a41/PROVENANCE.md`).
- **Depth 5** — **~3.1 h / ~8.5 GB at 8 threads**, or 6.7 h / 16.1 GB on the
  pessimistic bound (measured 2026-08-22, `results/undertow.md`;
  this line asserted ~51 GB / ~23 h from a two-point slope).
  `severance_w3_depth5_gate.py` is
  written red-first and joins `GATE_TARGETS` the day the table exists.
- **The five-terms sweep** — disk-capped at Nmax 43 as things stand, and his
  call.

## The reach rule, for whoever picks this up

    k_max = hmax + J - 2,     rows complete for  n <= 2*hmax + J - 1

+1 row per depth, +2 per height — and depths are now *measured* steeper than
heights (~6x per excess against ~3x per height), so **heights are the better
buy**. Motley at hmax = 18 gives n\* = 39 with tables already on disk, 40 at
J = 5. Past that the construction is exhausted and n >= 41 needs sweeps.
