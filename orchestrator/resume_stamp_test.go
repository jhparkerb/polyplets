package orchestrator

// resume_stamp_test.go — red-first regressions for AUDIT-2026-07-30 O3
// ("Strict Route Amnesia") and O4 ("Mode Amnesia"): two run parameters that
// silently change what a resumed run COMPUTES, neither covered by June's B1
// config stamp.
//
// O3: --max-diag-k decides, per height, whether a strip is injected from its
// closed form or really swept. The flag's own help said "a resumed run must
// pass the same value" and nothing enforced it, so a resume under a different
// cap re-sweeps (or injects) a different set of cells than the run it
// continues — which can manufacture self-confirming holdout evidence: a strip
// swept for real before the crash, injected from the very formula it was
// meant to test after it.
//
// O4: the two checkpoint FORMS are not interchangeable. An overlap
// (Done-set) checkpoint resumed sequentially short-circuits the B7
// height-membership check and re-sweeps every height on top of an already
// populated triangle; a sequential checkpoint resumed in overlap mode has no
// Done set, so all progress is silently discarded.
//
// RED before the fix:
//
//	--- FAIL: TestResumeRefusesMaxDiagKMismatch (0.09s)
//	    resume_stamp_test.go:76: resume with --max-diag-k -1 from a checkpoint
//	        written under --max-diag-k 2 was ALLOWED: the two runs inject a
//	        different set of cells
//	--- FAIL: TestResumeRefusesOverlapCheckpointSequentially (0.08s)
//	    resume_stamp_test.go:136: sequential resume from an OVERLAP checkpoint
//	        (done=[8 5 7 6]) was ALLOWED: the Done set short-circuits the B7
//	        height check and every height re-sweeps onto a populated triangle
//	--- FAIL: TestResumeRefusesSequentialCheckpointInOverlap (0.05s)
//	    resume_stamp_test.go:155: overlap resume from a SEQUENTIAL checkpoint
//	        (H=3 col=0) was ALLOWED: it has no Done set, so all progress is
//	        silently discarded

import (
	"context"
	"sync"
	"testing"
)

// cancelAtFirstColumn runs cfg and cancels at its first column boundary,
// leaving a sequential-form checkpoint on disk.
func cancelAtFirstColumn(t *testing.T, cfg SweepConfig) {
	t.Helper()
	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()
	fired := false
	cfg.afterColumn = func(int, int) {
		if !fired {
			fired = true
			cancel()
		}
	}
	if _, err := Run(ctx, cfg, nil); err == nil {
		t.Fatal("expected a cancellation error, got nil")
	}
	if !fired {
		t.Fatal("afterColumn never fired: no checkpoint written")
	}
}

func TestResumeRefusesMaxDiagKMismatch(t *testing.T) {
	dir := t.TempDir()
	cfg := baseCfg(t, dir)
	cfg.MaxDiagK = 2 // k=3 (H=5) really swept instead of injected
	cancelAtFirstColumn(t, cfg)

	ck, err := ReadCheckpoint(cfg.CheckpointPath)
	if err != nil {
		t.Fatalf("read checkpoint: %v", err)
	}
	resumed := baseCfg(t, dir) // MaxDiagK back at the no-cap default
	if _, err := Run(context.Background(), resumed, ck); err == nil {
		t.Fatalf("resume with --max-diag-k %d from a checkpoint written under --max-diag-k %d was ALLOWED: the two runs inject a different set of cells", resumed.MaxDiagK, cfg.MaxDiagK)
	}
}

// TestResumeAcceptsMatchingMaxDiagK is the must-not-over-refuse direction.
func TestResumeAcceptsMatchingMaxDiagK(t *testing.T) {
	known := loadKnownTriangle(t)
	dir := t.TempDir()
	cfg := baseCfg(t, dir)
	cfg.MaxDiagK = 2
	cancelAtFirstColumn(t, cfg)

	ck, err := ReadCheckpoint(cfg.CheckpointPath)
	if err != nil {
		t.Fatalf("read checkpoint: %v", err)
	}
	resumed := baseCfg(t, dir)
	resumed.MaxDiagK = 2
	res, err := Run(context.Background(), resumed, ck)
	if err != nil {
		t.Fatalf("resume under the SAME --max-diag-k must work: %v", err)
	}
	checkTriangle(t, "max-diag-k matched resume", known, res.Triangle)
}

// overlapCheckpoint runs an overlap sweep and cancels after its first height
// completion, leaving an overlap-form (Done-set) checkpoint.
func overlapCheckpoint(t *testing.T, dir string) SweepConfig {
	t.Helper()
	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()
	cfg := baseCfg(t, dir)
	cfg.OverlapHeights = 4
	var mu sync.Mutex
	done := 0
	cfg.afterHeight = func(int) {
		mu.Lock()
		done++
		mu.Unlock()
		cancel()
	}
	if _, err := Run(ctx, cfg, nil); err == nil {
		t.Fatal("expected a cancellation error from the overlap run, got nil")
	}
	return cfg
}

func TestResumeRefusesOverlapCheckpointSequentially(t *testing.T) {
	dir := t.TempDir()
	cfg := overlapCheckpoint(t, dir)

	ck, err := ReadCheckpoint(cfg.CheckpointPath)
	if err != nil {
		t.Fatalf("read overlap checkpoint: %v", err)
	}
	if len(ck.Done) == 0 {
		t.Fatalf("checkpoint has no Done set: not the overlap form, test is vacuous")
	}
	resumed := baseCfg(t, dir) // sequential
	if _, err := Run(context.Background(), resumed, ck); err == nil {
		t.Fatalf("sequential resume from an OVERLAP checkpoint (done=%v) was ALLOWED: the Done set short-circuits the B7 height check and every height re-sweeps onto a populated triangle", ck.Done)
	}
}

func TestResumeRefusesSequentialCheckpointInOverlap(t *testing.T) {
	dir := t.TempDir()
	cfg := baseCfg(t, dir)
	cancelAtFirstColumn(t, cfg)

	ck, err := ReadCheckpoint(cfg.CheckpointPath)
	if err != nil {
		t.Fatalf("read checkpoint: %v", err)
	}
	if len(ck.Done) != 0 {
		t.Fatalf("checkpoint has a Done set: not the sequential form, test is vacuous")
	}
	resumed := baseCfg(t, dir)
	resumed.OverlapHeights = 4
	if _, err := Run(context.Background(), resumed, ck); err == nil {
		t.Fatalf("overlap resume from a SEQUENTIAL checkpoint (H=%d col=%d) was ALLOWED: it has no Done set, so all progress is silently discarded", ck.H, ck.Col)
	}
}
