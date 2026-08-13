"""sweep.py -- mechanical low-order hypothesis sweep over the T(n,H) triangle.

Purpose, exact command, machine, cost (docs/job-checklist.md):
  purpose : the team brief's no-judgment-cost sweep of small (s,t) slices and
            local stencils through verify.py's fit-low/predict-high rule
  command : python3 experiments/tristruct/sweep.py   (from the repo root or
            this directory; writes sweep_report.md next to this file)
  machine : gympie (local), single core, pure Python exact arithmetic
  cost    : measured 0.8 s wall, <300 MB RAM (smoke-timed, then measured)
  resume  : stateless; just re-run

SEARCH SPACE (stated exactly; anything outside it is NOT covered):

  Slices s*n + t*H = c, cells restricted to the triangle 1 <= H <= n <= 40,
  ordered by increasing n. Directions: all primitive (s,t) with |s| <= 3,
  1 <= t <= 3 (canonical sign t > 0; t = 0 -- rows -- is excluded because a
  fixed-n row has no n-direction to extrapolate, so the fit-low/predict-high
  rule cannot apply to it). That is 15 directions; the bound |s|,|t| <= 3 is
  where slices stop having enough lattice points in the 40x40 triangle: a
  slice is only TESTABLE if it has >= MIN_FIT points with n <= 22 and
  >= MIN_HOLD points with 23 <= n <= 39, and steeper directions fail that
  filter (the report counts exactly how many slices each direction lost to
  it). The row-sum sequence a(n) is swept as one extra sequence.

  Per testable sequence, the hypothesis battery (all fitted ONLY on n <= 22,
  then pushed through verify.py, which refits in its sandbox and scores
  n = 23..39 by row; row 40 reported separately):

  1. P-recursive: sum_{i=0}^{r} p_i(n) u(n-th previous position) = 0 with
     polynomial coefficients p_i of degree <= d, for d = 0..2, r = 1..7,
     (r+1)(d+1) <= 16 unknowns, needing >= unknowns+3 fit equations
     (overdetermined by >= 3). Exact Fraction nullspace; first (d,r) with a
     1+-dim nullspace is taken (minimal class), primitive integer vector.
     d = 0 is the C-finite case. Free parameters = (r+1)(d+1) - 1.
  2. Congruences mod m for m in MODULI (below):
     (i)  eventually-constant residue (last CONST_TAIL fit positions equal;
          onset = start of the constant tail within the fit region), 1 param;
     (ii) periodic residue, period p = 2..9, >= 2p+4 fit points, 0 params
          beyond the p residues (params = p);
     (iii) order-2 recurrence u_x = a*u_{x-1} + b*u_{x-2} (mod m), brute-forced
          over (a,b), only for m <= 13 and only where (i) and (ii) both
          failed; params = 2.
     Tried in that order per modulus; first hit wins (a period-2 constant
     sequence is reported as constant, not as period 4, etc.).

  Local stencils: every subset S of the offset box {0,1,2}x{0,1,2} (offsets
  (dn,dH) from a base cell) with 2 <= |S| <= 5, constant integer
  coefficients from the exact nullspace of the fit-region equations (base
  cells whose touched cells all lie in the triangle and have n <= 22, at
  least one touched cell nonzero, >= 20 equations). Vectors with a zero
  coefficient are skipped (that identity lives in a smaller stencil).
  Candidates are boolean identities; the equation's target cell is its
  lexicographically largest touched cell, so holdout is by target row n.

NOT covered (do not claim the sweep excluded these): |s| or |t| >= 4;
recurrence order > 7 or coefficient degree > 2; moduli outside MODULI;
recurrences mod m of order > 2 or for m > 13; stencils outside the 3x3 box
or with > 5 cells; any nonlinear (multiplicative, convolutional) hypothesis.

Output: sweep_report.md (survivors ranked, then the FULL negative record --
every testable sequence x hypothesis class with its verdict, plus every
slice skipped for support and every skipped-direction count). Exit 0 always
(the report is the result); exit 1 on data validation failure.
"""

import math
import os
import sys
import time
from fractions import Fraction

from triangle import Triangle, TriangleDataError, NMAX
from schema import Candidate
import verify

MODULI = [2, 3, 4, 5, 7, 8, 9, 11, 13, 16, 17, 19, 23, 25, 27,
          29, 31, 32, 49, 64, 81, 121, 125, 128, 169, 243, 256]
REC_MOD_MAX = 13     # (iii) brute force bound
MIN_FIT = 10         # min fit points (n <= 22) for a testable sequence
MIN_HOLD = 5         # min holdout points (23 <= n <= 39)
CONST_TAIL = 6       # (i): last this-many fit residues must agree
FIT_MAX_N = 22
MAX_UNKNOWNS = 16
STENCIL_MIN_EQS = 20

INDEP = dict(
    input_footprint="banked triangle cells on the swept slice (mechanical)",
    derivation_independence="none: fitted to banked data on n<=22 by the sweep",
    rule_independence="none: same enumeration lineage as the banked triangle")


# ---------------------------------------------------------------- linalg

def nullspace(rows):
    """Nullspace basis of a matrix (list of Fraction/int rows), exact."""
    if not rows:
        return []
    m = [list(map(Fraction, r)) for r in rows]
    ncol = len(m[0])
    piv_of_col = {}
    r = 0
    for c in range(ncol):
        piv = next((i for i in range(r, len(m)) if m[i][c] != 0), None)
        if piv is None:
            continue
        m[r], m[piv] = m[piv], m[r]
        inv = m[r][c]
        m[r] = [x / inv for x in m[r]]
        for i in range(len(m)):
            if i != r and m[i][c] != 0:
                f = m[i][c]
                m[i] = [a - f * b for a, b in zip(m[i], m[r])]
        piv_of_col[c] = r
        r += 1
        if r == len(m):
            break
    basis = []
    free = [c for c in range(ncol) if c not in piv_of_col]
    for fc in free:
        v = [Fraction(0)] * ncol
        v[fc] = Fraction(1)
        for c, pr in piv_of_col.items():
            v[c] = -m[pr][fc]
        basis.append(v)
    return basis


def primitive(vec):
    """Scale a rational vector to coprime integers, first nonzero > 0."""
    from functools import reduce
    den = reduce(lambda a, b: a * b // math.gcd(a, b),
                 (f.denominator for f in vec), 1)
    ints = [int(f * den) for f in vec]
    g = reduce(math.gcd, (abs(x) for x in ints if x), 1) or 1
    ints = [x // g for x in ints]
    lead = next((x for x in ints if x), 0)
    if lead < 0:
        ints = [-x for x in ints]
    return ints


# ---------------------------------------------------------------- sequences

def slice_positions(s, t, c):
    """In-triangle positions of slice s*n+t*H=c as [(n,H)] increasing in n."""
    out = []
    for n in range(1, NMAX + 1):
        if t != 0:
            num = c - s * n
            if num % t:
                continue
            H = num // t
        else:
            continue
        if 1 <= H <= n:
            out.append((n, H))
    return out


def directions():
    out = []
    for t in range(1, 4):
        for s in range(-3, 4):
            if math.gcd(abs(s), t) == 1:
                out.append((s, t))
    return out


# ---------------------------------------------------------------- hypotheses

def prec_fit_from_view(getcell, pos, d, r):
    """Fit sum_i p_i(n) u_{x-i} = 0, deg p_i <= d, on positions with
    target n <= FIT_MAX_N. getcell(n,H) -> value. Returns primitive integer
    coefficient vector (a_{i,j}) or None."""
    nunk = (r + 1) * (d + 1)
    eqs = []
    for x in range(r, len(pos)):
        n_t = pos[x][0]
        if n_t > FIT_MAX_N:
            break
        row = []
        for i in range(r + 1):
            u = getcell(*pos[x - i])
            for j in range(d + 1):
                row.append(u * n_t ** j)
        eqs.append(row)
    if len(eqs) < nunk + 3:
        return None
    basis = nullspace(eqs)
    if not basis:
        return None
    return primitive(basis[0])


def make_prec_candidate(seq_id, s, t, c, pos, d, r, coeffs_hint):
    """P-recursive candidate; fit re-derives the nullspace inside the sandbox."""
    posidx = {p: i for i, p in enumerate(pos)}
    nunk = (r + 1) * (d + 1)

    def fit(view):
        vec = prec_fit_from_view(view.cell, pos, d, r)
        if vec is None:
            raise ValueError("nullspace vanished on refit")
        return vec

    def predict(pvec, n, H, ctx):
        x = posidx[(n, H)]
        # sum_i p_i(n) u_{x-i} = 0  ->  solve for u_x
        lead = sum(pvec[j] * n ** j for j in range(d + 1))
        if lead == 0:
            return None
        acc = 0
        for i in range(1, r + 1):
            u = ctx.cell(*pos[x - i])
            pi = sum(pvec[i * (d + 1) + j] * n ** j for j in range(d + 1))
            acc += pi * u
        q = Fraction(-acc, lead)
        return int(q) if q.denominator == 1 else None

    return Candidate(
        id="%s-prec-r%d-d%d" % (seq_id, r, d), proposer="sweep",
        statement="order-%d recurrence, poly-coeff deg<=%d, on %s" % (r, d, seq_id),
        tier="B", kind="value",
        region=lambda n, H, _pos=set(pos[r:]): (n, H) in _pos,
        n_params=nunk - 1, fit=fit, predict=predict, **INDEP)


def congruence_candidates(seq_id, pos, fitvals):
    """Battery 2 on one slice. fitvals = [(n,H,value)] for n<=FIT_MAX_N."""
    cands = []
    posidx = {(n, H): i for i, (n, H) in enumerate(pos)}
    for m in MODULI:
        res = [v % m for (_, _, v) in fitvals]
        hit = None
        # (i) eventually constant
        if len(res) >= CONST_TAIL and len(set(res[-CONST_TAIL:])) == 1:
            r0 = res[-1]
            onset = len(res)
            while onset > 0 and res[onset - 1] == r0:
                onset -= 1
            n_onset = fitvals[onset][0]
            cands.append(Candidate(
                id="%s-mod%d-const" % (seq_id, m), proposer="sweep",
                statement="%s == %d (mod %d) for n >= %d" % (seq_id, r0, m, n_onset),
                tier="C", kind="congruence", modulus=m,
                region=lambda n, H, _pos=set(pos), _n0=n_onset:
                    (n, H) in _pos and n >= _n0,
                n_params=1,
                fit=lambda view, _m=m, _pos=pos, _n0=n_onset:
                    _const_refit(view, _m, _pos, _n0),
                predict=lambda p, n, H, ctx: p, **INDEP))
            hit = "const"
        # (ii) periodic
        if hit is None:
            for p in range(2, 10):
                if len(res) >= 2 * p + 4 and all(
                        res[i] == res[i % p] for i in range(len(res))) \
                        and len(set(res[:p])) > 1:
                    cands.append(Candidate(
                        id="%s-mod%d-per%d" % (seq_id, m, p), proposer="sweep",
                        statement="%s mod %d periodic with period %d along the "
                                  "slice" % (seq_id, m, p),
                        tier="C", kind="congruence", modulus=m,
                        region=lambda n, H, _pos=set(pos): (n, H) in _pos,
                        n_params=p,
                        fit=lambda view, _m=m, _pos=pos, _p=p:
                            _periodic_refit(view, _m, _pos, _p),
                        predict=lambda pr, n, H, ctx,
                                       _idx=posidx, _p=p: pr[_idx[(n, H)] % _p],
                        **INDEP))
                    hit = "per%d" % p
                    break
        # (iii) order-2 recurrence mod m
        if hit is None and m <= REC_MOD_MAX and len(res) >= 10:
            found = None
            for a in range(m):
                for b in range(m):
                    if all(res[i] == (a * res[i - 1] + b * res[i - 2]) % m
                           for i in range(2, len(res))):
                        found = (a, b)
                        break
                if found:
                    break
            if found:
                a, b = found
                cands.append(Candidate(
                    id="%s-mod%d-rec2" % (seq_id, m), proposer="sweep",
                    statement="%s: u = %d*u' + %d*u'' (mod %d) along the slice"
                              % (seq_id, a, b, m),
                    tier="C", kind="congruence", modulus=m,
                    region=lambda n, H, _pos=set(pos[2:]): (n, H) in _pos,
                    n_params=2,
                    fit=lambda view, _m=m, _pos=pos: _rec2_refit(view, _m, _pos),
                    predict=lambda pr, n, H, ctx, _pos=pos, _idx=posidx, _m=m:
                        (pr[0] * ctx.cell(*_pos[_idx[(n, H)] - 1])
                         + pr[1] * ctx.cell(*_pos[_idx[(n, H)] - 2])) % _m,
                    **INDEP))
    return cands


def _const_refit(view, m, pos, n_onset):
    vals = [view.cell(n, H) % m for n, H in pos
            if n_onset <= n <= view.max_n]
    if len(set(vals)) != 1:
        raise ValueError("not constant on refit")
    return vals[0]


def _periodic_refit(view, m, pos, p):
    vals = [view.cell(n, H) % m for n, H in pos if n <= view.max_n]
    if not all(vals[i] == vals[i % p] for i in range(len(vals))):
        raise ValueError("not periodic on refit")
    return vals[:p]


def _rec2_refit(view, m, pos):
    vals = [view.cell(n, H) % m for n, H in pos if n <= view.max_n]
    for a in range(m):
        for b in range(m):
            if all(vals[i] == (a * vals[i - 1] + b * vals[i - 2]) % m
                   for i in range(2, len(vals))):
                return (a, b)
    raise ValueError("no order-2 recurrence on refit")


# ---------------------------------------------------------------- rowsum

def rowsum_candidates(tri):
    """Same battery classes on the a(n) sequence itself (scope rowsum)."""
    cands = []
    fitvals = [tri.rowsum(n) for n in range(1, FIT_MAX_N + 1)]
    # P-recursive on a(n) (a global P-recurrence is refuted in the repo, but
    # the sweep tests it mechanically anyway -- a negative here is a record)
    for d in range(0, 3):
        for r in range(1, 8):
            nunk = (r + 1) * (d + 1)
            if nunk > MAX_UNKNOWNS:
                continue
            eqs = []
            for x in range(r, FIT_MAX_N):
                n_t = x + 1
                row = []
                for i in range(r + 1):
                    for j in range(d + 1):
                        row.append(fitvals[x - i] * n_t ** j)
                eqs.append(row)
            if len(eqs) < nunk + 3 or not nullspace(eqs):
                continue

            def fit(view, _d=d, _r=r):
                eqs = []
                for x in range(_r, view.max_n):
                    n_t = x + 1
                    row = []
                    for i in range(_r + 1):
                        for j in range(_d + 1):
                            row.append(view.rowsum(x + 1 - i) * n_t ** j)
                    eqs.append(row)
                basis = nullspace(eqs)
                if not basis:
                    raise ValueError("nullspace vanished on refit")
                return primitive(basis[0])

            def predict(pvec, n, H, ctx, _d=d, _r=r):
                lead = sum(pvec[j] * n ** j for j in range(_d + 1))
                if lead == 0:
                    return None
                acc = 0
                for i in range(1, _r + 1):
                    pi = sum(pvec[i * (_d + 1) + j] * n ** j
                             for j in range(_d + 1))
                    acc += pi * ctx.rowsum(n - i)
                q = Fraction(-acc, lead)
                return int(q) if q.denominator == 1 else None

            cands.append(Candidate(
                id="a(n)-prec-r%d-d%d" % (r, d), proposer="sweep",
                statement="order-%d poly-coeff recurrence on a(n)" % r,
                tier="A", kind="value", scope="rowsum",
                region=lambda n, H, _r=r: n > _r,
                n_params=nunk - 1, fit=fit, predict=predict, **INDEP))
            break  # minimal r for this d
    # congruences on a(n)
    pos = [(n, None) for n in range(1, NMAX + 1)]
    for m in MODULI:
        res = [v % m for v in fitvals]
        if len(set(res[-CONST_TAIL:])) == 1:
            r0 = res[-1]
            onset = len(res)
            while onset > 0 and res[onset - 1] == r0:
                onset -= 1
            n_onset = onset + 1

            def fit(view, _m=m, _n0=n_onset):
                vals = [view.rowsum(n) % _m for n in range(_n0, view.max_n + 1)]
                if len(set(vals)) != 1:
                    raise ValueError("not constant on refit")
                return vals[0]

            cands.append(Candidate(
                id="a(n)-mod%d-const" % m, proposer="sweep",
                statement="a(n) == %d (mod %d) for n >= %d" % (r0, m, n_onset),
                tier="C", kind="congruence", modulus=m, scope="rowsum",
                region=lambda n, H, _n0=n_onset: n >= _n0,
                n_params=1, fit=fit,
                predict=lambda p, n, H, ctx: p, **INDEP))
        else:
            for p in range(2, 10):
                if all(res[i] == res[i % p] for i in range(len(res))) \
                        and len(set(res[:p])) > 1:
                    def fit(view, _m=m, _p=p):
                        vals = [view.rowsum(n) % _m
                                for n in range(1, view.max_n + 1)]
                        if not all(vals[i] == vals[i % _p]
                                   for i in range(len(vals))):
                            raise ValueError("not periodic on refit")
                        return vals[:_p]

                    cands.append(Candidate(
                        id="a(n)-mod%d-per%d" % (m, p), proposer="sweep",
                        statement="a(n) mod %d has period %d" % (m, p),
                        tier="C", kind="congruence", modulus=m, scope="rowsum",
                        region=lambda n, H: True,
                        n_params=p, fit=fit,
                        predict=lambda pr, n, H, ctx, _p=p: pr[(n - 1) % _p],
                        **INDEP))
                    break
    return cands


# ---------------------------------------------------------------- stencils

def stencil_candidates(tri):
    """Constant-coefficient linear identities on small local stencils."""
    from itertools import combinations
    box = [(dn, dH) for dn in range(3) for dH in range(3)]
    cands = []
    tried = 0
    for size in (2, 3, 4, 5):
        for S in combinations(box, size):
            tried += 1
            eqs = []
            for n in range(1, FIT_MAX_N + 1):
                for H in range(1, n + 1):
                    cellsv = []
                    ok = True
                    nz = False
                    for dn, dH in S:
                        n2, H2 = n + dn, H + dH
                        if not (1 <= H2 <= n2 <= FIT_MAX_N):
                            ok = False
                            break
                        v = tri.cell(n2, H2)
                        nz = nz or v != 0
                        cellsv.append(v)
                    if ok and nz:
                        eqs.append(cellsv)
            if len(eqs) < STENCIL_MIN_EQS:
                continue
            basis = nullspace(eqs)
            for vec in basis[:2]:
                iv = primitive(vec)
                if any(x == 0 for x in iv):
                    continue  # lives in a smaller stencil
                cands.append(_make_stencil_candidate(S, iv))
    return cands, tried


def _make_stencil_candidate(S, iv):
    # target = lexicographically largest offset; check reads the others
    ti = max(range(len(S)), key=lambda i: S[i])
    tdn, tdH = S[ti]

    def region(n, H):
        # (n,H) is the TARGET cell of some base cell (n-tdn, H-tdH)
        bn, bH = n - tdn, H - tdH
        if not (1 <= bH <= bn):
            return False
        return all(1 <= bH + dH <= bn + dn <= NMAX for dn, dH in S)

    def fit(view):
        eqs = []
        for n in range(1, view.max_n + 1):
            for H in range(1, n + 1):
                row = []
                ok = True
                nz = False
                for dn, dH in S:
                    n2, H2 = n + dn, H + dH
                    if not (1 <= H2 <= n2 <= view.max_n):
                        ok = False
                        break
                    v = view.cell(n2, H2)
                    nz = nz or v != 0
                    row.append(v)
                if ok and nz:
                    eqs.append(row)
        basis = nullspace(eqs)
        if not basis:
            raise ValueError("nullspace vanished on refit")
        for vec in basis:
            piv = primitive(vec)
            if all(x != 0 for x in piv):
                return piv
        raise ValueError("only degenerate vectors on refit")

    def check(pvec, n, H, value, ctx):
        bn, bH = n - tdn, H - tdH
        acc = 0
        for i, (dn, dH) in enumerate(S):
            n2, H2 = bn + dn, bH + dH
            v = value if (n2, H2) == (n, H) else ctx.cell(n2, H2)
            acc += pvec[i] * v
        return acc == 0

    return Candidate(
        id="stencil-%s" % "".join("%d%d" % o for o in S), proposer="sweep",
        statement="linear identity sum c_i*T(n+dn,H+dH)=0 on offsets %s, "
                  "coeffs %s (fit)" % (list(S), iv),
        tier="C", kind="boolean",
        region=region, n_params=len(S) - 1, fit=fit, check=check, **INDEP)


# ---------------------------------------------------------------- driver

def main():
    t0 = time.time()
    try:
        tri = Triangle.load()
    except TriangleDataError as e:
        print("DATA VALIDATION FAILED: %s" % e, file=sys.stderr)
        return 1

    survivors = []
    negatives = []      # (seq_id, class, verdict-string)
    skipped = []        # (direction, c, reason)
    dir_stats = {}

    def run(cand):
        r = verify.verify_candidate(cand, tri)
        if r["verdict"] == "SURVIVES":
            survivors.append(r)
        else:
            negatives.append((r["id"], r["statement"], r["verdict"]))
        return r

    # ---- slices ----
    n_seq = 0
    for s, t in directions():
        cs = sorted({s * n + t * H for n in range(1, NMAX + 1)
                     for H in range(1, n + 1)})
        tested = lost = 0
        for c in cs:
            pos = slice_positions(s, t, c)
            nfit = sum(1 for n, _ in pos if n <= FIT_MAX_N)
            nhold = sum(1 for n, _ in pos if FIT_MAX_N < n <= 39)
            if nfit < MIN_FIT or nhold < MIN_HOLD:
                lost += 1
                skipped.append(((s, t), c, "support %d fit/%d holdout" % (nfit, nhold)))
                continue
            tested += 1
            n_seq += 1
            seq_id = "S(%d,%d)c%d" % (s, t, c)
            # P-recursive battery: minimal (d,r) hit per d
            for d in range(0, 3):
                got = False
                for r in range(1, 8):
                    if (r + 1) * (d + 1) > MAX_UNKNOWNS:
                        break
                    vec = prec_fit_from_view(tri.cell, pos, d, r)
                    # NOTE: candidate refits inside the sandbox; this call
                    # only touches targets with n <= FIT_MAX_N by construction
                    if vec is not None:
                        run(make_prec_candidate(seq_id, s, t, c, pos, d, r, vec))
                        got = True
                        break
                if got:
                    break  # minimal d too; deeper d adds params, not info
            else:
                negatives.append((seq_id + "-prec",
                                  "no P-recursion r<=5,d<=2 fits n<=22",
                                  "BARREN(no fit-region solution)"))
            # congruence battery
            fitvals = [(n, H, tri.cell(n, H)) for n, H in pos if n <= FIT_MAX_N]
            got_any = set()
            for cand in congruence_candidates(seq_id, pos, fitvals):
                run(cand)
                got_any.add(cand.modulus)
            for m in MODULI:
                if m not in got_any:
                    negatives.append(("%s-mod%d" % (seq_id, m),
                                      "no const/periodic/order-2 residue "
                                      "pattern mod %d on n<=22" % m,
                                      "BARREN(no fit-region pattern)"))
        dir_stats[(s, t)] = (tested, lost)

    # ---- rowsum sequence ----
    for cand in rowsum_candidates(tri):
        run(cand)

    # ---- stencils ----
    sc, stencils_tried = stencil_candidates(tri)
    for cand in sc:
        run(cand)

    wall = time.time() - t0
    write_report(survivors, negatives, skipped, dir_stats, n_seq,
                 stencils_tried, len(sc), wall)
    print("sweep done in %.1fs: %d sequences, %d stencil shapes, "
          "%d survivors, %d negatives -> sweep_report.md"
          % (wall, n_seq, stencils_tried, len(survivors), len(negatives)))
    return 0


def write_report(survivors, negatives, skipped, dir_stats, n_seq,
                 stencils_tried, stencil_cands, wall):
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "sweep_report.md")
    survivors.sort(key=lambda r: (-(r["bits_row40"] or 0),
                                  -r["holdout_matched"]))
    with open(path, "w") as f:
        f.write("# Mechanical sweep report -- T(n,H) triangle\n\n")
        f.write("Generated by `experiments/tristruct/sweep.py` in %.1fs. "
                "Search space: see the sweep.py docstring (the authoritative "
                "statement of what was and was NOT covered).\n\n" % wall)
        f.write("Sequences tested: %d slices + a(n). Stencil shapes tried: %d "
                "(yielding %d fit-region identities).\n\n"
                % (n_seq, stencils_tried, stencil_cands))
        f.write("## Survivors (fit n<=22, exact on all rows 23..39)\n\n")
        if not survivors:
            f.write("NONE.\n\n")
        for r in survivors:
            f.write("- **%s** (%s): %s\n  holdout %d/%d cells, row40 %s, "
                    "params %d, bits_row40 %s\n  provenance: holdout %s, "
                    "row40 %s\n  flags: %s\n"
                    % (r["id"], r["kind"], r["statement"],
                       r["holdout_matched"], r["holdout_cells"],
                       r["row40"]["result"], r["n_params"],
                       ("%.2f" % r["bits_row40"]) if r["bits_row40"] is not None
                       else "unquantified",
                       r["holdout_real_sweep"], r["row40_real_sweep"],
                       r["flags"] or "none"))
        f.write("\n## Direction coverage\n\n")
        f.write("| (s,t) | slices tested | skipped (support) |\n|---|---|---|\n")
        for st, (tested, lost) in sorted(dir_stats.items()):
            f.write("| %s | %d | %d |\n" % (st, tested, lost))
        f.write("\n## Full negative record\n\n")
        f.write("Every tested hypothesis that did not survive. BARREN = no "
                "hypothesis of the class even fits the n<=22 region; "
                "FAILS(n) = fitted but broke at holdout row n; CULLED = "
                "rejected by a verifier guard (reason given).\n\n")
        for sid, stmt, verdict in negatives:
            f.write("- %s: %s -- %s\n" % (sid, verdict, stmt))
        f.write("\n## Slices skipped for support (not probed at all)\n\n")
        for st, c, why in skipped:
            f.write("- (s,t)=%s c=%d: %s\n" % (st, c, why))


if __name__ == "__main__":
    sys.exit(main())
