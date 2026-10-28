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
	"math/big"
	"os"
	"path/filepath"
	"sort"
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
	Height      int
	Maxn        int
	Records     uint64
	Counter     string // "u64" or "u128"
	KeyLo       string
	KeyHi       string
	Rev         string
	Compression int // 0 plain, 1 single zstd frame, 2 block-framed zstd
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
		var perr error
		switch k {
		case "height":
			hdr.Height, perr = strconv.Atoi(v)
		case "maxn":
			hdr.Maxn, perr = strconv.Atoi(v)
		case "records":
			hdr.Records, perr = strconv.ParseUint(strings.TrimSpace(v), 10, 64)
		case "counter":
			hdr.Counter = strings.TrimSpace(v)
		case "keylo":
			hdr.KeyLo = v
		case "keyhi":
			hdr.KeyHi = v
		case "rev":
			hdr.Rev = v
		case "compression":
			hdr.Compression, perr = strconv.Atoi(strings.TrimSpace(v))
		}
		if perr != nil {
			return PolyrunHeader{}, 0, fmt.Errorf("%s: header line %q: %w", path, line, perr)
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
	Value      *big.Int // nil when the manifest has no value line
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
				var perr error
				switch k {
				case "path":
					entry.Path = v
				case "records":
					entry.Records, perr = strconv.ParseUint(v, 10, 64)
				case "crc":
					entry.CRC, perr = strconv.ParseUint(v, 16, 64)
				}
				if perr != nil {
					return Manifest{}, fmt.Errorf("%s: file line %q: %w", path, line, perr)
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
			var perr error
			if m.N, perr = strconv.Atoi(v); perr != nil {
				return Manifest{}, fmt.Errorf("%s: line %q: %w", path, line, perr)
			}
		case "value":
			val, ok := new(big.Int).SetString(strings.TrimSpace(v), 10)
			if !ok {
				return Manifest{}, fmt.Errorf("%s: unparseable value %q", path, v)
			}
			m.Value = val
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
// across all records, plus the actual record count. Counts and sums are
// big.Int, so u128 runs and sums past 2^64 are read exactly.
func SumCountsInFile(path string) (map[int]*big.Int, uint64, error) {
	hdr, bodyOff, err := parsePolyrunHeader(path)
	if err != nil {
		return nil, 0, err
	}
	// FAIL-CLOSED: a compressed body's bytes are not records — decoding them
	// as varints yields garbage sums with no signal. This independent verifier
	// deliberately has no zstd path; say so instead of misreading, and say what
	// DOES cover such a file (runcat is Go too, and there is no C++ dumper —
	// the old "use the C++ readers (runcat)" referral was circular).
	if hdr.Compression != 0 {
		return nil, 0, fmt.Errorf("%s: compressed body (compression %d): this Go verifier decodes plain bodies only. Integrity of a compressed body rests on the in-band zstd frame checksum, which the C++ readers (core/runfile.h) enforce fail-closed — any decode or checksum failure aborts the reading worker rather than reading short. To check or dump one by hand: tail -c +%d %s | zstd -d", path, hdr.Compression, bodyOff+1, path)
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
	sums := make(map[int]*big.Int)
	var recCount uint64

	br := bufio.NewReader(f)
	sig := make([]byte, keyLen)
	meta := make([]byte, 2)
	// Read exactly hdr.Records records; the 8-byte CRC trailer follows immediately
	// after. Counts are LEB128 varints (core/run.h encodeVarint).
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
			val, err := readBigUvarint(br)
			if err != nil {
				return nil, recCount, fmt.Errorf("reading counts in %s: %w", path, err)
			}
			if sums[lo+i] == nil {
				sums[lo+i] = new(big.Int)
			}
			sums[lo+i].Add(sums[lo+i], val)
		}
		recCount++
	}
	return sums, recCount, nil
}

// readBigUvarint decodes one LEB128 unsigned varint of any width. More than
// 19 bytes (past u128) is corruption, not a count.
func readBigUvarint(br io.ByteReader) (*big.Int, error) {
	v := new(big.Int)
	var shift uint
	for i := 0; i < 19; i++ {
		b, err := br.ReadByte()
		if err != nil {
			return nil, err
		}
		v.Or(v, new(big.Int).Lsh(big.NewInt(int64(b&0x7f)), shift))
		if b < 0x80 {
			return v, nil
		}
		shift += 7
	}
	return nil, fmt.Errorf("varint longer than 19 bytes")
}

// ─── Triangle file ────────────────────────────────────────────────────────────

// ReadTriangleFile reads data/triangle/a<N>.txt and returns a map[n]→value.
// Lines have format: "tri <H> <n> <value>" — values are summed over all H. A
// tri line that does not parse is an error: skipping it would drop its n from
// the row-sum check, which would then pass unchecked.
func ReadTriangleFile(path string) (map[int]*big.Int, error) {
	f, err := os.Open(path)
	if err != nil {
		return nil, err
	}
	defer f.Close()

	sums := make(map[int]*big.Int)
	sc := bufio.NewScanner(f)
	for sc.Scan() {
		line := sc.Text()
		if strings.HasPrefix(line, "#") || line == "" {
			continue
		}
		parts := strings.Fields(line)
		if len(parts) == 0 || parts[0] != "tri" {
			continue
		}
		if len(parts) != 4 {
			return nil, fmt.Errorf("%s: malformed tri line %q", path, line)
		}
		n, err1 := strconv.Atoi(parts[2])
		v, ok := new(big.Int).SetString(parts[3], 10)
		if err1 != nil || !ok {
			return nil, fmt.Errorf("%s: malformed tri line %q", path, line)
		}
		if sums[n] == nil {
			sums[n] = new(big.Int)
		}
		sums[n].Add(sums[n], v)
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
		res, ok := parseResidue(line)
		if !ok {
			return nil, fmt.Errorf("%s: malformed residue line %q", path, line)
		}
		out = append(out, res)
	}
	return out, sc.Err()
}

// parseResidue parses one "n prime residue" line.
func parseResidue(line string) (Residue, bool) {
	parts := strings.Fields(line)
	if len(parts) != 3 {
		return Residue{}, false
	}
	n, e1 := strconv.Atoi(parts[0])
	p, e2 := strconv.ParseUint(parts[1], 10, 64)
	r, e3 := strconv.ParseUint(parts[2], 10, 64)
	if e1 != nil || e2 != nil || e3 != nil || p < 2 {
		return Residue{}, false
	}
	return Residue{N: n, Prime: p, Residue: r}, true
}

// ─── Result ───────────────────────────────────────────────────────────────────

// CheckResult holds one verification result.
type CheckResult struct {
	Pass   bool
	Check  string // short tag, e.g. "crc", "row-sum", "growth"
	Detail string // human-readable detail
	IsWarn bool   // WARN rather than FAIL
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
	N       int
	DataDir string
	Verbose bool
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
	allSums := make(map[int]*big.Int) // n → sum across all heights
	for _, fe := range mf.Files {
		hdr, bodyOff, err := parsePolyrunHeader(fe.Path)
		if err != nil {
			results = append(results, fail("crc", fmt.Sprintf("cannot parse header %s: %v", fe.Path, err)))
			continue
		}

		// CRC check. Compressed bodies carry zstd frame checksums instead of
		// the FNV trailer — this verifier cannot check them; fail explicitly
		// rather than compare FNV-of-zstd-bytes against frame-tail bytes. The
		// zstd checksum is not weaker, just in-band: the C++ readers validate
		// it on every frame and abort on failure (core/runfile.h). What is
		// missing here is an INDEPENDENT check, so the failure stands.
		if hdr.Compression != 0 {
			results = append(results, fail("crc", fmt.Sprintf("%s: compressed body (compression %d): no FNV trailer for this Go verifier to check independently; its integrity check is the in-band zstd frame checksum, enforced fail-closed by the C++ readers. Hand check: tail -c +%d %s | zstd -d", fe.Path, hdr.Compression, bodyOff+1, fe.Path)))
			continue
		}
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
			if allSums[n] == nil {
				allSums[n] = new(big.Int)
			}
			allSums[n].Add(allSums[n], v)
		}
	}

	// ── Row-sum: Σ_H T(n,H) for each n ──
	// Use triangle file if available, else use manifest value for target n only.
	triangleSums, triErr := ReadTriangleFile(trianglePath)
	if triErr != nil && !os.IsNotExist(triErr) {
		results = append(results, fail("row-sum", triErr.Error()))
	} else if len(triangleSums) > 0 {
		anyFail := false
		for n, expected := range triangleSums {
			got := bigOrZero(allSums[n])
			if got.Cmp(expected) != 0 {
				results = append(results, fail("row-sum", fmt.Sprintf("n=%d: runs sum %d triangle says %d", n, got, expected)))
				anyFail = true
			}
		}
		if !anyFail {
			results = append(results, pass("row-sum", fmt.Sprintf("n=%d all %d sizes matched", cfg.N, len(triangleSums))))
		}
	} else if mf.Value != nil {
		// No triangle file: check just a(N) against manifest value field.
		got := bigOrZero(allSums[cfg.N])
		if got.Cmp(mf.Value) != 0 {
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
	if resErr != nil && !os.IsNotExist(resErr) {
		results = append(results, fail("residue", resErr.Error()))
	} else if len(residues) > 0 {
		for _, r := range residues {
			gotMod := new(big.Int).Mod(bigOrZero(allSums[r.N]), new(big.Int).SetUint64(r.Prime)).Uint64()
			if gotMod != r.Residue {
				results = append(results, fail("residue", fmt.Sprintf("n=%d mod %d: got %d expected %d", r.N, r.Prime, gotMod, r.Residue)))
			} else {
				results = append(results, pass("residue", fmt.Sprintf("n=%d mod %d = %d ok", r.N, r.Prime, r.Residue)))
			}
		}
	}

	return results
}

// checkGrowthRatio verifies a(n+1)/a(n) is in [3.9, 7.2] for consecutive pairs.
// A006770's ratios climb monotonically from ~4.0 (a2/a1) toward the growth
// constant lambda ~ 7.10; high-n pairs sit at ~6.7-6.8 (a21/a20 ~ 6.78). The
// band brackets the smallest legitimate ratio below and the asymptote above.
func checkGrowthRatio(sums map[int]*big.Int) []CheckResult {
	// Collect sorted keys with nonzero values.
	var ns []int
	for n, v := range sums {
		if v != nil && v.Sign() > 0 {
			ns = append(ns, n)
		}
	}
	if len(ns) < 2 {
		return nil
	}
	sort.Ints(ns)

	var results []CheckResult
	anyFail := false
	for i := 0; i+1 < len(ns); i++ {
		a, b := ns[i], ns[i+1]
		if b != a+1 {
			continue // gap; skip
		}
		ratio, _ := new(big.Float).Quo(new(big.Float).SetInt(sums[b]), new(big.Float).SetInt(sums[a])).Float64()
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

// bigOrZero returns v, or zero when v is nil (an n no file contributed to).
func bigOrZero(v *big.Int) *big.Int {
	if v == nil {
		return new(big.Int)
	}
	return v
}
