package main

import (
	"encoding/binary"
	"os"
	"path/filepath"
	"testing"

	"polyominoes/orchestrator"
)

// TestCatFileFailsOnCrcMismatch proves runcat reports a CRC mismatch as an
// error (so the process exits nonzero), instead of printing "# CRC: MISMATCH"
// and returning success. A valid seed must still cat cleanly.
func TestCatFileFailsOnCrcMismatch(t *testing.T) {
	dir := t.TempDir()
	path := filepath.Join(dir, "seed_h3.bin")
	if err := orchestrator.WriteSeedPolyrun(path, "test", 3, 8); err != nil {
		t.Fatal(err)
	}

	// Control: an intact file cats without error.
	if err := catFile(path); err != nil {
		t.Fatalf("intact seed reported an error: %v", err)
	}

	// Corrupt one body byte (just before the 8-byte CRC trailer) so the stored
	// CRC no longer matches the recomputed body.
	data, err := os.ReadFile(path)
	if err != nil {
		t.Fatal(err)
	}
	data[len(data)-9] ^= 0xFF
	if err := os.WriteFile(path, data, 0o644); err != nil {
		t.Fatal(err)
	}

	if err := catFile(path); err == nil {
		t.Fatalf("catFile returned nil on a CRC mismatch (runcat would exit 0)")
	}
}

// TestCatFileFailsOnShortBody proves a body that ends inside a record is an
// error even when its checksum is consistent: the seed's last count byte is
// cut and the trailer recomputed over the shortened body.
func TestCatFileFailsOnShortBody(t *testing.T) {
	dir := t.TempDir()
	path := filepath.Join(dir, "seed_h3.bin")
	if err := orchestrator.WriteSeedPolyrun(path, "test", 3, 8); err != nil {
		t.Fatal(err)
	}
	_, bodyOff, err := orchestrator.ParseHeader(path)
	if err != nil {
		t.Fatal(err)
	}
	data, err := os.ReadFile(path)
	if err != nil {
		t.Fatal(err)
	}
	body := data[bodyOff : len(data)-9]
	short := append(append([]byte{}, data[:bodyOff]...), body...)
	short = binary.LittleEndian.AppendUint64(short, orchestrator.Fnv1a64(body))
	if err := os.WriteFile(path, short, 0o644); err != nil {
		t.Fatal(err)
	}

	if err := catFile(path); err == nil {
		t.Fatalf("catFile returned nil on a body that ends inside a record")
	}
}
