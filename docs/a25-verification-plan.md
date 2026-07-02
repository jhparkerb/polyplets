# a(25) verification plan — turnkey

**a(25) = 14,994,811,325,186,658,577** (dalby-solo run, rev `54d41fc`, `runs/ns_a25`).
Status: **computed, single-source**. This plan upgrades it to **certified**.

Already closed, verify nothing:
- **Group A** (proven closed forms): H1,2 and diagonals k=0,1,2 (H23,24,25). First-principles proofs in `docs/proofs/`.
- **Group B** (k=3–7 diagonals, H18–22): closed by the #4 desk audit
  (`scripts/audit_diagonals.py`) — over-determined blind fits, leading coeff
  `25ᵏ/k!` emergent, held-out swept points reproduced, engine coeffs match.

Three jobs remain, one per open group. **Independent, no cross-job dependency —
run in parallel, one per box.** All use existing tooling (gates checked
2026-07-01; no new code needed).

---

## Standing rules (apply to every job — do NOT deviate)
- **tmux only:** add a WINDOW to session `0` on each box (`tmux new-window -t 0: -n <name>`); never `tmux new-session`. Run **foreground + `tee`** so progress is on-screen. One session per box.
- **Completion:** after confirming the PID is alive (`ps`), start a background `tail --pid <PID> -f /dev/null` waiter (on linux: `gtail`; on the remote box use plain `tail`). Never busy-wait/poll; never `nohup`.
- **Never** `pkill`/`killall`/`pgrep`. Get PIDs from `ps`, kill by explicit number.
- **RAM per worker** = (total RAM × 0.6) / cores. Never a flat value. Values below are pre-computed.
- **gympie:** ≤10 perf cores, hard cap. **ayr:** fits 78 GB / 32 cores. **dalby:** ssh `dalby.jhpb.org`.
- These are all **>1 h jobs** → each needs an explicit user go-ahead before launch (beg-and-agree rule). Launch nothing unprompted.

---

## Job 1 — H17 sweep (closes Group C: the k=8 cell) — CRITICAL PATH
**Box: ayr** (x86/gcc — different compiler from dalby's clang). Fallback dalby (½ wall, weaker independence).

**Build** (ayr Go is too old → cross-compile orchestrate on gympie, workers native on ayr):
```
# on gympie, in ~/src/polyominoes at the run rev:
git checkout 54d41fc && mkdir -p build/ns
CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -o build/ns/orchestrate.linux-x86 ./orchestrator/cmd/orchestrate
scp build/ns/orchestrate.linux-x86 ayr:~/src/polyominoes/build/ns/orchestrate
# on ayr:
cd ~/src/polyominoes && git checkout 54d41fc && \
  make build/ns/map_worker build/ns/merge_worker        # native g++
```

**Launch** (ayr; sweeps only H17 at maxn=25, writes h17.out):
```
mkdir -p runs/ns_a25_verify/ayr/spill runs/ns_a25_verify/perheight
./build/ns/orchestrate --maxn 25 --heights 17 --counter u64 \
  --cores 30 --ram 1073741824 --unit-mult 4 --steal-grain 0.05 \
  --run-dir runs/ns_a25_verify/ayr --spill-dir runs/ns_a25_verify/ayr/spill \
  --checkpoint runs/ns_a25_verify/ayr/CKPT --checkpoint-every 900 \
  --per-height-out runs/ns_a25_verify/perheight \
  2>&1 | tee runs/ns_a25_verify/ayr/h17.log
```
**Cost:** ~366 core-h → **~19.7 h on ayr** (~10.6 h on dalby). *Cost-model estimate, not measured.*

**VERDICT:**
```
awk '/^25 /{print $2}' runs/ns_a25_verify/perheight/h17.out
```
- **PASS** iff `= 187767529262410933`.
- **FAIL** ⇒ P₈ formula is wrong ⇒ a(25) is wrong. Re-pin P₈ from this real T(25,17), re-assemble a(25).

---

## Job 2 — u128 overflow check (closes Group D-arithmetic)
**Box: dalby** (already at rev `54d41fc` with binaries from the a25 run — **no rebuild**). u128 is exact to ~a(48); if u64 didn't overflow, u128 rows are byte-identical.

**Launch** (re-sweep the stripe H3–16 at u128):
```
mkdir -p runs/ns_a25_u128/dalby/spill runs/ns_a25_u128/perheight
./build/ns/orchestrate --maxn 25 --heights 3-16 --counter u128 \
  --cores 80 --ram 1073741824 --unit-mult 4 --steal-grain 0.05 \
  --run-dir runs/ns_a25_u128/dalby --spill-dir runs/ns_a25_u128/dalby/spill \
  --checkpoint runs/ns_a25_u128/dalby/CKPT --checkpoint-every 900 \
  --per-height-out runs/ns_a25_u128/perheight \
  2>&1 | tee runs/ns_a25_u128/dalby/run.log
```
**Cost:** enumeration-bound → **~2.4 h on dalby** (≈ the u64 stripe run).

**VERDICT** (compare against the u64 rows in `results/ns_a25/swept_rows.txt`):
```
for h in $(seq 3 16); do
  diff <(cat runs/ns_a25_u128/perheight/h$h.out) \
       <(awk -v H=$h '/^===H/{on=($0=="===H"H"===")} on&&/^[0-9]/{print}' results/ns_a25/swept_rows.txt) \
    && echo "H$h OK" || echo "H$h DIFFERS <<< FAIL"
done
```
- **PASS** iff every height OK (u128 == u64). **FAIL** ⇒ u64 overflow/carry bug in the stripe.

---

## Job 3 — Redelmeier per-height (closes Group D-logic)
**Box: gympie** (ARM — bonus ISA diversity; ≤10 cores). Independent algorithm (Redelmeier generate-and-count), fully separate from the transfer-matrix `stepColumnSquare8`.

**Build:** `make build/g2`  (native on gympie).

**Launch** (target n=17 ≈1 h; all swept heights H3–16 appear by n=16, so n=17 covers them + margin. Push to 18 (~6 h) if desired). Parallelize with `--split` if wanted; single process is fine to n=16.
```
mkdir -p runs/ns_a25_verify
./build/g2 square8 17 --per-box 2>&1 | tee runs/ns_a25_verify/redelmeier_n17.txt
```
`--per-box` emits `n w h count`. **Reach ceiling n=19** (Redelmeier's limit); n=17–18 is the practical target.

**VERDICT** (aggregate over width → T(n,H), compare to swept stripe):
```
python3 scripts/verify_redelmeier.py runs/ns_a25_verify/redelmeier_n17.txt results/ns_a25/swept_rows.txt
```
- **PASS** iff every `T(n,H)` (H=3–16, n≤ceiling) matches the swept stripe.
- **FAIL** ⇒ `stepColumnSquare8` logic bug ⇒ the whole stripe AND Job 1 are invalid; **kill Job 1**, debug the engine.

---

## Sequencing & certification
```
ayr    ├──────── Job 1: H17 sweep (~20h) ────────┤   ← critical path
dalby  ├─ Job 2: u128 (~2.4h) ─┤
gympie ├─ Job 3: Redelmeier n17 (~1h) ─┤
```
- Launch all three together. **Jobs 2 & 3 are the fail-fast kill-switch:** they test the shared engine cheaply; if either FAILs, kill the 20 h Job 1 (same engine ⇒ worthless).
- **Certified when all three PASS.** Then update `results/ns_a25/RESULT.md` tier: computed→certified, and record the three verdicts.

## Pre-launch checklist (per docs/job-checklist.md)
1. Confirm each box free / within budget (`ps`, `free -h` / disk).
2. Confirm rev `54d41fc` on ayr & dalby after build; `build/g2` fresh on gympie.
3. Get explicit user go-ahead (each job >1 h).
