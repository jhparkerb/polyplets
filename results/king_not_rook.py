#!/usr/bin/env python3
# "Essentially-diagonal" fixed animals: king-connected (polyplet) but NOT
# rook-connected (polyomino) -- i.e. animals that fall into >=2 pieces if every
# diagonal-only contact is cut. Count = A006770(n) - A001168(n), since every fixed
# polyomino is a fixed polyplet (rook adjacency implies king adjacency). A clean
# characteristically-polyplet class; candidate new OEIS sequence.
A006770 = [1, 4, 20, 110, 638, 3832, 23592, 147941, 940982, 6053180, 39299408,
           257105146, 1692931066, 11208974860, 74570549714, 498174818986,
           3340366308393, 22471158811164, 151609203011580, 1025573519362016]
A001168 = [1, 2, 6, 19, 63, 216, 760, 2725, 9910, 36446, 135268, 505861, 1903890,
           7204874, 27394666, 104592937, 400795844, 1540820542, 5940738676,
           22964779660]

d = [k - r for k, r in zip(A006770, A001168)]
print("n  king(A006770)  rook(A001168)  king-not-rook")
for i, (k, r, dd) in enumerate(zip(A006770, A001168, d), 1):
    print(f"{i:2d}  {k:>16d}  {r:>14d}  {dd:>16d}")
print("\nking-not-rook, n=1..20:")
print(", ".join(map(str, d)))
print("\nfraction king-not-rook = d(n)/A006770(n):")
print(", ".join(f"{dd/k:.4f}" for dd, k in zip(d, A006770)))
