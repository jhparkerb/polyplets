// diag_width_probe.cpp -- test the load-bearing claim for a 4-direction lambda^(n/2)
// king-polyplet enumerator: for every fixed polyplet of size n, the minimum over the four
// sweep directions of the boundary width is small (conjectured ~ n/2, the X-shape worst case).
//
// boundary width per direction = the animal's max occupancy on a line perpendicular to the
// sweep (= transfer-matrix frontier size, the exponent of that sweep's cost):
//   column sweep   -> H = row extent            (cost ~ mu^H)
//   row sweep      -> W = col extent             (~ mu^W)
//   main-diag sweep-> max cells on any (x-y)=c   (~ mu^maxMD)
//   anti-diag sweep-> max cells on any (x+y)=c   (~ mu^maxAD)
// m = min(H, W, maxMD, maxAD). If max over all animals of m grows like n/2 (not n), routing
// each animal to its thinnest direction gives a lambda^(n/2) method -> a(22) in minutes.
//
// Reports per n: animal count (== A006770 a(n), a built-in check), max(m), and the histogram
// of m. Standard Redelmeier (fixed polyplets, origin = lex-min cell, half-plane anchoring).
// Build: g++ -std=c++20 -O3 -o build/diag_probe experiments/diag_width_probe.cpp
// Run on gympie (local), single core. Usage: build/diag_probe N
#include <cstdio>
#include <cstdlib>
#include <vector>
#include <unordered_set>
#include <algorithm>
using namespace std;

static int N;
static const int DX[8] = {1, -1, 0, 0, 1, 1, -1, -1};
static const int DY[8] = {0, 0, 1, -1, 1, -1, 1, -1};

static inline long long key(int x, int y) { return (long long)(x + 2000) * 1000003 + (y + 2000); }
static inline bool allowed(int x, int y) { return y > 0 || (y == 0 && x > 0); }  // > origin

static unordered_set<long long> reached;
static vector<pair<int,int>> cells;
static vector<long long> count_n;          // count_n[n]
static vector<vector<long long>> hist;     // hist[n][m_ext]
static vector<int> maxm;                    // maxm[n] = max m_ext (extent-based)
static vector<int> maxm_occ;                // max m_occ (occupancy-based)

static void measure() {
    int n = (int)cells.size();
    if (n < 1 || n > N) return;
    count_n[n]++;
    int xmn = 1<<30, xmx = -(1<<30), ymn = 1<<30, ymx = -(1<<30);
    for (auto& c : cells) {
        xmn = min(xmn, c.first); xmx = max(xmx, c.first);
        ymn = min(ymn, c.second); ymx = max(ymx, c.second);
    }
    int H = ymx - ymn + 1, W = xmx - xmn + 1;
    // diagonal EXTENTS (range of x-y and x+y) -- the perpendicular extent a standard
    // transfer matrix pays mu^(.) for -- and diagonal OCCUPANCIES (max cells on a line).
    int mdmn = 1<<30, mdmx = -(1<<30), admn = 1<<30, admx = -(1<<30);
    static vector<int> md, ad;
    int mdBase = xmn - ymx, mdLen = (xmx - ymn) - mdBase + 1;
    int adBase = xmn + ymn, adLen = (xmx + ymx) - adBase + 1;
    md.assign(mdLen, 0); ad.assign(adLen, 0);
    int maxMD = 0, maxAD = 0;
    for (auto& c : cells) {
        int dm = c.first - c.second, da = c.first + c.second;
        mdmn = min(mdmn, dm); mdmx = max(mdmx, dm);
        admn = min(admn, da); admx = max(admx, da);
        int a = ++md[dm - mdBase]; if (a > maxMD) maxMD = a;
        int b = ++ad[da - adBase]; if (b > maxAD) maxAD = b;
    }
    int Dmain = mdmx - mdmn + 1, Danti = admx - admn + 1;
    int m_ext = min(min(H, W), min(Dmain, Danti));   // standard extent-based engine cost
    int m_occ = min(min(H, W), min(maxMD, maxAD));    // occupancy-based (smarter) engine
    if (m_ext > maxm[n]) maxm[n] = m_ext;
    if (m_occ > maxm_occ[n]) maxm_occ[n] = m_occ;
    if (m_ext >= (int)hist[n].size()) hist[n].resize(m_ext + 1, 0);
    hist[n][m_ext]++;
}

static void grow(vector<pair<int,int>> untried) {
    measure();
    if ((int)cells.size() == N) return;
    while (!untried.empty()) {
        auto c = untried.back(); untried.pop_back();
        vector<pair<int,int>> added;
        for (int d = 0; d < 8; d++) {
            int nx = c.first + DX[d], ny = c.second + DY[d];
            if (!allowed(nx, ny)) continue;
            long long k = key(nx, ny);
            if (reached.insert(k).second) added.push_back({nx, ny});
        }
        cells.push_back(c);
        vector<pair<int,int>> nu = untried;
        nu.insert(nu.end(), added.begin(), added.end());
        grow(nu);
        cells.pop_back();
        for (auto& a : added) reached.erase(key(a.first, a.second));
    }
}

int main(int argc, char** argv) {
    N = argc > 1 ? atoi(argv[1]) : 12;
    count_n.assign(N + 1, 0); maxm.assign(N + 1, 0); maxm_occ.assign(N + 1, 0);
    hist.assign(N + 1, {});
    reached.insert(key(0, 0));
    cells.push_back({0, 0});
    vector<pair<int,int>> untried;
    for (int d = 0; d < 8; d++) {
        int nx = DX[d], ny = DY[d];
        if (allowed(nx, ny) && reached.insert(key(nx, ny)).second) untried.push_back({nx, ny});
    }
    grow(untried);
    printf("%3s %14s %8s %8s   histogram of m_ext = min(H,W,Dmain,Danti)  [m:count]\n",
           "n", "a(n)", "max_ext", "max_occ");
    for (int n = 1; n <= N; n++) {
        printf("%3d %14lld %8d %8d   ", n, count_n[n], maxm[n], maxm_occ[n]);
        for (int m = 1; m < (int)hist[n].size(); m++)
            if (hist[n][m]) printf("%d:%lld ", m, hist[n][m]);
        printf("\n");
    }
    return 0;
}
