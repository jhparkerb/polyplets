package orchestrator

// poleheight_test.go — the H=maxn-1 strip (the run's pole) is closed-form:
//   T(maxn-1,maxn-1) = 3^(maxn-2)            (diagonal top of the strip)
//   T(maxn,maxn-1)   = (25*maxn-45)*3^(maxn-4)  (C1, PROVEN; see docs/proofs)
// It must be contributed WITHOUT a column sweep — it is ~24% of run wall.

import (
	"context"
	"testing"
)

// TestPoleHeightFormula pins both pole-strip closed forms against known triangle
// values. This is the correctness gate: a wrong C1 formula (e.g. a botched proof)
// is caught here regardless of the proof's validity.
func TestPoleHeightFormula(t *testing.T) {
	// (maxn): T(maxn-1,maxn-1) diagonal, T(maxn,maxn-1) sub-diagonal — read off
	// results/ns_a20/Tnh_triangle.txt.
	cases := []struct {
		maxn       int
		wantDiag   uint64 // T(maxn-1, maxn-1) = 3^(maxn-2)
		wantSubdia uint64 // T(maxn, maxn-1) = (25*maxn-45)*3^(maxn-4)
	}{
		{4, 9, 55},        // T(3,3)=9,    T(4,3)=55
		{5, 27, 240},      // T(4,4)=27,   T(5,4)=240
		{8, 729, 12555},   // T(7,7)=729,  T(8,7)=12555
		{21, pow3(19), 61987278240}, // T(20,20)=3^19, T(21,20)=61,987,278,240
	}
	for _, c := range cases {
		tri := make([]uint64, c.maxn+1)
		contributePoleHeight(c.maxn, tri, SweepConfig{})
		if tri[c.maxn-1] != c.wantDiag {
			t.Errorf("maxn=%d: T(%d,%d)=%d want %d", c.maxn, c.maxn-1, c.maxn-1, tri[c.maxn-1], c.wantDiag)
		}
		if tri[c.maxn] != c.wantSubdia {
			t.Errorf("maxn=%d: T(%d,%d)=%d want %d", c.maxn, c.maxn, c.maxn-1, tri[c.maxn], c.wantSubdia)
		}
	}
}

// TestPoleHeightNoColumnWork proves a full a(maxn) sweep starts no column work
// at H==maxn-1 while still reproducing the known triangle. On the pre-C1 engine
// the pole is swept, so afterColumn fires and the test fails red.
func TestPoleHeightNoColumnWork(t *testing.T) {
	known := loadKnownTriangle(t)
	dir := t.TempDir()
	cfg := baseCfg(t, dir) // maxn = resumeMaxn (8); pole = H7
	pole := 0
	cfg.afterColumn = func(H, col int) {
		if H == cfg.Maxn-1 {
			pole++
			t.Errorf("column work started at pole height H=%d (maxn-1) col=%d", H, col)
		}
	}
	res, err := Run(context.Background(), cfg, nil)
	if err != nil {
		t.Fatalf("full sweep maxn=%d: %v", cfg.Maxn, err)
	}
	if pole != 0 {
		t.Fatalf("%d columns ran at pole height H=%d (want 0)", pole, cfg.Maxn-1)
	}
	checkTriangle(t, "pole-height-no-column-work", known, res.Triangle)
}
