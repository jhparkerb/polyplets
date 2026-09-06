// The dmirror spine split, in C++ and with a cell budget -- the enumerator
// that reaches the levels the grand-form test needs.
//
// WHY.  results/symmetry-classes.md counts diagonal-mirror animals apart by
// which ground-state spine they sit on, and finds each family separately
// linear at c_2 where the summed family is quadratic.  The next cumulant, c_3,
// is what would distinguish "has the grand form" from "agrees with it to
// second order", and it needs level k = 3 pinned on both parities: S = 16 even
// and S = 17 odd.  experiments/dmirror_spine_split.py is a hook transfer
// matrix in pure Python and took 6 h 38 min for S = 14 alone.
//
// THE TWO CHANGES.  (1) C++.  (2) A CELL BUDGET: only cells with n <= S + KMAX
// are wanted, n never decreases along the sweep, and each hook a state enters
// costs at least one cell -- so a partial with n over budget is dropped, and
// the next hook's occupancies are enumerated in increasing cell count and cut
// off at the remaining budget rather than run over all 2^(S-k) of them.  At
// the levels this is for, k <= 6, that turns the inner loop from tens of
// thousands of masks into hundreds.
//
// The geometry is computed from cell coordinates by brute force, exactly as
// the Python does, and for the same reason: the first version of that file
// collapsed each mirror pair {(k,k+p), (k+p,k)} to one node, which counts
// disconnected animals as connected, and only the coordinate-level adjacency
// caught it.  A mirror pair is one POSITION and two CELLS.
//
// GATE, fail-closed and run before any new S: the histogram summed over corner
// counts must reproduce the banked `dmirror_strip` rows of
// results/sym_counts.txt cell for cell, over every S the gate covers.  Those
// rows come from cpp/sym/symtm.cpp, which shares no code with this.  The gate
// runs UNCAPPED so it checks every banked cell at those S, not just the low
// levels.
//
// Usage:
//     build/dmirror_spine --gate              # S = 2..11 uncapped, exit
//     build/dmirror_spine S [KMAX]            # one S, cells n <= S+KMAX
//
// Output is one line per (S, k): total, main, anti, neither -- "neither" is
// nonzero only where the split is undefined (S <= 2k+1) and is reported
// rather than assumed away.
//
// Target: ayr or dalby.

#include <algorithm>
#include <array>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <unordered_map>
#include <vector>

#include "obs.h"

namespace {

using u8 = uint8_t;
using u32 = uint32_t;
using u64 = uint64_t;

constexpr int MAXS = 24;
constexpr int MAXCELL = 2 * MAXS;  // cells in a hook: 2*(S-k)-1

// ------------------------------------------------------------------ geometry
//
// Hook k has positions 0..L-1 with L = S-k.  Position 0 is the corner (k,k),
// one cell; position p >= 1 is the mirror pair {(k,k+p), (k+p,k)}, two cells.
struct Hook {
  int L = 0;
  std::vector<int> pos;                      // position of each cell
  std::vector<std::pair<int, int>> xy;       // its coordinates
  std::vector<std::pair<int, int>> within;   // edges inside the hook
  std::vector<std::pair<int, int>> between;  // edges to the next hook
  std::vector<u8> cellsOfMask;               // cells an occupancy costs
  std::vector<std::vector<u32>> byCells;     // masks grouped by that cost
  std::vector<u8> touchesEdge;               // mask reaches coordinate S-1
};

inline bool adjacent(std::pair<int, int> a, std::pair<int, int> b) {
  return a != b && std::abs(a.first - b.first) <= 1 &&
         std::abs(a.second - b.second) <= 1;
}

std::vector<Hook> geometry(int S) {
  std::vector<Hook> hs(S);
  for (int k = 0; k < S; ++k) {
    Hook& h = hs[k];
    h.L = S - k;
    h.pos.push_back(0);
    h.xy.push_back({k, k});
    for (int p = 1; p < h.L; ++p) {
      h.pos.push_back(p);
      h.xy.push_back({k, k + p});
      h.pos.push_back(p);
      h.xy.push_back({k + p, k});
    }
  }
  for (int k = 0; k < S; ++k) {
    Hook& h = hs[k];
    const int n = static_cast<int>(h.xy.size());
    for (int a = 0; a < n; ++a)
      for (int b = a + 1; b < n; ++b)
        if (adjacent(h.xy[a], h.xy[b])) h.within.push_back({a, b});
    if (k + 1 < S) {
      const Hook& g = hs[k + 1];
      const int m = static_cast<int>(g.xy.size());
      for (int a = 0; a < n; ++a)
        for (int b = 0; b < m; ++b)
          if (adjacent(h.xy[a], g.xy[b])) h.between.push_back({a, b});
    }
    const u32 nmask = 1u << h.L;
    h.cellsOfMask.assign(nmask, 0);
    h.touchesEdge.assign(nmask, 0);
    h.byCells.assign(2 * h.L + 1, {});
    for (u32 occ = 1; occ < nmask; ++occ) {
      int c = 0;
      bool edge = false;
      for (int i = 0; i < n; ++i)
        if ((occ >> h.pos[i]) & 1) {
          ++c;
          if (std::max(h.xy[i].first, h.xy[i].second) == S - 1) edge = true;
        }
      h.cellsOfMask[occ] = static_cast<u8>(c);
      h.touchesEdge[occ] = edge ? 1 : 0;
      h.byCells[c].push_back(occ);
    }
  }
  return hs;
}

// ------------------------------------------------------------------- the DP
//
// A state is one hook's occupancy together with the component labelling of its
// occupied cells, whether the animal has reached coordinate S-1 yet, and the
// two statistics being accumulated: cells so far and occupied corners so far.
// Corners are what separate the spines -- the main diagonal is exactly the set
// of hook corners.
struct State {
  u32 occ = 0;
  std::array<u64, 5> lab{};  // 6 bits per occupied cell, first-seen order
  u8 touched = 0;
  u8 n = 0;
  u8 corners = 0;

  bool operator==(const State& o) const {
    return occ == o.occ && lab == o.lab && touched == o.touched && n == o.n &&
           corners == o.corners;
  }
};

struct StateHash {
  size_t operator()(const State& s) const {
    u64 h = 1469598103934665603ull;
    auto mix = [&h](u64 v) { h ^= v; h *= 1099511628211ull; };
    mix(s.occ);
    for (u64 v : s.lab) mix(v);
    mix(s.touched | (u64(s.n) << 8) | (u64(s.corners) << 16));
    return static_cast<size_t>(h);
  }
};

// Six bits per cell, ten cells per word, five words -- 50 slots against the
// 48 cells a hook can hold at MAXS, and 63 labels against the 48 components
// those cells can form.  Four bits was not enough: hook 0 of an S x S board
// has 2S-1 cells and a position p >= 2 contributes its two mirror cells as
// SEPARATE components, so an alternating occupancy reaches ~S components --
// nineteen at S = 20, and sixteen from S = 16 up.  See LABEL WIDTH below.
inline void setLab(std::array<u64, 5>& a, int i, int v) {
  a[i / 10] |= (u64(v & 63) << (6 * (i % 10)));
}
inline int getLab(const std::array<u64, 5>& a, int i) {
  return static_cast<int>((a[i / 10] >> (6 * (i % 10))) & 63);
}

// The largest number of components any one hook has carried this run.  The
// four-bit field held 16 labels and aliased the 17th onto the first, so this
// is the number that says whether a four-bit run was sound: at most 16 and it
// was, 17 or more and it silently merged two components.
int g_maxComp = 0;

struct DSU {
  int p[MAXCELL];
  void init(int n) { for (int i = 0; i < n; ++i) p[i] = i; }
  int find(int x) {
    while (p[x] != x) x = p[x] = p[p[x]];
    return x;
  }
  void unite(int a, int b) {
    a = find(a);
    b = find(b);
    if (a != b) p[std::max(a, b)] = std::min(a, b);
  }
};

// Label one hook's occupied cells, honouring components inherited from the
// hook below.  Returns the number of distinct inherited components that
// actually arrived -- the caller compares it against the number that were
// live, and a shortfall means a component stranded.
int labelHook(const Hook& h, u32 occ, const int* inhCell, const int* inhLab,
              int nInh, std::array<u64, 5>& out, int* ncomp) {
  int slot[MAXCELL];
  int m = 0;
  const int n = static_cast<int>(h.xy.size());
  for (int i = 0; i < n; ++i) {
    slot[i] = -1;
    if ((occ >> h.pos[i]) & 1) slot[i] = m++;
  }
  DSU d;
  d.init(m);
  for (auto& e : h.within)
    if (slot[e.first] >= 0 && slot[e.second] >= 0)
      d.unite(slot[e.first], slot[e.second]);
  // Cells inheriting the same old label are one component.
  int firstOf[64];
  for (int i = 0; i < 64; ++i) firstOf[i] = -1;
  int arrived = 0;
  for (int t = 0; t < nInh; ++t) {
    const int c = slot[inhCell[t]];
    if (c < 0) continue;
    const int L = inhLab[t];
    if (firstOf[L] < 0) {
      firstOf[L] = c;
      ++arrived;
    } else {
      d.unite(firstOf[L], c);
    }
  }
  int root2lab[MAXCELL];
  for (int i = 0; i < m; ++i) root2lab[i] = -1;
  int nl = 0;
  out = {};
  for (int i = 0; i < m; ++i) {
    const int r = d.find(i);
    if (root2lab[r] < 0) root2lab[r] = nl++;
    // LABEL WIDTH.  Six bits hold labels 0..63, so 64 components fit and the
    // 65th would alias onto label 0 and silently merge two components.  The
    // test below is one step tighter than that -- it refuses at 64, before
    // anything is lost -- and the four-bit version it replaces was tight in
    // the same way: it refused at 16 components, which four bits still hold,
    // so its firing at S = 20 was a refusal and not a corruption.  Kept
    // fail-closed rather than argued away, because the four-bit version came
    // with the argument ("the cell budget keeps a hook far below that") and
    // the argument was wrong.
    if (nl > 63) {
      std::fprintf(stderr,
                   "FATAL: %d components in one hook exceeds the 6-bit label "
                   "field; raise the packing before trusting any count\n", nl);
      std::exit(3);
    }
    setLab(out, i, root2lab[r]);
  }
  *ncomp = nl;
  if (nl > g_maxComp) g_maxComp = nl;
  return arrived;
}

// hist[(n, corners)] over animals whose bounding box is exactly S x S.
// cap is the largest n wanted; 0 means no cap.
std::unordered_map<u32, u64> sweep(int S, int cap, obs::Reporter* rep) {
  const std::vector<Hook> hs = geometry(S);
  std::unordered_map<u32, u64> hist;  // key = n * 64 + corners

  std::unordered_map<State, u64, StateHash> cur, nxt;
  {
    const Hook& h = hs[0];
    for (u32 occ = 1; occ < (1u << h.L); ++occ) {
      const int cells = h.cellsOfMask[occ];
      if (cap && cells > cap) continue;
      State s;
      s.occ = occ;
      int nc = 0;
      labelHook(h, occ, nullptr, nullptr, 0, s.lab, &nc);
      s.touched = h.touchesEdge[occ];
      s.n = static_cast<u8>(cells);
      s.corners = static_cast<u8>(occ & 1);
      cur[s] += 1;
    }
  }

  for (int k = 0; k < S; ++k) {
    const Hook& h = hs[k];
    nxt.clear();
    for (const auto& kv : cur) {
      const State& s = kv.first;
      const u64 mult = kv.second;
      // How many components are live in this hook?
      int m = 0, ncomp = 0;
      const int n = static_cast<int>(h.xy.size());
      int slot[MAXCELL];
      for (int i = 0; i < n; ++i) {
        slot[i] = -1;
        if ((s.occ >> h.pos[i]) & 1) {
          slot[i] = m;
          ncomp = std::max(ncomp, getLab(s.lab, m) + 1);
          ++m;
        }
      }
      if (ncomp == 1 && s.touched)
        hist[u32(s.n) * 64u + s.corners] += mult;  // the animal ends here
      if (k + 1 >= S) continue;

      const Hook& g = hs[k + 1];
      const int budget = cap ? cap - s.n : (2 * g.L);
      if (budget <= 0) continue;
      const int top = std::min<int>(budget, 2 * g.L);
      int inhCell[MAXCELL], inhLab[MAXCELL];
      for (int c = 1; c <= top; ++c) {
        for (const u32 occ2 : g.byCells[c]) {
          int nInh = 0;
          for (auto& e : h.between) {
            if (slot[e.first] < 0) continue;
            if (!((occ2 >> g.pos[e.second]) & 1)) continue;
            inhCell[nInh] = e.second;
            inhLab[nInh] = getLab(s.lab, slot[e.first]);
            ++nInh;
          }
          State t;
          int nc2 = 0;
          const int arrived =
              labelHook(g, occ2, inhCell, inhLab, nInh, t.lab, &nc2);
          if (arrived != ncomp) continue;  // a component stranded
          t.occ = occ2;
          t.touched = static_cast<u8>(s.touched | g.touchesEdge[occ2]);
          t.n = static_cast<u8>(s.n + c);
          t.corners = static_cast<u8>(s.corners + (occ2 & 1));
          nxt[t] += mult;
        }
      }
    }
    cur.swap(nxt);
    if (rep)
      rep->beat(k + 1, "hook=" + std::to_string(k) + " states=" +
                           std::to_string(cur.size()));
  }
  return hist;
}

// ------------------------------------------------------------------- banked
std::unordered_map<u64, u64> banked(const std::string& root) {
  std::unordered_map<u64, u64> out;
  const std::string p = root + "/results/sym_counts.txt";
  FILE* f = std::fopen(p.c_str(), "r");
  if (!f) {
    std::fprintf(stderr, "cannot read %s\n", p.c_str());
    return out;
  }
  char name[64];
  long long S, n, v;
  char line[512];
  while (std::fgets(line, sizeof line, f)) {
    if (std::sscanf(line, "%63s %lld %lld %lld", name, &S, &n, &v) == 4 &&
        std::strcmp(name, "dmirror_strip") == 0)
      out[u64(S) * 1000 + u64(n)] = static_cast<u64>(v);
  }
  std::fclose(f);
  return out;
}

std::string repoRoot(const char* argv0) {
  std::string p(argv0);
  const size_t s = p.find_last_of('/');
  std::string dir = (s == std::string::npos) ? "." : p.substr(0, s);
  return dir + "/..";
}

bool gate(const std::string& root, int smax) {
  const auto bank = banked(root);
  if (bank.empty()) return false;
  int checked = 0;
  bool ok = true;
  for (int S = 2; S <= smax; ++S) {
    const auto hist = sweep(S, 0, nullptr);
    std::unordered_map<u32, u64> byn;
    for (const auto& kv : hist) byn[kv.first / 64] += kv.second;
    for (const auto& kv : byn) {
      const auto it = bank.find(u64(S) * 1000 + kv.first);
      if (it == bank.end()) continue;
      ++checked;
      if (it->second != kv.second) {
        std::printf("  GATE FAILED S=%d n=%u got %llu banked %llu\n", S,
                    kv.first, (unsigned long long)kv.second,
                    (unsigned long long)it->second);
        ok = false;
      }
    }
    // Every banked cell at this S must have been produced, not just agree
    // where produced: a missing cell is a silent undercount.
    for (const auto& b : bank) {
      if (b.first / 1000 != u64(S)) continue;
      const u32 n = static_cast<u32>(b.first % 1000);
      if (byn.find(n) == byn.end() && b.second != 0) {
        std::printf("  GATE FAILED S=%d n=%u banked %llu, not produced\n", S, n,
                    (unsigned long long)b.second);
        ok = false;
      }
    }
  }
  std::printf("gate: %d banked dmirror_strip cells at S <= %d, %s\n", checked,
              smax, ok ? "all reproduced" : "MISMATCH");
  return ok;
}

}  // namespace

int main(int argc, char** argv) {
  if (argc < 2) {
    std::fprintf(stderr, "usage: dmirror_spine --gate | S [KMAX]\n");
    return 2;
  }
  const std::string root = repoRoot(argv[0]);
  if (std::strcmp(argv[1], "--gate") == 0) return gate(root, 11) ? 0 : 1;

  const int S = std::atoi(argv[1]);
  const int kmax = (argc > 2) ? std::atoi(argv[2]) : 6;
  if (S < 2 || S > MAXS) {
    std::fprintf(stderr, "S out of range\n");
    return 2;
  }
  if (!gate(root, std::min(S, 11))) {
    std::fprintf(stderr, "gate failed -- refusing to report\n");
    return 1;
  }

  obs::Reporter rep("dmirror_spine", S,
                    "S=" + std::to_string(S) + " kmax=" + std::to_string(kmax));
  const auto hist = sweep(S, S + kmax, &rep);

  // corners >= S-k is the main spine, corners <= k+1 the anti; the two ranges
  // are disjoint exactly when S >= 2k+2, and anything between them belongs to
  // neither and is reported.
  std::printf("  %-4s %-4s %-14s %-12s %-12s %-9s\n", "S", "k", "total", "main",
              "anti", "neither");
  for (int k = 0; k <= kmax; ++k) {
    const u32 n = static_cast<u32>(S + k);
    u64 tot = 0, main_ = 0, anti = 0;
    for (u32 c = 0; c <= 63; ++c) {
      const auto it = hist.find(n * 64 + c);
      if (it == hist.end()) continue;
      tot += it->second;
      if (static_cast<int>(c) >= S - k) main_ += it->second;
      if (static_cast<int>(c) <= k + 1) anti += it->second;
    }
    std::printf("  %-4d %-4d %-14llu %-12llu %-12llu %-9lld%s\n", S, k,
                (unsigned long long)tot, (unsigned long long)main_,
                (unsigned long long)anti,
                (long long)(tot - main_ - anti),
                (S >= 2 * k + 2) ? "" : "   <== SPLIT UNDEFINED");
    std::fflush(stdout);
  }
  std::printf("  max components in one hook: %d (six bits hold 64; the "
              "four-bit field this replaced held 16, and aliased at 17)\n",
              g_maxComp);
  rep.done("S=" + std::to_string(S) + " kmax=" + std::to_string(kmax) +
           " maxcomp=" + std::to_string(g_maxComp));
  return 0;
}
