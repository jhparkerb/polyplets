package orchestrator

// lowheight_test.go — the trivial low strips H==1 and H==2 have closed forms
// (T(n,1)=1; T(n,2): 3, 10, then 2·T(n-1,2)+T(n-2,2)+4) and must be contributed
// WITHOUT a per-column worker sweep — the same waste class as the H==maxn top
// strip (BUGS-OF-SHAME C2).

import (
	"context"
	"testing"
)

// TestLowHeightFormula pins the H==1 and H==2 closed forms against the values
// in the a(20) triangle.
func TestLowHeightFormula(t *testing.T) {
	const maxn = 12
	// T(n,1) = 1 for every n.
	r1 := lowHeightRow(1, maxn)
	for n := 1; n <= maxn; n++ {
		if r1[n] != 1 {
			t.Errorf("T(%d,1)=%d want 1", n, r1[n])
		}
	}
	// T(n,2): triangle column 2, n=2..12.
	wantH2 := map[int]uint64{2: 3, 3: 10, 4: 27, 5: 68, 6: 167, 7: 406, 8: 983,
		9: 2376, 10: 5739, 11: 13858, 12: 33459}
	r2 := lowHeightRow(2, maxn)
	for n, want := range wantH2 {
		if r2[n] != want {
			t.Errorf("T(%d,2)=%d want %d", n, r2[n], want)
		}
	}
}

// TestLowHeightNoColumnWork proves a full a(maxn) sweep starts no column work at
// H==1 or H==2 while still reproducing the known triangle. On the unfixed engine
// both heights are swept column by column, so afterColumn fires and the test
// fails red.
func TestLowHeightNoColumnWork(t *testing.T) {
	known := loadKnownTriangle(t)
	dir := t.TempDir()
	cfg := baseCfg(t, dir) // maxn = resumeMaxn (8)
	low := 0
	cfg.afterColumn = func(H, col int) {
		if H == 1 || H == 2 {
			low++
			t.Errorf("column work started at low height H=%d col=%d", H, col)
		}
	}
	res, err := Run(context.Background(), cfg, nil)
	if err != nil {
		t.Fatalf("full sweep maxn=%d: %v", cfg.Maxn, err)
	}
	if low != 0 {
		t.Fatalf("%d columns ran at H=1/H=2 (want 0)", low)
	}
	checkTriangle(t, "low-height-no-column-work", known, res.Triangle)
}
