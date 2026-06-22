# T2 — the k-hole GF order law: order(G_{H,k}) = (k+1)·order(G_{H,0})

For a fixed strip height H, let `G_{H,k}(x) = Σ_n B_{H,k}(n) x^n` be the generating
function for fixed polyplets of height exactly H with exactly k holes, recovered exactly
(mod-p transfer matrix + Berlekamp–Massey + CRT, `results/hole_gfs.txt`). Its **recurrence
order** = deg of the denominator Q_{H,k}.

**Law (conjecture, confirmed H=3..7).** The order is *exactly linear in the hole count k*:

```
   order(G_{H,k}) = m_H · (k+1)        for k ≥ 1,
```

and for **H ≥ 5 the slope equals the hole-free order**, m_H = order(G_{H,0}), giving the
clean proportional form

```
   order(G_{H,k}) = (k+1) · order(G_{H,0})        (H ≥ 5).
```

| H | slope m_H | order(G_{H,0}) | k≥1: order = m_H·(k+1)? |
|---|----------:|---------------:|:-----------------------:|
| 3 |     6     |       9        | YES (m_3 = 9−3)         |
| 4 |    20     |      22        | YES (m_4 = 22−2)        |
| 5 |    68     |      68        | YES, and = (k+1)·order₀ |
| 6 |   185     |     185        | YES, and = (k+1)·order₀ |
| 7 |   537     |     537        | YES, and = (k+1)·order₀ |

(Verified for every k present in the data, `experiments/hole_order_law.py`.) For H=3,4
the slope is the hole-free order minus a small constant (3, 2); the proportional form is
exact from H=5 on. Slope sequence m_H = 6, 20, 68, 185, 537 (H=3..7); the hole-free orders
order(G_{H,0}) = 1, 3, 9, 22, 68, 185, 537, 1499 (H=1..8).

## Interpretation and path to a proof
Each additional hole contributes a **fixed block** of order m_H — the k-hole denominator
behaves like (k+1) copies of a single height-H "hole factor." This is the structural
content of the listed T2 ("the c_H(k+1) hole-GF order law"). A proof should come from the
transfer matrix that carries the hole count as an extra Euler-characteristic (q-) index:
each hole closes via one q-marked event, and the q-degree adds one block of the hole-free
order. The clean H≥5 onset (vs the +3/+2 correction at H=3,4) is the small-height
boundary effect, exactly as in the lifetime-3 order analysis (`results/fixed_height_gf.md`).

## Status
Conjecture, confirmed H=3..7 over all available k. The hole-free order sequence
`1, 3, 9, 22, 68, 185, 537, 1499` and the identity `slope = order(G_{H,0})` (H≥5) are
candidate OEIS / paper observations.
