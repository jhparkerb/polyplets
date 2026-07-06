package orchestrator

// diag_p13_test.go — the H=maxn-13 strip is the k=13 diagonal, closed-form via
// P_13 (scripts/derive_p13.py). Wiring it drops a(32)'s top real height one
// tier (H=maxn-13 = H19 becomes closed-form, so the real sweep tops at H18).
// The validated P_9..P_12 fits pin the shared symbols {a7..a12,b8..b12}
// exactly, so 12 of 14 coefficients are clean from theory; a13,b13 were fit
// from T(30,17) and T(31,18). This test pins diagonalCell(n,13) against all
// five real diagonal-13 points — n=27,28,29 were HELD OUT of the derivation.
// Values exceed 2^64 (T(31,18) ~ 4.6e19), so they are compared as big.Int.

import (
	"math/big"
	"testing"
)

func TestDiagonalP13Formula(t *testing.T) {
	cases := []struct {
		n    int
		want string
	}{
		{27, "63986427407097237332"},    // T(27,14), held out (results/ns_a27)
		{28, "343733831675681363476"},   // T(28,15), held out (results/ns_a28)
		{29, "1795111626265027715356"},  // T(29,16), held out (results/ns_a29)
		{30, "9142099138689979555656"},  // T(30,17), fit point (results/ns_a30)
		{31, "45518261981941858305944"}, // T(31,18), fit point (results/ns_a31)
	}
	for _, c := range cases {
		want, ok := new(big.Int).SetString(c.want, 10)
		if !ok {
			t.Fatalf("bad literal %q", c.want)
		}
		if got := diagonalCell(c.n, 13); got.Cmp(want) != 0 {
			t.Errorf("diagonalCell(%d,13) = T(%d,%d) = %d, want %s", c.n, c.n, c.n-13, got, c.want)
		}
	}
}

// TestDiagonalP13StripContribution drives the production strip path
// (contributeDiagonalStrip -> diagonalCell) for the k=13 strip at a32's scale
// (maxn=32), asserting every cell of the H=maxn-13 strip lands in the triangle.
func TestDiagonalP13StripContribution(t *testing.T) {
	const maxn, k = 32, 13
	if !diagonalStripValid(maxn, k) {
		t.Fatalf("k=13 strip must dispatch at maxn=%d", maxn)
	}
	triangle := newBigRow(maxn + 1)
	contributeDiagonalStrip(maxn, k, triangle, SweepConfig{})
	for j := 0; j <= k; j++ {
		n := maxn - k + j
		want := diagonalCell(n, j)
		if triangle[n].Cmp(want) != 0 {
			t.Errorf("strip cell T(%d,%d) = %d, want %d", n, maxn-k, triangle[n], want)
		}
	}
}
