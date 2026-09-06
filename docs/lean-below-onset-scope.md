# Lean and the below-onset frame: what is formalizable, what is a certificate

2026-08-22, executing `docs/time-at-the-bar.md` B5. Written from the module
inventory, not from a plan: 86 sorry-free modules under `polyplets/Polyplets/`,
`polyplets/PROOF-STATUS.md` as the status of record.

B5's instruction was to **split the scope honestly before anything is
attempted**, decide whether the frame is worth the Lean hours, and if it is not,
say in `PROOF-STATUS.md` that the newest result is the one the formalization
does not reach. This is that split. **Nothing is started here.** The decision is
jasonp's and the last section is what it is between.

## The gap, stated precisely

`Grand/PinGrand.lean` certifies the production polynomials `P_1..P_16` for all
`n ≥ 2k+1` from exactly **two real-swept cells per level**:

    A_k = T(2k+1, k+1)      B_k = T(2k+2, k+2)

Both sit **at or above** the onset. That is the whole of what Lean currently
knows about how a level gets pinned.

Undertow replaces one of those anchors with a cell **below** the onset,
corrected by the defect `D_j(k)`. a(41) rests on that substitution, and Lean has
no statement of it. So the missing theorem is not deep in the machinery — it is
one substitution lemma away from work already finished, and that is what makes
it worth pricing rather than dismissing.

## What Lean already has, and what it does not

| piece | module | status |
|---|---|---|
| the diagonal law's *shape* | `Shape.lean` | theorem |
| the grand form | `Grand/*` | theorem, standard axioms |
| pinning from two **onset** cells | `Grand/PinGrand.lean` | `P_1..P_16`, 26 anchors for levels 4..16 |
| the depth-`j` assembly arithmetic | `DepthAssembly.lean` | the `(C)`/`(D)` identities, as exact rational arithmetic |
| **the below-onset identity itself** | — | **absent** |
| **that a corrected below-onset cell may substitute for an anchor** | — | **absent** |

`DepthAssembly.lean` is the piece most likely to be mistaken for coverage it does
not give. It formalizes `D_j(k) = [z^(k+1−j)] D(z)` as a finite exact-rational
assembly of the excess-graded cluster weight families, which is real and is
sorry-free. But its `sigTable`, `bbTable` and `ppTable` are `def`s carrying
hardcoded data, and its theorems take `(sig bb pp : BivZ)` as **hypotheses** —
they say "if the tables are these, then `D_1(k)` is that". The tables come from
the family DP. **They are certificates, not theorems**, and the module is
honest about being parameterized on them.

## The split

**Formalizable — the frame.** Given `D_j(k)` as an opaque rational, two things:

- **(F1)** the below-onset identity: for `n = 2k+1−j`,
  `T(n, n−k) = (P_k(n) + D_j(k))·3^(n−1−3k)` — that the corrected value lies on
  the same polynomial;
- **(F2)** the substitution: two such equations, or one of them together with one
  real onset cell, pin the level — i.e. `PinGrand`'s anchor pair may have a
  member replaced by a corrected below-onset cell.

F2 is nearly bookkeeping once F1 exists: `PinGrand` already does the linear
algebra, and F2 says the new equation is of the same form. **F1 is the work**,
and it is grand-form-shaped — it is a statement about the same staircase
identity, extended one step past its stated range, with a named error term.

**Not formalizable now — the values.** That `D_j(k)` *is* what the family DP
says it is. That needs the DP's correctness against the combinatorial
definition, which is a different and much larger project, and it is the same
class of input as the cluster weight tables `PinGrand` already depends on.

Stating it that way is what makes the split honest: **Lean would not be
certifying a(41), it would be certifying that a(41)'s argument is valid given
the same kind of certificate the existing proof already takes on trust.** That
is a real gain — it removes a step of hand-reasoning from the newest result — and
it is a smaller gain than "a(41) is proved", which nobody should be able to read
into it.

## The honest cost

I am not going to quote hours. What can be said from the tree:

- `Grand/PinGrand.lean` is **machine-generated** by `scripts/gen_grand_pin.py`.
  If F1 lands, F2's per-level instances are generated the same way, so the
  per-level cost is a generator change and not 16 hand proofs.
- F1 has no precedent in the tree to copy. `Shape.lean` and the `Grand/` chain
  are the nearest work, and the below-onset extension is not a special case of
  either — it is one step outside the range the staircase is proved on.
- There is no gate. `polyplets/PROOF-STATUS.md` says it plainly: no `make` gate
  runs Lean, the Linux boxes have no toolchain, and the only thing between the
  tree and a red one is somebody typing `lake build` on gympie. Any Lean work
  inherits that, and the 2026-08-19 duplicate-declaration incident — 8643 green
  module targets and a red root, unnoticed for a whole campaign — is what that
  risk looks like in practice.

## The recommendation, and it is a recommendation and not a decision

**Do not start F1 now.** Two reasons, in order:

1. It is not on the landing path. `docs/pre-landing.md` does not need it, and B1 —
   the gate sweep, done — was the item about the repository being trustworthy.
   F1 makes the repository *more proved*, which is a different axis and a slower
   one.
2. The cheaper half of its value is available immediately by writing the gap
   down, which is what B5's fallback asks for and what the next section does.

If it is started, start with F1 alone and stop there until it is green: F2
without F1 is worth nothing, and F1 without F2 is still a publishable statement
about the diagonal law past its onset.

## What goes in `PROOF-STATUS.md` if F1 is not started

A short section saying, in the file's own register, that **the formalization
covers the route a(40) took and not the route a(41) took** — that `PinGrand`
pins from two onset cells, that Undertow's below-onset substitution is not
stated in Lean, and that `DepthAssembly` formalizes the arithmetic of `D_j`
while taking its weight tables as inputs. A reader who sees "86 sorry-free
modules" and "the grand form against standard axioms" should not have to
reconstruct which of the project's results that covers.

That note is one paragraph, it costs nothing, and it is the part of B5 that
should happen whatever is decided about the Lean hours.
