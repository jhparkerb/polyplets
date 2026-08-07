# Unexplored avenues — IDEAS ONLY, nothing here is banked

2026-08-03. Written at jasonp's request after a sweep of the accumulated state
(HANDOFF, open-conjectures, the lambda-bracket doc, the non-D-finiteness
theorem, the universal diagonal law, the closed-door notes) looking for
directions the project has not taken.

> ## READ THIS FIRST — status of everything below
>
> **These are unvetted ideas, not results.** Nothing here has been reviewed,
> planned, costed properly, or agreed to. Specifically:
>
> - **Novelty is UNCHECKED** on every item. Several are elementary enough that
>   they are probably folklore. Nothing here may be described as new to anyone
>   outside this file until it has been grepped against OEIS, the literature,
>   and the repo's own closed doors.
> - **Cost estimates are back-of-envelope**, derived from growth-rate
>   arithmetic, not from measurement. Treat every "cheap" as a guess.
> - **Idea 3 is a proof sketch with a known-hard target.** It may well be
>   wrong. It is written down because the mechanism is concrete enough to be
>   killed quickly, not because it is believed.
> - **No compute has been requested or authorised** for any of this, and none
>   should be started on the strength of this note.
> - The project **closes at a(40)**; remaining work is report placeholders and
>   publish prep. Everything here is downstream of that, if it happens at all.
>
> Two small things below **were** measured in-session and are marked MEASURED.
> Those measurements are trustworthy; the conclusions drawn from them are not
> automatically so.

Standing filter (MEMORY.md, claim-pruning): before chasing any of these, name
the sentence in the paper that gets *shorter* if it works. Where I can name it
I have; where I cannot I have said so.

---

## 1. Burnside run backwards: congruences for a(n) -- EXECUTED 2026-08-07

**Status: no longer an idea.** Built, gated and run; see
`results/subgroup-mod4.md` for what it found, and read the struck bullet
below before quoting this section's payoffs.

**The observation.** D4 acts on fixed polyplets; orbit sizes divide 8. With
`n_k` = number of orbits of size `k`,

```
a(n) = n1 + 2*n2 + 4*n4 + 8*n8
```

so `a(n) = n1 (mod 2)`, `= n1 + 2 n2 (mod 4)`, `= n1 + 2 n2 + 4 n4 (mod 8)`.
`n1` counts animals with FULL D4 symmetry; their cells lie in D4-orbits of
size 8, 4 (on an axis or diagonal) or 1 (centre), so `n = 8p + 4q + r` with
`r` in {0,1}, forcing `n = 0 or 1 (mod 4)`. Hence:

    a(n) is EVEN whenever n = 2 or 3 (mod 4).

**MEASURED** (`experiments/orbit_parity_probe.py`, brute force n<=9 plus the
banked b-file):

- all three congruences hold exactly at every n <= 9;
- across the 40 banked terms `a(n)` is odd at exactly
  **n = 1, 8, 17, 21, 24, 25, 28, 29, 40** — every one `= 0 or 1 (mod 4)`,
  zero violations. 9 odd terms out of 40 where a null model wants 20; the
  whole deficit is this congruence.
- The same pattern holds for A001168 (fixed polyominoes odd only at
  n = 1,4,5,8,12,16,21,25) — same group, same argument.

**What is not in the repo.** `results/sym_counts.txt` banks per-ELEMENT
`Fix(g)`, which is enough for Burnside orbit-*counting* (how the free counts
are derived) but NOT for the orbit-*size* distribution. The subgroup-invariant
counts `I(D4)`, `I(D2ax)`, `I(D2diag)` are separate objects and are not banked.

**Guessed cost ladder** (UNMEASURED — pure growth-rate arithmetic):

| needed for | quantities | rough family size | guess |
|---|---|---|---|
| mod 2 | `I(D4)` | ~lambda^(n/8) ~ 2e4 at n=40 | trivial |
| mod 4 | + `I(C4)`, `I(D2ax)`, `I(D2diag)` | ~lambda^(n/4) ~ 3e8 at n=40 | laptop |
| mod 8 | + `I(C2)`, `I(h)`, `I(d)` | ~lambda^(n/2) | hmirror/r180 cheap; **dmirror is the 24h/126GB blocker** (`results/related-seqs-n33.md`) |

**Claimed payoffs, if any of the above survives contact with reality:**

- `ns_a40/PROVENANCE.md` records H15-19 (43.8% of a(40)) with no second
  source. Two independent bits mod 4, from a structurally unrelated algorithm
  on a quotient domain, would cover 100% of the row. **This is the sentence
  that gets shorter.**
- ~~The same inputs are what A030222/A030233/A030234/A030235/A194596 need;
  they have been stranded at n=32-34 while fixed reached 40.~~
  **WRONG, struck 2026-08-07.** Burnside needs per-ELEMENT `Fix(g)` --
  `free_num = fixed + 2 Fix(r90) + Fix(r180) + 2 Fix(h) + 2 Fix(d)`
  (`tests/common.py:132`, `free_and_one_sided`) -- and the binding input there
  is `Fix(d)`, the diagonal-mirror count, which is exactly the 24h/126GB
  lambda^(n/2) blocker of `results/related-seqs-n33.md`. The order-4 subgroup
  counts `I(C4)`, `I(D2ax)`, `I(D2diag)` are a *different object* (invariant
  under every element of a subgroup, not fixed by one element) and do not feed
  Burnside at all. The five related sequences stay stranded; nothing in this
  idea moves them.
- Statements about terms that will never be computed (`a(60) mod 4`).

**Sharper than the mod-4 row total, found while implementing it (2026-08-07).**
D2ax = {e, h, v, r180} is *exactly* the height-preserving subgroup of D4 --
r90, r270 and both diagonal mirrors swap height with width -- so it acts on
the animals of each fixed height separately, orbit sizes there divide 4, and

    T(n,H) = I_H(D2ax)   (mod 2)

is one independent bit per triangle CELL rather than two bits on a row total.
That is what actually addresses the payoff bullet above: it localises the
check to the H15-19 band instead of only constraining the sum a(40).

**Rider, separate and weaker.** This is the natural place to test the
resonance `results/anisotropic-not-dfinite.md` flags as *"open and nobody has
looked"* — Klazar Thm 4 (P-recursive mod 2^k with no P-recursive parent) vs
the ternary spine. Cheap probe: `deg(psi_H mod 2)` for H <= 10; over Q these
grow x2.7, and if mod 2 they stay bounded then `a(n) mod 2` would be
2-automatic by Christol. **MEASURED and negative so far:**
`experiments/modp_bm_probe.py` runs Berlekamp-Massey on the 40 terms mod
{2,3,5,7,11,13} and finds order ~n/2 in every case — no C-finite structure.
That is the expected answer and rules nothing out about algebraicity; it also
does not support it.

**Novelty: UNCHECKED, and the congruence is elementary.** Probably known for
polyominoes. Must be grepped against OEIS comments and the literature before
being called anything.

---

## 2. Polyominoes and polyplets are a matching pair (percolation lens)

**The observation.** The king lattice is the matching lattice of Z^2 for site
percolation — which is why `p_c(square site) = 0.59275` and
`p_c(king site) = 0.40725` sum to 1 (a 2D theorem for matching pairs, not a
coincidence). Grepping the repo, percolation appears exactly once, as a
convention cross-check on site-perimeter in `results/polyplet-zoo.md`.

So A001168 and A006770 are not two unrelated families the project happens to
study; they are the two halves of a matching pair, and the classical
Sykes-Essam identity relates their PERIMETER-REFINED counts, with an
inhomogeneous term that is a Euler-characteristic count — i.e. the same
topological data as the hole stratification (`results/hole_gfs.txt`, A0/A1,
the maxhole work).

**The convention detail that decides whether this works at all:** in the
matching identity each cluster's boundary is measured in the *other* lattice —
a polyomino's perimeter w.r.t. the king neighbourhood, a polyplet's w.r.t. the
rook neighbourhood. Get this wrong and nothing will check out. Testable today
against the n<=19 `byBox`/site-perimeter data plus published polyomino
perimeter polynomials, before any new compute.

**Claimed payoffs (speculative):**

- A cross-family exact identity — a validation channel of a kind the project
  has never had (every existing second source re-counts the same objects).
- Perimeter-refined king-lattice cluster series are published to roughly
  n ~ 12-15; the triangle machinery with `--perimeter` reaching n ~ 30 would
  be an extension with a physics audience, and yields p_c directly (testable
  against the known 0.40725).

**Honest limit, stated up front:** the identity constrains the
perimeter-refined counts, so it is NOT a cheap check on a(40) unless the
perimeter refinement is pushed to n=40, which is expensive. This is structure
plus an outward deliverable, not frontier validation. **No sentence in the
current paper gets shorter.**

---

## 3. lambda upper bound: a bridge-credit sketch (MOST LIKELY WRONG)

**CLOSED 2026-08-07 — it was wrong, and unsound rather than merely unproved.**
`results/bridge-credit-closed.md`, `experiments/band_charge_probe.py`. The
short version: step 1's encoding is not injective (all three 2-cell animals
share one code; 96% of the n=8 census collides at H=1), because it records no
band-to-band horizontal alignment — which is exactly the `c(H)` the scheme
existed to bound. Assuming `c(H)=1` gives `lambda <= mu_H`, contradicting the
certified `mu_17 = 6.543 < lambda`. **Step 2, the claim flagged below as
load-bearing, holds in everything measured; the kill is one step earlier.**
Read the rest for the record, not as a live lead.

`docs/open-problem-lambda-bracket.md` asks whether the vertical join between
height-H strips is boundable and reads candidate (1) as "most promising, may
itself be non-local". A possible mechanism, offered as a sketch to be killed:

1. Cut an animal into bands of height H. Encode each band as its left-to-right
   sequence of component shapes plus the **gap lengths** between them. Shapes
   cost `mu_H^cells`.
2. A gap of length `g` in band `i` exists only because those components connect
   through band `i +/- 1`, which needs **>= g cells** bridging it there. A cell
   can be charged by at most two gaps (one above, one below), so
   `sum of gaps <= 2n`: gap entropy is `~4^n`, a constant-per-cell factor, not
   `n^Theta(n)`. This is the step that would evade the comb shatter of
   `results/concatenation-upper-bound.md` — horizontal band cuts do not shatter
   a comb; BBO's lexicographic cut does.
3. The credit: a bridging run of `g` cells has ONE shape, but `mu_H^g` was paid
   for it in step 1. Since `mu_13 = 6.306` and `mu_17 = 6.543` are both `> 4`,
   the credit would beat the cost per bridged cell.

If the accounting survived nesting and multi-band connections it would give
`lambda <= mu_H * c(H)` with `c(H) -> 1` — a bound outside the finite-type
class, so not floored by the P2 slack audit.

**Gate it must pass:** any valid bound needs `c(17) >= lambda/mu_17 = 1.087`,
so the target shape is something like `exp(K/H)` with `K >~ 1.41`.

**Fastest way to kill it:** write the charging map for a two-band example with
nested bridges and check whether a cell can be charged more than twice. Step 2
is the load-bearing claim and it is asserted, not proved.

**Why it is written down at all:** it is the only route I could construct that
has connectivity AND unbounded extent simultaneously, which is exactly what
the bracket doc identifies as missing on both faces. That is a reason to spend
an evening disproving it, not a reason to believe it. If it worked the paper's
lambda bracket sentence would be rewritten outright.

---

## 4. A lambda atlas over the row-local class (new-paper-sized)

The repo has the only lattice-generic animal toolkit I am aware of: the
universal diagonal law, the Northcott anisotropic non-D-finiteness criterion,
a generic strip ladder with exact Collatz-Wielandt certificates, and a generic
certificate checker. All four are currently exercised on one lattice each.

Instantiating the bracket machinery across a designed family — square (q=4),
hex (6), king (8), and a *spread* q=8 set such as
`{(+-1,0),(0,+-1),(+-2,0),(0,+-2)}` with the same coordination number but far
fewer triangles — would make sharp the question:

> is lambda a function of coordination number, or does local cycle structure
> move it?

Prediction to state before measuring: spread-8 should land noticeably above
king's 7.11, toward the tree bound `(q-1)^(q-1)/(q-2)^(q-2)`, because
clustering suppresses lambda. Certified two-sided brackets for more than one
or two lattices do not appear to exist anywhere; producing several would also
make the two universal theorems non-vacuous by exhibiting instances.

**Ranked last deliberately:** this shortens no sentence in the polyplets
paper. It is a separate project.

---

# Second sweep, 2026-08-04: questions that are not "how many"

Prompted by jasonp asking what else there is to explore besides enumeration
(including enumeration filtered by subtype or attribute). Ideas 1-4 above are
still counting questions wearing different hats; everything in results/ is a
count, a growth rate, or a structural fact in service of a count. The sections
below are question classes whose *answer is not a number or a sequence*.

Same disclaimers as the top of this file: novelty UNCHECKED throughout, costs
guessed unless marked, nothing authorised. Coverage claims below come from one
grep over `results/ docs/ papers/` on 2026-08-04 for the obvious keywords; the
absences are absences of the *word*, which is weaker than absence of the idea.

---

## 5. What does a TYPICAL polyplet look like?

Not a count — a limit object.

- **Local weak limit** (Benjamini-Schramm): does the neighbourhood of a
  uniformly random cell in a uniformly random n-polyplet converge, as
  `n -> infinity`, to a fixed random infinite object? The observable
  consequence is that the contact-type distribution at a random cell converges
  to constants. `results/rook-bishop-edge-distribution.md` samples exactly this
  at n=12 and never asks whether it converges.
- **Limit shape**: `results/nu-exponent.md` measures the extent exponent nu but
  not whether rescaled occupancy has a deterministic limit shape. It should not
  — animals are not convex-limit objects the way Young diagrams are — and
  saying so with evidence is itself the result.
- **The blocker is the interesting part.** Uniform sampling above oracle scale
  does not exist in this repo (zero hits for "random sampl"). Everything
  sampled so far is n <= 12ish by rejection or exhaustion. Without a sampler
  none of this is measurable past the enumeration frontier, which is what makes
  idea 8 below load-bearing rather than decorative.

**Sentence that gets shorter:** none in the current paper. New-paper-sized.

---

## 6. Universality: Parisi-Sourlas, Yang-Lee, and the central charge

**6.1 is CLOSED, 2026-08-07** — see the strike at the end of this section.
6.2 is untouched.

**The highest-value gap the sweep found, and it needs no new compute.**

Lattice animals are conjecturally in the Yang-Lee edge universality class in
`d-2` dimensions (Parisi-Sourlas dimensional reduction). That is where
`theta = -1` in 2D comes from. `results/series-analysis-da.md` *measures*
`theta = -1` by differential approximants and never connects it to the reason.
The words Parisi, Yang-Lee, and central charge appear **nowhere** in the repo.

Two concrete, separable questions:

1. ~~**Finite-size scaling of the strip data.** Conformal invariance predicts the
   strip free energy `ln mu_H` approaches `ln lambda` with a universal `1/H^2`
   correction whose coefficient carries a central charge. The repo owns
   `mu_13 ... mu_17` with exact Collatz-Wielandt certificates
   (`results/strip-mu-certificates.md`). This is a **fit to data already on
   disk**. If the coefficient lands near the Yang-Lee value the project has an
   independent confirmation of its own universality class; if it does not, that
   is a more interesting note.~~
   **STRUCK 2026-08-07** — `results/strip-growth-lambda-bounds.md` answered
   this item's own stated prerequisite, and the answer is no. The ladder's
   approach to `lambda` is not analytic in `1/H` at `H <= 17`: the surface
   term `H(ln lambda - ln mu_H)` is still falling at H=17 and its increments
   shrink only ~6.5% per rung where a clean `1/H^2` correction demands ~11.4%,
   so there is a term between `1/H` and `1/H^2` (most likely logarithmic) that
   the two-parameter ansatz cannot see. No `1/H^2` coefficient, hence no
   central charge, can be read off this data. Not an afternoon's fitting; it
   would need `mu_H` far past H=17, which the strip engine cannot reach.
2. **Is the king lattice in the same class as the square lattice?** It must be
   if universality holds. That is a *prediction*, testable against the two
   theta fits, rather than a count. **Still open** — it does not go through the
   strip ladder, so 6.1's closure does not touch it.

**Honest limits.** Five certified `mu_H` values is a short series for a
two-parameter finite-size fit, and the certificates bracket rather than pin
each `mu_H`; the fit must propagate those brackets or it is worthless.
Whether `lambda` itself is known precisely enough to expose a `1/H^2` term is
the first thing to check, before any fitting. **That check has now been run
and it failed — see the strike on 6.1 above.**

**Sentence that gets shorter:** the `theta = -1` paragraph in the series
analysis, which currently reports a fitted exponent with no explanation of why
that number. Only 6.2 could still shorten it, and 6.2 is a comparison of two
theta fits, not a derivation.

---

## 7. Extremal / isoperimetric questions

"What is the *best* n-polyplet", not "how many are there". `maxhole-proof.md`
is exactly this shape — measure at small n, guess the closed form, prove it —
and it produced a theorem, so the machinery and the taste are both proven here.

- **Minimum site-perimeter for n cells on the king lattice**, and the extremal
  shapes: the Harary-Harborth analogue (square-lattice case is A027709/A027710).
  "isoperimet" appears in the repo only inside the maxhole doc.
  **Phase 4a done** (`results/min-site-perimeter.md`): the search half only
  (n=1..14, king adjacency pinned against `results/polyplet-zoo.md`'s
  percolation cross-check). Data hits A235382 = A027709(n)+4 exactly on every
  term measured; A027710 turns out unrelated to any perimeter notion (a
  citation error in the plan, corrected there).
  **Phase 4b done — this bullet is CLOSED** (same file, final section): the
  guess-and-prove half was killed by its own criterion, because the closed
  form is already published. A235382 gives
  `a(n) = 2*ceiling(2*sqrt(n)) + 4 = A027709(n) + 4`; that is verified
  integer-exactly against all 14 measured terms
  (`experiments/min_site_perim_closed_form.py`) and is someone else's result,
  not re-proved here. No new theorem, by design.
- Max diameter, min diameter at fixed n; max articulation points; max hole
  *count* (as opposed to max single-hole area, which is `M(n)`).
- "diameter" appears **nowhere** in the repo.

Cheap entry: the oracle already computes perimeter exactly at oracle scale, so
the minimum over each n is a one-line reduction over data the repo can already
produce. Novelty UNCHECKED and the square-lattice case is classical, so grep
OEIS before getting excited.

**Sentence that gets shorter:** none directly, but it extends the paper's
existing extremal result rather than starting a new topic.

---

## 8. Dynamics of the SPACE, not of the objects

- Is the graph on n-polyplets under **single-cell moves that preserve
  connectivity** connected? Exhaustively decidable at n <= 10 with the existing
  oracle — the cheapest item in this whole file.
- If yes: mixing time, hence a uniform sampler, hence measurement of nu and of
  everything in idea 5 at n = 100+, far past the enumeration frontier.

"Markov" appears in the repo only in `defect-gas.md`, in an unrelated sense.

This is the item that converts a dead end (idea 5's blocker) into a programme,
which is why it is worth an evening even though the connectivity question
itself is probably folklore for polyominoes.

---

## 9. Inverse and decision problems

- **Discrete tomography**: reconstruct a polyplet from its row and column sums.
  For polyominoes this is NP-hard in general and polynomial for hv-convex ones
  (Barcucci et al., Woeginger — citations UNVERIFIED, from memory, check before
  use). King-connectivity changes the constraint structure in a way that is not
  obviously either. Zero repo hits for "tomograph".
- Complexity of deciding whether a property vector (holes, perimeter, bounding
  box) is realizable at size n.

**Sentence that gets shorter:** none. Different field, different paper.

---

## 10. Tiling, and the point-contact convention underneath it

- Which polyplets tile the plane, or a rectangle? Rep-tiles? Heesch numbers?
  "Heesch" gets zero repo hits; "tiling" hits only utilization/glossary prose.
- **The subtlety that is specific to this lattice and worth more than the
  tiling questions themselves:** a polyplet realized as a closed planar region
  joins at *points*, so it is not a disk, and "tile", "hole", "boundary" and
  "simply connected" are all convention-dependent in a way the square lattice
  hides. `results/hole-free-growth-constant.md` picks a convention and
  `results/polyplet-zoo.md` notes the site-perimeter convention was
  cross-checked against percolation literature; nothing anywhere examines the
  choice itself. If any published king-lattice number ever disagrees with ours,
  this is the first place to look.

---

## Ranked, cheapest first (2026-08-04 sweep only)

1. **Idea 8**, connectivity under single-cell moves — existing oracle, n <= 10,
   one script. **The only one of the three still open.**
2. ~~**Idea 6.1**, the finite-size / central-charge fit — data already on disk,
   an afternoon, and it is the only item here that shortens an existing
   sentence.~~ **CLOSED 2026-08-07**, negatively: the data on disk cannot
   support the fit (`results/strip-growth-lambda-bounds.md`).
3. ~~**Idea 7**, king isoperimetry — small-n search, then guess-and-prove exactly
   as maxhole went.~~ **CLOSED**: search done, closed form already published as
   A235382 (`results/min-site-perimeter.md`).

Ideas 5, 9 and 10 are new-paper-sized and should not be started while the
project is closing out at a(40).

---

## Cheapest genuinely open item, already named elsewhere

Not from this sweep — `results/series-analysis-da.md` names it itself and it
is still undone: refit the 40 terms admitting a `mu_1^sqrt(n)` stretched
exponential as a fourth parameter and see whether `mu_1` is driven to 1. That
converts a named untested alternative hypothesis into a measurement.

---

## Provenance

Ideas 5-10 added 2026-08-04 from a second sweep, this one asking what is not a
counting question. No probes were written for that sweep; its only measurement
is a keyword grep over `results/ docs/ papers/`, and the sections say where the
hits landed. Everything in ideas 5-10 is unexecuted.

Probes written and run in-session 2026-08-03:
`experiments/orbit_parity_probe.py` (D4 orbit-size census by brute force,
n<=9, plus the mod-4 congruence check against `results/b006770_upload.txt`)
and `experiments/modp_bm_probe.py` (Berlekamp-Massey mod small primes on the
40 banked terms). Both are standalone and take seconds. Everything else in
this file is unexecuted.
