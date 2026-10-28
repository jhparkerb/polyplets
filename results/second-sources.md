# Recounts of the triangle by other programs

`T(n,H)` is the number of fixed polyplets (king-connected sets of `n` cells)
whose bounding box has height `H`; `a(n) = Σ_H T(n,H)` is A006770. The
production transfer matrix (`core/kink.h`, `core/transition.h`) produced every
entry to `n = 40` (`results/triangle.txt`) and heights `1..20` of row 41
(`results/a41/`). Three other programs recount parts of the triangle. This
file is the detailed record behind `results/confidence.md`: what each program
computes, what it shares with the production engine, which runs were made,
and what no recount reaches.

| program | code | reach | shared with the production engine |
|---|---|---|---|
| strip transfer matrix | `cpp/strip_tm.cpp`; reference `experiments/strip_engine.py` | `H ≤ 14`, `n ≤ 40` | the connectivity rule (union-find over a column, stranded-component death); no code, frontier or state encoding |
| the coloring recount | rule `results/coloring-recount/cutcount_b1.cpp.59e90660` lines 93–173; parallel engine `cpp/coloring_recount.cpp` | `H ≤ 19`, `n ≤ 41` | nothing: it never decides connectivity |
| Redelmeier enumeration | `cpp/g2_redelmeier.cpp` (`build/g2`) | whole rows `n ≤ 22` | nothing; its cost grows with the count |

Which program reached which entry is generated in `results/provenance-table.md`
(`make gate-provenance`); the entries no exact recount reaches, in
`results/residual-cells.md` (`make gate-residual-cells`).

## The strip transfer matrix

A strip of height `H` is processed column by column, carrying the partition of
the current column's occupied rows into king-connected components. With the
leftmost occupied column fixed and every vertical placement counted, it returns
`C_H(n) = Σ_{h ≤ H} (H − h + 1) · T(n,h)`, and the triangle is the exact second
difference

    T(n,H) = C_H(n) − 2 C_{H−1}(n) + C_{H−2}(n),     C_0 = C_{−1} = 0.

The minimal recurrences of `C_H` have orders 1, 2, 4, 9, 29, 68, …, which the
engine reproduces (the `q_H` of `results/diagonal-formula.md`).

**Independence.** Disjoint from the production kernel: no shared code,
frontier or state encoding. Not a different connectivity rule: its union-find
with stranded-component death is the rule of the reference column oracle
`core/transition.h`, written independently, so a shared misconception about
king connectivity would not be caught. The Python reference and the C++
program were written together; their agreement on every `C_H`, `H ≤ 10`, is a
transcription check. The brute-force anchor (`brute_T` in
`experiments/strip_engine.py`) is independent of both, agrees exactly for
`n ≤ 9`, and exists only in the Python reference
(`results/strip_engine_python_run.log`, `Hmax 10`, `Nmax 14`).

**Result.** Every entry computed matches the production triangle.

| run | entries confirmed | log | machine, date, wall |
|---|---|---|---|
| `Hmax 10` | 315 | — | ~5 s |
| `Hmax 13`, `n ≤ 36` | columns `H ≤ 13` | `results/strip_engine_run.log` (C++ output despite the name; `C_13` 606 s) | ~730 s |
| `Hmax 14`, `n ≤ 36` | 413, 0 mismatch | `results/strip_C14_run.log` | dalby 2026-07-22, ~7.5 h (`C_14` 22,919 s) |
| `Hmax 14`, `n ≤ 40` | 469, 0 mismatch | `results/strip_C14_n40_run.log`, rev `5239e73` | dalby 2026-07-30, ~8.6 h (`C_14` 25,892 s) |

The first C++ run stopped after `C_13`, so its end-of-run comparison never
ran. `C_14` needs about 38 GB; `C_15` would need over 200 GB.

Redelmeier confirms whole rows only to `n = 22`; the strip's cost grows as about
`2^H` whatever the count, so it confirms columns `H ≤ 14` at every `n` to 40.
When a(40) was first computed, the closed forms `P_k`, `4 ≤ k ≤ 18`, had 30 fit
entries, 19 inside the strip's reach and 11 outside (the Lean development counts
level 3's two cells as well, hence its 32): T(28,15), T(29,15), T(30,16),
T(31,16), T(32,17), T(33,17), T(34,18), T(35,18), T(36,19), T(37,19), T(38,20).
The coloring recount at `H ≤ 19` later recounted all but T(38,20).

**Coverage, three ways**, over the 820 entries `1 ≤ H ≤ n ≤ 40`: `R` =
`H ≤ 4` (recurrences); `S` = strip, `H ≤ 14`; `P` = closed forms `P_k` on
diagonals `k = n − H ≤ 18` with `n ≥ 2k + 1` (diagonal 19 excluded: `P_19`
was fitted with no entry held back and would add only its two fit points,
T(39,20) and T(40,21)). The first figure is `|R ∪ P ∪ S|`; the second is
`|R ∪ S ∪ (P ∩ {H ≤ 21})|`, a closed form not being a recount of an entry it
produced.

| figure | strip `n ≤ 36` | strip `n ≤ 40` |
|---|---|---|
| with every closed-form entry | 742 (90.5%) | 782 (95.4%) |
| closed forms only where enumerated | 552 (67.3%) | 592 (72.2%) |
| strip alone | 413 (50.4%) | 469 (57.2%) |

`experiments/paper1_reproducibility_check.py` recomputes the right-hand column
and `scripts/provenance_table.py` checks it. These are counts of entries, not
shares of a term: a term is wrong if any one entry is wrong.

**Complexity (C++).** Partition states per height 1, 3, 8, 20, 50, 126, 322,
834, 2187, 5797, …, about 2.65× per height; wall about 6× per height
(`H = 10`: 3.5 s). `__int128` suffices for `n ≤ 40`, `H ≤ 15` since
`C_H(n) ≤ H · a(n) < 1.7·10^38`; the state packs 4 bits per row, so `H ≤ 15`.

## The coloring recount

Write `A_n(q) = Σ_S q^{c(S)}` over the `n`-cell subsets `S` of the strip, with
`c(S)` the number of king-connected components; the connected count is
`[q^1] A_n(q)`. The program computes it by a frontier dynamic program over
color-coincidence partitions of the last `H + 1` cells in scan order, in
`ℤ[q]/(q^2)`: a cell with no earlier occupied king neighbor adopts a live color
or takes a fresh one at weight `q − b`; a cell whose earlier neighbors carry
two colors contributes 0. No union-find, no stranded-component death, no
completion predicate. That the sum of the weights is `q^{c(S)}` exactly in
`ℤ[q]` is the cut-count cancellation identity, the Potts spin form of the
Fortuin–Kasteleyn correspondence, proved in `docs/proofs/cutcount-identity.md`
and checked by brute force on 10 boards and 223,000 subsets
(`experiments/birthright_identity_check.py`). The output is the strip's
`C_H(n)` and the triangle the same second difference.

The self-checks `q0_zero` (`[q^0] A_n = 0`) and `q1eval_binomial`
(`A_n(1) = C(HW, n)`) follow from the identity and consult no connectivity: a
stencil defect anchored at the bottom row passes both. Only comparison against
independently computed entries catches the rule going wrong.

**Runs**, Nmax 40 unless stated. The single-thread engine `cutcount_b1` was
built on the `second-source` branch (`48ac108` for step 0, `4df3fec9` after);
this tree holds only its rule source.

| run | payload | date | script, outputs | agreement | cost |
|---|---|---|---|---|---|
| calibration, `H ≤ 16` | exact 256-bit; source sha `59e90660` | dalby 2026-08-11 | — | 640 of 640 entries match `results/triangle.txt` | `H = 16`: 16,475 s, 60.8 GB |
| step 0, `H ≤ 16` | exact; clean build `git=48ac1089`, binary sha256 `e66f4466…` | dalby 2026-08-14 | `scripts/dalby_coloring_step0.sh` | 16 rows identical to calibration; 640 of 640 | three streams: `H = 16` 17,047 s, 62.3 GB; `H = 15` 4,806 s, 20.4 GB; `H ≤ 14` ~2,400 s, 6.9 GB; 88 GB together |
| `H = 17` | exact 128-bit; build `4df3fec9`, sha256 `dd173239…` | dalby 2026-08-14 | `scripts/dalby_coloring_h17.sh`; `results/coloring-recount/rows/C17.out` | T(n,17), `n = 17..40`: 24 of 24 | 39,117 s (10.9 h), 95.0 GB, 23,681,423 states |
| `H = 18` | five 31-bit primes, one pass each; CRT from four, the fifth predicted | dalby 2026-08-14 to 08-19 | `scripts/dalby_coloring_h18.sh`; `results/coloring-recount/rows/C18.out`, `results/coloring-recount/residues/` | T(n,18), `n = 18..40`: 23 of 23; prime 2147483563 predicted at 40 of 40 | 399,700 s on one core (4.63 days), 65.9 GB, 72,487,711 states |
| Nmax 41, `H ≤ 19` | nine 16-bit primes per height; eight reconstruct, the ninth must predict every entry | dalby 2026-08-20 to 08-21, rev `18b90ab6` | `scripts/coloring_ladder.sh`; `results/coloring-recount/rows41/`, `results/coloring-recount/residues41/` | 589 entries `H ≤ 19`, `n ≤ 40` match the triangle; 19 entries at `n = 41` match `results/a41/h<H>.out`; ninth prime predicted at all 19 heights | `H = 19`: nine passes of ~5,630 s, peak 61.6 GB, 80 threads |

The `H = 18` passes:

| prime | wall s | peak RSS MB |
|---|---|---|
| 2147483647 | 80,632.9 | 65,943.7 |
| 2147483629 | 80,614.0 | 65,945.9 |
| 2147483587 | 79,069.6 | 65,941.4 |
| 2147483579 | 79,039.5 | 65,946.1 |
| 2147483563 (predicted) | 80,344.3 | 65,941.8 |

The passes agree within 2.0% on wall. Against `H = 17` the mod-p payload
traded wall for memory: 2.05× the wall per pass, 0.69× the peak, five passes
for one. The ratios measured at `H = 16 → 17`, wall ×3.198, peak ×2.963,
states ×3.023, sit against ×3.209 and ×2.984 from the census
`Σ_k C(H+1, 2k) · Bell(k)`. The `H = 16` baseline of those ratios, 12,231 s
and 32.06 GB with the 128-bit payload, has no run record in the tree beyond
this line.

**Provenance.** The calibration rows came from a source (sha256
`59e90660b42a0d94ceae5459287db35b4d93f87a5e62753ccd549235edaa8d3d`) matching
neither committed revision on `second-source`; the diff against `7b13137` is
71 lines, almost all the removal of its `--modp` mode
(`results/coloring-recount/PROVENANCE.md`). Step 0 reproduced its 16 rows from a
clean build. `C18.out` has sha256
`26b4fa322303c8b26798c41dd0daafb698bd6909ab440a834a0eb95bbd0aeb81`.

**Checks.** `make gate-cutcount-assembly` (`scripts/cutcount_assembly_gate.py`)
assembles the rows against `results/triangle.txt` (567 entries from `rows/`,
589 from `rows41/`), compares `rows41` at `n = 41` against `results/a41/` (19
entries), reconstructs `C_18` from four primes and predicts the fifth, and
re-derives the ninth-prime verdict at all 19 heights of the Nmax-41 run (779
entries), with 16 controls that must fail. `make gate-coloring-crt`
(`scripts/coloring_crt.py --selftest`) reconstructs `C_18` and `C_19` and
confirms a corrupted residue is caught. `tests/gate_coloring_recount.py` checks the
parallel engine against the exact rows at three payload widths and for
thread-count determinism (needs `-fopenmp`).

**The parallel engine** (`results/coloring-recount/parallel/README.md`) keeps the five rule
functions and replaces the accounting: flat open-addressed table, OpenMP over
source rows, payload width from the prime, release of each consumed chunk. At
`H = 14` it is 50× the single-thread engine on 80 threads; it reproduced all
five `H = 18` residue rows at about 3,350 s per prime against about 79,940 s;
its `H = 19` census is 224,529,648 states.

## Redelmeier whole-row recounts

`build/g2` (`cpp/g2_redelmeier.cpp`) generates every fixed polyplet once and
shares no counting logic with either transfer matrix.

**Row 20** (`results/redelmeier_row20/`): dalby,
`scripts/g2_wholerow.sh 20 10 800 80`, 2026-07-10, rev `7eab237`. Rows
`n = 1..20` match `results/b006770_upload.txt`; a(20) = 1025573519362016 is
confirmed by two algorithms, and A030233, A030222 and A194596 inherit the
confirmation at `n = 20`.

| quantity | value |
|---|---|
| wall | 28,684 s (7.97 h) |
| core-seconds | 2,204,116 (96.1% utilization of 80 workers) |
| shard wall s: mean, median, p99, max | 2,755, 2,752, 3,092, 3,188 |
| full-cost nodes (size ≤ 19) | Σ a(1..19) ≈ 1.777·10^14 |
| cost per node | 12.4 ns ≈ 37 cycles (Neoverse N1, 3.0 GHz) |

**Row 22** (`results/redelmeier_row22/PROVENANCE.md`): three machines,
2026-07-11 to 07-16, 24,000 shards; every row `n ≤ 22` matches.

## What the recounts leave uncovered

Exact recounts: Redelmeier `n ≤ 22`; strip `H ≤ 14`; the coloring recount
`H ≤ 19`; small-height recurrences `H ≤ 4`; decorrelated fixed-height
generating functions `H ≤ 10`; the closed forms `P_k` where an enumeration
also reached the entry. Every entry also carries the mod-2 and mod-4
congruence of the height-preserving subgroup census
(`results/symmetry-classes.md`), which catches an error only if the error is
nonzero mod 4.

| coloring recount reach | congruence-only entries: no exact recount, no closed form <!--q:prose--> |
|---|---|
| `H ≤ 17` | 11 <!--q:congruence_only.count@17=11--> |
| `H ≤ 18` | 6: (38,19), (39,19), (39,20), (40,19), (40,20), (40,21) <!--q:congruence_only.count@18=6--><!--q:congruence_only.cells@18=(38,19),(39,19),(39,20),(40,19),(40,20),(40,21)--> |
| `H ≤ 19`, where it stands | 3: (39,20), (40,20), (40,21) <!--q:congruence_only.count@19=3--><!--q:congruence_only.cells@19=(39,20),(40,20),(40,21)--> |

A second question is which entries of row 40 still rest on the production
engine's connectivity rule: those with `h ≤ 21` until the coloring recount
reaches `h`, and those with `h ≥ 22`, computed from `P_k` at `k = 40 − h`,
until both fit points `T(2k+1,k+1)` and `T(2k+2,k+2)` are inside its reach.

| coloring recount reach | row 40 entries on the production rule | a(n) closed by overlap of the recount and closed forms |
|---|---|---|
| `H ≤ 17` | 7 <!--q:row40_residual.count@17=7--> | `n ≤ 33` <!--q:closure_n@17=33--> |
| `H ≤ 18` | 5 <!--q:row40_residual.count@18=5--> | `n ≤ 35` <!--q:closure_n@18=35--> |
| `H ≤ 19` | 3: T(40,20), T(40,21), T(40,22) <!--q:row40_residual.count@19=3--><!--q:row40_residual.cells@19=(40,20),(40,21),(40,22)--> | `n ≤ 37` <!--q:closure_n@19=37--> |
| `H ≤ 20` | 1 <!--q:row40_residual.count@20=1--> | `n ≤ 38` <!--q:closure_n@20=38--> |
| `H ≤ 21` | 0 <!--q:row40_residual.count@21=0--> | `n ≤ 39` <!--q:closure_n@21=39--> |

Both counts reach zero only at `H = 21`, which does not fit in memory (below).
Fitting each level from entries below the range where its formula holds, with
the exactly known defect (`results/below-onset.md`, `results/below-onset-fit.md`),
gives a(n) rule-independent for every `n ≤ 39` with the coloring recount at
`H ≤ 18`; that route is one formula strategy fitted from the recount's data,
not a second enumeration, and the provenance table carries it as tag U.

## The height an enumeration must reach

`P_k` holds for `n ≥ 2k + 1`, its onset (the shape is the theorem of
`docs/proofs/diagonal-law.md`); its two free coefficients were fitted from two
enumerated entries, cheapest at `T(2k+1,k+1)` and `T(2k+2,k+2)`. Row 40: 20
entries at `H ≤ 20` enumerated; T(40,21) enumerated and also `P_19`'s second
fit point; 19 entries at `H ≥ 22` from `P_k`, `k ≤ 18`, never enumerated.
Every fit point of `k ≤ 18` lies at `H ≤ 20`, so a coloring run to `H = 20`
at Nmax 40 makes every entry of row 40 but T(40,21) rule-independent at no
additional compute, with checks inside the run (`P_5`'s diagonal continues
through `H = 8..21`, thirteen entries past its fit points; `P_17` two; `P_18`
one, T(39,21)). The formula is cheaper than enumeration for T(40, 40−k) only
when `k + 2 < 40 − k`, i.e. `H > 21`, so no height at or below 21 is skipped.
For a target `n` the enumeration must reach `H ≤ ⌊(n+2)/2⌋` at Nmax `n`:

| target | enumerate to | top-height RAM (changes below) |
|---|---|---|
| a(37) | `H ≤ 19` | 82 GB at D |
| a(38) | `H ≤ 20` | 88 GB at G |
| a(39) | `H ≤ 20` | 90 GB at G |
| a(40) | `H ≤ 21` | out of RAM at every change |

a(40) is the odd one out because `21 = (40+2)/2` exactly. The topmost level a
run consumes has nothing to check it: for a(39), level 18 predicts T(39,21)
with no comparison entry. The below-onset fitting of `results/below-onset-fit.md`
lowers the required height from `(n+2)/2` to `(n−3)/2`.

The coloring engine's memory is about 8,100 bytes per frontier state with
the exact 256-bit payload and 130 after the changes `results/coloring-recount/parallel/README.md`
describes (residue passes, a flat arena, releasing consumed chunks); states
grow about 3.1× per height (72,487,711 at H = 18, 224,529,648 at H = 19), so
H = 19 ran in 61.6 GB and H = 21 would need the better part of a terabyte.
The H = 19 run retired three entries that had only a congruence check,
(38,19), (39,19) and (40,19)
<!--q:retires.count@19=3--><!--q:retires.cells@19=(38,19),(39,19),(40,19)-->,
and gave row 40 its entries T(40,19) and T(40,23)
<!--q:row40_retires.cells@19=T(40,19),T(40,23)-->.

Two exact routes to the uncovered entries were tested and closed; the record
is in `results/closed-doors.md` (the characteristic-2 collapse does not lift
to ℤ/2^k, and the mod-2 subgroup bit cannot shorten the CRT reconstruction).

## Proving the rule

The rule is 80 lines (`slot`, `canon`, `gather`, `shifted`, `successors`) and
does not change as the engine gets faster. The cancellation identity it rests
on is proved in `docs/proofs/cutcount-identity.md`, exactly in `ℤ[q]`, with
the window-reach lemma (king adjacency reaches at most `H + 1` cells back in
scan order). That the dynamic program realizes the sum is not proved; what
such a proof would need is set out in that note's §6. That the binary
realizes the program is not provable; its check is the Lean model evaluated
on small boards against the C++ at `H ≤ 6`, as
`polyplets/Polyplets/Compute.lean` does for `T n H`.

## Open problems

- T(40,21) has one enumeration. `H = 21` needs 151× the baseline against a
  ceiling of about 41×: out-of-core or nothing.
- Top-bottom mirror symmetry of the strip, the one 2× that would move
  `H = 21`, is unpriced.
- `C_15` of the strip transfer matrix, over 200 GB, has not been run.
- The two unproved steps above, and formalizing the identity
  (`docs/proofs/cutcount-identity.md` §9).

## Reproduce

    make build/strip_tm                              # clang++ -O3 -std=c++17 cpp/strip_tm.cpp
    ./build/strip_tm 14 40 results/ns_a40/perheight  # ~38 GB, ~8.6 h
    python3 experiments/strip_engine.py 10 36        # Python reference with the brute-force anchor
    python3 experiments/paper1_reproducibility_check.py   # coverage (D), Redelmeier (C), coloring recount (F)
    make gate-cutcount-assembly gate-coloring-crt gate-provenance gate-residual-cells
    python3 scripts/coloring_crt.py --dir results/coloring-recount/residues41 --height 19
    python3 experiments/below_onset_fit_ri.py --hmax 19 --jmax 4 --rowdir results/coloring-recount/rows41 --rows 39,40,41
    make build/coloring_recount && make gate-coloring-recount    # needs -fopenmp
    scripts/g2_wholerow.sh 20 10 800 80              # Redelmeier row 20 on 80 workers
