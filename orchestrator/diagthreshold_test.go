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
// this change: it's the concrete claim that a26 (maxn=26) can use P9's
// diagonal shortcut at all. Under the old guard (maxn>=3k+1), k=9 at maxn=26
// was rejected (26 < 3*9+1=28) even though the true threshold (maxn>=2*9+1=19)
// is satisfied.
func TestDiagonalStripValidTrueThreshold(t *testing.T) {
	// k=8 at maxn=17 (=2*8+1): true threshold says valid; old 3k+1=25 guard
	// would have rejected it. diagonalStripValid must accept it.
	if !diagonalStripValid(17, 8) {
		t.Errorf("diagonalStripValid(17, 8) = false; want true (17 >= 2*8+1=17, the true threshold; the old maxn>=3*8+1=25 guard would wrongly reject this)")
	}
	if diagonalStripValid(16, 8) {
		t.Errorf("diagonalStripValid(16, 8) = true; want false (16 < 2*8+1=17)")
	}
	// k=9 (P_9, now wired): a26 (maxn=26) must be able to use it, even though
	// 26 < 3*9+1=28 (the old guard would have wrongly rejected this — this is
	// the concrete claim that made the whole guard-threshold fix worthwhile).
	if !diagonalStripValid(26, 9) {
		t.Errorf("diagonalStripValid(26, 9) = false; want true (26 >= 2*9+1=19; a26 must be able to use P_9's shortcut)")
	}
	if diagonalStripValid(18, 9) {
		t.Errorf("diagonalStripValid(18, 9) = true; want false (18 < 2*9+1=19)")
	}
	// k=11 (P_11, now wired): a28 (maxn=28) must be able to use it (28 >= 2*11+1=23,
	// keeping a28's top real height at H=maxn-11 rather than a new column tier).
	if !diagonalStripValid(28, 11) {
		t.Errorf("diagonalStripValid(28, 11) = false; want true (28 >= 2*11+1=23; a28 must be able to use P_11's shortcut)")
	}
	if diagonalStripValid(22, 11) {
		t.Errorf("diagonalStripValid(22, 11) = true; want false (22 < 2*11+1=23)")
	}
	// k=12 is out of range until P_12 is derived and wired — diagonalStripValid
	// must refuse it regardless of maxn, since diagonalCell has no case 12.
	if diagonalStripValid(100, 12) {
		t.Errorf("diagonalStripValid(100, 12) = true; want false (k=12/P_12 not wired into diagonalCell yet)")
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
