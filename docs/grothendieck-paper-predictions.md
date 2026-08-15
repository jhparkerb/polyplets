# Predictions: arXiv 2608.11195 (Grothendieck-constant AI case study)

2026-08-14, written from the TITLE ONLY — "Long-Horizon AI Research for
Grothendieck Constant: A Case Study in Human–AI Mathematical Collaboration."
The paper has not been fetched or read; jasonp asked for falsifiable
predictions first. Grade each TRUE/FALSE against the paper.

## The mathematics

1. The headline result is a numerical improvement to ONE side of the real
   Grothendieck bracket (1.676… < K_G < 1.7822…), not a closed form, not an
   exact determination, and not the complex constant.
2. The improved side is the UPPER bound: a Krivine/Naor–Braverman-style
   rounding-scheme optimization pushing below 1.78221. (Fallback graded
   half-credit: lower bound above ~1.676 via a Davie-style construction.)
3. The improvement is small — it changes the third significant decimal at
   best; the bracket narrows by less than 10% of its width.
4. The new bound carries a machine-checkable certificate (exact rational or
   interval arithmetic), and the paper treats the certificate, not the
   search, as the result.

## The process (the paper's real subject)

5. Methodology outweighs mathematics: at least twice as many pages on the
   collaboration/verification process as on the proof content.
6. The AI's demonstrated strength is breadth-search over scheme/kernel
   space; the humans own target selection and final verification. The paper
   says this explicitly, in some phrasing.
7. At least one plausible-but-wrong intermediate result is reported as
   caught by the verification layer (not by a human reading alone).
8. The dominant failure class named is goal/target selection or problem
   formulation — not calculation errors in accepted derivations.
9. The workflow converged on adversarial or fail-closed checking of the
   AI's claims — something equivalent to red-first controls on the
   verifier — and the paper presents this as a lesson learned.
10. Dead ends are documented deliberately as contributions (a section or
    appendix of negative results / abandoned routes).

## Meta

11. "Long-horizon" means multi-week-to-multi-month wall clock with
    persistent state across many agent sessions (not one long context).
12. The AI system is an LLM-agent harness (not a bespoke theorem-prover or
    RL system), and at least part of the pipeline is a general-purpose
    coding agent driving computer-algebra or numerical code.

Scoring note: 12 statements; I expect to lose at least two — most likely 2
(the side of the bracket) and 5 (page-ratio is a guess about editing, not
substance).

---

# Scorecard (2026-08-14, after reading; jasonp's pre-committed take:
# sha256 38e79a4e… = ~/Li-et-al, verified)

Ground truth: both sides moved — 6π/11 = 1.7135 ≤ K_G ≤ π/(2log(1+√2)) −
3.47×10⁻⁴; the lower bound is the run's discovery, closed-form, and the
first that constructs no hard instance (failed upper-bound schemes →
universal affine obstruction b₃ ≥ 2b₁ − 11/6 on Hermite coefficients →
dualized through Naor–Regev). Tenths digit of K_G pinned at 7.

 1. FALSE twice — both sides, and the lower bound is a closed form.
 2. HALF — upper bound is Krivine-style (limiting schemes) but predates
    the run; the run's headline is the lower bound.
 3. FALSE — bracket narrowed ~35%, not <10%; lower bound moved 0.037.
 4. TRUE — Arb + interval arithmetic certificates; their bar is stricter
    still (system-tested ≠ theorem until human-verified).
 5. TRUE — methodology dominates; math exposition ~4 pages of ~12 + appendix.
 6. TRUE, nearly verbatim: "exceptionally strong at technical execution,
    substantially less reliable at research judgement and research-state
    representation."
 7. TRUE — session-44 upper bound withdrawn by machine testing.
 8. HALF — target selection is one named failure class (six escapes fail
    identically, run opens a seventh); the second, research-state
    representation (caveats lost in iterated rewriting; a criterion proved
    in session 8, lost in a handoff, reproved 25 days later), I failed to
    predict despite living the countermeasure.
 9. HALF — internal verification protocol + adversarial review, yes;
    red-first controls specifically, not stated. Wager lost.
10. TRUE, understated — the dead ends became the theorem itself.
11. TRUE — 39 days, ~240 sessions, file-based memory, session reports.
12. TRUE — GPT-5.5/5.6-Pro reasoning + Claude Code (Opus, later Fable 5)
    as the coding agent.

Net ≈ 7/12 with both self-declared expected losses mispicked: #5 held;
the real misses (#1, #3) were underestimating the mathematics. The process
predictions were cheap — the paper's harness (bulletin ≈ operator
directives, session report ≈ HANDOFF.md, state-compression decay ≈ the
reason for receipt gates) converged on practices this repo already runs.
