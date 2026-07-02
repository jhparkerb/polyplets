# a(25) — fixed polyplets (king-move animals), CERTIFIED 2026-07-02

```
a(25) = 14,994,811,325,186,658,577
```

Computed dalby-solo (`docs/a25-dalby-solo-launch.md`/`scripts/dalby_a25.sh`,
rev `54d41fc`). Real-swept H1-16; H17-25 filled by closed-form diagonal
injection (P₀-P₈, `orchestrator/sweep.go` `diagonalCell` cases 0-8). At launch
time this left the run **single-source, computed tier**: one engine, one box,
and T(25,17) — P₈'s only genuinely new prediction beyond its own fitting
range (n=17..24) — was an unconfirmed extrapolation.

`docs/a25-verification-plan.md` defined three independent, parallel jobs to
close every open trust gap without re-running the expensive parts. All three
**PASS**:

## Job 1 — H17 sweep (ayr, closes Group C: the k=8 cell) — PASS

Real (non-closed-form) sweep of H=17 at maxn=25 on ayr (x86/gcc — a different
compiler AND ISA from dalby's clang/ARM production run), rev `54d41fc`.

```
$ awk '/^25 /{print $2}' runs/ns_a25_verify/perheight/h17.out
187767529262410933
```

**Matches the P₈ prediction exactly** (`T(25,17) = 187,767,529,262,410,933`).
This was P₈'s one genuinely falsifiable extrapolation (all 8 of its defining
points are n=17..24; n=25 was never in the fit) — real sweep confirms it.
Wall 45841.5s (~12.7h) on ayr's 30 cores.

## Job 2 — u128 overflow check (dalby, closes Group D-arithmetic) — PASS

Re-swept the stripe H3-16 at maxn=25 with `--counter u128` (exact to ~a48;
the production run used u64, exact only to a25 — right at the boundary).
Compared cell-by-cell against the production u64 rows
(`results/ns_a25/swept_rows.txt`):

```
H3 OK  H4 OK  H5 OK  H6 OK  H7 OK  H8 OK  H9 OK
H10 OK H11 OK H12 OK H13 OK H14 OK H15 OK H16 OK
```

All 14 heights byte-identical between u64 and u128 — no overflow/carry bug in
the u64 stripe. (Comparison required stripping stray `\r` from
`swept_rows.txt` — a CRLF artifact in that file from an earlier remote pull,
cosmetic only, does not affect its numeric content or any prior use of it,
e.g. the P₉/P₁₀ derivation scripts already parse it with `.rstrip("\r\n")`.)

## Job 3 — Redelmeier per-height (gympie, closes Group D-logic) — PASS

Independent enumeration algorithm (Redelmeier generate-and-count via
`build/g2 square8`), fully separate code path from the transfer-matrix
`stepColumnSquare8` engine that produced the production sweep. Reached n=17.

```
$ python3 scripts/verify_redelmeier.py runs/ns_a25_verify/redelmeier_n17.txt results/ns_a25/swept_rows.txt
PASS: all 119 swept cells (H=3..16, n<=17) match Redelmeier.
```

Every swept T(n,H) for H=3..16, n≤17 matches an algorithm that shares no
logic with the production engine.

## Certification

All three jobs PASS → **a(25) is certified** (tier: computed → certified).
Every previously-open trust gap is closed:
- Group A (H1,2; diagonals k=0,1,2): proven closed forms (`docs/proofs/`).
- Group B (k=3-7 diagonals): closed by the desk audit
  (`scripts/audit_diagonals.py`) prior to this run.
- Group C (k=8 diagonal, T(25,17)): closed by Job 1 (real sweep matches the
  extrapolated prediction exactly).
- Group D (arithmetic + engine logic): closed by Jobs 2 and 3
  (independent counter width, independent algorithm).

## Files

- `results/ns_a25/provenance.txt`, `provenance_triangle.txt` — T(25,H)
  breakdown and full triangle provenance (generated before Job 1 landed; the
  H=17 row there is annotated `?` for not-yet-confirmed — now confirmed).
- `results/ns_a25/swept_rows.txt` — real T(n,H) data, H=3-16, n=1-25 (the
  ground truth Jobs 2/3 verified against, and the source data for the P₉/P₁₀
  closed-form derivations in `scripts/derive_p9.py`/`derive_p10.py`).
- `docs/a25-verification-plan.md` — the verification plan this RESULT
  reports against.
