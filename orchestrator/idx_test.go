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
	got, err := indexKeysInRange(idxPath, keyLen, lo, true, hi, true, 10)
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

// TestIndexKeysInRangeBinarySearch — correctness guard for the Steal Sort fix:
// the binary-search + stride must return only valid in-range, ascending keys.
// (Cuts become steal-child range boundaries, so a wrong cut would miscount.)
func TestIndexKeysInRangeBinarySearch(t *testing.T) {
	dir := t.TempDir()
	H := 3
	keyLen := H + 2 // 5
	var keys [][]byte
	for v := 1; v <= 20; v++ {
		keys = append(keys, []byte{0, 0, 0, 0, byte(v * 10)}) // 10,20,...,200 ascending
	}
	idxPath := dir + "/run.bin.idx"
	writeCppIdx(t, idxPath, keyLen, keys)

	lo, _ := hexBytes("0000000037", keyLen) // 0x37 = 55
	hi, _ := hexBytes("000000009b", keyLen) // 0x9b = 155
	got, err := indexKeysInRange(idxPath, keyLen, lo, true, hi, true, 4)
	if err != nil {
		t.Fatalf("indexKeysInRange: %v", err)
	}
	if len(got) == 0 || len(got) > 4 {
		t.Fatalf("got %d keys, want 1..4: %v", len(got), got)
	}
	for i, h := range got {
		b, _ := hexBytes(h, keyLen)
		v := int(b[4])
		if v <= 55 || v >= 155 { // strictly inside (lo, hi)
			t.Errorf("key %s (v=%d) out of range (55,155)", h, v)
		}
		if v%10 != 0 { // must be one of the real index keys
			t.Errorf("key %s (v=%d) is not a real index key", h, v)
		}
		if i > 0 {
			pb, _ := hexBytes(got[i-1], keyLen)
			if int(pb[4]) >= v {
				t.Errorf("keys not strictly ascending: %v", got)
			}
		}
	}
	// empty range → no keys.
	loE, _ := hexBytes("0000000045", keyLen) // 69
	hiE, _ := hexBytes("0000000046", keyLen) // 70 (exclusive) → nothing in (69,70)
	if e, _ := indexKeysInRange(idxPath, keyLen, loE, true, hiE, true, 4); len(e) != 0 {
		t.Errorf("empty range returned %v", e)
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

	cuts, err := SampleKeys(path, H, keyLen, 3)
	if err != nil {
		t.Fatalf("SampleKeys: %v", err)
	}
	if len(cuts) == 0 {
		t.Fatalf("SampleKeys returned no cuts — it scanned the (absent) body instead of the .idx (Body Crawl)")
	}
	if !sort.StringsAreSorted(cuts) {
		t.Errorf("cuts not sorted: %v", cuts)
	}
}

// TestSampleKeysExplicitKeyLen — RED before de-hardcoding SampleKeys off an
// internal H+2 assumption (Design 14 Phase 2, step 2.1). SampleKeys must use
// the caller-supplied keyLen, not silently re-derive H+2, so it works on the
// kink kernel's H+4-keyed mixed-state stage tables. Builds a run+idx pair at
// keyLen=H+4 (kink's width) and asserts SampleKeys reads it correctly; before
// the fix this failed with "idx keyLen 9 != 7" (SampleKeys passing the wrong,
// internally-derived keyLen into sampleIndexKeys/readIndexHeader).
func TestSampleKeysExplicitKeyLen(t *testing.T) {
	dir := t.TempDir()
	H := 5
	keyLen := kinkKeyLen(H) // H+4 = 9, distinct from the column kernel's H+2 = 7
	path := dir + "/stage.bin"
	writeHeaderOnly(t, path, H, 10, 1000)

	var keys [][]byte
	idxSet := map[string]bool{}
	for v := byte(1); v <= 8; v++ {
		k := make([]byte, keyLen)
		k[keyLen-1] = v
		keys = append(keys, k)
		idxSet[bytesToHex(k)] = true
	}
	writeCppIdx(t, path+".idx", keyLen, keys)

	cuts, err := SampleKeys(path, H, keyLen, 3)
	if err != nil {
		t.Fatalf("SampleKeys at keyLen=%d: %v", keyLen, err)
	}
	if len(cuts) == 0 {
		t.Fatalf("SampleKeys returned no cuts at keyLen=%d", keyLen)
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
