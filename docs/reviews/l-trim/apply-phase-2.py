#!/usr/bin/env python3
"""Apply phase 2 of the L-trim campaign — the result-level cuts.

Mechanical and fail-closed, on the `apply-phase-1.py` model, with one change
mandated by the verdict's ledger corrections: every edit is CONTENT-ADDRESSED.
The verbatim text is the authority; the line numbers in the ledgers are
advisory only (two residue anchors there are off by one line).  Every site is
asserted to occur exactly once before anything is changed, and a single failed
assertion aborts the whole run with no file written.

The rulings are `phase-2-verdict.md`'s — the verdict, not the cuts file, is
the authority on what text ships.  Its four ledger corrections are all
implemented here:

  1. content-addressed matching everywhere (this file has no line numbers);
  2. P2.L5.2 ships the defender's text, with "to arbitrary precision";
  3. every pure removal takes exactly one adjacent blank line, so the
     phase-1 one-separator invariant is kept (in-place demotions replace the
     environment between its two blanks and touch neither);
  4. the two adopted stylistic alternates ship — L2's "unchecked against the
     OEIS ... or anywhere else" residue, and L5's parenthetical entry into
     the related-work paragraph.

Run from anywhere:

    python3 docs/reviews/l-trim/apply-phase-2.py          # apply
    python3 docs/reviews/l-trim/apply-phase-2.py --check  # assert only, write nothing

`paper/verify_l_papers.py` is frozen and is not touched.
"""

import sys
from pathlib import Path

PAPER = Path(__file__).resolve().parents[3] / "paper"

L1 = "L1-diagonal-law.tex"
L2 = "L2-ternary-spine.tex"
L3 = "L3-lambda-bounds.tex"
L5 = "L5-convex-king-animals.tex"
L6 = "L6-perimeter-gradings.tex"

# --- the twelve rulings, as verbatim blocks --------------------------------
#
# REMOVALS: (pid, file, block).  The block must occur exactly once, sit
# between two blank lines, and is removed together with ONE adjacent blank.
#
# DEMOTIONS: (pid, file, block, replacement).  In-place: the environment's
# text is replaced, the surrounding blanks are untouched.
#
# RESIDUES: (pid, file, old, new).  Exact, unique, content-addressed.

REMOVALS = [
    ("P2.L1.2", L1, r"""\begin{theorem}[degree and leading coefficient]
\label{thm:D}
$\deg q_k = k$ exactly, and the coefficient of $n^k$ in $P_k$ is $\Wp^{\,k}/k!$.
In particular $[n^1]P_1 = \Wp$.
\end{theorem}
"""),
    ("P2.L1.3", L1, r"""\begin{openproblem}[onset sharpness in general]
Theorem~\ref{thm:A} proves validity from $n = 2k+1$. Prove that the formula fails
at $n = 2k$ for every $k$ --- equivalently, that $\deg D = k$ exactly, with no
cancellation. Verified on all banked king data through $k \le 17$ and proved ab
initio from the weight table for $k \le 5$. The obvious route, a rational
generating function for the top coefficient of $R_k$, is blocked: the all-pairs
weight family is not C-finite.
\end{openproblem}
"""),
    ("P2.L2.2", L2, r"""\begin{remark}[why one per three]
The $\lceil\cdot/3\rceil$ is the activation slope $3/2$ against the diagonal, and
it is the same $/3$ that appears elsewhere in this triangle's structure --- the
columns factor as products of three consecutive atoms, and the $3$-adic content
of the law itself runs $3^{n-1}$ on the diagonal and $3^{3k+1}$ across it. The
SNF count, the atom factorisation and the $3$-adic exponents are not three
phenomena. They are one, and it is the cubic.
\end{remark}
"""),
    ("P2.L2.3", L2, r"""\begin{openproblem}[is $H$ known?]
$H = 1, 25, 208, 1483, 20688, 130208, \dots$ is the per-row transfer series of
the defect gas. It is a candidate new integer sequence and we have not checked
it against the OEIS~\cite{oeis} or anywhere else (\S\ref{sec:novelty}).
\end{openproblem}
"""),
    ("P2.L3.1", L3, r"""\begin{proposition}[existence, and terms are floors]
\label{prop:fekete}
$a(m)a(n) \le a(m+n)$; hence $\lambda$ exists, and $a(n) \le \lambda^n$ for all
$n$.
\end{proposition}
"""),
    ("P2.L3.2", L3, r"""\begin{openproblem}[the missing concatenation lemma]
Find a connected split of a lattice animal into two pieces with sizes prescribed
to within $O(1)$ and with $\mathrm{poly}(n)$ reassembly information. This would
give $\lambda \le 7.745$ here and improve the polyomino record; the second
consequence is why it should be expected to be hard.
\end{openproblem}
"""),
    ("P2.L5.1", L5, r"""\begin{remark}[the square-lattice analogue is classical]
Convex polyominoes by area grow at $2.30914\dots$~\cite{bender1974} and the
parallelogram subclass \oeis{A006958} has the same constant --- measured here at
$2.309138593330495$, flat from $n = 100$ to $n = 400$. So
Proposition~\ref{prop:squeeze}'s conclusion could have been read off the solved
models one lattice over. What the proposition adds is the king case, where
neither class is solved, and the statement for \emph{every} intermediate class
rather than for two particular ones.
\end{remark}
"""),
    ("P2.L5.3", L5, r"""\begin{openproblem}[the arithmetic of $\mu$]
Is $\mu$ irrational? Transcendental? \S\ref{sec:exclusions} excludes boxes and
nothing more.
\end{openproblem}
"""),
    ("P2.L6.1", L6, r"""\begin{openproblem}[the higher tips]
The tip family is $\phi_1, \phi_2$ for corner indices $1, 2$, and $\phi_3$ is
\emph{not} the answer at index $3$ (\S\ref{sec:tips}). What is?
\end{openproblem}
"""),
]

DEMOTIONS = [
    # P2.L1.1 — the finiteness lemma goes; the defender's salvage sentence
    # stands where it stood (verdict: the cutter's "clearest case" rested on a
    # false claim; prop:chain's sums need this stated).
    ("P2.L1.1", L1, r"""\begin{lemma}[finiteness]
\label{lem:finite}
Every weight above is finite, and for each $k$ there are finitely many cluster
types of surplus $k$ --- exactly the $2^{k-1}$ compositions of $k$ into parts
$\ge 1$, one part per row.
\end{lemma}

\begin{proof}
A connected set of $c$ cells has $x$-spread at most $(c-1)\max|dx|$, which is
finite by (R) and (U); so a cluster of bounded surplus, together with its two
contact cells, ranges over a finite set of configurations once we quotient by
$x$-translation. The type count is the composition count, and $\ell_c \le k_c$ by
\eqref{eq:elllek}.
\end{proof}
""",
     r"""All four weight families are finite, and each surplus admits only finitely
many cluster types: by (R) and (U) a connected set of cells has bounded
$x$-spread, so clusters of bounded surplus range over finitely many
configurations once $x$-translation is quotiented out. The sums in
Proposition~\ref{prop:chain} are therefore formal power series.
"""),
    # P2.L2.1 — the automaton remark demoted to one sentence; both citations
    # (christol1980, allouche2003 — sole occurrences in L2) are carried.
    ("P2.L2.1", L2, r"""\begin{remark}[the automaton]
$W$ is algebraic over $\F_3(t)$, so by Christol's
theorem~\cite{christol1980} --- a power series over $\F_p$ is algebraic exactly
when its coefficient sequence is $p$-automatic --- the array is
$3$-automatic~\cite{allouche2003}. Theorem~\ref{thm:digit} is that automaton made
explicit for the two-dimensional array: to read $T(n,H) \bmod 3$, expand $n$ in
base $3$ and multiply one factor per digit. Nothing about the animals is
consulted.
\end{remark}
""",
     r"""$W$ is algebraic over $\F_3(t)$, so by Christol's
theorem~\cite{christol1980} the array is $3$-automatic~\cite{allouche2003},
and Theorem~\ref{thm:digit} is its automaton written out for the
two-dimensional case.
"""),
    # P2.L5.2 — the shooting corollary demoted to prose.  The DEFENDER's text
    # ships (verdict correction 2): "to arbitrary precision" is the scope of
    # the claim and stays.
    ("P2.L5.2", L5, r"""\begin{corollary}[$\mu$ by shooting]
\label{cor:shoot}
Shooting on that recurrence computes $\mu$ to arbitrary precision in
$O(h_{\max})$ operations, with no series and no extrapolation. It reproduces all
$199$ banked digits and continues past them, and reaches \textbf{$987$ digits in
$1.6$ seconds} on one core --- against a $700$-term enumeration plus
extrapolation for $200$.
\end{corollary}
""",
     r"""Shooting on that recurrence computes $\mu$ to arbitrary precision in
$O(h_{\max})$ operations, with no series and no extrapolation: it reproduces
all $199$ banked digits, continues past them, and reaches $987$ digits in
$1.6$ seconds on one core, against a $700$-term enumeration plus extrapolation
for $200$.
"""),
]

RESIDUES = [
    # P2.L1.2: thm:D's two \ref sites; either one missed is a dangling \ref.
    ("P2.L1.2", L1,
     "since by Theorem~\\ref{thm:D} the leading one is",
     "since by Corollary~\\ref{cor:lead} the leading one is"),
    ("P2.L1.2", L1,
     "\\begin{corollary}[leading coefficient; Theorem~\\ref{thm:D}]",
     "\\begin{corollary}[leading coefficient]"),
    # P2.L1.2: the forward-pointer paragraph becomes the demoted statement
    # (cutter's replacement text, verdict-approved; "Precisely:" retained —
    # the adjudicator declined the defender's alternative).
    ("P2.L1.2", L1,
     """The proof is a corollary of the grand form and is given in
Section~\\ref{sec:grand} (Corollary~\\ref{cor:lead}); it is written out for the
""",
     """Precisely: $\\deg q_k = k$ exactly, the coefficient of $n^k$ in $P_k$ is
$\\Wp^{\\,k}/k!$, and in particular $[n^1]P_1 = \\Wp$. That is
Corollary~\\ref{cor:lead}, proved in Section~\\ref{sec:grand} once the grand
form is available; it is written out for the
"""),
    # P2.L1.3: the back-reference at the onset-sharpness paragraph.  "We
    # record" ends its line (the ledger's 503 was off by one); the span is
    # matched across the wrap, not by line number.
    ("P2.L1.3", L1,
     """We record
onset sharpness as an open problem (Section~\\ref{sec:open}) and note that
""",
     """We record
it as open and note that
"""),
    # P2.L2.3: the residue carries \cite{oeis} (sole occurrence in L2 after
    # the cut) and ships the defender's adopted alternate, without the dash
    # aside.  "Whether" ends its line (the ledger's 214 was off by one).
    ("P2.L2.3", L2,
     """Whether
$H$ itself is a known sequence is one of the things the missing novelty sweep
would settle.
""",
     """Whether
$H$ itself is a known sequence, unchecked against the OEIS~\\cite{oeis} or
anywhere else, is one of the things the missing novelty sweep would settle.
"""),
    # P2.L3.1: "This" loses its antecedent; the sentence goes.
    ("P2.L3.1", L3,
     "This is Fekete's lemma on $\\log a$. The ladder --- supermultiplicativity, the",
     "The ladder --- supermultiplicativity, the"),
    # P2.L5.1: the measurement enters the related-work paragraph in
    # parentheses (defender's adopted alternate, not a second dash aside).
    ("P2.L5.1", L5,
     "sharing it, mean that",
     """sharing it (measured here at $2.309138593330495$, flat from $n = 100$ to
$n = 400$), mean that"""),
]

# --- post-transform guards -------------------------------------------------
# (file, substring, why) — each must still occur at least once after every
# edit.  These mirror the gate's pinned constants and the citation keys this
# phase is at risk of silently losing.
MUST_SURVIVE = [
    (L1, "\\Wp = 58", "gate check 6: single-occurrence constant, in rem:notsquares"),
    (L1, "\\Wp = 57", "gate check 6 constant"),
    (L2, "1, 25, 208, 1483, 20688, 130208", "gate check 6: H series (2 -> 1 occurrence is permitted, 0 is not)"),
    (L2, "\\cite{christol1980}", "gate check 7: sole citation, carried by P2.L2.1's replacement"),
    (L2, "\\cite{allouche2003}", "gate check 7: sole citation, carried by P2.L2.1's replacement"),
    (L2, "\\cite{oeis}", "gate check 7: sole citation, carried by P2.L2.3's residue"),
    (L3, "6.543", "gate check 6 constant"),
    (L3, "9.3154", "gate check 6 constant"),
    (L5, "3.12340450886853853211", "gate check 6: single-occurrence constant, in cor:floor"),
    (L5, "\\cite{bender1974}", "attribution, still present outside the removed remark"),
    (L6, "1, 6, 22, 68, 187, 470, 1106", "gate check 6 constant"),
]

# (file, substring, why) — each must occur exactly zero times after every
# edit: labels whose environments this phase removes, with zero references
# tree-wide per the defense's collateral checks.
MUST_VANISH = [
    (L1, "lem:finite", "P2.L1.1: label had zero references"),
    (L1, "thm:D", "P2.L1.2: both \\ref sites are residue-edited"),
    (L3, "prop:fekete", "P2.L3.1: label had zero references"),
    (L5, "cor:shoot", "P2.L5.2: label had zero references"),
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
    # single separator (verdict correction 3).
    texts[name] = text[:i] + text[j + 1:]
    print(f"  cut  {pid:9s} {name:28s} {block.count(chr(10))} lines removed (+1 blank)")

# --- demotions: in-place replacement between untouched blanks --------------
for pid, name, block, replacement in DEMOTIONS:
    i = unique_site(pid, name, block)
    if i < 0:
        continue
    text = texts[name]
    if not check(text[i - 2:i] == "\n\n" if i >= 2 else False,
                 f"{pid}: {name}: environment is not preceded by a blank line"):
        continue
    if not check(text[i + len(block):i + len(block) + 1] == "\n",
                 f"{pid}: {name}: environment is not followed by a blank line"):
        continue
    texts[name] = text[:i] + replacement + text[i + len(block):]
    print(f"  demote {pid:7s} {name:28s} {block.count(chr(10))} -> {replacement.count(chr(10))} lines")

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
    print("\napply-phase-2: ABORTED, no file written")
    for f in failures:
        print(f"  FAIL  {f}")
    sys.exit(1)

if "--check" in sys.argv[1:]:
    print("\napply-phase-2: --check passed, no file written")
    sys.exit(0)

for name, text in texts.items():
    (PAPER / name).write_text(text)
print(f"\napply-phase-2: wrote {len(texts)} files")
