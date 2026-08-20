# Undertow review — Lane A: circularity audit

2026-08-20 07:35 EDT, branch `lastditch`. Adversarial audit per
`docs/undertow-review-brief.md` §3 Lane A. Findings filed first to
`results/undertow-review-queue.md` (blind append; no other lane's output read).

Core question: **is any Undertow number derived, directly or transitively,
from a value that depends on it?**

Short answer: **no Undertow number is circular.** But two of the four claims
count by-construction matches as checks, and the four-term reassembly table's
"short sweep" framing is circular *as an independence claim* for three of its
four rows. Grades below.

## The one fact that reprices most of the checks

`results/ns_a40/PROVENANCE.md` ("Real sweeps H3-H21; H22-H40 via wired P_k
closed forms"): the banked triangle's H >= 22 cells are **not enumerations** —
they are `diagCoeffTable` evaluations written into `h22.out..h40.out` by the
run itself. Verified numerically: all 171 in-onset banked cells at H >= 22
equal the wired-law evaluation exactly, 0 differ (script re-deriving
`slope2_law_vs_truth.law` against `read_tri`). And `extract_ab` →
`grand_form` (`experiments/undertow_pin.py:132-160`) is an exact inverse pair,
so any tower whose levels k <= 19 come from `extract_ab(read_pk())` evaluates
to **identically** the same polynomial the run injected. Every "does the tower
reproduce the banked cell?" comparison at H >= 22 is therefore
formula-vs-formula: guaranteed to pass, worth only "Python and Go evaluate the
same polynomial the same way."

Two further by-construction identities at the frontier levels:

- `P_19` was fit from `T(39,20)` and `T(40,21)` (comment at its
  `orchestrator/sweep.go` diagCoeffTable entry; `results/ns_a40/PROVENANCE.md`
  "P_19 being the formula fitted to that very cell"). Two constants, two
  cells, exact rational fit: the wired evaluation reproduces both anchors
  identically. Any check that scores those two cells against wired `P_19` is
  scoring a fit against its own fitting data.
- Same for `P_18` at `T(37,19)`, `T(38,20)`. Levels j <= 17 are better off:
  j = 1,2 are proven, and 3..17 carry independent holdout certifications
  (table comments; the P_0..P_18 holdout mass-cert in ns_a40/PROVENANCE.md
  covers 18 via `T(39,21)`).

## Claim 1 — rule-independence for n <= 39, gap = T(40,19)

**Grade: CLEAN.** (`experiments/undertow_ri.py`)

Traced every input to ground:

- **Motley triangle**: `undertow_pin.py:44-70 read_tri_motley` reads only
  `results/cutcount_b1/rows/C*.out` (different connectivity rule, proved
  telescope `docs/proofs/cutcount-identity.md`). 720 cells, H <= 18; I
  re-verified all 720 agree with the incumbent (0 differ) — that agreement is
  the *known* part, and it is a target, not an input.
- **Levels 1..9**: `undertow_ri.py:44-58 abinitio_levels` reads
  `results/severance_w1_weights_k9.txt` through
  `severance_w1_assemble.load_weights/assemble_R/pk_from_R`. That file was
  written by `cpp/severance_w1.cpp` (independent cluster enumerator),
  cross-validated by the pure-Python `cluster_weight_dp.py`. No wired-table or
  triangle read on this path (`severance_w1_assemble.py` imports
  `read_pk/read_tri` at module level but calls them only in its own
  `main`, lines 247-248).
- **D_j**: `undertow_pin.load_depths` → `depth1_gap_walk.walk_families/
  series_D1` (pure DP, no file reads) and `severance_w3_depths.D_series`
  (pure DP, or the cached `results/severance_w3_families_K*.txt` tables from
  `cpp/severance_w3_families.cpp` — cluster weights, no sweep input; headers
  checked).
- **Levels 10..20**: `undertow_ri.py:81-95 build_tower` pins from `mtri` only,
  every cell H <= 18, `forbid_row` excluding the answered row from its own
  pinning set — the value-used-as-input-and-target trap is explicitly avoided
  here, and I confirmed the code does what the prose says.
- **Comparison targets only**: `read_tri()` (incumbent) and
  `known_a()` (b-file) appear solely on the right-hand side of comparisons
  (`undertow_ri.py:116-131`).

Reproduced the run (1.1 s): rows 30..39 COMPLETE/sum MATCHES, row 40 GAP [19],
and additionally rows 19..29 COMPLETE/sum MATCHES (undertow.md only shows
30..40; the claim "every n <= 39" holds for 19..39 as run).

Two caveats, neither circularity:

- **Rows <= 18 crash the script** (`undertow_ri.py:139`, `min()` on an empty
  tower band): the pure-Motley rows are claimed but not attestable by the
  script as written. Mathematically they reduce to the 720-cell Motley
  agreement, which I re-verified, so the claim survives; the attestation gap
  is a bug. (Queue row S-A3.)
- In the RI tower, level 20 pins from a **single** Motley pair
  `(37,17),(38,18)` (j = 3,4 — j = 2's cell `(39,19)` is above hmax 18), so
  the RI values of `T(39,19)` and `T(40,20)` rest on a 0-independent-check
  level plus `D_2(20)/D_1(20)` extrapolated past their validated k <= 19
  range. They agree with the incumbent — a real two-construction agreement —
  but the internal redundancy at that level is zero, same shape as the a(41)
  level-21 weakness.

## Claim 2 — "342 banked cells re-derived from strictly shorter cells, 0 wrong"

**Grade: WEAKER-THAN-STATED.** (`undertow_pin.py:318-357 audit`)

Ran it (both jmax 3 and 4): AUDIT GREEN, 342/0, reproduced. But:

- **153 of the 342 are the injected formula cells** (H >= 22; split verified:
  189 enumerated H <= 21, 153 injected, per level `min(40,k+21)` cuts the
  diagonal). For those 153, once the re-pinned `(a_k,b_k)` equal the wired
  ones — which is what `--verify` already established — the match is an
  identity. Honest headline: **189 enumerated cells re-derived, 0 wrong**,
  plus 153 evaluator-consistency checks worth one line, not 153.
- **"Strictly shorter" is per-level, not transitive.** `audit` takes lower
  levels from the wired table (`undertow_pin.py:330 extract_ab(P, max(P))`),
  not from short-cell pins. Wired `P_18` embeds `T(38,20)` (height 20), so
  the audit's prediction of `T(39,20)` (height 20) uses an equal-height cell
  transitively; in general the shortest predicted cell at level k (height
  k+1) transitively uses level k-1's anchor at the same height. Never the
  same cell — no circularity — but the claim as worded overstates. The
  transitively-clean version of this statement is `undertow_ri.py`'s tower
  (everything re-pinned from H <= 18), which is what Claim 1 runs.
- What the audit **is** worth: the 189 real cells include `T(39,20)` and
  `T(40,21)` predicted from H <= 18 (jmax 4: H <= 17) pins — the first and
  only independent cross-check wired `P_19` has ever had (every earlier level
  got a holdout; 18 and 19 hadn't). That is genuine and is the strongest
  single result in the file.

## Claim 3 — a(40)/a(39)/a(38)/a(37) reassembled from short sweeps

**Grade: WEAKER-THAN-STATED; for a(39)/a(38)/a(37), CIRCULAR as an
independence claim** (fine as a pipeline smoke test).
(`experiments/undertow_a41.py`, undertow.md "Four terms reassembled…" and
"The dry run".)

The deciding arithmetic: `undertow_a41.py:186 kmax_new = n - (hcap+1)`. Only
the a(40) row (hcap 19 → kmax_new 20) pins any level at all. For a(39) and
a(38), kmax_new = 19 = max(P); for a(37), 18. `build()`'s pin loop
(`undertow_a41.py:118 range(max(P)+1, kmax_new+1)`) is empty: **those three
reassemblies contain no Undertow content whatsoever** — they are the wired
table plus banked short sweeps plus D_j, i.e. a replay of the classical
assembly those terms already had.

Worse for the framing: each of those rows claims "swept heights <= hcap"
while consuming wired constants fitted to cells **above** hcap:

- a(39), hcap 19: `T(39,20)` — the exact cell the run claims not to need — is
  `P_19`'s own fit datum and re-enters through the wired table. The H = 20
  value in the reassembly *is* the swept `T(39,20)`, laundered through a
  two-parameter exact fit.
- a(38)/a(37), hcap 18: wired `P_18` (fit: H = 19, 20) and `P_19` (H = 20,
  21) both above the cap. The `hmax` guard (`undertow_pin.py:169 all_pairs`)
  only constrains *newly pinned* levels; undertow.md's sentence "a run that
  says 'heights <= H' refuses to touch a taller cell anywhere" is not true of
  the wired levels.

The a(40) dry run is the real row. Its content decomposes as: heights 1-19
banked sweep (input) + `T(40,20)` predicted from a level-20 pin whose cells
are all H <= 19 (**1 real, novel check — the pipeline's actual evidence**) +
`T(40,21)` = P_19 fit anchor (identity) + H >= 22 injected formulas
(identities) + total re-sums to a(40) (implied by the above). "a(40) comes
out of heights 1–19 alone" is therefore not what the script demonstrates —
it demonstrates it **modulo the wired table**. The statement becomes true
when composed with `--verify` (every wired level re-derived exactly from
H <= 19 cells + ab-initio D_j; ran it, VERIFY GREEN, 0.2 s), but that
composition spans two script invocations and no single gate enforces it.
undertow.md's own dry-run paragraph concedes the assembly/regression overlap
but does not concede the wired-table dependency of the headline.

Also: in the dry run, `sweep_agrees_with_banked` compares
`results/ns_a40/perheight` **against itself** (`read_tri` reads the same
directory) — the "760 cells agree" line is file-vs-itself there. Vacuous but
harmless; the same check in the real a41 run is real (below).

## Claim 4 — a(41) = 393811462683918679824582849262105

**Grade: CLEAN on circularity.** (`experiments/undertow_a41.py`,
`results/a41/PROVENANCE.md`)

No component of a(41) depends on anything derived from a(41):

- Heights 1..19: real sweep at Nmax 41. Injection impossible at those heights
  (`orchestrator/sweep.go:2320-2325 diagonalStripEnabled`: injection is
  per-strip H = Maxn-k, k <= 19 → H >= 22 at Maxn 41), so all n = 41 cells
  are enumerated. The 760-cell regression is real-vs-real across Nmax 40/41
  (re-verified independently: 779 cells in `results/a41/h*.out`, 760 shared
  with the banked triangle, 0 disagree, 19 new n = 41 cells). Caveat on its
  *meaning*: same engine, same rule — it catches Nmax-bump and dispatch
  regressions, not rule or engine-family errors. It is a consistency check,
  not an independent source, and nobody claimed otherwise.
- Heights 20..41: tower. Pinning cells are banked n <= 40 cells only
  (`build(..., forbid_row=41)` — moot, since no n = 41 cell is in `tri`, but
  fail-closed). Level 20: 3 pairs, 2 independent checks, all H <= 19. Level
  21: single pair `(40,19),(39,18)`, **0 independent checks**, and its
  `D_3(21)/D_4(21)` (pin) and `D_2(21)` (the `T(41,20)` cell) sit past W3's
  validated k <= 19 — extrapolation of an exact derivation, but extrapolation.
  `results/a41/PROVENANCE.md` states exactly this, names the two runs that
  would fix it, and downgrades the term to "computed-and-checked, not
  validated" — the honesty is already in the file. One addition from this
  audit: the k = 20..22 rows of `results/severance_w3_families_K22_e*.txt`
  rest on the C++ enumerator alone (Python cross-checks stop at K = 19), so
  the extrapolation has a software leg as well as a mathematical one
  (queue row S-A4).
- Discounts that carry over: the quoted "row-40 regression: 21 cells" is 1
  real check (T(40,20)) + 1 fit-anchor identity + 19 injected-formula
  identities, per Claim 3. The growth-ratio check is soft and the PROVENANCE
  treats it as such.

## Checks that are real and passed (so this lane says so)

- `--verify` (ran, GREEN): 18 wired levels' constants re-derived **exactly**
  from below-onset enumerated cells + ab-initio D_j. This is the claim's
  whole content and it is genuine — the below-onset cells are real sweeps
  (H <= 19), the comparison targets (wired constants) were fitted from the
  tall real sweeps, and D_j owes nothing to either. Multiplicity note: "N
  depth pairs" counts pairs sharing cells; a level with c cells carries c-2
  independent checks (~2/level, ~36 at jmax 4, not 100). Conclusion stands.
- `--selftest` (ran, all 3 RED controls fire): perturbed D_j breaks the pin,
  duplicate equation refused, corrupted lower level breaks the pin.
- `extract_ab`'s linearity assertion (`undertow_pin.py:150-155`) is a real
  fail-closed structural check on every wired level.
- The Motley 720-cell agreement and the a41 760-cell cross-Nmax regression,
  re-counted independently: both exact.

## Verdict table

| # | Claim | Grade | Decided by |
|---|---|---|---|
| 1 | a(n) rule-independent, n <= 39; row-40 gap = T(40,19) | CLEAN (attestation bug for n <= 18) | undertow_ri.py:44-95, 116-131; read_tri_motley; ran rows 19-40 |
| 2 | 342 cells re-derived from strictly shorter cells | WEAKER-THAN-STATED: 189 enumerated + 153 injected; "strictly shorter" not transitive | ns_a40/PROVENANCE.md ("H22-H40 via wired P_k"); undertow_pin.py:330; verified split |
| 3 | a(37)..a(40) reassembled from short sweeps | a(40): WEAKER-THAN-STATED (true only composed with --verify). a(37)-a(39): no Undertow content; height-cap claim circular through wired anchors | undertow_a41.py:186 (kmax_new), :118 (empty pin loop); sweep.go P_18/P_19 fit comments |
| 4 | a(41) | CLEAN on circularity; weaknesses correctly self-stated; check multiplicities inflated | undertow_a41.py build/forbid_row; sweep.go:2320; a41/PROVENANCE.md "one weak point" |

Everything run by this lane was seconds-scale foreground Python on banked
files (longest single run 1.2 s); no jobs dispatched, nothing on gympie
beyond reading and arithmetic. Successor queue rows S-A1..S-A4 filed.

## §S-A4 — the software leg of the K=22 family tables (closed 2026-08-20)

Question from the lead: the D_j consumed at k = 20, 21 come from the k = 20..22
rows of `results/severance_w3_families_K22_e*.txt`, which rested on
`cpp/severance_w3_families.cpp` alone (Python cross-checks stopped at
(K, emax) = (9,3), (19,1), (19,2)). How far can the pure-Python path be pushed
to overlap them, and does it agree?

All runs foreground on banked files, `_load_table` monkeypatched out to force
the Python DP; timing ladder measured first (K = 9/12/15 at emax 2: 2.6 / 9.5
/ 25.9 s, ~1.4x per unit K) before committing to the big one.

### emax <= 2: the C++ table is confirmed over its entire range

`families(22, 2)` in pure Python: **150.2 s**. Against
`results/severance_w3_families_K22_e2.txt`: **207 cells compared (e <= 2,
k <= 22, all three weight kinds), 0 mismatch** — including all nine (e,k)
cells at k = 20, 21, 22. The e <= 1 rows double as a check of the `_e1` table
(a type of final excess <= 1 never passes through higher excess, so the
emax cap cannot affect those cells; and the derived D_2 below agrees with the
C++ `_e1`-table path, which closes the loop empirically).

### D_2 and D_3 at k = 20, 21: independently derived, identical

`D_series(2, 22)` and `D_series(3, 22)` computed twice — once from the Python
families, once (fresh cache) from the C++ tables: **identical at every
k <= 22**. In particular

    D_2(20), D_3(20), D_2(21), D_3(21)  — all now two-source.

Consequences for a(41)'s weakest joint:

- **Level 20 is now fully grounded on two-source D.** Its three agreeing
  pairs include the D_4-free pair (2,3), which alone determines the same
  constants — so nothing at level 20 depends on single-source input anymore.
- **`D_2(21)` — the defect inside `T(41,20)` itself — is confirmed outright.**
  Lane B's mod-3^23 integrality argument was the only check it had; it now
  has a full independent derivation (and the value matches the one Lane B
  quotes, denominator 3^23 and all).
- **Level 21's pin still consumes `D_4(21)`** (its only pair is depths (3,4)),
  and D_4 needs e = 3.

### emax = 3: pushed from k <= 9 to k <= 12; the residual named exactly

Python e3 runs, each against `K22_e3`: K = 10 (62.5 s), 11 (105.5 s), 12
(169.3 s) — **52 cells at K = 12, 0 mismatch**. Scaling ~1.6x per unit K puts
Python K = 22 e3 at roughly 3-4 h plus the RAM growth that killed the K = 19
attempt at 1.5 GB — not foreground; a job request if wanted, but see below
for why it buys less than it appears to.

Collateral re-verified: `K19_e3` vs `K22_e3` overlap (different C++ runs,
different span caps 42/47): 228 cells, 0 mismatch.

What actually remains single-source: `severance_w3_gate.py` already validates
D_4 functionally against 16+ banked cells at k <= 19, which exercises the
e = 3 family cells at k <= 19 in combination. So the unvalidated surface is
precisely the **e = 3 rows at k = 20, 21, 22 of `K22_e3`** — nine numbers
from one C++ run, no dual-run overlap (K19_e3 stops at 19), no Python check,
no gate coverage — of which the k = 20, 21 cells feed `D_4(21)` and hence
level 21's single pin pair. That, plus the pinning cells `T(40,19)`/
`T(39,18)` themselves, is now the entire non-two-source content of a(41)'s
tower half. A Python e3 push to K = 22 would retire those nine numbers;
the H = 20 sweep at Nmax 41 would instead make the level-21 *output* a
holdout and is the stronger artifact per hour.

## §B17 — the integrality-congruence gate (built, GREEN, REDs proven)

`experiments/undertow_congruence_gate.py`. Generalises Lane B's one-off
D_2(21) observation: a below-onset cell at level k, depth j is
`P_k(2k+1-j)*3^(-(k+j)) + D_j(k)`, an integer, and `den(D_j(k)) | 3^(k+j)`
(checked, not assumed — it holds at every j <= 4, k <= 21). So integrality
pins `D_j(k)`'s numerator mod `3^(k+j)` from `P_k` alone. The modulus grows
with k and j: **the strongest congruences sit exactly on the frontier's
unbanked cells**, which is where nothing else reaches.

Ran (0.17 s, GREEN): 71 banked cells checked at full equality (strictly
stronger than the congruence; subsumes the W3-gate surface and T(40,20)),
pin cells reported but never counted (by construction), and the two FREE
cells — the gate's new evidence:

    T(42,21) (k=21, j=1): D_1(21) congruent mod 3^22   OK
    T(41,20) (k=21, j=2): D_2(21) congruent mod 3^23   OK

`D_1(21)` previously had **zero** checks of any kind; `D_2(21)` gains a third
leg (C++ table, §S-A4 Python derivation, now the congruence). Fail-closed:
the FREE surface going empty is itself a gate failure.

RED controls, all fired (0.27 s):

- RED 1: `D_2(21) + 3^-23` caught at the free cell (smallest representable
  fractional perturbation).
- RED 2: corrupted `a_21` caught.
- RED 3 (the blind spot, demonstrated on purpose): an INTEGER shift of a
  free cell's defect passes — the congruence sees only the fractional part,
  k+j trits of the value, and the gate's docstring says so.
- RED 4 (measured, not argued): `D_4(21) + 3^-25` — **the one single-source
  constant left in a(41)'s tower** — is caught *transitively*: the perturbed
  pin shifts (a_21, b_21) and integrality breaks at the free cells. So the
  congruence gate reaches the pin inputs' fractional parts too, which no
  other check touches. Coverage claim is exactly what RED 4 measured (a
  3^-25 shift); the integer part of D_4(21) stays uncovered until depth 5
  or the H=20 sweep.

## §B13 — the depth-5 gate, red-first, predating D_5

`experiments/severance_w3_depth5_gate.py`. The banked surface for depth 5
already exists — the 15 cells `T(2k-4, k-4)`, k = 5..19 — and had no gate.
This one is written while `D_5` does not exist, so the emax=4 table lands
into a gate that predates it.

- **Production run is RED today, by design and fail-closed** (exit 1,
  verified): `D_series(5,19)` needs `results/severance_w3_families_K*_e4.txt`
  (K >= 19), which the ayr emax=4 K-ladder has not yet produced. The gate
  refuses to fall back to the pure-Python emax=4 DP (hours; a hang is not a
  gate) and says exactly why it is red. A sub-19 intermediate rung of the
  ladder will not turn it green — `_load_table` requires K >= 19.
- **The comparator is `severance_w3_gate.check_depth` imported, not
  reimplemented** — the code proved red here is the code the future table
  faces.
- `--selftest` runs today (0.1 s, GREEN): depth-1 anchor, then the empirical
  depth-5 series (T - law, extracted from the banked cells — a tautological
  pass, labelled as harness-sanity in the output itself), then a perturbed
  entry (`+3^-17` at k=12) which the comparator catches. Red-first proof
  complete with no D_5 anywhere.

Neither gate is wired into `make gates`: `severance_w3_gate.py` itself is
not, so the standalone-experiment-gate convention was followed — but see
successor row S-A5, because the Makefile's own meta-warning applies.
