// worker.go — spawn map_worker and merge_worker subprocesses.
package orchestrator

import (
	"bufio"
	"bytes"
	"context"
	"fmt"
	"os/exec"
	"path/filepath"
	"strconv"
	"strings"
	"syscall"
)

// WorkerBin holds paths to the compiled worker binaries.
type WorkerBin struct {
	MapWorker   string
	MergeWorker string
	// FusedColumn is the Even Keel D6 per-column fused worker
	// (worker/fused_column.cpp): one process runs a whole column in RAM
	// (seed + H stages + finalize, no inter-stage files). Empty => not
	// wired; sweepHeightKink then uses the map+merge round path.
	FusedColumn string
}

// DefaultWorkerBin returns WorkerBin pointing into build/ns/ relative to dir.
func DefaultWorkerBin(repoRoot string) WorkerBin {
	return WorkerBin{
		MapWorker:   filepath.Join(repoRoot, "build/ns/map_worker"),
		MergeWorker: filepath.Join(repoRoot, "build/ns/merge_worker"),
		FusedColumn: filepath.Join(repoRoot, "build/ns/fused_column"),
	}
}

// FusedColumnArgs is the argument set for one fused_column invocation (Even
// Keel D6 per-column fusion). One call replaces a whole column's seed + H
// stage + finalize rounds.
type FusedColumnArgs struct {
	InPaths   []string // this column's frontier (H+2-keyed)
	H, Maxn   int
	Cores     int
	Fold      bool
	Counter   string // "u64" | "u128"
	Cuts      []string // hex cut keys for partitioning the next frontier
	OutPrefix string   // writes <OutPrefix>_u<b>.bin per range
	Rev       string
	RAM       uint64
}

func fusedColumnArgsTokens(a FusedColumnArgs) []string {
	fold := "0"
	if a.Fold {
		fold = "1"
	}
	toks := []string{
		"--in", strings.Join(a.InPaths, ","),
		"--H", strconv.Itoa(a.H),
		"--maxn", strconv.Itoa(a.Maxn),
		"--cores", strconv.Itoa(a.Cores),
		"--fold", fold,
		"--counter", a.Counter,
		"--out-prefix", a.OutPrefix,
		"--rev", a.Rev,
		"--ram", strconv.FormatUint(a.RAM, 10),
	}
	if len(a.Cuts) > 0 {
		toks = append(toks, "--cuts", strings.Join(a.Cuts, ","))
	}
	return toks
}

// RunFusedColumnWorker spawns a fused_column worker, waits, and returns the
// parsed result (TriContribs from the harvested triangle rows, Acct from
// event=done). Output range files are <OutPrefix>_u<b>.bin.
func RunFusedColumnWorker(ctx context.Context, bin string, a FusedColumnArgs) (WorkerResult, error) {
	return runWorker(ctx, bin, fusedColumnArgsTokens(a), nil, nil)
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
	Kernel   string // "column" (default) or "kink"; empty = column
	Stage    string // kink kernel only: "seed", "finalize", or an int stage index
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
	KeyLen  int // 0 = merge_worker's own H+2 default; kink stage tables pass H+4
}

// mapArgsTokens/mergeArgsTokens build the flag/value argv for map_worker/
// merge_worker from MapArgs/MergeArgs -- the single source of truth for
// this flag set, used both for a one-shot exec.Cmd's args (RunMapWorker/
// RunMergeWorker below) and for the --persistent pool's space-joined
// request line (workerpool.go's mapArgsLine/mergeArgsLine). Previously
// duplicated as two independently-maintained implementations; a field
// added to MapArgs/MergeArgs without updating both would silently drift
// between the one-shot and persistent-pool code paths.
func mapArgsTokens(a MapArgs) []string {
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
	if a.Kernel != "" && a.Kernel != "column" {
		args = append(args, "--kernel", a.Kernel)
	}
	if a.Stage != "" {
		args = append(args, "--stage", a.Stage)
	}
	return args
}

func mergeArgsTokens(a MergeArgs) []string {
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
	if a.KeyLen != 0 {
		args = append(args, "--keylen", fmt.Sprint(a.KeyLen))
	}
	return args
}

// RunMapWorker spawns a map_worker, waits for it, and returns the parsed result.
// onProgress (may be nil) is called with the worker's cumulative processed-record
// count as event=progress lines stream in.
// stop (may be nil) is the work-stealing signal: when it is closed (or receives
// a value), the worker is sent SIGTERM, which it treats as a cooperative stop —
// it finalizes a valid partial output and reports its cursor in result.StopKey.
func RunMapWorker(ctx context.Context, bin WorkerBin, a MapArgs, onProgress func(uint64), stop <-chan struct{}) (WorkerResult, error) {
	return runWorker(ctx, bin.MapWorker, mapArgsTokens(a), onProgress, stop)
}

// RunMergeWorker spawns a merge_worker, waits for it, and returns the parsed
// result. onProgress/stop have the same work-stealing contract as
// RunMapWorker (may be nil): stop closing sends SIGTERM, which merge_worker
// treats as a cooperative early stop, reporting its cursor in
// result.StopKey (Bottleneck: Merge Range Straggler).
func RunMergeWorker(ctx context.Context, bin WorkerBin, a MergeArgs, onProgress func(uint64), stop <-chan struct{}) (WorkerResult, error) {
	return runWorker(ctx, bin.MergeWorker, mergeArgsTokens(a), onProgress, stop)
}

func runWorker(ctx context.Context, binary string, args []string, onProgress func(uint64), stop <-chan struct{}) (WorkerResult, error) {
	cmd := exec.CommandContext(ctx, binary, args...)
	stdout, err := cmd.StdoutPipe()
	if err != nil {
		return WorkerResult{}, err
	}
	// Capture stderr so a worker's failure diagnostic (e.g. "cannot read input")
	// surfaces in the returned error instead of being discarded. Workers write
	// nothing here in normal operation (progress goes to stdout), so this stays
	// small.
	var stderrBuf bytes.Buffer
	cmd.Stderr = &stderrBuf

	if err := cmd.Start(); err != nil {
		return WorkerResult{}, fmt.Errorf("spawn %s: %w", filepath.Base(binary), err)
	}

	// Work-stealing: forward a stop request to the worker as SIGTERM, which it
	// catches as a cooperative early stop (exit 0 with a cursor).  The watcher
	// exits when the process does (done is closed after Wait), so it never leaks.
	done := make(chan struct{})
	if stop != nil {
		go func() {
			select {
			case <-stop:
				_ = cmd.Process.Signal(syscall.SIGTERM)
			case <-done:
			}
		}()
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

	err = cmd.Wait()
	close(done) // release the stop watcher
	if err != nil {
		if diag := strings.TrimSpace(stderrBuf.String()); diag != "" {
			return WorkerResult{}, fmt.Errorf("%s: %w: %s", filepath.Base(binary), err, diag)
		}
		return WorkerResult{}, fmt.Errorf("%s: %w", filepath.Base(binary), err)
	}

	result, perr := ParseWorkerOutput(lines)
	if perr != nil {
		return WorkerResult{}, fmt.Errorf("%s: %w", filepath.Base(binary), perr)
	}
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
