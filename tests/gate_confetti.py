#!/usr/bin/env python3
"""gate_confetti.py — Confetti (Motley rung 2) gate battery.

Spec: results/triangle-r3-ladder-gate.md §4, adapted per docs/motley-plan.md
"Rung 2 — Confetti".  Runs per built binary, per machine, before any
production --modp column.  Fail-closed: exits nonzero unless every GREEN
passes AND every RED fails; the receipt is written only on full success, and
the production runner (scripts/dalby_confetti_h18.sh) refuses to start
without a receipt whose sha256 matches the binary it is about to run.

GREEN-1  --modp [q^1] against an independent brute-force enumeration.
         Oracle: fixed king-connected polyplets enumerated by BFS growth
         (translation-normalized, no DP, no frontier), classified by bounding
         -box height h; C_H(n) = sum_{h<=H} (H-h+1) T_h(n).  Compared for
         H = 2..6, every n <= 8, every one of the 5 production primes.  This
         covers the six (H,W) boxes of the §4 battery and more: every cell of
         every listed box has h <= 6, n <= 8.
GREEN-2  the exact-payload battery, wholesale: tests/gate_cutcount_b1.py
         (banked-triangle compare + its own RED controls) must exit 0.
GREEN-3  identities: [q^0] = 0 is asserted in-engine on every --modp run
         (FATAL q0_nonzero_modp, exit 2).  NOTE, out loud per the plan: the
         --modp payload carries TWO streams — there is NO A(1)/binomial check
         in residue mode.  The held-out prime (RED-D, in the runner) and this
         battery carry that weight.
RED-A    NW-stencil drop (cross-cut stencil {r-1, r}): passes the in-engine
         identities and the state census; must be caught by GREEN-1.
RED-B    rook stencil (both cross-column diagonals dropped): the symmetric
         error class censuses cannot see; must be caught by GREEN-1.
RED-BOT  bottom-anchored: SW diagonal dropped at r = 0 only.  Measured
         2026-08-14 (docs/motley-plan.md, "What the in-engine self-checks do
         not check"): passes q0_zero AND q1eval_binomial at every height;
         must be caught by GREEN-1.
RED-C    fresh-class weight corrupted (q-b -> q-b+1): must make the engine
         itself exit 2 via q0_nonzero_modp (exercises the fail-closed path).

Each RED is a one-substitution mutant of the SAME source file, applied by
exact-string replacement that asserts exactly one occurrence (a drifted
source fails the gate rather than silently testing nothing), compiled with
the production flags.

Receipt (on success): <binary>.confetti-receipt with sha256, obs git stamp,
date, primes, and the battery verdict line.
"""

import datetime
import hashlib
import os
import re
import subprocess
import sys
import tempfile
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
B1 = os.path.join(ROOT, "build", "cutcount_b1")
SRC = os.path.join(ROOT, "cpp", "cutcount_b1.cpp")

PRIMES = [2147483647, 2147483629, 2147483587, 2147483579, 2147483563]
NB = 8          # brute oracle depth
HMAXB = 6       # brute oracle heights 2..HMAXB

KING = [(dc, dr) for dc in (-1, 0, 1) for dr in (-1, 0, 1) if (dc, dr) != (0, 0)]


def fixed_polyplets_by_height(nmax):
    """T[h][n] = number of translation-fixed king-connected n-cell shapes of
    bounding-box height exactly h, by BFS growth with normalization."""
    T = defaultdict(lambda: defaultdict(int))

    def norm(cells):
        mc = min(c for c, r in cells)
        mr = min(r for c, r in cells)
        return frozenset((c - mc, r - mr) for c, r in cells)

    cur = {norm([(0, 0)])}
    for n in range(1, nmax + 1):
        for s in cur:
            h = max(r for c, r in s) + 1
            T[h][n] += 1
        if n == nmax:
            break
        nxt = set()
        for s in cur:
            for (c, r) in s:
                for dc, dr in KING:
                    p = (c + dc, r + dr)
                    if p not in s:
                        nxt.add(norm(list(s) + [p]))
        cur = nxt
    return T


def oracle_rows(T):
    """C_H(n) for H = 2..HMAXB, n = 1..NB, exact integers."""
    C = {}
    for H in range(2, HMAXB + 1):
        C[H] = {n: sum((H - h + 1) * T[h][n] for h in range(1, H + 1))
                for n in range(1, NB + 1)}
    return C


def run_modp(binary, H, nmax, p):
    """Run --modp, return dict n -> residue, or ('exit', rc)."""
    with tempfile.TemporaryDirectory() as td:
        out = os.path.join(td, "row.out")
        r = subprocess.run([binary, "--modp", str(H), str(nmax), str(p), out],
                           capture_output=True, text=True)
        if r.returncode != 0:
            return ("exit", r.returncode, r.stderr)
        rows = {}
        for line in open(out):
            n, v = line.split()
            rows[int(n)] = int(v)
        return rows


def modp_matches_oracle(binary, C, primes, heights):
    """Returns (ok, ncells, first_bad).  ok = every cell matches."""
    ncells = 0
    for H in heights:
        for p in primes:
            got = run_modp(binary, H, NB, p)
            if isinstance(got, tuple):
                return (False, ncells, f"H={H} p={p} engine exit {got[1]}")
            for n in range(1, NB + 1):
                ncells += 1
                if got.get(n, 0) != C[H][n] % p:
                    return (False, ncells,
                            f"H={H} n={n} p={p}: engine {got.get(n)} "
                            f"oracle {C[H][n] % p}")
    return (True, ncells, None)


MUTANTS = [
    ("RED-A_nw_drop",
     "    if (r > 0) push(H);",
     "    if (0 && r > 0) push(H);",
     "mismatch"),
    ("RED-B_rook",
     "    if (r + 1 < H) push(H - 2);\n    push(H - 1);\n    if (r > 0) push(H);",
     "    push(H - 1);",
     "mismatch"),
    ("RED-BOT_bottom_anchored",
     "    if (r + 1 < H) push(H - 2);",
     "    if (r + 1 < H && r > 0) push(H - 2);",
     "mismatch"),
    ("RED-C_weight",
     "  out[n++] = { shifted(key, H, mx + 1), -b, 1, 1 };",
     "  out[n++] = { shifted(key, H, mx + 1), -b + 1, 1, 1 };",
     "exit2"),
]


def build_mutant(name, old, new, td):
    src = open(SRC).read()
    cnt = src.count(old)
    assert cnt == 1, f"{name}: anchor text found {cnt} times (want 1) -- source drifted, gate refuses"
    msrc = os.path.join(td, name + ".cpp")
    open(msrc, "w").write(src.replace(old, new))
    mbin = os.path.join(td, name)
    r = subprocess.run(["c++", "-O2", "-std=c++17", "-I", os.path.join(ROOT, "cpp"),
                        msrc, "-o", mbin], capture_output=True, text=True)
    assert r.returncode == 0, f"{name}: mutant build failed:\n{r.stderr[-2000:]}"
    return mbin


def main():
    receipt = B1 + ".confetti-receipt"
    if os.path.exists(receipt):
        os.unlink(receipt)   # stale receipts die first; rewritten only on GREEN

    assert os.path.exists(B1), f"missing {B1} -- build first"
    assert os.path.exists(SRC)

    fails = []
    say = print

    T = fixed_polyplets_by_height(NB)
    # oracle sanity anchor: fixed king polyplets total = A030232
    tot = {n: sum(T[h][n] for h in T) for n in range(1, NB + 1)}
    A030232 = {1: 1, 2: 4, 3: 20, 4: 110, 5: 638, 6: 3832, 7: 23592, 8: 147941}
    assert tot == A030232, f"brute oracle census broken: {tot}"
    C = oracle_rows(T)
    heights = list(range(2, HMAXB + 1))

    ok, ncells, bad = modp_matches_oracle(B1, C, PRIMES, heights)
    say(f"GREEN-1 brute battery: {ncells} cells (H=2..{HMAXB}, n<=8, "
        f"{len(PRIMES)} primes): {'OK' if ok else 'FAIL ' + str(bad)}")
    if not ok:
        fails.append("GREEN-1")

    r = subprocess.run([sys.executable, os.path.join(HERE, "gate_cutcount_b1.py")],
                       capture_output=True, text=True)
    say(f"GREEN-2 exact battery (gate_cutcount_b1.py): rc={r.returncode} "
        f"{'OK' if r.returncode == 0 else 'FAIL'}")
    if r.returncode != 0:
        fails.append("GREEN-2")
        say(r.stdout[-2000:] + r.stderr[-2000:])

    say("GREEN-3 note: --modp asserts [q^0]=0 in-engine; residue mode has NO "
        "A(1)/binomial stream -- held-out prime + this battery carry it.")

    with tempfile.TemporaryDirectory() as td:
        for name, old, new, expect in MUTANTS:
            mbin = build_mutant(name, old, new, td)
            if expect == "exit2":
                got = run_modp(mbin, 4, NB, PRIMES[0])
                caught = isinstance(got, tuple) and got[1] == 2
                how = f"engine exit {got[1] if isinstance(got, tuple) else 0}"
            else:
                mok, _, mbad = modp_matches_oracle(mbin, C, PRIMES[:1], heights)
                caught = not mok
                how = f"first divergence: {mbad}" if caught else "NOT CAUGHT"
            say(f"{name}: {'caught -- ' + how if caught else 'FAIL: mutant passed the battery'}")
            if not caught:
                fails.append(name)

    if fails:
        say(f"CONFETTI GATE: RED ({', '.join(fails)}) -- no receipt written")
        return 1

    sha = hashlib.sha256(open(B1, "rb").read()).hexdigest()
    r = subprocess.run([B1, "--modp", "2", "2", str(PRIMES[0]), "/dev/null"],
                       capture_output=True, text=True)
    m = re.search(r"git=(\S+)", r.stderr)
    stamp = m.group(1) if m else "UNKNOWN"
    with open(receipt, "w") as f:
        f.write(f"sha256={sha}\n")
        f.write(f"git={stamp}\n")
        f.write(f"date={datetime.datetime.now().isoformat()}\n")
        f.write(f"primes={','.join(str(p) for p in PRIMES)}\n")
        f.write("verdict=GREEN\n")
    say(f"CONFETTI GATE: GREEN -- receipt {receipt} (sha256 {sha[:16]}..., git={stamp})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
