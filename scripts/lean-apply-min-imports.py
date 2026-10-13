#!/usr/bin/env python3
"""Rewrite each polyplets module's import block from scripts/lean-min-imports.sh
output: keep the module's `import Polyplets.*` lines, replace its Mathlib
imports by the set `#min_imports` reported (polyplets/build/mi/<Module>.imports).
Modules with no report are left alone. Prints a one-line diff summary per module."""
import os, re, sys
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'polyplets')
os.chdir(ROOT)
mods = sys.argv[1:]
if not mods:
    for dp, _, fs in os.walk('Polyplets'):
        for f in fs:
            if f.endswith('.lean'):
                mods.append(os.path.relpath(os.path.join(dp, f), 'Polyplets')[:-5].replace('/', '.'))
mods.sort()
for m in mods:
    rep = f'build/mi/{m.replace(".", "_")}.imports'
    if not os.path.exists(rep) or os.path.getsize(rep) == 0:
        print(f'{m}: no report'); continue
    want = [l.strip() for l in open(rep) if l.strip()]
    want = [l for l in want if l.startswith('import Mathlib') and 'MinImports' not in l]
    path = f'Polyplets/{m.replace(".", "/")}.lean'
    src = open(path).read()
    lines = src.split('\n')
    # import block: the maximal run of lines starting with `import ` after the header comment
    first = next(i for i, l in enumerate(lines) if l.startswith('import '))
    last = first
    while last + 1 < len(lines) and lines[last + 1].startswith('import '):
        last += 1
    old_block = lines[first:last + 1]
    poly = [l for l in old_block if l.startswith('import Polyplets')]
    old_math = sorted(l for l in old_block if not l.startswith('import Polyplets'))
    new_block = sorted(want) + poly
    if sorted(want) == old_math:
        print(f'{m}: unchanged'); continue
    lines[first:last + 1] = new_block
    open(path, 'w').write('\n'.join(lines))
    print(f'{m}: {len(old_math)} -> {len(want)} Mathlib imports')
