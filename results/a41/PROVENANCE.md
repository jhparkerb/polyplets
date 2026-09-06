# a(41) provenance

    a(41) = 393811462683918679824582849262105

Computed 2026-08-20 on dalby, branch `lastditch`. **The first term of A006770
past a(40)** — and the first computed without sweeping the two tall poles.

## How

Two halves, per `results/undertow.md`:

- **heights 1..19, real sweep**, `scripts/dalby_a41_low.sh`:
  `orchestrate --maxn 41 --kernel kink --counter u128 --cores 40 --ram 1GiB
  --overlap-heights 19 --heights 1-19`. Rows in `results/a41/h*.out`.
  **wall 16,998.7 s (4.72 h) on 40 cores, cpu 605,643 s, rss_max 557 MB**,
  run-dir peak well under 100 GB.
- **height 20, real sweep, 2026-09-05** (`scripts/dalby_a41_h20.sh`, dalby, 76
  cores, 9.63 h; section "The H = 20 sweep landed" below): `results/a41/h20.out`,
  equal to the tower's prediction for `T(41,20)`.
- **heights 21..41, the diagonal tower**, `experiments/undertow_a41.py`:
  levels k = 41-H = 0..20, with k <= 19 from the wired table and k = 20 pinned
  from BELOW-onset cells (Undertow); `T(41,21)` is exactly at onset on level
  20. Until 2026-09-05 the tower also supplied `T(41,20)` as depth 2 on level
  21, carrying the exact `D_2(21)` defect; that cell is now swept and the value
  agreed.

The classical rule would have needed a real sweep to H = 21 at Nmax 41 — the
a(40) run's two tall phases were 9.6 h/48c and 36.4 h/32c with a **363.4 GB**
disk peak. Neither was run.

Twenty-two of the forty-one cells are therefore formula, not enumeration. The
rule that permits that — shape proved, cell inside a **proved** onset,
constants pinned from real cells with a holdout — is written once in
`results/confidence.md` and governs the diagonal-mirror tower as well. This
tower meets all three: the shape and the onset `n >= 2k+1` are theorems
(`docs/proofs/diagonal-law.md`), the onset was proved sharp 2026-09-05, and
every level below is overdetermined. The diagonal-mirror tower fails the second
condition and its assembled term stays conjecture-assisted
(`results/related-seqs-n33.md`).

What the rule does **not** cover is the one thing that actually limits this
term, and the sections below are about it: the depth-`j` corrections `D_j` let
levels 20 and 21 be pinned from cells *below* onset, and those corrections were
checked against banked cells only at `k <= 19`.

## Checks, all of them

- **The sweep's own regression: 760 banked cells agree, 0 disagree.** A run at
  Nmax 41 also re-produces every row n <= 40 at every height it sweeps, and
  those rows are banked. `undertow_a41.py` refuses to use the n = 41 row unless
  they match and unless at least 200 cells were compared.
- **Row-40 regression, on a separate tower with row 40 excluded from its own
  pinning set**: 21 cells reproduced, 0 wrong, and the banked row re-sums to
  a(40) exactly. Two towers are built deliberately — pointing one at both jobs
  makes the regression either circular or vacuous.
- **Edges exact**: `T(41,41) = 3^40` and `T(41,40) = (25n-45)*3^37`.
- **Growth**: `a(41)/a(40) = 6.9394`, continuing 6.9212, 6.9261, 6.9308,
  6.9352. The successive differences are 0.0049, 0.0047, 0.0044, **0.0042** —
  monotonically shrinking, as a series converging to λ ≈ 7.1 must.
- The method itself: 18 levels re-derived exactly from below-onset cells
  (100 depth pairs, ~36 of them independent), an audit in which **189
  enumerated** banked cells come back from shorter cells with 0 wrong, and
  `a(n)` rule-independent for every n <= 39. `results/undertow.md`, as
  corrected by `results/undertow-review-A.md` — the earlier "342 cells" and
  "four terms reassembled from short sweeps" figures were inflated and are
  struck there.

## Independently recomputed

Lane B of the review (`results/undertow-review-B.md` §5,
`experiments/lane_b_a41_recount.py`) rebuilt the term by a route built to
differ wherever difference was possible: levels k = 1..19 pinned from their two
**onset anchors** in `results/triangle.txt` rather than read from
`diagCoeffTable`, level 20 pinned from depths (1,2) with (3,4) held out — a
different overdetermination cut from the assembler's — and its own polynomial,
grand-form, solver and assembly code throughout. `undertow_a41.py` is never
read or imported.

**AGREE**, and the lead re-ran it rather than taking the report's word:

    anchor-pinned k<=19 predict banked in-onset cells: 342 ok, 0 wrong
    imported D_j vs own empirical extraction at k<=19: 70 ok, 0 wrong
    level 20 pinned from depths (1,2); depths 3 and 4 hold out OK
    T(41,21) = 12639811314502944123098075912198   (level 20, at onset)
    T(41,20) = 18004779862205054677763902712770   (level 21, depth 2)
    a(41) recount = 393811462683918679824582849262105  -- AGREE

Because it never touches the wired table, the agreement additionally says the
wired `diagCoeffTable` is consistent with a fresh fit to its own onset anchors.

**What the agreement is worth, in Lane B's own grading: CLEAN as a second
implementation, NOT a second source.** It retires assembly, transcription,
fencing and arithmetic error across two disjoint codebases — the class that
produced the Zero Harvest incident and the lead's own `hmax` bug tonight. It
does not touch what the two routes share: `D_j` at k = 20, 21, the pinning
cells `T(40,19)`/`T(39,18)`, and the grand-form theorem (Lean-complete, so
shared *theorem* rather than shared *risk*).

### One real, weak check on D_2(21)

`T(41,20) = P_21(41)*3^(41-1-63) + D_2(21)` — the main term carries `3^-23`,
and `D_2(21) = 1534183878653401344302049616588 / 94143178827` with
`94143178827 = 3^23` exactly. Integrality of `T(41,20)` therefore forces
`P_21(41) + N == 0 mod 3^23`. It is weak and it is mod a single prime power,
but it is **the only check `D_2(21)` currently has**, and the assembler's
integrality assert is what enforces it.

## The one weak point, stated plainly — and closed at depth 5 (2026-09-05)

`T(41,20)` sits on level 21. At depths j <= 4 **level 21 pins from a single
depth pair** — `T(40,19)` and `T(39,18)` — with **no independent check at its
own level**:

    level k=20 pinned from [(36,16), (37,17), (38,18), (39,19)], 6 pairs, 5 independent checks
    level k=21 pinned from [(39,18), (40,19)],                   1 pair,  0 independent checks

(The 2026-08-20 text of this section gave level 20 as "3 pairs, 2 independent
checks"; that was the `--jmax 3` count. At `--jmax 4`, the recipe the run used,
it is 6 and 5. AUDIT-2026-09-02 M1.)

**What the single-source constant's stated guard was worth.** The congruence
gate of 2026-08-24 was described, here and in `results/confidence.md`, as
constraining `D_4(21)` transitively. It constrains its fractional part only.
A shift Δ in `D_4(21)` moves `T(41,20)` by 9Δ, and every single-entry error in
the e = 3 row of `results/severance_w3_families_K22_e3.txt` enters `D_4(21)`
with a coefficient in (1/9)Z, so every error a real table can carry is an
integer shift of a(41), invisible to an integrality test. Measured 2026-09-05
on a shadow copy of the table: `sig[3][21] + 9` leaves
`gate-undertow-congruence` green and moves the depth-4 assembler's a(41) by
exactly 9. The exposed surface was three integers — `sig`, `bb`, `pp` at
e = 3, k = 21 — not the "nine numbers" of `docs/lastditch-campaign.md`: the
k = 22 row is truncated away by `D_series(4, 21)` and the k = 20 row is pinned
by level 20's pair agreement.

**Depth 5 closes it.** `results/severance_w3_families_K21_e4.txt` (banked
2026-08-23, `results/depth5-gate-green.md`) supplies `D_5`, and at `--jmax 5`
level 21 gains `T(38,17)`, a Motley-covered cell:

    python3 experiments/undertow_a41.py --jmax 5 --perheight results/a41
    level k=20 pinned from [(36,16), (37,17), (38,18), (39,19)] (tallest H=19), 6 pair(s), 5 independent check(s)
    level k=21 pinned from [(38,17), (39,18), (40,19)] (tallest H=19), 3 pair(s), 2 independent check(s)
    sweep vs banked triangle: 760 cells agree, 0 disagree
    a(41) = 393811462683918679824582849262105

`pp[3][21]` enters `D_4(21)` but not `D_5(21)`, and `sig`, `bb` enter the two
with different coefficients, so any single-entry error in that row makes the
three pairs disagree and `build()` refuses. Also run 2026-09-05:
`undertow_pin.py --verify --jmax=5`, 18 levels re-derived exactly over 160
depth pairs, 0 wrong; `--audit --jmax=5`, 342 banked cells predicted from
shorter cells, 0 wrong.

Gated: `make gate-undertow-pairs` (`experiments/undertow_pairs_gate.py`)
rebuilds the depth-5 tower with the pin cells and pair counts pinned, requires
a(41) from `results/a41/h*.out` plus the tower to equal the value above, and
carries five RED controls, each refused at depth 5: the +9 mutation measured
end to end (congruence gate green, depth-4 shift 9, depth-5 refusal), `bb` and
`pp` at (3, 21), the K21_e4 table's own e = 4 row, and a corrupted pin cell.

**What remained open, and closed 2026-09-05 21:19 EDT.** Three pairs agreeing
is agreement between fits that share `D_j(20..21)` and the grand form; it is
not an enumeration of `T(41,20)`. The assumption-disjoint holdout of that cell
was the H = 20 sweep at Nmax 41, and it has now run: see the next section. The
swept cell equals the tower's prediction digit for digit.

## The H = 20 sweep landed (2026-09-05)

`scripts/dalby_a41_h20.sh`, dalby, rev `b88b38bc5`, kink kernel, u128, fold,
76 cores, `--max-diag-k -1` (nothing injected). Started 11:41 EDT at jasonp's
word, finished 21:19:14 EDT, rc = 0. From `runs/a41_h20/run.log`:

    wall=34678.8s cpu_s=1766882.070 wall_s=1987133.775 rss_max_mb=814.7

9.63 h on 76 cores against the script header's 10-11 h on 48. Per-column
profile (`runs/a41_h20/cost_profile.tsv` on dalby, banked here as
`results/a41/h20_cost_profile.tsv` with the run.log summary line): the frontier peaks at
129,487,745 records at column 7, and columns 6-8 each take ~2,300 s of wall at
~126,000 cpu-s. The run directory is 860 KB after the orchestrator's own
cleanup, so the disk peak is not recorded (the header predicted 185-190 GB;
nothing measured it).

    T(41,20) = 18004779862205054677763902712770    swept
    T(41,20) = 18004779862205054677763902712770    tower, level 21 depth 2 (above)

Banked as `results/a41/h20.out` (this file's `h*.out` set is now H = 1..20).
The sweep's rows at n <= 40 agree with the banked triangle on all 40 cells of
column H = 20, including `T(40,20)` (same kernel at a different Nmax, so a
regression, not a second source). Re-assembly with the swept height:

    python3 experiments/undertow_a41.py --jmax 5 --perheight results/a41
    heights swept: 1..20;  heights from the tower: 21..41
    sweep vs banked triangle: 800 cells agree, 0 disagree
    a(41) = 393811462683918679824582849262105

What changes: a(41) no longer depends on `P_21` at all (H = 21 is level 20 at
onset, pinned ten ways at depth 5 once `T(40,20)` joins its pins), and the
tower's top level has the one holdout that crosses assumption families. What
does not change: heights 21-41 are still formula; the colouring second source
still stops at H = 19, so `T(41,20)` has one enumeration and one formula
prediction, not two enumerations.

Gated: `make gate-undertow-pairs` now also compares the swept `T(41,20)` with
the tower's prediction for it, the tower built without that cell among its
pins, and carries a sixth RED control (the swept value +1 in a shadow copy of
`results/a41` is reported).
