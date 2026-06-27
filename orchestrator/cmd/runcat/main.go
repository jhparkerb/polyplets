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
	for _, path := range os.Args[1:] {
		if err := catFile(path); err != nil {
			fmt.Fprintf(os.Stderr, "runcat: %s: %v\n", path, err)
			os.Exit(1)
		}
	}
}

func catFile(path string) error {
	hdr, bodyOff, err := orchestrator.ParseHeader(path)
	if err != nil {
		return err
	}

	fmt.Printf("# POLYRUN run: %s\n", path)
	fmt.Printf("# height=%d maxn=%d counter=%s classifier=triangle records=%d rev=%s\n",
		hdr.Height, hdr.Maxn, hdr.Counter, hdr.Records, hdr.Rev)
	fmt.Printf("# keylo=%s keyhi=%s\n", hdr.KeyLo, hdr.KeyHi)

	// CRC check.
	crcStatus := crcCheck(path)
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
	wordBytes := hdr.WordBytes()
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
			buf := make([]byte, wordBytes)
			if _, err := io.ReadFull(r, buf); err != nil {
				break
			}
			if wordBytes == 8 {
				v := binary.LittleEndian.Uint64(buf)
				counts[i] = fmt.Sprintf("%d", v)
			} else {
				// u128: two LE u64 words
				lo64 := binary.LittleEndian.Uint64(buf[:8])
				hi64 := binary.LittleEndian.Uint64(buf[8:])
				var b big.Int
				b.SetUint64(hi64)
				b.Lsh(&b, 64)
				var lo128 big.Int
				lo128.SetUint64(lo64)
				b.Or(&b, &lo128)
				counts[i] = b.String()
			}
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
	return nil
}

// crcCheck verifies the stored FNV-1a-64 CRC against the body bytes.
func crcCheck(path string) string {
	data, err := os.ReadFile(path)
	if err != nil {
		return fmt.Sprintf("ERROR: %v", err)
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
		return "ERROR: cannot locate body"
	}
	body := data[start : len(data)-8]
	stored := binary.LittleEndian.Uint64(data[len(data)-8:])
	computed := fnv1a64(body)
	if computed == stored {
		return "OK"
	}
	return fmt.Sprintf("MISMATCH: computed=%016x stored=%016x", computed, stored)
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
