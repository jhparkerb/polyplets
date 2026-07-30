package orchestrator

// checkpoint_terminator_test.go — red-first regression for AUDIT-2026-07-30
// O7 ("Truncated Ledger"). ReadCheckpoint accepted any PREFIX of a checkpoint:
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
	"math/big"
	"os"
	"path/filepath"
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
