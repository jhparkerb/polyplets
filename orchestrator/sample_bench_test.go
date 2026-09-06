package orchestrator

import (
	"os"
	"testing"
)

// BenchmarkSampleIndexKeys measures the hot allocation path SampleKeysMulti
// exercises on every map/merge round of every column of every height
// (docs/engine-record.md Bottleneck #4). A real dalby A/B for
// an allocation-only question is a ~5min round trip; this gives the same
// signal (via -benchmem) in milliseconds, locally, no dalby needed. Use this
// for iterating on this hot path; reserve real dalby runs for confirming a
// promising local result at production scale/concurrency.
func BenchmarkSampleIndexKeys(b *testing.B) {
	dir := b.TempDir()
	keyLen := 20 // realistic kink stage width, H~16-18
	const nKeys = 6400 // realistic per-column .idx size (one entry/64 records)
	keys := make([][]byte, nKeys)
	for i := range keys {
		k := make([]byte, keyLen)
		k[0] = byte(i >> 16)
		k[1] = byte(i >> 8)
		k[2] = byte(i)
		keys[i] = k
	}
	idxPath := dir + "/run.bin.idx"
	writeCppIdxBench(b, idxPath, keyLen, keys)

	b.ResetTimer()
	b.ReportAllocs()
	for i := 0; i < b.N; i++ {
		if _, err := sampleIndexKeys(idxPath, keyLen, 320); err != nil {
			b.Fatalf("sampleIndexKeys: %v", err)
		}
	}
}

// BenchmarkParseHeader measures ParseHeader's text-header scan (called once
// per SampleKeys call, i.e. once per file per map/merge round).
func BenchmarkParseHeader(b *testing.B) {
	dir := b.TempDir()
	path := dir + "/run.bin"
	if err := WriteSeedPolyrun(path, "bench", 16, 30); err != nil {
		b.Fatalf("WriteSeedPolyrun: %v", err)
	}
	b.ResetTimer()
	b.ReportAllocs()
	for i := 0; i < b.N; i++ {
		if _, _, err := ParseHeader(path); err != nil {
			b.Fatalf("ParseHeader: %v", err)
		}
	}
}

// writeCppIdxBench is writeCppIdx (idx_test.go) without requiring *testing.T
// (benchmarks use *testing.B) -- same on-disk format core/runfile.h emits.
func writeCppIdxBench(b *testing.B, path string, keyLen int, keys [][]byte) {
	b.Helper()
	f, err := os.Create(path)
	if err != nil {
		b.Fatalf("create idx: %v", err)
	}
	defer f.Close()
	hdr := make([]byte, 0, idxHeaderBytes)
	hdr = appendU32(hdr, 0x49594C50)
	hdr = appendU16(hdr, 1)
	hdr = append(hdr, 1)
	hdr = appendU32(hdr, uint32(keyLen))
	hdr = appendU64(hdr, uint64(len(keys)))
	if _, err := f.Write(hdr); err != nil {
		b.Fatalf("write idx header: %v", err)
	}
	entry := make([]byte, keyLen+16)
	for i, k := range keys {
		copy(entry, k)
		appendU64At(entry[keyLen:], uint64(i*100))
		appendU64At(entry[keyLen+8:], uint64(i*64))
		if _, err := f.Write(entry); err != nil {
			b.Fatalf("write idx entry: %v", err)
		}
	}
}

func appendU16(b []byte, v uint16) []byte {
	return append(b, byte(v), byte(v>>8))
}
func appendU32(b []byte, v uint32) []byte {
	return append(b, byte(v), byte(v>>8), byte(v>>16), byte(v>>24))
}
func appendU64(b []byte, v uint64) []byte {
	return append(b, byte(v), byte(v>>8), byte(v>>16), byte(v>>24),
		byte(v>>32), byte(v>>40), byte(v>>48), byte(v>>56))
}
func appendU64At(b []byte, v uint64) {
	b[0], b[1], b[2], b[3] = byte(v), byte(v>>8), byte(v>>16), byte(v>>24)
	b[4], b[5], b[6], b[7] = byte(v>>32), byte(v>>40), byte(v>>48), byte(v>>56)
}
