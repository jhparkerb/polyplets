#!/usr/bin/env python3
"""Gate MAKEFILE-WIRING: no gate goes unrun, at either of two surfaces.

The Makefile's own GATE_TARGETS comment says it: "A `gate-foo:` recipe that
never reaches GATE_TARGETS is a check `make gates` does not run, which is the
meta-version of the failure two of this week's commits fixed." It then asks for
a lint with an allowlist for the deliberate exclusions. This is that lint.

It was written after successor row S-A5 (results/undertow-review-queue.md)
found FOUR unwired gates at once -- the whole Severance family -- three of
which had no reason to be out beyond nobody having wired them. A green suite
that silently skips four real checks is worse than a red one.

There are TWO surfaces, and the second is the one that actually bit us. The
first is recipe-vs-GATE_TARGETS. The second is SCRIPT-vs-Makefile: the four
Severance gates were not recipes missing from GATE_TARGETS -- they had no
recipe at all, so a recipe-level check sees nothing wrong and passes. A gate
script that the Makefile has never heard of is the quieter failure and the more
common one. Checking only the first surface would have passed the tree on the
day S-A5 was filed; extending to the second turned up a fifth, tests/
gate_modp.py, live and green and unrun since August.

Ways to be red, all fail-closed:

  1. A gate-* recipe exists that is neither in GATE_TARGETS nor in EXCUSED.
  2. A GATE_TARGETS entry names a target with no recipe (typo, or a rename that
     moved the recipe and left the reference).
  3. EXCUSED names a gate whose recipe no longer exists. An allowlist that
     outlives what it excuses is how an exclusion becomes permanent by
     accident, so a stale entry is red, not ignored.
  4. A gate script on disk is named nowhere in the Makefile and is not in
     EXCUSED_SCRIPTS.
  5. EXCUSED_SCRIPTS names a script that no longer exists, or one the Makefile
     does now reference.

Every EXCUSED entry carries its reason in this file, in the open, where the
next person deciding whether to wire it can read why it was not.

Usage:
  python3 tests/gate_makefile_wiring.py             # GREEN if consistent
  python3 tests/gate_makefile_wiring.py --selftest  # RED controls

Exit 0 = GATE GREEN; anything else = red.
"""

import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAKEFILE = os.path.join(ROOT, "Makefile")

# Deliberate exclusions. Key = target, value = why it is not in GATE_TARGETS.
# Adding an entry here is a decision to make in the open, not a way to quiet
# this gate: the reason is printed on every green run.
EXCUSED = {
    "gate-motley-par":
        "needs build/motley_par, which needs -fopenmp: it does not compile on "
        "gympie (Apple clang, no libomp) or dalby (no omp.h), so no automatic "
        "chain can carry it without failing on two of the three boxes. Run by "
        "hand on ayr. The reason used to read 'lives with the ns-gates', which "
        "ns-gates has never done -- an allowlist reason that was not true",
    "gate-notary":
        "runs `lake build` over the Lean development, which needs the Lean "
        "toolchain and vendored Mathlib present and is minutes even warm; "
        "the Lean tree has its own build discipline (docs/lean-environment.md)",
}


# Where gate scripts live, and what a gate script looks like. Kept broad on
# purpose: a gate that hides from the glob is a gate that hides from the lint.
SCRIPT_GLOBS = ("tests/gate_*.py", "experiments/*_gate.py",
                "experiments/*/*_gate.py",          # tristruct/, skeletonkey/, ...
                "scripts/*gate*.sh", "scripts/*/*gate*.sh")

# Scripts that are deliberately not run by the Makefile, with the reason.
EXCUSED_SCRIPTS = {
    "scripts/lastditch/h18_release_gate.sh":
        "not a suite gate -- a one-shot remote release check from the last-ditch "
        "campaign, run by hand on a specific box against a specific build. Kept "
        "as the campaign's run record",
    "scripts/lastditch/gate_sizes_wrap.sh":
        "not a gate -- the argv wrapper that hands gate-motley-par a census "
        "sizes file so it exercises the release path. It is invoked BY that "
        "gate's command line, not by the Makefile",
    "scripts/profile_gates.sh":
        "not a gate -- it is the PROFILER for the gate suite, and it runs "
        "`make gates` itself. Wiring it into the Makefile would make `make "
        "gates` recurse into itself; it is run by hand when a push feels slow",
    "scripts/dir4_perim_gate_red_check.sh":
        "not a gate -- it is the manual RED demonstration FOR gate-dir4-perim-"
        "alg, and it deliberately damages its own input file to prove the gate "
        "stops. Running it inside the suite would be running a fault injector "
        "in parallel with the gate it injects into",
}


# The `gates` recipe names the RED gate(s) by sed-ing its own log. That sed has
# been wrong twice: once because GNU make prints "[Makefile:2: gate-foo]" where
# 3.81 prints "[gate-foo]", and a red run on both Linux boxes printed an EMPTY
# list; and now the targets are timed-gate-foo, so there is a third format. A
# parser with no test is how both happened, so this runs the REAL pattern --
# lifted out of the Makefile, not a copy -- over every format it must handle.
SED_EXPR = re.compile(r"named=\$\$\(sed -n '(.*?)' \$\(GATELOG\)")

RED_LINE_CASES = [
    ("make: *** [gate-tma] Error 1", "gate-tma"),
    ("make[1]: *** [Makefile:2: gate-tma] Error 1", "gate-tma"),
    ("make: *** [timed-gate-tma] Error 1", "gate-tma"),
    ("make[1]: *** [Makefile:126: timed-gate-severance-w1] Error 1",
     "gate-severance-w1"),
    # a red PREREQUISITE names no gate, and must not invent one
    ("make: *** [build/g2] Error 1", None),
    ("ok   H holes-sum square8 n<=9", None),
]


def check_red_naming(text):
    """Failures in the RED-gate namer. Empty list = green."""
    m = SED_EXPR.search(text)
    if not m:
        return ["cannot find the RED-gate sed in the `gates` recipe -- if it "
                "was rewritten, this lint has to be rewritten with it"]
    expr = m.group(1)
    bad = []
    for line, want in RED_LINE_CASES:
        out = subprocess.run(["sed", "-n", expr], input=line + "\n",
                             capture_output=True, text=True).stdout.strip()
        got = out or None
        if got != want:
            bad.append(f"RED-gate namer on {line!r}: got {got!r}, want {want!r}")
    return bad


# One spelling of the DEPS_<gate> line, used by both checks below.
DEPS_RE = re.compile(r"^DEPS_((?:ns-)?gate-[A-Za-z0-9_-]+)\s*=\s*"
                     r"((?:.*\\\n)*.*)$", re.M)


def recipe_lines(text, gate):
    """The tab-indented recipe lines of one target."""
    body, seen = [], False
    for line in text.splitlines():
        if re.match(rf"^{re.escape(gate)}\s*:", line):
            seen = True
            continue
        if seen:
            if line.startswith("\t"):
                body.append(line)
            elif line.strip():
                break
    return body


def check_gate_deps(text):
    """A DECLARED gate must list its own script among its inputs.

    `make gates` skips a declared gate while its stamp is newer than everything
    in DEPS_<gate>. Leaving the gate's own script out of that list means editing
    the gate does not re-run it -- a green suite that silently skipped the check
    you just changed. Undeclared gates always run, so this only has to police
    the declarations that exist.
    """
    bad = []
    for m in DEPS_RE.finditer(text):
        gate, deps = m.group(1), m.group(2).replace("\\\n", " ")
        body = recipe_lines(text, gate)
        # not [\w/]+ -- that swallows the leading slash of "./scripts/foo.sh"
        scripts = set(re.findall(r"\w[\w/]*\.(?:py|sh)", "\n".join(body)))
        missing = sorted(x for x in scripts if x not in deps)
        if missing:
            bad.append(f"DEPS_{gate} does not list the script its recipe runs, "
                       f"so editing it would not re-run the gate: "
                       + ", ".join(missing))
    return bad


# Where a gate script can import a repo-local module from.
_IMPORT_DIRS = ("tests", "experiments", "oracle", "scripts", "paper", "sym")


def _local_imports(path, seen):
    """Transitive repo-local modules imported by `path`, as repo-relative paths."""
    import ast as _ast
    if path in seen or not os.path.exists(path):
        return
    seen.add(path)
    try:
        tree = _ast.parse(open(path).read())
    except SyntaxError:
        return
    names = set()
    for node in _ast.walk(tree):
        if isinstance(node, _ast.Import):
            names.update(a.name.split(".")[0] for a in node.names)
        elif isinstance(node, _ast.ImportFrom) and node.level == 0 and node.module:
            names.add(node.module.split(".")[0])
    for name in names:
        for d in _IMPORT_DIRS:
            cand = os.path.join(ROOT, d, name + ".py")
            if os.path.exists(cand):
                yield os.path.relpath(cand, ROOT)
                yield from _local_imports(cand, seen)


def check_gate_imports(text):
    """A declared gate must list every repo-local module its script imports.

    DEPS_<gate> is what makes the gate skip. `tests/common.py` is imported by
    nearly every gate script and named in none of their recipes, so a
    hand-written dependency list is exactly where it goes missing -- and then
    editing common.py stops re-running the gates that use it. Computed, not
    trusted.
    """
    bad = []
    for m in DEPS_RE.finditer(text):
        gate, deps = m.group(1), m.group(2).replace("\\\n", " ")
        for script in re.findall(r"[\w/]+\.py", deps):
            for mod in _local_imports(os.path.join(ROOT, script), set()):
                if mod not in deps:
                    bad.append(f"DEPS_{gate} omits {mod}, which {script} "
                               f"imports -- editing it would not re-run the gate")
    return sorted(set(bad))


def _recipe_sources(text, body):
    """The repo files a recipe actually executes.

    Scripts appear by name. A binary does not, so it is resolved through its own
    build rule to the source it is built from -- which is where a --deep flag
    would live.
    """
    out = set()
    for tok in re.findall(r"\.?/?([\w][\w/.-]*\.(?:py|sh))", "\n".join(body)):
        out.add(tok)
    for binary in re.findall(r"\b(build/[\w/]+)", "\n".join(body)):
        rule = re.search(rf"^{re.escape(binary)}\s*:\s*(\S+)", text, re.M)
        if rule:
            out.add(rule.group(1))
    return out


def check_deep_wiring(text):
    """A gate whose code reads --deep must have $(GATE_DEEP) on its recipe.

    The push-tier/deep-tier split is carried from the recipe to the gate by
    $(GATE_DEEP), and that transport is a wiring surface like any other: a gate
    that sniffs --deep but is never passed it runs at PUSH depth under
    `make gates-deep`, while the deep tier reports itself green at full size.
    That is not hypothetical -- gate-king-grid and gate-multidirected both
    landed that way, in the same change that added the tier.
    """
    # A file that merely MENTIONS --deep (this lint does, in its own controls)
    # is not a consumer of it. Match the three ways a gate actually reads it.
    consumes = re.compile(r'"--deep"\s+in\s+sys\.argv'      # python
                          r'|^\s*--deep\)'                    # shell case arm
                          r'|argv\[\w+\],\s*"--deep"'        # C++ strcmp
                          r'|==\s*"--deep"', re.M)             # C++ string compare
    bad = []
    for gate in sorted(set(re.findall(r"^((?:ns-)?gate-[A-Za-z0-9_-]+)\s*:",
                                      text, re.M))):
        body = recipe_lines(text, gate)
        if not body:
            continue
        recipe = "\n".join(body)
        for src in sorted(_recipe_sources(text, body)):
            path = os.path.join(ROOT, src)
            if not os.path.exists(path):
                continue
            if not consumes.search(open(path, errors="ignore").read()):
                continue
            if "$(GATE_DEEP)" not in recipe:
                bad.append(f"{gate} runs {src}, which reads --deep, but its "
                           f"recipe never passes $(GATE_DEEP) -- "
                           f"`make gates-deep` would run it at push depth")
            break
    return bad


# The ns-gate-* family is carried by two aggregate lists rather than by
# GATE_TARGETS, and BOTH of this lint's original surfaces missed it: parse()
# anchors on ^gate-, and a binary-backed ns gate has no script for the script
# surface to see. So an ns-gate-foo recipe dropped from ns-gates and
# ns-gate-fast would go unrun AND unlinted -- the same shape as the four
# Severance gates, in the one family the lint could not see.
NS_AGGREGATES = ("ns-gates", "ns-gate-fast")

# Deliberate exclusions in the ns family. Separate from EXCUSED because that
# one is checked for staleness against gate-* recipes only.
EXCUSED_NS = {
    "ns-gate-resume":
        "the AC-1 long-run gate: ./build/ns/driver1 --compare at maxn 18, "
        "hours to days depending on box, invoked by hand (documented at its "
        "recipe). No aggregate can carry a gate measured in days",
}


def check_ns_wiring(text, excused=EXCUSED_NS):
    """Every ns-gate-* recipe is carried by an aggregate, and vice versa."""
    recipes = set(re.findall(r"^(ns-gate-[A-Za-z0-9_-]+)\s*:", text, re.M))
    recipes -= set(NS_AGGREGATES)

    carried = set()
    m = re.search(r"^ns-gates:\s*((?:.*\\\n)*.*)$", text, re.M)
    if m:
        carried |= set(m.group(1).replace("\\\n", " ").split())
    m = re.search(r"^NS_FAST_TARGETS\s*=\s*((?:.*\\\n)*.*)$", text, re.M)
    if m:
        carried |= set(m.group(1).replace("\\\n", " ").split())

    bad = []
    unwired = sorted(r for r in recipes
                     if r not in carried and r not in excused)
    if unwired:
        bad.append("ns-gate recipes carried by neither ns-gates nor "
                   "ns-gate-fast (a check nothing runs): " + ", ".join(unwired))
    stale = sorted(x for x in excused if x not in recipes)
    if stale:
        bad.append("EXCUSED_NS names ns-gates that no longer exist: "
                   + ", ".join(stale))
    both = sorted(x for x in excused if x in carried)
    if both:
        bad.append("EXCUSED_NS names ns-gates that ARE carried -- the excuse "
                   "is obsolete: " + ", ".join(both))
    # and the other direction: an aggregate naming something with no recipe
    all_recipes = recipes | set(re.findall(r"^(gate-[A-Za-z0-9_-]+)\s*:",
                                           text, re.M))
    orphan = sorted(t for t in carried if t not in all_recipes)
    if orphan:
        bad.append("an ns aggregate names targets with no recipe: "
                   + ", ".join(orphan))
    return bad


def check_prereqs(text):
    """GATE_PREREQS must be a superset of every gate-*: prerequisite.

    `make gates` builds GATE_PREREQS once, then runs a sub-make per gate to time
    it. A binary that is a prerequisite of two gates but missing from
    GATE_PREREQS would be built by two sub-makes at once, into the same output
    file. A superset can only build something unnecessary; a subset is a race.
    """
    bad = []
    for pv, tv in (("GATE_PREREQS", "GATE_TARGETS"),
                   ("NS_FAST_PREREQS", "NS_FAST_TARGETS")):
        bad += _prereqs_one(text, pv, tv)
    return bad


def _prereqs_one(text, prereq_var, target_var):
    m = re.search(rf"^{prereq_var}\s*=\s*((?:.*\\\n)*.*)$", text, re.M)
    if not m:
        return [f"no {prereq_var} assignment found in Makefile"]
    declared = set(m.group(1).replace("\\\n", " ").split())
    # Only the WIRED gates matter: the sweep runs exactly the target list, so an
    # excused gate's binary (build/motley_par) is never built concurrently and
    # listing it here would just make every push compile something nothing runs.
    w = re.search(rf"^{target_var}\s*=\s*((?:.*\\\n)*.*)$", text, re.M)
    wired = set(w.group(1).replace("\\\n", " ").split()) if w else set()
    needed = set()
    for line in text.splitlines():
        g = re.match(r"^((?:ns-)?gate-[A-Za-z0-9_-]+)\s*:(.*)$", line)
        if g and g.group(1) in wired:
            needed.update(g.group(2).split())
    # $(if $(GMP_LDFLAGS),...) tokens appear in both sides verbatim; compare
    # only the build/ artifacts, which is what can actually be raced.
    missing = sorted(t for t in needed
                     if t.startswith("build/") and t not in declared)
    if missing:
        return [f"{prereq_var} is missing gate prerequisites -- the stamp "
                f"comparison would see a stale binary: " + ", ".join(missing)]
    return []


def parse(text):
    """(recipes, wired) from Makefile source."""
    recipes = set(re.findall(r"^(gate-[A-Za-z0-9_-]+)\s*:", text, re.M))
    m = re.search(r"^GATE_TARGETS\s*=\s*(.*)$", text, re.M)
    if not m:
        raise SystemExit("GATE RED: no GATE_TARGETS assignment found in Makefile")
    wired = set(m.group(1).split())
    return recipes, wired


def scripts_on_disk(root):
    import glob as _g
    out = set()
    for pat in SCRIPT_GLOBS:
        for p in _g.glob(os.path.join(root, pat)):
            out.add(os.path.relpath(p, root))
    return out


def recipe_text(text):
    """Only the RECIPE lines of a Makefile -- the tab-indented commands.

    Searching the whole file would count a script named in a COMMENT as run,
    and that is not hypothetical: the pre-fix Makefile named
    severance_w3_depth5_gate.py in a comment explaining why it was NOT wired.
    A substring check over the raw text reads that as coverage and passes the
    exact gate the comment says is unrun.
    """
    return "\n".join(l for l in text.splitlines() if l.startswith("\t"))


def check_scripts(scripts, text, excused):
    """Failures on the script surface. Empty list = green."""
    text = recipe_text(text)
    bad = []
    unref = sorted(s for s in scripts
                   if os.path.basename(s) not in text and s not in excused)
    if unref:
        bad.append("gate scripts the Makefile never names (written, green, and "
                   "never run): " + ", ".join(unref))
    stale = sorted(s for s in excused if s not in scripts)
    if stale:
        bad.append("EXCUSED_SCRIPTS names scripts that no longer exist: "
                   + ", ".join(stale))
    obsolete = sorted(s for s in excused
                      if s in scripts and os.path.basename(s) in text)
    if obsolete:
        bad.append("EXCUSED_SCRIPTS names scripts the Makefile DOES reference "
                   "-- the excuse is obsolete: " + ", ".join(obsolete))
    return bad


def check(recipes, wired, excused):
    """Return a list of failure strings. Empty list = green."""
    bad = []
    unwired = sorted(recipes - wired - set(excused))
    if unwired:
        bad.append(
            "gate recipes neither wired nor excused (a check `make gates` "
            "never runs): " + ", ".join(unwired))
    orphan = sorted(wired - recipes)
    if orphan:
        bad.append(
            "GATE_TARGETS names targets with no recipe: " + ", ".join(orphan))
    stale = sorted(set(excused) - recipes)
    if stale:
        bad.append(
            "EXCUSED names gates that no longer exist (stale allowlist): "
            + ", ".join(stale))
    both = sorted(set(excused) & wired)
    if both:
        bad.append(
            "EXCUSED names gates that ARE wired -- the excuse is obsolete and "
            "misleading: " + ", ".join(both))
    return bad


def main():
    text = open(MAKEFILE).read()
    recipes, wired = parse(text)
    scripts = scripts_on_disk(ROOT)
    bad = (check(recipes, wired, EXCUSED)
           + check_scripts(scripts, text, EXCUSED_SCRIPTS)
           + check_red_naming(text)
           + check_prereqs(text)
           + check_gate_deps(text)
           + check_gate_imports(text)
           + check_deep_wiring(text)
           + check_ns_wiring(text))
    if bad:
        for b in bad:
            print("  RED: " + b)
        raise SystemExit("GATE RED: Makefile gate wiring is inconsistent")
    print(f"  recipes: {len(recipes)} gate-* -- {len(recipes & wired)} wired, "
          f"{len(EXCUSED)} excused, 0 unaccounted")
    print(f"  scripts: {len(scripts)} on disk -- "
          f"{len(scripts) - len(EXCUSED_SCRIPTS)} named by the Makefile, "
          f"{len(EXCUSED_SCRIPTS)} excused, 0 unaccounted")
    for t, why in sorted(EXCUSED.items()):
        print(f"  excused (recipe): {t} -- {why}")
    for t, why in sorted(EXCUSED_NS.items()):
        print(f"  excused (ns):     {t} -- {why}")
    for t, why in sorted(EXCUSED_SCRIPTS.items()):
        print(f"  excused (script): {t} -- {why}")
    print("  deep-tier: every gate that reads --deep is passed $(GATE_DEEP)")
    print("  ns-wiring: every ns-gate-* recipe is carried by an aggregate")
    print("  prereqs:   GATE_PREREQS and NS_FAST_PREREQS each cover their\n             own targets' build/ prerequisites")
    print("  gate-deps: every DECLARED gate lists its own script and every\n             repo-local module that script imports")
    print(f"  red-namer: {len(RED_LINE_CASES)} bracket formats parsed "
          "correctly by the Makefile's own sed")
    print("GATE GREEN")


def selftest():
    # Same rule as the script surface below: every excused gate must exist on
    # the synthetic tree, or adding an excuse turns the baseline red.
    recipes = {"gate-a", "gate-b"} | set(EXCUSED)
    wired = {"gate-a", "gate-b"}
    ok = check(recipes, wired, EXCUSED)
    assert not ok, f"selftest baseline should be green, got {ok}"
    print("  [baseline] wired + excused, nothing unaccounted -> green")

    # RED 1: an unwired, unexcused recipe.
    bad = check(recipes | {"gate-orphan"}, wired, EXCUSED)
    assert any("never runs" in b for b in bad), bad
    print("  [RED 1] unwired gate-orphan caught")

    # RED 2: GATE_TARGETS naming a target with no recipe.
    bad = check(recipes, wired | {"gate-typo"}, EXCUSED)
    assert any("no recipe" in b for b in bad), bad
    print("  [RED 2] GATE_TARGETS entry with no recipe caught")

    # RED 3: a stale allowlist entry.
    bad = check(recipes, wired, dict(EXCUSED, **{"gate-gone": "removed"}))
    assert any("stale allowlist" in b for b in bad), bad
    print("  [RED 3] stale EXCUSED entry caught")

    # RED 4: an excuse for a gate that is in fact wired.
    bad = check(recipes, wired | {"gate-motley-par"}, EXCUSED)
    assert any("obsolete and misleading" in b for b in bad), bad
    print("  [RED 4] excuse for an already-wired gate caught")

    # --- script surface ---
    text = "gate-x:\n\tpython3 tests/gate_seen.py\n"
    # Every excused script must be on the synthetic disk, or the baseline goes
    # red on "no longer exists" the moment an excuse is added -- which is how
    # this selftest broke the first time a second entry landed.
    scr = {"tests/gate_seen.py"} | set(EXCUSED_SCRIPTS)
    ok = check_scripts(scr, text, EXCUSED_SCRIPTS)
    assert not ok, f"script baseline should be green, got {ok}"
    print("  [baseline] script named + script excused -> green")

    # RED 5: the failure that actually happened -- a gate script with no recipe
    # anywhere. A recipe-level check alone cannot see this.
    bad = check_scripts(scr | {"experiments/severance_w3_gate.py"}, text,
                        EXCUSED_SCRIPTS)
    assert any("never names" in b for b in bad), bad
    print("  [RED 5] gate script with no Makefile recipe caught "
          "(the S-A5 failure mode)")

    # RED 6: stale script excuse.
    bad = check_scripts(scr, text, dict(EXCUSED_SCRIPTS,
                                        **{"scripts/gone.sh": "removed"}))
    assert any("no longer exist" in b for b in bad), bad
    print("  [RED 6] stale EXCUSED_SCRIPTS entry caught")

    # RED 7: an excuse for a script the Makefile does reference.
    bad = check_scripts(scr, text + "\n\tbash scripts/dir4_perim_gate_red_check.sh\n",
                        EXCUSED_SCRIPTS)
    assert any("obsolete" in b for b in bad), bad
    print("  [RED 7] excuse for a referenced script caught")

    # RED 8: the namer must be able to FAIL. A pattern that anchors on the
    # bare "[gate-" -- the one that was live until the Linux boxes caught it --
    # has to be reported wrong by this check, or the check is decoration.
    stale = ("named=$$(sed -n 's/^.*\\*\\*\\* \\[\\(gate-[a-z0-9-]*\\)\\] "
             "Error.*/    \\1/p' $(GATELOG)")
    bad = check_red_naming(stale)
    assert any("Makefile:2" in b or "timed-gate" in b for b in bad), bad
    print("  [RED 8] the pre-2026-08 sed, which missed GNU make's format, "
          "is caught")

    # RED 9: a gate prerequisite missing from GATE_PREREQS is the race.
    fake = ("GATE_PREREQS = build/a build/b\nGATE_TARGETS = gate-x\n"
            "NS_FAST_PREREQS =\nNS_FAST_TARGETS =\n"
            "gate-x: build/a build/zzz\n")
    bad = check_prereqs(fake)
    assert any("build/zzz" in b for b in bad), bad
    # ...and an EXCUSED gate's binary is not required, because `make gates`
    # never builds it.
    unwired = ("GATE_PREREQS = build/a\nGATE_TARGETS = gate-x\n"
               "NS_FAST_PREREQS =\nNS_FAST_TARGETS =\n"
               "gate-x: build/a\ngate-y: build/only_for_y\n")
    assert not check_prereqs(unwired), check_prereqs(unwired)
    print("  [RED 9] a gate prerequisite missing from GATE_PREREQS is caught")

    # RED 10: a declared gate whose deps omit its own script would never
    # re-run when that script is edited.
    fake = ("DEPS_gate-x = paper/a.tex\n"
            "gate-x:\n\tpython3 tests/gate_x.py\n")
    bad = check_gate_deps(fake)
    assert any("tests/gate_x.py" in b for b in bad), bad
    ok_case = ("DEPS_gate-x = paper/a.tex tests/gate_x.py\n"
               "gate-x:\n\tpython3 tests/gate_x.py\n")
    assert not check_gate_deps(ok_case), check_gate_deps(ok_case)
    print("  [RED 10] a declared gate that omits its own script is caught")

    # RED 11: a declared gate that omits a module its script imports.
    probe = "DEPS_gate-tma = tests/gate_tma.py\n"
    bad = check_gate_imports(probe)
    assert any("tests/common.py" in b for b in bad), bad
    print("  [RED 11] a declared gate that omits an imported module is caught")

    # RED 12: the hole this check was written for -- a gate whose script reads
    # --deep, whose recipe does not pass it. Uses a REAL script known to read
    # --deep, so the control cannot pass by the file simply being absent.
    probe = "gate-king-grid:\n\tpython3 tests/gate_king_grid.py\n"
    bad = check_deep_wiring(probe)
    assert any("gate-king-grid" in b for b in bad), bad
    ok_case = "gate-king-grid:\n\tpython3 tests/gate_king_grid.py $(GATE_DEEP)\n"
    assert not check_deep_wiring(ok_case), check_deep_wiring(ok_case)
    print("  [RED 12] a gate that reads --deep but is never passed it is caught")

    # RED 13: an ns-gate recipe carried by neither aggregate, and an aggregate
    # entry with no recipe. Neither of the original two surfaces could see the
    # ns family at all.
    base = ("ns-gates: ns-gate-a\nNS_FAST_TARGETS = ns-gate-b\n"
            "ns-gate-a:\n\ttrue\nns-gate-b:\n\ttrue\n")
    assert not check_ns_wiring(base, {}), check_ns_wiring(base, {})
    bad = check_ns_wiring(base + "ns-gate-lost:\n\ttrue\n", {})
    assert any("ns-gate-lost" in b for b in bad), bad
    bad = check_ns_wiring(base, {"ns-gate-gone": "removed"})
    assert any("no longer exist" in b for b in bad), bad
    bad = check_ns_wiring(base, {"ns-gate-a": "but it IS carried"})
    assert any("obsolete" in b for b in bad), bad
    bad = check_ns_wiring("ns-gates: ns-gate-typo\nNS_FAST_TARGETS =\n", {})
    assert any("no recipe" in b for b in bad), bad
    print("  [RED 13] unwired ns-gate, stale excuse, obsolete excuse, and an "
          "aggregate entry with no recipe -- all four caught")

    # And the real Makefile must parse -- a lint that cannot read its own
    # subject is not a lint.
    real = open(MAKEFILE).read()
    r, w = parse(real)
    assert r and w, "parsed no recipes or no GATE_TARGETS from the real Makefile"
    disk = scripts_on_disk(ROOT)
    assert len(disk) > 20, f"script glob found only {len(disk)} -- globs broken?"
    print(f"  [parse] real Makefile: {len(r)} recipes, {len(w)} wired, "
          f"{len(disk)} gate scripts on disk")
    print("GATE SELFTEST GREEN: 13/13 red controls fired")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
    else:
        main()
