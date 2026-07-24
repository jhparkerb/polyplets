// fastmap.go — tmpfs routing for transient map outputs (--fast-map-dir).
//
// A map round writes ~the frontier volume as map_*.bin, which the merge
// round reads once and deletes: half of a run's device writes and reads never
// need to touch the durable disk at all (measured: dalby's H20 pole saturates
// its NVMe mirror at ~750MB/s writes + ~720MB/s reads, w_await 17-26ms;
// results/fanin-tax.md ladder section). Routing those files to a
// tmpfs-backed dir (e.g. /dev/shm/<run>) removes the round trip.
//
// Fail-safe by construction: the choice is re-made EVERY round from live
// statfs numbers with 20% headroom over a 2x output projection, so a fat
// round falls back to the run dir instead of filling the tmpfs. If a write
// still hits ENOSPC (projection wrong by >2.4x), the C++ writer aborts
// loudly (writeOrDie) rather than truncating — a dead run, never a wrong
// count. Map outputs are transient: a resume recomputes the round, so tmpfs
// contents are never needed across a reboot.

package orchestrator

import (
	"os"
	"syscall"
)

// pickMapDir is the pure routing decision: fast dir iff it is configured,
// statfs succeeded, and the projected round output (2x input volume, plus a
// 256MB floor for zero/tiny rounds) fits within avail with 20% headroom.
// Every uncertain case answers runDir — the safe, merely-slower choice.
func pickMapDir(fastDir, runDir string, inBytes, availBytes uint64, statErr error) string {
	if fastDir == "" || statErr != nil {
		return runDir
	}
	need := 2*inBytes + 256<<20
	if need+need/5 > availBytes {
		return runDir
	}
	return fastDir
}

// pickMapDirForRound gathers the live inputs for pickMapDir: the frontier
// files' on-disk sizes (compressed sizes when frontier zstd is on — map
// outputs are compressed the same way, so the projection stays comparable)
// and the fast dir's available bytes.
func pickMapDirForRound(fastDir, runDir string, frontier []string) string {
	if fastDir == "" {
		return runDir
	}
	var in uint64
	for _, p := range frontier {
		if st, err := os.Stat(p); err == nil {
			in += uint64(st.Size())
		}
	}
	avail, err := fsAvailBytes(fastDir)
	return pickMapDir(fastDir, runDir, in, avail, err)
}

// fsAvailBytes returns the filesystem's available bytes at path (what an
// unprivileged writer can actually use).
func fsAvailBytes(path string) (uint64, error) {
	var st syscall.Statfs_t
	if err := syscall.Statfs(path, &st); err != nil {
		return 0, err
	}
	return uint64(st.Bavail) * uint64(st.Bsize), nil
}
