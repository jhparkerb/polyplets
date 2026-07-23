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
	// k=11 (P_11, wired): a28 (maxn=28) must be able to use it (28 >= 2*11+1=23,
	// keeping a28's top real height at H=maxn-11 rather than a new column tier).
	if !diagonalStripValid(28, 11) {
		t.Errorf("diagonalStripValid(28, 11) = false; want true (28 >= 2*11+1=23; a28 must be able to use P_11's shortcut)")
	}
	if diagonalStripValid(22, 11) {
		t.Errorf("diagonalStripValid(22, 11) = true; want false (22 < 2*11+1=23)")
	}
	// k=12 (P_12, now wired): a29 (maxn=29) must be able to use it (29 >= 2*12+1=25),
	// keeping a29's top real height at H=maxn-12, same tier as a28.
	if !diagonalStripValid(29, 12) {
		t.Errorf("diagonalStripValid(29, 12) = false; want true (29 >= 2*12+1=25; a29 must be able to use P_12's shortcut)")
	}
	if diagonalStripValid(24, 12) {
		t.Errorf("diagonalStripValid(24, 12) = true; want false (24 < 2*12+1=25)")
	}
	// k=13 (P_13, now wired): a32 (maxn=32) must be able to use it (32 >= 2*13+1=27),
	// dropping a32's top real height a tier (H=maxn-13=H19 becomes closed-form).
	if !diagonalStripValid(32, 13) {
		t.Errorf("diagonalStripValid(32, 13) = false; want true (32 >= 2*13+1=27; a32 must be able to use P_13's shortcut)")
	}
	if diagonalStripValid(26, 13) {
		t.Errorf("diagonalStripValid(26, 13) = true; want false (26 < 2*13+1=27)")
	}
	// k=14 (P_14, now wired): a33 (maxn=33) must be able to use it (33 >= 2*14+1=29),
	// keeping a33's top real height at H=maxn-15=H18 (H=maxn-14=H19 becomes closed-form).
	if !diagonalStripValid(33, 14) {
		t.Errorf("diagonalStripValid(33, 14) = false; want true (33 >= 2*14+1=29; a33 must be able to use P_14's shortcut)")
	}
	if diagonalStripValid(28, 14) {
		t.Errorf("diagonalStripValid(28, 14) = true; want false (28 < 2*14+1=29)")
	}
	// k=15 (P_15, now wired): a34 (maxn=34) must be able to use it (34 >= 2*15+1=31),
	// keeping a34's top real height at H=maxn-16=H18 (H=maxn-15=H19 becomes closed-form).
	if !diagonalStripValid(34, 15) {
		t.Errorf("diagonalStripValid(34, 15) = false; want true (34 >= 2*15+1=31; a34 must be able to use P_15's shortcut)")
	}
	if diagonalStripValid(30, 15) {
		t.Errorf("diagonalStripValid(30, 15) = true; want false (30 < 2*15+1=31)")
	}
	// k=16 (P_16, now wired): a35 (maxn=35) must be able to use it (35 >= 2*16+1=33),
	// keeping a36's top real height at H=maxn-17=H19 (H=maxn-16=H20 becomes closed-form).
	if !diagonalStripValid(35, 16) {
		t.Errorf("diagonalStripValid(35, 16) = false; want true (35 >= 2*16+1=33; must be able to use P_16's shortcut)")
	}
	if diagonalStripValid(32, 16) {
		t.Errorf("diagonalStripValid(32, 16) = true; want false (32 < 2*16+1=33)")
	}
	// k=17 (P_17, now wired): a37 (maxn=37) must be able to use it (37 >= 2*17+1=35),
	// keeping a37's top real height at H=maxn-18=H19 (H=maxn-17=H20 becomes closed-form).
	if !diagonalStripValid(37, 17) {
		t.Errorf("diagonalStripValid(37, 17) = false; want true (37 >= 2*17+1=35; a37 must be able to use P_17's shortcut)")
	}
	if diagonalStripValid(34, 17) {
		t.Errorf("diagonalStripValid(34, 17) = true; want false (34 < 2*17+1=35)")
	}
	// k=18 is out of range until P_18 is derived and wired — diagonalStripValid
	// must refuse it regardless of maxn, since diagonalCell has no case 18.
	if diagonalStripValid(100, 18) {
		t.Errorf("diagonalStripValid(100, 18) = true; want false (k=18/P_18 not wired into diagonalCell yet)")
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

// TestHornerDiagKFactExactnessAssertion proves hornerDiag panics when the Horner
// numerator is not exactly divisible by k!, rather than silently truncating it
// with Quo — closing the fail-closed-armor gap the AUDIT-2026-07-13 pass found
// (applyPow3 guards only the 3-power divide; on positive-exponent record cells it
// merely multiplies, so this k!-divide is the only check on the divide path). A
// coefficient-transcription error that breaks k!-divisibility must surface, not
// bank a wrong cell.
func TestHornerDiagKFactExactnessAssertion(t *testing.T) {
	defer func() {
		if recover() == nil {
			t.Fatalf("hornerDiag(numerator not divisible by k!) did not panic")
		}
	}()
	// Single coefficient => numerator == 1 at any N; k!=2 does not divide 1.
	hornerDiag(7, diagCoeffs{coeffs: []string{"1"}, kfact: 2}, 0)
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
