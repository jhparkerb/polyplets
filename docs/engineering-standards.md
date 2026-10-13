# Engineering standards

Standing practices that turn a silent wrong answer, or a fix that never
reached the deployed binary, into an immediate failure. Keep them few; keep
them enforced.

## 1. Gates run automatically, not by memory

A gate that isn't run rots.

- Pre-push hook. `make install-hooks` points `core.hooksPath` at
  `.githooks/`; the `pre-push` hook runs `make ns-gate-fast` (under ~16s: the
  full Go suite plus the sub-second C++ format/arith gates). Run once per clone.
  `git push --no-verify` bypasses it; then fix what you skipped.
- Full suite before a release or record run: `make ns-gates` adds the heavy
  C++ sweeps (spill, parallel, holes, maxn=14 regression).
- No GitHub Actions; the hook is the enforcement point.

## 2. Encode known truths as cheap invariant gates

Anything we can state as an invariant is a free, fast tripwire.

- `make ns-gate-closedform` asserts every known closed form is contributed
  directly, never enumerated (top strip `T(N,N)=3^(N-1)`; low strips `T(n,1)=1`,
  the `T(n,2)` recurrence). Add a case here the moment a new closed form or
  conservation law is established, before it can be silently recomputed.
- The same applies to any new invariant (partition-independence, fold ==
  unfold, growth-ratio bounds): a five-line assertion is cheaper than a wrong
  number.

## 3. Two standing code rules

- Fail closed. A new flag, guard, or parser defaults to refuse. The silent
  failures we have had (counter overflow, missing shard, unreadable input,
  resume config mismatch, unknown counter tag) all continued with a wrong
  number instead of stopping at the start. When in doubt, refuse and make the
  caller opt in.
- A test that fails first. A bug fix is not done until a test that failed on
  the old code passes on the new, and the captured failure goes in the commit
  message. Ship the test with the fix; a fix without a regression test is how
  the same bug comes back.

## 3b. Never weigh a cell by its size

A term is wrong if any one of its cells is wrong. So "T(40,19) is 5.7% of
a(40)", "43.84% of a(40) has no second source", "97% rule-independent" and every
other share-of-a(n) figure is banned: it is a number with no decision attached
to it, and it invites the reading it cannot support, that a term is partly
trustworthy in proportion to the cells that were checked.

State cells. "Eleven cells of the triangle have one source, and here they are"
is the same fact without the false arithmetic. `results/provenance-table.md` is
the form to copy, and `make gate-provenance` pins the count.

This applies to papers, notes, commit messages, and conversation.

## 4. Don't run a record job from a stale or uncommitted build

The build stamps `GIT_REV` with `-dirty` when the tree differs from HEAD. A fix
that exists but was never committed never reaches the deployment, and a remote
box then runs a clean but stale binary.

Enforced as a pre-launch checklist gate, not a code guard: a code guard you
bypass with `--allow-dirty` every time trains you to ignore it, and a code guard
cannot catch the clean-but-stale-remote case (only a person verifying "is my fix
in this binary?" can). See [job-checklist.md](job-checklist.md) item 4: before
any run whose result you keep, confirm the deployed binary's rev is clean and
contains the change you intend.

## 5. Code reaches a remote box by `git pull`, and by nothing else

Commits are pushed whenever they are made, and code arrives on the compute
servers by git pull only, running from one checkout per box (or a sharply
limited number of worktrees, each a real worktree of that checkout).

No `rsync`, no `scp` of source, no hand-copied `foo2.cpp` / `foo4.cpp`
alongside `foo.cpp`. Job scripts are committed and invoked from the checkout.
Binaries are built by the Makefile in the checkout, so `GIT_REV` is a rev.

What copying instead of pulling produces:

- A tree that cannot pull: a checkout whose `origin` points at a local bundle
  file, so pushing never reaches it, and files arrive by `scp` and sit
  untracked.
- A silent path bug: `rsync -a a b c host:dir/` flattens, so a generator edit
  lands at the repo root instead of `scripts/` and a "fixed" gate run tests the
  unfixed generator.
- A stray polluting a gate: an engine source hand-copied beside the original
  under a `_rel` suffix is picked up by the `cpp/*.cpp` glob in
  `scripts/compile_db_sources.txt` and fails `gate-compile-db` on a file that is
  not in the repo at all.
- A missing build rule: an engine built by hand with no Makefile rule is not
  buildable from the tree, and the compile-database gate is what eventually
  says so.
- A provenance defect on a record run: a binary built from a hand-copied source
  stamped with a branch name instead of a rev, which item 4 forbids.

The rule composes with item 4: if the only way code arrives is a pull, then "is
the deployed binary's rev clean and does it contain my change?" is answerable by
`git log` on the box instead of by memory.

## Scope

These catch regressions against known-good behaviour, fast. They do not certify
a novel frontier result (a21+) beyond known values; that needs the independent
mod-p cross-check. A green `ns-gate-fast` means "nothing known broke", not "the
new number is right".
