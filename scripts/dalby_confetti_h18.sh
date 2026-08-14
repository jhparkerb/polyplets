#!/bin/bash
# Motley rung 2 (Confetti) production run: C_18(n) mod 5 primes, n <= 40.
#
# Purpose: T(n,18) = C_18 - 2*C_17 + C_16, closing a(n) rule-independently
# for n <= 35.  Payload: the committed --modp mode (2 streams, u32), five
# 31-bit primes run as SEQUENTIAL passes; exact C_18 reconstructed by CRT
# from the first FOUR primes (product ~2^124 against values < 2^112), the
# FIFTH prime held out: its residue is PREDICTED from the reconstruction and
# compared (RED-D of results/triangle-r3-ladder-gate.md §4).
#
# Target machine: dalby.  Binary: ~/src/pm-halfmeasure/build/cutcount_b1.
#
# RECEIPT ENFORCEMENT (new with this rung, per docs/motley-plan.md): this
# runner refuses to start unless <binary>.confetti-receipt exists, says
# verdict=GREEN, and its sha256 matches the binary AS HASHED NOW.  The
# receipt is written only by tests/gate_confetti.py on a fully-green
# battery (brute oracle x 5 primes, exact battery, 4 mutant REDs caught).
#
# Predicted cost (docs/motley-plan.md, re-priced after the measured H=17
# point): census H=18 ~ 71.5M windows (x3.02/height, measured); RAM well
# under the H=17 run's 95 GB (u32 2-stream payload is 328 B/window vs
# u128 3-stream 1968 B); wall unmeasured for the residue loop -- the first
# pass IS the measurement.  Five passes, sequential, one core.
#
# Kill/resume: the unit is one prime pass.  Kill any pass by PID; re-running
# the script skips passes whose output file exists and runs the rest.
#
# Exact command:  ./dalby_confetti_h18.sh
#
# Fail-closed: set -e; engine exits 2 on q0_nonzero_modp; the assembly
# refuses on CRT overflow (>= 2^112), held-out mismatch, any T(n,18)
# mismatch against the incumbent triangle, or zero cells compared.

set -euo pipefail

# Paths overridable via env for the fail-closed self-test
# (synthetic-fixture RED runs); production uses the defaults.
BIN="${CONFETTI_BIN:-$HOME/src/pm-halfmeasure/build/cutcount_b1}"
RECEIPT="$BIN.confetti-receipt"
OUT="${CONFETTI_OUT:-$HOME/var/motley-h18}"
C16="${CONFETTI_C16:-$HOME/var/motley-step0/rows/C16.out}"
C17="${CONFETTI_C17:-$HOME/var/motley-h17/C17.out}"
TRIANGLE="${CONFETTI_TRIANGLE:-$HOME/var/motley-h17/triangle.txt}"
NMAX=40
H=18
PRIMES=(2147483647 2147483629 2147483587 2147483579 2147483563)

# ---- receipt gate: no green receipt for THIS binary, no run ----
[ -s "$RECEIPT" ] || { echo "REFUSED: no gate receipt $RECEIPT -- run tests/gate_confetti.py" >&2; exit 1; }
grep -q '^verdict=GREEN$' "$RECEIPT" || { echo "REFUSED: receipt verdict is not GREEN" >&2; exit 1; }
want_sha=$(grep '^sha256=' "$RECEIPT" | cut -d= -f2)
have_sha=$(sha256sum "$BIN" | cut -d' ' -f1)
[ "$want_sha" = "$have_sha" ] || { echo "REFUSED: receipt sha $want_sha != binary sha $have_sha (rebuilt since gating?)" >&2; exit 1; }

for f in "$C16" "$C17" "$TRIANGLE"; do
  [ -s "$f" ] || { echo "MISSING $f" >&2; exit 1; }
done

mkdir -p "$OUT"

for p in "${PRIMES[@]}"; do
  f="$OUT/C18.p$p.out"
  if [ ! -s "$f" ]; then
    echo "=== C_18 mod $p start $(date -Is) host=$(hostname)" >> "$OUT/run.log"
    "$BIN" --modp $H $NMAX "$p" "$f.tmp" 2>&1 | tee -a "$OUT/run.log"
    mv "$f.tmp" "$f"
    echo "=== C_18 mod $p done $(date -Is)" >> "$OUT/run.log"
  fi
done

python3 - "$OUT" "$C17" "$C16" "$TRIANGLE" "${PRIMES[@]}" <<'PY'
import sys

outdir, c17f, c16f, trif = sys.argv[1:5]
primes = [int(p) for p in sys.argv[5:]]
crt_primes, heldout = primes[:4], primes[4]

def rows(p):
    d = {}
    for line in open(p):
        n, v = line.split()
        d[int(n)] = int(v)
    return d

res = {p: rows(f"{outdir}/C18.p{p}.out") for p in primes}
C17, C16 = rows(c17f), rows(c16f)
want = {}
for line in open(trif):
    if line.startswith('#'):
        continue
    n, H, v = line.split()
    if int(H) == 18:
        want[int(n)] = int(v)

M = 1
for p in crt_primes:
    M *= p
BOUND = 1 << 112

C18 = {}
for n in range(1, 41):
    x = 0
    for p in crt_primes:
        Mi = M // p
        x = (x + res[p][n] * Mi * pow(Mi, -1, p)) % M
    if x >= BOUND:
        print(f"FATAL crt_overflow n={n}: reconstruction >= 2^112")
        sys.exit(2)
    if x % heldout != res[heldout][n]:
        print(f"FATAL heldout_mismatch n={n}: predict {x % heldout} "
              f"measured {res[heldout][n]}")
        sys.exit(2)
    C18[n] = x
print(f"RED-D held-out prime {heldout}: 40/40 residues predicted correctly")

match = mismatch = 0
for n in sorted(C18):
    t = C18[n] - 2 * C17[n] + C16[n]
    if n in want:
        if t == want[n]:
            match += 1
        else:
            mismatch += 1
            print(f"MISMATCH T({n},18): motley {t}  incumbent {want[n]}")
    elif t:
        print(f"NOTE T({n},18) = {t} with no banked value")

with open(f"{outdir}/C18.out", "w") as f:
    for n in sorted(C18):
        f.write(f"{n} {C18[n]}\n")

print(f"T(n,18) vs results/triangle.txt: {match} match, {mismatch} mismatch")
if mismatch or match == 0:
    sys.exit(2)
print("CONFETTI H=18: GREEN")
PY
