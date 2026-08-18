# Acceptance queue — work that makes the basic results defensible

Written 2026-08-17. Scope set by jasonp: things *Claude* can execute, ranked by
how much they improve the chances that the results he can explain and defend —
a(21)..a(40), the T(n,H) triangle, the lambda bracket — survive scrutiny.
Esoteric or deep-math results are deliberately out of scope here even where they
are mathematically the more interesting open threads.

Status column is the state at the time of writing; update in place.

## 1. Finish the Motley ladder — Confetti (H=18), then Ticker Tape (H=19)

STATUS: Confetti launched 2026-08-14 on dalby, tmux `motley-h18`, driver PID in
`~/var/motley-h18/driver.pid`. State unverified from gympie (no ssh agent).

The only item that moves the defensibility of the headline numbers. Today's
honest statement: a(n) is closed rule-independently for n <= 33 (Motley H=17,
`results/motley-h17.md`), and a(40)'s H15-19 band — 43.8% of the term — has no
independent second source beyond the mod-2 / mod-4 congruences.

- Confetti GREEN -> n <= 35 rule-independent.
- Ticker Tape (H=19) -> n <= 37.
- Row 40's residual band: 9 -> 7 -> 5 -> 3 cells across the ladder.

Every referee objection that will actually be raised about a(34)..a(40) is "one
engine, one connectivity rule". This is the answer to it.

First action: read the Confetti heartbeat and quote the real `eta=`; do not
restart a healthy run.

## 2. Fresh-clone reproducibility, end to end, on a clean box

STATUS: known broken — a fresh worktree fails two gates (`build/ns/*_worker` not
built by bare `make`; `papers/` PDFs are gitignored, so citation checks want
files that a clone does not have).

A referee's first act is `git clone && make`. Failing that on a project whose
whole credibility rests on its gate battery is the worst available first
impression. Do a genuine clean-clone run on ayr or dalby, fix what breaks, and
add one documented command that reproduces a real value (a(26) is the right
size) from nothing but the clone.

## 3. One provenance table, per-cell, replacing the scattered accounting

"What is confirmed, by which independent source, covering what share" is spread
across `results/ns_a40/PROVENANCE.md`, `results/strip-engine.md`,
`results/subgroup-mod4.md`, `results/motley-h17.md` and HANDOFF.md. That spread
is not auditable by a referee or by us — the strip-coverage vs holdout
confusion already bit once. Generate one table; gate it against the banked rows
so it cannot drift.

## 4. Mechanically verify the OEIS / b-file artifacts from banked data

The submission artifacts are what get scrutinized, and they are currently
produced by scripts whose output is not gate-checked against the primary rows.
Fail-closed check, cheap to write. A wrong digit in a b-file is the most
embarrassing failure mode available to this project.

## 5. The lambda bracket's two ends

6.543 <= lambda <= 9.3154, both ends machine-checkable in exact arithmetic, and
explainable in two sentences. Confirm both certificates regenerate from scratch
on a clean box (rides on item 2), and that the paper quotes **9.3154** — not a
rounded 9.3153.

## 6. Narrow adversarial re-read of the paper's load-bearing claims

Not a new campaign. `verify_technical_report.py` covers 781 checks; the gap is
numeric claims in prose that the verifier does not parse. Check each against
banked data, list the failures, change nothing in
`paper/technical-report.tex` without explicit direction.

## Below the line, by jasonp's criterion

Open and interesting, but they do not make a(40) believable: Exact Change (H=13
basis test), the Ridgeline depth-amplitude family, the onset-defect constants,
Lean formalization of the cutcount identity.

## Blocked on jasonp

- Item 1 needs a working ssh path to dalby from gympie (ssh-agent session pending).
