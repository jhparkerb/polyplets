# Recounts of the triangle by other programs

`T(n,H)` is the number of fixed polyplets (king-connected sets of `n` cells)
whose bounding box has height `H`; `a(n) = Σ_H T(n,H)` is A006770. The
production engine, a transfer matrix over the kink frontier (`core/kink.h`,
`core/transition.h`), produced every entry to `n = 40` (`results/triangle.txt`)
and heights `1..20` of row 41 (`results/a41/`). Three other programs recount
parts of the triangle. Every agreement below is a measured comparison with a
dated log in the tree; the identity the coloring program evaluates is a
theorem; the memory model is measured to `H = 19` and projected above; each
closed door carries the measurement that closed it.

| program | code | reach | shared with the production engine |
|---|---|---|---|
| strip transfer matrix | `cpp/strip_tm.cpp`; reference `experiments/strip_engine.py` | `H ≤ 14`, `n ≤ 40` | the connectivity rule (union-find over a column, stranded-component death); no code, frontier or state encoding |
| Motley, the coloring transfer matrix | frozen rule `results/cutcount_b1/cutcount_b1.cpp.59e90660` lines 93–173; parallel engine `cpp/motley_par.cpp` | `H ≤ 19`, `n ≤ 41` | nothing: it never decides connectivity |
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

**Independence** (AUDIT-2026-07-30 S1–S3). Disjoint from the kink kernel: no
shared code, frontier or state encoding. Not a different connectivity rule:
its union-find with stranded-component death is the rule of the reference
column oracle `core/transition.h`, written independently, so a shared
misconception about king connectivity would not be caught. The Python
reference and the C++ program landed in one commit (`713540c`); their
agreement on every `C_H`, `H ≤ 10`, is a transcription check. The brute-force
anchor (`brute_T` in `experiments/strip_engine.py`) is independent of both,
agrees exactly for `n ≤ 9`, and exists only in the Python reference
(`results/strip_engine_python_run.log`, gympie 2026-07-30, `Hmax 10`, `Nmax 14`).

**Result.** Every entry computed matches the production triangle.

| run | entries confirmed | log | machine, date, wall |
|---|---|---|---|
| `Hmax 10` | 315 | — | ~5 s |
| `Hmax 13`, `n ≤ 36` | columns `H ≤ 13` | `results/strip_engine_run.log` (C++ output despite the name; `C_13` 606 s) | ~730 s |
| `Hmax 14`, `n ≤ 36` | 413, 0 mismatch | `results/strip_C14_run.log` | dalby 2026-07-22, ~7.5 h (`C_14` 22,919 s) |
| `Hmax 14`, `n ≤ 40` | **469, 0 mismatch** | `results/strip_C14_n40_run.log`, rev `5239e73` | dalby 2026-07-30, ~8.6 h (`C_14` 25,892 s) |

The first C++ run stopped after `C_13`, so its end-of-run comparison never
ran. `C_14` needs about 38 GB and thrashed on gympie (24 GB); dalby is about
5.4× slower per thread than gympie. `C_15` would need over 200 GB.

Redelmeier confirms whole rows only to `n = 22`; the strip's cost grows as
about `2^H` whatever the count, so it confirms columns `H ≤ 14` at every `n`
to 40. At the a(40) close the grand-form levels `k ≤ 18` had 30 anchor entries,
19 inside the strip's reach and 11 outside: T(28,15), T(29,15), T(30,16),
T(31,16), T(32,17), T(33,17), T(34,18), T(35,18), T(36,19), T(37,19),
T(38,20). Motley's rows at `H ≤ 19` later recounted all but T(38,20).

**Coverage, three ways** (AUDIT-2026-07-30 S4), over the 820 entries
`1 ≤ H ≤ n ≤ 40`: `R` = `H ≤ 4` (recurrences); `S` = strip, `H ≤ 14`;
`P` = closed forms `P_k` on diagonals `k = n − H ≤ 18` with `n ≥ 2k + 1`
(diagonal 19 excluded: `P_19` was fitted with no entry held back and would add
only its two fit points, T(39,20) and T(40,21)). Doc-style = `|R ∪ P ∪ S|`;
honest = `|R ∪ S ∪ (P ∩ {H ≤ 21})|`, a closed form not being a recount of an
entry it produced.

| figure | strip `n ≤ 36` | strip `n ≤ 40` |
|---|---|---|
| doc-style | 742 (90.5%) | 782 (95.4%) |
| honest | 552 (67.3%) | 592 (72.2%) |
| strip alone | 413 (50.4%) | 469 (57.2%) |

`experiments/paper1_reproducibility_check.py` recomputes the right-hand column
and `scripts/provenance_table.py` checks it. The share of a term these entries
make up is not reported: a term is wrong if any one entry is wrong.

**Complexity (C++).** Partition states per height 1, 3, 8, 20, 50, 126, 322,
834, 2187, 5797, …, about 2.65× per height; wall about 6× per height
(`H = 10`: 3.5 s). `__int128` suffices for `n ≤ 40`, `H ≤ 15` since
`C_H(n) ≤ H · a(n) < 1.7·10^38`; the state packs 4 bits per row, so `H ≤ 15`.

## Motley, the coloring transfer matrix

Write `A_n(q) = Σ_S q^{c(S)}` over the `n`-cell subsets `S` of the strip, with
`c(S)` the number of king-connected components; the connected count is
`[q^1] A_n(q)`. Motley computes it by a frontier dynamic program over
color-coincidence partitions of the last `H + 1` cells in scan order, in
`ℤ[q]/(q^2)`: a cell with no earlier occupied king neighbor adopts a live color
or takes a fresh one at weight `q − b`; a cell whose earlier neighbors carry
two colors contributes 0. No union-find, no stranded-component death, no
completion predicate. That the sum of the weights is `q^{c(S)}` exactly in
`ℤ[q]` is the cut-count cancellation identity, the Potts spin form of the
Fortuin–Kasteleyn correspondence, proved in `docs/proofs/cutcount-identity.md`
(2026-08-14) and checked by brute force on 10 boards and 223,000 subsets
(`experiments/birthright_identity_check.py`). The output is the strip's
`C_H(n)` and the triangle the same second difference.

The self-checks `q0_zero` (`[q^0] A_n = 0`) and `q1eval_binomial`
(`A_n(1) = C(HW, n)`) follow from the identity and consult no connectivity: a
stencil defect anchored at the bottom row passes both. Only comparison against
independently computed entries catches the rule going wrong.

**Runs**, Nmax 40 unless stated. The single-thread engine `cutcount_b1` was
built on the `second-source` branch (`48ac108` for step 0, `4df3fec9` after);
this tree holds only its frozen rule source.

| run | payload | date | script, artifacts | agreement | cost |
|---|---|---|---|---|---|
| calibration, `H ≤ 16` | exact 256-bit; source sha `59e90660`, uncommitted | dalby 2026-08-11 | `results/cutcount_b1/calib_run.log` | 640 of 640 entries match `results/triangle.txt` | `H = 16`: 16,475 s, 60.8 GB |
| step 0, `H ≤ 16` | exact; clean gated build `git=48ac1089`, binary sha256 `e66f4466…` | dalby 2026-08-14 | `scripts/dalby_motley_step0.sh` | 16 rows identical to calibration; 640 of 640 | three streams: `H = 16` 17,047 s, 62.3 GB; `H = 15` 4,806 s, 20.4 GB; `H ≤ 14` ~2,400 s, 6.9 GB; 88 GB together |
| `H = 17` | exact 128-bit; build `4df3fec9`, sha256 `dd173239…` | dalby 2026-08-14 | `scripts/dalby_motley_h17.sh`; `rows/C17.out` | T(n,17), `n = 17..40`: 24 of 24 | 39,117 s (10.9 h), 95.0 GB, 23,681,423 states |
| `H = 18`, Confetti | five 31-bit primes, one pass each; CRT from four, the fifth predicted | dalby 2026-08-14 to 08-19 | `scripts/dalby_confetti_h18.sh`; `rows/C18.out`, `residues/`, `results/cutcount_b1/confetti_h18_run.log` | T(n,18), `n = 18..40`: 23 of 23; prime 2147483563 predicted at 40 of 40 | 399,700 s on one core (4.63 days), 65.9 GB, 72,487,711 states |
| Nmax 41, `H ≤ 19` | nine 16-bit primes per height; eight reconstruct, the ninth must predict every entry | dalby 2026-08-20 to 08-21, rev `18b90ab6` | `scripts/motley_ladder.sh`; `results/cutcount_b1/rows41/`, `residues41/`, `rows41/run/timings.txt` | 589 entries `H ≤ 19`, `n ≤ 40` match the triangle; 19 entries at `n = 41` match `results/a41/h<H>.out`; ninth prime predicted at all 19 heights | `H = 19`: nine passes of ~5,630 s, peak 61.6 GB, 80 threads |

Confetti's passes:

| prime | wall s | peak RSS MB |
|---|---|---|
| 2147483647 | 80,632.9 | 65,943.7 |
| 2147483629 | 80,614.0 | 65,945.9 |
| 2147483587 | 79,069.6 | 65,941.4 |
| 2147483579 | 79,039.5 | 65,946.1 |
| 2147483563 (predicted) | 80,344.3 | 65,941.8 |

The passes agree within 2.0% on wall. Against `H = 17` the mod-p payload
traded wall for memory: 2.05× the wall per pass, 0.69× the peak, five passes
for one. The constants measured at `H = 16 → 17`, wall ×3.198, peak ×2.963,
states ×3.023, sit against ×3.209 and ×2.984 from the census
`Σ_k C(H+1, 2k) · Bell(k)`; the stop condition, more than 20% off the census
ratio, did not fire. The `H = 16` baseline of those ratios, 12,231 s and
32.06 GB with the 128-bit payload, has no run record in the tree beyond this
line.

**Provenance.** The calibration rows came from a source (sha256
`59e90660b42a0d94ceae5459287db35b4d93f87a5e62753ccd549235edaa8d3d`) matching
neither committed revision on `second-source`, with a gate battery predating
the fail-closed exit codes; the diff against `7b13137` is 71 lines, almost all
the removal of its `--modp` mode (`results/cutcount_b1/PROVENANCE.md`). Step 0
retired the caveat. Its first assembly check pointed at the wrong directory,
compared zero entries, and exited 3 with `FATAL no_banked_cells_compared`, the
fail-open hole `48ac108` closes. The `H = 17` launch was refused by the
previous binary (`limits: H<=16`), exposing three hard-coded height caps and a
latent `H = 18` fan-out overflow. Confetti's row was harvested by `scp` after
a harvest through `ssh cat` failed its checksum; `C18.out` has sha256
`26b4fa322303c8b26798c41dd0daafb698bd6909ab440a834a0eb95bbd0aeb81`. Each
runner refuses to start without its input rows, Confetti's also without a
receipt naming the binary's sha256 and a green gate.

**Gates.** `make gate-cutcount-assembly` (`scripts/cutcount_assembly_gate.py`)
assembles the rows against `results/triangle.txt` (567 entries from `rows/`,
589 from `rows41/`), compares `rows41` at `n = 41` against `results/a41/` (19
entries), reconstructs `C_18` from four primes and predicts the fifth, and
re-derives the ninth-prime verdict at all 19 heights of the Nmax-41 run (779
entries), with 16 controls that must fail. `make gate-motley-crt`
(`scripts/motley_crt.py --selftest`) reconstructs `C_18` and `C_19` and
confirms a corrupted residue is caught. `tests/gate_motley_par.py` checks the
parallel engine against the exact rows at three payload widths and for
thread-count determinism (ayr only: `-fopenmp`).

**The parallel engine** (`results/motley-par/README.md`, 2026-08-20) keeps the
five rule functions and replaces the accounting: flat open-addressed table,
OpenMP over source rows, payload width from the prime, release of each
consumed chunk. At `H = 14` it is 50× the single-thread engine on 80 threads;
it reproduced all five Confetti residue rows on ayr at about 3,350 s per prime
against about 79,940 s; its `H = 19` census is 224,529,648 states.

## Redelmeier whole-row recounts

`build/g2` (`cpp/g2_redelmeier.cpp`) generates every fixed polyplet once and
shares no counting logic with either transfer matrix. It is the canonical
enumerator.

**Row 20** (`results/redelmeier_row20/`): dalby,
`scripts/g2_wholerow.sh 20 10 800 80`, launched 2026-07-10 18:03 EDT, rev
`7eab237`. Rows `n = 1..20` match `results/b006770_upload.txt`;
a(20) = 1025573519362016 is confirmed by two algorithms, and A030233, A030222
and A194596 inherit the confirmation at `n = 20`.

| quantity | value |
|---|---|
| wall | 28,684 s (7.97 h) |
| core-seconds | 2,204,116 (96.1% utilization of 80 workers) |
| shard wall s: mean, median, p99, max | 2,755, 2,752, 3,092, 3,188 |
| full-cost nodes (size ≤ 19) | Σ a(1..19) ≈ 1.777·10^14 |
| cost per node | 12.4 ns ≈ 37 cycles (Neoverse N1, 3.0 GHz) |

**Row 22** (`results/redelmeier_row22/PROVENANCE.md`): three machines,
2026-07-11 to 07-16, 24,000 shards; every row `n ≤ 22` matches. This is tier
T1 of the technical report.

## What the recounts leave uncovered

Exact recounts: Redelmeier `n ≤ 22`; strip `H ≤ 14`; Motley `H ≤ 19`;
small-height recurrences `H ≤ 4`; decorrelated fixed-height generating
functions `H ≤ 10`; the closed forms `P_k` where an enumeration also reached
the entry. Every entry also carries the mod-2 and mod-4 congruence of the
height-preserving subgroup census (`results/symmetry-classes.md`), which
catches an error only if the error is nonzero mod 4.

| Motley reach | congruence-only entries: no exact recount, no closed form <!--q:prose--> |
|---|---|
| `H ≤ 17` | 11 <!--q:congruence_only.count@17=11--> |
| `H ≤ 18` | 6: (38,19), (39,19), (39,20), (40,19), (40,20), (40,21) <!--q:congruence_only.count@18=6--><!--q:congruence_only.cells@18=(38,19),(39,19),(39,20),(40,19),(40,20),(40,21)--> |
| `H ≤ 19`, the record | 3: (39,20), (40,20), (40,21) <!--q:congruence_only.count@19=3--><!--q:congruence_only.cells@19=(39,20),(40,20),(40,21)--> |

A second question is which entries of row 40 still rest on the production
engine's connectivity rule: those with `h ≤ 21` until Motley reaches `h`, and
those with `h ≥ 22`, computed from `P_k` at `k = 40 − h`, until both fit points
`T(2k+1,k+1)` and `T(2k+2,k+2)` are inside Motley's reach.

| Motley reach | row 40 entries on the production rule | a(n) closed by overlap of Motley and closed forms |
|---|---|---|
| `H ≤ 17` | 7 <!--q:row40_residual.count@17=7--> | `n ≤ 33` <!--q:closure_n@17=33--> |
| `H ≤ 18` | 5 <!--q:row40_residual.count@18=5--> | `n ≤ 35` <!--q:closure_n@18=35--> |
| `H ≤ 19` | 3: T(40,20), T(40,21), T(40,22) <!--q:row40_residual.count@19=3--><!--q:row40_residual.cells@19=(40,20),(40,21),(40,22)--> | `n ≤ 37` <!--q:closure_n@19=37--> |
| `H ≤ 20` | 1 <!--q:row40_residual.count@20=1--> | `n ≤ 38` <!--q:closure_n@20=38--> |
| `H ≤ 21` | 0 <!--q:row40_residual.count@21=0--> | `n ≤ 39` <!--q:closure_n@21=39--> |

Both counts reach zero only at `H = 21`, which does not fit in memory (below).
The later record (`results/undertow.md`, 2026-08-20; `docs/handoff.md`) states a(n)
rule-independent for every `n ≤ 39` with Motley at `H ≤ 18`, by fitting each
level from entries below the range where its formula holds, with the ab initio
defect; `docs/audits/AUDIT-2026-09-02.md` (M2) grades that route as one formula strategy
fitted from Motley's data, not a second enumeration; the provenance table
carries it as tag U.

## The height an enumeration must reach

`P_k` holds for `n ≥ 2k + 1`, its onset (the shape is the theorem of
`docs/proofs/diagonal-law.md`); its two free coefficients were fitted from two
enumerated entries, cheapest at `T(2k+1,k+1)` and `T(2k+2,k+2)`. Row 40: 20
entries at `H ≤ 20` enumerated; T(40,21) enumerated and also `P_19`'s second
fit point; 19 entries at `H ≥ 22` from `P_k`, `k ≤ 18`, never enumerated.
Every fit point of `k ≤ 18` lies at `H ≤ 20`, so a Motley run to `H = 20` at
Nmax 40 makes every entry of row 40 but T(40,21) rule-independent at no
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
with no comparison entry. This rule was superseded on 2026-08-20 by the
below-onset fitting of `results/undertow.md`, which lowers the required height
from `(n+2)/2` to `(n−3)/2`.

## Memory model of the coloring engine

Measured on the calibration run (dalby, one thread, exact 256-bit payload):

| H | states | wall s | peak RSS MiB | bytes per state |
|---|---|---|---|---|
| 14 | 891,074 | 1,618.6 | 6,924.6 | 8,149 |
| 15 | 2,624,197 | 5,134.5 | 20,382.8 | 8,144 |
| 16 | 7,832,667 | 16,475.2 | 60,827.4 | 8,143 |

Marginal slope `H = 15 → 16`: 8,142 bytes per state. The payload model,
41 area slots × 3 coefficient streams × 32 bytes × 2 buffers = 7,872 bytes,
accounts for it to 3%; the remaining ~270 bytes are container overhead
(`unordered_map` node plus one heap vector per state). Measured states over
the census: 2.286, 2.298, 2.308, 2.318, 2.327 at `H = 12..16`, rising about
0.011 per height.

| H | 17 | 18 | 19 | 20 | 21 |
|---|---|---|---|---|---|
| states, projected (±20%) | 23.7 M | 72.8 M | 226 M | 709 M | 2.25 B |
| states, measured | 23,681,423 | 72,487,711 | 224,529,648 | — | — |

Budget: dalby, 125 GB, about 121 available. `C_16(40) = 1.42·10^32`
(`2^106.8`) with a falling per-height ratio (1.44, 1.36), so `C_21(40)`
projects to `2^108`–`2^111`, inside a wrapping 128-bit word; the `A_n(1)`
check is compared against a Pascal row in the same wrapping ring.

Changes, each a factor on bytes per state, cumulative in the order listed;
peak RSS in GB:

| change | factor | bytes/state | H17 | H18 | H19 | H20 | H21 | top H |
|---|---|---|---|---|---|---|---|---|
| measured baseline | — | 8,142 | 193 | 593 | 1,839 | 5,772 | 18,322 | — |
| A: 256-bit to 128-bit payload (exact by the same ring argument) | 1.9× | 4,206 | 100 | 306 | 950 | 2,982 | 9,465 | 17 |
| B: the `A_n(1)` check as its own pass (3 streams to 2; wall up a half) | 1.5× | 2,894 | 69 | 211 | 654 | 2,052 | 6,513 | 17 |
| F: flat arena, open-addressed index (overhead ~270 to ~57 bytes) | 1.1× | 2,681 | 64 | 195 | 606 | 1,901 | 6,033 | 17 |
| C: residue passes at 32 bits (4 primes plus one predicted; values `< 2^112`) | 4× over A | 713 | 17 | 52 | 161 | 505 | 1,605 | 18 |
| D: 16 bits, 8 primes | 8× over A | 385 | 9 | 28 | 87 | 273 | 866 | 19 |
| E: 8 bits, 16 primes | 16× over A | 221 | 5 | 16 | 50 | 157 | 497 | 19 |
| G: release each consumed chunk, `MADV_DONTNEED` (peak 2× to ~1.2× the working set; unmeasured when planned) | 1.7× | 130 | 3 | 9 | 29 | 92 | 293 | 20 |

Each height demands, off the baseline, H17 1.6×, H18 4.9×, H19 15.2×,
H20 47.7×, H21 151×. `H = 21` never fits: the payload floor caps the list at
about 41× (at one byte per slot-coefficient the payload is still 164 bytes and
the keys 57), so it is out-of-core or nothing, for the one entry T(40,21).

Measured afterward: `H = 17` after A, projected 100 GB, measured 95.0;
`H = 18` after C, projected 52 GB, measured 65.9, Confetti's container
overhead being 909.7 bytes per state against the 57 assumed; `H = 19` with F,
G and 16-bit residues in the parallel engine, projected 59 GB, measured 61.6.
The release path measured 0.53× the peak of the same run without it.

**Ticker Tape, `H = 19` priced on the single-thread engine** (2026-08-18,
from Confetti's first four passes at 79,039 s and 65.9 GB, with the ×3.209
wall and ×2.984 RSS per height): about 253,700 s (70.5 h) per pass, nine
passes, 634 h ≈ 26 days (about 40 with change B), peak about 197 GB against
dalby's 125. The recommendation then was to stop at `H = 18`. What `H = 19`
buys does not depend on how it was run: two entries of row 40, T(40,19) and
T(40,23) <!--q:row40_retires.cells@19=T(40,19),T(40,23)-->, and two terms,
a(36) and a(37); it retires three congruence-only entries, (38,19), (39,19)
and (40,19) <!--q:retires.count@19=3--><!--q:retires.cells@19=(38,19),(39,19),(40,19)-->.
The parallel engine ran it two days later in 50,745 s of wall over nine passes.

**Not levers**, measured with `experiments/cutcount/cutcount_b1_probe.cpp`
(the frozen engine plus an occupancy census, gated by reproducing `C9.out`):

- Ranged-area payload (store only `[n_lo, n_hi]` per state): mean nonzero span
  at the peak column 36.4, 35.9, 35.4 of 41 slots at `H = 8, 9, 10`, a gain of
  1.127×, 1.143×, 1.160×. The nonzero count equals the span, so sparse storage
  is dead too.
- Fewer columns: the state set saturates at column 2 of 41 at every `H`
  measured; column count is a wall lever only.
- Evaluating in the area variable: the true degree in `x` is `H · W = 861`,
  not 40; the 41-slot vector is the truncation to `n ≤ 40`, and evaluation
  cannot truncate. Cyclic aliasing mod `x^41 − 1` fails the same way.
- Truncating the width from `W = 41` to `42 − H`: sound for the second
  difference when all three heights use the same `W`, but a time lever (~2× at
  `H = 21`), not a memory one.
- Top-bottom mirror symmetry (~2× on states, the one factor that would move
  `H = 21`): the flip commutes with a column-at-a-time transfer but not with
  the row-at-a-time scan the engine uses. Unpriced.

## Closed doors

**Coin Lift: the characteristic-2 collapse does not lift.**
`experiments/tristruct/r3_lift_snf_probe.py`, logs
`experiments/tristruct/r3_lift_snf_probe.log` (p = 2) and
`experiments/tristruct/r3_lift_snf_probe_p3.log`; gympie 2026-08-14, about
90 minutes. Does the small rank of the Hankel observability matrix over GF(2)
survive lifting to `ℤ/2^k`, giving an exact route to the uncovered entries?
The gate as first written ("kill if the `ℤ/4` free rank jumps") cannot fire:
an invariant factor is a unit mod 4 iff it is odd iff it survives mod 2, so
that rank is the GF(2) rank identically. The deciding quantity is
`μ_k(H) = #{invariant factors d_i with v_2(d_i) < k}`, the minimal number of
generators over `ℤ/2^k`, with `μ_1` the GF(2) rank and `μ_∞` the rank over `ℚ`.

| H | states | μ_1 = GF(2) | μ_2 = ℤ/4 | μ_3 = ℤ/8 | μ_4 | rank mod p | μ_2/μ_1 |
|---|---|---|---|---|---|---|---|
| 4 | 20 | 6 | 6 | 6 | 6 | 6 | 1.000 |
| 5 | 50 | 15 | 17 | 17 | 17 | 17 | 1.133 |
| 6 | 126 | 27 | 35 | 35 | 35 | 35 | 1.296 |
| 7 | 322 | 58 | 86 | 88 | 88 | 88 | 1.483 |
| 8 | 834 | 112 | 194 | 204 | 204 | 204 | 1.732 |
| 9 | 2,187 | 229 | 459 | 500 | 501 | 501 | 2.004 |

`μ_2/μ_1` grows every height and at `H = 9` the second bit has spent the whole
factor of 2; `μ_4` is the generic rank at every height. The collapse is the
degeneracy `x + x = 0` and nothing more. At p = 3, `μ_1` is 6, 17, 35, 87,
201, 488 against the generic 6, 17, 35, 88, 204, 501; at p = 5 and 7 the rank
is generic at every `H ≤ 8`; extension fields of characteristic 2 change no
rank. `μ_∞` reproduces the mod-p ranks by an independent computation over `ℤ`,
so the rational rank equals the mod-p rank wherever measured. The probe exits
nonzero unless `μ_1` equals the recorded GF(2) ranks 6, 15, 27, 58, 112, 229
and a second, independently written GF(2) elimination, `μ_K` equals the mod-p
rank wherever both exist, and a stencil with one diagonal dropped moves the
profile (6 to 11 at `H = 4`; 15, 17, 17 to 24, 25, 25 at `H = 5`). That
battery caught a defect: the first `H = 9` run reported `μ_8 = 498` against
501, the closure pruning having dropped an incoming vector after a
valuation-ordered swap; rows `H ≤ 8` were identical either way. The uncovered
entries therefore have no cheap exact closer.

**The mod-2 subgroup bit and the CRT reconstruction do not compose**
(2026-08-22, desk arithmetic). CRT is not partial: once the primes give the
exact integer, the parity is a check on a value already known, which is how the
provenance table uses it (tag C). Nine primes near `2^16` give a modulus of
about `2^144`; adjoining 2 adds 0.7%. Reconstructing modulo a product smaller
than the value and using parity plus a size bound is not excluded, but needs
the value bracketed within a factor of two, which nothing supplies. The same
item found the provenance generator carrying Motley's reach as a hand-set
constant a height behind the rows in the tree, invisible to its gate;
`scripts/provenance_table.py` now derives the reach from the row sets that
assemble to the triangle.

## Proving the rule

The rule is 80 lines (`slot`, `canon`, `gather`, `shifted`, `successors`) and
does not change as the engine gets faster. Tier 1, the cancellation identity,
is proved in `docs/proofs/cutcount-identity.md`; four statements of the plan
that preceded it must not be copied into a theorem: the identity is exact in
`ℤ[q]`, not a mod-`q^2` phenomenon; a subset carries a sum over
configurations, not one product of birth factors; `b` counts live labels, not
live components; and the window-reach lemma (king adjacency reaches at most
`H + 1` cells back in scan order) belongs to this tier. Tier 2, that the
dynamic program realizes the sum, is delimited in the proof's §7, invariant
work of the kind `polyplets/Polyplets/Defs.lean` and
`polyplets/Polyplets/Graph.lean` already carry (`kingAdj`, `KingConnected`,
`kingConnected_iff_reachable`). Tier 3, the bridge to the binary, is never
provable; its gate is the Lean model evaluated on small boards against the C++
at `H ≤ 6`, as `polyplets/Polyplets/ComputeBridge.lean` does for `T n H`.

## Open problems

- T(40,21) has one enumeration. `H = 21` needs 151× the baseline against a
  ceiling of about 41×: out-of-core or nothing.
- Top-bottom mirror symmetry of the strip, the one 2× that would move
  `H = 21`, is unpriced.
- `C_15` of the strip transfer matrix, over 200 GB, has not been run.
- Tiers 2 and 3 above, and formalizing the identity
  (`docs/proofs/cutcount-identity.md` §10).

## Reproduce

    make build/strip_tm                              # clang++ -O3 -std=c++17 cpp/strip_tm.cpp
    ./build/strip_tm 14 40 results/ns_a40/perheight  # the 2026-07-30 run: ~38 GB, ~8.6 h on dalby
    python3 experiments/strip_engine.py 10 36        # Python reference with the brute-force anchor
    python3 experiments/paper1_reproducibility_check.py   # coverage (D), Redelmeier (C), Motley (F)
    make gate-cutcount-assembly gate-motley-crt gate-provenance gate-residual-cells
    python3 scripts/motley_crt.py --dir results/cutcount_b1/residues41 --height 19
    python3 experiments/undertow_ri.py --hmax 19 --jmax 4 --rowdir results/cutcount_b1/rows41 --rows 39,40,41
    make build/motley_par && make gate-motley-par    # ayr only (-fopenmp)
    scripts/g2_wholerow.sh 20 10 800 80              # Redelmeier row 20 on 80 workers
    python3 experiments/tristruct/r3_lift_snf_probe.py   # Coin Lift

## Sources

- `results/strip-engine.md` (deleted 2026-09-06; its content is above)
- `results/motley-h17.md` (deleted 2026-09-06; its content is above)
- `results/motley-h18.md` (deleted 2026-09-06; its content is above)
- `results/motley-step0.md` (deleted 2026-09-06; its content is above)
- `results/coin-lift-g2.md` (deleted 2026-09-06; its content is above)
- `results/ticker-tape-assessment.md` (deleted 2026-09-06; its content is above)
- `results/congruence-crt-combination.md` (deleted 2026-09-06; its content is above)
- `results/redelmeier_row20/RESULT.md` (deleted 2026-09-06; its content is above)
- `docs/b1-closure-plan.md` (deleted 2026-09-06; its content is above)
