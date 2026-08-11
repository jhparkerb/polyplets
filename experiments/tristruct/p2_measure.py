#!/usr/bin/env python3
"""p2_measure.py -- Proposer 2 quick measurements for the congruence hunt.

Checks (exact integer arithmetic throughout):
  M1. Klein/Burnside per-cell integrality on SELF-enumerated data (n<=13):
      T + I_tb + I_lr + I_180 == 0 mod 4 for every cell.
  M2. Forced zeros on self data: n odd & H even => I_tb = I_180 = 0.
  M3. Pairing sanity on self data: T == I_tb == I_lr == I_180 (mod 2) per cell.
  M4. Banked triangle: T(n,H) == 0 mod 2 for all n odd, H even (n <= 39).
  M5. Banked triangle: same region mod 4 residues of T (distribution; T == -I_lr
      mod 4 predicted there, I_lr not banked -- just report residues).
  M6. Cross-link: sum_H I_tb(n,H) == hmirror(n) and sum_H I_180(n,H) == r180(n)
      from runs/sym34 (different code path), n <= 13.
  M7. a(n) parity vs hmirror/r180 parity, n <= 34 (banked both sides).

Run from experiments/tristruct/:  python3 p2_measure.py
"""
import os, sys
from triangle import Triangle

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))

def load_sym(path):
    """p2_enum --sym lines: n H T tb lr r180 klein -> {(n,H): tuple}."""
    d = {}
    with open(path) as f:
        for ln in f:
            p = ln.split()
            if len(p) != 7:
                raise SystemExit("bad --sym line: " + ln)
            n, H = int(p[0]), int(p[1])
            d[(n, H)] = tuple(int(x) for x in p[2:])
    return d

def load_nv(path):
    d = {}
    with open(path) as f:
        for ln in f:
            ln = ln.strip()
            if not ln or ln.startswith('#'):
                continue
            a, b = ln.split()[:2]
            d[int(a)] = int(b)
    return d

def main():
    tri = Triangle.load()
    sym = load_sym(os.path.join(HERE, 'data', 'p2_sym_n13.txt'))
    nmax_self = max(n for n, _ in sym)

    # M1 Klein integrality
    bad = [(n, H) for (n, H), (T, tb, lr, rot, kl) in sym.items()
           if (T + tb + lr + rot) % 4 != 0]
    print("M1 Klein (T+tb+lr+rot)%%4==0 on self data n<=%d: %s"
          % (nmax_self, "ALL PASS" if not bad else "FAIL %s" % bad[:5]))

    # M2 forced zeros
    bad = [(n, H) for (n, H), (T, tb, lr, rot, kl) in sym.items()
           if n % 2 == 1 and H % 2 == 0 and (tb != 0 or rot != 0)]
    print("M2 n odd,H even => tb=rot=0 on self data: %s"
          % ("ALL PASS" if not bad else "FAIL %s" % bad[:5]))

    # M3 pairing parities
    bad = [(n, H) for (n, H), (T, tb, lr, rot, kl) in sym.items()
           if not (T % 2 == tb % 2 == lr % 2 == rot % 2)]
    print("M3 T==tb==lr==rot mod 2 on self data: %s"
          % ("ALL PASS" if not bad else "FAIL %s" % bad[:5]))

    # M4 banked: n odd, H even => T even, n<=39 and beyond structural range
    bad, cnt = [], 0
    for n in range(1, 40):
        if n % 2 == 0:
            continue
        for H in range(2, n + 1, 2):
            cnt += 1
            if tri.cell(n, H) % 2 != 0:
                bad.append((n, H))
    print("M4 banked T(n,H) even for n odd, H even (n<=39): %d cells, %s"
          % (cnt, "ALL PASS" if not bad else "FAIL %s" % bad[:5]))

    # M5 mod-4 residue distribution on that region
    from collections import Counter
    c = Counter(tri.cell(n, H) % 4 for n in range(3, 40, 2)
                for H in range(2, n + 1, 2))
    print("M5 mod-4 residues on {n odd, H even}: %s" % dict(sorted(c.items())))

    # M6 cross-link to runs/sym34 (different code path)
    hm = load_nv(os.path.join(ROOT, 'runs/sym34/hmirror.out'))
    r180 = load_nv(os.path.join(ROOT, 'runs/sym34/r180.out'))
    ok = True
    for n in range(1, nmax_self + 1):
        stb = sum(v[1] for (nn, H), v in sym.items() if nn == n)
        srot = sum(v[3] for (nn, H), v in sym.items() if nn == n)
        slr = sum(v[2] for (nn, H), v in sym.items() if nn == n)
        if stb != hm.get(n) or srot != r180.get(n) or slr != hm.get(n):
            ok = False
            print("M6 MISMATCH n=%d: sum tb=%d sum lr=%d hmirror=%s; "
                  "sum rot=%d r180=%s" % (n, stb, slr, hm.get(n), srot, r180.get(n)))
    if ok:
        print("M6 sum_H tb == sum_H lr == hmirror(n), sum_H rot == r180(n), "
              "n<=%d vs runs/sym34: ALL PASS" % nmax_self)

    # M7 a(n) parity vs hmirror/r180 parity (banked both sides), n<=34
    bad = [n for n in range(1, 35)
           if not (tri.rowsum(n) % 2 == hm[n] % 2 == r180[n] % 2)]
    print("M7 a(n)==hmirror(n)==r180(n) mod 2, n<=34: %s"
          % ("ALL PASS" if not bad else "FAIL n=%s" % bad))

if __name__ == '__main__':
    main()
