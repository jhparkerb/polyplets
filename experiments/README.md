# experiments/ — one file per question asked

Each file here is the working behind a sentence somewhere in `results/`: a
derivation run once, a probe that measured a cost, a check that killed an idea.
They are kept so a result can be reproduced, not so they can be reused, and
they do not import each other except where a header says so. The conclusions
are in `results/`; the file headers say which record each one feeds.

**Eighteen of them are gate inputs**, run by `make gates` and therefore green
at every commit:

    grep -o 'experiments/[a-z0-9_/]*\.py' Makefile | sort -u

as of 2026-09-06 those are `cluster_weight_dp.py`, `convex_perimeter.py`,
`convex_tm.py`, `depth1_gap_walk.py`, `depth1_recurrence.py`,
`diamond_free_removals.py`, `multidirected_king.py`, `r1_sym_fold_check.py`,
the four `severance_w1/w2/w3*` gates and kernels, `slope2_law_vs_truth.py`,
and the three `undertow_*` gates.

Everything else ran once, on the date in its header. A script that takes
`--selftest` says so in its usage; several carry their own RED controls. None
of them is production: the enumerator is `core/`, `orchestrator/`, `worker/`
and `cpp/`, and the toolchain around it is `scripts/`.

The consolidation of 2026-09-06 deleted 170 files from here and from
`scripts/` that no tracked document cited; `docs/consolidation-plan.md` waves
4a and 4b name the commits they are readable at.
