# R1-C — rook Hankel ranks at small H

2026-08-13, gympie, scout lane of `docs/rook1-brief.md`. Probe:
`experiments/rook1/rook1_R1-C_rank_probe.py` + `.log` (final run MAXH=9,
~45 s wall foreground; smoke run at MAXH=6 in `.smoke.log`). Pure Python,
exact arithmetic; automaton adapted from
`experiments/tristruct/r3_inv_rank_probe.py` by parameterizing the
cross-column stencil (king `(-1,0,1)` → rook `(0,)`) — a throwaway
observability probe, not the out-of-scope rook transfer-matrix engine; the
stencil swap itself was already externally validated in
`experiments/tristruct/r3_adv3_rook_schema.py` against A292357/A001168.

## Verdict in one line

**Rook does NOT show the char-2 crack — its GF(2) Hankel rank is essentially
full (77–100% of states at H = 4..9, growth ~2.42×/height, no 2^H law) and
its mod-p rank is exactly full at every measured H — so the king collapse is
a king-stencil-specific structure, not a property of the straight-cut
connectivity vocabulary; the specific king decision this changes: the INV-4
explicit-basis hunt (`results/triangle-r3-involution.md` §NOT ESTABLISHED,
the conditional T(40,21)-mod-2-in-laptop-hours route) loses its CKN-precedent
justification and must be re-priored as a king-specific anomaly hunt, not a
transfer of a known constructive theorem.**

## Measured ranks (observability closure = exact Hankel rank; deterministic
automaton, same construction and rank code as the king probe)

| lattice | H | states | rank GF(2), x=1 | rank GF(2^16), graded, 2 random t | rank mod p=32749 |
|---|---|---|---|---|---|
| king | 4 | 20 | 6 | 6, 6 | 6 |
| king | 5 | 50 | 15 | 15, 15 | 17 |
| king | 6 | 126 | 27 | 27, 27 | 35 |
| king | 7 | 322 | 58 | 58, 58 | 88 |
| king | 8 | 834 | 112 | — | 204 |
| king | 9 | 2187 | 229 | — | not run |
| rook | 4 | 20 | 20 | 20, 20 | 20 |
| rook | 5 | 50 | 49 | 49, 49 | 50 |
| rook | 6 | 126 | 119 | 119, 119 | 126 |
| rook | 7 | 322 | 288 | 288, 288 | 322 |
| rook | 8 | 834 | 696 | — | not run (cost) |
| rook | 9 | 2187 | 1681 | — | not run (cost) |

Log for every number above: `experiments/rook1/rook1_R1-C_rank_probe.log`.

The two signatures, side by side:

- **King (banked, reproduced here):** GF(2) rank tracks 0.375–0.45 · 2^H
  (growth locked at ~2.0×/height) under mod-p growth 2.06–2.83×/height. The
  CKN-style char-2 collapse.
- **Rook (new):** GF(2) rank / states = 100%, 98%, 94.4%, 89.4%, 83.5%,
  76.9% at H = 4..9; GF(2) growth 2.45, 2.43, 2.42, 2.417, 2.415 —
  flat at ~2.42×/height against state growth 2.5–2.62×/height. Mod-p rank
  equals the state count exactly at every H measured (4..7). No 2^H law, no
  characteristic-2 anything: at H = 9 the rook GF(2) rank is 1681 where a
  0.44·2^H law would give 229 (the king value).
- Grading is free in char 2 on both lattices (GF(2^16) graded rank = ungraded
  GF(2) rank at all six measured points per lattice, H ≤ 7).
- Byproduct: the rook and king state censuses are identical at every
  H ≤ 9 (Motzkin(H+1)−1 = 20, 50, 126, 322, 834, 2187), extending gate 1's
  "identical state sets at H ≤ 8" note (`docs/rook-parity.md:120`) one
  height. Identical spaces, different transitions — which is exactly why the
  rank measurement is informative and why symmetric gate-1 checks are not.

## Verification chain (all fail-closed asserts in the probe; log as above)

- **Rank-code regression:** the king GF(2) ranks must equal the banked table
  (`results/triangle-r3-involution.md` §2: 6, 15, 27, 58, 112, 229) and the
  king mod-p ranks must equal A-S1's (6, 17, 35, 88, 204) before any rook
  number is read. They do — the rank routines are regressed against known
  outputs, including a two-prime spot check (p = 32749 vs p = 2³¹−1 agree at
  H ≤ 6).
- **Ground truth:** fixed polyominoes a(n), n ≤ 8, assembled end-to-end from
  the rook automaton (grading + exact-height second difference over H ≤ 8)
  equal A001168 equal `build/g2 square8 8 --rook-bishop`, run and parsed in
  the probe (the charter's named ground-truth source,
  `cpp/g2_redelmeier.cpp:84-93`).
- **Semantics:** automaton word counts vs brute-force rook-connected
  enumeration at (H,W) = (2,3), (3,3), (3,4).
- **RED A (planted wrong stencil):** the king stencil fed to the rook brute
  check must miscount, and does.
- **RED B (planted corrupt input):** one killed reachable transition (the
  row-0 bar transition) breaks the word-count regression that guards the same
  delta the rank code consumes, and does.

## Collateral finding: anchored defects are invisible to the A001168 tie

The RED-B defect, planted instead against the assembled-a(n) gate, **cancels
exactly**: a bottom-anchored transition kill removes the same configurations
from N_H and N_{H−1}, and the exact-height second-difference telescope
subtracts them away — the corrupted engine still reproduces A001168 for all
n ≤ 8 (demonstrated in the log, "observation: same defect vs A001168 tie ->
CANCELS"). An end-to-end tie against banked values can pass a broken engine
for a whole defect class. Directly relevant to gate 1's mandatory asymmetric
RED control (`docs/rook-parity.md:117-120`): the planted-defect battery
should include an anchored-transition kill, not only the NW-stencil drop.
Filed as queue row C4.

## The king decision, named (the charter's required clause)

**The decision that changes:** whether a round-2 lane hunts the explicit
GF(2) basis realizing the king char-2 collapse — the open constructive step
of INV-4 (`results/triangle-r3-involution.md` §NOT ESTABLISHED), whose prize
was T(40,21) mod 2 in megabytes and laptop hours. That row's stated precedent
was CKN ("Fast Hamiltonicity checking via bases of perfect matchings",
arXiv:1211.1506): the matchings-connectivity matrix collapses to 2^(t/2−1)
over GF(2) *with an explicit basis*, so — the argument ran — the same
phenomenon here likely has one too. Rook is the lattice where that
matchings/planarity machinery natively lives, and rook shows **no collapse at
all** on the identical state space. So the king collapse is not the generic
CKN connectivity phenomenon riding on the cut vocabulary; it is produced by
the diagonal stencil specifically, and the precedent leg of the basis hunt is
measured out from under it. The hunt is not killed — the king rank numbers
are real and reproduced — but its prior must be reset from "known phenomenon
with a known constructive precedent" to "unexplained king-specific structure,
mechanism unknown", and a mechanism probe (queue row C1) is the cheap next
step, not a basis search.

For this campaign's own goal the same measurement closes a door: no
field-linear realization of the rook strip functional beats the Motzkin
dimension in any characteristic at measured H — parity (char 2) included. The
√3 exponent is linear-realization-tight on rook as far as measured; the
goal file's honest frame ("parity means matching the Motzkin exponent, not
breaking it", `docs/rook-parity.md:154-158`) now has a measurement behind it.
Filed as queue row C2.

## NOT ESTABLISHED

- Rook mod-p ranks at H ≥ 8 (cost; the H ≤ 7 pattern is exact fullness and
  nothing suggests a turn).
- Whether the rook GF(2) share of states (100% → 77% over H = 4..9) is
  polynomial thinning or a late-onset exponential gap. Growth is pinned at
  ~2.42×/height over five consecutive ratios, far above 2.0; distinguishing
  the two readings needs H = 10..11 (queue row C3, job-scale). No round-2
  decision currently depends on it.
- The king 0.44·2^H law past H = 9 remains unverified (unchanged from the
  banked caveat); this lane reproduced the king numbers with the same-family
  rank code, which is a regression, not an independent re-derivation.
- Why the king stencil produces the char-2 collapse — mechanism unknown;
  queue row C1 is the cheapest discriminating probe (the asymmetric
  one-diagonal stencil).

## Queue rows filed

C1–C4, appended to `results/rook1/queue.md`.
