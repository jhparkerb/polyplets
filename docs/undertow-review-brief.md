# Undertow review — the brief

Authored 2026-08-20 by the lead, committed before any lane launched. Every lane
reads this file, not a paraphrase of it.

**Mission, one sentence:** find out whether the Undertow result is circular,
whether its pieces interact the way the lead thinks, and whether the diagonal
tower can be freed from fitting altogether.

---

## 1. The fact pack — what exists, with file:line where it matters

**The object.** `T(n,H)` = fixed king-lattice polyplets with `n` cells in a
bounding box of height exactly `H`. `a(n) = sum_H T(n,H)` = A006770.

**The diagonal tower.** `docs/proofs/diagonal-law.md` (shape proved, Lean),
`docs/proofs/grand-form.md` (Lean-complete): for `n >= 2k+1`,

    T(n, n-k) = P_k(n) * 3^(n-1-3k),   P_k(n) = [y^k] exp( sum_j (a_j + b_j n) y^j )

so level `k` carries exactly **two new constants** `(a_k, b_k)`.

**The standing anchor rule.** `docs/b1-closure-plan.md` §1: level `k` is pinned
by its two cheapest IN-ONSET cells, `T(2k+1,k+1)` and `T(2k+2,k+2)` — the two
TALLEST cells on its diagonal. Every cost table in the campaign follows from
this.

**Undertow** (`results/undertow.md`, `experiments/undertow_pin.py`): a
BELOW-onset cell is also a linear equation in `(a_k, b_k)`,

    T(2k+1-j, k+1-j) = P_k(2k+1-j) * 3^(2k-3k-j) + D_j(k)

with `D_j(k)` the depth-`j` defect. That cell sits at height `k+1-j`, i.e. `j`
rows SHORTER than the onset anchor. Two depths, two equations, one level.

**`D_j(k)`.** Severance W3, `results/onset-defect-depths234.md`, exposed by
`experiments/severance_w3_depths.py::D_series(j, K)`. Exact at `j = 1..4`. Its
own docstring claims it reads neither the triangle nor the wired `P_k`.
Validated by `experiments/severance_w3_gate.py` against 16-19 banked cells per
depth at `k <= 19`. Family tables: `results/severance_w3_families_K22_e*.txt`
(fresh, and identical to the banked K=19 table wherever they overlap).

**Ab-initio low levels.** Severance W1, `results/severance-w1-anchor-cut.md`:
`P_1..P_9` from cluster weights alone, `results/severance_w1_weights_k9.txt` +
`experiments/severance_w1_assemble.py`. Ceiling `k = 9`, declined on memory
(53 GB at k=9, scales ~20x/level).

**Motley.** `results/cutcount_b1/rows/C*.out`, H = 1..18, a DIFFERENT
connectivity rule (`docs/proofs/cutcount-identity.md`). Telescoped
`T = C_H - 2C_{H-1} + C_{H-2}` by `undertow_pin.py::read_tri_motley`.

**The incumbent.** `results/ns_a40/perheight/h*.out`, the kink column sweep, is
what produced a(30)..a(40) and what the wired `orchestrator/sweep.go
diagCoeffTable` was fitted to.

## 2. What is CLOSED — do not re-derive

- The four measured-dead engine levers (new sweep axis, finite-lattice method,
  MPS/boundary compression, holonomic accelerator) and the 45°/anti-diagonal
  TM. Receipts in the memory index; connectivity is the wall.
- **Dual-connectivity TM** (track the complement's 4-connectivity, planar hence
  non-crossing, recover components from `C = χ + holes`). Dead: the doomed-
  configuration prune forces you to carry the component count, and
  `b·Cat(b)` exceeds `Bell(b)` at the block counts that dominate —
  11,440 vs 4,140 at b = 8. `docs/lastditch-ideas.md` §6.
- **Per-level span cap in the family DP.** Looks certain, is 9x faster and 5x
  smaller, and UNDERCOUNTS (333 vs 339 at `(e,k) = (0,2)`, K = 9). A prefix's
  span is bounded by the FINAL cluster's cell count, not its own: two 2-cell
  rows `{0,3}` over `{1,2}` are connected with span 3, and the first row alone
  spans 3 with two cells. `docs/lastditch-ideas.md` §2.
- **Exact Change / linear-algebra compression.** char-2 rank is A034299 exactly
  and the cell-level compression is only ~6x, mod-2 only; mod-p ranks do not
  collapse. `results/exactchange-probes.md`.
- Coin Lift's exact-value route, excluded by the mod-p Hankel floor.

## 3. The lanes

Each lane's FIRST deliverable is its own findings list, timestamped, appended
to `results/undertow-review-queue.md` **before it reads any other lane's
output**. Append-only. The lead holds a withheld seed list for every lane and
will score against it afterwards: what the lane found that the seed lacked,
what the seed held that the lane missed, and the convergence rate. Lanes are
given **no candidate list**.

### Lane A — circularity audit (adversarial)

Question: **is any Undertow number derived, directly or transitively, from a
value that depends on it?**

The lead's claims to attack, strongest first:

1. `a(n)` is rule-independent for every `n <= 39`, and row 40's only gap is
   `T(40,19)` (`experiments/undertow_ri.py`).
2. 342 banked cells re-derived from strictly shorter cells, 0 wrong
   (`undertow_pin.py --audit`).
3. a(40), a(39), a(38), a(37) reassembled exactly from short sweeps.
4. a(41) = 393811462683918679824582849262105 (`results/a41/PROVENANCE.md`).

Trace every input to ground. Read the code, not the prose. Where a value is
used both as an input and as a comparison target, say which. Where a "check"
is guaranteed to pass by construction, say so and say how much it was worth.
Grade each claim CLEAN / WEAKER-THAN-STATED / CIRCULAR with the file:line that
decides it.

### Lane B — interaction, and what a(41)/a(42) would nail down

Question: **can a run at n = 41 or 42 close a(40)'s remaining gap, and what
exactly would it close?**

`T(40,19)` sits on level 21. Work out, from the dependency structure alone,
which cells at n = 41 and n = 42 bear on level 21 and on `T(40,19)`, what each
would establish, and what it would cost against `results/ns_a40/PROVENANCE.md`
and `results/ns_a40/rundir_size.log`. Distinguish **validation** (the value is
checked) from **rule-independence** (the value is derived without the incumbent
rule) — they are different questions with different answers here.

### Lane C — freedom from fitting

Question: **can the tower be built without fitting `(a_k, b_k)` to any swept
cell?**

W1 does it ab initio to `k = 9` and stops on memory. Undertow changes which
cells are fitted, not whether. Say what the real obstruction is, whether it is
intrinsic, and what the cheapest route past it would be. If you conclude the
obstruction is intrinsic, argue it about the family and not the instance.

## 4. Compute

**Agents do not run jobs.** `docs/r3-job-dispatch.md`. The test is
backgrounding, not size: anything you would background, wrap in `timeout`, or
tee and come back to is a job request to the lead, not a command you run.
Nothing runs on gympie. dalby and ayr are idle as of 07:20 EDT and are the
lead's to dispatch. Job requests carry wall / RAM / disk / cores, each labelled
MEASURED (at what scale) / EXTRAPOLATED (how far) / ASSERTED, plus **what
decision changes if the number comes out differently**. A job that changes no
decision is not dispatched.

Seconds-scale foreground reading and arithmetic is yours. `python3` on a banked
file is fine. Anything that would take minutes is a request.

## 5. Output

- Findings list first, into `results/undertow-review-queue.md`, before
  anything else.
- Then the lane file: `results/undertow-review-A.md`, `-B.md`, `-C.md`.
- **File before you halt.** Context is not a deliverable. Write results as you
  get them.
- Every lane that closes a candidate files **at least two successor rows** in
  the queue, different in kind rather than parameter tweaks. Half-formed rows
  are wanted. Cross-lane rows are wanted.

## 6. Stop conditions

A lane stops when its question is answered with evidence, or when it can say
precisely what would answer it and why that is out of reach. "I could not
determine this" without naming what would determine it is not a stop.
