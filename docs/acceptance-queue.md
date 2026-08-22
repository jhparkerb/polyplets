# Acceptance queue — work that makes the basic results defensible

Written 2026-08-17. Scope set by jasonp: things *Claude* can execute, ranked by
how much they improve the chances that the results he can explain and defend —
a(21)..a(40), the T(n,H) triangle, the lambda bracket — survive scrutiny.
Esoteric or deep-math results are deliberately out of scope here even where they
are mathematically the more interesting open threads.

Status column is the state at the time of writing; update in place.
Last swept 2026-08-18 (item 2 closed by the ayr clean-clone run; items 3, 4
and 6 closed earlier the same day; item 1 rescoped).

## 1. Finish the Motley ladder — Confetti (H=18), then Ticker Tape (H=19)

STATUS: **DONE** (2026-08-19 08:58 EDT). **Confetti GREEN.**
`results/motley-h18.md`. Five sequential single-core passes, 399,700 s total
(4.63 days), peak RSS 65.9 GB, frontier 72,487,711 states; held-out prime
2147483563 predicted 40/40 residues from the CRT reconstruction; T(n,18)
matches the incumbent triangle at all 23 cells n = 18..40, 0 mismatch. The
assembly was re-derived here from the banked rows after the harvest, so the
23/0 is not the runner's word for it.

**a(n) is now closed rule-independently for all n <= 35.** Measured off
`scripts/provenance_table.py` at MOTLEY_H 17 against 18: the cells carrying
only the mod-4 congruence drop **11 -> 6**
<!--q:congruence_only.count@17=11--><!--q:congruence_only.count@18=6-->, retiring
(36,18), (37,18), (38,18), (39,18) and (40,18)
<!--q:retires.cells@18=(36,18),(37,18),(38,18),(39,18),(40,18)-->. What is left
is (38,19), (39,19), (39,20), (40,19), (40,20), (40,21)
<!--q:congruence_only.cells@18=(38,19),(39,19),(39,20),(40,19),(40,20),(40,21)-->.
The pinned count in the gate moved from 11 to 6 deliberately, which is what it
was pinned for. Both figures are generated in `results/residual-cells.md`.

**Superseded 2026-08-22 by the Nmax-41 ladder.** The figures above are
Confetti's and remain true of H <= 18. The Nmax-41 ladder (2026-08-21,
`results/cutcount_b1/rows41/`) reached H <= 19, and the congruence-only set is
now three cells <!--q:congruence_only.count@19=3--> rather than six —
`results/provenance-table.md` is regenerated and
`scripts/provenance_table.py` derives Motley's reach from the banked row sets
instead of carrying it as a constant.

**Ticker Tape is priced and not recommended** --- `results/ticker-tape-assessment.md`,
2026-08-18: on Confetti's measured constants H=19 needs ~197 GB against dalby's
125 and ~26 days of wall, and it buys no statement the project can otherwise
not make. So the ladder stops at H=18 unless the arena is redesigned first, and
n <= 35 is where this ends.

The only item that moves the defensibility of the headline numbers. It moved:
a(n) is closed rule-independently for n <= 35, and the three cells of row 40 at
H = 19, 20 and 21 are what still carry nothing but the congruence
<!--q:row40_congruence_only.cells@18=T(40,19)..T(40,21)-->.

- Confetti GREEN -> n <= 35 rule-independent. **Done.**
- Ticker Tape (H=19) -> n <= 37 --- priced, not recommended, see above. It is
  the rung that would take (38,19), (39,19) and (40,19)
  <!--q:retires.cells@19=(38,19),(39,19),(40,19)-->, which is three of the six
  remaining congruence-only cells <!--q:retires.count@19=3-->. It leaves
  (39,20), (40,20) and (40,21)
  <!--q:congruence_only.cells@19=(39,20),(40,20),(40,21)-->.
- The "9 -> 7 -> 5 cells" band this entry used to quote is **correct**, and the
  note that said it does not reproduce was the error. It is a different
  quantity: row 40's rule-independence band, computed off
  `docs/b1-closure-plan.md` section 1's anchor rule rather than off the
  provenance table. Both are now generated and checked in
  `results/residual-cells.md`, which names them Q1 and Q2 so the next reader
  does not have to work out that there were two.

Every referee objection that will actually be raised about a(34)..a(40) is "one
engine, one connectivity rule". This is the answer to it.

First action: read the Confetti heartbeat and quote the real `eta=`; do not
restart a healthy run.

## 2. Fresh-clone reproducibility, end to end, on a clean box

STATUS: **DONE** (2026-08-18, ayr). `scripts/clean_clone_check.sh` clones from a
bundle, runs every phase a reader would run, and records an exit code per phase
instead of stopping at the first failure. Final run, rev `0171909`, all green:

| phase | wall |
|---|---|
| `make` (the gate suite; there is no separate build step) | 404 s |
| `make ns-gates` | 769 s |
| `ALLOW_PARTIAL=1 python3 paper/verify_claims.py` (425 of 428) | 902 s |
| `python3 paper/verify_l_papers.py` (336 checks, 23 RED) | <1 s |
| `python3 paper/verify_technical_report.py` (781 checks) | <1 s |
| `make -C paper` (11 PDFs) | 13 s |
| `scripts/dalby_term.sh 26` --- **a(26) = 102607513847014153892** | 23 s |

Four things were broken and are fixed. The citations gate was scoping its
history class to `git log --all`, so it passed on gympie's 50 local refs and
went RED with 65 dangling citations in a clone of master --- every one of them
on `triangle-structure` or `half-measure`, campaign branches that are not on
origin. Four translation units did not compile under GCC (`strip_mu_kink`'s
compound literal broke the build outright; the rest were `-Werror` warnings
clang does not raise). `scripts/dalby_term.sh` began with `cd
~/src/polyominoes`. And `make -C paper` died on a TeX Live without `lmodern`,
because microtype cannot expand the bitmap font METAFONT hands back for a TS1
glyph.

Two things a reader should know rather than have fixed: `verify_claims.py`
exits 1 on a clone without `ALLOW_PARTIAL=1`, because three of its checks read
`runs/sym32` and that is run output; and the 65 branch citations are still
citations into branches origin does not carry. **Whether those two branches get
published is his call** --- the gate no longer passes on evidence the reader
does not have either way.

## 3. One provenance table, per-cell, replacing the scattered accounting

STATUS: **DONE** (`b705687`). `results/provenance-table.md`, generated by
`scripts/provenance_table.py`, gated by `make gate-provenance` --- the gate
regenerates the table and fails if any coverage figure drifts from the note that
publishes it.

"What is confirmed, by which independent source, covering what share" is spread
across `results/ns_a40/PROVENANCE.md`, `results/strip-engine.md`,
`results/subgroup-mod4.md`, `results/motley-h17.md` and HANDOFF.md. That spread
is not auditable by a referee or by us — the strip-coverage vs holdout
confusion already bit once. Generate one table; gate it against the banked rows
so it cannot drift.

## 4. Mechanically verify the OEIS / b-file artifacts from banked data

STATUS: **DONE** (`47dbd97`). `scripts/bfile_gate.py`, wired as
`make gate-bfiles`: every uploaded term is re-derived from banked data,
fail-closed.

The submission artifacts are what get scrutinized, and they are currently
produced by scripts whose output is not gate-checked against the primary rows.
Fail-closed check, cheap to write. A wrong digit in a b-file is the most
embarrassing failure mode available to this project.

## 5. The lambda bracket's two ends

STATUS: **DONE** (2026-08-19). Both halves.

The clean-box half: `scripts/lambda_cert_reproduce.sh` rebuilt `strip_mu_cert`
from a fresh clone on ayr and re-derived the H<=11 ladder and H=17, diffing
every rational against the primary log --- fail-closed, a banked row it cannot
find counts as a failure. **VERDICT: REPRODUCED**, eleven for eleven, `mu_17 >=
6543/1000 PASS` among them. Receipts: `results/strip_mu_certificates_ayr.log`.
That number had existed exactly once before, from one machine, from a binary
built on that machine. `attempts`, `states` and `min_ratio` agree exactly and
`mu_float` agrees to all ten printed digits, so the two runs land on the same
value rather than a nearby one. H=17 cost 4559 s against gympie's 772.7 s,
which is the machines.

The paper half was already clean
--- `paper/L3-lambda-bounds.tex` states the bound as 9.3154 (ten occurrences).
Its only mentions of 9.3153 are a footnote that exists to forbid it (the
certificate proves 20000/2147 = 9.31532..., so truncating would claim
3.2e-5 more than it gives) and the exact expansion 1/x = 9.31532... inside the
proof. Neither is a rounded claim.

6.543 <= lambda <= 9.3154, both ends machine-checkable in exact arithmetic, and
explainable in two sentences. Confirm both certificates regenerate from scratch
on a clean box (rides on item 2), and that the paper quotes **9.3154** — not a
rounded 9.3153.

## 6. Narrow adversarial re-read of the paper's load-bearing claims

STATUS: **DONE, and it is his to act on** (`caffcc1`).
`docs/main-paper-audit-2026-08-18.md`: verifier clean, one loose lambda claim,
and the provenance sentence gives away four terms. Nothing in
`paper/technical-report.tex` was changed.

Not a new campaign. `verify_technical_report.py` covers 781 checks; the gap is
numeric claims in prose that the verifier does not parse. Check each against
banked data, list the failures, change nothing in
`paper/technical-report.tex` without explicit direction.

## Below the line, by jasonp's criterion

Open and interesting, but they do not make a(40) believable: Exact Change (H=13
basis test), the Ridgeline depth-amplitude family, the onset-defect constants,
Lean formalization of the cutcount identity.

## Blocked on jasonp

- Item 1's remaining decision is whether the ladder stops at H=18. The compute
  question is answered; the call is not ours.
- Item 6's findings are listed and unapplied by design --- the report is his
  prose.
