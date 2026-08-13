// p2_enum.cpp -- Proposer 2's independent king-animal (polyplet) enumerator.
//
// Written from the lattice definition only, per the team brief's mandatory
// first task. NOT derived from core/transition.h, cpp/strip_tm.cpp, or any
// existing kernel (none were read).
//
// Definition used: cells are points of Z^2; two cells are adjacent iff they
// differ by at most 1 in each coordinate and are distinct (8 king moves).
// An animal is a finite nonempty king-connected cell set; FIXED animals are
// counted up to translation only. T(n,H) = number of fixed n-cell animals
// whose occupied rows span exactly H consecutive-or-not values (bounding-box
// height: maxrow - minrow + 1).
//
// Counting scheme (independent normalization): every translation class has a
// unique representative whose minimum row is 0 and whose row-0 minimum column
// is 0. Enumerate connected supersets of the origin cell that avoid the
// forbidden cells {row 0, col < 0}, growing one cell at a time from a frontier
// ("untried") list; a popped frontier cell is either included (recurse) or
// permanently excluded for the remainder of that subtree. Each representative
// is generated exactly once. Every intermediate size is tallied, so one run
// yields the whole triangle for n <= N.
//
// Mode B (--sym) additionally tallies, per (n,H), animals invariant (as
// translation classes, i.e. about their own bounding-box midlines) under:
// top-bottom flip, left-right flip, 180-degree rotation, and the full Klein
// group {id, tb, lr, 180}. Used to validate the symmetric-fold enumerator.
//
// Build:  g++ -O2 -o build/p2_enum experiments/tristruct/p2_enum.cpp
// Run:    build/p2_enum N [--sym] > out
// Output: lines "n H count [tb lr r180 klein]".
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cstdint>

static int N;          // max cells
static int W;          // padded grid width = 2N+1; origin col index N
static uint8_t *seen;  // cell already on (or through) the frontier this path
static uint8_t *occ;   // cell currently in the animal
static unsigned long long *tally;   // [n*(N+1)+H]
static unsigned long long *symtal;  // [4][n*(N+1)+H] tb, lr, r180, klein
static int *occlist;   // occupied cells in inclusion order
static bool do_sym;

static const int DR[8] = {-1,-1,-1,0,0,1,1,1};
static const int DC[8] = {-1,0,1,-1,1,-1,0,1};

static inline bool cellok(int r, int c) {
    if (r < 0 || r >= N) return false;
    if (c < 1 || c > 2*N - 1) return false;
    if (r == 0 && c < N) return false;   // origin (0,N); row-0 left of it forbidden
    return true;
}

// symmetry tests on the current occupied set of size sz
static void symcheck(int sz, int maxrow) {
    int cmin = 1 << 30, cmax = -(1 << 30);
    for (int i = 0; i < sz; i++) {
        int c = occlist[i] % W;
        if (c < cmin) cmin = c;
        if (c > cmax) cmax = c;
    }
    bool tb = true, lr = true, rot = true;
    for (int i = 0; i < sz; i++) {
        int r = occlist[i] / W, c = occlist[i] % W;
        int rf = maxrow - r, cf = cmin + cmax - c;   // minrow == 0 always
        if (tb  && !occ[rf * W + c])  tb = false;
        if (lr  && !occ[r * W + cf])  lr = false;
        if (rot && !occ[rf * W + cf]) rot = false;
        if (!tb && !lr && !rot) return;
    }
    int idx = sz * (N + 1) + maxrow + 1;
    if (tb)        symtal[0 * (N + 1) * (N + 1) + idx]++;
    if (lr)        symtal[1 * (N + 1) * (N + 1) + idx]++;
    if (rot)       symtal[2 * (N + 1) * (N + 1) + idx]++;
    if (tb && lr)  symtal[3 * (N + 1) * (N + 1) + idx]++;   // then rot too
}

static void grow(const int *unt, int nunt, int size, int maxrow) {
    int *mine = new int[nunt + 8];
    memcpy(mine, unt, nunt * sizeof(int));
    int m = nunt;
    while (m > 0) {
        int cell = mine[--m];
        int r = cell / W, c = cell % W;
        int nm = maxrow > r ? maxrow : r;
        int ns = size + 1;
        tally[ns * (N + 1) + nm + 1]++;
        if (do_sym) {
            occ[cell] = 1; occlist[size] = cell;
            symcheck(ns, nm);
        }
        if (ns < N) {
            if (!do_sym) { occ[cell] = 1; occlist[size] = cell; }
            int added[8], na = 0;
            int *ext = new int[m + 8];
            memcpy(ext, mine, m * sizeof(int));
            int e = m;
            for (int k = 0; k < 8; k++) {
                int rr = r + DR[k], cc = c + DC[k];
                if (!cellok(rr, cc)) continue;
                int d = rr * W + cc;
                if (seen[d]) continue;
                seen[d] = 1; ext[e++] = d; added[na++] = d;
            }
            grow(ext, e, ns, nm);
            delete[] ext;
            for (int k = 0; k < na; k++) seen[added[k]] = 0;
            if (!do_sym) occ[cell] = 0;
        }
        if (do_sym) occ[cell] = 0;
        // cell stays 'seen': excluded for the rest of this subtree
    }
    delete[] mine;
}

int main(int argc, char **argv) {
    if (argc < 2) { fprintf(stderr, "usage: %s N [--sym]\n", argv[0]); return 2; }
    N = atoi(argv[1]);
    do_sym = (argc > 2 && !strcmp(argv[2], "--sym"));
    W = 2 * N + 1;
    int ncell = N * W;
    seen = new uint8_t[ncell](); occ = new uint8_t[ncell]();
    tally = new unsigned long long[(N + 1) * (N + 1)]();
    symtal = new unsigned long long[4 * (N + 1) * (N + 1)]();
    occlist = new int[N + 1];
    int origin = 0 * W + N;
    seen[origin] = 1;
    int unt0[1] = {origin};
    grow(unt0, 1, 0, 0);
    for (int n = 1; n <= N; n++)
        for (int H = 1; H <= n; H++) {
            unsigned long long t = tally[n * (N + 1) + H];
            if (do_sym)
                printf("%d %d %llu %llu %llu %llu %llu\n", n, H, t,
                       symtal[0*(N+1)*(N+1) + n*(N+1)+H],
                       symtal[1*(N+1)*(N+1) + n*(N+1)+H],
                       symtal[2*(N+1)*(N+1) + n*(N+1)+H],
                       symtal[3*(N+1)*(N+1) + n*(N+1)+H]);
            else
                printf("%d %d %llu\n", n, H, t);
        }
    return 0;
}
