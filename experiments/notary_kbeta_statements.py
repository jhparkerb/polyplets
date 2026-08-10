#!/usr/bin/env python3
"""Notary piece K, wave K-beta: pre-verify every skeleton statement.

Verifies numerically, against depth1_gap_walk.transitions (the independent
source), every statement the wave K-beta skeletons assert
(`GapWalkExact.lean`, `GapWalkColumns.lean`), in the exact form stated:

  b1. the start packages: startCount = (4,1,0,4,|6), bareCount = (1,0,0,1,|1)
      in the StartData shape (j01, j02, p1=0, p02, pt);
  b2. pE m 1 = 0 for all m, both starts;
  b3. the step recurrences with the stated Icc source ranges:
        jE(m+1, gp) = sum_{g in [1, 2m+2]} jE(m,g) stepMul(g,J,gp,J)
                    + sum_{g in [1, 3]}    pE(m,g) stepMul(g,P,gp,J)
        pE(m+1, gp) = sum_{g in [1, 2m+2]} jE(m,g) stepMul(g,J,gp,P)
                    + sum_{g in [1, gp+2]} pE(m,g) stepMul(g,P,gp,P)   (gp>=2)
      against the big-cap walk (sources outside the ranges must contribute 0);
  b4. J-support: jE(m, g) = 0 for g > 2m+2;
  b5. the ten column identities of GapWalkColumns.lean, coefficient-wise in y
      to order YO, both starts, each in its exact Lean statement form
      (J columns u^3..u^6 + generic, P columns u^4..u^6 + generic, pY 1 = 0);
  b6. the end-functional evaluations:
        qEndF   = 4 jE(m,1) + 5 jE(m,2) + 6 sum_{g in [3, 2m+2]} jE(m,g)
                + 2 pE(m,1) + pE(m,2)
        bareEndF = jE(m,1) + jE(m,2) + sum_{g in [3, 2m+2]} jE(m,g)
      against the full-sum definitions over all gaps <= cap, and the interior
      qEndF stream against the banked walkFamilies first coordinates
      (GapWalkBridge.walkFamilies19 rows, W(2^l) for l = 1..8: the wave's
      walkFamilies_entry bridge).

Exact command:
  python3 experiments/notary_kbeta_statements.py \
      | tee build/notary_kbeta_statements.log
Target machine: gympie (local).  Predicted cost: < 30 s, one core, tiny.
Kill/resume: stateless; rerun from scratch.
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from depth1_gap_walk import transitions                          # noqa: E402

YO = 14                       # y-orders of walk data
CAP = 4 * YO + 40             # cone margin: exact for g <= CAP - 2*YO
t0 = time.time()
checks = 0


def stage(name):
    print(f"  [{time.time() - t0:6.1f}s] {name}", flush=True)


def fail(msg):
    print(f"FAIL: {msg}", flush=True)
    sys.exit(1)


ROWS = {}
for g in range(1, CAP + 1):
    for c in 'JP':
        ROWS[(g, c)] = transitions(g, c, CAP)


def step_mul(g, c, gp, cp):
    return ROWS[(g, c)].get((gp, cp), 0)


def run_walk(start):
    j = [[0] * (CAP + 1) for _ in range(YO + 1)]
    p = [[0] * (CAP + 1) for _ in range(YO + 1)]
    for (g, c), v in start.items():
        (j if c == 'J' else p)[0][g] = v
    for m in range(YO):
        for g in range(1, CAP + 1):
            for c, arr in (('J', j), ('P', p)):
                v = arr[m][g]
                if not v:
                    continue
                for (gp, cp), w in ROWS[(g, c)].items():
                    (j if cp == 'J' else p)[m + 1][gp] += v * w
    return j, p


# b1: start packages -----------------------------------------------------
# StartData F j01 j02 p02 pt: F(1,J)=j01, F(2,J)=j02, F(1,P)=0, F(2,P)=p02,
# F(g>=3,J)=0, F(g>=3,P)=pt.
START = {
    'int':  dict(j01=4, j02=1, p02=4, pt=6),
    'bare': dict(j01=1, j02=0, p02=1, pt=1),
}


def start_vec(d):
    v = {(1, 'J'): d['j01'], (2, 'J'): d['j02'], (2, 'P'): d['p02']}
    for g in range(3, CAP + 1):
        v[(g, 'P')] = d['pt']
    return {k: w for k, w in v.items() if w}


# the reference start vectors, from depth1_gap_walk's own convention
# (startCount / bareCount of GapWalk.lean; values re-asserted by
# notary_k_measure m1 against W2.check_walk)
if start_vec(START['int']) != {(1, 'J'): 4, (2, 'J'): 1, (2, 'P'): 4,
                               **{(g, 'P'): 6 for g in range(3, CAP + 1)}}:
    fail("interior StartData package mis-stated")
if start_vec(START['bare']) != {(1, 'J'): 1,
                                **{(g, 'P'): 1 for g in range(2, CAP + 1)}}:
    fail("bare StartData package mis-stated")
stage("b1: StartData packages (4,1,0,4|6) and (1,0,0,1|1)")

WALKS = {name: run_walk(start_vec(d)) for name, d in START.items()}


def jE(w, m, g):
    return w[0][m][g] if 1 <= g <= CAP else 0


def pE(w, m, g):
    return w[1][m][g] if 1 <= g <= CAP else 0


# b2, b4 -----------------------------------------------------------------
for name, w in WALKS.items():
    for m in range(YO + 1):
        if pE(w, m, 1) != 0:
            fail(f"pE({m},1) != 0 ({name})")
        for g in range(2 * m + 3, CAP + 1):
            if jE(w, m, g) != 0:
                fail(f"J-support violated ({name}) m={m} g={g}")
stage("b2: pE m 1 = 0; b4: J-support <= 2m+2, both starts")

# b3: step recurrences with the stated source ranges ---------------------
GP_CHECK = CAP - 2 * YO - 4   # targets safely inside the exact cone
for name, w in WALKS.items():
    for m in range(YO):
        for gp in range(1, GP_CHECK + 1):
            want = jE(w, m + 1, gp)
            got = (sum(jE(w, m, g) * step_mul(g, 'J', gp, 'J')
                       for g in range(1, 2 * m + 3))
                   + sum(pE(w, m, g) * step_mul(g, 'P', gp, 'J')
                         for g in range(1, 4)))
            if want != got:
                fail(f"jE_step ({name}) m={m} gp={gp}: {want} != {got}")
            checks += 1
            if gp >= 2:
                want = pE(w, m + 1, gp)
                got = (sum(jE(w, m, g) * step_mul(g, 'J', gp, 'P')
                           for g in range(1, 2 * m + 3))
                       + sum(pE(w, m, g) * step_mul(g, 'P', gp, 'P')
                             for g in range(1, gp + 3)))
                if want != got:
                    fail(f"pE_step ({name}) m={m} gp={gp}: {want} != {got}")
                checks += 1
stage(f"b3: jE_step / pE_step Icc ranges, both starts ({checks} checks)")

# b5: the ten column identities, coefficient-wise ------------------------
# Series X * S has coeff 0 = 0 and coeff (m+1) = coeff m of S; C c has
# coeff 0 = c.  Each identity below is (lhs column) = const + X * (rhs),
# checked at every y-coefficient 0..YO (rhs read at order m for coeff m+1,
# rhs orders 0..YO-1).
for name, w in WALKS.items():
    d = START[name]

    def jY(g, m):
        return jE(w, m, g)

    def pY(g, m):
        return pE(w, m, g)

    def Jm(m):
        return sum(jE(w, m, g) for g in range(3, 2 * m + 3))

    def f(g, m):
        return pY(g, m) - 2 * jY(g, m)

    def check(label, lhs_at, const, rhs_at):
        for m in range(YO + 1):
            want = lhs_at(m)
            got = (const if m == 0 else 0) + (rhs_at(m - 1) if m >= 1 else 0)
            if want != got:
                fail(f"{label} ({name}) coeff {m}: {want} != {got}")

    check("jY_col_one", lambda m: jY(1, m), d['j01'],
          lambda m: 5 * jY(1, m) + 6 * jY(2, m) + 8 * Jm(m) - jY(3, m)
          + 2 * pY(2, m) + pY(3, m))
    check("jY_col_two", lambda m: jY(2, m), d['j02'],
          lambda m: 2 * jY(1, m) + 3 * jY(2, m) + 2 * Jm(m) + 2 * jY(3, m)
          + jY(4, m) + 2 * pY(2, m))
    check("jY_col_three", lambda m: jY(3, m), 0,
          lambda m: jY(1, m) + 2 * jY(2, m) + 3 * jY(3, m) + 2 * jY(4, m)
          + jY(5, m))
    check("jY_col_four", lambda m: jY(4, m), 0,
          lambda m: jY(2, m) + 2 * jY(3, m) + 3 * jY(4, m) + 2 * jY(5, m)
          + jY(6, m))
    for k in range(0, 20):
        check(f"jY_col_generic k={k}", lambda m, k=k: jY(k + 5, m), 0,
              lambda m, k=k: jY(k + 7, m) + 2 * jY(k + 6, m)
              + 3 * jY(k + 5, m) + 2 * jY(k + 4, m) + jY(k + 3, m))
    check("pY_col_two", lambda m: pY(2, m), d['p02'],
          lambda m: f(4, m) + 2 * f(3, m) + 8 * Jm(m) + 4 * jY(1, m)
          + 4 * jY(2, m) + pY(2, m))
    check("pY_col_three", lambda m: pY(3, m), d['pt'],
          lambda m: f(5, m) + 2 * f(4, m) + 3 * f(3, m) + 12 * Jm(m)
          + 6 * jY(1, m) + 6 * jY(2, m) + 4 * pY(2, m))
    check("pY_col_four", lambda m: pY(4, m), d['pt'],
          lambda m: f(6, m) + 2 * f(5, m) + 3 * f(4, m) + 2 * f(3, m)
          + 12 * Jm(m) + 8 * jY(1, m) + 8 * jY(2, m) + 3 * pY(2, m))
    for k in range(0, 20):
        check(f"pY_col_generic k={k}", lambda m, k=k: pY(k + 5, m), d['pt'],
              lambda m, k=k: f(k + 7, m) + 2 * f(k + 6, m) + 3 * f(k + 5, m)
              + 2 * f(k + 4, m) + f(k + 3, m) + 12 * Jm(m) + 8 * jY(1, m)
              + 10 * jY(2, m) + 2 * pY(2, m))
stage("b5: all ten column identities, y-orders <= 14, generic k <= 19, "
      "both starts")

# b6: end-functional evaluations -----------------------------------------
def q_weight(g, c):
    if c == 'J':
        return g + 3 if g <= 2 else 6
    return 3 - g if g <= 2 else 0


qint = []
for name, w in WALKS.items():
    for m in range(YO + 1):
        full_q = sum(q_weight(g, c) * (jE(w, m, g) if c == 'J'
                                       else pE(w, m, g))
                     for g in range(1, CAP + 1) for c in 'JP')
        stated_q = (4 * jE(w, m, 1) + 5 * jE(w, m, 2)
                    + 6 * sum(jE(w, m, g) for g in range(3, 2 * m + 3))
                    + 2 * pE(w, m, 1) + pE(w, m, 2))
        if full_q != stated_q:
            fail(f"qEndF eval ({name}) m={m}: {full_q} != {stated_q}")
        full_b = sum(jE(w, m, g) for g in range(1, CAP + 1))
        stated_b = (jE(w, m, 1) + jE(w, m, 2)
                    + sum(jE(w, m, g) for g in range(3, 2 * m + 3)))
        if full_b != stated_b:
            fail(f"bareEndF eval ({name}) m={m}: {full_b} != {stated_b}")
        if name == 'int':
            qint.append(stated_q)
stage("b6: qEndF / bareEndF restricted reads = full sums, both starts")

# walkFamilies bridge: interior qEndF stream = W(2^l), banked first
# coordinates of walkFamilies (GapWalkBridge.walk_table_19, rows 1..8)
W_BANKED = [25, 339, 4778, 68314, 981085, 14115141, 203235615, 2927318947]
if qint[:8] != W_BANKED:
    fail(f"interior qEndF stream != banked W(2^l): {qint[:8]}")
stage("b6: interior qEndF stream matches banked W(2^l), l = 1..8")

print(f"ALL PASS ({time.time() - t0:.1f}s)")
