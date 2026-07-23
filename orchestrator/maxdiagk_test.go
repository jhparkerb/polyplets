package orchestrator

// maxdiagk_test.go — the strict-route enabler. With P_17 wired, a(37)'s
// H20 would closed-form-short-circuit, so the strict certification sweep
// (real H20 = the first independent P_17 holdout) needs a runtime cap on
// which wired diagonals may dispatch: --max-diag-k. This test proves the
// cap (a) actually forces the capped diagonal height back to a real column
// sweep, and (b) the real sweep reproduces the closed form's cells exactly
// — which is precisely the strict route's validation semantics in miniature.

import (
	"context"
	"testing"
)

func TestMaxDiagKForcesRealSweep(t *testing.T) {
	known := loadKnownTriangle(t)
	dir := t.TempDir()
	cfg := baseCfg(t, dir) // maxn = resumeMaxn (8): k=3 diagonal is H=5
	cfg.MaxDiagK = 2       // cap: k=3 (H=5) must now column-sweep for real
	hit := 0
	cfg.afterColumn = func(H, col int) {
		if H == cfg.Maxn-3 {
			hit++
		}
	}
	res, err := Run(context.Background(), cfg, nil)
	if err != nil {
		t.Fatalf("full sweep maxn=%d max-diag-k=%d: %v", cfg.Maxn, cfg.MaxDiagK, err)
	}
	if hit == 0 {
		t.Fatalf("no column work at H=maxn-3=%d: the k=3 diagonal still closed-form despite MaxDiagK=2", cfg.Maxn-3)
	}
	// The real sweep must reproduce the known triangle (including the cells
	// the P_3 closed form would have generated) byte-for-byte.
	checkTriangle(t, "max-diag-k-capped", known, res.Triangle)
}
