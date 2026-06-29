#!/usr/bin/env bash
# Generate compile_commands.json for clangd.
#
# Without a compilation database, clangd has no include path and analyzes each
# header standalone — producing phantom "core/run.h not found" errors that
# cascade into fake "undeclared identifier" (u64/Sig/RunRecord/SIGMAX). With this
# DB, clangd resolves the project's "core/foo.h" includes and analyzes every
# header in the context of a real translation unit that includes it.
#
# The argument list MIRRORS the Makefile's NSFLAGS (incl. -DGIT_REV/-DBUILD_TIME,
# which make injects per build) so clangd matches the real compile exactly — a
# missing define would itself read as a phantom "undeclared identifier". Static
# placeholder values are fine: clangd only needs the macros DEFINED.
#
# The output carries absolute, host-specific paths, so it is git-ignored and
# regenerated per host (run `make compile-commands` after adding/removing a .cpp).
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
cd "$root"

python3 - "$root" <<'PY'
import glob, json, sys
root = sys.argv[1]
args = ["c++", "-std=c++20", "-Wall", "-Wextra", "-Werror",
        '-DGIT_REV="dev"', '-DBUILD_TIME="dev"', "-I."]
entries = [
    {"directory": root, "arguments": args + [f], "file": f"{root}/{f}"}
    for f in sorted(glob.glob("worker/*.cpp") + glob.glob("test/*.cpp"))
]
with open("compile_commands.json", "w") as out:
    json.dump(entries, out, indent=2)
    out.write("\n")
print(f"wrote compile_commands.json ({len(entries)} entries)")
PY
