// telemetry_test.go — D3 (Even Keel): per-round effective-cores telemetry.
package orchestrator

import (
	"bufio"
	"io"
	"os"
	"strings"
	"testing"
	"time"
)

// captureStdout redirects os.Stdout for the duration of fn and returns
// everything written to it.
func captureStdout(t *testing.T, fn func()) string {
	t.Helper()
	r, w, err := os.Pipe()
	if err != nil {
		t.Fatalf("os.Pipe: %v", err)
	}
	orig := os.Stdout
	os.Stdout = w
	defer func() { os.Stdout = orig }()

	fn()

	if err := w.Close(); err != nil {
		t.Fatalf("close pipe writer: %v", err)
	}
	var sb strings.Builder
	if _, err := io.Copy(&sb, bufio.NewReader(r)); err != nil {
		t.Fatalf("read pipe: %v", err)
	}
	return sb.String()
}

// TestEffCores checks the pure cpu_s/wall_s computation (NOT divided by
// cores) and its divide-by-zero guard.
func TestEffCores(t *testing.T) {
	cases := []struct {
		cpu, wall, want float64
	}{
		{160, 2, 80},    // 160 cpu-seconds over 2 wall-seconds -> 80 cores busy
		{6.8, 1, 6.8},   // the benchmark's "before" figure
		{74.6, 1, 74.6}, // the benchmark's "after" figure
		{10, 0, 0},      // zero wall must not divide-by-zero
		{0, 0, 0},
	}
	for _, c := range cases {
		if got := effCores(c.cpu, c.wall); got != c.want {
			t.Errorf("effCores(%v, %v) = %v, want %v", c.cpu, c.wall, got, c.want)
		}
	}
}

// TestObserveRoundEmitsEffCores verifies a synthetic round with known
// cpu/wall emits map_eff_cores and merge_eff_cores on the event=kink_round
// line, and that all pre-existing fields survive unchanged (pure addition).
func TestObserveRoundEmitsEffCores(t *testing.T) {
	tel, err := newTelemetry(SweepConfig{Cores: 80, Maxn: 20, RunDir: t.TempDir()}, time.Now())
	if err != nil {
		t.Fatalf("newTelemetry: %v", err)
	}

	out := captureStdout(t, func() {
		// map: 160 cpu-seconds over 4 wall-seconds -> 40 effective cores.
		// merge: 37.3 cpu-seconds over 0.5 wall-seconds -> 74.6 effective cores
		// (the benchmark's "after" figure).
		tel.observeRound(18, 7, "stage3", 1_000_000, 4, 160, 0.5, 37.3, 40, 80)
	})

	line := strings.TrimSpace(out)
	if !strings.HasPrefix(line, "event=kink_round ") {
		t.Fatalf("unexpected line: %q", line)
	}
	for _, want := range []string{
		"H=18", "col=7", "round=stage3", "frontier_in=1000000",
		"map_wall_s=4.000", "map_cpu_s=160.000",
		"merge_wall_s=0.500", "merge_cpu_s=37.300",
		"map_units=40", "merge_ranges=80",
		"map_eff_cores=40.00", "merge_eff_cores=74.60",
	} {
		if !strings.Contains(line, want) {
			t.Errorf("event=kink_round line missing %q: %s", want, line)
		}
	}
}

// TestObserveEmitsEffCores verifies the per-column event=column line gains
// eff_cores as a pure addition (no existing field renamed or removed).
func TestObserveEmitsEffCores(t *testing.T) {
	tel, err := newTelemetry(SweepConfig{Cores: 80, Maxn: 20, RunDir: t.TempDir()}, time.Now())
	if err != nil {
		t.Fatalf("newTelemetry: %v", err)
	}

	out := captureStdout(t, func() {
		tel.observe(ColumnCost{
			H: 18, Col: 7, FrontierIn: 16_000_000, FrontierOut: 15_500_000,
			WallS: 10, CPUS: 746, RSSMax: 512,
			MapWallS: 6, MapCPUS: 480, MergeWallS: 4, MergeCPUS: 266,
			NMapUnits: 640, NMergeRanges: 80,
		})
	})

	line := strings.TrimSpace(out)
	if !strings.HasPrefix(line, "event=column ") {
		t.Fatalf("unexpected line: %q", line)
	}
	for _, want := range []string{
		"H=18", "col=7", "frontier_in=16000000", "frontier_out=15500000",
		"wall_s=10.00", "cpu_s=746.0", "rss_max_mb=512.0",
		"map_wall_s=6.00", "map_cpu_s=480.0", "merge_wall_s=4.00", "merge_cpu_s=266.0",
		"map_units=640", "merge_ranges=80",
		"eff_cores=74.60",
	} {
		if !strings.Contains(line, want) {
			t.Errorf("event=column line missing %q: %s", want, line)
		}
	}
}
