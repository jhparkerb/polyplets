"""test_verify.py -- RED-first tests for the tristruct harness.

The verifier is a checker, and checkers are held to a HIGHER standard than the
content they protect. Every guarantee verify.py makes has a test here that
PLANTS a bad candidate and asserts the verifier CATCHES it:

  * a candidate whose fit() reads holdout rows  -> FIT-REGION-VIOLATION, culled
  * a lookup-table candidate that matches n<=22 and fails at n=23
                                              -> first_fail_row == 23, FAILS
  * a candidate with as many free parameters as holdout cells matched
                                              -> FITTED-NOT-TESTED, culled
  * the diagonal law in disguise               -> KNOWN-COINCIDENT, culled
  * a mod-8 congruence claiming 64 bits        -> BITS-INFLATED, bits = 3/cell
  * a boolean check claiming bits with no justification -> NO-BITS-JUSTIFIED
  * a candidate with no holdout cells at all   -> NO-HOLDOUT, culled
  * row 40 never fittable (FitView refuses)    -> FitRegionViolation
  * loader refuses corrupt row sums / anchors  -> TriangleDataError

Plus one green sanity: a true, parameter-free, not-prior-work relation
(T(n,1) == 1) SURVIVES.

Run:  python3 experiments/tristruct/test_verify.py
"""

import math
import unittest

from triangle import Triangle, TriangleDataError
from schema import Candidate, FitView, FitRegionViolation, PeekViolation, PredictContext
import verify

TRI = Triangle.load()

def has_flag(r, prefix):
    return any(f.startswith(prefix) for f in r["flags"])


INDEP = dict(input_footprint="test plant",
             derivation_independence="test plant",
             rule_independence="test plant")


class TestLoaderRefusals(unittest.TestCase):
    def _copy(self):
        cells = {nh: v for nh, v in TRI.cells()}
        rowsums = {n: TRI.rowsum(n) for n in range(1, 41)}
        return cells, rowsums

    def test_row_sum_corruption_refused(self):
        cells, rowsums = self._copy()
        cells[(37, 12)] += 1
        with self.assertRaises(TriangleDataError):
            Triangle.from_data(cells, rowsums)

    def test_anchor_corruption_refused(self):
        cells, rowsums = self._copy()
        delta = 3 ** 36
        cells[(40, 39)] += delta   # break the T(40,39)=955*3^36 anchor
        rowsums[40] += delta       # keep the row sum consistent
        with self.assertRaises(TriangleDataError):
            Triangle.from_data(cells, rowsums)

    def test_structural_zero_refused(self):
        cells, rowsums = self._copy()
        cells[(5, 9)] = 7          # H > n must be zero
        rowsums[5] += 7
        with self.assertRaises(TriangleDataError):
            Triangle.from_data(cells, rowsums)


class TestFitRegionSandbox(unittest.TestCase):
    def test_row_40_never_fittable(self):
        with self.assertRaises(FitRegionViolation):
            FitView(TRI, 40)
        v = FitView(TRI, 39)
        with self.assertRaises(FitRegionViolation):
            v.cell(40, 20)

    def test_fit_reading_holdout_is_caught(self):
        # fit() peeks at row 30 -- must be culled with FIT-REGION-VIOLATION
        cand = Candidate(
            id="plant-peek", proposer="test", statement="peeks at row 30",
            tier="A", kind="value", region=lambda n, H: H == 1,
            n_params=1,
            fit=lambda view: [view.cell(30, 15)],
            predict=lambda p, n, H, ctx: 1,
            **INDEP)
        r = verify.verify_candidate(cand, TRI)
        self.assertTrue(r["culled"], r)
        self.assertTrue(has_flag(r, "FIT-REGION-VIOLATION"), r)


class TestHoldoutIsReal(unittest.TestCase):
    def test_lookup_table_fails_at_23(self):
        # memorizes fit rows of column H=2, predicts 0 above -- the verifier
        # must report failure at n=23, not a 22/22 "pass"
        cand = Candidate(
            id="plant-lookup", proposer="test",
            statement="lookup table on column 2",
            tier="A", kind="value", region=lambda n, H: H == 2,
            n_params=1,
            fit=lambda view: {n: view.cell(n, 2) for n in range(1, 23)},
            predict=lambda p, n, H, ctx: p.get(n, 0),
            **INDEP)
        r = verify.verify_candidate(cand, TRI)
        self.assertEqual(r["first_fail_row"], 23, r)
        self.assertTrue(r["verdict"].startswith("FAILS"), r)

    def test_no_holdout_culled(self):
        cand = Candidate(
            id="plant-nohold", proposer="test",
            statement="region stops at n=22",
            tier="C", kind="value", region=lambda n, H: H == 1 and n <= 22,
            n_params=0, predict=lambda p, n, H, ctx: 1,
            **INDEP)
        r = verify.verify_candidate(cand, TRI)
        self.assertTrue(r["culled"], r)
        self.assertTrue(has_flag(r, "NO-HOLDOUT"), r)


class TestPeekGuard(unittest.TestCase):
    def test_echo_cheat_is_caught(self):
        # the ultimate cheat: "predict" T(n,H) by reading T(n,H) -- the
        # PredictContext must refuse and the candidate must be culled
        cand = Candidate(
            id="plant-echo", proposer="test",
            statement="echoes the target cell back",
            tier="A", kind="value", region=lambda n, H: H == 5,
            n_params=0,
            predict=lambda p, n, H, ctx: ctx.cell(n, H),
            **INDEP)
        r = verify.verify_candidate(cand, TRI)
        self.assertTrue(r["culled"], r)
        self.assertTrue(has_flag(r, "PEEK-VIOLATION"), r)

    def test_context_allows_smaller_rows(self):
        ctx = PredictContext(TRI, 30, 10, "value")
        self.assertEqual(ctx.cell(29, 10), TRI.cell(29, 10))
        with self.assertRaises(PeekViolation):
            ctx.cell(30, 9)   # same row, value kind: refused
        with self.assertRaises(PeekViolation):
            ctx.rowsum(30)    # contains the target cell


class TestParameterAccounting(unittest.TestCase):
    def test_fitted_not_tested_culled(self):
        # correct on all 17 holdout cells of column 1, but declares 20 free
        # parameters: as many knobs as cells matched -> not a test of anything
        cand = Candidate(
            id="plant-overpar", proposer="test",
            statement="T(n,1)=1 wearing 20 parameters",
            tier="A", kind="value", region=lambda n, H: H == 1,
            n_params=20,
            fit=lambda view: list(range(20)),
            predict=lambda p, n, H, ctx: 1,
            **INDEP)
        r = verify.verify_candidate(cand, TRI)
        self.assertTrue(r["culled"], r)
        self.assertTrue(has_flag(r, "FITTED-NOT-TESTED"), r)


class TestKnownCull(unittest.TestCase):
    def test_diagonal_law_in_disguise(self):
        # interpolates P_2 on the fit region and predicts diagonal k=2 --
        # exactly docs/proofs/diagonal-law.md; must be flagged KNOWN-COINCIDENT
        from fractions import Fraction

        def fit(view):
            xs = [5, 6, 7]
            ys = [Fraction(view.cell(n, n - 2), 3 ** (n - 7)) if n >= 7
                  else Fraction(view.cell(n, n - 2)) * 3 ** (7 - n) for n in xs]
            return (xs, ys)

        def predict(p, n, H, ctx):
            xs, ys = p
            acc = Fraction(0)
            for i in range(3):
                term = ys[i]
                for j in range(3):
                    if i != j:
                        term *= Fraction(n - xs[j], xs[i] - xs[j])
                acc += term
            v = acc * Fraction(3) ** (n - 7)
            return int(v)

        cand = Candidate(
            id="plant-diag-disguise", proposer="test",
            statement="quadratic times 3-power on k=2",
            tier="B", kind="value",
            region=lambda n, H: n - H == 2 and n >= 5,
            n_params=3, fit=fit, predict=predict,
            **INDEP)
        r = verify.verify_candidate(cand, TRI)
        self.assertTrue(any(f.startswith("KNOWN-COINCIDENT") for f in r["flags"]), r)
        self.assertTrue(r["culled"], r)


class TestLowStripCull(unittest.TestCase):
    def test_engine_lowstrip_restatement_is_culled(self):
        # T(n,1) == 1 restates the engine's own lowHeightRow closed form --
        # the very formula that GENERATED those cells; must be culled
        cand = Candidate(
            id="plant-lowstrip", proposer="test",
            statement="T(n,1) == 1 for all n >= 1",
            tier="B", kind="value", region=lambda n, H: H == 1,
            n_params=0, predict=lambda p, n, H, ctx: 1,
            **INDEP)
        r = verify.verify_candidate(cand, TRI)
        self.assertTrue(r["culled"], r)
        self.assertTrue(has_flag(r, "KNOWN-COINCIDENT"), r)
        # and the provenance annotation shows these cells are not real sweeps
        self.assertEqual(r["holdout_real_sweep"], "0/17 real-sweep")


class TestColumnCfiniteCull(unittest.TestCase):
    """The four sweep survivors of 2026-08-11 are restatements of the pinned
    column recurrences (results/diagonal-formula.md sections 1-2): columns
    H<=4 are C-finite (orders 1,3,7,15), and a C-finite integer sequence's
    residues mod m are forced by the recurrence + initial terms. The extended
    known.py must cull all four as KNOWN-COINCIDENT."""

    def _run_sweep_survivor(self, cand):
        r = verify.verify_candidate(cand, TRI)
        self.assertTrue(r["culled"], r)
        self.assertTrue(has_flag(r, "KNOWN-COINCIDENT"), r)

    def test_col3_order7_recurrence_culled(self):
        import sweep
        pos = sweep.slice_positions(0, 1, 3)
        vec = sweep.prec_fit_from_view(TRI.cell, pos, 0, 7)
        self.assertIsNotNone(vec)
        self._run_sweep_survivor(
            sweep.make_prec_candidate("S(0,1)c3", 0, 1, 3, pos, 0, 7, vec))

    def test_col3_mod2_per4_culled(self):
        self._run_sweep_survivor(Candidate(
            id="plant-col3-mod2", proposer="test",
            statement="T(n,3) mod 2 period 4",
            tier="C", kind="congruence", modulus=2,
            region=lambda n, H: H == 3 and n >= 3,
            n_params=0, predict=lambda p, n, H, ctx: 1 if n % 4 in (3, 0) else 0,
            **INDEP))

    def test_col3_mod4_per8_culled(self):
        residues = {n % 8: TRI.cell(n, 3) % 4 for n in range(3, 11)}
        self._run_sweep_survivor(Candidate(
            id="plant-col3-mod4", proposer="test",
            statement="T(n,3) mod 4 period 8",
            tier="C", kind="congruence", modulus=4,
            region=lambda n, H: H == 3 and n >= 3,
            n_params=0,
            predict=lambda p, n, H, ctx, _r=residues: _r[n % 8],
            **INDEP))

    def test_col4_mod2_per4_culled(self):
        residues = {n % 4: TRI.cell(n, 4) % 2 for n in range(4, 8)}
        self._run_sweep_survivor(Candidate(
            id="plant-col4-mod2", proposer="test",
            statement="T(n,4) mod 2 period 4",
            tier="C", kind="congruence", modulus=2,
            region=lambda n, H: H == 4 and n >= 4,
            n_params=0,
            predict=lambda p, n, H, ctx, _r=residues: _r[n % 4],
            **INDEP))


class TestBitsAccounting(unittest.TestCase):
    def test_congruence_bits_inflated(self):
        # true congruence claiming 64 bits; the verifier must override with
        # log2(2)=1 per cell and flag the inflation. (The relation itself is
        # a restatement of the pinned column-3 recurrence, so it is ALSO
        # culled KNOWN-COINCIDENT -- bits accounting is computed regardless.)
        cand = Candidate(
            id="plant-bits", proposer="test",
            statement="column 3 mod 2 period 4, inflated bits claim",
            tier="C", kind="congruence", modulus=2,
            region=lambda n, H: H == 3 and n >= 3,
            n_params=0, predict=lambda p, n, H, ctx: 1 if n % 4 in (3, 0) else 0,
            bits_claimed=64.0, bits_justification="trust me",
            **INDEP)
        r = verify.verify_candidate(cand, TRI)
        self.assertTrue(has_flag(r, "BITS-INFLATED"), r)
        self.assertAlmostEqual(r["bits_per_cell"], 1.0)
        self.assertAlmostEqual(r["bits_row40"], 1.0)

    def test_boolean_without_justification_gets_no_bits(self):
        cand = Candidate(
            id="plant-bool", proposer="test",
            statement="T(n,1) is a perfect square, bits from nowhere",
            tier="C", kind="boolean",
            region=lambda n, H: H == 1,
            n_params=0,
            check=lambda p, n, H, v, ctx: math.isqrt(v) ** 2 == v,
            bits_claimed=10.0,  # no justification supplied
            **INDEP)
        r = verify.verify_candidate(cand, TRI)
        self.assertTrue(has_flag(r, "NO-BITS-JUSTIFIED"), r)
        self.assertIsNone(r["bits_row40"])


class TestGreenSanity(unittest.TestCase):
    def test_tautological_boolean_culled(self):
        # the strip re-weighting identity T(n,7) = C_7 - 2*C_6 + C_5 is a
        # TAUTOLOGY: the target's coefficient cancels, so the check passes
        # for ANY value of T(n,7). A boolean with no sensitivity to its
        # target value has zero checking power -- the verifier must detect
        # this (perturb the value, see the check still pass) and cull it.
        def C(ctx, n, h, v):
            return sum((h - j + 1) * (v if j == 7 else ctx.cell(n, j))
                       for j in range(1, h + 1)) if h >= 1 else 0

        cand = Candidate(
            id="plant-tautology", proposer="test",
            statement="T(n,7) == C_7(n) - 2*C_6(n) + C_5(n) (tautology)",
            tier="C", kind="boolean",
            region=lambda n, H: H == 7 and n >= 7,
            n_params=0,
            check=lambda p, n, H, v, ctx:
                v == C(ctx, n, 7, v) - 2 * C(ctx, n, 6, v) + C(ctx, n, 5, v),
            **INDEP)
        r = verify.verify_candidate(cand, TRI)
        self.assertTrue(r["culled"], r)
        self.assertTrue(has_flag(r, "VALUE-INSENSITIVE"), r)

    def test_true_planted_relation_survives(self):
        # sanity that SURVIVES is reachable and value-sensitive: plant a
        # synthetic C-finite column 9 (u = 3u' + u'') into a copy of the
        # triangle, then verify the candidate that fits and predicts it.
        cells = {nh: v for nh, v in TRI.cells()}
        rowsums = {n: TRI.rowsum(n) for n in range(1, 41)}
        u = {9: 5, 10: 17}
        for n in range(11, 41):
            u[n] = 3 * u[n - 1] + u[n - 2]
        for n in range(9, 41):
            rowsums[n] += u[n] - cells[(n, 9)]
            cells[(n, 9)] = u[n]
        tri2 = Triangle.from_data(cells, rowsums)

        def fit(view):
            # solve u_n = a*u_{n-1} + b*u_{n-2} exactly on the fit region
            n = 13
            a1, b1, c1 = view.cell(n - 1, 9), view.cell(n - 2, 9), view.cell(n, 9)
            a2, b2, c2 = view.cell(n, 9), view.cell(n - 1, 9), view.cell(n + 1, 9)
            det = a1 * b2 - a2 * b1
            a = (c1 * b2 - c2 * b1) // det
            b = (a1 * c2 - a2 * c1) // det
            for m in range(11, view.max_n + 1):
                if view.cell(m, 9) != a * view.cell(m - 1, 9) + b * view.cell(m - 2, 9):
                    raise ValueError("recurrence does not fit")
            return (a, b)

        cand = Candidate(
            id="sane-planted-col9", proposer="test",
            statement="planted order-2 recurrence on synthetic column 9",
            tier="B", kind="value",
            region=lambda n, H: H == 9 and n >= 11,
            n_params=2, fit=fit,
            predict=lambda p, n, H, ctx:
                p[0] * ctx.cell(n - 1, 9) + p[1] * ctx.cell(n - 2, 9),
            **INDEP)
        r = verify.verify_candidate(cand, tri2)
        self.assertFalse(r["culled"], r)
        self.assertEqual(r["verdict"], "SURVIVES")
        self.assertIsNone(r["first_fail_row"])
        self.assertEqual(r["row40"]["result"], "ok")


if __name__ == "__main__":
    unittest.main(verbosity=2)
