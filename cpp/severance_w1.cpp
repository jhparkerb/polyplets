// Cluster-weight row-transfer DP -- C++ port of experiments/cluster_weight_dp.py
// (Severance W1, docs/onset-defect-severance-plan.md section 3).
//
// Purpose: the ab-initio cluster weights (interior, boundary_bottom,
// boundary_top, pure) for every composition at levels k = 1..K, where a
// composition is a row-size vector s_i >= 2 with sum(s_i - 1) = k (the SURPLUS,
// exactly as in the reference's compositions(k)). The Python reference dies
// around k = 6 (~20x per level); this is a straight translation with one added
// search prune and cross-composition memoization.
//
//   usage: build/severance_w1 K [threads]
//   stdout (contract with experiments/severance_w1_gate.py), one line per
//   composition, levels ascending, compositions in compositions(k) order:
//       v1,v2,...,vm \t interior \t boundary_bottom \t boundary_top \t pure
//   stderr: obs.h start/heartbeat/done event stream.
//
//   options: --no-rev-memo   disable the up/down mirror memoization (each stack
//                            computed in its own orientation). Used as a
//                            self-check: output must be identical with and
//                            without it.
//
// Predicted cost (measured, see results/severance_w1_weights_k*.txt headers in
// the campaign log): k<=7 seconds, k=8 minutes, k=9 hours (dalby).
// Kill/resume: no checkpointing -- a level is recomputed from scratch; levels
// are independent and printed as they finish.
//
// Weights are exact integers held in unsigned __int128 with an explicit
// overflow check on every accumulation (die() on overflow, never wrap).

#include <algorithm>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <map>
#include <mutex>
#include <string>
#include <thread>
#include <unordered_map>
#include <vector>

#include "obs.h"

using u128 = unsigned __int128;

namespace {

constexpr int MAXC = 20;  // max cells in one row = k+1; k<=10 here

[[noreturn]] void die(const char* msg) {
  std::fprintf(stderr, "FATAL: %s\n", msg);
  std::exit(2);
}

// Exact accumulation: an overflowing weight is a wrong answer, not a big one.
void add_checked(u128& acc, u128 x) {
  if (acc > ~static_cast<u128>(0) - x) die("u128 overflow in weight accumulation");
  acc += x;
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
// A state is the current (top) row's cell columns, normalized so the leftmost
// is 0, together with that row's connectivity partition (labels compacted in
// order of appearance) -- exactly the Python state.
struct Key {
  uint8_t n;
  int16_t c[MAXC];
  uint8_t p[MAXC];
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

using StateMap = std::unordered_map<Key, u128, KeyHash, KeyEq>;

// Within a row, cells at consecutive columns share a block; blocks are runs of
// consecutive columns, hence intervals, hence ordered left to right.
void row_partition(const int16_t* cells, int n, uint8_t* part) {
  int lab = 0;
  part[0] = 0;
  for (int i = 1; i < n; ++i) {
    if (cells[i] - cells[i - 1] > 1) ++lab;
    part[i] = static_cast<uint8_t>(lab);
  }
}

// One row transition: place the next row of `s` cells anywhere in the safe
// window, prune old blocks that can never be touched again, merge, normalize.
struct Expand {
  const int16_t* c = nullptr;
  const uint8_t* p = nullptr;
  int n = 0, nb = 0, s = 0, lo = 0, hi = 0;
  int16_t bmax[MAXC];
  int16_t T[MAXC];
  uint32_t mask = 0, full = 0;
  u128 cnt = 0;
  StateMap* out = nullptr;

  void run() {
    // A block of a transferred state need NOT be an interval of columns: two
    // new cells joined through a common old block share a label while sitting
    // columns apart. So contact is tested cell by cell (as in the reference);
    // bmax is only used for the dead-subtree prune.
    for (int b = 0; b < nb; ++b) bmax[b] = -32768;
    for (int i = 0; i < n; ++i) {
      int b = p[i];
      if (c[i] > bmax[b]) bmax[b] = c[i];
    }
    full = (nb >= 32) ? 0xffffffffu : ((1u << nb) - 1);
    mask = 0;
    rec(0, lo);
  }

  void rec(int j, int start) {
    if (j == s) {
      if (mask == full) emit();
      return;
    }
    const int last = hi - (s - 1 - j);
    // An untouched block can only be reached by a cell <= (its rightmost
    // cell)+1; cells are placed left to right, so once t passes the smallest
    // such limit among untouched blocks the subtree is dead.
    int limit = 32767;
    for (uint32_t un = (~mask) & full; un; un &= un - 1) {
      int b = __builtin_ctz(un);
      if (bmax[b] + 1 < limit) limit = bmax[b] + 1;
    }
    for (int t = start; t <= last; ++t) {
      if (t > limit) return;
      const uint32_t saved = mask;
      for (int i = 0; i < n; ++i) {
        int d = t - c[i];
        if (d >= -1 && d <= 1) mask |= (1u << p[i]);
      }
      T[j] = static_cast<int16_t>(t);
      rec(j + 1, t + 1);
      mask = saved;
    }
  }

  int lab[2 * MAXC];
  int find(int x) {
    while (lab[x] != x) {
      lab[x] = lab[lab[x]];
      x = lab[x];
    }
    return x;
  }
  void unite(int a, int b) {
    int ra = find(a), rb = find(b);
    if (ra != rb) lab[ra] = rb;
  }

  void emit() {
    const int tot = nb + s;
    for (int i = 0; i < tot; ++i) lab[i] = i;
    for (int j = 0; j < s; ++j) {
      for (int i = 0; i < n; ++i) {
        int d = T[j] - c[i];
        if (d >= -1 && d <= 1) unite(p[i], nb + j);
      }
    }
    for (int j = 0; j + 1 < s; ++j) {
      if (T[j + 1] - T[j] <= 1) unite(nb + j, nb + j + 1);
    }
    Key k = blank_key();
    k.n = static_cast<uint8_t>(s);
    int canon[2 * MAXC];
    for (int i = 0; i < tot; ++i) canon[i] = -1;
    int next = 0;
    for (int j = 0; j < s; ++j) {
      k.c[j] = static_cast<int16_t>(T[j] - T[0]);
      int r = find(nb + j);
      if (canon[r] < 0) canon[r] = next++;
      k.p[j] = static_cast<uint8_t>(canon[r]);
    }
    add_checked((*out)[k], cnt);
  }
};

// Count king-connected configurations of a stack of rows with the given sizes
// (bottom to top), modulo horizontal translation.
u128 count_stack(const std::vector<int>& sizes) {
  int total = 0;
  for (int s : sizes) {
    if (s > MAXC) die("row size exceeds MAXC");
    total += s;
  }
  const int M = total + 1;  // safe window: a connected C-cell king set spans < C

  StateMap states;
  {
    const int s0 = sizes[0];
    int16_t cells[MAXC];
    cells[0] = 0;
    // combinations(range(1, M+1), s0-1)
    std::vector<int> idx(s0 - 1);
    for (int i = 0; i < s0 - 1; ++i) idx[i] = i + 1;
    while (true) {
      if (s0 == 1) {
        Key k = blank_key();
        k.n = 1;
        add_checked(states[k], 1);
        break;
      }
      for (int i = 0; i < s0 - 1; ++i) cells[i + 1] = static_cast<int16_t>(idx[i]);
      Key k = blank_key();
      k.n = static_cast<uint8_t>(s0);
      uint8_t part[MAXC];
      row_partition(cells, s0, part);
      for (int i = 0; i < s0; ++i) {
        k.c[i] = cells[i];
        k.p[i] = part[i];
      }
      add_checked(states[k], 1);
      // next combination of (s0-1) from [1..M]
      int i = s0 - 2;
      while (i >= 0 && idx[i] == M - (s0 - 2 - i)) --i;
      if (i < 0) break;
      ++idx[i];
      for (int j = i + 1; j < s0 - 1; ++j) idx[j] = idx[j - 1] + 1;
    }
  }

  for (size_t r = 1; r < sizes.size(); ++r) {
    const int s = sizes[r];
    StateMap next;
    Expand e;
    e.out = &next;
    e.s = s;
    for (const auto& kv : states) {
      const Key& k = kv.first;
      e.c = k.c;
      e.p = k.p;
      e.n = k.n;
      int nb = 0;
      for (int i = 0; i < k.n; ++i) nb = std::max(nb, static_cast<int>(k.p[i]) + 1);
      e.nb = nb;
      e.lo = k.c[0] - M;
      e.hi = k.c[k.n - 1] + M;
      e.cnt = kv.second;
      e.run();
    }
    states.swap(next);
  }

  u128 tot = 0;
  for (const auto& kv : states) {
    int nb = 0;
    for (int i = 0; i < kv.first.n; ++i)
      nb = std::max(nb, static_cast<int>(kv.first.p[i]) + 1);
    if (nb == 1) add_checked(tot, kv.second);
  }
  return tot;
}

// ------------------------------------------------------------- compositions
void comp_rec(std::vector<std::vector<int>>& out, std::vector<int>& vec, int left) {
  if (left == 0) {
    if (!vec.empty()) out.push_back(vec);
    return;
  }
  for (int s = 2; s <= left + 1; ++s) {
    vec.push_back(s);
    comp_rec(out, vec, left - (s - 1));
    vec.pop_back();
  }
}
std::vector<std::vector<int>> compositions(int k) {
  std::vector<std::vector<int>> out;
  std::vector<int> vec;
  comp_rec(out, vec, k);
  return out;
}

std::vector<int> rev(const std::vector<int>& v) {
  return std::vector<int>(v.rbegin(), v.rend());
}

}  // namespace

int main(int argc, char** argv) {
  int K = 4;
  int threads = 0;
  bool rev_memo = true;
  std::vector<std::string> pos;
  for (int i = 1; i < argc; ++i) {
    std::string a = argv[i];
    if (a == "--no-rev-memo") rev_memo = false;
    else pos.push_back(a);
  }
  if (!pos.empty()) K = std::atoi(pos[0].c_str());
  if (pos.size() > 1) threads = std::atoi(pos[1].c_str());
  if (threads <= 0) {
    unsigned hw = std::thread::hardware_concurrency();
    threads = static_cast<int>(hw ? std::min(hw, 10u) : 1u);
  }

  char extra[128];
  std::snprintf(extra, sizeof extra, "K=%d threads=%d rev_memo=%d", K, threads,
                rev_memo ? 1 : 0);
  obs::Reporter rep("severance_w1", 0, extra);

  for (int k = 1; k <= K; ++k) {
    const auto comps = compositions(k);

    // Each composition needs four stacks. Up/down mirror symmetry makes
    // count_stack(sizes) == count_stack(reverse(sizes)) (the same symmetry the
    // reference's boundary() invokes), so canonicalize by reversal and compute
    // each distinct stack once. --no-rev-memo turns the canonicalization off.
    auto stacks_for = [&](const std::vector<int>& v) {
      std::vector<std::vector<int>> s(4);
      s[0].push_back(1);
      for (int x : v) s[0].push_back(x);
      s[0].push_back(1);                                    // interior
      s[1].push_back(1);
      for (int x : rev(v)) s[1].push_back(x);               // boundary bottom
      s[2].push_back(1);
      for (int x : v) s[2].push_back(x);                    // boundary top
      s[3] = v;                                             // pure
      return s;
    };
    auto canon = [&](std::vector<int> s) {
      if (rev_memo) {
        std::vector<int> r = rev(s);
        if (r < s) return r;
      }
      return s;
    };

    std::vector<std::vector<int>> jobs;
    std::map<std::vector<int>, size_t> seen;
    for (const auto& v : comps) {
      for (const auto& s : stacks_for(v)) {
        std::vector<int> cs = canon(s);
        if (seen.find(cs) == seen.end()) {
          seen[cs] = jobs.size();
          jobs.push_back(cs);
        }
      }
    }
    // Longest-processing-time-ish: the heavy stacks (most cells, biggest row)
    // start first so the tail is short.
    std::vector<size_t> order(jobs.size());
    for (size_t i = 0; i < order.size(); ++i) order[i] = i;
    auto cost = [&](const std::vector<int>& s) {
      long long t = 0, mx = 0;
      for (int x : s) { t += x; mx = std::max<long long>(mx, x); }
      return t * 100 + mx;
    };
    std::sort(order.begin(), order.end(), [&](size_t a, size_t b) {
      return cost(jobs[a]) > cost(jobs[b]);
    });

    std::vector<u128> res(jobs.size(), 0);
    std::vector<char> done(jobs.size(), 0);
    std::mutex mu;
    size_t nextIdx = 0, ndone = 0;
    auto worker = [&]() {
      while (true) {
        size_t i;
        {
          std::lock_guard<std::mutex> g(mu);
          if (nextIdx >= order.size()) return;
          i = order[nextIdx++];
        }
        u128 w = count_stack(jobs[i]);
        {
          std::lock_guard<std::mutex> g(mu);
          res[i] = w;
          done[i] = 1;
          ++ndone;
          char ex[64];
          std::snprintf(ex, sizeof ex, "k=%d stacks=%zu", k, order.size());
          rep.beat(static_cast<double>(ndone), ex);
        }
      }
    };
    std::vector<std::thread> pool;
    for (int t = 0; t < threads; ++t) pool.emplace_back(worker);
    for (auto& t : pool) t.join();

    for (const auto& v : comps) {
      std::string line;
      for (size_t i = 0; i < v.size(); ++i) {
        if (i) line += ",";
        line += std::to_string(v[i]);
      }
      for (const auto& s : stacks_for(v)) {
        line += "\t";
        line += to_dec(res[seen[canon(s)]]);
      }
      std::printf("%s\n", line.c_str());
    }
    std::fflush(stdout);
    char ex[96];
    std::snprintf(ex, sizeof ex, "level=%d comps=%zu stacks=%zu", k, comps.size(),
                  jobs.size());
    rep.beat(static_cast<double>(ndone), ex, true);
  }

  rep.done("");
  return 0;
}
