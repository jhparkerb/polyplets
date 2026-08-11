# Refuter B: Proposer 2's parity and symmetry claims

2026-08-11, Refuter B of the triangle-structure hunt
(`docs/triangle-structure-team-brief.md`). Targets:
`results/triangle-hunt-klein-parity.md`,
`results/triangle-hunt-sym-diagonals.md`. Attack scripts (all exact
arithmetic, all run to completion): `experiments/tristruct/refB_parity_check.py`,
`refB_recount.py`, `refB_fits.py`. Default verdict was OVERFIT; the verdicts
below are what survived the attacks, with the attacks named.

## Verdict table

| claim | verdict | correction |
|---|---|---|
| C1 parity theorem: T(n,H) ≡ 0 (mod 2), n odd, H even | **SURVIVES** (proof audited, holds) | none; one lemma worth writing out (below) |
| zero set of I(n,H) is exactly {n odd, H even} on n ≤ 40 | **SURVIVES** | none (data-reading claim; verified against the file's absent-row convention) |
| bits on a(40) = 0, honesty of the accounting | **CONFIRMED** | none; no restatement sneaks a(40) back in |
| increment over `results/subgroup-mod4.md` | **REAL, modest** | as stated: the proof replaces a computed input by a closed-form 0 on 190 cells |
| diagonals I(n,n−k) quasi-polynomial, k ≤ 5 | **SURVIVES — and upgraded**: every claimed cell independently recomputed by my own enumeration, n = 2k+2..40 | k=4 printed form is WRONG at odd n: m must be ⌈n/2⌉, not the file's m = ⌊n/2⌋ |
| k=5 marginal-support fit | **SURVIVES** (no longer a fit question: verified by direct count, all even n = 12..40) | note: the proposer's own script culls k=5 by the 2d+3 rule; the table row is a disclosed manual override |
| column recurrences I(·,3) order 8, I(·,4) order 5 | **SURVIVES — upgraded**: I(n,3), I(n,4) recomputed independently for ALL n ≤ 40, incl. I(40,3)=187425, I(40,4)=8117; the recurrences hold on MY numbers | none |
| columns H=5..12 / diagonals k≥6 negatives | **CONFIRMED** (procedures re-run, no passing form) | none |
| corollary P_k(n) ≡ I(n,n−k) (mod 2) | SURVIVES but **zero increment**: implied by the banked T ≡ I identity + the proved diagonal law (3^m odd). Checked on 378 diagonal cells, 0 mismatches | proposer already frames it as a corollary; keep it framed that way |
| "the mechanical sweep could not have found this" | **SURVIVES-WEAKENED**: conclusion right, justification partly wrong | the H=4 column mod 2 IS periodic (period 4) and the sweep found+culled it; H=6, H=8 are periodic too (period 8, under-supported in the fit region); only H ≥ 10 is irregular. See §4 |

## 1. The parity theorem — proof audit (the attack surface is the proof)

Every step checked; the proof is sound. The one step that deserves a written
lemma: F is an involution on *translation classes*, so "F-invariant" a priori
means reflect(A) = A + t, not reflect(A) = A. The gap closes because the
reflection is about A's own bounding-box midline, so box(reflect(A)) = box(A);
equality with A + t forces box(A) + t = box(A), hence t = 0 and genuine set
equality. From there: the row involution i ↦ H+1−i is fixed-point-free for H
even; each column (all cells at a given x, contiguous or not) maps to itself
and pairs its cells, so every column has even size and n is even. Also
checked: reflection is a king-lattice automorphism (Chebyshev metric invariant
under y-negation), height is preserved exactly (box maps to box), H = 2 has no
edge case, and the same box argument makes the r180 variant and the
T ≡ I_H(D2ax) (mod 2) orbit identity airtight. Suggested edit: one sentence in
the writeup making the t = 0 lemma explicit.

Numerics (mine, own loader on the raw `h<H>.out` files, not `triangle.py`):
region = 190 cells, all n ≤ 39, zero row-40 cells, 0 parity violations, and 0
region cells with T = 0 — every one of the 190 bits is non-vacuous
(`refB_parity_check.py`). Banked-I zero-set: the 630-row file has no explicit
zeros and its 190 absent grid cells are exactly the region.

Prior-art grep re-run myself (`parity|mod 2|klein|d2ax` over `results/*.md`,
`docs/proofs/*.md`): `subgroup-mod4.md` banks the two-sided computed identity;
`percell-mod4.md`'s "genuine zeros" note is about the ⟨h⟩/C2 inputs of the
mod-4 refinement, empirical, no characterization. The n-odd/H-even theorem
appears nowhere else. Novelty claim stands at its stated (modest) size.

## 2. Independent recomputation — the decisive attack (`refB_recount.py`)

Everything below is my own code from the lattice definition; no engine
source read, no proposer code reused.

- **From-scratch enumerator, n ≤ 8**: T(n,H) and I(n,H) both match banked on
  every cell. (Rule independence: my own connectivity and canonicalization.)
- **Columns H=3, H=4, ALL n ≤ 40**: a Klein-invariant animal of height 3/4 is
  a palindromic word of tb-symmetric columns; connectivity reduces to a
  scan rule which I validated against per-word BFS on all 528 words with
  n ≤ 16 before trusting it (checker held to a higher standard). Result:
  every banked I(n,3), I(n,4) matches, including the two headline holdout
  targets I(40,3) = 187425 and I(40,4) = 8117, and **both claimed recurrences
  hold on my independently computed numbers**, not just on banked ones.
- **Diagonals k ≤ 5, n = 2k+2..40**: direct enumeration of narrow
  Klein-invariant animals (width ≤ 2k+1, palindromic row-words, excess k,
  per-configuration BFS). Every value matches banked; the k=3 and k=5 forms
  and the corrected k=4 form match on every past-onset cell; the k=5
  pre-onset failures are exactly the claimed −6, −1, +3 at n = 6, 8, 10.

Consequence for lineage (the proposer's phase-2 fits touched banked n ≤ 22,
and fit *and* holdout share the single `symcount_fast` code path): closed.
The entire claimed cell surface is now two-source — banked `symcount_fast`
vs. my enumeration — with the proposer's own n ≤ 14 self-data as a third
lineage. A systematic symcount error shaped like a nice quasi-polynomial is
excluded by direct recount, not by fit statistics.

My first enumeration attempt had a wrong width bound (w ≤ k+1; the diamond
at n=4 already has w = 3 = 2k+1) and undercounted three diagonals until the
banked comparison caught it — recorded here as evidence the comparison is a
live check, not a formality. Correct bound: a heavy row of excess e covers at
most e+1 columns, total excess k ⇒ w ≤ 2k+1.

**The k=4 correction.** As printed ("(m−1)(m−2)/2 + 2", m = ⌊n/2⌋, class
"both"), the form fails at every odd n (first at n=11: form 8, true 12 —
against banked AND my recount). With m = ⌈n/2⌉ it matches everywhere
n = 7..40 (equivalently: I(n,n−4) depends only on ⌈n/2⌉; the proposer's own
phase-2 fit points (17,30),(19,38),(21,47) vs (18,30),(20,38),(22,47) show
the underlying per-class fits were right — this is a write-up transcription
error, not a data error). SURVIVES-WEAKENED until the file is fixed; with the
one-character fix, SURVIVES.

**Upgrade path, for the proof-first lane**: the enumeration parametrization
is a proof sketch of the claimed shape — Klein-invariant diagonal animals are
placements of at most ⌊k/2⌋ heavy-row profiles in ⌊H/2⌋ palindromic slots
with O(1) local connectivity constraints, so I(n,n−k) is eventually
quasi-polynomial in n of period 2 and degree ≤ ⌊k/2⌋ for EVERY k (the k ≥ 6
"not determined" is about reachability from n ≤ 22, not existence). Likewise
the H=3 recurrence's characteristic polynomial factors as
(x²−1)(x⁶−x⁴−x²−1) — tribonacci in x², exactly the palindromic 3-letter
column-word mechanism (letter sizes 1,2,3; halves substitute x → x²).

## 3. Fit-procedure attacks and the luck rate (`refB_fits.py`)

- **Alternative forms, k=5** (attack on the 6-point/deg-2 marginal fit):
  deg-3 through the top 4 fit points collapses to the same quadratic; deg-1
  fails the fit region itself; period-4 linear pairs fail their own fit
  points. No competing form passes — the holdout defence was already sound,
  and §2 makes it moot.
- **Refit lower (cap n ≤ 18)**: k=3 and the H=3 order-8 recurrence emerge
  identically and pass 22-term holdouts. k=4/k=5 lack 2d+3 support at ≤ 18
  (rule-honest "no pass") but with the rule waived the same forms emerge and
  pass. H=4's order-5 needs 10 even-n terms — genuinely impossible below
  n ≤ 22; the proposer's fit-region choice was forced, as declared.
- **Luck rate, 268 perturbation trials** (one fit-region cell changed by
  ±1/±2, identical procedures re-run): **0 false passes** — no case where a
  form making different holdout predictions survived. 36 trials re-found the
  true form with the perturbed cell excluded by the measured onset or landing
  on the form; 8 trials (perturbing the first two terms of the H=3 column)
  passed by absorbing the corrupted head into an order-9/10 recurrence whose
  holdout predictions are the true form's. Calibration lesson for the whole
  fitted class: a holdout pass certifies *tail* structure, not head-cell
  integrity, and reported minimal order is the head's certificate.
- **Procedures on 13 negative controls** (diagonal classes k=6..10, columns
  H=5..12): 0 manufactured passes; matches the proposer's negatives, which I
  re-ran from their scripts and reproduce.

## 4. Ruling on the prior-work boundary (lead's follow-up)

**Is the parity theorem a repackaging of `results/subgroup-mod4.md`?** Ruled
NO — the increment is real and is already priced at its true (small) size.
Basis, checked myself:

- `subgroup-mod4.md` banks T(n,H) ≡ I_H(D2ax) (mod 2) by computing BOTH
  sides on all 820 cells (row 40 included). It nowhere states, proves, or
  characterizes any vanishing of I. The n-odd/H-even zeros sit in its data
  artifact `subgroup_d2ax_byheight.txt` as 190 silently absent rows —
  banked-but-unremarked.
- `percell-mod4.md`'s "genuine zeros" aside is about the ⟨h⟩ and C2 inputs
  of the mod-4 refinement, at n ≤ 32, empirical, with no characterization —
  different subgroups, different statement.
- No one-line derivation from banked statements exists without supplying
  precisely the new ingredient (the fixed-point-free row reflection forcing
  even column sizes). That ingredient is elementary, but it is in no file;
  greps over `results/*.md` and `docs/proofs/*.md` in §1 and again for
  vanishing/empty/zero phrasing found nothing.
- Confirmed the lead's premise: the team brief's prior-work list omits both
  subgroup files. The proposer found them by grep before proposing and
  scoped its claim to the delta — the file's own novelty section draws
  exactly the right boundary.
- Fair repricing note, unchanged from the proposer's own accounting: the
  190 cells already carried a *computed* parity bit from subgroup-mod4; the
  theorem upgrades their provenance (proof-grade, symcount-independent), it
  does not add cells to the parity coverage, and it adds nothing at n = 40.

**Could the sweep have found it?** The conclusion stands — the sweep has no
hypothesis class for a region/parity-class statement ("the odd-n subsequence
of every even-H column vanishes mod 2"); its congruence classes are
whole-column patterns. But the proposer's justification ("on an even-H
column the mod-2 residues are ... neither constant, periodic, nor an
order-2 recurrence") is measurably wrong at small H: T(n,4) mod 2 is
periodic with period 4 on n = 4..40 and `sweep_report.md` line 485 shows the
sweep FOUND it (culled KNOWN-COINCIDENT, low-strip closed form); T(n,6) and
T(n,8) mod 2 are periodic with period 8 on all of n ≤ 40 (measured here) and
the sweep missed them only for fit-region support (period 8 needs 2p+4 = 20
fit points; those columns have 17 and 15). H = 10 is the first even column
genuinely aperiodic (no period ≤ 9, no order-2 GF(2) recurrence, n ≤ 40).
The parity file's sweep-immunity sentence should be softened to the
region-statement argument, which is the correct one. (Side observation for
the lead, not pursued: the full-column mod-2 periodicity of H = 6, 8 out to
n = 40 is real data the sweep's support rule excluded; it is presumably the
low-strip closed forms' parity and worth one line in someone's ledger, not
a candidate.)

## Bits and tier, corrected

- Parity theorem: Tier C as claimed; **0 bits on a(40)** (correct and
  honestly stated); 190 non-vacuous theorem-grade parity bits on n ≤ 39.
- Sym-structure file: ~0 direct bits on a(40), as self-declared. Its real
  contribution after this review is stronger than fitted-tier: the row-40
  parity-check inputs I(40,3), I(40,4) and diagonal I(40,H) for H = 35..40
  are now confirmed by an enumeration that shares no code with
  `symcount_fast` — but note this hardens the *inputs* of the banked per-cell
  parity check; the check's yield on T(40,H) remains 1 bit/cell.

## Deferrals / not re-audited

- Diagonal cells n ∈ {9,10,11} at k=4,5 (between my full-enumeration reach
  n ≤ 8 and my part-3 range n ≥ 2k+2) rest on banked + proposer self-data
  only; the corrected k=4 form matches banked there (spot-checked).
- The Wave-0 verifier's 135/135 count was not re-audited; my own 190/190
  direct region check supersedes it.
- The parity file's claim that the mechanical sweep could not have found C1
  was not verified; it does not bear on validity.
