# Paper 1, §Reproducibility — source material

2026-08-06, sortie plan §8 item 2. `paper/technical-report.tex`'s
Reproducibility section is empty and
`paper/technical-report-gaps.md` item 1 calls it the report's biggest hole.
This file is the material for it: every claim, the number it rests on, the
command that regenerates that number, the gate that pins it, and the limit
past which the claim must not be pushed.

**This file proposes; it does not edit.** `technical-report.tex` is jasonp's
(memory: `paper-is-jasonps-words`). Nothing here is drafted prose — it is
checked content to write from.

Every number below was regenerated 2026-08-06 by
`experiments/paper1_reproducibility_check.py` (0.05 s) from the banked
artifacts, not copied from the notes that first reported it. That script is
the section's backing evidence and carries its own RED controls.

---

## 1. The claim the section has to defend

a(40) = 56749893611764175164545926946127 is correct, and so is the T(n,H)
triangle it was summed from, in a project where no reader can re-run the
computation. Four independent defences, weakest to strongest in reach and
strongest to weakest in independence.

## 2. Defence 1 — every production run re-derives everything below it

Each `maxn = N` run recomputes the whole height triangle rather than extending
a stored one, and byte-matches every prior computed term through n = N−1.
a(1)–a(18) additionally match what OEIS serves for A006770 today (checked live
2026-07-30; the site's b-file there is auto-synthesized from the DATA field,
which is worth a footnote if the claim is made in print).

Regenerated: all 40 rows of the per-height sweep sum to the banked terms, so
the triangle and the term list are consistent artifact by artifact —
`results/ns_a40/perheight/h*.out` against `results/b006770_upload.txt`,
check A of the script.

## 3. Defence 2 — Redelmeier, a second algorithm, to n = 22

A three-machine, three-architecture fleet run (24000 disjoint shards, ~120 h
wall per box, completed 2026-07-16) reproduced every row n ≤ 22
digit-for-digit against the transfer-matrix values. The two counters share no
counting logic: one grows cell sets, the other sweeps a column frontier.

Regenerated: `results/redelmeier_row22/combined.txt` against the banked terms,
check C, with a RED control that flips one digit and must break the agreement.

Reach is the limitation: Redelmeier's cost is proportional to object count, so
n = 22 is where it stops. Nothing above 22 has a second *whole-term* source.

## 4. Defence 3 — the strip transfer matrix, a second source per cell

An independent strip engine sweeps a height-H strip column by column carrying a
king-connectivity partition state, computes the cumulative
`C_H(n) = Σ_{h≤H} (H−h+1) T(n,h)`, and recovers the triangle by the exact
second difference in H. It shares no enumeration code, no frontier, and no
state encoding with the kink NW-carry kernel that produced the banked triangle.

Result: **469 cells, 0 mismatches**, columns H ≤ 14 at every n ≤ 40
(dalby, 2026-07-30, ~8.6 h, rev 5239e73, `results/strip_C14_n40_run.log`).

Regenerated: 469 is exactly `|{(n,H) : 1 ≤ H ≤ min(14,n), n ≤ 40}|` — check D
recomputes it from the cell set rather than trusting the log.

**The independence must be scoped honestly, and `results/strip-engine.md`
already does it.** Do not write "independent" unqualified. It is disjoint from
the kink kernel; it is *not* a different connectivity idea (union-find over the
new column against the old column's labels, the same rule as the repo's own
reference oracle), so a shared misconception about king-connectivity would
survive it; and the Python reference and the C++ port are a transcription
check, not a second source. The genuinely disjoint axes are boundary
granularity, accounting layer, count representation and orchestration.

## 5. Defence 4 — the pinned diagonals, with holdout discipline

The tall heights are composed rather than swept, from height-diagonal closed
forms P_k (k = n − H ≤ 18), each of which was fitted on real cells and then
**held out** against a real cell it did not see. The full holdout chain
P_15 → T(33,18) … P_18 → T(39,21) is already written up in
`paper/polyplets-report.tex`'s validation section.

Regenerated: the three diagonals that can be stated in closed form —
T(n,n) = 3^(n−1), T(n,n−1) = 5(5n−9)3^(n−4),
T(n,n−2) = ½(625n²−2459n+1134)3^(n−7) — hold on every banked cell in range
(40, 37 and 36 cells respectively), check B, with a RED control that perturbs
each leading coefficient and must break the fit.

## 6. Coverage, stated three ways

The honest framing is `results/strip-engine.md`'s and it should survive into
the report. Over the closed n ≤ 40 triangle (820 cells), all four figures
regenerated today:

| figure | cells | share | what it counts |
|---|---|---|---|
| strip alone | 469 | 57.2% | the strip engine's own verified region |
| honest | 592 | 72.2% | + low-height recurrences and P_k credited **only** on really-swept cells |
| doc-style | 782 | 95.4% | + P_k credited everywhere in its onset — flattering, since a closed form is not a second source for a cell it generated |

Exact rule, so the figures are not folklore: cells are all (n,H) with
1 ≤ H ≤ n ≤ 40; `R` = H ≤ 4; `S` = H ≤ 14; `P` = diagonals k = n−H with
k ≤ 18 and n ≥ 2k+1. Then doc-style = |R ∪ P ∪ S| and
honest = |R ∪ S ∪ (P ∩ {H ≤ 21})|. Diagonal k = 19 is excluded deliberately:
P_19 is fitted-with-no-holdout and certifies nothing.

Cells are the flattering denominator, because the triangle's cells are wildly
unequal in size. By **mass**, the share of each late row inside the strip
engine's reach (regenerated, check E):

| term | mass in H ≤ 14 |
|---|---|
| a(37) | 53.8% |
| a(38) | 50.8% |
| a(39) | 47.9% |
| a(40) | 45.0% |

Do not confuse this with the holdout-confirmed mass (9.1% / 5.5% / 2.5% /
0.0%), which is a different quantity — closed-form cells later reached by a
real sweep, tabulated in `results/ns_a40/PROVENANCE.md`.

**The third mass split is the one a referee will actually ask for**, and the
repo prints it: how much of each term was really swept, how much came from a
closed form that later data confirmed, and how much rests on a closed form
conditionally. `scripts/verify_diagonal_pins.py` (`make ns-gate-diag-pins`,
ALL CHECKS PASS 2026-08-06) ends with exactly that decomposition —

| n | real sweep, H ≤ 21 | formula k ≤ 10 | formula k > 10, conditional |
|---|---|---|---|
| 29 | 99.9103% | 0.0897% | 0.0000% |
| 35 | 98.8042% | 0.0866% | 1.1092% |
| 40 | 95.8551% | 0.0054% | 4.1394% |

so the honest headline for a(40) is: **95.9% of the mass was enumerated, 4.1%
is composed from held-out closed forms**. The same script re-interpolates each
level from real data alone and re-checks every wired P_k against every
real-swept in-onset cell, which is what stops the composition from being
circular.

## 7. What the section must not claim

- **Not** that the strip engine is a fully independent second implementation
  (§4).
- **Not** that a(23)–a(40) are two-algorithm confirmed. They are not; the
  two-algorithm frontier is 22.
- **Not** that every banked cell is second-sourced. At the a(40) close the
  Grand tier has 30 anchors, 19 strip-second-sourced and **11 kink-only**:
  T(28,15), T(29,15), T(30,16), T(31,16), T(32,17), T(33,17), T(34,18),
  T(35,18), T(36,19), T(37,19), T(38,20).
- **Not** that the strip check could be pushed further on this hardware. C_14
  measured ~38 GB; C_15 would need ~200+ GB.
- P_19's two fit points, T(39,20) and T(40,21), carry no holdout. That is why
  `polyplets-report.tex` grades a(39) and a(40) T2⁻ rather than T2.

## 8. The tier vocabulary already exists

`paper/polyplets-report.tex` §"Confidence tiers" defines T1 / T2 / T2⁻ / T3 in
jasonp's own words and tags every numeric claim with one, already updated to
the a(40) close: T1 = a(1)–a(22), T2 = a(23)–a(38), T2⁻ = a(39)+a(40) whose top
real-swept strata sit on the never-held-out k = 19 diagonal (lines 57–59,
149–151, 197). The technical report can adopt that table verbatim; nothing in
it needs changing.

## 9. Gates and recipes

What is pinned automatically, and therefore what a reader can re-run in
minutes rather than CPU-months:

```
make gates                 # every gate; 3m05s on gympie, all GREEN 2026-08-06
make gate-g2               # the Redelmeier engine against the oracle and fixtures
make gate-strip-cert       # RED-first self-test of the strip certificate checker
make ns-gate-diag-pins     # every wired P_k against every real-swept in-onset cell
python3 experiments/paper1_reproducibility_check.py   # every number in this file
python3 paper/verify_claims.py                        # the report's own numerics
```

The last one is the model for how the report should be defended: a
self-contained re-checker that reads the paper's numbers and re-derives them.
Re-run 2026-08-06: **428 checks passed, 0 failed, 0 skipped**. (HANDOFF records
448/448 at the a(40) close; the count moved with the report's own trim, not
with a failure.)

## 10. Suggested shape

Six paragraphs, no mathematics: the claim; the four defences in the order
above; the coverage table with the honest figure quoted and the doc-style one
either dropped or shown alongside it; the limits of §7 stated in the section
rather than in a footnote; the tier table; the recipes. The section's job is
to let a referee grade the claim without re-running it, and the coverage table
plus §7 are what make that possible.
