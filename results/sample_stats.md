# Statistics of a uniform sample of 19-cell polyplets

10,000 specimens drawn uniformly at random (heights ≤13 = 97.6% of a(19); the
tall 2.4% are excluded, a slight bias for height-dependent stats). Common
features are well-measured (~1% error); rare classes (polyomino-ness ≈0.004%,
symmetry ≈10⁻⁶) are invisible at this sample size — use exact counts for those.

## The portrait
A typical uniform 19-cell polyplet is a **sparse, branchy, corner-glued
structure** — not the tidy blob one pictures for a polyomino:
- it shatters into **~10 edge-connected pieces** held together mostly by
  **diagonal (corner) contacts** (59% of all contacts are corners);
- it's **never** an honest polyomino in the sample (rook-connected ≈0.004%, ~0
  expected) and never biconnected (0% with no cut cell);
- it fills only **~25%** of a roughly-square bounding box, is low-degree
  (avg ~2.3) and highly articulated (most cells are cut points);
- it has about a **1-in-3.5 chance of enclosing a hole**.

## Numbers
GEOMETRY
- bounding box: mean 9.2 (w) × 9.0 (h); density 19/(w·h) mean 0.246 (0.10–0.48)
- aspect (max/min): mean 1.42, max 4.0 — mildly elongated, rarely extreme
- radius of gyration: mean 3.44 (2.23–5.70)

TOPOLOGY
- fraction with ≥1 hole: **28.3%**; #holes 0:71.7% 1:23.3% 2:4.4% 3:0.5% 4:0.1%
- hole area (empty cells enclosed): mean 0.41, max 16

DIAGONAL-NESS / CONNECTIVITY
- rook-components: mean **10.07**, peak at 9–11; range 2–17 (1 = polyomino: none seen)
- contacts: edge mean 9.1, corner mean 13.1 → **corners = 59%** of the glue

KING-GRAPH STRUCTURE
- cell degree: 1:18% 2:43% 3:29% 4:9% 5:1% (mean ≈2.3 — sparse, tree-like)
- cut cells per animal: mean **11.3 of 19**; biconnected (0 cut cells): **0%**

CHECKERBOARD COLOUR
- |#even − #odd|: 1:30% 3:27% 5:19% 7:13% 9:7% … (fairly balanced; both colours
  present ⇒ genuine polyplets, not disguised polyominoes)

## Cross-checks passed
- no rook-connected specimen appears (consistent with A001168(19)/a(19) ≈ 0.004%)
- no single-colour/symmetric specimen of note (consistent with their rarity)
- (the height histogram already matched byHeight/a(19) in the sampler χ² test)
