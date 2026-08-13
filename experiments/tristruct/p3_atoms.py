"""p3_atoms.py -- Proposer 3: compute the strip atoms q_H ab initio, H <= 6.

Derivation-blind pipeline (no banked triangle data consumed anywhere here):

  1. Strip sequences S_H(n) = C_H(n) for n <= NLONG from Proposer 3's own
     strip transfer matrix (p3_striptm.build_states / strip_series, written
     from the lattice definition only; cross-checked against p3_enum_out.txt,
     Proposer 3's independent Redelmeier enumerator, on all cells n <= 12).
  2. Minimal recurrence of each S_H by Berlekamp-Massey mod NPRIMES ~60-bit
     primes (degrees must agree across all primes), coefficients CRT-lifted
     to the symmetric range.
  3. EXACT certification over Z: the lifted recurrence is checked on every
     available instance n in [1+deg .. NLONG] against the exact bignum terms.
     A CRT shortfall or a wrong degree cannot survive this step.
  4. Structural checks, exact: q_H squarefree (gcd(q, q') = 1 mod p =>
     gcd = 1 over Q), pairwise coprime; and the column factorization
     p_H = q_H*q_{H-1}*q_{H-2} annihilates the column T(n,H) =
     S_H - 2*S_{H-1} + S_{H-2} on every available instance.
  5. Outputs: data/p3_atoms_q.txt (exact atom coefficients, one per line:
     "H deg c_0 c_1 ... c_deg" for q_H = sum c_j x^{deg-j}, c_0 = 1),
     data/p3_striptm_T.txt (T(n,H), H <= 6, n <= 40, exact -- the value
     table the p3_columns candidate serves).

Run from experiments/tristruct/:  python3 p3_atoms.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from p3_striptm import build_states, strip_series  # noqa: E402

HMAX = 6
NLONG = 160
NPRIMES = 6


def is_prime(n):
    if n < 2:
        return False
    for p in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if n % p == 0:
            return n == p
    d, s = n - 1, 0
    while d % 2 == 0:
        d //= 2
        s += 1
    for a in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        x = pow(a, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(s - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False
    return True


def gen_primes(k, start=10**18):
    out, n = [], start + 9
    while len(out) < k:
        if is_prime(n):
            out.append(n)
        n += 2
    return out


def berlekamp_massey(seq, p):
    """Minimal LFSR of seq over F_p; returns c with c[0]=1 and
    sum_j c[j]*seq[n-j] == 0 (mod p) for all n >= len(c)-1."""
    C, B = [1], [1]
    L, m, b = 0, 1, 1
    for i, s in enumerate(seq):
        d = s % p
        for j in range(1, L + 1):
            d = (d + C[j] * seq[i - j]) % p
        if d == 0:
            m += 1
        elif 2 * L <= i:
            T = C[:]
            coef = d * pow(b, p - 2, p) % p
            C = C + [0] * (len(B) + m - len(C))
            for j, x in enumerate(B):
                C[j + m] = (C[j + m] - coef * x) % p
            L, B, b, m = i + 1 - L, T, d, 1
        else:
            coef = d * pow(b, p - 2, p) % p
            C = C + [0] * (len(B) + m - len(C))
            for j, x in enumerate(B):
                C[j + m] = (C[j + m] - coef * x) % p
            m += 1
    return [x % p for x in C[:L + 1]]


def crt_lift(residues, primes):
    """Symmetric-range CRT lift of one coefficient."""
    M, x = 1, 0
    for r, p in zip(residues, primes):
        g = pow(M % p, p - 2, p) if M % p else None
        t = ((r - x) % p) * g % p
        x += M * t
        M *= p
    if x > M // 2:
        x -= M
    return x


def polymul(a, b):
    out = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[i + j] += x * y
    return out


def polygcd_modp(a, b, p):
    """Monic gcd of int-coeff polys mod p (lists, highest degree first)."""
    a = [x % p for x in a]
    b = [x % p for x in b]

    def strip(v):
        while v and v[0] == 0:
            v = v[1:]
        return v
    a, b = strip(a), strip(b)
    while b:
        inv = pow(b[0], p - 2, p)
        r = a[:]
        while len(r) >= len(b):
            r = strip(r)
            if len(r) < len(b):
                break
            f = r[0] * inv % p
            for j in range(len(b)):
                r[j] = (r[j] - f * b[j]) % p
            r = strip(r[1:]) if r and r[0] == 0 else strip(r)
        a, b = b, strip(r)
    inv = pow(a[0], p - 2, p)
    return [x * inv % p for x in a]


def deriv(q):
    d = len(q) - 1
    return [c * (d - i) for i, c in enumerate(q[:-1])]


def check_recurrence(coeffs, seq, lo):
    """Exact: sum_j coeffs[j]*seq[n-j] == 0 for all n in [lo, len(seq)-1].
    Returns number of instances checked; raises on any failure."""
    d = len(coeffs) - 1
    cnt = 0
    for n in range(max(lo, d), len(seq)):
        s = sum(coeffs[j] * seq[n - j] for j in range(d + 1))
        assert s == 0, "recurrence FAILS at n=%d (order %d)" % (n, d)
        cnt += 1
    return cnt


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    primes = gen_primes(NPRIMES)
    print("primes:", primes)

    S = {0: [0] * (NLONG + 1), -1: [0] * (NLONG + 1)}
    for H in range(1, HMAX + 1):
        S[H], ns = strip_series(H, NLONG)
        print("H=%d  states=%d  S_%d(%d) has %d digits"
              % (H, ns, H, NLONG, len(str(S[H][NLONG]))))
        sys.stdout.flush()

    # cross-check vs own independent enumerator, n <= 12 (blind check)
    mine = {}
    with open(os.path.join(here, "p3_enum_out.txt")) as f:
        for line in f:
            n, h, v = map(int, line.split())
            mine[(n, h)] = v
    bad = 0
    for (n, h), v in mine.items():
        if h <= HMAX:
            t = S[h][n] - 2 * S[h - 1][n] + S[h - 2][n]
            if t != v:
                print("TM vs enum MISMATCH n=%d H=%d" % (n, h))
                bad += 1
    nchk = sum(1 for (n, h) in mine if h <= HMAX)
    print("TM vs own enum: %d cells (n<=12,H<=%d), %d mismatches"
          % (nchk, HMAX, bad))
    assert bad == 0

    # atoms by BM mod p + CRT + exact certification
    q = {}
    for H in range(1, HMAX + 1):
        seq = S[H][1:]          # n = 1..NLONG
        polys = [berlekamp_massey(seq, p) for p in primes]
        degs = {len(c) - 1 for c in polys}
        assert len(degs) == 1, "degree disagrees across primes H=%d: %s" % (H, degs)
        d = degs.pop()
        coeffs = [crt_lift([polys[k][j] for k in range(NPRIMES)], primes)
                  for j in range(d + 1)]
        ninst = check_recurrence(coeffs, seq, 0)
        q[H] = coeffs
        print("q_%d: degree %d, exact-certified on %d instances (n in [%d,%d])"
              % (H, d, ninst, d + 1, NLONG))
        sys.stdout.flush()

    # squarefree + pairwise coprime (gcd = 1 mod p => gcd = 1 over Q)
    p0 = primes[0]
    for H in range(1, HMAX + 1):
        g = polygcd_modp(q[H], deriv(q[H]), p0)
        print("gcd(q_%d, q_%d') mod p: degree %d %s"
              % (H, H, len(g) - 1, "SQUAREFREE" if len(g) == 1 else "NOT SQUAREFREE"))
    for a in range(1, HMAX + 1):
        for b in range(a + 1, HMAX + 1):
            g = polygcd_modp(q[a], q[b], p0)
            assert len(g) == 1, "q_%d, q_%d share a factor" % (a, b)
    print("pairwise coprime: all pairs q_a, q_b (a<b<=%d) have gcd 1" % HMAX)

    # column factorization p_H = q_H q_{H-1} q_{H-2} annihilates T(.,H)
    q[0] = [1]
    q[-1] = [1]
    for H in range(2, HMAX + 1):
        pH = polymul(polymul(q[H], q[H - 1]), q[H - 2] if H >= 3 else [1])
        Tcol = [S[H][n] - 2 * S[H - 1][n] + S[H - 2][n]
                for n in range(NLONG + 1)]
        ninst = check_recurrence(pH, Tcol, len(pH) - 1 + H)
        print("p_%d = q_%d*q_%d*q_%d (order %d) annihilates T(.,%d): "
              "%d exact instances" % (H, H, H - 1, max(H - 2, 0),
                                      len(pH) - 1, H, ninst))

    # outputs
    with open(os.path.join(here, "data", "p3_atoms_q.txt"), "w") as f:
        for H in range(1, HMAX + 1):
            f.write("%d %d %s\n" % (H, len(q[H]) - 1,
                                    " ".join(map(str, q[H]))))
    with open(os.path.join(here, "data", "p3_striptm_T.txt"), "w") as f:
        for H in range(1, HMAX + 1):
            for n in range(1, 41):
                f.write("%d %d %d\n"
                        % (n, H, S[H][n] - 2 * S[H - 1][n] + S[H - 2][n]))
    print("wrote data/p3_atoms_q.txt and data/p3_striptm_T.txt")
    return 0


if __name__ == "__main__":
    sys.exit(main())
