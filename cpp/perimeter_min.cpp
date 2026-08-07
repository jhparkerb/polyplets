// Minimum-site-perimeter enumerator: fixed animals near the ISOPERIMETRIC end
// of the perimeter range, by complementation rather than by growth.
//
//   perimeter_min {square4|square8} PMAX RMAX  ->  lines "n p count"
//
// cpp/perimeter_defect.cpp grades the same table A(n,p) from the other end,
// k = pmax(n) - p, where the extremal animals are STICKS and a defect-budgeted
// Redelmeier DFS is exact because the defect is monotone under cell addition.
// Neither of those holds here.  At the minimum-perimeter end the extremal
// animals are BALLS of the adjacency metric, and p - pmin(n) is NOT monotone
// under cell addition (adding a cell can lower it), so no growth prune exists.
//
// WHAT REPLACES THE PRUNE.  Near-minimal animals are FAT: they fill their own
// bounding box up to a few cells, so they are cheap to reach by complementation
// -- enumerate boxes, then remove small subsets -- which costs sum_r C(M, r)
// instead of anything exponential in n.  Concretely, writing pbox(B) for the
// site perimeter of the fully-filled box B and nmax(p) = max{|B| : pbox(B)<=p}:
//
//   (H1)  every animal whose frame bounding box is B has p >= pbox(B).
//
// Given (H1), an animal with perimeter p and area n = nmax(p) - i sits in a box
// with pbox <= p, hence |B| <= nmax(p), hence its removal count is
// |B| - n <= nmax(p) - n = i.  So enumerating all boxes with pbox <= PMAX and
// all removals of size <= RMAX yields EVERY animal with perimeter <= PMAX and
// area deficit i <= RMAX -- the output is complete on exactly that domain, and
// on nothing more.  Animals with a larger deficit are missed BY DESIGN; the
// header line of the output states the domain so a consumer cannot forget it.
//
// (H1) is a hypothesis, not a theorem, so it is not trusted: every animal this
// program emits is checked against pbox at runtime (a violation aborts), and
// scripts/perimeter_min_gate.sh runs the whole thing with RMAX = unbounded on
// small boxes, where it degenerates to a complete brute force, and compares it
// cell for cell against build/g2's --siteperim census.  A (H1) violation would
// show up there as a missing animal.
//
// THE ROTATED FRAME.  On square8 (king) the fat shapes are L-infinity balls,
// i.e. filled boxes, and the frame is the plain (x,y) one.  On square4 (rook)
// they are L-1 balls -- DIAMONDS -- which do not fill any (x,y) box, and the
// complement trick would enumerate half-empty boxes and die.  So square4 is
// worked in the rotated frame u = x+y, v = x-y, where the four rook neighbours
// become the four DIAGONAL neighbours and every cell carries u+v even.  A
// diamond of radius r is then exactly the parity-restricted (2r+1)x(2r+1) box:
// full again, and the same code runs.  The map is a bijection onto the even
// sublattice ((u,v) -> ((u+v)/2, (u-v)/2)), so nothing is lost or double
// counted.  Both parity classes of a box must be enumerated: translating a
// general animal to umin = vmin = 0 leaves u+v congruent to either 0 or 1.
//
// Transposing the frame box is a reflection in (x,y) on both lattices and fixed
// animals are reflection-symmetric as a population, so only W <= H is walked
// and W < H is counted twice.
//
// COST is sum over boxes of sum_{r<=RMAX} C(M,r) nodes, each O(1) amortised
// (perimeter and bounding-box occupancy are maintained incrementally across the
// removal DFS) plus a u128 flood fill for connectivity.  square8 PMAX=40
// RMAX=6 is ~1e9 nodes; the box loop is threaded.

#include <atomic>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <map>
#include <mutex>
#include <string>
#include <thread>
#include <vector>

#include "obs.h"

using u64 = std::uint64_t;
using u128 = unsigned __int128;

struct Offset { int du, dv; };

// square8 in the plain frame: the 8 king neighbours.
static constexpr Offset kKing[] = {{-1,-1},{0,-1},{1,-1},{-1,0},
                                   {1,0},{-1,1},{0,1},{1,1}};
// square4 in the rotated frame: the 4 rook neighbours become the 4 diagonals.
static constexpr Offset kDiag[] = {{-1,-1},{1,-1},{-1,1},{1,1}};

static constexpr int kMaxCells = 128;          // u128 connectivity mask

struct BoxResult {
  // (n, p) -> count, already multiplied by the transpose factor
  std::map<std::pair<int,int>, long long> tally;
  long long nodes = 0, emitted = 0;
  int violations = 0;                          // (H1) failures
};

struct BoxRun {
  int W, H, parity, mult, rmax;
  const Offset* off;
  int noff;

  BoxRun(int W_, int H_, int parity_, int mult_, int rmax_,
         const Offset* off_, int noff_)
      : W(W_), H(H_), parity(parity_), mult(mult_), rmax(rmax_),
        off(off_), noff(noff_) {}

  // frame geometry, expanded by one ring so neighbours are always in range
  int EW = 0, EH = 0;
  std::vector<int> cellPos;                    // cell index -> expanded pos
  std::vector<std::vector<int>> nbrPos;        // cell index -> neighbour posns
  std::vector<u128> nbrIdx;                    // cell index -> in-box nbr mask
  std::vector<int> cellU, cellV;
  int M = 0;

  std::vector<int> cnt;                        // expanded pos -> animal nbrs
  std::vector<char> inAnimal;
  std::vector<int> occU, occV;                 // occupied cells per row/column
  int perim = 0;
  int pbox = 0;
  u128 remaining = 0;

  BoxResult res;

  int pos(int u, int v) const { return (v + 1) * EW + (u + 1); }

  bool build() {
    EW = W + 2; EH = H + 2;
    if (EW * EH > 4096) return false;
    for (int v = 0; v < H; ++v)
      for (int u = 0; u < W; ++u) {
        // parity < 0 means "no sublattice filter" (square8, plain frame);
        // 0/1 select a class of the rotated square4 frame, where every cell
        // carries u+v of one fixed parity.
        if (parity >= 0 && ((u + v) & 1) != parity) continue;
        cellU.push_back(u); cellV.push_back(v);
        cellPos.push_back(pos(u, v));
        ++M;
      }
    if (M == 0 || M > kMaxCells) return false;
    // the filled box must actually span W x H, else this (W,H,parity) is not a
    // legal frame bounding box and every animal in it is counted elsewhere
    bool u0 = false, u1 = false, v0 = false, v1 = false;
    for (int i = 0; i < M; ++i) {
      if (cellU[i] == 0) u0 = true;
      if (cellU[i] == W - 1) u1 = true;
      if (cellV[i] == 0) v0 = true;
      if (cellV[i] == H - 1) v1 = true;
    }
    if (!(u0 && u1 && v0 && v1)) return false;

    std::vector<int> posToIdx(EW * EH, -1);
    for (int i = 0; i < M; ++i) posToIdx[cellPos[i]] = i;

    nbrPos.resize(M); nbrIdx.assign(M, 0);
    for (int i = 0; i < M; ++i) {
      int u = cellU[i], v = cellV[i];
      for (int d = 0; d < noff; ++d) {
        int nu = u + off[d].du, nv = v + off[d].dv;
        if (nu < -1 || nu > W || nv < -1 || nv > H) continue;
        int q = pos(nu, nv);
        nbrPos[i].push_back(q);
        int j = posToIdx[q];
        if (j >= 0) nbrIdx[i] |= (u128)1 << j;
      }
    }

    cnt.assign(EW * EH, 0);
    inAnimal.assign(EW * EH, 0);
    occU.assign(W, 0); occV.assign(H, 0);
    for (int i = 0; i < M; ++i) {
      inAnimal[cellPos[i]] = 1;
      ++occU[cellU[i]]; ++occV[cellV[i]];
      for (int q : nbrPos[i]) ++cnt[q];
    }
    perim = 0;
    for (int q = 0; q < EW * EH; ++q)
      if (cnt[q] > 0 && !inAnimal[q]) ++perim;
    pbox = perim;
    remaining = (M == 128) ? ~(u128)0 : (((u128)1 << M) - 1);
    return true;
  }

  bool spans() const {
    return occU[0] && occU[W - 1] && occV[0] && occV[H - 1];
  }

  bool connected() const {
    if (remaining == 0) return false;
    int first = 0;
    while (!((remaining >> first) & 1)) ++first;
    u128 seen = (u128)1 << first, frontier = seen;
    while (frontier) {
      u128 next = 0;
      u128 f = frontier;
      while (f) {
        int i = 0;
        u128 low = f & (~f + 1);
        while (!((low >> i) & 1)) ++i;
        next |= nbrIdx[i];
        f ^= low;
      }
      next &= remaining & ~seen;
      seen |= next;
      frontier = next;
    }
    return seen == remaining;
  }

  void remove(int i) {
    int p0 = cellPos[i];
    inAnimal[p0] = 0;
    remaining &= ~((u128)1 << i);
    --occU[cellU[i]]; --occV[cellV[i]];
    if (cnt[p0] > 0) ++perim;                 // i itself becomes perimeter
    for (int q : nbrPos[i]) {
      if (--cnt[q] == 0 && !inAnimal[q]) --perim;
    }
  }

  void restore(int i) {
    int p0 = cellPos[i];
    for (int q : nbrPos[i]) {
      if (cnt[q]++ == 0 && !inAnimal[q]) ++perim;
    }
    if (cnt[p0] > 0) --perim;
    inAnimal[p0] = 1;
    remaining |= (u128)1 << i;
    ++occU[cellU[i]]; ++occV[cellV[i]];
  }

  void record(int r) {
    ++res.nodes;
    if (!spans()) return;
    int n = M - r;
    if (n <= 0) return;
    // Connectivity FIRST: (H1) is a claim about animals, and a disconnected
    // cell set can sit inside a box with a smaller perimeter than the box
    // (two opposite corners of a 3x3 have p=15 against the box's 16) without
    // saying anything about the hypothesis.
    if (!connected()) return;
    if (perim < pbox) {                               // (H1) check
      ++res.violations;
      if (res.violations <= 8) {
        std::fprintf(stderr, "event=h1 W=%d H=%d parity=%d n=%d p=%d pbox=%d "
                     "cells=", W, H, parity, n, perim, pbox);
        for (int i = 0; i < M; ++i)
          if ((remaining >> i) & 1)
            std::fprintf(stderr, "(%d,%d)", cellU[i], cellV[i]);
        std::fprintf(stderr, "\n");
      }
      return;
    }
    res.tally[{n, perim}] += mult;
    ++res.emitted;
  }

  void dfs(int start, int r) {
    record(r);
    if (r == rmax) return;
    for (int i = start; i < M; ++i) {
      remove(i);
      dfs(i + 1, r + 1);
      restore(i);
    }
  }

  void run() { dfs(0, 0); }
};

int main(int argc, char** argv) {
  if (argc < 4) {
    std::fprintf(stderr,
                 "usage: perimeter_min {square4|square8} PMAX RMAX [--threads T]\n"
                 "  RMAX < 0 means unbounded (complete brute force per box)\n");
    return 2;
  }
  std::string lat = argv[1];
  int PMAX = std::atoi(argv[2]);
  int RMAX = std::atoi(argv[3]);
  int threads = 1;
  for (int a = 4; a < argc; ++a)
    if (!std::strcmp(argv[a], "--threads") && a + 1 < argc)
      threads = std::atoi(argv[++a]);

  const Offset* off; int noff; std::vector<int> parities;
  if (lat == "square8")      { off = kKing; noff = 8; parities = {-1}; }
  else if (lat == "square4") { off = kDiag; noff = 4; parities = {0, 1}; }
  else { std::fprintf(stderr, "unknown lattice %s\n", lat.c_str()); return 2; }

  obs::Reporter rep("perimeter_min", 0,
                    "lattice=" + lat + " pmax=" + std::to_string(PMAX) +
                    " rmax=" + std::to_string(RMAX));

  // Collect the box list first: for fixed W, pbox is nondecreasing in H, so
  // stop at the first H that overshoots.  pbox is MEASURED off the filled box
  // (BoxRun::build), never a formula, so the box loop makes no lattice-specific
  // assumption about what the isoperimetric shape is.
  struct Job { int W, H, parity, mult; };
  std::vector<Job> jobs;
  for (int W = 1;; ++W) {
    bool anyW = false;
    for (int H = W;; ++H) {
      bool anyH = false;
      for (int par : parities) {
        BoxRun probe(W, H, par, 1, 0, off, noff);
        if (!probe.build()) continue;
        if (probe.pbox > PMAX) continue;
        anyH = anyW = true;
        jobs.push_back({W, H, par, W == H ? 1 : 2});
      }
      if (!anyH) break;
    }
    if (!anyW) break;
  }
  std::fprintf(stderr, "event=plan job=perimeter_min boxes=%zu\n", jobs.size());

  std::map<std::pair<int,int>, long long> total;
  std::mutex mu;
  std::atomic<size_t> next{0};
  std::atomic<long long> nodes{0}, emitted{0};
  std::atomic<int> violations{0};

  auto worker = [&]() {
    for (;;) {
      size_t j = next.fetch_add(1);
      if (j >= jobs.size()) break;
      const Job& job = jobs[j];
      BoxRun r(job.W, job.H, job.parity, job.mult,
               RMAX < 0 ? kMaxCells : RMAX, off, noff);
      if (!r.build()) continue;
      if (RMAX < 0) r.rmax = r.M;
      r.run();
      std::lock_guard<std::mutex> g(mu);
      for (auto& kv : r.res.tally) total[kv.first] += kv.second;
      nodes += r.res.nodes; emitted += r.res.emitted;
      violations += r.res.violations;
      rep.beat((double)(j + 1), "boxes=" + std::to_string(jobs.size()) +
                                " nodes=" + std::to_string(nodes.load()));
    }
  };

  std::vector<std::thread> pool;
  for (int t = 1; t < threads; ++t) pool.emplace_back(worker);
  worker();
  for (auto& t : pool) t.join();

  std::printf("# perimeter_min lattice=%s pmax=%d rmax=%d git=%s\n",
              lat.c_str(), PMAX, RMAX, GIT_REV);
  std::printf("# COMPLETE only for animals with perimeter <= %d AND area\n"
              "# deficit i = nmax(p) - n at most %d. Rows outside that domain\n"
              "# are present but partial -- do not read them as counts.\n",
              PMAX, RMAX);
  for (auto& kv : total)
    std::printf("%d %d %lld\n", kv.first.first, kv.first.second, kv.second);

  if (violations > 0) {
    std::fprintf(stderr,
                 "event=error job=perimeter_min hypothesis=H1 violations=%d "
                 "-- an animal beat its own filled box's perimeter, so the "
                 "completeness argument is void\n", violations.load());
    rep.done("result=fail");
    return 1;
  }
  rep.done("result=ok", "boxes=" + std::to_string(jobs.size()) +
                        " nodes=" + std::to_string(nodes.load()) +
                        " emitted=" + std::to_string(emitted.load()) +
                        " cells=" + std::to_string(total.size()));
  return 0;
}
