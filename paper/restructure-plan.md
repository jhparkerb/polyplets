# Paper restructure plan — 2026-07-05

The current draft (a19-polyplets.tex) headlines a(19)/a(20). The project now
holds a(34) — sixteen new terms — plus the companion sequences to n=32/33
(34 for one-sided), two engines the paper never mentions, and a new piece of
mathematics (the diagonal quasi-polynomial structure, both triangles). The
restructure puts the strongest results first and makes the confidence tiers
— which now genuinely differ across claims — explicit and structural.

## Proposed title / headline

"Fixed polyplets through a(34): sixteen new terms of OEIS A006770, their
symmetry companions, and the diagonal structure of king-animal triangles."

Abstract leads with a(34) = 515316838423862758858377704 and the count of new
terms, then the companions' reach, then the two structural results (height-
diagonal closed forms P_k with the exp/cumulant law; bbox-diagonal
quasi-polynomials for the symmetric family), then the tiered-verification
statement. The current abstract's framing ("a single 15-digit count from one
program is properly a conjecture") scales up well — keep that voice.

## The organizing device: a confidence-tier table in Section 1

Every numeric claim in the paper gets a tier, stated once in a front table
and referenced throughout. Proposed tiers:

- **T1 dual-algorithm**: two counting methods sharing no logic.
  a(1)..a(19); symmetry counts n<=24 (symtm vs symcount_fast); every
  companion value derived only from T1 inputs.
- **T2 single-algorithm, multiply decorrelated**: one algorithm family,
  confirmed by (i) full chain-reproduction of all prior terms, (ii)
  cross-ISA/compiler recount (ARM vs x86), (iii) held-out diagonal
  closed-form P_k matching the top height cells — a per-term independent
  check that is the strongest thing we have past Redelmeier's reach, and
  (iv) mod-p/CRT internal consistency. a(20)..a(33); a(34) is T2 minus
  (iii) — P_16 has no holdout — and the paper must say so explicitly.
  Symmetry counts 24 < n <= 32 (prefix-validated single engine).
- **T3 conjecture-assisted**: exact computation composed with EMPIRICALLY
  pinned but unproven quasi-polynomial formulas (dmirror P_k: pinned,
  holdout-hit, forward-confirmed on strips computed after pinning — but
  not proved). The n=33 companions (P_4 strips) and, if run, n=34 (P_5).
  These are publishable with the same "computed and validated but not
  proved" label the current paper already uses for scaling claims —
  provided the tier is unmissable.

The tier table is the paper's spine; every results table cites tiers.

## Section skeleton

1. **Introduction** — history, contributions list with forward pointers,
   the tier table. One paragraph on why single-family results can still be
   trusted (the validation architecture is a contribution, not an apology).
2. **Definitions** — as current Section 2 (good), plus bbox/height
   triangles T(n,H) and the symmetric fixed-point counts (D4 setup).
3. **Headline results** — a(1)..a(34) table (split over two columns),
   growth-ratio/lambda estimate REDONE with 34 terms; companions table to
   their reach (A030233 to 34; A030222/34/35, A194596 to 32 or 33). All
   tier-annotated. The current Tables 1-2 are subsets of this.
4. **Methods, as an escalation ladder** (each subsection: idea, why the
   previous method ran out, what it computed):
   a. Redelmeier king enumeration (current SecA) — a(<=19), and the
      explicit oracle for everything else.
   b. Column transfer matrix (current SecB) — a(20)..a(23)-era, byheight
      decomposition, the bijection invariants.
   c. **Kink-carry cell-at-a-time TM with NW carry + spill** (absent from
      the draft entirely) — the a(24)..a(34) engine: cell-at-a-time state,
      carry column, disk-spilled sharded frontier, map/shuffle. One
      diagram. Measured base ~2.5/term.
   d. **Symmetric transfer matrices (Hall of Mirrors)** — fixed-point
      counts at ~sqrt cost: hmirror palindromic columns; r180 half-sweep +
      self-glue with the W>=H transpose restriction; dmirror exact-bbox
      hook sweep (unfolded state) + the Shrink Ray compact frontier;
      strip farming with exact disjoint sums.
   e. **Diagonal closed forms** — height-diagonal P_2..P_15 (exp/cumulant
      recurrence, b_1 = 25, two constants per level, holdout discipline;
      wired into the production sweep so each P_k drops a real sweep
      height); and the NEW bbox-diagonal quasi-polynomials for dmirror
      (period 2, degree k, leading S^k/k!, onset ~2k+2; GF form
      N_k(x)/((1-x)^{k+1}(1+x)^k) with N_k(+-1)=(+-2)^k; the cumulant/exp
      fitter; the falsified two-spine gas and the excursion/segment-grammar
      picture as the structural explanation). This is the paper's
      mathematical novelty — currently 100% absent.
5. **Validation architecture** (promoted, expanded from current
   "Confirmation") — chain-matching, cross-ISA, held-out P_k per-term
   checks (a(33)'s top cell vs held-out P_15 is the flagship example),
   fault injection, sanitizers, the gate suite, divisibility asserts in
   Burnside (/4, /8), and the explicit weakest links: a(34) top cell
   (P_16 unheld), symmetry counts n>24 single-engine, T3 terms.
6. **Companion sequences** — Burnside assembly, the bilateral =(H+D)/2
   double-count proof (keep verbatim, it's nice), full reach tables.
7. **Hole stratification** — extend rows to the current banked reach
   (h19/h20 runs landed; check exact ceiling), M(n) to 16, the diamond
   isoperimetrix argument (keep).
8. **Fixed-height generating functions and rigorous bounds** — as
   current, but the "a(25) lower bound where enumeration is hopeless"
   example is now comic (a(25) is exact); move the bound showcase to
   n>=35 and recompute capture fractions against a(34).
9. **Sampling portrait** — keep at n=19/20 scale (honest about being
   pre-frontier); optionally one sampled a(30)-class specimen if the
   sampler still runs on the new engine (it does not — say so and keep
   the old figures).
10. **Reach and limits** — measured growth per term (cpu ~2.5x, the
    RAM/disk story, Shrink Ray numbers), the polyplet-vs-polyomino reach
    comparison, what a(35) would take (P_16 holdout problem included).
11. **Data/code availability** — update: per-height rows to 34,
    PROVENANCE.md ledgers per term, gates, verify_claims.py (must be
    re-pointed at the new claim set), b-files for all six sequences.
12. **AI note** — update model naming and scope (algorithm design,
    implementation, operations, drafting; author owns decisions and
    correctness), same stance as current.

## What survives nearly verbatim

Definitions; the bilateral double-count proof; hole conventions + Euler
machinery paragraphs; Strang/isoperimetrix argument; GF recovery method
(Berlekamp-Massey + CRT + holdout); fault-injection and sanitizer bullets;
AI note skeleton; bibliography (add: transfer-matrix quasi-polynomial /
Ehrhart references if we cite the GF-basis structure, and the OEIS entries
gain terms).

## Known rot to purge while restructuring

- TODO(a20-confirm) block: resolved long ago (a(20) confirmed by the
  ns-engine chain) — delete, fold into the tier table.
- "absent from OEIS" claims: superseeker-confirmed novel; b-files exist;
  wording should say "submitted/pending" per what jasonp decides.
- Growth-ratio paragraph: lambda estimate from 34 terms, not 20.
- Reach section numbers: superseded by kink-carry measurements.
- verify_claims.py: re-target to the new claim set (it currently verifies
  the a(19)/a(20)-era claims only).

## Open decisions for jasonp

1. **One paper or two?** The dmirror quasi-polynomial structure (+ the
   falsified gas, GF laws, segment grammar) could be a standalone short
   note; folding it in makes this paper long but self-contained. Plan
   above assumes ONE paper; the section-4e/6 material lifts out cleanly
   if split later.
2. **Tier for the companion frontier**: publish n=33 (and n=34 if run)
   as T3 with the label, or hold companions at n=32 (pure T2) and put
   T3 values in an appendix/OEIS-comments only.
3. **a(34) caveat prominence**: tier table + one sentence in the results
   section, or also a line in the abstract.
4. Title wording, and whether A194596 (free non-polyomino) joins the
   headline companions.
