# Ghost Ship — recorded divergences from cited prior work

Filed mid-run, before any grading. The preregistration stays sealed;
this file pins down where our protocol differs from the Li et al. flow
it descends from, with citations, so the writeup can't blur them.

## D1. Steering: Li et al. is responsive, ours is broadcast-only (filed 2026-08-15, after s01, outcome unknown; corrected same day after reading the paper)

Li et al. (arXiv:2608.11195, "Long-Horizon AI Research for
Grothendieck Constant") steer responsively and say so explicitly: §3,
"The human operators periodically reviewed the harness outputs by
reading and summarizing the session reports," issuing ~40 dated
directives; §4 credits the run's main theorem (K_G ≥ 6π/11) to one
such review-driven pivot. Their bulletin is also read by agents
periodically *during* work; ours is inlined at launch only, and our §4
abstention bars reading report content mid-run entirely.

The preregistration already disclaims replication — intro: "The
experiment no longer claims to test Li et al.'s condition"; §9 lists
the structural differences (theirs: two models, parallel sessions,
forty directives). So this is a recorded rescope, not a discovered
flaw: our run measures the fully-unattended end of the spectrum, with
the historical court flow as the responsively-steered arm. Q2 measures
launch-time broadcast pickup only and says nothing about Li-style
steering. A Li-style responsive arm on the same time-cut would be a
third condition, a separate run if this one's grading motivates it.

Other structural deltas from Li et al., for the writeup's comparison
table: single model, no reasoning-model/coding-agent split; 14 serial
sessions vs ~240 with up to 5 parallel; stdlib-Python desk compute vs
GPU + Arb certification; graded against a sealed historical baseline
vs an open-ended record.

## D2. Operator-paced launches ahead of cron (filed 2026-08-15, updated same day)

The preregistered 4/12/20 cadence existed to keep bulletin-edit
windows open; the operator concluded the bulletin has no legitimate
content-steering use (foreknowledge of the graded ladder) and directed
manual back-to-back launches instead. s01 launched 10:03 EDT with the
NOT_BEFORE gate suppressed (banked rc=0, 10:20); s02 launched ~11:08
(banked rc=0, 11:25); s03 was the noon cron slot; s04–s14 were manual
back-to-back launches, with NOT_BEFORE parked far-future during each
session so the 20:00/04:00 cron slots could not race a mid-flight run.
All 14 banked 2026-08-15 10:20–20:38 EDT — the preregistered 5-day
span compressed to one day. rc=0 throughout except s11 (rc=1: envelope
subtype=success/is_error=true — loop completed, final message was an
error; report present and hashed; stderr empty). HALT written by the
launcher's own completion rule ("run complete"). MANIFEST lines are
the receipts. Q2 reports NOT TESTED: the bulletin was never edited,
per the D1 reasoning.
