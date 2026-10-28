package verify

import (
	"encoding/binary"
	"fmt"
	"os"
	"path/filepath"
	"strings"
	"testing"
)

// writePolyrun writes a minimal valid POLYRUN file (one record) with a
// correct FNV-1a-64 body CRC trailer.
func writePolyrun(t *testing.T, path string) {
	t.Helper()
	const H = 3
	keyLen := H + 2
	// body = sig[keyLen] + lo(1) + len(1) + one LEB128 varint count (1)
	body := make([]byte, keyLen+2+1)
	body[keyLen] = 0   // lo
	body[keyLen+1] = 1 // len
	body[keyLen+2] = 1 // counts[0] = 1

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

// TestVerifyCRCDetectsCorruptBody locks in the corruption backstop: the
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

// A compressed POLYRUN body (compression 1/2) has no FNV trailer and its
// records are not raw bytes: both body readers must fail with a clear
// compression error, never misread zstd bytes as records/CRC.
func TestCompressedBodyFailsClosed(t *testing.T) {
	dir := t.TempDir()
	path := dir + "/comp.bin"
	f, err := os.Create(path)
	if err != nil {
		t.Fatal(err)
	}
	fmt.Fprintf(f, "POLYRUN 2\nheight 3\nmaxn 8\ncounter u64\nclassifier triangle\nkeylo \nkeyhi \nrecords %018d\nrev test\nbyteorder 1\ncompression 2\n\n", 64)
	f.Write(make([]byte, 1024))
	f.Close()
	if _, _, err := SumCountsInFile(path); err == nil || !strings.Contains(err.Error(), "compress") {
		t.Fatalf("SumCountsInFile on compressed body: want compression error, got %v", err)
	}
}

// TestValuesPastU64AreExact: a(26) and beyond exceed 2^64. The triangle file,
// the manifest value and the varint counts must be read exactly, and a value
// that does not parse must be an error, not a skipped line (a skipped tri
// line drops its n from the row-sum check, which then passes unchecked).
func TestValuesPastU64AreExact(t *testing.T) {
	dir := t.TempDir()
	const big26 = "102607513847014153892" // a(26), past 2^64
	tri := filepath.Join(dir, "tri.txt")
	if err := os.WriteFile(tri, []byte("tri 5 26 "+big26+"\ntri 6 26 1\n"), 0o644); err != nil {
		t.Fatal(err)
	}
	sums, err := ReadTriangleFile(tri)
	if err != nil {
		t.Fatalf("ReadTriangleFile: %v", err)
	}
	if got := sums[26].String(); got != "102607513847014153893" {
		t.Fatalf("triangle sum for n=26 = %s, want 102607513847014153893", got)
	}
	if err := os.WriteFile(tri, []byte("tri 5 26 12x\n"), 0o644); err != nil {
		t.Fatal(err)
	}
	if _, err := ReadTriangleFile(tri); err == nil {
		t.Fatalf("a malformed tri line was skipped instead of refused")
	}

	man := filepath.Join(dir, "man.txt")
	if err := os.WriteFile(man, []byte("n=26\nvalue="+big26+"\n"), 0o644); err != nil {
		t.Fatal(err)
	}
	m, err := ParseManifest(man)
	if err != nil || m.Value == nil || m.Value.String() != big26 {
		t.Fatalf("manifest value = %v (err %v), want %s", m.Value, err, big26)
	}

	// 2^70 + 5 as a varint: past u64, so binary.ReadUvarint would refuse it.
	v, err := readBigUvarint(strings.NewReader("\x85\x80\x80\x80\x80\x80\x80\x80\x80\x80\x01"))
	if err != nil || v.String() != "1180591620717411303429" {
		t.Fatalf("readBigUvarint = %v (err %v), want 2^70+5 = 1180591620717411303429", v, err)
	}
}
