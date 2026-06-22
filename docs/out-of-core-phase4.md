# Phase 4 — out-of-core column sweep (unbounded reach, disk-bound)

The four in-RAM levers (R1 fold, R2 ranged, R3 u32-modp, B blocked) cut the peak by
~10–14×, reaching ~a(25) on dalby. Past that the state set simply does not fit in RAM.
Phase 4 removes the RAM ceiling entirely by spilling the boundary-state store to disk —
slow, but unbounded. **B is precisely its seam**: B already drains the db store one hash
partition at a time and frees each; Phase 4 just *spills to disk* instead of freeing, and
*streams back* instead of holding everything resident.

> **STATUS: IMPLEMENTED + GATED** (`cpp/tma/sweep8_ooc.h`, `cpp/tma_ooc_test.cpp`,
> `tests/gate_ooc.py`, `make gate-ooc`). db and next live as S partition files; per column
> the db partitions are streamed in one at a time (harvest + transitions append
> `(target,row)` contributions to S spill files), then each spill is reduced into a
> RAM-sized FlatDB and written back as the next partition, then swapped by rename. Only
> ~one partition is resident at a time → peak RAM ≈ peak/S. Verified: out-of-core a(n) ==
> exact A006770 (n≤10) **and independent of S** (S=4 ≡ S=16, byte-identical), scratch
> self-cleaning. The reduce is `addCounts` exactly (duplicate-Sig contributions sum via
> `slot()`), so it composes with R1/R2/R3 unchanged. Serial + naive I/O (a per-record row
> buffer, S open spill files) — correct first; production tuning (buffered/batched
> records, larger S with a file-handle pool, overlap I/O with compute) is the next pass.

## Feasibility — already established
A FlatDB partition round-trips to disk **byte-identically**: `cpp/tma/checkpoint.h`
(`tmaCkptSave`/`tmaCkptLoad`) serializes the live `(Sig, counts-row)` set with an atomic
temp→fsync→rename and a crc32, and the gate proves a reload is bit-for-bit identical to a
clean run (the store is a *set* read via `for_each`, never via slot/probe order — same
reason `--reserve` is identity). So the only new work is the *dataflow*, not the I/O.

## The external-memory column step
Fix S hash partitions, S chosen so any single partition fits comfortably in RAM
(peakStates/S × per-state bytes ≪ RAM). Per column, with db partitions `db_0..db_{S-1}`
resident only on disk:

```
for i in 0..S-1:                       # stream db, one partition at a time
    load db_i from disk                # ~1 partition resident
    for each (sig, row) in db_i:
        for each viable mask:
            out = step(sig, mask)      # (apply R1 fold / R3 u32 here too)
            append (out, shifted row) to spill-bucket  next_{hash(out)&(S-1)}
    free db_i                          # release before the next
# now reduce each next bucket (which may have duplicate Sigs from many db_i):
for j in 0..S-1:
    load spill-bucket next_j (append-only list of (Sig,row) contributions)
    sum duplicates in a RAM FlatDB (fits)   # the only resident structure
    write next_j to disk;  free
swap db <-> next  (just a directory/file rename)
```

Peak RAM = **one db partition + one next bucket's reduced FlatDB + I/O buffers** — i.e.
`O(peakStates/S)`, made as small as desired by raising S. Everything else is on disk.
Correctness is identical to B (each db state processed once; contributions summed by Sig);
the per-bucket reduce is the only addition, and it is the same `addCounts` over a set.

## Cost and reach
- **Disk:** peak boundary store on disk ≈ peakStates × per-state bytes (with R1+R2+R3
  applied, ~250 B/state). a(26)≈1.8e9 states ⇒ ~0.45 TB; a(28)≈1.1e10 ⇒ ~2.7 TB. Routine
  for a spinning-disk array; the spill is sequential (append) + sequential (re-read).
- **Time:** two sequential disk passes over the store per column (stream db, reduce next).
  Bandwidth-bound, not seek-bound (sequential). At ~1 GB/s this is ~minutes/column for
  sub-TB stores — the "last resort," but it *terminates*.
- **Reach:** unbounded in n, limited only by disk and wall-clock. Combined with R1/R2/R3
  the disk footprint is ~10× smaller than naive, pushing the practical frontier to ~a(28).

## Status / next step
Design only (not built). The build is: (1) a partitioned on-disk store (reuse the
checkpoint serializer per partition); (2) the spill-bucket append + per-bucket reduce in
`sweep8_blocked.h`'s drain loop; (3) gate `out-of-core a(n) == exact` (small N, tiny S so
the disk path actually exercises). Highest-value once a(25) is in hand and a real term
past it is wanted — and per the standing guidance, only after confirming it is the best
use of the compute/space budget.
