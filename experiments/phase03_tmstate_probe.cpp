// phase03_tmstate_probe.cpp -- direct TM state-space growth, COLUMN vs DIAGONAL, no per-animal
// enumeration (so it reaches higher n than phase02 and removes any Redelmeier-side artifact).
//
// We forward-explore the reachable boundary-signature set of each sweep, exactly as the real
// engine does, but we only need the DISTINCT-STATE COUNT per size-budget n (the growth base), so
// we track for each reachable signature the MIN cells used to reach it, and report, per n, the
// number of distinct signatures reachable with <= n cells (peak over the sweep position is the
// frontier; here we accumulate the whole reachable set per height/band and bucket by min-cells,
// which gives the same growth base).
//
// COLUMN sweep, height-H strip (== the incumbent engine, transition mirrors sweep8.h):
//   state = (occupancy+connectivity of the current column's H cells) as a partition with labels,
//   plus we DON'T need touch flags for a pure state-growth measurement. Transition = choose the
//   next column's occupancy mask (king step), recompute connectivity. We count distinct states
//   reachable with min-cells <= n.
//
// DIAGONAL sweep (45), processing anti-diagonals d = x+y in increasing order:
//   On anti-diagonal d, the cells are at integer x with y=d-x. Two cells (x,d-x) and (x',d-x')
//   on the SAME anti-diagonal are king-adjacent iff |x-x'|<=1 AND |Δy|<=1 -> since Δy=-(Δx),
//   |Δx|<=1 -> adjacent only if x'=x+-1, i.e. consecutive along the diagonal ARE king-neighbors
//   (offset (1,-1) is a king move). A cell (x,d-x) is king-adjacent to a cell on anti-diagonal
//   d-1 = (x'', (d-1)-x'') iff |x-x''|<=1 and |Δy|<=1; Δy = (d-x)-((d-1)-x'') = 1-(x-x''); so
//   for x''=x: Δy=1 (move (0,1)) OK; x''=x-1: Δy=0 (move (1,0)) OK; x''=x+1: Δy=2 NO. So a new
//   anti-diagonal cell at column-index x connects back to previous-diagonal cells at x and x-1.
//   The frontier we carry = occupancy+connectivity of the most recent anti-diagonal, indexed by x.
//   This is a legitimate width-bounded (along x within a band) transfer matrix.
//
// Both are exact TM state spaces; comparing their distinct-state growth base IS the FLM test.
// We bound the transverse extent to W (so the state is finite) and take W large enough that the
// size budget n binds first (W=n). Build:
//   g++ -std=c++20 -O3 -o build/phase03_tmstate experiments/phase03_tmstate_probe.cpp
// Run: build/phase03_tmstate N   (reaches n=16+ in seconds-minutes)
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <vector>
#include <unordered_map>
#include <algorithm>
#include <functional>
using namespace std;

static int N;          // size budget
static int WID;        // transverse cell-index window width (= N)

// A frontier state: a length-WID array of labels (0 = empty, else component id), canonicalized.
// Encoded as a string for hashing. Connectivity is among the labeled cells via the swept history.
typedef vector<unsigned char> Sig;

static Sig canon(Sig s){
    unsigned char map_[256]={0}; unsigned char nx=1;
    for(auto&v:s){ if(v){ if(!map_[v])map_[v]=nx++; v=map_[v]; } }
    return s;
}
struct VH{ size_t operator()(const Sig&s)const{ size_t h=1469598103934665603ull; for(auto c:s){h^=c;h*=1099511628211ull;} return h;} };

// distinct[n] = number of distinct (canonical) frontier states reachable with min-cells == ... <=n
// We do a Dijkstra-like exploration over states keyed by min-cells, capped at N.
// transition: COLUMN (dir 0) or DIAGONAL (dir 1). For each current frontier state (a labeling of
// WID slots = the just-placed line), choose the NEXT line's occupancy mask over WID slots; build
// the new labels: a new occupied slot i connects to (a) other new occupied slots adjacent within
// the new line, and (b) previous-line occupied slots per the dir's back-adjacency. Old line then
// drops away; the frontier becomes the new line's connectivity (components that had cells only in
// the old line are CLOSED and must rejoin or they become separate animals -- for a STATE-GROWTH
// proxy we keep all reachable labelings, which over-counts equally for both dirs, fair for ratio).
//
// Back-adjacency offsets (which previous-line slots j a new slot i touches):
//   COLUMN  : new column to the right of old; king back-neighbors of (x+1,i) are (x,i-1),(x,i),(x,i+1) -> j in {i-1,i,i+1}
//   DIAGONAL: new anti-diag d, slot index = x; back-neighbors on d-1 are x and x-1 -> j in {i-1,i}
// Within-line adjacency (new slot i to new slot i'): COLUMN vertical neighbors i,i+1 (Δ=(0,1)) king-adj;
//   DIAGONAL consecutive x,x+1 are king-adj (move (1,-1)). Both: i and i+1 adjacent. Same.

static const int BACK_COL[3]={-1,0,1};
static const int BACK_DIA[2]={-1,0};

static long long explore(int dir){
    // BFS by min-cells. state -> min cells. Start: empty frontier (all zero), 0 cells.
    unordered_map<Sig,int,VH> best;
    // we process in increasing cell count using buckets
    vector<vector<Sig>> bucket(N+1);
    Sig start(WID,0);
    best[start]=0; bucket[0].push_back(start);
    long long distinctTotal=0;
    vector<long long> perN(N+1,0);
    const int* back; int nb;
    if(dir==0){back=BACK_COL;nb=3;} else {back=BACK_DIA;nb=2;}
    for(int cc=0; cc<=N; ++cc){
        for(auto&cur:bucket[cc]){
            auto it=best.find(cur);
            if(it==best.end()||it->second!=cc) continue; // stale
            // enumerate next-line masks over WID slots (nonzero to make progress, but also allow
            // the all-zero? no -- empty next line ends the strip; for growth we require nonzero).
            // To bound branching, restrict masks to those within remaining budget.
            int rem=N-cc;
            // iterate masks 1..(1<<WID)-1 but prune by popcount<=rem; WID up to N=16 -> 65535, ok small N
            int lim=1<<WID;
            for(int mask=1; mask<lim; ++mask){
                int pc=__builtin_popcount(mask);
                if(pc>rem) continue;
                // build labels for the new line
                Sig nl(WID,0);
                // union-find over new-line slots + connection to current via shared component id.
                // We need connectivity THROUGH current frontier: two new slots in the same comp if
                // they connect within the new line OR via current-line cells they both touch.
                // Represent: assign each new occupied slot a provisional id, union by within-line
                // adjacency and by shared current-line component.
                static int uf[64]; static int curComp[64];
                int occ[64], no=0;
                for(int i=0;i<WID;i++) if(mask&(1<<i)) occ[no++]=i;
                for(int t=0;t<no;t++) uf[t]=t;
                function<int(int)> find=[&](int a){while(uf[a]!=a){uf[a]=uf[uf[a]];a=uf[a];}return a;};
                // within-line adjacency: occ[t], occ[u] adjacent if |i-i'|==1
                for(int t=0;t<no;t++)for(int u=t+1;u<no;u++) if(abs(occ[t]-occ[u])==1){int a=find(t),b=find(u);if(a!=b)uf[a]=b;}
                // connection through current line: for each new slot i, the set of current comps it touches
                // = labels of cur[j] for j in i+back offsets. Two new slots sharing a current comp unite.
                // map current comp label -> first new-slot-index touching it
                int seen[256]; for(int z=0;z<256;z++)seen[z]=-1;
                for(int t=0;t<no;t++){
                    int i=occ[t];
                    for(int k=0;k<nb;k++){ int j=i+back[k]; if(j<0||j>=WID)continue; unsigned char lb=cur[j]; if(lb){ if(seen[lb]<0)seen[lb]=t; else {int a=find(seen[lb]),b=find(t);if(a!=b)uf[a]=b;} } }
                }
                // assign canonical labels to new line
                int lab[64]; for(int t=0;t<no;t++)lab[t]=-1; int nlbl=1;
                for(int t=0;t<no;t++){ int r=find(t); if(lab[r]<0)lab[r]=nlbl++; nl[occ[t]]=(unsigned char)lab[r]; }
                Sig key=canon(nl);
                int nc=cc+pc;
                auto f=best.find(key);
                if(f==best.end()||f->second>nc){ best[key]=nc; if(nc<=N) bucket[nc].push_back(key); }
            }
        }
    }
    // count distinct states by min-cells bucket
    vector<long long> cnt(N+1,0);
    for(auto&kv:best) if(kv.second>=0&&kv.second<=N) cnt[kv.second]++;
    // cumulative distinct reachable with <= n cells == growth measure
    printf("# dir=%s  distinct frontier states with min-cells == k:\n", dir==0?"COLUMN":"DIAGONAL");
    long long cum=0;
    for(int k=1;k<=N;k++){ cum+=cnt[k]; double r = k>1&&cum-cnt[k]?(double)cum/(cum-cnt[k]):0; printf("  k=%2d  new=%lld  cum=%lld  cumratio=%.3f\n",k,cnt[k],cum,r); }
    return cum;
}

#include <functional>
int main(int argc,char**argv){
    N=argc>1?atoi(argv[1]):12;
    WID=argc>2?atoi(argv[2]):N;   // transverse window; default N (size budget binds)
    if(WID>16) WID=16;            // mask enumeration cap
    printf("N=%d WID=%d\n",N,WID);
    explore(0);
    explore(1);
    return 0;
}
