#!/usr/bin/env python3
"""The mod-p recovery pipeline's own soundness gate, run on a BANKED fixed-height GF.

Purpose: results/fixed_height_gfs.txt banks H=11 with validated=False; the owed
question (results/diagonal-formula.md, results/anisotropic-not-dfinite.md) was whether
P_11/Q_11 is WRONG -- a CRT wraparound -- or merely unvalidated.  Test: Q_H * B_H ==
P_H as power series modulo a fresh prime disjoint from the recovery pool, for
n = 0..2*order+30, with B_H(n) from the transfer-matrix engine build/gf_modp.
Reports the first mismatching n, which localizes the first bad coefficient
(degree = n - H).  Reads results/, writes nothing there.

    gf_h11_validate.py [H] [--perturb DEG]

H defaults to 11.  --perturb DEG is the RED control: add 1 to Q[DEG] before the
check, which must then fail at n = DEG + H exactly.  Exit 0 = the banked entry
passes; 1 = mismatch; 2 = RED control did not fire where expected.

Machine: gympie.  H=8 ~5 s, H=9 ~45 s, H=11 ~15 min (engine 14.8 s + 0.029 s per
column at N = 26792), ~300 MB, 1 core.  Over five minutes: run in a tmux window.
Measured 2026-09-05: H=11 first mismatch at n = 8170 (degree 8159).
"""
import os, re, subprocess, sys, time
from operator import mul

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GF = os.path.join(ROOT, "build", "gf_modp")
VAL_PRIME = 1073741789          # largest prime below 2^30; the recovery pool sits below 2^31
assert all(VAL_PRIME % q for q in range(2, 32769)), "VAL_PRIME must be prime"


def seq_modp(H, N, p):
    out = subprocess.run([GF, str(H), str(N), str(p)], capture_output=True, text=True).stdout
    d = {0: 0}
    for line in out.split("\n"):
        q = line.split()
        if len(q) == 2:
            d[int(q[0])] = int(q[1])
    return [d[n] for n in range(N + 1)]


args = [a for a in sys.argv[1:] if not a.startswith("--")]
H = int(args[0]) if args else 11
perturb = int(sys.argv[sys.argv.index("--perturb") + 1]) if "--perturb" in sys.argv else None

txt = open(os.path.join(ROOT, "results", "fixed_height_gfs.txt")).read()
m = re.search(r"H=%d\s+order=(\d+)\s+validated=(\w+)[^\n]*\nP: (\[[^\]]*\])\nQ: (\[[^\]]*\])" % H, txt)
d, flag, P, Q = int(m.group(1)), m.group(2), eval(m.group(3)), eval(m.group(4))
if perturb is not None:
    Q[perturb] += 1
N = 2 * d + 30
print(f"banked H={H}: order={d} validated={flag}; testing to N={N} mod {VAL_PRIME}"
      + (f"; RED control: Q[{perturb}] += 1" if perturb is not None else ""), flush=True)
t0 = time.time()
B = seq_modp(H, N, VAL_PRIME)
print(f"engine sweep done in {time.time()-t0:.1f}s", flush=True)

t1 = time.time()
Qp = [q % VAL_PRIME for q in Q]                       # pre-reduce ONCE (bignum mods are the trap)
Pp = [p % VAL_PRIME for p in P] + [0] * (N + 1)
first = None
for n in range(N + 1):
    acc = sum(map(mul, Qp, B[n::-1]))      # map stops at the shorter operand
    if acc % VAL_PRIME != Pp[n]:
        first = n
        break
print(f"convolution check done in {time.time()-t1:.1f}s", flush=True)
if perturb is not None:
    want = perturb + H
    if first == want:
        print(f"RED control fired at n={first} = DEG + H, as required")
        sys.exit(0)
    print(f"RED control FAILED: expected first mismatch at n={want}, got {first}")
    sys.exit(2)
if first is None:
    print(f"RESULT: banked H={H} PASSES the fresh-prime series gate (no mismatch to n={N})")
    sys.exit(0)
print(f"RESULT: banked H={H} FAILS the fresh-prime series gate; first mismatch at n={first} (degree {first-H})")
sys.exit(1)
