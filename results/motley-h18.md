# Motley rung 2 (Confetti) — H = 18, GREEN

Run 2026-08-14 17:56 to 2026-08-19 08:58 EDT on dalby, `docs/motley-plan.md`
§"Rung 2". Runner `scripts/dalby_confetti_h18.sh`; row banked here as
`results/cutcount_b1/rows/C18.out`, the run's own log as
`results/cutcount_b1/confetti_h18_run.log`.

**GREEN.** T(n,18) = C_18(n) − 2 C_17(n) + C_16(n), assembled from this run's
C_18 and the banked C_16/C_17, matches the incumbent's triangle
(`results/triangle.txt`) at **all 23 cells n = 18..40, 0 mismatch**. The
assembly was re-run here from the banked rows after the harvest, independently
of the runner's own verdict, and reproduces the same 23/0.

**Product: a(n) is closed rule-independently for all n ≤ 35** (n = 2H − 1 at
H = 18), by the colour-symmetrized cancellation rule — no union-find verdict,
no stranded-component death, no completion predicate. This moves the
rule-independent frontier from n ≤ 33 (`results/motley-h17.md`) to n ≤ 35.

What it does to the gap, measured off `scripts/provenance_table.py` at
`MOTLEY_H` 17 against 18 rather than off any plan's forecast: the cells
carrying **only** the mod-4 congruence — no exact recount, no closed form —
drop from **11 to 6**, and the six are (38,19), (39,19), (39,20), (40,19),
(40,20), (40,21). On row 40 alone that is four cells down to three; (40,18) is
what Confetti bought there. The count of cells with no exact source at all is
195, down from 200, the rest being formula-only and unchanged at 189.

## Provenance

| | |
|---|---|
| binary | `~/src/pm-halfmeasure/build/cutcount_b1`, stamp `git=4df3fec9`, no `-dirty` |
| binary sha256 | `dd1732399703d5aa786e11c8b450fb2aa3a7af8dfd599906c79fb474193b883e` |
| receipt | `verdict=GREEN`, sha256 matching the binary as hashed at launch, primes recorded — the runner refuses to start without it |
| `C18.out` sha256 | `26b4fa322303c8b26798c41dd0daafb698bd6909ab440a834a0eb95bbd0aeb81`, verified on both sides after `scp` |
| held-out prime | 2147483563: **40/40 residues predicted correctly** from the CRT reconstruction over the other four |
| oracle for the product | the incumbent triangle, independently computed |
| inputs C_16, C_17 | banked rows from step 0 and rung 1 (`results/motley-step0.md`, `results/motley-h17.md`) |

The harvest is `scp`, not `ssh cat`: the first attempt piped the row through a
remote shell and the sha256 did not match. Whatever that inserted, it is the
reason this table quotes a checksum verified on both sides.

## Cost, measured

Five sequential single-core passes, one per prime, exact C_18 reconstructed by
CRT from the first four with the fifth held out.

| pass | prime | wall | cpu | peak RSS |
|---|---|---|---|---|
| 1 | 2147483647 | 80,632.9 s | 80,583.5 s | 65,943.7 MB |
| 2 | 2147483629 | 80,614.0 s | 80,568.3 s | 65,945.9 MB |
| 3 | 2147483587 | 79,069.6 s | 79,023.2 s | 65,941.4 MB |
| 4 | 2147483579 | 79,039.5 s | 78,992.9 s | 65,946.1 MB |
| 5 | 2147483563 | 80,344.3 s | 80,303.3 s | 65,941.8 MB |

**Total 399,700 s = 4.63 days of wall on one core**, peak RSS 65.9 GB, frontier
72,487,711 states. The five passes agree to within 2.0% of each other on wall,
which is what a sequential single-core residue loop should look like and is
worth recording as the calibration for any further rung.

Against rung 1 (H = 17, u128, 39,117 s, 95.0 GB): the modp payload trades wall
for RAM exactly as designed — 2.05x the wall per pass and 0.69x the peak, and
five passes instead of one.

## What this does not do

It does not extend the sequence, and it is not a second source for any cell the
incumbent had not already computed. It is a second *rule*: the same 23 cells,
reached by a method that never asks whether a configuration is connected.
Row 40's cells at H = 19, 20 and 21 still carry nothing but the mod-4
congruence, which catches an error only if it is nonzero mod 4.
