// motley_par.cpp — PARALLEL colour-symmetrized spin transfer matrix (Motley).
//
// Same rule, same answer, more cores.  `docs/b1-closure-plan.md` §4 names the
// wall this file removes: "The engine is still single-threaded ... the wall
// figures demand a parallel frontier that does not exist yet.  RAM is the wall
// this document plans around; cores are the next one."  Confetti (H = 18) spent
// 399,700 s of wall on ONE core of an 80-core box.
//
// THE RULE IS NOT MINE TO CHANGE.  `slot`, `canon`, `gather`, `shifted` and
// `successors` below are transcribed character for character from the frozen
// spec `results/cutcount_b1/cutcount_b1.cpp.59e90660` (sha256 59e90660...,
// lines 93-173), which is what `docs/proofs/cutcount-identity.md` proves and
// what every banked C_H row was produced by.  Everything else in this file --
// the table, the parallelism, the payload width, the checkpoint -- is
// accounting, and the gate is that the rows come out byte-identical.
//
// What is different from `cutcount_b1 --modp`:
//   * open-addressed flat table (24 B/bucket) + a contiguous payload slab,
//     instead of unordered_map + one heap vector per state per cell-step;
//   * the cell-step is an OpenMP parallel loop over source buckets, with
//     lock-free find-or-insert and a per-state spinlock over the n-loop;
//   * payload width is a template parameter picked from the prime: p < 2^8
//     -> u8, p < 2^16 -> u16, else u32.  Same C_H(n) mod p either way;
//   * column-boundary checkpoint / resume, because a multi-day pass that
//     cannot be interrupted is a defect (docs/job-checklist.md §5).
//
// Modes:
//   motley_par --census <H> <Nmax> [--threads T]
//        reachable frontier states per cell-step; no payload.  This is the
//        measurement docs/b1-closure-plan.md §2 projects with a +-20% census
//        ratio.
//   motley_par --modp <H> <Nmax> <p> <outfile> [--threads T] [--ckpt DIR]
//        C_H(n) mod p for n = 1..Nmax, "n value" lines, same format as
//        cutcount_b1 --modp.
//
// Events (obs.h) on stderr; stdout is the human-readable report.

#include <atomic>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <chrono>
#include <string>
#include <vector>
#include <omp.h>
#include "obs.h"

static obs::Reporter* g_rep = nullptr;

using u64 = uint64_t;
using u32 = uint32_t;
using u128 = unsigned __int128;

// ===================== rule core (frozen spec, verbatim) =====================

static const int BITS = 5;
static const u128 SLOTMASK = 0x1F;
static const int SUCC_CAP = 32;
static const int HMAX_KEY = 24;

static inline void check_height(int H) {
  if ((H + 1) * BITS > 128) { fprintf(stderr, "FATAL key_width H=%d\n", H); std::exit(2); }
  if (H / 2 + 1 > (int)SLOTMASK) { fprintf(stderr, "FATAL slot_width H=%d\n", H); std::exit(2); }
  if (H / 2 + 2 > SUCC_CAP) { fprintf(stderr, "FATAL succ_cap H=%d\n", H); std::exit(2); }
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
static inline int successors(u128 key, int H, int r, int c, Succ out[SUCC_CAP]) {
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

// ============================ concurrent table ==============================
//
// Open addressing, linear probing, insert-only, one slab of payload rows.  A
// bucket's `idx` is the state's payload row and doubles as the publication
// flag: EMPTY -> CLAIM (one winner, by CAS) -> the row number, released after
// the key and the zeroed payload row are in place.  A reader that sees a
// published index has, by the release/acquire pair, also seen the key.

static const u32 IDX_EMPTY = 0xFFFFFFFFu;
static const u32 IDX_CLAIM = 0xFFFFFFFEu;

struct Bucket {
  u64 lo, hi;
  std::atomic<u32> idx;
  u32 pad;
};

// A thread's private slice of the index space.  The row counter is the one
// truly global write in the cell-step, so it is handed out in blocks: 80
// threads doing fetch_add per insertion serialise on one cache line and cost
// more than the insertion.
struct Alloc {
  size_t next = 0, end = 0;
};
static const size_t ALLOC_BLOCK = 256;

static inline size_t keyhash(u128 k) {
  u64 lo = (u64)k, hi = (u64)(k >> 64);
  u64 h = lo * 0x9E3779B97F4A7C15ull ^ (hi + 0x9E3779B97F4A7C15ull + (lo << 6) + (lo >> 2));
  return (size_t)(h ^ (h >> 29));
}

static inline void cpu_relax() {
#if defined(__aarch64__)
  __asm__ __volatile__("yield");
#elif defined(__x86_64__)
  __builtin_ia32_pause();
#endif
}

// One frontier buffer: bucket array (power-of-two), payload slab, spinlocks.
struct Buf {
  Bucket* b = nullptr;
  size_t nb = 0;                 // bucket count, power of two
  size_t cap = 0;                // payload rows allocated
  unsigned char* pay = nullptr;  // cap * stride; row = [lock u32][pad][payload]
  size_t rowbytes = 0;           // payload bytes per row
  size_t stride = 0;             // rowbytes + LOCKOFF, 0 in census mode
  alignas(64) std::atomic<size_t> n{0};
  alignas(64) std::atomic<int> overflow{0};

  static const size_t LOCKOFF = 8;   // the spinlock shares the row's cache line
  inline unsigned char* row(size_t id) const { return pay + id * stride; }
  inline std::atomic<u32>* rowlock(size_t id) const {
    return reinterpret_cast<std::atomic<u32>*>(row(id));
  }
  inline unsigned char* rowpay(size_t id) const { return row(id) + LOCKOFF; }

  void release() {
    std::free(b); std::free(pay);
    b = nullptr; pay = nullptr; nb = cap = 0;
  }
  // Size for at least `want` states; keeps existing allocation when it fits.
  void ensure(size_t want, size_t rb) {
    want += (size_t)omp_get_max_threads() * ALLOC_BLOCK;
    size_t needb = 1;
    while (needb < want * 3 / 2) needb <<= 1;   // load factor <= 2/3
    if (needb < 1024) needb = 1024;
    if (needb > nb || want > cap || rb != rowbytes) {
      release();
      nb = needb; cap = want; rowbytes = rb;
      stride = rb ? rb + LOCKOFF : 0;
      b = (Bucket*)std::malloc(nb * sizeof(Bucket));
      pay = rb ? (unsigned char*)std::malloc(cap * stride) : nullptr;
      if (!b || (rb && !pay)) {
        fprintf(stderr, "FATAL alloc buckets=%zu cap=%zu rowbytes=%zu\n", nb, cap, rb);
        std::exit(3);
      }
    }
  }
  void clear() {
    n.store(0, std::memory_order_relaxed);
    overflow.store(0, std::memory_order_relaxed);
#pragma omp parallel for schedule(static)
    for (size_t i = 0; i < nb; i++) b[i].idx.store(IDX_EMPTY, std::memory_order_relaxed);
  }
  inline u128 key(size_t i) const { return ((u128)b[i].hi << 64) | b[i].lo; }

  // `n` is the reservation high-water, not the population: block allocation
  // leaves a partial block per thread unused.  Counting means scanning.
  size_t count_states() const {
    size_t tot = 0;
#pragma omp parallel for schedule(static) reduction(+ : tot)
    for (size_t i = 0; i < nb; i++)
      if (b[i].idx.load(std::memory_order_relaxed) < IDX_CLAIM) tot++;
    return tot;
  }

  // Returns the payload row for `k`, inserting it (zeroed) if new.
  // Returns IDX_EMPTY on capacity overflow (caller retries the whole step).
  inline u32 find_or_insert(u128 k, Alloc& al) {
    size_t h = keyhash(k) & (nb - 1);
    for (;;) {
      Bucket& B = b[h];
      u32 v = B.idx.load(std::memory_order_acquire);
      if (v == IDX_EMPTY) {
        u32 exp = IDX_EMPTY;
        if (B.idx.compare_exchange_strong(exp, IDX_CLAIM, std::memory_order_acq_rel,
                                          std::memory_order_acquire)) {
          if (al.next == al.end) {
            al.next = n.fetch_add(ALLOC_BLOCK, std::memory_order_relaxed);
            al.end = al.next + ALLOC_BLOCK;
          }
          size_t id = al.next++;
          if (id >= cap) {
            overflow.store(1, std::memory_order_relaxed);
            B.idx.store(IDX_EMPTY, std::memory_order_release);
            return IDX_EMPTY;
          }
          B.lo = (u64)k; B.hi = (u64)(k >> 64);
          if (stride) std::memset(row(id), 0, stride);
          B.idx.store((u32)id, std::memory_order_release);
          return (u32)id;
        }
        v = exp;
      }
      while (v == IDX_CLAIM) { cpu_relax(); v = B.idx.load(std::memory_order_acquire); }
      if (v != IDX_EMPTY && B.lo == (u64)k && B.hi == (u64)(k >> 64)) return v;
      h = (h + 1) & (nb - 1);
    }
  }
};

static inline void lock_row(std::atomic<u32>* a) {
  u32 exp = 0;
  while (!a->compare_exchange_weak(exp, 1, std::memory_order_acquire,
                                   std::memory_order_relaxed)) {
    exp = 0;
    cpu_relax();
  }
}
static inline void unlock_row(std::atomic<u32>* a) {
  a->store(0, std::memory_order_release);
}

// ============================== census mode =================================

static void census(int H, int Nmax) {
  check_height(H);
  const int W = Nmax + 1;
  Buf a, b;
  a.ensure(1024, 0); a.clear();
  { Alloc al; a.find_or_insert(0, al); }
  Buf* cur = &a; Buf* nxt = &b;
  size_t maxstates = 0;
  auto t0 = std::chrono::steady_clock::now();
  for (int c = 0; c < W; c++) {
    for (int r = 0; r < H; r++) {
      size_t ns = cur->count_states();
      size_t want = ns + ns / 4 + 4096;
      for (;;) {
        nxt->ensure(want, 0);
        nxt->clear();
#pragma omp parallel
        {
          Alloc al;
#pragma omp for schedule(dynamic, 512)
          for (size_t i = 0; i < cur->nb; i++) {
            u32 sid = cur->b[i].idx.load(std::memory_order_relaxed);
            if (sid >= IDX_CLAIM) continue;
            Succ s[SUCC_CAP];
            int m = successors(cur->key(i), H, r, c, s);
            for (int j = 0; j < m; j++)
              if (nxt->find_or_insert(s[j].key, al) == IDX_EMPTY) break;
          }
        }
        if (!nxt->overflow.load()) break;
        want *= 2;
        fprintf(stderr, "census regrow c=%d r=%d want=%zu\n", c, r, want);
      }
      std::swap(cur, nxt);
      maxstates = std::max(maxstates, cur->count_states());
    }
    size_t ncur = cur->count_states();
    double dt = std::chrono::duration<double>(std::chrono::steady_clock::now() - t0).count();
    printf("col %d states %zu max %zu wall %.1f\n", c, ncur, maxstates, dt);
    fflush(stdout);
    if (g_rep) g_rep->beat(c + 1, "census H=" + std::to_string(H) +
                                      " states=" + std::to_string(ncur));
  }
  printf("H %d maxstates %zu\n", H, maxstates);
}

// ============================== mod-p engine ================================

template <class T>
static void step_modp(Buf* cur, Buf* nxt, int H, int Nmax, int r, int c, u64 p) {
  const int NA = Nmax + 1;
#pragma omp parallel
  {
    Alloc al;
#pragma omp for schedule(dynamic, 1024)
    for (size_t i = 0; i < cur->nb; i++) {
      u32 sid = cur->b[i].idx.load(std::memory_order_relaxed);
      if (sid >= IDX_CLAIM) continue;
      Succ s[SUCC_CAP];
      int m = successors(cur->key(i), H, r, c, s);
      const T* P = (const T*)cur->rowpay(sid);
      for (int j = 0; j < m; j++) {
        u64 m0 = (u64)((s[j].m0 % (int64_t)p + (int64_t)p) % (int64_t)p);
        u64 m1 = (u64)(s[j].m1 % (int64_t)p);
        int dn = s[j].dn;
        u32 did = nxt->find_or_insert(s[j].key, al);
        if (did == IDX_EMPTY) break;             // overflow; step will be redone
        T* Q = (T*)nxt->rowpay(did);
        lock_row(nxt->rowlock(did));
        for (int n = 0; n + dn <= Nmax; n++) {
          u64 c0 = P[2 * n], c1 = P[2 * n + 1];
          if (!(c0 | c1)) continue;
          T& d0 = Q[2 * (n + dn)];
          T& d1 = Q[2 * (n + dn) + 1];
          d0 = (T)((d0 + c0 * m0) % p);
          d1 = (T)((d1 + c1 * m0 + c0 * m1) % p);
        }
        unlock_row(nxt->rowlock(did));
      }
    }
  }
}

// Column-boundary sums, per stream and area.
template <class T>
static void column_sum(Buf* cur, int Nmax, u64 p, std::vector<u64>& out) {
  const int NA = Nmax + 1;
  std::fill(out.begin(), out.end(), 0);
  const int nth = omp_get_max_threads();
  std::vector<u64> part((size_t)nth * 2 * NA, 0);
#pragma omp parallel
  {
    int t = omp_get_thread_num();
    u64* q = part.data() + (size_t)t * 2 * NA;
#pragma omp for schedule(static)
    for (size_t i = 0; i < cur->nb; i++) {
      u32 id = cur->b[i].idx.load(std::memory_order_relaxed);
      if (id >= IDX_CLAIM) continue;
      const T* row = (const T*)cur->rowpay(id);
      for (int k = 0; k < 2 * NA; k++) q[k] = (q[k] + row[k]) % p;
    }
  }
  for (int t = 0; t < nth; t++)
    for (int k = 0; k < 2 * NA; k++)
      out[k] = (out[k] + part[(size_t)t * 2 * NA + k]) % p;
}

// checkpoint format: magic, H, Nmax, p, sizeof(T), column, nstates,
// then per state: key lo, key hi, payload row.  fprev/fcur follow.
static const u64 CKPT_MAGIC = 0x4D4F544C45593031ull;  // "MOTLEY01"

template <class T>
static bool ckpt_write(const char* path, Buf* cur, int H, int Nmax, u64 p, int col,
                       const std::vector<u64>& fprev, const std::vector<u64>& fcur) {
  std::string tmp = std::string(path) + ".tmp";
  FILE* f = fopen(tmp.c_str(), "wb");
  if (!f) return false;
  const int NA = Nmax + 1;
  u64 hdr[7] = { CKPT_MAGIC, (u64)H, (u64)Nmax, p, (u64)sizeof(T), (u64)col,
                 (u64)cur->count_states() };
  bool ok = fwrite(hdr, sizeof hdr, 1, f) == 1;
  ok = ok && fwrite(fprev.data(), sizeof(u64), 2 * NA, f) == (size_t)(2 * NA);
  ok = ok && fwrite(fcur.data(), sizeof(u64), 2 * NA, f) == (size_t)(2 * NA);
  for (size_t i = 0; ok && i < cur->nb; i++) {
    u32 id = cur->b[i].idx.load(std::memory_order_relaxed);
    if (id >= IDX_CLAIM) continue;
    u64 kk[2] = { cur->b[i].lo, cur->b[i].hi };
    ok = fwrite(kk, sizeof kk, 1, f) == 1 &&
         fwrite(cur->rowpay(id), sizeof(T), 2 * NA, f) == (size_t)(2 * NA);
  }
  ok = ok && fflush(f) == 0;
  fclose(f);
  if (!ok) { remove(tmp.c_str()); return false; }
  return rename(tmp.c_str(), path) == 0;
}

template <class T>
static bool ckpt_read(const char* path, Buf* cur, int H, int Nmax, u64 p, int& col,
                      std::vector<u64>& fprev, std::vector<u64>& fcur) {
  FILE* f = fopen(path, "rb");
  if (!f) return false;
  const int NA = Nmax + 1;
  u64 hdr[7];
  if (fread(hdr, sizeof hdr, 1, f) != 1 || hdr[0] != CKPT_MAGIC ||
      (int)hdr[1] != H || (int)hdr[2] != Nmax || hdr[3] != p || hdr[4] != sizeof(T)) {
    fclose(f);
    fprintf(stderr, "FATAL ckpt_mismatch %s\n", path);
    std::exit(4);
  }
  col = (int)hdr[5];
  size_t ns = hdr[6];
  if (fread(fprev.data(), sizeof(u64), 2 * NA, f) != (size_t)(2 * NA) ||
      fread(fcur.data(), sizeof(u64), 2 * NA, f) != (size_t)(2 * NA)) {
    fclose(f); fprintf(stderr, "FATAL ckpt_short %s\n", path); std::exit(4);
  }
  cur->ensure(ns + ns / 4 + 1024, sizeof(T) * 2 * NA);
  cur->clear();
  Alloc al;
  std::vector<T> row(2 * NA);
  for (size_t i = 0; i < ns; i++) {
    u64 kk[2];
    if (fread(kk, sizeof kk, 1, f) != 1 ||
        fread(row.data(), sizeof(T), 2 * NA, f) != (size_t)(2 * NA)) {
      fclose(f); fprintf(stderr, "FATAL ckpt_short %s\n", path); std::exit(4);
    }
    u128 k = ((u128)kk[1] << 64) | kk[0];
    u32 id = cur->find_or_insert(k, al);
    if (id == IDX_EMPTY) { fclose(f); fprintf(stderr, "FATAL ckpt_overflow\n"); std::exit(4); }
    std::memcpy(cur->rowpay(id), row.data(), sizeof(T) * 2 * NA);
  }
  fclose(f);
  return true;
}

template <class T>
static void run_modp(int H, int Nmax, u64 p, const char* outfile, const char* ckptdir) {
  check_height(H);
  const int W = Nmax + 1, NA = Nmax + 1;
  const size_t rowbytes = sizeof(T) * 2 * NA;
  Buf a, bb;
  Buf* cur = &a; Buf* nxt = &bb;
  std::vector<u64> fprev(2 * NA, 0), fcur(2 * NA, 0);
  int c0col = 0;
  std::string ckpt;
  if (ckptdir && *ckptdir) ckpt = std::string(ckptdir) + "/motley.ckpt";

  bool resumed = false;
  if (!ckpt.empty()) resumed = ckpt_read<T>(ckpt.c_str(), cur, H, Nmax, p, c0col, fprev, fcur);
  if (resumed) {
    printf("resumed from column %d, states %zu\n", c0col, cur->count_states());
  } else {
    cur->ensure(1024, rowbytes);
    cur->clear();
    Alloc al;
    u32 id = cur->find_or_insert(0, al);
    ((T*)cur->rowpay(id))[0] = 1;    // n=0: c0 = 1
  }

  auto t0 = std::chrono::steady_clock::now();
  for (int c = c0col; c < W; c++) {
    for (int r = 0; r < H; r++) {
      size_t ns = cur->count_states();
      size_t want = ns + ns / 4 + 4096;
      for (;;) {
        nxt->ensure(want, rowbytes);
        nxt->clear();
        step_modp<T>(cur, nxt, H, Nmax, r, c, p);
        if (!nxt->overflow.load()) break;
        want *= 2;
        fprintf(stderr, "regrow c=%d r=%d want=%zu\n", c, r, want);
      }
      std::swap(cur, nxt);
    }
    fprev = fcur;
    column_sum<T>(cur, Nmax, p, fcur);
    size_t ncur = cur->count_states();
    double dt = std::chrono::duration<double>(std::chrono::steady_clock::now() - t0).count();
    printf("col %d states %zu wall %.1f\n", c, ncur, dt);
    fflush(stdout);
    if (g_rep) g_rep->beat(c + 1, "modp H=" + std::to_string(H) +
                                      " states=" + std::to_string(ncur));
    if (!ckpt.empty() && !ckpt_write<T>(ckpt.c_str(), cur, H, Nmax, p, c + 1, fprev, fcur))
      fprintf(stderr, "WARN ckpt_write_failed\n");
  }

  FILE* f = fopen(outfile, "w");
  if (!f) { perror(outfile); std::exit(1); }
  for (int n = 1; n <= Nmax; n++) {
    u64 q0 = (fcur[2 * n] + p - fprev[2 * n]) % p;
    u64 q1 = (fcur[2 * n + 1] + p - fprev[2 * n + 1]) % p;
    if (q0) { fprintf(stderr, "FATAL q0_nonzero_modp H=%d n=%d\n", H, n); std::exit(2); }
    fprintf(f, "%d %llu\n", n, (unsigned long long)q1);
  }
  fclose(f);
}

// ================================== main ====================================

int main(int argc, char** argv) {
  obs::Reporter rep("motley_par");
  g_rep = &rep;
  const char* ckptdir = nullptr;
  std::vector<char*> pos;
  for (int i = 1; i < argc; i++) {
    if (!std::strcmp(argv[i], "--threads") && i + 1 < argc) {
      omp_set_num_threads(atoi(argv[++i]));
    } else if (!std::strcmp(argv[i], "--ckpt") && i + 1 < argc) {
      ckptdir = argv[++i];
    } else pos.push_back(argv[i]);
  }
  if (pos.size() >= 3 && !std::strcmp(pos[0], "--census")) {
    int H = atoi(pos[1]), Nmax = atoi(pos[2]);
    if (H > HMAX_KEY) { fprintf(stderr, "limits: H<=%d\n", HMAX_KEY); return 1; }
    census(H, Nmax);
    rep.done("mode=census H=" + std::to_string(H));
    return 0;
  }
  if (pos.size() >= 5 && !std::strcmp(pos[0], "--modp")) {
    int H = atoi(pos[1]), Nmax = atoi(pos[2]);
    u64 p = strtoull(pos[3], nullptr, 10);
    if (H > HMAX_KEY || p >= (1ull << 31) || p < 2) {
      fprintf(stderr, "limits: H<=%d, 2<=p<2^31\n", HMAX_KEY); return 1;
    }
    // Payload width from the prime: the accumulator is u64, so the only
    // requirement is that a residue fits the stored type.
    if (p < (1ull << 8)) run_modp<uint8_t>(H, Nmax, p, pos[4], ckptdir);
    else if (p < (1ull << 16)) run_modp<uint16_t>(H, Nmax, p, pos[4], ckptdir);
    else run_modp<uint32_t>(H, Nmax, p, pos[4], ckptdir);
    printf("C_%d mod %llu, n<=%d -> %s\n", H, (unsigned long long)p, Nmax, pos[4]);
    rep.done("mode=modp H=" + std::to_string(H));
    return 0;
  }
  fprintf(stderr,
          "usage: motley_par --census <H> <Nmax> [--threads T]\n"
          "       motley_par --modp <H> <Nmax> <p> <out> [--threads T] [--ckpt DIR]\n");
  return 1;
}
