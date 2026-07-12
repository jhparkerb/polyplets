# Joint box table B(n, W, H): quick probe (2026-07-13)

One-afternoon look at counts by (cells, exact width, exact height), per the
"is there insight in it" question. Tool: `experiments/joint_box_probe.py`
(row transfer + connectivity partitions + box-edge offsets (dl, dr);
shape-transitions cached — H <= 11, k = n-H <= 2 in ~1s; every marginal
matches the banked T(n,H)).

## What the probe found

- **Edges are clean and classical**, as predicted: B(H,W,H) is the trinomial
  walk-range distribution (B(H,2,H) = 2^H - 2; monotone tail 2; next-to-tail
  2(H+1)); first k=1 laws read off instantly (B(H+1,2,H) = H*2^(H-1),
  tail 2(H+2)). Derivable via the defect gas with a range coordinate;
  derivative of known structure, not pursued.
- **The mod-3 wildcard has substance**: the k=0 slice mod 3 is visibly
  3-automatic — row H=9 is 100000122, a zero desert carrying row H=3's
  "102" skeleton (trinomial digit-product/Lucas structure, provable with
  the spine's char-3 toolkit). k=1,2 slices show parity striping
  (020202..., 002222002221) — patterned, undecoded.
- Nothing here touches the squat region or the cost wall (readout
  partition, not a decomposition), confirming the prior assessment.

## Disposition

Parked. If ever revisited: (i) prove the k=0 mod-3 digit law (easy,
known-math flavor), (ii) decode the k>=1 stripes (the only genuinely
open pattern), (iii) the full production-scale table costs an a(36)-sized
re-run and should wait for a reason.
