package orchestrator

import (
	"math/big"
	"testing"
)

// P_19 (diagonal k=19): fit from the two smallest in-onset points (onset
// n >= 2k+1 = 39), BOTH real swept values — T(39,20) from the a(39) run
// (results/ns_a39) and T(40,21) from the a(40) run (results/ns_a40, the
// project's tallest real sweep). UNLIKE k<=18 there is no independent
// held-out diagonal-19 point and never will be: the first, T(41,22), needs
// a real H22 sweep (a(42)-scale) and the project closes at a(40). P_19 is
// permanently fitted-no-holdout; certification rests on the proven grand
// form (the exp identity pins the whole polynomial once a19,b19 are set)
// plus the leading-coeff 25^19/19! and k!-integrality checks.
func TestDiagonalP19Formula(t *testing.T) {
	cases := []struct {
		n    int
		want string
	}{
		{39, "305997488346556404027895440838"},  // T(39,20), fit point (results/ns_a39)
		{40, "1613457978443478071138613405555"}, // T(40,21), fit point (results/ns_a40)
	}
	for _, c := range cases {
		want, ok := new(big.Int).SetString(c.want, 10)
		if !ok {
			t.Fatalf("bad literal %q", c.want)
		}
		if got := diagonalCell(c.n, 19); got.Cmp(want) != 0 {
			t.Errorf("diagonalCell(%d,19) = T(%d,%d) = %d, want %s", c.n, c.n, c.n-19, got, c.want)
		}
	}
}

// TestDiagonalP19StripContribution drives the production strip path for the
// k=19 strip at a(40)'s scale (maxn=40), asserting every cell of the
// H=maxn-19 strip lands in the triangle.
func TestDiagonalP19StripContribution(t *testing.T) {
	const maxn, k = 40, 19
	if !diagonalStripValid(maxn, k) {
		t.Fatalf("k=19 strip must dispatch at maxn=%d", maxn)
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
