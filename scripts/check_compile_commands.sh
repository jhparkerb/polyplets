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
missing="$(python3 -c '
import glob, json, os
have = {os.path.relpath(e["file"]) for e in json.load(open("compile_commands.json"))}
want = set(glob.glob("worker/*.cpp") + glob.glob("test/*.cpp")
           + glob.glob("cpp/*.cpp") + glob.glob("cpp/*/*.cpp"))
for f in sorted(want - have):
    print(f)
')"
if [ -n "${missing}" ]; then
  echo "MISSING from compile_commands.json (clangd will fall back and misreport):"
  printf '%s\n' "${missing}" | sed 's/^/    /'
  echo "run: make compile-commands"
  exit 1
fi

fails=0
total=0
while IFS= read -r line; do
  total=$((total + 1))
  err="$(eval "${line} -fsyntax-only" 2>&1)" && continue
  fails=$((fails + 1))
  echo "FAIL: ${line}"
  printf '%s\n' "${err}" | head -20 | sed 's/^/    /'
done < <(python3 -c '
import json, shlex
for e in json.load(open("compile_commands.json")):
    print(" ".join(shlex.quote(a) for a in e["arguments"]))
')

echo "checked ${total} entries, ${fails} failed"
[ "${fails}" -eq 0 ]
