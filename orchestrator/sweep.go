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
	"math/big"
	"os"
	"path/filepath"
	"sort"
	"strconv"
	"sync"
	"sync/atomic"
	"time"
)

// SweepConfig holds all parameters for a height-sweep run.
type SweepConfig struct {
	Maxn            int
	Fold            bool
	Kernel          string // "column" (default) or "kink"; empty = "column"
	Cores           int           // max concurrent workers
	UnitMult        int           // MAP work units per core (default 1); units = Cores*UnitMult, concurrency stays Cores
	MergeMult       int           // MERGE ranges per core (0 = follow UnitMult); set low to cut the (cores*mult)^2 merge fan-in
	StealGrain      float64       // map work-stealing grain as a fraction of a core's fair share (0 = off; design sweet spot ≈ 0.05). When a core idles in the column tail, the longest-remaining unit is stopped at a cursor and its remainder split across idle cores. Coexists with OverlapHeights: dynamically gated to fire only once a height is the pool's sole occupant (see stealAllowed) — safe in the common endgame where the dominant height outlives its siblings.
	OverlapHeights  int           // heights to sweep CONCURRENTLY sharing one Cores-wide pool (0/1 = sequential). Hides one height's low-util merge behind another's map. Checkpoints at HEIGHT boundaries (the completed-height set), not per column.
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

	// afterHeight, if non-nil, is called in overlap mode after a height
	// completes and its height-boundary checkpoint is written. Unexported test
	// seam (overlap_resume_test.go cancels the run after the k-th completion).
	afterHeight func(H int)
}

// SweepResult is the output of a complete run over all heights.
type SweepResult struct {
	Triangle []*big.Int // Triangle[n] = Σ_H T(n,H)
	Acct     Acct
}

// newBigRow returns a zero-filled []*big.Int of length n, with every slot a
// distinct non-nil *big.Int (a nil slot panics on .Add). Centralizing this
// keeps the "no nil slots" invariant in one place instead of repeated at
// every triangle/row allocation site.
func newBigRow(n int) []*big.Int {
	row := make([]*big.Int, n)
	for i := range row {
		row[i] = new(big.Int)
	}
	return row
}

// addTriContribs folds a column's per-cell triangle contributions into the
// running height row hTri, dropping any n outside [0, maxn]. Shared by the
// column and kink sweep drivers (which both accumulate contributions only
// after the column's merge succeeds).
func addTriContribs(hTri []*big.Int, triContribs []map[int]map[int]*big.Int, maxn int) {
	for _, hm := range triContribs {
		for _, nm := range hm {
			for n, v := range nm {
				if n >= 0 && n <= maxn {
					hTri[n].Add(hTri[n], v)
				}
			}
		}
	}
}

// copyBigRow deep-copies a []*big.Int row so the result doesn't alias the
// source's *big.Int pointers (mutating one via .Add must not mutate both).
func copyBigRow(src []*big.Int) []*big.Int {
	dst := make([]*big.Int, len(src))
	for i, v := range src {
		if v == nil {
			dst[i] = new(big.Int)
		} else {
			dst[i] = new(big.Int).Set(v)
		}
	}
	return dst
}

// counterName normalizes a counter-width tag, mapping "" to the u64 default.
func counterName(c string) string {
	if c == "" {
		return "u64"
	}
	return c
}

// kernelName normalizes a kernel tag, mapping "" to the column default.
func kernelName(k string) string {
	if k == "" {
		return "column"
	}
	return k
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
	if want, got := kernelName(cfg.Kernel), kernelName(resume.Kernel); got != want {
		return fmt.Errorf("resume: checkpoint kernel=%s != --kernel %s", got, want)
	}
	// Overlap-form checkpoint (Done set): resume skips completed heights by set
	// membership, not by a single resume.H, so the H-in-heights check below does
	// not apply.
	if len(resume.Done) > 0 {
		return nil
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
	triangle := newBigRow(maxn + 1)
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
		// Restore the accumulated triangle from the checkpoint. Copy each
		// value rather than aliasing the checkpoint's *big.Int pointers, since
		// triangle[n] is mutated in place (.Add) below.
		for n, v := range resume.Triangle {
			if n <= maxn && v != nil {
				triangle[n] = new(big.Int).Set(v)
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
	writeCheckpoint := func(H, col int, frontier []string, hTri []*big.Int) {
		// Combine outer accumulated triangle with current height's contribution.
		combined := copyBigRow(triangle)
		for n, v := range hTri {
			if n < len(combined) && v != nil {
				combined[n].Add(combined[n], v)
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
			Kernel:   kernelName(cfg.Kernel),
		}
		if err := ck.Write(cfg.CheckpointPath); err != nil {
			fmt.Fprintf(os.Stderr, "checkpoint write: %v\n", err)
		}
	}

	tel, err := newTelemetry(cfg, time.Now())
	if err != nil {
		return nil, err
	}

	// activeHeights counts heights CURRENTLY sweeping (between entering and
	// leaving sweepHeight). The sequential path below sets it to 1 once and never
	// touches it again — exactly one height sweeps at a time by construction, so
	// it's always 1, the same value sequential mode has always implicitly had.
	// runOverlap increments/decrements it around each height's real sweepHeight
	// call; mapPhase's steal gate (stealAllowed) reads it live to allow stealing
	// once a height becomes the pool's sole occupant (the overlap+steal coexist
	// fix — see stealAllowed's doc).
	activeHeights := new(atomic.Int32)

	// Shared Cores-wide worker pool. In overlap mode several heights draw from it
	// concurrently, so a height's low-utilization merge phase runs alongside
	// another's map phase rather than idling the box.
	sem := make(chan struct{}, cfg.Cores)

	// Kernel dispatch: sweepHeight (whole-column) unless --kernel kink selects
	// sweepHeightKink (per-cell boundary sweep). Both share sweepHeightFn's
	// signature so the sequential and overlap paths below need no other change.
	sweepFn := sweepHeight
	if kernelName(cfg.Kernel) == "kink" {
		sweepFn = sweepHeightKink
	}

	if cfg.OverlapHeights > 1 {
		// Resume in overlap mode is by completed-height SET: drop the Done heights
		// (their contributions are already restored into `triangle` above) and
		// sweep the rest. A height that was in flight at the crash is absent from
		// Done, so it re-runs from scratch — no double-count, no gap.
		pending := heights
		if resume != nil && len(resume.Done) > 0 {
			done := make(map[int]bool, len(resume.Done))
			for _, H := range resume.Done {
				done[H] = true
			}
			pending = nil
			for _, H := range heights {
				if !done[H] {
					pending = append(pending, H)
				}
			}
		}
		// Long-pole-first: sweep the TALLEST heights first so the critical-path
		// height (the longest serial column chain) starts at t=0 and overlaps the
		// whole run, instead of trailing as a lone tail at the end when nothing is
		// left to fill the cores behind its light merges. runOverlap acquires the
		// height pool in this order, so the order is honored deterministically.
		pending = append([]int(nil), pending...)
		sort.Sort(sort.Reverse(sort.IntSlice(pending)))
		return runOverlap(ctx, cfg, pending, triangle, acct, tel, sem, activeHeights, sweepFn)
	}

	// Sequential mode sweeps exactly one height at a time by construction, so
	// activeHeights is always 1 here — set once, never touched again (no per-
	// height inc/dec needed; see the activeHeights comment above).
	activeHeights.Store(1)

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

		// Strips H==maxn-k are closed-form (proven/data-pinned diagonals); see
		// diagonalStripValid for the true n>=2k+1 validity threshold.
		if k := maxn - H; diagonalStripValid(maxn, k) {
			contributeDiagonalStrip(maxn, k, triangle, cfg)
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

		hTri, hAcct, err := sweepFn(ctx, cfg, H, startCol, frontier, writeCheckpoint, tel, sem, activeHeights)

		// Accumulate this height's contributions before handling the error,
		// so the checkpoint written on cancellation includes them.
		for n, v := range hTri {
			if n <= maxn {
				triangle[n].Add(triangle[n], v)
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
// sequential path; results accumulate under `mu`. Checkpoints are written at
// HEIGHT boundaries (markDone snapshots the completed-height set + triangle);
// resume skips the done heights and re-runs any that were in flight at the
// crash from scratch — no mid-HEIGHT (column) resume here. Caller guarantees
// cfg.OverlapHeights >= 2.
//
// activeHeights tracks how many heights are CURRENTLY between entering and
// leaving sweepHeight (real column work; the closed-form short-circuits below
// never touch it, since they don't draw from `sem` at all). mapPhase's
// work-stealing reads it live to allow stealing once a height becomes the
// pool's sole occupant — the overlap+steal coexistence fix (see stealAllowed).
func runOverlap(ctx context.Context, cfg SweepConfig, heights []int,
	triangle []*big.Int, acct Acct, tel *telemetry, sem chan struct{},
	activeHeights *atomic.Int32, sweepFn sweepHeightFn) (*SweepResult, error) {

	var mu sync.Mutex
	var firstErr error
	noopCkpt := func(int, int, []string, []*big.Int) {} // overlap: no MID-height checkpoint
	heightSem := make(chan struct{}, cfg.OverlapHeights)
	var wg sync.WaitGroup

	// Height-boundary checkpoint: heights complete out of order here, so the
	// resumable unit is the SET of completed heights (not a single H/col). When a
	// height finishes, markDone (caller holds mu, has already folded the height's
	// contribution into triangle) records it and snapshots {done-set, triangle,
	// acct} to POLYCKPT. On resume the done heights are skipped and the rest —
	// including any that were in flight at the crash — re-run from scratch.
	doneHeights := []int{}
	markDone := func(H int) {
		doneHeights = append(doneHeights, H)
		if cfg.CheckpointPath == "" {
			return
		}
		ck := &Checkpoint{
			H: -1, Col: -1,
			Done:     append([]int(nil), doneHeights...),
			Triangle: copyBigRow(triangle),
			Acct:     acct,
			Maxn:     cfg.Maxn,
			Counter:  counterName(cfg.CounterWidth),
			Fold:     cfg.Fold,
			Kernel:   kernelName(cfg.Kernel),
		}
		if err := ck.Write(cfg.CheckpointPath); err != nil {
			fmt.Fprintf(os.Stderr, "overlap checkpoint H=%d: %v\n", H, err)
		}
	}
	fireAfterHeight := func(H int) {
		if cfg.afterHeight != nil {
			cfg.afterHeight(H)
		}
	}

	for _, H := range heights {
		// Acquire the height-pool slot HERE, in loop order, so the long-pole-first
		// ordering set by the caller is honored deterministically (rather than
		// left to which goroutine the scheduler runs first). Stop launching once
		// ctx is cancelled.
		select {
		case heightSem <- struct{}{}:
		case <-ctx.Done():
			wg.Wait()
			return nil, context.Canceled
		}
		wg.Add(1)
		go func(H int) {
			defer wg.Done()
			defer func() { <-heightSem }()

			// Closed-form strips: contribute directly, no map/merge (see Run).
			// Each is a completed height -> markDone + checkpoint under mu.
			if H == cfg.Maxn {
				mu.Lock()
				contributeTopHeight(cfg.Maxn, triangle, cfg)
				markDone(H)
				mu.Unlock()
				fireAfterHeight(H)
				return
			}
			if H == cfg.Maxn-1 && cfg.Maxn >= 4 {
				mu.Lock()
				contributePoleHeight(cfg.Maxn, triangle, cfg)
				markDone(H)
				mu.Unlock()
				fireAfterHeight(H)
				return
			}
			if k := cfg.Maxn - H; diagonalStripValid(cfg.Maxn, k) {
				mu.Lock()
				contributeDiagonalStrip(cfg.Maxn, k, triangle, cfg)
				markDone(H)
				mu.Unlock()
				fireAfterHeight(H)
				return
			}
			if H == 1 || H == 2 {
				mu.Lock()
				contributeLowHeight(H, cfg.Maxn, triangle, cfg)
				markDone(H)
				mu.Unlock()
				fireAfterHeight(H)
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
			// This height now starts drawing real (map/merge) work from the shared
			// pool — count it as active for the steal gate's duration.
			activeHeights.Add(1)
			hTri, hAcct, err := sweepFn(ctx, cfg, H, 0, []string{seed}, noopCkpt, tel, sem, activeHeights)
			activeHeights.Add(-1)

			mu.Lock()
			// Only fold a height's contribution in (and mark it done) if it
			// COMPLETED. A cancelled height returns a partial hTri; adding it would
			// corrupt the triangle and, worse, leak into the next completed height's
			// checkpoint snapshot. On error we record firstErr and leave H un-done
			// so resume re-runs it from scratch.
			if err != nil {
				if firstErr == nil {
					firstErr = fmt.Errorf("H=%d: %w", H, err)
				}
				mu.Unlock()
				return
			}
			for n, v := range hTri {
				if n >= 0 && n <= cfg.Maxn {
					triangle[n].Add(triangle[n], v)
				}
			}
			acct.Add(hAcct)
			markDone(H)
			mu.Unlock()
			fireAfterHeight(H)
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

// sweepHeightFn is the shape shared by sweepHeight (column kernel) and
// sweepHeightKink (kink kernel), so Run/runOverlap's one-line kernel dispatch
// (see cfg.Kernel) can select between them without any other change to the
// sequential or overlap driving code.
type sweepHeightFn func(
	ctx context.Context,
	cfg SweepConfig,
	H, startCol int,
	frontier []string,
	writeCheckpoint func(H, col int, frontier []string, hTri []*big.Int),
	tel *telemetry,
	sem chan struct{},
	activeHeights *atomic.Int32,
) ([]*big.Int, Acct, error)

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
	writeCheckpoint func(H, col int, frontier []string, hTri []*big.Int),
	tel *telemetry,
	sem chan struct{},
	activeHeights *atomic.Int32,
) ([]*big.Int, Acct, error) {

	hTri := newBigRow(cfg.Maxn + 1) // contributions from this height only
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
		mapOuts, triContribs, mapAcct, err := mapPhase(ctx, cfg, H, col, frontier, tel, sem, activeHeights, columnKeyLen(H), "")
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
		mergeOuts, totalRecs, mergeAcct, err := mergePhase(ctx, cfg, H, col, mapOuts, sem, columnKeyLen(H), "")
		stopHB()
		if err != nil {
			// hTri does NOT include current col's contributions.
			writeCheckpoint(H, col-1, frontier, hTri)
			return hTri, acct, fmt.Errorf("H=%d col=%d merge: %w", H, col, err)
		}
		acct.Add(mergeAcct)

		// Both map and merge succeeded: now accumulate this col's contributions.
		addTriContribs(hTri, triContribs, cfg.Maxn)

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

// removeRuns deletes each run file (with its .idx sidecar) in paths.
func removeRuns(paths []string) {
	for _, p := range paths {
		removeRun(p)
	}
}

// sweepHeightKink sweeps one height H from startCol using the kink kernel
// (Design 14): a column is one H+2-keyed "seed" round (harvest this column's
// completions, append the carry/touch suffix, keyLen H+2->H+4), H sequential
// H+4-keyed mid-column stage rounds (the per-cell king-adjacency transfer),
// and one H+4-keyed "finalize" round (drop the carry with a stranding check,
// canonicalize/prune/fold, keyLen H+4->H+2) — a barrier at every stage instead
// of once per column (Phase 0's Option A). Checkpointing is column-level only
// (the locked-in Phase 2 decision): a crash mid-column re-runs the whole
// column's stage sequence from its seed, same as sweepHeight re-runs a whole
// column's single map+merge round.
//
// Mirrors sweepHeight's shape exactly (same signature via sweepHeightFn, same
// cancellation/error/checkpoint/GC structure) so the two can share Run's and
// runOverlap's driving code; the only real difference is the inner stage loop
// between a column's map and its next-column frontier.
func sweepHeightKink(
	ctx context.Context,
	cfg SweepConfig,
	H, startCol int,
	frontier []string,
	writeCheckpoint func(H, col int, frontier []string, hTri []*big.Int),
	tel *telemetry,
	sem chan struct{},
	activeHeights *atomic.Int32,
) ([]*big.Int, Acct, error) {

	hTri := newBigRow(cfg.Maxn + 1)
	var acct Acct
	lastCkpt := time.Now()

	forwardCheckpoint := func(col int, frontier []string) {
		writeCheckpoint(H, col, frontier, hTri)
		if cfg.afterColumn != nil {
			cfg.afterColumn(H, col)
		}
	}

	frontierIn := sumFrontierRecords(frontier)
	inKeyLen := columnKeyLen(H)
	stageKeyLen := kinkKeyLen(H)

	for col := startCol; col <= cfg.Maxn; col++ {
		if len(frontier) == 0 {
			break
		}

		select {
		case <-ctx.Done():
			writeCheckpoint(H, col-1, frontier, hTri)
			return hTri, acct, ctx.Err()
		default:
		}

		colStart := time.Now()
		stopHB := tel.startColumn(H, col)
		var colAcct Acct
		var colMapWall, colMergeWall, colMapCPU, colMergeCPU float64
		var nMapUnits, nMergeRanges int

		// runRound executes one map+merge round of the column's stage sequence
		// and folds its accounting into colAcct/colMap*/colMerge*. name is only
		// used in error messages and per-round telemetry. When mergeless is set
		// (the seed round only), the merge barrier is skipped: kinkSeedStage0
		// appends a CONSTANT key suffix, so each map unit's output covers a
		// disjoint key range and is internally sorted+deduplicated — their
		// concatenation IS the sorted stage-0 table, and a merge would be a pure
		// pass-through fork over the column's largest frontier (invariant gated
		// in test/gate_kink_column.cpp testSeedOutputSortedAndUnique).
		runRound := func(name string, in []string, mapKeyLen int, stage string, mergeKeyLen int, mergeless bool) ([]string, []map[int]map[int]*big.Int, error) {
			frontierRecs := sumFrontierRecords(in)
			t0 := time.Now()
			mapOuts, triContribs, mapAcct, err := mapPhase(ctx, cfg, H, col, in, tel, sem, activeHeights, mapKeyLen, stage)
			if err != nil {
				return nil, nil, fmt.Errorf("H=%d col=%d kink %s map: %w", H, col, name, err)
			}
			roundMapWall := time.Since(t0).Seconds()
			colAcct.Add(mapAcct)
			colMapWall += roundMapWall
			colMapCPU += mapAcct.CPUS
			nMapUnits += len(mapOuts)

			if mergeless {
				tel.observeRound(H, col, name, frontierRecs, roundMapWall, mapAcct.CPUS, 0, 0, len(mapOuts), 0)
				return mapOuts, triContribs, nil
			}

			t1 := time.Now()
			mergeOuts, _, mergeAcct, err := mergePhase(ctx, cfg, H, col, mapOuts, sem, mergeKeyLen, stage)
			removeRuns(mapOuts)
			if err != nil {
				return nil, nil, fmt.Errorf("H=%d col=%d kink %s merge: %w", H, col, name, err)
			}
			roundMergeWall := time.Since(t1).Seconds()
			colAcct.Add(mergeAcct)
			colMergeWall += roundMergeWall
			colMergeCPU += mergeAcct.CPUS
			nMergeRanges += len(mergeOuts)
			tel.observeRound(H, col, name, frontierRecs, roundMapWall, mapAcct.CPUS, roundMergeWall, mergeAcct.CPUS, len(mapOuts), len(mergeOuts))
			return mergeOuts, triContribs, nil
		}

		// Seed: H+2 -> H+4, harvests this column's completions (classify happens
		// here, at column START — see the design doc's kink_tm.cpp re-read). The
		// merge is skipped (mergeless): the constant-suffix transform leaves the
		// per-unit map outputs already sorted + collision-free across ranges.
		stageTable, triContribs, err := runRound("seed", frontier, inKeyLen, "seed", stageKeyLen, true)
		if err != nil {
			stopHB()
			writeCheckpoint(H, col-1, frontier, hTri)
			return hTri, acct, err
		}
		addTriContribs(hTri, triContribs, cfg.Maxn)

		// H mid-column stage rounds: H+4 -> H+4, the per-cell king-adjacency
		// carry transfer (core/kink.h's kinkStageTransition via
		// map_shard_stage_file).
		for r := 0; r < H; r++ {
			next, _, err := runRound(fmt.Sprintf("stage%d", r), stageTable, stageKeyLen, strconv.Itoa(r), stageKeyLen, false)
			removeRuns(stageTable)
			if err != nil {
				stopHB()
				writeCheckpoint(H, col-1, frontier, hTri)
				return hTri, acct, err
			}
			stageTable = next
		}

		// Finalize: H+4 -> H+2, drop the carry (stranding-checked), canonicalize,
		// prune, fold — this column's contribution to the next column's frontier.
		nextFrontier, _, err := runRound("finalize", stageTable, stageKeyLen, "finalize", inKeyLen, false)
		removeRuns(stageTable)
		stopHB()
		if err != nil {
			writeCheckpoint(H, col-1, frontier, hTri)
			return hTri, acct, err
		}

		acct.Add(colAcct)
		totalRecs := sumFrontierRecords(nextFrontier)
		colWall := time.Since(colStart).Seconds()
		tel.observe(ColumnCost{
			H: H, Col: col,
			FrontierIn:   frontierIn,
			FrontierOut:  totalRecs,
			WallS:        colWall,
			CPUS:         colAcct.CPUS,
			RSSMax:       colAcct.RSSMax,
			MapWallS:     colMapWall,
			MapCPUS:      colMapCPU,
			MergeWallS:   colMergeWall,
			MergeCPUS:    colMergeCPU,
			NMapUnits:    nMapUnits,
			NMergeRanges: nMergeRanges,
		})
		frontierIn = totalRecs

		oldFrontier := frontier
		frontier = nextFrontier

		if totalRecs == 0 {
			forwardCheckpoint(col, nil)
			removeRuns(oldFrontier)
			frontier = nil
			break
		}

		interval := cfg.CheckpointEvery
		if interval == 0 || time.Since(lastCkpt) >= interval {
			forwardCheckpoint(col, frontier)
			lastCkpt = time.Now()
		}

		removeRuns(oldFrontier)
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
	started   time.Time      // when this unit went in-flight (for rate-based sizing)
}

// remaining estimates the input records this unit has left (clamped at 0).
func (r *runningUnit) remaining() uint64 {
	p := r.processed.Load()
	if p >= r.u.estTotal {
		return 0
	}
	return r.u.estTotal - p
}

// indexStride mirrors core/runfile.h kIndexStride: the .idx holds one key per
// indexStride records, so a remnant needs ≥2 strides to contain an interior cut.
const indexStride = 64

// stealEligible reports whether an in-flight unit is worth stealing: making
// progress, not already stopped/un-splittable, and at least 2 index strides of
// records remaining so the .idx can actually cut the remnant (without this
// clause the stealer stops a victim it then cannot split, paying the
// stop+respawn overhead for zero fan-out — Stop-Then-Shrug). Above that floor,
// eligibility is granted by EITHER of two signals:
//
//   - the fast path: remaining RECORDS alone exceed grainRecs (the common
//     case — cheap to check, no rate math needed).
//   - the slow path: this unit's remaining record count is small, but at its
//     OWN observed rate the remaining WALL TIME exceeds grainSeconds. This is
//     the fix for results/steal-tail-h18.md's diagnosed miss — a
//     compute-heavy straggler (a handful of pathological keys) can have few
//     records left yet dominate the column tail; the record-only floor
//     filtered it out before stealScore's own wall-time ranking ever saw it.
//
// grainSeconds<=0 (no usable pool-wide reference rate yet, e.g. column just
// started) disables the slow path, NOT the whole check — falls back to
// record-only, same as before this fix.
func stealEligible(r *runningUnit, grainRecs uint64, grainSeconds float64, now time.Time) bool {
	if r.stopped || r.u.noSteal || r.processed.Load() == 0 {
		return false
	}
	rem := r.remaining()
	if rem < 2*indexStride {
		return false
	}
	if rem > grainRecs {
		return true
	}
	return grainSeconds > 0 && stealScore(r, now) > grainSeconds
}

// stealAllowed reports whether work-stealing may fire RIGHT NOW. A height's own
// "queue empty, a goroutine is about to go idle" signal is LOCAL to that height —
// it only equals BOX-WIDE idleness when this height is the SOLE occupant of the
// shared core pool (sem). In overlap mode with sibling heights still active, a
// "locally idle" goroutine may really be blocked on sem behind another height's
// units; stealing then would interrupt a legitimately-running straggler to hand
// its remainder to a goroutine that isn't actually free — paying the
// stop+finalize+respawn cost for zero real concurrency gained.
//
// Once every sibling height has finished — the common endgame: the dominant
// height (e.g. H16) outlives every cheap one — local idle becomes EXACTLY box
// idle, the same condition sequential mode always has, so stealing is fully safe
// there. This is what lets overlap and stealing coexist instead of being
// mutually exclusive: each height's mapPhase re-checks this on every steal
// decision (not once at column start), because columns can run for HOURS and the
// height landscape changes underneath a single long column.
//
// activeHeights nil means "no dynamic tracking" (steal unconditionally allowed,
// subject to the other gates) — used by callers that don't run heights
// concurrently and so never need the check.
func stealAllowed(activeHeights *atomic.Int32) bool {
	return activeHeights == nil || activeHeights.Load() <= 1
}

// stealScore ranks steal-eligible victims; the highest-scoring is stolen. We want
// the unit with the most WALL TIME left, not the most records — a compute-heavy
// straggler (a few pathological keys) can have few records remaining yet dominate
// the column tail. Score = estimated seconds remaining = records_left / rate,
// where rate = processed / elapsed.
func stealScore(r *runningUnit, now time.Time) float64 {
	rem := float64(r.remaining())
	elapsed := now.Sub(r.started).Seconds()
	p := r.processed.Load()
	if p == 0 || elapsed <= 0 {
		return rem // not enough signal yet → fall back to records
	}
	rate := float64(p) / elapsed
	if rate <= 0 {
		return rem
	}
	return rem / rate
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
// Stealing is gated on cfg.StealGrain>0 and, dynamically, on activeHeights (see
// stealAllowed): it only fires while this height is the sole occupant of the
// shared pool, which is always true in sequential mode and becomes true in
// overlap mode once sibling heights finish.  With StealGrain off, this is a
// plain pull queue — the same work partition as before.
//
// keyLen is the key width of frontier (the round's INPUT table); it drives
// SampleKeysMulti/splitRemainder and is always explicit so a kink-kernel round
// reading an H+4-keyed stage table isn't silently sampled at the column
// kernel's H+2 default. stage selects the kink kernel round ("" = column
// kernel, unchanged behavior; "seed"/"finalize"/an int stage index = kink)
// and is passed straight through to MapArgs.Kernel/Stage. Work-stealing is
// additionally gated off for "seed"/"finalize": those rounds run in-RAM
// (Phase 2 decision) and don't implement the SIGTERM cooperative-stop
// protocol the mid-column int-stage rounds (map_shard_stage_file) support, so
// stopping one would kill it outright rather than yield a valid partial
// output.
func mapPhase(
	ctx context.Context,
	cfg SweepConfig,
	H, col int,
	frontier []string,
	tel *telemetry,
	sem chan struct{},
	activeHeights *atomic.Int32,
	keyLen int,
	stage string,
) ([]string, []map[int]map[int]*big.Int, Acct, error) {

	// Invariant: column work must never start at the top strip — H==maxn is
	// contributed in closed form (contributeTopHeight) and must be short-circuited
	// before any sweep. Tripping this means that short-circuit was bypassed.
	if H == cfg.Maxn {
		return nil, nil, Acct{}, fmt.Errorf("mapPhase: column work started at top height H=%d (maxn=%d); closed-form short-circuit was bypassed", H, cfg.Maxn)
	}

	kernel := ""
	if stage != "" {
		kernel = "kink"
	}

	// Units seed a Cores-wide pull queue (each = one map_worker fork+exec). The
	// default Cores*UnitMult over-provisions a SMALL frontier: SampleKeysMulti
	// would still cut it into that many ranges and we'd spawn a worker per range,
	// most handling near-zero records. Measured at a30 H17: declining/tail columns
	// fork+exec'd ~6000 workers to transform a few hundred states. Cap units so
	// each carries >= minPerUnit records; peak/mid columns (large frontier) keep
	// the full count and are unaffected. Partition count doesn't affect the
	// result, so this is behavior-preserving.
	frontierIn := sumFrontierRecords(frontier)
	numUnits := cfg.Cores * unitMult(cfg)
	const minPerUnit = 2048
	if capUnits := int((frontierIn + minPerUnit - 1) / minPerUnit); capUnits < numUnits {
		numUnits = capUnits
	}
	if numUnits < 1 {
		numUnits = 1
	}
	cuts, err := SampleKeysMulti(frontier, H, keyLen, numUnits-1)
	if err != nil {
		return nil, nil, Acct{}, err
	}
	los, his := cutsToBounds(cuts)
	n0 := len(los)

	// Grain floor in records: don't steal a remnant smaller than StealGrain of a
	// core's fair share (design sweet spot ≈ 0.05).  0 ⇒ stealing off.  The
	// activeHeights dynamic gate (stealAllowed) is checked separately, per
	// decision, in pickVictim — not folded in here, since it can change mid-column.
	var grainRecs uint64
	stealConfigured := cfg.StealGrain > 0 && cfg.Cores > 1 && stage != "seed" && stage != "finalize"
	if stealConfigured && frontierIn > 0 {
		grainRecs = uint64(cfg.StealGrain * float64(frontierIn) / float64(cfg.Cores))
	}

	// phaseStart/completedProcessed track this mapPhase call's POOL-WIDE
	// average pace (records/s across every unit, fast and slow alike),
	// independent of any single unit's own rate. It's the reference the
	// wall-time steal floor (stealEligible's slow path) converts grainRecs
	// into seconds against — deliberately NOT the victim's own rate, which
	// would make the comparison tautological (rem/rate > grainRecs/rate
	// reduces to rem > grainRecs for any rate). completedProcessed retains
	// the contribution of units that have already exited inflight.
	phaseStart := time.Now()
	completedProcessed := new(atomic.Uint64)

	var (
		mu          sync.Mutex
		cond        = sync.NewCond(&mu)
		queue       []mapUnit
		inflight    = map[int]*runningUnit{}
		outstanding = n0 // queued + in-flight units not yet terminal
		nextIdx     = n0 // next unique unit id (for steal children)
		firstErr    error

		outPaths    []string
		triContribs []map[int]map[int]*big.Int
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

	// pickVictim returns the steal-eligible in-flight unit with the most estimated
	// WALL TIME left (stealScore), or nil. Caller holds mu. Eligible = making
	// progress, not already stopped, not un-splittable, > a grain of work left.
	pickVictim := func() *runningUnit {
		if grainRecs == 0 || !stealAllowed(activeHeights) {
			return nil
		}
		now := time.Now()
		// Pool-wide reference rate: everything completed so far, plus every
		// in-flight unit's current cumulative, over elapsed phase time. Fast
		// units dominate this average (there are many more of them than
		// stragglers), so it tracks "normal" pace, not the victim's own.
		var grainSeconds float64
		if elapsed := now.Sub(phaseStart).Seconds(); elapsed > 0 {
			totalDone := completedProcessed.Load()
			for _, r := range inflight {
				totalDone += r.processed.Load()
			}
			if refRate := float64(totalDone) / elapsed; refRate > 0 {
				grainSeconds = float64(grainRecs) / refRate
			}
		}
		var best *runningUnit
		var bestScore float64
		for _, r := range inflight {
			if !stealEligible(r, grainRecs, grainSeconds, now) {
				continue
			}
			if sc := stealScore(r, now); sc > bestScore {
				bestScore, best = sc, r
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
				r := &runningUnit{u: u, processed: new(atomic.Uint64), stop: make(chan struct{}), started: time.Now()}
				inflight[u.idx] = r
				mu.Unlock()

				sem <- struct{}{}
				outName := fmt.Sprintf("map_h%d_c%d_u%d.bin", H, col, u.idx)
				if stage != "" {
					// Distinguish a kink column's seed/stage-r/finalize rounds, which
					// otherwise all reuse the same (H,col,idx) filename and would
					// collide — the next round's map phase would read a file its own
					// merge phase is about to overwrite, and GC would delete a
					// just-produced round's output because it shares the prior
					// round's name.
					outName = fmt.Sprintf("map_h%d_c%d_k%s_u%d.bin", H, col, stage, u.idx)
				}
				outPath := filepath.Join(cfg.RunDir, outName)
				a := MapArgs{
					InPaths: frontier, H: H, Maxn: cfg.Maxn, Fold: cfg.Fold,
					RAM: cfg.RAM, SpillDir: cfg.SpillDir, OutPath: outPath,
					Counter: cfg.CounterWidth, LoHex: u.lo, HiHex: u.hi, Rev: cfg.Rev,
					Kernel: kernel, Stage: stage,
				}
				res, runErr := RunMapWorker(mctx, cfg.Bin, a, unitProgress(tel, r.processed), r.stop)
				<-sem

				mu.Lock()
				completedProcessed.Add(r.processed.Load())
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
					children := splitRemainder(frontier, H, keyLen, res.StopKey, u.hi,
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
func splitRemainder(frontier []string, H, keyLen int, cursor, hi string, freeCores int,
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
		cutKeys, _ = SplitRangeByIndex(frontier, H, keyLen, cursor, hi, parts-1)
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
// keyLen is the key width of mapOuts (this round's OUTPUT table) — the column
// kernel and the kink kernel's finalize round both produce H+2-keyed records,
// but kink's seed and mid-column stage rounds produce H+4-keyed ones, so this
// is always passed explicitly rather than derived from H (see mapPhase's
// keyLen doc for why an implicit default is unsafe here). stage tags the
// output filename ("" = column kernel, unchanged naming); a kink column runs
// several rounds at the same (H,col) and the rounds' outputs would otherwise
// collide on name (see mapPhase's matching outName comment).
func mergePhase(
	ctx context.Context,
	cfg SweepConfig,
	H, col int,
	mapOuts []string,
	sem chan struct{},
	keyLen int,
	stage string,
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

	cuts, err := SampleKeysMulti(mapOuts, H, keyLen, numRanges-1)
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

			outName := fmt.Sprintf("merge_h%d_c%d_r%d.bin", H, col, idx)
			if stage != "" {
				outName = fmt.Sprintf("merge_h%d_c%d_k%s_r%d.bin", H, col, stage, idx)
			}
			outPath := filepath.Join(cfg.RunDir, outName)
			a := MergeArgs{
				InPaths: mapOuts,
				H:       H,
				OutPath: outPath,
				Counter: cfg.CounterWidth,
				KLoHex:  los[idx],
				KHiHex:  his[idx],
				Rev:     cfg.Rev,
				KeyLen:  keyLen,
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
func writePerHeight(dir string, H, maxn int, hTri []*big.Int) error {
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
		v := big.NewInt(0)
		if n < len(hTri) && hTri[n] != nil {
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
func topHeightClosedForm(maxn int) *big.Int {
	if maxn <= 0 {
		return big.NewInt(0)
	}
	return pow3(maxn - 1)
}

// lowHeightRow returns the closed-form T(n,H) row for the trivial low strips
// H==1 and H==2, indexed by n (0 outside 1..maxn / below H):
//   T(n,1) = 1               (a single row of n cells)
//   T(n,2): T(2,2)=3, T(3,2)=10, T(n,2)=2·T(n-1,2)+T(n-2,2)+4  (n>=4)
// Returns nil for any other H. Both are verified exact against the a(20)
// triangle (results/ns_a20/Tnh_triangle.txt).
func lowHeightRow(H, maxn int) []*big.Int {
	if H != 1 && H != 2 {
		return nil
	}
	row := newBigRow(maxn + 1)
	if H == 1 {
		for n := 1; n <= maxn; n++ {
			row[n].SetInt64(1)
		}
		return row
	}
	for n := 2; n <= maxn; n++ {
		switch n {
		case 2:
			row[n].SetInt64(3)
		case 3:
			row[n].SetInt64(10)
		default:
			// row[n] = 2*row[n-1] + row[n-2] + 4
			row[n].Lsh(row[n-1], 1)
			row[n].Add(row[n], row[n-2])
			row[n].Add(row[n], big.NewInt(4))
		}
	}
	return row
}

// contributeLowHeight adds the closed-form row for H==1 or H==2 to the triangle
// (and writes its per-height row if requested), doing no map/merge.
func contributeLowHeight(H, maxn int, triangle []*big.Int, cfg SweepConfig) {
	row := lowHeightRow(H, maxn)
	for n := 1; n <= maxn && n < len(triangle); n++ {
		triangle[n].Add(triangle[n], row[n])
	}
	if cfg.PerHeightOut != "" {
		if werr := writePerHeight(cfg.PerHeightOut, H, maxn, row); werr != nil {
			fmt.Fprintf(os.Stderr, "per-height write H=%d: %v\n", H, werr)
		}
	}
}

// pow3 returns 3^k as a *big.Int, for k>=0 (0 for k<0). Negative-exponent
// division (needed once the true n>=2k+1 diagonal threshold is wired) is
// handled by applyPow3, not here — see the guard-threshold fix.
func pow3(k int) *big.Int {
	v := big.NewInt(1)
	if k < 0 {
		return v
	}
	three := big.NewInt(3)
	v.Exp(three, big.NewInt(int64(k)), nil)
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
func contributePoleHeight(maxn int, triangle []*big.Int, cfg SweepConfig) {
	H := maxn - 1
	row := newBigRow(maxn + 1)
	row[H] = pow3(maxn - 2)
	row[maxn] = new(big.Int).Mul(big.NewInt(int64(25*maxn-45)), pow3(maxn-4))
	if H < len(triangle) {
		triangle[H].Add(triangle[H], row[H])
	}
	if maxn < len(triangle) {
		triangle[maxn].Add(triangle[maxn], row[maxn])
	}
	if cfg.PerHeightOut != "" {
		if werr := writePerHeight(cfg.PerHeightOut, H, maxn, row); werr != nil {
			fmt.Fprintf(os.Stderr, "per-height write H=%d: %v\n", H, werr)
		}
	}
}

// diagCoeffs holds one Pk's integer-numerator Horner coefficients (leading
// term first, decimal strings — P10's constant term already exceeds int64,
// so a literal []int64 would silently fail to compile for it and would
// truncate for wider future Pk's) and the factorial divisor k!.
// T(n,n-k) = (Horner(coeffs)/kfact) * 3^(n-1-3k). Populated by
// diagCoeffTable below.
type diagCoeffs struct {
	coeffs []string
	kfact  int64
}

// diagCoeffTable holds j=1..10's coefficients (j=0 is the trivial pow3(n-1)
// case, handled separately). Source: docs/proofs/T-n-nm1.md,
// T-n-nm2-and-general.md (j=1,2 proven; j=3..6 data-pinned, exact in int64
// through the n these were originally used at); j=7,8 from
// scripts/pin_diagonal_k8_final.py / the derive-p{7,8} pipeline (big.Int-only
// from the start since their coefficients overflow int64 at the n they're
// used at); j=9,10 from scripts/derive_p9.py + scripts/derive_p10.py, freshly
// re-run via scripts/show_p9_p10_p11.py and copied verbatim (P_9: 6 of 10
// coefficients from theory alone, 4 from 4 of 7 real points n=19-22, 3 held
// out n=23-25 matched exactly; P_10: 7 of 11 from theory+the b7 recovered
// from P_9's own n^3 coefficient, 4 from 4 of 5 structurally-valid real
// points n=21-24, 1 held out n=25 matched exactly — see
// docs/a26-a30-diagonal-plan.md). All cases share one big.Int Horner
// evaluator (hornerDiag) instead of j=1..6 doing native int64/uint64
// arithmetic, since the guard-threshold fix (n>=2k+1, see applyPow3) invokes
// j=1..6 at larger n than before where int64 would overflow, and P_10's
// constant term already exceeds int64 outright.
var diagCoeffTable = map[int]diagCoeffs{
	1: {[]string{"25", "-45"}, 1},
	2: {[]string{"625", "-2459", "1134"}, 2},
	3: {[]string{"15625", "-100050", "122213", "-32940"}, 6},
	4: {[]string{"390625", "-3596250", "8099843", "-6462882", "1752840"}, 24},
	5: {[]string{"9765625", "-120546875", "425836625", "-650171245", "422003550", "76975920"}, 120},
	6: {[]string{"244140625", "-3861328125", "19486496875", "-47366857935", "55373728180", "946828380", "-32099353920"}, 720},
	// j=7: P_7 is data-pinned and validated at scale by the a(23) swept H=16
	// row (T(23,16)=4492550651512074, T(22,15)=1035856891052731).
	7: {[]string{"6103515625", "-119765625000", "812310625000", "-2839739579250", "5194366339015", "-1878923357430", "-6841564107480", "7756630081200"}, 5040},
	// j=8: P_8 is pinned from a(24)'s real T(24,16)=42594477635772598 (n=17..24,
	// 8 points, leading coeff fixed at 25^8/8! by the confirmed conjecture) --
	// see scripts/pin_diagonal_k8_final.py, whose fit reproduces all 8 defining
	// points exactly and whose result matches the pre-a(24) falsifiable
	// sum-of-roots prediction exactly.
	8: {[]string{"152587890625", "-3625976562500", "31658675781250", "-149222374175000", "391357255277905", "-350057694296660", "-718224955399380", "2136536485853040", "-923712586957440"}, 40320},
	// j=9: P_9, fully derived and validated (scripts/derive_p9.py,
	// scripts/derive_p9_calibrate.py). Leading coeff 25^9/9! emerged
	// independently, not assumed.
	9: {[]string{
		"3814697265625", "-107720947265625", "1172546074218750", "-7126125723281250",
		"25246485663128625", "-39217219391133945", "-44784313962337720", "312218815384892340",
		"-359168984859479760", "17928204588927360",
	}, 362880},
	// j=10: P_10, fully derived and validated (scripts/derive_p10.py).
	// Leading coeff 25^10/10! confirmed independently.
	10: {[]string{
		"95367431640625", "-3151702880859375", "41724067382812500", "-316409147402343750",
		"1450416433150453125", "-3370526923710995055", "-1108292379978242050", "31805482385795516100",
		"-69735093253554241800", "32190356082435763680", "25618243319042572800",
	}, 3628800},
	// j=11: P_11, fully derived and validated (scripts/derive_p11.py). The
	// validated P_9 and P_10 fits pin the shared universal series symbols
	// {a7..a10,b8..b10} exactly, so 10 of 12 coefficients emerge clean from
	// theory alone; only a11,b11 (degrees n^0,n^1) needed new data, supplied by
	// the two fresh sweeps T(26,15)=5614506356004078534 (results/ns_a26) and
	// T(27,16)=27798973373501478242 (results/ns_a27). The three a25 diagonal-11
	// points n=23,24,25 (held out of both the fit and the shared-symbol solve)
	// matched exactly; leading coeff 25^11/11! confirmed independently.
	11: {[]string{
		"2384185791015625", "-91056823730468750", "1437517181396484375", "-13264842209179687500",
		"76160367268876171875", "-243501035699144280750", "120586120186765409825", "2497738719648063722600",
		"-9207797682124933481700", "10269478266342644052000", "3325021854753536899200", "5868473845727607206400",
	}, 39916800},
	// j=12: P_12, fully derived and validated (scripts/derive_p12.py). The
	// validated P_9/P_10/P_11 fits pin the shared symbols {a7..a11,b8..b11}
	// exactly (12 eqns, 9 unknowns, consistent), so 11 of 13 coefficients come
	// clean from theory; only a12,b12 (degrees n^0,n^1) needed new data, from
	// T(26,14)=8490578913536448064 (results/ns_a26) and
	// T(27,15)=44416775012217775973 (results/ns_a27). The a25 diagonal-12 point
	// T(25,13)=1573134737210737385, held out of both the fit and the
	// shared-symbol solve, matched exactly; leading coeff 25^12/12! confirmed.
	// Keeps a(29)'s top real height at H=maxn-12 (same tier as a28's H=maxn-11).
	12: {[]string{
		"59604644775390625", "-2602958679199218750", "48223920440673828125", "-530815263596191406250",
		"3721840065507802734375", "-15512118396389744456250", "21149152791035920752695", "157168222110058996109130",
		"-936571784113889621399900", "1860945781255305037306200", "-561954556767083249661120", "2518353204096205882465920",
		"-12192370946767873838592000",
	}, 479001600},
	// j=13: P_13, fully derived and validated (scripts/derive_p13.py). The
	// validated P_9..P_12 fits pin the shared symbols {a7..a12,b8..b12}
	// exactly, so 12 of 14 coefficients come clean from theory; only a13,b13
	// (degrees n^0,n^1) needed new data, fit from T(30,17)=9142099138689979555656
	// (results/ns_a30) and T(31,18)=45518261981941858305944 (results/ns_a31).
	// The three older diagonal-13 points T(27,14),T(28,15),T(29,16), held out of
	// both the fit and the shared-symbol solve, all matched exactly; leading
	// coeff 25^13/13! confirmed. Wiring it makes H=maxn-13 closed-form, dropping
	// a(32)'s top real height a tier (H19->H18).
	13: {[]string{
		"1490116119384765625", "-73735713958740234375", "1581930904388427734375", "-20438647987884521484375",
		"171498867051782080078125", "-897242973195286876640625", "2053473678621559440657125", "7845602899216787491993635",
		"-78302966517647904123999050", "242568775590879458927220300", "-252892500470648129748781800", "630295671430278785315535840",
		"-4709212944929227143077529600", "8516420444581467205615027200",
	}, 6227020800},
	// j=14: P_14, derived via scripts/derive_pk_fast.py (exp recurrence). The
	// validated P_9..P_13 fits pin the shared symbols {a7..a13,b8..b13}
	// exactly, so 13 of 15 coefficients come clean from theory; only a14,b14
	// (degrees n^0,n^1) needed new data, fit from T(29,15) and T(30,16)
	// (results/ns_a29, results/ns_a30). The two later diagonal-14 points
	// T(31,17) and T(32,18) (results/ns_a31, results/ns_a32), held out of the
	// fit, both matched exactly; leading coeff 25^14/14! confirmed. Wiring it
	// makes H=maxn-14 closed-form, keeping a(33)'s top real height at H18
	// (H19 without it). P_15 is deliberately NOT wired: it is held out so a(33)
	// sweeps H18 and yields the independent holdout point T(33,18).
	14: {[]string{
		"37252902984619140625", "-2072393894195556640625", "50912246036529541015625", "-761843525055694580078125",
		"7524678110464896240234375", "-48052027303805350998046875", "157448856577961057749371875", "276655470142052990154351185",
		"-5583936647603503419750059540", "25191124931485376140721243800", "-47958023503387714879301084400", "118184880567640594471489711440",
		"-979514007904340174674683668160", "3638916058760447487430557542400", "-4028797193164605150126008371200",
	}, 87178291200},
	// j=15: P_15, derived via scripts/derive_pk_fast.py (exp recurrence). The
	// validated P_9..P_14 fits pin the shared symbols {a7..a14,b8..b14}
	// exactly, so 14 of 16 coefficients come clean from theory; only a15,b15
	// (degrees n^0,n^1) needed new data, fit from T(31,16) and T(32,17)
	// (results/ns_a31, results/ns_a32). The diagonal-15 point T(33,18) =
	// 2965403643769893816836542 (results/ns_a33), HELD OUT of the fit, matched
	// the swept value exactly (a33 was run with P_15 unwired precisely to
	// produce this independent holdout); leading coeff 25^15/15! confirmed.
	// Wiring it makes H=maxn-15 closed-form, keeping a(34)'s top real height at
	// H18 (H19 without it).
	15: {[]string{
		"931322574615478515625", "-57846307754516601562500", "1611761021614074707031250", "-27620633003425598144531250",
		"316736418664104003906250000", "-2416046782053819856347656250", "10461322884210958342060156250", "1967893236430787060707991250",
		"-346618516939812097631010184825", "2203970151840239765899986819750", "-6398534829863605593928976949100", "17955993014682160383586429971000",
		"-146852693386847802168160405132800", "824216279306486381670291956424000", "-1935618838774923672066722617670400", "1370506748049564268873803929856000",
	}, 1307674368000},
}

// hornerDiag evaluates a diagCoeffs' numerator at N via big.Int Horner,
// divides exactly by kfact, and applies 3^exp (exp may be negative — see
// applyPow3).
func hornerDiag(N int64, c diagCoeffs, exp int) *big.Int {
	num := new(big.Int)
	if _, ok := num.SetString(c.coeffs[0], 10); !ok {
		panic("hornerDiag: bad coefficient literal " + c.coeffs[0])
	}
	for _, coefStr := range c.coeffs[1:] {
		coef, ok := new(big.Int).SetString(coefStr, 10)
		if !ok {
			panic("hornerDiag: bad coefficient literal " + coefStr)
		}
		num.Mul(num, big.NewInt(N))
		num.Add(num, coef)
	}
	num.Quo(num, big.NewInt(c.kfact))
	return applyPow3(num, exp)
}

// applyPow3 multiplies num by 3^e (e>=0) or divides it exactly by 3^(-e)
// (e<0). The true diagonal validity threshold is n>=2k+1
// (docs/proofs/T-n-nm2-and-general.md), much looser than the old n>=3k+1
// dispatch guard — that guard existed only because pow3 had no
// negative-exponent path. In the n<3k+1 region the exponent n-1-3k is
// negative, but the numerator is proven exactly divisible by 3^|exponent|
// there; a nonzero remainder means a derivation or dispatch bug (invoked
// outside the proven-valid regime), not a value to silently round, so this
// panics rather than truncate.
func applyPow3(num *big.Int, e int) *big.Int {
	if e >= 0 {
		return num.Mul(num, pow3(e))
	}
	q, r := new(big.Int).QuoRem(num, pow3(-e), new(big.Int))
	if r.Sign() != 0 {
		panic(fmt.Sprintf("applyPow3: %s not exactly divisible by 3^%d (remainder %s) — derivation or dispatch bug, or called outside the proven n>=2k+1 regime", num, -e, r))
	}
	return q
}

// diagonalStripValid reports whether the k-th diagonal strip (H=maxn-k) can
// be filled by diagonalCell instead of a real column sweep. k<=15 now that
// P9..P15 are wired (case 9..15). The true structural threshold is n>=2k+1
// (docs/proofs/T-n-nm2-and-general.md); both sweep.go dispatch sites
// (sequential and overlap) must use this single helper so a future threshold
// or k-range change can't apply to only one path.
func diagonalStripValid(maxn, k int) bool {
	return k >= 2 && k <= 15 && maxn >= 2*k+1
}

// diagonalCell returns T(n, n-j), the j-th height-diagonal, for j=0..12
// (docs/proofs/T-n-nm1.md, T-n-nm2-and-general.md). j=0,1,2 are proven from first
// principles; j=3..10 are data-pinned from the triangle (leading 25^j/j!,
// integer-exact) and VALIDATED at scale by the a(23)/a(24)/a25 sweeps (their
// swept H=16..18 == k=5..7 reproduce the formulas exactly; j=8 is pinned from
// a(24)'s T(24,16), matched the pre-a(24) falsifiable sum-of-roots prediction
// exactly -- see results/k8-pinning.md, scripts/pin_diagonal_k8_final.py; j=9
// and j=10 are P_9/P_10 from scripts/derive_p9.py / derive_p10.py, see
// diagCoeffTable). Each is a degree-j polynomial in n times a power of 3; the
// numerator is divisible by j! for all valid n (verified), so the integer
// division is exact. The true validity threshold is n >= 2j+1
// (docs/proofs/T-n-nm2-and-general.md); below n=3j+1 the exponent n-1-3j is
// negative, handled by applyPow3's exact division path. diagonalStripValid's
// dispatch guard guarantees n >= 2j+1.
func diagonalCell(n, j int) *big.Int {
	if j == 0 {
		return pow3(n - 1)
	}
	c, ok := diagCoeffTable[j]
	if !ok {
		panic("diagonalCell: unsupported diagonal j")
	}
	return hornerDiag(int64(n), c, n-1-3*j)
}

// contributeDiagonalStrip adds the closed-form strip H=maxn-k (the k-th
// diagonal, k=0..10) to the triangle, doing no map/merge. The strip carries k+1
// cells: T(n, maxn-k) for n=maxn-k..maxn, where the offset j=n-(maxn-k) makes
// each cell the j-th diagonal at n, = diagonalCell(n, j). Callers guarantee
// maxn >= 2k+1 so every cell is in its validity range.
func contributeDiagonalStrip(maxn, k int, triangle []*big.Int, cfg SweepConfig) {
	H := maxn - k
	row := newBigRow(maxn + 1)
	for j := 0; j <= k; j++ {
		n := maxn - k + j
		row[n] = diagonalCell(n, j)
		if n < len(triangle) {
			triangle[n].Add(triangle[n], row[n])
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
func contributeTopHeight(maxn int, triangle []*big.Int, cfg SweepConfig) {
	v := topHeightClosedForm(maxn)
	if maxn < len(triangle) {
		triangle[maxn].Add(triangle[maxn], v)
	}
	if cfg.PerHeightOut != "" {
		hTri := newBigRow(maxn + 1)
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
