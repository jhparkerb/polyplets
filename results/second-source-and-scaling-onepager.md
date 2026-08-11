# Second-source & scaling — one-pager

2026-08-11. Written at the close of the two-campaign session, after the local
machine OOMed and took the previous session's tmux and ssh-agent with it.

**Branch:** `second-source`, not pushed. Gated (`make gate-cutcount-b1`) and
the suite re-run on ayr; gympie is deliberately untouched.

## The setup that produced it

Two briefs, each fanned to three lanes, then merged:

- **`docs/second-source-team-brief.md`** — lane A enumeration/statistical
  mechanics, lane B model counting/parameterised algorithms, lane C coverage
  map of adjacent literatures. Framed by jasonp's ruling that the strip engine
  does not qualify as verification (same union-find-with-death rule as
  `core/transition.h`), so the bar is a different mechanism for **deciding
  connectivity**, not a different encoding or machine.
- **`docs/scaling-exploration-brief.md`** — same three-lane shape, scored on
  cost *growth* rather than wall time.
- **`docs/second-source-brief-critique.md`** — a critique pass that corrected
  the first brief's repo-state claims before it went out.

Protocol details that mattered: lanes ran concurrently and blind, so
cross-critique ran as a **second wave over the first wave's output**; a claim
counts as "two-source" only when two lanes reached it by different routes, and
double proposals traced to a common repo file (the Sykes–Essam identity, out of
`results/unexplored-avenues.md`) were explicitly discounted to zero evidential
weight. Lane files A/B/C survive as the working record under both merged docs.

The sharpest thing the setup did: lane A attacked B's top candidate,
reimplemented the DP from B's stated rules with independent canonicalization,
matched state counts at every H = 4..10 and `[q¹]` against its own floodfill
brute force beyond B's validation set — **and conceded**, retracting its own
competing claim. Both lanes' first sampled Hankel-rank attempts under-measured
the same way and both recorded it.

**State at filing:** all lanes finished and merged; nothing running locally.
One job live on dalby (B1 per-height): H = 14 landed clean at 10:02 EDT
(1618 s, peak RSS 6.9 GB, `q0_zero=OK q1eval_binomial=OK`), 14/14 heights;
H = 15 running since, 2,624,197 window states, 17.3 GB RSS, ~130 s/column.
The one loose in-flight probe, `results/atoms_ext/q9_verdict.txt`, is
**cancelled** — it reports q_9 unresolved at 2250 terms, and q_9 = 1254 was
banked all along (see correction 8).

## Results, ranked by importance to the project

1. **B1 — a genuinely rule-independent second count of T(n,H), calibrated and
   running.** Colour-symmetrized spin TM over ℤ[q]/(q²); connectivity is never
   decided, only read off the linear coefficient. Moves per-cell
   rule-independent coverage from **0% above n = 22 today** to 45.0% of a(40)
   at H ≤ 14, 66.7% at H ≤ 16 (the running binary), 75.7% at H ≤ 17 after a
   half-day payload change — and flips 4 (then 6) of the 11 kink-only Grand
   anchors to two-source. Carries a self-check the incumbent's blind spot
   cannot survive: A_n(1) = C(HW, n) by Pascal in the same wrapping ring,
   logged per height, fatal on violation. H ≥ 18 closed permanently at
   ~210 GB.
2. **The class floor — an unconditional lower bound on every method in the
   incumbent's class.** Hankel rank of the strip word function, plus Nisan's
   theorem closing the layer-varying escape: no sweep algorithm carrying a
   linear summary over a field beats it. Measured d_H = 6, 17, 35, 88, 204,
   501, 1217 (H = 4..10), two blind implementations agreeing exactly. This
   converts "we could not find a faster method" into "no method of this shape
   exists", a paper-grade statement about the project's ceiling.
3. **THEOREM: the king column TM has exactly Motzkin(H+1) − 1 states** (states
   = nonempty fill + non-crossing partition; crossings die on the 2×2 K₄).
   Verified across three implementations at H = 1..10, reachability
   machine-checked over 3,419 cases. It has been sitting unrecognised in the
   banked strip state series all along. Corollary that reaches the paper:
   **the incumbent's asymptotic base is exactly 3 — the "~2.65×/height" quoted
   in `results/strip-engine.md` is a local ratio near H ≈ 10.**
4. **The coverage census.** 252 cells at n = 23..40, H ≤ 14 carry no
   rule-independent constraint at all, holding 94.8% of a(23) down to 45.0% of
   a(40). This is the number that says what verification work is actually
   worth doing, and it is what B1's tier table is priced against.
5. **External definition anchors delivered.** Mertens 1990 Table IVB: 101 of
   102 king perimeter coefficients match banked data exactly, and the single
   disagreement is provably **his misprint** (his own column sum breaks by
   exactly the delta). Plus OEIS A286139 agreement to n = 9 against Resta's
   `ConnectedGraphQ` brute force — no frontier, no union-find anywhere in it.
6. **pw(P_m ⊠ P_n) = m + 1** (exact DP m = 2..5, m ≤ pw ≤ m+1 proved). The
   kink frontier already sits at the graph's pathwidth, so the geometry axis
   is closed and every remaining candidate must differ on the rule.
7. **The kill lists — 18 second-source directions and 13 scaling directions
   closed with numbers**, several two-source. Most expensive correction: the
   g2 `--siteperim` n = 20 route was priced at 2.6 fleet-hours off the wrong
   kernel; measured on dalby it is **94,000 core-hours**. Dead, do not
   re-propose.
8. **Three record corrections that reach outside the campaign**, two now
   applied: the 2.65 base above (applied to `results/strip-engine.md`); window
   cuts vs column cuts, where conflating them produced two wrong cross-engine
   comparisons in one day (the warning is carried in both canonical files);
   and — found after the merge, by grep — **the campaign's "new" atom degrees
   q_7 = 181, q_8 = 462 were already banked**, along with q_9 = 1254 and
   q_10 = 3289 (`results/anisotropic-not-dfinite.md` and four other files,
   plus the L4 paper). Lane A's coordination note cites the banked sequence;
   lane B marked its measurements "(new)" and the merge adopted that without
   checking. The measurement stands as a cross-method confirmation
   (Berlekamp–Massey mod p vs ψ_H denominator degrees), and the in-flight q_9
   probe is cancelled as redundant.

## Close-out work on the branch (2026-08-11, after the merge)

- **B1 was fail-OPEN and is now fail-closed.** Its banked comparison compared
  whatever it could read: an unreadable or empty banked directory printed
  "0 match, 0 MISMATCH" and exited 0. Both the full and `--assemble` paths now
  exit 3 on a zero-cell comparison and 2 on any mismatch.
- **`gate-cutcount-b1` added and wired into `GATE_TARGETS`** (~7 s): 84 cells
  at H ≤ 6, 400 at H ≤ 10, the per-height self-checks, and the `--assemble`
  path the production run uses — each with a RED control (perturbed cell must
  be caught *and located*, empty banked dir must fail, deleted C_H row must
  abort the assemble instead of leaving a hole).
- **Collateral, not this campaign's:** three strip-mu engines did not build
  under ayr's gcc (-Werror on misleading-indentation and address-of-temporary,
  both clang-silent), and the compile DB did not mirror the fact that
  `cpp/strip_mu.cpp`'s `#pragma omp` directives are inert in the real build.
  Fixed mechanically so the gate suite runs on a box that is not gympie.

## Open, and jasonp's

- **H = 17 payload change** (u128 + 63-bit prime check, half a day) — buys 2
  anchors and 9.1% of a(40). His call once the H = 16 verdict and measured
  H = 15/16 walls land.
- **The floor's growth base** — the evidence leans geometric (≈ 2.79, a real
  opening below 3) but a lean is not a verdict; H = 11 at 7.2 h per x-value is
  the discriminating point.
- **B2 (certified knowledge compilation) declined 2026-08-11** — with it, a
  tier-3 exact-arithmetic certificate has no live mechanism.
- Two 15-minute matching-identity probes are free-rein and unrun.

## Canonical files

- `results/second-source-candidates.md` (+ lanes A/B/C)
- `results/scaling-exploration.md` (+ lanes A/B/C)
- `results/king-column-motzkin.md` — the Motzkin theorem, standalone
- `results/mertens-1990-perimeter-crosscheck.md`
- `cpp/cutcount_b1.cpp`, `scripts/run_cutcount_b1_calib.sh`
