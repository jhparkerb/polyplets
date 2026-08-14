# Coin Lift — ensemble goal document

Plan: `docs/coin-lift-plan.md`. Probe:
`experiments/tristruct/r3_inv_rank_probe.py`.

## Recommendation, stated first

**Do not convene an ensemble yet.** Gates G1 and G2 together cost under a day
of one executor's time, and between them they price the entire program: G1
asks whether the char-2 collapse survives past H = 9, G2 asks whether it
survives to Z/4 at all. Both are small, exact, self-checking computations on
matrices of dimension <= 229 (G2) and <= ~40,000 (G1). An ensemble adds
nothing to a Smith normal form.

**Convene one for G3, and only if G1 and G2 both pass.** G3 — finding a
combinatorial description of the compressed basis that does not come from
projecting the incumbent's automaton — is genuine open-ended search over a
literature (CKN, BCKN, Kluk-Nederlof) plus a structure hunt over extracted
bases. That is ensemble-shaped work: independent lanes, adversarial kill,
diverse lenses on the same object.

## The goal

Determine whether the characteristic-2 rank collapse of the strip-counting
functional can be turned into a **deterministic, rule-independent** check on
the cells Motley cannot sweep — and if so, how many bits per cell.

Done means one of: (a) a construction with an explicit basis, explicit
transitions, priced at H = 20-22, validated against banked T(n,H) mod 2^k for
H <= 16; or (b) a documented negative naming which gate failed and why.

## What is already excluded — do not re-derive

**Exact values at char-2 dimension are impossible.** A Z/2^k realization of
bounded dimension for all k yields a Z_2-, hence Q-, realization, and
rank_Q >= rank_{F_p} for every p; the measured mod-p rank extrapolates to
~2.3e7 at H = 21 against a char-2 dimension of 9.2e5. The floor is 25x the
collapse. `docs/coin-lift-plan.md` §1 carries the argument. Any lane that
proposes megabyte-scale exact counting has not read it.

The live ceiling is **two or three deterministic bits per cell** (Z/4, Z/8),
which the limit argument does not touch.

## Kill conditions, in order

1. **G1**: rank departs from 0.44 x 2^H by H = 12 — especially if it turns
   toward the mod-p 2.45x/height curve. Program ends.
2. **G2**: Z/4 free rank jumps toward the mod-p curve. Coin Lift ends; Coin
   Flip, Coin Roll and Biased Coin Flip survive as one-bit and probabilistic
   instruments.
3. **G3**: no describable basis by H = 12. The realization can then only be
   obtained by projecting the incumbent's automaton, which **inherits the
   incumbent's rule and certifies nothing**. Program ends.
4. **G4**: compressed transitions dense with no factorisation. At 2^H x D^2
   per column that is 1.8e18 at H = 21. Program ends.

## Lanes, for G3 only

| lane | scope |
|---|---|
| **LIT** | CKN15, BCKN15, Kluk-Nederlof 2025, Nederlof's cut-and-count line: is the explicit GF(2) basis for connectivity already constructive, and at what dimension? Does anything in the literature lift past char 2? |
| **EXT** | extract explicit bases at H = 6..11 from the observability closure; publish them as data for the other lanes |
| **STRUCT** | find an index set for EXT's bases — subsets, parity classes, matchings-like objects — guess the general form, test at H = 12 |
| **INDEP** | adversarial: for any proposed basis, decide whether its derivation is independent of the incumbent's automaton or a projection of it. This lane has veto power |
| **DENSITY** | price G4 against whatever STRUCT produces, at H = 10-12 |

INDEP is the lane that matters most and the one an ensemble is worst at
staffing honestly, because every other lane is incentivised to declare
success. Give it the seed-list treatment: it scores the others, it does not
propose.

## Standing constraints

- Every rank and every basis is exact arithmetic. No floating point, no
  sampling.
- The probe's RED control (corrupted stencil must miscount against brute
  force) rides along with every extension; a lane that extends the probe
  without carrying the RED forward has not extended the probe.
- Quote the measured ladder, not the extrapolation, whenever both exist.
- Nothing in this program touches Motley or the incumbent. It is a third
  mechanism or it is nothing.
