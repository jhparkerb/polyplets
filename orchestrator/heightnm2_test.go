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

// TestHeightNm2Formula pins the proven diagonals diagonalCell(n,j), j=0..4,
// against known triangle values (at valid n >= 3j+1) — the correctness gate:
// a wrong diagonal formula is caught regardless of the proof.
func TestHeightNm2Formula(t *testing.T) {
	cases := []struct {
		n, j int
		want uint64
	}{
		{8, 0, 2187},        // T(8,8)=3^7
		{8, 1, 12555},       // T(8,7)
		{7, 2, 7273},        // T(7,5)
		{8, 2, 32193},       // T(8,6)
		{10, 3, 1134865},    // T(10,7)
		{11, 3, 5001114},    // T(11,8)
		{13, 4, 189262009},  // T(13,9)
		{14, 4, 829622715},  // T(14,10)
		{16, 5, 32703766750},     // T(16,11)  (k=5, data-pinned; n=3j+1 boundary)
		{21, 5, 40713857307270},  // T(21,16)
		{19, 6, 5776897734667},   // T(19,13)  (k=6, data-pinned; n=3j+1 boundary)
		{21, 6, 106805460671316}, // T(21,15)
		{22, 7, 1035856891052731}, // T(22,15)  (k=7, big.Int; pinned+validated by a(23))
		{23, 7, 4492550651512074}, // T(23,16)
		{24, 7, 19111727676683781}, // T(24,17)  (k=7, validated by a(24))
		// k=8, big.Int; pinned by a(24)'s T(24,16) (results/k8-pinning.md,
		// scripts/pin_diagonal_k8_final.py). j=8 is only ever invoked at
		// n=25 (case 8 requires n>=3*8+1=25 for its pow3 exponent to be
		// non-negative; the maxn>=3k+1 strip dispatch guarantees this).
		// T(25,17) is a genuine EXTRAPOLATION beyond the 8 fitting points
		// (n=17..24) -- this pins the Go transcription against the Python
		// fit's own output, not an independent confirmation; a(25)'s own
		// sweep of H=17 is the actual confirmation, same as a(24) was for k=7.
		{25, 8, 187767529262410933}, // T(25,17)
	}
	for _, c := range cases {
		if got := diagonalCell(c.n, c.j); got != c.want {
			t.Errorf("diagonalCell(%d,%d) = T(%d,%d) = %d, want %d", c.n, c.j, c.n, c.n-c.j, got, c.want)
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
