#!/usr/bin/env python3
"""Sum farmed dmirror strip outputs into the full count file.

  scripts/dmirror_sum.py MAXN [RUNDIR]

Reads RUNDIR/dmirror.S*.out (default runs/sym<MAXN>/), each the exact-bbox
strip contribution from `symtm dmirror MAXN T S S`. Refuses to combine
unless every strip S=1..MAXN is present exactly once (disjointness +
coverage are what make the sum the theorem). Writes RUNDIR/dmirror.out in
the standard "n count" form and echoes it.
"""

import glob
import os
import re
import sys


def main():
    maxn = int(sys.argv[1])
    rundir = sys.argv[2] if len(sys.argv) > 2 else f"runs/sym{maxn}"
    seen = {}
    for path in glob.glob(os.path.join(rundir, "dmirror.S*.out")):
        s = int(re.search(r"dmirror\.S(\d+)\.out$", path).group(1))
        if s in seen:
            raise SystemExit(f"strip S={s} appears twice ({path}, {seen[s]})")
        seen[s] = path
    missing = [s for s in range(1, maxn + 1) if s not in seen]
    extra = [s for s in seen if not 1 <= s <= maxn]
    if missing or extra:
        raise SystemExit(f"bad strip coverage: missing={missing} extra={extra}")

    total = [0] * (maxn + 1)
    for s, path in sorted(seen.items()):
        with open(path) as f:
            for ln in f:
                parts = ln.split()
                if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                    n, c = int(parts[0]), int(parts[1])
                    if not 1 <= n <= maxn:
                        raise SystemExit(f"{path}: n={n} out of range")
                    total[n] += c

    out = os.path.join(rundir, "dmirror.out")
    with open(out, "w") as f:
        for n in range(1, maxn + 1):
            if total[n]:
                f.write(f"{n} {total[n]}\n")
    with open(out) as f:
        sys.stdout.write(f.read())
    print(f"wrote {out} from {len(seen)} strips", file=sys.stderr)


if __name__ == "__main__":
    main()
