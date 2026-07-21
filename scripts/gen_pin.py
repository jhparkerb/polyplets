#!/usr/bin/env python3
"""Generate the k=4..16 tier of Pin.lean from pin-data.md.

Conditional tier  k=4..11: hypotheses are the k+1 banked T-values.
Partial     tier  k=12..16: hypotheses are m(k) banked + (k+1-m(k)) PREDICTED
                             (beyond-banked) T-values, flagged in the docstring.
"""
import re, sys

SRC = "/Users/jasonp/src/polyominoes/polyplets/pin-data.md"

def parse():
    blocks = {}
    cur = None
    for line in open(SRC):
        m = re.match(r'## k=(\d+)', line)
        if m:
            cur = int(m.group(1))
            blocks[cur] = {'num': None, 'kf': None, 'banked': [], 'pred': []}
            continue
        if cur is None:
            continue
        m = re.match(r'numerator \(desc n\): \[(.*)\]', line)
        if m:
            blocks[cur]['num'] = [x.strip() for x in m.group(1).split(',')]
            continue
        m = re.match(r'kfact: (\d+)', line)
        if m:
            blocks[cur]['kf'] = m.group(1); continue
        m = re.match(r'\s*T\((\d+),(\d+)\) = (\d+)', line)
        if m:
            blocks[cur]['banked'].append((int(m.group(1)), int(m.group(2)), m.group(3)))
            continue
        m = re.match(r'\s*T\((\d+),(\d+)\) =pred= (\d+)', line)
        if m:
            blocks[cur]['pred'].append((int(m.group(1)), int(m.group(2)), m.group(3)))
            continue
    return blocks

def emit(k, b):
    num = b['num']; kf = b['kf']
    pts = sorted(b['banked'] + b['pred'])          # (a, bb, v)
    predset = {(a, bb) for a, bb, _ in b['pred']}
    assert len(pts) == k + 1, f"k={k}: got {len(pts)} pts, need {k+1}"
    assert all(a == 2*k+1+i for i, (a, bb, v) in enumerate(pts)), f"k={k} pts not consecutive"
    L = []
    ap = L.append
    # polynomial + degree
    ap(f"/-- k={k} production polynomial (numerator / {kf}), transcribed from `pin-data.md`. -/")
    ap(f"noncomputable def Pp{k} : Polynomial ℚ := prodPoly")
    # wrap the coefficient list
    coeffs = ", ".join(num)
    ap(f"  [{coeffs}] {kf}")
    ap(f"lemma Pp{k}_deg : Pp{k}.natDegree ≤ {k} := by")
    ap(f"  rw [Pp{k}]; exact le_trans (prodPoly_natDegree_le _ _) (by norm_num)")
    # guards
    for a, bb, v in pts:
        e = 3*k+1 - a
        ap(f"lemma guard_{k}_{a} : Pp{k}.eval ({a} : ℚ) = (({v} * 3 ^ {e} : ℕ) : ℚ) := by")
        ap(f"  rw [Pp{k}, prodPoly_eval]; norm_num")
    # theorem
    tier = "banked" if k <= 11 else "partial"
    npred = len(b['pred'])
    doc = []
    if k <= 11:
        doc.append(f"**k={k}, conditional tier.** Given the {k+1} banked onset values")
        doc.append(f"`T(n,n-{k})` at `n = {2*k+1}..{3*k+1}` (all in `results/triangle.txt`),")
        doc.append(f"the production polynomial is pinned by Lagrange uniqueness.")
    else:
        bkd = k+1 - npred
        doc.append(f"**k={k}, PARTIAL tier.** {bkd} of the {k+1} required onset points are")
        doc.append(f"banked (`n = {2*k+1}..36`); the remaining {npred} hypotheses")
        preds = ", ".join(f"`T({a},{bb})`" for a, bb, _ in b['pred'])
        doc.append(f"({preds}) are the production polynomial's own PREDICTED")
        doc.append(f"values beyond the banked range (`n = 37..{3*k+1}`), NOT independent data.")
        doc.append(f"The theorem is therefore honest about exactly which unverified values")
        doc.append(f"would close the gap.")
    ap("/-- " + "\n    ".join(doc) + " -/")
    hypnames = []
    hypargs = []
    for a, bb, v in pts:
        hn = f"h{a}"
        hypnames.append((hn, a, bb, v))
        tag = " -- PREDICTED (beyond banked)" if (a, bb) in predset else ""
        hypargs.append(f"    ({hn} : T {a} {bb} = {v}){tag}")
    sig = f"theorem P{k}_pinned_of_{tier}"
    ap(sig)
    for ha in hypargs:
        ap(ha)
    ap(f"    : ∀ n : ℕ, 2 * {k} + 1 ≤ n →")
    ap(f"      (T n (n - {k}) : ℚ) = Pp{k}.eval (n : ℚ) * (3 : ℚ) ^ ((n : ℤ) - 1 - 3 * {k}) := by")
    pinset = "{" + ", ".join(str(a) for a, _, _ in pts) + "}"
    ap(f"  refine pin {k} Pp{k} Pp{k}_deg ({pinset} : Finset ℕ) (by decide) ?_ ?_")
    ap(f"  · intro n hn; fin_cases hn <;> norm_num")
    ap(f"  · intro n hn")
    ap(f"    fin_cases hn")
    for hn, a, bb, v in hypnames:
        e = 3*k+1 - a
        ap(f"    · simp only [show ({a} - {k} : ℕ) = {bb} from rfl,")
        ap(f"        show (3 * {k} + 1 - {a} : ℕ) = {e} from rfl, {hn}]")
        ap(f"      exact guard_{k}_{a}")
    return "\n".join(L)

def main():
    blocks = parse()
    out = []
    for k in range(4, 17):
        out.append(emit(k, blocks[k]))
        out.append("")
    print("\n".join(out))

main()
