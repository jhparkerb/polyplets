#!/usr/bin/env python3
"""refB_deficit.py -- Refuter B attacks on Proposer 1's mod-3 deficit-family
congruences (results/triangle-hunt-proof-first.md section 2,
candidates/p1_deficit_families.py). Families: cells (n,H) = (3k+1-d, 2k+1-d),
k >= d, on the lines 2n-3H = d-1 (direction (2,-3)).

A. Reproduce the four families' residues from the banked triangle; verify the
   claimed patterns; print per-cell provenance (triangle.py's flags) and
   known.py implication (DiagonalLaw reach).
B. Cull-boundary audit: exactly which holdout cells are (i) known.py-implied
   (k <= 13 interpolation), (ii) closed-form-Pk wired in the bank itself
   (H >= 22), (iii) real-sweep AND not implied. The proposer's "one law-free
   real-sweep cell at k=14" claim is decided by (iii).
C. d=3 retrodiction: zeros on the line exactly at k == 1 (mod 3), k = 3..14,
   with provenance per zero; the (40,26) prediction's provenance.
D. Below-onset probe: does each pattern extend to k = d-1 (one step below
   the family's chosen start)?
E. Luck rate, comparable support: the IDENTICAL fit procedure (constant tail
   via last-3, or exact period 2..4, mirroring p1_deficit_families._fit_factory)
   run over every sparse line s*n + t*H = c (|s|<=3, 1<=t<=3, primitive) with
   4..6 fit cells (n<=22) and >=5 holdout cells (n=23..40), excluding the
   proved d=0,1,2 lines and the four target lines. Passes classified by
   whether every holdout cell is known.py-implied / formula-wired. Also a
   head-cut variant (drop up to 3 leading cells) that is GENEROUS to chance,
   mirroring the families' own below-onset head cut.
F. Perturbation trials to the 268-trial standard: one fit-cell residue
   shifted by +1/+2 mod 3, identical procedure re-run, passes counted.

Exact integer arithmetic. Run from experiments/tristruct/.
"""
from triangle import Triangle
from known import KNOWN, DiagonalLaw

TRI = Triangle.load()
LAW = next(x for x in KNOWN if isinstance(x, DiagonalLaw))


def family_cells(d, hi_n=40):
    out = []
    for k in range(d, 40):
        n, H = 3 * k + 1 - d, 2 * k + 1 - d
        if n <= hi_n and 1 <= H <= n:
            out.append((k, n, H))
    return out


def implied_mod3(n, H):
    """Any known.py relation that determines the residue mod 3 here."""
    for rel in KNOWN:
        r = rel.predict_mod(TRI, n, H, 3)
        if r is not None:
            return rel.name.split()[0]
    return None


def fit_procedure(res):
    """Mirror of p1_deficit_families._fit_factory on a residue list.
    Returns ('const', c) or ('periodic', p, pattern) or None."""
    if len(res) >= 4 and len(set(res[-3:])) == 1:
        return ('const', res[-1])
    for p in (2, 3, 4):
        if len(res) >= 2 * p and all(res[i] == res[i % p]
                                     for i in range(len(res))) \
                and len(set(res[:p])) > 1:
            return ('periodic', p, res[:p])
    return None


def holdout_pass(fit, res_all, n_fit):
    """Do the residues past the fit prefix continue the fitted pattern?"""
    if fit is None:
        return False
    if fit[0] == 'const':
        return all(r == fit[1] for r in res_all[n_fit:])
    _, p, pat = fit
    return all(res_all[i] == pat[i % p] for i in range(n_fit, len(res_all)))


def part_a_b():
    print("A/B. families, per-cell audit (res = T mod 3):")
    for d in (3, 4, 5, 6):
        cells = family_cells(d)
        rows = []
        for k, n, H in cells:
            rows.append((k, n, H, TRI.cell(n, H) % 3,
                         TRI.provenance(n, H), implied_mod3(n, H)))
        fitc = [r for r in rows if r[1] <= 22]
        holdc = [r for r in rows if r[1] > 22]
        print(" d=%d: fit %d cells, holdout %d cells" % (d, len(fitc), len(holdc)))
        for k, n, H, r, prov, imp in rows:
            tag = "FIT " if n <= 22 else "HOLD"
            print("   %s k=%-2d (%2d,%2d) res=%d  %-20s implied-by=%s"
                  % (tag, k, n, H, r, prov, imp or "NONE"))
        fit = fit_procedure([r[3] for r in fitc])
        ok = holdout_pass(fit, [r[3] for r in rows], len(fitc))
        lawfree_sweep = [r for r in holdc
                        if r[5] is None and r[4] == "real-sweep"]
        print("   procedure verdict: fit=%s holdout-pass=%s" % (fit, ok))
        print("   holdout cells NOT known.py-implied: %s"
              % [(r[0], r[1], r[2], r[4]) for r in holdc if r[5] is None])
        print("   'law-free AND real-sweep' holdout cells: %d %s"
              % (len(lawfree_sweep), lawfree_sweep))


def part_c():
    print("C. d=3 line zeros (claim: exactly k == 1 mod 3), k=3..14:")
    for k, n, H in family_cells(3):
        r = TRI.cell(n, H) % 3
        z = "ZERO" if r == 0 else "    "
        flag = "match" if (r == 0) == (k % 3 == 1) else "**PATTERN BREAK**"
        print("   k=%-2d (%2d,%2d) res=%d %s k%%3=%d %s [%s]"
              % (k, n, H, r, z, k % 3, flag, TRI.provenance(n, H)))
    print("   census cross-check: zeros above should be exactly "
          "(4,10),(7,19),(10,28),(13,37) plus none at k=14 (40,26)")


def part_d():
    print("D. below-onset probe, one step under each family's start:")
    for d in (3, 4, 5, 6):
        k = d - 1
        n, H = 3 * k + 1 - d, 2 * k + 1 - d
        if H < 1 or n < 1:
            continue
        r = TRI.cell(n, H) % 3
        cells = family_cells(d)
        first = TRI.cell(cells[0][1], cells[0][2]) % 3
        print("   d=%d: k=%d cell (%d,%d) res=%d vs family start res=%d -> %s"
              % (d, k, n, H, r, first,
                 "extends" if r == first else "breaks (as a law-region "
                 "artifact should)"))


def sparse_lines():
    """All (s,t,c) lines, |s|<=3, 1<=t<=3, gcd=1, one cell per n, with
    4..6 fit cells (n<=22) and >=5 holdout (n=23..40)."""
    from math import gcd
    out = []
    for s in range(-3, 4):
        for t in range(1, 4):
            if gcd(abs(s), t) != 1:
                continue
            cs = set()
            for n in range(1, 41):
                for H in range(1, n + 1):
                    cs.add(s * n + t * H)
            for c in sorted(cs):
                cells = [(n, (c - s * n) // t) for n in range(1, 41)
                         if (c - s * n) % t == 0
                         and 1 <= (c - s * n) // t <= n]
                fit = [x for x in cells if x[0] <= 22]
                hold = [x for x in cells if x[0] > 22]
                if 4 <= len(fit) <= 6 and len(hold) >= 5:
                    out.append((s, t, c, cells, len(fit)))
    return out


def part_e():
    lines = sparse_lines()
    # exclude the target family lines and the proved d=0,1,2 lines:
    # family lines are s=2,t=-3 i.e. canonical (-2,3) with negated c;
    # as (s,t,c) here: 2n-3H = d-1  <=>  s=-2,t=3,c=1-d
    targets = {(-2, 3, 1 - d) for d in range(0, 7)}
    ctrl = [l for l in lines if (l[0], l[1], l[2]) not in targets]
    strict = heady = 0
    strict_free = []
    for s, t, c, cells, nf in ctrl:
        res = [TRI.cell(n, H) % 3 for n, H in cells]
        f = fit_procedure(res[:nf])
        if holdout_pass(f, res, nf):
            strict += 1
            unimplied = [(n, H, TRI.provenance(n, H)) for n, H in cells[nf:]
                         if implied_mod3(n, H) is None]
            strict_free.append(((s, t, c), f, unimplied))
        # generous head-cut variant
        for cut in range(0, 4):
            if len(res) - cut < nf - cut + 5 or nf - cut < 4:
                continue
            f2 = fit_procedure(res[cut:nf])
            if holdout_pass(f2, res[cut:], nf - cut):
                heady += 1
                break
    print("E. luck rate on %d comparable sparse control lines "
          "(4..6 fit, >=5 holdout, mod 3):" % len(ctrl))
    print("   strict passes: %d  (rate %.3f)" % (strict, strict / len(ctrl)))
    for key, f, unimp in strict_free:
        print("     pass %s fit=%s; holdout cells NOT known-implied: %s"
              % (key, f, unimp or "none (fully implied -> would be culled)"))
    print("   head-cut (<=3) passes: %d  (rate %.3f)"
          % (heady, heady / len(ctrl)))


def part_f():
    trials = passes = 0
    for d in (3, 4, 5):
        cells = family_cells(d)
        res = [TRI.cell(n, H) % 3 for _, n, H in cells]
        nf = sum(1 for _, n, _h in cells if n <= 22)
        for i in range(nf):
            for delta in (1, 2):
                pert = list(res)
                pert[i] = (pert[i] + delta) % 3
                trials += 1
                f = fit_procedure(pert[:nf])
                if holdout_pass(f, pert, nf):
                    passes += 1
                    print("   F PASS d=%d perturb fit idx %d +%d: fit=%s"
                          % (d, i, delta, f))
    print("F. perturbation trials: %d, passes: %d" % (trials, passes))


if __name__ == '__main__':
    part_a_b()
    part_c()
    part_d()
    part_e()
    part_f()
