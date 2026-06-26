// phase01_width_probe.cpp -- Phase 0.1 (frontier-revision-plan §0.1 / docs/scheduling-design.md
// "B-BS 45° rotation" parked idea): does a single 45°-rotated (diagonal) transfer matrix have a
// thinner frontier than our column sweep, for KING-polyplets?
//
// A bounded-bbox transfer matrix pays ~mu^(swept bbox dimension); with the transpose trick it
// sweeps the SHORTER dimension. So the worst-case cost exponent of each method = the max over all
// n-cell animals of that method's per-animal swept width:
//   our column/row sweep (transpose) : min(H, W)
//   B-BS 45° sweep      (transpose)  : min(Dmain, Danti)      Dmain=range(x-y), Danti=range(x+y)
//   4-direction routing (not a single TM, the OTHER idea) : min(H, W, Dmain, Danti)
// We Redelmeier-enumerate every fixed polyplet of size n (count == A006770 a(n) = validation gate)
// and report, per n, max + mean of each, plus the per-axis extents and occupancies for detail.
//
// THE COMPARISON: maxHW = max min(H,W)  vs  maxDD = max min(Dmain,Danti).
//   maxDD << maxHW  -> the 45° rotation genuinely thins the worst case -> RAM cliff moves out.
//   maxDD ~= maxHW  -> deflation confirmed WITH numbers (king diagonal staircases / X-shapes
//                      saturate the rotated box just as bars/+-shapes saturate the upright box).
// Per-axis extent is the dense (B-BS) exponent; occupancy (max cells on a line) is what a sparse
// connectivity engine would pay -- reported too, since the definitive peak-STATE-count (distinct
// connectivity signatures, the real base vs our column 2.44) is the careful follow-up to this.
//
// Build: g++ -std=c++20 -O3 -o build/phase01_probe experiments/phase01_width_probe.cpp
// Run (gympie, single core): build/phase01_probe N   (N=15 ~ a few hours)
#include <cstdio>
#include <cstdlib>
#include <vector>
#include <unordered_set>
#include <algorithm>
using namespace std;

static int N;
static const int DX[8] = {1,-1,0,0,1,1,-1,-1};
static const int DY[8] = {0,0,1,-1,1,-1,1,-1};
static inline long long key(int x,int y){ return (long long)(x+2000)*1000003 + (y+2000); }
static inline bool allowed(int x,int y){ return y>0 || (y==0 && x>0); }   // > origin

static unordered_set<long long> reached;
static vector<pair<int,int>> cells;
static vector<long long> count_n;
// headline: per-n max & sum of the two single-method worst-case exponents + the routing one
static vector<int> maxHW, maxDD, max4;
static vector<long long> sumHW, sumDD, sum4;
// detail: per-n max of each axis (extent) and the two diagonal occupancies
static vector<int> mxH, mxW, mxDmain, mxDanti, mxOccMD, mxOccAD;

static void measure(){
    int n = (int)cells.size();
    if (n < 1 || n > N) return;
    count_n[n]++;
    int xmn=1<<30, xmx=-(1<<30), ymn=1<<30, ymx=-(1<<30);
    int mdmn=1<<30, mdmx=-(1<<30), admn=1<<30, admx=-(1<<30);
    for (auto& c : cells){
        xmn=min(xmn,c.first); xmx=max(xmx,c.first); ymn=min(ymn,c.second); ymx=max(ymx,c.second);
        int dm=c.first-c.second, da=c.first+c.second;
        mdmn=min(mdmn,dm); mdmx=max(mdmx,dm); admn=min(admn,da); admx=max(admx,da);
    }
    int H = ymx-ymn+1, W = xmx-xmn+1;
    int Dmain = mdmx-mdmn+1, Danti = admx-admn+1;          // rotated bbox dimensions (dense exponent)
    // diagonal OCCUPANCIES (max cells on a single line) -- sparse-engine exponent
    static vector<int> md, ad;
    md.assign(Dmain,0); ad.assign(Danti,0);
    int occMD=0, occAD=0;
    for (auto& c : cells){
        int a = ++md[(c.first-c.second)-mdmn]; if (a>occMD) occMD=a;
        int b = ++ad[(c.first+c.second)-admn]; if (b>occAD) occAD=b;
    }
    int hw = min(H,W), dd = min(Dmain,Danti), m4 = min(hw,dd);
    if (hw>maxHW[n]) maxHW[n]=hw;  sumHW[n]+=hw;
    if (dd>maxDD[n]) maxDD[n]=dd;  sumDD[n]+=dd;
    if (m4>max4[n])  max4[n]=m4;   sum4[n]+=m4;
    mxH[n]=max(mxH[n],H); mxW[n]=max(mxW[n],W);
    mxDmain[n]=max(mxDmain[n],Dmain); mxDanti[n]=max(mxDanti[n],Danti);
    mxOccMD[n]=max(mxOccMD[n],occMD); mxOccAD[n]=max(mxOccAD[n],occAD);
}

static void grow(vector<pair<int,int>> untried){
    measure();
    if ((int)cells.size() == N) return;
    while (!untried.empty()){
        auto c = untried.back(); untried.pop_back();
        vector<pair<int,int>> added;
        for (int d=0; d<8; d++){
            int nx=c.first+DX[d], ny=c.second+DY[d];
            if (!allowed(nx,ny)) continue;
            long long k = key(nx,ny);
            if (reached.insert(k).second) added.push_back({nx,ny});
        }
        cells.push_back(c);
        vector<pair<int,int>> nu = untried;
        nu.insert(nu.end(), added.begin(), added.end());
        grow(nu);
        cells.pop_back();
        for (auto& a : added) reached.erase(key(a.first,a.second));
    }
}

int main(int argc, char** argv){
    N = argc > 1 ? atoi(argv[1]) : 12;
    auto zI=[&](vector<int>&v){v.assign(N+1,0);}; auto zL=[&](vector<long long>&v){v.assign(N+1,0);};
    zL(count_n);
    zI(maxHW);zI(maxDD);zI(max4); zL(sumHW);zL(sumDD);zL(sum4);
    zI(mxH);zI(mxW);zI(mxDmain);zI(mxDanti);zI(mxOccMD);zI(mxOccAD);
    reached.insert(key(0,0));
    cells.push_back({0,0});
    vector<pair<int,int>> untried;
    for (int d=0; d<8; d++){
        int nx=DX[d], ny=DY[d];
        if (allowed(nx,ny) && reached.insert(key(nx,ny)).second) untried.push_back({nx,ny});
    }
    grow(untried);
    printf("# Phase 0.1: single-sweep worst-case width, king-polyplets. a(n)==A006770 = gate.\n");
    printf("# HEADLINE: maxHW=max min(H,W) [our column+transpose]  vs  maxDD=max min(Dmain,Danti) [B-BS 45deg]\n");
    printf("# max4=max min(H,W,Dmain,Danti) [4-dir routing, the other idea].  (mean in parens)\n");
    printf("%3s %15s | %-16s %-16s %-16s | %s\n", "n","a(n)",
           "maxHW(mean)","maxDD(mean)","max4(mean)","axis-max H/W Dmn/Dan occMD/occAD");
    for (int n=1; n<=N; n++){
        double c = count_n[n] ? (double)count_n[n] : 1;
        printf("%3d %15lld | %2d(%6.3f)       %2d(%6.3f)       %2d(%6.3f)       | %d/%d %d/%d %d/%d\n",
               n, count_n[n],
               maxHW[n], sumHW[n]/c, maxDD[n], sumDD[n]/c, max4[n], sum4[n]/c,
               mxH[n],mxW[n],mxDmain[n],mxDanti[n],mxOccMD[n],mxOccAD[n]);
    }
    return 0;
}
