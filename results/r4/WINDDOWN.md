# Round 4 — wind-down record

2026-08-13, ~07:00 EDT, on jasonp's instruction: bring all agents to a close,
leave the compute running, save state. Findings are in the per-agent files
under `results/r4/`; open work is in `results/r4/queue.md`; every instrument and
its receipt is in `results/r4/INSTRUMENTS.md`.

## Agents — none running

Thirteen were dispatched; all have exited. Twelve filed a deliverable. One did
not, and the write-ahead rule is what caught it:

| agent | kind | filed |
|---|---|---|
| r4-a | scout — is the committed `--modp` the residue binary? | yes |
| r4-gen, r4-gen2..gen7 | generators (7) | yes, ~150 queue rows |
| r4-perf | scout — performance levers | yes |
| r4-inv | scout — INV-8 buildability | yes |
| r4-spinbuild | builder — the spin engine | yes, 1113 lines, compiles clean |
| r4-spinproj | scout — m=18..21 projection on measured constants | yes |
| r4-ladder | scout — H=17..19 re-plan | yes |
| r4-adv-ind, r4-adv-cost | adversaries (2) | yes |
| r4-tallband | scout — H=22..40 provenance | yes |
| r4-floors | adversary — the three floors | yes |
| r4-lean2 | builder — the Lean encoding layer | yes, `results/r4/r4-lean2.md` (28 KB) + `experiments/tristruct/r4_lean2_encode.lean` + rows R4-LEAN2-1..4 |

**CORRECTION, entered 07:05.** An earlier version of this file recorded
r4-lean2 as having died without filing. That was wrong: it was still working
when I checked at 06:52 — its progress file showed an unmatched `ABOUT TO`
because the step was in flight, which is the write-ahead rule working exactly
as designed — and it filed at 06:59. **All thirteen agents filed.** The lead
read a live progress marker as a death certificate; the correct action on an
unmatched `ABOUT TO` is to check whether the agent is still running before
concluding anything.

What does stand, because I verified it independently: `encode_faithful` and
`encode_faithful_colAt` in that source elaborate with zero output and axioms
`[propext, Classical.choice, Quot.sound]`, no `sorryAx`. The proof is real; the
story about how it was recovered was not.

## Jobs — left running deliberately

| job | box | purpose | state at wind-down |
|---|---|---|---|
| spin m=1..21 | dalby | T(40,20), T(40,21) mod 2 | RUNNING, m=19, ~88% of total work, launched 06:00 EDT |
| spin m=1..21 | ayr | same, cross-ISA | RUNNING, m=19, same point |

Both write `results/r4/spin_m21*.txt` plus a `.metrics` file on their own box
and log to `experiments/tristruct/r4_spin_m21*.log`. When they finish, the
comparison to make is `cmp` of the two output files — the engine is
deterministic across ISAs (GATE 0 outputs already matched at sha256
`691cd7a3…`), so anything other than byte-identical is a finding.

Two local `tail --pid` waiters are still attached to those PIDs and will
surface the exits if the session resumes. They hold no state.

Completed and logged this round: LG-JOB-1R (B1 residue H=12..16, 360 residues
green), PERF-JOB-1 (patch bit-exact, 1.12-1.28x), spin gates, spin m=1..16,
JOB-IND-1 at n<=8 and n<=10, the Lean funnel probe. Receipts in
`results/r4/logs/` and `INSTRUMENTS.md`.

## What the round actually bought

1. **T(40,15) and T(40,16) — 21.64% of a(40) — banked**, recovered from
   untracked files on one machine, and checked against the literal 3x3
   flood-fill definition rather than only against the incumbent.
2. **`encode_faithful` and `encode_faithful_colAt` are proved**, sorry-free,
   axioms `[propext, Classical.choice, Quot.sound]`. This is the encoding layer
   `r4-adv-cost` §5 flagged as "priced on nothing" and the Lean lane's largest
   remaining risk after the crux. Recovered from a dead agent.
3. **The three floors are all over-applied, and two are wrong as stated**
   (`r4-floors.md`). The information floor's own number is **25,837x below**
   the incumbent's cost at H=21 (M(12) = 15,511 vs M(22)-1 = 400,763,222), so
   it excludes nothing affordable. The state floor is **false as literally
   stated**: GF(2) Hankel ranks of 58/112/229 at H=7/8/9 sit below cell-frontier
   counts of 322/834/2187, and the char-2 rank grows 0.44*2^H against Motzkin's
   ~3^H — about 1e6 against 4e8 at H=21, a cut-crossing representation ~400x
   smaller than the incumbent, already measured in this repo.
4. **T(40,21) is the thinnest cell in row 40**, not an over-attended one:
   Lean's `P_k` covers k <= 18, which at n = 40 is exactly H = 22..40, while
   k = 19 (H = 21) is deliberately unpinned with no holdout possible.
5. Measured constants replacing borrowed ones: 941.8 B/window; residue only
   2.40x faster than exact; the fast-modp patch 1.12-1.28x and **declining**
   with height; spin `ns_per_transition` flat at 13.97 over m=11..16, which
   re-priced m=18..21 from 22.6 thread-days to ~2.6 thread-hours.

## Process findings, all of them about the lead

- **Transmission loss with a sign.** `r4-gen7` R4-G7-00 found the round quoting
  instruments ahead of what was on disk, and every drift upgraded
  written-but-unrun to completed. Fixed by `INSTRUMENTS.md`; the cause was
  reporting terminal output that never became a receipt.
- **Gate claims without logs**, twice, charged by `r4-adv-ind` and then
  repeated by me on the cross-ISA check hours after I said I had fixed it.
- **"Seven gates GREEN" for a patch whose changes those gates do not reach** —
  the battery covers the exact-payload path, the patch is entirely in `--modp`.
- **The generator charter was violated twice.** `docs/triangle-round4.md` lines
  47-48 and 124 require generation to be *always* running. Agents here are
  one-shot, so "always" means relaunching on every completion; batching them
  into waves opened a 2.5-hour gap after wave 1 and a second gap at close.
- **The round was dispatched as measurement.** Nearly every brief pointed at
  cost, gates, provenance and repricing; no mathematical lane existed until the
  floors audit, which was dispatched last and produced the round's best result.

## The obvious next move

The floors audit reopened the argument space this campaign had written off. The
concrete object is the char-2 / Hankel realization: a cut-crossing
representation ~400x smaller than the incumbent, compliant with the information
floor, whose explicit basis does not yet exist. Round 3 dismissed it because
"a rank is an existence statement" — which is work not done, not an obstruction.
CKN have explicit bases for matchings and that analogue was cited and dropped.
Finding that basis needs no compute.
