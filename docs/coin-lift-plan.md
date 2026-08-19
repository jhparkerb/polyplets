# Coin Lift — the program, its gates, and the one thing it cannot be

> **CLOSED 2026-08-14, at G2. Coin Lift is dead.** The char-2 collapse does
> not survive one lift: mu_2/mu_1 grows every height (1.00, 1.13, 1.30, 1.48,
> 1.73, 2.00 at H = 4..9) and mu_4 is the generic rank exactly. G3 and G4 do
> not run. Coin Flip, Coin Roll and Biased Coin Flip are untouched — one
> deterministic bit, or a probabilistic fingerprint. Measurement, the restated
> gate, and the other characteristics: `results/coin-lift-g2.md`. G1 stands on
> its own for those three: the collapse itself holds to H = 11 measured
> (rank 912 = 0.445 x 2^11).
>
> **And the survivors cannot be extended either, by theorem.**
> `results/coin-flip-characteristic-landscape.md`: every weighted automaton
> over every commutative ring has dimension at least min_p rank_{F_p}; field
> extensions of char 2 are rank-identical; multiplicative grading is exactly
> rank-preserving (so Coin Roll is free by theorem); and a determinantal-
> divisor budget makes the surviving sweep finite and certifies it at
> H = 6..9. At H = 6, p = 2 is the only prime in the universe that drops the
> rank at all. One deterministic bit is the unique optimum of the class, not
> the best thing found in it.

**Coin Flip** is the hypothetical algorithm that computes T(n,H) mod 2 through
the characteristic-2 rank collapse of the strip-counting functional. **Coin
Roll** is its area-graded form: one run, every n, free. **Biased Coin Flip**
weights cells randomly over GF(2^k) so a false pass costs 40/2^k. **Coin Lift**
is the deterministic ambition: lift the collapse from GF(2) to Z/2^k and read
exact values, with no probability anywhere.

Target: the residual band Motley cannot sweep — after `docs/motley-plan.md`,
T(40,20), T(40,21), T(40,22)
<!--q:row40_residual.cells@19=T(40,20)..T(40,22)--> (generated in
`results/residual-cells.md`).

## 0. The measured ground, quoted

`experiments/tristruct/r3_inv_rank_probe.py`, log banked alongside. The object
is the height-H strip automaton: alphabet = the 2^H - 1 nonempty column fills,
f(w) = [the placed cells form exactly one king-connected component]. It is
deterministic, so the Hankel rank of f over a field equals the dimension of the
observability closure, and that rank is a **floor for any field-linear
realization** of the count.

| H | states (Motzkin(H+1)-1) | rank GF(2) | rank GF(2^16) graded | rank mod 2^31-1 |
|---|---|---|---|---|
| 4 | 20 | 6 | 6 | 6 |
| 5 | 50 | 15 | 15 | 17 |
| 6 | 126 | 27 | 27 | 35 |
| 7 | 322 | 58 | 58 | 88 |
| 8 | 834 | 112 | 112 | 204 |
| 9 | 2,187 | 229 | 229 | 501 |

Two facts, both load-bearing:

- **char-2 collapse**: rank tracks 0.42-0.45 x 2^H, against a mod-p rank
  growing ~2.45x/height. Extrapolated to H = 21: **9.2e5 in char 2**,
  **~2.3e7 mod p**, against 4.0e8 incumbent states and 9.4e8 Motley states.
- **grading is free in char 2**: GF(2^16) graded rank equals ungraded GF(2)
  rank at every measured point, six for six. This is what makes Coin Roll
  free, and it is the only evidence that *any* weighting survives the collapse.

## 1. The exclusion — state it before anything else

**Coin Lift cannot produce exact values at char-2 dimension.** The argument
uses only numbers in the table above.

Suppose a Z/2^k realization of dimension D existed for every k. Their inverse
limit is a Z_2-realization of dimension <= D, hence a Q_2-realization, so the
Hankel rank of f over Q_2 — which equals its rank over Q, the entries being
integers — is at most D. But reduction mod p can only *drop* rank, so
rank_Q >= rank_{F_p} for every p, and rank_{F_p} is measured: 501 at H = 9,
extrapolating to ~2.3e7 at H = 21.

So **D >= 2.3e7 at H = 21 — twenty-five times the char-2 dimension** — and
that is a floor, not a construction. The picture of a megabyte-scale exact
engine is excluded by the repo's own mod-p measurements.

What the argument does *not* exclude: a Z/4 or Z/8 realization at or near the
char-2 dimension. The inverse limit needs all k; a fixed small k is untouched
by it. **Two or three deterministic bits per cell remain live**, and that is
the honest ceiling of this program until measured otherwise.

**G2 measured it.** The limit argument leaves a fixed small k alone, but the
module itself does not: mu_2 = 459 and mu_4 = 501 = the generic rank at
H = 9. The ceiling above was the right ceiling and the floor came up to meet
it at the first lift.

Restating the program's realistic payoff, so nobody rediscovers it late:

| variant | what it yields per cell | excluded? |
|---|---|---|
| Coin Flip | 1 deterministic bit | no |
| Coin Roll | 1 bit, every n, free | no |
| Biased Coin Flip | false pass 40/2^k, probabilistic | no |
| **Coin Lift to Z/4, Z/8** | 2-3 deterministic bits | **yes, by G2 as measured — the dimension is the generic one** |
| Coin Lift to exact values | the value | **yes, by §1** |

## 2. Gates, in order, cheapest first

### G1 — does the collapse hold above H = 9? (hours to a day)

Extend the ladder to H = 10, 11, 12, and H = 13 if it is wanted overnight. The
probe's cost grows ~7x/height (6 s at H = 8, 44 s at H = 9), so H = 12 is a
few hours and H = 13 is an overnight run; the observability closure, not the
rank, is the limit.

**Kill:** if rank departs from 0.44 x 2^H — in particular if it turns toward
the mod-p 2.45x/height curve — the whole program ends here, in a day.

### G2 — does the collapse survive to Z/4 and Z/8? (hours) — RUN, AND IT KILLED

**As first written this gate could never have fired**, and the correction is
worth carrying to any future gate of the same shape. "The Z/4 free rank" — the
number of invariant factors that are units mod 4 — counts the *odd* invariant
factors, and a factor is odd iff it survives reduction mod 2. It is
identically the GF(2) rank the ladder already measured. Nothing can jump.

The well-posed object is the minimal number of generators of the Hankel column
module over Z/2^k, the floor on the dimension of any Z/2^k realization:

    mu_k(H) = #{ invariant factors d_i with v_2(d_i) < k },
    mu_1 = rank GF(2),   mu_inf = rank_Q >= rank_{F_p}.

**Prior: poor.** The likely mechanism for the collapse is x + x = 0 — the
degeneracy that thins the cut algebra in characteristic 2 — and it dies mod 4.
CKN's rank bounds are GF(2) statements for the same reason.

**The prior was right.** At H = 9: mu_1 = 229, mu_2 = 459, mu_3 = 500,
mu_4 = 501 = the generic rank exactly. The second bit costs a factor that
*grows* with height rather than a constant overhead. Kill fired;
`results/coin-lift-g2.md`. Other characteristics were asked at the same time
and answer the same way: p = 3 thins 501 to 488 at H = 9, p = 5 and p = 7 not
at all, and extension fields of char 2 cannot help because rank is invariant
under field extension.

### G3 — is the basis describable *without* the incumbent's automaton?

**Does not run: G2 killed the program.** Kept because the hazard it names is
general — any compressed realization obtained by projecting the incumbent's
automaton inherits the incumbent's rule and certifies nothing — and the next
compression idea will meet it too.

**This gate decides whether the program is worth anything at all, and it is
easy to miss.** The probe builds the automaton from the incumbent's rule —
union-find over column partitions with stranded-component death — and
computes the collapse by projecting it. **A compressed realization obtained by
projection inherits the incumbent's rule and provides no rule-independence
whatsoever.** It would check the incumbent's implementation against itself.

Independence requires the compressed basis to have a combinatorial description
derived from the *definition* of king-connectivity, with transitions written
from that description — the way CKN's representative sets are constructive for
matchings.

Work: extract explicit bases at H = 6..11 from the closure, look for an index
set (subsets? parity classes? matchings-like objects?), guess the general form,
test the guess at H = 12.

**Kill:** no describable structure by H = 12, and the program yields a check
that cannot certify anything the incumbent doesn't already assert.

### G4 — are the compressed transitions affordable?

**Does not run: G2 killed the program.**

The alphabet is 2^H - 1 column fills. A dense compressed transition costs
~2^H x D^2 per column: at H = 21 with D = 9.2e5 that is **1.8e18** — hopeless.
Sparsity or a factored transition form is a hard requirement, not an
optimisation.

**Kill:** dense transitions with no factorisation. Price this at H = 10-12
against the extracted basis, before anyone builds anything.

## 3. If all four gates pass — they did not; this section is dead as written

- Build the compressed realization over Z/2^k for the largest k that survives
  G2, with transitions from G3's description.
- Validate against banked T(n,H) mod 2^k for every H <= 16 — hundreds of cells,
  free, and a real RED battery (planted stencil defect must fail).
- Run the residual band. Compare against the incumbent's swept values at
  H = 20, 21 and against the P_k predictions at H = 22.
- Note the asymmetry: above H = 21 the incumbent never swept anything, so the
  comparison there is against a formula, and only exact values (excluded by
  §1) or parity are available.

## 4. Separate lead, recorded so it is not lost

The mod-p Hankel rank at H = 21 extrapolates to ~2.3e7 against the incumbent's
4.0e8 column states — a **17x exact-arithmetic floor that nothing constructs**.
A-S1 measured it and called it non-constructive headroom; it is still that. It
is a bigger prize than Coin Lift (exact values, all characteristics) and a
harder one (no collapse mechanism is known to explain it). Not part of this
program; worth a line in any future algorithm hunt.

## 5. Cost summary

| stage | cost | decides |
|---|---|---|
| G1 rank ladder to H = 12 | hours | is there a collapse to build on — **yes to H = 10 measured** |
| G2 Z/4, Z/8 module structure | ~90 min, spent | is Coin Lift more than one bit — **no. KILL** |
| G3 basis structure | days to weeks | not run |
| G4 transition density | days | not run |
| build + validate + run | weeks | not run |

G1 and G2 together are under a day and price the entire program. **Nothing
downstream should start before both have landed.**
