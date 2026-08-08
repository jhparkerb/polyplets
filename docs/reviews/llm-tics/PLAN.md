> **NOTE: authored by Claude at jasonp's direction, 2026-08-08.** The plan for
> making the L papers read as human prose. Written for jasonp to edit; execution
> resumes from this file post-/clear. Deliberately uncommitted until he has
> marked it up.

# A proscription on model usage

+++ Rewriting the papers with Fable has been very expensive.  No Fable +++
+++ models may be used for this project without a justification and    +++
+++ approval by jasonp.  Do NOT seek justification without cause.      +++

# Readability plan for the six L papers

## Where this starts from

- Trim campaign complete and merged (master `8d3fb86` + fixes through
  `aa4b416`).
- Round 1 tic pass committed as `2301b4e`: 71 candidates, 24 fixed, 47 kept.
  jasonp's verdict: item-level adjudication misses the point — the tell is
  **density**, not individual defensibility.
- The ruler is committed as `26379d1`: `docs/reviews/llm-tics/density.py`
  measures marker constructions per 1000 prose words. Baselines frozen in
  `density-before.txt` (per-paper) and `density-corpus.txt` (64 published
  English papers from `papers/`, 807k words). Run: `python3
  docs/reviews/llm-tics/density.py` (papers) and `--corpus papers`.
- Measured fingerprint vs published p90: dash-asides 10x (2.20/1k vs 0.22),
  clefts 7x (0.92 vs 0.13), contrastive negation 3x (0.96 vs 0.31; L6 at 2.30 is
  above the corpus max), short-declarative cadence 1.5x, mean sentence length
  18-27 words vs ~28.
- Round 2 was launched twice and killed twice (usage window, then jasonp's
  stop). **No round-2 edit has ever been applied**; papers are exactly at
  `2301b4e`+`26379d1` = `aa4b416`-era text plus round 1.

## Ground rules, all phases

- Meaning, scope, and epistemic status of every claim identical before and
  after. Disclosure blocks, draft banners, and L5's three attribution sites
  verbatim. Constants, cites, labels untouched; pinned literals per `CONSTANTS`
  in `scripts/l_trim_gate.sh`.
- Every edit ledgered OLD → NEW in `docs/reviews/llm-tics/round2-*.md`.
- Gates green before any commit: `paper/verify_l_papers.py` (326),
  `tests/gate_l_paper_verifier.py` (46/46), `scripts/l_trim_gate.sh check 5`.
- One commit per phase (per paper in phase 2). Nothing pushed.
- All agents Opus. Agents read this file, the catalog
  (`docs/reviews/llm-tics/catalog.md`), and the round-1 ledgers
  (`findings-L1-L3.md`, `findings-L4-L6.md`) from disk.

## Phase 1 — pilot: L2

L2 is shortest (3,547 words) and has the worst cadence (mean sentence 18.3
words, punch 3.93/1k). One Opus agent rewrites it **at the paragraph level, for
flow**, in the register of the `papers/` corpus — each paragraph re-read and
re-expressed as a working mathematician writes, sentences connected rather than
stacked. The density ceilings (published p90: contrast-neg 0.35, cleft 0.15,
dash-aside 0.30, punch 0.95 per 1k; mean length toward >=25) are the **tripwire
checked afterward, not the writing objective** — rewriting to hit numbers
produces flat mush, which is the failure mode this phase exists to avoid.

Deliverable: the L2 diff, its ledger, before/after density lines. Committed
alone.

**Calibration gate: jasonp reads L2. Nothing else moves until his verdict.** His
notes (too timid / too flat / wrong register / specific dislikes) become part of
the phase-2 brief.

## Phase 2 — the other five papers

Same recipe as calibrated by the L2 read. Order proposal: L6 (contrast-neg
outlier), L1, L3, L4, L5. One agent and one commit per paper, so each is
reviewable and revertable alone. Parallelize only if the L2 verdict was clean.

## Phase 3 — blind referee

A fresh Opus agent reads all six cover to cover with the ledgers and catalog
**withheld** (instructed not to open `docs/reviews/llm-tics/` at all), acting as
a hostile journal referee, and reports every place the prose smells
machine-made: cadence, coinage, uniform paragraph shapes, over-signposting,
anything. A second agent applies what survives scrutiny; re-measure; one commit.

## Phase 4 — exit

- Densities inside the published band for every paper.
- Referee report comes back with nothing actionable.
- The real test: jasonp's own fresh read. Claude's judgment is never the last
  gate — round 1 established that its tic detector under-fires.

## Open choices (jasonp's, edit here)

- Pilot paper: L2 proposed. Alternative: L6.
- Phase-2 commits: per paper (proposed) or one batch.
- Calibration input: prose notes, or jasonp marks up the L2 diff directly.
- Anything in the ground rules he wants tightened or relaxed.
