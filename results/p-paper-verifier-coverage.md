# What the report's verifier actually reads

Called the P-paper coverage measurement for historical reasons: it was built
when `paper/technical-report.tex` was a P paper, jasonp's own prose, and it is
one again as of 2026-09-25.

Measured, not assumed. `tests/p_paper_coverage_audit.py` (deleted 2026-10-13; the
gate `tests/gate_p_paper_verifier.py` now runs the same full sweep on every push) perturbs the last
digit of every numeric literal of four or more digits in a COPY of the `.tex`
and re-runs the verifier: a literal whose perturbation still passes is one the
paper prints and no check reads. `tests/gate_p_paper_verifier.py` is the gate
that keeps the answer from drifting. jasonp's prose is never written to.

## The answer, re-measured 2026-09-25

| paper | verifier | literals | guarded | unguarded |
|---|---|---|---|---|
| `paper/technical-report.tex` | `paper/verify_technical_report.py` (2840 checks) | 294 | **293** | 1 |

The one exception is the year in the report's `\date{}`. It is named in the
gate's `ALLOWED` with that reason, and any new unguarded literal fails the
gate, so coverage cannot silently drop.

From 2026-09-06 to 2026-09-25 the file held the machine-written report, which
measured 229 of 235 with six named exceptions; the figure above is for his
restored text.

## Why this measurement exists

Until 2026-08-23 the same audit covered a second manuscript,
`paper/polyplets-report.tex`, whose verifier `paper/verify_claims.py` read 154
of its 264 literals: a whole printed triangle, the a(40) lower bound, the four
companion values at n = 33 and the λ certificate's numerator were all printed
by the paper and read by nothing. Transcription was the gap — every number was
correct when written, and nothing would have caught it going stale. That
manuscript and its verifier were deleted in wave 3 of the 2026-09
consolidation (`docs/consolidation-plan.md`), superseded by the technical
report, which is why the surviving row reads 293 of 294 rather than 154 of 264:
the report's verifier reads its tables out of the `.tex` and compares them to
the banked sources, which is the shape that closes the gap.

The L-paper side of the same measurement is
`results/l-paper-verifier-coverage.md`, and it is the one that still shows
exposure: 74 of 531.

## Reproduce

    make gate-p-paper-verifier                  # the gate, with its own RED control (the audit script is deleted)
