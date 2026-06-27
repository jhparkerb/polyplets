# 04 — multi-machine via height-split

## Capability today

The orchestrator is **strictly single-host**: all map/merge units are local
processes coordinated by goroutines, semaphores, and the local filesystem. There is
no network/RPC/ssh code anywhere in `orchestrator/`.

But the computation is **height-decomposable**, exactly like the old engine:

- `a(n) = Σ_H T(n,H)` (sweep.go:45).
- `Run` loops `for H := startH; H <= maxn` (sweep.go:92); each height starts from its
  own independent seed (`WriteSeedPolyrun(..., H, ...)`, sweep.go:101–105) and produces
  its own contribution `hTri` (sweep.go:140), accumulated into the triangle
  (sweep.go:112–117). The checkpoint `Triangle` is additive across heights
  (checkpoint.go:30–33).

So per-height sweeps can run on different machines and the per-machine triangles
**sum** to the full triangle. This is the old `an_fold_parallel` split (ayr heights +
dalby heights → combine) reimplemented on the new engine — a scheduling layer, **not**
a distributed-systems build. (True intra-height column distribution across hosts would
be a real network build and is explicitly out of scope.)

## Design

Partition the height set {1..maxn} across machines; each machine runs `orchestrate`
over its subset; a combine step sums the outputs and runs the gates.

### Implementation

1. **`--heights LIST` flag** (main.go) — e.g. `--heights 1-12` or `--heights 17,19,20`.
   `Run` iterates the parsed set instead of `1..maxn` (sweep.go:92). Resume key becomes
   (height-set, H, col); the checkpoint already stores H/col, so only the loop source
   changes. Each height is the atom — assigned to exactly one machine.

2. **Per-machine output** — write the machine's final `Triangle` to
   `runs/<run>/triangle_<host>.txt` (`n  value` lines). This is just the existing
   `result.Triangle` (main.go:134-ish) dumped to a file.

3. **Per-height rows (recommended)** — also emit each height's `T(n,H)` row to
   `runs/<run>/h<H>.out` (same format the old engine used). `map_worker` already emits
   `tri H n V` (map_worker.cpp:107/112), aggregated into `hTri`; write `hTri` per height
   at height-done. Two payoffs: (a) finer combine granularity, and (b) **direct
   cross-check against the salvaged old-engine `h1..h16.out`** — byte-compare per cell.

4. **`combine` tool** (`orchestrator/cmd/combine`) — read all `triangle_<host>.txt`
   (or `h<H>.out`) across machines, sum by n, write the final triangle + a(n) column,
   then run the verifier (`verify/`: row-sum, growth gate, `--compare`). Refuse to
   combine if the per-machine height sets overlap or do not cover 1..maxn (each height
   exactly once).

5. **Driver script** (`scripts/`) — launch per-host `orchestrate --heights <subset>` in
   a tmux window per the long-jobs-tmux rule, with `tail --pid` waiters, then rsync
   outputs to the combine host. Mirrors the retired `an_fold_parallel.sh` + dalby/ayr
   split.

### Height balancing

Per-height cost is unimodal in H (peaks near H≈n/2; for a(21), H9 was the largest
T(21,H)). Assign heights to machines to balance **total predicted cost** (greedy /
longest-processing-first using the doc-02 predictor's per-height estimates), not by
count. Tall heights are cheap, middle heights dominate.

### Sizing constraint

The largest single height must fit one machine's RAM (a height is indivisible here).
For a(22)/a(23), check the peak-height RAM against the target box before assigning.

## Scope and timing

Not needed for a(21): it fits dalby alone, and ayr is occupied with the old-engine
cross-check. Multi-machine is the lever for **a(22)/a(23)** (the a(23) record), and
re-enables ayr + gympie once they free up. **Phase B** — build it while a(21) runs.

## Effort

~half day: `--heights` flag + per-height output + `combine` tool + driver script.
