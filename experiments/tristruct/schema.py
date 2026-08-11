"""schema.py -- the candidate schema every proposer emits, plus the fit-region
sandbox the verifier uses to refit candidates.

A candidate is a Candidate object (see fields below) collected in a module-level
list named CANDIDATES inside a Python file the proposer writes (convention:
experiments/tristruct/candidates/<proposer>_<topic>.py). verify.py loads such
files, REFITS every candidate itself on the declared fit region, and scores the
predictions on held-out rows. See README.md for a worked example.

Design rule: parameters are NEVER baked in. A candidate supplies a `fit`
callable; the verifier calls it with a FitView that exposes ONLY cells with
n <= fit_max_n (default 22, hard ceiling 39). Any attempt to read a higher row
during fitting raises FitRegionViolation and the candidate is culled. A
parameter-free relation sets fit=None and n_params=0.

Candidate kinds (ctx is a PredictContext, see below):
  "value"       predict(params, n, H, ctx) -> exact int, claimed == T(n,H).
                For scope "rowsum", predict(params, n, None, ctx) -> a(n).
  "congruence"  modulus m required; predict(params, n, H, ctx) -> residue in
                0..m-1, claimed == T(n,H) % m (a(n) % m for scope "rowsum").
  "boolean"     check(params, n, H, value, ctx) -> bool on the banked value.
                Must carry bits_claimed AND bits_justification, or the verifier
                refuses to credit any bits (see verify.py).

PredictContext: predictions are allowed to CONSUME banked cells -- the mission
is exactly "turn banked numbers into a prediction" -- but under a peek guard:
  value/congruence: only cells/rowsums with n' < n (strictly smaller row);
  boolean: additionally cells with n' == n, H' != H (stencil equations may tie
           several same-row cells together);
  the target cell itself is NEVER readable. Violations raise PeekViolation and
  the verifier culls the candidate. What a prediction consumes is precisely
  its input footprint -- declare it in the independence fields.

Region: region(n, H) -> bool says which grid cells the relation claims to
cover (for scope "rowsum": region(n, None)). The verifier partitions the
region BY n: fit rows n <= fit_max_n, holdout rows fit_max_n < n <= 39,
and row 40 scored separately and never fitted.

Independence fields (all four required, free text, per the team brief):
  input_footprint          banked cells the DERIVATION consumed, largest n
  derivation_independence  did the derivation touch banked data, or only the
                           definition and self-enumerated cells?
  rule_independence        does it decide king-connectivity the way the
                           engines do (shared code/rule), or independently?
  bits_claimed/_justification  proposer's a-priori pass-probability claim;
                           the verifier recomputes where it can and flags
                           inflation.
"""

NMAX = 40
DEFAULT_FIT_MAX_N = 22
HOLDOUT_MAX_N = 39  # row 40 is scored separately, never fitted, never "holdout"

TIERS = ("A", "B", "C", "D", "softer")
KINDS = ("value", "congruence", "boolean")
SCOPES = ("cell", "rowsum")


class FitRegionViolation(Exception):
    """A candidate's fit() tried to read data above its declared fit region."""


class PeekViolation(Exception):
    """A candidate's predict/check tried to read a cell it must not see."""


class PredictContext:
    """Banked-data access during prediction of cell (n, H), peek-guarded.

    value/congruence kinds may read rows n' < n only; boolean kind may also
    read same-row cells H' != H. The target cell is never readable.
    """

    def __init__(self, tri, n, H, kind):
        self._tri = tri
        self._n = n
        self._H = H
        self._kind = kind

    def _guard(self, n2, H2):
        if n2 < self._n:
            return
        if (self._kind == "boolean" and n2 == self._n and H2 is not None
                and H2 != self._H):
            return
        raise PeekViolation(
            "predict of (n=%d,H=%s) read (n=%d,H=%s)"
            % (self._n, self._H, n2, H2))

    def cell(self, n2, H2):
        self._guard(n2, H2)
        return self._tri.cell(n2, H2)

    def rowsum(self, n2):
        # a(n2) contains every cell of row n2, so only strictly smaller rows
        if n2 >= self._n:
            raise PeekViolation(
                "predict of (n=%d,H=%s) read rowsum(%d)"
                % (self._n, self._H, n2))
        return self._tri.rowsum(n2)


class SchemaError(Exception):
    """A candidate violates the schema contract."""


class FitView:
    """Read-only view of a Triangle exposing ONLY rows n <= max_n.

    This is the fail-closed fit sandbox: fit() receives this instead of the
    triangle, so it cannot consume holdout rows even by accident. Row 40 is
    never exposed regardless of max_n.
    """

    def __init__(self, tri, max_n):
        if max_n > HOLDOUT_MAX_N:
            raise FitRegionViolation("fit_max_n=%d > %d" % (max_n, HOLDOUT_MAX_N))
        self._tri = tri
        self.max_n = max_n

    def _guard(self, n):
        if n > self.max_n:
            raise FitRegionViolation(
                "fit read row n=%d above fit_max_n=%d" % (n, self.max_n))

    def cell(self, n, H):
        self._guard(n)
        return self._tri.cell(n, H)

    def rowsum(self, n):
        self._guard(n)
        return self._tri.rowsum(n)

    def row(self, n):
        self._guard(n)
        return self._tri.row(n)

    def col(self, H):
        return {n: v for n, v in self._tri.col(H).items() if n <= self.max_n}

    def diag(self, k):
        return {n: v for n, v in self._tri.diag(k).items() if n <= self.max_n}

    def slice(self, s, t, c):
        return [((n, H), v) for (n, H), v in self._tri.slice(s, t, c)
                if n <= self.max_n]

    def provenance(self, n, H):
        self._guard(n)
        return self._tri.provenance(n, H)


class Candidate:
    REQUIRED = ("id", "proposer", "statement", "tier", "kind", "scope",
                "region", "n_params", "predict_or_check",
                "input_footprint", "derivation_independence",
                "rule_independence")

    def __init__(self, id, proposer, statement, tier, kind,
                 region, n_params,
                 fit=None, predict=None, check=None, modulus=None,
                 scope="cell", fit_max_n=DEFAULT_FIT_MAX_N,
                 fit_region_reason=None,
                 bits_claimed=None, bits_justification=None,
                 input_footprint=None, derivation_independence=None,
                 rule_independence=None):
        self.id = id
        self.proposer = proposer
        self.statement = statement
        self.tier = tier
        self.kind = kind
        self.scope = scope
        self.region = region
        self.n_params = n_params
        self.fit = fit
        self.predict = predict
        self.check = check
        self.modulus = modulus
        self.fit_max_n = fit_max_n
        self.fit_region_reason = fit_region_reason
        self.bits_claimed = bits_claimed
        self.bits_justification = bits_justification
        self.input_footprint = input_footprint
        self.derivation_independence = derivation_independence
        self.rule_independence = rule_independence
        self._validate()

    def _validate(self):
        if not self.id or not self.proposer or not self.statement:
            raise SchemaError("id, proposer, statement are required")
        if self.tier not in TIERS:
            raise SchemaError("%s: tier must be one of %s" % (self.id, (TIERS,)))
        if self.kind not in KINDS:
            raise SchemaError("%s: kind must be one of %s" % (self.id, (KINDS,)))
        if self.scope not in SCOPES:
            raise SchemaError("%s: scope must be one of %s" % (self.id, (SCOPES,)))
        if not callable(self.region):
            raise SchemaError("%s: region must be callable(n, H) -> bool" % self.id)
        if not isinstance(self.n_params, int) or self.n_params < 0:
            raise SchemaError("%s: n_params must be a nonnegative int" % self.id)
        if self.n_params > 0 and not callable(self.fit):
            raise SchemaError(
                "%s: n_params=%d but no fit callable -- baked-in parameters "
                "are not falsifiable; supply fit(FitView) -> params"
                % (self.id, self.n_params))
        if self.kind in ("value", "congruence") and not callable(self.predict):
            raise SchemaError("%s: kind=%s needs predict" % (self.id, self.kind))
        if self.kind == "congruence":
            if not isinstance(self.modulus, int) or self.modulus < 2:
                raise SchemaError("%s: congruence needs integer modulus >= 2" % self.id)
        if self.kind == "boolean" and not callable(self.check):
            raise SchemaError("%s: kind=boolean needs check" % self.id)
        if not (1 <= self.fit_max_n <= HOLDOUT_MAX_N):
            raise SchemaError("%s: fit_max_n must be in 1..%d (row 40 is never "
                              "fittable)" % (self.id, HOLDOUT_MAX_N))
        if self.fit_max_n > DEFAULT_FIT_MAX_N and not self.fit_region_reason:
            raise SchemaError(
                "%s: fit_max_n=%d > default %d requires fit_region_reason "
                "naming the hypothesis class that forced it"
                % (self.id, self.fit_max_n, DEFAULT_FIT_MAX_N))
        for f in ("input_footprint", "derivation_independence", "rule_independence"):
            if not getattr(self, f):
                raise SchemaError("%s: independence field %r is required" % (self.id, f))

    def region_cells(self):
        """All grid points the region claims, as (n, H) pairs (H None for rowsum)."""
        if self.scope == "rowsum":
            return [(n, None) for n in range(1, NMAX + 1) if self.region(n, None)]
        return [(n, H) for n in range(1, NMAX + 1) for H in range(1, NMAX + 1)
                if self.region(n, H)]


def load_candidates(path):
    """Load CANDIDATES from a proposer's .py file, returning the list."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "cand_" + path.replace("/", "_").replace(".", "_"), path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    if not hasattr(mod, "CANDIDATES"):
        raise SchemaError("%s defines no CANDIDATES list" % path)
    for c in mod.CANDIDATES:
        if not isinstance(c, Candidate):
            raise SchemaError("%s: CANDIDATES entries must be schema.Candidate" % path)
    return list(mod.CANDIDATES)
