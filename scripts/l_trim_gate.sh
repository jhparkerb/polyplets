#!/usr/bin/env bash
# ---------------------------------------------------------------------------
#  scripts/l_trim_gate.sh — the commit gate for the L-paper trim campaign.
#
#  docs/reviews/l-trim/PROTOCOL.md is the campaign.  This is the thing that
#  stands between a phase and a commit.  Nothing lands unless every check here
#  is green, and every check is fail-closed: a check that cannot run is a
#  failure, not a skip.
#
#      scripts/l_trim_gate.sh baseline     # record the pre-campaign metrics
#      scripts/l_trim_gate.sh check N      # gate phase N against baseline
#
#  The five checks, in the order a breakage is cheapest to diagnose:
#
#    1. compile      every L paper builds, three passes, -halt-on-error
#    2. references   no "undefined" reference or citation appears in any log,
#                    which is how a cut \label or a cut \bibitem shows up
#    3. verify       paper/verify_l_papers.py, all checks, RED controls firing
#    4. monotone     no paper is longer in words than it was at baseline
#    5. untouched    technical-report.tex, polyplets-report.tex and shared/
#                    are byte-identical to baseline
#
#  Check 5 exists because the campaign's blast radius is six files and the
#  ledger.  technical-report.tex is jasonp's prose and is read-only to the
#  machine; shared/disclosure.tex carries the verification ledgers that the
#  whole authorship split rests on.  A trim agent reaching either of those is
#  a bug, and this is where it stops.
# ---------------------------------------------------------------------------
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PAPER="$ROOT/paper"
LEDGER="$ROOT/docs/reviews/l-trim"
BASELINE="$LEDGER/baseline.tsv"

L_PAPERS=(
  L1-diagonal-law
  L2-ternary-spine
  L3-lambda-bounds
  L4-not-dfinite
  L5-convex-king-animals
  L6-perimeter-gradings
)

# Files the campaign must not touch, and the reason each is on the list.
FROZEN=(
  paper/technical-report.tex
  paper/polyplets-report.tex
  paper/shared/disclosure.tex
  paper/shared/preamble.tex
  paper/shared/refs.bib
  paper/verify_l_papers.py
)

fail=0
say()  { printf '  %-12s %s\n' "$1" "$2"; }
bad()  { printf '  %-12s %s\n' "FAIL" "$*"; fail=1; }

# --- baseline ---------------------------------------------------------------
if [[ "${1:-}" == "baseline" ]]; then
  mkdir -p "$LEDGER"
  : > "$BASELINE"
  for p in "${L_PAPERS[@]}"; do
    printf 'words\t%s\t%s\n' "$p" "$(wc -w < "$PAPER/$p.tex" | tr -d ' ')" >> "$BASELINE"
  done
  for f in "${FROZEN[@]}"; do
    [[ -e "$ROOT/$f" ]] || { echo "l_trim_gate: frozen file missing: $f" >&2; exit 1; }
    printf 'sha\t%s\t%s\n' "$f" "$(shasum -a 256 "$ROOT/$f" | cut -d' ' -f1)" >> "$BASELINE"
  done
  echo "l_trim_gate: baseline written to ${BASELINE#$ROOT/}"
  exit 0
fi

if [[ "${1:-}" != "check" ]]; then
  echo "usage: $0 {baseline|check [phase]}" >&2
  exit 2
fi
phase="${2:-?}"

[[ -s "$BASELINE" ]] || { echo "l_trim_gate: no baseline; run '$0 baseline' first" >&2; exit 1; }

echo "l_trim_gate: phase $phase"

# --- 1. compile -------------------------------------------------------------
for p in "${L_PAPERS[@]}"; do
  if make -C "$PAPER" "$p.pdf" >/dev/null 2>&1; then
    say "compile" "$p"
  else
    bad "compile $p — rerun: make -C paper $p.pdf"
  fi
done

# --- 2. references ----------------------------------------------------------
# pdflatex does not exit nonzero on an undefined \ref or \cite, so -halt-on-error
# cannot see them.  A cut that removes a \label still referenced, or a \cite whose
# bibitem went with it, lands here and nowhere else.
for p in "${L_PAPERS[@]}"; do
  log="$PAPER/$p.log"
  if [[ ! -f "$log" ]]; then
    bad "references $p — no log, compile did not run"
    continue
  fi
  undef=$(grep -c 'undefined' "$log" 2>/dev/null || true)
  if [[ "$undef" -gt 0 ]]; then
    bad "references $p — $undef undefined ref/cite:"
    grep -n 'undefined' "$log" | head -5 | sed 's/^/                 /'
  else
    say "references" "$p"
  fi
done

# --- 3. verify --------------------------------------------------------------
if out=$(cd "$ROOT" && python3 paper/verify_l_papers.py 2>&1); then
  say "verify" "$(echo "$out" | tail -1)"
else
  bad "verify — paper/verify_l_papers.py:"
  echo "$out" | tail -15 | sed 's/^/                 /'
fi

# --- 4. monotone ------------------------------------------------------------
# "In no case shall the document get larger except temporarily."  Temporarily
# means within a phase; at a commit boundary every paper is at or below where
# it started.
while IFS=$'\t' read -r kind key val; do
  [[ "$kind" == "words" ]] || continue
  now=$(wc -w < "$PAPER/$key.tex" | tr -d ' ')
  if (( now > val )); then
    bad "monotone $key — grew ${val} -> ${now} words"
  else
    pct=$(python3 -c "print(f'{100*(1-$now/$val):.1f}')")
    say "monotone" "$(printf '%-24s %5d -> %5d words  (-%s%%)' "$key" "$val" "$now" "$pct")"
  fi
done < "$BASELINE"

# --- 5. untouched -----------------------------------------------------------
while IFS=$'\t' read -r kind key val; do
  [[ "$kind" == "sha" ]] || continue
  if [[ ! -e "$ROOT/$key" ]]; then
    bad "untouched $key — DELETED"
    continue
  fi
  now=$(shasum -a 256 "$ROOT/$key" | cut -d' ' -f1)
  if [[ "$now" != "$val" ]]; then
    bad "untouched $key — MODIFIED, and it is out of scope"
  else
    say "untouched" "$key"
  fi
done < "$BASELINE"

echo
if (( fail )); then
  echo "l_trim_gate: PHASE $phase BLOCKED — do not commit"
  exit 1
fi
echo "l_trim_gate: phase $phase clear to commit"
