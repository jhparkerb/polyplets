// main.go — orchestrate CLI entry point.
//
// Usage:
//   orchestrate [--maxn N] [--fold] [--cores N] [--ram BYTES]
//               [--run-dir DIR] [--spill-dir DIR] [--checkpoint PATH]
//               [--checkpoint-every SECS] [--resume] [--compare]
//               [--workers-dir DIR]
//
// AC-2 gate (parallel == serial):
//   orchestrate --maxn 16 --compare
//
// AC-2 gate (kill+resume):
//   orchestrate --maxn 16 --compare   # kill with SIGTERM mid-run
//   orchestrate --maxn 16 --resume --compare  # resumes from checkpoint
package main

import (
	"context"
	"flag"
	"fmt"
	"os"
	"os/signal"
	"path/filepath"
	"runtime"
	"sort"
	"strconv"
	"strings"
	"syscall"
	"time"

	"polyominoes/orchestrator"
)

func main() {
	maxn := flag.Int("maxn", 16, "max cell count")
	fold := flag.Bool("fold", true, "R1 vertical-mirror fold")
	cores := flag.Int("cores", runtime.NumCPU(), "max parallel workers")
	unitMult := flag.Int("unit-mult", 1, "work units per core (units = cores*unit-mult; concurrency stays cores)")
	ram := flag.Uint64("ram", 128<<20, "map_worker spill budget in bytes")
	counter := flag.String("counter", "u64", "counter width: u64 or u128")
	runDir := flag.String("run-dir", "", "directory for run files (default: auto in /tmp)")
	spillDir := flag.String("spill-dir", "", "directory for map_worker internal spills")
	ckptPath := flag.String("checkpoint", "", "checkpoint path (default: <run-dir>/POLYCKPT)")
	ckptEvery := flag.Float64("checkpoint-every", 30, "checkpoint interval in seconds (0=every column)")
	resume := flag.Bool("resume", false, "resume from checkpoint")
	compare := flag.Bool("compare", false, "compare final total to fixtures/b006770.txt")
	workersDir := flag.String("workers-dir", "", "directory containing map_worker/merge_worker binaries")
	costProfileOut := flag.String("cost-profile-out", "", "emit per-column cost profile here (default: <run-dir>/cost_profile.tsv)")
	costProfileRef := flag.String("cost-profile-ref", "", "reference cost profile to drive the live ETA")
	heightsArg := flag.String("heights", "", "subset of heights to sweep, e.g. 1-12 or 17,19,20 (default: all 1..maxn; for multi-machine split)")
	perHeightOut := flag.String("per-height-out", "", "dir to write per-height h<H>.out rows (for combine + old-engine cross-check)")
	flag.Parse()

	heights, herr := parseHeights(*heightsArg, *maxn)
	if herr != nil {
		fmt.Fprintf(os.Stderr, "orchestrate: --heights: %v\n", herr)
		os.Exit(2)
	}

	pid := os.Getpid()

	// Default directories.
	if *runDir == "" {
		*runDir = fmt.Sprintf("/tmp/ns_orch_%d", pid)
	}
	if *spillDir == "" {
		*spillDir = filepath.Join(*runDir, "spill")
	}
	if *ckptPath == "" {
		*ckptPath = filepath.Join(*runDir, "POLYCKPT")
	}

	if err := os.MkdirAll(*runDir, 0o777); err != nil {
		fmt.Fprintf(os.Stderr, "orchestrate: mkdir %s: %v\n", *runDir, err)
		os.Exit(1)
	}
	if err := os.MkdirAll(*spillDir, 0o777); err != nil {
		fmt.Fprintf(os.Stderr, "orchestrate: mkdir %s: %v\n", *spillDir, err)
		os.Exit(1)
	}

	// Worker binaries.
	bin := orchestrator.WorkerBin{}
	if *workersDir != "" {
		bin.MapWorker = filepath.Join(*workersDir, "map_worker")
		bin.MergeWorker = filepath.Join(*workersDir, "merge_worker")
	} else {
		// Auto-detect: look for build/ns/ relative to the executable's parent
		// or relative to cwd.
		bin = findWorkers()
	}

	rev := gitRev()

	cfg := orchestrator.SweepConfig{
		Maxn:            *maxn,
		Fold:            *fold,
		Cores:           *cores,
		UnitMult:        *unitMult,
		RAM:             *ram,
		CounterWidth:    *counter,
		RunDir:          *runDir,
		SpillDir:        *spillDir,
		CheckpointPath:  *ckptPath,
		CheckpointEvery: time.Duration(float64(time.Second) * *ckptEvery),
		Rev:             rev,
		CostProfileOut:  *costProfileOut,
		CostProfileRef:  *costProfileRef,
		Heights:         heights,
		PerHeightOut:    *perHeightOut,
		Bin:             bin,
	}

	fmt.Printf("orchestrate maxn=%d fold=%v cores=%d unit_mult=%d ram=%d counter=%s run_dir=%s rev=%s\n",
		*maxn, *fold, *cores, *unitMult, *ram, *counter, *runDir, rev)

	// Resume from checkpoint if requested.
	var ckpt *orchestrator.Checkpoint
	if *resume {
		c, err := orchestrator.ReadCheckpoint(*ckptPath)
		if err != nil {
			fmt.Fprintf(os.Stderr, "orchestrate: cannot read checkpoint %s: %v\n", *ckptPath, err)
			os.Exit(1)
		}
		ckpt = c
		fmt.Printf("resuming from H=%d col=%d acct=%s\n", ckpt.H, ckpt.Col, ckpt.Acct)
	}

	// Set up graceful shutdown on SIGTERM/SIGINT.
	ctx, cancel := context.WithCancel(context.Background())
	sigCh := make(chan os.Signal, 1)
	signal.Notify(sigCh, syscall.SIGTERM, syscall.SIGINT)
	go func() {
		sig := <-sigCh
		fmt.Fprintf(os.Stderr, "\norchestrate: received %v — writing checkpoint and stopping\n", sig)
		cancel()
	}()

	t0 := time.Now()
	result, err := orchestrator.Run(ctx, cfg, ckpt)
	wall := time.Since(t0).Seconds()

	if err != nil {
		// Context cancellation = graceful stop with checkpoint; not an error.
		if ctx.Err() == nil {
			fmt.Fprintf(os.Stderr, "orchestrate: %v\n", err)
			os.Exit(1)
		}
		fmt.Printf("orchestrate: stopped (checkpoint written to %s)\n", *ckptPath)
		os.Exit(0)
	}

	fmt.Printf("\nwall=%.1fs %s\n", wall, result.Acct)

	if !*compare {
		return
	}

	// Compare against known a(n) from fixtures.
	known, err := orchestrator.LoadKnown("fixtures/b006770.txt")
	if err != nil || len(known) <= 1 {
		fmt.Fprintln(os.Stderr, "orchestrate: no known values from fixtures/b006770.txt (run from repo root)")
		os.Exit(1)
	}

	allOK := true
	for n := 1; n <= *maxn; n++ {
		got := result.Triangle[n]
		want := uint64(0)
		if n < len(known) {
			want = known[n]
		}
		ok := got == want
		status := "OK"
		if !ok {
			status = "FAIL"
			allOK = false
		}
		fmt.Printf("n=%2d  a(n)=%d  known=%d  %s\n", n, got, want, status)
	}
	if allOK {
		fmt.Printf("gate_parallel PASS (maxn=%d)\n", *maxn)
	} else {
		fmt.Printf("gate_parallel FAIL\n")
		os.Exit(1)
	}
}

// parseHeights parses "1-12", "17,19,20", or "" (= all 1..maxn) into a sorted,
// deduplicated, validated height list.
func parseHeights(arg string, maxn int) ([]int, error) {
	if strings.TrimSpace(arg) == "" {
		return nil, nil // empty = all heights (Run fills 1..maxn)
	}
	seen := map[int]bool{}
	var out []int
	add := func(h int) error {
		if h < 1 || h > maxn {
			return fmt.Errorf("height %d out of range 1..%d", h, maxn)
		}
		if !seen[h] {
			seen[h] = true
			out = append(out, h)
		}
		return nil
	}
	for _, part := range strings.Split(arg, ",") {
		part = strings.TrimSpace(part)
		if part == "" {
			continue
		}
		if lo, hi, ok := strings.Cut(part, "-"); ok {
			a, e1 := strconv.Atoi(strings.TrimSpace(lo))
			b, e2 := strconv.Atoi(strings.TrimSpace(hi))
			if e1 != nil || e2 != nil || a > b {
				return nil, fmt.Errorf("bad range %q", part)
			}
			for h := a; h <= b; h++ {
				if err := add(h); err != nil {
					return nil, err
				}
			}
		} else {
			h, err := strconv.Atoi(part)
			if err != nil {
				return nil, fmt.Errorf("bad height %q", part)
			}
			if err := add(h); err != nil {
				return nil, err
			}
		}
	}
	sort.Ints(out)
	return out, nil
}

func gitRev() string {
	// Best-effort: read from the binary embed if available, else "unknown".
	// The Makefile injects GIT_REV into C++ binaries via -D; Go doesn't have
	// that path, but we can shell out if needed. For M2, "unknown" is fine.
	return "unknown"
}

func findWorkers() orchestrator.WorkerBin {
	// Try build/ns/ relative to cwd, then two levels up (when run from the
	// package dir).  repoRoot "." and "../.." map to those two locations.
	for _, repoRoot := range []string{".", "../.."} {
		bin := orchestrator.DefaultWorkerBin(repoRoot)
		if _, err := os.Stat(bin.MapWorker); err == nil {
			return bin
		}
	}
	// Fall back to PATH lookup.
	return orchestrator.WorkerBin{MapWorker: "map_worker", MergeWorker: "merge_worker"}
}
