# r4-a — R4-1: is the committed `--modp` mode the residue binary LG-JOB-1 was blocked on?

SCOUT, 2026-08-12. No compute was run for this deliverable: it is reading,
`git show`, and arithmetic on numbers already on disk. The three sources were
compared with `diff -u` over `git show` output; nothing was built or executed.

**One caveat up front:** `experiments/tristruct/r4_a_modp_rowcheck.py`, the
RED-modp comparator this deliverable's job request calls, was written here and
**has never been run** — a scout runs no compute. Its first execution is part of
LG-JOB-1R and it should be exercised against a deliberately perturbed row before
its green is believed.

Line numbers below are for `7b13137:cpp/cutcount_b1.cpp`. **They are valid for
`48ac108` too** — the diff between the two is 33 lines in two hunks starting at
line 437 and line 491, so everything I cite (lines 1–436) is byte-identical in
both.

---

## 1. Verdict on R4-1

**PARTLY YES, and the part that is yes is bigger than expected.** The premise of
LG-JOB-1 — "a ~20-line residue-payload variant nobody has authored" — is **false
for the measurement job and true for the production ladder.**

- The **measurement job (LG-JOB-1R, §3) needs no C++ authoring at all.** The
  committed `--modp` mode runs at H ≤ 16, self-reports `peak_rss_mb` and
  `states=` in the exact obs format the ladder-gate's measurement recipe
  assumes, and can be validated against the recovered `C<H>.out` rows reduced
  mod p. Dispatchable tonight.
- The **production H=17..19 ladder does not unblock today.** Six items must be
  authored or changed (§2), one of which (`Succ out[12]`, §2.2) is a plausible
  stack-buffer overflow at exactly the heights the ladder wants.
- The mode's **payload is `uint32_t`, not `uint8_t`** (line 306). That single
  fact rewrites the cost table (§4) and answers the 8-bit/16-bit question: with
  the committed code the prime width **changes no code and changes no RAM**, so
  the right choice is 31-bit primes, which cuts the run count from 15 to 5.

### 1a. Same stencil, same transitions — yes, and by shared function, not by copy

`run_height_modp` (lines 303–360) calls exactly the same transition machinery as
the exact-payload `run_height` (lines 212–301):

| shared function | line | used by modp at |
|---|---|---|
| `successors(key, H, r, c, s)` | 151 | 317 |
| `gather` (the stencil: `r>0`, `r+1<H`, `H-2`, `H-1`, `H`) | 129 | via 156 |
| `shifted` / `canon` (key packing, relabel) | 144 / 110 | via 154–172 |
| `KeyHash`, `BITS=5`, `SLOTMASK` | 97–105 | 306 |

The header comment at line 124 already labels this block "shared by both modes".
There is no second stencil and no second weight table in the file. The
coefficient recurrence is also identical algebra:

    exact (253-255):   d0 += c0*m0 ;  d1 += c1*m0 + c0*m1
    modp  (338-342):   d0 = (d0 + c0*m0) % p ;  d1 = (d1 + c1*m0 + c0*m1) % p

and the column-boundary accounting (`fprev = fcur`, column sums, then
`C_H(n) = f_W(n) − f_{W−1}(n)`) matches: exact at 263–270 / 284–288, modp at
344–349 / 353–354. Same `W = Nmax+1` columns, same `n=1..Nmax` extraction.

**Overflow is safe as written.** Line 377 rejects `p >= 2^31`. Then
`c0*m0 < 2^62`, and the worst expression `d1 + c1*m0 + c0*m1` is bounded by
`2^31 + 2^62 + 2^62 < 2^64`. Signed `m0` (which is `−b`) is folded into
`[0,p)` at line 332 before use; `m1 ∈ {0,1}` at 333. No latent wrap.

### 1b. Self-checks — HALF the battery, and the missing half is the one the gate calls load-bearing

| check | exact path | modp path |
|---|---|---|
| `[q^0] C_H(n) = 0` | line 289, `FATAL q0_nonzero`, `exit(2)` | **line 355**, `FATAL q0_nonzero_modp`, `exit(2)` — present, but only mod p |
| `A_n(1)` = binomial identity | lines 275–295, `FATAL q1eval_binomial`, `exit(2)` | **ABSENT** |
| `selfcheck H=... q0_zero=OK q1eval_binomial=OK` log line | line 298 | **ABSENT** — modp logs nothing per height beyond `mode=modp H=` |

This is not cosmetic. The exact path carries a **third** coefficient
(`Payload.a[3n+2]`, declared line 209, `ST = 3` at 216) whose only purpose is the
q=1 all-subsets binomial identity, and `tests/gate_cutcount_b1.py`'s check C
describes it as "a full exercise of the transition weights with no connectivity
in it anywhere". `run_height_modp` uses `2*NA` slots (line 307) and drops that
coefficient entirely. **GREEN-3 of the ladder-gate §4 battery is unavailable in
residue mode as committed** — half of it (`q0_zero`) survives, the half that sees
the transition weights does not. §2.3 prices restoring it.

### 1c. Row format — compatible; the *comparison* is not

`run_height_modp` writes `"%d %llu\n"` (line 357) to a caller-named outfile —
byte-identical in shape to `--height`'s `"%d %s\n"` (line 390), which is what the
calib runner produced as `rows/C<H>.out`. So `--assemble` (396–441) will *parse*
modp rows without complaint: `parse_i128s` at 362 reads them fine.

**It will then compare them against exact banked values and report every cell as
a MISMATCH.** `--assemble` has no `p` argument and no reduction step (411–437).
Feeding it residue rows produces a fail-closed exit 2 — safe, but useless. §2.4.

### 1d. Fail-closed behaviour in 48ac108 — the modp path was not touched

48ac108's 33-line diff adds exactly two guards, both in *exact*-value compare
paths: `--assemble` returning 3 on a zero-cell comparison (48ac108:440–446), and
the same rule plus `rep.done` in the full-run path (48ac108:501–510). Neither is
reachable from `--modp`, which returns 0 at line 381 unconditionally after
`run_height_modp`. The modp mode's only fail-closed exit is the `q0_nonzero_modp`
`exit(2)` at line 355. `tests/gate_cutcount_b1.py` on that branch has **zero
`--modp` coverage** — checks A–G exercise only the exact paths.

So: correct as committed, within its declared limits, but under-checked. It is a
probe mode ("atom/BM probe", per its own usage line 28), not a production ladder
engine, and it is honest about that.

---

## 2. Gap list — what must be authored before a production residue ladder

Ordered by whether it blocks correctness or blocks scale. Sizes are my estimate
of the diff, not a measurement.

### 2.1 The `H > 16` guard — 1 line, but it needs a stated bound (BLOCKS EVERYTHING)

Line 377: `if (H > 16 || p >= (1ull << 31))`. H=17..19 is rejected outright.

The packing survives the raise, by inspection:
- key uses `BITS*(H+1) = 5*20 = 100` bits of a `u128` at H=19 (`shifted`, 144–147;
  `canon`, 110–121). Hard limit `5*(H+1) ≤ 128` → **H ≤ 24**.
- block ids after `canon` are ≤ `H+1 = 20`; `shifted` prepends `mx+1 ≤ 21`, which
  fits 5 bits (≤31); `int map[32]` / `int present[32]` are indexed by those ids.
  Hard limit **H ≤ 29**.
- the `uint32_t` state index (306, 335) holds 224.5M states at H=19 comfortably
  (it is tight but valid even at H=21's 2.23e9 < 2^32).

Change: raise to `H > 24`, with the two bounds in a comment, and add a
compile-time `static_assert`-style check for the successor buffer (2.2).

### 2.2 `Succ out[12]` — a stack buffer with no headroom at H=19 (POSSIBLE MEMORY BUG)

`successors` (151–174) writes `1 (empty) + b (join each live block) + 1 (fresh)`
entries into a caller-supplied `Succ out[12]`, with **no bounds check**. Callers
declare `Succ s[12]` at lines 189 (`census`), 230 (`run_height`) and 316
(`run_height_modp`).

`b` counts distinct live block ids among the H+1 window slots (165–169). The
window is `r` cells from column `c` plus `H+1−r` from column `c−1`; cells
adjacent within a column are king-adjacent, so distinct blocks must be
non-adjacent within each part, giving

    b <= ceil(r/2) + ceil((H+1-r)/2) <= floor((H+3)/2)

| H | bound on b | entries written | `out[12]` |
|---|---|---|---|
| 16 | 9 | 11 | fits (matches the source's own comment at line 96, "<= 9 for H<=16") |
| 17 | 10 | 12 | exactly full |
| 18 | 10 | 12 | exactly full |
| 19 | 11 | **13** | **overflows** |

The bound is ARGUED, not measured — cross-column king adjacency may merge blocks
and keep the real maximum lower. But `out[12]` has zero headroom from H=17 up and
the code has no guard, so this is a stack smash waiting on an unproven
inequality. Change: `Succ out[16]` at 151/189/230/316 plus an explicit
`if (n >= 16) abort()`, and settle the question by running `--states 17 19 41`
with an instrumented max-successor counter (queue row R4-A2, seconds of compute).

### 2.3 The binomial self-check in residue mode — +50% payload, or a documented waiver

Restoring GREEN-3 means carrying the third coefficient mod p: `ST = 3` in the
modp payload, `de = (de + ev*(m0+m1)) % p`, and a Pascal row computed mod p
(the exact path's `binom_rows` lambda, 275–281, ported to `uint32_t`). Roughly
25 lines. Cost: payload 656 B → 984 B per window, i.e. +50% RAM at every height
(§4 table).

The alternative — GREEN-3 at gate heights only, production runs on `q0_zero` plus
RED-D — is defensible but it is a *deliberate weakening of the gate battery the
ladder-gate §4 was written to enforce*, and the phase-2 brief has to say so in
those words rather than inherit the omission silently. **Lead's call; I recommend
carrying it, because §4 shows H=17 fits dalby with the third coefficient anyway.**

### 2.4 A mod-p compare path — ~12 lines of C++, or ~30 of Python (recommended)

`--assemble` needs a residue sibling. Two options:

- C++: `--assemble-modp <Hmax> <Nmax> <p> <rowdir> <banked_dir>`, which is
  `--assemble` (396–441) with `parse_i128s(val) % p` applied to the banked side
  and `T(n,H)` reduced mod p, keeping the 48ac108 exit-3 zero-cell guard.
- **Python, and this is the better answer for LG-JOB-1R:** the recovered
  `results/cutcount_b1/rows/C<H>.out` are *exact* `C_H(n)` for H=1..16. A
  comparator that reduces those mod p and diffs against the modp output needs no
  engine change at all, and checks `C_H` directly rather than the
  second-difference `T`, which is a strictly stronger row-level check.

### 2.5 CRT assembly + RED-D — new script, no engine change

Nothing in the engine reconstructs. Author
`experiments/tristruct/r4_*_crt_assemble.py`: read `C<H>.p<i>.out` for k primes,
CRT per (H,n), form `T = C_H − 2C_{H−1} + C_{H−2}`, compare against banked where
banked exists. `second-source:tests/gate_modp.py` already contains a correct
incremental `crt(residues, mods)` — lift it rather than rewrite it.

**RED-D** rides in the same script: reconstruct from k−1 primes, *predict* the
held-out k-th residue, and fail if it does not match. This is what forces k =
(primes needed for the bit budget) **+ 1**, and it is the only control in the
battery that tests the reconstruction rather than the DP.

Bit budget, from measured values: `C_H(40) ≤ 41·a(40)`, and summing
`results/triangle.txt` gives `sum_H T(40,H)` at **106 bits**, so
`C_H(40) < 2^112` for every H ≤ 40 — MEASURED anchor, loose bound. Directly
measured for comparison: `C_12(40)` is 105 bits, `C_14(40)` 106, `C_16(40)` 107.
Four 31-bit primes give 124 bits. **k = 4 + 1 held out = 5.**

### 2.6 A runner script with per-(H,prime) resume — ~40 lines of bash

`run_cutcount_b1_calib.sh` resumes on `[ -s rows/C$H.out ]`. The residue ladder
needs `rows/C${H}.p${P}.out` naming, a prime list, and the same skip rule.
Mechanical.

### 2.7 8-bit vs 16-bit vs 31-bit: **the committed code makes this a non-question**

The payload is `std::vector<uint32_t>` (line 307) regardless of `p`. So **prime
width changes no line of code and no byte of RAM** below `p < 2^31`. Narrowing to
`uint8_t`/`uint16_t` is a *separate* change (the payload vector type plus the
`% p` accumulator types, ~6 lines) that trades 2.1x–1.5x RAM against 3.2x/1.6x
more runs. §4 prices all of it. 61-bit primes are **not** a 6-line change: they
overflow the `u64` accumulator at 338–342 and need `__int128` mulmod plus a
`uint64_t` payload.

---

## 3. JOB REQUEST — LG-JOB-1R

Supersedes LG-JOB-1 in `results/triangle-r3-ladder-gate.md` §2. Every estimate
labelled. **The measurement no longer has an authoring prerequisite** — the only
new artifact is a ~30-line Python comparator, and even that is optional for the
RSS numbers.

    job id:            LG-JOB-1R  (supersedes LG-JOB-1)
    measures:          (a) bytes/window marginal RSS slope of the COMMITTED --modp
                       payload at H=12..16, and (b) us/slot-col wall of residue
                       arithmetic vs the measured I256 anchors on the same box.
                       (c) free-riding: a production-scale correctness check of
                       --modp at H=16 against exact banked rows.
    decides:           the whole H=17..19 routing table (§4 below). Confirms or
                       refutes the 926 B/window EXTRAPOLATION that currently says
                       H=17 fits dalby 5-way concurrent, H=18 is a 6-day job, and
                       H=19 is out of reach without a flat container. Also decides
                       whether narrowing the payload to u8/u16 (a real code change)
                       is worth doing before H=18.

    box:               dalby, and dalby specifically. RECOMMENDED because every
                       anchor this measurement is compared against -- the 8,143
                       B/window marginal slope, the 8,143-vs-7,872 overhead
                       residual, and all five walls -- was MEASURED on dalby with
                       this allocator, this libc and this ISA. Running the residue
                       slope on ayr (x86, different allocator behaviour) would
                       compare a new number against anchors from another machine
                       and make any difference uninterpretable. dalby also already
                       holds results/ns_a40/perheight and the C<H>.out oracle.
    cores:             1 (single-threaded; the marginal-slope method requires it)

    build:             # worktree, so dalby's untracked cpp/cutcount_b1.cpp (the
                       # 59e90660 working copy that produced the banked rows) is
                       # NOT clobbered
                       git -C ~/src/polyominoes fetch
                       git -C ~/src/polyominoes worktree add ~/src/pm-b1 48ac108
                       cd ~/src/pm-b1
                       sha256sum cpp/cutcount_b1.cpp     # MUST be 5ab04877...
                       make build/cutcount_b1
                       sha256sum build/cutcount_b1       # record: the gate receipt names this
                       python3 tests/gate_cutcount_b1.py # GATE RECEIPT, ~7 s, must be GREEN

    run:               P1=2147483647; P=(2147483647 2147483629 2147483587 2147483579 2147483563)
                       mkdir -p results/cutcount_b1/modp
                       # (a)+(b)+(c): the slope ladder, one prime, five heights
                       for H in 12 13 14 15 16; do
                         ./build/cutcount_b1 --modp $H 40 $P1 \
                           results/cutcount_b1/modp/C$H.p$P1.out
                       done
                       # CRT + RED-D rehearsal, cheap height, five primes
                       for p in "${P[@]}"; do
                         ./build/cutcount_b1 --modp 13 40 $p \
                           results/cutcount_b1/modp/C13.p$p.out
                       done
                       # (c) the correctness check: exact banked rows reduced mod p
                       python3 experiments/tristruct/r4_a_modp_rowcheck.py \
                         results/cutcount_b1/rows results/cutcount_b1/modp
                       (all of it under `tee` to
                        experiments/tristruct/r4_a_modp_bpw.log, tmux window on dalby)

    heights:           12, 13, 14, 15, 16 at p=2147483647 (four consecutive
                       marginal slopes, which is what exposes a rehash
                       discontinuity), plus H=13 at four more primes.

    wall estimate:     <= 7.2 h single-thread. MEASURED upper bound: the exact
                       I256 binary's own dalby walls for the same heights sum to
                       23,890 s = 6.64 h (calib_run.log: 158.5 + 503.4 + 1,618.6
                       + 5,134.5 + 16,475.2), plus 4 x 503.4 s = 0.56 h for the
                       extra H=13 primes. EXTRAPOLATED: residue arithmetic should
                       be several-fold cheaper than 4-limb I256 -- but it pays a
                       64-bit `%` per coefficient per slot, so I do not estimate a
                       speedup. Measuring it is output (b).
    RAM estimate:      peak <= 6.8 GiB at H=16. EXTRAPOLATED from 926 B/window
                       (see §4) x 7,832,667 windows. MEASURED hard ceiling: the
                       exact binary hit 60,827 MiB at the same height, and the
                       residue payload is strictly smaller, so this cannot exceed
                       59 GiB under any container assumption.
    disk estimate:     < 1 MB (9 row files of 40 lines + the log)
    interruptible:     yes -- one file per (H, prime); a kill costs at most the
                       height in flight. Nothing else on dalby is touched.

    RED controls riding along:
      RED-gate  the gate receipt above (checks D/E/G of tests/gate_cutcount_b1.py:
                perturbed banked cell -> exit 2 and names the cell; empty banked
                dir -> exit 3; missing C_H row -> exit 1). Must be GREEN before any
                RSS number is believed. Note it covers the EXACT paths only --
                there is no --modp gate coverage on the branch (§1d), which is why
                RED-modp below exists.
      RED-modp  the H=16 row check (c): every one of the 40 values of
                `C_16(40) mod p` from --modp must equal the recovered exact
                C16.out reduced mod p. This is a NEW control the original
                LG-JOB-1 did not have and could not have had: the recovered rows
                give a per-height oracle up to H=16, so the residue path is
                validated at 7.8M states -- production scale -- not just at the
                gate's H<=10. Its RED half: perturb one line of the modp output
                and confirm the comparator reports exactly that (n,H).
      RED-D     the CRT control, rehearsed at H=13: reconstruct C_13(n) from four
                of the five primes, predict the fifth residue, and fail if it
                differs. Exercises the reconstruction code end to end at a height
                where the exact answer is also known.
      identities  `q0_zero` fires per height in modp (line 355, exit 2).
                The q=1 binomial identity does NOT (§1b) -- record that as a
                known gap in the receipt rather than letting the log's silence
                imply it passed.

    changes if:        slope <= ~200 B/window  -> the payload dominates as modelled;
                                                  narrowing to u8 buys the full 2.1x
                                                  and H=19 becomes arguable.
                       ~200-350 B/window       -> as extrapolated; §4's table stands.
                       > 350 B/window          -> the container, not the payload, is
                                                  the cost; narrowing the payload is
                                                  wasted work and the only lever left
                                                  is a flat open-addressed table.
    closes:            R4-1's cost half, and the synthesis's go/no-go NOT ESTABLISHED
                       (the "104 B/window" model number, which §4 shows is wrong on
                       its own terms).

---

## 4. What this changes about the H=17..19 plan

Three corrections, compounding. All of them make the ladder more expensive, and
the third one is the discovery that pays for it.

### 4.1 The ladder-gate's residue model is off by a factor of 2 on its own convention

`r3_adv_window_census.log` line 34 states the model as "41 area slots x bytes(m)
x 2 buffers", then gives 104 B/window for an 8-bit prime = 41 x 1 x 2 + 22. **It
counted one coefficient per area slot.** The DP carries two (`c0`, `c1`) and the
exact path's own model in the same log counts three (41 x 3 x 32 x 2 = 7,872).
So the correct 8-bit figure is 41 x **2** x 1 x 2 = 164 B payload, and the 63-bit
figure is 1,312 B, not 678.

### 4.2 The committed payload is u32, and the measured container overhead is 270 B

Payload = `coeffs x 41 slots x sizeof(word) x 2 buffers`. Container overhead is
**MEASURED at ~270 B/window** — the ladder-gate's own H=15→16 marginal slope of
8,142 B minus the 7,872 B exact payload. It is the same `unordered_map` +
per-state heap vector in both modes, so it carries.

| variant | code state | B/window |
|---|---|---|
| **committed `--modp`** (2 coeff, u32) | ships today | **926** |
| + binomial self-check (3 coeff, u32) | §2.3, ~25 lines | 1,254 |
| narrowed u16 (2 coeff) | §2.7, ~6 lines | 598 |
| narrowed u8 (2 coeff) | §2.7, ~6 lines | 434 |
| narrowed u8 + self-check (3 coeff) | both | 516 |
| flat open-addressed table, u8, 2 coeff | a rewrite, not a diff | ~180 |

RAM per run, GiB, = exact census x B/window (EXTRAPOLATED from the MEASURED 270 B
overhead and the MEASURED exact censuses). Boxes: ayr 77 GiB, dalby 121 GiB
available, both checked 2026-08-12 in the ladder-gate.

| H | windows | committed u32 | +selfcheck | u16 | u8 | u8+sc | flat u8 |
|---|---|---|---|---|---|---|---|
| 17 | 23,681,423 | **20.4** | 27.7 | 13.2 | 9.6 | 11.4 | 4.0 |
| 18 | 72,487,711 | **62.5** | 84.7 | 40.4 | 29.3 | 34.8 | 12.2 |
| 19 | 224,529,648 | 193.6 | 262.2 | 125.1 | **90.8** | 107.9 | 37.6 |
| 20 | 703,470,478 | 606.7 | 821.7 | 391.9 | 284.3 | 338.1 | 117.9 |

### 4.3 The run count: 5, not 2 — and that is still the good news

The ladder-gate's Piece 1 priced H=17..18 as **two** 61-bit-prime runs. Two
problems: 61-bit primes overflow the committed accumulator (§2.7) and two primes
leave no held-out prime for RED-D. With the committed code and 31-bit primes,
the bit budget (§2.5) needs 4 + 1 = **5 runs**, i.e. 2.5x the wall the gate
priced — bought in exchange for zero C++ authoring on the arithmetic.

Wall per run per height, MEASURED-anchored upper bound (the exact I256 walls on
dalby, scaled by `windows x H`, which reproduces the observed 3.21 per-height
ratio to three digits): **H=17 ≤ 14.7 h, H=18 ≤ 47.7 h, H=19 ≤ 156 h** per
thread per prime. Residue arithmetic should beat this; by how much is LG-JOB-1R
output (b).

Routing, on the committed code plus §2.1/§2.2 (the two changes that are not
optional):

- **H=17 is a one-night job on dalby, and this is the headline.** Five runs at
  20.4 GiB = 102 GiB against 121 GiB available — **all five primes concurrently**,
  so the wall is one run's wall: **≤ 14.7 h**, likely well under. With the
  binomial self-check restored (27.7 GiB), four fit on dalby and the fifth on
  ayr — same wall. 9.06% of a(40).
- **H=18 is a ~6-day job.** 62.5 GiB/run allows one concurrent run per box; five
  runs across ayr + dalby is three waves x 47.7 h ≈ 143 h. Narrowing to u16 does
  not help (8 primes at 40.4 GiB = three waves too). 7.42%.
- **H=19 does not fit any plan priced from measured anchors.** The only in-RAM
  variant is u8 (90.8 GiB, dalby only, one at a time), and u8 needs 16 runs:
  16 x 156 h ≈ **104 days serial**. A flat container (37.6 GiB, three concurrent
  on dalby) still gives six waves x 156 h ≈ **39 days**. Neither is a phase-2
  job. H=19 needs either intra-run parallelism (still ASSERTED, nobody has run
  this DP multi-core) or a different idea. 5.72%.
- **H=20/21 are unchanged and remain out.**

**So the achievable band this quarter is H=17 — one night — and H=18 — one
week — for 16.48% of a(40), taking the two-source total from 21.64% to 38.12%.**
H=19 should be treated as a separate open problem, not as the tail of a ladder.

### 4.4 One thing the discovery makes strictly cheaper

The recovered `C<H>.out` rows are an exact oracle at every height up to 16. Any
residue binary can now be validated at H=16 — 7.8M states, production scale —
before it is trusted at H=17. Before the recovery, the deepest available
cross-check was the gate's H ≤ 10 (13,733 states). That is a 570x increase in the
state count at which the residue path is checked, at the cost of one H=16 run,
and it is folded into LG-JOB-1R as RED-modp.

---

## NOT ESTABLISHED

- **The residue binary's actual bytes/window and us/slot-col.** Everything in §4
  marked EXTRAPOLATED rests on the 270 B container overhead carrying from the
  I256 payload to the u32 payload. It is the same container by inspection, but
  allocator behaviour at a 328 B allocation is not the same as at 3,936 B.
  LG-JOB-1R measures it.
- **The exact maximum of `b` in `successors`.** My `floor((H+3)/2)` bound is
  ARGUED from king-adjacency within a column; cross-column merging may make the
  real maximum smaller and `out[12]` safe through H=19. Seconds of compute
  settles it (R4-A2) and it must be settled before any H ≥ 17 run.
- **Whether residue arithmetic is faster or slower than I256 per slot-col.** The
  `%` operator is the wildcard. I refuse to guess; every wall in §4 is the
  measured I256 anchor used as an upper bound.
- **Whether this DP shards across cores.** Still ASSERTED, unchanged from round
  3. Every H=18/19 wall above is single-threaded. If it shards, H=18 collapses
  and H=19 becomes arguable; that is the highest-leverage unknown left in the
  ladder and it is a separate job.
- **`C_H(40)` bit lengths above H=16.** I used the bound `41 x a(40) < 2^112`
  from the banked triangle; the measured values at H=12/14/16 (105/106/107 bits)
  suggest the true H=19 figure is ~108, so the 4-prime budget has ~16 bits of
  slack. I did not compute the true value.
- **Whether dalby's RAM and disk are free at phase-2 time.** Checked 2026-08-12
  only, in the ladder-gate.
