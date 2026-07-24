// runref.go — RunRef handle, POLYRUN header parsing, key sampling, CRC verification.
package orchestrator

import (
	"bufio"
	"encoding/binary"
	"fmt"
	"io"
	"os"
	"sort"
	"strconv"
	"strings"
)

// RunRef is a handle to a completed sorted POLYRUN file on disk.
type RunRef struct {
	Path    string
	Records uint64
}

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

// WordBytes returns the byte width of one count value (8 for u64, 16 for u128).
func (h PolyrunHeader) WordBytes() int {
	if h.Counter == "u128" {
		return 16
	}
	return 8
}

// columnKeyLen returns the whole-column kernel's end-of-column sig key width
// (boundary + touch-top + touch-bottom) for height H. kinkKeyLen returns the
// kink kernel's mixed-state stage key width (boundary + touch flags + carry
// byte + placed-any flag), mirroring core/kink.h's kinkKeyLen.
func columnKeyLen(H int) int { return H + 2 }
func kinkKeyLen(H int) int   { return H + 4 }

// ParseHeader reads a POLYRUN header and returns it with the byte offset
// where the binary body begins.
func ParseHeader(path string) (PolyrunHeader, int64, error) {
	f, err := os.Open(path)
	if err != nil {
		return PolyrunHeader{}, 0, err
	}
	defer f.Close()

	// Small explicit buffer, not bufio.NewReader's 4KB default: the text
	// header is a handful of short "key value" lines (height/maxn/records/
	// counter/keylo/keyhi/rev), a few hundred bytes at most, but ParseHeader
	// is called once per SampleKeys call -- i.e. once per file per map/merge
	// round -- so the oversized default buffer showed up as the largest
	// remaining allocator in a real heap profile after fixing the two
	// wasted-reader call sites above (docs/utilization-bottleneck-log.md
	// Bottleneck #4).
	br := bufio.NewReaderSize(f, 256)
	var hdr PolyrunHeader
	var offset int64

	for {
		line, err := br.ReadString('\n')
		offset += int64(len(line))
		line = strings.TrimRight(line, "\r\n")
		if line == "" {
			break
		}
		if err != nil {
			break
		}
		k, v, ok := strings.Cut(line, " ")
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
		case "compression":
			hdr.Compression, _ = strconv.Atoi(strings.TrimSpace(v))
		}
	}
	return hdr, offset, nil
}

// SampleKeys samples up to numCuts evenly-spaced sig keys from a POLYRUN file
// for input-space partitioning.  Returns hex-encoded keys; len <= numCuts.
// Caller converts into unit boundaries: unit i covers [cuts[i-1], cuts[i]).
//
// keyLen is the run's key width in bytes (H+2 for the column kernel's
// end-of-column sigs, H+4 for the kink kernel's mixed-state stage keys) —
// callers must pass it explicitly, it is not derived from H.
//
// Fast path: the .idx sidecar already holds one key per 64 records (evenly
// spaced) — sample from it and never touch the multi-GB body.  Falls back to a
// buffered body scan only when no usable .idx is present.
func SampleKeys(path string, H, keyLen, numCuts int) ([]string, error) {
	if numCuts <= 0 {
		return nil, nil
	}
	hdr, bodyOff, err := ParseHeader(path)
	if err != nil {
		return nil, err
	}
	if hdr.Records == 0 || hdr.Height != H {
		return nil, nil
	}
	cuts, idxErr := sampleIndexKeys(path+".idx", keyLen, numCuts)
	if idxErr == nil && len(cuts) > 0 {
		return cuts, nil
	}
	// Compressed bodies cannot be body-scanned: zstd bytes read as records
	// would silently mis-partition the round. Two distinct cases here:
	//  - idx parsed fine but yielded nothing interior (any run under one
	//    index stride — kink stage merges produce these constantly): that IS
	//    the answer, return it without error;
	//  - idx missing/corrupt: FAIL-CLOSED — compressed frontier files always
	//    publish an .idx (RunFileWriter writes one for every indexed file
	//    with records), so this means the sidecar is gone, not the run tiny.
	if hdr.Compression != 0 {
		if idxErr == nil {
			return cuts, nil
		}
		return nil, fmt.Errorf("SampleKeys %s: compressed body (compression %d) with no usable .idx (%v) — cannot body-scan", path, hdr.Compression, idxErr)
	}
	return sampleBodyKeys(path, bodyOff, keyLen, int(hdr.Records), numCuts)
}

// sampleIndexKeys returns up to numCuts evenly-spaced interior keys from the
// .idx sidecar, reading no run body.  The first index entry (record 0) is
// dropped so a cut never equals the run's minimum key (empty first piece).
func sampleIndexKeys(idxPath string, keyLen, numCuts int) ([]string, error) {
	f, err := os.Open(idxPath)
	if err != nil {
		return nil, err
	}
	defer f.Close()
	cnt, err := readIndexHeader(f, keyLen)
	if err != nil {
		return nil, err
	}
	if cnt <= 1 {
		return nil, nil // only the record-0 entry → nothing interior to cut on
	}
	// SEEK to ~numCuts evenly-spaced interior entries — O(numCuts) reads, never the
	// whole index (entries are fixed width, so position i is a direct offset).
	// Entry 0 (the run minimum) is skipped: j starts at 1.
	entryLen := int64(keyLen + 16)
	key := make([]byte, keyLen)
	stride := cnt / uint64(numCuts+1)
	if stride < 1 {
		stride = 1
	}
	var keys []string
	for j := 1; j <= numCuts; j++ {
		i := uint64(j) * stride
		if i >= cnt {
			i = cnt - 1
		}
		off := int64(idxHeaderBytes) + int64(i)*entryLen
		if _, err := f.ReadAt(key, off); err != nil {
			break
		}
		if h := bytesToHex(key); len(keys) == 0 || keys[len(keys)-1] != h {
			keys = append(keys, h) // dedup adjacent (strides can clamp to cnt-1)
		}
	}
	return keys, nil
}

// discardVarint consumes one LEB128 unsigned varint from br without
// reconstructing its value. It is width-agnostic on purpose: unlike
// binary.ReadUvarint (which errors on a value exceeding u64), it correctly skips
// u128 counts at a26+ magnitudes -- we only need to advance past the record.
func discardVarint(br io.ByteReader) error {
	for {
		b, err := br.ReadByte()
		if err != nil {
			return err
		}
		if b < 0x80 {
			return nil
		}
	}
}

// sampleBodyKeys is the fallback when the .idx is absent/unreadable: a buffered
// streaming scan of the run body. Record layout is keyLen + 2 meta bytes
// (lo, length) + `length` LEB128 varint counts (core/run.h encodeVarint) -- the
// counts are variable-width, so each is skipped by discardVarint, NOT by a fixed
// length*wordBytes (the pre-varint layout, which desynced after the first record
// and sampled garbage keys).
func sampleBodyKeys(path string, bodyOff int64, keyLen, records, numCuts int) ([]string, error) {
	f, err := os.Open(path)
	if err != nil {
		return nil, err
	}
	defer f.Close()
	if _, err := f.Seek(bodyOff, io.SeekStart); err != nil {
		return nil, err
	}
	br := bufio.NewReader(f)
	stride := records / (numCuts + 1)
	if stride < 1 {
		stride = 1
	}
	sig := make([]byte, keyLen)
	meta := make([]byte, 2)
	var cuts []string
	idx := 0
	for {
		if _, err := io.ReadFull(br, sig); err != nil {
			break
		}
		if _, err := io.ReadFull(br, meta); err != nil {
			break
		}
		length := int(meta[1])
		bad := false
		for i := 0; i < length; i++ {
			if err := discardVarint(br); err != nil {
				bad = true
				break
			}
		}
		if bad {
			break
		}
		idx++
		if idx%stride == 0 && len(cuts) < numCuts {
			cuts = append(cuts, bytesToHex(sig))
		}
	}
	return cuts, nil
}

// subsampleEvenly returns up to numCuts evenly-spaced interior elements of keys.
func subsampleEvenly(keys []string, numCuts int) []string {
	if len(keys) <= numCuts {
		return keys
	}
	out := make([]string, numCuts)
	stride := len(keys) / (numCuts + 1)
	if stride < 1 {
		stride = 1
	}
	for i := range out {
		idx := (i + 1) * stride
		if idx >= len(keys) {
			idx = len(keys) - 1
		}
		out[i] = keys[idx]
	}
	return out
}

// BalancedCutsMulti returns TRUE global record-quantile cut keys across
// multiple POLYRUN files. It replaced an earlier per-file sampler that drew a
// fixed number of samples FROM EACH FILE, so a file holding 590M records
// contributed the same number of samples as one holding 64K -- the big file
// was under-sampled and its records collapsed into one open-ended bucket (the
// measured straggler, docs/full-utilization-redesign.md).
//
// Each .idx sidecar holds exactly one entry per 64 records (core/runfile.h
// kIndexStride), uniformly spaced. The union of ALL files' FULL index
// entries is therefore a uniform 1-per-64 sample of ALL records regardless
// of key-range overlap: reading that full union, sorting it, and taking
// evenly-spaced quantiles gives cuts on true record rank, not per-file rank.
// A key that appears in several files' indexes is simply represented in
// proportion to how many records carry it -- correct for record-balanced
// cuts (a hot key gets finer cuts around it) -- so, unlike SampleKeysMulti,
// this does NOT dedup across files.
//
// keyLen: see SampleKeys. H is intentionally omitted: the index format is
// self-describing (readIndexHeader validates keyLen from the sidecar) and
// never needs the caller's H on the fast path. numCuts<=0 returns (nil, nil).
func BalancedCutsMulti(paths []string, keyLen, numCuts int) ([]string, error) {
	if numCuts <= 0 {
		return nil, nil
	}
	var all []string
	for _, p := range paths {
		keys, err := allIndexKeys(p+".idx", keyLen)
		if err == nil && len(keys) > 0 {
			all = append(all, keys...)
			continue
		}
		// No usable .idx: fall back to SampleKeys's own body-scan path so a
		// missing/unreadable sidecar degrades to today's behaviour instead of
		// silently dropping the file's records from the quantile. Rare in
		// practice -- production runs always write_index=true. H is read from
		// the file's own header (self-consistent) rather than threaded through
		// this function's signature.
		hdr, _, herr := ParseHeader(p)
		if herr != nil {
			continue // unreadable file: contributes nothing, same tolerance as SplitRangeByIndex
		}
		fb, ferr := SampleKeys(p, hdr.Height, keyLen, numCuts)
		if ferr != nil {
			return nil, ferr
		}
		all = append(all, fb...)
	}
	if len(all) == 0 {
		return nil, nil
	}
	sort.Strings(all)
	return subsampleEvenly(all, numCuts), nil
}

// allIndexKeys reads the FULL union of a .idx sidecar's entries (not a
// sparse sample of it -- that is the whole fix), dropping entry 0 (the run
// minimum) so a cut never equals a run's first key, mirroring
// sampleIndexKeys' "skip entry 0". Reads the entry block in one bulk
// io.ReadFull, not one ReadAt per entry -- this is a hot path, called once
// per file per map/merge round.
func allIndexKeys(idxPath string, keyLen int) ([]string, error) {
	f, err := os.Open(idxPath)
	if err != nil {
		return nil, err
	}
	defer f.Close()
	cnt, err := readIndexHeader(f, keyLen)
	if err != nil {
		return nil, err
	}
	if cnt <= 1 {
		return nil, nil // only the record-0 entry → nothing interior to cut on
	}
	entryLen := keyLen + 16
	n := int(cnt - 1) // drop entry 0
	// Entry 0 lives at idxHeaderBytes; entries [1, cnt) follow contiguously.
	if _, err := f.Seek(int64(idxHeaderBytes)+int64(entryLen), io.SeekStart); err != nil {
		return nil, err
	}
	buf := make([]byte, n*entryLen)
	if _, err := io.ReadFull(f, buf); err != nil {
		return nil, err
	}
	keys := make([]string, 0, n)
	for off := 0; off < len(buf); off += entryLen {
		keys = append(keys, bytesToHex(buf[off:off+keyLen]))
	}
	return keys, nil
}

// SplitRangeByIndex picks numCuts keys that divide (loHex, hiHex) into
// numCuts+1 roughly record-equal sub-ranges, for splitting a work-stealing
// straggler's remaining range across idle cores.  It reads only the sparse
// .idx sidecars (one entry per 64 records), never the run bodies, so it is
// cheap even on a multi-GB frontier — steals happen in the column tail, and
// re-reading the frontier per steal would defeat the purpose.
//
// Cuts are strictly inside (lo, hi) and ascending, so every sub-range is
// non-empty.  Returns fewer than numCuts (possibly zero) when the indexes hold
// too few in-range samples to cut finely — the caller then steals less (or not
// at all), which is the correct degenerate behaviour.
// keyLen: see SampleKeys.
func SplitRangeByIndex(frontier []string, H, keyLen int, loHex, hiHex string, numCuts int) ([]string, error) {
	if numCuts <= 0 {
		return nil, nil
	}
	loB, hasLo := hexBytes(loHex, keyLen)
	hiB, hasHi := hexBytes(hiHex, keyLen)

	// Gather in-range index keys across all frontier files. Frontier (merge
	// output) files are disjoint key ranges, so a simple sorted union of their
	// in-range index keys is record-balanced (uniform 1-per-64 stride per file).
	var keys []string
	seen := make(map[string]bool)
	for _, p := range frontier {
		ks, err := indexKeysInRange(p+".idx", keyLen, loB, hasLo, hiB, hasHi, numCuts)
		if err != nil {
			continue // missing/short index → just contributes no cut candidates
		}
		for _, k := range ks {
			if !seen[k] {
				seen[k] = true
				keys = append(keys, k)
			}
		}
	}
	if len(keys) == 0 {
		return nil, nil
	}
	sort.Strings(keys)

	return subsampleEvenly(keys, numCuts), nil
}

// indexKeysInRange reads a .idx sidecar and returns the hex keys that fall in
// (lo, hi) — strictly greater than lo (a cut equal to lo would leave an empty
// first piece) and, if hi is set, strictly less than hi.
// Sidecar format MUST match core/runfile.h writeIndexSidecar:
//   magic(u32 'PLYI') ver(u16) bo(u8) keyLen(u32) count(u64), little-endian,
//   then count × { key[keyLen] u64 offset u64 recidx }.
const (
	idxMagic       = 0x49594C50 // 'PLYI', little-endian
	idxVersion     = 1
	idxByteOrderLE = 1
	idxHeaderBytes = 19 // magic4 + ver2 + bo1 + keyLen4 + count8 (packed, no padding)
)

// readIndexHeader reads + validates the .idx self-describing header (the single
// place that knows the on-disk layout) and returns the entry count. Takes a
// plain io.Reader (an *os.File works directly, no buffering) and reads the
// fixed idxHeaderBytes in one call: this is a hot path (called once per
// SampleKeysMulti/indexKeysInRange invocation -- every map/merge round of
// every column of every height), and the two callers that read only this
// header before switching to positioned f.ReadAt calls were each allocating
// a full bufio.Reader (4KB default buffer) just to decode 19 bytes, then
// discarding it -- confirmed via a real heap-alloc profile as ~35% of a real
// run's total allocation (docs/utilization-bottleneck-log.md Bottleneck #4).
func readIndexHeader(r io.Reader, wantKeyLen int) (uint64, error) {
	var hdr [idxHeaderBytes]byte
	if _, err := io.ReadFull(r, hdr[:]); err != nil {
		return 0, err
	}
	magic := binary.LittleEndian.Uint32(hdr[0:4])
	ver := binary.LittleEndian.Uint16(hdr[4:6])
	bo := hdr[6]
	if magic != idxMagic || ver != idxVersion || bo != idxByteOrderLE {
		return 0, fmt.Errorf("idx bad header: magic=%#x ver=%d bo=%d", magic, ver, bo)
	}
	kl := binary.LittleEndian.Uint32(hdr[7:11])
	cnt := binary.LittleEndian.Uint64(hdr[11:19])
	if int(kl) != wantKeyLen {
		return 0, fmt.Errorf("idx keyLen %d != %d", kl, wantKeyLen)
	}
	return cnt, nil
}

// indexKeysInRange returns up to maxKeys evenly-spaced .idx keys strictly inside
// (lo, hi). Entries are ascending by key, so it BINARY-SEARCHES the in-range span
// and SEEKS to ~maxKeys strided entries — O(log cnt + maxKeys) reads, never the
// whole index (the Steal Sort fix). maxKeys<=0 means unbounded.
func indexKeysInRange(idxPath string, keyLen int, lo []byte, hasLo bool, hi []byte, hasHi bool, maxKeys int) ([]string, error) {
	f, err := os.Open(idxPath)
	if err != nil {
		return nil, err
	}
	defer f.Close()
	cnt, err := readIndexHeader(f, keyLen)
	if err != nil {
		return nil, err
	}
	if cnt == 0 {
		return nil, nil
	}
	entryLen := int64(keyLen + 16)
	buf := make([]byte, keyLen)
	at := func(i uint64) ([]byte, bool) {
		if _, err := f.ReadAt(buf, int64(idxHeaderBytes)+int64(i)*entryLen); err != nil {
			return nil, false
		}
		return buf, true
	}
	// [loIdx, hiIdx) = entries with key > lo and key < hi (entries ascending).
	loIdx := uint64(0)
	if hasLo {
		loIdx = uint64(sort.Search(int(cnt), func(i int) bool {
			k, ok := at(uint64(i))
			return ok && bytesCompare(k, lo) > 0
		}))
	}
	hiIdx := cnt
	if hasHi {
		hiIdx = uint64(sort.Search(int(cnt), func(i int) bool {
			k, ok := at(uint64(i))
			return ok && bytesCompare(k, hi) >= 0
		}))
	}
	if loIdx >= hiIdx {
		return nil, nil
	}
	stride := uint64(1)
	if span := hiIdx - loIdx; maxKeys > 0 && span > uint64(maxKeys) {
		stride = span / uint64(maxKeys)
	}
	var keys []string
	for i := loIdx; i < hiIdx; i += stride {
		k, ok := at(i)
		if !ok {
			break
		}
		if h := bytesToHex(k); len(keys) == 0 || keys[len(keys)-1] != h {
			keys = append(keys, h)
		}
		if maxKeys > 0 && len(keys) >= maxKeys {
			break
		}
	}
	return keys, nil
}

// hexBytes decodes a hex key to keyLen bytes; ok=false for an empty/short hex
// (an open range end).
func hexBytes(hexStr string, keyLen int) ([]byte, bool) {
	if len(hexStr) != keyLen*2 {
		return nil, false
	}
	b := make([]byte, keyLen)
	for i := 0; i < keyLen; i++ {
		var hi, lo byte
		if !hexNibble(hexStr[i*2], &hi) || !hexNibble(hexStr[i*2+1], &lo) {
			return nil, false
		}
		b[i] = hi<<4 | lo
	}
	return b, true
}

func hexNibble(c byte, out *byte) bool {
	switch {
	case c >= '0' && c <= '9':
		*out = c - '0'
	case c >= 'a' && c <= 'f':
		*out = c - 'a' + 10
	case c >= 'A' && c <= 'F':
		*out = c - 'A' + 10
	default:
		return false
	}
	return true
}

func bytesCompare(a, b []byte) int {
	for i := 0; i < len(a) && i < len(b); i++ {
		if a[i] != b[i] {
			if a[i] < b[i] {
				return -1
			}
			return 1
		}
	}
	return len(a) - len(b)
}

const fnvOffset uint64 = 14695981039346656037
const fnvPrime uint64 = 1099511628211

// Fnv1a64 computes the FNV-1a-64 hash used for POLYRUN body CRCs. Exported
// so cmd/runcat can share this instead of carrying its own copy (simplify
// pass: the two were byte-for-byte identical).
func Fnv1a64(data []byte) uint64 {
	h := fnvOffset
	for _, b := range data {
		h ^= uint64(b)
		h *= fnvPrime
	}
	return h
}

func bytesToHex(b []byte) string {
	const hexChars = "0123456789abcdef"
	s := make([]byte, len(b)*2)
	for i, v := range b {
		s[i*2] = hexChars[v>>4]
		s[i*2+1] = hexChars[v&0xf]
	}
	return string(s)
}

// u64ExactMaxN and u128ExactMaxN are the largest maxn each counter word can
// hold exactly (per DESIGN/counter.h); beyond that the count wraps silently
// (only detectable post-hoc via the mod-p shadow). Shared by CheckCounterWidth
// and resultPipelineMaxN (via u128ExactMaxN) so the two guards can't drift
// apart the way the two independently-hardcoded diagonal dispatch guards
// once did (see diagonalStripValid).
const (
	u64ExactMaxN  = 25
	u128ExactMaxN = 48
)

// CheckCounterWidth refuses at start (FR-7) if the configured counter word
// cannot hold a(maxn), so the orchestrator refuses before spawning workers
// rather than run for hours and produce a wrong number.
func CheckCounterWidth(counter string, maxn int) error {
	var limit int
	switch counter {
	case "", "u64":
		counter, limit = "u64", u64ExactMaxN
	case "u128":
		limit = u128ExactMaxN
	default:
		return fmt.Errorf("CheckCounterWidth: unknown counter %q (want u64 or u128)", counter)
	}
	if maxn > limit {
		return fmt.Errorf("counter %s holds exact counts only to a(%d), but maxn=%d; use a wider --counter", counter, limit, maxn)
	}
	return nil
}

// ramThrashFloor is the --ram below which map_worker spills constantly even on a
// modest real sweep. The 128 MB default is fine for the small gates but thrashes
// a real run; every launch script overrides it, so a naive direct caller gets a
// warning rather than a silently slow run.
const ramThrashFloor = 1 << 30 // 1 GiB

// RAMAdvisory returns a non-empty warning if --ram is small enough to force
// spill-thrash, else "".
func RAMAdvisory(ram uint64) string {
	if ram < ramThrashFloor {
		return fmt.Sprintf("warning: --ram %d is below %d (1 GiB) and will spill-thrash a real sweep; pass a realistic --ram (several GiB)", ram, ramThrashFloor)
	}
	return ""
}

// resultPipelineMaxN is the largest maxn the Go result pipeline can hold
// exactly. BUGS-OF-SHAME A2 widened accounting/triangle/checkpoint/known/
// combine from uint64 to big.Int, so the Go side itself is now unbounded; the
// real remaining ceiling is the widest counter available (u128, exact to
// u128ExactMaxN), not a Go-side type limit.
const resultPipelineMaxN = u128ExactMaxN

// CheckResultWidth refuses at start if maxn exceeds what the Go result
// pipeline can represent under the CONFIGURED counter width. Post-A2 this
// mirrors CheckCounterWidth's cap rather than an independent Go-side limit —
// kept as a belt-and-suspenders check since CheckResultWidth doesn't take
// --counter, so it can only enforce the widest (u128) ceiling; a u64 run past
// a(25) is still caught by CheckCounterWidth.
func CheckResultWidth(maxn int) error {
	if maxn > resultPipelineMaxN {
		return fmt.Errorf("maxn=%d exceeds a(%d), the widest counter's (u128) exact range", maxn, resultPipelineMaxN)
	}
	return nil
}

// WriteSeedPolyrun writes a seed POLYRUN file for height H (col 0: empty boundary,
// counts[0]=1).  counter is "u64" or "u128" (empty = "u64").
// The record count is known upfront so no fseek is needed.
func WriteSeedPolyrun(path, rev string, H, maxn int, counter ...string) error {
	counterTag := "u64"
	if len(counter) > 0 && counter[0] != "" {
		switch counter[0] {
		case "u64", "u128":
			counterTag = counter[0]
		default:
			// Fail loud: an unknown tag (typo) must not silently default to u64
			// and miscount a run that was meant to be wider.
			return fmt.Errorf("WriteSeedPolyrun: unknown counter %q (want u64 or u128)", counter[0])
		}
	}
	f, err := os.Create(path)
	if err != nil {
		return err
	}
	defer f.Close()

	if rev == "" {
		rev = "unknown"
	}
	// Header.
	fmt.Fprintf(f, "POLYRUN 1\n")
	fmt.Fprintf(f, "height %d\n", H)
	fmt.Fprintf(f, "maxn %d\n", maxn)
	fmt.Fprintf(f, "counter %s\n", counterTag)
	fmt.Fprintf(f, "classifier triangle\n")
	fmt.Fprintf(f, "keylo \n")
	fmt.Fprintf(f, "keyhi \n")
	fmt.Fprintf(f, "records %018d\n", 1)
	fmt.Fprintf(f, "rev %s\n", rev)
	fmt.Fprintf(f, "byteorder 1\n")
	fmt.Fprintf(f, "\n")

	// One binary record: sig=(H+2 zero bytes), lo=0, len=1, counts[0]=1 as a
	// single-byte LEB128 varint (0x01), matching core/run.h encodeVarint. The
	// counter tag in the header still selects the in-memory decode width.
	keyLen := H + 2
	body := make([]byte, keyLen+2+1)
	// body[0..keyLen-1] = 0 (sig); body[keyLen] = 0 (lo)
	body[keyLen+1] = 1 // len = 1
	body[keyLen+2] = 1 // counts[0] = 1 (varint single byte)

	crc := Fnv1a64(body)
	crcBytes := make([]byte, 8)
	binary.LittleEndian.PutUint64(crcBytes, crc)

	if _, err := f.Write(body); err != nil {
		return err
	}
	if _, err := f.Write(crcBytes); err != nil {
		return err
	}
	return f.Close()
}

// keyBounds is one input file's [keylo, keyhi) header stamp, decoded for
// range-overlap tests. hasLo/hasHi false = that side open (bound absent from
// the header -- e.g. a first/last merge range, or a file written before the
// stamp existed).
type keyBounds struct {
	lo, hi       []byte
	hasLo, hasHi bool
}

// loadKeyBounds parses each path's header once and returns its stamped key
// bounds. One ParseHeader per file per round -- the whole point is that the
// per-UNIT cost of consulting bounds must be zero syscalls.
func loadKeyBounds(paths []string, keyLen int) []keyBounds {
	bounds := make([]keyBounds, len(paths))
	for i, p := range paths {
		hdr, _, err := ParseHeader(p)
		if err != nil {
			continue // unreadable header = unstamped = never pruned
		}
		bounds[i].lo, bounds[i].hasLo = hexBytes(hdr.KeyLo, keyLen)
		bounds[i].hi, bounds[i].hasHi = hexBytes(hdr.KeyHi, keyLen)
	}
	return bounds
}

// pruneByBounds returns the subset of paths whose stamped [keylo, keyhi)
// overlaps the unit range [loHex, hiHex) ("" = open end). The writer stamps
// the REQUESTED range, so every record in a file lies inside its stamp; a
// file whose stamp misses the unit range cannot contribute a record and is
// safely dropped (Fan-In Tax, results/fanin-tax.md). Unstamped files are
// always kept. If nothing overlaps (a steal-child remnant can shrink past
// every file), the FULL list is returned: the unit then range-filters to an
// empty output, byte-identical to pre-prune behavior.
func pruneByBounds(paths []string, bounds []keyBounds, loHex, hiHex string, keyLen int) []string {
	uLo, hasULo := hexBytes(loHex, keyLen)
	uHi, hasUHi := hexBytes(hiHex, keyLen)
	kept := make([]string, 0, 4)
	for i, p := range paths {
		b := bounds[i]
		if b.hasHi && hasULo && sigLE(b.hi, uLo) {
			continue // file entirely below the unit ([lo,hi): hi==uLo excludes)
		}
		if b.hasLo && hasUHi && sigLE(uHi, b.lo) {
			continue // file entirely above the unit
		}
		kept = append(kept, p)
	}
	if len(kept) == 0 {
		return paths
	}
	return kept
}

// sigLE reports a <= b for equal-length key byte strings.
func sigLE(a, b []byte) bool {
	for i := range a {
		if a[i] != b[i] {
			return a[i] < b[i]
		}
	}
	return true
}

// mergeRangeCount caps a round's merge fan-out so each range carries at
// least minPerRange records, mirroring mapPhase's minPerUnit cap: a tiny
// stage table must not be cut into cores*mult ranges each paying the full
// per-range open-every-input cost (Fan-In Tax's merge half).
func mergeRangeCount(base int, totalIn uint64, nOuts int) int {
	const minPerRange = 2048
	n := base
	if capR := int((totalIn + minPerRange - 1) / minPerRange); capR < n {
		n = capR
	}
	if n > nOuts {
		n = nOuts
	}
	if n < 1 {
		n = 1
	}
	return n
}
