#!/usr/bin/env python3
# Strip-fast gate. The indexed-array engine (cpp/strip_mu_fast.cpp, frozen per-stage
# sparse operators) is ~200x the hash-map engine it replaces, and speed is exactly the
# circumstance in which a silently-wrong operator table would go unnoticed. So the gate
# pins it, in seconds, against two things it cannot influence:
#
#   1. the OLD engine (build/strip_mu_kink, unordered_map, validated against the
#      fixed-height GF roots) -- same mu_H to all printed digits and the same state
#      count, for every H it is cheap to run both at;
#   2. the PUBLISHED certificates (results/strip-mu-certificates.md) -- the exact
#      unsigned-__int128 Collatz-Wielandt check must PASS at the certified numerator
#      and FAIL at numerator+1, which brackets mu_H to the last certified digit.
#
# The RED arms live in the binary's own --selftest (a corrupted transition table and a
# corrupted finalize map must both move mu_6; an over-claim and a vacuous all-zero
# vector must both be refused) and are run here first: if the tables were not what the
# answer depends on, every comparison below would be theatre.
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HMAX = 8                      # both engines finish H<=8 in ~3 s total
# Certified numerators over 10^7, from results/strip-mu-certificates.md. Pinned here
# rather than parsed from results/strip_mu_certificates.log: the log is append-only and
# a scheduled run may be writing to it while the gate runs.
CERTS = {2: 24142135, 3: 34437183, 4: 41823214, 5: 47178012,
         6: 51153244, 7: 54178476, 8: 56533727}
DEN = 10000000
fails = 0


def check(name, ok):
    global fails
    print(f"  {'ok  ' if ok else 'FAIL'} {name}")
    fails += 0 if ok else 1


def run(cmd):
    return subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)


def ladder(binary):
    """H -> (states, mu_H string) from an engine's table, both share the format."""
    r = run([binary, "2", str(HMAX)])
    if r.returncode != 0:
        return None
    out = {}
    for line in r.stdout.splitlines():
        parts = [p.strip() for p in line.split("|")]
        if len(parts) < 3 or not parts[0].isdigit():
            continue
        out[int(parts[0])] = (int(parts[1]), parts[2])
    return out


print("gate-strip-fast: indexed-array strip engine vs the map engine and the certificates")

# 0. RED-first: the binary's own corruption / over-claim / vacuous-vector arms.
r = run(["./build/strip_mu_fast", "--selftest"])
check("--selftest (corrupted tables and over-claims are refused)", r.returncode == 0)
if r.returncode != 0:
    sys.stdout.write(r.stdout)

# 1. Old engine vs new engine, mu_H to all printed digits and exact state counts.
old, new = ladder("./build/strip_mu_kink"), ladder("./build/strip_mu_fast")
check("both engines produced a ladder", old is not None and new is not None)
if old and new:
    check(f"same heights covered (2..{HMAX})", sorted(old) == sorted(new) == list(range(2, HMAX + 1)))
    for H in sorted(set(old) & set(new)):
        check(f"H={H}: mu {new[H][1]} == old {old[H][1]}", new[H][1] == old[H][1])
        check(f"H={H}: states {new[H][0]} == old {old[H][0]}", new[H][0] == old[H][0])

# 2. The exact kernel brackets each published certificate: PASS at num, FAIL at num+1.
for H, num in sorted(CERTS.items()):
    p = run(["./build/strip_mu_fast", "--verify", str(H), str(num), str(DEN)])
    f = run(["./build/strip_mu_fast", "--verify", str(H), str(num + 1), str(DEN)])
    check(f"H={H}: exact check PASSes the certified {num}/{DEN}",
          p.returncode == 0 and "result=PASS" in p.stdout)
    check(f"H={H}: exact check FAILs the over-claim {num + 1}/{DEN}",
          f.returncode == 1 and "result=FAIL" in f.stdout)

# 3. Bad arguments are refused, not clamped (fail-closed CLI).
for bad in [["--verify", "1", "1", "1"], ["--bogus"], ["--verify", "8", "1", "0"],
            ["--verify", "8", str(CERTS[8]), str(DEN), "--vbits", "120"]]:
    check(f"refuses {' '.join(bad)}", run(["./build/strip_mu_fast"] + bad).returncode == 2)

print("gate-strip-fast:", "PASS" if fails == 0 else f"FAIL ({fails})")
sys.exit(0 if fails == 0 else 1)
