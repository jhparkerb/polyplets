# Round-3 independence adversary — adjudicated levels, the isomorphism verdict, and the CRT audit

2026-08-12, independence adversary per `docs/triangle-round3-brief.md`, scored
under `docs/skeptical-reader-standard.md`, argued against
`results/triangle-r3-harness.md` Part 3 (the engines' shared rule, stated in
code terms). Probe: `experiments/tristruct/r3_adv_state_iso.py` (+ `.log`),
62 s laptop, exact integer arithmetic, a third implementation of the
cancellation DP written from the identity — not the branch's probe, not L6's.

**First line: the round's best candidate survives. L6-1 (residue/CRT ladder
on the cancellation DP) clears entry-ticket levels 1 AND 2 under hostile
read; its state object is measurably NOT the incumbent's Motzkin object; the
ranking does not change. Three corrections attach to it (14 primes not 13; a
rising-ratio RAM risk at H=20..21; a stencil-blind self-check pair), none
fatal, all phase-2-gate material.**

Cells named below: T(40,15) = 6374412577120147022430261962743, quoted from
`Triangle.load().cell(40,15)` this session; `tri.provenance(40,H)` =
`'real-sweep'` for H = 15, 20, 21 (loader classification
`experiments/tristruct/triangle.py:53-58`), matching harness Part 2.

---

## 1. The isomorphism verdict on the cancellation DP — measured, not argued

**Verdict: NOT the same object. The colour-coincidence state set strictly
CONTAINS the incumbent's connectivity state set from H = 7 up, the surplus is
exactly the crossing partitions, and the transition dynamics differ in kind:
the incumbent's defining move (uniting two distinct old labels) never occurs
in the colour DP, and the colour DP's defining moves (clash-zeroing,
join-at-birth of disconnected cells) never occur in the incumbent.**

Measurement (`r3_adv_state_iso.py` Part 4; my own colour DP and my own
union-find DP with stranded death, both validated first — Part 1: colour DP
[q¹] matches my own brute-force BFS at (2,4), (3,3), (3,4), (4,3) for every
n, [q⁰] ≡ 0, A_n(1) = C(HW,n)):

| H | colour cut states | Σ_{k≥1} C(H+1,2k)·Bell(k) | incumbent cut states | Motzkin(H+1)−1 | crossing states |
|---|---|---|---|---|---|
| 2 | 3 | 3 | 3 | 3 | 0 |
| 3 | 8 | 8 | 8 | 8 | 0 |
| 4 | 20 | 20 | 20 | 20 | 0 |
| 5 | 50 | 50 | 50 | 50 | 0 |
| 6 | 126 | 126 | 126 | 126 | 0 |
| 7 | 323 | 323 | 322 | 322 | 1 |
| 8 | 843 | 843 | 834 | 834 | 9 |
| 9 | 2242 | 2242 | 2187 | 2187 | 55 |

- **The distinguishing pair of states, exhibited.** At H = 7, the column
  state with fill rows {0,2,4,6} and run-partition ABAB — label tuple
  (1,0,2,0,1,0,2) — is reachable in the colour DP and does not exist in the
  incumbent's reachable set (crossing partitions are excluded there by the
  non-crossing lemma of `git show second-source:results/king-column-motzkin.md`,
  which my union-find census reproduces exactly as Motzkin(H+1)−1 at every
  H ≤ 9). It is the unique surplus state at H = 7.
- **Containment, checked:** every incumbent state appears among the colour
  states at every H ≤ 9 (colour ⊇ incumbent, strict from H = 7). So the
  honest geometry is *superset*, not disjointness: the L6 file's "larger and
  a different base" is the weak form of the right claim. A superset state
  space alone would NOT be independence — the incumbent's object rides
  inside it — which is why the level-2 verdict below rests on the dynamics
  and failure modes, not on the state census.
- **Dynamics.** My union-find DP logs merge events (two distinct old labels
  united by a new cell) at every H ≥ 3; the colour DP's three transition
  branches (extend/retire, join-at-birth, clash-drop) provably never
  identify two existing classes — a successor state never has two
  previously-distinct labels merged. No stranded-component death, no
  completion predicate (height/translation accounting is the strip engine's
  second-difference layer, already two-sourced and disjoint from
  connectivity).
- This independently confirms, with a third implementation, what the
  `second-source` branch had already measured (`git show
  second-source:results/scaling-exploration-A.md` §A-S4/A-S6: 2242 vs 2187
  at H = 9, closed forms Bell vs Catalan). L6's independence argument did
  not cite A-S4; it should have — the sharp question this round asked was
  answered there first. L3's parallel finding (contour cut states ≅ the
  Motzkin object, banked SVD ranks 21/51/127 = M(5)/M(6)/M(7)) is
  arithmetic-checked here too (my Motzkin column) and stands.

**Level-2 adjudication for the cancellation DP, stated against harness
Part 3.** Of the three shared propositions, the DP assumes only a corollary
of proposition 1 (frontier separation: cells more than one column back are
never king-adjacent to a future cell — a one-line Chebyshev fact, and the
weakest tier of sharedness, the adjacency definition itself). Proposition 2
(label partition as sufficient statistic, stranded death) and proposition 3
(completion predicate) are not assumed anywhere: disconnected subsets flow
through and cancel in ℤ[q]/(q²). Failure modes if the DP's rule were wrong:
fresh-class weight (q−b), ring truncation, class canonicalization,
clash-zeroing logic — none of which exists in any union-find engine; the
converse failure modes (wrong union, wrong death, wrong completion) have no
carrier in the DP. Disjoint, with the named shared residue above. **Levels 1
and 2: CLEARED. L6's self-assessment upheld.**

## 2. The residue/CRT layer, audited as arithmetic

- **Soundness of [q¹] mod p: YES.** The DP is ring arithmetic only
  (additions, multiplications by −b); ℤ → ℤ/p is a ring homomorphism
  commuting with the ℤ[q]/(q²) quotient, so per-prime runs compute C₁ mod p
  exactly. There is no division and no rational reconstruction, hence **no
  "leading coefficient vanishes" failure mode exists**: a vanishing residue
  C₁ ≡ 0 (mod p) is a legitimate value, demonstrated benign at probe scale
  (Part 3: residues mod 5, 7, 11, 13 all equal exact mod p, CRT
  reconstruction equals exact, vanishing cases (3,5), (5,5), (10,11), (5,13)
  handled correctly).
- **Prime count for the exact-value stretch: 14, not 13.** Measured exactly
  (Part 6): the product of the 13 largest 8-bit primes is 2^100.77 <
  T(40,15) = 2^102.33; 14 gives 2^108.25. L6's "13 runs exceed
  log₂ T(40,15) ≈ 103 bits" conflated 13×8 = 104 with the true Σ log₂ pᵢ
  (8-bit primes carry < 8 bits each; the same correction applies to the
  "8k bits per cell" line, which should read Σ log₂ pᵢ ≈ 7.9k). Immaterial
  to the verdict — one more days-scale run — but the phase-2 costing should
  say 14.
- Note the asymmetry: **testing** the banked band values needs no CRT at
  all — each prime run is a self-contained congruence check worth log₂ p
  bits; CRT-to-exact is needed only for the stretch claim. L6's framing is
  compatible with this; recording it so the phase-2 brief prices the two
  deliverables separately.
- **RED controls: one real gap found.** Measured (Part 2): with the NW
  adjacency deliberately dropped, BOTH structural self-checks still pass —
  [q⁰] ≡ 0 holds for any constraint graph, and A_n(1) = C(HW,n) evaluates
  every colouring as 1 regardless of constraints — while [q¹] is wrong at
  n = 2..10. **The two identities L6's disclosure block offers as the
  checker are blind to stencil errors.** They do catch weight/truncation
  corruption (L6's own RED, reproduced). The stencil is covered only by the
  small-n brute-force battery (present in both L6's probe and mine) and by
  the banked-cell comparison at H ≤ 10 (legitimate there: those cells are
  strip-confirmed two-source). A phase-2 gate plan must include the brute
  battery per built binary as a first-class RED, not the two identities
  alone. A reconstruction-level control worth adding: hold out one prime,
  reconstruct from the rest, predict the held-out residue.
- **Cost-model risk, quantified.** My window census (Part 5) reproduces the
  branch's bit-for-bit at every H = 4..12 and shows the per-height ratio
  RISING steadily — 2.467 → 2.817 over H = 5..12 (+0.045/step), Bell-driven,
  not flat at 2.9. Continuing the measured trend instead of L6's flat
  ×2.9: H = 20 ≈ 7.1×10⁸ windows ≈ 74 GB (vs L6's 55 GB) — still inside
  ayr's 78 GB but with no margin; H = 21 ≈ 2.3×10⁹ ≈ 235 GB (vs 160 GB).
  The H = 15..20-in-RAM headline survives; the H = 20 sizing is tight and
  the H = 21 phase-2 number is understated ~1.5×. Queue row filed for the
  cost adversary; an exact census at H = 15..16 (hours-scale) would pin it.
- **"The variant no branch priced": accurate as stated.** Verified against
  `git show 5793ddf:results/second-source-candidates-B.md` (read in full,
  plus candidates-A and the 2b3115b team brief): the branch *anticipated*
  the idea in one sentence ("B1 at production scale would likely use CRT
  internally for coefficient arithmetic; that is arithmetic plumbing … not
  the banned 'CRT as a second source'") but priced only exact payloads
  (I256/u128; "H ≥ 18 stays dead (~210 GB)"). No residue-payload RAM table
  or ceiling exists on any branch. L6's own concession — "a variant pricing,
  not a new method" — is the correct score.

## 3. Adjudicated level table, all lanes

| candidate | claimed | adjudicated | argument in one line | evidence |
|---|---|---|---|---|
| **L6-1** residue ladder on cancellation DP | 1+2 | **1+2 — upheld** | no union/death/completion anywhere; state object measurably ⊋ Motzkin with different dynamics; shared residue = adjacency definition + frontier separation only | §1, §2; `r3_adv_state_iso.py` Parts 1–4 |
| **L6-2** raw spin basis q=2 mod 2 | 1+2 | **1+2 — upheld** | no partitions in the state at all; marginal value as L6 itself says (bit already two-sourced, one source label-free) | mechanism inspection; harness Part 3 on symcount_fast |
| **L4** quotient-domain `--byheight` | 1+2, priced out | **1+2, priced out — upheld** | symcount_fast BFS-on-lifted-set, no cut (harness Part 3 concurs); failure modes global-object; the routing audit (3 of 4 mod-4 inputs currently frontier-class) is verified against harness and is the lane's sharpest finding | `results/triangle-r3-l4-quotient.md`; harness §symcount_fast |
| **L3** contour | 1 only, 2 fails by isomorphism | **1 only — upheld, honest self-grade** | cut object = (fill, non-crossing partition) = the incumbent's exact state set; rank identities M(5)/M(6)/M(7) = 21/51/127 arithmetic-checked here | `results/triangle-r3-l3-contour.md` §3; my Motzkin column |
| **L1** corner gluing | 1 only (non-executable variant); executable variant neither | **upheld, honest self-grade** | piece states ⊋ cell frontier at every measured H (their cell baseline = Motzkin(H+1)−1 matches my census exactly); assembly DP inherits the frontier failure class | `results/triangle-r3-l1-corner-gluing.md`; my Part 4 incumbent column |
| **L5** Lean / ASP / CNF | 1 all; 2 Lean full, ASP argued, CNF partial | **upheld** | Lean: decision procedure is Mathlib's, no cut — level 2 clean; CNF "partial" is the right call (component cache is partition-shaped; the semantics-vs-performance asymmetry is fair but the run-time structure is frontier-shaped, so ranking it below Lean is correct) | `results/triangle-r3-l5-constraint.md` |
| **involution scout** | closure; both levels "would clear trivially", moot | **upheld** | forced-parity lemma is correct (any two correct involutions agree by necessity); the merger into L6-1 is real — the sign-reversing involution on (subset, colouring) IS the cancellation identity | `results/triangle-r3-involution.md` |

Every lane graded itself honestly; no self-assessment is overturned. The
project standard rewards that and it is recorded here as fact, not
courtesy.

## 4. Ranked list, by the round's criteria

1. **L6-1** — both levels, reaches H = 15..20 in RAM (48.00% of a(40),
   band cells all `'real-sweep'`), 14-run CRT stretch to exact at H ≤ 20;
   the round's only live phase-2 route. Carry the three corrections (§2)
   into any phase-2 brief.
2. **L6-2** — both levels, H = 20..21 mod 2 backstop; real but marginal.
3. **L4 quotient route** — both levels, correctly declined on its own
   answer-size floor; its durable products are the routing audit and the
   mod-8 ceiling proof.
4. **L5 Lean formalisation** — definition-level witness, cheapest checker
   in the round; no reach, and never claimed any.
5. **L3, L1** — established negatives with named obstructions; L3's
   rank-equality identity and L1's piece-refines-frontier measurement are
   the round's two best pruning facts.

## 5. Queue rows filed

Appended to `results/triangle-r3-queue.md` as ADV-1 (stencil-blind
self-checks → phase-2 gate requirement), ADV-2 (rising window-ratio RAM
risk at H = 20..21, exact census H = 15..16 would pin it), ADV-3 (14-prime
correction + hold-out-prime RED for the reconstruction).

## 6. Appended 2026-08-12 late — the census made EXACT at H = 15..21

Dispatch from the lead after §2's rising-ratio flag: pin the window census at
H = 15..16 and beyond. Result: **the whole curve is now exact arithmetic, not
a fit** — the extrapolation risk in §2 and queue row ADV-2 is retired.
Script: `experiments/tristruct/r3_adv_window_census.py` (+ `.log`), 1.6 s.

**The closed form.** The window's king-adjacency graph decomposes into two
consecutive-slot paths plus ≤ 3 cross edges with endpoints in slots
{0, 1, H−1, H} (verified programmatically at every (H, r) used). With the
reachability hypothesis "every (mask, partition-of-window-chunks) pair is a
state", census(H) = max over kink position r of Σ_masks Bell(#chunks). That
hypothesis **matches the measured census exactly at all eleven points
H = 4..14** (mine/L6's/branch's Python census H ≤ 12, branch C++ 306,858 and
891,074 at H = 13, 14), and the polynomial-cost path-DP evaluation equals
direct mask enumeration at every (H, r), H ≤ 14, before being used above
H = 14. Argmax is r = 0 at every H.

| H | windows (exact) | ratio | cut states (exact) | RAM 8-bit | RAM 63-bit | wall, 1 thread |
|---|---|---|---|---|---|---|
| 15 | 2,624,197 | 2.9450 | 1,132,106 | 0.3 GiB | 1.7 GiB | 0.7 h |
| 16 | 7,832,667 | 2.9848 | 3,365,626 | 0.8 GiB | 4.9 GiB | 2.1 h |
| 17 | 23,681,423 | 3.0234 | 10,137,558 | 2.3 GiB | 15.0 GiB | 6.1 h |
| 18 | 72,487,711 | 3.0610 | 30,920,942 | 7.0 GiB | 45.8 GiB | 17.8 h |
| 19 | 224,529,648 | 3.0975 | 95,457,177 | 21.7 GiB | 141.8 GiB | 52.9 h |
| 20 | 703,470,478 | 3.1331 | 298,128,277 | **68.1 GiB** | 444.2 GiB | 158 h |
| 21 | 2,228,466,695 | 3.1678 | 941,574,416 | **215.8 GiB** | 1407 GiB | 477 h |

- **The ratio is still rising at 15..21 and does not converge**: 2.9450 →
  3.1678, increments +0.040 shrinking to +0.035 per step. This is
  Bell-driven — no finite limit exists (the incumbent's Motzkin ratio tends
  to 3; the colour census ratio passes 3 at H = 17 and keeps climbing). No
  fit was made and none is needed: the numbers above are exact.
- **Payload model, stated explicitly** (L6's/the branch's): ~22 B key+hash
  per window; payload = 41 area slots × bytes(modulus) × 2 buffers = 104
  B/window at an 8-bit prime, 678 B/window at a 63-bit prime. Wall =
  windows × 41 × 0.94 µs/slot-col (branch-measured at H = 14) × (41−H)
  columns.
- **Where the corrections land vs L6's table:** H = 15..17 essentially as
  priced; H = 18: 72.5M vs 63M; H = 19: 224.5M vs 183M (21.7 vs 19 GB);
  H = 20: 703.5M vs 530M — **68.1 GiB vs 55 GB**; H = 21: 2.23G vs 1.54G —
  **215.8 GiB vs 160 GB**.
- **Phase-2 shape the exact numbers support.** H = 15..19 (43.84% of a(40),
  the standard's largest unconfirmed block, all `'real-sweep'`) is a
  comfortable ayr job at ≤ 21.7 GiB. H = 20 is a **sole-tenant** ayr job:
  68.1 GiB against 78 GB total leaves ~10 GiB for everything else, so it
  fits iff the real bytes-per-window stays ≤ ~119 — a constant measurable
  from the actual binary at small H, and the single go/no-go number a
  phase-2 brief must pin first (hash-table load factor and allocator
  overhead are exactly the kind of ×1.2 that breaks it; a flat sorted-array
  double buffer would beat 104 B). H = 21 does not fit ayr under any
  bookkeeping: dalby RAM or out-of-core, or it stays kink-only. Wall at
  H = 20 is ~158 thread-hours — days-scale parallel, as L6 said.
- The cut-census column is exact arithmetic under the all-pairs
  reachability verified at H ≤ 9 (Part 4); it is not the RAM driver and is
  listed for completeness.

Queue row ADV-4 filed, superseding ADV-2.

## NOT ESTABLISHED

- ~~No census at H = 15..21 exists anywhere; the H = 20/21 RAM numbers in
  §2 are trend extrapolations~~ — superseded by §6: exact, under a
  reachability hypothesis verified at all eleven measured points and a
  window-graph decomposition asserted programmatically. What would still
  upset it: a reachability failure appearing first at H ≥ 15 (no mechanism
  visible — the join/fresh/clash moves that realise every partition at
  H ≤ 14 do not change character with H).
- The 104 B/window payload constant is the model's, not a measurement; the
  real bytes-per-window of a built binary decides H = 20-on-ayr (§6).
- Whether the branch's B1 calibration run (H = 15/16 on dalby, live
  2026-08-11 per its file) completed — same gap L6 declared; its walls
  would replace both my and L6's extrapolated first rows.
- L6-2's throughput estimate was not audited (L6 already marks it as its
  weakest number; nothing in my read depends on it).
- The ASP and CNF routes' third-party evaluations remain blocked on
  toolchain installs (L5 declares this; nothing to add).
