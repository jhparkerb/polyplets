// main.go — runcat: render a POLYRUN binary file to human-readable text.
//
// Usage:
//   runcat <file.bin> [<file.bin> ...]
//
// Output per file:
//   # POLYRUN run: path/to/file.bin
//   # height=H maxn=N counter=u64 classifier=triangle records=M rev=REV
//   # keylo=HEX keyhi=HEX
//   # CRC: OK   (or MISMATCH: computed=X stored=Y)
//   sig=HEX lo=LO len=LEN counts=[C0,C1,...]
//   ...
//   # total: M records
package main

import (
	"bufio"
	"encoding/binary"
	"encoding/hex"
	"fmt"
	"io"
	"math/big"
	"os"
	"strings"

	"polyominoes/orchestrator"
)

func main() {
	if len(os.Args) < 2 {
		fmt.Fprintln(os.Stderr, "usage: runcat <file.bin> [<file.bin> ...]")
		os.Exit(1)
	}
	exit := 0
	for _, path := range os.Args[1:] {
		if err := catFile(path); err != nil {
			fmt.Fprintf(os.Stderr, "runcat: %s: %v\n", path, err)
			exit = 1
		}
	}
	os.Exit(exit)
}

func catFile(path string) error {
	hdr, bodyOff, err := orchestrator.ParseHeader(path)
	if err != nil {
		return err
	}
	// FAIL-CLOSED: runcat decodes raw record bytes; a compressed body would be
	// misread as garbage records rather than erroring. No Go zstd path here —
	// say so, and point at something that actually exists: verify.go is Go too
	// and there is no C++ dump tool, so the honest answers are the readers'
	// own fail-closed frame-checksum enforcement and a manual zstd -d.
	if hdr.Compression != 0 {
		return fmt.Errorf("%s: compressed body (compression %d): runcat decodes plain bodies only. Integrity of a compressed body is the in-band zstd frame checksum, enforced fail-closed by the C++ readers (core/runfile.h) — a decode or checksum failure aborts the reading worker. To dump it by hand: tail -c +%d %s | zstd -d", path, hdr.Compression, bodyOff+1, path)
	}

	fmt.Printf("# POLYRUN run: %s\n", path)
	fmt.Printf("# height=%d maxn=%d counter=%s classifier=triangle records=%d rev=%s\n",
		hdr.Height, hdr.Maxn, hdr.Counter, hdr.Records, hdr.Rev)
	fmt.Printf("# keylo=%s keyhi=%s\n", hdr.KeyLo, hdr.KeyHi)

	// CRC check.
	crcStatus, crcOK := crcCheck(path)
	fmt.Printf("# CRC: %s\n", crcStatus)

	f, err := os.Open(path)
	if err != nil {
		return err
	}
	defer f.Close()

	if _, err := f.Seek(bodyOff, io.SeekStart); err != nil {
		return err
	}

	r := bufio.NewReader(f)
	keyLen := hdr.Height + 2
	sig := make([]byte, keyLen)
	meta := make([]byte, 2)

	var count uint64
	for {
		if _, err := io.ReadFull(r, sig); err != nil {
			if err == io.EOF {
				break
			}
			// At end we'll hit the 8-byte CRC trailer; short read is normal stop.
			break
		}
		if _, err := io.ReadFull(r, meta); err != nil {
			break
		}
		lo := meta[0]
		length := int(meta[1])

		counts := make([]string, length)
		for i := range counts {
			v, err := readVarintBig(r)
			if err != nil {
				break
			}
			counts[i] = v.String()
		}

		fmt.Printf("sig=%s lo=%d len=%d counts=[%s]\n",
			hex.EncodeToString(sig), lo, length, strings.Join(counts, ","))
		count++

		// Stop after hdr.Records to avoid reading into the CRC.
		if count >= hdr.Records {
			break
		}
	}

	fmt.Printf("# total: %d records\n", count)
	if !crcOK {
		// The mismatch was already printed on the "# CRC:" line; surface it as a
		// process failure so a corrupt run file can't pass unnoticed (exit 0).
		return fmt.Errorf("CRC mismatch")
	}
	return nil
}

// crcCheck verifies the stored FNV-1a-64 CRC against the body bytes, returning a
// human-readable status and whether it matched.
func crcCheck(path string) (status string, ok bool) {
	data, err := os.ReadFile(path)
	if err != nil {
		return fmt.Sprintf("ERROR: %v", err), false
	}
	// Find header end: first \n\n.
	start := -1
	for i := 0; i < len(data)-1; i++ {
		if data[i] == '\n' && data[i+1] == '\n' {
			start = i + 2
			break
		}
	}
	if start < 0 || len(data)-start < 8 {
		return "ERROR: cannot locate body", false
	}
	body := data[start : len(data)-8]
	stored := binary.LittleEndian.Uint64(data[len(data)-8:])
	computed := orchestrator.Fnv1a64(body)
	if computed == stored {
		return "OK", true
	}
	return fmt.Sprintf("MISMATCH: computed=%016x stored=%016x", computed, stored), false
}

// readVarintBig reads one LEB128 unsigned varint (core/run.h encodeVarint) as a
// big.Int, so u128-scale counts print exactly. r must be an io.ByteReader.
func readVarintBig(r io.ByteReader) (*big.Int, error) {
	result := new(big.Int)
	chunk := new(big.Int)
	for shift := uint(0); ; shift += 7 {
		b, err := r.ReadByte()
		if err != nil {
			return nil, err
		}
		chunk.SetUint64(uint64(b & 0x7f))
		result.Or(result, chunk.Lsh(chunk, shift))
		if b&0x80 == 0 {
			return result, nil
		}
	}
}
