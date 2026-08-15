# The minimal state system — BANKED 2026-08-14, not yet adopted

Distilled from the Offside panel (`results/offside/`, lanes A–F) after
jasonp's simplification call. Five mechanisms; everything else is a cut
with a named reopen condition.

1. **Memory carries pointers, never status; every path must resolve.**
   Closes all five errors lane D measured; one evening; reuses
   `scripts/check_receipts.sh`.
2. **One append-only card per thread** (`state/<thread>.md`). A block is
   four lines — date+status, claim, receipt path, caveat (or `none`).
   Statuses: OPEN / CLOSED+ / CLOSED−. New facts are new blocks;
   contradicting an old block means saying so in the new one.
3. **`STATE.md` is rendered, one screen, transclusion only** — latest
   block per live thread, verbatim. HANDOFF.md becomes the append-only
   chronicle, no status language.
4. **One gate**: paths resolve, vocabulary exact, generated file
   hash-checked. Reuses `check_receipts.sh`; red-first fixtures.
5. **Papers spawn red-first** — a notable result owes a paragraph and a
   named check in the draft's verifier, same act (existing practice,
   written down).

Cut, with reopen conditions:

- `tier`/arity — reopen: a two-source claim gets misquoted as proved.
- `depends:`/git-freshness — reopen: a repaired proof's dependents go
  unnoticed again (it caught one real case; true-positive rate
  unmeasured).
- `kill:`/`goal:` — reopen: another ill-posed goal survives a round.
- Door fields beyond the caveat line — reopen: a closed door gets
  re-derived.
- TTLs, Converts-to — dead (prohibition inversion; unfillable at close).
  Do not reopen.
- Citation-asymmetry sweep — build separately if its false-positive rate
  measures low; it is a script, not schema. (It found three real stale
  items on first manual run: the a(40) provenance row, triangle-snf's
  ladder bullet, onset-defect-law's "nothing available" — all repaired
  2026-08-14.)

Candidate heuristic 12, from lane E, awaiting the heuristics file:
**a test that a known positive also fails cannot close a thread** —
discovered independently twice (band-structure mod-m; strip-spectrum
float roots), uncited both ways, ~7 scattered instances.
