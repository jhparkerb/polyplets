# results/

## Data

| where | what |
|---|---|
| `triangle.txt` | T(n,H) for n ≤ 40: the number of polyplets with n cells and bounding-box height H |
| `b006770_upload.txt` | a(1)–a(40) as an OEIS b-file; the other `b*_upload.txt` files are b-files for related sequences |
| `ns_a20/` … `ns_a40/` | one directory per term: the run's per-height output and a `PROVENANCE.md` saying how it was produced and checked |
| `a41/` | the a(41) computation and its `PROVENANCE.md` |
| `redelmeier_row20/`, `redelmeier_row22/` | whole-term recounts by Redelmeier enumeration |
| `cutcount_b1/`, `motley-par/` | the coloring recount (`cutcount_b1/PROVENANCE.md`) |
| `subgroup_raw/`, `subgroup_counts.txt`, `percell_raw/` | symmetry-subgroup counts behind the mod-4 congruence |
| `holes_*.txt`, `holes_perheight/` | polyplets counted by number of holes |
| other `.txt` and `.log` files | data behind particular statements in the notes below, which cite them |

## Notes

Start with `confidence.md` for how far each term can be trusted.

| file | what |
|---|---|
| `confidence.md` | the evidence behind each term, and where an error could still hide |
| `provenance-table.md` | generated: for each entry of the triangle, which independent computations agree with it |
| `residual-cells.md` | generated: the entries with only one enumeration behind them |
| `second-sources.md` | the independent recounts in detail: what each computes, how far it reaches, what it shares with the main program |
| `diagonal-formula.md` | the closed forms for the tall part of the triangle, and how their constants are determined |
| `below-onset.md` | the exact deviation from the closed forms just below where they start to hold |
| `undertow.md` | determining the closed forms from entries below their onset, which is how a(41) was computed |
| `symmetry-classes.md` | free, one-sided, bilateral and asymmetric polyplets, and the congruences between them |
| `growth-constant.md` | the growth constant λ: proved bounds and estimates |
| `arithmetic-structure.md` | the triangle modulo 3 and 5, denominators and integrality |
| `perimeter.md` | polyplets counted by site perimeter |
| `subclasses.md` | directed, convex and other subclasses, and holes |
| `anisotropic-not-dfinite.md` | a proof that the height-graded generating function is not D-finite |
| `closed-doors.md` | approaches that were tried and did not work, and why |
| `oeis-candidates.md` | notes on new sequences that could be submitted to the OEIS |
| `l-paper-verifier-coverage.md` | how many of the numbers printed in the machine-written papers are checked by `paper/verify_l_papers.py` |
