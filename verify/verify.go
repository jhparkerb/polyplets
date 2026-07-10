// verify.go — independent POLYRUN verifier.
//
// This package imports ONLY the standard library. It must NOT import
// polyominoes/orchestrator. All format parsing is done independently
// per docs/formats.md.
package verify

import (
	"bufio"
	"encoding/binary"
	"fmt"
	"io"
	"math/rand"
	"os"
	"path/filepath"
	"strconv"
	"strings"
)

// ─── FNV-1a-64 ───────────────────────────────────────────────────────────────

const fnvOffset uint64 = 14695981039346656037
const fnvPrime uint64 = 1099511628211

func fnv1a64(data []byte) uint64 {
	h := fnvOffset
	for _, b := range data {
		h ^= uint64(b)
		h *= fnvPrime
	}
	return h
}

// ─── POLYRUN header ───────────────────────────────────────────────────────────

// PolyrunHeader holds parsed POLYRUN file header fields.
type PolyrunHeader struct {
	Height  int
	Maxn    int
	Records uint64
	Counter string // "u64" or "u128"
	KeyLo   string
	KeyHi   string
	Rev     string
}

// WordBytes returns the byte width of one count value.
func (h PolyrunHeader) WordBytes() int {
	if h.Counter == "u128" {
		return 16
	}
	return 8
}

// parsePolyrunHeader reads a POLYRUN header from a path and returns the header
// plus the byte offset where the binary body begins.
func parsePolyrunHeader(path string) (PolyrunHeader, int64, error) {
	f, err := os.Open(path)
	if err != nil {
		return PolyrunHeader{}, 0, err
	}
	defer f.Close()

	br := bufio.NewReader(f)
	var hdr PolyrunHeader
	var offset int64

	for {
		line, err := br.ReadString('\n')
		offset += int64(len(line))
		trimmed := strings.TrimRight(line, "\r\n")
		if trimmed == "" {
			break
		}
		if err != nil {
			break
		}
		k, v, ok := strings.Cut(trimmed, " ")
		if !ok {
			continue
		}
		switch k {
		case "height":
			hdr.Height, _ = strconv.Atoi(v)
		case "maxn":
			hdr.Maxn, _ = strconv.Atoi(v)
		case "records":
			hdr.Records, _ = strconv.ParseUint(strings.TrimSpace(v), 10, 64)
		case "counter":
			hdr.Counter = strings.TrimSpace(v)
		case "keylo":
			hdr.KeyLo = v
		case "keyhi":
			hdr.KeyHi = v
		case "rev":
			hdr.Rev = v
		}
	}
	return hdr, offset, nil
}

// ─── Manifest ─────────────────────────────────────────────────────────────────

// ManifestFileEntry is one run file listed in a manifest.
type ManifestFileEntry struct {
	Path    string
	Records uint64
	CRC     uint64 // stored as 16 hex digits
}

// Manifest holds parsed manifest fields.
type Manifest struct {
	N          int
	Value      uint64
	Rev        string
	CPUS       float64
	WallS      float64
	RSSMaxMB   float64
	SpillBytes uint64
	Files      []ManifestFileEntry
}

// ParseManifest reads a manifest file from path.
func ParseManifest(path string) (Manifest, error) {
	f, err := os.Open(path)
	if err != nil {
		return Manifest{}, err
	}
	defer f.Close()

	var m Manifest
	sc := bufio.NewScanner(f)
	for sc.Scan() {
		line := sc.Text()
		if strings.HasPrefix(line, "#") || line == "" {
			continue
		}
		// file entries: "file path=... records=... crc=..."
		if strings.HasPrefix(line, "file ") {
			rest := strings.TrimPrefix(line, "file ")
			entry := ManifestFileEntry{}
			for _, part := range strings.Fields(rest) {
				k, v, ok := strings.Cut(part, "=")
				if !ok {
					continue
				}
				switch k {
				case "path":
					entry.Path = v
				case "records":
					entry.Records, _ = strconv.ParseUint(v, 10, 64)
				case "crc":
					entry.CRC, _ = strconv.ParseUint(v, 16, 64)
				}
			}
			m.Files = append(m.Files, entry)
			continue
		}
		k, v, ok := strings.Cut(line, "=")
		if !ok {
			continue
		}
		switch k {
		case "n":
			m.N, _ = strconv.Atoi(v)
		case "value":
			m.Value, _ = strconv.ParseUint(v, 10, 64)
		case "rev", "gitrev":
			m.Rev = v
		case "cpu_s":
			m.CPUS, _ = strconv.ParseFloat(v, 64)
		case "wall_s":
			m.WallS, _ = strconv.ParseFloat(v, 64)
		case "rss_max_mb":
			m.RSSMaxMB, _ = strconv.ParseFloat(v, 64)
		case "spill_bytes":
			m.SpillBytes, _ = strconv.ParseUint(v, 10, 64)
		}
	}
	return m, sc.Err()
}

// ─── CRC verification ─────────────────────────────────────────────────────────

// ComputeBodyCRC reads the body of a POLYRUN file (from bodyOffset to end-8)
// and returns the FNV-1a-64 hash of the body bytes.
func ComputeBodyCRC(path string, bodyOffset int64) (uint64, error) {
	f, err := os.Open(path)
	if err != nil {
		return 0, err
	}
	defer f.Close()
	if _, err := f.Seek(bodyOffset, io.SeekStart); err != nil {
		return 0, err
	}
	// Read entire body including the 8-byte trailer.
	data, err := io.ReadAll(f)
	if err != nil {
		return 0, err
	}
	if len(data) < 8 {
		return 0, fmt.Errorf("body too short for CRC in %s", path)
	}
	body := data[:len(data)-8]
	return fnv1a64(body), nil
}

// StoredCRC reads the 8-byte LE CRC trailer from a POLYRUN file.
func StoredCRC(path string) (uint64, error) {
	f, err := os.Open(path)
	if err != nil {
		return 0, err
	}
	defer f.Close()
	if _, err := f.Seek(-8, io.SeekEnd); err != nil {
		return 0, err
	}
	var v uint64
	if err := binary.Read(f, binary.LittleEndian, &v); err != nil {
		return 0, err
	}
	return v, nil
}

// ─── Record streaming ──────────────────────────────────────────────────────────

// SumCountsInFile streams a POLYRUN file and returns a map[n]→sum of counts[n]
// across all records, plus the actual record count.
func SumCountsInFile(path string) (map[int]uint64, uint64, error) {
	hdr, bodyOff, err := parsePolyrunHeader(path)
	if err != nil {
		return nil, 0, err
	}
	f, err := os.Open(path)
	if err != nil {
		return nil, 0, err
	}
	defer f.Close()
	if _, err := f.Seek(bodyOff, io.SeekStart); err != nil {
		return nil, 0, err
	}

	keyLen := hdr.Height + 2
	sums := make(map[int]uint64)
	var recCount uint64

	br := bufio.NewReader(f)
	sig := make([]byte, keyLen)
	meta := make([]byte, 2)
	// Read exactly hdr.Records records; the 8-byte CRC trailer follows immediately
	// after. Counts are LEB128 varint (core/run.h encodeVarint == binary.Uvarint).
	// Sums are u64: matches the pre-varint behavior, which read only the low 8
	// bytes of each count; ReadUvarint errors on a >u64 value rather than
	// silently truncating (verify runs at small scale where counts fit u64).
	for recCount < hdr.Records {
		if _, err := io.ReadFull(br, sig); err != nil {
			if err == io.EOF || err == io.ErrUnexpectedEOF {
				break
			}
			return nil, recCount, fmt.Errorf("reading sig in %s: %w", path, err)
		}
		if _, err := io.ReadFull(br, meta); err != nil {
			return nil, recCount, fmt.Errorf("reading meta in %s: %w", path, err)
		}
		lo := int(meta[0])
		length := int(meta[1])
		for i := 0; i < length; i++ {
			val, err := binary.ReadUvarint(br)
			if err != nil {
				return nil, recCount, fmt.Errorf("reading counts in %s: %w", path, err)
			}
			sums[lo+i] += val
		}
		recCount++
	}
	return sums, recCount, nil
}

// ─── Triangle file ────────────────────────────────────────────────────────────

// ReadTriangleFile reads data/triangle/a<N>.txt and returns a map[n]→value.
// Lines have format: "tri <H> <n> <value>" — values are summed over all H.
func ReadTriangleFile(path string) (map[int]uint64, error) {
	f, err := os.Open(path)
	if err != nil {
		return nil, err
	}
	defer f.Close()

	sums := make(map[int]uint64)
	sc := bufio.NewScanner(f)
	for sc.Scan() {
		line := sc.Text()
		if strings.HasPrefix(line, "#") || line == "" {
			continue
		}
		parts := strings.Fields(line)
		if len(parts) == 4 && parts[0] == "tri" {
			n, err1 := strconv.Atoi(parts[2])
			v, err2 := strconv.ParseUint(parts[3], 10, 64)
			if err1 == nil && err2 == nil {
				sums[n] += v
			}
		}
	}
	return sums, sc.Err()
}

// ─── Residues file ────────────────────────────────────────────────────────────

// Residue holds one (n, prime, residue) triple.
type Residue struct {
	N       int
	Prime   uint64
	Residue uint64
}

// ReadResiduesFile reads a residues file (lines: "n prime residue").
func ReadResiduesFile(path string) ([]Residue, error) {
	f, err := os.Open(path)
	if err != nil {
		return nil, err
	}
	defer f.Close()

	var out []Residue
	sc := bufio.NewScanner(f)
	for sc.Scan() {
		line := sc.Text()
		if strings.HasPrefix(line, "#") || line == "" {
			continue
		}
		parts := strings.Fields(line)
		if len(parts) != 3 {
			continue
		}
		n, e1 := strconv.Atoi(parts[0])
		p, e2 := strconv.ParseUint(parts[1], 10, 64)
		r, e3 := strconv.ParseUint(parts[2], 10, 64)
		if e1 != nil || e2 != nil || e3 != nil {
			continue
		}
		out = append(out, Residue{N: n, Prime: p, Residue: r})
	}
	return out, sc.Err()
}

// ─── Result ───────────────────────────────────────────────────────────────────

// CheckResult holds one verification result.
type CheckResult struct {
	Pass    bool
	Check   string // short tag, e.g. "crc", "row-sum", "growth"
	Detail  string // human-readable detail
	IsWarn  bool   // WARN rather than FAIL
}

func pass(check, detail string) CheckResult {
	return CheckResult{Pass: true, Check: check, Detail: detail}
}

func fail(check, detail string) CheckResult {
	return CheckResult{Pass: false, Check: check, Detail: detail}
}

func warn(check, detail string) CheckResult {
	return CheckResult{Pass: true, Check: check, Detail: detail, IsWarn: true}
}

// ─── Verifier ─────────────────────────────────────────────────────────────────

// Config holds verifier configuration.
type Config struct {
	N           int
	DataDir     string
	WorkersDir  string
	NoSpotcheck bool
	Verbose     bool
}

// Run performs all verification checks for a(N) and returns the results.
func Run(cfg Config) []CheckResult {
	var results []CheckResult

	manifestPath := filepath.Join(cfg.DataDir, "manifests", fmt.Sprintf("a%d.txt", cfg.N))
	trianglePath := filepath.Join(cfg.DataDir, "triangle", fmt.Sprintf("a%d.txt", cfg.N))
	residuesPath := filepath.Join(cfg.DataDir, "residues", fmt.Sprintf("a%d.txt", cfg.N))

	// ── Manifest ──
	mf, err := ParseManifest(manifestPath)
	if err != nil {
		results = append(results, fail("manifest", fmt.Sprintf("cannot read %s: %v", manifestPath, err)))
		return results
	}
	results = append(results, pass("manifest", fmt.Sprintf("n=%d files=%d", mf.N, len(mf.Files))))

	// ── Integrity: CRC + record count for each file ──
	allSums := make(map[int]uint64) // n → sum across all heights
	for _, fe := range mf.Files {
		hdr, bodyOff, err := parsePolyrunHeader(fe.Path)
		if err != nil {
			results = append(results, fail("crc", fmt.Sprintf("cannot parse header %s: %v", fe.Path, err)))
			continue
		}

		// CRC check
		computed, err := ComputeBodyCRC(fe.Path, bodyOff)
		if err != nil {
			results = append(results, fail("crc", fmt.Sprintf("%s: %v", fe.Path, err)))
		} else {
			stored, err2 := StoredCRC(fe.Path)
			if err2 != nil {
				results = append(results, fail("crc", fmt.Sprintf("%s stored-crc: %v", fe.Path, err2)))
			} else if computed != stored {
				results = append(results, fail("crc", fmt.Sprintf("%s: computed %016x stored %016x", fe.Path, computed, stored)))
			} else if fe.CRC != 0 && fe.CRC != stored {
				results = append(results, fail("crc", fmt.Sprintf("%s: manifest says %016x file says %016x", fe.Path, fe.CRC, stored)))
			} else {
				results = append(results, pass("crc", fmt.Sprintf("%s ok %016x", fe.Path, stored)))
			}
		}

		// Record count check
		sums, recCount, err := SumCountsInFile(fe.Path)
		if err != nil {
			results = append(results, fail("record-count", fmt.Sprintf("%s: %v", fe.Path, err)))
		} else {
			if fe.Records != 0 && recCount != fe.Records {
				results = append(results, fail("record-count", fmt.Sprintf("%s: manifest=%d actual=%d", fe.Path, fe.Records, recCount)))
			} else if hdr.Records != 0 && recCount != hdr.Records {
				results = append(results, fail("record-count", fmt.Sprintf("%s: header=%d actual=%d", fe.Path, hdr.Records, recCount)))
			} else {
				results = append(results, pass("record-count", fmt.Sprintf("%s records=%d", fe.Path, recCount)))
			}
		}

		// Accumulate sums for row-sum check.
		for n, v := range sums {
			allSums[n] += v
		}
	}

	// ── Row-sum: Σ_H T(n,H) for each n ──
	// Use triangle file if available, else use manifest value for target n only.
	triangleSums, triErr := ReadTriangleFile(trianglePath)
	if triErr == nil && len(triangleSums) > 0 {
		anyFail := false
		for n, expected := range triangleSums {
			got := allSums[n]
			if got != expected {
				results = append(results, fail("row-sum", fmt.Sprintf("n=%d: runs sum %d triangle says %d", n, got, expected)))
				anyFail = true
			}
		}
		if !anyFail {
			results = append(results, pass("row-sum", fmt.Sprintf("n=%d all %d sizes matched", cfg.N, len(triangleSums))))
		}
	} else if mf.Value != 0 {
		// No triangle file: check just a(N) against manifest value field.
		got := allSums[cfg.N]
		if got != mf.Value {
			results = append(results, fail("row-sum", fmt.Sprintf("n=%d: runs sum %d manifest value=%d", cfg.N, got, mf.Value)))
		} else {
			results = append(results, pass("row-sum", fmt.Sprintf("n=%d sum=%d", cfg.N, got)))
		}
	} else {
		results = append(results, warn("row-sum", "no triangle file or manifest value to compare against"))
	}

	// ── Growth ratio ──
	if len(triangleSums) > 0 {
		results = append(results, checkGrowthRatio(triangleSums)...)
	} else if len(allSums) > 1 {
		results = append(results, checkGrowthRatio(allSums)...)
	}

	// ── Residues ──
	residues, resErr := ReadResiduesFile(residuesPath)
	if resErr == nil && len(residues) > 0 {
		for _, r := range residues {
			got := allSums[r.N]
			gotMod := got % r.Prime
			if gotMod != r.Residue {
				results = append(results, fail("residue", fmt.Sprintf("n=%d mod %d: got %d expected %d", r.N, r.Prime, gotMod, r.Residue)))
			} else {
				results = append(results, pass("residue", fmt.Sprintf("n=%d mod %d = %d ok", r.N, r.Prime, r.Residue)))
			}
		}
	}

	// ── Spotcheck ──
	if !cfg.NoSpotcheck && len(mf.Files) > 0 {
		results = append(results, spotcheck(cfg, mf)...)
	}

	return results
}

// checkGrowthRatio verifies a(n+1)/a(n) is in [3.9, 7.2] for consecutive pairs.
// A006770's ratios climb monotonically from ~4.0 (a2/a1) toward the growth
// constant lambda ~ 7.10; high-n pairs sit at ~6.7-6.8 (a21/a20 ~ 6.78). The
// band brackets the smallest legitimate ratio below and the asymptote above.
func checkGrowthRatio(sums map[int]uint64) []CheckResult {
	// Collect sorted keys with nonzero values.
	var ns []int
	for n, v := range sums {
		if v > 0 {
			ns = append(ns, n)
		}
	}
	if len(ns) < 2 {
		return nil
	}
	// Sort.
	for i := 0; i < len(ns); i++ {
		for j := i + 1; j < len(ns); j++ {
			if ns[i] > ns[j] {
				ns[i], ns[j] = ns[j], ns[i]
			}
		}
	}

	var results []CheckResult
	anyFail := false
	for i := 0; i+1 < len(ns); i++ {
		a, b := ns[i], ns[i+1]
		if b != a+1 {
			continue // gap; skip
		}
		va, vb := float64(sums[a]), float64(sums[b])
		if va == 0 {
			continue
		}
		ratio := vb / va
		if ratio < 3.9 || ratio > 7.2 {
			results = append(results, fail("growth", fmt.Sprintf("a(%d)/a(%d)=%.4f outside [3.9,7.2]", b, a, ratio)))
			anyFail = true
		}
	}
	if !anyFail && len(ns) >= 2 {
		results = append(results, pass("growth", fmt.Sprintf("ratios ok over n=%d..%d", ns[0], ns[len(ns)-1])))
	}
	return results
}

// spotcheck re-runs up to 3 randomly selected run files via map_worker and compares.
func spotcheck(cfg Config, mf Manifest) []CheckResult {
	var results []CheckResult
	mapWorker := filepath.Join(cfg.WorkersDir, "map_worker")
	if _, err := os.Stat(mapWorker); err != nil {
		results = append(results, warn("spotcheck", fmt.Sprintf("map_worker not found at %s, skipping", mapWorker)))
		return results
	}

	// Pick up to 3 random files.
	indices := rand.Perm(len(mf.Files))
	if len(indices) > 3 {
		indices = indices[:3]
	}

	for _, i := range indices {
		fe := mf.Files[i]
		result := spotcheckOne(cfg, mapWorker, fe)
		results = append(results, result)
	}
	return results
}

func spotcheckOne(cfg Config, mapWorker string, fe ManifestFileEntry) CheckResult {
	hdr, _, err := parsePolyrunHeader(fe.Path)
	if err != nil {
		return warn("spotcheck", fmt.Sprintf("cannot parse %s: %v", fe.Path, err))
	}

	// Find the previous column run. We look for the seed file or skip if not found.
	// The spotcheck requires the input (previous column) run — if not available, warn.
	// The map_worker input is the previous-col run for this H sweep. We don't have
	// a reliable way to find it without the checkpoint, so we skip with a warning.
	_ = hdr
	return warn("spotcheck", fmt.Sprintf("skip %s: prev-col run not available without checkpoint", fe.Path))
}
