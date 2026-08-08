> **NOTE: authored by Claude at jasonp's direction.** Resume state for the
> L-trim campaign. Updated in every commit that changes what it describes;
> true of the tree it sits in (PROTOCOL amendment 2).

# L-trim: where this stands

Branch **`l-trim`**, off `master` at `9cebd90`. Nothing pushed, nothing merged.
The branch was **rebuilt on 2026-08-07**: the first running of the campaign
produced a history that misstated itself, and jasonp had it rewritten rather
than annotated. The mistakes and the rules that now prevent them are recorded
in PROTOCOL's Amendments section.

## Done, as of this commit

| commit | what |
|---|---|
| `72ec45a` | phase 0 — PROTOCOL, `scripts/l_trim_gate.sh`, baseline, RED-tested |
| `895d85f` | phase 1 — nine sections removed across all six papers, 34,758 → 33,411 words (−3.9%) |
| `859969e` | checkers hardened — verifier substring repair (mutation gate 12/12), gate checks 6–7 |
| *(this commit)* | PROTOCOL amendments 1–5; this rewrite of STATE |

## Next, in order

1. **Kill matrix** (PROTOCOL amendment 1): pair every check site in
   `paper/verify_l_papers.py` with the RED control or mutation that kills it,
   extending `tests/gate_l_paper_verifier.py`. Own commit. A vacuous site is a
   finding, not a patch.
2. **Apply phase 2.** Argued and adjudicated; ledgers land with the
   application, in one commit, per amendment 2. The applier is written fresh
   from the ledgers by a Fable agent: content-addressed anchors only (two
   residue line numbers in the cuts file are off by one — the verdict's
   "Corrections applied to the ledger" section is the authority), and result
   environments sit between two blank lines, so each removal takes one
   adjacent blank to keep the one-separator invariant.
3. **Phases 3, 4, 5** — paragraphs, sentences, words. Per phase: fresh Fable
   cutter, defender, adjudicator writing the three ledgers and the applier;
   the driving session runs applier + gate and makes the phase's one commit.

## Standing cautions

- Three pinned constants occur exactly once, at **L1:481**, **L4:329**,
  **L5:340** (line numbers valid pre-phase-2). A phase going near them must
  relocate the literal first or gate check 6 blocks the commit.
- `verify_l_papers.py` is frozen (checksum in `baseline.tsv`). Its stale
  comment at `:273` ("the paper says ~2.7 per level") and L5's outdated header
  comment block are post-campaign hygiene, on record here so they are not lost.

## Open, and not this campaign's to fix

- `make gates` red on `gate-citations`: five citations to ayr_pmin48 paths
  from `fb5a0d4`/`f333ec1`, earlier on 2026-08-07, files untouched here.
- **L5 `tab:perim` row 3** states a dir4-by-area exclusion verdict nothing in
  L5 warrants (`sec:exclusions` tests the HV-convex king series and the
  polyomino control, never dir4). Carried from phase 1's verdict.
- The other ~30 `tests/gate_*.py` unaudited for assertions that cannot fail;
  offered to jasonp as a read-only audit, not yet run.

## Compute alongside (as of 2026-08-07 evening)

- **pdk6 square8 n=78 k=6**, dalby, driver PID 2420612 — 454/456 shards at
  last look. **L6 is gated on this run**: four live predictions ride on k=6.
  If k=6 contradicts, L6 needs more than a trim.
- **square4 deep**, dalby, driver PID 2423184 — W=15 banked, W=17 running.
