#!/usr/bin/env python3
"""Integer-relation search for the (dir4, HV-convex)/HV-convex amplitude ratio.

results/subclasses.md Table B ran this at 54 digits and found
nothing in any in-capacity box (degree <= 12 at height <= 1e2, <= 5 at 1e4,
<= 3 at 1e6, <= 2 at 1e8).  The digit count is what bounds the boxes: a
relation of degree d and height H is only detectable when its CAPACITY
(d+1)*log10(H) sits well inside the available digits, so more digits buy
strictly larger boxes and nothing else does.

experiments/amplitude_feed_vectors.py raised the count from 54, so this rerun
uses the same capacity rule to enlarge every box, and adds two searches Table B
could not afford:

  * over Q(mu): PSLQ on { mu^i r^j }, i <= I, j <= J.  mu is the shared growth
    constant; r might be algebraic over Q(mu) while transcendental over Q, and
    a search over Q alone would never see it.
  * over Q(mu) with the reciprocal:  { mu^i r^j } including j < 0 is the same
    box, so it is not run separately; instead 2r is checked, since
    results/subclasses.md's feed-vector identity makes 2r, not r, the
    natural object (r = (1/2)(w4.phi)/(w.phi)).

POSITIVE CONTROL, run at every precision: a genuine algebraic number of
comparable degree and height must be FOUND in the box that should contain it.
Without it a negative is worthless -- an unpowered guesser reports "none"
for everything.

Usage: python3 experiments/amplitude_pslq.py
         [--constants results/amplitude_ratio_constants.txt]
         [--digits 185] [--boxes 45:100,22:10000,...] [--field 3:5,5:9]
Target machine: gympie (laptop).  MEASURED: the 185-digit sweep is about 40 s;
the 492-digit sweep's top box (degree 122) dominates and is minutes.  No
checkpointing: kill with SIGINT and rerun with fewer boxes.
"""
import argparse
import sys
import time

from mpmath import mp, mpf, sqrt, pslq


def read_constants(path):
    with open(path) as fh:
        rows = [ln.strip() for ln in fh if ln.strip()
                and not ln.startswith('#')]
    return mpf(rows[0]), mpf(rows[1])          # mu, r


def capacity(nterms, height):
    return nterms * mp.log10(max(height, 2))


def search_poly(val, max_deg, max_height, digits, beat=False):
    """PSLQ on (1, val, ..., val^d) for d = 2..max_deg.  Returns hits."""
    hits = []
    t0 = time.time()
    for d in range(2, max_deg + 1):
        if beat and d % 5 == 0:
            print(f"    ... degree {d}/{max_deg}, {time.time() - t0:.0f} s",
                  flush=True)
        vec = [val ** k for k in range(d + 1)]
        rel = pslq(vec, maxcoeff=max_height, maxsteps=200000,
                   tol=mpf(10) ** (-(digits - 5)))
        if rel:
            h = max(abs(c) for c in rel)
            cap = capacity(d + 1, h)
            hits.append((d, h, float(cap),
                         'REJECTED-ARTIFACT' if cap > 0.5 * digits
                         else 'SURVIVES-CAPACITY-TEST'))
    return hits


def search_field(val, mu, imax, jmax, max_height, digits):
    """PSLQ on { mu^i r^j }: is val algebraic over Q(mu) in this box?"""
    vec, lab = [], []
    for i in range(imax + 1):
        for j in range(jmax + 1):
            vec.append(mu ** i * val ** j)
            lab.append((i, j))
    rel = pslq(vec, maxcoeff=max_height, maxsteps=200000,
               tol=mpf(10) ** (-(digits - 5)))
    return rel, lab, capacity(len(vec), max_height)


def positive_control(digits, max_deg, max_height):
    """A real algebraic number the same sweep must FIND."""
    saved = mp.dps
    mp.dps = digits
    val = (1 + sqrt(2)) / 3                       # 9x^2 - 6x - 1 = 0
    hits = search_poly(+val, min(max_deg, 4), max_height, digits)
    mp.dps = saved
    return hits


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--constants', default='results/amplitude_ratio_constants.txt')
    ap.add_argument('--digits', type=int, required=True)
    ap.add_argument('--boxes', required=True,
                    help='comma-separated maxdegree:maxheight')
    ap.add_argument('--field', default='3:5,5:9',
                    help='comma-separated imax:jmax for the Q(mu) search')
    ap.add_argument('--field-height', type=float, default=1e6)
    args = ap.parse_args()

    mp.dps = args.digits + 20
    mu, r = read_constants(args.constants)
    digits = args.digits
    print(f"# amplitude ratio, integer relations at {digits} trusted digits")
    print(f"#   r  = {str(r)[:60]}...")
    print(f"#   mu = {str(mu)[:60]}...")
    print(f"# capacity budget: a box is in-capacity while (terms)*log10(height)"
          f" < {0.5 * digits:.0f}")

    ctrl = positive_control(digits, 4, 100)
    ok = any(d == 2 and v.startswith('SURVIVES') for d, _, _, v in ctrl)
    print(f"\n## positive control (1+sqrt2)/3, degree <= 4 at height <= 1e2:"
          f" {'FOUND at degree 2 -- guesser is powered' if ok else 'NOT FOUND -- GUESSER IS DEAD'}")
    if not ok:
        return 1

    mp.dps = digits
    r_t, mu_t = +r, +mu
    print(f"\n## over Q: integer polynomial with r as a root")
    survivors = 0
    for box in args.boxes.split(','):
        dd, hh = box.split(':')
        max_deg, max_h = int(dd), int(float(hh))
        cap = capacity(max_deg + 1, max_h)
        tag = 'in-capacity' if cap < 0.5 * digits else 'OUT OF CAPACITY'
        t0 = time.time()
        hits = search_poly(r_t, max_deg, max_h, digits, beat=True)
        dt = time.time() - t0
        if not hits:
            print(f"  degree <= {max_deg:3d} at height <= {max_h:g}: "
                  f"none   [{tag}, capacity {float(cap):.0f}, {dt:.0f} s]",
                  flush=True)
        for d, h, cp, verdict in hits:
            print(f"  degree <= {max_deg:3d} at height <= {max_h:g}: "
                  f"hit degree {d} height {h} capacity {cp:.0f} -> {verdict}"
                  f"   [{dt:.0f} s]")
            if verdict.startswith('SURVIVES'):
                survivors += 1

    print(f"\n## over Q(mu): is r algebraic over Q(mu)?"
          f"  (height <= {args.field_height:g})")
    for fb in args.field.split(','):
        parts = fb.split(':')
        imax, jmax = int(parts[0]), int(parts[1])
        fh = int(float(parts[2])) if len(parts) > 2 else int(args.field_height)
        rel, lab, cap = search_field(r_t, mu_t, imax, jmax, fh, digits)
        tag = 'in-capacity' if cap < 0.5 * digits else 'OUT OF CAPACITY'
        if rel is None:
            print(f"  mu^i r^j, i <= {imax}, j <= {jmax}, height <= {fh:g}"
                  f" ({(imax+1)*(jmax+1)} terms): none"
                  f"   [{tag}, capacity {float(cap):.0f}]")
        else:
            h = max(abs(c) for c in rel)
            cp = capacity(len(lab), h)
            verdict = ('REJECTED-ARTIFACT' if cp > 0.5 * digits
                       else 'SURVIVES-CAPACITY-TEST')
            print(f"  mu^i r^j, i <= {imax}, j <= {jmax}: hit height {h}"
                  f" capacity {float(cp):.0f} of {digits} -> {verdict}"
                  f"   [box {tag}]")
            if verdict.startswith('SURVIVES'):
                survivors += 1

    print(f"\n## 2r (the feed-vector ratio itself), degree <= 12 at height <= 1e2")
    hits2 = search_poly(2 * r_t, 12, 100, digits)
    print("  " + ("none" if not hits2 else str(hits2)))
    survivors += sum(1 for _, _, _, v in hits2 if v.startswith('SURVIVES'))

    print(f"\n=> {'NO relation survives the capacity test in any box tried'
                 if survivors == 0 else f'{survivors} SURVIVING relation(s)'}")
    return 0


if __name__ == '__main__':
    sys.exit(main())
