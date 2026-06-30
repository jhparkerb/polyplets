package orchestrator

import (
	"sync/atomic"
	"testing"
	"time"
)

// unit builds a runningUnit with the given remaining/processed input records.
func unit(remaining, processed uint64) *runningUnit {
	p := new(atomic.Uint64)
	p.Store(processed)
	return &runningUnit{u: mapUnit{estTotal: remaining + processed}, processed: p}
}

// TestStealEligibleSkipsUnsplittable — RED before the Stop-Then-Shrug fix.
// A remnant larger than a grain but smaller than 2 index strides cannot be cut
// by the .idx (one key per indexStride records), so stealing it stops the victim
// and pays the respawn overhead for zero fan-out. It must NOT be eligible.
// Pre-fix, stealEligible only checks the grain floor, so it stole such remnants.
func TestStealEligibleSkipsUnsplittable(t *testing.T) {
	grain := uint64(10)

	// remaining=50: above the grain (10) but below 2*indexStride (128) → too
	// small to split → must be ineligible (the Stop-Then-Shrug case).
	if stealEligible(unit(50, 100), grain) {
		t.Fatalf("stole an unsplittable remnant (50 records < 2*indexStride=%d) — Stop-Then-Shrug", 2*indexStride)
	}
	// remaining=1000: above grain AND ≥2 strides → splittable → eligible.
	if !stealEligible(unit(1000, 100), grain) {
		t.Fatalf("a large splittable remnant should be steal-eligible")
	}
	// at the grain floor → ineligible.
	if stealEligible(unit(10, 100), grain) {
		t.Fatalf("remnant at the grain floor must be ineligible")
	}
	// no progress yet (processed=0) → ineligible (can't size it).
	if stealEligible(unit(1000, 0), grain) {
		t.Fatalf("a unit with no progress must be ineligible")
	}
}

// TestStealAllowedGatesOnActiveHeights — the overlap+steal coexistence gate.
// Pre-fix, stealing was disabled outright whenever OverlapHeights>1 (a static
// config check), so the dominant height's own lone endgame — after every
// sibling height finishes, exactly when stealing is both safe AND most needed —
// never got it. stealAllowed must read activeHeights LIVE: blocked while >1
// height shares the pool (a local "idle" goroutine may really be blocked on sem
// behind a sibling), allowed once this height is the sole occupant (then local
// idle == box idle, the same condition sequential mode always has).
func TestStealAllowedGatesOnActiveHeights(t *testing.T) {
	var n atomic.Int32

	n.Store(0)
	if !stealAllowed(&n) {
		t.Fatalf("0 active heights (not yet counted, or sequential's implicit case) must allow stealing")
	}
	n.Store(1)
	if !stealAllowed(&n) {
		t.Fatalf("1 active height (sole occupant — sequential mode, or overlap's endgame) must allow stealing")
	}
	n.Store(2)
	if stealAllowed(&n) {
		t.Fatalf("2 active heights must BLOCK stealing — a local idle signal isn't box-wide idle when a sibling height shares the pool")
	}
	n.Store(5)
	if stealAllowed(&n) {
		t.Fatalf("5 active heights must block stealing")
	}

	// Dynamic: the same counter must flip the decision as siblings finish —
	// this is what lets a long column re-evaluate mid-flight instead of being
	// stuck with a stale snapshot from column start.
	n.Store(3)
	if stealAllowed(&n) {
		t.Fatalf("3 active: must block")
	}
	n.Store(1)
	if !stealAllowed(&n) {
		t.Fatalf("dropped to 1 active (siblings finished): must now allow")
	}

	// nil = no dynamic tracking configured: unconditionally allowed (subject to
	// the other gates in mapPhase), matching callers that never run heights
	// concurrently.
	if !stealAllowed(nil) {
		t.Fatalf("nil activeHeights must allow stealing unconditionally")
	}
}

// TestStealScorePrefersComputeHeavy — RED before the tail-miss fix.
// Victim selection must size by WALL TIME remaining, not records: a compute-heavy
// straggler (few records left, slow rate) must outscore a record-heavy fast unit.
// Pre-fix, stealScore ranked by remaining records, so the fast unit won.
func TestStealScorePrefersComputeHeavy(t *testing.T) {
	now := time.Now()
	// record-heavy but FAST: 200 records left, 800 processed in 8s → ~100/s → ~2s left.
	fast := unit(200, 800)
	fast.started = now.Add(-8 * time.Second)
	// compute-heavy STRAGGLER: 100 records left, 100 processed in 100s → ~1/s → ~100s left.
	slow := unit(100, 100)
	slow.started = now.Add(-100 * time.Second)
	if stealScore(slow, now) <= stealScore(fast, now) {
		t.Fatalf("compute-heavy straggler (more wall time left) must outscore the record-heavy one: slow=%.1f fast=%.1f",
			stealScore(slow, now), stealScore(fast, now))
	}
}
