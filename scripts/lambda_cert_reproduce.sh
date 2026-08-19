#!/bin/bash
# lambda_cert_reproduce.sh --- acceptance-queue item 5, the clean-box half.
#
# PURPOSE   L3 states 6.543 <= lambda <= 9.3154 and calls both ends checkable in
#           exact arithmetic. The lower end rests on one receipt: mu_17 >=
#           6543/1000, banked in results/strip_mu_certificates.log from a gympie
#           run on 2026-07-31. This regenerates it somewhere else, from a clone,
#           and diffs the rational against the banked one -- so the claim rests
#           on a reproduction rather than on a single machine's log line.
#
#           The cheap H=2..11 ladder runs first: if the operator or the state
#           enumeration has drifted at all, it shows there in three minutes
#           instead of twenty.
#
# TARGET    any box with a C++20 compiler. Single-threaded; ~2 GB peak at H=17
#           (6,536,381 states, 128-bit vector entries plus int32 successors).
#
# COMMAND   scripts/lambda_cert_reproduce.sh [outdir]
#
# COST      gympie 2026-07-31, for reference: H<=11 ladder 173 s summed, H=17
#           772.7 s. Budget half an hour and expect less.
#
# RESUME    None: each H is independent and re-running is cheap relative to
#           reasoning about a partial result. Kill it with the pid it prints.
#
# OUTPUT    $OUT/reproduced.log (receipts, same format as the banked log) and
#           $OUT/verdict.txt. Exit 0 only if every H reproduces its banked
#           num/den exactly.

set -u
cd "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT=${1:-runs/lambda-cert-reproduce}
BANKED=results/strip_mu_certificates.log
mkdir -p "$OUT"
LOG=$OUT/reproduced.log
VERDICT=$OUT/verdict.txt
: > "$LOG"
: > "$VERDICT"
echo "pid $$"

make build/strip_mu_cert || exit 1

# digits per H as the banked receipts were taken: 7 through H=14, then the
# denominator shrinks as the state count forces a wider vector. Reproducing at
# a DIFFERENT digit count would not compare against the banked rational.
run() {  # run H digits
    echo "=== H=$1 digits=$2 $(date -Is) ===" | tee -a "$VERDICT"
    ./build/strip_mu_cert "$1" "$1" --digits "$2" --log "$LOG" 2>&1 | tail -2
}
for H in $(seq 2 11); do run "$H" 7; done
run 17 3

# Compare each reproduced receipt against the last banked receipt for the same
# H and digit count. Fail closed: a missing banked row is a failure, not a skip.
python3 - "$BANKED" "$LOG" >> "$VERDICT" 2>&1 <<'PY'
import sys, re
def rows(path):
    out = {}
    for line in open(path):
        f = dict(kv.split("=", 1) for kv in line.split() if "=" in kv)
        if f.get("event") != "certificate":
            continue
        out[(f["H"], f["digits"])] = (f["num"], f["den"], f["result"])
    return out
banked, repro = rows(sys.argv[1]), rows(sys.argv[2])
bad = 0
for key in sorted(repro, key=lambda k: int(k[0])):
    got, want = repro[key], banked.get(key)
    H, digits = key
    if want is None:
        print(f"H={H} digits={digits}: NO BANKED RECEIPT to compare against")
        bad += 1
    elif got != want:
        print(f"H={H} digits={digits}: banked {want} reproduced {got}  MISMATCH")
        bad += 1
    elif got[2] != "PASS":
        print(f"H={H} digits={digits}: reproduced {got[0]}/{got[1]} but result={got[2]}")
        bad += 1
    else:
        print(f"H={H} digits={digits}: {got[0]}/{got[1]} PASS, matches banked")
print("VERDICT:", "REPRODUCED" if bad == 0 else f"{bad} FAILURE(S)")
sys.exit(1 if bad else 0)
PY
RC=$?
tail -3 "$VERDICT"
exit $RC
