# modp_recover bottleneck analysis (2026-06-23)

Profiled per-phase, after the H=11 run took 15h. My initial guess (BM is the
bottleneck) was WRONG; measurement (experiments/profile_modp.py) gives:

per-prime times, scaling fit over H=8,9,10:
  sweep (C++ build/gf_modp) ~ N^2.76     bm (Python, O(N^2)) ~ N^2.04
H=11 (N=26792, ~133 primes) wall breakdown:

  phase             ~wall    nature                       fix
  ----------------  -------  ---------------------------  -----------------------------
  C++ sweeps        ~7.0h    C++, 8-way parallel          run WIDER (32-80 way) -> ~1-2h
  P-reconstruction  ~4.6h    Python, redundant bignum %p  hoist Q%p + parallelize -> ~4m
  Berlekamp-Massey  ~1.5h    Python, was SERIAL           parallelize -> ~0.2h
  find_order        ~0.8h    serial single-prime sweeps   minor; leave
  CRT(Q) + validate ~few m   bignum (C-backed)            negligible
  (sum ~= the 15h observed)

KEY FINDINGS
- BM is NOT the bottleneck (1.5h, and bm/sweep shrinks with H: 0.19->0.11->0.05).
  Fast-BM (O(N log^2 N)) would shave the small term and leave the 7h sweep -- not worth it.
- The C++ sweep dominates (7h) and is ALREADY C++; the lever is parallelism WIDTH
  (gympie ran 8-way; dalby 80-core / ayr 32-core cut it to ~1-2h). Not a language issue.
- HIDDEN #2: P-numerator reconstruction recomputed `Q[i] % p` (a ~1200-digit bignum mod)
  inside the k x prime x i triple loop ~1.2e10 times = ~4.6h. A pure-Python perf bug.

FIXES APPLIED (gf/modp_recover.py; validated: H=6 normal + H=8 forced-growth both
recover P+Q byte-identical to the known-good file):
1. P-reconstruction: pre-reduce Q mod p ONCE (pconv_modp), then convolve small ints,
   PARALLEL across primes. ~4.6h -> ~4min (measured 9x from the hoist alone + ~8x pool).
2. Berlekamp-Massey: parallelized across primes (was serial). ~1.5h -> ~0.2h.
3. (earlier) adaptive prime growth + conditional clear (correctness, not speed).

NOT a code fix, but the biggest single win: run the recovery on a WIDE box with high
POLY_MAX_WORKERS (dalby/ayr) so the 7h sweep phase parallelizes to ~1-2h. Net H=11
expected ~3h on a wide box (was 15h on gympie 8-way).

Verdict on "rewrite in C++": no. Compute that matters (sweeps) is already C++; the
Python parts were either glue or had an algorithmic/parallelism bug now fixed. Reach
for fast-BM or a C++ BM only if BM ever profiles as dominant -- it doesn't at H<=11.
