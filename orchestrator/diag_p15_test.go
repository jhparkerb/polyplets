package orchestrator

// diag_p15_test.go — the H=maxn-15 strip is the k=15 diagonal, closed-form via
// P_15 (scripts/derive_pk_fast.py). Wiring it keeps a(34)'s top real height at
// H=maxn-16 = H18 (H=maxn-15 = H19 becomes closed-form, so the real sweep tops
// at H18 instead of H19). The validated P_9..P_14 fits pin the shared symbols
// {a7..a14,b8..b14} exactly, so 14 of 16 coefficients are clean from theory;
// a15,b15 were fit from T(31,16) and T(32,17). This test pins diagonalCell(n,15)
// against all three real diagonal-15 points — n=33 was HELD OUT of the
// derivation (a(33) was run with P_15 unwired precisely to produce it). Values
// exceed 2^64 (T(33,18) ~ 3.0e24), so they are compared as big.Int.

import (
	"math/big"
	"testing"
)

func TestDiagonalP15Formula(t *testing.T) {
	cases := []struct {
		n    int
		want string
	}{
		{31, "106848447386284024770292"},  // T(31,16), fit point (results/ns_a31)
		{32, "569579285523233406028051"},  // T(32,17), fit point (results/ns_a32)
		{33, "2965403643769893816836542"}, // T(33,18), held out (results/ns_a33)
	}
	for _, c := range cases {
		want, ok := new(big.Int).SetString(c.want, 10)
		if !ok {
			t.Fatalf("bad literal %q", c.want)
		}
		if got := diagonalCell(c.n, 15); got.Cmp(want) != 0 {
			t.Errorf("diagonalCell(%d,15) = T(%d,%d) = %d, want %s", c.n, c.n, c.n-15, got, c.want)
		}
	}
}

// TestDiagonalP15StripContribution drives the production strip path
// (contributeDiagonalStrip -> diagonalCell) for the k=15 strip at a34's scale
// (maxn=34), asserting every cell of the H=maxn-15 strip lands in the triangle.
func TestDiagonalP15StripContribution(t *testing.T) {
	const maxn, k = 34, 15
	if !diagonalStripValid(maxn, k) {
		t.Fatalf("k=15 strip must dispatch at maxn=%d", maxn)
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
