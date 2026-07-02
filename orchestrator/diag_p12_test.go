package orchestrator

// diag_p12_test.go — the H=maxn-12 strip is the k=12 diagonal, closed-form via
// P_12 (scripts/derive_p12.py). Wiring it keeps a(29)'s top real height at
// H=maxn-12, the same tier as a(28)'s H=maxn-11. The validated P_9/P_10/P_11
// fits pin the shared symbols exactly, so 11 of 13 coefficients are clean from
// theory; a12,b12 were fit from T(26,14) and T(27,15). This test pins
// diagonalCell(n,12) against all three real diagonal-12 points — the a25 point
// n=25 was HELD OUT of the derivation. Values fit in uint64 (all < 2^64), but
// they are compared as big.Int decimal strings for uniformity with P_11.

import (
	"math/big"
	"testing"
)

func TestDiagonalP12Formula(t *testing.T) {
	cases := []struct {
		n    int
		want string
	}{
		{25, "1573134737210737385"},  // T(25,13), held out (results/ns_a25)
		{26, "8490578913536448064"},  // T(26,14), fit point (results/ns_a26)
		{27, "44416775012217775973"}, // T(27,15), fit point (results/ns_a27)
	}
	for _, c := range cases {
		want, ok := new(big.Int).SetString(c.want, 10)
		if !ok {
			t.Fatalf("bad literal %q", c.want)
		}
		if got := diagonalCell(c.n, 12); got.Cmp(want) != 0 {
			t.Errorf("diagonalCell(%d,12) = T(%d,%d) = %d, want %s", c.n, c.n, c.n-12, got, c.want)
		}
	}
}

// TestDiagonalP12StripContribution drives the production strip path
// (contributeDiagonalStrip -> diagonalCell) for the k=12 strip at a29's scale
// (maxn=29), asserting every cell of the H=maxn-12 strip lands in the triangle.
func TestDiagonalP12StripContribution(t *testing.T) {
	const maxn, k = 29, 12
	if !diagonalStripValid(maxn, k) {
		t.Fatalf("k=12 strip must dispatch at maxn=%d", maxn)
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
