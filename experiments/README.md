# experiments/

Each file here is the calculation behind a statement in `results/`: a
derivation run once, a measurement, or a check that ruled an idea out. They
are kept so a result can be reproduced, not for reuse, and they do not import
each other except where a header says so. Each file's header says which note
it serves.

Some are also run by `make` as checks, so they pass at every commit:

    grep -o 'experiments/[a-z0-9_/]*\.py' Makefile | sort -u

The rest were run once. A script that takes `--selftest` says so in its usage.
None of this is the production enumerator, which is `core/`, `orchestrator/`,
`worker/` and `cpp/`; the tools around it are in `scripts/`.
