# Cross-n scaling of uniform-random polyplets (#27)

Uniform samples (~8000 each; n=19 from the existing 10k in `a19_samples.txt`, tall-height-excluded ~2.4% bias). Hole convention = primary 4-connected background (#28). Validation: the n=19 row reproduces `sample_stats.md` (R_g≈3.44, rook≈10.07, holed≈28.3%).

| n | specimens | R_g | rook-pieces | holed frac | holes/cell |
|--:|--:|--:|--:|--:|--:|
| 8 | 8000 | 1.906 | 4.53 | 0.083 | 0.0110 |
| 11 | 8000 | 2.381 | 6.04 | 0.146 | 0.0143 |
| 14 | 8000 | 2.809 | 7.51 | 0.201 | 0.0163 |
| 19 | 10000 | 3.440 | 10.07 | 0.283 | 0.0178 |

## Scaling
- **Radius of gyration**: R_g ~ n^nu with **nu ≈ 0.683** (log-log fit over a short n-range, so finite-size effects inflate it). A compact 2-D blob gives nu→1/2; this sits well above, consistent with the **2-D lattice-animal universality class** (asymptotic nu ≈ 0.6408) — i.e. uniform polyplets are extended, ramified clusters, not blobs, exactly as the ~25% bounding-box density and tree-like degree profile imply.
- **Rook-pieces** grow ~ n^0.92 (near-linear) — the diagonal-glued shattering is an **extensive** property: a roughly constant fraction of cells start a new rook-component as n grows (from 4.5 pieces at n=8 to 10.1 at n=19).
- **Holes are extensive and still rising**: the holed fraction climbs 8.3%→28.3% and holes-per-cell 0.0110→0.0178 across n=8→19 — monotone and concave, i.e. the per-cell hole rate is approaching a positive asymptote rather than vanishing. Enclosed holes are a generic feature of large polyplets, not a small-n artifact.

Single-core, reused the a(19) sample; did not touch the a(20) run.
