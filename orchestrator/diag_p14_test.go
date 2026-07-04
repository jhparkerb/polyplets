package orchestrator

// diag_p14_test.go — the H=maxn-14 strip is the k=14 diagonal, closed-form via
// P_14 (scripts/derive_pk_fast.py). Wiring it keeps a(33)'s top real height at
// H=maxn-15 = H18 (H=maxn-14 = H19 becomes closed-form, so the real sweep tops
// at H18 instead of H19). The validated P_9..P_13 fits pin the shared symbols
// {a7..a13,b8..b13} exactly, so 13 of 15 coefficients are clean from theory;
// a14,b14 were fit from T(29,15) and T(30,16). This test pins diagonalCell(n,14)
// against all four real diagonal-14 points — n=31,32 were HELD OUT of the
// derivation. Values exceed 2^64 (T(32,18) ~ 3.7e20), so they are compared as
// big.Int.

import (
	"math/big"
	"testing"
)

func TestDiagonalP14Formula(t *testing.T) {
	cases := []struct {
		n    int
		want string
	}{
		{29, "2611110015255604740530"},   // T(29,15), fit point (results/ns_a29)
		{30, "13969442417594351366268"},  // T(30,16), fit point (results/ns_a30)
		{31, "72837427176953272756444"},  // T(31,17), held out (results/ns_a31)
		{32, "371092643133615870167145"}, // T(32,18), held out (results/ns_a32)
	}
	for _, c := range cases {
		want, ok := new(big.Int).SetString(c.want, 10)
		if !ok {
			t.Fatalf("bad literal %q", c.want)
		}
		if got := diagonalCell(c.n, 14); got.Cmp(want) != 0 {
			t.Errorf("diagonalCell(%d,14) = T(%d,%d) = %d, want %s", c.n, c.n, c.n-14, got, c.want)
		}
	}
}

// TestDiagonalP14StripContribution drives the production strip path
// (contributeDiagonalStrip -> diagonalCell) for the k=14 strip at a33's scale
// (maxn=33), asserting every cell of the H=maxn-14 strip lands in the triangle.
func TestDiagonalP14StripContribution(t *testing.T) {
	const maxn, k = 33, 14
	if !diagonalStripValid(maxn, k) {
		t.Fatalf("k=14 strip must dispatch at maxn=%d", maxn)
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
