#!/usr/bin/env python3
"""P_k hunt for the dmirror strip triangle (Hall of Mirrors / Shrink Ray
follow-on): d(S, S+k) -- diagonal-symmetric king-animals with S+k cells and
bbox exactly SxS -- is QUASI-polynomial in S for fixed k, period 2 (an
off-diagonal cell and its mirror land together, so the defect combinatorics
split by S parity; measured: k=0 is the constant 2 = main + anti diagonal,
k=1 is S+6 / S+7 on the even/odd classes).

If enough diagonals pin, the expensive high-S strips of an n=33/34 run
(which only carry small k) come from closed forms instead of ~100-340GB
sweeps -- the P9..P15 trick transplanted from the Fixed height triangle.

Method (exact integer arithmetic throughout), per diagonal k and per parity
class (points stepped by 2 in S):
  1. load d(S, n) from per-strip farm outputs runs/sym*/dmirror.S*.out;
     duplicate (S, n) reports must agree;
  2. work on the largest gap-free block of the class; difference until the
     last DEG_WIN values of the D-th difference are equal => degree D;
  3. pin a Newton polynomial on the block's LAST D+1 points (deepest into
     the polynomial regime);
  4. walk BACKWARD to the onset S0 = smallest S from which the polynomial
     reproduces every exact value (points in [S0, pin) are holdout hits);
  5. verify FORWARD against any exact points beyond the block (e.g. the
     n=32 farm's S=27..32 strips, which arrive gap-separated from a
     maxn<=26 triangle).

Usage: dmirror_diagonals.py SYMDIR [SYMDIR ...]   e.g. runs/sym26 runs/sym32
"""
import glob
import os
import re
import sys
from fractions import Fraction

DEG_WIN = 3  # constant-tail witnesses required beyond the fitted degree


def load(symdirs):
    d = {}  # (S, n) -> count
    for sd in symdirs:
        for path in glob.glob(os.path.join(sd, "dmirror.S*.out")):
            S = int(re.search(r"dmirror\.S(\d+)\.out$", path).group(1))
            for ln in open(path):
                parts = ln.split()
                if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                    n, c = int(parts[0]), int(parts[1])
                    if d.setdefault((S, n), c) != c:
                        raise SystemExit(f"conflict at S={S} n={n}: "
                                         f"{d[(S, n)]} vs {c} ({path})")
    return d


def blocks(pts, step):
    """Split [(S, v)] (S ascending) into maximal runs with spacing `step`."""
    out = []
    for S, v in pts:
        if out and S == out[-1][-1][0] + step:
            out[-1].append((S, v))
        else:
            out.append([(S, v)])
    return out


def tail_degree(vals):
    row, deg = list(vals), 0
    while len(row) >= DEG_WIN + 1:
        if len(set(row[-(DEG_WIN + 1):])) == 1:
            return deg
        row = [b - a for a, b in zip(row, row[1:])]
        deg += 1
    return None


def newton_fit(pts):
    """Exact polynomial through pts [(S, v)]; returns integer-eval callable."""
    xs = [Fraction(S) for S, _ in pts]
    fd = [[Fraction(v) for _, v in pts]]
    for j in range(1, len(pts)):
        fd.append([(fd[-1][i + 1] - fd[-1][i]) / (xs[i + j] - xs[i])
                   for i in range(len(fd[-1]) - 1)])
    coef = [row[0] for row in fd]

    def ev(S):
        acc, prod = Fraction(0), Fraction(1)
        for j, c in enumerate(coef):
            acc += c * prod
            prod *= S - xs[j]
        assert acc.denominator == 1, f"non-integer P(S={S})"
        return acc.numerator

    std = [Fraction(0)] * len(coef)  # expand to standard basis
    prod = [Fraction(1)]
    for j, c in enumerate(coef):
        for i, p in enumerate(prod):
            std[i] += c * p
        prod = [Fraction(0)] + prod
        for i in range(len(prod) - 1):
            prod[i] -= xs[j] * prod[i + 1]
    return ev, std


def poly_str(std):
    terms = []
    for i in range(len(std) - 1, -1, -1):
        c = std[i]
        if not c:
            continue
        s = f"{c}" if i == 0 else (f"{c}*S" if i == 1 else f"{c}*S^{i}")
        terms.append(s)
    return " + ".join(terms).replace("+ -", "- ") or "0"


def main():
    if len(sys.argv) < 2:
        raise SystemExit("usage: dmirror_diagonals.py SYMDIR [SYMDIR ...]")
    d = load(sys.argv[1:])
    kmax = max(n - S for S, n in d)
    smax_all = max(S for S, _ in d)
    print(f"triangle: {len(d)} (S,n) values, k=0..{kmax}, S<={smax_all}")
    fits = {}  # (k, parity) -> (degree, S0, ev)
    for k in range(kmax + 1):
        pts = sorted((S, c) for (S, n), c in d.items() if n - S == k)
        for par in (0, 1):
            cls = [(S, c) for S, c in pts if S % 2 == par]
            if not cls:
                continue
            blk = max(blocks(cls, 2), key=len)
            beyond = [(S, c) for S, c in cls if S > blk[-1][0]]
            tag = f"k={k:2d} S%2={par}"
            if len(blk) < DEG_WIN + 2:
                print(f"{tag}: only {len(blk)} block points -- skipped")
                continue
            deg = tail_degree([c for _, c in blk])
            if deg is None:
                print(f"{tag}: {len(blk)} points, no constant tail "
                      f"(degree > {len(blk) - DEG_WIN - 1} or pre-onset)")
                continue
            pin = blk[-(deg + 1):]
            ev, std = newton_fit(pin)
            s0 = pin[0][0]
            for S, c in reversed(blk[:-(deg + 1)]):
                if ev(S) != c:
                    break
                s0 = S
            hold = (pin[0][0] - s0) // 2
            fwd = ""
            if beyond:
                ok = all(ev(S) == c for S, c in beyond)
                fwd = (f", FORWARD {'CONFIRMED' if ok else 'FAILED'} at "
                       f"S={[S for S, _ in beyond]}")
                if not ok:
                    for S, c in beyond:
                        if ev(S) != c:
                            print(f"{tag}:   P({S})={ev(S)} != exact {c}")
            print(f"{tag}: degree {deg}, pin S={pin[0][0]}..{pin[-1][0]}, "
                  f"exact from S0={s0} ({hold} holdout hits){fwd}")
            print(f"       P(S) = {poly_str(std)}")
            fits[(k, par)] = (deg, s0, ev)
    print()
    print(f"pinned: {len(fits)} class-polynomials across "
          f"k={sorted(set(k for k, _ in fits))}")


if __name__ == "__main__":
    main()
