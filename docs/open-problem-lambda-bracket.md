# Open problem (for jasonp): break the connectivity wall on λ's upper bound

2026-07-11. A framed collaboration target — genuinely hard, and the bottleneck is
mathematical insight, not compute. Everything below the "what's needed" line is
settled; the question is a new idea.

## State of the rigorous bracket

| | value | nature |
|---|---|---|
| lower (exact) | λ ≥ 3+2√2 ≈ **5.828** | directed king animals, closed form |
| lower (num.) | λ ≥ **6.475** | multi-directed (Bacher), numerical |
| lower ladder | μ_H ↗ λ, μ₁₃ = 6.306 | exact strip growth constants, → λ from below (compute-limited: μ_H≈6.6 needs H≈18–20) |
| **estimate** | λ ≈ **7.110(1)** | ratio + confluent fit + **independent differential approximants** (this session) + μ_H extrapolation — four methods agree |
| upper | λ ≤ **9.3153** | Bui finite-type convolution certificate, exact rational (paper headline) |
| upper (crude) | λ ≤ 12.2 | Eden/twig `C(5n,n)` |

The estimate 7.110 is nailed. The **rigorous bracket [5.83, 9.32] is embarrassingly
wide around it**, and the upper half is where it's stuck.

## Why the upper bound is stuck — a PROVEN barrier, not a tuning failure

The state-of-the-art upper-bound methods (Klarner–Rivest L-context, Barequet–Shalah
cut hierarchy, Bui convolution certificates) are all **finite-type**: they encode an
animal by a local BFS "twig" alphabet within a window of radius R and over-count the
formal sequences. The king machinery is fully built and validated (`experiments/
king_bound_R.py`, `king_certificate.py`; R=1→13.0, R=3→9.315), and larger R is a valid
tighter over-count by construction.

But the P2 slack audit (`experiments/king_slack.py`, `docs/certificate-squeeze-plan.md`)
measured *where the 9.315 over-count lives* and found it is:
- **diffuse** — median slack 1.14, no single type worse than 1.22 (not a fixable hot spot);
- **compounding — slack grows +0.022 per cell, i.e. with n**; and the anchor type's
  growth is asymptotically clean (= λ).

Slack that grows with n is the signature of a **non-local** over-count: the formal
twig sequences the certificate admits include configurations whose *distant* parts
fail to connect / overlap-collide, and that failure is invisible to any finite window.
**No finite context R, no multi-cell casing (measured — only relocates the slack) can
see a non-local constraint.** So this whole method class floors strictly above λ. This
is a real barrier, and arguably a publishable observation in its own right: *finite-type
convolution bounds cannot reach λ for the king lattice.*

The dual asymmetry is telling: the μ_H strip ladder is EXACT (it enforces full
connectivity, but only within a bounded height) and converges to λ from *below*; the
twig method has UNBOUNDED extent but RELAXED connectivity and floors from *above*.
**Connectivity + unbounded extent is exactly what neither side achieves** — that's the
wall, on both faces.

## What's needed (the hard part — your input)

A rigorous upper bound → λ needs a method **outside the finite-type class** that
captures non-local connectivity while staying computable. Candidate directions, with
my read; the decision of which (if any) to chance is where a mathematician's judgment
is the lever:

1. **Strip-decomposition + tail bound.** Cut an animal into horizontal strips of height
   H; each piece grows ≤ μ_H, and pieces join vertically. If the *vertical-join
   multiplicity* per column can be bounded by a factor c(H) with μ_H·c(H) ↓ λ as H→∞,
   that's an upper bound converging to λ. The join factor is the crux — it is where the
   Klarner–Rivest "analytic height control" would go, ported to king seams. **My read:**
   most promising, but the join multiplicity may itself be non-local (a tall bridge
   between strips) — needs your eye on whether the vertical interface is boundable.
2. **Connectivity-witnessed certificate.** Augment the convolution system with a term
   that charges for maintaining a spanning connection — a non-local decoration made
   local by a potential/flow argument. **My read:** speculative; unclear if it stays a
   valid over-count.
3. **A different invariant.** Bound λ via perimeter/interface entropy or a
   cluster-expansion / Ruelle-type bound rather than direct enumeration. **My read:**
   least explored here, possibly the cleanest if a known animal bound ports.
4. **Accept the asymmetry.** Push μ_H to H≈18–20 (compute) for a ~6.6–7.0 rigorous
   lower bound, keep 9.32 upper, and rest on the four-method estimate 7.110. **My read:**
   the honest fallback; the bracket stays wide but the estimate is unimpeachable.

## The questions for you

- Is (1) real? Can the vertical join between height-H strips be bounded by a local
  factor, or is a tall bridge genuinely non-local (killing it the same way)?
- Do you know an animal upper-bound technique that is *not* finite-type convolution —
  anything that has beaten a connectivity wall for polyominoes/polyhexes?
- Strategic: is a tighter rigorous *upper* bound worth a real research push for the
  paper, or is [5.83, 9.32] + the pinned estimate 7.110 the right place to stop?

Machinery ready to test any concrete alphabet/system: `experiments/certificate_bound.py`
(exact rational certificate checker), `kernel_system.py`, `king_bound_R.py`. Any
candidate is sanity-gated against the rook analog and must stay above μ₁₃=6.306 and the
observed a(n) ratios ≈ 6.9.
