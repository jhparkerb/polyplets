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
	KeyLo   string
	KeyHi   string
	Rev     string
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

	// Stream records (variable-length: keyLen + 2 + len*8 bytes for u64).
	keyLen := H + 2
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
		// Skip count bytes (u64 = 8 B each).
		if _, err := io.CopyN(io.Discard, f, int64(length*8)); err != nil {
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
// counts[0]=1).  The record count is known upfront so no fseek is needed.
func WriteSeedPolyrun(path, rev string, H, maxn int) error {
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
	fmt.Fprintf(f, "counter u64\n")
	fmt.Fprintf(f, "classifier triangle\n")
	fmt.Fprintf(f, "keylo \n")
	fmt.Fprintf(f, "keyhi \n")
	fmt.Fprintf(f, "records %018d\n", 1)
	fmt.Fprintf(f, "rev %s\n", rev)
	fmt.Fprintf(f, "byteorder 1\n")
	fmt.Fprintf(f, "\n")

	// One binary record: sig=(H+2 zero bytes), lo=0, len=1, counts[0]=1 LE u64.
	keyLen := H + 2
	body := make([]byte, keyLen+2+8)
	// body[0..keyLen-1] = 0 (sig)
	// body[keyLen] = 0 (lo)
	// body[keyLen+1] = 1 (len)
	body[keyLen+1] = 1
	// body[keyLen+2..keyLen+9] = 1 as LE u64
	binary.LittleEndian.PutUint64(body[keyLen+2:], 1)

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
