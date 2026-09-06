#!/usr/bin/env python3
"""Generate Polyplets/Upper/BuiData<RD>.lean: the king Bui convolution
certificate (docs/proofs/polyplet-upper-bound.md, BREAKTHROUGH + Certificate
Squeeze) exported as a `RatCert` for Polyplets/Upper/Certificate.lean.

The system and the certificate algorithm are exactly those of
experiments/king_bui.py / experiments/king_certificate.py (canonical 'll'
casing order, eps = 1e-3 safety margin, common denominator CD = 10^6,
ceil-to-CD repair sweeps).  Fail-closed:

  * the closure size must match the banked type count (RD=2: 185, RD=3: 5930);
  * the rational rate x must equal the banked value
    (RD=2: 106251/10^6 => lambda <= 9.4117...; RD=3: 2147/20000 => 9.31532...);
  * the super-solution inequalities are verified in exact Fraction arithmetic
    (the same check king_certificate.py performs), AND in the cleared-
    denominator integer form that the emitted Lean `decide` re-checks;
  * every certificate value must have denominator dividing CD;
  * the rank table (free king neighbors) must strictly decrease along every
    T'-edge, and every rule index must be in range;
  * unless --skip-oracle, `python3 -m experiments.king_certificate <RD>` is
    run as an independent oracle and must print the same x and PASS.

ANY failure aborts with no output.  Determinism note: the certificate values
come from a float fixpoint iteration + exact rational repair; the emitted file
is deterministic for a given platform/Python, and any regeneration is
re-validated by the same fail-closed checks (and by Lean's kernel `decide`),
so a differing-but-valid certificate is still a proof of the same bound.

Run from the repo root:
  python3 scripts/gen_bui_cert.lean.py --rd 2
  python3 scripts/gen_bui_cert.lean.py --rd 3 --tactic native_decide
"""
import argparse
import math
import os
import re
import subprocess
import sys
from fractions import Fraction as F

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from experiments.king_types import OFF  # noqa: E402

KING8 = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1)]

BANKED = {
    2: {"nt": 185, "x": F(106251, 10**6)},
    3: {"nt": 5930, "x": F(2147, 20000)},
}

CD = 10**6      # common denominator of every exported value
DENOM = 10**6   # denominator used when picking the rational x
EPS = 1e-3      # safety margin below x*


def die(msg):
    sys.exit(f"gen_bui_cert: ABORT: {msg}")


def free_cells(f):
    return [d for d in KING8 if d not in f]


# ---------------------------------------------------------------- closure
def build_closure(rd):
    """The Bui-faithful king system at split window RD (== king_certificate.py:
    canonical lowest-leftmost casing order)."""
    wd = [(dx, dy) for dx in range(-rd, rd + 1) for dy in range(-rd, rd + 1)
          if (dx, dy) != (0, 0)]

    def d_type(f, d):
        ke = {(0, 0)} | (set(KING8) - {d}) | set(f)
        return frozenset(o for o in wd if (d[0] + o[0], d[1] + o[1]) in ke)

    def canonical(free):
        return min(free, key=lambda p: (p[1], p[0]))

    recur = {}
    g8 = frozenset({OFF[o] for o in ('W', 'SW', 'S', 'SE')})
    seen = {g8}
    q = [g8]
    while q:
        t = q.pop()
        fr = free_cells(t)
        if not fr:
            recur[t] = None
            continue
        d = canonical(fr)
        tp = frozenset(set(t) | {d})
        dt = d_type(t, d)
        recur[t] = (tp, dt)
        for xx in (tp, dt):
            if xx not in seen:
                seen.add(xx)
                q.append(xx)
    tl = list(recur)
    ix = {t: i for i, t in enumerate(tl)}
    rule = [None if recur[t] is None else (ix[recur[t][0]], ix[recur[t][1]])
            for t in tl]
    return tl, rule, ix[g8]


# ---------------------------------------------------------------- certificate
def find_certificate(rule, root, nt):
    """== experiments/king_certificate.py: float bisection for x*, rational
    x below it, float fixpoint, ceil-to-CD rationalization + repair."""
    def fstep(v, x):
        nv = [0.0] * nt
        for i in range(nt):
            r = rule[i]
            if r is None:
                nv[i] = x
            else:
                a = v[r[0]]
                nv[i] = a + a * v[r[1]]
        return nv

    def bounded(x, iters=6000, cap=1e12):
        v = [x] * nt
        for _ in range(iters):
            nv = fstep(v, x)
            if nv[root] > cap:
                return None
            if abs(nv[root] - v[root]) < 1e-14 * nv[root]:
                return v
            v = nv
        return v

    lo, hi = 1 / 13.0, 1 / 4.0
    for _ in range(60):
        m = 0.5 * (lo + hi)
        if bounded(m) is not None:
            lo = m
        else:
            hi = m
    xstar = lo

    x = F(round(xstar * (1 - EPS) * DENOM), DENOM)
    vfix = bounded(float(x), iters=200000, cap=1e300)
    if vfix is None:
        die("system diverges at chosen x; increase EPS")

    def ceil_cd(fr):
        return F(math.ceil(fr * CD), CD)

    u = [ceil_cd(F(val).limit_denominator(CD)) for val in vfix]

    def fx_exact(u, i):
        r = rule[i]
        if r is None:
            return x
        a = u[r[0]]
        return a + a * u[r[1]]

    sweeps = None
    for sweep in range(5000):
        viol = 0
        for i in range(nt):
            need = fx_exact(u, i)
            if u[i] < need:
                u[i] = ceil_cd(need)
                viol += 1
        if viol == 0:
            sweeps = sweep
            break
    if sweeps is None:
        die("repair did not converge; x too close to x*")

    # exact verification (the king_certificate.py check, replicated)
    if not all(u[i] >= fx_exact(u, i) for i in range(nt)):
        die("exact Fraction certificate check FAILED")
    return x, u, sweeps


# ---------------------------------------------------------------- validation
def validate(rd, rule, ranks, root, x, u, nt):
    b = BANKED[rd]
    if nt != b["nt"]:
        die(f"type count {nt} != banked {b['nt']}")
    if x != b["x"]:
        die(f"x = {x} != banked {b['x']}")
    if root < 0 or root >= nt:
        die("root out of range")
    if x.numerator * (CD // x.denominator) != (x * CD).numerator or (x * CD).denominator != 1:
        die("x does not scale to denominator CD")
    for i, v in enumerate(u):
        if CD % v.denominator != 0:
            die(f"u[{i}] denominator {v.denominator} does not divide CD")
    xn = int(x * CD)
    nums = [int(v * CD) for v in u]
    if xn <= 0:
        die("X <= 0")
    for i in range(nt):
        r = rule[i]
        if r is None:
            if not xn <= nums[i]:
                die(f"integer base check fails at row {i}")
        else:
            a, bb = r
            if not (0 <= a < nt and 0 <= bb < nt):
                die(f"rule index out of range at row {i}")
            if not ranks[a] < ranks[i]:
                die(f"rank does not decrease at row {i}")
            if not nums[a] * CD + nums[a] * nums[bb] <= nums[i] * CD:
                die(f"integer super-solution check fails at row {i}")
    return xn, nums


def run_oracle(rd, x):
    """Independent cross-check: experiments/king_certificate.py itself."""
    print(f"gen_bui_cert: running oracle `python3 -m experiments.king_certificate {rd}` ...")
    p = subprocess.run([sys.executable, "-m", "experiments.king_certificate", str(rd)],
                       cwd=ROOT, capture_output=True, text=True)
    out = p.stdout
    if p.returncode != 0:
        die(f"oracle exited {p.returncode}:\n{out}\n{p.stderr}")
    m = re.search(r"x = (\d+)/(\d+) =", out)
    if not m:
        die(f"oracle output unparsable:\n{out}")
    ox = F(int(m.group(1)), int(m.group(2)))
    if ox != x:
        die(f"oracle x = {ox} != generator x = {x}")
    if "EXACT certificate check: PASS" not in out:
        die("oracle did not PASS")
    print("gen_bui_cert: oracle agrees (same x, PASS)")


# ---------------------------------------------------------------- Lean emission
CHUNK = 400


def off_name(o):
    for k, v in OFF.items():
        if v == o:
            return k
    return None


def type_comment(t):
    """Human-readable forbidden set: king ring by name, window cells by offset."""
    named = sorted(off_name(o) for o in t if off_name(o) is not None)
    rest = sorted((o for o in t if off_name(o) is None), key=lambda p: (p[1], p[0]))
    parts = named + [f"({dx},{dy})" for dx, dy in rest]
    return "{" + ",".join(parts) + "}"


def emit_chunks(name, ty, items, fmt):
    out = []
    nch = (len(items) + CHUNK - 1) // CHUNK
    for c in range(nch):
        body = ", ".join(fmt(v) for v in items[c * CHUNK:(c + 1) * CHUNK])
        out.append(f"private def {name}{c} : {ty} := [{body}]\n")
    concat = " ++ ".join(f"{name}{c}" for c in range(nch))
    out.append(f"def {name} : {ty} := {concat}\n")
    return "".join(out)


def fmt_rule(r):
    if r is None:
        return "none"
    return f"some ({r[0]}, {r[1]})"


def emit(rd, tl, rule, ranks, root, xn, nums, tactic, sweeps, with_table):
    nt = len(tl)
    lam = F(CD, xn)
    lines = [f'''/-
Copyright (c) 2026 Jason H Parker. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Jason H Parker
-/
import Polyplets.Upper.Certificate

/-!
# BuiData{rd}: the exported RD={rd} king Bui certificate

The {nt}-type king convolution system at split window RD = {rd} and its exact
rational super-solution at x = {xn}/{CD}, giving the conditional bound
`lambda <= {lam.numerator}/{lam.denominator}` = {float(lam):.6f} (see `Upper/BuiRD{rd}.lean`).

Machine-generated by `scripts/gen_bui_cert.lean.py --rd {rd}` from the system of
`experiments/king_bui.py` / `experiments/king_certificate.py` (canonical 'll'
casing, eps = 1e-3, repair converged after {sweeps} sweeps); cross-checked
against `python3 -m experiments.king_certificate {rd}` (same x, exact-check PASS).
Do not edit by hand; regenerate instead.

`buiRD{rd}_valid` is the *entire arithmetic side* of the certificate: index
bounds, rank descent, and the cleared-denominator super-solution inequalities,
checked by `{tactic}`.  The combinatorial side stays a named hypothesis
(`KingBuiSystemRD{rd}Holds`).
-/

namespace Polyplets

section BuiData{rd}
set_option linter.style.longLine false
''']
    if tactic == "native_decide":
        lines.append("set_option linter.style.nativeDecide false\n")
    if with_table:
        lines.append(
            "/- Type table (index : forbidden offsets, x right / y up; king ring by\n"
            "   compass name, split-window cells by (dx,dy)):\n")
        for i, t in enumerate(tl):
            lines.append(f"   {i:4d} : {type_comment(t)}\n")
        lines.append("-/\n")
    lines.append("\n/-- Casing table: `none` = base, `some (T', D)` = split. -/\n")
    lines.append(emit_chunks(f"buiRD{rd}Rules", "List (Option (ℕ × ℕ))", rule, fmt_rule))
    lines.append("\n/-- Free-king-neighbor counts (the termination measure). -/\n")
    lines.append(emit_chunks(f"buiRD{rd}Ranks", "List ℕ", ranks, str))
    lines.append(f"\n/-- Certificate numerators: `u_i = nums[i] / {CD}`. -/\n")
    lines.append(emit_chunks(f"buiRD{rd}Nums", "List ℕ", nums, str))
    lines.append(f'''
/-- The RD={rd} king Bui certificate: {nt} types, rate `x = {xn}/{CD}`,
anchor type `{root}` (the G8 corner type, W/SW/S/SE forbidden). -/
def buiRD{rd} : RatCert :=
  ⟨{CD}, {xn}, {root}, buiRD{rd}Rules, buiRD{rd}Ranks, buiRD{rd}Nums⟩

set_option maxRecDepth 8192 in
/-- **The certificate arithmetic**, machine-checked: every side condition of
`RatCert.valid` — positivity, table lengths, index bounds, rank descent, and
the {nt} cleared-denominator super-solution inequalities. -/
theorem buiRD{rd}_valid : buiRD{rd}.valid = true := by {tactic}

end BuiData{rd}

end Polyplets
''')
    return "".join(lines)


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rd", type=int, default=2, choices=(2, 3))
    ap.add_argument("--tactic", default=None, choices=(None, "decide", "native_decide"))
    ap.add_argument("--out", default=None)
    ap.add_argument("--skip-oracle", action="store_true")
    args = ap.parse_args()
    rd = args.rd
    tactic = args.tactic or ("decide" if rd == 2 else "native_decide")
    out = args.out or os.path.join(ROOT, "polyplets", "Polyplets", "Upper",
                                   f"BuiData{rd}.lean")

    tl, rule, root = build_closure(rd)
    nt = len(tl)
    print(f"gen_bui_cert: king system RD={rd}: {nt} types, root={root}")
    ranks = [len(free_cells(t)) for t in tl]

    x, u, sweeps = find_certificate(rule, root, nt)
    print(f"gen_bui_cert: x = {x}  lambda <= {float(1/x):.6f}  "
          f"(repair sweeps: {sweeps}, exact Fraction check PASS)")

    xn, nums = validate(rd, rule, ranks, root, x, u, nt)
    print(f"gen_bui_cert: fail-closed checks PASS (banked x, {nt} integer rows, "
          f"rank descent, denominators | {CD})")

    if not args.skip_oracle:
        run_oracle(rd, x)

    text = emit(rd, tl, rule, ranks, root, xn, nums, tactic, sweeps,
                with_table=(rd == 2))
    with open(out, "w") as f:
        f.write(text)
    print(f"gen_bui_cert: wrote {out}")


if __name__ == "__main__":
    main()
