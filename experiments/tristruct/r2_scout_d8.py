#!/usr/bin/env python3
"""r2 extension scout (triangle-structure round 2, agent 4): does the proved
tower method reach d = 8..19, and what would it buy?

Per docs/triangle-structure-round2-brief.md (Team shape, agent 4) and
results/triangle-r2-d3-audit.md (Extension-scout recommendation). This is a
SCOUTING and COSTING run, not a proving run. Sections, each a subcommand:

  levels  Actually run the d=4 (mod 243) and d=5 (mod 729) tower levels --
          agent 1's census says they are free -- and, if the five new m=7
          weights come in under their probe timeouts, the d=6 (mod 3^7)
          level too. Every level: fixed point vs banked h_k (k<=17), monic
          curve E == 0, G vs banked g_k, family residues vs the measured
          cycles of results/triangle-hunt-synthesis.md, all exact integer
          arithmetic, wall-clock printed.
  census  Exact per-level weight requirements m = 3..20 (interior + boundary
          slots), classified: known / closed-form / cheap pair-stack DP /
          fitted-formula-only / newDP, with the newly-entering-at-m lists
          and DP-only exposure flags (agent 3 finding 2's shape).
  probes  Small-sample DP timings (measure-don't-reason): re-time two banked
          two-row cells to normalize this machine against the 2026-08-01
          walls, then time three-row k=5,6 cells, a four-row k=6 cell, the
          five m=7 interior weights, and matching boundary cells. Hard
          per-cell SIGALRM timeouts; a timeout is itself a lower bound.
  bits    The mission's number: bit accounting against ENUMERATION error for
          outcomes d=8 only / d=8..12 / d=8..19, plus the separate
          formula-chain count, with provenance quoted from triangle.py per
          cell and the H=15..19 row-40 block share verified.

Exact integer arithmetic throughout. No section exceeds ~5 min.
"""
import os
import signal
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "experiments"))
sys.path.insert(0, HERE)

from cluster_weight_dp import (KNOWN_WEIGHTS, TWO_ROW_INTERIOR, compositions,
                               interior, boundary)
import r2_tower_mod81 as t1

t1.KX = 60          # series order: banked check needs k<=17, family scan k<=40
KX = t1.KX
LOG2_3 = 1.5849625007211562

# W(2,6) = 6111 is banked in results/defect-gas.md (a=2 cubic holdout) but
# absent from TWO_ROW_INTERIOR; include it as a known interior weight.
TWO_ROW = dict(TWO_ROW_INTERIOR)
TWO_ROW[(2, 6)] = 6111

# Weights with an independent DIRECT-ENUMERATION cross-check (agent 3 finding
# 2's axis): validate() covers all k<=3 types, and results/defect-gas.md's
# master-equation table additionally enumerates (3,3) and (2,4)/(4,2).
ENUM_CHECKED = {(2,), (3,), (4,), (2, 2), (2, 3), (3, 2), (2, 2, 2),
                (3, 3), (2, 4), (4, 2)}


def v3(x):
    return t1.v3(x)


# ---------------------------------------------------------------- weights --

class Timeout(Exception):
    pass


def _alarm(signum, frame):
    raise Timeout()


def timed_weight(fn, vec, limit):
    """(value, seconds) or (None, limit) on timeout."""
    signal.signal(signal.SIGALRM, _alarm)
    signal.alarm(limit)
    try:
        t0 = time.time()
        w = fn(vec)
        signal.alarm(0)
        return w, time.time() - t0
    except Timeout:
        return None, limit


def weight_tables(extra_int=None, extra_bnd=None):
    """(interior, bnd_bottom, bnd_top) dicts from the banked table plus any
    extras computed this run. Boundary-top of v = boundary(reversed(v))."""
    wi = {v: w[0] for v, w in KNOWN_WEIGHTS.items()}
    wb = {v: w[1] for v, w in KNOWN_WEIGHTS.items()}
    wt = {v: w[2] for v, w in KNOWN_WEIGHTS.items()}
    if extra_int:
        wi.update(extra_int)
    if extra_bnd:
        for v, w in extra_bnd.items():
            wb[v] = w
            wt[tuple(reversed(v))] = w
    return wi, wb, wt


def survivors(M, wi, wb, wt):
    """Interior / eps_b / eps_t / den survivor term lists mod 3^M over the
    given tables. Completeness (defect-gas VALUATION LEMMA + row bound):
    interior candidates need 2k-l-1 <= M-1, boundary need 2k-l <= M-1;
    raises if a candidate weight is missing from the tables."""
    MOD = 3 ** M
    ints, ebs, ets, dens = [], [], [], []
    for k in range(1, M + 1):
        for c in compositions(k):
            l = len(c)
            if 2 * k - l - 1 <= M - 1:
                if c not in wi:
                    raise KeyError(("interior", c))
                what = wi[c] * 3 ** (2 * k - l - 1)
                if v3(what) < M:
                    ints.append((c, k, l, what % MOD))
                if v3((l + 1) * what) < M:
                    dens.append((c, k, l, ((l + 1) * what) % MOD))
            if 2 * k - l <= M - 1:
                if c not in wb or c not in wt:
                    raise KeyError(("boundary", c))
                bb = wb[c] * 3 ** (2 * k - l)
                bt = wt[c] * 3 ** (2 * k - l)
                if v3(bb) < M:
                    ebs.append((c, k, l, bb % MOD))
                if v3(bt) < M:
                    ets.append((c, k, l, bt % MOD))
    return ints, ebs, ets, dens


# ----------------------------------------------------------------- levels --

def run_level(M, wi, wb, wt, P, Gs, Hb, peval, cycle, cyc_start):
    """One tower level mod 3^M = the d = M-1 level. Returns wall seconds."""
    d = M - 1
    MOD = 3 ** M
    t0 = time.time()
    ints, ebs, ets, dens = survivors(M, wi, wb, wt)
    xmul, xinv, xpow = t1.series_ops(MOD)

    H = t1.fixed_point(ints, MOD)
    assert H[:18] == [h % MOD for h in Hb], "H mod 3^%d vs banked" % M

    D = max(k + l for _, k, l, _ in ints)
    E = xpow(H, D + 1)
    HD = xpow(H, D)
    for m in range(KX + 1):
        E[m] = (E[m] - HD[m]) % MOD
    for _, k, l, w in ints:
        Hp = xpow(H, D - k - l)
        for m in range(KX + 1 - k):
            if Hp[m]:
                E[m + k] = (E[m + k] - w * Hp[m]) % MOD
    assert all(c == 0 for c in E), "monic curve mod 3^%d" % M

    def eps_series(terms):
        out = [1] + [0] * KX
        for _, k, l, w in terms:
            Hp = xpow(H, -(k + l))
            for m in range(KX + 1 - k):
                if Hp[m]:
                    out[m + k] = (out[m + k] + w * Hp[m]) % MOD
        return out

    eb, et = eps_series(ebs), eps_series(ets)
    den = eps_series(dens)
    u = [0, 1] + [0] * (KX - 1)
    Hp = [((m + 1) * H[m + 1]) % MOD for m in range(KX)] + [0]
    fac = [((1 if m == 0 else 0) - xmul(xmul(u, Hp), xinv(H))[m]) % MOD
           for m in range(KX + 1)]
    G = xmul(xmul(xmul(eb, et), fac), xinv(den))
    assert G[:18] == [g % MOD for g in Gs], "G mod 3^%d vs banked" % M

    def Pk_mod(k, n):
        Hn = xpow(H, n)
        return sum(G[j] * Hn[k - j] for j in range(k + 1)) % MOD

    # family d: (n, H) = (3k+1-d, 2k+1-d), in-sleeve k >= d
    res = {}
    for k in range(max(d, 1), KX - 4):
        n = 3 * k + 1 - d
        p = Pk_mod(k, n)
        if k <= 17:
            assert p == int(peval(P[k], n)) % MOD, ("banked P_k", k)
        assert p % 3 ** d == 0, ("integrality", k, p)
        res[k] = (p // 3 ** d) % 3
    ks = sorted(res)
    assert all(res[k] == res[k + 3] for k in ks if k + 3 in res), "period 3"
    meas = [res[cyc_start], res[cyc_start + 1], res[cyc_start + 2]]
    assert meas == list(cycle), ("cycle", meas, cycle)
    dt = time.time() - t0
    print("  d=%d (mod 3^%d): %d interior terms, curve deg %d monic, "
          "H+G match banked k<=17, family cycle %s from k=%d "
          "(k up to %d on derived series)  [%.1f s]"
          % (d, M, len(ints), D + 1, tuple(meas), cyc_start, ks[-1], dt))
    return dt


def cmd_levels():
    print("== tower levels actually run (the measured plateau) ==")
    P, Gs, Hb, peval = t1.banked(17)
    wi, wb, wt = weight_tables()

    # d=3 reference re-run (agent 1's level) for a same-machine baseline
    run_level(4, wi, wb, wt, P, Gs, Hb, peval, (2, 0, 1), 3)
    # d=4, d=5: agent 1's census says zero new weights -- verify by running
    run_level(5, wi, wb, wt, P, Gs, Hb, peval, (2, 2, 2), 4)
    ei = {(2,) * 6: interior((2,) * 6)}
    eb = {(2,) * 6: boundary((2,) * 6)}
    wi, wb, wt = weight_tables(ei, eb)
    run_level(6, wi, wb, wt, P, Gs, Hb, peval, (2, 2, 2), 5)

    # d=6 (mod 3^7): needs the five k=6, l=5 interior weights + (2^7) + the
    # matching boundary cells. Compute them live with timeouts; report cost.
    print("  d=6 prerequisite weights (the census's '5 cheap newDP'):")
    need = [c for c in compositions(6) if len(c) == 5]
    extra_i, extra_b, tot = {}, {}, 0.0
    ok = True
    for c in need:
        w, dt = timed_weight(interior, c, 240)
        if w is None:
            print("    interior%s TIMEOUT >%ds" % (c, dt))
            ok = False
            continue
        extra_i[c] = w
        tot += dt
        print("    interior%s = %d  v3=%d  [%.1f s]" % (c, w, v3(w), dt))
        wbv, dtb = timed_weight(boundary, c, 240)
        if wbv is None:
            ok = False
            continue
        extra_b[c] = wbv
        tot += dtb
        print("    boundary%s = %d  v3=%d  [%.1f s]" % (c, wbv, v3(wbv), dtb))
    for c in [(2,) * 7]:
        w, dt = timed_weight(interior, c, 240)
        if w is None:
            ok = False
        else:
            extra_i[c] = w
            tot += dt
    if ok:
        extra_i[(2,) * 6] = ei[(2,) * 6]
        extra_b[(2,) * 6] = eb[(2,) * 6]
        wi, wb, wt = weight_tables(extra_i, extra_b)
        print("  (all m=7 weights in %.0f s of DP)" % tot)
        run_level(7, wi, wb, wt, P, Gs, Hb, peval, (2, 1, 1), 6)
    else:
        print("  d=6 level SKIPPED: a prerequisite weight exceeded its probe "
              "timeout -- that is itself the measurement")


# ----------------------------------------------------------------- census --

def slot_status(c, kind):
    """Status of one weight slot. kind in {'int','bnd'}."""
    k, l = sum(c) - len(c), len(c)
    if l == 1:
        return "closed-form"                    # (2s+1)^2 / 2s+1, proved
    if c in KNOWN_WEIGHTS:
        return "known"
    if c == (2,) * l:
        return "cheapDP"                        # pair stack, polynomial cost
    if kind == "int" and l == 2 and tuple(sorted(c)) in TWO_ROW:
        return "known"                          # banked 2026-08-01 (DP walls)
    if kind == "int" and l == 2 and min(c) in (2, 3):
        return "fitted-formula"                 # a=2 cubic / a=3 quartic,
    return "newDP"                              # holdout-checked, NOT proved


def census_slots(m):
    """All (vec, kind) weight slots the mod-3^m level can consult."""
    out = []
    for k in range(1, m + 1):
        for c in compositions(k):
            l = len(c)
            if 2 * k - l - 1 <= m - 1:
                out.append((c, "int"))
            if 2 * k - l <= m - 1:
                out.append((c, "bnd"))
    return out


def cmd_census():
    print("== per-level weight census, m = 3..20 (level m serves d = m-1) ==")
    print("   slots = interior + boundary weight cells the valuation filter")
    print("   consults; newDP = no banked value, no proved closed form")
    print()
    print("   m   d | slots  known cform cheap fitted newDP | newDP entering at m")
    prev = set()
    for m in range(3, 21):
        slots = census_slots(m)
        cnt = {"known": 0, "closed-form": 0, "cheapDP": 0,
               "fitted-formula": 0, "newDP": 0}
        newdp = []
        for c, kind in slots:
            s = slot_status(c, kind)
            cnt[s] += 1
            if s == "newDP":
                newdp.append((c, kind))
        entering = [x for x in newdp if x not in prev]
        prev |= set(newdp)
        by_l = {}
        for c, kind in entering:
            by_l.setdefault((len(c), kind), []).append(c)
        desc = "; ".join(
            "l=%d %s x%d (max k=%d, widest row %d)"
            % (l, kind, len(vs), max(sum(v) - len(v) for v in vs),
               max(max(v) for v in vs))
            for (l, kind), vs in sorted(by_l.items()))
        print("  %2d  %2d | %5d  %5d %5d %5d %6d %5d | %s"
              % (m, m - 1, len(slots), cnt["known"], cnt["closed-form"],
                 cnt["cheapDP"], cnt["fitted-formula"], cnt["newDP"],
                 desc or "-"))
    print()
    print("== DP-only exposure flags (agent 3 finding 2's shape) ==")
    print("   enumeration-checked weights: %s" % sorted(ENUM_CHECKED))
    print("   every OTHER consulted weight is DP-only; per level, the newly-")
    print("   entering DP-only digits are the entire new exposure. First few:")
    prev = set()
    for m in range(3, 21):
        ent = []
        for c, kind in census_slots(m):
            key = (c, kind)
            if key in prev:
                continue
            prev.add(key)
            if slot_status(c, kind) != "closed-form" and c not in ENUM_CHECKED:
                k, l = sum(c) - len(c), len(c)
                shift = 2 * k - l - 1 if kind == "int" else 2 * k - l
                ent.append((c, kind, m - shift))
        if ent:
            worst = sorted(ent, key=lambda x: -x[2])[:4]
            print("  m=%2d: %3d new DP-only slots; deepest digits needed: %s"
                  % (m, len(ent),
                     ", ".join("%s[%s] mod 3^%d" % (c, kind, dig)
                               for c, kind, dig in worst)))


# ----------------------------------------------------------------- probes --

PROBES = [
    # (vec, fn-name, limit-s, banked-wall-s-or-None, banked-value-or-None)
    ((3, 5), "int", 300, 89, 19671),      # machine-normalization anchors
    ((4, 4), "int", 300, 120, 28559),
    ((2, 2, 4), "int", 120, None, 29515),  # three-row k=5 (banked value)
    ((2, 3, 3), "int", 120, None, 67371),  # three-row k=5
    ((2, 2, 5), "int", 300, None, None),   # three-row k=6
    ((2, 3, 4), "int", 300, None, None),
    ((3, 3, 3), "int", 300, None, None),
    ((2, 2, 6), "int", 300, None, None),   # three-row k=7 (may time out)
    ((2, 2, 2, 4), "int", 300, None, None),  # four-row k=6
    ((3, 5), "bnd", 120, None, None),      # boundary-vs-interior cost ratio
    ((4, 4), "bnd", 120, None, None),
    ((5, 5), "bnd", 300, None, None),      # interior took 30137 s banked
    ((2, 2, 5), "bnd", 120, None, None),
]


def cmd_probes():
    print("== DP cost probes (small samples; timeouts are lower bounds) ==")
    results = {}
    for vec, kind, limit, bw, bv in PROBES:
        fn = interior if kind == "int" else boundary
        w, dt = timed_weight(fn, vec, limit)
        tag = "interior" if kind == "int" else "boundary"
        if w is None:
            print("  %s%s: TIMEOUT >%d s" % (tag, vec, limit))
            results[(vec, kind)] = (None, limit)
            continue
        note = ""
        if bv is not None:
            assert w == bv, (vec, w, bv)
            note += " (matches banked value)"
        if bw is not None:
            note += "  banked wall %d s -> machine factor x%.2f" % (bw, bw / dt)
        print("  %s%s = %d  v3=%d  [%.1f s]%s" % (tag, vec, w, v3(w), dt, note))
        results[(vec, kind)] = (w, dt)
    # growth read-offs
    print()
    print("  banked two-row growth per unit surplus (2026-08-01 walls):")
    print("    a=2: (2,7)->(2,8) 178->1502 s      = x8.4")
    print("    a=3: (3,5)->(3,6)->(3,7) 89->1144->13388 s = x12.9, x11.7")
    print("    balanced: (4,4)->(5,5) 120->30137 s = x15.9/surplus (k 6->8)")
    tr = results.get(((2, 2, 5), "int"), (None, None))[1]
    t4 = results.get(((2, 2, 4), "int"), (None, None))[1]
    if tr and t4:
        print("  three-row (2,2,b) growth k 5->6: %.1f -> %.1f s = x%.1f"
              % (t4, tr, tr / t4))
    t6 = results.get(((2, 2, 6), "int"), (None, None))
    if t6[0] is not None and tr:
        print("  three-row (2,2,b) growth k 6->7: x%.1f" % (t6[1] / tr))


# --------------------------------------------------------------------- d8 --

def cmd_d8():
    """Build the mod-3^9 tower level (d=8) as the final measured probe: the
    full weight set with per-cell walls, H+G vs banked k<=17, the d=8 family
    residues against every banked cell, and a long-range periodicity scan of
    the target (round 1 measured 'not period-3' on the few grid points).
    NOT a proof: no LB certificate is attempted; the level is the check."""
    print("== d=8 tower level, built and measured ==")
    M = 9
    P, Gs, Hb, peval = t1.banked(17)
    wi, wb, wt = weight_tables()
    need = []
    for c, kind in census_slots(M):
        tab = wi if kind == "int" else wb
        if c not in tab and (kind == "int" or tuple(reversed(c)) not in wb):
            need.append((c, kind))
    # boundary table is filled by bottom-orientation runs; dedupe reversals
    bnd_need = sorted({tuple(sorted([c, tuple(reversed(c))]))[0]
                       for c, kind in need if kind == "bnd"})
    int_need = sorted({c for c, kind in need if kind == "int"})
    print("  missing weights: %d interior, %d boundary orientations "
          "(x2 runs where asymmetric)" % (len(int_need), len(bnd_need)))
    t0 = time.time()
    ei, eb = {}, {}
    budget = 2700
    aborted = False
    for c in sorted(int_need, key=lambda c: (sum(c), max(c))):
        if time.time() - t0 > budget:
            aborted = True
            break
        w, dt = timed_weight(interior, c, 300)
        if w is None:
            print("    interior%s TIMEOUT >300 s -- ABORT" % (c,))
            aborted = True
            break
        ei[c] = w
        if dt > 5:
            print("    interior%s = %d  v3=%d  [%.1f s]" % (c, w, v3(w), dt))
    for c in bnd_need:
        if aborted or time.time() - t0 > budget:
            aborted = True
            break
        w, dt = timed_weight(boundary, c, 300)
        if w is None:
            aborted = True
            break
        eb[c] = w
        if dt > 5:
            print("    boundary%s = %d  v3=%d  [%.1f s]" % (c, w, v3(w), dt))
        r = tuple(reversed(c))
        if r != c:
            w2, dt2 = timed_weight(boundary, r, 300)
            if w2 is None:
                aborted = True
                break
            eb[r] = w2
    wall = time.time() - t0
    if aborted:
        print("  MEASURED BOUND: weight set did NOT complete in %.0f s; "
              "d=8 is not minutes-cheap on this box" % wall)
        return
    print("  full m=9 weight set computed in %.0f s of DP "
          "(%d interior + %d boundary runs)"
          % (wall, len(ei), len(eb)))

    wi, wb, wt = weight_tables(ei, eb)
    t0 = time.time()
    MOD = 3 ** M
    ints, ebs, ets, dens = survivors(M, wi, wb, wt)
    xmul, xinv, xpow = t1.series_ops(MOD)
    H = t1.fixed_point(ints, MOD)
    assert H[:18] == [h % MOD for h in Hb], "H mod 3^9 vs banked"
    D = max(k + l for _, k, l, _ in ints)

    def eps_series(terms):
        out = [1] + [0] * KX
        for _, k, l, w in terms:
            Hp = xpow(H, -(k + l))
            for m in range(KX + 1 - k):
                if Hp[m]:
                    out[m + k] = (out[m + k] + w * Hp[m]) % MOD
        return out

    ebs_s, ets_s, den = eps_series(ebs), eps_series(ets), eps_series(dens)
    u = [0, 1] + [0] * (KX - 1)
    Hp = [((m + 1) * H[m + 1]) % MOD for m in range(KX)] + [0]
    fac = [((1 if m == 0 else 0) - xmul(xmul(u, Hp), xinv(H))[m]) % MOD
           for m in range(KX + 1)]
    G = xmul(xmul(xmul(ebs_s, ets_s), fac), xinv(den))
    assert G[:18] == [g % MOD for g in Gs], "G mod 3^9 vs banked"
    print("  tower: %d interior survivors, curve deg %d monic; H+G match "
          "banked k<=17  [%.1f s]" % (len(ints), D + 1, time.time() - t0))

    def Pk_mod(k, n):
        Hn = xpow(H, n)
        return sum(G[j] * Hn[k - j] for j in range(k + 1)) % MOD

    d = 8
    res = {}
    for k in range(d, KX - 4):
        n = 3 * k + 1 - d
        p = Pk_mod(k, n)
        if k <= 17:
            assert p == int(peval(P[k], n)) % MOD, ("banked P_k", k)
        assert p % 3 ** d == 0, ("integrality", k)
        res[k] = (p // 3 ** d) % 3
    ks = sorted(res)
    seq = [res[k] for k in ks]
    print("  d=8 family residues r_k, k=%d..%d: %s"
          % (ks[0], ks[-1], "".join(map(str, seq))))
    per = next((p for p in (1, 3, 9, 27)
                if all(seq[i] == seq[i + p]
                       for i in range(len(seq) - p))), None)
    tailper = next((p for p in (1, 3, 9, 27)
                    if all(seq[i] == seq[i + p]
                           for i in range(9, len(seq) - p))), None)
    print("  periodicity: full-range period %s; from k=%d period %s"
          % (per, ks[0] + 9, tailper))

    # the check against the banked triangle
    from triangle import Triangle
    tri = Triangle.load()
    print("  family-8 cells vs banked triangle (T*3^8 == P_k(n) mod 3^9, "
          "i.e. T mod 3 == r_k):")
    npass = ntot = 0
    for k in range(8, 16):
        n, Hh = 3 * k - 7, 2 * k - 7
        if n > 40 or Hh > 40:
            continue
        got = tri.cell(n, Hh) % 3
        prov = tri.provenance(n, Hh)
        ok = got == res[k]
        npass += ok
        ntot += 1
        star = " <-- the d=8 LAW-FREE ENUMERATED cell" \
            if (k, prov) == (14, "real-sweep") else ""
        print("    k=%2d (n,H)=(%2d,%2d) [%s]: banked %d, predicted %d  %s%s"
              % (k, n, Hh, prov, got, res[k],
                 "MATCH" if ok else "*** MISMATCH ***", star))
    print("  %d/%d cells match" % (npass, ntot))

    # why round 1 saw "not period-3 for d >= 8": its scan included grid
    # cells with k < d, which sit below the proved onset n >= 2k+1
    print("  banked-grid periodicity scan (in-onset restriction k >= d):")
    for dd in range(8, 16):
        row = [(k, tri.cell(3 * k + 1 - dd, 2 * k + 1 - dd) % 3)
               for k in range(1, 20)
               if 1 <= 2 * k + 1 - dd <= 3 * k + 1 - dd <= 40]
        rs = [r for _, r in row]
        tail = [r for k, r in row if k >= dd]
        p3 = lambda s: (len(s) > 3
                        and all(s[i] == s[i + 3] for i in range(len(s) - 3)))
        print("    d=%2d: all-grid %s period3=%s | k>=d %s period3=%s "
              "(%d pts)" % (dd, "".join(map(str, rs)), p3(rs),
                            "".join(map(str, tail)), p3(tail), len(tail)))


# ------------------------------------------------------------------- bits --

def cmd_bits():
    print("== bit accounting (the mission's number) ==")
    from triangle import Triangle
    tri = Triangle.load()
    a40 = tri.rowsum(40)
    blk = sum(tri.cell(40, H) for H in range(15, 20))
    print("  a(40) block shares (banked):")
    print("    H=15..19 of row 40: %.4f%% of a(40)  (brief says 43.84%%)"
          % (100 * blk / a40))
    print("    H=15..21 of row 40: %.4f%% of a(40)"
          % (100 * sum(tri.cell(40, H) for H in range(15, 22)) / a40))
    print("    T(40,21) alone:     %.4f%% of a(40)"
          % (100 * tri.cell(40, 21) / a40))
    print()

    # the 42 law-free in-grid sleeve cells: k = 14..19, n = 2k+1..min(3k+1,40)
    cells = []
    for k in range(14, 20):
        for n in range(2 * k + 1, min(3 * k + 1, 40) + 1):
            H = n - k
            d = 3 * k + 1 - n
            cells.append((k, n, H, d, tri.provenance(n, H),
                          tri.cell(n, H) % 3))
    enum = [c for c in cells if c[4] == "real-sweep"]
    form = [c for c in cells if c[4] == "closed-form-Pk"]
    assert len(cells) == 42 and len(enum) == 27 and len(form) == 15
    assert all(8 <= c[3] <= 19 for c in enum)
    print("  the 27 enumerated law-free sleeve cells (provenance quoted from")
    print("  triangle.py provenance(n,H); d = 2k+1-H; residue = T mod 3):")
    for k, n, H, d, prov, r in sorted(enum, key=lambda c: (c[3], c[0])):
        print("    d=%2d  k=%2d  (n,H)=(%2d,%2d)  T mod 3 = %d  [%s]"
              % (d, k, n, H, r, prov))
    print()

    for label, dmax in [("d=8 only", 8), ("d=8..12", 12), ("d=8..19", 19)]:
        m = dmax + 1
        e = [c for c in enum if c[3] <= dmax]
        f = [c for c in form if c[3] <= dmax]
        e1 = len(e) * LOG2_3
        edig = sum(m - c[3] for c in e)
        fdig = sum(m - c[3] for c in f)
        print("  outcome %-9s (tower to mod 3^%d):" % (label, m))
        print("    bits against ENUMERATION error:   %5.1f  (unit check: "
              "%d cells x log2(3))" % (e1, len(e)))
        print("      full-depth variant:             %5.1f  (%d ternary "
              "digits over the same %d cells: each cell checked mod "
              "3^(m-d))" % (edig * LOG2_3, edig, len(e)))
        print("    bits against FORMULA-CHAIN error: %5.1f  (%d ternary "
              "digits over %d wired-P_k law-free cells, full depth; "
              "conditional on the frame)" % (fdig * LOG2_3, fdig, len(f)))
    print()
    print("  row-40 cells among the 27: %s"
          % [(n, H, "d=%d" % d) for k, n, H, d, p, r in enum if n == 40])
    print("  NOTE: no H=15..19 row-40 cell is touched by ANY d<=19 level;")
    print("  those cells sit at k=21..25, d=24..36 (d = 2n-3H+1 at n=40).")


if __name__ == "__main__":
    cmds = {"levels": cmd_levels, "census": cmd_census,
            "probes": cmd_probes, "d8": cmd_d8, "bits": cmd_bits}
    for arg in sys.argv[1:] or ["census", "bits"]:
        cmds[arg]()
