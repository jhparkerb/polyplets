// r4_spin_engine.cpp -- INV-8 spin-basis parity engine (q=2 colour DP), the C++
// port of the validated desk pipeline experiments/tristruct/r3_spin_pipeline.py.
//
// UNCOMPILED AT AUTHORING TIME. Written by agent r4-spinbuild, round 4, which
// is forbidden to build or run anything. Nothing below has ever been compiled
// or executed. See results/r4/r4-spinbuild.md.
//
// WHAT IT COUNTS
// --------------
// For a strip of height m rows swept along the width, it computes
//
//     Z_{w,m}(n) = sum over n-cell subsets S of the w x m box of 2^{c(S)}
//                = # of pairs (S, f) with f: S -> {A,B} constant on the
//                  king-components of S
//                = # of colourings of the box by {E,A,B} with n non-E cells in
//                  which any two king-adjacent occupied cells agree
//
// exactly the quantity r3_spin_pipeline.py's z_table() computes, but mod 4 and
// cell-at-a-time instead of exactly and column-at-a-time (the whole-column
// kernel is priced out at ~4.646^m transition pairs, results/triangle-r3-spin.md
// section 1). Because 2^c == 0 (mod 4) for c >= 2,
//
//     Z_{w,m}(n) == 2 * #{connected S} (mod 4),
//
// so connectivity is never decided: no partition in the state, no union, no
// stranded-component death, no closability test. It is read off a residue.
//
// Accounting, identical in form to the Python reference:
//     A_m(n)  = Z_{n,m}(n) - Z_{n-1,m}(n)       width-translation fix
//     N_H(n)  = A_H(n) - 2 A_{H-1}(n) + A_{H-2}(n)      row extent exactly H
//     T(n,H) == N_H(n)/2   (mod 2)
// with A_m := 0 for m < 1. A_m(n) is not stable in exact value as w grows (ever
// wider disconnected classes keep entering) but IS stable mod 4; the w = n+1
// recomputation is the in-run restatement of that, and it is a BOOKKEEPING
// check, blind to stencil errors -- never promote it to a correctness check.
//
// STATE AND KERNEL
// ----------------
// Kink (cell-at-a-time) sweep. When the cell about to be placed is (x, r) the
// live frontier is exactly the m+1 cells
//     { (x, j) : j < r }  u  { (x-1, j) : j >= r-1 }
// (r3_spin_counts.py window_cells(m, r), same set). Laid out in ROW order with
// the (x-1, r-1) "carry" cell spliced in at index r,
//
//     u = ( (x,0) ... (x,r-1), (x-1,r-1), (x-1,r), ... (x-1,m-1) )
//
// consecutive entries of u are king-adjacent for every r -- u is a Hamiltonian
// path of the frontier's constraint graph, which is the injection into path
// strings that bounds the window census by t_{m+1} (spin file section 1). So
// the reachable states inject into
//
//     L_{m+1} = { s in {E,A,B}^{m+1} : no two adjacent entries clash }
//
// of size t_{m+1} = 2 t_m + t_{m-1}, t_1 = 3, t_2 = 7 (companion Pell). The
// engine is DENSELY RANKED over L_{m+1}: the array index IS the state, there is
// no key and no hash. Mandatory per results/r4/r4-inv.md section 1.3 -- it
// deletes the 8-byte key and is what makes the borrowed 40 ns/slot anchor a
// model of what the kernel does. The waste is the measured W(m)/t_{m+1} =
// 0.8995 gap, i.e. ~11%, exactly the figure r4-inv priced.
//
// In that layout placing (x,r) = v is simply "overwrite u[r] with v":
//     N  = u[r-1]  (r > 0)      NW = u[r]
//     W  = u[r+1]               SW = u[r+2]  (r+2 <= m)
// and v is dropped iff it is occupied and clashes with an occupied one of them.
// u[r-1] and u[r+1] are v's path neighbours in the destination string, so the
// destination is in L_{m+1} by construction; the rank moves by a two-term
// difference, O(1). The last stage of a column (r = m-1) instead produces
// u'' = (E, u[0..m-2], v), a shift; its rank is maintained incrementally by the
// same odometer that walks the source strings.
//
// PAYLOAD
// -------
// Per state, one polynomial in the area: coefficients mod 4, one 2-bit lane per
// area slot n = 0..nmax, packed into a uint64 (slots 0..31) plus a uint32
// (slots 32..47). Lane-wise mod-4 addition is
//     (a ^ b) ^ (((a & b) & LOW) << 1)
// -- four instructions per word, no per-slot loop. The cost model's "slot-op"
// is therefore a NOTIONAL unit here: this kernel does not execute 41 operations
// per transition, so a measured ns/slot-op below the 40 ns B1 anchor is a
// statement about the model's units, not only about the hardware. Said plainly
// because the whole point of the calibration is to stop borrowing constants.
// Area beyond nmax is discarded on the shift (we only ever need n <= nmax);
// that truncation is exact for the coefficients we keep, is counted, and is
// reported -- it is by design, not a bound violation.
//
// FAIL-CLOSED / BLIND HARVEST
// ---------------------------
// The engine writes its output file and hashes it BEFORE the oracle is so much
// as opened; the comparison is a second pass that re-reads the written file
// from disk, so it structurally cannot use an in-memory value (r4-inv 3.3).
// Exit codes implement r4-inv 3.4; a run that compared zero cells is a failure,
// not a pass.
//
// Usage:
//   r4_spin_engine --m <lo>[..<hi>] --cols <C> --nmax <N> --mod 4 --dense-rank
//                  --oracle <dir> --out <file>
//                  [--mutant none|drop-nw|drop-sw|rook|slot40|noharvestdiff]
//                  [--inject <m>,<col>,<stage>,<slot>] [--expect-flips <k>]
//                  [--threads <t>] [--verify-rank 0|1] [--report-rss]
//
//   --oracle names a directory of C<H>.out files ("n value" lines, C_H(n)
//   exact); T(n,H) = C_H - 2 C_{H-1} + C_{H-2} is reduced mod 2 and compared
//   against the engine's parity for every cell both sides cover.
//   <file> carries only mathematical output, so two runs that differ merely in
//   thread count, box or ISA must be byte-identical; measurements go to
//   <file>.metrics and to the stderr event stream.
//
//   --verify-rank cross-checks every incrementally computed destination rank
//   against a from-scratch rank of the destination string. Default: on for
//   m <= 10, off above (it costs an O(m) rank per transition). The language
//   walk that confirms rank/unrank is a bijection is separate and runs
//   unconditionally to m = 16, --verify-rank 1 above that.
//
// Exit codes (0 = everything that was supposed to be checked was checked and
// agreed; see results/r4/r4-spinbuild.md section 4 for the gate sequence):
//    1 bad arguments        2 I/O failure          3 zero cells compared
//   70 n<=7 desk-table subset mismatch (GATE 0, via --nmax 7 --m 1..7)
//   71 RED mutant produced an EMPTY flip set, or missed --expect-flips
//   72 fault injection did not surface
//   73 oracle comparison mismatched (clean run)
//   74 --report-rss asked for measurements that were not obtained
//   76 in-run structural (bookkeeping) check failed on a clean run
//   77 incremental rank disagreed with the from-scratch rank
//   78 bound violation (state space, area slots, arithmetic overflow)
//   79 refused: no oracle, so nothing would have been checked

#include <version>

#include <algorithm>
#include <atomic>
#include <chrono>
#include <cstdarg>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <fstream>
#include <sstream>
#include <string>
#include <thread>
#include <vector>

#include "argparse.h"
#include "obs.h"

#if defined(__cpp_lib_atomic_ref) && __cpp_lib_atomic_ref >= 201806L
#define SPIN_HAVE_ATOMIC_REF 1
#else
#define SPIN_HAVE_ATOMIC_REF 0
#endif

using u32 = uint32_t;
using u64 = uint64_t;

// ---------------------------------------------------------------- bounds ----
// Every fixed size in this file is stated here with the reason it holds at the
// production target m = 21, nmax = 40. Nothing data-dependent lives in a fixed
// buffer: the frontier string, the rank tables, the payload arrays and the Z
// table are all std::vector sized from the arguments. (Round 3 found a real
// `Succ out[12]` overflow in the B1 engine; the response here is not a bigger
// constant but no such buffer at all.)
static const int kMaxSlots = 48;   // 64 payload bits in lo + 32 in hi, 2 per slot
static const int kMaxNmax = 47;    // slots 0..nmax must fit kMaxSlots
static const int kMaxM = 40;       // guards the Pell tables against u64 overflow
static const u64 kMaxStates = (u64)1 << 34;  // 17 G states; m=21 needs 3.18e8
static_assert(2 * kMaxSlots == 64 + 32, "payload lane budget");
static_assert(kMaxNmax + 1 <= kMaxSlots, "nmax must fit the payload lanes");

static const u64 kLow64 = 0x5555555555555555ull;  // low bit of each 2-bit lane
static const u32 kLow32 = 0x55555555u;

static obs::Reporter* g_rep = nullptr;
static double g_progress = 0;  // columns finished, across every m of this run

[[noreturn]] static void die(int code, const char* fmt, ...)
    __attribute__((format(printf, 2, 3)));
[[noreturn]] static void die(int code, const char* fmt, ...) {
  va_list ap;
  va_start(ap, fmt);
  std::fprintf(stderr, "FATAL ");
  std::vfprintf(stderr, fmt, ap);
  std::fputc('\n', stderr);
  va_end(ap);
  std::fflush(stderr);
  std::exit(code);
}

// ------------------------------------------------------- spin alphabet ----
// E = 0 (empty), A = 1, B = 2. Identical to the Python reference's E, A, B.
static inline bool clash(int x, int y) { return x > 0 && y > 0 && x != y; }
// p == 3 means "no predecessor" (first position of a string).
static inline bool compat(int p, int y) { return p == 3 || !clash(p, y); }

// next symbol > c that is compatible with predecessor p, or -1
static inline int next_sym(int p, int c) {
  for (int y = c + 1; y <= 2; y++)
    if (compat(p, y)) return y;
  return -1;
}

// ------------------------------------------------------- packed payload ----
// One 2-bit mod-4 lane per area slot. Lane-wise add: the low bits xor, the high
// bits xor and take the carry out of the low bits.
static inline void add4(u64& dlo, u32& dhi, u64 slo, u32 shi) {
  dlo = (dlo ^ slo) ^ (((dlo & slo) & kLow64) << 1);
  dhi = (dhi ^ shi) ^ (((dhi & shi) & kLow32) << 1);
}

// ---------------------------------------------------- ranking over L_len ----
// g[k][x] = number of valid completions of positions k..len-1 with s[k] = x.
// h[k][p][x] = sum of g[k][y] over y < x compatible with predecessor p, i.e.
// the number of strings that sort before s at position k given the prefix.
// rank(s) = sum_k h[k][ k ? s[k-1] : NONE ][ s[k] ], a plain mixed-radix rank.
struct Ranker {
  int len = 0;
  std::vector<u64> g;  // len * 3
  std::vector<u64> h;  // len * 4 * 3
  u64 total = 0;

  inline u64 G(int k, int x) const { return g[(size_t)k * 3 + x]; }
  inline u64 H(int k, int p, int x) const {
    return h[((size_t)k * 4 + p) * 3 + x];
  }

  void build(int len_) {
    len = len_;
    g.assign((size_t)len * 3, 0);
    h.assign((size_t)len * 4 * 3, 0);
    for (int x = 0; x < 3; x++) g[(size_t)(len - 1) * 3 + x] = 1;
    for (int k = len - 2; k >= 0; k--)
      for (int x = 0; x < 3; x++) {
        u64 s = 0;
        for (int y = 0; y < 3; y++)
          if (compat(x, y)) {
            // Pell growth is ~2.414^len; kMaxM caps len at 41 (~1e15), but the
            // check is here rather than argued, because it is free.
            if (s > (~(u64)0) - G(k + 1, y)) die(78, "rank_table_overflow len=%d", len);
            s += G(k + 1, y);
          }
        g[(size_t)k * 3 + x] = s;
      }
    for (int k = 0; k < len; k++)
      for (int p = 0; p < 4; p++) {
        u64 acc = 0;
        for (int x = 0; x < 3; x++) {
          h[((size_t)k * 4 + p) * 3 + x] = acc;
          if (compat(p, x)) acc += G(k, x);
        }
      }
    total = 0;
    for (int x = 0; x < 3; x++) total += G(0, x);
  }

  u64 rank(const uint8_t* s) const {
    u64 r = 0;
    for (int k = 0; k < len; k++) r += H(k, k ? s[k - 1] : 3, s[k]);
    return r;
  }

  void unrank(u64 idx, uint8_t* s) const {
    for (int k = 0; k < len; k++) {
      const int p = k ? s[k - 1] : 3;
      int chosen = -1;
      for (int x = 0; x < 3; x++) {
        if (!compat(p, x)) continue;
        if (idx < G(k, x)) { chosen = x; break; }
        idx -= G(k, x);
      }
      if (chosen < 0) die(78, "unrank_out_of_range");
      s[k] = (uint8_t)chosen;
    }
  }

  // Advance s to the lexicographic successor inside L_len. Returns the lowest
  // position that changed, or -1 when the language is exhausted. E is
  // compatible with every predecessor, so the reset suffix is all zeros.
  int advance(uint8_t* s) const {
    for (int k = len - 1; k >= 0; k--) {
      const int nv = next_sym(k ? s[k - 1] : 3, s[k]);
      if (nv >= 0) {
        s[k] = (uint8_t)nv;
        for (int j = k + 1; j < len; j++) s[j] = 0;
        return k;
      }
    }
    return -1;
  }
};

// The index space is the whole engine's correctness floor: if rank/unrank is
// not a bijection onto [0, total) then payloads land on the wrong states and
// every downstream check is comparing garbage to garbage. Two independent
// confirmations, both cheap:
//   (a) total must equal the companion Pell number t_len (t_1 = 3, t_2 = 7,
//       t_k = 2 t_{k-1} + t_{k-2}) -- the count round 3 brute-forced to m <= 12
//       in r3_spin_counts.py;
//   (b) walking the odometer from the all-E string must visit exactly `total`
//       strings, in rank order, with rank(s) == the visit counter throughout.
// (b) is O(total * len) so it runs unconditionally up to len = 17 (~4e6 strings,
// well under a second) and on demand above that via --verify-rank 1.
static void verify_language(const Ranker& rk, bool full) {
  u64 a = 1, b = 3;  // t_0 = 1, t_1 = 3
  for (int k = 2; k <= rk.len; k++) { const u64 c = 2 * b + a; a = b; b = c; }
  const u64 pell = (rk.len == 1) ? 3 : b;
  if (rk.total != pell)
    die(78, "state_count_not_pell len=%d total=%llu pell=%llu", rk.len,
        (unsigned long long)rk.total, (unsigned long long)pell);
  if (!full) return;
  std::vector<uint8_t> s((size_t)rk.len, 0);
  u64 seen = 0;
  for (;;) {
    if (rk.rank(s.data()) != seen)
      die(78, "rank_not_sequential len=%d at=%llu got=%llu", rk.len,
          (unsigned long long)seen, (unsigned long long)rk.rank(s.data()));
    seen++;
    if (rk.advance(s.data()) < 0) break;
  }
  if (seen != rk.total)
    die(78, "language_walk_size len=%d walked=%llu total=%llu", rk.len,
        (unsigned long long)seen, (unsigned long long)rk.total);
}

// ---------------------------------------------------------------- config ----
enum class Mutant { kNone, kDropNw, kDropSw, kRook, kSlot40, kNoHarvestDiff };

struct Config {
  int mlo = 0, mhi = 0;
  int cols = 0, nmax = 0;
  Mutant mutant = Mutant::kNone;
  int threads = 1;
  int verify_rank = -1;  // -1 = auto (on for m <= 10)
  bool report_rss = false;
  long expect_flips = -1;
  std::string oracle, out;
  // fault injection
  bool inject = false;
  int inj_m = 0, inj_col = 0, inj_stage = 0, inj_slot = 0;

  bool red() const { return mutant != Mutant::kNone || inject; }
  bool use_nw() const {
    return mutant != Mutant::kDropNw && mutant != Mutant::kRook;
  }
  bool use_sw() const {
    return mutant != Mutant::kDropSw && mutant != Mutant::kRook;
  }
  // The W (due-west, offset d = 0) constraint is one of the two path-adjacencies
  // the dense index space encodes, so no mutant may drop it without putting
  // reachable states outside the array. Listed exhaustively rather than
  // returned as a bare `true`: a future mutant that drops W then trips the
  // startup guard instead of silently corrupting the ranking.
  bool use_w() const {
    switch (mutant) {
      case Mutant::kNone:
      case Mutant::kDropNw:
      case Mutant::kDropSw:
      case Mutant::kRook:
      case Mutant::kSlot40:
      case Mutant::kNoHarvestDiff:
        return true;
    }
    return false;
  }
};

static const char* mutant_name(Mutant m) {
  switch (m) {
    case Mutant::kNone: return "none";
    case Mutant::kDropNw: return "drop-nw";
    case Mutant::kDropSw: return "drop-sw";
    case Mutant::kRook: return "rook";
    case Mutant::kSlot40: return "slot40";
    case Mutant::kNoHarvestDiff: return "noharvestdiff";
  }
  return "?";
}

// --------------------------------------------------------------- buffers ----
struct Buf {
  std::vector<u64> lo;
  std::vector<u32> hi;
  void alloc(size_t n) { lo.assign(n, 0); hi.assign(n, 0); }
  void zero() {
    std::fill(lo.begin(), lo.end(), (u64)0);
    std::fill(hi.begin(), hi.end(), (u32)0);
  }
  void release() {
    std::vector<u64>().swap(lo);
    std::vector<u32>().swap(hi);
  }
};

struct StagePlan {
  const Ranker* rk;
  const Buf* src;
  Buf* dst;
  int m, r;
  bool wrap;
  bool use_nw, use_sw;
  int slot_cap;      // highest area slot kept
  u64 lo_keep;       // mask of kept lanes in lo after a shift
  u32 hi_keep;
  bool verify_rank;
};

struct StageStats {
  u64 transitions = 0;
  u64 truncated = 0;
  u64 stage0_invariant_violations = 0;
};

// Add payload (slo,shi), optionally shifted up one area slot, into dst[idx].
template <bool ATOMIC>
static inline void deposit(Buf* dst, u64 idx, u64 slo, u32 shi) {
  if constexpr (ATOMIC) {
#if SPIN_HAVE_ATOMIC_REF
    if (slo) {
      std::atomic_ref<u64> a(dst->lo[idx]);
      u64 cur = a.load(std::memory_order_relaxed), want;
      do {
        want = cur;
        u32 dummy = 0;
        add4(want, dummy, slo, 0);
      } while (!a.compare_exchange_weak(cur, want, std::memory_order_relaxed));
    }
    if (shi) {
      std::atomic_ref<u32> a(dst->hi[idx]);
      u32 cur = a.load(std::memory_order_relaxed), want;
      do {
        want = cur;
        u64 dummy = 0;
        add4(dummy, want, 0, shi);
      } while (!a.compare_exchange_weak(cur, want, std::memory_order_relaxed));
    }
#else
    (void)dst; (void)idx; (void)slo; (void)shi;
    die(78, "threads_unsupported_no_atomic_ref");
#endif
  } else {
    add4(dst->lo[idx], dst->hi[idx], slo, shi);
  }
}

// One stage of one column over source indices [i0, i1).
template <bool ATOMIC>
static void run_stage(const StagePlan& P, u64 i0, u64 i1, StageStats* st) {
  const Ranker& rk = *P.rk;
  const int len = rk.len;          // = m + 1
  const int r = P.r;
  std::vector<uint8_t> u((size_t)len, 0);
  std::vector<uint8_t> tmp((size_t)len, 0);  // --verify-rank scratch only
  std::vector<u64> pw((size_t)len + 1, 0);   // wrap-path prefix sums

  rk.unrank(i0, u.data());

  // Wrap destination rank: for u'' = (E, u[0..m-2], v),
  //   rank(u'') = sum_{k=1}^{m-1} h[k][ k==1 ? E : u[k-2] ][ u[k-1] ]
  //               + h[m][ m>=2 ? u[m-2] : E ][ v ]
  // (the k = 0 term is h[0][NONE][E] = 0). pw[k] holds the running sum, and is
  // recomputed only from the lowest digit the odometer changed.
  const int m = P.m;
  auto recompute_pw = [&](int from) {
    if (from < 1) from = 1;
    for (int k = from; k <= m - 1; k++) {
      const int prev = (k == 1) ? 0 : u[k - 2];
      pw[k] = pw[k - 1] + rk.H(k, prev, u[k - 1]);
    }
  };
  if (P.wrap) recompute_pw(1);

  for (u64 idx = i0; idx < i1; idx++) {
    const u64 slo = P.src->lo[idx];
    const u32 shi = P.src->hi[idx];
    if (slo || shi) {
      const int nsym = u[r];
      const int nb_n = (r > 0) ? u[r - 1] : 0;
      const int nb_w = u[r + 1];  // r + 1 <= m = len - 1 always
      const int nb_sw = (r + 2 <= len - 1) ? u[r + 2] : 0;

      // Stage 0 of a column can only be reached with an empty carry: the wrap
      // transition writes E into position 0. A live state that violates it
      // means the index space and the sweep have come apart.
      if (r == 0 && nsym != 0) st->stage0_invariant_violations++;

      // Precompute the parts of the destination rank that do not depend on v.
      u64 base = 0;
      int pred = 3;
      if (!P.wrap) {
        pred = (r > 0) ? u[r - 1] : 3;
        base = idx - rk.H(r, pred, nsym) - rk.H(r + 1, nsym, nb_w);
      } else {
        base = pw[m - 1 >= 1 ? m - 1 : 0];
        pred = (m >= 2) ? u[m - 2] : 0;
      }

      for (int v = 0; v <= 2; v++) {
        if (v != 0) {
          if (clash(nb_n, v)) continue;
          if (P.use_nw && clash(nsym, v)) continue;
          if (clash(nb_w, v)) continue;          // W: never dropped, see use_w()
          if (P.use_sw && clash(nb_sw, v)) continue;
        }
        u64 dst;
        if (!P.wrap) {
          if (!compat(pred, v) || !compat(v, nb_w)) continue;  // unreachable
          dst = base + rk.H(r, pred, v) + rk.H(r + 1, v, nb_w);
        } else {
          if (!compat(pred, v)) continue;                       // unreachable
          dst = base + rk.H(len - 1, pred, v);
        }
        if (P.verify_rank) {
          if (!P.wrap) {
            std::copy(u.begin(), u.end(), tmp.begin());
            tmp[r] = (uint8_t)v;
          } else {
            tmp[0] = 0;
            for (int k = 1; k <= m - 1; k++) tmp[k] = u[k - 1];
            tmp[len - 1] = (uint8_t)v;
          }
          const u64 want = rk.rank(tmp.data());
          if (want != dst)
            die(77, "rank_mismatch m=%d r=%d idx=%llu incremental=%llu scratch=%llu",
                P.m, r, (unsigned long long)idx, (unsigned long long)dst,
                (unsigned long long)want);
        }
        if (dst >= rk.total) die(78, "dst_rank_out_of_range m=%d r=%d", P.m, r);

        u64 olo = slo;
        u32 ohi = shi;
        if (v != 0) {
          // multiply by x: shift every 2-bit lane up by one slot. Anything past
          // slot_cap is area we never need; dropping it is exact for the
          // coefficients we keep, and is counted rather than ignored.
          const u64 carry = (olo >> 62) & 0x3ull;
          const u64 raw_lo = olo << 2;
          const u64 raw_hi = ((u64)ohi << 2) | carry;  // 34 bits wide at most
          if ((raw_lo & ~P.lo_keep) || (raw_hi & ~(u64)P.hi_keep))
            st->truncated++;
          olo = raw_lo & P.lo_keep;
          ohi = (u32)(raw_hi & (u64)P.hi_keep);
          if (!olo && !ohi) { st->transitions++; continue; }
        }
        deposit<ATOMIC>(P.dst, dst, olo, ohi);
        st->transitions++;
      }
    }
    if (idx + 1 < i1) {
      const int changed = rk.advance(u.data());
      if (changed < 0) die(78, "odometer_exhausted_early m=%d r=%d", P.m, r);
      if (P.wrap) recompute_pw(changed + 1);
    }
  }
}

// ------------------------------------------------------------- SHA-256 ----
namespace sha256 {
struct Ctx {
  u32 h[8] = {0x6a09e667u, 0xbb67ae85u, 0x3c6ef372u, 0xa54ff53au,
              0x510e527fu, 0x9b05688cu, 0x1f83d9abu, 0x5be0cd19u};
  unsigned char buf[64] = {};
  size_t len = 0;   // bytes buffered
  u64 total = 0;    // total bytes
};
static inline u32 ror(u32 x, int n) { return (x >> n) | (x << (32 - n)); }
static void block(Ctx& c, const unsigned char* p) {
  static const u32 K[64] = {
      0x428a2f98u,0x71374491u,0xb5c0fbcfu,0xe9b5dba5u,0x3956c25bu,0x59f111f1u,
      0x923f82a4u,0xab1c5ed5u,0xd807aa98u,0x12835b01u,0x243185beu,0x550c7dc3u,
      0x72be5d74u,0x80deb1feu,0x9bdc06a7u,0xc19bf174u,0xe49b69c1u,0xefbe4786u,
      0x0fc19dc6u,0x240ca1ccu,0x2de92c6fu,0x4a7484aau,0x5cb0a9dcu,0x76f988dau,
      0x983e5152u,0xa831c66du,0xb00327c8u,0xbf597fc7u,0xc6e00bf3u,0xd5a79147u,
      0x06ca6351u,0x14292967u,0x27b70a85u,0x2e1b2138u,0x4d2c6dfcu,0x53380d13u,
      0x650a7354u,0x766a0abbu,0x81c2c92eu,0x92722c85u,0xa2bfe8a1u,0xa81a664bu,
      0xc24b8b70u,0xc76c51a3u,0xd192e819u,0xd6990624u,0xf40e3585u,0x106aa070u,
      0x19a4c116u,0x1e376c08u,0x2748774cu,0x34b0bcb5u,0x391c0cb3u,0x4ed8aa4au,
      0x5b9cca4fu,0x682e6ff3u,0x748f82eeu,0x78a5636fu,0x84c87814u,0x8cc70208u,
      0x90befffau,0xa4506cebu,0xbef9a3f7u,0xc67178f2u};
  u32 w[64];
  for (int i = 0; i < 16; i++)
    w[i] = ((u32)p[4 * i] << 24) | ((u32)p[4 * i + 1] << 16) |
           ((u32)p[4 * i + 2] << 8) | (u32)p[4 * i + 3];
  for (int i = 16; i < 64; i++) {
    const u32 s0 = ror(w[i - 15], 7) ^ ror(w[i - 15], 18) ^ (w[i - 15] >> 3);
    const u32 s1 = ror(w[i - 2], 17) ^ ror(w[i - 2], 19) ^ (w[i - 2] >> 10);
    w[i] = w[i - 16] + s0 + w[i - 7] + s1;
  }
  u32 a = c.h[0], b = c.h[1], cc = c.h[2], d = c.h[3];
  u32 e = c.h[4], f = c.h[5], g = c.h[6], hh = c.h[7];
  for (int i = 0; i < 64; i++) {
    const u32 S1 = ror(e, 6) ^ ror(e, 11) ^ ror(e, 25);
    const u32 ch = (e & f) ^ (~e & g);
    const u32 t1 = hh + S1 + ch + K[i] + w[i];
    const u32 S0 = ror(a, 2) ^ ror(a, 13) ^ ror(a, 22);
    const u32 mj = (a & b) ^ (a & cc) ^ (b & cc);
    const u32 t2 = S0 + mj;
    hh = g; g = f; f = e; e = d + t1; d = cc; cc = b; b = a; a = t1 + t2;
  }
  c.h[0] += a; c.h[1] += b; c.h[2] += cc; c.h[3] += d;
  c.h[4] += e; c.h[5] += f; c.h[6] += g; c.h[7] += hh;
}
static void update(Ctx& c, const unsigned char* p, size_t n) {
  c.total += n;
  while (n) {
    const size_t take = std::min(n, sizeof c.buf - c.len);
    std::memcpy(c.buf + c.len, p, take);
    c.len += take; p += take; n -= take;
    if (c.len == sizeof c.buf) { block(c, c.buf); c.len = 0; }
  }
}
static std::string finish(Ctx& c) {
  const u64 bits = c.total * 8;
  // Bound: 1 marker byte + at most 63 zeros to reach offset 56 + 8 length
  // bytes = 72, which is the array's size. c.total is not used after this.
  unsigned char pad[72];
  size_t padlen = 0;
  pad[padlen++] = 0x80;
  while ((c.len + padlen) % 64 != 56) {
    if (padlen >= sizeof pad - 8) die(78, "sha256_pad_overflow");
    pad[padlen++] = 0;
  }
  for (int i = 0; i < 8; i++) pad[padlen++] = (unsigned char)(bits >> (56 - 8 * i));
  update(c, pad, padlen);
  char out[65];
  for (int i = 0; i < 8; i++) std::snprintf(out + 8 * i, 9, "%08x", c.h[i]);
  return std::string(out, 64);
}
static std::string of_file(const std::string& path) {
  std::ifstream f(path, std::ios::binary);
  if (!f) die(2, "sha256_open_failed path=%s", path.c_str());
  Ctx c;
  std::vector<char> buf(1 << 16);
  for (;;) {
    f.read(buf.data(), (std::streamsize)buf.size());
    const std::streamsize n = f.gcount();
    if (n > 0) update(c, (const unsigned char*)buf.data(), (size_t)n);
    if (n < (std::streamsize)buf.size()) break;
  }
  return finish(c);
}
}  // namespace sha256

// ------------------------------------------------------------- per-m run ----
struct RunMetrics {
  int m = 0;
  u64 states = 0, transitions = 0, truncated = 0;
  double wall_s = 0, peak_rss_mb = 0;
};

// Returns Z[w][n] mod 4 for w = 0..cols, n = 0..nmax.
static std::vector<std::vector<uint8_t>> run_m(const Config& cfg, int m,
                                               RunMetrics* met) {
  const int len = m + 1;
  const int nmax = cfg.nmax;
  const int slot_cap =
      (cfg.mutant == Mutant::kSlot40) ? nmax - 1 : nmax;  // RED: loses n = nmax
  if (slot_cap < 0) die(1, "slot_cap_negative nmax=%d", nmax);

  Ranker rk;
  rk.build(len);
  if (rk.total == 0 || rk.total > kMaxStates)
    die(78, "state_space_out_of_bounds m=%d states=%llu limit=%llu", m,
        (unsigned long long)rk.total, (unsigned long long)kMaxStates);
  verify_language(rk, len <= 17 || cfg.verify_rank == 1);

  // Lane masks for the kept area slots. Slots 0..31 live in lo, 32..47 in hi.
  u64 lo_keep = 0;
  u32 hi_keep = 0;
  for (int s = 0; s <= slot_cap; s++) {
    if (s < 32) lo_keep |= (u64)0x3 << (2 * s);
    else hi_keep |= (u32)0x3 << (2 * (s - 32));
  }

  Buf a, b;
  a.alloc((size_t)rk.total);
  b.alloc((size_t)rk.total);
  a.lo[0] = 1;  // rank 0 is the all-E frontier; area 0, weight 1

  const bool verify =
      cfg.verify_rank >= 0 ? (cfg.verify_rank != 0) : (m <= 10);

  const auto t0 = std::chrono::steady_clock::now();
  StageStats tot;
  std::vector<std::vector<uint8_t>> Z((size_t)cfg.cols + 1,
                                      std::vector<uint8_t>((size_t)nmax + 1, 0));
  Z[0][0] = 1;  // the empty prefix: Z_{0,m}(0) = 1

  Buf* src = &a;
  Buf* dst = &b;
  for (int col = 0; col < cfg.cols; col++) {
    for (int r = 0; r < m; r++) {
      if (cfg.inject && cfg.inj_m == m && cfg.inj_col == col &&
          cfg.inj_stage == r) {
        // Flip one mod-4 lane in the lowest-indexed live state. This is the
        // uncompared-cell path: nothing else in the run notices.
        u64 hit = ~(u64)0;
        for (u64 i = 0; i < rk.total; i++)
          if (src->lo[i] || src->hi[i]) { hit = i; break; }
        if (hit == ~(u64)0) die(72, "inject_no_live_state m=%d col=%d stage=%d",
                                m, col, r);
        const int s = cfg.inj_slot;
        if (s < 32) add4(src->lo[hit], src->hi[hit], (u64)1 << (2 * s), 0);
        else add4(src->lo[hit], src->hi[hit], 0, (u32)1 << (2 * (s - 32)));
        std::fprintf(stderr,
                     "event=inject job=r4_spin_engine m=%d col=%d stage=%d "
                     "state=%llu slot=%d\n",
                     m, col, r, (unsigned long long)hit, s);
        std::fflush(stderr);
      }

      dst->zero();
      StagePlan P{&rk, src, dst, m, r, r == m - 1, cfg.use_nw(), cfg.use_sw(),
                  slot_cap, lo_keep, hi_keep, verify};
      if (cfg.threads <= 1) {
        StageStats st;
        run_stage<false>(P, 0, rk.total, &st);
        tot.transitions += st.transitions;
        tot.truncated += st.truncated;
        tot.stage0_invariant_violations += st.stage0_invariant_violations;
      } else {
#if !SPIN_HAVE_ATOMIC_REF
        die(78, "threads_unsupported_no_atomic_ref");
#else
        const int T = cfg.threads;
        std::vector<StageStats> sts((size_t)T);
        std::vector<std::thread> th;
        th.reserve((size_t)T);
        for (int t = 0; t < T; t++) {
          const u64 i0 = rk.total * (u64)t / (u64)T;
          const u64 i1 = rk.total * (u64)(t + 1) / (u64)T;
          if (i0 >= i1) continue;
          th.emplace_back([&, i0, i1, t] { run_stage<true>(P, i0, i1, &sts[(size_t)t]); });
        }
        for (auto& x : th) x.join();
        for (const auto& s : sts) {
          tot.transitions += s.transitions;
          tot.truncated += s.truncated;
          tot.stage0_invariant_violations += s.stage0_invariant_violations;
        }
#endif
      }
      std::swap(src, dst);
    }
    // Column boundary: Z_{col+1,m}(n) = sum of the payloads over all states.
    u64 hlo = 0;
    u32 hhi = 0;
    for (u64 i = 0; i < rk.total; i++) add4(hlo, hhi, src->lo[i], src->hi[i]);
    for (int n = 0; n <= nmax; n++)
      Z[(size_t)col + 1][(size_t)n] =
          (uint8_t)(n < 32 ? (hlo >> (2 * n)) & 0x3 : (hhi >> (2 * (n - 32))) & 0x3);
    g_progress += 1;
    if (g_rep)
      g_rep->beat(g_progress,
                  "m=" + std::to_string(m) + " col=" + std::to_string(col + 1) +
                      " states=" + std::to_string(rk.total));
  }

  if (tot.stage0_invariant_violations)
    die(78, "carry_invariant_violated m=%d count=%llu", m,
        (unsigned long long)tot.stage0_invariant_violations);

  met->m = m;
  met->states = rk.total;
  met->transitions = tot.transitions;
  met->truncated = tot.truncated;
  met->wall_s =
      std::chrono::duration<double>(std::chrono::steady_clock::now() - t0).count();
  a.release();
  b.release();
  met->peak_rss_mb = obs::rss_mb();
  return Z;
}

// ---------------------------------------------------------------- oracle ----
// C<H>.out lines are "n value", value an exact decimal integer far beyond u64.
// Only the residue is needed, so it is reduced digit by digit; no bignum.
static bool load_oracle_row(const std::string& dir, int H, int nmax,
                            std::vector<int>* c4) {
  char path[1024];
  std::snprintf(path, sizeof path, "%s/C%d.out", dir.c_str(), H);
  std::ifstream f(path);
  if (!f) return false;
  c4->assign((size_t)nmax + 1, -1);
  std::string line;
  while (std::getline(f, line)) {
    std::istringstream is(line);
    long long n = 0;
    std::string val;
    if (!(is >> n >> val)) continue;
    if (n < 0 || n > nmax) continue;
    int acc = 0;
    for (char ch : val) {
      if (ch < '0' || ch > '9') { acc = -1; break; }
      acc = (acc * 10 + (ch - '0')) % 4;
    }
    if (acc < 0) return false;
    (*c4)[(size_t)n] = acc;
  }
  return true;
}

// ------------------------------------------------------------------ main ----
int main(int argc, char** argv) {
  Config cfg;
  bool dense = false, saw_mod = false;

  auto need = [&](int i, const char* what) {
    if (i >= argc) die(1, "missing value for %s", what);
    return argv[i];
  };
  for (int i = 1; i < argc; i++) {
    const std::string k = argv[i];
    if (k == "--m") {
      const std::string v = need(++i, "--m");
      const size_t dots = v.find("..");
      if (dots == std::string::npos) {
        cfg.mlo = cfg.mhi = (int)argparse::ArgInt(v.c_str(), "--m", 1, kMaxM);
      } else {
        cfg.mlo = (int)argparse::ArgInt(v.substr(0, dots).c_str(), "--m lo", 1, kMaxM);
        cfg.mhi = (int)argparse::ArgInt(v.substr(dots + 2).c_str(), "--m hi", 1, kMaxM);
      }
      if (cfg.mlo > cfg.mhi) die(1, "--m lo > hi");
    } else if (k == "--cols") {
      cfg.cols = (int)argparse::ArgInt(need(++i, "--cols"), "--cols", 1, 4096);
    } else if (k == "--nmax") {
      cfg.nmax = (int)argparse::ArgInt(need(++i, "--nmax"), "--nmax", 1, kMaxNmax);
    } else if (k == "--mod") {
      const long v = argparse::ArgInt(need(++i, "--mod"), "--mod", 4, 4);
      (void)v;
      saw_mod = true;
    } else if (k == "--dense-rank") {
      dense = true;
    } else if (k == "--oracle") {
      cfg.oracle = need(++i, "--oracle");
    } else if (k == "--out") {
      cfg.out = need(++i, "--out");
    } else if (k == "--report-rss") {
      cfg.report_rss = true;
    } else if (k == "--threads") {
      cfg.threads = (int)argparse::ArgInt(need(++i, "--threads"), "--threads", 1, 512);
    } else if (k == "--verify-rank") {
      cfg.verify_rank =
          (int)argparse::ArgInt(need(++i, "--verify-rank"), "--verify-rank", 0, 1);
    } else if (k == "--expect-flips") {
      cfg.expect_flips =
          argparse::ArgInt(need(++i, "--expect-flips"), "--expect-flips", 0, 1 << 20);
    } else if (k == "--mutant") {
      const std::string v = need(++i, "--mutant");
      if (v == "none") cfg.mutant = Mutant::kNone;
      else if (v == "drop-nw") cfg.mutant = Mutant::kDropNw;
      else if (v == "drop-sw") cfg.mutant = Mutant::kDropSw;
      else if (v == "rook") cfg.mutant = Mutant::kRook;
      else if (v == "slot40") cfg.mutant = Mutant::kSlot40;
      else if (v == "noharvestdiff") cfg.mutant = Mutant::kNoHarvestDiff;
      else die(1, "unknown --mutant '%s'", v.c_str());
    } else if (k == "--inject") {
      const std::string v = need(++i, "--inject");
      int a1 = 0, a2 = 0, a3 = 0, a4v = 0;
      if (std::sscanf(v.c_str(), "%d,%d,%d,%d", &a1, &a2, &a3, &a4v) != 4)
        die(1, "--inject wants <m>,<col>,<stage>,<slot>");
      cfg.inject = true;
      cfg.inj_m = a1; cfg.inj_col = a2; cfg.inj_stage = a3; cfg.inj_slot = a4v;
    } else {
      die(1, "unknown argument '%s'", k.c_str());
    }
  }

  if (!cfg.mhi || !cfg.cols || !cfg.nmax || cfg.out.empty())
    die(1, "usage: %s --m <lo>..<hi> --cols C --nmax N --mod 4 --dense-rank "
           "--oracle DIR --out FILE [--mutant M] [--inject m,col,stage,slot] "
           "[--expect-flips K] [--threads T] [--verify-rank 0|1] [--report-rss]",
        argv[0]);
  if (!saw_mod) die(1, "--mod 4 is required (no other payload modulus exists)");
  if (!dense)
    die(1, "--dense-rank is required: dense ranking is mandatory per "
           "results/r4/r4-inv.md section 1.3, and no keyed path is implemented");
  if (cfg.oracle.empty())
    die(79, "refused: no --oracle, so this run would check nothing");
  if (cfg.cols < cfg.nmax + 1)
    die(1, "--cols %d < nmax+1 = %d: A_m(n) needs Z at w = n+1", cfg.cols,
        cfg.nmax + 1);
  if (!cfg.use_w())
    die(78, "the W constraint may not be dropped: the dense index space is the "
            "Hamiltonian-path language that encodes it");
  if (cfg.inject &&
      (cfg.inj_m < cfg.mlo || cfg.inj_m > cfg.mhi || cfg.inj_col < 0 ||
       cfg.inj_col >= cfg.cols || cfg.inj_stage < 0 ||
       cfg.inj_stage >= cfg.inj_m || cfg.inj_slot < 0 || cfg.inj_slot > cfg.nmax))
    die(1, "--inject target is outside the run");

  obs::Reporter rep("r4_spin_engine",
                    (double)(cfg.mhi - cfg.mlo + 1) * cfg.cols,
                    "m=" + std::to_string(cfg.mlo) + ".." + std::to_string(cfg.mhi) +
                        " cols=" + std::to_string(cfg.cols) +
                        " nmax=" + std::to_string(cfg.nmax) +
                        " mutant=" + mutant_name(cfg.mutant) +
                        " threads=" + std::to_string(cfg.threads) +
                        " inject=" + (cfg.inject ? "yes" : "no"));
  g_rep = &rep;

  // ---------------- PHASE A: compute, write, hash. No oracle is opened. ----
  const int nmax = cfg.nmax;
  std::vector<std::vector<uint8_t>> A((size_t)cfg.mhi + 1),
      Astab((size_t)cfg.mhi + 1);
  std::vector<RunMetrics> mets;
  for (int m = cfg.mlo; m <= cfg.mhi; m++) {
    RunMetrics met;
    const auto Z = run_m(cfg, m, &met);
    mets.push_back(met);
    A[(size_t)m].assign((size_t)nmax + 1, 0);
    Astab[(size_t)m].assign((size_t)nmax + 1, 0);
    for (int n = 1; n <= nmax; n++) {
      const int zn = Z[(size_t)n][(size_t)n];
      const int zn1 = Z[(size_t)n - 1][(size_t)n];
      const int zp1 = Z[(size_t)n + 1][(size_t)n];
      if (cfg.mutant == Mutant::kNoHarvestDiff) {
        // RED: drop the width-translation fix and harvest the raw Z.
        A[(size_t)m][(size_t)n] = (uint8_t)zn;
        Astab[(size_t)m][(size_t)n] = (uint8_t)zp1;
      } else {
        A[(size_t)m][(size_t)n] = (uint8_t)((zn - zn1 + 4) % 4);
        Astab[(size_t)m][(size_t)n] = (uint8_t)((zp1 - zn + 4) % 4);
      }
    }
    rep.beat(g_progress,
             "m_done=" + std::to_string(m) +
                 " states=" + std::to_string(met.states) +
                 " wall_s=" + std::to_string(met.wall_s) +
                 " peak_rss_mb=" + std::to_string(met.peak_rss_mb),
             true);
  }

  // T(n,H) for the H whose three strip heights were all run. A_m := 0 for m < 1.
  auto Aof = [&](int m, int n, bool stab) -> int {
    if (m < 1) return 0;
    return stab ? Astab[(size_t)m][(size_t)n] : A[(size_t)m][(size_t)n];
  };
  struct Cell { int H, n, par; };
  std::vector<Cell> cells;
  u64 struct_checks = 0, struct_fail = 0;
  for (int H = cfg.mlo; H <= cfg.mhi; H++) {
    bool have = true;
    for (int d = 0; d < 3; d++) {
      const int mm = H - d;
      if (mm >= 1 && (mm < cfg.mlo || mm > cfg.mhi)) have = false;
    }
    if (!have) continue;
    for (int n = 1; n <= nmax; n++) {
      const int g = (Aof(H, n, false) + 2 * Aof(H - 1, n, false) +
                     Aof(H - 2, n, false)) % 4;   // -2a == +2a (mod 4)
      const int gs = (Aof(H, n, true) + 2 * Aof(H - 1, n, true) +
                      Aof(H - 2, n, true)) % 4;
      struct_checks += 2;
      if (g != gs) struct_fail++;
      if (g % 2 != 0) struct_fail++;
      cells.push_back({H, n, (g % 4) / 2});
    }
  }
  if (cells.empty()) die(3, "no reportable H in --m %d..%d", cfg.mlo, cfg.mhi);

  // The output file carries ONLY mathematical content, so runs that differ in
  // thread count, box or ISA must be byte-identical and their sha256s equal.
  {
    FILE* f = std::fopen(cfg.out.c_str(), "w");
    if (!f) die(2, "cannot write %s", cfg.out.c_str());
    std::fprintf(f, "# r4_spin_engine spin-basis parity, T(n,H) mod 2\n");
    std::fprintf(f, "# m=%d..%d cols=%d nmax=%d mod=4 dense_rank=1 mutant=%s inject=%s\n",
                 cfg.mlo, cfg.mhi, cfg.cols, cfg.nmax, mutant_name(cfg.mutant),
                 cfg.inject ? "yes" : "no");
    for (int m = cfg.mlo; m <= cfg.mhi; m++)
      for (int n = 1; n <= nmax; n++)
        std::fprintf(f, "A m=%d n=%d a4=%d\n", m, n, (int)A[(size_t)m][(size_t)n]);
    for (const auto& c : cells)
      std::fprintf(f, "T H=%d n=%d par=%d\n", c.H, c.n, c.par);
    std::fprintf(f, "X structural_checks=%llu structural_failures=%llu\n",
                 (unsigned long long)struct_checks, (unsigned long long)struct_fail);
    if (std::fclose(f) != 0) die(2, "cannot close %s", cfg.out.c_str());
  }
  const std::string digest = sha256::of_file(cfg.out);
  std::fprintf(stderr, "event=harvest job=r4_spin_engine out=%s sha256=%s cells=%zu\n",
               cfg.out.c_str(), digest.c_str(), cells.size());
  std::fflush(stderr);

  {
    const std::string mpath = cfg.out + ".metrics";
    FILE* f = std::fopen(mpath.c_str(), "w");
    if (!f) die(2, "cannot write %s", mpath.c_str());
    std::fprintf(f, "# measurements; deliberately NOT in %s so that file's "
                    "sha256 is comparable across boxes and thread counts\n",
                 cfg.out.c_str());
    std::fprintf(f, "sha256 %s\n", digest.c_str());
    for (const auto& k : mets) {
      const double slot_ops = (double)k.transitions * (double)(nmax + 1);
      std::fprintf(f,
                   "K m=%d states=%llu transitions=%llu slot_ops=%.6g wall_s=%.3f "
                   "peak_rss_mb=%.1f bytes_per_state=%.2f ns_per_slot_op=%.4f "
                   "ns_per_transition=%.4f truncated=%llu\n",
                   k.m, (unsigned long long)k.states,
                   (unsigned long long)k.transitions, slot_ops, k.wall_s,
                   k.peak_rss_mb,
                   k.states ? k.peak_rss_mb * 1048576.0 / (double)k.states : 0.0,
                   slot_ops > 0 ? k.wall_s * 1e9 / slot_ops : 0.0,
                   k.transitions ? k.wall_s * 1e9 / (double)k.transitions : 0.0,
                   (unsigned long long)k.truncated);
    }
    if (std::fclose(f) != 0) die(2, "cannot close %s", mpath.c_str());
  }

  if (cfg.report_rss)
    for (const auto& k : mets)
      if (!(k.peak_rss_mb > 0) || !(k.wall_s > 0) || k.transitions == 0)
        die(74, "report_rss_incomplete m=%d rss=%.3f wall=%.3f trans=%llu", k.m,
            k.peak_rss_mb, k.wall_s, (unsigned long long)k.transitions);

  // ---------------- PHASE B: re-read the written file, then compare. -------
  // Deliberately parsed back off disk: the comparison cannot see an in-memory
  // value, so a debugger who knows the banked answers cannot shortcut it.
  std::vector<Cell> from_disk;
  {
    std::ifstream f(cfg.out);
    if (!f) die(2, "cannot re-read %s", cfg.out.c_str());
    std::string line;
    while (std::getline(f, line)) {
      int H = 0, n = 0, p = 0;
      if (std::sscanf(line.c_str(), "T H=%d n=%d par=%d", &H, &n, &p) == 3)
        from_disk.push_back({H, n, p});
    }
  }
  if (from_disk.size() != cells.size())
    die(2, "readback_size_mismatch wrote=%zu read=%zu", cells.size(),
        from_disk.size());

  std::vector<std::vector<int>> C4((size_t)cfg.mhi + 1);
  for (int H = 1; H <= cfg.mhi; H++) {
    std::vector<int> row;
    if (load_oracle_row(cfg.oracle, H, nmax, &row)) C4[(size_t)H] = row;
  }
  auto oracle_par = [&](int H, int n, int* par) -> bool {
    int acc = 0;
    for (int d = 0; d < 3; d++) {
      const int mm = H - d;
      if (mm < 1) continue;
      if ((size_t)mm >= C4.size() || C4[(size_t)mm].empty()) return false;
      const int v = C4[(size_t)mm][(size_t)n];
      if (v < 0) return false;
      acc += (d == 1 ? 2 * v : v);  // C_H - 2C_{H-1} + C_{H-2}, mod 4
    }
    *par = (acc % 4) % 2;
    return true;
  };

  // Two tallies, because the two fixtures live in different domains. The full
  // tally is the 640-cell oracle (H = 1..16 x n = 1..40, cells with H > n
  // included: both routes give T = 0 there, since C_H and A_m are linear in the
  // strip height once the height exceeds n, so the second difference vanishes).
  // The H <= n tally is the domain r3_spin_pipeline.py reports, and is the one
  // round 3's 12 / 12 / 4 mutant flip counts were measured over; --expect-flips
  // is compared against it so those fixtures transfer unchanged.
  u64 compared = 0, mismatch = 0, compared_hlen = 0, mismatch_hlen = 0;
  for (const auto& c : from_disk) {
    int want = 0;
    if (!oracle_par(c.H, c.n, &want)) continue;
    compared++;
    if (c.H <= c.n) compared_hlen++;
    if (want != c.par) {
      mismatch++;
      if (c.H <= c.n) mismatch_hlen++;
      if (mismatch <= 20)
        std::printf("MISMATCH H=%d n=%d engine=%d oracle=%d\n", c.H, c.n, c.par,
                    want);
    }
  }
  std::printf("oracle=%s compared=%llu mismatch=%llu compared_hlen=%llu "
              "mismatch_hlen=%llu mutant=%s inject=%s structural_checks=%llu "
              "structural_failures=%llu sha256=%s\n",
              cfg.oracle.c_str(), (unsigned long long)compared,
              (unsigned long long)mismatch, (unsigned long long)compared_hlen,
              (unsigned long long)mismatch_hlen, mutant_name(cfg.mutant),
              cfg.inject ? "yes" : "no", (unsigned long long)struct_checks,
              (unsigned long long)struct_fail, digest.c_str());
  std::fflush(stdout);
  rep.done("compared=" + std::to_string(compared) +
           " mismatch=" + std::to_string(mismatch) +
           " mismatch_hlen=" + std::to_string(mismatch_hlen) +
           " mutant=" + mutant_name(cfg.mutant) + " sha256=" + digest);

  // ---------------- exit contract (results/r4/r4-inv.md section 3.4) -------
  if (compared == 0)
    die(3, "no_oracle_cells_compared dir=%s -- a check that cannot fail is not "
           "a check", cfg.oracle.c_str());

  if (cfg.expect_flips >= 0 && (u64)cfg.expect_flips != mismatch_hlen)
    die(71, "flip_set_size_mismatch expected=%ld measured_hlen=%llu total=%llu",
        cfg.expect_flips, (unsigned long long)mismatch_hlen,
        (unsigned long long)mismatch);

  if (cfg.red()) {
    // A RED that agrees with the oracle everywhere is a gate-DESIGN failure:
    // it means the battery cannot see the fault it was built to see.
    if (mismatch == 0)
      die(cfg.mutant != Mutant::kNone ? 71 : 72,
          "RED produced an EMPTY flip set: mutant=%s inject=%s",
          mutant_name(cfg.mutant), cfg.inject ? "yes" : "no");
    return 0;
  }

  if (struct_fail)
    die(76, "structural_check_failed count=%llu (bookkeeping check, blind to "
            "stencil errors -- never a correctness certificate)",
        (unsigned long long)struct_fail);
  if (mismatch)
    die(cfg.nmax <= 7 ? 70 : 73, "oracle_mismatch count=%llu of %llu",
        (unsigned long long)mismatch, (unsigned long long)compared);
  return 0;
}
