# HANDOFF — 2026-07-05

Frontier **a(34) = 515316838423862758858377704**, banked+validated, term chase
**parked**. **MERGED TO MASTER 2026-07-06** (master is the repo's public
face; kink-carry remains the working branch). Big tidy DONE — README.md is
the fork-and-reproduce entry point. Durable facts live in `MEMORY.md`,
`results/*.md`, `README.md`, and git history — this file is the live state.
GitHub repo RENAMED to `jhparkerb/polyplets` 2026-07-06; remotes updated
on all three hosts. Local dirs stay `~/src/polyominoes` until the running
jobs finish (their cwd lives there).

## Frontier / what's banked
- **a(1)…a(34)** all banked under `results/ns_a{n}/` (triangle, PROVENANCE,
  perheight, cost_profile). a(1)-a(20) match the b-file; a(21)-a(34) chain-match
  each prior term; ayr cross-ISA verify folded into a34 PROVENANCE.
- **Diagonal closed forms P_2…P_15 wired** (`orchestrator/sweep.go`
  diagCoeffTable, `diagonalStripValid` k≤15); deriver `scripts/derive_pk_fast.py`.
- **Symmetric counts (Hall of Mirrors, `cpp/sym/symtm.cpp`)** — all four types
  built, gated (`tests/gate_symtm.py`) and byte-matched to `runs/sym24/`:
  - **r90, r180, hmirror: n=34 banked** (gympie `runs/sym34/`;
    r180(34)=48710062997772, hmirror(34)=17385821908346).
  - **dmirror: n=32 banked** (`runs/sym32/dmirror.out`, D(32)=2156235549286;
    32-strip farm dalby+ayr complete 2026-07-05, prefix-matches sym24+sym28).
    Engine is the **Shrink Ray** compact-frontier rewrite (b358e39): flat
    sharded storage, ~1.6× RAM + ~2× speed vs the unordered_map frontier
    that OOMed dalby. Farm cost: dalby S=26..31 3.0M cpu-s / ayr S≤25
    1.7M cpu-s.
- **Related sequences: all five banked to full current reach**
  (`results/related-seqs-n32.md`): A030233 to n=34; the D-dependent four
  (A030222/34/35/194596) to n=32. n=33 for the four lands with the dalby
  run (T3, P_4-assisted — OEIS comment-only). Combiner
  `scripts/derive_related.py` via symdir `runs/sym32.derive/` (symlinks
  sym34 r90/r180/hmirror + sym32 dmirror); validates all 95 known OEIS
  terms, /4 and /8 divisibility asserts.
- **OEIS staging (2026-07-05)**: b-files `results/b*_upload.txt` for all six
  sequences (A006770+A030233 to a(33), the four D-dependent to n=32);
  a(34)/A030233(34) staged as *conjectured comments*, deliberately out of
  the b-files (no held-out P_16 check until a(35)). Entry files
  `oeis/A*.txt` updated with %C/%E, signatures normalized to full-date
  form. **Pre-submission checklist** (from jasonp's past editor threads) is
  in `oeis/README.md` — check every batch against it; signature dates must
  be set to the actual submission day. Submission is jasonp's.
- **dmirror diagonal quasi-polynomials** (`results/dmirror-diagonals.md`):
  d(S,S+k) is period-2 quasi-polynomial, degree k per parity class, leading
  S^k/k!, onset ≈2k+2. **P_0..P_4 pinned BOTH parities** (P_4-odd pinned by
  the completed n=32 farm's S=23 strip; P_4-even also cross-validated by two
  independent methods); **P_5 both parities fitted** via the cumulant/exp
  form (`scripts/dmirror_pk_exp.py`), now with 6 exact witnesses/parity —
  unchanged from the 4-witness fit (forward confirmation); level 6 refuses.
  GF-basis structure: G_k = N_k(x)/((1-x)^(k+1)(1+x)^k), N_k(±1) = (±2)^k
  for k≥1; G_k generates the polynomial law (raw counts agree in-regime
  only — paper wording fixed accordingly). No low-order bivariate closure.
  These formulas replace the RAM-impossible sparse strips: n=33 needs only
  P_4 (direct S≤28), n=34 only P_5 (direct S≤28).
- **Paper (`paper/polyplets-report.tex`)**: computational-report form,
  through five external review rounds + one big self-check round.
  Growth §3 upgraded to the confluent 3-param fit (Δ₁=1/2, λ≈7.111,
  θ→-1.02 emergent; `paper/lambda_fit.py`). GF bound recomputed beyond
  frontier (a(35)≥5.07e26, a(40)≥4.27e30; 16% capture at 34).
  **`paper/verify_claims.py` re-targeted at the full report — 397 checks
  GREEN** (parses tables from the .tex; caught + fixed 3 overclaims:
  G_k definition, residual-factor claim, N_k boundary k≥1). Restored
  91bdcdc-deleted data files it needs (results/fixed_height_gfs.txt etc.).
  Remaining TODO: n33-cost (job-gated).

## Jobs landed (2026-07-07 early morning; both started 2026-07-06)
- **dalby — M(17) max-hole-area sweep DONE 2026-07-07 04:27** (78-way
  split, wall 74,870s ≈ 20.8h, 4.928M cpu-s ≈ 1369 core-h). **Result:
  M(17)=28 — confirms Conjecture 1's prediction exactly** (fitted on
  n≤16, no forward test until this run). results/maxhole.txt pulled to
  the Mac (was stale at n≤16 locally, now synced through n=17). Paper
  updated (`paper/polyplets-report.tex`, the M(n) paragraph + Conjecture
  1 + open problem block): verified range n≤16→n≤17, next untested
  prediction is now M(18)=32 (exact, no rounding ambiguity).
- **ayr — dmirror n=33 cross-ISA recompute DONE 2026-07-07 03:34**
  (queue S=25,24,23,22,21,20 fully drained). **Cross-ISA byte-compare
  (ayr x86 vs dalby ARM): ALL SIX STRIPS MATCH** (S=25 matched earlier;
  S=24..20 matched this morning) — closes the "S≤25 compare pending"
  item in `results/related-seqs-n33.md`.
- ~~dalby n=33 direct strips~~ **DONE 2026-07-06 07:39** (24.0h wall,
  6.71M cpu-s, peak 126.2GB) — **completion drill EXECUTED**: strips on
  gympie runs/sym33/, all n<=32 prefixes byte-match n=32 farm (413/413);
  **D(33)=5475149862148** via fail-closed `scripts/dmirror_hybrid_sum.py`
  (closed forms reproduced 124 overlap cells before supplying 15 sparse
  cells); companions n=33 (T3) banked results/related-seqs-n33.md + staged
  as conjectured OEIS comments; **P_5-even conventionally PINNED** (equals
  exp fit; P_5-odd stays fitted, 7 witnesses; level 6 refuses); paper
  updated (D(33) ‡ cell, companions block, n=33 cost, dagger narrowed),
  verify_claims 398 GREEN.
- **n=34 dmirror: DECLINED 2026-07-06** (jasonp, at the close deadline).
  Measured n=33 peaks supersede the old ~90-160GB estimate: S=28@34 (k<=6)
  extrapolates to ~175-200GB and S=27@34 (k<=7) similar, vs dalby's 189GB
  incl. swap — marginal-to-infeasible, and P_6 (the formula escape) is
  unpinnable without n=34 data (circular). If ever revisited: probe
  S=28@34 alone first. The related-seqs reach is final at n=32 (T2) /
  n=33 (T3, comments); term chase for a(35)+ stays parked.

## Data ceiling (why the term chase is parked)
- **P_16 is derivable** (fit from T(33,17)+T(34,18), self-consistent) but has
  **no independent holdout** until a(35); a(34)'s top cell has no closed-form
  cross-check. More terms need a fresh sweep — not planned pre-close.
- **Transfer-matrix Option 5** (`scripts/diag_transfer_gen.py`) infeasible:
  state count ~7.4×/k. Dead end without a rewritten engine.

## Open independent threads
- **Lean proof** (branch `lean-diagonal-proofs`, `polyplets/PROOF-STATUS.md`):
  (a) finiteness, (b) row profile, (c-fwd), (d-local) done+green; remain
  (c-rev), (d-global gap≤2), (e) offset-chain count.
- **Steal-tail diagnostic** (`results/steal-tail-h18.md`): banked, not
  deployed (trusted config).

## OEIS submission readiness (supersedes the hard 2026-07-06 date)
Batch is staged and checklist-clean, but **submission is now gated on
jasonp's own readiness process, at his insistence** — the OEIS AI policy
makes the author personally responsible for correctness, and editors now
routinely ask "how much of this is AI-generated?". Research on the policy
+ accepted/rejected precedents: `docs/oeis-ai-policy.md`.
- **The viva** (local-only files, deliberately uncommitted, in
  .git/info/exclude: docs/viva-exam.md, viva-reserve.md [chmod 000],
  viva-state.md, drill1-counting.md, drill2-tiers.md): exam taken
  2026-07-05, 56.5/100 vs bar (>=80, no core question below half).
  **Drill 1 (counting arguments) DONE 2026-07-06** — all of A1/A2/B1/B2/
  C1/C2 closed. **Drill 2 (tiers + validation) graded 2026-07-06/07** —
  D1 tier definitions done (one contested point resolved, jasonp's
  answer stands); E1 shared-logic mitigations strong but missing the
  held-out P_k item; F1 mod-p mechanism correct but doesn't name the
  reimplementation as the closing answer. Cold retake variants still
  pending after a spacing gap. **Full grading state: docs/viva-state.md**
  (local).
- Before submitting, also: jasonp rewrites all staged %C lines in his own
  words (Claude meaning-checks only); signature dates -> actual
  submission day; pink-box replies are jasonp's alone, always.

## Remaining work ledger
1. ~~Housekeeping~~ DONE 2026-07-06 (the big tidy: process docs, one-shot
   scripts, experiments/, stale drafts, autonomy/, polyplets/ removed;
   README.md replaces ROADMAP.md as the repo face).
2. ~~M(17) on dalby~~ DONE 2026-07-07 04:27 — M(17)=28 confirmed, paper
   Conjecture-1 note + maxhole.txt updated (see "Jobs landed" above).
3. Paper: final read-through after the tidy passes.
4. Viva drills + retakes, %C authorship pass, then jasonp submits.
5. **Lessons-learned document** (jasonp + Claude collaboration) — after
   compute and paper are done, BEFORE submitting. jasonp's explicit ask
   2026-07-06.
