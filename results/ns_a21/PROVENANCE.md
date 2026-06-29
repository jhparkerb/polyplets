# a(21) — number of fixed polyplets (king-move animals) of 21 cells

## a(21) = 6,954,084,405,510,437

New frontier term (A006770). Computed 2026-06-29.

## Run

- **Host:** dalby, `~/src/polyominoes-ns` worktree, orchestrate PID 993738.
- **Binary rev:** `35eb9e1` — **UNFIXED**: it brute-force-enumerated the H=21 top
  strip (the closed form `T(21,21)=3^20=3,486,784,401`) instead of injecting it,
  costing the long single-core straggler tail on H21 col2 (the A1 incident — the
  value is nonetheless correct). Fixed in the post-run audit (A1 `2d782e2`,
  work-stealing `b8b448b`); a re-run on a current binary would be far cheaper.
- **Wall:** ~129,023 s (~35.8 h). Completed `2026-06-29T07:29:44-04:00`, clean
  exit (status 0). Full log: `a21.log` on dalby.

## Validation

- **a(1)–a(19) match the A006770 b-file exactly** (0 mismatches): a(1)–a(18) are
  the OEIS-published terms; a(19) is the project's two-algorithm-confirmed term.
- **a(20) = 1,025,573,519,362,016** matches the prior validated a(20) run (new
  engine == old engine, byte-identical).
- **Growth a(21)/a(20) = 6.78068** — inside the [3.9, 7.2] band, on the forecast.
- **Per-height h1–h17 are BYTE-IDENTICAL between dalby and ayr** (independent
  machines, independent runs; sha256 match on all 17). ayr's salvage
  (`runs/a21fold`) reached h17 (h18 partial).
- h21 top value = `3^20 = 3,486,784,401` (closed form), consistent.

## Open: the novel term is not yet independently certified

The new content of a(21) lives in the high heights **h18–h21, which are
single-source (dalby only)** — ayr's independent salvage stops at h17. A
shared-enumeration bug affecting only the high heights would not be caught by the
checks above. Closing that needs the mod-p shadow (audit A6, deferred) or a full
independent reimplementation. Per "validate at scale before record," treat
a(21) as our computed value **pending independent certification of h18–h21** —
not yet OEIS-submission-final.

## Artifacts (this dir)

- `triangle.txt` — a(n) for n=1..21.
- `perheight/h{1..21}.out` — the `T(n,H)` rows per height H.
