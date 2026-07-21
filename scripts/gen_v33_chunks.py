#!/usr/bin/env python3
"""Generate the per-column chunk-value Lean files for the heavy leaf `V 3 3`.

`Polyplets/WeightsChunk.lean` proves (native_decide-free) that
`V 3 3 = ∑_{m=-7}^{7} (CFGVchunk m).card`. This script emits one Lean file per
column `m` holding the single `native_decide` `(CFGVchunk m).card = <value>`,
one heavy chunk per file so `lake` builds them in parallel (module-level).

The fifteen expected cardinalities are the leftmost-cluster-column histogram of
the 4778 V(3,3) configurations, cross-checked out of Lean by
`scripts/gen_v33_chunks.py --check` (mirrors `Weights.lean`'s predicates):

    m:   -7  -6   -5   -4   -3    -2    -1    0    1   2..7
  card:   4  43  203  504  835  1033  1032  682  442    0    (sum 4778)

Per-chunk enumeration base (`C(cells,6)·15` pairs, cells = width·3):
  m ∈ [-7,0]: 8 cols → C(24,6)·15 ≈ 2.02M   (the eight heavy files)
  m = 1:      7 cols → C(21,6)·15 ≈ 0.81M
  m ∈ [2,7]:  shrinking, all folded into one tail file (counts 0)
All ≤ the proven-safe 3.26M ceiling (`Vt 3 3` built at that scale).
"""
from __future__ import annotations
import sys
from itertools import combinations
from pathlib import Path

# leftmost-cluster-column histogram of V(3,3); index = m, value = (CFGVchunk m).card
CARD = {-7: 4, -6: 43, -5: 203, -4: 504, -3: 835, -2: 1033, -1: 1032, 0: 682,
        1: 442, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0}

HEADER = """/-
Copyright (c) 2026 Jason H Parker. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Jason H Parker
-/
import Polyplets.WeightsChunk

/-!
# `V 3 3` chunk value{plural}: column{plural} {cols}

`native_decide` leaf {leaf} of the `V 3 3` partition
(`WeightsChunk.V_3_3_eq_sum_chunks`).
{scale}
-/

namespace Polyplets

set_option linter.style.nativeDecide false
set_option maxRecDepth 4000

"""


def tag(m: int) -> str:
    return f"n{-m}" if m < 0 else f"p{m}"


def theorem(m: int) -> str:
    return (f"/-- `(CFGVchunk {m}).card = {CARD[m]}` "
            f"(heavy `native_decide`; cross-checked enumeration). -/\n"
            f"theorem CFGVchunk_card_{tag(m)} : (CFGVchunk ({m} : ℤ)).card = {CARD[m]} := by\n"
            f"  native_decide\n")


# one file per heavy column m ∈ [-7, 0] (the eight 2.02M columns), plus one tail
# file for the lighter columns m ∈ [1, 7]. Nine chunk modules total, so a full
# `lake build` runs ≤ 9 heavy `native_decide`s at once (10-core budget).
FILES: dict[str, list[int]] = {}
letters = "ABCDEFGH"  # eight heavy columns -7..0
for i, m in enumerate(range(-7, 1)):
    FILES[f"WeightsChunk{letters[i]}"] = [m]
FILES["WeightsChunkTail"] = list(range(1, 8))


def emit(outdir: Path) -> None:
    for name, cols in FILES.items():
        plural = "s" if len(cols) > 1 else ""
        colstr = ", ".join(str(m) for m in cols)
        if len(cols) == 1:
            scale = "Enumerates ≈ 2.02M pairs (8-column window)."
        else:
            scale = ("Column 1 enumerates ≈ 0.81M pairs; columns 2..7 are empty\n"
                     "(no config's cluster starts that far right) over shrinking\n"
                     "windows. All light — folded into one file.")
        leaf = "for " + colstr if len(cols) == 1 else "for columns " + colstr
        body = HEADER.format(plural=plural, cols=colstr, leaf=leaf, scale=scale)
        body += "\n".join(theorem(m) for m in cols) + "\n\nend Polyplets\n"
        (outdir / f"{name}.lean").write_text(body)
        print(f"wrote {name}.lean  (m = {colstr})")


# ---- out-of-Lean cross-check of the CARD histogram (mirrors Weights.lean) ----
def king_connected(S):
    S = set(S)
    if not S:
        return True
    start = next(iter(S)); seen = {start}; st = [start]
    while st:
        x, y = st.pop()
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == dy == 0:
                    continue
                nb = (x + dx, y + dy)
                if nb in S and nb not in seen:
                    seen.add(nb); st.append(nb)
    return seen == S


def check():
    l = j = 3
    w = l + j + 1  # |x| <= 7
    cols = range(-w, w + 1)
    interior = [(x, y) for y in range(1, l + 1) for x in cols]
    uniq = set()
    for C in combinations(interior, l + j):
        if not all(sum(1 for c in C if c[1] == i) >= 2 for i in range(1, l + 1)):
            continue
        for qx in cols:
            S = frozenset(C) | {(0, 0), (qx, l + 1)}
            if len(S) == l + j + 2 and king_connected(S):
                uniq.add(S)
    hist = {m: 0 for m in range(-7, 8)}
    for S in uniq:
        m = min(c[0] for c in S if 1 <= c[1] <= l)
        hist[m] += 1
    ok = hist == CARD and sum(hist.values()) == 4778
    print("histogram:", hist)
    print("sum:", sum(hist.values()))
    print("matches embedded CARD and totals 4778:", ok)
    return ok


if __name__ == "__main__":
    if "--check" in sys.argv:
        sys.exit(0 if check() else 1)
    emit(Path(__file__).resolve().parent.parent / "polyplets" / "Polyplets")
