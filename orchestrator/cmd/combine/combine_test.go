package main

import (
	"fmt"
	"math/big"
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

// TestFirstNonMonotoneCatchesWrap encodes the a26 stale-u64-combine near-miss:
// a(26) ~1.03e20 summed by a stale u64 binary wrapped mod 2^64 to below a(25).
// The monotone-growth guard must flag it (fixed-polyplet counts strictly rise),
// and must pass a genuinely increasing prefix. Red before firstNonMonotone.
func TestFirstNonMonotoneCatchesWrap(t *testing.T) {
	mk := func(vals ...string) []*big.Int {
		tri := make([]*big.Int, len(vals))
		for i, s := range vals {
			tri[i], _ = new(big.Int).SetString(s, 10)
		}
		return tri
	}
	// index n holds a(n); index 0 unused.
	good := mk("0", "1", "4", "20", "110", "638")
	if got := firstNonMonotone(good, 5); got != 0 {
		t.Fatalf("strictly-increasing prefix: firstNonMonotone=%d, want 0", got)
	}
	// a(25) then a(26)-wrapped (< a(25)): must flag n=2 (the wrapped index).
	wrapped := mk("0", "14994811325186658577", "10373793478466395812")
	if got := firstNonMonotone(wrapped, 2); got != 2 {
		t.Fatalf("wrapped a(26): firstNonMonotone=%d, want 2", got)
	}
}

// TestCombineWidth proves a cell value exceeding 2^64-1 (BUGS-OF-SHAME A2)
// combines to its exact big.Int sum rather than silently wrapping, dropping,
// or erroring. 3^45 alone already exceeds 2^64 (~1.8e19); the value is split
// across two shards (heights 1 and 2, both contributing to n=2=maxn) so
// addRow's accumulation itself is exercised twice on the same triangle cell,
// not just the parse of a single wide literal.
func TestCombineWidth(t *testing.T) {
	// 3^45 = 92709463147897837085761925410587, split as two summands that
	// add back to it exactly.
	partA, _ := new(big.Int).SetString("50000000000000000000000000000000", 10)
	partB, _ := new(big.Int).SetString("42709463147897837085761925410587", 10)
	want := new(big.Int).Add(partA, partB)

	dir := t.TempDir()
	writeFile(t, dir, 1, fmt.Sprintf("1 0\n2 %s\n", partA))
	writeFile(t, dir, 2, fmt.Sprintf("1 0\n2 %s\n", partB))

	tri, _, err := runCombine([]string{dir}, 2, false)
	if err != nil {
		t.Fatalf("runCombine: %v", err)
	}
	if tri[2].Cmp(want) != 0 {
		t.Fatalf("combine width: got %s want %s (a uint64 pipeline would have wrapped or errored)", tri[2], want)
	}
}

// TestRunDiffMatches proves two identical per-height directory sets diff
// clean — the baseline runCombine's summed-total check can't distinguish
// (Design 14 2.7: cell-by-cell, not just the sum).
func TestRunDiffMatches(t *testing.T) {
	a, b := t.TempDir(), t.TempDir()
	for H := 1; H <= 4; H++ {
		writeShard(t, a, H, 4)
		writeShard(t, b, H, 4)
	}
	ok, err := runDiff([]string{a}, []string{b}, 4)
	if err != nil {
		t.Fatalf("runDiff: %v", err)
	}
	if !ok {
		t.Fatalf("runDiff on identical shard sets: got FAIL, want PASS")
	}
}

// TestRunDiffCatchesCellMismatch proves a single differing T(n,H) cell fails
// the diff even though the two sides' SUMMED a(n) totals could plausibly
// still match (the whole point of a cell-by-cell check over runCombine's
// summed-total one). Red before runDiff: a same-total, different-shape pair
// (kink kernel producing the right a(n) via a wrong per-height split) is
// exactly the bug class this tool exists to catch.
func TestRunDiffCatchesCellMismatch(t *testing.T) {
	a, b := t.TempDir(), t.TempDir()
	writeRawShard(t, a, 2, [][2]int{{1, 0}, {2, 1}, {3, 1}, {4, 1}})
	writeRawShard(t, b, 2, [][2]int{{1, 0}, {2, 1}, {3, 1}, {4, 2}}) // n=4 differs
	writeShard(t, a, 1, 4)
	writeShard(t, b, 1, 4)
	writeShard(t, a, 3, 4)
	writeShard(t, b, 3, 4)
	writeShard(t, a, 4, 4)
	writeShard(t, b, 4, 4)

	ok, err := runDiff([]string{a}, []string{b}, 4)
	if err != nil {
		t.Fatalf("runDiff: %v", err)
	}
	if ok {
		t.Fatalf("runDiff missed a differing T(4,2) cell (got PASS, want FAIL)")
	}
}

// TestRunDiffCatchesMissingHeight proves a height present on only one side
// fails the diff rather than being silently skipped.
func TestRunDiffCatchesMissingHeight(t *testing.T) {
	a, b := t.TempDir(), t.TempDir()
	for H := 1; H <= 4; H++ {
		writeShard(t, a, H, 4)
		if H == 3 {
			continue // b is missing height 3
		}
		writeShard(t, b, H, 4)
	}
	ok, err := runDiff([]string{a}, []string{b}, 4)
	if err != nil {
		t.Fatalf("runDiff: %v", err)
	}
	if ok {
		t.Fatalf("runDiff missed a height present only on the A side (got PASS, want FAIL)")
	}
}
