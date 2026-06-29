package orchestrator

// heightnm2_test.go — the H=maxn-2 strip is closed-form (k=2, proven; see
// docs/proofs/T-n-nm2-and-general.md). It carries three cells:
//   T(maxn-2,maxn-2) = 3^(maxn-3)                         (diagonal)
//   T(maxn-1,maxn-2) = (25(maxn-1)-45)*3^(maxn-5)         (C1 at n=maxn-1)
//   T(maxn,maxn-2)   = (625*maxn^2-2459*maxn+1134)/2 * 3^(maxn-7)
// and must be contributed WITHOUT a column sweep (valid for maxn>=7).

import (
	"context"
	"testing"
)

// TestHeightNm2Formula pins all three strip cells against known triangle values
// — the correctness gate (a wrong k=2 formula is caught regardless of the proof).
func TestHeightNm2Formula(t *testing.T) {
	cases := []struct {
		maxn               int
		wantDiag           uint64 // T(maxn-2,maxn-2)
		wantSub1, wantSub2 uint64 // T(maxn-1,maxn-2), T(maxn,maxn-2)
	}{
		{7, 81, 729, 7273},          // T(5,5)=3^4, T(6,5)=945? -> see below
		{8, 243, 3510, 32193},       // T(6,6)=243, T(7,6)=3510, T(8,6)=32193
		{21, pow3(18), 0, 0},        // diagonal only checked structurally at 21
	}
	// exact triangle values: maxn=7 -> T(5,5)=81, T(6,5)=945, T(7,5)=7273.
	cases[0].wantSub1, cases[0].wantSub2 = 945, 7273
	for _, c := range cases {
		tri := make([]uint64, c.maxn+1)
		contributeHeightNminus2(c.maxn, tri, SweepConfig{})
		if tri[c.maxn-2] != c.wantDiag {
			t.Errorf("maxn=%d diag T(%d,%d)=%d want %d", c.maxn, c.maxn-2, c.maxn-2, tri[c.maxn-2], c.wantDiag)
		}
		if c.wantSub1 != 0 && tri[c.maxn-1] != c.wantSub1 {
			t.Errorf("maxn=%d T(%d,%d)=%d want %d", c.maxn, c.maxn-1, c.maxn-2, tri[c.maxn-1], c.wantSub1)
		}
		if c.wantSub2 != 0 && tri[c.maxn] != c.wantSub2 {
			t.Errorf("maxn=%d T(%d,%d)=%d want %d", c.maxn, c.maxn, c.maxn-2, tri[c.maxn], c.wantSub2)
		}
	}
}

// TestHeightNm2NoColumnWork proves a full sweep starts no column work at
// H=maxn-2 while still reproducing the known triangle. Pre-fix the strip is
// swept, so afterColumn fires and the test fails red.
func TestHeightNm2NoColumnWork(t *testing.T) {
	known := loadKnownTriangle(t)
	dir := t.TempDir()
	cfg := baseCfg(t, dir) // maxn = resumeMaxn (8) >= 7; H=maxn-2 = 6
	hit := 0
	cfg.afterColumn = func(H, col int) {
		if H == cfg.Maxn-2 {
			hit++
			t.Errorf("column work started at H=maxn-2=%d col=%d", H, col)
		}
	}
	res, err := Run(context.Background(), cfg, nil)
	if err != nil {
		t.Fatalf("full sweep maxn=%d: %v", cfg.Maxn, err)
	}
	if hit != 0 {
		t.Fatalf("%d columns ran at H=maxn-2=%d (want 0)", hit, cfg.Maxn-2)
	}
	checkTriangle(t, "height-nm2-no-column-work", known, res.Triangle)
}
