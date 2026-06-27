// sweep.go — column-sweep orchestrator: parallel map+merge per column, checkpoint.
//
// One height at a time (H=1..maxn).  Within a height-sweep each column is:
//   1. Partition source key-space → map units (one unit per worker).
//   2. Run map_worker per unit in parallel (pool of ≤ cores goroutines).
//   3. Sample output key-space → merge ranges (one per worker).
//   4. Run merge_worker per range in parallel.
//   5. GC consumed runs.  Write checkpoint.  Repeat.
package orchestrator

import (
	"context"
	"fmt"
	"os"
	"path/filepath"
	"sync"
	"time"
)

// SweepConfig holds all parameters for a height-sweep run.
type SweepConfig struct {
	Maxn            int
	Fold            bool
	Cores           int           // max concurrent workers
	UnitMult        int           // work units per core (default 1); units = Cores*UnitMult, concurrency stays Cores
	RAM             uint64        // bytes per map_worker spill budget
	RunDir          string        // directory for all run files
	SpillDir        string        // directory for map_worker internal spills
	CheckpointPath  string        // path to write/read POLYCKPT
	CheckpointEvery time.Duration // wall cadence for checkpoints (0 = every column)
	Rev             string        // git rev for POLYRUN headers
	CounterWidth    string        // "u64" or "u128"; empty = default (u64)
	Bin             WorkerBin

	// afterColumn, if non-nil, is called after each forward checkpoint is
	// written (one per completed column, plus the height-done checkpoint).
	// Unexported test seam: cmd/orchestrate (package main) cannot set it, so
	// it is invisible to the production CLI.  resume_test.go uses it to cancel
	// the run at each successive checkpoint boundary and assert that resuming
	// from there reproduces the serial result.
	afterColumn func(H, col int)
}

// SweepResult is the output of a complete run over all heights.
type SweepResult struct {
	Triangle []uint64 // Triangle[n] = Σ_H T(n,H)
	Acct     Acct
}

// Run executes the full height-sweep (H=1..maxn) and returns the triangle.
// If resume is non-nil, it skips already-completed heights and restores acct.
func Run(ctx context.Context, cfg SweepConfig, resume *Checkpoint) (*SweepResult, error) {
	maxn := cfg.Maxn
	triangle := make([]uint64, maxn+1)
	var acct Acct

	startH := 1
	if resume != nil {
		acct = resume.Acct
		// Restore the accumulated triangle from the checkpoint.
		for n, v := range resume.Triangle {
			if n <= maxn {
				triangle[n] = v
			}
		}
		startH = resume.H
	}

	// writeCheckpoint writes a POLYCKPT with the outer triangle + the current
	// height's partial contributions (hTri).  Both are needed: the outer triangle
	// holds completed heights; hTri holds the current height's progress so far.
	writeCheckpoint := func(H, col int, frontier []string, hTri []uint64) {
		// Combine outer accumulated triangle with current height's contribution.
		combined := make([]uint64, len(triangle))
		copy(combined, triangle)
		for n, v := range hTri {
			if n < len(combined) {
				combined[n] += v
			}
		}
		ck := &Checkpoint{
			H:        H,
			Col:      col,
			Frontier: frontier,
			Triangle: combined,
			Acct:     acct,
		}
		if err := ck.Write(cfg.CheckpointPath); err != nil {
			fmt.Fprintf(os.Stderr, "checkpoint write: %v\n", err)
		}
	}

	for H := startH; H <= maxn; H++ {
		startCol := 0
		var frontier []string

		if resume != nil && H == resume.H {
			startCol = resume.Col + 1
			frontier = resume.Frontier
			resume = nil
		} else {
			seed := filepath.Join(cfg.RunDir, fmt.Sprintf("seed_h%d.bin", H))
			if err := WriteSeedPolyrun(seed, cfg.Rev, H, maxn, cfg.CounterWidth); err != nil {
				return nil, fmt.Errorf("H=%d: write seed: %w", H, err)
			}
			frontier = []string{seed}
		}

		hTri, hAcct, err := sweepHeight(ctx, cfg, H, startCol, frontier, writeCheckpoint)

		// Accumulate this height's contributions before handling the error,
		// so the checkpoint written on cancellation includes them.
		for n, v := range hTri {
			if n <= maxn {
				triangle[n] += v
			}
		}
		acct.Add(hAcct)

		if err != nil {
			return nil, err
		}
	}

	return &SweepResult{Triangle: triangle, Acct: acct}, nil
}

// sweepHeight sweeps one height H from startCol.
// Returns the triangle contributions from this height, accumulated accounting,
// and any error (ctx.Err() on cancellation).
// writeCheckpoint is called with (H, col, frontier, hTri) after each completed
// column; it combines the outer triangle with hTri before writing POLYCKPT.
func sweepHeight(
	ctx context.Context,
	cfg SweepConfig,
	H, startCol int,
	frontier []string,
	writeCheckpoint func(H, col int, frontier []string, hTri []uint64),
) ([]uint64, Acct, error) {

	hTri := make([]uint64, cfg.Maxn+1) // contributions from this height only
	var acct Acct
	lastCkpt := time.Now()

	// forwardCheckpoint writes a checkpoint at a completed-column boundary and
	// fires the afterColumn test seam.  Every forward (non-error) checkpoint
	// goes through here, so the seam can never drift out of sync with a new
	// call site; the cancel/error paths call writeCheckpoint directly and
	// deliberately skip the notification (the test drives cancellation through
	// afterColumn, so notifying there would recurse).
	forwardCheckpoint := func(col int, frontier []string) {
		writeCheckpoint(H, col, frontier, hTri)
		if cfg.afterColumn != nil {
			cfg.afterColumn(H, col)
		}
	}

	for col := startCol; col <= cfg.Maxn; col++ {
		if len(frontier) == 0 {
			break
		}

		// Check for cancellation before each column.
		select {
		case <-ctx.Done():
			writeCheckpoint(H, col-1, frontier, hTri)
			return hTri, acct, ctx.Err()
		default:
		}

		// MAP PHASE
		mapOuts, triContribs, mapAcct, err := mapPhase(ctx, cfg, H, col, frontier)
		if err != nil {
			// hTri does NOT yet include current col's contributions.
			writeCheckpoint(H, col-1, frontier, hTri)
			return hTri, acct, fmt.Errorf("H=%d col=%d map: %w", H, col, err)
		}
		acct.Add(mapAcct)

		// MERGE PHASE (frontier files still alive — not GC'd yet).
		// Accumulate triContribs ONLY after merge succeeds, so that if merge
		// fails (or is cancelled), the checkpoint at col-1 has correct hTri.
		// A failed merge causes us to checkpoint at col-1 with unchanged hTri;
		// the resume will re-run this col from scratch.
		mergeOuts, totalRecs, mergeAcct, err := mergePhase(ctx, cfg, H, col, mapOuts)
		if err != nil {
			// hTri does NOT include current col's contributions.
			writeCheckpoint(H, col-1, frontier, hTri)
			return hTri, acct, fmt.Errorf("H=%d col=%d merge: %w", H, col, err)
		}
		acct.Add(mergeAcct)

		// Both map and merge succeeded: now accumulate this col's contributions.
		for _, hm := range triContribs {
			for _, nm := range hm {
				for n, v := range nm {
					if n >= 0 && n <= cfg.Maxn {
						hTri[n] += v
					}
				}
			}
		}

		oldFrontier := frontier
		oldMapOuts := mapOuts
		frontier = mergeOuts

		// totalRecs is the new frontier's record count, summed by the merge
		// workers (no re-read of the files they just wrote).
		fmt.Printf("H=%d col=%d frontier_records=%d acct=%s\n", H, col, totalRecs, acct)

		if totalRecs == 0 {
			// Height exhausted: write a "height-done" checkpoint with nil frontier
			// BEFORE GC so the stale per-column checkpoint (which named oldFrontier
			// files) is superseded before those files are deleted.
			forwardCheckpoint(col, nil)
			for _, p := range oldFrontier {
				os.Remove(p)
			}
			for _, p := range oldMapOuts {
				os.Remove(p)
			}
			frontier = nil
			break
		}

		// Write per-column checkpoint BEFORE GC so resume can always find the frontier.
		// Include hTri so the current height's in-progress contributions are saved.
		interval := cfg.CheckpointEvery
		if interval == 0 || time.Since(lastCkpt) >= interval {
			forwardCheckpoint(col, frontier)
			lastCkpt = time.Now()
		}

		// GC only after checkpoint is written.
		for _, p := range oldFrontier {
			os.Remove(p)
		}
		for _, p := range oldMapOuts {
			os.Remove(p)
		}
	}

	return hTri, acct, nil
}

// mapPhase runs one map_worker per key-range unit in parallel.
func mapPhase(
	ctx context.Context,
	cfg SweepConfig,
	H, col int,
	frontier []string,
) ([]string, []map[int]map[int]uint64, Acct, error) {

	// Units are decoupled from concurrency: numUnits = Cores*UnitMult finer
	// key-ranges, but the semaphore below still caps concurrency at Cores.
	// Finer units let a core that finishes early pull the next queued unit
	// instead of idling to the barrier (approximates work-stealing).
	numUnits := cfg.Cores * unitMult(cfg)
	if numUnits < 1 {
		numUnits = 1
	}

	cuts, err := SampleKeysMulti(frontier, H, numUnits-1)
	if err != nil {
		return nil, nil, Acct{}, err
	}
	los, his := cutsToBounds(cuts)
	actualUnits := len(los)

	type unitResult struct {
		idx     int
		outPath string
		result  WorkerResult
		err     error
	}
	results := make([]unitResult, actualUnits)

	sem := make(chan struct{}, cfg.Cores)
	var wg sync.WaitGroup
	for i := 0; i < actualUnits; i++ {
		wg.Add(1)
		go func(idx int) {
			defer wg.Done()
			sem <- struct{}{}
			defer func() { <-sem }()

			outPath := filepath.Join(cfg.RunDir,
				fmt.Sprintf("map_h%d_c%d_u%d.bin", H, col, idx))
			a := MapArgs{
				InPaths:  frontier,
				H:        H,
				Maxn:     cfg.Maxn,
				Fold:     cfg.Fold,
				RAM:      cfg.RAM,
				SpillDir: cfg.SpillDir,
				OutPath:  outPath,
				Counter:  cfg.CounterWidth,
				LoHex:    los[idx],
				HiHex:    his[idx],
				Rev:      cfg.Rev,
			}
			r, err := RunMapWorker(ctx, cfg.Bin, a)
			results[idx] = unitResult{idx: idx, outPath: outPath, result: r, err: err}
		}(i)
	}
	wg.Wait()

	var outPaths []string
	var triContribs []map[int]map[int]uint64
	var acct Acct
	for _, ur := range results {
		if ur.err != nil {
			return nil, nil, Acct{}, fmt.Errorf("unit %d: %w", ur.idx, ur.err)
		}
		if ur.result.OutRecords > 0 {
			outPaths = append(outPaths, ur.outPath)
		} else {
			os.Remove(ur.outPath)
		}
		triContribs = append(triContribs, ur.result.TriContribs)
		acct.Add(ur.result.Acct)
	}
	return outPaths, triContribs, acct, nil
}

// mergePhase merges all map outputs into a new frontier via parallel merge workers.
func mergePhase(
	ctx context.Context,
	cfg SweepConfig,
	H, col int,
	mapOuts []string,
) ([]string, uint64, Acct, error) {

	if len(mapOuts) == 0 {
		return nil, 0, Acct{}, nil
	}

	numRanges := cfg.Cores * unitMult(cfg)
	if numRanges < 1 {
		numRanges = 1
	}
	if numRanges > len(mapOuts) {
		numRanges = len(mapOuts)
	}

	cuts, err := SampleKeysMulti(mapOuts, H, numRanges-1)
	if err != nil {
		return nil, 0, Acct{}, err
	}
	los, his := cutsToBounds(cuts)
	actualRanges := len(los)

	type rangeResult struct {
		idx     int
		outPath string
		result  WorkerResult
		err     error
	}
	results := make([]rangeResult, actualRanges)

	sem := make(chan struct{}, cfg.Cores)
	var wg sync.WaitGroup
	for i := 0; i < actualRanges; i++ {
		wg.Add(1)
		go func(idx int) {
			defer wg.Done()
			sem <- struct{}{}
			defer func() { <-sem }()

			outPath := filepath.Join(cfg.RunDir,
				fmt.Sprintf("merge_h%d_c%d_r%d.bin", H, col, idx))
			a := MergeArgs{
				InPaths: mapOuts,
				H:       H,
				OutPath: outPath,
				Counter: cfg.CounterWidth,
				KLoHex:  los[idx],
				KHiHex:  his[idx],
				Rev:     cfg.Rev,
			}
			r, err := RunMergeWorker(ctx, cfg.Bin, a)
			results[idx] = rangeResult{idx: idx, outPath: outPath, result: r, err: err}
		}(i)
	}
	wg.Wait()

	var outPaths []string
	var totalRecs uint64
	var acct Acct
	for _, rr := range results {
		if rr.err != nil {
			return nil, 0, Acct{}, fmt.Errorf("merge range %d: %w", rr.idx, rr.err)
		}
		if rr.result.OutRecords > 0 {
			outPaths = append(outPaths, rr.outPath)
			totalRecs += rr.result.OutRecords
		} else {
			os.Remove(rr.outPath)
		}
		acct.Add(rr.result.Acct)
	}
	return outPaths, totalRecs, acct, nil
}

// unitMult returns the configured units-per-core, defaulting to 1.
func unitMult(cfg SweepConfig) int {
	if cfg.UnitMult < 1 {
		return 1
	}
	return cfg.UnitMult
}

// cutsToBounds turns N-1 sorted cut keys into N (lo,hi) hex bounds: unit i
// covers [los[i], his[i]), with open ends ("") at the extremes.
func cutsToBounds(cuts []string) (los, his []string) {
	los = make([]string, len(cuts)+1)
	his = make([]string, len(cuts)+1)
	for i, c := range cuts {
		his[i] = c
		los[i+1] = c
	}
	return los, his
}
