package orchestrator

// diag_p17_test.go — the H=maxn-17 strip is the k=17 diagonal, closed-form via
// P_17 (scripts/derive_pk_fast.py). Wiring it keeps a(37)'s top real height at
// H=maxn-18 = H19 (H=maxn-17 = H20 becomes closed-form). The validated
// P_9..P_16 fits pin the shared symbols, so only a17,b17 were fit — from
// T(35,18) and T(36,19), the two smallest in-onset points (onset n>=2k+1=35).
// Unlike k<=16 there is NO independent held-out diagonal-17 point yet: a(37)'s
// real H20 sweep (strict route) would produce the first one, T(37,20). Until
// then P_17's certification rests on the proven grand form (exp identity pins
// the whole polynomial given a17,b17; leading coeff 25^17/17! and k!-
// integrality both emerged, not assumed). The out-of-onset point T(34,17)
// (n=2k=34) does NOT lie on the polynomial — checked during derivation,
// consistent with the sharp onset observed at every lower k, so it is neither
// a fit point nor a holdout (this corrects HANDOFF's earlier parenthetical).
// Values exceed 2^64, so they are compared as big.Int.

import (
	"math/big"
	"testing"
)

func TestDiagonalP17Formula(t *testing.T) {
	cases := []struct {
		n    int
		want string
	}{
		{35, "180152359823857046862682314"},  // T(35,18), fit point (results/ns_a35)
		{36, "954543410624801880699125196"},  // T(36,19), fit point (results/ns_a36)
	}
	for _, c := range cases {
		want, ok := new(big.Int).SetString(c.want, 10)
		if !ok {
			t.Fatalf("bad literal %q", c.want)
		}
		if got := diagonalCell(c.n, 17); got.Cmp(want) != 0 {
			t.Errorf("diagonalCell(%d,17) = T(%d,%d) = %d, want %s", c.n, c.n, c.n-17, got, c.want)
		}
	}
}

// TestDiagonalP17StripContribution drives the production strip path
// (contributeDiagonalStrip -> diagonalCell) for the k=17 strip at a37's scale
// (maxn=37), asserting every cell of the H=maxn-17 strip lands in the triangle.
func TestDiagonalP17StripContribution(t *testing.T) {
	const maxn, k = 37, 17
	if !diagonalStripValid(maxn, k) {
		t.Fatalf("k=17 strip must dispatch at maxn=%d", maxn)
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
