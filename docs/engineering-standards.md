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

## 4. (OPEN) Don't run a record job from an uncommitted build

*Not yet adopted — enforcement undecided.* The A1 incident's root was a fix that
existed but was never committed, so it never reached the deployment. The build
already stamps `GIT_REV` with a `-dirty` suffix when the tree differs from HEAD.
Two candidate enforcements, to be chosen:
- a checklist line in [job-checklist.md](job-checklist.md) (provenance section)
  — "binary rev is clean, not `-dirty`"; lightweight, fits the existing
  pre-launch ritual; or
- a startup guard in `orchestrate` that refuses a real run on a `-dirty` rev
  unless `--allow-dirty` — stronger, but easy to habitually bypass.

## What these do NOT cover

These catch **regressions vs. known-good behavior**, fast. They do not certify a
**novel** frontier result (a21+) beyond known values — that still needs the
independent mod-p cross-check (audit A6, deferred). Don't read a green
`ns-gate-fast` as "the new number is right," only as "nothing known broke."
