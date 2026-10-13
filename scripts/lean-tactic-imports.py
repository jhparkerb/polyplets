#!/usr/bin/env python3
"""Add the Mathlib tactic imports a module's proofs use. `#min_imports` tracks
the constants a declaration elaborates to, not the tactic frontends a proof
invokes, so after replacing `import Mathlib` a module can fail with
"unknown tactic". This scans each module for tactic names and adds the
corresponding Mathlib tactic module when missing; unused ones are pruned by
`lake exe shake` afterwards. Usage: lean-tactic-imports.py [Module ...]."""
import os, re, sys
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'polyplets')
os.chdir(ROOT)
TACTICS = {
    r'\b(ring|ring_nf|ring1)\b': 'Mathlib.Tactic.Ring',
    r'\b(linarith|nlinarith)\b': 'Mathlib.Tactic.Linarith',
    r'\bpositivity\b': 'Mathlib.Tactic.Positivity',
    r'\bnorm_num\b': 'Mathlib.Tactic.NormNum',
    r'\bfield_simp\b': 'Mathlib.Tactic.FieldSimp',
    r'\bfin_cases\b': 'Mathlib.Tactic.FinCases',
    r'\binterval_cases\b': 'Mathlib.Tactic.IntervalCases',
    r'\blinear_combination\b': 'Mathlib.Tactic.LinearCombination',
    r'(?<![\w.])group\b(?!\s*:)': 'Mathlib.Tactic.Group',
    r'(?<![\w.])abel\b': 'Mathlib.Tactic.Abel',
    r'\bpush Not\b': 'Mathlib.Tactic.Push',
    r'\bsimp_rw\b': 'Mathlib.Tactic.SimpRw',
    r'\bgcongr\b': 'Mathlib.Tactic.GCongr',
    r'(?<![\w.])set\s+\w+\s*:': 'Mathlib.Tactic.Set',
    r'\bfilter_upwards\b': 'Mathlib.Order.Filter.Basic',
    r'\bchoose\b': 'Mathlib.Tactic.Choose',
    r'deriving[^\n]*Fintype': 'Mathlib.Tactic.DeriveFintype',
}
def strip_comments(s):
    s = re.sub(r'/-.*?-/', ' ', s, flags=re.S)
    return re.sub(r'--[^\n]*', ' ', s)
mods = sys.argv[1:]
if not mods:
    for dp, _, fs in os.walk('Polyplets'):
        for f in fs:
            if f.endswith('.lean'):
                mods.append(os.path.relpath(os.path.join(dp, f), 'Polyplets')[:-5].replace('/', '.'))
mods.sort()
for m in mods:
    path = f'Polyplets/{m.replace(".", "/")}.lean'
    src = open(path).read()
    code = strip_comments(src)
    need = set()
    for pat, imp in TACTICS.items():
        if re.search(pat, code):
            need.add(imp)
    lines = src.split('\n')
    first = next(i for i, l in enumerate(lines) if l.startswith('import '))
    last = first
    while last + 1 < len(lines) and lines[last + 1].startswith('import '):
        last += 1
    block = lines[first:last + 1]
    have = {l[len('import '):] for l in block}
    add = sorted(i for i in need if i not in have)
    if not add:
        continue
    math = sorted([l for l in block if not l.startswith('import Polyplets')] + [f'import {i}' for i in add])
    poly = [l for l in block if l.startswith('import Polyplets')]
    lines[first:last + 1] = math + poly
    open(path, 'w').write('\n'.join(lines))
    print(f'{m}: + {", ".join(add)}')
