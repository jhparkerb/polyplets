// Fan-In Tax (results/fanin-tax.md): every map unit opened EVERY input range
// file of the prior round (~80 files x ~640 units x ~0.45ms of header+idx+
// buffer setup per open = ~50k opens/round), measured as ~75% of all worker
// CPU on the dalby H15/maxn30 bench -- drowning the real transition work.
// Inputs are disjoint [keylo,keyhi) range files the orchestrator itself
// partitioned, so a unit covering [lo,hi) can only draw records from files
// whose stamped range overlaps it. These tests pin the pruning predicate
// (half-open semantics, open ends, unstamped-file fallback) and the merge-
// range record cap that stops a tiny round from being cut into cores*mult
// ranges regardless of payload.
package orchestrator

import (
	"fmt"
	"testing"
)

// bnd builds a keyBounds from hex strings ("" = open end) at keyLen 2.
func bnd(t *testing.T, lo, hi string) keyBounds {
	t.Helper()
	var b keyBounds
	b.lo, b.hasLo = hexBytes(lo, 2)
	b.hi, b.hasHi = hexBytes(hi, 2)
	return b
}

func TestPruneByBounds(t *testing.T) {
	paths := []string{"r0", "r1", "r2", "r3"}
	bounds := []keyBounds{
		bnd(t, "", "0a0a"),         // r0: (-inf, 0a0a)
		bnd(t, "0a0a", "1414"),     // r1: [0a0a, 1414)
		bnd(t, "1414", "1e1e"),     // r2: [1414, 1e1e)
		bnd(t, "1e1e", ""),         // r3: [1e1e, +inf)
	}
	cases := []struct {
		lo, hi string
		want   []string
	}{
		// interior unit inside one file
		{"0b0b", "1010", []string{"r1"}},
		// unit spanning a file boundary
		{"1313", "1515", []string{"r1", "r2"}},
		// open-lo unit
		{"", "0a0a", []string{"r0"}},
		// open-hi unit
		{"1e1e", "", []string{"r3"}},
		// half-open: file.hi == unit.lo excludes the file
		{"1414", "1717", []string{"r2"}},
		// half-open: file.lo == unit.hi excludes the file
		{"0b0b", "1414", []string{"r1"}},
		// fully open unit keeps everything
		{"", "", []string{"r0", "r1", "r2", "r3"}},
	}
	for i, c := range cases {
		got := pruneByBounds(paths, bounds, c.lo, c.hi, 2)
		if fmt.Sprint(got) != fmt.Sprint(c.want) {
			t.Errorf("case %d [%q,%q): got %v want %v", i, c.lo, c.hi, got, c.want)
		}
	}
}

func TestPruneByBoundsUnstampedKept(t *testing.T) {
	// A file with no header stamp (old writer) must never be pruned.
	paths := []string{"old", "r1"}
	bounds := []keyBounds{{}, bnd(t, "0a0a", "1414")}
	got := pruneByBounds(paths, bounds, "2020", "3030", 2)
	if fmt.Sprint(got) != fmt.Sprint([]string{"old"}) {
		t.Errorf("unstamped file pruned: got %v", got)
	}
}

func TestPruneByBoundsEmptyFallsBack(t *testing.T) {
	// If nothing overlaps (possible for a steal-child remnant), fall back to
	// the full list: the unit then filters to an empty output, exactly the
	// pre-prune behavior -- never an --in-less worker invocation.
	paths := []string{"r0"}
	bounds := []keyBounds{bnd(t, "", "0a0a")}
	got := pruneByBounds(paths, bounds, "1414", "1e1e", 2)
	if fmt.Sprint(got) != fmt.Sprint(paths) {
		t.Errorf("empty prune must fall back to full list: got %v", got)
	}
}

func TestMergeRangeRecordCap(t *testing.T) {
	cases := []struct {
		base    int
		totalIn uint64
		nOuts   int
		want    int
	}{
		{80, 10_000_000, 640, 80}, // fat round: full fan-out
		{80, 8_000, 640, 4},       // small round: capped by records
		{80, 100, 640, 1},         // tiny round: single range
		{80, 0, 640, 1},           // empty round: still one range
		{80, 10_000_000, 40, 40},  // capped by file count
	}
	for i, c := range cases {
		if got := mergeRangeCount(c.base, c.totalIn, c.nOuts); got != c.want {
			t.Errorf("case %d: got %d want %d", i, got, c.want)
		}
	}
}
