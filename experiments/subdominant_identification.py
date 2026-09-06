#!/usr/bin/env python3
"""Is the (dir4, HV-convex) spectrum the union of two known spectra?

The question left open by results/subclasses.md: the 4-cone series'
subdominant exponential growth rate looks like the growth constant of the
truncated (0,1) descent block, and the unrestricted subdominant looks like it
is still present behind it.  results/subclasses.md measured that with
Aitken plus a two-exponential peel.  This measures it with
experiments/prony_spectrum.py, which reads every exponential in one solve, and
then does the identification arithmetic:

    spectrum(dir4, HV-convex)  ==?  spectrum(staircase)  U  spectrum(block)

Each row of the output is one claimed coincidence between two numbers measured
on two DIFFERENT series, with the digit agreement and the trusted-digit floor
of the weaker of the two.  A coincidence can only be asserted to the smaller of
the two trusted counts, however many digits happen to agree.

Usage: python3 experiments/subdominant_identification.py [--order 10]
                [--dps 1500] [--shift 50]
Target machine: gympie (laptop).  MEASURED: about 30 s at order 10 / dps 1500
over five 700-term series.  Nothing to resume.
"""
import argparse
import sys

from mpmath import mp, mpf, nstr

sys.path.insert(0, __file__.rsplit('/', 1)[0])
from prony_spectrum import prony, nearest_agree, selftest  # noqa: E402
from seriestools import read_terms, agree_digits  # noqa: E402

SERIES = {
    'dir4':  'results/mk_hvdir4_terms_n700.txt',
    'dir4asc': 'results/mk_hvdir4asc_terms_n700.txt',
    'dir4desc': 'results/mk_hvdir4desc_terms_n700.txt',
    'stair': 'results/mk_stair_terms_n700.txt',
    'hv':    'results/convex_area_terms_n700_king.txt',
    'hvmono': 'results/mk_hvmono_terms_n700.txt',
    'block': 'results/mk_dir4_descblock_n700.txt',
}


def spectrum(path, order, shift):
    a = read_terms(path)
    N = len(a)
    base = prony(a, order, N)
    alt_n = prony(a, order, N - shift)
    alt_k = prony(a, order + 1, N)
    out = []
    for i, z in enumerate(base):
        d1, d2 = nearest_agree(z, alt_n), nearest_agree(z, alt_k)
        out.append((z, max(0, min(d1, d2) - 2)))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--order', type=int, default=10)
    ap.add_argument('--dps', type=int, default=1500)
    ap.add_argument('--shift', type=int, default=50)
    ap.add_argument('--show', type=int, default=6)
    args = ap.parse_args()
    mp.dps = args.dps

    ok, msg = selftest()
    print(('ok   ' if ok else 'FAIL ') + msg)
    if not ok:
        return 1

    sp = {}
    for name, path in SERIES.items():
        sp[name] = spectrum(path, args.order, args.shift)
        print(f"\n## {name}  ({path})")
        for i, (z, t) in enumerate(sp[name][:args.show]):
            print(f"  lambda_{i + 1} = {nstr(z, max(min(t, 30), 6)):<34}"
                  f" trusted {t}")

    print("\n## claimed identifications")
    print("   'agree' = digits the two measured numbers share;  'bearable' =")
    print("   the smaller of the two trusted counts, which is all the")
    print("   coincidence can be asserted to however many digits agree.")
    print(f"\n{'claim':<48} {'agree':>6} {'bearable':>9}")
    claims = [
        # the decisive one: the complementary halves have the two spectra
        ('lambda_1(dir4desc) == lambda_1(block)', ('dir4desc', 0), ('block', 0)),
        ('lambda_2(dir4desc) == lambda_2(block)', ('dir4desc', 1), ('block', 1)),
        ('lambda_3(dir4desc) == lambda_3(block)', ('dir4desc', 2), ('block', 2)),
        ('lambda_1(dir4asc)  == lambda_1(stair)', ('dir4asc', 0), ('stair', 0)),
        ('lambda_2(dir4asc)  == lambda_2(stair)', ('dir4asc', 1), ('stair', 1)),
        ('lambda_3(dir4asc)  == lambda_3(stair)', ('dir4asc', 2), ('stair', 2)),
        ('lambda_4(dir4asc)  == lambda_4(stair)', ('dir4asc', 3), ('stair', 3)),
        # and the whole series' spectrum is their interleaving
        ('lambda_1(dir4) == lambda_1(stair)', ('dir4', 0), ('stair', 0)),
        ('lambda_2(dir4) == lambda_1(block)', ('dir4', 1), ('block', 0)),
        ('lambda_3(dir4) == lambda_2(stair)', ('dir4', 2), ('stair', 1)),
        ('lambda_4(dir4) == lambda_2(block)', ('dir4', 3), ('block', 1)),
        ('lambda_5(dir4) == lambda_3(stair)', ('dir4', 4), ('stair', 2)),
        ('lambda_6(dir4) == lambda_4(stair)', ('dir4', 5), ('stair', 3)),
        # the unrestricted rungs, for Table B
        ('lambda_2(stair) == lambda_2(hv)', ('stair', 1), ('hv', 1)),
        ('lambda_2(stair) == lambda_2(hvmono)', ('stair', 1), ('hvmono', 1)),
    ]
    for label, (an, ai), (bn, bi) in claims:
        if ai >= len(sp[an]) or bi >= len(sp[bn]):
            print(f"{label:<48} {'n/a':>6}")
            continue
        x, tx = sp[an][ai]
        y, ty = sp[bn][bi]
        print(f"{label:<48} {agree_digits(x, y):>6} {min(tx, ty):>9}")

    print("\n## negative controls -- these must NOT match")
    neg = [
        ('block lambda_1 vs every root of dir4asc', ('block', 0), 'dir4asc'),
        ('block lambda_2 vs every root of dir4asc', ('block', 1), 'dir4asc'),
        ('stair lambda_2 vs every root of dir4desc', ('stair', 1), 'dir4desc'),
    ]
    for label, (an, ai), bn in neg:
        x, _ = sp[an][ai]
        best = nearest_agree(x, [z for z, _ in sp[bn]])
        verdict = 'ok (absent)' if best < 3 else 'PRESENT -- claim broken'
        print(f"{label:<48} best {best:>3} digits   {verdict}")

    print("\n## Table B's ratios, recomputed from the spectrum")
    mu = sp['dir4'][0][0]
    for name, idx in (('dir4', 1), ('dir4asc', 1), ('stair', 1), ('hv', 1),
                      ('hvmono', 1)):
        z, t = sp[name][idx]
        base = sp[name][0][0]
        r = z / base
        print(f"  {name:<7} |lambda_2/lambda_1| = "
              f"{nstr(abs(r), max(min(t, 24), 6))}   (trusted {t})")
    z3, t3 = sp['dir4'][2]
    print(f"  dir4    |lambda_3/lambda_1| = "
          f"{nstr(abs(z3 / mu), max(min(t3, 24), 6))}   (trusted {t3})")
    return 0


if __name__ == '__main__':
    sys.exit(main())
