# Disk does not scale like CPU — the Nmax-45 sweep fits

**2026-08-24, dalby, 40 cores, rev `7429268b1`.** `scripts/dalby_nmax_disk.sh`,
raw output `~/var/nmax-disk/disk.txt`.

`docs/five-terms-plan.md` priced the Nmax-45 sweep's disk peak at **~580 GB
against 563 GB free** and concluded it "does not fit", making a ~160 GB
cleanup a precondition for the fifth term. That number was the **measured CPU**
factor for Nmax 40→45 applied to the a(40) run's measured 363.4 GB disk peak.
Nothing had checked that disk and CPU scale alike. They do not.

## Measured

Peak run-dir size, sampled every 10 s, spill kept:

| H | Nmax 40 | Nmax 42 | Nmax 45 | 40→45 | 40→44 (interpolated) |
|---|---|---|---|---|---|
| 14 | 499 MB | 437 MB | 580 MB | 1.162 | 1.058 |
| 15 | 1,244 MB | 1,533 MB | 1,872 MB | **1.505** | 1.408 |
| 16 | 3,634 MB | 4,456 MB | 5,040 MB | **1.387** | 1.331 |

**H=14 is not usable.** Its Nmax-42 peak reads *below* its Nmax-40 peak, which
is impossible; at 40 cores those runs are under a minute, so 10 s sampling gets
six samples and misses the peak. It is reported rather than dropped because it
is the evidence for how coarse the sampling is, and that caveat applies in
smaller measure to H=15 and H=16 too — every figure here is a floor on the
true peak.

## What it implies

Against the a(40) run's 363.4 GB measured peak (`results/ns_a40/`):

| target | factor | projected peak | vs 563 GB free |
|---|---|---|---|
| Nmax 44 | 1.331–1.408 | 484–512 GB | **+51 to +79 GB** |
| Nmax 45 | 1.387–1.505 | 504–547 GB | **+16 to +59 GB** |
| Nmax 45, as the plan assumed | 1.620 | 589 GB | −26 GB |

**Both targets fit, on every usable reading, with nothing deleted.** The plan's
1.62× was too pessimistic by 8–17%.

## Why the direction is the interesting part

The CPU factor **climbs** with height: 1.442 at H=14, 1.466 at H=15, which is
what the plan extrapolated out six heights to ~1.6 at H=21. The disk factor
**falls**: 1.505 at H=15, 1.387 at H=16. Applying a rising CPU exponent to disk
was not a conservative simplification; it moved the estimate the wrong way.

Two rungs pointing down is not a law, and it is the same weak shape the plan
flagged in its own CPU extrapolation — two points setting a slope run out five
more heights. It is stated here as what it is. What it is *enough* for is the
negative claim: nothing in the measurement supports 1.62×, and the cleanup that
number was demanding is not needed.

## What this does not decide

It removes disk as an argument against the fifth term. It says nothing about
the other one, which stands unchanged: **row 45 rests on level k=23, which has
one pin pair and no holdout.** Depth 5 does not reach it — `D_5` stops at k=21
with a K=21 table — so a(45) would ship with a caveat that a(41)..a(44) do not
carry. That is a publication question, not a disk question.
