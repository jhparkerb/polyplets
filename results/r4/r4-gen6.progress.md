# r4-gen6 progress

ABOUT TO: step 1 -- read charter, queue, predecessors
DONE: step 1 -> read charter, queue (R4-G4* = gen4's rows), spinproj 3.1, diagonal-law/grand-form proofs
ABOUT TO: step 2 -- price near-diagonal enumeration off results/triangle.txt (desk arithmetic only)
DONE: step 2 -> a(n) table computed; near-diagonal T(H+k,H) matrix for H=15..21, k=0..8
ABOUT TO: FLAGSHIP -- evaluate the Lean-verified cluster-weight recursion (Weights.lean d-recursion) at H=17..21
DONE: FLAGSHIP -> 72/72 exact match incl. 20 cells at H=17..21; an incumbent-free oracle above H=16 EXISTS
ABOUT TO: write the flagship into results/r4/r4-gen6.md before anything else
DONE: flagship written -> results/r4/r4-gen6.md sec 1
ABOUT TO: commit the oracle as a script + log
DONE: experiments/tristruct/r4_gen6_weight_oracle.py + .log -> 142/142 match, 26 ms
ABOUT TO: steps 3-6 -- error matrix, other routes, cheapest cell, broaden; write sec 2-5
DONE: sec 2 (reach/coverage/row-40), sec 3 (error matrix), sec 4 (routes: brute force wall, width kill, row22 histogram), sec 5 (rows)
DONE: 20 rows appended to results/r4/queue.md as R4-G61..R4-G620
FILED. Nothing held in context that is not on disk.
