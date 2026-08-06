#!/usr/bin/env python3
"""Gate CONVEX-DFINITE: docs/middle-kingdom-plan.md Phase 2a/2b acceptance.

Guards the sharpened non-D-finite verdict for HV-convex animals BY AREA --
king (convex polyplets, novel) and edge-adjacent (A067675, the control) --
and the growth constants extracted from the same series.

The claim being guarded is a *negative*, so the gate's real job is to keep the
guesser powered. Every check below is either a positive control the guesser
must PASS (find a relation that is known to exist) or a negative control it
must reject:

  prec positive  HV-convex by semiperimeter has a banked order-5 degree-2
                 P-recurrence (results/convex-polyplets.md). build/prec_guess
                 must find it -- rank-deficient AND the fitted nullspace must
                 predict every held-out row.
  prec negative  the same series in the (2,1) box, too small to hold that
                 recurrence: must come back EXCLUDED. Without this, a guesser
                 that reported CANDIDATE for everything would look healthy.
  alg positive   A005436 (convex polyominoes by semiperimeter) is algebraic,
                 Delest-Viennot. Algebraic mode must find the relation at
                 degree 2, and must not find one at t-degree 4 (too small).
  adjacency      build/convex_area_tm king=1 and king=0 must reproduce their
                 two reference prefixes exactly and differ from each other --
                 the king=0 path is new in Phase 2a and A067675 is its oracle.

Only then are the two exclusions themselves checked, in both modes.
"""
import os
import subprocess
import sys
from decimal import Decimal, getcontext

from common import ROOT, Gate

GUESS = os.path.join(ROOT, "build", "prec_guess")
AREA = os.path.join(ROOT, "build", "convex_area_tm")

KING14 = [1, 4, 16, 61, 221, 766, 2566, 8390, 26982, 85834, 271174, 853111,
          2677214, 8389720]
# A067675, fixed convex polyominoes by area (docs/middle-kingdom-plan.md
# reference table, "convex polyomino by area (CONTROL)").
POLY14 = [1, 2, 6, 19, 59, 176, 502, 1374, 3630, 9312, 23320, 57279,
          138536, 331032]

KING_TERMS = os.path.join(ROOT, "results", "convex_area_terms_n700_king.txt")
POLY_TERMS = os.path.join(ROOT, "results", "convex_area_terms_n700_poly.txt")
PERIM_TERMS = os.path.join(ROOT, "results", "convex_perim_terms_s200.txt")
A005436_TERMS = os.path.join(ROOT, "results", "a005436_perim_s100.txt")

# Phase 2b, 199 (king) and 121 (control) trusted digits; the gate pins the
# leading 15, which a broken transfer matrix could not reproduce by accident.
MU_KING = "3.12894326973088"
MU_POLY = "2.30913859333049"


def guess(mode, terms, a, b, extra=()):
    """Run build/prec_guess; return (verdict, nullity, holdout, rows_held)."""
    r = subprocess.run([GUESS, mode, terms, str(a), str(b)] + list(extra),
                       capture_output=True, text=True)
    if r.returncode not in (0, 3):
        raise RuntimeError(f"prec_guess rc={r.returncode}\n{r.stderr}\n{r.stdout}")
    verdict, nullity, hold, held = None, None, None, None
    for line in r.stdout.splitlines():
        if line.startswith("VERDICT:"):
            verdict = line.split()[1]
        elif line.startswith("full rank="):
            nullity = int(line.rsplit("=", 1)[1])
        elif line.startswith("holdout rows="):
            parts = line.split()
            held = int(parts[1].split("=")[1])
            hold = int(parts[2].split("=")[1])
    return verdict, nullity, hold, held


def terms_of(path):
    with open(path) as f:
        return [int(l.split()[-1]) for l in f if l.strip()
                and not l.startswith("#")]


def main():
    g = Gate()

    # --- the adjacency switch, against both oracles -------------------------
    # convex_area_tm needs GMP, which the Makefile treats as optional; the
    # terms files it produced are in the tree either way, so the exclusions
    # below still run on a box without it.
    if os.path.exists(AREA):
        for king, ref, label in ((1, KING14, "king (convex polyplets)"),
                                 (0, POLY14, "king=0 (A067675 control)")):
            out = subprocess.run([AREA, "14", str(king)], capture_output=True,
                                 text=True, check=True).stdout
            got = [int(x) for x in out.strip().split(",")]
            g.check(got == ref, f"convex_area_tm 14 {king} reproduces {label}")
    else:
        print("skip  convex_area_tm adjacency oracle (no GMP build)")
    g.check(terms_of(KING_TERMS)[:14] == KING14,
            "banked king series starts with the reference 14 terms")
    g.check(terms_of(POLY_TERMS)[:14] == POLY14,
            "banked control series starts with A067675's first 14 terms")

    # --- positive control: the guesser must FIND a known recurrence ---------
    v, nul, hold, held = guess("prec", PERIM_TERMS, 5, 2)
    g.check(v == "CANDIDATE" and nul >= 1,
            f"prec positive control: banked (5,2) recurrence found (nullity {nul})")
    g.check(hold == held and held > 100,
            f"prec positive control: fitted recurrence predicts all {held} held-out rows")

    # --- negative control: a box too small must be EXCLUDED -----------------
    v, nul, _, _ = guess("prec", PERIM_TERMS, 2, 1)
    g.check(v == "EXCLUDED" and nul == 0,
            "prec negative control: (2,1) box correctly excluded")

    # --- algebraic mode, both directions ------------------------------------
    v, nul, hold, held = guess("alg", A005436_TERMS, 2, 8)
    g.check(v == "CANDIDATE" and nul >= 1,
            f"alg positive control: A005436 algebraic at (2,8) (nullity {nul})")
    g.check(hold == held and held > 30,
            f"alg positive control: relation holds on all {held} held-out rows")
    v, nul, _, _ = guess("alg", A005436_TERMS, 2, 4)
    g.check(v == "EXCLUDED" and nul == 0,
            "alg negative control: A005436 at (2,4) correctly excluded")

    # --- the finding ---------------------------------------------------------
    for path, label in ((KING_TERMS, "convex polyplets by area"),
                        (POLY_TERMS, "convex polyominoes by area (A067675)")):
        for mode in ("prec", "alg"):
            v, nul, _, _ = guess(mode, path, 20, 20)
            g.check(v == "EXCLUDED" and nul == 0,
                    f"{label}: {mode} box (20,20) EXCLUDED")

    # --- growth constants ----------------------------------------------------
    getcontext().prec = 40
    for path, mu, label in ((KING_TERMS, MU_KING, "mu_king"),
                            (POLY_TERMS, MU_POLY, "mu_control")):
        a = terms_of(path)
        r = Decimal(a[-1]) / Decimal(a[-2])
        g.check(str(r).startswith(mu), f"{label} tail ratio starts {mu} (got {str(r)[:16]})")

    return g.verdict("CONVEX-DFINITE")


if __name__ == "__main__":
    sys.exit(main())
