"""Shared helpers for gate scripts: repo paths, fixtures, engine I/O, scoring."""

import os
import subprocess

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


def run(binary, *args):
    """Run an engine binary, returning its stdout; raise on nonzero exit."""
    r = subprocess.run([binary] + [str(a) for a in args],
                       capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"{binary} {args}: rc={r.returncode}\n{r.stderr}")
    return r.stdout


def parse_counts(out):
    """Parse engine output lines into a dict; keys are the leading ints,
    value the trailing one: '"n c"' -> {(n,): c}; '"h n c"' -> {(h,n): c}."""
    d = {}
    for line in out.strip().splitlines():
        parts = line.split()
        d[tuple(map(int, parts[:-1]))] = int(parts[-1])
    return d


class Gate:
    """Accumulates pass/fail results and prints a GREEN/RED verdict."""

    def __init__(self):
        self.failures = 0

    def check(self, ok, label):
        print(("ok   " if ok else "FAIL ") + label)
        if not ok:
            self.failures += 1

    def verdict(self, name):
        print(f"GATE {name}:",
              "GREEN" if self.failures == 0 else f"RED ({self.failures} failures)")
        return 1 if self.failures else 0
