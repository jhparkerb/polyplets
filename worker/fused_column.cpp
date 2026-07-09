// fused_column.cpp — Even Keel D6 (per-COLUMN fusion).
//
// Runs a WHOLE kink column in one process, keeping every intermediate table
// in RAM across all H stages -- NO inter-stage POLYRUN files. Per-STAGE
// fusion (the reverted fused_stage.cpp) was memory-bandwidth-bound at
// ~13-22 cores because it re-serialized each stage's output to files and
// re-read it next stage, so 80 threads blocked on page-cache I/O instead of
// computing. Keeping the data in RAM across stages drops the file traffic
// H-fold (read frontier once, write next frontier once) so each in-RAM
// stage runs at the benchmark's ~74 cores (experiments/full_column_bench.cpp).
//
// Flow: read column frontier (parallel) -> kinkSeedStage0 (harvest T(n,H))
// -> H parallel in-RAM stage map+reduce -> kinkFinalizeColumn -> write next
// frontier (parallel, partitioned by --cuts). Emits the harvested triangle
// rows + accounting, matching map_worker's seed contract so the orchestrator
// collects T(n,H) unchanged.
//
// Usage:
//   fused_column --in P[,P...] --H N --maxn N [--counter u64|u128]
//                [--cores N] [--fold 0|1] --out-prefix PREFIX
//                [--cuts HEX,HEX,...] [--ram BYTES] [--rev GITREV]
//
// Correctness is IDENTICAL to the map+merge column: same transition, same
// combine, same finalize; fusion only changes where intermediate data lives
// (RAM vs files). Gated byte-identical in test/gate_fused_column.cpp.

#include <algorithm>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <thread>
#include <vector>

#include "core/classifier.h"
#include "core/fdlimit.h"
#include "core/kink.h"
#include "core/kink_column.h"
#include "core/run.h"
#include "core/runfile.h"
#include "core/signature.h"
#include "worker/worker_util.h"

// ---- parallel sort+dedup of a Run (sample-sort + per-bucket combine) -------
// Records that share a canonical key are COMBINED (deduplicateRun); cuts are
// on whole keys so a key lands in exactly one bucket -> per-bucket dedup is
// complete, and concatenating buckets in ascending order yields one globally
// sorted+deduped Run, byte-identical to sortRun+deduplicateRun on the whole.
template <class W>
static Run<W> parallelSortDedup(std::vector<Run<W>>&& shards, int keyLen, int threads) {
  size_t total = 0;
  for (const auto& s : shards) total += s.size();
  if (total == 0) return Run<W>();

  // 1. sample splitters (record-quantile) from a stride over all shards
  std::vector<Sig> samp;
  {
    const size_t want = std::min<size_t>(total, 200000);
    const size_t stride = std::max<size_t>(1, total / want);
    size_t seen = 0;
    for (const auto& s : shards)
      for (size_t i = 0; i < s.size(); ++i, ++seen)
        if (seen % stride == 0) samp.push_back(s[i].sig);
  }
  std::sort(samp.begin(), samp.end(),
            [&](const Sig& a, const Sig& b) { return sigCmp(a.b, b.b, keyLen) < 0; });
  const int P = std::max(1, threads);
  std::vector<Sig> split;
  for (int t = 1; t < P && !samp.empty(); ++t)
    split.push_back(samp[(size_t)t * samp.size() / P]);
  const int nb = static_cast<int>(split.size()) + 1;
  auto bucketOf = [&](const Sig& s) {
    int lo = 0, hi = static_cast<int>(split.size());
    while (lo < hi) { int m = (lo + hi) / 2; if (sigCmp(s.b, split[m].b, keyLen) < 0) hi = m; else lo = m + 1; }
    return lo;
  };

  // 2. scatter each shard's records into per-shard-per-bucket buffers (parallel)
  const int ns = static_cast<int>(shards.size());
  std::vector<std::vector<Run<W>>> tl(static_cast<size_t>(ns), std::vector<Run<W>>(static_cast<size_t>(nb)));
  {
    std::vector<std::thread> pool;
    for (int s = 0; s < ns; ++s)
      pool.emplace_back([&, s]() {
        for (auto& rec : shards[static_cast<size_t>(s)])
          tl[static_cast<size_t>(s)][static_cast<size_t>(bucketOf(rec.sig))].push_back(std::move(rec));
        Run<W>().swap(shards[static_cast<size_t>(s)]);
      });
    for (auto& th : pool) th.join();
  }

  // 3. each bucket owner gathers its column, sort+dedup (parallel over buckets)
  std::vector<Run<W>> buckets(static_cast<size_t>(nb));
  {
    std::vector<std::thread> pool;
    for (int b = 0; b < nb; ++b)
      pool.emplace_back([&, b]() {
        Run<W>& B = buckets[static_cast<size_t>(b)];
        size_t tot = 0;
        for (int s = 0; s < ns; ++s) tot += tl[static_cast<size_t>(s)][static_cast<size_t>(b)].size();
        B.reserve(tot);
        for (int s = 0; s < ns; ++s)
          for (auto& x : tl[static_cast<size_t>(s)][static_cast<size_t>(b)]) B.push_back(std::move(x));
        sortRun(B);
        deduplicateRun(B);
      });
    for (auto& th : pool) th.join();
  }

  // 4. concat buckets in ascending key order
  Run<W> out;
  size_t o = 0; for (auto& B : buckets) o += B.size();
  out.reserve(o);
  for (auto& B : buckets) { for (auto& x : B) out.push_back(std::move(x)); Run<W>().swap(B); }
  return out;
}

// ---- one in-RAM parallel stage: transition + parallel sort+dedup ----------
template <class W>
static Run<W> parallelStage(const Run<W>& src, int H, int maxn, int r, int threads) {
  const int kLen = kinkKeyLen(H);
  const int T = std::max(1, threads);
  std::vector<Run<W>> per(static_cast<size_t>(T));
  {
    std::vector<std::thread> pool;
    const size_t chunk = (src.size() + static_cast<size_t>(T) - 1) / static_cast<size_t>(T);
    for (int t = 0; t < T; ++t)
      pool.emplace_back([&, t]() {
        const size_t i0 = std::min(src.size(), static_cast<size_t>(t) * chunk);
        const size_t i1 = std::min(src.size(), i0 + chunk);
        Run<W>& buf = per[static_cast<size_t>(t)];
        if (i1 > i0) buf.reserve((i1 - i0) * 2);
        for (size_t i = i0; i < i1; ++i) {
          const RunRecord<W>& rec = src[i];
          const int ms = rec.minSize();
          if (ms < 0) continue;
          kinkStageTransition(rec.sig, H, r, ms, maxn, [&](const Sig& tg, int shift) {
            const int nl = static_cast<int>(rec.lo) + shift;
            if (nl > maxn) return;
            const int nlen = std::min<int>(rec.len, maxn - nl + 1);
            RunRecord<W> s;
            s.sig = tg; s.H = static_cast<uint8_t>(H); s.keyLen = static_cast<uint8_t>(kLen);
            s.lo = static_cast<uint8_t>(nl); s.len = static_cast<uint8_t>(nlen);
            s.counts.assign(rec.counts.begin(), rec.counts.begin() + nlen);
            buf.push_back(std::move(s));
          });
        }
      });
    for (auto& th : pool) th.join();
  }
  return parallelSortDedup<W>(std::move(per), kLen, T);
}

// ---- parallel read of the column frontier files ---------------------------
template <class W>
static Run<W> parallelRead(const std::vector<std::string>& inPaths, int H, int keyLen, int threads) {
  const int ns = static_cast<int>(inPaths.size());
  std::vector<Run<W>> shards(static_cast<size_t>(std::max(1, ns)));
  {
    std::vector<std::thread> pool;
    for (int i = 0; i < ns; ++i)
      pool.emplace_back([&, i]() {
        RunFileReader<W> rr(inPaths[static_cast<size_t>(i)], H, keyLen);
        if (!rr.ok()) { std::fprintf(stderr, "fused_column: cannot read %s\n", inPaths[static_cast<size_t>(i)].c_str()); std::exit(1); }
        RunRecord<W> rec;
        Run<W>& sh = shards[static_cast<size_t>(i)];
        while (rr.next(rec)) sh.push_back(std::move(rec));
      });
    for (auto& th : pool) th.join();
  }
  // frontier files may share keys (col-0 seed) -> combine via parallel sort+dedup
  return parallelSortDedup<W>(std::move(shards), keyLen, threads);
}

// ---- parallel partitioned write of the next frontier ----------------------
template <class W>
static size_t parallelWrite(const Run<W>& next, int H, int keyLen, const std::vector<Sig>& cuts,
                            const std::string& outPrefix, const std::string& rev, int /*threads*/) {
  const int nb = static_cast<int>(cuts.size()) + 1;
  auto bucketOf = [&](const Sig& s) {
    int lo = 0, hi = static_cast<int>(cuts.size());
    while (lo < hi) { int m = (lo + hi) / 2; if (sigCmp(s.b, cuts[static_cast<size_t>(m)].b, keyLen) < 0) hi = m; else lo = m + 1; }
    return lo;
  };
  // next is globally sorted -> each range is a contiguous [beg,end) span; find
  // spans by scanning once, then write ranges in parallel.
  std::vector<size_t> begin(static_cast<size_t>(nb) + 1, next.size());
  begin[0] = 0;
  { int cur = 0; begin[0] = 0;
    for (size_t i = 0; i < next.size(); ++i) {
      int b = bucketOf(next[i].sig);
      while (cur < b) { begin[static_cast<size_t>(++cur)] = i; }
    }
    while (cur < nb) begin[static_cast<size_t>(++cur)] = next.size();
  }
  std::vector<size_t> counts(static_cast<size_t>(nb), 0);
  {
    std::vector<std::thread> pool;
    for (int b = 0; b < nb; ++b)
      pool.emplace_back([&, b]() {
        const size_t a = begin[static_cast<size_t>(b)], e = begin[static_cast<size_t>(b + 1)];
        if (a >= e) return;
        const std::string path = outPrefix + "_u" + std::to_string(b) + ".bin";
        RunFileWriter<W> w(path, H, 0, "", "", rev, keyLen, /*write_index=*/true);
        for (size_t i = a; i < e; ++i) w.append(next[i]);
        counts[static_cast<size_t>(b)] = w.finalize();
      });
    for (auto& th : pool) th.join();
  }
  size_t tot = 0; for (size_t c : counts) tot += c;
  return tot;
}

static std::vector<Sig> parseCuts(const std::string& s, int keyLen) {
  std::vector<Sig> out;
  size_t start = 0;
  while (start < s.size()) {
    size_t pos = s.find(',', start);
    const std::string tok = (pos == std::string::npos) ? s.substr(start) : s.substr(start, pos - start);
    if (!tok.empty()) { Sig sig; std::memset(sig.b, 0, SIGMAX);
      if (!hexToBytes(tok, sig.b, keyLen)) { std::fprintf(stderr, "fused_column: bad --cuts %s\n", tok.c_str()); std::exit(1); }
      out.push_back(sig); }
    if (pos == std::string::npos) break;
    start = pos + 1;
  }
  return out;
}

template <class W>
static int runColumn(const std::vector<std::string>& inPaths, int H, int maxn, int cores,
                     bool fold, const std::vector<Sig>& cuts, const std::string& outPrefix,
                     const std::string& rev, size_t ramBudget) {
  const double t0Wall = wallSeconds(), t0Cpu = cpuSeconds();

  Run<W> frontier = parallelRead<W>(inPaths, H, H + 2, cores);

  const size_t recBytes = sizeof(RunRecord<W>) + static_cast<size_t>(maxn) * sizeof(W) + 32;
  if (ramBudget > 0 && frontier.size() * recBytes * 8 > ramBudget) {
    std::fprintf(stderr, "fused_column: column too large for in-RAM fusion "
                 "(%zu frontier records); needs spill (unimplemented)\n", frontier.size());
    return 1;
  }

  TriangleRow<W> triangle(H, maxn);
  Run<W> stage = kinkSeedStage0<W, ClassifyTriangle>(frontier, H, triangle);
  Run<W>().swap(frontier);
  for (int r = 0; r < H; ++r) stage = parallelStage<W>(stage, H, maxn, r, cores);
  Run<W> next = kinkFinalizeColumn<W>(stage, H, maxn, fold);
  Run<W>().swap(stage);

  const size_t outRecs = parallelWrite<W>(next, H, H + 2, cuts, outPrefix, rev, cores);

  printTriangleRows(H, maxn, triangle.row);
  std::printf("event=done cpu_s=%.3f wall_s=%.3f peak_rss_mb=%.1f records=%zu spill_bytes=0 stop_key=\n",
              cpuSeconds() - t0Cpu, wallSeconds() - t0Wall, peakRssMB(), outRecs);
  return 0;
}

int main(int argc, char** argv) {
  std::vector<std::string> inPaths;
  int H = -1, maxn = -1, cores = static_cast<int>(std::thread::hardware_concurrency());
  bool fold = true;
  std::string counter = "u128", outPrefix, cutsArg, rev;
  size_t ram = 0;
  auto split = [](const std::string& s) { std::vector<std::string> v; size_t p = 0; while (p < s.size()) { size_t c = s.find(',', p); v.push_back(s.substr(p, c == std::string::npos ? c : c - p)); if (c == std::string::npos) break; p = c + 1; } return v; };
  for (int i = 1; i < argc; ++i) {
    std::string a = argv[i];
    auto next = [&]() { return std::string(i + 1 < argc ? argv[++i] : ""); };
    if (a == "--in") inPaths = split(next());
    else if (a == "--H") H = std::atoi(next().c_str());
    else if (a == "--maxn") maxn = std::atoi(next().c_str());
    else if (a == "--cores") cores = std::atoi(next().c_str());
    else if (a == "--fold") fold = std::atoi(next().c_str()) != 0;
    else if (a == "--counter") counter = next();
    else if (a == "--out-prefix") outPrefix = next();
    else if (a == "--cuts") cutsArg = next();
    else if (a == "--ram") ram = std::strtoull(next().c_str(), nullptr, 10);
    else if (a == "--rev") rev = next();
  }
  if (inPaths.empty() || H < 0 || maxn < 0 || outPrefix.empty()) {
    std::fprintf(stderr, "fused_column: need --in --H --maxn --out-prefix\n");
    return 2;
  }
  raiseFdLimitToHard();
  const std::vector<Sig> cuts = parseCuts(cutsArg, H + 2);
  if (cores < 1) cores = 1;
  return counter == "u64" ? runColumn<u64>(inPaths, H, maxn, cores, fold, cuts, outPrefix, rev, ram)
                          : runColumn<u128>(inPaths, H, maxn, cores, fold, cuts, outPrefix, rev, ram);
}
