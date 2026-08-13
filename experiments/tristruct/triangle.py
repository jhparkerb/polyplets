"""triangle.py -- exact-int loader for the banked T(n,H) polyplet triangle.

T(n,H) = number of fixed king-animals (polyplets) with n cells and bounding-box
height exactly H, banked for n,H in 1..40 by the a(40) close-out run.

Data source (authoritative, verified by the team lead):
  results/ns_a40/perheight/h<H>.out   H=1..40, lines "<n> <T(n,H)>", n=1..40
  results/ns_a40/triangle.txt         lines "<n> <a(n)>", n=1..40

Load-time validation (the loader REFUSES to serve data if any fails):
  * every h<H>.out has exactly one line per n=1..40, nonnegative ints
  * row-sum identity: a(n) == sum_H T(n,H) for every n=1..40
  * structural zeros: T(n,H) == 0 whenever H > n
  * anchors: T(40,40) == 3^39 and T(40,39) == 955 * 3^36

Per-cell provenance (matters for independence scoring; see README.md):
  "real-sweep"          H in 3..21  -- kink-carry production sweeps
                        (PROVENANCE.md line 26: "Real sweeps H3-H21")
  "closed-form-Pk"      H in 22..40 -- wired P_k diagonal closed forms,
                        k = n-H <= 18 (same line of PROVENANCE.md)
  "closed-form-lowstrip" H in 1..2  -- engine's analytic low-strip rows
                        (orchestrator/sweep.go lowHeightRow), never swept

Usage:
    from triangle import Triangle
    tri = Triangle.load()          # default repo paths, full validation
    tri.cell(40, 21)               # exact Python int
    tri.row(37)                    # {H: T(37,H)} for all H with 1<=H<=40
    tri.col(14)                    # {n: T(n,14)}
    tri.diag(3)                    # {n: T(n, n-3)}  (k = n-H fixed)
    tri.slice(2, -1, 30)           # cells with 2n - H == 30, sorted by n
    tri.rowsum(40)                 # a(40)
    tri.provenance(40, 25)         # "closed-form-Pk"
    tri.is_real_sweep(40, 21)      # True

Triangle.from_data(cells, rowsums) builds an instance from in-memory dicts
(same validation) -- used by the test suite to plant corrupt data without
touching the banked files.
"""

import os

NMAX = 40
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PERHEIGHT_DIR = os.path.join(REPO, "results", "ns_a40", "perheight")
TRIANGLE_TXT = os.path.join(REPO, "results", "ns_a40", "triangle.txt")


class TriangleDataError(Exception):
    """Raised when the banked data fails a load-time validation check."""


def _provenance(n, H):
    if 3 <= H <= 21:
        return "real-sweep"
    if H >= 22:
        return "closed-form-Pk"
    return "closed-form-lowstrip"


class Triangle:
    def __init__(self, cells, rowsums):
        # cells: {(n,H): int} complete over 1..NMAX squared; rowsums: {n: int}
        self._cells = cells
        self._rowsums = rowsums
        self._validate()

    # ---------- construction ----------

    @classmethod
    def load(cls, perheight_dir=PERHEIGHT_DIR, triangle_txt=TRIANGLE_TXT):
        cells = {}
        for H in range(1, NMAX + 1):
            path = os.path.join(perheight_dir, "h%d.out" % H)
            seen = set()
            with open(path) as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    a, b = line.split()
                    n, v = int(a), int(b)
                    if not (1 <= n <= NMAX):
                        raise TriangleDataError("%s: n=%d out of range" % (path, n))
                    if n in seen:
                        raise TriangleDataError("%s: duplicate n=%d" % (path, n))
                    if v < 0:
                        raise TriangleDataError("%s: negative count at n=%d" % (path, n))
                    seen.add(n)
                    cells[(n, H)] = v
            if seen != set(range(1, NMAX + 1)):
                raise TriangleDataError("%s: missing rows %s" % (path, sorted(set(range(1, NMAX + 1)) - seen)))
        rowsums = {}
        with open(triangle_txt) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                a, b = line.split()
                rowsums[int(a)] = int(b)
        if set(rowsums) != set(range(1, NMAX + 1)):
            raise TriangleDataError("%s: expected n=1..%d" % (triangle_txt, NMAX))
        return cls(cells, rowsums)

    @classmethod
    def from_data(cls, cells, rowsums):
        """Build from in-memory dicts (test hook). Same validation as load()."""
        return cls(dict(cells), dict(rowsums))

    def _validate(self):
        for n in range(1, NMAX + 1):
            for H in range(1, NMAX + 1):
                if (n, H) not in self._cells:
                    raise TriangleDataError("missing cell (n=%d, H=%d)" % (n, H))
                if H > n and self._cells[(n, H)] != 0:
                    raise TriangleDataError(
                        "structural zero violated: T(%d,%d)=%d != 0" % (n, H, self._cells[(n, H)]))
        for n in range(1, NMAX + 1):
            s = sum(self._cells[(n, H)] for H in range(1, NMAX + 1))
            if s != self._rowsums[n]:
                raise TriangleDataError(
                    "row-sum identity FAILS at n=%d: sum_H T = %d but a(n) = %d"
                    % (n, s, self._rowsums[n]))
        if self._cells[(40, 40)] != 3 ** 39:
            raise TriangleDataError("anchor FAILS: T(40,40) != 3^39")
        if self._cells[(40, 39)] != 955 * 3 ** 36:
            raise TriangleDataError("anchor FAILS: T(40,39) != 955*3^36")

    # ---------- accessors (all exact ints) ----------

    def cell(self, n, H):
        """T(n,H). Raises KeyError outside the 1..40 grid."""
        return self._cells[(n, H)]

    def rowsum(self, n):
        """a(n) = sum_H T(n,H)."""
        return self._rowsums[n]

    def row(self, n):
        """{H: T(n,H)} for H=1..40 (includes structural zeros)."""
        return {H: self._cells[(n, H)] for H in range(1, NMAX + 1)}

    def col(self, H):
        """{n: T(n,H)} for n=1..40."""
        return {n: self._cells[(n, H)] for n in range(1, NMAX + 1)}

    def diag(self, k):
        """{n: T(n, n-k)} for the diagonal k = n-H, over in-grid n."""
        return {n: self._cells[(n, n - k)]
                for n in range(max(1, k + 1), NMAX + 1) if 1 <= n - k <= NMAX}

    def slice(self, s, t, c):
        """[((n,H), T(n,H))] with s*n + t*H == c, sorted by (n,H)."""
        out = []
        for n in range(1, NMAX + 1):
            for H in range(1, NMAX + 1):
                if s * n + t * H == c:
                    out.append(((n, H), self._cells[(n, H)]))
        return out

    def cells(self):
        """Iterate ((n,H), value) over the full grid."""
        return iter(sorted(self._cells.items()))

    # ---------- provenance ----------

    def provenance(self, n, H):
        """One of "real-sweep", "closed-form-Pk", "closed-form-lowstrip"."""
        if not (1 <= n <= NMAX and 1 <= H <= NMAX):
            raise KeyError((n, H))
        return _provenance(n, H)

    def is_real_sweep(self, n, H):
        return self.provenance(n, H) == "real-sweep"


if __name__ == "__main__":
    t = Triangle.load()
    print("loaded %d cells; all validations passed" % (NMAX * NMAX))
    print("a(40) =", t.rowsum(40))
    print("real-sweep cells: %d of %d nonzero cells"
          % (sum(1 for (n, H), v in t.cells() if v and t.is_real_sweep(n, H)),
             sum(1 for _, v in t.cells() if v)))
