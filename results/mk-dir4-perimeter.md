# (dir4, HV-convex) by semiperimeter — the mode and its validator

`docs/middle-kingdom-followups-plan.md` Phase 2a (**not** `docs/middle-kingdom-plan.md`'s
own Phase 2a, the D-finiteness-by-area work in `results/convex-polyplets.md` —
same name, different plan, disambiguated here on purpose). `results/middle-kingdom.md`
flagged this as the sixth novel sequence the grid produces ("HV-convex by
semiperimeter is a sixth, counted by a different statistic") without
generating it; this note does.

## What's new

`cpp/convex_perim_tm.cpp` already counted HV-convex king animals by
semiperimeter (`results/convex-polyplets.md`'s Phase 1b, `results/convex_perim_terms_s200.txt`).
It now has a `dir4` mode filtering that population to the half-plane-4-cone-directed
subset, and a `dir4bad` RED control. Usage unchanged for old callers:
`build/convex_perim_tm SMAX [king] [mode]`, `mode` in `{hv, dir4, dir4bad}`,
default `hv` (the original, unfiltered behavior). `dir4`/`dir4bad` require
`king=1` (dir4 is a king-cone notion; there is no A005436-style edge-adjacency
variant of it).

## The translation — verified, not assumed

The plan's own working hypothesis was: "on the left-descending phase the left
boundary strictly decreases every row." That is exactly right, but it needed
checking on paper against Proposition 2 first, which is what follows.

Proposition 2 (`results/middle-kingdom-phase3.md`, proved on the COLUMN-built
transfer matrix `cpp/middle_kingdom_tm.cpp`) says a column-convex king animal
is half-plane-4-cone directed iff the column-bottom profile satisfies
`b(j+1) >= b(j) - 1` for every `j`. `cpp/convex_perim_tm.cpp` is ROW-built
instead (bottom row first, state = the row's column interval `[l, r]` plus
two unimodality phase flags), so the translation has to be re-derived against
*this* DP's state, not read off the column DP.

For a column `j` to the left of the bottom row (`j < l(1)`), the right
boundary never restricts it (`r(1) >= l(1) > j` already), so `b(j)` is simply
the first row `i` (searching bottom to top) with `l(i) <= j` — a
right-continuous inverse of `l()` restricted to `l`'s *descending* phase
(the DP's `pl = 0` phase, before the left boundary starts moving right again).
Two things follow directly from that:

- A single row where `l` **drops by `k >= 1` in one step** covers `k` new
  columns at once: `b` is constant across them (diff 0), which Proposition 2
  allows.
- A row where `l` does **not** drop (`lp == l`, "fails to extend left")
  wastes a row index without covering a new column. If `l` drops again on
  any *later* row while still in the descending phase, the two columns
  either side of that wasted row have `b` differing by `>= 2` — exactly the
  drop Proposition 2 forbids.

By the symmetric argument on the right boundary's *ascending* phase (columns
to the right of the bottom row, `j > r(1)`), the same wasted-row pattern only
makes `b` **rise** across the gap — which Proposition 2 does not restrict —
so the right boundary needs no extra condition, and neither does the left
boundary's own ascending phase or the right boundary's descending phase (both
only affect the range where `b` is already pinned to 1 by the other side, or
rises, which is unrestricted).

So: dir4 = "in the left-descending phase, `lp < l` strictly on every row; the
first row that fails to strictly decrease locks the phase (`lp >= l` from
then on), exactly the way the unrestricted DP already locks on `lp > l`."
One line of code (`cpp/convex_perim_tm.cpp`'s `npl` transition): replace
`lp > l` with `lp >= l`.

Worked by hand against small `l`-sequences before touching code:
`l = [5,4,4,2]` (drop 1, flat, drop 2) gives `b(3)=4, b(4)=2`
(`a(3)=4, a(4)=2` at the failing sub-boundary) — `b(4)-b(3) = -2`, a real
violation, correctly rejected by the strict rule (locks at the flat row,
then the later drop to 2 is disallowed). `l = [5,3,3,3]` (drop 2, then flat
forever) has no later drop after the flat row, so nothing is skipped —
correctly accepted. `l = [5,3,1]` (two single-step drops of 2 each, no flat
rows) is also correctly accepted: a same-row multi-column jump is fine,
only a *wasted* row followed by a *later* drop is not.

## RED control: dir4bad

The plan asked by name for "a deliberately wrong variant (e.g. non-strict
decrease)." `dir4bad` is exactly that: the un-strengthened `lp > l` rule,
i.e. *verbatim* the unrestricted-HV transition mislabeled as dir4 — the most
natural mistake a translator makes (forgetting that a flat row needs
excluding too, only an actual increase). Confirmed to be exactly that, not a
different wrong rule: `dir4bad`'s output is byte-identical to the `hv` mode's
at every `s` (same code path). It diverges from the true dir4 counts starting
at `s=5` (34 vs 36) — the RED control fails as required.

## Brute-force validation

`build/directed_cone_anchor` gained a `gridperim` mode: the same Redelmeier
enumeration as the already-gated `grid` mode, reusing `reach(Dir4)` and
`convexity()` **verbatim** (no new predicate code, only a new bucketing key),
tallying by box `s = W+H` instead of by area. Coverage caveat, as the plan
required: an area-`<=N` enumeration settles `s` completely only up to
`floor(s/2)*ceil(s/2) <= N` (max area at that box), so `N=14` settles `s<=7`
completely (`floor(7/2)*ceil(7/2) = 12 <= 14`); beyond that the brute-force
count is a **lower bound only**, not an exact value. Run: `build/directed_cone_anchor
gridperim 14 8` — wall 74.4 s, peak RSS 1.9 MB (`results/mk_dir4_perim_brute_n14.log`),
data in `results/mk_dir4_perim_brute_n14.txt`.

| s | brute hv | brute dir4 | TM hv | TM dir4 | complete? |
|---|---|---|---|---|---|
| 2 | 1 | 1 | 1 | 1 | yes |
| 3 | 2 | 2 | 2 | 2 | yes |
| 4 | 9 | 9 | 9 | 9 | yes |
| 5 | 36 | 34 | 36 | 34 | yes |
| 6 | 154 | 137 | 154 | 137 | yes |
| 7 | 668 | 553 | 668 | 553 | yes |
| 8 | 2909 | 2230 | 2916 | 2237 | no (lower bound) |
| 9 | 11946 | 8358 | 12740 | 9038 | no (lower bound) |

Exact match on every `s` the enumeration settles completely (`s<=7`); beyond
that the TM is `>=` the brute-force lower bound at every `s` checked (never
undercuts it, which would indicate the TM itself was missing animals).
`tests/gate_mk_dir4_perim.py` (`make gate-mk-dir4-perim`) pins this, the RED
control, and the termwise sanity check below.

## Termwise sanity against the unrestricted mode

`dir4(s) <= hv(s)` at **every** `s` in `2..200` (checked against every one of
the 199 banked terms of both series, zero violations), with equality
**only** at `s = 2, 3, 4` — the brute force confirms every animal of box
`2, 3, 4` is already dir4-directed (the shapes are too small to fail
Proposition 2), and the two series separate at `s=5` and never rejoin.
`ratio dir4(200)/hv(200) = 0.01019` — the dir4 restriction is already cutting
the population by two orders of magnitude by `s=200`.
`tests/gate_mk_dir4_perim.py` pins the same check for `s<=15` against a live
run of the binary (not the banked file) on every `make`.

## A005436 control

`king=0` forces `mode=hv` (dir4 is undefined off the king lattice); unaffected
by any of this — `build/convex_perim_tm 11 0 hv` still reproduces A005436's
first 10 terms (`1, 2, 7, 28, 120, 528, 2344, 10416, 46160, 203680`) exactly.

## Novelty

No hit anywhere in `results/`, `docs/`, `papers/` for the leading terms
(`grep`), and `experiments/oeis_lookup.py` on `1,2,9,34,137,553,2237,9038,36435,146511`
returns `NO MATCH`. The area-indexed sibling of this class (Table B of
`docs/middle-kingdom-followups-plan.md`, `results/b_hvdir4_upload.txt`) was
separately confirmed novel on 2026-08-05; this is the semiperimeter-indexed
sixth cell `results/middle-kingdom.md` flagged and left ungenerated.

## The series

199 terms (s=2..200) in `results/mk_dir4_perim_terms_s200.txt` (`s value` per
line, reformatted from the binary's own comma-separated stdout to match the
sibling `results/convex_perim_terms_s200.txt` and the format `prec_guess`
reads), generated by `build/convex_perim_tm 200 1 dir4` on gympie.

| run | wall_s | peak_rss_mb |
|---|---|---|
| baseline: `hv` (unrestricted) king, s=200 (`results/convex-polyplets.md`) | 1246.4 | 345.5 |
| this phase: `dir4`, s=200 | 1072.7 | 325.2 |

**~14% faster, ~6% less RSS than the baseline, not slower.** Expected from
the code, not a surprise: the `dir4` transition changes one comparison
(`lp >= l` vs `lp > l`) in the same loop structure, with the same iteration
bounds (`lpLo`/`lpHi`/`rpLo`/`rpHi` are unchanged) — no change in DP shape or
asymptotic cost. The dir4 population is strictly smaller at every `s > 4`
(down to ~1% of `hv` by `s=200`, see below), so the `mpz_class` accumulators
carry smaller integers throughout the run, which is cheaper GMP arithmetic
end to end. `cpu_s=1072.6` in the log is within noise of `wall_s`
(single-threaded, as expected — this DP is not parallelized).

Reproduce:

```
make build/convex_perim_tm build/directed_cone_anchor
build/directed_cone_anchor gridperim 14 8 > results/mk_dir4_perim_brute_n14.txt
build/convex_perim_tm 200 1 dir4 > results/mk_dir4_perim_terms_s200.txt
make gate-mk-dir4-perim
```

## Scope note

This phase stops at the series and its validation, per
`docs/middle-kingdom-followups-plan.md`: Phase 2b (running the P-recurrence/
algebraic guessers on this series to test whether the "area wild, perimeter
tame" D-finiteness lever survives the dir4 restriction) is a separate,
Opus-tier phase and is not attempted here.

Phase 2b has since run: the lever survives, and this series' generating
function is **algebraic of degree 4** (t-degree 22, exact over Q, holdout
81 of 199 rows) — verdict, controls and the quartic itself are in
`results/convex-polyplets.md`, "The perimeter lever survives directedness".
