// runref.go — RunRef handle, POLYRUN header parsing, key sampling, CRC verification.
package orchestrator

import (
	"bufio"
	"encoding/binary"
	"fmt"
	"io"
	"os"
	"sort"
	"strconv"
	"strings"
)

// RunRef is a handle to a completed sorted POLYRUN file on disk.
type RunRef struct {
	Path    string
	Records uint64
	KeyLo   string // hex, empty = start of key space
	KeyHi   string // hex, empty = end of key space
}

// PolyrunHeader holds parsed POLYRUN file header fields.
type PolyrunHeader struct {
	Height  int
	Maxn    int
	Records uint64
	Counter string // "u64" or "u128"
	KeyLo   string
	KeyHi   string
	Rev     string
}

// WordBytes returns the byte width of one count value (8 for u64, 16 for u128).
func (h PolyrunHeader) WordBytes() int {
	if h.Counter == "u128" {
		return 16
	}
	return 8
}

// ParseHeader reads a POLYRUN header and returns it with the byte offset
// where the binary body begins.
func ParseHeader(path string) (PolyrunHeader, int64, error) {
	f, err := os.Open(path)
	if err != nil {
		return PolyrunHeader{}, 0, err
	}
	defer f.Close()

	br := bufio.NewReader(f)
	var hdr PolyrunHeader
	var offset int64

	for {
		line, err := br.ReadString('\n')
		offset += int64(len(line))
		line = strings.TrimRight(line, "\r\n")
		if line == "" {
			break
		}
		if err != nil {
			break
		}
		k, v, ok := strings.Cut(line, " ")
		if !ok {
			continue
		}
		switch k {
		case "height":
			hdr.Height, _ = strconv.Atoi(v)
		case "maxn":
			hdr.Maxn, _ = strconv.Atoi(v)
		case "records":
			hdr.Records, _ = strconv.ParseUint(strings.TrimSpace(v), 10, 64)
		case "counter":
			hdr.Counter = strings.TrimSpace(v)
		case "keylo":
			hdr.KeyLo = v
		case "keyhi":
			hdr.KeyHi = v
		case "rev":
			hdr.Rev = v
		}
	}
	return hdr, offset, nil
}

// SampleKeys samples up to numCuts evenly-spaced sig keys from a POLYRUN file
// for input-space partitioning.  Returns hex-encoded keys; len <= numCuts.
// Caller converts into unit boundaries: unit i covers [cuts[i-1], cuts[i]).
func SampleKeys(path string, H, numCuts int) ([]string, error) {
	if numCuts <= 0 {
		return nil, nil
	}
	hdr, bodyOff, err := ParseHeader(path)
	if err != nil {
		return nil, err
	}
	if hdr.Records == 0 || hdr.Height != H {
		return nil, nil
	}

	f, err := os.Open(path)
	if err != nil {
		return nil, err
	}
	defer f.Close()
	if _, err := f.Seek(bodyOff, io.SeekStart); err != nil {
		return nil, err
	}

	// Stream records (variable-length: keyLen + 2 + len*wordBytes bytes).
	keyLen := H + 2
	wordBytes := hdr.WordBytes()
	stride := int(hdr.Records) / (numCuts + 1)
	if stride < 1 {
		stride = 1
	}
	sig := make([]byte, keyLen)
	meta := make([]byte, 2)
	var cuts []string
	idx := 0
	for {
		if _, err := io.ReadFull(f, sig); err != nil {
			break
		}
		if _, err := io.ReadFull(f, meta); err != nil {
			break
		}
		length := int(meta[1])
		// Skip count bytes (wordBytes per entry).
		if _, err := io.CopyN(io.Discard, f, int64(length*wordBytes)); err != nil {
			break
		}
		idx++
		if idx%stride == 0 && len(cuts) < numCuts {
			cuts = append(cuts, bytesToHex(sig))
		}
	}
	return cuts, nil
}

// SampleKeysMulti samples cut points across multiple POLYRUN files.
// The cuts are returned in ascending lexicographic order (the correct merge order).
// IMPORTANT: map output files have OVERLAPPING output key ranges (multiple workers
// can emit the same successor key), so the file list is NOT in sorted key order.
// We must sort the combined samples before subsampling to get valid partition cuts.
func SampleKeysMulti(paths []string, H, numCuts int) ([]string, error) {
	if numCuts <= 0 {
		return nil, nil
	}
	if len(paths) == 1 {
		return SampleKeys(paths[0], H, numCuts)
	}
	// Collect samples from all files and deduplicate.
	var all []string
	seen := make(map[string]bool)
	for _, p := range paths {
		c, err := SampleKeys(p, H, numCuts)
		if err != nil {
			return nil, err
		}
		for _, k := range c {
			if !seen[k] {
				seen[k] = true
				all = append(all, k)
			}
		}
	}
	// Sort lexicographically; hex-encoded sigs sort the same as the raw bytes.
	sort.Strings(all)

	if len(all) <= numCuts {
		return all, nil
	}
	// Subsample evenly.
	out := make([]string, numCuts)
	stride := len(all) / (numCuts + 1)
	if stride < 1 {
		stride = 1
	}
	for i := range out {
		idx := (i + 1) * stride
		if idx >= len(all) {
			idx = len(all) - 1
		}
		out[i] = all[idx]
	}
	return out, nil
}

// SplitRangeByIndex picks numCuts keys that divide (loHex, hiHex) into
// numCuts+1 roughly record-equal sub-ranges, for splitting a work-stealing
// straggler's remaining range across idle cores.  It reads only the sparse
// .idx sidecars (one entry per 64 records), never the run bodies, so it is
// cheap even on a multi-GB frontier — steals happen in the column tail, and
// re-reading the frontier per steal would defeat the purpose.
//
// Cuts are strictly inside (lo, hi) and ascending, so every sub-range is
// non-empty.  Returns fewer than numCuts (possibly zero) when the indexes hold
// too few in-range samples to cut finely — the caller then steals less (or not
// at all), which is the correct degenerate behaviour.
func SplitRangeByIndex(frontier []string, H int, loHex, hiHex string, numCuts int) ([]string, error) {
	if numCuts <= 0 {
		return nil, nil
	}
	keyLen := H + 2
	loB, hasLo := hexBytes(loHex, keyLen)
	hiB, hasHi := hexBytes(hiHex, keyLen)

	// Gather in-range index keys across all frontier files. Frontier (merge
	// output) files are disjoint key ranges, so a simple sorted union of their
	// in-range index keys is record-balanced (uniform 1-per-64 stride per file).
	var keys []string
	seen := make(map[string]bool)
	for _, p := range frontier {
		ks, err := indexKeysInRange(p+".idx", keyLen, loB, hasLo, hiB, hasHi)
		if err != nil {
			continue // missing/short index → just contributes no cut candidates
		}
		for _, k := range ks {
			if !seen[k] {
				seen[k] = true
				keys = append(keys, k)
			}
		}
	}
	if len(keys) == 0 {
		return nil, nil
	}
	sort.Strings(keys)

	if len(keys) <= numCuts {
		return keys, nil
	}
	out := make([]string, numCuts)
	stride := len(keys) / (numCuts + 1)
	if stride < 1 {
		stride = 1
	}
	for i := range out {
		idx := (i + 1) * stride
		if idx >= len(keys) {
			idx = len(keys) - 1
		}
		out[i] = keys[idx]
	}
	return out, nil
}

// indexKeysInRange reads a .idx sidecar and returns the hex keys that fall in
// (lo, hi) — strictly greater than lo (a cut equal to lo would leave an empty
// first piece) and, if hi is set, strictly less than hi.
// Sidecar format (native byte order): [u32 keyLen][u64 count]{key[keyLen], u64 offset, u64 recidx}*.
func indexKeysInRange(idxPath string, keyLen int, lo []byte, hasLo bool, hi []byte, hasHi bool) ([]string, error) {
	f, err := os.Open(idxPath)
	if err != nil {
		return nil, err
	}
	defer f.Close()
	br := bufio.NewReader(f)

	var kl uint32
	var cnt uint64
	if err := binary.Read(br, binary.LittleEndian, &kl); err != nil {
		return nil, err
	}
	if err := binary.Read(br, binary.LittleEndian, &cnt); err != nil {
		return nil, err
	}
	if int(kl) != keyLen {
		return nil, fmt.Errorf("idx keyLen %d != %d", kl, keyLen)
	}
	entry := make([]byte, int(kl)+16) // key + u64 offset + u64 recidx
	key := entry[:kl]
	var keys []string
	for i := uint64(0); i < cnt; i++ {
		if _, err := io.ReadFull(br, entry); err != nil {
			break
		}
		if hasLo && bytesCompare(key, lo) <= 0 {
			continue
		}
		if hasHi && bytesCompare(key, hi) >= 0 {
			continue
		}
		keys = append(keys, bytesToHex(key))
	}
	return keys, nil
}

// hexBytes decodes a hex key to keyLen bytes; ok=false for an empty/short hex
// (an open range end).
func hexBytes(hexStr string, keyLen int) ([]byte, bool) {
	if len(hexStr) != keyLen*2 {
		return nil, false
	}
	b := make([]byte, keyLen)
	for i := 0; i < keyLen; i++ {
		var hi, lo byte
		if !hexNibble(hexStr[i*2], &hi) || !hexNibble(hexStr[i*2+1], &lo) {
			return nil, false
		}
		b[i] = hi<<4 | lo
	}
	return b, true
}

func hexNibble(c byte, out *byte) bool {
	switch {
	case c >= '0' && c <= '9':
		*out = c - '0'
	case c >= 'a' && c <= 'f':
		*out = c - 'a' + 10
	case c >= 'A' && c <= 'F':
		*out = c - 'A' + 10
	default:
		return false
	}
	return true
}

func bytesCompare(a, b []byte) int {
	for i := 0; i < len(a) && i < len(b); i++ {
		if a[i] != b[i] {
			if a[i] < b[i] {
				return -1
			}
			return 1
		}
	}
	return len(a) - len(b)
}

// VerifyCRC reads a POLYRUN file and checks its FNV-1a-64 body CRC.
// A mismatch is fatal: corrupt data must never silently proceed.
func VerifyCRC(path string) error {
	data, err := os.ReadFile(path)
	if err != nil {
		return err
	}
	// Find header end (first blank line = \n\n).
	start := -1
	for i := 0; i < len(data)-1; i++ {
		if data[i] == '\n' && data[i+1] == '\n' {
			start = i + 2
			break
		}
	}
	if start < 0 {
		return fmt.Errorf("VerifyCRC %s: no header end", path)
	}
	if len(data)-start < 8 {
		return fmt.Errorf("VerifyCRC %s: body too short for CRC", path)
	}
	body := data[start : len(data)-8]
	stored := binary.LittleEndian.Uint64(data[len(data)-8:])
	computed := fnv1a64(body)
	if computed != stored {
		return fmt.Errorf("CRC MISMATCH %s: computed %016x stored %016x", path, computed, stored)
	}
	return nil
}

const fnvOffset uint64 = 14695981039346656037
const fnvPrime uint64 = 1099511628211

func fnv1a64(data []byte) uint64 {
	h := fnvOffset
	for _, b := range data {
		h ^= uint64(b)
		h *= fnvPrime
	}
	return h
}

func bytesToHex(b []byte) string {
	const hexChars = "0123456789abcdef"
	s := make([]byte, len(b)*2)
	for i, v := range b {
		s[i*2] = hexChars[v>>4]
		s[i*2+1] = hexChars[v&0xf]
	}
	return string(s)
}

// WriteSeedPolyrun writes a seed POLYRUN file for height H (col 0: empty boundary,
// counts[0]=1).  counter is "u64" or "u128" (empty = "u64").
// The record count is known upfront so no fseek is needed.
func WriteSeedPolyrun(path, rev string, H, maxn int, counter ...string) error {
	counterTag := "u64"
	if len(counter) > 0 && counter[0] != "" {
		switch counter[0] {
		case "u64", "u128":
			counterTag = counter[0]
		default:
			// Fail loud: an unknown tag (typo) must not silently default to u64
			// and miscount a run that was meant to be wider.
			return fmt.Errorf("WriteSeedPolyrun: unknown counter %q (want u64 or u128)", counter[0])
		}
	}
	wordBytes := (PolyrunHeader{Counter: counterTag}).WordBytes()

	f, err := os.Create(path)
	if err != nil {
		return err
	}
	defer f.Close()

	if rev == "" {
		rev = "unknown"
	}
	// Header.
	fmt.Fprintf(f, "POLYRUN 1\n")
	fmt.Fprintf(f, "height %d\n", H)
	fmt.Fprintf(f, "maxn %d\n", maxn)
	fmt.Fprintf(f, "counter %s\n", counterTag)
	fmt.Fprintf(f, "classifier triangle\n")
	fmt.Fprintf(f, "keylo \n")
	fmt.Fprintf(f, "keyhi \n")
	fmt.Fprintf(f, "records %018d\n", 1)
	fmt.Fprintf(f, "rev %s\n", rev)
	fmt.Fprintf(f, "byteorder 1\n")
	fmt.Fprintf(f, "\n")

	// One binary record: sig=(H+2 zero bytes), lo=0, len=1, counts[0]=1 LE.
	keyLen := H + 2
	body := make([]byte, keyLen+2+wordBytes)
	// body[0..keyLen-1] = 0 (sig)
	// body[keyLen] = 0 (lo)
	// body[keyLen+1] = 1 (len)
	body[keyLen+1] = 1
	// body[keyLen+2..keyLen+wordBytes+1] = 1 as LE value
	binary.LittleEndian.PutUint64(body[keyLen+2:], 1)
	// for u128, the upper 8 bytes remain zero (already zero-initialized)

	crc := fnv1a64(body)
	crcBytes := make([]byte, 8)
	binary.LittleEndian.PutUint64(crcBytes, crc)

	if _, err := f.Write(body); err != nil {
		return err
	}
	if _, err := f.Write(crcBytes); err != nil {
		return err
	}
	return f.Close()
}
