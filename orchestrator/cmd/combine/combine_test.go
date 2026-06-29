package main

import (
	"fmt"
	"os"
	"path/filepath"
	"testing"
)

// writeHeight writes a minimal h<H>.out shard with one "n value" row.
func writeHeight(t *testing.T, dir string, H int, n int, v uint64) {
	t.Helper()
	p := filepath.Join(dir, fmt.Sprintf("h%d.out", H))
	if err := os.WriteFile(p, []byte(fmt.Sprintf("%d %d\n", n, v)), 0o644); err != nil {
		t.Fatal(err)
	}
}

// TestCombineDefaultRequiresCover proves that under the default cover policy a
// missing height shard is rejected, not silently summed into a too-low a(n).
// With requireCoverDefault==false (the bug) combine accepts the gap and returns
// a confident wrong total.
func TestCombineDefaultRequiresCover(t *testing.T) {
	dir := t.TempDir()
	// maxn=4 but only heights 1..3 present — h4 is missing (e.g. a bad rsync).
	writeHeight(t, dir, 1, 1, 1)
	writeHeight(t, dir, 2, 2, 1)
	writeHeight(t, dir, 3, 3, 1)

	_, _, err := runCombine([]string{dir}, 4, requireCoverDefault)
	if err == nil {
		t.Fatalf("combine accepted a missing height under the default cover policy (silent too-low a(n))")
	}
}

// TestCombineRejectsDoubleCount proves a height supplied by two dirs aborts.
func TestCombineRejectsDoubleCount(t *testing.T) {
	a, b := t.TempDir(), t.TempDir()
	writeHeight(t, a, 2, 2, 1)
	writeHeight(t, b, 2, 2, 1)
	if _, _, err := runCombine([]string{a, b}, 4, false); err == nil {
		t.Fatalf("combine accepted height 2 from two dirs (double-count)")
	}
}
