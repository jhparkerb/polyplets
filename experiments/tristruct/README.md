# tristruct — harness for the T(n,H) triangle structure hunt

> Some files cited below were filed on the unmerged branch `triangle-structure` and never reached this one: `git show triangle-structure:<path>`.

Wave-0 deliverable for `docs/triangle-structure-team-brief.md`. Everything a
proposer or refuter needs is in this directory; a stranger should be able to
use it from the docstrings alone.

## Files and invocations

| file | what | run |
|---|---|---|
| `triangle.py` | exact-int loader with validation + provenance | `python3 triangle.py` (smoke) |
| `schema.py` | the candidate schema + fit/predict sandboxes | imported |
| `known.py` | executable prior-work predicates (cull baseline) | imported |
| `verify.py` | the automatic verifier | `python3 verify.py candidates/<f>.py`, `python3 verify.py --selftest` |
| `sweep.py` | mechanical slice/stencil sweep | `python3 sweep.py` → `sweep_report.md` |
| `test_verify.py` | RED-first tests of the harness's own guards | `python3 test_verify.py` |
| `candidates/example.py` | worked template for emitting a candidate | `python3 verify.py candidates/example.py` |

All paths relative to `experiments/tristruct/`; scripts run from this
directory (they compute the repo root themselves).

## The data, and the provenance caveat (read before scoring independence)

Loader source: `results/ns_a40/perheight/h<H>.out` (H=1..40, lines
`<n> <T(n,H)>`, n=1..40) and `results/ns_a40/triangle.txt` (`<n> <a(n)>`).
At load time the loader asserts, and refuses to serve data otherwise:
the row-sum identity a(n) = Σ_H T(n,H) for every n=1..40, the anchors
T(40,40)=3^39 and T(40,39)=955·3^36, structural zeros (H>n), and file
completeness.

**Not every banked cell is an enumeration result.** Determination, from
`results/ns_a40/PROVENANCE.md` line 26 ("Real sweeps H3-H21; H22-H40 via
wired P_k closed forms (k = 40-H <= 18)") and `orchestrator/sweep.go`
(lines 428-430 and 1938-1970, `lowHeightRow`/`contributeLowHeight`):

| H | provenance flag | meaning |
|---|---|---|
| 1–2 | `closed-form-lowstrip` | engine's analytic strip rows: T(n,1)=1; T(n,2)=2T(n-1,2)+T(n-2,2)+4. PROVENANCE.md line 12 lists phase A as "H1-19", but H1/H2 inside it are formula contributions, never swept (sweep.go:428-430 short-circuits them) |
| 3–21 | `real-sweep` | kink-carry production sweeps (phases A/B/C) |
| 22–40 | `closed-form-Pk` | wired diagonal closed forms P_k, k = n−H ≤ 18, for **all** n in those files, not just n=40 |

Why it matters: a candidate whose holdout/row-40 cells are all
closed-form-derived is checking the *wiring of a formula*, not the
enumeration — near-zero independent-check value on a(40). Every verify
report therefore carries `holdout_real_sweep` and `row40_real_sweep`
("x/y real-sweep") computed from `Triangle.provenance(n,H)`. Further
lineage nuance from PROVENANCE.md you should know when scoring: H21 is
real-swept but is P_19's second fit point (no holdout exists at any n);
H20 has a byte-identical independent re-sweep; rows H15–19 (43.8% of
a(40)) rest on the single production sweep alone.

## Emitting a candidate (proposers)

Write `candidates/<you>_<topic>.py` defining `CANDIDATES = [Candidate(...)]`
— copy `candidates/example.py`. The contract (full details in `schema.py`):

- **Never bake parameters in.** Supply `fit(view)`; the verifier calls it
  with a `FitView` that physically cannot serve rows above `fit_max_n`
  (default 22, hard ceiling 39; row 40 is never served). `n_params > 0`
  without a `fit` callable is a schema error.
- **kinds**: `value` (exact T(n,H), or a(n) for `scope="rowsum"`),
  `congruence` (residue mod `modulus`), `boolean`
  (`check(params,n,H,value,ctx)`).
- **predictions may consume banked cells** via `ctx` (`PredictContext`):
  rows strictly below the target only (boolean may also read same-row
  cells); the target cell itself is never readable (PeekViolation ⇒ cull).
- **the four independence fields are mandatory** (`input_footprint`,
  `derivation_independence`, `rule_independence`, plus
  `bits_claimed`/`bits_justification` if you claim bits).
- `fit_max_n > 22` requires `fit_region_reason` naming the hypothesis class
  that forced it, and is flagged for a lower independence score.

## Reading the verifier

`python3 verify.py candidates/<f>.py` prints one line per candidate plus
flags. Verdicts: `SURVIVES` (fit n≤22 consistent, all holdout rows 23–39
exact), `FAILS(first fail row n=…)`, `CULLED(reason)`. Row 40 is scored
separately (`row40` column) as the final prediction and never affects the
verdict or the fit. Bits: congruence mod m ⇒ log2(m) per cell (claims above
that are overridden and flagged BITS-INFLATED; summing across cells assumes
independent failure — refuters judge correlation); exact-value and boolean
predictions get NO bits number unless the proposer justifies one
(BITS-UNVERIFIED) — the verifier refuses to invent it. Candidates whose
holdout predictions are implied by prior work are CULLED
KNOWN-COINCIDENT; `known.py` currently encodes the diagonal law
(`docs/proofs/diagonal-law.md`, exact, k ≤ 13 fully determined in-grid),
the ternary spine mod 3 (`results/ternary-spine.md`: T4 activation zeros,
T1 digit-product spine values, T3 even boundary, deficit-2 ≡ 2), and the
engine's low-strip columns H ≤ 2. Restating anything on the brief's
prior-work list that `known.py` does NOT encode (column TM results,
height-distribution collapse, …) is still a zero — grep before claiming
new; the machine only catches the three families above.

## What the sweep already covered — do not re-probe

`sweep.py` ran to completion (0.8 s single-core; measured, well under the
budget). Authoritative search-space statement: the `sweep.py` docstring.
Summary: all slices s·n+t·H=c with primitive |s|≤3, 1≤t≤3 having ≥10 fit
points (n≤22) and ≥5 holdout points (23≤n≤39); per slice, P-recursive
relations (order ≤7, coefficient degree ≤2, ≤16 unknowns), congruence
patterns (27 moduli 2…256: eventually-constant, period ≤9, order-2
recurrence mod m≤13); the a(n) sequence itself; and all constant-coefficient
stencil identities on ≤5 cells of the 3×3 offset box. Everything was pushed
through `verify.py`'s fit-low/predict-high rule.

Results (`sweep_report.md` has the full record):

- **Geometry finding**: only directions with |slope dH/dn| ≤ 1/2 (columns
  (0,1), diagonals (−1,1), half-slope (−1,2)) have slices spanning both the
  fit and holdout regions; all 12 other directions have ZERO testable
  slices (counted per direction in the report). Anti-diagonals (1,1) are
  untestable by this rule — no slice has both fit and holdout support.
  Rows (t=0) are excluded by construction: fixed n has no n-extrapolation.
- **Survivors: NONE.** The sweep's first pass left four, all on real-sweep
  columns: T(n,3) mod 4 period 8 (hence mod 2 period 4), T(n,4) mod 2
  period 4, and an order-7 constant-coefficient recurrence for T(n,3)
  (each 17/17 holdout rows + row 40). All four were then **culled
  KNOWN-COINCIDENT** once `known.py` grew the `ColumnCFinite` family
  (`results/triangle-structure.md` §1–2: minimal column recurrences for
  H≤4, orders 1,3,7,15). They are restatements: the order-7 recurrence IS
  the banked H=3 column recurrence, and eventual residue periodicity mod m
  follows from any C-finite integer sequence — so the congruences are
  forced by reducing that same known recurrence. `sweep_report.md`'s
  survivors section is the authority and now reads NONE; the four stay
  visible in the negative record with their cull reason.

  Independently confirmed from two directions: Proposer 3's ab-initio
  atoms give column H=3 true minimal order exactly 7 over 151 exact
  instances (`results/triangle-hunt-atoms-ab-initio.md`), and Proposer 4's
  cross-lattice test found the same phenomena on the square lattice with
  its own column orders — generic mechanism, not king structure
  (`results/triangle-hunt-cross-lattice.md`). The one residue of
  king-specific content there: king χ ≡ (x+1)^r mod 2 for H=3,4 (fully
  unipotent), which is what forces the periods to be so small.
- **Full negative**: 920 tested-and-rejected hypotheses recorded
  one-per-line (BARREN = nothing in the class even fits n≤22; FAILS(n);
  CULLED(KNOWN-COINCIDENT) — the diagonal-law and spine restatements the
  sweep rediscovered and the cull correctly burned). Slices skipped for
  support are listed individually. Anything outside the stated space is NOT
  covered — the docstring's "NOT covered" paragraph is the boundary.

## The harness's own tests

`python3 test_verify.py` — 15 tests, RED-first: each guard was watched to
FAIL against a deliberately naive verifier before the guard landed. Plants:
fit() peeking at row 30; a lookup table matching n≤22 and failing at 23; a
20-parameter dressing of a 17-cell column; the diagonal law in disguise
(P_2 interpolation); an engine low-strip restatement; a mod-2 congruence
claiming 64 bits; a boolean claiming bits with no justification; a
no-holdout region; predict() echoing the target cell back; corrupt row
sums / anchors / structural zeros fed to the loader. All caught.
