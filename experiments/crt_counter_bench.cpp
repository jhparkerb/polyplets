// crt_counter_bench — measure the cost of CRT-style modular accumulation as a
// function of (counter width, reduction style, in-degree). Models the inner loop
// of the polyomino transfer-matrix sweep: each destination state's counts-by-size
// row is the modular sum of its in-edges' source rows. The matrix is 0/1, so the
// operation is purely additive — dst[n] = (dst[n] + src[n]) mod p, with both
// operands already < p.
//
// What it isolates:
//   - WIDTH b in {8,16,32,64}: bytes/count = b/8 sets the dominant per-state RAM
//     and the per-pass memory traffic. Smaller width => smaller working set =>
//     better cache/bandwidth, but needs more moduli (more passes) for the same
//     exact range.
//   - STYLE: noreduce (bandwidth ceiling) | naivemod (current engine: widen to
//     u64, "% p") | condsub (add + one conditional subtract) | deferred (sum the
//     whole in-edge group in a wide temp, reduce once per dest — amortizes the
//     reduction over the in-degree).
//   - INDEGREE D: average # of source rows accumulated per destination. Sets how
//     much the deferred reduction is amortized.
//
// Kill-safe: each (width,style,indegree) result line is printed AND appended+flushed
// to the --out file the instant it is measured, so `timeout 3600` losing the process
// loses no completed data point.

#include <cstdio>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <vector>
#include <random>
#include <chrono>
#include <string>

using std::uint8_t; using std::uint16_t; using std::uint32_t; using std::uint64_t;

static const int R = 24;          // row length (counts for n=1..maxn, ~a(22) regime)
static double TARGET_S = 0.40;    // measure each config for ~this many seconds

// Largest prime below 2^b (general primes; the realistic "arbitrary prime" case).
template <class T> struct Mod;
template <> struct Mod<uint8_t>  { static const uint32_t P = 251u; };          // 2^8-5
template <> struct Mod<uint16_t> { static const uint32_t P = 65521u; };        // 2^16-15
template <> struct Mod<uint32_t> { static const uint32_t P = 2147483647u; };   // 2^31-1 (Mersenne)
template <> struct Mod<uint64_t> { static const uint64_t P = 0ull; };          // 64-bit: exact, no modulus

enum Style { NOREDUCE, NAIVEMOD, CONDSUB, DEFERRED };
static const char* styleName(Style s) {
  switch (s) { case NOREDUCE: return "noreduce"; case NAIVEMOD: return "naivemod";
               case CONDSUB: return "condsub"; default: return "deferred"; }
}

// One sweep over all destinations; returns a checksum to defeat dead-code elim.
template <class T>
uint64_t sweep(const std::vector<T>& pool, int nstates,
               const std::vector<uint32_t>& srcIdx, int D, Style style, uint64_t p) {
  std::vector<T> dst(static_cast<size_t>(nstates) * R, 0);
  const T P = static_cast<T>(p);
  for (int d = 0; d < nstates; ++d) {
    T* o = &dst[static_cast<size_t>(d) * R];
    const uint32_t* si = &srcIdx[static_cast<size_t>(d) * D];
    if (style == DEFERRED) {
      uint64_t acc[R]; for (int n = 0; n < R; ++n) acc[n] = 0;
      for (int e = 0; e < D; ++e) {
        const T* s = &pool[static_cast<size_t>(si[e]) * R];
        for (int n = 0; n < R; ++n) acc[n] += s[n];   // wide temp, no reduce
      }
      if (p) for (int n = 0; n < R; ++n) o[n] = static_cast<T>(acc[n] % p);
      else   for (int n = 0; n < R; ++n) o[n] = static_cast<T>(acc[n]);
    } else {
      for (int e = 0; e < D; ++e) {
        const T* s = &pool[static_cast<size_t>(si[e]) * R];
        for (int n = 0; n < R; ++n) {
          if (style == NOREDUCE || p == 0) {
            o[n] = static_cast<T>(o[n] + s[n]);                       // wraparound / exact
          } else if (style == NAIVEMOD) {
            o[n] = static_cast<T>((static_cast<uint64_t>(o[n]) + s[n]) % p);
          } else { // CONDSUB: operands < p, single add, one conditional subtract
            uint64_t t = static_cast<uint64_t>(o[n]) + s[n];
            o[n] = static_cast<T>(t >= p ? t - p : t);
          }
        }
      }
    }
  }
  uint64_t sum = 0; for (size_t i = 0; i < dst.size(); i += 257) sum += dst[i];
  return sum;
}

template <class T>
void run(const char* wname, int bbits, FILE* out, std::mt19937& rng) {
  const uint64_t p = Mod<T>::P;
  // Working set: pool sized to ~exceed cache. nstates*R*sizeof(T). Keep #rows fixed
  // across widths so edge/enumeration work is identical and only byte-traffic scales.
  const int nstates = 3'000'000;
  std::vector<T> pool(static_cast<size_t>(nstates) * R);
  {
    std::uniform_int_distribution<uint64_t> ud(0, p ? p - 1 : 0xffffffffffffffffull);
    for (auto& x : pool) x = static_cast<T>(p ? ud(rng) : ud(rng));
  }
  for (int D : {2, 4, 8, 16}) {
    std::vector<uint32_t> srcIdx(static_cast<size_t>(nstates) * D);
    std::uniform_int_distribution<uint32_t> id(0, nstates - 1);
    for (auto& x : srcIdx) x = id(rng);
    for (Style style : {NOREDUCE, NAIVEMOD, CONDSUB, DEFERRED}) {
      if (p == 0 && (style == NAIVEMOD || style == CONDSUB)) continue; // 64b exact: no modulus
      // time it: repeat sweeps until ~TARGET_S elapsed
      auto t0 = std::chrono::steady_clock::now();
      uint64_t reps = 0, chk = 0; double el = 0;
      do {
        chk += sweep<T>(pool, nstates, srcIdx, D, style, p);
        ++reps;
        el = std::chrono::duration<double>(std::chrono::steady_clock::now() - t0).count();
      } while (el < TARGET_S);
      double accums = static_cast<double>(reps) * nstates * D;   // dst+=src events
      double nsPerAccum = el / accums * 1e9;
      double bytes = accums * R * (bbits / 8.0) * 3.0;           // read src+rd/wr dst ~3x
      double gbps = bytes / el / 1e9;
      double accPerS = accums / el;
      // mega-accumulations/sec; GB/s; ns per (dst+=src) row-add of R counts
      std::fprintf(out, "%-4s b=%2d P=%-12llu D=%2d style=%-9s  Macc/s=%8.1f  ns/accum=%6.3f  GB/s=%6.2f  chk=%llu\n",
                   wname, bbits, (unsigned long long)p, D, styleName(style),
                   accPerS / 1e6, nsPerAccum, gbps, (unsigned long long)chk);
      std::fflush(out);
      std::printf("%-4s b=%2d D=%2d style=%-9s  Macc/s=%8.1f  ns/accum=%6.3f  GB/s=%6.2f\n",
                  wname, bbits, D, styleName(style), accPerS / 1e6, nsPerAccum, gbps);
      std::fflush(stdout);
    }
  }
}

int main(int argc, char** argv) {
  const char* outpath = "experiments/crt_bench_results.txt";
  for (int i = 1; i < argc; ++i)
    if (!std::strcmp(argv[i], "--out") && i + 1 < argc) outpath = argv[++i];
    else if (!std::strcmp(argv[i], "--secs") && i + 1 < argc) TARGET_S = std::atof(argv[++i]);
  FILE* out = std::fopen(outpath, "a");
  if (!out) { std::perror("fopen"); return 1; }
  std::fprintf(out, "# crt_counter_bench  R=%d nstates=3e6  secs/cfg=%.2f\n", R, TARGET_S);
  std::fflush(out);
  std::mt19937 rng(12345);
  run<uint8_t >("u8",   8, out, rng);
  run<uint16_t>("u16", 16, out, rng);
  run<uint32_t>("u32", 32, out, rng);
  run<uint64_t>("u64", 64, out, rng);
  std::fprintf(out, "# done\n"); std::fflush(out); std::fclose(out);
  return 0;
}
