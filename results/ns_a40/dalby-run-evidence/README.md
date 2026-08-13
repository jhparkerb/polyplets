# a(40) production run — preserved dalby-side evidence

Copied from `dalby.jhpb.org:src/polyominoes/runs/ns_a40/dalby/` on 2026-08-12,
byte-identical (sha256 verified against the remote at copy time, both sides
recorded below). Banked because this is currently the **only** material that
converts the a(40) provenance record from assertion into evidence, and it lived
in exactly one place, in a run directory alongside 983 MB of merge shards that
would plausibly be swept.

Identified by the round-3 provenance audit,
`results/triangle-r3-provenance.md` (queue rows ADV-2, PROV-2).

## What is here

| file | bytes | what it is |
|---|---|---|
| `run.log` | 3,821,306 | the production run's teed stdout, 28,316 lines |
| `POLYCKPT.A` | 1,213 | phase A checkpoint |
| `POLYCKPT.B` | 751 | phase B checkpoint |
| `POLYCKPT.C` | 722 | phase C checkpoint |
| `combine.log` | 1,136 | final combine step |
| `h20.out.zero-harvest-bug` | 191 | the preserved Zero Harvest artifact |

    sha256
    1da65fc81f7d3fe1b1a4349c0ed97e7f38f38b8016fef30bc4769af79f9345d8  run.log
    ab2b913165eb395a115ad60cdaa4b2c7e36aab3857a9596fbe06b79753141c24  POLYCKPT.A
    5b161d58602804ed7623445ba30e3ea0ab1476b60aaae16947175e89a8fb56ad  POLYCKPT.B
    ba957c4934dbb525a1883a77bb702c53e6744dadb150553cad8e4a9da468d7ec  POLYCKPT.C
    da9e478a439fd9de1805279b222393cc8477f639e0ba1d5a5b210b02ad8d5ecf  combine.log
    89e2e70dec4b4586fda6bb184016a8234a7998df3983c0b3745c8db6141364af  h20.out.zero-harvest-bug

## Why it is evidence rather than testimony

`run.log` carries eight `orchestrate` banners whose `rev=` is **build-stamped**
into the binary via the Makefile's `ldflags -X main.gitRev`, with the `-dirty`
suffix machinery (`main.go:193`, `330-333`) — not a value the script prints
from its own environment. Grepped at copy time: **zero `-dirty` anywhere**,
`kernel=kink` in every banner, and `max_diag_k=0` throughout, i.e. the P_19
closed form was not wired and H=21 was genuinely swept.

    line     1  cores=80  rev=38956525
    line 15060  cores=64  rev=38956525
    line 16263  cores=80  rev=801afd59
    line 16267  cores=48  rev=801afd59
    line 19307  cores=32  rev=801afd59
    (plus three further 801afd59 banners at 19309/19313/19317)

## Two things this does NOT establish

1. **Worker-binary identity.** The banners stamp the *orchestrate* build. The
   C++ worker processes — the ones that actually count — never log their baked
   `GIT_REV`, and dalby's `build/ns` was rebuilt on 2026-07-28 for the recheck,
   so the run-time worker binaries no longer exist. Worker identity is bounded
   inference (the only commit between the two revs is a malloc_trim worker
   change; the last counting-kernel source change predates both, so any
   candidate tree has byte-identical kernel source). Queue row PROV-1 proposes
   fail-closed worker self-identification for future runs.
2. **Phase B as recorded upstream.** `results/ns_a40/PROVENANCE.md` records a
   flat "48 cores" for phase B and no rev. The log shows two segments: cols
   0..6 at 64 cores on 38956525, cols 6..40 at 48 cores on 801afd59. Erratum
   only — the zero-harvest re-entry banner and the preserved artifact match the
   incident narrative exactly. Correcting `PROVENANCE.md` is jasonp's call and
   nothing banked was edited.
