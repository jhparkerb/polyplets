# Convex polyplets — SEE docs/proofs/convex-mirage.md (prior, deeper)

Date: 2026-07-10. **Integration correction:** convex polyplets were already
investigated, more thoroughly, in **`docs/proofs/convex-mirage.md`** ("Convex
Mirage"). This note re-derived a subset of that and is retained only for the few
additive pieces below. The primary source is convex-mirage.

## What convex-mirage already established (the real result)

- **Convex polyplet** = HV-convex king animal (every row and column a single
  contiguous run; king-connected). Same object.
- Sequence by area, **38 terms**: 1, 4, 16, 61, 221, 766, 2566, 8390, 26982,
  85834, 271174, 853111, … (via a ROW transfer matrix, state
  `(left-phase, right-phase, width)`).
- Growth **μ ≈ 3.129**.
- **The finding:** convex polyplets by area are **empirically non-D-finite**
  (holdout-validated P-recurrence guesser fails; the convex-polyomino control
  failing is the discriminator). "Convex" is a *perimeter* tractability lever,
  not an *area* one — hence "Mirage."

## What THIS session actually added (the only additive bits)

- An **independent brute-force cross-check** of the first 10 terms
  (`experiments/convex_polyplets.py` here is a Redelmeier-growth + HV-convex
  filter, reproducing A006770 through n=10 and the convex counts 1,4,16,…,85834).
  NOTE: this brute version is inferior to convex-mirage's transfer matrix (it caps
  ~n=10; **it does NOT reach 38 terms** — convex-mirage's "reproduce with
  convex_polyplets.py 38" now needs the transfer-matrix version restored, which
  was lost before this session).
- Sonnet lit/OEIS check: NOT in OEIS; no king convex enumeration in the
  literature (all classical convex work is edge-connected). Classical anchors:
  Bender 2.30914 (convex polyominoes by area), Temperley column-convex 3.2056.
- Framing as a λ lower bound: μ≈3.129 is a valid but WEAK lower bound on
  λ_polyplet (~7.11), far below the banked directed/multi-directed 5.828/6.475
  (results/directed-king-animals.md) — which in turn sit inside the rigorous
  two-sided bracket 5.828 ≤ λ ≤ 9.3153 (upper: ../docs/proofs/polyplet-upper-bound.md).
  So convex is NOT useful as a bound.

## Status

Convex polyplets are a real, novel-to-OEIS sequence but a documented tractability
mirage (non-D-finite by area). If submitted (OEIS Candidate C, deferred), use
convex-mirage's 38 terms + the non-D-finite finding, not this note's 10.
**TODO CLOSED 2026-07-13:** the transfer-matrix tool is restored as
`experiments/convex_tm.py` (row intervals, unimodal-envelope phase automaton,
unique parse); regenerates all 38 terms, first 20 matching convex-mirage's
reference exactly; mu = 3.12894 confirmed. Structural note: the unbounded
interval width is the same mechanism behind the all-pairs cluster family's
non-C-finiteness (results/defect-gas.md, 2026-07-13) -- one phenomenon, two
guises.
