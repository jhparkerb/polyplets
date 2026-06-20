// Fixed-height KNIGHT-animal transfer matrix over Z/pZ.
//
// Knight adjacency: (+-1,+-2) and (+-2,+-1). Two features make this harder than
// the king/rook/reach-V sweeps: (i) the (2,+-1) moves jump TWO columns, so the
// boundary needs the last two occupied columns; (ii) knight animals can SKIP a
// column (cells two columns apart, the one between empty), so consecutive
// occupied columns are at GAP 1 or 2 -- which must be tracked, since the gap
// decides which knight moves connect them. This is the genuine horizontal-reach
// test of the lifetime-3 law.
//
// State (P, Q, gap, partition, tT, tB): the last two OCCUPIED columns P (older),
// Q (newer) with column-gap gap in {1,2} between them (gap 0 = start, no P yet),
// a canonical component partition over filled cells of P then Q, and touch flags.
// Add an occupied column R at gap gR in {1,2} after Q:
//   R-Q: gR==1 -> |dr|==2 (the (1,+-2) moves); gR==2 -> |dr|==1 (the (2,+-1)).
//   R-P: only if gap==1 and gR==1 (so R is 2 columns past P) -> |dr|==1.
// A component left entirely in P (dropped) is stranded -> reject. Counts mod p.
//
// CLI: gf_knight H N P  -> "n  B_H^knight(n) mod P".  Validate vs the brute force
// in /tmp/knight_brute.py (must agree mod P for n<=7).

#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <unordered_map>
#include <vector>

#include "obs.h"  // shared observability/provenance runtime (docs/observability.md)

using u64 = std::uint64_t;
static int H;

static int uf_find(int* p,int x){ while(p[x]!=x){p[x]=p[p[x]];x=p[x];} return x; }
static void uf_union(int* p,int a,int b){int ra=uf_find(p,a),rb=uf_find(p,b); if(ra!=rb)p[ra]=rb;}
static int rowsOf(int m,int* r){ int k=0; for(int i=0;i<H;++i) if(m>>i&1) r[k++]=i; return k; }
static u64 packCanon(const int* roots,int k){
  int map[128]; for(int i=0;i<128;++i) map[i]=-1; u64 packed=0; int nx=0;
  for(int i=0;i<k;++i){int r=roots[i]; if(map[r]<0)map[r]=nx++; packed|=(u64)(map[r]&0xF)<<(4*i);}
  return packed; }

struct State{ int P,Q,gap; u64 lab; bool tT,tB; };
struct Key{ int P,Q,gap,flags; u64 lab;
  bool operator==(const Key&o)const{return P==o.P&&Q==o.Q&&gap==o.gap&&flags==o.flags&&lab==o.lab;} };
struct KeyHash{ size_t operator()(const Key&k)const{ u64 h=1469598103934665603ull;
  for(u64 v:{(u64)k.P,(u64)k.Q,(u64)k.gap,(u64)k.flags,k.lab}){h^=v;h*=1099511628211ull;} return h; } };

// (P,Q,gap) + new column R at gap gR -> partition over (Q,R); false if a P-only
// component is stranded.
static bool step(int P,int Q,int gap,u64 lab,int R,int gR,u64* outLab){
  int rp[16],rq[16],rr[16];
  int nP=rowsOf(P,rp), nQ=rowsOf(Q,rq), nR=rowsOf(R,rr);
  int tot=nP+nQ+nR, par[48]; for(int i=0;i<tot;++i) par[i]=i;
  int lpq[32]; for(int i=0;i<nP+nQ;++i) lpq[i]=(int)((lab>>(4*i))&0xF);
  for(int i=0;i<nP+nQ;++i) for(int j=i+1;j<nP+nQ;++j) if(lpq[i]==lpq[j]) uf_union(par,i,j);
  for(int a=0;a<nR;++a){
    int nodeR=nP+nQ+a, rR=rr[a];
    for(int j=0;j<nQ;++j){                         // R-Q
      int dr=rR-rq[j]; if(dr<0)dr=-dr;
      if((gR==1&&dr==2)||(gR==2&&dr==1)) uf_union(par,nodeR,nP+j);
    }
    if(gap==1&&gR==1)                               // R-P only when R is 2 past P
      for(int i=0;i<nP;++i){ int dr=rR-rp[i]; if(dr<0)dr=-dr; if(dr==1) uf_union(par,nodeR,i); }
  }
  bool alive[48]; for(int i=0;i<tot;++i) alive[i]=false;
  for(int j=0;j<nQ;++j) alive[uf_find(par,nP+j)]=true;
  for(int a=0;a<nR;++a) alive[uf_find(par,nP+nQ+a)]=true;
  for(int i=0;i<nP;++i) if(!alive[uf_find(par,i)]) return false;
  int roots[32],k=0;
  for(int j=0;j<nQ;++j) roots[k++]=uf_find(par,nP+j);
  for(int a=0;a<nR;++a) roots[k++]=uf_find(par,nP+nQ+a);
  *outLab=packCanon(roots,k); return true;
}

int main(int argc,char**argv){
  if(argc<4){ std::fprintf(stderr,"usage: %s H N P\n",argv[0]); return 2; }
  H=std::atoi(argv[1]); const int N=std::atoi(argv[2]); const u64 P=std::strtoull(argv[3],nullptr,10);
  if(H<1||H>7){ std::fprintf(stderr,"H out of range (1..7)\n"); return 2; }
  const int full=(1<<H)-1, top=1, bot=1<<(H-1);
  obs::Reporter rep("gfknight-H" + std::to_string(H) + "-N" + std::to_string(N), N,
                    "H=" + std::to_string(H) + " P=" + std::to_string(P));
  std::unordered_map<Key,int,KeyHash> id; std::vector<State> states;
  auto intern=[&](int Pm,int Qm,int gap,u64 lab,bool tT,bool tB)->int{
    Key k{Pm,Qm,gap,(tT?2:0)|(tB?1:0),lab}; auto it=id.find(k); if(it!=id.end()) return it->second;
    int s=(int)states.size(); id.emplace(k,s); states.push_back({Pm,Qm,gap,lab,tT,tB}); return s; };
  std::vector<int> startId,startCells;
  for(int m=1;m<=full;++m){
    int rr[16]; int nq=rowsOf(m,rr); int roots[16]; for(int i=0;i<nq;++i) roots[i]=i;
    startId.push_back(intern(0,m,0,packCanon(roots,nq),m&top,m&bot));
    startCells.push_back(__builtin_popcount(m));
  }
  std::vector<int> efrom,eto,eadd;
  for(size_t s=0;s<states.size();++s){
    State st=states[s];
    for(int R=1;R<=full;++R) for(int gR=1;gR<=2;++gR){
      u64 nl; if(!step(st.P,st.Q,st.gap,st.lab,R,gR,&nl)) continue;
      int t=intern(st.Q,R,gR,nl, st.tT||(R&top), st.tB||(R&bot));
      efrom.push_back((int)s); eto.push_back(t); eadd.push_back(__builtin_popcount(R));
    }
  }
  const int S=(int)states.size(); const size_t E=efrom.size();
  std::vector<char> term(S);
  for(int s=0;s<S;++s){
    int k=__builtin_popcount(states[s].P)+__builtin_popcount(states[s].Q), mx=0;
    for(int i=0;i<k;++i) mx=std::max(mx,(int)((states[s].lab>>(4*i))&0xF));
    term[s]=(k>0)&&(mx==0)&&states[s].tT&&states[s].tB;
  }
  const int Wn=H+1; std::vector<u64> buf((size_t)Wn*S,0);
  auto row=[&](int n)->u64*{ return &buf[(size_t)(n%Wn)*S]; };
  std::vector<u64> res(N+1,0);
  for(int n=1;n<=N;++n){
    u64* bn=row(n); std::fill(bn,bn+S,0);
    for(size_t i=0;i<startId.size();++i) if(startCells[i]==n) bn[startId[i]]=(bn[startId[i]]+1)%P;
    for(size_t e=0;e<E;++e) if(n-eadd[e]>=1){ u64 v=row(n-eadd[e])[efrom[e]]; if(v) bn[eto[e]]=(bn[eto[e]]+v)%P; }
    u64 acc=0; for(int s=0;s<S;++s) if(term[s]&&bn[s]) acc=(acc+bn[s])%P;
    res[n]=acc;
    rep.beat(n, "n=" + std::to_string(n) + " states=" + std::to_string(S));
  }
  for(int n=1;n<=N;++n) std::printf("%d %llu\n",n,(unsigned long long)res[n]);
  rep.done("result=" + std::to_string((unsigned long long)res[N]) +
           " states=" + std::to_string(S));
  return 0;
}
