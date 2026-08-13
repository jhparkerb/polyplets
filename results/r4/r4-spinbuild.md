# r4-spinbuild — the spin-basis parity engine in C++, written and UNCOMPILED

Round 4 builder, 2026-08-12, gympie. Governed by `docs/triangle-round4.md`.
Artifact: `experiments/tristruct/r4_spin_engine.cpp`, 1113 lines.

**Every claim below is about source that has never been compiled and never been
run.** I am forbidden to build or execute anything; the lead does that. Nothing
here says the engine is correct or works. What it says is what the code is
supposed to do, where the two implementations could come apart, and what the
gate would look like if it were run.

**Verdict in one line: the port is written, dense-ranked, fail-closed and
instrumented, and it makes one structural departure from the Python reference
that everything else rests on — the Python is a whole-column transfer and this
is a cell-at-a-time kink sweep, because the whole-column kernel is priced out at
~4.646^m transition pairs. Section 3 is the argument that the two compute the
same Z, and it is an argument, not a measurement.**

---

## 1. What I wrote, function by function against the Python

The specification is `experiments/tristruct/r3_spin_pipeline.py` (28/28 cells at
n ≤ 7 against a self-grown union-find grower, exact N_H spot checks to
N_4(6) = 821,380, RED battery). Where the prose in
`results/triangle-r3-spin.md` and `results/r4/r4-inv.md` disagrees with the
Python, the Python governs; the one place it does (harvest granularity) is
called out in §3(a).

| Python | C++ | correspondence |
|---|---|---|
| `E, A, B = 0, 1, 2` | same literals | identical alphabet, identical encoding |
| `clash(x,y)` | `clash(int,int)` | identical predicate, character for character |
| `valid_columns(m)` | not materialized | the same predicate ("no clash between vertically adjacent occupied cells") becomes two things: the N-check inside the transition, and the adjacency of the ranking language `L_{m+1}` |
| `z_table(w,m,deltas)` | `run_m()` | **the structural departure.** Python: precompute `succ[s]` per whole column, one transfer per column. C++: m stages per column, one cell each. §3(a) |
| `z_table`'s per-state `{n: coeff}` dict | `Buf{vector<u64> lo, vector<u32> hi}` | exact ints → 2-bit mod-4 lanes, one lane per area slot 0..nmax, split u64 (slots 0–31) / u32 (slots 32–47) |
| `poly[n] += v`, `tgt[n+da] += v` | `add4()` and the `<< 2` lane shift | `add4(a,b) = (a^b) ^ (((a&b)&0x5555…)<<1)` is lane-wise mod-4 addition; area advance is a two-bit left shift with cross-word carry |
| `harvest(st)` | the column-boundary sum loop in `run_m` | sum of all payloads → `Z[w][n]` mod 4 |
| `zs[0] = {0: 1}` | `Z[0][0] = 1` | identical |
| `aval(n,m,w) = zs[m][w] - zs[m][w-1]` | the `A[m][n]` / `Astab[m][n]` block in `main` | identical formula, mod 4 |
| `nn(w) = aval(H) - 2 aval(H-1) + aval(H-2)` | `g` / `gs` in `main` | identical; `-2a ≡ +2a (mod 4)` so the code adds |
| `assert g % 4 == g_stab % 4` | `if (g != gs) struct_fail++` | same check; **exit 76 on a clean run**, recorded-not-fatal under a RED so the flip set is still measurable |
| `assert g % 2 == 0` | `if (g % 2) struct_fail++` | same |
| `res[(n,H)] = (g // 2) % 2` | `cells.push_back({H, n, (g%4)/2})` | identical, since g is even and known mod 4 |
| `deltas` argument (`FULL`, `(0,1)`, `(-1,0)`, `(0,)`) | `--mutant none / drop-nw / drop-sw / rook` | §1.1 below |
| `brute_z`, `brute_G`, `grow_animals` | **not ported** | the C++'s ground truth is the 640-cell B1 oracle instead. This is a real gap: the binary carries no self-contained independent truth. See §3(k) |

### 1.1 The stencil, which is the one thing shared with the production engines

The Python's cross-cut loop is, for a new-column cell at row `r` against old
column `s`: `for d in deltas: rr = r + d; if clash(s[rr], sp[r]): reject`.
So with the new column to the east of the old:

| `d` | old-column cell | compass | Python label | dropped by |
|---|---|---|---|---|
| −1 | `s[r-1]` | NW | the file's own comment says "−1 = NW" | `drop-NW = (0,1)` |
| 0 | `s[r]` | W | — | nothing (see below) |
| +1 | `s[r+1]` | SW | "+1 = SW" | `drop-SW = (-1,0)` |

and `rook = (0,)` drops both diagonals. Within-column (N) validity is enforced
by `valid_columns` **regardless of `deltas`**, in both the Python and here. The
C++ mirrors this exactly: `clash(nb_n, v)` is unconditional, `use_nw()` and
`use_sw()` gate the two diagonals, and W is never droppable.

W is never droppable for a reason that is not aesthetic: the dense index space
*is* the language of the Hamiltonian path through the frontier, and one of that
path's edges is the W-adjacency at row r−1. A mutant that dropped W would put
reachable states outside the array. `Config::use_w()` enumerates the mutants
exhaustively and `main` aborts (exit 78) if it ever returns false — so a future
mutant that drops W trips a guard instead of silently corrupting the ranking.

### 1.2 The kink layout, and why the transition is an overwrite

When the cell about to be placed is (x, r), the live frontier is exactly the
m+1 cells `{(x,j) : j < r} ∪ {(x-1,j) : j ≥ r-1}` — the same set
`r3_spin_counts.py:window_cells(m,r)` enumerates. Written in row order with the
carry cell (x−1, r−1) spliced in at index r:

    u = ( (x,0) … (x,r-1), (x-1,r-1), (x-1,r), … (x-1,m-1) )

Every consecutive pair of `u` is king-adjacent, for every r: pairs inside column
x and inside column x−1 are vertical, the pair at index (r−1, r) is the W
adjacency at row r−1, and the pair at (r, r+1) is vertical in column x−1. So
`u` is a Hamiltonian path of the frontier's constraint graph — this is the same
observation `r3_spin_counts.py` §5 uses to bound W(m) by t_{m+1}, used here for
a different purpose: the reachable states inject into

    L_{m+1} = { s ∈ {E,A,B}^{m+1} : no adjacent clash },  |L_{m+1}| = t_{m+1}

and the array index is the rank of `u` in `L_{m+1}`. Neighbours are then
`N = u[r-1]`, `NW = u[r]`, `W = u[r+1]`, `SW = u[r+2]`, and placing v is exactly
"overwrite `u[r]` with v", so the rank moves by

    dst = idx − h[r][p][u[r]] − h[r+1][u[r]][u[r+1]]
              + h[r][p][v]    + h[r+1][v][u[r+1]]

which is O(1). The last stage of a column (r = m−1) instead produces
`u'' = (E, u[0..m-2], v)`, a shift; its rank is maintained incrementally by the
same odometer that walks the source strings (`pw[]`, recomputed only from the
lowest digit the odometer changed, amortised O(1)).

Worked by hand at m = 2, column 0, to check the layout and the ranks: the sweep
produces states (E,E,E)@area0, (E,E,A)@1, (E,E,B)@1, (E,A,E)@1, (E,A,A)@2,
(E,B,E)@1, (E,B,B)@2 at ranks 0,1,2,3,4,5,6, giving `Z_{1,2} = {0:1, 1:4, 2:2}`.
Brute force on the 1×2 box: empty → 1; two singletons → 2 each; the connected
pair → 2. Agrees. I also hand-checked the accounting end to end at
(n,H) = (2,2): A_1(2) = 2, A_2(2) = 10, N_2(2) = 10 − 4 = 6, T = 3, and the
oracle's `C2.out` gives `C_2(2) − 2C_1(2) = 5 − 2 = 3`. Agrees.

### 1.3 Dense ranking, per r4-inv §1.3

Mandatory and the only path implemented: `--dense-rank` is a required flag and
the binary refuses without it (exit 1). There is no key and no hash. The index
space is `L_{m+1}` rather than the reachable set W(m), because `L_{m+1}` is
r-independent while the reachable set is not (the carry's constraints move with
r). The cost is the measured W/t = 0.8995 gap, ~11% of memory and of scan time
— exactly the waste r4-inv §1.3 priced when it wrote `318,281,039 × 22`.

Bytes/state: 12 per buffer (u64 + u32, structure-of-arrays, both naturally
aligned), 24 double-buffered, against r4-inv's 22 B model for an 11-byte packed
payload. I traded 2 bytes for alignment. At m = 21: 318,281,039 × 24 = **7.64 GB
= 7.11 GiB**, inside r4-inv's 6.52 GiB dense estimate to within the alignment
choice, and far inside the 9.43 GiB keyed figure.

### 1.4 Instrumentation, which is half the job's deliverable

`obs::Reporter` with the house `event=start` / `event=heartbeat` / `event=done`
vocabulary, plus `event=harvest` (output path + sha256) and `event=inject`. Per
m the binary records states, transitions, slot-ops, wall, peak RSS,
bytes/state, ns/slot-op, ns/transition and the truncation count, and writes them
to `<out>.metrics`.

**One thing the lead must not let anyone quote naively.** The cost model's
"slot-op" counts 41 operations per transition. This kernel does *two* — one
64-bit and one 32-bit lane-parallel add. A measured `ns_per_slot_op` far below
the borrowed 40 ns anchor is therefore mostly a statement about the model's
units, not about the hardware. `ns_per_transition` is the number that means what
it says. Both are emitted; the model-comparable one is `ns_per_slot_op` and it
should always be quoted with that sentence attached.

Peak RSS is `ru_maxrss`, a process high-water mark. Buffers are released before
the next (larger) m allocates, and m increases monotonically, so each m's
reading is that m's own peak — modulo allocator retention, which I cannot bound
from here.

---

## 2. Every fixed bound, and why it holds at m = 21

Round 3 found a real `Succ out[12]` overflow in the B1 engine — a fixed buffer
written with a data-dependent count, exactly full at H = 17. **There is no
analogue here: no data-dependent count is written into a fixed-size array
anywhere in this file.** The frontier string, the rank tables, the payload
arrays and the Z table are all `std::vector` sized from the arguments. What
remains is a short list of genuine compile-time constants.

| # | bound | where | why it holds at m = 21, nmax = 40 |
|---|---|---|---|
| 1 | payload is two words, 48 lanes | `kMaxSlots = 48`, `static_assert(2*kMaxSlots == 64+32)` | area slots run 0..nmax; nmax is 40 at every scale of this campaign and is CLI-clamped to ≤ 47. m does not enter. |
| 2 | `kMaxNmax = 47` | `argparse::ArgInt(…, 1, kMaxNmax)` + `static_assert(kMaxNmax+1 <= kMaxSlots)` | compile-time; the CLI cannot get past it |
| 3 | `kMaxM = 40` → `len ≤ 41` | CLI clamp | t_41 ≈ 1.1e16 < 2^63. m = 21 gives len = 22. Additionally `Ranker::build` carries a **runtime** overflow guard on every table addition (exit 78) rather than resting on the argument |
| 4 | `kMaxStates = 2^34` | checked in `run_m`, exit 78 | m = 21 needs t_22 = 318,281,039 ≈ 2^28.25 — 54× headroom. The real binding constraint is the 7.64 GB allocation, not this number; `std::vector::assign` throws on failure rather than truncating |
| 5 | `char path[1024]` | `load_oracle_row` | written by `snprintf` with `sizeof path`; the path is `<oracle-dir>/C<H>.out`. Truncation cannot overflow, and a truncated path fails the open and returns false, which makes the cell uncompared, which makes `compared` smaller, which is caught by the zero-cells check |
| 6 | `char out[65]` | `sha256::finish` | 8 × `snprintf(…, 9, "%08x")` = 64 chars + NUL, exact |
| 7 | `unsigned char pad[72]` | `sha256::finish` | 1 marker + at most 63 zeros to reach offset 56 + 8 length bytes = 72. Bound stated in a comment **and** guarded at runtime (`sha256_pad_overflow`, exit 78) |
| 8 | branch count = 3 | the `for (v = 0..2)` loop | E/A/B; no buffer at all, so nothing to overflow |
| 9 | thread range arithmetic `total*(t+1)/T` | `run_m` | total ≤ 2^34, T ≤ 512 → ≤ 2^43, no u64 overflow |
| 10 | `u[len]`, `tmp[len]`, `pw[len+1]`, `Z[cols+1][nmax+1]` | vectors | sized from arguments; `len = m+1 ≤ 41`, `cols ≤ 4096` |

Two additional runtime aborts that exist because the bound is *not*
compile-time: `dst >= rk.total` on every computed destination rank (exit 78),
and the carry invariant "stage 0 of a column can only be live with u[0] = E"
(exit 78). The area truncation past `slot_cap` is **not** in this list: it is by
design (we only ever need n ≤ nmax, and area only increases), it is exact for
the coefficients kept, and it is counted and reported rather than silent.

---

## 3. Where the C++ and the Python could disagree

The section the lead said they would read most carefully, and the one where
round 3's lesson applies hardest: my confidence about an uncompiled artifact is
worth nothing. So this is a list of exposures with the argument attached, not a
list of reassurances.

**(a) Whole-column transfer vs cell-at-a-time. The big one.** The Python builds
an explicit `succ[s]` list over whole columns and does one transfer per column.
The C++ does m stages of one cell each. They are the same computation only if
the constraint sets coincide, which is the claim that for each placed cell the
C++ checks exactly {N, W, NW, SW} and the Python checks exactly {within-column
vertical} ∪ {d ∈ deltas}. §1.1's table is that mapping; §1.2 is the layout
argument that the four positions `u[r-1], u[r], u[r+1], u[r+2]` are those four
neighbours for every r, including r = 0 (no N, and the carry is E by the wrap
transition, so no NW) and r = m−1 (index r+2 is off the end, so no SW). I
hand-verified the layout at m = 2 and m = 3 and the boundary cases at m = 1.
**This is the exposure I would attack first.** GATE 0 attacks it: the 28 cells at
n ≤ 7 are the Python's own validated set, and a translation error in the kink
layout should not survive them.

**(b) Exact integers vs mod 4.** The Python carries exact ints throughout. Here
the payload is mod 4, and the harvest, the width difference and the second
difference are all evaluated mod 4. Well-defined: `2(a + 4k) = 2a + 8k ≡ 2a
(mod 4)`, so `A_H − 2A_{H-1} + A_{H-2}` mod 4 depends only on the A's mod 4, and
`N_H/2 mod 2` is recoverable from `N_H mod 4`. Nothing else the route reads is
above mod 4. What is *lost* relative to the Python is the exact-value check of
its check 4 (`N_4(6) = 821,380`) — the C++ cannot reproduce that, and does not
try.

**(c) Area truncation.** The Python keeps coefficients up to `w*m`. The C++
discards area above `slot_cap`. Exact for the retained coefficients because the
DP's area is monotone non-decreasing, so no discarded term can re-enter a slot
≤ nmax. Counted as `truncated=` in the metrics and expected to be large — it is
not an error signal.

**(d) Initial condition.** The Python seeds `state = {s: {area[s]: 1}}` over all
valid columns, i.e. column 0 is placed by fiat. The C++ seeds a single all-E
frontier and sweeps column 0 like any other, with the "previous column" reading
as all-E and therefore imposing no constraint. Equivalent, and hand-checked at
m = 2 (§1.2): both give `Z_1 = {0:1, 1:4, 2:2}`.

**(e) Cells with H > n.** The Python reports only `1 ≤ H ≤ n`. The C++ reports
every (H, n) whose three strip heights were run, which at `--m 1..16 --nmax 40`
is 16 × 40 = **640** cells — the number r4-inv §3 claims for the oracle. Both
routes should give T = 0 there, because `C_H(n)` and `A_m(n)` are each
`Σ_h (H−h+1)·T(n,h)` over h ≤ n, hence linear in H once H ≥ n, hence killed by
the second difference. **That derivation is mine; neither the Python nor r4-inv
states it.** If it is wrong the extra 120 cells simply mismatch and the gate goes
red, which is the safe direction — and the binary reports `mismatch_hlen`
separately so the H ≤ n verdict is readable even then.

**(f) The `--expect-flips` domain.** Round 3's 12 / 12 / 4 flip counts were
measured over the 28 cells at n ≤ 7 with H ≤ n. `--expect-flips` is therefore
compared against `mismatch_hlen`, not the total. If it were compared against the
total, extra flips in the H > n region would break the fixture for reasons that
have nothing to do with the mutant.

**(g) Threads.** The Python has none. The C++ shards the source index range and
deposits with per-word atomic compare-exchange. Order-independence rests on the
lane-wise mod-4 add being commutative and associative and on `lo` and `hi` being
independent words of the same value — so a torn pair is not a wrong pair, only a
transiently inconsistent one, and the final value is the same for any
interleaving. GATE 5 is the empirical check, not this paragraph. If the
toolchain lacks `std::atomic_ref` the binary refuses `--threads > 1` (exit 78)
rather than falling back silently; `--threads 1` is unaffected.

**(h) The two new mutants have no Python counterpart.** `slot40` and
`noharvestdiff` are r4-inv §3.2's REDs 4 and 5, invented at the desk with no
measured flip set anywhere. My implementations are readings of the prose:
`slot40` caps the area slots at nmax−1 (so n = 40 is lost and nothing below it
is), `noharvestdiff` sets `A_m(n) = Z_{n,m}(n)` with the width-translation
difference dropped. GATE 1 fails closed if either turns out invisible over the
640 cells, which is the correct outcome for a RED that cannot see.

**(i) The engine does not measure W(m).** It iterates t_{m+1} states and skips
the dead ones. So the run yields `transitions` (measured) but not the window
census; anyone recomputing ns/slot-op from r4-inv's `5043·m·W(m)` and this run's
wall is mixing a modelled state count with a measured wall. Use the emitted
`transitions`.

**(j) Common-mode accounting.** `N_H = A_H − 2A_{H-1} + A_{H-2}` here and
`T = C_H − 2C_{H-1} + C_{H-2}` in the oracle are the same second difference with
the same semantics. r4-inv §1.4 says this in bold and it stays true: a
misconception in the extent accounting hits both sides identically, and the
oracle cannot detect it. The gate tests the connectivity rule and the
implementation, not that layer.

**(k) The binary has no self-contained ground truth.** I did not port
`brute_z`, `brute_G` or `grow_animals`. Everything the C++ checks itself against
is the oracle. **Recommendation: the lead should re-run `r3_spin_pipeline.py`
(6.5 s, laptop-scale, self-contained — it grows its own animals and brute-forces
its own Z) alongside GATE 0**, so the gate chain is anchored on something that
does not depend on the recovered B1 rows being right.

**(l) Untested code paths.** `--inject`, `--mutant slot40`, `--mutant
noharvestdiff`, the threaded deposit, the `verify_language` walk and the SHA-256
implementation have no reference to be checked against and have never executed.
The SHA-256 in particular is hand-written; if GATE 5's cross-thread comparison
behaves oddly, checking the digest against `sha256sum` on the same file is the
first thing to try — the gate sequence in §4 does that explicitly for that
reason.

---

## 4. Build command and gate sequence

### 4.1 Build

No Makefile target exists. Either add this stanza next to
`build/middle_kingdom_tm` (it follows the same shape):

```make
# INV-8 spin-basis parity engine (results/r4/r4-spinbuild.md).
build/r4_spin_engine: experiments/tristruct/r4_spin_engine.cpp cpp/argparse.h cpp/obs.h | build
	$(CXX) $(CXXFLAGS) -O3 -Icpp $< -o $@ -pthread
```

or build it directly, with the same provenance defines the Makefile bakes in:

```
c++ -std=c++20 -Wall -Wextra -Werror -O3 -Icpp \
    -DGIT_REV='"'"$(git rev-parse --short HEAD)$(test -n "$(git status --porcelain)" && echo -dirty)"'"' \
    -DBUILD_TIME='"'"$(date +%Y-%m-%dT%H:%M:%S%z)"'"' \
    experiments/tristruct/r4_spin_engine.cpp -o build/r4_spin_engine -pthread
```

**Expected observable:** clean compile, no diagnostics. `-Werror` is not
optional here; it is the only static check this artifact has ever had.
**A failure means my source**, and the likely candidates are the
`std::atomic_ref` feature test, the `__attribute__((format))` / `[[noreturn]]`
pairing on `die`, and unused-parameter diagnostics in the non-atomic branch of
`deposit`.

### 4.2 Gates, in order

Run them in this order; each is cheap relative to the next. `ORA` below is
`results/cutcount_b1/rows`, `OUT` a scratch path under `results/r4/`.

**GATE 0 — the n ≤ 7 desk table (exit 70 on failure).**
```
build/r4_spin_engine --m 1..7 --cols 8 --nmax 7 --mod 4 --dense-rank \
  --oracle $ORA --out $OUT/spin_g0.txt --report-rss
```
Expected: exit 0 and a final stdout line with `compared=49 mismatch=0
compared_hlen=28 mismatch_hlen=0 structural_failures=0`. `--verify-rank`
defaults on at m ≤ 10, so every incremental rank in this run is cross-checked
against a from-scratch rank, and the language walk runs for every m.
Seconds. **Alongside it, run `python3 experiments/tristruct/r3_spin_pipeline.py`
(6.5 s) so the chain is anchored on the self-contained reference too (§3k).**
Failure meanings: **70** = the port disagrees with the 28 cells the Python
validated, i.e. the kink translation of §1.2 is wrong; **77** = the incremental
ranking is wrong; **78** = the index space is not a bijection or the carry
invariant broke; **76** = the mod-4 bookkeeping is wrong.

**GATE 1 — the recorded mutant flip sets (exit 71).** Three fixtures from round
3, enforced by count:
```
for M in drop-nw:12 drop-sw:12 rook:4; do
  build/r4_spin_engine --m 1..7 --cols 8 --nmax 7 --mod 4 --dense-rank \
    --oracle $ORA --mutant ${M%%:*} --expect-flips ${M##*:} \
    --out $OUT/spin_g1_${M%%:*}.txt
done
```
Expected: exit 0 for each, with `mismatch_hlen` equal to 12, 12, 4 respectively.
A **71** means either the stencil mutant is not the Python's mutant or the clean
path is wrong in a way that cancels. Then the two mutants with no fixture, at
production scale — these are measurements, not comparisons, and their flip sets
should be **recorded in the run log as new fixtures**:
```
build/r4_spin_engine --m 1..16 --cols 41 --nmax 40 --mod 4 --dense-rank \
  --oracle $ORA --mutant slot40        --out $OUT/spin_g1_slot40.txt
build/r4_spin_engine --m 1..16 --cols 41 --nmax 40 --mod 4 --dense-rank \
  --oracle $ORA --mutant noharvestdiff --out $OUT/spin_g1_nohd.txt
```
Expected: exit 0 with non-empty flip sets. `slot40` should flip **only** cells
at n = 40; anything else means my area-cap reading is not what r4-inv meant.
An empty flip set exits **71** and blocks dispatch — that is the gate-design
failure r4-inv §3.2 asks for, not a pass.

**GATE 2 — fault injection (exit 72).**
```
build/r4_spin_engine --m 1..7 --cols 8 --nmax 7 --mod 4 --dense-rank \
  --oracle $ORA --inject 6,3,2,5 --out $OUT/spin_g2.txt
```
Expected: an `event=inject … state=<i> slot=5` line on stderr, then exit 0 with
`mismatch > 0`. **72** means a single corrupted mod-4 lane mid-sweep did not
reach the harvest — the uncompared-cell path is not live.

**GATE 3 — the 640-cell oracle (exit 73). The main event.**
```
build/r4_spin_engine --m 1..16 --cols 41 --nmax 40 --mod 4 --dense-rank \
  --oracle $ORA --report-rss --out $OUT/spin_gate_m1_16.txt
```
Expected: exit 0, `compared=640 mismatch=0 compared_hlen=520 mismatch_hlen=0
structural_failures=0`, and an `event=harvest … sha256=…` line emitted **before**
any comparison happens. **73** is a bug certificate against one of the two rule
classes and escalates immediately; the first 20 mismatching cells are printed,
and their (H, n) pattern is the localizer.

Wall: **NOT ESTABLISHED.** r4-inv's 5.1 thread-hours is the borrowed-40-ns
upper bracket. This kernel does two word-ops per transition rather than 41 slot
ops, and the total transition count at m ≤ 16 is order 10^10, so minutes is as
plausible as hours. The thing I would actually watch is write locality: for
stage r the destination rank differs from the source by h-terms of magnitude
~t_{len−r}, so late stages write near the source index and early stages write
across the whole array. That asymmetry, not the arithmetic, is what will set the
constant — and it is exactly what this gate is for.

**GATE 4 — the two constants (exit 74).** Read `$OUT/spin_gate_m1_16.txt.metrics`.
Expected: one `K m=… states=… transitions=… wall_s=… peak_rss_mb=…
bytes_per_state=… ns_per_slot_op=… ns_per_transition=… truncated=…` line per m,
present and non-zero at m = 14, 15, 16. These are output (b) and (c) of
R4-SPIN-JOB-0: they retire the 38 B / 22 B model and the borrowed 40 ns anchor.
Quote `ns_per_slot_op` only with §1.4's sentence attached. **74** means the run
did not obtain what it was asked to measure.

**GATE 5 — sharding race (exit 75 in the contract; here a file comparison).**
```
build/r4_spin_engine --m 1..16 --cols 41 --nmax 40 --mod 4 --dense-rank \
  --oracle $ORA --threads 16 --report-rss --out $OUT/spin_gate_thr16.txt
cmp $OUT/spin_gate_m1_16.txt $OUT/spin_gate_thr16.txt
sha256sum $OUT/spin_gate_m1_16.txt $OUT/spin_gate_thr16.txt
grep ^sha256 $OUT/spin_gate_m1_16.txt.metrics $OUT/spin_gate_thr16.txt.metrics
```
Expected: `cmp` silent, the two `sha256sum` digests equal, and both equal to the
binary's own `sha256` lines — which also validates my hand-written SHA-256
against the system one (§3l). The output file deliberately contains no thread
count, host or timing, so byte-identity is a real check rather than an artifact.
A difference is a race in the atomic deposit and blocks dispatch.

**GATE 6 — the bookkeeping check.** Already covered: the
`X structural_checks=… structural_failures=0` line inside the output file, and
`structural_failures=0` on stdout. Labelled in the source and in this file as a
bookkeeping check that is **blind to stencil errors** — round 3 measured that
blindness. It never certifies correctness.

**Optional and cheap: cross-ISA.** Repeat GATE 3 on ayr and compare the sha256
against dalby's. r4-inv recommends it; ~the same wall as GATE 3 for the cheapest
independence evidence in the campaign, and the output-file design makes the
comparison a one-line `cmp`.

**Only after GATES 0–6 all pass** does m = 18..21 (SPIN-JOB-1) get dispatched.
There is no override path in the binary and no known-benign list.

---

## 5. What the spec left underdetermined, and what I chose

1. **Harvest granularity.** The prose says cell-at-a-time; the Python is
   column-at-a-time; the brief says the Python governs. I went cell-at-a-time
   because the whole-column kernel is priced out (P_21 = 1.47e14 pairs,
   `r3_spin_counts.py` §4) at m = 16 as well as at m = 21, so the Python's
   kernel is not implementable at the gate's own scale. §3(a) is the debt this
   creates and GATE 0 is the payment.
2. **What to rank densely over.** `L_{m+1}` (t_{m+1} states) rather than the
   reachable W(m). The reachable set is r-dependent; `L_{m+1}` is not, which is
   what makes the rank update O(1). Costs the 11% W/t gap that r4-inv already
   priced.
3. **Bytes/state.** 12 per buffer (aligned u64 + u32) instead of 11 (packed).
   7.11 GiB at m = 21 rather than 6.52.
4. **GATE 0's "28-cell desk table" is not a fixture file anywhere.** Realised as
   the H ≤ n subset of the oracle at n ≤ 7 — `compared_hlen=28` — since the
   desk table's values are by definition T(n,H) mod 2.
5. **GATE 1's "reproduces its recorded flip set exactly".** Enforced by *count*
   (`--expect-flips`), not by the exact cell set: no fixture file of cell sets
   exists, and 12 / 12 / 4 is what round 3 actually recorded. The exact first
   cells round 3 names ((2,2), (3,3), (4,2) for drop-NW; (4,3) for rook) are
   readable from the printed MISMATCH lines and should be eyeballed once.
6. **RED runs and the structural checks.** Recorded, not fatal, under a mutant
   or an injection — otherwise a mutant could abort before its flip set is
   measurable. Fatal (exit 76) on a clean run.
7. **`--oracle` is mandatory** (exit 79 without it). A compute-only mode would
   be a run that checks nothing, which the contract forbids.
8. **`--mod` accepts only 4** — no other payload modulus is implemented, and
   accepting the flag while ignoring it would be the wrong kind of politeness.
9. **Threading model**: source-sharded with per-word atomic CAS, chosen because
   the mod-4 lane add commutes, making the result order-independent by
   construction and GATE 5 a real check.
10. **Output / metrics split**, so the mathematical file is byte-comparable
    across thread counts, boxes and ISAs and its sha256 means something.
11. **`--inject` target**: the lowest-indexed live state at the named
    (m, col, stage), with its index logged.
12. **Exit-code assignment** follows r4-inv §3.4 for 70–76 and adds 1, 2, 3, 77,
    78, 79 for argument, I/O, zero-cells, rank, bound and no-oracle failures.
    GATE 5's exit 75 is not produced by the binary — a sharding race shows up as
    two different output files, so the gate is a `cmp`, not an exit code.

---

## NOT ESTABLISHED

- **Nothing in `r4_spin_engine.cpp` has been compiled or executed.** Not by me,
  not anywhere. Every statement above about its behaviour is about intent.
- No wall, RSS or ns/op figure for this kernel exists. GATE 3 and GATE 4 produce
  the first ones; my "minutes as plausible as hours" in §4.2 is a guess from an
  operation count and is labelled as such.
- The equivalence of the kink sweep to the Python's column transfer (§3a) is
  argued from the neighbour-position table and hand-checked at m = 1, 2, 3 and
  at the cell (n,H) = (2,2). It is not tested.
- The H > n vanishing claim (§3e) is my derivation from the linearity of
  `C_H(n)` in H for H ≥ n. Neither source states it.
- `slot40` and `noharvestdiff` have no measured flip set anywhere, at any scale.
  Their implementations are my reading of r4-inv §3.2's prose.
- The SHA-256, the threaded deposit path, `verify_language`, and the injection
  path have no reference implementation to check against and have never run.
- I did not re-run `r3_spin_pipeline.py` or `r3_spin_counts.py` (agents run
  nothing). I read both sources in full and their logs' banked numbers as
  reported by `results/triangle-r3-spin.md` and `results/r4/r4-inv.md`; I did
  not read `r3_spin_pipeline.log` line by line.
- The engine is *structurally* ready for m = 18..21 — the bounds in §2 hold
  there and no constant caps m below 40 — but no m > 16 path has been exercised
  even on paper beyond the arithmetic in §1.3. The one place the code changes
  behaviour with m is the `--verify-rank` default (off above m = 10) and the
  language walk (off above len = 17); both are checks, so above m = 16 the
  engine runs with strictly fewer self-checks. That is a deliberate cost choice
  and the lead should turn `--verify-rank 1` on for at least one short m = 18
  column before the full production run.
