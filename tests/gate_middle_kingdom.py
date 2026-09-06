#!/usr/bin/env python3
"""Gate MIDDLE-KINGDOM: results/subclasses.md (formerly docs/middle-kingdom-plan.md) Phase 3 acceptance.

build/middle_kingdom_tm is a COLUMN transfer matrix for the column-convex
cells of the Phase 3 grid. Phase 3's finding is that on a column-convex king
animal every directedness predicate in the grid reduces to a condition on the
bottom profile b(j) alone (results/middle-kingdom-phase3.md):

  dir5   b valley-unimodal (nonincreasing then nondecreasing)
  dir4   b(j) >= b(j-1) - 1 (the bottom drops at most one row per step right)
  ctrlB  every local minimum of b sits at the global minimum
  hv     b valley-unimodal AND t peak-unimodal (this IS HV-convexity)

The transfer matrix counts bottom profiles directly, so it is a completely
different machine from the Redelmeier brute force in
build/directed_cone_anchor -- which is exactly what makes the agreement below
worth having. Phase 0's brute-force table (results/middle-kingdom-grid.md,
n = 1..14, 20 cells since Phase 3 added the mdir row) is the oracle; the plan is explicit that no transfer matrix is
trusted until it matches that table on its overlap.

Positive controls the TM must PASS (the machinery is calibrated by sequences
that were known before Phase 3):
  cc      column-convex king animals = A187077
  ccmono  column-convex + bottoms nondecreasing = A007052 (the identity
          results/king-subfamilies.md proves, and Phase 0 Finding 1's
          "fifth convexity variant")
  hv      HV-convex king animals by area = the novel convex-polyplet series,
          checked against ALL 700 terms of results/convex_area_terms_n700_king.txt,
          which came from an independent ROW transfer matrix (convex_area_tm)

RED controls that must DIVERGE (a predicate that quietly matched everything
would make every positive above meaningless):
  ccdir4bad   dir4's bottom-drop bound loosened from 1 to 2
  ccctrlbbad  ctrlB with the plateau rule dropped (a local-minimum PLATEAU
              above the global minimum wrongly accepted)
  ccmono      vs ccdir5: bottoms-nondecreasing is not valley-unimodality
  hvdir4ascbad  the phase split with phase (1,0) deleted instead of (0,1)
  d=0 join      Lemma 3's column-join with d = 0 instead of max(0, h - h')
                must leave the class
  stacks P(n)   A001523 must VIOLATE supermultiplicativity, or the
                M(i)M(j) <= M(i+j) check would pass for any sequence
"""
import os
import sys

from common import ROOT, Gate, prec_guess, read_terms_file, run

BIN = os.path.join(ROOT, "build", "middle_kingdom_tm")
KING_TERMS = os.path.join(ROOT, "results", "convex_area_terms_n700_king.txt")
# middle_kingdom_tm needs GMP, which the Makefile treats as optional. The
# series it produced are in the tree either way, so on a box without GMP this
# gate falls back to them and skips only the checks that need a fresh run
# (the RED controls and the two modes with no banked file), exactly as
# tests/gate_convex_dfinite.py does for convex_area_tm.
TERMS_FILE = {
    "cc": os.path.join(ROOT, "results", "mk_cc_terms_n700.txt"),
    "ccdir5": os.path.join(ROOT, "results", "mk_ccdir5_terms_n700.txt"),
    "ccdir4": os.path.join(ROOT, "results", "mk_ccdir4_terms_n700.txt"),
    "ccctrlb": os.path.join(ROOT, "results", "mk_ccctrlb_terms_n250.txt"),
    "hvdir4": os.path.join(ROOT, "results", "mk_hvdir4_terms_n700.txt"),
}
HAVE_BIN = os.path.exists(BIN)

# results/middle-kingdom-grid.md, the brute-force grid table, n = 1..14.
# Column-convex block (conv=colconvex) for each directedness row, plus the
# HV-convex column for none/dir4.
GRID = {
    "cc": [1, 4, 18, 83, 385, 1788, 8305, 38575, 179170, 832189, 3865253,
           17952864, 83385309, 387298083],
    "ccdir5": [1, 4, 17, 71, 289, 1149, 4481, 17209, 65281, 245169, 913153,
               3377505, 12418561, 45428161],
    "ccdir4": [1, 4, 17, 73, 314, 1351, 5813, 25012, 107621, 463069, 1992482,
               8573203, 36888569, 158723236],
    "ccctrlb": [1, 4, 18, 79, 339, 1423, 5872, 23909, 96336, 384934, 1527712,
                6029421, 23686066, 92685759],
    "hv": [1, 4, 16, 61, 221, 766, 2566, 8390, 26982, 85834, 271174, 853111,
           2677214, 8389720],
    "hvdir4": [1, 4, 15, 53, 177, 567, 1767, 5417, 16465, 49897, 151288,
               459836, 1402387, 4292477],
    # staircase column of results/mk_grid20_n14.txt = A225114 (skew shapes with
    # no empty row or column, results/king-subfamilies.md). It is the LOWER rung
    # of the growth sandwich in results/hv-growth-sandwich.md, so the transfer
    # matrix has to reproduce it before that proof's numerics mean anything.
    "stair": [1, 3, 9, 28, 87, 272, 850, 2659, 8318, 26025, 81427, 254777,
              797175, 2494307],
    # (dir4, HV-convex) animals whose unimodality-phase path never visits
    # (0,1) -- the half of the series the truncated descending block cannot
    # reach (results/hv-growth-sandwich.md, "The series splits"). Oracle:
    # experiments/descent_block_oracle.py --phases 14, an independent DFS over
    # explicit column intervals that carries the two phase bits itself.
    "hvdir4asc": [1, 3, 10, 34, 115, 382, 1244, 3993, 12689, 40065, 126005,
                  395369, 1238923, 3879468],
}
# Same DFS with phase (1,0) deleted instead of (0,1) -- the RED control for the
# phase split. If banPhase were a no-op, or wired to the wrong phase code, the
# hvdir4asc row above would come out equal to one of these two.
HVDIR4ASCBAD = [1, 3, 9, 27, 79, 222, 602, 1589, 4112, 10497, 26565, 66879,
                167900, 421000]
A007052 = [1, 3, 10, 34, 116, 396, 1352, 4616, 15760, 53808, 183712, 627232]

# Phase 3's closed forms (results/middle-kingdom-phase3.md): denominator and
# numerator of the rational generating function F(x) = sum_{n>=1} a(n) x^n,
# low-order coefficient first. Each was DERIVED (the transfer operator on a
# column-convex animal has rank <= 2, because the number of ways to place a
# height-h' column against a height-h one is h + h' + 1), so this check is
# what turns "the guesser found a recurrence" into "the derivation is right".
# cc's is A187077's own published g.f. -- the calibration for the other two.
GF = {
    "cc":     ([1, -7, 13, -10, 2],     [0, 1, -3, 3, -1]),
    "ccdir5": ([1, -9, 28, -36, 20, -4], [0, 1, -5, 9, -6, 2]),
    "ccdir4": ([1, -5, 3],              [0, 1, -1]),
}
# Cells with no closed form: the guesser must still come back EXCLUDED in the
# boxes Phase 3 quotes, or the writeup's negatives are worthless.
EXCLUDE = [("ccctrlb", "prec", 12, 12), ("ccctrlb", "alg", 8, 14),
           ("hvdir4", "prec", 20, 20), ("hvdir4", "alg", 20, 20)]


def terms(mode, n):
    """First n terms of a mode: from the binary, or the banked file, or None."""
    if HAVE_BIN:
        out = run(BIN, mode, n)
        return [int(line.split()[-1]) for line in out.strip().splitlines()]
    if mode in TERMS_FILE:
        vals = read_terms_file(TERMS_FILE[mode])
        return vals[:n] if len(vals) >= n else None
    return None


def main():
    gate = Gate()
    if not HAVE_BIN:
        gate.skip(f"fresh {BIN} runs (no GMP build); using the banked series")

    # --- positive: every column-convex cell vs Phase 0's brute force ---------
    for mode, ref in GRID.items():
        got = terms(mode, len(ref))
        if got is None:
            gate.skip(f"{mode} vs Phase 0 grid (needs a GMP build)")
            continue
        bad = [i + 1 for i, (a, b) in enumerate(zip(got, ref)) if a != b]
        gate.check(got == ref,
                   f"{mode} vs Phase 0 brute-force grid n<=14"
                   + (f"  MISMATCH at n={bad}: got {got}" if bad else ""))

    if HAVE_BIN:
        # --- positive: ccmono = A007052 (king-subfamilies.md Theorem dcc) ---
        got = terms("ccmono", len(A007052))
        gate.check(got == A007052,
                   f"ccmono = A007052 (order-consecutive partitions): got {got}")

        # --- positive: hv vs the independent ROW transfer matrix ------------
        ref700 = read_terms_file(KING_TERMS)
        n700 = min(len(ref700), 120)
        got = terms("hv", n700)
        bad = [i + 1 for i, (a, b) in enumerate(zip(got, ref700[:n700]))
               if a != b]
        gate.check(got == ref700[:n700],
                   f"hv (column TM) vs convex_area_tm row TM, n<={n700}"
                   + (f"  MISMATCH at n={bad[:5]}" if bad else ""))

        # --- RED: loosened dir4 bound must diverge -------------------------
        bad4 = terms("ccdir4bad", 14)
        gate.check(bad4 != GRID["ccdir4"],
                   f"RED ccdir4bad (drop<=2) MUST diverge from ccdir4: got {bad4}")
        gate.check(all(x >= y for x, y in zip(bad4, GRID["ccdir4"])),
                   "RED ccdir4bad is a superset of ccdir4 (termwise >=)")

        # --- RED: ctrlB with the plateau rule dropped must diverge ---------
        badB = terms("ccctrlbbad", 14)
        gate.check(badB != GRID["ccctrlb"],
                   f"RED ccctrlbbad MUST diverge from ccctrlb: got {badB}")

        # --- RED: bottoms-nondecreasing is not valley-unimodality ----------
        gate.check(terms("ccmono", 6) != GRID["ccdir5"][:6],
                   "RED ccmono MUST diverge from ccdir5")

        # --- RED: staircase needs BOTH boundaries monotone ------------------
        # Dropping the tops condition from `stair` leaves `ccmono` = A007052,
        # which must not accidentally equal A225114 -- otherwise the `stair`
        # mode would be testing nothing about tops.
        gate.check(terms("ccmono", 14) != GRID["stair"],
                   "RED ccmono (tops unconstrained) MUST diverge from stair")

        # --- structural: the growth sandwich of results/hv-growth-sandwich.md
        # stair subset hvmono subset hvdir4 subset hv, termwise. The middle two
        # have no independent brute force, so this nesting is what pins them.
        st, hm = terms("stair", 14), terms("hvmono", 14)
        gate.check(all(a <= b <= c <= d for a, b, c, d
                       in zip(st, hm, GRID["hvdir4"], GRID["hv"])),
                   f"stair <= hvmono <= hvdir4 <= hv termwise: "
                   f"stair={st[:6]} hvmono={hm[:6]}")
        gate.check(st != hm and hm != GRID["hvdir4"][:14],
                   "the sandwich is strict somewhere (no rung is a duplicate)")

        # --- the phase split of results/hv-growth-sandwich.md ---------------
        # hvdir4 = hvdir4asc + (the animals whose phase path visits (0,1)).
        # The split is what turns "the 4-cone series' subdominant equals the
        # descending block's growth constant" from a coincidence between two
        # extrapolated numbers into a decomposition of the series, so the
        # identity below is load-bearing for that write-up.
        asc = terms("hvdir4asc", 14)
        gate.check(all(a <= b for a, b in zip(GRID["stair"], asc)),
                   f"stair <= hvdir4asc termwise (the staircase never enters "
                   f"phase (0,1)): got {asc[:6]}")
        gate.check(all(a <= b for a, b in zip(asc, GRID["hvdir4"])),
                   "hvdir4asc <= hvdir4 termwise (it is a subclass)")
        gate.check(asc != GRID["hvdir4"],
                   "the phase split is not a no-op: hvdir4asc != hvdir4")
        # RED: deleting phase (1,0) instead of (0,1) must give other numbers.
        gate.check(terms("hvdir4ascbad", 14) == HVDIR4ASCBAD != asc,
                   "RED hvdir4ascbad (phase (1,0) deleted) MUST diverge from "
                   "hvdir4asc")
    else:
        gate.skip("ccmono/hv positives and the three RED controls "
                  "(no banked series for those modes)")

    # --- structural: dir5 subset ctrlB subset cc, and hvdir4 subset hv ------
    d5, cb, c0 = GRID["ccdir5"], GRID["ccctrlb"], GRID["cc"]
    gate.check(all(a <= b <= c for a, b, c in zip(d5, cb, c0)),
               "dir5 <= ctrlB <= column-convex termwise (nesting)")
    gate.check(all(a <= b for a, b in zip(GRID["hvdir4"], GRID["hv"])),
               "dir4-HV <= HV termwise (nesting)")

    # --- positive: the derived rational generating functions ----------------
    # GF_N terms, not 700: the largest denominator here has 6 coefficients, so
    # 150 terms over-determine the identity by ~145 equations and nothing is
    # weakened -- while the engine is ~O(N^3), so 700 cost 5.6 s of this
    # gate's 7.8 s and 150 costs 0.04 s. The engine itself is pinned against
    # the independent row transfer matrix on 120 terms above.
    GF_N = 150
    for mode, (den, num) in GF.items():
        a = [0] + terms(mode, GF_N)
        prod = [sum(den[i] * a[m - i] for i in range(len(den)) if 0 <= m - i < len(a))
                for m in range(len(a))]
        ok = prod[:len(num)] == num and not any(prod[len(num):])
        gate.check(ok, f"{mode}: derived g.f. denominator*F == numerator "
                       f"exactly, all {GF_N} terms"
                   + ("" if ok else f"  got {prod[:len(num) + 3]}"))

    # --- the exclusions the write-up quotes, re-run here -------------------
    guess = os.path.join(ROOT, "build", "prec_guess")
    if os.path.exists(guess):
        for name, mode, j, d in EXCLUDE:
            v, _, _, _ = prec_guess(guess, mode, TERMS_FILE[name], j, d)
            gate.check(v == "EXCLUDED",
                       f"{name}: {mode} box ({j},{d}) EXCLUDED "
                       f"(no P-recurrence / algebraic relation of that size): "
                       f"got {v}")
    else:
        gate.skip("prec_guess exclusions (build/prec_guess absent)")

    # --- the amplitude-ratio identity ---------------------------------------
    # results/hv-growth-sandwich.md, "The amplitude ratio is a ratio of two
    # explicit feed vectors". Two things carry that section and neither is
    # checked anywhere else: Proposition 9's mirror involution (which is the
    # whole content of the factor 1/2) and the feed-vector evaluation of the
    # ratio, which has to reproduce results/subclasses.md (formerly docs/middle-kingdom-followups-plan.md)
    # Table B's 54 MEASURED digits. Both run in under a second.
    sys.path.insert(0, os.path.join(ROOT, "experiments"))
    import descent_block_oracle as dbo

    tot, v10, v01, nei = dbo.brute_hv_mirror(11)
    gate.check(tot[1:12] == GRID["hv"][:11],
               f"HV-convex phase split totals vs the grid n<=11: got {tot[1:12]}")
    gate.check(v10[1:] == v01[1:],
               f"Prop 9: A_(1,0) == A_(0,1) termwise n<=11: got {v10[1:]}"
               f" vs {v01[1:]}")
    gate.check(v10[2:] != nei[2:],
               "RED the mirror halves MUST differ from the phase-(0,0)->(1,1) "
               "remainder (else the split is vacuous)")

    # --- Lemma 3: the column-join is injective at FIXED (i, j) --------------
    # results/hv-growth-sandwich.md Lemma 3, strengthened to M(i)M(j) <=
    # M(i+j) (docs/sortie-publication-plan.md B1). What the proof turns on is
    # that column areas are positive, so the area-i prefix is unique and no
    # split index has to be carried; the checks below are the join landing in
    # the class, the injectivity, and the inequality on all 700 banked terms.
    import staircase_supermul as sms

    M = sms.banked(sms.TERMS)
    pool = {n: sms.animals(n) for n in range(1, 9)}
    gate.check(all(len(pool[n]) == M[n] for n in pool),
               f"staircase animals as (heights, offsets) reproduce M(1..8): "
               f"got {[len(pool[n]) for n in sorted(pool)]}")
    inclass = injective = True
    for i in range(1, 8):
        for j in range(1, 9 - i):
            seen = {sms.join(x, y) for x in pool[i] for y in pool[j]}
            inclass &= all(sms.is_animal(*z) and sum(z[0]) == i + j for z in seen)
            injective &= (len(seen) == len(pool[i]) * len(pool[j])
                          and all(sms.cut(z, i) for z in seen))
    gate.check(inclass, "the column-join stays a staircase animal of area i+j")
    gate.check(injective,
               "the column-join is injective at fixed (i,j) and the area-i cut "
               "inverts it, i+j <= 8")
    gate.check(any(not sms.is_animal(*sms.join(x, y, rule="zero"))
                   for i in range(1, 8) for j in range(1, 9 - i)
                   for x in pool[i] for y in pool[j]),
               "RED the d=0 join MUST leave the class (else the max(0,.) rule "
               "is doing nothing)")
    bad = sms.supermul_violations(M, len(M) - 1)
    gate.check(not bad,
               f"M(i)M(j) <= M(i+j) for every pair with i+j <= {len(M) - 1}: "
               f"got {len(bad)} violations {bad[:3]}")
    P = sms.stacks(24)
    gate.check(sms.supermul_violations(P, 24),
               "RED the stacks P(n) = A001523 MUST violate supermultiplicativity "
               "(else the check above passes for any sequence)")

    # --- Lemma 2 without Hardy-Ramanujan (sortie plan B2) -------------------
    # p(n) <= (n+1)^(s+L+1) by splitting a partition at s = ceil(sqrt n). The
    # inequality itself is slack by miles, so what is pinned is the counting:
    # the small/large encoding must be injective and must land in the two
    # ranges the exponent multiplies, and the large-part cap must be ATTAINED
    # (one fewer and the bound would be false).
    import monotone_block_growth as mbg

    p = mbg.partitions(120)
    Pn = mbg.dp(120)
    gate.check(all(p[n] <= (n + 1) ** mbg.small_large_exponent(n)
                   and mbg.small_large_exponent(n) <= 2 * n ** 0.5 + 2
                   for n in range(1, 121)),
               "p(n) <= (n+1)^(s+L+1) <= (n+1)^(2 sqrt(n)+2), n <= 120")
    gate.check(all(Pn[n] <= (n + 1) ** 2 * p[n] ** 2 for n in range(1, 121)),
               "P(n) <= (n+1)^2 p(n)^2 (split the stack at its peak), n <= 120")
    enc_ok, cap_tight = True, True
    for n in range(1, 21):
        s = mbg.ceil_sqrt(n)
        cap, codes, most = n // (s + 1), set(), 0
        for lam in mbg._partitions_of(n):
            codes.add((tuple(sum(1 for x in lam if x == v) for v in range(1, s + 1)),
                       tuple(x for x in lam if x > s)))
            most = max(most, sum(1 for x in lam if x > s))
        enc_ok &= len(codes) == p[n] and most <= cap
        cap_tight &= most == cap
    gate.check(enc_ok,
               "the small/large split encodes partitions injectively inside the "
               "ranges the exponent counts, n <= 20")
    gate.check(cap_tight,
               "RED the large-part cap floor(n/(s+1)) is ATTAINED at every "
               "n <= 20, so a smaller cap would be a false bound")

    try:
        import amplitude_feed_vectors as afv
        from mpmath import mpf
    except ImportError:
        gate.skip("feed-vector amplitude identity (mpmath absent)")
    else:
        mu, r, r_nohalf, r_cap3, minphi = afv.evaluate(120, 300)
        gate.check(minphi > 0,
                   f"Perron: the staircase eigenvector is positive (min {minphi})")
        gate.check(afv.agree_digits(mu, mpf(afv.MU_BANKED)) >= 110,
                   "mu by shooting on phi(h)=(2-x^(h-1))phi(h-1)-phi(h-2) "
                   "reproduces the banked mu to >=110 digits")
        d_tb = afv.agree_digits(r, mpf(afv.TABLE_B))
        gate.check(d_tb >= 53,
                   f"(1/2)(w4.phi)/(w.phi) reproduces Table B's 54 measured "
                   f"digits: got {d_tb}")
        gate.check(afv.agree_digits(r_nohalf, mpf(afv.TABLE_B)) < 3,
                   "RED dropping the factor 1/2 MUST NOT reproduce Table B")
        gate.check(afv.agree_digits(r_cap3, mpf(afv.TABLE_B)) < 3,
                   "RED truncating the (0,0) block at 3 instead of 2 MUST NOT "
                   "reproduce Table B")

    return gate.verdict("MIDDLE-KINGDOM")


if __name__ == "__main__":
    sys.exit(main())
