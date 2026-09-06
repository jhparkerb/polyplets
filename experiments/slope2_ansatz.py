"""Which asymptotic form, if any, can 20 points of T(2H,H) support?

Discipline, fixed before any number is read:
  * fit window H in [H0, 17]; H = 18,19,20 held out and predicted.
  * every model is linear in log space -- no optimizer, no starting guess.
  * CONTROL: the identical pipeline is run on 20 terms of a(n), whose answer is
    known independently from 40 terms + differential approximants
    (lambda = 7.110(1), theta = -1.000(1), results/growth-constant.md).
    Whatever resolving power the pipeline has there is the ceiling here.
  * CONFUSION: synthesize from each model at its own fitted parameters, refit
    all models, and see whether the generating model actually wins.
"""
import glob, re, math
import numpy as np

T, A = {}, {}
for f in glob.glob('results/ns_a40/perheight/h*.out'):
    H = int(re.findall(r'h(\d+)', f)[0])
    for line in open(f):
        p = line.split()
        if len(p) == 2:
            n, v = int(p[0]), int(p[1])
            T[(n, H)] = v
            A[n] = A.get(n, 0) + v

# basis functions in log space
BASIS = {
    'const': lambda H: np.ones_like(H, dtype=float),
    'H':     lambda H: H.astype(float),
    'lnH':   lambda H: np.log(H),
    'sqrtH': lambda H: np.sqrt(H),
    'invH':  lambda H: 1.0 / H,
    'invH2': lambda H: 1.0 / H ** 2,
}
MODELS = {
    'M1  C.mu^H':                    ['const', 'H'],
    'M2  C.mu^H.H^th':               ['const', 'H', 'lnH'],
    'M3  C.mu^H.H^th.e^{c/H}':       ['const', 'H', 'lnH', 'invH'],
    'M4  C.mu^H.H^-1.5 (locked)':    ['const', 'H'],            # theta pinned below
    'M5  C.mu^H.H^th.nu^sqrtH':      ['const', 'H', 'lnH', 'sqrtH'],
    'M7  C.mu^H.H^th.e^{c/H+d/H^2}': ['const', 'H', 'lnH', 'invH', 'invH2'],
}
LOCKED = {'M4  C.mu^H.H^-1.5 (locked)': -1.5}

def design(names, H):
    return np.column_stack([BASIS[b](H) for b in names])

def fit_predict(name, H, y, Hfit, yfit, Hout):
    names = MODELS[name]
    off = LOCKED.get(name, 0.0)
    Xf = design(names, Hfit)
    c, *_ = np.linalg.lstsq(Xf, yfit - off * np.log(Hfit), rcond=None)
    pred = design(names, Hout) @ c + off * np.log(Hout)
    return c, pred

def report(label, Hs, vals, fitmax, outs, H0):
    H = np.array(Hs, float); y = np.log(np.array(vals, dtype=float))
    m_fit = (H >= H0) & (H <= fitmax)
    m_out = np.isin(H, outs)
    print(f"\n--- {label}: fit H in [{H0},{fitmax}] ({m_fit.sum()} pts), holdout H={list(outs)} ---")
    print(f"{'model':32s} {'mu':>10s} {'theta':>9s}  {'max holdout rel err':>20s}")
    rows = []
    for name in MODELS:
        c, pred = fit_predict(name, H, y, H[m_fit], y[m_fit], H[m_out])
        err = np.max(np.abs(np.expm1(pred - y[m_out])))
        names = MODELS[name]
        mu = math.exp(c[names.index('H')])
        th = LOCKED.get(name, c[names.index('lnH')] if 'lnH' in names else float('nan'))
        print(f"{name:32s} {mu:10.5f} {th:9.4f}  {err:19.3%}")
        rows.append((name, mu, th, err))
    return rows

# ---------- CONTROL: a(n), 20 terms, answer known from 40 terms + DAs ----------
ns = list(range(21, 41))                       # last 20 terms of a(n)
report("CONTROL a(n), last 20 terms (truth: lambda=7.110, theta=-1.000)",
       ns, [A[n] for n in ns], fitmax=37, outs=(38, 39, 40), H0=21)
ns2 = list(range(1, 41))                       # all 40, for reference
report("REFERENCE a(n), all 40 terms (same truth)",
       ns2, [A[n] for n in ns2], fitmax=37, outs=(38, 39, 40), H0=5)

# ---------- the real question ----------
Hs = [H for H in range(1, 21) if (2 * H, H) in T and T[(2 * H, H)]]
S = [T[(2 * H, H)] for H in Hs]
for H0 in (3, 5, 7):
    report(f"SLOPE-2 T(2H,H), onset H0={H0}", Hs, S, fitmax=17, outs=(18, 19, 20), H0=H0)

# ---------- CONFUSION: can these models be told apart at this length? ----------
print("\n=== confusion matrix: rows = generating model, cols = fitted model ===")
print("    entry = max holdout rel err; the generating model should win its own row\n")
H = np.array(Hs, float); y = np.log(np.array(S, dtype=float))
m_fit = (H >= 5) & (H <= 17); m_out = np.isin(H, (18, 19, 20))
synth = {}
for gen in MODELS:
    c, _ = fit_predict(gen, H, y, H[m_fit], y[m_fit], H[m_out])
    off = LOCKED.get(gen, 0.0)
    ln = design(MODELS[gen], H) @ c + off * np.log(H)
    synth[gen] = np.log(np.round(np.exp(ln)))          # integer-rounded, like real data
hdr = "".join(f"{n.split()[0]:>9s}" for n in MODELS)
print(f"{'generator':32s}{hdr}")
for gen in MODELS:
    ys = synth[gen]
    line = ""
    best, bestname = 1e9, None
    for fitm in MODELS:
        c, pred = fit_predict(fitm, H, ys, H[m_fit], ys[m_fit], H[m_out])
        e = np.max(np.abs(np.expm1(pred - ys[m_out])))
        line += f"{e:9.2%}" if e < 10 else f"{'>1000%':>9s}"
        if e < best: best, bestname = e, fitm
    flag = "OK" if bestname == gen else f"WRONG WINNER: {bestname.split()[0]}"
    print(f"{gen:32s}{line}   {flag}")

print("\n=== theta locked, mu free: which exponents survive the holdout? ===")
print("(same protocol; control row first so the resolving power is visible)")
def locked_scan(label, Hs, vals, fitmax, outs, H0):
    H = np.array(Hs, float); y = np.log(np.array(vals, dtype=float))
    m_fit = (H >= H0) & (H <= fitmax); m_out = np.isin(H, outs)
    print(f"\n{label}")
    print(f"{'theta':>8s} {'mu':>10s} {'max holdout rel err':>20s}")
    for th in (0.5, 0.0, -0.25, -0.5, -0.75, -1.0, -1.25, -1.5, -2.0):
        X = design(['const', 'H'], H[m_fit])
        c, *_ = np.linalg.lstsq(X, y[m_fit] - th * np.log(H[m_fit]), rcond=None)
        pred = design(['const', 'H'], H[m_out]) @ c + th * np.log(H[m_out])
        e = np.max(np.abs(np.expm1(pred - y[m_out])))
        print(f"{th:8.2f} {math.exp(c[1]):10.5f} {e:19.3%}")

locked_scan("CONTROL a(n) last 20 terms (truth theta = -1.000)",
            list(range(21, 41)), [A[n] for n in range(21, 41)], 37, (38, 39, 40), 21)
locked_scan("SLOPE-2 T(2H,H), H0=5", Hs, S, 17, (18, 19, 20), 5)

print("\n=== control on a KNOWN poly-times-exponential: s=1 k=2, truth = quadratic * 3^H ===")
def locked_scan2(label, Hs, vals, fitmax, outs, H0, thetas):
    H = np.array(Hs, float); y = np.log(np.array(vals, dtype=float))
    m_fit = (H >= H0) & (H <= fitmax); m_out = np.isin(H, outs)
    print(f"\n{label}\n{'theta':>8s} {'mu':>10s} {'max holdout rel err':>20s}")
    for th in thetas:
        X = design(['const', 'H'], H[m_fit])
        c, *_ = np.linalg.lstsq(X, y[m_fit] - th * np.log(H[m_fit]), rcond=None)
        pred = design(['const', 'H'], H[m_out]) @ c + th * np.log(H[m_out])
        print(f"{th:8.2f} {math.exp(c[1]):10.5f} "
              f"{np.max(np.abs(np.expm1(pred - y[m_out]))):19.3%}")

Hk = [H for H in range(1, 21) if (H + 2, H) in T and T[(H + 2, H)]]
Sk = [T[(H + 2, H)] for H in Hk]
locked_scan2("s=1 k=2 (T(H+2,H)), same 20-point window as the slope-2 slice",
             Hk[:20], Sk[:20], 17, (18, 19, 20), 5, (2.5, 2.25, 2.0, 1.75, 1.5, 1.0, 0.0))
