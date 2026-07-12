# Related polyplet sequences: n=33 (T3, conjecture-assisted)

2026-07-06. Extends `results/related-seqs-n32.md` by one term for the four
D-dependent sequences. **These values are tier T3**: exact computation
composed with empirically pinned but unproven quasi-polynomial formulas.
For OEIS they are COMMENT-ONLY (never b-file data), per the batch rule.

## D(33) assembly (the T3 step)

D(33) = **5475149862148** = direct strips S=1..28 + pinned closed forms
P_0..P_4 for the 15 sparse cells S=29..33 (`scripts/dmirror_hybrid_sum.py
33 28 runs/sym33`). Safeguards, all enforced by the script (fail-closed):

- direct strips complete (28/28) and each covers its full n-range;
- the closed forms reproduce **124 in-regime direct cells** on the
  overlap before being trusted for the 15 off-edge cells;
- only PINNED classes usable (P_5-odd is fitted -> hard refusal if needed;
  it is not needed at maxn=33);
- prefix: the hybrid dmirror.out matches banked n<=32 exactly.

Direct strips: dalby, 2026-07-05 07:41 -> 07-06 07:39 (24.0h wall,
6.71M cpu-s ≈ 1864 core-h, peak strip RSS 126.2GB = S=28, brushed into
swap). Every strip's n<=32 prefix byte-matches the n=32 farm (413
entries, 0 mismatches). Cross-ISA: ayr (x86) independently recomputed
the S<=25 tail (compare completed; the n=33 result is banked and used downstream).

## The n=33 terms (T3)

| seq | value at n=33 |
|---|---|
| A030222 free | 9328935247555296909698722 |
| A030234 bilateral | 5909238725043 |
| A030235 asymmetric | 9328935247549387670973679 |
| A194596 free-non-poly | 9328935102907028734392020 |

(A030233 one-sided needs no D; its n=33/34 values are banked T2/T2- in
related-seqs-n32.md.) Derivation `scripts/derive_related.py
runs/sym33.derive` — validates all 95 known OEIS terms, /8 /4 /2
integralities at every n.

## P_k dividend

The n=33 k=5 points pin **P_5-even conventionally** (exact differencing,
S0=12, 3 holdout hits; identical to the exp fit — forward confirmation of
the fitted form). P_5-odd remains exp-fitted (7 exact witnesses). Level 6
still refuses. Updated in results/dmirror-diagonals.md territory: the
n=34 path (P_5 for S>=29 + direct S<=28) would rest on fitted P_5-odd for
odd S>=29 cells — grade accordingly if run.
