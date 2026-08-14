# R1-C plan — rook Hankel ranks at small H

2026-08-13. Scout, rook-parity round 1. Charter: `docs/rook1-brief.md` §R1-C.

**Question (one sentence):** does rook show the char-2 Hankel-rank crack that
`results/triangle-r3-involution.md` §2 measured on king (~0.44·2^H, mod-p growth
2.5–2.8x/height vs ~3x states), and what specific king decision does the answer
change (or "changes nothing").

## Steps

1. Read `results/triangle-r3-involution.md` §2 and whatever script produced it,
   to pin the exact object: which matrix, over what data, what "rank at H"
   means, and how char-2 vs mod-p were computed. Produces: a precise
   restatement in R1-C.md §1.
2. Inventory `build/` and `experiments/` for existing tools that can produce
   the rook-side analogue of that data (g2 --rook-bishop is counts only;
   the Hankel object may need per-cut or per-height data). Produces: a
   data-availability verdict — computable seconds-scale on gympie, or a job
   request, or structurally unavailable without the (out-of-scope) rook TM.
3. If seconds-scale: write `experiments/rook1/rook1_R1-C_hankel.py` (planned
   name; see the revision at the end of this file) (or reuse
   the king script with a rook data source), compute char-2 and mod-p ranks for
   rook at the same small H range, log beside the script. RED control: plant a
   corrupted input (bit-flipped matrix entry / truncated sequence) and show the
   pipeline rejects or visibly changes — a rank routine that never went red is
   not evidence.
4. Verdict: crack present / absent / not measurable at desk scale, with
   numbers, and the NAMED king decision it changes or "changes nothing".
5. File ≥2 successor queue rows different in kind; run
   `./scripts/check_receipts.sh`; stop.

## What would make me stop

- Step 2 shows the rook analogue requires a rook transfer matrix (none
  in-tree, days to build — chartered out of scope): file that as the finding,
  state what data WOULD decide it as a job request or round-2 row, and close
  with the verdict "not measurable at desk scale" plus the king-decision
  clause. That is a full filing, not a failure.
- Any computation that I would background, wrap in timeout, or tee: becomes a
  job request per `docs/r3-job-dispatch.md`; I do not run a small version
  locally while waiting.

## Revision, appended by the lead 2026-08-14

Step 3's script was filed as `experiments/rook1/rook1_R1-C_rank_probe.py`, not
the `..._hankel.py` planned above. The plan is not rewritten, per the
write-ahead rule; the planned name is labelled in place and the actual name
recorded here. `make gate-citations` is what surfaced the discrepancy — a plan
citing a path that was never created.
