# OEIS submission — authoritative index and case file

2026-07-16. **This file decides scope and order.** The three older lists
(`submissions/oeis/README.md`, `oeis/README.md`, `results/oeis-candidates.md`)
keep their per-item detail but their status sections defer here.

**Nothing is submitted by Claude, ever.** jasonp pushes every button
([[publishing-is-jasonps-call]]); submission is further gated on his viva
([[oeis-submission-viva-gate]]) and the human steps in the checklist below.

---

## 1. What we have (inventory, by wave)

### Wave 1 — extensions to six existing entries (submit first)

The least arguable, highest-value batch: new terms for 30-year-old `hard`
sequences, nothing about novelty to defend.

| entry | staged | b-file | new terms | anchor |
|---|---|---|---|---|
| A006770 (fixed polyplets) | `oeis/A006770.txt` | `results/b006770_upload.txt` | a(19)–a(35), +a(36) as %C conjecture | a(1)–a(22) two-algorithm |
| A030233 (one-sided) | `oeis/A030233.txt` | `results/b030233_upload.txt` | a(18)–a(34) | Burnside from A006770 + r90/r180 |
| A030222 (free) | `oeis/A030222.txt` | `results/b030222_upload.txt` | a(18)–a(32), +a(33) %C conjecture | Burnside (needs dmirror) |
| A030234 (bilateral) | `oeis/A030234.txt` | `results/b030234_upload.txt` | a(18)–a(32), +a(33) %C | (E+G)/2 identity |
| A030235 (asymmetric) | `oeis/A030235.txt` | `results/b030235_upload.txt` | a(18)–a(32), +a(33) %C | A030222 − A030234 |
| A194596 (free non-poly) | `oeis/A194596.txt` | `results/b194596_upload.txt` | a(18)–a(32) | A030222 − A000105 |

All six b-files audited 2026-07-16: zero disagreement with live OEIS terms on
every shared index, contiguous, format-clean, cross-entry Burnside identities
verified numerically at every shared n (see §5).

Checklist rule 1 (linked entries move together) is satisfied by submitting the
six as one batch — the policy notes six related extensions is normal practice,
not "bulk."

### Wave 2 — new sequences: the hole family + two singletons (staged, READY*)

`submissions/oeis/` — see its README for per-item provenance.

| # | sequence | status |
|---|---|---|
| 0 | Hole triangle T(n,k) (`oeis/draft-hole-triangle.txt` + b-file) | submit FIRST in this wave: 1 and 2 cite its A-number |
| 1 | Hole-free count (column k=0), n=1..18 | READY — Superseeker-clear 2026-06-19 |
| 2 | One-hole count (column k=1), n=4..18 | READY — Superseeker-clear 2026-06-19 |
| 3 | Square-bounding-box count, n=1..16 | Superseeker pass still OWED (jasonp sends; lookup string in submissions README) |
| 4 | Max distinct holes, proven closed form, n=1..30 | READY — cross-refs corrected 2026-07-16 (see §5) |

*READY = data/provenance ready; the human steps of §3 still apply to every item.

### Wave 3 — new triangles (curated 2026-07-10: "2 strong + 1 optional, NOT a flood")

`results/oeis-candidates.md` is the source of truth for these.

- **A: height triangle T(n,H)** (row sums A006770, diagonal 3^(n-1)) — strongest
  new-sequence candidate; the diagonal closed forms live in its comments.
  Already staged as a skeleton: `oeis/draft-Tnh-triangle.txt` +
  `oeis/b-draft-Tnh-triangle.txt` (20 rows / 210 cells, verified 2026-07-17:
  row sums == A006770, T(n,n) == 3^(n-1), T(n,1) == 1).
- **B: component triangle C(n,c)** (row sums A006770, both edge columns A001168).
- **C (optional): HV-convex king animals** (38 terms, non-D-finite by area).

Novelty for A and B was model-checked only (2026-07-10); a **Superseeker pass is
still owed** before submission. Do NOT submit the T(n,n-k) anti-diagonals
separately (explicitly declined; they are derivable).

### Wave 4 — discuss-first / optional (do not submit without a separate decision)

- 8 free-polyplet symmetry-class drafts (`oeis/draft-sym-*.txt`) — plain-search
  novel only; Superseeker owed per class.
- GF orders + atom degrees (`oeis/draft-gf-orders.txt`, `draft-atom-degrees.txt`)
  — flagged NOT READY in `oeis/README.md` (report asserts non-membership;
  raise with editors first).
- Comment-grade edits to A187077 / A007052 / A225114
  (`oeis/draft-comments-subfamilies.txt`).

**Recommendation:** submit Wave 1 alone first and let it land; it builds the
contributor track record the later waves lean on. Waves 2–3 after, spaced.
Wave 4 only after editor rapport exists. Total scope and pacing are jasonp's
call.

---

## 2. The case to editors (facts to argue from — jasonp phrases them)

Everything below is checkable by an editor from the public artifacts; none of
it requires trusting prose.

1. **Digit-for-digit agreement of two algorithms that share no counting logic**
   through a(22): direct Redelmeier enumeration (three machines, three
   architectures, 24000 disjoint shards, ~120 h wall per box, completed
   Jul 16 2026; `results/redelmeier_row22/`) vs the transfer-matrix engine.
   The strongest kind of evidence a computational extension can offer.
2. **Every run re-derives all previous terms** as a by-product (the triangle
   recomputation), so each submission's b-file is internally re-verified, and
   a(1)–a(18) byte-match the live OEIS b-file.
3. **Held-out closed-form predictions**: P_15, pinned before a(33) existed,
   predicted T(33,18) exactly; P_16, fitted on a(33)–a(34), predicted the
   later holdouts T(35,19) and T(36,20) exactly. Terms whose newest cell lacks
   such a holdout are *explicitly downgraded* (a(36) is a comment, not b-file
   data).
4. **Honest grading is built into the entries themselves**: the %C text and
   b-file headers state exactly which terms are two-algorithm, which are
   single-algorithm-multiply-cross-checked, and which are conjectured. Nothing
   is presented above its evidence.
5. **Cross-ISA recounts** (ARM/clang vs x86/GCC byte-identical at a(34);
   split-architecture at a(36)) and **fault-injection-tested gates** (planted
   errors are caught; the checks fail on wrong programs).
6. **Everything regenerates**: engines, gates, per-term provenance ledgers, and
   a self-contained checker live in the repo; the full computational report
   (`paper/polyplets-report.tex`, "Fixed polyplets through a(36)") documents
   methods, validation architecture, and limits, including an explicit
   author's note on AI use (§"Author's note").

## 3. Human steps before ANY submission (mechanical checklist)

1. **Viva** passes jasonp's own bar (local process; docs/viva-state.md).
2. **Own-words pass**: jasonp rewrites every staged %C in his own words
   (AI-sounding prose is itself a live rejection trigger; Claude
   meaning-checks against the data only). The staged text is a FACT SOURCE,
   not submission copy.
3. **Signature dates**: every `_Jason H Parker_` date → the actual day of
   submission on oeis.org (Heinz precedent; README rule 2). Currently staged
   as Jul 16 2026 (A030234/A030235/A194596 entry files may still carry
   Jul 05/Jun 21 — bump at submission).
4. **DATA lines**: %S/%T/%U may be extended from the b-file at submission
   time (convention: fill ~3 lines); staged entries deliberately keep the
   live-OEIS DATA.
5. **Superseeker debts**: Wave 2 #3; Wave 3 A and B; Wave 4 sym classes.
   jasonp sends (body `lookup <terms>`, subject blank, 1/hour;
   [[oeis-superseeker-format]]).
6. **A-number resolution order**: hole triangle before its columns (Wave 2);
   fill every `Axxxxx?` placeholder consistently once real numbers are
   assigned.
7. **AI-disclosure answer ready**: one paragraph, jasonp's words, shaped like
   the paper's §"Author's note: use of AI" — exactly what AI did (algorithm
   design, implementation, drafting, run orchestration) and exactly what the
   author did (goals, design and verification decisions, machine ownership and
   operation, inspection, responsibility for correctness), plus the checkable
   verification protocol of §2. The A396719 precedent shows a precise answer
   defuses the probe; evasion sinks entries.
8. **Repo visibility**: %H links require the repo (github.com/jhparkerb/polyplets)
   or a compiled paper at a stable URL to be publicly reachable — jasonp
   decides what to publish and links accordingly. If neither is public at
   submission time, drop the %H links rather than link dead URLs.

## 4. Keyword judgment calls (flag, jasonp decides)

- Seqs 1–2 (Wave 2) carry `nonn,hard`; seq 3 carries `nonn,hard,more`. Adding
  `more` to 1–2 is defensible (18 exact terms, extendable with compute).
- A006770 already carries `nonn,hard,more` upstream — unchanged.

## 5. Audit trail (why to trust the staged data)

- **2026-07-16 pre-submission audit** (two independent read-only passes over
  all staged material):
  - All six Wave-1 b-files: zero disagreement with live OEIS values, contiguous,
    clean; Burnside/subtraction identities re-verified numerically at every
    shared n; A006770 b-file matches the banked triangle AND the independent
    Redelmeier combine on every shared index.
  - All four Wave-2 drafts: %S/%T/%U ≡ b-files term-for-term; offsets verified;
    backing data re-derived (hole-triangle columns; bbox diagonal + A006770
    marginal recomputed from `results/bbox_polyplets_n16_exact.txt`; max-holes
    formula re-checked for all 30 terms).
  - **One real error found and fixed** (`dbeef51`): seq 4 cited A337601 as
    "maximum holes of an n-omino" — it is actually a coprime-triples sequence;
    the prefix overlap is a numeric coincidence (a(n)=A337601(n-1) for
    n=1..12, diverging at a(13)). Corrected to A118797 (whose a(1)=7, the
    holey heptomino, was re-confirmed by brute force here) with the
    coincidence stated as such. The dangling "max-hole-AREA companion"
    reference was likewise resolved to A001971(n-2) (verified against
    exhaustive M(n) data, n ≤ 17).
- **2026-07-16 a(22) fleet confirmation**: `results/redelmeier_row22/PROVENANCE.md`.
- **2026-07-17 anti-confabulation sweep**: every real A-number cited in every
  staged draft was fetched from oeis.org and its definition checked against the
  claimed relationship — all 24 distinct A-numbers consistent (the sole failure,
  A337601, was the one already caught and fixed). All eight sym-class ↔
  polyomino-counterpart pairings correct; the 8-class sum == A030222 and the
  5-reflection-class sum == A030234 re-verified numerically for all 19 terms;
  A389193 is verified by the gate suite itself (gate H).
- **2026-07-17 green board**: full `make ns-gates` suite GREEN (incl. the
  newly-wired gate-g2); the paper's self-contained claim checker passes
  412/412; the paper compiles warning-free.
- Engine audits: `AUDIT-2026-06-28.md`, `AUDIT-2026-07-13.md` (all fixes
  red-first-tested; no banked value affected).
