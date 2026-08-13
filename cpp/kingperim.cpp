// Exhaustive minimal-site-perimeter king animals (polyplets) for small n.
// For each bounding-box shape, enumerate all subsets, keep connected ones whose
// bounding box is exactly the grid (dedup across grids + translations), and
// record perimeter |P| and border |B| under 8-neighbour adjacency.
#include <cstdio>
#include <cstdint>
#include <vector>
#include <map>

static const int NMAX = 25;

struct Rec { int minP = 1e9; std::map<std::pair<int,int>,long long> stats; };
// stats key: (|B|, |P|-|B|) -> count, among shapes with |P| == minP

int main() {
    Rec rec[NMAX+1];

    std::vector<std::pair<int,int>> boxes;
    for (int H=1; H<=30; H++) for (int W=1; W<=30; W++)
        if (H*W <= 30 && H*W >= 1) boxes.push_back({H,W});

    for (auto &bx : boxes) {
        int H = bx.first, W = bx.second;
        int nb = H*W;
        uint64_t total = 1ULL << nb;
        // row/col occupancy masks for a fast exact-bounding-box test
        uint64_t rowm[32], colm[32];
        for (int r=0;r<H;r++) { rowm[r]=0; for (int c=0;c<W;c++) rowm[r] |= 1ULL<<(r*W+c); }
        for (int c=0;c<W;c++) { colm[c]=0; for (int r=0;r<H;r++) colm[c] |= 1ULL<<(r*W+c); }
        // padded coords: cell (r,c) of grid -> pad (r+1, c+1) in (H+2)x(W+2)
        for (uint64_t m = 1; m < total; ++m) {
            int n = __builtin_popcountll(m);
            if (n < 1 || n > NMAX) continue;
            // bounding box must be exactly the grid: touch row0, row H-1, col0, col W-1
            if (!(m & rowm[0]) || !(m & rowm[H-1]) || !(m & colm[0]) || !(m & colm[W-1])) continue;
            // connectivity (king) via flood fill
            uint64_t seen = 0, stack[64]; int sp=0;
            int first = __builtin_ctzll(m);
            stack[sp++] = first; seen |= 1ULL<<first;
            while (sp) {
                int idx = (int)stack[--sp];
                int r = idx / W, c = idx % W;
                for (int dr=-1; dr<=1; dr++) for (int dc=-1; dc<=1; dc++) {
                    if (!dr && !dc) continue;
                    int rr=r+dr, cc=c+dc;
                    if (rr<0||rr>=H||cc<0||cc>=W) continue;
                    int j = rr*W+cc;
                    if ((m>>j & 1ULL) && !(seen>>j & 1ULL)) { seen |= 1ULL<<j; stack[sp++]=j; }
                }
            }
            if (__builtin_popcountll(seen) != n) continue;
            // perimeter and border on the padded grid
            int PH = H+2, PW = W+2;
            std::vector<char> o(PH*PW, 0);
            for (int r=0;r<H;r++) for (int c=0;c<W;c++) if (m>>(r*W+c) & 1ULL) o[(r+1)*PW+(c+1)] = 1;
            int P=0, B=0;
            for (int r=0;r<PH;r++) for (int c=0;c<PW;c++) {
                int nOcc=0, nEmp=0;
                for (int dr=-1; dr<=1; dr++) for (int dc=-1; dc<=1; dc++) {
                    if (!dr && !dc) continue;
                    int rr=r+dr, cc=c+dc;
                    char v = (rr<0||rr>=PH||cc<0||cc>=PW) ? 0 : o[rr*PW+cc];
                    if (v) nOcc++; else nEmp++;
                }
                if (o[r*PW+c]) { if (nEmp>0) B++; }
                else { if (nOcc>0) P++; }
            }
            Rec &R = rec[n];
            if (P < R.minP) { R.minP = P; R.stats.clear(); }
            if (P == R.minP) R.stats[{B, P-B}]++;
        }
    }

    printf("  n  eps(n)   (|B|, c=|P|-|B|) x count  among minimal-perimeter animals\n");
    for (int n=1;n<=NMAX;n++) {
        printf("%3d %6d   ", n, rec[n].minP);
        for (auto &kv : rec[n].stats)
            printf("(%d,%d)x%lld  ", kv.first.first, kv.first.second, kv.second);
        printf("\n");
    }
    return 0;
}
