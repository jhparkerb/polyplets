// Bounded-excess cluster-weight FAMILIES -- C++ port of the row-transfer DP in
// experiments/severance_w3_depths.py (Severance W3, docs/onset-defect-severance-
// plan.md section 3).
//
// The Python file's section 3 records why depth j = 4 stalled: the depth-j
// identity needs the aggregated weight families of excess e <= j-1, and at
// j = 4, K = 19 the excess-3 families put 5-cell rows into the row-transfer DP
// (span cap 2K+emax+1 = 42, so ~1.7e5 reachable 5-cell states) -- hours in
// Python. This is a straight translation of families()/weights_for_type() with
// the row placement enumerated by pruned DFS instead of by shape x offset, and
// the per-level state expansion spread over threads.
//
//   usage:
//     build/severance_w3_families families K EMAX [threads]
//     build/severance_w3_families types  2,3 4,2 5 ...      [validation mode]
//
//   stdout, families mode (the contract with severance_w3_depths.py::_load_table):
//       # severance_w3_families K=<K> emax=<EMAX>
//       <e> <k> <sig> <bb> <pp>            one line per (excess e, surplus k)
//     with sig = sum of interior weights over all cluster types of surplus k and
//     excess e, bb = bottom-edge (cluster + q above, no p below), pp = pure
//     (cluster alone).  Lines are ascending in (e, k); cells with k < 1 are
//     omitted.  '#' lines are comments.
//   stdout, types mode (contract with the validation in severance_w3_depths.py):
//       <v1,v2,...> \t interior \t bottom \t top \t pure
//   stderr: obs.h start/heartbeat/done event stream.
//
// Weights are exact integers in unsigned __int128 with an explicit overflow
// check on every accumulation (die() on overflow, never wrap). At K = 19 the
// largest cell is ~1e26, six orders under the 3.4e38 ceiling; the check is
// there so that a future K cannot silently wrap.
//
// Span cap: a connected king animal's column projection is an interval, so a
// c-cell animal spans at most c-1 columns; a cluster of l rows and excess e,
// plus the p below and q above, has 2l+e+2 cells and therefore every row of it
// spans at most 2l+e+1 <= 2K+EMAX+1. Capping row spans there is exact.

#include <algorithm>
#include <climits>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <mutex>
#include <string>
#include <thread>
#include <unordered_map>
#include <vector>

#include "obs.h"

using u128 = unsigned __int128;

namespace {

constexpr int MAXN = 8;  // max cells in one row: EMAX+2 in families mode, the
                         // largest row of a validation type otherwise

[[noreturn]] void die(const char* msg) {
  std::fprintf(stderr, "FATAL: %s\n", msg);
  std::exit(2);
}

void add_checked(u128& acc, u128 x) {
  if (acc > ~static_cast<u128>(0) - x) die("u128 overflow in weight accumulation");
  acc += x;
}

u128 mul_checked(u128 a, u128 b) {
  if (a != 0 && b > ~static_cast<u128>(0) / a) die("u128 overflow in weight product");
  return a * b;
}

std::string to_dec(u128 v) {
  if (v == 0) return "0";
  char buf[48];
  int i = sizeof buf;
  while (v) {
    buf[--i] = static_cast<char>('0' + static_cast<int>(v % 10));
    v /= 10;
  }
  return std::string(buf + i, sizeof buf - i);
}

// ---------------------------------------------------------------- DP state
// The current (top) row's cell columns normalized so the leftmost is 0, plus
// that row's connectivity partition (labels compacted in order of appearance)
// -- exactly the Python state (cells, part).
struct Key {
  uint8_t n;
  int8_t c[MAXN];
  uint8_t p[MAXN];
};

Key blank_key() {
  Key k;
  std::memset(&k, 0, sizeof k);
  return k;
}

struct KeyEq {
  bool operator()(const Key& a, const Key& b) const {
    return std::memcmp(&a, &b, sizeof(Key)) == 0;
  }
};
struct KeyHash {
  size_t operator()(const Key& k) const {
    const unsigned char* p = reinterpret_cast<const unsigned char*>(&k);
    uint64_t h = 1469598103934665603ULL;
    for (size_t i = 0; i < sizeof(Key); ++i) {
      h ^= p[i];
      h *= 1099511628211ULL;
    }
    return static_cast<size_t>(h);
  }
};

using Map = std::unordered_map<Key, u128, KeyHash, KeyEq>;

int nblocks(const Key& k) {
  int nb = 0;
  for (int i = 0; i < k.n; ++i) nb = std::max(nb, static_cast<int>(k.p[i]) + 1);
  return nb;
}

// Columns adjacent to every pending component: the placements of the free cell
// q above that close the animal (Python q_end).
int q_end(const Key& k) {
  const int nb = nblocks(k);
  const uint32_t full = (1u << nb) - 1;
  const int lo = k.c[0] - 1, hi = k.c[k.n - 1] + 1;
  uint32_t m[132];  // >= span+3, span <= 126 by the int8 cell-range check
  const int width = hi - lo + 1;
  for (int i = 0; i < width; ++i) m[i] = 0;
  for (int i = 0; i < k.n; ++i)
    for (int d = -1; d <= 1; ++d) m[k.c[i] + d - lo] |= (1u << k.p[i]);
  int cnt = 0;
  for (int i = 0; i < width; ++i)
    if (m[i] == full) ++cnt;
  return cnt;
}

// 1 if the stack is already a single component (Python bare_end).
int bare_end(const Key& k) { return nblocks(k) == 1 ? 1 : 0; }

// -------------------------------------------------------------- transitions
// All placements of a next row of `t` cells, as the Python transitions(): the
// row's own span is capped at `span`, and every pending component of the source
// must have a cell adjacent to the new row (an untouched component can never
// reconnect -- king adjacency moves the row index by at most 1).
//
// The Python enumerates (shape, offset); here the cells are placed left to
// right by DFS with two prunes, which is the same set: the offset window
// [xmin-sp-1, xmax+1] is implied by the touch condition (the block holding
// xmin forces a cell >= xmin-1, the block holding xmax a cell <= xmax+1).
struct Expand {
  int span = 0, t = 0;
  Map* out = nullptr;

  const int8_t* c = nullptr;
  const uint8_t* p = nullptr;
  int n = 0, nb = 0;
  u128 cnt = 0;
  int bmin[MAXN], bmax[MAXN];
  int T[MAXN];
  uint32_t mask = 0, full = 0;
  int lab[2 * MAXN];

  void run(const Key& k, u128 count) {
    c = k.c;
    p = k.p;
    n = k.n;
    nb = nblocks(k);
    cnt = count;
    for (int b = 0; b < nb; ++b) {
      bmin[b] = INT_MAX;
      bmax[b] = INT_MIN;
    }
    for (int i = 0; i < n; ++i) {
      const int b = p[i];
      bmin[b] = std::min(bmin[b], static_cast<int>(c[i]));
      bmax[b] = std::max(bmax[b], static_cast<int>(c[i]));
    }
    full = (1u << nb) - 1;
    mask = 0;
    // T[0] must leave every block reachable: some cell of the row lies in
    // [bmin[b]-1, bmax[b]+1] for every b, and all cells lie in [T0, T0+span].
    int lo = -span - 1, hi = INT_MAX;
    for (int b = 0; b < nb; ++b) {
      lo = std::max(lo, bmin[b] - 1 - span);
      hi = std::min(hi, bmax[b] + 1);
    }
    rec(0, lo, hi);
  }

  void rec(int j, int start, int last) {
    if (j == t) {
      if (mask == full) emit();
      return;
    }
    // An untouched block can only be reached by a cell <= (its rightmost
    // cell)+1; cells are placed left to right, so once x passes the smallest
    // such limit among untouched blocks the subtree is dead.
    int limit = INT_MAX;
    for (uint32_t un = (~mask) & full; un; un &= un - 1)
      limit = std::min(limit, bmax[__builtin_ctz(un)] + 1);
    for (int x = start; x <= last; ++x) {
      if (x > limit) return;
      const uint32_t saved = mask;
      for (int i = 0; i < n; ++i) {
        const int d = x - c[i];
        if (d >= -1 && d <= 1) mask |= (1u << p[i]);
      }
      T[j] = x;
      if (j == 0) {
        rec(1, x + 1, x + span - (t - 2));
      } else {
        rec(j + 1, x + 1, T[0] + span - (t - 2 - j));
      }
      mask = saved;
    }
  }

  int find(int x) {
    while (lab[x] != x) {
      lab[x] = lab[lab[x]];
      x = lab[x];
    }
    return x;
  }
  void unite(int a, int b) {
    const int ra = find(a), rb = find(b);
    if (ra != rb) lab[ra] = rb;
  }

  void emit() {
    const int tot = nb + t;
    for (int i = 0; i < tot; ++i) lab[i] = i;
    for (int j = 0; j < t; ++j)
      for (int i = 0; i < n; ++i) {
        const int d = T[j] - c[i];
        if (d >= -1 && d <= 1) unite(p[i], nb + j);
      }
    for (int j = 0; j + 1 < t; ++j)
      if (T[j + 1] - T[j] <= 1) unite(nb + j, nb + j + 1);
    Key k = blank_key();
    k.n = static_cast<uint8_t>(t);
    int canon[2 * MAXN];
    for (int i = 0; i < tot; ++i) canon[i] = -1;
    int next = 0;
    for (int j = 0; j < t; ++j) {
      k.c[j] = static_cast<int8_t>(T[j] - T[0]);
      const int r = find(nb + j);
      if (canon[r] < 0) canon[r] = next++;
      k.p[j] = static_cast<uint8_t>(canon[r]);
    }
    add_checked((*out)[k], cnt);
  }
};

// Apply one row of `t` cells to every state of `src`, accumulating into `dst`.
// Parallel over source states; each thread fills a private map, merged after.
void step(const Map& src, Map& dst, int t, int span, int threads) {
  if (src.empty()) return;
  std::vector<const std::pair<const Key, u128>*> items;
  items.reserve(src.size());
  for (const auto& kv : src) items.push_back(&kv);
  const int nth = std::max(1, std::min<int>(threads, static_cast<int>(items.size())));
  std::vector<Map> parts(nth);
  std::vector<std::thread> pool;
  std::mutex mu;
  size_t nextIdx = 0;
  const size_t chunk = 64;
  for (int th = 0; th < nth; ++th) {
    pool.emplace_back([&, th]() {
      Expand e;
      e.span = span;
      e.t = t;
      e.out = &parts[th];
      while (true) {
        size_t lo;
        {
          std::lock_guard<std::mutex> g(mu);
          if (nextIdx >= items.size()) return;
          lo = nextIdx;
          nextIdx = std::min(items.size(), lo + chunk);
        }
        for (size_t i = lo; i < std::min(items.size(), lo + chunk); ++i)
          e.run(items[i]->first, items[i]->second);
      }
    });
  }
  for (auto& th : pool) th.join();
  for (auto& pm : parts)
    for (const auto& kv : pm) add_checked(dst[kv.first], kv.second);
}

// All normalized shapes of `t` cells with span <= `span` (Python _shapes),
// each as a fresh state with the within-row adjacency partition.
void seed_shapes(Map& dst, int t, int span) {
  std::vector<int> cells(t);
  cells[0] = 0;
  std::vector<int> idx(t - 1);
  for (int i = 0; i < t - 1; ++i) idx[i] = i + 1;
  while (true) {
    for (int i = 0; i < t - 1; ++i) cells[i + 1] = idx[i];
    Key k = blank_key();
    k.n = static_cast<uint8_t>(t);
    int lab = 0;
    k.c[0] = 0;
    k.p[0] = 0;
    for (int i = 1; i < t; ++i) {
      if (cells[i] - cells[i - 1] > 1) ++lab;
      k.c[i] = static_cast<int8_t>(cells[i]);
      k.p[i] = static_cast<uint8_t>(lab);
    }
    add_checked(dst[k], 1);
    int i = t - 2;
    while (i >= 0 && idx[i] == span - (t - 2 - i)) --i;
    if (i < 0) break;
    ++idx[i];
    for (int j = i + 1; j < t - 1; ++j) idx[j] = idx[j - 1] + 1;
  }
}

Key single_cell() {
  Key k = blank_key();
  k.n = 1;
  return k;
}

// ------------------------------------------------------------ families mode
void families(int K, int emax, int threads, obs::Reporter& rep) {
  if (emax + 2 > MAXN) die("EMAX too large for MAXN");
  const int span = 2 * K + emax + 1;
  if (span > 126) die("span exceeds int8 cell range");
  std::vector<std::vector<u128>> sig(emax + 1, std::vector<u128>(K + 1, 0));
  std::vector<std::vector<u128>> bb(emax + 1, std::vector<u128>(K + 1, 0));
  std::vector<std::vector<u128>> pp(emax + 1, std::vector<u128>(K + 1, 0));

  std::vector<Map> dp_i(emax + 1), dp_b(emax + 1);
  dp_i[0][single_cell()] = 1;  // the p cell below

  for (int ell = 1; ell <= K; ++ell) {
    std::vector<Map> n_i(emax + 1), n_b(emax + 1);
    for (int t = 2; t <= emax + 2; ++t) {
      const int de = t - 2;
      for (int e = 0; e + de <= emax; ++e) {
        const int e2 = e + de;
        if (ell + e2 > K) continue;
        step(dp_i[e], n_i[e2], t, span, threads);
        step(dp_b[e], n_b[e2], t, span, threads);
      }
      if (ell == 1 && de <= emax && 1 + de <= K) seed_shapes(n_b[de], t, span);
    }
    dp_i.swap(n_i);
    dp_b.swap(n_b);
    size_t ns = 0;
    for (int e = 0; e <= emax; ++e) {
      if (ell + e > K) continue;
      ns += dp_i[e].size() + dp_b[e].size();
      for (const auto& kv : dp_i[e])
        add_checked(sig[e][ell + e], mul_checked(kv.second, q_end(kv.first)));
      for (const auto& kv : dp_b[e]) {
        add_checked(bb[e][ell + e], mul_checked(kv.second, q_end(kv.first)));
        add_checked(pp[e][ell + e], mul_checked(kv.second, bare_end(kv.first)));
      }
    }
    char ex[96];
    std::snprintf(ex, sizeof ex, "level=%d states=%zu", ell, ns);
    rep.beat(static_cast<double>(ell), ex, true);
  }

  std::printf("# severance_w3_families K=%d emax=%d\n", K, emax);
  for (int e = 0; e <= emax; ++e)
    for (int k = 1; k <= K; ++k)
      std::printf("%d %d %s %s %s\n", e, k, to_dec(sig[e][k]).c_str(),
                  to_dec(bb[e][k]).c_str(), to_dec(pp[e][k]).c_str());
  std::fflush(stdout);
}

// --------------------------------------------------------------- types mode
// The Python weights_for_type(): the four weights of ONE cluster type, by the
// same DP -- validation against cluster_weight_dp.KNOWN_WEIGHTS / count_stack.
u128 run_type(const std::vector<int>& seq, bool start_p, int span, bool pure) {
  Map dp;
  size_t first = 0;
  if (start_p) {
    dp[single_cell()] = 1;
  } else {
    seed_shapes(dp, seq[0], span);
    first = 1;
  }
  for (size_t r = first; r < seq.size(); ++r) {
    Map nxt;
    step(dp, nxt, seq[r], span, 1);
    dp.swap(nxt);
  }
  u128 tot = 0;
  for (const auto& kv : dp)
    add_checked(tot, mul_checked(kv.second, pure ? bare_end(kv.first) : q_end(kv.first)));
  return tot;
}

void types_mode(const std::vector<std::string>& specs) {
  for (const auto& s : specs) {
    std::vector<int> v;
    size_t i = 0;
    while (i < s.size()) {
      size_t j = s.find(',', i);
      if (j == std::string::npos) j = s.size();
      v.push_back(std::atoi(s.substr(i, j - i).c_str()));
      i = j + 1;
    }
    int span = 2;
    for (int x : v) {
      if (x > MAXN) die("row size exceeds MAXN");
      span += x;
    }
    if (span > 126) die("span exceeds int8 cell range");
    std::vector<int> rv(v.rbegin(), v.rend());
    const u128 wi = run_type(v, true, span, false);
    const u128 wb = run_type(v, false, span, false);
    const u128 wt = run_type(rv, false, span, false);
    const u128 wp = run_type(v, false, span, true);
    std::printf("%s\t%s\t%s\t%s\t%s\n", s.c_str(), to_dec(wi).c_str(),
                to_dec(wb).c_str(), to_dec(wt).c_str(), to_dec(wp).c_str());
    std::fflush(stdout);
  }
}

}  // namespace

int main(int argc, char** argv) {
  if (argc < 2) die("usage: severance_w3_families families K EMAX [threads] "
                    "| types v1 v2 ...");
  const std::string mode = argv[1];
  if (mode == "types") {
    std::vector<std::string> specs(argv + 2, argv + argc);
    obs::Reporter rep("severance_w3_families", 0, "mode=types");
    types_mode(specs);
    rep.done("");
    return 0;
  }
  if (mode != "families") die("unknown mode (expected 'families' or 'types')");
  const int K = argc > 2 ? std::atoi(argv[2]) : 9;
  const int emax = argc > 3 ? std::atoi(argv[3]) : 3;
  int threads = argc > 4 ? std::atoi(argv[4]) : 0;
  if (threads <= 0) {
    const unsigned hw = std::thread::hardware_concurrency();
    threads = static_cast<int>(hw ? std::min(hw, 10u) : 1u);
  }
  char extra[128];
  std::snprintf(extra, sizeof extra, "mode=families K=%d emax=%d threads=%d span=%d",
                K, emax, threads, 2 * K + emax + 1);
  obs::Reporter rep("severance_w3_families", K, extra);
  families(K, emax, threads, rep);
  rep.done("");
  return 0;
}
