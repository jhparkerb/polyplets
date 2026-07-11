# HANDOFF — live state (updated 2026-07-11)

Live state only. Completed compute sessions (a(35), Even Keel, the utilization
redesign/deployment passes, the 2026-07-07 M(17)/dmirror/related-seqs jobs, the
terminal-sort investigation) are banked in `results/*.md`, `MEMORY.md`, and git
history — not repeated here. Read this file, then `MEMORY.md`'s index.

## Frontier
- **a(36) = 24629107617723857143962968288** banked+validated, `results/ns_a36/`
  (varint engine, dalby H19 long pole 3.28h). a(1)…a(36) all banked under
  `results/ns_a{n}/`; a(1)-a(20) match the b-file, a(21)+ chain-match each prior term.
- **P17 derivable+validatable** (fit real T(34,17)+T(35,18), holdout real T(36,19));
  wiring it makes a(37)'s top real height H19. **Atom Ledger** banked
  (`results/triangle-structure.md`): triangle dependency structure fully mapped,
  root-separation theorem proves no bounded-depth cross-column relation.
- **a(20) two-algorithm CONFIRMED 2026-07-11** (Redelmeier `build/g2` rev 7eab237 vs
  the TM engine): whole row n≤20 matches banked exactly, 0 mismatches. Banked
  `results/redelmeier_row20/`. Two-algorithm frontier now **20**.
- **Terminal Velocity (a(21) whole-row push) — kernel optimized + fleet validated,
  LAUNCH PENDING jasonp's go.** g2 kernel now **2.06× faster** (rev 7eab237→HEAD):
  L1 terminal pure-count (85% of nodes → branchless load+sum), L3 compile-time
  neighbour offsets, L4 u16 untried, built with clang++ (Makefile G2CXX). L2/gcc-PGO/
  -mcpu measured neutral-or-worse and dropped. Ledger `results/terminal-velocity.md`.
  Fleet (dalby 80 + ayr 32 + gympie 10 cores; per-core 1.0/1.28/3.0): **a(21) ETA
  ~14h**, well under the <24h target (dalby-alone 26h). Row-18 fleet validated
  (all 18 rows match banked across 3 ISAs); row-19 validating. Launch/gather via
  `scripts/g2_fleet_launch.sh 21 12 2400` + `g2_fleet_gather.sh 21 2400`; robust
  poll-waiter (NOT tail --pid). **Reach:** optimization+fleet puts a(22) whole-row
  in reach at ~3.9 days (was ~15 days). Acceptance: rows 1..20 vs banked + row 21 ==
  6954084405510437.

## Rigorous λ bounds (NEW 2026-07-11)
- **Two-sided rigorous bracket 5.828 ≤ λ ≤ 9.3153**, numerical λ≈7.111 inside.
  Lower: directed/multi-directed king animals (3+2√2 exact, 6.475 Bacher). Upper
  (first ever, ours): Bui-style finite-type convolution certificate, `x=2147/20000`,
  machine-verified in exact rational arithmetic.
- Derivation `docs/proofs/polyplet-upper-bound.md`; certificate `experiments/king_certificate.py`.
  **Certificate Squeeze** (docs/certificate-squeeze-plan.md): P1 (exact cert) + P2 (slack
  audit) done; **P3 not pursued** — the over-count is the connectivity wall (diffuse,
  compounding, non-local), floors this method class above λ. Paper paragraph + `bui2025`
  bib entry landed in `paper/polyplets-report.tex`.

## OEIS submission — gated on jasonp's viva
Batch staged and checklist-clean (`oeis/README.md` checklist; b-files
`results/b*_upload.txt` for all six sequences — A006770+A030233 to a(33), the four
D-dependent to n=32; a(34)+ staged as conjectured comments). **Submission is jasonp's,
gated on his own readiness process** (OEIS AI policy makes the author personally
responsible; `docs/oeis-ai-policy.md`).
- **Viva** (local-only, git-excluded: docs/viva-exam.md, viva-reserve.md [chmod 000],
  viva-state.md, drill{1,2}-*.md): first exam 56.5/100 vs bar ≥80. Drills 1 & 2 graded;
  cold retake variants (V8/V12/V13, V18/V19/V20) still pending after a spacing gap.
  Full state: docs/viva-state.md.
- Before submit: jasonp rewrites all staged %C in his own words (Claude meaning-checks
  only); signature dates → actual submission day; pink-box replies jasonp's alone.

## Paper (`paper/polyplets-report.tex`)
Computational-report form, five external review rounds + self-check. Growth §3 confluent
3-param fit (Δ₁=1/2, λ≈7.111). Now includes the rigorous **upper-bound** paragraph
(above). `paper/verify_claims.py` — 397+ checks GREEN (parses tables from the .tex).
Compiles clean (no undefined refs/citations). **TODO: final read-through** after the
close-out passes.

## Open threads
- **Lean proof** (branch `lean-diagonal-proofs`, `polyplets/PROOF-STATUS.md`):
  (a) finiteness, (b) row profile, (c-fwd), (d-local) done+green; remain (c-rev),
  (d-global gap≤2), (e) offset-chain count.
- **Unmerged engine branches — jasonp's call whether/when** (engine work deprioritized
  per the close target): `tm-hotpath-optim` (RunRecord shrink + pmr allocator, real
  4.47% dalby win, gates+ASan clean); `redesign` / kink-sharded (K-shard private-sweep
  kernel, opt-in `--kernel kink-sharded`, real 4.93x at H14/maxn26, still not the default
  and not head-to-head'd at dominant-height scale).
- **steal-tail diagnostic** (`results/steal-tail-h18.md`): banked, not deployed.

## Remaining work ledger
1. **Paper final read-through.**
2. **Viva cold retakes**, then %C authorship pass (jasonp's own words), then jasonp submits.
3. **Lessons-learned document** (jasonp + Claude) — jasonp's explicit ask; after compute
   and paper, BEFORE submitting. The six postmortem failure classes as day-one practices
   are captured in MEMORY.md ([[next-project-practice]]).

## Starting a fresh session from here
Read this file, then `MEMORY.md`'s index (auto-loaded) for standing practices. No open
thread needs immediate action; pacing is jasonp's (viva retakes, whether to merge the
unmerged engine branches, whether to revisit a(37)+ compute given the reach ceiling).
