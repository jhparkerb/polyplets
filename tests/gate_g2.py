#!/usr/bin/env python3
"""Gate G2: the C++ Redelmeier engine vs oracle and fixtures.

Four checks, per implementation-plan.md:
  A. aggregate counts equal pinned b-files (deeper than G1 can reach)
  B. per-bounding-box histograms equal the G1 oracle exactly
  C. split-mode invariance: the K split workers' outputs sum to the full run
  D. the ASan/UBSan build runs clean and agrees with the optimized build

Written before the engine exists (TDD); expects binaries at build/g2 and
build/g2_asan with the CLI:
    g2 LATTICE MAXN [--per-box] [--split S K IDX]
emitting "n count" lines (or "n w h count" with --per-box).
"""

import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "oracle"))

from g1_naive import count_by_box  # noqa: E402

G2 = os.path.join(ROOT, "build", "g2")
G2_ASAN = os.path.join(ROOT, "build", "g2_asan")

# check A: lattice -> (b-file, depth) -- a few seconds each, optimized build
FIXTURE_CASES = {
    "square4": ("b001168.txt", 14),
    "square8": ("b006770.txt", 11),
    "tri6":    ("b001207.txt", 12),
}
# check B: per-box equality vs G1 (G1 runtime bounds the depth)
PERBOX_CASES = {"square4": 9, "square8": 7, "tri6": 7}
# check C: split invariance
SPLIT_CASE = ("square8", 9, 4, 3)  # lattice, maxn, split size S, K workers
# check D: sanitizer build depths
ASAN_CASES = {"square4": 11, "square8": 8, "tri6": 9}

failures = 0


def check(ok, label):
    global failures
    print(("ok   " if ok else "FAIL ") + label)
    if not ok:
        failures += 1


def run(binary, *args):
    r = subprocess.run([binary] + [str(a) for a in args],
                       capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"{binary} {args}: rc={r.returncode}\n{r.stderr}")
    return r.stdout


def parse_counts(out):
    d = {}
    for line in out.strip().splitlines():
        parts = line.split()
        d[tuple(map(int, parts[:-1]))] = int(parts[-1])
    return d  # keys: (n,) or (n, w, h)


def read_bfile(name):
    terms = {}
    with open(os.path.join(ROOT, "fixtures", name)) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                n, a = line.split()
                terms[int(n)] = int(a)
    return terms


def main():
    for b in (G2, G2_ASAN):
        if not os.path.exists(b):
            print(f"FAIL missing binary {b} (run: make build/g2 build/g2_asan)")
            return 1

    # A. fixtures
    for lattice, (bfile, depth) in FIXTURE_CASES.items():
        expected = read_bfile(bfile)
        got = parse_counts(run(G2, lattice, depth))
        bad = [n for n in range(1, depth + 1)
               if n in expected and got.get((n,)) != expected[n]]
        check(not bad, f"A fixtures  {lattice:8s} n<={depth}  vs {bfile}"
              + (f"  MISMATCH at n={bad}" if bad else ""))

    # B. per-box vs oracle
    for lattice, depth in PERBOX_CASES.items():
        oracle = count_by_box(lattice, depth)
        engine = {k: v for k, v in
                  parse_counts(run(G2, lattice, depth, "--per-box")).items()}
        check(engine == oracle,
              f"B per-box   {lattice:8s} n<={depth}  vs G1 oracle "
              f"({len(oracle)} box classes)")

    # C. split invariance
    lattice, maxn, S, K = SPLIT_CASE
    full = parse_counts(run(G2, lattice, maxn))
    summed = {}
    for idx in range(K):
        part = parse_counts(run(G2, lattice, maxn, "--split", S, K, idx))
        for k, v in part.items():
            summed[k] = summed.get(k, 0) + v
    check(summed == full,
          f"C split     {lattice} n<={maxn} S={S} K={K}: workers sum to full run")

    # D. sanitizer build agrees and runs clean
    for lattice, depth in ASAN_CASES.items():
        opt = parse_counts(run(G2, lattice, depth))
        san = parse_counts(run(G2_ASAN, lattice, depth))
        check(opt == san, f"D asan      {lattice:8s} n<={depth}  clean + equal")

    print("GATE G2:", "GREEN" if failures == 0 else f"RED ({failures} failures)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
