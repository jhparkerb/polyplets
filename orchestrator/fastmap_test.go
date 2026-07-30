package orchestrator

import (
	"errors"
	"testing"
)

// Concurrent rounds must not collectively overfill the fast dir: each round
// RESERVES its projection before routing to tmpfs and releases on completion,
// against a hard RAM floor. The a(40) launch died exactly here: N overlapping
// heights' rounds each passed a point-in-time statfs check, tmpfs pages ate
// RAM, and the OOM killer took the tmux server (second occurrence of the
// a(35) failure class).
func TestFastMapReservationRace(t *testing.T) {
	rm := newFastMapReserver(func() (uint64, error) { return 60 << 30, nil }, 16<<30)
	const need = 20 << 30
	got := 0
	for i := 0; i < 5; i++ {
		if rm.reserve(need) {
			got++
		}
	}
	// avail 60GB, floor 16GB -> only TWO 20GB rounds fit (60-16=44 budget).
	if got != 2 {
		t.Fatalf("reserved %d rounds of 20GB against 60GB avail/16GB floor; want 2", got)
	}
	rm.release(need)
	if !rm.reserve(need) {
		t.Fatalf("release must return capacity to the pool")
	}
	// statfs error -> never reserve.
	bad := newFastMapReserver(func() (uint64, error) { return 0, errors.New("boom") }, 16<<30)
	if bad.reserve(1) {
		t.Fatalf("reserve must fail closed on statfs error")
	}
}

// TestFastMapFloorEnvFailsLoudly — red-first regression for AUDIT-2026-07-30
// O5 ("Floor Guards the Wrong Resource", env-parse half). An unparseable
// POLY_FASTMAP_FLOOR_GB silently fell back to the 24GB default: an operator
// who wrote "40GB" or "40g" got a floor 16GB lower than the one they thought
// they had set, on the exact knob whose misconfiguration is implicated in the
// four-OOM history. The floor must be refused at start, not guessed.
//
// RED before the fix:
//
//	--- FAIL: TestFastMapFloorEnvFailsLoudly (0.00s)
//	    fastmap_test.go:55: POLY_FASTMAP_FLOOR_GB="40GB" accepted silently:
//	        floor fell back to 24GB, not what the operator asked for
//	    [... and for "40g", "", " ", "-8", "0", "24.5" ...]
func TestFastMapFloorEnvFailsLoudly(t *testing.T) {
	for _, bad := range []string{"40GB", "40g", "", " ", "-8", "0", "24.5"} {
		t.Setenv("POLY_FASTMAP_FLOOR_GB", bad)
		r, err := newFastMapReserverFor(t.TempDir())
		if err == nil {
			t.Errorf("POLY_FASTMAP_FLOOR_GB=%q accepted silently: floor fell back to %dGB, not what the operator asked for", bad, r.floor>>30)
		}
	}
	t.Setenv("POLY_FASTMAP_FLOOR_GB", "40")
	r, err := newFastMapReserverFor(t.TempDir())
	if err != nil {
		t.Fatalf("POLY_FASTMAP_FLOOR_GB=40: %v", err)
	}
	if got := r.floor >> 30; got != 40 {
		t.Errorf("floor = %dGB, want 40GB", got)
	}
}
