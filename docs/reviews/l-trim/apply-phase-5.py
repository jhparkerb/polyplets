#!/usr/bin/env python3
"""Apply phase 5 of the L-trim campaign — the word-and-phrase cuts.

Mechanical and fail-closed, on the `apply-phase-4.py` model.  Every edit is a
CONTENT-ADDRESSED REPLACEMENT (old, new): `old` is a verbatim span of the tree
covering the cut words PLUS surviving boundary text, and `new` is that boundary
text with the words gone (or, for the rewordings this phase allows, the
verdict's replacement).  Both sides are asserted — `old` must occur exactly
once before, `new` exactly once after — and a single failed assertion aborts
the whole run with no file written.

The rulings are `phase-5-verdict.md`'s — the verdict, not the cuts file, is
the authority on what text ships.  Forty-two proposals applied as forty-five
instances; P5.L1.6 is RETAINED and appears below only as a guard asserting its
sentence survives untouched.

One convention of the cuts ledger is deliberately NOT implemented: its
"literal \\n means newline, unescape before matching" rule.  The defender
showed that rule self-contradicts on P5.L5.5, whose old text contains the
math token $\\nu$ — the bytes backslash-n-u — which a naive unescape corrupts.
So this file carries every string VERBATIM, with real newlines where the tree
has them and real backslashes where LaTeX has them, and no unescaping step
exists at all.

Edits with their own tripwires, guarded in the edit text or below:

  P5.L1.4   deletes the \\label{rem:newton} line AND its newline: `old` spans
            the full three lines (remark open, label, body start) so the splice
            asserts the surviving neighbours join with no blank line left; a
            guard asserts rem:newton is gone from L1 entirely (it was defined
            once and referenced nowhere, re-verified repo-wide);
  P5.L5.5   the $\\nu$ / newline collision above; the string here has the one
            real newline (between "of an" and "explicitly") and $\\nu$ intact;
  P5.L1.10  edits a remark title six lines above L1's single-occurrence pin
            \\Wp = 58; the pin is asserted below;
  P5.L1.6   RETAINED — guard only.

Post-transform guards mirror `scripts/l_trim_gate.sh`: all eight pinned
CONSTANTS (check 6), the per-paper \\cite-key set unchanged (check 7, computed
from the text), no \\ref key vanishing, splice hygiene (no double space, no
space before punctuation, no trailing whitespace, no double blank line),
sentence capitalisation at every paragraph-opening splice, and no paper may
grow in words.

Run from anywhere:

    python3 docs/reviews/l-trim/apply-phase-5.py          # apply
    python3 docs/reviews/l-trim/apply-phase-5.py --check  # assert only, write nothing

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

# --- the forty-five applied instances, as (pid, file, old, new) -------------
#
# Strings are verbatim tree text: real newlines, real backslashes, no escape
# convention.  `new` must be strictly shorter than `old`.

EDITS = [
    # -- L1 ------------------------------------------------------------------
    ("P5.L1.1", L1,
     "cite the nearest published relative, which is close\n"
     "enough to be worth stating plainly.",
     "cite the nearest published relative."),
    ("P5.L1.2", L1,
     "which is Lemma~\\ref{lem:sep} and the engine of\n"
     "everything after it.",
     "which is Lemma~\\ref{lem:sep}."),
    ("P5.L1.3", L1,
     "We state the measured position honestly:",
     "The measured position:"),
    ("P5.L1.4", L1,  # the label line and its newline; neighbours must join
     "\\begin{remark}[integer values, not integer coefficients]\n"
     "\\label{rem:newton}\n"
     "$P_k$ is integer-\\emph{valued};",
     "\\begin{remark}[integer values, not integer coefficients]\n"
     "$P_k$ is integer-\\emph{valued};"),
    ("P5.L1.5", L1,
     "each new $k$ turns out to cost exactly two new rational constants.",
     "each new $k$ costs exactly two new rational constants."),
    # P5.L1.6 RETAINED — see MUST_SURVIVE.
    ("P5.L1.7", L1,
     "each is elementary and\neach is exact per order.",
     "each is elementary and exact per order."),
    ("P5.L1.8", L1,
     "to determine $q_k$ outright.",
     "to determine $q_k$."),
    ("P5.L1.9", L1,
     "A reader who wants to check this rather than take it on trust should note",
     "A reader who wants to check this should note"),
    ("P5.L1.10", L1,
     "\\begin{remark}[$4, 9, 25$ are not squares, and that matters]",
     "\\begin{remark}[$4, 9, 25$ are not squares]"),
    ("P5.L1.11", L1,
     "\\begin{remark}[a name collision worth stating once]",
     "\\begin{remark}[a name collision]"),
    # -- L2 ------------------------------------------------------------------
    ("P5.L2.1", L2,
     "The proposition is worth pausing on, because the leading coefficient of $P_k$ is\n"
     "$25^k/k!$ --- emphatically not an integer.",
     "The leading coefficient of $P_k$ is $25^k/k!$ --- not an integer."),
    ("P5.L2.2", L2,
     "$k+1$ wide, with nothing to spare.",
     "$k+1$ wide."),
    ("P5.L2.3", L2,
     "--- verified through $y^{17}$ and no further.",
     "--- verified through $y^{17}$."),
    ("P5.L2.4", L2,
     "master equation, and we state them\n"
     "with that provenance rather than the older one.",
     "master equation."),
    ("P5.L2.5", L2,
     "That is unconditional and it is the easy half.",
     "That is unconditional."),
    ("P5.L2.6", L2,
     "genuinely different where it does not.",
     "different where it does not."),
    ("P5.L2.7", L2,
     "No law is claimed and the open problem is stated at\nthe end.",
     "No law is claimed."),
    ("P5.L2.8", L2,
     "(at $k=8$, $n=17$), so there is no runaway.",
     "(at $k=8$, $n=17$)."),
    # -- L3 ------------------------------------------------------------------
    ("P5.L3.1", L3,
     "\\footnote{Worth one sentence because it is easy to get\nbackwards.",
     "\\footnote{Easy to get backwards."),
    ("P5.L3.2", L3,
     "in a strict sense that is worth stating,\n"
     "because it is the organising idea of the paper.",
     "in a strict sense."),
    ("P5.L3.3", L3,
     "three facts, and it is worth\nseparating them, because only",
     "three facts: only"),
    ("P5.L3.4", L3,
     "make that sound rather than merely careful.",
     "make that sound."),
    ("P5.L3.5", L3,
     "The value of this is that it is \\emph{structurally} independent:",
     "It is \\emph{structurally} independent:"),
    ("P5.L3.6a", L3,
     "and, decisively, that it",
     "and that it"),
    ("P5.L3.6b", L3,
     "is genuinely uncertain:",
     "is uncertain:"),
    ("P5.L3.6c", L3,
     "is precisely what the Klarner--Rivest",
     "is what the Klarner--Rivest"),
    ("P5.L3.6d", L3,
     "has \\emph{no effect at all} here.",
     "has \\emph{no effect} here."),
    # -- L4 ------------------------------------------------------------------
    ("P5.L4.1", L4,
     "starts the same way, and we should\n"
     "say so before saying what is different.",
     "starts the same way."),
    ("P5.L4.2", L4,
     "we cite it rather\nthan re-deriving it as though it were ours.",
     "we cite it rather than re-deriving it."),
    ("P5.L4.3", L4,
     "cannot\nfollow, and it is worth being exact about why: the step",
     "cannot follow: the step"),
    ("P5.L4.4", L4,
     "--- a genuinely different instrument",
     "--- a different instrument"),
    # -- L5 ------------------------------------------------------------------
    ("P5.L5.1", L5,
     "and it turns out to hold for both\nlattices,",
     "and it holds for both lattices,"),
    ("P5.L5.2", L5,
     "the area side was never tractable in the first place.",
     "the area side was never tractable."),
    ("P5.L5.3", L5,
     "about the\nindividual classes --- the whole job is those two.",
     "about the individual classes."),
    ("P5.L5.4", L5,
     "and both are\nworth stating because they are what makes",
     "and they are what makes"),
    ("P5.L5.5", L5,  # $\nu$ is the math token, NOT a newline; the one real
     #                 newline sits between "of an" and "explicitly"
     "So $\\nu$ is not an artefact of an extrapolation: it is the growth constant of an\n"
     "explicitly counted half of the series. Measured,",
     "Measured,"),
    ("P5.L5.6", L5,
     "That reading\nis wrong, and the correction is instructive:",
     "That reading is wrong:"),
    ("P5.L5.7", L5,
     "A free by-product of the split:",
     "A by-product of the split:"),
    # -- L6 ------------------------------------------------------------------
    ("P5.L6.1", L6,
     "are quite different creatures:",
     "are different creatures:"),
    ("P5.L6.2", L6,
     "found nothing --- the law\n"
     "is there and the first two terms hide it. It predicts",
     "found nothing. The law predicts"),
    ("P5.L6.3", L6,
     "odd-$p$ rows\nstabilise perfectly well.",
     "odd-$p$ rows stabilise."),
    ("P5.L6.4", L6,
     "\\paragraph{A refutation worth recording.}",
     "\\paragraph{A refutation.}"),
    ("P5.L6.5", L6,
     "as explicit\nas $P(x)$ itself and no more, and",
     "as explicit as $P(x)$ itself, and"),
    ("P5.L6.6", L6,
     "--- so it is sharp and no better bound exists.",
     "--- so it is sharp."),
    ("P5.L6.7", L6,
     "an apparent exception, and resolving it is the sharpest thing here:\neach",
     "an apparent exception: each"),
]

# Edits whose `new` opens a sentence (or a footnote): the first letter must be
# capitalised, and the contextual anchors in MUST_SURVIVE pin the splice.
SENTENCE_OPENERS = {"P5.L1.3", "P5.L2.1", "P5.L3.1", "P5.L3.5", "P5.L5.5"}

# --- post-transform guards -------------------------------------------------
# (file, substring, why) — each must still occur at least once after every
# edit.  The constants mirror scripts/l_trim_gate.sh's CONSTANTS list
# (check 6) verbatim.
MUST_SURVIVE = [
    (L1, "\\Wp = 58", "gate check 6: single-occurrence constant, six lines below P5.L1.10's title edit"),
    (L1, "\\Wp = 57", "gate check 6 constant"),
    (L2, "1, 25, 208, 1483, 20688, 130208", "gate check 6: H series, single occurrence"),
    (L3, "6.543", "gate check 6 constant"),
    (L3, "9.3154", "gate check 6 constant"),
    (L4, "1, 2, 4, 9, 29, 68, 181, 462, 1254, 3289", "gate check 6: psi-degree list, single occurrence"),
    (L5, "3.12340450886853853211", "gate check 6: single-occurrence constant, cor:floor"),
    (L6, "1, 6, 22, 68, 187, 470, 1106", "gate check 6 constant, comma form"),
    # P5.L1.6 is RETAINED: the ranked list and its aside survive verbatim.
    (L1, "and --- the load-bearing feature --- no weight enumeration, so the\n"
         "proof covers all $k$ at once",
     "P5.L1.6 retained: the causal attribution stays"),
    # the splice neighbourhoods that carry their own risk, in post-edit form:
    (L1, "\\begin{remark}[integer values, not integer coefficients]\n"
         "$P_k$ is integer-\\emph{valued}; its coefficients",
     "P5.L1.4: the label line is gone and its neighbours join with no blank line"),
    (L1, "replaced by $\\Wp$ throughout. The measured position: the",
     "P5.L1.3: sentence opens capitalised after the splice"),
    (L2, "\\end{proof}\n\nThe leading coefficient of $P_k$ is $25^k/k!$ --- not an integer. Integer-valuedness",
     "P5.L2.1: paragraph opens capitalised after the splice"),
    (L3, "actually certified.\\footnote{Easy to get backwards. The lower certificate",
     "P5.L3.1: footnote opens capitalised after the splice"),
    (L3, "term ratios give.\n\nIt is \\emph{structurally} independent: strip spectra",
     "P5.L3.5: paragraph opens capitalised after the splice"),
    (L5, "\\end{proof}\n\nMeasured,\n\\begin{quote}\\small\n$\\nu = 2.514",
     "P5.L5.5: the stranded fragment is now a paragraph-opening sentence, capitalised, "
     "with the quote block as its object"),
    (L6, "That is exactly as explicit as $P(x)$ itself, and this paper does not call it a closed form.",
     "P5.L6.5: 'exactly' and the not-a-closed-form hedge both survive"),
]

# (file, substring, why) — each must occur exactly zero times after every
# edit: one distinctive phrase per removed span, plus the dead label.
MUST_VANISH = [
    (L1, "worth stating plainly", "P5.L1.1"),
    (L1, "the engine of", "P5.L1.2"),
    (L1, "position honestly", "P5.L1.3"),
    (L1, "rem:newton", "P5.L1.4: label gone, and nothing ever referenced it"),
    (L1, "turns out to cost", "P5.L1.5"),
    (L1, "and\neach is exact", "P5.L1.7"),
    (L1, "outright", "P5.L1.8"),
    (L1, "rather than take it on trust", "P5.L1.9"),
    (L1, "and that matters", "P5.L1.10"),
    (L1, "worth stating once", "P5.L1.11"),
    (L2, "worth pausing on", "P5.L2.1"),
    (L2, "emphatically", "P5.L2.1"),
    (L2, "with nothing to spare", "P5.L2.2"),
    (L2, "and no further", "P5.L2.3"),
    (L2, "that provenance rather than the older one", "P5.L2.4"),
    (L2, "the easy half", "P5.L2.5"),
    (L2, "genuinely different", "P5.L2.6"),
    (L2, "the open problem is stated at", "P5.L2.7"),
    (L2, "no runaway", "P5.L2.8"),
    (L3, "Worth one sentence", "P5.L3.1"),
    (L3, "the organising idea of the paper", "P5.L3.2"),
    (L3, "worth\nseparating them", "P5.L3.3"),
    (L3, "rather than merely careful", "P5.L3.4"),
    (L3, "The value of this is that", "P5.L3.5"),
    (L3, "decisively", "P5.L3.6a"),
    (L3, "genuinely uncertain", "P5.L3.6b"),
    (L3, "precisely what the Klarner", "P5.L3.6c"),
    (L3, "at all} here", "P5.L3.6d"),
    (L4, "say so before saying what is different", "P5.L4.1"),
    (L4, "as though it were ours", "P5.L4.2"),
    (L4, "worth being exact about why", "P5.L4.3"),
    (L4, "genuinely different instrument", "P5.L4.4"),
    (L5, "turns out to hold", "P5.L5.1"),
    (L5, "in the first place", "P5.L5.2"),
    (L5, "the whole job is those two", "P5.L5.3"),
    (L5, "worth stating because", "P5.L5.4"),
    (L5, "not an artefact of an extrapolation", "P5.L5.5"),
    (L5, "the correction is instructive", "P5.L5.6"),
    (L5, "A free by-product", "P5.L5.7"),
    (L6, "quite different creatures", "P5.L6.1"),
    (L6, "the first two terms hide it", "P5.L6.2"),
    (L6, "perfectly well", "P5.L6.3"),
    (L6, "refutation worth recording", "P5.L6.4"),
    (L6, "and no more", "P5.L6.5"),
    (L6, "no better bound exists", "P5.L6.6"),
    (L6, "the sharpest thing here", "P5.L6.7"),
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


def first_letter(s: str) -> str:
    # skip any leading LaTeX command-plus-brace prefix (\footnote{, \emph{, ...)
    s = re.sub(r"^(\\[A-Za-z]+\{)+", "", s)
    for ch in s:
        if ch.isalpha():
            return ch
    return ""


# --- static sanity of the edit table itself --------------------------------
seen_pids = set()
for pid, name, old, new in EDITS:
    check(pid not in seen_pids, f"{pid}: duplicate edit id")
    seen_pids.add(pid)
    check(len(new) < len(old), f"{pid}: replacement is not shorter")
    check(len(new.split()) < len(old.split()), f"{pid}: replacement is not fewer words")
    for label, s in (("old", old), ("new", new)):
        check("  " not in s, f"{pid}: {label} contains a double space")
        check(" \n" not in s, f"{pid}: {label} contains a trailing space before newline")
        check(not s.endswith(" "), f"{pid}: {label} ends with a space")
        check("\n\n" not in s, f"{pid}: {label} crosses a paragraph boundary")
    check(not re.search(r" [.,;!?]", new), f"{pid}: new has a space before punctuation")
    if pid in SENTENCE_OPENERS:
        check(first_letter(new).isupper(), f"{pid}: sentence-opening splice is not capitalised")
check(len(EDITS) == 45, f"edit table holds {len(EDITS)} instances, expected 45")

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
    # splice hygiene at the boundary, one character each side of the new span
    idx = texts[name].find(new)
    window = texts[name][max(0, idx - 1): idx + len(new) + 1]
    check("  " not in window, f"{pid}: splice created a double space")
    check(not re.search(r" [.,;!?]", window), f"{pid}: splice created a space before punctuation")
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
    print("\napply-phase-5: ABORTED, no file written")
    for f in failures:
        print(f"  FAIL  {f}")
    sys.exit(1)

if "--check" in sys.argv[1:]:
    print("\napply-phase-5: --check passed, no file written")
    sys.exit(0)

for name, text in texts.items():
    (PAPER / name).write_text(text)
print(f"\napply-phase-5: wrote {len(texts)} files")
