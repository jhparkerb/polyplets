# King anchor — the king schema vs the external A006770 prefix, and the polyhex probe

2026-08-12, wave-5 scout off queue rows ADV3-S2 and ADV3-S1 (successors filed
by the external-anchor scout). Scored under `docs/skeptical-reader-standard.md`,
mapped to phase 1 per the round brief. Scripts:
`experiments/tristruct/r3_kanchor_king_external.py` and
`r3_kanchor_hex_convention.py` (+ `.log` each). Extends
`results/triangle-r3-external-anchor.md`; the gap that file names — no
square-lattice agreement tests the king-specific cross-cut content
`{r-1, r+1}` — is exactly what both rows attack.

## The entry ticket, answered honestly

This is consistency-class work, not a route: it decides king-connectedness
nowhere new, reaches no band cell, and clears neither entry-ticket level *as a
route*. It is the stencil-content complement of the rook external anchor: the
first time the shared schema's KING instantiation meets arithmetic this
project did not produce. The rook run corroborated props 2+3 and the generic
shape of prop 1; only a king-lattice or asymmetric-lattice comparison can
exercise the stencil content itself, and those are rows S2 and S1
respectively. Ranked below every band-reaching candidate, said plainly.

## Disclosure block (mapped to phase 1)

    claim:              (S2) the shared rule schema, king-instantiated
                        (r3_l3_schema_dp.py sweep, byte-identical), reproduces
                        the externally published A006770 prefix; measured GREEN
                        to n=8 today, job filed for n<=13
                        (S1) external per-height polyhex data EXISTS, its
                        height convention is pinned by measurement, and props
                        2+3 transfer to the asymmetric hex stencil
    share of a(40) reached:            0%  (no band cell; the external prefix
                                       ends at n=18, the band is n=40)
    bits against enumeration error:    0   for a(40). The instrument's bits are
                                       against KING-SCHEMA error at small n:
                                       8 exact external row-sum comparisons
                                       today, ~13 after the job
    bits against formula-chain error:  0   conditional on: nothing — no formula
                                       chain is exercised
    rule independence:                 N/A with reason: the king rule itself is
                                       the object under test; reference values
                                       are Redelmeier's 1991 enumeration,
                                       Mertens' 1990 Fortran enumeration,
                                       Myers 2002, Tremblay-Vernay 2024 — none
                                       a frontier DP of this project's lineage
    derivation independence:           full — neither script imports banked
                                       data; the king comparison consumes ONLY
                                       the 18 external terms and its own
                                       arithmetic
    input footprint:                   0 banked cells
    checker:                           r3_kanchor_king_external.py, 6.3 s at
                                       NMAX=8 on gympie, fail-closed; RED =
                                       --red corrupts a COMPARED external term,
                                       run aborts exit 1 (verified);
                                       r3_kanchor_hex_convention.py, 0.1 s at
                                       NMAX=8, fail-closed, --red verified
    sensitivity:                       king RED: corrupt a(NMAX) -> ABORT
                                       (verified at n=7); the standing
                                       cross-lattice RED also binds: the rook
                                       instantiation against these same king
                                       terms fails from n=2 (4 vs 2). Hex RED:
                                       corrupt Table-1 (K=5,n=8) -> ABORT
                                       (verified). False-pass rate of shipped
                                       batteries: 0/3
    prior-work grep:                   git log --all --oneline --name-only --
                                       'results/*.md' 'docs/*.md'
                                       'docs/**/*.md' | grep -iE 'king-anchor|
                                       external.anchor|a006770|polyhex|
                                       hex-anchor|apagodu|tremblay' — one hit
                                       (348a3ba, an unrelated A006770
                                       log-convexity conjecture menu); no prior
                                       schema-vs-external king or hex
                                       comparison on any branch. Working-tree
                                       hex machinery found and reused:
                                       experiments/hex_gas.py adjacency

---

## S2 — the king schema against the external king prefix

### How far the external prefix reaches, per-term, from primary sources

The published A006770 prefix is **18 terms**, and it is the only external
king-lattice arithmetic in existence. Provenance ladder, each rung checked
today against the primary source where held:

| terms | source | verification today |
|---|---|---|
| n ≤ 10 | Peters, Stauffer, Hölters & Loewenich, Z. Phys. B 34 (1979) 399, doi:10.1007/BF01325205 | attribution read from Mertens 1990 ("ref. 11"); paper not held → `papers/MISSING.md` |
| n ≤ 14 | S. Mertens, J. Stat. Phys. 58 (1990) 1095–1108, Table I "nnSquare" (~30 h Fortran, Apollo; `papers/mertens_1990_lattice_animals.pdf`) | Table I read from the held PDF; all 14 terms match the OEIS data; s ≤ 13 additionally perimeter-graded (Table IVB, cross-checked coefficient-level by the second-source branch, one misprint proved Mertens') |
| n ≤ 16 | D. H. Redelmeier, emails to N. J. A. Sloane, 16 Jul 1991 (`oeis.org/A006770/a006770.pdf`) | the scan fetched and read visually today: "polyominoes with square cells where corners (as well as edges) touching count as a connection... fixed counts up to size 16" — all 16 terms match |
| n = 17 | Joseph Myers, OEIS extension line, Sep 26 2002 | OEIS entry record only; method not stated there |
| n = 18 | H. Tremblay & J. Vernay, RAIRO-Theor. Inf. Appl. 58 (2024) Art. 16, p. 13, doi:10.1051/ita/2024013; added to OEIS Dec 2025 | full text 403-paywalled today (publisher + DOI both), no preprint found → `papers/MISSING.md`; the OEIS record and their public code repo (github.com/J-Vernay/discrete-figures, NMAX default 20) verified to exist |

The prefix is genuinely multi-source: n ≤ 14 has at least two fully
independent external computations (Peters-lineage + Mertens; Redelmeier
overlapping both), n = 15..16 rests on Redelmeier alone, n = 17 on Myers
alone, n = 18 on Tremblay-Vernay alone.

### What was measured today (gympie, foreground, seconds-scale)

`r3_kanchor_king_external.py` — the king schema sweep byte-identical to
`r3_l3_schema_dp.py` (stencil `(r-1, r, r+1)`), importing **no banked data**;
row sums Σ_H T(n,H) vs the external terms:

- **n ≤ 8: all 8 external comparisons match** (largest 147,941). 6.3 s.
- RED verified: corrupting a compared external term aborts exit 1.
- Wall factor measured on the king side itself: 1.1 s (n=7) → 6.3 s (n=8),
  **×5.7 per unit n** (rook side was ×5.5; the wider stencil costs ~4%).

This is the first time any schema instantiation has been compared to external
king numbers. Small n, said plainly — but a dropped-NW-class stencil error,
the class ADV-1 measured the structural self-checks blind to, fails this
comparison from n = 2 or 3, so the content of prop 1's king stencil is now
exercised against outside arithmetic, not merely against the project's own
enumerators.

### How far the spec can reach

- **n ≤ 13, all H**: 6.3 s × 5.7⁵ ≈ **10.5 h single-core**. EXTRAPOLATED
  (five compoundings of a two-point measured factor). This is the job below.
- **n = 14**: ≈ 60 h — past what the unmodified Python spec should be asked
  for (same verdict as the rook file at its n=14).
- **n = 18 (the full prefix)**: Python is out (~×5.7⁵ more, ~7 years); a C++
  port runs it in fleet-days (peak state count at (18,18) is
  Motzkin(19)−1 ≈ 6.5e6 label-partitions with count vectors — RAM-trivial,
  wall-bound). EXTRAPOLATED from the ops model, no C++ anchor. Filed as
  successor KANCH-2, not requested now.

Context for what n=13 buys: the project's four-enumerator definition lock
(`results/triangle-hunt-enumerator-crosscheck.md`) covers n ≤ 12 with
project-run counters. The spec-vs-external comparison is different in kind
(external arithmetic, not project arithmetic) at every n, and at n = 13 it
passes the lock's edge — thin, priced honestly, and the reason KANCH-2 (full
prefix to 18, six terms wholly beyond the lock) is the natural successor.

### JOB REQUEST — filed per docs/r3-job-dispatch.md

    job id:            KANCH-JOB-1
    measures:          king-schema row sums sum_H T(n,H) for n <= 13 vs the
                       externally published A006770 prefix (13 comparisons,
                       largest term 1,692,931,066 = Mertens/Redelmeier overlap)
    decides:           whether the king instantiation of the shared schema
                       carries external corroboration of its stencil CONTENT,
                       or fails it. A mismatch => prop 1's king stencil (or
                       props 2/3 as instantiated) is wrong AS STATED at small
                       n, every production engine inherits it, and the
                       harness Part-3 statement re-opens — round-changing.
                       Agreement => the external-anchor pairing is complete
                       (rook = props 2+3 + generic shape, king = stencil
                       content, small n), citable next to ADV3-JOB-1 in the
                       L3-6 package framing.
    command:           python3 experiments/tristruct/r3_kanchor_king_external.py 13
    script:            experiments/tristruct/r3_kanchor_king_external.py
                       (written, GREEN at n<=8, RED verified exit 1)
    wall estimate:     ~10.5 h single-core — EXTRAPOLATED (measured 1.1 s ->
                       6.3 s for NMAX 7 -> 8, x5.7/n, compounded x5)
    RAM estimate:      < 4 GB peak — ASSERTED (peak partition-states at
                       (13,13) ~ Motzkin(14)-1 = 113,633; short count vecs;
                       rook-side precedent <2 GB at its n=14)
    disk estimate:     log file only, < 1 MB
    cores:             1 (serial script; per-H parallelism exists but not
                       worth a rewrite at this wall)
    interruptible:     no checkpoint; on kill, restart loses everything below
                       the last completed H line in the log
    RED control:       --red corrupts a COMPARED external term -> abort
                       (verified exit 1); fail-closed on any mismatch
    closes:            queue row ADV3-S2 (the king-stencil-content gap the
                       rook anchor names in its own NOT ESTABLISHED list)

### What agreement would and would not establish

It tests the stencil CONTENT `{r-1, r+1}` against external arithmetic — the
one thing no square-lattice agreement can do — but only over n ≤ 13 (18 with
the C++ successor), and **the band is not in that range**: n = 40 stays
untouched, 0% share, 0 enumeration bits against a(40). A schema error that
switches on only at large n or large H (none is hypothesised, but the reader
does not grant hypotheses) is not excluded. The definition-level closure for
every n at once remains L3-5's proof; this is its empirical small-n
complement on the king side, as the rook run is on the generic side.

---

## S1 — the polyhex instantiation

### Question 1: does published per-height polyhex data exist? YES — verified

The queue filed this NOT ESTABLISHED; it is now established positively, with
the sources held or cited:

| source | what it holds | extent | provenance |
|---|---|---|---|
| **Apagodu & Chow, "Counting hexagonal lattice animals confined to a strip", arXiv:math/0202295v5 (2009), Table 1** — pulled today, `papers/apagodu_2009_hexagonal_animals_strip.pdf` | rational GFs + series for fixed hexanimals in a strip of height K, K = 1..6, K in **half-hexagon units** (their square-lattice parity-polyomino embedding) | series printed to 8 terms; the **GFs are rational → counts extensible to any cell count n at K ≤ 6**, n = 40 included | Zeilberger's ANIMALS transfer-matrix machinery [Z1] adapted via a hexanimal↔parity-polyomino bijection; Maple packages HexANIMALS/HexaFreeANIMALS published |
| OEIS **A157608** | the same Table-1 array (cumulative counts by strip height), read by antidiagonals | small array (~12 antidiagonals) | J. V. Post 2009 from Apagodu-Chow; Zabolotskiy 2024 formula note |
| OEIS **A059716** + b-file | 1-board (column-convex) hexanimals — the "locally skinny" K-board family the same paper treats | 24 published terms; **order-4 linear recurrence** (6,−10,7,−1), b-file to n=1704 | Klarner 1967 GF lineage; Vöge-Guttmann [GV] |
| Apagodu-Chow p. 12–13 | 2-board hexanimal series (analogue of A001170) | 12 terms | first computed there |
| OEIS **A001207** + b-file | fixed polyhexes, totals — the row-sum control | paper states n ≤ 35 [GV = Vöge & Guttmann, TCS 307 (2003) 433–453]; Kotesovec b-file to n = 46 "from reference by A. J. Guttmann" | external, multiple lineages (Sykes-Glen 1976, Redelmeier 1991 to n=19 — read from the same email scan today — Vöge-Guttmann) |

So the hex probe has the same shape the rook probe had: full-triangle checks
at small n (Table 1 / A157608), **deep tall-narrow runs at fixed height via
the printed rational GFs — external per-height values at n = 40 itself for
K ≤ 6**, and an external row-sum control.

### The convention, pinned by measurement (not read off the paper)

Their height is the height of the square-lattice embedding: each hexagon
covers two half-unit rows and adjacent hex columns shift by one half-unit.
`r3_kanchor_hex_convention.py` brute-enumerates fixed hexanimals under the
project's validated axial adjacency (`experiments/hex_gas.py`:
(x±1,y), (x,y±1), (x−1,y+1), (x+1,y−1)) and tallies by geometric half-unit
height = extent of `2y+x`, +2. **47 comparisons match**: Table-1 columns
K = 2..6 through n = 8 and A001207 row sums; RED (corrupt a Table-1 cell)
aborts exit 1. 0.1 s. The convention is now MEASURED:

    C(K, n) = #{ fixed n-cell hexanimals with max(2y+x) - min(2y+x) + 2 <= K }

with exact-height counts recoverable by first differences in K.

### Question 2: do props 2 and 3 transfer to the hex stencil?

**Prop 2 — YES, verbatim.** The axial hex cross-cut is `{r, r+1}` (new cell
(x,r) meets old column only at rows r and r+1): reach is exactly one column,
which is the property the rook file identified as what prop 2 actually needs.
The asymmetric hex stencil is *inside* the one-column-reach family, so
label-partition sufficiency and stranded-component death transfer unchanged.
A knight-type lattice (two-column reach) remains the family's boundary; hex
does not cross it.

**Prop 3 — connectivity half YES, height half NO.** The one-component
completion predicate transfers (and "no empty column inside the bounding
box" holds — hex adjacency steps columns by ≤ 1). But the height-exactness
accounting does NOT transfer unchanged: the graded quantity (geometric
half-unit height, `2y+x`) is **not the swept row coordinate**, because the
half-unit offset accumulates one step per column. A strip-K instantiation
needs: per-column mask windows shifted by column parity (equivalently, a
window drifting one half-unit per column in axial coordinates), bottom-touch
normalization (which the Table-1 convention requires — verified implicitly by
the 47-comparison match), and first differences in K for exact height. That
is a real design delta beyond a stencil-line swap — more than the rook's
one-line diff, less than a new DP — and it is pinned above so the successor
row can build it without re-deriving the convention.

**Why this matters for the round:** the hex stencil is asymmetric, which is
precisely the error class the round measured its structural checks blind to
three separate times (the `[q^0]`/`A_n(1)` invariants, the symmetric-census
blindness in L4-13's caveat, and the rook anchor's first RED incident). Rook
cannot probe it; hex can. A hex-instantiation agreement would corroborate the
schema's handling of asymmetric cross-cut content against external data —
including at n = 40 for K ≤ 6 via the GFs — while still not testing the king
stencil itself (that is S2's job; the two rows are complements, not
substitutes).

---

## Successor rows (filed in results/triangle-r3-queue.md)

- **KANCH-1** — build the hex-strip instantiation against the pinned
  convention: asymmetric stencil + parity windows + bottom-touch, vs Table-1
  GF expansions at deep n (external per-height values at n = 40, K ≤ 6) and
  A059716/2-board series via mask-run filters. The asymmetric-stencil
  external anchor the whole ADV3 family exists to reach.
- **KANCH-2** — C++ port of the king schema spec to reach the full 18-term
  external prefix: n = 13..18 is six terms of external overlap wholly beyond
  the four-enumerator lock, the strongest small-n stencil-content test short
  of the L3-5 proof.
- **KANCH-3** — cross-lane, half-formed: the project's own hex triangle
  (`hex-diagonal-law.md`, axial row-extent convention) has never been
  externally anchored per-height; a convention converter (axial extent vs
  half-unit extent, both computed by the same brute today) would let
  Apagodu-Chow's GFs anchor it. Also merges naturally with L6-5
  (third-party-code extension of external prefixes; their Maple packages and
  Tremblay-Vernay's C generator are both published code — running either is
  jasonp's call).

## NOT ESTABLISHED

- **Tremblay & Vernay 2024 full text**: 403-paywalled at publisher and DOI
  today, no preprint found; a(18)'s value rests on the OEIS record of their
  p. 13. Logged in `papers/MISSING.md`. What would establish it: library
  access, or running their public generator (NMAX default 20) — jasonp's
  call, per standing third-party-code practice.
- **Peters, Stauffer, Hölters & Loewenich 1979**: not held; n ≤ 10
  attribution is via Mertens' ref. 11. Logged in `papers/MISSING.md`.
- **Myers 2002 method** for a(17): the OEIS extension line is the whole
  record I could reach.
- Whether the ×5.7/n wall factor holds to n = 13 (two-point measurement,
  compounded ×5; the job carries the protocol's 3× headroom).
- **A001207 b-file extent** (n = 46 vs the paper's stated n ≤ 35): Kotesovec
  attributes the b-file to "reference by A. J. Guttmann" without a per-term
  ladder; the hex row-sum control above n = 35 should be treated as
  single-attribution until the Vöge-Guttmann successor lineage is pulled.
- Everything the rook file's NOT ESTABLISHED list already carries
  (Howroyd-independence, A335606 recurrence coefficients) — unchanged here.
