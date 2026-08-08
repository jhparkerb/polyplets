#!/usr/bin/env python3
"""Apply phase 1 of the L-trim campaign — the section-level cuts.

Mechanical and fail-closed.  Every edit asserts on the text it expects to find
before it changes anything, and a single failed assertion aborts the whole run
with no file written: the papers are read into memory, transformed, checked,
and only then written back.  Deletions within a file are applied bottom-up so
that earlier line numbers stay valid.

The anchors are `phase-1-cuts.md`'s, confirmed by `phase-1-defense.md` and
again by the adjudicator.  The rulings are `phase-1-verdict.md`'s.  Run from
the repo root:

    python3 docs/reviews/l-trim/apply-phase-1.py

`paper/verify_l_papers.py` is deliberately NOT touched — see the verdict, §3 of
"Applier residues".  It is frozen by the commit gate.
"""

import sys
from pathlib import Path

PAPER = Path(__file__).resolve().parents[3] / "paper"

# (file, first_line, last_line, expected_first_line_text, proposal_id)
# Line numbers are 1-based and inclusive.  Each range opens on its sectioning
# command and closes on the blank line before the next one.
DELETIONS = [
    ("L1-diagonal-law.tex",        177, 190, r"\subsection{How to read the rest}",              "P1.L1.1"),
    ("L2-ternary-spine.tex",       142, 178, r"\subsection{What is proved}",                    "P1.L2.1"),
    ("L3-lambda-bounds.tex",       158, 175, r"\subsection{Two things this paper also reports}", "P1.L3.1"),
    ("L4-not-dfinite.tex",         162, 186, r"\subsection{What is gained, and what is given up}", "P1.L4.1"),
    ("L4-not-dfinite.tex",         425, 432, r"\subsection{The growth rate, for calibration}",  "P1.L4.2"),
    ("L4-not-dfinite.tex",         568, 577, r"\subsection{One resonance, unexplored}",         "P1.L4.3"),
    ("L5-convex-king-animals.tex", 154, 183, r"\subsection{What is proved, and what is measured}", "P1.L5.1"),
    ("L5-convex-king-animals.tex", 690, 702, r"\subsection{The reading}",                       "P1.L5.2"),
    ("L6-perimeter-gradings.tex",  618, 642, r"\section{Status of these claims}",               "P1.L6.1"),
]

# The salvage for P1.L2.1: the only sentence in L2 crediting the spine cubic to
# the companion paper is inside the cut range.  Adjudicator's text, not the
# defender's draft — the draft dropped L1 Theorem B's w != 0 hypothesis, used
# \Wp (defined in L1 alone), and \ref'd a label in another document.
SALVAGE_AFTER = "statements about two power series."
SALVAGE = r"""The spine cubic below is theirs too: the companion paper's universal spine
theorem gives the same curve for every prime $p$ dividing the base, provided
the pair weight is nonzero modulo $p$, after rescaling $t$ by that weight.
Here $p = 3$ and $25 \equiv 1 \pmod 3$, so no rescaling is visible."""

# (file, old, new, why) — exact, unique, single-occurrence replacements.
REPLACEMENTS = [
    ("L4-not-dfinite.tex",
     "lightness claim in the introduction",
     "lightness claim in the abstract",
     "P1.L4.1 removes the introduction's lightness claim; the abstract keeps it"),
    ("L6-perimeter-gradings.tex",
     r"\subsection{Novelty}",
     r"\section{Novelty}",
     "P1.L6.1 removes Novelty's parent section; unpromoted it re-parents to k6"),
]

failures: list[str] = []
texts: dict[str, list[str]] = {}


def load(name: str) -> list[str]:
    if name not in texts:
        texts[name] = (PAPER / name).read_text().splitlines(keepends=True)
    return texts[name]


def check(cond: bool, msg: str) -> bool:
    if not cond:
        failures.append(msg)
    return cond


# --- deletions, bottom-up per file -----------------------------------------
for name, a, b, expect, pid in sorted(DELETIONS, key=lambda d: (d[0], -d[1])):
    lines = load(name)
    if not check(b <= len(lines), f"{pid}: {name} has {len(lines)} lines, range ends at {b}"):
        continue
    first = lines[a - 1].rstrip("\n")
    if not check(first == expect, f"{pid}: {name}:{a} is {first!r}, expected {expect!r}"):
        continue
    if not check(lines[b - 1].strip() == "", f"{pid}: {name}:{b} is not the expected blank line"):
        continue
    if not check(a >= 2 and lines[a - 2].strip() == "",
                 f"{pid}: {name}:{a-1} is not blank; deleting would join two paragraphs"):
        continue
    nxt = lines[b].lstrip()
    if not check(nxt.startswith("\\section") or nxt.startswith("\\subsection"),
                 f"{pid}: {name}:{b+1} is {nxt[:40]!r}, not a sectioning command"):
        continue
    del lines[a - 1:b]
    print(f"  cut  {pid:9s} {name:28s} lines {a}-{b}  ({b - a + 1} lines)")

# --- salvage ---------------------------------------------------------------
lines = load("L2-ternary-spine.tex")
hits = [i for i, ln in enumerate(lines) if ln.rstrip("\n").endswith(SALVAGE_AFTER)]
if check(len(hits) == 1, f"salvage: {len(hits)} insertion points match {SALVAGE_AFTER!r}, need exactly 1"):
    i = hits[0]
    check(lines[i + 1].strip() == "", "salvage: insertion point is not the end of its paragraph")
    lines.insert(i + 1, SALVAGE + "\n")
    print(f"  add  P1.L2.1   L2-ternary-spine.tex         salvage after line {i + 1} (4 lines)")

# --- replacements ----------------------------------------------------------
for name, old, new, why in REPLACEMENTS:
    lines = load(name)
    n = sum(ln.count(old) for ln in lines)
    if not check(n == 1, f"replacement in {name}: {old!r} occurs {n} times, need exactly 1"):
        continue
    for i, ln in enumerate(lines):
        if old in ln:
            lines[i] = ln.replace(old, new)
            print(f"  fix  {name:28s} line {i + 1}: {why}")
            break

# --- commit to disk, or nothing --------------------------------------------
if failures:
    print("\napply-phase-1: ABORTED, no file written")
    for f in failures:
        print(f"  FAIL  {f}")
    sys.exit(1)

for name, lines in texts.items():
    (PAPER / name).write_text("".join(lines))
print(f"\napply-phase-1: wrote {len(texts)} files")
