#!/usr/bin/env python3
"""Gate KINK-ORACLE: the production kink kernel against an external oracle with
NO closed-form injection, and against the column kernel height by height.

The kink-carry kernel produced a(30)..a(40) and a(41)'s swept half.  Its
in-make oracle coverage before 2026-09-05 was the maxn-14 sweeps of
ns-gate-asan / ns-gate-parallel, where the wired diagonal closed forms inject
every height H >= 8, so the kernel itself was exercised at H <= 7 only
(AUDIT-2026-09-02, "a(23)..a(35)"); its production validation was the a(29)
cell-diff against the column kernel (scripts/kink_validate.sh) and the Motley
agreement, neither in `make`.  This gate is the automated version.

Two runs of build/ns/orchestrate with --max-diag-k 0, which disables every
wired diagonal (orchestrator/maxdiagk_test.go, TestMaxDiagKZeroDisablesInjection),
so every height is a real sweep:

  ORACLE   --kernel kink --maxn 18: the per-height rows h<H>.out must be
           present for every H = 1..18, carry every n, and sum over H to the
           EXTERNALLY published a(1)..a(18) of fixtures/b006770.txt
           (Redelmeier, Mertens, Tremblay-Vernay -- nothing of ours).  This is
           the kink kernel reproducing the whole known sequence with every
           height enumerated.  Measured 2026-09-05 on gympie: 68 s at 8 cores,
           90 MB.
  TWIN     --kernel kink and --kernel column at --maxn 16, both all-real: the
           two per-height directories must be byte-identical, every height,
           every n.  The column kernel is the reference implementation kept as
           the correctness oracle (orchestrate --help).  0.7 s + ~10 s.

Both checks are done here in Python from the h<H>.out files; the
orchestrator's own --compare line is not what is trusted.  Fail-closed on
coverage: a missing height, an empty row, or a run that wrote fewer files
than maxn fails rather than shrinking the comparison.

RED controls (--selftest, no engine run): one cell of a staged per-height set
perturbed by one must fail the oracle sum and the twin diff; a missing height
must fail coverage; an empty directory must fail rather than compare nothing.

Usage: python3 tests/gate_kink_oracle.py [--selftest] [--keep DIR]
"""
import os
import shutil
import subprocess
import sys
import tempfile

from common import ROOT, Gate, read_bfile

ORCHESTRATE = os.path.join(ROOT, "build", "ns", "orchestrate")
WORKERS = os.path.join(ROOT, "build", "ns")
MAXN_ORACLE = 18
MAXN_TWIN = 16
CORES = 4
RAM = 256 * 1024 * 1024


def sweep(kernel, maxn, workdir):
    """Run one all-real sweep; return the per-height directory."""
    run_dir = os.path.join(workdir, f"{kernel}{maxn}")
    ph = os.path.join(run_dir, "ph")
    os.makedirs(os.path.join(run_dir, "spill"))
    os.makedirs(ph)
    cmd = [ORCHESTRATE, "--maxn", str(maxn), "--cores", str(CORES),
           "--ram", str(RAM), "--kernel", kernel, "--max-diag-k", "0",
           "--workers-dir", WORKERS,
           "--run-dir", run_dir, "--spill-dir", os.path.join(run_dir, "spill"),
           "--checkpoint", os.path.join(run_dir, "POLYCKPT"),
           "--checkpoint-every", "0", "--per-height-out", ph]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"orchestrate {kernel} maxn={maxn} rc={r.returncode}\n"
                           f"{r.stdout[-800:]}\n{r.stderr[-800:]}")
    return ph


def read_perheight(ph, maxn):
    """{H: {n: T(n,H)}}; raises on a missing height or an empty row."""
    T = {}
    for H in range(1, maxn + 1):
        path = os.path.join(ph, f"h{H}.out")
        if not os.path.exists(path):
            raise ValueError(f"h{H}.out missing under {ph}")
        rows = {}
        for line in open(path):
            q = line.split()
            if len(q) == 2:
                rows[int(q[0])] = int(q[1])
        if set(rows) != set(range(1, maxn + 1)):
            raise ValueError(f"h{H}.out carries n = {sorted(rows)[:3]}..., "
                             f"not 1..{maxn}")
        T[H] = rows
    return T


def check_oracle(ph, maxn, fixture):
    """Row sums over all real-swept heights equal the published a(n)."""
    T = read_perheight(ph, maxn)
    bad = []
    for n in range(1, maxn + 1):
        tot = sum(T[H].get(n, 0) for H in T)
        if tot != fixture[n]:
            bad.append((n, tot, fixture[n]))
    return bad, maxn * maxn


def check_twin(ph_kink, ph_col, maxn):
    """The two kernels' per-height rows are identical, cell for cell."""
    A, B = read_perheight(ph_kink, maxn), read_perheight(ph_col, maxn)
    bad = [(n, H) for H in range(1, maxn + 1) for n in range(1, maxn + 1)
           if A[H].get(n) != B[H].get(n)]
    return bad, maxn * maxn


def main():
    gate = Gate()
    if not os.path.exists(ORCHESTRATE):
        print(f"FAIL missing binary {ORCHESTRATE} (run: make build/ns/orchestrate)")
        return 1
    fixture = read_bfile("b006770.txt")
    keep = sys.argv[sys.argv.index("--keep") + 1] if "--keep" in sys.argv else None
    work = keep or tempfile.mkdtemp(prefix="gate_kink_oracle.")
    try:
        ph18 = sweep("kink", MAXN_ORACLE, work)
        bad, cells = check_oracle(ph18, MAXN_ORACLE, fixture)
        gate.check(not bad,
                   f"ORACLE kink, every height real, maxn={MAXN_ORACLE}: row sums "
                   f"== published a(1..{MAXN_ORACLE}) ({cells} cells summed)"
                   + (f"  MISMATCH at n={[b[0] for b in bad]}" if bad else ""))
        phk = sweep("kink", MAXN_TWIN, work)
        phc = sweep("column", MAXN_TWIN, work)
        bad, cells = check_twin(phk, phc, MAXN_TWIN)
        gate.check(not bad,
                   f"TWIN   kink == column, every height real, maxn={MAXN_TWIN}: "
                   f"{cells} cells byte-identical"
                   + (f"  DIFFER at {bad[:4]}" if bad else ""))
        bad, _ = check_oracle(phc, MAXN_TWIN, fixture)
        gate.check(not bad,
                   f"ORACLE column, every height real, maxn={MAXN_TWIN}: row sums "
                   f"== published a(1..{MAXN_TWIN})")
    finally:
        if not keep:
            shutil.rmtree(work, ignore_errors=True)
    return gate.verdict("kink-oracle")


def selftest():
    """RED controls on staged per-height sets; no engine is run."""
    fixture = read_bfile("b006770.txt")
    problems = []
    maxn = 6
    with tempfile.TemporaryDirectory() as d:
        # A correct set: T(n,H) from the banked triangle, n <= 6.
        tri = {}
        for line in open(os.path.join(ROOT, "results", "triangle.txt")):
            if line.strip() and not line.startswith("#"):
                n, h, v = line.split()
                tri[(int(n), int(h))] = int(v)

        def write(ph, mutate=None):
            os.makedirs(ph)
            for H in range(1, maxn + 1):
                rows = {n: tri.get((n, H), 0) for n in range(1, maxn + 1)}
                if mutate:
                    mutate(H, rows)
                with open(os.path.join(ph, f"h{H}.out"), "w") as fh:
                    for n in range(1, maxn + 1):
                        if n in rows:
                            fh.write(f"{n} {rows[n]}\n")

        good = os.path.join(d, "good")
        write(good)
        bad, _ = check_oracle(good, maxn, fixture)
        if bad:
            problems.append(f"GREEN: the banked triangle fails the oracle sum: {bad}")

        # RED 1: one cell off by one fails the sum and the twin diff.
        off = os.path.join(d, "off")
        write(off, lambda H, rows: rows.__setitem__(4, rows[4] + 1) if H == 2 else None)
        bad, _ = check_oracle(off, maxn, fixture)
        if [b[0] for b in bad] != [4]:
            problems.append(f"RED 1: a +1 cell was not caught by the oracle sum ({bad})")
        bad, _ = check_twin(good, off, maxn)
        if bad != [(4, 2)]:
            problems.append(f"RED 1: a +1 cell was not caught by the twin diff ({bad})")

        # RED 2: a missing height must fail coverage, not sum fewer rows.
        short = os.path.join(d, "short")
        write(short)
        os.unlink(os.path.join(short, f"h{maxn}.out"))
        try:
            check_oracle(short, maxn, fixture)
            problems.append("RED 2: a missing height passed")
        except ValueError:
            pass

        # RED 3: an empty directory must fail, not compare nothing.
        empty = os.path.join(d, "empty")
        os.makedirs(empty)
        try:
            check_twin(empty, empty, maxn)
            problems.append("RED 3: two empty directories compared equal")
        except ValueError:
            pass

        # RED 4: a row with a missing n must fail coverage.
        holed = os.path.join(d, "holed")
        write(holed, lambda H, rows: rows.pop(3) if H == 1 else None)
        try:
            check_oracle(holed, maxn, fixture)
            problems.append("RED 4: a row missing n = 3 passed")
        except ValueError:
            pass

    if problems:
        print("kink-oracle selftest FAILED:")
        for p in problems:
            print("  " + p)
        return 1
    print("kink-oracle selftest ok: 1 green control, 4 RED controls, all fired")
    return 0


if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv else main())
