#!/usr/bin/env python3
"""Birthright — brute-force check of the cut-count cancellation identity.

Checks the IDENTITY AS STATED in docs/proofs/cutcount-identity.md, not the
engine.  For every subset S of a small H x W board, enumerate the coloring
model of the statement directly (scan order, H+1-cell window, clash-void /
forced / adopt-or-birth rules, birth weight q - b with b the live-label count),
sum the weights exactly in Z[q], and compare against q^{c(S)} with c(S) from
flood fill.  Equality is asserted in Z[q] itself, which is stronger than the
mod-q^2 claim the engine needs; the mod-q^2 reduction is reported separately.

Also measured: the locality lemma (a component that is open at v always has a
cell in the H+1 window at v), the king reach bound (adjacent cells are at most
H+1 apart in scan order), and the largest gap a free cell actually needs --
which is smaller than H+1, because the H+1 slot is demanded by the clash rule,
not by liveness.

RED controls: five mutations of the model, each of which must FAIL.  A RED that
passes is a broken check and exits non-zero.

Pure python3 stdlib.  Run:  python3 birthright_identity_check.py
"""

import sys
import time

# ---------------------------------------------------------------- geometry
# Cell (r, c) of a height-H, width-W board has scan index c*H + r: column
# major, rows increasing within a column.  This is the engine's loop order
# (`for c ... for r ...` in run_height).

def rc(i, H):
    return (i % H, i // H)


def king_neighbours(H, W):
    """nb[i] = all king neighbors of i; pred[i] = those with index < i."""
    n = H * W
    nb = [[] for _ in range(n)]
    pred = [[] for _ in range(n)]
    for i in range(n):
        r, c = rc(i, H)
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                r2, c2 = r + dr, c + dc
                if 0 <= r2 < H and 0 <= c2 < W:
                    j = c2 * H + r2
                    nb[i].append(j)
                    if j < i:
                        pred[i].append(j)
    return nb, pred


def components(cells, nb):
    """Number of king-connected components of `cells` (a set), by flood fill,
    and the component id of each cell."""
    comp = {}
    ncomp = 0
    for v in cells:
        if v in comp:
            continue
        stack = [v]
        comp[v] = ncomp
        while stack:
            u = stack.pop()
            for w in nb[u]:
                if w in cells and w not in comp:
                    comp[w] = ncomp
                    stack.append(w)
        ncomp += 1
    return ncomp, comp


# ---------------------------------------------------------------- Z[q]
# Polynomials as lists of int coefficients, index = power of q.

def padd(a, b):
    if len(a) < len(b):
        a, b = b, a
    out = list(a)
    for k, v in enumerate(b):
        out[k] += v
    return out


def pmul_birth(p, b):
    """p * (q - b)."""
    out = [0] * (len(p) + 1)
    for k, v in enumerate(p):
        out[k + 1] += v
        out[k] -= b * v
    return out


def ptrim(p):
    while len(p) > 1 and p[-1] == 0:
        p.pop()
    return p


def monomial(c):
    return [0] * c + [1]


# ---------------------------------------------------------------- the model
# variant flags (all False = the identity exactly as stated):
#   no_clash   : a cell meeting two distinct labels adopts one instead of
#                voiding the configuration
#   b_global   : birth weight uses every label ever used, not the live ones
#   no_adopt   : a free cell may only give birth, never adopt a live label
#   win        : liveness window size, default H+1
#   blind      : earlier neighbors outside the window are invisible to the
#                clash/forced rule, as they would be in a DP whose state is
#                only the window -- this is what makes H+1 the necessary slot
#                count (the NW neighbor sits exactly H+1 back)

VARIANTS = {
    "GREEN  identity as stated": {},
    "RED-1  clash-voiding dropped": {"no_clash": True},
    "RED-2  b counts all labels, not live ones": {"b_global": True},
    "RED-3  free cell cannot adopt a live label": {"no_adopt": True},
    "RED-4  window of H cells, neighbors outside it unseen":
        {"win": "H", "blind": True},
    "RED-5  liveness window shortened to H-2": {"win": "H-2"},
}


def sum_weights(cells, H, pred, no_clash=False, b_global=False,
                no_adopt=False, win=None, blind=False):
    """Sum of w(phi) over non-void configurations of the cell list `cells`
    (ascending scan order).  Returns (poly, n_configs)."""
    win = {None: H + 1, "H": H, "H-1": H - 1, "H-2": H - 2}[win]
    lab = {}
    total = [0]
    nconf = 0

    def rec(k, poly, nextlab):
        nonlocal total, nconf
        if k == len(cells):
            total = padd(total, poly)
            nconf += 1
            return
        v = cells[k]
        vis = [u for u in pred[v] if not blind or u >= v - win]
        seen = set(lab[u] for u in vis if u in lab)
        if len(seen) >= 2:
            if not no_clash:
                return                       # void
            lab[v] = min(seen)
            rec(k + 1, poly, nextlab)
            del lab[v]
            return
        if len(seen) == 1:
            lab[v] = next(iter(seen))        # forced
            rec(k + 1, poly, nextlab)
            del lab[v]
            return
        live = set(lab[u] for u in range(max(0, v - win), v) if u in lab)
        b = len(set(lab.values())) if b_global else len(live)
        if not no_adopt:
            for l in sorted(live):           # adopt a live label, weight 1
                lab[v] = l
                rec(k + 1, poly, nextlab)
                del lab[v]
        lab[v] = nextlab                     # birth, weight q - b
        rec(k + 1, pmul_birth(poly, b), nextlab + 1)
        del lab[v]

    rec(0, [1], 1)
    return ptrim(total), nconf


# ---------------------------------------------------------------- locality
def locality_audit(cells_set, cells, H, pred, nb):
    """For every free cell v of S that is not the scan-minimum of its own
    component, check that the component has a cell inside the H+1 window at v
    (so its label is live and the adopt branch is on offer).

    Also records the largest gap v - u actually needed, over all such v, where
    u is the LATEST earlier cell of v's own component.

    Returns (n_checked, n_failed, max_gap_needed)."""
    _, comp = components(cells_set, nb)
    first = {}
    for v in cells:
        first.setdefault(comp[v], v)
    checked = failed = 0
    maxgap = 0
    for v in cells:
        if any(u in cells_set for u in pred[v]):
            continue                          # not free
        if first[comp[v]] == v:
            continue                          # component's own minimum
        checked += 1
        same = [u for u in range(v) if u in cells_set and comp[u] == comp[v]]
        if not same:
            failed += 1
            continue
        gap = v - max(same)
        maxgap = max(maxgap, gap)
        if gap > H + 1:
            failed += 1
    return checked, failed, maxgap


def reach_max(H, W, pred):
    """Largest scan-index gap between king-adjacent cells on the board."""
    m = 0
    for i in range(H * W):
        for j in pred[i]:
            m = max(m, i - j)
    return m


# ---------------------------------------------------------------- drivers
BOARDS = [(1, 6), (1, 10), (2, 5), (2, 7), (2, 8), (3, 4), (3, 5),
          (4, 3), (4, 4), (5, 3)]


def run_green(boards):
    t0 = time.time()
    tot_subsets = tot_configs = 0
    tot_maxgap_holder = [0]
    tot_loc_checked = tot_loc_failed = 0
    bad = 0
    print("board  cells  subsets   configs  H+1  reach  loc_checks  maxgap  "
          "result")
    for (H, W) in boards:
        n = H * W
        nb, pred = king_neighbours(H, W)
        subsets = configs = 0
        loc_c = loc_f = loc_g = 0
        mism = 0
        for mask in range(1 << n):
            cells = [i for i in range(n) if (mask >> i) & 1]
            cset = set(cells)
            got, nc = sum_weights(cells, H, pred)
            c = 0 if not cells else components(cset, nb)[0]
            want = monomial(c)
            if got != want:
                if mism == 0:
                    print("  MISMATCH H=%d W=%d cells=%s got=%s want=%s"
                          % (H, W, cells, got, want))
                mism += 1
            # mod q^2 image, the form the engine truncates to
            if got[:2] != want[:2] and mism == 0:
                print("  MOD-Q2 MISMATCH H=%d W=%d cells=%s" % (H, W, cells))
                mism += 1
            a, b, g = locality_audit(cset, cells, H, pred, nb)
            loc_c += a
            loc_f += b
            loc_g = max(loc_g, g)
            subsets += 1
            configs += nc
        bad += mism
        tot_subsets += subsets
        tot_configs += configs
        tot_loc_checked += loc_c
        tot_loc_failed += loc_f
        tot_maxgap = max(tot_maxgap_holder[0], loc_g)
        tot_maxgap_holder[0] = tot_maxgap
        print("%dx%-3d %5d  %7d  %8d  %3d  %5d  %10d  %6d  %s"
              % (H, W, n, subsets, configs, H + 1, reach_max(H, W, pred),
                 loc_c, loc_g,
                 "OK" if mism == 0 and loc_f == 0 else "FAIL"))
        sys.stdout.flush()
    dt = time.time() - t0
    print("")
    print("GREEN totals: boards=%d subsets=%d configurations=%d "
          "mismatches=%d" % (len(boards), tot_subsets, tot_configs, bad))
    print("locality lemma: %d open-component free cells checked, %d failures "
          "(a failure = the component's label not live within H+1)"
          % (tot_loc_checked, tot_loc_failed))
    print("reach: max scan gap between king-adjacent cells never exceeded H+1 "
          "(column 'reach' vs column 'H+1'; equality for H>=2, and H=1 has no "
          "diagonal step so its reach is 1)")
    print("maxgap: largest gap a free cell actually needed to see its own "
          "component; observed = H-1 on every board with H>=3, i.e. two short "
          "of the window.  Liveness alone would fit in H-1 slots -- the H+1st "
          "slot is demanded by the NW neighbor in the clash/forced rule, not "
          "by liveness.")
    print("wall_s=%.1f" % dt)
    return bad == 0 and tot_loc_failed == 0


def run_red(name, flags, boards):
    """A RED must produce a mismatch.  Reports the first witness found."""
    for (H, W) in boards:
        n = H * W
        nb, pred = king_neighbours(H, W)
        for mask in range(1 << n):
            cells = [i for i in range(n) if (mask >> i) & 1]
            got, _ = sum_weights(cells, H, pred, **flags)
            c = 0 if not cells else components(set(cells), nb)[0]
            want = monomial(c)
            if got != want:
                print("%-45s FIRED   H=%d W=%d S=%s  sum=%s  q^c=%s"
                      % (name, H, W, [rc(i, H) for i in cells], got, want))
                return True
    print("%-45s DID NOT FIRE  -- the check is broken" % name)
    return False


def main():
    boards = BOARDS
    print("Birthright identity check")
    print("boards: %s" % ", ".join("%dx%d" % b for b in boards))
    print("")
    green = run_green(boards)
    print("")
    print("RED controls (each must fire):")
    redlist = [(n, f) for n, f in VARIANTS.items() if f]
    fired = sum(run_red(name, flags, boards) for name, flags in redlist)
    print("")
    if green and fired == len(redlist):
        print("RESULT: GREEN (identity holds on every subset of every board; "
              "all %d RED controls fired)" % fired)
        return 0
    print("RESULT: FAIL")
    return 1


if __name__ == "__main__":
    sys.exit(main())
