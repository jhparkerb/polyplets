# dir4_perim_lib.sh -- shared setup for the Phase 2b dir4-semiperimeter sweeps.
#
# Sourced, not executed. Every scripts/dir4_perim_*.sh used to carry its own
# copy of the paths, the null-control cut and a bare `prec_guess ... 2>/dev/null`
# call. Three things went wrong with that:
#
#   * the "re-cut, never reuse a stale copy" invariant was stated five times and
#     could rot in four of them independently;
#   * the shells' cut was guarded by nothing but `[ -f "$SRC" ]`, while
#     tests/gate_dir4_perim_alg.py's cut_null_control() -- the definition of what
#     the control IS -- also checks length, digit-ness and the banked 14-term
#     prefix. A source regenerated with the wrong adjacency sailed through the
#     shells and produced logs the write-ups cite;
#   * 2>/dev/null plus `case $out in CANDIDATE*)` turned a missing terms file
#     into "no candidate anywhere", indistinguishable from a real negative
#     across an entire scan.
#
# So: one cut, checked the way the gate checks it, and one runner that refuses
# an exit code that is not a verdict.

G=build/prec_guess
DIR4=results/mk_dir4_perim_terms_s200.txt
HV=results/convex_perim_terms_s200.txt
NULL=build/dir4_perim_null199.txt
SRC=results/convex_area_terms_n700_king.txt   # the null control's real source

# The first 14 terms of HV-convex king animals by area
# (docs/middle-kingdom-plan.md reference table). Same constant as
# tests/gate_dir4_perim_alg.py's KING14.
KING14=1,4,16,61,221,766,2566,8390,26982,85834,271174,853111,2677214,8389720

# Re-cut the 199-term null control from the by-area king series, every run.
# The control is only a control if it IS that series, so the source is checked
# to exist, to be long enough, to be all digits, and to start with the banked
# prefix. Nothing derived is kept in results/, and a missing or altered source
# stops the script rather than falling back to a previously cut file.
cut_null_control() {
  [ -f "$SRC" ] || {
    echo "missing null-control source $SRC (results/convex-polyplets.md)" >&2
    exit 1
  }
  local n got
  n=$(grep -cv '^[[:space:]]*\(#\|$\)' "$SRC")
  [ "$n" -ge 199 ] || {
    echo "null-control source $SRC has $n terms, need >= 199" >&2; exit 1
  }
  got=$(grep -v '^[[:space:]]*\(#\|$\)' "$SRC" | head -14 | awk '{print $NF}' \
        | paste -sd, -)
  [ "$got" = "$KING14" ] || {
    echo "null-control source $SRC does not start with the banked king prefix" >&2
    echo "  want: $KING14" >&2
    echo "  got:  $got" >&2
    exit 1
  }
  grep -v '^[[:space:]]*\(#\|$\)' "$SRC" | head -199 > "$NULL"
  awk 'NF && $NF !~ /^[0-9]+$/ {print "non-numeric term at line "NR": "$0 > "/dev/stderr"; exit 1}' \
    "$NULL" || exit 1
}

# guess <mode> <file> <J> <D> [prime] -- run prec_guess and echo its stdout.
# prec_guess signals its verdict in the exit code too: 0 EXCLUDED, 2
# INCONCLUSIVE, 3 CANDIDATE. Anything else (missing file, refused argument) is
# a failure, not a verdict, and stops the script instead of being read as one.
guess() {
  local mode=$1 file=$2 out rc
  shift 2
  out=$("$G" "$mode" "$file" "$@" 2>/dev/null)
  rc=$?
  case $rc in
    0|2|3) printf '%s\n' "$out" ;;
    *) echo "prec_guess $mode $file $* failed: rc=$rc" >&2
       "$G" "$mode" "$file" "$@" >/dev/null   # rerun with stderr visible
       exit 1 ;;
  esac
}
