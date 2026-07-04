# HANDOFF — 2026-07-04

Frontier **a(34) = 515316838423862758858377704**, banked+validated, term chase
**parked** per the 2026-07-06 close plan. Branch `kink-carry`, tip `56beca5`,
all pushed to origin. Durable facts live in `MEMORY.md`, `results/*.md`,
`ROADMAP.md`, and git history — this file is just the live state. (Older
session-by-session logs pruned 2026-07-04; recover from git history if needed.)

## Frontier / what's banked
- **a(1)…a(34)** all banked under `results/ns_a{n}/` (triangle, PROVENANCE,
  perheight, cost_profile). a(1)-a(20) match the b-file; a(21)-a(34) chain-match
  each prior term; growth monotone ~6.90 climbing toward λ≈7.1.
  - a(33) = 74631481980411777590683952 (`results/ns_a33/`).
  - a(34) = 515316838423862758858377704 (`results/ns_a34/`).
- **Diagonal closed forms P_2…P_15 wired** (`orchestrator/sweep.go`
  diagCoeffTable, `diagonalStripValid` k≤15). Each P_k drops the top real sweep
  height a tier; P_15 kept a(33)/a(34) topping at H18 (~3.4h) instead of H19
  (~11h). Fast deriver `scripts/derive_pk_fast.py` (exp recurrence).
- **Related sequences A030222/A030233/A030234/A030235/A194596 → n=24**
  (`results/related-seqs-n24.md`). Burnside from Fixed (A006770) + symmetric
  counts; all 95 known OEIS terms re-validated.

## Live jobs (Hall of Mirrors — symmetric TM pushes to n=34)
- **dalby — symtm hmirror 34** (`scripts/symtm_run.sh hmirror 34 32`): PID
  2994466, tmux `0:hm34`, rev `f306aa31`, → `runs/sym34/hmirror.out`. Predicted
  ~1-1.5h wall / 15-25GB; at 13:22 was 28/34 strips, self-ETA ~13:32, RSS 8GB.
  On completion: diff n≤24 prefix vs `runs/sym24/hmirror.out`, copy to gympie.
- **dalby — symtm r180 34** (`scripts/symtm_run.sh r180 34 32`): PID 2996883,
  tmux `0:r18034`, rev `7bc042e5`, → `runs/sym34/r180.out`. Predicted ~2.5h cpu
  / ~15-30min wall at 32 threads / ~7-20GB (gympie ladder n=26/28/30). Same
  completion drill. r180 unlocks **A030233 (one-sided) at n=34** (needs only
  r90+r180; r90 already banked in gympie `runs/sym34/r90.out`).
- **ayr — a(34) cross-ISA verify: DONE, `A34_VERIFY_PASS`** — x86 triangle
  n=1..34 byte-identical to banked dalby (ARM); folded into a34 PROVENANCE.
  ayr now FREE.

## Data ceiling (why the term chase is parked)
- **P_16 is derivable** (fit from T(33,17)+T(34,18), self-consistent — verified)
  but has **no independent holdout** until a(35). The diagonal-polynomial route
  has caught up to the data, so a(34)'s top cell has no closed-form cross-check
  (unlike a(33), whose T(33,18) matched the held-out P_15 exactly).
- More terms would need a fresh sweep (a35: H19 ~11h with P_15, or H18 ~3.4h if
  P_16 wired — but then P_16 has no holdout). Not planned pre-close.
- **Transfer-matrix Option 5** (`scripts/diag_transfer_gen.py`) as an
  independent P_k route is **infeasible in practice**: state count grows ~7.4×/k
  (59→437→… measured), so K=16 ≈ 9×10¹³ states. Dead end without a rewritten
  engine. (Its low-K output agrees with our P_2 in-regime — a good sanity check.)

## Extending the related sequences (optional; cost-bound, not correctness-bound)
- Gated **only by the symmetric counts**: Fixed reaches n=34, free polyominoes
  (A000105) n=59, symmetry counts n=24 — the gate. So they can go to n=34 in
  principle.
- `symcount_fast` is explicit Redelmeier — ~2.5×/term. Threaded `sym_extend.sh`
  (all four types over roots; mirror types were the pole, now ~90× faster):
  n=24 was ~2.2h. **n=25 ≈ 5.5h, n=26 ≈ 14h, n=27 ≈ 35h, n=28+ infeasible** for
  the close.
- The symmetric transfer-matrix engine **exists now**: `cpp/sym/symtm.cpp`
  (Hall of Mirrors), gated live vs symcount_fast (`tests/gate_symtm.py`) and
  byte-matched to the banked `runs/sym24/` oracles.
  - **hmirror**: palindromic-column sweep — n=34 running on dalby.
  - **r180**: left-half sweep + self-glue (seam union-find; palindromic middle
    column for odd widths), transpose-restricted to W≥H (weight 2/1) which
    collapsed the tall strips (n=20: 79.9s→0.93s). n=34 running on dalby.
  - **r90**: n=34 banked (`runs/sym34/r90.out`, gympie, 5.9s).
  - **dmirror**: not built — the remaining blocker for A030222/34/35 at n=34;
    hook-sweep design discussed 2026-07-04 (L-shells, folded arm state,
    selfPaired bit, ±2 corner stencil).

## Open independent threads
- **Lean proof** (branch `lean-diagonal-proofs`, `polyplets/PROOF-STATUS.md`):
  (a) finiteness, (b) row profile, (c-fwd), (d-local) done+green; remain
  (c-rev), (d-global gap≤2), (e) offset-chain count.
- **Steal-tail diagnostic** (`results/steal-tail-h18.md`): work-stealing fired
  0× on a32; root-caused to the record-based `grainRecs` eligibility floor
  missing compute-heavy stragglers. Banked, **not deployed** (trusted config).

## Landing plan for the 2026-07-06 publish (jasonp steers; nothing auto-started)
1. **Code tidy** — `/simplify` over the delta since the `simplified` tag. Clean
   untracked cruft: `autonomy/` (empty), `polyplets/.lake` (Lean build cache →
   gitignore).
2. **OEIS prep** — b-file for A006770 to n=34; upload files for the five related
   seqs to n=24 (only b030222 exists, and only to n=19). **Submission is
   jasonp's call** — prep only.
3. **Paper** — `paper/a19-polyplets.tex` revision (was deferred until the term
   chase stopped — now). Paper is last per ROADMAP.
4. **Repo** — README/HANDOFF/ROADMAP coherence; results/ provenance complete.
5. **Verify** — fold the ayr a(34) cross-ISA verdict into a34's provenance.
