// accounting.go — worker event-line parsing and accounting aggregation.
package orchestrator

import (
	"fmt"
	"math/big"
	"strconv"
	"strings"
)

// Acct accumulates resource usage across workers and across checkpoint segments.
// cpu_s and wall_s SUM; rss_max is MAX (the same fold checkpoint.go uses).
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
	TriContribs map[int]map[int]*big.Int
	OutRecords  uint64
	SpillBytes  uint64
	// StopKey is non-empty iff a map_worker stopped early at a work-stealing
	// cursor: its output covers [lo, StopKey) and the orchestrator must requeue
	// [StopKey, hi).  Empty = the worker ran its whole [lo, hi) to completion.
	StopKey string
	Acct    Acct
}

// ParseWorkerOutput parses all lines of worker stdout into a WorkerResult.
// Lines may be "tri H n V" (map_worker) or "event=done key=value...". A
// malformed "tri" line is a hard error (fail-closed) rather than a silent
// skip: a worker only ever emits well-formed tri lines, so a bad one means
// real corruption, not a value to quietly drop. Values are big.Int, so no
// width is too wide.
func ParseWorkerOutput(lines []string) (WorkerResult, error) {
	r := WorkerResult{TriContribs: make(map[int]map[int]*big.Int)}
	for _, line := range lines {
		line = strings.TrimSpace(line)
		if strings.HasPrefix(line, "tri ") {
			var H, n int
			var vs string
			if _, err := fmt.Sscanf(line, "tri %d %d %s", &H, &n, &vs); err != nil {
				return WorkerResult{}, fmt.Errorf("malformed tri line %q: %w", line, err)
			}
			v, ok := new(big.Int).SetString(vs, 10)
			if !ok {
				return WorkerResult{}, fmt.Errorf("malformed tri value %q in line %q", vs, line)
			}
			if r.TriContribs[H] == nil {
				r.TriContribs[H] = make(map[int]*big.Int)
			}
			if cur, seen := r.TriContribs[H][n]; seen {
				cur.Add(cur, v)
			} else {
				r.TriContribs[H][n] = v
			}
			continue
		}
		if strings.HasPrefix(line, "event=done") {
			if err := parseEventDone(line, &r); err != nil {
				return WorkerResult{}, err
			}
		}
	}
	return r, nil
}

// parseEventDone reads the done line's key=value fields. Every number must
// parse, and records must be present: a unit whose records reads 0 has its
// output deleted as empty.
func parseEventDone(line string, r *WorkerResult) error {
	sawRecords := false
	for _, field := range strings.Fields(line) {
		k, v, ok := strings.Cut(field, "=")
		if !ok {
			continue
		}
		var err error
		switch k {
		case "cpu_s":
			r.Acct.CPUS, err = strconv.ParseFloat(v, 64)
		case "wall_s":
			r.Acct.WallS, err = strconv.ParseFloat(v, 64)
		case "peak_rss_mb":
			r.Acct.RSSMax, err = strconv.ParseFloat(v, 64)
		case "records":
			r.OutRecords, err = strconv.ParseUint(v, 10, 64)
			sawRecords = true
		case "spill_bytes":
			r.SpillBytes, err = strconv.ParseUint(v, 10, 64)
		case "stop_key":
			r.StopKey = v
		}
		if err != nil {
			return fmt.Errorf("malformed done line %q: %w", line, err)
		}
	}
	if !sawRecords {
		return fmt.Errorf("done line has no records count: %q", line)
	}
	return nil
}
