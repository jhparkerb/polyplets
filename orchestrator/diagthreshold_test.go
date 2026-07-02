package orchestrator

// diagthreshold_test.go — proves the true n>=2k+1 diagonal validity threshold
// (docs/proofs/T-n-nm2-and-general.md) replaced the old, overly-conservative
// n>=3k+1 dispatch guard, and that applyPow3's negative-exponent division
// path fails loudly rather than silently rounding when asked to divide a
// non-divisible numerator.

import (
	"math/big"
	"testing"
)

// TestDiagonalStripValidTrueThreshold is the single most load-bearing test in
// this change: it's the concrete claim that a future term can use a wired
// diagonal shortcut well below the old n>=3k+1 guard, as long as the true
// n>=2k+1 threshold is satisfied.
func TestDiagonalStripValidTrueThreshold(t *testing.T) {
	// k=8 at maxn=17 (=2*8+1): true threshold says valid; old 3k+1=25 guard
	// would have rejected it. diagonalStripValid must accept it.
	if !diagonalStripValid(17, 8) {
		t.Errorf("diagonalStripValid(17, 8) = false; want true (17 >= 2*8+1=17, the true threshold; the old maxn>=3*8+1=25 guard would wrongly reject this)")
	}
	if diagonalStripValid(16, 8) {
		t.Errorf("diagonalStripValid(16, 8) = true; want false (16 < 2*8+1=17)")
	}
	// k=9 is out of range until P_9 is wired into diagCoeffTable —
	// diagonalStripValid must refuse it regardless of maxn.
	if diagonalStripValid(26, 9) {
		t.Errorf("diagonalStripValid(26, 9) = true; want false (k=9/P_9 not wired into diagonalCell yet)")
	}
}

// TestApplyPow3ExactnessAssertion proves applyPow3 panics on a non-divisible
// numerator in its negative-exponent branch, rather than silently rounding —
// the fail-closed proof that a future coefficient-derivation bug (or a case
// invoked outside its proven-valid regime) surfaces immediately instead of
// producing a quietly wrong triangle cell.
func TestApplyPow3ExactnessAssertion(t *testing.T) {
	defer func() {
		if recover() == nil {
			t.Fatalf("applyPow3(non-divisible, negative exponent) did not panic")
		}
	}()
	// 10 is not divisible by 3^1=3.
	applyPow3(big.NewInt(10), -1)
}

// TestApplyPow3PositiveExponentUnchanged is a refactor-safety net: the
// pow3->applyPow3 swap in hornerDiag must not change behavior for the
// existing non-negative-exponent cases (j=0..6, and j=7/8 at their original
// n>=3k+1 fitting points).
func TestApplyPow3PositiveExponentUnchanged(t *testing.T) {
	got := applyPow3(big.NewInt(5), 3) // 5 * 3^3 = 135
	if want := big.NewInt(135); got.Cmp(want) != 0 {
		t.Errorf("applyPow3(5, 3) = %s, want %s", got, want)
	}
}
