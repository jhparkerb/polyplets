# L4 — the symmetry quotient, pushed: routing audit, quotient-domain route, and the mod-8 ceiling

2026-08-12, gympie. Round-3 lane deliverable per `docs/triangle-round3-brief.md`,
scored under `docs/skeptical-reader-standard.md`. Blind list filed first at
`results/triangle-r3-blind-l4.md` (18:21 EDT, before any code was read).
Scripts: `experiments/tristruct/r3_l4_quotient_measure.py`,
`experiments/tristruct/r3_l4_vmirror_brute.py`, logs alongside. No new code in
any engine; every run below used the banked `build/symcount_fast` binary of
2026-08-07 or pure throwaway Python.

**Verdict in one line: the quotient-domain `--byheight` route exists — two of
its three inputs are already in the shipped binary, decline reason 1 does not
bind against it, and it clears both entry-ticket levels — and it is priced out
at n=40 by the size of its own answer: ≥6.6×10¹⁵ candidates per mirror input,
measured engine rate ⇒ centuries of laptop, decades of fleet, for one
additional bit per cell. No phase-2 proposal. The ceiling is proved: mod 4 is
the end of this route for T(n,H).**

## Disclosure block (mapped to phase 1 per the brief)

    claim:                             a costed quotient-domain route to T(40,H) mod 4,
                                       H=15..21; verdict: route exists, priced out; declined
    share of a(40) reached:            50.84% (band H=15..21; provenance: 'real-sweep',
                                       quoted from triangle.provenance(40,H) for each of
                                       H=15..21, run 2026-08-12)
    bits against enumeration error:    0 as delivered (route declined; if bought at
                                       phase 2: 2 per band cell mod 4, of which 1 is
                                       already banked by results/subgroup-mod4.md —
                                       net +1 bit per cell)
    bits against formula-chain error:  0   conditional on: nothing — the band is
                                       real-sweep; no formula chain is involved
    rule independence:                 quotient DFS + BFS-on-lifted-set; no frontier, no
                                       component labels, no cut (see entry ticket below)
    derivation independence:           the mod-4 identity is Burnside algebra from the
                                       lattice definition, not fitted; banked data was
                                       read only to VERIFY the toy runs (checker
                                       validation, not derivation)
    input footprint:                   0 banked cells consumed by the route itself;
                                       verification consumed the n<=32 percell_raw
                                       tables and results/sym_counts.txt, max n = 32
    checker:                           phase-2 artifact (declined): an assembler in the
                                       style of experiments/subgroup_mod4.py comparing
                                       four quotient-DFS --byheight tables against
                                       banked T(n,H) mod 4, minutes on a laptop, RED
                                       control = corrupted-cell battery
    sensitivity:                       DEFERRED (phase-1 route proposal, per brief)
    prior-work grep:                   git log --all --oneline --name-only -- 'results/*.md'
                                       'docs/**/*.md' 'docs/*.md'  (both docs terms, per the
                                       corrected standard; 327 unique paths), then grep of the
                                       symmetry-related subset and git show on
                                       docs/s2-symmetric-enumerator.md (78602f8^); per-cell
                                       mod-8 ceiling unaddressed anywhere; row-level a(n)
                                       mod 8 exists in results/subgroup-mod4.md and is a
                                       different object

## Entry ticket

King-connectedness in the proposed route is decided by `symcount_fast`'s
per-candidate BFS over the *lifted cell set* (`cpp/sym/symcount_fast.cpp:209-227`):
every emitted animal is checked whole, `reachedCnt == n`, against the KDX/KDY
adjacency tables. There is no frontier, no cut, no component label, no
sufficient-statistic abstraction of connectivity — the definition is evaluated
directly on the complete object. **Level 1: cleared** — the engines'
hypothesised misconception (harness Part 3: stencil completeness, label
partition as sufficient statistic, completion predicate) has no analogue here;
the only shared assumption is the 8-neighbour adjacency definition itself.
**Level 2: cleared** — the failure modes this route would exhibit if wrong are
a wrong orbit graph, a wrong anchor (translation double-count), or a wrong
placement census (axis through row vs between rows); all are global-object
errors, disjoint from union-find-over-a-frontier's stranding/label-merge
failure class. This is the same argument the brief itself accepts for the
banked mod-2 route, and it is why cost, not independence, is this lane's
verdict.

## Task 1 — the routing audit

Where each of the four mod-4 inputs decides connectivity, established from
code, not inherited:

| input | binary (as wired by `scripts/percell_mod4.sh`) | connectivity decision |
|---|---|---|
| `I_H(⟨h⟩)` | `build/symtm hmirror --byheight` | **frontier + union-find**: `symtm.cpp:71` includes `core/transition.h`; `stepColumnSquare8` called at `symtm.cpp:255` and `:579`; its own header (lines 15-17) says "connectivity union-find, stranding, closable harvest, completion prune — is the production transition, unchanged" |
| `I_H(⟨v⟩)` | same table grouped by W (transpose reading, `percell_mod4.sh` header) | same binary, same rule — **frontier + union-find** |
| `I_H(C2)` | `build/symtm r180 --byheight` | same binary, `sweepR180` also routes through `stepColumnSquare8` (`symtm.cpp:579`) — **frontier + union-find** |
| `I_H(D2ax)` | `build/symcount_fast d2ax --byheight` | quotient-domain DFS, per-candidate BFS on the lifted set (`symcount_fast.cpp:209-227`), **no frontier** |

The harness's conclusions on symtm and symcount_fast are **verified** (I read
both files; the line numbers above are mine, and they agree with harness
Part 3).

**Plain statement asked for by the brief:** as currently wired, three of the
four inputs — and therefore the entire incremental content of the mod-4 bit
beyond the banked mod-2 bit — are computed by the production rule class.
Mod 2, the identity collapses to `T ≡ I_H(D2ax)`, which is quotient-only;
the *second* bit is carried by `I_H(⟨h⟩) + I_H(⟨v⟩) + I_H(C2)`, all three
from `symtm`'s shared `stepColumnSquare8`. The mod-4 refinement as it exists
today would add a frontier-class consistency bit, not an independent one.

## Task 2 — the quotient-domain `--byheight` route

### Existence: yes, and two-thirds of it is already shipped

`symcount_fast` already carries `hmirror` and `r180` as per-element types
(`symcount_fast.cpp:59-68`), and `--byheight` classifies by the **true
bounding-box height of the whole lifted animal** (`symcount_fast.cpp:250-256`;
the output comment at `:381-382` says exactly this). `Fix(h) = I(⟨h⟩)` and
`Fix(r180) = I(C2)` for these order-2 subgroups, so:

- `I_H(⟨h⟩)`: `build/symcount_fast hmirror MAXN --byheight` — **exists, no new code.**
- `I_H(C2)`: `build/symcount_fast r180 MAXN --byheight` — **exists, no new code.**
- `I_H(⟨v⟩)`: does **not** exist (no vmirror type, no `--bywidth`). It needs a
  ~6-line `makeType` branch (`{ID, {-1,0,E, 0,1,0}}`, E=0,1, anchor pinning y)
  — new code, addressed under decline reason 3 below.

Verification, run today (`r3_l4_quotient_measure.log`): both existing modes,
N=12..18, cross-checked **per cell** against the banked symtm frontier tables
(`results/percell_raw/*.byheight.n32.out`, summed over W for hmirror):
**0 mismatches on every (n,H) cell, n ≤ 18, both modes.** This is itself a
small two-rule-class agreement — quotient DFS vs frontier TM — on the same
objects. And `r3_l4_vmirror_brute.py` pins the ⟨v⟩ semantics from scratch
(canonical-translation growth, no shared code, A006770 totals asserted
1,4,20,110,638,3832,23592,147941): v-symmetric-by-true-height equals the
hmirror table grouped by W on all 36 nonzero cells, n ≤ 8, 0 mismatches.

### Decline reason 1 does not bind — the crux, answered

Reason 1 ("`I_H(⟨v⟩)` has no bounded-height route") was measured against
strip-frontier methods, where the transpose sends a v-symmetric animal's
height to an unbounded width. A quotient DFS never transposes: it holds the
full lifted cell set and reads the true y-extent directly, so height
classification — and an H ≤ 21 prune — is free in this scheme. **The
obstruction was a property of the strip method, not of the object.**

### Cost: measured, extrapolated, and floored

Measured on gympie, 8 threads, banked binary (`r3_l4_quotient_measure.log`):

| mode | N=14 | N=16 | N=18 | per-term ratio |
|---|---|---|---|---|
| hmirror | 0.14 s | 1.20 s | 7.49 s | 2.50–2.91 |
| r180 | 0.87 s | 7.05 s | 53.08 s | 2.74–2.84 |

The measured ratio brackets λ^(1/2) ≈ 2.669, as it must — the quotient domain
has ~n/2 free cells. Extrapolating 22 terms at λ^(1/2) (2.669²² ≈ 2.4×10⁹):

- hmirror at N=40: 7.49 s × 2.4×10⁹ ≈ **1.8×10¹⁰ s ≈ 570 laptop-years**
- r180 at N=40: 53.1 s × 2.4×10⁹ ≈ **1.3×10¹¹ s ≈ 4,000 laptop-years**

And the floor that no engineering removes: an explicit enumeration must visit
at least one node per accepted candidate. From the banked exact values at
n=32 (`percell_raw` totals, which match `Fix(h)(32) = 2546382907164` and
`Fix(r180)(32) = 7063812264280` in `results/sym_counts.txt`), extrapolated by
λ⁴ ≈ 2574 over 8 terms:

- `I(⟨h⟩)(40) ≈ 6.6×10¹⁵`, `I(⟨v⟩)(40)` the same total, `I(C2)(40) ≈ 1.8×10¹⁶`.

Measured accept rates today (8 threads): hmirror ≈ 8.5×10⁵/s, r180 ≈
3.1×10⁵/s. Floor times: **~240 laptop-years (⟨h⟩), ~1,900 laptop-years (C2)**
— and the floor is optimistic (the DFS visits rejected candidates too).
Restricting to the band helps by a constant only: measured at n=32, the
scaled-band (H=12..17 ↔ H=15..21 at n=40) share of each input is 19.7–48.7%,
i.e. a ≤5× saving. The fleet's 32 cores buy ~4×. Every accounting lands
**3–4 orders of magnitude above any budget this project has ever approved**,
for a payoff of one additional bit per cell.

**Structural statement, which is the durable part:** for order-2 subgroups the
invariant counts are themselves ~λ^(n/2) ≈ 10¹⁶ at n=40, so *any* explicit
(per-animal) quotient method is priced out by the size of its own answer. Any
method cheaper than the answer must aggregate across a cut — and the
aggregating method for this domain already exists: it is `symtm`, the frontier
engine this round exists to escape. Within the symmetry lane, level-2-clearing
and affordability are mutually exclusive at n=40.

### Decline reason 3, addressed head-on

For `⟨h⟩` and `C2` the argued override turned out to be unnecessary: the
quotient route needs **no new code at all** — the modes sit in the same binary
and behind the same gate history (`gate-subgroup`, brute-oracle since June,
sym-farm r90 reproduction) as the banked mod-2 route, and they cross-check
against the symtm tables per cell to n=18 as of today. Only `⟨v⟩` needs a new
~6-line type, and for it reason 3 applies in full: that mode would have no
history, and its first large run would be the thing being trusted. I do not
argue that override, because the cost verdict makes it moot — there is nothing
worth buying behind it.

## Task 3 — the ceiling: mod 4 is the end, proved

**Claim: there is no group giving T(n,H) mod 8 by this route, and mod 4 is the
ceiling of stabilizer-orbit congruences for the per-cell triangle.**

The mechanism of the mod-2ᵏ identities is orbit counting: a 2-group G acting
on the fixed (translation-class) animals of size n and height exactly H, orbit
sizes dividing |G|, T ≡ Σ over stabilizer classes (mod |G|). The group must
act height-preservingly on every animal. The available actions are the point
group D4 (translations are already quotiented out in "fixed" counts, and
glide-type elements collapse: A = m(A) + t with t parallel to the axis forces
t = 0 for a finite animal, by applying the element twice). An element of D4
preserves bounding-box height for all animals iff its linear part maps the
y-axis to itself: of the eight linear parts, exactly {e, h, v, r180} do —
r90/r270 and both diagonal mirrors send the 1×2 domino (H=2) to a 2×1 (H=1).
So the full height-preserving group is D2ax, order 4 (the fact
`results/subgroup-mod4.md` banks), and **no order-8 subgroup of any available
symmetry action exists. Mod 8 via a group is impossible, not merely
unfound.**

Two escape hatches, named and closed:

1. **Resolving the free orbits instead.** T = m₁ + 2m₂ + 4m₄; mod 8 needs
   m₄ mod 2, the parity of the *trivial-stabilizer* orbit count. That is
   (T − I-terms)/4 — a quotient of the full λⁿ domain by 4, no smaller domain
   computes it, and computing it from T is circular.
2. **Changing the object.** Full D4 (order 8) does act on the joint box table:
   it gives mod-8 congruences for `B(n,W,H) + B(n,H,W)` (and for the W=H
   slice alone), with all inputs quotient-computable. But summing over W
   collapses exactly back to the mod-4 identity for T(n,H); the height marginal
   forgets the W↔H pairing. Worth a line in the synthesis as a *different*
   claim someone could someday want; it is not T(n,H) mod 8.

The only remaining route to an eighth residue class would be a non-isometric
involution on height-H animals with a controlled fixed set. None is known to
me, none appears in the corpus (grep above), and any candidate would itself be
a new unverified rule — reason 3 squared.

Note the distinction with the **row-level** identity: `a(n)` mod 8 IS banked
(`subgroup-mod4.md` §mod-8 by-product) because the full D4 acts on rows. The
ceiling proved here is per-cell, where height-preservation binds.

## The three questions, answered

1. **Does it reach H=15..21 at n=40?** In principle yes — the route is
   well-defined, height-classified, and two-thirds shipped; in practice no —
   see cost.
2. **At what cost?** Measured walls 7.49 s / 53.1 s at N=18 (8 threads),
   per-term growth 2.5–2.9 (brackets λ^(1/2) = 2.669), extrapolated
   570–4,000 laptop-years per input at N=40; candidate-count floor
   ≈ 6.6×10¹⁵–1.8×10¹⁶ per input makes any explicit variant ≥ decades of
   fleet. Band restriction ≤5×, fleet ~4×. Declined.
3. **Which levels?** Both. The route fails on cost alone.

## NOT ESTABLISHED

- The λ⁴ extrapolation of the n=32 invariant counts to n=40 (factor 2574) is
  a growth-law estimate, not a measurement; establishing the exact floor would
  itself cost the run being declined. The measured per-term wall ratios at
  N=14..18 bracket the same constant, which is the evidence offered.
- Whether the ~6-line vmirror type would reproduce the banked ⟨v⟩ table at
  scale — the n ≤ 8 brute pins its semantics, but the mode was deliberately
  not written (scout brief; and moot under the cost verdict).
- Whether a non-isometric involution on height-H animals exists that would
  yield an eighth residue class — proved impossible for symmetry actions,
  open (and unpursued) for arbitrary combinatorial involutions.

## Artifacts

- `experiments/tristruct/r3_l4_quotient_measure.py` + `.log` — timing and the
  per-cell quotient-vs-frontier cross-check, N ≤ 18, 0 mismatches
- `experiments/tristruct/r3_l4_vmirror_brute.py` + `.log` — from-scratch ⟨v⟩
  semantics reference, n ≤ 8, 0 mismatches
- `results/triangle-r3-blind-l4.md` — blind list, filed first; appended note
  records the one expectation the code corrected (two modes already existed)

## Appended 2026-08-12 evening — successor mining (queue amendment)

The lead's mid-round amendment (`results/triangle-r3-queue.md`) asked what
this lane's closure implies. Rows L4-1..L4-6 filed there. One of them was
cheap enough to measure rather than speculate:

**The cheapest implicit route is now excluded, not just unexamined.** If
`Fix(h)(n)` or `Fix(r180)(n)` were P-recursive, the banked n ≤ 34 series
would extend to n = 40 by recurrence and deliver the mod-4 inputs with no
enumeration — evading the answer-size floor entirely, since a recurrence step
costs nothing. Measured today (`experiments/tristruct/
r3_l4_precurrence_probe.py` + `.log`): exact rational nullspace search over
the 34 banked terms of each series, box r ≤ 6, d ≤ 4, ≥ 5 surplus equations,
every candidate re-verified on all terms; RED-controlled by the same probe
finding the order-1 degree-1 recurrences of factorial and Catalan. **Neither
series admits any recurrence in the box.** This matches the shape of
`results/isotropic-dfinite-boxes.md` for a(n) itself and narrows queue row
LEAD-1: the surviving implicit forms are algebraic/ADE structures and
character-sum identities, both unexamined and neither with a mechanism I can
name.

## Appended 2026-08-12 late — LEAD-1's remainder: implicit routes, run down

Dispatch: after L4-2 killed the P-recurrence branch, LEAD-1 narrowed to
algebraic-GF and character-sum implicit forms. Both examined. Scripts:
`experiments/tristruct/r3_l4_algebraic_probe.py`,
`experiments/tristruct/r3_l4_fixedh_order.py`, logs alongside.

**First, the association the dispatch warned against, checked:** the banked
non-D-finiteness theorem (`results/anisotropic-not-dfinite.md`) is about the
bivariate F(x,y) = Σ T(n,H) xⁿ y^H — its pole argument runs over the
fixed-height denominators ψ_H. It says nothing about the one-variable
symmetric series Fix(h)(n), Fix(r180)(n), and nothing below excludes their
D-finiteness as a theorem. Everything here is a finite box, and is labeled so.

**Algebraic GF: excluded in the box.** Direct fit of P(x, F(x)) = 0,
bidegree Dx ≤ 8, Dy ≤ 4, exact rational arithmetic, fit on coefficients
x⁰..x²⁶ (n ≤ 26), holdout on x²⁷..x³³ (n = 27..34, 8 coefficients).
RED-controlled in both directions: Catalan (algebraic) passes fit+holdout at
its true bidegree (1,2) and every superset; a seeded random-digit series
fails holdout everywhere. **Neither Fix(h) nor Fix(r180) admits any relation
in the box.** Note algebraic ⊂ D-finite, so L4-2's P-recurrence exclusion
already implied a (smaller) algebraic exclusion; this run tests the larger
direct box.

**Fixed-H: the implicit form provably exists, and its order is the wall.**
For fixed H every one of I_H(⟨h⟩), I_H(⟨v⟩), I_H(C2) has a RATIONAL
generating function in n (finite column transfer matrix; palindromic column
sequences for ⟨v⟩/C2 reduce to matrix-power diagonals) — so "turn the count
into an evaluation" succeeds trivially at every H, and the only question is
what pins the recurrence. Measured minimal orders from the banked n ≤ 32
tables (fit head, hold out the last 6 banked terms; RED control recovers a
planted order-5 and rejects noise):

    I_H(<h>):  H=1:1  H=2:2  H=3:5  H=4:6   H>=5: order > 12 (cap of 32 terms)
    I_H(<v>):  H=1:1  H=2:5           H>=3: order > 12
    I_H(C2):   H=1:1  H=2:4  H=3:9    H>=4: order > 12

The growth is geometric in H (and `git show`n on the second-source branch,
`results/king-column-motzkin.md` gives the state-count shape: Motzkin-type in
the strip height — for the ⟨h⟩ quotient at H=15 the half-height-8 TM has
order plausibly in the hundreds). Pinning an order-r recurrence needs ~2r
terms in n at that fixed H. Rule-independent terms come only from
enumeration — the thing the floor prices out — and TM-derived terms make the
recurrence a restatement of the frontier engine: a consistency check under
the standard, worth zero as verification. **The fixed-H implicit route
exists, and independently pinning it costs more rule-independent enumeration
than the band check it would replace.**

**Character sums: the branch reduces to the problem.** Burnside/Möbius
identities over the subgroup lattice interconvert {I(K)} and {Fix(g)} — the
project already uses them in both directions — but they re-express fixed-point
counts, never evaluate them. An evaluation would need the fixed-point sets to
biject onto a solvable family; the banked no-free-composition result
(`results/component-stratification.md`) and the measured order blowup above
are the evidence against, and I can name no mechanism. NOT ESTABLISHED as a
theorem; closed as having no candidate mechanism after examination.

**How many more terms would decide the aggregate question:** they cannot
decide it — more terms only enlarge exclusion boxes; no finite number proves
non-D-finiteness. For scale: one more rule-independent term (n = 35, quotient
DFS) costs ~×2.669 over the n=34 sweep — days of laptop and growing 2.7× per
term — while frontier-TM terms (symtm N=36 ≈ 6 h, N=40 ≈ 4 laptop-days
extrapolated at the measured 2.09×/n) are provenance-circular for this
purpose. The decisive instrument is a theorem, not terms; filed as successor
L4-7.

## Appended 2026-08-12 late — L4-9 closed at the desk: the fixed-H order wall made exact

Restart agent, per lead dispatch. Queue row L4-9 asked for the symmetric
quotients' fixed-H transfer-matrix state counts at H = 15..21, exact rather
than extrapolated. Answered by arithmetic plus a sub-second verification
closure; **no job needed, none requested.** Script:
`experiments/tristruct/r3_l4_symfrontier_census.py` (+ `.log`), 0.96 s
foreground.

### 1. Relation to the independence adversary's closed form: same decomposition, different lattice

The adversary's exact window census (`results/triangle-r3-adv-independence.md`
§6) is Σ over masks of Bell(#chunks) — the **colour cancellation DP**, whose
cut states carry arbitrary partitions. The object L4-9 needs is NOT that
census: different DP (connectivity frontier vs colour coincidence), different
partition lattice, different height parameter. But it IS expressible in the
same masks-over-chunks decomposition, and the three censuses line up as one
family — mask counts times a per-k partition census:

    colour DP cut states      = Σ_k C(H+1,2k) · Bell(k)            (adversary §1, all partitions)
    connectivity frontier     = Σ_k C(H+1,2k) · Cat(k)  = M(H+1)−1 (banked king-column-motzkin; non-crossing)
    hmirror-quotient frontier = Σ_k C(N,k) · C(k,⌊k/2⌋), N = ⌈H/2⌉ (this note; reversal-invariant non-crossing)

So the answer to the dispatch's question 1 is: **not the same object, but the
same decomposition with the partition lattice swapped** — Bell → Catalan →
central binomial — and the height halved for the mirror quotient. The swap is
forced by two facts, each proved/verified here: (i) the number of h-symmetric
column masks of height H with exactly k runs is C(⌈H/2⌉, k), both parities
(hockey-stick identity over the centered-run position; derivation in the
script header and checked by the closure); (ii) the number of non-crossing
partitions of k linearly ordered runs invariant under the reversal forced by
the mirror is C(k,⌊k/2⌋) (verified by direct filter, k ≤ 8). The total
Σ_k C(N,k)·C(k,⌊k/2⌋) = **A005773(N+1) − 1** (directed animals / palindromic
Motzkin left-factors — OEIS lookup run today; the "palindromic Motzkin"
gloss is exactly the symmetric analogue of the full frontier's Motzkin
census). Growth 3 per unit N = √3 ≈ 1.732 per unit H, against 3 per unit H
for the full frontier.

### 2. Verification, three-way, with a positive and a RED control

`r3_l4_symfrontier_census.py`: a from-scratch union-find/stranding closure
over symmetric columns (none of the predecessor's code, none of the
engines'), compared per H against (a) the directly generated predicted set
{(symmetric mask, reversal-invariant NC partition of its runs)} and (b) the
closed form. **Exact agreement of all three, and set equality not just
cardinality, at every H = 1..13** (1, 1, 4, 4, 12, 12, 34, 34, 95, 95, 266,
266, 749). Controls:

- POSITIVE: the same closure run over ALL masks reproduces the banked/proved
  full-frontier census Motzkin(H+1)−1 at every H = 2..8 — the transition
  code is validated against an independently proved value, not against
  itself.
- RED: an asymmetric stencil (NE diagonal dropped) changes the census —
  the check fails when the rule is corrupted.
- Recorded observation, echoing the adversary's stencil-blindness finding
  (queue ADV-1): a symmetric rook stencil reaches the **same state set** at
  every H ≤ 8 — the census is stencil-robust between rook and king, so a
  census-level RED must break the symmetry to bite. Anyone using state
  censuses as a gate should know the observable is blind to symmetric
  stencil errors; the counts differ, the state space does not.

### 3. The order wall, exact

The reachability hypothesis (every symmetric-mask/symmetric-NC-partition
pair reachable) is verified exactly at H ≤ 13, same epistemic shape as the
adversary's §6 census (verified at 11 points, then evaluated). Exact values
across the band, with the exact-height realization dimension (symmetric
strip has its axis pinned, so exactly-H = strip_H − strip_{H−2}, dimension
S(H) + S(H−2)) and the crude order-in-n ceiling H·dim (denominator degree of
det(I − M(x)) with column weights x^{|mask|}):

    H     S(H)    exact-height dim   order ceiling in n
    15    2,122        2,871              43,065
    16    2,122        2,871              45,936
    17    6,045        8,167             138,839
    18    6,045        8,167             147,006
    19   17,302       23,347             443,593
    20   17,302       23,347             466,940
    21   49,720       67,022           1,407,462

Small-H calibration against the measured minimal orders (this file, L4-7
section): H = 1: dim 1, measured 1. H = 2: ceiling 2, measured 2 (tight).
H = 3: dim 5, measured 5 (tight at the dim). H = 4: dim 5, ceiling 20,
measured 6 — the true order sits between dim and ceiling. So the table's
numbers are exact ceilings on the minimal order r, and the measured floor is
r > 12 at every H ≥ 5 (cap of the banked terms).

**The arithmetic sentence the synthesis needs.** Pinning an order-r
recurrence by fitting needs ~2r rule-independent terms (plus holdout), i.e.
terms of I_H(·)(n) out to n ≈ 2r. The only rule-independent term source is
quotient DFS at ~λ^(n/2) = 2.669^n per term (measured per-term ratio
2.5–2.9 brackets 2.669, this file; rule-independent by-height terms exist
today only to n = 18). Two ends of the range r ∈ (12, ceiling]:

- Most favorable untested case, r ≈ 50: terms to n ≈ 106 cost
  ~2.669^106 ≈ 3×10^45 candidate visits ≈ 10^32 laptop-years at the
  measured 8.5×10^5/s. The full L6-1 band ladder is ~75 thread-hours.
  Gap: **> 10^36**.
- Ceiling case, r = 43,065 (H = 15 alone): ~86,000 terms, cost
  2.669^86000 — a number of ~36,700 digits. Not an economics statement; an
  impossibility one.

Either way the fixed-H fitting route is dead by arithmetic, not adjective.
For the other two inputs there is no half-height quotient — the v-mirror and
r180 realizations run on the **full** frontier (matrix-power diagonals, this
file), so their exact realization dimensions are the banked Motzkin censuses
M(H+1)−1: 853,466 / 2,356,778 / 6,536,381 / 18,199,283 / 50,852,018 /
142,547,558 / 400,763,222 at H = 15..21 — worse than ⟨h⟩ by the square.

### 4. Symmetric-specific or general? General — cross-lane fact

The exact state counts above are facts about the symmetric families'
minimal *known* realizations (a smaller hidden realization is not excluded;
the measured floor is only r > 12). But the **wall does not depend on the
census**. It needs exactly two inputs: (i) the minimal order is not tiny —
measured for all three symmetric families (> 12 at H ≥ 5) and banked for
T(n,H) itself (column recurrences closed above H = 4; onsets n = 43, 107
already at H ≤ 4); (ii) rule-independent terms cost c^n — true of every
sequence on this lattice (2.669^n symmetric, λ^n = 7.12^n for T(n,H) by
enumeration). Any fixed-H recurrence-fitting program on this lattice,
symmetric or not, in any vocabulary, hits the same two facts; the symmetric
structure changes only the ceiling's base (3^(H/2) vs 3^H). Filed as a
cross-lane queue row (L4-12): it generically kills "fit a recurrence for X
at fixed H" rows unless a term source cheaper than enumeration exists — and
that is LEAD-1, closed.

### 5. L4-8, costed in one paragraph and not pursued

The haruspicy extension (prove/refute D-finiteness of Fix(h)/Fix(r180), or
the new-root structure of the symmetric fixed-H denominators ψ_H^sym) is a
theorem campaign: sessions-to-weeks of proof effort on the pattern of
`results/anisotropic-not-dfinite.md`, zero compute, zero cells, zero bits —
it converts L4-2/L4-7's finite-box exclusions into a closed door and does
nothing else. The one asset this note adds: the ψ_H^sym are now concretely
realizable as det(I − xM_sym) over the verified state space, so the
program's raw material is computable at small H. Ranked below every
band-reaching row by the standing order; left OPEN in the queue; not
pursued here.

### NOT ESTABLISHED (this append)

- Reachability of every (symmetric mask, symmetric NC partition) pair is
  verified exactly at H ≤ 13 and asserted beyond, exactly parallel to the
  adversary's §6 hypothesis; no mechanism changes character with H (the
  merge moves that realize every partition at H ≤ 13 are height-local).
- The minimal orders r at H = 15..21 remain unknown inside (12, ceiling];
  only the ceilings are exact. Pinning r exactly is the thing the wall
  prices out, and no bound tighter than the realization dimension is
  claimed.
- The tightness pattern (dim exact at H ≤ 3, slack at H = 4) is an
  observation, not a law.
