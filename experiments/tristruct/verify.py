"""verify.py -- automatic verifier for T(n,H) structure candidates.

Implements the team brief's independence rule in exact integer arithmetic:

  * FIT LOW: the candidate's fit() callable is handed a FitView exposing ONLY
    rows n <= fit_max_n (default 22, hard ceiling 39; row 40 is never
    exposed). Reading above it raises and the candidate is culled
    (FIT-REGION-VIOLATION). fit_max_n > 22 is allowed only with a declared
    reason and is flagged FIT-REGION-EXTENDED (lower independence score).
  * PREDICT HIGH: predictions are scored on the region's cells with
    fit_max_n < n <= 39, held out BY n, never randomly. Per-row exact
    match/mismatch and the first failing row are reported.
  * ROW 40 SEPARATE: cells with n = 40 are scored and reported as the FINAL
    PREDICTION; they never enter fitting and never affect the verdict.

Culls (a culled candidate is out, whatever else it does):
  FIT-REGION-VIOLATION  fit() read a holdout row
  FIT-ERROR / PREDICT-ERROR  the callables crashed
  FIT-INCONSISTENT      the relation fails on its own fit region
  NO-HOLDOUT            region has no cells with fit_max_n < n <= 39
  FITTED-NOT-TESTED     n_params >= holdout cells matched: as many knobs as
                        cells, so nothing was predicted
  KNOWN-COINCIDENT(x)   predictions on every holdout cell are implied by an
                        already-banked relation from known.py (scores zero
                        per the brief)
  VALUE-INSENSITIVE     boolean check that still passes when the target value
                        is perturbed, on every holdout cell: a tautology with
                        zero checking power

Bits of check ("bits of independent check on a(40)" per the brief; log2 of
the a-priori probability that a wrong count passes):
  congruence mod m: log2(m) per cell. bits_row40 = log2(m) * (row-40 cells in
      region); bits_holdout = log2(m) * holdout cells matched. A bits_claimed
      exceeding log2(m) is overridden and flagged BITS-INFLATED. CAVEAT
      (documented, not solved here): summing over cells assumes the cells fail
      independently under the error model; refuters judge correlated cells.
  value: an exact-value prediction has no defensible a-priori pass
      probability without an error model, so bits are reported as None
      ("unquantified") unless the candidate supplies bits_claimed AND
      bits_justification, which are passed through flagged BITS-UNVERIFIED
      for the refuters. We refuse to invent a number.
  boolean: bits_claimed used only if bits_justification present, flagged
      BITS-UNVERIFIED; otherwise None and NO-BITS-JUSTIFIED.

Usage:
  python3 verify.py candidates/foo.py [bar.py ...]     # verify proposer files
  python3 verify.py --selftest                          # loader + known checks

Exit codes: 0 = ran (verdicts in the table); 1 = data validation failure;
2 = candidate file/schema error. Library entry point: verify_candidate(cand,
tri) -> report dict (used by sweep.py and test_verify.py).
"""

import math
import sys

from schema import (Candidate, FitView, FitRegionViolation, PeekViolation,
                    PredictContext, DEFAULT_FIT_MAX_N, HOLDOUT_MAX_N,
                    load_candidates)
import known as known_mod

NMAX = 40


def _actual(tri, n, H):
    return tri.rowsum(n) if H is None else tri.cell(n, H)


def _prov_count(tri, cells):
    """'x/y real-sweep' over concrete cells; rowsum cells count as aggregate."""
    if not cells:
        return "0/0"
    real = tot = 0
    for n, H in cells:
        if H is None:
            return "aggregate(a(n): mixed provenance)"
        tot += 1
        real += tri.is_real_sweep(n, H)
    return "%d/%d real-sweep" % (real, tot)


def _cell_ok(cand, params, tri, n, H):
    """(ok, predicted) for one cell; predicted is None for boolean kind."""
    v = _actual(tri, n, H)
    ctx = PredictContext(tri, n, H, cand.kind)
    if cand.kind == "value":
        p = cand.predict(params, n, H, ctx)
        return p == v, p
    if cand.kind == "congruence":
        p = cand.predict(params, n, H, ctx)
        return p == v % cand.modulus, p
    return bool(cand.check(params, n, H, v, ctx)), None


def _known_coincident(cand, params, tri, hold_cells):
    """Name of a known relation implying ALL the candidate's holdout
    predictions, or None. Value kind is compared against known exact values;
    congruence kind mod 3 against the ternary spine's mod-3 map."""
    if not hold_cells:
        return None
    for kn in known_mod.KNOWN:
        implied = True
        for n, H in hold_cells:
            ctx = PredictContext(tri, n, H, cand.kind)
            if cand.kind == "value":
                kv = kn.predict_value(tri, n, H)
                if kv is None or kv != cand.predict(params, n, H, ctx):
                    implied = False
                    break
            elif cand.kind == "congruence":
                km = kn.predict_mod(tri, n, H, cand.modulus)
                if km is None or km != cand.predict(params, n, H, ctx):
                    implied = False
                    break
            else:
                implied = False  # boolean checks are judged by refuters
                break
        if implied:
            return kn.name
    return None


def verify_candidate(cand, tri):
    flags = []
    culled = False

    if cand.fit_max_n > DEFAULT_FIT_MAX_N:
        flags.append("FIT-REGION-EXTENDED(n<=%d: %s)"
                     % (cand.fit_max_n, cand.fit_region_reason))

    # ---- fit, sandboxed ----
    params = None
    if cand.fit is not None:
        try:
            params = cand.fit(FitView(tri, cand.fit_max_n))
        except FitRegionViolation as e:
            flags.append("FIT-REGION-VIOLATION")
            flags.append(str(e))
            culled = True
        except Exception as e:
            flags.append("FIT-ERROR(%s: %s)" % (type(e).__name__, e))
            culled = True

    cells = cand.region_cells()
    fit_cells = [(n, H) for n, H in cells if n <= cand.fit_max_n]
    hold_cells = [(n, H) for n, H in cells if cand.fit_max_n < n <= HOLDOUT_MAX_N]
    final_cells = [(n, H) for n, H in cells if n == NMAX]

    report = {
        "id": cand.id, "proposer": cand.proposer, "tier": cand.tier,
        "kind": cand.kind, "statement": cand.statement,
        "n_params": cand.n_params, "flags": flags,
        "fit_cells": len(fit_cells),
        "fit_rows": sorted({n for n, _ in fit_cells}),
        "holdout_cells": len(hold_cells),
        "holdout_matched": 0, "holdout_rows": {},
        "first_fail_row": None,
        "row40": {"cells": len(final_cells), "result": "no-cells",
                  "predictions": {}},
        "bits_per_cell": None, "bits_holdout": None, "bits_row40": None,
        "bits_note": "", "culled": False, "verdict": "",
        "independence": {
            "input_footprint": cand.input_footprint,
            "derivation_independence": cand.derivation_independence,
            "rule_independence": cand.rule_independence,
            "fit_max_n": cand.fit_max_n,
        },
        # provenance composition of the cells this candidate is scored on:
        # a "check" whose cells are all closed-form-derived checks the wiring
        # of a formula, not the enumeration (see README.md)
        "holdout_real_sweep": _prov_count(tri, hold_cells),
        "row40_real_sweep": _prov_count(tri, final_cells),
    }

    if culled:
        report["culled"] = True
        report["verdict"] = "CULLED(%s)" % flags[0]
        return report

    try:
        # ---- fit-region consistency ----
        fit_bad = [(n, H) for n, H in fit_cells
                   if not _cell_ok(cand, params, tri, n, H)[0]]
        if fit_bad:
            flags.append("FIT-INCONSISTENT(first at n=%d,H=%s)"
                         % (fit_bad[0][0], fit_bad[0][1]))
            report["culled"] = True
            report["verdict"] = "CULLED(FIT-INCONSISTENT)"
            return report

        # ---- holdout, by n ----
        rows = {}
        matched = 0
        first_fail = None
        insensitive_all = cand.kind == "boolean" and bool(hold_cells)
        for n, H in hold_cells:
            ok, _ = _cell_ok(cand, params, tri, n, H)
            if ok:
                matched += 1
                rows.setdefault(n, "ok")
            else:
                rows[n] = "FAIL"
                if first_fail is None or n < first_fail:
                    first_fail = n
            if insensitive_all:
                # tautology guard: a boolean check with no sensitivity to its
                # target value has zero checking power; perturb the value and
                # see whether the check notices
                v = _actual(tri, n, H)
                ctx = PredictContext(tri, n, H, cand.kind)
                try:
                    if not cand.check(params, n, H, v + 1, ctx):
                        insensitive_all = False
                except Exception:
                    insensitive_all = False  # crashing on a wrong value counts
                    # as noticing it
        report["holdout_rows"] = {n: rows[n] for n in sorted(rows)}
        report["holdout_matched"] = matched
        report["first_fail_row"] = first_fail

        # ---- row 40, scored separately, never fitted ----
        if final_cells:
            ok40 = True
            for n, H in final_cells:
                ok, pred = _cell_ok(cand, params, tri, n, H)
                report["row40"]["predictions"][H] = pred
                ok40 = ok40 and ok
            report["row40"]["result"] = "ok" if ok40 else "FAIL"
    except FitRegionViolation as e:
        flags.append("FIT-REGION-VIOLATION")
        report["culled"] = True
        report["verdict"] = "CULLED(FIT-REGION-VIOLATION at predict: %s)" % e
        return report
    except PeekViolation as e:
        flags.append("PEEK-VIOLATION(%s)" % e)
        report["culled"] = True
        report["verdict"] = "CULLED(PEEK-VIOLATION)"
        return report
    except Exception as e:
        flags.append("PREDICT-ERROR(%s: %s)" % (type(e).__name__, e))
        report["culled"] = True
        report["verdict"] = "CULLED(PREDICT-ERROR)"
        return report

    # ---- culls that need the holdout numbers ----
    if not hold_cells:
        flags.append("NO-HOLDOUT")
        report["culled"] = True
        report["verdict"] = "CULLED(NO-HOLDOUT)"
        return report
    if cand.kind == "boolean" and insensitive_all:
        flags.append("VALUE-INSENSITIVE(check passes with perturbed values on "
                     "every holdout cell -- tautology, zero checking power)")
        report["culled"] = True
        report["verdict"] = "CULLED(VALUE-INSENSITIVE)"
        return report
    if first_fail is not None:
        # a real holdout failure is the most informative verdict; report it
        # (param accounting still noted for the record)
        if cand.n_params >= matched:
            flags.append("FITTED-NOT-TESTED(%d params >= %d holdout cells "
                         "matched)" % (cand.n_params, matched))
        report["verdict"] = "FAILS(first fail row n=%d)" % first_fail
        return report
    if cand.n_params >= matched:
        flags.append("FITTED-NOT-TESTED(%d params >= %d holdout cells matched)"
                     % (cand.n_params, matched))
        report["culled"] = True
        report["verdict"] = "CULLED(FITTED-NOT-TESTED)"
        return report

    # ---- bits of check (computed before the known-cull so that a culled
    # candidate's report still shows honest bits accounting and any
    # BITS-INFLATED flag) ----
    if cand.kind == "congruence":
        bpc = math.log2(cand.modulus)
        if cand.bits_claimed is not None and cand.bits_claimed > bpc + 1e-9:
            flags.append("BITS-INFLATED(claimed %.1f > log2(m)=%.2f)"
                         % (cand.bits_claimed, bpc))
        report["bits_per_cell"] = bpc
        report["bits_holdout"] = bpc * matched
        report["bits_row40"] = bpc * len(final_cells)
        report["bits_note"] = ("log2(m) per cell; summing assumes cells fail "
                               "independently -- refuters judge correlation")
    else:
        if cand.bits_claimed is not None and cand.bits_justification:
            report["bits_per_cell"] = cand.bits_claimed
            report["bits_row40"] = cand.bits_claimed * len(final_cells)
            report["bits_holdout"] = cand.bits_claimed * matched
            flags.append("BITS-UNVERIFIED(proposer-claimed: %s)"
                         % cand.bits_justification)
        elif cand.bits_claimed is not None:
            flags.append("NO-BITS-JUSTIFIED(claimed %.1f with no justification"
                         " -- refused)" % cand.bits_claimed)
            report["bits_note"] = "bits claim refused: no justification"
        else:
            report["bits_note"] = ("unquantified: exact-value/boolean match "
                                   "with no a-priori error model; we refuse "
                                   "to invent a number")

    kn = _known_coincident(cand, params, tri, hold_cells)
    if kn:
        flags.append("KNOWN-COINCIDENT(%s)" % kn)
        report["culled"] = True
        report["verdict"] = "CULLED(KNOWN-COINCIDENT)"
        return report

    report["verdict"] = "SURVIVES"
    return report


# ---------------------------------------------------------------- reporting

def format_table(reports):
    hdr = ("%-28s %-4s %-10s %6s %6s %9s %10s %8s %8s  %s"
           % ("id", "tier", "kind", "params", "fit", "holdout", "first-fail",
              "row40", "bits40", "verdict"))
    lines = [hdr, "-" * len(hdr)]
    for r in reports:
        hold = "%d/%d" % (r["holdout_matched"], r["holdout_cells"])
        b40 = "-" if r["bits_row40"] is None else "%.1f" % r["bits_row40"]
        lines.append("%-28s %-4s %-10s %6d %6d %9s %10s %8s %8s  %s"
                     % (r["id"][:28], r["tier"], r["kind"], r["n_params"],
                        r["fit_cells"], hold,
                        r["first_fail_row"] or "-",
                        r["row40"]["result"], b40, r["verdict"]))
        lines.append("    provenance: holdout %s, row40 %s"
                     % (r["holdout_real_sweep"], r["row40_real_sweep"]))
        for f in r["flags"]:
            lines.append("    flag: %s" % f)
    return "\n".join(lines)


def main(argv):
    from triangle import Triangle, TriangleDataError
    try:
        tri = Triangle.load()
    except TriangleDataError as e:
        print("DATA VALIDATION FAILED: %s" % e, file=sys.stderr)
        return 1
    if argv and argv[0] == "--selftest":
        print("loader: OK (row sums, anchors, structural zeros)")
        dl, sp, ls, cf = known_mod.KNOWN
        nok = sum(1 for n in range(1, NMAX + 1) for H in range(1, n + 1)
                  if dl.predict_value(tri, n, H) == tri.cell(n, H))
        print("known diagonal-law predicate: %d cells reproduced" % nok)
        nok = sum(1 for n in range(1, NMAX + 1) for H in range(1, n + 1)
                  if sp.predict_mod(tri, n, H, 3) == tri.cell(n, H) % 3)
        print("known ternary-spine predicate: %d cells reproduced" % nok)
        nok = sum(1 for n in range(1, NMAX + 1) for H in (1, 2)
                  if ls.predict_value(tri, n, H) == tri.cell(n, H))
        print("known low-strip predicate: %d cells reproduced" % nok)
        nok = sum(1 for n in range(1, NMAX + 1) for H in range(1, 5)
                  if cf.predict_value(tri, n, H) == tri.cell(n, H))
        print("known column-C-finite predicate: %d cells reproduced "
              "(onsets %s; regenerated from seed terms alone)"
              % (nok, cf.onsets(tri)))
        print("strip identity C_H - 2C_{H-1} + C_{H-2}: %d cells checked"
              % known_mod.strip_identity_holds(tri))
        return 0
    if not argv:
        print(__doc__)
        return 0
    reports = []
    for path in argv:
        try:
            cands = load_candidates(path)
        except Exception as e:
            print("CANDIDATE FILE ERROR %s: %s" % (path, e), file=sys.stderr)
            return 2
        for c in cands:
            reports.append(verify_candidate(c, tri))
    reports.sort(key=lambda r: (r["culled"], r["verdict"] != "SURVIVES",
                                -(r["bits_row40"] or 0)))
    print(format_table(reports))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
