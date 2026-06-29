// telemetry.go — per-column cost telemetry, cost-profile emission, and a live
// ETA driven by an optional reference profile.
//
// Every run EMITS a cost profile (per-(H,col) wall + frontier sizes) to the run
// dir; the a-priori predictor scales one of these to the target n to produce a
// reference profile for the next run.  A run that LOADS a reference profile
// reports a live, self-correcting ETA against it.  Without a reference, the run
// still emits per-column telemetry but makes no ETA claim (honest: the first run
// of a sequence has nothing to predict from).
package orchestrator

import (
	"bufio"
	"fmt"
	"math"
	"os"
	"strconv"
	"strings"
	"sync"
	"sync/atomic"
	"time"
)

// ColumnCost is the measured cost of one completed column.
type ColumnCost struct {
	H, Col      int
	FrontierIn  uint64  // records entering the column (map input)
	FrontierOut uint64  // records leaving the column (new frontier)
	WallS       float64 // orchestrator wall-clock for map+merge of this column
	CPUS        float64 // summed worker cpu seconds (map+merge)
	RSSMax      float64 // peak worker RSS (MB) this column
	// Phase split: the map and merge phases run sequentially, so cpu/wall per
	// phase separates "map starved" from "merge dragging the blend". Effective
	// cores in a phase = phase_cpu / phase_wall.
	MapWallS   float64
	MapCPUS    float64
	MergeWallS float64
	MergeCPUS  float64
	// Worker-invocation counts: map units fanned out this column, and merge
	// ranges fanned in. Feed the post-run stats harvest (scripts/job_stats.py)
	// so per-column parallelism is an observed datum, not derived from config.
	NMapUnits    int
	NMergeRanges int
}

// telemetry accumulates ColumnCosts, emits structured progress, writes the cost
// profile, and (if a reference profile is loaded) reports a live ETA.
type telemetry struct {
	t0       time.Time
	cores    int
	maxn     int
	outPath  string
	mu       sync.Mutex       // guards observe() state when heights run concurrently (overlap mode)
	cols     []ColumnCost
	cumWall  float64          // running Σ WallS over observed columns
	clock    func() time.Time // injectable for tests; defaults to time.Now
	hbEvery  time.Duration    // heartbeat cadence (POLY_HEARTBEAT_SECS, default 30s)

	// processed is the live count of input records consumed across the running
	// map units of the current column, fed by worker event=progress lines.
	processed atomic.Uint64

	// steals counts work-stealing tail-splits performed in the current column
	// (reset per column in startColumn); surfaced in the heartbeat.
	steals atomic.Uint64

	// Reference profile for live ETA: (H,col) -> predicted wall seconds.
	ref      map[[2]int]float64
	refTotal float64 // Σ ref over all (H,col)
	refBasis string  // provenance of the reference (path / description)
	donePred float64 // Σ ref wall for completed columns
	doneAct  float64 // Σ actual wall for completed columns
}

// newTelemetry builds a telemetry sink.  refPath may be "" (no live ETA).
func newTelemetry(cfg SweepConfig, t0 time.Time) (*telemetry, error) {
	out := cfg.CostProfileOut
	if out == "" {
		out = cfg.RunDir + "/cost_profile.tsv"
	}
	// Heartbeat cadence defaults to sqrt(checkpoint interval) in seconds: the
	// number of heartbeats between checkpoints is then ~sqrt(checkpoint_s) — a
	// bounded count that stays sparse as the checkpoint interval grows (e.g. a
	// 900s checkpoint → 30s heartbeat → ~30 heartbeats/checkpoint). Env override
	// (POLY_HEARTBEAT_SECS) wins, mainly for tests.
	hb := 30 * time.Second
	if cfg.CheckpointEvery > 0 {
		hb = time.Duration(math.Sqrt(cfg.CheckpointEvery.Seconds()) * float64(time.Second))
	}
	if s := os.Getenv("POLY_HEARTBEAT_SECS"); s != "" {
		if v, err := strconv.ParseFloat(s, 64); err == nil && v > 0 {
			hb = time.Duration(v * float64(time.Second))
		}
	}
	t := &telemetry{
		t0:      t0,
		cores:   cfg.Cores,
		maxn:    cfg.Maxn,
		outPath: out,
		clock:   time.Now,
		hbEvery: hb,
	}
	if cfg.CostProfileRef != "" {
		ref, total, err := LoadCostProfile(cfg.CostProfileRef)
		if err != nil {
			return nil, fmt.Errorf("load reference profile %s: %w", cfg.CostProfileRef, err)
		}
		t.ref = ref
		t.refTotal = total
		t.refBasis = cfg.CostProfileRef
		fmt.Printf("apriori basis=%s apriori_wall_s=%.0f apriori_eta_at=%s\n",
			cfg.CostProfileRef, total, t0.Add(time.Duration(total*float64(time.Second))).Format(time.RFC3339))
	}
	return t, nil
}

// observe records one completed column, emits telemetry + ETA, and rewrites the
// profile file.  A nil receiver is a no-op so callers need not guard.
func (t *telemetry) observe(c ColumnCost) {
	if t == nil {
		return
	}
	t.mu.Lock()
	defer t.mu.Unlock()
	t.cols = append(t.cols, c)
	t.cumWall += c.WallS

	fmt.Printf("event=column H=%d col=%d frontier_in=%d frontier_out=%d "+
		"wall_s=%.2f cum_wall_s=%.1f cpu_s=%.1f rss_max_mb=%.1f "+
		"map_wall_s=%.2f map_cpu_s=%.1f merge_wall_s=%.2f merge_cpu_s=%.1f "+
		"map_units=%d merge_ranges=%d\n",
		c.H, c.Col, c.FrontierIn, c.FrontierOut, c.WallS, t.cumWall, c.CPUS, c.RSSMax,
		c.MapWallS, c.MapCPUS, c.MergeWallS, c.MergeCPUS, c.NMapUnits, c.NMergeRanges)

	if t.ref != nil {
		if pred, ok := t.ref[[2]int{c.H, c.Col}]; ok {
			t.donePred += pred
			t.doneAct += c.WallS
		}
		t.emitETA()
	}

	if err := t.writeProfile(); err != nil {
		fmt.Fprintf(os.Stderr, "telemetry: write profile: %v\n", err)
	}
}

// addProcessed bumps the live input-record counter for the running column.
// Fed by worker event=progress lines streamed from map units.
func (t *telemetry) addProcessed(delta uint64) {
	if t == nil {
		return
	}
	t.processed.Add(delta)
}

// progressFunc returns a fresh per-unit callback that converts a map worker's
// cumulative processed-record count into deltas on the shared column counter.
// Returns nil for a nil telemetry (runWorker treats nil as "no streaming").
func (t *telemetry) progressFunc() func(uint64) {
	if t == nil {
		return nil
	}
	var last uint64
	return func(cumulative uint64) {
		if cumulative >= last {
			t.addProcessed(cumulative - last)
			last = cumulative
		}
	}
}

// steal records one work-stealing tail-split in the current column.  Nil-safe.
func (t *telemetry) steal() {
	if t == nil {
		return
	}
	t.steals.Add(1)
}

// unitProgress wraps the shared column heartbeat callback so a single map
// worker's cumulative processed count is ALSO recorded on its own atomic — the
// stealer reads this to size each in-flight unit's remaining work.  Always
// returns a non-nil callback (it must capture `processed` even when telemetry
// is nil).
func unitProgress(t *telemetry, processed *atomic.Uint64) func(uint64) {
	tf := t.progressFunc()
	return func(cumulative uint64) {
		processed.Store(cumulative)
		if tf != nil {
			tf(cumulative)
		}
	}
}

// startColumn launches a background heartbeat for the column that is about to
// run and returns a stop function (idempotent-safe: call exactly once).  The
// heartbeat reports elapsed time, the aggregate records/s pulse from the
// workers, and — if a reference profile predicts this column — a within-column
// fraction (elapsed / predicted wall).  In fast runs (sub-cadence columns) it
// never fires, so tests stay quiet.
func (t *telemetry) startColumn(H, col int) func() {
	if t == nil {
		return func() {}
	}
	t.processed.Store(0)
	t.steals.Store(0)
	start := t.clock()
	predWall, hasRef := 0.0, false
	if t.ref != nil {
		if w, ok := t.ref[[2]int{H, col}]; ok && w > 0 {
			predWall, hasRef = w, true
		}
	}
	stop := make(chan struct{})
	go func() {
		tick := time.NewTicker(t.hbEvery)
		defer tick.Stop()
		for {
			select {
			case <-stop:
				return
			case <-tick.C:
				el := t.clock().Sub(start).Seconds()
				proc := t.processed.Load()
				steals := t.steals.Load()
				rate := 0.0
				if el > 0 {
					rate = float64(proc) / el
				}
				if hasRef {
					frac := math.Min(el/predWall, 0.999)
					fmt.Printf("event=heartbeat H=%d col=%d elapsed_s=%.0f processed=%d "+
						"rate_per_s=%.0f steals=%d pred_wall_s=%.0f frac=%.3f\n",
						H, col, el, proc, rate, steals, predWall, frac)
				} else {
					fmt.Printf("event=heartbeat H=%d col=%d elapsed_s=%.0f processed=%d "+
						"rate_per_s=%.0f steals=%d\n", H, col, el, proc, rate, steals)
				}
			}
		}
	}()
	var once bool
	return func() {
		if !once {
			once = true
			close(stop)
		}
	}
}

// emitETA prints a cost-weighted done fraction and a self-corrected ETA.
func (t *telemetry) emitETA() {
	if t.refTotal <= 0 {
		return
	}
	correction := 1.0
	if t.donePred > 0 {
		correction = t.doneAct / t.donePred // actual vs predicted pace so far
	}
	doneFrac := t.donePred / t.refTotal
	remainingPred := t.refTotal - t.donePred
	if remainingPred < 0 {
		remainingPred = 0
	}
	etaRemain := remainingPred * correction
	etaAt := t.clock().Add(time.Duration(etaRemain * float64(time.Second)))
	fmt.Printf("event=eta done_frac=%.4f eta_remaining_s=%.0f eta_at=%s "+
		"pace=%.2f basis=ref\n",
		doneFrac, etaRemain, etaAt.Format(time.RFC3339), correction)
}

// writeProfile rewrites the full cost profile (atomic via temp+rename).
func (t *telemetry) writeProfile() error {
	tmp := t.outPath + ".tmp"
	f, err := os.Create(tmp)
	if err != nil {
		return err
	}
	w := bufio.NewWriter(f)
	fmt.Fprintf(w, "# cost_profile maxn=%d cores=%d\n", t.maxn, t.cores)
	fmt.Fprintf(w, "# H\tcol\tfrontier_in\tfrontier_out\twall_s\tcpu_s\trss_max_mb\n")
	for _, c := range t.cols {
		fmt.Fprintf(w, "%d\t%d\t%d\t%d\t%.3f\t%.3f\t%.1f\n",
			c.H, c.Col, c.FrontierIn, c.FrontierOut, c.WallS, c.CPUS, c.RSSMax)
	}
	if err := w.Flush(); err != nil {
		f.Close()
		return err
	}
	if err := f.Close(); err != nil {
		return err
	}
	return os.Rename(tmp, t.outPath)
}

// ProfileMeta holds the header fields of a cost profile.
type ProfileMeta struct {
	Maxn  int
	Cores int
}

// ReadCostProfileFull reads a cost profile into its rows and header metadata.
// Used by the a-priori predictor, which needs frontier/rss columns the live-ETA
// LoadCostProfile path discards.
func ReadCostProfileFull(path string) ([]ColumnCost, ProfileMeta, error) {
	data, err := os.ReadFile(path)
	if err != nil {
		return nil, ProfileMeta{}, err
	}
	var rows []ColumnCost
	var meta ProfileMeta
	for _, line := range strings.Split(string(data), "\n") {
		line = strings.TrimRight(line, "\r")
		if strings.HasPrefix(line, "#") {
			for _, f := range strings.Fields(line) {
				if v, ok := strings.CutPrefix(f, "maxn="); ok {
					meta.Maxn, _ = strconv.Atoi(v)
				} else if v, ok := strings.CutPrefix(f, "cores="); ok {
					meta.Cores, _ = strconv.Atoi(v)
				}
			}
			continue
		}
		if strings.TrimSpace(line) == "" {
			continue
		}
		f := strings.Fields(line)
		if len(f) < 7 {
			continue
		}
		var c ColumnCost
		c.H, _ = strconv.Atoi(f[0])
		c.Col, _ = strconv.Atoi(f[1])
		c.FrontierIn, _ = strconv.ParseUint(f[2], 10, 64)
		c.FrontierOut, _ = strconv.ParseUint(f[3], 10, 64)
		c.WallS, _ = strconv.ParseFloat(f[4], 64)
		c.CPUS, _ = strconv.ParseFloat(f[5], 64)
		c.RSSMax, _ = strconv.ParseFloat(f[6], 64)
		rows = append(rows, c)
	}
	return rows, meta, nil
}

// LoadCostProfile reads a cost profile and returns (H,col)->wall_s plus the total.
// It is the live-ETA view over ReadCostProfileFull's rows.
func LoadCostProfile(path string) (map[[2]int]float64, float64, error) {
	rows, _, err := ReadCostProfileFull(path)
	if err != nil {
		return nil, 0, err
	}
	ref := make(map[[2]int]float64, len(rows))
	var total float64
	for _, c := range rows {
		ref[[2]int{c.H, c.Col}] = c.WallS
		total += c.WallS
	}
	return ref, total, nil
}
