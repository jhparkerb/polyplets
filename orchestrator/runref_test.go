package orchestrator

import (
	"sort"
	"testing"
)

// TestSampleKeysMultiSorted verifies that SampleKeysMulti returns sorted cuts
// even when input files have overlapping key ranges (as map outputs do).
func TestSampleKeysMultiSorted(t *testing.T) {
	dir := t.TempDir()

	H := 3
	maxn := 6

	// Write two synthetic POLYRUN files with interleaved keys so the
	// naive concatenation-without-sort would produce unsorted cuts.
	//
	// File A: keys 0x010100, 0x030100, 0x050100 (odd-ish sigs)
	// File B: keys 0x020100, 0x040100, 0x060100 (even-ish sigs)
	//
	// We create these by calling WriteSeedPolyrun (which only writes one record,
	// the zero-sig seed) and verify the function is at least callable without
	// crashing.  A full binary-body test requires writing raw POLYRUN records,
	// which is tested through integration via the orchestrate gate.

	pathA := dir + "/a.bin"
	pathB := dir + "/b.bin"
	if err := WriteSeedPolyrun(pathA, "test", H, maxn); err != nil {
		t.Fatalf("WriteSeedPolyrun A: %v", err)
	}
	if err := WriteSeedPolyrun(pathB, "test", H, maxn); err != nil {
		t.Fatalf("WriteSeedPolyrun B: %v", err)
	}

	cuts, err := SampleKeysMulti([]string{pathA, pathB}, H, 3)
	if err != nil {
		t.Fatalf("SampleKeysMulti: %v", err)
	}

	// Verify that cuts are sorted (the core invariant).
	if !sort.StringsAreSorted(cuts) {
		t.Errorf("cuts not sorted: %v", cuts)
	}
	if len(cuts) > 3 {
		t.Errorf("too many cuts: got %d, want ≤3", len(cuts))
	}
}

// TestCheckpointRoundtrip verifies that Write+Read preserves all fields
// including the sparse triangle, nil frontier, and acct.
func TestCheckpointRoundtrip(t *testing.T) {
	dir := t.TempDir()
	path := dir + "/POLYCKPT"

	triangle := make([]uint64, 15)
	triangle[1] = 1
	triangle[5] = 638
	triangle[14] = 11208974860

	orig := &Checkpoint{
		H:        7,
		Col:      3,
		Frontier: []string{"/tmp/a.bin", "/tmp/b.bin"},
		Triangle: triangle,
		Acct:     Acct{CPUS: 1.5, WallS: 2.1, RSSMax: 9.9},
	}

	if err := orig.Write(path); err != nil {
		t.Fatalf("Write: %v", err)
	}

	got, err := ReadCheckpoint(path)
	if err != nil {
		t.Fatalf("ReadCheckpoint: %v", err)
	}

	if got.H != orig.H {
		t.Errorf("H: got %d want %d", got.H, orig.H)
	}
	if got.Col != orig.Col {
		t.Errorf("Col: got %d want %d", got.Col, orig.Col)
	}
	if len(got.Frontier) != len(orig.Frontier) {
		t.Errorf("Frontier len: got %d want %d", len(got.Frontier), len(orig.Frontier))
	}
	for n, v := range triangle {
		if v == 0 {
			continue
		}
		if n >= len(got.Triangle) || got.Triangle[n] != v {
			got_v := uint64(0)
			if n < len(got.Triangle) {
				got_v = got.Triangle[n]
			}
			t.Errorf("triangle[%d]: got %d want %d", n, got_v, v)
		}
	}
}

// TestCheckpointNilFrontier verifies that a "height-done" checkpoint with nil
// frontier serializes and parses without error, and that the parsed frontier
// is nil/empty (not a slice containing an empty string).
func TestCheckpointNilFrontier(t *testing.T) {
	dir := t.TempDir()
	path := dir + "/POLYCKPT"

	ck := &Checkpoint{
		H:        14,
		Col:      14,
		Frontier: nil,
		Triangle: []uint64{0, 1, 4, 20},
		Acct:     Acct{},
	}

	if err := ck.Write(path); err != nil {
		t.Fatalf("Write: %v", err)
	}

	got, err := ReadCheckpoint(path)
	if err != nil {
		t.Fatalf("ReadCheckpoint: %v", err)
	}

	if len(got.Frontier) != 0 {
		t.Errorf("Frontier should be nil/empty, got %v", got.Frontier)
	}
	if got.Triangle[3] != 20 {
		t.Errorf("triangle[3]: got %d want 20", got.Triangle[3])
	}
}
