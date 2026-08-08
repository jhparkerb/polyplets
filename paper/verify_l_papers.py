#!/usr/bin/env python3
"""Verify the printed numbers of the L papers against banked results.

    python3 paper/verify_l_papers.py          # run from anywhere

Covers paper/L1-diagonal-law.tex, paper/L3-lambda-bounds.tex,
paper/L4-not-dfinite.tex and paper/L6-perimeter-gradings.tex.  Read-only with respect to the .tex files: it parses
their tables and displayed constants and checks them against results/, against
an independent brute-force enumeration, and against each other.

Exact arithmetic only (stdlib Fraction); no external packages.  Exit 0 iff every
check passed and every RED control failed as it was supposed to.

RED-first (docs/engineering-standards.md).  A verifier that cannot fail proves
nothing, so five controls run alongside the checks and each one MUST be
rejected:

  R1  a ladder row with its certified value nudged up by one ulp
  R2  a psi-box widened by one degree
  R3  the A308359 quadratic evaluated at n = 2k, where the onset is sharp
  R4  a linear fit to the A308359 diagonal, which must miss the third point
  R5  the king diagonal formula evaluated one row below its proved onset
  R6  a min-end column claimed stable one rung before its onset

R3 and R5 are not bookkeeping: they are what puts the *onset* of the diagonal
law under test rather than merely its shape.
"""
import re
import sys
from collections import defaultdict
from fractions import Fraction as F
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAPER = ROOT / "paper"

failures = []
checks = 0
reds = 0


def ok(cond, what):
    global checks
    checks += 1
    if not cond:
        failures.append(what)


def red(cond_should_be_false, what):
    """A control: cond must be False, i.e. the bad thing must be rejected."""
    global checks, reds
    checks += 1
    reds += 1
    if cond_should_be_false:
        failures.append("RED CONTROL DID NOT FIRE: " + what)


def prints_number(src, value):
    """True iff `src` prints `value` as a number, not as a digit substring.

    `str(value) in src` is not this test and must never be used for it.  It was,
    until 2026-08-07, at three sites here, and tests/gate_l_paper_verifier.py
    exists because of what that let through: "58" is satisfied by the "6558" in
    a table entry, and "1", "2", "4", "9" are satisfied by any LaTeX document at
    all, so `all(str(d) in src for d in PSI_DEGREES)` could not fail.  Deleting
    the line of L4 that printed every psi-degree left the check green, and so
    did mistyping the last one.

    The guard is a digit boundary on both sides: a match may not be preceded or
    followed by another digit, and may not be preceded by a decimal point (so
    "114" does not match inside "3.114").
    """
    return re.search(r"(?<![\d.])" + re.escape(str(value)) + r"(?!\d)", src) is not None


def prints_together(src, values, window=240):
    """True iff `src` prints all of `values` as numbers within one `window`.

    Presence-anywhere is the wrong claim when a number occurs in the paper for
    more than one reason.  L1 prints 114 twice: once as the b=5 interval pair
    weight and once as a residue mod 5, four hundred lines apart.  So
    `prints_number(src, 114)` stays true even when the sentence that states the
    pair weights is mistyped -- measured, and the last mutation
    tests/gate_l_paper_verifier.py caught.  What the paper actually claims is
    that 58 and 114 are the b = 4, 5 weights *together*, and co-occurrence is
    the testable form of that.  The window is characters, so it survives
    rewording and rewrapping but not a typo at the statement site.
    """
    for m in re.finditer(r"(?<![\d.])" + re.escape(str(values[0])) + r"(?!\d)", src):
        near = src[m.start(): m.start() + window]
        if all(prints_number(near, v) for v in values[1:]):
            return True
    return False


def prints_sequence(src, values, sep=", "):
    """True iff `src` prints the whole sequence, in order, as one list.

    Checking the members one at a time cannot see a dropped line: every member
    of L6's [1, 6, 22, 68, 187, 470, 1106] occurs somewhere in L6 for unrelated
    reasons.  The list as a unit occurs once, where the paper states it.
    """
    return sep.join(str(v) for v in values) in src


def tex(name):
    p = PAPER / name
    if not p.exists():
        failures.append(f"missing manuscript {p}")
        return ""
    return p.read_text()


# ---------------------------------------------------------------------------
# L3 — the certified ladder, against results/strip_mu_certificates.log
# ---------------------------------------------------------------------------

def best_receipts():
    """Strongest PASS certificate per H, from the receipt log.

    The log is append-only and holds several receipts per H (re-runs, and
    deliberate re-certifications at different --digits).  The paper quotes the
    strongest one, so that is what we compare against.
    """
    log = ROOT / "results" / "strip_mu_certificates.log"
    if not log.exists():
        failures.append(f"missing {log}")
        return {}
    best = {}
    for line in log.read_text().splitlines():
        if "result=PASS" not in line:
            continue
        f = dict(kv.split("=", 1) for kv in line.split() if "=" in kv)
        try:
            H = int(f["H"])
            lo = F(f["mu_lower"])
        except (KeyError, ValueError):
            continue
        if H not in best or lo > best[H][0]:
            best[H] = (lo, f)
    return best


def check_l3_ladder():
    src = tex("L3-lambda-bounds.tex")
    if not src:
        return
    best = best_receipts()
    if not best:
        return

    body = src.split(r"\label{tab:ladder}")[0]
    rows = []
    for line in body.splitlines():
        m = re.match(
            r"\s*(\d+)\s*&\s*\\?t?e?x?t?b?f?\{?([\d.]+)\}?\s*&\s*([\d]+)\s*&"
            r"\s*([\d.]+)\s*&\s*(\d+)\s*&",
            line.replace(",", ""),
        )
        if m:
            rows.append((int(m.group(1)), F(m.group(2)), int(m.group(3)),
                         m.group(4), int(m.group(5))))
    ok(len(rows) == 16, f"tab:ladder should have 16 rows H=2..17, parsed {len(rows)}")

    for H, printed, states, mu_float, sweeps in rows:
        if H not in best:
            failures.append(f"tab:ladder H={H} has no PASS receipt")
            continue
        certified, f = best[H]
        ok(printed == certified,
           f"tab:ladder H={H}: printed {printed} != receipt {certified}")
        ok(states == int(f["states"]),
           f"tab:ladder H={H}: states {states} != receipt {f['states']}")
        ok(mu_float == f["mu_float"],
           f"tab:ladder H={H}: mu_float {mu_float} != receipt {f['mu_float']}")
        ok(sweeps == int(f["attempts"]),
           f"tab:ladder H={H}: sweeps {sweeps} != receipt {f['attempts']}")
        # The certificate is a FLOOR: it may never exceed what the search found.
        ok(printed <= F(f["mu_float"]),
           f"tab:ladder H={H}: certified {printed} exceeds float {f['mu_float']}")

    # R1: nudge one certified value up and require the comparison to reject it.
    if rows:
        H, printed, _, _, _ = rows[-1]
        red(printed + F(1, 10**7) <= best[H][0],
            f"a ladder value above the receipt at H={H}")

    # The headline bracket must be the ladder's top rung, not a rounder number.
    top = max(rows)[1] if rows else None
    ok(top == F("6.543"), f"L3 top rung should be 6.543, got {top}")
    flat = " ".join(src.split())
    ok(r"6.543 \;\le\; \lambda \;\le\; 9.3154" in flat,
       "L3 abstract must state the bracket 6.543 <= lambda <= 9.3154")
    ok(r"\dfrac{6543}{1000} \;\le\; \lambda \;\le\; \dfrac{20000}{2147}" in flat,
       "L3 theorem must state the bracket as exact rationals")


def check_l3_constants():
    import math
    src = tex("L3-lambda-bounds.tex")
    if not src:
        return
    # Crude bound: 5^5/4^4.
    ok(F(5**5, 4**4) == F(3125, 256), "5^5/4^4 = 3125/256")
    ok(abs(float(F(3125, 256)) - 12.2) < 0.06, "3125/256 rounds to 12.2")
    ok(r"5^5/4^4" in src, "L3 must print the crude bound as 5^5/4^4")

    # Upper certificates: the paper quotes x, so 1/x must give the bound -- and
    # a decimal in bound position must round UP, never truncate.  This is the
    # check that caught the repository's banked "9.3153", which is 20000/2147
    # truncated and so does not follow from the certificate.
    for x, quoted in ((F(2147, 20000), "9.3154"), (F(106251, 10**6), "9.4117")):
        inv = 1 / x
        ceil4 = F(math.ceil(inv * 10**4), 10**4)
        ok(ceil4 == F(quoted),
           f"1/({x}) rounds up to {quoted}, got {ceil4}")
        ok(F(quoted) >= inv, f"{quoted} must be >= 1/({x}) = {float(inv):.7f}")
        ok(quoted in src, f"L3 must print {quoted}")

    # R1b: the truncated form is NOT a valid upper bound and must be rejected.
    red(F("9.3153") >= 1 / F(2147, 20000),
        "the truncated decimal 9.3153 in upper-bound position")

    # The rook control that kills the two false shortcuts: both would give 4,
    # and the true polyomino growth constant exceeds it.
    ok(F(4**4, 3**3) > F(9, 1) and float(F(4**4, 3**3)) < 9.5,
       "4^4/3^3 is the ~9.48 the growth-tree shortcut would have given")
    ok(r"\lambda_{\text{polyomino}} \le 4" in src,
       "L3 must state the rook control explicitly")


# ---------------------------------------------------------------------------
# L4 — the exclusion boxes, from the psi-degrees
# ---------------------------------------------------------------------------

PSI_DEGREES = [1, 2, 4, 9, 29, 68, 181, 462, 1254, 3289]   # H = 1..10


def boxes_from(degrees):
    """The rule stated in L4: exclude (r, D) whenever at least r+1 certified
    levels have deg psi_H > D.  The widest excluded D at order r is therefore
    one below the (r+1)-th largest degree."""
    desc = sorted(degrees, reverse=True)
    return {r: desc[r] - 1 for r in range(len(desc))}


def check_l4_boxes():
    src = tex("L4-not-dfinite.tex")
    if not src:
        return

    # The list as a unit, not member by member: "1", "2", "4" and "9" are
    # satisfied by any LaTeX file, so the member-wise form could not fail.
    ok(prints_sequence(src, PSI_DEGREES),
       "L4 must print the psi-degree list " + ", ".join(map(str, PSI_DEGREES)))
    red(prints_sequence(src, PSI_DEGREES[:-1] + [PSI_DEGREES[-1] + 9]),
        "a psi-degree list with the last degree mistyped")

    full = boxes_from(PSI_DEGREES)
    for r, D in ((5, 28), (4, 67), (3, 180), (2, 461), (1, 1253), (0, 3288)):
        ok(full[r] == D, f"tab:psiboxes r<={r} should exclude D<={full[r]}, prints {D}")
        ok(f"D \\le {D}" in src or f"$D \\le {D}$" in src,
           f"L4 must print the box r<={r}, D<={D}")

    # The self-contained family uses only the irreducibility-certified levels.
    irr = boxes_from(PSI_DEGREES[:8])
    for r, D in ((4, 8), (3, 28), (2, 67), (1, 180), (0, 461)):
        ok(irr[r] == D, f"tab:irrboxes r<={r} should exclude D<={irr[r]}, prints {D}")

    # R2: a box one degree wider is not supported by the same data.
    red(full[3] >= 181, "a psi-box widened past the 4th largest degree")

    # psi-degree growth rate: the paper says ~2.7 per level, near sqrt(lambda).
    ratios = [PSI_DEGREES[i + 1] / PSI_DEGREES[i] for i in range(4, 9)]
    mean = sum(ratios) / len(ratios)
    ok(2.4 < mean < 2.9, f"psi-degree growth ~2.7, measured {mean:.2f}")


def check_l4_mu_agrees_with_l3():
    """The two papers print the same strip growth constants.  They are written
    independently and must not drift apart."""
    l3, l4 = tex("L3-lambda-bounds.tex"), tex("L4-not-dfinite.tex")
    if not (l3 and l4):
        return
    body = l4.split(r"\label{tab:mu}")[0]
    m = re.search(r"\$\\mu_H\$([^\\]*(?:\\\\)?)", body)
    row = None
    for line in body.splitlines():
        if line.strip().startswith(r"$\mu_H$"):
            row = line
    if row is None:
        failures.append("L4 tab:mu row not found")
        return
    vals = re.findall(r"[\d]+\.[\d]+", row)
    ok(len(vals) >= 8, f"L4 tab:mu should list several mu_H, found {len(vals)}")
    receipts = best_receipts()
    for i, v in enumerate(vals):
        H = i + 1
        if H == 1:
            # The height-1 strip is horizontal bars; mu_1 = 1 exactly, and no
            # certificate is issued for it.
            ok(float(v) == 1.0, f"L4 tab:mu says mu_1 = {v}, should be 1.0")
            continue
        if H not in receipts:
            failures.append(f"L4 tab:mu H={H} has no receipt to check against")
            continue
        got, want = float(v), float(receipts[H][1]["mu_float"])
        # The table prints 5 decimals, rounded; allow half an ulp of that.
        ok(abs(got - want) <= 5e-6,
           f"L4 tab:mu H={H}: printed {v}, receipt {want}")
    del m


# ---------------------------------------------------------------------------
# L1 — the diagonal law, against the banked king triangle and an independent
#      brute-force enumeration of fixed polyominoes by bounding-box width
# ---------------------------------------------------------------------------

def king_triangle():
    p = ROOT / "results" / "triangle.txt"
    if not p.exists():
        failures.append(f"missing {p}")
        return {}
    T = {}
    for line in p.read_text().splitlines():
        if line.startswith("#") or not line.strip():
            continue
        parts = line.split()
        if len(parts) >= 3:
            T[(int(parts[0]), int(parts[1]))] = int(parts[2])
    return T


def check_l1_king_diagonals():
    src = tex("L1-diagonal-law.tex")
    T = king_triangle()
    if not src or not T:
        return

    nmax = max(n for n, _ in T)

    # k = 0: the pure walk, T(n,n) = b^(n-1) with b = 3.
    for n in range(1, min(nmax, 40) + 1):
        ok(T.get((n, n)) == 3 ** (n - 1), f"T({n},{n}) = 3^{n-1}")

    # k = 1: P_1(n) = 25n - 45, valid for n >= 2k+1 = 3.
    def P1(n):
        return 25 * n - 45

    for n in range(3, min(nmax, 40) + 1):
        want = P1(n) * 3 ** (n - 1 - 3)
        ok(T.get((n, n - 1)) == want, f"T({n},{n-1}) = (25n-45) 3^(n-4)")

    # R5: the onset is sharp, so the same formula must FAIL at n = 2k = 2.
    red(T.get((2, 1)) == P1(2) * 3 ** (2 - 1 - 3),
        "the k=1 diagonal formula one row below its proved onset")

    # k = 2: P_2(n) = (625 n^2 - 2459 n + 1134)/2, valid for n >= 5.
    def P2(n):
        return F(625 * n * n - 2459 * n + 1134, 2)

    for n in range(5, min(nmax, 40) + 1):
        want = P2(n) * 3 ** (n - 1 - 6)
        ok(F(T.get((n, n - 2), -1)) == want,
           f"T({n},{n-2}) = P_2(n) 3^(n-7)")

    # R5b: sharp at n = 2k = 4 as well.
    red(F(T.get((4, 2), -1)) == P2(4) * F(1, 3 ** 3),
        "the k=2 diagonal formula one row below its proved onset")

    # The paper prints P_2 as (625/2)n^2 - (2459/2)n + 567; 1134/2 = 567.
    ok(F(1134, 2) == 567, "P_2 constant term")
    ok(r"\tfrac{625}{2}n^2-\tfrac{2459}{2}n+567" in src.replace(" ", ""),
       "L1 must print the king k=2 form")

    # Leading coefficients: [n^k] P_k = W_pair^k / k!.
    for W, k, lead in ((25, 1, F(25)), (25, 2, F(625, 2)),
                       (4, 1, F(4)), (4, 2, F(8)), (4, 3, F(32, 3)),
                       (4, 4, F(32, 3)), (9, 1, F(9)), (9, 2, F(81, 2)),
                       (9, 3, F(243, 2))):
        fact = 1
        for i in range(2, k + 1):
            fact *= i
        ok(F(W ** k, fact) == lead,
           f"leading coefficient {W}^{k}/{k}! should be {lead}")


def fixed_polyominoes_by_width(nmax):
    """Independent brute force: fixed polyominoes of n cells by bounding-box
    width.  Deliberately naive -- growth from a canonical seed with a visited
    set of frozensets -- because its job is to disagree with the transfer
    machinery if the transfer machinery is wrong."""
    seen = {1: {frozenset({(0, 0)})}}
    for n in range(2, nmax + 1):
        cur = set()
        for shape in seen[n - 1]:
            for (x, y) in shape:
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    c = (x + dx, y + dy)
                    if c in shape:
                        continue
                    grown = shape | {c}
                    mx = min(a for a, _ in grown)
                    my = min(b for _, b in grown)
                    cur.add(frozenset((a - mx, b - my) for a, b in grown))
        seen[n] = cur
    counts = defaultdict(int)
    for n, shapes in seen.items():
        for s in shapes:
            w = max(a for a, _ in s) - min(a for a, _ in s) + 1
            counts[(n, w)] += 1
    return counts


def check_l1_a308359():
    """Corollary: T(n,n-2) = 8n^2 - 51n + 86 for n >= 5 on the square lattice.

    Enumerated here from scratch rather than read off the OEIS entry, in the
    three stages the paper describes, so that a disagreement says where it
    lives."""
    src = tex("L1-diagonal-law.tex")
    if not src:
        return
    C = fixed_polyominoes_by_width(9)

    # Stage 0: row sums must be A001168.
    a001168 = [1, 2, 6, 19, 63, 216, 760, 2725, 9910]
    for n in range(1, 10):
        tot = sum(v for (m, _), v in C.items() if m == n)
        ok(tot == a001168[n - 1], f"fixed polyominoes a({n}) = {a001168[n-1]}")

    # Stage 1: the k=1 diagonal must reproduce the form A308359 records as
    # PROVED.  This is the step that certifies our object is their object.
    for n in range(3, 10):
        ok(C.get((n, n - 1)) == 4 * n - 8, f"square T({n},{n-1}) = 4n-8")

    # Stage 2: three in-onset values determine the quadratic, and it is theirs.
    def Q(n):
        return 8 * n * n - 51 * n + 86

    for n in range(5, 10):
        ok(C.get((n, n - 2)) == Q(n), f"square T({n},{n-2}) = 8n^2-51n+86")

    # R3: sharp onset -- the quadratic must miss at n = 2k = 4.
    red(C.get((4, 2)) == Q(4), "the A308359 quadratic below its proved onset")
    ok(C.get((4, 2)) == 9 and Q(4) == 10,
       f"the paper's control values: T(4,2)=9 vs quadratic 10, "
       f"got {C.get((4,2))} vs {Q(4)}")

    # R4: a linear fit through n=5,6 must miss at n=7.
    slope = Q(6) - Q(5)
    lin7 = Q(5) + 2 * slope
    red(lin7 == Q(7), "a linear fit to the A308359 diagonal")
    ok(lin7 == 105 and Q(7) == 121,
       f"the paper's control values: linear 105 vs true 121, got {lin7} vs {Q(7)}")

    # The paper's square k=3 form is checkable against A308359's own printed
    # triangle without running anything; check it against our enumeration too.
    def P3(n):
        return F(32, 3) * n ** 3 - 140 * n ** 2 + F(1960, 3) * n - 1090

    for n in range(7, 10):
        ok(F(C.get((n, n - 3), -1)) == P3(n), f"square T({n},{n-3}) = P_3(n)")
    ok(P3(7) == 282 and P3(8) == 638,
       f"the paper's spot values 282 and 638, got {P3(7)} and {P3(8)}")


def check_l6_min_end():
    """L6's king minimum-end ladder, against the p<=48 census.

    Reads the census cold and rebuilds the C(p,i) table, then checks the paper's
    two claims: the stabilised constants, and the onset p* = 4i + 8.  King pmin
    is always even, so no odd p is ever an isoperimetric perimeter: every
    positive odd-p census row must sit strictly above the pmin formula, and
    odd-p rows that are present must be genuine counts (a census that leaked
    partial rows would fill them with zeros)."""
    import math
    src = tex("L6-perimeter-gradings.tex")
    census = ROOT / "results" / "perimmin_square8_p48_r6.txt"
    if not src:
        return
    if not census.exists():
        failures.append(f"missing {census}")
        return

    A = {}
    for line in census.read_text().splitlines():
        if line.startswith("#") or not line.strip():
            continue
        n, p, c = (int(x) for x in line.split())
        A[(n, p)] = c

    # pmin on the king lattice is A235382 = 2*ceil(2*sqrt(n)) + 4.
    nmax = {}
    for n in range(1, 4000):
        q = 2 * math.ceil(2 * math.sqrt(n)) + 4
        if q <= 48:
            nmax[q] = max(nmax.get(q, 0), n)

    stable = [1, 6, 22, 68, 187, 470, 1106]
    # As a list: every member occurs somewhere in L6 for unrelated reasons, and
    # "1" and "6" occur in any document, so member-wise this could not fail.
    ok(prints_sequence(src, stable),
       "L6 must print the king p=0 mod 4 constants "
       + ", ".join(map(str, stable)))
    red(prints_sequence(src, stable[:-1] + [stable[-1] - 100]),
        "a min-end constant list with the last entry mistyped")

    # The constants, at every p where the paper says all seven have stabilised.
    for p in (32, 36, 40, 44, 48):
        got = [A.get((nmax[p] - i, p), 0) for i in range(7)]
        ok(got == stable, f"L6 tab:mincoeffs at p={p}: {got} != {stable}")

    # The onset law: column i takes its stable value first at p = 4i + 8.
    for i, want in enumerate(stable):
        onset = 4 * i + 8
        ok(A.get((nmax[onset] - i, onset), 0) == want,
           f"L6 onset: column i={i} should reach {want} at p={onset}")
        if onset - 4 in nmax:
            red(A.get((nmax[onset - 4] - i, onset - 4), 0) == want,
                f"column i={i} already stable one rung early, at p={onset-4}")

    # Odd p is never attained on the king lattice, so those columns are empty.
    odd = [p for (_, p) in A if p % 2 == 1 and p <= 48]
    ok(all(A[(n, p)] > 0 for (n, p) in A if p % 2 == 1) or not odd,
       "odd-p rows present in the census are genuine counts, not zeros")
    # Until 2026-08-07 (the second documented unfreeze) this site compared the
    # always-even pmin formula against odd p over a range of n -- a parity
    # tautology, green for ANY census content.  The claim is universally
    # quantified over the census itself: an animal with odd perimeter exists
    # only strictly above its area's pmin, so every positive odd-p row must sit
    # strictly above 2*ceil(2*sqrt(n)) + 4.  A row below that (like a claimed
    # odd pmin) is rejected.
    def odd_above_pmin(table):
        return all(p > 2 * math.ceil(2 * math.sqrt(n)) + 4
                   for (n, p), c in table.items() if p % 2 == 1 and c > 0)

    ok(odd_above_pmin(A),
       "no odd p is attained as king pmin -- the attainability claim")
    red(odd_above_pmin({**A, (5, 13): 7}),
        "a census row claiming the odd perimeter 13 attained at n=5, "
        "below pmin(5) = 14")


def check_l1_pair_weights():
    """W_pair is the slope of P_1 on every lattice, and 4, 9, 25 are NOT
    (b+1)^2 in general -- the paper says so and the numbers must agree."""
    src = tex("L1-diagonal-law.tex")
    if not src:
        return
    import math
    for b, W in ((1, 4), (2, 9), (3, 25)):
        r = math.isqrt(W)
        ok(r * r == W, f"the b<=3 coincidence: W_pair({b}) = {W} is a square")

    def Wpair_interval(b):
        return b ** 3 - F(b * (b + 1), 2) + 4

    for b, W in ((1, 4), (2, 9), (3, 25), (4, 58), (5, 114)):
        ok(Wpair_interval(b) == W, f"W_pair({b}) = {W} from the closed form")
    # ...and the squares stop at b = 3, which is the point of the remark.
    for b in (4, 5):
        W = int(Wpair_interval(b))
        r = math.isqrt(W)
        ok(r * r != W, f"W_pair({b}) = {W} is not a square")
    # Digit-bounded, and co-occurring: "58" as a bare substring is satisfied by
    # the "6558" in the six-lattice table, and 114 appears twice in L1 for two
    # different reasons, so neither containment nor presence-anywhere can see a
    # typo at the site that states them.
    ok(prints_together(src, [58, 114]),
       "L1 must print 58 and 114 together as the b = 4, 5 interval pair weights")
    ok(prints_number(src, 57),
       "L1 must print the corrected pair weight 57 for D = {-2,0,2}")

    # Unit controls on the matchers themselves, on synthetic input: these are
    # what was missing when the substring form shipped.
    red(prints_number("the entry 6558 and nothing else", 58),
        "a digit substring inside a larger number satisfying a number check")
    red(prints_number("a coefficient 3.114 appears", 114),
        "a digit substring after a decimal point satisfying a number check")
    red(prints_together("W = 58 here." + "x" * 400 + "and 114 far away", [58, 114]),
        "two numbers far apart satisfying a co-occurrence check")
    red(prints_sequence("1, 6, 22, 68, 187, 470, 1006", [1, 6, 22, 68, 187, 470, 1106]),
        "a mistyped list satisfying a sequence check")

    # Theorem B's two sharpness witnesses.
    ok(57 % 3 == 0, "D = {-2,0,2} realises the degenerate branch mod 3")
    ok(114 % 5 == 4, "interval b=5 gives w = 4, a unit but not 1, mod 5")
    ok(25 % 3 == 1 and 9 % 2 == 1, "king and hex both give w = 1")


# ---------------------------------------------------------------------------

def main():
    check_l3_ladder()
    check_l3_constants()
    check_l4_boxes()
    check_l4_mu_agrees_with_l3()
    check_l1_king_diagonals()
    check_l1_a308359()
    check_l1_pair_weights()
    check_l6_min_end()

    if failures:
        print(f"verify_l_papers: {len(failures)} FAILURE(S) of {checks} checks\n")
        for f in failures:
            print("  FAIL " + f)
        return 1
    print(f"verify_l_papers: all {checks} checks passed "
          f"({reds} of them RED controls, every one of which fired)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
