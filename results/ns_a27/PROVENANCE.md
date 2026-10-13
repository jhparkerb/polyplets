# a(27)

a(27) = 703126792093436034256

Computed 2026-07-02 at revision `b390518`, 128-bit counter, split across two
machines: dalby (80 cores, 13,553.9 s of wall) enumerated height 16 and
filled heights 1, 2 and 17..27 from the closed forms; ayr (32 cores, 9697.2 s)
enumerated heights 3..15. The H = 16 frontier peaked near 2.10 M states with
126 GB spilled to disk. The rows were combined at revision `b14e0b1` with
every height 1..27 required to be present exactly once.

Files: `triangle.txt`, `perheight/h{1..27}.out`, `cost_profile_dalby.tsv`.

Checks:

- a(1)..a(20) match `fixtures/b006770.txt`; a(21)..a(26) match
  `results/ns_a2{1..6}`.
- Growth: a(27)/a(26) = 6.8526 (6.821, 6.833, 6.843, 6.853).

T(27,16) = 27798973373501478242 is the second cell fixing P_11. It exceeds
2^64, so the row total needs the 128-bit counter, though per-state counts
stay near 40 bits.
