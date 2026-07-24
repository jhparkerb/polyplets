package orchestrator

import (
	"math/big"
	"testing"
)

// P_18 (diagonal k=18): fit from the two smallest in-onset points (onset
// n >= 2k+1 = 37), BOTH real swept values — T(37,19) from the a(37) run
// (results/ns_a37) and T(38,20) from the a(38) run (results/ns_a38).
// Like P_17 at wiring time there is no independent held-out diagonal-18
// point yet: the first, T(39,21), comes only from a real H21 sweep (a(40)).
// Certification meanwhile rests on the proven grand form. Wiring makes
// H = maxn-18 closed-form, keeping a(39)'s top real height at H20.
func TestDiagonalP18Formula(t *testing.T) {
	cases := []struct {
		n    int
		want string
	}{
		{37, "7418664369542642927200487045"},   // T(37,19), fit point (results/ns_a37)
		{38, "39207474138446972682720171554"},  // T(38,20), fit point (results/ns_a38)
	}
	for _, c := range cases {
		want, ok := new(big.Int).SetString(c.want, 10)
		if !ok {
			t.Fatalf("bad literal %q", c.want)
		}
		if got := diagonalCell(c.n, 18); got.Cmp(want) != 0 {
			t.Errorf("diagonalCell(%d,18) = T(%d,%d) = %d, want %s", c.n, c.n, c.n-18, got, c.want)
		}
	}
}

// TestDiagonalP18StripContribution drives the production strip path for the
// k=18 strip at a(39)'s scale (maxn=39), asserting every cell of the
// H=maxn-18 strip lands in the triangle.
func TestDiagonalP18StripContribution(t *testing.T) {
	const maxn, k = 39, 18
	if !diagonalStripValid(maxn, k) {
		t.Fatalf("k=18 strip must dispatch at maxn=%d", maxn)
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
