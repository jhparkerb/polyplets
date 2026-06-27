package orchestrator

// resume_test.go — exhaustive kill+resume gate (replaces the old random-timing
// fuzz harness, tests/gate_ns_resume.sh).
//
// The resumable state space is finite: a checkpoint is only ever written at a
// completed-column boundary (H, col).  So instead of SIGTERMing the process at
// a random wall-clock delay and hoping to land mid-run, we enumerate every
// boundary, cancel cleanly there via the afterColumn test seam, and assert that
// resuming from the checkpoint reproduces the known triangle.  Deterministic,
// exhaustive, reproducible by boundary index k.

import (
	"context"
	"os"
	"path/filepath"
	"strconv"
	"testing"
)

const (
	resumeMaxn  = 8
	resumeCores = 4
	resumeRAM   = 4 << 20
)

// TestKillResumeAllBoundaries walks every checkpoint boundary k = 0, 1, 2, …:
// run the sweep, cancel right after the k-th forward checkpoint, then resume
// from that checkpoint to completion and check the total.  The loop ends when
// cancelling at k would be at/after the final boundary (the run completes with
// no error and the full result is verified directly).
func TestKillResumeAllBoundaries(t *testing.T) {
	known := loadKnownTriangle(t)

	for k := 0; ; k++ {
		dir := t.TempDir()

		// Stop half: real Run, cancelled after the k-th forward checkpoint.
		ctx, cancel := context.WithCancel(context.Background())
		seen := 0
		cfg := baseCfg(t, dir)
		cfg.afterColumn = func(H, col int) {
			if seen == k {
				cancel()
			}
			seen++
		}
		res, err := Run(ctx, cfg, nil)
		cancel()

		if err == nil {
			// k is at/past the last boundary: the run completed.  Verify the
			// full result once and stop enumerating.
			checkTriangle(t, "natural-finish", known, res.Triangle)
			t.Logf("enumerated %d checkpoint boundaries", k)
			return
		}
		if ctx.Err() == nil {
			t.Fatalf("k=%d: run failed (not a cancellation): %v", k, err)
		}

		// Resume half: real Run from the checkpoint the stop half just wrote.
		ck, err := ReadCheckpoint(cfg.CheckpointPath)
		if err != nil {
			t.Fatalf("k=%d: read checkpoint: %v", k, err)
		}
		res, err = Run(context.Background(), baseCfg(t, dir), ck)
		if err != nil {
			t.Fatalf("k=%d: resume (H=%d col=%d): %v", k, ck.H, ck.Col, err)
		}
		checkTriangle(t, "resume k="+strconv.Itoa(k), known, res.Triangle)
	}
}

func baseCfg(t *testing.T, dir string) SweepConfig {
	t.Helper()
	spill := filepath.Join(dir, "spill")
	if err := os.MkdirAll(spill, 0o777); err != nil {
		t.Fatalf("mkdir spill: %v", err)
	}
	return SweepConfig{
		Maxn:            resumeMaxn,
		Fold:            true,
		Cores:           resumeCores,
		RAM:             resumeRAM,
		RunDir:          dir,
		SpillDir:        spill,
		CheckpointPath:  filepath.Join(dir, "POLYCKPT"),
		CheckpointEvery: 0, // checkpoint every column
		Rev:             "test",
		Bin:             DefaultWorkerBin(".."),
	}
}

func checkTriangle(t *testing.T, ctx string, known, got []uint64) {
	t.Helper()
	for n := 1; n <= resumeMaxn; n++ {
		want := uint64(0)
		if n < len(known) {
			want = known[n]
		}
		g := uint64(0)
		if n < len(got) {
			g = got[n]
		}
		if g != want {
			t.Fatalf("%s: n=%d a(n)=%d known=%d", ctx, n, g, want)
		}
	}
}

// loadKnownTriangle reads the same fixture the production --compare uses.
func loadKnownTriangle(t *testing.T) []uint64 {
	t.Helper()
	path := filepath.Join("..", "fixtures", "b006770.txt")
	known, err := LoadKnown(path)
	if err != nil {
		t.Fatalf("read fixture %s: %v", path, err)
	}
	if len(known) <= resumeMaxn {
		t.Fatalf("fixture has too few values: got %d, need > %d", len(known), resumeMaxn)
	}
	return known
}
