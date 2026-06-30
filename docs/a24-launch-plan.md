# a(24) launch plan (turnkey)

**Status: ready to fire — needs the >1hr beg-and-agree + machine availability.**
a(24) is the stepping stone to a(25). It uses the **current validated engine**
as-is (no new code): it injects k≤7, which is already wired. Running it now buys
three things:

1. **a(24) itself** — a certified new term (~2.2×10¹⁸).
2. **De-risks the a(25) pipeline** — exercises the multi-machine split + combine
   path that a(25) depends on, at ~⅕ the cost.
3. **Confirms the k=8 prediction** — a(24)'s swept H16 column yields **T(24,16)**,
   which must equal the falsifiable prediction **42,594,477,635,772,598**
   (results/k8-pinning.md). Match ⇒ a(25)'s k=8 injection is sound.

## What's swept vs injected (maxn=24)

Injection (existing `diagonalCell`, k≤7) contributes the closed-form heights;
the engine sweeps the rest:

| | heights | how |
|---|---|---|
| **swept** | **H3–H16** (14 heights), peak **H16** | column sweep |
| injected | H1,H2 (low); H17–H22 (k=2–7 diagonals); H23 (pole); H24 (top) | closed form |

Peak swept = **H16** (the critical path). a(24) = Σ_H T(24,H), assembled at combine.

## Engine + counter

- **Binary: the validated `next-system` build @ `f40e12b`** (combine grow-in-place
  + sigCmp + overlap + height-boundary checkpoints; **a(20) `--compare` byte-exact
  PASS**, results/perf-outcomes.md).
- **`--counter u64`** — a(24) ≈ 2.2×10¹⁸ < 2⁶⁴ (8× headroom; comfortable, unlike
  a(25)'s tight 1.2×). `CheckCounterWidth` enforces this at start.

## The split (3-box) — wall ≈ 2.4 h

H16 is the indivisible monster (can't cross machines; ~81 core-h ÷ dalby's 34.5
eff = **2.35 h floor**). Balance the rest under it. Per-height core-h ≈ a(23)
measured × g (g≈1.8): H16=81, H15=29, H14=10, H13≈4, H3–12≈3.

| Box | `--heights` | `--overlap-heights` | `--cores` | work | wall |
|---|---|---|---|---|---|
| **dalby** (34.5 eff) | `3-12,16` | `9` | ~64 | H16 + cheap tail (hidden in H16's merge gaps) | **2.35 h** |
| **ayr** (18.6 eff) | `13-15` | `3` | ~28 | the expensive mid-band, 43 core-h | **2.3 h** |
| **gympie** | — standby — | | | (a(24)'s cheap heights don't justify NAT-bridging it; reserve it for a(25)) |

Floor is H16-on-dalby. dalby & ayr land together ≈ **2.4 h**.

> **Resourcing note:** ayr is currently running the a(23) H17/H18 cross-ISA
> verify (do NOT preempt it — it's the independent certification of a(23)). So
> the 3-box split is gated on that finishing. Until then, use the **dalby-solo
> fallback** below, or wait for the watcher to report ayr free.

**Home-only fallback (no dalby):** ayr `3-15` (~3 h) — H16 on ayr is 81/18.6 =
4.4 h, so home-only is ~4.5 h. Feasible; dalby's cores earn their keep on H16.

**Simplest fallback (dalby solo):** dalby `--heights 3-16 --overlap-heights 14`
≈ **3.7 h**, one machine, no cross-machine combine. Use if coordination is a
hassle — but the 3-box run is the better a(25) de-risk (it tests the combine).

## Operational flags (per machine)

```
orchestrate --maxn 24 --counter u64 --ram 4294967296 \
  --heights <LIST> --overlap-heights <M> --cores <N> --unit-mult 4 \
  --run-dir runs/ns_a24/<HOST> --spill-dir runs/ns_a24/<HOST>/spill \
  --checkpoint runs/ns_a24/<HOST>/POLYCKPT \
  --per-height-out runs/ns_a24/perheight \
  --cost-profile-out runs/ns_a24/<HOST>/cost_profile.tsv
```

- **`--overlap-heights <M> = the count of heights that box sweeps** — overlap them
  all (RAM is a non-issue: all a(24) swept frontiers co-resident <1 GB; H16 ~0.45
  GB dominates). This is the ~18% utilization lever (results/scheduling.md).
- **Resumable now**: overlap writes height-boundary checkpoints. On a crash,
  re-launch the **same command with `--resume`** — it skips completed heights and
  re-runs only those in flight. (This is new this session; overlap used to be
  non-resumable.)
- `--unit-mult 4`, `--checkpoint-every 0` (checkpoint each boundary). Run each in
  a tmux window, foreground + `tee`, with a `tail --pid` waiter.

## Deploy (before launch)

Per the cross-compile note: build `orchestrate` on gympie
(`CGO_ENABLED=0 GOOS=linux GOARCH=amd64`) and `scp` to dalby/ayr; build
`map_worker`/`merge_worker` **native** on each linux box; native build on gympie.
All three must report `rev=f40e12b`. (Stale-binary check: a wrong rev silently
ignores the new flags — verify the rev line on each box before trusting a run.)

## Combine → a(24) + validation

1. Gather every box's `perheight/h<H>.out` into one dir.
2. Assemble a(24) = Σ_{H=1}^{24} T(24,H) (swept H3–16 + injected H1,2,17–24), as
   for a(23) in results/ns_a23 (the `combine` tool).
3. **Built-in cross-checks (the run self-validates):**
   - **T(24,16) == 42,594,477,635,772,598** ⇒ k=8 prediction confirmed → a(25)
     injection sound. (Mismatch ⇒ STOP, investigate before a(25).)
   - a(20)=Σ_H T(20,H) == **1,025,573,519,362,016** (known) — the swept rows
     reconstruct every a(n), n≤24.
   - a(21), a(22), a(23) == our records (6954084405510437 / 47255332844367680 /
     321749260511448732) — full regression against the prior run.

## Caveats

1. **g is estimated** (no a(21) cost profile) — the 2.4 h figure could move ~±50%.
   a(24)'s own cost profile **pins g**, sharpening the a(25) wall estimate (another
   reason to run it first).
2. a(24) is a **certified** term — every swept height is real, and the injected
   k≤7 diagonals are validated through a(23). No extrapolation in a(24) itself
   (unlike a(25)'s k=8, which a(24) is what makes sound).
3. The ~2.4 h is wall on the cluster; utilization ≈ 80% (the H16 endgame solo
   tail, measured at a(20)) — expected, bounded, not a problem.
4. Confirm spill headroom on each box (trivial for a(24): <1 GB frontiers).

## After a(24)

Pin P₈ from the swept T(24,16) (8 points n=17..24 + leading 25⁸/8!), wire
`diagonalCell case 8`, then a(25) injects k≤8 (peak swept **H16**, self-pinning —
see the ordering discussion). a(25) is the current Go result-pipeline ceiling
(`CheckResultWidth` caps maxn at 25); a(26)+ needs the pipeline widened.
