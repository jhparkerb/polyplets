// reframe_measure.cpp -- measure the frontier-zstd ratio-vs-frame-size curve
// on a REAL frontier file (results/fanin-tax.md, Mirror Toll thread). Reads a
// POLYRUN file (plain or compressed) and rewrites it at each candidate frame
// size, reporting bytes and bytes/record. The 1.83x whole-file measurement
// does not survive tiny frames (~1.08x realized at 64 records on live a(39)
// H20 data); this tool locates the sweet spot against the seek-overshoot cpu
// cost that killed 1024-record frames.
//
// Usage: reframe_measure FILE H KEYLEN [FRAME_SIZES...]
//   defaults: 64 128 256 512 1024
// Env: POLY_FRONTIER_ZSTD must be unset here -- the tool sets the writer's
// compress flag directly. Writes temp files next to FILE, removes them.
#include <cstdio>
#include <cstdlib>
#include <string>
#include <vector>
#include <sys/stat.h>
#include <sys/wait.h>
#include <unistd.h>
#include "core/runfile.h"

int main(int argc, char** argv) {
  if (argc < 4) {
    std::fprintf(stderr, "usage: %s FILE H KEYLEN [FRAME_SIZES...]\n", argv[0]);
    return 2;
  }
  const std::string in = argv[1];
  const int H = std::atoi(argv[2]);
  const int keyLen = std::atoi(argv[3]);
  std::vector<long> sizes;
  for (int i = 4; i < argc; i++) sizes.push_back(std::atol(argv[i]));
  if (sizes.empty()) sizes = {64, 128, 256, 512, 1024};

  // Load all records once (bounded by the file's slice size; run on a range
  // file, not a whole frontier).
  std::vector<RunRecord<u128>> recs;
  {
    RunFileReader<u128> r(in, H, keyLen);
    if (!r.ok()) { std::fprintf(stderr, "cannot read %s\n", in.c_str()); return 1; }
    RunRecord<u128> rec;
    while (r.next(rec)) recs.push_back(rec);
  }
  struct stat st{};
  ::stat(in.c_str(), &st);
  std::printf("input %s: %zu records, %lld bytes (%.1f B/rec)\n", in.c_str(),
              recs.size(), (long long)st.st_size,
              recs.empty() ? 0.0 : (double)st.st_size / (double)recs.size());

  for (long fs : sizes) {
    // Writer frame size comes from the env knob; it is cached per process, so
    // fork a child per candidate.
    const std::string out = in + ".reframe.tmp";
    pid_t pid = fork();
    if (pid == 0) {
      // fs == 0: plain (uncompressed) rewrite — the absolute baseline.
      setenv("POLY_FRONTIER_ZSTD_BLOCK", std::to_string(fs > 0 ? fs : 64).c_str(), 1);
      RunFileWriter<u128> w(out, H, 0, "", "", "reframe", keyLen,
                            /*write_index=*/true, /*compress=*/fs > 0);
      for (const auto& r : recs) w.append(r);
      w.finalize();
      _exit(0);
    }
    int status = 0;
    waitpid(pid, &status, 0);
    struct stat so{};
    if (::stat(out.c_str(), &so) != 0) {
      std::fprintf(stderr, "frame=%ld: rewrite failed\n", fs);
      continue;
    }
    std::printf("frame=%-5ld  %lld bytes  %.1f B/rec  ratio vs input %.2fx\n",
                fs, (long long)so.st_size,
                recs.empty() ? 0.0 : (double)so.st_size / (double)recs.size(),
                so.st_size ? (double)st.st_size / (double)so.st_size : 0.0);
    std::remove(out.c_str());
    std::remove((out + ".idx").c_str());
  }
  return 0;
}
