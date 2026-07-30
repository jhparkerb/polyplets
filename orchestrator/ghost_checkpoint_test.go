package orchestrator

// ghost_checkpoint_test.go — red-first regression for AUDIT-2026-07-30 O1
// ("Ghost Checkpoint"): the residual G1 stranding hole on the checkpoint
// ERROR path.
//
// writeCheckpoint used to swallow Checkpoint.Write errors (log + continue),
// and the sweep loops passed the THROTTLE decision — "was a write attempted?"
// — into frontierGuard.afterColumn rather than the write OUTCOME. So when a
// write failed (ENOSPC at the a(40) run's 363 GB peak was the realistic
// regime), the guard concluded the on-disk checkpoint now named the NEW
// frontier and GC'd the old one — while Checkpoint.Write's temp+rename means
// the STALE checkpoint, naming exactly those deleted files, survived on disk.
// That is G1's stranding shape reintroduced: resume fails loudly with "cannot
// read input" and the height re-runs from column 0.
//
// The test forces every checkpoint write to fail by pointing CheckpointPath
// into a directory that does not exist (Checkpoint.Write's os.CreateTemp in
// filepath.Dir(path) then fails deterministically on every platform, with no
// dependence on file modes or on the test not running as root), and asserts
// the entry frontier the surviving checkpoint would name is still on disk.
//
// RED before the fix (checkpoint dir absent, maxn=8, checkpoint-every-column):
//
//	--- FAIL: TestFailedCheckpointWriteRetainsFrontier (0.62s)
//	    ghost_checkpoint_test.go:63: seed frontier ".../seed_h3.bin" was GC'd
//	        after every checkpoint write failed: the surviving on-disk
//	        checkpoint names files that no longer exist (G1 stranding on the
//	        error path)
//	--- FAIL: TestFailedCheckpointWriteRetainsFrontierKink (0.55s)
//	    ghost_checkpoint_test.go:63: seed frontier ".../seed_h3.bin" was GC'd ...

import (
	"context"
	"fmt"
	"os"
	"path/filepath"
	"testing"
)

// checkFrontierRetainedOnCheckpointFailure runs cfg with an unwritable
// checkpoint path and asserts the real-swept heights' seed frontiers survive.
func checkFrontierRetainedOnCheckpointFailure(t *testing.T, cfg SweepConfig) {
	t.Helper()
	// Parent directory deliberately absent: every Checkpoint.Write fails.
	cfg.CheckpointPath = filepath.Join(cfg.RunDir, "no_such_dir", "POLYCKPT")
	cfg.CheckpointEvery = 0 // attempt a write at every column boundary

	if _, err := Run(context.Background(), cfg, nil); err != nil {
		t.Fatalf("run with a failing checkpoint path: %v", err)
	}
	if _, err := os.Stat(cfg.CheckpointPath); err == nil {
		t.Fatalf("checkpoint %s exists: the write did not actually fail, test is vacuous", cfg.CheckpointPath)
	}
	// maxn=8 real-sweeps H=3 and H=4 (H=1,2 low closed forms; k=2,3 diagonals;
	// H=7 pole; H=8 top). Their seeds are each height's entry frontier — what a
	// resume checkpoint would name — so neither may be GC'd while no checkpoint
	// superseding them was ever persisted.
	for _, H := range []int{3, 4} {
		seed := filepath.Join(cfg.RunDir, fmt.Sprintf("seed_h%d.bin", H))
		if _, err := os.Stat(seed); err != nil {
			t.Fatalf("seed frontier %q was GC'd after every checkpoint write failed: the surviving on-disk checkpoint names files that no longer exist (G1 stranding on the error path)", seed)
		}
	}
}

func TestFailedCheckpointWriteRetainsFrontier(t *testing.T) {
	dir := t.TempDir()
	checkFrontierRetainedOnCheckpointFailure(t, baseCfg(t, dir))
}

func TestFailedCheckpointWriteRetainsFrontierKink(t *testing.T) {
	dir := t.TempDir()
	checkFrontierRetainedOnCheckpointFailure(t, kinkCfg(t, dir))
}
