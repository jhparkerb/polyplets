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
	"sync/atomic"
	"time"
)

// SweepConfig holds all parameters for a height-sweep run.
type SweepConfig struct {
	Maxn            int
	Fold            bool
	Cores           int           // max concurrent workers
	UnitMult        int           // MAP work units per core (default 1); units = Cores*UnitMult, concurrency stays Cores
	MergeMult       int           // MERGE ranges per core (0 = follow UnitMult); set low to cut the (cores*mult)^2 merge fan-in
	StealGrain      float64       // map work-stealing grain as a fraction of a core's fair share (0 = off; design sweet spot ≈ 0.05). When a core idles in the column tail, the longest-remaining unit is stopped at a cursor and its remainder split across idle cores.
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

// counterName normalizes a counter-width tag, mapping "" to the u64 default.
func counterName(c string) string {
	if c == "" {
		return "u64"
	}
	return c
}

// checkResumeConfig hard-fails a resume whose checkpoint was written under a
// different run config. A mismatched --maxn/--counter/--fold silently corrupts
// the triangle (B1); a --heights list that no longer contains the checkpoint
// height makes startIdx fall back to 0 and re-sweep completed heights, double-
// counting (B7). Both must abort rather than produce a wrong answer.
func checkResumeConfig(cfg SweepConfig, resume *Checkpoint, heights []int) error {
	if resume == nil {
		return nil
	}
	if resume.Maxn != cfg.Maxn {
		return fmt.Errorf("resume: checkpoint maxn=%d != --maxn %d", resume.Maxn, cfg.Maxn)
	}
	if want, got := counterName(cfg.CounterWidth), counterName(resume.Counter); got != want {
		return fmt.Errorf("resume: checkpoint counter=%s != --counter %s", got, want)
	}
	if resume.Fold != cfg.Fold {
		return fmt.Errorf("resume: checkpoint fold=%v != --fold %v", resume.Fold, cfg.Fold)
	}
	for _, H := range heights {
		if H == resume.H {
			return nil
		}
	}
	return fmt.Errorf("resume: checkpoint H=%d not in --heights %v (would re-sweep from the start and double-count)", resume.H, heights)
}

// Run executes the full height-sweep (H=1..maxn) and returns the triangle.
// If resume is non-nil, it skips already-completed heights and restores acct.
func Run(ctx context.Context, cfg SweepConfig, resume *Checkpoint) (*SweepResult, error) {
	// Refuse-at-start: a cap-0 worker pool spawns no goroutines and silently
	// undercounts (firstErr stays nil); a negative cap panics later. Reject both
	// here with one check rather than miscount or crash mid-run.
	if cfg.Cores < 1 {
		return nil, fmt.Errorf("Cores must be >= 1, got %d", cfg.Cores)
	}

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

	if err := checkResumeConfig(cfg, resume, heights); err != nil {
		return nil, err
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
			Maxn:     cfg.Maxn,
			Counter:  counterName(cfg.CounterWidth),
			Fold:     cfg.Fold,
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

		// Top strip H==maxn is the closed-form diagonal T(maxn,maxn)=3^(maxn-1);
		// contribute it directly — no map/merge (see contributeTopHeight).
		if H == maxn {
			contributeTopHeight(maxn, triangle, cfg)
			continue
		}

		// Pole strip H==maxn-1 is closed-form (C1, proven); contribute it
		// directly — it is ~24% of run wall. (maxn>=4 keeps H=maxn-1>=3 distinct
		// from the H=1/H=2 low strips and 3^(maxn-4) non-negative.)
		if H == maxn-1 && maxn >= 4 {
			contributePoleHeight(maxn, triangle, cfg)
			continue
		}

		// Strip H==maxn-2 is closed-form (k=2, proven). maxn>=7 keeps the
		// smallest 3-power (3^(maxn-7)) non-negative; below that it is swept.
		if H == maxn-2 && maxn >= 7 {
			contributeHeightNminus2(maxn, triangle, cfg)
			continue
		}

		// Trivial low strips H==1 and H==2 also have closed forms (C2);
		// contribute them directly instead of spawning a worker per column.
		if H == 1 || H == 2 {
			contributeLowHeight(H, maxn, triangle, cfg)
			continue
		}

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

			// Closed-form strips: contribute directly, no map/merge (see Run).
			if H == cfg.Maxn {
				mu.Lock()
				contributeTopHeight(cfg.Maxn, triangle, cfg)
				mu.Unlock()
				return
			}
			if H == cfg.Maxn-1 && cfg.Maxn >= 4 {
				mu.Lock()
				contributePoleHeight(cfg.Maxn, triangle, cfg)
				mu.Unlock()
				return
			}
			if H == cfg.Maxn-2 && cfg.Maxn >= 7 {
				mu.Lock()
				contributeHeightNminus2(cfg.Maxn, triangle, cfg)
				mu.Unlock()
				return
			}
			if H == 1 || H == 2 {
				mu.Lock()
				contributeLowHeight(H, cfg.Maxn, triangle, cfg)
				mu.Unlock()
				return
			}

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

// mapUnit is one key-range work item: process [lo, hi) of the source frontier.
type mapUnit struct {
	idx      int
	lo, hi   string // hex key bounds; "" = open end
	estTotal uint64 // estimated input records in [lo,hi) — drives the grain floor
	noSteal  bool   // un-splittable remnant of an earlier steal; never steal again
}

// runningUnit tracks an in-flight map unit so the stealer can size its remaining
// work and signal it to stop at a cursor.
type runningUnit struct {
	u         mapUnit
	processed *atomic.Uint64 // cumulative input records this worker has consumed
	stop      chan struct{}  // closed once to request a cooperative stop
	stopped   bool           // guarded by the scheduler mutex; set when stop is closed
}

// remaining estimates the input records this unit has left (clamped at 0).
func (r *runningUnit) remaining() uint64 {
	p := r.processed.Load()
	if p >= r.u.estTotal {
		return 0
	}
	return r.u.estTotal - p
}

// mapPhase maps the source frontier to the next column via a dynamic work-stealing
// pool (DESIGN 08, T2.3).  numUnits = Cores*UnitMult key-range units seed a pull
// queue worked by Cores goroutines.  When the queue drains and a core goes idle
// while another unit is still grinding (the straggler tail), the idle worker
// signals the longest-remaining unit to stop at a key cursor; that unit finalizes
// a valid output over [lo,cursor) and the remainder [cursor,hi) is split across
// the idle cores.  Splitting the RUNNING straggler's cursor — not a finer static
// cut — is what the design shows is necessary (heaviness concentrates by key, so
// static subdivision isolates rather than divides it).  Result-invariant: the
// merge recombines by output key regardless of how input work was partitioned.
//
// Stealing is gated on cfg.StealGrain>0 and disabled under overlap (where the
// shared pool's idle-core accounting wouldn't be local).  With it off, this is a
// plain pull queue — the same work partition as before.
func mapPhase(
	ctx context.Context,
	cfg SweepConfig,
	H, col int,
	frontier []string,
	tel *telemetry,
	sem chan struct{},
) ([]string, []map[int]map[int]uint64, Acct, error) {

	// Invariant: column work must never start at the top strip — H==maxn is
	// contributed in closed form (contributeTopHeight) and must be short-circuited
	// before any sweep. Tripping this means that short-circuit was bypassed.
	if H == cfg.Maxn {
		return nil, nil, Acct{}, fmt.Errorf("mapPhase: column work started at top height H=%d (maxn=%d); closed-form short-circuit was bypassed", H, cfg.Maxn)
	}

	numUnits := cfg.Cores * unitMult(cfg)
	if numUnits < 1 {
		numUnits = 1
	}
	cuts, err := SampleKeysMulti(frontier, H, numUnits-1)
	if err != nil {
		return nil, nil, Acct{}, err
	}
	los, his := cutsToBounds(cuts)
	n0 := len(los)

	// Grain floor in records: don't steal a remnant smaller than StealGrain of a
	// core's fair share (design sweet spot ≈ 0.05).  0 ⇒ stealing off.
	frontierIn := sumFrontierRecords(frontier)
	var grainRecs uint64
	stealOn := cfg.StealGrain > 0 && cfg.Cores > 1 && cfg.OverlapHeights <= 1
	if stealOn && frontierIn > 0 {
		grainRecs = uint64(cfg.StealGrain * float64(frontierIn) / float64(cfg.Cores))
	}

	var (
		mu          sync.Mutex
		cond        = sync.NewCond(&mu)
		queue       []mapUnit
		inflight    = map[int]*runningUnit{}
		outstanding = n0 // queued + in-flight units not yet terminal
		nextIdx     = n0 // next unique unit id (for steal children)
		firstErr    error

		outPaths    []string
		triContribs []map[int]map[int]uint64
		acct        Acct
	)
	estPer := uint64(1)
	if n0 > 0 {
		estPer = frontierIn / uint64(n0)
	}
	for i := 0; i < n0; i++ {
		queue = append(queue, mapUnit{idx: i, lo: los[i], hi: his[i], estTotal: estPer})
	}

	// Cancel siblings on the first error so a failed unit doesn't leave a column
	// half-mapped with cores still busy.
	mctx, mcancel := context.WithCancel(ctx)
	defer mcancel()

	// pickVictim returns the longest-remaining steal-eligible in-flight unit, or
	// nil. Caller holds mu. Eligible = making progress, not already stopped, not
	// flagged un-splittable, and with more than a grain of work left.
	pickVictim := func() *runningUnit {
		if grainRecs == 0 {
			return nil
		}
		var best *runningUnit
		var bestRem uint64
		for _, r := range inflight {
			if r.stopped || r.u.noSteal || r.processed.Load() == 0 {
				continue
			}
			if rem := r.remaining(); rem > grainRecs && rem > bestRem {
				bestRem, best = rem, r
			}
		}
		return best
	}

	var wg sync.WaitGroup
	for w := 0; w < cfg.Cores; w++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for {
				mu.Lock()
				for {
					if firstErr != nil || outstanding == 0 {
						mu.Unlock()
						return
					}
					if len(queue) > 0 {
						break
					}
					// Idle with work still running: become a thief — nominate the
					// fattest straggler to stop, then wait for its children.
					if v := pickVictim(); v != nil {
						v.stopped = true
						close(v.stop)
					}
					cond.Wait()
				}
				u := queue[len(queue)-1]
				queue = queue[:len(queue)-1]
				r := &runningUnit{u: u, processed: new(atomic.Uint64), stop: make(chan struct{})}
				inflight[u.idx] = r
				mu.Unlock()

				sem <- struct{}{}
				outPath := filepath.Join(cfg.RunDir,
					fmt.Sprintf("map_h%d_c%d_u%d.bin", H, col, u.idx))
				a := MapArgs{
					InPaths: frontier, H: H, Maxn: cfg.Maxn, Fold: cfg.Fold,
					RAM: cfg.RAM, SpillDir: cfg.SpillDir, OutPath: outPath,
					Counter: cfg.CounterWidth, LoHex: u.lo, HiHex: u.hi, Rev: cfg.Rev,
				}
				res, runErr := RunMapWorker(mctx, cfg.Bin, a, unitProgress(tel, r.processed), r.stop)
				<-sem

				mu.Lock()
				delete(inflight, u.idx)
				if runErr != nil {
					if firstErr == nil {
						firstErr = fmt.Errorf("unit %d [%s,%s): %w", u.idx, u.lo, u.hi, runErr)
						mcancel()
					}
					cond.Broadcast()
					mu.Unlock()
					continue
				}
				if res.OutRecords > 0 {
					outPaths = append(outPaths, outPath)
				} else {
					removeRun(outPath)
				}
				triContribs = append(triContribs, res.TriContribs)
				acct.Add(res.Acct)
				if os.Getenv("POLY_UNIT_LOG") != "" {
					fmt.Printf("event=unit H=%d col=%d u=%d lo=%s hi=%s out_records=%d cpu_s=%.3f wall_s=%.3f stop_key=%s\n",
						H, col, u.idx, u.lo, u.hi, res.OutRecords, res.Acct.CPUS, res.Acct.WallS, res.StopKey)
				}

				// Did this unit stop early at a steal cursor? If so requeue the
				// remainder [cursor,hi), split across the idle cores.
				if res.StopKey != "" && res.StopKey != u.hi {
					children := splitRemainder(frontier, H, res.StopKey, u.hi,
						cfg.Cores-len(inflight), r.remaining(), grainRecs, &nextIdx)
					queue = append(queue, children...)
					outstanding += len(children) - 1 // this unit done; children added
					tel.steal()
					if os.Getenv("POLY_UNIT_LOG") != "" {
						fmt.Printf("event=steal H=%d col=%d victim_u=%d cursor=%s children=%d rem=%d\n",
							H, col, u.idx, res.StopKey, len(children), r.remaining())
					}
				} else {
					outstanding-- // ran to completion
				}
				cond.Broadcast()
				mu.Unlock()
			}
		}()
	}
	wg.Wait()

	if firstErr != nil {
		return nil, nil, Acct{}, firstErr
	}
	return outPaths, triContribs, acct, nil
}

// splitRemainder divides a stopped straggler's remaining range [cursor,hi) into
// up to freeCores+1 record-balanced child units (half-split when freeCores is 0).
// It returns at least one child so no work is dropped; if the .idx samples can't
// be cut (a narrow range), it returns the single range flagged noSteal so the
// stealer won't thrash on it.  Each child inherits an even share of the parent's
// remaining estimate.  Caller holds the scheduler mutex (mutates *nextIdx).
func splitRemainder(frontier []string, H int, cursor, hi string, freeCores int,
	remaining, grainRecs uint64, nextIdx *int) []mapUnit {

	parts := freeCores + 1
	if parts < 2 {
		parts = 2
	}
	// Don't carve pieces below the grain floor.
	if grainRecs > 0 {
		if maxParts := int(remaining / grainRecs); maxParts >= 1 && parts > maxParts {
			parts = maxParts
		}
	}
	var cutKeys []string
	if parts >= 2 {
		cutKeys, _ = SplitRangeByIndex(frontier, H, cursor, hi, parts-1)
	}
	los, his := splitBounds(cursor, hi, cutKeys)
	est := remaining / uint64(len(los))
	if est == 0 {
		est = 1
	}
	out := make([]mapUnit, len(los))
	for i := range los {
		out[i] = mapUnit{idx: *nextIdx, lo: los[i], hi: his[i], estTotal: est,
			noSteal: len(cutKeys) == 0} // single un-splittable remnant: don't re-steal
		*nextIdx++
	}
	return out
}

// splitBounds turns cut keys inside (lo,hi) into contiguous [lo,hi) sub-ranges.
func splitBounds(lo, hi string, cuts []string) (los, his []string) {
	los = append(los, lo)
	for _, c := range cuts {
		his = append(his, c)
		los = append(los, c)
	}
	his = append(his, hi)
	return los, his
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

// topHeightClosedForm returns T(maxn,maxn) = 3^(maxn-1), the count of fixed
// polyplets whose bounding box is exactly maxn tall under an maxn-cell budget:
// one cell per row, three horizontal offsets at each of the maxn-1 steps.
func topHeightClosedForm(maxn int) uint64 {
	if maxn <= 0 {
		return 0
	}
	v := uint64(1)
	for i := 0; i < maxn-1; i++ {
		v *= 3
	}
	return v
}

// lowHeightRow returns the closed-form T(n,H) row for the trivial low strips
// H==1 and H==2, indexed by n (0 outside 1..maxn / below H):
//   T(n,1) = 1               (a single row of n cells)
//   T(n,2): T(2,2)=3, T(3,2)=10, T(n,2)=2·T(n-1,2)+T(n-2,2)+4  (n>=4)
// Returns nil for any other H. Both are verified exact against the a(20)
// triangle (results/ns_a20/Tnh_triangle.txt).
func lowHeightRow(H, maxn int) []uint64 {
	if H != 1 && H != 2 {
		return nil
	}
	row := make([]uint64, maxn+1)
	if H == 1 {
		for n := 1; n <= maxn; n++ {
			row[n] = 1
		}
		return row
	}
	for n := 2; n <= maxn; n++ {
		switch n {
		case 2:
			row[n] = 3
		case 3:
			row[n] = 10
		default:
			row[n] = 2*row[n-1] + row[n-2] + 4
		}
	}
	return row
}

// contributeLowHeight adds the closed-form row for H==1 or H==2 to the triangle
// (and writes its per-height row if requested), doing no map/merge.
func contributeLowHeight(H, maxn int, triangle []uint64, cfg SweepConfig) {
	row := lowHeightRow(H, maxn)
	for n := 1; n <= maxn && n < len(triangle); n++ {
		triangle[n] += row[n]
	}
	if cfg.PerHeightOut != "" {
		if werr := writePerHeight(cfg.PerHeightOut, H, maxn, row); werr != nil {
			fmt.Fprintf(os.Stderr, "per-height write H=%d: %v\n", H, werr)
		}
	}
}

// pow3 returns 3^k for k>=0 (0 for k<0).
func pow3(k int) uint64 {
	v := uint64(1)
	for i := 0; i < k; i++ {
		v *= 3
	}
	return v
}

// contributePoleHeight adds the closed-form pole strip H=maxn-1 to the triangle
// (and writes its per-height row), doing no map/merge. The strip occupies n in
// {maxn-1, maxn}:
//
//	T(maxn-1, maxn-1) = 3^(maxn-2)              (the diagonal, = T(H,H))
//	T(maxn,   maxn-1) = (25*maxn-45)*3^(maxn-4) (C1, proven; docs/proofs/T-n-nm1.md)
//
// Caller guarantees maxn>=4. ns-gate-closedform pins both formulas against the
// triangle so a derivation error can never reach a result.
func contributePoleHeight(maxn int, triangle []uint64, cfg SweepConfig) {
	H := maxn - 1
	row := make([]uint64, maxn+1)
	row[H] = pow3(maxn - 2)
	row[maxn] = uint64(25*maxn-45) * pow3(maxn-4)
	if H < len(triangle) {
		triangle[H] += row[H]
	}
	if maxn < len(triangle) {
		triangle[maxn] += row[maxn]
	}
	if cfg.PerHeightOut != "" {
		if werr := writePerHeight(cfg.PerHeightOut, H, maxn, row); werr != nil {
			fmt.Fprintf(os.Stderr, "per-height write H=%d: %v\n", H, werr)
		}
	}
}

// contributeHeightNminus2 adds the closed-form strip H=maxn-2 (the third
// diagonal, k=2, proven) to the triangle, doing no map/merge. The strip spans
// n in {maxn-2, maxn-1, maxn}:
//
//	T(maxn-2,maxn-2) = 3^(maxn-3)                                 (diagonal)
//	T(maxn-1,maxn-2) = (25(maxn-1)-45)*3^(maxn-5)                 (C1 at n=maxn-1)
//	T(maxn,  maxn-2) = (625*maxn^2-2459*maxn+1134)/2 * 3^(maxn-7) (proven, n>=5)
//
// Caller guarantees maxn>=7 (so 3^(maxn-7)>=1). The numerator 625n^2-2459n+1134
// is always even (n^2-n is even). ns-gate-closedform pins all three against the
// triangle.
func contributeHeightNminus2(maxn int, triangle []uint64, cfg SweepConfig) {
	H := maxn - 2
	row := make([]uint64, maxn+1)
	row[H] = pow3(maxn - 3)
	row[maxn-1] = uint64(25*(maxn-1)-45) * pow3(maxn-5)
	row[maxn] = uint64((625*maxn*maxn-2459*maxn+1134)/2) * pow3(maxn-7)
	for _, n := range []int{H, maxn - 1, maxn} {
		if n < len(triangle) {
			triangle[n] += row[n]
		}
	}
	if cfg.PerHeightOut != "" {
		if werr := writePerHeight(cfg.PerHeightOut, H, maxn, row); werr != nil {
			fmt.Fprintf(os.Stderr, "per-height write H=%d: %v\n", H, werr)
		}
	}
}

// contributeTopHeight adds the closed-form top strip T(maxn,maxn) to the
// triangle (and writes its per-height row if requested), doing no map/merge.
func contributeTopHeight(maxn int, triangle []uint64, cfg SweepConfig) {
	v := topHeightClosedForm(maxn)
	if maxn < len(triangle) {
		triangle[maxn] += v
	}
	if cfg.PerHeightOut != "" {
		hTri := make([]uint64, maxn+1)
		hTri[maxn] = v
		if werr := writePerHeight(cfg.PerHeightOut, maxn, maxn, hTri); werr != nil {
			fmt.Fprintf(os.Stderr, "per-height write H=%d: %v\n", maxn, werr)
		}
	}
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
