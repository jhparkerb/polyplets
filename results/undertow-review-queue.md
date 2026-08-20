# Undertow review — the queue

Append-only. Row format:

    | id | lane | status | rank | what |

`status` is OPEN / CLOSED / DROPPED. A lane that closes a candidate files at
least two successor rows, different in kind, not parameter tweaks. Half-formed
rows are wanted. Cross-lane rows are wanted. Pruned near-misses go here, never
into a silent cap.

Each lane's FIRST action is to append its own findings list, timestamped,
before reading any other lane's output.

| id | lane | status | rank | what |
|---|---|---|---|---|

## Lane C blind findings list — filed 2026-08-20 07:26 EDT, before reading any other lane's output

Candidates for the real obstruction and routes past it, filed before
investigation. Status column to be resolved in undertow-review-C.md.

- C1. Hypothesis: the W1 obstruction is the connectivity-partition frontier in
  the stack DP (Bell-number state growth) — the same wall that killed the four
  engine levers. If so, it is a family-level obstruction, not an instance one.
- C2. Route: symmetry quotient (left-right reflection) of the W1 DP state.
  Expected constant-factor (~2x) — buys at most one level. Check whether
  cpp/severance_w1.cpp already does it.
- C3. Route: frontier compression via canonical partition relabeling/hashing in
  the W1 stack DP. Check what the state actually is before pricing this.
- C4. Route: repackage cluster-weight extraction as a column transfer matrix
  over the defect strip (height <= k+1) instead of the stack DP — trade
  ~20x/level memory for a 3^H-style cost profile. May already be equivalent to
  the incumbent sweep, in which case it is not "freedom".
- C5. Route: algebraic-GF ladder. Depth-1 defect GF is algebraic and reached
  k=200 (results/onset-defect-depth1-closed.md); algebraicity at depth j>=2 is
  listed open. If depth-j GFs close in j, invert the Undertow linear relations
  to get (a_k, b_k) from defect series alone, no swept cell. Key question:
  determinacy — whether the defect family actually pins both constants or is
  underdetermined without one enumerated fact per level.
- C6. Definitional finding (suspected): two new constants per level require two
  exact facts per level from SOMEWHERE. "Freedom from fitting" can only mean
  freedom from the incumbent enumeration engine, not freedom from exact
  computation. If every exact source (sweep, brute force at n=2k+1, cluster DP)
  is itself an enumeration, the question reduces to which enumeration is
  cheapest and most independent, not whether one is needed.
- C7. Cross-lane (A): W3's D_series claims to read neither the triangle nor the
  wired P_k. If that survives Lane A, Undertow+D_j moves the pin to cheaper
  cells but the cells are still swept; ab-initio status of D_j does not confer
  ab-initio status on (a_k, b_k).

## Lane B blind findings list — filed 2026-08-20 07:31 EDT, before reading any other lane's output

Sources: the brief's key files plus ns_a40 provenance/rundir log, motley_par.cpp,
cutcount_b1/PROVENANCE.md, and the scripts/ tree. Full workings in
undertow-review-B.md.

| id | lane | status | rank | what |
|---|---|---|---|---|
| B1 | B | CLOSED | 1 | T(40,19) is depth-3 on level 21 (onset n=43). Exactly ONE level-21-bearing cell per row exists at n=41/42: T(41,20) (j=2, sweep H=20@Nmax41) and T(42,21) (j=1, sweep H=21@Nmax42). Nothing else in an n=41/42 run bears on the gap. |
| B2 | B | CLOSED | 1 | No n=41/42 run can close the RULE-INDEPENDENCE gap: every cell it makes is incumbent-rule. It buys VALIDATION only (a holdout equation for level 21). The RI routes are not n=41/42 runs: Motley C_19 (direct enumeration, no D_j, no grand form) or depth 5 + banked Motley H<=18 (tower). |
| B3 | B | CLOSED | 2 | Level 21 today: one pin pair (j=3,4 = T(40,19),T(39,18)), zero cross-checks; T(40,19) is a pinning INPUT, so banked data cannot predict it. Purchasable second equations, each making T(40,19) a genuine holdout: depth 5 (pin 4,5), H=20@41 (pin 2,4), H=21@42 (pin 1,4 — dominated, buys nothing H=20@41 does not). |
| B4 | B | OPEN | 2 | Shared assumption: EVERY tower statement about T(40,19) contains D_3(21); pairs of tower routes also share the grand form and most D_j(21). Mutual agreement of two tower routes is NOT two confirmations. Only agreement against an enumeration (incumbent sweep or Motley C_19) crosses assumption families. |
| B5 | B | CLOSED | 3 | Motley-pinned and incumbent-pinned towers at level 21 pin from the SAME (n,H) cells (j=3,4); once the cells agree the towers are numerically identical. Cross-rule content lives in the cells, not in re-running the tower under the other rule. |
| B6 | B | OPEN | 1 | Motley C_19 RAM is unpriced in every doc that quotes its ~11-15 h wall. Extrapolating measured motley_par H=18 (60 GB RSS, u32 payload, states 72.5M) at the measured x2.96-3.02/height: ~180 GB (u32) / ~110 GB (u16) / ~68 GB (u8) at H=19 vs dalby 125 GB. Feasibility likely survives via narrower primes + more passes; census run decides. JOB REQUEST filed in lane file. |
| B7 | B | OPEN | 2 | Three cited scripts absent from lastditch: dalby_a41_h20.sh (cited "staged" in five-terms-plan.md:134 and a41/PROVENANCE.md:56), dalby_a41_low.sh, nmax_scaling.sh. The 20-30 h / 450 GB H20@41 price is ASSERTED with no inspectable script; extrapolation from MEASURED phase B (9.6 h/48c, 172 GB) x Nmax^3.9 gives ~11 h / ~190 GB — 2-3x cheaper. Unresolved; probably dalby working-tree files. |
| B8 | B | CLOSED | 3 | The "a(42) validation seam" (T(41,22) as P_19's first holdout, ns_a40/PROVENANCE.md Notes) is SUPERSEDED: Undertow's audit already re-derives P_19 from H<=18 and predicts swept T(39,20), T(40,21) as enumeration holdouts. n=42 buys nothing for P_19 any more. |
| B9 | B | CLOSED | 2 | Five-terms interaction: any Nmax>=42 tall sweep produces T(41,20)/T(42,21) as side effects, so level 21's validation comes FREE inside that plan; buying H=20@41 standalone duplicates it. Depth 5 and Motley C_19 sit on the other axis (rule-independence) and no five-terms sweep ever supplies them. |
| B10 | B | OPEN | 2 | depth-5 (`families 21 4`) margin: 103 GB is 9 K-steps of a 1.6x/K RSS ratio from K=12; +5% ratio error compounds past dalby's 125 GB. Stage with K=14 (~15 min) and K=16 (~50 min) measurements first; and D_5 must pass a W3-style gate vs banked depth-5 cells at k<=19 (~15 cells, free) before any use at k=21. |
| B11 | B | CLOSED | 4 | The already-run a41 low sweep re-swept T(40,19) at Nmax 41 (760-cell regression) — a banked same-rule re-derivation at different run config; catches machine/config error only, no rule content. |

Successor rows (different in kind):

| id | lane | status | rank | what |
|---|---|---|---|---|
| B12 | B | OPEN | 1 | JOB (compute, dalby): `motley_par --census 19 40` — exact H=19 state count, prices B6's RAM and fixes the +-20% census band. Decision changed: prime width (u16 vs u8), pass count, and whether Motley C_19 or depth-5 is the cheaper RI route. |
| B13 | B | OPEN | 2 | DESK (gate, red-first): extend severance_w3_gate.py to depth 5 against banked cells k<=19 before D_5 exists at k=21 — the only sub-frontier check D_5 will ever get; refuse the depth-5 route without it. |
| B14 | B | OPEN→A | 2 | CROSS-LANE for A: undertow.md's "~11 h on dalby" Motley H=19 repricing quotes wall only; RAM unstated (B6). Check whether other repricings in undertow.md/five-terms-plan carry the same one-axis pattern. |
| B15 | B | OPEN | 3 | DESK: recover dalby_a41_h20.sh / dalby_a41_low.sh / nmax_scaling.sh from the dalby working tree into the repo (B7); the asserted-vs-extrapolated 2-3x cost gap for H20@41 is decided by whatever the script actually does. |

## Lane A — circularity audit — filed 2026-08-20 (before reading any other lane's output)

Findings (detail and deciding lines in results/undertow-review-A.md):

- A1. Every "match" line `--predict` can print is guaranteed by construction: they are all n=40, k<=19 cells, where banked H>=22 cells are themselves diagCoeffTable injections (ns_a40/PROVENANCE.md "H22-H40 via wired P_k closed forms") and T(40,21) is P_19's own fit anchor. undertow.md's Predict-section flourish about T(40,21) is worth zero; the audit section's re-derivation of the same cell is the real one.
- A2. "Row-40 regression: 21 cells, 0 wrong" decomposes as 1 real check (T(40,20), swept, predicted from H<=19 pins) + 1 fit-anchor identity (T(40,21)) + 19 formula-vs-formula identities (banked H>=22 = injected). Same discount applies where a41/PROVENANCE.md quotes it.
- A3. "--audit: 342 banked cells" = 189 enumerated cells (H<=21) + 153 injected formula cells (H>=22, verified 0 differ from wired law). The 153 witness only that Python and Go evaluate the same polynomial identically. Honest count: 189.
- A4. Of the four-term reassembly table, only a(40) (hcap 19 -> kmax_new 20) exercises an Undertow pin at all; a(39)/a(38)/a(37) have kmax_new <= 19, pin nothing, and are wired-table replays. Their "swept heights <= hcap" framing is broken by wired anchors above the cap (P_19 fit from H=20,21; P_18 from H=19,20): for a(39) the avoided cell T(39,20) re-enters as P_19's own fit datum. Rescued only by composing with --verify's re-derivation, which no single gate enforces.
- A5. Dry-run headline "a(40) comes out of heights 1-19 alone": as coded it uses wired constants fitted to cells up to H=21. True as mathematics via --verify (all wired levels re-derived from H<=19 cells exactly), but that composition lives in a different script invocation.
- A6. In the dry run, "sweep vs banked triangle: 760 cells agree" compares results/ns_a40/perheight against itself (read twice) — vacuous there. In the real a41 run the same check is real: 760 shared cells across Nmax 40/41, 0 disagree (re-verified independently), all real sweeps on both sides (no injection possible at H<=19 for either Maxn).
- A7. Claim 1 (rule-independence): traced every input to ground — Motley C rows (different rule, cpp engine), W1 weights (cpp/severance_w1.cpp + Python DP cross-check), D_j (pure DP / C++ family tables, no sweep reads), grand form (theorem); incumbent triangle and b-file used only as comparison targets. NOT circular. Reproduced rows 19..39 COMPLETE/MATCH + row 40 GAP [19]. Caveat: rows <= 18 crash undertow_ri.py (min() on empty tower band), so the pure-Motley rows are claimed but not attestable by the script as written.
- A8. verify's "N depth pairs, 0 wrong" overstates multiplicity: pairs share cells, so a level with c cells carries c-2 independent checks, ~<=2 per level, not 6-pairs' worth. Conclusion unaffected.
- A9. a(41): no Undertow number depends on itself, directly or transitively (all pinning cells are banked n<=40; forbid_row=41 is moot; n=41 swept cells cannot be injected at H<=19). CLEAN on circularity; the two real weaknesses (level 21 single-pair, D_j extrapolated past validated k<=19 — including the C++ family-table rows k=20..22 having no Python cross-check) are already stated in a41/PROVENANCE.md.
- A10. Wired-table provenance is better than "fitted to tall anchors" for k<=17 (j=1,2 proven; 3..17 have independent holdout certs); the no-holdout levels are exactly 18,19 — and Undertow's verify is currently P_19's ONLY independent cross-check. Worth recording at the k=19 table comment.

Successor rows (different in kind):

- S-A1 [provenance hygiene, cross-lane]: banked perheight files mix enumerated and injected cells with no in-file marker; every future "N cells agree" counter inherits A2/A3-style inflation. Add an injection manifest (or comment lines in h*.out) and make regression counters refuse to count injected cells as enumerations.
- S-A2 [job request seed, for the lead]: depth-5 families run (`families 21 4`, ~16 h / ~103 GB dalby, EXTRAPOLATED from measured emax=4 ladder at K=8..12) is the single run that gives level 21 a second pin pair (T(38,17)) — 0 -> 1 independent checks under a(41) — and, with Motley H<=18 already banked, makes a(40) fully rule-independent without any new sweep. Decision it changes: whether a(41) is quotable as validated and whether T(40,19) needs the ~11 h Motley H=19 run at all.
- S-A3 [tooling]: fix undertow_ri.py rows <= 18 crash so the rule-independence attestation covers its full claimed range in one run.
- S-A4 [dependency freshness]: severance_w3_families_K22_e*.txt rows at k=20..22 rest on the C++ enumerator alone (Python cross-checks stop at K=19); a cheap Python families(22,1)/(22,2) cross-check would ground the exact D_2/D_3 values used at levels 20-21.

## Lane C successor rows — filed 2026-08-20 07:52 EDT (undertow-review-C.md complete)

- C-R1 [JOB REQUEST, to the lead]. Calibrate the excess ladder on dalby:
  build/severance_w3_families families 22 EMAX for EMAX = 4, 5, 6, recording
  wall + peak RSS per step. Wall EXTRAPOLATED ~10-100 s / ~10 min / ~1 h at
  the measured 4.3-7.2x per excess unit (K=8 ladder, undertow-review-C.md §4);
  RAM EXTRAPOLATED from 494 MB at (K19,e3), ASSERTED to track wall ratio;
  cores: the binary threads, 16 fine; disk: MBs. Decision it changes: whether
  depth-8/9 closure — which frees every tower level k <= 21, including
  T(40,19)'s level, from the incumbent sweep using already-banked strip cells
  — is a days-scale dalby job or needs external-memory engineering first. If
  the per-e RAM ratio comes out >= ~7x, e=8 will not fit 125 GB and the spill
  design has to come before any depth-9 talk.
- C-R2 [desk, theory]. Kernel method at excess 1: run the W2 elimination with
  one size-3 marker on the gap walk and test the shared-branch-point
  conjecture (onset-defect-depth1-closed.md:203) one step up.
  results/severance_w3_families_K60_e1.txt is 60 orders of ready-made holdout.
  Different in kind from C-R1: it measures how the ALGEBRAIC route grows in e,
  which decides whether family tables can ever be replaced by desk algebra.
- C-R3 [cross-lane, A]. Route 1's D_j at k = 20, 21 is derivation-extrapolation
  past the k <= 19 validation window. The Motley telescope (C_H to H = 18)
  reaches diagonal-20 cells at heights <= 18, i.e. depths j >= 3: a Motley-side
  check of the depth-3/4 identities AT k = 20 would convert extrapolation to
  validation for the exact regime route 1 leans on. Cheap if the C*.out rows
  cover the needed n; someone should look.
- C-R4 [engineering, strict freedom]. External-memory W1 (sort/merge-spill the
  stack-DP state maps to dalby NVMe, plus the ~2x mirror quotient): buys
  k = 10 at ~1 TB spill (EXTRAPOLATED at the measured 20x/level), k = 11 at
  ~20 TB. Worth exactly two more end-to-end two-source rows and two fewer
  anchored levels; never a route to 21. File under "do if the certification
  map wants rows 25-26, not as tower strategy".

## Lead triage, 2026-08-20 07:45 EDT — C-R1 answered

C-R1 was reshaped (Lane C asked for K=22 EMAX=4,5,6; the first step alone
extrapolates to ~46 h / ~220 GB from the measured K=8/10/12 ladder and does
not fit the box) and run as a per-excess ladder at fixed K=10 on **ayr** —
also replacing Lane C's gympie-run timings.

| emax | wall | RSS | per-e wall | per-e RSS |
|---|---|---|---|---|
| 0 | 0.01 s | 4 MB | - | - |
| 1 | 0.09 s | 4 MB | 9.0x | 1.0x |
| 2 | 0.74 s | 17 MB | 8.2x | 4.1x |
| 3 | 4.92 s | 83 MB | 6.6x | 4.9x |
| 4 | 46.71 s | 480 MB | 9.5x | 6.0x |

**Per-excess RSS costs ~6x and rising.** Lane C's threshold was 7x; the
measured 6x is close enough that the conclusion is the same one:

| id | lane | status | rank | what |
|---|---|---|---|---|
| L-1 | lead | CLOSED | - | **Depths 8-9 (emax 7, 8) are dead by orders of magnitude.** At the measured ~6x/excess, emax=7 at K=21 is 10^4-10^5 GB on any per-K extrapolation in range. Lane C's "useful freedom" route -- pin every level from strip-confirmed H<=14 cells -- does not survive its own cost model. Closed on arithmetic, not on judgement. |
| L-2 | lead | OPEN | 1 | Depth 5 (emax=4 at K=21) is between ~110 GB and ~390 GB depending on which per-K ratio you trust: K=8->10 is 4.18x per +2K, K=10->12 is 2.68x, so the ratio is DECELERATING and the geometric mean over the whole range overestimates the tail. Two more points (K=14, K=16 at emax=4, ~15 and ~50 min) settle it. Until then depth 5 is "marginal", not "16 h / 103 GB" as earlier plans assert. |
| L-3 | lead | OPEN | 2 | Both L-1 and L-2 push the same way, and Lane B's shared-assumption finding (B4/B5) pushes the same way independently: **Motley C_19 is the buy for closing T(40,19)**, being the only route that crosses assumption families rather than adding another statement containing D_3(21). |

## Lane B addendum — filed 2026-08-20 (lead-tasked a(41) recount)

| id | lane | status | rank | what |
|---|---|---|---|---|
| B16 | B | CLOSED | 1 | a(41) independently recomputed (experiments/lane_b_a41_recount.py: anchor-pinned k<=19, no wired table, own code): AGREES = 393811462683918679824582849262105; T(41,21) matches the published prediction. Graded CLEAN second implementation, NOT second source — shares D_j(21) x3 and the pinning cells T(40,19)/T(39,18) with every tower route (B4). All 70 D_j(k<=19) values also re-verified by empirical extraction, 0 wrong. |
| B17 | B | OPEN | 3 | Integrality of below-onset tower cells is a free mod-3^e congruence gate on D_j at the frontier (T(41,20): denominators 3^23 must cancel). Both assemblies assert it implicitly; worth stating in the provenance as the one check D_2(21) currently has. |
