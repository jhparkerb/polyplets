#!/usr/bin/env python3
"""Apply phase 3 of the L-trim campaign — the paragraph-level cuts.

Mechanical and fail-closed, on the `apply-phase-2.py` model: every edit is
CONTENT-ADDRESSED.  The verbatim text below is taken from the tree itself, not
pasted from the ledgers — the verdict's correction 8 records that P3.L6.1's
excerpt in `phase-3-cuts.md` is re-wrapped relative to the manuscript and would
never match.  Every site is asserted to occur exactly once before anything is
changed, and a single failed assertion aborts the whole run with no file
written.

The rulings are `phase-3-verdict.md`'s — the verdict, not the cuts file, is the
authority on what text ships.  Sixteen removals, of which three carry a
residue:

  P3.L2.3  the removed paragraph is replaced in place by the load-bearing
           hedge "These three are measured, not proved." (the sole hedge on
           section lift's three congruences — the Ldisclosure ledger does not
           cover that section);
  P3.L5.1  the Definition's parenthetical gains the skew-shape synonym;
  P3.L6.1  "the height grading" at its first surviving occurrence becomes
           "a companion paper's height grading", so the first open problem's
           "has a proof" claim keeps a locatable referent.

Pure removals take the block and exactly ONE adjacent blank line (the phase-1
one-separator invariant); the in-place replacement touches neither of its
blanks.

Run from anywhere:

    python3 docs/reviews/l-trim/apply-phase-3.py          # apply
    python3 docs/reviews/l-trim/apply-phase-3.py --check  # assert only, write nothing

`paper/verify_l_papers.py` is frozen and is not touched.
"""

import sys
from pathlib import Path

PAPER = Path(__file__).resolve().parents[3] / "paper"

L1 = "L1-diagonal-law.tex"
L2 = "L2-ternary-spine.tex"
L3 = "L3-lambda-bounds.tex"
L4 = "L4-not-dfinite.tex"
L5 = "L5-convex-king-animals.tex"
L6 = "L6-perimeter-gradings.tex"

# --- the sixteen rulings, as verbatim blocks -------------------------------
#
# REMOVALS: (pid, file, block).  The block must occur exactly once, sit
# between two blank lines, and is removed together with ONE adjacent blank.
#
# REPLACEMENTS: (pid, file, block, replacement).  In-place: the paragraph's
# text is replaced, the surrounding blanks are untouched.
#
# RESIDUES: (pid, file, old, new).  Exact, unique, content-addressed.

REMOVALS = [
    ("P3.L1.1", L1, r"""Three things about that statement are worth flagging before the proof.

\paragraph{The onset is proved, not fitted.} $H \ge k+1$ --- equivalently
$n \ge 2k+1$ in the other coordinate --- comes out of the argument, as exactly
the reach of a correction polynomial whose degree is bounded by a triviality
about cluster rows. It is not read off data and then hoped for. This is what
makes the law useful as a \emph{tool}: because the degree is $\le k$ and the
onset is $\ge k+1$, any $k+1$ enumerated in-onset values determine $q_k$
outright, and every further value is a theorem rather than a test.

\paragraph{The class, not the lattice, is the object.} The proof never uses
$b=3$, or symmetry of the step set, or any arithmetic particular to a lattice.
The square lattice is the degenerate case $b=1$; polyhexes are $b=2$; king
animals are $b=3$. Getting all three from one argument is not economy for its own
sake --- it is what makes the mod-$p$ result of Section~\ref{sec:spine} possible,
since there the lattice's only contributions are a prime and a scalar.

\paragraph{Where it stops is informative.} Polyiamonds are not in the class, and
for a reason that is easy to state: a triangular cell's three neighbours depend
on whether the triangle points up or down, so the adjacency is not
translation-invariant and there is no single step set to count. The law
nevertheless appears to hold with a period-2 correction. We report that as data
(Section~\ref{sec:polyiamond}) and do not dress it as a theorem.
"""),
    ("P3.L1.2", L1, r"""Coefficients are rational rather than integral, which is the shape
Remark~\ref{rem:newton} predicts: $k!\,P_k \in \Z[n]$, and
$\tfrac{32}{3}\cdot 3! = 64$.
"""),
    ("P3.L1.3", L1, r"""Two things are worth noting beyond the corollary itself. The onset in the
conjecture, ``$n \ge 5$'', was presumably read off data; Theorem~\ref{thm:A}
gives $2k+1$ for every $k$, proved, which is where the next diagonals of that
entry come from --- rows 3 and 4 of Table~\ref{tab:machine}.
"""),
    ("P3.L2.1", L2, r"""A pattern like that is either a coincidence of small numbers or a shadow of
something. It is the second, and the something is a cubic.
"""),
    ("P3.L2.2", L2, r"""So the conditionality of this paper is: the diagonal law and the grand form
(theorems), and the gas-derived master equation. No finitely-verified
coefficient identity remains as an input.
"""),
    ("P3.L3.1", L3, r"""The point of insisting on this is that a power iteration is not a proof. Re-run a
bisection over a power iteration on another machine and one gets a different set
of last digits, with no artifact anyone can audit. A certificate replaces the
whole chain with a finite object and a finite integer computation, and anyone can
re-run the second part.
"""),
    ("P3.L3.2", L3, r"""Before the method that worked, the method that did not, since the reason is
instructive.
"""),
    ("P3.L3.3", L3, r"""The certified $6.543$ supersedes both of Bacher's lower bounds, and it is worth
being precise about the sense in which it does: the multi-directed $6.4752$ is a
numerical value, and $6.543$ is the first value we know of to beat it with a
certificate.
"""),
    ("P3.L4.1", L4, r"""Ours tracks \emph{one} distinguished pole per slice --- the singularity
$x = 1/\mu_H$ at the radius of convergence --- and asks about its degree over
$\Q$. If the lower slices are all regular there, the recurrence forces the
leading coefficient to vanish at $1/\mu_H$; but a nonzero rational polynomial of
degree $\le D$ cannot vanish at an algebraic number of degree $> D$. So a
D-finite $F$ caps $[\Q(\mu_H):\Q]$ at all but finitely many heights. Northcott
says that cap is impossible, because the $\mu_H$ are infinitely many distinct
algebraic integers of bounded house.
"""),
    ("P3.L4.2", L4, r"""By contrast, \cite{bmr2002}'s route needs an explicit combinatorial description
of the denominators --- cyclotomic factors from $k$-sections, in their case --- to
be redone for each new family. That difference is the actual content of the
lightness claim in the abstract, and it is why we think the transport
statement is the more useful half of this paper.
"""),
    ("P3.L4.3", L4, r"""A side effect is worth recording: irreducibility together with positivity of the
dominant root means, by Galois conjugation, that \emph{every} root of the atom is
active in $T(n,H)$. So the minimality ingredient that an earlier root-separation
argument needed is not needed at these levels.
"""),
    ("P3.L5.1", L5, r"""A by-product: \oeis{A225114}, the staircase king animals (equivalently skew
shapes with no empty row or column), has growth constant $\mu$ too, measured
here to $204$ digits. That entry carries no asymptotic.
"""),
    ("P3.L5.2", L5, r"""This is the capacity artifact in its natural habitat. A degree-$3$ relation of
height $\sim3\times10^4$ can absorb about $4\log_{10}(3.4\times10^4) \approx 18$
digits of input, so \emph{any} $16$-to-$18$-digit decimal admits such a cubic.
The number of digits fed to an integer-relation search is the whole ballgame,
and anyone with a $16$-digit $\mu$ and a cubic solver will find this polynomial.
It means nothing.
"""),
    # NOTE: this block is anchored to the TREE's line-wrapping, which differs
    # from the re-wrapped excerpt in phase-3-cuts.md (verdict correction 8).
    ("P3.L6.1", L6, r"""\paragraph{What the two ends give.} At the maximum end, quasi-polynomials with a
triangular onset law and an unexpected amount of lattice-independence. At the
minimum end, eventually constant classes with a \emph{linear} onset law, and
lattice-independence failing at the first nontrivial term. Neither end dominates
the other, and the honest summary is that the perimeter grading is more
universal in \emph{content} at the max end while the height grading --- the
subject of a companion paper --- is cleaner in \emph{form}, being a proved plain
polynomial with a proved sharp onset.
"""),
    ("P3.L6.2", L6, r"""So the two lattices agree at the maximum end on period, degree, onset and
leading coefficient, and disagree at the minimum end from the very first
nontrivial constant: $1, 4, 14, 40, 105$ on king against $1, 4, 18, 60, 187$ on
square.
"""),
]

REPLACEMENTS = [
    # P3.L2.3 — the justification half goes; the hedge is the only thing
    # separating \S lift's three displayed congruences from the paper's proved
    # results (the \Ldisclosure ledger does not cover \S lift), so it ships as
    # its own paragraph, in place, between untouched blanks.
    ("P3.L2.3", L2, r"""These three are measured, not proved. They are stated because the pattern ---
one series governing every level --- is what an eventual Witt-vector treatment
would have to explain, and because the deficit-$d$ open problem above is
presumably the same question asked one level at a time.
""",
     r"""These three are measured, not proved.
"""),
]

RESIDUES = [
    # P3.L5.1 — the skew-shape synonym survives at the place the object is
    # defined.  The tab:fourrungs occurrence lacks the "OEIS" prefix, so this
    # anchor is unique.
    ("P3.L5.1", L5,
     r"(OEIS \oeis{A225114}).",
     r"(OEIS \oeis{A225114}, the skew shapes with no empty row or column)."),
    # P3.L6.1 — the defender's required residue: after the cut, "companion"
    # occurs nowhere in L6 and the first open problem's "The height grading
    # has a proof" would have no locatable referent.  Three words at the first
    # surviving occurrence repair it.
    ("P3.L6.1", L6,
     "on the model of the height grading",
     "on the model of a companion paper's height grading"),
]

# --- post-transform guards -------------------------------------------------
# (file, substring, why) — each must still occur at least once after every
# edit.  These mirror scripts/l_trim_gate.sh's CONSTANTS list (check 6), the
# at-risk citation keys (check 7), and the three residue texts the verdict
# says must ship.
MUST_SURVIVE = [
    # gate check 6, the full CONSTANTS list:
    (L1, r"\Wp = 58", "gate check 6: single-occurrence constant, rem:notsquares"),
    (L1, r"\Wp = 57", "gate check 6 constant"),
    (L2, "1, 25, 208, 1483, 20688, 130208", "gate check 6: H series, single occurrence"),
    (L3, "6.543", "gate check 6 constant (14 -> 12 occurrences; the verifier's two untouched)"),
    (L3, "9.3154", "gate check 6 constant"),
    (L4, "1, 2, 4, 9, 29, 68, 181, 462, 1254, 3289", "gate check 6: psi-degree list, single occurrence"),
    (L5, "3.12340450886853853211", "gate check 6: single-occurrence constant, cor:floor"),
    (L6, "1, 6, 22, 68, 187, 470, 1106", "gate check 6 constant"),
    # gate check 7, keys at risk near this phase's ranges:
    (L4, r"\cite{bmr2002}", "gate check 7: P3.L4.2 removes one of nine occurrences"),
    (L3, r"\cite{bacher2015}", "gate check 7: named in P3.L3.3's argument but not in its excerpt"),
    (L2, r"\cite{christol1980}", "gate check 7: sole citation in L2, phase-2 residue, untouched"),
    (L2, r"\cite{allouche2003}", "gate check 7: sole citation in L2, phase-2 residue, untouched"),
    (L2, r"\cite{oeis}", "gate check 7: sole citation in L2, phase-2 residue, untouched"),
    # the verdict's residue texts:
    (L2, "These three are measured, not proved.", "P3.L2.3 residue: the sole hedge on \\S lift"),
    (L5, "the skew shapes with no empty row or column", "P3.L5.1 residue at the Definition"),
    (L6, "a companion paper's height grading", "P3.L6.1 residue: the proof's locatable referent"),
    # labels whose only in-range \refs were outbound (nothing may dangle):
    (L1, r"\label{sec:spine}", "P3.L1.1 removes an outbound ref; two refs survive"),
    (L1, r"\label{sec:polyiamond}", "P3.L1.1 removes an outbound ref; three refs survive"),
    (L2, r"\label{sec:lift}", "P3.L2.3's section keeps both inbound refs"),
]

# (file, substring, why) — each must occur exactly zero times after every
# edit.
MUST_VANISH = [
    (L1, r"\ref{rem:newton}", "P3.L1.2 removes the paper's only ref; the label stays (phase-5 sweep)"),
    (L6, "on the model of the height grading", "P3.L6.1 residue rewrites this phrase"),
    (L5, "That entry carries no asymptotic", "P3.L5.1: the one conceded outright loss"),
]

failures: list[str] = []
texts: dict[str, str] = {}
orig_words: dict[str, int] = {}


def load(name: str) -> str:
    if name not in texts:
        texts[name] = (PAPER / name).read_text()
        orig_words[name] = len(texts[name].split())
    return texts[name]


def check(cond: bool, msg: str) -> bool:
    if not cond:
        failures.append(msg)
    return cond


def unique_site(pid: str, name: str, needle: str) -> int:
    """Assert `needle` occurs exactly once in `name`; return its offset or -1."""
    text = load(name)
    n = text.count(needle)
    if not check(n == 1, f"{pid}: {name}: expected text occurs {n} times, need exactly 1: "
                         f"{needle.splitlines()[0][:60]!r}..."):
        return -1
    return text.index(needle)


# --- removals: block + exactly one adjacent blank line ---------------------
for pid, name, block in REMOVALS:
    i = unique_site(pid, name, block)
    if i < 0:
        continue
    text = texts[name]
    if not check(text[i - 2:i] == "\n\n" if i >= 2 else False,
                 f"{pid}: {name}: block is not preceded by a blank line"):
        continue
    j = i + len(block)
    if not check(text[j:j + 1] == "\n",
                 f"{pid}: {name}: block is not followed by a blank line"):
        continue
    # Take the block and the blank line AFTER it; the one before remains the
    # single separator (the phase-1/2 one-separator invariant).
    texts[name] = text[:i] + text[j + 1:]
    print(f"  cut  {pid:9s} {name:28s} {block.count(chr(10))} lines removed (+1 blank)")

# --- replacements: in-place, between untouched blanks ----------------------
for pid, name, block, replacement in REPLACEMENTS:
    i = unique_site(pid, name, block)
    if i < 0:
        continue
    text = texts[name]
    if not check(text[i - 2:i] == "\n\n" if i >= 2 else False,
                 f"{pid}: {name}: paragraph is not preceded by a blank line"):
        continue
    if not check(text[i + len(block):i + len(block) + 1] == "\n",
                 f"{pid}: {name}: paragraph is not followed by a blank line"):
        continue
    texts[name] = text[:i] + replacement + text[i + len(block):]
    print(f"  keep {pid:9s} {name:28s} {block.count(chr(10))} -> {replacement.count(chr(10))} lines (hedge retained)")

# --- residues: exact single-occurrence replacements ------------------------
for pid, name, old, new in RESIDUES:
    i = unique_site(pid, name, old)
    if i < 0:
        continue
    texts[name] = texts[name].replace(old, new)
    print(f"  fix  {pid:9s} {name:28s} residue: {old.splitlines()[0][:50]!r}...")

# --- guards ----------------------------------------------------------------
for name, needle, why in MUST_SURVIVE:
    check(needle in load(name), f"guard: {name} no longer contains {needle!r} ({why})")

for name, needle, why in MUST_VANISH:
    n = load(name).count(needle)
    check(n == 0, f"guard: {name} still contains {needle!r} {n}x ({why})")

for name in texts:
    check("\n\n\n" not in texts[name],
          f"guard: {name} has a double blank line; the one-separator invariant is broken")
    delta = len(texts[name].split()) - orig_words[name]
    check(delta <= 0, f"guard: {name} GREW by {delta} words")

# --- report, then commit to disk or nothing --------------------------------
print()
for name in sorted(texts):
    print(f"  words {name:28s} {orig_words[name]:5d} -> {len(texts[name].split()):5d}"
          f"  ({len(texts[name].split()) - orig_words[name]:+d})")

if failures:
    print("\napply-phase-3: ABORTED, no file written")
    for f in failures:
        print(f"  FAIL  {f}")
    sys.exit(1)

if "--check" in sys.argv[1:]:
    print("\napply-phase-3: --check passed, no file written")
    sys.exit(0)

for name, text in texts.items():
    (PAPER / name).write_text(text)
print(f"\napply-phase-3: wrote {len(texts)} files")
