// fastmap.go — tmpfs routing for transient map outputs (--fast-map-dir).
//
// A map round writes ~the frontier volume as map_*.bin, which the merge
// round reads once and deletes: half of a run's device writes and reads never
// need to touch the durable disk at all (measured: dalby's H20 pole saturates
// its NVMe mirror; results/fanin-tax.md Mirror Toll). Routing those files to
// a tmpfs-backed dir (e.g. /dev/shm/<run>) removes the round trip — measured
// 1.5x on a(39)'s H20 pole columns.
//
// tmpfs pages ARE RAM. The original per-round statfs check was a TOCTOU race
// under --overlap-heights: N heights' rounds each passed a point-in-time
// "enough free" check, collectively overfilled /dev/shm, and the OOM killer
// took out the tmux server (a(40) launch, 2026-07-25 — the second occurrence
// of the a(35) tmpfs failure class). Routing therefore goes through a
// RESERVER: a round reserves its projection under a lock before touching
// tmpfs and releases when its map phase ends, with a hard floor of RAM slack
// kept free at all times. Uncertain cases (statfs error, floor breach) fall
// back to the run dir — the safe, merely-slower choice. If a projection is
// still wrong by >2.4x the C++ writer aborts loudly on ENOSPC (writeOrDie)
// rather than truncating.

package orchestrator

import (
	"os"
	"strconv"
	"sync"
	"syscall"
)

// fastMapReserver serializes tmpfs admission for concurrent map rounds.
// statfs reflects bytes already written by in-flight rounds; held covers the
// not-yet-written remainder of their projections — counting both is
// deliberately conservative.
type fastMapReserver struct {
	avail func() (uint64, error) // live available bytes in the fast dir
	floor uint64                 // hard RAM slack kept free at all times
	mu    sync.Mutex
	held  uint64
}

func newFastMapReserver(avail func() (uint64, error), floor uint64) *fastMapReserver {
	return &fastMapReserver{avail: avail, floor: floor}
}

func (r *fastMapReserver) reserve(need uint64) bool {
	r.mu.Lock()
	defer r.mu.Unlock()
	a, err := r.avail()
	if err != nil {
		return false
	}
	if need+r.held+r.floor > a {
		return false
	}
	r.held += need
	return true
}

func (r *fastMapReserver) release(need uint64) {
	r.mu.Lock()
	defer r.mu.Unlock()
	if need > r.held {
		r.held = 0
		return
	}
	r.held -= need
}

// newFastMapReserverFor builds the production reserver for a fast dir. Floor
// default 24GB (env POLY_FASTMAP_FLOOR_GB): on a 125GB box with 80 workers x
// 1GiB spill budgets, tmpfs admission tops out well under the level that
// starved the a(40) launch.
func newFastMapReserverFor(fastDir string) *fastMapReserver {
	floor := uint64(24) << 30
	if e := os.Getenv("POLY_FASTMAP_FLOOR_GB"); e != "" {
		if v, err := strconv.Atoi(e); err == nil && v > 0 {
			floor = uint64(v) << 30
		}
	}
	return newFastMapReserver(func() (uint64, error) { return fsAvailBytes(fastDir) }, floor)
}

// mapRoundProjection is the reserve size for a round reading the given
// frontier files: 2x their on-disk volume (map outputs are bounded by ~the
// input volume per stage round; 2x covers expansion stages) plus a floor for
// zero/tiny rounds.
func mapRoundProjection(frontier []string) uint64 {
	var in uint64
	for _, p := range frontier {
		if st, err := os.Stat(p); err == nil {
			in += uint64(st.Size())
		}
	}
	return 2*in + 256<<20
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
