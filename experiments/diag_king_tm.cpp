// diag_king_tm.cpp -- ADVERSARIAL test of the "45-degree diagonal king TM has base ~2.04" claim.
//
// VERDICT (measured 2026-06, gympie): CLAIM FALSIFIED.  The correct anti-diagonal king TM
//   reproduces a(n)=A006770 (gate PASS through n=11, incl. a(11)=39299408) but its REAL peak-state
//   base is ~4.52 --
//   roughly the SQUARE of the column engine's 2.42, not the probe's 2.04.  Cause: king's (-1,-1)/
//   (1,1) corner move jumps TWO diagonals, so a correct TM must carry a TWO-diagonal boundary
//   (2W slots) where the column carries one column (W slots); doubling the carried boundary
//   squares the partition count and pushes the base from ~2.4 to ~2.4^2.  Side-by-side (mode 3):
//      n     col_peak  base     diag_peak  base
//      10       8160   2.43      1231054   4.52
//      11      20597   2.52      5558056   4.52      (diag/col ratio 270x, growing)
//   The probe's 2.04 came from phase03's BACK_DIA={-1,0}: it models only the consecutive diagonal
//   and OMITS the D-2 corner link, so it is not a valid king TM -- it undercounts state.  The
//   diagonal sweep is WORSE for king polyplets, not better; the original WIDTH no-go stands and is
//   reinforced by the state-count (which the careful follow-up was supposed to either rescue or
//   bury -- it buries it).  Do NOT reopen the diagonal-sweep idea for the king lattice.
//
// Builds a CORRECT anti-diagonal (d = x+y) transfer matrix for fixed king-move polyplets
// (A006770), with the FULL king-adjacency closure across the diagonal cut, and:
//   (1) a Sigma==a(n) correctness gate (the sweep sums every fixed polyplet exactly once,
//       stratified by transverse width W exactly as the column engine stratifies by height H),
//   (2) a forward reachable-state exploration that measures the REAL distinct-state growth base
//       of this TM (the thing the probe only proxied with a partition count).
//
// THE KING-DIAGONAL CLOSURE FACTS (the crux the probes got wrong):
//   A cell on anti-diagonal D has king neighbours on diagonals D-2, D-1, D, D+1, D+2.
//   Offsets vs diagonal-delta (ox+oy): (-1,-1)->-2 ; (-1,0),(0,-1)->-1 ; (1,-1),(-1,1)->0 ;
//   (1,0),(0,1)->+1 ; (1,1)->+2.  Consequences:
//   * A NEW cell on diagonal D connects backward to BOTH diagonal D-1 (edge moves (-1,0),(0,-1))
//     AND diagonal D-2 (the (-1,-1) corner move).  So the boundary MUST carry the last TWO
//     diagonals.  phase03's BACK_DIA={-1,0} (only the consecutive diagonal) is an INCORRECT king
//     TM -- it omits the D-2 corner link and so undercounts state (its ~2.04 is a phantom).
//   * Because (1,1)/(−1,−1) jump TWO diagonals, a king-polyplet can have an EMPTY intermediate
//     diagonal bridged by a corner.  So an empty diagonal is a NORMAL shift step, NOT a harvest;
//     a component seals only once it has no surviving cell in the two carried diagonals.  Carrying
//     exactly two diagonals is sufficient: king reach is +-2, so two consecutive empty diagonals
//     fully sever the past.
//
// Transverse coordinate x in [0,W).  Within a diagonal, cells at x and x+1 are king-adjacent
// (offset (1,-1)) -- so a diagonal is contiguous-in-x just as a column is contiguous-in-y; the
// analogy to the column engine is exact under x<->y, D<->col.
//
// Build: g++ -std=c++20 -O3 -o build/diag_king_tm experiments/diag_king_tm.cpp
// Run  : build/diag_king_tm N [mode]   (mode 0=both 1=gate 2=growth; gympie, N<=12 minutes)
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <vector>
#include <unordered_map>
#include <algorithm>
#include <string>
using namespace std;

static const long long AREF[] = {1,1,4,20,110,638,3832,23592,147941,940982,6053180,39299408,257105146,1692931066};
static const int AREF_MAX = 13;

static int N;
static long long aOut[40];
static size_t gatePeakStates=0;   // real TM memory high-water (max live distinct sigs over sweep)

static inline int uf_find(int* p,int x){ while(p[x]!=x){p[x]=p[p[x]];x=p[x];} return x; }
static inline void uf_union(int* p,int a,int b){ a=uf_find(p,a); b=uf_find(p,b); if(a!=b)p[a]=b; }

static void canonicalizeSigC(unsigned char* b,int H){
    unsigned char map_[256]={0}; unsigned char nx=1;
    for(int i=0;i<H;i++){ unsigned char v=b[i]; if(v){ if(!map_[v])map_[v]=nx++; b[i]=map_[v]; } }
}
// canonicalize 2W labels (relabel by first occurrence over P then C)
static void canon2(unsigned char* b,int W){
    unsigned char map_[256]={0}; unsigned char nx=1;
    for(int i=0;i<2*W;i++){ unsigned char v=b[i]; if(v){ if(!map_[v])map_[v]=nx++; b[i]=map_[v]; } }
}

// Sig layout (length 2W+2): b[0..W-1]=P (diagonal d-1), b[W..2W-1]=C (diagonal d),
//   b[2W]=touched x=0, b[2W+1]=touched x=W-1.   label 0 = empty.
//
// Step: add diagonal d+1 with occupancy mask m over W slots (m may be 0 = empty diagonal).
// New boundary becomes (P_new=old C, C_new=new diagonal).  A new cell at slot x is king-adjacent
// to already-placed cells:  new-diag x-1,x+1 ; old C x-1,x ; old P x-1.
// Returns:
//   2 = HARVEST: the whole partial animal sealed into a single finished component this step
//                (its last cell just left the boundary, boundary now empty), AND it touched both
//                transverse ends -> a complete fixed polyplet; *harvestComp/touch reported via out
//                flag (we signal by returning 2; caller adds cnt).  out is the (empty) new sig.
//   1 = ALIVE  : valid continuation; canonical new sig in out.
//   0 = DEAD   : a component got stranded while others survive (=> would be a disconnected piece).
static int stepDiag(const unsigned char* old,int W,unsigned m,unsigned char* out,
                    bool* harvestOK){
    const int NEWB=2*W;            // new diagonal slots
    const int LBL=3*W;             // label anchors for old components
    int p[3*32+260];
    int tot=3*W+260;
    for(int i=0;i<tot;i++) p[i]=i;
    for(int x=0;x<W;x++){ unsigned char L=old[x];   if(L) uf_union(p,x,   LBL+L); }   // P->anchor
    for(int x=0;x<W;x++){ unsigned char L=old[W+x]; if(L) uf_union(p,W+x, LBL+L); }   // C->anchor
    for(int x=0;x<W;x++){
        if(!((m>>x)&1u)) continue;
        int nx=NEWB+x;
        if(x+1<W && ((m>>(x+1))&1u)) uf_union(p,nx,NEWB+x+1);     // within new diagonal
        if(x-1>=0 && old[W+x-1]) uf_union(p,nx, W+x-1);           // to C (d): (-1,0)
        if(           old[W+x ]) uf_union(p,nx, W+x  );           // to C (d): (0,-1)
        if(x-1>=0 && old[x-1])   uf_union(p,nx, x-1);             // to P (d-1): (-1,-1)
    }
    // Surviving roots: cells that remain in the new boundary = old C (becomes P_new) + new diagonal.
    char surv[3*32+260]={0};
    for(int x=0;x<W;x++) if(old[W+x])   surv[uf_find(p,W+x)]=1;
    for(int x=0;x<W;x++) if((m>>x)&1u)  surv[uf_find(p,NEWB+x)]=1;

    // Total component count present anywhere on (old P, old C, new diagonal).
    char rootSeen[3*32+260]={0};
    int comps=0;
    auto noteRoot=[&](int r){ if(!rootSeen[r]){rootSeen[r]=1; comps++; } };
    for(int x=0;x<W;x++) if(old[x])     noteRoot(uf_find(p,x));
    for(int x=0;x<W;x++) if(old[W+x])   noteRoot(uf_find(p,W+x));
    for(int x=0;x<W;x++) if((m>>x)&1u)  noteRoot(uf_find(p,NEWB+x));

    // Count sealed components (no surviving cell).
    int sealed=0, sealedRoot=-1;
    // re-scan distinct roots
    char seen2[3*32+260]={0};
    for(int x=0;x<W;x++){
        if(!old[x]) continue; int r=uf_find(p,x);
        if(seen2[r]) continue; seen2[r]=1;
        if(!surv[r]){ sealed++; sealedRoot=r; }
    }
    for(int x=0;x<W;x++){
        if(!old[W+x]) continue; int r=uf_find(p,W+x);
        if(seen2[r]) continue; seen2[r]=1;
        if(!surv[r]){ sealed++; sealedRoot=r; }
    }
    // new-diagonal roots always survive, skip.

    *harvestOK=false;
    // HARVEST: if after this step NOTHING survives (boundary empty) and there was exactly ONE
    // component total -> the animal finished as a single piece.  Caller checks touch flags.
    bool nothingSurvives = true;
    for(int x=0;x<W;x++) if(old[W+x]){ nothingSurvives=false; break; }
    if(nothingSurvives) for(int x=0;x<W;x++) if((m>>x)&1u){ nothingSurvives=false; break; }
    if(nothingSurvives){
        // boundary becomes empty.  Valid harvest iff exactly one component existed.
        if(comps==1){
            // touch flags including old P/C (the just-sealed cells)
            bool tl = old[2*W] || old[0] || old[W+0] || (m&1u);
            bool tr = old[2*W+1] || old[W-1] || old[2*W-1] || ((m>>(W-1))&1u);
            *harvestOK = (tl && tr);
            memset(out,0,2*W+2);
            return 2;
        }
        // boundary empty but >1 component => disconnected pieces => invalid
        return 0;
    }
    // Something survives.  If a component sealed while others survive -> stranded disconnected -> Dead.
    if(sealed>0) return 0;

    // ALIVE: build new boundary P_new=old C, C_new=new diagonal.
    memset(out,0,2*W+2);
    unsigned char lab[3*32+260]; memset(lab,0,sizeof(lab)); unsigned char nl=1;
    for(int x=0;x<W;x++) if(old[W+x]){ int r=uf_find(p,W+x); if(!lab[r])lab[r]=nl++; out[x]=lab[r]; }
    for(int x=0;x<W;x++) if((m>>x)&1u){ int r=uf_find(p,NEWB+x); if(!lab[r])lab[r]=nl++; out[W+x]=lab[r]; }
    canon2(out,W);
    out[2*W]   = (old[2*W]   || old[W+0]   || (m&1u))          ? 1 : 0;
    out[2*W+1] = (old[2*W+1] || old[2*W-1] || ((m>>(W-1))&1u)) ? 1 : 0;
    return 1;
}

// Viable-mask filter for the diagonal step: a P-only component (present in old P, absent from old
// C) leaves the boundary this step and can ONLY be saved by a new cell that king-touches it, i.e.
// a new cell at slot x with x-1 in that component (the (-1,-1) link).  If any required P-only
// component is uncoverable by the remaining slots, prune.  C-components always survive (C->P_new),
// so they impose no coverage requirement.  We also always allow mask 0 (empty diagonal) only when
// there are NO P-only comps to cover (else it would strand them).  Mirrors forEachViableMask.
// NOTE: a per-label "viable mask" generator was tried to skip stranding masks faster, but the
// king-diagonal stranding test is genuinely CONNECTIVITY-based (a P-only component can merge with C
// through the new diagonal's internal chaining), not a simple per-label coverage check -- the
// simplified generator UNDERCOUNTED (gate mismatched).  So stepDiag remains the sole authority:
// the gate enumerates all 2^W masks and lets stepDiag classify Dead/Alive/Harvest.  This is the
// proven-correct path (Sigma==a(n) through n=11); the 2^W cost is acceptable for this probe.

// ---- GATE: sum fixed polyplets in transverse band x in [0,W) touching x=0 and x=W-1 ----
static void gateWidth(int W){
    typedef string Key;
    unordered_map<Key,vector<long long>> db, nxt;
    {
        string seed(2*W+2,0);
        db[seed]=vector<long long>(N+1,0); db[seed][0]=1;
    }
    // Sweep diagonals until db empty.  An n-cell animal spans at most ~2n diagonals (gaps), so cap
    // generously; db empties on its own once budget exhausted.
    int maxDiag=2*N+4;
    for(int d=0; d<=maxDiag && !db.empty(); ++d){
        if(db.size()>gatePeakStates) gatePeakStates=db.size();   // real peak-state high-water
        nxt.clear();
        for(auto& kv: db){
            const unsigned char* b=(const unsigned char*)kv.first.data();
            const vector<long long>& cnt=kv.second;
            int ms=-1; for(int n=0;n<=N;n++) if(cnt[n]){ms=n;break;}
            if(ms<0) continue;
            int budget=N-ms;
            unsigned lim=1u<<W;
            for(unsigned m=0;m<lim;++m){            // m=0 allowed (empty diagonal / seal)
                int pc=__builtin_popcount(m);
                if(pc>budget) continue;
                unsigned char out[2*32+2]; bool harv=false;
                int r=stepDiag(b,W,m,out,&harv);    // stepDiag is the authority (Dead/Alive/Harvest)
                if(r==0) continue;
                if(r==2){ if(harv) for(int n=1;n<=N;n++) aOut[n]+=cnt[n]; continue; }
                string k((char*)out,2*W+2);
                auto& v=nxt[k]; if(v.empty()) v.assign(N+1,0);
                for(int n=0;n+pc<=N;n++) if(cnt[n]) v[n+pc]+=cnt[n];
            }
        }
        db.swap(nxt);
    }
}

// ---- STATE-GROWTH: forward reachable distinct sigs, window W=N, by min-cells ----
static void stateGrowth(int W){
    typedef string Key;
    unordered_map<Key,int> best;
    vector<vector<Key>> bucket(N+1);
    string seed(2*W+2,0);
    best[seed]=0; bucket[0].push_back(seed);
    long long maxLive=0;
    for(int cc=0; cc<=N; ++cc){
        long long live=0;
        for(auto& cur: bucket[cc]){
            auto it=best.find(cur); if(it==best.end()||it->second!=cc) continue;
            live++;
            const unsigned char* b=(const unsigned char*)cur.data();
            int rem=N-cc;
            unsigned lim=1u<<W;
            for(unsigned m=1;m<lim;++m){           // growth: only progress-making (nonzero) masks
                int pc=__builtin_popcount(m); if(pc>rem) continue;
                unsigned char out[2*32+2]; bool harv=false;
                int r=stepDiag(b,W,m,out,&harv);
                if(r!=1) continue;
                string k((char*)out,2*W+2);
                int nc=cc+pc;
                auto f=best.find(k);
                if(f==best.end()||f->second>nc){ best[k]=nc; if(nc<=N) bucket[nc].push_back(k); }
            }
        }
        if(live>maxLive) maxLive=live;
    }
    vector<long long> cnt(N+1,0);
    for(auto& kv: best) if(kv.second>=1&&kv.second<=N) cnt[kv.second]++;
    printf("# DIAGONAL (correct 2-diagonal king closure) distinct frontier states, min-cells==k:\n");
    long long cum=0;
    for(int k=1;k<=N;k++){
        cum+=cnt[k];
        double rnew = k>1&&cnt[k-1]?(double)cnt[k]/cnt[k-1]:0;
        double rcum = k>1&&cum-cnt[k]?(double)cum/(cum-cnt[k]):0;
        printf("  k=%2d  new=%lld  cum=%lld  new_ratio=%.3f cum_ratio=%.3f\n",k,cnt[k],cum,rnew,rcum);
    }
}

// ===========================================================================
//  COLUMN reference engine (mirror of cpp/tma transition_square8.h), SAME methodology, so its
//  peak-state base is measured identically to the diagonal one (no per-engine metric drift).
//  Boundary = one column of H rows + 2 touch flags; king step uses old rows r-1,r,r+1 (full column
//  present -> no carry).  Sum over height H of completed animals == a(n).
// ===========================================================================
static size_t colPeakStates=0;
static long long colOut[40];
static int stepCol(const unsigned char* old,int H,unsigned mask,unsigned char* out){
    int p[2*32]; for(int i=0;i<2*H;i++)p[i]=i;          // new rows 0..H-1 ; old labels H+L
    for(int r=0;r<H;r++){
        if(!((mask>>r)&1u)) continue;
        if(r+1<H && ((mask>>(r+1))&1u)) uf_union(p,r,r+1);
        for(int rr=r-1;rr<=r+1;rr++){ if(rr<0||rr>=H)continue; unsigned char L=old[rr]; if(L) uf_union(p,r,H+L);}
    }
    char rootHasNew[2*32]={0};
    for(int r=0;r<H;r++) if((mask>>r)&1u) rootHasNew[uf_find(p,r)]=1;
    for(int i=0;i<H;i++){ unsigned char L=old[i]; if(L&&!rootHasNew[uf_find(p,H+L)]) return 0; }
    memset(out,0,H+2);
    for(int r=0;r<H;r++) if((mask>>r)&1u) out[r]=(unsigned char)(uf_find(p,r)+1);
    canonicalizeSigC(out,H);
    out[H]=(old[H]||(mask&1u))?1:0;
    out[H+1]=(old[H+1]||((mask>>(H-1))&1u))?1:0;
    return 1;
}
static void colHeight(int H){
    typedef string Key;
    unordered_map<Key,vector<long long>> db,nxt;
    string seed(H+2,0); db[seed]=vector<long long>(N+1,0); db[seed][0]=1;
    for(int col=0; col<=N && !db.empty(); ++col){
        if(db.size()>colPeakStates) colPeakStates=db.size();
        nxt.clear();
        for(auto& kv:db){
            const unsigned char* b=(const unsigned char*)kv.first.data();
            const vector<long long>& cnt=kv.second;
            int ms=-1; for(int n=0;n<=N;n++) if(cnt[n]){ms=n;break;} if(ms<0)continue;
            int comps=0; for(int j=0;j<H;j++) if(b[j]>comps)comps=b[j];
            if(comps==1 && b[H] && b[H+1]) for(int n=1;n<=N;n++) colOut[n]+=cnt[n];
            int budget=N-ms; unsigned lim=1u<<H;
            for(unsigned m=1;m<lim;++m){
                int pc=__builtin_popcount(m); if(pc>budget)continue;
                unsigned char out[32]; if(!stepCol(b,H,m,out))continue;
                string k((char*)out,H+2); auto& v=nxt[k]; if(v.empty())v.assign(N+1,0);
                for(int n=0;n+pc<=N;n++) if(cnt[n]) v[n+pc]+=cnt[n];
            }
        }
        db.swap(nxt);
    }
}

int main(int argc,char**argv){
    N=argc>1?atoi(argv[1]):11;
    int mode=argc>2?atoi(argv[2]):0;
    printf("N=%d  (correct anti-diagonal king TM: 2-diagonal carried boundary)\n",N);
    if(mode==0||mode==1){
        memset(aOut,0,sizeof(aOut));
        for(int W=1;W<=N;W++) gateWidth(W);
        printf("\n# GATE: Sigma over transverse width of diagonal-swept fixed polyplets vs a(n)\n");
        printf("%3s %16s %16s %s\n","n","diag_sum","a(n)","status");
        bool ok=true;
        for(int n=1;n<=N;n++){
            long long ref = n<=AREF_MAX? AREF[n] : -1;
            bool match=(ref>=0 && aOut[n]==ref);
            if(ref>=0 && !match) ok=false;
            printf("%3d %16lld %16lld %s\n",n,aOut[n],ref,ref<0?"(no ref)":(match?"OK":"*** MISMATCH ***"));
        }
        printf("# GATE %s\n", ok?"PASSED (Sigma==a(n))":"FAILED");
    }
    if(mode==0||mode==2){ printf("\n"); stateGrowth(N); }
    if(mode==3){
        // REAL peak-state base: run each engine's full gate sweep at budget n=1..N and record the
        // memory high-water (max live distinct sigs over the sweep).  Fit base = peak(n)/peak(n-1).
        printf("\n# REAL peak-state high-water per budget n (the engine's actual memory cost).\n");
        printf("%3s | %12s %7s | %12s %7s | %s\n","n","col_peak","ratio","diag_peak","ratio","diag/col");
        int saveN=N;
        size_t pcPrev=0,pdPrev=0;
        for(int n=1;n<=saveN;n++){
            N=n;
            colPeakStates=0; memset(colOut,0,sizeof(colOut));
            for(int H=1;H<=n;H++) colHeight(H);
            gatePeakStates=0; memset(aOut,0,sizeof(aOut));
            for(int W=1;W<=n;W++) gateWidth(W);
            double rc=pcPrev?(double)colPeakStates/pcPrev:0;
            double rd=pdPrev?(double)gatePeakStates/pdPrev:0;
            bool cok = (n<=AREF_MAX) ? (colOut[n]==AREF[n]) : true;
            bool dok = (n<=AREF_MAX) ? (aOut[n]==AREF[n]) : true;
            printf("%3d | %12zu %7.3f | %12zu %7.3f | %6.3f  %s\n",n,colPeakStates,rc,gatePeakStates,rd,
                   colPeakStates?(double)gatePeakStates/colPeakStates:0,
                   (cok&&dok)?"[both==a(n)]":"[*** COUNT MISMATCH ***]");
            pcPrev=colPeakStates; pdPrev=gatePeakStates;
        }
        N=saveN;
    }
    return 0;
}
