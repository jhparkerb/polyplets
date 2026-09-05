# Paper 1, §Reproducibility — source material

2026-08-06, sortie plan §8 item 2; **refreshed 2026-09-05** (unattended item
5) after AUDIT-2026-09-02. `paper/technical-report.tex`'s Reproducibility
section is empty and `paper/technical-report-gaps.md` calls it the report's
biggest hole; the 2026-09-04 decisions there make it the next section jasonp
writes. This file is the material for it: every claim, the number it rests on,
the command that regenerates that number, the gate that pins it, and the limit
past which the claim must not be pushed.

**This file proposes; it does not edit.** `technical-report.tex` is jasonp's
(memory: `paper-is-jasonps-words`). Nothing here is drafted prose — it is
checked content to write from.

Every number below was regenerated 2026-09-05 by
`experiments/paper1_reproducibility_check.py` (checks A–F, 0.1 s) from the
banked artifacts, not copied from the notes that first reported it; the
cell-provenance figures come from `scripts/provenance_table.py --check`, which
`make gate-provenance` runs. What changed since 2026-08-06: the colouring
second source (Motley) reached height 19 at the size row 41 needs; the
Undertow tower re-derives the wired diagonals from short cells; a(41) exists,
with an asterisk (B5); the kink-only cell count was 11 here and is 3; and
coverage is stated in cells only.

---

## 1. The claim the section has to defend

a(40) = 56749893611764175164545926946127 is correct, and so is the T(n,H)
triangle it was summed from, in a project where no reader can re-run the
computation. Five independent defences, in the order a referee meets them.
a(41) = 393811462683918679824582849262105 rides on the same five with one
stated gap (§6, §8).

## 2. Defence 1 — every production run re-derives everything below it

Each `maxn = N` run recomputes the whole height triangle rather than extending
a stored one, and byte-matches every prior computed term through n = N−1.
a(1)–a(18) additionally match what OEIS serves for A006770 today (checked live
2026-07-30 and 2026-09-05; the site's b-file is auto-synthesized from the DATA
field, which is worth a footnote if the claim is made in print).

Regenerated: all 40 rows of the per-height sweep sum to the banked terms
(`results/ns_a40/perheight/h*.out` against `results/b006770_upload.txt`,
check A). The a(41) sweep is another instance: its rows at n ≤ 40 agree with
the banked triangle on 760 cells (`results/a41/PROVENANCE.md`; the assembler
refuses to use the n = 41 row otherwise).

## 3. Defence 2 — Redelmeier, a second algorithm, to n = 22

A three-machine, three-architecture fleet run (24000 disjoint shards, ~120 h
wall per box, completed 2026-07-16) reproduced every row n ≤ 22
digit-for-digit against the transfer-matrix values. The two counters share no
counting logic: one grows cell sets, the other sweeps a column frontier.

Regenerated: `results/redelmeier_row22/combined.txt` against the banked terms,
check C, with a RED control that flips one digit and must break the agreement.
`make gate-g2` runs the Redelmeier engine against the oracle and fixtures on
every push, and since 2026-09-05 its rook/bishop and transpose checks fail on
empty engine output rather than passing vacuously.

Reach is the limitation: Redelmeier's cost is proportional to object count, so
n = 22 is where it stops. Nothing above 22 has a second *whole-term
enumeration*; the next two defences are per cell.

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
survive it. The genuinely disjoint axes are boundary granularity, accounting
layer, count representation and orchestration. Defence 4 is what crosses the
connectivity rule.

## 5. Defence 4 — Motley, a second source under a different counting rule

The colouring program (Motley, `cpp/motley_par.cpp`; the exact source of the Nmax-40 rows
is banked as `results/cutcount_b1/cutcount_b1.cpp.59e90660`)
never decides connectivity. It computes `A_n(q) = Σ_S q^{c(S)}` over n-cell
subsets weighted by component count, by a frontier DP over colour-coincidence
partitions in `Z[q]/(q²)`, and reads the connected count off a coefficient at
the end; the identity that makes this the cut-count is proved
(`docs/proofs/cutcount-identity.md`). It shares no code with either engine
above. This is the machine-work pointer jasonp chose for the report
(`technical-report-gaps.md`, 2026-09-04).

Results, all banked and gated:

- **Nmax 40, H ≤ 18** (`results/cutcount_b1/rows/`): 567 cells equal the
  triangle; C_18 reconstructed by CRT from four primes with the fifth held out
  and predicted at every n (`make gate-cutcount-assembly`).
- **Nmax 41, H ≤ 19** (`results/cutcount_b1/rows41/`, dalby 2026-08-20/21,
  ~22 h, nine 16-bit primes per height): **589 cells** with n ≤ 40 equal the
  triangle, and the **19 cells at n = 41** equal the kink engine's own sweep
  (`results/a41/h*.out`) — two engines, no shared code, on every swept cell of
  a(41). The held-out prime predicts every cell at every one of the 19 heights
  (779 cells, from the 171 residue rows banked 2026-09-05 in
  `results/cutcount_b1/residues41/`). Check F regenerates the 589 and the 19;
  `make gate-cutcount-assembly` pins all three numbers and
  `make gate-motley-crt` re-derives the C_18 and C_19 reconstructions.

What this settles, in the audit's words (AUDIT-2026-09-02 M2), which are the
words to use:

- **a(n) for n ≤ 35**: every cell either direct Motley or on a wired diagonal
  whose two anchors are Motley cells — two programs, no shared code.
- **a(36)–a(39)**: every cell direct Motley or a tower cell pinned on Motley
  cells and ab-initio constants (Defence 5); "no part depends on the original
  program" is true; "two programs sharing no code" applies to the direct
  cells only.
- **rows 40 and 41**: **19 swept heights two-source with no shared code;
  heights 20 and up one tower strategy pinned from Motley's data**, sharing
  the depth tables `D_j(20..21)` with the original route. Not "every cell
  covered by two independent programs" — that was the 2026-08-23 wording and
  the audit struck it.

Independence analysis: `results/cutcount_b1/PROVENANCE.md` and the review it
cites. The reach
Motley is credited with is derived from the banked rows *and verified against
the triangle* by `scripts/provenance_table.py` (a corrupt banked row shrinks
it), not hand-set.

## 6. Defence 5 — the pinned diagonals, with holdout discipline, and Undertow

The tall heights are composed rather than swept, from height-diagonal closed
forms P_k (k = n − H ≤ 19). The shape is a theorem (`docs/proofs/diagonal-law.md`,
Lean-complete): degree k, leading coefficient 25^k/k!, onset n ≥ 2k+1, two free
constants per level. Two kinds of check pin the constants.

**Holdouts against later sweeps.** Each P_k was fitted on real cells and then
held out against a real cell it did not see: P_15 → T(33,18), P_16 → T(35,19),
P_17 → T(37,20), P_18 → T(39,21), the last arriving as one row of the a(40)
run's real H = 21 sweep. Written up in `paper/polyplets-report.tex`'s
validation section. `make ns-gate-diag-pins` re-checks every wired P_k against
every real-swept in-onset cell and re-interpolates levels k ≤ 10 from real data
alone.

**Undertow: the same constants from short cells.** Below onset a cell obeys
`T(2k+1−j, k+1−j) = P_k(2k+1−j)·3^{−(k+j)} + D_j(k)` with `D_j` computed ab
initio from cluster-weight families (Severance W3; `D_2`, `D_3` two-sourced
Python against C++ to k = 22). Two depths pin a level from cells far below its
onset anchors, and:

- all 18 wired levels k = 2..19 are re-derived exactly from below-onset cells,
  160 depth pairs at depths ≤ 5, 0 wrong (`experiments/undertow_pin.py
  --verify --jmax=5`); 342 banked cells are predicted from shorter ones, 0
  wrong (`--audit --jmax=5`). This is the first check of any kind wired P_18
  and P_19 have had beyond their own fit points.
- a(41)'s heights 20–41 are the tower with levels 20 and 21 pinned below
  onset. Level 20: six depth pairs, five independent checks. Level 21: **three
  depth pairs at depth 5** through T(38,17), T(39,18), T(40,19), two
  independent checks (`make gate-undertow-pairs`, 2026-09-05). Until 2026-09-05
  it was one pair, and the guard cited for it — the 3-power congruence gate —
  tests integrality only: an error of 9 in one table entry moves a(41) by 9
  and passes it (measured; the gate's first RED control).

Regenerated: the three diagonals that can be stated in closed form —
T(n,n) = 3^(n−1), T(n,n−1) = 5(5n−9)3^(n−4),
T(n,n−2) = ½(625n²−2459n+1134)3^(n−7) — hold on every banked cell in range
(40, 37 and 36 cells respectively), check B, with a RED control that perturbs
each leading coefficient and must break the fit.

## 7. Coverage, in cells

The unit is the cell. A wrong cell ruins a(n) whatever its size, so a
percentage of a(n) carries no decision and is not reported (standing ruling,
2026-08-18; the 2026-08-06 version of this file tabulated shares and they are
withdrawn). Over the closed n ≤ 40 triangle, 820 cells
(`scripts/provenance_table.py --check`, all pinned):

| what | cells | source |
|---|---|---|
| recomputed exactly by at least one second source (Redelmeier n ≤ 22; fixed-height GFs H ≤ 10; recurrences H ≤ 4; strip H ≤ 14; Motley H ≤ 19; a wired P_k on a really-swept cell) | 628 | provenance table, tiers B G R S M P |
| strip engine alone | 469 | check D |
| the 2026-08-06 "honest" rule, R ∪ S ∪ (P ∩ {H ≤ 21}) | 592 | check D |
| no exact recount: wired P_k above H = 21, the formula holdout-validated elsewhere | 189 | tier F |
| no exact recount and no wired closed form | 3 <!--q:congruence_only.count@19=3--> | tier C only: T(39,20), T(40,20), T(40,21) <!--q:congruence_only.cells@19=(39,20),(40,20),(40,21)--> |
| of the 192 above, reproduced by the Motley-pinned tower (tier U, Defence 5) | 192 | `experiments/undertow_ri.py`, agreeing with the incumbent at every one |

The three cells in the fifth row are the kink-only cells of the triangle: each
computed by one enumeration, checked by the mod-4 subgroup congruence and
reproduced by the Motley-pinned tower, never enumerated a second time. (The
2026-08-06 version of this file listed **11** kink-only cells; Motley's reach
was H ≤ 16 then. It is 3.)

Per row, how the cells were produced (check E; H ≤ 21 was really swept in the
a(40) run, k ≤ 10 is where the diag-pins audit shows the level pinned by real
data alone):

| n | really swept, H ≤ 21 | wired P_k, k ≤ 10 | wired P_k, k > 10 |
|---|---|---|---|
| 29–32 | 21 | 8, 9, 10, 11 | 0 |
| 33 | 21 | 11 | 1 |
| 35 | 21 | 11 | 3 |
| 37 | 21 | 11 | 5 |
| 40 | 21 | 11 | 8 |

Row 40 by second source: 19 cells direct Motley (H ≤ 19); 21 cells from the
tower fitted to Motley's data, of which three <!--q:row40_residual.count@19=3-->
— T(40,20), T(40,21), T(40,22) — still rest on the incumbent's connectivity
rule under the anchor criterion of `results/residual-cells.md`.

## 8. What the section must not claim

- **Not** that the strip engine is a fully independent second implementation
  (§4). Motley is the one that crosses the connectivity rule (§5).
- **Not** that a(23)–a(40) are two-algorithm confirmed as whole terms. The
  two-algorithm *enumeration* frontier is 22. What can be said: every cell of
  every row n ≤ 39 is Motley-direct or Motley-pinned formula; rows 40 and 41
  are 19 swept heights two-source and the rest one tower strategy pinned from
  Motley's data.
- **Not** that every banked cell is second-sourced. Three are enumerated once:
  T(39,20), T(40,20), T(40,21) <!--q:congruence_only.cells@19=(39,20),(40,20),(40,21)-->.
- **Not** that a(41) carries a(40)'s validation. Its 19 swept heights are
  two-engine; its top 22 cells are the tower, every level overdetermined;
  nothing has enumerated T(41,20) (the H = 20 sweep at Nmax 41, ~11 h on
  dalby, unrun). `paper/technical-report-gaps.md` B5 has jasonp's asterisk
  decision and the 2026-09-05 status.
- **Not** that the tower's agreement with itself is a second source: the two
  fits of levels 20–21 share `D_j(20..21)` and the grand form (a theorem).
- **Not** that the strip check could be pushed further on this hardware. C_14
  measured ~38 GB; C_15 would need ~200+ GB. Motley at H = 20 is the same
  wall (`docs/b1-closure-plan.md` §3: H = 21 does not fit in RAM at any rung).
- P_19's two fit points, T(39,20) and T(40,21), carry no enumeration holdout.
  That is why `polyplets-report.tex` grades a(39) and a(40) T2⁻ rather than
  T2; the Undertow re-derivation of P_19 from short cells is a consistency
  check on banked values, not an independent confirmation of them.

## 9. The tier vocabulary already exists

`paper/polyplets-report.tex` §"Confidence tiers" defines T1 / T2 / T2⁻ / T3 in
jasonp's own words and tags every numeric claim with one, already updated to
the a(40) close: T1 = a(1)–a(22), T2 = a(23)–a(38), T2⁻ = a(39)+a(40) whose top
real-swept strata sit on the never-held-out k = 19 diagonal. The technical
report can adopt that table verbatim. Whether Motley's rule-independence to
n = 39 moves a(36)–a(39) is his call; nothing here changes the tier
definitions.

## 10. Gates and recipes

What is pinned automatically, and therefore what a reader can re-run in
minutes rather than CPU-months:

```
make gates                     # every gate, GREEN 2026-09-05 (time in the final make log)
make gate-g2                   # the Redelmeier engine against the oracle and fixtures
make gate-kink-oracle          # the kink kernel, every height real, vs the published a(1..18);
                               #   kink == column per height at maxn 16   (2026-09-05)
make gate-cutcount-assembly    # Motley's rows assemble to the triangle; held-out primes at every height
make gate-motley-crt           # C_18 and C_19 reconstructed from their residue rows
make gate-provenance           # the per-cell source table and its pinned counts
make gate-residual-cells       # every restatement of the residual figures, checked
make gate-undertow-pairs       # a(41)'s tower, level 21 three ways at depth 5
make gate-undertow-congruence  # the 3-power congruences on the unbanked defects
make ns-gate-diag-pins         # every wired P_k against every real-swept in-onset cell
python3 experiments/paper1_reproducibility_check.py   # every number in this file, A-F
python3 paper/verify_technical_report.py              # the report's own numerics
```

The last one is the model for how the report should be defended: a
self-contained re-checker that reads the paper's numbers and re-derives them.
Re-run 2026-09-05: **781 checks, 0 failures**.

## 11. Suggested shape

Seven paragraphs, no mathematics: the claim; the five defences in the order
above, Motley getting its own; the coverage table in cells with the three
once-enumerated cells named; the limits of §8 stated in the section rather
than in a footnote; the tier table; the recipes. The section's job is to let a
referee grade the claim without re-running it, and the coverage table plus §8
are what make that possible.
