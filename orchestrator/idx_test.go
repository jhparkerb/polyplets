package orchestrator

import (
	"bytes"
	"encoding/binary"
	"fmt"
	"os"
	"sort"
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

// writeHeaderOnly writes a POLYRUN with a valid text header claiming `records`
// records but NO binary body — so a code path that scans the body finds nothing,
// while one that reads the .idx still works.
func writeHeaderOnly(t *testing.T, path string, H, maxn, records int) {
	t.Helper()
	var b bytes.Buffer
	fmt.Fprintf(&b, "POLYRUN 1\nheight %d\nmaxn %d\ncounter u64\nclassifier triangle\n", H, maxn)
	fmt.Fprintf(&b, "keylo \nkeyhi \nrecords %018d\nrev test\nbyteorder 1\n\n", records)
	if err := os.WriteFile(path, b.Bytes(), 0o644); err != nil {
		t.Fatalf("write header: %v", err)
	}
}

// TestSampleKeysUsesIndexNotBody — RED before the Body Crawl fix.
// SampleKeys must sample from the .idx sidecar, not scan the multi-GB body.
// The run has a header claiming 1000 records but NO body, and a complete .idx;
// the body-scanning code returns zero cuts, the .idx code returns real cuts.
func TestSampleKeysUsesIndexNotBody(t *testing.T) {
	dir := t.TempDir()
	H := 3
	keyLen := H + 2
	path := dir + "/run.bin"
	writeHeaderOnly(t, path, H, 6, 1000) // claims 1000 records, writes NO body

	var keys [][]byte
	idxSet := map[string]bool{}
	for v := byte(1); v <= 8; v++ {
		k := []byte{0, 0, 0, 0, v}
		keys = append(keys, k)
		idxSet[bytesToHex(k)] = true
	}
	writeCppIdx(t, path+".idx", keyLen, keys)

	cuts, err := SampleKeys(path, H, 3)
	if err != nil {
		t.Fatalf("SampleKeys: %v", err)
	}
	if len(cuts) == 0 {
		t.Fatalf("SampleKeys returned no cuts — it scanned the (absent) body instead of the .idx (Body Crawl)")
	}
	if !sort.StringsAreSorted(cuts) {
		t.Errorf("cuts not sorted: %v", cuts)
	}
	for _, c := range cuts {
		if !idxSet[c] {
			t.Errorf("cut %s is not one of the .idx keys", c)
		}
	}
}
