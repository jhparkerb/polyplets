"""candidates/example.py -- worked example of a proposer candidate file.

This is a TEMPLATE, not a claim: it wraps one relation the mechanical sweep
already found (T(n,3) odd iff n = 3,0 mod 4) purely to show the schema in
action. Copy this file, replace the relation, fill the independence fields
honestly, then run:

    python3 verify.py candidates/<yourfile>.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from schema import Candidate  # noqa: E402


def _fit(view):
    """Fit the 4 period residues on the fit region (n <= 22 only -- the view
    physically cannot serve higher rows). The verifier re-runs this itself;
    parameters are never baked in."""
    res = {n % 4: view.cell(n, 3) % 2 for n in range(3, view.max_n + 1)}
    # refuse to fit if the fit region is not actually periodic
    for n in range(3, view.max_n + 1):
        if view.cell(n, 3) % 2 != res[n % 4]:
            raise ValueError("not period-4 on the fit region")
    return res


CANDIDATES = [
    Candidate(
        id="example-col3-parity",
        proposer="example",
        statement="T(n,3) is odd iff n == 3 or 0 (mod 4), for n >= 3",
        tier="C",
        kind="congruence", modulus=2,
        region=lambda n, H: H == 3 and n >= 3,
        n_params=4,                    # the four period residues
        fit=_fit,
        predict=lambda p, n, H, ctx: p[n % 4],
        # the four independence fields, answered honestly:
        input_footprint="column H=3 cells, n <= 22, largest n = 22",
        derivation_independence="none -- pattern read off banked data "
                                "(this is a template, not a derivation)",
        rule_independence="none -- same enumeration lineage",
    ),
]
