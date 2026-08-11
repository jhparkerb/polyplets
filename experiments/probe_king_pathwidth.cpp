// probe_king_pathwidth.cpp — second-source team, Teammate B probe (throwaway).
// Purpose: exact pathwidth of the m x n king graph P_m ⊠ P_n via the
//   vertex-separation DP  f[S] = min_{v in S} max(f[S \ v], |∂S|),
//   pw = vs (Kinnersley 1992). Settles whether pw = m or m+1 at small sizes.
// Command: build/probe_king_pathwidth <m> <n>   (mn <= 28)
// Machine: gympie. Predicted cost: mn=28 -> 2^28 bytes RAM (~268 MB), ~1 min.
// Kill: ctrl-C; no checkpoint (probe, seconds-scale).
#include <cstdio>
#include <cstdlib>
#include <cstdint>
#include <vector>
#include <algorithm>
int main(int argc, char** argv) {
    if (argc != 3) { fprintf(stderr, "usage: %s m n\n", argv[0]); return 1; }
    int m = atoi(argv[1]), n = atoi(argv[2]), V = m * n;
    if (V > 28) { fprintf(stderr, "mn too big\n"); return 1; }
    std::vector<uint32_t> nbr(V, 0);
    auto id = [&](int r, int c) { return c * m + r; };
    for (int c = 0; c < n; c++) for (int r = 0; r < m; r++)
        for (int dc = -1; dc <= 1; dc++) for (int dr = -1; dr <= 1; dr++) {
            if (!dr && !dc) continue;
            int r2 = r + dr, c2 = c + dc;
            if (r2 >= 0 && r2 < m && c2 >= 0 && c2 < n) nbr[id(r, c)] |= 1u << id(r2, c2);
        }
    size_t N = 1ull << V;
    std::vector<uint8_t> f(N, 0);
    uint32_t full = (V == 32) ? ~0u : ((1u << V) - 1);
    for (size_t S = 1; S < N; S++) {
        // boundary size of S: vertices in S with a neighbor outside S
        int b = 0;
        uint32_t s = (uint32_t)S;
        for (uint32_t t = s; t; t &= t - 1) {
            int v = __builtin_ctz(t);
            if (nbr[v] & ~s & full) b++;
        }
        int best = 255;
        for (uint32_t t = s; t; t &= t - 1) {
            int v = __builtin_ctz(t);
            best = std::min(best, (int)f[S & ~(1ull << v)]);
        }
        f[S] = (uint8_t)std::max(best, b);
    }
    printf("king %dx%d: pathwidth = %d\n", m, n, (int)f[N - 1]);
    return 0;
}
