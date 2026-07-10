# a(36) provenance

a(36) = 24629107617723857143962968288

Computed 2026-07-10 on the two-machine disk-split, varint engine rev f4edb3b
(LEB128 varint run-file counts), launched 09:19 EDT, both jobs foreground in
tmux with tee'd logs.

- **ayr** (x86, 32 core): heights 1-18 real sweeps + 20-36 via wired P_k
  closed forms (k = 36-H <= 16). wall 6988.2s (1.94h), cpu 187437.7s,
  rss_max 351.6 MB. Run dir runs/ns_a36_split/h1_18_20_36.
- **dalby** (ARM, 80 core): height 19 real sweep — the long pole, and the
  genuine k=17 diagonal value T(36,19). wall 11810.4s (3.28h), cpu 397861s,
  rss_max 380.2 MB. vs a(35)'s H19 at 25112.2s pre-varint: 2.13x faster
  despite one term higher — the varint disk-write reduction is the driver.

## Validation

- a(1)..a(35) from the combined 36-shard triangle match the banked
  results/ns_a35/triangle.txt exactly (all 35 terms).
- fixtures/b006770.txt comparison OK through its full extent (n=20).
- T(36,36) = 3^35 exactly (king-chain identity T(n,n) = 3^(n-1)).
- T(36,35) = 855 * 3^32 with 855 = 25*36 - 45 = P_1(36) exactly.
- Diagonal k=16 ratio trend smooth across the P16-generated T(36,20) and the
  real T(35,19): 5.31 -> 5.20 -> 5.10, declining toward 3 as expected.

## Notes

T(36,19) is a real computed value on diagonal k=17: together with real
T(34,17) and T(35,18) it gives fit+holdout material to derive and validate
P_17, which would push the closed-form frontier one diagonal deeper for a(37).
