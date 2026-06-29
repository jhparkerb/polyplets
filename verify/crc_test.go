package verify

import (
	"encoding/binary"
	"os"
	"path/filepath"
	"testing"
)

// writePolyrun writes a minimal valid POLYRUN file (one u64 record) with a
// correct FNV-1a-64 body CRC trailer, and returns its body offset.
func writePolyrun(t *testing.T, path string) {
	t.Helper()
	const H = 3
	keyLen := H + 2
	// body = sig[keyLen] + lo(1) + len(1) + counts(1 * 8 bytes LE)
	body := make([]byte, keyLen+2+8)
	body[keyLen] = 0             // lo
	body[keyLen+1] = 1           // len
	binary.LittleEndian.PutUint64(body[keyLen+2:], 1)

	var buf []byte
	buf = append(buf, []byte("POLYRUN 1\n")...)
	buf = append(buf, []byte("height 3\n")...)
	buf = append(buf, []byte("maxn 8\n")...)
	buf = append(buf, []byte("counter u64\n")...)
	buf = append(buf, []byte("classifier triangle\n")...)
	buf = append(buf, []byte("keylo \n")...)
	buf = append(buf, []byte("keyhi \n")...)
	buf = append(buf, []byte("records 000000000000000001\n")...)
	buf = append(buf, []byte("rev test\n")...)
	buf = append(buf, []byte("byteorder 1\n")...)
	buf = append(buf, '\n')
	buf = append(buf, body...)
	crc := make([]byte, 8)
	binary.LittleEndian.PutUint64(crc, fnv1a64(body))
	buf = append(buf, crc...)

	if err := os.WriteFile(path, buf, 0o644); err != nil {
		t.Fatal(err)
	}
}

// TestVerifyCRCDetectsCorruptBody locks in the B3 corruption backstop: the
// verify tool's independent full-body CRC pass must accept an intact run file
// and reject one with a flipped body byte. This is the out-of-band check that
// covers seeked production reads (which skip the body CRC by design).
func TestVerifyCRCDetectsCorruptBody(t *testing.T) {
	path := filepath.Join(t.TempDir(), "h3.bin")
	writePolyrun(t, path)

	_, bodyOff, err := parsePolyrunHeader(path)
	if err != nil {
		t.Fatal(err)
	}
	check := func(wantMatch bool) {
		computed, err := ComputeBodyCRC(path, bodyOff)
		if err != nil {
			t.Fatal(err)
		}
		stored, err := StoredCRC(path)
		if err != nil {
			t.Fatal(err)
		}
		if (computed == stored) != wantMatch {
			t.Fatalf("CRC match=%v, want %v (computed=%016x stored=%016x)", computed == stored, wantMatch, computed, stored)
		}
	}
	check(true) // intact file verifies

	// Flip one body byte; the backstop must now report a mismatch.
	data, err := os.ReadFile(path)
	if err != nil {
		t.Fatal(err)
	}
	data[bodyOff] ^= 0xFF
	if err := os.WriteFile(path, data, 0o644); err != nil {
		t.Fatal(err)
	}
	check(false) // corruption detected
}
