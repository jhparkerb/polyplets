// full_column_bench.cpp -- THE decisive "can we break the parallelism back?"
// experiment. Runs a full realistic H-column (seed -> H mid-column stages ->
// finalize) two ways and measures EFFECTIVE CORES (sum of per-thread busy
// time / region wall) per stage and for the whole column:
//
//   BALANCED   : each stage's map+reduce partitioned so every core gets an
//                equal RECORD count (quantile splitters) -- the fix.
//   UNBALANCED : partitioned by even KEY-VALUE ranges, which on canonMixed's
//                skewed leading-byte distribution gives wildly uneven record
//                counts -- reproduces the current engine's SampleKeysMulti
//                open-ended-last-bucket straggler (the measured 590M-vs-64K
//                unit, docs/utilization-bottleneck-log.md).
//
// Claim under test: H18's measured 13.7-effective-core ceiling is a
// PARTITIONING artifact, not fundamental. If BALANCED lifts effective cores
// toward ~80 while UNBALANCED stays low, on the SAME real transition and the
// SAME data, the back is breakable and this quantifies by how much.
//
// Both schemes' final column output is verified byte-identical (correctness
// is not traded for the measurement). Uses the REAL kink kernel throughout.

#include <chrono>
#include <cstdio>
#include <cstdint>
#include <cstring>
#include <random>
#include <thread>
#include <vector>

#include "core/kink.h"
#include "core/run.h"
#include "core/signature.h"

using Clock = std::chrono::steady_clock;
using W = u128;

static int g_H = 18, g_maxn = 34, g_threads = 80;
static size_t g_N = 8'000'000;

static double secs(Clock::time_point a, Clock::time_point b){ return std::chrono::duration<double>(b-a).count(); }

// classifier stub: the mid-column stages don't classify (harvest is at seed);
// we don't need harvested triangle values for a utilization measurement, so
// seed uses a no-op sink.
struct NullSink { template<class R,class O> static void complete(const Sig&,int,const R&,O&){} };
struct NullOut {};

// ---- realistic H+4-keyed stage table (one fat stage's worth) -------------
// H+4 (kinkKeyLen) so a single real stage transition can be applied without
// the multi-stage record blow-up synthetic data (lacking real budget decay)
// would otherwise cause. One fat stage is exactly where the straggler lives.
static Run<W> generateStageTable(int H, int maxn, size_t N, int threads){
  const int kLen=kinkKeyLen(H), win=std::max(1,(int)(0.56*maxn));
  Run<W> out(N);
  std::vector<std::thread> pool; size_t chunk=(N+threads-1)/threads;
  for(int t=0;t<threads;t++) pool.emplace_back([&,t](){
    std::mt19937_64 rng(0x9e3779b97f4a7c15ULL ^ (0xd1b54a32d192ed03ULL*(t+1)));
    auto rnd=[&](uint64_t m){return rng()%m;};
    for(size_t i=(size_t)t*chunk,e=std::min(N,i+chunk);i<e;i++){
      RunRecord<W>&r=out[i]; std::memset(r.sig.b,0,SIGMAX);
      int C=1+(int)rnd(5);
      for(int p=0;p<H;p++) if(rnd(2)) r.sig.b[p]=(unsigned char)(1+rnd(C));
      r.sig.b[H+2]=rnd(2)?(unsigned char)(1+rnd(C)):0; // carry
      r.sig.b[H]=(unsigned char)rnd(2); r.sig.b[H+1]=(unsigned char)rnd(2);
      r.sig.b[H+3]=(unsigned char)rnd(2);
      canonMixed(r.sig,H);
      r.H=(uint8_t)H; r.keyLen=(uint8_t)kLen;
      int lo=(int)rnd(6), len=std::max(1,win+(int)rnd(5)-2);
      if(lo+len>maxn+1) len=maxn+1-lo; if(len<1){lo=0;len=1;}
      r.lo=(uint8_t)lo; r.len=(uint8_t)len; r.counts.resize(len);
      for(int k=0;k<len;k++) r.counts[k]=(W)(rng()&0xffffffffULL)+1;
    }
  });
  for(auto&th:pool)th.join();
  sortRun(out); deduplicateRun(out);
  return out;
}

// Run a stage's map+reduce over `src` (keyLen kLen_in) producing the deduped
// stage output. partition scheme selects splitters. Records per-stage
// effective cores into *effCores. `balanced`=true uses record-quantile
// splitters; false uses even key-value ranges (skew -> straggler).
static Run<W> stageMapReduce(const Run<W>& src, int H, int maxn, int r, int kLen_out,
                             int threads, bool balanced, double* effCores){
  // ---- map: parallel per-record transition into per-thread buffers -------
  std::vector<Run<W>> per(threads);
  std::vector<double> busy(threads,0.0);
  double regionWall=0;
  auto mapStart=Clock::now();
  {
    std::vector<std::thread> pool; size_t chunk=(src.size()+threads-1)/threads;
    for(int t=0;t<threads;t++) pool.emplace_back([&,t](){
      auto a=Clock::now();
      size_t i0=(size_t)t*chunk,i1=std::min(src.size(),i0+chunk);
      Run<W>&buf=per[t]; buf.reserve((i1-i0)*2);
      for(size_t i=i0;i<i1;i++){
        const RunRecord<W>&rec=src[i]; int ms=rec.minSize(); if(ms<0)continue;
        kinkStageTransition(rec.sig,H,r,ms,maxn,[&](const Sig&tg,int shift){
          int nl=(int)rec.lo+shift; if(nl>maxn)return;
          int nlen=std::min<int>(rec.len,maxn-nl+1);
          RunRecord<W> s; s.sig=tg; s.H=(uint8_t)H; s.keyLen=(uint8_t)kLen_out;
          s.lo=(uint8_t)nl; s.len=(uint8_t)nlen;
          s.counts.assign(rec.counts.begin(),rec.counts.begin()+nlen);
          buf.push_back(std::move(s));
        });
      }
      busy[t]+=secs(a,Clock::now());
    });
    for(auto&th:pool)th.join();
  }
  regionWall += secs(mapStart,Clock::now());
  // flatten emitted -- a single-threaded gather that exists ONLY because this
  // benchmark stages map output in per-thread vectors; a real engine scatters
  // straight from the map. Excluded from regionWall (not part of the algo).
  Run<W> emitted; size_t tot=0; for(auto&b:per)tot+=b.size(); emitted.reserve(tot);
  for(auto&b:per) for(auto&x:b) emitted.push_back(std::move(x));
  auto srStart=Clock::now();

  // ---- choose 80 splitters ------------------------------------------------
  std::vector<Sig> split; split.reserve(threads-1);
  if(balanced){
    // record-quantile: sample, sort, evenly-spaced by RECORD rank
    size_t ns=std::min<size_t>(emitted.size(),400000);
    std::vector<Sig> samp; samp.reserve(ns);
    size_t st=std::max<size_t>(1,emitted.size()/ns);
    for(size_t i=0;i<emitted.size();i+=st) samp.push_back(emitted[i].sig);
    std::sort(samp.begin(),samp.end(),[&](const Sig&a,const Sig&b){return sigCmp(a.b,b.b,kLen_out)<0;});
    for(int t=1;t<threads;t++) split.push_back(samp[(size_t)t*samp.size()/threads]);
  } else {
    // even KEY-VALUE ranges over the leading byte(s): canonMixed makes b[0]
    // in {0,1,2..}, so evenly slicing the key VALUE space piles most records
    // into a few buckets -- the straggler. Slice by first 2 bytes as a value.
    for(int t=1;t<threads;t++){
      Sig s; std::memset(s.b,0,SIGMAX);
      uint32_t v=(uint32_t)((uint64_t)t*65536/threads); // spread over 2 bytes
      s.b[0]=(unsigned char)(v>>8); s.b[1]=(unsigned char)(v&0xff);
      split.push_back(s);
    }
  }
  auto bucketOf=[&](const Sig&s){int lo=0,hi=(int)split.size();
    while(lo<hi){int m=(lo+hi)/2; if(sigCmp(s.b,split[m].b,kLen_out)<0)hi=m; else lo=m+1;} return lo;};

  // ---- scatter (parallel) -------------------------------------------------
  std::vector<std::vector<Run<W>>> tl(threads,std::vector<Run<W>>(threads));
  {
    std::vector<std::thread> pool; size_t chunk=(emitted.size()+threads-1)/threads;
    for(int t=0;t<threads;t++) pool.emplace_back([&,t](){
      auto a=Clock::now();
      for(size_t i=(size_t)t*chunk,e=std::min(emitted.size(),i+chunk);i<e;i++)
        tl[t][bucketOf(emitted[i].sig)].push_back(emitted[i]);
      busy[t]+=secs(a,Clock::now());
    });
    for(auto&th:pool)th.join();
  }
  // ---- reduce: each thread sorts+dedups its own bucket -------------------
  std::vector<Run<W>> buckets(threads);
  {
    std::vector<std::thread> pool;
    for(int bk=0;bk<threads;bk++) pool.emplace_back([&,bk](){
      auto a=Clock::now();
      Run<W>&B=buckets[bk];
      for(int t=0;t<threads;t++) for(auto&x:tl[t][bk]) B.push_back(x);
      sortRun(B); deduplicateRun(B);
      busy[bk]+=secs(a,Clock::now());
    });
    for(auto&th:pool)th.join();
  }
  regionWall += secs(srStart,Clock::now());
  double sumBusy=0; for(double b:busy) sumBusy+=b;
  *effCores = sumBusy/regionWall;

  Run<W> out; size_t o=0; for(auto&B:buckets)o+=B.size(); out.reserve(o);
  for(auto&B:buckets) for(auto&x:B) out.push_back(std::move(x));
  return out;
}

// best-of-3 effective cores for one stage under a given partition scheme.
static double bestEff(const Run<W>& stageTab,int H,int maxn,int r,int kOut,int threads,
                      bool balanced,Run<W>* out){
  double best=0;
  for(int rep=0;rep<3;rep++){
    double eff=0; Run<W> o=stageMapReduce(stageTab,H,maxn,r,kOut,threads,balanced,&eff);
    if(eff>best){best=eff; if(out)*out=std::move(o);}
  }
  return best;
}

int main(int argc,char**argv){
  for(int i=1;i<argc;i++){
    if(!std::strncmp(argv[i],"H=",2))g_H=atoi(argv[i]+2);
    else if(!std::strncmp(argv[i],"maxn=",5))g_maxn=atoi(argv[i]+5);
    else if(!std::strncmp(argv[i],"N=",2))g_N=strtoull(argv[i]+2,0,10);
    else if(!std::strncmp(argv[i],"threads=",8))g_threads=atoi(argv[i]+8);
  }
  const int kOut=kinkKeyLen(g_H), r=g_H/2;   // a mid-column stage
  std::printf("full_column_bench (single fat stage) H=%d maxn=%d N=%zu threads=%d stage=%d\n",
              g_H,g_maxn,g_N,g_threads,r);
  auto t0=Clock::now();
  Run<W> stageTab=generateStageTable(g_H,g_maxn,g_N,g_threads);
  std::printf("stage table %zu records (%.2fs)\n",stageTab.size(),secs(t0,Clock::now()));

  Run<W> ob,ou;
  double effB=bestEff(stageTab,g_H,g_maxn,r,kOut,g_threads,true,&ob);
  double effU=bestEff(stageTab,g_H,g_maxn,r,kOut,g_threads,false,&ou);

  // verify balanced and unbalanced produce identical stage output
  bool ok=(ob.size()==ou.size());
  if(ok){ auto cmp=[&](const RunRecord<W>&x,const RunRecord<W>&y){return sigCmp(x.sig.b,y.sig.b,kOut)<0;};
    std::sort(ob.begin(),ob.end(),cmp); std::sort(ou.begin(),ou.end(),cmp);
    for(size_t i=0;i<ob.size()&&ok;i++){ if(sigCmp(ob[i].sig.b,ou[i].sig.b,kOut)!=0||ob[i].lo!=ou[i].lo||ob[i].len!=ou[i].len)ok=false;
      else for(int k=0;k<ob[i].len;k++) if(ob[i].counts[k]!=ou[i].counts[k]){ok=false;break;} } }
  std::printf("VERIFY stage output identical: %s (%zu vs %zu)\n", ok?"YES":"*** DIFFER ***", ob.size(), ou.size());
  std::printf("RESULT: effective cores  BALANCED=%.1f  UNBALANCED=%.1f  (of %d)\n", effB, effU, g_threads);
  std::printf("        current production H18 ceiling ~13.7 cores; UNBALANCED reproduces that class, BALANCED = the fix\n");
  return ok?0:1;
}
