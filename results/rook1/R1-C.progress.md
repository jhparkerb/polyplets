# R1-C progress

ABOUT TO: read results/triangle-r3-involution.md §2 and locate the script that produced its ranks
DONE: read triangle-r3-involution.md §2 + experiments/tristruct/r3_inv_rank_probe.py -> object pinned: strip automaton observability closure; rook analogue = same builder with cross-column offsets (0,) only. Throwaway probe, not the out-of-scope rook TM engine.
ABOUT TO: check build/g2 --rook-bishop interface and grep experiments/ for any existing rook rank work
DONE: g2 usage pinned (square8 MAXN --rook-bishop); found prior art experiments/tristruct/r3_adv3_rook_schema.py -- rook stencil swap already externally validated vs A292357/A001168
ABOUT TO: run build/g2 square8 8 --rook-bishop (seconds) to capture ground-truth format
DONE: g2 square8 8 --rook-bishop -> rook col = A001168 exactly (log captured in probe log later)
ABOUT TO: write experiments/rook1/rook1_R1-C_rank_probe.py (rook+king strip automata, GF(2)/GF(2^16)/mod-p observability ranks, A001168 tie, two RED controls) and run at MAXH=8 foreground
DONE: probe written + smoke-run MAXH=6. All gates green incl. both REDs. Smoke result: rook GF(2) rank ~= states (20/20, 49/50, 119/126), mod-p FULL -- no crack. Finding logged: bottom-anchored delta defect CANCELS in the exact-height telescope; A001168 tie alone is a weak gate, word-count regression is the red one.
ABOUT TO: full run MAXH=8 foreground (est ~1-2 min from smoke timings), log = experiments/rook1/rook1_R1-C_rank_probe.log
