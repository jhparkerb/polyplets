> **NOTE: authored by Claude at jasonp's direction, 2026-08-07.** This is a
> planning document, not a result. It supersedes §2 and §6 of
> `docs/publication.md`; that file's §3 (Proposition 6 / B1), §4
> (the Lean push) and §5 (the N1–N6 novelty sweep) still stand and are not
> restated here.

# The publication split: which papers are jasonp's, which are Claude's

2026-08-07. The earlier plan was cut on a *warrant* axis — jasonp writes all
prose, and results past his vetting ship as statement-plus-citation. This one is
cut on an **authorship** axis: papers whose mathematics jasonp can read and
believe are his to write; papers whose mathematics he cannot vet are written
end to end by Claude and marked as such. Relaxing the old rule moves proofs out
of his papers and into their own, which shrinks his and makes both halves
honest.

## 1. The three categories, and the marking

jasonp's constraint, stated 2026-08-07:

> Under no circumstances will there be any ambiguity about whether a paper is
> wholly my work (none), merely my prose (some) or entirely LLM-authored (some).

**No document is category one.** Every paper carries one of two fixed
disclosure blocks on page 1, verbatim, with no per-paper variation and no
hedging in the body.

- **P — jasonp's prose.** Byline: Jason Parker, alone. The block states that he
  wrote every sentence, that he has read and believes every proof the paper
  states, that he is responsible for correctness, and that the machine did the
  enumeration, formalization, novelty search, tables, figures, LaTeX and
  checking. `paper/technical-report.tex`'s abstract already carries a version of
  this line.
- **L — entirely machine-written.** The block states that the document was
  written end to end by a large language model, exactly how much of it jasonp
  verified (per result, not in aggregate), and what warrants the rest — Lean
  kernel, exact certificate, or labelled measurement.

**On the byline for L-papers.** The Leiden Declaration's "Affirm the humanity of
authorship" clause would forbid naming Claude as author. jasonp's ruling,
2026-08-07: the declaration is an aspiration, not a suicide pact; he is content
either to claim authorship of an L-paper or to disclaim it entirely, provided
the disclosure is precise about how much he was able to verify. The byline is
therefore a per-paper decision, not a policy, and precision about verification
is what carries the honesty — not the author line.

## 2. jasonp's papers (P)

| | paper | contents | pages | his hours | Claude | reach |
|---|---|---|---|---|---|---|
| **P1** | Fixed polyplets through a(40) | a(19)–a(40); the five symmetry companions; hole stratification; the engine; the validation architecture; λ≈7.111 with the Fekete floor 6.2208 and the Madras ratio theorem; log-convexity C2 and the ratio log-concavity theorem | 20–28 | **30–50** | low | **highest** |
| **P2** | Two stratifications of A006770 | T(n,H); his hand-derived T(n,n−1) and T(n,n−2); the defect gas and 25 = 16 + 9; onset and integrality; C(n,c) and the C(n,1) = C(n,n) = A001168 bijection; the universal law *stated*, cited to L1 | 12–16 | 15–25 | low | med-high |
| **P3** | King animals by convexity and directedness | the 5×4 grid; the eight collapse propositions; A018902's first lattice-animal interpretation; the A187077 correction; A222205 to 200 terms and µ = 6.475196280297; 3 + 2√2 reproduced; µ = 3.128943… for the staircase→HV band; the λ bracket *stated*, cited to L3; the five novel sequences as labelled data | 14–20 | 20–30 | low-med | med-high |

**P1 has two drafts and only one is usable.** `paper/polyplets-report.tex` is
1122 lines of complete, trimmed, machine-written prose;
`paper/technical-report.tex` is 331 lines in jasonp's words, roughly 40% built.
Under a three-category scheme with no ambiguity the first cannot be lifted into
the second — sentence-level reuse is exactly the blur being ruled out. Treat
`polyplets-report.tex` as notes and source material. Most of the 30–50 hours is
the engine chapter and §Reproducibility, both still unwritten.

**P2's boundary with P1 is real.** T(n,H) appears in P1 as *method* — the P_k
closed forms are how a(37)–a(40) were composed — and in P2 as *object*: the law,
the mechanism, the arithmetic. Say so in both, once.

**P3's open gate is unchanged.** Proposition 6 is tier-1-eligible but the
reading gate on `results/subclasses.md` Lemmas 2 and 3 is still open. If
jasonp reads them, µ = 3.128943… is his; if he does not, it moves to L5 and P3
cites it.

## 3. Claude's papers (L)

| | paper | contents | pages | Claude sessions | his hours | reach | novelty |
|---|---|---|---|---|---|---|---|
| **L3** | Bounds for λ: 6.543 ≤ λ ≤ 9.3154 | both certificates in full; the strip ladder µ_H; the Collatz–Wielandt rationals; the Lean upper bound | 14–18 | 3–4 | ~2 | **highest of L** | N4 clean — no published upper bound existed |
| **L1** | A diagonal law for row-local lattices | T(H+k,H) = q_k(H)·b^H; the abstract shape engine; square, hex and king instances; the grand form; the polyiamond case where the hypothesis fails and the conclusion survives | 12–16 | 2–3 | ~2 | high | N5 clean; cite the polycube dimension-defect line as precedent |
| **L4** | The by-height GF is not D-finite | the quantified ψ-degree argument; mod-p certificates with preserved degrees; transport to polyominoes, polyhexes, polyiamonds | 12–16 | 3 | ~1 | high | N6 clean |
| **L2** | The mod-3 arithmetic of the height triangle | the spine cubic W³ = W² + t; the base-3 digit-product formula; SNF all 3-powers with ⌈(N−1)/3⌉ nontrivial factors; the 3-adic lift | 10–12 | 2 | ~1 | medium | **UNCHECKED** — N1–N6 never covered it |
| **L5** | Convex king animals | non-D-finite and non-algebraic exclusions at order/degree ≤ 24 on 700 terms; µ to 199 digits; the squeeze in full; subdominant Lemma 4 / Prop 7 / Conjecture 8; the amplitude ratio and the PSLQ negative | 16–22 | 4–5 | ~1 | medium | N1/N2 clean; **N3 is a real collision** (Gouyou-Beauchamps & Leroux) — cite in three places |
| **L6** | Perimeter gradings, king and square | quasi-polynomiality on both lattices with identical leading coefficients through k = 5; the triangular onset at the max end and the linear one at the min; the 4-coloured partition convolution | 10–14 | 3 | ~1 | low-med | **UNCHECKED**, and days old |

Plus the Lean development as a citable Zenodo artifact — not a paper, cited by
P2, P3, L1 and L3.

**The asymmetry is the point.** The P side costs jasonp 65–105 hours and the L
side costs him about eight, because on the L side his only job is reading a
statement and deciding to release it. So L1, L3 and L4 — the three with clean
novelty verdicts, two of which P2 and P3 cite — should run in parallel with his
P1 writing rather than after it.

## 4. OEIS lineup

The softened April-2026 policy still requires a human author responsible for
correctness, %C text in his words, and no AI-sounding prose (A394641 was
rejected for the sound alone). **An entry may cite a P-paper as its warrant,
never an L-paper.**

| OEIS item | backing paper | note |
|---|---|---|
| Wave 1 — A006770 a(19)–a(40); A030233→34; A030222 / A030234 / A030235 / A194596→32 | **P1** | re-run the `oeis/SUBMISSION.md` §5 mechanical audit on A006770 first; a(36)–a(40) postdate it |
| Wave 2 — hole triangle, hole-free column, one-hole column, square bounding box, max distinct holes | **P1** | max hole area cites Sieben and Wang & Wang; claim the enumeration, not the theorem. Square-bbox still owes a Superseeker pass |
| Wave 3A — T(n,H) height triangle | **P2** | %C carries *his* k = 1, 2 closed forms; the universal law is a citation to L1, not a claim in the entry. Superseeker owed |
| Wave 3B — C(n,c) component triangle | **P2** | Superseeker owed |
| Wave 3C — HV-convex king animals by area, 700 terms | **P3** | the non-D-finite %C survives only as a *labelled measurement he ran* — "excluded at order ≤ 24, degree ≤ 24 on 700 terms" — never as L5's theorem |
| A222205 b-file, 23 → 200 terms | **P3** | pure extension, no novelty claim |
| The five comments and corrections — A018902, A187077, A055834, A007052, A225114 | **P3** | highest value per word; all his to vet |
| The five novel Middle Kingdom sequences | **P3** | after the N3 citation fix lands |
| Wave 4 — eight free-polyplet symmetry-class drafts | **P1** | Superseeker owed per class |
| GF orders, atom degrees | **none — do not submit** | their home is L4; already flagged NOT READY in `oeis/README.md` |

**Nothing lands on an L-paper, and no authorship was moved to achieve that.** It
falls out: everything OEIS-facing is data plus elementary structure, which is
the P side by construction. The one item that would have needed an L-paper as
warrant — the atom-degree and GF-order drafts — is the one already flagged
not-ready for independent reasons.

## 5. What has to wait, and for what

Two different kinds of gate. Only one paper is waiting on a machine.

### Gated on compute now running

**L6 is the only compute-gated paper.** All three of today's jobs feed it and
nothing else:

| job | box | feeds | state |
|---|---|---|---|
| `scripts/dalby_square4_deep.sh` (window `j7w17`, PID 2423184) | dalby | the **minimum end** of `results/perimeter.md` — square4 boxes W = 15, 17 at parity 0, rmax = 8; the `1, 4, 18, 60, 187` ladder that diverges from king's `1, 4, 14, 40, 105` | running, 4.6 h in at 17:38 |
| `dalby_perimeter_defect_pool.sh square8 78 6` then `square4 78 6` (window `pdk6big`, stage-1 driver PID 2420612, outer PID 2420610) | dalby | **k = 6** for `results/perimeter.md`, which is currently banked only through k = 5 — the claim "identical degree, period, onset and leading coefficient on both lattices through k = 5" either extends or breaks here | running, 7.5 h in at 17:38; stage 2 (square4) has not started |
| `scripts/ayr_pmin48.sh` (driver PID 2261, tmux `0:pmin48`) | ayr | the **king-lattice** minimum end at p = 48, the partner of the square4 run above | restarted 18:01 EDT on the resumable per-frame driver, after the first attempt lost 3.9 h to a 0-byte all-or-nothing output. Gates and a p=40 reproduction check both green first |

So L6 cannot be written until the k = 6 pool lands on both lattices and both
minimum-end runs finish. Writing it before then risks publishing a k ≤ 5
universality claim that k = 6 contradicts.

**No other paper is waiting on a machine.** P1, P2, P3, L1, L2, L3, L4 and L5
all rest on banked data: the a(40) triangle, the 700-term Middle Kingdom series,
the strip certificates, the ψ-degree certificates and the Lean development are
all complete and validated.

### Gated on reading, not compute

- **P1** — the mod-2 / mod-4 subgroup census landed *today*
  (`results/symmetry-classes.md`, `results/symmetry-classes.md`): a parity bit on all
  820 cells of the a(40) triangle with 0 mismatches, covering every cell of
  mass including the 43.84% band that previously had no second source at all,
  plus a(n) mod 4 confirmed at every n ≤ 40 and a mod-8 cross-check to n ≤ 32.
  That is a material change to the validation chapter, which until today topped
  out at the strip engine's 72.2% cell coverage. Read both notes before writing
  §Reproducibility. `results/growth-constant.md` also landed today
  and belongs in the growth paragraph: µ₁ → 1.0068 against a method calibrated
  to resolve 1%, so the stretched exponential is tested and absent, and the same
  fit returns θ → −0.981 while free to blame one.
- **P3** — `results/subclasses.md` Lemmas 2 and 3 and Proposition 6.
  Reading only; decides whether µ = 3.128943… is P3's or L5's.
- **L2 and L6** — a novelty sweep each, in the N1–N6 style. No compute. N1–N6
  covered the diagonal law, haruspicy, the staircase squeeze, HV-convex king
  animals and the λ upper bound; they never touched the ternary spine, the SNF
  count or the perimeter gradings. Sweep before writing, not after.

### Suggested order

P1 starts now and runs throughout. L1, L3 and L4 in parallel with it. Novelty
sweeps for L2 and L6. Then P2, then P3, then L5, then L2 and L6 if their sweeps
come back clean — L6 additionally behind its three jobs.
