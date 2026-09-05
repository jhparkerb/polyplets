#!/usr/bin/env python3
"""Reconstruct an exact Motley C_H row from its mod-p residue rows.

WHY THIS FILE EXISTS.  The CRT reconstruction that turned Confetti's five
residue rows into the banked exact C_18 lived inside a heredoc in
scripts/dalby_confetti_h18.sh -- a runner that executes on dalby and that
`make` never touches.  That is the same defect scripts/cutcount_assembly_gate.py
was written to fix one level up, and it means the next ladder has nothing to
run.  This is that code, extracted, generalised over the prime count, and
given a self-test against the banked Confetti data.

THE METHOD.  Run the engine once per prime.  Reconstruct C_H(n) by CRT over
all but one of them; the LAST prime is held out, its residue PREDICTED from
the reconstruction, and compared.  A held-out prime that agrees at every n is
the check that the reconstruction is right rather than merely consistent --
an error inside the CRT set can hide, an error that also matches an unused
prime cannot (short of a multiple of that prime, hence 2^16 odds per cell).

FAIL-CLOSED, all of these exit non-zero:
  * a reconstruction >= the product of the CRT primes (silent wraparound),
  * a held-out residue that does not match,
  * a missing residue row, or fewer than two primes,
  * zero cells compared.

Usage:
  motley_crt.py --dir DIR --height H [--nmax N] [--out FILE]
        DIR holds C<H>.p<prime>.out, one per prime, as motley_par --modp writes
        them.  Primes are read from the filenames.  Writes the exact row as
        "n value" lines.

  motley_crt.py --selftest
        Reconstructs C_18 from results/cutcount_b1/residues/ (Confetti, five
        primes) and C_19 from results/cutcount_b1/residues41/ (the Nmax-41
        ladder, nine primes), requires each to equal its banked exact row
        exactly, then checks at both heights that a corrupted residue is caught.
"""

import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def read_row(path):
    out = {}
    with open(path) as fh:
        for line in fh:
            parts = line.split()
            if len(parts) == 2:
                out[int(parts[0])] = int(parts[1])
    if not out:
        sys.exit(f"FATAL empty_row {path}")
    return out


def find_residues(d, H):
    """{prime: {n: residue}} from C<H>.p<prime>.out in `d`."""
    got = {}
    for fn in sorted(os.listdir(d)):
        m = re.fullmatch(rf"C{H}\.p(\d+)\.out", fn)
        if m:
            got[int(m.group(1))] = read_row(os.path.join(d, fn))
    return got


def crt(residues, primes):
    """Garner: the unique 0 <= x < prod(primes) with x = residues[i] mod p_i."""
    x, mod = 0, 1
    for r, p in zip(residues, primes):
        # solve x + mod*t = r (mod p)
        t = ((r - x) * pow(mod, -1, p)) % p
        x += mod * t
        mod *= p
    return x, mod


def reconstruct(res, height, nmax=None):
    primes = sorted(res)
    if len(primes) < 2:
        sys.exit(f"FATAL too_few_primes {len(primes)} (need >= 2: one held out)")
    crt_primes, heldout = primes[:-1], primes[-1]
    ns = sorted(set.intersection(*(set(res[p]) for p in primes)))
    if nmax is not None:
        ns = [n for n in ns if n <= nmax]
    if not ns:
        sys.exit("FATAL no_common_n across the residue rows")

    prod = 1
    for p in crt_primes:
        prod *= p
    exact, checked = {}, 0
    for n in ns:
        x, mod = crt([res[p][n] for p in crt_primes], crt_primes)
        if x >= prod:
            sys.exit(f"FATAL crt_overflow n={n}")
        if x % heldout != res[heldout][n]:
            sys.exit(f"FATAL heldout_mismatch n={n}: predicted {x % heldout}, "
                     f"measured {res[heldout][n]} mod {heldout}")
        exact[n] = x
        checked += 1
    if checked == 0:
        sys.exit("FATAL zero_cells_compared")
    return exact, crt_primes, heldout, checked


def selftest_height(H, res_dir, banked, min_common, label):
    """Reconstruct C_H from the banked residue rows, require equality with the
    banked exact row, then corrupt one residue and require the held-out prime
    to catch it.  One height, one posture; called once per banked ladder."""
    res = find_residues(res_dir, H)
    if len(res) < 2:
        sys.exit(f"FATAL selftest: found {len(res)} residue rows for C_{H} in {res_dir}")
    exact, crt_p, held, n = reconstruct(res, H)
    want = read_row(banked)
    bad = [k for k in exact if k in want and exact[k] != want[k]]
    if bad:
        sys.exit(f"SELFTEST RED ({label}): {len(bad)} cells differ from the "
                 f"banked row, first n={bad[0]}")
    common = sum(1 for k in exact if k in want)
    if common < min_common:
        sys.exit(f"SELFTEST RED ({label}): only {common} cells compared -- vacuous")
    print(f"selftest {label}: C_{H} reconstructed from {len(crt_p)} primes, held "
          f"out {held}, {n} cells; {common} match the banked row exactly")

    # RED control: corrupt one residue and require the held-out check to fire.
    p0 = crt_p[0]
    res[p0] = dict(res[p0])
    some_n = sorted(res[p0])[len(res[p0]) // 2]
    res[p0][some_n] = (res[p0][some_n] + 1) % p0
    pid = os.fork()
    if pid == 0:
        sys.stdout = sys.stderr = open(os.devnull, "w")
        try:
            reconstruct(res, H)
        except SystemExit as e:
            os._exit(1 if e.code else 0)
        os._exit(0)
    _, status = os.waitpid(pid, 0)
    if os.WEXITSTATUS(status) == 0:
        sys.exit(f"SELFTEST RED ({label}): a corrupted residue was NOT caught")
    print(f"RED control GREEN ({label}): a corrupted residue is caught by the "
          f"held-out prime")


def selftest():
    """Both banked ladders.  Confetti (H = 18, five ~31-bit primes, Nmax 40)
    and the Nmax-41 ladder (H = 19, nine ~16-bit primes, banked 2026-09-05 per
    AUDIT-2026-09-02 M3).  Until then this selftest covered C_18 only and the
    nineteen held-out verdicts of the ladder were a README sentence."""
    cb = os.path.join(ROOT, "results", "cutcount_b1")
    selftest_height(18, os.path.join(cb, "residues"),
                    os.path.join(cb, "rows", "C18.out"), 30, "Confetti")
    selftest_height(19, os.path.join(cb, "residues41"),
                    os.path.join(cb, "rows41", "C19.out"), 41, "Nmax-41 ladder")


def main():
    if "--selftest" in sys.argv:
        selftest()
        return
    def opt(name, default=None):
        return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else default
    d = opt("--dir")
    H = opt("--height")
    if not d or not H:
        sys.exit(__doc__)
    H = int(H)
    nmax = opt("--nmax")
    res = find_residues(d, H)
    if not res:
        sys.exit(f"FATAL no C{H}.p*.out rows in {d}")
    exact, crt_p, held, n = reconstruct(res, H, int(nmax) if nmax else None)
    out = opt("--out", os.path.join(d, f"C{H}.out"))
    with open(out, "w") as fh:
        for k in sorted(exact):
            fh.write(f"{k} {exact[k]}\n")
    print(f"C_{H}: {n} cells from {len(crt_p)} primes, held-out {held} "
          f"predicted correctly at every n -> {out}")


if __name__ == "__main__":
    main()
