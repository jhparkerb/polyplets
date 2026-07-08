// sweep_sharded.go — orchestrator wiring for the sharded-private column
// sweep (core/kink_sharded.h, redesign branch). Opt-in and parallel to
// sweepHeightKink's standard mapPhase/mergePhase-per-round path: today's
// production sweep synchronizes ALL workers at every one of a column's
// H+1 rounds (seed, H mid-column stage transitions, finalize); this
// synchronizes at exactly ONE point per column instead.
//
// See core/kink_sharded.h's header comment for the full design and the
// permissiveBudget correctness mechanism, test/gate_kink_sharded.cpp for
// the library-level multi-column-chain validation, and
// test/gate_kink_sharded_worker_cli.cpp for the real-subprocess CLI-level
// validation this file's own dispatch mirrors.
//
// STATUS: implemented and locally validated (both gates above), NOT yet
// exercised at production scale or wired into cmd/orchestrate's default
// path -- sweepColumnSharded exists as a standalone, independently
// testable function so it can be validated against small, known a(n)
// values (the existing --compare machinery) before ever being trusted
// for a real term, per the standing "validate at scale before record"
// practice.
package orchestrator

import (
	"context"
	"fmt"
	"io"
	"math/big"
	"os"
	"path/filepath"
	"sync"
	"sync/atomic"
	"time"
)

// sweepColumnSharded runs ONE kink column via the sharded-private design:
// split the column's source frontier (keyLen H+2) into K disjoint
// key-range shards, run each shard through map_worker's
// --kernel kink --stage sharded mode in parallel (seed + all H
// mid-column stages, no cross-shard merge at any point during this
// phase), then merge all K shards' outputs via exactly ONE
// --stage finalize call (which already merges multiple --in paths before
// running kinkFinalizeColumn -- see worker/map_worker.cpp's own comment).
// Returns the next column's frontier paths, this column's triangle
// contributions, and the accumulated resource accounting.
func sweepColumnSharded(
	ctx context.Context,
	cfg SweepConfig,
	H, col, K int,
	frontier []string,
	sem chan struct{},
) ([]string, []map[int]map[int]*big.Int, Acct, error) {

	if H == cfg.Maxn {
		return nil, nil, Acct{}, fmt.Errorf("sweepColumnSharded: column work started at top height H=%d (maxn=%d); closed-form short-circuit was bypassed", H, cfg.Maxn)
	}
	if len(frontier) == 0 {
		return nil, nil, Acct{}, nil
	}

	inKeyLen := columnKeyLen(H)

	if K < 1 {
		K = 1
	}
	cuts, err := SampleKeysMulti(frontier, H, inKeyLen, K-1)
	if err != nil {
		return nil, nil, Acct{}, fmt.Errorf("H=%d col=%d sharded sample: %w", H, col, err)
	}
	los, his := cutsToBounds(cuts)
	actualK := len(los)

	type shardResult struct {
		idx     int
		outPath string
		result  WorkerResult
		err     error
	}
	results := make([]shardResult, actualK)

	var wg sync.WaitGroup
	for i := 0; i < actualK; i++ {
		wg.Add(1)
		go func(idx int) {
			defer wg.Done()
			outPath := filepath.Join(cfg.RunDir, fmt.Sprintf("shard_h%d_c%d_k%d.bin", H, col, idx))
			a := MapArgs{
				InPaths: frontier, H: H, Maxn: cfg.Maxn, Fold: cfg.Fold,
				RAM: cfg.RAM, SpillDir: cfg.SpillDir, OutPath: outPath,
				Counter: cfg.CounterWidth, LoHex: los[idx], HiHex: his[idx],
				Rev: cfg.Rev, Kernel: "kink", Stage: "sharded",
			}
			var res WorkerResult
			var runErr error
			if cfg.Pool != nil {
				res, runErr = cfg.Pool.RunMap(a, nil, nil)
			} else {
				sem <- struct{}{}
				res, runErr = RunMapWorker(ctx, cfg.Bin, a, nil, nil)
				<-sem
			}
			results[idx] = shardResult{idx: idx, outPath: outPath, result: res, err: runErr}
		}(i)
	}
	wg.Wait()

	var shardOuts []string
	var triContribs []map[int]map[int]*big.Int
	var acct Acct
	for _, r := range results {
		if r.err != nil {
			return nil, nil, Acct{}, fmt.Errorf("H=%d col=%d sharded unit %d [%s,%s): %w",
				H, col, r.idx, los[r.idx], his[r.idx], r.err)
		}
		if r.result.OutRecords > 0 {
			shardOuts = append(shardOuts, r.outPath)
		} else {
			removeRun(r.outPath)
		}
		triContribs = append(triContribs, r.result.TriContribs)
		acct.Add(r.result.Acct)
	}

	if len(shardOuts) == 0 {
		// Every shard produced nothing (an empty/exhausted frontier) --
		// same terminal condition sweepHeightKink checks after finalize.
		return nil, triContribs, acct, nil
	}

	// The one cross-shard synchronization point: a single finalize call
	// over every shard's output. map_worker's --stage finalize already
	// merges multiple --in paths (readRangedRunFiles: read all, sort,
	// dedup once) before running the real, unmodified kinkFinalizeColumn.
	finalOut := filepath.Join(cfg.RunDir, fmt.Sprintf("final_h%d_c%d.bin", H, col))
	fa := MapArgs{
		InPaths: shardOuts, H: H, Maxn: cfg.Maxn, Fold: cfg.Fold,
		RAM: cfg.RAM, SpillDir: cfg.SpillDir, OutPath: finalOut,
		Counter: cfg.CounterWidth, Rev: cfg.Rev, Kernel: "kink", Stage: "finalize",
	}
	var finalRes WorkerResult
	var finalErr error
	if cfg.Pool != nil {
		finalRes, finalErr = cfg.Pool.RunMap(fa, nil, nil)
	} else {
		sem <- struct{}{}
		finalRes, finalErr = RunMapWorker(ctx, cfg.Bin, fa, nil, nil)
		<-sem
	}
	for _, p := range shardOuts {
		removeRun(p)
	}
	if finalErr != nil {
		return nil, nil, Acct{}, fmt.Errorf("H=%d col=%d sharded finalize: %w", H, col, finalErr)
	}
	acct.Add(finalRes.Acct)

	var nextFrontier []string
	if finalRes.OutRecords > 0 {
		nextFrontier = []string{finalOut}
	} else {
		removeRun(finalOut)
	}

	return nextFrontier, triContribs, acct, nil
}

// sweepHeightKinkSharded drives a whole height's column-by-column sweep
// using sweepColumnSharded, mirroring sweepHeightKink's own outer column
// loop shape but WITHOUT its checkpoint/resume/telemetry/overlap-heights
// machinery -- this is a validation driver (see ValidateShardedHeight
// below), not a production dispatch path. Wiring the sharded design into
// sweepHeightKink's full machinery is deliberately a separate, later step
// once this has been validated at real scale.
func sweepHeightKinkSharded(ctx context.Context, cfg SweepConfig, H, maxn, K int, seed []string, sem chan struct{}) ([]*big.Int, error) {
	hTri := newBigRow(maxn + 1)
	frontier := seed
	for col := 0; col <= maxn && len(frontier) > 0; col++ {
		next, triContribs, _, err := sweepColumnSharded(ctx, cfg, H, col, K, frontier, sem)
		if err != nil {
			return nil, fmt.Errorf("col=%d: %w", col, err)
		}
		addTriContribs(hTri, triContribs, maxn)
		frontier = next
	}
	return hTri, nil
}

// ValidateShardedHeight runs ONE real height sweep two ways -- the
// standard column kernel (sweepHeight, the trusted reference) and the
// sharded-private kink design (sweepHeightKinkSharded, K shards) -- and
// reports whether their triangle rows match exactly. Exported so
// cmd/orchestrate can offer a real CLI entry point for validating this
// design at whatever scale the caller chooses, without touching
// sweepHeightKink's production dispatch path or writing any checkpoint/
// combine output. mismatches, if any, are one string per differing n:
// "n=<n>: reference=<v> sharded=<v>".
func ValidateShardedHeight(ctx context.Context, cfg SweepConfig, H, K int, seed []string, sem chan struct{}) (match bool, mismatches []string, err error) {
	tel, err := newTelemetry(cfg, time.Now())
	if err != nil {
		return false, nil, fmt.Errorf("telemetry: %w", err)
	}
	activeHeights := new(atomic.Int32)
	activeHeights.Store(1)
	noopCkpt := func(int, int, []string, []*big.Int) {}

	// Both sweeps consume (and eventually delete, via removeRuns) their own
	// frontier files as they iterate columns -- give each its own copy of
	// the seed so the reference run's normal cleanup can't delete the
	// sharded run's input out from under it.
	refSeed, err := copySeedFiles(seed, "ref")
	if err != nil {
		return false, nil, fmt.Errorf("copy seed for reference: %w", err)
	}
	shSeed, err := copySeedFiles(seed, "sharded")
	if err != nil {
		return false, nil, fmt.Errorf("copy seed for sharded: %w", err)
	}

	refTri, _, err := sweepHeight(ctx, cfg, H, 0, refSeed, noopCkpt, tel, sem, activeHeights)
	if err != nil {
		return false, nil, fmt.Errorf("reference sweepHeight: %w", err)
	}

	shTri, err := sweepHeightKinkSharded(ctx, cfg, H, cfg.Maxn, K, shSeed, sem)
	if err != nil {
		return false, nil, fmt.Errorf("sharded sweep: %w", err)
	}

	for n := 1; n <= cfg.Maxn; n++ {
		rv := bigOrZero(refTri, n)
		sv := bigOrZero(shTri, n)
		if rv.Cmp(sv) != 0 {
			mismatches = append(mismatches, fmt.Sprintf("n=%d: reference=%s sharded=%s", n, rv, sv))
		}
	}
	return len(mismatches) == 0, mismatches, nil
}

func bigOrZero(row []*big.Int, n int) *big.Int {
	if n < len(row) && row[n] != nil {
		return row[n]
	}
	return new(big.Int)
}

// copySeedFiles copies each path in `paths` (and its .idx sidecar, if
// present) to a fresh "<original>.<suffix>copy" path, so two independent
// sweeps can each consume (and eventually delete, via the normal
// removeRuns cleanup every sweepHeightFn does as it advances columns)
// their own frontier files without racing each other.
func copySeedFiles(paths []string, suffix string) ([]string, error) {
	out := make([]string, len(paths))
	for i, p := range paths {
		dst := p + "." + suffix + "copy"
		if err := copyFile(p, dst); err != nil {
			return nil, err
		}
		if err := copyFile(p+".idx", dst+".idx"); err != nil && !os.IsNotExist(err) {
			return nil, err
		}
		out[i] = dst
	}
	return out, nil
}

func copyFile(src, dst string) error {
	in, err := os.Open(src)
	if err != nil {
		return err
	}
	defer in.Close()
	out, err := os.Create(dst)
	if err != nil {
		return err
	}
	defer out.Close()
	_, err = io.Copy(out, in)
	return err
}
