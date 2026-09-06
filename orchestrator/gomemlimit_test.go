package orchestrator

// gomemlimit_test.go — red-first regression for AUDIT-2026-07-30 O6
// ("Unbounded Orchestrator Heap"). cmd/orchestrate set GOGC=1000 with no
// memory limit, so the heap could grow to ~11x live before a collection —
// the mechanism behind head #4's 4.4 GB-and-climbing RSS in
// docs/engine-record.md (the audit found no leak).
//
// debug.SetMemoryLimit(-1) reads the current limit without changing it, so
// the applied bound is directly observable.
//
// RED before the fix (ApplyGoMemoryLimit present but not yet setting a limit,
// i.e. exactly what main.go did):
//
//	--- FAIL: TestApplyGoMemoryLimitDefault (0.00s)
//	    gomemlimit_test.go:41: memory limit is 9223372036854775807 (unbounded is
//	        9223372036854775807, Go's default); want the 4GiB bound 4294967296
//	--- FAIL: TestApplyGoMemoryLimitEnvOverride (0.00s)
//	    gomemlimit_test.go:52: POLY_GO_MEMLIMIT_GB=2: limit is
//	        9223372036854775807, want 2147483648

import (
	"math"
	"runtime/debug"
	"testing"
)

// restoreMemLimit puts the process limit back after a test touches it.
func restoreMemLimit(t *testing.T) {
	t.Helper()
	prev := debug.SetMemoryLimit(-1)
	t.Cleanup(func() { debug.SetMemoryLimit(prev) })
}

func TestApplyGoMemoryLimitDefault(t *testing.T) {
	restoreMemLimit(t)
	if _, err := ApplyGoMemoryLimit(); err != nil {
		t.Fatalf("ApplyGoMemoryLimit: %v", err)
	}
	if got, want := debug.SetMemoryLimit(-1), int64(goMemLimitDefaultGB)<<30; got != want {
		t.Fatalf("memory limit is %d (unbounded is %d, Go's default); want the %dGiB bound %d", got, int64(math.MaxInt64), goMemLimitDefaultGB, want)
	}
}

func TestApplyGoMemoryLimitEnvOverride(t *testing.T) {
	restoreMemLimit(t)
	t.Setenv("POLY_GO_MEMLIMIT_GB", "2")
	if _, err := ApplyGoMemoryLimit(); err != nil {
		t.Fatalf("ApplyGoMemoryLimit: %v", err)
	}
	if got, want := debug.SetMemoryLimit(-1), int64(2)<<30; got != want {
		t.Fatalf("POLY_GO_MEMLIMIT_GB=2: limit is %d, want %d", got, want)
	}

	// 0 = explicitly unbounded (Go's own default).
	t.Setenv("POLY_GO_MEMLIMIT_GB", "0")
	if _, err := ApplyGoMemoryLimit(); err != nil {
		t.Fatalf("ApplyGoMemoryLimit(0): %v", err)
	}
	if got := debug.SetMemoryLimit(-1); got != math.MaxInt64 {
		t.Fatalf("POLY_GO_MEMLIMIT_GB=0: limit is %d, want unbounded %d", got, int64(math.MaxInt64))
	}

	// A set-but-unusable value is refused, not guessed.
	for _, bad := range []string{"4GB", "", "-1", "2.5"} {
		t.Setenv("POLY_GO_MEMLIMIT_GB", bad)
		if _, err := ApplyGoMemoryLimit(); err == nil {
			t.Errorf("POLY_GO_MEMLIMIT_GB=%q accepted silently", bad)
		}
	}
}
