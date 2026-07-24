package orchestrator

import (
	"errors"
	"testing"
)

// pickMapDir routes a round's transient map outputs to the tmpfs-backed fast
// dir only when it has comfortable headroom; every uncertain case must fall
// back to the durable run dir (fail-safe: a wrong "disk" answer costs
// bandwidth, a wrong "fast" answer can ENOSPC-abort the run mid-column).
func TestPickMapDir(t *testing.T) {
	const gb = uint64(1) << 30
	cases := []struct {
		name    string
		fastDir string
		inBytes uint64
		avail   uint64
		statErr error
		want    string
	}{
		{"unset fast dir -> run dir", "", 1 * gb, 62 * gb, nil, "run"},
		{"roomy tmpfs -> fast dir", "/dev/shm/x", 10 * gb, 62 * gb, nil, "fast"},
		{"tight tmpfs -> run dir", "/dev/shm/x", 30 * gb, 62 * gb, nil, "run"},
		{"statfs error -> run dir", "/dev/shm/x", 1 * gb, 0, errors.New("boom"), "run"},
		{"zero-input round still needs slack", "/dev/shm/x", 0, 128 << 20, nil, "run"},
		{"zero-input round with slack -> fast", "/dev/shm/x", 0, 1 * gb, nil, "fast"},
	}
	for _, c := range cases {
		got := pickMapDir(c.fastDir, "run", c.inBytes, c.avail, c.statErr)
		want := c.want
		if want == "fast" {
			want = c.fastDir
		}
		if got != want {
			t.Errorf("%s: pickMapDir(%q, run, in=%d, avail=%d, err=%v) = %q, want %q",
				c.name, c.fastDir, c.inBytes, c.avail, c.statErr, got, want)
		}
	}
}
