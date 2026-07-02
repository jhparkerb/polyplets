# a(26) — provenance

**a(26) = 102607513847014153892**  (new frontier term)

- **Computed:** 2026-07-02, dalby-solo, `scripts/dalby_a26.sh`, rev `246cb09`.
  orchestrate PID 2086881, tmux `0:a26`, waiter `bbxvuyztq`. Wall **4066.5s
  (~68 min)** on 80 cores. u128 counter (first term past the u64 a25 ceiling).
- **Shape:** real sweep H1–15 (top real H15, the maxn=26 monster ~91% of cost);
  closed-form injection H16–24 (P9/P10 diagonals) + pole H25 + top H26 + low
  H1,H2. First run on the widened big.Int result pipeline.
- **Validation:**
  - a(1)–a(20) byte-match `fixtures/b006770.txt` exactly.
  - a(21)–a(25) match the certified `results/ns_a2{1..5}` values exactly.
  - growth a26/a25 = **6.8429**, continuing the trend (a24/a23=6.821,
    a25/a24=6.833) — monotone, no anomaly.
- **Byproduct:** T(26,15) = 5614506356004078534 → closes one of P11's two
  remaining equations (the other comes from a27's T(27,16)).
- **Tier:** computed, single-source. Pending certification (independent-ISA
  re-sweep + mod-p overflow guard + g2 low-height, per the a25 recipe;
  see docs/next-system/designs/13-fast-frontier-verification.md).

## STALE-BINARY NEAR-MISS (process lesson)

The first `combine` run reported a(26) = 10373793478466395812 — *smaller than
a(25)*, an obvious impossibility caught by the monotone-growth sanity check.
Cause: the `combine` binary on dalby was **stale** (pre-`1a0ac2d` big.Int
widening) and summed the row in u64, wrapping a26 (~1.03e20) mod 2^64. The
per-height data was correct all along (u128, full precision); only the summation
binary was old. Fix: rebuilt `combine` on dalby, re-ran → correct value.

**Lesson:** "rebuild remote after engine edit" must include `combine`, not just
orchestrate + workers. a26+ is the first regime where a stale u64 combine
silently corrupts — a25 and below fit u64 so the bug was invisible. See the
follow-up guard task.
