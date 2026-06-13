#!/usr/bin/env python3
"""Gate E0: weighted connected-subgraph counter vs exhaustive 2^V brute force.

E0 is the generic counter under the symmetric enumerator. Its oracle here is
dead-simple: enumerate every subset of vertices, test connectivity directly,
tally by total weight. Different code, different language -- a true oracle for
the C++ counter. Tested on hand-structured graphs plus random graphs.
"""

import itertools
import os
import subprocess
import sys

from common import ROOT, Gate

E0 = os.path.join(ROOT, "build", "subgraph_count")


def brute(V, weights, edges, maxn):
    """Count connected subsets by total weight, by exhaustive enumeration."""
    adj = {i: set() for i in range(V)}
    for a, b in edges:
        adj[a].add(b)
        adj[b].add(a)
    counts = [0] * (maxn + 1)
    for size in range(1, V + 1):
        for subset in itertools.combinations(range(V), size):
            w = sum(weights[i] for i in subset)
            if w > maxn:
                continue
            s = set(subset)
            seen = {subset[0]}
            stack = [subset[0]]
            while stack:
                x = stack.pop()
                for y in adj[x]:
                    if y in s and y not in seen:
                        seen.add(y)
                        stack.append(y)
            if seen == s:  # connected
                counts[w] += 1
    return {w: counts[w] for w in range(1, maxn + 1) if counts[w]}


def run_e0(V, weights, edges, maxn):
    lines = [str(V), " ".join(map(str, weights)), str(len(edges))]
    lines += [f"{a} {b}" for a, b in edges]
    r = subprocess.run([E0, str(maxn)], input="\n".join(lines) + "\n",
                       capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"E0 rc={r.returncode}: {r.stderr}")
    out = {}
    for line in r.stdout.strip().splitlines():
        w, c = line.split()
        out[int(w)] = int(c)
    return out


# (name, V, weights, edges, maxn)
CASES = [
    ("path-3", 3, [1, 1, 1], [(0, 1), (1, 2)], 3),
    ("triangle", 3, [1, 1, 1], [(0, 1), (1, 2), (0, 2)], 3),
    ("weighted-edge", 2, [1, 2], [(0, 1)], 3),
    ("star-4", 4, [1, 1, 1, 1], [(0, 1), (0, 2), (0, 3)], 4),
    ("weighted-path", 4, [1, 2, 1, 4], [(0, 1), (1, 2), (2, 3)], 8),
    ("square-4cycle", 4, [1, 1, 1, 1], [(0, 1), (1, 2), (2, 3), (3, 0)], 4),
    ("3x3-king", 9, [1] * 9,
     [(0, 1), (1, 2), (3, 4), (4, 5), (6, 7), (7, 8),
      (0, 3), (1, 4), (2, 5), (3, 6), (4, 7), (5, 8),
      (0, 4), (1, 3), (1, 5), (2, 4), (3, 7), (4, 6), (4, 8), (5, 7)], 5),
    ("mixed-weights", 5, [2, 1, 2, 1, 4],
     [(0, 1), (1, 2), (2, 3), (3, 4), (0, 4), (1, 3)], 7),
]


def main():
    if not os.path.exists(E0):
        print(f"FAIL missing binary {E0} (run: make build/subgraph_count)")
        return 1
    gate = Gate()
    for name, V, w, edges, maxn in CASES:
        want = brute(V, w, edges, maxn)
        got = run_e0(V, w, edges, maxn)
        gate.check(got == want, f"{name:16s} maxn={maxn}  "
                   + ("match" if got == want else f"\n   E0={got}\n   brute={want}"))
    return gate.verdict("E0")


if __name__ == "__main__":
    sys.exit(main())
