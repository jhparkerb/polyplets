# The cut-count cancellation identity

Thread **Birthright**, 2026-08-14. Tier 1 of `docs/b1-closure-plan.md` §7: the
mathematical content of the Motley/B1 second-source engine, stated in closed
form and proved as combinatorics. Ground truth for the rule is the banked
source `results/cutcount_b1/cutcount_b1.cpp.59e90660` (sha256
`59e90660b42a0d94ceae5459287db35b4d93f87a5e62753ccd549235edaa8d3d`), lines
93–173 — `slot`, `canon`, `gather`, `shifted`, `successors`. The core of
`experiments/cutcount/cutcount_b1_probe.cpp` is byte-identical over those
lines, so there is one rule, not two.

No program appears in the proof. The engine, its 256-bit arithmetic, its
window state and its translation accounting are all outside the statement;
what is proved here is a fact about finite sets of cells.

## 0. Vocabulary

The objects are those of `polyplets/Polyplets/Defs.lean`: `kingAdj p q` is
Chebyshev-distance-one adjacency (`p ≠ q ∧ |p.1 − q.1| ≤ 1 ∧ |p.2 − q.2| ≤ 1`)
and `KingConnected S` is pairwise reachability inside `S` under that relation,
shown equivalent to `SimpleGraph.Reachable` in `kingGraph S` by
`kingConnected_iff_reachable` in `Polyplets/Graph.lean`. This document is a
paper proof and cites that vocabulary only for agreement on definitions; it is
not a Lean task.

Write `c(S)` for the number of king-connected components of a finite cell set
`S`, with `c(∅) = 0`.

## 1. Setup: board, scan order, window

Fix integers `H ≥ 1` (height) and `W ≥ 1` (width) and let

    Γ = { (r, c) : 0 ≤ r < H, 0 ≤ c < W }

be the board, with cells written (row, column). The **scan order** is the
engine's loop order — `for c … for r …` in `run_height` — so cell `(r, c)` has
scan index

    ord(r, c) = c·H + r,

and `u ≺ v` means `ord(u) < ord(v)`. For a cell `v` the **window** is the block
of `H + 1` cells immediately preceding it:

    Win(v) = { u ∈ Γ : ord(v) − (H+1) ≤ ord(u) ≤ ord(v) − 1 }.

This is exactly the engine's frontier key: `slot k` of the key holds the label
of the cell `k + 1` positions back, for `0 ≤ k ≤ H`. Unrolling the indices,
slot 0 is `(r−1, c)`, slot `H−2` is `(r+1, c−1)`, slot `H−1` is `(r, c−1)` and
slot `H` is `(r−1, c−1)` — the north, south-west, west and north-west
neighbours, which are precisely the four king neighbours of `(r, c)` that
precede it in scan order. `gather` reads those four slots under exactly those
in-board guards.

For `v ∈ S` put

    N⁻(v) = { u ∈ S : kingAdj u v and u ≺ v }.

**Lemma 1 (king reach).** If `u` and `v` are king-adjacent cells of `Γ` with
`u ≺ v`, then `1 ≤ ord(v) − ord(u) ≤ H + 1`; in particular `u ∈ Win(v)`, so
`N⁻(v) ⊆ Win(v)`.

*Proof.* Write `Δr = r_v − r_u` and `Δc = c_v − c_u`, both in `{−1, 0, 1}` by
king adjacency, not both zero. Then `ord(v) − ord(u) = H·Δc + Δr`. If `Δc = −1`
this is `−H + Δr ≤ −H + 1 ≤ 0`, contradicting `u ≺ v`; the only way to reach 0
would be `H = 1` with `Δr = 1`, impossible because `H = 1` forces `r = 0` for
every cell. So `Δc ∈ {0, 1}` and `H·Δc + Δr ≤ H + 1`. ∎

The bound is attained (for `H ≥ 2`) by the north-west neighbour, `Δc = Δr = 1`.
For `H = 1` there is no vertical step and the largest gap is 1. The check
script measures both, per board.

## 2. The colouring model

Fix `S ⊆ Γ`. A **configuration** of `S` is a map `φ : S → ℤ_{>0}` built by
visiting the cells of `S` in scan order and, at each `v`, obeying:

- **clash.** If `φ(N⁻(v))` has two or more elements, the configuration is
  **void** and is discarded.
- **forced.** If `φ(N⁻(v))` is a single label `ℓ`, then `φ(v) = ℓ`.
- **free.** If `N⁻(v) = ∅`, let

      L_φ(v) = φ( S ∩ Win(v) ),      b_φ(v) = |L_φ(v)|

  be the set of **live labels** at `v` and their number. Then either
  `φ(v) ∈ L_φ(v)` (**adopt**), or `φ(v)` is the next unused label, i.e. one
  more than the number of births so far (**birth**).

Let `Cfg(S)` be the set of non-void configurations and `B(φ) ⊆ S` the set of
cells at which `φ` gave birth. The **weight** of `φ` is the polynomial

    w(φ) = Π_{v ∈ B(φ)} ( q − b_φ(v) )   ∈ ℤ[q],

an empty product being 1.

Three points where this is the code and not a paraphrase of it. First, adopt
offers *every* live label, including labels of blocks the cell does not touch —
`successors` loops `for (x = 1; x <= mx; x++) if (present[x])`, with no
adjacency test. Second, `b` is the number of distinct live **labels**, not of
live components: `successors` counts distinct ids present in the window, so two
components that share a colour are counted once. Because adopt lets one
component take another's colour, that distinction is real, not cosmetic. Third,
"live" means *in the window*, so a label whose last cell has left the window is
gone and is not counted in `b` — which is why the engine can recycle colours.

## 3. The identity

> **The cut-count cancellation identity.** For every `H, W ≥ 1` and every
> `S ⊆ Γ`,
>
>     Σ_{φ ∈ Cfg(S)}  Π_{v ∈ B(φ)} ( q − b_φ(v) )  =  q^{c(S)}      in ℤ[q].

The equality is in `ℤ[q]` itself, with no truncation. This is stronger than
what §7 and the engine's header claim, and it is discussed in §6 below.

**Corollary (what the engine reads off).** Summing over all `S ⊆ Γ` with
`|S| = n` and reducing mod `q²`,

    A_n(q) = Σ_{|S| = n} q^{c(S)} ≡ (#{S : |S| = n, S king-connected})·q  (mod q²),

so `[q¹] A_n(q)` counts the connected `n`-cell subsets of the board and
`[q⁰] A_n(q) = 0` for `n ≥ 1`. Setting `q = 1` gives `Σ_{φ} w(φ)|_{q=1} = 1`
for every `S`, so the `q = 1` evaluation counts all subsets, `C(HW, n)`. Those
two consequences are exactly the engine's `q0_zero` and `q1eval_binomial`
self-checks; note that neither of them consults connectivity, which is why
`results/motley-step0.md` is right that only comparison against independently
computed values can catch the rule going wrong.

## 4. Proof

Throughout, `S` is fixed with components `C_1, …, C_c` (`c = c(S)`), numbered
so that their scan-minima satisfy `v_1 ≺ v_2 ≺ … ≺ v_c`, where
`v_i = min_≺ C_i`.

**Lemma 2 (survivors are constant on components).** `φ ∈ Cfg(S)` if and only if
`φ` is constant on each component of `S` and is generated by the rules of §2.

*Proof.* (⇒) Let `φ` be non-void and suppose `u, v ∈ S` are king-adjacent with
`u ≺ v`. Then `u ∈ N⁻(v) ≠ ∅`, so `v` was handled by the clash or forced rule;
non-void means the forced rule, so `φ(v) = φ(u)`. Adjacent cells therefore
carry equal labels, and by induction along paths `φ` is constant on components.
(⇐) Immediate: constancy is what the forced rule produces and what the clash
rule fails to violate. ∎

**Lemma 3 (component minima are free; nothing else is born).** For each `i`,
`N⁻(v_i) = ∅`, so `v_i` is a free cell. Conversely, for `φ ∈ Cfg(S)`,
`B(φ) ⊆ {v_1, …, v_c}`.

*Proof.* A king neighbour of `v_i` lying in `S` lies in `C_i`; if it preceded
`v_i` it would contradict minimality, so `N⁻(v_i) = ∅`. For the converse, let
`v ∈ B(φ)` and let `C` be its component with minimum `m`. By Lemma 2,
`φ(m) = φ(v)`. If `v ≠ m` then `m ≺ v`, so the label `φ(v)` is already in use
before `v`, and birth assigns an unused label — contradiction. Hence `v = m`. ∎

**Lemma 4 (the adopt branch a component needs is always on offer).** Let
`φ ∈ Cfg(S)` and let `v ∈ C_i` be a free cell with `v ≠ v_i`. Then
`φ(v_i) ∈ L_φ(v)`; that is, the component's own label is live at `v`, so the
required adopt branch exists.

*Proof.* Let `A = { u ∈ C_i : u ≺ v }`, non-empty since `v_i ∈ A`, and
`B = C_i \ A`, non-empty since `v ∈ B`. `C_i` is king-connected, so choose a
path inside `C_i` from `v_i` to `v`, let `y` be its first vertex lying in `B`
and `x` its predecessor on the path, so `x ∈ A`, `y ∈ B`, and `x`, `y` are
king-adjacent. Then `ord(x) < ord(v) ≤ ord(y)`, and by Lemma 1
`ord(y) − ord(x) ≤ H + 1`, whence

    ord(v) − ord(x) ≤ ord(y) − ord(x) ≤ H + 1,

so `x ∈ Win(v)`. By Lemma 2, `φ(x) = φ(v_i)`, so `φ(v_i) ∈ L_φ(v)`. ∎

Lemma 4 is where the window size earns its place, and it is the reason Lemma 1
belongs to Tier 1 rather than Tier 2 (see §6).

**Lemma 5 (configurations are choice sequences).** The map sending
`φ ∈ Cfg(S)` to the sequence of its choices at `v_1, …, v_c` — for each `i`,
either "birth" or "adopt `ℓ`" for a specific live label `ℓ` — is a bijection
onto the set of sequences realisable by the rules, and

    w(φ) = Π_{i : choice i is birth} ( q − b_φ(v_i) ).

Moreover `b_φ(v_i)` depends only on the choices at `v_1, …, v_{i−1}`.

*Proof.* Injectivity: the choices at `v_1, …, v_c` determine `φ(v_i)` for all
`i`, and by Lemma 2 `φ` is then determined on all of `S`. Surjectivity: given
any realisable sequence, every remaining cell of `S` has its label determined —
non-free cells by the forced rule, and free cells `v ≠ v_i` of `C_i` by
Lemma 2, with the adopt branch available by Lemma 4. The resulting `φ` is
constant on components, hence non-void by Lemma 2. The weight formula is
Lemma 3. Finally, no cell of `C_j` with `j > i` precedes `v_i` (their minima
come later), so `S ∩ Win(v_i)` meets only `C_1, …, C_{i−1}`, whose labels are
fixed by the earlier choices. ∎

**Proof of the identity.** For `1 ≤ i ≤ c+1` and a history `h` of choices at
`v_1, …, v_{i−1}`, let

    F_i(h) = Σ over choices at v_i, …, v_c consistent with h
             of the product of their weights.

We show `F_i(h) = q^{c−i+1}` for every `i` and every `h`, by downward induction
on `i`. For `i = c+1` the sum is over the empty sequence and `F_{c+1}(h) = 1`.
For `i ≤ c`, write `b = b_φ(v_i)`, which by Lemma 5 is determined by `h`. The
choices at `v_i` are the `b` adopt branches, each of weight 1, and the single
birth branch, of weight `q − b`. Applying the induction hypothesis to each
resulting history,

    F_i(h) = b · 1 · q^{c−i} + (q − b) · q^{c−i} = ( b + q − b ) · q^{c−i}
           = q^{c−i+1}.

The value does not depend on `b`, so it does not depend on `h`, which is what
makes the induction go through. Taking `i = 1` and using Lemma 5,

    Σ_{φ ∈ Cfg(S)} w(φ) = F_1(∅) = q^c = q^{c(S)}.   ∎

That is the whole cancellation: at each component minimum the `b` adopt terms
of weight 1 and the birth term of weight `q − b` sum to `q` regardless of `b`,
and because the branches downstream contribute a factor independent of `b`, the
`b`-dependence never reaches the total. The "join a block it does not touch"
branch is not an optimisation — it is the term that cancels `−b`.

**Where each ingredient is used.** Removing the clash rule breaks Lemma 2;
counting all labels rather than live ones breaks the `b + (q − b)` sum at the
one place it must hold; removing adopt leaves `q − b` alone, off by `b`;
shrinking the window breaks Lemma 4, or — if the window also bounds what the
clash rule can see — Lemma 1 and hence Lemma 2. The verification script
mutates each of these in turn and each mutation fails at small size.

## 5. Verification

`experiments/birthright_identity_check.py` checks the identity **as stated
above**, not the engine: it enumerates the model of §2 directly by brute force
over every subset of ten small boards, sums weights exactly in `ℤ[q]`, and
compares against `q^{c(S)}` with `c(S)` from flood fill. It also audits
Lemma 4 (every free non-minimal cell, is its component's label live?) and
measures the king reach of Lemma 1. Pure `python3` stdlib.

Run on **dalby**, 2026-08-14 23:18 UTC, python 3.13.12, script sha256
`d2dc1fbf763b2ffd2e1aba32a2cd14f43ee1444f0a13708b290aa1dcb76dc672`
(the run was routed to dalby because ayr was unreachable — `ssh: connect to
host ayr port 22: No route to host` — and no project code may run on gympie):

```
Birthright identity check
boards: 1x6, 1x10, 2x5, 2x7, 2x8, 3x4, 3x5, 4x3, 4x4, 5x3

board  cells  subsets   configs  H+1  reach  loc_checks  maxgap  result
1x6       6       64       101    2      1           0       0  OK
1x10     10     1024      2575    2      1           0       0  OK
2x5      10     1024      1220    3      3           0       0  OK
2x7      14    16384     21892    3      3           0       0  OK
2x8      16    65536     92736    3      3           0       0  OK
3x4      12     4096      5315    4      4         880       2  OK
3x5      15    32768     45516    4      4        8944       2  OK
4x3      12     4096      5817    5      5        1264       3  OK
4x4      16    65536    100709    5      5       27376       3  OK
5x3      15    32768     56054    6      6       15088       4  OK

GREEN totals: boards=10 subsets=223296 configurations=331935 mismatches=0
locality lemma: 53552 open-component free cells checked, 0 failures
wall_s=5.4

RED controls (each must fire):
RED-1  clash-voiding dropped                  FIRED   H=3 W=4 S=[(0, 0), (2, 0), (1, 1)]  sum=[0, 0, 1]  q^c=[0, 1]
RED-2  b counts all labels, not live ones     FIRED   H=1 W=6 S=[(0, 0), (0, 3)]  sum=[0, -1, 1]  q^c=[0, 0, 1]
RED-3  free cell cannot adopt a live label    FIRED   H=1 W=6 S=[(0, 0), (0, 2)]  sum=[0, -1, 1]  q^c=[0, 0, 1]
RED-4  window of H cells, neighbours outside it unseen FIRED   H=2 W=5 S=[(0, 0), (1, 1)]  sum=[0, 0, 1]  q^c=[0, 1]
RED-5  liveness window shortened to H-2       FIRED   H=3 W=4 S=[(0, 0), (2, 0), (1, 1)]  sum=[0]  q^c=[0, 1]

RESULT: GREEN (identity holds on every subset of every board; all 5 RED controls fired)
```

223,296 subsets, 331,935 configurations, 0 mismatches, in 5.4 s; 53,552
instances of Lemma 4 checked with 0 failures. Every number quoted in this
document is printed by that script.

Two things the numbers say beyond "it passes".

**The reach bound is tight where it can be.** The `reach` column equals `H + 1`
on every board with `H ≥ 2`, attained by the north-west neighbour, and equals 1
for `H = 1`, which has no diagonal step. Lemma 1 is not slack.

**Liveness alone would fit in a shorter window.** The `maxgap` column — the
largest distance from a free cell back to the nearest earlier cell of its own
component — is `H − 1` on every board with `H ≥ 3`, two short of the window.
Sharpening the proof of Lemma 4: if `v` is free then `y ≠ v` (else `x` would be
an earlier neighbour of `v`), so `ord(v) − ord(x) ≤ H`, and a gap of exactly
`H` forces `Δc = 1, Δr = 0`, i.e. `x = (r, c−1)`, again a neighbour of `v`.
Hence `ord(v) − ord(x) ≤ H − 1`. So the `(H+1)`-st slot is demanded by the
clash/forced rule — the north-west neighbour sits exactly `H + 1` back — and
not by liveness. RED-4 (window of `H`, with neighbours outside it unseen) and
RED-5 (liveness window `H − 2`) fire on either side of that, which is why both
controls are in the battery.

**Missing file.** The engine header cites `experiments/probe_cutcount_dp.py`
as the brute-force validation of the rule ("5 board sizes, exact"). That file
is not in the tree: it was added in commit `7b13137` and has since been
deleted; `git cat-file -e HEAD:experiments/probe_cutcount_dp.py` fails. The
header's claim is therefore uncheckable as it stands, and
`birthright_identity_check.py` re-establishes an equivalent check under the
definitions of §2 — with the difference that it checks the *theorem's* model
rather than the engine's, and carries RED controls.

## 6. Where the code differs from §7's description

Four points, none of which invalidates §7's conclusion, all of which would
mis-state the identity if copied into a theorem.

1. **The identity is exact in `ℤ[q]`, not merely mod `q²`.** Both §7 and the
   engine header say the count is computed "exactly in the ring `ℤ[q]/(q²)`".
   The truncation is a computational economy — only `[q¹]` is wanted, and a
   two-coefficient payload is cheap — but the sum over configurations equals
   `q^{c(S)}` on the nose. §7's remark that `(q−b₁)(q−b₂) = −q(b₁+b₂) + b₁b₂`
   mod `q²` invites the reading that the cancellation is a mod-`q²`
   phenomenon. It is not: it is the identity `b·1 + (q − b) = q` repeated once
   per component, in `ℤ[q]`. The `q²` truncation happens afterwards.

2. **"A product of `(q − b_i)` factors, one per component birth" describes one
   term, not the subset's value.** §7's phrasing suggests each subset carries a
   single product. It carries a sum over all configurations, most of which have
   *fewer* than `c(S)` birth factors because some component minima adopted an
   existing colour instead. The all-birth configuration is one term of that
   sum. This is the paraphrase most likely to produce a false statement.

3. **`b` counts live labels, not live components.** The brief's "b = number of
   live blocks" is right if "block" means colour class; `successors` counts
   distinct ids present in the window, and since adopt lets a component take
   another component's colour, two live components can contribute 1 to `b`.
   The proof is indifferent to the value of `b`, but a statement that said
   "number of live components" would be false.

4. **The window-reach lemma is Tier 1, not Tier 2.** §7 files "king adjacency
   reaches at most `H+1` cells back in scan order" under Tier 2 as part of the
   sufficient-statistic argument. It is load-bearing in Tier 1: without it
   Lemma 4 fails, the adopt branch a component needs is not on offer, and the
   identity itself is false — RED-5 exhibits a 3-cell witness on a 3×4 board.
   The Tier 1 / Tier 2 line should be drawn after Lemma 4, not before it.

Two smaller observations on the source, neither a defect:

- The frontier-key comment says "a window of `H+2` cells" while the window is
  `H+1` cells (`H+1` slots, slot `k` holding the cell `k+1` back). Comment
  only; `canon` keeps ids at most `H+2`, comfortably inside the 5-bit field.
- `gather` would evaluate `slot(key, H−2)` with `H−2 = −1` at `H = 1`, but the
  guard `r + 1 < H` is false there, so it never does.

## 7. Tier 2, delimited

Not proved here, and deliberately: that the engine's window DP computes the sum
of §3. The argument has three parts, all mechanical.

- **Locality.** Lemma 1 says every earlier king neighbour of `v` lies in
  `Win(v)`, so `gather` sees all of `N⁻(v)` — this half is proved above,
  because Lemma 4 needed it.
- **Sufficient statistic.** The rules of §2 consult the past only through
  *equality* of labels within the window and the *number* of distinct live
  labels. So the colour-coincidence partition of the window determines the
  remaining weight, and `canon` is the canonical form of that partition
  (first-occurrence relabelling, slot 0 upward).
- **Colour reuse.** The engine's birth label `mx + 1` is fresh only within the
  window, whereas §2's births are globally fresh. The two agree because an
  expired label is never consulted again — neither by the clash rule (Lemma 1)
  nor by the adopt/`b` rules, which range over the window.

§7 prices this as routine for this development, and the GapWalk chain is the
precedent. The bridge from a formal model to the compiled binary (§7's Tier 3)
is not addressed at all.

## 8. Limits ledger

**Proved.** The identity of §3, for every `H, W ≥ 1` and every `S ⊆ Γ`, in
`ℤ[q]`, unconditionally — no hypothesis was needed and none is carried. The
one place a condition looked likely (a window-size proviso tying `H+1` to king
reach) is discharged by Lemma 1, which is a theorem about the scan order, not
an assumption. Lemmas 1–5 are elementary and self-contained.

**Checked, not proved.** That the model of §2 is the rule implemented by
`successors`. That reading is mine, from lines 93–173 of the banked source; it
is argued in §1 (slot indices to compass directions) and §2 (three points of
difference from the paraphrases) but it is a reading of C++, not a derivation.
A wrong reading here would make this document prove the wrong theorem, and no
amount of internal rigour would show it. That is the single largest weak point
and I am not able to close it from the paper side; closing it is Tier 2 plus
Tier 3.

**Checked, not proved.** That the engine computes the sum at all (Tier 2), and
that the compiled binary computes what the engine's source says (Tier 3).

**Not addressed.** The accounting layer — `C_H(n) = f_W(n) − f_{W−1}(n)` and
`T(n,H) = C_H − 2C_{H−1} + C_{H−2}` — which fixes translations and extracts
the bounding-box height. It is shared with the strip engine and disjoint from
the connectivity rule; §3's identity is per-board and says nothing about it.

**Conceded weak points.**

- The brute force reaches 16 cells and `H ≤ 5`. It cannot see a phenomenon that
  first appears at larger `H`. The proof is uniform in `H` and `W`, so the
  check is there to catch a mis-statement, not to extend a range; but if the
  statement is wrong in a way that only bites at `H ≥ 6`, this battery will not
  say so.
- The RED controls test the ingredients I identified as load-bearing. A missing
  ingredient I did not think of would have no control.
- The proof is a paper proof, unformalised. §7's own standard —
  "every cell a real kernel-recorded theorem, not a comment" — is not met here
  and is not claimed.
- The `H = 1` boards exercise no free non-minimal cells at all (`loc_checks`
  column is 0), so Lemma 4 is checked only for `H ≥ 3`. That is correct
  behaviour, not a gap: for `H ≤ 2` a free cell's component cannot re-enter
  later. But the reader should not read 53,552 checks as spread evenly.

## 9. Priority: the identity is classical

Added 2026-08-23, when `paper/L9-cutcount-identity.tex` was withdrawn as a
manuscript and folded back into this file. The section is the priority pass's
finding, and it is the reason the withdrawal was the right call: the
mathematics above is a specialisation of a correspondence from 1972, and this
document is the engine's correctness argument rather than a result. The pass
itself, with the searches it ran, is `docs/priority-passes-2026-08-18.md`.

**The statement is an instance of Fortuin–Kasteleyn.** The random-cluster
partition function is `Z = Σ_g v^{b(g)} q^{c(g)}` (Fortuin & Kasteleyn 1972),
and counting connected subgraphs is its `q → 0`, `v = 1` content. The standard
device for evaluating `q^c` without carrying a connectivity state is the Potts
*spin* representation — colour each component, count colourings — and §3's
identity is that device specialised to site clusters and executed in scan
order. The telescoping of §4 is the correspondence performed cell by cell: `b`
ways to reuse a live colour against one birth of weight `q − b`, summing to `q`
per component. It is not a new theorem and none is claimed.

**Two further antecedents.** The unsigned ancestor of §2's scan-order
labelling is Hoshen–Kopelman (1976), which assigns cluster labels in one sweep
with a merge structure. The method this rule is an *alternative* to — carrying
the connectivity partition of a frontier — is Jensen's lattice-animal
algorithm (2001), which is the whole reason an independent second source is
worth building.

**What the searches did not find.** No source states this particular rule: the
window of `H+1` cells, the liveness convention that makes an expired label
uncountable, the adopt branch offering every live label regardless of
adjacency, and Lemma 1 showing that the window suffices under king adjacency.
Lemma 1 is the one step that is not translation — it is a statement about the
scan order, and it discharges the hypothesis a reader would otherwise expect
to see attached to §3.

So the durable content here is implementation-grade, which is what §8's limits
ledger already said in its own words: the mathematics is classical, the rule is
proved because an engine implements it, and a count with no closed form has
nothing to lean on but a second method.
