# R1-K plan (pre-launch adversary, rook round 1)

Role: audit docs/rook1-brief.md before any lane spawns. Kill authority. No generation.

Steps, in order:
1. Read docs/rook1-brief.md, docs/rook-parity.md, docs/rook-parity-team-process.md
   (control #5), docs/agent-types.md (write-ahead rule).
2. Premise audit (Q1), each item verdict CONFIRMED / WRONG / NOT ESTABLISHED:
   a. 84% cpu split: re-derive 1,116,858 + 3,329,644 vs 5,318,465 s from repo
      artifacts for a(40) phases B and C, not from the brief.
   b. beta kill: recompute ln 2.42 / ln 1.73 exactly (python3), check 1.61 claim.
   c. sqrt-lambda sandwich: sqrt(6.543), sqrt(9.3154), interval [2.558, 3.052],
      and whether 2.67 lies strictly inside (pin unfailable-by-vacuity claim).
   d. The three contradictory base claims: read results/kink-carry.md:46,
      results/kink-carry.md:69, results/ns_a40/PROVENANCE.md:19,25; state what
      each asserts and about what quantity.
   e. Citation sweep: every repo path + line number cited in the brief is
      readable on master and says what the brief says. Spot-check rook-parity.md
      citations that lanes depend on.
3. Gate audit (Q2): for each lane R1-A..R1-D, name the gate (rook-parity.md:106-123)
   it moves and answer the hostile null (total success moves nothing?).
   Audit the lead for silent caps / narrowing dispatch / leaked candidate lists.
4. Pre-registration audit: kill thresholds fixed before measurement; round
   deliverable falsifiable.
5. File findings to results/rook1/R1-K.md as they exist; queue rows for
   out-of-charter items (>=2 if I close something).
6. Verdicts per lane + round; if round PASS, write results/rook1/R1-K.PASS.
7. Run ./scripts/check_receipts.sh; then report verdicts to lead.

Compute: desk-only (grep, Read, small python3). No lean/lake, no fs-wide scans.
Progress discipline: ABOUT TO / DONE lines in results/rook1/R1-K.progress.md
around every step.
