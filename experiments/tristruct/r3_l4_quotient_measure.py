#!/usr/bin/env python3
"""r3_l4_quotient_measure: L4 lane measurement (round 3).

Runs the BANKED build/symcount_fast (rev of 2026-08-07, no new code) in
hmirror --byheight and r180 --byheight modes at small N, times each run,
and cross-checks every emitted (n,H,count) row against the banked symtm
frontier tables in results/percell_raw/ (sum over W for hmirror).

Purpose: anchor the cost model for a quotient-domain route to
I_H(<h>) and I_H(C2), and establish that the quotient DFS classifies by
TRUE bounding-box height (so decline reason 1 -- "no bounded-height
route" -- does not bind against a quotient-domain method).

Throwaway per docs/triangle-round3-brief.md measurement boundary:
laptop, minutes, small N, exact integer arithmetic.
"""
import subprocess, sys, time, collections, os

ROOT = "/Users/jasonp/src/polyominoes"
BIN = os.path.join(ROOT, "build/symcount_fast")
RAW = os.path.join(ROOT, "results/percell_raw")

def load_symtm_hmirror():
    # n H W count -> I_H(<h>) = sum over W ; I_W(<v>) = group by W
    ih = collections.Counter()
    iv = collections.Counter()
    with open(os.path.join(RAW, "hmirror.byheight.n32.out")) as f:
        for line in f:
            n, H, W, c = map(int, line.split())
            ih[(n, H)] += c
            iv[(n, W)] += c
    return ih, iv

def load_symtm_r180():
    ic2 = {}
    with open(os.path.join(RAW, "r180.byheight.n32.out")) as f:
        for line in f:
            n, H, c = map(int, line.split())
            ic2[(n, H)] = c
    return ic2

def run(mode, N, threads=8):
    t0 = time.monotonic()
    out = subprocess.run([BIN, mode, str(N), str(threads), "--byheight"],
                         capture_output=True, text=True, check=True)
    wall = time.monotonic() - t0
    table = {}
    for line in out.stdout.splitlines():
        n, H, c = map(int, line.split())
        table[(n, H)] = c
    return wall, table

def main():
    ih, iv = load_symtm_hmirror()
    ic2 = load_symtm_r180()
    for mode, ref in (("hmirror", ih), ("r180", ic2)):
        prev = None
        for N in [int(x) for x in sys.argv[1:]] or [12, 14, 16, 18]:
            wall, tab = run(mode, N)
            # cross-check every cell with n <= N against banked symtm table
            mism = 0
            cells = 0
            for n in range(1, N + 1):
                for H in range(1, n + 1):
                    a = tab.get((n, H), 0)
                    b = ref.get((n, H), 0)
                    cells += 1
                    if a != b:
                        mism += 1
                        print(f"MISMATCH {mode} n={n} H={H} dfs={a} symtm={b}")
            tot = sum(c for (n, _), c in tab.items() if n == N)
            ratio = (wall / prev) if prev and prev > 0.01 else float("nan")
            print(f"{mode} N={N} wall={wall:.2f}s Fix(N)={tot} "
                  f"cells={cells} mismatches={mism} ratio_vs_prev={ratio:.3f}")
            prev = wall
    print("done")

if __name__ == "__main__":
    main()
