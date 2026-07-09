package orchestrator

import (
	"encoding/binary"
	"fmt"
	"math/big"
	"os"
	"sort"
	"testing"
)

// writeTestIdx writes a raw .idx sidecar at path+".idx" matching the on-disk
// format in core/runfile.h (header: magic4+ver2+bo1+keyLen4+count8, then
// count entries of keyLen key bytes + 8 offset + 8 recidx), with one entry
// per kIndexStride(=64) records, exactly like the real writer. keyFn maps a
// record index [0,records) to its keyLen-byte key. Offset/recidx values are
// synthetic (only the key bytes matter to BalancedCutsMulti).
func writeTestIdx(t *testing.T, path string, keyLen, records int, keyFn func(i int) []byte) {
	t.Helper()
	const stride = 64
	f, err := os.Create(path + ".idx")
	if err != nil {
		t.Fatalf("create idx: %v", err)
	}
	defer f.Close()

	var count uint64
	for i := 0; i < records; i += stride {
		count++
	}

	hdr := make([]byte, idxHeaderBytes)
	binary.LittleEndian.PutUint32(hdr[0:4], idxMagic)
	binary.LittleEndian.PutUint16(hdr[4:6], idxVersion)
	hdr[6] = idxByteOrderLE
	binary.LittleEndian.PutUint32(hdr[7:11], uint32(keyLen))
	binary.LittleEndian.PutUint64(hdr[11:19], count)
	if _, err := f.Write(hdr); err != nil {
		t.Fatalf("write idx header: %v", err)
	}

	entry := make([]byte, keyLen+16)
	for i := 0; i < records; i += stride {
		key := keyFn(i)
		if len(key) != keyLen {
			t.Fatalf("keyFn returned %d bytes, want %d", len(key), keyLen)
		}
		copy(entry, key)
		binary.LittleEndian.PutUint64(entry[keyLen:keyLen+8], uint64(i)*32) // fake offset
		binary.LittleEndian.PutUint64(entry[keyLen+8:], uint64(i))          // recidx
		if _, err := f.Write(entry); err != nil {
			t.Fatalf("write idx entry: %v", err)
		}
	}
}

// writeTestRunHeader writes a minimal POLYRUN text header (no body/CRC) at
// path, sufficient for ParseHeader + the .idx fast path (sampleIndexKeys
// never touches the body). H must match the H passed to SampleKeys*.
func writeTestRunHeader(t *testing.T, path string, H, records int) {
	t.Helper()
	f, err := os.Create(path)
	if err != nil {
		t.Fatalf("create run header: %v", err)
	}
	defer f.Close()
	fmt.Fprintf(f, "POLYRUN 1\n")
	fmt.Fprintf(f, "height %d\n", H)
	fmt.Fprintf(f, "maxn 0\n")
	fmt.Fprintf(f, "counter u64\n")
	fmt.Fprintf(f, "classifier triangle\n")
	fmt.Fprintf(f, "keylo \n")
	fmt.Fprintf(f, "keyhi \n")
	fmt.Fprintf(f, "records %018d\n", records)
	fmt.Fprintf(f, "rev test\n")
	fmt.Fprintf(f, "byteorder 1\n")
	fmt.Fprintf(f, "\n")
}

// bucketOf returns the index of the half-open bucket [cuts[i-1], cuts[i])
// (cutsToBounds' convention, sweep.go) that hex key k falls into.
func bucketOf(cuts []string, k string) int {
	return sort.Search(len(cuts), func(j int) bool { return cuts[j] > k })
}

// TestBalancedCutsRecordEqual is the regression test for the root cause an
// earlier per-file sampler had: it drew numCuts keys PER FILE, so a big file
// (many records) was under-sampled relative to a small file and its records
// collapsed into one bucket. BalancedCutsMulti instead cuts on true global
// record-quantiles: every bucket within ±10% of total/numBuckets, even on a
// heavily skewed file-size mix.
func TestBalancedCutsRecordEqual(t *testing.T) {
	dir := t.TempDir()
	const keyLen = 2
	// A:B record ratio is 1:9 (10%/90% of total) with both files holding many
	// more .idx entries than numCuts -- the skew a per-file-fixed-count sampler
	// mishandled ("a file holding 590M records gets the SAME numCuts samples as
	// one holding 64K"). BalancedCutsMulti must balance it regardless.
	const recsA = 6_400   // small file: 100 idx entries
	const recsB = 57_600  // fat file: 900 idx entries -- the straggler
	total := recsA + recsB
	const numCuts = 9 // -> 10 buckets

	// File A: keys spread over [0x0000, 0x1fff]. File B: keys spread over
	// [0x2000, 0xffff]. Disjoint, monotonically increasing -- mirrors a
	// realistic merge-input key partition.
	keyFnA := func(i int) []byte {
		v := uint16(i * 0x1fff / (recsA - 1))
		return []byte{byte(v >> 8), byte(v)}
	}
	keyFnB := func(i int) []byte {
		v := uint16(0x2000 + i*(0xffff-0x2000)/(recsB-1))
		return []byte{byte(v >> 8), byte(v)}
	}

	const H = 5
	pathA := dir + "/a.bin"
	pathB := dir + "/b.bin"
	writeTestRunHeader(t, pathA, H, recsA)
	writeTestRunHeader(t, pathB, H, recsB)
	writeTestIdx(t, pathA, keyLen, recsA, keyFnA)
	writeTestIdx(t, pathB, keyLen, recsB, keyFnB)

	// Full per-record key list, used to count records per bucket regardless
	// of which sampler produced the cuts.
	var allKeys []string
	for i := 0; i < recsA; i++ {
		allKeys = append(allKeys, bytesToHex(keyFnA(i)))
	}
	for i := 0; i < recsB; i++ {
		allKeys = append(allKeys, bytesToHex(keyFnB(i)))
	}

	checkBalanced := func(t *testing.T, cuts []string) (ok bool, counts []int) {
		counts = make([]int, len(cuts)+1)
		for _, k := range allKeys {
			counts[bucketOf(cuts, k)]++
		}
		want := float64(total) / float64(len(counts))
		ok = true
		for _, c := range counts {
			if float64(c) < 0.9*want || float64(c) > 1.1*want {
				ok = false
			}
		}
		return ok, counts
	}

	cuts, err := BalancedCutsMulti([]string{pathA, pathB}, keyLen, numCuts)
	if err != nil {
		t.Fatalf("BalancedCutsMulti: %v", err)
	}
	if !sort.StringsAreSorted(cuts) {
		t.Errorf("cuts not sorted: %v", cuts)
	}
	ok, counts := checkBalanced(t, cuts)
	if !ok {
		t.Errorf("buckets not balanced within ±10%% of %d: counts=%v cuts=%v", total/len(counts), counts, cuts)
	}
}

// TestBalancedCutsSorted extends TestSampleKeysMultiSorted's invariant to
// BalancedCutsMulti: cuts must be strictly ascending even when files'
// key ranges interleave/overlap (as map outputs do).
func TestBalancedCutsSorted(t *testing.T) {
	dir := t.TempDir()
	const keyLen = 1

	pathA := dir + "/a.bin"
	pathB := dir + "/b.bin"
	// Interleaved: A has odd-ish keys, B has even-ish keys.
	writeTestIdx(t, pathA, keyLen, 200, func(i int) []byte { return []byte{byte(2 * (i / 64))} })
	writeTestIdx(t, pathB, keyLen, 200, func(i int) []byte { return []byte{byte(2*(i/64) + 1)} })

	cuts, err := BalancedCutsMulti([]string{pathA, pathB}, keyLen, 3)
	if err != nil {
		t.Fatalf("BalancedCutsMulti: %v", err)
	}
	if !sort.StringsAreSorted(cuts) {
		t.Errorf("cuts not sorted: %v", cuts)
	}
	for i := 1; i < len(cuts); i++ {
		if cuts[i] == cuts[i-1] {
			t.Errorf("cuts not strictly ascending (duplicate) at %d: %v", i, cuts)
		}
	}
}

// TestBalancedCutsDegenerate covers the degenerate-input contracts, which
// must match SampleKeysMulti's: numCuts<=0 -> (nil,nil); a file with only
// the entry-0 index contributes nothing; a missing index falls back to
// SampleKeys (which itself returns (nil,nil) for a missing/unreadable run
// file, so the union is empty -> (nil,nil)); empty paths -> (nil,nil).
func TestBalancedCutsDegenerate(t *testing.T) {
	dir := t.TempDir()
	const keyLen = 2

	t.Run("empty_paths", func(t *testing.T) {
		cuts, err := BalancedCutsMulti(nil, keyLen, 5)
		if err != nil || cuts != nil {
			t.Errorf("got (%v, %v), want (nil, nil)", cuts, err)
		}
	})

	t.Run("numCuts_zero", func(t *testing.T) {
		path := dir + "/tiny.bin"
		writeTestIdx(t, path, keyLen, 1, func(i int) []byte { return []byte{0, 0} })
		cuts, err := BalancedCutsMulti([]string{path}, keyLen, 0)
		if err != nil || cuts != nil {
			t.Errorf("numCuts=0: got (%v, %v), want (nil, nil)", cuts, err)
		}
	})

	t.Run("single_tiny_file_only_entry_zero", func(t *testing.T) {
		// records=1 -> exactly one index entry (record 0), which is dropped
		// as the run minimum -> no interior keys -> (nil, nil).
		path := dir + "/onerecord.bin"
		writeTestIdx(t, path, keyLen, 1, func(i int) []byte { return []byte{0x12, 0x34} })
		cuts, err := BalancedCutsMulti([]string{path}, keyLen, 5)
		if err != nil {
			t.Fatalf("BalancedCutsMulti: %v", err)
		}
		if len(cuts) != 0 {
			t.Errorf("expected no interior cuts from a single-entry index, got %v", cuts)
		}
	})

	t.Run("missing_index_falls_back_to_SampleKeys", func(t *testing.T) {
		// A path with no .idx at all and no run body either: SampleKeys
		// returns an error from ParseHeader (file doesn't exist), so this
		// file contributes nothing -- same tolerance as SplitRangeByIndex.
		cuts, err := BalancedCutsMulti([]string{dir + "/does-not-exist.bin"}, keyLen, 5)
		if err != nil {
			t.Fatalf("BalancedCutsMulti: %v", err)
		}
		if cuts != nil {
			t.Errorf("expected nil cuts for a wholly-missing file, got %v", cuts)
		}
	})
}

// TestCheckpointRoundtrip verifies that Write+Read preserves all fields
// including the sparse triangle, nil frontier, and acct.
func TestCheckpointRoundtrip(t *testing.T) {
	dir := t.TempDir()
	path := dir + "/POLYCKPT"

	triangle := make([]*big.Int, 15)
	for i := range triangle {
		triangle[i] = new(big.Int)
	}
	triangle[1].SetInt64(1)
	triangle[5].SetInt64(638)
	triangle[14].SetInt64(11208974860)

	orig := &Checkpoint{
		H:        7,
		Col:      3,
		Frontier: []string{"/tmp/a.bin", "/tmp/b.bin"},
		Triangle: triangle,
		Acct:     Acct{CPUS: 1.5, WallS: 2.1, RSSMax: 9.9},
		Maxn:     20,
		Counter:  "u128",
		Fold:     true,
		Kernel:   "kink",
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
	if got.Maxn != orig.Maxn || got.Counter != orig.Counter || got.Fold != orig.Fold || got.Kernel != orig.Kernel {
		t.Errorf("config: got maxn=%d counter=%s fold=%v kernel=%s; want maxn=%d counter=%s fold=%v kernel=%s",
			got.Maxn, got.Counter, got.Fold, got.Kernel, orig.Maxn, orig.Counter, orig.Fold, orig.Kernel)
	}
	for n, v := range triangle {
		if v.Sign() == 0 {
			continue
		}
		if n >= len(got.Triangle) || got.Triangle[n] == nil || got.Triangle[n].Cmp(v) != 0 {
			got_v := big.NewInt(0)
			if n < len(got.Triangle) && got.Triangle[n] != nil {
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
		Triangle: []*big.Int{big.NewInt(0), big.NewInt(1), big.NewInt(4), big.NewInt(20)},
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
	if got.Triangle[3].Cmp(big.NewInt(20)) != 0 {
		t.Errorf("triangle[3]: got %d want 20", got.Triangle[3])
	}
}
