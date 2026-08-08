> **NOTE: authored by Claude at jasonp's direction, 2026-08-08.** DEFENDER's
> phase-4 ledger for the L-trim campaign. Verdicts on `phase-4-cuts.md`'s
> twenty-two proposals; no `.tex` file was touched. Every excerpt was matched
> byte-exact against the post-phase-3 tree at 9d05633 by a mechanical pass
> (multi-line string containment plus whitespace-normalised recount): all
> twenty-two occur exactly once, exact and normalised. Every `\ref`, `\cite` and
> pin claim below was grep-counted rather than taken from the cuts file.

# Phase 4 — sentences. DEFENDER's verdicts.

**Twenty-two proposals, twenty-two concessions, no retains, no residues.** The
cutter's excerpt discipline is the cleanest of the four phases — every excerpt
byte-exact, none containing a `\cite`, a `\label`, or any of the gate's eight
pinned literals (re-checked against `l_trim_gate.sh`'s CONSTANTS block, not
against the cuts file's summary of it). Four factual defects in the ledger are
corrected on the record below; none changes a verdict and none would have
tripped the applier, because all four live in anchor *context* or collateral
commentary, never in an excerpt.

Sentence grain is where hedges live, so every proposal got a scoping-qualifier
pass: does the sentence carry the only statement of a bound, a precision, a
dataset size, or a machine context that warrants a nearby claim? The answer is
no at all twenty-two, and the per-entry arguments say where each candidate
qualifier's surviving home is. The two proposals that came closest to a RETAIN
are argued at length: P4.L3.1 (the cutter's self-conceded weakest — ruled on
its merits, and it concedes on its merits) and P4.L2.2 (the one excerpt that
*is* a scope hedge — conceded because the scoped statement is proved
unconditionally two sections later, so the empirical scoping is superseded, not
lost).

---

## L1-diagonal-law.tex

### P4.L1.1 — §priorart's "not unheard of" closer — CONCEDE

Anchor verified byte-exact and unique; splice leaves the paragraph ending "and
is proved once for all of them." with the next paragraph ("The one place where
our theorem settles...") intact. The binding statement of the posture survives
fourteen lines up — "We do not claim to be first, because absence is not a
database result" (L1:132, the cutter's L1:131 is off by one, advisory) — and
the *evidence* that the phenomenon is precedented is the surviving
Barequet–Shalah paragraph itself, with both `\cite`s untouched
(`barequetBarequetRote2010`, `barequetShalah2017`, each still present). The
closer neither scopes a claim nor carries attribution; it re-performs an
acknowledgment the intervening paragraph performs by stating the relative in
full. "not unheard of" occurs nowhere else in L1 (grep: 1). Conceded.

### P4.L1.2 — the gas-picture lead-in — CONCEDE

Anchor verified; the paragraph re-opens on "Write $F(n,u) = \dots$", clean. The
excerpt contains L1's third `\ref{cor:two}`; the other two survive in §machine
(L1:694 and L1:697 — both confirmed inside `sec:machine`), so nothing dangles
and check 2 is safe. The cutter's content claim checks out: the surviving
paragraph's own third sentence is "Then Theorem~\ref{thm:C} says exactly
that...", which ties the reading to the object it actually reads, and the
subsection title carries both the reading's name and its purpose. What the
reader loses is the sentence announcing that the paragraph deserves to exist —
PROTOCOL's named scaffolding form. No hedge, no number. Conceded.

### P4.L1.3 — §machine's "small computation" topic sentence — CONCEDE

Anchor verified; the paragraph re-opens on "A surplus-budgeted row transfer,
parametric in the step set $D$...", which is the working description. Both of
the removed claims are re-stated where they are earned, inside the same
paragraph: "The cost therefore depends on $k$ and $H$, not on the number of
animals" (L1:704–705) carries the no-enumeration claim with its reason, and the
state description is what "small" means. The scoping pass: no bound, no
dataset, no machine context is stated here and only here — the cost claim's
warrant is the surviving state description. Conceded.

### P4.L1.4 — §polyiamond's "doing real work" closer — CONCEDE

Anchor verified; the section now ends on "...we state the periodic law as an
extension rather than a result." — which is the load-bearing hedge, and it
survives untouched. The section's opening paragraph makes the same point at the
point of failure with the mechanism attached: hypothesis (U) fails
(orientation-dependent adjacency, no single step set) and "This is not a
technicality that a little more care would remove" (L1:788, confirmed). The
closer's extra content — naming (U) rather than the failure — is recoverable
from the opening, which names (U) explicitly. `\ref{thm:A}`: 16 occurrences,
15 survive (the cutter's "~15" is right). Conceded.

---

## L2-ternary-spine.tex

### P4.L2.1 — the abstract's "telescopes" closer — CONCEDE

Anchor verified; the abstract now ends "...and the level-$3$ correction is
again $W$." — a complete sentence carrying the same fact. "telescopes" occurs
exactly twice in L2 (grep: 2); the surviving occurrence is the §lift bullet at
L2:525–526, confirmed verbatim as the cutter quotes it, with *more* content
(what telescoping means: no new object per level). The measured-not-proved
status of the lifts is carried by the disclosure and by phase-3's P3.L2.3
residue ("These three are measured, not proved.", L2:531), both untouched — the
abstract sentence never carried that hedge, so no scoping is lost. Conceded.

### P4.L2.2 — the intro's "Not mostly" fragment — CONCEDE

Anchor verified; the paragraph ends on "Every invariant factor is a power of
$3$." This is the one excerpt in the phase that *is* a scope hedge — "at every
$N$ anyone has computed" scopes the observation as empirical — so it got the
hardest look. It concedes because the scoped statement is
Theorem~`thm:snf-3power`, proved unconditionally for every $N$ by the two-line
determinant argument (L2:390–396), and the paper says so in the immediately
following line ("§snf3 does it in two lines"). A hedge is load-bearing when it
is the difference between a measurement and a false theorem; here the theorem
is true and in the same paper, so deleting the hedge leaves an unqualified
statement that is *proved*, not overstated. The empirical dataset size is not
lost either: "Verified directly on the enumerated matrix for every $N \le 36$"
(L2:425) and the disclosure's "every $N \le 36$ for the Smith normal form" both
survive. Conceded.

### P4.L2.3 — "The count is the content." — CONCEDE

Anchor verified; the bridge line becomes "That is unconditional and it is the
easy half." — which still re-orients the reader toward the hard half, and the
introduction states the easy/hard framing at full length (L2:119–121,
confirmed verbatim). The maxim's only content is that framing. `thm:snf`'s
statement follows two lines down and says what the content is. Conceded.

### P4.L2.4 — the Lagrange–Bürmann "accident" closer — CONCEDE

Anchor verified; the paragraph ends on "The correction factor in \eqref{eq:LB}
is identically $1$." — the mathematical fact the two proofs consume, stated
with its derivation ($\varphi' = -3(1-x)^2 = 0$ in characteristic 3) in the
same paragraph. The "accident" framing survives in the abstract at L2:90–91,
confirmed verbatim. The promise that the proofs will be one line each is
redeemed by the proofs themselves, immediately below. Conceded.

### P4.L2.5 — the deficit-2 "reusable part" closer — CONCEDE

Anchor verified; the paragraph ends on "...and Theorem~\ref{thm:deficit2} the
third." — the `\ref` is in the surviving sentence as the cutter says
(`\ref{thm:deficit2}`: 3 occurrences in L2, none in the excerpt). This cut
*removes* an unhedged reach claim ("applies to any congruence for a family
linear in $(n,k)$") that the paper neither demonstrates nor verifies, in a
paper whose banner instructs that everything be read as "what we can prove".
Checked downstream: neither open problem leans on the method's generality (the
deficit-$d$ problem points at the Witt tower, the other-primes problem at the
polyhex triangle). A reader who wants to reuse the method has the Method
paragraph's explicit pipeline. Pruning a claim, not a warrant. Conceded.

---

## L3-lambda-bounds.tex

### P4.L3.1 — the ladder table's "honest parts" topic sentence — CONCEDE

The cutter's self-conceded weakest, ruled on its merits with no deference
either way. Anchor verified byte-exact and unique; the paragraph re-opens on
"The certified value is the floor: at $H = 2$..." — grammatical and complete.

The question is whether the framing instruction ("read these as disclosure,
not defect") is load-bearing over and above the two sentences that follow. It
is not, because each feature arrives with its own disclosure reading attached:
feature 1 carries "because a certificate states what is \emph{proved}" and
feature 2 carries "Clamping can only lower the certified value; it can never
falsify it" (L3:280–281). What phase 3's ledger identified as decisive about
this paragraph — a reader squaring the certified $2.4142135$ against
$\mu_2 = 2.4142136$, without which the first rung reads as a typo — survives
whole and untouched; the cut takes only the announcement that two such
features exist. No number, no proof step, no hypothesis, no warrant. Under the
protocol's standard ("tone, symmetry, completeness ... not decisive") this is
not a defence I can make decisive. Conceded.

One correction at this entry, recorded below as ledger defect 2: the decisive
2.4142135-argument the cutter attributes to "the phase-3 defence" was made by
the phase-3 *cutter*, in its considered-and-not-brought list
(`phase-3-cuts.md:608–613`); the phase-3 defender never ruled on this
paragraph. The substance of the claim — that argument was about content that
this cut leaves intact — is correct.

### P4.L3.2 — "A checker that cannot fail is not a checker." — CONCEDE

Anchor verified; the body line becomes "Four self-tests run as a gate:", which
opens the list cleanly. The subsection title four lines up — "The checker has
to be able to say no" — is the same statement, and the substantive point (the
failure mode a reader cannot see from a receipt) is carried by the surviving
"Test~D is the one that matters most..." paragraph. The smallest seam in the
six papers, exactly as argued. Conceded.

### P4.L3.3 — the crippling paragraph's "honestly" closer — CONCEDE

Anchor verified; the paragraph ends on "...at a wall time indistinguishable
from the full-precision run." The evidence — four failing states, the one-ulp
shortfall, $O(1)$ not $O(H)$ flooring loss, twenty-sweep recovery — survives
in full; what goes is the third statement of the soundness moral, whose two
surviving homes I confirmed: L3:280–281 (ladder paragraph) and §exact's
downward-rounding argument (L3:296–301), each with the mechanism attached.
Prune the claim's echo, keep the warrant. Conceded.

### P4.L3.4 — the two-engine self-appraising closer — CONCEDE

Anchor verified; the paragraph ends on "...same minimum ratio to all nine
printed digits." The removed sentence's two jobs are both done elsewhere:
naming the event (the surviving sentence *describes* the cross-validation —
two engines, receipts field for field, $H = 12, 13, 14$) and scoping it (the
trusted-not-certified hedge is the previous paragraph's explicit job,
L3:386–387 — the cutter's "385–386" is off by one, advisory). What is removed
outright is the superlative ("the strongest statement available"), which is
self-appraisal, not scope. Conceded.

### P4.L3.5 — §gap's findings-preview sentence — CONCEDE

Anchor verified; mid-paragraph splice leaves "This section measures where that
looseness sits. Everything here is measurement against brute-force counts." —
both load-bearing neighbours intact, exactly the two the cutter names (the
section's job, and its evidentiary status). The preview's three clauses each
have a verified home: the abstract's final paragraph states the finding with
the numbers (L3:97–102, confirmed verbatim including "median slack $1.144$,
maximum $1.222$" and "\emph{grows with $n$}"), and the four `\paragraph` heads
deliver it under names ("Diffuse, not concentrated", "It grows with $n$",
"What that rules out"). The paragraph's first sentence with the pinned `6.543`
and `9.3154` is untouched, as promised — both pins re-confirmed present at
their gate-read sites. Conceded.

### P4.L3.6 — "\emph{Per-type tuning is dead.}" — CONCEDE

Anchor verified; the paragraph ends on "...fixing the worst four barely moves
the bound." — which *is* the closed door's operational content, with the slack
audit's numbers above it intact. The ruled-out-lever claim also survives at
full strength in the abstract ("not a local defect that a larger window or
per-type tuning could remove", L3:100–101) and in "What that rules out". The
purest aphoristic closer in the six papers, and the warrant is the surviving
sentence. Conceded.

---

## L4-not-dfinite.tex

### P4.L4.1 — the BMR walkthrough's proof re-derivation — CONCEDE

The phase-3 deferral, brought with exactly the boundary phase 3 drew, and the
boundary holds up under checking. Anchor verified byte-exact (the longest
excerpt of the phase, six lines); the paragraph now ends on "...then $P$ has
only finitely many limit points." — the statement of their lemma, kept, with
the head (where Lemma 9 is and is not cited in the haruspicy papers) kept
above it. Collateral verified independently: `bmr2002` occurs 8 times in L4
and zero times in the excerpt, so check 7 is untouched; the head's
"(from~[4])" and "(from~[6])" are quoted prose, not `\cite`s, and survive; no
label, ref or pin in the run; the ψ-degree pin sits in §effective, far away.

What the reader loses is a line-by-line reperformance of *their* proof, which
the surviving `tab:sidebyside` mechanism row compresses ("asymptotic in $n$:
divide by $n^d$, take the limit, hit the leading coefficient" — confirmed at
L4:444) and which the citation this paper makes eight times supplies in full.
The run's closing sentence ("Every limit point is a root of one fixed
polynomial.") is the walkthrough's own summary and adds nothing to the kept
statement's "finitely many limit points". L4's banner posture needs the reader
to know what the lemma says and where it lives; both survive. The attribution
sites — disclosure, §shape, the table row, the "Step~1 is theirs" paragraph —
are all outside the run and all survive. Conceded.

### P4.L4.2 — "That is a ceiling on the method." — CONCEDE

Anchor verified — the six-word sentence is unique (the subsection title's
"ceiling on our method" is a different string) — and the paragraph now ends on
the bold sentence, which is the precisely scoped statement: over $\Q(x)$, does
not extend to $D_A$-finite. Third statement confirmed at all three sites: the
subsection title (L4:457), the abstract's "That is a real limit of the method,
not a gap in the exposition" (L4:92–93), and the bold sentence itself. The
scope hedge is the bold sentence and it survives verbatim with its
`\ref{thm:main}`. Conceded.

---

## L5-convex-king-animals.tex

### P4.L5.1 — the "Read informally" proof-preview run — CONCEDE

The phase-3 deferral, honoured on phase 3's terms: the paragraph's unique
content — "Every intermediate class is trapped between $M$ and $A$ term by
term, so nothing has to be proved about the individual classes --- the whole
job is those two", the proof's actual map — survives as the paragraph's close.
Anchor verified byte-exact; the splice ends the paragraph at "...those two."

Every clause of the removed run was traced to its claimed surviving home and
all five check out: fattens/shears/thins is in the abstract nearly verbatim
(L5:106–109, confirmed, including "too few to move an exponential");
middle-is-staircase/ends-are-stacks is `lem:blocks`'s statement and
`lem:stacks`'s title directly below; "too few to carry an exponential" is
`lem:stacks`'s "hence sub-exponential"; "glue end to end without waste" is
`lem:supermul`'s join; "one direction is free" is the containment line of
`prop:squeeze`'s proof (L5:357–359, confirmed). No labels, refs or cites in
the run; the `cor:floor` pin (L5:340) is outside the paragraph and confirmed
intact. A prose preview of three lemma statements that begin two inches lower.
Conceded.

### P4.L5.2 — the dangling "mirage" opener — CONCEDE

Anchor verified; §perimeter now opens "By \emph{semiperimeter} --- ... --- the
same class is not merely D-finite but algebraic.", self-contained under the
section title. The dangling-referent finding is confirmed by grep: "mirage"
occurs in L5 only at line 17 (the header comment's pointer to
`docs/proofs/convex-mirage.md`, not rendered) and in this sentence. A sentence
whose subject is undefined in the rendered document conveys nothing; phase 3
deferred this as a repair and removal resolves it at phase 4's unit. The cut
loses nothing and fixes a defect. Conceded.

### P4.L5.3 — the "entire role" restatement — CONCEDE

Anchor verified; mid-line splice leaves "...however many stacks there are,
they carry no exponential. Hardy and Ramanujan~\cite{hardyRamanujan1918} would
give..." — confirmed workable, single space. One flag for the applier,
stronger than the cutter states it: `hardyRamanujan1918` is that key's *sole*
occurrence in L5 (grep: 1), so this splice sits directly against a check-7
tripwire; the excerpt boundary as given ends at "discarded." and leaves the
citation sentence whole, so a byte-exact application is safe. The role
statement survives at L5:264–266 ("The lemma is two claims bolted together
... Only the second is used downstream", confirmed verbatim) and the
mathematical point in the surviving preceding sentence. `\ref{lem:stacks}`:
11 occurrences, 10 survive (the cutter's "9+" is right and conservative).
Conceded.

---

## L6-perimeter-gradings.tex

### P4.L6.1 — the "worth one sentence" lead-in — CONCEDE

Anchor verified; the paragraph re-opens on "$k = 3$ carries a genuine
period-$2$ term on \emph{both} lattices, so quasi-polynomiality is intrinsic
to the perimeter grading and not a square-lattice artefact." — which is the
working claim, complete with its warrant and its universality scope. Checked
that nothing downstream refers to the investigation's origin ("started"
appears nowhere else in a narrative sense; the paper's claims never consume
it). Scaffolding in PROTOCOL's named form plus repository narrative. This is
also nowhere near §k6's protected sentence (L6:600–601 names "the sentence
about periodicities costing two units of defect apiece", which is in
§"cyclotomic content" and untouched — confirmed). Conceded.

### P4.L6.2 — the A120452 refutation's closing epigram — CONCEDE

Anchor verified; the paragraph — a genuine closed door, and the disclosure of
a database error — ends on "So A120452 is wrong at its seventh term: $23$,
where the correct value is $24$." Everything that makes the refutation
auditable survives: the $g^4$ prediction $1384$ against the measured $1388$,
the convergence rule with its verification at $j=4$ and $j=5$, the wider
confirming run, both numbers in the verdict sentence. The removed sentence's
first clause restates the paragraph's own second sentence ("The six-term
prefix $1,1,3,5,9,14$ matches..."; "six-term" grep: 2, both in this
paragraph); its second clause is a cautionary maxim. The warrant is everything
before it. The L6 pin `1, 6, 22, 68, 187, 470, 1106` confirmed intact at
L6:418–419 and in `tab:mincoeffs`. Conceded — with the collateral correction
recorded below as ledger defect 1.

---

## Corrections to the ledger

Four defects, none verdict-changing, all recorded per the standing rule that a
right cut argued from a wrong fact must have the fact corrected on the record.

1. **P4.L6.2's collateral miscounts the `\oeis` macro.** The cuts file says
   "`\oeis{A120452}` occurs twice in the surviving part of the same
   paragraph". Grep: the macro occurs **once** in L6, at L6:506; the other two
   occurrences of the string (L6:507, L6:511) are bare text "A120452" with no
   macro. The safety conclusion is unaffected — the sole macro site survives
   and the excerpt contains neither form — but the count as written is false.

2. **P4.L3.1 attributes a cutter argument to "the phase-3 defence".** The
   decisive 2.4142135/2.4142136 argument for the honest-parts paragraph was
   made by the phase-3 *cutter*, arguing itself out of a paragraph proposal in
   its considered-and-not-brought list (`phase-3-cuts.md:608–613`); the
   phase-3 defender never ruled on that paragraph. The substance — the
   decisive content survives this sentence-level cut whole — is correct.

3. **Three anchor-context quotations are printed re-wrapped.** The *preceding
   context* blocks of P4.L4.2 ("and does / not extend"), P4.L5.1 ("proved
   about the / individual classes") and P4.L6.2 ("where the correct value is /
   $24$") wrap differently from the tree. Whitespace-normalised they each
   match exactly once, and every one of the twenty-two *excerpts* is
   byte-exact as printed, so the applier — which asserts on excerpts, not
   contexts — is unaffected. Recorded so the ledger does not overstate its own
   precision: the cuts file's implicit claim that quoted text mirrors the tree
   holds for excerpts only.

4. **Two advisory line numbers are off by one.** P4.L1.1 cites "L1:131" for
   the no-first-claim sentence (it is at L1:132) and P4.L3.4 cites
   "L3:385–386" for the trusted-not-certified sentence (L3:386–387).
   Amendment 3 makes these advisory; noted for the record only.

## Verified clean, for the adjudicator's accounting

- All 22 excerpts byte-exact, each occurring exactly once in its paper (exact
  and whitespace-normalised counts both 1).
- Zero `\cite` and zero `\label` in any excerpt; no cite key's occurrence
  count changes, so check 7 cannot fire. The one check-7-adjacent splice
  (P4.L5.3, sole `hardyRamanujan1918`) is flagged at its entry.
- None of the gate's eight pinned literals (re-read from `l_trim_gate.sh`'s
  CONSTANTS block) appears in any excerpt; L3's `6.543`/`9.3154` gate-read
  sites and L5's `cor:floor` and L6's septuple pins confirmed present and
  outside every cut range.
- `\ref` accounting: `cor:two` 3→2 (both survivors in §machine), `thm:A`
  16→15, `lem:stacks` 11→10, `thm:deficit2` 3→3, `thm:main` (L4) untouched.
  No label's reference count reaches zero this phase; no label is defined in
  any excerpt.
- Every mid-paragraph splice and every end-of-paragraph boundary was checked
  against the tree: each removal leaves a complete sentence on at least one
  side and no double blank line inside a paragraph.
