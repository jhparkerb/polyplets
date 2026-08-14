# R1-D plan — adversary, the transport obstruction

2026-08-13. Charter: `docs/rook1-brief.md` §R1-D; goal text `docs/rook-parity.md:75-90`.

## Question, one sentence

State precisely what a size-preserving king→rook reduction must do to the
Motzkin cut information, or exhibit the obstruction — and separately, derive or
refute the asserted "diagonal-splice β ≥ 2" (rook-parity.md:86), queue row K2.

## Steps, in order

1. Read the closed record I must not re-derive: `results/rook1/R1-K.md` (esp.
   §1b), `results/kink-carry.md` (cut vocabulary), commit `210fb0b` message,
   `results/triangle-r3-involution.md` §2, and whatever in-repo file defines
   the king TM cut states. Product: a precise statement of what a king cut
   carries beyond a rook/Motzkin cut.
2. Derive the surplus: count/characterize the extra cut information king
   connectivity (diagonal adjacency) forces across a straight cut, versus the
   Motzkin matching vocabulary that suffices for rook. Product: §1 of R1-D.md,
   the requirement statement — what any size-preserving reduction must do with
   that surplus.
3. Attempt the obstruction as a counting/information argument: growth rate of
   distinguishable king cut states vs rook cut states at equal width, and why
   a size-preserving (β = 1, or even β < 1.61) map cannot re-encode the surplus
   into rook geometry without breaking locality. Product: §2, the obstruction
   or the honest "requirement only" fallback, labelled as a hand argument.
4. K2: diagonal splice. Define the splice family precisely, derive its blowup β
   from the geometry (worst case and typical), or exhibit a member with β < 2.
   Product: §3, with the derivation. Small exact foreground checks only.
5. File two successor queue rows, different in kind, per
   `docs/agent-types.md:51-54`.
6. `./scripts/check_receipts.sh`, then report to lead.

## Stop conditions

- Both the requirement/obstruction and the K2 verdict filed → stop.
- Any step needing compute beyond a foreground seconds-scale exact check →
  job-request queue row per `docs/r3-job-dispatch.md`, continue with desk work.
- Stop instruction from lead → write partials first, labelled.
