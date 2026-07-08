package orchestrator

// kink_sweep_sharded_test.go — orchestrator-level validation for the
// sharded-private column sweep (sweep_sharded.go, core/kink_sharded.h),
// driven through the REAL compiled map_worker binary (not synthesized
// in-process), mirroring kink_sweep_test.go's own pattern for the
// standard sweepHeightKink path. This is the Go-orchestrator-level
// counterpart to test/gate_kink_sharded_worker_cli.cpp's direct-CLI check
// -- same correctness bar (a whole real height's triangle row must match
// exactly), reached through the actual sweepColumnSharded dispatch code
// instead of a test driving map_worker calls by hand.

import (
	"context"
	"fmt"
	"math/big"
	"os"
	"path/filepath"
	"testing"
	"time"
)

// sweepHeightKinkSharded drives a whole height's column-by-column sweep
// using sweepColumnSharded (K shards, one merge point) instead of
// sweepHeightKink's per-round mapPhase/mergePhase barriers. Test-only
// glue: this is deliberately NOT promoted to production dispatch (no
// checkpoint/resume, no telemetry, no overlap-heights) -- it exists only
// to drive sweepColumnSharded across a real multi-column height for
// validation, matching kink_sweep_test.go's runOneHeight harness shape.
func sweepHeightKinkSharded(ctx context.Context, cfg SweepConfig, H, maxn, K int, seed []string, sem chan struct{}) ([]*big.Int, error) {
	hTri := newBigRow(maxn + 1)
	frontier := seed
	for col := 0; col <= maxn && len(frontier) > 0; col++ {
		next, triContribs, _, err := sweepColumnSharded(ctx, cfg, H, col, K, frontier, sem)
		if err != nil {
			return nil, fmt.Errorf("col=%d: %w", col, err)
		}
		addTriContribs(hTri, triContribs, maxn)
		frontier = next
	}
	return hTri, nil
}

func TestKinkSweepShardedMatchesColumnSweep(t *testing.T) {
	cases := []struct {
		H, maxn, K int
	}{
		{H: 6, maxn: 14, K: 4},
		{H: 6, maxn: 14, K: 8},
		{H: 10, maxn: 20, K: 8},
	}
	for _, c := range cases {
		t.Run(fmt.Sprintf("H%d_maxn%d_K%d", c.H, c.maxn, c.K), func(t *testing.T) {
			columnRow := runOneHeight(t, c.H, c.maxn, sweepHeight)
			shardedRow := runOneHeightSharded(t, c.H, c.maxn, c.K)
			for n := 1; n <= c.maxn; n++ {
				cv, sv := columnRow[n], shardedRow[n]
				if cv == nil {
					cv = new(big.Int)
				}
				if sv == nil {
					sv = new(big.Int)
				}
				if cv.Cmp(sv) != 0 {
					t.Errorf("H=%d maxn=%d K=%d n=%d: column=%s sharded=%s",
						c.H, c.maxn, c.K, n, cv, sv)
				}
			}
		})
	}
}

// runOneHeightSharded is runOneHeight's counterpart for the sharded
// design: same real-seed, real-compiled-worker setup, driven via
// sweepHeightKinkSharded instead of a sweepHeightFn.
func runOneHeightSharded(t *testing.T, H, maxn, K int) []*big.Int {
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

	sem := make(chan struct{}, cfg.Cores)
	ctx, cancel := context.WithTimeout(context.Background(), 60*time.Second)
	defer cancel()

	hTri, err := sweepHeightKinkSharded(ctx, cfg, H, maxn, K, []string{seed}, sem)
	if err != nil {
		t.Fatalf("sweepHeightKinkSharded(H=%d,maxn=%d,K=%d): %v", H, maxn, K, err)
	}
	return hTri
}
