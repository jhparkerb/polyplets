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
# cpp/ is covered too, with the extra flags its Makefile rules pass: -Icpp (for
# cpp/obs.h and cpp/tma/*.h, included as "obs.h"/"tma/foo.h") and, for the three
# GMP translation units, the same -DPOLY_GMP plus MacPorts -isystem the Makefile
# auto-detects. Without those, clangd reported gmpxx.h as missing and cascaded
# fake "unknown type name 'mpz_class'" through every use.
#
# test/ and worker/ get the zstd flags for the same reason: without -DPOLY_ZSTD
# the POLY_ZSTD-guarded call sites in test/gate_runfile.cpp vanish and its
# helpers read as -Wunused-function errors under the -Werror this DB mirrors.
#
# GMP and zstd are both detected per host exactly as the Makefile does it
# (Darwin: MacPorts /opt/local; else /usr/include). If a dev header is absent
# its flags are omitted, matching a build where that feature is skipped.
#
# scripts/check_compile_commands.sh proves the result: every entry here must
# survive a real -fsyntax-only compile with exactly these flags.
#
# The output carries absolute, host-specific paths, so it is git-ignored and
# regenerated per host (run `make compile-commands` after adding/removing a .cpp).
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
cd "$root"

python3 - "$root" <<'PY'
import glob, json, platform, os, sys
root = sys.argv[1]
args = ["c++", "-std=c++20", "-Wall", "-Wextra", "-Werror",
        '-DGIT_REV="dev"', '-DBUILD_TIME="dev"', "-I."]

# Mirror the Makefile's GMP auto-detection, including the -isystem (not -I):
# gmpxx.h itself trips -Wdeprecated-literal-operator under -Werror.
darwin = platform.system() == "Darwin"
if darwin:
    gmp_hdr, gmp_flags = "/opt/local/include/gmpxx.h", ["-DPOLY_GMP", "-isystem", "/opt/local/include"]
    zstd_hdr, zstd_flags = "/opt/local/include/zstd.h", ["-DPOLY_ZSTD", "-I/opt/local/include"]
else:
    gmp_hdr, gmp_flags = "/usr/include/gmpxx.h", ["-DPOLY_GMP"]
    zstd_hdr, zstd_flags = "/usr/include/zstd.h", ["-DPOLY_ZSTD"]
if not os.path.exists(gmp_hdr):
    gmp_flags = []
if not os.path.exists(zstd_hdr):
    zstd_flags = []

def flags_for(f):
    if not f.startswith("cpp/"):
        return args + zstd_flags
    extra = ["-Icpp"]
    with open(f) as fh:
        src = fh.read()
    if "gmpxx.h" in src:
        extra += gmp_flags
    # cpp/strip_mu.cpp carries `#pragma omp` but its Makefile rule passes no
    # -fopenmp, so the real build ignores those pragmas -- and mirroring the
    # real build is this DB's whole contract. clang says nothing; gcc raises
    # -Werror=unknown-pragmas and fails the check on a file that builds fine.
    if "#pragma omp" in src:
        extra += ["-Wno-unknown-pragmas"]
    return args + extra

sources = sorted(f for pat in open("scripts/compile_db_sources.txt")
                 if pat.strip() and not pat.startswith("#")
                 for f in glob.glob(pat.strip()))
entries = [
    {"directory": root, "arguments": flags_for(f) + [f], "file": f"{root}/{f}"}
    for f in sources
]
# Write-then-rename, NOT in place. gate-compile-db regenerates on every `make`,
# and clangd watches this file: an in-place json.dump leaves it truncated for the
# duration of the write, clangd re-reads it mid-rewrite, finds no entry for the
# open file, falls back to .clangd's defaults and reports exactly the phantom
# "gmpxx.h not found" / "unknown type name 'mpz_class'" errors this DB exists to
# prevent. os.replace is atomic within a filesystem, so clangd sees old or new,
# never half. The temp file is a sibling to keep the rename on one filesystem.
tmp = "compile_commands.json.tmp"
with open(tmp, "w") as out:
    json.dump(entries, out, indent=2)
    out.write("\n")
os.replace(tmp, "compile_commands.json")
print(f"wrote compile_commands.json ({len(entries)} entries)")
PY
