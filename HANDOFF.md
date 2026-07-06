# HANDOFF — 2026-07-05

Frontier **a(34) = 515316838423862758858377704**, banked+validated, term chase
**parked** per the 2026-07-06 close plan. Branch `kink-carry`, all pushed to
origin. Durable facts live in `MEMORY.md`, `results/*.md`, `ROADMAP.md`, and
git history — this file is just the live state.

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

## Live jobs (2026-07-05 evening)
- **dalby — dmirror n=33 direct strips** (`scripts/dmirror_strips.sh 33 80 28
  27 .. 1`): driver PID 3035912, tmux `0:dm33`, rev `b358e397`,
  → `runs/sym33/dmirror.S*.out`. Started 07:41. **S=28 DONE** 13:28 (5.8h
  wall, 1.61M cpu-s, peak RSS 126.2GB — brushed into swap, fine; column
  d(28,28..33) = 2,34,600,6434,66960,506530; n≤32 prefix matches the n=32
  farm's S=28 exactly). **S=27 DONE** 18:13 (~4.75h). S=26 running since
  18:13. Peak-RAM risk is behind us; remaining strips shrink (ayr did all
  of S≤25 at n=32 in ~15h wall). Kill = numeric strip PID; resume = rerun
  missing strips.
- **ayr — dmirror n=33 cross-ISA recompute** (`scripts/dmirror_strips.sh 33
  32 25 24 23 22 21 20`): driver PID 3054773, tmux `0:dm33x`, rev `b358e39`,
  started 2026-07-06 00:47 → ayr `runs/sym33/dmirror.S*.out`. Purpose:
  independent x86 recount of strips dalby (ARM) computes — byte-compare per
  strip when both exist. S>=26 excluded (dalby peaks 86.8-126GB > ayr 78GB
  budget; ayr S=25 predicted ~<65GB from dalby's live 44GB@2.6h). Kill after
  current strip when dalby's farm lands; then **M(17) launches on ayr**
  (measured prediction: single-core n=13 maxhole = 25.4min -> ~835 core-h
  ~26-30h wall on 32 cores; sampling/maxhole_split.py 17 32; tests
  Conjecture 1's first prediction M(17)=28).
- ~~ayr n=32 tail~~ **DONE 2026-07-05 11:50** — drill executed: strips scp'd,
  sum + prefix validations PASS, companions derived+banked
  (results/related-seqs-n32.md), P_4-odd PINNED, P_5 forward-confirmed
  (6 witnesses), level 6 refuses, paper tables filled. ayr is FREE.
- **dalby n=33 completion drill** (waiter bihhw0fbn; if dead: `ps -p
  3035912`): prefix validations, P_5 pins conventionally from its k=5
  points, assemble n=33 = P_4 formulas (S≥29) + direct strips (T3 label),
  companions n=33 as OEIS comment-only + paper note, n=33-cost paper TODO,
  then decide n=34 (formulas S≥29 via P_5 + direct S≤28 at maxn=34; S=28@34
  budget-6 strip est ~90-160GB — the one marginal strip, swap covers).

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
  viva-state.md, drill1-counting.md): exam taken 2026-07-05, 56.5/100 vs
  bar (>=80, no core question below half). Drill 1 (counting arguments)
  nearly done — only exercise A2 outstanding; drill 2 (tier system +
  validation architecture, report §1+§5 explain-back) not started; cold
  retake variants after a spacing gap. **Full grading state:
  docs/viva-state.md** (local).
- Before submitting, also: jasonp rewrites all staged %C lines in his own
  words (Claude meaning-checks only); signature dates -> actual
  submission day; pink-box replies are jasonp's alone, always.

## Remaining work ledger
1. Housekeeping: gitignore `polyplets/.lake`, clean `autonomy/`.
2. dalby n=33 completion drill (above), then the n=34 dmirror decision.
3. Paper: TODO(n33-cost) after the run; final read-through.
4. Viva drills + retakes, %C authorship pass, then jasonp submits.
