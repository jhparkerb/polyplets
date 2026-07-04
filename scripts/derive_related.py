#!/usr/bin/env python3
"""Derive the related polyplet sequences from Fixed (A006770) + symmetric
fixed-point counts, via Burnside:

    Free      (A030222) = (Fixed + 2*R90 + R180 + 2*H + 2*D) / 8
    OneSided  (A030233) = (Fixed + 2*R90 + R180) / 4
    Bilateral (A030234) = (H + D) / 2
    Asym      (A030235) = Free - Bilateral
    FreeNonPoly (A194596) = Free - A000105

H = hmirror (axis-parallel mirror), D = dmirror (diagonal mirror).

Validates every computed term against the known OEIS terms (parsed from
oeis/A*.txt) before emitting. Usage: derive_related.py <symdir>  e.g. runs/sym22
"""
import sys, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def load_nv(path):
    """Parse 'n value' lines (b-file / triangle), skipping comments. -> {n:int}."""
    d = {}
    with open(path) as f:
        for ln in f:
            ln = ln.strip()
            if not ln or ln.startswith('#'):
                continue
            a, b = ln.split()[:2]
            d[int(a)] = int(b)
    return d

def load_oeis_terms(anum):
    """Parse the %S/%T/%U data lines of oeis/<anum>.txt -> {n:int} (offset from %O)."""
    path = os.path.join(ROOT, 'oeis', anum + '.txt')
    body, offset = '', 1
    with open(path) as f:
        for ln in f:
            m = re.match(r'%[STU] ' + anum + r' (.*)', ln)
            if m:
                body += m.group(1)
            mo = re.match(r'%O ' + anum + r' (-?\d+)', ln)
            if mo:
                offset = int(mo.group(1))
    vals = [int(x) for x in body.replace(' ', '').rstrip(',').split(',') if x]
    return {offset + i: v for i, v in enumerate(vals)}

def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: derive_related.py <symdir>  e.g. runs/sym24")
    symdir = os.path.join(ROOT, sys.argv[1])

    fixed = load_nv(os.path.join(ROOT, 'results/ns_a34/triangle.txt'))
    a105  = load_nv(os.path.join(ROOT, 'fixtures/b000105.txt'))  # free polyominoes
    R90  = load_nv(os.path.join(symdir, 'r90.out'))
    R180 = load_nv(os.path.join(symdir, 'r180.out'))
    H    = load_nv(os.path.join(symdir, 'hmirror.out'))
    # dmirror is the shortest-reach type; without it only OneSided derives.
    dpath = os.path.join(symdir, 'dmirror.out')
    D = load_nv(dpath) if os.path.exists(dpath) else {}
    g = lambda dct, n: dct.get(n, 0)   # missing symmetric count => 0
    # r90 legitimately has no n=2,3 (mod 4) lines (no 90-deg-fixed animals
    # there), so g's 0 default is exact for it; every other type must be
    # PRESENT to cap its dependents, never defaulted.

    # per-sequence reach: OneSided needs r90+r180; the rest also need H and D
    nmax_one = min(max(R180), max(fixed))
    nmax = min(nmax_one, max(H), max(D)) if D else 0

    known = {a: load_oeis_terms(a) for a in
             ('A030222', 'A030233', 'A030234', 'A030235', 'A194596')}

    seqs = {a: {} for a in known}
    bad = []
    for n in range(1, max(nmax, nmax_one) + 1):
        fx = g(fixed, n)
        num_one = fx + 2*g(R90, n) + g(R180, n)
        assert num_one % 4 == 0, f"OneSided numerator not /4 at n={n}: {num_one}"
        seqs['A030233'][n] = num_one // 4
        if n <= nmax:
            num_free = num_one + 2*g(H, n) + 2*g(D, n)
            assert num_free % 8 == 0, f"Free numerator not /8 at n={n}: {num_free}"
            assert (g(H, n) + g(D, n)) % 2 == 0, f"(H+D) odd at n={n}"
            free = num_free // 8
            seqs['A030222'][n] = free
            seqs['A030234'][n] = (g(H, n) + g(D, n)) // 2
            seqs['A030235'][n] = free - seqs['A030234'][n]
            seqs['A194596'][n] = free - g(a105, n)
        for a in known:
            if n in seqs[a] and n in known[a] and known[a][n] != seqs[a][n]:
                bad.append((a, n, seqs[a][n], known[a][n]))

    if bad:
        print("VALIDATION FAILED:")
        for a, n, got, exp in bad:
            print(f"  {a}(n={n}): computed {got} != known {exp}")
        sys.exit(1)

    checked = sum(1 for a in known for n in seqs[a] if n in known[a])
    print(f"VALIDATE OK: {checked} computed terms match known OEIS terms "
          f"(nmax={nmax}, nmax_onesided={nmax_one}, "
          f"symdir={os.path.relpath(symdir, ROOT)})")
    print()
    names = {'A030222': 'free', 'A030233': 'one-sided', 'A030234': 'bilateral',
             'A030235': 'asymmetric', 'A194596': 'free-non-polyomino'}
    for a in ('A030222', 'A030233', 'A030234', 'A030235', 'A194596'):
        if not seqs[a]:
            print(f"{a} ({names[a]}): not derivable (no dmirror counts)")
            continue
        reach = max(seqs[a])
        newn = [n for n in seqs[a] if n not in known[a]]
        tag = f"NEW n={newn}" if newn else "(no new terms past known)"
        print(f"{a} ({names[a]}): through n={reach}  {tag}")
        for n in sorted(seqs[a]):
            mark = '  <- NEW' if n not in known[a] else ''
            if n >= reach - 3 or mark:
                print(f"    {n} {seqs[a][n]}{mark}")

if __name__ == '__main__':
    main()
