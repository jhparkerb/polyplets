// G3: campaign harness and provenance ledger (implementation-plan.md, Layer 1).
//
// A campaign runs an engine binary split into K deterministic subtree workers
// (the engine's --split mode, invariance-tested by gate G2), supervises them
// with bounded parallelism and retries, checkpoints per-worker results so a
// killed campaign resumes where it stopped, merges worker outputs, and
// appends provenance entries to an append-only JSONL ledger. Verify compares
// two campaigns' merged results (rule 3: a number is submittable only when
// independent runs agree, and the agreement is on the ledger).

package main

import (
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"errors"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"sort"
	"strconv"
	"strings"
	"sync"
	"time"
)

// Spec is the part of a campaign that defines the computation. Operational
// knobs (J, Retries) are not identity: a resume may change them.
type Spec struct {
	Binary  string `json:"binary"`
	Lattice string `json:"lattice"`
	MaxN    int    `json:"maxn"`
	SplitS  int    `json:"split_s"`
	K       int    `json:"k"`
	Retries int    `json:"retries"`
	J       int    `json:"j"`
}

// identity returns the fields that must match for a resume to be legal.
func (s Spec) identity() [5]string {
	return [5]string{s.Binary, s.Lattice,
		strconv.Itoa(s.MaxN), strconv.Itoa(s.SplitS), strconv.Itoa(s.K)}
}

type Campaign struct {
	Dir    string
	Ledger string
	Spec   Spec
}

type LedgerEntry struct {
	Time         string `json:"time"`
	Event        string `json:"event"` // campaign_complete | verified
	Campaign     string `json:"campaign"`
	Other        string `json:"other,omitempty"` // second campaign for verified
	Host         string `json:"host"`
	GitCommit    string `json:"git_commit,omitempty"`
	BinarySHA256 string `json:"binary_sha256,omitempty"`
	ResultSHA256 string `json:"result_sha256"`
	Spec         *Spec  `json:"spec,omitempty"`
}

func fileSHA256(path string) (string, error) {
	data, err := os.ReadFile(path)
	if err != nil {
		return "", err
	}
	sum := sha256.Sum256(data)
	return hex.EncodeToString(sum[:]), nil
}

// writeFileAtomic writes via a temp file + rename so a crash never leaves a
// half-written file that a resume could mistake for a real result.
func writeFileAtomic(path string, data []byte) error {
	tmp := path + ".tmp"
	if err := os.WriteFile(tmp, data, 0o644); err != nil {
		return err
	}
	return os.Rename(tmp, path)
}

func (c *Campaign) workerOut(idx int) string {
	return filepath.Join(c.Dir, "workers", fmt.Sprintf("w%03d.out", idx))
}

func (c *Campaign) workerOK(idx int) string {
	return filepath.Join(c.Dir, "workers", fmt.Sprintf("w%03d.ok", idx))
}

// workerDone reports whether idx has a result whose .ok hash matches.
func (c *Campaign) workerDone(idx int) bool {
	ok, err := os.ReadFile(c.workerOK(idx))
	if err != nil {
		return false
	}
	sum, err := fileSHA256(c.workerOut(idx))
	if err != nil {
		return false
	}
	return strings.TrimSpace(string(ok)) == sum
}

// markWorkerDone installs output for a worker as if it had completed.
// Used by tests; also the seam for importing externally computed shards.
func markWorkerDone(c *Campaign, idx int, output []byte) error {
	if err := writeFileAtomic(c.workerOut(idx), output); err != nil {
		return err
	}
	sum, err := fileSHA256(c.workerOut(idx))
	if err != nil {
		return err
	}
	return writeFileAtomic(c.workerOK(idx), []byte(sum+"\n"))
}

func (c *Campaign) runWorker(idx int) error {
	var lastErr error
	for attempt := 0; attempt <= c.Spec.Retries; attempt++ {
		cmd := exec.Command(c.Spec.Binary, c.Spec.Lattice,
			strconv.Itoa(c.Spec.MaxN), "--split",
			strconv.Itoa(c.Spec.SplitS), strconv.Itoa(c.Spec.K),
			strconv.Itoa(idx))
		out, err := cmd.Output()
		if err != nil {
			lastErr = fmt.Errorf("worker %d attempt %d: %w", idx, attempt+1, err)
			continue
		}
		return markWorkerDone(c, idx, out)
	}
	return lastErr
}

// parseCounts parses "n count" lines into a map.
func parseCounts(data []byte) (map[int]uint64, error) {
	m := make(map[int]uint64)
	for _, line := range strings.Split(strings.TrimSpace(string(data)), "\n") {
		if line == "" {
			continue
		}
		f := strings.Fields(line)
		if len(f) != 2 {
			return nil, fmt.Errorf("bad count line %q", line)
		}
		n, err := strconv.Atoi(f[0])
		if err != nil {
			return nil, fmt.Errorf("bad n in %q: %w", line, err)
		}
		v, err := strconv.ParseUint(f[1], 10, 64)
		if err != nil {
			return nil, fmt.Errorf("bad count in %q: %w", line, err)
		}
		m[n] = v
	}
	return m, nil
}

func readCounts(path string) (map[int]uint64, error) {
	data, err := os.ReadFile(path)
	if err != nil {
		return nil, err
	}
	return parseCounts(data)
}

func formatCounts(m map[int]uint64) []byte {
	ns := make([]int, 0, len(m))
	for n := range m {
		ns = append(ns, n)
	}
	sort.Ints(ns)
	var b strings.Builder
	for _, n := range ns {
		fmt.Fprintf(&b, "%d %d\n", n, m[n])
	}
	return []byte(b.String())
}

// merge sums all workers' counts elementwise, refusing on u64 overflow.
func (c *Campaign) merge() (map[int]uint64, error) {
	total := make(map[int]uint64)
	for idx := 0; idx < c.Spec.K; idx++ {
		m, err := readCounts(c.workerOut(idx))
		if err != nil {
			return nil, fmt.Errorf("worker %d output: %w", idx, err)
		}
		for n, v := range m {
			s := total[n] + v
			if s < total[n] {
				return nil, fmt.Errorf("u64 overflow merging n=%d", n)
			}
			total[n] = s
		}
	}
	return total, nil
}

func appendLedger(path string, e LedgerEntry) error {
	e.Time = time.Now().UTC().Format(time.RFC3339)
	e.Host, _ = os.Hostname()
	if out, err := exec.Command("git", "rev-parse", "--short", "HEAD").Output(); err == nil {
		e.GitCommit = strings.TrimSpace(string(out))
	}
	line, err := json.Marshal(e)
	if err != nil {
		return err
	}
	if err := os.MkdirAll(filepath.Dir(path), 0o755); err != nil {
		return err
	}
	f, err := os.OpenFile(path, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0o644)
	if err != nil {
		return err
	}
	defer f.Close()
	_, err = f.Write(append(line, '\n'))
	return err
}

// Run executes (or resumes) the campaign to completion: spec check, workers
// with bounded parallelism and retries, merge, results.txt, ledger entry.
func (c *Campaign) Run() error {
	if err := os.MkdirAll(filepath.Join(c.Dir, "workers"), 0o755); err != nil {
		return err
	}

	specPath := filepath.Join(c.Dir, "spec.json")
	if data, err := os.ReadFile(specPath); err == nil {
		var prev Spec
		if err := json.Unmarshal(data, &prev); err != nil {
			return fmt.Errorf("corrupt spec.json: %w", err)
		}
		if prev.identity() != c.Spec.identity() {
			return fmt.Errorf("spec mismatch: campaign dir %s was created with %+v",
				c.Dir, prev)
		}
	} else {
		data, _ := json.MarshalIndent(c.Spec, "", "  ")
		if err := writeFileAtomic(specPath, data); err != nil {
			return err
		}
	}

	j := c.Spec.J
	if j < 1 {
		j = 1
	}
	sem := make(chan struct{}, j)
	var wg sync.WaitGroup
	var mu sync.Mutex
	var errs []error
	for idx := 0; idx < c.Spec.K; idx++ {
		if c.workerDone(idx) {
			continue
		}
		wg.Add(1)
		sem <- struct{}{}
		go func(i int) {
			defer wg.Done()
			defer func() { <-sem }()
			if err := c.runWorker(i); err != nil {
				mu.Lock()
				errs = append(errs, err)
				mu.Unlock()
			}
		}(idx)
	}
	wg.Wait()
	if len(errs) > 0 {
		return errors.Join(errs...)
	}

	total, err := c.merge()
	if err != nil {
		return err
	}
	resPath := filepath.Join(c.Dir, "results.txt")
	if err := writeFileAtomic(resPath, formatCounts(total)); err != nil {
		return err
	}
	resSum, err := fileSHA256(resPath)
	if err != nil {
		return err
	}
	binSum, _ := fileSHA256(c.Spec.Binary)
	spec := c.Spec
	return appendLedger(c.Ledger, LedgerEntry{
		Event:        "campaign_complete",
		Campaign:     c.Dir,
		BinarySHA256: binSum,
		ResultSHA256: resSum,
		Spec:         &spec,
	})
}

// Verify compares two campaigns' merged results; on agreement it appends a
// "verified" ledger entry, otherwise it reports the first divergence.
func Verify(dirA, dirB, ledger string) error {
	a, err := readCounts(filepath.Join(dirA, "results.txt"))
	if err != nil {
		return err
	}
	b, err := readCounts(filepath.Join(dirB, "results.txt"))
	if err != nil {
		return err
	}
	if len(a) != len(b) {
		return fmt.Errorf("size mismatch: %d vs %d terms", len(a), len(b))
	}
	for n, v := range a {
		if b[n] != v {
			return fmt.Errorf("disagreement at n=%d: %d vs %d", n, v, b[n])
		}
	}
	sum, err := fileSHA256(filepath.Join(dirA, "results.txt"))
	if err != nil {
		return err
	}
	return appendLedger(ledger, LedgerEntry{
		Event:        "verified",
		Campaign:     dirA,
		Other:        dirB,
		ResultSHA256: sum,
	})
}
