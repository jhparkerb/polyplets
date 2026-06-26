#!/usr/bin/env bash
# h19_after_h20.sh <H20-pid> -- wait for the running a(21) H20 pole to finish, THEN launch
# H19 (resume from its checkpoint) solo on the freed RAM. Durable: runs in a dalby tmux
# window and blocks on `tail --pid` (the approved wait, NOT a poll), so it survives ssh
# drops and a dead control session. The actuator lives on the box.
#
# WHY sequential: two heavy heights OOM'd dalby (ram_guard fired 2026-06-26T03:23, dropped
# H19, kept the H20 pole). H20 solo fits; then H19 solo fits -- but not both at once. H19's
# checkpoint was written on dalby (aarch64), so this is a SAME-ARCH resume (no cross-arch
# gamble). It resumes with the on-disk build/tma, which is the unchanged 0f48081 binary that
# wrote the checkpoint -- do NOT `make` (rebuild -> 8b869c9 -> checkpoint-incompatible).
# Resume picks up from ckpt_h19 (last write 2026-06-25T21:40; progress since is replayed).
#
# USAGE (dalby, in tmux session 0 as a new window):  scripts/h19_after_h20.sh 30478
set -u
cd "$(dirname "$0")/.."
H20PID="${1:?usage: h19_after_h20.sh <H20-pid>}"
DIR="runs/a21fold"
echo $$ > "$DIR/h19_waiter.pid"
echo "$(date -Is) waiting on H20 pid $H20PID; will launch H19 resume when it exits..."
tail -f /dev/null --pid "$H20PID"        # blocks until H20 exits (approved wait, not a poll)
echo "$(date -Is) H20 pid $H20PID exited. free=$(free -g | awk '/^Mem:/{print $7}')GB. H20 result:"
awk '$1==21{print "  B_20(21)="$2}' "$DIR/h20.out" 2>/dev/null || echo "  (h20.out has no n=21 row -- H20 may have been killed, not completed)"
echo "$(date -Is) launching H19 resume (threads=40, --fold, resume ckpt_h19) ..."
build/tma square8 21 --only-height 19 --threads 40 --fold \
  --checkpoint "$DIR/ckpt_h19" >> "$DIR/h19.out" 2>> "$DIR/h19.log"
rc=$?
echo "$(date -Is) H19 exited rc=$rc  B_19(21)=$(awk '$1==21{print $2}' "$DIR/h19.out" 2>/dev/null)"
echo "$(date -Is) NOTE: H18 and H17 still un-run (driver was killed by the guard). Launch them next."
