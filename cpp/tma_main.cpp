// Transfer-matrix driver.
//
// CLI:  tma {square4|square8} MAXN [--per-height] [--checkpoint DIR]
//   totals: "n count" lines; --per-height: "h n count" lines.
//   --checkpoint DIR (square8): persist each strip height as it finishes and
//     resume completed heights on restart -- so a crash mid-run costs one
//     height, not the whole multi-day sweep. Heights are independent sub-sums.
//     With --only-height, this ALSO checkpoints WITHIN that one height at column
//     boundaries (DIR/ckpt, atomic) and resumes mid-height -- so a kill of an
//     18 h diagonal job costs one cadence interval, not the whole height. Knobs:
//     TMA_CKPT_SECS (cadence, default 1800), TMA_CKPT_MIN_STATES (skip below).

#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <filesystem>
#include <string>
#include <thread>

#include "obs.h"
#include "tma/sweep.h"
#include "tma/sweep8.h"
#include "tma/sweep8_modp.h"
#include "tma/sweep8_modp_blocked.h"
#include "tma/sweep8_holes.h"
#include "tma/sweep8_perim.h"

namespace fs = std::filesystem;

// Load checkpoint height file "DIR/hH.txt" ("n count" lines) into row; returns
// false if it does not exist yet (height still to compute).
static bool loadHeight(const std::string& dir, int H, int maxn, Counts& row) {
  const std::string path = dir + "/h" + std::to_string(H) + ".txt";
  FILE* f = std::fopen(path.c_str(), "r");
  if (!f) return false;
  row.assign(maxn + 1, 0);
  int n;
  unsigned long long c;
  while (std::fscanf(f, "%d %llu", &n, &c) == 2)
    if (n >= 0 && n <= maxn) row[n] = c;
  std::fclose(f);
  return true;
}

// Atomically persist a height row: write a temp file, then rename it into
// place. A crash mid-write leaves the temp (ignored on resume), never a
// half-written hH.txt -- so "hH.txt exists" reliably means "height H is done".
static void saveHeight(const std::string& dir, int H, int maxn, const Counts& row) {
  const std::string tmp = dir + "/h" + std::to_string(H) + ".tmp";
  const std::string path = dir + "/h" + std::to_string(H) + ".txt";
  FILE* f = std::fopen(tmp.c_str(), "w");
  if (!f) { std::perror("checkpoint open"); std::exit(1); }
  for (int n = 1; n <= maxn; ++n)
    if (row[n]) std::fprintf(f, "%d %llu\n", n, static_cast<unsigned long long>(row[n]));
  std::fflush(f);
  std::fclose(f);
  if (std::rename(tmp.c_str(), path.c_str()) != 0) {
    std::perror("checkpoint rename");
    std::exit(1);
  }
}

// Guard a checkpoint dir against being reused with mismatched args (a resume
// must use the same lattice+maxn or the partial rows are meaningless).
static void checkMeta(const std::string& dir, const std::string& lattice, int maxn) {
  const std::string path = dir + "/meta";
  if (FILE* f = std::fopen(path.c_str(), "r")) {
    char lat[32] = {0};
    int m = 0;
    const bool ok = std::fscanf(f, "%31s %d", lat, &m) == 2;
    std::fclose(f);
    if (ok && (lattice != lat || maxn != m)) {
      std::fprintf(stderr,
                   "checkpoint %s is for %s maxn=%d, not %s maxn=%d -- refuse\n",
                   path.c_str(), lat, m, lattice.c_str(), maxn);
      std::exit(2);
    }
    if (ok) return;
  }
  if (FILE* f = std::fopen(path.c_str(), "w")) {
    std::fprintf(f, "%s %d\n", lattice.c_str(), maxn);
    std::fclose(f);
  }
}

// --- holes-sweep checkpoint: one file per finished height ---------------------
// The (size,#holes) sweep sums independent per-height contributions, so each
// height's nonzero "(n holes count)" entries persist as hH.txt (atomic temp +
// rename, like saveHeight) and a completed height resumes instead of recomputing.
// A kill costs one height, not the whole multi-hour run. (Intra-height resume is
// the out-of-core #20 work, separate.)
static bool loadHoleHeight(const std::string& dir, int H, int Kp,
                           std::vector<u64>& row) {
  const std::string path = dir + "/h" + std::to_string(H) + ".txt";
  FILE* f = std::fopen(path.c_str(), "r");
  if (!f) return false;
  std::fill(row.begin(), row.end(), 0);
  int n, k;
  unsigned long long c;
  while (std::fscanf(f, "%d %d %llu", &n, &k, &c) == 3) {
    const size_t idx = static_cast<size_t>(n) * Kp + k;
    if (idx < row.size()) row[idx] = c;
  }
  std::fclose(f);
  return true;
}

static void saveHoleHeight(const std::string& dir, int H, int maxn, int Kp,
                           const std::vector<u64>& row) {
  const std::string tmp = dir + "/h" + std::to_string(H) + ".tmp";
  const std::string path = dir + "/h" + std::to_string(H) + ".txt";
  FILE* f = std::fopen(tmp.c_str(), "w");
  if (!f) { std::perror("hole checkpoint open"); std::exit(1); }
  for (int n = 1; n <= maxn; ++n)
    for (int k = 0; k < Kp; ++k) {
      const u64 v = row[static_cast<size_t>(n) * Kp + k];
      if (v) std::fprintf(f, "%d %d %llu\n", n, k,
                          static_cast<unsigned long long>(v));
    }
  std::fflush(f);
  std::fclose(f);
  if (std::rename(tmp.c_str(), path.c_str()) != 0) {
    std::perror("hole checkpoint rename");
    std::exit(1);
  }
}

// Guard a holes checkpoint dir against a resume with mismatched params (a different
// maxn/kmax/hdrop/modp would mix incompatible per-height tables into one answer).
static void checkHoleMeta(const std::string& dir, int maxn, int kmax, bool hdrop,
                          u64 modp) {
  const std::string path = dir + "/meta";
  char want[128];
  std::snprintf(want, sizeof want, "holes maxn=%d kmax=%d hdrop=%d modp=%llu",
                maxn, kmax, hdrop ? 1 : 0, static_cast<unsigned long long>(modp));
  if (FILE* f = std::fopen(path.c_str(), "r")) {
    char have[128] = {0};
    if (std::fgets(have, sizeof have, f)) have[std::strcspn(have, "\n")] = 0;
    std::fclose(f);
    if (std::strcmp(have, want) != 0) {
      std::fprintf(stderr, "hole checkpoint %s is for '%s', not '%s' -- refuse\n",
                   path.c_str(), have, want);
      std::exit(2);
    }
    return;
  }
  if (FILE* f = std::fopen(path.c_str(), "w")) {
    std::fprintf(f, "%s\n", want);
    std::fclose(f);
  }
}

static void emit(const SweepResults& res, int maxn, bool perHeight) {
  std::fprintf(stderr, "peak_states %llu peak_height %d\n",
               static_cast<unsigned long long>(res.peakStates), res.peakHeight);
  if (perHeight) {
    for (int h = 1; h <= maxn; ++h)
      for (int n = 1; n <= maxn; ++n)
        if (res.byHeight[h][n])
          std::printf("%d %d %llu\n", h, n,
                      static_cast<unsigned long long>(res.byHeight[h][n]));
  } else {
    for (int n = 1; n <= maxn; ++n)
      std::printf("%d %llu\n", n, static_cast<unsigned long long>(res.totals[n]));
  }
}

// Fill `ctl` from --checkpoint DIR + the TMA_CKPT_* env knobs; returns &ctl when a
// checkpoint dir was given (else nullptr). Dedups the two identical intra-height setups.
static const CkptCtl* setupCkpt(const std::string& dir, CkptCtl& ctl) {
  if (dir.empty()) return nullptr;
  fs::create_directories(dir);
  ctl.dir = dir;
  if (const char* e = std::getenv("TMA_CKPT_SECS")) ctl.everySeconds = std::atof(e);
  if (const char* e = std::getenv("TMA_CKPT_MIN_STATES"))
    ctl.minStates = std::strtoull(e, nullptr, 10);
  return &ctl;
}

// TODO(simplify): main() routes ~13 flags through a deep nested if/else cascade
// (perim / holes{only-height,per-height,ckpt} / only-height{modp{bbox,closed-form,blocked},
// exact} / global-ckpt / plain), where flag compatibility is enforced by POSITION in the
// cascade rather than validated. Deeper form: parse into a Config, pick a mode enum once
// (with an explicit compat check), dispatch one function per mode. Larger refactor -- its
// own focused pass, gate-protected.
int main(int argc, char** argv) {
  proctitle::init(argc, argv);  // capture argv span for the htop title (before parsing overwrites)
  if (argc < 3) {
    std::fprintf(stderr,
                 "usage: %s {square4|square8} MAXN [--per-height] "
                 "[--holes [--kmax K] [--only-height H] [--modp P]] "
                 "[--checkpoint DIR]\n",
                 argv[0]);
    return 2;
  }
  const std::string lattice = argv[1];
  if (lattice != "square4" && lattice != "square8") {
    std::fprintf(stderr, "lattice must be square4 or square8\n");
    return 2;
  }
  const int maxn = std::atoi(argv[2]);
  // Cap is a safety bound, not an algorithmic limit: the fixed-width signature
  // supports strip heights H<=30, but the cell budget n is independent. The 64
  // cap guards the EXACT u64 path (counts overflow past ~n=50 at H>=3); the mod-p
  // holes path (--modp, #5b) has no overflow, so it gathers many more terms --
  // the relaxed bound for it is applied after arg parsing once --modp is known.
  // Here we only enforce a generous sanity ceiling (catch typos / runaway alloc);
  // the real exact-path cap (n<=64) is enforced below once --modp is parsed.
  if (maxn < 1 || maxn > (1 << 20)) {
    std::fprintf(stderr, "MAXN out of range (1..%d)\n", 1 << 20);
    return 2;
  }
  bool perHeight = false, perimeter = false, holes = false;
  int kmax = -1;  // default set to maxn below: an n-cell animal has < n holes,
                  // so maxn can never overflow (override down to save memory)
  std::string checkpointDir;
  int nthreads = 1, onlyHeight = 0;
  u64 modp = 0;  // --modp P: count B_{H,k}(n) mod P (holes path, #5b GF recovery)
  bool fold = false;  // --fold: R1 vertical-mirror fold (~2x fewer states); composes with --modp
                      // on the plain a(n) --only-height path (R1xR3 reach engine, ~4x less RAM)
  bool hdrop = false;  // --hdrop: drop holes > kmax (exact for k<=kmax, bounds RAM)
  int blockedS = 0;    // --blocked S: B (blocked store) on the modp reach path -- S
                       // hash partitions, drained-and-freed per column (~2x less RAM,
                       // composes with --fold/--modp). 0 = off. Rounded up to pow2.
  u64 reserveStates = 0;  // --reserve N: pre-size the state store to ~N states (skip
                          // the doubling-grow transient; pass the calibrated peak)
  bool bbox = false;  // --bbox: with --only-height H --modp P, emit "H W n B_{H,W}(n) mod P"
                      // (bounding-box stratified: height EXACTLY H, width EXACTLY W).
  for (int i = 3; i < argc; ++i) {
    if (std::strcmp(argv[i], "--per-height") == 0) {
      perHeight = true;
    } else if (std::strcmp(argv[i], "--perimeter") == 0) {
      perimeter = true;
    } else if (std::strcmp(argv[i], "--holes") == 0) {
      holes = true;
    } else if (std::strcmp(argv[i], "--kmax") == 0 && i + 1 < argc) {
      kmax = std::atoi(argv[++i]);
    } else if (std::strcmp(argv[i], "--checkpoint") == 0 && i + 1 < argc) {
      checkpointDir = argv[++i];
    } else if (std::strcmp(argv[i], "--threads") == 0 && i + 1 < argc) {
      nthreads = std::atoi(argv[++i]);
      if (nthreads < 1) nthreads = 1;
    } else if (std::strcmp(argv[i], "--only-height") == 0 && i + 1 < argc) {
      onlyHeight = std::atoi(argv[++i]);
    } else if (std::strcmp(argv[i], "--modp") == 0 && i + 1 < argc) {
      modp = static_cast<u64>(std::atoll(argv[++i]));
    } else if (std::strcmp(argv[i], "--fold") == 0) {
      fold = true;
    } else if (std::strcmp(argv[i], "--hdrop") == 0) {
      hdrop = true;
    } else if (std::strcmp(argv[i], "--blocked") == 0 && i + 1 < argc) {
      int s = std::atoi(argv[++i]);
      blockedS = 1;
      while (blockedS < s) blockedS <<= 1;  // round up to a power of two (mask requires it)
    } else if (std::strcmp(argv[i], "--reserve") == 0 && i + 1 < argc) {
      reserveStates = static_cast<u64>(std::strtoull(argv[++i], nullptr, 10));
    } else if (std::strcmp(argv[i], "--bbox") == 0) {
      bbox = true;
    } else {
      std::fprintf(stderr, "unknown arg: %s\n", argv[i]);
      return 2;
    }
  }
  // The exact (non-mod-p) paths overflow u64 well before n=64; only --modp may
  // exceed the cap, since its counts are reduced and cannot overflow.
  if (maxn > 64 && modp == 0) {
    std::fprintf(stderr, "MAXN > 64 requires --modp P (exact counts overflow)\n");
    return 2;
  }

  // (size, edge-perimeter) joint distribution via the column transfer matrix
  // (square8 only) -- isolated path, cross-checked against `g2 --perimeter`.
  if (perimeter) {
    if (lattice != "square8") {
      std::fprintf(stderr, "--perimeter is supported for square8 only\n");
      return 2;
    }
    obs::Reporter rep("tma-perim-N" + std::to_string(maxn), 0, "");
    const int Pmax = 4 * maxn, Pp = Pmax + 1;
    std::vector<u64> dist = sweepSquare8Perim(maxn, Pmax);
    rep.done("result=ok");
    for (int n = 1; n <= maxn; ++n)
      for (int p = 0; p <= Pmax; ++p) {
        const u64 v = dist[static_cast<size_t>(n) * Pp + p];
        if (v) std::printf("%d %d %llu\n", n, p, static_cast<unsigned long long>(v));
      }
    return 0;
  }

  // (size, #holes) joint distribution via the column transfer matrix (square8
  // only), primary 4-connected-background convention -- removes the per-animal
  // flood, so it reaches the bare count's n. Cross-checked vs `g2 --holes`.
  //   default: "n holes count" (summed over heights)
  //   --per-height: "h n holes count" (the per-(height,holes) slices the GF
  //                 recovery consumes)
  if (holes) {
    if (lattice != "square8") {
      std::fprintf(stderr, "--holes is supported for square8 only\n");
      return 2;
    }
    if (kmax < 0) kmax = maxn;  // safe default: holes < n always
    const int Kp = kmax + 1;
    // single height: the per-(H,k) sequences the GF recovery consumes. Isolates
    // one strip height so a LOW height sweeps cheaply to high n (the all-heights
    // sweep would explode); emits "H n holes count", same as --per-height for 1 H.
    if (onlyHeight > 0) {
      CkptCtl ckctl;  // intra-height resume for this single height
      const CkptCtl* ckptPtr = setupCkpt(checkpointDir, ckctl);
      obs::Reporter rep(
          "tma-holes-H" + std::to_string(onlyHeight) + "-N" +
              std::to_string(maxn) + "-k" + std::to_string(kmax),
          0,
          "height=" + std::to_string(onlyHeight) +
              (modp ? " modp=" + std::to_string(modp) : std::string()) +
              (hdrop ? std::string(" hdrop=1") : std::string()) +
              " threads=" + std::to_string(nthreads) +
              (ckptPtr ? std::string(" ckpt=1") : std::string()));
      std::vector<u64> row(static_cast<size_t>(maxn + 1) * Kp, 0);
      sweepSquare8HeightHoles(onlyHeight, maxn, kmax, Conn::FG8, row, modp, hdrop,
                              nthreads, static_cast<size_t>(reserveStates), ckptPtr);
      rep.done("result=ok");
      for (int n = 1; n <= maxn; ++n)
        for (int k = 0; k <= kmax; ++k) {
          const u64 v = row[static_cast<size_t>(n) * Kp + k];
          if (v) std::printf("%d %d %d %llu\n", onlyHeight, n, k,
                             static_cast<unsigned long long>(v));
        }
      return 0;
    }
    if (perHeight) {
      obs::Reporter rep("tma-holes-allH-N" + std::to_string(maxn), maxn,
                        "threads=" + std::to_string(nthreads));
      for (int H = 1; H <= maxn; ++H) {
        std::vector<u64> row(static_cast<size_t>(maxn + 1) * Kp, 0);
        sweepSquare8HeightHoles(H, maxn, kmax, Conn::FG8, row, 0, false, nthreads,
                                static_cast<size_t>(reserveStates));
        rep.beat(H, "height=" + std::to_string(H), true);
        for (int n = 1; n <= maxn; ++n)
          for (int k = 0; k <= kmax; ++k) {
            const u64 v = row[static_cast<size_t>(n) * Kp + k];
            if (v) std::printf("%d %d %d %llu\n", H, n, k,
                               static_cast<unsigned long long>(v));
          }
      }
      rep.done("result=ok");
    } else {
      const bool ckpt = !checkpointDir.empty();
      obs::Reporter rep("tma-holes-N" + std::to_string(maxn),
                        ckpt ? static_cast<double>(maxn) : 0.0,
                        "threads=" + std::to_string(nthreads) +
                            (ckpt ? std::string(" ckpt=1") : std::string()));
      std::vector<u64> dist(static_cast<size_t>(maxn + 1) * Kp, 0);
      if (ckpt) {
        // per-height checkpoint: bank each finished height's (size,#holes) table,
        // resume completed heights on restart -- a kill costs one height.
        fs::create_directories(checkpointDir);
        checkHoleMeta(checkpointDir, maxn, kmax, hdrop, modp);
        for (int H = 1; H <= maxn; ++H) {
          std::vector<u64> hrow(static_cast<size_t>(maxn + 1) * Kp, 0);
          const bool resumed = loadHoleHeight(checkpointDir, H, Kp, hrow);
          if (!resumed) {
            sweepSquare8HeightHoles(H, maxn, kmax, Conn::FG8, hrow, modp, hdrop,
                                    nthreads, static_cast<size_t>(reserveStates));
            saveHoleHeight(checkpointDir, H, maxn, Kp, hrow);
          }
          for (size_t i = 0; i < dist.size(); ++i)
            dist[i] = modp ? (dist[i] + hrow[i]) % modp : dist[i] + hrow[i];
          rep.beat(H, "height=" + std::to_string(H) +
                          (resumed ? " resumed=1" : ""), true);
        }
      } else {
        dist = sweepSquare8Holes(maxn, kmax, Conn::FG8, nthreads,
                                 static_cast<size_t>(reserveStates));
      }
      rep.done("result=ok");
      for (int n = 1; n <= maxn; ++n)
        for (int k = 0; k <= kmax; ++k) {
          const u64 v = dist[static_cast<size_t>(n) * Kp + k];
          if (v) std::printf("%d %d %llu\n", n, k,
                             static_cast<unsigned long long>(v));
        }
    }
    return 0;
  }

  // Compute a single strip height (square8) -- for measuring per-height scaling
  // and for running heights as independent jobs (the a(n) diagonal sweep). This
  // is the long-running path with no prior progress signal, so it heartbeats per
  // column: col/maxn is the denominator, live-state count the liveness, and the
  // ETA is self-computed from the measured column rate.
  if (onlyHeight > 0) {
    if (modp > 0) {
      if (bbox) {
        // Bounding-box stratified: emit "H W n B_{H,W}(n) mod P" for every nonzero entry.
        // Width == column at harvest (leftmost pinned at col 0). Sum_W recovers B_H(n).
        u64 peak = 0;
        const auto bbw = sweepSquare8HeightWidthModP(
            onlyHeight, maxn, static_cast<std::uint32_t>(modp), peak);
        obs::Reporter rep("tma-bbox-H" + std::to_string(onlyHeight) + "-N" +
                              std::to_string(maxn),
                          maxn, "height=" + std::to_string(onlyHeight) + " modp=" +
                                    std::to_string(modp) + " bbox=1");
        unsigned long long emitted = 0;
        for (int W = 1; W <= maxn; ++W)
          for (int n = 1; n <= maxn; ++n)
            if (bbw[W][n]) {
              std::printf("%d %d %d %u\n", onlyHeight, W, n, bbw[W][n]);
              ++emitted;
            }
        rep.done("rows=" + std::to_string(emitted),
                 "peak_states=" +
                     std::to_string(static_cast<unsigned long long>(peak)));
        return 0;
      }
      // Top strip height H==N: a trivial closed form, not worth sweeping the largest,
      // emptiest strip. A height-N king-polyomino of N cells has exactly one cell per
      // row, and each of the N-1 inter-row steps shifts the column by -1/0/+1 (8-neighbor
      // adjacency), so B_N(N) = 3^(N-1) (fixed: the first cell is translation-normalized);
      // n<N cannot span N rows, so B_N(n<N)=0. Byte-identical to the real --only-height N
      // sweep (verified n<=8); for a(20) this replaced a ~2-day h20 sweep.
      if (onlyHeight == maxn) {
        u64 v = 1 % modp;
        const u64 base = 3 % modp;
        for (int e = 0; e < maxn - 1; ++e) v = (v * base) % modp;
        obs::Reporter rep("tma-H" + std::to_string(onlyHeight) + "-modp-N" +
                              std::to_string(maxn),
                          0, "height=" + std::to_string(onlyHeight) + " modp=" +
                                 std::to_string(modp) + " closed_form=3^(N-1)");
        rep.done("result=" + std::to_string(static_cast<unsigned long long>(v)));
        for (int n = 1; n < maxn; ++n) std::printf("%d %u\n", n, 0u);
        std::printf("%d %u\n", maxn, static_cast<std::uint32_t>(v));
        return 0;
      }
      // R1xR3 production reach path: fold + u32 mod-p sweep of one strip height -- emits
      // "n B_H(n) mod p". CRT over 2-3 primes (scripts/an_modp_crt.sh) recovers the exact
      // B_H(n); summing over H gives a(n). ~4x less RAM than the exact u64 sweep.
      u64 peak = 0, peakBytes = 0;
      const std::vector<std::uint32_t> row =
          blockedS > 0
              ? sweepSquare8HeightModPBlocked(onlyHeight, maxn,
                                              static_cast<std::uint32_t>(modp), fold,
                                              blockedS, peak, peakBytes)
              : sweepSquare8HeightModP(onlyHeight, maxn,
                                       static_cast<std::uint32_t>(modp), fold, peak,
                                       nthreads);
      obs::Reporter rep("tma-H" + std::to_string(onlyHeight) + "-modp-N" +
                            std::to_string(maxn),
                        maxn, "height=" + std::to_string(onlyHeight) + " modp=" +
                                  std::to_string(modp) + " fold=" +
                                  std::to_string(fold ? 1 : 0) + " threads=" +
                                  std::to_string(nthreads) +
                                  (blockedS > 0 ? " blocked=" + std::to_string(blockedS)
                                                : ""));
      rep.done("result=" + std::to_string(static_cast<unsigned long long>(row[maxn])),
               "peak_states=" +
                   std::to_string(static_cast<unsigned long long>(peak)) +
                   (blockedS > 0
                        ? " peak_store_mb=" +
                              std::to_string(static_cast<unsigned long long>(
                                  peakBytes >> 20))
                        : ""));
      for (int n = 1; n <= maxn; ++n)
        std::printf("%d %u\n", n, row[n]);
      return 0;
    }
    SweepResults res;
    res.byHeight.assign(maxn + 1, Counts(maxn + 1, 0));
    res.totals.assign(maxn + 1, 0);
    // intra-height checkpoint: --checkpoint DIR resumes this single height's sweep
    // from the last column boundary (env knobs TMA_CKPT_SECS / TMA_CKPT_MIN_STATES).
    CkptCtl ckctl;
    const CkptCtl* ckptPtr = setupCkpt(checkpointDir, ckctl);
    obs::Reporter rep("tma-H" + std::to_string(onlyHeight) + "-N" +
                          std::to_string(maxn),
                      maxn, "height=" + std::to_string(onlyHeight) + " threads=" +
                          std::to_string(nthreads) +
                          (ckptPtr ? std::string(" ckpt=1") : std::string()));
    // htop process title: "tma a(N) H<h> c=<col>/<maxn> ~<pct>%", refreshed ~1.5s
    std::thread titleThread = proctitle::start(maxn, onlyHeight, maxn);
    res.byHeight[onlyHeight] = heightRow(
        onlyHeight, maxn, nthreads, res, [&](int col, u64 live) {
          proctitle::setCol(col);  // covers the serial path (MT path also sets it)
          rep.beat(col, "col=" + std::to_string(col) + " states=" +
                            std::to_string(live) + " peak_states=" +
                            std::to_string(res.peakStates));
        },
        static_cast<size_t>(reserveStates), ckptPtr, fold);
    proctitle::stop(titleThread);
    for (int n = 1; n <= maxn; ++n) res.totals[n] = res.byHeight[onlyHeight][n];
    rep.done("result=" + std::to_string(static_cast<unsigned long long>(
                             res.byHeight[onlyHeight][maxn])),
             "peak_states=" +
                 std::to_string(static_cast<unsigned long long>(res.peakStates)));
    emit(res, maxn, perHeight);
    return 0;
  }

  if (!checkpointDir.empty()) {
    if (lattice != "square8") {
      std::fprintf(stderr, "--checkpoint is supported for square8 only\n");
      return 2;
    }
    fs::create_directories(checkpointDir);
    checkMeta(checkpointDir, lattice, maxn);

    SweepResults res;
    res.byHeight.assign(maxn + 1, Counts(maxn + 1, 0));
    res.totals.assign(maxn + 1, 0);
    obs::Reporter rep("tma-ckpt-N" + std::to_string(maxn), maxn,
                      "threads=" + std::to_string(nthreads));
    for (int H = 1; H <= maxn; ++H) {
      Counts row;
      if (loadHeight(checkpointDir, H, maxn, row)) {
        rep.beat(H, "height=" + std::to_string(H) + " resumed=1", true);
      } else {
        row = heightRow(H, maxn, nthreads, res);
        saveHeight(checkpointDir, H, maxn, row);
        rep.beat(H, "height=" + std::to_string(H) + " peak_states=" +
                        std::to_string(static_cast<unsigned long long>(
                            res.peakStates)),
                 true);
      }
      res.byHeight[H] = std::move(row);
    }
    accumulateTotals(res, maxn);
    rep.done("result=" + std::to_string(static_cast<unsigned long long>(
                             res.totals[maxn])),
             "peak_states=" +
                 std::to_string(static_cast<unsigned long long>(res.peakStates)));
    emit(res, maxn, perHeight);
    return 0;
  }

  obs::Reporter rep("tma-N" + std::to_string(maxn), maxn,
                    "threads=" + std::to_string(nthreads));
  SweepResults res = (lattice == "square4") ? sweepSquare4(maxn)
                                            : sweepSquare8(maxn, nthreads);
  rep.done("result=" +
               std::to_string(static_cast<unsigned long long>(res.totals[maxn])),
           "peak_states=" +
               std::to_string(static_cast<unsigned long long>(res.peakStates)));
  emit(res, maxn, perHeight);
  return 0;
}
