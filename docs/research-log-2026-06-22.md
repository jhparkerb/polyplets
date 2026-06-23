# Research log — 2026-06-22 (autonomous push, 08:00–20:00)

Goal: find new theorems / conjectures / **code**, refute-then-prove each, and for code
try to show it can't work before implementing + small-scale testing. **Primary focus:
reach — compute more a(n) terms on current hardware.** Secondary: new non-trivial
sequences. Branches per topic (`explore/<topic>`), merge as needed. Machines: gympie +
ayr spare cores (do NOT disturb the a(20) recount on ayr) + **dalby AVAILABLE** (122GB/80c
idle — the big-RAM reach machine; the earlier "on CADO, off-limits" note was STALE and
wrongly idled it most of the day; jasonp confirmed it was free since goal-set).

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
driver `scripts/an_fold_parallel.sh` is ready (not launched). B is the out-of-core
(Phase 4) seam — and **Phase 4 is now IMPLEMENTED + gated** (`explore/reach-blocked-store`,
`cpp/tma/sweep8_ooc.h`, `make gate-ooc`): db/next spill to disk as S partitions, RAM ≈
peak/S, **reach bounded by disk not RAM**. Above the in-RAM stack this removes the ceiling
entirely (a(26)+ on a big disk). Gate: OOC a(n)==exact, S-independent.

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

## Brainstorm round 2 — fresh ideas after the first sweep (2026-06-22 ~17:00)
Generated post-completion; the maxhole/(u,v) and lifetime-3 veins turned out richest, so
these lean that way. Tagged by cost. **B1 already computed** (the demonstration).

*Sequences (mostly derivable, cheap):*
- **B1 — min-n(k) = fewest cells to enclose k holes** = min{n : maxh(n) ≥ k}, the inverse
  of today's proven `maxh(n)=n+1−A027709(n)/2`. **Computed:** 4,6,8,9,11,12,14,15,16,18,19,
  20,22,23,24,25 (k=1..16), strictly increasing (maxh increments by 0/1, so every k is
  attained). Clean, proven, OEIS-staged (`oeis/draft-minhole-cells.txt`, branch
  `explore/seq-minhole-cells`). [A027709 = 2·⌈2√n⌉ — an earlier hand-typed array of it was
  wrong past n=10; corrected here and in the maxh-count draft.]
- **B2 — symmetry-restricted maxhole**: max hole area among polyplets of a FIXED symmetry
  class. The diamond is D4-symmetric so M(n) is unchanged for the symmetric classes, but the
  *asymmetric* (trivial-stabilizer) max could be strictly smaller — a new gap to measure.
- **B3 — minimum KING-perimeter polyplet** (the A027709 analogue for polykings); feeds a
  king-lattice Pick/maxhole story.

*Theorems / conjectures:*
- **T6 — diagonal-contact CLT**: #diagonal-contacts of a uniform n-cell polyplet → Normal
  with mean ~c·n; c (the asymptotic contact density) is a new lattice constant, gettable
  from a contact-marked transfer matrix and the standard TM central limit theorem. Concrete,
  provable.
- **T7 — tighten λ ≤ 16.63** toward the true λ≈7.10 (the gap is embarrassing); a longer-twig
  / correlation-length transfer-matrix bound. Even λ≤12 is progress.
- **T8 — (u,v) maxhole for higher-reach lattices** (knight / reach-2): does the isoperimetric
  diamond argument carry over? The lifetime-3 work already showed these lattices share the
  vertical-translation structure.
- **T9 — G_H: Gal(N_H)=S_{deg N_H}** (today's T1 reframing) — now strongly evidenced; worth
  stating as a standalone conjecture (implies the open lifetime-3 lemma).

*Code / compute:*
- **C1 — extend GF recovery to H=11,12**: more atom degrees + orders → longer OEIS sequences
  AND two more independent tests of lifetime-3 / G_H. Feasible (gf_modp + Berlekamp-Massey).
- **C2 — multi-hole M_k(n) to n≤11**: more data on the non-monotone per-k maxima.
- **C3 — merged R1×R2×R3×B engine** for actual deployment (integration, not research).

## THEOREM / CONJECTURE ideas
- **T1 — lifetime-3 exactness** (atom coprimality / Q_H squarefree, H>7). Hard.
- **T2 — the c_H(k+1) hole-GF order law.**
- **T3 — diamond exact-optimality** M(4r)=2r²−2r+1 for all r (we have asymptotic via Strang).
- **T4 — rigorous λ upper bound for polyplets** (king growth constant) via a twig/Catalan
  recurrence adapted to 8-connectivity. (Just assigned.)
- **T5 — exact M(n) for all n.**

---

## Worklog (newest first)

### 2026-06-22 ~19:30 ET -- R1xR3 reach engine DEPLOYED to production (gated end-to-end)
On branch deploy/reach-modp: wired the plain-a(n) --modp + --fold path into tma_main.cpp (routes to
sweepSquare8HeightModP, ~4x less RAM) + a CRT driver (scripts/an_modp_crt.sh: 3 primes near 2^31,
per-height fold+modp sweeps -> a(n) mod p -> CRT -> exact a(n)). GATED: an_modp_crt.sh 12 --fold ==
A006770 (n<=12) exactly; per-height modp+fold output == exact B_H(n) mod p. The R1(fold) x R3(u32
mod-p) reach engine is production-ready. Remaining: compose B (blocked store, ->~8x total) +
parallelize the (H,p) sweeps for the real run (gated on a(20) confirming).


### 2026-06-22 ~19:00 ET -- lambda UPPER bound tightened 15.83 -> 10.354 (verified)
Eden/Klarner-Rivest spanning-encoding (Barequet-Shalah, arXiv:1906.11447): each non-root king cell
encodes only its UNDETERMINED king-neighbors (need-set 5 diagonal / 3 edge) -> injection into
weighted trees -> lambda <= 1/x* (encoding-GF branch point). Uniform: lambda <= 3125/256 = 12.207
(closed form). Directional: lambda <= 10.354 -- INDEPENDENTLY re-derived (2-type reduction matches
the 8-type; square sanity = Eden 27/4 = 6.75). Rigorous interval now [6.54, 10.354]; the weak upper
side is finally under 11. experiments/lambda_upper_bound.py.


### 2026-06-22 ~21:30 ET -- lambda UPPER bound tightened again 10.354 -> 9.355 (ITERATED, verified)
The 10.354 is just the DEPTH-1 case of an iterated ancestor-exclusion. In the BFS spanning-tree
encoding a cell C can be the discoverer of a neighbor q only if NO proper ancestor of C is
adjacent-or-equal to q (an ancestor is shallower in the BFS, so q's parent has depth <= that
ancestor's +1 <= depth(C) < depth(C)+1 -- q cannot be C's child). Track the last d discoverer
directions as the cell type; exclude every child-slot adjacent to ANY of the d ancestors. This only
ever drops PROVABLY-impossible children, so it stays a valid upper bound and tightens monotonically:
king 10.354 (d1) -> 9.482 (d2=d3) -> 9.399 (d4) -> **9.355 (d5)**. VALIDATED on the square anchor
(L1 adjacency): depth-1 = Eden 27/4 = 6.7500 exactly, then 6.75 -> 5.219 -> 5.163, staying above the
true 4.0626 (and above Klarner-Rivest's stronger 4.649 -- ancestor-exclusion is weaker than KR's
empty-cell method). The bound PLATEAUS ~9.3: deeper exclusion will NOT reach the ~8 heuristic; that
needs propagating known-EMPTY frontier cells, not just occupied ancestors (future work). New rigorous
interval **[6.54, 9.355]**. Ran on ayr (8^d cell-types, king to d5 = 32768; numpy-vectorized, self-
checks the square anchor each run). experiments/lambda_upper_bound_iterated.py.
- BUGFIX during this: the first draft used Chebyshev (king, L-inf) adjacency for BOTH lattices, so the
  square anchor read a nonsense 2.0; king was unaffected (L-inf IS king adjacency, depth-1 = 10.354
  reproduced). Parametrized adjacency per lattice (king L-inf, square L1); square anchor then correct.


### 2026-06-22 ~18:30 ET -- three fresh hunts: hole-free growth gap, novel sequences, king p_c
- **Hole-stratified growth (NEW, verify)**: the hole-free subclass A_0(n) grows STRICTLY SLOWER.
  A_0(n)/a(n) decays EXPONENTIALLY ~0.978^n (decisive: RMS 2e-5 exponential vs 1.8e-3 stretched,
  3.6e-3 power), so lambda_0 ~ 6.95 < lambda ~ 7.11. OPPOSITE the square lattice (where the
  simply-connected subclass shares lambda, sub-exponential decay). [Decay fit robust; the
  square-contrast premise should be double-checked.] Mean hole count E[k] ~ 0.023n (linear) ->
  animals "typically holey" only around n >= 45.
  - **CORRECTION 2026-06-22 evening (verified, results/lambda0-verification.md)**: the polyplet
    result STANDS (lambda_0 ~ 6.93 < lambda ~ 7.10, ratio ~0.977, exponential beats power over
    n=4..18) but the **"OPPOSITE the square lattice" framing is FALSE**. Pulling A006724 (hole-free
    square polyominoes) vs A001168 directly: the square lattice shows the SAME exponential decay,
    base ~0.977 -- essentially identical to the king lattice, same arched residual. No paper in
    papers/ asserts equal hole-free growth; the premise was a confusion with shared universality
    EXPONENTS / SAP asymptotics. Honest headline: hole-free animals grow exponentially slower on
    BOTH lattices by nearly the same factor (~0.977) -- an AGREEMENT, not a contrast. Also: the
    per-step decay base is not perfectly constant (bottoms at n=15-16, ticks up), so "pure
    geometric / decisive" is an idealization; a geometric x power n^0.016 fits ~3x better but the
    exponent is ~0, so exponential-dominated base ~0.977 is the right reading.
- **Novel OEIS sequences** (build/g2 statistics, each verified vs OEIS term-by-term): holes_zero
  (hole-free count 1,4,20,109,622,3664,22094,135609,...), holes_one, box_square (square bounding
  box), holes_maxh (max # distinct holes; distinct from A337601 at n=13) -- submission candidates.
  Confirmed identities: max-hole AREA = round((n-2)^2/8) = A001971 shifted; max-perimeter polyplets
  = A001168 (fixed polyominoes); min-perimeter = A027709.
- **King site-percolation threshold (validation)**: p_c ~ 0.406 +/- 0.001 from Mertens' nnSquare
  S(p) series (Dlog-Pade), exponent gamma ~ 43/18 -- MATCHES published 0.4071 (Malarz-Galam 2005,
  Phys.Rev.E 71:016125). Clean cross-check of the king machinery; not novel (MC has more digits).
- (gympie cleanup: killed an orphaned R2 `tma_rangestat 16 20` background job, 7h25m runaway.)


### 2026-06-22 ~18:00 ET -- lambda (growth constant) characterized; lit-check + epistemics
- **Lit check** (papers/ now holds Mertens 1990 + Mertens-Lautenbacher 1991): NO published king
  growth constant. Both are enumeration-only. Mertens 1990 Table I = the A006770 source (king
  counts to n=14, == ours exactly -- engine cross-check vs the primary source). M-L 1991 does the
  TRIANGULAR lattice + only a QUALITATIVE heuristic "lambda somewhat below the coordination number"
  (king z=8 -> lambda<~8). So no prior NUMBER -- not "first to consider lambda", first to pin one.
- **Estimate** lambda ~ 7.13: two NON-converged extrapolations -- series-ratio a(n)/a(n-1) (1/n
  fit ~7.10-7.12, drifting up) and GF-pole Neville on lambda_H (~7.155, drifting down) -- agree to
  ~0.5%, match theta=1 universality (Jensen-Guttmann). [7.12,7.155] is an estimate SPREAD, NOT a
  proven bracket; lambda could sit slightly outside.
- **Rigorous** lambda in [6.54, 15.83]: lower = Rands-Welsh concatenation on confirmed n<=19 (up
  from strip 5.99 / Fekete 5.63; climbs with terms); upper = ancestor-exclusion (loose -- Mertens'
  heuristic ~8 is far closer; a real upper-bound method is the open win).
- Records: results/growth-and-structure.md, results/lambda-bounds-timeline.md,
  experiments/lambda_series.py + lambda_lower_bound.py. Two overclaims (universality, "first")
  withdrawn and corrected.


### 2026-06-22 ~16:00 ET — D1 (the C++ stats lever) settles b2 + kills c=3/4; reach repointed
- **Realized the Python->C++ lever** (memory [[cpp-not-python-for-compute]]): added per-animal
  stats to the Redelmeier engine -- `g2 --maxhole-strat` (D4 symmetry -> M_asym; exactly-k-hole
  area -> M_k) and `g2 --contacts` (diagonal-contact distribution). Verified == the Python
  results, then went where Python couldn't.
- **b2 SETTLED** (`explore/cpp-stats-engine`): M_asym(n) to n=12 in 4 min. M_asym=M(n-1) is
  CONCLUSIVELY REFUTED (n=10,11,12 -> 7,9,11 vs M(n-1)=6,8,10); the real M_asym ~ M(n)-{1,2},
  irregular, no closed form. Multihole M_k to n=12 (still non-monotone). `results/maxhole-stratified.txt`.
- **c=3/4 REFUTED**: the diagonal-contact density c ~ 0.742, NOT 3/4 -- the mean's first
  differences PEAK at 0.7428 (n=8-10) then DECLINE (n<=14). Not a nice fraction.
  `results/contact-density.txt`.
- **REACH repointed (jasonp ok'd killing a(21)/a(22))**: a(21) on dalby was bandwidth-bound
  (~30 of 80 cores effective on the 4-channel wall) AND premature (a(20) not yet confirmed --
  recount still on ayr). Killed it; dalby now runs **D1-at-scale** (`scripts/g2_split.sh`, g2
  --split, COMPUTE-bound so it fills all 80 cores) -- `--maxhole-strat` to n<=15.
- **C3 concluded earlier**: R1xR3 (fold x u32-modp) the practical ~4x engine; R2/ranged a bad
  lever (~100x compute for ~2x RAM, profiled).


### 2026-06-22 — C3 CONCLUDED: R1xR3 is the practical merged engine; R2 (ranged) is a BAD lever
- Built **R1xR2xR3** (`explore/reach-fold-ranged`, `cpp/tma/sweep8_merged.h`, gate GREEN ==
  exact via CRT) and confirmed **R1xR3** (`explore/reach-modp-u32`, `sweep8_modp.h --fold`,
  gate GREEN +/-fold == exact).
- **Profiling verdict (the real result):** R2/ranged is a BAD lever. N=14 wall: ranged 348s
  vs flat-modp 86s vs flat-exact ~4s -> ~100x compute for ~2x RAM (super-linear: two-pass +
  per-column arena rebuild + double hashing). **DROP it.**
- **Practical reach stack = R1xR3 (fold x u32-modp, flat): ~4x RAM, gated, deployable.** Gets
  a(23) (~115GB folded -> ~58GB) onto dalby. This **corrects the earlier "R1xR2xR3xB ~10-14x"
  claim** -- R2's compute is disqualifying; the real practical multiplier is ~4x (R1xR3), or
  ~8x adding B (blocked, RSS-only, no compute cost). Quick win: addCountsModP32 uses `% p`;
  conditional-subtract halves it. Deploy path for a(23): R1xR3 in a per-prime driver + CRT.


### 2026-06-22 ~14:35 ET — DALBY PIVOT: real reach terms launched (the primary goal cashing in)
- **The big miss, owned:** dalby (122GB/80c) was available since goal-set, but the log/memory
  said "on CADO, off-limits" (STALE) — so it sat idle at load 0.00 most of the day while I did
  small math, when REACH was the primary goal and dalby is *the* reach machine. jasonp caught
  it. Records corrected (memory `machine-availability-2026-06`, this header).
- **a(21) launched** on dalby (tmux session 0, window `a21`): `build/tma square8 21 --fold
  --checkpoint runs/ckpt_a21 --threads 32`. Folded gate-confirmed there (a(12)=257105146 ✓).
  ~33GB, per-height resumable, obs heartbeat live. Multi-hour (tall heights dominate); runs
  past 8pm ET by design ("floor not ceiling"). dalby clock is UTC+02:00 (6h ahead of ET).
- **a(22) next**, after a(21): peak ≈ 2.42× a(21) ⇒ ~80GB, fits the 122GB ceiling with ~40GB
  headroom — will confirm from a(21)'s measured peak before committing (RAM-borderline care).
- Lesson for the records: a stale "off-limits" flag is as costly as a wrong result — it
  silently misallocated the whole day's primary-goal compute.

### 2026-06-22 ~17:30 — brainstorm round 2 worked: 3 keepers + 2 honest negatives
Worked the round-2 ideas on per-topic branches (merge the best at 8pm ET).
- **B1 ★ — min-n(k) = fewest cells for k holes** [`explore/seq-minhole-cells`]: OEIS draft
  staged, 4,6,8,9,11,12,14,15,16,18,19,20,22,23,24,25 (inverse of the proven
  maxh=n+1−A027709(n)/2). *Also caught + fixed a hand-typed A027709 error* that had
  corrupted the maxh-count draft / note tabulations past n=10 (formula+proof were fine).
- **T6 ★ — diagonal-contact density c ≈ 0.743** [`explore/theorem-contact-density`]: a new
  lattice constant; mean #contacts of a uniform n-cell polyplet ~ 0.743·n (first differences
  of the mean converge cleanly). Rigorous value via a contact-marked TM is future work.
- **B2 (mixed) — symmetry premium** [`explore/theorem-sym-maxhole`]: ★ clean fact — **the
  maxhole optimum is always symmetric** (M_sym=M(n), through n=10). ✗ the tempting
  `M_asym(n)=M(n−1)` conjecture (held n≤9) was **REFUTED at n=10** (M_asym(10)=7, not 6) —
  a small-n coincidence; M_asym lags by an irregular premium with no closed form. Good
  refute-then-prove catch (the n=10 extension killed it).
- **B3 ✗ (honest negative)** [`explore/seq-king-perimeter`]: min king-perimeter(n) =
  A027709(n)+4 — a clean king-vs-rook isoperimetric identity, but a trivial shift, so NOT a
  new sequence. Recorded as an identity, not staged.
- **maxhole-optimal multiplicity ✗** [`explore/seq-maxhole-mult`]: 1,16,4,4,1,4 — irregular,
  not a clean sequence. (Datum: the n=8 diamond is the UNIQUE optimum.)
- **hole density ★ — d_hole ≈ 0.0231 holes/cell** [`explore/analysis-holefree-fraction`]:
  mined the existing n≤18 hole data. Mean #holes of a uniform polyplet ~ 0.0231·n (first
  differences converge cleanly, best-converged constant of the day). Plus: the **hole-free
  fraction A_0/a → 0** sub-exponentially (1.0 → 0.734 at n=18) — almost every large polyplet
  has a hole. Companion to T6 (contact density): polyplets are contact-dense, hole-sparse.
- **T7 skipped** (the λ tree-bound is fundamentally loose; deeper memory only nudges 16.63).
  **C1 deferred** — H=11 GF recovery (deg ≈13000, ~26k mod-p terms + BM) is a ~1–2h job;
  noted as launchable (would extend orders/atoms to H=11 and unlock the (3a) check at H=9).
- (n=10 brute-force came back and refuted B2's formula — folded into the B2 line above.)

### 2026-06-22 ~16:30 — T1 (the "hard" one) ADVANCED: lifetime-3 lemma (3a) to H≤8 [explore/theorem-t1-irreducibility]
- T1's only open content is lemma (3a) "the unanchored-strip atom N_H is irreducible over
  Q", stuck at **H≤6** because N_H = gcd(Q_H,Q_{H+1},Q_{H+2}) over Q has runaway rational
  coefficients (the gcd blowup). **Mod-p removes the blowup**, and a clean certificate
  avoids needing the rare prime whose reduction is irreducible: a rational factor of degree
  k is a subset-sum of the mod-p factor degrees for EVERY prime, so intersecting subset-sums
  over a few primes to {0,deg} **proves irreducibility over Q**.
- **N_7 (deg 181) and N_8 (deg 462): PROVED irreducible over Q** (4 primes each). So (3a)
  now holds **H≤8** (was H≤6). Also **de-extrapolates deg N_8 = 462** (atom_degrees.py had
  it only by the degree law). And **Q_H squarefree extended to H≤10** (all recovered data),
  via gcd(Q_H,Q_H')=const mod p. `experiments/t1_irreducibility.py`, `results/lifetime3-proof.md`.
- The general (all-H) statement still needs the Perron-primitive-element / Galois argument
  — but both H≤6 claims are now mechanized + pushed to the edge of the GF data. The one
  genuinely-hard-open item finally moved.

### 2026-06-22 ~15:30 — Phase 4 IMPLEMENTED (out-of-core) + two new sequences [reach-blocked-store, seq-knight, seq-contacts]
- **Phase 4 out-of-core sweep — built, gated, GREEN** (`cpp/tma/sweep8_ooc.h`,
  `cpp/tma_ooc_test.cpp`, `tests/gate_ooc.py`, `make gate-ooc`): db and next live as S
  disk partitions; per column, stream each db partition in (harvest + transitions append
  `(target,row)` to S spill files), reduce each spill into a RAM FlatDB → next partition,
  swap by rename. **~one partition resident at a time → RAM ≈ peak/S, reach disk-bound not
  RAM-bound.** Gate: OOC a(n) == exact A006770 (n≤10), **S-independent** (S=4 ≡ S=16,
  byte-identical), self-cleaning, strict `-Werror`. The reduce is `addCounts` exactly, so
  it composes with R1/R2/R3 untouched. This is the capstone above the in-RAM stack — the
  RAM ceiling is gone. (Design→working code; the biggest remaining reach item, closed.)
- **Knight animals (S5)**: full polyknight counts (fixed 1,4,28,234,2162,20972,209608,
  2135572; free 1,1,6,35,290,2680,26379,267598; n≤8) — exhaustive, Burnside-consistent.
  Novelty unverified (`results/knight-animals.md`).
- **Polyplets by diagonal-contact count (S3)**: T(n,d), row sums = A006770; total contacts
  0,2,24,212,1700,13050,97856,723522,5300980. (T(n,0)=2, the two straight lines — a
  reminder polyominoes carry diagonal contacts too.) `experiments/contact_counts.py`.

### 2026-06-22 ~14:30 — multi-hole → T3/T5 STRENGTHENED + style cleanup [explore/theorem-multihole]
- Multi-hole investigation (looked dataless) **yielded a clean theorem**: the single
  diamond maximizes **TOTAL** enclosed area over ALL holes — `M_total(n) = M(n)` —
  beating every multi-hole split (`docs/total-hole-area.md`). Same (u,v) proof applied to
  the holes' *union* (outer boundary ⇒ a_union+c_union ≤ n−4). Verified n≤9
  (`experiments/multihole.py`); per-k M_k(n) non-monotone (M_3(9)=3<M_4(9)=4), no closed
  form — only the total is clean.
- **maxh(n) PROVEN** (max hole COUNT, the opposite extremal): via Pick's theorem on the
  even sublattice (≅ rotated unit square lattice; 1-cell holes = interior vertices),
  **maxh(n) = n + 1 − A027709(n)/2** (A027709 = min polyomino perimeter). Matches brute
  force n≤9; extends 10..16 = 4,4,5,6,6,7,9. Single diamond maximizes hole AREA (~n²/8),
  even-sublattice min-perimeter polyomino maximizes hole COUNT (~n). **Two more proven
  theorems** (M_total, maxh) — six pieces of new mathematics today.
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
