// worker.go — spawn map_worker and merge_worker subprocesses.
package orchestrator

import (
	"bufio"
	"context"
	"fmt"
	"os/exec"
	"path/filepath"
	"strconv"
	"strings"
)

// WorkerBin holds paths to the compiled worker binaries.
type WorkerBin struct {
	MapWorker   string
	MergeWorker string
}

// DefaultWorkerBin returns WorkerBin pointing into build/ns/ relative to dir.
func DefaultWorkerBin(repoRoot string) WorkerBin {
	return WorkerBin{
		MapWorker:   filepath.Join(repoRoot, "build/ns/map_worker"),
		MergeWorker: filepath.Join(repoRoot, "build/ns/merge_worker"),
	}
}

// MapArgs is the full argument set for one map_worker invocation.
type MapArgs struct {
	InPaths  []string // comma-joined on the CLI
	H        int
	Maxn     int
	Fold     bool
	RAM      uint64 // bytes
	SpillDir string
	OutPath  string
	Counter  string // "u64" or "u128"; empty = default (u64)
	LoHex    string // empty = no lower bound
	HiHex    string // empty = no upper bound
	Rev      string
}

// MergeArgs is the full argument set for one merge_worker invocation.
type MergeArgs struct {
	InPaths []string
	H       int
	OutPath string
	Counter string // "u64" or "u128"; empty = default (u64)
	KLoHex  string
	KHiHex  string
	Rev     string
}

// RunMapWorker spawns a map_worker, waits for it, and returns the parsed result.
// onProgress (may be nil) is called with the worker's cumulative processed-record
// count as event=progress lines stream in.
func RunMapWorker(ctx context.Context, bin WorkerBin, a MapArgs, onProgress func(uint64)) (WorkerResult, error) {
	fold := "0"
	if a.Fold {
		fold = "1"
	}
	args := []string{
		"--in", strings.Join(a.InPaths, ","),
		"--H", fmt.Sprint(a.H),
		"--maxn", fmt.Sprint(a.Maxn),
		"--fold", fold,
		"--ram", fmt.Sprint(a.RAM),
		"--spill", a.SpillDir,
		"--out", a.OutPath,
	}
	if a.Counter != "" {
		args = append(args, "--counter", a.Counter)
	}
	if a.LoHex != "" {
		args = append(args, "--lo", a.LoHex)
	}
	if a.HiHex != "" {
		args = append(args, "--hi", a.HiHex)
	}
	if a.Rev != "" {
		args = append(args, "--rev", a.Rev)
	}
	return runWorker(ctx, bin.MapWorker, args, onProgress)
}

// RunMergeWorker spawns a merge_worker, waits for it, and returns the parsed result.
func RunMergeWorker(ctx context.Context, bin WorkerBin, a MergeArgs) (WorkerResult, error) {
	args := []string{
		"--in", strings.Join(a.InPaths, ","),
		"--H", fmt.Sprint(a.H),
		"--out", a.OutPath,
	}
	if a.Counter != "" {
		args = append(args, "--counter", a.Counter)
	}
	if a.KLoHex != "" {
		args = append(args, "--klo", a.KLoHex)
	}
	if a.KHiHex != "" {
		args = append(args, "--khi", a.KHiHex)
	}
	if a.Rev != "" {
		args = append(args, "--rev", a.Rev)
	}
	return runWorker(ctx, bin.MergeWorker, args, nil)
}

func runWorker(ctx context.Context, binary string, args []string, onProgress func(uint64)) (WorkerResult, error) {
	cmd := exec.CommandContext(ctx, binary, args...)
	stdout, err := cmd.StdoutPipe()
	if err != nil {
		return WorkerResult{}, err
	}
	cmd.Stderr = nil // discard stderr (workers write diagnostics there)

	if err := cmd.Start(); err != nil {
		return WorkerResult{}, fmt.Errorf("spawn %s: %w", filepath.Base(binary), err)
	}

	// Stream stdout live: event=progress lines feed onProgress and are NOT
	// retained; everything else (tri rows, event=done) is collected for parsing.
	var lines []string
	sc := bufio.NewScanner(stdout)
	for sc.Scan() {
		line := sc.Text()
		if onProgress != nil && strings.HasPrefix(line, "event=progress") {
			if n, ok := parseProcessed(line); ok {
				onProgress(n)
			}
			continue
		}
		lines = append(lines, line)
	}

	if err := cmd.Wait(); err != nil {
		return WorkerResult{}, fmt.Errorf("%s: %w", filepath.Base(binary), err)
	}

	result := ParseWorkerOutput(lines)
	return result, nil
}

// parseProcessed extracts the cumulative processed count from an event=progress
// line: "event=progress processed=<N> elapsed_s=<t>".
func parseProcessed(line string) (uint64, bool) {
	for _, f := range strings.Fields(line) {
		if v, ok := strings.CutPrefix(f, "processed="); ok {
			n, err := strconv.ParseUint(v, 10, 64)
			return n, err == nil
		}
	}
	return 0, false
}
