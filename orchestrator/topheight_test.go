package orchestrator

// topheight_test.go — the top strip H==maxn is the closed-form diagonal
// T(maxn,maxn)=3^(maxn-1) and must be contributed WITHOUT any column sweep.
// Enumerating it would brute-force all 3^(maxn-1) diagonals — the single most
// expensive strip of the run — to rederive a known number.

import (
	"context"
	"math/big"
	"path/filepath"
	"testing"
)

// TestTopHeightClosedForm pins the diagonal formula T(n,n)=3^(n-1).
func TestTopHeightClosedForm(t *testing.T) {
	cases := []struct {
		n    int
		want uint64
	}{{1, 1}, {2, 3}, {3, 9}, {4, 27}, {5, 81}, {8, 2187}, {14, 1594323}}
	for _, c := range cases {
		want := new(big.Int).SetUint64(c.want)
		if got := topHeightClosedForm(c.n); got.Cmp(want) != 0 {
			t.Errorf("topHeightClosedForm(%d)=%d want %d", c.n, got, c.want)
		}
	}
}

// TestTopHeightNoWorkers proves the top strip is computed with NO map/merge: it
// runs ONLY H==maxn with bogus worker binaries, so any attempt to spawn a map
// or merge worker fails to exec and surfaces as an error. Success with the
// correct closed-form total means no enumeration ran. On the unfixed engine the
// top strip is swept, so RunMapWorker execs /nonexistent and Run returns an
// error — the test fails red.
func TestTopHeightNoWorkers(t *testing.T) {
	const maxn = 9
	const want = 6561 // 3^(maxn-1) = 3^8
	dir := t.TempDir()
	cfg := SweepConfig{
		Maxn:            maxn,
		Fold:            true,
		Cores:           4,
		RAM:             4 << 20,
		RunDir:          dir,
		SpillDir:        dir,
		CheckpointPath:  filepath.Join(dir, "POLYCKPT"),
		CheckpointEvery: 0,
		Rev:             "test",
		Heights:         []int{maxn}, // the top strip only
		Bin: WorkerBin{
			MapWorker:   "/nonexistent/map_worker",
			MergeWorker: "/nonexistent/merge_worker",
		},
	}
	res, err := Run(context.Background(), cfg, nil)
	if err != nil {
		t.Fatalf("top strip H=%d spawned a worker (or failed): %v", maxn, err)
	}
	if res.Triangle[maxn].Cmp(big.NewInt(want)) != 0 {
		t.Fatalf("T(%d,%d)=%d want %d", maxn, maxn, res.Triangle[maxn], want)
	}
}

// TestTopHeightNoColumnWork proves that during a full a(maxn) computation the
// orchestrator never starts column work at the top height. A real sweep records
// every completed column via the afterColumn seam and asserts none is at
// H==maxn, while the total still matches the known a(n). On the unfixed engine
// the top strip is swept column by column, so afterColumn fires at H==maxn and
// the test fails red.
func TestTopHeightNoColumnWork(t *testing.T) {
	known := loadKnownTriangle(t)
	dir := t.TempDir()
	cfg := baseCfg(t, dir) // maxn = resumeMaxn (8), real workers in ../build/ns
	topCols := 0
	cfg.afterColumn = func(H, col int) {
		if H == cfg.Maxn {
			topCols++
			t.Errorf("column work started at top height H=%d col=%d", H, col)
		}
	}
	res, err := Run(context.Background(), cfg, nil)
	if err != nil {
		t.Fatalf("full sweep maxn=%d: %v", cfg.Maxn, err)
	}
	if topCols != 0 {
		t.Fatalf("%d columns ran at top height H=%d (want 0)", topCols, cfg.Maxn)
	}
	checkTriangle(t, "top-height-no-column-work", known, res.Triangle)
}
