# OEIS submission — authoritative index and case file

2026-07-16. **This file decides scope and order.** The three older lists
(`oeis/wave2/README.md`, `oeis/README.md`, `results/oeis-candidates.md`)
keep their per-item detail but their status sections defer here.

**Nothing is submitted by Claude, ever.** jasonp pushes every button, after
the human steps in the checklist below.

---

## 1. What we have (inventory, by wave)

### Wave 1 — extensions to six existing entries (submit first)

The least arguable, highest-value batch: new terms for 30-year-old `hard`
sequences, nothing about novelty to defend.

| entry | staged | b-file | new terms | anchor |
|---|---|---|---|---|
| A006770 (fixed polyplets) | `oeis/A006770.txt` | `results/b006770_upload.txt` | a(19)–a(40) | a(1)–a(22) two-algorithm |
| A030233 (one-sided) | `oeis/A030233.txt` | `results/b030233_upload.txt` | a(18)–a(34) | Burnside from A006770 + r90/r180 |
| A030222 (free) | `oeis/A030222.txt` | `results/b030222_upload.txt` | a(18)–a(32), +a(33) %C conjecture | Burnside (needs dmirror) |
| A030234 (bilateral) | `oeis/A030234.txt` | `results/b030234_upload.txt` | a(18)–a(32), +a(33) %C | (E+G)/2 identity |
| A030235 (asymmetric) | `oeis/A030235.txt` | `results/b030235_upload.txt` | a(18)–a(32), +a(33) %C | A030222 − A030234 |
| A194596 (free non-poly) | `oeis/A194596.txt` | `results/b194596_upload.txt` | a(18)–a(32) | A030222 − A000105 |

All six b-files audited 2026-07-16: zero disagreement with live OEIS terms on
every shared index, contiguous, format-clean, cross-entry Burnside identities
verified numerically at every shared n (see §5).

**2026-07-29 — A006770 promoted to a(40).** The a(37)–a(40) ladder (final
term a(40), project close) retired the a(36) downgrade: P_16/P_17/P_18 each
passed real-swept holdouts (T(35,19), T(37,20), T(39,21)), and the a(40)
run's real H21 sweep re-confirmed P_0..P_18 on every row n = 21..39 at once
(`results/ns_a40/PROVENANCE.md`; T(40,20) re-swept standalone,
byte-identical). a(36)–a(40) added to the b-file, the a(36)-conjecture %C
dropped, %E/header updated. These five terms postdate the 2026-07-16 audit:
**re-run the §5 mechanical audit on A006770 before submission** (n ≤ 18
byte-match vs live OEIS re-verified 2026-07-29 by
`paper/verify_technical_report.py`; the other five entries are untouched).

**2026-09-06 — the A006770 re-audit of the note above is done, and the staged
text is rewritten.** The staged b-file was diffed against the live one
(`oeis.org/A006770/b006770.txt`, still auto-synthesized from an 18-term DATA):
18 shared indices, zero disagreements. The two comments dated Jul 16 2026 were
stale in a way that *understated* the evidence -- they called a(23)-a(40)
single-algorithm results, which stopped being true when the coloring transfer
matrix landed on 2026-08-21. They now say what is true: every entry for
23 <= n <= 39 is either recounted by that program or given by a closed form
pinned on its entries, a(40) has 19 of its 40 heights recounted, and three
entries of the whole table have one enumeration behind them. Every signature
date is now the token `~~~~`, which the OEIS edit form expands to the
contributor's name and the day of submission, so a staged date can no longer go
stale. A `%H` link to the now-public repository was added.

Checklist rule 1 (linked entries move together) is satisfied by submitting the
six as one batch. The OEIS AI guideline forbids bulk or serial submission of
machine-generated *sequences* without prior permission and says nothing about
extensions (§6).

### Wave 2 — new sequences: the hole family + two singletons (staged, READY*)

`oeis/wave2/` — see its README for per-item provenance.

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
  Already staged: `oeis/draft-Tnh-triangle.txt` +
  `oeis/b-draft-Tnh-triangle.txt` (40 rows / 820 cells — extended 2026-07-29
  from the banked a(40) triangle, 210-cell prefix byte-identical; verified:
  row sums == A006770 for n <= 40, T(n,n) == 3^(n-1), T(n,1) == 1; diagonal
  closed-form %C/%F added).
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
2. **Every run recomputes the enumerated heights of all previous terms** as a
   by-product (the tall heights come from the closed forms, not from
   enumeration; `results/confidence.md`), and
   a(1)–a(18) match the values OEIS serves today, line for line (checked
   live 2026-07-30: A006770 has no author-uploaded b-file, so
   oeis.org/A006770/b006770.txt is auto-synthesized from the entry's DATA
   field — the comparison is against DATA, which is what our submission
   would extend).
3. **Held-out closed-form predictions**: P_15, pinned before a(33) existed,
   predicted T(33,18) exactly; P_16, fitted on a(33)–a(34), predicted the
   later real-swept holdout T(35,19); P_17 predicted the real-swept
   T(37,20); and the a(40) run's first-ever real H21 sweep reproduced the
   closed-form column-21 values on every row n = 21..39 at once — P_18's
   first holdout, T(39,21), among them.
   No term in the b-file rests on a formula without a passed holdout (P_19
   exists but is fitted-only and is used for NO banked term).
4. **Honest grading is built into the entries themselves**: the %C text and
   b-file headers state exactly which terms are two-algorithm, which are
   single-algorithm-multiply-cross-checked, and which are conjectured. Nothing
   is presented above its evidence.
5. **Cross-ISA recounts** (ARM/clang vs x86/GCC byte-identical at a(34);
   split-architecture at a(36)) and **fault-injection-tested gates** (planted
   errors are caught; the checks fail on wrong programs).
6. **Everything regenerates**: engines, checks, per-term provenance records
   and a self-contained checker live in the repo, and the technical report
   (`paper/technical-report.tex`) documents methods and limits.

## 3. Human steps before ANY submission (mechanical checklist)

1. **Own-words pass**: jasonp rewrites every staged %C in his own words.
   The staged text is a fact source, not submission copy.
2. **Signature dates**: every `_Jason H Parker_` date → the actual day of
   submission on oeis.org (Heinz precedent; README rule 2). Currently staged
   as Jul 16 2026 (A030234/A030235/A194596 entry files may still carry
   Jul 05/Jun 21 — bump at submission).
3. **DATA lines**: %S/%T/%U may be extended from the b-file at submission
   time (convention: fill ~3 lines); staged entries deliberately keep the
   live-OEIS DATA.
4. **Superseeker debts**: Wave 2 #3; Wave 3 A and B; Wave 4 sym classes.
   jasonp sends (body `lookup <terms>`, subject blank, one per hour).
5. **A-number resolution order**: hole triangle before its columns (Wave 2);
   fill every `Axxxxx?` placeholder consistently once real numbers are
   assigned.
6. **AI-disclosure answer ready**: one paragraph, jasonp's words: what the
   machine did (algorithm design, implementation, drafting, run orchestration)
   and what the author did (goals, design and verification decisions,
   machine ownership and operation, inspection, responsibility for
   correctness), plus the checkable verification protocol of §2. Editors do
   ask ("Did you use AI to generate this sequence?", the first A396719, Jun
   2026); the guideline and what editors did under it are in §6.
7. **Repo visibility**: %H links require the repo (github.com/jhparkerb/polyplets)
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

## 6. AI use: the guideline and what editors did (checked 2026-10-23)

**The guideline** is the OEIS wiki page "Use of AI for OEIS Submissions" (the
old title "...is Forbidden" redirects to it; latest approved revision 29 Aug
2026; its earlier history needs a wiki login). A human author is responsible
for anything an AI produced, and must verify the name, the terms, that
formulas are provably correct, that programs are correct and produce the
terms, and that comments are accurate and comprehensible. Forbidden: AI text
in the pink boxes; an AI as author or co-author; AI-generated full text of
comments; an AI-generated program whose working and limits the submitter does
not understand; bulk or serial submission of machine-generated sequences
without permission. It quotes Tao: authors who cannot give a clear,
expert-level talk on the result should not publish it.

**Rejections.** A rejected entry's A-number is recycled, so these numbers now
show unrelated approved sequences; the record is in the history pages
(`oeis.org/history?seq=A396919&start=20`, and likewise for the others).
- A396919 (Noor Alenizy, Jul 2026): pink-box replies carried hidden zero-width
  characters; "Rejected, NFO, violation of AI-policies" (Irvine, Jul 3);
  Arndt proposed blocking the account.
- A396748 (Tomáš Kling, Jun 2026): data wrong, and "AI is not allowed in pink
  boxes" (Branicky); recycled Jun 17.
- A396719 (Chen Wei-Shi, Jun 2026): asked whether AI generated it, answered
  no; rejected Jun 9 for another reason (it repackaged columns already in
  the OEIS).

**Accepted extensions whose code an AI wrote**, each with a GitHub repo linked
from the entry:

| entry | contributor, repo | added | editors' questions |
|---|---|---|---|
| A142886 | Michael Spiegel, `mspiegel/A142886` (62 of 65 commits Claude) | b-file 0..163 to 0..203, Jun 2026 | credit for the existing terms in the b-file link, "(terms 0..163 from Robert A. Russell)", per oeis.org/SubmitB.html |
| A104430 | Jeremia Passmore, `Horizon-Hawk/oeis-A104430` (all commits Claude) | a(20), proposed Oct 18, approved Oct 19 2026 | none |
| A109455 | James Guillochon, `guillochon/oeis-results` | corrected a(6), Sep 26 to Oct 10 2026 | whether the published source (Knuth) has the wrong value, so it can be noted |
| A181671 | Gaurav Vyas, `realgauravvyas/ramanujan-primes-beyond-1e19` | a(18)-a(23), Aug 2026 | |
| A347537 and about 30 others | Jacob Glickman, `jhg023/first-knowns` (all code Claude) | Aug-Oct 2026 | |
| A096772 | Adam Reichert (C++ by Claude Code; program uploaded to the OEIS) | b-file to 825, Apr 2026 | |

How much AI use the repo disclosed ranged from nothing (A104430) to a
statement at the top of the README (first-knowns), and none of these
histories has an editor comment about AI. The single-sequence repos have 16
to 42 files. Passmore's whole pink-box note was three sentences: the new
term, the two independent implementations that agree and both reproduce
a(0)-a(19), and that code and logs are at the link.

Not yet in the OEIS, with no pending draft: `Jourdelune/langford31` (L(2,31)
for A014552, entirely Claude), `kanestar2/oeis-a072503`,
`PowyBot/oeis-a400741`.
