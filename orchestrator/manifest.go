// manifest.go — per-a(n) provenance manifest writer.
package orchestrator

import (
	"encoding/binary"
	"fmt"
	"os"
	"path/filepath"
)

// WriteManifest writes a provenance manifest for a(n) to outPath.
// If outPath is empty, it defaults to data/manifests/a<n>.txt relative to cwd.
// The manifest records: git rev, resource accounting, total spill, and each run
// file with its FNV-1a-64 CRC.
func WriteManifest(n int, rev string, acct Acct, spillBytes uint64, runs []RunRef, outPath string) error {
	if outPath == "" {
		outPath = filepath.Join("data", "manifests", fmt.Sprintf("a%d.txt", n))
	}
	if err := os.MkdirAll(filepath.Dir(outPath), 0o777); err != nil {
		return err
	}
	f, err := os.Create(outPath)
	if err != nil {
		return err
	}
	defer f.Close()

	fmt.Fprintf(f, "n=%d\n", n)
	fmt.Fprintf(f, "rev=%s\n", rev)
	fmt.Fprintf(f, "cpu_s=%.3f\n", acct.CPUS)
	fmt.Fprintf(f, "wall_s=%.3f\n", acct.WallS)
	fmt.Fprintf(f, "rss_max_mb=%.1f\n", acct.RSSMax)
	fmt.Fprintf(f, "spill_bytes=%d\n", spillBytes)
	fmt.Fprintf(f, "files=%d\n", len(runs))

	for _, r := range runs {
		crc, crcErr := fileCRC(r.Path)
		crcStr := ""
		if crcErr != nil {
			crcStr = "ERROR"
		} else {
			crcStr = fmt.Sprintf("%016x", crc)
		}
		fmt.Fprintf(f, "file path=%s records=%d crc=%s\n", r.Path, r.Records, crcStr)
	}

	return f.Close()
}

// fileCRC computes the FNV-1a-64 CRC stored at the end of a POLYRUN file
// (reads only the last 8 bytes — cheap, no body re-hash needed).
func fileCRC(path string) (uint64, error) {
	data, err := os.ReadFile(path)
	if err != nil {
		return 0, err
	}
	if len(data) < 8 {
		return 0, fmt.Errorf("fileCRC %s: file too short", path)
	}
	return binary.LittleEndian.Uint64(data[len(data)-8:]), nil
}
