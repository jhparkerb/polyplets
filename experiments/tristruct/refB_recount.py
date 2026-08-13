#!/usr/bin/env python3
"""refB_recount.py -- Refuter B: independent recomputation of the I(n,H)
cells behind Proposer 2's fitted claims (results/triangle-hunt-sym-diagonals.md).

All code here is written from the lattice definition (king adjacency =
Chebyshev distance 1; fixed animal = translation class; I(n,H) = animals of
height exactly H equal to their own top-bottom AND left-right bounding-box
reflections -- box invariance forces genuine set equality, see the report).
Nothing below reads core/transition.h or any engine.

Parts:
 1. From-scratch enumerator, n <= 8: T(n,H) and I(n,H) vs banked (rule check).
 2. I(n,3), I(n,4) for ALL n <= 40 by palindromic column-word counting.
    The scan connectivity rule is validated against explicit per-word BFS
    for n <= 16 before the DP is trusted (checker held to a higher standard).
    Targets: the order-8 H=3 recurrence and order-5 H=4 recurrence holdouts,
    including I(40,3) = 187425 and I(40,4) = 8117.
 3. Diagonals I(n, n-k), k <= 5, n up to 40, by direct enumeration of
    narrow (width <= k+1) Klein-invariant animals: palindromic row-words
    with total excess k, per-configuration BFS connectivity. Targets: the
    quasi-polynomial diagonal forms incl. the self-declared marginal k=5.

Run from experiments/tristruct/:  python3 refB_recount.py
"""
import os
import sys
from itertools import combinations

sys.setrecursionlimit(10000)

_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))
BANKED = {}
with open(os.path.join(_ROOT, 'results/subgroup_d2ax_byheight.txt')) as f:
    for ln in f:
        n, H, c = (int(x) for x in ln.split())
        BANKED[(n, H)] = c

NBR = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if dx or dy]


def connected(cells):
    cells = set(cells)
    start = next(iter(cells))
    seen = {start}
    stack = [start]
    while stack:
        x, y = stack.pop()
        for dx, dy in NBR:
            p = (x + dx, y + dy)
            if p in cells and p not in seen:
                seen.add(p)
                stack.append(p)
    return len(seen) == len(cells)


# ---------- Part 1: from-scratch enumerator, n <= 8 ----------

def canon(cells):
    mx = min(x for x, _ in cells)
    my = min(y for _, y in cells)
    return frozenset((x - mx, y - my) for x, y in cells)


def enumerate_fixed(nmax):
    level = {canon([(0, 0)])}
    yield 1, level
    for n in range(2, nmax + 1):
        nxt = set()
        for a in level:
            for (x, y) in a:
                for dx, dy in NBR:
                    p = (x + dx, y + dy)
                    if p not in a:
                        nxt.add(canon(a | {p}))
        level = nxt
        yield n, level


def part1(nmax=8):
    ok = True
    # banked T via own direct read
    T = {}
    import os
    root = os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))))
    for H in range(1, 41):
        with open(os.path.join(root, 'results/ns_a40/perheight/h%d.out' % H)) as f:
            for ln in f:
                if ln.strip():
                    a, b = (int(x) for x in ln.split())
                    T[(a, H)] = b
    for n, animals in enumerate_fixed(nmax):
        tn = {}
        inh = {}
        for a in animals:
            h = max(y for _, y in a) + 1
            w = max(x for x, _ in a) + 1
            tn[h] = tn.get(h, 0) + 1
            tb = frozenset((x, h - 1 - y) for x, y in a)
            lr = frozenset((w - 1 - x, y) for x, y in a)
            if tb == a and lr == a:
                inh[h] = inh.get(h, 0) + 1
        for h in range(1, n + 1):
            if tn.get(h, 0) != T[(n, h)]:
                print("P1 MISMATCH T(%d,%d): mine %d banked %d"
                      % (n, h, tn.get(h, 0), T[(n, h)]))
                ok = False
            if inh.get(h, 0) != BANKED.get((n, h), 0):
                print("P1 MISMATCH I(%d,%d): mine %d banked %d"
                      % (n, h, inh.get(h, 0), BANKED.get((n, h), 0)))
                ok = False
    print("P1 own enumerator n<=%d: %s"
          % (nmax, "ALL T(n,H) and I(n,H) MATCH banked" if ok else "MISMATCH"))


# ---------- Part 2: columns H=3 and H=4 to n=40 ----------

# H=3 column alphabet (symmetric nonempty subsets of rows {0,1,2}):
#   A={1} size1, B={0,2} size2, C={0,1,2} size3.
# Scan rule claimed: word connected <=> contains A or C; height==3 <=> B or C.
# H=4: a={1,2} size2, b={0,3} size2, c={0,1,2,3} size4.
#   connected <=> contains a or c; height==4 <=> b or c.

ALPH3 = {'A': (1,), 'B': (0, 2), 'C': (0, 1, 2)}
ALPH4 = {'a': (1, 2), 'b': (0, 3), 'c': (0, 1, 2, 3)}


def word_cells(word, alph):
    return [(i, r) for i, ch in enumerate(word) for r in alph[ch]]


def validate_scan_rule(alph, conn_letters, nmax):
    """BFS-check the scan connectivity rule on every palindromic word with
    sum <= nmax. Returns number of words checked, and asserts agreement."""
    letters = sorted(alph)
    sizes = {ch: len(alph[ch]) for ch in letters}
    checked = 0
    # enumerate halves (as words) with 2*sum <= nmax, plus optional middle
    def halves(budget):
        yield ''
        stack = [('', 0)]
        while stack:
            w, s = stack.pop()
            for ch in letters:
                s2 = s + sizes[ch]
                if s2 <= budget:
                    yield w + ch
                    stack.append((w + ch, s2))
    for u in halves(nmax // 2):
        su = sum(sizes[c] for c in u)
        for mid in [None] + letters:
            n = 2 * su + (sizes[mid] if mid else 0)
            if n == 0 or n > nmax:
                continue
            word = u + (mid if mid else '') + u[::-1]
            cells = word_cells(word, alph)
            scan = any(c in conn_letters for c in word)
            bfs = connected(cells)
            assert scan == bfs, (word, scan, bfs)
            checked += 1
    return checked


def column_counts(alph, conn_letters, tall_letters, nmax=40):
    """I(n,H) for this column height, n=1..nmax, by counting palindromic
    words containing >=1 connector letter and >=1 full-height letter."""
    letters = sorted(alph)
    sizes = {ch: len(alph[ch]) for ch in letters}
    # f[s][(fc, ft)] = number of (ordered) words with size-sum s and flags
    # fc = contains connector, ft = contains tall letter
    f = [dict() for _ in range(nmax + 1)]
    f[0][(False, False)] = 1
    for s in range(0, nmax + 1):
        for (fc, ft), cnt in list(f[s].items()):
            for ch in letters:
                s2 = s + sizes[ch]
                if s2 <= nmax:
                    k = (fc or ch in conn_letters, ft or ch in tall_letters)
                    f[s2][k] = f[s2].get(k, 0) + cnt
    out = {}
    for n in range(1, nmax + 1):
        tot = 0
        # even length: word = u + rev(u), n = 2*su, flags(word) = flags(u)
        if n % 2 == 0:
            for (fc, ft), cnt in f[n // 2].items():
                if fc and ft:
                    tot += cnt
        # odd length: u + mid + rev(u)
        for mid in letters:
            rem = n - sizes[mid]
            if rem >= 0 and rem % 2 == 0:
                for (fc, ft), cnt in f[rem // 2].items():
                    if (fc or mid in conn_letters) and (ft or mid in tall_letters):
                        tot += cnt
        out[n] = tot
    return out


def part2():
    ch3 = validate_scan_rule(ALPH3, 'AC', 16)
    ch4 = validate_scan_rule(ALPH4, 'ac', 16)
    print("P2 scan-rule BFS validation: H=3 %d words, H=4 %d words, all agree"
          % (ch3, ch4))
    c3 = column_counts(ALPH3, 'AC', 'BC')
    c4 = column_counts(ALPH4, 'ac', 'bc')
    bad = 0
    for n in range(1, 41):
        for H, mine in ((3, c3[n]), (4, c4[n])):
            if H <= n and mine != BANKED.get((n, H), 0):
                print("P2 MISMATCH I(%d,%d): mine %d banked %d"
                      % (n, H, mine, BANKED.get((n, H), 0)))
                bad += 1
    print("P2 I(n,3), I(n,4) all n<=40 vs banked: %s"
          % ("ALL MATCH" if not bad else "%d MISMATCHES" % bad))
    print("P2 my I(40,3)=%d (claim 187425), I(40,4)=%d (claim 8117)"
          % (c3[40], c4[40]))
    # recurrences on MY numbers (not banked): claimed H=3 order 8:
    r3 = all(c3[n] == 2 * c3[n - 2] - c3[n - 8] for n in range(11, 41))
    ev = [c4[n] for n in range(4, 41, 2)]
    co = [1, 2, -2, 1, -1]
    r4 = all(ev[i] == sum(co[j] * ev[i - 1 - j] for j in range(5))
             for i in range(5, len(ev)))
    print("P2 claimed recurrences hold on MY independent numbers: "
          "H=3 order-8 %s (n=11..40), H=4 order-5 even-subseq %s"
          % (r3, r4))


# ---------- Part 3: diagonals k <= 5 ----------

def sym_letters(w):
    """Nonempty lr-symmetric subsets of columns 0..w-1, as sorted tuples."""
    half = (w + 1) // 2
    out = []
    for mask in range(1, 1 << half):
        cols = set()
        for i in range(half):
            if mask >> i & 1:
                cols.add(i)
                cols.add(w - 1 - i)
        out.append(tuple(sorted(cols)))
    return out


def diag_count(n, k):
    """I(n, n-k) by enumeration of Klein-invariant animals of height
    H = n-k and width w (odd, <= k+1), rows = palindromic word of
    lr-symmetric row-letters, total excess sum(|r|-1) = k."""
    H = n - k
    if H < 1:
        return 0
    total = 0
    # width bound: the (w-1)/2 non-center column PAIRS must be covered by
    # heavy rows; a heavy of excess e covers at most floor((e+1)/2) pairs
    # beyond the center, and total excess is k => w <= 2k+1.
    for w in range(1, 2 * k + 2):
        if w % 2 == 0:
            # every symmetric letter has even size >= 2 => excess >= H > k
            if 2 * H <= n:  # unreachable for n >= 2k+2; guard anyway
                raise ValueError("even width regime touched")
            continue
        letters = sym_letters(w)
        exc = {r: len(r) - 1 for r in letters}
        minrow = ((w - 1) // 2,)
        heavies = [r for r in letters if exc[r] > 0]
        L = H // 2
        midpos = (H % 2 == 1)
        # distribute excess: 2*(half excess) + (middle excess if H odd) = k
        for me in range(0, k + 1):
            if midpos:
                mids = [r for r in letters if exc[r] == me] if me else [minrow]
            else:
                if me:
                    continue
                mids = [None]
            rem = k - me
            if rem % 2:
                continue
            he = rem // 2  # excess to place in the half
            for npos in range(0, he + 1):
                if npos > L:
                    break
                for pos in combinations(range(L), npos):
                    # assign heavy letters at pos with excesses summing to he
                    def assign(i, left, chosen):
                        nonlocal total
                        if i == len(pos):
                            if left:
                                return
                            for mid in mids:
                                rows = [minrow] * L
                                for p, r in zip(pos, chosen):
                                    rows[p] = r
                                word = rows + ([mid] if mid else []) + rows[::-1]
                                # width exactly w and connectivity
                                cols = set()
                                for r in word:
                                    cols.update(r)
                                if cols != set(range(w)):
                                    continue
                                cells = [(x, y) for y, r in enumerate(word)
                                         for x in r]
                                if connected(cells):
                                    total += 1
                            return
                        for r in heavies:
                            if exc[r] <= left - (len(pos) - i - 1):
                                if exc[r] <= left:
                                    assign(i + 1, left - exc[r], chosen + [r])
                        return
                    assign(0, he, [])
    return total


def part3():
    forms = {
        0: lambda n: 1,
        1: lambda n: 1 if n % 2 == 0 else 0,
        2: lambda n: (n - 1) // 2,
        3: lambda n: n // 2 if n % 2 == 0 else 0,
        # k=4 as PRINTED in the results table (m = floor(n/2), both classes):
        4: lambda n: (n // 2 - 1) * (n // 2 - 2) // 2 + 2,
        # k=4 corrected (m = ceil(n/2)) -- tested separately below
        '4c': lambda n: ((n + 1) // 2 - 1) * ((n + 1) // 2 - 2) // 2 + 2,
        5: lambda n: ((n // 2) ** 2 - n // 2 + 8) // 2 if n % 2 == 0 else 0,
    }
    onset = {0: 1, 1: 2, 2: 3, 3: 8, 4: 7, 5: 12}
    for k in range(0, 6):
        bad_bank, bad_form, rows = [], [], 0
        for n in range(max(2 * k + 2, k + 1), 41):
            mine = diag_count(n, k)
            rows += 1
            b = BANKED.get((n, n - k), 0)
            if mine != b:
                bad_bank.append((n, mine, b))
            if n >= onset[k] and mine != forms[k](n):
                bad_form.append((n, mine, forms[k](n)))
        print("P3 diag k=%d: %d values n<=40 recomputed; vs banked: %s; "
              "vs claimed form (past onset): %s"
              % (k, rows,
                 "ALL MATCH" if not bad_bank else "MISMATCH %s" % bad_bank[:4],
                 "ALL MATCH" if not bad_form else "MISMATCH %s" % bad_form[:4]))
        if k == 4:
            bad_c = [(n, diag_count(n, 4), forms['4c'](n))
                     for n in range(10, 41)
                     if diag_count(n, 4) != forms['4c'](n)]
            print("P3 diag k=4 vs CORRECTED form m=ceil(n/2): %s"
                  % ("ALL MATCH n=10..40" if not bad_c
                     else "MISMATCH %s" % bad_c[:4]))


if __name__ == '__main__':
    part1()
    part2()
    part3()
