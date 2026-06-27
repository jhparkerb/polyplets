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

func main() {
	inArg := flag.String("in", "", "comma-separated dirs containing h<H>.out files (required)")
	maxn := flag.Int("maxn", 0, "max n (required)")
	compare := flag.Bool("compare", false, "compare a(n) to fixtures/b006770.txt")
	requireCover := flag.Bool("require-cover", false, "fail unless heights 1..maxn are all present exactly once")
	out := flag.String("out", "", "write the combined triangle here (n value lines)")
	flag.Parse()

	if *inArg == "" || *maxn == 0 {
		fmt.Fprintln(os.Stderr, "combine: --in and --maxn are required")
		os.Exit(2)
	}

	triangle := make([]uint64, *maxn+1)
	heightSrc := map[int]string{} // H -> first dir that supplied it
	var dup bool

	for _, dir := range strings.Split(*inArg, ",") {
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
				fmt.Fprintf(os.Stderr, "combine: ERROR height %d in both %s and %s (double-count)\n", H, prev, dir)
				dup = true
				continue
			}
			heightSrc[H] = dir
			if err := addRow(p, *maxn, triangle); err != nil {
				fmt.Fprintf(os.Stderr, "combine: %s: %v\n", p, err)
				os.Exit(1)
			}
		}
	}
	if dup {
		os.Exit(1)
	}

	// Coverage report.
	var have []int
	for H := range heightSrc {
		have = append(have, H)
	}
	sort.Ints(have)
	fmt.Printf("combine: %d heights present: %v\n", len(have), have)
	if *requireCover {
		var missing []int
		for H := 1; H <= *maxn; H++ {
			if _, ok := heightSrc[H]; !ok {
				missing = append(missing, H)
			}
		}
		if len(missing) > 0 {
			fmt.Fprintf(os.Stderr, "combine: ERROR missing heights %v\n", missing)
			os.Exit(1)
		}
	}

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

func heightFromName(path string) (int, bool) {
	base := filepath.Base(path)
	base = strings.TrimSuffix(base, ".out")
	if !strings.HasPrefix(base, "h") {
		return 0, false
	}
	H, err := strconv.Atoi(base[1:])
	return H, err == nil
}

// addRow adds one h<H>.out file's "n value" rows into the triangle.
func addRow(path string, maxn int, triangle []uint64) error {
	data, err := os.ReadFile(path)
	if err != nil {
		return err
	}
	for _, line := range strings.Split(string(data), "\n") {
		f := strings.Fields(line)
		if len(f) < 2 {
			continue
		}
		n, e1 := strconv.Atoi(f[0])
		v, e2 := strconv.ParseUint(f[1], 10, 64)
		if e1 != nil || e2 != nil || n < 1 || n > maxn {
			continue
		}
		triangle[n] += v
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
	allOK := true
	for n := 1; n <= maxn; n++ {
		want := uint64(0)
		if n < len(known) {
			want = known[n]
		}
		status := "OK"
		if triangle[n] != want {
			status = "FAIL"
			allOK = false
		}
		fmt.Printf("n=%2d  a(n)=%d  known=%d  %s\n", n, triangle[n], want, status)
	}
	if allOK {
		fmt.Printf("combine_compare PASS (maxn=%d)\n", maxn)
		return 0
	}
	fmt.Printf("combine_compare FAIL\n")
	return 1
}
