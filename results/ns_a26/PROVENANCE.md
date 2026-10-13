# a(26)

a(26) = 102607513847014153892

Computed 2026-07-02 on dalby at revision `246cb09`, 80 cores, 4066.5 s of
wall, 128-bit counter (the first term past the 64-bit range). Heights 1..15
enumerated, with H = 15 most of the cost; heights 1, 2 and 16..26 from the
closed forms (P_9 and P_10 newly in use).

Files: `triangle.txt`, `perheight/h{1..26}.out`, `cost_profile.tsv`.

Checks:

- a(1)..a(20) match `fixtures/b006770.txt`; a(21)..a(25) match
  `results/ns_a2{1..5}`.
- Growth: a(24)/a(23) = 6.821, a(25)/a(24) = 6.833, a(26)/a(25) = 6.8429.

T(26,15) = 5614506356004078534 is one of the two cells needed to fix P_11
(the other is T(27,16) from the a(27) run).

A first summation of the per-height rows used a stale `combine` binary that
still added in 64 bits and gave a value smaller than a(25); the growth
check caught it, the binary was rebuilt, and the rows themselves were
unaffected.
