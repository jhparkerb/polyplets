#!/usr/bin/env python3
"""Fail-closed gate for cpp/motley_par.cpp, the parallel Motley engine.

The engine is only worth having if it is the SAME engine.  Three things are
checked, and the first is the one that matters:

  1. RULE.  C_H(n) mod p must equal the banked exact rows
     results/cutcount_b1/rows/C<H>.out reduced mod p, at every n and every
     height run.  The banked rows are the frozen spec's own output; agreeing
     with them is agreeing with the rule, not with my transcription of it.
  2. IMPLEMENTATION.  The output must be byte-identical to
     `cutcount_b1 --modp` at the same (H, Nmax, p), when that binary is
     available.  This catches an accounting difference the rule check would
     absorb (it would not: the rows are the same numbers -- but a byte diff
     localises a format slip immediately).
  3. DETERMINISM.  Thread count must not change a digit.  Mod-p addition is
     associative and commutative, so any order must give the same row; if it
     does not, there is a race.

Usage:
  python3 tests/gate_motley_par.py [HMAX] [--bin PATH] [--ref PATH] [--rows DIR]
  python3 tests/gate_motley_par.py --selftest      # RED controls

Exit 0 = GATE GREEN.  Anything else is red, including a missing banked row:
a gate that silently checks nothing is worse than no gate.
"""

import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PRIMES = [2147483647, 65521, 251]        # exercises the u32, u16 and u8 payloads
NMAX = 40


def opt(name, default):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else default


def run_rows(binary, H, p, threads, extra=()):
    with tempfile.NamedTemporaryFile(suffix=".out", delete=False) as fh:
        path = fh.name
    cmd = [binary, "--modp", str(H), str(NMAX), str(p), path]
    if threads:
        cmd += ["--threads", str(threads)]
    cmd += list(extra)
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        os.unlink(path)
        raise AssertionError(f"{os.path.basename(binary)} H={H} p={p} "
                             f"exit {r.returncode}: {r.stderr.strip()[-300:]}")
    with open(path) as fh:
        body = fh.read()
    os.unlink(path)
    return body


def banked(rowdir, H):
    path = os.path.join(rowdir, f"C{H}.out")
    if not os.path.exists(path):
        raise AssertionError(f"no banked row {path} -- the rule check would be vacuous")
    out = {}
    for line in open(path):
        parts = line.split()
        if len(parts) == 2:
            out[int(parts[0])] = int(parts[1])
    if not out:
        raise AssertionError(f"{path} parsed to nothing")
    return out


def parse(body):
    return {int(a): int(b) for a, b in
            (line.split() for line in body.splitlines() if line.strip())}


def check_rule(rows, exact, H, p, corrupt=None):
    """Every C_H(n) mod p against the banked exact row.  `corrupt` is the RED
    control: an n whose banked value is shifted by 1 before comparing."""
    n_checked = 0
    for n, want in exact.items():
        if n > NMAX:
            continue
        w = (want + (1 if corrupt == n else 0)) % p
        got = rows.get(n)
        if got is None:
            raise AssertionError(f"H={H} p={p}: engine produced no n={n}")
        if got != w:
            raise AssertionError(f"H={H} p={p} n={n}: engine {got} != banked {w}")
        n_checked += 1
    if n_checked < 10:
        raise AssertionError(f"H={H}: only {n_checked} cells compared -- vacuous")
    return n_checked


def main():
    hmax = 15
    for a in sys.argv[1:]:
        if a.isdigit():
            hmax = int(a)
    binary = opt("--bin", os.path.join(ROOT, "build", "motley_par"))
    ref = opt("--ref", "")
    rowdir = opt("--rows", os.path.join(ROOT, "results", "cutcount_b1", "rows"))
    selftest = "--selftest" in sys.argv

    if not os.path.exists(binary):
        raise SystemExit(f"no engine at {binary}")

    if selftest:
        H, p = 8, PRIMES[0]
        rows = parse(run_rows(binary, H, p, 8))
        exact = banked(rowdir, H)
        try:
            check_rule(rows, exact, H, p, corrupt=max(exact))
        except AssertionError:
            print("RED 1 GREEN: a corrupted banked value is caught")
        else:
            raise SystemExit("RED CONTROL FAILED: corruption not caught")
        try:
            check_rule(rows, exact, H, PRIMES[1])
        except AssertionError:
            print("RED 2 GREEN: the wrong modulus is caught")
        else:
            raise SystemExit("RED CONTROL FAILED: wrong modulus not caught")
        return

    total = 0
    for H in range(1, hmax + 1):
        exact = banked(rowdir, H)
        for p in PRIMES:
            body = run_rows(binary, H, p, 8)
            total += check_rule(parse(body), exact, H, p)
            if ref and os.path.exists(ref):
                if body != run_rows(ref, H, p, 0):
                    raise AssertionError(f"H={H} p={p}: parallel != cutcount_b1 byte for byte")
        # determinism: one prime, three thread counts
        base = run_rows(binary, H, PRIMES[0], 1)
        for t in (16, 80):
            if run_rows(binary, H, PRIMES[0], t) != base:
                raise AssertionError(f"H={H}: thread count {t} changed the row -- race")
        print(f"  H={H:2d}: {len(exact)} cells x {len(PRIMES)} primes vs banked, "
              f"3 thread counts identical")
    print(f"GATE GREEN: {total} cell-comparisons against banked rows, H = 1..{hmax}")


if __name__ == "__main__":
    main()
