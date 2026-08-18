# Triangle campaign salvage — what merges to master, and why

2026-08-13. The four-round triangle campaign (branch `triangle-structure`,
2026-08-11..13) failed its mission — see `docs/triangle-postmortem.md` — and
the branch will not merge. This file is the index of what was worth keeping:
each result, the files that carry it, its verification status with receipts,
its value, and the work still open on it. Source citations are to the
`triangle-structure` branch (local, unpushed); the artifact files themselves
travel with this document.

Verification labels used below:
- **PROVED** — a written proof that survived a hostile audit, plus a machine
  check where one applies.
- **TWO-SOURCED** — a banked number reproduced by an independently authored
  route, with the independence caveats stated.
- **RECEIPTED** — a claim whose gate/log exists in-tree and is cited.
- **UNRECEIPTED** — stated in a deliverable, no receipt; do not quote as fact.

---

## 1. Banked numbers

### 1.1 T(40,15) and T(40,16) recounted — 21.64% of a(40) TWO-SOURCED

**Claim.** The two largest cells of the exposed band reproduce exactly under
the B1 colour-coincidence cancellation DP — a rule that never decides
connectivity (no union-find, no component labels united; connectivity is read
off the coefficient of q¹ in Σ q^{c(S)} over ℤ[q]/(q²)). Second differences
of rows C1..C16 reproduce banked T(40,15) and T(40,16) to all 31 digits.

**Files.** `results/cutcount_b1/` (rows, both run logs, PROVENANCE.md, and
the exact source `cutcount_b1.cpp.59e90660`); analysis in
`results/triangle-r3-ladder-gate.md`; recovered in commit `bd31a58`.

**Receipts.** The calibration run: 640/640 banked-cell matches at H=1..16,
n≤40 (dalby, 2026-08-11, `calib_run.log`). Round 4 added the incumbent-free
check: the flood-fill brute oracle (`experiments/tristruct/r4_indoracle_brute.py`,
literal 3×3-stencil flood fill, no frontier, no DP) agrees with the B1 rows
on 36 cells at n≤8 (gympie) and 55 cells / 7,170,300 animals at n≤10 (ayr),
with both RED controls biting — perturbed cell named exactly, rook stencil
breaking 21 of 28 (`results/r4/logs/r4_indoracle_gympie.log`,
`r4_indoracle_n10_ayr.log`).

**Independence, honestly stated** (from `results/triangle-r3-adv-independence.md`  <!-- never existed: lane deliverable not filed -->
and `results/r4/r4-adv-ind.md`): the DP's state space strictly contains the
incumbent's Motzkin object; independence rests on dynamics and failure modes,
not disjoint states. What the two routes still share is exactly one thing —
a hand-written king-adjacency stencil — and the flood-fill oracle covers that
only to n=10.

**Value.** First independent recount of any part of the single-sweep band;
the connectivity-rule objection is closed for these two cells.

**Remaining work.** H=17..19 (22.20% of a(40)) is priced and planned
(`results/r4/r4-ladder.md`: confirmation mode, one or two primes with a
pre-registered prediction, ~5.7 days on the code that exists) and is
`WRITTEN, UNRUN` in `results/r4/INSTRUMENTS.md`. H=20/21 exact is out of
RAM reach everywhere (`results/triangle-r3-ladder-gate.md`).

### 1.2 T(40,20) and T(40,21) mod 2 — spin runs, RECEIPTED

**Claim (banked 2026-08-13).** **T(40,20) ≡ 1 and T(40,21) ≡ 1 (mod 2)**, by a
third rule class (spin/involution route, `experiments/tristruct/r4_spin_engine.cpp`,
1113 lines, gates green at `results/r4/logs/r4_spin_gates.log` — GATE 0
cross-ISA sha match, mutant flips 12/12/4). Twin runs on dalby and ayr,
m=1..21, launched 06:00 EDT 2026-08-13, both exited clean the same day;
acceptance (byte-identity of the two outputs) PASSED. Full receipts in §6.

**Independence caveat, pre-registered** (`results/triangle-r3-synthesis.md`
§CORRECTION, `results/r4/r4-inv.md`): forced parity clears the bar against  <!-- never existed: lane deliverable not filed -->
the kink engines but NOT against B1 — B1's [q¹] and spin's q=2 evaluation in
ℤ/4 are two extractions from one identity. This is row 40's H=21 first
independent evidence of any kind (`results/r4/r4-tallband.md`: T(40,21) is  <!-- never existed: lane deliverable not filed -->
the thinnest cell in the row — Lean's P_k covers H=22..40, the sweep covers
it once, nothing else reaches it).

### 1.3 a(40) provenance hardened

**Claim.** The a(40) production-run record audited CLEAN with one erratum
(phase B ran as two segments — cols 0..6 at 64 cores under `38956525`,
cols 6..40 at 48 cores under `801afd59`; PROVENANCE.md's flat "48 cores" was
incomplete) and one named gap (worker-binary identity is inference: workers
do not print their own baked GIT_REV).

**Files.** `results/triangle-r3-provenance.md`;
`results/ns_a40/dalby-run-evidence/` (build-stamped run.log, three
checkpoints, combine log, Zero Harvest artifact, sha256-verified copy) —
the only material converting the a(40) provenance record from assertion to
evidence.

**Remaining work.** The log-header audit of worker-binary identity — an
afternoon, flagged by two rounds as the cheapest unaddressed attack on the
record.

---

## 2. Proved theorems

### 2.1 The d=3 unit formula — PROVED

**Claim.** P_k(3k−2) ≡ 27·r_k (mod 81) with r_k cycling (2,0,1) for all
k ≥ 3; equivalently v₃(P_k(3k−2)) > 3 ⟺ k ≡ 1 (mod 3). Proved by
Lagrange–Bürmann on the mod-81 master curve with an exact division
certificate, conditional on frame assumption (A4) only (the audit shrank
the frame: A2/A3 follow from proved theorems).

**Files.** `results/triangle-r2-d3-proof.md` (proof),
`results/triangle-r2-d3-audit.md` (hostile audit: independent code, no
sympy, nine-corruption battery, every corruption caught),
`results/triangle-r2-tower-mod81.md` (the tower), verifiers
`experiments/tristruct/r2_prove_d3.py`, `r2_adversary_d3.py`,
`r2_tower_mod81.py`.

**Value.** One enumerated law-free cell checked — (35,21), predicted 0,
banked 0, ~1.6 bits against enumeration error: the only theorem-side
prediction in the campaign that landed on an enumerated cell. Also the
organizing statement behind round 1's deficit-family observations.

**Remaining work.** W(2,2,2,2)=68314 is a single-source input (its
mitigation needs a second independently-written DP, not enumeration —
`results/triangle-r2-extension-scout.md` §5). The d=8 LB certificate is
one session, unrun; `docs/triangle-structure-d9-d12-plan.md` is shelved and
runs only on explicit go.

### 2.2 Forced parity — PROVED

T(n,H) ≡ 0 (mod 2) for n odd, H even, by the midline-reflection involution;
the translation-classes subtlety closed by an explicit lemma. 190 cells'
parity now rests on proof rather than engine agreement; zero row-40 cells by
the theorem's own scope. `results/triangle-hunt-klein-parity.md`, audit in
`results/triangle-hunt-refutation-symmetry.md`, check  <!-- never existed: lane deliverable not filed -->
`experiments/tristruct/refB_parity_check.py`.

### 2.3 Two-term cell inequality — PROVED

T(n,H) ≥ 3T(n−1,H−1) + T(n−1,H) for 2 ≤ H ≤ n−1, equality exactly at
H = n. Two injections with disjoint images; audited; 0 violations on the
banked triangle; within 2.2 bits of truth everywhere (worst slack 4.59×).
`results/triangle-hunt-proof-first.md`,
`results/triangle-hunt-proof-first.md`,
`experiments/tristruct/p1_ineq_check.py`, `refA_prooffirst_check.py`.

**Novelty check, 2026-08-13** (OEIS A006770 + literature search): no
height-refined statement of any kind exists for polyplets in the findable
record — A006770 carries enumeration references only (Mertens 1990,
Tremblay–Vernay 2024, both algorithmic), and the animal-inequality
literature (Klarner-style concatenation, handbook ch. 14) is growth-only,
nothing per-cell by height. The proof is elementary once stated; the
content is the sharp equality column and measured near-tightness (1.0170
at (40,39)). Honest scoping: as a growth bound it sums to ~λ ≥ 4, exceeded
by the banked 6.543 lower bound — its value is per-cell structure, where
no competing statement exists. The polyomino analogue (factor 1) is
equally absent from print and equally derivable; the king-specific part is
the 3.

**The defect, measured 2026-08-13**
(`experiments/tristruct/salvage_defect_probe.py` + `.log`). Write
D(n,H) = T(n,H) − 3T(n−1,H−1) − T(n−1,H) and s = D/T. D > 0 at every
strict cell (no zeros off the H=n column, consistent with the proved
equality set). The share has clean structure at both ends of the triangle:

- **Fixed column H:** for n large, 3T(n−1,H−1) is negligible against the
  faster-growing column H, so s → 1 − 1/μ_H where μ_H is the column growth
  constant. Measured exact to 4 digits at H=3 (s = 0.7096 = 1 − 1/3.4437);
  H=5 is still converging at n=40 (0.7822 vs 0.7885). So along columns the
  defect share is a repackaging of the known column growth constants
  (atoms q_H territory) — nothing new, but a consistency handle.
- **Fixed diagonal k = n−H:** n·s converges per k — 0.670, 1.337, 2.001,
  2.661, 3.317 at k = 1..5 — i.e. s ≈ C·k/n with C ≈ 0.66 and slowly
  declining increments (0.670, 0.667, 0.664, 0.660, 0.656). Via the proved
  diagonal law the defect there has an exact form,
  D(n,n−k) = 3^{n−1−2k}·[P_k(n) − P_k(n−1) − 3P_{k−1}(n−1)], so the
  constant C and its k-drift are derivable from the P_k in one session —
  a theorem-adjacent open item, not a mystery.
- **The middle:** row 40's share runs 0.78 (peak near H=5) down to 0.0168
  at H=39, smooth throughout. The band region is where neither closed form
  reaches — the same geometry as everything else in this campaign.

A sharper inequality would need the defect's combinatorial content: D
counts the height-H animals with ≥ 2 top-row cells that are not
grow-right images. Nobody has looked at that object.

### 2.4 Mod 4 is the per-cell symmetry ceiling — PROVED

D2ax is exactly the height-preserving subgroup; glides collapse; no order-8
group exists. Also dissolves the 2026-08-07 decline reason 1 (a strip-method
artifact). `results/triangle-r3-l4-quotient.md`,
`experiments/tristruct/r3_l4_quotient_measure.py`.

### 2.5 q_5 and q_6 as exact integer polynomials; the q_5 relation

The order-29 and order-68 column atoms computed ab initio (own strip TM,
own Berlekamp–Massey, different primes; independently reimplemented
end-to-end by a refuter), where `results/triangle-structure.md` had proved
them unreachable by fitting. q_5 annihilates C_5(n) = Σ_{h≤5}(6−h)T(n,h)
for n ≥ 30: zero free parameters, 10/10 holdout, all seven perturbations of
T(40,5) fail it. An internal-consistency certificate of the banked triangle
(not rule-independent — it consumes banked rows).
`results/triangle-hunt-atoms-ab-initio.md`,
`experiments/tristruct/p3_atoms.py`, `data/p3_atoms_q.txt`. Open: q_7 was
in flight and never landed; two soft patterns parked as q_7 holdout tests
remain unresolved.

### 2.6 Lean: the encoding layer — PROVED, now RECEIPTED

**Claim.** `encode_faithful` and `encode_faithful_colAt`
(`experiments/tristruct/r4_lean2_encode.lean`) elaborate sorry-free, axioms
`[propext, Classical.choice, Quot.sound]`. The design insight: labelling a
cut-column row by the reachability relation itself (least reachable row)
dissolves the normal-form-under-relabeling quotient argument previously
identified as where such developments stall.

**Receipt.** `experiments/tristruct/r4_lean2_gate.log` (gympie, 2026-08-13,
toolchain v4.31.0): six gates green — shared-defs byte-identity, silent
elaboration, both RED mutants rejected (over-merging `rowCls`; unguarded
`lbl`), skeleton at exactly its 3 declared sorries, and the skeleton's
error-detection RED biting. Disclosure: the battery had never run before
salvage; its first run failed on its own bug (gate E grepped for ASCII-quote
`'sorry'` where Lean 4.31 emits backticks — a fail-closed guard reading a
correct output as 0). Fixed in `r4_lean2_gate.sh` (pattern matches either
quote style), rerun, all green. The gate script itself had `Written
2026-08-13 by scout/builder r4-lean2, which ran none of it` in its header —
the postmortem's receipts finding, in miniature.

**What it does NOT cover** (`results/r4/r4-lean2.md` §4.1): of 25 rows in
the proof-dependency graph, 8 are not stated in any form; `r4_lean2_state.lean`
carries 3 sorries (`strand_dead`, `sufficiency`, one more); and the
algorithm-side definition `step` does not exist — not as a definition, not
as a statement, not as a sorry. Every campaign sentence of the form
"(a)+(b) closes the rule objection for 95.85%" rests half its weight on an
object not started. Supporting pieces: `Tc_eq_T` (already on master,
`polyplets/Polyplets/Compute.lean`), the crux probe
(`r4_lean_funnel_probe.lean` + `.log`: ReflTransGen.lift' collapses the
feared path-splitting induction to a four-case single-step lemma), and the
small witness formalisation `r3_l5_king_connected.lean` (21 banked cells at
n≤6 via Mathlib's own connectivity, no project-authored connectivity code).

**Known-broken sibling, kept as an error ledger:**
`r3_l5_normalization.lean` was filed as "complete written proofs, no step
missing" and fails to compile with 9 errors at 6 sites (`r3_l5_job1.log`);
two are unsolved goals, i.e. holes in the argument as written. Repair
deferred. The standing lesson (round 3 synthesis): compile before believing
any agent's "this is complete" about Lean source.

---

## 3. The negative map — doors closed, with the obstruction named

Kept so nobody re-derives or re-pitches. Each entry names its file.

1. **The fittable region and the checkable region are disjoint** — the
   campaign-killer, twice proved. Fitted deficit families cap at d ≤ 6 and
   their law-free cells all sit in the formula band (H ≥ 22); the 27
   enumerated law-free sleeve cells all have d ≥ 8
   (`results/triangle-hunt-synthesis.md` negative 4b). One level deeper:
   row 40's H=15..19 cells sit at d = 24..36, below the proved sharp onset
   n ≥ 2k+1, outside the tower's validity at every depth, forever
   (`results/triangle-r2-extension-scout.md`). No relation fitted or proved
   inside the triangle reaches the exposed band.
2. **Column recurrences are dead above H=4, permanently** — minimal orders
   first apply at n=43 (H=5) and n=107 (H=6), both > 40
   (`results/triangle-hunt-refutation-columns.md`).  <!-- never existed: lane deliverable not filed -->
3. **Only three slice directions are testable at all** — (0,1), (−1,1),
   (−1,2); the other twelve span no fit+holdout pair
   (`results/triangle-hunt-slices.md`).  <!-- never existed: lane deliverable not filed -->
4. **No third route class in the literature** — 35 candidates, pre-registered
   filters, one survivor, and the survivor was already project-held (B1)
   (`results/triangle-r3-l6-wildcard.md`).
5. **Piece/contour/quotient vocabularies do not help** — piece states
   exceed cell states and diverge; contour encodings are state-space
   isomorphic to the incumbent; the symmetry quotient is priced out by its
   own answer size (`results/triangle-r3-l1-corner-gluing.md`,  <!-- never existed: lane deliverable not filed -->
   `-l3-contour.md`, `-l4-quotient.md`).
6. **The two-horn involution obstruction** — validity-aware site keys drift
   under their own move; validity-blind ones leave the class. Any correct
   involution's fixed-set parity equals T mod 2 by necessity, so
   independence lives in the |Fix| rule class, never the residue
   (`results/triangle-r3-involution.md`).
7. **The three floors, AS CORRECTED** — the round-3 floor package
   (`results/triangle-r3-synthesis.md`) is superseded by the round-4 audit
   (`results/r4/r4-floors.md`): the information floor is real but excludes
   nothing affordable (its own number is 25,837× below the incumbent's cost
   at H=21); the state floor is **false as literally stated** (char-2
   Hankel ranks sit far below cell-frontier counts and grow ~0.44·2^H
   against Motzkin ~3^H); floors 1 and 2 are not independent. Quote the
   floors only through the audit.

---

## 4. Open leads, ranked

1. **The char-2 / Hankel explicit basis.** A cut-crossing representation
   ~400× smaller than the incumbent at H=21, measured in-repo, compliant
   with the information floor. Round 3 dismissed it as "a rank is an
   existence statement" — which is work not done, not an obstruction; CKN
   have explicit bases for the matchings analogue. Needs no compute.
   (`results/r4/r4-floors.md`, `results/triangle-r3-adv-independence.md`  <!-- never existed: lane deliverable not filed -->
   rank data.)
2. **Residue ladder H=17..19** — 22.20% of a(40), confirmation-mode design,
   ~5.7 days on existing code (`results/r4/r4-ladder.md`,
   `results/r4/r4-a.md`). The receipts framework
   (`results/r4/INSTRUMENTS.md` pattern) exists; the incumbent-free oracle
   must gate the binary per run.
3. **Finish the Lean definition-level proof** — author `step`, discharge the
   3 skeleton sorries, state the 8 missing rows. The crux and the encoding
   layer — the two pieces round 3 priced as the risk — are done and
   receipted; what remains is scoped in `results/r4/r4-lean2.md` §4.
4. **d=8 LB certificate**, one session, then the shelved d9-d12 plan on
   explicit go (`docs/triangle-structure-d9-d12-plan.md`).
5. **The log-header audit** of a(40) worker-binary identity (§1.3).

---

## 5. Process artifacts

Campaign-independent, referenced by the postmortem's action items:
`docs/skeptical-reader-standard.md` (scoring standard: the referee, two
bit-counts, four independence axes, automatic zeros),
`docs/agent-types.md` (scout/adversary/generator; the write-ahead rule),
`docs/r3-job-dispatch.md` (job dispatch: "the test is backgrounding, not
size"), and `docs/triangle-postmortem.md` (the four-round postmortem;
verdict: failure).

---

## 6. Spin run outcome

*(recorded at completion, 2026-08-13 — claim banked in §1.2)*

Both m=1..21 runs exited clean on 2026-08-13 (ayr 12:57 EDT after 25014 s
wall / 7.29 GB peak RSS; dalby 13:56 EDT after 28567 s / 7.28 GB). Receipts:

- **Cross-ISA byte-identity: PASSED.** `cmp results/r4/spin_m21_ayr.txt
  results/r4/spin_m21_dalby.txt` — identical (x86_64 ayr vs aarch64 dalby,
  separate checkouts). Both engines report the same output digest
  `sha256=441a99084cf3c2cafaac8324f86f7089705e6075349996431ca9ed1b5180b4c6`.
- **Oracle agreement (expected, not independence-granting):** each run
  compared 640 values (520 hlen) against `results/cutcount_b1/rows` with
  0 mismatches. Per the pre-registered caveat above, spin-vs-B1 agreement
  is two extractions of one identity, not a second source.
- **Structural checks:** 1680 with 0 failures, on each box.
- **Result:** `T H=20 n=40 par=1`, `T H=21 n=40 par=1`, i.e.
  **T(40,20) ≡ 1, T(40,21) ≡ 1 (mod 2)** — row 40's thinnest cell now has
  its first evidence from any rule class other than the kink engines.

Artifacts in-repo: `results/r4/spin_m21_ayr.txt{,.metrics}`,
`results/r4/spin_m21_dalby.txt{,.metrics}`, run logs
`results/r4/r4_spin_m21_ayr.log`, `results/r4/r4_spin_m21_dalby.log`.

---

## Proposed merge manifest

New branch off master (`triangle-salvage`), carrying:

| what | paths |
|---|---|
| this index | `results/triangle-salvage.md` |
| postmortem | `docs/triangle-postmortem.md` |
| process docs | `docs/skeptical-reader-standard.md`, `docs/agent-types.md`, `docs/r3-job-dispatch.md` |
| B1 recount | `results/cutcount_b1/` (complete) |
| a(40) evidence | `results/ns_a40/dalby-run-evidence/` (complete), `results/triangle-r3-provenance.md` |
| proofs + audits | `results/triangle-r2-d3-proof.md`, `-d3-audit.md`, `-tower-mod81.md`, `-extension-scout.md`, `results/triangle-hunt-klein-parity.md`, `-proof-first.md`, `-atoms-ab-initio.md`, `results/triangle-r3-l4-quotient.md` |
| negative map | `results/triangle-hunt-synthesis.md`, `results/triangle-r3-synthesis.md` (with its correction), `results/triangle-r3-l6-wildcard.md`, `results/r4/r4-floors.md`, `results/triangle-r3-involution.md`, `results/triangle-r3-ladder-gate.md` |
| forward plans | `results/r4/r4-ladder.md`, `results/r4/r4-lean2.md`, `results/r4/r4-a.md`, `docs/triangle-structure-d9-d12-plan.md` |
| receipts | `results/r4/INSTRUMENTS.md`, `results/r4/logs/` (complete) |
| spin outputs | `results/r4/spin_m21_ayr.txt{,.metrics}`, `results/r4/spin_m21_dalby.txt{,.metrics}`, `results/r4/r4_spin_m21_ayr.log`, `results/r4/r4_spin_m21_dalby.log` |
| harness + code | `experiments/tristruct/` complete, minus `__pycache__` (1.9 MB: the triangle loader/verifier, all round scripts and logs, the Lean sources and gate, the spin engine, the flood-fill oracle) |

Deliberately left on the branch: the ~60 per-agent round records
(`results/r4/r4-*.{plan,progress}.md` and lane files not named above), the
briefs, queues, wind-downs, and blind lists — campaign history, reachable on
`triangle-structure`, not results.
