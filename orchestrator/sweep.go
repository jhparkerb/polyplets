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
	UnitMult        int           // MAP work units per core (default 1); units = Cores*UnitMult, concurrency stays Cores
	MergeMult       int           // MERGE ranges per core (0 = follow UnitMult); set low to cut the (cores*mult)^2 merge fan-in
	OverlapHeights  int           // heights to sweep CONCURRENTLY sharing one Cores-wide pool (0/1 = sequential). Hides one height's low-util merge behind another's map. No mid-run checkpoint in this mode.
	RAM             uint64        // bytes per map_worker spill budget
	RunDir          string        // directory for all run files
	SpillDir        string        // directory for map_worker internal spills
	CheckpointPath  string        // path to write/read POLYCKPT
	CheckpointEvery time.Duration // wall cadence for checkpoints (0 = every column)
	Rev             string        // git rev for POLYRUN headers
	CounterWidth    string        // "u64" or "u128"; empty = default (u64)
	CostProfileOut  string        // where to emit the cost profile (default: <RunDir>/cost_profile.tsv)
	CostProfileRef  string        // optional reference profile to drive the live ETA
	Heights         []int         // subset of heights to sweep (empty = 1..Maxn); for multi-machine split
	PerHeightOut    string        // dir to write per-height h<H>.out files (empty = none)
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

	// Heights to sweep: an explicit subset (multi-machine split) or all 1..maxn.
	heights := cfg.Heights
	if len(heights) == 0 {
		heights = make([]int, 0, maxn)
		for H := 1; H <= maxn; H++ {
			heights = append(heights, H)
		}
	}

	startIdx := 0
	if resume != nil {
		acct = resume.Acct
		// Restore the accumulated triangle from the checkpoint.
		for n, v := range resume.Triangle {
			if n <= maxn {
				triangle[n] = v
			}
		}
		// Resume at the list position matching the checkpoint height.
		for i, H := range heights {
			if H == resume.H {
				startIdx = i
				break
			}
		}
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

	tel, err := newTelemetry(cfg, time.Now())
	if err != nil {
		return nil, err
	}

	// Shared Cores-wide worker pool. In overlap mode several heights draw from it
	// concurrently, so a height's low-utilization merge phase runs alongside
	// another's map phase rather than idling the box.
	sem := make(chan struct{}, cfg.Cores)

	if cfg.OverlapHeights > 1 {
		return runOverlap(ctx, cfg, heights[startIdx:], triangle, acct, tel, sem)
	}

	for hi := startIdx; hi < len(heights); hi++ {
		H := heights[hi]
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

		hTri, hAcct, err := sweepHeight(ctx, cfg, H, startCol, frontier, writeCheckpoint, tel, sem)

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

		// Per-height row (multi-machine combine + direct cross-check vs the old
		// engine's h<H>.out). Written only on a fully completed height.
		if cfg.PerHeightOut != "" {
			if werr := writePerHeight(cfg.PerHeightOut, H, maxn, hTri); werr != nil {
				fmt.Fprintf(os.Stderr, "per-height write H=%d: %v\n", H, werr)
			}
		}
	}

	return &SweepResult{Triangle: triangle, Acct: acct}, nil
}

// runOverlap sweeps heights CONCURRENTLY — cfg.OverlapHeights at a time, all
// drawing from the single Cores-wide pool `sem` — so one height's
// low-utilization merge phase overlaps another height's map phase instead of
// idling cores. Heights are independent, so the totals are identical to the
// sequential path; results accumulate under `mu`. No mid-run checkpoint here
// (resuming K in-flight heights is deferred): on failure, re-run. This is the
// throughput/benchmark path; the sequential Run loop stays the resumable
// production path. Caller guarantees cfg.OverlapHeights >= 2.
func runOverlap(ctx context.Context, cfg SweepConfig, heights []int,
	triangle []uint64, acct Acct, tel *telemetry, sem chan struct{}) (*SweepResult, error) {

	var mu sync.Mutex
	var firstErr error
	noopCkpt := func(int, int, []string, []uint64) {} // overlap mode: no mid-run checkpoint
	heightSem := make(chan struct{}, cfg.OverlapHeights)
	var wg sync.WaitGroup

	for _, H := range heights {
		wg.Add(1)
		go func(H int) {
			defer wg.Done()
			select {
			case heightSem <- struct{}{}:
			case <-ctx.Done():
				return
			}
			defer func() { <-heightSem }()

			seed := filepath.Join(cfg.RunDir, fmt.Sprintf("seed_h%d.bin", H))
			if err := WriteSeedPolyrun(seed, cfg.Rev, H, cfg.Maxn, cfg.CounterWidth); err != nil {
				mu.Lock()
				if firstErr == nil {
					firstErr = fmt.Errorf("H=%d seed: %w", H, err)
				}
				mu.Unlock()
				return
			}
			hTri, hAcct, err := sweepHeight(ctx, cfg, H, 0, []string{seed}, noopCkpt, tel, sem)

			mu.Lock()
			for n, v := range hTri {
				if n >= 0 && n <= cfg.Maxn {
					triangle[n] += v
				}
			}
			acct.Add(hAcct)
			if err != nil && firstErr == nil {
				firstErr = fmt.Errorf("H=%d: %w", H, err)
			}
			mu.Unlock()
			if err != nil {
				return
			}
			if cfg.PerHeightOut != "" {
				if werr := writePerHeight(cfg.PerHeightOut, H, cfg.Maxn, hTri); werr != nil {
					fmt.Fprintf(os.Stderr, "per-height write H=%d: %v\n", H, werr)
				}
			}
		}(H)
	}
	wg.Wait()
	if firstErr != nil {
		return nil, firstErr
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
	tel *telemetry,
	sem chan struct{},
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

	// frontierIn is this column's map input size. It equals the previous
	// column's frontier_out (totalRecs), so we read headers only once (the seed
	// or resume frontier) and carry the count forward — no per-column re-read.
	frontierIn := sumFrontierRecords(frontier)

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

		colStart := time.Now()
		stopHB := tel.startColumn(H, col)

		// MAP PHASE
		mapOuts, triContribs, mapAcct, err := mapPhase(ctx, cfg, H, col, frontier, tel, sem)
		if err != nil {
			stopHB()
			// hTri does NOT yet include current col's contributions.
			writeCheckpoint(H, col-1, frontier, hTri)
			return hTri, acct, fmt.Errorf("H=%d col=%d map: %w", H, col, err)
		}
		acct.Add(mapAcct)
		mapWall := time.Since(colStart).Seconds()
		mergeStart := time.Now()

		// MERGE PHASE (frontier files still alive — not GC'd yet).
		// Accumulate triContribs ONLY after merge succeeds, so that if merge
		// fails (or is cancelled), the checkpoint at col-1 has correct hTri.
		// A failed merge causes us to checkpoint at col-1 with unchanged hTri;
		// the resume will re-run this col from scratch.
		mergeOuts, totalRecs, mergeAcct, err := mergePhase(ctx, cfg, H, col, mapOuts, sem)
		stopHB()
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

		// Per-column telemetry: orchestrator wall-clock for this column's
		// map+merge, with frontier sizes for the cost model and live ETA.
		mergeWall := time.Since(mergeStart).Seconds()
		colWall := time.Since(colStart).Seconds()
		var colAcct Acct
		colAcct.Add(mapAcct)
		colAcct.Add(mergeAcct)
		tel.observe(ColumnCost{
			H: H, Col: col,
			FrontierIn:  frontierIn,
			FrontierOut: totalRecs,
			WallS:       colWall,
			CPUS:        colAcct.CPUS,
			RSSMax:      colAcct.RSSMax,
			MapWallS:     mapWall,
			MapCPUS:      mapAcct.CPUS,
			MergeWallS:   mergeWall,
			MergeCPUS:    mergeAcct.CPUS,
			NMapUnits:    len(mapOuts),
			NMergeRanges: len(mergeOuts),
		})
		frontierIn = totalRecs // next column's input = this column's output

		if totalRecs == 0 {
			// Height exhausted: write a "height-done" checkpoint with nil frontier
			// BEFORE GC so the stale per-column checkpoint (which named oldFrontier
			// files) is superseded before those files are deleted.
			forwardCheckpoint(col, nil)
			for _, p := range oldFrontier {
				removeRun(p)
			}
			for _, p := range oldMapOuts {
				removeRun(p)
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
			removeRun(p)
		}
		for _, p := range oldMapOuts {
			removeRun(p)
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
	tel *telemetry,
	sem chan struct{},
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

	// sem (the Cores-wide worker pool) is shared across concurrently-running
	// heights in overlap mode, so the global core budget is respected.
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
			r, err := RunMapWorker(ctx, cfg.Bin, a, tel.progressFunc())
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
			removeRun(ur.outPath)
		}
		triContribs = append(triContribs, ur.result.TriContribs)
		acct.Add(ur.result.Acct)
		// Per-unit cost trace for scheduling research (#32/LPT): result-invariant,
		// gated off by default so production logs stay clean. Records the unit's
		// key-range and measured cost to test whether per-unit cost is predictable
		// (e.g. column-to-column by key region).
		if os.Getenv("POLY_UNIT_LOG") != "" {
			fmt.Printf("event=unit H=%d col=%d u=%d lo=%s hi=%s out_records=%d cpu_s=%.3f wall_s=%.3f\n",
				H, col, ur.idx, los[ur.idx], his[ur.idx],
				ur.result.OutRecords, ur.result.Acct.CPUS, ur.result.Acct.WallS)
		}
	}
	return outPaths, triContribs, acct, nil
}

// mergePhase merges all map outputs into a new frontier via parallel merge workers.
func mergePhase(
	ctx context.Context,
	cfg SweepConfig,
	H, col int,
	mapOuts []string,
	sem chan struct{},
) ([]string, uint64, Acct, error) {

	if len(mapOuts) == 0 {
		return nil, 0, Acct{}, nil
	}

	numRanges := cfg.Cores * mergeMult(cfg)
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

	// sem (the Cores-wide worker pool) is shared across concurrently-running
	// heights in overlap mode; here one height's merge can fill cores a
	// concurrent height's map phase has freed.
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
			removeRun(rr.outPath)
		}
		acct.Add(rr.result.Acct)
	}
	return outPaths, totalRecs, acct, nil
}

// writePerHeight writes one height's T(n,H) row to <dir>/h<H>.out as "n value"
// lines for n=1..maxn (matching the old engine's per-height output, so the two
// can be byte-compared cell by cell).
func writePerHeight(dir string, H, maxn int, hTri []uint64) error {
	if err := os.MkdirAll(dir, 0o777); err != nil {
		return err
	}
	path := filepath.Join(dir, fmt.Sprintf("h%d.out", H))
	tmp := path + ".tmp"
	f, err := os.Create(tmp)
	if err != nil {
		return err
	}
	for n := 1; n <= maxn; n++ {
		var v uint64
		if n < len(hTri) {
			v = hTri[n]
		}
		if _, err := fmt.Fprintf(f, "%d %d\n", n, v); err != nil {
			f.Close()
			return err
		}
	}
	if err := f.Close(); err != nil {
		return err
	}
	return os.Rename(tmp, path)
}

// sumFrontierRecords totals the record counts across frontier run files, read
// cheaply from POLYRUN headers (no body scan).  Used as the per-column input
// size for the cost model.
func sumFrontierRecords(frontier []string) uint64 {
	var n uint64
	for _, p := range frontier {
		hdr, _, err := ParseHeader(p)
		if err != nil {
			continue
		}
		n += hdr.Records
	}
	return n
}

// removeRun deletes a run file together with its sparse-index sidecar (if any).
func removeRun(p string) {
	os.Remove(p)
	os.Remove(p + ".idx")
}

// unitMult returns the configured MAP units-per-core, defaulting to 1.
func unitMult(cfg SweepConfig) int {
	if cfg.UnitMult < 1 {
		return 1
	}
	return cfg.UnitMult
}

// mergeMult returns the MERGE ranges-per-core. It follows --unit-mult unless
// MergeMult is set, letting map run at high granularity (fill cores) while merge
// runs at low granularity (fewer ranges → less (cores*mult)^2 fan-in I/O).
func mergeMult(cfg SweepConfig) int {
	if cfg.MergeMult >= 1 {
		return cfg.MergeMult
	}
	return unitMult(cfg)
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
