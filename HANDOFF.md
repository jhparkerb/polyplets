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
  - **dmirror**: n≤28 banked (`runs/sym28/dmirror.out`, dmirror(28)=
    47198412763); n=32 farm nearly complete (see live jobs). Engine is the
    **Shrink Ray** compact-frontier rewrite (b358e39): flat sharded storage,
    ~1.6× RAM + ~2× speed vs the unordered_map frontier that OOMed dalby.
- **Related sequences**: **A030233 (one-sided) derived+validated to n=34**
  (128829209605977867230343869 at n=34; needs only Fixed+r90+r180). The
  D-dependent four (A030222/34/35/194596) stand at n=24 banked
  (`results/related-seqs-n24.md`); n=32 lands with the ayr tail, n=33 with
  the dalby run. Combiner `scripts/derive_related.py` (per-sequence reach,
  validates every known OEIS term, /4 and /8 divisibility asserts).
- **dmirror diagonal quasi-polynomials** (`results/dmirror-diagonals.md`):
  d(S,S+k) is period-2 quasi-polynomial, degree k per parity class, leading
  S^k/k!, onset ≈2k+2. **P_0..P_4 pinned** (P_4-even also cross-validated by
  two independent methods), **P_4-odd + P_5 both parities fitted** via the
  cumulant/exp form (`scripts/dmirror_pk_exp.py`, 4-9 exact witnesses).
  GF-basis structure: G_k = N_k(x)/((1-x)^(k+1)(1+x)^k), N_k(±1) = (±2)^k;
  no low-order bivariate closure (each level carries fresh gadget content).
  These formulas replace the RAM-impossible sparse strips: n=33 needs only
  P_4 (direct S≤28), n=34 only P_5 (direct S≤28).

## Live jobs (2026-07-05 morning)
- **dalby — dmirror n=33 direct strips** (`scripts/dmirror_strips.sh 33 80 28
  27 .. 1`): driver PID 3035912, tmux `0:dm33`, rev `b358e397`,
  → `runs/sym33/dmirror.S*.out`. Predicted ~9.5M cpu-s ≈ 33h wall, peak strip
  (S=28, runs first) ~80-95GB vs 125GB + 64GB swapfile (`/swapfile2`, added
  2026-07-05). Purpose: n=33 related-seqs terms — strips S≥29 come from P_4
  closed forms; the run also yields the k=5 points that pin P_5 → n=34.
  Kill = numeric strip PID; resume = rerun missing strips.
- **ayr — dmirror n=32 tail** (`scripts/dmirror_strips.sh 32 32 25 .. 1`):
  driver PID 3024316, tmux `0:dm32c`, rev `b358e39`. S=25/24 done (banked on
  gympie), S=23 running as of 07:38. dalby's half S=26..32 done + banked.
- **Completion drills** (waiters do not survive a context clear — check
  directly: dalby `ps -p 3035912`, ayr `ps -p 3024316`):
  - ayr n=32 done → scp `runs/sym32/dmirror.S*.out` to gympie,
    `python3 scripts/dmirror_sum.py 32`, prefix-validate vs runs/sym24 (n≤24)
    and runs/sym28 (n≤28), `derive_related.py runs/sym32`-style combine (needs
    a symdir with all four types' counts — copy/symlink alongside sym34 data),
    rerun `dmirror_diagonals.py` + `dmirror_pk_exp.py` (pins P_4-odd via S=23,
    forward-tests P_5, attempts level 6). Bank a related-seqs results doc.
  - dalby n=33 done → same prefix validations, P_5 pins conventionally from
    its k=5 points, assemble n=33 = P_4 formulas (S≥29) + direct strips, then
    decide n=34 (formulas S≥29 via P_5 + direct S≤28 at maxn=34; S=28@34
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
3. **Paper** — `paper/a19-polyplets.tex` revision. The dmirror diagonal
   P_k structure (results/dmirror-diagonals.md) may merit a section or a
   separate note.
4. **Repo** — README/HANDOFF/ROADMAP coherence; results/ provenance complete;
   related-seqs results doc for the final reach.
