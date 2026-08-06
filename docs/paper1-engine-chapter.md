# Paper 1, the engine chapter — source material

2026-08-06, sortie plan §2 Paper 1. The record's other half: how a(23)–a(40)
were computed on three home machines. `paper/technical-report.tex` has three
Methods paragraphs; this is the material for the chapter they gesture at.

**This file proposes; it does not edit.** Nothing here is drafted prose.
Every number is quoted with the file that measured it, and the ones that could
be re-derived cheaply were re-derived rather than copied. Where a source note
carries a correction, the correction is what is quoted.

The through-line, if the chapter wants one: **the wins were all in keeping the
cores fed, not in making the kernel faster.** The one genuine algorithmic
change (kink carry) is a base change, and everything else is scheduling,
memory and I/O.

---

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
regression test.

## 2. Utilization was the lever, not cores

`results/a34-utilization-postmortem.md`, `results/utilization-fix-and-ceiling.md`,
`docs/utilization-bottleneck-log.md`. (`results/beyond-polyplets.md` cites a
`results/cloud-investigation-2026-07-07.md` for the cloud half; that file is in
neither the tree nor the history, so the cloud conclusion has to be re-sourced
or dropped before it is printed.)

The a(34) run was measured, from raw per-column telemetry rather than
estimated, at

    TOTAL wall_s = 13300.4   cpu_s = 210666.1   util = 19.8%

and the shape of the waste is the finding: utilization **peaks at H16 (33.6%)
and reverses exactly where the wall-clock lives** — H18 is 70.2% of the run at
17.2% utilization. So the waste was concentrated precisely where fixing it
paid most, which is what ruled out "it is just an average over a fine run".

This is also the answer to the cloud question — at 19.8% utilization, core
count was not the binding constraint — but see the caveat above: the note that
worked that out is missing from the repo, so if the chapter makes the cloud
argument it needs a live source.

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

The investigation refutes the direction of its own question. Going to smaller
counters (16- or 8-bit) needs 4–5 or 9–10 primes respectively, runs *slower*
per pass in scalar code, and — because the dominant cost is enumeration paid
per pass — more primes means proportionally more wall time.

The structural fact underneath: a single `uint64` counter is exact all the way
through **a(25)**; CRT becomes necessary only at a(26)+. For a(21)–a(25), CRT
is a RAM-reduction choice, not a correctness requirement.

Settled design: u32 primes with the 31-bit interleave
(`results/crt-counter-shaping.md`, banked as settled — do not re-litigate).

## 6. PGO: no

`results/terminal-velocity.md`, `pgo-no-go-dalby`.

gcc PGO measured **worse than gcc -O3**: 91.0 s, a 1.84× speedup where the
settled combination of kernel levers gives 2.06×. It was dropped; clang PGO
was blocked on missing toolchain packages on dalby and skipped. The reason is diagnostic rather than incidental: the
workload is **branch-mispredict-bound** — the profile shows IPC 2.37 with a
1.96% branch-miss rate costing ≈9% of cycles — so profile-guided layout has
little left to win. Kernel levers settled at 2.06× (L1 + L3 + L4 + clang).

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

## 9. Suggested shape

Kernel choice (§1) is the one piece of mathematics and should lead. Then the
utilization story (§2) as the chapter's argument — measured waste, located
ceiling, a fix that works and a fix that provably cannot — with §3 as its
cautionary companion. Then memory and I/O (§4), representation (§5), the
negative results (§6, §8), and the a(40) cost table (§7) as the closing
ledger. The negatives are worth as much as the wins here: PGO, LPT,
work-stealing at scale, tmpfs past a(34), and cloud all cost real time and are
each reproducible from the notes cited above.
