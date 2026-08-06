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


def read_terms_file(path):
    """Parse a banked series file into a list of a(n), in file order.

    The format every results/*_terms_*.txt uses: one 'n a(n)' pair per line,
    blank lines and '#' comments skipped, the value being the trailing field."""
    vals = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                vals.append(int(line.split()[-1]))
    return vals


def run(binary, *args):
    """Run an engine binary, returning its stdout; raise on nonzero exit.

    Prefer this to subprocess.run(..., check=True): CalledProcessError reports
    the exit code but not stderr, so a gate whose engine refuses an argument or
    dies prints a number and nothing about why."""
    r = subprocess.run([binary] + [str(a) for a in args],
                       capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"{binary} {args}: rc={r.returncode}\n{r.stderr}")
    return r.stdout


def require_binary(path, make_target):
    """True if the engine is built; otherwise print how to build it."""
    if os.path.exists(path):
        return True
    print(f"FAIL missing {path} (run: make {make_target})")
    return False


# build/prec_guess signals its verdict through the exit code as well as stdout:
# 0 EXCLUDED, 2 INCONCLUSIVE (underdetermined), 3 CANDIDATE. Anything else is a
# real failure -- a missing terms file, a refused argument -- and must not be
# read as a verdict. Owning the contract here keeps three gates from each
# deciding for themselves which codes are survivable; check=True in particular
# turned a *falsified* claim (rc=3) into a traceback instead of a RED line.
PREC_GUESS_RC = {0: "EXCLUDED", 2: "INCONCLUSIVE", 3: "CANDIDATE"}


def prec_guess(binary, mode, terms, a, b, *extra):
    """Run build/prec_guess; return (verdict, nullity, holdout_pass, holdout_rows).

    nullity/holdout are None for an INCONCLUSIVE run, which prints neither."""
    r = subprocess.run([binary, mode, terms, str(a), str(b)]
                       + [str(x) for x in extra],
                       capture_output=True, text=True)
    if r.returncode not in PREC_GUESS_RC:
        raise RuntimeError(f"prec_guess {mode} {a},{b}: rc={r.returncode}\n"
                           f"{r.stderr}{r.stdout}")
    verdict, nullity, hold_pass, hold_rows = None, None, None, None
    for line in r.stdout.splitlines():
        if line.startswith("VERDICT:"):
            verdict = line.split()[1]
        elif line.startswith("full rank="):
            nullity = int(line.rsplit("=", 1)[1])
        elif line.startswith("holdout rows="):
            parts = line.split()
            hold_rows = int(parts[1].split("=")[1])
            hold_pass = int(parts[2].split("=")[1])
    if verdict != PREC_GUESS_RC[r.returncode]:
        raise RuntimeError(f"prec_guess {mode} {a},{b}: rc={r.returncode} says "
                           f"{PREC_GUESS_RC[r.returncode]}, stdout says {verdict}")
    return verdict, nullity, hold_pass, hold_rows


def parse_counts(out):
    """Parse engine output lines into a dict; keys are the leading ints,
    value the trailing one: '"n c"' -> {(n,): c}; '"h n c"' -> {(h,n): c}."""
    d = {}
    for line in out.strip().splitlines():
        parts = line.split()
        d[tuple(map(int, parts[:-1]))] = int(parts[-1])
    return d


def free_and_one_sided(fixed, r90, r180, hmirror, dmirror):
    """Burnside's lemma on the square lattice (D4): free and one-sided polyomino/
    polyplet counts from the fixed count plus the four symmetric counts (each
    one orientation; the 2x coefficients cover the conjugate orientations).
    Returns (free, one_sided); raises ValueError if a total is not integral,
    which signals a wrong fixed or symmetric input."""
    free_num = fixed + 2 * r90 + r180 + 2 * hmirror + 2 * dmirror
    one_num = fixed + 2 * r90 + r180
    if free_num % 8 or one_num % 4:
        raise ValueError(f"Burnside not integral (free8={free_num}, one4={one_num})")
    return free_num // 8, one_num // 4


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
