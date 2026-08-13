// Does inflation preserve perimeter-minimality on the king lattice?
// (Lemma 2 of Barequet & Ben-Shachar 2022, tested against eps(n)=2*ceil(2*sqrt(n))+4 = A235382.)
// For every minimal-perimeter king animal Q with |Q| <= NMAX, form I(Q) = Q + 3x3 ball,
// and compare |P(I(Q))| with eps(|I(Q)|).  Also check injectivity of I on each M_n.
#include <cstdio>
#include <cstdint>
#include <cmath>
#include <vector>
#include <set>
#include <map>
#include <algorithm>

static const int NMAX = 16;

static int eps(long long n) {  // A235382
    long long k = (long long)std::ceil(2.0 * std::sqrt((double)n) - 1e-12);
    while ((k-1)*(k-1) >= 4*n) k--;      // guard the floating sqrt
    while (k*k < 4*n) k++;
    return (int)(2*k + 4);
}

struct Shape { std::vector<std::pair<int,int>> cells; };

int main() {
    // pass 1: find eps(n) and collect all minimal-perimeter animals, n <= NMAX
    std::map<int,int> minP;
    std::map<int, std::vector<Shape>> M;

    for (int H=1; H<=26; H++) for (int W=1; W<=26; W++) {
        if (H*W > 26) continue;
        int nb = H*W;
        uint64_t rowm[32], colm[32];
        for (int r=0;r<H;r++) { rowm[r]=0; for (int c=0;c<W;c++) rowm[r] |= 1ULL<<(r*W+c); }
        for (int c=0;c<W;c++) { colm[c]=0; for (int r=0;r<H;r++) colm[c] |= 1ULL<<(r*W+c); }
        for (uint64_t m = 1; m < (1ULL<<nb); ++m) {
            int n = __builtin_popcountll(m);
            if (n < 1 || n > NMAX) continue;
            if (!(m & rowm[0]) || !(m & rowm[H-1]) || !(m & colm[0]) || !(m & colm[W-1])) continue;
            uint64_t seen = 0; int stack[64], sp=0;
            int first = __builtin_ctzll(m); stack[sp++]=first; seen |= 1ULL<<first;
            while (sp) { int idx=stack[--sp], r=idx/W, c=idx%W;
                for (int dr=-1;dr<=1;dr++) for (int dc=-1;dc<=1;dc++) { if(!dr&&!dc) continue;
                    int rr=r+dr, cc=c+dc; if(rr<0||rr>=H||cc<0||cc>=W) continue; int j=rr*W+cc;
                    if ((m>>j & 1ULL) && !(seen>>j & 1ULL)) { seen |= 1ULL<<j; stack[sp++]=j; } } }
            if (__builtin_popcountll(seen) != n) continue;
            std::set<std::pair<int,int>> occ;
            for (int r=0;r<H;r++) for (int c=0;c<W;c++) if (m>>(r*W+c) & 1ULL) occ.insert({r,c});
            std::set<std::pair<int,int>> per;
            for (auto &p : occ) for (int dr=-1;dr<=1;dr++) for (int dc=-1;dc<=1;dc++) {
                if(!dr&&!dc) continue; std::pair<int,int> q{p.first+dr,p.second+dc};
                if (!occ.count(q)) per.insert(q); }
            int P = (int)per.size();
            auto it = minP.find(n);
            if (it == minP.end() || P < it->second) { minP[n] = P; M[n].clear(); }
            if (P == minP[n]) { Shape s; s.cells.assign(occ.begin(), occ.end()); M[n].push_back(s); }
        }
    }

    printf("  n  eps_meas  eps_formula |M_n|   ->  m=n+eps  |P(I(Q))| values   eps(m)   verdict\n");
    for (int n=1; n<=NMAX; n++) {
        if (!minP.count(n)) continue;
        int e = minP[n];
        // inflate each member, record perimeter of the inflation, and check injectivity
        std::set<std::vector<std::pair<int,int>>> images;
        std::set<int> infP, infSize;
        for (auto &s : M[n]) {
            std::set<std::pair<int,int>> occ(s.cells.begin(), s.cells.end());
            std::set<std::pair<int,int>> inf = occ;
            for (auto &p : occ) for (int dr=-1;dr<=1;dr++) for (int dc=-1;dc<=1;dc++)
                inf.insert({p.first+dr, p.second+dc});
            std::set<std::pair<int,int>> per;
            for (auto &p : inf) for (int dr=-1;dr<=1;dr++) for (int dc=-1;dc<=1;dc++) {
                if(!dr&&!dc) continue; std::pair<int,int> q{p.first+dr,p.second+dc};
                if (!inf.count(q)) per.insert(q); }
            infSize.insert((int)inf.size());
            infP.insert((int)per.size());
            // normalise translation for the injectivity check
            int mr=1e9, mc=1e9; for (auto &p:inf){ mr=std::min(mr,p.first); mc=std::min(mc,p.second);}
            std::vector<std::pair<int,int>> key;
            for (auto &p:inf) key.push_back({p.first-mr, p.second-mc});
            std::sort(key.begin(), key.end());
            images.insert(key);
        }
        int m = n + e;
        printf("%3d %7d %10d %7zu   ->  %5d   ", n, e, eps(n), M[n].size(), m);
        for (int v : infP) printf("%d ", v);
        printf("  %6d   ", eps(m));
        bool sizeok = (infSize.size()==1 && *infSize.begin()==m);
        bool minok  = (infP.size()==1 && *infP.begin()==eps(m));
        bool inj    = (images.size() == M[n].size());
        printf("%s%s%s\n", sizeok?"":"SIZE-MISMATCH ", minok?"min-perim OK":"NOT MINIMAL",
               inj?", injective":", NOT INJECTIVE");
    }
    return 0;
}
