"""Proposer 1 (proof-first): deficit-d family congruences mod 3, d = 3..6.

The proved landscape: the deficit-1 family T(3k,2k) == 1 (mod 3) (spine T3)
and deficit-2 family T(3m+2,2m+1) == 2 (mod 3) (deficit2_proof.py) are
CONSTANT along their (n,k)-linear lines n = 3k+1-d. The d >= 3 families are
the named open remainder of the Witt tower (`results/ternary-spine.md`,
sleeve units). The mechanical sweep could NOT test these lines: direction
(2,-3) has zero slices with both fit and holdout support under its >= 10-fit
rule (sweep_report geometry finding); each family has only 4-6 fit points.
This candidate file puts the natural first hypothesis class (eventually
constant, or exact period 2..4 in k -- the class the proved d = 1, 2 cases
belong to) through the verifier on those unswept lines. Honest framing: own
data already shows d = 3 is NOT constant (T(10,6) == 0, T(13,8) == 1,
T(19,12) == 0 mod 3), so the constant branch is expected to fail there;
either verdict is a recorded result on a line nothing else has probed.
Row-40 stakes: d = 3 and d = 6 lines end at the open sleeve cells (40,26)
and (40,25).
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from schema import Candidate


def _family_cells(d, lo_n=1, hi_n=40):
    out = []
    for k in range(d, 40):
        n = 3 * k + 1 - d
        H = n - k
        if lo_n <= n <= hi_n and 1 <= H <= n:
            out.append((n, H))
    return out


def _fit_factory(d):
    def fit(view):
        res = []
        for (n, H) in _family_cells(d, hi_n=view.max_n):
            res.append(view.cell(n, H) % 3)
        if len(res) >= 4 and len(set(res[-3:])) == 1:
            return ("const", res[-1])
        for p in (2, 3, 4):
            if len(res) >= 2 * p and all(
                    res[i] == res[i % p] for i in range(len(res))) \
                    and len(set(res[:p])) > 1:
                return ("periodic", p, res[:p], d)
        raise ValueError(
            "deficit-%d family: no constant tail and no exact period <= 4 "
            "on the %d fit residues" % (d, len(res)))
    return fit


def _predict_factory(d):
    cells = _family_cells(d)
    idx = {c: i for i, c in enumerate(cells)}
    def predict(params, n, H, ctx):
        if params[0] == "const":
            return params[1]
        _, p, pat, _ = params
        return pat[idx[(n, H)] % p]
    return predict


def _mk(d):
    cells = set(_family_cells(d))
    return Candidate(
        id="p1-deficit%d-family-mod3" % d,
        proposer="p1-proof-first",
        statement=("deficit-%d family T(3k+1-%d, 2k+1-%d) mod 3 follows a "
                   "constant/short-period pattern in k (class of the proved "
                   "d=1,2 families)" % (d, d, d)),
        tier="C", kind="congruence", modulus=3, scope="cell",
        region=lambda n, H, _c=cells: (n, H) in _c,
        n_params=4,
        fit=_fit_factory(d), predict=_predict_factory(d),
        input_footprint=("family cells n <= 22 only (4-6 cells, largest "
                         "n = 22); prediction consumes no banked cells"),
        derivation_independence=("hypothesis class = the proved d=1,2 "
                                 "analogues; own-enumerated family values "
                                 "n <= 13 examined first"),
        rule_independence=("no connectivity decision in the relation; own "
                           "enumerator used for the small cells"),
    )


CANDIDATES = [_mk(d) for d in (3, 4, 5, 6)]
