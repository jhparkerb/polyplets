#!/usr/bin/env python3
"""king twigs, level 1 — machine verification of the twig-scheme bounds.

Thread: king twigs (docs/king-twigs-plan.md (deleted), Phases 0-2).

Verifies, over ALL fixed animals up to --maxn:
  1. The enumeration itself (A006770 / A001168 prefixes).
  2. counterexample: the crude-bound decision tree of
     docs/proofs/polyplet-upper-bound.md ("only ahead-neighbours newly enter
     the frontier") MISSES re-entrant animals — reachable count < a(n).
  3. Scheme D0 (eager, parent-frame slots, no deferral): encode/decode
     round-trip, weight identity (n-1 opens, n letters), alphabet census.
     Expected alphabet = all masks of the 5-slot frame -> (1+x)^5,
     bound 5^5/4^4 = 12.207 — the SOUND derivation of the banked constant.
  4. Scheme D1 (D0 + KR-style adjacency deferral) MUST FAIL coverage:
     a deferred cell c is adjacent to both u and the child e it is deferred
     to, hence c is in N(e) cap N(u) = e's shared set, hence NOT in e's
     slot frame — nobody ever opens c. The harness demonstrates the block
     on a 3-cell witness. This is the structural reason the KR/BS gain
     does not transfer to king adjacency at first-order contexts (KR's
     deferred cell is DIAGONAL from u, outside N(u), on the square lattice).
  5. Square-lattice controls in the same harness: D0_sq alphabet (1+x)^3
     (Eden 27/4); extractor gate: KR's Sigma w = y(1+2x+2x^2) must give
     2+2sqrt(2) to 8+ digits.
  6. RED control: D0 with a slot silently dropped from the diagonal frame
     must FAIL (coverage or round-trip) — the harness must catch it.

Bound extraction: for weight polynomial h(x) = Sigma_letters x^{opens},
lambda <= min_{b>0} h(b)/b (Cauchy bound on [x^{n-1}] h(x)^n; root letters
are a constant factor). Certified at an explicit rational b in exact
arithmetic (Fraction), printed as an exact fraction >= the bound.

Run from repo root (on ayr): python3 experiments/kingtwigs/l1_schemes.py
"""
import sys
from fractions import Fraction
from itertools import combinations

# ---------- lattice definitions ----------
KING = [(1,0),(1,1),(0,1),(-1,1),(-1,0),(-1,-1),(0,-1),(1,-1)]
SQUARE = [(1,0),(0,1),(-1,0),(0,-1)]

def neigh(c, dirs):
    return [(c[0]+d[0], c[1]+d[1]) for d in dirs]

def adjacent(a, b, dirs):
    return (b[0]-a[0], b[1]-a[1]) in dirs

# scan order: top->bottom (larger y first), then left->right
def skey(c):
    return (-c[1], c[0])

# ---------- animal enumeration (translation-normalized) ----------
def normalize(cells):
    m = min(cells, key=skey)
    return frozenset((c[0]-m[0], c[1]-m[1]) for c in cells)

def enumerate_animals(maxn, dirs):
    """All fixed animals as frozensets, per size. Naive grow+dedupe."""
    levels = [set(), {normalize([(0, 0)])}]
    for n in range(2, maxn+1):
        cur = set()
        for a in levels[n-1]:
            grown = set()
            for c in a:
                for nb in neigh(c, dirs):
                    if nb not in a:
                        grown.add(nb)
            for g in grown:
                cur.add(normalize(a | {g}))
        levels.append(cur)
    return levels

# ---------- twig frames ----------
# For parent direction pd (direction FROM u TO its parent), the frame is:
#   known: parent cell + shared = N(u) cap N(parent)  (2 shared for diagonal
#   parents, 4 for orthogonal), unknown slots = the rest, listed in an order
#   that maps the slot adjacency onto the canonical graph
#   path p0-p1-p2-p3-p4 with chord p1-p3 (diagonal parents; 5 slots) or its
#   sub-path p0-p1-p2 images (orthogonal parents; 3 slots -> positions 0,1,2).
def build_frames(dirs):
    frames = {}
    for pd in dirs:
        parent = pd
        shared = [d for d in dirs
                  if d != pd and (d[0]-pd[0], d[1]-pd[1]) in dirs]
        unknown = [d for d in dirs if d != pd and d not in shared]
        # order unknown slots along their adjacency path: endpoints first
        g = {d: [e for e in unknown if e != d and (e[0]-d[0], e[1]-d[1]) in dirs]
             for d in unknown}
        if not unknown:
            frames[pd] = []
            continue
        ends = sorted([d for d in unknown if len(g[d]) <= 1])
        order = [ends[0]] if ends else [sorted(unknown)[0]]
        seen = {order[0]}
        # walk the path greedily (slot graphs here are paths + one chord;
        # walk by fewest-unseen-neighbours to follow the path spine)
        while len(order) < len(unknown):
            last = order[-1]
            nxt = [e for e in g[last] if e not in seen]
            if not nxt:
                rest = [e for e in unknown if e not in seen]
                nxt = [sorted(rest)[0]]
            nxt = sorted(nxt, key=lambda e: len([f for f in g[e] if f not in seen]))
            order.append(nxt[0]); seen.add(nxt[0])
        frames[pd] = order
    return frames

# ---------- schemes ----------
class Scheme:
    """Twig scheme: FIFO processing; per processed cell u, walk the frame
    slots in order; open slot cells that are in P and unopened, unless the
    deferral rule suppresses them. Letter = tuple of opened-flags over the
    frame slots. Root uses the full direction list as its frame."""
    def __init__(self, dirs, defer_adjacent, drop_slot=False):
        self.dirs = dirs
        self.frames = build_frames(dirs)
        if drop_slot:  # RED control: silently truncate diagonal frames
            self.frames = {pd: (f[:-1] if len(f) == 5 else f)
                           for pd, f in self.frames.items()}
        self.defer_adjacent = defer_adjacent

    def _step_mask(self, u, frame, P, opened):
        mask = []
        opened_now = []
        for d in frame:
            c = (u[0]+d[0], u[1]+d[1])
            bit = False
            if c in P and c not in opened:
                suppress = False
                if self.defer_adjacent:
                    for e in opened_now:
                        if adjacent(c, e, self.dirs):
                            suppress = True
                            break
                if not suppress:
                    bit = True
                    opened_now.append(c)
            mask.append(bit)
        return tuple(mask), opened_now

    def encode(self, P):
        """-> (root_letter, [(parent_dir, letter), ...]) in process order."""
        root = min(P, key=skey)
        opened = {root: None}          # cell -> parent direction (u->parent)
        queue = [root]
        letters = []
        qi = 0
        while qi < len(queue):
            u = queue[qi]; qi += 1
            pd = opened[u]
            frame = self.dirs if pd is None else self.frames[pd]
            mask, opened_now = self._step_mask(u, frame, P, opened)
            for c in opened_now:
                # parent direction points from c back to u
                opened[c] = (u[0]-c[0], u[1]-c[1])
                queue.append(c)
            letters.append((pd, mask))
        assert len(opened) == len(P), "coverage failure: %r" % (sorted(P),)
        return tuple(letters)

    def decode(self, letters):
        root = (0, 0)
        opened = {root: None}
        queue = [root]
        qi = 0
        for pd, mask in letters:
            if qi >= len(queue):
                return None
            u = queue[qi]; qi += 1
            if opened[u] != pd:
                return None
            frame = self.dirs if pd is None else self.frames[pd]
            if len(mask) != len(frame):
                return None
            for d, bit in zip(frame, mask):
                if bit:
                    c = (u[0]+d[0], u[1]+d[1])
                    if c in opened:
                        return None
                    opened[c] = (u[0]-c[0], u[1]-c[1])
                    queue.append(c)
        return normalize(set(opened))

# ---------- the broken crude-bound decision tree ----------
def crude_reachable(P, dirs):
    """docs/proofs/polyplet-upper-bound.md scheme: frontier grows ONLY by
    ahead-in-scan-order neighbours of included cells. True iff every cell of
    P ever enters the frontier (i.e. P is generatable by that tree)."""
    ahead = [d for d in dirs if skey(d) > skey((0, 0))]
    root = min(P, key=skey)
    frontier = [root]
    seen = {root}
    included = set()
    qi = 0
    while qi < len(frontier):
        c = frontier[qi]; qi += 1
        if c in P:
            included.add(c)
            for d in ahead:
                nb = (c[0]+d[0], c[1]+d[1])
                if nb not in seen:
                    seen.add(nb)
                    frontier.append(nb)
    return included == P

# ---------- bound extraction ----------
def poly_from_alphabet(alphabet):
    """alphabet: set of (pd_class, mask) -> dict degree -> count, over
    DISTINCT letters (masks in the shared 5-bit space; pd folded per class)."""
    h = {}
    for mask in alphabet:
        d = sum(mask)
        h[d] = h.get(d, 0) + 1
    return h

def h_eval(h, b):
    return sum(c * b**d for d, c in h.items())

def certify_min(h, lo=Fraction(1, 100), hi=Fraction(3, 1), steps=2000,
                rounds=5):
    """Exact-rational scan + local refinement for a near-optimal b.
    Returns (b, h(b)/b) exact — h(b)/b is a rigorous upper bound at any b."""
    best = None
    for r in range(rounds):
        step = (hi - lo) / steps
        for i in range(steps + 1):
            b = lo + step * i
            if b <= 0:
                continue
            v = h_eval(h, b) / b
            if best is None or v < best[1]:
                best = (b, v)
        lo = max(best[0] - step, Fraction(1, 10**9))
        hi = best[0] + step
    return best

# ---------- main ----------
def run(maxn_king=8, maxn_sq=9):
    ok = True

    def check(name, cond, detail=""):
        nonlocal ok
        print("%-58s %s %s" % (name, "PASS" if cond else "FAIL", detail))
        if not cond:
            ok = False

    print("== enumeration self-check ==")
    king = enumerate_animals(maxn_king, KING)
    a6770 = [1, 4, 20, 110, 638, 3832, 23592, 147941]
    got = [len(king[n]) for n in range(1, maxn_king+1)]
    check("king counts = A006770[1..%d]" % maxn_king,
          got == a6770[:maxn_king], str(got))
    sq = enumerate_animals(maxn_sq, SQUARE)
    a1168 = [1, 2, 6, 19, 63, 216, 760, 2725, 9910]
    gots = [len(sq[n]) for n in range(1, maxn_sq+1)]
    check("square counts = A001168[1..%d]" % maxn_sq,
          gots == a1168[:maxn_sq], str(gots))

    print("\n== crude-bound decision tree (docs/proofs/polyplet-upper-bound.md) ==")
    missed = {n: sum(0 if crude_reachable(P, KING) else 1 for P in king[n])
              for n in range(1, maxn_king+1)}
    print("   unreachable animals by n:", missed)
    witness = frozenset([(0,3),(0,2),(0,1),(0,0),(1,0),(2,0),(3,0),(3,1)])
    check("hand witness (re-entrant hook) is missed",
          not crude_reachable(witness, KING))
    check("scheme misses animals from n=%d on (proof broken)"
          % min((n for n in missed if missed[n]), default=0),
          any(missed.values()))

    frames = build_frames(KING)
    diag_frames = {pd: f for pd, f in frames.items() if pd[0] and pd[1]}
    orth_frames = {pd: f for pd, f in frames.items() if not (pd[0] and pd[1])}
    check("diagonal frames have 5 slots",
          all(len(f) == 5 for f in diag_frames.values()))
    check("orthogonal frames have 3 slots",
          all(len(f) == 3 for f in orth_frames.values()))
    # canonical slot-graph shape: path 0-1-2-3-4 plus chord 1-3
    shapes = set()
    for pd, f in diag_frames.items():
        edges = frozenset((i, j) for i, j in combinations(range(5), 2)
                          if adjacent(f[i], f[j], KING))
        shapes.add(edges)
    want = frozenset({(0,1),(1,2),(2,3),(3,4),(1,3)})
    check("all diagonal slot graphs are path+chord(1,3)",
          shapes == {want}, str(shapes) if shapes != {want} else "")

    print("\n== king scheme D0 (eager, no deferral) ==")
    s = Scheme(KING, False)
    alpha = set()
    weight_ok = True
    seen_codes = {}
    inj_ok = True
    rt_ok = True
    for n in range(1, maxn_king+1):
        for P in king[n]:
            code = s.encode(P)
            opens = sum(sum(m) for _, m in code)
            if opens != n - 1 or len(code) != n:
                weight_ok = False
            if code in seen_codes and seen_codes[code] != P:
                inj_ok = False
            seen_codes[code] = P
            if s.decode(code) != P:
                rt_ok = False
            for pd, m in code:
                if pd is not None:
                    alpha.add(m)
    check("decode(encode(P)) == P for all n<=%d" % maxn_king, rt_ok)
    check("codes pairwise distinct", inj_ok)
    check("weight identity (n-1 opens, n letters)", weight_ok)
    # orthogonal letters embed in 5-bit space at positions 0,1,2
    alpha5 = set(m if len(m) == 5 else tuple(m) + (False, False)
                 for m in alpha)
    h = poly_from_alphabet(alpha5)
    check("alphabet census = (1+x)^5",
          h == {0: 1, 1: 5, 2: 10, 3: 10, 4: 5, 5: 1}, str(h))
    b, v = certify_min(h)
    print("   certified: lambda <= h(b)/b = %s = %.9f at b = %s"
          % (v, float(v), b))
    check("D0 bound = 5^5/4^4 to 4 digits", abs(float(v) - 3125/256) < 5e-4)

    print("\n== king scheme D1 (KR-style deferral): the structural block ==")
    s1 = Scheme(KING, True)
    blocked = False
    wit = None
    for n in range(2, 5):
        for P in king[n]:
            try:
                s1.encode(P)
            except AssertionError:
                blocked = True
                wit = sorted(P)
                break
        if blocked:
            break
    check("deferral scheme fails coverage (KR trick blocked on king)",
          blocked, "witness %s" % (wit,))

    print("\n== RED control: D0 with a dropped slot must be caught ==")
    s_bad = Scheme(KING, False, drop_slot=True)
    caught = False
    for n in range(2, 7):
        for P in king[n]:
            try:
                if s_bad.decode(s_bad.encode(P)) != P:
                    caught = True
                    break
            except AssertionError:
                caught = True
                break
        if caught:
            break
    check("harness catches the slot-dropped scheme", caught)

    print("\n== square controls ==")
    s = Scheme(SQUARE, False)
    alpha = set()
    rt_ok = True
    for n in range(1, maxn_sq+1):
        for P in sq[n]:
            code = s.encode(P)
            if s.decode(code) != P:
                rt_ok = False
            for pd, m in code:
                if pd is not None:
                    alpha.add(m)
    check("square D0 round-trip", rt_ok)
    h = poly_from_alphabet(alpha)
    check("square D0 alphabet = (1+x)^3", h == {0: 1, 1: 3, 2: 3, 3: 1}, str(h))
    b, v = certify_min(h)
    print("   certified: lambda_2 <= %s = %.9f (Eden 27/4 = 6.75)" % (v, float(v)))
    check("square D0 bound ~ 27/4", abs(float(v) - 6.75) < 1e-3)
    # extractor gate on KR's twig polynomial
    h_kr = {0: 1, 1: 2, 2: 2}
    b, v = certify_min(h_kr)
    import math
    check("extractor gate: KR 1+2x+2x^2 -> 2+2*sqrt(2) to 8 digits",
          abs(float(v) - (2 + 2*math.sqrt(2))) < 5e-8, "%.10f" % float(v))

    print("\nOVERALL:", "GREEN" if ok else "RED")
    return 0 if ok else 1

if __name__ == "__main__":
    maxn = int(sys.argv[1]) if len(sys.argv) > 1 else 8
    sys.exit(run(maxn_king=maxn))
