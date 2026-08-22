#!/usr/bin/env python3
"""Gate MK-DIR4-PERIM: docs/middle-kingdom-followups-plan.md Phase 2a
acceptance.

cpp/convex_perim_tm.cpp's new dir4 mode filters HV-convex king animals BY
SEMIPERIMETER down to the half-plane-4-cone-directed subset (Proposition 2 of
results/middle-kingdom-phase3.md, translated onto this row-built transfer
matrix -- see the header comment there for the derivation). This gate is the
brute-force validator, plus the RED control and the termwise sanity check the
plan's acceptance requires.

Ground truth: build/directed_cone_anchor's new "gridperim" mode reuses the
SAME reach(Dir4)/convexity() predicate code the (already gated, see
gate_king_grid.py) "grid" mode uses, just bucketed by box (s = W+H) instead of
area. An area-<=N enumeration settles semiperimeter s completely only up to
s where floor(s/2)*ceil(s/2) <= N (max area at that box); beyond that the
brute-force count is a LOWER bound only, so the gate restricts its equality
check to the fully-covered range and does not compare beyond it.

Checks, in the plan's order:
  1. RED control FIRST: the dir4bad mode (the "e.g. non-strict decrease"
     variant the plan named -- verbatim the unrestricted-HV transition,
     mislabeled dir4) must diverge from the true brute-force dir4 counts.
  2. Brute force: convex_perim_tm's dir4 mode must exactly reproduce
     directed_cone_anchor's gridperim brute force at every s the enumeration
     settles completely.
  3. Termwise sanity: dir4(s) <= hv(s) (the unrestricted convex_perim_tm
     mode) at every s in range, with equality only at the small s where
     brute force confirms every animal of that box is already dir4-directed.
  4. The A005436 control (king=0) is unaffected by any of this -- still
     reproduces its banked reference prefix.
"""
import os
import sys

from common import ROOT, Gate, run, require_binary

TM = os.path.join(ROOT, "build", "convex_perim_tm")
ANCHOR = os.path.join(ROOT, "build", "directed_cone_anchor")

# A005436 (convex polyominoes by semiperimeter), banked reference prefix --
# results/convex-polyplets.md / Delest-Viennot.
A005436_REF = [1, 2, 7, 28, 120, 528, 2344, 10416, 46160, 203680]


def run_tm(smax, king, mode):
    out = run(TM, smax, king, mode)
    return [int(x) for x in out.strip().split(",")]  # index 0 == s=2


def run_brute(n, threads=4):
    out = run(ANCHOR, "gridperim", n, threads)
    hv, dir4 = {}, {}
    for line in out.strip().splitlines():
        s, h, d = (int(x) for x in line.split())
        hv[s], dir4[s] = h, d
    return hv, dir4


def main():
    gate = Gate()
    if not require_binary(ANCHOR, "build/directed_cone_anchor"):
        return 1
    if not os.path.exists(TM):
        # convex_perim_tm needs GMP, which the Makefile treats as optional
        # (see gate-middle-kingdom/gate-convex-dfinite for the same pattern).
        gate.skip(f"{TM} absent (no GMP build) -- the WHOLE gate; "
                  f"nothing below ran and nothing was verified")
        return gate.verdict("MK-DIR4-PERIM")

    accept_n = 12   # floor(7/2)*ceil(7/2) = 12: full coverage through s=7
    full_smax = 7   # inclusive
    hv_brute, dir4_brute = run_brute(accept_n)

    smax = 15
    hv_tm = run_tm(smax, 1, "hv")
    dir4_tm = run_tm(smax, 1, "dir4")
    dir4bad_tm = run_tm(smax, 1, "dir4bad")

    def at(series, s):
        return series[s - 2]

    # --- 1. RED control first -------------------------------------------
    bad = [s for s in range(2, full_smax + 1) if at(dir4bad_tm, s) != dir4_brute[s]]
    gate.check(bool(bad),
               "RED control dir4bad MUST diverge from brute-force dir4 "
               f"somewhere in s<=  {full_smax}: diverged at s={bad}")
    # dir4bad is literally the unrestricted transition, so it should agree
    # with the hv mode exactly (confirms the RED control is what it claims
    # to be, not a different, accidentally-also-wrong rule).
    same_as_hv = [s for s in range(2, smax + 1)
                  if at(dir4bad_tm, s) != at(hv_tm, s)]
    gate.check(not same_as_hv,
               "RED control dir4bad == hv mode exactly (same code path)"
               + (f"  DIFFERS at s={same_as_hv}" if same_as_hv else ""))

    # --- 2. brute force, exact match where the enumeration is complete ---
    bad_hv = [s for s in range(2, full_smax + 1) if at(hv_tm, s) != hv_brute[s]]
    gate.check(not bad_hv,
               f"hv mode vs gridperim brute force, s<={full_smax} (complete)"
               + (f"  MISMATCH at s={bad_hv}" if bad_hv else ""))
    bad_dir4 = [s for s in range(2, full_smax + 1)
                if at(dir4_tm, s) != dir4_brute[s]]
    gate.check(not bad_dir4,
               f"dir4 mode vs gridperim brute force, s<={full_smax} (complete)"
               + (f"  MISMATCH at s={bad_dir4}" if bad_dir4 else ""))
    # Beyond full coverage the brute force is a lower bound only -- the TM
    # must never undercut it (that would mean the TM itself is missing
    # animals, not just that brute force is incomplete).
    bad_lb = [s for s in range(full_smax + 1, accept_n + 2)
              if at(dir4_tm, s) < dir4_brute.get(s, 0)]
    gate.check(not bad_lb,
               f"dir4 mode >= brute-force LOWER BOUND beyond s={full_smax}"
               + (f"  UNDERCUT at s={bad_lb}" if bad_lb else ""))

    # --- 3. termwise sanity: dir4 <= hv everywhere ------------------------
    bad_order = [s for s in range(2, smax + 1) if at(dir4_tm, s) > at(hv_tm, s)]
    gate.check(not bad_order,
               "dir4(s) <= hv(s) at every s"
               + (f"  VIOLATED at s={bad_order}" if bad_order else ""))
    eq = [s for s in range(2, smax + 1) if at(dir4_tm, s) == at(hv_tm, s)]
    gate.check(eq == [2, 3, 4],
               f"dir4(s) == hv(s) only at the small s where brute force "
               f"confirms every animal is already directed: got {eq} want [2,3,4]")

    # --- 4. A005436 control unaffected ------------------------------------
    poly = run_tm(11, 0, "hv")
    got = poly[:len(A005436_REF)]
    gate.check(got == A005436_REF,
               f"king=0 control (A005436) unaffected: got {got}")

    print(f"hv   s=2..{smax}: {hv_tm}")
    print(f"dir4 s=2..{smax}: {dir4_tm}")
    print(f"brute (n<={accept_n}) hv:   {[hv_brute.get(s) for s in range(2, accept_n+2)]}")
    print(f"brute (n<={accept_n}) dir4: {[dir4_brute.get(s) for s in range(2, accept_n+2)]}")

    return gate.verdict("MK-DIR4-PERIM")


if __name__ == "__main__":
    sys.exit(main())
