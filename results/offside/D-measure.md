# Offside Lane D — the three unknowns, measured

2026-08-14. Wave 2, measurement lane. Executes the queue rows from C (claim
granularity), A (writes-per-session baseline) and B (migration baseline).
Desk only; nothing executed on any box. Every number below is followed by the
command that produces it, run from `/Users/jasonp/src/polyominoes` unless the
path says otherwise. `$M` denotes
`/Users/jasonp/.claude/projects/-Users-jasonp-src-polyominoes/memory`.

---

## 0. Headline, before the tables

1. **Write cost was never the binding question.** The candidate's rows cost
   19–51 lines on a note-landing day against a measured baseline of ~3,500
   markdown lines added per active day. That is under 1.5%. What actually
   varies by a factor of six is not the cost but the *count*: the candidate
   never says what granularity a claim is, and the same note yields 3 rows or
   19 depending on a decision the design leaves to the session. Lane A's
   format has no such freedom — one landed result is one block — and produces
   1–2 blocks for the same notes.
2. **The current state is not bad, and where it is wrong it is wrong in one
   specific way.** Of the assertions I could check against the tree, the
   HANDOFF top entry scored 9 right, 0 wrong, 2 unverifiable-by-desk. Every
   error found was in the memory index, and **three of the five errors are
   dead pointers, not false statements** — files deleted out from under a
   `[[memory]]` line. TTLs do not catch those. Claim-checks do not catch
   those. A path-existence check catches all three, and one already exists
   (`scripts/check_receipts.sh`).
3. **A third finding, not asked for and decision-relevant:** the memory index
   *as injected into this session's context* does not match the memory index
   *on disk*. Section 3.4.

---

## 1. Claim granularity — the row sets, written out

The comparison the queue row asks for is same-note counts under both designs,
so both are written out in full for one note and counted for the other two.

### 1.1 What each design demands

**Candidate** (`docs/offside-design.md` §1, §2, §6): the atomic unit is a
claim — name, one-line statement, tier, and an executable check or an explicit
`check: none`. Non-executable assertions (plans, priorities, operational
state) are *bets*, with a machine stamp and a per-species TTL. A closed or
parked thread additionally owes Lock / Reopen / Converts-to (/ Price).

**Lane A** (`results/offside/A-ab-initio.md` §1): the atomic unit is a
*block*, one per landed result or status transition, appended never edited,
with fields `at: claim: receipt: harness: depends: caveat:` (plus `kill:` on
OPEN, `reopens:`/`withdraws:` on contradictions).

The two are not the same unit. The candidate's unit is **an assertion**; lane
A's is **an event**. Every count below follows from that.

### 1.2 `results/motley-h17.md` (57 lines) — written out in full

Command for the line count: `wc -l results/motley-h17.md`.

**(a) Candidate — 19 rows** (17 claims, 1 bet, 1 door row), strict reading
(every assertion that would be false if the note were wrong):

| # | row | tier | check | class |
|---|---|---|---|---|
| 1 | T(n,17) = C₁₇ − 2C₁₆ + C₁₅ matches the banked triangle at all 24 cells n=17..40, 0 mismatch | two-source | compare vs `results/triangle.txt` | re-runnable-cheap |
| 2 | a(n) closed rule-independently for all n ≤ 33 | single-source | `check: none` (interpretive consequence of 1) | receipt-only |
| 3 | binary stamp `git=4df3fec9`, no `-dirty` | measured-once | recorded stamp | receipt-only |
| 4 | binary sha256 `dd1732399703d5aa…` | measured-once | sha of the dalby binary | receipt-only |
| 5 | `gate-cutcount-b1` GREEN on this build | two-source | `make gate-cutcount-b1` | re-runnable-expensive (needs the dalby build) |
| 6 | oracle rows byte-identical to banked C rows at H=12..16 | two-source | `scripts/hm_byte_oracle.sh` | re-runnable-cheap |
| 7 | inputs C₁₅, C₁₆ are step-0 rows that reproduced the banked ladder byte-for-byte | two-source | byte compare | re-runnable-cheap |
| 8 | wall H=16 = 12,231 s | measured-once | — | receipt-only |
| 9 | wall H=17 = 39,117 s (10.9 h) | measured-once | — | receipt-only |
| 10 | wall ratio ×3.198 vs ladder constant ×3.209 | measured-once | arithmetic on 8, 9 | re-runnable-cheap |
| 11 | peak RSS 32.06 GB → 95.0 GB, ×2.963 | measured-once | — | receipt-only |
| 12 | census 7,832,667 → 23,681,423, ×3.023 | measured-once | re-run the height | re-runnable-expensive (10.9 h, 95 GB) |
| 13 | predicted 91 GB / 7–10 h; measured 95.0 GB / 10.9 h; inside the ±20% band | measured-once | arithmetic | re-runnable-cheap |
| 14 | the plan's kill condition does not fire | measured-once | arithmetic on 13 vs `docs/motley-plan.md` | re-runnable-cheap |
| 15 | engine self-checks `q0_zero=OK`, `q1eval_binomial=OK (n=1..40)`, `fits_pay` bound | two-source | in-engine, per run | re-runnable-expensive |
| 16 | those self-checks are arithmetic only, **not** connectivity checks | proved | `check: none` (a scope statement) | receipt-only |
| 17 | first launch refused by binary `b9d725be` (`limits: H<=16`); three hard-coded height caps and a latent H=18 fan-out overflow found and fixed in `4df3fec9` | measured-once | `check: none` (historical) | receipt-only |
| 18 | **bet:** H=18/H=19 RAM projections for Confetti and Ticker Tape now rest on a measured point above the banked ladder | plan | TTL: weeks | receipt-only |
| 19 | **door:** Motley rung 1 GREEN → rung 2 (Confetti) — Lock/Reopen/Converts-to | — | — | receipt-only |

Classification totals: **re-runnable-cheap 6, re-runnable-expensive 3,
receipt-only 10.** Three of the 19 carry `check: none`; two more are
receipts of a run that costs 10.9 h and 95 GB to reproduce, so their check is
nominal.

**(b) Lane A — 1 block** (2 if the engine bug is filed separately):

```
## 2026-08-14 · Motley rung 1, H=17 · CLOSED
at:       10144a5
claim:    T(n,17) = C_17 - 2C_16 + C_15 matches the banked triangle at all
          24 cells n=17..40, 0 mismatch; a(n) closed rule-independently to n<=33
receipt:  results/motley-h17.md
harness:  scripts/dalby_motley_h17.sh
depends:  docs/motley-plan.md results/motley-step0.md results/triangle.txt
caveat:   the in-engine self-checks are arithmetic only, not connectivity;
          the connectivity evidence is the external 24-cell comparison alone
```

**19 rows against 1 block for the same note.**

### 1.3 `results/coin-flip-characteristic-landscape.md` (158 lines)

**Candidate — 24 rows** at claim granularity, or **52** if each cell of the
sweep table is its own claim (the design does not say which):

- 5 theorem rows (T1–T5), all tier `proved`, all **`check: none`** — a
  formal-proof claim has no executable check by construction, and T5 carries a
  scope restriction (artinian simple quotients only) that does not fit in a
  one-line statement.
- 2 corollary rows (Coin Roll free by theorem; Biased Coin Flip's GF(2^k) buys
  probability 40/2^k and no dimensions). `check: none`.
- 4 sweep rows, H=6..9, each carrying 7 measured values (states, N, B, rank_Q,
  primes tested, T4 cutoff, the drop list). H=6,7 re-runnable-cheap; H=8,9
  **re-runnable-expensive** (2,187 states, 196 primes at H=9).
  Harness `experiments/tristruct/r3_char_landscape_certify.py`.
- 3 trend rows (char-2 share grows 22.9→54.3%; p=3 stays ≤2.6%; the T4 cutoff
  falls 44,633→849). re-runnable-cheap, arithmetic on the table.
- 1 instrument row: the certifier refuses a verdict unless consistency,
  pinning and completeness all close, and voided its own first H=6 run.
  re-runnable-cheap; this is the note's RED control.
- 5 "what this settles" rows. `check: none`; each is an interpretation of T1–T5.
- 4 scope rows ("what it does not settle": non-linear methods, a different
  functional, non-artinian R, H ≤ 9). `check: none`.

Totals: **re-runnable-cheap 6, re-runnable-expensive 2, receipt-only 16.**
**Sixteen of 24 rows are `check: none` and can never be otherwise** — this is
the strongest single-note case for B's alarm-fatigue objection, and it lands
on the most rigorous note of the three. The note is *five theorems*; the
design's central mechanism has nothing to compute about it.

**Lane A — 1 block.** Claim: "no field, ring, weighting or auxiliary object
other than characteristic 2 collapses the strip functional; the landscape is
indexed by the characteristic and p=2 is its unique minimiser." Receipt the
note, harness the certifier. But A's format allows **one** `caveat:` field and
this note has four independent scope limits. A would either concatenate them
(losing the structure the note took care to give them) or split into four
blocks. Not a fatal defect; a real one, and A did not name it.

### 1.4 `results/ridgeline-depth-amplitudes.md` (352 lines)

**Candidate — 51 rows**, counted by section:

| section | rows | note |
|---|---|---|
| §4 verification table | 13 | 13 explicit quantity/value/source triples, already in claim shape |
| §5 "Derived" | 4 | proved-modulo-assumptions |
| §5 "Assumed, with the evidence named" | 4 | **no species fits these** — see below |
| §5 "Verified, not derived" | 2 | tier `measured-once` with an explicit bias envelope |
| §5 "Open" | 3 | bets |
| §5 "Weak points, conceded up front" | 3 | `check: none` |
| §6 "What this supersedes" | 4 | each retires or refines a claim in another note |
| headline + §2/§3 constants (α=50/81, 35/8, Σ=450, C₁, exponent −1/2, the 14/27 trap, the 378/438/450 controls) | 11 | mixed |
| §3/§5 cost timings (7 measured (K,emax) points) | 7 | receipt-only |

Classification: **re-runnable-cheap 21** (`ridgeline_master.py` and
`ridgeline_vertex.py` are seconds; §4's first three rows and the Σ controls
are all in this class), **re-runnable-expensive 6** (`ridgeline_scaling.py 60
1` is 395 s uncached, `(11,3)` is 290 s, and the emax=4 cases do not
terminate), **receipt-only 24**.

**The representational gap, which is the real finding here.** §5's four
*assumptions* — the exponent stays −1/2 under small t, Y_c(t) analytic at 0,
the ρ-cancellation persists at every order, the flat zero-momentum projection
behind α = Σ/729 — are not claims (no check exists or can exist), not bets
(they do not expire; they are load-bearing indefinitely, and re-stamping them
means *proving* them), and not doors. **The candidate has no species for a
standing conditional caveat**, which is exactly what the note itself says the
weight sits on. Lane A has the `caveat:` field but one slot for four items.
Neither design represents this note's most important content; the note's own
plain-markdown limits ledger does it better than either.

### 1.5 Same-note comparison, the number the row asked for

| note | lines | candidate rows (strict) | candidate rows (headline only) | lane A blocks |
|---|---|---|---|---|
| `motley-h17.md` | 57 | 19 | 3 | 1–2 |
| `coin-flip-characteristic-landscape.md` | 158 | 24 (52 at cell level) | 7 | 1 |
| `ridgeline-depth-amplitudes.md` | 352 | 51 | 12 | 1 |
| **total** | 567 | **94** | **22** | **3–4** |

Aggregate classification across all 94: **re-runnable-cheap 33,
re-runnable-expensive 11, receipt-only 50.** Just over half of everything the
candidate would file has no check and never will.

The strict/headline spread is a factor of 4.3. That spread is not noise, it is
the design's unstated parameter, and it is larger than any cost difference
between the two designs. B counted 20–25 writes by hand-enumerating one
HANDOFF entry and conceded the count was one reader's enumeration; my strict
counts run at 0.30–0.33 rows per line of note, against B's 0.43 per line of
HANDOFF entry. Two independent enumerations landing within 30% of each other
is the closest thing to corroboration this quantity has.

---

## 2. Writes-per-session baseline — what the current system already costs

```
git log master --since=2026-07-31 --until=2026-08-15 --no-merges \
  --date=short --pretty='C %ad' --numstat | awk '...'      # per-day rollup
ls -lT $M | awk 'NF>8{print $6" "$7}' | sort | uniq -c     # memory writes
```

Nine active days out of fourteen calendar days. 2026-08-03..05 and 08-11..12
carry zero commits (the pattern is Tue/Wed off, plus 08-03).

| day | dow | commits | files | md files | md lines+ | HANDOFF+ | HANDOFF commits | results/*.md + | memory writes |
|---|---|---|---|---|---|---|---|---|---|
| 08-01 | Sat | 42 | 91 | 48 | 1,982 | 133 | 5 | 737 | 3 |
| 08-02 | Sun | 5 | 6 | 3 | 69 | 55 | 1 | 13 | 2 |
| 08-06 | Thu | 40 | 290 | 89 | 8,027 | 83 | 5 | 5,412 | 0 |
| 08-07 | Fri | 55 | 285 | 88 | 6,747 | 105 | 5 | 1,912 | 17 |
| 08-08 | Sat | 9 | 66 | 22 | 15,165 | 9 | 2 | 0 | 5 |
| 08-09 | Sun | 33 | 134 | 35 | 3,497 | 1 | 1 | 1,962 | 9 |
| 08-10 | Mon | 31 | 76 | 20 | 573 | 0 | 0 | 169 | 2 |
| 08-13 | Thu | 14 | 295 | 86 | 12,913 | 105 | 2 | 7,964 | 4 |
| 08-14 | Fri | 13 | 49 | 24 | 1,985 | 167 | 5 | 634 | 10 |
| **total** | | **242** | **1,292** | **415** | **50,958** | **658** | **26** | **18,803** | **52** |
| **median** | | **31** | **91** | **35** | **3,497** | **83** | **2** | **737** | **4** |

Two of the md-line figures are machine-generated dumps and should be excluded
before the number is quoted: `paper/L-novel-ngrams.md` (11,490 lines on 08-08)
and `experiments/tristruct/sweep_report.md` (2,636 lines on 08-13). Adjusted
totals: 36,832 md lines, median unchanged at 3,497.

```
for d in 2026-08-08 2026-08-13; do git log master --since="$d 00:00" \
  --until="$d 23:59" --no-merges --pretty='' --numstat | \
  awk 'NF==3 && $3 ~ /\.md$/ && $1!="-"{a[$3]+=$1} END{for(f in a) print a[f],f}' | sort -rn | head; done
```

**The current daily write cost, stated plainly.** A median active day is 31
commits touching 91 files, of which 35 are markdown, adding ~3,500 lines of
markdown — ~740 of them into `results/*.md`, ~83 into `HANDOFF.md` across 2
commits, plus 4 memory files rewritten. `HANDOFF.md` grew by a net 597 lines
over the fortnight (658 added, 61 deleted) and now stands at 1,150 lines:

```
git log master --since=2026-07-31 --until=2026-08-15 --no-merges \
  --pretty='' --numstat -- HANDOFF.md | awk '{a+=$1;d+=$2} END{print a,d,a-d}'
```

**The denominator, applied.** The candidate's 19–51 rows for a note-landing
day are one line each. Against a median 3,497 markdown lines per active day,
that is 0.5–1.5%. Against the 83 lines that already go into `HANDOFF.md`
daily, it is comparable or larger — so on the *narrow* comparison (state layer
vs state layer) the candidate roughly doubles to halves the current cost
depending on granularity, and on the *broad* comparison (state writes vs all
writes) it is noise.

Caveats on this measurement, up front: memory-write counts come from mtimes
and are lower bounds (a file rewritten on two days shows only the later); the
memory directory is not versioned, so nothing finer is recoverable; and 08-13
is a merge-day outlier (295 files, 43 distinct `results/*.md`) that inflates
the totals but not the medians.

---

## 3. Migration baseline — how wrong is the current state

Method: (i) mechanical resolution of every path token in `MEMORY.md`;
(ii) grep-verification of every headline constant against `results/` and
`docs/`; (iii) reading fourteen substantive status assertions against their
primary docs; (iv) the same for the HANDOFF top entry.

```
grep -oE '[A-Za-z0-9_./-]+\.(md|py|sh|tex|txt)' $M/MEMORY.md | sort -u | \
  while read p; do [ -e "$p" ] || [ -e "$M/$p" ] || echo "ABSENT $p"; done
```

By my definition — a line is status-bearing if it asserts a state of the work,
a result value, or the location of an artifact — **62 of `MEMORY.md`'s 103
index lines are status-bearing** (`grep -c '^- ' $M/MEMORY.md`); the rest are
practice, voice and standing bans, which have no primary doc to check against.

### 3.1 Wrong — 5, listed explicitly

**W1. `MEMORY.md:50` — `scripts/dalby_holes_perheight.sh` does not exist.**
Deleted in `91bdcdc` ("next-system: branch for v2 build + aggressive
research-corpus cleanup"). `docs/perimeter-defect-plan.md` still points at it
too, so the repo carries the same dead pointer.
`git log --all --oneline --name-only -- '*holes_perheight*'`

**W2. `MEMORY.md:119` — "designs/08,09" resolves to nothing.** The real path
was `docs/next-system/designs/08-straggler-tail-sizing.md` and
`09-cost-model-and-work-assignment.md`, both deleted in `78602f8` ("the big
tidy", 2026-07-06). The memory *body* also cites `designs/06` and `designs/09`
inline. Dead for five and a half weeks.

**W3. `MEMORY.md:120` — "designs/10"** — same deletion, same commit.
`git log --oneline -1 --diff-filter=D -- docs/next-system/designs/09-cost-model-and-work-assignment.md`

**W4. `MEMORY.md:60` — "observability.md implemented across scripts +
engines"** is an overclaim. `obs.py` (409 lines) is imported by two project
files (`experiments/tristruct/exactchange_kernel_probe.py`,
`sampling/maxhole_split.py`) plus a `Makefile` reference; `scripts/*.sh`
reference it zero times, and no C++ engine does.
`grep -rln "obs\.py\|import obs\|from obs " --include=*.py --include=*.sh --include=Makefile . | grep -v worktrees`

**W5. `MEMORY.md:76` — "remaining: report placeholders + publish prep"** is
stale by twelve days. `HANDOFF.md:1144` records "the two
`technical-report.tex` placeholders are now filled — a(40) is literal in both
the abstract and `tab:an`, and `verify_technical_report.py` reports 781
checks, 0 failures", and `grep -n "5.7e31" paper/technical-report.tex` is
empty.

A sixth error, on the primary-doc side rather than the memory side, is worth
recording because of *when* it happened:

**W6. `docs/middle-kingdom-plan.md:4-9` still reads "Phases 0, 1, 2 and 3 all
DONE 2026-08-05, uncommitted … Phase 4 is what remains."** All four cited
results notes are tracked, `docs/middle-kingdom-followups-plan.md:10` says
"The campaign itself is closed", and `MEMORY.md:108` was corrected on
2026-08-14 to "COMPLETE, all 5 phases committed". The 2026-08-14 repair fixed
the memory line and left the primary doc it points at asserting the opposite.
This is the failure the candidate's rendered views are designed to make
impossible, occurring inside the very repair the design cites as its
motivating incident.

### 3.2 Unverifiable — 5

- **U1. `MEMORY.md:126`, Notary "δ in flight".** `grep -in notary HANDOFF.md`
  returns nothing at all; the only results note is
  `results/notary-depth1-lean.md`; `docs/notary-k-plan.md:176` says the full
  δ chain was "settled 2026-08-10, stage-1 generator data in
  `build/notary_kdelta_data.json`, verified". Whether δ is running, done or
  abandoned cannot be determined from the tree. A four-day-old operational
  assertion with no receipt — exactly the species the candidate's TTLs target,
  and the only one of the 62 lines where a TTL would have fired usefully.
- **U2. `MEMORY.md:19`, L-readability campaign "RUNNING".** Last artifact
  `docs/reviews/llm-tics/round2-L2.md`, 2026-08-08. Separately, the primary
  doc `docs/reviews/llm-tics/PLAN.md` carries a hard proscription — no Fable
  model may be used on this project without jasonp's approval — which the
  memory line does not record. A governing caveat present in the primary doc
  and absent from the index line that routes to it, which is Li et al.'s
  failure mode in miniature.
- **U3. `MEMORY.md:61`,** "../oeis adopts observability.md wholesale" — a
  sibling repo, not checked (no filesystem-wide scan).
- **U4/U5. HANDOFF top entry:** "ayr unreachable since ~23:00 UTC" and
  "Confetti H=18 still running on dalby". Desk-only lane; not checkable here.
- **U6. `MEMORY.md:83`,** "OEIS batch staged" — "staged" has no in-tree
  definition and no staging manifest was found; two plan docs reference
  staged b-files.

### 3.3 Right — everything else I checked

Every path token in `MEMORY.md` other than W1–W3 resolves (`ROADMAP.md` and
`technical-report.tex` are named as deleted/elsewhere and both statements are
correct: `git show --name-only 78602f8 | grep ROADMAP` confirms the deletion,
and `paper/technical-report.tex` exists).

Fifteen headline constants grepped, fifteen corroborated:
T(40,21)=2.84% (`results/triangle-r2-extension-scout.md:253`, 2.8431%);
keys 135 GB (`docs/motley-plan.md:268`); tmpfs 4.6× to a34, OOM at a35
(`results/beyond-polyplets.md:167`); b=1.7266 (`results/rook1/INSTRUMENTS.md:25`);
strip coverage 72.2% (`results/strip-engine.md:108`); utilization 19.8%
(`results/beyond-polyplets.md:172`); 6.543 ≤ λ ≤ 9.3154
(`results/strip-mu-certificates.md:283` — 9.3154, not rounded back);
μ₂=42.39460 (`results/slope-growth-saddle.md:56`);
a = 3293/92928 − 3251√3/185856 (`results/onset-defect-depth1-closed.md:21`);
3+2√2 (`results/directed-king-animals.md:11`); c₂₁=3 predicted
(`results/converse-sweep.md:74`); A034299's 3643 and the H=13 pricing
(`results/exactchange-probes.md:240`); α=50/81 and j=5 → 35/8
(`results/ridgeline-depth-amplitudes.md`); `TestKinkResumeMidColumn`
(`orchestrator/kink_resume_midcolumn_test.go`); `build/g2` present.

Substantive statuses verified right: anisotropic novelty closed 2026-08-01
across three databases with no collision
(`results/anisotropic-not-dfinite.md:296,314,342`); Outworks still not pushed
(`git log --oneline origin/master..master | wc -l` → **121**); Middle Kingdom
complete and committed (all four notes tracked; see W6 for the contradiction
in its own plan doc); Exact Change H=13 priced and unlaunched.

**HANDOFF top entry — 9 right, 0 wrong, 2 unverifiable.** Verified: the five
new/modified paths exist with the stated tracked/untracked status; the 10.5
kill line is real (`docs/king-twigs-plan.md:104`); the 65%-of-n=8 re-entrant
figure is in `results/king-twigs-l1.md:21`; the birthright checker carries
five named RED controls (`experiments/birthright_identity_check.py:121-124`);
`probe_cutcount_dp.py` is indeed gone from the tree (present only in history,
`7b13137`); the Exact Change ranks 453/912/1818 and the 1696 s H=12 wall are
at `results/exactchange-probes.md:231-233`; C₁ to 2.5e−12 matches the note's
2.46e−12; and **"everything from this set is uncommitted" is exactly right** —
`git status --short` shows all eleven paths modified or untracked. The two
unverifiable ones are both operational (U4/U5).

### 3.4 The finding nobody asked for

`MEMORY.md` on disk and `MEMORY.md` as auto-injected into this session's
context **do not match**. The injected copy carries the pre-repair text of the
three 2026-08-14 incidents:

| line | injected into context | on disk now |
|---|---|---|
| 101 anisotropic | "novelty vs literature UNCHECKED" | "novelty check CLOSED 2026-08-01, no collision" |
| 108 middle kingdom | "Phases 0-2 DONE uncommitted, Phase 3 next" | "COMPLETE, all 5 phases committed" |
| 110 severance W4 | "CLOSED negative … amplitude family fit-unresolvable" | "amplitude family DERIVED (Ridgeline): α=50/81, j=5 is 35/8" |
| 106 king twigs | *absent* | present |

The same session also received a `gitStatus` block listing two modified paths
where `git status --short` reports twenty. I record the second as a single
observation rather than a measurement — I did not establish when the snapshot
was taken — but the `MEMORY.md` divergence is direct: the file was repaired,
and every lane of this panel, including A, B and C, has been reasoning from
the unrepaired text and quoting those three entries as live incidents.

The consequence for the adoption decision is sharp and neither the candidate
nor lane A addresses it. **Repairing a state file does not repair the state
already loaded into the sessions reading it.** A rendered view (candidate §3)
is rendered at `make state` time and read into a context that then persists
for hours; a git-freshness mark (A §3) is computed at gate time and likewise
frozen on read. Both designs assume the session re-reads. This session did
not, and could not have known to.

---

## 4. Bottom line

**Is the candidate's write cost affordable?** Yes, and the question was mis-framed.
19–51 one-line rows against a median 3,497 markdown lines added per active day
is 0.5–1.5% of the day's writing, and most of those rows describe work the
session was documenting anyway. Nothing in the measurement supports "the
candidate is too expensive to write." What the measurement does show is that
**the candidate does not determine its own cost**: 3 rows or 19 for the same
note, a 4.3× spread across the three notes, decided by a session with no rule
to follow. That is not a cost problem, it is a specification hole, and it is
the one thing in §1 that must be closed before adoption — a rule as crude as
"one claim per bolded verdict in the note" would close it and would land the
counts at the headline column.

Two structural findings against the candidate come out of §1 and should
outweigh the cost argument in either direction. **Fifty of 94 rows are
receipt-only and just over half carry `check: none`** — on the
characteristic-landscape note, sixteen of twenty-four, because the note is
five theorems and there is nothing for a checker to compute. B predicted
alarm fatigue from a third; the measured share is higher. And the
**ridgeline note's four standing assumptions fit no species in the design** —
not claims, not bets, not doors — while being, by the note's own statement,
where the weight sits.

**Is the current state bad enough to justify replacement?** On this evidence,
no — not the whole state layer. The hand-written HANDOFF top entry scored 9/9
on everything checkable, including the assertion most likely to rot ("all
eleven paths uncommitted"). All five errors are in the memory index, which is
precisely B's item-7 territory, and B's recommendation — land item 7 alone,
hold 1–6 — is corroborated rather than contradicted by the count.

But the *shape* of the errors argues for a mechanism neither B nor the
candidate proposed. **Three of the five are dead pointers**: files deleted in
`78602f8` and `91bdcdc`, weeks and months ago, still named by index lines that
route sessions to them. A TTL would not have caught them (the *claims* are
still true — those design docs did say what memory says they said). A claim
suite would not have caught them (there is nothing to run). What catches all
three, in one command, is path existence — which `scripts/check_receipts.sh`
already implements with three planted mutants, and which lane A's `receipt:`
field is built on and the candidate's design has no equivalent of. **The
cheapest correct intervention available is: memory carries no status (item 7),
plus every memory pointer's path must resolve.** That is one evening and it
closes 5 of the 5 errors measured — three by path check, two (W4, W5) by the
no-status rule.

W6 is the counterweight and should be read before anyone concludes the
current system is fine. The 2026-08-14 repair pass fixed a memory line and
left the primary doc it points at asserting the opposite, on the same day, in
the same thread. Hand repair does not propagate. That is the honest case for
*some* rendering, even if not this one.

---

## 5. Queue rows appended

Two rows, in `results/offside/queue.md`. The first is the one measurement in
this file I could not take and which changes the adoption decision; the second
is the mechanism §4 argues for, which no lane has priced.
