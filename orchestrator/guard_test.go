package orchestrator

// guard_test.go — refuse-at-start guards (BUGS-OF-SHAME cat 2): an invalid
// config must fail loudly at the start of Run, not silently miscount.

import (
	"context"
	"testing"
)

// TestRejectZeroCores proves Run refuses Cores<1 instead of silently
// undercounting. With Cores==0 the worker pool spawns zero goroutines, so every
// map phase produces no output and Run returns a too-low triangle with a nil
// error — a silent wrong answer. The guard must turn this into a start-time
// error.
func TestRejectZeroCores(t *testing.T) {
	dir := t.TempDir()
	cfg := baseCfg(t, dir)
	cfg.Cores = 0
	cfg.Heights = []int{2} // a single ordinary (non-closed-form) height
	_, err := Run(context.Background(), cfg, nil)
	if err == nil {
		t.Fatalf("Run(Cores=0) returned nil error (silent undercount); want a refuse-at-start error")
	}
}
