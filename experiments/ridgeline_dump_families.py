#!/usr/bin/env python3
"""Dump an excess-graded family table in the format severance_w3_depths._load_table reads.

The Python family DP is the cost of every Ridgeline run at large K
(families(60, emax=1) is ~6.5 min); caching it makes reruns instant.  Format is
exactly the one cpp/severance_w3_families writes:

    # severance_w3_families K=<K> emax=<E>
    e k sig bb pp

Written to results/severance_w3_families_K<K>_e<E>.txt.  ridgeline_master.
load_families picks it up for any K' <= K at the same emax;
severance_w3_depths._load_table also does, but only for K < 40, which is why the
Ridgeline reader exists (the useful excess-1 table is K = 60).

Run from repo root:  python3 experiments/ridgeline_dump_families.py K EMAX [outdir]
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import severance_w3_depths as W                                    # noqa: E402


def main():
    K = int(sys.argv[1])
    emax = int(sys.argv[2])
    outdir = sys.argv[3] if len(sys.argv) > 3 else W.TABLE_DIR
    path = os.path.join(outdir, "severance_w3_families_K%d_e%d.txt" % (K, emax))
    if os.path.exists(path):
        print("refusing to overwrite existing %s" % path)
        return 1
    t0 = time.time()
    sig, bb, pp = W.families(K, emax, verbose=True)
    print("families(%d, %d) in %.1fs" % (K, emax, time.time() - t0))
    tmp = path + ".partial"
    with open(tmp, "w") as fh:
        fh.write("# severance_w3_families K=%d emax=%d\n" % (K, emax))
        for e in range(emax + 1):
            for k in range(K + 1):
                fh.write("%d %d %d %d %d\n" % (e, k, sig[e][k], bb[e][k], pp[e][k]))
    os.rename(tmp, path)
    print("wrote %s" % path)
    # read it straight back and insist it reproduces the arrays.  Note
    # severance_w3_depths._load_table only scans K < 40, so the reader used here
    # is ridgeline_master.load_families, which accepts any K.
    W._FAM.clear()
    from ridgeline_master import load_families                     # noqa: E402
    got = load_families(K, emax)
    assert got[0] == sig and got[1] == bb and got[2] == pp, \
        "round-trip through the table file changed the families"
    print("round-trip OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
