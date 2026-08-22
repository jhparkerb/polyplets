# The D2ax bit and the CRT ladder do not combine — and the provenance table is a height stale

2026-08-22, executing `docs/last-orders.md` C1.4. Desk arithmetic; no compute
job.

## The combination, and why there is nothing in it

C1.4 asked whether the two independent modular views of the triangle compose
into a single per-cell warrant:

- `results/subgroup-mod4.md` ships `T(n,H) ≡ I_H(D2ax) (mod 2)` on all 820
  cells, one bit per cell from the height-preserving subgroup, sharing nothing
  with any enumeration;
- the Motley ladder produces every cell modulo nine primes near 2¹⁶ and
  reconstructs by CRT, holding one prime out as a check.

**They do not compose, and the reason is that CRT is not partial.** <!--q:prose-->
Once the reconstructing primes give the exact integer, that integer determines
its own parity. The D2ax bit is then a check on a value already known exactly —
which is precisely how `subgroup-mod4.md` already uses it, and it is already
recorded in `results/provenance-table.md` as source tag **C, "congruence
only"**.

Nor does the parity substitute for a prime. Nine primes near 2¹⁶ give a modulus
of about 2¹⁴⁴; adjoining the modulus 2 makes it 2¹⁴⁵, a gain of 0.7%. There is
no regime in which the bit buys a pass, a prime, or a cell.

**Verdict: nothing to build.** The two views are already combined, in the only
way they can be — one checks the other — and the provenance table already says
so. This is the accounting test returning "already shipped", which is the same
answer breadth-pass row #19 got for the same subgroup work.

## What the item did surface

Checking what the provenance table records turned up that it is **stale by one
height**, in the conservative direction.

`scripts/provenance_table.py` line 58:

    MOTLEY_H = 18          # Confetti landed 2026-08-19, results/motley-h18.md

Confetti is the Nmax-40 ladder. The **Nmax-41 ladder landed 2026-08-21** and
covers H = 1..19 — `results/cutcount_b1/rows41/C1.out .. C19.out`, banked, with
its own README, the held-out prime green at all nineteen heights, and
`T(40,19) = 3247572468599336484342102174163` agreeing with the incumbent. So
Motley's rule-independent reach is 19, not 18, and has been since the day
before this was written.

The table's headline consequence is the six cells "carrying **only** the mod-4
congruence — no exact recount, no closed form"
<!--q:congruence_only.count@18=6-->:

    T(38,19), T(39,19), T(39,20), T(40,19), T(40,20), T(40,21)
    <!--q:congruence_only.cells@18=(38,19),(39,19),(39,20),(40,19),(40,20),(40,21)-->

Three of those six are at H = 19 and are now directly computed by a second
program. `make gate-provenance` does not catch this: the gate regenerates the
table from the generator and fails if the *published note* drifts from it, so a
stale constant in the generator is reproduced faithfully by both sides and the
gate stays green. The gate protects against transcription drift, not against
the generator being behind the evidence.

This is a front-door problem, not a bookkeeping one: `README.md` puts
`results/provenance-table.md` on page one as the answer to "why should I
believe a(40)", and the answer currently on that page is a day out of date and
understates itself.

**Filed as an A item** in `docs/last-orders.md` — because fixing it means
advancing `MOTLEY_H`, regenerating, and re-reading the congruence-only set,
which is work rather than a note. <!--q:prose-->

## Honest limits

- The 0.7% CRT figure assumes the nine primes are the ones the ladder used
  (near 2¹⁶, per `results/cutcount_b1/rows41/README.md`). With 31-bit primes
  the fraction is smaller still, so the conclusion is not sensitive to it.
- "CRT is not partial" is true of the reconstruction as run. A scheme that
  deliberately reconstructed modulo a product *smaller* than the value and used
  the parity plus a size bound to disambiguate is not excluded by the above —
  but it would need the value bracketed to within a factor of two, which
  nothing here supplies.
