# 13 — Fast independent frontier verification (relaxing bounds for speed)

**2026-07-02.** Goal: confirm a frontier term (a26+) independently *without* a
full ~2.5× re-run on ayr. The question posed: which bounds can we relax to buy
"slightly weaker but vastly faster" confirmation?

## The independence problem (why this is hard)

What could be wrong, and what catches it:

| bug class | caught by | cost |
|---|---|---|
| counter overflow / arithmetic | mod-p re-sweep (`sweep8_modp.h`) | enumeration-bound (≈ real run) |
| merge / data-structure / spill | mod-p re-sweep, or 2nd sort-engine run | enumeration-bound |
| transient / hardware / nondeterminism | any re-run of the same ranges | sample-fraction |
| **enumeration LOGIC (`stepColumnSquare8`)** | **only an INDEPENDENT stepper** | see below |

The catch: **`sweep8_modp.h` shares `stepColumnSquare8`** (sweep8_modp.h:26,178)
with the production sort engine. It differs only in counter (mod-p vs exact) and
store (hash vs sort-merge). So a mod-p re-sweep does **not** catch a bug in the
step kernel itself. The *only* truly independent stepper we have is **g2**
(Redelmeier, `cpp/g2_redelmeier.cpp` — no shared headers), and it is
enumeration-bound at **n≤19**, far below the frontier. It cannot be
range-restricted by signature (it is recursive generate-and-count, no columns).

So there is **no existing** check that is both (a) independent for kernel logic
and (b) reaches the frontier n. That gap (the "residual gap closed only by
independent reimplementation" note) is real.

## The bounds, and which to relax

1. **Exactness → mod-p.** Makes arithmetic single-word and an independent
   implementation simple. But enumeration is ~85–90% of cost, so mod-p *alone*
   is not faster — a full mod-p re-sweep on ayr is still ~2.5× dalby. Value:
   simplicity + catches arithmetic/overflow, not speed.
2. **Completeness → sample.** THE speed lever. Recompute a random k% of the
   expensive height's map ranges and check their subtotals. Cost = k%·(height
   cost). A systematic kernel bug corrupts a large fraction of ranges → caught
   w.h.p. even at small k; k is a tunable confidence knob. Requires the main run
   to emit per-range subtotals (it computes them anyway).
3. **Independence level → choose.** Sampling with the *same* sort engine
   (map_worker `--lo/--hi` on sampled ranges) is fast but catches only
   transient/nondeterminism. Sampling with an *independent* stepper catches
   kernel logic too — but that stepper must be built.

## Recommended scheme: sampled range audit + a clean-room stepper

The only design that is BOTH vastly faster AND independent-for-logic:

- **One-time:** write a clean-room column stepper — a second implementation of
  the king-graph frontier step that does **not** include `transition_square8.h`
  (different connectivity bookkeeping, e.g. explicit union-find on the boundary
  rather than the label-canonicalization scheme). It must be *correct*, not
  fast: it only ever processes a sample. Validate it against g2 at n≤19 and
  against the sort engine's per-height rows at small maxn.
- **Per term:** the main dalby run emits, for the expensive swept height(s),
  each map range's subtotal **mod a prime p** (cheap add-on; it already sums
  them). The auditor on ayr picks a random k% of those ranges, recomputes each
  with the clean-room stepper mod p (seed → sweep restricted to that key
  range), and checks equality. It also independently re-derives the range
  partition so a *missing-range* bug is caught, not just a wrong-subtotal bug.
- **Confidence:** a kernel bug that mis-steps a common signature corrupts many
  ranges → detection prob ≈ 1−(1−f)^{k·R} for f = fraction of ranges hit, near 1
  even at k=5–10%. Rare-signature bugs need higher k; raise it for the terms you
  most care about. Layer mod-two-primes to nail arithmetic coincidences.

**Cost:** ~k%·(height cost) per term — e.g. ~50 min on ayr at k=10% vs ~8.5 h
for a full re-run — plus the one-time clean-room stepper. It *replaces* g2's
n≤19 kernel-transfer argument with a check that actually touches the real
frontier n, at a fraction of a full re-run.

## Cheap corroborations to layer on (near-free, weak alone)

- **R1 reversal invariant:** `foldSig` already asserts σ and reflect(σ) complete
  identically; a per-height check that the frontier respects this catches an
  adjacency-symmetry bug for free.
- **Low-height recurrence:** {T(n,H)}_n is C-finite for small H
  ([[boundary-push-recurrence]]); fit on prior validated terms, verify the new
  term's low-H rows instantly. (Only low H — high-H order is ~frontier-sized.)
- **mod-p whole-sweep** (shared kernel) as the a25-style arithmetic/overflow
  guard — not independent for logic, but cheap insurance and already scripted.

## Honest bottom line

There is no free lunch that is independent-for-logic AND vastly-faster *without*
building the clean-room stepper. Given that, the sampled range audit is the
right investment: it is the cheapest path to closing the residual
independent-reimplementation gap, and its per-term cost scales with the sample
rate, not the term. Until it exists, frontier terms stay "computed, pending
certification," certified per-term by the a25 three-job recipe (mod-p overflow +
g2 low-height kernel + independent-ISA full re-sweep).
