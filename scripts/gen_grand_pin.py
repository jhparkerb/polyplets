#!/usr/bin/env python3
"""Generate Polyplets/Grand/PinGrand.lean: the grand-form pinning of the
production polynomials P_1..P_18 from TWO real banked cells per level.

Task GF-5 of the grand-form Lean formalization (polyplets/GRANDFORM-PLAN.md (deleted),
polyplets/briefs/GF5-pingrand.md, deleted at close; in git history).
Fail-closed: recomputes the mu table
level-by-level from results/triangle.txt exactly as experiments/staircase_check.py
does, re-runs that oracle's checks (209-instance staircase, P-staircase identity,
anchor parity, weight-side mu parity for k<=3), and enforces H <= 20 for every
hypothesized anchor (every anchor real-swept: columns H <= 21 are real in
the a(40) run).  ANY failure aborts with no output.

Architecture (per level k):
  * Pstair{k}  -- the P-staircase ring identity with INTEGER coefficients
                 pc_i = mu_i * 3^(2i-1) (all integer); pure `ring`.
  * mu{k}_val  -- mu_k solved from the staircase at H=k+1 (the second real
                 cell B_k pins it); the other RHS cells come from the lower
                 grand forms and T_diag_pow.  (k >= 4 only.)
  * P{k}_grand_of_banked -- 3^(3k+1) T(H+k,H) = P_k(H+k) 3^(H+k) for all
                 H >= k+1, by induction on H; base = A_k, step = staircase +
                 lower grand forms, closed by full polynomial expansion.
  * P{k}_grand_prod -- the production n-form with the zpow exponent.

Levels 1..3 are discharged from the existing closed forms (Pin.P1_pinned,
P2_pinned, Weights3Heavy.P3_pinned); only k = 4..16 carry banked hypotheses,
so P16_grand_of_banked carries EXACTLY the 26 anchors A_j,B_j for j = 4..16.

Pp0..Pp16, horner, prodPoly, prodPoly_eval are REUSED from Pin.lean (they are
already defined there); nothing is re-emitted.

Run: python3 scripts/gen_grand_pin.py [--out PATH] [--kmax K]
"""
import argparse
import os
import re
import sys
from fractions import Fraction as F

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KMAX = 18
HMAX_ANCHOR = 20

# Lean-verified aggregated interior weights (Weights.lean/Weights3(Heavy).lean).
V = {(1, 1): 25, (1, 2): 49, (2, 2): 339, (1, 3): 81, (2, 3): 1860, (3, 3): 4778}


def die(msg):
    sys.exit(f"gen_grand_pin: ABORT: {msg}")


# ---------------------------------------------------------------- inputs
def read_triangle():
    """results/triangle.txt -> {(n,H): T}."""
    path = os.path.join(ROOT, "results", "triangle.txt")
    if not os.path.exists(path):
        die(f"missing {path}")
    d = {}
    for line in open(path):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        p = line.split()
        if len(p) != 3:
            die(f"bad triangle line: {line!r}")
        n, H, t = int(p[0]), int(p[1]), int(p[2])
        d[(n, H)] = t
    return d


def read_sweep():
    """orchestrator/sweep.go diagCoeffTable -> {k: (coeffs_desc, kfact)}."""
    src = open(os.path.join(ROOT, "orchestrator", "sweep.go")).read()
    tbl = {0: ([1], 1)}
    for mm in re.finditer(r'\n\t(\d+): \{\[\]string\{([^}]*)\}, (\d+)\}', src):
        k = int(mm.group(1))
        tbl[k] = ([int(x) for x in re.findall(r'"(-?\d+)"', mm.group(2))],
                  int(mm.group(3)))
    return tbl


def read_pindata():
    """polyplets/pin-data.md -> {k: (coeffs_desc, kfact)} (secondary source)."""
    path = os.path.join(ROOT, "polyplets", "pin-data.md")
    blocks = {}
    cur = None
    for line in open(path):
        m = re.match(r'## k=(\d+)', line)
        if m:
            cur = int(m.group(1))
            blocks[cur] = {'num': None, 'kf': None}
            continue
        if cur is None:
            continue
        m = re.match(r'numerator \(desc n\): \[(.*)\]', line)
        if m:
            blocks[cur]['num'] = [int(x.strip()) for x in m.group(1).split(',')]
            continue
        m = re.match(r'kfact: (\d+)', line)
        if m:
            blocks[cur]['kf'] = int(m.group(1))
    out = {}
    for k, b in blocks.items():
        if b['num'] is not None:
            out[k] = (b['num'], b['kf'])
    return out


# ---------------------------------------------------------------- core numerics
def build(real, tbl):
    def T(n, H):
        if n == H:
            return 3 ** (n - 1)
        if (n, H) not in real:
            die(f"cell T({n},{H}) not banked")
        return real[(n, H)]

    def P(k, n):
        c, kf = tbl[k]
        num = 0
        for co in c:
            num = num * n + co
        return F(num, kf)

    # solve mu level by level from the pinning cells (== staircase_check.py)
    mu = {0: F(3)}
    for k in range(1, KMAX + 1):
        rhs_known = sum(mu[i] * T(2 * k + 1 - i, k + 1) for i in range(k))
        mu[k] = (F(T(2 * k + 2, k + 2)) - rhs_known) / T(k + 1, k + 1)
    return T, P, mu


def check_all(T, P, mu):
    """Re-run the numeric oracle in full; abort on any mismatch."""
    # 1. overdetermination: staircase at all 209 real in-range instances
    #    (k <= 18, H <= 20; was 170 at the k <= 16 / n <= 36 tier).
    total, bad = 0, []
    for k in range(0, KMAX + 1):
        for H in range(k + 1, 21):
            if H + 1 + k > 40:
                continue
            lhs = F(T(H + 1 + k, H + 1))
            rhs = sum(mu[i] * T(H + k - i, H) for i in range(k + 1))
            total += 1
            if lhs != rhs:
                bad.append((k, H))
    if bad:
        die(f"staircase FAILS at {bad[:5]} ({len(bad)} total)")
    if total != 209:
        die(f"expected 209 staircase instances, got {total}")

    # 2. weight-side fixed point for mu_1..mu_3.
    nu = {0: F(1, 3)}

    def conv(a, b, m):
        return sum(a.get(i, F(0)) * b.get(m - i, F(0)) for i in range(m + 1))

    def conv_pow(a, e, m):
        r = {0: F(1)}
        for _ in range(e):
            r = {i: conv(r, a, i) for i in range(m + 1)}
        return r

    mu_w = {0: F(3)}
    for m in range(1, 4):
        acc = F(0)
        for l in range(1, m + 1):
            vl = {j: F(V[(l, j)]) for j in (1, 2, 3) if (l, j) in V and l <= j}
            acc += conv(vl, conv_pow(nu, l, m), m)
        mu_w[m] = acc
        nu[m] = -sum(mu_w.get(i, F(0)) * nu[m - i] for i in range(1, m + 1)) / 3
    if any(mu_w[m] != mu[m] for m in (1, 2, 3)):
        die("weight-side mu_1..3 != data-side mu_1..3")

    # 3. P-staircase identity for production P_k at k+2 points.
    for k in range(1, KMAX + 1):
        for n in range(0, k + 2):
            lhs = P(k, n + 1)
            rhs = sum(mu[i] * F(3) ** (2 * i - 1) * P(k - i, n - i)
                      for i in range(k + 1))
            if lhs != rhs:
                die(f"P-staircase FAILS at k={k}, n={n}")

    # 4. anchors match production values.
    for k in range(1, KMAX + 1):
        for n in (2 * k + 1, 2 * k + 2):
            e = n - 1 - 3 * k
            want = P(k, n) * (F(3) ** e if e >= 0 else F(1, 3 ** -e))
            if want != T(n, n - k):
                die(f"anchor T({n},{n - k}) != production P_{k}")


def mu_lit(mu_k):
    """mu_k = num / 3^e ; assert denominator is a power of 3."""
    d = mu_k.denominator
    dd, e = d, 0
    while dd % 3 == 0:
        dd //= 3
        e += 1
    if dd != 1:
        die(f"mu denominator {d} is not a power of 3")
    return mu_k.numerator, e


# ---------------------------------------------------------------- Lean emission
def anchor_hyps(k):
    """Hypothesis-binder string for levels 4..k."""
    out = []
    for j in range(4, k + 1):
        out.append(f"    (hA{j} : T {2 * j + 1} {j + 1} = {ANCH_A[j]})")
        out.append(f"    (hB{j} : T {2 * j + 2} {j + 2} = {ANCH_B[j]})")
    return "\n".join(out)


def anchor_args(k):
    """Applied-argument string `hA4 hB4 ... hAk hBk` for levels 4..k."""
    return " ".join(f"hA{j} hB{j}" for j in range(4, k + 1))


def grand_ref(j):
    """A Lean term proving the level-j grand form at a still-to-apply height."""
    if j <= 3:
        return f"P{j}_grand"
    return f"P{j}_grand_of_banked {anchor_args(j)}".rstrip()


def mu_ref(i):
    """A Lean simp lemma for `mu i = <lit>`."""
    if i == 0:
        return "mu_zero"
    if i == 1:
        return "mu_one"
    if i == 2:
        return "mu_two"
    if i == 3:
        return "mu_three_of V_3_3"
    return f"mu{i}_val {anchor_args(i)}".rstrip()


def emit_header(inputs_line):
    return f'''/-
Copyright (c) 2026 Jason H Parker. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Jason H Parker
-/
import Polyplets.Grand.Staircase
import Polyplets.Pin
import Polyplets.Weights3Heavy

/-!
# PinGrand: production polynomials `P_1..P_16` pinned from two real cells/level

The payoff of the grand-form staircase (`GRANDFORM-PLAN.md`, `briefs/GF5`):
the production polynomials of `orchestrator/sweep.go` (`Pin.Pp1..Pp16`) are
certified for **all** `n ≥ 2k+1` from only the two real-swept onset cells
`A_k = T(2k+1, k+1)` and `B_k = T(2k+2, k+2)` per level (`H ≤ 20` throughout,
every anchor a real-swept cell).

* `Pstair<k>` — the P-staircase ring identity
  `P_k(x+1) = Σ_i (μ_i·3^{{2i-1}})·P_{{k-i}}(x-i)` with **integer** coefficients.
* `mu<k>_val` — `μ_k` solved from `T_staircase k (k+1)`: the second real cell
  `B_k` pins it (`k ≥ 4`; `μ_1..μ_3` come from `Mu.lean`).
* `P<k>_grand_of_banked` — `3^{{3k+1}}·T(H+k,H) = P_k(H+k)·3^{{H+k}}`
  (`∀ H ≥ k+1`), by induction on `H` through `T_staircase`.
* `P<k>_grand_prod` — the production `n`-form `T(n,n-k) = P_k(n)·3^{{n-1-3k}}`.

Levels 1..3 are discharged from the existing closed forms
(`Pin.P1_pinned`/`P2_pinned`, `Weights3Heavy.P3_pinned`), so
`P16_grand_of_banked` carries EXACTLY the 26 anchors for levels 4..16.
`Pp0..Pp16`, `horner`, `prodPoly`, `prodPoly_eval` are reused from `Pin.lean`.

Machine-generated by `scripts/gen_grand_pin.py` from
{inputs_line}
Do not edit by hand; regenerate instead.
-/

namespace Polyplets

open Polynomial

section GrandPin
set_option linter.style.longLine false

/-- **Generic H→n coordinate change** (2026-07-31 dedup): from the staircase
banked form `3^(3k+1)·T(H+k,H) = P(H+k)·3^(H+k)` (`∀ H ≥ k+1`) to the
production `n`-form. One lemma replaces the fifteen per-level copies of
this proof that `P<k>_grand_prod` used to carry. -/
lemma grand_to_prod {{k : ℕ}} {{P : Polynomial ℚ}}
    (h : ∀ H : ℕ, k + 1 ≤ H →
      (3 : ℚ) ^ (3 * k + 1) * (T (H + k) H : ℚ) = P.eval ((H : ℚ) + k) * 3 ^ (H + k)) :
    ∀ n : ℕ, 2 * k + 1 ≤ n →
      (T n (n - k) : ℚ) = P.eval (n : ℚ) * (3 : ℚ) ^ ((n : ℤ) - 1 - 3 * k) := by
  intro n hn
  have hg := h (n - k) (by omega)
  rw [show n - k + k = n from by omega,
    show ((n - k : ℕ) : ℚ) + k = (n : ℚ) from by rw [Nat.cast_sub (by omega)]; ring] at hg
  rw [show ((n : ℤ) - 1 - 3 * k) = (n : ℤ) - (3 * k + 1 : ℕ) from by push_cast; ring,
    zpow_sub₀ (by norm_num : (3 : ℚ) ≠ 0), zpow_natCast, zpow_natCast]
  field_simp
  linear_combination hg
'''


def emit_P123_grand(k):
    return f'''
/-- **k={k} grand form** (from the existing closed form `P{k}_pinned`):
`3^(3·{k}+1)·T(H+{k},H) = P_{k}(H+{k})·3^(H+{k})` for all `H ≥ {k}+1`. -/
theorem P{k}_grand : ∀ H : ℕ, {k} + 1 ≤ H →
    (3 : ℚ) ^ (3 * {k} + 1) * (T (H + {k}) H : ℚ) = Pp{k}.eval ((H : ℚ) + {k}) * 3 ^ (H + {k}) := by
  intro H hH
  have hn := P{k}_pinned (H + {k}) (by omega)
  rw [show H + {k} - {k} = H from by omega] at hn
  push_cast at hn
  rw [hn, ← mul_assoc, mul_comm ((3 : ℚ) ^ (3 * {k} + 1)) _, mul_assoc]
  congr 1
  rw [← zpow_natCast (3 : ℚ) (3 * {k} + 1), ← zpow_natCast (3 : ℚ) (H + {k}),
    ← zpow_add₀ (by norm_num : (3 : ℚ) ≠ 0)]
  congr 1
  push_cast; ring
'''


def emit_pstair(k, pc):
    terms = " + ".join(f"{pc[i]} * Pp{k - i}.eval (x - {i})" for i in range(k + 1))
    pps = ", ".join(f"Pp{j}" for j in range(k, -1, -1))
    return f'''
/-- **P-staircase at k={k}**: `P_{k}(x+1) = Σ_{{i=0}}^{{{k}}} (μ_i·3^(2i-1))·P_{{{k}-i}}(x-i)`
with integer coefficients `μ_i·3^(2i-1)`. A pure polynomial identity. -/
lemma Pstair{k} (x : ℚ) :
    Pp{k}.eval (x + 1) = {terms} := by
  simp only [{pps}, prodPoly_eval]
  norm_num
  ring
'''


def hb_option(k):
    """Levels k >= 17 exceed the default 200000-heartbeat budget (the mu-sum
    simp and the closing ring expansion grow with k); scale the limit."""
    return "set_option maxHeartbeats 1600000 in\n" if k >= 17 else ""

def emit_mu_val(k, T, num, e):
    lines = []
    lines.append(hb_option(k) + f'''
/-- **μ_{k} solved from the staircase** at `H={k}+1`: the second real cell
`B_{k} = T({2 * k + 2},{k + 2})` pins `μ_{k}`. -/
lemma mu{k}_val
{anchor_hyps(k)} :
    mu {k} = {num} / 3 ^ {e} := by
  have hst := T_staircase {k} {k + 1} (by norm_num)
  have cA : (T {2 * k + 1} {k + 1} : ℚ) = {ANCH_A[k]} := by exact_mod_cast hA{k}
  have cB : (T {2 * k + 2} {k + 2} : ℚ) = {ANCH_B[k]} := by exact_mod_cast hB{k}''')
    cells = []
    for i in range(1, k):
        j = k - i
        n = 2 * k + 1 - i
        val = T(n, k + 1)
        cells.append(f"c{i}")
        lines.append(
            f'''  have c{i} : (T {n} {k + 1} : ℚ) = {val} := by
    have h := {grand_ref(j)} {k + 1} (by norm_num)
    norm_num [Pp{j}, prodPoly_eval] at h; linarith [h]''')
    lines.append(
        f'''  have cD : (T {k + 1} {k + 1} : ℚ) = {3 ** k} := by
    rw [T_diag_pow {k + 1} (by norm_num)]; norm_num''')
    mus = ", ".join(mu_ref(i) for i in range(0, k))
    clist = ", ".join(["cA", "cB"] + cells + ["cD"])
    lines.append(
        f'''  simp only [Finset.sum_range_succ, Finset.sum_range_zero, zero_add,
    {mus}, {clist}] at hst
  linarith [hst]''')
    return "\n".join(lines) + "\n"


def emit_grand_of_banked(k):
    lines = []
    lines.append(hb_option(k) + f'''
/-- **k={k} grand form from two real cells per level** (levels 4..{k}).
`3^(3·{k}+1)·T(H+{k},H) = P_{k}(H+{k})·3^(H+{k})` for all `H ≥ {k}+1`,
by induction on `H` through `T_staircase`.  Hypotheses: the anchors
`A_j = T(2j+1,j+1)`, `B_j = T(2j+2,j+2)` for `j = 4..{k}` (all `H ≤ 20`, real-swept). -/
theorem P{k}_grand_of_banked
{anchor_hyps(k)} :
    ∀ H : ℕ, {k} + 1 ≤ H →
      (3 : ℚ) ^ (3 * {k} + 1) * (T (H + {k}) H : ℚ) = Pp{k}.eval ((H : ℚ) + {k}) * 3 ^ (H + {k}) := by
  intro H hH
  induction H, hH using Nat.le_induction with
  | base =>
    have cA : (T {2 * k + 1} {k + 1} : ℚ) = {ANCH_A[k]} := by exact_mod_cast hA{k}
    norm_num [Pp{k}, prodPoly_eval, cA]
  | succ H hH ih =>
    have hst := T_staircase {k} H hH''')
    for d in range(k, 0, -1):
        ref = "ih" if d == k else f"{grand_ref(d)} H (by omega)"
        lines.append(
            f'''    have e{d} : (T (H + {d}) H : ℚ)
        = Pp{d}.eval ((H : ℚ) + {d}) * 3 ^ (H + {d}) / 3 ^ {3 * d + 1} := by
      rw [eq_div_iff (by positivity)]; linear_combination {ref}''')
    lines.append(
        f'''    have eD : (T H H : ℚ) = (3 : ℚ) ^ H / 3 := by
      rw [T_diag_pow H (by omega), zpow_sub₀ (by norm_num : (3 : ℚ) ≠ 0), zpow_one, zpow_natCast]''')
    mus = ", ".join(mu_ref(i) for i in range(0, k + 1))
    erw = ", ".join([f"e{d}" for d in range(k, 0, -1)] + ["eD"])
    pps = ", ".join(f"Pp{j}" for j in range(k, 0, -1))
    lines.append(
        f'''    rw [hst]
    simp only [Finset.sum_range_succ, Finset.sum_range_zero, zero_add, Nat.sub_self,
      Nat.add_zero, {mus}]
    rw [{erw}]
    simp only [{pps}, prodPoly_eval]
    norm_num
    field_simp
    ring''')
    return "\n".join(lines) + "\n"


def emit_grand_prod(k):
    return hb_option(k) + f'''
/-- **k={k} production `n`-form**: `T(n, n-{k}) = P_{k}(n)·3^(n-1-3·{k})` for all
`n ≥ 2·{k}+1`, from `P{k}_grand_of_banked` via `grand_to_prod`. -/
theorem P{k}_grand_prod
{anchor_hyps(k)} :
    ∀ n : ℕ, 2 * {k} + 1 ≤ n →
      (T n (n - {k}) : ℚ) = Pp{k}.eval (n : ℚ) * (3 : ℚ) ^ ((n : ℤ) - 1 - 3 * {k}) :=
  grand_to_prod (P{k}_grand_of_banked {anchor_args(k)})
'''


def emit_footer(kmax):
    prints = ""
    if kmax >= 4:
        prints = (f"#print axioms P{kmax}_grand_of_banked\n"
                  f"#print axioms P{kmax}_grand_prod\n")
    return f'''
end GrandPin

/-! ## Axiom sanity check -/

section Sanity

{prints}
end Sanity

end Polyplets
'''


# ---------------------------------------------------------------- main
ANCH_A = {}
ANCH_B = {}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(
        ROOT, "polyplets", "Polyplets", "Grand", "PinGrand.lean"))
    ap.add_argument("--kmax", type=int, default=KMAX)
    args = ap.parse_args()
    if not (1 <= args.kmax <= KMAX):
        die(f"--kmax must be in 1..{KMAX}")

    real = read_triangle()
    sweep = read_sweep()
    pindata = read_pindata()

    # cross-check the two production-polynomial sources.
    for k in range(0, KMAX + 1):
        if k in pindata and sweep[k] != pindata[k]:
            die(f"sweep.go vs pin-data.md mismatch at k={k}")

    T, P, mu = build(real, sweep)
    check_all(T, P, mu)

    # anchors + H<=18 enforcement.
    for k in range(1, KMAX + 1):
        ANCH_A[k] = T(2 * k + 1, k + 1)
        ANCH_B[k] = T(2 * k + 2, k + 2)
        for (n, H) in ((2 * k + 1, k + 1), (2 * k + 2, k + 2)):
            if H > HMAX_ANCHOR:
                die(f"anchor T({n},{H}) has H > {HMAX_ANCHOR}")

    # integer P-staircase coefficients pc_i = mu_i * 3^(2i-1).
    pc = {}
    for i in range(0, KMAX + 1):
        val = mu[i] * F(3) ** (2 * i - 1)
        if val.denominator != 1:
            die(f"pc_{i} = {val} is not an integer")
        pc[i] = val.numerator

    print("gen_grand_pin: ALL CHECKS PASS "
          "(staircase 209/209, P-staircase, anchors, weight-side mu_1..3, "
          f"pc integers, anchors H<=20); kmax={args.kmax}")

    inputs_line = ("results/triangle.txt, orchestrator/sweep.go, "
                   "polyplets/pin-data.md (2026-07-29, n <= 40 triangle).")
    out = [emit_header(inputs_line)]

    # Pstair for all levels.
    for k in range(1, args.kmax + 1):
        out.append(emit_pstair(k, pc))

    # Levels 1..3 grand forms from the closed forms.
    for k in (1, 2, 3):
        if k <= args.kmax:
            out.append(emit_P123_grand(k))

    # Levels 4..kmax: mu_val, grand_of_banked, grand_prod.
    for k in range(4, args.kmax + 1):
        num, e = mu_lit(mu[k])
        out.append(emit_mu_val(k, T, num, e))
        out.append(emit_grand_of_banked(k))
        out.append(emit_grand_prod(k))

    out.append(emit_footer(args.kmax))

    with open(args.out, "w") as f:
        f.write("".join(out))
    print(f"gen_grand_pin: wrote {args.out}")


if __name__ == "__main__":
    main()
