"""Shared helpers for gate scripts: repo paths and fixture parsing."""

import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


def read_bfile(name):
    """Parse an OEIS b-file from fixtures/ into {n: a(n)}."""
    terms = {}
    with open(os.path.join(ROOT, "fixtures", name)) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                n, a = line.split()
                terms[int(n)] = int(a)
    return terms
