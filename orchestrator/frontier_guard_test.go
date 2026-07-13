package orchestrator

// frontier_guard_test.go — regression pin for the throttled-checkpoint /
// unconditional-frontier-GC stranding bug (AUDIT-2026-07-13, corroborated by two
// independent audit passes). Before the fix, sweepHeight/sweepHeightKink deleted
// each column's consumed frontier unconditionally, even when that column's
// checkpoint was throttled away — so the last persisted checkpoint pointed at
// files a later column had already deleted, and a crash-resume failed loudly
// ("cannot read input"), forcing the whole height to re-run from col 0.
//
// RED before the fix: with unconditional deletion, delOnThrottle below would
// return the protected frontier, i.e. the last checkpoint's files get deleted.

import (
	"reflect"
	"testing"
)

// flatten concatenates the returned delete-sets into a single ordered list.
func flatten(sets [][]string) []string {
	var out []string
	for _, s := range sets {
		out = append(out, s...)
	}
	return out
}

func TestFrontierGuardRetainsCheckpointedFrontier(t *testing.T) {
	// Entry frontier is what a resume checkpoint would name.
	seed := []string{"seed.run"}
	g := &frontierGuard{protected: seed}

	f1 := []string{"c1.run"}
	f2 := []string{"c2.run"}
	f3 := []string{"c3.run"}
	f4 := []string{"c4.run"}

	// Col 1 writes a checkpoint naming f1: the seed it consumed is now safe.
	del := g.afterColumn(true, seed, f1)
	if got := flatten(del); !reflect.DeepEqual(got, seed) {
		t.Fatalf("col1: want delete %v, got %v", seed, got)
	}
	if !sameRunSet(g.protected, f1) {
		t.Fatalf("col1: protected want %v, got %v", f1, g.protected)
	}

	// Col 2 is THROTTLED (no checkpoint). The on-disk checkpoint still names f1,
	// so f1 must survive; the consumed intermediate is f1 -> it is the protected
	// set, so nothing is deleted this column.
	del = g.afterColumn(false, f1, f2)
	if got := flatten(del); len(got) != 0 {
		t.Fatalf("col2 throttled: must not delete the checkpointed frontier %v, but deleted %v", f1, got)
	}
	if !sameRunSet(g.protected, f1) {
		t.Fatalf("col2: protected must stay %v, got %v", f1, g.protected)
	}

	// Col 3 is THROTTLED. It consumed f2 (an unreferenced intermediate) — f2 is
	// safe to delete, but f1 (still checkpointed) must NOT be.
	del = g.afterColumn(false, f2, f3)
	if got := flatten(del); !reflect.DeepEqual(got, f2) {
		t.Fatalf("col3 throttled: want delete only intermediate %v, got %v", f2, got)
	}
	if !sameRunSet(g.protected, f1) {
		t.Fatalf("col3: protected must stay %v, got %v", f1, g.protected)
	}

	// Col 4 writes a checkpoint naming f4: now the old protected f1 AND the
	// just-consumed f3 are both unreferenced and deletable.
	del = g.afterColumn(true, f3, f4)
	got := flatten(del)
	want := append(append([]string{}, f1...), f3...)
	if !reflect.DeepEqual(got, want) {
		t.Fatalf("col4 checkpoint: want delete %v (old protected + consumed), got %v", want, got)
	}
	if !sameRunSet(g.protected, f4) {
		t.Fatalf("col4: protected want %v, got %v", f4, g.protected)
	}
}

// TestFrontierGuardHeightDoneFlushesProtected covers the height-exhausted branch:
// a nil (height-done) checkpoint supersedes everything, so any retained protected
// frontier plus the final consumed frontier are all released.
func TestFrontierGuardHeightDoneFlushesProtected(t *testing.T) {
	f1 := []string{"c1.run"}
	f2 := []string{"c2.run"}
	g := &frontierGuard{protected: f1} // f1 retained from an earlier throttled gap

	// Height done at a column that consumed f2, writing the nil checkpoint.
	del := g.afterColumn(true, f2, nil)
	got := flatten(del)
	want := append(append([]string{}, f1...), f2...)
	if !reflect.DeepEqual(got, want) {
		t.Fatalf("height-done: want release %v, got %v", want, got)
	}
}
