#!/usr/bin/env python3
"""The depth-1 below-onset defect, with the lattice as a parameter.

`results/below-onset.md` closes depth 1 on the king lattice: the
defect `D_1(k) = T(2k,k) - P_k(2k)/3^(k+1)` assembles from the all-pairs cluster
families by the gap-walk identity (II), and its generating function is the
quartic `Phi`.  Every piece of that is written for king adjacency.  Here the
same machine runs on any row-local lattice whose up-neighbours of `(c, y)` are
`(c+d, y+1)` for `d` in a drift set `D` -- square `D = {0}`, hex `D = {-1, 0}`,
king `D = {-1, 0, 1}` -- with `b = |D|`.

What this file establishes, and how:

  DERIVED  The bulk gap kernel is `u^(b-1) - y * Sigma_b(u)^2` with
           `Sigma_b(u) = 1 + u + ... + u^(b-1)`.  Reason, not fit: at large gap
           a P-row must touch both old cells, so the new gap is
           `g + d2 - d1` with `d1, d2` in `D`, and the shift distribution is the
           autocorrelation of `D`.  For an interval `D` that is
           `Sigma_b(u)^2 / u^(b-1)`.  `--kernel` checks the claim against the
           enumerated transition table on all three lattices.

  DERIVED  The assembly identity (II) is parametric with `3 -> b`:
           `D_1(k) = [y^k]( Phat - B^2 / (b + S) )`.  The 3 is the drift-step
           weight of the renewal chain, exactly as in
           `results/closed-doors.md`; the derivation in
           `onset-defect-depth1-closed.md` Sec. 2 never uses anything else about
           the king lattice.

  CHECKED  square, `D_1(k) = (-1)^(k+1)` -- to k = 40, against
           `results/undertow.md`, which measured it at k <= 6.
  CHECKED  hex, against `T_hex(2k,k) - P_k(2k)/2^(k+1)` from
           `results/hex_diagonal_cells.txt` -- to k = 6.
  CHECKED  king, against `experiments/depth1_gap_walk.py`'s banked series.

  NOT DERIVED  the algebraic equation on a lattice other than king.  The g = 1
           and g = 2 rows of the walk are genuine boundary exceptions whose
           constants change with `D`; `--boundary` prints them per lattice.
           See the note at the foot of this file.

Target machine: gympie, single core, well under a minute, no RAM concern.

    python3 experiments/depth1_parametric.py            # all gates, fail-closed
    python3 experiments/depth1_parametric.py --kernel   # bulk-kernel derivation
    python3 experiments/depth1_parametric.py --boundary # the g <= 2 rows per lattice
"""
import argparse
import os
import sys
from collections import defaultdict
from fractions import Fraction as Fr

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from diagonal_machine import LATTICES                             # noqa: E402
from depth1_sharpness import phi_at_series                       # noqa: E402
PAIR_WEIGHT = {'square': 4, 'hex': 9, 'king': 25}       # W_pair(b) = b^3 - b(b+1)/2 + 4


# ---------------------------------------------------------------- the gap walk

def transitions(D, g, c, gp_max):
    """`experiments/depth1_gap_walk.transitions`, with the drift set as input.

    A new cell at `t` touches an old cell at `c0` iff `t - c0` is in `D`.  Two
    cells in the same row are adjacent iff their positions differ by 1, which is
    lattice-independent.  Old pair at (0, g), class `c`: J = already one
    component, P = two.  Returns {(new gap, new class): count}.
    """
    Ds = set(D)
    out = defaultdict(int)
    for gp in range(1, gp_max + 1):
        cand = sorted({a for d in Ds for a in (d, g + d, d - gp, g + d - gp)})
        for a in cand:
            T = (a, a + gp)
            touch0 = any((t - 0) in Ds for t in T)
            touchg = any((t - g) in Ds for t in T)
            if c == 'P':
                if not (touch0 and touchg):
                    continue
            elif not (touch0 or touchg):
                continue
            if gp == 1:
                nc = 'J'
            elif c == 'J':
                a0 = (T[0] in Ds) or ((T[0] - g) in Ds)
                a1 = (T[1] in Ds) or ((T[1] - g) in Ds)
                nc = 'J' if (a0 and a1) else 'P'
            else:
                par = {k: k for k in 'ABxy'}

                def find(k):
                    while par[k] != k:
                        k = par[k]
                    return k

                def uni(u, v):
                    ru, rv = find(u), find(v)
                    if ru != rv:
                        par[ru] = rv

                for lab, t in (('x', T[0]), ('y', T[1])):
                    if t in Ds:
                        uni(lab, 'A')
                    if (t - g) in Ds:
                        uni(lab, 'B')
                nc = 'J' if find('x') == find('y') else 'P'
            out[(gp, nc)] += 1
    return dict(out)


def q_end(D, dp):
    """Close the stack with the free single contact cell above.

    A P-state needs that cell to join the pair, so it must touch both:
    |D & (g+D)| ways.  A J-state needs it only to attach: |D | (g+D)| ways.
    """
    Ds = set(D)
    tot = 0
    for (g, c), v in dp.items():
        gD = {d + g for d in Ds}
        tot += v * len(Ds | gD if c == 'J' else Ds & gD)
    return tot


def bare_end(dp):
    return sum(v for (g, c), v in dp.items() if c == 'J')


def walk_families(D, L):
    """(W(2^l), W^b(2^l), W^p(2^l)) for l = 1..L: interior, bottom-edge, pure."""
    b = len(D)
    gmax = (b - 1) * L + 4
    Ds = set(D)
    trans = {(g, c): transitions(D, g, c, gmax)
             for g in range(1, gmax + 1) for c in 'JP'}

    dp_int = defaultdict(int)
    for g in range(1, gmax + 1):
        for a in sorted(set(Ds) | {d - g for d in Ds}):
            T = (a, a + g)
            if not any(t in Ds for t in T):
                continue
            nc = 'J' if (g == 1 or all(t in Ds for t in T)) else 'P'
            dp_int[(g, nc)] += 1
    dp_bare = defaultdict(int)
    for g in range(1, gmax + 1):
        dp_bare[(g, 'J' if g == 1 else 'P')] += 1

    out = []
    for _ in range(L):
        out.append((q_end(D, dp_int), q_end(D, dp_bare), bare_end(dp_bare)))
        nxt = []
        for dp in (dp_int, dp_bare):
            ndp = defaultdict(int)
            for (g, c), v in dp.items():
                for (gp, nc), t in trans[(g, c)].items():
                    ndp[(gp, nc)] += v * t
            nxt.append(ndp)
        dp_int, dp_bare = nxt
    return out


def series_D1(fams, b, K):
    """(II) with 3 -> b:  D_1(k) = [y^k]( Phat - B^2 / (b + S) )."""
    S = [Fr(0)] + [Fr(w) for w, _, _ in fams[:K]]
    B = [Fr(1)] + [Fr(w) for _, w, _ in fams[:K]]
    Ph = [Fr(0)] + [Fr(w) for _, _, w in fams[:K]]

    def smul(p, q):
        return [sum(p[i] * q[m - i] for i in range(m + 1)) for m in range(K + 1)]

    den = [Fr(b) + S[0]] + S[1:]
    inv = [1 / den[0]] + [Fr(0)] * K
    for m in range(1, K + 1):
        inv[m] = -sum(den[i] * inv[m - i] for i in range(1, m + 1)) / den[0]
    chain = smul(smul(B, B), inv)
    return [Ph[k] - chain[k] for k in range(K + 1)]


# -------------------------------------------------------- the bulk gap kernel

def sigma_sq(b):
    """Coefficients of Sigma_b(u)^2 = (1 + u + ... + u^(b-1))^2, u^0 .. u^(2b-2)."""
    s = [1] * b
    out = [0] * (2 * b - 1)
    for i in range(b):
        for j in range(b):
            out[i + j] += s[i] * s[j]
    return out


def bulk_row(D, g, gp_max):
    """The P-row at gap g as {shift: weight}, shift = new gap - g."""
    return {gp - g: v for (gp, c), v in transitions(D, g, c='P', gp_max=gp_max).items()
            if c == 'P'}


def check_kernel(name, D, verbose=True):
    """The generic P-row is the autocorrelation of D, i.e. Sigma_b(u)^2/u^(b-1)."""
    b = len(D)
    want = {i - (b - 1): w for i, w in enumerate(sigma_sq(b))}
    want = {k: v for k, v in want.items() if v}
    for g in range(2 * b + 1, 2 * b + 12):
        got = bulk_row(D, g, g + 2 * b)
        assert got == want, (name, g, got, want)
    if verbose:
        terms = ' + '.join(f"{v}u^{k}" for k, v in sorted(want.items()))
        print(f"  {name:6s} b={b}  bulk row = {terms}"
              f"   kernel  u^{b - 1} - y*(1+...+u^{b - 1})^2")
    return want


# ---------------------------------------- the generic row, derived from D

def template_row(D, g, gp_max):
    """The generic transition rows at gap g >= b, from counting alone.

    A new pair at gap `gp` far from the old pair must touch one of the two old
    cells, so its left end lies in `D | (D-gp) | (g+D) | (g+D-gp)`; by symmetry
    that is `2|D | (D-gp)|` placements.  Of them, `2|D & (D-gp)|` touch the same
    old cell twice and so leave the pair joined (class J); at `gp = 1` the new
    cells are row-adjacent and all of them are J.  Near the old gap the two ends
    can touch different old cells: that happens at `gp = g + d2 - d1` with
    `d1, d2` in `D`, i.e. with the autocorrelation weight `k_d`, and those
    placements were already counted once in the union, so class P loses `2 k_d`
    while class J gains `k_d`.  A target `gp = 1` is folded into J.

    Returns {'J': row, 'P': row} for the two starting classes.
    """
    Ds = set(D)
    b = len(Ds)
    bulk = {}
    for d1 in Ds:
        for d2 in Ds:
            bulk[d2 - d1] = bulk.get(d2 - d1, 0) + 1
    outJ, outP = defaultdict(int), defaultdict(int)
    for gp in range(1, gp_max + 1):
        tot = 2 * len(set(Ds) | {a - gp for a in Ds})
        joined = 2 * len(set(Ds) & {a - gp for a in Ds})
        if gp == 1:
            outJ[(1, 'J')] += tot
        else:
            outJ[(gp, 'J')] += joined
            outJ[(gp, 'P')] += tot - joined
    for d, k in bulk.items():
        gp = g + d
        if gp < 1 or gp > gp_max:
            continue
        if gp == 1:
            outJ[(1, 'J')] += k - 2 * k
            outP[(1, 'J')] += k
        else:
            outJ[(gp, 'J')] += k
            outJ[(gp, 'P')] -= 2 * k
            outP[(gp, 'P')] += k
    clean = lambda d: {a: v for a, v in d.items() if v}
    return {'J': clean(outJ), 'P': clean(outP)}


def check_template(name, D, gmax=14, verbose=True):
    b = len(D)
    for g in range(b, gmax + 1):
        want = template_row(D, g, gmax + b)
        for c in 'JP':
            got = transitions(D, g, c, gmax + b)
            assert got == want[c], (name, g, c, got, want[c])
    if verbose:
        print(f"  {name:6s} generic rows g = {b}..{gmax} match the counting "
              f"template; exceptional gaps: g < {b}")
    return True


# ------------------------------------------- square: the closed form, derived

def square_closed_form():
    """S, B, Phat and F_1 for D = {0}, from the walk's two-state structure."""
    import sympy as sp
    y = sp.symbols('y')
    D = (0,)
    N = 12
    # The reachable states are (1,J) and (g,P), g >= 2, and the (g,P) mass is
    # flat in g.  Assert the three rows that make that true.
    assert transitions(D, 1, 'J', N) == dict(
        [((1, 'J'), 3)] + [((gp, 'P'), 4) for gp in range(2, N + 1)])
    assert transitions(D, 1, 'P', N) == {(1, 'J'): 1}
    for g in range(2, N - 1):
        want = {(1, 'J'): 4, (g, 'J'): 1, (g, 'P'): 2}
        for gp in range(2, N + 1):
            if gp != g:
                want[(gp, 'P')] = 4
        assert transitions(D, g, 'J', N) == want, g
        assert transitions(D, g, 'P', N) == {(g, 'P'): 1}, g
    # So j -> 3j on the J side, and no P state ever returns to J.  The end
    # functionals see the J mass only: q_end weighs a g = 1 J state by
    # |D | (1+D)| = 2, and a P state at g >= 2 by |D & (g+D)| = 0.
    j0_int, j0_bare = 2, 1              # dp_int (1,J) = 2, dp_bare (1,J) = 1
    # S = sum_l 2 j0_int 3^(l-1) y^l and B = 1 + sum_l 2 j0_bare 3^(l-1) y^l, summed.
    S = sp.cancel(2 * j0_int * y / (1 - 3 * y))
    B = sp.cancel(1 + 2 * j0_bare * y / (1 - 3 * y))
    Ph = sp.cancel(y / (1 - 3 * y))
    F1 = sp.cancel(Ph - B ** 2 / (1 + S))
    return y, S, B, Ph, sp.simplify(F1)


# -------------------------------------------- hex: the kernel closure, b = 2

def hex_kernel():
    """Solve the b = 2 closure; return the algebraic equation for hex F_1.

    Unknowns: `j1` = J-mass at gap 1, `j2` = J-mass at gap 2, `Jm` = J-mass at
    gaps >= 2, `p2` = P-mass at gap 2.  P-mass at gap 1 is identically zero: a
    new pair at gap 1 is row-adjacent, hence class J.  With `J_2 = J - j1 u` and
    `P_2 = P`, the template rows of `template_row` plus the one exceptional row
    (g = 1) give

      J = J0 + y[ 6 Jm u + K J_2 - 2 j2 u + p2 u + j1(4u + u^2) ]
      P = P0 + y[ 8 Jm u^2/(1-u) - 2(K J_2 - j2 u) + K P_2 - p2 u
                  + j1(4u^2 + 6u^3/(1-u)) ]

    with K(u) = (1+u)^2/u.  Multiplying by u and using D(u) = u - y(1+u)^2:

      D J = Q,  Q = u J0 + y[ (6Jm - 2j2 + p2) u^2 + j1(-u + 2u^2) ]
      D P = u P0 + y[ 8Jm u^3/(1-u) - 2(1+u)^2 (J - j1 u) + 2 j2 u^2 - p2 u^2
                      + j1(4u^3 + 6u^4/(1-u)) ]

    The kernel is quadratic in u, so there is one small root; the four closing
    conditions are Q(u1) = 0, the u^1 self-consistency, J at u = 1, and the P
    equation at u1 (using J(u1) = Q'(u1)/D'(u1)).

    Everything is rational in `A = sqrt(1-4y)`: with `y = (1-A^2)/4` the small
    root is `u1 = (1-A)/(1+A)`.
    """
    import sympy as sp
    A, u, T = sp.symbols('A u T')
    y = (1 - A ** 2) / 4
    u1 = (1 - A) / (1 + A)

    def solve_start(J0, P0, J0_1, J0_at1):
        j1, j2, Jm, p2 = sp.symbols('j1 j2 Jm p2')
        Q = u * J0 + y * ((6 * Jm - 2 * j2 + p2) * u ** 2 + j1 * (-u + 2 * u ** 2))
        Ju1 = sp.diff(Q, u).subs(u, u1) / (1 - 2 * y * (1 + u1))
        Peq = (u * P0 + y * (8 * Jm * u ** 3 / (1 - u)
                             - 2 * (1 + u) ** 2 * (Ju1 - j1 * u)
                             + 2 * j2 * u ** 2 - p2 * u ** 2
                             + j1 * (4 * u ** 3 + 6 * u ** 4 / (1 - u))))
        eqs = [Q.subs(u, u1),
               j1 - J0_1 - y * (6 * Jm - j2 + p2 + 4 * j1),
               (j1 + Jm) - J0_at1 - y * (10 * Jm - 2 * j2 + p2 + 5 * j1),
               Peq.subs(u, u1)]
        sol = sp.solve([sp.numer(sp.cancel(sp.together(e))) for e in eqs],
                       [j1, j2, Jm, p2], dict=True)
        assert len(sol) == 1, sol
        return [sp.cancel(sol[0][v]) for v in (j1, j2, Jm, p2)]

    ji1, _, jim, _ = solve_start(3 * u, 4 * u ** 2 / (1 - u), 3, 3)
    jb1, _, jbm, _ = solve_start(u, u ** 2 / (1 - u), 1, 1)
    S = sp.cancel(y * (3 * ji1 + 4 * jim))
    B = sp.cancel(1 + y * (3 * jb1 + 4 * jbm))
    Ph = sp.cancel(y * (jb1 + jbm))
    F1 = sp.cancel(Ph - B ** 2 / (2 + S))
    # minimal polynomial over Q(y): the conjugate is A -> -A
    conj = sp.cancel(F1.subs(A, -A))
    mp = sp.cancel(sp.expand((T - F1) * (T - conj)))
    yy = sp.symbols('yy')
    mp = sp.simplify(mp.subs(A ** 2, 1 - 4 * yy))
    mp = sp.Poly(sp.together(mp).as_numer_denom()[0], T)
    return A, y, S, B, Ph, F1, sp.Poly([sp.factor(c) for c in mp.all_coeffs()], T)


# ------------------------------------------------------------------ hex cells

def hex_defects(kmax):
    """D_1(k) = T_hex(2k,k) - P_k(2k)/2^(k+1), from the enumerated triangle."""
    import hex_diag_deep as hx
    cells = hx.load()
    P, _ = hx.fit(cells, kmax, verbose=False)
    out = {}
    for k in range(1, kmax + 1):
        if (2 * k, k) not in cells:
            continue
        out[k] = Fr(cells[(2 * k, k)]) - hx.evalp(P[k], 2 * k) / Fr(2) ** (k + 1)
    return out


# ------------------------------------------------- the normalised equations

def phi_hex(mp):
    """Phi(x, W) for hex, with W = N(x) = sum_k N_k x^k, N_k = 2^(k+1) D_1(k).

    `mp` is the minimal polynomial from hex_kernel().  Same normalisation as
    the king quartic of `results/below-onset.md` Sec. 3: y = b x
    and N = b F_1(b x) + 1, here with b = 2.
    """
    import sympy as sp
    x, W, Y = sp.symbols('x W yy')
    cs = [sp.expand(c) for c in mp.all_coeffs()][::-1]
    Phi = sp.expand(4 * sum(cs[k].subs(Y, 2 * x) * ((W - 1) / sp.Integer(2)) ** k
                            for k in range(3)))
    p = sp.Poly(Phi, W)
    co = [sp.expand(p.coeff_monomial(W ** k)) for k in range(3)]
    g = sp.gcd(co)
    co = [sp.expand(sp.cancel(c / g)) for c in co]
    if sp.LC(sp.Poly(co[2], x)) < 0:
        co = [sp.expand(-c) for c in co]
    return x, W, co


def annihilates(co, N, order):
    """Phi(x, N(x)) = 0 through x^order, in exact integers (N is integral)."""
    import sympy as sp
    x = sp.symbols('x')
    phi = [[int(v) for v in sp.Poly(c, x).all_coeffs()[::-1]] for c in co]
    return all(v == 0 for v in phi_at_series(phi, [int(v) for v in N], order))


# ---------------------------------------------------------------------- gates


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--kernel', action='store_true')
    ap.add_argument('--boundary', action='store_true')
    ap.add_argument('--kmax', type=int, default=25)
    a = ap.parse_args()

    if a.boundary:
        for name, D in LATTICES.items():
            b = len(D)
            print(f"== {name}: D = {D}, b = {b}, exceptional gaps g < {b}")
            for g in range(1, b):
                for c in 'JP':
                    row = transitions(D, g, c, 3 * b + 6)
                    print(f"   g={g} {c}: {dict(sorted(row.items()))}")
            if b == 1:
                print("   none")
        return 0

    print("== the bulk gap kernel is the autocorrelation of D  [DERIVED]")
    for name, D in LATTICES.items():
        check_kernel(name, D)
    print("== the whole generic row is counting, not fitting  [DERIVED]")
    for name, D in LATTICES.items():
        check_template(name, D)
    if a.kernel:
        return 0

    print("== pair weights W(2) = b^3 - b(b+1)/2 + 4")
    fams = {}
    for name, D in LATTICES.items():
        # TODO(simplify 2026-09-05): king is capped at 20 because the reference
        # walk below is enumerated to 20; --kmax above 20 does not reach king.
        fams[name] = walk_families(D, a.kmax if name != 'king' else 20)
        got = fams[name][0][0]
        assert got == PAIR_WEIGHT[name], (name, got)
        print(f"  {name:6s} W(2) = {got}")

    print("== king: the parametric walk reproduces experiments/depth1_gap_walk.py")
    import depth1_gap_walk as dgw
    ref = dgw.walk_families(20)
    assert fams['king'] == ref, (fams['king'][:8], ref[:8])
    d1_king = series_D1(fams['king'], 3, 20)
    assert d1_king[1:] == dgw.series_D1(ref, 20)[1:], 'king D_1 series'
    print("  (W, W^b, W^p) and D_1(k) agree for l, k <= 20  OK")

    print("== square: the walk closes on two states, so F_1 is a rational "
          "function  [DERIVED]")
    import sympy as sp
    y, S, B, Ph, F1 = square_closed_form()
    print(f"  S = {sp.factor(S)},  B = {sp.factor(B)},  Phat = {sp.factor(Ph)}")
    assert sp.simplify(F1 + 1 / (1 + y)) == 0
    print("  F_1 = -1/(1+y), hence D_1(k) = (-1)^(k+1) for every k >= 1")
    d1_sq = series_D1(fams['square'], 1, a.kmax)
    for k in range(1, a.kmax + 1):
        if d1_sq[k] != Fr((-1) ** (k + 1)):
            raise SystemExit(f"FAIL: square D_1({k}) = {d1_sq[k]}")
    print(f"  the enumerated walk agrees k <= {a.kmax}; "
          f"results/undertow.md measured k <= 6  OK")

    print("== hex: the b = 2 kernel closure  [DERIVED]")
    A, yh, Sh, Bh, Phh, F1h, mp = hex_kernel()
    d1_hex = series_D1(fams['hex'], 2, a.kmax)
    ser = sp.series(F1h.subs(A, sp.sqrt(1 - 4 * sp.Symbol('t'))),
                    sp.Symbol('t'), 0, a.kmax + 1).removeO()
    ser = sp.Poly(sp.expand(ser), sp.Symbol('t'))
    for k in range(0, a.kmax + 1):
        c = Fr(str(ser.coeff_monomial(sp.Symbol('t') ** k)))
        if c != d1_hex[k]:
            raise SystemExit(f"FAIL: hex F_1 coefficient {k}: {c} vs walk {d1_hex[k]}")
    print(f"  the closed form reproduces the enumerated walk, k <= {a.kmax}  OK")
    x, W, co = phi_hex(mp)
    print("  Phi_hex(x, W) = " + " + ".join(
        f"({sp.factor(c)})*W^{k}" for k, c in enumerate(co) if c != 0))
    N = [Fr(0)] + [d1_hex[k] * 2 ** (k + 1) for k in range(1, a.kmax + 1)]
    for k in range(1, a.kmax + 1):
        assert N[k].denominator == 1, (k, N[k])
    assert annihilates(co, N, a.kmax), 'Phi_hex does not annihilate N'
    print(f"  N_k = 2^(k+1) D_1(k) integral and annihilated through x^{a.kmax}: "
          + ", ".join(str(N[k].numerator) for k in range(1, 8)) + ", ...  OK")

    print("== hex onset sharpness: Phi mod 2  [DERIVED]")
    lhs = sp.expand((W + 1) * ((1 + x) * W + x)
                    - sum(co[k] * W ** k for k in range(3)))
    assert all(int(c) % 2 == 0 for c in sp.Poly(lhs, W, x).coeffs()), lhs
    print("  Phi = (W+1)((1+x)W + x) in F_2[x, W], coefficient by coefficient")
    for k in range(1, a.kmax + 1):
        if N[k].numerator % 2 != 1:
            raise SystemExit(f"FAIL: N_{k} is even")
    print("  N(0) = 0 kills the W+1 branch, so (1+x)N = x in F_2[[x]], "
          "so N_k is odd")
    print("  hence D_1(k) != 0 for every k >= 1: the hex onset n >= 2k+1 is sharp")

    print("== hex: against the enumerated triangle  [CHECKED]")
    hx = hex_defects(6)
    for k, want in sorted(hx.items()):
        if d1_hex[k] != want:
            raise SystemExit(f"FAIL: hex D_1({k}) = {d1_hex[k]}, "
                             f"enumeration gives {want}")
    print("  D_1(k) = T_hex(2k,k) - P_k(2k)/2^(k+1) at k = "
          + ", ".join(str(k) for k in sorted(hx)) + "  OK")

    print("== RED controls")
    for name, b, ok in (
            ('square', 2, lambda d: all(d[k] == Fr((-1) ** (k + 1))
                                        for k in range(1, 9))),
            ('hex', 3, lambda d: all(d[k] == hx[k] for k in sorted(hx))),
            ('king', 4, lambda d: d[1:9] == d1_king[1:9])):
        if ok(series_D1(fams[name], b, 8)):
            raise SystemExit(f"FAIL: b -> b+1 did not break {name}")
    print("  b -> b+1 breaks the identity on all three lattices")
    bad = list(N)
    bad[3] += 1
    if annihilates(co, bad, a.kmax):
        raise SystemExit("FAIL: Phi_hex annihilates a perturbed series")
    print("  a perturbed N_3 is not annihilated by Phi_hex")
    D_bad = (-2, 0)
    try:
        check_template('gapped', D_bad, gmax=8, verbose=False)
        raise SystemExit("FAIL: the template fired on a non-interval drift set")
    except AssertionError:
        pass
    print("  the counting template is refused by a non-interval drift set")
    return 0


if __name__ == '__main__':
    sys.exit(main())
