#!/usr/bin/env python3
"""Session 12: adjudicate the REGISTERED delta-multiplicity conjecture
ord_{y=1/4} Q_r = ceil(r/2) (equivalently Delta_x^ceil(r/2) | Q_r on the
slice x=1/4) at r <= 12, from the slice engine's fitted Q_r coefficients
(out_s12_slice_PQ_r12.json, per-prime mod-p lists; falls back to the s09
r<=8 receipt if the r12 run has not landed).

Method: for each mode, r, prime: synthetic-divide the mod-p polynomial
Q_r(y) by (y - 1/4) repeatedly until remainder != 0; same at y = 9/4.
ord(Delta_x) = min of the two orders. Also reports ord of P_r at 1/4
(expected 0) as a control.

Usage: python3 experiments/s12_Qord_check.py
Output: out_s12_Qord_check.txt
"""
import json, os

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
OUT = []


def say(m):
    print(m, flush=True)
    OUT.append(str(m))


def ord_at(coeffs, ypt, p, maxord=12):
    """vanishing order of sum c_i y^i at y=ypt mod p (synthetic division)."""
    cs = [c % p for c in coeffs]
    for o in range(maxord + 1):
        # evaluate; if nonzero, order is o; else deflate by (y - ypt)
        acc = 0
        for c in reversed(cs):
            acc = (acc * ypt + c) % p
        if acc:
            return o
        # synthetic division cs / (y - ypt)
        q = [0] * (len(cs) - 1)
        carry = 0
        for i in range(len(cs) - 1, 0, -1):
            carry = (cs[i] + carry * ypt) % p
            q[i - 1] = carry
        cs = q
        if not cs:
            return o + 1
    return maxord + 1


def main():
    for fn in ("out_s12_slice_PQ_r12.json", "out_s09_slice_PQ_run1.json"):
        path = os.path.join(ROOT, fn)
        if os.path.exists(path):
            break
    d = json.load(open(path))
    say(f"source receipt: {fn}")
    say("PREDICTION (registered in reports/session-12.md before this "
        "receipt existed): ord_{y=1/4} Q_r = ceil(r/2), both modes, r>=1")
    allok = True
    for mode in ("king", "poly"):
        say(f"[{mode}]")
        for rs, rec in sorted(d[mode].items(), key=lambda kv: int(kv[0])):
            r = int(rs)
            for pstr, qc in rec["qC"].items():
                p = int(pstr)
                inv4 = pow(4, p - 2, p)
                y14 = inv4 % p
                y94 = 9 * inv4 % p
                o14 = ord_at(qc, y14, p)
                o94 = ord_at(qc, y94, p)
                po14 = ord_at(rec["pC"][pstr], y14, p)
                want = (r + 1) // 2
                ok = (o14 == want) if r >= 1 else True
                allok &= ok
                say(f"  r={r} p={pstr[:6]}..: ord(Q,1/4)={o14} "
                    f"ord(Q,9/4)={o94} want={want if r>=1 else '-'} "
                    f"{'OK' if ok else 'MISMATCH'}  [ord(P,1/4)={po14}]")
    say(f"VERDICT: {'ALL MATCH — law confirmed at this range' if allok else 'MISMATCHES PRESENT'}")
    with open(os.path.join(ROOT, "out_s12_Qord_check.txt"), "w") as fp:
        fp.write(__doc__ + "\n" + "\n".join(OUT) + "\n")
    say("receipt: out_s12_Qord_check.txt")


if __name__ == "__main__":
    main()
