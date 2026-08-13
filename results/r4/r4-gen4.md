# r4-gen4 — the state after success, retargetability, and the cheapest bit

GENERATOR, round 4. Replacement for `r4-gen2`. Angle assigned by the lead so it
collides with neither predecessor: **what happens after this round succeeds, and
what it would mean for it to have succeeded.** Nothing here re-derives a closed
door from `results/triangle-r3-synthesis.md` §"Closed, with the obstruction
named" or its three floors, and nothing here re-files an `R4-G*` or `R4-G2-*`
row; where I would have, I file the successor or the kill and cite the row.

Rows are appended to `results/r4/queue.md` as `R4-G41 .. R4-G422`.

---

## §1 — Suppose every live route lands

### 1.1 The accounting, measured

Computed from `results/triangle.txt`, row n=40 (the whole row; a(40) =
56,749,893,611,764,175,164,545,926,946,127, 106 bits — which also independently
reproduces `r4-adv-cost` §3's 106-bit figure):

| height block | share of a(40) | state after every live route lands |
|---|---|---|
| H = 1..14 | **45.0107%** | exact, two-sourced (strip TM N=40, `[[strip-engine-second-source]]`) |
| H = 15,16 | **21.6439%** | exact, two-sourced (B1, banked `bd31a58`) |
| H = 17,18,19 | **22.1993%** | **modular confirmation only** — 2 primes, never recomputed as an integer |
| H = 20,21 | **7.0013%** | **one bit each** — parity, from a rule r4-inv shows is *not* independent of B1 |
| H = 22..40 | **4.1449%** | **never swept by anything**; closed-form injection; outside the Lean theorem's scope |

Three different epistemic objects, and the campaign's single currency
("share of a(40) two-sourced") flattens all of them. Written out:

- **exact-two-source tops out at 66.65%**, not at 95.85% and not at 100%. That
  is the honest ceiling of this round even in total success.
- **22.20% is confirmed, not recounted.** No integer was produced twice.
- **7.00% has two bits**, and by `r4-inv` §"forced parity clears the
  independence bar against the kink engines but **not** against B1" those two
  bits are against one rule class only.
- **4.14% has nothing** — no sweep, no second rule, no Lean coverage
  (95.85% = 100 − 4.1449, i.e. the Lean statement's scope is exactly the swept
  cells and stops where the closed-form injection starts).

### 1.2 The finding I did not expect

**The block with no confirmation of any kind (4.14%) is larger than the block
this round is spending thread-days on (H=21, 2.84%).** H=22..40 is 1.46x H=21
and 0.997x H=20. It is not on the mission statement, it has one open row in the
whole queue (`R4-G3-09`, whose cheapest kill is a grep), and its cells are
produced by *evaluating a proved-shape polynomial* rather than by counting —
which plausibly makes them the **cheapest cells in the table to two-source**,
not the most expensive. Nobody has checked, because the band framing put them
outside the round. See `R4-G42`.

### 1.3 What a skeptical referee still would not accept

Taking `docs/skeptical-reader-standard.md` and the entry ticket at face value,
after total success the surviving objections are:

1. **"You did not recount 22.20%; you checked a residue."** True, and the
   project has no defined term for the object it would be publishing. The
   tier scheme in `docs/provenance-tables.md` has four tiers and none of them
   is "confirmed mod p by an independent rule"; tier 3 (exact-arithmetic
   certificate) is close and tier 4 (reproducible measurement with an
   independent second source) is what the paper would otherwise claim.
   → `R4-G43`.
2. **"Two bits is two bits."** Already conceded in-queue (`R4-G2-24`,
   `R4-SPINPROJ-3`). What is *not* stated anywhere: after success, H=20 and
   H=21 are the only cells in the table whose confirmation is weaker than
   their neighbours' by more than an order of magnitude, and the round will
   have spent its scarcest resource there.
3. **"Your Lean theorem is about a mathematical object; your number came out of
   a C++ program."** `R4-G3-16` closed `native_decide` and `R4-G3-17` closed
   verified extraction, both correctly. The residue neither closed: **nothing
   maps the Lean definitions onto the lines of the binary.** That
   correspondence exists today only inside people's heads and in prose. It is
   a one-page artifact and it is the cheapest thing that makes the 95.85%
   mean anything operationally. → `R4-G44`.
4. **"Which height was each animal counted at?"** `R4-G3-06` is right that this
   is rank 1, and total success does not touch it: B1 produces cumulatives, so
   an attribution swap between H=17 and H=18 cancels; spin gives per-height
   parity but only at H=20,21; the strip TM covers H<=14. After every route
   lands, **height attribution at 17/18/19 is corroborated only at n <= 12**,
   by a brute grower that has not been run. → `R4-G45`.
5. **"Has anyone hostile actually read the claim sentence?"** No. The project
   has the precedent (`docs/lean-hostile-witness.md`) and has never applied it
   to the a(40) claim itself. → `R4-G46`.

---

## §2 — The generalization nobody has asked for

Four instruments are being built or used tonight. The question is what each
costs to point at another sequence this project holds. I scored them by
reading, not by running.

| instrument | retarget cost | what it reaches |
|---|---|---|
| flood-fill brute grower (`probe_cutcount_dp.py`) | **zero** — adjacency and statistic are both parameters; it grows animals and measures | any lattice, any statistic: holes, perimeter, convex, directed |
| B1 colour DP | **one line** — MEASURED, not argued: `experiments/tristruct/r3_adv3_rook_schema.py` is the schema DP with `(r-1,r,r+1) -> (r,)` and nothing else, and it passes 117 external checks | rook (polyominoes), hex; height-indexed statistics only |
| spin engine | **one language** — the window language `L_{m+1}` is stencil-specific; the ranking and the mod-4 lanes are not | any lattice with a regular window language |
| Lean recurrence | **one parameter if done now, a rewrite if done later** | every lattice whose adjacency links only columns c, c±1 |

### 2.1 The flagship: external data exists at the band's heights

`experiments/tristruct/r3_adv3_a292357.txt` (already in the tree, fetched by
r3's ADV-3) is Howroyd's A292357 a-file: fixed **polyominoes** by
(width, height, cells) for every box with width + height <= 24. A connected
animal of height H and n cells has width <= n − H + 1, so **T_sq(n,H) is
externally complete for every n <= 23 at every height**, including H = 17..21.

r3-adv3 used it at n <= 9, H <= 9 plus two deep columns (H=2,3 to n=33) and
stopped. The band heights were left on the table. Pointing the existing rook
schema DP at H = 17..21, n <= 23 gives the campaign **its first external
anchor at the band's heights** — third-party numbers, computed by other people
by other methods, against every H-indexed slot, guard and extent-accounting
path at exactly the heights where `r4-gen2`'s `R4-G2-19` identified the blind
spot. It does not test the king stencil's *content* (r3-adv3 says so and I
repeat it), and it is minutes of laptop-scale work. → `R4-G47`, and `R4-G48`
for the same comparison against the C++ B1 binary rather than the Python.

This is also the concrete answer to `R4-G3-14` ("the outside world constrains
this project at n <= 20 and nowhere else"): on the rook lattice it constrains
us at n <= 23 at *every* height, and `R4-G3-24` — which proposes hunting the
literature for published *king* values — is the harder version of the same
idea. Change the lattice instead of the search.

### 2.2 The time-critical one

The Lean crux `redReach_of_reach` depends on the stencil only through
`cut_edge_cols` — adjacency links columns c and c±1. Rook, king and hex all
satisfy that. **Parameterizing the development over the column stencil before
increment 3 costs a parameter; after increments 3–6 it costs a rewrite.** The
Lean lane is mid-development right now, which is the only moment this is cheap.
Payoff: one machine-checked sufficiency theorem covering the strip DPs used
across the polyomino, holes and directed work, instead of one covering king
animals. → `R4-G49`.

### 2.3 The instrument the campaign has invested least in is the one that
### retargets for free

The brute grower is the project's **only** incumbent-free oracle
(`r4-adv-ind` §1.2), it is a few dozen lines, and it is the one instrument
whose cost depends on n and not on the statistic being measured. The holes,
perimeter-defect and convex campaigns each rest on their own engines and it is
NOT ESTABLISHED that any of them has an incumbent-free oracle at all. One
afternoon of pointing an existing script at four campaigns. → `R4-G410`.

---

## §3 — The cheapest remaining bit anywhere

### 3.1 The one I think is the best next thread-hour

**A mod-4 congruence on a(40) from independently computed rotation-fixed
counts.** One-sided animals = (1/4)(a(n) + 2·Fix(r90) + Fix(r180)), and
`scripts/derive_related.py:101` already enforces the analogous integrality
(`assert num_free % 8 == 0`) at every n it computes. Integrality is a
**congruence on a(n)**, not a value derived from it:

    a(40) ≡ −(2·Fix(r90) + Fix(r180))  (mod 4)

`R4-G3-23` closed the symmetry route correctly — Burnside as a *value* check is
circular, because the free count is derived from a(40). It did not consider the
integrality congruence, which is not circular: the Fix counts come out of the
symtm family (hook sweep, r180 seam glue, its own step function per
`docs/dmirror-design.md` — a different geometry, not the column frontier), and
their integrality binds a(40) mod 4 whether or not anyone divides.

Why it ranks first: **2 bits on the entire row** — every height at once,
including the 4.14% nothing else touches and the 7.00% the round is spending
thread-days on — against 2 bits at 2 cells for ~11 thread-hours from
SPINPROJ-JOB-1. The binding question is price: `results/related-seqs-n33.md`
puts the D-dependent modes at 1864 core-h for n=33 and A030233 (the
rotation-only one) needs no D and is banked to n=34. **The cheapest kill is a
cost read, not a run: price Fix(r90)/Fix(r180) at n=40 off the banked symtm
scaling.** If it is out, the row degrades to §3.2, which is already banked.
→ `R4-G414`.

### 3.2 Bits already in the bank that nobody has counted

The same `%8` assertion has **already passed at every n <= 33**. That is a
3-bit check on each of a(21)..a(33) against a different engine family, and it
appears in no ledger, no provenance table and no chain-coverage claim —
`A40_VALIDATE_PASS`'s "chain coverage 19/19" chains against the same engine
family and says so (`R4-G3-14`). Free, banked, unclaimed. → `R4-G415`.

### 3.3 The free theorem-vs-engine oracle at a band height

`results/triangle-hunt-klein-parity.md`: **T(n,H) is even for n odd, H even**,
proved, holdout-verified 135/135. n = 40 is even so it says nothing about the
target cell — which is why `GEN-10` closed it as a route. As a **control on the
spin engine** it is unclaimed and free: H = 20 is even, so the theorem predicts
`T(n,20) ≡ 0 (mod 2)` for all ~20 odd n <= 40, and SPINPROJ-JOB-1 emits exactly
those cells. It is the only oracle above H = 16 in the entire campaign that is
a **theorem** rather than another engine, and it costs nothing but a comparison
inside a run already requested. → `R4-G416`.

### 3.4 The ranking, and the defence

Best use of the next thread-hour, in order, all under one hour each:

1. `R4-G416` — theorem-vs-engine at H=20, free, rides a planned run.
2. `R4-G47` — external third-party data at H=17..21, minutes, laptop-scale.
3. `R4-G2-19` (r4-gen2's, not mine) — the H-indexed `gather()` assertion.
4. `R4-G415` — count the bits already banked.
5. `R4-G414` — the cost read for the mod-4 congruence.

**The obvious objection is that none of these is the frontier.** The defence is
that the frontier is defined by the currency, and the currency is wrong. Every
item above buys protection against an error class that the frontier work
*cannot* buy protection against at any price: 1 and 3 test the H-indexed code
paths at band heights, which no n=40 run can do because there is nothing to
compare an n=40 run to; 2 is the only external number in the campaign above
n=23; 4 and 5 are the only checks that cross engine families. Spending a
thread-hour here does not slow the ladder — the ladder is blocked on dispatch
and on a build, not on cores.

### 3.5 The unit problem underneath

`R4-G21` proposes bits-against-error as a second ranking column; `R4-G3-20`
proposes lines-to-audit as a third; the two disagree about which route wins.
I think both are right and both are under-specified, because **the columns do
not add — they multiply against a common-mode ceiling.** A modular
confirmation at 2^-62 is not 62 bits of anything: it is bounded above by the
prior that the *rule* being confirmed is correct, and that prior is exactly
what the Lean theorem moves and what the stencil common mode
(`r4-adv-ind` §7) caps. Under that reading the Lean route's 95.85% and the
recount percentages are factors of one product, not addends of one sum — which
is the formal version of the sentence `R4-G3-16` says a paper must carry.
→ `R4-G418`.

---

## §4 — Second pass: what my own rows share

Three properties, and the third is a complaint about my own list.

**(a) Every row above buys confirmation from something that is not a run of our
own code at n=40.** External published values, a proved theorem, a different
engine family, a correspondence document, a hostile read. That is not a
coincidence of my angle — it is what is *left* once you assume the round's
compute succeeds. The compute answers "did the number come out twice"; nothing
in the compute answers "twice from what".

**(b) My rows are cheap because the expensive rows are already filed.** Three
generators have now worked this queue and the marginal idea is getting cheaper
and smaller, not bigger. That is a real signal about the round's state: the
generation lane's remaining value is in **re-ranking and cross-linking** what
exists, not in a 23rd mechanism. I would say so to the lead directly if the
standing instruction did not read "never stop making ideas" — and I file it as
a row rather than as advice, because it is checkable.

**(c) The entry ticket exposes the gap in my own list.** Of my 21 substantive
rows, `R4-G47`/`R4-G48` clear **level 1** (external formalisation of the object
by third parties) and none clears **level 2** at n=40, because none of them
recounts anything. `r4-gen2` closed its second pass with the same finding from
the other side ("nobody has filed a new rule class that reaches the band since
B1"). Two independent generators arriving at the same gap in their own output
is the strongest evidence in this file about where the round actually stands:
**the round has confirmation instruments and no new rule.** → `R4-G422`.

---

## §5 — What I did not establish

- The cost of Fix(r90)/Fix(r180) at n=40 (`R4-G414`) — NOT ESTABLISHED; I read
  `results/related-seqs-n33.md`'s n=33 anchors and did not extrapolate them,
  because the scaling differs per mode and guessing it is exactly the error
  class this round has been correcting all night.
- Whether the rook schema DP is affordable at H=21 with Nmax=23. Its log shows
  peak states 1,928 at H=9 for n<=9; the H=21 figure is EXTRAPOLATED nowhere
  and should be measured by the run itself, which is why `R4-G47` asks for
  `maxstates` as a reported output (`R4-G2-6`'s rider).
- Whether the strip engine is stencil-parameterized (`R4-G413`) — one grep,
  which I did not run because it needs a reading of the engine rather than a
  match.
- Whether `derive_related.py`'s `%8` assertions are non-vacuous, i.e. whether
  any Fix input is itself derived from a(n) (`R4-G415`'s kill).
