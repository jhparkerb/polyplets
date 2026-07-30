package orchestrator

// kink_sweep_test.go — Design 14 Phase 2.6 cheap pre-check: sweepHeightKink
// must reproduce sweepHeight's per-height triangle row byte-for-byte, driven
// through the REAL compiled map_worker/merge_worker binaries (not synthesized
// in-process), before trusting the kink kernel to a full a(20) --kernel kink
// --compare gate (2.8, hours-scale). Each (H,maxn) pair is chosen away from
// Run's closed-form short-circuits (H==maxn, H==maxn-1, low strips, diagonal
// strips) so both functions actually walk a real column sweep, not a
// dispatch this test can't reach.
import (
	"context"
	"fmt"
	"math/big"
	"os"
	"path/filepath"
	"sync/atomic"
	"testing"
	"time"
)

func TestKinkSweepMatchesColumnSweep(t *testing.T) {
	cases := []struct{ H, maxn int }{
		{H: 6, maxn: 14},
		{H: 10, maxn: 20},
	}
	for _, c := range cases {
		t.Run(fmt.Sprintf("H%d_maxn%d", c.H, c.maxn), func(t *testing.T) {
			columnRow := runOneHeight(t, c.H, c.maxn, sweepHeight)
			kinkRow := runOneHeight(t, c.H, c.maxn, sweepHeightKink)
			for n := 1; n <= c.maxn; n++ {
				cv, kv := columnRow[n], kinkRow[n]
				if cv == nil {
					cv = new(big.Int)
				}
				if kv == nil {
					kv = new(big.Int)
				}
				if cv.Cmp(kv) != 0 {
					t.Errorf("H=%d maxn=%d n=%d: column=%s kink=%s", c.H, c.maxn, n, cv, kv)
				}
			}
		})
	}
}

// runOneHeight drives sweepFn over a single real height H (real seed, real
// compiled workers) and returns its triangle row (index n -> T(n,H)).
func runOneHeight(t *testing.T, H, maxn int, sweepFn sweepHeightFn) []*big.Int {
	t.Helper()
	dir := t.TempDir()
	spill := filepath.Join(dir, "spill")
	if err := os.MkdirAll(spill, 0o777); err != nil {
		t.Fatalf("mkdir spill: %v", err)
	}
	cfg := SweepConfig{
		Maxn:     maxn,
		Fold:     true,
		Cores:    4,
		RAM:      4 << 20,
		RunDir:   dir,
		SpillDir: spill,
		Rev:      "test",
		Bin:      DefaultWorkerBin(".."),
	}

	seed := filepath.Join(dir, "seed.bin")
	if err := WriteSeedPolyrun(seed, cfg.Rev, H, maxn, cfg.CounterWidth); err != nil {
		t.Fatalf("WriteSeedPolyrun: %v", err)
	}

	tel, err := newTelemetry(cfg, time.Now())
	if err != nil {
		t.Fatalf("newTelemetry: %v", err)
	}
	sem := make(chan struct{}, cfg.Cores)
	activeHeights := new(atomic.Int32)
	activeHeights.Store(1)
	noopCkpt := func(int, int, []string, []*big.Int) bool { return true }

	hTri, _, err := sweepFn(context.Background(), cfg, H, 0, []string{seed}, noopCkpt, tel, sem, activeHeights)
	if err != nil {
		t.Fatalf("sweepFn(H=%d,maxn=%d): %v", H, maxn, err)
	}
	return hTri
}
