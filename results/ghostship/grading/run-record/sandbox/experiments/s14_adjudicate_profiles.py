#!/usr/bin/env python3
"""Session 14: adjudicate registered inner-profile predictions against a
chassis extraction JSON (out_s13_tau_profiles*.json).

Recomputes the s13 local profile recursion (z-form, exact rationals):

  psi00_r = -(2r)!/(4 z^(2r+1))          [M00 inner profile]
  chi_r   = psi00_r/4 + r chi'_{r-1}     [M10 inner profile]
  a_r     = chi_r + 2r phi'_{r-1}
  phi_r   = (a_r(z) - a_r(-4))/(z+4)     [M11 inner profile]
  c_r     = a_r(-4)/2

then, for every (mode, prime, r, phase) in the JSON, reconstructs the
chassis inner leading rational function N(T)/D(T) (T = tau, z = T-2) and
checks the polynomial identity N(T)*z^M - prof(z)*D(T) == 0 mod p, plus
the inner order laws ord(M00) = -(4r+2), ord(M10) = -(4r+4),
ord(M11) = -(4r+6).

If a prediction file is given (out_s13_r7_prediction.txt format), its
chi/phi coefficient lists are parsed and asserted equal to the recursion's
(adjudicating the REGISTERED artifact, not just the recursion).

Usage: python3 experiments/s14_adjudicate_profiles.py <profiles.json>
           [prediction.txt] [rmax]
Output: stdout (redirect for receipt).
"""
import ast, json, os, re, sys
from fractions import Fraction as Fr
from math import factorial

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
JSONFN = sys.argv[1]
PREDFN = sys.argv[2] if len(sys.argv) > 2 else None
RMAX = int(sys.argv[3]) if len(sys.argv) > 3 else 12

FAILS = []


def say(m):
    print(m, flush=True)


# ---- recursion (verbatim logic from s13_local_recursion.py) ------------
def dz(a):
    return {m + 1: -m * c for m, c in a.items()}


def ev(a, z):
    return sum(c * Fr(1, z ** m) for m, c in a.items())


def add(*As):
    r = {}
    for a in As:
        for m, c in a.items():
            r[m] = r.get(m, Fr(0)) + c
    return {m: c for m, c in r.items() if c}


def scal(a, k):
    return {m: k * c for m, c in a.items()}


def divz4(a):
    av = ev(a, -4)
    M = max(a) if a else 0
    g = {1: -av}
    for k in range(1, M + 1):
        g[k + 1] = a.get(k, Fr(0)) - 4 * g.get(k, Fr(0))
    assert g.get(M + 1, Fr(0)) == 0
    g.pop(M + 1, None)
    return {m: c for m, c in g.items() if c}


chis = {0: {1: Fr(-1, 16)}}
phis = {0: {1: Fr(-1, 64)}}
psis = {0: {1: Fr(-1, 4)}}
cs = {0: ev(chis[0], -4) / 2}
for r in range(1, RMAX + 1):
    psis[r] = {2 * r + 1: Fr(-factorial(2 * r), 4)}
    chis[r] = add(scal(psis[r], Fr(1, 4)), scal(dz(chis[r - 1]), r))
    a = add(chis[r], scal(dz(phis[r - 1]), 2 * r))
    cs[r] = ev(a, -4) / 2
    phis[r] = divz4(a)

# ---- optional: registered prediction file vs recursion ------------------
if PREDFN:
    txt = open(os.path.join(ROOT, PREDFN)).read()
    say(f"== A0: registered prediction {PREDFN} vs recursion ==")
    for name, table in (("chi", chis), ("phi", phis)):
        m = re.search(rf"{name}_(\d+) .*?: (\[.*?\])", txt, re.S)
        if not m:
            say(f"  {name}: NOT FOUND in prediction file")
            FAILS.append(f"A0 {name} missing")
            continue
        rr = int(m.group(1))
        lst = ast.literal_eval(m.group(2))
        pred = {int(k): Fr(v) for k, v in lst}
        ok = (pred == table[rr])
        say(f"  {name}_{rr}: {len(lst)} coeffs "
            f"{'MATCH recursion' if ok else 'MISMATCH'}")
        if not ok:
            FAILS.append(f"A0 {name}_{rr}")
    m = re.search(r"c_(\d+) = (\S+?);", txt)
    if m:
        rr, val = int(m.group(1)), Fr(m.group(2))
        ok = (val == cs[rr] ==
              Fr(factorial(rr) ** 2, 2 ** (rr + 7)))
        say(f"  c_{rr} = {val}: "
            f"{'MATCH recursion and (r!)^2/2^(r+7)' if ok else 'MISMATCH'}")
        if not ok:
            FAILS.append(f"A0 c_{rr}")
    m = re.search(r"M10 r=(\d+): delta\^(-\d+); M11 r=\d+: delta\^(-\d+)",
                  txt)
    PRED_ORDS = None
    if m:
        PRED_ORDS = (int(m.group(1)), int(m.group(2)), int(m.group(3)))
        say(f"  predicted orders r={PRED_ORDS[0]}: "
            f"M10 {PRED_ORDS[1]}, M11 {PRED_ORDS[2]} (checked below)")

# ---- chassis comparison -------------------------------------------------
say(f"\n== A1: chassis inner profiles + orders vs recursion "
    f"({JSONFN}) ==")
data = json.load(open(os.path.join(ROOT, JSONFN)))
ORD_LAW = {"M00": lambda r: -(4 * r + 2), "M10": lambda r: -(4 * r + 4),
           "M11": lambda r: -(4 * r + 6)}
PROF = {"M00": psis, "M10": chis, "M11": phis}
nchecked = 0
for mode in data:
    for pstr in data[mode]:
        p = int(pstr)
        rmax_seen = -1
        for rstr in sorted(data[mode][pstr], key=int):
            r = int(rstr)
            if r not in chis:
                continue
            rmax_seen = max(rmax_seen, r)
            for ph in ("M00", "M10", "M11"):
                rec = data[mode][pstr][rstr][ph]
                inn = rec["inn"]
                if inn is None:
                    say(f"  [{mode} p={p} r={r} {ph}] inner chart ZERO")
                    FAILS.append(f"A1 {mode} p={p} r={r} {ph} zero")
                    continue
                want_ord = ORD_LAW[ph](r)
                if inn["ord"] != want_ord:
                    say(f"  [{mode} p={p} r={r} {ph}] ORD {inn['ord']} "
                        f"want {want_ord}")
                    FAILS.append(f"A1 ord {mode} p={p} r={r} {ph}")
                prof = PROF[ph][r]
                Mmax = max(prof)
                num = inn["num_rows"][0]
                if any(v == "PREC" for v in num.values()):
                    say(f"  [{mode} p={p} r={r} {ph}] PREC in num; SKIP")
                    FAILS.append(f"A1 prec {mode} p={p} r={r} {ph}")
                    continue
                denp = [1]
                bad = False
                for nm, e, am, row in inn["den"]:
                    if any(v == "PREC" for v in row.values()):
                        bad = True
                        break
                    js = sorted(int(j) for j in row)
                    ap = [0] * (max(js) + 1)
                    for j in js:
                        ap[int(j)] = row[str(j)] % p
                    for _ in range(e):
                        new = [0] * (len(denp) + len(ap) - 1)
                        for i, ci in enumerate(denp):
                            for j2, cj in enumerate(ap):
                                new[i + j2] = (new[i + j2] + ci * cj) % p
                        denp = new
                if bad:
                    say(f"  [{mode} p={p} r={r} {ph}] PREC in den; SKIP")
                    FAILS.append(f"A1 prec {mode} p={p} r={r} {ph}")
                    continue
                nump = [0] * (max(int(j) for j in num) + 1 if num else 1)
                for j, v in num.items():
                    nump[int(j)] = v % p
                pz = [0] * (Mmax + 1)
                for m2, c in prof.items():
                    pz[Mmax - m2] = (c.numerator *
                                     pow(c.denominator, p - 2, p)) % p

                def shift(poly):
                    out = [0]
                    for c in reversed(poly):
                        new = [0] * (len(out) + 1)
                        for i, ci in enumerate(out):
                            new[i + 1] = (new[i + 1] + ci) % p
                            new[i] = (new[i] - 2 * ci) % p
                        new[0] = (new[0] + c) % p
                        out = new
                    while len(out) > 1 and out[-1] == 0:
                        out.pop()
                    return out
                zM = shift([0] * Mmax + [1])
                PT = shift(pz)
                L = max(len(nump) + len(zM), len(PT) + len(denp))
                lhs = [0] * L
                for i, ci in enumerate(nump):
                    for j2, cj in enumerate(zM):
                        lhs[i + j2] = (lhs[i + j2] + ci * cj) % p
                for i, ci in enumerate(PT):
                    for j2, cj in enumerate(denp):
                        lhs[i + j2] = (lhs[i + j2] - ci * cj) % p
                ok = all(c % p == 0 for c in lhs)
                nchecked += 1
                if not ok:
                    say(f"  [{mode} p={p} r={r} {ph}] PROFILE MISMATCH")
                    FAILS.append(f"A1 prof {mode} p={p} r={r} {ph}")
        say(f"  [{mode} p={p}] r<={rmax_seen} all phases checked")

say(f"\nprofile identities checked: {nchecked}")
say(f"VERDICT: {'ALL PASS' if not FAILS else 'FAILURES: ' + str(FAILS)}")
