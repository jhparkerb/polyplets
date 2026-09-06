"""known.py -- executable predicates for relations ALREADY BANKED in this repo,
used by verify.py to flag candidates whose predictions coincide with prior work
on the tested cells. A candidate that restates one of these scores zero
(team brief, "What already exists").

Implemented (exact statements from the cited files):

1. Diagonal law (docs/proofs/diagonal-law.md, THEOREM):
       T(n, n-k) = P_k(n) * 3^(n-1-3k)   for all n >= 2k+1,
   with P_k an integer-valued polynomial of degree <= k. Here P_k is
   interpolated exactly (Fraction arithmetic) through the k+1 banked cells at
   n = 2k+1 .. 3k+1, which determine it completely; the grid reaches 3k+1 <= 40
   so this covers k <= 13. For k > 13 the law's shape is still a theorem but
   the polynomial is not determined by in-grid onset cells alone; predict
   returns None there. (Using banked cells is fine HERE: this is the cull
   baseline, not a candidate.)

2. Ternary spine mod 3 (results/arithmetic-structure.md):
   The full mod-3 value of every in-regime cell. With k = n-H:
     * T4 activation: T(n,H) == 0 (mod 3) for n < floor(3H/2)  [column reading]
     * in-regime (n >= 2k+1) with exponent e = n-1-3k >= 1: T == 0 (mod 3)
     * spine n = 3k+1 (e = 0): T(n,H) mod 3 = P_k(n) mod 3 by T1's digit
       product: writing n = sum n_i 3^i, P_k(n) mod 3 = [y^k] prod_i
       W(y^(3^i))^(n_i) over F_3, where W is the root of the spine cubic
       W^3 = W^2 + t, W(0)=1.
   Cells covered: the in-regime wedge n >= 2k+1 plus the proved zero region
   n < floor(3H/2). Below-onset cells outside those return None.

Each known relation exposes:
    name
    predict_value(tri, n, H) -> int | None   (None = relation silent there)
    predict_mod(tri, n, H, m) -> int | None  (residue mod m if the relation
                                              determines it, else None)
"""

from fractions import Fraction

NMAX = 40


class DiagonalLaw:
    name = "diagonal-law (docs/proofs/diagonal-law.md)"

    def __init__(self):
        self._pk_cache = {}

    def _pk(self, tri, k):
        """P_k as exact Newton-form interpolation through n = 2k+1..3k+1."""
        if k in self._pk_cache:
            return self._pk_cache[k]
        if 3 * k + 1 > NMAX or k < 0:
            self._pk_cache[k] = None
            return None
        xs = list(range(2 * k + 1, 3 * k + 2))
        ys = []
        for n in xs:
            e = n - 1 - 3 * k
            t = tri.cell(n, n - k)
            if e >= 0:
                ys.append(Fraction(t, 3 ** e))
            else:
                ys.append(Fraction(t * 3 ** (-e)))
        # divided differences
        dd = list(ys)
        for j in range(1, len(xs)):
            for i in range(len(xs) - 1, j - 1, -1):
                dd[i] = (dd[i] - dd[i - 1]) / (xs[i] - xs[i - j])

        def pk(n):
            acc = Fraction(0)
            prod = Fraction(1)
            for i, x in enumerate(xs):
                acc += dd[i] * prod
                prod *= (n - x)
            return acc

        self._pk_cache[k] = pk
        return pk

    def predict_value(self, tri, n, H):
        if H is None:
            return None
        k = n - H
        if k < 0 or n < 2 * k + 1:
            return None
        pk = self._pk(tri, k)
        if pk is None:
            return None
        e = n - 1 - 3 * k
        v = pk(n) * Fraction(3) ** e
        if v.denominator != 1:
            return None  # e < 0 territory where 3-valuation absorbs; stay silent
        return int(v)

    def predict_mod(self, tri, n, H, m):
        v = self.predict_value(tri, n, H)
        return None if v is None else v % m


def _spine_W(deg):
    """Coefficients of W in F_3[[t]], W^3 = W^2 + t, W(0)=1, to degree deg.

    Over F_3, W(t)^3 = W(t^3), so W(t^3) = W(t)^2 + t coefficient-wise:
    for m >= 1:  (W_[m/3] if 3|m else 0) = [t^m](W^2) + [m==1].
    [t^m](W^2) = 2*W_m*W_0 + sum_{0<i<m} W_i W_{m-i}; W_0 = 1; solve for W_m
    (inverse of 2 mod 3 is 2).
    """
    W = [1] + [0] * deg
    for m in range(1, deg + 1):
        rhs = (W[m // 3] if m % 3 == 0 else 0)
        cross = sum(W[i] * W[m - i] for i in range(1, m)) % 3
        one = 1 if m == 1 else 0
        # 2*W_m + cross + one == rhs (mod 3)
        W[m] = (2 * (rhs - cross - one)) % 3
    return W


class TernarySpineMod3:
    name = "ternary-spine mod 3 (results/arithmetic-structure.md)"

    def __init__(self):
        self._W = _spine_W(NMAX)

    def _pk_mod3(self, n, k):
        """P_k(n) mod 3 via T1's digit product."""
        # digits of n base 3
        digits = []
        nn = n
        while nn:
            digits.append(nn % 3)
            nn //= 3
        # prod_i W(y^(3^i))^(n_i), truncated at degree k
        poly = [1] + [0] * k  # F_3[y] / y^(k+1)
        for i, d in enumerate(digits):
            step = 3 ** i
            if step > k and d > 0:
                # W(y^(3^i)) = 1 + O(y^(3^i)) contributes only its constant 1
                continue
            base = [0] * (k + 1)
            for j in range(0, k // step + 1):
                base[j * step] = self._W[j] if j <= NMAX else 0
            for _ in range(d):
                new = [0] * (k + 1)
                for a in range(k + 1):
                    if poly[a]:
                        for b in range(k + 1 - a):
                            if base[b]:
                                new[a + b] = (new[a + b] + poly[a] * base[b]) % 3
                poly = new
        return poly[k] % 3

    def predict_value(self, tri, n, H):
        return None  # mod-3 relation only

    def predict_mod(self, tri, n, H, m):
        if H is None or m % 3 != 0:
            return None  # determines residues only mod 3 (and hence only if 3|m
            # would need CRT info we don't have; we compare mod 3 in verify.py)
        k = n - H
        if k < 0:
            return None
        e = n - 1 - 3 * k
        r3 = None
        if n < (3 * H) // 2:
            r3 = 0  # T4 activation zero region (proved)
        elif n == (3 * H) // 2:
            # activation boundary: H odd is the spine cell n=3k+1 (T2, via T1's
            # digit product); H even is T3's T(3k,2k) == 1 (mod 3)
            r3 = self._pk_mod3(n, k) if H % 2 == 1 else 1
        elif e >= 1:
            r3 = 0  # in-regime, positive 3-power
        elif n % 3 == 2 and n >= 5 and H == 2 * ((n - 2) // 3) + 1:
            r3 = 2  # deficit-2 last-nonzero row: T(3m+2, 2m+1) == 2 (mod 3), m>=1
        if r3 is None:
            return None  # sleeve cells: residue not determined by the spine
        if m == 3:
            return r3
        return None  # cannot determine residues mod 9, 27, ... from mod 3


class LowStripColumns:
    """The engine's own closed forms for columns H=1,2 (orchestrator/sweep.go
    lowHeightRow): T(n,1) = 1; T(2,2)=3, T(3,2)=10, and
    T(n,2) = 2*T(n-1,2) + T(n-2,2) + 4 for n >= 4. These cells are GENERATED
    by this formula in the banked data (provenance closed-form-lowstrip), so
    any candidate restating them has zero independent-check value."""

    name = "low-strip columns H<=2 (orchestrator/sweep.go lowHeightRow)"

    def __init__(self):
        self._t2 = {2: 3, 3: 10}
        for n in range(4, NMAX + 1):
            self._t2[n] = 2 * self._t2[n - 1] + self._t2[n - 2] + 4

    def predict_value(self, tri, n, H):
        if H == 1:
            return 1 if n >= 1 else None
        if H == 2:
            return self._t2.get(n, 0 if n < 2 else None)
        return None

    def predict_mod(self, tri, n, H, m):
        v = self.predict_value(tri, n, H)
        return None if v is None else v % m


def _polymul(a, b):
    out = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[i + j] += x * y
    return out


class ColumnCFinite:
    """Pinned constant-coefficient column recurrences for H <= 4
    (results/diagonal-formula.md sections 1-2). Atoms (measured minimal
    char polys, coefficients descending):
        q_1 = x - 1
        q_2 = x^2 - 2x - 1
        q_3 = x^4 - 4x^3 + 2x^2 - 1
        q_4 = x^9 - 5x^8 + 2x^7 + 8x^6 - 6x^5 - 12x^4 + 4x^3 + 2x^2 - 3x - 1
    Column char poly p_H = q_H * q_{H-1} * q_{H-2} (q_0 = q_{-1} = 1),
    orders 1, 3, 7, 15 -- exactly section 1's minimal column recurrences.

    Each column is regenerated here from the recurrence seeded ONLY with its
    first onset+order banked terms (small n), then verified against the whole
    banked column. Because an integer C-finite sequence's residues mod any m
    are forced by the recurrence + initial terms, predict_mod answers every
    modulus: a congruence or periodicity claim on columns H <= 4 that matches
    the data is thereby a RESTATEMENT of the pinned recurrence, and the
    verifier's coincidence cull will burn it.

    Section 2's strip identity -- C_H(n) = sum_{h<=H} (H-h+1)*T(n,h) with
    T(n,H) = C_H(n) - 2*C_{H-1}(n) + C_{H-2}(n) -- is an exact re-weighting
    identity; strip_identity_holds() checks it on the banked data (see
    --selftest). A candidate restating it scores zero by definition.
    """

    name = "column C-finite H<=4 (results/diagonal-formula.md sections 1-2)"

    Q = {
        1: [1, -1],
        2: [1, -2, -1],
        3: [1, -4, 2, 0, -1],
        4: [1, -5, 2, 8, -6, -12, 4, 2, -3, -1],
    }

    def __init__(self):
        self._by_tri = {}  # id(tri) -> {H: (onset n0, {n: value})}

    def _build(self, tri):
        cols = self._by_tri.get(id(tri))
        if cols is not None:
            return cols
        cols = {}
        for H in range(1, 5):
            p = [1]
            for j in (H, H - 1, H - 2):
                if j >= 1:
                    p = _polymul(p, self.Q[j])
            ord_ = len(p) - 1
            col = tri.col(H)
            # minimal n0 with the recurrence exact on all banked n >= n0
            def holds(n):
                return col[n] == -sum(p[i] * col[n - i]
                                      for i in range(1, ord_ + 1))
            n0 = next(n for n in range(ord_ + 1, NMAX + 1)
                      if all(holds(x) for x in range(n, NMAX + 1)))
            # regenerate from the seed terms alone and verify byte-exact
            vals = {n: col[n] for n in range(1, n0)}
            for n in range(n0, NMAX + 1):
                vals[n] = -sum(p[i] * vals[n - i] for i in range(1, ord_ + 1))
                assert vals[n] == col[n], (H, n)
            cols[H] = (n0, vals)
        self._by_tri[id(tri)] = cols
        return cols

    def predict_value(self, tri, n, H):
        cols = self._build(tri)
        if H not in cols:
            return None
        n0, vals = cols[H]
        return vals[n] if n >= n0 else None

    def predict_mod(self, tri, n, H, m):
        v = self.predict_value(tri, n, H)
        return None if v is None else v % m

    def onsets(self, tri):
        return {H: n0 for H, (n0, _) in self._build(tri).items()}


def strip_identity_holds(tri):
    """Section 2's exact identity T(n,H) = C_H - 2*C_{H-1} + C_{H-2} with
    C_H(n) = sum_{h<=H} (H-h+1)*T(n,h). Returns number of (n,H) cells checked
    (raises on any mismatch)."""
    def C(n, H):
        return sum((H - h + 1) * tri.cell(n, h) for h in range(1, H + 1)) \
            if H >= 1 else 0
    checked = 0
    for n in range(1, NMAX + 1):
        for H in range(1, n + 1):
            assert tri.cell(n, H) == C(n, H) - 2 * C(n, H - 1) + C(n, H - 2), (n, H)
            checked += 1
    return checked


KNOWN = [DiagonalLaw(), TernarySpineMod3(), LowStripColumns(),
         ColumnCFinite()]
