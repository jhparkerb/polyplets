#!/usr/bin/env python3
"""Finite-size-scaling ladder for the strip growth constants mu_H.

docs/middle-kingdom-followups-plan.md Phase 5. Supersedes the Phase-0-scoped
probe `experiments/strip_fss_probe.py` (folded in here, deleted) and turns
Table D of the plan into a reproducible section of
results/strip-growth-lambda-bounds.md.

Reproduces, from one command:
  1. The two-parameter fit  ln mu_H = ln lambda - a/H - b/H^2  on consecutive
     triples of the banked mu_H ladder (Table D).
  2. Its conditioning: perturb each mu_H by +/-1 unit in its last recorded
     decimal digit (the ladder is banked to 7 decimals -- see MU/
     LAST_DIGIT_UNIT below), all 8 sign combinations, report the spread each
     fitted parameter inherits from that input precision.
  3. Whether the substantive claims (b climbing, lambda drifting) survive
     that noise floor.
  4. The surface term H*(ln lambda - ln mu_H) and its increment-shrink
     diagnostic, at both banked lambda candidates (7.1102, 7.111).
  5. Optional third ansatz  ln mu_H = ln lambda - a/H - c*ln(H)/H^2  --
     cheap since the machinery is already here; report only, no claim.
  6. An H>=18 cost estimate, extrapolated from the measured throughputs in
     results/strip-mu-fast.md (NOT a new compute job -- H>=18 is a
     beg-and-agree item per the plan's hard rules).

mu_H values below are the banked ladder at its *original* precision --
results/strip-mu-engine-resumption.md:30 (H<=14) and
results/strip-mu-certificates.md's "the ladder extended to H=17" addendum
table, `mu_float` column, H=15..17 -- 7 decimal digits throughout. This is
the input precision Table D's fits used (confirmed in Phase 0: refitting
from the 9-decimal results/strip_mu_certificates.log mu_float moves *all
three* triples away from Table D's printed numbers, not just [11,12,13],
which only makes sense if Table D itself was fit at 7-decimal precision).

Usage: python3 experiments/strip_fss.py [--lambda 7.1102]
"""
import argparse
import itertools
import math

MU = {
    2: 2.4142136, 3: 3.4437184, 4: 4.1823214, 5: 4.7178013, 6: 5.1153245,
    7: 5.4178476, 8: 5.6533728, 9: 5.8404579, 10: 5.9916958, 11: 6.1158416,
    12: 6.2191246, 13: 6.3060713, 14: 6.3800344, 15: 6.4435408,
    16: 6.4985245, 17: 6.5464870,
}
LAST_DIGIT_UNIT = 1e-7  # every MU value above is printed to 7 decimals

TRIPLE_STARTS = (11, 13, 15)

# --- strip-mu-fast.md measured throughputs (H=16 row), for the H>=18 cost
# estimate. Not re-measured here -- cited constants, see results/
# strip-mu-fast.md's "Cost model (measured through H=16)" table.
FAST_MD_H16 = {
    'sum_S_r': 71_339_063,
    'table_mb': 563.9,
    'build_rss_gb': 4.94,
    'build_s': 23.2,
    'float_matvec_s': 0.0680,
    'exact_sweep_s': 0.561,
    'matvecs': 2280,        # fitted count at H=16, strip-mu-fast.md
}
GROWTH_PER_H = 2.95         # measured 2.95x/H, steady H=11..16
MATVEC_GROWTH_PER_H = 140   # "+~140 per H", strip-mu-fast.md
CERT_TOLERANCE_FACTOR = 1.13  # measured H=11: 120.9s vs 107.5s


def det3(m):
    return (m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1])
            - m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0])
            + m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0]))


def fit3(rows, rhs):
    """Exact 3x3 linear solve by Cramer's rule."""
    D = det3(rows)
    sols = []
    for col in range(3):
        m2 = [list(r) for r in rows]
        for i in range(3):
            m2[i][col] = rhs[i]
        sols.append(det3(m2) / D)
    return sols


def fit_triple(h1, h2, h3, mu=None):
    """Exact solve of ln mu_H = L - a/H - b/H^2 for H in (h1,h2,h3)."""
    mu = mu or MU
    rows = [(1.0, -1.0 / h, -1.0 / (h * h)) for h in (h1, h2, h3)]
    rhs = [math.log(mu[h]) for h in (h1, h2, h3)]
    L, a, b = fit3(rows, rhs)
    return math.exp(L), a, b


def fit_triple_log(h1, h2, h3, mu=None):
    """Third ansatz: ln mu_H = L - a/H - c*ln(H)/H^2."""
    mu = mu or MU
    rows = [(1.0, -1.0 / h, -math.log(h) / (h * h)) for h in (h1, h2, h3)]
    rhs = [math.log(mu[h]) for h in (h1, h2, h3)]
    L, a, c = fit3(rows, rhs)
    return math.exp(L), a, c


def conditioning(h1, h2, h3, unit=LAST_DIGIT_UNIT, fit=fit_triple):
    """Spread in the three fitted parameters over all 8 sign combinations
    of a +/-unit perturbation applied independently to each of the 3 mu_H
    inputs."""
    p0 = fit(h1, h2, h3)
    cols = [[v] for v in p0]
    for signs in itertools.product((-1, 1), repeat=3):
        mu = dict(MU)
        for h, s in zip((h1, h2, h3), signs):
            mu[h] = MU[h] + s * unit
        p = fit(h1, h2, h3, mu)
        for col, v in zip(cols, p):
            col.append(v)
    return tuple(max(c) - min(c) for c in cols)


def section_two_param():
    print("## two-parameter fit ln mu_H = ln lambda - a/H - b/H^2, exact "
          "3-point solve")
    print("(7-decimal mu_H, results/strip-mu-engine-resumption.md:30 for "
          "H<=14 / results/strip-mu-certificates.md addendum mu_float for "
          "H=15..17)")
    print(f"{'triple':>12} | {'lambda':>10} | {'a':>10} | {'b':>10}")
    fits = {}
    for h1 in TRIPLE_STARTS:
        lam, a, b = fit_triple(h1, h1 + 1, h1 + 2)
        fits[h1] = (lam, a, b)
        print(f"[{h1},{h1+1},{h1+2}]".rjust(12)
              + f" | {lam:10.5f} | {a:10.5f} | {b:10.5f}")
    return fits


def section_conditioning(fits):
    print(f"\n## conditioning: perturb each mu_H by +/-1 unit in its last"
          f" recorded digit ({LAST_DIGIT_UNIT:g}), all 8 sign combos,"
          f" report the spread")
    print(f"{'triple':>12} | {'lambda spread':>14} | {'a spread':>10}"
          f" | {'b spread':>10}")
    spreads = {}
    for h1 in TRIPLE_STARTS:
        dl, da, db = conditioning(h1, h1 + 1, h1 + 2)
        spreads[h1] = (dl, da, db)
        print(f"[{h1},{h1+1},{h1+2}]".rjust(12)
              + f" | {dl:14.2e} | {da:10.2e} | {db:10.2e}")
    return spreads


def section_noise_floor(fits, spreads):
    print("\n## does the substantive claim survive the noise floor?")
    b_vals = [fits[h1][2] for h1 in TRIPLE_STARTS]
    b_spreads = [spreads[h1][2] for h1 in TRIPLE_STARTS]
    print(f"  b across triples: {b_vals[0]:.5f} -> {b_vals[1]:.5f} ->"
          f" {b_vals[2]:.5f}  (changes {b_vals[1]-b_vals[0]:+.5f},"
          f" {b_vals[2]-b_vals[1]:+.5f}) vs b spread {min(b_spreads):.2e}"
          f"..{max(b_spreads):.2e}: change is"
          f" {abs(b_vals[1]-b_vals[0])/max(b_spreads):.0f}x-"
          f"{abs(b_vals[2]-b_vals[1])/max(b_spreads):.0f}x the noise floor")
    lam_vals = [fits[h1][0] for h1 in TRIPLE_STARTS]
    lam_spreads = [spreads[h1][0] for h1 in TRIPLE_STARTS]
    # per-rung drift: triple centers are H=12,14,16, two rungs apart.
    drift1 = (lam_vals[1] - lam_vals[0]) / 2
    drift2 = (lam_vals[2] - lam_vals[1]) / 2
    print(f"  lambda across triples: {lam_vals[0]:.5f} -> {lam_vals[1]:.5f}"
          f" -> {lam_vals[2]:.5f}  (per-rung drift {drift1:+.5f},"
          f" {drift2:+.5f}) vs lambda spread {min(lam_spreads):.2e}"
          f"..{max(lam_spreads):.2e}: drift is"
          f" {abs(drift1)/max(lam_spreads):.0f}x-"
          f"{abs(drift2)/max(lam_spreads):.0f}x the noise floor")
    top_lam = lam_vals[-1]
    print(f"  top triple lambda {top_lam:.5f} vs differential-approximant"
          f" 7.1102: overshoot {top_lam - 7.1102:+.5f}")


def section_surface_term(lam):
    print(f"\n## surface term H*(ln(lambda) - ln(mu_H)), lambda = {lam}")
    vals = {}
    for H in sorted(MU):
        vals[H] = H * (math.log(lam) - math.log(MU[H]))
        print(f"  H={H:2d}  {vals[H]:.6f}")
    print("  increments (falling per rung) and their ratio to the "
          "previous increment:")
    Hs = sorted(MU)
    incs = {}
    for i in range(1, len(Hs)):
        H = Hs[i]
        incs[H] = vals[H] - vals[Hs[i - 1]]
    for i in range(2, len(Hs)):
        H = Hs[i]
        prev = Hs[i - 1]
        ratio = incs[H] / incs[prev] if incs[prev] else float('nan')
        print(f"  H={H:2d}  inc={incs[H]:+.6f}  inc/inc_prev={ratio:.4f}"
              f"  (pure 1/H^2 predicts {((H-1)/H)**2:.4f})")
    return incs


def section_third_ansatz():
    print("\n## optional third ansatz: ln mu_H = ln lambda - a/H - "
          "c*ln(H)/H^2 (report only -- 3 free params on 16 rungs proves "
          "nothing)")
    print(f"{'triple':>12} | {'lambda':>10} | {'a':>10} | {'c':>10}")
    for h1 in TRIPLE_STARTS:
        lam, a, c = fit_triple_log(h1, h1 + 1, h1 + 2)
        print(f"[{h1},{h1+1},{h1+2}]".rjust(12)
              + f" | {lam:10.5f} | {a:10.5f} | {c:10.5f}")


def section_cost_estimate():
    print("\n## H>=18 cost estimate (extrapolated from results/"
          "strip-mu-fast.md measured throughputs -- NOT a new run; "
          "H>=18 is a beg-and-agree item)")
    row = dict(FAST_MD_H16)
    print(f"  H=16 (measured): sum|S_r|={row['sum_S_r']:,}  "
          f"table={row['table_mb']:.1f} MB  build_rss={row['build_rss_gb']:.2f} GB  "
          f"build={row['build_s']:.1f} s  float_matvec={row['float_matvec_s']:.4f} s  "
          f"matvecs~{row['matvecs']}")
    for H in (17, 18, 19, 20):
        n = H - 16
        sum_sr = row['sum_S_r'] * GROWTH_PER_H ** n
        table_mb = row['table_mb'] * GROWTH_PER_H ** n
        build_rss_gb = row['build_rss_gb'] * GROWTH_PER_H ** n
        build_s = row['build_s'] * GROWTH_PER_H ** n
        float_matvec_s = row['float_matvec_s'] * GROWTH_PER_H ** n
        exact_sweep_s = row['exact_sweep_s'] * GROWTH_PER_H ** n
        matvecs = row['matvecs'] + MATVEC_GROWTH_PER_H * n
        float_solve_s = build_s + matvecs * float_matvec_s
        # certificate ~ 1 sweep for a quick estimate (varies 3-8 sweeps
        # across H=15..17 in results/strip-mu-certificates.md)
        cert_s = float_solve_s * CERT_TOLERANCE_FACTOR + exact_sweep_s
        print(f"  H={H}: sum|S_r|~{sum_sr:,.0f}  table~{table_mb/1024:.2f} GB  "
              f"build_rss~{build_rss_gb:.1f} GB  float_solve~{float_solve_s/60:.1f} min "
              f"cert(1 sweep)~{cert_s/60:.1f} min")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--lambda_', type=float, default=7.1102, dest='lam')
    args = ap.parse_args()

    fits = section_two_param()
    spreads = section_conditioning(fits)
    section_noise_floor(fits, spreads)
    for lam in (args.lam, 7.111):
        section_surface_term(lam)
    section_third_ansatz()
    section_cost_estimate()


if __name__ == '__main__':
    main()
