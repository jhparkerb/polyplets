#!/usr/bin/env python3
"""Session 04: subfamily AREA sequences from the q-Temperley solution
(x=y=1), king and polyomino modes:

  stacks          = phase (0,0) alone  (identical in both modes: king
                    constraints are inactive in phase (0,0));
                    expected = A001523 (stack polyominoes by area)
  directed-convex = phases (0,0)+(1,0)  (s03's subfamily, by AREA now;
                    by semiperimeter it was A014300 for king)
  full            = all phases (cross-checked in s04_q_temperley.py)

Also verifies the stack identification against a tiny independent DP
(nested-interval rows, bottom-up), and prints everything for OEIS lookup.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from s04_q_temperley import QS, Solver, series_ints
from collections import defaultdict

N = int(sys.argv[1]) if len(sys.argv) > 1 else 30


def stacks_dp(nmax):
    """Independent check: # row-nested animals (row_i contained in row_{i+1},
    reading top to bottom) with n cells, up to translation.  DP over
    (last-row length) building upward: prev row inside current."""
    # build DOWNWARD from top: each next row contains previous: length grows
    # state: current bottom-row length k; ways counted with multiplicity of
    # placements: from k to k' >= k there are k'-k+1 offsets
    out = [0] * (nmax + 1)
    dp = defaultdict(int)
    for k in range(1, nmax + 1):
        dp[(k, k)] = 1  # (last length, area)
    for (k, n), c in list(dp.items()):
        out[n] += c
    frontier = dp
    while frontier:
        nd = defaultdict(int)
        for (k, n), c in frontier.items():
            for kp in range(k, nmax - n + 1):
                nd[(kp, n + kp)] += c * (kp - k + 1)
        for (k, n), c in nd.items():
            out[n] += c
        frontier = nd
    return out[1:]


def main():
    QS.N = N
    for king in (True, False):
        tag = "king" if king else "poly"
        s = Solver(1, 1, king=king)
        F = s.solve()
        stacks = series_ints(s.F001)[1:]
        dirconv = series_ints(s.F001 + s.F101)[1:]
        full = series_ints(F)[1:]
        print(f"== {tag} ==")
        print("stacks (F00):     " + ", ".join(map(str, stacks[:24])))
        print("directed (F00+F10): " + ", ".join(map(str, dirconv[:24])))
        print("full:             " + ", ".join(map(str, full[:24])))
        if king:
            k_stacks, k_dir = stacks, dirconv
        else:
            p_stacks, p_dir = stacks, dirconv
    same = k_stacks == p_stacks
    print(f"\nstacks identical king vs poly (phase (0,0) has no king "
          f"constraint): {'OK' if same else 'FAIL'}")
    assert same

    ref = stacks_dp(min(N, 22))
    ok = k_stacks[:len(ref)] == ref
    print(f"stacks vs independent nested-interval DP (n<={len(ref)}): "
          f"{'OK' if ok else 'FAIL ' + str(ref)}")
    assert ok


if __name__ == "__main__":
    main()
