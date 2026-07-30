package orchestrator

// legacy_ledger_test.go — red-first regression for AUDIT-2026-07-30 O2
// ("Legacy Ledger"): a checkpoint written BEFORE the Zero Harvest fix
// (c789bfb) carries no `htri` lines, so resume.HTri is nil and a MID-HEIGHT
// resume rewrites h<H>.out from the post-resume columns alone — a short but
// NONZERO row. Nothing catches it: writePerHeight's all-zero refusal only
// fires when zero columns were swept, and combine's guards are blind to a
// nonzero under-count. The two formats were indistinguishable (same
// `POLYCKPT 1` header, and "no htri lines" is not a usable discriminator
// because a legitimately-zero partial row is sparse-encoded identically), so
// the fix stamps a format VERSION and refuses the unreconstructable case.
//
// RED before the fix:
//
//	--- FAIL: TestLegacyCheckpointMidHeightResumeRefused (0.45s)
//	    legacy_ledger_test.go:112: resume from a pre-htri mid-height checkpoint
//	        (H=4 col=1) was ALLOWED and wrote a SHORT h4.out: n=4 got "26"
//	        want "27" (whole row); nothing downstream catches a nonzero
//	        under-count

import (
	"bufio"
	"context"
	"os"
	"path/filepath"
	"strings"
	"testing"
)

// writeLegacyCheckpoint rewrites a checkpoint in the pre-Zero-Harvest format:
// header forced to version 1, every `htri` line dropped, and the `end`
// terminator removed (version 1 had none — see O7). Returns the new path (the
// original is left intact).
func writeLegacyCheckpoint(t *testing.T, path string) string {
	t.Helper()
	f, err := os.Open(path)
	if err != nil {
		t.Fatalf("open checkpoint: %v", err)
	}
	defer f.Close()
	var b strings.Builder
	sc := bufio.NewScanner(f)
	first := true
	for sc.Scan() {
		line := sc.Text()
		if first {
			line, first = "POLYCKPT 1", false
		} else if strings.HasPrefix(line, "htri ") || strings.HasPrefix(line, "end ") {
			continue
		}
		b.WriteString(line)
		b.WriteString("\n")
	}
	if err := sc.Err(); err != nil {
		t.Fatalf("scan checkpoint: %v", err)
	}
	out := path + ".legacy"
	if err := os.WriteFile(out, []byte(b.String()), 0o666); err != nil {
		t.Fatalf("write legacy checkpoint: %v", err)
	}
	return out
}

// midHeightCheckpoint runs the single-height sweep and cancels it at a
// mid-height column boundary (col>=1), leaving a checkpoint with completed
// columns whose contributions live only in the ledger.
func midHeightCheckpoint(t *testing.T, dir string) SweepConfig {
	t.Helper()
	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()
	cfg := perHeightCfg(t, dir, zeroHarvestH)
	fired := false
	cfg.afterColumn = func(H, col int) {
		if !fired && col >= 1 {
			fired = true
			cancel()
		}
	}
	if _, err := Run(ctx, cfg, nil); err == nil {
		t.Fatal("expected a cancellation error from the mid-height kill, got nil")
	}
	if !fired {
		t.Fatal("afterColumn never fired at col>=1: mid-height path not exercised")
	}
	return cfg
}

func TestLegacyCheckpointMidHeightResumeRefused(t *testing.T) {
	want := refPerHeightRow(t, zeroHarvestH)

	dir := t.TempDir()
	cfg := midHeightCheckpoint(t, dir)

	legacy := writeLegacyCheckpoint(t, cfg.CheckpointPath)
	ck, err := ReadCheckpoint(legacy)
	if err != nil {
		t.Fatalf("read legacy checkpoint: %v", err)
	}
	if ck.Col < 0 || len(ck.Frontier) == 0 {
		t.Fatalf("checkpoint H=%d col=%d frontier=%v is not mid-height: test is vacuous", ck.H, ck.Col, ck.Frontier)
	}
	if len(ck.HTri) != 0 {
		t.Fatalf("legacy rewrite left %d htri entries: test is vacuous", len(ck.HTri))
	}

	resumed := perHeightCfg(t, dir, zeroHarvestH)
	resumed.CheckpointPath = legacy
	if _, err := Run(context.Background(), resumed, ck); err == nil {
		got := readPerHeightRow(t, resumed.PerHeightOut, zeroHarvestH)
		for n, w := range want {
			if g := got[n]; g != w {
				t.Fatalf("resume from a pre-htri mid-height checkpoint (H=%d col=%d) was ALLOWED and wrote a SHORT h%d.out: n=%d got %q want %q (whole row); nothing downstream catches a nonzero under-count",
					ck.H, ck.Col, zeroHarvestH, n, g, w)
			}
		}
		t.Fatalf("resume from a pre-htri mid-height checkpoint (H=%d col=%d) was ALLOWED", ck.H, ck.Col)
	}
}

// TestLegacyCheckpointCompletedHeightResumeAllowed pins the state O2 must NOT
// over-refuse: a legacy checkpoint at a COMPLETED height (nil frontier — the
// preserved a(40) POLYCKPT.B shape). checkResumeConfig lets it through; the
// sweep then finds no columns left, writePerHeight's all-zero refusal fires,
// and the good h<H>.out on disk survives. Since O9 that refusal also fails the
// run — the failure must be the write refusal, never O2's start-time refusal.
func TestLegacyCheckpointCompletedHeightResumeAllowed(t *testing.T) {
	want := refPerHeightRow(t, zeroHarvestH)

	dir := t.TempDir()
	cfg := perHeightCfg(t, dir, zeroHarvestH)
	if _, err := Run(context.Background(), cfg, nil); err != nil {
		t.Fatalf("initial run: %v", err)
	}
	legacy := writeLegacyCheckpoint(t, cfg.CheckpointPath)
	ck, err := ReadCheckpoint(legacy)
	if err != nil {
		t.Fatalf("read legacy checkpoint: %v", err)
	}
	if len(ck.Frontier) != 0 {
		t.Fatalf("checkpoint frontier=%v: height not complete, test is vacuous", ck.Frontier)
	}
	resumed := perHeightCfg(t, dir, zeroHarvestH)
	resumed.CheckpointPath = legacy
	_, err = Run(context.Background(), resumed, ck)
	if err != nil && strings.Contains(err.Error(), "predates the Zero Harvest fix") {
		t.Fatalf("O2 refused a legacy COMPLETED-height checkpoint at start; only the MID-height case is unserveable: %v", err)
	}
	if err == nil || !strings.Contains(err.Error(), "refusing to write all-zero") {
		t.Fatalf("resume of a legacy COMPLETED-height checkpoint: got %v, want the all-zero write refusal (fatal since O9)", err)
	}
	checkPerHeightRow(t, "legacy-completed-height-resume", want,
		readPerHeightRow(t, resumed.PerHeightOut, zeroHarvestH))
}

// TestLegacyCheckpointFreshHeightResumeAllowed pins the other legitimate
// legacy state: a height that had not completed a single column (col=-1), so
// there is nothing for htri to carry and the rewritten row is whole.
func TestLegacyCheckpointFreshHeightResumeAllowed(t *testing.T) {
	want := refPerHeightRow(t, zeroHarvestH)

	dir := t.TempDir()
	cfg := perHeightCfg(t, dir, zeroHarvestH)
	seed := filepath.Join(cfg.RunDir, "seed_h4.bin")
	if err := WriteSeedPolyrun(seed, cfg.Rev, zeroHarvestH, cfg.Maxn, cfg.CounterWidth); err != nil {
		t.Fatalf("write seed: %v", err)
	}
	ck := &Checkpoint{
		Version: 1, H: zeroHarvestH, Col: -1, Frontier: []string{seed},
		Maxn: cfg.Maxn, Counter: counterName(cfg.CounterWidth),
		Fold: cfg.Fold, Kernel: kernelName(cfg.Kernel),
	}
	if _, err := Run(context.Background(), cfg, ck); err != nil {
		t.Fatalf("resume of a legacy FRESH-height checkpoint must still work: %v", err)
	}
	checkPerHeightRow(t, "legacy-fresh-height-resume", want,
		readPerHeightRow(t, cfg.PerHeightOut, zeroHarvestH))
}
