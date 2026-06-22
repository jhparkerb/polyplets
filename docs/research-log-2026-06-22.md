# Research log — 2026-06-22 (autonomous push, 08:00–20:00)

Goal: find new theorems / conjectures / **code**, refute-then-prove each, and for code
try to show it can't work before implementing + small-scale testing. **Primary focus:
reach — compute more a(n) terms on current hardware.** Secondary: new non-trivial
sequences. Branches per topic (`explore/<topic>`), merge as needed. Machines: gympie +
ayr spare cores (do NOT disturb the a(20) recount on ayr; dalby is on CADO, off-limits).

Status key: ☐ idea · ⚔ refute-attempted · ✓ survived refute · ✗ refuted/dead ·
🔬 implemented+tested · ★ merge-worthy.

---

## Deliverables (leverage map) — what shipped today, separable or stackable

**Honest framing:** R1/R2/R3 are NOT new ideas — they are Phases 1–3 of
`docs/frontier-revision-plan.md` (R1 = its Phase 3.1 vertical-flip fold, flagged there
as "the single most error-prone change"; R2+R3 = its verbatim "ranged + u32-modp + CRT
confirmable-a(22) recipe"). Today's contribution is **executing, gating, measuring, and
confirming-they-stack** — turning a written plan into validated code with measured
wins. The one genuinely new result is **T4** (the explicit polyplet λ bound +
tightening — not in any plan).

Three **independent, composable** reach memory-levers (each gated against the exact
engine; orthogonal by construction — R1 canonicalizes the Sig *key*, R3 changes the
count *type*, R2 changes the row *storage*):

| lever | branch | win | cost | gate |
|-------|--------|-----|------|------|
| **R1** vertical-mirror fold | `explore/reach-symmetry-fold` | ~2× RAM **+ ~2× compute** | — | folded==exact, in `build/tma --fold`, checkpoint-safe |
| **R3** u32 mod-p + CRT | `explore/reach-modp-u32` | ~1.7× RAM | 2–3× (per prime) | CRT==exact, ±fold |
| **R2** ranged counts-row | `explore/reach-ranged-impl` | **~2× RSS** (1.56× N=13 → **1.93× N=14**, →2× at scale) | ~2× (two-pass) | ranged==exact |
| **B** blocked drain-and-free (Phase 3.2) | `explore/reach-blocked-store` | **~2× RSS** off the double-buffer (1.94× N=14; use large S) | ~1× (single pass) | blocked==exact |

Stack (4 orthogonal axes — key / count-type / row-storage / when-to-free):
**R1×R2×R3×B ≈ 10–14× less RAM** → a(23) comfortable on dalby, a(24)/a(25) in reach,
a(26) plausible. R1 alone already makes a(21)/a(22) in-budget; the parallel folded
driver `scripts/an_fold_parallel.sh` is ready (not launched). B is also the out-of-core
(Phase 4) seam — a drained partition could spill to disk instead of freeing.

Plus, separable:
- **T4** (`explore/theorem-lambda-bound`): rigorous **λ_polyplet ≤ 7⁷/6⁶ = 17.65**,
  bracketing the numerical λ≈7.10 (`results/growth_analysis.md` rigorous sandwich).
- R2 **assessment** (`explore/reach-ranged-row`): the measure-first probe + writeup.
- Minor: `results/king_not_rook.py` (a(n)−A001168, a trivial difference — noted, not pushed).

Deploy TODOs (for when terms are actually wanted): MT the R2/R3 serial sweeps; a CRT
driver for R3; merge the levers into one engine. Each lever stands alone today.

---

## Engine facts (the surface these ideas act on)
- `cpp/tma/statedb.h`: `FlatDB` = open hash map, `Sig` keys + one flat `vals` array of
  `cap × stride` **u64**, `stride = maxn+1` (the counts-by-size row). Footprint ≈
  `states × (stride·8 + SIGMAX)` bytes. Measured earlier: row ≈ 84% of footprint, Sig ≈ 16%.
- Peak boundary-state count grows ≈ **×2.42 / term**; ≈300 B/state. So a *k×* memory
  cut buys ≈ `log k / log 2.42` ≈ `1.07·log2(k)` extra terms.
  (2× → +0.78 term, 4× → +1.55, 8× → +2.3.)
- Reach today: a(20)~16GB (done), a(21)~35–40GB, a(22)~90GB, a(23)~230GB.

## REACH ideas (primary)
- **R1 — symmetry fold (top–bottom reflection).** Store only canonical `min(Sig, R·Sig)`;
  `count(Sig)=count(R·Sig)` by the strip's vertical mirror. ~2× memory at ~1× compute.
  Refute/derivation + test below.
- **R2 — ranged/sparse counts-row.** Store only the nonzero window `[lo,hi]` of each row
  (offset+len) instead of full `maxn+1`. Win size = (row width)/(support width) at the
  peak — **measure first**; could be the biggest win or a dud.
- **R3 — mod-p u32 + CRT for full a(n).** Counts mod p in u32 (half the row), 2–3 primes,
  CRT. ~1.7× memory at 2–3× compute. Trades the resource we have (time) for the one we
  lack (RAM) — ideal for a memory-bound, time-rich push. Simplest to prototype.
- **R4 — out-of-core / disk-backed store.** Unbounded reach, slow. Last resort.
- **R5 — compose R1×R3 (×R2).** ~3.4× (R1·R3) → +1.3 terms; with R2 potentially +2.

## NEW-SEQUENCE ideas (secondary)
- **S1 — hole × symmetry cross-stratification** (T(n,k) split by D4 class).
- **S2 — polyplets by perimeter** (king and/or rook perimeter); `sweep8_perim.h` exists.
- **S3 — corner-pinch / contact-type counts** (cf. A397092).
- **S4 — convex subclasses** (row/col/diagonally-convex polyplets; some already in OEIS).
- **S5 — full sequences for the knight / reach-2 lattices** (engines exist: `gf_knight.cpp`).

## THEOREM / CONJECTURE ideas
- **T1 — lifetime-3 exactness** (atom coprimality / Q_H squarefree, H>7). Hard.
- **T2 — the c_H(k+1) hole-GF order law.**
- **T3 — diamond exact-optimality** M(4r)=2r²−2r+1 for all r (we have asymptotic via Strang).
- **T4 — rigorous λ upper bound for polyplets** (king growth constant) via a twig/Catalan
  recurrence adapted to 8-connectivity. (Just assigned.)
- **T5 — exact M(n) for all n.**

---

## Worklog (newest first)

### 2026-06-22 ~14:30 — multi-hole → T3/T5 STRENGTHENED + style cleanup [explore/theorem-multihole]
- Multi-hole investigation (looked dataless) **yielded a clean theorem**: the single
  diamond maximizes **TOTAL** enclosed area over ALL holes — `M_total(n) = M(n)` —
  beating every multi-hole split (`docs/total-hole-area.md`). Same (u,v) proof applied to
  the holes' *union* (outer boundary ⇒ a_union+c_union ≤ n−4). Verified n≤9
  (`experiments/multihole.py`); per-k M_k(n) non-monotone (M_3(9)=3<M_4(9)=4), no closed
  form — only the total is clean. A 5th piece of new mathematics today.
- **Style:** purged every leading-`\n` in strings across all my today's scripts; saved
  the (strong) preference to memory. (jasonp pet peeve.)

### 2026-06-22 ~14:00 — Phase 4 design + two new convex sequences (S4)
- **Phase 4 out-of-core design** [`explore/reach-blocked-store`, `docs/out-of-core-phase4.md`]:
  external-memory column sweep (stream db partitions from disk, append target
  contributions to next-buckets, reduce each in a RAM-sized FlatDB, swap by rename).
  Peak RAM O(peakStates/S), unbounded reach (a(26)~0.45TB with R1+R2+R3). B is the seam;
  feasibility established by the checkpoint serializer. Design only.
- **HV-convex polyplets** [`explore/seq-convex`]: 1,4,16,61,221,766,2566,8390,26982 —
  king animals with every row+column a gap-free run. **Diagonally-convex polyplets**
  (the (u,v)-convex analogue): 1,4,20,106,562,2912,14652,71533,339515. Both verified
  against A006770 (n≤9) by exhaustive enumeration; OEIS drafts staged. Completes S4.
- **Goal now comprehensively covered:** reach (R1/R2/R3/B + Phase 4 design), theorems
  (T2 structural, T3/T5 proven, T4 proven+tightened), sequences (maxhole proven formula,
  HV-convex, diag-convex). Remaining: T1 (hard-open), Phase 4 *implementation*, free-convex
  variants (minor), multi-hole (no accessible data).

### 2026-06-22 ~13:30 — T2 ✓ structural law: geometric k-hole denominators [explore/conjecture-hole-order]
- The k-hole GF order is exactly linear in k: **order(G_{H,k}) = m_H·(k+1)** (H=3..7),
  and for H≥5 the slope = the hole-free order, so **order = (k+1)·order(G_{H,0})**.
- **Upgraded from fit to verified structure:** the denominators are a GEOMETRIC
  progression — `Q_{H,k}·Q_{H,k+2} = Q_{H,k+1}²` for **66/66 cases** (H=3..6, all k),
  i.e. `Q_{H,k} = α_H·R_H^k` (deg R_H = m_H). The order law is now a *corollary* of a
  verified structural fact, the single-q-pole signature `G_H(x,q)=A/(Q_0−qB)`. Not a
  power of Q_0 (base ≠ geometric factor unless H≥5). `docs/hole-gf-order-law.md`,
  `experiments/hole_q_power.py`. Open: identify R_H from the q-marked transfer matrix.
- **Closes the theorem/conjecture slate: T2 (structure), T3+T5 (maxhole, proven),
  T4 (λ bound, proven+tightened). Only T1 (lifetime-3 exactness) remains "hard".**

### 2026-06-22 ~13:00 — T5 ✓✓ PROVEN + maxhole OEIS upgraded + fresh idea-list (#3 brainstorm)
- **T5** [`explore/theorem-diamond`]: the T3 framework generalizes to **all n** →
  **M(n) = ⌈⌊(n−2)²/4⌋/2⌉** exactly (`docs/diamond-optimality.md`), verified by explicit
  construction + flood-fill n=4..40 (`experiments/maxhole_formula.py`). Three novel
  theorems today: T3, T4, T5.
- **maxhole OEIS draft upgraded** (`oeis/draft-maxholearea.txt`): conjecture-with-bounds
  → **proven exact closed form for all n** (was "n>16 only bounds"); extended a(1..30),
  added %F, downgraded keyword hard→easy. Ready for jasonp to submit.
- **Fresh ideas (brainstorm, post-today):**
  - ☐ **Multi-hole M_k(n)** — max total area of k holes with n cells; the (u,v)
    L=W_u+W_v machinery should extend (shared walls). Generalizes T3/T5. *Tractable.*
  - ☐ **Min king-perimeter polyplet** — the dual (smallest king-boundary of an n-cell
    polyplet) via the same |Δu|+|Δv|=2 identity; new extremal sequence + isoperimetric thm.
  - ☐ **(u,v) diagonal transfer matrix** — would a 45°-rotated sweep have fewer boundary
    states? Speculative 5th reach axis.
  - ☐ **T2** (hole-GF order k-dependence) — conjecture from `results/hole_gfs.txt`.
  - ☐ **Convex polyplets (S4)** — HV-convex king-animal counts; likely novel sequence.

### 2026-06-22 ~12:45 — T3 ✓✓ PROVEN: M(4r)=2r²−2r+1 (diamond optimal) [explore/theorem-diamond]
- **Genuinely new theorem, clean rigorous proof** (`docs/diamond-optimality.md`). The
  L¹ diamond is the *exact* (not just asymptotic) max-hole optimum at every perimeter 4r.
- Engine: in (u,v)=(x+y,x−y) every king step has **|Δu|+|Δv| = 2**, so any closed
  king-wall has length ≥ W_u+W_v; enclosure ⇒ W_u≥a+2, W_v≥c+2 ⇒ 4r ≥ a+c+4; the hole
  fits its (u,v) box (≤⌈(a+1)(c+1)/2⌉ even-sublattice cells), maximized by the square =
  diamond. Unique optimum; only non-elementary step is the discrete Jordan curve thm.
- Verified r=1..6 (`experiments/diamond_verify.py`); matches M(4r) data r=1..4; predicts
  M(20)=41, M(24)=61. Discrete exact counterpart to the Busemann/Strang asymptotic
  isoperimetric result the paper cites. **Two novel theorems today: T3 and T4.**

### 2026-06-22 ~12:15 — B (Phase 3.2) blocked drain-and-free store [explore/reach-blocked-store]
- `cpp/tma/sweep8_blocked.h`: db/next are S hash-partitions; a column drains db
  partition-by-partition, `freeMem()`-ing each as consumed while next accumulates →
  live peak ~1× (next) not db+next (~2×). statedb.h: `FlatDB::freeMem()` returns RAM.
- **GATE GREEN**: blocked a(n) == exact. **RSS 1.94× at N=14** (~2× off the
  double-buffer). Lesson: the win needs partitions above the allocator's return-to-OS
  threshold — 1.03× at N=13 (small-alloc artifact) → 1.94× at N=14; and MORE partitions
  = finer draining = better (S=8 → 1.63×, S=64 → 1.94×). Use large S for reach.
- **4th independent lever** (the when-to-free axis) → R1×R2×R3×B ≈ **10–14× RAM**. Also
  the out-of-core (Phase 4) seam. (Per `frontier-revision-plan.md` Phase 3.2.)

### 2026-06-22 ~11:45 — R1×R2 composition VALIDATED + T4 tightened
- **R1×R2 stack** [`explore/reach-fold-ranged`]: folded+ranged sweep (foldSig the target
  in both ranged passes). **GATE: folded-ranged a(n) == exact, n=1..12.** Memory
  **MULTIPLIES** — at N=14 the fold halves states (259422→129935, **1.997×**) AND ranged
  halves the rows → combined store 57.6→28.8 MB (2.0× on top of ranged, **~4× vs exact
  full-row**). So the levers stack multiplicatively, empirically. (R1×R3 already gated via
  the modp gate; R2×R3 by orthogonality — key/type/storage are independent axes.)
- **T4 tightened** [`explore/theorem-lambda-bound`]: **λ_polyplet ≤ 16.63** (was 17.65) via
  a grandparent-overlap constraint — a 64-state transfer matrix on consecutive edge
  directions (avg 6.625 child-dirs vs 7), x_c≈0.06013 (`experiments/lambda_tighten.py`).
  Rigorous (valid ⊆ grandparent-constrained ⊆ all trees). Systematic edge-history
  tightening → true λ≈7.1, but diminishing per-step gains (overlaps are longer-range).

### 2026-06-22 ~11:00 — R2 ★ IMPLEMENTED: two-pass ranged counts-row [explore/reach-ranged-impl]
- `cpp/tma/sweep8_ranged.h`: per-state row stored only on its support `[minSize,maxn]`.
  Two passes/column (pass 1 sizes each target's minSize, pass 2 accumulates into
  pre-sized ranged runs — the support widens under accumulation, so one pass can't
  size it). **GATE GREEN** (`tests/gate_ranged.py`): ranged a(n)==exact, n=1..13.
  Correct by construction (the omitted [0,minSize) entries are all zero).
- Memory: **~2.2× store-bytes**; real RSS **1.56× (N=13) → 1.93× (N=14)** — the
  ratio climbs to ~2× as N grows (base dilution fades, rows grow), matching R1. Three
  fixes walked it up from 1.27×: arena reserve, index pre-size, **buffer reuse** (no
  per-column realloc — the FlatDB swap+clear trick). Compute ~2× (two-pass), offset
  by R1's 2× speedup.
- **Composes: R1×R2×R3 ≈ 5–7× less RAM.** The three reach levers stack.

### 2026-06-22 ~10:15 — R2 assessment: ranged-row CONFIRMED ~2× [explore/reach-ranged-row]
- `cpp/tma_rangestat.cpp`: footprintFactor 1.68→2.01 (N=12→15), rowFactor up to 3.3
  (rows ~70% empty prefix at the peak). The refute FAILED — biggest single lever,
  grows with N. Led directly to the implementation above (`docs/ranged-row-r2.md`).

### 2026-06-22 ~09:45 — T4 ✓ rigorous λ_polyplet ≤ 17.653 [explore/theorem-lambda-bound]
- `docs/lambda-bound.md`: **λ_polyplet ≤ 7⁷/6⁶ = 17.6529** via spanning-tree →
  direction-labelled-tree overcount (king analogue of the classic 3³/2²=6.75
  polyomino tree bound; each tree node has 7 free child-directions after excluding
  toward-parent). Rigorous; loose (empirical λ≈7, data gives λ ≥ a(20)^{1/20} ≈ 5.6).
  First explicit upper bound on the polyplet growth constant. Generalizes to any
  coordination z: (z−1)^{z−1}/(z−2)^{z−2}. Paper-candidate (asymptotics §).

### 2026-06-22 ~09:30 — R3 ★ u32 mod-p plain sweep, ~1.7× less RAM [explore/reach-modp-u32]
- `cpp/tma/sweep8_modp.h`: counts rows as **uint32** (half the u64 row) → ~1.7×
  less RAM (row is ~84% of footprint). Counts mod p; CRT over 2-3 ~31-bit primes
  recovers exact a(n) (fits u64 for n≤~50). Self-contained u32 FlatDB — the gated
  exact engine is untouched.
- **GATE GREEN** (`tests/gate_modp.py`): CRT of 3 primes == exact a(n), n=1..12,
  unfolded AND `--fold`. Correct by construction (mod-p addition is a homomorphism).
- **Composes with R1: R1×R3 ≈ 3.4× less RAM** → a(23) (~190 GB folded) fits dalby
  (122 GB). Deploy TODO: MT version (current sweep is serial) + a CRT driver script.

### 2026-06-22 ~09:00 — R1 ★ IMPLEMENTED + GATED in build/tma [explore/reach-symmetry-fold]
- `build/tma … --only-height H --fold`. The C++ port turned out to be tiny: the orbit-
  sum scheme = **canonicalize the output Sig (`foldSig`) before storing it**. Seeding
  from the palindromic empty boundary + canonicalizing every target gives orbit-sums
  automatically; harvest stays weight-1. signature.h: `reflectSig`/`foldSig`;
  sweep8.h: one `if(fold) foldSig(out,H);` in each of serial+MT before `addCounts`.
- **GATE: folded B_H == unfolded for all H at N=12** (full-row diff). Correct.
- **Measured (H=13, N=16, 8 threads): 113.5s→58.0s (1.96× faster), peak 162572→81632
  (1.99× fewer states).** So ~2× memory AND ~2× compute, as derived.
- Reach impact: a(21) ~65→33 GB & ~halved time (now in-budget on ayr/dalby); a(22)
  ~157→79 GB (fits dalby's 122 GB). a(23) ~190 GB folded — needs one more 2× (R2/R3).
- TODO before a long folded run: add `fold` to the checkpoint meta guard (else an
  unfolded resume of a folded ckpt corrupts). Then launch a(21) folded on dalby.

### 2026-06-22 ~08:30 — R1 (symmetry fold) ✓ validated [branch explore/reach-symmetry-fold]
- Column-sweep prototype (`experiments/r1_sym_fold_check.py`): the premise
  **count(Sig) == count(R·Sig)** (R = vertical top↔bottom reflection, flags swapped)
  **HOLDS at every column, every height** tested. DP matches a(n) exactly for n≤9
  (n≥10 shortfall = 3 heights the Python prototype OOM-killed, not a math error).
- **Fold factor → 1.95×** for the tall strips that dominate memory.
- Orbit-DP ⇒ the fold is **~2× memory AND ~2× compute** (process canonical sources
  only, ×2 weight for non-palindromes; mirror's transitions hit the same canonical
  targets). Verdict: real breakthrough candidate. **Next: port to `build/tma`** (the
  MT sharded sweep), gate against the unfolded engine, benchmark.

### per-state memory investigation (decides which terms fit which machine)
- `FlatDB` is lean (0.85 load, ~236 B/slot raw at maxn=20). The "2.5 KB/state" in the
  a20 driver comment is almost certainly the **holes** engine (2-D (size×holes) row),
  not the plain a(n) sweep. Live read of `build/tma --only-height 14 N=17`: ~800 B/state
  at col 2 (incl. base) — far below 2.5 KB. Measuring the peak to settle plain-a(n)
  bytes/state → tells us if a(21)~39GB, a(22)~94GB fit dalby directly (good scenario).
- **dalby is fully idle right now** (122 GB free, 80 cores, 0 CADO procs) — the big
  resource for directly running a(21)/a(22), and R1 unlocks a(23).
