#!/usr/bin/env python3
"""Gate DIR4-PERIM-ALG: docs/middle-kingdom-followups-plan.md Phase 2b.

The claim guarded here is a POSITIVE one -- (dir4, HV-convex) king animals by
semiperimeter have an algebraic generating function -- so the gate's job is
the mirror image of gate_convex_dfinite.py's: it must pin the relation that
was found, and it must keep a negative control alongside every positive arm so
that a guesser which said CANDIDATE to everything would fail here.

  positive     build/prec_guess alg on results/mk_dir4_perim_terms_s200.txt in
               the box (4,22): nullity exactly 1, and the nullspace fitted on
               the first 119 rows must annihilate all 81 later ones.
  negative     the same series at (4,21) and (3,48): EXCLUDED. The relation is
               minimal in BOTH directions, so one notch smaller must fail.
  null control 199 terms of the by-area king series -- the same length, and
               rigorously non-D-finite (EXCLUDED at (24,24) on its 700 terms,
               results/convex-polyplets.md). Must be EXCLUDED in every box
               where the dir4 series is a CANDIDATE. Re-cut from that series
               into build/ on every run (see cut_null_control): the gate keeps
               no derived copy of its own input, so there is no stale file to
               fall back to, and a missing or wrong source is a loud stop.
  nullity law  a genuine minimal (K0,L0) relation forces nullity
               (K-K0+1)(L-L0+1) as the box opens. Pinned at four boxes; a
               spurious rank defect does not obey it.
  A005436      the Delest-Viennot algebraic control from gate_convex_dfinite,
               kept wired here too: the plan requires the guesser stay
               demonstrably powered on a series whose answer is known
               independently of anything this repo computed.
  the equation the exact quartic itself, recovered over Q by
               experiments/dir4_perim_find_alg.py, coefficient for
               coefficient, plus its P-recurrence sibling at (19,3).

~8 s.
"""
import os
import subprocess
import sys

from common import ROOT, Gate
# KING14: the by-area king series' first 14 terms, the reference prefix
# gate_convex_dfinite.py already guards. Imported, not copied, so the null
# control here and the exclusion there are pinned to the same numbers.
from gate_convex_dfinite import KING14

GUESS = os.path.join(ROOT, "build", "prec_guess")
DIR4 = os.path.join(ROOT, "results", "mk_dir4_perim_terms_s200.txt")
HV = os.path.join(ROOT, "results", "convex_perim_terms_s200.txt")
AREA700 = os.path.join(ROOT, "results", "convex_area_terms_n700_king.txt")
NULL199 = os.path.join(ROOT, "build", "dir4_perim_null199.txt")
A005436 = os.path.join(ROOT, "results", "a005436_perim_s100.txt")
FIND_ALG = os.path.join(ROOT, "experiments", "dir4_perim_find_alg.py")
NULL_N = 199

# The relation, from results/dir4_perim_find_alg.log. sum_j q_j(t) F^j = 0,
# q_j written low-degree-first from t^0.
QUARTIC = [
    [0, 0, 0, 0, 9, -120, 676, -2140, 4283, -5576, 4198, -906, -1270, 1350,
     -96, 364, 888, 526, 349, 246, 98, 16, 1],
    [0, 0, 0, -30, 482, -3174, 11056, -21912, 24026, -9132, -11860, 13626,
     492, -2894, 6540, 8332, 7390, 6696, 4312, 1616, 314, 24, 0],
    [0, 0, 37, -700, 5389, -21320, 44037, -37722, -13978, 48384, -20464,
     -33324, 20515, 32808, 26909, 36302, 40156, 26936, 10841, 2516, 286, 8, 0],
    [0, -20, 438, -3916, 17882, -40900, 28522, 51028, -69112, -44984, 48224,
     20452, -21166, 31956, 110234, 124676, 81772, 34364, 9190, 1424, 96, 0, 0],
    [4, -100, 1029, -5446, 14407, -10250, -32039, 43974, 65620, -55556,
     -141788, -55634, 115295, 212542, 190333, 112426, 46834, 13732, 2689, 312,
     16, 0, 0],
]


def guess(mode, terms, a, b, prime=0):
    """(verdict, nullity, holdout_pass, holdout_rows) from build/prec_guess."""
    r = subprocess.run([GUESS, mode, terms, str(a), str(b), str(prime)],
                       capture_output=True, text=True)
    if r.returncode not in (0, 2, 3):
        raise RuntimeError(f"prec_guess rc={r.returncode}\n{r.stderr}{r.stdout}")
    v, nul, hp, hr = None, None, None, None
    for line in r.stdout.splitlines():
        if line.startswith("VERDICT:"):
            v = line.split()[1]
        elif line.startswith("full rank="):
            nul = int(line.rsplit("=", 1)[1])
        elif line.startswith("holdout rows="):
            p = line.split()
            hr = int(p[1].split("=")[1])
            hp = int(p[2].split("=")[1])
    return v, nul, hp, hr


def parse_poly(line, L):
    """'  q_0(t) = 9*t^4 + -120*t^5 + ...' -> dense coefficient list."""
    cs = [0] * (L + 1)
    for term in line.split("=", 1)[1].split(" + "):
        c, _, p = term.strip().partition("*t^")
        cs[int(p)] = int(c)
    return cs


def stop(why):
    """Refuse to run rather than test something other than what is claimed."""
    sys.exit(f"GATE DIR4-PERIM-ALG: RED -- {why}")


def terms_of(path):
    """Non-comment lines and their trailing values, in file order."""
    lines, vals = [], []
    with open(path) as f:
        for line in f:
            if line.strip() and not line.startswith("#"):
                lines.append(line)
                vals.append(line.split()[-1])
    return lines, vals


def cut_null_control():
    """Re-cut the null control from the by-area king series, into build/.

    The control is only a control if it IS that series: length-matched to the
    dir4 series and rigorously non-D-finite on its full 700 terms. So the cut
    is made here, every run, from the real source -- checked to exist, to be
    long enough, and to start with the banked 14-term prefix -- and nothing
    derived is kept in results/. A missing or altered source stops the gate;
    it never silently falls back to a previously cut file.
    """
    if not os.path.isfile(AREA700):
        stop(f"null control source missing: {AREA700}\n"
             "  It is the 700-term HV-convex-king-animals-by-area series"
             " (results/convex-polyplets.md).\n"
             "  Regenerate (needs GMP, ~8 min; the engine prints the terms"
             " comma-separated,\n  this file is one 'n a(n)' pair per line):\n"
             "    build/convex_area_tm 700 1 | tr ',' '\\n' |"
             " awk '{print NR, $1}' \\\n"
             "      > results/convex_area_terms_n700_king.txt")
    lines, vals = terms_of(AREA700)
    if len(vals) < NULL_N:
        stop(f"null control source {AREA700} has {len(vals)} terms,"
             f" fewer than the {NULL_N} the control needs")
    if not all(v.isdigit() for v in vals[:NULL_N]):
        stop(f"null control source {AREA700} is not a list of positive"
             " integer terms")
    if [int(v) for v in vals[:14]] != KING14:
        stop(f"null control source {AREA700} does not start with the banked"
             f" by-area king prefix\n  want {KING14}\n"
             f"  got  {[int(v) for v in vals[:14]]}")
    os.makedirs(os.path.dirname(NULL199), exist_ok=True)
    with open(NULL199, "w") as f:
        f.writelines(lines[:NULL_N])
    return vals[:NULL_N]


def main():
    g = Gate()

    # --- the null control, re-cut from its source, matched to the dir4 series -
    null = cut_null_control()
    _, dir4_vals = terms_of(DIR4)
    g.check(len(null) == NULL_N == len(dir4_vals),
            f"null control: {NULL_N} terms of the by-area king series,"
            f" length-matched to the dir4 series ({len(dir4_vals)})")

    # --- positive: the relation, and its holdout ----------------------------
    for prime in (0, 1):
        v, nul, hp, hr = guess("alg", DIR4, 4, 22, prime)
        g.check(v == "CANDIDATE" and nul == 1,
                f"dir4 alg (4,22) prime{prime}: nullity exactly 1 (got {nul})")
        g.check(hp == hr and hr == 81,
                f"dir4 alg (4,22) prime{prime}: fit predicts all {hr} held-out rows")

    v, nul, hp, hr = guess("prec", DIR4, 19, 3)
    g.check(v == "CANDIDATE" and nul == 1,
            f"dir4 prec (19,3): nullity exactly 1 (got {nul})")
    g.check(hp == hr and hr == 96,
            f"dir4 prec (19,3): fit predicts all {hr} held-out rows")

    # --- negative: one notch smaller in each direction must be EXCLUDED -----
    for mode, a, b, why in (("alg", 4, 21, "t-degree one short"),
                            ("alg", 3, 48, "algebraic degree 3, t-degree 48"),
                            ("prec", 19, 2, "degree one short"),
                            ("prec", 18, 3, "order one short"),
                            ("prec", 5, 2, "the unrestricted series' own box")):
        v, nul, _, _ = guess(mode, DIR4, a, b)
        g.check(v == "EXCLUDED" and nul == 0,
                f"dir4 {mode} ({a},{b}) EXCLUDED -- {why}")

    # --- null control: EXCLUDED wherever dir4 is a candidate -----------------
    for mode, a, b in (("alg", 4, 22), ("alg", 4, 24), ("prec", 19, 3),
                       ("prec", 27, 2), ("prec", 13, 9)):
        v, nul, _, _ = guess(mode, NULL199, a, b)
        g.check(v == "EXCLUDED" and nul == 0,
                f"null control {mode} ({a},{b}) EXCLUDED (same box, same length)")

    # --- the nullity law a genuine minimal relation obeys --------------------
    for a, b, want in ((5, 22, 2), (6, 22, 3), (4, 23, 2), (4, 24, 3)):
        _, nul, _, _ = guess("alg", DIR4, a, b)
        g.check(nul == want,
                f"dir4 alg ({a},{b}) nullity {want} = (K-3)(L-21) (got {nul})")

    # --- A005436, the external algebraic control ----------------------------
    v, nul, hp, hr = guess("alg", A005436, 2, 8)
    g.check(v == "CANDIDATE" and nul >= 1,
            f"A005436 algebraic at (2,8) (nullity {nul})")
    g.check(hp == hr and hr > 30,
            f"A005436: relation holds on all {hr} held-out rows")
    v, nul, _, _ = guess("alg", A005436, 2, 4)
    g.check(v == "EXCLUDED" and nul == 0, "A005436 at (2,4) EXCLUDED")

    # --- the unrestricted series is algebraic too, at degree 2 --------------
    v, nul, hp, hr = guess("alg", HV, 2, 9)
    g.check(v == "CANDIDATE" and nul == 1,
            f"unrestricted HV-convex alg (2,9): nullity 1 (got {nul})")
    v, nul, _, _ = guess("alg", HV, 2, 8)
    g.check(v == "EXCLUDED" and nul == 0,
            "unrestricted HV-convex alg (2,8) EXCLUDED -- (2,9) is minimal")

    # --- the equation itself, exactly, over Q -------------------------------
    r = subprocess.run([sys.executable, FIND_ALG, "4", "22"],
                       capture_output=True, text=True)
    g.check(r.returncode == 0, f"dir4_perim_find_alg.py rc={r.returncode}")
    lines = [l for l in r.stdout.splitlines() if l.strip().startswith("q_")]
    g.check("rows failing over Z: 0 of 200" in r.stdout,
            "recovered quartic annihilates all 200 rows over Z")
    g.check(len(lines) == 5, f"five coefficient polynomials (got {len(lines)})")
    if len(lines) == 5:
        for j, line in enumerate(lines):
            g.check(parse_poly(line, 22) == QUARTIC[j],
                    f"q_{j}(t) matches the banked quartic")

    return g.verdict("DIR4-PERIM-ALG")


if __name__ == "__main__":
    sys.exit(main())
