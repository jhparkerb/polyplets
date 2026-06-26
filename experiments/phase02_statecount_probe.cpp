// phase02_statecount_probe.cpp -- THE FLM decisive test (frontier-revision-plan 0.1 follow-up).
//
// phase01 (worst-case WIDTH) showed maxHW = maxDD = n: the 45 rotation gives zero worst-case
// frontier-width improvement. But width = peak frontier SIZE, not the distinct STATE count -- and
// the incumbent's real per-term cost base is the distinct-boundary-SIGNATURE growth (the engine's
// measured peak_states ratio ~2.42/term at the diagonal H=n). phase01 explicitly flagged the
// distinct state-count as "the careful follow-up". This is it.
//
// We count the DISTINCT boundary signatures a real transfer-matrix sweep instantiates, two ways,
// over the same object (all king-polyplets), and compare the growth BASE:
//   dir 0 COLUMN  (height-bounded): cut line x=c, frontier = swept cells with x==c, connectivity
//                 through {x<=c}; perp coord = y. (== the incumbent engine's state.)
//   dir 1 DIAG    (width-bounded by the 45 rotation): cut line x-y=c, frontier = swept cells with
//                 x-y==c, connectivity through {x-y<=c}; perp coord = x+y. (== B-BS rotation.)
// For each animal and each internal cut we form the canonical connectivity partition of the
// frontier (the exact TM state, with perp-gaps encoded so geometry is preserved) and add it to a
// per-(n,dir,cut) set. PEAK over cut of |distinct signatures| at size n, term-over-term, is the
// growth base. col_peak ratio must reproduce the engine's ~2.42 (validation of the proxy);
// diag_peak ratio < 2.42 => width-bounding bends the base (FLM survives); >= 2.42 => killed.
//
// Also reports the peak frontier WIDTH per direction (max cells on a cut) -- so the state-base
// signal can be read against the width signal (phase01) in one table.
//
// Optimized cut sweep: process cuts left-to-right incrementally with a union-find rebuilt once
// per cut but only over swept cells, animals are small (n<=13) so this is fast enough.
//
// Build: g++ -std=c++20 -O3 -o build/phase02_statecount experiments/phase02_statecount_probe.cpp
// Run (gympie, single core): build/phase02_statecount N    (N=12 ~ minutes, N=13 ~ tens of min)
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <vector>
#include <unordered_set>
#include <unordered_map>
#include <algorithm>
#include <functional>
#include <string>
using namespace std;

static int N;
static const int DX[8] = {1,-1,0,0,1,1,-1,-1};
static const int DY[8] = {0,0,1,-1,1,-1,1,-1};
static inline long long key(int x,int y){ return (long long)(x+2000)*4000 + (y+2000); }
static inline bool allowed(int x,int y){ return y>0 || (y==0 && x>0); }

static unordered_set<long long> reached;
static vector<pair<int,int>> cells;
static vector<long long> count_n;

struct Key { int n, dir, c; bool operator==(const Key&o)const{return n==o.n&&dir==o.dir&&c==o.c;} };
struct KeyH { size_t operator()(const Key&k)const{ return ((size_t)(k.n*131+k.dir))*1000003u + (size_t)(k.c+1000); } };
static unordered_map<Key, unordered_set<string>, KeyH> sigsets;
static vector<vector<int>> peakWidth; // peakWidth[dir][n] = max frontier width seen

static void recordCut(int n, int dir){
    int m=(int)cells.size();
    static vector<int> cv; cv.resize(m);
    int umn=1<<30,umx=-(1<<30);
    for(int i=0;i<m;i++){ int v=(dir==0)?cells[i].first:cells[i].first-cells[i].second; cv[i]=v; umn=min(umn,v);umx=max(umx,v);}
    // position lookup for adjacency
    static unordered_map<long long,int> pos; pos.clear(); pos.reserve(m*2);
    for(int i=0;i<m;i++) pos[key(cells[i].first,cells[i].second)]=i;
    for(int u=umn; u<umx; ++u){
        // swept cells: cv<=u
        static vector<int> swept; swept.clear();
        static vector<int> sidx; sidx.assign(m,-1);
        for(int i=0;i<m;i++) if(cv[i]<=u){ sidx[i]=(int)swept.size(); swept.push_back(i); }
        int s=(int)swept.size(); if(!s) continue;
        static vector<int> uf; uf.assign(s,0); for(int i=0;i<s;i++)uf[i]=i;
        function<int(int)> find=[&](int a){ while(uf[a]!=a){uf[a]=uf[uf[a]];a=uf[a];} return a; };
        for(int j=0;j<s;j++){ auto&c=cells[swept[j]];
            for(int d=0;d<8;d++){ auto it=pos.find(key(c.first+DX[d],c.second+DY[d])); if(it!=pos.end()&&sidx[it->second]>=0){ int a=find(j),b=find(sidx[it->second]); if(a!=b)uf[a]=b; } } }
        static vector<pair<int,int>> fr; fr.clear();
        for(int j=0;j<s;j++){ int i=swept[j]; if(cv[i]==u){ int perp=(dir==0)?cells[i].second:cells[i].first+cells[i].second; fr.push_back({perp,j}); } }
        sort(fr.begin(),fr.end());
        if((int)fr.size()>peakWidth[dir][n]) peakWidth[dir][n]=(int)fr.size();
        string sig; sig.reserve(fr.size()*2+2);
        unordered_map<int,int> lab; int nl=1; int prevv=fr.empty()?0:fr[0].first;
        for(auto&p:fr){ int dv=p.first-prevv; prevv=p.first; int r=find(p.second); if(!lab.count(r))lab[r]=nl++; sig.push_back((char)(dv+1)); sig.push_back((char)(lab[r]+1)); }
        sigsets[Key{n,dir,u}].insert(sig);
    }
}

static void measure(){
    int n=(int)cells.size(); if(n<1||n>N)return; count_n[n]++;
    recordCut(n,0); recordCut(n,1);
}
static void grow(vector<pair<int,int>> untried){
    measure();
    if((int)cells.size()==N) return;
    while(!untried.empty()){
        auto c=untried.back(); untried.pop_back();
        vector<pair<int,int>> added;
        for(int d=0;d<8;d++){ int nx=c.first+DX[d],ny=c.second+DY[d]; if(!allowed(nx,ny))continue; long long kk=key(nx,ny); if(reached.insert(kk).second)added.push_back({nx,ny}); }
        cells.push_back(c);
        vector<pair<int,int>> nu=untried; nu.insert(nu.end(),added.begin(),added.end());
        grow(nu); cells.pop_back();
        for(auto&a:added) reached.erase(key(a.first,a.second));
    }
}
int main(int argc,char**argv){
    N=argc>1?atoi(argv[1]):11;
    count_n.assign(N+1,0);
    peakWidth.assign(2, vector<int>(N+1,0));
    reached.insert(key(0,0)); cells.push_back({0,0});
    vector<pair<int,int>> untried;
    for(int d=0;d<8;d++){ int nx=DX[d],ny=DY[d]; if(allowed(nx,ny)&&reached.insert(key(nx,ny)).second)untried.push_back({nx,ny}); }
    grow(untried);
    vector<vector<long long>> peak(2, vector<long long>(N+1,0));
    for(auto&kv:sigsets){ const Key&k=kv.first; long long sz=(long long)kv.second.size(); if(sz>peak[k.dir][k.n]) peak[k.dir][k.n]=sz; }
    printf("# Phase 02: PEAK distinct boundary-SIGNATURE count + peak frontier WIDTH per term.\n");
    printf("# col = height-bounded (incumbent, base must reproduce ~2.42); diag = width-bounded (B-BS 45).\n");
    printf("%3s %14s | %11s %6s %5s | %11s %6s %5s\n","n","a(n)","col_states","ratio","colW","diag_states","ratio","diaW");
    for(int n=1;n<=N;n++){
        double rc = n>1&&peak[0][n-1]?(double)peak[0][n]/peak[0][n-1]:0;
        double rd = n>1&&peak[1][n-1]?(double)peak[1][n]/peak[1][n-1]:0;
        printf("%3d %14lld | %11lld %6.3f %5d | %11lld %6.3f %5d\n",n,count_n[n],peak[0][n],rc,peakWidth[0][n],peak[1][n],rd,peakWidth[1][n]);
    }
    return 0;
}
