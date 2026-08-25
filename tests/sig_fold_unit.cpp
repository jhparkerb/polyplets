// Isolated unit test for the R1 vertical-mirror fold (cpp/tma/signature.h),
// BEFORE any enumeration is involved.
//
// The fold stores only the orbit-canonical signature min(s, reflect(s)) and
// sums into it, halving live states. That is exact only if reflection is a
// symmetry of the whole column step, and THAT is a property of ~40 lines of
// signature/transition code -- not of the polyplet counts. gate_tma check M
// proved it by enumerating square8 to n=14 twice (391 s of that gate's 429 s,
// per its own comment); the same statement is settled here exhaustively over
// the signature space in well under a second.
//
// The header cites experiments/r1_sym_fold_check.py as the fold's validation.
// That file was deleted in 91bdcdc. This is its replacement, in-tree and run
// by `make gates`.
//
// Checks, over EVERY canonical signature at height H (not merely the reachable
// ones -- a superset only makes the statements stronger):
//
//   P1 reflect is an involution:          reflect(reflect(s)) == s
//   P2 fold picks the orbit representative: fold(s) == fold(reflect(s)), and
//      the result is one of the two orbit members
//   P3 the admissible completion bound is reflection-invariant (else the
//      size-budget prune would drop a state and keep its mirror)
//   P4 the column step COMMUTES with reflection: for every mask m,
//      step(reflect(s), reverse(m)) has the same outcome as step(s, m), and on
//      Alive its output is reflect(out)
//   P5 the engine's whole per-state keep-set corresponds under reflection, for
//      every size budget: forEachViableMask + step + the completionLowerBound
//      prune, exactly as sweep8.h composes them. (forEachViableMask ALONE is
//      not mirror-symmetric -- its reach prune looks only at top reach -- so
//      the property has to be stated on the composition the sweep uses.)
//   P6 the closing predicate (one component, both edges touched) is
//      reflection-invariant, so folded and unfolded states harvest alike
//
// Build: c++ -std=c++20 -O2 -Wall tests/sig_fold_unit.cpp -o build/sig_fold_unit
// Usage: sig_fold_unit [HMAX|--deep]   (default 6, --deep = 8)
//        sig_fold_unit --selftest   RED controls: three mutant folds must fail
//
// Exit 0 = green.
//
// TODO(2026-08-24, from the simplify pass): two known redundancies, both left
// in on purpose. (1) enumSigs yields both members of every mirror orbit, and
// P1-P6 are symmetric under the swap, so the whole sweep runs twice; skipping
// one representative would halve it. (2) P5's budget loop re-steps every mask
// once per budget, and P4 has already stepped them all -- a per-signature
// mask table would serve both. Neither was applied because this is a
// VERIFIER: it is 0.9 s on the push tier, and stating each property as its own
// straight-line loop is what makes it readable against the six claims in the
// header. Revisit if the deep tier (92 s at H=8) ever becomes a bottleneck.

#include <algorithm>
#include <cstdio>
#include <cstring>
#include <cstdlib>
#include <set>
#include <string>
#include <utility>
#include <vector>

#include "../cpp/tma/signature.h"
#include "../cpp/tma/transition_square8.h"

using ReflectFn = Sig (*)(const Sig&, int);
using FoldFn = void (*)(Sig&, int);

static Sig realReflect(const Sig& s, int H) { return reflectSig(s, H); }
static void realFold(Sig& s, int H) { foldSig(s, H); }

static std::string key(const Sig& s) {
  return std::string(reinterpret_cast<const char*>(s.b), SIGMAX);
}

static unsigned revMask(unsigned m, int H) {
  unsigned r = 0;
  for (int i = 0; i < H; ++i)
    if ((m >> i) & 1u) r |= 1u << (H - 1 - i);
  return r;
}

// Every canonical signature at height H: a subset of occupied rows, a set
// partition of them written as a restricted-growth string (which IS canonical
// label order), and the two touch flags.
static std::vector<Sig> enumSigs(int H) {
  std::vector<Sig> out;
  std::vector<int> rows;
  for (unsigned sub = 0; sub < (1u << H); ++sub) {
    rows.clear();
    for (int i = 0; i < H; ++i)
      if ((sub >> i) & 1u) rows.push_back(i);
    const int k = static_cast<int>(rows.size());
    std::vector<int> a(static_cast<size_t>(k), 1);
    for (;;) {
      for (int tt = 0; tt < 4; ++tt) {
        Sig s;
        std::memset(s.b, 0, SIGMAX);
        for (int i = 0; i < k; ++i)
          s.b[rows[i]] = static_cast<unsigned char>(a[i]);
        s.b[H] = static_cast<unsigned char>(tt & 1);
        s.b[H + 1] = static_cast<unsigned char>((tt >> 1) & 1);
        out.push_back(s);
      }
      if (k == 0) break;
      int i = k - 1, mx;
      for (; i >= 0; --i) {
        mx = 0;
        for (int j = 0; j < i; ++j) mx = std::max(mx, a[j]);
        if (a[i] <= mx) {
          ++a[i];
          for (int j = i + 1; j < k; ++j) a[j] = 1;
          break;
        }
      }
      if (i < 0) break;
    }
  }
  return out;
}

// The per-state keep-set the sweep actually builds: viable masks, stepped,
// surviving the size-budget prune. `budget` is maxn - (min cells so far).
static std::set<std::pair<unsigned, std::string>>
keepSet(const Sig& s, int H, int budget) {
  std::set<std::pair<unsigned, std::string>> out;
  forEachViableMask(s, H, budget, [&](unsigned mask) {
    Sig nxt;
    if (stepColumnSquare8(s, H, mask, nxt) != Outcome::Alive) return;
    const int cells = __builtin_popcount(mask);
    if (cells + completionLowerBound(nxt.b, H) > budget) return;
    out.insert({mask, key(nxt)});
  });
  return out;
}

static bool closes(const Sig& s, int H) {
  int comps = 0;
  for (int j = 0; j < H; ++j)
    if (s.b[j] > comps) comps = s.b[j];
  return comps == 1 && s.b[H] && s.b[H + 1];
}

// Returns the number of failing properties (0 = green). `quiet` suppresses the
// per-failure report, for the RED controls which EXPECT failure.
static int properties(int Hmax, ReflectFn refl, FoldFn fold, bool quiet) {
  int fails = 0;
  auto bad = [&](int H, const char* what, const Sig& s) {
    ++fails;
    if (quiet || fails > 5) return;
    std::printf("  FAIL H=%d %s at sig [", H, what);
    for (int i = 0; i < H + 2; ++i) std::printf("%d", s.b[i]);
    std::printf("]\n");
  };

  for (int H = 2; H <= Hmax; ++H) {
    const std::vector<Sig> sigs = enumSigs(H);
    for (const Sig& s : sigs) {
      const Sig rs = refl(s, H);

      if (!(refl(rs, H) == s)) bad(H, "P1 reflect not an involution", s);

      Sig fs = s, frs = rs;
      fold(fs, H);
      fold(frs, H);
      if (!(fs == frs)) bad(H, "P2 fold disagrees across the orbit", s);
      if (!(fs == s || fs == rs)) bad(H, "P2 fold left the orbit", s);

      if (completionLowerBound(s.b, H) != completionLowerBound(rs.b, H))
        bad(H, "P3 completion bound not mirror-invariant", s);

      if (closes(s, H) != closes(rs, H))
        bad(H, "P6 closing predicate not mirror-invariant", s);

      for (unsigned m = 1; m < (1u << H); ++m) {
        Sig o, ro;
        const Outcome a = stepColumnSquare8(s, H, m, o);
        const Outcome b = stepColumnSquare8(rs, H, revMask(m, H), ro);
        if (a != b) { bad(H, "P4 step outcome differs under reflection", s); continue; }
        if (a == Outcome::Alive && !(refl(o, H) == ro))
          bad(H, "P4 step output is not the reflected output", s);
      }

      for (int budget = 0; budget <= H + 1; ++budget) {
        std::set<std::pair<unsigned, std::string>> want;
        for (const auto& [m, k] : keepSet(s, H, budget)) {
          Sig o;
          std::memcpy(o.b, k.data(), SIGMAX);
          want.insert({revMask(m, H), key(refl(o, H))});
        }
        if (want != keepSet(rs, H, budget))
          bad(H, "P5 keep-set does not correspond under reflection", s);
      }
    }
    if (!quiet)
      std::printf("  H=%d: %zu canonical signatures, P1-P6 hold\n", H, sigs.size());
  }
  return fails;
}

// --- RED controls ------------------------------------------------------------
// Each mutant breaks the fold in a way the engine would silently miscount, and
// each must be caught. A gate that cannot fail is a decoration.

static Sig mutNoFlagSwap(const Sig& s, int H) {  // forgets top<->bottom
  Sig r;
  std::memcpy(r.b, s.b, SIGMAX);
  for (int i = 0; i < H; ++i) r.b[i] = s.b[H - 1 - i];
  canonicalizeSig(r.b, H);
  return r;
}

static Sig mutNoCanon(const Sig& s, int H) {  // forgets to relabel
  Sig r;
  std::memcpy(r.b, s.b, SIGMAX);
  for (int i = 0; i < H; ++i) r.b[i] = s.b[H - 1 - i];
  r.b[H] = s.b[H + 1];
  r.b[H + 1] = s.b[H];
  return r;
}

static void mutIdentityFold(Sig&, int) {}  // folds nothing: orbit not collapsed

static int selftest() {
  const int H = 5;
  struct { const char* name; ReflectFn refl; FoldFn fold; } muts[] = {
      {"reflect without the touch-flag swap", mutNoFlagSwap, realFold},
      {"reflect without label canonicalization", mutNoCanon, realFold},
      {"fold that never folds", realReflect, mutIdentityFold},
  };
  int fired = 0;
  for (const auto& m : muts) {
    const int f = properties(H, m.refl, m.fold, true);
    std::printf("  [RED] %-42s -> %d failing properties\n", m.name, f);
    if (f > 0) ++fired;
  }
  const int clean = properties(H, realReflect, realFold, true);
  std::printf("  [baseline] real reflect + real fold -> %d failing properties\n", clean);
  if (clean != 0) {
    std::printf("SELFTEST RED: the baseline itself fails\n");
    return 1;
  }
  if (fired != 3) {
    std::printf("SELFTEST RED: only %d/3 mutants were caught\n", fired);
    return 1;
  }
  std::printf("SIG-FOLD SELFTEST GREEN: 3/3 red controls fired\n");
  return 0;
}

int main(int argc, char** argv) {
  if (argc > 1 && std::string(argv[1]) == "--selftest") return selftest();
  // H=6 is 3508 canonical signatures and the whole check is milliseconds; the
  // deep tier goes to H=8, which is ~85k signatures and a few seconds. The
  // statement is the same at every H -- more of them is more of the same.
  int Hmax = 6;
  if (argc > 1) Hmax = std::string(argv[1]) == "--deep" ? 8 : std::atoi(argv[1]);
  if (Hmax < 2 || Hmax > 12) {
    std::printf("HMAX out of range (2..12)\n");
    return 2;
  }
  const int fails = properties(Hmax, realReflect, realFold, false);
  if (fails) {
    std::printf("SIG-FOLD RED: %d failing properties\n", fails);
    return 1;
  }
  std::printf("SIG-FOLD GREEN: reflection is a symmetry of the column step "
              "(H=2..%d, exhaustive)\n", Hmax);
  return 0;
}
