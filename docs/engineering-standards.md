# Engineering standards — catching regressions fast

Adopted 2026-06-29 after the regression sweep in [AUDIT-2026-06-28.md](../AUDIT-2026-06-28.md),
where a working fix sat uncommitted while the deployed engine brute-forced a
closed form for ~16h, and a batch of silent-wrong-answer bugs reached HEAD
because nothing red-flagged them. These are the small, standing practices that
turn those classes into immediate, loud failures. Keep them few; keep them
enforced.

## 1. Gates run automatically, not by memory

A gate that isn't run rots. Existing gates had drifted out of the aggregate
(`ns-gates`) and out of habit.

- **Pre-push hook.** `make install-hooks` points `core.hooksPath` at
  `.githooks/`; the `pre-push` hook runs `make ns-gate-fast` (<~16s: the full Go
  suite + the sub-second C++ format/arith gates). Run once per clone. Emergency
  bypass is `git push --no-verify` — then fix what you skipped.
- **Full suite before a release / record run.** `make ns-gates` adds the heavy
  C++ sweeps (spill, parallel, holes, maxn=14 regression).
- No GitHub Actions by choice — the hook is the enforcement point.

## 2. Encode known truths as cheap invariant gates

The original incident wasn't subtle: the engine enumerated a *known closed
form*. Anything we can state as an invariant is a free, fast tripwire.

- `make ns-gate-closedform` asserts every known closed form is contributed
  directly, never enumerated (top strip `T(N,N)=3^(N-1)`; low strips `T(n,1)=1`,
  the `T(n,2)` recurrence). **Add a case here the moment a new closed form or
  conservation law is established** — before it can be silently recomputed.
- The same spirit applies to any new invariant (partition-independence, fold ==
  unfold, growth-ratio bounds): a five-line assertion is cheaper than a wrong
  number.

## 3. Two standing code rules

- **Fail closed.** A new flag, guard, or parser defaults to *refuse*, never
  fail-open. Almost every CRITICAL in the audit was silent because the failure
  mode was "continue with a wrong number" instead of "stop at the start"
  (counter overflow, missing shard, unreadable input, resume config mismatch,
  unknown counter tag). When in doubt, refuse and make the caller opt in.
- **Red-first.** A bug fix is not done until a test that was **RED on the old
  code** is GREEN on the new — and the captured red goes in the commit message.
  Ship the tripwire *with* the fix; a fix without a regression test is how the
  same bug comes back. (The audit campaign retrofitted this 20×; do it up front.)

## 3b. Never weigh a cell by its size

**A term is wrong if any one of its cells is wrong.** So "T(40,19) is 5.7% of
a(40)", "43.84% of a(40) has no second source", "97% rule-independent" and every
other share-of-a(n) figure is banned: it is a number with no decision attached
to it, and it invites the reading it cannot support — that a term is partly
trustworthy in proportion to the cells that were checked.

State cells. "Eleven cells of the triangle have one source, and here they are"
is the same fact without the false arithmetic. `results/provenance-table.md` is
the form to copy, and `make gate-provenance` pins the count.

Standing ruling, restated 2026-08-18 after this framing reappeared in a day's
worth of new notes. It applies to papers, notes, commit messages, memory, and
conversation. Removing it from a historical record is not required where the
edit would mangle the record; not writing it again is.

## 4. Don't run a record job from a stale or uncommitted build

The A1 incident's root was a fix that existed but was never committed, so it
never reached the deployment (a remote box ran a clean-but-*stale* binary). The
build stamps `GIT_REV` with `-dirty` when the tree differs from HEAD.

Enforced as a **pre-launch checklist gate**, not a code guard — chosen
deliberately: a code guard you bypass with `--allow-dirty` every time trains you
to ignore it, and a code guard can't catch the clean-but-stale-remote case that
actually bit us (only a human verifying "is my fix *in* this binary?" can). See
[job-checklist.md](job-checklist.md) item 4: before any run whose result you keep,
confirm the deployed binary's rev is clean **and** contains the change you intend.

## What these do NOT cover

These catch **regressions vs. known-good behavior**, fast. They do not certify a
**novel** frontier result (a21+) beyond known values — that still needs the
independent mod-p cross-check (audit A6, deferred). Don't read a green
`ns-gate-fast` as "the new number is right," only as "nothing known broke."
