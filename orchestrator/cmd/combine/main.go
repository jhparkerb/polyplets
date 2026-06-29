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
package main

import (
	"flag"
	"fmt"
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
	flag.Parse()

	if *inArg == "" || *maxn == 0 {
		fmt.Fprintln(os.Stderr, "combine: --in and --maxn are required")
		os.Exit(2)
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

// runCombine sums each dir's h<H>.out rows into the triangle, rejecting a height
// supplied by two dirs (double-count) and — when requireCover — any gap in
// 1..maxn. Returns the triangle and the sorted set of heights present.
func runCombine(dirs []string, maxn int, requireCover bool) (triangle []uint64, have []int, err error) {
	triangle = make([]uint64, maxn+1)
	heightSrc := map[int]string{} // H -> first dir that supplied it

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
			if prev, seen := heightSrc[H]; seen {
				return nil, nil, fmt.Errorf("height %d in both %s and %s (double-count)", H, prev, dir)
			}
			heightSrc[H] = dir
			if e := addRow(p, maxn, triangle); e != nil {
				return nil, nil, fmt.Errorf("%s: %w", p, e)
			}
		}
	}

	for H := range heightSrc {
		have = append(have, H)
	}
	sort.Ints(have)

	if requireCover {
		var missing []int
		for H := 1; H <= maxn; H++ {
			if _, ok := heightSrc[H]; !ok {
				missing = append(missing, H)
			}
		}
		if len(missing) > 0 {
			return nil, nil, fmt.Errorf("missing heights %v", missing)
		}
	}
	return triangle, have, nil
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
func addRow(path string, maxn int, triangle []uint64) error {
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
		v, e2 := strconv.ParseUint(f[1], 10, 64)
		if e1 != nil || e2 != nil || n < 1 {
			continue
		}
		if n > maxn {
			if v != 0 && n > overflowN {
				overflowN = n
			}
			continue
		}
		if n == maxn {
			sawMaxn = true
		}
		if v != 0 {
			nonzero = true
		}
		triangle[n] += v
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

func writeTriangle(path string, maxn int, triangle []uint64) error {
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

func compareKnown(maxn int, triangle []uint64) int {
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
