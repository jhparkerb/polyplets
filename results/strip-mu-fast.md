# The indexed-array strip engine — mu_H at H=16 in minutes

Date: 2026-07-31. Companion to
[strip-growth-lambda-bounds.md](strip-growth-lambda-bounds.md) (the `mu_H` ladder
and the lambda claim) and [strip-mu-certificates.md](strip-mu-certificates.md)
(what promotes a `mu_H` to a machine-checkable rational). This note covers only
the **engine**: the build increment that
[strip-growth-lambda-bounds.md](strip-growth-lambda-bounds.md) named as missing
("needs an indexed-array rewrite of the same logic (per-stage sparse
operators)"), and what it measures out at.

Tool: `cpp/strip_mu_fast.cpp` + `cpp/strip_stage_ops.h` -> `build/strip_mu_fast`
(`make build/strip_mu_fast`). Gate: `make gate-strip-fast` (~10 s, also in
`make gates`). The map engine `cpp/strip_mu_kink.cpp` stays in the tree, built
and gated, as the cross-check.

## Where the old engine's time went (measured, not assumed)

`cpp/strip_mu_kink.cpp` holds every intermediate stage of the column sweep in an
`unordered_map<Sig, double>` and re-derives the kink transition for every state
on every matvec. Splitting one sweep into "transition + map accumulate" versus
"transition only, same states, no map writes" (`sample` plus a direct
instrumented A/B, H=10 and H=11):

| H | emits/sweep-state | full | transition only | map share | ns per emit |
|---|---|---|---|---|---|
| 10 | 1.96 | 0.356 s | 0.222 s | 37.7% | 83.9 |
| 11 | 1.96 | 0.568 s | 0.359 s | 36.8% | 90.5 |

So the hash map is **37%** of the sweep — and the other 63% is the union-find,
`canonMixed` and hash-bucket walk that produce the *same answer every time*. The
bottleneck is not the map specifically; it is that ~100% of the sweep recomputes
a fixed graph. `sample` agrees on the split (of 15116 main samples at H=11, 5369
land unambiguously in `__emplace_unique_key_args` / `operator new` / `free`).

Per-emit cost is nearly flat in H (83.9 -> 90.5 ns), so the old engine's ~3.4x/H
was almost entirely state growth, not per-state degradation.

## The rewrite

`cpp/strip_stage_ops.h` enumerates the layered state graph **once** per H and
freezes it:

- `S_0` — the boundary states (H canonical label bytes, flags zero); exactly the
  key set the map engines' vectors converge to.
- `S_1 .. S_H` — the mixed states after stages `0..H-1` (row bytes, carry byte
  `b[H+2]`, touch flags, nonempty flag).
- `t0[r]`, `t1[r]` — for each `i` in `S_r`, the index in `S_{r+1}` of the "no
  cell" and "cell placed" successor, or `-1` where the kink transition suppresses
  it. A stage emits at most two successors per state, so the sparse operator is
  **two int32 arrays, not CSR**.
- `fin` — for each `i` in `S_H`, the `S_0` index it finalizes to, or `-1` (empty
  column = completion, or a stranded outgoing label).

A matvec is then H flat scatter passes plus one finalize pass: no hashing, no
union-find, no signature byte touched. The enumeration is a layered BFS with a
per-stage watermark, so every state is expanded exactly once and building the
tables costs about one symbolic sweep — which thousands of matvecs amortize away.

Two things make it a shared kernel rather than a second engine:

- `applyOps` is templated on the value type and a **weight policy**, so the float
  power iteration (`double`, weight `x`) and the certificate's exact check
  (`unsigned __int128`, `floor(v*p/q)` with a 2^126 guard) drive the *same* frozen
  operator over the *same* frozen state set. A policy may fail (overflow);
  `applyOps` then returns false and the caller must treat that as a failed
  certificate — fail-closed, never a silent wrap.
- The enumerator's state store is a flat open-addressing interner over keys packed
  to `H+4` bytes. An `unordered_map<Sig,int32>` costs ~165 bytes per state
  (measured, H=14: 1.36 GB peak); the packed interner costs ~60 (530 MB), and
  since the build holds every stage live at once, that difference is what keeps
  H=16 a memory question rather than a memory wall.

## Old vs new (same box, single core, gympie)

`mu_H` and state counts are **identical**, to every printed digit:

| H | states | `mu_H` | old `strip_mu_kink` | new `strip_mu_fast` | speedup |
|---|---|---|---|---|---|
|  9 |   2187 | 5.8404579 |   8.7 s | 0.05 s | 174x |
| 10 |   5797 | 5.9916958 |  29.8 s | 0.16 s | 186x |
| 11 |  15510 | 6.1158416 | 107.5 s | 0.51 s | 211x |
| 12 |  41834 | 6.2191246 | (not run) | 1.7 s | — |

And against the certificate tool, which does the same float phase plus the exact
check (`--verify` runs the identical arithmetic over the frozen operators):

| H | `strip_mu_cert` wall | `strip_mu_fast --verify` | speedup |
|---|---|---|---|
| 11 | 120.9 s | 0.5 s | 242x |
| 12 | 393.5 s | 1.7 s | 231x |

Every published certificate `H=2..12` re-verifies: `result=PASS` at the certified
numerator and `result=FAIL` at numerator+1, with `vrange_bits` and `acc_bits`
reproducing the receipts exactly (24.1 / 39.7 / 44.8 / 52.5 / 57.5 at H=8..12,
`acc_bits` 96.5-96.7) and `min_ratio` agreeing to 8-9 digits (the last digit moves
because the float phase sums in index order rather than hash order).

## Cost model (measured through H=16)

Throughput is measured directly with `--bench` (a fixed small number of matvecs at
one x, no `mu_H` solve) so the H>=15 projection does not have to guess whether the
indexed scatter falls off a cache cliff. **It does not** — the frozen tables grow
from 7.5 MB at H=12 to 564 MB at H=16 and the per-stage-state cost moves 0.89 ->
0.95 ns:

| H | states | sum \|S_r\| | table | build | build RSS | float ns/state | exact ns/state | float matvec | exact sweep |
|---|---|---|---|---|---|---|---|---|---|
|  9 |     2187 |     36,575 |   0.3 MB |  0.0 s |       | 0.80 | 7.46 |        |        |
| 10 |     5797 |    108,182 |   0.9 MB |  0.0 s |       | 0.87 | 7.29 |        |        |
| 11 |    15510 |    319,492 |   2.6 MB |  0.1 s |  17 MB| 0.86 | 7.24 | 0.0003 s | 0.002 s |
| 12 |    41834 |    942,747 |   7.5 MB |  0.2 s |  45 MB| 0.89 | 7.46 | 0.0008 s | 0.007 s |
| 13 |   113633 |  2,780,660 |  22.2 MB |  0.5 s |       | 0.86 | 7.44 | 0.0024 s | 0.021 s |
| 14 |   310571 |  8,200,480 |  65.1 MB |  1.8 s | 530 MB| 0.85 | 7.54 | 0.0070 s | 0.062 s |
| 15 |   853466 | 24,185,132 | 191.6 MB |  6.5 s | 1.36 GB| 0.87 | 7.64 | 0.0210 s | 0.185 s |
| 16 |  2356778 | 71,339,063 | 563.9 MB | 23.2 s | 4.94 GB| 0.95 | 7.86 | 0.0680 s | 0.561 s |

`sum |S_r|` grows a very steady **2.95x/H** (2.950, 2.949, 2.949, 2.950, 2.950
across H=11..16) and the boundary state count 2.71x/H. Build RSS is a transient:
after the enumeration only the int32 tables and the `S_0` signatures stay live
(~0.7 GB at H=16).

Matvec counts per solve are 1311 / 1471 / 1627 / 1755 at H=9..12, i.e. +~140 per
H (the bisection is fixed at 55 steps; the growth is power-iteration steps as the
spectral gap narrows). Extrapolating that linearly is the only fitted quantity in
the projections below; everything else is measured.

### Projected wall (single core, this box)

    float solve      = build + matvecs(H) x float_matvec_s(H)
    certificate      = float solve x 1.13 (the cert's tighter 1e-13 tolerance,
                       measured at H=11: 120.9 s vs 107.5 s) + exact sweeps

| H | matvecs (fitted) | **float solve** | **certificate** (1 sweep / 40-sweep search) |
|---|---|---|---|
| 13 | ~1890 |   4 s |   5 s / 6 s |
| 14 | ~2020 |  16 s |  18 s / 21 s |
| 15 | ~2150 |  52 s |  58 s / 65 s |
| 16 | ~2280 | 3.0 min | 3.4 min / 3.8 min |

For scale, the paragraph this replaces projected **~12 h** for the H=16 float
solve on the map engine, and `strip_mu` (the all-column engine) could not reach
H=16 at all. H=17 projects to ~1.7 GB of tables, a ~14.5 GB build peak and ~9 min
— reachable, but that is an extrapolation of the memory curve, not a measurement.

## RED-first gate (`--selftest`, `make gate-strip-fast`)

A 200x engine is exactly the circumstance in which a silently-wrong operator table
goes unnoticed, so the gate pins it against things it cannot influence:

- **A.** `mu_2 = 1 + sqrt(2)`, independent of everything in the program.
- **B.** Boundary state counts H=2..8 match the banked ladder (3, 8, 20, 50, 126,
  322, 834).
- **C.** Dropping the heaviest-carrying "cell placed" edge at each of the first
  three stages must move `mu_6` — all three do. The edge is chosen *by mass under
  the converged eigenvector*, because an edge that carries none (the empty seed's,
  for one: nothing ever finalizes back to the empty boundary) legitimately does
  not move `mu`, and demanding otherwise would make the check a coin flip.
- **D.** Dropping one finalize edge must move `mu_6` — it does (5.0687009 vs
  5.1153245).
- **E.** The exact kernel must PASS `mu_2 >= 2.4142135` and FAIL `>= 2.4142136`.
- **F.** The all-zero vector satisfies `A v >= v` vacuously and must be refused.

Then `tests/gate_strip_fast.py` compares the two engines head to head at H=2..8
(same `mu_H` string, same state count) and brackets every published certificate
H=2..8 (PASS at the numerator, FAIL at numerator+1), and checks the CLI refuses
bad arguments rather than clamping them.

Demonstrated, not assumed: reverting one line of the copied kink transition
(`if (r > 0) uadd(s.b[r - 1])` -> never) makes the gate fail loudly — state counts
go 3,8,20,50,126,322,834 -> 4,13,39,124,394,1283,4250 and every `mu_H` moves. The
corruption was then removed and the gate re-run green.

## Adopting the kernel in `strip_mu_cert`

Not done here, deliberately: a certificate run
(`scripts/run_strip_mu_cert_h14.sh`) was live on the box, and editing
`cpp/strip_mu_cert.cpp` arms `make gates` / `make ns-gate-fast` to relink
`build/strip_mu_cert` out from under a running job. The change is small and
mechanical, and `strip_mu_fast --verify` is the working reference for every part
of it — same arithmetic, same frozen operators, reproducing the receipts:

1. `#include "strip_stage_ops.h"`; delete the file's verbatim `canonMixed` /
   `labelInMixedState` / `kinkStageTransition` copy (the header has it, in
   `namespace strip`).
2. `Vec` / `IVec` become `std::vector<double>` / `std::vector<u128>` dense over
   `S_0`. `matvecF` and `matvecExact` are both replaced by `strip::applyOps` with
   `FloatWeight` / `ExactWeight`; `matvecExact`'s `maxAcc` out-parameter becomes
   `ExactWeight::maxAcc`, and its `return false` on overflow becomes `applyOps`
   returning false. The `keep` parameter of `matvecF` disappears — it is already
   dead (`certifyH` passes `nullptr` at every call site), and the dense vector over
   `S_0` *is* the restriction to `S` that `matvecExact`'s `if (!v.count(t))`
   implements.
3. `quantize`, `checkCert` and `vectorChecksum` index by position instead of by
   `Sig`; the checksum still sorts by raw signature bytes, using
   `StageOps::boundary[i]`, so receipts stay comparable across the change.

One behavioural note for whoever lands it: `S_0` also holds the empty seed
boundary, which no finalize edge targets, so the dense vector is one entry longer
than the `states` the receipts record and that entry is identically zero.
`checkCert` already skips zero entries (`0 <= anything`), so the certificate is
unchanged — but the receipt's `states` must keep reporting `StageOps::states()`
(the in-edge-reachable count), not the vector length, or the published table
shifts by one.

## Honest scope

- The engine computes the same thing the map engine does, by the same
  mathematics; nothing here changes what is *proved*. The certificates remain the
  load-bearing artifact ([strip-mu-certificates.md](strip-mu-certificates.md)).
- The kink transition is still a verbatim copy of `core/kink.h` (now in
  `namespace strip`, so a TU with its own copy can include the header). Three
  copies of it now exist in the tree — this one, `strip_mu_kink.cpp`'s and
  `strip_mu_cert.cpp`'s; adopting this header in both drivers would collapse that
  to one.
- `int32` indices cap a single stage at 2^31 states; the largest stage at H=16 is
  ~5.2M, and at 2.95x/H that ceiling is ~H=25.
- The projections above are wall-clock arithmetic over measured throughputs and
  one fitted quantity (matvec count per solve). They have not been confirmed by an
  actual H>=13 solve — that is the orchestrator's to schedule.
- `vrange_bits` (the precision budget the certificate spends) is measured at 44.8
  / 52.5 / 57.5 for H=10/11/12, increments +7.7 / +5.0 — running *below* the
  loose extrapolation in [strip-mu-certificates.md](strip-mu-certificates.md)
  ("H=14 range near 76 bits"). At `vbits = 96` the smallest entries would still
  sit around 2^35 at H=16 on that trend. If the range does run ahead, the failure
  mode is bounded and already handled: the numerator search absorbs it as lost
  digits, never as a wrong claim.

## Reproduce

    make build/strip_mu_fast
    make gate-strip-fast                                   # ~10 s, RED arms included
    ./build/strip_mu_fast 2 12                             # the ladder, ~4 s
    ./build/strip_mu_fast --verify 12 62191246 10000000    # re-check a certificate
    ./build/strip_mu_fast --ops 12 16                      # table sizes / memory
    ./build/strip_mu_fast --bench 14 16 --iters 20         # throughput probe
