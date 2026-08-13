# L4 blind list — symmetry quotient, filed before any code was read

2026-08-12 18:21 EDT. Written from `docs/triangle-round3-brief.md`,
`docs/skeptical-reader-standard.md`, `results/triangle-r3-harness.md`, and the
lane's named prior art (`results/subgroup-mod4.md`, `results/percell-mod4.md`,
`results/symtm_strip_profile_n40.txt`) only. No engine or script source read
yet. Append-only from here.

## Candidates, as I see them before the audit

1. **Routing audit expectation.** From `percell-mod4.md`'s own text, the mod-4
   RHS as wired is: `I_H(D2ax)` from `symcount_fast` (quotient DFS, no
   frontier) and the other three inputs (`I_H(<h>)`, `I_H(<v>)`, `I_H(C2)`)
   from `symtm --byheight`, which the harness says includes
   `core/transition.h` and calls `stepColumnSquare8` directly. Expectation:
   three of four inputs are in the production rule class; only the mod-2 bit's
   input is outside it. To verify from code, not inherit.

2. **The actual target: quotient-domain (Redelmeier-style) `--byheight` for
   the three order-2 subgroups.** The construction I expect to exist for each:
   - Orbits of cells under the order-2 group (pairs off-axis, singletons on a
     mirror axis; for C2 with n even, all pairs). DFS over connected subsets
     of the orbit graph, lift each candidate, check connectivity of the lifted
     set by BFS, exactly symcount_fast's scheme.
   - **Height classification is free in this scheme**: the DFS holds the full
     lifted cell set, so the true bounding-box height is trackable exactly and
     can prune at H > 21. This is the crux: decline reason 1 ("`I_H(<v>)` has
     no bounded-height route") was measured against symtm strips, where the
     transpose sends height to width. A quotient DFS never transposes — it
     classifies by the lift's real extent. Prior expectation: **reason 1 does
     not bind against a quotient-domain method.**

3. **The cost wall I expect instead.** Order-2 subgroups halve the domain,
   not quarter it: ~n/2 = 20 orbits at n=40, domain ~λ^(n/2), versus D2ax's
   λ^(n/4). The DFS must visit at least I(⟨h⟩)(40) ≈ Fix(h)(40) candidates,
   and Fix(h) grows ~λ^(n/2) — the same growth class as the Fix(d) wall that
   stopped the related-sequences work at n≈33. Extrapolating from banked
   Fix(h)(32) ≈ 2.5e12 by λ^4 per 8 cells gives ~10^15–10^16 candidates per
   input at n=40. Prior expectation: **the route exists, clears level 2, and
   is priced out by λ^(n/2) — fleet-months for one additional bit per cell.**
   To be anchored on my own small-n measurement, not this extrapolation alone.

4. **Height-band restriction will not save it.** H=15..21 sits near the bulk
   of the height distribution; restricting the DFS to lifts with H in 15..21
   prunes a constant factor, not an exponential one. To be measured.

5. **The ceiling (mod 8).** T(n,H) mod 2^k via stabilizers needs a 2-group of
   order 2^k acting height-preservingly on fixed height-H animals. The acting
   group on fixed (translation-class) animals is the point group D4;
   its height-preserving subgroup is exactly D2ax = {e,h,v,r180}, order 4 —
   r90/r270 and both diagonal mirrors swap H and W. Glide reflections do not
   extend it: A = m(A) + t with t parallel to the axis forces t = 0 for a
   finite animal (apply twice). Prior expectation: **no group exists; mod 4 is
   this route's ceiling for T(n,H).** The only escape hatch I can name is
   changing the object: on the joint box table B(n,W,H), full D4 acts with
   orbit sizes dividing 8, giving mod-8 information about the symmetrized
   quantity B(n,W,H)+B(n,H,W) — but that is not T(n,H), and summing over W
   collapses it back to the mod-4 identity. A non-isometric involution on
   height-H animals with controlled fixed points would be the other escape;
   I know of none.

6. **Decline reason 3 (trust is history).** Any quotient route for the three
   inputs is new code — symcount_fast's census covered only the order-≥4
   subgroups (c4, d2ax, d2diag, d4). The override argument available: the new
   part is orbit construction + height tracking; the DFS core and lifted-BFS
   connectivity check are the parts with the gate history (brute oracle,
   sym-farm r90 reproduction). That is an argument to state, not a settlement
   — and it is moot if candidate 3's cost holds.

7. **Small-n verification data already banked**: `results/percell_raw/
   hmirror.byheight.n32.out` and `r180.byheight.n32.out` give exact
   I_H(⟨h⟩), I_H(⟨v⟩), I_H(C2) to n=32 for checking any toy I write.

## Appended after the audit — 2026-08-12 18:29 EDT

Candidate 6 overstated the new-code need: `symcount_fast` already ships
`hmirror` and `r180` types with `--byheight` (true lifted-bbox height), so
two of the three quotient inputs need no code at all; only ⟨v⟩ does (~6-line
type). Candidates 1–5 confirmed by the audit and measurements; see
`results/triangle-r3-l4-quotient.md`.
