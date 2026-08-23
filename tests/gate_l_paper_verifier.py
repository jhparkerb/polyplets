#!/usr/bin/env python3
"""Gate: the kill matrix for paper/verify_l_papers.py.

RED-first, and it is a gate on the *verifier*, not on the papers.  PROTOCOL
Amendment 1 (docs/reviews/l-trim/PROTOCOL.md): confidence in a checker is a
demonstrated kill, never a count.  This file pairs every ok() site in
paper/verify_l_papers.py with the specific corruption that has been watched
turning it red, runs every corruption, and fails if any pairing stops holding.

Why it exists: until 2026-08-07 three manuscript checks were written as
`str(value) in src`, plain substring containment, so "58" was satisfied by the
"6558" in a table entry and the psi-degree list check could not fail at all.
Twelve manuscript mutations measured that; six sailed through.  The verifier
was repaired (the first documented unfreeze) and this gate keeps the standard:
a check is trusted only if a specific corruption has turned it red.

The verifier has 51 ok() sites and 15 red() control sites (20 red instances,
some in loops).  Kill mechanisms, in preference order:

  mut:<id>    a manuscript mutation applied to a temp copy of the papers --
              a plausible error: a digit typed wrong, a line lost in a trim
  res:<id>    a corrupted temp copy of a banked results file the verifier
              recomputes against (results/ inputs, unreachable from the .tex)
  patch:<id>  a monkeypatched internal input -- corrupted enumeration,
              corrupted module constant, corrupted Fraction arithmetic --
              for recomputation sites no external file reaches
  red:<name>  an existing RED control inside the verifier that feeds the same
              predicate its corrupted value on every run; baseline enforces
              that it fired
  VACUOUS     no corruption constructible from outside the frozen file turns
              the site red.  Tolerated with a loud WARNING, never silently.

The matrix is the SITES table below: one row per ok() site, in verifier
source order, each carrying its kill(s) and the failure-message fragment that
attributes a detection to that site and not to a neighbour.  RED_SITES lists
the negative controls, which corrupt their own inputs on every verifier run;
the baseline run (which must be clean) is the proof each of them fired.

VACUOUS findings, reported prominently (they trigger the documented unfreeze
procedure; this gate only tolerates and warns):

  a308.linear-ctrl, pw.squares, pw.mod3, pw.mod5, pw.units -- closed integer
      arithmetic over literals inside the frozen verifier (e.g. ok(57%3==0)).
      No injectable input exists: int arithmetic cannot be monkeypatched and
      the literals live in the checksum-pinned file.  These pin the prose's
      arithmetic against verifier-source typos only; the freeze is their
      guard.  Corruptions tried: the bad-Fraction patch (does not reach int
      ops), manuscript mutation (they read no manuscript).

Formerly VACUOUS, repaired: l6.odd-attain compared the always-even pmin
formula against odd p -- a parity tautology, green for ANY census content;
the demo run `census-oddp-claimed` (a census row claiming odd perimeter 13
IS attained, count 7) left the verifier green.  The second documented
unfreeze (2026-08-07) rewrote the site as a universally-quantified check
over census entries -- every positive odd-p row strictly above the pmin
formula -- and census-oddp-claimed is now a REQUIRED kill below.

Everything runs on temp copies: the manuscripts on disk, results/ files and
the verifier itself are never modified.

    python3 tests/gate_l_paper_verifier.py            # gate
    python3 tests/gate_l_paper_verifier.py -v         # per-run detail

Exit 0 iff the baseline is clean, every listed kill is detected (its
site-attributing fragment appears among the failures of its run), every
mutation target still exists, and any vacuity demo stays green.
"""

import importlib.util
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAPER = ROOT / "paper"
VERIFIER = PAPER / "verify_l_papers.py"

# Enumerated, not frozen.  The 2026-08-23 contraction merged four manuscripts
# into their partners (docs/l-corpus-contraction.md) and a hardcoded list turned
# that into a FileNotFoundError in this gate's setup, which is a crash rather
# than a verdict.  The gate copies whatever manuscripts exist; the mutation
# matrix below names the sites it perturbs, and a site in a manuscript that is
# gone is caught by the matrix's own pairing assertions, not by a missing file.
L_PAPERS = sorted(
    (p.name for p in PAPER.glob("L[0-9]*.tex")),
    key=lambda n: int(n.split("-")[0][1:]),
)

RESULTS_FILES = [
    "strip_mu_certificates.log",
    "triangle.txt",
    "perimmin_square8_p48_r6.txt",
]

# ---------------------------------------------------------------------------
# Manuscript mutations.  id -> (why, [(paper, old, new), ...]).
# `new` of None deletes the line containing `old` -- how a trim loses a
# constant.  Multi-edit mutations exist because prints_number() is
# presence-anywhere: a value printed at two sites must be corrupted at both.
# ---------------------------------------------------------------------------

MUTATIONS = {
    "psi-degrees-dropped": (
        "L4 loses the line printing every psi-degree the boxes are built from",
        [("L4-not-dfinite.tex",
          "1, 2, 4, 9, 29, 68, 181, 462, 1254, 3289", None)]),

    "psi-degree-typo": (
        "L4 prints 3298 for the H=10 psi-degree instead of 3289",
        [("L4-not-dfinite.tex",
          "1, 2, 4, 9, 29, 68, 181, 462, 1254, 3289",
          "1, 2, 4, 9, 29, 68, 181, 462, 1254, 3298")]),

    "psi-box-typo": (
        "L4 prints an exclusion box one degree narrower than the data supports",
        [("L4-not-dfinite.tex", r"D \le 3288", r"D \le 3287")]),

    "pair-weights-dropped": (
        "L1 loses the line printing the corrected interval pair weights",
        [("L1-diagonal-law.tex", r"$\Wp = 58$ and $114$", None)]),

    "pair-weight-typo": (
        "L1 prints 115 for the b=5 interval pair weight instead of 114",
        [("L1-diagonal-law.tex", r"$\Wp = 58$ and $114$",
          r"$\Wp = 58$ and $115$")]),

    "pair-weight-57-typo": (
        "L1 prints 56 for the D={-2,0,2} pair weight at both places it appears",
        [("L1-diagonal-law.tex", r"$\Wp = 57$ for", r"$\Wp = 56$ for"),
         ("L1-diagonal-law.tex", r"$\Wp = 57 \equiv", r"$\Wp = 56 \equiv")]),

    "min-end-dropped": (
        "L6 loses the line printing the stabilised king min-end constants",
        [("L6-perimeter-gradings.tex", "$1, 6, 22, 68, 187, 470, 1106$", None)]),

    "min-end-typo": (
        "L6 prints 1006 for the seventh min-end constant instead of 1106",
        [("L6-perimeter-gradings.tex", "$1, 6, 22, 68, 187, 470, 1106$",
          "$1, 6, 22, 68, 187, 470, 1006$")]),

    "crude-bound-typo": (
        "L3 prints the crude bound with the wrong exponent",
        [("L3-lambda-bounds.tex", "5^5/4^4", "5^5/4^5")]),

    "upper-certificate-typo": (
        "L3 prints an upper certificate that its own rational does not round to",
        [("L3-lambda-bounds.tex", "9.4117", "9.4118")]),

    "polyomino-bound-dropped": (
        "L3 loses the statement of the false polyomino bound it exists to correct",
        [("L3-lambda-bounds.tex", r"$\lambda_{\text{polyomino}} \le 4$", None)]),

    "king-quadratic-typo": (
        "L1 prints 568 for P_2's constant term instead of 567",
        [("L1-diagonal-law.tex",
          r"\tfrac{625}{2}n^2-\tfrac{2459}{2}n+567",
          r"\tfrac{625}{2}n^2-\tfrac{2459}{2}n+568")]),

    "ladder-certified-typo": (
        "L3's top certified rung mistyped 6.543 -> 6.544 everywhere it appears",
        [("L3-lambda-bounds.tex", "6.543", "6.544")]),

    "ladder-row-dropped": (
        "L3 loses the H=12 row of the certified ladder in an edit",
        [("L3-lambda-bounds.tex", "6.2191246", None)]),

    "ladder-states-typo": (
        "L3 prints 853465 boundary states for H=15 instead of 853466",
        [("L3-lambda-bounds.tex", "853466", "853465")]),

    "ladder-mufloat-typo": (
        "L3 prints a search float the receipt log does not contain",
        [("L3-lambda-bounds.tex", "6.443540832", "6.443540831")]),

    "ladder-sweeps-typo": (
        "L3 prints 19 sweeps for H=14 where the receipt says 18",
        [("L3-lambda-bounds.tex", "6.380034445 & 18", "6.380034445 & 19")]),

    "ladder-floor-violation": (
        "L3 certifies H=16 above what the search found -- a floor over its float",
        [("L3-lambda-bounds.tex", "6.4984", "6.4986")]),

    "rational-bracket-typo": (
        "L3's theorem states the exact upper rational with a wrong denominator",
        [("L3-lambda-bounds.tex", r"\dfrac{20000}{2147}", r"\dfrac{20000}{2148}")]),

    "mu-row-truncated": (
        "L4's tab:mu row loses its last two entries",
        [("L4-not-dfinite.tex", "& 5.65337 & 5.84046", "")]),

    "mu1-typo": (
        "L4 prints 1.5 for mu_1, which is exactly 1",
        [("L4-not-dfinite.tex", r"$\mu_H$ & 1.0", r"$\mu_H$ & 1.5")]),

    "mu-row-typo": (
        "L4 prints 5.84047 for mu_9 where the receipt rounds to 5.84046",
        [("L4-not-dfinite.tex", "5.84046", "5.84047")]),
}

# ---------------------------------------------------------------------------
# Corrupted banked-results copies, for sites that recompute against results/
# files the manuscripts cannot reach.  Each edits a temp copy of one file.
# ---------------------------------------------------------------------------


def _bump_counts(path, keys):
    """In a 'a b count' table file, add 1 to count on the rows keyed (a, b)."""
    out = []
    hit = 0
    for line in path.read_text().splitlines(keepends=True):
        parts = line.split()
        if not line.startswith("#") and len(parts) == 3 and \
                (int(parts[0]), int(parts[1])) in keys:
            parts[2] = str(int(parts[2]) + 1)
            line = " ".join(parts) + "\n"
            hit += 1
    # (loop bodies must not silently miss -- see assertion below)
        out.append(line)
    assert hit == len(keys), f"{path.name}: corrupted {hit} of {len(keys)} rows"
    path.write_text("".join(out))


def corrupt_triangle(results_dir):
    """The banked king triangle disagrees with the diagonal law at k=0,1,2."""
    _bump_counts(results_dir / "triangle.txt", {(10, 10), (11, 10), (12, 10)})


def corrupt_census(results_dir):
    """The min-end census: a stable column off by one at p=48, the i=6 onset
    cell off by one at p=32, and an odd-p row with a zero count."""
    p = results_dir / "perimmin_square8_p48_r6.txt"
    _bump_counts(p, {(121, 48), (43, 32)})
    p.write_text(p.read_text() + "5 13 0\n")


def census_oddp_claimed(results_dir):
    """A census row claiming the odd perimeter 13 IS attained at n=5, below
    pmin(5) = 14.  Formerly the vacuity demo for l6.odd-attain; since the
    second unfreeze repaired that site, this is a required kill."""
    p = results_dir / "perimmin_square8_p48_r6.txt"
    p.write_text(p.read_text() + "5 13 7\n")


RESULTS_RUNS = {
    "triangle-corrupt": corrupt_triangle,
    "census-corrupt": corrupt_census,
    "census-oddp-claimed": census_oddp_claimed,
}

# No current vacuity demos: l6.odd-attain, the only one, was repaired in the
# second documented unfreeze.  The machinery stays for the next finding.
VACUITY_DEMOS = {}

# ---------------------------------------------------------------------------
# Monkeypatched internal inputs, for recomputation sites no file reaches.
# ---------------------------------------------------------------------------


def patch_brute_force(vlp):
    """Corrupt the independent polyomino enumeration at the four cells the
    A308359 checks read: a row sum, the k=1 and k=2 diagonals, the onset
    control cell, and the cubic's first in-onset cell."""
    orig = vlp.fixed_polyominoes_by_width

    def corrupted(nmax):
        C = orig(nmax)
        for key in ((3, 2), (6, 4), (4, 2), (7, 4)):
            C[key] += 1
        return C

    vlp.fixed_polyominoes_by_width = corrupted


def patch_psi_irreducible(vlp):
    """Mistype the H=8 psi-degree (462 -> 463): moves both the full and the
    irreducibility-certified exclusion boxes off the paper's printed values."""
    vlp.PSI_DEGREES = [1, 2, 4, 9, 29, 68, 181, 463, 1254, 3289]


def patch_psi_growth(vlp):
    """Mistype the H=10 psi-degree tenfold (3289 -> 32890): the growth-rate
    band 2.4 < mean ratio < 2.9 must reject it."""
    vlp.PSI_DEGREES = [1, 2, 4, 9, 29, 68, 181, 462, 1254, 32890]


def patch_bad_fraction(vlp):
    """A Fraction whose arithmetic lies: equality inverted, float() high by
    0.1, multiplication off by 1/7, right-subtraction off by 6 (chosen so the
    b=4 pair weight 58 corrupts to the perfect square 64).  Every pinned-
    rational site the verifier computes through F must go red under it."""
    from fractions import Fraction

    class BadF(Fraction):
        __hash__ = Fraction.__hash__

        def __eq__(self, other):
            r = Fraction.__eq__(self, other)
            return r if r is NotImplemented else not r

        def __float__(self):
            return Fraction.__float__(self) + 0.1

        def __mul__(self, other):
            r = Fraction.__mul__(self, other)
            return r if r is NotImplemented else r + Fraction(1, 7)

        def __rsub__(self, other):
            r = Fraction.__rsub__(self, other)
            return r if r is NotImplemented else r + 6

    vlp.F = BadF


PATCH_RUNS = {
    "brute-force": patch_brute_force,
    "psi-irreducible": patch_psi_irreducible,
    "psi-growth": patch_psi_growth,
    "bad-fraction": patch_bad_fraction,
}

# ---------------------------------------------------------------------------
# THE KILL MATRIX.  One row per ok() site of verify_l_papers.py, in source
# order: (site, function, what the site asserts, [kills]).  A kill is
# (kind, run-id, fragment): the run must produce a failure containing the
# fragment, which is specific to this site's message template.  kind "red"
# cites a RED control already inside the verifier (baseline proves it fired);
# kind "VACUOUS" documents that no constructible corruption reaches the site.
# ---------------------------------------------------------------------------

SITES = [
    # -- check_l3_ladder ----------------------------------------------------
    ("l3ladder.rowcount", "check_l3_ladder",
     "tab:ladder parses to exactly 16 rows H=2..17",
     [("mut", "ladder-row-dropped", "should have 16 rows")]),
    ("l3ladder.certified", "check_l3_ladder",
     "each printed certified mu_H equals its strongest PASS receipt",
     [("mut", "ladder-certified-typo", "!= receipt"),
      ("red", "R1-ladder-nudge", None)]),
    ("l3ladder.states", "check_l3_ladder",
     "each printed state count equals the receipt's",
     [("mut", "ladder-states-typo", "states 853465 != receipt")]),
    ("l3ladder.mufloat", "check_l3_ladder",
     "each printed search float equals the receipt's",
     [("mut", "ladder-mufloat-typo", "mu_float 6.443540831 != receipt")]),
    ("l3ladder.sweeps", "check_l3_ladder",
     "each printed sweep count equals the receipt's attempts",
     [("mut", "ladder-sweeps-typo", "sweeps 19 != receipt")]),
    ("l3ladder.floor", "check_l3_ladder",
     "no certified value exceeds the float the search proposed",
     [("mut", "ladder-floor-violation", "exceeds float")]),
    ("l3ladder.toprung", "check_l3_ladder",
     "the ladder's top rung is 6.543 exactly",
     [("mut", "ladder-certified-typo", "top rung should be")]),
    ("l3ladder.bracket-abstract", "check_l3_ladder",
     "the abstract states 6.543 <= lambda <= 9.3154",
     [("mut", "ladder-certified-typo", "abstract must state")]),
    ("l3ladder.bracket-rational", "check_l3_ladder",
     "the theorem states the bracket as exact rationals",
     [("mut", "rational-bracket-typo", "exact rationals")]),

    # -- check_l3_constants -------------------------------------------------
    ("l3const.crude-arith", "check_l3_constants",
     "5^5/4^4 = 3125/256",
     [("patch", "bad-fraction", "5^5/4^4 = 3125/256")]),
    ("l3const.crude-round", "check_l3_constants",
     "3125/256 rounds to 12.2",
     [("patch", "bad-fraction", "rounds to 12.2")]),
    ("l3const.crude-print", "check_l3_constants",
     "L3 prints the crude bound as 5^5/4^4",
     [("mut", "crude-bound-typo", "must print the crude bound")]),
    ("l3const.ceil4", "check_l3_constants",
     "each quoted upper bound is 1/x rounded UP to 4 places",
     [("patch", "bad-fraction", "rounds up to")]),
    ("l3const.bound-direction", "check_l3_constants",
     "each quoted decimal is >= its exact rational (a valid upper bound)",
     [("red", "R1b-truncated-9.3153", None)]),
    ("l3const.quoted-print", "check_l3_constants",
     "L3 prints each certificate decimal",
     [("mut", "upper-certificate-typo", "L3 must print 9.4117")]),
    ("l3const.rook-arith", "check_l3_constants",
     "4^4/3^3 is the ~9.48 the growth-tree shortcut would give",
     [("patch", "bad-fraction", "growth-tree shortcut")]),
    ("l3const.rook-print", "check_l3_constants",
     "L3 states the rook control lambda_polyomino <= 4",
     [("mut", "polyomino-bound-dropped", "rook control")]),

    # -- check_l4_boxes -----------------------------------------------------
    ("l4boxes.psi-list", "check_l4_boxes",
     "L4 prints the ten psi-degrees as one ordered list",
     [("mut", "psi-degrees-dropped", "must print the psi-degree list"),
      ("mut", "psi-degree-typo", "must print the psi-degree list")]),
    ("l4boxes.full", "check_l4_boxes",
     "the six full exclusion boxes follow from the psi-degrees",
     [("patch", "psi-irreducible", "tab:psiboxes")]),
    ("l4boxes.box-print", "check_l4_boxes",
     "L4 prints each box 'r<=r, D<=D'",
     [("mut", "psi-box-typo", "must print the box")]),
    ("l4boxes.irr", "check_l4_boxes",
     "the five certified-only boxes follow from the first 8 degrees",
     [("patch", "psi-irreducible", "tab:irrboxes")]),
    ("l4boxes.growth", "check_l4_boxes",
     "the psi-degree growth ratio is ~2.7",
     [("patch", "psi-growth", "psi-degree growth")]),

    # -- check_l4_mu_agrees_with_l3 -----------------------------------------
    ("l4mu.width", "check_l4_mu_agrees_with_l3",
     "L4's tab:mu row lists at least 8 values",
     [("mut", "mu-row-truncated", "found 7")]),
    ("l4mu.mu1", "check_l4_mu_agrees_with_l3",
     "L4 prints mu_1 = 1.0 exactly",
     [("mut", "mu1-typo", "mu_1 = 1.5")]),
    ("l4mu.match", "check_l4_mu_agrees_with_l3",
     "each printed mu_H matches L3's receipt to half an ulp of 5 decimals",
     [("mut", "mu-row-typo", "printed 5.84047")]),

    # -- check_l1_king_diagonals --------------------------------------------
    ("l1king.k0", "check_l1_king_diagonals",
     "T(n,n) = 3^(n-1) against the banked triangle",
     [("res", "triangle-corrupt", "T(10,10) = 3^9")]),
    ("l1king.k1", "check_l1_king_diagonals",
     "T(n,n-1) = (25n-45) 3^(n-4) from its onset",
     [("res", "triangle-corrupt", "T(11,10) = (25n-45)"),
      ("red", "R5-below-onset", None)]),
    ("l1king.k2", "check_l1_king_diagonals",
     "T(n,n-2) = P_2(n) 3^(n-7) from its onset",
     [("res", "triangle-corrupt", "T(12,10) = P_2(n)"),
      ("red", "R5b-below-onset", None)]),
    ("l1king.p2const", "check_l1_king_diagonals",
     "P_2's constant term 1134/2 = 567",
     [("patch", "bad-fraction", "P_2 constant term")]),
    ("l1king.k2-print", "check_l1_king_diagonals",
     "L1 prints the king k=2 quadratic verbatim",
     [("mut", "king-quadratic-typo", "must print the king k=2 form")]),
    ("l1king.leading", "check_l1_king_diagonals",
     "[n^k] P_k = W_pair^k / k! for nine (W,k) pairs",
     [("patch", "bad-fraction", "leading coefficient")]),

    # -- check_l1_a308359 ---------------------------------------------------
    ("a308.rowsums", "check_l1_a308359",
     "the independent enumeration's row sums are A001168",
     [("patch", "brute-force", "fixed polyominoes a(3)")]),
    ("a308.k1", "check_l1_a308359",
     "square T(n,n-1) = 4n-8 -- the step certifying our object is theirs",
     [("patch", "brute-force", "T(3,2) = 4n-8")]),
    ("a308.quad", "check_l1_a308359",
     "square T(n,n-2) = 8n^2-51n+86 in onset",
     [("patch", "brute-force", "T(6,4) = 8n^2-51n+86"),
      ("red", "R3-below-onset", None)]),
    ("a308.onset-ctrl", "check_l1_a308359",
     "the paper's onset control values T(4,2)=9 vs quadratic 10",
     [("patch", "brute-force", "T(4,2)=9 vs quadratic")]),
    ("a308.linear-ctrl", "check_l1_a308359",
     "the paper's linear-fit control values 105 vs 121",
     [("VACUOUS", "int-pin", None)]),
    ("a308.cubic", "check_l1_a308359",
     "square T(n,n-3) = P_3(n) in onset",
     [("patch", "brute-force", "T(7,4) = P_3(n)")]),
    ("a308.cubic-spot", "check_l1_a308359",
     "the paper's spot values P_3(7)=282, P_3(8)=638",
     [("patch", "bad-fraction", "spot values 282 and 638")]),

    # -- check_l1_pair_weights ----------------------------------------------
    ("pw.squares", "check_l1_pair_weights",
     "W_pair(b) is a perfect square for b <= 3",
     [("VACUOUS", "int-pin", None)]),
    ("pw.closed-form", "check_l1_pair_weights",
     "W_pair(b) = b^3 - b(b+1)/2 + 4 gives 4, 9, 25, 58, 114",
     [("patch", "bad-fraction", "from the closed form")]),
    ("pw.nonsquare", "check_l1_pair_weights",
     "W_pair(4), W_pair(5) are not squares -- the remark's point",
     [("patch", "bad-fraction", "= 64 is not a square")]),
    ("pw.cooccur", "check_l1_pair_weights",
     "L1 prints 58 and 114 together at the statement site",
     [("mut", "pair-weights-dropped", "58 and 114 together"),
      ("mut", "pair-weight-typo", "58 and 114 together")]),
    ("pw.print57", "check_l1_pair_weights",
     "L1 prints the corrected pair weight 57",
     [("mut", "pair-weight-57-typo", "corrected pair weight 57")]),
    ("pw.mod3", "check_l1_pair_weights",
     "57 = 0 mod 3 (Theorem B degenerate-branch witness)",
     [("VACUOUS", "int-pin", None)]),
    ("pw.mod5", "check_l1_pair_weights",
     "114 = 4 mod 5 (unit-but-not-1 witness)",
     [("VACUOUS", "int-pin", None)]),
    ("pw.units", "check_l1_pair_weights",
     "king and hex give w = 1",
     [("VACUOUS", "int-pin", None)]),

    # -- check_l6_min_end ---------------------------------------------------
    ("l6.stable-list", "check_l6_min_end",
     "L6 prints the seven stabilised constants as one list",
     [("mut", "min-end-dropped", "L6 must print the king"),
      ("mut", "min-end-typo", "L6 must print the king")]),
    ("l6.stable-cols", "check_l6_min_end",
     "the census reproduces all seven constants at p = 32..48",
     [("res", "census-corrupt", "tab:mincoeffs at p=48")]),
    ("l6.onset", "check_l6_min_end",
     "column i reaches its stable value first at p = 4i+8",
     [("res", "census-corrupt", "onset: column i=6"),
      ("red", "Ronset-one-rung-early", None)]),
    ("l6.odd-counts", "check_l6_min_end",
     "odd-p census rows, where present, are genuine counts not zeros",
     [("res", "census-corrupt", "genuine counts")]),
    ("l6.odd-attain", "check_l6_min_end",
     "every positive odd-p census row sits strictly above the pmin formula",
     [("res", "census-oddp-claimed", "the attainability claim"),
      ("red", "Roddp-below-pmin", None)]),
]

# The verifier's own negative controls: each corrupts its input on every run
# and main() fails unless every one fired.  The clean baseline run is
# therefore the proof of all 15 sites (20 instances; two are in loops).
RED_SITES = [
    ("R1-ladder-nudge", "check_l3_ladder",
     "a ladder value one ulp above its receipt is rejected"),
    ("R1b-truncated-9.3153", "check_l3_constants",
     "the truncated decimal 9.3153 is rejected in upper-bound position"),
    ("Rpsi-mistyped-list", "check_l4_boxes",
     "a psi-degree list with the last degree mistyped is not found in L4"),
    ("R2-widened-box", "check_l4_boxes",
     "a box one degree wider than the 4th largest degree is rejected"),
    ("R5-below-onset", "check_l1_king_diagonals",
     "the k=1 diagonal formula fails at n = 2k = 2"),
    ("R5b-below-onset", "check_l1_king_diagonals",
     "the k=2 diagonal formula fails at n = 2k = 4"),
    ("R3-below-onset", "check_l1_a308359",
     "the A308359 quadratic fails at n = 2k = 4"),
    ("R4-linear-fit", "check_l1_a308359",
     "a linear fit through n=5,6 misses at n=7"),
    ("Rpair-substring", "check_l1_pair_weights",
     "'58' inside '6558' does not satisfy a number check (synthetic)"),
    ("Rpair-decimal", "check_l1_pair_weights",
     "'114' inside '3.114' does not satisfy a number check (synthetic)"),
    ("Rpair-window", "check_l1_pair_weights",
     "58 and 114 four hundred characters apart do not co-occur (synthetic)"),
    ("Rpair-sequence", "check_l1_pair_weights",
     "a mistyped list does not satisfy a sequence check (synthetic)"),
    ("Rminend-mistyped-list", "check_l6_min_end",
     "a min-end list with the last entry mistyped is not found in L6"),
    ("Ronset-one-rung-early", "check_l6_min_end",
     "no column is stable one rung before its onset (6 instances)"),
    ("Roddp-below-pmin", "check_l6_min_end",
     "a synthetic census row claiming odd p=13 attained at n=5 is rejected"),
]


# ---------------------------------------------------------------------------
# Harness.
# ---------------------------------------------------------------------------


def load_verifier():
    """Import verify_l_papers.py fresh, so module globals start clean."""
    spec = importlib.util.spec_from_file_location("vlp_%d" % load_verifier.n, VERIFIER)
    load_verifier.n += 1
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


load_verifier.n = 0


def run_verifier(paper_dir, results_root=None, patch=None):
    """Run the verifier against paper_dir (and optionally a corrupted results
    tree or a monkeypatch).  Returns (failures, checks)."""
    vlp = load_verifier()
    vlp.PAPER = Path(paper_dir)
    if results_root is not None:
        vlp.ROOT = Path(results_root)
    if patch is not None:
        patch(vlp)
    vlp.print = lambda *a, **k: None
    vlp.main()
    return list(vlp.failures), vlp.checks


def apply_mutation(paper_dir, edits):
    """Apply one mutation's edits to the copy in paper_dir.
    Returns the description of the first stale edit, or None if all applied."""
    for paper, old, new in edits:
        p = Path(paper_dir) / paper
        text = p.read_text()
        if old not in text:
            return f"{old!r} not found in {paper}"
        if new is None:
            kept = [ln for ln in text.splitlines(keepends=True) if old not in ln]
            p.write_text("".join(kept))
        else:
            p.write_text(text.replace(old, new))
    return None


def main():
    verbose = "-v" in sys.argv
    if not VERIFIER.exists():
        print(f"gate_l_paper_verifier: {VERIFIER} not found")
        return 1

    # Group the matrix's kills by run.
    expectations = {}          # run id -> [(site, fragment)]
    red_cited = set()
    vacuous = []               # (site, reason)
    for site, fn, claim, kills in SITES:
        for kind, run_id, fragment in kills:
            if kind in ("mut", "res", "patch"):
                expectations.setdefault((kind, run_id), []).append((site, fragment))
            elif kind == "red":
                red_cited.add(run_id)
            elif kind == "VACUOUS":
                vacuous.append((site, run_id))
    unknown_red = red_cited - {r[0] for r in RED_SITES}
    assert not unknown_red, f"matrix cites unknown RED controls: {unknown_red}"
    for run_id in MUTATIONS:
        assert ("mut", run_id) in expectations, f"mutation {run_id} unpaired in matrix"
    for run_id in RESULTS_RUNS:
        assert ("res", run_id) in expectations, f"results run {run_id} unpaired in matrix"
    for run_id in PATCH_RUNS:
        assert ("patch", run_id) in expectations, f"patch {run_id} unpaired in matrix"

    problems = []              # (run, site, what went wrong)
    killed = set()

    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        clean = td / "clean"
        clean.mkdir()
        for n in L_PAPERS:
            shutil.copy2(PAPER / n, clean / n)

        # Baseline: clean papers, real results.  Must pass -- and a pass IS
        # the demonstration that all 19 RED-control instances fired, because
        # a red that does not fire is itself a failure.
        base_failures, base_checks = run_verifier(clean)
        if base_failures:
            print("gate_l_paper_verifier: the UNMUTATED papers already fail; "
                  "fix that before trusting this gate")
            for f in base_failures:
                print("  " + f)
            return 1
        print(f"  baseline     {base_checks} checks clean; all "
              f"{len(RED_SITES)} RED-control sites fired")

        def check_run(kind, run_id, failures):
            expected = expectations[(kind, run_id)]
            blob = "\n".join(failures)
            missed = [(site, frag) for site, frag in expected if frag not in blob]
            for site, frag in expected:
                if frag in blob:
                    killed.add(site)
            if missed:
                for site, frag in missed:
                    problems.append((run_id, site, f"no failure contained {frag!r}"))
                print(f"  UNDETECTED   {run_id}: " +
                      ", ".join(site for site, _ in missed))
            else:
                sites = ", ".join(site for site, _ in expected)
                print(f"  detected     {run_id} -> {sites}" if verbose
                      else f"  detected     {run_id}")

        # Manuscript mutations, each on its own copy of the papers.
        for run_id, (why, edits) in MUTATIONS.items():
            work = td / ("mut-" + run_id)
            shutil.copytree(clean, work)
            stale = apply_mutation(work, edits)
            if stale:
                for site, _ in expectations[("mut", run_id)]:
                    problems.append((run_id, site, "STALE mutation: " + stale))
                print(f"  STALE        {run_id}: {stale}")
                continue
            failures, _ = run_verifier(work)
            check_run("mut", run_id, failures)

        # Corrupted banked-results copies, papers clean.
        def results_tree(tag, corrupt):
            root = td / ("res-" + tag)
            (root / "results").mkdir(parents=True)
            for n in RESULTS_FILES:
                shutil.copy2(ROOT / "results" / n, root / "results" / n)
            corrupt(root / "results")
            return root

        for run_id, corrupt in RESULTS_RUNS.items():
            failures, _ = run_verifier(clean, results_root=results_tree(run_id, corrupt))
            check_run("res", run_id, failures)

        # Monkeypatched internals, papers and results clean.
        for run_id, patch in PATCH_RUNS.items():
            failures, _ = run_verifier(clean, patch=patch)
            check_run("patch", run_id, failures)

        # Vacuity demos: the corruption that SHOULD kill the site, staying
        # green.  A red here means the site is no longer vacuous and the
        # matrix (and the unfreeze finding) is stale.
        for run_id, (corrupt, site) in VACUITY_DEMOS.items():
            failures, _ = run_verifier(clean, results_root=results_tree(run_id, corrupt))
            if failures:
                problems.append((run_id, site,
                                 "vacuity demo went RED -- site is killable, "
                                 "matrix is stale: " + failures[0]))
                print(f"  MATRIX-STALE {run_id}: verifier went red")
            else:
                print(f"  demonstrated {run_id}: verifier stayed green "
                      f"(vacuity of {site} confirmed)")

    # Sites killed only by a RED control the baseline proved.
    for site, fn, claim, kills in SITES:
        if any(k[0] == "red" for k in kills):
            killed.add(site)

    print()
    ok_sites = len(SITES)
    vac_sites = {s for s, _ in vacuous}
    killable = ok_sites - len(vac_sites)
    n_runs = len(MUTATIONS) + len(RESULTS_RUNS) + len(PATCH_RUNS)

    if problems:
        print(f"gate_l_paper_verifier: {len(problems)} kill(s) NOT demonstrated\n")
        for run_id, site, what in problems:
            print(f"  MISS  {site} via {run_id}")
            print(f"        {what}")
        print("\nA check that cannot fail is not a check.")
        return 1

    print(f"gate_l_paper_verifier: {len(killed & (set(s for s, _, _, _ in SITES) - vac_sites))}"
          f"/{killable} killable ok-sites killed "
          f"({n_runs} corruption runs: {len(MUTATIONS)} manuscript, "
          f"{len(RESULTS_RUNS)} results, {len(PATCH_RUNS)} patch); "
          f"{len(RED_SITES)}/{len(RED_SITES)} RED-control sites fired in baseline")
    for site, reason in sorted(set(vacuous)):
        detail = ("closed integer arithmetic over literals in the frozen "
                  "verifier; no reachable input")
        print(f"  WARNING: VACUOUS site {site} [{reason}] -- {detail}")
    print(f"  ({len(vac_sites)} of {ok_sites} ok-sites VACUOUS -- tolerated, "
          f"see docstring; a vacuous site is an unfreeze finding, not a gate failure)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
