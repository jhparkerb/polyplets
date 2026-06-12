# Polyomino Enumeration: Research Options

*Compiled June 11, 2026. All sequence extents verified against OEIS b-files on this date.*

## Background: where the main sequence stands

[A001168](https://oeis.org/A001168) (fixed polyominoes) is known through **n = 70**. Terms
a(57)–a(70) were computed in one campaign by Gill Barequet and Gil Ben-Shachar
(["Counting Polyominoes, Revisited"](https://doi.org/10.1137/1.9781611977929.10),
ALENEX 2024; journal version in Algorithmica, June 2026 —
[preprint PDF](https://www.researchsquare.com/article/rs-4304962/v1.pdf), local copy:
`papers/counting_polyominoes_revisited.pdf`). Their method is Jensen's transfer-matrix
algorithm (TMA) run on the square lattice **rotated 45°**, which makes signature
pruning dramatically more effective: closing a vertical gap of k cells costs 2k+1
cells on the rotated lattice vs. k+2 on the regular one, so doomed partial
configurations die early.

Cost of the record: **A(70) took ~15,000 CPU-hours (21 months) on a 32-core machine
with 32 GB RAM**. Signature counts grow by less than √2 ≈ 1.41× per term (and the
growth rate is still falling past n = 49). Extrapolating, **a(71) ≈ 20,000 CPU-hours
and ~1.4× the memory** — roughly two weeks on a 64-core machine. The binding
constraint is implementation effort: no public code exists for either Jensen's or
the Barequet–Ben-Shachar algorithm, and the authors list "more terms" as their own
future work, so racing them head-on has both a build cost and scoop risk.

The options below are adjacent problems that have received **much less** attention,
ordered roughly by payoff-per-effort.

---

## Option 1: Close the free-polyomino gap (cheapest win)

**Status:** [A000105](https://oeis.org/A000105) (free polyominoes) is stuck at
**n = 59** while fixed polyominoes are known to n = 70. Eleven terms of one of the
most famous sequences in the OEIS are implied-but-uncomputed.

**Why the gap exists:** Free counts are derived from fixed counts plus the eight
symmetry-class sequences via John Mason's formula
(a(n) = 8·A006749 + 4·A006746 + 4·A006748 + 4·A006747 + 2·A056877 + 2·A056878 +
2·A144553 + A142886). The high-symmetry classes are far ahead (D8-symmetric
[A142886](https://oeis.org/A142886) is at n = 203) because symmetry makes shapes
exponentially rarer. The bottleneck is exactly three low-symmetry classes:

| Sequence | Symmetry class | Known to |
|---|---|---|
| [A006746](https://oeis.org/A006746) | mirror, axis-parallel | n = 60 |
| [A006747](https://oeis.org/A006747) | 180° rotation (C2) | n = 59 |
| [A006748](https://oeis.org/A006748) | mirror, diagonal | n = 66 |
| [A056877](https://oeis.org/A056877) | two orthogonal axes | n = 81 |
| [A056878](https://oeis.org/A056878) | two diagonal axes | n = 87 |
| [A144553](https://oeis.org/A144553) | C4 rotation, chiral | n = 95 |
| [A142886](https://oeis.org/A142886) | full D8 | n = 203 |

(The asymmetric class [A006749](https://oeis.org/A006749) follows by subtraction.)

**What it would take:** Extend A006746, A006747, A006748 from ~60/59/66 to 70. A
symmetric polyomino is determined by (roughly) half of itself, so counting
n-cell symmetric polyominoes costs about what counting (n/2 + const)-cell general
shapes costs — workstation scale, not cluster scale. Approaches: a
symmetry-restricted Redelmeier enumeration, or a TMA whose boundary starts on the
symmetry axis. Toshihiro Shirakawa's October 2025 paper
([arXiv:2510.22446](https://arxiv.org/abs/2510.22446)) is precisely this game — he
pushed the system to n = 59 — so the area is active but at one-person scale.

**Payoff:** b-file extensions to A000105 and one-sided
[A000988](https://oeis.org/A000988) (also stuck at 59) through n = 70.

---

## Option 2: Polyplets / king-connected animals (most neglected)

**Status:** Fixed polyplets [A006770](https://oeis.org/A006770) known only to
**n = 18**; free polyplets [A030222](https://oeis.org/A030222) to **n = 17**.

**Why neglected:** These extents are Redelmeier-era — direct enumeration only.
Nobody has ever pointed a transfer-matrix algorithm at 8-connectivity, even though
nothing about the method fundamentally requires 4-connectivity; the signature
alphabet and transition table just need reworking for diagonal adjacency.

**What it would take:** Port Jensen's TMA (or the rotated variant) with
king-move connectivity in the boundary signatures. Given that the square-lattice
TMA reached n = 56 two decades ago on commodity hardware, an 8-connectivity port
should add **dozens** of terms past n = 18. The pruning analysis would need
redoing (gaps close faster under king moves, so pruning is weaker — growth
constant for polyplets is larger, ~5.9, so terms get big faster).

**Payoff:** Likely the largest number of new terms per unit of effort of any
option here. Physics hook: polyplets are the site animals of the square lattice's
matching lattice, which appears in site-percolation duality arguments.

---

## Option 3: Polyhexes — does the rotation trick generalize?

**Status:** Fixed polyhexes [A001207](https://oeis.org/A001207) known to
**n = 46**, a record from the Jensen era (early 2000s). For contrast, fixed
polyiamonds [A001420](https://oeis.org/A001420) are at n = 75 — the triangular
lattice is *ahead*, not behind.

**The open question:** The Barequet–Ben-Shachar speedup came from re-orienting the
sweep direction relative to the lattice so that pruning bites earlier. Is there an
analogous "good direction" for the hexagonal lattice? Nobody has investigated.
The hexagonal lattice has different natural sweep directions (armchair vs. zigzag,
in nanotube terms) and the connectivity-gap-closing cost differs between them —
exactly the asymmetry the square-lattice trick exploits.

**What it would take:** First a paper-and-pencil analysis of gap-closing costs per
sweep direction, then a TMA implementation. Even *without* a rotation trick, plain
Jensen-style TMA with modern hardware and 20 years of Moore's law should move
n = 46 substantially.

**Payoff:** New terms plus, if the directional analysis pans out, a genuinely new
algorithmic observation worth publishing on its own.

---

## Option 4: Polycubes — 3D has never had its Jensen moment

**Status:** Fixed polycubes [A001931](https://oeis.org/A001931) and free polycubes
[A000162](https://oeis.org/A000162) both known to **n = 22** (community effort,
2023, after the Computerphile video; Stanley Dodds' n = 22 computation).

**The gap:** All known terms come from Redelmeier-style direct enumeration —
counting by generating. The transfer-matrix paradigm, which is *why* 2D is at
n = 70 instead of n = 24, has never been made to work in 3D: the boundary of a
partly-built polycube is a 2D surface, connectivity-on-a-surface has a vastly
richer state space than connectivity-on-a-line (related to counting planar
partitions of surface regions rather than non-crossing partitions / Motzkin
paths), and naïve signature counts explode. Barequet & Ben-Shachar explicitly
name "generalizing the method to three dimensions" as future work.

**What it would take:** A real research project, not an engineering port. Plausible
angles: exploit the fact that pruning (the thing their paper shows matters most)
may tame the surface-state explosion; find the right sweep direction in 3D (body
diagonal = the 3D analog of their 45° trick?); hybrid schemes where the TMA handles
one dimension and direct enumeration handles cross-sections.

**Payoff:** High risk, step-change reward. Even reaching n = 30 would be a landmark.
The growth constant of polycubes (believed ≈ 8.35, rigorous bounds far apart) would
also tighten.

---

## Option 5: Rigorous bounds on Klarner's constant (the theorem option)

**Status:** Everyone "knows" λ = lim A(n)^(1/n) ≈ **4.0625696** (Jensen's estimate,
refined to ±5·10⁻⁷ using the 14 new terms). But the *proven* bounds are only
**4.0025 < λ < 4.5252** — a gap of 0.52 around a value believed to 7 digits.

**Two distinct attacks:**

1. **The monotonicity conjecture (pure math, zero compute).** It is verified
   empirically but unproven that A(n+1)/A(n) is monotone increasing. Madras (1999)
   proved the ratio converges to λ. If monotonicity were proven, every computed
   ratio becomes a rigorous lower bound — instantly, A(70)/A(69) > 4.00512 beats
   the current record lower bound 4.0025, and future terms keep improving it for
   free. The Barequet–Ben-Shachar paper highlights this (Remark 1, §6). Few people
   appear to be working on it.

2. **Twisted cylinders (compute-heavy).** The 4.0025 lower bound
   (Barequet–Rote–Shalah, [CACM 2016](https://doi.org/10.1145/2851485)) came from
   computing the dominant eigenvalue of a transfer matrix on a width-27 twisted
   cylinder — a then-enormous out-of-core computation. Pushing to width 28–30 is a
   memory/IO engineering problem (state counts grow ~3× per width step) that
   essentially one research group touches. Upper-bound improvements
   (Klarner–Rivest-style concatenation arguments, Barequet–Shalah) are similarly
   a one-group area.

**Payoff:** Theorems rather than terms. The monotonicity conjecture in particular
is a clean, statable problem where a proof would convert 20 years of computation
into rigorous bounds.

---

## Option 6: Structural and analytic questions (wide open, low crowding)

- **Non-D-finiteness.** The generating function of A001168 is universally believed
  to be non-D-finite (Guttmann's solvability criteria; numerical evidence from
  series analysis), but there is no proof. A proof technique would likely apply to
  a whole family of unsolved lattice models.
- **Congruences.** Essentially nothing is known about A(n) mod p — no Lucas-style
  congruences, no parity characterization. Even empirical structure-hunting over
  the 70 known terms appears not to have been published.
- **Enumeration by perimeter.** [A391197](https://oeis.org/A391197) (fixed
  polyominoes by perimeter) was only added to the OEIS in 2025. Perimeter- and
  site-perimeter-weighted counts feed directly into percolation series expansions
  (the original 1950s motivation for this entire field). The rotated-lattice TMA
  could be adapted to carry perimeter weights at modest extra cost.
- **Exotic animals.** The long tail is barely touched: polyaboloes
  [A057724](https://oeis.org/A057724) sit at n = 15; similar near-virgin territory
  exists for polysticks, polyominoids, and animals on Archimedean lattices. Any of
  these is a TMA port away from a large extension.

---

## Recommendation summary

| Option | Effort | Compute | Risk | Payoff |
|---|---|---|---|---|
| 1. Free-polyomino gap | weeks | workstation | low | 11 terms of A000105 |
| 2. Polyplets TMA | weeks–months | workstation | low | dozens of terms, untouched area |
| 3. Polyhexes + rotation trick | months | workstation–server | medium | terms + possible new algorithmic idea |
| 4. 3D transfer matrix | open-ended | large | high | landmark if it works |
| 5a. Monotonicity proof | open-ended | none | high | rigorous λ bounds for free |
| 5b. Twisted cylinder width++ | months | very large (TB-scale) | medium | better proven lower bound |
| 6. Structural questions | varies | small | varies | papers, not b-files |

**Maximum result-per-effort:** Option 1 — workstation-scale compute, famous
sequence, clear finish line. **Best untouched territory:** Option 2. **Frontier
with transformative potential:** Option 4. **Cleanest theorem to aim at:** the
monotonicity conjecture in Option 5.

A sensible build order for any of options 1–4: implement Redelmeier first
(n ≈ 24, a weekend, validates everything downstream), then a classic Jensen TMA
(n ≈ 45–50 on a laptop), then the variant the chosen option needs. Every stage
is fully checkable against known OEIS terms.
