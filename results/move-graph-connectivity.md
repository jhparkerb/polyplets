# The single-cell-move graph on king animals is connected for n <= 10

2026-08-07, gympie. Executes idea 8 of `results/unexplored-avenues.md`, which
ranked it the cheapest item in that file and called it "the item that converts
a dead end (idea 5's blocker) into a programme".

**Answer: yes at every n <= 10, with no component splitting anywhere.**

**Novelty: NOT claimed, and probably already published.** See §"Prior art"
before describing any of this as new.

## The move, and the question

From an n-animal `A`, pick a cell `c` that is not a cut vertex — so `A \ {c}`
is still king-connected and non-empty — then place `c` at any empty position
king-adjacent to `A \ {c}`. The result is an n-animal, connected by
construction. This is the standard cell-move chain for lattice animals. If its
graph is connected then the chain is irreducible, which is the *first* of
several gates on a uniform sampler.

Vertices are **fixed** animals (translation classes), which is what `a(n)`
counts and what a sampler would target. Connectivity of the fixed graph implies
connectivity of the free graph, the latter being a quotient.

## The reformulation that made it cheap

The naive cost is (animals) x (n cells to lift) x (~8n re-attachment sites) —
about 40x more work than needed. Instead:

> `A` and `B` are adjacent **iff they share a common connected
> (n-1)-subanimal.**

So bucket every n-animal by its set of legal deletions, and union-find the
animals that share a bucket. Each deletion is computed once, and the whole move
expansion never happens. `experiments/move_graph_connectivity.py`.

## Results

| n | animals | components | largest | verdict | wall |
|---|---|---|---|---|---|
| 1 | 1 | 1 | 1 | connected | 0.0 s |
| 2 | 4 | 1 | 4 | connected | 0.0 s |
| 3 | 20 | 1 | 20 | connected | 0.0 s |
| 4 | 110 | 1 | 110 | connected | 0.0 s |
| 5 | 638 | 1 | 638 | connected | 0.0 s |
| 6 | 3832 | 1 | 3832 | connected | 0.1 s |
| 7 | 23592 | 1 | 23592 | connected | 0.5 s |
| 8 | 147941 | 1 | 147941 | connected | 4.4 s |
| 9 | 940982 | 1 | 940982 | connected | 35.6 s |
| 10 | 6053180 | 1 | 6053180 | connected | 289.7 s |

Single-threaded Python, `results/move_graph_20260807.log`.

**Free regression:** the vertex counts are A006770 line for line through
n = 10. The probe grows its own animals rather than reading the b-file, so this
is an independent reproduction of the first ten terms as a by-product.

**No animal is ever stuck.** The census finds exactly one animal with no legal
move — the single cell at n = 1, which has no non-empty deletion. That is not
luck and does not need checking at larger n: every connected graph on >= 2
vertices has at least two non-cut vertices, so every animal with n >= 2 has at
least two liftable cells. The chain cannot deadlock at any n.

## Cost, if it is ever worth going further

Wall grows 8.1x per term, twice running (4.4 -> 35.6 -> 289.7 s), tracking the
6.9x growth of `a(n)` plus the per-animal work. Extrapolating one term is
therefore honest and two is not:

- n = 11 (`a(11)` = 39299408): ~40 min, and memory becomes the binding
  constraint before time does — the run holds every n-animal plus every
  (n-1)-animal live.
- n = 12 (`a(12)` = 257105146): ~5.3 h in this implementation, and it will not
  fit. It needs the C++ treatment, not a longer Python run.

Nothing here justifies either. n <= 10 was the question asked.

## What this does NOT establish

Stated plainly, because the payoff bullet in idea 8 reads much stronger than
what was measured.

1. **It is a census, not a proof.** Connectivity at n <= 10 says nothing about
   n = 100, and the sampler payoff needs irreducibility at the n being sampled.
   The proof route is standard — show every animal reaches a canonical bar by
   moves — and the "no animal is stuck" fact above is its first step, but the
   induction is not written and is not written here.
2. **Irreducibility is necessary, nowhere near sufficient.** A uniform sampler
   needs the chain to *mix*, and this probe measures nothing about mixing time.
   Idea 8's payoff bullet — "if yes: mixing time, hence a uniform sampler, hence
   measurement of nu and of everything in idea 5 at n = 100+" — treats these as
   one step. They are not; the second is the hard one and is completely
   untouched. **Do not quote that bullet as though this file supported it.**
3. **It shortens no sentence in the paper.** It was worth an evening as a gate,
   and it cost twenty minutes.

## Prior art — check before calling any of this new

`papers/MISSING.md` wants **Janse van Rensburg & Madras, "Metropolis Monte
Carlo simulation of lattice animals," J. Phys. A 30 (1997) 8035-8066** for an
unrelated reason (its §2.4/§2.8 are where "simply-connected animals are
exponentially rare" would already be stated). That paper is now wanted for a
second reason: **a Metropolis chain on lattice animals cannot be published
without establishing its own irreducibility, and the move it uses is this
move.** The square-lattice case of this file is very likely a lemma in its §2,
together with whatever is known about the mixing.

The MISSING.md entry has been updated with this second reason. Until it is in
hand, the honest statement is: *confirmed for king animals at n <= 10*, not
*shown*.

## Artifacts

- `experiments/move_graph_connectivity.py` — the probe
- `results/move_graph_20260807.log` — the run
