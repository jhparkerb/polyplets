package orchestrator

// sample_body_test.go — regression pin for the varint-migration miss in
// sampleBodyKeys (AUDIT-2026-07-13). The run body encodes counts as LEB128
// varint, but sampleBodyKeys skipped each record's counts as a fixed
// length*wordBytes (the pre-varint layout). After the first record the byte
// stream desynced and every sampled key was read from mid-record.
//
// RED before the fix: with the fixed-width skip, the returned keys do not match
// the strided record sigs (garbage / early truncation).

import (
	"encoding/binary"
	"os"
	"path/filepath"
	"testing"
)

func TestSampleBodyKeysVarintAligned(t *testing.T) {
	const keyLen = 3
	const records = 8
	const numCuts = 2

	var body []byte
	var tmp [binary.MaxVarintLen64]byte
	for r := 0; r < records; r++ {
		sig := []byte{byte(r + 1), 0, 0} // distinct, ascending
		body = append(body, sig...)
		// meta: lo, length. Two counts, each a variable-width varint (1-3 bytes) —
		// deliberately NOT 8 bytes, so a fixed length*8 skip desyncs immediately.
		body = append(body, 1, 2)
		for _, v := range []uint64{uint64(r + 1), uint64(1000 + r)} {
			n := binary.PutUvarint(tmp[:], v)
			body = append(body, tmp[:n]...)
		}
	}

	path := filepath.Join(t.TempDir(), "body.run")
	if err := os.WriteFile(path, body, 0o600); err != nil {
		t.Fatalf("write body: %v", err)
	}

	got, err := sampleBodyKeys(path, 0, keyLen, records, numCuts)
	if err != nil {
		t.Fatalf("sampleBodyKeys: %v", err)
	}

	// stride = records/(numCuts+1) = 8/3 = 2; cuts at 1-based idx 2 and 4 -> the
	// 2nd and 4th records (r=1, r=3).
	want := []string{
		bytesToHex([]byte{2, 0, 0}),
		bytesToHex([]byte{4, 0, 0}),
	}
	if len(got) != len(want) {
		t.Fatalf("got %d cuts %v, want %d %v", len(got), got, len(want), want)
	}
	for i := range want {
		if got[i] != want[i] {
			t.Fatalf("cut %d: got %q, want %q (full got=%v)", i, got[i], want[i], got)
		}
	}
}
