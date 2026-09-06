# What the P-paper verifier actually reads

Measured, not assumed. `tests/p_paper_coverage_audit.py` perturbs the last
digit of every numeric literal of four or more digits in a COPY of the `.tex`
and re-runs the verifier: a literal whose perturbation still passes is one the
paper prints and no check reads. `tests/gate_p_paper_verifier.py` is the gate
that keeps the answer from drifting. jasonp's prose is never written to.

## The answer, re-measured 2026-09-06

| paper | verifier | literals | guarded | unguarded |
|---|---|---|---|---|
| `paper/technical-report.tex` | `paper/verify_technical_report.py` (3406 checks) | 235 | **229** | 6 |

The six exceptions are named in the gate's `ALLOWED`, each with its reason:
the year in the report's `\date{}`, the month and day of the release-approval
date in its disclosure block, the two rotation subscripts of the Burnside
setup, and A000105, an OEIS entry this project does not compute and subtracts
only to define A194596. Any new unguarded literal fails the gate, so coverage
cannot silently drop.

The count changed on 2026-09-06, when the machine-written report replaced the
partial one and became `technical-report.tex`: a different file, with different
literals, audited the same way. The measurement before the swap was 293 of 294
on the file it replaced.

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

    python3 tests/p_paper_coverage_audit.py     # about 3 minutes
    make gate-p-paper-verifier                  # the gate, with its own RED control
