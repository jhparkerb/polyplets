# Ghost Ship — sandbox specification (published pre-launch)

2026-08-15. Companion to `docs/ghostship-preregistration.md` §2. This file is
the published, mechanically derived sandbox definition; it is itself excluded
from the sandbox (`results/ghostship/**`).

## Cut

`74b2c2036531080ca6828df6e99df1bee10c6553` — 2026-07-12 17:59,
"tool(convex): restore lost 38-term transfer matrix (convex-mirage TODO)".
The last commit before the perimeter idea existed.

## Slice derivation (no hand filtering)

Core: the 7-file self-contained slice measured in
`review/R3-mechanics.md` §(b) — `results/convex-polyplets.md` plus its
markdown-reference closure at the cut.

Targets: every repo path matched by
`grep -o -E '(docs|results|experiments|scripts|paper|build|tests)/[A-Za-z0-9_./-]+'`
over the 7 core files at `74b2c20` (trailing punctuation stripped, sorted,
deduped) that is not already in the core: exactly 14 paths, all present at
the cut (verified 2026-08-15 with `git cat-file -e`). Zero dangling
references in the shipped slice.

### The 21 files

Core (7):

    docs/proofs/convex-mirage.md
    docs/proofs/polyplet-upper-bound.md
    results/convex-polyplets.md
    results/defect-gas.md
    results/directed-king-animals.md
    experiments/convex_polyplets.py
    experiments/convex_tm.py

Referenced targets (14):

    docs/proofs/diagonal-law.md
    experiments/certificate_bound.py
    experiments/cluster_weight_dp.py
    experiments/defect_gas.py
    experiments/diagonal_law_proof_check.py
    experiments/holefree_gas.py
    experiments/kernel_bound.py
    experiments/king_bound_fast.py
    experiments/king_bui.py
    experiments/king_certificate.py
    experiments/king_slack.py
    experiments/king_types.py
    experiments/spine_deeper.py
    results/strip-growth-lambda-bounds.md

## Build commands (run verbatim at launch; output shipped as-is)

    cd ~/src/polyominoes
    git archive 74b2c20 -- \
      docs/proofs/convex-mirage.md docs/proofs/polyplet-upper-bound.md \
      results/convex-polyplets.md results/defect-gas.md \
      results/directed-king-animals.md experiments/convex_polyplets.py \
      experiments/convex_tm.py docs/proofs/diagonal-law.md \
      experiments/certificate_bound.py experiments/cluster_weight_dp.py \
      experiments/defect_gas.py experiments/diagonal_law_proof_check.py \
      experiments/holefree_gas.py experiments/kernel_bound.py \
      experiments/king_bound_fast.py experiments/king_bui.py \
      experiments/king_certificate.py experiments/king_slack.py \
      experiments/king_types.py experiments/spine_deeper.py \
      results/strip-growth-lambda-bounds.md \
      | ssh dalby.jhpb.org 'mkdir -p ~/var/ghostship/sandbox && tar -x -C ~/var/ghostship/sandbox'

    git log 74b2c20 --date=iso-local -- <the same 21 paths> \
      > /tmp-stage/HISTORY.txt   # shipped unfiltered; clean by construction
    # (staged locally, copied into ~/var/ghostship/sandbox/HISTORY.txt)

Excluded always: `.git`, `results/ghostship/**`, `docs/ghostship-*`, all
memory content, `~/.claude/CLAUDE.md`, project CLAUDE.md, `oeis/`, viva
files. The sandbox is an archive export — no object store, no refs; a
worktree would share `.git` and is not blind.

## Tool availability at the cut

Both inherited scripts are Python 3 stdlib only (`sys`,
`collections.defaultdict`). No Makefile, no GMP, no mpmath, no build/.
Measured cost from the note's own table: n=100 in 3.07 s / 17.2 MB; n=200
in 47.9 s / 23.3 MB. Seconds-scale desk compute, as §2 requires.

## C4 review (leak sweep, run 2026-08-15)

Sweep: `grep -i -E 'semiperimeter|perimeter|temperley|A187077|A059716|column.convex'`
over all 21 files at the cut. Findings:

- **Present in the slice**: "convex is a *perimeter* tractability lever"
  (`convex-mirage.md` ×3, `convex-polyplets.md:18`) and the name
  "Temperley column-convex 3.2056" as a growth-constant comparison
  (`convex-polyplets.md:32`).
- **Ruling: not a leak.** The cut is a time cut; these lines were on disk
  when the court sat down on 2026-07-12 and the court still took 24 minutes
  to act on the first and 61 more to act on the second. Both arms start
  from the identical corpus, hints included. Consequence for grading: the
  rungs measure **acting on a hint already on disk**, not inventing it —
  the answer key and prediction files must be read with that scope.
- **Absent from the slice**: A187077, A059716, semiperimeter (the word),
  any statement that perimeter-counting for *king* convex animals is
  D-finite, and rung 3 in any form. The withheld ladder stays withheld.
