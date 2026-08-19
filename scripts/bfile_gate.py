#!/usr/bin/env python3
"""Check every OEIS b-file artifact against banked primary data, fail-closed.

The submission artifacts are what get scrutinised, and until now they were
produced by scripts whose output nothing re-derived.  A wrong digit in a b-file
is the most embarrassing failure available to this project, and it is also the
cheapest to prevent: every one of these sequences is a function of data banked
elsewhere in the tree, so the b-file can simply be recomputed and compared.

    python3 scripts/bfile_gate.py             # check
    python3 scripts/bfile_gate.py --selftest  # RED controls, each must fire

What is checked, and against what:

  b006770   a(n), fixed polyplets       row sums of results/triangle.txt, AND
                                        the original OEIS terms in
                                        fixtures/b006770.txt on the overlap
  b030233   one-sided                   Burnside from results/sym_counts.txt
  b030222   free                        Burnside
  b030234   bilateral                   Burnside
  b030235   asymmetric                  free - bilateral
  b194596   free non-polyominoes        free - A000105 (fixtures/b000105.txt)
  all files                             format: one "n value" per line, n
                                        contiguous from the offset, values
                                        nonnegative integers, no duplicates

Burnside, with H the axis mirror and D the diagonal mirror:

    OneSided  = (Fixed + 2*R90 + R180) / 4
    Free      = (Fixed + 2*R90 + R180 + 2*H + 2*D) / 8
    Bilateral = (H + D) / 2
    Asym      = Free - Bilateral

The divisions must come out exact in integers; a non-integral quotient is a
failure, not a rounding question.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results"
FIXTURES = ROOT / "fixtures"

failures: list[str] = []
checks = 0
reds = 0


def ok(cond, msg):
    global checks
    checks += 1
    if not cond:
        failures.append(msg)


# TODO (deferred from the 2026-08-19 simplify checkpoint, too large for a
# cleanup pass): four scripts hand-roll the same whitespace-column parse over
# banked files -- this one, provenance_table.read_triangle, and the ls-files
# walks in tests/gate_citations.tracked_markdown and
# tests/gate_docs_index.tracked_docs. A shared module would have to sit above
# both scripts/ and tests/, and these are freshly validated gates, so the
# consolidation wants its own change rather than a drive-by.
def load_nv(path):
    """Parse 'n value' lines, skipping comments."""
    out = {}
    for ln in Path(path).read_text().splitlines():
        ln = ln.strip()
        if not ln or ln.startswith("#"):
            continue
        f = ln.split()
        if len(f) != 2:
            raise ValueError("%s: expected 'n value', got %r" % (path, ln))
        out[int(f[0])] = int(f[1])
    return out


def load_sym():
    sym = {}
    for ln in (RESULTS / "sym_counts.txt").read_text().splitlines():
        if not ln.strip() or ln.startswith("#"):
            continue
        f = ln.split()
        if f[0] == "dmirror_strip":
            continue
        sym.setdefault(f[0], {})[int(f[1])] = int(f[2])
    # dmirror33 extends dmirror32 and they agree on the overlap; check that
    # rather than assuming it, then merge.
    a, b = sym.get("dmirror32", {}), sym.get("dmirror33", {})
    ok(all(a[n] == b[n] for n in set(a) & set(b)),
       "dmirror32 and dmirror33 disagree on their overlap")
    sym["dmirror"] = dict(a)
    sym["dmirror"].update(b)
    return sym


def fixed_from_triangle():
    """a(n) as row sums of the T(n,H) triangle -- the assembly, not a copy."""
    a = {}
    for ln in (RESULTS / "triangle.txt").read_text().splitlines():
        if not ln.strip() or ln.startswith("#"):
            continue
        n, h, v = ln.split()
        a[int(n)] = a.get(int(n), 0) + int(v)
    return a


def derive(sym, fixed):
    r90, r180 = sym["r90"], sym["r180"]
    H, D = sym["hmirror"], sym["dmirror"]
    out = {"onesided": {}, "free": {}, "bilateral": {}, "asym": {}}
    for n in sorted(fixed):
        # r90 has no entries where no animal can be 90-degree symmetric; that
        # is a real zero, and every other type must be present or the term is
        # simply not derivable and is skipped rather than defaulted.
        if n not in r180:
            continue
        q = fixed[n] + 2 * r90.get(n, 0) + r180[n]
        if q % 4 == 0:
            out["onesided"][n] = q // 4
        else:
            failures.append("one-sided at n=%d is not divisible by 4" % n)
        if n in H and n in D:
            q8 = q + 2 * H[n] + 2 * D[n]
            if q8 % 8 == 0:
                out["free"][n] = q8 // 8
            else:
                failures.append("free at n=%d is not divisible by 8" % n)
            if (H[n] + D[n]) % 2 == 0:
                out["bilateral"][n] = (H[n] + D[n]) // 2
            else:
                failures.append("bilateral at n=%d is not divisible by 2" % n)
            if n in out["free"] and n in out["bilateral"]:
                out["asym"][n] = out["free"][n] - out["bilateral"][n]
    return out


def check_format(path):
    """b-file hygiene: contiguous n, positive values, no duplicates."""
    seen = []
    for ln in Path(path).read_text().splitlines():
        s = ln.strip()
        if not s or s.startswith("#"):
            continue
        f = s.split()
        ok(len(f) == 2, "%s: line %r is not 'n value'" % (path.name, s))
        if len(f) != 2:
            return
        n, v = int(f[0]), int(f[1])
        # Zero is legal and occurs: no asymmetric polyplet exists at n=1,2 and
        # no non-polyomino polyplet at n=1.  Negative is not.
        ok(v >= 0, "%s: negative value at n=%d" % (path.name, n))
        seen.append(n)
    ok(len(seen) == len(set(seen)), "%s: duplicate n" % path.name)
    ok(seen == list(range(seen[0], seen[0] + len(seen))),
       "%s: n is not contiguous from %d" % (path.name, seen[0] if seen else -1))


def compare(name, banked, derived, path):
    """Every term of the b-file must equal the re-derived value.

    Two further conditions, because equality on the overlap alone would pass a
    truncated or holed file:

      * a HOLE -- an n the derivation supports, below the file's own last term,
        that the file does not carry -- is a failure.
      * a SHORTFALL -- the derivation reaching further than the file -- is
        reported, not failed: the artifact is stale rather than wrong, and
        extending a staged submission is jasonp's call, not the gate's.
    """
    shared = sorted(set(banked) & set(derived))
    ok(shared, "%s: no overlap between the b-file and the derivation" % name)
    bad = [n for n in shared if banked[n] != derived[n]]
    ok(not bad, "%s: %d terms differ, first at n=%s (%s vs %s)"
       % (name, len(bad), bad[0] if bad else "-",
          banked.get(bad[0]) if bad else "-", derived.get(bad[0]) if bad else "-"))
    top = max(banked) if banked else 0
    holes = [n for n in derived if n < top and n not in banked]
    ok(not holes, "%s: derivable terms missing below the file's last (n=%s)"
       % (name, holes[:5]))
    shortfall = sorted(n for n in derived if n > top)
    beyond = [n for n in banked if n not in derived]
    return len(shared), beyond, shortfall


# The front page asserts a(40) in full, and until 2026-08-19 nothing re-derived
# it: verify_technical_report covers the manuscript, this gate covered the
# b-files, and the one number every visitor reads first was checked by nobody.
# Scoped to the top-level README deliberately. A tree-wide sweep would flag
# results/ns_a26/PROVENANCE.md, which quotes the WRONG a(26) on purpose --- it
# records the stale-binary near-miss --- so tree-wide wants an exemption
# mechanism, and the front page does not.
README_CLAIM_RE = re.compile(r"\ba\((\d+)\)\s*=\s*(\d{4,})")


def readme_claims(fixed, text=None):
    """Mismatches between the README's a(n) = ... assertions and the bank."""
    if text is None:
        text = (ROOT / "README.md").read_text()
    found, bad = 0, []
    for m in README_CLAIM_RE.finditer(text):
        n, claimed = int(m.group(1)), int(m.group(2))
        if n not in fixed:
            continue
        found += 1
        if claimed != fixed[n]:
            bad.append((n, claimed, fixed[n]))
    return found, bad


def run(mutate=None):
    """mutate: optional callable applied to the loaded b-files, for RED tests."""
    global failures, checks
    failures, checks = [], 0
    sym = load_sym()
    fixed = fixed_from_triangle()

    files = {
        "b006770": RESULTS / "b006770_upload.txt",
        "b030233": RESULTS / "b030233_upload.txt",
        "b030222": RESULTS / "b030222_upload.txt",
        "b030234": RESULTS / "b030234_upload.txt",
        "b030235": RESULTS / "b030235_upload.txt",
        "b194596": RESULTS / "b194596_upload.txt",
    }
    banked = {k: load_nv(p) for k, p in files.items() if p.exists()}
    for k, p in files.items():
        if p.exists():
            check_format(p)
    if mutate:
        mutate(banked)

    der = derive(sym, fixed)
    a105 = load_nv(FIXTURES / "b000105.txt")
    nonpoly = {n: der["free"][n] - a105[n]
               for n in der["free"] if n in a105}

    report = []
    for name, derived in (("b006770", fixed), ("b030233", der["onesided"]),
                          ("b030222", der["free"]), ("b030234", der["bilateral"]),
                          ("b030235", der["asym"]), ("b194596", nonpoly)):
        if name not in banked:
            continue
        shared, beyond, shortfall = compare(name, banked[name], derived,
                                            files[name])
        report.append((name, len(banked[name]), shared, len(beyond), shortfall))

    # The original OEIS terms are an outside check on a(n): the b-file must
    # agree with them everywhere they overlap.
    # The front page's own numbers, against the same row sums.
    found, bad = readme_claims(fixed)
    ok(found > 0, "README.md asserts no a(n) value the bank knows -- the "
                  "front page changed shape and this check went vacuous")
    ok(not bad, "README.md disagrees with the bank: %s"
       % ["a(%d) claims %d, bank has %d" % t for t in bad])

    orig = load_nv(FIXTURES / "b006770.txt")
    if "b006770" in banked:
        bad = [n for n in sorted(set(orig) & set(banked["b006770"]))
               if orig[n] != banked["b006770"][n]]
        ok(not bad, "b006770 disagrees with the original OEIS terms at %s" % bad[:3])
    return report


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    if args.selftest:
        global reds
        controls = [
            ("one digit changed in a(40)",
             lambda b: b["b006770"].__setitem__(40, b["b006770"][40] + 1)),
            ("a term dropped from the middle of the free b-file",
             lambda b: b["b030222"].pop(max(b["b030222"]) - 3)),
            ("bilateral and asymmetric swapped",
             lambda b: b.update({"b030234": b["b030235"],
                                 "b030235": b["b030234"]})),
        ]
        # Two synthetic controls for the README check: a wrong digit must be
        # caught, and a front page that stopped asserting anything must not
        # pass by having nothing left to check.
        fixed = fixed_from_triangle()
        n40 = fixed[max(fixed)]
        found, wrong = readme_claims(fixed, "a(%d) = %d\n" % (max(fixed), n40 + 1))
        print("  RED %-42s %s" % ("one digit changed in the README's a(n)",
                                  "FIRED" if wrong else "DID NOT FIRE"))
        vacuous, _ = readme_claims(fixed, "no claims here\n")
        print("  RED %-42s %s" % ("a README that asserts no a(n) at all",
                                  "FIRED" if vacuous == 0 else "DID NOT FIRE"))
        bad = []
        if not wrong:
            bad.append("readme wrong-digit control")
        if vacuous != 0:
            bad.append("readme vacuous control")
        for label, mut in controls:
            run(mutate=mut)
            fired = bool(failures)
            print("  RED %-42s %s" % (label, "FIRED" if fired else "DID NOT FIRE"))
            if not fired:
                bad.append(label)
        run()
        print("  clean run: %d checks, %d failures" % (checks, len(failures)))
        if bad or failures:
            print("SELFTEST FAILED")
            return 1
        print("selftest ok")
        return 0

    report = run()
    print("b-file gate: every uploaded term re-derived from banked data")
    stale = []
    for name, terms, shared, beyond, shortfall in report:
        extra = ", %d beyond the derivation's reach" % beyond if beyond else ""
        print("  %-9s %3d terms, %3d re-derived%s" % (name, terms, shared, extra))
        if shortfall:
            stale.append((name, shortfall))
    if stale:
        print("\n  STALE (derivable from banked data, absent from the artifact):")
        for name, ns in stale:
            print("    %-9s n = %s" % (name, ", ".join(map(str, ns))))
        print("  Not a gate failure -- the artifacts are staged for submission,"
              "\n  and extending one is jasonp's call. Regenerate with"
              " scripts/derive_related.py.")
    if failures:
        print("\nb-file gate RED: %d of %d checks failed" % (len(failures), checks))
        for f in failures:
            print("  " + f)
        return 1
    print("b-file gate GREEN (%d checks)" % checks)
    return 0


if __name__ == "__main__":
    sys.exit(main())
