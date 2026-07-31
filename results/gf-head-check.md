# Head-check: banked fixed-height GFs vs the exact triangle, n <= 40

Date: 2026-07-31. The banked `G_H(x) = P_H/Q_H` (`results/fixed_height_gfs.txt`,
H = 1..11, recurrence orders 1, 3, 7, 15, 42, 106, 278, 711, 1897, 5005, 13381)
had never been re-expanded against the finished triangle. Tool:
`experiments/gf_head_check.py` (exact integer series division; `Q_H[0] = 1`, so
no fractions arise). Motivated by the H=11 entry, banked `validated=False` and
flagged anomalous in [anisotropic-not-dfinite.md](anisotropic-not-dfinite.md).

```
python3 experiments/gf_head_check.py
```

Method: only the first 41 coefficients of `P_H` and `Q_H` are parsed (heads of a
12 MB line), since tail terms beyond `x^40` provably cannot influence a
coefficient `<= 40`. Convention confirmed as `G_H = sum_n T(n,H) x^n` with no
offset: H=1 is `x/(1-x)` (T(n,1)=1), H=2 reproduces T(3,2)=10, and every series
vanishes below `x^H` (`low0` column) as exact-height counting requires.

## Result: all 11 heights match, cell for cell

| H | order | validated | cells compared (n=H..40) | match | first mismatch |
|---|-------|-----------|--------------------------|-------|----------------|
| 1 | 1 | True | 40 | 40 | - |
| 2 | 3 | True | 39 | 39 | - |
| 3 | 7 | True | 38 | 38 | - |
| 4 | 15 | True | 37 | 37 | - |
| 5 | 42 | True | 36 | 36 | - |
| 6 | 106 | True | 35 | 35 | - |
| 7 | 278 | True | 34 | 34 | - |
| 8 | 711 | True | 33 | 33 | - |
| 9 | 1897 | True | 32 | 32 | - |
| 10 | 5005 | True | 31 | 31 | - |
| **11** | **13381** | **False** | **30** | **30** | **-** |

385 cells compared, 385 exact agreements, zero mismatches; below-`x^H`
vanishing holds at every height. Runtime 0.04s.

## Sanity control (so a clean pass means something)

Two scratch GF files (scratchpad, not `results/`), both fed to the same
comparator:

- **truncation control** — all 11 blocks cut to 41 coefficients: still PASSES,
  confirming the head-slicing is sound (tails cannot reach the head);
- **corruption control** — the same file with `P_11[20] += 1` and `Q_5[7] += 1`:
  FAILS at exactly the predicted places, `H=5` first mismatch `n=12` (= 7+5,
  the first coefficient the perturbed `Q` term can reach) and `H=11` first
  mismatch `n=20`, exit status 1.

The comparator is therefore not vacuous, and it fails closed (nonzero exit on
any mismatch, missing triangle cell, or parse surprise).

## Conclusion — carefully scoped

The **head** of the banked H=11 generating function is now confirmed against the
exact triangle for every `n <= 40`. **This does not clear the `validated=False`
flag.** The anomaly recorded in
[anisotropic-not-dfinite.md](anisotropic-not-dfinite.md) is about the *full
rational function* — `Q_11` shares no roots with `Q_9 Q_10` mod p, inconsistent
with the atom law that holds at every validated level — and a head-check is
structurally incapable of touching it: 30 coefficients against a
(13381 + 13381)-coefficient rational function is a wildly underdetermined
constraint. What is now known is narrower and worth having: *if* the H=11 entry
is wrong, it is wrong in the tail, not in the range where the triangle exists.
The re-recovery of H=11 is still owed before that entry is used anywhere, and
its exclusion from the psi-ladder certificates remains correct.

For H = 1..10 the head-check is a genuine (if weak) independent corroboration of
the mod-p + Berlekamp-Massey + CRT recovery: the triangle comes from the
enumeration engines, the GFs from the transfer-matrix/BM pipeline, and they
agree on 355 cells.

## mu_11 provenance (grade check)

`experiments/mu_H_from_atoms.py` parses **every** `Q:` block of
`results/fixed_height_gfs.txt`, including H=11, and bisects for the smallest
positive root — so the `mu_11 = 6.1158` printed in
[strip-growth-lambda-bounds.md](strip-growth-lambda-bounds.md) does, as banked,
derive from the `validated=False` denominator. But the number itself is **not**
tainted: `cpp/strip_mu.cpp` (`build/strip_mu`) computes `mu_H` by Perron power
iteration on the height-H king connectivity transfer matrix and never reads the
GF file at all. Re-run today, `./build/strip_mu 10 11` gives
`mu_10 = 5.9916958, mu_11 = 6.1158416` in 10.3s — identical to the GF-root value
to all printed digits, and `cpp/strip_mu_kink.cpp` is a third, structurally
different (cell-at-a-time) engine that also reproduces it. So the `mu_11` rung
of the lower-bound ladder stands on an independent construction; only its
attribution needs care. Note that this agreement pins one root of `Q_11` (the
dominant pole) and says nothing about the other 13380 — it is not evidence
against the root-structure anomaly.
