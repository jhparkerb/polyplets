# Paper 1, the engine chapter — source material

2026-08-06, sortie plan §2 Paper 1; **updated 2026-09-04** (jasonp's finish
list, item 4): §0 added with code anchors for every component, §1a added
(which kernel produced which term), §5 corrected (the production counters are
native words, not CRT), §7a added (the per-term ledger, a(26)–a(41)), §8a added
(the a(41) route), §9 added (what the 2026-09-02 audit says the chapter must
and must not claim). The 2026-08-06 sections are otherwise as they were.

The record's other half: how a(23)–a(41) were computed on three home
machines. `paper/technical-report.tex` has three Methods paragraphs; this is
the material for the chapter they gesture at.

**This file proposes; it does not edit.** Nothing here is drafted prose.
Every number is quoted with the file that measured it, and the ones that could
be re-derived cheaply were re-derived rather than copied. Where a source note
carries a correction, the correction is what is quoted. Code anchors are
`file:line` at commit `25d7f61`.

The through-line, if the chapter wants one: **the wins were all in keeping the
cores fed, not in making the kernel faster.** The one genuine algorithmic
change (kink carry) is a base change, and everything else is scheduling,
memory and I/O.

`paper/polyplets-report.tex:293-448` is the machine-written account of the
same material (Methods A–C). Two of its sentences disagree with the run
records and should not be inherited: it calls the cell-at-a-time kernel "the
production engine for a(24)–a(40)" (`:359-360`), where the records say the
kink kernel entered production at a(30) and a(23)–a(29) ran the whole-column
kernel (§1a below); and its "~200× at H=16" speedup (`:374-376`) has no
measurement behind it in the tree — the measured table is §1's (11×, 29×,
~55× estimated).

---

## 0. What the engine is, component by component

The object is `T(n,H)`, the number of fixed polyplets of size `n` and
bounding-box height exactly `H`, one height at a time; `a(n) = Σ_H T(n,H)`.
Heights are independent jobs (`orchestrator/sweep.go:1-8`), which is what
makes multi-machine splits by height (§7a) and the closed-form injection of
the tall heights (§0.8) possible without any cross-talk.

### 0.1 The boundary state

Column kernel: a signature is `H+2` bytes — one byte per row of the most
recent column holding `0` (empty) or a component label, then a touched-top
flag and a touched-bottom flag. Labels partition the occupied boundary cells
into the partial animal's connected components; **crossing partitions are
allowed**, which king adjacency needs and which is why the Motzkin encodings
of the polyomino literature do not apply (`core/signature.h:1-13`). Labels are
renumbered in first-occurrence order after every step so that equivalent
partitions cannot proliferate as distinct states (`core/signature.h:69-71`).
The hot path uses a fixed 32-byte inline key (`H <= 30`), so the state store
is a flat sorted run rather than a hash map of strings (`core/signature.h:26-45`).

### 0.2 The two transitions

**Whole column** (`core/transition.h:1-14`): because king adjacency reaches
the diagonal neighbours `(c-1, r±1)`, a cell-at-a-time boundary would have
already overwritten the north-west cell a new cell may attach to. The column
kernel sidesteps this by transferring an entire column per step, with the old
column wholly present; connectivity is resolved by union–find over the new
column's cells and the old column's components, so k-way merges (a new cell
fusing its W/NW/SW old neighbours plus N/S new neighbours) need no special
cases. A mask that strands an old component is `Dead`.

**Kink carry** (`core/kink.h:1-31`): the boundary advances one cell per
stage, `H` micro-stages per column. The key grows to `H+4` bytes: the mixed
boundary (new-column cells above the stage row, old-column cells below), the
two touch flags, a **carry byte** holding the one old cell overwritten a stage
ago that is still king-reachable, and a placed-any bit. Canonicalisation
relabels the boundary and the carry together (`core/kink.h:49-67`). Column
boundaries are handled by `core/kink_column.h:1-19`: harvest (classify
completed animals) happens at column *start* on the state being seeded;
finalize at column end drops the last carry with a stranding check, then
canonicalises, prunes, folds and dedups back to an end-of-column run. §1 is
the measured price of the two.

### 0.3 The payload: ranged counts by size

Each state carries a count vector indexed by cells placed so far, stored as
a window `(lo, len, counts[])`; two records with the same key combine by
elementwise addition, growing the window in place (`core/run.h:100-145`).
The combine is commutative and associative, which is what makes the merged
result independent of shard cuts and run order — the "bit-identical" property
the orchestrator relies on (`core/mapreduce.h:8-12`). Every add is guarded:
`slot < prev` after an addition means a word overflowed and the run aborts
(`core/run.h:107-118`, live only because `NSFLAGS` carries no `-DNDEBUG`; see
§9).

### 0.4 Counter width

Two compile-time counter tags: `u64`, exact to a(25); `u128`, exact to about
a(48). The orchestrator refuses to start with an undersized counter for the
requested `maxn` (`core/counter.h:1-27`, `orchestrator/runref.go:597`). Every
production run from a(26) on used `u128` (`results/ns_a26/PROVENANCE.md:4-6`).
No CRT, no modular arithmetic anywhere in the production path — see §5.

### 0.5 The admissibility prune

A state is dropped when cells-so-far plus a lower bound on cells any
completion must still place exceeds `maxn`. The bound is the sum of three
disjoint forcings: rows to climb to reach row 0 if the top is untouched, rows
to descend to reach row `H-1` if the bottom is untouched, and every empty row
band between occupied rows that **no single component spans** (a band one
component already bridges through its history costs nothing). It must never
over-estimate, since an over-estimate silently drops real animals; the gate
that re-derives every published term is the oracle for that
(`core/signature.h:123-174`).

### 0.6 Map, merge, classify

`map_shard` streams one shard of the current frontier: for each state, check
the completion predicate and tally if met; enumerate the viable successor
masks; apply the transition; prune; optionally fold under the vertical mirror
(`--fold`, the R1 symmetry, halving the state space); collect
`(successor, counts)`; then sort and deduplicate into one sorted run
(`core/mapreduce.h:42-50`). `merge` is a k-way merge of sorted runs combining
equal keys (`core/mapreduce.h:8-12`). Completion is the closing-column path:
a state whose next column is empty and whose boundary is a single component
with both touch flags set is one fixed polyplet of height exactly `H`,
tallied by size into the row `T(·,H)`; the holes variant reuses the Euler
accounting of `core/euler.h` (`core/classifier.h:1-14`).

### 0.7 On disk

Frontiers live as `POLYRUN` files: a text header (height, maxn, counter
width, classifier, key range, record count, git rev, byte order) followed by
sorted binary records and an FNV-1a-64 checksum over the body
(`core/runfile.h:1-15`); zstd framing for spill and frontier files is a
build option (`core/runfile.h:36`). Checkpoints are `POLYCKPT` files naming
the frontier run files plus the accumulated triangle, so the bulk of a
checkpoint *is* the frontier already on disk (`orchestrator/checkpoint.go:1-12`).
Resume refuses a configuration mismatch, and specifically refuses a different
`--max-diag-k`, because that changes which heights were injected versus swept
(`orchestrator/sweep.go:157-190`).

### 0.8 The orchestrator

Go, one process per box. Per column: partition the source key space into map
units, run map workers in parallel from a pool of persistent worker processes
(`orchestrator/workerpool.go:193-252`), sample the output key space into merge
ranges, run merge workers, garbage-collect consumed runs, checkpoint
(`orchestrator/sweep.go:1-8`). The knobs that mattered in production are all
in `SweepConfig` (`orchestrator/sweep.go:24-45`): `Cores`, `UnitMult` (map
units per core), `MergeMult`, `StealGrain`, `OverlapHeights`, `RAM` (per-worker
spill budget), `FastMapDir` (tmpfs for transient map output), `Heights` (the
multi-machine split), `CounterWidth`, `MaxDiagK`.

**Work stealing** (`orchestrator/sweep.go:1160-1260`): when a core idles in a
column's tail, the longest-remaining unit is stopped at a cursor and its
remainder split across idle cores. A unit is eligible when either its
remaining records or, at its own observed rate, its remaining wall time
exceeds a grain (`stealEligible`, `:1179`); the grain in seconds comes from
the pace of *finished* units, not elapsed wall time, because the latter is
diluted by however long the current straggler has been idling everyone
(`refGrainSeconds`, `:1208`, with a measured-regression test). Stealing fires
only when a height is the sole occupant of the core pool (`stealAllowed`,
`:1239`), which is what lets it coexist with overlap. Its located ceiling is
in §2.

**Overlapping heights** (`runOverlap`, `orchestrator/sweep.go:510`): several
heights share one core pool so one height's low-utilisation merge hides
behind another's map; checkpoints fall at height boundaries. §2 has the
measurement.

**Injection** (`orchestrator/sweep.go:2039-2063, 2293-2376`): heights `H=1,2`
are elementary rows, `H = maxn` is `3^(n-1)`, `H = maxn-1` is the pole
formula, and heights with `k = maxn - H` in the wired table are composed from
`P_k` (`diagCoeffTable`, `j = 1..19`, `orchestrator/sweep.go:2063`) instead of
swept. `--max-diag-k` caps which diagonals may be injected; the zero value of
the config means *no injection*, so a caller that forgets to set it gets more
real sweeping, never a wrong cell (`orchestrator/sweep.go:45`). Per-height
rows are written as `h<H>.out` (`writePerHeight`, `:1866`) and re-summed by a
combiner that refuses partial or duplicated inputs
(`results/ns_a27/PROVENANCE.md:12-13`, `--require-cover`).

## 1. The kernel choice: whole column vs one cell at a time

`results/kink-carry.md` (2026-07-02).

The production engine transferred a **whole column** per step, because king
adjacency needs the old NW cell that a cell-at-a-time boundary has already
overwritten. Every published polyomino transfer matrix (Jensen 2001 through
Barequet–Ben-Shachar 2024) moves the boundary **one cell** at a time instead.
The choice had never been priced: it was recorded only in a header comment.

Pricing it (measured, one core):

| H | maxn | column TM | kink carry | speedup |
|---|---|---|---|---|
| 10 | 18 | 4.5 s | 0.41 s | **11.1×** |
| 12 | 22 | 175 s | 6.0 s | **29.2×** |
| 14 | 26 | ~5000 s (est) | **95 s** | ~55× |

The ratio grows ~2.7× per +2H because it is the masks-per-state exponential
being deleted. It is a **base change, not a constant**: per-term compute
growth falls from ~4.4× (state growth ~2.42 × masks-per-state growth ~1.8) to
about the state growth alone, ~2.5×. In b^n terms, b ≈ 4.4 → b ≈ 2.5.

Second consequence, as large: the shuffle collapses. Per-column record volume
drops from Σ masks (627 M at H12; the 126 GB spill peak at a(27) H16) to
frontier-sized, so the sort/spill/merge machinery and its zstd pipeline stop
being necessary for frontier terms.

Validation of the new kernel against the old: T(20..22,12) at maxn=22 and
T(24..26,14) at maxn=26 match `results/ns_a27/perheight/` exactly. The kink TM
is an independent transition implementation (per-cell union-find + carry
stranding vs per-column union-find), so this is a real cross-check, not a
regression test. Its production-scale validation is the a(29) cell-diff:
every per-height row of a kink run at maxn=29 against the banked column-kernel
rows (`scripts/kink_validate.sh:1-15`), after which the kink kernel carried
a(30) (`results/ns_a30/PROVENANCE.md:3-9`). The 2026-09-02 audit's caveat on
how much of this is *automated* is in §9.

## 1a. Which kernel produced which term

From the per-term records; all `results/ns_aNN/PROVENANCE.md:1-14` unless
noted.

| terms | engine | counter | notes |
|---|---|---|---|
| a(19)–a(20) | the earlier `cpp/tma` column engine | — | a(20) on ayr, "seek-index engine", all heights swept (`results/ns_a20/PROVENANCE.md:6-8`); a(19) is the two-algorithm term |
| a(21)–a(22) | new engine, column kernel | u64 | a(21) dalby, 35.8 h, all heights swept, ayr h1–17 byte-identical (`results/ns_a21/PROVENANCE.md:8-30`); a(22) inside the a(23) run; both Redelmeier-confirmed by the 2026-07-16 fleet |
| a(23) | new engine, column kernel | u64 | ayr H1–16 + dalby H17–23, H17/H18 byte-exact across ISAs (`ns_a23:5-9`) |
| a(24)–a(25) | column kernel | u64 | dalby; **first closed-form injection** at a(24) (k ≤ 7), P0–P8 at a(25) |
| a(26)–a(29) | column kernel | u128 | first `u128` term is a(26); a(27) split dalby H16 + ayr H3–15; a(28) ayr solo, a(29) dalby solo, run concurrently |
| a(30)–a(41) | **kink kernel** | u128 | a(30) is the first kink production term; config fixed from the a(29) cell-diff onward |

Top real height per term: H15 (a26, a28), H16 (a27, a29), H17 (a30), H18
(a31–a34), H19 (a35–a37), H20 (a38–a39), H21 (a40), H19 (a41, with the tower
above — §8a). This is the "injection boundary advancing as each new P_k is
certified" that `paper/polyplets-report.tex:394-396` describes.

## 2. Utilization was the lever, not cores

`results/a34-utilization-postmortem.md`, `results/utilization-fix-and-ceiling.md`,
`docs/utilization-bottleneck-log.md`.

The a(34) run was measured, from raw per-column telemetry rather than
estimated, at

    TOTAL wall_s = 13300.4   cpu_s = 210666.1   util = 19.8%

and the shape of the waste is the finding: utilization **peaks at H16 (33.6%)
and reverses exactly where the wall-clock lives** — H18 is 70.2% of the run at
17.2% utilization. So the waste was concentrated precisely where fixing it
paid most, which is what ruled out "it is just an average over a fine run".

**This is also the answer to the cloud question**, and both halves are
citable. At 19.8% utilization, core count was not the binding constraint —
that is the postmortem above. The cost half is `docs/cloud-burst-plan.md`,
removed in the big tidy and readable at
`git show 78602f8^:docs/cloud-burst-plan.md`: the wall is floored by the single
most expensive height, which is an inherently sequential column sweep, so cloud
can only help by giving *that one height* more physical cores than dalby's 80.
The sizing lands on one `hpc7a.96xlarge` (192 physical cores, no SMT, ≈2.4×
dalby) at roughly $7–8/hr on demand, and the decision, 2026-07-02, was not to
buy it. A chapter paragraph on this should quote the structural reason rather
than the price: extra *small* boxes do nothing for the floor, so the only
purchasable speedup is a single bigger box for one height.

**What worked** (`--overlap-heights`, real test at maxn=34, fixed binary):

| | wall | cpu-s | utilization |
|---|---:|---:|---:|
| H17 alone | 2462.7 s | 47,335.4 | 24.0% |
| H16 alone | 722.1 s | 19,395.0 | 33.6% |
| sum, hypothetical | 3,184.8 s | 66,730.4 | 26.2% |
| **H16+H17 overlapped** | **2,522 s** | **66,596.3** | **33.0%** |

H16's entire 722 s landed almost free: the combined run took 59 s longer than
H17 alone, a validated **21% wall cut**, with byte-identical CPU-seconds —
overlap packs work, it does not redo it.

**What did not work, and why it is interesting.** Work-stealing measured ~0 at
this scale and was *root-caused* rather than shrugged off: the interrupt point
lives between records, so a single pathological record is unsplittable by any
cursor-based scheduler, however correct its scoring. Fixing that means
checking the stop flag inside the enumeration loop itself — the most measured,
most guarded code in the engine. LPT scheduling was tried and rejected
(`results/scheduling.md`). The honest conclusion is a **located ceiling**
rather than a target: at H17/H18 shapes, utilization will not approach 80%
under this architecture, and the floor component is the pathological-record
limit.

## 3. The fan-in tax: 75% of worker CPU spent opening files

`results/fanin-tax.md` (2026-07-23), thread *Fan-In Tax*.

A benchmark meant to confirm a 3.36× buffered-I/O win measured on gympie
reproduced **not at all** on dalby: 336 s wall / 20,106 cpu-s on both the old
and new revisions, against a recorded baseline of 140.9 s / 4,554 cpu-s. The
cause was a dalby-shaped pathology the gympie profiling could never have seen
— worker CPU going into `open()` fan-in, not into counting.

The general lesson for the chapter: **a performance result measured on one box
is a result about that box.** The repo's standing rule that a remote engine is
rebuilt and re-benchmarked after every edit comes from here.

## 4. Memory is the wall, four times over

`results/overcommit-hydra.md` (2026-07-25), thread *Overcommit Hydra*: four
a(40) OOM deaths in one day, each ~1–1.5 h in, at maxn=40's peak height
co-residency (H19+H20+H21 overlapping), each kernel-OOM-confirmed, twice
taking down the tmux server and the ssh-agent with it.

Each head was measured and fixed: a /dev/shm admission TOCTOU (N concurrent
rounds each passing a point-in-time `statfs`) fixed by reservation with a 24 GB
floor; a RAM co-budget failure (80 × 1 GiB worker budgets plus ~38 GB admitted
shm plus unbounded idle zstd pools) fixed by capping the pool at 64, raising
the floor to 40 GB and dropping `--ram` to 768 M.

The rule that came out of it, and that the chapter should state as a rule:
**per-worker RAM budget is (total × margin) / cores, never a flat number.**

Related and worth a sentence: the tmpfs map-output crossover is a 4.6× win up
to a(34) and **fails at a(35)** (OOM). Neither the win nor the failure is
predictable from the other.

## 5. Counting representation: fewer, wider counters

`results/crt-counter-shaping.md` (2026-06-25).

**Scope correction, 2026-09-04.** The CRT investigation below was about the
earlier `cpp/tma` engine (`cpp/tma/sweep8_modp.h`), whose counts were
residues. The production engine that computed a(23)–a(41) counts in native
64- or 128-bit words with no modular arithmetic at all (§0.4); CRT survives in
the tree only in the Motley second source, which is a different program. The
chapter should not say the production counts were reconstructed from primes.

The investigation refutes the direction of its own question. Going to smaller
counters (16- or 8-bit) needs 4–5 or 9–10 primes respectively, runs *slower*
per pass in scalar code, and — because the dominant cost is enumeration paid
per pass — more primes means proportionally more wall time.

The structural fact underneath: a single `uint64` counter is exact all the way
through **a(25)**, and the production engine switched to `u128` at a(26)
(`results/ns_a26/PROVENANCE.md:4-6`). For a(21)–a(25), CRT was a RAM-reduction
choice, not a correctness requirement.

Settled design for the mod-p engines: u32 primes with the 31-bit interleave
(`results/crt-counter-shaping.md`, banked as settled — do not re-litigate).

## 6. PGO: no

`results/terminal-velocity.md`, `pgo-no-go-dalby`.

gcc PGO measured **worse than gcc -O3**: 91.0 s, a 1.84× speedup where the
settled combination of kernel levers gives 2.06×. It was dropped; clang PGO
was blocked on missing toolchain packages on dalby and skipped. The reason is
diagnostic rather than incidental: the workload is
**branch-mispredict-bound** — the profile shows IPC 2.37 with a 1.96%
branch-miss rate costing ≈9% of cycles — so profile-guided layout has little
left to win. Kernel levers settled at 2.06× (L1 + L3 + L4 + clang).

## 7. What a(40) actually cost

`results/ns_a40/PROVENANCE.md`, regenerated figures in
`docs/paper1-reproducibility.md`.

Computed 2026-07-25..28 on dalby alone (80-core ARM Ampere Altra, 125 GB),
as three phases, because maxn=40 with full overlap does not fit RAM:

| phase | heights | cores | wall | cpu-s | rss max |
|---|---|---|---|---|---|
| A | H1–19 + H22–40 | 80 | ~6.3 h | 871,963 | 827 MB |
| B | H20 solo | 48 | 9.6 h (one interruption + resume) | 1,116,858 | 1023 MB |
| C | H21 solo | 32 | 36.4 h | 3,329,644 | 4045 MB |

Disk peak 363.4 GB, hit mid-H21, well above the ~234 GB projection that had
paused the ladder at a(39); the H21-solo phasing plus post-a(39) cleanup made
it fit anyway. H21's frontier peaked at 355,390,806 records, a stable ~2.7×
per-column cost over H20. H21 is the tallest real sweep of the project.

## 7a. The per-term ledger, a(26)–a(41)

Every figure is the run record's own; `results/ns_aNN/PROVENANCE.md:1-14`,
`results/a41/PROVENANCE.md:9-24`. Blank means the record does not state it.
Where two boxes ran, the wall is per box, not summed.

| n | date | box, cores | kernel | real H | wall | cpu-s | rss max | disk peak |
|---|---|---|---|---|---|---|---|---|
| 26 | 07-02 | dalby 80 | column | 1–15 | 4,066.5 s | | | |
| 27 | 07-02 | dalby 80 (H16) + ayr 32 (H3–15) | column | 3–16 | 13,553.9 s / 9,697.2 s | | | spill ~126 GB |
| 28 | 07-02 | ayr 32 | column | 3–15 | 11,723.8 s | 353,201.8 | 786.9 MB | |
| 29 | 07-02 | dalby 80 | column | 3–16 | 26,202.2 s | 1,960,646.8 | 1,647.1 MB | |
| 30 | 07-03 | dalby 80 | kink | 3–17 | 3,711 s | | ~76 MB | |
| 31 | 07-03 | dalby 80 | kink | 3–18 | 10,003.1 s | | ~5.9 GB | |
| 32 | 07-03 | dalby 80 | kink | 3–18 | 10,945.3 s | | ~5.78 GB | |
| 33 | 07-04 | dalby 80 | kink | 3–18 | 12,200.3 s | | ~6.02 GB | |
| 34 | 07-04 | dalby 80 | kink | 3–18 | 13,316.7 s | | ~6.44 GB | |
| 35 | 07-10 | dalby 80 (H19) + ayr 32 (rest) | kink | 3–19 | 25,112.2 s (dalby) | | 372 MB | |
| 36 | 07-10 | ayr 32 (H1–18) + dalby 80 (H19) | kink | 3–19 | 6,988.2 s / 11,810.4 s | 187,437.7 / 397,861 | 351.6 / 380.2 MB | |
| 37 | 07-23 | dalby 80 | kink | 3–19 | 13,048.4 s | 580,223 | 394.6 MB | 75.7 GB |
| 38 | 07-23/24 | dalby 80 | kink | 3–20 | 56,994 s | 1,783,598 | 971 MB | 221.5 GB |
| 39 | 07-24/25 | dalby 80 | kink | 3–20 | 39,957 s | 2,070,672 | 1,516 MB | 174.5 GB |
| 40 | 07-25..28 | dalby, three phases (§7) | kink | 3–21 | see §7 | 5,318,465 (sum) | 4,045 MB | 363.4 GB |
| 41 | 08-20 | dalby 40 | kink, H1–19 only | 3–19 | 16,998.7 s | 605,643 | 557 MB | < 100 GB |

Three things the table shows without commentary: the kink kernel's entry at
a(30) (H17 in 62 minutes where the column kernel took 7.3 hours for H16 at
a(29)); the disk-not-RAM wall from a(37) on; and that a(41) cost less than
a(37) because the two tall heights were never swept (§8a).

## 8. Where the engine stops

- **Scaling is disk-bound at ~4.4×/term** on the pre-kink base, ~2.5× on the
  kink base (§1).
- **The connectivity wall**: the algorithmic levers examined were measured
  dead, and the same wall shows up from the bounding side too
  (`results/second-wind.md` §114, `results/strip-growth-lambda-bounds.md`
  §132, `docs/full-utilization-redesign.md` Part 4). What is left is
  engineering, not algorithms.
- **Cost is not the count.** A height's compute cost tracks its frontier
  (~2^H), not the number of animals it contributes, so the top heights are
  never "trivial" however small their counts — the a(40) phase table above is
  the demonstration: H21 alone cost 36.4 h.
- The strip second source cannot follow: C_14 measured ~38 GB, C_15 would need
  ~200+ GB (`results/strip-engine.md`).

## 8a. How a(41) was reached without the two tall heights

`results/a41/PROVENANCE.md:1-24`, `results/undertow.md:1-40`.

The rule that priced the ladder was that level `k` of the diagonal tower
needs two *above-onset* anchors, the two tallest cells on its diagonal; for
`P_19` those were `T(39,20)` and `T(40,21)`, the latter being a(40)'s 36.4-hour
phase C. The grand form (`docs/proofs/grand-form.md`, Lean-complete) makes
each level carry exactly two new constants, so any two independent linear
equations pin it, and the below-onset defect identity
(`results/onset-defect-depths234.md`) supplies such equations from cells
`j` rows *shorter* than the onset anchor, with the defect `D_j(k)` computed ab
initio from cluster-weight families that read neither the triangle nor the
wired table. Nothing new was proved; the content is the choice of anchors.

So a(41) was two jobs: heights 1–19 swept for real at Nmax 41 (`--kernel kink
--counter u128 --cores 40 --overlap-heights 19 --heights 1-19`, 4.72 h), and
heights 20–41 composed by `experiments/undertow_a41.py` — levels `k <= 19`
from the wired table, `k = 20, 21` pinned from below-onset cells. A run at
Nmax 41 also reproduces every banked row `n <= 40` at the heights it sweeps:
760 cells, 0 disagree, and the assembler refuses the `n = 41` row unless they
match (`results/a41/PROVENANCE.md:29-31`). An independent recount by a route
that never reads the assembler agrees (`:49-67`).

What the tower is and is not, for the chapter's wording: for the 19 swept
heights, two engines with no shared code agree on every cell; for heights 20
and up, the tower is a second *implementation* of the same closed forms fed
the same defect tables, not a second source (`AUDIT-2026-09-02.md:81-104`).
The only enumeration that would cross assumption families for `T(41,20)` is
the H = 20 sweep at Nmax 41, priced at about 11 h and 190 GB on dalby and not
run (`AUDIT-2026-09-02.md:78-79, 224-226`).

## 9. What the 2026-09-02 audit says the chapter must and must not claim

`AUDIT-2026-09-02.md`, four read-only lanes over `25d7f61`; nothing was built
or run. Engine-side findings only; the M1–M3 findings are about the checks
around a(41) and belong to the validation section.

**May be quoted as the audit's own statement** (`:32-38`): the engine lane
found no counting defect in the transition, the kink-carry kernel, the
admissibility bound, the ranged count-vector arithmetic, the sharding and
steal protocol, or the checkpoint and resume paths.

**Must not be claimed, or must be scoped** (`:140-154, :179-186`):

- The disk layer does not fail closed everywhere. The plain-format body CRC
  only prints on mismatch and is never invoked on the seeking reads production
  uses; under zstd the last frame of a range-bounded read is never
  checksummed (`:149-151`, `core/runfile.h:1075-1090`). The "fails closed
  rather than losing states silently" paragraph at
  `paper/polyplets-report.tex:382-388` is stronger than this supports.
- The a(40) run predates the short-read fix `b5b4948`, under which a
  truncated frontier body read as end-of-run with exit 0. A dropped record
  loses a whole count vector, so the chain and H21 holdout checks would almost
  certainly have caught it, but it is a residual, not a closed door
  (`:144-148`).
- No manifest or `build/ns/verify` pass is recorded for a(40) or a(41)
  (`:151-152`).
- The H20 byte-identical recheck of a(40) is determinism on the same reader,
  not independence; `results/ns_a40/PROVENANCE.md:133` should not call it
  that (`:152-154`).
- The `u128` ceiling is refused at maxn 48 on the *final row sum* alone,
  while intermediate multi-component counts exceed the row sum; silent wrap is
  prevented only by the `assert(slot >= prev)` guards, live because `NSFLAGS`
  has no `-DNDEBUG`, and `core/counter.h:24-26` still says overflow is silent
  (`:179-186`). Any Nmax ≥ 45 sweep should first measure the largest per-state
  count in an existing run.
- The kink kernel's only independent-oracle gate reachable from `make` goes to
  H ≤ 7; its production validation is the a(29) cell-diff against the column
  kernel and the Motley agreement, neither automated (`:160-166`).

## 10. Suggested shape

The components (§0) first, briefly, since the chapter's reader has only the
three Methods paragraphs to go on. Kernel choice (§1) is the one piece of
mathematics and should follow, with §1a's table saying which kernel produced
which term. Then the utilization story (§2) as the chapter's argument —
measured waste, located ceiling, a fix that works and a fix that provably
cannot — with §3 as its cautionary companion. Then memory and I/O (§4),
representation (§5, now scoped), the negative results (§6, §8), the a(41)
route (§8a), and the cost ledger (§7, §7a) as the closing table. §9 is the
list of sentences not to write. The negatives are worth as much as the wins
here: PGO, LPT, work-stealing at scale, tmpfs past a(34), and cloud all cost
real time and are each reproducible from the notes cited above.
