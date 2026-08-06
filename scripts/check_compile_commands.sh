#!/usr/bin/env bash
# Verify compile_commands.json is honest: every entry must survive a real
# -fsyntax-only compile with exactly the flags recorded for it.
#
# Why this exists: the database is what clangd believes, and a wrong entry is
# invisible in `make` (which uses the Makefile's own flags) while producing
# phantom editor errors -- the failure this script was written after was
# cpp/*.cpp missing from the DB entirely, so clangd fell back to the .clangd
# defaults, could not find <gmpxx.h> or "obs.h", and cascaded fake
# "unknown type name 'mpz_class'" through every use.
#
# Syntax-only, so it is seconds, not a build. Non-zero exit on any failure.
set -uo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
cd "$root"

if [ ! -f compile_commands.json ]; then
  echo "compile_commands.json absent -- run: make compile-commands" >&2
  exit 1
fi

# Completeness first. This is the half that matters most: a source MISSING from
# the DB is exactly the original bug, and the per-entry compile below cannot see
# it -- an absent entry has nothing to fail.
# The glob list is scripts/compile_db_sources.txt -- the SAME file the generator
# reads. Spelled out separately here, a source directory added to the generator
# alone would leave this want-set blind to it and the check would pass vacuously.
missing="$(python3 -c '
import glob, json, os
have = {os.path.relpath(e["file"]) for e in json.load(open("compile_commands.json"))}
want = {f for pat in open("scripts/compile_db_sources.txt")
        if pat.strip() and not pat.startswith("#")
        for f in glob.glob(pat.strip())}
for f in sorted(want - have):
    print(f)
')"
if [ -n "${missing}" ]; then
  echo "MISSING from compile_commands.json (clangd will fall back and misreport):"
  printf '%s\n' "${missing}" | sed 's/^/    /'
  echo "run: make compile-commands"
  exit 1
fi

# The per-entry compiles are fully independent, and this gate is in `gates`,
# which is the default goal -- so it runs on every bare `make`. Serially the 34
# entries measured 10.9 s; fanned out over the box's cores it is ~2 s. Each job
# emits its whole failure block in one printf so parallel output stays readable.
jobs="$( (command -v nproc >/dev/null && nproc) \
         || sysctl -n hw.ncpu 2>/dev/null || echo 4)"
total="$(python3 -c '
import json; print(len(json.load(open("compile_commands.json"))))')"

python3 -c '
import json, shlex
for e in json.load(open("compile_commands.json")):
    print(" ".join(shlex.quote(a) for a in e["arguments"]), end="\0")
' | xargs -0 -P "${jobs}" -n1 bash -c '
  err="$(eval "$0 -fsyntax-only" 2>&1)" && exit 0
  printf "FAIL: %s\n%s\n" "$0" "$(printf "%s\n" "$err" | head -20 | sed "s/^/    /")"
  exit 1'
rc=$?

if [ "${rc}" -eq 0 ]; then
  echo "checked ${total} entries, 0 failed"
else
  echo "checked ${total} entries, at least one failed (see FAIL above)"
fi
[ "${rc}" -eq 0 ]
