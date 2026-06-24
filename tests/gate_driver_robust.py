#!/usr/bin/env python3
# Driver-robustness gate. Proves the hardened reach driver (an_modp_crt.sh) and combine
# (crt_combine.py) REFUSE to produce a result from a crashed / raced / corrupted sweep --
# the exact failure mode that once yielded a wrong a(22) (a dead sweep's empty output was
# silently summed as a zero). Strategy: build a complete valid run for a tiny N, confirm
# it is correct, then inject each corruption and assert the combine aborts non-zero.
import os
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
N = 4
DIR = os.path.join(ROOT, f"runs/anmodp_N{N}")
PRIMES = ["2147483647", "2147483629", "2147483587"]
fails = 0


def run(cmd):
    return subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)


def combine():
    return run([sys.executable, "scripts/crt_combine.py", DIR, str(N)] + PRIMES)


def check(name, ok):
    global fails
    print(f"  {'ok  ' if ok else 'FAIL'} {name}")
    fails += 0 if ok else 1


shutil.rmtree(DIR, ignore_errors=True)

# 1. A valid run combines and is correct (vs the OEIS fixture).
r = run(["bash", "scripts/an_modp_crt.sh", str(N)])
exp = next((int(x[1]) for x in (ln.split() for ln in
           open(os.path.join(ROOT, "fixtures/b006770.txt"))) if len(x) == 2 and int(x[0]) == N), None)
got = next((int(x[1]) for x in (ln.split() for ln in r.stdout.splitlines())
           if len(x) == 2 and int(x[0]) == N), None)
check(f"valid run: a({N})={got} == fixture {exp}", r.returncode == 0 and got is not None and got == exp)

# 2. Intact rows -> combine exits 0.
check("intact rows -> combine exit 0", combine().returncode == 0)

victim = os.path.join(DIR, f"rows_p{PRIMES[0]}_H{N}.txt")
bak = victim + ".bak"
shutil.copy(victim, bak)

# 3. Missing sweep file (crash before any output) -> abort.
os.remove(victim)
check("missing file -> combine abort", combine().returncode != 0)
shutil.copy(bak, victim)

# 4. Empty sweep file (crash, e.g. std::bad_alloc) -> abort.
open(victim, "w").close()
check("empty file -> combine abort", combine().returncode != 0)
shutil.copy(bak, victim)

# 5. Duplicate-n line (the concurrent-run / race corruption symptom) -> abort.
with open(victim, "a") as f:
    f.write(f"{N} 12345\n")
check("duplicate-n (race) -> combine abort", combine().returncode != 0)
shutil.copy(bak, victim)

# 6. Lock held -> a second run on the same dir fails fast (exit 3), no clobber.
os.makedirs(os.path.join(DIR, ".lock"), exist_ok=True)
check("lock held -> second run exit 3", run(["bash", "scripts/an_modp_crt.sh", str(N)]).returncode == 3)
shutil.rmtree(os.path.join(DIR, ".lock"), ignore_errors=True)

shutil.rmtree(DIR, ignore_errors=True)
print("GATE DRIVER-ROBUST:", "GREEN" if fails == 0 else f"RED ({fails} failed)")
sys.exit(1 if fails else 0)
