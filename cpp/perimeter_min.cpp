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
// removal DFS) plus a bitmask flood fill for connectivity.  square8 PMAX=40
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

// Connectivity mask.  This was an unsigned __int128, which capped a frame at
// 128 cells and so capped the square4 diamond at W=15 -- one term short of the
// j=7 free-removal test.  Four words buys W=17 (145 cells) with room over.
//
// Every operation is bounded by `nw`, the number of words a given frame
// actually uses, so a 113-cell box still touches two words and pays what it
// used to.  The flood fill in connected() is the hot loop and the only reason
// this is hand-rolled rather than a std::bitset.
static constexpr int kMaskWords = 4;
static constexpr int kMaxCells = 64 * kMaskWords;

struct Mask {
  u64 w[kMaskWords] = {0, 0, 0, 0};

  void set(int i)        { w[i >> 6] |= u64(1) << (i & 63); }
  void clear(int i)      { w[i >> 6] &= ~(u64(1) << (i & 63)); }
  bool test(int i) const { return (w[i >> 6] >> (i & 63)) & 1; }

  bool any(int nw) const {
    for (int k = 0; k < nw; ++k) if (w[k]) return true;
    return false;
  }
  bool equals(const Mask& o, int nw) const {
    for (int k = 0; k < nw; ++k) if (w[k] != o.w[k]) return false;
    return true;
  }
  void orWith(const Mask& o, int nw)  { for (int k = 0; k < nw; ++k) w[k] |= o.w[k]; }
  void andNot(const Mask& o, int nw)  { for (int k = 0; k < nw; ++k) w[k] &= ~o.w[k]; }
  void andWith(const Mask& o, int nw) { for (int k = 0; k < nw; ++k) w[k] &= o.w[k]; }

  // index of the lowest set bit; -1 if empty
  int lowest(int nw) const {
    for (int k = 0; k < nw; ++k)
      if (w[k]) return (k << 6) + __builtin_ctzll(w[k]);
    return -1;
  }
  // all M low bits set
  static Mask full(int M) {
    Mask m;
    for (int k = 0; k < kMaskWords; ++k) {
      int bits = M - (k << 6);
      if (bits <= 0) break;
      m.w[k] = (bits >= 64) ? ~u64(0) : ((u64(1) << bits) - 1);
    }
    return m;
  }
};

struct Offset { int du, dv; };

// square8 in the plain frame: the 8 king neighbours.
static constexpr Offset kKing[] = {{-1,-1},{0,-1},{1,-1},{-1,0},
                                   {1,0},{-1,1},{0,1},{1,1}};
// square4 in the rotated frame: the 4 rook neighbours become the 4 diagonals.
static constexpr Offset kDiag[] = {{-1,-1},{1,-1},{-1,1},{1,1}};
// tri6, the 6-neighbour triangular/hex lattice, in axial coordinates -- the
// same offsets g2 uses, so its --siteperim census gates this one too.
static constexpr Offset kTri6[] = {{0,-1},{1,-1},{-1,0},{1,0},{-1,1},{0,1}};

// A HULL is a range on each of a few linear functionals of (u,v). The
// complement trick works only when the lattice's isoperimetric shape is a FULL
// hull, so the functionals are chosen per lattice to make that true:
//
//   square8  balls are L-infinity squares  -> u, v          (a rectangle)
//   square4  balls are L-1 diamonds, which are rectangles in the rotated
//            frame                          -> u, v          (a rectangle)
//   tri6     balls are HEXAGONS, which are no parallelogram in any frame, so a
//            third constraint is needed     -> u, v, u+v     (a hexagon)
//
// Two functionals is the old behaviour exactly; the third is inert unless the
// lattice asks for it.
struct Func { int a, b; };
static constexpr Func kFuncsRect[] = {{1,0},{0,1}};
static constexpr Func kFuncsHex[]  = {{1,0},{0,1},{1,1}};

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
  // Range of the third functional u+v. hex3 == false leaves it inert, which is
  // exactly the old two-functional rectangle.
  bool hex3 = false;
  int slo = 0, shi = 0;

  BoxRun(int W_, int H_, int parity_, int mult_, int rmax_,
         const Offset* off_, int noff_,
         bool hex3_ = false, int slo_ = 0, int shi_ = 0)
      : W(W_), H(H_), parity(parity_), mult(mult_), rmax(rmax_),
        off(off_), noff(noff_), hex3(hex3_), slo(slo_), shi(shi_) {}

  // frame geometry, expanded by one ring so neighbours are always in range
  int EW = 0, EH = 0;
  std::vector<int> cellPos;                    // cell index -> expanded pos
  std::vector<std::vector<int>> nbrPos;        // cell index -> neighbour posns
  std::vector<Mask> nbrIdx;                    // cell index -> in-box nbr mask
  std::vector<int> cellU, cellV;
  int M = 0;
  int nw = 0;                                  // mask words this frame uses
  // A frame that spans and is within PMAX but has more than kMaxCells cells.
  // build() still fills in pbox for it, so the caller can tell an over-mask
  // frame that MATTERS from one that was out of perimeter range anyway.  The
  // old code returned a bare false here, which a sweep could not distinguish
  // from "not a legal frame" -- a silently missing animal.
  bool tooBig = false;

  std::vector<int> cnt;                        // expanded pos -> animal nbrs
  std::vector<char> inAnimal;
  std::vector<int> occU, occV, occS;           // occupied cells per functional value
  int perim = 0;
  int pbox = 0;
  Mask remaining;

  BoxResult res;
  // Perimeter-PRESERVING removals, by removal count. These are the free moves
  // -- the corner staircases -- and their generating function is the per-box
  // factor the whole stable ladder convolves. Kept separately because the
  // aggregate (n,p) table cannot be deconvolved without knowing which box each
  // animal came from.
  std::vector<long long> freeByR;

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
        if (hex3 && (u + v < slo || u + v > shi)) continue;
        cellU.push_back(u); cellV.push_back(v);
        cellPos.push_back(pos(u, v));
        ++M;
      }
    if (M == 0) return false;
    // the filled box must actually span W x H, else this (W,H,parity) is not a
    // legal frame bounding box and every animal in it is counted elsewhere
    bool u0 = false, u1 = false, v0 = false, v1 = false, s0 = false, s1 = false;
    for (int i = 0; i < M; ++i) {
      if (cellU[i] == 0) u0 = true;
      if (cellU[i] == W - 1) u1 = true;
      if (cellV[i] == 0) v0 = true;
      if (cellV[i] == H - 1) v1 = true;
      if (cellU[i] + cellV[i] == slo) s0 = true;
      if (cellU[i] + cellV[i] == shi) s1 = true;
    }
    if (!(u0 && u1 && v0 && v1)) return false;
    if (hex3 && !(s0 && s1)) return false;

    std::vector<int> posToIdx(EW * EH, -1);
    for (int i = 0; i < M; ++i) posToIdx[cellPos[i]] = i;

    nbrPos.resize(M);
    for (int i = 0; i < M; ++i) {
      int u = cellU[i], v = cellV[i];
      for (int d = 0; d < noff; ++d) {
        int nu = u + off[d].du, nv = v + off[d].dv;
        if (nu < -1 || nu > W || nv < -1 || nv > H) continue;
        nbrPos[i].push_back(pos(nu, nv));
      }
    }

    cnt.assign(EW * EH, 0);
    inAnimal.assign(EW * EH, 0);
    occU.assign(W, 0); occV.assign(H, 0); occS.assign(W + H, 0);
    for (int i = 0; i < M; ++i) {
      inAnimal[cellPos[i]] = 1;
      ++occU[cellU[i]]; ++occV[cellV[i]]; ++occS[cellU[i] + cellV[i]];
      for (int q : nbrPos[i]) ++cnt[q];
    }
    perim = 0;
    for (int q = 0; q < EW * EH; ++q)
      if (cnt[q] > 0 && !inAnimal[q]) ++perim;
    pbox = perim;

    // Size verdict last, so pbox is filled in before it is passed judgement on.
    // The caller compares pbox against PMAX and only then decides whether an
    // over-mask frame is a problem or merely out of range.
    if (M > kMaxCells) { tooBig = true; return true; }

    nw = (M + 63) / 64;
    nbrIdx.assign(M, Mask());
    for (int i = 0; i < M; ++i)
      for (int q : nbrPos[i]) {
        int j = posToIdx[q];
        if (j >= 0) nbrIdx[i].set(j);
      }
    remaining = Mask::full(M);
    return true;
  }

  bool spans() const {
    if (!(occU[0] && occU[W - 1] && occV[0] && occV[H - 1])) return false;
    if (hex3 && !(occS[slo] && occS[shi])) return false;
    return true;
  }

  bool connected() const {
    int first = remaining.lowest(nw);
    if (first < 0) return false;
    Mask seen, frontier;
    seen.set(first);
    frontier.set(first);
    while (frontier.any(nw)) {
      Mask next;
      for (int k = 0; k < nw; ++k) {
        u64 f = frontier.w[k];
        while (f) {
          int i = (k << 6) + __builtin_ctzll(f);
          next.orWith(nbrIdx[i], nw);
          f &= f - 1;
        }
      }
      next.andWith(remaining, nw);
      next.andNot(seen, nw);
      seen.orWith(next, nw);
      frontier = next;
    }
    return seen.equals(remaining, nw);
  }

  void remove(int i) {
    int p0 = cellPos[i];
    inAnimal[p0] = 0;
    remaining.clear(i);
    --occU[cellU[i]]; --occV[cellV[i]]; --occS[cellU[i] + cellV[i]];
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
    remaining.set(i);
    ++occU[cellU[i]]; ++occV[cellV[i]]; ++occS[cellU[i] + cellV[i]];
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
          if (remaining.test(i))
            std::fprintf(stderr, "(%d,%d)", cellU[i], cellV[i]);
        std::fprintf(stderr, "\n");
      }
      return;
    }
    res.tally[{n, perim}] += mult;
    ++res.emitted;
    if (perim == pbox) {
      if ((int)freeByR.size() <= r) freeByR.resize(r + 1, 0);
      ++freeByR[r];                      // per box, NOT multiplied by mult
    }
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

  // ONE frame across many cores.  The frame loop in main() is the usual source
  // of parallelism, but --only has a single frame, and at RMAX=7 on 145 cells
  // that frame alone is ~2.4e11 nodes.
  //
  // The decomposition is by the first two removals, which partitions the search
  // exactly: every removal set of size >= 2 has a unique lexicographically
  // first pair (i,j), every set of size 1 a unique i, and the empty set is the
  // root.  So the tasks are
  //
  //     (-1,-1)  the empty removal, records r=0
  //     (i, -1)  records r=1 for that single removal
  //     (i,  j)  i<j: records r=2 and the whole subtree beneath it
  //
  // Depth 2 rather than depth 1 on purpose: the depth-1 shards are wildly
  // uneven (shard 0 alone is ~6% of the tree, capping speedup near 17x),
  // while ~C(M,2) depth-2 shards bring the largest under a percent.
  void runTask(int i, int j) {
    if (i < 0) { record(0); return; }
    remove(i);
    if (j < 0) {
      record(1);
    } else {
      remove(j);
      dfs(j + 1, 2);
      restore(j);
    }
    restore(i);
  }

  // The task list for runTask(), in the order above.
  static std::vector<std::pair<int,int>> tasksFor(int M, int rmax) {
    std::vector<std::pair<int,int>> t;
    t.push_back({-1, -1});
    if (rmax >= 1)
      for (int i = 0; i < M; ++i) t.push_back({i, -1});
    if (rmax >= 2)
      for (int i = 0; i < M; ++i)
        for (int j = i + 1; j < M; ++j) t.push_back({i, j});
    return t;
  }
};

int main(int argc, char** argv) {
  if (argc < 4) {
    std::fprintf(stderr,
                 "usage: perimeter_min {square4|square8|tri6} PMAX RMAX\n"
                 "         [--threads T] [--boxes] [--only W H PARITY [SLO SHI]]\n"
                 "  RMAX < 0 means unbounded (complete brute force per box)\n"
                 "  --boxes  per-frame free-removal breakdown\n"
                 "  --only   run ONE frame; SLO SHI give the tri6 u+v window\n");
    return 2;
  }
  std::string lat = argv[1];
  int PMAX = std::atoi(argv[2]);
  int RMAX = std::atoi(argv[3]);
  int threads = 1;
  bool boxes_out = false;
  int onlyW = 0, onlyH = 0, onlyP = 0, onlySlo = 0, onlyShi = 0;
  bool onlyHex = false;
  for (int a = 4; a < argc; ++a) {
    if (!std::strcmp(argv[a], "--threads") && a + 1 < argc)
      threads = std::atoi(argv[++a]);
    else if (!std::strcmp(argv[a], "--boxes"))
      boxes_out = true;                  // per-box free-removal breakdown
    else if (!std::strcmp(argv[a], "--only") && a + 3 < argc) {
      // Run ONE box. The per-box free-removal sequence converges to its limit
      // only once the box side exceeds the removal count, so pinning the limit
      // means reaching a box far bigger than any full PMAX sweep can afford.
      onlyW = std::atoi(argv[++a]);
      onlyH = std::atoi(argv[++a]);
      onlyP = std::atoi(argv[++a]);
      // optional hex window: --only W H parity SLO SHI
      if (a + 2 < argc && argv[a + 1][0] != '-') {
        onlySlo = std::atoi(argv[++a]);
        onlyShi = std::atoi(argv[++a]);
        onlyHex = true;
      }
    }
  }

  const Offset* off; int noff; std::vector<int> parities; bool hex3 = false;
  if (lat == "square8")      { off = kKing; noff = 8; parities = {-1}; }
  else if (lat == "square4") { off = kDiag; noff = 4; parities = {0, 1}; }
  else if (lat == "tri6")    { off = kTri6; noff = 6; parities = {-1};
                               hex3 = true; }
  else { std::fprintf(stderr, "unknown lattice %s\n", lat.c_str()); return 2; }
  (void)kFuncsRect; (void)kFuncsHex;

  obs::Reporter rep("perimeter_min", 0,
                    "lattice=" + lat + " pmax=" + std::to_string(PMAX) +
                    " rmax=" + std::to_string(RMAX));

  // Collect the box list first: for fixed W, pbox is nondecreasing in H, so
  // stop at the first H that overshoots.  pbox is MEASURED off the filled box
  // (BoxRun::build), never a formula, so the box loop makes no lattice-specific
  // assumption about what the isoperimetric shape is.
  struct Job { int W, H, parity, mult, slo, shi; };
  std::vector<Job> jobs;
  if (onlyW) {
    jobs.push_back({onlyW, onlyH, onlyP, 1,
                    onlyHex ? onlySlo : 0,
                    onlyHex ? onlyShi : onlyW + onlyH - 2});
    if (onlyHex) hex3 = true;
    boxes_out = true;
  }
  // Transposing (u,v) is a lattice symmetry on all three lattices and fixes the
  // u+v window, so only W <= H is walked and W < H counted twice.
  for (int W = 1; !onlyW; ++W) {
    bool anyW = false;
    for (int H = W;; ++H) {
      bool anyH = false;
      const int smax = W + H - 2;
      for (int par : parities) {
        // hex3: walk every window [slo,shi] of u+v. Without it the single
        // full window is the plain rectangle, i.e. the old behaviour.
        for (int slo = 0; slo <= (hex3 ? smax : 0); ++slo)
          for (int shi = (hex3 ? slo : smax); shi <= smax; ++shi) {
            BoxRun probe(W, H, par, 1, 0, off, noff, hex3, slo, shi);
            if (!probe.build()) continue;
            if (probe.pbox > PMAX) continue;
            // In range AND unrepresentable: every animal in this frame would be
            // missing from the output with nothing to say so.  Refuse the run.
            if (probe.tooBig) {
              std::fprintf(stderr,
                           "FATAL: frame W=%d H=%d parity=%d has %d cells, over "
                           "the connectivity mask (%d). Its pbox=%d is within "
                           "PMAX=%d, so skipping it would silently drop animals. "
                           "Raise kMaskWords.\n",
                           W, H, par, probe.M, kMaxCells, probe.pbox, PMAX);
              return 3;
            }
            anyH = anyW = true;
            jobs.push_back({W, H, par, W == H ? 1 : 2, slo, shi});
            if (!hex3) break;
          }
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
  // --only pushes its frame without going through the plan loop's probe, so the
  // over-mask refusal has to exist here too.  Without it a too-big frame walks
  // into connected() with an empty nbrIdx.
  std::atomic<int> overMask{0};

  std::vector<long long> freeTotal;          // sharded path's free-removal sums

  // --only with --threads: shard the removal DFS itself.  The frame loop cannot
  // help when there is one frame, and that is exactly the case (a single huge
  // hull) where the deep RMAX values live.
  const bool shardOneFrame = (jobs.size() == 1 && threads > 1);
  if (shardOneFrame) {
    const Job& job = jobs[0];
    BoxRun probe(job.W, job.H, job.parity, job.mult,
                 RMAX < 0 ? kMaxCells : RMAX, off, noff, hex3, job.slo, job.shi);
    if (!probe.build()) {
      std::fprintf(stderr, "FATAL: --only frame W=%d H=%d parity=%d is not a "
                   "legal frame bounding box\n", job.W, job.H, job.parity);
      return 3;
    }
    if (probe.tooBig) {
      std::fprintf(stderr, "FATAL: frame W=%d H=%d parity=%d has %d cells, over "
                   "the connectivity mask (%d). Raise kMaskWords.\n",
                   job.W, job.H, job.parity, probe.M, kMaxCells);
      return 3;
    }
    const int rmaxEff = (RMAX < 0) ? probe.M : RMAX;
    const auto tasks = BoxRun::tasksFor(probe.M, rmaxEff);
    std::fprintf(stderr, "event=plan job=perimeter_min shards=%zu cells=%d\n",
                 tasks.size(), probe.M);

    std::atomic<size_t> nextT{0};
    auto shardWorker = [&](bool beats) {
      BoxRun r(job.W, job.H, job.parity, job.mult, rmaxEff, off, noff,
               hex3, job.slo, job.shi);
      if (!r.build()) return;
      r.rmax = rmaxEff;
      for (;;) {
        size_t t = nextT.fetch_add(1);
        if (t >= tasks.size()) break;
        r.runTask(tasks[t].first, tasks[t].second);
        if (beats && (t & 0xff) == 0)
          rep.beat((double)t, "shards=" + std::to_string(tasks.size()) +
                              " nodes=" + std::to_string(nodes.load()));
      }
      std::lock_guard<std::mutex> g(mu);
      for (auto& kv : r.res.tally) total[kv.first] += kv.second;
      nodes += r.res.nodes; emitted += r.res.emitted;
      violations += r.res.violations;
      if (freeTotal.size() < r.freeByR.size())
        freeTotal.resize(r.freeByR.size(), 0);
      for (size_t k = 0; k < r.freeByR.size(); ++k) freeTotal[k] += r.freeByR[k];
    };

    std::vector<std::thread> shardPool;
    for (int t = 1; t < threads; ++t) shardPool.emplace_back(shardWorker, false);
    shardWorker(true);
    for (auto& t : shardPool) t.join();

    if (boxes_out) {
      std::string s;
      for (long long v : freeTotal) s += " " + std::to_string(v);
      std::printf("# box W=%d H=%d parity=%d slo=%d shi=%d pbox=%d cells=%d "
                  "mult=%d free:%s\n",
                  probe.W, probe.H, probe.parity, probe.slo, probe.shi,
                  probe.pbox, probe.M, probe.mult, s.c_str());
    }
  }

  auto worker = [&]() {
    for (;;) {
      size_t j = next.fetch_add(1);
      if (j >= jobs.size()) break;
      const Job& job = jobs[j];
      BoxRun r(job.W, job.H, job.parity, job.mult,
               RMAX < 0 ? kMaxCells : RMAX, off, noff,
               hex3, job.slo, job.shi);
      if (!r.build()) continue;
      if (r.tooBig) {
        if (overMask.fetch_add(1) == 0)
          std::fprintf(stderr,
                       "FATAL: frame W=%d H=%d parity=%d has %d cells, over the "
                       "connectivity mask (%d). Raise kMaskWords.\n",
                       r.W, r.H, r.parity, r.M, kMaxCells);
        continue;
      }
      if (RMAX < 0) r.rmax = r.M;
      r.run();
      std::lock_guard<std::mutex> g(mu);
      if (boxes_out) {
        std::string s;
        for (size_t j2 = 0; j2 < r.freeByR.size(); ++j2)
          s += " " + std::to_string(r.freeByR[j2]);
        std::printf("# box W=%d H=%d parity=%d slo=%d shi=%d pbox=%d cells=%d "
                    "mult=%d free:%s\n",
                    r.W, r.H, r.parity, r.slo, r.shi, r.pbox, r.M, r.mult,
                    s.c_str());
      }
      for (auto& kv : r.res.tally) total[kv.first] += kv.second;
      nodes += r.res.nodes; emitted += r.res.emitted;
      violations += r.res.violations;
      rep.beat((double)(j + 1), "boxes=" + std::to_string(jobs.size()) +
                                " nodes=" + std::to_string(nodes.load()));
    }
  };

  if (!shardOneFrame) {
    std::vector<std::thread> pool;
    for (int t = 1; t < threads; ++t) pool.emplace_back(worker);
    worker();
    for (auto& t : pool) t.join();
  }

  if (overMask.load()) return 3;   // fail closed: output would be incomplete

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
