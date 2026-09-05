# Unattended work, 2026-09-05

Proposed at jasonp's request before a several-hour absence: work that can run
with nobody watching and moves the repo toward confident publication of
a(19) through a(40). Written at `25d7f61` with the 2026-09-04 working tree
uncommitted. He picks; nothing here starts on its own.

**Scope constraint.** Neither ayr nor dalby is reachable from the session shell
(no agent socket; ayr does not resolve). Every item runs on gympie alone, with
minutes of compute at most. Anything needing a remote box is listed at the end
as not offered.

## The menu

1. **M1, the audit's first item, run locally.** `AUDIT-2026-09-02.md` M1 says
   level 21 of the a(41) tower is pinned from one depth pair whose stated guard
   tests integrality only. The closing test is pure Python over tracked files
   (`experiments/undertow_a41.py --jmax 5 --perheight results/a41`) and its
   imports resolve on gympie. Run the three-pair agreement at level 21, the
   mutation demo (add 9 to `sig[3][21]` in a shadow copy of
   `results/severance_w3_families_K22_e3.txt`; the congruence gate must stay
   green while the `--jmax 4` assembler prints a(41) shifted by 9), and
   `undertow_pin.py --verify --jmax=5` and `--audit --jmax=5`. Then record the
   depth-5 re-pin in `results/a41/PROVENANCE.md` and `results/confidence.md`,
   correct the two overstated sentences (`confidence.md:131-133`,
   `PROVENANCE.md:94`), and wire a level-21 pair-agreement gate into
   `GATE_TARGETS` so the blind spot closes by a check rather than a note.
   This is what the a(41) asterisk (`paper/technical-report-gaps.md` B5)
   waits on. Seconds of compute.

2. **M2 and the local half of M3: the two-source statement carried by
   gates.** Add the tower-from-Motley source tag to
   `scripts/provenance_table.py`; extend `TRIGGER_RE` in
   `scripts/residual_cells.py` to "N of 40 cells" phrasings; add a `rows41` arm
   to `scripts/cutcount_assembly_gate.py` pinned at 589 cells against the
   triangle and 19 against `results/a41` (`results/cutcount_b1/rows41/` C1..C19
   are in the tree); make `motley_reach()` require that match; make
   `experiments/undertow_ri.py` exit non-zero on MISMATCH or "sum WRONG".
   Reword the machine-owned prose sites to the audit's statement, "19 swept
   heights two-source with no shared code; heights 20 and up one tower
   strategy pinned from Motley's data": `results/confidence.md:21,104`,
   `docs/state-2026-08-23.md:16`, `paper/L8-below-onset.tex:107-109`.
   `README.md:111-121` and the staged OEIS text are jasonp's to align or
   freeze. Banking the residues (M3 proper) needs dalby and stays open.
   Result: the 779-cell Motley agreement at Nmax 41, which the audit says is
   "recorded nowhere in the tree", becomes gated.

3. **Gate hygiene, red-first.** From the audit's small-items list:
   `tests/gate_g2.py:121,146` and `tests/gate_holes.py:43` pass on empty
   engine output; `tests/gate_sym.py:98` and `tests/gate_subgroup.py:78`
   note-skip instead of `gate.skip()`; `tests/gate_modp.py` ignores the
   engine exit status; `undertow_a41.py --selftest` trips the integrality
   exit before the regression it names, and `undertow_pin.py` RED 1 and 3
   are linear-algebra tautologies. Each fix shown red before green. The
   Redelmeier gate is what backs a(19) to a(22). Full `make` at the end,
   about five minutes.

4. **A kink independent-oracle gate.** The kink kernel produced a(30) to
   a(40) and its only in-make oracle gate reaches H <= 7 (column and kink at
   maxn 14, where H >= 8 is injected). Add
   `--kernel kink --max-diag-k 0 --maxn 16 --compare` (minutes) plus an
   exhaustive kink-equals-column check at H <= 6, wired into `ns-gates` if it
   overruns the `make gates` budget. `build/ns/orchestrate` exists on gympie.

5. **Refresh the Reproducibility source material.** jasonp writes that section
   next (`technical-report-gaps.md`, decisions of 2026-09-04) from
   `docs/paper1-reproducibility.md`, dated 2026-08-06. It predates Undertow
   and Motley to H = 19; lists 11 kink-only cells where the audit counts 3
   (`T(39,20)`, `T(40,20)`, `T(40,21)`); omits Motley as the machine-work
   pointer he decided on; and its §6 and check E of
   `experiments/paper1_reproducibility_check.py` print row shares, the banned
   framing. Regenerate every number, restate coverage in cells, fold in the
   outcomes of items 1 and 2. Zero compute.

6. **Bibliography (B3).** A new file `paper/technical-report.bib` plus a note
   naming each sentence in the tex that would take a cite and its key:
   Redelmeier, Klarner-Rivest, Jensen, Barequet-Ben-Shachar, Bacher, Madras
   (`arXiv math/9902161`), Mertens, the OEIS entries. Entries checked against
   the PDFs in `papers/`; unfindable ones to `papers/MISSING.md`.
   `paper/technical-report.tex` is not touched.

7. **Commit and push the 2026-09-04 working tree.** The abstract rewrite in
   `paper/technical-report.tex`, `paper/technical-report-gaps.md`,
   `docs/paper1-engine-chapter.md`, `AUDIT-2026-09-02.md`,
   `docs/prove2me-note.md`. `paper/verify_technical_report.py` is 781 green on
   it as of this writing.

**Order if all are approved:** 1, 3, 2, 4, then 5 and 6, one full `make`,
then 7.

## Not offered

- Anything on ayr or dalby: banking the Motley residues (M3), the H = 20 sweep
  at Nmax 41, the a(30) H17 column cross-check close-out.
- Every C-item in `paper/technical-report-gaps.md`: his prose.

## Disposition

**2026-09-05 ~09:20, jasonp: "execute docs/unattended-2026-09-05.md"**, then
"I'm afk all day, do not stop working on a prompt for me, just behave
reasonably. keep most of the compute running on dalby to the extent possible,
jobs are permitted on gympie if there is no reasonable fear they will OOM the
machine." All seven items approved.

Two departures from the text above, both recorded here rather than asked:

- **Item 7 was done first**, not last. Items 1-6 edit files the 2026-09-04
  working tree also touches (`paper/technical-report-gaps.md`,
  `docs/README.md`), and committing his tree on its own first keeps his prose
  in a commit of its own. The full `make` still runs at the end.
- **The scope constraint was wrong by the time work started**: `ssh dalby`
  works from the tool shell (his `ssh dalby hostname` at 09:2x, and mine). So
  M3's banking half -- copying the 171 residue rows, the timings and the
  console logs out of `dalby:~/var/motley-ladder` and gating them -- is done
  with item 2. It is a file copy, not compute. The H = 20 sweep at Nmax 41
  (~11 h, ~190 GB) stays unlaunched: frontier rule, >1 h needs his explicit
  go, and it is his call in the audit's own words.
