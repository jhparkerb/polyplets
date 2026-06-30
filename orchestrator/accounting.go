// accounting.go — worker event-line parsing and accounting aggregation.
package orchestrator

import (
	"fmt"
	"strconv"
	"strings"
)

// Acct accumulates resource usage across workers and across checkpoint segments.
// cpu_s and wall_s SUM; rss_max is MAX (per DESIGN §9 / checkpoint.go fold rule).
type Acct struct {
	CPUS   float64
	WallS  float64
	RSSMax float64
}

func (a *Acct) Add(b Acct) {
	a.CPUS += b.CPUS
	a.WallS += b.WallS
	if b.RSSMax > a.RSSMax {
		a.RSSMax = b.RSSMax
	}
}

func (a Acct) String() string {
	return fmt.Sprintf("cpu_s=%.3f wall_s=%.3f rss_max_mb=%.1f", a.CPUS, a.WallS, a.RSSMax)
}

// WorkerResult holds the parsed output of one map_worker or merge_worker call.
type WorkerResult struct {
	// Triangle contributions from map_worker (H -> n -> value).
	// Empty for merge_worker.
	TriContribs map[int]map[int]uint64
	OutRecords  uint64
	SpillBytes  uint64
	// StopKey is non-empty iff a map_worker stopped early at a work-stealing
	// cursor: its output covers [lo, StopKey) and the orchestrator must requeue
	// [StopKey, hi).  Empty = the worker ran its whole [lo, hi) to completion.
	StopKey string
	Acct    Acct
}

// ParseWorkerOutput parses all lines of worker stdout into a WorkerResult.
// Lines may be "tri H n V" (map_worker) or "event=done key=value...".
func ParseWorkerOutput(lines []string) WorkerResult {
	r := WorkerResult{TriContribs: make(map[int]map[int]uint64)}
	for _, line := range lines {
		line = strings.TrimSpace(line)
		if strings.HasPrefix(line, "tri ") {
			var H, n int
			var vs string
			if _, err := fmt.Sscanf(line, "tri %d %d %s", &H, &n, &vs); err == nil {
				v, err := strconv.ParseUint(vs, 10, 64)
				if err == nil {
					if r.TriContribs[H] == nil {
						r.TriContribs[H] = make(map[int]uint64)
					}
					r.TriContribs[H][n] += v
				}
			}
			continue
		}
		if strings.HasPrefix(line, "event=done") {
			parseEventDone(line, &r)
		}
	}
	return r
}

func parseEventDone(line string, r *WorkerResult) {
	for _, field := range strings.Fields(line) {
		k, v, ok := strings.Cut(field, "=")
		if !ok {
			continue
		}
		switch k {
		case "cpu_s":
			r.Acct.CPUS, _ = strconv.ParseFloat(v, 64)
		case "wall_s":
			r.Acct.WallS, _ = strconv.ParseFloat(v, 64)
		case "peak_rss_mb":
			r.Acct.RSSMax, _ = strconv.ParseFloat(v, 64)
		case "records":
			r.OutRecords, _ = strconv.ParseUint(v, 10, 64)
		case "spill_bytes":
			r.SpillBytes, _ = strconv.ParseUint(v, 10, 64)
		case "stop_key":
			r.StopKey = v
		}
	}
}
