#!/usr/bin/env python3
"""Which numbers in an L paper does verify_l_papers.py actually read?

The P-paper measurement (tests/p_paper_coverage_audit.py) pointed at the L
corpus.  It matters more here.  On the P side the question was how much of one
guarded manuscript is guarded; on the L side only four of the six manuscripts
have any checks at all, and every one of the six carries a disclosure block
reading "human verification: none".  Unguarded literals are the whole exposure.

    python3 tests/l_paper_coverage_audit.py            # all six
    python3 tests/l_paper_coverage_audit.py --paper L5

verify_l_papers.py runs in 0.16 s, so there is no subprocess cache and no
sharding: the full sweep is minutes on one core.  That verifier reads several
manuscripts, so the perturbed copy reaches it through VERIFY_TEX plus
VERIFY_TEX_NAME, which says which one it replaces.

TWO CHANGES FROM THE P-SIDE SWEEP, both because the L papers state their claims
differently.

  1. Decimals count.  The P extractor is `[0-9]{4,}` with a lookbehind that
     rejects a leading '.', so it cannot see 6.543 or 9.3154 -- which are L3's
     two headline constants and the whole point of that paper.  Here a decimal
     is one literal, perturbed in its last digit.
  2. The integer floor is 3 digits, not 4, because L6's min-end constants run
     1, 6, 22, 68, 187, 470, 1106 and L3's certified rungs are three digits.
     Below three the sweep is noise: a bumped "2" is not a wrong claim, it is a
     different sentence.

Both widen coverage rather than narrow it, so a literal this reports as
unguarded really is one the verifier does not read.

The GREEN control runs first, as on the P side: if the unmutated copy does not
pass on this box the run exits 2, rather than reporting a wall of false
"guarded" results.  A manuscript with no checks at all comes back as an honest
"0 of N guarded" -- that is the measurement, not a failure.
"""
import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VERIFIER = ROOT / "paper" / "verify_l_papers.py"

# Numbers inside these never assert anything about the mathematics.  The
# \textwidth clause is here because `R{0.56\textwidth}` is a column width and
# reading it as a claim was the first false positive this sweep produced.
STRIP = re.compile(
    r"\\(cite|label|ref|eqref|url|href|arxiv|includegraphics)\{[^}]*\}"
    r"|[0-9.]+\\(text|line|column|page)width"
    r"|%[^\n]*")
LITERAL = re.compile(
    r"(?<![0-9A-Za-z.])[0-9]+\.[0-9]+(?![0-9])"      # decimals, whole
    r"|(?<![0-9A-Za-z.])[0-9]{3,}(?![0-9])")         # integers, 3+ digits

# The papers write thousands as 96{,}065.  Extract from a copy with those
# separators removed, so the literal is 96065 and not the fragment 065, and put
# the separator back as an optional group when searching the real source.
SEP = re.compile(r"\{,\}")


def pattern(lit):
    body = r"(?:\{,\})?".join(re.escape(c) for c in lit)
    return r"(?<![0-9A-Za-z.])" + body + r"(?![0-9])"

# literal -> why it is not a claim any verifier should read
ALLOWED = {
    "2026": r"the year in \date{August 2026} on every title page",
}


def literals(src):
    masked = STRIP.sub(lambda m: " " * len(m.group(0)), src)
    return sorted({m.group(0) for m in LITERAL.finditer(SEP.sub("", masked))})


# TODO(2026-08-24, /simplify): sweep() and context() below are a hand-copied
# variant of tests/gate_p_paper_verifier.py's, which the SIBLING audit
# (tests/p_paper_coverage_audit.py) imports rather than copies. The differences
# are small and parametrizable: a pattern() tolerating {,} thousands
# separators, the VERIFY_TEX_NAME env var, and no cache shim. Parametrizing the
# gate's sweep on a pattern-builder plus extra env would let this import it too
# -- one mutation harness instead of two. Not done here because it edits a gate
# on the per-push path to serve an unwired audit.
def sweep(src, lits, name, tmpdir):
    """Return the literals whose perturbation the verifier does NOT catch."""
    path = os.path.join(tmpdir, "under-test.tex")
    env = dict(os.environ, VERIFY_TEX=path, VERIFY_TEX_NAME=name)
    argv = [sys.executable, str(VERIFIER)]

    Path(path).write_text(src)
    green = subprocess.run(argv, env=env, capture_output=True, text=True)
    if green.returncode != 0:
        print("GREEN CONTROL FAILED: the unmutated copy does not pass, so no")
        print("result below would mean anything.")
        print(green.stdout[-2000:])
        sys.exit(2)

    unguarded = []
    for lit in lits:
        last = str((int(lit[-1]) + 1) % 10)
        Path(path).write_text(
            re.sub(pattern(lit), lambda m: m.group(0)[:-1] + last, src))
        r = subprocess.run(argv, env=env, capture_output=True, text=True)
        if r.returncode == 0:
            unguarded.append(lit)
    return unguarded


def context(src, lit):
    m = re.search(pattern(lit), src)
    if not m:
        return ""
    a, b = max(0, m.start() - 70), min(len(src), m.end() + 40)
    return re.sub(r"\s+", " ", src[a:b]).strip()


def manuscripts():
    # Enumerated, not frozen: the 2026-08-23 contraction merged four
    # manuscripts into their partners, and a hardcoded list would have gone
    # stale that day.
    # Numeric key, matching tests/gate_l_paper_verifier.py and
    # docs/reviews/llm-tics/density.py, which enumerate the same glob. Plain
    # sorted() is lexicographic, which put L10 between L1 and L2 here and
    # nowhere else -- three copies of one enumeration, already drifting.
    return {p.name.split("-")[0]: p
            for p in sorted((ROOT / "paper").glob("L[0-9]*.tex"),
                            key=lambda f: int(f.name.split("-")[0][1:]))}


# TODO(2026-08-24, /simplify): this measures L-corpus literal coverage and
# always exits 0, so coverage can regress silently while gate-l-paper-verifier
# stays green -- the kill matrix proves EXISTING checks can fail, it says
# nothing about NEW literals being read at all. The full sweep is ~80 s, less
# than the wired gate-severance-w1 was. A per-paper unguarded-count ceiling
# seeded from the banked table (results/l-paper-verifier-coverage.md) would
# ratchet it; the readability campaign only lowers counts, so a ceiling never
# fights it. ~30 lines + a recipe. Not now: that campaign is mid-flight and
# rewriting these files.
def main():
    papers = manuscripts()
    ap = argparse.ArgumentParser()
    ap.add_argument("--paper", choices=sorted(papers) + ["all"], default="all")
    ap.add_argument("--out")
    a = ap.parse_args()

    report, tot_l, tot_u = {}, 0, 0
    for key in (sorted(papers) if a.paper == "all" else [a.paper]):
        tex = papers[key]
        src = tex.read_text()
        lits = [l for l in literals(src) if l not in ALLOWED]
        with tempfile.TemporaryDirectory() as d:
            unguarded = sweep(src, lits, tex.name, d)
        tot_l += len(lits)
        tot_u += len(unguarded)
        print(f"{tex.name}: {len(lits)} literals, "
              f"{len(lits) - len(unguarded)} guarded, "
              f"{len(unguarded)} unguarded", flush=True)
        for lit in unguarded:
            print(f"  UNGUARDED {lit}: ...{context(src, lit)}...")
        report[tex.name] = {"literals": lits, "unguarded": unguarded}

    if a.paper == "all":
        print(f"\nL corpus: {tot_l} literals, {tot_l - tot_u} guarded, "
              f"{tot_u} unguarded")
    if a.out:
        Path(a.out).write_text(json.dumps(report, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
