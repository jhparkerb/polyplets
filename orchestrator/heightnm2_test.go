package orchestrator

// heightnm2_test.go — the H=maxn-2 strip is closed-form (k=2, proven; see
// docs/proofs/T-n-nm2-and-general.md). It carries three cells:
//   T(maxn-2,maxn-2) = 3^(maxn-3)                         (diagonal)
//   T(maxn-1,maxn-2) = (25(maxn-1)-45)*3^(maxn-5)         (C1 at n=maxn-1)
//   T(maxn,maxn-2)   = (625*maxn^2-2459*maxn+1134)/2 * 3^(maxn-7)
// and must be contributed WITHOUT a column sweep (valid for maxn>=7).

import (
	"context"
	"math/big"
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
		// scripts/pin_diagonal_k8_final.py). Historically (a24/a25) only ever
		// invoked at n=25, back when the dispatch guard required n>=3*8+1=25;
		// the true validity threshold is n>=2*8+1=17 (applyPow3 handles the
		// resulting negative pow3 exponent below n=25 via exact division).
		// T(25,17) is a genuine EXTRAPOLATION beyond the 8 fitting points
		// (n=17..24) -- this pins the Go transcription against the Python
		// fit's own output, not an independent confirmation; a(25)'s own
		// sweep of H=17 is the actual confirmation, same as a(24) was for k=7.
		{25, 8, 187767529262410933}, // T(25,17)
		// n=17=2*8+1: the true validity threshold, well below the old n>=25
		// (3*8+1) guard. Exercises applyPow3's negative-exponent division
		// path for the first time on a REAL value (exponent 17-1-24=-8), not
		// just a self-consistency check -- this is the load-bearing proof
		// that the division path is correct, not just non-panicking. Source:
		// results/ns_a25/swept_rows.txt ===H9=== block, n=17.
		{17, 8, 603392972436}, // T(17,9)
		// j=9 (P_9): held-out real points n=19..25, source
		// results/ns_a25/swept_rows.txt. n=19=2*9+1 is the true validity
		// boundary (exponent 19-1-27=-9, exercises applyPow3's negative path).
		{19, 9, 24014057424024},    // T(19,10)
		{20, 9, 132107598093637},   // T(20,11)
		{21, 9, 694918765309300},   // T(21,12)
		{22, 9, 3521085234178586},  // T(22,13)
		{23, 9, 17278818571437182}, // T(23,14)
		{24, 9, 82463515269090962}, // T(24,15)
		{25, 9, 384025992867882686}, // T(25,16)
		// j=10 (P_10): held-out real points n=21..25, source
		// results/ns_a25/swept_rows.txt. n=21=2*10+1 is the true validity
		// boundary (exponent 21-1-30=-10).
		{21, 10, 962797249464752},    // T(21,11)
		{22, 10, 5257610926802452},   // T(22,12)
		{23, 10, 27605091155079103},  // T(23,13)
		{24, 10, 140166422140948001}, // T(24,14)
		{25, 10, 691293861738937174}, // T(25,15)
	}
	for _, c := range cases {
		want := new(big.Int).SetUint64(c.want)
		if got := diagonalCell(c.n, c.j); got.Cmp(want) != 0 {
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
