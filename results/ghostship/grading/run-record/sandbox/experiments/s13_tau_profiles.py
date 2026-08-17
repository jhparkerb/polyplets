#!/usr/bin/env python3
"""Session 13: tau-profiles of the moment phases at the collision.

Reuses the s12 delta-Laurent chassis (imported from s12_delta_local.py,
UNMODIFIED) to build levels r = 0..MAXR, then for each phase G in
(M00, M10, M11) extracts the LOCAL structure at s* = 2:

  * Newton table: numerator recentered at s = 2 + w, coefficients
    n_j(delta) of w^j listed as (j, val n_j, leading coeffs);
  * chart profiles: for chart weight k (k=1 outer w = delta*tau,
    k=2 inner w = delta^2*tau) the leading form
        G(2 + delta^k tau) = delta^ord * N(tau)/D(tau) * (1 + O(delta)),
    computed exactly in F_p((delta))(tau): numerator profile from the
    Newton table (minimize val n_j + k*j), denominator profile from the
    SAME machinery applied to each denominator atom (1-xs, D00, PK1).

Two primes, CRT + Wang rational reconstruction => exact rational profile
coefficients.  Receipts: out_s13_tau_profiles.txt (human),
out_s13_tau_profiles.json (full tables mod both primes + reconstructed).

Usage: python3 experiments/s13_tau_profiles.py [MAXR] [NUCAP] [mode]
"""
import sys, os, json, time
from math import comb
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
sys.path.insert(0, HERE)

MAXR = int(sys.argv[1]) if len(sys.argv) > 1 else 6
NUCAP_ARG = int(sys.argv[2]) if len(sys.argv) > 2 else 128
MODEARG = sys.argv[3] if len(sys.argv) > 3 else "both"

# import chassis with a clean argv so its module-level arg parse is inert
_argv = sys.argv
sys.argv = [sys.argv[0]]
import s12_delta_local as CH
sys.argv = _argv

PRIMES = [(1 << 61) - 1, 10 ** 18 + 9]
OUT = []


def say(m):
    print(m, flush=True)
    OUT.append(str(m))


def recenter(spoly, P):
    """coeffs n_j of (s-2)^j: n_j = sum_i cs[i] C(i,j) 2^(i-j), as L."""
    cs = spoly.cs
    out = []
    for j in range(len(cs)):
        acc = CH.L()
        for i in range(j, len(cs)):
            k = comb(i, j) * pow(2, i - j, P)
            acc = acc + cs[i].scal(k)
        out.append(acc)
    return out


def newton_table(njs, nlead=3):
    """[(j, val, [leading coeffs] or None-if-zero-to-precision, pr)]"""
    tab = []
    for j, n in enumerate(njs):
        if n.d:
            v = n.vlb()
            tab.append((j, v, [n.get(v + i) for i in range(nlead)], n.pr))
        else:
            tab.append((j, None, [], n.pr))
    return tab


def chart_profile(njs, k, nsub=2):
    """leading + nsub-1 subleading rows of the chart-k form of sum n_j w^j.
    Returns (m, rows) with rows[t] = dict j -> coeff of delta^(m+t) tau^j,
    or (None, []) if identically zero. Precision-checked."""
    m = None
    for j, n in enumerate(njs):
        if n.d:
            c = n.vlb() + k * j
            if m is None or c < m:
                m = c
    if m is None:
        return None, []
    rows = []
    for t in range(nsub):
        row = {}
        for j, n in enumerate(njs):
            e = m + t - k * j
            if e < n.pr:
                c = n.get(e)
                if c:
                    row[j] = c
            else:
                row[j] = "PREC"      # unknown at this order
        rows.append(row)
    return m, rows


def frat_chart(G, ctx, P, k, nsub=2):
    """chart-k leading form of FRat G: (ord, numrows, [(atomname, e_i,
    atom_m, atomrow0)]) with ord = num_m - sum e_i atom_m."""
    njs = recenter(G.num, P)
    m, rows = chart_profile(njs, k, nsub)
    if m is None:
        return None
    den = []
    ordv = m
    for i, name in enumerate(("one_m_xs", "D00", "PK1")):
        e = G.e[i]
        if e:
            am, arows = chart_profile(recenter(ctx.atoms[i], P), k, 1)
            den.append((name, e, am, arows[0]))
            ordv -= e * am
    return dict(num_m=m, num_rows=rows, den=den, ord=ordv)


# ---------------- rational reconstruction --------------------------------
def wang(a, m):
    """rational p/q = a mod m with |p|, q <= sqrt(m/2); None if none."""
    a %= m
    r0, r1 = m, a
    s0, s1 = 0, 1
    bound = int((m // 2) ** 0.5)
    while r1 > bound:
        q = r0 // r1
        r0, r1 = r1, r0 - q * r1
        s0, s1 = s1, s0 - q * s1
    if abs(s1) > bound or s1 == 0:
        return None
    if r1 % (g := __import__("math").gcd(r1, abs(s1))) == 0 and g > 1:
        return None
    p, q = (r1, s1) if s1 > 0 else (-r1, -s1)
    return Fr(p, q)


def crt2(a1, a2, p1, p2):
    m = p1 * p2
    return (a1 * p2 * pow(p2, -1, p1) + a2 * p1 * pow(p1, -1, p2)) % m


def recon(c1, c2, p1, p2):
    if c1 == "PREC" or c2 == "PREC":
        return "PREC"
    v = crt2(c1, c2, p1, p2)
    w = wang(v, p1 * p2)
    return str(w) if w is not None else f"?{v}"


# ---------------- main ---------------------------------------------------
def run():
    modes = ["king", "poly"] if MODEARG == "both" else [MODEARG]
    say(f"s13 tau-profiles: MAXR={MAXR} NUCAP={NUCAP_ARG} modes={modes} "
        f"primes={PRIMES}")
    data = {}          # data[mode][prime] = per-level dicts
    for mode in modes:
        data[mode] = {}
        for p in PRIMES:
            CH.P = p
            CH.NUCAP = NUCAP_ARG
            t0 = time.time()
            ctx, levels, doms = CH.solve_all(mode == "king", MAXR)
            say(f"[{mode} p={p}] solve {time.time()-t0:.0f}s")
            per = {}
            for r, Lr in enumerate(levels):
                rec = {}
                for ph in ("M00", "M10", "M11"):
                    G = Lr[ph]
                    njs = recenter(G.num, p)
                    rec[ph] = dict(
                        e=list(G.e),
                        newton=newton_table(njs),
                        out=frat_chart(G, ctx, p, 1),
                        inn=frat_chart(G, ctx, p, 2),
                        val1=CH.lead_data(Lr[{"M00": "M001",
                                              "M10": "M101",
                                              "M11": "M111"}[ph]], 4))
                per[r] = rec
            data[mode][p] = per
    p1, p2 = PRIMES

    # ---- report with CRT-reconstructed rationals ----
    for mode in modes:
        A, B = data[mode][p1], data[mode][p2]
        say(f"\n================ {mode} ================")
        for r in range(MAXR + 1):
            say(f"-- r={r} --")
            for ph in ("M00", "M10", "M11"):
                a, b = A[r][ph], B[r][ph]
                say(f"  {ph}: den atom exps (1-xs,D00,PK1)={a['e']}")
                nt_a, nt_b = a["newton"], b["newton"]
                rows = []
                for (j, v, cs, pr), (j2, v2, cs2, pr2) in zip(nt_a, nt_b):
                    if v is None:
                        rows.append(f"    j={j}: 0 (pr {pr})")
                        continue
                    if v != v2:
                        rows.append(f"    j={j}: VAL MISMATCH {v}/{v2}")
                        continue
                    lead = [recon(c, c2, p1, p2)
                            for c, c2 in zip(cs, cs2)]
                    rows.append(f"    j={j}: val={v} lead={lead}")
                say("\n".join(rows))
                for chart in ("out", "inn"):
                    ca, cb = a[chart], b[chart]
                    if ca is None:
                        say(f"    {chart}: zero")
                        continue
                    if ca["ord"] != cb["ord"] or ca["num_m"] != cb["num_m"]:
                        say(f"    {chart}: ORD MISMATCH {ca['ord']}/"
                            f"{cb['ord']}")
                        continue
                    nr = []
                    for t, (ra, rb) in enumerate(zip(ca["num_rows"],
                                                     cb["num_rows"])):
                        js = sorted(set(ra) | set(rb))
                        terms = [f"{recon(ra.get(j, 0), rb.get(j, 0), p1, p2)}"
                                 f"*T^{j}" for j in js]
                        nr.append(f"[d^{ca['num_m']+t}] " +
                                  (" + ".join(terms) if terms else "0"))
                    dstr = []
                    for (nm, e, am, row), (nm2, e2, am2, row2) in zip(
                            ca["den"], cb["den"]):
                        js = sorted(set(row) | set(row2))
                        poly = " + ".join(
                            f"{recon(row.get(j, 0), row2.get(j, 0), p1, p2)}"
                            f"*T^{j}" for j in js)
                        dstr.append(f"({poly})^{e}[d^{am}x{e}]")
                    say(f"    {chart}: ord={ca['ord']}  num: "
                        + " ; ".join(nr))
                    say(f"         den: " + " * ".join(dstr))
                # value at s=1
                (v1a, c1a), (v1b, c1b) = a["val1"], b["val1"]
                if v1a is not None and v1a == v1b:
                    lead = [recon(c, c2, p1, p2)
                            for c, c2 in zip(c1a, c1b)]
                    say(f"    val@s=1: val={v1a} lead={lead}")
    suf = os.environ.get("S13_OUT_SUFFIX", "")
    with open(os.path.join(ROOT, f"out_s13_tau_profiles{suf}.json"),
              "w") as fp:
        json.dump({m: {str(p): {str(r): {ph: {kk: vv for kk, vv in
                  rec.items() if kk != "val1"}
                  for ph, rec in per.items()}
                  for r, per in dd.items()}
                  for p, dd in md.items()} for m, md in data.items()}, fp)
    with open(os.path.join(ROOT, f"out_s13_tau_profiles{suf}.txt"),
              "w") as fp:
        fp.write(__doc__ + "\n" + "\n".join(OUT) + "\n")
    say(f"receipts: out_s13_tau_profiles{suf}.txt, "
        f"out_s13_tau_profiles{suf}.json")


if __name__ == "__main__":
    run()
