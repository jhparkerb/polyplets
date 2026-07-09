// reduce_bench.cpp -- decisive micro-benchmark for the ONE open design
// question in docs/full-utilization-redesign.md: which parallel REDUCE
// primitive wins for the kink stage map-output at frontier scale, on 80
// cores?
//
//   alpha : partitioned parallel sort-merge. Partition the emitted multiset
//           into T key-RANGE buckets (evenly-spaced sampled splitters, like
//           the engine's SampleKeysMulti), each thread sortRun+deduplicateRun
//           its own bucket. This is the current engine's reduce, made
//           embarrassingly parallel across buckets.
//   rho   : radix-partitioned private hash-aggregation. Scatter each emitted
//           record into one of P = T*f partitions by hash(full key); each
//           thread hash-aggregates (combine on collision) the partitions it
//           owns, entirely privately -- no shared table, no lock. Because
//           partitioning is by key-hash, each key lands in exactly one
//           partition, so per-partition aggregation IS the global aggregate
//           (no final merge).
//
// Both consume the SAME emitted multiset, produced by the REAL
// kinkStageTransition over a realistically-structured canonical mixed-state
// population (canonMixed keys, ~0.56*maxn u128 count windows, fan-out<=2).
// The two outputs are verified byte-identical as key->combined-value maps
// before any timing is trusted.
//
// Build (native, like other experiments/): see build cmd in reduce_bench.sh.
// Throwaway measurement tool; not wired into any gate.

#include <chrono>
#include <cstdio>
#include <cstdint>
#include <cstring>
#include <random>
#include <thread>
#include <vector>

#include "core/kink.h"
#include "core/run.h"
#include "core/signature.h"

using Clock = std::chrono::steady_clock;
using W = u128;

static int g_H = 18;
static int g_maxn = 34;
static int g_stage = 9;            // a mid-column stage r in [0,H)
static size_t g_N = 8'000'000;     // input records (emitted ~ 2x)
static int g_threads = 80;
static int g_overpart = 8;         // rho over-partition factor f

static double secs(Clock::time_point a, Clock::time_point b) {
  return std::chrono::duration<double>(b - a).count();
}

// ---- realistic canonical mixed-state generation --------------------------
// Produce N stage records (keyLen H+4) with canonMixed key structure and
// realistic u128 count windows. Not required to be reachable states -- the
// reduce only cares about key byte-distribution, collision rate, and value
// size, all reproduced here. Parallel, per-thread RNG.
static Run<W> generateInput(int H, int maxn, size_t N, int threads) {
  const int kLen = kinkKeyLen(H);
  const int win = std::max(1, (int)(0.56 * maxn));   // ~measured window width
  Run<W> out(N);
  std::vector<std::thread> pool;
  size_t chunk = (N + threads - 1) / threads;
  for (int t = 0; t < threads; ++t) {
    pool.emplace_back([&, t]() {
      std::mt19937_64 rng(0x9e3779b97f4a7c15ULL ^ (0xd1b54a32d192ed03ULL * (t + 1)));
      auto rnd = [&](uint64_t m) { return rng() % m; };
      size_t lo_i = (size_t)t * chunk, hi_i = std::min(N, lo_i + chunk);
      for (size_t i = lo_i; i < hi_i; ++i) {
        RunRecord<W>& r = out[i];
        std::memset(r.sig.b, 0, SIGMAX);
        // boundary labels b[0..H): ~half occupied, C in 1..5 raw components
        int C = 1 + (int)rnd(5);
        for (int p = 0; p < H; ++p)
          if (rnd(2)) r.sig.b[p] = (unsigned char)(1 + rnd(C));
        r.sig.b[H + 2] = rnd(2) ? (unsigned char)(1 + rnd(C)) : 0; // carry
        r.sig.b[H]     = (unsigned char)rnd(2);
        r.sig.b[H + 1] = (unsigned char)rnd(2);
        r.sig.b[H + 3] = (unsigned char)rnd(2);
        canonMixed(r.sig, H);           // REAL canonicalization
        r.H = (uint8_t)H; r.keyLen = (uint8_t)kLen;
        int lo = (int)rnd(6);
        int len = std::max(1, win + (int)rnd(5) - 2);
        if (lo + len > maxn + 1) len = maxn + 1 - lo;
        if (len < 1) { lo = 0; len = 1; }
        r.lo = (uint8_t)lo; r.len = (uint8_t)len;
        r.counts.resize(len);
        for (int k = 0; k < len; ++k) r.counts[k] = (W)(rng() & 0xffffffffULL) + 1;
      }
    });
  }
  for (auto& th : pool) th.join();
  return out;
}

// ---- map: REAL kinkStageTransition over the input -> emitted multiset ----
static Run<W> mapEmit(const Run<W>& src, int H, int maxn, int r, int threads) {
  const int kLen = kinkKeyLen(H);
  std::vector<Run<W>> per(threads);
  std::vector<std::thread> pool;
  size_t chunk = (src.size() + threads - 1) / threads;
  for (int t = 0; t < threads; ++t) {
    pool.emplace_back([&, t]() {
      size_t lo_i = (size_t)t * chunk, hi_i = std::min(src.size(), lo_i + chunk);
      Run<W>& buf = per[t];
      buf.reserve((hi_i - lo_i) * 2);
      for (size_t i = lo_i; i < hi_i; ++i) {
        const RunRecord<W>& rec = src[i];
        int trueMs = rec.minSize();
        if (trueMs < 0) continue;
        kinkStageTransition(rec.sig, H, r, trueMs, maxn, [&](const Sig& tg, int shift) {
          int new_lo = (int)rec.lo + shift;
          if (new_lo > maxn) return;
          int new_len = std::min<int>(rec.len, maxn - new_lo + 1);
          RunRecord<W> s;
          s.sig = tg; s.H = (uint8_t)H; s.keyLen = (uint8_t)kLen;
          s.lo = (uint8_t)new_lo; s.len = (uint8_t)new_len;
          s.counts.assign(rec.counts.begin(), rec.counts.begin() + new_len);
          buf.push_back(std::move(s));
        });
      }
    });
  }
  for (auto& th : pool) th.join();
  Run<W> all;
  size_t tot = 0; for (auto& b : per) tot += b.size();
  all.reserve(tot);
  for (auto& b : per) for (auto& r2 : b) all.push_back(std::move(r2));
  return all;
}

static uint64_t hashKey(const Sig& s, int kLen) {
  uint64_t h = 1469598103934665603ULL;
  for (int i = 0; i < kLen; ++i) { h ^= s.b[i]; h *= 1099511628211ULL; }
  h ^= h >> 33; h *= 0xff51afd7ed558ccdULL; h ^= h >> 33;
  return h;
}

// ---- alpha: partitioned parallel sort-merge ------------------------------
static Run<W> reduceAlpha(const Run<W>& emitted, int kLen, int threads) {
  // sampled evenly-spaced key-range splitters (like SampleKeysMulti)
  size_t nsamp = std::min<size_t>(emitted.size(), 200000);
  std::vector<Sig> samp; samp.reserve(nsamp);
  size_t stride = std::max<size_t>(1, emitted.size() / nsamp);
  for (size_t i = 0; i < emitted.size(); i += stride) samp.push_back(emitted[i].sig);
  std::sort(samp.begin(), samp.end(), [&](const Sig& a, const Sig& b){ return sigCmp(a.b,b.b,kLen)<0; });
  std::vector<Sig> split;
  for (int t = 1; t < threads; ++t) split.push_back(samp[(size_t)t * samp.size() / threads]);
  auto bucketOf = [&](const Sig& s) {
    int lo = 0, hi = (int)split.size();
    while (lo < hi) { int m=(lo+hi)/2; if (sigCmp(s.b, split[m].b, kLen) < 0) hi=m; else lo=m+1; }
    return lo;
  };
  // scatter into per-bucket vectors (parallel over threads, each scans a slice
  // and appends to thread-local per-bucket buffers, then concatenate)
  std::vector<std::vector<Run<W>>> tl(threads, std::vector<Run<W>>(threads));
  std::vector<std::thread> pool; size_t chunk=(emitted.size()+threads-1)/threads;
  for (int t=0;t<threads;t++) pool.emplace_back([&,t](){
    size_t a=(size_t)t*chunk,b=std::min(emitted.size(),a+chunk);
    for(size_t i=a;i<b;i++){ int bk=bucketOf(emitted[i].sig); tl[t][bk].push_back(emitted[i]); }
  });
  for(auto&th:pool)th.join(); pool.clear();
  std::vector<Run<W>> buckets(threads);
  std::vector<std::thread> pool2;
  for(int bk=0;bk<threads;bk++) pool2.emplace_back([&,bk](){
    Run<W>& B=buckets[bk];
    for(int t=0;t<threads;t++) for(auto&r:tl[t][bk]) B.push_back(r);
    sortRun(B); deduplicateRun(B);
  });
  for(auto&th:pool2)th.join();
  Run<W> out; size_t tot=0; for(auto&B:buckets)tot+=B.size(); out.reserve(tot);
  for(auto&B:buckets) for(auto&r:B) out.push_back(std::move(r));
  return out;
}

// ---- rho: radix hash-partition + private per-partition hash-agg ----------
// The reduce uses a FLAT open-addressing (linear-probe) table per partition
// -- the whole point of rho is cache-resident probing. std::unordered_map
// (node-per-insert malloc, pointer-chase) would defeat exactly the property
// being tested, so it is deliberately NOT used.
static uint64_t nextPow2(uint64_t x){ uint64_t p=1; while(p<x)p<<=1; return p; }

static Run<W> reduceRho(const Run<W>& emitted, int kLen, int threads, int f) {
  int P = threads * f;
  // scatter by hash(key) into P partitions via thread-local buffers
  std::vector<std::vector<Run<W>>> tl(threads, std::vector<Run<W>>(P));
  std::vector<std::thread> pool; size_t chunk=(emitted.size()+threads-1)/threads;
  for(int t=0;t<threads;t++) pool.emplace_back([&,t](){
    size_t a=(size_t)t*chunk,b=std::min(emitted.size(),a+chunk);
    for(size_t i=a;i<b;i++){ int pt=(int)(hashKey(emitted[i].sig,kLen)%(uint64_t)P); tl[t][pt].push_back(emitted[i]); }
  });
  for(auto&th:pool)th.join(); pool.clear();
  std::vector<Run<W>> partOut(P);
  std::vector<std::thread> pool2;
  int pchunk=(P+threads-1)/threads;
  for(int t=0;t<threads;t++) pool2.emplace_back([&,t](){
    for(int p=t*pchunk, pe=std::min(P,p+pchunk); p<pe; p++){
      size_t cnt=0; for(int tt=0;tt<threads;tt++) cnt+=tl[tt][p].size();
      if(!cnt){ continue; }
      // flat linear-probe table: slots[] holds index+1 into entries, 0=empty.
      uint64_t cap=nextPow2(cnt*2), mask=cap-1;
      std::vector<uint32_t> slots(cap,0);
      Run<W>& entries=partOut[p]; entries.reserve(cnt);
      for(int tt=0;tt<threads;tt++) for(auto&r:tl[tt][p]){
        uint64_t h=hashKey(r.sig,kLen)&mask;
        for(;;){
          uint32_t s=slots[h];
          if(s==0){ entries.push_back(r); slots[h]=(uint32_t)entries.size(); break; }
          RunRecord<W>& e=entries[s-1];
          if(std::memcmp(e.sig.b,r.sig.b,kLen)==0){ e.combine(r); break; }
          h=(h+1)&mask;
        }
      }
    }
  });
  for(auto&th:pool2)th.join();
  Run<W> out; size_t tot=0; for(auto&O:partOut)tot+=O.size(); out.reserve(tot);
  for(auto&O:partOut) for(auto&r:O) out.push_back(std::move(r));
  return out;
}

// canonical compare: sort both by key and check same key set + same combined
// value per key.
static bool sameResult(Run<W> a, Run<W> b, int kLen) {
  if (a.size()!=b.size()) { std::printf("  MISMATCH size %zu vs %zu\n",a.size(),b.size()); return false; }
  auto cmp=[&](const RunRecord<W>&x,const RunRecord<W>&y){return sigCmp(x.sig.b,y.sig.b,kLen)<0;};
  std::sort(a.begin(),a.end(),cmp); std::sort(b.begin(),b.end(),cmp);
  for(size_t i=0;i<a.size();i++){
    if(sigCmp(a[i].sig.b,b[i].sig.b,kLen)!=0){std::printf("  MISMATCH key @%zu\n",i);return false;}
    // compare combined value over union window
    if(a[i].lo!=b[i].lo||a[i].len!=b[i].len){std::printf("  MISMATCH window @%zu (%d,%d)vs(%d,%d)\n",i,a[i].lo,a[i].len,b[i].lo,b[i].len);return false;}
    for(int k=0;k<a[i].len;k++) if(a[i].counts[k]!=b[i].counts[k]){std::printf("  MISMATCH count @%zu[%d]\n",i,k);return false;}
  }
  return true;
}

int main(int argc, char** argv) {
  for (int i=1;i<argc;i++){
    if(!std::strncmp(argv[i],"H=",2))g_H=atoi(argv[i]+2);
    else if(!std::strncmp(argv[i],"maxn=",5))g_maxn=atoi(argv[i]+5);
    else if(!std::strncmp(argv[i],"stage=",6))g_stage=atoi(argv[i]+6);
    else if(!std::strncmp(argv[i],"N=",2))g_N=strtoull(argv[i]+2,0,10);
    else if(!std::strncmp(argv[i],"threads=",8))g_threads=atoi(argv[i]+8);
    else if(!std::strncmp(argv[i],"f=",2))g_overpart=atoi(argv[i]+2);
  }
  const int kLen = kinkKeyLen(g_H);
  std::printf("reduce_bench H=%d maxn=%d stage=%d N=%zu threads=%d f=%d keyLen=%d\n",
              g_H,g_maxn,g_stage,g_N,g_threads,g_overpart,kLen);

  auto t0=Clock::now();
  Run<W> input = generateInput(g_H,g_maxn,g_N,g_threads);
  auto t1=Clock::now();
  Run<W> emitted = mapEmit(input,g_H,g_maxn,g_stage,g_threads);
  auto t2=Clock::now();
  std::printf("setup: gen %.2fs (%zu recs), map %.2fs -> emitted %zu recs\n",
              secs(t0,t1),input.size(),secs(t1,t2),emitted.size());

  // warmup (first-touch page faults, freq scaling) discarded; best-of-5.
  { Run<W> w1=reduceAlpha(emitted,kLen,g_threads); Run<W> w2=reduceRho(emitted,kLen,g_threads,g_overpart);
    std::printf("warmup done (alpha %zu, rho %zu)\n", w1.size(), w2.size()); }
  double aBest=1e18,rBest=1e18; Run<W> aOut,rOut;
  for(int rep=0;rep<5;rep++){
    auto a=Clock::now(); Run<W> o=reduceAlpha(emitted,kLen,g_threads); auto b=Clock::now();
    double s=secs(a,b); if(s<aBest){aBest=s;aOut=std::move(o);}
    std::printf("  alpha rep%d %.3fs\n",rep,s);
  }
  for(int rep=0;rep<5;rep++){
    auto a=Clock::now(); Run<W> o=reduceRho(emitted,kLen,g_threads,g_overpart); auto b=Clock::now();
    double s=secs(a,b); if(s<rBest){rBest=s;rOut=std::move(o);}
    std::printf("  rho   rep%d %.3fs\n",rep,s);
  }

  std::printf("distinct out: alpha=%zu rho=%zu\n",aOut.size(),rOut.size());
  bool ok=sameResult(aOut,rOut,kLen);
  std::printf("VERIFY: %s\n", ok?"IDENTICAL":"*** MISMATCH ***");
  std::printf("RESULT: alpha=%.3fs rho=%.3fs  rho_speedup=%.2fx  (%s)\n",
              aBest,rBest,aBest/rBest, ok?"valid":"INVALID-OUTPUTS-DIFFER");
  return ok?0:1;
}
