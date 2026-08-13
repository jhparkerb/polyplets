"""refA_columns_check.py -- Refuter A's independent verification of Proposer
3's column/atom claims (candidates/p3_columns.py, results/
triangle-hunt-atoms-ab-initio.md).

Everything here is written by Refuter A from the lattice definition and the
data files under scrutiny; p3_striptm.py / p3_atoms.py are NOT imported.
Exact integer arithmetic throughout.

Checks:
  A. Refuter's own strip transfer matrix (own state construction: BFS/merge
     closure instead of union-find) computes S_H(n), H<=6, n<=NLONG.
  B. T(n,H) = S_H - 2 S_{H-1} + S_{H-2} compared against (i) the banked
     triangle results/ns_a40/perheight/h{5,6}.out for ALL n<=40, H<=6, and
     (ii) the proposer's table data/p3_striptm_T.txt.
  C. q_5, q_6 as banked in data/p3_atoms_q.txt annihilate the refuter's own
     S_5, S_6 exactly over Z on every available instance; degrees, monicity.
  D. Refuter's own Berlekamp-Massey mod two fresh primes (not the proposer's)
     confirms minimal orders 29 and 68.
  E. Squarefree + pairwise coprime via gcd == 1 mod a fresh prime (a valid
     one-sided certificate over Q).
  F. The q_5 candidate check on PURELY BANKED data, n = 30..40, plus
     perturbation: T(40,5) off by d must fail for various d; and p_5 =
     q_5 q_4 q_3 onset probing at n = 43..46 (proposer claims first valid
     instance n = 47).
  G. Share of a(40) covered by T(40,5)+T(40,6), and row-40 columns h<=6.

Run from experiments/tristruct/:  python3 refA_columns_check.py
"""

import os
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
NLONG = 170
FAILS = []


def report(name, ok, detail=""):
    print("%-58s %s  %s" % (name, "OK" if ok else "FAIL", detail))
    if not ok:
        FAILS.append(name)


# ---------- A. own strip TM ----------------------------------------------

def components_after(H, omask, opart, ocells, m2):
    """Refuter's transition: new column mask m2 after old (omask, opart).

    Returns canonical partition tuple of the new column's cells, or None if
    an old component is stranded (disconnection).  Method: seed one group
    per maximal vertical run of m2, attach the set of old classes each group
    touches (old cell within |dy| <= 1 of a group cell), then merge groups
    transitively while any two share an old class.  No union-find.
    """
    ncells = [b for b in range(H) if (m2 >> b) & 1]
    # maximal vertical runs
    groups = []
    for c in ncells:
        if groups and groups[-1][-1] == c - 1:
            groups[-1].append(c)
        else:
            groups.append([c])
    nold = (max(opart) + 1) if opart else 0
    glinks = []
    for g in groups:
        touch = set()
        for c in g:
            for dy in (-1, 0, 1):
                c2 = c + dy
                if 0 <= c2 < H and (omask >> c2) & 1:
                    touch.add(opart[ocells.index(c2)])
        glinks.append([set(g), touch])
    if set().union(*(t for _, t in glinks)) != set(range(nold)):
        return None  # stranded old component
    # transitive merge on shared old classes
    changed = True
    while changed:
        changed = False
        for i in range(len(glinks)):
            for j in range(i + 1, len(glinks)):
                if glinks[i][1] & glinks[j][1]:
                    glinks[i][0] |= glinks[j][0]
                    glinks[i][1] |= glinks[j][1]
                    del glinks[j]
                    changed = True
                    break
            if changed:
                break
    lab = {}
    for gi, (cells, _t) in enumerate(glinks):
        for c in cells:
            lab[c] = gi
    seen, out = {}, []
    for c in ncells:
        if lab[c] not in seen:
            seen[lab[c]] = len(seen)
        out.append(seen[lab[c]])
    return tuple(out)


def start_partition(H, m):
    cells = [b for b in range(H) if (m >> b) & 1]
    lab, cls = {}, -1
    prev = None
    for c in cells:
        if prev is None or c != prev + 1:
            cls += 1
        lab[c] = cls
        prev = c
    seen, out = {}, []
    for c in cells:
        if lab[c] not in seen:
            seen[lab[c]] = len(seen)
        out.append(seen[lab[c]])
    return tuple(out)


def own_strip_series(H, nmax, limb=768):
    """S_H(n), n = 0..nmax, exact.  Polynomial in x packed into one int."""
    masks = list(range(1, 1 << H))
    ids = {}
    edges = []
    accept = []

    def sid(mask, part):
        k = (mask, part)
        if k not in ids:
            ids[k] = len(edges)
            edges.append(None)
            accept.append(len(part) > 0 and max(part) == 0)
        return ids[k]

    frontier = []
    starts = {}
    for m in masks:
        i = sid(m, start_partition(H, m))
        if i not in starts:
            starts[i] = bin(m).count("1")
            frontier.append(i)
    k = 0
    while k < len(frontier):
        i = frontier[k]
        k += 1
        if edges[i] is not None:
            continue
        (mask, part) = next(kk for kk, vv in ids.items() if vv == i)
        ocells = [b for b in range(H) if (mask >> b) & 1]
        out = []
        for m2 in masks:
            p2 = components_after(H, mask, part, ocells, m2)
            if p2 is None:
                continue
            j = sid(m2, p2)
            out.append((j, bin(m2).count("1")))
            if edges[j] is None and j not in frontier[k:]:
                frontier.append(j)
        edges[i] = out
    for i, e in enumerate(edges):
        if e is None:
            edges[i] = []
    trunc = 1 << (limb * (nmax + 1))
    dp = [0] * len(edges)
    for i, pc in starts.items():
        dp[i] += 1 << (limb * pc)
    tot = 0
    for _ in range(nmax):
        for i in range(len(edges)):
            if accept[i]:
                tot = (tot + dp[i]) % trunc
        nd = [0] * len(edges)
        for i, v in enumerate(dp):
            if v:
                for j, pc in edges[i]:
                    nd[j] = (nd[j] + (v << (limb * pc))) % trunc
        dp = nd
    for i in range(len(edges)):
        if accept[i]:
            tot = (tot + dp[i]) % trunc
    lm = (1 << limb) - 1
    seq = []
    for n in range(nmax + 1):
        v = (tot >> (limb * n)) & lm
        assert v < (1 << (limb - 16)), "limb margin"
        seq.append(v)
    return seq, len(edges)


# ---------- helpers -------------------------------------------------------

def load_banked_col(H):
    out = {}
    with open(os.path.join(REPO, "results", "ns_a40", "perheight",
                           "h%d.out" % H)) as f:
        for line in f:
            n, v = line.split()
            out[int(n)] = int(v)
    return out


def load_q():
    q = {}
    with open(os.path.join(HERE, "data", "p3_atoms_q.txt")) as f:
        for line in f:
            p = line.split()
            q[int(p[0])] = [int(x) for x in p[2:]]
            assert len(q[int(p[0])]) == int(p[1]) + 1
    return q


def bm(seq, p):
    C, B, L, m, b = [1], [1], 0, 1, 1
    for i, s in enumerate(seq):
        d = s % p
        for j in range(1, L + 1):
            d = (d + C[j] * seq[i - j]) % p
        if d == 0:
            m += 1
            continue
        coef = d * pow(b, p - 2, p) % p
        C2 = C + [0] * (len(B) + m - len(C))
        for j, x in enumerate(B):
            C2[j + m] = (C2[j + m] - coef * x) % p
        if 2 * L <= i:
            L, B, b, m, C = i + 1 - L, C[:], d, 1, C2
        else:
            m += 1
            C = C2
    return [x % p for x in C[:L + 1]]


def gcd_modp(a, b, p):
    a = [x % p for x in a]
    b = [x % p for x in b]

    def st(v):
        i = 0
        while i < len(v) and v[i] == 0:
            i += 1
        return v[i:]
    a, b = st(a), st(b)
    while b:
        inv = pow(b[0], p - 2, p)
        r = list(a)
        while len(r) >= len(b):
            f = r[0] * inv % p
            for j in range(len(b)):
                r[j] = (r[j] - f * b[j]) % p
            r = st(r)
            if not r:
                break
        a, b = b, r
    return len(a) - 1  # degree of gcd


def main():
    q = load_q()
    report("q degrees are 1,2,4,9,29,68",
           [len(q[h]) - 1 for h in range(1, 7)] == [1, 2, 4, 9, 29, 68])
    report("q_5, q_6 monic (unit target coefficient)",
           q[5][0] == 1 and q[6][0] == 1)

    # A. own TM
    S = {0: [0] * (NLONG + 1), -1: [0] * (NLONG + 1)}
    scounts = []
    for H in range(1, 7):
        S[H], ns = own_strip_series(H, NLONG)
        scounts.append(ns)
    report("own TM state counts = 1,3,8,20,50,126 (Motzkin M_{H+1}-1)",
           scounts == [1, 3, 8, 20, 50, 126], str(scounts))

    T = {(n, H): S[H][n] - 2 * S[H - 1][n] + S[H - 2][n]
         for H in range(1, 7) for n in range(1, 41)}

    # B. against banked and against proposer's table
    bank = {H: load_banked_col(H) for H in range(1, 7)}
    bad = sum(1 for (n, H), v in T.items() if bank[H][n] != v)
    report("own TM vs BANKED triangle, all 240 cells n<=40 H<=6", bad == 0,
           "%d mismatches" % bad)
    ptab = {}
    with open(os.path.join(HERE, "data", "p3_striptm_T.txt")) as f:
        for line in f:
            n, h, v = map(int, line.split())
            ptab[(n, h)] = v
    bad = sum(1 for k, v in T.items() if ptab[k] != v)
    report("own TM vs proposer table p3_striptm_T.txt (240 cells)", bad == 0)
    report("structural zeros T(n,H)=0 for n<H in own TM",
           all(T[(n, H)] == 0 for H in range(1, 7) for n in range(1, H)))

    # C. q_5, q_6 annihilate own S_5, S_6 exactly over Z
    for H, d in ((5, 29), (6, 68)):
        cnt = 0
        ok = True
        for n in range(d + 1, NLONG + 1):
            s = sum(q[H][j] * S[H][n - j] for j in range(d + 1))
            if s != 0:
                ok = False
                break
            cnt += 1
        report("q_%d annihilates own S_%d exactly over Z" % (H, H), ok,
               "%d instances (n=%d..%d)" % (cnt, d + 1, NLONG))

    # D. own BM, fresh primes
    for p in ((1 << 61) - 1, (1 << 62) - 57):
        degs = [len(bm(S[H][1:], p)) - 1 for H in range(1, 7)]
        report("own BM mod %d degrees 1,2,4,9,29,68" % p,
               degs == [1, 2, 4, 9, 29, 68], str(degs))
    # coefficient agreement mod one prime (both monic)
    p = (1 << 61) - 1
    for H in (5, 6):
        c = bm(S[H][1:], p)
        report("BM(own S_%d) == banked q_%d mod 2^61-1" % (H, H),
               all((a - b) % p == 0 for a, b in zip(c, q[H])))

    # E. squarefree + pairwise coprime, fresh prime
    p = (1 << 62) - 57

    def deriv(v):
        d = len(v) - 1
        return [c * (d - i) for i, c in enumerate(v[:-1])]
    report("all q_H squarefree (gcd(q,q') = 1 mod fresh prime)",
           all(gcd_modp(q[H], deriv(q[H]), p) == 0 for H in range(1, 7)))
    report("pairwise coprime (gcd = 1 mod fresh prime)",
           all(gcd_modp(q[a], q[b], p) == 0
               for a in range(1, 7) for b in range(a + 1, 7)))

    # F. candidate check on purely banked data + perturbation
    def C5_banked(n, t5=None):
        v = t5 if t5 is not None else bank[5][n]
        return v + sum((6 - h) * bank[h][n] for h in range(1, 5))

    ok = all(sum(q[5][j] * C5_banked(n - j) for j in range(30)) == 0
             for n in range(30, 41))
    report("q_5 check on PURELY BANKED cells, n=30..40 (11 instances)", ok)
    pert_ok = True
    for d in (1, -1, 3, -27, 3 ** 20, -3 ** 30, 10 ** 15 + 7):
        s = (sum(q[5][j] * C5_banked(40 - j) for j in range(1, 30))
             + C5_banked(40, bank[5][40] + d))
        if s == 0:
            pert_ok = False
    report("perturbed T(40,5) (7 offsets incl. +-3^k) all FAIL q_5 check",
           pert_ok)
    # sanity: banked C_5 equals own S_5 on n<=40
    report("banked C_5(n) == own S_5(n), n=1..40",
           all(C5_banked(n) == S[5][n] for n in range(1, 41)))
    # p_5 = q_5 q_4 q_3 onset: proposer claims first valid n = 47

    def polymul(a, b):
        o = [0] * (len(a) + len(b) - 1)
        for i, x in enumerate(a):
            for j, y in enumerate(b):
                o[i + j] += x * y
        return o
    p5 = polymul(polymul(q[5], q[4]), q[3])
    Tcol5 = [S[5][n] - 2 * S[4][n] + S[3][n] for n in range(NLONG + 1)]
    first_ok = None
    for n in range(43, NLONG + 1):
        if sum(p5[j] * Tcol5[n - j] for j in range(43)) == 0:
            if first_ok is None:
                first_ok = n
        elif first_ok is not None:
            first_ok = None  # must hold contiguously once it starts
    holds_43 = all(sum(p5[j] * Tcol5[n - j] for j in range(43)) == 0
                   for n in range(43, 48))
    print("p_5 order-42 on T(.,5): first contiguous-valid n = %s "
          "(holds at 43..47: %s; proposer claimed 47)"
          % (first_ok, holds_43))

    # G. share of a(40)
    a40 = 0
    with open(os.path.join(REPO, "results", "ns_a40", "triangle.txt")) as f:
        for line in f:
            n, v = line.split()
            if int(n) == 40:
                a40 = int(v)
    cover = bank[5][40] + bank[6][40]
    cover6 = sum(bank[h][40] for h in range(1, 7))
    print("T(40,5)+T(40,6) = %d" % cover)
    print("a(40)           = %d" % a40)
    print("share = %.3e ; columns h<=6 total share = %.3e"
          % (Fraction(cover, a40), Fraction(cover6, a40)))

    print()
    if FAILS:
        print("FAILURES:", FAILS)
        return 1
    print("ALL CHECKS PASS")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
