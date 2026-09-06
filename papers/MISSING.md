# MISSING — citations we want but couldn't pull full text for

Papers we reference but do **not** have a local copy of and could not access a free
version of online. For university-library lookup. Add to this list any time a paper
can't be found; remove (and drop the PDF in `papers/`) once obtained.

Format: `Author(s), "Title," Venue Vol (Year) pages. DOI/ID. — why we want it. [priority]`

## Claude's web-search pass over this file, 2026-08-06

Two obtained, six confirmed paywalled with their metadata pinned, one new lead.
**Do not re-run the plain "title + pdf" search on the paywalled six; it has been run.**

**Obtained:**

- **Whittington & Soteros 1990** — free from Grimmett's own Hammersley-festschrift
  page, `statslab.cam.ac.uk/~grg1000/books/hammfest/19-sgw.pdf`. Filed. Its title page
  settles the author order *against* the note below: it reads Whittington & Soteros, so
  Barequet–Rote had it right and Madras's bibliography reversed it.
- **Guttmann, Jensen, Wong & Enting, "Punctured polygons and polyominoes on the square
  lattice," J. Phys. A 33 (2000) 1735–1764, arXiv cond-mat/0003441** — free, and it was
  on no list. Found while hunting the 1990 punctured-discs paper. It matters: its
  Appendix proves k-punctured polyominoes share the unpunctured growth constant with the
  exponent shifting by exactly 1 per puncture, which is the asymptotic content of our
  hole-fill bijection. `results/subclasses.md` now cites it. It
  also reproduces van Rensburg & Whittington's method, which largely discharges that want.

**Metadata pinned, no free copy (all confirmed paywalled at Springer/IOP):**

- Janse van Rensburg & Madras 1997 — IOP, `10.1088/0305-4470/30/23/007`. Nothing on the
  author's York page.
- Madras 1995 — Springer, `10.1007/BF02183684`. The abstract gives the result: **θ ≥
  (d−1)/d**, so in 2D a rigorous θ ≥ ½ — consistent with, and much weaker than, the
  universal 1 our approximants find. Worth a clause in the growth paragraph either way.
- Bollobás & Leader, "Edge-isoperimetric inequalities in the grid" — **volume confirmed:
  Combinatorica 11 (1991) 299–314**, `10.1007/BF01275667`. The entry below no longer
  needs its "unconfirmed" caveat.
- Conway, Brak & Guttmann 1993 — confirmed J. Phys. A 26 (1993) 3085–3091. ResearchGate
  has a copy behind an account wall.
- Janse van Rensburg & Whittington 1990 (punctured discs) — no free copy anywhere.
- Ibn-Majdoub-Hassani 1996 — the thesis record exists, `theses.fr/1996PA112406`, with
  abstract and jury; **no digitised full text**. Confirms the desk is exhausted.

**Sampling literature — found 2026-08-22, and it is NOT missing.**
`docs/time-at-the-bar.md` A2.1 required a prior-art check before any sampler was
designed, on the grounds that lattice animals under Rosenbluth sampling is not a
new idea. It is not, and the two central papers are free on arXiv:

- Hsu & Grassberger, "An improved Rosenbluth Monte Carlo scheme for cluster
  counting and lattice animal enumeration" — `arXiv:physics/9911023`.
- Hsu, Nadler & Grassberger, "Simulations of lattice animals and trees" —
  `arXiv:cond-mat/0408061`.

The method is PERM (pruned-enriched Rosenbluth), applied to lattice animals
directly rather than only to polymers, reaching site animals on the square
lattice to **n = 46** — past this project's n = 41 — and producing precise
estimates of the partition sum and the entropic exponent. Estimates with error
bars, never exact counts, which is the whole question for whether the channel
can falsify a term. **These should be fetched into `papers/`;** the paywalled
Janse van Rensburg–Madras 1997 entry above is not the state of that literature
and this file should not be read as implying it is.

**Also noted:** Madras 1999, which we hold, is on arXiv as `math/9902161` — cite the
arXiv id, and it explains the copy's poor OCR.

**New want, raised by reading Asinowski et al. (2026-08-06, unsearched):**
P. J. Peard & D. S. Gaunt, "1/d-expansions for the free energy of lattice animal models
of a self-interacting branched polymer," J. Phys. A **28** (1995) 6109–6124 — p. 6113,
eq. (2.15) is where the *diagonal formula* shape `DX(n,n−k) = 2^{n−2k+1} n^{n−2k−1}
g_k(n)` was first predicted, twenty-two years before Barequet–Shalah proved it. If Paper 2
cites the polycube line as precedent for the statement shape, this is the earliest
occurrence and the honest first citation. Also of interest, same authors: Gaunt & Peard,
"1/d-expansions for the free energy of weakly embedded site animal models," J. Phys. A
**33** (2000) 7515–7539. **[med]**

**New wants from the N5 re-run on "diagonal formulae" (2026-08-06, unsearched
beyond confirming no free copy exists):**

- G. Barequet & B. Magal, "Automatic generation of formulae for polyominoes with
  a fixed perimeter defect," Comput. Geom. **108** (2022/23) 101919, DOI
  10.1016/j.comgeo.2022.101919. — the **perimeter**-defect member of the same
  family as our height-defect diagonals: an algorithm that emits closed formulae
  and generating functions per defect, k ≤ 5 (previously k ≤ 3). Paper 2 should
  cite it as prior art for the statement shape; worth reading to see whether
  their automatic generation subsumes or complements our defect-gas machinery.
  ScienceDirect returns 403 and the author's own publications page carries no
  PDF for it. **[high]**
- G. Barequet & M. Shalah, "Improved upper bounds on the growth constants of
  polyominoes and polycubes," Algorithmica (2022). — spotted on the same page.
  Bears on `docs/proofs/polyplet-upper-bound.md`, where our 9.3154 is the loose
  half of the bracket and the polyomino comparison figures are quoted
  second-hand. Note for that doc: Barequet–Shalah 2017 states the best known
  polyomino bounds as ~4.0025 (lower) and **4.649551** (Klarner–Rivest, upper),
  where our doc says "4.63". **[med]**

**New lead, not chased:** Barber & Erde, "Isoperimetry in integer lattices,"
arXiv 1707.04411 (2017/18). Solves the **edge**-isoperimetric problem asymptotically for
Cayley graphs on ℤ^d, optimal shapes being zonotopes. The king lattice is such a Cayley
graph, so this is the modern reference *if* the report ever prints the bond-perimeter
twin. Asymptotic only, and free.

## High priority

- **G. E. Andrews, "Generalized Frobenius partitions," Memoirs of the American
  Mathematical Society, Number 301, May 1984.** — RAISED 2026-08-07, and the
  most wanted thing in this file. The square4 diamond tip's free-removal factor
  is `phi_2` = A053993, and we cite Andrews eq. (5.9) for its product form
  **entirely second-hand from the OEIS entry**. We verified the product against
  our own cone count to n=40, so nothing is at risk numerically, but the
  citation is unread. More important: the memoir is where `phi_k` is defined and
  developed, so it is the place to find out whether "order ideals of the cone
  {a >= |b|}" is a KNOWN reading of `phi_2`. Andrews' `phi_k` are two-rowed
  arrays and our object is a pair of nested partitions, which smells like the
  same bijection; if it is already in there, the min-end result cites it rather
  than claiming it.

  **LOCATED 2026-08-07, PARKED — jasonp is not searching further from work.**
  ISBN 0821823027 / 9780821823026, LCCN 84003059, AMS 1984, 26 cm. Pitt's
  discovery layer lists it under **"Ebook Central Perpetual and DDA"**, so an
  electronic copy may exist. Caveat: DDA is demand-driven, so the title is
  discoverable without necessarily being owned, and a walk-in guest account may
  not be able to trigger the purchase. Try the Ebook Central link first; fall
  back to print (Memoirs vol. 49, no. 301). Do NOT chase the online *serial*
  record (ISSN 1947-6221) — that is the whole Memoirs run and carries no
  per-item holdings; search the monograph by title/author instead.

  Pitt access notes: visitors get a temporary guest computer account at any ULS
  library with photo ID, on-site only, no remote access. Hillman Mon-Thu
  8:30-22:00, Fri 8:30-18:00, Sat/Sun 10:00-18:00; Bevier (science/engineering,
  the likelier home of print J. Phys. A runs) Mon-Fri 9:00-17:00 only. **All ULS
  libraries closed Monday 2026-08-10.**

  When it is in hand, two things to read: **eq. (5.9)**, the product form we
  quote from OEIS and have never read, and whether Andrews gives `phi_2` a
  combinatorial description matching our pair of nested partitions
  `(lambda, mu)` — that is the difference between a new interpretation and a
  known one. **[high]**

_(everything below was obtained 2026-08-06.)_

**The maxhole attribution chain, closed the same day it was opened.** A
backward pass through the reference lists of Sieben 2008 and Altshuler et al.
2006 raised an attribution question — not a gap in the proof — and jasonp
pulled all five candidates within the hour. Answer: **the primary is Wang &
Wang 1977.**

- D. L. Wang & P. Wang, "Discrete Isoperimetric Problems," SIAM J. Appl. Math.
  **32**(4) (1977) 860–870. — **READ. It is the source.** A linear ordering of
  ℤⁿ whose every prefix minimizes the boundary (points not in the set at
  Euclidean distance 1 — in ℤ², exactly our N(A)) among sets of that size.
  Arbitrary sets, no connectivity, which is the hypothesis the union argument
  needs. Minimizers are "standard spheres", |x|+|y| ≤ m plus part of the next
  shell: our diagonal diamonds. They also show it is equivalent to Macaulay's
  theorem. Cite this first; Sieben and Altshuler et al. supply closed forms.
- B. Bollobás & A. J. Radcliffe (EJC 11, 1990); F. Chung (Surveys in Diff.
  Geom. IX, 2004); S. L. Bezrukov (Bolyai Soc. Math. Stud. 3, 1994). — held,
  all three. Cube-centred; the grid is a section, not the subject. Wang–Wang
  is the cleaner citation for our statement, so these are context only.
- T. Prellberg & A. L. Owczarek, Commun. Math. Phys. **201**(3) (1999)
  493–505. — held. Sieben's [10]. The bond-perimeter twin is their eq (3.1),
  stated in passing without proof: max area of a polygon of perimeter 2n is
  n²/4 (n even), (n²−1)/4 (n odd). That is the rook-side 1/16 against our
  site-side 1/8. Quotable, but it is folklore there, not a theorem of theirs.

Deliberately not chased from those two reference lists: Bousquet-Mélou &
Rechnitzer, "The site-perimeter of bargraphs" (Adv. Appl. Math. 31, 2003);
Delest, Gouyou-Beauchamps & Vauquelin (Graphs Combin. 3, 1987); Stratychuk &
Soteros (J. Phys. A 29, 1996). All three are site-perimeter *enumeration* or
solvent contacts — a different question from the extremal one. Revisit only if
the report grows a perimeter section.

_Cleared earlier: Barequet–Moffie 2007 and Mertens 1990, obtained 2026-06-25.
Sieben 2008 and Altshuler et al. 2006, obtained 2026-08-06 — both read the same
day, and they answered more than was asked: Sieben's Thm 4.1 is M(n) verbatim
rather than inverted, the two papers' statements do coincide (checked at every
k ≤ 200,000 in `experiments/maxhole_sieben_check.py`), and the no-connectivity
hypothesis closed the multi-hole case outright — `results/subclasses.md`
§The union argument._

## Citation scan of the isoperimetry batch, 2026-08-06 — three found, six not

Scanned the reference lists of all seven papers filed that afternoon (Wang–Wang,
Bollobás–Radcliffe, Chung, Bezrukov, Prellberg–Owczarek, Barequet–Barequet–Rote,
Barequet–Shalah). Dead ends worth not re-scanning: Wang–Wang's own references are
pure extremal set theory (Macaulay, Kruskal, Katona, Clements–Lindström) with no
lattice-animal content; Chung is spectral/Cheeger throughout; Bollobás–Radcliffe
and Bezrukov cite cube isoperimetry only.

**Obtained and read:**

- N. Madras, "A pattern theorem for lattice clusters," Ann. Comb. **3** (1999)
  357–384. → `papers/madras_1999_*.pdf`. **The find.** Covers the king lattice
  (his §3.1(f) at M=1, sup norm). λ₀ < λ for hole-free animals is a corollary
  of his Theorem 2.1, and `a(n+1)/a(n) → λ` is his Theorem 2.2. See
  `results/subclasses.md`, which retracted a claim on the
  strength of it.
- M. E. Fisher, A. J. Guttmann & S. G. Whittington, J. Phys. A **24** (1991)
  3095–3106. → `papers/fisher_guttmann_whittington_1991_*.pdf`. States the
  bond-perimeter maximum (m²/16, or (m²−4)/16) as "clearly", exactly as
  Prellberg–Owczarek does. **Question closed with a negative: the 1/16 twin is
  folklore and has no primary.** Don't keep hunting for one.
- A. Asinowski, G. Barequet, R. Barequet & G. Rote, J. Integer Seq. **15**
  (2012) #12.8.4. → `papers/asinowski_etal_2012_*.pdf`. Open access.

**New wants raised by Madras's own reference list** (Madras 1995 searched in the
pass at the top of this file — paywalled, metadata pinned; MSW 1988 unsearched):

- N. Madras, "A rigorous bound on the critical exponent for the number of
  lattice trees, animals, and polygons," J. Statist. Phys. **78** (1995)
  681–699. — bears directly on the θ = −1.000(1) paragraph: a *rigorous* bound
  on the exponent we estimate numerically. **[med]**
- N. Madras, C. E. Soteros & S. G. Whittington, "Statistics of lattice
  animals," J. Phys. A **21** (1988) 4617–4635. — the classical rigorous-
  statistics paper for animals; the natural place to check what else about
  sub-classes is already proved. **[med]**

## Searched by jasonp 2026-08-06 and NOT FOUND — library or nothing

Do not re-search these from the desk; the desk has been tried.

- F. Ibn-Majdoub-Hassani, "Combinatoire des polyominos et des tableaux décalés oscillants,"
  PhD thesis, Université de Paris Sud, Orsay, November 1996. — reference [6] of
  Gouyou-Beauchamps & Leroux 2004, the source of the C-convex hexagonal class, and the one
  candidate origin of the growth-phase block decomposition that `docs/publication.md`
  N3 could not obtain either. His 1997 FPSAC paper uses strata instead, so this is a long
  shot, and it is now the only untested one. **Not found; very small result set.** A French
  institutional repository (theses.fr, Orsay) is the remaining route. **[med]**
- A. R. Conway, "Enumerating 2D percolation series by the finite-lattice method: theory,"
  J. Phys. A 28 (1995) 335–349. DOI 10.1088/0305-4470/28/2/011. — FLM theory (bounding-box
  Möbius decomposition = the architecture our 4-direction split sits inside).
  **Not found.** **[med]**
- A. R. Conway & A. J. Guttmann, "On two-dimensional percolation," J. Phys. A 28 (1995)
  891–904. DOI 10.1088/0305-4470/28/4/015. **Not found.** **[med]**
- I. G. Enting, "Generating functions for enumerating self-avoiding rings on the square
  lattice," J. Phys. A 13 (1980) 3713. — origin of the finite-lattice method.
  **Not found.** **[med]**

All four are wanted for lineage and citation courtesy, not for any claim: nothing in the
repo depends on reading them.

Not found in the second round (the citation scan above), same disposition:

- ~~C. E. Soteros & S. G. Whittington, "Lattice animals: rigorous results and wild
  guesses"~~ — **OBTAINED 2026-08-06**, free from Grimmett's page; see the search pass at
  the top. Correct order is Whittington & Soteros.
- E. J. Janse van Rensburg & S. G. Whittington, "Punctured discs on the square lattice,"
  J. Phys. A **23** (1990) 1287–1294. — the nearest thing to prior art on *holes* the scan
  turned up; `results/subclasses.md` claims no paper measures hole area, and this is the
  one that could contradict it. **[med]**
- I. G. Enting & A. J. Guttmann, "On the area of square lattice polygons," J. Stat. Phys.
  **58** (1990) 475–484. — was wanted as the possible primary for the bond-perimeter
  maximum. **Demoted: Fisher–Guttmann–Whittington 1991 shows that statement is folklore**,
  so there is probably nothing to find here either. **[low]**
- D. J. Kleitman, M. M. Krieger & B. L. Rothschild, "Configurations maximizing the number
  of pairs of Hamming-adjacent lattice points," Studies in Appl. Math. **50** (1971) no. 2.
  — Wang–Wang's [9]; the edge-isoperimetric extremal problem on ℤⁿ, i.e. the bond-side
  companion to the vertex result we now cite. **[low]**
- B. Bollobás & I. Leader, "Edge-isoperimetric inequalities in the grid," Combinatorica
  **11** (1991) 299–314, DOI 10.1007/BF01275667 (volume confirmed 2026-08-06); and
  "Exact edge-isoperimetric inequalities," European J. Combin. **11** (1990) 325–340.
  — only needed if the report prints the bond-perimeter twin. **[low]**
- S. L. Bezrukov, "An isoperimetric problem for Manhattan lattices," proceedings, possibly
  in Russian (his own [19]). — the title is our exact setting, but Wang–Wang already
  answers it. Curiosity. **[low]**

Not found in the third round either — the scan of Madras 1999's own bibliography, none
of these previously listed:

- E. J. Janse van Rensburg & N. Madras, "Metropolis Monte Carlo simulation of lattice
  animals," J. Phys. A **30** (1997) 8035–8066. — **the one that checks our own claim.**
  Madras 1999 points at its §2.4 and §2.8 for "further applications of the pattern theorem
  for weighted animals". Those sections are where the corollaries were drawn, so if anyone
  has already stated "simply-connected animals are exponentially rare", it is there — and
  that is the one thing we still call ours in `results/subclasses.md`.

  **Second reason to want it, added 2026-08-07 — it now settles two questions.**
  A Metropolis chain on lattice animals cannot be published without establishing
  its own irreducibility, and the move it uses is the connectivity-preserving
  single-cell move. So the square-lattice case of idea 8 of
  `results/closed-doors.md` — is the move graph connected — is almost
  certainly a lemma in this paper, along with whatever they know about its
  mixing. We have now measured the king case directly
  (`results/subclasses.md`); what this paper would supply is the
  proof technique for all `n`, and the honest prior art. Check §2 for the chain's
  definition and ergodicity argument before anything in that results file is
  described as new. **[high]**
- N. Madras & G. Slade, *The Self-Avoiding Walk*, Birkhäuser, Boston, 1993. — a book, so
  library or purchase rather than download. Load-bearing if the report states the ratio
  limit: Madras 1999 proves his Theorem 2.2 by reusing "the proof of Theorem 7.3.2 in
  Madras and Slade (1993)". Also the standard monograph for the pattern-theorem lineage.
  **[med]**
- A. R. Conway, R. Brak & A. J. Guttmann, "Directed animals on two-dimensional lattices,"
  J. Phys. A **26** (1993) 3085–3091. — Madras's [3], cited for numerical growth constants
  of bond trees vs bond animals vs site animals across several directed 2D lattices. Wanted
  only to see whether their lattice list includes the king/diagonal case, against
  `results/subclasses.md`. Distinct from the two A. R. Conway 1995 percolation
  papers listed above. **[low-med]**
- D. J. Klein, "Rigorous results for branched polymers with excluded volume," J. Chem.
  Phys. **75** (1981) 5186–5189. — Madras's [11], cited beside Klarner 1967 as the other
  route to *existence* of the growth constant by concatenation and subadditivity. Citation
  courtesy; we hold Klarner and nothing depends on this. **[low]**

Checked in Madras's bibliography and deliberately **not** wanted, so the list is not
re-walked: Kesten 1963 (the SAW pattern theorem he generalises — name it in prose, no need
to hold it); Bender–Gao–Richmond 1992 (submaps of maps, the same 0–1 phenomenon for planar
maps); Madras–Soteros–Whittington et al. 1990 (collapsing branched polymer, the θ-point
neighbourhood we already declined with Stratychuk–Soteros); Hara–Slade 1992 (high
dimensions, lace expansion); Swierczak–Guttmann 1996 (non-Euclidean lattices);
Vanderzande 1998 (polymer textbook); Grimmett 1989; Hammersley–Morton 1954; Cassels 1959
(cited only for a lattice-periodicity technicality).

## Cleared 2026-08-06 — the polycube defect-diagonal line, both obtained

Wanted by `docs/publication.md` N5: the same "fix the defect, get polynomial ×
exponential" statement shape as our universal diagonal law, with the defect measured in
dimension instead of height. Paper 2 should cite both. **Both now in `papers/`; neither
has been read past the abstract.**

- R. Barequet, G. Barequet & G. Rote, "Formulae and growth rates of high-dimensional
  polycubes," Combinatorica 30 (2010) 257–275. → `barequet_barequet_rote_2010_*.pdf`
- G. Barequet & M. Shalah, "Counting n-cell polycubes proper in n−k dimensions,"
  European J. Combin. 63 (2017) 146–163. → `barequet_shalah_2017_*.pdf`

## Cleared — were on the "check for a free version first" list, both already held

- H. Tremblay & J. Vernay, "On the generation of discrete figures with connectivity
  constraints," RAIRO-Theor. Inf. Appl. 58 (2024) Art. 16. — held since 2026-06-11 as
  `papers/tremblay_vernay.pdf`. Source of the record a(18) for A006770; code at
  github.com/J-Vernay/discrete-figures.
- G. Barequet, M. Moffie, A. Ribó, G. Rote, "Counting polyominoes on twisted cylinders."
  Held since 2026-06-28 as `papers/barequet_rote_twisted_cylinders.pdf`; **the uncertain
  venue is settled from its own title page** — INTEGERS: Electronic Journal of
  Combinatorial Number Theory **6** (2006), #A22, four authors. `INDEX.txt` corrected.
- G. Aleksandrowicz & G. Barequet, "Counting d-dimensional polycubes and nonrectangular
  planar polyominoes," IJCGA (2006). — dropped rather than obtained: its stated question
  ("confirm they don't touch king") was answered by the 2009 companion we hold.
- G. Barequet, M. Moffie, A. Ribó, G. Rote, "Counting polyominoes on twisted cylinders,"
  (venue uncertain — INTEGERS / Electronic J.? ~2006). — the cleanest "width W alone bounds
  TM cost" realization; want exact venue + free version.

## Obtained 2026-08-01 from jasonp's lattice-animal searches — all in papers/
Six papers, all now held. First-pass dispositions below; **one is worth
following up and it is not the one first flagged.**

- **G. Barequet, G. Ben-Shachar, M. C. Osegueda, "Concatenation arguments and
  their applications to polyominoes and polycubes," Comput. Geom. 98 (2021)
  101790.** Flagged sight-unseen as an attack on C2 (log-convexity) on the
  guess that concatenation supplies the missing injection. **Read: it does
  not.** The method is Fekete on quasi sub-/super-multiplicative sequences
  (Z(m+n) >= P(m+n)Z(m)Z(n)), which bounds *growth constants*, not
  log-convexity — a different inequality from a(n)^2 < a(n-1)a(n+1). C2 is
  unmoved and its "no clean injection is known" stands.
  **What it does bear on is the lambda bracket.** The super-multiplicative
  direction is already banked and superseded (Fekete gives
  lambda >= a(40)^(1/40) ~ 6.22, commit 8ae1462; the certified ladder's 6.543
  beats it). The open direction is **quasi-sub-multiplicativity, which yields
  UPPER bounds** — and our upper end, 9.3154, is the loose half of the
  bracket. Whether king animals admit a concatenation-based sub-multiplicative
  bound below 9.3154 is a live question that would shorten a sentence in the
  paper. Not attempted. **[the one worth a look]**
  **LOOKED, 2026-08-01 — CLOSED, no gain** (`results/growth-constant.md`,
  `experiments/concatenation_bound_check.py`). Priced first: with `a(40)` banked,
  a degree-2 `P` would give `lambda <= 7.745` (degree 3 gives 8.642; degree 4
  gives 9.642 and helps nothing), and the measured `a(m+n)/(a(m)a(n))` grows
  linearly in `m+n`, so 40 terms refute nothing. Then the proof: BBO's
  lexicographic split shatters a king comb into `~n/4` components (measured), so
  the reassembly code is `n^Theta(n)`, not polynomial; the centroid/spanning-tree
  split that keeps both sides connected cannot prescribe the halves to within the
  `O(1)` that Theorem 1(a)/(b) needs. Decisive: the same lemma for ordinary
  polyominoes would give `lambda_poly <= 4.3828`, beating Barequet-Shalah's
  4.5252 from published terms alone — it is a known-hard target, not an oversight.
- **G. Aleksandrowicz & G. Barequet, "Counting polycubes without the
  dimensionality curse," Discrete Math. 309 (2009).** The [med] want above is
  **CLOSED**: its open question was "confirm they don't touch king," and they
  do not — the algorithm is face-adjacency hypercubic throughout (each cell
  has 2d neighbours). Generalization is by dimension, not by adjacency, as
  suspected.
- **T. Mansour & R. Rastegar, "Enumeration of various animals on the
  triangular lattice," European J. Combin. 94 (2021) 103294** (also arXiv
  2011.05318). Baryiamonds, column-convex and convex polyiamonds by perimeter.
  Bears on the universality work's open item (polyiamonds, which need row
  conventions) and on the parked convex side quest.
- **L. L. Liu & Y. Wang, "On the log-convexity of combinatorial sequences,"
  Adv. Appl. Math. 39 (2007) 453-476** (also arXiv math/0602672). Held; the
  abstract-level read stands — closure operations plus three-term recurrences,
  and a(n) satisfies no known recurrence. Reading it would confirm the
  negative and sharpen *why* C2 is hard, which is worth a line in
  open-conjectures.md if anyone does it.
- **D. Gouyou-Beauchamps & G. Viennot, "Equivalence of the two-dimensional
  directed animal problem to a one-dimensional path problem," Adv. Appl. Math.
  9 (1988) 334-357.** Context for the directed-animal lineage behind the
  Bacher comparison bound and behind BM-R's heaps.
- **M. Bousquet-Melou, "q-Enumeration de polyominos convexes," JCTA 64 (1993)
  265-288.** For the convex side quest if revived.

Still un-obtained from that search, low value, not chased: Duchi-Rinaldi-
Schaeffer (Z-convex, 2008), Delest column-convex GFs (JCTA 1988),
Dubernard & Dutour (1996), Feretic & Svrtan (1996), Bousquet-Melou "New
enumerative results on two-dimensional directed animals" (1998).

## Notes
- arXiv-available (NOT missing): Jensen cond-mat/0007239 & 0007238, Conway 1610.09806,
  Jensen math/0506317, Guttmann-Jensen cond-mat/0603833, Clisby-Jensen 1111.5877,
  Barequet-Shalah 1906.11447, Shirakawa 2510.22446, Bui 2511.00461 & 2412.20143,
  Foster-Pinettes cond-mat/0210548, BM-Linusson-Nevo math/0701890, BM-Brak 0811.4415.
- In papers/: Jensen 2001, Jensen 2003 (ICCS), Barequet–Ben-Shachar 2024
  (counting_polyominoes_revisited.pdf), Vöge–Guttmann 2003,
  **barequet_moffie_2007_jensen_complexity.pdf, mertens_1990_lattice_animals.pdf,
  read_1962_cell_growth.pdf, klarner_rivest_1973_upper_bound.pdf,
  klarner_1967_cell_growth_problems.pdf** (added 2026-06-25).
- Also filed 2026-06-25: Mertens & Lautenbacher, "Counting Lattice Animals: A Parallel
  Attack," J. Stat. Phys. 66 (1992) 669 → mertens_lautenbacher_1991_parallel.pdf.

## Northcott + monotonicity => anisotropic non-D-finiteness (2026-07-15)
Need a literature check before claiming novelty: does the argument
"y-slices rational/integer, strip growth constants strictly increasing and
bounded => slice degrees unbounded by Northcott => two-variable GF not
D-finite" appear anywhere? Closest known: A. Rechnitzer, "Haruspicy and
anisotropic generating functions" (Adv. Appl. Math. 2003); "...2: bond
animals" (2006); "...3: SAPs" (JCTA 2006). Also check: J. Bell / S. Gerhold
/ M. Mezzarobba-adjacent non-D-finiteness criteria; Guttmann's solvability
tests; Bousquet-Melou anisotropic surveys. If truly absent, this is a
publishable stand-alone note.

**PARTIALLY DISCHARGED 2026-08-01 — and the target paper changed.** The
D-finiteness *test* the Haruspicy papers use is not in Haruspicy 1. Both
Haruspicy 2 (Theorem 15) and Haruspicy 3 (Theorem 5) attribute it verbatim
to **Bousquet-Melou & Rechnitzer, "Lattice animals and heaps of dimers,"
Discrete Math. 258 (2002) 235-274, Lemma 9** — which is free from
labri.fr/perso/bousquet and is now in `papers/` along with both Haruspicy
papers (arXiv math/0406450, math/0408054). Side-by-side comparison against
our dominant-pole dichotomy: `results/anisotropic-not-dfinite.md`. Summary:
the opening move (extract y-coefficients from the ODE to get a linear
recurrence with polynomial coefficients) is **shared and is theirs, 2002**;
everything after diverges — their conclusion is topological (finitely many
limit points of the whole pole set, via an asymptotic-in-n argument on the
leading coefficient), ours is arithmetic and effective (a degree bound on
one distinguished pole per slice, giving explicit (r,D) exclusion boxes).
Northcott appears in neither.

**REMAINING LEADS SWEPT 2026-08-01 — item now CLOSED.** The other names in
the original list were checked and none collides:

- **Bell, Gerhold, Klazar & Luca**, "Non-holonomicity of sequences defined
  via elementary functions," Ann. Comb. (2008), arXiv math/0605142 (saved to
  `papers/`). Method is **analytic** -- counting zeros of elementary and
  analytic functions -- and the class is sequences obtained by evaluating an
  elementary function at positive integers. T(n,H) is not of that form.
- **Gerhold**, "On some non-holonomic sequences," Electron. J. Combin. 11
  (2004): same analytic family.
- **Bell, Hu & Satriano**, "Height gap conjectures, D-finiteness, and weak
  dynamical Mordell-Lang," arXiv 2003.01255. The one paper found that pairs
  **heights with D-finiteness** -- but in arithmetic dynamics, bounding
  h(f(Phi^n(x))) along orbits of rational maps, with D-finite coefficient
  growth as an application. Different configuration entirely; not slice
  growth constants. Closest arithmetic-flavoured relative located, and not a
  collision.
- **Guttmann**, "Indicators of solvability for lattice models," Discrete
  Math. 217 (2000) 167-189: the programmatic source of the anisotropic-GF
  solvability test that Rechnitzer's programme answers, not a theorem in our
  configuration.
- Also noted: the classical arithmetic constraint (D-finite + integer
  coefficients + K rho^n n^alpha ==> alpha rational), used for quarter-plane
  excursions. Arithmetic, but about one sequence's asymptotic exponent, not
  a family of algebraic degrees.

**Verdict.** Every non-D-finiteness method located in this literature is
either topological (BM-R pole accumulation) or analytic (Klazar divergence;
BGKL zero-counting). Northcott-on-slice-growth-constants was not found.
Absence still cannot be established by search, so the paper now claims the
argument with that qualification stated explicitly rather than resting on
it -- see `paper/polyplets-report.tex`, "Relation to existing work", which
also records the ceiling (our method cannot reach D_A-finiteness).

Optional, not needed for the claim as now scoped: MathSciNet's citation
graph on BM-R 2002 (weekday guest pass, Pitt Hillman or CMU Hunt), or
asking Rechnitzer (UBC) directly. Both jasonp's call.

## CITATION GRAPH CRAWLED 2026-08-01 — no collision (was the standing action)
Done from the desk with two independent citation databases instead of
MathSciNet: **OpenAlex** and **Semantic Scholar**, both free APIs, driven by
`experiments/citation_crawl.py` (re-runnable; dump kept out of the repo).
Counts differ between sources, so neither is complete — but they disagree on
*coverage*, not on the answer.

Forward citations read, seed by seed:

| seed | OpenAlex | S2 | what cites it |
|---|---|---|---|
| BM-R 2002 (the criterion) | 83 | 74 | heaps/directed-animal combinatorics, prudent and column-convex polygons, Haruspicy 2/3, Mishna-Rechnitzer's non-holonomic quarter-plane walks, Guttmann's survey volume |
| Haruspicy 2 | 13 | 17 | same neighbourhood; newest is a 2025 J. Phys. A SAW paper |
| Haruspicy 3 | 4 | 4 | four items, none about a criterion |
| Chan-Rechnitzer 2018 | 20 | 2 | mostly a symbolic-dynamics book's chapters; one 2025 preprint |
| BBEP 2020 (Av(1324)) | 3 | 20 | permutation patterns only, through 2026 |

Extra seeds added on the way, because a colliding paper would have to cite
one of them: **Bell-Hu-Satriano** (5 citing), **Bell-Gerhold-Klazar-Luca**
(25 citing). Both citation sets are pure number theory / computer algebra —
no lattice model anywhere in them.

**Verdict: no collision.** Every descendant of BM-R that proves
non-D-finiteness uses the pole/singularity-accumulation route. Nobody in
these citation sets runs an arithmetic endgame on a family of slice growth
constants.

**One find worth the crawl** — the nearest arithmetic relative, better than
Bell-Hu-Satriano: Bell, Nguyen & Zannier, *D-finiteness, rationality, and
height*, Trans. AMS 373 (2020) 4889-4906, with part II (Adv. Math. 414, 2023)
and part III, the multivariate Polya-Carlson dichotomy (Math. Z. 306, 2024,
with S. Chen). Genuinely height-theoretic theorems about D-finite series —
but they bound the Weil heights of the *coefficients* and conclude
rationality, where ours bounds degree and house of the *slice growth
constants* and concludes a contradiction. Different configuration; and
their own forward citations (15 + 3 + 4) contain no combinatorial
application. Now cited in the paper's "Relation to existing work" paragraph,
which no longer rests on absence alone.

Two 2025 items checked and cleared: He, *Upper bounds for the connective
constant of weighted self-avoiding walks* (J. Phys. A, 2025) — Alm's
algorithm extended, SAWs and self-avoiding trails only, not site animals;
Liang, *Independent set enumeration ... of grid graphs and their variants*
(arXiv 2507.04007) — tensor-network numerics for hard-core models including
king graphs, estimates rather than rigorous bounds, and independent sets are
not animals.

**Still not done, still jasonp's if he wants belt-and-braces:** MathSciNet
(weekday walk-in guest pass, Pitt Hillman or CMU Hunt) and Google Scholar's
own "Cited by", which sees preprints and theses these two APIs miss.

### The original entry, for the record
**Nothing obtained so far has been forward-searched.** Every paper in this
session was found by keyword or by following references *backwards*; we have
never asked "who cites this?" for any of them. That is the one search
direction that could still surface a collision, because a 2026 paper reusing
BM-R's Lemma 9 with an arithmetic endgame would be invisible to every probe
run so far.

Do this when idle. Priority order, forward citations of:
1. **Bousquet-Melou & Rechnitzer 2002** (the criterion itself) — highest yield;
   anyone building on the non-D-finiteness test lands here.
2. **Haruspicy 2 and 3** — the programme's visible face.
3. **Chan & Rechnitzer 2018** — anyone extending CTM growth-rate bounds; would
   also catch a workaround for the locality/symmetry conditions we fail.
4. **Bevan-Brignall-Elvey Price-Pantone 2020** — anyone porting the
   inject-into-a-labelled-simpler-class template outside permutation classes.

Tooling: MathSciNet is the right instrument and needs a weekday walk-in guest
pass (Pitt Hillman or CMU Hunt, read-only — see the notes above). Google
Scholar's "Cited by" is the free approximation and can be done from the desk.

**Haruspicy 1 OBTAINED 2026-08-01** (jasonp, ScienceDirect) →
`papers/rechnitzer_2003_haruspicy1_anisotropic_gf.pdf`. Confirms the reading
above from the source: its content is the combinatorial section/density
machinery (coefficient of y^n rational, numerator degree <= denominator
degree, denominator a product of cyclotomic polynomials, plus a tight
multiplicative upper bound), not a D-finiteness test. Also filed from the
same issue: `klazar_2003_non_p_recursiveness_matchings.pdf` (Haruspicy 2's
reference [13], adjacent prior art on non-P-recursiveness).

## THIRD DATABASE: GOOGLE SCHOLAR, RUN BY jasonp 2026-08-01 — no collision
The optional belt-and-braces above, half-discharged: Scholar done, MathSciNet
still unrun (and now judged not worth the walk-in — see the verdict below).

Scholar's **"search within citing articles"** is full-text over its index, not
title/abstract, so it can hit a paper that uses a tool in a proof without ever
advertising it. That makes it a strictly different instrument from OpenAlex and
S2, which only matched metadata. Run over BM-R 2002's Cited-by (**79** — a
third count, against OpenAlex 83 and S2 74; all three disagree, as expected):

| term | hits | reading |
|---|---|---|
| `Northcott` | **0** | the discriminating search. Zero across 79 citing full texts. |
| `Mahler` | **0** | second discriminating search. Zero. |
| `algebraic degree` | ~9 | all false: degree of the *algebraic equation* a GF satisfies (Feretic's "degree-four algebraic equation", Le Borgne's approximants). Not degree of an algebraic number. |
| `height` | ~10 | all false, and the term is hopeless here: column height, path height, bargraph height. Carries no information. |
| `house` | 3 | all false (incidental prose). Expected — nobody indexes "the house of an algebraic number" usefully. |

`"growth constant" Northcott D-finite` and
`"transfer matrix" "algebraic degree" "not D-finite"` as plain Scholar
searches: **0 results each.**

Haruspicy 2's Cited-by (**14**; OpenAlex 13, S2 17) read in full. Contents:
Mishna-Rechnitzer's non-holonomic quarter-plane walks (iterated kernel —
analytic), BM's ICM survey, Mishna's book, BM-Brak "Exactly solved models"
(x2), He 2025 weighted-SAW connective constant (already cleared in the API
crawl), Clisby's AMS Notices survey, Richard's limit distributions (x2),
Schwerdtfeger's prudent polygons + thesis, Rechnitzer's own chapter version,
Beaton's thesis. Every one is construction, survey, or the
pole/singularity-accumulation route. Nothing arithmetic.

One item in that list was new to us and is the closest the whole sweep came:
**Assis, van Hoeij & Maillard, "The perimeter generating functions of
three-choice, imperfect, and one-punctured staircase polygons," J. Phys. A
(2016)** — the differential-algebra crowd, 8th-order linear Fuchsian ODEs.
Cleared at title/abstract level and the direction is opposite to ours: it
*constructs* ODEs for solvable models (D-finiteness demonstrated by exhibition),
it does not supply a criterion for proving a series non-D-finite. Not read in
full; not a collision.

**Verdict, three databases now: no collision.** Northcott-on-slice-growth-
constants is not in this literature, and the negative is stronger than the API
crawl's because Scholar searched full text rather than metadata. The paper's
scoping in `paper/polyplets-report.tex` ("we have not located ... a literature
search cannot establish absence") is unchanged and remains correct as written.

**MathSciNet: NOT RUN, and recommended closed rather than pending.** Its edge
over the APIs is curated indexing of journals they miss; but Scholar already
covers a superset of venues *and* searches full text, which is the property
that mattered for a proof-internal tool like Northcott. A weekday library
walk-in for a fourth negative on a question three sources have answered is not
a good trade. Reopen only if a referee asks.

## How to actually get these (researched 2026-08-07)

Full notes in the `library-access-pittsburgh` memory. The short of it:

- **Remote e-access is not purchasable** by an unaffiliated person; licences tie
  it to affiliation. Everything below is on-site or print.
- **Penn State is free to all Pennsylvania residents** — borrowing privileges at
  every PSU library on a PA licence/state ID. Open question worth one email to
  `ul-common-services@psu.edu`: does the resident card allow requesting from
  University Park, which is where 1980s J. Phys. A would live.
- **Pitt** guest account (on-site) or Special Borrower ($50 alumni / $100 other,
  books not journals). **Bevier** sci/eng library is Mon-Fri 9-5 only and is the
  real constraint. **CMU** guest pass gives two-hour sessions, on-site only.
- **Pre-1995 is the hard part**: IOP sells old content as a separate archive
  product, so a current IOPscience licence does not imply 1980-1993 access.
- **Email the authors.** For Barequet & Magal — one of the two load-bearing
  items — this is likely faster than any library, and we already hold five
  Barequet papers.

## From the 2026-08-13 reading pass (citation chase over the 11 fetched PDFs)

Wanted, no arXiv version found (arXiv API title/author queries run 2026-08-13;
plain web "title + pdf" search NOT yet run on these):

- Rands & Welsh, "Animals, trees and renewal sequences," IMA J. Appl. Math. 27
  (1981) 1–18. — The renewal identity P(n) = sum Q(i)P(n-i) over inconstructible
  animals; if stated lattice-generically it hands polyplets the same identity,
  and with it Bui's conditional upper-bound machinery (arXiv:2211.14909 §4).
  Also the general-lattice framework G-P cite for the old honeycomb bound. [med]
- Delyon, "Taille, forme et nombre des amas dans les problèmes de percolation,"
  Thèse de 3ème cycle, Univ. Pierre et Marie Curie, 1980. — The original
  cluster-size non-decay result the Hammond/G-P equality-at-p_c chain builds
  on. French 3rd-cycle thesis, no DOI; likely unobtainable. [low]
- Barequet & Ben-Shachar, "Algorithms for counting minimal-perimeter lattice
  animals" (cited as under submission, 2020; check for the published version).
  — The tool for extending our king |M_n| sequence (1,2,6,1,8,2,22,6,1,30,...,
  no OEIS match) without brute force. [med]
- Gaunt & Peard, "1/d-expansions for the free energy of weakly embedded site
  animal models of branched polymers," J. Phys. A 33 (2000) 7515–7539. — The
  degree/dimension-expansion literature; Barequet–Shalah's arXiv v2 cites it as
  a broken "[?]" at their p.7523/Eq. 4.9 use. IOP, pre-arXiv-era physics. [low]
- Harary & Harborth, "Extremal animals," J. Comb. Inf. Syst. Sci. 1 (1976)
  1–8. — Earliest extremal min/max perimeter across lattices; the most likely
  place a king-lattice perimeter statement already exists. [low]

## Claude's re-try pass, 2026-08-18

**One entry came free, and it mattered.** The Asinowski–Barequet–Zheng
conference slides ("Enumeration of polyominoes with fixed perimeter defect",
Séminaire Lotharingien 79) are free at
`mat.univie.ac.at/~slc/wpapers/s79vortrag/asinowski.pdf` and were pulled in
full text. They carry the k = e + 2f defect identity and the theorem that each
fixed-defect generating function is rational with cyclotomic denominator — both
of which L6 had been treating as its own. See
`docs/priority-passes-2026-08-18.md` §L6.

The underlying paywalled paper is still wanted: the slides state the theorems
without the proofs, and the pattern-classification method behind them is what
would say whether the king column is a corollary of their framework or a
separate derivation.

**Lesson recorded, not just the entry.** Two of the three collisions found in
the 2026-08-18 priority passes came from pulling full text of sources already
listed here, not from new keyword searches. Re-try this file before searching.

## Claude's second re-try pass, 2026-08-18 (later) — the ABZ paper is OBTAINED

**The underlying paywalled ABZ paper is no longer wanted.** The full text with
proofs is free from Simon Plouffe's OEIS citation mirror,
`plouffe.fr/OEIS/citations/3174304.3175272.pdf` — it is the ANALCO 2018 paper
A. Asinowski, G. Barequet & Y. Zheng, "Polycubes with small perimeter defect,"
Proc. ANALCO 2018, 93–100 (SIAM), the 3-dimensional companion to the ENDM 2017
polyomino note the slides were drawn from. Filed as
`papers/asinowski_barequet_zheng_2018_polycubes_small_perimeter_defect.pdf`.
Read; verdict in `docs/priority-passes-2026-08-18.md` §ABZ full text.

**Method note for whoever chases the remaining wants:** that mirror is a flat
directory of ~800 PDFs at `plouffe.fr/OEIS/citations/`, filenames mostly
opaque ACM/DOI ids, no search. Grepping its index for our author names yields
nothing else — `conway.pdf`, `harborth.pdf` and `harborth_diss.pdf` are all
false friends (Grassmannian packings; a Magdeburg scheduling dissertation by a
different Harborth). **Do not re-grep that index.** It was found by a title
search that happened to surface the mirror, so title searches are still the
route; the mirror itself is exhausted for us.

**Still wanted, and re-confirmed unobtainable this pass:**

- **Barequet & Magal 2023 (Comput. Geom. 108, 101919)** — no preprint, no
  conference version, no author PDF. Barequet's publications page carries no
  hrefs at all now and instead offers a reprint-request mailto. **The remaining
  high-priority perimeter-defect want.** [high]
- **Andrews, Memoirs AMS 301** — `ams.org/memo/0301/memo0301.pdf` exists and
  returns an access page, not the PDF, to an unaffiliated fetch. Unchanged:
  library job. [high]
- **Rands & Welsh 1981** — OUP `academic.oup.com/imamat/article-abstract/27/1/1`,
  abstract only, no free copy anywhere. [med]
- **Barequet & Ben-Shachar, minimal-perimeter counting** — the published version
  is *Algorithmica* **85**(1) (2023) 75–99, "Algorithms for Counting
  Minimum-Perimeter Lattice Animals," doi 10.1007/s00453-022-01008-9. No arXiv.
  Metadata pinned; the citation can now be given correctly even unread. [med]
