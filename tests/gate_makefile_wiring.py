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
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAKEFILE = os.path.join(ROOT, "Makefile")

# Deliberate exclusions. Key = target, value = why it is not in GATE_TARGETS.
# Adding an entry here is a decision to make in the open, not a way to quiet
# this gate: the reason is printed on every green run.
EXCUSED = {
    "gate-motley-par":
        "needs build/motley_par and a few minutes; lives with the ns-gates "
        "rather than the fast suite (documented at its recipe)",
    "gate-notary":
        "runs `lake build` over the Lean development, which needs the Lean "
        "toolchain and vendored Mathlib present and is minutes even warm; "
        "the Lean tree has its own build discipline (docs/lean-environment.md)",
}


# Where gate scripts live, and what a gate script looks like. Kept broad on
# purpose: a gate that hides from the glob is a gate that hides from the lint.
SCRIPT_GLOBS = ("tests/gate_*.py", "experiments/*_gate.py", "scripts/*gate*.sh")

# Scripts that are deliberately not run by the Makefile, with the reason.
EXCUSED_SCRIPTS = {
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
    bad = check(recipes, wired, EXCUSED) + check_scripts(scripts, text,
                                                         EXCUSED_SCRIPTS)
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
    for t, why in sorted(EXCUSED_SCRIPTS.items()):
        print(f"  excused (script): {t} -- {why}")
    print("GATE GREEN")


def selftest():
    recipes = {"gate-a", "gate-b", "gate-motley-par", "gate-notary"}
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

    # And the real Makefile must parse -- a lint that cannot read its own
    # subject is not a lint.
    real = open(MAKEFILE).read()
    r, w = parse(real)
    assert r and w, "parsed no recipes or no GATE_TARGETS from the real Makefile"
    disk = scripts_on_disk(ROOT)
    assert len(disk) > 20, f"script glob found only {len(disk)} -- globs broken?"
    print(f"  [parse] real Makefile: {len(r)} recipes, {len(w)} wired, "
          f"{len(disk)} gate scripts on disk")
    print("GATE SELFTEST GREEN: 7/7 red controls fired")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
    else:
        main()
