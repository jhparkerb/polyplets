# The gate-class sweep — asking all 33 gates whether they can fail

2026-08-22, executing `docs/time-at-the-bar.md` B1. `docs/last-orders.md` named
this and did not do it.

**The question, asked once of each member of `GATE_TARGETS`:** does this gate
touch ground truth, or does it compare two artifacts that a single stale input
makes wrong together?

**The method, per the standing rule:** red-first. For each gate, plant the
staleness the gate is supposed to catch and confirm it goes red. *A gate that
stays green under its own planted failure is the finding.*

**The failure that prompted it.** `make gate-provenance` stayed green while the
front-door provenance table went a height stale, because the gate compared the
published note against its generator and a hand-edited `MOTLEY_H = 18` made both
stale together. That constant is now derived from the banked row directories.
The question was whether the pattern was swept. It was not, and this file is the
sweep.

## What the sweep found

Two defects, both fixed here. Three limits, reported and not fixed because each
is a deliberate design choice that a reader should nevertheless know about.

**The suite came out of this well.** Thirty-one of thirty-three gates put
external ground truth, an independent reimplementation, or the filesystem on the
expected side. The two that did not are the two below.

### F1 — `gate-cutcount-assembly` had the same defect, in the same shape. FIXED.

`scripts/cutcount_assembly_gate.py` carried `NMAX = 40`, hand-edited, and its
assembly loop is `for n in range(1, NMAX + 1)`.

Planted: 41 fabricated rows for `n = 41` appended to `results/triangle.txt` —
what the file will genuinely look like the day a(41)'s per-height table is
banked, which is what `docs/five-terms-plan.md` is for.

| gate | under the planted growth |
|---|---|
| `gate-provenance` | **RED**, all six figures — `cells_total` 861 vs 820, and so on |
| `gate-residual-cells` | **RED** |
| `gate-cutcount-assembly` | **GREEN** — it never looked at the new rows |
| `gate-bfiles` | GREEN, for a different and defensible reason (F4) |

`NMAX` is now derived from the triangle, the way `MOTLEY_H` was. The pinned
counts beside it then do the work: the day the triangle grows, `EXPECT_CELLS`
and `EXPECT_HELDOUT_CELLS` stop matching and the gate fires, which forces the
coverage question to be answered deliberately instead of silently narrowing.

Re-probed after the fix: **RED** under the same plant (`held-out check covered
40 of 41 cells, pinned at 41`), GREEN with the triangle restored, `--selftest`
still green.

### F2 — `results/strip-mu-certificates.md` was stale, and no gate reads it. FIXED (the note).

Found by asking what `gate-strip-fast` puts on its expected side. It pins seven
certified numerators as a `CERTS` dict, hand-transcribed, with a stated reason
(the log is append-only and a scheduled run may be writing to it). The
transcription is safe in the direction that matters — the numerators are checked
against the *engine*, so a typo goes red — but it means **nothing in the gate
suite reads `results/strip-mu-certificates.md` at all**, and seven files cite it.

It had drifted. Its headline table stops at H = 11 and its *Honest scope*
section said "`H >= 12` is not certified yet", while:

- `results/strip_mu_certificates.log` carries H = 12, 13 and 14 as `result=PASS`,
  **twice each** — once under `git=4ab40fa` and again under `900b4ff` after the
  frozen-kernel adoption, with identical `num` both times;
- the same note's own 2026-07-31 addendum discusses those very runs;
- `paper/L3-lambda-bounds.tex:252` has published the H = 14 row since.

The note now carries the three receipts and marks the stale bullet as stale.
What is *not* fixed is the structural gap: this artifact is still checked by
nothing. Closing it is a gate that parses the note against the log, which is a
change and not a sweep finding, so it is written down here rather than made.

### F3 — one gate can decline to run and still leave `make gates` green.

`gate-mk-dir4-perim` is wrapped in `$(if $(GMP_LDFLAGS),...)`. Without GMP it
prints

    *** GATE MK-DIR4-PERIM NOT RUN: no GMP, and this gate has no banked-series
    fallback -- NOTHING was verified ***

and `make` exits 0. This is deliberate and it is loud, and the recipe says the
true thing in the plainest available words. It is recorded because it is the one
case where "all gates green" means 32 gates, not 33, and the clean-clone run at
R is exactly the circumstance that would produce it. It ran here (GMP is present
on gympie): `GATE MK-DIR4-PERIM: GREEN`.

### F4 — `gate-bfiles` narrows its own coverage silently.

`derive()` skips any `n` absent from the symmetry counts (`if n not in r180:
continue`) rather than defaulting it — correct, and the code says why: "the term
is simply not derivable and is skipped rather than defaulted". But the skip is
not counted or reported, so a triangle row with no symmetry data produces no
signal of any kind. That is why it stayed green under F1's plant. The neighbours
`gate-provenance` and `gate-residual-cells` cover the same growth, so nothing is
unguarded; what is missing is a line saying which `n` were skipped.

### F5 — the external anchor is checksum-pinned, not re-verified.

`fixtures/` is protected by `SHA256SUMS`, and `gate_g1` checks it before doing
anything else — corrupting `fixtures/b006770.txt` by 1 turns `gate-g1`,
`gate-g2` and `gate-sym` red, and correctly leaves `gate-s2` green because it
reads different fixtures. But `SHA256SUMS` is itself regenerable, so the pinning
is against accident and not against a deliberate edit of both. Nothing re-checks
a fixture against OEIS, and nothing can without network access in the gate
suite. The mitigation already in the tree is that the b-file headers record the
OEIS revision and date they were checked against — `b006770.txt` says "Re-checked
live 2026-08-19: entry revision 44 (2026-05-30)". That is the right control for
this; it is a provenance record rather than a gate, and it should not be
mistaken for one.

## The 33, classified

`GT-ext` external ground truth (OEIS, published literature). `GT-oracle` an
independent reimplementation — different algorithm, usually a different
language — computed at gate time. `GT-fs` the filesystem or git. `art-gen` a
published artifact against its generator: the failure class.

**probe** = a defect was planted in this sweep and the result observed.
**controls** = the gate's own RED controls were run. **read** = classified by
reading it; no new probe was run, because the gate already carries per-site
kills or its expected side is plainly external.

| # | gate | expected side | class | evidence |
|---|---|---|---|---|
| 1 | `gate-citations` | git + disk | GT-fs | **probe**: a never-existed path → RED; a path deleted today → `history`, allowed by design and counted. 3 controls fire |
| 2 | `gate-docs-index` | `git ls-files docs/` | GT-fs | **probe**: a *staged* unindexed docs file → RED. An untracked one is invisible, which is the right scope |
| 3 | `gate-no-copyright-pdfs` | `git ls-files` | GT-fs | read + 2 controls, one of them against a vacuous pass when the git call fails |
| 4 | `gate-receipts` | path exists, non-empty, in-tree | GT-fs | **controls**: `--self-test` green |
| 5 | `gate-provenance` | banked rows + triangle | art-gen | **probe**: planted growth → RED on all six figures. `MOTLEY_H` derived |
| 6 | `gate-residual-cells` | same, via `import PT` | art-gen | **probe**: planted growth → RED. Imports `PT.NMAX`/`PT.SWEEP_H`, so the two generators cannot disagree |
| 7 | `gate-cutcount-assembly` | Motley rows + triangle | art-gen | **probe**: **F1**, green under planted growth. Fixed, re-probed RED |
| 8 | `gate-undertow-congruence` | integrality mod `3^(k+j)` | GT-arith | **controls**: `--selftest` green; 4 controls, one transitive through the pin `D_4(21)` feeds |
| 9 | `gate-bfiles` | OEIS + triangle row sums | GT-ext | **controls** green; **F4** on silent skips |
| 10 | `gate-l-paper-verifier` | 51 `ok()` sites, each with a named kill | GT-mutation | read. A kill matrix with `mut:`/`res:`/`patch:`/`red:` mechanisms and VACUOUS sites reported loudly. This is the standard the sweep was measuring against |
| 11 | `gate-perimeter-min` | `g2 --siteperim` | GT-oracle | read: complete brute force on small boxes, an entirely different search (growth, not complementation) |
| 12 | `gate-perimeter-min-shard` | the monolithic run | GT-oracle | read: byte-for-byte, plus four kinds of damaged frame each of which must be refused |
| 13 | `gate-perimeter-defect` | `g2 --siteperim` | GT-oracle | read: 4 arms, incl. pruned-vs-unpruned and shard-sum |
| 14 | `gate-g1` | OEIS b-files under `SHA256SUMS` | GT-ext | **probe**: corrupted fixture → RED |
| 15 | `gate-g2` | b-files + the G1 Python oracle | GT-ext + GT-oracle | **probe**: corrupted fixture → RED |
| 16 | `gate-tma` | b-files + G2 marginals + ASan | GT-ext + GT-oracle | read; ran green in the full suite |
| 17 | `gate-s2` | A000105/A030222 + Burnside identities | GT-ext | **probe**: correctly unaffected by the b006770 corruption — it reads other fixtures |
| 18 | `gate-e0` | exhaustive `2^V` in Python | GT-oracle | read: different language, different method |
| 19 | `gate-sym` | brute oracle + A030222 | GT-ext + GT-oracle | **probe**: corrupted fixture → RED |
| 20 | `gate-symtm` | `symcount_fast` | GT-oracle | read: cross-algorithm, and the oracle is itself gated by #19 |
| 21 | `gate-subgroup` | three order-4 subgroup families | GT-oracle | read: reaches n = 40 by a route the full engine does not use |
| 22 | `gate-euler` | hand cases against `cpp/tma/euler.h` | GT-oracle | read |
| 23 | `gate-driver` | injected corruptions must be refused | GT-behav | read: red-first by construction — it exists because a dead sweep's empty output once summed as a zero |
| 24 | `gate-strip-cert` | the binary's own kills | GT-behav | **controls**: `--selftest` green — a corrupted transition table and a corrupted finalize map must both move `mu_6`, and an over-claim and an all-zero vector must both be refused |
| 25 | `gate-strip-fast` | the old map engine + pinned numerators | GT-oracle | read; **F2** on the note nothing reads |
| 26 | `gate-king-grid` | plan acceptance vs the grid pass | GT-oracle | read + controls present |
| 27 | `gate-site-perim` | convention pinned before the code | GT-oracle | read |
| 28 | `gate-multidirected` | GF series vs Redelmeier brute | GT-oracle | read: exact integer series to n = 200 against a DFS |
| 29 | `gate-convex-dfinite` | positive and negative controls on the guesser | GT-behav | read: the claim is a negative, so the gate keeps the guesser powered |
| 30 | `gate-middle-kingdom` | the Phase 0 grid pass | GT-oracle | read |
| 31 | `gate-mk-dir4-perim` | `directed_cone_anchor` brute | GT-oracle | read; **F3** on the GMP skip |
| 32 | `gate-dir4-perim-alg` | the banked series + a negative control | GT-oracle | **probe**: one banked term perturbed by 1 → RED, 13 failures |
| 33 | `gate-compile-db` | a real `-fsyntax-only` compile | GT-behav | read: completeness first, then every entry compiled with exactly its recorded flags |

## What was not swept

The two gates deliberately outside `GATE_TARGETS` — `gate-motley-par` (needs
`build/motley_par`) and the depth-5 gate `experiments/severance_w3_depth5_gate.py`
(correctly RED in production until the `emax = 4` table exists). Neither is part
of what `make gates` claims, so neither is part of what a reader is told to
trust. The Makefile's own comment already asks for a lint that would catch a
`gate-foo:` recipe never reaching `GATE_TARGETS`; that lint still does not exist,
and it is the meta-version of this sweep.

## Reproduce

Everything above was run against `c25fefe` plus the same day's C-section
changes. The full suite was green (`make exit code: 0`) before the sweep began
and the two fixes are the only gate-affecting changes it made.

    scripts/run_full_make.sh results/make_<topic>.log     # the whole suite

The plants were applied to the working tree and reverted with `git checkout`
immediately after each observation; `fixtures/SHA256SUMS` was re-verified clean
afterwards (15 OK, 0 failures).
