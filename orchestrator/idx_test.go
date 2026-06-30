package orchestrator

import (
	"bytes"
	"encoding/binary"
	"os"
	"testing"
)

// writeCppIdx writes a .idx sidecar in the EXACT format core/runfile.h emits:
// magic(u32 'PLYI') + ver(u16) + bo(u8) + keyLen(u32) + count(u64) then
// count × { key[keyLen] u64 offset u64 recidx }, all little-endian.
func writeCppIdx(t *testing.T, path string, keyLen int, keys [][]byte) {
	t.Helper()
	var buf bytes.Buffer
	binary.Write(&buf, binary.LittleEndian, uint32(0x49594C50)) // kRunIndexMagic 'PLYI'
	binary.Write(&buf, binary.LittleEndian, uint16(1))          // kRunIndexVersion
	buf.WriteByte(1)                                            // kRunByteOrderLE
	binary.Write(&buf, binary.LittleEndian, uint32(keyLen))
	binary.Write(&buf, binary.LittleEndian, uint64(len(keys)))
	for i, k := range keys {
		if len(k) != keyLen {
			t.Fatalf("key %d len %d != keyLen %d", i, len(k), keyLen)
		}
		buf.Write(k)
		binary.Write(&buf, binary.LittleEndian, uint64(i*100)) // offset (arbitrary)
		binary.Write(&buf, binary.LittleEndian, uint64(i*64))  // recidx
	}
	if err := os.WriteFile(path, buf.Bytes(), 0o644); err != nil {
		t.Fatalf("write idx: %v", err)
	}
}

// TestIdxReaderSkipsCppMagicHeader — RED before the Magic Misread fix.
// The Go .idx reader (indexKeysInRange) must skip the C++ magic+ver+bo prefix.
// Unfixed, it reads the 4-byte magic 'PLYI' as keyLen → "idx keyLen mismatch".
func TestIdxReaderSkipsCppMagicHeader(t *testing.T) {
	dir := t.TempDir()
	H := 3
	keyLen := H + 2 // 5
	keys := [][]byte{
		{0, 0, 0, 0, 1},
		{0, 0, 0, 0, 3},
		{0, 0, 0, 0, 5},
	}
	idxPath := dir + "/run.bin.idx"
	writeCppIdx(t, idxPath, keyLen, keys)

	lo, okLo := hexBytes("0000000002", keyLen)
	hi, okHi := hexBytes("0000000006", keyLen)
	if !okLo || !okHi {
		t.Fatal("hexBytes setup failed")
	}
	got, err := indexKeysInRange(idxPath, keyLen, lo, true, hi, true)
	if err != nil {
		t.Fatalf("indexKeysInRange errored on a valid C++ .idx (Magic Misread): %v", err)
	}
	want := []string{"0000000003", "0000000005"}
	if len(got) != len(want) {
		t.Fatalf("got %v, want %v", got, want)
	}
	for i := range want {
		if got[i] != want[i] {
			t.Fatalf("key %d: got %s want %s", i, got[i], want[i])
		}
	}
}
