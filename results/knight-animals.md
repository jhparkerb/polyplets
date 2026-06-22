# Knight-move animals (polyknights) — full counts (S5)

Cells connected through knight moves (the 8 offsets (±1,±2),(±2,±1)); "animals" = knight-
connected sets. Computed by exhaustive canonical growth (`experiments/knight_animals.py`),
the same enumeration method verified against A006770 for the king case.

| n | fixed | one-sided (C4) | free (D4) |
|---|------:|---------------:|----------:|
| 1 | 1 | 1 | 1 |
| 2 | 4 | 2 | 1 |
| 3 | 28 | 8 | 6 |
| 4 | 234 | 68 | 35 |
| 5 | 2162 | 550 | 290 |
| 6 | 20972 | 5328 | 2680 |
| 7 | 209608 | 52484 | 26379 |
| 8 | 2135572 | 534793 | 267598 |

Sanity checks: fixed(2)=4 = the 8 knight vectors in 4 translation classes; free(2)=1
(D4 acts transitively on the knight vectors); free counts are Burnside-consistent with the
fixed counts. (The knight graph on Z² is connected, so these are ordinary connected
animals on that graph.)

**Novelty UNVERIFIED — check OEIS before submitting.** "Polyknight" / knight-connected-
animal sequences may already exist (this is a natural object). The repo's `cpp/gf_knight.cpp`
is the related existing tool (a fixed-height knight transfer matrix over Z/pZ, for a
horizontal-reach test); the *full* counts above (summed over all heights, free/one-sided/
fixed) are what this enumeration adds. If a known sequence matches, treat this as a
confirmation + the free/one-sided companions; if not, a candidate submission.
