# The hole-free growth constant λ₀: simple-connectivity is exponentially costly

2026-07-11 (research during the a(22) fleet run). `experiments/holefree_growth.py`
on the banked hole distribution `results/holes_n18.txt` (n≤18, exact).

> Provenance correction (2026-07-31): this line previously read "g2 `--holes`".
> The commit that banked the table (`8e41a63`) records it as
> `tma_holes square8 18 --holes` on ayr (x86/GCC, 44 h single-core), i.e. the
> production TM holes engine, *not* g2. `results/holes_n18.dalby.txt` is a
> byte-identical cross-ISA reproduction on dalby. `tma_holes` is itself
> cross-checked against `g2 --holes` at small n by `tests/gate_holes.py` and
> `tests/gate_g2.py`, but the n=18 table is single-engine.

## Question

The height/diagonal structure of the triangle is well mapped, and polyplets are
confirmed to sit in the 2D lattice-animal universality class (extent exponent
ν≈0.64, [[nu-exponent]]; growth θ≈−1). Open, unanalysed here: does the **hole-free**
(simply-connected) sub-class A₀(n) share the full growth constant λ≈7.11, or grow
strictly slower? I.e. is a hole a *polynomially* rare accident or an *exponential*
entropic gain? `polyplet-zoo.md` only noted the fraction at a single n (73.4% at 18).

## Result — λ₀ < λ, hole-free fraction decays purely exponentially

From A₀(n) (holes=0), A₁(n) (one hole), and a(n)=ΣA_k, n≤18:

| quantity | growth constant | θ (finite-size) | method |
|---|---|---|---|
| a(n) total | **λ ≈ 7.096** | −0.93 (→ universal −1) | Domb-Sykes + Richardson + log-linear fit |
| A₀(n) hole-free | **λ₀ ≈ 6.94** | −0.93 (same) | same |
| gap λ − λ₀ | **≈ 0.157** | | |

Two independent, mutually confirming facts make λ₀ < λ robust despite n≤18:

1. **The hole-free fraction A₀/a decays as a clean geometric ρⁿ.** log(A₀/a) vs n
   is linear to 5 decimals (second difference ≈ 1×10⁻⁵ across n=12..18), slope
   −0.0222/cell → **ρ = 0.9779 per cell**. A shared growth constant would give a
   *sub-exponential* (polynomial) fraction; the fit is unambiguously exponential.
2. **ρ equals λ₀/λ.** Measured per-cell fraction decay 0.97800 vs the fitted
   λ₀/λ = 0.97789 — agreement to four decimals. So the two constants and the
   fraction decay are one consistent picture: **A₀ ~ λ₀ⁿ, a ~ λⁿ, A₀/a ~ (λ₀/λ)ⁿ.**

The **ratio λ₀/λ = 0.978 is pinned** by (1) even though the absolute λ, λ₀ carry
finite-size uncertainty (~±0.02 at n≤18): whatever the true λ, the hole-free class
runs a constant factor 0.978 per cell behind it.

## Addendum 2026-07-31 — the n=19 term (TIER-DEGRADED input)

A complete but never-banked n=19 per-height holes run was recovered from rescued
dalby telemetry and assembled into **`results/holes_n19.txt`**. New terms:

- a(19) = 151 609 203 011 580 (matches `results/triangle.txt` row sum)
- **A₀(19) = 108 898 235 427 176**, A₁(19) = 35 127 667 632 232; max 11 holes
- hole-free fraction 0.7183 (was 0.7344 at n=18)

**Tier caveat — read `results/holes_n19.txt`'s header before citing.** Every log in
that run carries binary stamp `git=2c5e3e7-dirty`, which `docs/job-checklist.md`
item 4 bars from first-class banking: the exact source is not recoverable. What it
does have is strong corroboration — all 95 cells with n≤18 agree *exactly* with the
independently-produced `results/holes_n18.txt` (whole-run invocation on ayr,
reproduced cross-ISA on dalby), all 55 cells with n≤14 agree with the independent
flood oracle `results/holes_n14.txt`, and row sums equal a(n) for every n≤19. That
is a same-engine consistency check across a different decomposition, threading and
ISA, plus a genuinely independent oracle up to n=14 — not an independent-engine
check at n=19. **Treat the n=19 row as provisional.**

Rerunning `experiments/holefree_growth.py` with and without the new term:

| quantity | n≤18 (banked control) | n≤19 (incl. degraded term) | Δ |
|---|---|---|---|
| λ | 7.0958 | 7.0974 | +0.0016 |
| λ₀ | **6.9389** | **6.9411** | +0.0022 |
| gap λ − λ₀ | 0.1569 | 0.1563 | −0.0006 |
| ratio λ₀/λ | 0.97789 | 0.97798 | +0.00009 |
| θ (both classes) | −0.93 | −0.94 | −0.01 |
| measured fraction decay ρ | 0.97800 (17→18) | **0.97801** (18→19) | +0.00001 |

The n≤18 control reproduces the banked numbers to every printed digit, so the
comparison is like-for-like.

**Gap-constancy test.** The gap moved by −0.0006 (0.4%) and the ratio by +9×10⁻⁵
(0.009%) on adding a term — i.e. the gap is constant to within the finite-size drift
of λ itself, and the *ratio* is the stabler of the two, as claimed above. The
pure-exponential test also holds: the second differences of log(A₀/a) continue their
slow, monotone drift at the 10⁻⁵ level (n=17: +3×10⁻⁶, n=18: +6×10⁻⁶,
n=19: +8×10⁻⁶) — still flat to 5 decimals, no sign of curvature. And ρ measured at
18→19 (0.97801) still matches the fitted λ₀/λ (0.97798) to four decimals.

**Conclusion: n=19 changes nothing qualitatively.** It nudges λ₀ up by 0.002 —
inside the stated ±0.02 — and tightens confidence that λ₀ < λ with a constant ratio.
The quotable outputs are unchanged: λ₀ ≈ 6.94, ρ = λ₀/λ ≈ 0.978.

## Reading

- **Simple-connectivity is exponentially costly: ~2.2% of the per-cell entropy.**
  Almost every large polyplet has a hole; the hole-free ones are suppressed by
  (0.978)ⁿ, not by a mere power of n. Being simply-connected forbids a positive
  density of local configurations, and that ban compounds multiplicatively.
- **Same correction exponent θ ≈ −0.93 for both classes** — hole-free polyplets sit
  in the same universality class (same θ→−1), differing only in the non-universal
  growth constant. Clean separation of universal (θ, ν) from non-universal (λ, λ₀).
- **Holes are extensive.** Mean hole count per cell climbs monotonically
  (0.0132 → 0.0160 → 0.0176 at n=10/14/18), heading to a positive constant: a
  typical large polyplet has ~c·n holes (the lattice-animal pattern-theorem picture).
  The one- and two-hole classes A₁, A₂ approach λ from finite-size (their individual
  constants are not pinnable at n≤18; A₁'s ratio is still descending through 7.08).

## Caveats

- n≤18 is short for a growth constant. **λ₀ ≈ 6.94 is ±~0.02**; the *ratio* λ₀/λ =
  0.978 and the *exponential* nature are the robust, quotable outputs, not the third
  digit of λ₀. A handful more terms would tighten λ₀ and test whether the gap is
  exactly constant — but **more terms are not cheap**; see the measured cost model
  below. (This bullet previously read "production TM `--holes` to n≈22, cheap";
  that estimate was never measured and is false.)

## Measured cost of more terms (2026-07-31)

From the rescued per-height run logs
`results/dalby-run-telemetry-202606/holes_n{16,17,18,19}_ph/h*.log`
(`event=done wall_s=…`, dalby, `tma_holes … --holes --per-height`), summed over
all heights of each run:

| n | Σ per-height wall | worst single height (critical path) | ratio vs n−1 |
|---|---|---|---|
| 16 | 2 490 s (0.7 h) | h16 = 950 s | — |
| 17 | 12 511 s (3.5 h) | h17 = 4 524 s | ×5.02 |
| 18 | 52 334 s (14.5 h) | h18 = 17 204 s | ×4.18 |
| 19 | 220 828 s (61.3 h) | **h19 = 77 818 s (21.6 h)** | ×4.22 |

The n=19 run also cost 201 CPU-hours (`cpu_s` summed, `threads=8`). The scaling is
a steady **×4.2 per term**, and the top height dominates: at n=19 one height is
21.6 h of wall on its own, so even with all heights running in parallel the
critical path is a day.

Extrapolating ×4.2 from the n=19 baseline:

| target | Σ per-height wall (est.) | worst height = critical path (est.) |
|---|---|---|
| n=19 (measured) | 61 h ≈ 2.6 days | 21.6 h |
| n=20 | ~258 h ≈ 11 days | ~3.8 days |
| n=21 | ~1 080 h ≈ 45 days | ~16 days |
| n=22 | ~4 550 h ≈ 190 days | ~67 days |

(The critical-path column is the floor only if every height runs concurrently,
which at n=22 means ~22 simultaneous 8-thread jobs — well past dalby's core
budget, so real wall would land between the two columns.)

So "n≈22, cheap" is off by orders of magnitude: **n=20 alone is a multi-day dalby
campaign and n=22 is a multi-month one.** Decision deferred to jasonp — this is a
substantial resource commitment, not a spare-cycles run.
- This is the polyplet analogue of the (believed) polyomino behaviour that
  simply-connected polyominoes grow strictly slower than λ≈4.06; not claiming the
  polyomino literature here, only measuring it directly for king animals.

## Novelty / provenance

Not previously computed in-project: `polyplet-zoo.md` reported only the n=18 fraction
snapshot ("falling as n grows"); no growth-constant. Complements the diagonal closed
forms (height structure) and [[nu-exponent]] (extent) with a **topological**
growth-constant. Data `results/holes_n18.txt`; script `experiments/holefree_growth.py`.
