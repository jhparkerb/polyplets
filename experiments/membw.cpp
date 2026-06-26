// membw.cpp -- C2 microbench (frontier idea 03 / docs/frontier/03-seam-closure-analysis.md):
// SEQUENTIAL vs RANDOM memory bandwidth, the two regimes that decide the sort engine.
//   sequential  = the sort/stream engine's map + merge passes (streaming, prefetch-friendly)
//   random      = the HASH engine's find-or-insert into a >cache resident frontier table
//                 (cache/TLB-miss bound) -- the cost the sort engine is meant to escape.
// The ratio seq/random says how badly the hash engine's random access already costs IN RAM;
// combined with the fio NVMe numbers it answers C2: is sequential disk competitive with the
// random-RAM the hash engine OOMs trying to keep resident?
// Build: g++ -std=c++20 -O3 -o build/membw experiments/membw.cpp   Run: ./build/membw [GB pow2]
#include <cstdio>
#include <cstdint>
#include <cstdlib>
#include <vector>
#include <chrono>
using namespace std;
using clk = chrono::steady_clock;

int main(int argc, char** argv){
    size_t GB = argc>1 ? (size_t)atoi(argv[1]) : 8;          // power of 2 -> N words is power of 2
    size_t N = GB * (1ull<<30) / sizeof(uint64_t);           // GB=8 -> N=2^30 words (8 GB), >> LLC
    size_t mask = N - 1;                                     // valid index mask (N power of 2)
    vector<uint64_t> a(N);
    for (size_t i=0;i<N;i++) a[i]=i*2654435761ull+1;
    auto bw=[&](size_t bytes,double s){ return (double)bytes/1e9/s; };

    // SEQUENTIAL read (sum) -- warm pass then timed pass
    { volatile uint64_t w=0; for(size_t i=0;i<N;i++) w+=a[i]; (void)w; }
    auto t0=clk::now(); uint64_t s=0; for(size_t i=0;i<N;i++) s+=a[i]; auto t1=clk::now();
    double seq_s=chrono::duration<double>(t1-t0).count(), seq=bw(N*8,seq_s);

    // RANDOM read (LCG-indexed gather; idx independent of loaded value -> MLP bandwidth, not
    // pointer-chase latency -- matches the hash engine's many independent random probes).
    auto t2=clk::now();
    uint64_t r=0, idx=88172645463325252ull;
    for(size_t i=0;i<N;i++){ idx = idx*6364136223846793005ull + 1442695040888963407ull; r += a[idx & mask]; }
    auto t3=clk::now();
    double rnd_s=chrono::duration<double>(t3-t2).count(), rnd=bw(N*8,rnd_s);

    printf("array=%zuGB  N=%zu words (>> LLC)\n", GB, N);
    printf("mem SEQ  read : %6.1f GB/s\n", seq);
    printf("mem RAND read : %6.2f GB/s   (%.1fx slower than sequential)\n", rnd, seq/rnd);
    printf("[checksum %llu %llu]\n",(unsigned long long)s,(unsigned long long)r);
    return 0;
}
