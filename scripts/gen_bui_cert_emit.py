"""Lean emission of a `NatMap` literal (polyplets/Polyplets/Upper/Certificate.lean),
shared by gen_bui_cert.lean.py and bui_lists_to_trees.py.

A table `items[0..n-1]` becomes a balanced binary search tree keyed by index.
Subtrees below depth `SPLIT` are emitted as `private def`s so no single term is
huge; the top levels combine them."""

SPLIT = 4  # 2^SPLIT private subtree definitions


def _tree(items, lo, hi, fmt):
    """Balanced tree literal over indices lo..hi-1 (as a string)."""
    if lo >= hi:
        return 'NatMap.leaf'
    mid = (lo + hi) // 2
    return (f'NatMap.node ({_tree(items, lo, mid, fmt)}) {mid} ({fmt(items[mid])}) '
            f'({_tree(items, mid + 1, hi, fmt)})')


def emit_tree(name, ty, items, fmt, doc):
    """Return Lean text defining `name : ty` as the balanced tree of `items`,
    with docstring `doc`."""
    out = []
    counter = [0]

    def go(lo, hi, depth):
        if lo >= hi:
            return 'NatMap.leaf'
        if depth == SPLIT:
            k = counter[0]
            counter[0] += 1
            out.append(f'private def {name}_{k} : {ty} := {_tree(items, lo, hi, fmt)}\n')
            return f'{name}_{k}'
        mid = (lo + hi) // 2
        return (f'NatMap.node ({go(lo, mid, depth + 1)}) {mid} ({fmt(items[mid])}) '
                f'({go(mid + 1, hi, depth + 1)})')

    top = go(0, len(items), 0)
    out.append(f'/-- {doc} -/\ndef {name} : {ty} := {top}\n')
    return ''.join(out)
