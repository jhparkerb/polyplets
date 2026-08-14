# Coin Lift G2 — the collapse does not lift, and the kill fires

Probe: `experiments/tristruct/r3_lift_snf_probe.py`; logs
`r3_lift_snf_probe.log` (p = 2), `r3_lift_snf_probe_p3.log` (p = 3).
Plan: `docs/coin-lift-plan.md` §2 G2. Run 2026-08-14 on gympie, ~90 minutes
including the instrument.

**Coin Lift is dead.** Two deterministic bits per cell cost twice the char-2
dimension; three bits cost the whole generic rank. Coin Flip, Coin Roll and
Biased Coin Flip survive untouched — one bit, or a probabilistic fingerprint.
G3 and G4 do not need to run.

## The gate had to be restated first

G2 as written — "Smith normal form over Z/4, kill if the Z/4 **free rank**
jumps toward the mod-p curve" — can never fire. The free rank over Z/4 counts
the invariant factors that are units mod 4, a factor is a unit mod 4 iff it is
odd, and a factor is odd iff it survives reduction mod 2. So the Z/4 free rank
is *identically* the GF(2) rank already banked. It cannot jump.

The object that decides the gate is the minimal number of generators of the
Hankel column module over Z/2^k — the floor on the dimension of any Z/2^k
realization, the exact analogue over the ring of the field rank:

    mu_k(H) = #{ invariant factors d_i of the observability matrix
                 with v_2(d_i) < k }

with `mu_1` = rank over GF(2) (the collapse) and `mu_inf` = rank over Q, which
is >= the rank over F_p (the generic curve). The gate reads `mu_2`, `mu_3`.

## Measured, p = 2

| H | states | mu_1 = GF(2) | mu_2 = Z/4 | mu_3 = Z/8 | mu_4 | rank mod p | mu_2/mu_1 |
|---|---|---|---|---|---|---|---|
| 4 | 20 | 6 | 6 | 6 | 6 | 6 | 1.000 |
| 5 | 50 | 15 | 17 | 17 | 17 | 17 | 1.133 |
| 6 | 126 | 27 | 35 | 35 | 35 | 35 | 1.296 |
| 7 | 322 | 58 | 86 | 88 | 88 | 88 | 1.483 |
| 8 | 834 | 112 | 194 | 204 | 204 | 204 | 1.732 |
| 9 | 2,187 | 229 | 459 | 500 | **501** | 501 | 2.004 |

Two readings, both fatal:

- **`mu_2/mu_1` grows every height** — 1.00, 1.13, 1.30, 1.48, 1.73, 2.00. It
  is not a constant overhead to be absorbed; the second bit costs more the
  higher you go. At H = 9 the second bit has already spent the entire factor-2
  saving the collapse bought.
- **`mu_4` is the generic rank exactly** at every measured height. Four bits
  per cell is the full mod-p dimension — no compression at all. Z/8 is within
  1 of it at H = 9.

The collapse is the characteristic-2 degeneracy x + x = 0 and nothing more, as
`docs/coin-lift-plan.md` §2 predicted ("Prior: poor"). It does not survive one
lift.

## Measured, other characteristics — asked because the answer was cheap

`mu_1` at p = 3 is 6, 17, 35, 87, 201, **488** at H = 4..9, against a generic
rank of 6, 17, 35, 88, 204, 501: a 2.6% thinning at H = 9, nothing to build
on. At p = 5 and p = 7 the rank is the generic rank exactly at every H <= 8.
Extension fields of characteristic 2 need no measurement — rank is invariant
under field extension, so GF(2^k) on the same matrix *is* the GF(2) rank, and
the graded GF(2^16) probe already matched ungraded GF(2) six for six.

So the crack is specific to the characteristic as well as to the stencil
(round 1's R1-C found rook has no char-2 crack at all). One bit is the whole
prize.

## What the ladder confirms on the way past

`mu_inf` reproduces A-S1's measured mod-p ladder 6, 17, 35, 88, 204, 501 at
every height, by an independent computation over Z rather than mod 2^31-1. So
**rank_Q = rank_{F_p} here** — no invariant factor of large valuation, no
p-torsion accident. That tightens `docs/coin-lift-plan.md` §1: the exclusion
argument's floor `rank_Q >= rank_{F_p}` is now an equality where it has been
measured, and §4's separate lead (a 17x exact-arithmetic floor at H = 21 that
nothing constructs) stands unchanged.

## Battery

Fail-closed; the probe exits nonzero unless every GREEN passes and every RED
fires.

- GREEN `mu_1` equals the banked GF(2) ladder 6, 15, 27, 58, 112, 229.
- GREEN `mu_1` equals `obs_rank_gf2_x1`'s value — a second, independently
  written elimination (bitset over GF(2) against local elimination mod 2^K).
- GREEN `mu_K` equals A-S1's mod-p rank wherever both exist.
- RED the red=True stencil (one diagonal dropped from the merge) must move the
  mu profile: 6 -> 11 at H = 4, [15,17,17] -> [24,25,25] at H = 5.

**The battery caught a real defect before the number was believed.** The first
H = 9 run reported `mu_8` = 498 against a mod-p rank of 501, and the third
GREEN failed the run. The cause was in the closure pruning: when an incoming
residual carried a *shallower* 2-adic valuation than the basis row at its
pivot column, the two were swapped and the displaced row went on being
reduced — and if it then reduced to zero, the routine reported "already in the
module" and dropped the incoming vector, which had just changed the basis.
Three generators of 501 were lost at H = 9. The fix is to report the basis
having changed, not the residual having survived. No conclusion here rests on
the pre-fix numbers, and the H <= 8 rows were identical either way.
