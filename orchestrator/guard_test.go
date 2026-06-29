package orchestrator

// guard_test.go — refuse-at-start guards (BUGS-OF-SHAME cat 2): an invalid
// config must fail loudly at the start of Run, not silently miscount.

import (
	"context"
	"path/filepath"
	"testing"
)

// TestResumeConfigGuard proves a resume hard-fails when the checkpoint's
// stamped config (maxn/counter/fold) disagrees with the CLI, or when the
// checkpoint height is no longer in the --heights list (B7: startIdx would fall
// back to 0 and double-count completed heights). A matching resume must pass.
func TestResumeConfigGuard(t *testing.T) {
	cfg := SweepConfig{Maxn: 20, CounterWidth: "u64", Fold: true}
	heights := []int{17, 18, 19, 20}
	base := &Checkpoint{H: 18, Maxn: 20, Counter: "u64", Fold: true}

	if err := checkResumeConfig(cfg, base, heights); err != nil {
		t.Errorf("matching resume rejected: %v", err)
	}
	mismatch := func(name string, mutate func(*Checkpoint)) {
		c := *base
		mutate(&c)
		if checkResumeConfig(cfg, &c, heights) == nil {
			t.Errorf("%s mismatch not caught", name)
		}
	}
	mismatch("maxn", func(c *Checkpoint) { c.Maxn = 16 })
	mismatch("counter", func(c *Checkpoint) { c.Counter = "u128" })
	mismatch("fold", func(c *Checkpoint) { c.Fold = false })
	mismatch("height-not-in-list", func(c *Checkpoint) { c.H = 5 })
}

// TestResultWidthGuard proves the orchestrator refuses a maxn the uint64 result
// pipeline cannot hold (a(25) is the last value below 2^64), regardless of
// --counter, instead of silently dropping the overflowing tri rows in
// accounting and reporting a too-low a(n).
func TestResultWidthGuard(t *testing.T) {
	if err := CheckResultWidth(25); err != nil {
		t.Errorf("CheckResultWidth(25) = %v; want nil", err)
	}
	if err := CheckResultWidth(26); err == nil {
		t.Errorf("CheckResultWidth(26) = nil; want refusal (uint64 pipeline overflows past a(25))")
	}
	if err := CheckResultWidth(40); err == nil {
		t.Errorf("CheckResultWidth(40) = nil; want refusal")
	}
}

// TestRejectUnknownCounter proves the seed writer refuses an unrecognized
// --counter tag instead of silently falling back to u64. A typo like "u127"
// would otherwise write a u64 seed with no error, so a run meant to be u128
// could miscount with no signal.
func TestRejectUnknownCounter(t *testing.T) {
	path := filepath.Join(t.TempDir(), "seed_h3.bin")
	if err := WriteSeedPolyrun(path, "test", 3, 8, "u127"); err == nil {
		t.Fatalf(`WriteSeedPolyrun(counter="u127") returned nil error; want rejection of the unknown tag`)
	}
}

// TestCounterWidthGuard proves the FR-7 refuse-at-start guard rejects a maxn
// the counter cannot hold exactly: u64 is valid to a(25), u128 to ~a(48).
// Without the guard an overflowing run starts and wraps silently.
func TestCounterWidthGuard(t *testing.T) {
	mustErr := func(counter string, maxn int) {
		if err := CheckCounterWidth(counter, maxn); err == nil {
			t.Errorf("CheckCounterWidth(%q, %d) = nil; want overflow refusal", counter, maxn)
		}
	}
	mustOK := func(counter string, maxn int) {
		if err := CheckCounterWidth(counter, maxn); err != nil {
			t.Errorf("CheckCounterWidth(%q, %d) = %v; want nil", counter, maxn, err)
		}
	}
	mustOK("u64", 20)   // a(20) fits u64
	mustOK("u64", 25)   // boundary: still exact
	mustErr("u64", 26)  // overflows u64
	mustErr("u64", 30)  // well past
	mustOK("u128", 30)  // fits u128
	mustOK("u128", 48)  // boundary
	mustErr("u128", 49) // overflows u128
	mustErr("u127", 10) // unknown tag
}

// TestMapWorkerFailsOnMissingInput proves a map_worker whose input frontier
// file can't be opened exits nonzero, instead of treating the unreadable file
// as empty and silently dropping its records (a frontier file lost to a GC race
// would otherwise vanish from the count with no signal).
func TestMapWorkerFailsOnMissingInput(t *testing.T) {
	dir := t.TempDir()
	a := MapArgs{
		InPaths:  []string{filepath.Join(dir, "does_not_exist.bin")},
		H:        3,
		Maxn:     8,
		Fold:     true,
		RAM:      4 << 20,
		SpillDir: dir,
		OutPath:  filepath.Join(dir, "out.bin"),
	}
	_, err := RunMapWorker(context.Background(), DefaultWorkerBin(".."), a, nil, nil)
	if err == nil {
		t.Fatalf("map_worker returned success on a missing input file (silent data loss)")
	}
}

// TestRejectZeroCores proves Run refuses Cores<1 instead of silently
// undercounting. With Cores==0 the worker pool spawns zero goroutines, so every
// map phase produces no output and Run returns a too-low triangle with a nil
// error — a silent wrong answer. The guard must turn this into a start-time
// error.
func TestRejectZeroCores(t *testing.T) {
	dir := t.TempDir()
	cfg := baseCfg(t, dir)
	cfg.Cores = 0
	cfg.Heights = []int{2} // a single ordinary (non-closed-form) height
	_, err := Run(context.Background(), cfg, nil)
	if err == nil {
		t.Fatalf("Run(Cores=0) returned nil error (silent undercount); want a refuse-at-start error")
	}
}
