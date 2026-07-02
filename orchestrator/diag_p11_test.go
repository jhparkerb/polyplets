package orchestrator

// diag_p11_test.go — the H=maxn-11 strip is the k=11 diagonal, closed-form via
// P_11 (scripts/derive_p11.py). P_11 is the last diagonal needed to keep
// a(28)'s top real height at H=maxn-11 instead of a new column tier. 10 of its
// 12 coefficients come clean from the banked (validated) P_9/P_10 fits; a11,b11
// were fit from the two fresh sweeps T(26,15) and T(27,16). This test pins
// diagonalCell(n,11) against all five real diagonal-11 points — the three a25
// points (n=23,24,25) were HELD OUT of the derivation, so a wrong formula is
// caught regardless of the fit. Values exceed uint64 (T(27,16) > 2^64), so
// they are compared as big.Int decimal strings.

import (
	"math/big"
	"testing"
)

func TestDiagonalP11Formula(t *testing.T) {
	cases := []struct {
		n    int
		want string
	}{
		// held-out real points (results/ns_a25/swept_rows.txt), fed neither the
		// a11,b11 fit nor the shared-symbol solve.
		{23, "38826609174639928"},    // T(23,12)
		{24, "210692983396251014"},   // T(24,13)
		{25, "1104184694723970106"},  // T(25,14)
		// the two fitting points, from the fresh a26 / a27 sweeps.
		{26, "5614506356004078534"},  // T(26,15), results/ns_a26
		{27, "27798973373501478242"}, // T(27,16), results/ns_a27 (> 2^64)
	}
	for _, c := range cases {
		want, ok := new(big.Int).SetString(c.want, 10)
		if !ok {
			t.Fatalf("bad literal %q", c.want)
		}
		if got := diagonalCell(c.n, 11); got.Cmp(want) != 0 {
			t.Errorf("diagonalCell(%d,11) = T(%d,%d) = %d, want %s", c.n, c.n, c.n-11, got, c.want)
		}
	}
}

// TestDiagonalP11StripContribution drives the production strip path
// (contributeDiagonalStrip -> diagonalCell -> hornerDiag -> applyPow3) for the
// k=11 strip at a28's scale (maxn=28), asserting every cell of the H=maxn-11
// strip lands in the triangle exactly. This exercises the integration a full
// a20 --compare cannot: at maxn=20 the k=11 strip is below its 2k+1=23
// threshold and never dispatches, so only a maxn>=23 run reaches this code.
func TestDiagonalP11StripContribution(t *testing.T) {
	const maxn, k = 28, 11
	if !diagonalStripValid(maxn, k) {
		t.Fatalf("k=11 strip must dispatch at maxn=%d", maxn)
	}
	triangle := newBigRow(maxn + 1)
	contributeDiagonalStrip(maxn, k, triangle, SweepConfig{})
	// The strip H=maxn-k carries cells T(n, maxn-k) for n=maxn-k..maxn, each the
	// j=n-(maxn-k) diagonal at n.
	for j := 0; j <= k; j++ {
		n := maxn - k + j
		want := diagonalCell(n, j)
		if triangle[n].Cmp(want) != 0 {
			t.Errorf("strip cell T(%d,%d) = %d, want %d", n, maxn-k, triangle[n], want)
		}
	}
}

// TestDiagonalP11StripValid pins the dispatch guard: the k=11 strip is now
// eligible for closed-form fill at its validity threshold maxn>=2*11+1=23 and
// not below.
func TestDiagonalP11StripValid(t *testing.T) {
	if diagonalStripValid(22, 11) {
		t.Errorf("k=11 strip must be invalid at maxn=22 (< 2*11+1)")
	}
	if !diagonalStripValid(23, 11) {
		t.Errorf("k=11 strip must be valid at maxn=23 (= 2*11+1)")
	}
	if !diagonalStripValid(28, 11) {
		t.Errorf("k=11 strip must be valid at maxn=28")
	}
}
