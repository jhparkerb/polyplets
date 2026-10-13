#!/usr/bin/env python3
"""One-off: convert polyplets/Polyplets/Upper/BuiData{2,3}.lean from the
list-based `RatCert` (rules/ranks/nums as `List`s) to the tree-based one
(`NatMap` literals, `n` field), as scripts/gen_bui_cert.lean.py now emits.
Parses the existing literals so the oracle need not be rerun; the regenerated
files must be byte-identical (queue B5)."""
import re, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
from gen_bui_cert_emit import emit_tree  # shared emitter

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..',
                    'polyplets', 'Polyplets', 'Upper')

def parse_list(src, name):
    """Concatenate the private chunk lists `name<k>` in order."""
    chunks = re.findall(r'private def ' + name + r'(\d+) : [^:]*:= \[(.*?)\]\n', src)
    chunks.sort(key=lambda c: int(c[0]))
    items = []
    for _, body in chunks:
        body = body.strip()
        if not body:
            continue
        if 'some' in body or 'none' in body:
            for m in re.finditer(r'some \((\d+), (\d+)\)|none', body):
                items.append(None if m.group(0) == 'none' else (int(m.group(1)), int(m.group(2))))
        else:
            items.extend(int(x) for x in body.split(','))
    return items

def fmt_rule(r):
    return 'none' if r is None else f'some ({r[0]}, {r[1]})'

for rd in (2, 3):
    path = f'{ROOT}/BuiData{rd}.lean'
    src = open(path).read()
    rules = parse_list(src, f'buiRD{rd}Rules')
    ranks = parse_list(src, f'buiRD{rd}Ranks')
    nums = parse_list(src, f'buiRD{rd}Nums')
    n = len(rules)
    assert len(ranks) == n and len(nums) == n, (rd, n, len(ranks), len(nums))
    m = re.search(r'⟨(\d+), (\d+), (\d+), buiRD', src)
    CD, X, root = int(m.group(1)), int(m.group(2)), int(m.group(3))
    head = src[:src.index('/-- Casing table')]
    head = head.replace('set_option linter.style.nativeDecide false\n', '')
    head = head.replace('checked by `native_decide`.', 'checked by `decide +kernel`.')
    head = head.replace('checked by `decide`.', 'checked by `decide +kernel`.')
    out = [head]
    out.append(emit_tree(f'buiRD{rd}Rules', 'NatMap (Option (ℕ × ℕ))', rules, fmt_rule, 'Casing table: `none` = base, `some (T\', D)` = split.'))
    out.append('\n')
    out.append(emit_tree(f'buiRD{rd}Ranks', 'NatMap ℕ', ranks, str, 'Free-king-neighbor counts (the termination measure).'))
    out.append('\n')
    out.append(emit_tree(f'buiRD{rd}Nums', 'NatMap ℕ', nums, str, f'Certificate numerators: `u_i = num i / {CD}`.'))
    out.append(f'''
/-- The RD={rd} king Bui certificate: {n} types, rate `x = {X}/{CD}`,
anchor type `{root}` (the G8 corner type, W/SW/S/SE forbidden). -/
def buiRD{rd} : RatCert :=
  ⟨{CD}, {X}, {root}, {n}, buiRD{rd}Rules, buiRD{rd}Ranks, buiRD{rd}Nums⟩

/-- **The certificate arithmetic**, machine-checked by the kernel: positivity,
the anchor index in range, index bounds, rank descent, and the {n}
cleared-denominator super-solution inequalities. -/
theorem buiRD{rd}_valid : buiRD{rd}.valid = true := by decide +kernel

end BuiData{rd}

end Polyplets
''')
    open(path, 'w').write(''.join(out))
    print(f'BuiData{rd}: {n} types, CD={CD}, X={X}, root={root}')
