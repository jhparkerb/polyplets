#!/usr/bin/env python3
"""B17: the integrality-congruence gate on the Undertow tower's depth defects.

A below-onset tower cell at level k, depth j = 2k+1-n sits at

    T(2k+1-j, k+1-j) = P_k(2k+1-j) * 3^(-(k+j)) + D_j(k),

and T is an integer.  Since den(D_j(k)) divides 3^(k+j) (checked here, not
assumed), integrality of the left side forces

    P_k(2k+1-j) + 3^(k+j) * D_j(k)  ==  0   (mod 3^(k+j)),

i.e. D_j(k)'s NUMERATOR mod 3^(k+j) is pinned by P_k alone.  The modulus grows
with k and j, so the strongest congruences sit exactly where nothing else
reaches: the frontier levels' unbanked cells.  Discovered as a one-off for
D_2(21) by Lane B of the Undertow review (results/a41/PROVENANCE.md "One real,
weak check"); this gate is the systematic version across the whole tower.

Cell classes, kept honest:

  PIN     used to pin its own level's (a_k, b_k) -- integrality holds by
          construction, reported but never counted as evidence;
  BANKED  a banked cell exists -- the gate asserts full equality (strictly
          stronger than the congruence; this subsumes the W3 gate's cells and
          the row-40 regression's one real cell, T(40,20));
  FREE    no banked cell -- the congruence itself is the check, and it is the
          only check these D_j(k) have against the tower.  Today that is
          (k,j) = (21,1) mod 3^22 and (21,2) mod 3^23.

What the congruence can and cannot see: it constrains D_j(k) modulo 1 only --
an INTEGER perturbation of a free cell's defect passes (selftest RED 3
demonstrates this blind spot on purpose).  A perturbation of 1/3^(k+j), the
smallest representable, is caught (RED 1).  It also reaches the pin inputs
transitively: perturbing D_4(21) -- the one single-source constant left in
a(41)'s tower -- shifts the fitted (a_21, b_21) and breaks integrality at the
free cells (RED 4 measures this rather than asserting it from theory).

Usage:
  python3 experiments/undertow_congruence_gate.py             # the gate
  python3 experiments/undertow_congruence_gate.py --selftest  # RED controls

Exit 0 = GATE GREEN; anything else = red.
"""

import os
import sys
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from undertow_pin import all_pairs, grand_form, peval, pow3      # noqa: E402
from undertow_a41 import build                                   # noqa: E402

JMAX = 4
KMAX = 21          # wired 1..19 + Undertow-pinned 20, 21, as in the a(41) run
HMAX_PIN = 19      # the a(41) pin cap: no pinning cell taller than the sweep


def pin_cells(tri, jmax=JMAX, hmax=HMAX_PIN):
    """The cells each pinned level consumed, per the a(41) recipe."""
    used = {}
    for k in (20, 21):
        pairs = all_pairs(k, jmax, tri, hmax)
        used[k] = {(2 * k + 1 - j, k + 1 - j) for d in pairs for j in d}
    return used


def run_gate(ab, Dj, tri, quiet=False):
    """Returns (n_banked, n_free); raises AssertionError on any violation."""
    E = grand_form(ab, KMAX)
    used = pin_cells(tri)
    n_banked = n_free = 0
    for k in range(1, KMAX + 1):
        for j in range(1, JMAX + 1):
            n, H = 2 * k + 1 - j, k + 1 - j
            if H < 1 or k >= len(Dj[j]):
                continue
            d = Dj[j][k]
            m = k + j
            assert (F(3) ** m * d).denominator == 1, \
                f"den(D_{j}({k})) does not divide 3^{m}: {d}"
            val = peval(E[k], n) * pow3(-m) + d
            if (n, H) in used.get(k, ()):
                cls = "PIN"                      # by construction; not counted
            elif (n, H) in tri:
                cls = "BANKED"
                assert val == F(tri[(n, H)]), \
                    f"T({n},{H}) k={k} j={j}: tower {val} != banked {tri[(n, H)]}"
                n_banked += 1
            else:
                cls = "FREE"
                assert val.denominator == 1, \
                    f"CONGRUENCE RED at (k,j)=({k},{j}): P_{k}({n})/3^{m} + " \
                    f"D_{j}({k}) is not an integer -- D_{j}({k}) fails mod 3^{m}"
                n_free += 1
                if not quiet:
                    print(f"  FREE cell T({n},{H}) (k={k}, j={j}): "
                          f"D_{j}({k}) congruent mod 3^{m}  OK")
            if cls == "PIN" and not quiet:
                print(f"  pin  cell T({n},{H}) (k={k}, j={j}): by construction, "
                      f"not counted")
    return n_banked, n_free


# TODO(2026-08-24, /simplify): two couplings worth loosening, neither unsafe
# today (both fail loud rather than silently green). RED 4 monkeypatches
# load_depths in TWO modules because undertow_a41 from-imports the name, so an
# innocent import refactor turns the suite red; build() taking an optional Dj
# override would end that. And this file restates a(41)'s recipe as its own
# JMAX/KMAX/HMAX_PIN constants plus a reimplemented pin_cells(), so if the
# recipe moves, the gate keeps green-lighting the old one -- import the
# constants from undertow_a41 and have build() return the cells it consumed.
def build_tower():
    return build(JMAX, KMAX, forbid_row=None, hmax=HMAX_PIN)


def main():
    ab, Dj, tri, _ = build_tower()
    n_banked, n_free = run_gate(ab, Dj, tri)
    assert n_free >= 2, \
        f"only {n_free} FREE cells -- the gate's new-evidence surface is gone"
    print(f"congruence gate: {n_banked} banked cells equal exactly, "
          f"{n_free} unbanked defects pass their 3-power congruence "
          f"(strongest modulus 3^{KMAX + 2})")
    print("GATE GREEN")


def selftest():
    ab, Dj, tri, _ = build_tower()

    bad = {j: list(v) for j, v in Dj.items()}
    bad[2][21] += F(1, 3 ** 23)
    try:
        run_gate(ab, bad, tri, quiet=True)
    except AssertionError:
        print("RED 1 GREEN: D_2(21) + 3^-23 is caught at the free cell")
    else:
        raise SystemExit("RED 1 FAILED: minimal fractional perturbation passed")

    wrong = dict(ab)
    wrong[21] = (ab[21][0] + 1, ab[21][1])
    try:
        run_gate(wrong, Dj, tri, quiet=True)
    except AssertionError:
        print("RED 2 GREEN: a corrupted a_21 is caught")
    else:
        raise SystemExit("RED 2 FAILED: corrupted level constant passed")

    blind = {j: list(v) for j, v in Dj.items()}
    blind[2][21] += 1
    run_gate(ab, blind, tri, quiet=True)     # must NOT raise
    print("RED 3 GREEN (blind spot, by design): an INTEGER shift of a free "
          "cell's defect passes -- the congruence sees only the fractional part")

    # RED 4: the transitive probe.  Perturb D_4(21) BEFORE pinning; the fitted
    # (a_21, b_21) absorb the shift and the free cells' integrality breaks.
    import undertow_pin
    real = undertow_pin.load_depths

    def tampered(jmax, K):
        out = real(jmax, K)
        out[4][21] += F(1, 3 ** 25)
        return out
    undertow_pin.load_depths = tampered
    try:
        import undertow_a41
        undertow_a41.load_depths = tampered
        ab2, Dj2, tri2, _ = build_tower()
        try:
            run_gate(ab2, Dj2, tri2, quiet=True)
        except AssertionError:
            print("RED 4 GREEN: D_4(21) + 3^-25 -- the single-source constant "
                  "-- is caught TRANSITIVELY through the pinned (a_21, b_21)")
        else:
            print("RED 4: D_4(21) perturbation NOT caught -- the gate does not "
                  "reach the pin inputs; do not claim transitive coverage")
            raise SystemExit(1)
    finally:
        undertow_pin.load_depths = real
        undertow_a41.load_depths = real


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
    else:
        main()
