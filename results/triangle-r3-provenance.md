# Round-3 provenance scout — ADV-2 (binary provenance of the a(40) run) and ADV-5 (transpose accounting)

2026-08-12, wave-4 scout off the idea queue. Carries queue rows ADV-2 (the
cost adversary's row at `results/triangle-r3-queue.md` line 91 — note the
queue has an id collision: a second, unrelated "ADV-2" from the independence
adversary appears at line 96, already CLOSED by ADV-4; this file addresses
the line-91 row only) and ADV-5.

Method: reading, greps, git, plus read-only seconds-scale `ssh` listings and
greps on dalby (`~/src/polyominoes/runs/ns_a40/dalby/`), where the run
artifacts the repo cites actually live. No compute, no writes anywhere but
this file and the queue.

## Mapped disclosure block (phase-1 mapping per the round brief)

    claim:                             the banked a(40) phase A/B/C binaries are
                                       identified by build-stamped log banners, per
                                       phase, with one named gap (worker binaries)
    share of a(40) reached:            audit covers the provenance of 95.86% of
                                       a(40) (all real-swept bands H3..21); it adds
                                       0 enumeration bits — provenance, not counting
    bits against enumeration error:    0 (no cell recounted)
    bits against formula-chain error:  0 (no formula touched)
    rule independence:                 N/A — this is an audit of binary identity,
                                       not a counting route; ADV-5 is
                                       consistency-class by the standing ruling
                                       and is filed under that name
    derivation independence:           N/A — audit reads the banked record itself
    input footprint:                   0 cells consumed as inputs to any prediction
    checker:                           the reader repeats it: grep the banners in
                                       runs/ns_a40/dalby/run.log (dalby) and
                                       results/ns_a40/recheck/run.log (repo), then
                                       `git show <rev>` — minutes, no compute.
                                       RED control: a banner with a rev not in git,
                                       a `-dirty` suffix, or a kernel!=kink field
                                       would each fail the audit; none occurs
    sensitivity:                       N/A for an audit (nothing fitted); the
                                       failure modes above are what "broken input"
                                       looks like here
    prior-work grep:                   git log --all --oneline --name-only --
                                       'results/*.md' 'docs/*.md' 'docs/**/*.md'
                                       | grep -i 'provenance\|audit' — the
                                       AUDIT-2026-07-30 campaign exists (P4/P5/D1
                                       etc.) but audited artifacts and validation
                                       gating, not binary identity; the r3 harness
                                       filed binary provenance NOT ESTABLISHED and
                                       no lane picked it up

---

## TASK 1 — ADV-2: binary provenance of the banked a(40) run

### What a log header can and cannot establish here (read this first)

There are two different "rev" records in this system and they have different
evidentiary weight:

- **Script echo — testimony.** `scripts/dalby_term.sh:93` prints
  `rev: $(git rev-parse --short HEAD)`: the checked-out *tree*'s HEAD at
  launch, which says nothing about what the binary was built from, and does
  not capture dirtiness. This line also goes to the driver's stdout, *outside*
  the `tee -a "$RUNDIR/run.log"` that captures orchestrate — so it is not
  even present in the surviving run.log.
- **Orchestrate banner — evidence.** `orchestrator/cmd/orchestrate/main.go:193`
  prints `orchestrate maxn=... rev=%s` where the rev is **stamped into the
  binary at build time** via `-ldflags "-X main.gitRev=$(GIT_REV)$(GIT_DIRTY)"`
  (`Makefile:9-10,704`; `main.go:330-333`). `GIT_DIRTY` appends `-dirty` when
  the tree differs from HEAD. A banner rev therefore identifies the exact
  clean tree the *orchestrate* binary was compiled from. It does **not**
  identify the C++ worker binaries — see the gap below.

What was actually banked in the repo: `results/ns_a40/` holds no phase A/B/C
log at all. `validate-2026-07-30.log` says so explicitly ("The a(40) run's own
stdout was never banked", AUDIT-2026-07-30 P5) and is itself a labelled
post-hoc artifact-consistency regeneration, not run evidence.
`rundir_size.log` is du telemetry (timestamps only, no rev).
`recheck/run.log` is the H20 recheck, not the production run. So **on the
repo alone, phase A/B/C binary identity is pure testimony** — the harness's
NOT ESTABLISHED was correct.

But the production run's teed stdout **survives on dalby**:
`~/src/polyominoes/runs/ns_a40/dalby/run.log`, 3,821,306 bytes, mtime
2026-07-28 09:44 EDT (dalby's clock is EDT; `date` verified), alongside
`POLYCKPT.A/B/C`, `h20.out.zero-harvest-bug`, `cost_profile.tsv`,
`combine.log`, `a_n.txt`, and mid-run merge shards (`merge_h20_c7_*`, mtimes
2026-07-26 07:32). "Never banked" was accurate; "never captured" would not
have been. The audit below reads those banners.

### The banners (quoted from dalby, `runs/ns_a40/dalby/run.log`)

Eight `orchestrate` invocations, in append order; `grep -c dirty run.log` = 0
(no `-dirty` stamp anywhere); every banner says `kernel=kink counter=u128
ram=1073741824 run_dir=runs/ns_a40/dalby maxn=40`:

| line | cores | rev (build-stamped) | resuming from | reading |
|---|---|---|---|---|
| 1 | 80 | `38956525` | — | phase A launch, 07-25 20:42 EDT |
| 15060 | 64 | `38956525` | — | **phase B first segment, 64 cores** (~03:00 07-26) |
| 16263 | 80 | `801afd59` | H=-1 (A complete, no-op) | relaunch re-enters A |
| 16267 | 48 | `801afd59` | H=20 col=6 | **phase B resumed, 48 cores, new binaries** |
| 19307 | 32 | `801afd59` | — | phase C first launch, died at t=0 (`--resume`, no checkpoint; the dd748c4 bug) |
| 19309 | 80 | `801afd59` | H=-1 (no-op) | relaunch re-enters A |
| 19313 | 48 | `801afd59` | H=20 col=40 | re-enters *completed* B — **this is the Zero Harvest write** |
| 19317 | 32 | `801afd59` | — | phase C real run, 07-26 21:19 → 07-28 09:44 EDT |

Corroborating mtimes/content, all consistent: `POLYCKPT.A` 07-26 02:59 (=
claimed phase A end); `merge_h20_c7_*` shards 07-26 07:32 (phase B mid-col-7
before its interruption; the resume banner's `col=6` checkpoint is exactly one
column behind); `POLYCKPT.B` 07-26 21:16 (last touched at the Zero-Harvest
re-entry, = the claimed relaunch minute); `POLYCKPT.C` and run.log 07-28 09:44
(= claimed phase C end); run.log tail shows H=21 col=40 finalize with
`cum_wall_s=131071.0`, `rss_max_mb=4045.3` — PROVENANCE.md's 131,071 s and
4045 MB to the digit. Repo-side, `rundir_size.log` starts 07-25 20:43:30 EDT
(= claimed 20:42 launch + first du sample).

### Do the recorded revs match what the record says they select?

- `38956525` = "dalby_term: phased execution for N>=40", committed 07-25
  19:41:47 -0500 (20:41:47 EDT) — one minute before launch; it is the commit
  that *created* the phased driver. `801afd59` = "Overcommit Hydra head 5:
  malloc_trim", its direct child (`git log 3895652..801afd5` shows nothing
  between), committed 07-26 10:35 -0500 — inside phase B's interruption
  window. Both exist on `second-wind` (and master).
- `git show 38956525:scripts/dalby_term.sh` and `801afd59:...`: both pass
  `--kernel kink` in every invocation (single and `run_phase`), tee to
  `$RUNDIR/run.log` with `RUNDIR=runs/ns_a40/dalby`, and gate the
  `FRONTIER_LEVERS=1` env exactly as PROVENANCE.md's launch line says. The
  kernel the banners record (`kernel=kink`) is the kernel the record claims.
- `max_diag_k=0` in every banner = no override; P_19 was not wired until
  `9671e94` (post-run), so the reproduction note's concern is prospective
  only. H21 being a *real* sweep is directly evidenced by ~36 h of
  `event=column H=21` lines ending at col=40.
- `dd748c4` (the per-phase-resume fix, committed 07-26 21:18:39 EDT) touches
  **only** `scripts/dalby_term.sh` — which is why the phase C binaries still
  carry the `801afd59` stamp: no Go/C++ source changed, nothing to rebuild.
  The relaunch at 21:16 EDT ran the fixed script two minutes before its
  commit; the fix's content is what git records, its at-run state is
  testimony (and immaterial to binary identity).

### Per-phase provenance table

| phase | PROVENANCE.md claim | evidence found | testimony or evidence | verdict |
|---|---|---|---|---|
| A (H1-19 + H22-40) | 80 cores, rev `38956525` | banner line 1: cores=80 rev=38956525, no -dirty; POLYCKPT.A mtime = claimed end | **evidence** (orchestrate binary), inference (workers, see gap) | **CONFIRMED** |
| B (H20 solo) | "48 cores", no rev claimed | banners 15060 + 16267: **two segments** — cols 0..6 at 64 cores rev `38956525`, cols 6..40 at 48 cores rev `801afd59` | **evidence**, and it **corrects the claim** | **CONFIRMED with erratum**: PROVENANCE.md's "48 cores" describes only the second segment, and B ran under *both* revs. The claimed cum_wall 34,463.8 s and rss 1023 MB were not independently re-derived here (would need summing both segments' column lines) |
| B zero-harvest re-entry | incident narrative | banner 19313 (resume from completed H=20 col=40) + `h20.out.zero-harvest-bug` (191 B, preserved) | evidence | **CONFIRMED** — matches the incident text exactly |
| C (H21 solo) | 32 cores, rev `801afd59`, 07-26 21:19 → 07-28 09:44, cum_wall 131,071 s | banners 19307 (t=0 death) + 19317; tail cum_wall_s=131071.0 rss 4045.3; POLYCKPT.C mtime 09:44 | **evidence** (orchestrate), inference (workers) | **CONFIRMED** (t=0 death also directly visible, as claimed) |
| H20 recheck | "phase B's exact config, 48 cores", 43,747 s | repo-banked `recheck/run.log` line 1: cores=48 kernel=kink rev=`db01b5d4`; kernel sources byte-identical `801afd5..db01b5d` (only scripts/docs between) | **evidence** | **CONFIRMED**; note PROVENANCE.md never names the recheck's rev — it is `db01b5d4`, the recheck commit itself |
| validate log | A40_VALIDATE_PASS, chain 19/19 | `validate-2026-07-30.log`, self-labelled post-hoc VALIDATE_ONLY at `fac2b85` | evidence *about the banked artifacts today*, by its own honest header not about the original run | as labelled |

### Where the chain is testimony rather than evidence — the one real gap

**The C++ worker binaries (`map_worker`/`merge_worker`) — the processes that
actually count — are not self-identifying.** The banner rev is the
*orchestrate* binary's stamp; orchestrate passes *its own* rev to workers for
POLYRUN headers (`orchestrator/worker.go:91,118`), so shard headers echo the
orchestrator, not the worker build. `worker/` contains no GIT_REV logging
(the baked `-DGIT_REV` from `Makefile:12` is used by `cpp/obs.h` tools, not
by the ns workers). The script runs `./build/ns/orchestrate`, whose
`findWorkers()` falls back to the *unsuffixed* `build/ns/map_worker` — the
rev-suffixed same-rev pairing (`main.go:335-350`) applies only to the
installed `~/bin` layout, not to this run. And the run-time worker binaries
no longer exist: everything in dalby's `build/ns/` is mtime 07-28 12:45,
stamped `db01b5d4` — the post-run rebuild for the recheck.

So worker identity rests on inference, which is strong but is inference:

1. `801afd5`'s whole point was a *worker* change (`worker/worker_util.h`
   malloc_trim). The resumed B and C ran to completion without the OOM deaths
   that motivated it (five kills before; zero after) — behavioral evidence
   the workers were rebuilt.
2. Even under a stale-worker hypothesis, the candidate window is tiny and
   semantically inert: the only commit between the two banner revs is the
   malloc_trim itself, and the last change to any counting-kernel source
   (`core/kink.h`, `core/kink_column.h`, `core/transition.h`,
   `core/classifier.h`, `core/mapreduce.h`) before the run is `a82f55c`
   (07-23, IO framing). Any binary built from any tree between 07-23 and the
   recheck has byte-identical counting-kernel source.

What would have converted this to evidence: workers printing their own baked
GIT_REV per session, echoed into run.log (and ideally checked against the
orchestrator's). That is a successor row, not a retrofit — nothing can now
establish the July worker binaries' identity beyond the inference above.

Second, smaller testimony item: everything on dalby is one `rm -rf` from
gone. The record's strongest evidence (run.log, the checkpoints, the
preserved zero-harvest file) is cited by the repo but lives outside it,
unbanked and unhashed.

### ADV-2 verdict

**Clean, with one erratum and one named gap.** Every checkable assertion in
`results/ns_a40/PROVENANCE.md` about revs, kernel, cores (except phase B's),
timing, walls and RSS is confirmed by build-stamped banners and artifact
mtimes; no `-dirty` build, no unexplained invocation, no rev outside git,
`kernel=kink` throughout. The erratum: phase B ran in two segments, cols 0..6
at 64 cores under `38956525` and cols 6..40 at 48 cores under `801afd59` —
PROVENANCE.md's "48 cores" flat is incomplete, and it claims no rev for B at
all. The gap: worker-binary identity is inference (bounded, semantically
inert window), not evidence, for all three phases. For the exposure band
specifically: H=15..19 swept in phase A (rev evidence `38956525`), H=20 by
the two-segment phase B plus the byte-identical `db01b5d4` recheck, H=21 by
phase C (rev evidence `801afd59`). No phase's *orchestrate* identity rests on
assertion; every phase's *worker* identity rests on the same bounded
inference.

Whether to add the phase-B erratum to `results/ns_a40/PROVENANCE.md` is
jasonp's call; this file does not edit the banked record.

---

## TASK 2 — ADV-5: transpose-accounting consistency

The identity: a(n) is fixed (translation-only) counting, so 90° rotation is a
bijection sending height-exactly-H animals to width-exactly-H animals — the
height marginal vector T(n,·) must equal the width marginal cell-for-cell.

**Status: never exercised, anywhere, at any n — because no width-marginal
data exists in this repo.** The per-height artifacts (`h*.out`) are bare
`n count` rows keyed by H only; `cost_profile.tsv` is per-column *cost*, not
per-width counts; the Redelmeier confirmations (`redelmeier_row20/22`) banked
whole-row totals with no bounding-box binning; grep over `results/*.md` and
`docs/*.md` finds transpose used only for symmetry counting (symtm r180,
dmirror) and the 45° stratification bijection, never as a marginal-accounting
check. The cost adversary's phrasing ("the sweep computes the two by
different accounting") is aspirational: the sweep computes exactly one of
them.

What it would take, honestly costed:

- **At n=40 (the band):** the width of an animal is the index of the column
  at which its last component completes — the sweep has this at attribution
  time, so a per-width (or full T(n,H,W) joint) accounting is a small
  modification to the completion path, near-zero marginal runtime *in the
  same pass*. But there is no pass to piggyback on: banked h*.out cannot be
  re-binned, so exercising the identity on the band means **a full band
  re-sweep with the modified accounting — the same ~52 h of dalby phases the
  production run cost**, plus a build, which this round does not do. It is
  "cheap" only relative to an independent method, not in absolute terms.
- **What it would test:** the check runs the same union-find rule, so it is
  consistency-class by the standing ruling (2b3115b) — filed under that name.
  Its distinctive value is that it stresses the *height-exactness accounting*
  (touch flags / attribution), a different shared proposition (harness Part 3
  proposition 3) than the connectivity partition, and its failure mode
  (mis-binned H) is disjoint from mis-*counting*. It adds 0 bits against the
  connectivity objection.
- **Small-n witness, actually cheap:** g2 (Redelmeier, rooted growth — no
  frontier, no completion predicate) can bin by bounding box at n ≤ ~16 in
  minutes, giving both marginals from a non-frontier algorithm and comparing
  each against the banked T(n,·). That is a definition-level witness that the
  sweep's H-attribution is right, runnable today with one small tool, and is
  the form of ADV-5 worth dispatching first. Filed as a successor row, not a
  job request — it needs a ~50-line tool that does not exist yet, and the
  round does not build.

**ADV-5 verdict: NOT EXERCISED — assumed everywhere, run nowhere.** Nothing
suggests it would fail; nothing has ever tested it. What would establish it:
(cheap tier) the g2 bounding-box binning at small n; (band tier) a per-width
accounting mode in any future re-sweep of H=15..21, at near-zero marginal
cost *if and only if* such a re-sweep runs for some other reason (e.g. the
L6-1/window-census phase 2).

---

## Successor rows (appended to results/triangle-r3-queue.md)

- PROV-1 — wire worker self-identification: ns map/merge workers print their
  baked GIT_REV per session into run.log; orchestrate compares against its
  own stamp and refuses a mismatch (fail-closed). Closes the one testimony
  link in ADV-2 for every future run. Kind: observability engineering.
- PROV-2 — bank the dalby-side evidence: `runs/ns_a40/dalby/run.log` (3.8 MB),
  `POLYCKPT.A/B/C`, `h20.out.zero-harvest-bug` (or a hash manifest of them)
  into `results/ns_a40/` before any dalby cleanup deletes the only build-
  stamped record of the production banners; carries the phase-B erratum with
  it. Kind: record preservation, jasonp's call on the PROVENANCE.md edit.
- PROV-3 — ADV-5 small-n witness: g2-based bounding-box binning at n ≤ 16,
  both marginals from a rooted-growth (no-frontier) algorithm vs banked
  T(n,·); definition-level test of the H-attribution proposition. Kind:
  cheap consistency instrument, needs one new small tool.
- PROV-4 — ADV-5 band tier: per-width/joint (H,W) accounting as a rider on
  any future band re-sweep (window-census phase 2 or otherwise) — near-zero
  marginal cost in-pass, impossible retroactively. Kind: standing rider on
  phase-2 planning, consistency-class.

## NOT ESTABLISHED

- Worker-binary identity for phases A/B/C as *evidence* (vs the bounded
  inference above). Nothing on disk can now establish it; PROV-1 prevents
  the gap in future runs.
- Phase B's claimed cum_wall 34,463.8 s / rss_max 1023 MB were not re-derived
  from the two segments' column lines (would need summing ~3,000 log lines
  across the interruption; nothing turns on it).
- Whether `runs/ns_a40/dalby/` still holds any *frontier/shard state from the
  H=15..19 or H=21 phases* usable for the cost adversary's ADV-4-adjacent
  "archived-state replay" idea (queue row ADV-3-territory): the directory
  listing shows H20 col-7 merge shards surviving; a full inventory of the
  466 KB directory entry (thousands of files) was not taken. One `ssh ls`
  pattern per height would settle it.
