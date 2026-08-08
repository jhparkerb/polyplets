#!/usr/bin/env python3
"""Gate: mutation-test paper/verify_l_papers.py's text assertions.

RED-first, and it is a gate on the *verifier*, not on the papers.

verify_l_papers.py makes two kinds of assertion. Most of them recompute a value
from banked data and compare — those carry their own negative controls, thirteen
of them, and every one fires. The rest assert that a manuscript actually prints
a number the verifier just computed. Not one of those had a negative control,
and on 2026-08-07 that turned out to matter: the assertions were written as
`str(value) in src`, plain substring containment against the whole file, so

    ok(all(str(d) in src for d in PSI_DEGREES), ...)

is satisfied by "1", "2", "4" and "9" occurring anywhere in a LaTeX document.
Delete the line of L4 that prints all ten psi-degrees and the check stays green.
"58" in L1 is satisfied by the "6558" inside a table entry.

A check that cannot fail is not a check, and the only way to know which ones can
fail is to break the paper on purpose and watch. That is what this does: for each
text assertion, corrupt exactly the thing it claims to be watching, run the
verifier against the corrupted copy, and require it to go red. The manuscripts on
disk are never modified — every mutation is applied to a copy in a temp tree and
verify_l_papers.PAPER is pointed at it.

    python3 tests/gate_l_paper_verifier.py            # gate
    python3 tests/gate_l_paper_verifier.py -v         # per-mutation detail

Exit 0 iff every mutation below is detected.
"""

import importlib.util
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAPER = ROOT / "paper"
VERIFIER = PAPER / "verify_l_papers.py"

L_PAPERS = [
    "L1-diagonal-law.tex",
    "L2-ternary-spine.tex",
    "L3-lambda-bounds.tex",
    "L4-not-dfinite.tex",
    "L5-convex-king-animals.tex",
    "L6-perimeter-gradings.tex",
]

# (id, paper, old, new, what the corruption represents)
#
# Each mutation is a plausible manuscript error, not a nonsense edit: a digit
# typed wrong, or a line dropped in an edit. `new` of None means "delete the
# line containing `old`", which is how a trim loses a constant.
MUTATIONS = [
    ("psi-degrees-dropped", "L4-not-dfinite.tex",
     "1, 2, 4, 9, 29, 68, 181, 462, 1254, 3289", None,
     "L4 loses the line printing every psi-degree the boxes are built from"),

    ("psi-degree-typo", "L4-not-dfinite.tex",
     "1, 2, 4, 9, 29, 68, 181, 462, 1254, 3289",
     "1, 2, 4, 9, 29, 68, 181, 462, 1254, 3298",
     "L4 prints 3298 for the H=10 psi-degree instead of 3289"),

    ("psi-box-typo", "L4-not-dfinite.tex",
     r"D \le 3288", r"D \le 3287",
     "L4 prints an exclusion box one degree narrower than the data supports"),

    ("pair-weights-dropped", "L1-diagonal-law.tex",
     r"$\Wp = 58$ and $114$", None,
     "L1 loses the line printing the corrected interval pair weights"),

    ("pair-weight-typo", "L1-diagonal-law.tex",
     r"$\Wp = 58$ and $114$", r"$\Wp = 58$ and $115$",
     "L1 prints 115 for the b=5 interval pair weight instead of 114"),

    ("min-end-dropped", "L6-perimeter-gradings.tex",
     "$1, 6, 22, 68, 187, 470, 1106$", None,
     "L6 loses the line printing the stabilised king min-end constants"),

    ("min-end-typo", "L6-perimeter-gradings.tex",
     "$1, 6, 22, 68, 187, 470, 1106$", "$1, 6, 22, 68, 187, 470, 1006$",
     "L6 prints 1006 for the seventh min-end constant instead of 1106"),

    ("crude-bound-typo", "L3-lambda-bounds.tex",
     "5^5/4^4", "5^5/4^5",
     "L3 prints the crude bound with the wrong exponent"),

    ("upper-certificate-typo", "L3-lambda-bounds.tex",
     "9.4117", "9.4118",
     "L3 prints an upper certificate that its own rational does not round to"),

    ("polyomino-bound-dropped", "L3-lambda-bounds.tex",
     r"$\lambda_{\text{polyomino}} \le 4$", None,
     "L3 loses the statement of the false polyomino bound it exists to correct"),

    ("king-quadratic-typo", "L1-diagonal-law.tex",
     r"\tfrac{625}{2}n^2-\tfrac{2459}{2}n+567",
     r"\tfrac{625}{2}n^2-\tfrac{2459}{2}n+568",
     "L1 prints 568 for P_2's constant term instead of 567"),

    # Positive controls on the harness itself: these corrupt a value the
    # verifier recomputes, so they MUST be caught. If one of these is missed
    # the harness is broken, not the verifier.
    ("HARNESS-ladder-row", "L3-lambda-bounds.tex",
     "6.543", "6.544",
     "harness control: L3's top rung, recomputed and compared"),
]


def load_verifier():
    """Import verify_l_papers.py fresh, so module globals start clean."""
    spec = importlib.util.spec_from_file_location("vlp_%d" % load_verifier.n, VERIFIER)
    load_verifier.n += 1
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


load_verifier.n = 0


def run_against(paper_dir):
    """Run the verifier with PAPER pointed at paper_dir. Returns its failures."""
    vlp = load_verifier()
    vlp.PAPER = Path(paper_dir)
    vlp.failures = []
    vlp.checks = 0
    vlp.reds = 0
    out = []
    real_print = print
    try:
        vlp.print = lambda *a, **k: out.append(" ".join(str(x) for x in a))
    except Exception:
        pass
    vlp.main()
    return list(vlp.failures), vlp.checks


def apply_mutation(paper_dir, name, old, new):
    """Apply one mutation to the copy in paper_dir. Returns False if `old` is absent."""
    p = Path(paper_dir) / name
    text = p.read_text()
    if old not in text:
        return False
    if new is None:
        kept = [ln for ln in text.splitlines(keepends=True) if old not in ln]
        if len(kept) == len(text.splitlines(keepends=True)):
            return False
        p.write_text("".join(kept))
    else:
        p.write_text(text.replace(old, new))
    return True


def main():
    verbose = "-v" in sys.argv
    if not VERIFIER.exists():
        print(f"gate_l_paper_verifier: {VERIFIER} not found")
        return 1

    with tempfile.TemporaryDirectory() as td:
        clean = Path(td) / "clean"
        clean.mkdir()
        for n in L_PAPERS:
            shutil.copy2(PAPER / n, clean / n)

        base_failures, base_checks = run_against(clean)
        if base_failures:
            print("gate_l_paper_verifier: the UNMUTATED papers already fail; "
                  "fix that before trusting this gate")
            for f in base_failures:
                print("  " + f)
            return 1
        print(f"  baseline    {base_checks} checks, 0 failures")

        undetected = []
        for mid, paper, old, new, why in MUTATIONS:
            work = Path(td) / mid
            shutil.copytree(clean, work)
            if not apply_mutation(work, paper, old, new):
                print(f"  STALE       {mid}: {old!r} not found in {paper}")
                undetected.append((mid, why, "mutation target missing"))
                continue

            failures, _ = run_against(work)
            if failures:
                if verbose:
                    print(f"  detected    {mid}\n                -> {failures[0][:88]}")
                else:
                    print(f"  detected    {mid}")
            else:
                print(f"  UNDETECTED  {mid}")
                undetected.append((mid, why, "verifier stayed green"))

    print()
    if undetected:
        print(f"gate_l_paper_verifier: {len(undetected)} of {len(MUTATIONS)} "
              f"mutations NOT detected\n")
        for mid, why, how in undetected:
            print(f"  MISS  {mid}: {how}")
            print(f"        {why}")
        print("\nA check that cannot fail is not a check.")
        return 1

    print(f"gate_l_paper_verifier: all {len(MUTATIONS)} mutations detected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
