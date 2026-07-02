// show_tm.cpp — dump the actual king-graph (polyplet) column transfer matrix for
// a small height H, using the PRODUCTION kernel (forEachViableMask +
// stepColumnSquare8). Build:
//   c++ -std=c++20 -O2 -Icpp/tma experiments/show_tm.cpp -o build/show_tm
// Run: ./build/show_tm 2   (or 3)
//
// State = boundary signature: b[0..H-1] row component-labels (0=empty, else
// restricted-growth component id), b[H]=touched-top flag, b[H+1]=touched-bottom.
// A column step adds a cell in each row of `mask`; the transfer-matrix entry
// M[dst][src] gets one x^(cells added) term per mask taking src -> dst (Alive).
#include "signature.h"
#include "transition_square8.h"
#include <cstdio>
#include <map>
#include <queue>
#include <string>
#include <vector>
#include <array>

static std::string label(const Sig& s, int H) {
  std::string r = "[";
  for (int i = 0; i < H; ++i) { r += char('0' + s.b[i]); if (i < H-1) r += ' '; }
  r += "] t="; r += char('0' + s.b[H]); r += " b="; r += char('0' + s.b[H+1]);
  return r;
}
static std::array<unsigned char, SIGMAX> key(const Sig& s) {
  std::array<unsigned char, SIGMAX> k{}; for (int i=0;i<SIGMAX;i++) k[i]=s.b[i]; return k;
}

int main(int argc, char** argv) {
  int H = argc > 1 ? std::atoi(argv[1]) : 2;
  Sig seed; std::memset(seed.b, 0, SIGMAX);           // empty boundary
  std::map<std::array<unsigned char,SIGMAX>, int> id;
  std::vector<Sig> states;
  auto intern = [&](const Sig& s){ auto k=key(s); auto it=id.find(k);
    if (it!=id.end()) return it->second; int n=states.size(); id[k]=n; states.push_back(s); return n; };
  // BFS reachable states from the seed.  budget huge => no reach pruning (full matrix).
  std::queue<int> q; q.push(intern(seed));
  // transitions[src] : map dst -> (count of cells k -> multiplicity)
  std::vector<std::map<int,std::map<int,int>>> trans;
  while (!q.empty()) {
    int si = q.front(); q.pop();
    if ((int)trans.size() <= si) trans.resize(si+1);
    Sig src = states[si];
    forEachViableMask(src, H, /*budget=*/1000, [&](unsigned mask){
      Sig dst; if (stepColumnSquare8(src, H, mask, dst) != Outcome::Alive) return;
      int di = intern(dst);
      if ((int)trans.size() <= di) trans.resize(di+1);
      trans[si][di][__builtin_popcount(mask)]++;
      if (di >= (int)trans.size() || trans[di].empty()) {} // ensure visited
    });
  }
  // Re-run BFS closure so every interned state gets its outgoing edges.
  for (int si = 0; si < (int)states.size(); ++si) {
    if (si < (int)trans.size() && !trans[si].empty()) continue;
    if ((int)trans.size() <= si) trans.resize(si+1);
    Sig src = states[si];
    forEachViableMask(src, H, 1000, [&](unsigned mask){
      Sig dst; if (stepColumnSquare8(src, H, mask, dst) != Outcome::Alive) return;
      int di = intern(dst); if ((int)trans.size()<=di) trans.resize(di+1);
      trans[si][di][__builtin_popcount(mask)]++;
    });
  }

  std::printf("Height H=%d king-graph (polyplet) column transfer matrix\n", H);
  std::printf("%d reachable boundary states:\n", (int)states.size());
  for (int i = 0; i < (int)states.size(); ++i) {
    int comps = 0; for (int j=0;j<H;j++) if (states[i].b[j]>comps) comps=states[i].b[j];
    bool acc = (comps==1 && states[i].b[H] && states[i].b[H+1]);
    std::printf("  s%-2d %s%s\n", i, label(states[i],H).c_str(), acc? "   <- ACCEPT (1 comp, touches top+bottom)":"");
  }
  std::printf("\nTransitions  src --(x^cells [xmult])--> dst   (x marks cells added this column):\n");
  for (int si = 0; si < (int)trans.size(); ++si) {
    for (auto& [di, byk] : trans[si]) {
      std::string w;
      for (auto& [k,m] : byk) { if(!w.empty()) w+=" + "; w += (m>1? std::to_string(m):"") + "x^" + std::to_string(k); }
      std::printf("  s%-2d --%-14s--> s%d\n", si, w.c_str(), di);
    }
  }
  std::printf("\n(s0 = empty seed. GF for T(n,H) = paths seed -> ACCEPT, x marks total cells.)\n");
  return 0;
}
