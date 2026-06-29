package main

import (
	"fmt"
	"os"
	"path/filepath"
	"strings"
	"testing"
)

// writeShard writes a valid h<H>.out: rows n=1..maxn, count 1 for n>=H (every
// height contributes a non-zero T(H,H)) and 0 for n<H.
func writeShard(t *testing.T, dir string, H, maxn int) {
	t.Helper()
	var b strings.Builder
	for n := 1; n <= maxn; n++ {
		v := 0
		if n >= H {
			v = 1
		}
		fmt.Fprintf(&b, "%d %d\n", n, v)
	}
	writeFile(t, dir, H, b.String())
}

// writeRawShard writes an h<H>.out with exactly the given "n value" rows — used
// to forge truncated / zeroed / overflowing shards.
func writeRawShard(t *testing.T, dir string, H int, rows [][2]int) {
	t.Helper()
	var b strings.Builder
	for _, r := range rows {
		fmt.Fprintf(&b, "%d %d\n", r[0], r[1])
	}
	writeFile(t, dir, H, b.String())
}

func writeFile(t *testing.T, dir string, H int, body string) {
	t.Helper()
	p := filepath.Join(dir, fmt.Sprintf("h%d.out", H))
	if err := os.WriteFile(p, []byte(body), 0o644); err != nil {
		t.Fatal(err)
	}
}

// TestCombineDefaultRequiresCover proves that under the default cover policy a
// missing height shard is rejected, not silently summed into a too-low a(n).
func TestCombineDefaultRequiresCover(t *testing.T) {
	dir := t.TempDir()
	// maxn=4 but only heights 1..3 present — h4 is missing (e.g. a bad rsync).
	writeShard(t, dir, 1, 4)
	writeShard(t, dir, 2, 4)
	writeShard(t, dir, 3, 4)
	if _, _, err := runCombine([]string{dir}, 4, requireCoverDefault); err == nil {
		t.Fatalf("combine accepted a missing height under the default cover policy (silent too-low a(n))")
	}
}

// TestCombineRejectsDoubleCount proves a height supplied by two dirs aborts.
func TestCombineRejectsDoubleCount(t *testing.T) {
	a, b := t.TempDir(), t.TempDir()
	writeShard(t, a, 2, 4)
	writeShard(t, b, 2, 4)
	if _, _, err := runCombine([]string{a, b}, 4, false); err == nil {
		t.Fatalf("combine accepted height 2 from two dirs (double-count)")
	}
}

// TestCombineRejectsTruncatedShard proves a shard missing its top row (n==maxn)
// is rejected, not summed as a too-low contribution. Atomic writes make this a
// corruption/partial-rsync signal.
func TestCombineRejectsTruncatedShard(t *testing.T) {
	dir := t.TempDir()
	// rows n=1..3 only; the n=4 row (maxn) is gone.
	writeRawShard(t, dir, 2, [][2]int{{1, 0}, {2, 1}, {3, 1}})
	if _, _, err := runCombine([]string{dir}, 4, false); err == nil {
		t.Fatalf("combine accepted a truncated shard (missing n=maxn row)")
	}
}

// TestCombineRejectsZeroedShard proves an all-zero shard (every height has a
// non-zero T(H,H)) is rejected rather than contributing nothing.
func TestCombineRejectsZeroedShard(t *testing.T) {
	dir := t.TempDir()
	writeRawShard(t, dir, 2, [][2]int{{1, 0}, {2, 0}, {3, 0}, {4, 0}})
	if _, _, err := runCombine([]string{dir}, 4, false); err == nil {
		t.Fatalf("combine accepted an all-zero shard")
	}
}

// TestCombineRejectsOverflowRow proves combine refuses a shard whose data
// extends past --maxn (a nonzero n>maxn row), instead of silently dropping it
// (Silent Truncator: --maxn smaller than the data).
func TestCombineRejectsOverflowRow(t *testing.T) {
	dir := t.TempDir()
	// valid through n=4, but also a nonzero n=5 row while combine asks maxn=4.
	writeRawShard(t, dir, 2, [][2]int{{1, 0}, {2, 1}, {3, 1}, {4, 1}, {5, 7}})
	if _, _, err := runCombine([]string{dir}, 4, false); err == nil {
		t.Fatalf("combine silently dropped n=5 > maxn=4 data instead of refusing")
	}
}

// TestCombineAcceptsValidShards guards against over-strict checks: a full,
// non-empty, in-range set of shards must combine without error.
func TestCombineAcceptsValidShards(t *testing.T) {
	dir := t.TempDir()
	for H := 1; H <= 4; H++ {
		writeShard(t, dir, H, 4)
	}
	if _, _, err := runCombine([]string{dir}, 4, true); err != nil {
		t.Fatalf("valid shards rejected: %v", err)
	}
}
