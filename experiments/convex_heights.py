#!/usr/bin/env python3
"""H2: fixed-height convex-polyplet area GFs + psi analysis.

Height-resolved HV-convex king animals by area via the phase-automaton row
DP (multiplicity formulas; validated against brute force n<=8 and the
convex-mirage row sums). BM recovery with holdouts gives exact rational
GFs, denominator orders 1, 3, 7, 14, 25, 36, 53 (H = 1..7), stored in
results/convex_height_denominators.json. New-root contents psi_H have
degrees 1, 2, 3, 5, 7, 6, 8 -- root RECYCLING, the opposite of the full
family's Atom Ledger separation. See results/subclasses.md.
"""
import json
import os
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = (1 << 61) - 1


def trans_count(w, wp, ph, php):
    D = wp - w
    pl, pr = ph
    plp, prp = php
    if pl == 1 and plp == 0:
        return 0
    if pr == 1 and prp == 0:
        return 0
    if (pl, pr) == (0, 0):
        if (plp, prp) == (0, 0):
            return max(0, D + 1)
        if (plp, prp) == (1, 0):
            return max(0, w - max(1, -D) + 1)
        if (plp, prp) == (0, 1):
            return max(0, min(-1, D) + w + 1)
        return max(0, min(w, -1 - D))
    if (pl, pr) == (1, 0):
        if (plp, prp) == (1, 0):
            return max(0, w - max(0, -D) + 1)
        return max(0, min(w, -1 - D) + 1)
    if (pl, pr) == (0, 1):
        if (plp, prp) == (0, 1):
            return max(0, min(0, D) + w + 1)
        return max(0, min(w, -D))
    return max(0, min(w, -D) + 1)


def convex_by_height(H, N):
    PH = [(0, 0), (1, 0), (0, 1), (1, 1)]
    dp = defaultdict(lambda: [0] * (N + 1))
    for w in range(1, N + 1):
        dp[(w, (0, 0))][w] = 1
    for _ in range(H - 1):
        ndp = defaultdict(lambda: [0] * (N + 1))
        for (w, ph), vec in dp.items():
            nmin = next((i for i, v in enumerate(vec) if v), None)
            if nmin is None:
                continue
            for wp in range(1, N - nmin + 1):
                for php in PH:
                    t = trans_count(w, wp, ph, php)
                    if t:
                        tgt = ndp[(wp, php)]
                        for n0 in range(nmin, N - wp + 1):
                            if vec[n0]:
                                tgt[n0 + wp] += vec[n0] * t
        dp = ndp
    out = [0] * (N + 1)
    for vec in dp.values():
        for n0, v in enumerate(vec):
            out[n0] += v
    return out


def main():
    D = json.load(open(os.path.join(ROOT, "results",
                                    "convex_height_denominators.json")))
    Qs = {int(k): v for k, v in D.items()}
    assert {H: len(q) - 1 for H, q in sorted(Qs.items())} == \
        {1: 1, 2: 3, 3: 7, 4: 14, 5: 25, 6: 36, 7: 53}
    # each stored denominator annihilates a fresh series (full holdout)
    for H, q in sorted(Qs.items()):
        r = len(q) - 1
        N = max(3 * r + 10, 40)
        s = convex_by_height(H, N)
        assert all(sum(q[j] * s[i - j] for j in range(r + 1)) == 0
                   for i in range(2 * r + 2, N + 1)), H
    # row sums cross-check vs convex-mirage totals
    tot = [0] * 9
    for H in range(1, 9):
        s = convex_by_height(H, 8)
        for n in range(9):
            tot[n] += s[n]
    assert tot[1:] == [1, 4, 16, 61, 221, 766, 2566, 8390]
    print("convex height GFs: orders 1,3,7,14,25,36,53 re-verified on fresh "
          "series; row sums match  OK")


if __name__ == "__main__":
    main()
