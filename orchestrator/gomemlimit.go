// gomemlimit.go — soft memory limit for the orchestrator process.
//
// AUDIT-2026-07-30 O6 "Unbounded Orchestrator Heap", closing the open item in
// docs/engine-record.md. The orchestrator sets GOGC=1000 (the
// utilization work: default GOGC=100 churned ~8000 GC cycles against a tiny
// heap goal for no reason). GOGC alone is a RATIO, with no ceiling: the heap
// is allowed to grow to 11x live before a collection, which is how head #4
// reached 4.4 GB and climbing. The audit found NO leak — telemetry is
// streamed and every pool is capped — so the fix is a bound, not a hunt:
// GOGC=1000 keeps the low GC rate, debug.SetMemoryLimit caps what that ratio
// can cost. Go's soft limit makes the collector work harder as the limit is
// approached rather than failing, so an under-sized limit costs CPU, never
// correctness.
package orchestrator

import (
	"fmt"
	"math"
	"os"
	"runtime/debug"
	"strconv"
)

// goMemLimitDefaultGB is the default soft heap ceiling. The orchestrator's
// live heap is tens of MB; 4 GiB is ~2 orders of magnitude of headroom and
// still an order of magnitude under the RSS that made it an OOM contributor.
const goMemLimitDefaultGB = 4

// ApplyGoMemoryLimit sets the process's soft memory limit and returns the
// value applied. POLY_GO_MEMLIMIT_GB overrides the default; 0 disables the
// limit entirely (math.MaxInt64, Go's own default). A set-but-unusable value
// is an error rather than a silent fallback — same posture as
// POLY_FASTMAP_FLOOR_GB (O5).
func ApplyGoMemoryLimit() (int64, error) {
	gb := goMemLimitDefaultGB
	if e, set := os.LookupEnv("POLY_GO_MEMLIMIT_GB"); set {
		v, err := strconv.Atoi(e)
		if err != nil || v < 0 {
			return 0, fmt.Errorf("POLY_GO_MEMLIMIT_GB=%q: want a whole number of GB >= 0 (0 = no limit)", e)
		}
		gb = v
	}
	limit := int64(math.MaxInt64)
	if gb > 0 {
		limit = int64(gb) << 30
	}
	debug.SetMemoryLimit(limit)
	return limit, nil
}
