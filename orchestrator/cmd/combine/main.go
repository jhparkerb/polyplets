// combine — sum per-height h<H>.out rows (possibly from several machines) into
// the final triangle a(n) = Σ_H T(n,H), validating that each height appears
// exactly once and (optionally) that the set covers 1..maxn.
//
// This is the multi-machine join for the height-split: each machine runs
// `orchestrate --heights <subset> --per-height-out <dir>`, the dirs are rsynced
// to one host, and combine sums them.  It also cross-checks against the old
// engine's h<H>.out, which use the same format.
//
// Usage:
//   combine --in dirA[,dirB,...] --maxn 21 [--compare] [--require-cover] [--out triangle.txt]
//
// Design 14 Phase 2.7 diff mode — compares two --per-height-out directory
// sets CELL BY CELL (every T(n,H), not just the summed a(n) total the mode
// above checks), e.g. a --kernel kink run against a --kernel column run at
// the same maxn:
//   combine --in dirA[,...] --diff-b dirB[,...] --maxn 20
package main

import (
	"flag"
	"fmt"
	"math/big"
	"os"
	"path/filepath"
	"sort"
	"strconv"
	"strings"

	"polyominoes/orchestrator"
)

// requireCoverDefault is the default for --require-cover. A missing height shard
// (e.g. a bad rsync) otherwise sums to a confidently-printed, too-low a(n), so
// coverage is enforced by default; pass --require-cover=false to opt out.
const requireCoverDefault = true

func main() {
	inArg := flag.String("in", "", "comma-separated dirs containing h<H>.out files (required)")
	maxn := flag.Int("maxn", 0, "max n (required)")
	compare := flag.Bool("compare", false, "compare a(n) to fixtures/b006770.txt")
	requireCover := flag.Bool("require-cover", requireCoverDefault, "fail unless heights 1..maxn are all present exactly once")
	out := flag.String("out", "", "write the combined triangle here (n value lines)")
	diffB := flag.String("diff-b", "", "Phase 2.7 diff mode: compare --in's per-height rows against this comma-separated dir set, cell by cell (every T(n,H)); ignores --compare/--require-cover/--out")
	flag.Parse()

	if *inArg == "" || *maxn == 0 {
		fmt.Fprintln(os.Stderr, "combine: --in and --maxn are required")
		os.Exit(2)
	}

	if *diffB != "" {
		ok, err := runDiff(strings.Split(*inArg, ","), strings.Split(*diffB, ","), *maxn)
		if err != nil {
			fmt.Fprintf(os.Stderr, "combine: %v\n", err)
			os.Exit(1)
		}
		if !ok {
			os.Exit(1)
		}
		return
	}

	triangle, have, err := runCombine(strings.Split(*inArg, ","), *maxn, *requireCover)
	if err != nil {
		fmt.Fprintf(os.Stderr, "combine: %v\n", err)
		os.Exit(1)
	}

	fmt.Printf("combine: %d heights present: %v\n", len(have), have)
	for n := 1; n <= *maxn; n++ {
		fmt.Printf("a(%d) = %d\n", n, triangle[n])
	}

	// Monotone-growth guard. The fixed-polyplet count a(n) is strictly
	// increasing, so a(n) <= a(n-1) can only mean a counter overflow (the a26
	// stale-u64-combine near-miss: a26 ~1.03e20 wrapped mod 2^64 to below a25)
	// or missing data. Refuse a full-cover triangle that violates it rather than
	// print a confidently-wrong, too-low a(n). Only enforced under --require-cover
	// (a partial combine can legitimately be incomplete).
	if *requireCover {
		if n := firstNonMonotone(triangle, *maxn); n > 0 {
			fmt.Fprintf(os.Stderr, "combine: REFUSING — non-monotone a(n) at n=%d: "+
				"a(%d)=%d <= a(%d)=%d. The count is strictly increasing, so this is a "+
				"counter overflow (stale u64 combine binary? rebuild it) or missing data, "+
				"not a valid result.\n", n, n, triangle[n], n-1, triangle[n-1])
			os.Exit(1)
		}
	}

	if *out != "" {
		if err := writeTriangle(*out, *maxn, triangle); err != nil {
			fmt.Fprintf(os.Stderr, "combine: write %s: %v\n", *out, err)
			os.Exit(1)
		}
	}

	if *compare {
		os.Exit(compareKnown(*maxn, triangle))
	}
}

// newBigRow returns a zero-filled []*big.Int of length n with every slot a
// distinct non-nil *big.Int (a nil slot panics on .Add).
func newBigRow(n int) []*big.Int {
	row := make([]*big.Int, n)
	for i := range row {
		row[i] = new(big.Int)
	}
	return row
}

// collectHeightFiles globs h<H>.out under each dir and returns H -> path,
// rejecting a height supplied by two dirs (double-count) so the caller never
// silently sums (or diffs) the same shard twice under two different names.
func collectHeightFiles(dirs []string) (map[int]string, error) {
	files := map[int]string{}
	for _, dir := range dirs {
		dir = strings.TrimSpace(dir)
		if dir == "" {
			continue
		}
		paths, _ := filepath.Glob(filepath.Join(dir, "h*.out"))
		for _, p := range paths {
			H, ok := heightFromName(p)
			if !ok {
				continue
			}
			if prev, seen := files[H]; seen {
				return nil, fmt.Errorf("height %d in both %s and %s (double-count)", H, prev, p)
			}
			files[H] = p
		}
	}
	return files, nil
}

// runCombine sums each dir's h<H>.out rows into the triangle, rejecting a height
// supplied by two dirs (double-count) and — when requireCover — any gap in
// 1..maxn. Returns the triangle and the sorted set of heights present.
func runCombine(dirs []string, maxn int, requireCover bool) (triangle []*big.Int, have []int, err error) {
	triangle = newBigRow(maxn + 1)

	heightFiles, err := collectHeightFiles(dirs)
	if err != nil {
		return nil, nil, err
	}
	for H, p := range heightFiles {
		if e := addRow(p, maxn, triangle); e != nil {
			return nil, nil, fmt.Errorf("%s: %w", p, e)
		}
		have = append(have, H)
	}
	sort.Ints(have)

	if requireCover {
		var missing []int
		for H := 1; H <= maxn; H++ {
			if _, ok := heightFiles[H]; !ok {
				missing = append(missing, H)
			}
		}
		if len(missing) > 0 {
			return nil, nil, fmt.Errorf("missing heights %v", missing)
		}
	}
	return triangle, have, nil
}

// runDiff compares two --per-height-out directory sets CELL BY CELL: every
// T(n,H) for every height present on either side, not just the summed a(n)
// total runCombine checks. Prints a per-height report and returns whether
// every height matched exactly (present on both sides, every cell equal).
func runDiff(aDirs, bDirs []string, maxn int) (bool, error) {
	aFiles, err := collectHeightFiles(aDirs)
	if err != nil {
		return false, fmt.Errorf("side A: %w", err)
	}
	bFiles, err := collectHeightFiles(bDirs)
	if err != nil {
		return false, fmt.Errorf("side B: %w", err)
	}

	heights := map[int]bool{}
	for H := range aFiles {
		heights[H] = true
	}
	for H := range bFiles {
		heights[H] = true
	}
	var sorted []int
	for H := range heights {
		sorted = append(sorted, H)
	}
	sort.Ints(sorted)

	ok := true
	for _, H := range sorted {
		ap, aOK := aFiles[H]
		bp, bOK := bFiles[H]
		switch {
		case !aOK:
			fmt.Printf("H=%d: MISSING on A side (B has %s)\n", H, bp)
			ok = false
			continue
		case !bOK:
			fmt.Printf("H=%d: MISSING on B side (A has %s)\n", H, ap)
			ok = false
			continue
		}
		rowA := newBigRow(maxn + 1)
		rowB := newBigRow(maxn + 1)
		if e := addRow(ap, maxn, rowA); e != nil {
			return false, fmt.Errorf("A %s: %w", ap, e)
		}
		if e := addRow(bp, maxn, rowB); e != nil {
			return false, fmt.Errorf("B %s: %w", bp, e)
		}
		mismatches := 0
		for n := 1; n <= maxn; n++ {
			if rowA[n].Cmp(rowB[n]) != 0 {
				fmt.Printf("H=%d n=%d: A=%d B=%d MISMATCH\n", H, n, rowA[n], rowB[n])
				mismatches++
				ok = false
			}
		}
		if mismatches == 0 {
			fmt.Printf("H=%d: OK (%d cells)\n", H, maxn)
		}
	}

	if ok {
		fmt.Printf("combine_diff PASS (%d heights, maxn=%d)\n", len(sorted), maxn)
	} else {
		fmt.Printf("combine_diff FAIL\n")
	}
	return ok, nil
}

// firstNonMonotone returns the smallest n in [2,maxn] with a(n) <= a(n-1)
// (both positive), or 0 if a(1..maxn) is strictly increasing. Skips leading
// zeros so a not-yet-populated prefix doesn't false-trip.
func firstNonMonotone(triangle []*big.Int, maxn int) int {
	for n := 2; n <= maxn; n++ {
		if triangle[n-1].Sign() <= 0 || triangle[n].Sign() <= 0 {
			continue
		}
		if triangle[n].Cmp(triangle[n-1]) <= 0 {
			return n
		}
	}
	return 0
}

func heightFromName(path string) (int, bool) {
	base := filepath.Base(path)
	base = strings.TrimSuffix(base, ".out")
	if !strings.HasPrefix(base, "h") {
		return 0, false
	}
	H, err := strconv.Atoi(base[1:])
	return H, err == nil
}

// addRow adds one h<H>.out file's "n value" rows into the triangle, refusing a
// shard that is truncated, all-zero, or carries data past maxn:
//   - missing the n==maxn row  => truncated/corrupt (shards are written n=1..maxn
//     atomically, so a short file is a partial rsync or disk corruption);
//   - every count zero          => empty/zeroed shard (each height has T(H,H)>0);
//   - a nonzero n>maxn row       => --maxn is smaller than the data, which would
//     silently drop the high-n rows (Silent Truncator).
// Without these, a damaged shard sums to a confidently-printed, too-low a(n).
func addRow(path string, maxn int, triangle []*big.Int) error {
	data, err := os.ReadFile(path)
	if err != nil {
		return err
	}
	sawMaxn := false
	nonzero := false
	overflowN := 0
	for _, line := range strings.Split(string(data), "\n") {
		f := strings.Fields(line)
		if len(f) < 2 {
			continue
		}
		n, e1 := strconv.Atoi(f[0])
		v, ok := new(big.Int).SetString(f[1], 10)
		if e1 != nil || !ok || n < 1 {
			return fmt.Errorf("%s: malformed row %q", filepath.Base(path), line)
		}
		if n > maxn {
			if v.Sign() != 0 && n > overflowN {
				overflowN = n
			}
			continue
		}
		if n == maxn {
			sawMaxn = true
		}
		if v.Sign() != 0 {
			nonzero = true
		}
		triangle[n].Add(triangle[n], v)
	}
	if overflowN > 0 {
		return fmt.Errorf("%s: contains n=%d > maxn=%d with a nonzero count; --maxn too small (data would be dropped)", filepath.Base(path), overflowN, maxn)
	}
	if !sawMaxn {
		return fmt.Errorf("%s: missing the n=%d row (truncated/corrupt shard)", filepath.Base(path), maxn)
	}
	if !nonzero {
		return fmt.Errorf("%s: all counts zero (empty/corrupt shard)", filepath.Base(path))
	}
	return nil
}

func writeTriangle(path string, maxn int, triangle []*big.Int) error {
	f, err := os.Create(path)
	if err != nil {
		return err
	}
	defer f.Close()
	for n := 1; n <= maxn; n++ {
		fmt.Fprintf(f, "%d %d\n", n, triangle[n])
	}
	return nil
}

func compareKnown(maxn int, triangle []*big.Int) int {
	known, err := orchestrator.LoadKnown("fixtures/b006770.txt")
	if err != nil || len(known) <= 1 {
		fmt.Fprintln(os.Stderr, "combine: no known values (run from repo root)")
		return 1
	}
	if orchestrator.CompareToKnown(maxn, triangle, known) {
		fmt.Printf("combine_compare PASS (maxn=%d)\n", maxn)
		return 0
	}
	fmt.Printf("combine_compare FAIL\n")
	return 1
}
