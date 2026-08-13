"""Proposer 1 (proof-first): algebraicity of the mod-3 triangle series.

Hypothesis class (chosen from theory, not data -- see
results/triangle-hunt-proof-first.md): by Christol, the open mod-3 region
(sleeve + below onset, the coefficient array of R_k mod 3) has a law in the
spine's family iff the series

    F(y,z) = sum (T(n,H) mod 3) y^(n-H) z^H

(or its below-onset cone restriction) is ALGEBRAIC over F_3(y,z). The proved
in-regime structure (spine cubic W^3 = W^2 + t) is exactly of this type, and
periodicity-class laws are machine-refuted on the open region, so this is the
lightest mechanism-backed class left.

fit(): hunts Q(y,z,F) = 0 on a ladder of ansatzes (deg_F <= D, deg_y <= dy,
deg_z <= dz), keeping #equations >= 2x #unknowns inside the n <= 22 sandbox;
a found Q must Hensel-continue FROM SCRATCH (empty series) and reproduce every
sandbox coefficient before it is accepted. predict(): extends the root to
weight 40 by the same Hensel recursion -- consumes no banked cells at all.
An empty ladder raises (=> CULLED(FIT-ERROR), the machine-stamped negative).
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from schema import Candidate
import p1_alg_hunt as alg

NMAX = 40


def _known_mod3(n, H):
    """Mirror of known.py's mod-3 coverage (reimplemented; see p1_mod3_map.py).
    Returns a residue if prior work determines it, else None (open cell)."""
    k = n - H
    if k < 0:
        return 0
    e = n - 1 - 3 * k
    if n < (3 * H) // 2:
        return 0
    if n == (3 * H) // 2:
        return -1  # boundary: known via T2/T3 (value irrelevant here)
    if e >= 1:
        return 0
    if e == 0:
        return -1  # spine cell, known via T1 digit product
    if n % 3 == 2 and n >= 5 and H == 2 * ((n - 2) // 3) + 1:
        return 2
    return None


def _open_cell(n, H):
    return 1 <= H <= n and _known_mod3(n, H) is None and H >= 5


def _fit_factory(masked):
    def fit(view):
        # series coefficients from the sandbox
        f = {}
        for n in range(1, view.max_n + 1):
            for H in range(1, n + 1):
                k = n - H
                if masked and k < H:
                    continue
                r = view.cell(n, H) % 3
                if r:
                    f[(k, H)] = r
        N = view.max_n
        neq = (N + 1) * (N + 2) // 2
        tried = []
        ladder = sorted(
            ((D, dy, dz)
             for D in (1, 2, 3, 4)
             for dy in (1, 2, 3, 4, 5)
             for dz in (1, 2, 3, 4, 5)
             if 2 * (D + 1) * (dy + 1) * (dz + 1) <= neq),
            key=lambda t: (t[0] + 1) * (t[1] + 1) * (t[2] + 1))
        for (D, dy, dz) in ladder:
            real, _, nun = alg.hunt(f, N, D, dy, dz, verbose=False)
            tried.append(((D, dy, dz), nun, len(real)))
            for vec in real:
                terms = alg.q_terms(vec, D, dy, dz)
                try:
                    g = alg.hensel_extend(terms, {}, 1, N)
                except ValueError:
                    continue
                if g == f:
                    return {"terms": terms, "cache": dict(g), "upto": N}
        raise ValueError(
            "no algebraic Q on the %s series: every ansatz in the 2x-slack "
            "ladder (max unknowns %d, %d eqs) has empty kernel or no "
            "scratch-Hensel root matching the sandbox; ladder=%s"
            % ("below-onset cone" if masked else "full mod-3",
               max(t[1] for t in tried), neq,
               ",".join("D%ddy%ddz%d:k%d" % (t[0] + (t[2],)) for t in tried)))
    return fit


def _predict(params, n, H, ctx):
    if params["upto"] < NMAX:
        params["cache"] = alg.hensel_extend(
            params["terms"], params["cache"], params["upto"] + 1, NMAX)
        params["upto"] = NMAX
    return params["cache"].get((n - H, H), 0)


_INDEP = dict(
    input_footprint=(
        "derivation: own-enumerated cells n<=13 only (used to pick the "
        "hypothesis class and pre-test small ansatzes -- all empty); the "
        "equation itself is fitted by the sandbox on banked n<=22; "
        "predictions consume zero banked cells (scratch Hensel recursion)"),
    derivation_independence=(
        "class chosen from theory (Christol + the proved spine mechanism); "
        "no banked data read outside the FitView sandbox"),
    rule_independence=(
        "own king-adjacency implementation (p1_enum.cpp) for derivation "
        "data; the banked fit cells share the engines' rule lineage"),
)

CANDIDATES = [
    Candidate(
        id="p1-mod3-algebraic-full",
        proposer="p1-proof-first",
        statement=("the full triangle mod 3 is algebraic: Q(y,z,F)=0 for "
                   "polynomial Q found in-sandbox; residues of all open "
                   "cells (H>=5, sleeve + below onset) predicted by scratch "
                   "Hensel continuation of Q"),
        tier="C", kind="congruence", modulus=3, scope="cell",
        region=_open_cell, n_params=150,
        fit=_fit_factory(masked=False), predict=_predict,
        **_INDEP),
    Candidate(
        id="p1-mod3-algebraic-cone",
        proposer="p1-proof-first",
        statement=("the below-onset cone of the triangle mod 3 (cells with "
                   "n >= 2H) is algebraic over F_3(y,z); residues predicted "
                   "by scratch Hensel continuation"),
        tier="C", kind="congruence", modulus=3, scope="cell",
        region=lambda n, H: _open_cell(n, H) and n - H >= H,
        n_params=150,
        fit=_fit_factory(masked=True), predict=_predict,
        **_INDEP),
]
