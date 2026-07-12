# Anti-diagonal closed forms of the polyplet height triangle

Date: 2026-07-10. **Mostly a re-derivation of already-banked, partly-PROVEN work
— see the integration note at the bottom.** Kept for the production-matrix / SNF
cross-connections, which are the genuinely new part.

`T(n,H)` = # fixed polyplets, n cells, bbox height exactly H. `T(n,n-k)` = the
k-th sub-diagonal (near-maximal height). `experiments/Pk_explicit.py`.

## The closed forms (PRIMARY sources: proofs + k8-pinning)

`T(n,n-k) = P_k(n)·3^{n-1-3k}`, **degree(P_k) = k**, valid in the bulk
**`n ≥ 2k+1`** (below that, boundary terms), leading coefficient **`25^k/k!`**.
Proven k=0,1,2 from first principles; leading coeff verified k≤6 and confirmed
k=3..7; **k=8 pinned** (T(24,16) banked, `results/ns_a36/perheight/h16.out`;
a(24)…a(36) all banked). See:
- `docs/proofs/T-n-nm1.md`, `docs/proofs/T-n-nm2-and-general.md` (the proofs +
  "defect gas" structure),
- `results/k8-pinning.md` (leading-coeff conjecture `[n^k]P_k = 25^k/k!`
  confirmed, k=8 pinning method).

| k | closed form | onset |
|---|---|---|
| 0 | `3^{n-1}` (king chain, **A000244**) | all n |
| 1 | `(25n-45)·3^{n-4}` = `5(5n-9)3^{n-4}` | n≥3 |
| 2 | `½(625n²−2459n+1134)·3^{n-7}` | n≥5 |
| k | `P_k(n)·3^{n-1-3k}`, deg k, lead `25^k/k!` | n≥2k+1 |

(My earlier draft wrote these as `P_k(n)·3^n` with denominators `3^{3k+1}`, and
wrongly claimed onset `n≥k+2`. Both are corrected here: `3^n / 3^{3k+1} =
3^{n-1-3k}`, and the true onset is `2k+1` — e.g. `P_2(4)·3^4=24.04 ≠ 27=T(4,2)`,
so n=4 is a boundary term, not on the bulk polynomial.)

## The defect gas (PROVEN, banked — not a new result)

`docs/proofs/T-n-nm2-and-general.md` establishes: the excess-k cells form
*defect clusters* on the n-row king chain, independent except for adjacency, so
`S(y)=Σ_k P_k(n) y^k` has `log S(y)` exactly linear in n — the ideal/defect gas.
The per-defect weight `25=5²` is the `5·5` tromino-gadget config count, PROVEN.
`25^k/k!` = k indistinguishable defects. (My session re-derived the leading
coeff and the gas picture independently; they were already banked and proven.)

## OEIS / literature status (sonnet-checked 2026-07-10)

- k=0 = **A000244**. k=1..5 diagonals not in OEIS. But they are diagonals of the
  height triangle (OEIS Candidate A, results/oeis-candidates.md) and of banked,
  proven structure — **do NOT submit separately** (jasonp's call, confirmed).
- No prior *published* literature on T(n,n-k) closed forms for lattice animals
  (our proofs are the source); the structure is internal to this project.

## Integration note (what this session actually added)

The degree-k, onset-`2k+1`, `25^k/k!`, and defect-gas facts were ALREADY banked
and (k≤2) proven before this session. What is genuinely new here:
- **Production-matrix face** (results/production-matrix-probe.md): the band
  constants `3^{3k+2}` and the Newton-basis `3^{3k+1}` (= "P_k is 3-integral in
  the `3^{n-1-3k}` normalization"), offset by the de-tripling factor.
- **SNF** (results/triangle-snf.md): the whole triangle is all-3-power, rank
  `⌈(N-1)/3⌉` — same 3-adic phenomenon.

Boundary-push-recurrence.md's old "degree 2k" was the lone stale claim (now
fixed); the a26-a30 machinery and the paper already used degree k / onset 2k+1
correctly.