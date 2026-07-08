package orchestrator

import (
	"context"
	"os"
	"strconv"
	"testing"
)

// TestWorkerPoolMapMatchesOneShot drives the REAL compiled map_worker binary
// (build/ns/map_worker, must be built first -- `make build/ns/map_worker`)
// through WorkerPool.RunMap for several sequential requests on the same
// pool, and checks each result matches the old one-shot RunMapWorker exactly
// (same triangle contributions, same output record count) -- this is the
// Go-side half of Bottleneck #5 (docs/utilization-bottleneck-log.md): the
// C++ --persistent plumbing is gated separately (test/gate_persistent_worker.cpp);
// this proves the pool wrapper (checkout/checkin, request-line building,
// response scanning, lazy per-role start) is correct.
func TestWorkerPoolMapMatchesOneShot(t *testing.T) {
	bin := DefaultWorkerBin("..")
	if _, err := os.Stat(bin.MapWorker); err != nil {
		t.Skipf("build/ns/map_worker not built: %v (run `make build/ns/map_worker` first)", err)
	}

	dir := t.TempDir()
	ctx := context.Background()

	type col struct {
		H, maxn int
	}
	cols := []col{{H: 4, maxn: 8}, {H: 6, maxn: 10}, {H: 4, maxn: 8}}

	pool := NewWorkerPool(ctx, bin, 4)
	defer pool.Close()

	for i, c := range cols {
		seed := dir + "/seed" + strconv.Itoa(i) + ".bin"
		if err := WriteSeedPolyrun(seed, "test", c.H, c.maxn); err != nil {
			t.Fatalf("WriteSeedPolyrun: %v", err)
		}

		poolOut := dir + "/pool" + strconv.Itoa(i) + ".bin"
		poolArgs := MapArgs{
			InPaths: []string{seed}, H: c.H, Maxn: c.maxn,
			RAM: 128 * 1024 * 1024, SpillDir: dir, OutPath: poolOut,
		}
		poolRes, err := pool.RunMap(poolArgs, nil, nil)
		if err != nil {
			t.Fatalf("col %d: pool.RunMap: %v", i, err)
		}

		oneOut := dir + "/oneshot" + strconv.Itoa(i) + ".bin"
		oneArgs := poolArgs
		oneArgs.OutPath = oneOut
		oneRes, err := RunMapWorker(ctx, bin, oneArgs, nil, nil)
		if err != nil {
			t.Fatalf("col %d: RunMapWorker (one-shot ref): %v", i, err)
		}

		if poolRes.OutRecords != oneRes.OutRecords {
			t.Errorf("col %d: OutRecords pool=%d oneshot=%d", i, poolRes.OutRecords, oneRes.OutRecords)
		}
		if len(poolRes.TriContribs) != len(oneRes.TriContribs) {
			t.Errorf("col %d: TriContribs height count pool=%d oneshot=%d",
				i, len(poolRes.TriContribs), len(oneRes.TriContribs))
		}
		for h, row := range oneRes.TriContribs {
			poolRow, ok := poolRes.TriContribs[h]
			if !ok {
				t.Errorf("col %d: pool missing TriContribs[%d]", i, h)
				continue
			}
			for n, v := range row {
				pv, ok := poolRow[n]
				if !ok || pv.Cmp(v) != 0 {
					t.Errorf("col %d: TriContribs[%d][%d] pool=%v oneshot=%v", i, h, n, pv, v)
				}
			}
		}
	}
}
