#!/usr/bin/env python3
"""How much of the strip ladder's non-analyticity is really lambda's error bar?

`results/strip-growth-lambda-bounds.md` closes
`results/unexplored-avenues.md` idea 6.1 (the central-charge finite-size fit)
on one diagnostic: the surface term

    S(H) = H * (ln lambda - ln mu_H)

is still falling at H = 17 and its increments shrink ~6.5% per rung where a
clean 1/H^2 correction to ln mu_H predicts ~11.4%.  The conclusion drawn is
that there is a term between 1/H and 1/H^2 -- most likely logarithmic -- that
the two-parameter ansatz cannot see, hence no 1/H^2 coefficient and hence no
central charge can be read off this ladder.

That diagnostic feeds lambda in as a constant.  It is not one: it is
7.1102(1) from differential approximants, an *estimate*.  And the surface term
is exactly the place where an error in lambda is maximally dangerous, because

    ln lambda -> ln lambda + d   ==>   S(H) -> S(H) + H*d

adds a term LINEAR in H.  Its increments pick up a constant +d, which does not
decay at all, so a lambda that is slightly too small makes any correction look
slower-decaying than it is.  The existing note tests two lambda values, 7.1102
and 7.111, and finds the reading unchanged -- but those differ by 8e-4, which
is the quoted error bar, not the range over which the reading could flip.

This script asks the question the other way round.  Rather than assuming
lambda and reading the exponent, it solves for the lambda that WOULD make the
surface term decay at any given rate, and reports how far that lambda is from
the independent estimate.  Three outputs:

  1. lambda_star -- the lambda at which the top-rung increment ratio equals
     the clean-1/H^2 prediction.  If lambda_star sits inside the independent
     estimate's error bar, the non-analyticity reading is an artifact of that
     error bar and the banked conclusion needs correcting.  If it sits far
     outside, the reading survives WITH A MARGIN, which is a stronger
     statement than the note currently makes.
  2. The effective exponent q of the surface term's own correction,
     S(H) = S_inf + c*H^-q, read off the increment ratios at each lambda --
     the measurement the note replaces with the guess "most likely
     logarithmic".
  3. The same sweep at every rung, not just the top one, so that a reading
     driven by one noisy pair of values is visible as one.

Nothing here is a new compute job: the input is the sixteen banked mu_H.

RED controls (all must fire, or the script exits non-zero):
  - feeding a lambda for which the ladder is EXACTLY 1/H^2 must recover
    exponent 1 and lambda_star == that lambda;
  - a ladder built with a genuine log term must NOT report exponent 1;
  - the solver must refuse a lambda below max(mu_H), where ln lambda - ln mu_H
    changes sign and the surface term is meaningless.

Usage: python3 experiments/strip_fss_lambda_sensitivity.py
"""
import math
import sys

# The banked ladder, at the precision it is banked to -- identical to
# experiments/strip_fss.py's MU, which cites
# results/strip-mu-engine-resumption.md (H<=14) and
# results/strip-mu-certificates.md's addendum table (H=15..17).
MU = {
    2: 2.4142136, 3: 3.4437184, 4: 4.1823214, 5: 4.7178013, 6: 5.1153245,
    7: 5.4178476, 8: 5.6533728, 9: 5.8404579, 10: 5.9916958, 11: 6.1158416,
    12: 6.2191246, 13: 6.3060713, 14: 6.3800344, 15: 6.4435408,
    16: 6.4985245, 17: 6.5464870,
}
LAST_DIGIT_UNIT = 1e-7

# The two banked lambda estimates, and the quoted uncertainty on the first.
LAMBDA_DA = 7.1102        # differential approximants, results/series-analysis-da.md
LAMBDA_DA_SIGMA = 0.0001  # the "(1)" in 7.1102(1)
LAMBDA_RATIO = 7.111      # the a(n)-ratio fit


def surface(mu, lam):
    """S(H) = H (ln lam - ln mu_H), over the heights present in mu."""
    return {H: H * (math.log(lam) - math.log(m)) for H, m in mu.items()}


def increments(S):
    """dS(H) = S(H) - S(H-1), for every H whose predecessor is present."""
    return {H: S[H] - S[H - 1] for H in sorted(S) if H - 1 in S}


def ratio_at(mu, lam, H):
    """dS(H)/dS(H-1) -- the increment-shrink diagnostic at rung H."""
    d = increments(surface(mu, lam))
    if H not in d or H - 1 not in d:
        raise KeyError(f"rung {H} needs increments at H and H-1")
    if d[H - 1] == 0.0:
        raise ZeroDivisionError("increment vanishes; diagnostic undefined")
    return d[H] / d[H - 1]


def clean_square_ratio(H):
    """The increment ratio a pure 1/H^2 correction to ln mu_H predicts.

    ln mu_H = ln lam - a/H - b/H^2  =>  S(H) = a + b/H, so
    dS(H) = -b/(H(H-1)) and dS(H)/dS(H-1) = (H-2)/H.
    """
    return (H - 2) / H


def _ratio_of_exponent(q, H):
    """The rung-H increment ratio a pure S(H) = S_inf + c*H^-q would give.

    Solved EXACTLY at finite H, not asymptotically:
        dS(H)   = c(H^-q - (H-1)^-q)
        ratio   = (H^-q - (H-1)^-q) / ((H-1)^-q - (H-2)^-q)
    The asymptotic shortcut ((H-1)/H)^(q+1) is wrong by enough to matter here:
    it reads q = 1.065 off a ladder that is exactly 1/H^2, which is what the
    first RED control caught.  q -> 0 is the logarithmic limit, taken as a
    limit because H^0 - (H-1)^0 = 0 identically.
    """
    if abs(q) < 1e-12:
        num = math.log(H) - math.log(H - 1)
        den = math.log(H - 1) - math.log(H - 2)
        return num / den
    num = H ** (-q) - (H - 1) ** (-q)
    den = (H - 1) ** (-q) - (H - 2) ** (-q)
    return num / den


def effective_exponent(mu, lam, H, lo=-0.9, hi=8.0):
    """q in S(H) = S_inf + c*H^-q, from the increment ratio at rung H.

    q = 0 is a logarithmic correction; q = 1 is the clean 1/H^2 case.  The
    map q -> ratio is monotone, so this is a bisection with an asserted
    bracket rather than a closed form.
    """
    r = ratio_at(mu, lam, H)
    if r <= 0:
        return float('nan')

    def f(q):
        return _ratio_of_exponent(q, H) - r

    flo, fhi = f(lo), f(hi)
    if flo * fhi > 0:
        return float('nan')
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        fm = f(mid)
        if abs(hi - lo) < 1e-13:
            return mid
        if flo * fm <= 0:
            hi, fhi = mid, fm
        else:
            lo, flo = mid, fm
    return 0.5 * (lo + hi)


def sign_change_lambda(mu, H):
    """The lambda at which dS(H) changes sign -- the surface term stops falling.

    dS(H) = 0 means S(H) = S(H-1), i.e.
    H(ln lam - ln mu_H) = (H-1)(ln lam - ln mu_{H-1}), which solves exactly:
        ln lam = H ln mu_H - (H-1) ln mu_{H-1}.
    Above this lambda the diagnostic is meaningless (the term is rising, not
    falling), and the ratio is NOT monotone across it -- which is why this
    function exists rather than a wider bisection bracket.
    """
    return math.exp(H * math.log(mu[H]) - (H - 1) * math.log(mu[H - 1]))


def lambda_for_ratio(mu, H, target, lo=None, hi=None, tol=1e-14):
    """Solve for the lambda whose rung-H increment ratio equals `target`.

    An error d in ln lambda shifts every increment by exactly +d.  With both
    increments negative the ratio (dS(H)+d)/(dS(H-1)+d) falls monotonically as
    d rises, so the solve is a bisection on the branch BELOW the rung's sign
    change -- above it the ratio jumps through a pole and comes back down
    toward 1, and a naive wide bracket lands on the wrong side.
    """
    lo_default = max(mu.values()) + 1e-9
    # dS(H) hits zero first at rung H's own sign change; dS(H-1) at rung H-1's.
    # Stay strictly below the earlier of the two.
    hi_default = min(sign_change_lambda(mu, H),
                     sign_change_lambda(mu, H - 1)) - 1e-9
    lo = lo_default if lo is None else lo
    hi = hi_default if hi is None else hi
    if lo <= max(mu.values()):
        raise ValueError(f"lambda must exceed max mu_H = {max(mu.values())}")
    if hi <= lo:
        raise ValueError(f"rung {H}: no falling branch on [{lo}, {hi}]")

    def f(lam):
        return ratio_at(mu, lam, H) - target

    flo, fhi = f(lo), f(hi)
    if flo * fhi > 0:
        raise ValueError(
            f"target ratio {target:.6f} not bracketed on [{lo:.6f}, {hi:.6f}]: "
            f"f(lo)={flo:+.6e}, f(hi)={fhi:+.6e}")
    for _ in range(300):
        mid = 0.5 * (lo + hi)
        fm = f(mid)
        if abs(hi - lo) < tol:
            return mid
        if flo * fm <= 0:
            hi, fhi = mid, fm
        else:
            lo, flo = mid, fm
    return 0.5 * (lo + hi)


def extrapolate_power(seq):
    """Sum the tail of a monotone sequence whose increments decay as a power.

    seq is {H: value}.  Fit the decay exponent p from the last two increments
    (d(H) ~ k*H^-p), then add the integral of the tail from the top rung to
    infinity.  Returns (limit, p).  Deliberately crude: two points set the
    exponent, which is a weak extrapolation and is reported as one.
    """
    Hs = sorted(seq)
    d = {H: seq[H] - seq[H - 1] for H in Hs if H - 1 in seq}
    ds = sorted(d)
    h1, h0 = ds[-1], ds[-2]
    if d[h0] == 0:
        return seq[Hs[-1]], float('nan')
    # |d(H)| ~ k H^-p, so |d(h1)|/|d(h0)| = (h1/h0)^-p and p carries a minus.
    p = -math.log(abs(d[h1] / d[h0])) / math.log(h1 / h0)
    # d(H) = k H^-p with k from the top increment; tail = sum_{H>h1} d(H)
    # approximated by the integral, which for p > 1 is k*h1^(1-p)/(p-1).
    if p <= 1.0:
        return float('nan'), p
    k = abs(d[h1]) * h1 ** p
    tail = k * h1 ** (1 - p) / (p - 1)
    return seq[h1] - tail, p


def _solve_normal(rows, rhs, n):
    """Least squares by normal equations + Gaussian elimination."""
    ata = [[sum(rows[i][r] * rows[i][c] for i in range(len(rows)))
            for c in range(n)] for r in range(n)]
    atb = [sum(rows[i][r] * rhs[i] for i in range(len(rows))) for r in range(n)]
    for i in range(n):
        piv = max(range(i, n), key=lambda r: abs(ata[r][i]))
        ata[i], ata[piv] = ata[piv], ata[i]
        atb[i], atb[piv] = atb[piv], atb[i]
        for r in range(i + 1, n):
            f = ata[r][i] / ata[i][i]
            for c in range(i, n):
                ata[r][c] -= f * ata[i][c]
            atb[r] -= f * atb[i]
    x = [0.0] * n
    for i in reversed(range(n)):
        x[i] = (atb[i] - sum(ata[i][c] * x[c]
                             for c in range(i + 1, n))) / ata[i][i]
    return x


def fit_poly_in_inv_H(mu, lam, nterms):
    """Fit ln mu_H = ln lam - sum_{j=1..nterms} c_j / H^j; return coeffs, resid."""
    Hs = sorted(mu)
    rows = [[1.0 / H ** (j + 1) for j in range(nterms)] for H in Hs]
    rhs = [math.log(lam) - math.log(mu[H]) for H in Hs]
    x = _solve_normal(rows, rhs, nterms)
    resid = {H: rhs[i] - sum(rows[i][j] * x[j] for j in range(nterms))
             for i, H in enumerate(Hs)}
    return x, resid


def fit_with_lambda_free(mu, nterms):
    """Same expansion, but lambda is fitted rather than fed in.

    Solves ln mu_H = L - sum_{j} c_j/H^j for L and the c_j together, so the
    returned lambda = exp(L) is what the ladder says about lambda when it is
    not told.  Slow convergence of the correction series biases this UPWARD,
    which is the whole point of reporting it next to the fixed-lambda fit.
    """
    Hs = sorted(mu)
    rows = [[1.0] + [-1.0 / H ** (j + 1) for j in range(nterms)] for H in Hs]
    rhs = [math.log(mu[H]) for H in Hs]
    x = _solve_normal(rows, rhs, nterms + 1)
    resid = {H: rhs[i] - sum(rows[i][j] * x[j] for j in range(nterms + 1))
             for i, H in enumerate(Hs)}
    return math.exp(x[0]), x[1:], resid


def fit_three_term(mu, lam):
    """Least-squares a, b, c in ln mu_H = ln lam - a/H - b/H^2 - c/H^3.

    Plain normal equations on the heights available; three unknowns against
    sixteen rungs, so this is a fit and its residuals mean something.
    """
    Hs = sorted(mu)
    rows = [[1.0 / H, 1.0 / H ** 2, 1.0 / H ** 3] for H in Hs]
    rhs = [math.log(lam) - math.log(mu[H]) for H in Hs]
    # normal equations A^T A x = A^T b, solved by Gaussian elimination
    n = 3
    ata = [[sum(rows[i][r] * rows[i][c] for i in range(len(Hs)))
            for c in range(n)] for r in range(n)]
    atb = [sum(rows[i][r] * rhs[i] for i in range(len(Hs))) for r in range(n)]
    for i in range(n):
        piv = max(range(i, n), key=lambda r: abs(ata[r][i]))
        ata[i], ata[piv] = ata[piv], ata[i]
        atb[i], atb[piv] = atb[piv], atb[i]
        for r in range(i + 1, n):
            f = ata[r][i] / ata[i][i]
            for c in range(i, n):
                ata[r][c] -= f * ata[i][c]
            atb[r] -= f * atb[i]
    x = [0.0] * n
    for i in reversed(range(n)):
        x[i] = (atb[i] - sum(ata[i][c] * x[c] for c in range(i + 1, n))) / ata[i][i]
    return x[0], x[1], x[2]


def synth_power(lam, a, b, heights):
    """A ladder that is EXACTLY ln lam - a/H - b/H^2."""
    return {H: math.exp(math.log(lam) - a / H - b / H ** 2) for H in heights}


def synth_log(lam, a, c, heights):
    """A ladder with a genuine log term: ln lam - a/H - c*ln(H)/H^2."""
    return {H: math.exp(math.log(lam) - a / H - c * math.log(H) / H ** 2)
            for H in heights}


def red_controls():
    """Fail closed: every control must fire."""
    heights = sorted(MU)
    ok = True

    # 1. An exactly-1/H^2 ladder must read exponent 1 and recover its own lam.
    lam0, a0, b0 = 7.0, 1.0, 2.0
    mu0 = synth_power(lam0, a0, b0, heights)
    q0 = effective_exponent(mu0, lam0, 17)
    lam_star0 = lambda_for_ratio(mu0, 17, clean_square_ratio(17))
    good = abs(q0 - 1.0) < 1e-6 and abs(lam_star0 - lam0) < 1e-6
    print(f"RED  an exact 1/H^2 ladder reads q=1 and recovers its own lambda "
          f"(q={q0:.9f}, lambda*={lam_star0:.9f})  "
          f"{'OK' if good else 'FAILED'}")
    ok &= good

    # 2. A ladder with a real log term must NOT read exponent 1.
    mu1 = synth_log(7.0, 1.0, 3.0, heights)
    q1 = effective_exponent(mu1, 7.0, 17)
    good = abs(q1 - 1.0) > 0.05
    print(f"RED  a ladder with a genuine log term does not read q=1 "
          f"(q={q1:.6f})  {'OK' if good else 'FAILED'}")
    ok &= good

    # 3. A lambda at or below max(mu_H) must be refused, not silently used.
    try:
        lambda_for_ratio(MU, 17, 0.88, lo=max(MU.values()))
        print("RED  lambda <= max(mu_H) is refused  FAILED (no raise)")
        ok = False
    except ValueError:
        print("RED  lambda <= max(mu_H) is refused  OK")

    return ok


def main():
    heights = sorted(MU)
    top = heights[-1]

    print("=" * 72)
    print("Strip ladder: how much of the non-analyticity is lambda's error bar?")
    print("=" * 72)
    print(f"banked mu_H for H = {heights[0]}..{top}, "
          f"mu_{top} = {MU[top]:.7f}")
    print()

    print("--- 1. The banked diagnostic, reproduced ---")
    for lam, name in ((LAMBDA_DA, "differential approximants"),
                      (LAMBDA_RATIO, "a(n)-ratio fit")):
        d = increments(surface(MU, lam))
        r = ratio_at(MU, lam, top)
        print(f"lambda = {lam}  ({name})")
        print(f"  dS({top})        = {d[top]:+.6f}   "
              f"(the note's 'still falling by ...')")
        print(f"  dS({top})/dS({top-1}) = {r:.6f}   "
              f"-> {100*(1-r):.2f}% shrink per rung")
        print(f"  clean 1/H^2 predicts {clean_square_ratio(top):.6f}   "
              f"-> {100*(1-clean_square_ratio(top)):.2f}% shrink")
        print(f"  effective exponent q = {effective_exponent(MU, lam, top):+.4f}"
              f"   (q=1 clean 1/H^2, q=0 logarithmic)")
        print()

    print("--- 2. The lambda that would make it look clean ---")
    lam_star = lambda_for_ratio(MU, top, clean_square_ratio(top))
    delta = lam_star - LAMBDA_DA
    sigmas = delta / LAMBDA_DA_SIGMA
    print(f"lambda* = {lam_star:.6f}  -- the value at which rung {top}'s")
    print(f"          increment ratio equals the clean 1/H^2 prediction")
    print(f"offset from the independent estimate {LAMBDA_DA}(1): "
          f"{delta:+.6f} = {sigmas:+.0f} sigma")
    print()

    print("--- 3. Every rung, not just the top ---")
    print(f"{'H':>3}  {'lambda*':>10}  {'offset':>9}  "
          f"{'q(7.1102)':>10}  {'q(lambda*)':>10}")
    for H in heights:
        if H - 2 < heights[0]:
            continue
        try:
            ls = lambda_for_ratio(MU, H, clean_square_ratio(H))
            q = effective_exponent(MU, LAMBDA_DA, H)
            print(f"{H:>3}  {ls:>10.6f}  {ls-LAMBDA_DA:>+9.5f}  "
                  f"{q:>10.4f}  {1.0:>10.4f}")
        except ValueError as e:
            print(f"{H:>3}  {'unbracketed':>10}  "
                  f"({str(e).split(':')[0]})")
    print()

    print("--- 4. Input-precision floor ---")
    # The ladder is banked to 7 decimals; perturb the two mu that the top
    # rung's ratio depends on and see how far lambda* moves.
    spread = []
    for s15 in (-1, 0, 1):
        for s16 in (-1, 0, 1):
            for s17 in (-1, 0, 1):
                mu = dict(MU)
                mu[15] += s15 * LAST_DIGIT_UNIT
                mu[16] += s16 * LAST_DIGIT_UNIT
                mu[17] += s17 * LAST_DIGIT_UNIT
                spread.append(lambda_for_ratio(mu, top,
                                               clean_square_ratio(top)))
    print(f"lambda* over all 27 last-digit perturbations of mu_15..mu_17: "
          f"[{min(spread):.6f}, {max(spread):.6f}]")
    print(f"  spread {max(spread)-min(spread):.2e}, against an offset of "
          f"{abs(delta):.4f} -- ratio {abs(delta)/(max(spread)-min(spread)):.0f}x")
    print()

    print("--- 5. Does lambda*(H) converge, and to what? ---")
    # lambda*(H) -> lambda as H -> infinity for ANY expansion whose leading
    # correction is a/H, because the higher-order terms that spoil the
    # rung-H ratio all vanish.  So the drift itself is not evidence of
    # anything; where it LANDS is.
    seq = {}
    for H in heights:
        if H - 2 < heights[0]:
            continue
        try:
            seq[H] = lambda_for_ratio(MU, H, clean_square_ratio(H))
        except ValueError:
            pass
    lam_inf, p = extrapolate_power(seq)
    print(f"lambda*(H) decrements decay like H^-{p:.3f}; "
          f"summing the tail gives")
    print(f"  lambda*(inf) = {lam_inf:.4f}   against the independent "
          f"{LAMBDA_DA}(1)")
    print(f"  offset {lam_inf - LAMBDA_DA:+.4f}")
    print()

    print("--- 5b. The direct test: can an analytic form FIT the ladder? ---")
    # The lambda* machinery is indirect.  The direct question is whether
    # ln mu_H = ln lambda - a/H - b/H^2 - c/H^3 can reproduce the sixteen
    # banked values at all.  The ladder is banked to 1e-7; a fit whose
    # residuals sit at that level leaves nothing for a log term to explain,
    # and a fit whose residuals are orders above it is the real evidence.
    # Low rungs have no business in an asymptotic fit, so window it.
    print(f"  {'window':>8} {'terms':>6} {'rms resid':>11} {'worst':>11}"
          f"   {'lambda if free':>14}")
    for lo in (2, 8, 10, 12):
        mu_w = {H: v for H, v in MU.items() if H >= lo}
        for nterms in (2, 3, 4):
            if len(mu_w) <= nterms + 1:
                continue
            _, resid = fit_poly_in_inv_H(mu_w, LAMBDA_DA, nterms)
            worst = max(abs(r) for r in resid.values())
            rms = math.sqrt(sum(r * r for r in resid.values()) / len(resid))
            lam_free, _, _ = fit_with_lambda_free(mu_w, nterms)
            print(f"  {f'H>={lo}':>8} {nterms:>6} {rms:>11.3e} {worst:>11.3e}"
                  f"   {lam_free:>14.4f}")
    print(f"  banking precision of the ladder: {LAST_DIGIT_UNIT:.0e} in mu, "
          f"~{LAST_DIGIT_UNIT/MU[top]:.1e} in ln mu -- a truncation floor, "
          f"not a noise bar")
    print()

    print("--- 6. The control that decides it: synthetic ladders ---")
    # Feed the same diagnostic a ladder that is ANALYTIC in 1/H by
    # construction, with coefficients tuned to match the real mu_H, and a
    # ladder with a genuine log term.  If the analytic one reproduces the
    # observed lambda*(H) drift, the drift is not evidence of a log term.
    a_fit, b_fit, c_fit = fit_three_term(MU, LAMBDA_DA)
    print(f"analytic fit to the banked ladder at lambda={LAMBDA_DA}: "
          f"a={a_fit:.4f}, b={b_fit:.4f}, c={c_fit:.4f}")
    for label, mu_s in (
            ("analytic  a/H + b/H^2 + c/H^3",
             {H: math.exp(math.log(LAMBDA_DA) - a_fit / H - b_fit / H ** 2
                          - c_fit / H ** 3) for H in heights}),
            ("log term  a/H + c*ln(H)/H^2",
             synth_log(LAMBDA_DA, a_fit, 3.9, heights))):
        s = {}
        for H in heights:
            if H - 2 < heights[0]:
                continue
            try:
                s[H] = lambda_for_ratio(mu_s, H, clean_square_ratio(H))
            except ValueError:
                pass
        li, pp = extrapolate_power(s)
        print(f"  {label:32s} lambda*(17)={s[top]:.4f}  "
              f"decay H^-{pp:.2f}  lambda*(inf)={li:.4f}")
    print(f"  {'BANKED mu_H':32s} lambda*(17)={seq[top]:.4f}  "
          f"decay H^-{p:.2f}  lambda*(inf)={lam_inf:.4f}")
    print()

    print("--- RED controls ---")
    if not red_controls():
        print("\nSELFTEST: FAILED")
        return 1
    print("\nSELFTEST: ALL OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
