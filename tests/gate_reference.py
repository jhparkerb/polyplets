#!/usr/bin/env python3
"""Gate: every in-scope program still prints exactly what it printed before
the rewrite (docs/code-target.md).

Each case below is one run of one program at a fixed size.  Its output, less
the event= observability lines (which carry times and revisions), was
recorded from the code at master b093919 into tests/reference/<name>.txt,
and must match byte for byte.  The motley_par case was recorded after the
macOS clear() fix (085aa5f), which does not change what it computes.

Usage:
  python3 tests/gate_reference.py              # check every case
  python3 tests/gate_reference.py --record     # rewrite the reference files
  python3 tests/gate_reference.py --selftest   # RED controls, then check

A missing reference file is a failure, not a skip.  Peak memory of every
case is under 100 MB; the whole check takes about a minute on gympie.
"""

import os
import shutil
import subprocess
import sys
import tempfile

from common import ROOT, Gate, parse_counts, run

REFDIR = os.path.join(ROOT, "tests", "reference")
BUILD = os.path.join(ROOT, "build")
P = 2147483647


def strip_events(text):
    return "".join(ln + "\n" for ln in text.splitlines()
                   if not ln.startswith("event="))


def g2():
    return strip_events(run(f"{BUILD}/g2", "square8", 12, "--per-box"))


def per_height(binary, args_for, hmax):
    """Run one height at a time into a scratch file; lines are 'H n value'."""
    out = []
    with tempfile.TemporaryDirectory() as d:
        for H in range(1, hmax + 1):
            path = os.path.join(d, f"h{H}.out")
            run(binary, *args_for(H, path))
            with open(path) as f:
                out += [f"{H} {ln}" for ln in f.read().splitlines()]
    return "".join(ln + "\n" for ln in out)


def strip_tm():
    return per_height(f"{BUILD}/strip_tm",
                      lambda H, path: ("single", H, 24, path), 10)


def motley_par():
    return per_height(f"{BUILD}/motley_par",
                      lambda H, path: ("--modp", H, 24, P, path, "--threads", 4),
                      10)


def by_type(binary, types, maxn):
    """Each type's output lines, prefixed with the type."""
    return "".join(f"{t} {ln}\n" for t in types for ln in
                   strip_events(run(f"{BUILD}/{binary}", t, maxn)).splitlines())


def symcount_fast():
    return by_type("symcount_fast",
                   ["r90", "r180", "hmirror", "dmirror", "c4", "d2ax", "d2diag", "d4"], 16)


def symtm():
    return by_type("symtm", ["hmirror", "r180", "dmirror"], 20)


def dmirror_spine():
    return strip_events(run(f"{BUILD}/dmirror_spine", 10))


def term26():
    """scripts/term.sh 26: a(1..26), and the triangle T(n,H) as 'H n T' lines.

    term.sh writes its per-height rows to runs/ns_a26/perheight whatever
    RUNDIR is, so that directory is emptied first and read afterwards."""
    perheight = os.path.join(ROOT, "runs", "ns_a26", "perheight")
    shutil.rmtree(perheight, ignore_errors=True)
    with tempfile.TemporaryDirectory() as d:
        rundir = os.path.join(d, "ns_a26")
        r = subprocess.run([os.path.join(ROOT, "scripts", "term.sh"), "26"],
                           cwd=ROOT, env={**os.environ, "RUNDIR": rundir},
                           capture_output=True, text=True)
        if r.returncode != 0:
            raise RuntimeError(f"term.sh 26: rc={r.returncode}\n{r.stdout[-2000:]}{r.stderr}")
        with open(os.path.join(rundir, "a_n.txt")) as f:
            out = [f"a {ln}" for ln in f.read().splitlines()]
    for H in range(1, 27):
        with open(os.path.join(perheight, f"h{H}.out")) as f:
            out += [f"{H} {ln}" for ln in f.read().splitlines()]
    return "".join(ln + "\n" for ln in out)


CASES = [
    ("g2_square8_12", "build/g2 square8 12 --per-box", g2),
    ("strip_tm_h10_n24", "build/strip_tm single H 24, H = 1..10", strip_tm),
    ("motley_par_h10_n24", f"build/motley_par --modp H 24 {P}, H = 1..10", motley_par),
    ("symcount_fast_16", "build/symcount_fast TYPE 16, all eight types", symcount_fast),
    ("symtm_20", "build/symtm TYPE 20, hmirror r180 dmirror", symtm),
    ("dmirror_spine_10", "build/dmirror_spine 10", dmirror_spine),
    ("term_26", "scripts/term.sh 26: a(n) and the per-height triangle", term26),
]


def refpath(name):
    return os.path.join(REFDIR, name + ".txt")


def compare(got, want):
    """None if equal, else a one-line description of the first difference."""
    if got == want:
        return None
    g, w = got.splitlines(), want.splitlines()
    for i, (a, b) in enumerate(zip(g, w)):
        if a != b:
            return f"line {i + 1}: got '{a}' want '{b}'"
    return f"{len(g)} lines, want {len(w)}"


def cross_checks(gate, outputs):
    """Three programs, one triangle.  strip_tm's C_H(n) counts placements of
    polyplets of height <= H in a height-H strip, so its second difference in
    H is T(n,H); motley_par computes the same C_H(n) by coloring, mod P."""
    C = parse_counts(outputs["strip_tm_h10_n24"])
    T = parse_counts("\n".join(ln for ln in outputs["term_26"].splitlines()
                               if not ln.startswith("a ")))
    M = parse_counts(outputs["motley_par_h10_n24"])
    c = lambda H, n: C.get((H, n), 0)
    cells = [(H, n) for H in range(1, 11) for n in range(1, 25)]
    bad = [k for k in cells
           if c(k[0], k[1]) - 2 * c(k[0] - 1, k[1]) + c(k[0] - 2, k[1]) != T.get(k, 0)]
    gate.check(not bad, f"strip_tm second difference == term.sh triangle, "
                        f"{len(cells)} cells H<=10 n<=24" + (f"  MISMATCH {bad[:5]}" if bad else ""))
    bad = [k for k in cells if c(*k) % P != M.get(k, 0)]
    gate.check(not bad, f"motley_par == strip_tm mod {P}, {len(cells)} cells"
                        + (f"  MISMATCH {bad[:5]}" if bad else ""))


def selftest(gate, outputs):
    """Every case must fail against a reference with one digit changed, and
    against a missing line."""
    for name, _, _ in CASES:
        got = outputs[name]
        digit = next(i for i, c in enumerate(got) if c.isdigit())
        bent = got[:digit] + str((int(got[digit]) + 1) % 10) + got[digit + 1:]
        short = "".join(got.splitlines(keepends=True)[:-1])
        gate.check(compare(got, bent) is not None and compare(got, short) is not None,
                   f"RED {name}: a changed digit and a dropped line are both caught")


def main():
    gate = Gate()
    outputs = {}
    for name, desc, fn in CASES:
        outputs[name] = fn()
        if "--record" in sys.argv:
            os.makedirs(REFDIR, exist_ok=True)
            with open(refpath(name), "w") as f:
                f.write(outputs[name])
            print(f"recorded {name}: {len(outputs[name].splitlines())} lines  ({desc})")
            continue
        if not os.path.exists(refpath(name)):
            gate.check(False, f"{name}: no reference file {refpath(name)}")
            continue
        with open(refpath(name)) as f:
            diff = compare(outputs[name], f.read())
        gate.check(diff is None and outputs[name] != "",
                   f"{name}: {len(outputs[name].splitlines())} lines == reference  ({desc})"
                   + (f"\n   {diff}" if diff else ""))
    if "--record" in sys.argv:
        return 0
    cross_checks(gate, outputs)
    if "--selftest" in sys.argv:
        selftest(gate, outputs)
    return gate.verdict("REFERENCE")


if __name__ == "__main__":
    sys.exit(main())
