package orchestrator

// kink_sweep_fused_test.go — Even Keel D6, F2 gate: sweepHeightKink with the
// fused stage worker engaged (cfg.OverlapHeights==1, cfg.Bin.FusedWorker set)
// must reproduce the SAME per-height triangle row as the unmodified
// map+merge path over a real multi-column sweep, driven through the REAL
// compiled binaries (map_worker/merge_worker/fused_stage), mirroring
// kink_sweep_test.go's pattern for the column-vs-kink kernel check. This is
// the orchestrator-level counterpart to test/gate_fused_stage.cpp's
// single-round C++ gate: DDF9 requires end-to-end a(n) byte-identical, not
// just one stage round in isolation.

import (
	"fmt"
	"math/big"
	"testing"
)

func TestKinkSweepFusedMatchesUnfused(t *testing.T) {
	cases := []struct{ H, maxn int }{
		{H: 6, maxn: 14},
		{H: 10, maxn: 20},
	}
	for _, c := range cases {
		t.Run(fmt.Sprintf("H%d_maxn%d", c.H, c.maxn), func(t *testing.T) {
			unfusedRow := runOneHeightOverlap(t, c.H, c.maxn, false)
			fusedRow := runOneHeightOverlap(t, c.H, c.maxn, true)
			for n := 1; n <= c.maxn; n++ {
				uv, fv := unfusedRow[n], fusedRow[n]
				if uv == nil {
					uv = new(big.Int)
				}
				if fv == nil {
					fv = new(big.Int)
				}
				if uv.Cmp(fv) != 0 {
					t.Errorf("H=%d maxn=%d n=%d: unfused=%s fused=%s", c.H, c.maxn, n, uv, fv)
				}
			}
		})
	}
}

// runOneHeightOverlap is runOneHeight (kink_sweep_test.go) with
// OverlapHeights forced to 1 (DDF7's fusion-eligible path) and, when
// useFused is true, the real fused_stage binary wired up via
// DefaultWorkerBin's FusedWorker field; when false, FusedWorker is cleared
// so sweepHeightKink falls back to the unmodified map+merge path even
// though OverlapHeights==1 -- the DDF7 fallback this test relies on to get
// a same-OverlapHeights, fusion-only delta between the two runs.
func runOneHeightOverlap(t *testing.T, H, maxn int, useFused bool) []*big.Int {
	t.Helper()
	bin := DefaultWorkerBin("..")
	if !useFused {
		bin.FusedWorker = ""
	}
	cfg := baseSweepCfg(t, maxn)
	cfg.OverlapHeights = 1
	cfg.Bin = bin
	// baseSweepCfg's RAM (4 MB/core) is calibrated to force the OLD
	// map_worker's spill path early -- deliberately tiny, exercised by other
	// tests. The fused worker has no spill (DDF5: fails loud past its
	// ceiling instead), so this test needs a budget that comfortably covers
	// H10/maxn20's real stage-table sizes, not one tuned to trip a
	// mechanism this worker doesn't have.
	cfg.RAM = 64 << 20
	return runOneHeightCfg(t, cfg, H, maxn, sweepHeightKink)
}
