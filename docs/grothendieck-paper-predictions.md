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
