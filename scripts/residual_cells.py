#!/usr/bin/env python3
"""The residual-cell statement, computed once, plus a gate over every restatement.

Written 2026-08-19 after the Confetti harvest, when a sweep of the notes found
FOUR mutually inconsistent accounts of "the cells that still have one source":

  docs/motley-plan.md           row 40's residual band 9 -> 7 -> 5 -> 3
  results/ticker-tape-assessment.md   Ticker Tape's two cells: T(40,19), T(40,23)
  docs/acceptance-queue.md      Ticker Tape takes "four of the six"
  HANDOFF.md                    the 9 -> 7 -> 5 band "does not reproduce"

Three of the four are right and they disagree because **two different
quantities share one name**.  Nothing anywhere defined either of them, and
`scripts/provenance_table.py` pinned a COUNT for one of them and no list, so a
wrong list -- and a claim about the other quantity entirely -- sailed through
the gate for a day.

The two quantities:

  Q1  CONGRUENCE-ONLY cells.  Over all 820 cells of the triangle: those with no
      exact recount and no closed form, so the only thing standing behind the
      value is the mod-2/mod-4 subgroup census, which catches an error iff it
      is nonzero mod 4.  This is what scripts/provenance_table.py computes and
      pins.  Rule: results/subgroup-mod4.md, results/provenance-table.md.

  Q2  ROW 40'S RESIDUAL BAND.  Row 40 only: the cells that are not
      RULE-INDEPENDENT -- that still rest on the incumbent engine's union-find
      connectivity rule.  Two ends, per docs/b1-closure-plan.md section 1:
        h <= 21   swept by the incumbent; rule-independent once Motley reaches h
        h >= 22   never enumerated, wired from the P_k closed form at level
                  k = 40 - h.  The shape is a theorem (docs/proofs/
                  diagonal-law.md) but the two free coefficients per level are
                  fit from real swept cells, so the cell is rule-independent iff
                  BOTH anchors T(2k+1, k+1) and T(2k+2, k+2) -- heights 41 - h
                  and 42 - h -- are within Motley's reach.

They are different questions.  Q1 asks "was this value ever recomputed"; Q2
asks "does this value still depend on one connectivity rule".  A cell can be
comfortable on one axis and exposed on the other, which is why quoting a Q2
figure under a Q1 sentence looks like an error and is not, and why the reverse
looks fine and is.

    python3 scripts/residual_cells.py            # write results/residual-cells.md
    python3 scripts/residual_cells.py --check    # gate
    python3 scripts/residual_cells.py --selftest # RED controls

THE GATE.  results/residual-cells.md is the one place these numbers live.
Every other tracked document that states one must mark it inline with the fact
it is quoting, and the gate verifies the marked value -- count AND cell list --
against the computed one:

    <!--q:congruence_only.count@18=6-->
    <!--q:congruence_only.cells@18=(38,19),(39,19),(39,20),(40,19),(40,20),(40,21)-->

A unit that mentions residual or congruence-only cells and carries no marker
FAILS.  The unit is the PARAGRAPH for prose and the ROW for tables, because
prose wraps and a triggered table header has its numbers in the body; a bullet
starts a new unit so one marker cannot cover a list.  A unit that genuinely
states no checkable number declares `<!--q:prose-->`, and that declaration is
itself checked -- numbers that are names (a cell, a row, a term, a modulus, a
height bound, Q1/Q2, a date) are stripped and any digit still standing rejects
the declaration, so the escape hatch cannot smuggle a count past the gate.

Trigger matching runs with markdown emphasis stripped: HANDOFF.md wrote
"**only** the mod-4 congruence" and the first version of the pattern walked
straight past it, which is a fail-OPEN and has its own RED control.

Fail-closed in the vacuous direction too: if the scan finds no trigger lines at
all, the trigger pattern has rotted and the gate fails rather than reporting
that everything is fine.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
import provenance_table as PT          # noqa: E402  (path set above)

OUT = ROOT / "results" / "residual-cells.md"
CANONICAL = "results/residual-cells.md"

NMAX = PT.NMAX
# The ladder the notes actually discuss: banked step 0 through the height that
# would close row 40 outright.  MOTLEY_H is where it stands today.
LADDER = range(16, 22)

# results/ghostship/ is a frozen record of a different filesystem and a
# different day's numbers; it is excluded by scope, not by markers, for the
# same reason tests/gate_citations.py excludes it -- a record that gets edited
# to keep a gate happy has stopped being a record.
EXCLUDED_TREES = ("results/ghostship/",)


# --------------------------------------------------------------------------
# The facts.
# --------------------------------------------------------------------------

def formula_lo(n: int) -> int:
    """Lowest height on row n reached by the P_k closed-form band.

    Two constraints, both from docs/proofs/diagonal-law.md: the wired levels
    stop at k <= 18 (h >= n - 18), and the onset is sharp at n >= 2k+1
    (h >= (n+1)/2).  The band is whichever binds harder.
    """
    return max(n - 18, -(-(n + 1) // 2))


def row40_residual(motley_h: int) -> list[tuple[int, int]]:
    """Q2: row 40's cells that still rest on the incumbent connectivity rule."""
    out = []
    for h in range(1, NMAX + 1):
        if h <= 21:
            if h > motley_h:                 # swept, not yet re-swept by Motley
                out.append((NMAX, h))
        else:
            # wired at level k = 40 - h; anchors sit at heights 41-h and 42-h,
            # and the higher of the two is what has to be inside Motley's reach
            if (42 - h) > motley_h:
                out.append((NMAX, h))
    return out


def closure_n(motley_h: int) -> int:
    """Largest n whose every cell is rule-independent, by the OVERLAP criterion.

    Motley covers h <= H from below and the closed-form band covers
    h >= formula_lo(n) from above.  The published figure requires the two to
    OVERLAP -- at least one cell where both methods produce the value and can
    be compared -- not merely to abut.  That is the conservative reading and it
    is the one results/motley-h18.md publishes ("n <= 35" at H = 18).

    The shortcut "n <= 2H - 1" agrees with this for H <= 19 and parts company
    above it (H = 20 gives 38, not 39), so the criterion is computed, not the
    shortcut.
    """
    best = 0
    for n in range(1, NMAX + 1):
        if all(formula_lo(m) <= motley_h for m in range(1, n + 1)):
            best = n
    return best


def facts() -> dict:
    """Every quantity the notes are allowed to quote, keyed as they cite it."""
    T = PT.read_triangle()
    F = {}
    prev_q1 = prev_q2 = None
    for h in LADDER:
        _, _, _, stats = PT.analyse(T, motley_h=h)
        q1 = sorted(stats["congruence_only"])
        q2 = sorted(row40_residual(h))
        F["congruence_only.cells@%d" % h] = q1
        F["congruence_only.count@%d" % h] = len(q1)
        F["row40_congruence_only.cells@%d" % h] = [c for c in q1 if c[0] == NMAX]
        F["row40_congruence_only.count@%d" % h] = len(
            [c for c in q1 if c[0] == NMAX])
        F["row40_residual.cells@%d" % h] = q2
        F["row40_residual.count@%d" % h] = len(q2)
        F["closure_n@%d" % h] = closure_n(h)
        if prev_q1 is not None:
            # what the rung AT this height retires, which is the figure every
            # pricing note quotes and the one that was wrong.
            F["retires.cells@%d" % h] = [c for c in prev_q1 if c not in q1]
            F["retires.count@%d" % h] = len([c for c in prev_q1 if c not in q1])
            F["row40_retires.cells@%d" % h] = [c for c in prev_q2 if c not in q2]
            F["row40_retires.count@%d" % h] = len(
                [c for c in prev_q2 if c not in q2])
        prev_q1, prev_q2 = q1, q2
    return F


# --------------------------------------------------------------------------
# The scan.
# --------------------------------------------------------------------------

# A line is a residual claim if it names the subject unambiguously, or if it
# says "residual" in the same breath as a cell.  The second half is deliberately
# anchored to this triangle: results/onset-defect-crossover.md and
# results/v5-denominator-law.md talk about fit residuals over cells and are not
# about this at all.
TRIGGER_RE = re.compile(
    r"congruence[- ]only"
    r"|only the mod-4|only the congruence|nothing but the congruence"
    r"|residual (?:cells|band)\b(?=.*(?:row 40|T\(40|Motley|Ticker|congruence))"
    r"|row 40'?s residual",
    re.I)

# Emphasis inside the phrase must not hide it.  "**only** the mod-4 congruence"
# is the exact wording HANDOFF.md used and the trigger walked straight past it,
# which is a fail-OPEN and the worst kind of gate defect.  Trigger matching runs
# on the line with markdown emphasis stripped.
EMPHASIS_RE = re.compile(r"[*_`]")


def triggered(text: str) -> bool:
    return bool(TRIGGER_RE.search(EMPHASIS_RE.sub("", text)))


MARKER_RE = re.compile(r"<!--\s*q:([^>]*?)\s*-->")
CELL_RE = re.compile(r"\(\s*(\d{1,2})\s*,\s*(\d{1,2})\s*\)")
DIGIT_RE = re.compile(r"\d")
# Numbers that are names, not counts: a cell, a row, a term, a modulus, a
# height or size bound, a section, a date.  `q:prose` is checked by stripping
# these and requiring nothing numeric to be left -- so "row 40's residual band"
# may declare prose and "shrinking 9 -> 7 -> 5 -> 3 cells" may not.
NONCOUNT_RE = re.compile(
    r"T\(\s*\d+\s*,\s*\d+\s*\)|\(\s*\d+\s*,\s*\d+\s*\)|a\(\s*\d+\s*\)"
    r"|row\s+\d+|mod[- ]\d+|§\d+|\d{4}-\d\d-\d\d|\bQ[12]\b"
    r"|[HhNnKk]\s*(?:<=|>=|≤|≥|=|<|>)\s*\d+")

# results/provenance-table.md is generated by the OTHER generator and states
# the Q1 count and list in prose of its own.  Two generators emitting the same
# numbers is precisely the drift this gate exists to stop, so it is not asked
# for markers -- it is parsed and compared directly.  See check_peer().
GENERATED_PEER = "results/provenance-table.md"


def tracked_docs() -> list[str]:
    out = subprocess.run(["git", "ls-files", "*.md", "*.tex"], cwd=ROOT,
                         capture_output=True, text=True, check=True)
    return [p for p in out.stdout.split()
            if p not in (CANONICAL, GENERATED_PEER)
            and not p.startswith(EXCLUDED_TREES)]


def check_peer(F: dict) -> list[str]:
    """results/provenance-table.md states Q1 too; hold it to the same facts.

    Fail-closed on the parse: if neither the count nor the list can be found,
    the other generator's wording has moved and this check has silently stopped
    checking, which is worse than a disagreement.
    """
    path = ROOT / GENERATED_PEER
    if not path.exists():
        return ["%s is missing; it is a generated file and `make "
                "gate-provenance` writes it" % GENERATED_PEER]
    text = path.read_text(errors="replace")
    bad = []
    h = PT.MOTLEY_H
    m = re.search(r"only\*{0,2} the mod-4 congruence[^\n]*?\*\*(\d+)\*\*", text)
    if not m:
        bad.append("%s: cannot find the congruence-only count -- the other "
                   "generator's wording moved and this check went blind"
                   % GENERATED_PEER)
    elif int(m.group(1)) != F["congruence_only.count@%d" % h]:
        bad.append("%s: states %s congruence-only cells, computed %d"
                   % (GENERATED_PEER, m.group(1),
                      F["congruence_only.count@%d" % h]))
    # The generator writes the list on a line of its own, indented, nothing
    # else on it.  Match that line whole -- picking cells out of the whole file
    # would let an extra cell hide anywhere in it.
    listed = None
    for line in text.splitlines():
        if re.fullmatch(r"\s+T\(\d{1,2},\d{1,2}\)"
                        r"(?:,\s*T\(\d{1,2},\d{1,2}\))*\s*", line):
            listed = sorted((int(a), int(b)) for a, b in
                            re.findall(r"T\((\d{1,2}),(\d{1,2})\)", line))
            break
    want = sorted(F["congruence_only.cells@%d" % h])
    if listed is None:
        bad.append("%s: cannot find the congruence-only cell list -- the other "
                   "generator's wording moved and this check went blind"
                   % GENERATED_PEER)
    elif listed != want:
        bad.append("%s: lists %s, computed %s"
                   % (GENERATED_PEER, fmt(listed), fmt(want)))
    return bad


def parse_marker(body: str):
    """'name@H=value' -> (key, parsed value).  Returns None if malformed."""
    if body == "prose":
        return ("prose", None)
    if "=" not in body:
        return None
    key, _, val = body.partition("=")
    key, val = key.strip(), val.strip()
    if ".count@" in key or key.startswith("closure_n@"):
        try:
            return (key, int(val))
        except ValueError:
            return None
    # Range shorthand, so a marker can be the same text the prose already uses:
    # `T(40,17)..T(40,25)` is the contiguous run of heights on one row.
    rng = re.fullmatch(r"T\((\d+),(\d+)\)\.\.T\((\d+),(\d+)\)", val)
    if rng:
        n1, h1, n2, h2 = (int(x) for x in rng.groups())
        if n1 != n2 or h2 < h1:
            return None
        return (key, [(n1, h) for h in range(h1, h2 + 1)])
    cells = [(int(a), int(b)) for a, b in CELL_RE.findall(val)]
    if not cells:
        return None
    return (key, cells)


TABLE_RULE_RE = re.compile(r"^\s*\|[\s:|-]*\|\s*$")
BULLET_RE = re.compile(r"^\s*(?:[-*+]\s|\d+\.\s)")


def trigger_lines(text: str) -> list[tuple[int, str]]:
    """Which units of a document are residual claims, and what text each covers.

    Two shapes, and the unit differs:

    PROSE -- the unit is the paragraph, not the line.  Prose wraps, so the word
    that trips the trigger and the marker that answers it routinely land on
    different lines; tests/gate_citations.py learned the same lesson the hard
    way (commit 2c7b272, "prose wraps, and the first file to use the directive
    wrapped").  A paragraph-scoped unit also means `q:prose` is checked against
    the whole paragraph, which is strict on purpose.

    TABLE -- the unit is the row, and a triggered HEADER extends the trigger
    over the body.  The header is where the word "residual" appears and the
    body is where the numbers are, so checking only the matched line would
    leave every figure unguarded -- docs/motley-plan.md keeps the whole ladder
    in rows under a header that says "residual band".
    """
    out, lines = [], text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if not triggered(line):
            i += 1
            continue
        if line.lstrip().startswith("|"):
            out.append((i + 1, line))
            j = i + 1
            while j < len(lines) and lines[j].lstrip().startswith("|"):
                if not TABLE_RULE_RE.match(lines[j]):
                    out.append((j + 1, lines[j]))
                j += 1
            i = j
            continue
        # Prose: widen to the paragraph -- back to the last blank line, table
        # row or list bullet, forward to the next one.  A bullet starts a new
        # unit: a whole list read as one paragraph would let a marker in the
        # first bullet excuse an unmarked claim in the third.
        def boundary(j):
            return (not lines[j].strip()
                    or lines[j].lstrip().startswith("|")
                    or BULLET_RE.match(lines[j]))
        lo = i
        while lo > 0 and not boundary(lo - 1) and not BULLET_RE.match(lines[lo]):
            lo -= 1
        if not BULLET_RE.match(lines[lo]):
            while lo > 0 and not boundary(lo - 1):
                lo -= 1
        hi = i
        while hi + 1 < len(lines) and not boundary(hi + 1):
            hi += 1
        out.append((i + 1, "\n".join(lines[lo:hi + 1])))
        i = hi + 1
    return out


def scan(F: dict, docs: list[str], verbose=False):
    """Check every residual claim in every tracked document.  Returns problems."""
    bad, checked, triggers = [], 0, 0
    for rel in docs:
        text = (ROOT / rel).read_text(errors="replace")
        for i, line in trigger_lines(text):
            triggers += 1
            markers = MARKER_RE.findall(line)
            if not markers:
                bad.append("%s:%d: residual claim with no `<!--q:...-->` "
                           "marker -- %s"
                           % (rel, i, " ".join(line.split())[:90]))
                continue
            for body in markers:
                parsed = parse_marker(body)
                if parsed is None:
                    bad.append("%s:%d: malformed marker `q:%s`" % (rel, i, body))
                    continue
                key, val = parsed
                if key == "prose":
                    # The escape hatch, and it is checked: a line declaring it
                    # states no number may not contain one.
                    stripped = NONCOUNT_RE.sub("", MARKER_RE.sub("", line))
                    if DIGIT_RE.search(stripped):
                        bad.append("%s:%d: `q:prose` declared, but the line "
                                   "states a number -- %s"
                                   % (rel, i, stripped.strip()[:90]))
                    else:
                        checked += 1
                    continue
                if key not in F:
                    bad.append("%s:%d: marker names `%s`, which this script "
                               "does not compute" % (rel, i, key))
                    continue
                want = F[key]
                if isinstance(want, list):
                    want = sorted(want)
                    got = sorted(val) if isinstance(val, list) else val
                    ok = got == want
                else:
                    got, ok = val, (val == want)
                if not ok:
                    bad.append("%s:%d: `%s` -- document says %s, computed %s"
                               % (rel, i, key, got, want))
                else:
                    checked += 1
                    if verbose:
                        print("  ok  %-34s %s:%d" % (key, rel, i))
    if triggers == 0:
        bad.append("VACUOUS: the trigger pattern matched nothing in %d tracked "
                   "documents.  The pattern has rotted; this gate is not "
                   "checking anything." % len(docs))
    return bad, checked, triggers


# --------------------------------------------------------------------------
# Output.
# --------------------------------------------------------------------------

def fmt(cells) -> str:
    return ", ".join("T(%d,%d)" % c for c in cells) if cells else "none"


def write_note(F: dict):
    L = []
    L.append("# The residual cells — the one place\n")
    L.append("Generated by `scripts/residual_cells.py`; do not hand-edit.\n"
             "`make gate-residual-cells` regenerates it and fails if any other\n"
             "tracked document quotes one of these counts or lists and gets it\n"
             "wrong — or quotes one without saying which one it is quoting.\n")
    L.append("Written because four notes gave four accounts of \"the cells that\n"
             "still have one source\" and three of them were right: **two\n"
             "different quantities were sharing one name**, and nothing defined\n"
             "either. They are Q1 and Q2 below. Quoting a Q2 figure under a Q1\n"
             "sentence is the mistake that hid here for a day.\n")

    L.append("\n## Q1 — congruence-only cells\n")
    L.append("All 820 cells. A cell is **congruence-only** when nothing "
             "recomputed it and no closed form covers it, so the only check it "
             "carries is the mod-2/mod-4 subgroup census "
             "(`results/subgroup-mod4.md`) — which catches an error if and only "
             "if the error is nonzero mod 4. Computed by "
             "`scripts/provenance_table.py`.\n")
    L.append("| Motley reaches | congruence-only | retired by this rung | cells |")
    L.append("|---|---|---|---|")
    for h in LADDER:
        ret = F.get("retires.count@%d" % h)
        L.append("| H ≤ %d | %d | %s | %s |"
                 % (h, F["congruence_only.count@%d" % h],
                    "—" if ret is None else str(ret),
                    fmt(F["congruence_only.cells@%d" % h])))

    L.append("\n## Q2 — row 40's residual band\n")
    L.append("Row 40 only, and a different question: which cells still rest on "
             "the incumbent engine's union-find connectivity rule. Rule: "
             "`docs/b1-closure-plan.md` §1.\n")
    L.append("- `h ≤ 21` — swept by the incumbent, and rule-independent once "
             "Motley re-sweeps that height.")
    L.append("- `h ≥ 22` — never enumerated; wired from the closed form at "
             "level `k = 40 − h`. The shape is a theorem "
             "(`docs/proofs/diagonal-law.md`) but the two free coefficients per "
             "level are fit from real swept cells, so the cell is "
             "rule-independent exactly when both anchors `T(2k+1,k+1)` and "
             "`T(2k+2,k+2)` — heights `41−h` and `42−h` — are inside Motley's "
             "reach.\n")
    L.append("| Motley reaches | residual | retired by this rung | cells |")
    L.append("|---|---|---|---|")
    for h in LADDER:
        ret = F.get("row40_retires.cells@%d" % h)
        L.append("| H ≤ %d | %d | %s | %s |"
                 % (h, F["row40_residual.count@%d" % h],
                    "—" if ret is None else fmt(ret),
                    fmt(F["row40_residual.cells@%d" % h])))

    L.append("\n## Closure — the largest fully rule-independent a(n)\n")
    L.append("Motley covers `h ≤ H` from below; the closed-form band covers "
             "`h ≥ max(n−18, ⌈(n+1)/2⌉)` from above. The published figure "
             "requires the two to **overlap** — at least one cell where both "
             "methods produce the value and can be compared — not merely to "
             "abut. The shortcut `n ≤ 2H−1` agrees for H ≤ 19 and parts company "
             "above it, so the criterion is computed rather than the shortcut.\n")
    L.append("| Motley reaches | a(n) closed for | `2H−1` |")
    L.append("|---|---|---|")
    for h in LADDER:
        L.append("| H ≤ %d | n ≤ %d | %d |" % (h, F["closure_n@%d" % h], 2 * h - 1))

    L.append("\n## Where the ladder stops\n")
    L.append("Q1 and Q2 both reach zero only at **H = 21**, and H = 21 does not "
             "fit in RAM at any rung of the arena ladder "
             "(`docs/b1-closure-plan.md` §3). The formula end cannot substitute: "
             "level 19's own two anchors are `T(39,20)` and `T(40,21)`, so "
             "pinning `P_19` from them to corroborate them is circular, and the "
             "non-circular route — `(a_19, b_19)` ab initio from surplus-19 "
             "cluster weights (`docs/proofs/grand-form.md`) — is ten levels past "
             "the k ≤ 9 the Severance campaign reached. Ticker Tape (H = 19) is "
             "priced and declined in `results/ticker-tape-assessment.md`.\n")

    L.append("\n## How to quote these numbers\n")
    L.append("Mark the claim inline with the fact it quotes; the gate verifies "
             "count **and** cell list:\n")
    L.append("```")
    L.append("<!--q:congruence_only.count@18=6-->")
    L.append("<!--q:row40_residual.cells@18=T(40,19),T(40,20),T(40,21),"
             "T(40,22),T(40,23)-->")
    L.append("```")
    L.append("\nA residual claim with no marker fails the gate. A line that "
             "states no checkable number declares `<!--q:prose-->`, and that "
             "declaration is checked too — a `prose` line containing a number "
             "is rejected.\n")
    L.append("Facts available: `congruence_only.{count,cells}@H`, "
             "`row40_residual.{count,cells}@H`, `retires.{count,cells}@H`, "
             "`row40_retires.{count,cells}@H`, `closure_n@H`, for H = 16..21.\n")
    OUT.write_text("\n".join(L))


# --------------------------------------------------------------------------
# RED controls.
# --------------------------------------------------------------------------

def selftest() -> int:
    F = facts()
    import tempfile
    problems = []

    def run(body: str, name: str):
        """Scan one synthetic document; return the gate's complaints."""
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / name
            p.write_text(body)
            # scan() reads relative to ROOT, so hand it an absolute-ish shim
            saved, globals()["ROOT"] = ROOT, Path(d)
            try:
                bad, checked, trig = scan(F, [name])
            finally:
                globals()["ROOT"] = saved
            return bad, checked, trig

    def run_peer(count, cells):
        """Scan a synthetic provenance-table.md through check_peer()."""
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "results"
            p.mkdir()
            body = ""
            if count is not None:
                body += ("- cells carrying **only** the mod-4 congruence — no "
                         "exact recount, no closed form: **%d**\n\n" % count)
            if cells is not None:
                body += "  " + ", ".join("T(%d,%d)" % c for c in cells) + "\n"
            (p / "provenance-table.md").write_text(body or "nothing here\n")
            saved, globals()["ROOT"] = ROOT, Path(d)
            try:
                return check_peer(F)
            finally:
                globals()["ROOT"] = saved

    good_cells = ",".join("(%d,%d)" % c for c in F["congruence_only.cells@18"])

    # GREEN control: a correct marker passes, and is counted as checked.
    bad, checked, trig = run(
        "six congruence-only cells remain "
        "<!--q:congruence_only.count@18=6-->\n", "ok.md")
    if bad or checked != 1 or trig != 1:
        problems.append("GREEN control: correct marker did not pass cleanly "
                        "(%s, checked=%d, triggers=%d)" % (bad, checked, trig))

    # RED 1: a residual claim with no marker at all.
    bad, _, _ = run("four of the six remaining congruence-only cells\n", "r1.md")
    if not any("no `<!--q:" in b for b in bad):
        problems.append("RED 1: an unmarked residual claim was not caught")

    # RED 2: a wrong count.
    bad, _, _ = run("congruence-only cells: four "
                    "<!--q:congruence_only.count@18=4-->\n", "r2.md")
    if not any("document says 4, computed 6" in b for b in bad):
        problems.append("RED 2: a wrong count was not caught")

    # RED 3: the right COUNT and the WRONG LIST.  This is the control the old
    # gate did not have, and the defect it let through.
    wrong = good_cells.replace("(40,21)", "(40,23)")
    bad, _, _ = run("congruence-only cells <!--q:congruence_only.cells@18=%s-->\n"
                    % wrong, "r3.md")
    if not any("congruence_only.cells@18" in b for b in bad):
        problems.append("RED 3: a wrong cell list of the right length was not "
                        "caught -- this is the exact defect the gate exists for")

    # RED 4: the prose escape hatch used to smuggle a number.
    bad, _, _ = run("the residual band on row 40 is 4 cells "
                    "<!--q:prose-->\n", "r4.md")
    if not any("states a number" in b for b in bad):
        problems.append("RED 4: `q:prose` on a line with a number was accepted")

    # RED 5: a marker naming a fact that is not computed.
    bad, _, _ = run("congruence-only <!--q:invented.count@18=6-->\n", "r5.md")
    if not any("does not compute" in b for b in bad):
        problems.append("RED 5: a marker naming an unknown fact was accepted")

    # RED 6: vacuity.  A document set with no residual claims at all must FAIL,
    # not pass -- otherwise a broken trigger pattern reads as a clean repo.
    bad, _, trig = run("nothing about this subject at all\n", "r6.md")
    if not any(b.startswith("VACUOUS") for b in bad):
        problems.append("RED 6: an empty scan reported clean instead of vacuous")

    # RED 7: Q1 and Q2 must not be interchangeable -- if they ever compute the
    # same list at the same height, the gate cannot tell a conflation apart and
    # the whole point of separating them is gone.
    if F["congruence_only.cells@18"] == F["row40_residual.cells@18"]:
        problems.append("RED 7: Q1 and Q2 coincide at H=18; the gate can no "
                        "longer distinguish the two quantities")

    # GREEN 2: a table header that names row 40 and states no count may declare
    # prose.  If this stops passing the hatch has become unusable and every
    # header in the repo will be forced to carry a fake marker.
    bad, checked, _ = run("| after | closes outright | row 40's residual band |"
                          " <!--q:prose-->\n", "ok2.md")
    if bad or checked != 1:
        problems.append("GREEN 2: `q:prose` on a row-40 table header was "
                        "rejected (%s)" % bad)

    # RED 11: a triggered table header must pull its body rows in.  The header
    # is where the word "residual" is; the body is where the numbers are.
    bad, _, trig = run("| after | row 40's residual band | <!--q:prose-->\n"
                       "|---|---|\n"
                       "| Ticker Tape | 3 cells |\n", "r11.md")
    if trig != 2 or not any("r11.md:3" in b for b in bad):
        problems.append("RED 11: a table body row under a triggered header was "
                        "not checked (triggers=%d, %s)" % (trig, bad))

    # RED 12: the range shorthand must be checked as hard as an explicit list.
    bad, checked, _ = run("row 40's residual band "
                          "<!--q:row40_residual.cells@18=T(40,19)..T(40,23)-->\n",
                          "g4.md")
    if bad or checked != 1:
        problems.append("GREEN 4: a correct range shorthand was rejected (%s)"
                        % bad)
    bad, _, _ = run("row 40's residual band "
                    "<!--q:row40_residual.cells@18=T(40,19)..T(40,24)-->\n",
                    "r12.md")
    if not any("row40_residual.cells@18" in b for b in bad):
        problems.append("RED 12: a range shorthand with a wrong endpoint was "
                        "not caught")

    # RED 13 / GREEN 5: prose wraps.  A marker on the continuation line must
    # answer a trigger on the line above it, and a paragraph with no marker
    # anywhere must still fail.
    bad, checked, trig = run("six congruence-only cells remain, and the\n"
                             "list is <!--q:congruence_only.count@18=6-->\n",
                             "g5.md")
    if bad or checked != 1 or trig != 1:
        problems.append("GREEN 5: a marker on the wrapped continuation line was "
                        "not seen (%s, checked=%d)" % (bad, checked))
    bad, _, _ = run("six congruence-only cells remain, and the\nlist is here\n",
                    "r13.md")
    if not any("no `<!--q:" in b for b in bad):
        problems.append("RED 13: an unmarked wrapped paragraph was not caught")

    # RED 14: a marker in one bullet must not excuse the next bullet.
    bad, _, trig = run("- six congruence-only cells "
                       "<!--q:congruence_only.count@18=6-->\n"
                       "- the residual band on row 40 is 4 cells\n", "r14.md")
    if trig != 2 or not any("r14.md:2" in b for b in bad):
        problems.append("RED 14: a marker in one bullet excused the next "
                        "(triggers=%d, %s)" % (trig, bad))

    # RED 15: markdown emphasis inside the trigger phrase must not hide it.
    # This one was live -- HANDOFF.md wrote "**only** the mod-4 congruence" and
    # the pattern walked past it.  Fail-open, so it gets its own control.
    bad, _, trig = run("cells carrying **only** the mod-4 congruence "
                       "drop 11 -> 6\n", "r15.md")
    if trig != 1 or not any("no `<!--q:" in b for b in bad):
        problems.append("RED 15: emphasis inside the trigger phrase hid the "
                        "claim (triggers=%d)" % trig)

    h = PT.MOTLEY_H
    want = F["congruence_only.cells@%d" % h]

    # RED 8: the peer generator disagreeing on the count.
    if not any("states 4 congruence-only" in b
               for b in run_peer(4, want)):
        problems.append("RED 8: a wrong count in %s was not caught"
                        % GENERATED_PEER)

    # RED 9: the peer generator with the right count and the wrong list.
    swapped = [c if c != (40, 21) else (40, 23) for c in want]
    if not any("lists" in b for b in run_peer(len(want), swapped)):
        problems.append("RED 9: a wrong cell list in %s was not caught"
                        % GENERATED_PEER)

    # RED 10: the peer generator's wording moved, so the parse finds nothing.
    # Going blind must fail, not pass.
    blind = run_peer(None, None)
    if not any("went blind" in b for b in blind) or len(blind) != 2:
        problems.append("RED 10: an unparseable %s reported clean instead of "
                        "blind (%s)" % (GENERATED_PEER, blind))

    # GREEN 3: the peer generator agreeing.
    if run_peer(len(want), want):
        problems.append("GREEN 3: an agreeing %s did not pass"
                        % GENERATED_PEER)

    if problems:
        print("residual-cells selftest FAILED:")
        for p in problems:
            print("  " + p)
        return 1
    print("residual-cells selftest ok: 5 green controls, 15 RED controls, all fired")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    F = facts()
    if args.check:
        docs = tracked_docs()
        bad, checked, trig = scan(F, docs, verbose=args.verbose)
        bad += check_peer(F)
        print("residual-cells gate: %d claims in %d tracked documents, "
              "%d verified; %s cross-checked"
              % (trig, len(docs), checked, GENERATED_PEER))
        if bad:
            print("\nresidual-cells gate RED:")
            for b in bad:
                print("  " + b)
            return 1
        print("residual-cells gate GREEN")
        return 0
    write_note(F)
    print("wrote %s" % OUT.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
