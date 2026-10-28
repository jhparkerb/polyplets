package orchestrator

// checkpoint_terminator_test.go — red-first regression: ReadCheckpoint accepted any PREFIX of a checkpoint:
// there was no terminator and no record count, so a file cut short mid-`tri`
// parsed cleanly into a checkpoint whose triangle is missing its tail. Resume
// would then continue from a silently under-counted ledger. Write also never
// fsynced before the rename, so a crash could leave exactly such a prefix
// durably in place under the real checkpoint name.
//
// RED before the fix:
//
//	--- FAIL: TestReadCheckpointRejectsTruncated (0.00s)
//	    checkpoint_terminator_test.go:70: ReadCheckpoint accepted a checkpoint
//	        truncated to 207 of 363 bytes: got 2 tri entries of 8, silently
//	        under-counted

import (
	"fmt"
	"math/big"
	"os"
	"path/filepath"
	"strings"
	"testing"
)

// sampleCheckpoint writes a checkpoint with a full triangle and partial row.
func sampleCheckpoint(t *testing.T, path string) *Checkpoint {
	t.Helper()
	tri := newBigRow(9)
	hTri := newBigRow(9)
	for n := 1; n <= 8; n++ {
		tri[n].SetInt64(int64(1000000 + n))
		hTri[n].SetInt64(int64(n))
	}
	ck := &Checkpoint{
		H: 4, Col: 2, Frontier: []string{"/runs/f0.bin", "/runs/f1.bin"},
		Triangle: tri, HTri: hTri, Maxn: 8, Counter: "u64", Fold: true,
		Kernel: "kink", MaxDiagK: maxDiagKNoCap, MaxDiagKSet: true,
		Overlap: 1, OverlapSet: true,
	}
	if err := ck.Write(path); err != nil {
		t.Fatalf("write checkpoint: %v", err)
	}
	return ck
}

func countNonZero(row []*big.Int) int {
	n := 0
	for _, v := range row {
		if v != nil && v.Sign() != 0 {
			n++
		}
	}
	return n
}

func TestReadCheckpointRejectsTruncated(t *testing.T) {
	path := filepath.Join(t.TempDir(), "POLYCKPT")
	sampleCheckpoint(t, path)
	full, err := os.ReadFile(path)
	if err != nil {
		t.Fatalf("read back: %v", err)
	}
	// Cut in the middle of the tri lines.
	cut := len(full) * 4 / 7
	if err := os.WriteFile(path, full[:cut], 0o666); err != nil {
		t.Fatalf("truncate: %v", err)
	}
	got, err := ReadCheckpoint(path)
	if err == nil {
		t.Fatalf("ReadCheckpoint accepted a checkpoint truncated to %d of %d bytes: got %d tri entries of 8, silently under-counted", cut, len(full), countNonZero(got.Triangle))
	}
}

// TestReadCheckpointRoundTrip is the must-not-over-refuse direction: an intact
// checkpoint still reads back whole, terminator and all.
func TestReadCheckpointRoundTrip(t *testing.T) {
	path := filepath.Join(t.TempDir(), "POLYCKPT")
	want := sampleCheckpoint(t, path)
	got, err := ReadCheckpoint(path)
	if err != nil {
		t.Fatalf("ReadCheckpoint of an intact file: %v", err)
	}
	if got.Version != checkpointVersion || got.H != want.H || got.Col != want.Col {
		t.Errorf("header/state round-trip: version=%d H=%d col=%d, want %d/%d/%d", got.Version, got.H, got.Col, checkpointVersion, want.H, want.Col)
	}
	if n := countNonZero(got.Triangle); n != countNonZero(want.Triangle) {
		t.Errorf("tri entries = %d, want %d", n, countNonZero(want.Triangle))
	}
	if n := countNonZero(got.HTri); n != countNonZero(want.HTri) {
		t.Errorf("htri entries = %d, want %d", n, countNonZero(want.HTri))
	}
}

// TestReadCheckpointRejectsMalformedFields: a numeric field that does not
// parse is an error, not a silent zero (an unreadable H would resume height 0).
func TestReadCheckpointRejectsMalformedFields(t *testing.T) {
	path := filepath.Join(t.TempDir(), "POLYCKPT")
	sampleCheckpoint(t, path)
	full, err := os.ReadFile(path)
	if err != nil {
		t.Fatalf("read back: %v", err)
	}
	for _, c := range []struct{ old, new string }{
		{"\nH 4\n", "\nH four\n"},
		{"\ncol 2\n", "\ncol 2x\n"},
		{" maxn=8 ", " maxn=eight "},
		{" fold=true ", " fold=yes "},
		{" maxdiagk=-1 ", " maxdiagk=none "},
		{" overlap=1\n", " overlap=one\n"},
		{"\nfrontier ", "\ndone 3 x\nfrontier "},
	} {
		s := string(full)
		if !strings.Contains(s, c.old) {
			t.Fatalf("sample checkpoint has no %q", c.old)
		}
		if err := os.WriteFile(path, []byte(strings.Replace(s, c.old, c.new, 1)), 0o666); err != nil {
			t.Fatal(err)
		}
		if _, err := ReadCheckpoint(path); err == nil {
			t.Errorf("ReadCheckpoint accepted %q", strings.TrimSpace(c.new))
		}
	}
}

// TestReadCheckpointLongFrontier: the frontier line names every frontier
// file, so it can run well past bufio.Scanner's default 64 KB line limit.
func TestReadCheckpointLongFrontier(t *testing.T) {
	path := filepath.Join(t.TempDir(), "POLYCKPT")
	ck := sampleCheckpoint(t, path)
	ck.Frontier = nil
	for i := 0; i < 4000; i++ {
		ck.Frontier = append(ck.Frontier, fmt.Sprintf("/runs/a_long_run_directory_name/map_h20_c7_kstage3_u%05d.bin", i))
	}
	if err := ck.Write(path); err != nil {
		t.Fatal(err)
	}
	got, err := ReadCheckpoint(path)
	if err != nil {
		t.Fatalf("ReadCheckpoint with %d frontier files: %v", len(ck.Frontier), err)
	}
	if len(got.Frontier) != len(ck.Frontier) {
		t.Fatalf("frontier files = %d, want %d", len(got.Frontier), len(ck.Frontier))
	}
}
