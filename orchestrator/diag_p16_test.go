package orchestrator

// diag_p16_test.go — the H=maxn-16 strip is the k=16 diagonal, closed-form via
// P_16 (scripts/derive_pk_fast.py). Wiring it keeps a(36)'s top real height at
// H=maxn-17 = H19 (H=maxn-16 = H20 becomes closed-form). The validated
// P_9..P_15 fits pin the shared symbols, so only a16,b16 were fit — from
// T(33,17) and T(34,18). This test pins diagonalCell(n,16) against all three
// real diagonal-16 points — n=35 was HELD OUT of the derivation (a(35) was run
// with P_16 unwired precisely to produce it, deriver holdout(1)=True). Values
// exceed 2^64, so they are compared as big.Int.

import (
	"math/big"
	"testing"
)

func TestDiagonalP16Formula(t *testing.T) {
	cases := []struct {
		n    int
		want string
	}{
		{33, "4382793740312244017806517"},   // T(33,17), fit point (results/ns_a33)
		{34, "23288787870043631158670332"},  // T(34,18), fit point (results/ns_a34)
		{35, "121081244529132538941157409"}, // T(35,19), held out (results/ns_a35)
	}
	for _, c := range cases {
		want, ok := new(big.Int).SetString(c.want, 10)
		if !ok {
			t.Fatalf("bad literal %q", c.want)
		}
		if got := diagonalCell(c.n, 16); got.Cmp(want) != 0 {
			t.Errorf("diagonalCell(%d,16) = T(%d,%d) = %d, want %s", c.n, c.n, c.n-16, got, c.want)
		}
	}
}

// TestDiagonalP16StripContribution drives the production strip path
// (contributeDiagonalStrip -> diagonalCell) for the k=16 strip at a35's scale
// (maxn=35), asserting every cell of the H=maxn-16 strip lands in the triangle.
func TestDiagonalP16StripContribution(t *testing.T) {
	const maxn, k = 35, 16
	if !diagonalStripValid(maxn, k) {
		t.Fatalf("k=16 strip must dispatch at maxn=%d", maxn)
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
