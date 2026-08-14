# Rook parity, round 1 — the desk day

2026-08-13. Launched from `docs/rook-parity.md` (the goal) under
`docs/rook-parity-team-process.md` (the ruled process). Round 1 is the "First
questions" day of `rook-parity.md:125-137`, run desk-only: **no fleet compute,
no engine, no gate-1 work.** Its whole product is the bar and the go/kill for
the route.

## Mission, one sentence

Measure what the incumbent's base actually is, measure `g` for the ab-initio
`P_k` tower, and decide whether the tower route to rook parity is alive — before
anything is built.

## The round's falsifiable deliverable

`docs/rook-parity-bar.md` (planned; it does not exist yet, and its absence at
the end of the day is what round failure looks like), written by the lead from
the lane files, containing
exactly four things:

1. the **numeric measured clause** of the bar (the incumbent's fitted per-term
   cost ratio over n = 24..30, with residuals, and the threshold a challenger
   must beat);
2. the **`g` verdict** against the thresholds pre-registered below, every number
   labelled MEASURED or EXTRAPOLATED with the anchor named;
3. the **Hankel verdict** for rook at small H, and whether it changes any king
   decision;
4. the **go/kill for the tower route**.

Absence of that file is round failure. `results/rook1/queue.md` closed per the
close protocol, and `make gate-receipts` green, are the other two conditions.

## Pre-registered kill thresholds — registered now, before any measurement

These are fixed at brief time and **the lead cannot convert a fired kill into a
go.** That takes jasonp, in so many words. (`rook-parity.md:106-113`, and the
postmortem's item 2: every stop failure in the triangle campaign was a waiver,
not a detection failure.)

A complete numeric partition of `g`, with no unassigned band: every value that
can come out of the measurement fires exactly one row. Revised 2026-08-13 on
R1-K's pre-registration audit (`results/rook1/R1-K.md` §Pre-registration audit),
before wave 2 spawned and before any `g` existed.

| quantity | threshold | consequence |
|---|---|---|
| `g`, ab-initio `P_k` cost growth | `g ≤ 3` | parity: composite base ≈ max(√3, √g) holds the goal |
| `g` | `3 < g < b²` | route survives but beats the incumbent only, not parity |
| `g` | `g ≥ b²` | **the tower route is killed.** Round 2 does not launch on it |
| measured clause of the bar | set by R1-A on this day, before any challenger exists | a challenger must come in strictly below it on the same n = 24..30 window |

`b` is the incumbent's per-n cost base and `b²` is the boundary because the
composite base goes as `√g`: the tower beats the incumbent iff `√g < b`. **The
registered threshold is the function `b²`, not a negotiable number** — that is
what makes it pre-registered while R1-A and R1-B run in parallel. Under the
current best reading `b = 2.42`, the boundary is `2.42² = 5.856`; R1-A's
reconciliation of the 2.42 / 1.61 / 1.73 contradiction fixes `b`, and the
resulting number is registered in `docs/rook-parity-bar.md` (planned) *before*
`g` is compared against it. Not 5.9: a `g` in [5.856, 5.9) would satisfy a
threshold written as 5.9 while actually exceeding the incumbent.

`g ≤ 3` exactly, not "≲ 3": parity is `√g ≤ √3`, and a measured 3.05 is a kill
of the parity claim, not a conversation. The goal file's "g ≫ 6"
(`rook-parity.md:111`) is the loose form; this table is the binding one, and the
bar file restates it so round 2 cites one number.

R1-A proposes the measured-clause number; it is registered on this day and not
renegotiated afterwards. Chartering "beat X" after measuring the challenger is
round 2 of the triangle campaign again.

## What is CLOSED — do not re-derive, do not re-propose

Each of these cost something already. Re-opening one requires new evidence
named in a queue row, not an argument.

- **The 2.67 = √λ_king pin is dead.** The incumbent is already below it under
  every admissible λ (sandwich 6.543 ≤ λ ≤ 9.3154 ⇒ √λ ∈ [2.558, 3.052]).
- **√λ_rook = 2.015 is nobody's cost.** Polyomino counting is proven
  `O(n^{5/2}·√3^n)` (Barequet–Moffie 2007); empirical with pruning ≈1.41^n.
- **King→rook transport is out of scope as a mission.** The literature is
  directed-only (Gouyou-Beauchamps–Viennot 1988, Bousquet-Mélou–Rechnitzer 2002,
  Bacher 2015). Arithmetic kill for the obvious bijection family: a reduction
  with linear size blowup β beats the incumbent only for β < ln 2.42 / ln 1.73 =
  1.61, and king-cell → 2×2 block is β = 4, diagonal-splice β ≥ 2.
- **Every in-repo localization probe is measured dead**: 45° rotation falsified
  (commit `210fb0b` — and it is the one published rook-side base improvement
  since 2001, so it improves rook and worsens king), strong-product factoring
  negative, MPS χ ~ λ^(H/4), mod-p Hankel no collapse.
- **`min(H,W) ≤ n/2` does not apply to king animals** — a diagonal staircase has
  min(H,W) = n. `results/finite-lattice-crossover.md` is quotable only for its
  FLM-doesn't-stack conclusion, and its "remaining speed is engineering" line
  rests on the floors package, two-thirds of which `results/r4/r4-floors.md`
  found over-applied or false as stated.
- **The ab-initio `P_k` ceiling is k = 9** (53 GB peak, 66 min, 16 threads,
  dalby); k = 10 scales past dalby's 125 GB. Extending needs a state-space
  reduction, not more cores (`results/severance-w1-anchor-cut.md` §Ceiling).
- **Rook is a ground-truth source, not a method testbed.** `build/g2
  --rook-bishop` counts rook-connected polyplets, which are polyominoes,
  cross-checked against A001168. There is no rook transfer matrix in-tree and
  building one is days.
- The polyomino record is **n = 70** (Barequet–Ben-Shachar, ALENEX'24 /
  Algorithmica 2026), not the n = 56 that project docs still say.

Nothing here tells you what to try. That is deliberate.

## Lanes

Five spawns, all Fable, desk-only. R1-K runs alone and first; the other four
spawn only after its PASS file exists.

| id | type | question | deliverable (per `docs/agent-types.md`) |
|---|---|---|---|
| R1-K | adversary | is this brief launchable | `results/rook1/R1-K.md` + `results/rook1/R1-K.PASS` on pass |
| R1-A | scout | what is the incumbent's base, measured | `results/rook1/R1-A.md` |
| R1-B | scout | what is `g`, and is there a reduction past k = 10 | `results/rook1/R1-B.md` |
| R1-C | scout | rook Hankel ranks at small H | `results/rook1/R1-C.md` |
| R1-D | adversary | the transport obstruction, stated or exhibited | `results/rook1/R1-D.md` |

Three of the eight spawn slots are held for queue-successor re-dispatch. Under
the cap (`rook-parity-team-process.md` #6) re-dispatching an agent that has
already filed is free and preferred over a fresh spawn.

### R1-K — adversary on this brief, kill authority

Two questions, both required, verdict per question.

1. **Is the premise true?** Re-derive the numbers this brief and
   `rook-parity.md` rest on, from the repo: the 84% cpu split (1,116,858 +
   3,329,644 of 5,318,465 s), the β < 1.61 bound, the √λ sandwich arithmetic,
   and the three mutually contradictory in-repo base claims at
   `results/kink-carry.md:46`, `results/kink-carry.md:69`, and
   `results/ns_a40/PROVENANCE.md:19,25`. Citations must be readable on this
   branch.
2. **Does each chartered deliverable move a gate?** For each of R1-A/B/C/D:
   which gate of `rook-parity.md:106-123` does it move, by how much, and would
   total success still leave the bar untouched? A lane that answers its question
   perfectly and moves nothing is the failure this question exists to catch.

Verdict is PASS or KILL, per lane and for the round. **A KILL blocks the
launch**; the lead may appeal to jasonp and may not overrule. On PASS, write
`results/rook1/R1-K.PASS` (planned — you create it) containing the one-line
verdict; the wave-2 spawns are
gated on that file existing.

### R1-A — scout, base anatomy audit

From existing run logs only, seconds-scale work at most. Fit the incumbent's
per-term cost ratio over n = 24..30 with residuals, and reconcile the 2.42 /
1.61 / 1.73 contradiction: say which is the engine's base, which is a bound on
something else, and which is wrong. Deliverable includes the **proposed numeric
measured-clause threshold** for the bar, with the window and the fit stated
precisely enough to re-run.

### R1-B — scout, `P_k` tower feasibility

Fit `g` from the severance records (k ≤ 9 measured,
`results/severance-w1-anchor-cut.md` §Ceiling), and survey what a state-space
reduction past k = 10 would have to be. Check `docs/middle-kingdom-plan.md` for
overlap before calling anything new, and grep the existing results and build
tree before naming a tool. Report `g` against the pre-registered thresholds
above, each number labelled MEASURED (at what k) or EXTRAPOLATED (how far).

### R1-C — scout, rook Hankel ranks at small H

Ground truth is `build/g2 --rook-bishop` — check `build/` before writing
anything new; `build/g2` is the canonical Redelmeier. Seconds-scale on gympie,
or a job request to the lead for anything larger; **nothing in between.**
Verdict: does rook show the char-2 crack that `results/triangle-r3-involution.md`
§2 measured on king (~0.44·2^H against mod-p 2.5–2.8×/height vs ~3× states), or
not — and does the answer change any king decision. "No" is a full result here.
Your verdict must **name the specific king decision that changes, or say
"changes nothing" in those words** (R1-K's condition on this lane): a verdict
that leaves that open is not filed.

### R1-D — adversary, the transport obstruction

The one "find a route" lane the goal charters, run as its negative
(`rook-parity.md:88-90`): state precisely what a size-preserving king→rook
reduction must do to the Motzkin cut information, or exhibit the obstruction.
Either outcome files as a negative-map entry. Two successor queue rows are
mandatory (`docs/agent-types.md:51-54`).

## Compute rules

**Desk-only round.** The test is backgrounding, not size: anything you would
background, wrap in `timeout`, or tee and come back to does not run on gympie —
it is a job request to the lead, filed as a queue row plus the full field block
in your deliverable (`docs/r3-job-dispatch.md`), and you continue with desk work
rather than waiting. Never a judgement call: `lean`/`lake`, anything under
`timeout`, anything multi-GB, anything already killed once. Agents do not run
jobs; the lead dispatches them, to ayr or dalby, never to gympie.

A dispatched job is not DONE until its artifact and log have an **in-tree path**
in this working tree. A number that exists only on a remote box is not a result.

## Controls in force from hour zero

- **Write-ahead** (`docs/agent-types.md`): `results/rook1/<id>.plan.md` before
  any other action; `ABOUT TO:` / `DONE:` lines in
  `results/rook1/<id>.progress.md` around every step; findings appended to your
  deliverable the moment they exist. Your context is not a deliverable.
- **Receipts** (`make gate-receipts`, `scripts/check_receipts.sh`): in any file
  under `results/rook1/` or in this brief, a status token — PROVED, VERIFIED,
  GREEN, RUN, CONFIRMED, PASSED, MATCHED — in a table cell or on a `status:`
  line **must carry an in-tree, non-empty path on the same line.** No path means
  the thing is WRITTEN, UNRUN, and no file may describe it otherwise. The gate
  is fail-closed and runs in `make`; a claim you cannot receipt is a claim you
  do not write.
- **Instruments**: every instrument you build or run gets a row in
  `results/rook1/INSTRUMENTS.md` — one line, its status, its receipt. Status is
  quotable only as a copy of a row there. This applies to the lead's files too.
- **Queue** (`results/rook1/queue.md`, append-only): every closed candidate
  files **at least two successor rows, different in kind** — not parameter
  tweaks. What would have to be different about the problem for this to work;
  whether an adjacent object has that property; what the obstruction proves
  about the family rather than the instance. Pruned near-misses go in the queue,
  never into a silent cap. Cross-lane rows are wanted.
- **Ledger**: the lead appends a row to `results/rook1/LEDGER.md` at every
  spawn. At wind-down the ledger must match the enumerated census or the round
  does not close.
- **Round close**: the queue closes only after that census confirms every agent
  stopped or explicitly handed off. Anything filed after close becomes round 2's
  first queue rows. Round 2 launches from queue rows and receipts, not from
  anyone's synthesis narrative, and not before 2026-08-14.

## Stop conditions

- A lane whose question is answered files, files its successors, and stops. It
  does not go looking for adjacent work.
- On any stop instruction: write what you have to disk **first**, labelled with
  what is partial and what was killed, then halt. Do not reconstruct or estimate
  anything you did not measure — missing numbers are marked NOT ESTABLISHED.
- `g > 6` from R1-B kills the tower route; file it plainly and do not soften it.
- Round-level: a round that advances no gate and banks no negative-map entry is
  a strike. Two consecutive strikes trigger a mission review with jasonp instead
  of a round 3.
