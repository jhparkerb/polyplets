// p1_enum.cpp -- Proposer 1's independent fixed-polyplet enumerator.
//
// Written from the lattice definition ONLY (no existing kernel was read):
// a fixed polyplet (king-animal) of size n is a set of n cells of Z^2,
// connected under KING adjacency -- two cells are adjacent iff their
// coordinates differ by at most 1 in each axis and they are distinct
// (8 neighbours) -- counted up to translation. T(n,H) = number of such
// animals whose bounding-box height (max row - min row + 1) is exactly H.
//
// Algorithm: my own implementation of the classic untried-set backtracking
// (Redelmeier's scheme, reimplemented from the published idea, not from any
// repo code). Canonical translation: the first cell in row-major order
// (lowest row, then leftmost) is pinned at (0,0); every other cell has
// row > 0, or row == 0 and col > 0. Hence min row = 0 and H = maxrow+1.
//
// Output: lines "n H T(n,H)" for 1 <= n <= NMAX, plus row sums "n SUM a(n)".
// Usage: p1_enum NMAX
#include <cstdio>
#include <cstdint>
#include <cstdlib>
#include <vector>

static int NMAX;
static int W;              // board width = 2*NMAX - 1, cols shifted by NMAX-1
static std::vector<uint8_t> occupied; // cells currently in the animal
static std::vector<uint8_t> seen;     // cells ever added to the untried set on this path
static std::vector<std::vector<uint64_t>> count; // count[n][H]

// cell id for (row r >= 0, col c in [-(NMAX-1), NMAX-1]) is r*W + c + NMAX-1
static inline int cid(int r, int c) { return r * W + c + (NMAX - 1); }

static const int DR[8] = {-1, -1, -1, 0, 0, 1, 1, 1};
static const int DC[8] = {-1, 0, 1, -1, 1, -1, 0, 1};

// untried: stack of candidate cell ids; frontier grows by king neighbours.
static void rec(std::vector<int> &untried, int size, int maxrow) {
    // count the current animal (size >= 1 always when called)
    count[size][maxrow + 1]++;
    if (size == NMAX) return;
    // iterate over a private copy of the untried set, removing as we go
    std::vector<int> mine;
    mine.swap(untried);
    while (!mine.empty()) {
        int id = mine.back();
        mine.pop_back();
        int r = id / W, c = id % W - (NMAX - 1);
        occupied[id] = 1;
        // new untried cells: king neighbours of id, in the allowed half-plane,
        // never seen before on this path
        std::vector<int> added;       // marked for THIS choice only
        std::vector<int> next = mine; // cells still untried at this level
        for (int d = 0; d < 8; d++) {
            int nr = r + DR[d], nc = c + DC[d];
            if (nr < 0 || (nr == 0 && nc <= 0)) continue; // canonical half-plane
            if (nr >= NMAX || nc < -(NMAX - 1) || nc > NMAX - 1) continue;
            int nid = cid(nr, nc);
            if (seen[nid]) continue;
            seen[nid] = 1;
            added.push_back(nid);
            next.push_back(nid);
        }
        rec(next, size + 1, r > maxrow ? r : maxrow);
        occupied[id] = 0;
        // unmark this choice's frontier: in the sibling branch where `id` is
        // excluded, these cells may be reached again via other cells.
        // `id` itself stays excluded (popped from `mine`) -- that is what
        // makes each animal counted exactly once.
        for (int nid : added) seen[nid] = 0;
    }
}

int main(int argc, char **argv) {
    if (argc != 2) { fprintf(stderr, "usage: %s NMAX\n", argv[0]); return 2; }
    NMAX = atoi(argv[1]);
    if (NMAX < 1 || NMAX > 20) { fprintf(stderr, "NMAX out of range\n"); return 2; }
    W = 2 * NMAX - 1;
    occupied.assign((size_t)NMAX * W, 0);
    seen.assign((size_t)NMAX * W, 0);
    count.assign(NMAX + 1, std::vector<uint64_t>(NMAX + 1, 0));

    // root cell (0,0)
    int root = cid(0, 0);
    seen[root] = 1;
    occupied[root] = 1;
    std::vector<int> untried;
    untried.push_back(root);
    // rec expects untried to contain cells not yet placed; place root manually:
    // pop it as the sole level-0 choice by seeding the recursion directly.
    std::vector<int> init;
    for (int d = 0; d < 8; d++) {
        int nr = DR[d], nc = DC[d];
        if (nr < 0 || (nr == 0 && nc <= 0)) continue;
        int nid = cid(nr, nc);
        seen[nid] = 1;
        init.push_back(nid);
    }
    rec(init, 1, 0);

    for (int n = 1; n <= NMAX; n++) {
        unsigned long long s = 0;
        for (int H = 1; H <= n; H++) {
            printf("%d %d %llu\n", n, H, (unsigned long long)count[n][H]);
            s += count[n][H];
        }
        printf("%d SUM %llu\n", n, s);
    }
    return 0;
}
