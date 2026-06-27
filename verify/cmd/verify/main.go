// main.go — verify CLI entry point.
//
// Usage:
//   verify --n N [--data-dir DIR] [--workers-dir DIR] [--no-spotcheck] [--verbose]
//
// Exits 0 if all checks pass, 1 if any fail.
// Prints one line per check: "PASS row-sum n=21" or "FAIL crc path/to/run.bin".
package main

import (
	"flag"
	"fmt"
	"os"

	"polyominoes/verify"
)

func main() {
	n := flag.Int("n", 0, "which a(N) to verify (required)")
	dataDir := flag.String("data-dir", "data", "root data directory")
	workersDir := flag.String("workers-dir", "build/ns", "directory containing map_worker (for spotcheck)")
	noSpotcheck := flag.Bool("no-spotcheck", false, "skip the re-run spotcheck")
	verbose := flag.Bool("verbose", false, "print PASS lines too")
	flag.Parse()

	if *n <= 0 {
		fmt.Fprintf(os.Stderr, "verify: --n N is required\n")
		os.Exit(1)
	}

	cfg := verify.Config{
		N:           *n,
		DataDir:     *dataDir,
		WorkersDir:  *workersDir,
		NoSpotcheck: *noSpotcheck,
		Verbose:     *verbose,
	}

	results := verify.Run(cfg)

	anyFail := false
	for _, r := range results {
		switch {
		case r.IsWarn:
			fmt.Printf("WARN %-16s %s\n", r.Check, r.Detail)
		case r.Pass:
			if *verbose {
				fmt.Printf("PASS %-16s %s\n", r.Check, r.Detail)
			}
		default:
			fmt.Printf("FAIL %-16s %s\n", r.Check, r.Detail)
			anyFail = true
		}
	}

	if anyFail {
		os.Exit(1)
	}
}
