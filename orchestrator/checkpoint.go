// checkpoint.go — POLYCKPT write and read (DESIGN §9).
//
// POLYCKPT format (docs/formats.md; version history there too):
//   POLYCKPT 2
//   H <h>
//   col <c>
//   frontier <path> [<path>...]
//   acct cpu_s=<SUM> wall_s=<SUM> rss_max_mb=<MAX>
//   tri <n> <value>    (accumulated triangle, sparse)
//   htri <n> <value>   (current height's partial row alone, sparse)
//
// The bulk of the checkpoint IS the frontier run files already on disk; the
// POLYCKPT just names them.  Resume reloads the frontier, re-dispatches any
// remaining columns, and seeds accounting from the acct line.
package orchestrator

import (
	"bufio"
	"fmt"
	"math/big"
	"os"
	"path/filepath"
	"strconv"
	"strings"
	"time"
)

// checkpointVersion is the POLYCKPT format version this build WRITES.
//
//	1 — pre-c789bfb: no `htri` lines, so a mid-height resume cannot
//	    reconstruct the height's whole per-height row.
//	2 — carries `htri` (the Zero Harvest fix).
//
// The version is stamped explicitly because absence of `htri` is NOT a usable
// discriminator: the row is sparse-encoded, so a legitimately all-zero partial
// row from a version-2 writer looks exactly like a version-1 ledger. Resume
// refuses the one combination it cannot serve (O2 "Legacy Ledger", see
// checkResumeConfig).
const checkpointVersion = 2

// Checkpoint is the resumable state after completing one column.
type Checkpoint struct {
	Version  int // POLYCKPT format version read from the header (1 when absent)
	H        int
	Col      int      // last COMPLETED column (-1 = none yet)
	Frontier []string // paths to current frontier run files
	// Done is the SET of fully-completed heights in OVERLAP mode (where heights
	// finish out of order, so a single H/col can't express progress). When Done
	// is non-empty the checkpoint is the overlap form: H/Col/Frontier are unused
	// (H=-1) and resume skips the Done heights, re-running the rest from scratch.
	Done []int
	// Triangle holds the accumulated Σ_H T(n,H) for all COMPLETED heights
	// before H, plus contributions from completed columns within H.
	// Indexed by n; len = maxn+1.
	Triangle []*big.Int
	// HTri holds the CURRENT height H's partial contributions alone (the
	// within-H share already merged into Triangle above). Resume seeds the
	// height's sweep with it so the completion-time per-height write
	// (h<H>.out) is whole — without it, a resumed height's per-height row
	// carries only the post-resume columns (the Zero Harvest bug,
	// results/ns_a40/PROVENANCE.md: resuming an already-COMPLETED height has
	// no columns left and wrote all zeros over the good file). Absent from
	// pre-fix checkpoints (nil): the triangle still resumes correctly, only
	// the per-height row can't be reconstructed (writePerHeight's all-zero
	// guard then refuses the worst case).
	HTri []*big.Int
	Acct Acct
	Written  time.Time
	// Run config stamped at write time so resume can hard-fail on a mismatched
	// CLI (a different --maxn/--counter/--fold silently corrupts the triangle).
	Maxn    int
	Counter string // normalized "u64"/"u128"
	Fold    bool
	Kernel  string // normalized "column"/"kink"
	// MaxDiagK is --max-diag-k as resolved at write time (O3 "Strict Route
	// Amnesia"): it decides per height whether a strip is INJECTED from its
	// closed form or REALLY SWEPT, so a resume under a different cap computes
	// a different set of cells than the run it continues — and can manufacture
	// self-confirming holdout evidence. Meaningful only when MaxDiagKSet;
	// checkpoints written before this field existed leave it false.
	MaxDiagK    int
	MaxDiagKSet bool
	// Overlap is --overlap-heights at write time (O4 "Mode Amnesia"). The two
	// checkpoint FORMS are not interchangeable: an overlap (Done-set)
	// checkpoint resumed sequentially short-circuits the B7 height check and
	// re-sweeps everything onto a populated triangle; a sequential checkpoint
	// resumed in overlap mode has no Done set and discards all progress. When
	// OverlapSet is false the mode is inferred from the form (len(Done) > 0),
	// which is exact: runOverlap's only checkpoint writer is markDone, so an
	// overlap checkpoint always names at least one completed height.
	Overlap    int
	OverlapSet bool
}

// Write serializes the checkpoint to path atomically (write-then-rename).
func (ck *Checkpoint) Write(path string) error {
	f, err := os.CreateTemp(filepath.Dir(path), ".polyckpt_tmp_*")
	if err != nil {
		return err
	}
	tmp := f.Name()

	fmt.Fprintf(f, "POLYCKPT %d\n", checkpointVersion)
	fmt.Fprintf(f, "H %d\n", ck.H)
	fmt.Fprintf(f, "col %d\n", ck.Col)
	fmt.Fprintf(f, "config maxn=%d counter=%s fold=%v kernel=%s maxdiagk=%d overlap=%d\n",
		ck.Maxn, ck.Counter, ck.Fold, kernelName(ck.Kernel), ck.MaxDiagK, ck.Overlap)
	fmt.Fprintf(f, "frontier %s\n", strings.Join(ck.Frontier, " "))
	if len(ck.Done) > 0 {
		ds := make([]string, len(ck.Done))
		for i, H := range ck.Done {
			ds[i] = strconv.Itoa(H)
		}
		fmt.Fprintf(f, "done %s\n", strings.Join(ds, " "))
	}
	fmt.Fprintf(f, "acct cpu_s=%.6f wall_s=%.6f rss_max_mb=%.3f\n",
		ck.Acct.CPUS, ck.Acct.WallS, ck.Acct.RSSMax)
	// Sparse triangle: only non-zero entries.
	for n, v := range ck.Triangle {
		if v != nil && v.Sign() != 0 {
			fmt.Fprintf(f, "tri %d %d\n", n, v)
		}
	}
	// Sparse current-height partial row (see HTri). Additive line type:
	// ReadCheckpoint ignores unknown keys, so old readers skip it.
	for n, v := range ck.HTri {
		if v != nil && v.Sign() != 0 {
			fmt.Fprintf(f, "htri %d %d\n", n, v)
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

	ck := &Checkpoint{Col: -1, Version: 1}
	sc := bufio.NewScanner(f)
	sawHeader := false
	for sc.Scan() {
		line := sc.Text()
		if !sawHeader {
			if !strings.HasPrefix(line, "POLYCKPT") {
				return nil, fmt.Errorf("not a POLYCKPT file: %s", path)
			}
			// Version defaults to 1: that is what an unversioned or
			// unparseable header means for every checkpoint ever written.
			if _, v, ok := strings.Cut(line, " "); ok {
				if n, err := strconv.Atoi(strings.TrimSpace(v)); err == nil {
					ck.Version = n
				}
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
		case "done":
			for _, f := range strings.Fields(v) {
				if H, err := strconv.Atoi(f); err == nil {
					ck.Done = append(ck.Done, H)
				}
			}
		case "acct":
			parseAcct(v, &ck.Acct)
		case "tri":
			parts := strings.Fields(v)
			if len(parts) != 2 {
				return nil, fmt.Errorf("%s: malformed tri line %q", path, line)
			}
			n, err1 := strconv.Atoi(parts[0])
			val, ok := new(big.Int).SetString(parts[1], 10)
			if err1 != nil || !ok || n < 0 {
				return nil, fmt.Errorf("%s: malformed tri line %q", path, line)
			}
			for n >= len(ck.Triangle) {
				ck.Triangle = append(ck.Triangle, new(big.Int))
			}
			ck.Triangle[n] = val
		case "htri":
			parts := strings.Fields(v)
			if len(parts) != 2 {
				return nil, fmt.Errorf("%s: malformed htri line %q", path, line)
			}
			n, err1 := strconv.Atoi(parts[0])
			val, ok := new(big.Int).SetString(parts[1], 10)
			if err1 != nil || !ok || n < 0 {
				return nil, fmt.Errorf("%s: malformed htri line %q", path, line)
			}
			for n >= len(ck.HTri) {
				ck.HTri = append(ck.HTri, new(big.Int))
			}
			ck.HTri[n] = val
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
		case "kernel":
			ck.Kernel = v
		case "maxdiagk":
			if n, err := strconv.Atoi(v); err == nil {
				ck.MaxDiagK, ck.MaxDiagKSet = n, true
			}
		case "overlap":
			if n, err := strconv.Atoi(v); err == nil {
				ck.Overlap, ck.OverlapSet = n, true
			}
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
