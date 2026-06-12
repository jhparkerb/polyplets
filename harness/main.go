// CLI for the G3 harness.
//
//	harness run    -dir runs/NAME -binary build/g2 -lattice square8 -maxn 19 \
//	               -split 6 -k 64 -j 8 [-retries 2] [-ledger ledger/ledger.jsonl]
//	harness verify -a runs/A -b runs/B [-ledger ledger/ledger.jsonl]

package main

import (
	"flag"
	"fmt"
	"os"
)

func usage() {
	fmt.Fprintf(os.Stderr, "usage: harness {run|verify} [flags]; -h on a subcommand for details\n")
	os.Exit(2)
}

func main() {
	if len(os.Args) < 2 {
		usage()
	}
	switch os.Args[1] {
	case "run":
		fs := flag.NewFlagSet("run", flag.ExitOnError)
		dir := fs.String("dir", "", "campaign directory (required)")
		ledger := fs.String("ledger", "ledger/ledger.jsonl", "ledger file")
		binary := fs.String("binary", "build/g2", "engine binary")
		lattice := fs.String("lattice", "", "square4|square8|tri6 (required)")
		maxn := fs.Int("maxn", 0, "maximum animal size (required)")
		split := fs.Int("split", 0, "split depth S (required)")
		k := fs.Int("k", 0, "number of split classes / workers (required)")
		j := fs.Int("j", 1, "concurrent workers")
		retries := fs.Int("retries", 1, "retries per worker")
		fs.Parse(os.Args[2:])
		if *dir == "" || *lattice == "" || *maxn < 1 || *split < 1 || *k < 1 {
			fs.Usage()
			os.Exit(2)
		}
		c := &Campaign{Dir: *dir, Ledger: *ledger, Spec: Spec{
			Binary: *binary, Lattice: *lattice, MaxN: *maxn,
			SplitS: *split, K: *k, Retries: *retries, J: *j}}
		if err := c.Run(); err != nil {
			fmt.Fprintf(os.Stderr, "harness run: %v\n", err)
			os.Exit(1)
		}
		fmt.Printf("campaign complete: %s/results.txt\n", *dir)
	case "verify":
		fs := flag.NewFlagSet("verify", flag.ExitOnError)
		a := fs.String("a", "", "first campaign dir (required)")
		b := fs.String("b", "", "second campaign dir (required)")
		ledger := fs.String("ledger", "ledger/ledger.jsonl", "ledger file")
		fs.Parse(os.Args[2:])
		if *a == "" || *b == "" {
			fs.Usage()
			os.Exit(2)
		}
		if err := Verify(*a, *b, *ledger); err != nil {
			fmt.Fprintf(os.Stderr, "harness verify: FAILED: %v\n", err)
			os.Exit(1)
		}
		fmt.Println("verified: campaigns agree")
	default:
		usage()
	}
}
