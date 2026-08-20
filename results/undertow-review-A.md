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
