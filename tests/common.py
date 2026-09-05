"""Shared helpers for gate scripts: repo paths, fixtures, engine I/O, scoring."""

import concurrent.futures
import os
import subprocess
import time

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


# TODO(2026-09-05, /simplify): gate_g2, gate_holes, gate_modp and gate_tma each
# grew their own guard against an engine that prints nothing or dies after
# printing (AUDIT-2026-09-02, gate hygiene).  The shared fix is for run() to
# refuse empty stdout and parse_counts() an empty table, with gate_holes moved
# onto run().  Deferred: it changes every gate's contract in one edit.
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


# Background engine runs. A gate is a chain of independent engine invocations
# scored in printed order, and the long ones dominate: gate_tma's three full
# square8 n<=14 sweeps are 365 s of its 429 s (measured 2026-08-06, gympie).
# spawn() starts such a run immediately and returns a handle whose .result() is
# the same stdout string run() would have returned -- so the CHECK order, the
# arguments, and the assertions are untouched; only the waiting overlaps. The
# threads do nothing but wait on subprocesses, so the GIL is irrelevant here.
#
# ONLY for runs with no ordering dependency on each other. A gate step that
# reads state an earlier step wrote (gate_tma's J/L checkpoint write->resume
# chains) must keep calling run() straight-line.
_POOL = None
_POOL_MAX = 8  # engine processes in flight; each of gate_tma's sweeps peaks ~170 MB


def spawn(binary, *args):
    """Start an engine run now; returns a future whose .result() is its stdout."""
    global _POOL
    if _POOL is None:
        _POOL = concurrent.futures.ThreadPoolExecutor(max_workers=_POOL_MAX)
    return _POOL.submit(run, binary, *args)


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


# A gate that could not run part of itself is DEGRADED, and until 2026-08-22 a
# degraded gate was indistinguishable from a green one.  `results/gate-class-sweep.md`
# finding F3: tests/gate_middle_kingdom.py has three `skip` paths -- no GMP
# build, no build/prec_guess, no mpmath -- and two of them skip RED CONTROLS,
# so on a box missing any of the three the gate printed GREEN having never
# established that its own checks can fail.  `make gates` then reported a full
# green suite.
#
# The rule now: a skipped check is a FAILURE by default, and waiving it is an
# explicit act.  Set POLY_ALLOW_DEGRADED_GATES=1 to downgrade skips to a loud
# warning -- for the deliberate case of a box that genuinely lacks an optional
# dependency and where somebody has decided that is acceptable for that run.
# The waiver is per-run and leaves a line in the log naming every skip it
# forgave, so "the suite was green" and "the suite was green with four checks
# waived on a box without GMP" are never the same sentence.
ALLOW_DEGRADED = os.environ.get("POLY_ALLOW_DEGRADED_GATES") == "1"


class Gate:
    """Accumulates pass/fail results and prints a GREEN/RED verdict.

    Each check line carries the seconds since the previous one -- which is the
    work that produced it, since a gate is a straight-line chain of engine runs
    scored in printed order. `make gates` reports per-GATE time; this is the
    next level down, and it is what a gate needs to be shrunk on evidence rather
    than by guessing which check is the expensive one. Costs one clock read.
    """

    def __init__(self):
        self.failures = 0
        self.skips = []
        self._t = time.monotonic()

    def check(self, ok, label):
        now = time.monotonic()
        dt, self._t = now - self._t, now
        print(("ok   " if ok else "FAIL ") + f"[{dt:6.2f}s] " + label)
        if not ok:
            self.failures += 1

    def skip(self, label):
        """Record a check that could not run.  Fails the gate unless waived.

        Use this instead of `print("skip ...")` for anything that would
        otherwise have been checked -- especially a RED control, whose absence
        means nothing in this run established that the gate can fail."""
        print(("SKIP " if not ALLOW_DEGRADED else "skip ") + label)
        self.skips.append(label)

    def verdict(self, name):
        if self.skips:
            word = "waived" if ALLOW_DEGRADED else "NOT RUN"
            print(f"  {len(self.skips)} check(s) {word}:")
            for s in self.skips:
                print(f"    - {s}")
            if not ALLOW_DEGRADED:
                print("  A skipped check is a failure: nothing in this run "
                      "established what it would have established.")
                print("  Install the missing dependency, or re-run with "
                      "POLY_ALLOW_DEGRADED_GATES=1 to waive deliberately.")
        degraded = bool(self.skips) and not ALLOW_DEGRADED
        if self.failures == 0 and not degraded:
            state = "GREEN" + (f" ({len(self.skips)} waived)" if self.skips else "")
        elif self.failures:
            state = f"RED ({self.failures} failures"
            state += f", {len(self.skips)} not run)" if self.skips else ")"
        else:
            state = f"RED ({len(self.skips)} check(s) not run)"
        print(f"GATE {name}: {state}")
        return 1 if (self.failures or degraded) else 0
