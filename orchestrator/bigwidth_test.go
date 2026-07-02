package orchestrator

// bigwidth_test.go — proves the Go-side result pipeline (BUGS-OF-SHAME A2)
// holds values exceeding 2^64-1 exactly, instead of the old uint64 path's
// silent drop (accounting.go's ParseUint(_,64) `if err == nil` skip) or
// silent wraparound (triangle[n] += v as uint64 addition). 3^45 alone
// already exceeds 2^64 (~1.8e19), well within reach of a26+.

import (
	"math/big"
	"os"
	"path/filepath"
	"testing"
)

// big45 = 3^45, comfortably past 2^64-1 (~1.8e19).
const big45Str = "92709463147897837085761925410587"

func mustBig(t *testing.T, s string) *big.Int {
	t.Helper()
	v, ok := new(big.Int).SetString(s, 10)
	if !ok {
		t.Fatalf("bad literal %q", s)
	}
	return v
}

// TestParseWorkerOutputWidth proves a "tri" line carrying a value past
// 2^64-1 parses to its exact big.Int value, and that a genuinely malformed
// value is a hard error rather than a silent skip.
func TestParseWorkerOutputWidth(t *testing.T) {
	want := mustBig(t, big45Str)
	r, err := ParseWorkerOutput([]string{"tri 16 27 " + big45Str})
	if err != nil {
		t.Fatalf("ParseWorkerOutput: %v", err)
	}
	got := r.TriContribs[16][27]
	if got == nil || got.Cmp(want) != 0 {
		t.Fatalf("TriContribs[16][27] = %v, want %s", got, want)
	}

	if _, err := ParseWorkerOutput([]string{"tri 16 27 not-a-number"}); err == nil {
		t.Fatalf("ParseWorkerOutput accepted a malformed tri value with no error (silent drop)")
	}
}

// TestTriContribsAccumulationWidth proves two contributions to the same
// (H,n) cell, each individually under 2^64 but summing past it, accumulate
// exactly — this is the fold path sweepHeight uses on real worker output.
func TestTriContribsAccumulationWidth(t *testing.T) {
	halfA := "50000000000000000000000000000000"
	halfB := "42709463147897837085761925410587"
	want := mustBig(t, big45Str)

	r, err := ParseWorkerOutput([]string{
		"tri 16 27 " + halfA,
		"tri 16 27 " + halfB,
	})
	if err != nil {
		t.Fatalf("ParseWorkerOutput: %v", err)
	}
	got := r.TriContribs[16][27]
	if got == nil || got.Cmp(want) != 0 {
		t.Fatalf("accumulated TriContribs[16][27] = %v, want %s", got, want)
	}

	// Now drive it through the same fold loop sweepHeight uses.
	hTri := newBigRow(30)
	for _, hm := range []map[int]map[int]*big.Int{r.TriContribs} {
		for _, nm := range hm {
			for n, v := range nm {
				hTri[n].Add(hTri[n], v)
			}
		}
	}
	if hTri[27].Cmp(want) != 0 {
		t.Fatalf("hTri[27] = %s, want %s (uint64 addition would have wrapped)", hTri[27], want)
	}
}

// TestWritePerHeightWidth proves a per-height row value past 2^64-1 is
// written and read back exactly, byte for byte — this is the file every
// Pk-derivation script (scripts/derive_p9.py etc.) treats as ground truth.
func TestWritePerHeightWidth(t *testing.T) {
	dir := t.TempDir()
	want := mustBig(t, big45Str)
	row := newBigRow(3)
	row[2] = want
	if err := writePerHeight(dir, 5, 2, row); err != nil {
		t.Fatalf("writePerHeight: %v", err)
	}
	data, err := os.ReadFile(filepath.Join(dir, "h5.out"))
	if err != nil {
		t.Fatalf("read back: %v", err)
	}
	wantLine := "2 " + big45Str + "\n"
	if got := string(data); got != "1 0\n"+wantLine {
		t.Fatalf("h5.out = %q, want %q", got, "1 0\n"+wantLine)
	}
}

// TestCheckpointRoundTripWidth proves a triangle value past 2^64-1
// round-trips exactly through Write/ReadCheckpoint, and that a corrupted
// tri line is a hard read error rather than a silently-dropped row.
func TestCheckpointRoundTripWidth(t *testing.T) {
	dir := t.TempDir()
	path := filepath.Join(dir, "POLYCKPT")
	want := mustBig(t, big45Str)

	tri := newBigRow(28)
	tri[27] = want
	ck := &Checkpoint{H: 16, Col: 5, Triangle: tri}
	if err := ck.Write(path); err != nil {
		t.Fatalf("Write: %v", err)
	}
	got, err := ReadCheckpoint(path)
	if err != nil {
		t.Fatalf("ReadCheckpoint: %v", err)
	}
	if got.Triangle[27] == nil || got.Triangle[27].Cmp(want) != 0 {
		t.Fatalf("round-tripped triangle[27] = %v, want %s", got.Triangle[27], want)
	}

	// A corrupted tri line must hard-fail the read, not silently drop the row.
	corrupt := filepath.Join(dir, "POLYCKPT_BAD")
	if err := os.WriteFile(corrupt, []byte("POLYCKPT 1\nH 1\ncol 0\nconfig maxn=2 counter=u64 fold=true\nfrontier \nacct cpu_s=0.0 wall_s=0.0 rss_max_mb=0.0\ntri 1 not-a-number\n"), 0o644); err != nil {
		t.Fatalf("write corrupt checkpoint: %v", err)
	}
	if _, err := ReadCheckpoint(corrupt); err == nil {
		t.Fatalf("ReadCheckpoint accepted a malformed tri line with no error (silent drop)")
	}
}
