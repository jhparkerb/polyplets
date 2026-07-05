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
  S^k/k!, onset ≈2k+2. **P_0..P_4 pinned** (P_4-even also cross-validated by
  two independent methods), **P_4-odd + P_5 both parities fitted** via the
  cumulant/exp form (`scripts/dmirror_pk_exp.py`, 4-9 exact witnesses).
  GF-basis structure: G_k = N_k(x)/((1-x)^(k+1)(1+x)^k), N_k(±1) = (±2)^k;
  no low-order bivariate closure (each level carries fresh gadget content).
  These formulas replace the RAM-impossible sparse strips: n=33 needs only
  P_4 (direct S≤28), n=34 only P_5 (direct S≤28).

## Live jobs (2026-07-05 midday)
- **dalby — dmirror n=33 direct strips** (`scripts/dmirror_strips.sh 33 80 28
  27 .. 1`): driver PID 3035912, tmux `0:dm33`, rev `b358e397`,
  → `runs/sym33/dmirror.S*.out`. Started 07:41; S=28 (the big first strip)
  at ~4h had RSS 114.9GB vs predicted 80-95 (125GB + 64GB `/swapfile2` —
  fine but WATCH). Predicted ~9.5M cpu-s ≈ 33h wall total. Purpose: n=33
  related-seqs terms — strips S≥29 come from P_4 closed forms; the run also
  yields the k=5 points that pin P_5 → n=34.
  Kill = numeric strip PID; resume = rerun missing strips.
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

## Landing plan for the 2026-07-06 publish (jasonp steers; nothing auto-started)
1. ~~Code tidy~~ **DONE 2026-07-04**: `simplified` tag moved to c567893; full
   gate suite repaired (three casualties of the 91bdcdc cleanup restored) and
   GREEN end-to-end. Still open: gitignore `polyplets/.lake`, clean `autonomy/`.
2. **OEIS prep** — b-file for A006770 to n=34; b-files for the five related
   seqs (A030233 to n=34; the other four to n=32/33 as the runs land).
   **Submission is jasonp's call** — prep only.
3. **Paper** — `paper/polyplets-report.tex` revision. The dmirror diagonal
   P_k structure (results/dmirror-diagonals.md) may merit a section or a
   separate note.
4. **Repo** — README/HANDOFF/ROADMAP coherence; results/ provenance complete;
   related-seqs results doc for the final reach.
