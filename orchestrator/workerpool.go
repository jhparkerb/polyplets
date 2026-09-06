// workerpool.go — persistent map_worker/merge_worker process pools
// (Bottleneck #5: eliminating per-unit fork+exec).
//
// Every map unit and merge range used to spawn a brand-new OS process via
// exec.CommandContext, run for a fraction of a second, and exit -- paying
// real fork+exec+arg-marshal cost on every single work item, thousands of
// times per real run. A heap-alloc profile confirmed os/exec's own
// machinery (SlicePtrFromStrings, dedupEnvCase, Cmd.Start, startProcess)
// as a real, substantial share of total allocation, on top of the direct
// process-creation syscall cost -- not just a hunch, see
// docs/engine-record.md Bottleneck #5.
//
// WorkerPool holds `size` long-lived slots. Each slot lazily starts (at
// most) one persistent map_worker and one persistent merge_worker process
// (both launched with --persistent, worker/{map,merge}_worker.cpp) and
// keeps them alive for the pool's entire lifetime, feeding them one
// whitespace-tokenized request line per unit of work instead of spawning
// fresh. A slot is a single concurrency unit: checking it out for a map
// request and a merge request are mutually exclusive uses of the SAME
// budget, matching the single Cores-wide `sem` channel the exec-per-unit
// path used to share between map and merge (overlap-heights runs both
// concurrently across heights) -- so this preserves the exact same
// concurrency ceiling, not 2x it.
package orchestrator

import (
	"bufio"
	"context"
	"fmt"
	"io"
	"os/exec"
	"strings"
	"sync"
	"syscall"
)

// workerProc is one persistent worker process (either role): its stdin
// (write requests here) and a scanner over its stdout (read responses).
type workerProc struct {
	cmd    *exec.Cmd
	stdin  io.WriteCloser
	scan   *bufio.Scanner
	stderr *syncBuffer
}

func startPersistentWorker(ctx context.Context, binary string) (*workerProc, error) {
	cmd := exec.CommandContext(ctx, binary, "--persistent")
	stdin, err := cmd.StdinPipe()
	if err != nil {
		return nil, err
	}
	stdout, err := cmd.StdoutPipe()
	if err != nil {
		return nil, err
	}
	var stderrBuf syncBuffer
	cmd.Stderr = &stderrBuf
	if err := cmd.Start(); err != nil {
		return nil, fmt.Errorf("spawn persistent %s: %w", binary, err)
	}
	sc := bufio.NewScanner(stdout)
	sc.Buffer(make([]byte, 0, 64*1024), 16*1024*1024) // triangle rows can be wide
	return &workerProc{cmd: cmd, stdin: stdin, scan: sc, stderr: &stderrBuf}, nil
}

// runRequest sends one request line and reads until (and including) the
// event=done line, mirroring runWorker's per-invocation scanning contract
// exactly (event=progress lines feed onProgress and are dropped, everything
// else -- tri rows, event=done -- is collected for ParseWorkerOutput).
// stop, if non-nil, SIGTERMs the underlying process for cooperative early
// stop (work-stealing) -- same mechanism as the one-shot path, just aimed
// at a long-lived process instead of a fresh one; the watcher is scoped to
// this one request so it can't fire against a LATER request reusing the
// same slot.
func (w *workerProc) runRequest(requestLine string, onProgress func(uint64), stop <-chan struct{}) (WorkerResult, error) {
	// Two writes, not one requestLine+"\n" concatenation: the "\n" is a
	// static string literal (zero allocation), while "+" would allocate a
	// fresh copy of the whole line just to append one byte -- real cost at
	// this call frequency (once per work unit), found via a real heap-alloc
	// profile with --persistent-workers enabled.
	if _, err := io.WriteString(w.stdin, requestLine); err != nil {
		return WorkerResult{}, fmt.Errorf("write request: %w", err)
	}
	if _, err := io.WriteString(w.stdin, "\n"); err != nil {
		return WorkerResult{}, fmt.Errorf("write request newline: %w", err)
	}

	done := make(chan struct{})
	if stop != nil {
		go func() {
			select {
			case <-stop:
				_ = w.cmd.Process.Signal(syscall.SIGTERM)
			case <-done:
			}
		}()
	}

	var lines []string
	sawDone := false
	for w.scan.Scan() {
		line := w.scan.Text()
		if onProgress != nil && strings.HasPrefix(line, "event=progress") {
			if n, ok := parseProcessed(line); ok {
				onProgress(n)
			}
			continue
		}
		lines = append(lines, line)
		if strings.HasPrefix(line, "event=done") {
			sawDone = true
			break
		}
	}
	close(done)

	if !sawDone {
		if err := w.scan.Err(); err != nil {
			return WorkerResult{}, fmt.Errorf("persistent worker stream: %w", err)
		}
		diag := strings.TrimSpace(w.stderr.String())
		if diag != "" {
			return WorkerResult{}, fmt.Errorf("persistent worker exited: %s", diag)
		}
		return WorkerResult{}, fmt.Errorf("persistent worker exited without event=done")
	}

	result, perr := ParseWorkerOutput(lines)
	if perr != nil {
		return WorkerResult{}, perr
	}
	return result, nil
}

// signalShutdown sends EOF (the worker's persistent loop exits cleanly on
// stdin close) without blocking for exit. Split from wait() so Close() can
// signal every process before waiting on any of them -- see Close's comment.
func (w *workerProc) signalShutdown() {
	if w == nil {
		return
	}
	_ = w.stdin.Close()
}

func (w *workerProc) wait() {
	if w == nil {
		return
	}
	_ = w.cmd.Wait()
}

// syncBuffer is a mutex-guarded bytes.Buffer substitute (cmd.Stderr is
// written from the process's own OS thread machinery, read from ours).
type syncBuffer struct {
	mu  sync.Mutex
	buf []byte
}

func (b *syncBuffer) Write(p []byte) (int, error) {
	b.mu.Lock()
	defer b.mu.Unlock()
	b.buf = append(b.buf, p...)
	return len(p), nil
}
func (b *syncBuffer) String() string {
	b.mu.Lock()
	defer b.mu.Unlock()
	return string(b.buf)
}

// slot is one pool concurrency unit: at most one live map_worker AND at
// most one live merge_worker (lazily started on first use of each role),
// but checking it out for either role consumes the SAME slot.
type slot struct {
	mapBin, mergeBin string
	mapProc          *workerProc
	mergeProc        *workerProc
}

// WorkerPool manages `size` persistent-worker slots shared across the
// entire Run() call (all heights, all columns, all rounds) -- the same
// scope the old Cores-wide `sem` channel had.
type WorkerPool struct {
	ctx   context.Context
	slots chan *slot
	size  int
}

// NewWorkerPool creates size slots (no processes started yet -- lazy per
// role, per slot, on first use, so a run that only ever does mid-column
// kink stages never pays for an unused merge_worker where merge doesn't
// apply, etc.).
func NewWorkerPool(ctx context.Context, bin WorkerBin, size int) *WorkerPool {
	p := &WorkerPool{ctx: ctx, slots: make(chan *slot, size), size: size}
	for i := 0; i < size; i++ {
		p.slots <- &slot{mapBin: bin.MapWorker, mergeBin: bin.MergeWorker}
	}
	return p
}

// checkout blocks until a slot is available (the pool's own concurrency
// gate -- replaces the old Cores-wide `sem <- struct{}{}`).
func (p *WorkerPool) checkout() *slot {
	return <-p.slots
}
func (p *WorkerPool) checkin(s *slot) {
	p.slots <- s
}

// RunMap sends one map_worker request to a pooled persistent process
// (lazily starting it on this slot if not already running), blocking until
// a slot is free. Same signature/semantics as the old RunMapWorker.
func (p *WorkerPool) RunMap(a MapArgs, onProgress func(uint64), stop <-chan struct{}) (WorkerResult, error) {
	s := p.checkout()
	defer p.checkin(s)
	if s.mapProc == nil {
		proc, err := startPersistentWorker(p.ctx, s.mapBin)
		if err != nil {
			return WorkerResult{}, err
		}
		s.mapProc = proc
	}
	return s.mapProc.runRequest(mapArgsLine(a), onProgress, stop)
}

// RunMerge sends one merge_worker request to a pooled persistent process.
// Same signature/semantics as the old RunMergeWorker, now with the same
// work-stealing onProgress/stop contract as RunMap.
func (p *WorkerPool) RunMerge(a MergeArgs, onProgress func(uint64), stop <-chan struct{}) (WorkerResult, error) {
	s := p.checkout()
	defer p.checkin(s)
	if s.mergeProc == nil {
		proc, err := startPersistentWorker(p.ctx, s.mergeBin)
		if err != nil {
			return WorkerResult{}, err
		}
		s.mergeProc = proc
	}
	return s.mergeProc.runRequest(mergeArgsLine(a), onProgress, stop)
}

// Close tears down every started process (idle slots that never launched a
// worker cost nothing extra to close). Two-phase: signal every process's
// stdin closed FIRST (all children start exiting concurrently in the OS),
// THEN wait on each. A single-phase close-then-wait-per-slot would make
// total shutdown time the SUM of every process's exit latency instead of
// the max -- real, since Close() runs synchronously before the run's wall
// clock is reported (orchestrate/main.go), directly padding the measured
// number on every --persistent-workers run (found via /simplify, not a
// hypothetical: this is a utilization-sensitive branch where that padding
// mattered to what was being measured).
func (p *WorkerPool) Close() {
	slots := make([]*slot, p.size)
	for i := range slots {
		slots[i] = <-p.slots
		slots[i].mapProc.signalShutdown()
		slots[i].mergeProc.signalShutdown()
	}
	for _, s := range slots {
		s.mapProc.wait()
		s.mergeProc.wait()
	}
}

// mapArgsLine/mergeArgsLine space-join mapArgsTokens/mergeArgsTokens
// (worker.go -- the single source of truth for this flag set, shared with
// RunMapWorker/RunMergeWorker's one-shot exec.Cmd args) into one
// --persistent request line.
func mapArgsLine(a MapArgs) string     { return strings.Join(mapArgsTokens(a), " ") }
func mergeArgsLine(a MergeArgs) string { return strings.Join(mergeArgsTokens(a), " ") }
