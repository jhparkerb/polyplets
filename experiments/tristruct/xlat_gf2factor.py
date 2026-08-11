"""Factor the characteristic polynomials of the verified column recurrences
over GF(2), to name the MECHANISM behind the mod-2 period sizes in
xlat_verdicts.py (cross-lattice control, triangle-structure hunt).

For a C-finite sequence with integer recurrence coeffs c1..cr, the residues
mod 2 evolve by the companion matrix of chi(x) = x^r - c1 x^(r-1) - ... - cr
over GF(2).  The eventual period divides lcm over irreducible factors p_i^e_i
of chi mod 2 of (ord of a root of p_i, i.e. a divisor of 2^deg(p_i) - 1)
times 2^ceil(log2 e_i); a factor x^e contributes only preperiod.  A fully
unipotent chi mod 2 (chi = x^a (x+1)^b) forces a period that is a power of 2
<= 2^ceil(log2 b) — the "tiny 2-adic period" phenomenon.  A high-order
irreducible factor forces a long period.

Polynomials over GF(2) are ints (bit k = coeff of x^k); factorization is
trial division by irreducibles generated in degree order (degrees here are
<= 39, and the factors that appear are small).

Usage: python3 xlat_gf2factor.py   (from experiments/tristruct/, instant)
"""


def pmul(a, b):
    r = 0
    while b:
        if b & 1:
            r ^= a
        a <<= 1
        b >>= 1
    return r


def pmod(a, b):
    db = b.bit_length()
    while a.bit_length() >= db:
        a ^= b << (a.bit_length() - db)
    return a


def deg(a):
    return a.bit_length() - 1


def irreducibles(maxdeg):
    """All irreducible polys over GF(2) of degree 1..maxdeg, ascending."""
    out = []
    for p in range(2, 1 << (maxdeg + 1)):
        if not any(deg(q) <= deg(p) // 2 and pmod(p, q) == 0 for q in out):
            out.append(p)
    return out


def factor(p, irr):
    fs = {}
    for q in irr:
        while deg(p) >= deg(q) and pmod(p, q) == 0:
            # exact division p / q
            quo = 0
            r = p
            while deg(r) >= deg(q):
                s = deg(r) - deg(q)
                quo ^= 1 << s
                r ^= q << s
            assert r == 0
            fs[q] = fs.get(q, 0) + 1
            p = quo
        if p == 1:
            break
    assert p == 1, f"unfactored part {bin(p)}"
    return fs


def pstr(q):
    ts = [("x^%d" % k if k > 1 else ("x" if k == 1 else "1"))
          for k in range(deg(q), -1, -1) if (q >> k) & 1]
    return "+".join(ts)


def ord2(q):
    """Multiplicative order of x mod q (q irreducible, != x)."""
    d = deg(q)
    e = (1 << d) - 1
    # order divides 2^d - 1; try divisors
    divs = [k for k in range(1, e + 1) if e % k == 0]
    for k in divs:
        # x^k mod q == 1 ?
        r, base, kk = 1, 2, k
        while kk:
            if kk & 1:
                r = pmod(pmul(r, base), q)
            base = pmod(pmul(base, base), q)
            kk >>= 1
        if r == 1:
            return k
    raise AssertionError


RECURRENCES = {
    # column: coeffs c1..cr with T(n) = sum ci T(n-i); from xlat_verdicts.py
    'king  T(n,3) r=7': [7, -15, 9, 3, -5, 1, 1],
    'king  T(n,4) r=15': [11, -41, 49, 39, -113, -7, 155, -57, -67, 63, 19,
                          -17, 1, 5, 1],
    'square T(n,3) r=14': [5, -6, -4, 8, 1, 2, -8, 0, -1, 9, -2, -1, -3, 1],
    'square T(n,4) r=39': [7, -12, -12, 27, 58, -68, -107, 26, 85, 245, -41,
                           -257, -376, -29, 523, 559, 27, -680, -694, -112,
                           858, 700, 170, -740, -651, -167, 585, 387, 114,
                           -289, -139, 12, 164, 46, 2, -29, 2, -2, 1],
    'tri   T(n,3) r=23': [4, -3, -3, -3, 14, -1, -16, -10, 45, -29, 1, -16,
                          58, -41, -42, 63, 5, -40, 0, 31, 2, -14, -4],
}


def main():
    irr = irreducibles(10)
    for name, cs in RECURRENCES.items():
        r = len(cs)
        chi = 1 << r
        for i, c in enumerate(cs):
            if c & 1:
                chi ^= 1 << (r - 1 - i)
        fs = factor(chi, irr)
        parts = []
        for q, e in sorted(fs.items()):
            parts.append(f"({pstr(q)})^{e}" if e > 1 else f"({pstr(q)})")
        odd = 1
        for q in fs:
            if q not in (2,):        # q == x contributes nothing to period
                if q == 3:           # x+1: root 1, order 1
                    continue
                o = ord2(q)
                odd = odd * o // __import__('math').gcd(odd, o)
        print(f"{name}: chi mod 2 = {' '.join(parts)}   "
              f"[odd part of period divides {odd}]")


if __name__ == '__main__':
    main()
