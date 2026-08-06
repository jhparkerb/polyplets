// prec_guess.cpp -- P-recurrence and algebraic-relation exclusion, mod p.
//
// docs/middle-kingdom-plan.md Phase 2a. docs/proofs/convex-mirage.md banked
// "no P-recurrence of order <= 6, degree <= 5 on 38 terms" for HV-convex king
// animals by area and for the HV-convex polyomino control. This pushes the
// same question to order <= 20 / degree <= 20 on ~700 terms, which the
// Fraction-based guesser in experiments/convex_perimeter.py cannot reach.
//
// Why one box suffices. The ansatz boxes are nested: a solution of
//   sum_{i=0..J} p_i(n) a(n+i) = 0,  deg p_i <= D
// with J <= Jmax and D <= Dmax is also a solution of the (Jmax, Dmax) ansatz
// (pad the missing p_i with zero). So excluding the single maximal box
// excludes every (J, D) inside it -- no sweep needed.
//
// Why mod p is rigorous. The coefficient matrix has integer entries. If it has
// full column rank mod p then some maximal minor is nonzero mod p, hence
// nonzero over Q, hence the matrix has full column rank over Q and the only
// rational solution is the trivial one. Full rank mod p is therefore a proof
// of exclusion over Q (rank can only drop mod p, never rise). A rank *defect*
// mod p is only a candidate, and gets the holdout and second-prime treatment.
//
// Algebraic mode tests sum_{j=0..K} q_j(t) F(t)^j = 0 with deg q_j <= L, for
// F(t) = sum_{n>=1} a(n) t^n -- same linear algebra, different matrix. This is
// not implied by the D-finite exclusion in general (an algebraic function of
// degree K satisfies an ODE whose order/degree can exceed the box tested
// above), so it is worth running on its own.
//
// Usage:
//   build/prec_guess prec <terms_file> <J> <D> [prime_idx] [train_extra] [skip]
//   build/prec_guess alg  <terms_file> <K> <L> [prime_idx] [train_extra] [skip]
// skip drops that many leading rows, so a recurrence that only holds
// *eventually* (past an initial-condition anomaly) still shows up.
// terms_file: one term per line, either "value" or "n value"; blank lines and
// lines starting with '#' ignored. Terms are a(1), a(2), ... in order.
// stdout: a summary block, then VERDICT: EXCLUDED | CANDIDATE.
// stderr: obs.h start/done.
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <fstream>
#include <sstream>
#include <string>
#include <vector>

#include "argparse.h"
#include "obs.h"

namespace {

// Two unrelated primes. [0] is the repo's usual 2^61-1 (see
// experiments/anisotropic_dfinite.py); [1] is an independent check for
// candidates, since a rank defect mod one prime can be an accident of that
// prime.
const uint64_t kPrimes[2] = {(1ULL << 61) - 1, 1152921504606846883ULL};

uint64_t P;

inline uint64_t Mul(uint64_t a, uint64_t b) {
  return (uint64_t)((__uint128_t)a * b % P);
}
inline uint64_t Add(uint64_t a, uint64_t b) {
  uint64_t s = a + b;
  return s >= P ? s - P : s;
}
inline uint64_t Sub(uint64_t a, uint64_t b) { return a >= b ? a - b : a + P - b; }
uint64_t Pow(uint64_t a, uint64_t e) {
  uint64_t r = 1;
  while (e) {
    if (e & 1) r = Mul(r, a);
    a = Mul(a, a);
    e >>= 1;
  }
  return r;
}
inline uint64_t Inv(uint64_t a) { return Pow(a, P - 2); }

// Decimal string -> residue mod P, without bignum: Horner in base 10.
uint64_t ParseMod(const std::string& s) {
  uint64_t r = 0;
  for (char c : s) {
    if (c < '0' || c > '9') continue;
    r = Add(Mul(r, 10), (uint64_t)(c - '0'));
  }
  return r;
}

std::vector<std::string> ReadTerms(const char* path) {
  std::ifstream in(path);
  if (!in) {
    std::fprintf(stderr, "cannot open %s\n", path);
    std::exit(1);
  }
  std::vector<std::string> out;
  std::string line;
  while (std::getline(in, line)) {
    if (line.empty() || line[0] == '#') continue;
    std::istringstream is(line);
    std::string a, b;
    is >> a;
    if (is >> b)
      out.push_back(b);  // "n value"
    else
      out.push_back(a);  // "value"
  }
  return out;
}

// Row-reduce m (R x C) in place, returning the rank and, in piv, the pivot
// column of each rank-many pivot row (rows are permuted into pivot order).
size_t Rref(std::vector<std::vector<uint64_t>>& m, size_t C,
            std::vector<size_t>* piv) {
  size_t r = 0;
  piv->clear();
  for (size_t c = 0; c < C && r < m.size(); ++c) {
    size_t sel = m.size();
    for (size_t i = r; i < m.size(); ++i)
      if (m[i][c]) { sel = i; break; }
    if (sel == m.size()) continue;
    std::swap(m[r], m[sel]);
    const uint64_t iv = Inv(m[r][c]);
    for (size_t j = c; j < C; ++j) m[r][j] = Mul(m[r][j], iv);
    for (size_t i = 0; i < m.size(); ++i) {
      if (i == r || !m[i][c]) continue;
      const uint64_t f = m[i][c];
      for (size_t j = c; j < C; ++j) m[i][j] = Sub(m[i][j], Mul(f, m[r][j]));
    }
    piv->push_back(c);
    ++r;
  }
  return r;
}

// Nullspace basis of an already-RREF'd matrix with the given pivot columns.
std::vector<std::vector<uint64_t>> Nullspace(
    const std::vector<std::vector<uint64_t>>& m, size_t C,
    const std::vector<size_t>& piv) {
  std::vector<char> isPiv(C, 0);
  for (size_t c : piv) isPiv[c] = 1;
  std::vector<std::vector<uint64_t>> basis;
  for (size_t free_c = 0; free_c < C; ++free_c) {
    if (isPiv[free_c]) continue;
    std::vector<uint64_t> v(C, 0);
    v[free_c] = 1;
    for (size_t r = 0; r < piv.size(); ++r) v[piv[r]] = Sub(0, m[r][free_c]);
    basis.push_back(std::move(v));
  }
  return basis;
}

}  // namespace

int main(int argc, char** argv) {
  if (argc < 5) {
    std::fprintf(stderr,
                 "usage: %s prec|alg <terms_file> <J|K> <D|L> [prime_idx] "
                 "[train_extra] [skip]\n",
                 argv[0]);
    return 1;
  }
  const std::string mode = argv[1];
  const char* path = argv[2];
  const int A = (int)argparse::ArgInt(argv[3], "J|K", 0, 1 << 20);
  const int B = (int)argparse::ArgInt(argv[4], "D|L", 0, 1 << 20);
  const int pidx =
      argc > 5 ? (int)argparse::ArgInt(argv[5], "prime_idx", 0, 1) : 0;
  const size_t train_extra =
      argc > 6 ? (size_t)argparse::ArgInt(argv[6], "train_extra", 0, 1 << 30) : 4;
  const size_t skip =
      argc > 7 ? (size_t)argparse::ArgInt(argv[7], "skip", 0, 1 << 30) : 0;
  P = kPrimes[pidx];

  obs::Reporter rep("prec_guess", 0,
                    mode + " " + path + " " + std::to_string(A) + "," +
                        std::to_string(B) + " p" + std::to_string(pidx));

  const std::vector<std::string> raw = ReadTerms(path);
  const size_t M = raw.size();
  std::vector<uint64_t> a(M + 1, 0);  // a[1..M]
  for (size_t i = 0; i < M; ++i) a[i + 1] = ParseMod(raw[i]);

  const size_t C = (size_t)(A + 1) * (size_t)(B + 1);
  std::vector<std::vector<uint64_t>> rows;

  if (mode == "prec") {
    // Row n: entry for (i, d) is n^d * a(n+i), n = 1 .. M-A.
    for (size_t n = 1; n + (size_t)A <= M; ++n) {
      std::vector<uint64_t> row(C);
      uint64_t np = 1;
      const uint64_t nm = (uint64_t)n % P;
      std::vector<uint64_t> pw(B + 1);
      for (int d = 0; d <= B; ++d) { pw[d] = np; np = Mul(np, nm); }
      for (int i = 0; i <= A; ++i) {
        const uint64_t av = a[n + (size_t)i];
        for (int d = 0; d <= B; ++d) row[(size_t)i * (B + 1) + d] = Mul(pw[d], av);
      }
      rows.push_back(std::move(row));
    }
  } else if (mode == "alg") {
    // F(t) = sum_{n=1..M} a(n) t^n, truncated at t^M. pw[j] = F^j mod t^(M+1).
    std::vector<std::vector<uint64_t>> pw(A + 1, std::vector<uint64_t>(M + 1, 0));
    pw[0][0] = 1;
    for (int j = 1; j <= A; ++j)
      for (size_t u = 0; u <= M; ++u) {
        if (!pw[j - 1][u]) continue;
        const uint64_t c = pw[j - 1][u];
        for (size_t v = 1; u + v <= M; ++v)
          if (a[v]) pw[j][u + v] = Add(pw[j][u + v], Mul(c, a[v]));
      }
    // Row m: entry for (j, l) is [t^(m-l)] F^j, m = 0 .. M.
    for (size_t m = 0; m <= M; ++m) {
      std::vector<uint64_t> row(C, 0);
      for (int j = 0; j <= A; ++j)
        for (int l = 0; l <= B && (size_t)l <= m; ++l)
          row[(size_t)j * (B + 1) + l] = pw[j][m - (size_t)l];
      rows.push_back(std::move(row));
    }
  } else {
    std::fprintf(stderr, "unknown mode %s\n", mode.c_str());
    return 1;
  }

  if (skip) rows.erase(rows.begin(), rows.begin() + std::min(skip, rows.size()));
  const size_t R = rows.size();
  std::printf("mode=%s terms=%zu box=(%d,%d) unknowns=%zu rows=%zu skip=%zu"
              " prime=%llu\n",
              mode.c_str(), M, A, B, C, R, skip, (unsigned long long)P);
  if (R <= C) {
    std::printf("UNDERDETERMINED: rows %zu <= unknowns %zu -- more terms needed\n",
                R, C);
    std::printf("VERDICT: INCONCLUSIVE\n");
    rep.done("underdetermined");
    return 2;
  }

  // Holdout: fit on the first C+train_extra rows, then test the resulting
  // nullspace against every later row.
  const size_t Ttrain = std::min(R, C + train_extra);
  std::vector<std::vector<uint64_t>> tr(rows.begin(), rows.begin() + Ttrain);
  std::vector<size_t> piv;
  const size_t rk_tr = Rref(tr, C, &piv);
  const auto basis = Nullspace(tr, C, piv);
  std::printf("train rows=%zu rank=%zu nullity=%zu\n", Ttrain, rk_tr,
              C - rk_tr);
  size_t best_hold = 0;
  for (const auto& v : basis) {
    size_t ok = 0;
    for (size_t r = Ttrain; r < R; ++r) {
      uint64_t s = 0;
      for (size_t c = 0; c < C; ++c)
        if (v[c] && rows[r][c]) s = Add(s, Mul(v[c], rows[r][c]));
      if (s) break;
      ++ok;
    }
    if (ok > best_hold) best_hold = ok;
  }
  std::printf("holdout rows=%zu best_consecutive_pass=%zu\n", R - Ttrain,
              best_hold);

  // The exclusion itself: rank over ALL rows. Rank is monotone in the row set
  // and capped at C, so a full-rank training block already settles it -- skip
  // the second reduction rather than recompute a foregone conclusion.
  size_t rk = rk_tr;
  if (rk_tr < C) {
    std::vector<size_t> piv2;
    rk = Rref(rows, C, &piv2);
  }
  std::printf("full rank=%zu of %zu unknowns; nullity=%zu\n", rk, C, C - rk);
  const bool excluded = (rk == C);
  std::printf("VERDICT: %s\n", excluded ? "EXCLUDED" : "CANDIDATE");
  rep.done(std::string("rank=") + std::to_string(rk) + " of " +
           std::to_string(C));
  return excluded ? 0 : 3;
}
