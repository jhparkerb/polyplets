# r4-gen6 plan

**Question:** Can we manufacture an incumbent-free oracle for T(n,H) at H>=17,
where the campaign currently has none, and would such an oracle actually catch
the error classes it would be advertised against?

## Steps

1. Read charter, queue, and predecessors r4-gen{,2,3,4}.md. Product: a list of
   rows already filed on oracles/validation so I file successors and kills, not
   repeats. (Also skim r4-spinproj.md sec 3.1 and r4-gen2 row R4-G2-19.)
2. Read `results/triangle.txt` near-diagonal cells (H=17..21, n=H..H+k) and do
   desk arithmetic on the exact enumeration cost of each. Product: a priced
   near-diagonal reachability table -- free / hours / wall.
3. Adversarial error-class matrix: for each plausible defect (stencil, rank/carry
   at high m, height attribution off-by-one, state truncation, symmetry folding)
   decide whether near-diagonal H=17..21 cells expose it. Product: a table with
   an explicit "cannot see" column.
4. Other routes in kind: row-sweep transfer matrix (heights cheap axis), width-
   limited strips, the 45-degree sublattice bijection, symmetry-class counts,
   external published high-H values. Product: rows with priors + kills.
5. Cheapest single cell: pick the one (n,H>=17) cell worth buying and cost it.
6. Broaden past the angle (charter line 124: never stop making ideas).

## Products

- >=15 rows on the oracle angle in `results/r4/r4-gen6.md`, then broaden.
- Rows appended to `results/r4/queue.md` (append only).

## Stop conditions

- Angle exhausted (all four charter questions answered with numbers or an
  explicit NOT ESTABLISHED) and >=15 rows filed, then broaden until stopped.
- HARD: no compute anywhere; gympie desk arithmetic in `python3 -c` only,
  sub-second. Anything needing a real number becomes a job-request row.
