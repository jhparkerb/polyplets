> **Status: written, not launched.** Nothing here runs without jasonp's
> explicit go.

# Plan — tower levels d = 9..12

2026-08-11. Follow-up to round 2 (`cae6e43`), scoped by
`results/triangle-r2-extension-scout.md` §7 item 2. Read that file and
`results/triangle-r2-tower-mod81.md` before starting; this plan assumes both.

## What this is and is not

Round 2 closed the mission that motivated the tower: the row-40 H = 15..19
cells sit below the proved sharp onset n ≥ 2k+1 and are outside the method's
validity at every depth. **This plan does not reopen that.** It buys two
things the scout identified as the knee of the value/cost curve:

- **+12.7 unit bits against enumeration error** over 8 more enumerated
  law-free cells, in the same currency as the (35,21) check that round 2
  landed — the only bits the campaign has ever earned against enumeration
  error rather than against formula-chain error.
- **The genuine structural break.** Round 1 recorded a clean break at d = 8;
  the scout showed that was a below-onset scan artifact and the real break is
  at d = 9. The m = 10 tower settles which of three things d = 9 actually is:
  longer period, later start, or true aperiodicity of the 3-automatic target.
  Nobody currently knows, and it is the last unexplained qualitative feature
  of the family.

Cost: one box, one Python core, roughly a day — inside the free-rein line.
Not a fleet job, not a campaign.

## Preconditions

1. **d = 8 LB certificate first** (scout §7 item 1, one session, not yet run).
   Agent 2's Lagrange–Bürmann route applies verbatim now that the d = 8 target
   is known period-3 with cycle (0,1,1) from k = 8. Until that runs, d = 8 is a
   verified tower level with a measured cycle, not a theorem. Doing it before
   d = 9..12 means the d ≥ 9 work extends a proved base rather than an
   observed one, and it retires the corrected round-1 table row.
2. Round 2 committed and green. Done at `cae6e43`; `make` was clean except the
   pre-existing `gate-citations` red on `docs/notary-simplify-deferred.md`,
   which belongs to the notary work and is not ours to edit.

## The work

Levels m = 10, 11, 12, 13 (moduli 3^11 .. 3^14, i.e. d = 9..12), built the way
m = 9 was built in `experiments/tristruct/r2_scout_d8.py`. Per level:

1. **Weight enumeration.** Extend the DP over the newly-entering clusters for
   the level. This is the whole wall-clock; the scout measured 351 s to reach
   d = 8 and models ×5–15 per level thereafter, running conservative-high by
   about ×3 at short range. Cells parallelize perfectly if it drags.
2. **Master equation and G at the new modulus**, then the four checks the
   scout ran at every level and that must not be skipped:
   - fixed point vs. banked h_k for k ≤ 17,
   - explicit monic curve ≡ 0 as a series identity,
   - G vs. banked g_k,
   - family residues on the derived series out to k = 55.
3. **Target cycle** for the level's family, recorded whether or not it is
   periodic. If d = 9 is aperiodic, that is the finding — write it down as such
   rather than searching for a longer period until one fits.
4. **Enumerated-cell checks.** For each family cell in the level, quote
   `triangle.py`'s `provenance(n,H)` and state the prediction and the banked
   value. H ≥ 22 is wired P_k for every n and buys zero enumeration bits;
   H = 3..21 is real sweep and is where the bits live.

## Guards, earned by round 1 and round 2

- **Scan onset explicitly.** Round 1's phantom d = 8 break came from including
  cells with k < d, below onset. Every scan in this work states its onset
  filter in the output, not just in the code.
- **Flag DP-only weights per level.** Agent 3's finding 2: the newly-entering
  weights' mod-3^j digits are the entire exposure at each level, and from
  d ≥ 8 up they are all DP-only — direct enumeration cross-checks do not
  scale. Name them per level; do not let the exposure become invisible by
  being uniform.
- **Two bit-counts, first line**, per the round-2 brief's rule 3: bits against
  enumeration error, and bits against formula-chain error with what they are
  conditional on.
- **Scoring is `docs/skeptical-reader-standard.md`.** Every result opens with
  its disclosure block; results without one are not scored, and the
  automatic-zero list applies in full.
- **Sensitivity, not just agreement.** A level's checks passing means nothing
  unless a corrupted weight would have broken them. Agent 3's corruption
  battery is the model; run the equivalent at each new level.
- Standing project rules apply unchanged: exact arithmetic, named scripts under
  `experiments/`, no stdin jobs, no `/tmp`, no binaries outside `build/`, the
  run in a tmux window foregrounded and tee'd to a log, no jobs on gympie.

## Stop conditions

Stop and report, rather than pushing on, if any of these fire:

- A level's checks fail against banked h_k or g_k. That is either a weight bug
  or a real limit of the gas formalism, and it outranks finishing the tower.
- RAM binds before wall-clock at the wide cells. The scout flagged
  (6,7)-class state dictionaries as unmeasured and did not model them.
- A level costs more than ~5× its predecessor's measured wall. The scout's
  model says ×5–15 is expected, so this is not an alarm by itself — but it
  means the d = 13,14 question has been answered in the negative and the run
  should end at whatever level completed.
- d = 12 completes. **Do not continue into d = 13 on momentum.** That is a
  fleet-week decision and belongs to jasonp, not to this run.

## Deliverable

One file, `results/triangle-tower-d9-d12.md` (planned, does not exist yet): the
per-level table (modulus,
interior terms, curve degree, new weights, measured wall), the target cycle or
aperiodicity finding at each d, the enumerated-cell check table with
provenance, the two bit-counts, the DP-only exposure list, and the measured
cost curve set against the scout's model — the last of these is what a future
d = 13 decision would rest on.
