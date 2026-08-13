# r4-adv-ind — independence audit

Adversary, round 4. Standing question: **is the claim independent as claimed?**
Default verdict: *this smuggles the frontier rule back in.* Hostility ranks; it
does not exclude. Two levels every route must clear:

- **L1 semantic** — where is connectedness *defined* in this route, and could
  the hypothesised misconception reproduce there?
- **L2 algorithmic** — name the failure mode the route exhibits if its rule is
  wrong, and argue it is disjoint from union-find-over-a-frontier's.

Everything below is read off disk. Anything I could not check is marked
**NOT ESTABLISHED**.

---

## §1 The banked claim: B1 and `results/cutcount_b1/PROVENANCE.md`

Sources read: `results/cutcount_b1/cutcount_b1.cpp.59e90660` (all 434 lines),
`results/cutcount_b1/calib_run.log`, the 16 row files, and — recovered from the
parked `second-source` branch, because **neither file is present on
`triangle-structure`** — `experiments/probe_cutcount_dp.py` and
`tests/gate_cutcount_b1.py`.

### 1.1 "Never decides connectivity" — UPHELD, and for a better reason than the prose gives

The claim survives a line-by-line read, and I want to state *why* precisely,
because the prose in PROVENANCE.md ("clashes zero rather than join, there is no
union-find verdict, no stranded-component death") is a list of absences and an
absence is not an argument.

The positive argument is this. The DP does not count sets; it counts **proper
colourings**. A colouring of an occupied set `S` by `q` colours that is constant
across every king-adjacent pair is exactly a colouring constant on each
king-component, and the number of those is `q^{c(S)}` with colours chosen
independently per component — coincidences between components allowed. The DP
enumerates colourings and carries only the colour-*coincidence* partition of the
live frontier window (`successors`, lines 150-173):

- occupied cell meeting two distinct live colours → the branch dies (line 156).
  This is not a connectivity verdict; it is a colouring that violates the
  constancy constraint;
- occupied cell meeting exactly one → forced to that colour, weight 1;
- occupied cell meeting none → `b` branches of weight 1, one per live colour, and
  one branch of weight `q − b` standing for "any of the `q − b` colours that is
  not a live colour" (line 171, `{shifted(...), -b, 1, 1}`).

The `q − b` lumping is what makes stranded-component death unnecessary, and it
is *correct* rather than merely convenient: once a block scrolls out of the H+1
window it can never again constrain anything, so whether a new block coincides
with a dead block's colour is invisible to the future and is correctly absorbed
into the multiplicity `q − b`. That is the actual mechanism by which the
incumbent's hardest rule — "a component that leaves the frontier without a
future is dead" — is *not needed here*. Verified: no `union`, no `find`, no
component-death predicate, no completion test anywhere in the file.

`[q^1]` then extracts `c(S) = 1`. Connectivity is read off an exponent.

**L2 failure mode, named.** If B1's rule is wrong, the wrongness is in the
*colouring algebra* — a mis-set `b`, a missed coincidence branch, a bad canon —
and it manifests as a polynomial identity failure, i.e. wrong coefficients across
*all* `n` at once, typically with the `[q^0]` residue no longer vanishing.
Union-find-over-a-frontier's failure mode is a *set-membership* error: a
particular family of shapes admitted or rejected (stranded components, late
joins, resume boundaries). These are disjoint in kind. **L2: CLEARED.** This is
the strongest independence fact in the campaign and I could not dent it.

### 1.2 The residual common mode is the stencil, and it is not small

`gather()` (lines 128-141) hard-codes which already-processed cells are
king-adjacent to `(r,c)` in column-major order over an H-row strip: slot 0
(`r−1,c`), slot `H−2` (`r+1,c−1`), slot `H−1` (`r,c−1`), slot `H` (`r−1,c−1`).
I verified the four offsets against the processing order by hand and they are
right. **This is where "king-adjacent" is defined in B1** — and it is a
hand-written stencil, exactly as it is in the incumbent. A shared misconception
about the adjacency relation reproduces here verbatim. **L1: NOT CLEARED by the
engine itself.**

Worse, and this is the finding I would lead a referee with:

> **B1's two in-engine self-checks are provably blind to the stencil.**

- `q0_zero`: `[q^0] q^{c(S)} = 0` for every non-empty `S`, for *any* adjacency
  relation whatsoever. The check tests the `−b` cancellation algebra. It cannot
  see a wrong stencil.
- `q1eval_binomial`: at `q = 1` every colouring-sum collapses to `1` per subset,
  so the total is `C(H·W, n) − C(H·(W−1), n)` — the all-subsets binomial — again
  for *any* adjacency relation. The engine's own header sells this check as
  "exercises every transition weight at q=1, no connectivity involved" (line 18);
  that is true and it is the reason the check is stencil-blind. It is a strong
  test of the arithmetic and a null test of the semantics.

This is round 3's measured result — that structural self-checks are blind to
stencil errors — landing squarely on the banked artifact. Nobody had transposed
it to B1.

### 1.3 What *did* validate the stencil, and what did not

The source cites "Validated against brute force in
`experiments/probe_cutcount_dp.py` (5 board sizes, exact)" (line 15). I read
that file. Its `brute()` defines adjacency as the literal 3×3 neighbourhood
(`for dr in (-1,0,1): for dc in (-1,0,1)`) and does connectivity by explicit DFS
flood fill over all `2^(HW)` subsets. That is a genuine, obviously-correct,
incumbent-free oracle. It validates the **Python** DP at H,W ∈ {(2,3),(3,3),
(3,4),(2,6),(4,3)}.

The C++ `gather` is a *separate reimplementation* of that adjacency in packed
5-bit slot arithmetic. **Nothing anchors the C++ stencil to the brute force.**
I read `tests/gate_cutcount_b1.py` in full: checks A, B and F all compare the
C++ engine against `results/ns_a40/perheight` — the incumbent. Checks D, E and G
are RED controls on the *comparison plumbing* (perturbed cell located, empty
banked dir exits 3, missing row aborts) — they guard against a vacuous pass, and
they are good, but they are not controls on the rule. Check C only asserts the
two stencil-blind self-checks fired.

> **Finding: every committed check on the B1 C++ engine is a comparison against
> the incumbent. The one incumbent-free oracle in the campaign was never pointed
> at the binary that produced the banked rows.**

Counter-argument, stated fairly: a wrong C++ stencil would almost certainly
disagree with the banked triangle somewhere in 640 cells, so agreement *does*
test the stencil — unless the incumbent shares the error, which is precisely the
question. The argument is circular and cannot be broken from inside the existing
evidence. It can be broken for a few CPU-minutes; see JOB-IND-1 (§9).

### 1.4 The second difference: the agreement pins C-rows, not T — and that matters

The engine's own header is honest about this and I quote it, because it is a
lane pre-empting its adversary:

> "Accounting layer (**shared with the strip engine, disjoint from the
> connectivity rule**): sweep W = Nmax+1 columns; `C_H(n) = f_W(n) − f_{W−1}(n)`
> … then `T(n,H) = C_H − 2 C_{H−1} + C_{H−2}` exactly as strip_tm." (lines 17-20)

Two things follow, and they cut opposite ways.

**In B1's favour.** The compare in the log is over H = 1..16 *jointly* (`match=640
mismatch=0`, log line 202). The map `C ↦ T` on H = 1..16 with `C_0 = C_{−1} = 0`
is unitriangular, hence invertible. So the agreement is not the weak statement
"two engines applied the same linear map and agreed"; it forces B1's **raw
C-rows** to equal the incumbent's C-rows cell for cell, for all H ≤ 16, n ≤ 40.
The disagreement surface is the full 640-cell C table, not a projection of it.
Whoever set the compare up over all heights rather than the top two bought this
without saying so.

**Against B1.** Invertibility does not rescue the *interpretation*. If the true
relation were `T = L(C)` and both engines used the same wrong `L′`, both publish
`L′(C)` and agree, and the agreement establishes `C^{B1} = C^{prod}` — which is
true and which is not `T`. The step from C-rows to T is **common-mode and
verified by proof only**. The proof is three lines (`C_H(n) = Σ_h (H−h+1)·T(n,h)`
because a shape of exact height `h` sits in `H−h+1` vertical positions; the
second difference in `H` of the ramp `max(0, H−h+1)` is the Kronecker delta at
`h = H`), it is not in dispute, and I am not claiming it is wrong. I am claiming
it is **not independently verified**, and that the phrase in PROVENANCE.md —
"**21.64% of a(40), recounted exactly by a second rule**" — over-states by one
step. What was recounted by a second rule is `C_15`, `C_16` and their
predecessors. `T(40,15)` and `T(40,16)` were then produced from those by a
formula both routes share.

Precise replacement sentence a referee would accept:

> B1 independently reproduces the height-≤H cumulative counts `C_H(n)` for all
> H ≤ 16, n ≤ 40, by a rule that never decides connectivity; `T(40,15)` and
> `T(40,16)` follow from those by an elementary identity common to both routes.

> **Correction to §1.4, entered after §2 was researched — read §2.1 before
> quoting §1.4.** I checked the production Go engine for a second-difference
> layer and there is none: the incumbent gets "bounding box height exactly H"
> from touch-top/touch-bottom flags carried in the frontier key
> (`orchestrator/runref.go:42`), not from a linear map on cumulative rows. So
> the C→T step is *not* common-mode with the incumbent, and the 640-cell
> agreement therefore **does** test it. §1.4's "against B1" paragraph stands as
> a description of the challenger routes' shared form but does **not** apply to
> the banked comparison. The replacement sentence offered at the end of §1.4 is
> withdrawn; §2.1 has the correct one.

### 1.5 Does `results/triangle-r3-adv-independence.md` survive the rows being committed? — YES, with one internal tension it should own

Re-read in full. The file's central concession is:

> "A superset state space alone would NOT be independence — the incumbent's
> object rides inside it — which is why the level-2 verdict below rests on the
> dynamics and failure modes, not on the state census." (§1)

**Verdict: survivable, and slightly under-stated in exposition rather than in
substance.** The dynamics argument that carries the weight is not a census
claim at all — the colour DP's three branches (extend/retire, join-at-birth,
clash-drop) *provably* never identify two previously-distinct classes, which I
re-verified against `successors()` in the C++ (§1.1): no successor of a state
ever maps two distinct incoming slot-ids to one outgoing id. `canon()` relabels;
it never merges. That is a theorem about the transition set and it is untouched
by containment. Retreating from the census to the dynamics is the correct move
and it lands on solid ground.

Under-stated in this respect: the concession names the worry ("the incumbent's
object rides inside it") but never closes the sharper form of it — *if the
colour DP restricted to non-crossing states were dynamically isomorphic to the
incumbent, B1 would be the incumbent plus dead weight.* The dynamics bullet
does refute that, but the file leaves the reader to connect them. A referee who
reads §1's concession and stops has been handed the objection without the
answer.

**The tension I would put to that file's author.** §1 classifies the shared
residue as "frontier separation … and the weakest tier of sharedness, the
adjacency definition itself". §2 then measures that with NW adjacency
deliberately dropped, *both* structural self-checks still pass while `[q¹]` is
wrong at n = 2..10. Those two sentences cannot both be right about ranking. The
adjacency definition is not the weakest tier of sharedness; it is the **most
consequential** shared element in the entire campaign, because it is
semantically load-bearing, hand-implemented twice, and invisible to every
structural check either route runs. §2 knows this and §1's ranking language
contradicts it. This is a wording defect in an otherwise careful file, but it is
the wording a phase-2 brief would inherit.

**Credit where the file pre-empted me.** §2's RED-control finding is exactly my
§1.2, found first and measured rather than argued, and its prescription is
right: *"A phase-2 gate plan must include the brute battery per built binary as
a first-class RED, not the two identities alone."* My §1.3 finding is that the
banked run **did not do this** — the recommendation exists and the committed
gate (`tests/gate_cutcount_b1.py`, checks A/B/C/F) does not implement it.
Round 3 identified the gap; round 4 banked a result across it.

### 1.6 Provenance caveats — a note the file already makes, correctly

PROVENANCE.md states its own worst fact plainly (§"Provenance caveat, stated
plainly"): the producing binary matches neither committed version, its diff
against `7b13137` is the *removal* of `--modp`, and its gate battery predates
the fail-closed exit codes. I checked this is not worse than stated. It is
slightly better than stated in one respect and slightly worse in another:

- Better: the gate's fail-closed additions (exit 3 on empty banked dir, exit 2 on
  mismatch) are controls on the *compare*, and the production run did not rely on
  the compare for its output — the rows are the output, the compare is a witness.
  The compare printed `match=640 mismatch=0` explicitly, so the "silent 0 match,
  0 MISMATCH" hazard the gate was written to catch demonstrably did not occur.
- Worse: `--modp` removal means the run has **no residue cross-check of its own
  arithmetic**. The 256-bit wrapping arithmetic (lines 22-24) is justified by a
  bound argument in a comment, and `fits_i128` is checked per cell (line 289),
  which is a real guard. But the ring-hom argument `Z → Z/2^256` is asserted in
  the header, not gated.

### 1.7 §1 verdict

| level | verdict |
|---|---|
| L1 semantic (where connectedness is defined) | **PARTIAL.** The *extraction* of connectivity is genuinely disjoint from union-find. The *adjacency relation* is a second hand-written stencil and is fully common-mode. |
| L2 algorithmic (disjoint failure modes) | **CLEARED** for the connectivity rule: colouring-algebra failure vs. set-membership failure are different in kind. **NOT CLEARED** for the stencil and for the C→T accounting, whose failure modes are identical by construction. |

---

## §2 The common-mode finding in `r4-inv.md` §2 — one claim established, one refuted in the part that matters

The lead asked me to establish or refute two statements and say what each does
to the banked H = 15, 16 result. Answers first, then the work.

| claim | verdict |
|---|---|
| The height second difference is common-mode across B1, the strip engine and spin — one formula, one semantics. | **ESTABLISHED, and B1's own source says so.** |
| That common mode endangers the banked H = 15, 16 recount. | **REFUTED. The incumbent does not use a second difference.** |
| Forced parity clears independence against the kink engines. | **ESTABLISHED.** |
| Forced parity does not clear it against B1, because `[q¹]` in `Z[q]/(q²)` and `q = 2` in `Z/4` are two extractions from one identity. | **ESTABLISHED, and r4-inv under-states its own concession.** |

### 2.1 Common-mode among the challengers: yes. Common-mode with the incumbent: no.

**Established half.** B1's header self-declares it, and this is a lane naming its
own shared layer before an adversary got to it:

> "Accounting layer (**shared with the strip engine, disjoint from the
> connectivity rule**) … `T(n,H) = C_H − 2 C_{H−1} + C_{H−2}` **exactly as
> strip_tm**." — `cutcount_b1.cpp.59e90660:17-20`

Spin uses `N_H = A_H − 2A_{H−1} + A_{H−2}` (`r4-inv.md` §1.1). Same form, same
semantics — "extent at most H" differenced into "extent exactly H". r4-inv's
sentence *"it is one formula and one semantics, and a misconception in it would
hit all three routes identically"* is correct as written.

**Refuted half — and this is the finding that changes the standing of the banked
cells.** r4-inv's mitigation for the common mode is *"the layer is separately
two-sourced in the strip engine's own accounting"*, which is weak: two
implementations of one formula catch typos, not misconceptions. The real
mitigation is much stronger and nobody in the round has stated it.

**The production engine has no second-difference layer at all.** I searched the
Go orchestrator, core and worker packages for cumulative-then-difference
accounting and found none. The incumbent's per-height row is produced by the
sweep for that height directly (`sweepHeight` / `sweepHeightKink` return `hTri`,
"contributions from this height only", `orchestrator/sweep.go:687,911`), and
"bounding box height exactly H" is enforced *inside the state key*:

> "(boundary + **touch-top + touch-bottom**) for height H" —
> `orchestrator/runref.go:42`

Two mechanisms, not one. The incumbent decides exact height by carrying two
reachability flags through the frontier; B1 and spin decide it by a linear map
on cumulative counts. A misconception about extent semantics has to reproduce in
*both* to survive, and they have no structure in common.

Consequence, and it upgrades the banked result rather than damaging it:

> The `match=640 mismatch=0` compare over H = 1..16 is an **independent test of
> the second-difference accounting itself**, not merely a test downstream of it.
> Because the map `C ↦ T` on H = 1..16 is unitriangular and therefore
> invertible (§1.4), the agreement simultaneously pins B1's raw `C`-rows and
> validates the extent identity against a route that gets extent from
> touch-flags.

This retires the C→T entry in §1.7's L2 column and withdraws the replacement
sentence I offered at the end of §1.4. The corrected sentence a referee should
be given is:

> `T(40,15)` and `T(40,16)` were reproduced by a rule that never decides
> connectivity and that obtains bounding-box height by a completely different
> mechanism from the production engine. The one thing the two routes still
> share is the king-adjacency stencil.

**Scope limit, stated so nobody over-reads this.** The refutation covers the
*banked* cells, where the comparand is the kink engine. It does **not** cover a
future B1-vs-spin agreement: those two do share the second difference, and
r4-inv is right to bold it there.

### 2.2 Forced parity: r4-inv is right, and under-states its own concession

The claim — B1 computes `A_n(q) = Σ_S q^{c(S)}` in `Z[q]/(q²)` and reads `[q¹]`;
spin evaluates the same `A_n` at `q = 2` in `Z/4` and reads the residue; "two
extractions from one identity" — is correct.

It is worse than r4-inv says, in one direction and better in another, and the
decomposition matters because the spin gate oracle *is* B1.

**Worse.** The relationship is not merely "two extractions from one identity".
Spin **is B1's DP specialised to q = 2**. B1 carries the colour-coincidence
*partition* because `q` is an indeterminate; spin carries a concrete colour
*string* because `q = 2` makes the colours nameable. The per-cell rule is
identical in both — a new occupied cell must agree with every occupied
king-neighbour, else the branch dies. r4-inv writes:

> "The state bases differ genuinely … and the arithmetic differs … so
> implementation failures are largely disjoint — but if the cancellation
> identity itself were wrong, both die together."

"Implementation failures largely disjoint" is right. But the exposure is not
confined to "the cancellation identity"; it extends to **the stencil and the
colouring semantics**, which are one rule shared by both routes. If `gather()`
is wrong, spin reproduces the error, because spin's clash rule is the same
clash rule.

**Better.** The `q = 2` specialisation genuinely discards B1's most error-prone
machinery. Spin has no `(q − b)` inclusion–exclusion weight, no negative
coefficients, no `Z[q]/(q²)` truncation, no 256-bit wrapping arithmetic and no
`fits_i128` bound argument. Every one of those is a live B1 failure carrier with
no expression in spin. So spin is a real check on B1's *algebra* while being no
check at all on B1's *rule*.

The clean three-way statement, which is what a referee should be handed:

| layer | B1 vs kink | spin vs kink | spin vs B1 |
|---|---|---|---|
| connectivity decision | disjoint | disjoint | **identical rule** |
| king-adjacency stencil | **shared** | **shared** | **shared** |
| extent accounting | disjoint (§2.1) | disjoint (§2.1) | **shared formula** |
| coefficient arithmetic | disjoint | disjoint | disjoint |

Read down the "spin vs B1" column: spin's independence value is entirely against
the kink engines, exactly as r4-inv concludes. Read across the stencil row:
**every route in the campaign shares one hand-written adjacency relation, and no
committed gate on any built binary checks it against an incumbent-free oracle.**

### 2.3 What this does to the standing of banked H = 15, 16

- **Strengthened**, by §2.1: the extent accounting is independently tested, not
  common-mode, because the incumbent uses touch-flags.
- **Unchanged**, by §1.1: the connectivity rule is genuinely disjoint and I
  could not dent it.
- **Not improved**, by §1.2/§1.3/§2.2: the stencil remains a single point of
  common mode, tested only against the incumbent, invisible to every self-check,
  and shared by every route that could serve as a cross-check.

The banked claim is in better shape than round 4 has argued for it and its one
real weakness is not the one round 4 flagged.

---

## §3 The two batteries built tonight — one sees its error class, one tests code it did not touch

The lead's question: *do these batteries contain a control that sees the error
class they are advertised to see, or do they pass a broken engine?* Different
answers for the two artifacts.

### 3.0 First, the evidence gap, because it applies to both

**No gate log for either artifact exists on disk.** `experiments/tristruct/`
contains `r4_perf_fastmodp.patch` and `r4_spin_engine.cpp` and no `.log` beside
either. The queue's own row for the spin engine still reads:

> "`experiments/tristruct/r4_spin_engine.cpp` written (1113 lines, C++20 …
> **UNCOMPILED**) … **OPEN — needs the lead to build and gate**"
> — `results/r4/queue.md`, row R4-SB1

and r4-perf's job block says of the patch: *"Written by r4-perf, **NEVER
COMPILED, NEVER RUN**."* The gate outcomes reported to me — seven GREEN for the
patched B1, `compared=49 mismatch=0` for spin, `12/12/4` for the mutants — are
therefore **NOT ESTABLISHED as artifacts**. I audit the batteries as designed
and I take the outcomes as reported, but under this project's own standard a
gate result with no log is asserted, and the round's write-ahead rule says the
same thing. This is the lead-facing half of my role and I file it as such: two
binaries were built and gated with no run record, and the queue row that says
"needs the lead to build and gate" was never closed.

### 3.1 The spin battery — GATE 1 sees the class; GATE 0's oracle is not independent

**GATE 1 does contain the designed control and it is doing the work claimed.**
Round 3's measured obstruction is that a state census cannot see a *symmetric*
stencil error at all: rook and king closures reach identical state sets at every
H ≤ 8. The answer in the battery is that the mutant fixtures are **value-level,
not census-level** — round 3 says so in the same breath it records them
(`results/triangle-r3-spin.md:49`: "drop-NW, drop-SW, rook stencil mutants flip
12/12/4 cells at n ≤ 7 vs self-grown truth (0 false passes); value-level, not
census-level"). The rook mutant is the symmetric case, it flips 4 cells, and 4 >
0 is exactly the thing a census could not deliver. **The control is real.**

Two things to attach to it.

1. **It is the thinnest control in the battery and it guards the most dangerous
   class.** Drop-NW and drop-SW are asymmetric errors and flip 12 cells each;
   rook is the symmetric error and flips 4. The battery's sensitivity to the
   error class it most needs is a third of its sensitivity to the classes it
   needs least, over a 28-cell comparison set. That is not a defect — it is the
   correct number and it was measured — but a phase-2 brief should not read
   "12/12/4 GREEN" as three equally strong controls.
2. **A mutant fixture proves the detector has power. It does not prove the
   detector is pointed at an independent standard.** GATE 1 establishes that
   spin's output *changes* when spin's stencil is broken. It says nothing about
   whether spin's unbroken stencil is right, because the comparison is against
   B1, and §2.2 established that spin and B1 share one stencil and one colouring
   semantics. **A stencil error common to spin and B1 passes GATE 0 and GATE 1
   both, with the mutants firing correctly throughout.**

r4-spinbuild saw this and wrote it down before anyone asked, in its §3(k):

> "**The binary has no self-contained ground truth.** … Everything the C++
> checks itself against is the oracle. **Recommendation: the lead should re-run
> `r3_spin_pipeline.py` (6.5 s, laptop-scale, self-contained — it grows its own
> animals and brute-forces its own Z) alongside GATE 0**, so the gate chain is
> anchored on something that does not depend on the recovered B1 rows being
> right."

That recommendation is the fix for the exposure I just named, it costs 6.5
seconds, GATE 0's own text repeats it as a required alongside-step, and **the
reported GATE 0 result does not mention it.** Whether it was run is NOT
ESTABLISHED. If it was not, GATE 0 as executed is a two-implementation check of
one rule.

**A smaller point on the headline number.** The reported figure is "49 cells
zero mismatch". GATE 0's spec expects `compared=49 mismatch=0 compared_hlen=28
mismatch_hlen=0`. Only the 28 `hlen` cells are the Python's validated set; the
other 21 are the H > n structural zeros whose vanishing r4-spinbuild derived
itself and flagged as its own derivation (§3e: *"That derivation is mine;
neither the Python nor r4-inv states it"*). Quoting 49 attributes to the Python
reference 21 cells it never validated. The load-bearing number is 28.

### 3.2 The patched B1 battery — the gates are GREEN on code the patch does not touch

**Verdict: the seven gates do not test the error class the patch could
introduce, and r4-perf says so in the job block.** The patch is L0-L4:
edge specialisation, structure-of-arrays payload, Shoup reduction, lazy column
sum. All of it lives in the `--modp` path. `tests/gate_cutcount_b1.py` exercises
the exact-payload paths only — checks A, B and F run `cutcount_b1 <Hmax> <Nmax>
BANKED` and `--assemble`; nothing in the file passes `--modp`. r4-perf's own
words:

> "**RED-gate** … Note it covers the EXACT paths only — the patch does not touch
> them, so a gate failure here means the patch broke something it had no
> business touching, which is exactly the signal wanted."

That is the correct description of a **regression** control on untouched code,
and it is a real if narrow thing to have: it proves the patch did not corrupt
the exact path by accident. Reporting it as "seven gates GREEN including three
REDs" invites the reading that the patch was validated. It was not. The control
that would validate it is `RED-exact` — `cmp` of patched vs unpatched `--modp`
rows at H = 13, 14, 15, byte for byte — which is the whole point of levers that
claim bit-identical output, and which requires PERF-JOB-1 on dalby. There is no
`r4_perf_fastmodp.log`. **RED-exact: NOT RUN.**

Two further gaps in the modp path, both named by other lanes and neither closed:

- **The modp path has one self-check, and it is the stencil-blind one.**
  r4-perf: *"`q0_zero` fires per height in modp (line 356, exit 2). The q=1
  binomial identity is still absent in modp (r4-a section 1b); record that as a
  known gap in the receipt rather than letting the log's silence imply it
  passed."* Correct and well-flagged. Note from §1.2 that both identities are
  stencil-blind anyway, so what modp loses is arithmetic coverage, not semantic
  coverage — it had none of the latter to lose.
- **`FATAL succ_overflow` / `FATAL m1_not_bit` must not fire at H ≤ 15.** These
  are new guards. A guard that never fires in the only run it has had is an
  untested guard; r4-perf asks for the negative observation to be recorded,
  which is the right ask and is the weaker half of a fail-closed design.

### 3.3 Answering the question as posed

| battery | contains a control that sees its advertised error class? | could it pass a broken engine? |
|---|---|---|
| spin GATE 0 + GATE 1 | **Yes.** The value-level rook mutant is the designed answer to round 3's symmetric-stencil blindness and it flips 4 cells, where a census flips none. | **Yes, for one class:** a stencil or colouring-semantics error shared with B1, because B1 is the only oracle. Closable in 6.5 s by the alongside-run the lane already prescribed. |
| patched B1, seven gates | **No.** Every check exercises the exact path; the patch is entirely in `--modp`. | **Yes**, trivially — a `--modp`-only miscompute passes all seven. The control that would catch it (`RED-exact` byte diff) has not been run. |

---

## §4 The Lean route — the upgrade sentence over-reaches by exactly one word, and §0.3's correction is itself a misreading

Read: `results/r4/r4-lean.md` in full, `results/triangle-r3-l3-proofscope.md`
§§4.2, 7, and the two Lean anchors r4-lean cites (`Finite.lean:61-76`,
`Compute.lean:207`).

### 4.1 The (a)+(b) structure is sound and the scope disclaimer is honest

Statements (a) "the abstract recurrence counts what we say", (b) "the algorithm
implements (a)", (c) "the compiled kernels implement (b) — not proposed". This
is the right decomposition, and r4-lean's closing paragraph gives the scope
limit without being asked:

> "The theorem is about the rule, not about the binaries: a fault in one
> compiled kernel, on cells only that kernel swept, is untouched by it. Program
> verification of the optimized C++ … is not proposed, at any price."

I have no objection to (a)+(b) as the target. **L1 for the Lean route: CLEARED,
and it is the only route in the campaign that clears L1 outright** — connectivity
is `Relation.ReflTransGen` of `kingAdj` from `Defs.lean:29`, and `kingAdj` is a
Mathlib-idiom `|Δx| ≤ 1 ∧ |Δy| ≤ 1 ∧ (p ≠ q)` predicate rather than a
hand-written frontier stencil. That is the *one* place in this whole campaign
where the adjacency relation is written in a form a referee can check by eye
against the definition of a king move, and it is why §6 ranks this route first
on independence despite reaching nothing.

**L2: not applicable in the usual sense, and that is a strength, not a dodge.**
A proof has no failure mode of the "wrong family of shapes admitted" kind; it
has `sorry`s, bad definitions and axiom leakage, all of which are mechanically
detectable. The `#guard_msgs` axiom audit in the plan is the correct control.

### 4.2 The upgrade sentence — over-claims on scope, and smuggles a premise

The sentence in question, quoted whole:

> "The strip-transfer-matrix's 469 cells, the two production kernels, and
> `symtm` agree; today that agreement is discounted wholesale, precisely because
> they agree *as implementations of a rule that was itself unproved*. With the
> rule proved, the same agreements become what they always looked like:
> cross-checks between independently written codebases, **whose bug modes are
> disjoint**, of a rule that is now a theorem."

Three objections, in descending order of seriousness.

**(i) "whose bug modes are disjoint" is smuggled.** Nothing in (a)+(b) makes two
frontier implementations' bug modes disjoint. The chartered objection is
*precisely* that they are not disjoint — both decide connectivity by union-find
over a frontier against the previous column's labels. Proving the rule removes
the *rule* misconception and leaves the *implementation* correlation exactly
where it was. The clause asserts as a consequence of the theorem something the
theorem does not touch, and it is the load-bearing clause of the sentence:
delete it and the upgrade shrinks to "cross-checks between independently written
codebases of a rule that is now a theorem", which is true, useful, and much
smaller. r4-lean's own final paragraph concedes the point ("a fault in one
compiled kernel … is untouched by it"), so the file contains its own refutation
two paragraphs down. **Verdict: the sentence would not survive a referee. The
same sentence with four words deleted would.**

**(ii) The scope is wrong: the strip TM does not implement the rule being
proved.** The theorem's completion lemma is `G1: one class + both flags ⟺
KingConnected ∧ height exactly H` — i.e. it proves the *touch-flag* mechanism,
which is what the production kink kernels use (`orchestrator/runref.go:42`, §2.1).
The strip transfer matrix gets exact height from the second difference over
cumulative rows, a different mechanism the theorem says nothing about. So
proving (a)+(b) upgrades agreements among the **two production kernels** and
whatever else implements the same recurrence; it does **not** upgrade the strip
TM's 469 cells, and `symtm`'s status is NOT ESTABLISHED (I did not determine
which extent mechanism it uses). A referee who reads the list and then reads G1
finds the mismatch immediately.

**(iii) "discounted wholesale … become what they always looked like" over-states
the size of the move.** The agreements are discounted for two reasons: the rule
was unproved, *and* the implementations share a rule class. The theorem retires
the first. Going from "discounted for two reasons" to "discounted for one" is a
real gain and should be sold as one.

**And the pull-quote problem.** This sentence, three paragraphs earlier —

> "Once that theorem holds, the objection is closed for **every cell the sweep
> touched — H = 3..21, 95.85% of a(40) — with no enumeration performed at all.**"

— says "the objection is closed", unqualified and bolded, and the qualifier
("the proof closes the rule half of the objection") arrives 20 lines later. Both
numbers are right: I recomputed them off `results/ns_a40/` and got 95.8551% for
H = 3..21 and 21.6439% for the two banked cells. The arithmetic is not the
problem; the bolded unqualified verb is. Anyone lifting the highlighted sentence
into a brief propagates a claim the same file retracts.

### 4.3 The `stateOf` correction — the substantive point is right, the charge of error is not

r4-lean §0.3 says r3's census theorem "as worded is false" because it states
connectivity *in S* where the invariant must be connectivity in the prefix.

**Substantively correct:** the DP invariant must be prefix-connectivity, two
column-`c` cells can be joined only through columns `> c`, and a left-to-right
fold cannot see that. No dispute.

**But the charge against r3 does not hold on r3's text.** Read
`triangle-r3-l3-proofscope.md:94-97` whole:

> "`stateOf S c` = (partition of S's column-c cells by connectivity-in-S,
> flags); theorem: after k columns the DP's (state → count-by-cells) table
> equals the **census of viable k-column prefixes under `stateOf`**"

`stateOf` is applied to prefixes. `S` is therefore bound to the prefix, and
"connectivity-in-S" *is* prefix-connectivity. The very next lemma in the same
list confirms the binding:

> "*L-partition* (the crux): connectivity of **S ∪ M** restricted through the
> cut is determined by (partition of the boundary column, M)" (lines 100-102)

`S ∪ M` — S is the past, M is the future. r3 uses `S` for the prefix
consistently across both statements. r4-lean read `S` as the full set and found
a slip that is not in the text.

**Why this matters and is not pedantry.** Queue row **R4-LEAN-3** proposes to
"audit every r3 skeleton for the prefix-vs-global invariant slip found in §0.3".
That is a wave of work premised on an error I cannot find. **Re-scope R4-LEAN-3
to the half of it that stands** — §0.2's finding that the r3 L5 lane
re-derived `canonical_x_le` from scratch when it was already committed and
sorry-free at `Finite.lean:82`, which is a genuine and expensive duplication and
worth a systematic sweep.

r4-lean's other two corrections **do** hold and I checked both: `Tc_eq_T`
(`Compute.lean:207`) is a container change with no column, cut, state or
induction in it, so "half of (a) already exists" was wrong and the cost anchor
built on it was void; and `exists_adj_cross_of_reflTransGen`
(`Finite.lean:61-76`) is exactly the Finset-geometry column-cut induction r3
filed as non-existent. Finding a 16-line committed calibration anchor that a
prior round declared absent is the most useful thing in that deliverable.

### 4.4 Level verdict for the Lean route

| level | verdict |
|---|---|
| L1 semantic | **CLEARED, uniquely.** Connectivity is `ReflTransGen kingAdj` from the definition layer; no cut, no frontier, no labels, no completion predicate. The only adjacency relation in the campaign not written as a hand-rolled stencil. |
| L2 algorithmic | **CLEARED by category.** No shape-family failure mode exists; the failure modes are `sorry`, bad definition, axiom leak — all mechanically detectable, and the plan has the `#guard_msgs` audit for the third. |
| standing | **Everything is UNCOMPILED and the lane says so in bold at the top.** Zero Lean has been run. The route's independence is impeccable and its evidence is nil. |

---

## §5 One sentence a skeptical reader accepts, one they reject — per live route

Written in each route's own terms, per the brief. The accept sentence is what I
would put in front of a referee tomorrow. The reject sentence is what is
currently written or implied somewhere in the round's files.

### B1 residue ladder

**Accepted.** *"An engine that never decides connectivity — no union-find, no
component death, no completion predicate — reproduced the cumulative height-≤H
counts `C_H(n)` for every H ≤ 16 and n ≤ 40, from which `T(40,15)` and
`T(40,16)` follow by an identity the production engine does not use; 640 cells,
zero mismatch."*

Why they accept it: every clause is checkable off the committed source and the
committed log, the mechanism (colourings weighted `q^{c(S)}`, read at `[q¹]`) is
a two-line identity a referee can verify at the desk, and the extent accounting
is not shared with the comparand.

**Rejected.** *"21.64% of a(40), recounted exactly by a second rule."*
(`results/cutcount_b1/PROVENANCE.md`)

Why they reject it: "a second rule" is one rule short of the truth. The two
routes share a hand-written king-adjacency stencil, and no committed check on
the C++ binary tests that stencil against anything but the incumbent. A referee
asks "second rule for *what*?" and the honest answer is "for the connectivity
decision and the extent accounting, but not for the adjacency relation".

### Spin parity

**Accepted.** *"For `T(40,20)` and `T(40,21)`, a DP whose entire state is a
three-letter colour string and whose only arithmetic is a mod-4 add — with no
partition, no label, no union and no death rule anywhere in it — agrees with the
kink kernel's parity."*

Why they accept it: `2^{c(S)} ≡ 2 (mod 4)` iff `c = 1` is checkable in one line,
and the state object shares no structure at all with a frontier partition.

**Rejected.** *"…a second rule class against B1 as well."* (Nobody has written
this sentence, and r4-inv explicitly refuses to: *"It does not clear the bar
against B1, and nobody should claim it does."* I list it because it is the
sentence a summariser would produce from "two engines agreed" and because §2.2
shows it is worse than r4-inv's own concession — spin **is** B1's DP specialised
to `q = 2`, sharing the stencil and the colouring semantics outright.)

### The Lean proof

**Accepted.** *"King-connectedness is Mathlib's reflexive-transitive closure of
a king-adjacency predicate written from the definition; the frontier recurrence
is proved to count exactly the connected `n`-cell sets of bounding-box height
exactly `H`; no cut, frontier, label or completion predicate appears anywhere in
the statement."*

Why they accept it: it is the only place in the campaign where the adjacency
relation itself is stated in a checkable form, which is the one gap §1-§3 could
not close by any amount of recounting.

**Rejected.** *"…cross-checks between independently written codebases, whose bug
modes are disjoint, of a rule that is now a theorem."* (`results/r4/r4-lean.md`
§5)

Why they reject it: the theorem cannot make two union-find-over-a-frontier
implementations' bug modes disjoint; that was the objection, not the conclusion.
See §4.2(i).

---

## §6 Independence claims that would not survive a referee, ranked

Ranked by how much work the claim is doing × how far it is from what the
evidence supports. Each is quoted from the file that makes it.

1. **"cross-checks between independently written codebases, whose bug modes are
   disjoint, of a rule that is now a theorem"** — `r4-lean.md` §5. The strongest
   sentence in the campaign, and four of its words are unearned. It converts a
   rule-level theorem into an implementation-level guarantee, which is exactly
   the conversion the chartered objection forbids. Fix: delete "whose bug modes
   are disjoint" and narrow the codebase list to the two production kernels
   (§4.2 ii). Cost of the fix: nothing. Cost of not fixing it: it is the sentence
   most likely to end up in a paper.

2. **"21.64% of a(40), recounted exactly by a second rule"** —
   `results/cutcount_b1/PROVENANCE.md`. Banked, and therefore the most consumed
   claim in the round. Correct about connectivity and extent; silent about the
   shared stencil, which is the one common-mode element no self-check in either
   route can see. Fix: §1.4's replacement sentence, plus JOB-IND-1.

3. **"Once that theorem holds, the objection is closed for every cell the sweep
   touched — H = 3..21, 95.85% of a(40)"** — `r4-lean.md` §5, bolded and
   unqualified, retracted 20 lines later. A pull-quote hazard rather than a
   wrong belief.

4. **"the weakest tier of sharedness, the adjacency definition itself"** —
   `results/triangle-r3-adv-independence.md` §1. Contradicted by §2 of the same
   file, which measures that the adjacency definition is the one thing both
   self-checks are blind to. The ranking language is inherited by every
   downstream brief. Fix: one word — "weakest" → "only, and the most
   consequential".

5. **"seven gates GREEN including three REDs" for the patched B1 binary** — the
   round-4 dispatch summary. The seven gates exercise the exact-payload path;
   the patch is entirely in `--modp`. r4-perf labelled this correctly in its own
   job block; the summary did not carry the label. Fix: report it as a
   regression control and run `RED-exact`.

6. **"the layer is separately two-sourced in the strip engine's own
   accounting"** — `r4-inv.md` §1.4, offered as the mitigation for the
   second-difference common mode. Two implementations of one formula catch
   typos, not misconceptions. The real mitigation is stronger and different
   (§2.1): the incumbent does not use the formula at all. Fix: replace the
   mitigation with the right one — this *raises* r4-inv's conclusion.

7. **"the r3 skeleton's `stateOf` is stated wrong, and the wrong version is not
   provable"** — `r4-lean.md` §0.3. The invariant claim is right; the charge
   against r3's text is not (§4.3). It is here because queue row R4-LEAN-3
   budgets a wave against it.

8. **"GATE 0 … 49 cells, zero mismatch"** — round-4 dispatch summary. 28 of the
   49 are the Python-validated set; the other 21 are structural zeros
   r4-spinbuild derived itself and flagged as unvalidated by anyone else
   (§3(e)). Minor, and the binary reports the two counts separately precisely so
   this does not happen.

**Not on this list, deliberately.** "B1 never decides connectivity" (§1.1,
upheld and strengthened), "spin's parity clears independence against the kink
engines" (§2.2, upheld), and r4-inv's and r4-spinbuild's self-flagged weaknesses
(§8) — those are claims that survive.

---

## §7 What tonight's banked 21.64% settles, and what it does not

Recomputed independently off `results/ns_a40/`: `T(40,15) + T(40,16)` is
**21.6439%** of `a(40)`, and the two values match
`results/cutcount_b1/PROVENANCE.md` to all 31 digits.

### It settles

- **That the connectivity decision in the production kernels did not corrupt
  those two cells.** A rule with no union-find, no component death and no
  completion predicate produced the same numbers. This is the chartered
  objection's core, and for these two cells it is answered. Nothing in my read
  dented it.
- **That the extent accounting is not the weak link it was thought to be.** The
  incumbent gets exact height from touch-flags in the frontier key and B1 gets it
  from a second difference on cumulative rows; the 640-cell agreement tests both
  against each other (§2.1). This was not known before tonight and it is a
  genuine upgrade to the banked claim.
- **B1's C-rows for every H ≤ 16, not just the two headline cells** — by
  invertibility of the unitriangular `C ↦ T` map over H = 1..16 (§1.4). The
  disagreement surface was 640 cells wide, not 2.

### It does not settle

- **The king-adjacency stencil.** Shared by every route in the campaign except
  the Lean statement; invisible to `q0_zero`, to `q1eval_binomial`, and to every
  state census (round 3: rook and king closures are census-identical at H ≤ 8);
  and never checked against an incumbent-free oracle for the C++ binary that
  produced the rows. This is now, by elimination, **the whole of the residual
  common mode for H = 15, 16.**
- **Anything about H = 17..21.** B1 stops at 16. 21.64% is 21.64%.
- **The implementation half for these cells beyond a single agreement.** Two
  engines agreeing is two engines agreeing; the run's binary matches no committed
  version, and its `--modp` self-cross-check was removed before the run.
- **That the DP's arithmetic is residue-checked.** The 256-bit wrapping /
  ring-hom argument is a header comment plus a per-cell `fits_i128` guard. The
  `--modp` mode that would have provided an independent congruence check on the
  same rows exists in committed source (`7b13137`) and was deleted from the
  producing binary.

### The one-sentence version

> The banked 21.64% closes the connectivity-rule objection and the extent
> objection for two cells and leaves exactly one thing shared with the
> incumbent: a hand-written king-adjacency stencil that no check in either
> route can see.

---

## §8 Process: where lanes pre-empted me

This belongs on the record as evidence about the round, per the brief.

- **`r4-spinbuild`** is the clearest case. Its §3 is twelve labelled exposures
  written against its own artifact, and (j) and (k) are the two objections I
  arrived at independently — the common-mode second difference, and *"the binary
  has no self-contained ground truth … everything the C++ checks itself against
  is the oracle"* — each with the fix attached. It also flags its own
  unvalidated derivation (§3e, the H > n structural zeros: *"That derivation is
  mine; neither the Python nor r4-inv states it"*) and its own untested code
  paths (§3l). I found nothing in that file it had not already found. The one
  thing I added is that its §3(k) recommendation appears not to have been
  executed.
- **`r4-inv`** states the common-mode caveat *"in bold"* on its own initiative
  (§1.4), refuses the over-claim available to it (*"It does not clear the bar
  against B1, and nobody should claim it does"*, §2), and tells the reader
  exactly what a referee should not be told (§2, final paragraph). My §2 raises
  its conclusion rather than lowering it.
- **`r4-perf`** labelled its own gate battery as covering *"the EXACT paths
  only"* and asked for the absent `q=1` identity to be *"record[ed] as a known
  gap in the receipt rather than letting the log's silence imply it passed"*.
  That is a lane writing the adversary's paragraph for them.
- **`r4-lean`** opens with **"Standing label: I ran no compute of any kind …
  Everything Lean in this deliverable is UNCOMPILED"** and closes §5 with the
  scope limit that refutes its own upgrade sentence. The over-claim and its
  correction are in the same file; a reader who reads to the end is not misled.
- **`results/triangle-r3-adv-independence.md`** found the stencil-blindness by
  measurement before I found it by reading, prescribed the exact fix (*"a
  phase-2 gate plan must include the brute battery per built binary as a
  first-class RED"*), and conceded its own state-census result was not
  independence. Round 3's adversary was right; the gap is that round 4 banked a
  result without implementing the prescription.

The failure this round is not honesty. Every load-bearing weakness I found was
already written down by the lane that created it. The failure is **transmission
loss between the deliverable and the summary**: "covers the exact paths only"
became "seven gates GREEN"; "28 cells the Python validated" became "49 cells";
"closes the rule half of the objection" became "the objection is closed". Each
step of that loss happened above the lane, not inside it.

The lead-facing findings, stated as the role requires:

1. Two binaries were built and gated with no run record on disk (§3.0), against
   a round whose first rule is that nothing unwritten survives.
2. The queue row R4-SB1 still says "**OPEN** — needs the lead to build and
   gate". If it was built and gated, the row is stale; if the row is right, the
   gate results do not exist.
3. `experiments/probe_cutcount_dp.py` and `tests/gate_cutcount_b1.py` — the only
   incumbent-free oracle in the campaign and the only gate on the B1 engine —
   live on a parked branch and were **not** recovered along with the rows, though
   the round's first act was to recover the B1 artifacts. The recovery was
   incomplete in exactly the dimension this audit needed.

---

## §9 Job requests

Filed as rows in `results/r4/queue.md`; full field blocks here.

    job id:        JOB-IND-1  — the incumbent-free oracle, pointed at the binary
    measures:      T(n,H) for all n <= 12, H <= 6, computed two ways:
                     (i) direct brute force — grow every fixed king-animal by
                         flood fill over the literal 3x3 neighbourhood, bucket by
                         bounding-box height. No transfer matrix, no cut, no
                         second difference, no contact with results/ns_a40.
                     (ii) build/cutcount_b1 --assemble over its own --height rows.
                   Compare (i) against (ii) cell for cell.
    why:           This is the single control the campaign has never run. Every
                   committed check on the B1 C++ binary compares it to the
                   incumbent (tests/gate_cutcount_b1.py checks A, B, F), so the
                   shared king-adjacency stencil -- the whole of the residual
                   common mode after S2.1 -- is untested. It also tests the
                   second difference and the horizontal f_W - f_{W-1}
                   normalization against a route that uses neither.
    decides:       whether "recounted by a second rule" can be written without
                   the stencil caveat. A pass converts the banked 21.64% from
                   "agrees with the incumbent" to "agrees with the definition".
    box:           ayr or dalby, 1 core. NOT gympie only because it needs the
                   built binary; the brute half is seconds.
    cost:          MEASURED lower bound: probe_cutcount_dp.py already brute-forces
                   2^(HW) subsets at HW <= 12 in well under a minute. EXTRAPOLATED
                   for n <= 12, H <= 6 by growth rather than subset enumeration:
                   minutes. B1 side at H <= 6, n <= 12 is instant (gate check A
                   is 84 cells and the whole gate is ~7 s).
    RED control:   perturb one cell of the brute table by +1 and confirm the
                   comparison reports that exact (n,H). And run it once with
                   B1's stencil mutated to rook -- it must go red. If a rook-
                   mutated B1 passes against the brute force, the harness is
                   wrong, not the engine.
    deliverable:   experiments/tristruct/r4_indoracle_brute.py + .log
    changes if:    pass  -> S6 item 2 is retired and PROVENANCE.md gets one
                            corrected sentence.
                   fail  -> the banked rows are withdrawn pending diagnosis, and
                            so is every T(n,H) the campaign has compared to.

    job id:        JOB-IND-2  — close the spin gate chain's oracle dependency
    measures:      run `python3 experiments/tristruct/r3_spin_pipeline.py` (6.5 s,
                   self-contained: grows its own animals, brute-forces its own Z)
                   beside GATE 0 and diff its 28-cell n<=7 table against the C++
                   engine's compared_hlen set.
    why:           r4-spinbuild S3(k) prescribes exactly this and GATE 0's own
                   text repeats it as a required alongside-step. Without it the
                   spin chain is anchored solely on B1, which S2.2 shows shares
                   spin's rule. 6.5 seconds.
    box:           gympie is within limits (6.5 s, one core) -- but I run nothing.
    RED control:   already present: the 12/12/4 mutant fixtures, which are
                   measured against this pipeline's self-grown truth.
    changes if:    pass -> GATE 0 becomes a two-oracle check and S3.1's exposure
                           closes. fail -> the C++ port is wrong and GATE 0 was
                           passing on a shared error.

    job id:        JOB-IND-3  — file the gate receipts that do not exist
    measures:      nothing new. Re-run and TEE the two batteries the round
                   reports as passed: tests/gate_cutcount_b1.py on the patched
                   binary, and GATE 0 / GATE 1 on r4_spin_engine, to
                   experiments/tristruct/r4_perf_fastmodp.log and
                   experiments/tristruct/r4_spin_gate01.log.
    why:           S3.0. Under this project's standard a gate result with no log
                   is asserted, and both are currently load-bearing.
    cost:          MEASURED: ~7 s for the B1 gate (its own docstring); seconds
                   for GATE 0/1 per r4-spinbuild S4.2.

---

## NOT ESTABLISHED

- **The gate outcomes reported for both artifacts built tonight.** No log exists
  on disk for `tests/gate_cutcount_b1.py` against the patched binary, nor for
  spin GATE 0 / GATE 1. I audited the batteries as designed and took the
  outcomes as reported. JOB-IND-3.
- **Whether `r3_spin_pipeline.py` was run alongside GATE 0**, as r4-spinbuild
  §3(k) and GATE 0's own text both require. If not, GATE 0 is single-oracle.
- **Whether `RED-exact` (the `cmp` of patched vs unpatched `--modp` rows) has
  ever been run.** No `r4_perf_fastmodp.log` exists. Without it the patch is
  unvalidated on the only path it touches.
- **`symtm`'s extent mechanism.** §4.2(ii) narrows the Lean upgrade to routes
  implementing the touch-flag recurrence; I established that the production kink
  sweep does and that B1/spin/strip do not. I did not read `symtm` and cannot
  say which side it falls on.
- **Whether the production kink kernel's *stencil* is written independently of
  B1's.** I established both are hand-written and that neither is checked
  against a definition; I did not do a line-level comparison of the two stencils
  to determine whether one was derived from the other. If it was, the common
  mode is worse than §7 says.
- **Whether the `Unstranded` condition in the Lean plan matches the production
  death rule.** r4-lean files this itself; nothing in my read bears on it.
- **The C++ `gather` offsets at every (H, r) boundary case.** I verified the four
  slot offsets against the processing order by hand and at the `r = 0`,
  `r = H−1`, `c = 0` guards. I did not verify them programmatically, and a
  programmatic check is inside JOB-IND-1.
