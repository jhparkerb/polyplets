#!/usr/bin/env bash
# ---------------------------------------------------------------------------
#  scripts/check_receipts.sh — the receipt gate for the rook-parity campaign.
#
#  docs/rook-parity-team-process.md control #3.  The measured failure it exists
#  to stop: across round 4 of the triangle campaign every status drift had the
#  same sign -- an instrument that was WRITTEN, UNRUN got described as one that
#  had run (results/r4/INSTRUMENTS.md:4-8).  A drift with a sign is a bias, and
#  the rule that ended it on contact was "no log path in the table means the
#  instrument is unrun, and no brief may describe it otherwise".  That rule was
#  disciplinary; this makes it mechanical.
#
#      scripts/check_receipts.sh              # scan the default scope
#      scripts/check_receipts.sh FILE...      # scan named files
#      scripts/check_receipts.sh --self-test  # RED first: the planted claim
#
#  THE RULE.  In a status position -- a markdown table row, or a line whose
#  first field is `status:` -- the tokens PROVED VERIFIED GREEN RUN CONFIRMED
#  PASSED MATCHED are claims that something executed, and each needs a receipt
#  on the same line: a path that exists in this working tree, is non-empty, and
#  is INSIDE the repo.  In-tree is half the point: the campaign's largest result
#  sat only on dalby for two days (triangle-postmortem.md:259-264), so a path
#  that resolves outside the repo root is a violation, not a receipt.
#
#  WHAT IT DOES NOT DO.  It proves a receipt exists.  It does not read the
#  receipt, and a green log from a gate that never ran red is not evidence --
#  the lean2 battery's gate E read a correct output as zero sorries because of
#  an ASCII-vs-backtick pattern (triangle-postmortem.md:329-338).  Reading the
#  receipt is the numbers adversary's job.  This gate exists so that the
#  adversary spends its pass reading logs instead of hunting for their absence.
#
#  ESCAPE HATCH, deliberately narrow: a line carrying `status-quote:` is exempt,
#  for quoting history ("round 3 reported GREEN here").  It is a visible token
#  in the file, so a lane that waives the gate has to write the waiver down.
#
#  RED FIRST.  --self-test asserts that tests/fixtures/receipts/mutant.md -- a
#  deliverable claiming RUN with no log -- FAILS, and that clean.md passes.  A
#  gate that has never rejected a planted claim is not a gate; the self-test
#  runs first on every invocation of the make target and its failure is the
#  gate's failure.
# ---------------------------------------------------------------------------
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FIXTURES="$ROOT/tests/fixtures/receipts"

# Default scope: the round's deliverables and the round's brief.  Scope is
# narrow on purpose -- prose elsewhere in the repo says GREEN about history.
default_scope() {
	local f
	for f in "$ROOT"/results/rook*/*.md "$ROOT"/results/rook*/**/*.md \
	         "$ROOT"/docs/rook*-brief.md; do
		[ -f "$f" ] && printf '%s\n' "$f"
	done
}

# Emits one record per status-position line:
#   NORECEIPT <lineno> <text>        no path-shaped token on the line
#   PATH      <lineno> <path>        candidate receipt to validate
scan_file() {
	awk '
	function isword(s, i, j,   before, after) {
		before = (i == 1) ? "" : substr(s, i - 1, 1)
		after  = substr(s, i + j, 1)
		return (before !~ /[A-Za-z0-9_]/ && after !~ /[A-Za-z0-9_]/)
	}
	{
		if (index($0, "status-quote:") > 0) next
		if ($0 !~ /^[[:space:]]*\|/ && $0 !~ /^[[:space:]]*[Ss]tatus:/) next

		claim = 0
		n = split("PROVED VERIFIED GREEN RUN CONFIRMED PASSED MATCHED", tok, " ")
		for (t = 1; t <= n; t++) {
			rest = $0; off = 0
			while (match(rest, tok[t])) {
				pos = off + RSTART
				if (isword($0, pos, length(tok[t]))) { claim = 1; break }
				off = pos + RLENGTH - 1
				rest = substr(rest, RSTART + RLENGTH)
			}
			if (claim) break
		}
		if (!claim) next

		rest = $0; found = 0
		while (match(rest, /\/?[A-Za-z0-9_][A-Za-z0-9_.\/-]*\.(log|txt|json|csv|tsv|out|md|py|sh|lean)/)) {
			p = substr(rest, RSTART, RLENGTH)
			print "PATH\t" NR "\t" p
			found = 1
			rest = substr(rest, RSTART + RLENGTH)
		}
		if (!found) print "NORECEIPT\t" NR "\t" $0
	}' "$1"
}

check_file() {
	local file="$1" rel bad=0 kind lineno payload abs
	rel="${file#"$ROOT"/}"
	while IFS=$'\t' read -r kind lineno payload; do
		case "$kind" in
		NORECEIPT)
			printf 'RECEIPT MISSING  %s:%s\n    %s\n' "$rel" "$lineno" "$payload"
			bad=1
			;;
		PATH)
			# Out-of-tree is decided on the path itself, not on whether the
			# file happens to be here: a receipt naming another box is a
			# violation on gympie and on dalby alike.
			if [ "${payload#/}" != "$payload" ] && [ "${payload#"$ROOT"/}" = "$payload" ]; then
				printf 'RECEIPT OUT OF TREE  %s:%s  %s\n' "$rel" "$lineno" "$payload"
				bad=1
				continue
			fi
			case "$payload" in
			/*) abs="$payload" ;;
			*)  abs="$ROOT/$payload"
			    [ -e "$abs" ] || abs="$(dirname "$file")/$payload" ;;
			esac
			abs="$(cd "$(dirname "$abs")" 2>/dev/null && pwd)/$(basename "$abs")" || abs=""
			if [ -z "$abs" ] || [ ! -f "$abs" ]; then
				printf 'RECEIPT ABSENT   %s:%s  %s\n' "$rel" "$lineno" "$payload"
				bad=1
			elif [ ! -s "$abs" ]; then
				printf 'RECEIPT EMPTY    %s:%s  %s\n' "$rel" "$lineno" "$payload"
				bad=1
			elif [ "${abs#"$ROOT"/}" = "$abs" ]; then
				printf 'RECEIPT OUT OF TREE  %s:%s  %s\n' "$rel" "$lineno" "$payload"
				bad=1
			fi
			;;
		esac
	done < <(scan_file "$file")
	return $bad
}

self_test() {
	local rc=0 m
	# Three planted claims, one per way a receipt can fail to be one: absent
	# entirely, naming a file that is not there, and naming a path on another
	# box.  All three were real events in the triangle campaign.
	for m in mutant-noreceipt mutant-absent mutant-remote; do
		if [ ! -f "$FIXTURES/$m.md" ]; then
			echo "SELF-TEST FAILED: fixture $m.md missing under tests/fixtures/receipts" >&2
			return 1
		fi
		if check_file "$FIXTURES/$m.md" >/dev/null 2>&1; then
			echo "SELF-TEST FAILED: the planted claim in $m.md PASSED the gate" >&2
			rc=1
		fi
	done
	if [ ! -f "$FIXTURES/clean.md" ]; then
		echo "SELF-TEST FAILED: fixtures missing under tests/fixtures/receipts" >&2
		return 1
	fi
	if ! check_file "$FIXTURES/clean.md"; then
		echo "SELF-TEST FAILED: clean.md, which carries real receipts, was rejected" >&2
		rc=1
	fi
	[ $rc -eq 0 ] && echo "self-test OK: planted claim rejected, clean deliverable accepted"
	return $rc
}

main() {
	local files=() f rc=0 n=0
	if [ "${1:-}" = "--self-test" ]; then
		self_test
		exit $?
	fi
	self_test || exit 1

	if [ $# -gt 0 ]; then
		files=("$@")
	else
		while IFS= read -r f; do files+=("$f"); done < <(default_scope)
	fi

	if [ ${#files[@]} -eq 0 ]; then
		echo "receipts gate: no files in scope yet (results/rook*/, docs/rook*-brief.md)"
		exit 0
	fi

	for f in "${files[@]}"; do
		[ -f "$f" ] || { echo "receipts gate: not a file: $f" >&2; exit 1; }
		check_file "$f" || rc=1
		n=$((n + 1))
	done

	if [ $rc -ne 0 ]; then
		echo "receipts gate RED: a status claim above has no in-tree receipt." >&2
		exit 1
	fi
	echo "receipts gate green: $n file(s), every status claim carries an in-tree receipt"
}

main "$@"
