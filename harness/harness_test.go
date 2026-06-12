package main

// Gate G3 (TDD: written before the implementation).
//
// The harness is the custodian of provenance (implementation-plan.md rule 3),
// so the tests cover the four behaviors a campaign's integrity rests on:
//   1. split workers merge to exactly the unsplit engine run
//   2. resume skips completed workers and redoes missing ones
//   3. transient worker failures are retried
//   4. the ledger records campaigns and verification, append-only;
//      Verify accepts equal campaigns and rejects tampered ones

import (
	"encoding/json"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	"testing"
)

func repoRoot(t *testing.T) string {
	t.Helper()
	cwd, err := os.Getwd()
	if err != nil {
		t.Fatal(err)
	}
	return filepath.Dir(cwd)
}

func g2Binary(t *testing.T) string {
	t.Helper()
	p := filepath.Join(repoRoot(t), "build", "g2")
	if _, err := os.Stat(p); err != nil {
		t.Skipf("build/g2 not present (run make build/g2): %v", err)
	}
	return p
}

func writeScript(t *testing.T, dir, name, body string) string {
	t.Helper()
	p := filepath.Join(dir, name)
	if err := os.WriteFile(p, []byte(body), 0o755); err != nil {
		t.Fatal(err)
	}
	return p
}

func mustRun(t *testing.T, c *Campaign) {
	t.Helper()
	if err := c.Run(); err != nil {
		t.Fatalf("campaign failed: %v", err)
	}
}

// 1. A split campaign must reproduce the unsplit engine run exactly.
func TestCampaignMatchesUnsplitRun(t *testing.T) {
	g2 := g2Binary(t)
	tmp := t.TempDir()

	c := &Campaign{
		Dir:    filepath.Join(tmp, "camp"),
		Ledger: filepath.Join(tmp, "ledger.jsonl"),
		Spec: Spec{Binary: g2, Lattice: "square8", MaxN: 9,
			SplitS: 4, K: 3, Retries: 0, J: 2},
	}
	mustRun(t, c)

	merged, err := readCounts(filepath.Join(c.Dir, "results.txt"))
	if err != nil {
		t.Fatal(err)
	}
	direct, err := exec.Command(g2, "square8", "9").Output()
	if err != nil {
		t.Fatal(err)
	}
	want, err := parseCounts(direct)
	if err != nil {
		t.Fatal(err)
	}
	if len(merged) != len(want) {
		t.Fatalf("merged has %d sizes, want %d", len(merged), len(want))
	}
	for n, v := range want {
		if merged[n] != v {
			t.Errorf("n=%d: merged %d, unsplit %d", n, merged[n], v)
		}
	}
}

// 2. Resume: completed workers are not re-run; missing ones are redone.
func TestResumeSkipsCompletedWorkers(t *testing.T) {
	tmp := t.TempDir()
	fake := writeScript(t, tmp, "fake.sh", "#!/bin/sh\necho \"1 7\"\necho \"2 11\"\n")

	c := &Campaign{
		Dir:    filepath.Join(tmp, "camp"),
		Ledger: filepath.Join(tmp, "ledger.jsonl"),
		Spec: Spec{Binary: fake, Lattice: "square8", MaxN: 2,
			SplitS: 1, K: 3, Retries: 0, J: 1},
	}
	mustRun(t, c)

	// Plant a sentinel as worker 1's completed output (with a consistent
	// .ok hash): a resumed campaign must keep it untouched.
	sentinel := []byte("1 1000000\n2 2000000\n")
	if err := markWorkerDone(c, 1, sentinel); err != nil {
		t.Fatal(err)
	}
	// Remove worker 2 entirely: resume must regenerate it.
	for _, f := range []string{c.workerOut(2), c.workerOK(2)} {
		if err := os.Remove(f); err != nil {
			t.Fatal(err)
		}
	}
	mustRun(t, c)

	out1, err := os.ReadFile(c.workerOut(1))
	if err != nil {
		t.Fatal(err)
	}
	if string(out1) != string(sentinel) {
		t.Errorf("worker 1 was re-run on resume; sentinel clobbered")
	}
	if _, err := os.Stat(c.workerOut(2)); err != nil {
		t.Errorf("worker 2 not regenerated: %v", err)
	}
	merged, err := readCounts(filepath.Join(c.Dir, "results.txt"))
	if err != nil {
		t.Fatal(err)
	}
	if merged[1] != 7+1000000+7 {
		t.Errorf("merged n=1: got %d, want %d (sentinel respected)",
			merged[1], 7+1000000+7)
	}
}

// 3. A worker that fails transiently is retried and the campaign succeeds.
func TestRetryTransientFailure(t *testing.T) {
	tmp := t.TempDir()
	markers := filepath.Join(tmp, "markers")
	if err := os.MkdirAll(markers, 0o755); err != nil {
		t.Fatal(err)
	}
	t.Setenv("MARKER_DIR", markers)
	flaky := writeScript(t, tmp, "flaky.sh",
		"#!/bin/sh\n"+
			"idx=\"$6\"\n"+
			"if [ ! -f \"$MARKER_DIR/m$idx\" ]; then\n"+
			"  touch \"$MARKER_DIR/m$idx\"\n"+
			"  echo transient >&2\n"+
			"  exit 1\n"+
			"fi\n"+
			"echo \"1 5\"\n")

	c := &Campaign{
		Dir:    filepath.Join(tmp, "camp"),
		Ledger: filepath.Join(tmp, "ledger.jsonl"),
		Spec: Spec{Binary: flaky, Lattice: "square8", MaxN: 1,
			SplitS: 1, K: 2, Retries: 1, J: 1},
	}
	mustRun(t, c)
	merged, err := readCounts(filepath.Join(c.Dir, "results.txt"))
	if err != nil {
		t.Fatal(err)
	}
	if merged[1] != 10 {
		t.Errorf("merged n=1: got %d, want 10", merged[1])
	}
	// stderr from the failed first attempts must have been captured
	// implicitly, per worker, separately from stdout
	for idx := 0; idx < 2; idx++ {
		data, err := os.ReadFile(c.workerErr(idx))
		if err != nil {
			t.Errorf("worker %d stderr not captured: %v", idx, err)
		} else if !strings.Contains(string(data), "transient") {
			t.Errorf("worker %d .err missing diagnostic: %q", idx, data)
		}
	}
}

// A resumed campaign with a different spec must be rejected.
func TestSpecMismatchRejected(t *testing.T) {
	tmp := t.TempDir()
	fake := writeScript(t, tmp, "fake.sh", "#!/bin/sh\necho \"1 7\"\n")
	dir := filepath.Join(tmp, "camp")
	ledger := filepath.Join(tmp, "ledger.jsonl")

	a := &Campaign{Dir: dir, Ledger: ledger,
		Spec: Spec{Binary: fake, Lattice: "square8", MaxN: 1,
			SplitS: 1, K: 2, Retries: 0, J: 1}}
	mustRun(t, a)

	b := &Campaign{Dir: dir, Ledger: ledger,
		Spec: Spec{Binary: fake, Lattice: "square8", MaxN: 5, // changed
			SplitS: 1, K: 2, Retries: 0, J: 1}}
	if err := b.Run(); err == nil {
		t.Fatal("campaign with mismatched spec was accepted")
	}
}

// 4. Ledger records; Verify accepts agreement, rejects tampering.
func TestLedgerAndVerify(t *testing.T) {
	g2 := g2Binary(t)
	tmp := t.TempDir()
	ledger := filepath.Join(tmp, "ledger.jsonl")

	mk := func(name string, k int) *Campaign {
		return &Campaign{
			Dir:    filepath.Join(tmp, name),
			Ledger: ledger,
			Spec: Spec{Binary: g2, Lattice: "square8", MaxN: 8,
				SplitS: 3, K: k, Retries: 0, J: 2},
		}
	}
	a, b := mk("a", 2), mk("b", 3) // different splits, same truth
	mustRun(t, a)
	mustRun(t, b)

	if err := Verify(a.Dir, b.Dir, ledger); err != nil {
		t.Fatalf("verify of agreeing campaigns failed: %v", err)
	}

	data, err := os.ReadFile(ledger)
	if err != nil {
		t.Fatal(err)
	}
	lines := strings.Split(strings.TrimSpace(string(data)), "\n")
	if len(lines) != 3 { // 2 campaign_complete + 1 verified
		t.Fatalf("ledger has %d lines, want 3:\n%s", len(lines), data)
	}
	var last LedgerEntry
	if err := json.Unmarshal([]byte(lines[2]), &last); err != nil {
		t.Fatalf("ledger line not valid JSON: %v", err)
	}
	if last.Event != "verified" || last.ResultSHA256 == "" ||
		last.Host == "" || last.Time == "" {
		t.Errorf("verified entry incomplete: %+v", last)
	}

	// Tamper with campaign b and verify again: must fail.
	res := filepath.Join(b.Dir, "results.txt")
	if err := os.WriteFile(res, []byte("1 1\n2 999\n"), 0o644); err != nil {
		t.Fatal(err)
	}
	if err := Verify(a.Dir, b.Dir, ledger); err == nil {
		t.Fatal("verify accepted tampered results")
	}
}
