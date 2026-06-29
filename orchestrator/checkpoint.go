// checkpoint.go — POLYCKPT write and read (DESIGN §9).
//
// POLYCKPT format:
//   POLYCKPT 1
//   H <h>
//   col <c>
//   frontier <path> [<path>...]
//   acct cpu_s=<SUM> wall_s=<SUM> rss_max_mb=<MAX>
//
// The bulk of the checkpoint IS the frontier run files already on disk; the
// POLYCKPT just names them.  Resume reloads the frontier, re-dispatches any
// remaining columns, and seeds accounting from the acct line.
package orchestrator

import (
	"bufio"
	"fmt"
	"os"
	"path/filepath"
	"strconv"
	"strings"
	"time"
)

// Checkpoint is the resumable state after completing one column.
type Checkpoint struct {
	H        int
	Col      int      // last COMPLETED column (-1 = none yet)
	Frontier []string // paths to current frontier run files
	// Triangle holds the accumulated Σ_H T(n,H) for all COMPLETED heights
	// before H, plus contributions from completed columns within H.
	// Indexed by n; len = maxn+1.
	Triangle []uint64
	Acct     Acct
	Written  time.Time
	// Run config stamped at write time so resume can hard-fail on a mismatched
	// CLI (a different --maxn/--counter/--fold silently corrupts the triangle).
	Maxn    int
	Counter string // normalized "u64"/"u128"
	Fold    bool
}

// Write serializes the checkpoint to path atomically (write-then-rename).
func (ck *Checkpoint) Write(path string) error {
	f, err := os.CreateTemp(filepath.Dir(path), ".polyckpt_tmp_*")
	if err != nil {
		return err
	}
	tmp := f.Name()

	fmt.Fprintf(f, "POLYCKPT 1\n")
	fmt.Fprintf(f, "H %d\n", ck.H)
	fmt.Fprintf(f, "col %d\n", ck.Col)
	fmt.Fprintf(f, "config maxn=%d counter=%s fold=%v\n", ck.Maxn, ck.Counter, ck.Fold)
	fmt.Fprintf(f, "frontier %s\n", strings.Join(ck.Frontier, " "))
	fmt.Fprintf(f, "acct cpu_s=%.6f wall_s=%.6f rss_max_mb=%.3f\n",
		ck.Acct.CPUS, ck.Acct.WallS, ck.Acct.RSSMax)
	// Sparse triangle: only non-zero entries.
	for n, v := range ck.Triangle {
		if v != 0 {
			fmt.Fprintf(f, "tri %d %d\n", n, v)
		}
	}

	if err := f.Close(); err != nil {
		os.Remove(tmp)
		return err
	}
	return os.Rename(tmp, path)
}

// ReadCheckpoint parses a POLYCKPT file.
func ReadCheckpoint(path string) (*Checkpoint, error) {
	f, err := os.Open(path)
	if err != nil {
		return nil, err
	}
	defer f.Close()

	ck := &Checkpoint{Col: -1}
	sc := bufio.NewScanner(f)
	sawHeader := false
	for sc.Scan() {
		line := sc.Text()
		if !sawHeader {
			if !strings.HasPrefix(line, "POLYCKPT") {
				return nil, fmt.Errorf("not a POLYCKPT file: %s", path)
			}
			sawHeader = true
			continue
		}
		k, v, _ := strings.Cut(line, " ")
		switch k {
		case "H":
			ck.H, _ = strconv.Atoi(v)
		case "col":
			ck.Col, _ = strconv.Atoi(v)
		case "config":
			parseConfig(v, ck)
		case "frontier":
			if v != "" {
				ck.Frontier = strings.Fields(v)
			}
		case "acct":
			parseAcct(v, &ck.Acct)
		case "tri":
			parts := strings.Fields(v)
			if len(parts) == 2 {
				n, err1 := strconv.Atoi(parts[0])
				val, err2 := strconv.ParseUint(parts[1], 10, 64)
				if err1 == nil && err2 == nil {
					for n >= len(ck.Triangle) {
						ck.Triangle = append(ck.Triangle, 0)
					}
					ck.Triangle[n] = val
				}
			}
		}
	}
	if !sawHeader {
		return nil, fmt.Errorf("empty POLYCKPT file: %s", path)
	}
	return ck, sc.Err()
}

func parseConfig(s string, ck *Checkpoint) {
	for _, field := range strings.Fields(s) {
		k, v, ok := strings.Cut(field, "=")
		if !ok {
			continue
		}
		switch k {
		case "maxn":
			ck.Maxn, _ = strconv.Atoi(v)
		case "counter":
			ck.Counter = v
		case "fold":
			ck.Fold = v == "true"
		}
	}
}

func parseAcct(s string, a *Acct) {
	for _, field := range strings.Fields(s) {
		k, v, ok := strings.Cut(field, "=")
		if !ok {
			continue
		}
		switch k {
		case "cpu_s":
			a.CPUS, _ = strconv.ParseFloat(v, 64)
		case "wall_s":
			a.WallS, _ = strconv.ParseFloat(v, 64)
		case "rss_max_mb":
			a.RSSMax, _ = strconv.ParseFloat(v, 64)
		}
	}
}
