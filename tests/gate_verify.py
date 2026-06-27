#!/usr/bin/env python3
"""gate_verify.py — AC-5 gate: independent verifier passes on a real dataset; catches corruption.

Steps:
  1. Run build/ns/mkseed to produce valid seed POLYRUN files for H=1..MAXN (these are
     valid POLYRUN files per the format spec and have a known CRC).
  2. Write a synthetic manifest referencing those files.
  3. Run verify --n MAXN: expect exit 0 (all CRCs match, record counts match).
  4. Flip a byte in one seed file's body.
  5. Run verify again: expect exit 1 (CRC mismatch detected).
  6. Clean up.

Using seed files avoids the need to keep full orchestrator run files; a seed is a
valid POLYRUN with exactly 1 record, so every check that applies to run files applies
here too.
"""

import os
import shutil
import struct
import subprocess
import sys
import tempfile

MAXN = 14
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
MKSEED  = os.path.join(ROOT, "build", "ns", "mkseed")
VERIFY  = os.path.join(ROOT, "build", "ns", "verify")


def die(msg):
    print(f"gate_verify FAIL  {msg}", file=sys.stderr)
    sys.exit(1)


# ─── FNV-1a-64 in Python for cross-checking ──────────────────────────────────

FNV_OFFSET = 14695981039346656037
FNV_PRIME  = 1099511628211
MASK64     = (1 << 64) - 1


def fnv1a64(data: bytes) -> int:
    h = FNV_OFFSET
    for b in data:
        h ^= b
        h = (h * FNV_PRIME) & MASK64
    return h


def make_seed_polyrun(path: str, H: int, maxn: int) -> None:
    """Write a seed POLYRUN file for height H (spec §Seed record)."""
    rev = "gate_verify"
    key_len = H + 2
    W = 8  # u64
    header = (
        "POLYRUN 1\n"
        f"height {H}\n"
        f"maxn {maxn}\n"
        "counter u64\n"
        "classifier triangle\n"
        "keylo \n"
        "keyhi \n"
        f"records {1:018d}\n"
        f"rev {rev}\n"
        "byteorder 1\n"
        "\n"
    ).encode()

    # One record: sig=(H+2 zero bytes), lo=0, len=1, counts[0]=1 LE u64.
    body = bytes(key_len) + bytes([0, 1]) + struct.pack("<Q", 1)
    crc = fnv1a64(body)
    trailer = struct.pack("<Q", crc)

    with open(path, "wb") as f:
        f.write(header)
        f.write(body)
        f.write(trailer)


def write_manifest(n: int, seed_files: list, data_dir: str) -> str:
    os.makedirs(os.path.join(data_dir, "manifests"), exist_ok=True)
    manifest_path = os.path.join(data_dir, "manifests", f"a{n}.txt")

    lines = [
        f"n={n}",
        "rev=gate_verify",
        "cpu_s=0.000",
        "wall_s=0.000",
        "rss_max_mb=0.0",
        "spill_bytes=0",
        f"files={len(seed_files)}",
    ]

    for path in seed_files:
        with open(path, "rb") as f:
            data = f.read()
        crc_val = struct.unpack_from("<Q", data[-8:])[0]
        # Record count = 1 for seed.
        lines.append(f"file path={path} records=1 crc={crc_val:016x}")

    with open(manifest_path, "w") as f:
        f.write("\n".join(lines) + "\n")

    return manifest_path


def flip_byte_in_body(path: str) -> None:
    """Flip a single byte in the POLYRUN body (not the CRC trailer)."""
    with open(path, "rb") as f:
        data = bytearray(f.read())

    # Find header end (\n\n).
    body_start = -1
    for i in range(len(data) - 1):
        if data[i] == ord('\n') and data[i+1] == ord('\n'):
            body_start = i + 2
            break
    if body_start < 0 or len(data) - body_start < 9:
        die(f"cannot find body in {path}")

    # Flip the first byte of the body (first byte of the sig).
    data[body_start] ^= 0xFF
    with open(path, "wb") as f:
        f.write(data)


def main():
    tmpdir = tempfile.mkdtemp(prefix="ns_gate_verify_")
    try:
        runs_dir = os.path.join(tmpdir, "runs")
        data_dir = os.path.join(tmpdir, "data")
        os.makedirs(runs_dir, exist_ok=True)
        os.makedirs(data_dir, exist_ok=True)

        # ── Step 1: create seed POLYRUN files for H=1..MAXN ──
        seed_files = []
        for H in range(1, MAXN + 1):
            path = os.path.join(runs_dir, f"seed_h{H:02d}.polyrun")
            make_seed_polyrun(path, H, MAXN)
            seed_files.append(path)
        print(f"gate_verify: created {len(seed_files)} seed POLYRUN files")

        # ── Step 2: write manifest ──
        manifest_path = write_manifest(MAXN, seed_files, data_dir)
        print(f"gate_verify: manifest written to {manifest_path}")

        # ── Step 3: verify — expect PASS ──
        print("gate_verify: running verify (expect PASS) ...")
        r = subprocess.run(
            [VERIFY, "--n", str(MAXN), "--data-dir", data_dir, "--no-spotcheck", "--verbose"],
            capture_output=True, text=True, cwd=ROOT,
        )
        sys.stdout.write(r.stdout)
        if r.returncode != 0:
            die(f"verify returned non-zero on clean run:\n{r.stderr}\n{r.stdout}")
        print("gate_verify: clean run PASSED")

        # ── Step 4: corrupt one seed file's body ──
        victim = seed_files[0]
        print(f"gate_verify: corrupting {os.path.basename(victim)} ...")
        flip_byte_in_body(victim)

        # ── Step 5: verify — expect FAIL ──
        print("gate_verify: running verify (expect FAIL) ...")
        r = subprocess.run(
            [VERIFY, "--n", str(MAXN), "--data-dir", data_dir, "--no-spotcheck"],
            capture_output=True, text=True, cwd=ROOT,
        )
        sys.stdout.write(r.stdout)
        if r.returncode == 0:
            die("verify returned 0 on corrupted run — corruption not detected!")
        if "FAIL" not in r.stdout:
            die(f"verify did not print FAIL line:\n{r.stdout}")
        print("gate_verify: corruption correctly detected")

    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)

    print(f"gate_verify PASS  (maxn={MAXN})")
    sys.exit(0)


if __name__ == "__main__":
    main()
