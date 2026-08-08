#!/usr/bin/env python3
"""Apply phase 4 of the L-trim campaign — the sentence-level cuts.

Mechanical and fail-closed, on the `apply-phase-3.py` model, with one change
forced by the grain: a sentence removed from the middle of a paragraph must
splice its surviving neighbours with exactly one space, and a paragraph-final
sentence must leave no trailing whitespace.  So every edit here is a
CONTENT-ADDRESSED REPLACEMENT (old, new): `old` is a verbatim span of the tree
covering the cut sentence PLUS its surviving boundary text on each side, and
`new` is that boundary text alone, spliced.  Both sides of every edit are
asserted — `old` must occur exactly once before, `new` exactly once after — so
the post-edit local text is checked, not just the pre-edit anchor.  A single
failed assertion aborts the whole run with no file written.

The rulings are `phase-4-verdict.md`'s — the verdict, not the cuts file, is
the authority on what text ships.  Twenty-two removals, no residues.  All
twenty-two sit inside a paragraph (start, middle, or end), so no blank-line
seam is created; the one-separator invariant is asserted anyway.

Two edits sit against known tripwires and carry their guard in the edit text
itself:

  P4.L5.3  the splice lands one sentence before L5's SOLE occurrence of
           \\cite{hardyRamanujan1918} (gate check 7); the citation sentence's
           opening is part of both `old` and `new`, pinning the boundary;
  P4.L3.5  the cut paragraph's first sentence holds the pinned 6.543 and
           9.3154 (gate check 6); the edit's `old` begins after it.

Post-transform guards mirror `scripts/l_trim_gate.sh`: all eight pinned
CONSTANTS (check 6), the full per-paper \\cite-key set unchanged (check 7,
computed from the text rather than listed), no \\ref key vanishing, no double
space or trailing space at any splice, no double blank line, and no paper may
grow in words.

Run from anywhere:

    python3 docs/reviews/l-trim/apply-phase-4.py          # apply
    python3 docs/reviews/l-trim/apply-phase-4.py --check  # assert only, write nothing

`paper/verify_l_papers.py` is frozen and is not touched.
"""

import re
import sys
from pathlib import Path

PAPER = Path(__file__).resolve().parents[3] / "paper"

L1 = "L1-diagonal-law.tex"
L2 = "L2-ternary-spine.tex"
L3 = "L3-lambda-bounds.tex"
L4 = "L4-not-dfinite.tex"
L5 = "L5-convex-king-animals.tex"
L6 = "L6-perimeter-gradings.tex"

# --- the twenty-two rulings, as (pid, file, old, new) ----------------------
#
# `old` and `new` are anchored to the TREE's line-wrapping (amendment 3), not
# to the ledger excerpts.  `new` must be strictly shorter than `old` and is
# always the surviving boundary text of `old` with the sentence(s) gone.

EDITS = [
    # -- L1 ------------------------------------------------------------------
    ("P4.L1.1", L1,  # paragraph-final closer
     "and is proved once for all of them. The phenomenon is\n"
     "not unheard of and we do not present it as such.",
     "and is proved once for all of them."),
    ("P4.L1.2", L1,  # paragraph-initial lead-in
     "Corollary~\\ref{cor:two} has a physical reading that is worth one paragraph\n"
     "because it explains the shape rather than merely deriving it. Write\n"
     "$F(n,u) = \\sum_k P_k(n)u^k$ with $P_0 = 1$,",
     "Write\n"
     "$F(n,u) = \\sum_k P_k(n)u^k$ with $P_0 = 1$,"),
    ("P4.L1.3", L1,  # paragraph-initial topic sentence
     "Supplying those values is a small computation, not a large one, and it does not\n"
     "require enumerating animals. A surplus-budgeted row transfer, parametric in the",
     "A surplus-budgeted row transfer, parametric in the"),
    ("P4.L1.4", L1,  # section-final closer
     "extension rather than a result. What the polyiamond case does establish is that\n"
     "hypothesis (U) is doing real work in Theorem~\\ref{thm:A} and is not merely\n"
     "convenient.",
     "extension rather than a result."),
    # -- L2 ------------------------------------------------------------------
    ("P4.L2.1", L2,  # abstract-final closer
     "correction is again $W$. The $3$-adic tower telescopes through one series.",
     "correction is again $W$."),
    ("P4.L2.2", L2,  # paragraph-final emphasis fragment
     "Every invariant factor is a power of $3$. Not mostly; every one, at every\n"
     "$N$ anyone has computed.",
     "Every invariant factor is a power of $3$."),
    ("P4.L2.3", L2,  # epigram half of the one-line bridge
     "That is unconditional and it is the easy half. The count is the content.",
     "That is unconditional and it is the easy half."),
    ("P4.L2.4", L2,  # paragraph-final closer
     "The correction factor in \\eqref{eq:LB} is identically $1$. That accident is what\n"
     "makes the following two computations one line each rather than a page.",
     "The correction factor in \\eqref{eq:LB} is identically $1$."),
    ("P4.L2.5", L2,  # paragraph-final reach claim
     "spine theorems supply the first two cases and Theorem~\\ref{thm:deficit2} the\n"
     "third. The method --- Lagrange--B\\\"urmann onto the master curve, then exact\n"
     "division --- applies to any congruence for a family linear in $(n,k)$, and is\n"
     "the reusable part.",
     "spine theorems supply the first two cases and Theorem~\\ref{thm:deficit2} the\n"
     "third."),
    # -- L3 ------------------------------------------------------------------
    ("P4.L3.1", L3,  # paragraph-initial topic sentence
     "Two features of the table are the honest parts and deserve to be read as such.\n"
     "The certified value is the floor: at $H = 2$",
     "The certified value is the floor: at $H = 2$"),
    ("P4.L3.2", L3,  # maxim before the list
     "A checker that cannot fail is not a checker. Four self-tests run as a gate:",
     "Four self-tests run as a gate:"),
    ("P4.L3.3", L3,  # paragraph-final closer
     "at a wall time indistinguishable from the full-precision run. The cost of the\n"
     "crippling shows up honestly as lost digits and never as a wrong claim.",
     "at a wall time indistinguishable from the full-precision run."),
    ("P4.L3.4", L3,  # paragraph-final self-appraisal
     "count, same minimum ratio to all nine printed digits. That is a cross-validation\n"
     "of the operator by two implementations, which is the strongest statement\n"
     "available short of certifying the operator itself.",
     "count, same minimum ratio to all nine printed digits."),
    ("P4.L3.5", L3,  # mid-paragraph preview; the pinned first sentence is
     #                 upstream of this span and untouched
     "sits. The finding is that it does not sit anywhere: it is diffuse, it compounds\n"
     "with $n$, and it is therefore not reachable by the levers one would try next.\n"
     "Everything here is measurement against brute-force counts.",
     "sits. Everything here is measurement against brute-force counts."),
    ("P4.L3.6", L3,  # paragraph-final epigram
     "barely moves the bound. \\emph{Per-type tuning is dead.}",
     "barely moves the bound."),
    # -- L4 ------------------------------------------------------------------
    ("P4.L4.1", L4,  # paragraph-final run: the BMR proof re-derivation
     "then $P$ has only finitely many limit points.\n"
     "Their proof extracts the coefficient of $u^n$ from the ODE to get\n"
     "$a_0(q,n)S_n = a_1(q,n)S_{n-1} + \\dots$, so $S_n$ has denominator dividing\n"
     "$I(q)\\prod_m a_0(q,m)$; a limit point $\\ell$ produces $(q_i,n_i)$ with\n"
     "$q_i \\to \\ell$, $n_i \\to \\infty$ and $a_0(q_i,n_i) = 0$, and dividing\n"
     "$a_0 = \\sum_k b_k(q)n^k$ by $n_i^d$ in the limit gives $b_d(\\ell) = 0$. Every\n"
     "limit point is a root of one fixed polynomial.",
     "then $P$ has only finitely many limit points."),
    ("P4.L4.2", L4,  # paragraph-final echo of the bold scope sentence
     "not extend to $D_A$-finite.} That is a ceiling on the method.",
     "not extend to $D_A$-finite.}"),
    # -- L5 ------------------------------------------------------------------
    ("P4.L5.1", L5,  # paragraph-final run: the proof preview
     "individual classes --- the whole job is those two. One direction is free. For\n"
     "the other, read an HV-convex animal left to right: it fattens, then shears, then\n"
     "thins. The shearing middle is a staircase animal and the two ends are stacks;\n"
     "stacks are too few to carry an exponential, and the middle has a rate at all\n"
     "because two staircase animals glue end to end without waste.",
     "individual classes --- the whole job is those two."),
    ("P4.L5.2", L5,  # paragraph-initial dangling referent
     "The mirage refines cleanly when the statistic changes. By \\emph{semiperimeter}",
     "By \\emph{semiperimeter}"),
    ("P4.L5.3", L5,  # mid-paragraph; the following sentence holds L5's SOLE
     #                 \cite{hardyRamanujan1918} and pins the splice boundary
     "there are, they carry no exponential. That is Lemma~\\ref{lem:stacks}'s entire\n"
     "role --- the outer blocks are counted only to be discarded. Hardy and\n"
     "Ramanujan~\\cite{hardyRamanujan1918} would give",
     "there are, they carry no exponential. Hardy and\n"
     "Ramanujan~\\cite{hardyRamanujan1918} would give"),
    # -- L6 ------------------------------------------------------------------
    ("P4.L6.1", L6,  # paragraph-initial lead-in
     "Quasi-polynomiality itself is worth one sentence, because it was the question\n"
     "that started this. $k = 3$ carries a genuine period-$2$ term on \\emph{both}",
     "$k = 3$ carries a genuine period-$2$ term on \\emph{both}"),
    ("P4.L6.2", L6,  # paragraph-final epigram
     "where the correct value is\n"
     "$24$. A six-term coincidence, and the kind that only a computation past the\n"
     "match can catch.",
     "where the correct value is\n"
     "$24$."),
]

# --- post-transform guards -------------------------------------------------
# (file, substring, why) — each must still occur at least once after every
# edit.  The constants mirror scripts/l_trim_gate.sh's CONSTANTS list
# (check 6) verbatim; the cite-key and \ref guards below are computed from
# the text itself rather than listed.
MUST_SURVIVE = [
    (L1, r"\Wp = 58", "gate check 6: single-occurrence constant, rem:notsquares"),
    (L1, r"\Wp = 57", "gate check 6 constant"),
    (L2, "1, 25, 208, 1483, 20688, 130208", "gate check 6: H series, single occurrence"),
    (L3, "6.543", "gate check 6 constant; P4.L3.5's paragraph holds two sites, both untouched"),
    (L3, "9.3154", "gate check 6 constant, same paragraph, untouched"),
    (L4, "1, 2, 4, 9, 29, 68, 181, 462, 1254, 3289", "gate check 6: psi-degree list, single occurrence"),
    (L5, "3.12340450886853853211", "gate check 6: single-occurrence constant, cor:floor"),
    (L6, "1, 6, 22, 68, 187, 470, 1106", "gate check 6 constant, comma form"),
    # the two tripwire neighbourhoods, asserted in their post-cut form:
    (L5, "however many stacks\nthere are, they carry no exponential. Hardy and",
     "P4.L5.3: the splice must sit flush against the sole hardyRamanujan1918 cite"),
    (L3, "The bracket-and-bisect then lands on a slightly weaker rational in twenty sweeps,\n"
         "at a wall time indistinguishable from the full-precision run.",
     "P4.L3.3: the crippling measurement's evidence survives whole"),
]

# (file, substring, why) — each must occur exactly zero times after every
# edit: one distinctive phrase per removed sentence.
MUST_VANISH = [
    (L1, "not unheard of", "P4.L1.1"),
    (L1, "worth one paragraph", "P4.L1.2"),
    (L1, "a small computation, not a large one", "P4.L1.3"),
    (L1, "doing real work", "P4.L1.4"),
    (L2, "telescopes through one series", "P4.L2.1"),
    (L2, "Not mostly", "P4.L2.2"),
    (L2, "The count is the content", "P4.L2.3"),
    (L2, "That accident is what", "P4.L2.4"),
    (L2, "the reusable part", "P4.L2.5"),
    (L3, "the honest parts", "P4.L3.1"),
    (L3, "A checker that cannot fail", "P4.L3.2"),
    (L3, "shows up honestly as lost digits", "P4.L3.3"),
    (L3, "the strongest statement", "P4.L3.4"),
    (L3, "it does not sit anywhere", "P4.L3.5"),
    (L3, "Per-type tuning is dead", "P4.L3.6"),
    (L4, "Their proof extracts the coefficient", "P4.L4.1"),
    (L4, "That is a ceiling on the method", "P4.L4.2"),
    (L5, "One direction is free", "P4.L5.1"),
    (L5, "The mirage refines cleanly", "P4.L5.2"),
    (L5, "entire\nrole", "P4.L5.3"),
    (L6, "worth one sentence", "P4.L6.1"),
    (L6, "A six-term coincidence", "P4.L6.2"),
]

failures: list[str] = []
texts: dict[str, str] = {}
orig_words: dict[str, int] = {}
orig_cites: dict[str, set] = {}
orig_refs: dict[str, set] = {}


def cite_keys(text: str) -> set:
    keys = set()
    for group in re.findall(r"\\cite(?:\[[^\]]*\])?\{([^}]*)\}", text):
        keys.update(k.strip() for k in group.split(","))
    return keys


def ref_keys(text: str) -> set:
    return set(re.findall(r"\\(?:eq)?ref\{([^}]*)\}", text))


def load(name: str) -> str:
    if name not in texts:
        texts[name] = (PAPER / name).read_text()
        orig_words[name] = len(texts[name].split())
        orig_cites[name] = cite_keys(texts[name])
        orig_refs[name] = ref_keys(texts[name])
    return texts[name]


def check(cond: bool, msg: str) -> bool:
    if not cond:
        failures.append(msg)
    return cond


# --- static sanity of the edit table itself --------------------------------
for pid, name, old, new in EDITS:
    check(len(new) < len(old), f"{pid}: replacement is not shorter")
    for label, s in (("old", old), ("new", new)):
        check("  " not in s, f"{pid}: {label} contains a double space")
        check(" \n" not in s, f"{pid}: {label} contains a trailing space before newline")
        check(not s.endswith(" "), f"{pid}: {label} ends with a space")
        check("\n\n" not in s, f"{pid}: {label} crosses a paragraph boundary")

# --- the edits: assert old unique, splice, assert new unique ---------------
for pid, name, old, new in EDITS:
    text = load(name)
    n = text.count(old)
    if not check(n == 1, f"{pid}: {name}: expected text occurs {n} times, need exactly 1: "
                         f"{old.splitlines()[0][:60]!r}..."):
        continue
    texts[name] = text.replace(old, new)
    m = texts[name].count(new)
    check(m == 1, f"{pid}: {name}: post-edit text occurs {m} times, need exactly 1: "
                  f"{new.splitlines()[0][:60]!r}...")
    removed = len(old.split()) - len(new.split())
    print(f"  cut  {pid:9s} {name:28s} -{removed} words")

# --- guards ----------------------------------------------------------------
for name, needle, why in MUST_SURVIVE:
    check(needle in load(name), f"guard: {name} no longer contains {needle!r} ({why})")

for name, needle, why in MUST_VANISH:
    n = load(name).count(needle)
    check(n == 0, f"guard: {name} still contains {needle!r} {n}x ({why})")

for name in texts:
    check(cite_keys(texts[name]) == orig_cites[name],
          f"guard: {name} cite-key set changed (gate check 7): "
          f"lost {sorted(orig_cites[name] - cite_keys(texts[name]))}, "
          f"gained {sorted(cite_keys(texts[name]) - orig_cites[name])}")
    lost_refs = orig_refs[name] - ref_keys(texts[name])
    check(not lost_refs, f"guard: {name} lost all refs to {sorted(lost_refs)}")
    check("\n\n\n" not in texts[name],
          f"guard: {name} has a double blank line; the one-separator invariant is broken")
    check(not re.search(r"[ \t]+\n", texts[name]),
          f"guard: {name} has trailing whitespace on a line")
    delta = len(texts[name].split()) - orig_words[name]
    check(delta <= 0, f"guard: {name} GREW by {delta} words")

# --- report, then commit to disk or nothing --------------------------------
print()
for name in sorted(texts):
    print(f"  words {name:28s} {orig_words[name]:5d} -> {len(texts[name].split()):5d}"
          f"  ({len(texts[name].split()) - orig_words[name]:+d})")

if failures:
    print("\napply-phase-4: ABORTED, no file written")
    for f in failures:
        print(f"  FAIL  {f}")
    sys.exit(1)

if "--check" in sys.argv[1:]:
    print("\napply-phase-4: --check passed, no file written")
    sys.exit(0)

for name, text in texts.items():
    (PAPER / name).write_text(text)
print(f"\napply-phase-4: wrote {len(texts)} files")
