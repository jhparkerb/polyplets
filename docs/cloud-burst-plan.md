# Cloud burst sizing — cost-optimal, zero-waste

**2026-07-02.** Goal: accelerate a29/a30 with cloud compute, optimized for cost
*and* ~zero false starts / wasted jobs. The zero-waste priority drives the whole
shape: **do not pre-commit a30 cloud spend; stage and calibrate first.**

## 1. What cloud can and cannot accelerate

The wall is floored by the **single most expensive height**, which is an
inherently sequential column sweep (column j needs column j−1's frontier). It
cannot be split across nodes — only across cores of ONE box. So:

- Cloud helps **only** by giving the top height a box with **more physical cores
  than dalby's 80**. Everything else (cheaper heights) home boxes already cover
  for free.
- Extra *small* boxes (gympie, a second cloud node) do **nothing** for the floor
  — see the a29/a30 analysis: gympie saves ~1h on a29, ~0 on a30.
- Therefore the cloud burst is **one big single-node box running the top
  height**, while dalby+ayr sweep the rest at home in parallel.

## 2. The cost driver you must measure before sizing (the anti-waste core)

Per-term compute growth has two wildly different regimes:

- **Cheap path** — P11/P12/P13 close on schedule, so the top *real* height stays
  pinned ~H16–17 and each term is the mild "+1 maxn, same tier" ≈ **1.5×/term**.
  Then a30 may even finish at home in ~2–3 days; cloud is optional.
- **Expensive path** — a P_k lags, a new height tier opens, ≈ **4.4×/term**
  (measured reach factor). Then a30's top height is 20–100M cpu-s and cloud
  matters a lot.

The spread is **5–20×**. a26 measured 259,913 cpu-s (swept H1–15, 80% core
efficiency, 68 min). a27 is running now and gives the first real post-u128 data
point; a28 calibrates a29; a29 calibrates a30. **Sizing a30 cloud off today's
extrapolation would be the exact "wasted job" risk to avoid** — the prediction
could be off by 10×. Size it off a29's *measured* top-height cpu-s.

## 3. Staged plan (each stage gates the next)

| stage | where | why | cloud? |
|---|---|---|---|
| a28 | home (dalby H_top + ayr rest) | ~7.6h est; confirms P11 closed, measures growth | no |
| a29 | home, or cloud if a28 shows expensive path | ~1 day home if cheap path | maybe |
| a30 | **size from a29's measured top-height cpu-s** | only now is the number real | yes if expensive |

Do not skip ahead. a28 and a29 landing convert the 5–20× uncertainty into a
number, and only then is a30 cloud a calculable spend rather than a gamble.

## 4. Instance sizing (when a30 cloud is warranted)

- **ISA: x86-64** to match dalby/ayr — reuse the same validation, avoid a fresh
  cross-ISA proof. (AMD Genoa / Intel Sapphire Rapids both fine.)
- **Physical cores, not vCPU.** The map body is integer-bound enumeration
  (`viableRec`); SMT hyperthreads add only ~1.2×, not 2×. A "192 vCPU" box with
  96 physical cores ≈ ~115 effective cores; a 192-**physical**-core box ≈ 192.
- **Recommended:** `hpc7a.96xlarge` — **192 physical cores** (AMD Genoa, no SMT),
  768 GB, low-variance HPC fabric. ~2.4× dalby. On-demand ≈ $7–8/hr.
  **Fallback (easier to launch):** `c7i.48xlarge` — 96 physical + SMT ≈ 1.4×
  dalby, ~$8.6/hr.
- **On-demand, NOT spot/preemptible.** A preemption mid-sweep wastes hours of
  sequential top-height work; the checkpoint mitigates but re-acquisition +
  restart is exactly the "wasted job" we're avoiding. Spot's ~70% discount does
  not justify the false-start risk given the priority.
- **Disk:** the engine is spill-bound. Provision generous fast NVMe/EBS
  (size from a29's measured spill volume × growth; running out mid-run = total
  loss). Over-provision — disk is cheap relative to a wasted 1-day run.

## 5. Zero-waste preflight gate (all green before the real run — no exceptions)

Run ON THE CLOUD BOX, cheap (~$30–60 total, minutes-to-hours):

1. **Build + clean-rev check** — deployed binaries stamped clean (no `-dirty`),
   contain the intended commit. (The A1/stale-combine lesson.)
2. **a(20) `--compare` byte-match** — full known-value run on the cloud instance.
   Proves the engine byte-matches on this ISA/toolchain before any real spend.
3. **Checkpoint kill/resume test** — start a mid-size run, kill it, resume, and
   confirm byte-identical continuation. Proves a crash/instance-blip costs one
   column, not the run.
4. **Calibration run of a KNOWN term (a27)** — measures the box's real cpu-s and
   scaling efficiency (not modeled), AND independently reproduces a27 →
   doubles as cross-ISA certification. This is the number that makes the a30
   cost prediction real.
5. **Disk headroom check** — confirm free space ≥ predicted spill × safety
   margin before launching.

Only after 1–5 pass does the real top-height run start. This is the "zero false
starts" gate: the expensive run never begins on an unproven box.

## 6. Cost envelope (ranged; replace with a29-calibrated numbers)

Top height on `hpc7a.96xlarge` (192 cores, ~80% eff ≈ 154 eff cores), $7.5/hr:

| a30 top-height cpu-s | cloud wall | cloud cost | vs dalby-home wall |
|---|---|---|---|
| cheap ~5M | ~9h | ~$70 | ~22h (home fine — skip cloud) |
| mid ~20M | ~36h | ~$270 | ~87h (3.6d) |
| expensive ~60M | ~108h (4.5d) | ~$810 | ~260h (11d) |

Plus ~$30–60 preflight. So the realistic a30 cloud spend is **~$100–800**,
resolved to a point estimate once a29 measures the top-height cost. If a29 shows
the cheap path, **cloud may be unnecessary** and a30 finishes at home in a couple
of days for $0.

## 7. Recommendation

1. Run a28 at home (already the plan) — it costs nothing and resolves the P11
   question + growth regime.
2. Run a29 at home if a28 shows the cheap path; measure its top-height cpu-s.
3. **Only then** decide a30: if the measured floor is ≤ ~2–3 days at home and
   that's acceptable given the ~2026-07-06 close, skip cloud entirely. If not,
   provision one on-demand ≥128-physical-core x86 box, pass the §5 gate, run the
   top height there while home does the rest, combine.

The cheapest, zero-waste path is very possibly **$0 cloud** — the staging exists
precisely so we don't spend before the numbers justify it.
