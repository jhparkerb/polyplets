// argparse.h -- fail-closed integer command-line arguments.
//
// Every engine in cpp/ used to reach for atoi(), which maps "yes", "five" and
// "" all to 0 and reports no error. For a research binary that is the worst
// possible failure mode: `convex_area_tm 8 yes` silently enumerated
// edge-adjacent polyominoes when king animals were asked for, and
// `prec_guess prec terms five two` printed a confident VERDICT: EXCLUDED for
// box (0,0) at exit 0. Both look like results.
//
// Per docs/engineering-standards.md rule 3 (fail closed): a mistyped argument
// stops the run. Use ArgInt for a range, ArgFlag for a 0/1 switch.

#ifndef POLYOMINOES_CPP_ARGPARSE_H_
#define POLYOMINOES_CPP_ARGPARSE_H_

#include <cerrno>
#include <cstdio>
#include <cstdlib>

namespace argparse {

// Parse s as a decimal integer in [lo,hi]. Anything else -- trailing garbage,
// empty string, overflow, out of range -- exits 1 with a message naming the
// argument.
inline long ArgInt(const char* s, const char* name, long lo, long hi) {
  char* end = nullptr;
  errno = 0;
  const long v = std::strtol(s, &end, 10);
  if (errno != 0 || end == s || *end != '\0' || v < lo || v > hi) {
    std::fprintf(stderr, "bad %s '%s': want an integer in [%ld,%ld]\n", name, s,
                 lo, hi);
    std::exit(1);
  }
  return v;
}

// A switch that must be spelled exactly 0 or 1 -- "true"/"yes"/"" are refused,
// not quietly read as off.
inline bool ArgFlag(const char* s, const char* name) {
  return ArgInt(s, name, 0, 1) != 0;
}

}  // namespace argparse

#endif  // POLYOMINOES_CPP_ARGPARSE_H_
