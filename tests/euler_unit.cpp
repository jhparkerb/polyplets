// Isolated unit test for cpp/tma/euler.h (#28 hole accounting), BEFORE wiring
// it into the engine. Two things are proven, against an independent flood-fill
// oracle that shares no logic with the bit-quad helper:
//
//   (I)  whole-image identity: 1 - E_8fg == holes_4bg  and
//        comps_4fg - E_4fg == holes_8bg, where E_* comes from euler.h's
//        bit-quad windows and holes_*/comps_* come from flood fill.
//   (II) incremental/border identity: sweeping columns left to right with
//        closedEulerDelta4() reproduces 4*E of the closed partial image at
//        EVERY prefix -- this is what the transfer matrix relies on.
//
// Build: c++ -std=c++20 -O2 -Wall tests/euler_unit.cpp -o build/euler_unit
//
// A grid is rows*cols of 0/1; bit r of column c's mask = cell (r,c). Row 0 is
// the top. Matches the engine's mask convention (mask>>r & 1 == row r).

#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <vector>

#include "../cpp/tma/euler.h"

using Grid = std::vector<std::vector<int>>;  // [row][col], 0/1

static int rows(const Grid& g) { return (int)g.size(); }
static int cols(const Grid& g) { return g.empty() ? 0 : (int)g[0].size(); }

// ---- independent oracle: flood fill, no bit-quads ----------------------------

// Connected foreground components under 4- or 8-adjacency.
static int floodComps(const Grid& g, bool conn8) {
  const int R = rows(g), C = cols(g);
  std::vector<std::vector<int>> seen(R, std::vector<int>(C, 0));
  static const int d4r[] = {-1, 1, 0, 0}, d4c[] = {0, 0, -1, 1};
  static const int d8r[] = {-1, -1, -1, 0, 0, 1, 1, 1},
                   d8c[] = {-1, 0, 1, -1, 1, -1, 0, 1};
  const int* dr = conn8 ? d8r : d4r;
  const int* dc = conn8 ? d8c : d4c;
  const int nd = conn8 ? 8 : 4;
  int comps = 0;
  std::vector<std::pair<int, int>> stk;
  for (int r = 0; r < R; ++r)
    for (int c = 0; c < C; ++c) {
      if (!g[r][c] || seen[r][c]) continue;
      ++comps;
      stk.push_back({r, c});
      seen[r][c] = 1;
      while (!stk.empty()) {
        const auto pr = stk.back();
        const int y = pr.first, x = pr.second;
        stk.pop_back();
        for (int k = 0; k < nd; ++k) {
          const int ny = y + dr[k], nx = x + dc[k];
          if (ny < 0 || ny >= R || nx < 0 || nx >= C) continue;
          if (g[ny][nx] && !seen[ny][nx]) {
            seen[ny][nx] = 1;
            stk.push_back({ny, nx});
          }
        }
      }
    }
  return comps;
}

// Bounded (enclosed) empty regions under background connectivity bgConn8.
// Pad by one ring, flood the exterior from the corner; any unreached empty cell
// inside the original grid belongs to a hole. Count hole components.
static int floodHoles(const Grid& g, bool bgConn8) {
  const int R = rows(g), C = cols(g);
  const int PR = R + 2, PC = C + 2;
  // pad: 1 where occupied (within original), 0 elsewhere
  std::vector<std::vector<int>> p(PR, std::vector<int>(PC, 0));
  for (int r = 0; r < R; ++r)
    for (int c = 0; c < C; ++c) p[r + 1][c + 1] = g[r][c];
  static const int d4r[] = {-1, 1, 0, 0}, d4c[] = {0, 0, -1, 1};
  static const int d8r[] = {-1, -1, -1, 0, 0, 1, 1, 1},
                   d8c[] = {-1, 0, 1, -1, 1, -1, 0, 1};
  const int* dr = bgConn8 ? d8r : d4r;
  const int* dc = bgConn8 ? d8c : d4c;
  const int nd = bgConn8 ? 8 : 4;
  std::vector<std::vector<int>> ext(PR, std::vector<int>(PC, 0));
  std::vector<std::pair<int, int>> stk{{0, 0}};
  ext[0][0] = 1;
  while (!stk.empty()) {  // flood exterior background
    const auto pr = stk.back();
    const int y = pr.first, x = pr.second;
    stk.pop_back();
    for (int k = 0; k < nd; ++k) {
      const int ny = y + dr[k], nx = x + dc[k];
      if (ny < 0 || ny >= PR || nx < 0 || nx >= PC) continue;
      if (!p[ny][nx] && !ext[ny][nx]) {
        ext[ny][nx] = 1;
        stk.push_back({ny, nx});
      }
    }
  }
  // count connected components of empty-and-not-exterior cells
  std::vector<std::vector<int>> seen(PR, std::vector<int>(PC, 0));
  int holes = 0;
  for (int r = 0; r < PR; ++r)
    for (int c = 0; c < PC; ++c) {
      if (p[r][c] || ext[r][c] || seen[r][c]) continue;
      ++holes;
      stk.push_back({r, c});
      seen[r][c] = 1;
      while (!stk.empty()) {
        const auto pr = stk.back();
        const int y = pr.first, x = pr.second;
        stk.pop_back();
        for (int k = 0; k < nd; ++k) {
          const int ny = y + dr[k], nx = x + dc[k];
          if (ny < 0 || ny >= PR || nx < 0 || nx >= PC) continue;
          if (!p[ny][nx] && !ext[ny][nx] && !seen[ny][nx]) {
            seen[ny][nx] = 1;
            stk.push_back({ny, nx});
          }
        }
      }
    }
  return holes;
}

// ---- bit-quad whole-image E (independent of euler.h's column decomposition) --
// Brute window scan: top-left at every (r,c) in [-1,R-1]x[-1,C-1].
static int eulerBrute4(const Grid& g, Conn conn) {
  const int R = rows(g), C = cols(g);
  auto at = [&](int r, int c) -> int {
    return (r >= 0 && r < R && c >= 0 && c < C) ? g[r][c] : 0;
  };
  int s = 0;
  for (int r = -1; r < R; ++r)
    for (int c = -1; c < C; ++c)
      s += quadWindow(at(r, c), at(r, c + 1), at(r + 1, c), at(r + 1, c + 1),
                      conn);
  return s;
}

// column c's row bitmask
static std::uint32_t colMask(const Grid& g, int c) {
  std::uint32_t m = 0;
  for (int r = 0; r < rows(g); ++r)
    if (g[r][c]) m |= 1u << r;
  return m;
}

// ---- the two checks ----------------------------------------------------------

static int failures = 0;
static void check(bool ok, const char* what) {
  if (!ok) {
    std::printf("  FAIL: %s\n", what);
    ++failures;
  }
}

// Run all identities on one grid. `name` non-null prints a labelled report.
static void exercise(const Grid& g, const char* name) {
  const int H = rows(g), W = cols(g);
  const int e8 = eulerBrute4(g, Conn::FG8);  // 4*E_8fg
  const int e4 = eulerBrute4(g, Conn::FG4);  // 4*E_4fg
  const int comps8 = floodComps(g, true), comps4 = floodComps(g, false);
  const int holes4bg = floodHoles(g, false), holes8bg = floodHoles(g, true);

  // (I) whole-image Euler identity vs flood oracle
  check(comps8 * 4 - e8 == holes4bg * 4, "holes_4bg == comps8 - E_8fg");
  check(comps4 * 4 - e4 == holes8bg * 4, "holes_8bg == comps4 - E_4fg");

  // (II) incremental/border identity: closedEulerDelta4 reproduces 4*E of the
  // closed partial image at every prefix, for both conventions.
  for (Conn conn : {Conn::FG8, Conn::FG4}) {
    int A = 0;                       // 4*E of empty image = 0
    std::uint32_t prev = 0;          // left exterior
    for (int c = 0; c < W; ++c) {
      const std::uint32_t cur = colMask(g, c);
      A += closedEulerDelta4(prev, cur, H, conn);
      // closed partial image = columns 0..c
      Grid part(H, std::vector<int>(c + 1, 0));
      for (int r = 0; r < H; ++r)
        for (int cc = 0; cc <= c; ++cc) part[r][cc] = g[r][cc];
      check(A == eulerBrute4(part, conn), "incremental A == 4*E(prefix)");
      prev = cur;
    }
    check(A == eulerBrute4(g, conn), "incremental A == 4*E(whole)");
  }

  if (name) {
    std::printf("  %-14s comps8=%d holes4bg=%d | comps4=%d holes8bg=%d "
                "| E8=%d E4=%d\n",
                name, comps8, holes4bg, comps4, holes8bg, e8 / 4, e4 / 4);
  }
}

// Build a grid from ASCII art ('#'/'X' = cell). Rows must be equal length.
static Grid art(std::initializer_list<const char*> lines) {
  Grid g;
  for (const char* line : lines) {
    std::vector<int> row;
    for (const char* p = line; *p; ++p) row.push_back(*p == '#' || *p == 'X');
    g.push_back(row);
  }
  return g;
}

// Assert a named shape's hand-checked hole counts (catches an oracle bug too).
static void expectHoles(const Grid& g, const char* name, int h4bg, int h8bg) {
  exercise(g, name);
  check(floodHoles(g, false) == h4bg, "hand-checked holes_4bg");
  check(floodHoles(g, true) == h8bg, "hand-checked holes_8bg");
}

int main() {
  std::printf("named shapes (with hand-checked hole counts):\n");
  expectHoles(art({"#"}), "single", 0, 0);
  expectHoles(art({"##"}), "domino", 0, 0);
  expectHoles(art({"##", "##"}), "square2", 0, 0);
  expectHoles(art({".#.", "#.#", ".#."}), "diamond(n4)", 1, 0);
  expectHoles(art({"###", "#.#", "###"}), "ring3x3(n8)", 1, 1);
  expectHoles(art({"####", "#..#", "#..#", "####"}), "ring4x4", 1, 1);
  // two separate 4-bg holes (one wide cavity split by a diagonal pinch -> two
  // 4-connected holes, but one 8-connected hole):
  expectHoles(art({"####", "#.##", "##.#", "####"}), "pinch2holes", 2, 1);

  std::printf("fuzz (all identities on random images):\n");
  // deterministic LCG -- no Date/random needed, reproducible.
  std::uint64_t s = 0x9e3779b97f4a7c15ull;
  auto rnd = [&]() { s ^= s << 13; s ^= s >> 7; s ^= s << 17; return s; };
  int tested = 0;
  for (int it = 0; it < 200000; ++it) {
    const int H = 1 + (int)(rnd() % 6), W = 1 + (int)(rnd() % 6);
    Grid g(H, std::vector<int>(W, 0));
    int cells = 0;
    for (int r = 0; r < H; ++r)
      for (int c = 0; c < W; ++c) {
        g[r][c] = (int)(rnd() & 1);
        cells += g[r][c];
      }
    if (!cells) continue;
    exercise(g, nullptr);
    ++tested;
  }
  std::printf("  fuzzed %d non-empty images\n", tested);

  if (failures == 0)
    std::printf("\nALL PASS\n");
  else
    std::printf("\n%d FAILURES\n", failures);
  return failures ? 1 : 0;
}
