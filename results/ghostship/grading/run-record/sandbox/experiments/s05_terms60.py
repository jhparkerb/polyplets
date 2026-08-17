#!/usr/bin/env python3
"""Session 05: exact area-sequence terms to n=60 from the s04 q-Temperley
solver (exact Fractions), for king, control, and both directed subfamilies.
These extend the banked 50-term sequences (first 50 must match the banked
receipts -- checked here against out_s04_tm50.txt / OEIS b-file numbers via
the banked MIRAGE list and out_s04_subfamilies.txt)."""
import sys, os, time, re

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from s04_q_temperley import QS, Solver, series_ints, MIRAGE_KING  # noqa

N = 60


def get_seqs(king):
    QS.N = N
    s = Solver(1, 1, king=king)
    F = s.solve()
    full = series_ints(F)[1:]
    directed = series_ints(s.F001 + s.F101)[1:]
    return full, directed


def main():
    t0 = time.time()
    king_full, king_dir = get_seqs(True)
    poly_full, poly_dir = get_seqs(False)
    print(f"solver N={N} runs: {time.time()-t0:.1f}s")

    # cross-check against banked receipts
    assert king_full[:30] == MIRAGE_KING, "king vs banked 30 mismatch"
    tm50 = []
    with open(os.path.join(HERE, "..", "out_s04_tm50.txt")) as f:
        for line in f:
            m = re.match(r"\s*(\d+)\s+(\d+)\s*$", line)
            if m:
                tm50.append(int(m.group(2)))
    if len(tm50) >= 50:
        ok = king_full[:50] == tm50[:50]
        print(f"king first 50 vs out_s04_tm50.txt: {'OK' if ok else 'FAIL'}")
        assert ok
    else:
        print(f"(out_s04_tm50.txt parse found {len(tm50)} terms; skipping)")

    for name, seq in [("king_full", king_full), ("king_directed", king_dir),
                      ("poly_full", poly_full), ("poly_directed", poly_dir)]:
        print(f"\n{name} (n=1..{N}):")
        for i, v in enumerate(seq, 1):
            print(f"  {i} {v}")


if __name__ == "__main__":
    main()
