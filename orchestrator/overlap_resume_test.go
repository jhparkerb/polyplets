package orchestrator

// overlap_resume_test.go — kill+resume gate for OVERLAP mode (height-boundary
// checkpoints). In overlap mode heights finish out of order, so the resumable
// unit is the SET of completed heights. This walks k = 1, 2, …: run the overlap
// sweep, cancel right after the k-th height completes, then resume from the
// height-boundary checkpoint and assert the total reproduces the known triangle
// (no double-count of done heights, no gap from in-flight ones).
//
// RED before the feature: overlap used noopCkpt and wrote no resumable
// checkpoint, so ReadCheckpoint fails / resume re-runs everything and the
// triangle double-counts.

import (
	"context"
	"strconv"
	"sync"
	"testing"
)

func TestOverlapHeightResume(t *testing.T) {
	known := loadKnownTriangle(t)

	for k := 1; ; k++ {
		dir := t.TempDir()

		ctx, cancel := context.WithCancel(context.Background())
		var mu sync.Mutex
		done := 0
		cfg := baseCfg(t, dir)
		cfg.OverlapHeights = 4
		cfg.afterHeight = func(int) {
			mu.Lock()
			done++
			d := done
			mu.Unlock()
			if d == k {
				cancel()
			}
		}
		res, err := Run(ctx, cfg, nil)
		cancel()

		if err == nil {
			// k exceeded the number of height completions: the run finished.
			checkTriangle(t, "overlap natural-finish", known, res.Triangle)
			t.Logf("enumerated %d height completions", k)
			return
		}
		if ctx.Err() == nil {
			t.Fatalf("k=%d: overlap run failed (not a cancellation): %v", k, err)
		}

		ck, err := ReadCheckpoint(cfg.CheckpointPath)
		if err != nil {
			t.Fatalf("k=%d: read overlap checkpoint: %v", k, err)
		}
		if len(ck.Done) == 0 {
			t.Fatalf("k=%d: overlap checkpoint has no Done set (not resumable)", k)
		}

		rcfg := baseCfg(t, dir)
		rcfg.OverlapHeights = 4
		res, err = Run(context.Background(), rcfg, ck)
		if err != nil {
			t.Fatalf("k=%d: overlap resume (done=%v): %v", k, ck.Done, err)
		}
		checkTriangle(t, "overlap resume k="+strconv.Itoa(k), known, res.Triangle)
	}
}
