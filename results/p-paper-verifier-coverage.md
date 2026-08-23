# What the two P-paper verifiers actually read

2026-08-23. `tests/gate_p_paper_verifier.py` (gate) and
`tests/p_paper_coverage_audit.py` (audit). Method: perturb the last digit of
every numeric literal of four or more digits, in a COPY of the `.tex`, and
re-run the verifier. A literal whose perturbation still passes is one the paper
prints and no check reads. jasonp's prose is never written.

## The answer

| paper | verifier | checks | literals | guarded | unguarded |
|---|---|---|---|---|---|
| `technical-report.tex` | `verify_technical_report.py` | 781 | 200 | **199** | 1 |
| `polyplets-report.tex` | `verify_claims.py` | 428 | 264 | 154 | **110** |

The technical report's one exception is the year in `\date{July 18, 2026}`.
It is named in the gate's `ALLOWED` with that reason, and any new unguarded
literal fails the gate, so the coverage cannot silently drop.

Of polyplets-report's 110, **27 live only inside `thebibliography`** — years and
arXiv identifiers, which assert nothing. **83 are in the body.**

## The 83, by what they are

- **A whole printed triangle**, rows 5..18, every `\num{}` entry in it. The
  verifier checks the banked data this table was transcribed from; it does not
  check the transcription.
- **`a(40) >= 4266005101622209395058618248135`** — the paper's own headline
  lower bound.
- **The four companion values at n = 33**: `A030222`, `A030234`, `A030235`,
  `A194596`.
- **The lambda certificate `x = 2147/20000`**, and the `5930`-type system it
  names.
- **The denominator degrees** `1,2,4,9,29,68,181,462,1254,3289` and the
  denominator orders ending `1897, 5005`.

## Checked without the optimisation in the loop

The audit runs `verify_claims.py` under `tests/_audit_subprocess_cache.py`,
which memoises the nine `subprocess.run` calls that are 429 of its 431 s and
read no `.tex`. That is what makes the sweep ten minutes instead of 32
core-hours, and it is also exactly the thing that could manufacture this
result. So three of the alarming literals and one control were re-run with the
cache OFF, in parallel, against the real verifier:

| literal | what | uncached result |
|---|---|---|
| `4266005101622209395058618248135` | the a(40) bound | PASS — unguarded |
| `16503616943998` | triangle row 18 | PASS — unguarded |
| `2147` | certificate numerator | PASS — unguarded |
| `28988633422018953978570` | a literal the sweep calls guarded | FAIL — guarded |

The control is the half that matters: the harness does detect a guarded
literal through the same path.

## What this is not

Not a claim that any of the 83 is **wrong**. Every one of them was correct when
it was transcribed, `verify_claims.py`'s 428 checks are all green, and the
banked data behind the table is checked. What is missing is the link between
the banked data and what the paper prints: a typo in the transcription, or a
table that goes stale when the data is regenerated, is invisible to the
verifier today. That is the same failure `verify_technical_report.py` closes for
the other paper, at 199 of 200.

## What would close it

Extend `verify_claims.py` to read the printed table and the five singletons
above out of the `.tex` and compare them to the banked sources it already
loads — the same shape `verify_technical_report.py` already uses, which is why
its number is 199. Then the audit's unguarded set drops to the bibliography,
and the sweep becomes gateable at 2.2 s a run under the cache.
