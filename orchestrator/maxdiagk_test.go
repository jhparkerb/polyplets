package orchestrator

// maxdiagk_test.go — the strict-route enabler. With P_17 wired, a(37)'s
// H20 would closed-form-short-circuit, so the strict certification sweep
// (real H20 = the first independent P_17 holdout) needs a runtime cap on
// which wired diagonals may dispatch: --max-diag-k. This test proves the
// cap (a) actually forces the capped diagonal height back to a real column
// sweep, and (b) the real sweep reproduces the closed form's cells exactly
// — which is precisely the strict route's validation semantics in miniature.

import (
	"context"
	"testing"
)

func TestMaxDiagKForcesRealSweep(t *testing.T) {
	known := loadKnownTriangle(t)
	dir := t.TempDir()
	cfg := baseCfg(t, dir) // maxn = resumeMaxn (8): k=3 diagonal is H=5
	cfg.MaxDiagK = 2       // cap: k=3 (H=5) must now column-sweep for real
	hit := 0
	cfg.afterColumn = func(H, col int) {
		if H == cfg.Maxn-3 {
			hit++
		}
	}
	res, err := Run(context.Background(), cfg, nil)
	if err != nil {
		t.Fatalf("full sweep maxn=%d max-diag-k=%d: %v", cfg.Maxn, cfg.MaxDiagK, err)
	}
	if hit == 0 {
		t.Fatalf("no column work at H=maxn-3=%d: the k=3 diagonal still closed-form despite MaxDiagK=2", cfg.Maxn-3)
	}
	// The real sweep must reproduce the known triangle (including the cells
	// the P_3 closed form would have generated) byte-for-byte.
	checkTriangle(t, "max-diag-k-capped", known, res.Triangle)
}

// TestMaxDiagKZeroDisablesInjection — red-first regression for
// AUDIT-2026-07-30 D7 ("Cap Zero Inverts"). The dispatch predicate read
// `MaxDiagK == 0 || k <= MaxDiagK`, so an operator asking for NO injection
// with `--max-diag-k 0` got the MAXIMUM instead: every wired diagonal fired.
// The accidental disable value was 1 (which still injects k=1, itself a
// proven closed form, so nothing visibly broke). 0 now means what it says;
// "no cap" is the omitted/negative sentinel.
//
// RED before the fix:
//
//	--- FAIL: TestMaxDiagKZeroDisablesInjection (0.10s)
//	    maxdiagk_test.go:69: --max-diag-k 0 asked for NO diagonal injection but
//	        H=6 (k=2) and H=5 (k=3) were still closed-formed: 0 columns swept
//	        across both
func TestMaxDiagKZeroDisablesInjection(t *testing.T) {
	known := loadKnownTriangle(t)
	dir := t.TempDir()
	cfg := baseCfg(t, dir)
	cfg.MaxDiagK = 0 // "no diagonal injection at all"
	swept := 0
	cfg.afterColumn = func(H, col int) {
		if H == cfg.Maxn-2 || H == cfg.Maxn-3 {
			swept++
		}
	}
	res, err := Run(context.Background(), cfg, nil)
	if err != nil {
		t.Fatalf("full sweep maxn=%d max-diag-k=0: %v", cfg.Maxn, err)
	}
	if swept == 0 {
		t.Fatalf("--max-diag-k 0 asked for NO diagonal injection but H=%d (k=2) and H=%d (k=3) were still closed-formed: 0 columns swept across both", cfg.Maxn-2, cfg.Maxn-3)
	}
	checkTriangle(t, "max-diag-k-zero", known, res.Triangle)
}

// TestPhasedRecipeDiagCap pins the height/cap algebra of the recorded a(N>=40)
// reproduction recipe (scripts/term.sh, AUDIT-2026-07-30 D1 "Phase C
// Phantom"). The diagonal index is k = N-H and the phase split uses fixed
// offsets from N, so the same k ranges hold for every N >= 40:
//
//	phase A  H = 1..N-21  (k >= 21, past the fence) and H = N-18..N (k <= 18,
//	         the injected closed-form tail)
//	phase B  H = N-20     (k = 20, past the fence)
//	phase C  H = N-19     (k = 19 — P_19 is wired, so WITHOUT the cap this
//	         strip is injected from the formula it was fitted to, and the
//	         a(40) mass holdout is destroyed by its own reproduction recipe)
//
// The script pins --max-diag-k 18 on all three phases. This test is the
// executable form of that argument: the shell driver has no test harness.
func TestPhasedRecipeDiagCap(t *testing.T) {
	const phaseDiagCap = 18 // must match PHASE_DIAG_CAP in scripts/term.sh
	for _, N := range []int{40, 41, 44} {
		cfg := SweepConfig{Maxn: N, MaxDiagK: phaseDiagCap}
		// The cap is load-bearing, not decorative: uncapped, phase C's
		// strip IS injected. This is the defect D1 found.
		if !diagonalStripEnabled(SweepConfig{Maxn: N, MaxDiagK: maxDiagKNoCap}, 19) {
			t.Fatalf("N=%d: k=19 does not dispatch uncapped — the cap would be a no-op and this test is vacuous", N)
		}
		if k := N - (N - 19); diagonalStripEnabled(cfg, k) {
			t.Errorf("N=%d phase C: H=%d (k=%d) still injects under --max-diag-k %d; the recipe would not really sweep it", N, N-19, k, phaseDiagCap)
		}
		if k := N - (N - 20); diagonalStripEnabled(cfg, k) {
			t.Errorf("N=%d phase B: H=%d (k=%d) injects; it must be really swept", N, N-20, k)
		}
		// Phase A's tail must still be injected — that is the whole point of
		// the phase split, and a cap that blocked it would turn a cheap
		// closed-form tail into 19 real sweeps.
		for H := N - 18; H <= N-2; H++ {
			if k := N - H; !diagonalStripEnabled(cfg, k) {
				t.Errorf("N=%d phase A: H=%d (k=%d) must stay closed-form under --max-diag-k %d", N, H, k, phaseDiagCap)
			}
		}
	}
}

// TestValidateMaxDiagKRange pins the CLI range check: the flag used to accept
// -1, 99 or any other value silently, each with its own surprising dispatch.
func TestValidateMaxDiagKRange(t *testing.T) {
	for _, v := range []int{-1, 0, 1, 19} {
		if err := ValidateMaxDiagK(v); err != nil {
			t.Errorf("ValidateMaxDiagK(%d) = %v, want accepted", v, err)
		}
	}
	for _, v := range []int{-2, 20, 99} {
		if err := ValidateMaxDiagK(v); err == nil {
			t.Errorf("ValidateMaxDiagK(%d) = nil, want a range error", v)
		}
	}
}
