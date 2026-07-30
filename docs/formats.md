# Polyomino system data formats

## POLYRUN run file

A POLYRUN file is a sorted run of state-count records produced by a map or merge worker.
It has a text header, a binary body, and an 8-byte CRC trailer.

### Header

The header is a sequence of `key value\n` lines followed by a single blank line (`\n`).
All lines use ASCII; values are separated from the key by a single space.

| Field        | Type      | Example value              | Meaning |
|--------------|-----------|----------------------------|---------|
| `POLYRUN`    | literal   | `1`                        | Magic word + version; must appear first |
| `height`     | decimal   | `5`                        | Strip height H (number of boundary rows) |
| `maxn`       | decimal   | `21`                       | Maximum polyomino size tracked |
| `counter`    | string    | `u64`                      | Width of each count word: `u64` (8 bytes) or `u128` (16 bytes) |
| `classifier` | string    | `triangle`                 | Output type; `triangle` is the only value in v1 |
| `keylo`      | hex or empty | `0000000000000` or `` | Lower bound of key range (inclusive). Empty = start of key space |
| `keyhi`      | hex or empty | `ff000000000000` or `` | Upper bound of key range (exclusive). Empty = end of key space |
| `records`    | decimal   | `000000000000012345`       | 18-digit zero-padded count of binary records in the body |
| `rev`        | string    | `abc1234` or `unknown`     | Git commit hash of the build that wrote the file |
| `byteorder`  | decimal   | `1`                        | Byte order of count words: `1` = little-endian |

Field order in the file is exactly as listed above.
The blank line terminator (a lone `\n`) ends the header; the binary body begins immediately after.

`keylo` and `keyhi` are hex-encoded sig bytes of length `(H+2)*2` hex characters when present.
An empty value (just the key name, a space, then `\n`) means start-of-keyspace for `keylo` or end-of-keyspace for `keyhi`.
The key range is half-open: `[keylo, keyhi)`.

Example header for H=4, maxn=14, u64 counter, empty key range (full sweep):

```
POLYRUN 1
height 4
maxn 14
counter u64
classifier triangle
keylo 
keyhi 
records 000000000000004711
rev abc1234
byteorder 1

```

### Binary body

The body is a sequence of `records` records packed end-to-end with no padding or separators.
Each record has three parts:

```
sig[H+2 bytes] | lo[1 byte] | len[1 byte] | counts[len * W bytes, LE]
```

Where W = 8 for `u64`, 16 for `u128`.

**sig** (`H+2` bytes): the canonical boundary signature.

- `sig[0..H-1]`: component labels for each boundary row.
  - `0` = row is empty (no occupied cell on the current boundary column).
  - `1..254` = row belongs to the named connected component, in first-occurrence order top-to-bottom.
  Labels are canonical: the first label encountered scanning row 0 downward is 1, the next distinct one is 2, and so on.
- `sig[H]`: touch-top flag. Nonzero if any occupied cell has ever reached row 0.
- `sig[H+1]`: touch-bottom flag. Nonzero if any occupied cell has ever reached row H-1.

**lo** (`u8`): index of the first nonzero entry in the count vector. Valid range 0–255 (in practice 0 ≤ lo ≤ maxn).

**len** (`u8`): number of entries in the count vector. `len = 0` means no counts (unused; never written). Valid range 0–255.

**counts** (`len * W` bytes, little-endian): the count vector over a contiguous window of polyomino sizes.
`counts[i]` is the number of partial animals of size `lo + i` that produce this boundary signature.
Sizes outside `[lo, lo+len)` are implicitly zero.
Each `u64` value occupies 8 bytes LE; each `u128` value occupies 16 bytes LE (low 8 bytes then high 8 bytes).

### Sort order

Records are sorted in ascending `memcmp` order over the `H+2` sig bytes.
All bytes of sig participate; no sub-field is primary.

### CRC trailer

The last 8 bytes of the file are a FNV-1a-64 checksum of all binary body bytes
(every byte from the first sig byte through the last count byte; the header and
the CRC bytes themselves are excluded).

FNV-1a-64 algorithm:

```
hash = 14695981039346656037   (offset basis)
for each byte b in body:
    hash = hash XOR b
    hash = hash * 1099511628211 (mod 2^64)
```

The 8-byte trailer is `hash` in little-endian order.

A reader must verify the CRC after consuming all records. A mismatch indicates data corruption.

### Seed record

The seed POLYRUN for a height-H sweep has exactly one record:
all-zero sig, lo=0, len=1, counts[0]=1. It represents one partial animal of size 0
with an empty boundary (the start of column 0).

---

## POLYCKPT checkpoint file

A POLYCKPT file is a plain text file written atomically (write to temp, rename) after
each completed column. It captures enough state to resume a height sweep.

Format: one directive per line, no blank-line terminator.

| Line prefix | Format | Meaning |
|-------------|--------|---------|
| `POLYCKPT 2` | literal | Magic word + version; must be the first line |
| `H` | `H <decimal>` | Strip height being computed (`-1` in the overlap form) |
| `col` | `col <decimal>` | Index of the last COMPLETED column; `-1` means none yet |
| `config` | `config maxn=<d> counter=<u64\|u128> fold=<bool> kernel=<column\|kink> maxdiagk=<d> overlap=<d>` | Run config stamped at write time; resume hard-fails on a mismatch. `maxdiagk` and `overlap` were added by AUDIT-2026-07-30 O3/O4 — a config line without them is a pre-stamp checkpoint (resume then allows only the default cap, and infers the mode from whether a `done` line is present) |
| `frontier` | `frontier <path> [<path>...]` | Space-separated paths to current frontier POLYRUN files |
| `done` | `done <H> [<H>...]` | OVERLAP form only: the SET of fully-completed heights (heights finish out of order, so a single H/col cannot express progress). When present, `H`/`col`/`frontier` are unused |
| `acct` | `acct cpu_s=<float> wall_s=<float> rss_max_mb=<float>` | Accumulated resource usage to date |
| `tri` | `tri <n> <value>` | One triangle entry: size n, count value (decimal, arbitrary width). Only nonzero entries are written. Zero or more of these lines appear, in no specified order. |
| `htri` | `htri <n> <value>` | The CURRENT height's partial per-height row alone (same sparse encoding as `tri`). Version 2 only |

**Version history.** Version 1 had no `htri`. Resume from a version-1 checkpoint
therefore cannot reconstruct a whole per-height row, so a mid-height resume with
`--per-height-out` is refused outright (AUDIT-2026-07-30 O2); a version-1
checkpoint at `col=-1` or at a completed height (empty `frontier`) still resumes.
The version is stamped rather than inferred from the presence of `htri` lines,
because the row is sparse-encoded — a legitimately all-zero partial row from a
version-2 writer is byte-identical to a version-1 ledger.

`frontier` paths may contain spaces in principle, but in practice paths are chosen to be space-free.
If the value after `frontier ` is empty the frontier is empty.

`acct` fields:
- `cpu_s`: sum of CPU-seconds across all workers since job start (float, 6 decimal places).
- `wall_s`: sum of wall-clock seconds (float, 6 decimal places).
- `rss_max_mb`: peak RSS in megabytes across all workers (float, 3 decimal places); fold rule is MAX, not sum.

`tri` entries accumulate `Σ_H T(n,H)` contributions from all completed heights before this one, plus
contributions from completed columns within the current height H.

Example:

```
POLYCKPT 2
H 5
col 3
config maxn=6 counter=u64 fold=true kernel=kink maxdiagk=-1 overlap=1
frontier /data/runs/run_col3_a.polyrun /data/runs/run_col3_b.polyrun
acct cpu_s=142.831000 wall_s=38.201000 rss_max_mb=1024.000
tri 4 4
tri 5 12
tri 6 23
htri 5 7
htri 6 11
```

---

## Triangle output

Workers emit triangle contributions to stdout as they complete. The orchestrator accumulates them.

Format: one line per (H, n) pair:

```
tri <H> <n> <value>
```

- `H`: strip height (decimal integer).
- `n`: polyomino size (decimal integer).
- `value`: count as a decimal integer (u64 range).

Multiple `tri` lines with the same `(H, n)` from different workers are summed.
A complete a(n) result requires summing `tri H n` over all H from 1 to n.

Example:

```
tri 4 4 4
tri 4 5 12
tri 4 6 23
```

---

## Manifest

A manifest records provenance for a completed a(n) result. One manifest file per value of n.
Suggested path: `results/manifest_n<NN>.txt`.

Format: key=value lines, then one file entry per POLYRUN input file.

| Line | Format | Meaning |
|------|--------|---------|
| `n` | `n=<decimal>` | The polyomino size this manifest covers |
| `value` | `value=<decimal>` | The computed a(n) value |
| `gitrev` | `gitrev=<hex>` | Git commit hash of the engine that produced the run files |
| `cpu_s` | `cpu_s=<float>` | Total CPU-seconds (sum over all workers and heights) |
| `wall_s` | `wall_s=<float>` | Total wall-clock seconds (sum) |
| `rss_max_mb` | `rss_max_mb=<float>` | Peak RSS in megabytes (max over all workers) |
| `spill_bytes` | `spill_bytes=<decimal>` | Total NVMe spill bytes written during the run |
| `file` | `file=<path> records=<decimal> crc=<hex16>` | One run file entry; `crc` is the FNV-1a-64 body CRC as 16 lowercase hex digits |

Any number of `file=` lines appear, one per contributing POLYRUN file.
Lines beginning with `#` are comments and must be ignored by parsers.
Unknown keys must be ignored (forward-compatibility).

Example:

```
n=21
value=103246928482560
gitrev=abc1234def5678
cpu_s=28800.000
wall_s=7200.000
rss_max_mb=81920.000
spill_bytes=16106127360
file=/data/runs/h05_col05.polyrun records=000000000000091847 crc=3f8a1c2d4e5b6a7f
file=/data/runs/h06_col06.polyrun records=000000000000182033 crc=8b9c0d1e2f3a4b5c
```

---

## Residues

A residues file contains mod-p shadows of triangle values for multi-prime CRT verification.

Format: one triplet per line:

```
<n> <prime> <residue>
```

- `n`: polyomino size (decimal integer).
- `prime`: modulus (decimal integer; a prime).
- `residue`: `a(n) mod prime` (decimal integer, 0 ≤ residue < prime).

Lines may appear in any order. Lines beginning with `#` are comments.

Example:

```
# CRT residues for a(21) cross-check
21 1000000007 412847293
21 998244353 301928471
21 1000000009 509183742
```
