#!/usr/bin/env python3
"""Gate TMA: first transfer-matrix engine vs fixtures and the G2 engine.

Validation target is square-4 (polyominoes) per the implementation plan:
no new terms wanted, just the richest external truth available.

  A. totals: TMA counts equal b001168 (deeper than the oracle can reach)
  B. per-height: TMA's by-height counts equal G2's per-box height marginals
     (cross-ENGINE structural check: transfer matrix vs generation)
  C. ASan/UBSan build runs clean and agrees with the optimized build

CLI under test: tma LATTICE MAXN [--per-height] [--holes]
  totals: "n count" lines; --per-height: "h n count" lines;
  --holes: "n holes count" lines.
"""

import os
import shutil
import subprocess
import sys

from common import ROOT, Gate, parse_counts, read_bfile, run, spawn

TMA = os.path.join(ROOT, "build", "tma")
TMA_ASAN = os.path.join(ROOT, "build", "tma_asan")
TMA_HOLES = os.path.join(ROOT, "build", "tma_holes")  # holes/--modp engine (same source)
G2 = os.path.join(ROOT, "build", "g2")


def main():
    gate = Gate()
    for b in (TMA, TMA_ASAN, TMA_HOLES, G2):
        if not os.path.exists(b):
            print(f"FAIL missing binary {b} (run: make)")
            return 1

    # Checks M and N are the expensive end of this gate -- five square8 n<=14
    # sweeps, 391 s of the gate's 429 s serial (2026-08-06, gympie) -- and none
    # of them reads state another writes, so they run in the background while
    # A..L do their (cheap) work in front. Same binaries, same arguments, same
    # assertions, same printed order; only the waiting overlaps. Block measured
    # at 140 s concurrent vs 406 s serial. Everything below stays straight-line:
    # J and L resume from checkpoints their own previous step banked.
    depth_m, H_m = 14, 11
    f_plain_m = spawn(TMA, "square8", depth_m)
    f_fold_m = {t: spawn(TMA, "square8", depth_m, "--fold", "--threads", t)
                for t in (1, 4)}
    f_base_oh = spawn(TMA, "square8", depth_m, "--only-height", H_m)
    f_fold_oh = spawn(TMA, "square8", depth_m, "--only-height", H_m,
                      "--fold", "--threads", 4)
    f_smoke = spawn(TMA, "square8", 14, "--only-height", 12)

    # A. totals vs fixture
    depth_a = 12
    expected = read_bfile("b001168.txt")
    got = parse_counts(run(TMA, "square4", depth_a))
    bad = [n for n in range(1, depth_a + 1) if got.get((n,)) != expected[n]]
    gate.check(not bad, f"A totals      square4 n<={depth_a} vs b001168.txt"
          + (f"  MISMATCH at n={bad}" if bad else ""))

    # B. per-height vs G2 per-box marginals
    depth_b = 10
    tma_h = parse_counts(run(TMA, "square4", depth_b, "--per-height"))
    marg = {}
    for (n, w, h), c in parse_counts(run(G2, "square4", depth_b, "--per-box")).items():
        marg[(h, n)] = marg.get((h, n), 0) + c
    gate.check(tma_h == marg,
          f"B per-height  square4 n<={depth_b} vs G2 per-box marginals "
          f"({len(marg)} (h,n) classes)")

    # C. sanitizer build agrees and runs clean
    depth_c = 9
    opt = parse_counts(run(TMA, "square4", depth_c))
    san = parse_counts(run(TMA_ASAN, "square4", depth_c))
    gate.check(opt == san, f"C asan        square4 n<={depth_c} clean + equal")

    # --- square-8 (polyplets): THE novel transition ---

    # D. totals vs the real OEIS sequence A006770 (king-move animals)
    depth_d = 11
    exp8 = read_bfile("b006770.txt")
    got8 = parse_counts(run(TMA, "square8", depth_d))
    bad8 = [n for n in range(1, depth_d + 1) if got8.get((n,)) != exp8[n]]
    gate.check(not bad8, f"D totals      square8 n<={depth_d} vs b006770.txt"
          + (f"  MISMATCH at n={bad8}" if bad8 else ""))

    # E. per-height vs G2 per-box marginals (transfer matrix vs generation)
    depth_e = 9
    tma8_h = parse_counts(run(TMA, "square8", depth_e, "--per-height"))
    marg8 = {}
    for (n, w, h), c in parse_counts(
            run(G2, "square8", depth_e, "--per-box")).items():
        marg8[(h, n)] = marg8.get((h, n), 0) + c
    gate.check(tma8_h == marg8,
          f"E per-height  square8 n<={depth_e} vs G2 per-box marginals "
          f"({len(marg8)} (h,n) classes)")

    # F. square-8 sanitizer build clean + equal
    depth_f = 8
    gate.check(parse_counts(run(TMA, "square8", depth_f))
          == parse_counts(run(TMA_ASAN, "square8", depth_f)),
          f"F asan        square8 n<={depth_f} clean + equal")

    # G. (size, edge-perimeter) joint distribution: transfer matrix == generation.
    #    A finer-grained Method-B-vs-Method-A check than the totals -- the TM
    #    carries perimeter as a second DP index (cpp/tma/sweep8_perim.h).
    depth_g = 11
    tma_p = parse_counts(run(TMA, "square8", depth_g, "--perimeter"))
    g2_p = parse_counts(run(G2, "square8", depth_g, "--perimeter"))
    gate.check(tma_p == g2_p,
          f"G perimeter   square8 n<={depth_g} TMA==G2 "
          f"({len(g2_p)} (n,perimeter) cells)")

    # H. (size, #holes) joint distribution: transfer matrix == the validated
    #    per-animal flood oracle (results/holes_n14.txt, #24). The hole count is
    #    carried in the column DP via the Euler characteristic (cpp/tma/euler.h,
    #    sweep8_holes.h); this is the fast regression that the engine's hole
    #    accounting still agrees with the flood. PRIMARY convention = 4-bg holes.
    depth_h = 11
    oracle_path = os.path.join(ROOT, "results", "holes_n14.txt")
    flood = {}
    with open(oracle_path) as f:
        for line in f:
            n, holes, count = map(int, line.split())
            if n <= depth_h:
                flood[(n, holes)] = count
    holes_serial = parse_counts(run(TMA_HOLES, "square8", depth_h, "--holes"))
    holes_serial = {k: v for k, v in holes_serial.items() if k[0] <= depth_h}
    gate.check(holes_serial == flood,
          f"H holes       square8 n<={depth_h} tma_holes==flood oracle "
          f"({len(flood)} (n,#holes) classes)")

    # I. holes path multithreaded == serial: the sharded MT sweep
    #    (sweepSquare8HeightHolesMT) must be bit-identical to the single-thread one.
    depth_i = 11
    base = parse_counts(run(TMA_HOLES, "square8", depth_i, "--holes"))
    mt = parse_counts(run(TMA_HOLES, "square8", depth_i, "--holes", "--threads", "4"))
    gate.check(base == mt,
          f"I holes MT    square8 n<={depth_i} --threads 4 == serial")

    # J. holes per-height checkpoint: a full --checkpoint run equals plain, and a
    #    second run over the populated dir (every height resumed from disk)
    #    reproduces it -- exercises both the bank and the resume/load paths.
    depth_j = 11
    ckdir = os.path.join(ROOT, "runs", "ckpt", "gate_holes")
    shutil.rmtree(ckdir, ignore_errors=True)
    ck1 = parse_counts(run(TMA_HOLES, "square8", depth_j, "--holes", "--checkpoint", ckdir))
    ck2 = parse_counts(run(TMA_HOLES, "square8", depth_j, "--holes", "--checkpoint", ckdir))
    shutil.rmtree(ckdir, ignore_errors=True)
    gate.check(base == ck1 and ck1 == ck2,
          f"J holes ckpt  square8 n<={depth_j} write+resume == plain")

    # K. --reserve N pre-sizes the store (to skip the doubling-grow transient) but
    #    must not change the result -- it's pure allocation strategy.
    resv = parse_counts(run(TMA_HOLES, "square8", depth_i, "--holes", "--reserve", "200000"))
    gate.check(base == resv,
          f"K holes resv  square8 n<={depth_i} --reserve == plain")

    # L. intra-height checkpoint: a single --only-height sweep killed mid-height
    #    (env hook _Exit's right after the column-k save) resumes from the on-disk
    #    boundary state to a byte-identical result -- for serial AND MT.
    depth_l, H_l, kill_col = 14, 10, 5
    ckdir = os.path.join(ROOT, "runs", "ckpt", "gate_ih")
    base_l = run(TMA_HOLES, "square8", depth_l, "--only-height", H_l)  # clean baseline
    for threads in (1, 4):
        shutil.rmtree(ckdir, ignore_errors=True)
        argv = [TMA_HOLES, "square8", str(depth_l), "--only-height", str(H_l),
                "--threads", str(threads), "--checkpoint", ckdir]
        env = dict(os.environ, TMA_CKPT_SECS="0", TMA_CKPT_MIN_STATES="0",
                   TMA_CKPT_KILL_AT_COL=str(kill_col))
        killed = subprocess.run(argv, capture_output=True, text=True, env=env)
        banked = os.path.exists(os.path.join(ckdir, "ckpt"))
        resumed = subprocess.run(argv, capture_output=True, text=True)  # no kill env
        gate.check(killed.returncode == 137 and banked and resumed.stdout == base_l,
              f"L ihckpt T={threads}  square8 n<={depth_l} kill@col{kill_col} resume == clean")
    # ...and the holes --only-height path (same checkpoint, larger stride)
    shutil.rmtree(ckdir, ignore_errors=True)
    base_h = run(TMA_HOLES, "square8", depth_l, "--holes", "--only-height", H_l)
    argv_h = [TMA_HOLES, "square8", str(depth_l), "--holes", "--only-height", str(H_l),
              "--threads", "4", "--checkpoint", ckdir]
    env = dict(os.environ, TMA_CKPT_SECS="0", TMA_CKPT_MIN_STATES="0",
               TMA_CKPT_KILL_AT_COL=str(kill_col))
    killed_h = subprocess.run(argv_h, capture_output=True, text=True, env=env)
    resumed_h = subprocess.run(argv_h, capture_output=True, text=True)
    gate.check(killed_h.returncode == 137 and resumed_h.stdout == base_h,
          f"L ihckpt holes square8 n<={depth_l} kill@col{kill_col} resume == clean")
    shutil.rmtree(ckdir, ignore_errors=True)

    # M. R1 vertical-mirror fold (exact u64 path): --fold must be byte-identical to the
    #    unfolded counts at every n. The a(21)/a(22) launch runs the per-height FOLDED
    #    exact path (an_fold_parallel.sh -> --only-height H --fold), so this guards the
    #    production engine directly -- full sweep serial+MT, and the only-height unit.
    plain_m = parse_counts(f_plain_m.result())
    for threads in (1, 4):
        fold_m = parse_counts(f_fold_m[threads].result())
        gate.check(fold_m == plain_m,
              f"M fold T={threads}    square8 n<={depth_m} --fold == unfolded")
    # H_m = 11 is a heavy mid-height, the exact unit the driver invokes
    base_oh = parse_counts(f_base_oh.result())
    fold_oh = parse_counts(f_fold_oh.result())
    gate.check(fold_oh == base_oh,
          f"M fold only-h  square8 n<={depth_m} H{H_m} --fold MT == unfolded")

    # N. standing smoke fixture (docs/frontier/harness-spec.md Part 1): a FIXED,
    #    off-frontier (N,H) that runs in well under a minute on one core -- the
    #    dead-on-arrival check every engine-swap idea's `## Smoke test` cites. The
    #    dense FlatDB baseline (build/tma now) is the byte oracle; a backend swap
    #    that changes one count is a defect. As the swappable backends land behind
    #    statedb.h (experiments/bench_column.cpp's Backend seam), add them to this
    #    loop -- each must reproduce `base` byte-for-byte (absent backends skipped).
    smoke = parse_counts(f_smoke.result())
    base = {(12,): 177147, (13,): 5511240, (14,): 97548948}  # dense H12/N14 marginal
    gate.check({k: v for k, v in smoke.items() if v} == base,
          "N smoke       square8 H12 N14 dense baseline == 177147/5511240/97548948")
    # backend reproduction (build/tma gains --backend as each store lands; skip til then):
    # for backend in ("hash", "sort", "concurrent", "compressed", "u128"):
    #     got = run(TMA, "square8", 14, "--only-height", 12, "--backend", backend)
    #     gate.check(got == base, f"N smoke {backend:10} == dense baseline")

    return gate.verdict("TMA")


if __name__ == "__main__":
    sys.exit(main())
