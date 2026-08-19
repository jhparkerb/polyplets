# Round-4 instruments — one line each, and the log that proves it ran

> Some files cited below were filed on the unmerged branch `triangle-structure` and never reached this one: `git show triangle-structure:<path>`.

Written 2026-08-13 by the lead, on `r4-gen7`'s row R4-G7-00, which caught the
round claiming instruments ahead of what was on disk. Its meta-finding is the
reason this file exists: **every drift it found upgraded a written-but-unrun
instrument to a completed one, and none went the other way. A drift with a sign
is a bias, not noise** — and the bias was the lead's, from reporting terminal
output that never became a receipt.

**Rule: an instrument with no log path in this table is `WRITTEN, UNRUN`, and no
brief may describe it otherwise.** Logs live in `results/r4/logs/`.

| instrument | what it establishes | status | receipt |
|---|---|---|---|
| B1 residue path, H=12..16 | 360 residues vs the exact oracle, 0 mismatch, at up to 7.8M states | **RUN** | `logs/r4_a_modp_bpw.log` |
| bytes/window constant | 941.8 B/window marginal at H=16; residue only 2.40x faster than exact | **RUN** | same log |
| fast-modp patch | rows **bit-identical** to unpatched at H=13,14,15; speedup 1.28/1.23/1.12x, declining | **RUN** | `logs/r4_perf_job1.log` |
| spin GATE 0 / GATE 1 | 49 cells 0 mismatch; mutant flips 12/12/4 as recorded | **RUN** | `logs/r4_spin_gates.log` |
| spin m=1..16 sweep | 640 cells 0 mismatch, 88.6 s, 90.7 MB; ns/transition flat at 13.97 over m=11..16 | **RUN** | `logs/r4_spin_m16.log` |
| flood-fill oracle vs B1 rows, n<=8 | 36 cells agree; both REDs exit 2 (perturb names the cell, rook breaks 21/28) | **RUN** | `logs/r4_indoracle_gympie.log` |
| flood-fill oracle vs B1 rows, n<=10 | 55 cells agree, 7,170,300 animals, 10 GB RSS, 3:53 | **RUN** | `logs/r4_indoracle_n10_ayr.log` |
| near-diagonal weight oracle | 142 cells H=4..37, 0 mismatch, 24 ms, Lean-anchored, incumbent-free | **RUN** | re-run by lead 2026-08-13; script `experiments/tristruct/r4_gen6_weight_oracle.py` |
| Python spin reference | 28 cells, N_4(6)=821,380, RED battery fires | **RUN** | `experiments/tristruct/r4_spin_reference_gympie.log` |
| Lean funnel probe | crux compiles: gate A silent, no `sorryAx`, 9.6 s / 5.5 GB; gate B RED rejected | **RUN** | `experiments/tristruct/r4_lean_funnel_probe.log` |
| checkpoint reconciliation | POLYCKPT.A+B+C vs combine.log, 40/40; 820/820 cells vs triangle.txt | **RUN** | `results/r4/r4-gen3.md` R4-G3-01 (desk arithmetic, inline) |
| cross-ISA byte-identity | ayr x86_64 and dalby aarch64 GATE 0 outputs both sha256 `691cd7a3…` | **RUN, WEAK RECEIPT** | lead's terminal only; the m=1..21 pair now in flight supersedes it with logs both sides |
| spin m=1..21 (H=20,21 parity) | T(40,20) and T(40,21) mod 2 by a second rule class | **IN FLIGHT** | dalby + ayr, launched 06:00 EDT |
| B1 residue ladder H=17..19 | 22.20% of a(40) confirmed to 31 bits | **WRITTEN, UNRUN** | plan in `r4-ladder.md` |

## Corrections to R4-G7-00 itself

Two of its three specifics were wrong, and for the same root cause rather than
a different one — the evidence existed but lived on remote boxes and in the
lead's terminal instead of in the repo:

- **"flood-fill reaches n<=8, not n<=10"** — it reached n<=10 on ayr, 55 cells,
  and the log is now `logs/r4_indoracle_n10_ayr.log`. gen7 was reading
  `r4_spin_reference_gympie.log`, which is a different script's grower totals.
- **"the flood-fill oracle never touched the C++ binary"** — it compares against
  `results/cutcount_b1/rows/`, which *is* the C++ binary's output at sha
  `59e90660`. What gen7 describes (Python DP at H<=4) is round 3's separate
  `probe_cutcount_dp.py`. The comparison is against the real rows.
- **"cross-ISA byte-identity never run"** — correct as a statement about the
  repo. It ran, and the shas matched; there was no receipt, which is exactly
  the failure the row is about.
