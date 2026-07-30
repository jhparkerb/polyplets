package orchestrator

// zero_harvest_test.go — red-first regression for the Zero Harvest bug
// (a(40) incident, results/ns_a40/PROVENANCE.md).
//
// writePerHeight at height completion writes hTri — the per-height
// contributions accumulated by THIS process's sweep. On any mid-height
// resume the pre-resume columns' contributions live only in the
// checkpoint's combined triangle, so the rewritten h<H>.out under-counts;
// in the extreme case — resuming a checkpoint whose height is already
// COMPLETE (the driver re-entering a finished phase, exactly the a(40)
// phase-B relaunch) — there are no columns left to sweep and the file is
// overwritten with all zeros. The banked triangle total stays correct in
// both cases (the checkpoint carries it), which is what made the per-height
// corruption silent until combine's fail-closed guard fired 36h later.
//
// Fix under test: the checkpoint carries the current height's partial
// per-height row (htri lines) and resume seeds it, so the completion-time
// per-height write is whole regardless of where the resume landed; plus
// writePerHeight refuses an all-zero row outright (T(H,H)=3^(H-1)>0 makes
// a legitimate all-zero row impossible).

import (
	"bufio"
	"context"
	"fmt"
	"math/big"
	"os"
	"path/filepath"
	"testing"
)

// perHeightCfg is kinkCfg with per-height output enabled and the sweep
// restricted to the single real-swept height H — the a(40) phase-B shape
// (--heights 20) at gate scale.
func perHeightCfg(t *testing.T, dir string, H int) SweepConfig {
	t.Helper()
	cfg := kinkCfg(t, dir)
	cfg.Heights = []int{H}
	cfg.PerHeightOut = filepath.Join(dir, "perheight")
	if err := os.MkdirAll(cfg.PerHeightOut, 0o777); err != nil {
		t.Fatalf("mkdir perheight: %v", err)
	}
	return cfg
}

func readPerHeightRow(t *testing.T, dir string, H int) map[int]string {
	t.Helper()
	f, err := os.Open(filepath.Join(dir, fmt.Sprintf("h%d.out", H)))
	if err != nil {
		t.Fatalf("open per-height row: %v", err)
	}
	defer f.Close()
	row := map[int]string{}
	sc := bufio.NewScanner(f)
	for sc.Scan() {
		var n int
		var val string
		if _, err := fmt.Sscanf(sc.Text(), "%d %s", &n, &val); err == nil {
			row[n] = val
		}
	}
	return row
}

func checkPerHeightRow(t *testing.T, ctx string, want, got map[int]string) {
	t.Helper()
	if len(got) != len(want) {
		t.Errorf("%s: per-height row has %d entries, want %d", ctx, len(got), len(want))
	}
	for n, w := range want {
		if g, ok := got[n]; !ok || g != w {
			t.Errorf("%s: per-height row n=%d = %q, want %q", ctx, n, g, w)
		}
	}
}

const zeroHarvestH = 4 // real-swept at maxn=8 (diagonal k=4 needs maxn>=9)

// refPerHeightRow computes the reference h<H>.out from a clean, uninterrupted
// run — production-validated per-height output.
func refPerHeightRow(t *testing.T, H int) map[int]string {
	t.Helper()
	dir := t.TempDir()
	cfg := perHeightCfg(t, dir, H)
	if _, err := Run(context.Background(), cfg, nil); err != nil {
		t.Fatalf("reference run: %v", err)
	}
	return readPerHeightRow(t, cfg.PerHeightOut, H)
}

// TestResumeCompletedHeightPreservesPerHeight is the a(40) incident replay:
// run the single-height sweep to natural completion (final checkpoint at the
// last column), then Run again resuming from that checkpoint — the driver
// re-entering a finished phase. The resumed run finds no work; it must NOT
// overwrite the good h<H>.out with zeros.
func TestResumeCompletedHeightPreservesPerHeight(t *testing.T) {
	want := refPerHeightRow(t, zeroHarvestH)

	dir := t.TempDir()
	cfg := perHeightCfg(t, dir, zeroHarvestH)
	if _, err := Run(context.Background(), cfg, nil); err != nil {
		t.Fatalf("initial run: %v", err)
	}
	checkPerHeightRow(t, "pre-resume", want,
		readPerHeightRow(t, cfg.PerHeightOut, zeroHarvestH))

	ck, err := ReadCheckpoint(cfg.CheckpointPath)
	if err != nil {
		t.Fatalf("read checkpoint: %v", err)
	}
	res, err := Run(context.Background(), perHeightCfg(t, dir, zeroHarvestH), ck)
	if err != nil {
		t.Fatalf("resume of completed height (H=%d col=%d): %v", ck.H, ck.Col, err)
	}
	checkTriangleIsRow(t, "completed-height-resume", want, res.Triangle)
	checkPerHeightRow(t, "post-resume", want,
		readPerHeightRow(t, cfg.PerHeightOut, zeroHarvestH))
}

// TestAllZeroPerHeightRefusalIsFatal — red-first regression for
// AUDIT-2026-07-30 O9 ("Advisory Refusal"). Every writePerHeight error,
// INCLUDING the Zero Harvest all-zero refusal, was stderr-only: the run
// continued and exited 0, so the driver's $RC saw success and marched on to
// combine. That is precisely how the a(40) incident stayed silent for 36h.
// The refusal must still preserve the good file on disk (the safe direction)
// AND fail the run.
//
// The all-zero row is forced the way production produced it: resume a
// COMPLETED height from a checkpoint carrying no htri, so there are no
// columns left to sweep and nothing to reconstruct the row from.
//
// RED before the fix:
//
//	--- FAIL: TestAllZeroPerHeightRefusalIsFatal (0.44s)
//	    zero_harvest_test.go:155: Run returned nil after refusing to write an
//	        all-zero h4.out: the refusal is advisory, the process exits 0 and
//	        the driver proceeds to combine
func TestAllZeroPerHeightRefusalIsFatal(t *testing.T) {
	want := refPerHeightRow(t, zeroHarvestH)

	dir := t.TempDir()
	cfg := perHeightCfg(t, dir, zeroHarvestH)
	if _, err := Run(context.Background(), cfg, nil); err != nil {
		t.Fatalf("initial run: %v", err)
	}
	ck, err := ReadCheckpoint(writeLegacyCheckpoint(t, cfg.CheckpointPath))
	if err != nil {
		t.Fatalf("read legacy checkpoint: %v", err)
	}
	if len(ck.HTri) != 0 || len(ck.Frontier) != 0 {
		t.Fatalf("checkpoint htri=%d frontier=%v: not the all-zero-row shape, test is vacuous", len(ck.HTri), ck.Frontier)
	}
	if _, err := Run(context.Background(), perHeightCfg(t, dir, zeroHarvestH), ck); err == nil {
		t.Fatalf("Run returned nil after refusing to write an all-zero h%d.out: the refusal is advisory, the process exits 0 and the driver proceeds to combine", zeroHarvestH)
	}
	// The refusal must still have preserved the good row.
	checkPerHeightRow(t, "all-zero-refusal", want,
		readPerHeightRow(t, cfg.PerHeightOut, zeroHarvestH))
}

// TestClosedFormPerHeightWriteFailureIsFatal covers the other five
// writePerHeight call sites — the closed-form strips (low/pole/diagonal/top),
// which also only logged to stderr. PerHeightOut points at an existing FILE so
// the write fails at MkdirAll for every height.
func TestClosedFormPerHeightWriteFailureIsFatal(t *testing.T) {
	dir := t.TempDir()
	blocked := filepath.Join(dir, "not-a-dir")
	if err := os.WriteFile(blocked, []byte("x"), 0o666); err != nil {
		t.Fatalf("write blocker file: %v", err)
	}
	cfg := kinkCfg(t, dir)
	cfg.PerHeightOut = blocked
	cfg.Heights = []int{1} // H=1 is the low-strip closed form: no sweep at all
	if _, err := Run(context.Background(), cfg, nil); err == nil {
		t.Fatalf("Run returned nil after the H=1 closed-form per-height write failed against %s", blocked)
	}
}

// checkTriangleIsRow asserts a single-height run's triangle equals the
// per-height row T(n,H) (zero everywhere else) — for --heights H they are
// the same sum.
func checkTriangleIsRow(t *testing.T, ctx string, want map[int]string, got []*big.Int) {
	t.Helper()
	for n, v := range got {
		w, expected := want[n]
		if !expected {
			w = "0"
		}
		if v.String() != w {
			t.Errorf("%s: triangle[%d] = %s, want %s", ctx, n, v, w)
		}
	}
}

// TestResumeMidHeightPerHeightRow covers the silent variant: kill the sweep
// at a mid-height column boundary, resume to completion, and require the
// rewritten h<H>.out to be WHOLE — not just the post-resume columns'
// contributions. (The triangle total was always correct across this resume;
// only the per-height file under-counted.)
func TestResumeMidHeightPerHeightRow(t *testing.T) {
	want := refPerHeightRow(t, zeroHarvestH)

	dir := t.TempDir()
	ctx, cancel := context.WithCancel(context.Background())
	cfg := perHeightCfg(t, dir, zeroHarvestH)
	fired := false
	cfg.afterColumn = func(H, col int) {
		// col>=1: at least one column's contributions are checkpoint-only,
		// the exact under-count window.
		if !fired && col >= 1 {
			fired = true
			cancel()
		}
	}
	_, err := Run(ctx, cfg, nil)
	cancel()
	if !fired {
		t.Fatal("afterColumn never fired at col>=1: mid-height path not exercised")
	}
	if err == nil {
		t.Fatal("expected a cancellation error from the mid-height kill, got nil")
	}
	if ctx.Err() == nil {
		t.Fatalf("run failed for a non-cancellation reason: %v", err)
	}

	ck, err := ReadCheckpoint(cfg.CheckpointPath)
	if err != nil {
		t.Fatalf("read checkpoint: %v", err)
	}
	res, err := Run(context.Background(), perHeightCfg(t, dir, zeroHarvestH), ck)
	if err != nil {
		t.Fatalf("resume (H=%d col=%d): %v", ck.H, ck.Col, err)
	}
	checkTriangleIsRow(t, "mid-height-resume", want, res.Triangle)
	checkPerHeightRow(t, "mid-height-resume", want,
		readPerHeightRow(t, cfg.PerHeightOut, zeroHarvestH))
}
