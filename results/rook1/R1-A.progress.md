# R1-A progress

ABOUT TO: read R1-K.md §1d and the three source claims (kink-carry.md:46,69; ns_a40/PROVENANCE.md:16-25)
DONE: read R1-K.md §1d — three claims pinned: 2.42-2.5 (kink-carry:46 per-n cost), 1.612 (kink-carry:69 per-height states 2.6^H, H~n/2), 1.727 (PROVENANCE C/B cpu 2.981/height)
ABOUT TO: read kink-carry.md and ns_a40/PROVENANCE.md in full at the cited lines
DONE: read kink-carry.md + PROVENANCE.md — quotes verified at cited lines
ABOUT TO: inventory in-tree per-term cost records for n=24..30 (ls results/ns_a*, grep for cpu/wall totals)
DONE: inventory — cost_profile TSVs exist a26..a30; a24/25 records are wall-based; engines MIXED (col ≤a29, kink from a30); machines mixed (ayr a25,a28; dalby others; a27 split)
ABOUT TO: pull cpu totals (sum TSVs, read a24/a25 RESULT, a31-a34 provenance for the kink-series check)
DONE: pulled a24..a39 records — kink ladder starts a30; a30-34 dalby-solo same config; a35/36 split; a37-40 dalby (top-H 19,20,20,21)
ABOUT TO: sum a31-34 tsv cpu, grep a39 cpu + a24 H16 stats + a25 cpu, per-height cpu sums a30-34
DONE: full cpu series in hand — kink dalby ladder a30..a40 (a35/36 split, excluded), column window points a26/a28/a29, per-height sums
ABOUT TO: write+run experiments/rook1/rook1_R1-A_basefit.py (ln-cpu vs n least squares, residuals, per-height ratios)
