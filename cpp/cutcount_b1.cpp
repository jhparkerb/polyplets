// cutcount_b1.cpp — colour-symmetrized spin transfer matrix with clash-zeroing,
// for the polyplet triangle T(n,H): candidate B1 of
// results/second-source-candidates-B.md. (NOT the FK/random-cluster TM: that
// one joins partitions on adjacency; this one ZEROES on a clash of distinct
// colours and never joins — connectivity is never decided, only extracted.)
//
// Counts A_n(q) = sum over cell sets S of a height-H king strip of q^{c(S)}
// (c = number of king-connected components), exactly in the ring Z[q]/(q^2).
// The connected count is the LINEAR coefficient: T-type counts = [q^1] A_n(q).
// The frontier DP carries the COLOR-COINCIDENCE partition of the last H+1
// cells — it never decides connectivity: no union-find verdict, no stranded-
// component death. A cell adjacent to two distinct-color blocks has weight 0;
// a free cell joins an existing color (weight 1 each) or takes a fresh color
// (weight q−b, b = live blocks). Validated against brute force in
// experiments/probe_cutcount_dp.py (5 board sizes, exact).
//
// Accounting layer (shared with the strip engine, disjoint from the
// connectivity rule): sweep W = Nmax+1 columns; C_H(n) = f_W(n) − f_{W−1}(n)
// fixes horizontal translation (leftmost column = 0) and counts vertical
// placements, then T(n,H) = C_H − 2 C_{H−1} + C_{H−2} exactly as strip_tm.
//
// Coefficients: 4×u64 two's-complement WRAPPING arithmetic mod 2^256.
// Intermediates may wrap; the FINAL values are bounded by 40·C(574,40) < 2^216,
// so the mod-2^256 image determines them exactly (ring hom Z -> Z/2^256).
//
// Usage:
//   cutcount_b1 --states <Hmin> <Hmax> <Ncols>      state/transition census only
//   cutcount_b1 --modp <H> <Nmax> <p> <outfile>      C_H(n) mod p, n=1..Nmax (atom/BM probe)
//   cutcount_b1 --height <H> <Nmax> <outfile>        one C_H row -> outfile ("n value" lines)
//   cutcount_b1 --assemble <Hmax> <Nmax> <rowdir> <banked_dir>   T + per-H compare from row files
//   cutcount_b1 <Hmax> <Nmax> [banked_perheight_dir]  full run + banked compare
//
// Events (obs.h) on stderr; stdout is the human-readable report.

#include <cstdint>
#include <cstdio>
#include <cstring>
#include <cstdlib>
#include <string>
#include <vector>
#include <unordered_map>
#include <algorithm>
#include <chrono>
#include <fstream>
#include <sstream>
#include "obs.h"

static obs::Reporter* g_rep = nullptr;

using u64 = uint64_t;
using u128 = unsigned __int128;
using i128 = __int128;

// ---------- payload: wrapping 128-bit ring (Half Measure) ----------
// The DP is a ring homomorphism into Z/2^128, so every coefficient it carries
// is the true value reduced mod 2^128.  C_16(40) = 2^106.8 and the per-height
// ratio is falling (1.44, 1.36 at H = 15, 16), so C_19(40) projects to ~2^108
// -- inside the half-open [0, 2^127) window that fits_pay() enforces on every
// value before a row is written.  The A(1) self-check compares two values
// computed in the SAME wrapping ring, so it stays exact at any width even
// though its true value C(861,40) is ~2^229.
using Pay = u128;
static inline void iadd(Pay& a, const Pay& b) { a += b; }
// a += x * m for small signed m (|m| < 2^31); two's complement makes the
// sign-extended multiply the right answer mod 2^128.
static inline void iaddmul(Pay& a, const Pay& x, int64_t m) {
  a += x * (Pay)(i128)m;
}
static inline bool iszero(const Pay& a) { return a == 0; }
// exact as a nonnegative integer, and so convertible to signed 128
static inline bool fits_pay(const Pay& a) { return (a >> 127) == 0; }
static inline i128 to_i128(const Pay& a) { return (i128)a; }

static std::string i128str(i128 v) {
  if (v == 0) return "0";
  bool neg = v < 0;
  u128 u = neg ? (u128)(-v) : (u128)v;
  std::string s;
  while (u) { s += char('0' + int(u % 10)); u /= 10; }
  if (neg) s += '-';
  std::reverse(s.begin(), s.end());
  return s;
}

// ---------- frontier key: H+1 slots, 5 bits per slot, packed into u128 ----------
// slot k = color-block id of the cell processed k+1 cells ago (0 = empty).
// Max distinct blocks in a window of H+2 cells is <= 9 for H<=16; 5 bits is roomy.
struct KeyHash {
  size_t operator()(u128 k) const {
    u64 lo = (u64)k, hi = (u64)(k >> 64);
    u64 h = lo * 0x9E3779B97F4A7C15ull ^ (hi + 0x9E3779B97F4A7C15ull + (lo << 6) + (lo >> 2));
    return (size_t)(h ^ (h >> 29));
  }
};
static const u128 SLOTMASK = 0x1F;

// Height ceiling, and where each part of it comes from.  The frontier key
// packs H+1 slots of BITS bits into a u128, so (H+1)*BITS <= 128 gives
// H <= 24 -- that is the structural limit and the one HMAX_KEY enforces.
// The other two are far away and are asserted rather than relied on:
//   * block ids must fit a slot.  The maximum id is the number of distinct
//     blocks in the frontier, measured (census, H = 4..17) as ceil(H/2), so
//     it exceeds 31 only past H = 62.
//   * successors() writes at most (number of blocks) + 2 entries, measured as
//     ceil(H/2) + 1 -- 3,4,4,5,5,6,6,7,7,8,8 at H = 4..14 and confirmed
//     directly at 15, 16, 17.  SUCC_CAP = 32 covers every height the key
//     packing can reach, with a factor of three in hand.
// The engine shipped with a flat H <= 16 argument check, which was the height
// the banked ladder stopped at, not a property of the algorithm.
static const int BITS = 5;
static const int SUCC_CAP = 32;
static const int HMAX_KEY = 24;
static inline void check_height(int H) {
  if ((H + 1) * BITS > 128) {
    fprintf(stderr, "FATAL key_width H=%d\n", H); std::exit(2);
  }
  if (H / 2 + 1 > (int)SLOTMASK) {
    fprintf(stderr, "FATAL slot_width H=%d\n", H); std::exit(2);
  }
  if (H / 2 + 2 > SUCC_CAP) {
    fprintf(stderr, "FATAL succ_cap H=%d\n", H); std::exit(2);
  }
}

static inline int slot(u128 key, int k) { return (int)((key >> (BITS * k)) & SLOTMASK); }

// canonical relabel of block ids in first-occurrence order, slot 0 upward
static inline u128 canon(u128 key, int nslots) {
  int map[32]; std::memset(map, 0, sizeof map);
  int nxt = 1;
  u128 out = 0;
  for (int k = 0; k < nslots; k++) {
    int x = slot(key, k);
    if (x) {
      if (!map[x]) map[x] = nxt++;
      out |= (u128)map[x] << (BITS * k);
    }
  }
  return out;
}

// ---------- transition generation (shared by both modes) ----------
// For cell (r,c) in a height-H strip, incoming window key -> successors.
// Successor = (new key BEFORE canon+shift is applied by caller helper, weight m0,m1, dn)
struct Succ { u128 key; int64_t m0, m1; int dn; };

static inline int gather(u128 key, int H, int r, int c, int ids[4]) {
  int cnt = 0;
  auto push = [&](int k) {
    int x = slot(key, k);
    if (x) { for (int i = 0; i < cnt; i++) if (ids[i] == x) return; ids[cnt++] = x; }
  };
  if (r > 0) push(0);
  if (c > 0) {
    if (r + 1 < H) push(H - 2);
    push(H - 1);
    if (r > 0) push(H);
  }
  return cnt;
}

static inline u128 shifted(u128 key, int H, int newid) {
  // drop slot H, shift everything one slot older, prepend newid; then canon
  u128 kept = key & (((u128)1 << (BITS * H)) - 1); // slots 0..H-1
  return canon((kept << BITS) | (u128)newid, H + 1);
}

// enumerate successors of `key` at cell (r,c); returns count, fills out[]
static inline int successors(u128 key, int H, int r, int c, Succ out[12]) {
  int n = 0;
  // empty cell
  out[n++] = { shifted(key, H, 0), 1, 0, 0 };
  int ids[4];
  int nb = gather(key, H, r, c, ids);
  if (nb >= 2) return n;              // weight 0: distinct colors meet
  if (nb == 1) {
    out[n++] = { shifted(key, H, ids[0]), 1, 0, 1 };
    return n;
  }
  // free cell: join any existing block, or fresh color (q - b)
  int present[32]; std::memset(present, 0, sizeof present);
  int b = 0, mx = 0;
  for (int k = 0; k <= H; k++) {
    int x = slot(key, k);
    if (x && !present[x]) { present[x] = 1; b++; }
    if (x > mx) mx = x;
  }
  for (int x = 1; x <= mx; x++)
    if (present[x]) out[n++] = { shifted(key, H, x), 1, 0, 1 };
  out[n++] = { shifted(key, H, mx + 1), -b, 1, 1 };
  return n;
}

// ---------- states-only census ----------
static void census(int Hmin, int Hmax, int ncols) {
  printf("H, boundary_states_max, transitions_per_column_max, wall_s\n");
  for (int H = Hmin; H <= Hmax; H++) {
    auto t0 = std::chrono::steady_clock::now();
    std::unordered_map<u128, char, KeyHash> cur, nxt;
    cur[0] = 1;
    size_t maxstates = 0, maxtrans = 0;
    for (int c = 0; c < ncols; c++) {
      size_t trans = 0;
      for (int r = 0; r < H; r++) {
        nxt.clear();
        nxt.reserve(cur.size() * 2);
        Succ s[SUCC_CAP];
        for (auto& kv : cur) {
          int ns = successors(kv.first, H, r, c, s);
          trans += ns;
          for (int i = 0; i < ns; i++) nxt[s[i].key] = 1;
        }
        std::swap(cur, nxt);
      }
      maxstates = std::max(maxstates, cur.size());
      maxtrans = std::max(maxtrans, trans);
      if (g_rep) g_rep->beat(c + 1, "H=" + std::to_string(H)
                     + " states=" + std::to_string(cur.size()));
    }
    double dt = std::chrono::duration<double>(std::chrono::steady_clock::now() - t0).count();
    printf("%d, %zu, %zu, %.2f\n", H, maxstates, maxtrans, dt);
    fflush(stdout);
  }
}

// ---------- full engine ----------
struct Payload { std::vector<Pay> a; }; // 3*(Nmax+1): [3n]=c0, [3n+1]=c1, [3n+2]=A(1)

// run one height H, return per-n [q^1] of C_H (i128) — plus check [q^0]==0
static std::vector<i128> run_height(int H, int Nmax, double& wall) {
  auto t0 = std::chrono::steady_clock::now();
  int W = Nmax + 1;
  int NA = Nmax + 1;
  const int ST = 3;
  std::unordered_map<u128, uint32_t, KeyHash> idx, nidx;
  std::vector<Payload> pay, npay;
  idx[0] = 0;
  pay.push_back({});
  pay[0].a.assign(ST * NA, Pay{});
  pay[0].a[0] = 1; // n=0: c0=1
  pay[0].a[2] = 1; // n=0: A(1)=1
  std::vector<Pay> fprev(ST * NA, Pay{}), fcur(ST * NA, Pay{});
  for (int c = 0; c < W; c++) {
    for (int r = 0; r < H; r++) {
      nidx.clear();
      npay.clear();
      nidx.reserve(idx.size() * 2);
      Succ s[SUCC_CAP];
      for (auto& kv : idx) {
        const Payload& P = pay[kv.second];
        int ns = successors(kv.first, H, r, c, s);
        for (int i = 0; i < ns; i++) {
          auto it = nidx.find(s[i].key);
          uint32_t j;
          if (it == nidx.end()) {
            j = (uint32_t)npay.size();
            nidx.emplace(s[i].key, j);
            npay.push_back({});
            npay[j].a.assign(ST * NA, Pay{});
          } else j = it->second;
          Payload& Q = npay[j];
          int dn = s[i].dn;
          for (int n = 0; n + dn <= Nmax; n++) {
            const Pay& c0 = P.a[ST * n];
            const Pay& c1 = P.a[ST * n + 1];
            const Pay& ev = P.a[ST * n + 2];
            if (iszero(c0) && iszero(c1) && iszero(ev)) continue;
            Pay& d0 = Q.a[ST * (n + dn)];
            Pay& d1 = Q.a[ST * (n + dn) + 1];
            Pay& de = Q.a[ST * (n + dn) + 2];
            iaddmul(d0, c0, s[i].m0);
            iaddmul(d1, c1, s[i].m0);
            iaddmul(d1, c0, s[i].m1);
            iaddmul(de, ev, s[i].m0 + s[i].m1); // weight evaluated at q=1
          }
        }
      }
      std::swap(idx, nidx);
      std::swap(pay, npay);
    }
    // column boundary: f_c = column-sum of payloads
    fprev = fcur;
    std::fill(fcur.begin(), fcur.end(), Pay{});
    for (auto& P : pay)
      for (int t = 0; t < ST * NA; t++) iadd(fcur[t], P.a[t]);
    if (g_rep) g_rep->beat(c + 1, "H=" + std::to_string(H)
                   + " states=" + std::to_string(idx.size()));
  }
  // C_H(n) = f_W(n) - f_{W-1}(n); self-checks:
  //   (a) [q^0] C_H(n) = 0 for n>=1 (no constant term in sum_S q^{c(S)})
  //   (b) A(1)-part of C_H(n) = C(H*W, n) - C(H*(W-1), n)  (all-subsets binomial;
  //       exercises every transition weight at q=1, no connectivity involved)
  auto binom_rows = [&](int m) {           // Pascal in the same wrapping ring
    std::vector<Pay> row(NA, Pay{});
    row[0] = 1;
    for (int i = 1; i <= m; i++)
      for (int k = std::min(i, Nmax); k >= 1; k--) iadd(row[k], row[k - 1]);
    return row;
  };
  auto bW = binom_rows(H * W), bW1 = binom_rows(H * (W - 1));
  std::vector<i128> out(NA, 0);
  for (int n = 1; n < NA; n++) {
    Pay c0 = fcur[ST * n], c1 = fcur[ST * n + 1], ce = fcur[ST * n + 2];
    iaddmul(c0, fprev[ST * n], -1);
    iaddmul(c1, fprev[ST * n + 1], -1);
    iaddmul(ce, fprev[ST * n + 2], -1);
    if (!iszero(c0)) { fprintf(stderr, "FATAL q0_nonzero H=%d n=%d\n", H, n); std::exit(2); }
    if (!fits_pay(c1)) { fprintf(stderr, "FATAL q1_overflow_pay H=%d n=%d\n", H, n); std::exit(2); }
    Pay want = bW[n];
    iaddmul(want, bW1[n], -1);
    if (ce != want) {
      fprintf(stderr, "FATAL q1eval_binomial H=%d n=%d\n", H, n); std::exit(2);
    }
    out[n] = to_i128(c1);
  }
  printf("selfcheck H=%d: q0_zero=OK q1eval_binomial=OK (n=1..%d)\n", H, Nmax);
  wall = std::chrono::duration<double>(std::chrono::steady_clock::now() - t0).count();
  return out;
}

// mod-p series: same DP, payload (c0,c1) mod p per (state, area). p < 2^31.
static void run_height_modp(int H, int Nmax, uint64_t p, const char* outfile) {
  int W = Nmax + 1, NA = Nmax + 1;
  std::unordered_map<u128, uint32_t, KeyHash> idx, nidx;
  std::vector<std::vector<uint32_t>> pay, npay;   // 2*NA per state
  idx[0] = 0;
  pay.push_back(std::vector<uint32_t>(2 * NA, 0));
  pay[0][0] = 1;
  std::vector<uint64_t> fprev(2 * NA, 0), fcur(2 * NA, 0);
  for (int c = 0; c < W; c++) {
    for (int r = 0; r < H; r++) {
      nidx.clear(); npay.clear(); nidx.reserve(idx.size() * 2);
      Succ s[SUCC_CAP];
      for (auto& kv : idx) {
        const auto& P = pay[kv.second];
        int ns = successors(kv.first, H, r, c, s);
        for (int i = 0; i < ns; i++) {
          auto it = nidx.find(s[i].key);
          uint32_t j;
          if (it == nidx.end()) {
            j = (uint32_t)npay.size();
            nidx.emplace(s[i].key, j);
            npay.push_back(std::vector<uint32_t>(2 * NA, 0));
          } else j = it->second;
          auto& Q = npay[j];
          uint64_t m0 = (uint64_t)((s[i].m0 % (int64_t)p + (int64_t)p) % (int64_t)p);
          uint64_t m1 = (uint64_t)s[i].m1 % p;
          int dn = s[i].dn;
          for (int n = 0; n + dn <= Nmax; n++) {
            uint64_t c0 = P[2 * n], c1 = P[2 * n + 1];
            if (!(c0 | c1)) continue;
            uint32_t& d0 = Q[2 * (n + dn)];
            uint32_t& d1 = Q[2 * (n + dn) + 1];
            d0 = (uint32_t)((d0 + c0 * m0) % p);
            d1 = (uint32_t)((d1 + c1 * m0 + c0 * m1) % p);
          }
        }
      }
      std::swap(idx, nidx);
      std::swap(pay, npay);
    }
    fprev = fcur;
    std::fill(fcur.begin(), fcur.end(), 0);
    for (auto& P : pay)
      for (int t = 0; t < 2 * NA; t++) fcur[t] = (fcur[t] + P[t]) % p;
    if (g_rep) g_rep->beat(c + 1, "modp H=" + std::to_string(H)
                   + " states=" + std::to_string(idx.size()));
  }
  FILE* f = fopen(outfile, "w");
  if (!f) { perror(outfile); std::exit(1); }
  for (int n = 1; n <= Nmax; n++) {
    uint64_t c0 = (fcur[2 * n] + p - fprev[2 * n]) % p;
    uint64_t c1 = (fcur[2 * n + 1] + p - fprev[2 * n + 1]) % p;
    if (c0) { fprintf(stderr, "FATAL q0_nonzero_modp H=%d n=%d\n", H, n); std::exit(2); }
    fprintf(f, "%d %llu\n", n, (unsigned long long)c1);
  }
  fclose(f);
}

static i128 parse_i128s(const std::string& s) {
  i128 v = 0; size_t i = 0; bool neg = false;
  if (i < s.size() && (s[i] == '-' || s[i] == '+')) { neg = s[i] == '-'; ++i; }
  for (; i < s.size() && s[i] >= '0' && s[i] <= '9'; ++i) v = v * 10 + (s[i] - '0');
  return neg ? -v : v;
}

static std::vector<std::vector<i128>> loadC;

int main(int argc, char** argv) {
  obs::Reporter rep("cutcount_b1");
  g_rep = &rep;
  if (argc == 6 && !std::strcmp(argv[1], "--modp")) {
    int H = atoi(argv[2]), Nmax = atoi(argv[3]);
    uint64_t p = strtoull(argv[4], nullptr, 10);
    if (H > HMAX_KEY || p >= (1ull << 31)) { fprintf(stderr, "limits: H<=%d, p<2^31\n", HMAX_KEY); return 1; }
    check_height(H);
    run_height_modp(H, Nmax, p, argv[5]);
    printf("C_%d mod %llu, n<=%d -> %s\n", H, (unsigned long long)p, Nmax, argv[5]);
    rep.done("mode=modp H=" + std::to_string(H));
    return 0;
  }
  if (argc == 5 && !std::strcmp(argv[1], "--height")) {
    int H = atoi(argv[2]), Nmax = atoi(argv[3]);
    if (H > HMAX_KEY || Nmax > 60) { fprintf(stderr, "limits: H<=%d Nmax<=60\n", HMAX_KEY); return 1; }
    check_height(H);
    double wall = 0;
    auto row = run_height(H, Nmax, wall);
    FILE* f = fopen(argv[4], "w");
    if (!f) { perror(argv[4]); return 1; }
    for (int n = 1; n <= Nmax; n++) fprintf(f, "%d %s\n", n, i128str(row[n]).c_str());
    fclose(f);
    printf("C_%d done in %.1f s -> %s\n", H, wall, argv[4]);
    rep.done("mode=height H=" + std::to_string(H) + " wall_s=" + std::to_string(wall));
    return 0;
  }
  if (argc == 6 && !std::strcmp(argv[1], "--assemble")) {
    int Hmax = atoi(argv[2]), Nmax = atoi(argv[3]);
    std::vector<std::vector<i128>> C(Hmax + 1, std::vector<i128>(Nmax + 1, 0));
    for (int H = 1; H <= Hmax; H++) {
      char path[512];
      snprintf(path, sizeof path, "%s/C%d.out", argv[4], H);
      std::ifstream f(path);
      if (!f) { fprintf(stderr, "missing %s\n", path); return 1; }
      std::string line;
      while (std::getline(f, line)) {
        std::istringstream is(line);
        long long n; std::string val;
        if (is >> n >> val && n <= Nmax) C[H][n] = parse_i128s(val);
      }
    }
    auto T = [&](int n, int H) -> i128 {
      i128 t = C[H][n];
      if (H - 1 >= 1) t -= 2 * C[H - 1][n];
      if (H - 2 >= 1) t += C[H - 2][n];
      return t;
    };
    int allok = 0, allbad = 0;
    for (int H = 1; H <= Hmax; H++) {
      char path[512];
      snprintf(path, sizeof path, "%s/h%d.out", argv[5], H);
      std::ifstream f(path);
      std::string line;
      int ok = 0, bad = 0;
      while (std::getline(f, line)) {
        std::istringstream is(line);
        long long n; std::string val;
        if (!(is >> n >> val) || n < 1 || n > Nmax) continue;
        if (T((int)n, H) == parse_i128s(val)) ok++;
        else {
          bad++;
          printf("MISMATCH T(%lld,%d): engine=%s banked=%s\n", n, H,
                 i128str(T((int)n, H)).c_str(), val.c_str());
        }
      }
      printf("H=%d: %d match, %d mismatch\n", H, ok, bad);
      allok += ok; allbad += bad;
    }
    printf("\nvs banked triangle: %d match, %d MISMATCH\n", allok, allbad);
    rep.done("mode=assemble match=" + std::to_string(allok) + " mismatch=" + std::to_string(allbad));
    // Fail closed: an unreadable/empty banked dir compares NOTHING and would
    // otherwise print "0 match, 0 MISMATCH" and exit 0 -- a comparison that
    // cannot fail is not a check.
    if (!allbad && !allok) {
      fprintf(stderr, "FATAL no_banked_cells_compared dir=%s\n", argv[5]);
      return 3;
    }
    return allbad ? 2 : 0;
  }
  if (argc >= 2 && !std::strcmp(argv[1], "--states")) {
    if (argc != 5) { fprintf(stderr, "usage: %s --states Hmin Hmax Ncols\n", argv[0]); return 1; }
    census(atoi(argv[2]), atoi(argv[3]), atoi(argv[4]));
    rep.done("mode=census");
    return 0;
  }
  if (argc < 3) { fprintf(stderr, "usage: %s Hmax Nmax [banked_dir] | --states Hmin Hmax Ncols\n", argv[0]); return 1; }
  int Hmax = atoi(argv[1]), Nmax = atoi(argv[2]);
  if (Hmax > HMAX_KEY || Nmax > 60) { fprintf(stderr, "limits: Hmax<=%d Nmax<=60\n", HMAX_KEY); return 1; }
  for (int h = 1; h <= Hmax; h++) check_height(h);
  std::vector<std::vector<i128>> C(Hmax + 1);
  for (int H = 1; H <= Hmax; H++) {
    double wall = 0;
    C[H] = run_height(H, Nmax, wall);
    printf("C_%d done in %.1f s;  C_%d(%d) = %s\n", H, wall, H, Nmax, i128str(C[H][Nmax]).c_str());
    fflush(stdout);
    rep.beat(H, "height_done=H" + std::to_string(H) + " wall_s=" + std::to_string(wall), true);
  }
  // T(n,H) = C_H - 2 C_{H-1} + C_{H-2}
  auto T = [&](int n, int H) -> i128 {
    i128 t = C[H][n];
    if (H - 1 >= 1) t -= 2 * C[H - 1][n];
    if (H - 2 >= 1) t += C[H - 2][n];
    return t;
  };
  if (argc >= 4) {
    std::unordered_map<long long, i128> banked;
    int bmax = 0;
    for (int H = 1; H <= Hmax; H++) {
      char path[512];
      snprintf(path, sizeof path, "%s/h%d.out", argv[3], H);
      std::ifstream f(path);
      std::string line;
      while (std::getline(f, line)) {
        std::istringstream is(line);
        long long n; std::string val;
        if (is >> n >> val) { banked[n * 100 + H] = parse_i128s(val); if (n > bmax) bmax = (int)n; }
      }
    }
    int ok = 0, bad = 0;
    for (int H = 1; H <= Hmax; H++)
      for (int n = 1; n <= Nmax; n++) {
        auto it = banked.find((long long)n * 100 + H);
        if (it == banked.end()) continue;
        if (T(n, H) == it->second) ok++;
        else {
          bad++;
          if (bad == 1)
            printf("first MISMATCH T(%d,%d): engine=%s banked=%s\n", n, H,
                   i128str(T(n, H)).c_str(), i128str(it->second).c_str());
        }
      }
    printf("\nvs banked triangle: %d match, %d MISMATCH\n", ok, bad);
    rep.done("mode=full Hmax=" + std::to_string(Hmax) + " Nmax=" + std::to_string(Nmax)
             + " match=" + std::to_string(ok) + " mismatch=" + std::to_string(bad));
    // Same fail-closed rule as --assemble: mismatches are fatal, and a run
    // that compared zero cells (wrong/empty banked dir) is fatal too.
    if (bad) return 2;
    if (!ok) {
      fprintf(stderr, "FATAL no_banked_cells_compared dir=%s\n", argv[3]);
      return 3;
    }
    return 0;
  } else {
    for (int H = 1; H <= Hmax; H++) {
      printf("T(n,%d):", H);
      for (int n = 1; n <= std::min(Nmax, 12); n++) printf(" %s", i128str(T(n, H)).c_str());
      printf("\n");
    }
  }
  rep.done("mode=full Hmax=" + std::to_string(Hmax) + " Nmax=" + std::to_string(Nmax));
  return 0;
}
