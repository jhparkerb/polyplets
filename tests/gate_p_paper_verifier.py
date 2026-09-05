#!/usr/bin/env python3
"""RED-first gate for the P-paper verifier: prove a wrong number goes red.

WHY.  `paper/verify_l_papers.py` guards the machine-written papers with 23 RED
controls, every one of which fires.  The two verifiers that guard the
HUMAN-authored papers -- `paper/verify_technical_report.py` (781 checks) and
`paper/verify_claims.py` (428) -- had none.  Both were green, and nothing
established that they would be anything else if the paper were wrong.  A
verifier with no RED control is an assertion about itself.

WHAT THIS DOES.  Every numeric literal of two or more digits in
`paper/technical-report.tex` is perturbed in its last digit, in a COPY, and the
verifier is re-run.  A literal whose perturbation still passes is UNGUARDED --
the paper prints it and no check reads it.  Measured 2026-08-23 at four or
more digits: 199 of 200 guarded.  Widened 2026-09-05 to two or more, because
the paper's scope claims are two-digit (Redelmeier to 22, Motley to H = 19,
P_k to 19, holes to 18 and 14, 25^k/k!) and the verifier now reads each of
them out of its sentence; and the shading macro's brace-less argument
(\\g1480) is a literal too, where the old lookbehind skipped it.  The
exceptions -- the year on the title page, the type size -- are not claims and
are named in ALLOWED below with their reasons.  Any new unguarded literal
fails this gate, so the coverage cannot silently drop when the paper gains a
number.

jasonp's prose is never written.  The verifier takes VERIFY_TEX purely so this
gate can point it at a temporary copy; `paper/technical-report.tex` is opened
read-only here and by everything else in the tree.

`--selftest` is this gate's own RED control: run the same sweep against a stub
verifier that always exits 0, and every literal must come back unguarded.  If
the harness cannot detect a verifier that checks nothing, its green means
nothing.

    python3 tests/gate_p_paper_verifier.py [--selftest]
"""
import os
import re
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEX = ROOT / "paper" / "technical-report.tex"
VERIFIER = ROOT / "paper" / "verify_technical_report.py"

# literal -> why it is not a claim the verifier should read
ALLOWED = {
    "2026": r"the year in \date{July 18, 2026} on the title page",
}

# Numbers inside these never assert anything about the mathematics.
STRIP = re.compile(
    r"\\(cite|label|ref|eqref|url|href|arxiv|includegraphics)\{[^}]*\}|%[^\n]*")
# A literal stands alone (not part of a longer number, identifier or decimal)
# or follows the brace-less shading macro \g.
BOUNDARY = r"(?:(?<![0-9A-Za-z.])|(?<=\\g)|(?<=A))"
LITERAL = re.compile(BOUNDARY + r"[0-9]{2,}(?![0-9])")


def literals(src):
    masked = STRIP.sub(lambda m: " " * len(m.group(0)), src)
    return sorted({m.group(0) for m in LITERAL.finditer(masked)})


# Running the verifier as a child, optionally under the subprocess-output cache
# that makes a slow verifier auditable (tests/_audit_subprocess_cache.py).
_SHIM = ("import sys; sys.path.insert(0, {tests!r}); "
         "import _audit_subprocess_cache; import runpy; "
         "runpy.run_path({verifier!r}, run_name='__main__')")


def _argv(verifier):
    if os.environ.get("AUDIT_SUBPROC_CACHE"):
        return [sys.executable, "-c",
                _SHIM.format(tests=str(Path(__file__).resolve().parent),
                             verifier=str(verifier))]
    return [sys.executable, str(verifier)]


# One verifier run is 0.32 s of real work (measured; a bare interpreter is
# 0.01 s, so this is not startup), and there are 200 of them -- 70 s serial.
# Sampling the literals is not available: the whole statement is COVERAGE, and a
# sample would let coverage drop silently, which is the one thing this gate
# exists to prevent. So all 200 still run; they just stop waiting in line.
#
# They are independent by construction -- each is one perturbed copy judged on
# its own -- and each now writes its OWN copy, where the serial version reused a
# single under-test.tex that concurrency would have had them fighting over.
# ex.map preserves input order, so the output is identical to the serial sweep's.
# Same pattern as gate_tma's spawn block, and for the same reason.
# TODO(2026-08-24, from the simplify pass): this is a second pool-size policy
# beside tests/common.py's spawn()/_POOL_MAX. Reusing that pool needs
# common.spawn to grow env= and check=False (the probe needs both VERIFY_TEX and
# the returncode), which is a change to shared code outside this gate's diff.
WORKERS = min(8, os.cpu_count() or 4)


def sweep(verifier, src, lits, tmpdir):
    """Return the literals whose perturbation the verifier does NOT catch."""
    argv = _argv(verifier)

    # The green control runs alone and first: if the unmutated copy does not
    # pass, no RED result below would mean anything.
    path = os.path.join(tmpdir, "under-test.tex")
    open(path, "w").write(src)
    green = subprocess.run(argv, env=dict(os.environ, VERIFY_TEX=path),
                           capture_output=True, text=True)
    if green.returncode != 0:
        print("GREEN CONTROL FAILED: the unmutated copy does not pass, so no")
        print("RED result below would mean anything.")
        print(green.stdout[-2000:])
        sys.exit(2)

    def probe(lit):
        """-> lit if the verifier did NOT catch its perturbation, else None."""
        bumped = lit[:-1] + str((int(lit[-1]) + 1) % 10)
        p = os.path.join(tmpdir, f"under-test-{lit}.tex")
        open(p, "w").write(
            re.sub(BOUNDARY + lit + r"(?![0-9])", bumped, src))
        r = subprocess.run(argv, env=dict(os.environ, VERIFY_TEX=p),
                           capture_output=True, text=True)
        return lit if r.returncode == 0 else None

    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        return [lit for lit in ex.map(probe, lits) if lit is not None]


def context(src, lit):
    m = re.search(BOUNDARY + lit + r"(?![0-9])", src)
    a, b = max(0, m.start() - 70), min(len(src), m.end() + 40)
    return re.sub(r"\s+", " ", src[a:b]).strip()


def main():
    src = TEX.read_text()
    lits = literals(src)

    # TODO(2026-08-24, /simplify): the selftest sweeps ALL ~200 literals against
    # a stub that is sys.exit(0). The stub's verdict is literal-independent by
    # construction, so lits[:10] asserting 10/10 unguarded proves the same
    # property of the harness -- and every literal's regex is exercised anyway
    # by the production sweep below, in the same recipe. Left as-is because
    # narrowing a RED control's coverage deserves its own decision, and the
    # gate is stamp-gated now, so it runs only when the paper or verifier moves.
    if "--selftest" in sys.argv:
        with tempfile.TemporaryDirectory() as d:
            stub = os.path.join(d, "stub_verifier.py")
            open(stub, "w").write("import sys; sys.exit(0)\n")
            missed = sweep(Path(stub), src, lits, d)
        ok = len(missed) == len(lits)
        print(f"selftest: a verifier that checks nothing is reported as "
              f"{len(missed)}/{len(lits)} unguarded  "
              f"{'OK' if ok else 'FAILED'}")
        return 0 if ok else 1

    with tempfile.TemporaryDirectory() as d:
        unguarded = sweep(VERIFIER, src, lits, d)

    guarded = len(lits) - len(unguarded)
    print(f"{TEX.name}: {len(lits)} numeric literals, {guarded} guarded, "
          f"{len(unguarded)} unguarded")
    bad = []
    for lit in unguarded:
        why = ALLOWED.get(lit)
        if why:
            print(f"  allowed  {lit}  -- {why}")
        else:
            bad.append(lit)
            print(f"  UNGUARDED {lit}: ...{context(src, lit)}...")
    if bad:
        print()
        print(f"GATE P-PAPER-VERIFIER: RED -- {len(bad)} literal(s) the paper "
              f"prints and no check reads.")
        print("Add a check to paper/verify_technical_report.py, or, if the "
              "number is not a claim, name it in ALLOWED with its reason.")
        return 1
    print("GATE P-PAPER-VERIFIER: GREEN")
    return 0


if __name__ == "__main__":
    sys.exit(main())
