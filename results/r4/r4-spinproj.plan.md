# r4-spinproj — plan

**Question (one sentence).** What does the INV-8 spin run at m=18..21 actually
cost, projected from tonight's fifteen measured points on dalby rather than any
borrowed anchor, and does it reach T(40,20) and T(40,21) mod 2?

## Steps

1. Read the governing docs and priors: `docs/triangle-round4.md` (done),
   `results/triangle-r3-spin.md`, `results/r4/r4-spinbuild.md` §3,
   `results/r4/r4-inv.md`, `results/r4/r4-adv-cost.md` §2.
   Produces: the design, the corrected geometry, the honest per-op number.
2. Pull the measured record from dalby (read-only ssh):
   `~/src/pm-b1-perf/experiments/tristruct/r4_spin_m16.log`,
   `r4_spin_gates.log`, and `~/src/pm-b1/experiments/tristruct/r4_a_modp_bpw.log`.
   Copy verbatim into the scratchpad; do not paraphrase heartbeats.
   Produces: per-m `states=`, `wall_s=`, `peak_rss_mb=` for m=1..16.
3. Fit growth on the fifteen points. Ratio series states(m)/states(m-1) and
   wall(m)/wall(m-1); fit log-linear over the tail where the ratio has settled;
   report residuals per point. Produces: fitted ratio + residual table.
4. Project m=17..21 for states, wall, RAM. RAM from the log's own
   states/peak_rss pairs (measured bytes-per-state), never the 38 B model.
   Mark interpolation vs extrapolation and the reach beyond data.
   Produces: projection table, labelled MEASURED/EXTRAPOLATED/ASSERTED.
5. Go/no-go against ayr 78 GB / dalby 126 GB, naming the single deciding number.
6. Gate battery: establish whether any oracle exists above H=16, and if not,
   state plainly what the production run's correctness evidence actually is.
7. Value of the two bits given T(40,20)=1, T(40,21)=1 mod 2 already recorded in
   `r3_spin_pipeline.log`: prior, what agreement buys, what disagreement means.
8. File the job request block and >=2 successor queue rows different in kind.

## What would make me stop

- The log does not carry per-m heartbeats with all three fields -> file NOT
  ESTABLISHED for the fit, report exactly what the log does carry, stop.
- The ratio series does not settle over m=10..16 (no stable geometric tail) ->
  report the projection as a bracket, not a point, and say the fit failed.
- The measured cost turns out trivially small -> say so plainly, do not dress a
  cheap route up as marginal.

## Hard constraints on me

No compute anywhere, nothing on gympie. Read-only ssh to dalby/ayr. No /tmp
(scratchpad only). No pkill/pgrep. Every number labelled.
