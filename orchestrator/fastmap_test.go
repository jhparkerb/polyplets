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
