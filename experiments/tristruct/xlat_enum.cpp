// xlat_enum.cpp -- Proposer 4 (cross-lattice control), triangle-structure hunt.
//
// Independent fixed-animal enumerator by bounding-box height, written from the
// lattice definition ONLY. Deliberately does NOT read core/transition.h,
// cpp/strip_tm.cpp, or any other kernel in this repo (team-brief mandatory
// first task: an independent connectivity rule per proposer).
//
// Lattices:
//   king   : cells Z^2, u ~ v iff max(|dx|,|dy|) == 1   (8 neighbors)
//   square : cells Z^2, u ~ v iff |dx|+|dy| == 1        (4 neighbors)
//   tri    : polyiamonds in the (x,y,orientation-by-parity) coordinates:
//            (x,y) ~ (x+-1,y) always; (x,y) ~ (x,y+1) iff x+y+p odd,
//            where p in {0,1} is the run's parity offset. Fixed polyiamonds
//            are counted modulo translations with dx+dy even, so the total
//            is the sum over p = 0 and p = 1 (the lex-min cell's orientation
//            is translation-invariant).
//
// Method: Redelmeier untried-set enumeration of connected sets containing the
// root (0,0), restricted to the half-plane y > 0 or (y == 0 and x >= 0), so
// each translation class is counted exactly once (the lex-min cell in (y,x)
// order is normalized to the origin). All cells have y >= 0 and the root has
// y = 0, so bounding-box height = maxy + 1.
//
// Output: lines "n H count" for 1 <= n <= N, plus row sums "n SUM count".
//
// Usage: xlat_enum <king|square|tri> <N>

#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <vector>

static int N;                 // max cells
static int W;                 // grid width  = 2N+1  (x in [-N, N], offset +N)
static int Hrows;             // grid height = N+2
static std::vector<unsigned char> reached;
static std::vector<int> untried;   // shared stack of cell ids
static int ulen;
static long long cnt[64][64];      // cnt[n][height]
static int lattice;                // 0 king, 1 square, 2 tri
static int parityOff;              // tri only

static inline int cid(int x, int y) { return y * W + (x + N); }

// neighbors of (x,y) under the current lattice rule, within the allowed
// half-plane (y>0, or y==0 && x>=0), into out[]; returns count.
static inline int neighbors(int x, int y, int out[][2]) {
    int m = 0;
    if (lattice == 0) {                       // king: Chebyshev distance 1
        for (int dy = -1; dy <= 1; dy++)
            for (int dx = -1; dx <= 1; dx++) {
                if (!dx && !dy) continue;
                out[m][0] = x + dx; out[m][1] = y + dy; m++;
            }
    } else if (lattice == 1) {                // square: von Neumann
        const int d[4][2] = {{1,0},{-1,0},{0,1},{0,-1}};
        for (int i = 0; i < 4; i++) {
            out[m][0] = x + d[i][0]; out[m][1] = y + d[i][1]; m++;
        }
    } else {                                  // tri
        out[m][0] = x + 1; out[m][1] = y; m++;
        out[m][0] = x - 1; out[m][1] = y; m++;
        if ((x + y + parityOff) & 1) { out[m][0] = x; out[m][1] = y + 1; m++; }
        else                         { out[m][0] = x; out[m][1] = y - 1; m++; }
    }
    // filter to the allowed half-plane and the grid bounds
    int k = 0;
    for (int i = 0; i < m; i++) {
        int nx = out[i][0], ny = out[i][1];
        if (ny < 0 || (ny == 0 && nx < 0)) continue;
        if (nx < -N || nx > N || ny > N) continue;
        out[k][0] = nx; out[k][1] = ny; k++;
    }
    return k;
}

static void rec(int size, int ufirst, int maxy) {
    for (int i = ufirst; i < ulen; i++) {
        int c = untried[i];
        int y = c / W, x = c % W - N;
        int my = maxy > y ? maxy : y;
        cnt[size + 1][my + 1]++;
        if (size + 1 < N) {
            int save = ulen;
            int nb[8][2];
            int k = neighbors(x, y, nb);
            for (int j = 0; j < k; j++) {
                int id = cid(nb[j][0], nb[j][1]);
                if (!reached[id]) { reached[id] = 1; untried[ulen++] = id; }
            }
            rec(size + 1, i + 1, my);
            for (int j = save; j < ulen; j++) reached[untried[j]] = 0;
            ulen = save;
        }
    }
}

static void run(void) {
    reached.assign((size_t)W * Hrows, 0);
    untried.assign((size_t)W * Hrows, 0);
    ulen = 0;
    int root = cid(0, 0);
    reached[root] = 1;
    untried[ulen++] = root;
    rec(0, 0, 0);
}

int main(int argc, char **argv) {
    if (argc != 3) { fprintf(stderr, "usage: %s <king|square|tri> <N>\n", argv[0]); return 2; }
    if      (!strcmp(argv[1], "king"))   lattice = 0;
    else if (!strcmp(argv[1], "square")) lattice = 1;
    else if (!strcmp(argv[1], "tri"))    lattice = 2;
    else { fprintf(stderr, "unknown lattice %s\n", argv[1]); return 2; }
    N = atoi(argv[2]);
    if (N < 1 || N > 60) { fprintf(stderr, "N out of range\n"); return 2; }
    W = 2 * N + 1; Hrows = N + 2;
    memset(cnt, 0, sizeof cnt);
    if (lattice == 2) { for (parityOff = 0; parityOff <= 1; parityOff++) run(); }
    else run();
    for (int n = 1; n <= N; n++) {
        long long s = 0;
        for (int h = 1; h <= n; h++)
            if (cnt[n][h]) { printf("%d %d %lld\n", n, h, cnt[n][h]); s += cnt[n][h]; }
        printf("%d SUM %lld\n", n, s);
    }
    return 0;
}
