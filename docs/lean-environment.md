# Lean environment: where things are, how to build

2026-08-09. Reference doc, not prose — a lookup table for (a) writing/building
Lean here and (b) finding existing lemmas before writing a new one. All paths
verified with `ls`/`find` against this machine on this date.

## 1. Project layout

- `/Users/jasonp/src/polyominoes/polyplets/` — the only Lean project in the
  repo (single `lakefile.toml`, single `lean_lib`).
- `polyplets/lean-toolchain` — pins `leanprover/lean4:v4.31.0`.
- `polyplets/lakefile.toml` — `name = "polyplets"`, `defaultTargets =
  ["Polyplets"]`, one `[[require]]`: `mathlib`, scope
  `leanprover-community`, `rev = "v4.31.0"`. `[leanOptions]`:
  `pp.unicode.fun = true`, `relaxedAutoImplicit = false`,
  `weak.linter.mathlibStandardSet = true`, `maxSynthPendingDepth = 3`.
- `polyplets/lake-manifest.json` — pins the resolved mathlib commit:
  `fabf563a7c95a166b8d7b6efca11c8b4dc9d911f` (tag `v4.31.0`).
- `polyplets/Polyplets.lean` — the root import file, 66 lines, one `import
  Polyplets.<Module>` per module (top-level modules plus `Grand.*` and
  `Universal.*` and `Upper.*` submodules).
- `polyplets/Polyplets/` — the module tree: 77 `.lean` files, in
  `Polyplets/` (top level), `Polyplets/Grand/` (8 files), `Polyplets/
  Universal/` (13 files), `Polyplets/Upper/` (5 files).
- `polyplets/Draft/Prop6Skeleton.lean` — deliberately outside the build
  (contains `sorry`s, states architecture only). Not in `Polyplets.lean`,
  never compiled by `lake build`. See `docs/lean-artifact.md`.
- Non-Lean surroundings for context: `polyplets/PLAN.md`,
  `polyplets/PROOF-STATUS.md` (per-theorem ledger), `polyplets/
  GRANDFORM-PLAN.md`, `polyplets/OUTWORKS-PLAN.md`, `polyplets/DESIGN.md`,
  `polyplets/build-receipt-*.log` (dated build receipts).

## 2. Toolchain (elan)

- `~/.elan/toolchains/` has two installed toolchains:
  `leanprover--lean4---v4.31.0` (the pinned one) and
  `leanprover--lean4---v4.32.2`.
- `~/.elan/bin/` — `elan`, `lake`, `lean`, `leanc`, `leanchecker`,
  `leanmake`, `leanpkg`. These are elan shims that resolve to the toolchain
  pinned by the nearest `lean-toolchain` file, so run `lake` as
  `~/.elan/bin/lake` **from inside `polyplets/`** to get v4.31.0.
- Toolchain-specific binaries actually invoked:
  `~/.elan/toolchains/leanprover--lean4---v4.31.0/bin/{lean,lake,leanc,
  leanchecker,leanir,leanmake,cadical,clang,ld64.lld,llvm-ar}`.
- Core-library Lean **sources** (for lemma search) are at
  `~/.elan/toolchains/leanprover--lean4---v4.31.0/src/lean/` — subdirs
  `Init/`, `Std/`, `Lean/`, plus root files `Init.lean`, `Std.lean`,
  `Lean.lean`. (Not `lib/lean4/library` — that path does not exist on this
  toolchain; `lib/lean/` under the toolchain root holds compiled `.olean`
  and shared libraries, not `.lean` sources.)

## 3. Vendored dependencies (`polyplets/.lake/packages/`)

Each row: package dir name -> Lean source-root subdir (the one to grep),
file count, on-disk size of that subdir.

| package dir        | source root       | .lean files | size |
|---------------------|-------------------|------------:|-----:|
| `mathlib`           | `Mathlib/`        | 8169        | 107M |
| `batteries`         | `Batteries/`      | 175         | 1.3M |
| `aesop`             | `Aesop/`          | 137         | 900K |
| `proofwidgets`      | `ProofWidgets/`   | 37          | 216K |
| `importGraph`       | `ImportGraph/`    | 23          | 100K |
| `plausible`         | `Plausible/`      | 12          | 124K |
| `Qq`                | `Qq/`             | 13          | 100K |
| `Cli`               | `Cli/`            | 2           | 80K  |
| `LeanSearchClient`  | `LeanSearchClient/`| 3          | 40K  |

Mathlib dominates: an unscoped recursive grep across `.lake/packages/` costs
essentially one 8169-file, 107M scan of `Mathlib/`. Scope greps as below.

## 4. Lemma-search recipes

A Lean declaration reachable from this project lives in one of exactly these
places — the exhaustive search list:

1. `polyplets/Polyplets/` (project's own 77 files)
2. `polyplets/.lake/packages/mathlib/Mathlib/`
3. `polyplets/.lake/packages/batteries/Batteries/`
4. `polyplets/.lake/packages/aesop/Aesop/`
5. `polyplets/.lake/packages/proofwidgets/ProofWidgets/`
6. `polyplets/.lake/packages/importGraph/ImportGraph/`
7. `polyplets/.lake/packages/plausible/Plausible/`
8. `polyplets/.lake/packages/Qq/Qq/`
9. `polyplets/.lake/packages/Cli/Cli/`
10. `polyplets/.lake/packages/LeanSearchClient/LeanSearchClient/`
11. `~/.elan/toolchains/leanprover--lean4---v4.31.0/src/lean/` (`Init/`,
    `Std/`, `Lean/`) — Lean core itself

Concrete one-liners (run from repo root; all paths explicit, no filesystem
scan):

```
grep -rn 'countP_eq_length_filter' \
  /Users/jasonp/src/polyominoes/polyplets/.lake/packages/mathlib/Mathlib

grep -rln 'theorem.*supermul\|lemma.*supermul' \
  /Users/jasonp/src/polyominoes/polyplets/.lake/packages/mathlib/Mathlib \
  /Users/jasonp/src/polyominoes/polyplets/Polyplets

grep -rln 'native_decide' \
  /Users/jasonp/src/polyominoes/polyplets/Polyplets
```

Often faster than grepping for a candidate name: drop it into a scratch
`example` inside a Lean file already open in the editor and read Lean's
"unknown identifier" error (which sometimes suggests a rename) or run
`exact?` / `apply?` at the goal — both search mathlib's declaration index
directly and report a usable term, without touching the shell at all.

## 5. Build commands

All `lake` invocations below run from `polyplets/` and use
`~/.elan/bin/lake` (resolves to v4.31.0 via `polyplets/lean-toolchain`).

- Single module: `cd polyplets && ~/.elan/bin/lake build Polyplets.<Module>`
  (e.g. `Polyplets.Fekete`, `Polyplets.Grand.Audit`).
- Full project, cold: `cd polyplets && ~/.elan/bin/lake build` — mathlib
  build dominates; the project's own 77 files build in minutes once
  mathlib's `.olean`s are cached.
- Verify already-current: `cd polyplets && ~/.elan/bin/lake build
  --no-build` (~6 s per `docs/lean-artifact.md`).
- Repo gate for the notary campaign, `make gate-notary` (repo root,
  `Makefile:393-400`): greps `NOTARY_MODULES` (ten named files under
  `polyplets/Polyplets/GapWalk*` and `DepthOne*`) for `sorry`/`axiom`/
  `admit` and fails RED if any hit, then runs
  `lake build Polyplets.GapWalkBridge Polyplets.DepthOneConstants
  Polyplets.DepthOneSeries Polyplets.GapWalkRows Polyplets.GapWalkCanon
  Polyplets.GapWalkTrunc Polyplets.GapWalkStacks Polyplets.GapWalkPeel
  Polyplets.GapWalkEnds Polyplets.GapWalkBij`.
- Bare `make` (repo root) — runs the full engineering-standards gate list
  including `gate-notary`; per `docs/engineering-standards.md` this is the
  session-level check, not any single narrower gate.
- Build cache: `polyplets/.lake/build/lib/lean/` holds per-module
  `.olean`/`.ilean`/`.trace` files (e.g. `Polyplets.olean`); `polyplets/
  .lake/build/ir/` holds the generated `.c`/hash files. Deleting
  `polyplets/.lake/build/` forces a full rebuild of the project's own
  modules (vendored package `.olean`s live under each package's own
  `.lake/build/`, untouched by that).

### `#guard_msgs` axiom audits

Pattern lives in `polyplets/Polyplets/Grand/Audit.lean` (18 guarded
`#print axioms`) and `polyplets/Polyplets/AuditOutworks.lean` (70 more).
Example, `Grand/Audit.lean:38-40`:

```
/-- info: 'Polyplets.d_mu_rec' depends on axioms: [propext, Classical.choice, Quot.sound] -/
#guard_msgs in
#print axioms d_mu_rec
```

`#guard_msgs` pins the expected `#print axioms` output as a doc comment
immediately above; if the real footprint drifts (a new axiom, a dropped
`native_decide` leaf, etc.), the string comparison fails and `lake build`
errors — so axiom-footprint drift is a build failure, not something a
reviewer has to remember to check. 88 theorems are guarded this way; 148
more print footprints unguarded (informational only). See
`docs/lean-artifact.md` for the full standard/native breakdown.

## 6. Editor/config, linter conventions

- No `.vscode/` directory anywhere in the repo (`polyominoes/` or
  `polyominoes/polyplets/`) — no committed editor settings.
- `lakefile.toml`'s `[leanOptions]` (section 1 above) are the only
  project-wide Lean options; no `moreLeanArgs`/`moreServerArgs` set.
- Per-file `set_option` conventions actually used in `Polyplets/`:
  - `set_option linter.style.nativeDecide false` — silences the
    style linter's warning about `native_decide` use, in every module that
    has a named native leaf (`Compute.lean`, `ComputeBridge.lean`,
    `Weights.lean`, `Weights3Heavy.lean`, `WeightsChunk{A,B,C,E,G}.lean`,
    `Sequence.lean`, and others).
  - `set_option maxRecDepth <n>` (4000-10000) and `set_option
    maxHeartbeats <n>` — raised beside heavy `native_decide`/`decide`
    enumerations (`GapWalk.lean`, `Weights3Heavy.lean`,
    `WeightsChunkA.lean`).
  - `set_option linter.style.longLine false` — on files with an
    unavoidably long generated line (`Pin.lean`, `StairGrowth.lean`).

## See also

- `docs/lean-artifact.md` — the development as a citable artifact: module
  count, line count, sorry count, the full axiom-footprint accounting.
- `docs/notary-lean-plan.md` — an example of a Lean work plan in this
  repo's style, including which modules are/aren't formalized for a given
  campaign.
- `polyplets/PROOF-STATUS.md` — the per-theorem proof ledger.
