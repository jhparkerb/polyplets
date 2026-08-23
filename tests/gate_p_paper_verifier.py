#!/usr/bin/env python3
"""RED-first gate for the P-paper verifier: prove a wrong number goes red.

WHY.  `paper/verify_l_papers.py` guards the machine-written papers with 23 RED
controls, every one of which fires.  The two verifiers that guard the
HUMAN-authored papers -- `paper/verify_technical_report.py` (781 checks) and
`paper/verify_claims.py` (428) -- had none.  Both were green, and nothing
established that they would be anything else if the paper were wrong.  A
verifier with no RED control is an assertion about itself.

WHAT THIS DOES.  Every numeric literal of four or more digits in
`paper/technical-report.tex` is perturbed in its last digit, in a COPY, and the
verifier is re-run.  A literal whose perturbation still passes is UNGUARDED --
the paper prints it and no check reads it.  Measured 2026-08-23: 199 of 200
guarded.  The one exception is the year on the title page, which is not a
claim, and it is named in ALLOWED below with its reason.  Any new unguarded
literal fails this gate, so the coverage cannot silently drop when the paper
gains a number.

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
LITERAL = re.compile(r"(?<![0-9A-Za-z.])[0-9]{4,}(?![0-9])")


def literals(src):
    masked = STRIP.sub(lambda m: " " * len(m.group(0)), src)
    return sorted({m.group(0) for m in LITERAL.finditer(masked)})


def sweep(verifier, src, lits, tmpdir):
    """Return the literals whose perturbation the verifier does NOT catch."""
    path = os.path.join(tmpdir, "under-test.tex")
    env = dict(os.environ, VERIFY_TEX=path)

    open(path, "w").write(src)
    green = subprocess.run([sys.executable, str(verifier)], env=env,
                           capture_output=True, text=True)
    if green.returncode != 0:
        print("GREEN CONTROL FAILED: the unmutated copy does not pass, so no")
        print("RED result below would mean anything.")
        print(green.stdout[-2000:])
        sys.exit(2)

    unguarded = []
    for lit in lits:
        bumped = lit[:-1] + str((int(lit[-1]) + 1) % 10)
        open(path, "w").write(
            re.sub(r"(?<![0-9A-Za-z.])" + lit + r"(?![0-9])", bumped, src))
        r = subprocess.run([sys.executable, str(verifier)], env=env,
                           capture_output=True, text=True)
        if r.returncode == 0:
            unguarded.append(lit)
    return unguarded


def context(src, lit):
    m = re.search(r"(?<![0-9A-Za-z.])" + lit + r"(?![0-9])", src)
    a, b = max(0, m.start() - 70), min(len(src), m.end() + 40)
    return re.sub(r"\s+", " ", src[a:b]).strip()


def main():
    src = TEX.read_text()
    lits = literals(src)

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
