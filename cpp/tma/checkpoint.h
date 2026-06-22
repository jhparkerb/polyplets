// Intra-height checkpoint for the column transfer-matrix sweep (#20 resume gap).
//
// A single `--only-height` sweep can run many hours; this serializes the boundary
// state at a column boundary (atomic temp -> fsync -> rename, one rolling file) so a
// kill resumes from the last column instead of column 0. Driver glue, deliberately
// separate from the minimal `statedb.h` store.
//
// BYTE-IDENTICAL on resume: the store is read only as a SET of (Sig, counts-row)
// pairs via `for_each`, never via physical slot/capacity/probe order, so
// flatten-then-reinsert is an identity on the logical map (the same reason
// `--reserve` is byte-identical). The MT path stores no shard index; on reload each
// entry is re-routed by `hashSig & (S-1)`, a pure function of (Sig, nthreads).

#pragma once

#include <chrono>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>

#include <unistd.h>  // fsync, fileno

#include "signature.h"  // Sig, SIGMAX
#include "statedb.h"    // u64

#ifndef GIT_REV
#define GIT_REV "unknown"
#endif

// Wall-clock cadence + dir for intra-height checkpointing; null = disabled.
struct CkptCtl {
  std::string dir;
  double everySeconds = 1800.0;       // TMA_CKPT_SECS (default 30 min)
  size_t minStates = (1u << 20);      // don't bother below ~1M live states
};

// Run identity baked into the checkpoint; a mismatch means a different computation.
struct CkptMeta {
  std::int32_t maxn = 0, H = 0, kmax = 0;
  u64 modp = 0;
  std::uint8_t hdrop = 0;
  std::int32_t nthreads = 0;
  std::uint8_t lattice = 0;           // 0 = plain a(n), 1 = holes
  u64 stride = 0;                     // u64s per counts row
  std::uint8_t fold = 0;              // 1 = R1 vertical-mirror fold (canonical sigs)
};

enum class CkptStatus { None, Loaded, Refuse };  // no file / resumed / abort

// --- crc32 (IEEE), running register: init 0xFFFFFFFF, finalize ^ 0xFFFFFFFF ---
inline std::uint32_t crc32_update(std::uint32_t crc, const void* buf, size_t n) {
  static std::uint32_t T[256];
  static bool init = false;
  if (!init) {
    for (std::uint32_t i = 0; i < 256; ++i) {
      std::uint32_t c = i;
      for (int k = 0; k < 8; ++k) c = (c & 1) ? (0xEDB88320u ^ (c >> 1)) : (c >> 1);
      T[i] = c;
    }
    init = true;
  }
  const std::uint8_t* p = static_cast<const std::uint8_t*>(buf);
  for (size_t i = 0; i < n; ++i) crc = T[(crc ^ p[i]) & 0xFF] ^ (crc >> 8);
  return crc;
}

namespace tmackpt_detail {
struct Writer {
  std::FILE* f;
  std::uint32_t crc = 0xFFFFFFFFu;
  bool ok = true;
  void put(const void* p, size_t n) {
    if (!ok) return;
    if (std::fwrite(p, 1, n, f) != n) { ok = false; return; }
    crc = crc32_update(crc, p, n);
  }
  template <class T> void putv(const T& v) { put(&v, sizeof v); }
};
struct Reader {
  std::FILE* f;
  std::uint32_t crc = 0xFFFFFFFFu;
  bool ok = true;
  void get(void* p, size_t n) {
    if (!ok) return;
    if (std::fread(p, 1, n, f) != n) { ok = false; return; }
    crc = crc32_update(crc, p, n);
  }
  template <class T> void getv(T& v) { get(&v, sizeof v); }
};
}  // namespace tmackpt_detail

// Atomically write DIR/ckpt: header + nEntries*(Sig + row) + accumulator + crc32.
// `forEachEntry(emit)` must call emit(const Sig&, const u64* row) once per live
// entry (caller supplies db.for_each / a loop over shards). Returns false on any
// I/O failure WITHOUT disturbing the prior DIR/ckpt -- a failed checkpoint must
// never kill the job.
template <class EntrySource>
inline bool tmaCkptSave(const CkptCtl& ctl, const CkptMeta& m, u64 nEntries,
                        EntrySource&& forEachEntry, const u64* accum, u64 accumLen,
                        std::int32_t colNext, u64 peakStates,
                        std::int32_t peakHeight) {
  const std::string tmp = ctl.dir + "/ckpt.tmp";
  const std::string path = ctl.dir + "/ckpt";
  std::FILE* f = std::fopen(tmp.c_str(), "wb");
  if (!f) return false;
  tmackpt_detail::Writer w{f};

  w.put("TMCK", 4);
  std::uint32_t fmtver = 2; w.putv(fmtver);  // 2: added m.fold to the guard
  char gitrev[40] = {0}; std::strncpy(gitrev, GIT_REV, sizeof gitrev - 1);
  w.put(gitrev, sizeof gitrev);
  std::uint8_t byteorder = 1; w.putv(byteorder);  // little-endian
  w.putv(m.lattice); w.putv(m.fold);
  w.putv(m.maxn); w.putv(m.H); w.putv(m.kmax); w.putv(m.modp);
  w.putv(m.hdrop); w.putv(m.nthreads);
  w.putv(colNext); w.putv(peakStates); w.putv(peakHeight);
  w.putv(m.stride); w.putv(nEntries);

  forEachEntry([&](const Sig& sig, const u64* row) {
    w.put(sig.b, SIGMAX);
    w.put(row, m.stride * sizeof(u64));
  });
  w.put(accum, accumLen * sizeof(u64));

  std::uint32_t crc = w.crc ^ 0xFFFFFFFFu;
  if (w.ok && std::fwrite(&crc, 1, 4, f) != 4) w.ok = false;  // crc itself uncrc'd

  bool ok = w.ok;
  if (ok) { std::fflush(f); ok = (fsync(fileno(f)) == 0); }
  std::fclose(f);
  if (!ok) { std::remove(tmp.c_str()); return false; }
  if (std::rename(tmp.c_str(), path.c_str()) != 0) { std::remove(tmp.c_str()); return false; }
  return true;
}

// Load DIR/ckpt. Header mismatch or bad crc -> Refuse (caller aborts; never produce
// wrong counts). No file -> None (caller starts fresh). Loaded -> entries fed to
// `sink(const Sig&, const u64* row)`, accumulator filled, col/peaks set out.
template <class Sink>
inline CkptStatus tmaCkptLoad(const CkptCtl& ctl, const CkptMeta& expect, Sink&& sink,
                              u64* accum, u64 accumLen, std::int32_t& colNext,
                              u64& peakStates, std::int32_t& peakHeight) {
  const std::string path = ctl.dir + "/ckpt";
  std::FILE* f = std::fopen(path.c_str(), "rb");
  if (!f) return CkptStatus::None;
  tmackpt_detail::Reader r{f};

  char magic[4]; r.get(magic, 4);
  std::uint32_t fmtver; r.getv(fmtver);
  char gitrev[40]; r.get(gitrev, sizeof gitrev);
  std::uint8_t byteorder; r.getv(byteorder);
  std::uint8_t lattice, fold; r.getv(lattice); r.getv(fold);
  std::int32_t maxn, H, kmax; u64 modp; std::uint8_t hdrop; std::int32_t nthreads;
  r.getv(maxn); r.getv(H); r.getv(kmax); r.getv(modp); r.getv(hdrop); r.getv(nthreads);
  std::int32_t cn; u64 pk; std::int32_t ph; u64 stride, nEntries;
  r.getv(cn); r.getv(pk); r.getv(ph); r.getv(stride); r.getv(nEntries);

  if (!r.ok || std::memcmp(magic, "TMCK", 4) != 0 || fmtver != 2 || byteorder != 1 ||
      lattice != expect.lattice || fold != expect.fold ||
      maxn != expect.maxn || H != expect.H ||
      kmax != expect.kmax || modp != expect.modp || hdrop != expect.hdrop ||
      stride != expect.stride) {
    std::fclose(f);
    return CkptStatus::Refuse;  // header read OK but for a different run (or bad)
  }

  std::vector<u64> row(stride);
  Sig sig;
  for (u64 i = 0; i < nEntries && r.ok; ++i) {
    r.get(sig.b, SIGMAX);
    r.get(row.data(), stride * sizeof(u64));
    if (r.ok) sink(static_cast<const Sig&>(sig), row.data());
  }
  r.get(accum, accumLen * sizeof(u64));

  std::uint32_t want = r.crc ^ 0xFFFFFFFFu, got = 0;
  if (std::fread(&got, 1, 4, f) != 4) r.ok = false;
  std::fclose(f);
  if (!r.ok || got != want) return CkptStatus::Refuse;  // truncated / bit-rot

  colNext = cn; peakStates = pk; peakHeight = ph;
  return CkptStatus::Loaded;
}

// True (and resets `last`) once `ctl.everySeconds` of wall-clock has elapsed.
inline bool ckptDue(const CkptCtl& ctl,
                    std::chrono::steady_clock::time_point& last) {
  auto now = std::chrono::steady_clock::now();
  if (std::chrono::duration<double>(now - last).count() < ctl.everySeconds)
    return false;
  last = now;
  return true;
}

// Test-only hook: TMA_CKPT_KILL_AT_COL=k makes the process _Exit right AFTER the
// column-k checkpoint save, simulating a crash with a valid ckpt on disk (the gate
// kill/resume check). Behind an env var, so it never fires in production.
inline void ckptTestKill(std::int32_t col) {
  const char* e = std::getenv("TMA_CKPT_KILL_AT_COL");
  if (e && std::atoi(e) == col) {
    std::fprintf(stderr, "TMA_CKPT_KILL_AT_COL=%d hit; exiting post-save\n", col);
    std::_Exit(137);
  }
}
