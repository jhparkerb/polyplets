// bench_column -- single-column micro-bench harness (docs/frontier/harness-spec.md Part 2).
//
// Measures ONE column transition of the square-8 (polyplet) transfer-matrix sweep,
// apples-to-apples across swappable state-store backends: same FIXED input column,
// same byte-equality oracle, same states/sec + peak-RSS columns. Every engine-swap
// idea (03 sort, oq1 lock-free, 01 compression, 09 u128) collapses to "a Backend +
// a row in one table" instead of a bespoke prototype.
//
// SCOPE (this file): the `hash` baseline backend (the current FlatDB store,
// cpp/tma/statedb.h) AND the `sort` backend (03's sort+merge reduce). The other
// backends are declared in the Backend seam and left as clearly-marked stubs
// (concurrent/compressed/u128). The 03 sort kill-test needs the in-RAM slowdown
// S = (sort states/sec)/(hash states/sec); we print states/sec PROMINENTLY so
// that ratio is one division. FINDING (n=14,15 on gympie): S~=1.0 -- the wall is
// dominated by the SHARED map body (stepColumnSquare8/forEachViableMask closure
// math, ~96-97% of the transition); sort's reduce (sort+merge) is only ~3% and
// hash's find-or-insert is a comparably small slice, so swapping the store barely
// moves the wall. The sort reduce IS heavier per-emitted-record at larger m (the
// O(m log m) tax shows as ~66ns->73ns/emitted from n=14->15) but stays a small
// fraction of total. Caveat: in-RAM only -- this is gate-1 compute tax, not the
// external-memory verdict (the real engine spills sorted runs to NVMe).
//
// ----- ENGINE-COUPLING NOTE (what we did vs the ideal isolated transition) -----
// The spec wants ONE column transition invoked in isolation. The production engine
// (sweep8.h sweepSquare8Height) does NOT factor the transition into a callable
// unit: the inner body (for_each over the source column -> forEachViableMask ->
// stepColumnSquare8 -> addCounts into `next`, plus the comps==1 harvest) is INLINED
// inside the multi-column `for (col ...)` loop. So we do the faithful thing:
//   * capture mode replays the real sweep up to a chosen column boundary and dumps
//     that live FlatDB column to disk (via the engine's own for_each) -- the fixed
//     input, byte-for-byte what the engine holds there;
//   * bench mode loads that column and runs the transition body ONCE, copied
//     VERBATIM from sweep8.h's column loop (same forEachViableMask/stepColumn/
//     addCounts/harvest), parameterised over the Backend seam.
// Because the bench's transition body is the same code the engine runs, the `hash`
// output column is byte-identical to the dense engine's next column at that
// boundary BY CONSTRUCTION; the oracle (sorted-by-sig serialize + hash) makes that
// checkable and is the gate every future backend must pass.
// NEXT STEP to fully isolate: lift sweep8.h's column body into a shared
//   transitionColumn(src, Backend& dst, H, maxn, fold, Counts& harvest)
// free function that BOTH the engine and this bench call -- then "one transition"
// is a real function, not a copy, and a backend swap is provably the only delta.
// (That is the store-first refactor flagged in statedb.h's TODO(simplify) #30;
// deferred until a(21) is in-hand so it never races the live frontier job.)
// --------------------------------------------------------------------------------
//
// Build:  g++ -std=c++20 -O3 -o build/bench_column experiments/bench_column.cpp
// Capture the fixed input column once (heaviest column of the smoke fixture):
//   build/bench_column --capture square8 14 --only-height 12 --out experiments/col_n14.bin
// Bench a backend (asserts byte-identical-to-hash before reporting):
//   build/bench_column --backend hash --in experiments/col_n14.bin \
//       --out experiments/bench_column_results.txt

#include <algorithm>
#include <chrono>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>

#include "../cpp/tma/signature.h"
#include "../cpp/tma/statedb.h"
#include "../cpp/tma/transition_square8.h"

#include <sys/resource.h>

// Peak resident-set size in bytes (the RAM-cliff axis oq1/01 live on). getrusage's
// ru_maxrss is the process high-water; units differ by OS (Darwin: bytes; Linux: KB).
static size_t peakRSSBytes() {
  struct rusage ru;
  getrusage(RUSAGE_SELF, &ru);
#if defined(__APPLE__)
  return static_cast<size_t>(ru.ru_maxrss);          // Darwin: already bytes
#else
  return static_cast<size_t>(ru.ru_maxrss) * 1024;   // Linux: KB -> bytes
#endif
}

// --- Fixed-column file format (self-describing, version-tagged) ----------------
// magic "BCOL" | u32 version | i32 H | i32 maxn | i32 col | u64 nStates
// then nStates records: SIGMAX sig bytes, then (maxn+1) u64 counts.
struct ColHeader {
  char magic[4];
  std::uint32_t version;
  std::int32_t H, maxn, col;
  std::uint64_t nStates;
};
static constexpr std::uint32_t COL_VERSION = 1;

// ============================ Backend seam =====================================
// A backend implements the three statedb.h operations and nothing else; the
// transition body (transitionColumn, below) is written ONCE against this interface
// and never edited per backend. Swapping the backend swaps the store; the sweep
// never knows. Row is u64* for hash/sort/concurrent/compressed; u128 changes only
// the counter axis (a u128* view) -- stubbed below.
//
// MVP implements HashBackend only. sort/concurrent/compressed/u128 are stubs that
// print "not implemented" and exit nonzero, so `--backend sort` is a clean TODO,
// not a crash.

struct Metrics {
  double statesPerSec = 0;   // HEADLINE: output states produced / sec (the 03 S ratio)
  size_t peakRSS = 0;        // high-water bytes (oq1/01 RAM-cliff axis)
  std::uint64_t outStates = 0;
  double transitionSecs = 0;
  // per-backend counters (filled by the relevant backend only):
  std::uint64_t casRetries = 0;       // oq1: CAS-retry iters/insert
  double bytesPerState = 0;           // 01: store bytes/state
  double nsPerAccum = 0;              // 09: ns per addCounts row-add
};

// HashBackend: the current FlatDB (the dense baseline). slot/for_each/reserve are
// FlatDB's; the transition body calls them through this thin wrapper so a future
// backend is a drop-in with the same three operations.
struct HashBackend {
  FlatDB db;
  explicit HashBackend(int maxn) : db(maxn) {}
  void reserve(size_t n) { db.reserve(n); }
  u64* slot(const Sig& k) { return db.slot(k); }
  template <class F> void for_each(F&& fn) const { db.for_each(std::forward<F>(fn)); }
  size_t size() const { return db.size(); }
  void clear() { db.clear(); }
};

// SortBackend: the 03 sort/merge store. The transition body is UNCHANGED -- it
// still calls slot(out) per (source-state x viable-mask) and accumulates the
// shifted source row into the returned pointer. The semantic difference is that
// slot() here does NOT find-or-insert: it APPENDS a fresh (sig, count_vec) record
// to a flat emission vector and returns that record's (zeroed) row. So after the
// map every successor contribution is one row in `emit`, with duplicate out_sigs
// scattered throughout (no consolidation during the map -- no random lookup, the
// whole point of 03). consolidate() then does the reduce-by-key as a pure
// sort+merge: sort `emit` by out_sig under the SAME total order the oracle uses
// (memcmp over SIGMAX), then merge adjacent equal sigs by fixed-width vector-add
// of their count rows. After consolidate(), for_each/size mirror the hash backend
// exactly, so the oracle and the table apply byte-for-byte unchanged.
struct SortBackend {
  int maxn;
  size_t stride;                 // maxn+1, to match FlatDB row width
  std::vector<Sig> sigs;         // one entry per emitted contribution (pre-merge)
  std::vector<u64> rows;         // flat count rows, `stride` apart, parallel to sigs
  // post-consolidate view (filled by consolidate()):
  std::vector<Sig> outSigs;
  std::vector<u64> outRows;
  size_t outCnt = 0;
  bool consolidated = false;

  explicit SortBackend(int maxn_) : maxn(maxn_), stride(maxn_ + 1) {}

  void reserve(size_t n) {
    // n is the number of SOURCE states; each fans out over several masks, so the
    // emission count is a multiple of it. Reserve generously to skip reallocs
    // (this is the in-RAM materialization the task wants quantified).
    sigs.reserve(n * 8);
    rows.reserve(n * 8 * stride);
  }

  // MAP-step slot(): append a fresh record, return its zeroed row. No lookup.
  u64* slot(const Sig& k) {
    sigs.push_back(k);
    const size_t off = rows.size();
    rows.resize(off + stride, 0);   // value-init zeros the new row
    return &rows[off];
  }

  // REDUCE step: sort the emissions by out_sig (oracle's total order), then merge
  // adjacent equal sigs by summing their count rows. Output is the sorted, merged
  // (sig, row) column -- identical content to the hash backend's output column.
  void consolidate() {
    const size_t m = sigs.size();
    // Argsort indices by sig (memcmp), so we move small indices, not whole rows.
    std::vector<std::uint32_t> idx(m);
    for (size_t i = 0; i < m; ++i) idx[i] = static_cast<std::uint32_t>(i);
    std::sort(idx.begin(), idx.end(), [&](std::uint32_t a, std::uint32_t b) {
      return std::memcmp(sigs[a].b, sigs[b].b, SIGMAX) < 0;
    });
    // Merge runs of equal sigs, vector-adding their rows.
    outSigs.clear();
    outRows.clear();
    outSigs.reserve(m);
    outRows.reserve(m * stride);
    outCnt = 0;
    size_t i = 0;
    while (i < m) {
      const Sig& key = sigs[idx[i]];
      outSigs.push_back(key);
      const size_t base = outRows.size();
      outRows.resize(base + stride, 0);
      u64* acc = &outRows[base];
      size_t j = i;
      while (j < m && std::memcmp(sigs[idx[j]].b, key.b, SIGMAX) == 0) {
        const u64* r = &rows[static_cast<size_t>(idx[j]) * stride];
        for (size_t n = 0; n < stride; ++n) acc[n] += r[n];
        ++j;
      }
      ++outCnt;
      i = j;
    }
  }

  size_t size() const { return outCnt; }
  size_t emitted() const { return sigs.size(); }

  template <class F> void for_each(F&& fn) const {
    for (size_t i = 0; i < outCnt; ++i)
      fn(outSigs[i], &outRows[i * stride]);
  }
};

// ---- STUB backends (declared in the seam, not yet implemented) ----------------
// Each rides this same harness at its own idea's effort; the comparison table and
// the byte-equality oracle are already here, so landing one is "implement the
// three ops + flip the dispatch". Keep these as explicit TODOs, never a crash.
[[noreturn]] static void stubBackend(const char* name, const char* serves,
                                     const char* proves) {
  std::fprintf(stderr,
               "backend '%s' not implemented yet (serves %s: %s).\n"
               "Implement reserve/slot/for_each on the Backend seam and add a\n"
               "dispatch case; the oracle + states/sec table already apply.\n",
               name, serves, proves);
  std::exit(3);
}
// TODO(03 sort): sorted (sig,row) stream, sort+merge transition. Proves the in-RAM
//   sort-vs-hash slowdown S at n=14-16 (no random find-or-insert). S = (sort
//   states/sec)/(hash states/sec); this harness prints states/sec for the division.
// TODO(oq1 concurrent): ConcDB open-addr, CAS slot-claim + atomic row-accumulate.
//   Fill Metrics.casRetries (CAS iters/insert) + fetch_add attempts on hottest slots.
// TODO(01 compressed): ranged-row / packed-signature FlatDB. Fill Metrics.bytesPerState
//   + mean ranged-row width (hi-lo+1).
// TODO(09 u128): FlatDB with __uint128_t rows (counter swap, not store swap). Fill
//   Metrics.nsPerAccum + GB/s; real contest is vs crt_counter_bench's 31-bit arm.

// ====================== The shared transition body =============================
// ONE column transition, copied VERBATIM from sweep8.h sweepSquare8Height's column
// loop (lines ~86-109), parameterised over the Backend seam. Source column `src`
// (any backend) -> destination column `dst` (any backend). `harvest[n]` accumulates
// the comps==1 closures (animals completed this column). `fold` mirrors the engine's
// --fold orbit-canonicalization. Output is independent of store/threading => a swap
// of dst's backend cannot change the bytes (the oracle checks it).
template <class SrcB, class DstB>
static void transitionColumn(const SrcB& src, DstB& dst, int H, int maxn,
                             bool fold, Counts& harvest) {
  src.for_each([&](const Sig& sig, const u64* counts) {
    const int ms = minSizeRow(counts, maxn);
    if (ms < 0) return;
    // boundary is canonical => component count is its max label.
    int comps = 0;
    for (int j = 0; j < H; ++j)
      if (sig.b[j] > comps) comps = sig.b[j];
    // empty next column closes the animal: single component touching top+bottom.
    if (comps == 1 && sig.b[H] && sig.b[H + 1])
      for (int n = 1; n <= maxn; ++n) harvest[n] += counts[n];
    forEachViableMask(sig, H, maxn - ms, [&](unsigned mask) {
      Sig out;
      if (stepColumnSquare8(sig, H, mask, out) != Outcome::Alive) return;
      const int cells = __builtin_popcount(mask);
      if (ms + cells + completionLowerBound(out.b, H) > maxn) return;
      if (fold) foldSig(out, H);
      // addCounts against the backend's slot(): shift sizes by `cells`, drop > maxn.
      u64* drow = dst.slot(out);
      for (int n = 0; n + cells <= maxn; ++n)
        if (counts[n]) drow[n + cells] += counts[n];
    });
  });
}

// ====================== Oracle: canonical serialize + FNV hash =================
// for_each visits in UNSTABLE slot order (the spec flagged this), so we MUST sort
// by signature for a stable byte image. Serialize (sorted sig bytes || counts row)
// and FNV-1a it; two backends agree iff their output columns are byte-identical.
struct Entry {
  Sig sig;
  std::vector<u64> row;
  bool operator<(const Entry& o) const {
    return std::memcmp(sig.b, o.sig.b, SIGMAX) < 0;
  }
};

template <class B>
static std::vector<Entry> drainSorted(const B& dst, int maxn) {
  std::vector<Entry> v;
  dst.for_each([&](const Sig& sig, const u64* row) {
    Entry e;
    e.sig = sig;
    e.row.assign(row, row + (maxn + 1));
    v.push_back(std::move(e));
  });
  std::sort(v.begin(), v.end());
  return v;
}

static std::uint64_t hashSorted(const std::vector<Entry>& v, int maxn) {
  std::uint64_t h = 1469598103934665603ull;
  auto mix = [&](const void* p, size_t n) {
    const unsigned char* b = static_cast<const unsigned char*>(p);
    for (size_t i = 0; i < n; ++i) { h ^= b[i]; h *= 1099511628211ull; }
  };
  for (const auto& e : v) {
    mix(e.sig.b, SIGMAX);
    mix(e.row.data(), static_cast<size_t>(maxn + 1) * sizeof(u64));
  }
  return h;
}

// ============================ Capture mode =====================================
// Replay the real sweep (sweepSquare8Height path) up to column `targetCol` and dump
// that live FlatDB to `outPath`. We re-run the engine's exact column loop here (not
// a call into sweep8.h, which can't stop mid-height and hand back the store) so the
// captured column is byte-for-byte what the engine holds at that boundary. If
// targetCol<0, capture the HEAVIEST column (max live states) -- the most useful
// micro-bench input.
static int doCapture(int H, int maxn, int targetCol, bool fold,
                     const char* outPath) {
  FlatDB db(maxn), next(maxn);
  Sig seed;
  std::memset(seed.b, 0, SIGMAX);
  db.slot(seed)[0] = 1;

  // First pass to find the heaviest column if targetCol<0 (cheap: just sizes).
  // We hold the chosen column by re-running; the sweep is seconds at n=14.
  std::vector<size_t> sizes;
  {
    FlatDB a(maxn), b(maxn);
    a.slot(seed)[0] = 1;
    Counts harvest(maxn + 1, 0);
    for (int col = 0; col <= maxn && !a.empty(); ++col) {
      sizes.push_back(a.size());
      b.clear();
      HashBackend hb(maxn);  // wrapper view over b for transitionColumn
      hb.db = std::move(b);
      transitionColumn(a, hb, H, maxn, fold, harvest);
      b = std::move(hb.db);
      std::swap(a, b);
    }
  }
  int heaviest = 0;
  for (int c = 1; c < (int)sizes.size(); ++c)
    if (sizes[c] > sizes[heaviest]) heaviest = c;
  const int want = targetCol >= 0 ? targetCol : heaviest;
  std::fprintf(stderr, "capture H=%d maxn=%d cols=%zu heaviest col=%d (%zu states); "
               "capturing col=%d\n",
               H, maxn, sizes.size(), heaviest, sizes[heaviest], want);

  // Replay again, stop AT column `want`, dump db (the source column for that step).
  Counts harvest(maxn + 1, 0);
  for (int col = 0; col < want && !db.empty(); ++col) {
    next.clear();
    HashBackend hb(maxn);
    hb.db = std::move(next);
    transitionColumn(db, hb, H, maxn, fold, harvest);
    next = std::move(hb.db);
    std::swap(db, next);
  }
  if (db.empty()) {
    std::fprintf(stderr, "ERROR: column %d is empty (height exhausted)\n", want);
    return 1;
  }

  // Serialize the captured column (sorted, so the file itself is canonical/stable).
  std::vector<Entry> entries = drainSorted(db, maxn);
  FILE* f = std::fopen(outPath, "wb");
  if (!f) { std::perror("fopen capture out"); return 1; }
  ColHeader hdr{{'B', 'C', 'O', 'L'}, COL_VERSION, H, maxn, want, entries.size()};
  std::fwrite(&hdr, sizeof hdr, 1, f);
  for (const auto& e : entries) {
    std::fwrite(e.sig.b, 1, SIGMAX, f);
    std::fwrite(e.row.data(), sizeof(u64), maxn + 1, f);
  }
  std::fclose(f);
  std::fprintf(stderr, "wrote %s: H=%d maxn=%d col=%d states=%zu\n", outPath, H,
               maxn, want, entries.size());
  return 0;
}

// Load a captured column into a fresh HashBackend (the source column for the bench).
static bool loadColumn(const char* inPath, HashBackend& src, ColHeader& hdr) {
  FILE* f = std::fopen(inPath, "rb");
  if (!f) { std::perror("fopen capture in"); return false; }
  if (std::fread(&hdr, sizeof hdr, 1, f) != 1 ||
      std::memcmp(hdr.magic, "BCOL", 4) != 0 || hdr.version != COL_VERSION) {
    std::fprintf(stderr, "bad/old capture file %s\n", inPath);
    std::fclose(f);
    return false;
  }
  src.reserve(hdr.nStates + 1);
  std::vector<u64> row(hdr.maxn + 1);
  for (std::uint64_t i = 0; i < hdr.nStates; ++i) {
    Sig sig;
    if (std::fread(sig.b, 1, SIGMAX, f) != SIGMAX ||
        std::fread(row.data(), sizeof(u64), hdr.maxn + 1, f) !=
            static_cast<size_t>(hdr.maxn + 1)) {
      std::fprintf(stderr, "short read at state %llu\n", (unsigned long long)i);
      std::fclose(f);
      return false;
    }
    std::memcpy(src.slot(sig), row.data(), (hdr.maxn + 1) * sizeof(u64));
  }
  std::fclose(f);
  return true;
}

// ============================ Bench mode =======================================
// Run ONE transition through the selected backend, measure states/sec + peak RSS,
// and assert byte-identical-to-hash. The `hash` run also writes the reference
// oracle hash next to --in (col file + ".hash") so later backends compare to it.
static int doBench(const char* inPath, const std::string& backend,
                   bool fold, const char* outPath) {
  ColHeader hdr;
  HashBackend src(0);  // maxn fixed after header read; reconstruct below
  {
    // peek header to size src correctly
    FILE* f = std::fopen(inPath, "rb");
    if (!f) { std::perror("fopen"); return 1; }
    if (std::fread(&hdr, sizeof hdr, 1, f) != 1) { std::fclose(f); return 1; }
    std::fclose(f);
  }
  src = HashBackend(hdr.maxn);
  if (!loadColumn(inPath, src, hdr)) return 1;
  const int H = hdr.H, maxn = hdr.maxn;
  std::fprintf(stderr, "loaded col file: H=%d maxn=%d col=%d src_states=%llu "
               "backend=%s\n",
               H, maxn, hdr.col, (unsigned long long)src.size(), backend.c_str());

  // Dispatch. hash + sort implemented; others are clean stubs.
  if (backend == "concurrent")
    stubBackend("concurrent", "oq1", "lock-free shared table scaling at full T");
  if (backend == "compressed")
    stubBackend("compressed", "01", "bytes/state cut under packing, byte-identical");
  if (backend == "u128")
    stubBackend("u128", "09", "u128-row store stays exact within traffic budget");
  if (backend != "hash" && backend != "sort") {
    std::fprintf(stderr, "unknown backend '%s'\n", backend.c_str());
    return 2;
  }

  // --- run ONE transition, timed; backend selects the store/reduce. ---
  Metrics m;
  std::vector<Entry> outv;
  std::uint64_t emitted = 0;     // sort-only: pre-merge emission count
  if (backend == "hash") {
    HashBackend dst(maxn);
    dst.reserve(src.size() * 3 + 16);  // pre-size to skip grows (FlatDB::reserve)
    Counts harvest(maxn + 1, 0);
    auto t0 = std::chrono::steady_clock::now();
    transitionColumn(src, dst, H, maxn, fold, harvest);
    auto t1 = std::chrono::steady_clock::now();
    m.transitionSecs = std::chrono::duration<double>(t1 - t0).count();
    m.outStates = dst.size();
    m.bytesPerState = dst.size()
        ? static_cast<double>(dst.db.cap) *
              (sizeof(Sig) + dst.db.stride * sizeof(u64) + 1) / dst.size()
        : 0;
    outv = drainSorted(dst, maxn);
  } else {  // sort
    SortBackend dst(maxn);
    dst.reserve(src.size());
    Counts harvest(maxn + 1, 0);
    // Time map (emit) + reduce (sort+merge) together: that is the full column
    // transition cost the S ratio compares against hash's find-or-insert.
    auto t0 = std::chrono::steady_clock::now();
    transitionColumn(src, dst, H, maxn, fold, harvest);  // map: emit, no lookup
    auto tm = std::chrono::steady_clock::now();
    dst.consolidate();                                   // reduce: sort+merge
    auto t1 = std::chrono::steady_clock::now();
    m.transitionSecs = std::chrono::duration<double>(t1 - t0).count();
    std::fprintf(stderr, "sort split: map(emit)=%.4fs reduce(sort+merge)=%.4fs\n",
                 std::chrono::duration<double>(tm - t0).count(),
                 std::chrono::duration<double>(t1 - tm).count());
    m.outStates = dst.size();
    emitted = dst.emitted();
    // bytes/state: the materialized pre-merge emission buffer is the in-RAM tax.
    m.bytesPerState = dst.size()
        ? static_cast<double>(dst.emitted()) *
              (sizeof(Sig) + dst.stride * sizeof(u64)) / dst.size()
        : 0;
    outv = drainSorted(dst, maxn);
  }
  m.statesPerSec = m.transitionSecs > 0 ? m.outStates / m.transitionSecs : 0;
  m.peakRSS = peakRSSBytes();

  // --- oracle: serialize sorted-by-sig and hash; compare to the `hash` reference. ---
  const std::uint64_t outHash = hashSorted(outv, maxn);
  const std::string refPath = std::string(inPath) + ".hash";
  bool oraclePass = true;
  std::uint64_t refHash = outHash;
  if (backend == "hash") {
    // hash IS the reference: write/refresh it.
    FILE* rf = std::fopen(refPath.c_str(), "w");
    if (rf) { std::fprintf(rf, "%llu %d\n", (unsigned long long)outHash,
                           (int)outv.size()); std::fclose(rf); }
  } else {
    FILE* rf = std::fopen(refPath.c_str(), "r");
    if (rf) {
      int n = 0;
      if (std::fscanf(rf, "%llu %d", (unsigned long long*)&refHash, &n) >= 1)
        oraclePass = (refHash == outHash);
      std::fclose(rf);
    } else {
      std::fprintf(stderr, "no reference hash (%s) -- run --backend hash first\n",
                   refPath.c_str());
      oraclePass = false;
    }
  }

  // --- emit one kill-safe line (printed + appended+flushed to --out). ---
  char line[640];
  std::snprintf(line, sizeof line,
                "backend=%-10s H=%d maxn=%d col=%d src_states=%llu out_states=%llu "
                "emitted=%llu states_per_sec=%.3e transition_s=%.4f peak_rss_mb=%.1f "
                "bytes_per_state=%.1f oracle=%s out_hash=%llu\n",
                backend.c_str(), H, maxn, hdr.col,
                (unsigned long long)src.size(), (unsigned long long)m.outStates,
                (unsigned long long)emitted,
                m.statesPerSec, m.transitionSecs, m.peakRSS / 1048576.0,
                m.bytesPerState, oraclePass ? "PASS" : "FAIL",
                (unsigned long long)outHash);
  std::fputs(line, stdout);
  std::fflush(stdout);
  if (outPath) {
    FILE* of = std::fopen(outPath, "a");
    if (of) { std::fputs(line, of); std::fflush(of); std::fclose(of); }
  }
  // 03 S-ratio reminder: S = (this states_per_sec for sort) / (states_per_sec for hash).
  return oraclePass ? 0 : 1;
}

int main(int argc, char** argv) {
  bool capture = false;
  std::string backend = "hash", inPath, outPath, lattice;
  int maxn = 0, onlyHeight = 0, targetCol = -1;
  bool fold = false;
  for (int i = 1; i < argc; ++i) {
    std::string a = argv[i];
    if (a == "--capture") capture = true;
    else if (a == "--backend" && i + 1 < argc) backend = argv[++i];
    else if (a == "--in" && i + 1 < argc) inPath = argv[++i];
    else if (a == "--out" && i + 1 < argc) outPath = argv[++i];
    else if (a == "--only-height" && i + 1 < argc) onlyHeight = std::atoi(argv[++i]);
    else if (a == "--col" && i + 1 < argc) targetCol = std::atoi(argv[++i]);
    else if (a == "--fold") fold = true;
    else if (a == "square8") lattice = a;
    else if (a == "square4") { std::fprintf(stderr, "square8 only\n"); return 2; }
    else if (!a.empty() && (a[0] >= '0' && a[0] <= '9')) maxn = std::atoi(argv[i]);
    else { std::fprintf(stderr, "unknown arg: %s\n", argv[i]); return 2; }
  }

  if (capture) {
    if (lattice != "square8" || maxn < 1 || onlyHeight < 1) {
      std::fprintf(stderr,
                   "usage: %s --capture square8 MAXN --only-height H "
                   "[--col C] [--fold] --out FILE\n",
                   argv[0]);
      return 2;
    }
    if (outPath.empty()) { std::fprintf(stderr, "--capture needs --out\n"); return 2; }
    return doCapture(onlyHeight, maxn, targetCol, fold, outPath.c_str());
  }

  if (inPath.empty()) {
    std::fprintf(stderr,
                 "usage:\n"
                 "  %s --capture square8 MAXN --only-height H [--col C] --out FILE\n"
                 "  %s --backend {hash|sort|concurrent|compressed|u128} --in FILE "
                 "[--fold] [--out RESULTS]\n",
                 argv[0], argv[0]);
    return 2;
  }
  return doBench(inPath.c_str(), backend, fold, outPath.empty() ? nullptr
                                                                : outPath.c_str());
}
