# Team brief — scaling, not speed: exploration outside the existing body of work

2026-08-11. Written for teammates finishing the second-source campaign
(`docs/second-source-team-brief.md`). That brief asked for a second *count*.
This one asks a different question and is scored differently.

---

## The question

Is there a way to compute T(n,H) — or a(n) — whose **cost grows more slowly**
than the frontier transfer matrix's, even if it is far slower today?

The incumbent's cost tracks frontier size, ~2^H per column, and the project's
whole cost curve follows from that: ~2.5x/term on the kink base,
disk/spill-bound, a(40)'s H21 phase alone 36.4 h on 32 cores with a 363 GB disk
peak. Every engineering lever measured on that curve is dead
(`docs/paper1-engine-chapter.md` §8). A constant factor is worth nothing here.

**A method that is 1000x slower than the incumbent at H = 10 but whose cost
grows at 2.0x per height instead of 2.65x is a win**, and it is the kind of win
this brief exists to find. State every candidate as a growth rate with a
crossover height, never as a wall-clock number.

The scoring metric is:

- the base b in cost ~ b^H (or the exponent in cost ~ n^k, if you find something
  polynomial — say so loudly, that is a different universe);
- the **crossover point**: the H and n at which the candidate overtakes the
  incumbent, computed from two measured points, not asserted;
- and honestly, whether the crossover lands below H = 21 / n = 40, or past the
  end of this project.

A candidate that never crosses over inside the project's range is still worth
recording if its growth rate is genuinely lower — write it up as a negative
with the number attached.

## What "independent of the existing body of research" means here

The second-source campaign swept this repo's own ideas thoroughly, and its
kill lists are real. Do not re-tread them. In particular do not re-propose:
anything on the exhausted list in `docs/second-source-team-brief.md`; the four
measured-dead algorithmic levers; object-materialising enumeration in any form;
or engineering work on the existing kernels.

Two results from that campaign bound where a win can come from, and you should
treat both as closed doors rather than re-derive them:

- **The frontier geometry axis is shut.** pw(P_m ⊠ P_n) = m+1 at every probed
  size, with m <= pw <= m+1 in general, and the kink cell-at-a-time frontier
  achieves it. No frontier ordering beats it; the whole-column scan (width
  2m-1) is worse. A scaling win therefore cannot be a better frontier — it has
  to not be a frontier DP at all, or it has to change what is being carried.
- **The connectivity rule axis** is where the second-source campaign found its
  one live candidate (a colour-symmetrized spin TM with clash-zeroing, counting
  by coefficient rather than by union-find verdict). That is a *rule*
  independence win, and its state growth is slightly worse than the
  incumbent's. Do not confuse the two axes: this brief is about growth, and a
  candidate may score here while failing the independence bar entirely.

So: go outside. Read literature this project has not read, in fields it has not
searched. Speculative is fine. Wrong is fine if it is killed with a number.

## Directions worth a look — a starting list, not a fence

Nobody has probed these here. They are listed to get you moving, not to bound
you; a direction you find yourself and can price is worth more than one off
this list.

- **Tensor networks / MPS-MPO with exact (not truncated) bond dimension.**
  Does the bond dimension of the exact king-animal transfer operator grow
  slower than the naive frontier state count? Truncation is not allowed —
  we need exact integers — but exact bond-dimension reduction is a real
  phenomenon and nobody here has measured it.
- **Algebraic / holonomic structure.** The repo proved the anisotropic GF is
  not D-finite, which closes the obvious version. What it does not close:
  per-height generating functions C_H(x) (each is rational — what is the growth
  of its degree in H, and is there structure in the sequence of rationals?),
  or algebraic structure modulo small primes.
- **Automatic sequences / finite-state structure mod small p.** If a(n) mod 2
  or mod 3 is k-automatic, the cost of a term drops to polylog. The repo has a
  ternary spine result (`results/ternary-spine.md`); this is a different and
  much stronger claim. Cheap to probe, decisive either way.
- **Sparse interpolation and guessing.** Given the banked triangle as data,
  what is the cheapest certificate of the next row? Berlekamp-Massey /
  Pade / Hermite-Pade guessing on rows, columns, and diagonals of T(n,H).
  Note the trap: guessing produces a *prediction*, not a count. It scores here
  only if it comes with a verification whose cost also scales better.
- **Algebraic dynamic programming over a semiring** where connectivity is not
  a carried state at all — the second-source campaign found one such (the q²
  quotient); ask what else the same trick does. Rank-based methods, Möbius /
  zeta transforms over the subset lattice, subset convolution: what is the
  actual exponent, not the textbook one?
- **Lower bounds.** The most valuable negative available: is there an argument
  that no method can beat b^H for some explicit b? A communication-complexity
  or fooling-set lower bound on the exact counting problem would close this
  question permanently and is a publishable result in its own right. Kluk-
  Nederlof 2025 is a starting point (pure-DP lower bounds), cited in the
  second-source B lane.
- **Anything from a field this project has not searched.** Statistical
  mechanics of the Potts model at non-integer q, constraint-satisfaction
  counting complexity, algebraic complexity theory, cellular automata,
  symbolic dynamics, arithmetic geometry over finite fields.

## Rules

- **Two cores per agent, at a time.** Not two per job — two total. Size every
  job to that.
- Follow `docs/job-checklist.md`: predict cost before launching; named scripts
  on disk in `scripts/`, self-describing headers; nothing in `/tmp`; binaries
  into `build/`; obs event stream; anything that could exceed five minutes runs
  in a tmux window on the machine's existing session, never foreground, never
  nohup; no filesystem-wide scans.
- Probes are for measurement, not implementation. You are pricing growth
  curves, so a probe needs **at least two points** — a single data point is not
  a growth rate. Two cheap points beat one expensive one.
- Every quantitative claim comes from a probe or a citation. No estimates.
- Citations need a resolvable identifier. Un-findable references go to
  `papers/MISSING.md` with what was searched.
- Nothing gets committed. Leave work in the working tree.

## Deliverable

`results/scaling-exploration-<your-letter>.md`. Per candidate:

1. The mechanism, in enough detail that someone else could reimplement it.
2. **The measured growth rate**, with the two or more points it came from.
3. **The crossover point** against the incumbent's 2.65x/height (strip) or
   2.5x/term (kink base), computed from those points.
4. What binds it first — state, memory, arithmetic width, or something else.
5. Whether it also clears the second-source independence bar. Separate axis,
   worth noting, not required.

Negatives are deliverables and carry the same weight as positives, provided
they carry the number that killed them. A direction you can show is hopeless is
worth more to this project than a direction left ambiguous.
