package orchestrator

// kink_resume_midcolumn_test.go — red-first regression for the kink kernel's
// real-SIGTERM + resume over-count (docs/engine-record.md).
//
// The existing exhaustive resume gate (resume_test.go) cancels only at
// COMPLETED column boundaries via the afterColumn seam, and defaults to the
// column kernel — so it never exercises the kink kernel's MID-column error-path
// checkpoint. That path is where the bug lived: sweepHeightKink folded a
// column's seed-round contribution into hTri BEFORE the column finished, but a
// mid-column checkpoint stamps Col=col-1 and the pre-column input frontier. On
// resume the column re-runs from scratch and its seed contribution is counted
// twice → a consistent over-count from the killed height upward.
//
// This test kills the run mid-column (right after a seed round, before the
// stage/finalize rounds) via the afterSeedRound seam, resumes from the
// checkpoint, and asserts the resumed triangle matches the known values. It is
// deterministic (no wall-clock timing) and RED before the fix.

import (
	"context"
	"testing"
)

func kinkCfg(t *testing.T, dir string) SweepConfig {
	t.Helper()
	cfg := baseCfg(t, dir)
	cfg.Kernel = "kink"
	return cfg
}

// TestKinkResumeMidColumn cancels right after the seed round of the first
// mid-column position (col>=1) of the first real-swept height, then resumes.
func TestKinkResumeMidColumn(t *testing.T) {
	known := loadKnownTriangle(t)

	dir := t.TempDir()
	ctx, cancel := context.WithCancel(context.Background())
	cfg := kinkCfg(t, dir)

	fired := false
	cfg.afterSeedRound = func(H, col int) {
		// col>=1 guarantees the kill lands after at least one column of this
		// height has fully completed, so the checkpoint's Col=col-1 refers to a
		// real completed column and hTri already holds col's seed contribution
		// in the buggy code — the exact double-count window.
		if !fired && col >= 1 {
			fired = true
			cancel()
		}
	}

	_, err := Run(ctx, cfg, nil)
	cancel()

	if !fired {
		t.Fatal("afterSeedRound never fired at col>=1: test never exercised the mid-column path")
	}
	if err == nil {
		t.Fatal("expected a cancellation error from the mid-column kill, got nil")
	}
	if ctx.Err() == nil {
		t.Fatalf("run failed for a non-cancellation reason: %v", err)
	}

	ck, err := ReadCheckpoint(cfg.CheckpointPath)
	if err != nil {
		t.Fatalf("read checkpoint: %v", err)
	}

	res, err := Run(context.Background(), kinkCfg(t, dir), ck)
	if err != nil {
		t.Fatalf("resume (H=%d col=%d): %v", ck.H, ck.Col, err)
	}
	checkTriangle(t, "kink-mid-column-resume", known, res.Triangle)
}
