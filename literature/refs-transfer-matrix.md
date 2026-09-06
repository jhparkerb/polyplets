# Transfer-matrix / enumeration references

Indexed 2026-06-25 during the a(24)+ scheduling + compression design. NOTE: literature/ already
holds a rich collection from prior sessions (redelmeier_1981, tremblay_vernay, jensen_*,
klarner_*, mertens_*, etc.) — this file just points the scheduling-relevant ones at their
local files and notes WHY they matter here.

## The targets to actually mine (SOTA engine + the compression encoding)

- **Barequet & Ben-Shachar, "Counting Polyominoes, Revisited," ALENEX 2024.** Current
  *fixed*-polyomino record: **n=70** (A001168), by running the transfer matrix on a
  **45°-rotated** bounding box — an equivalent but computationally-easier problem — extending
  Jensen's n=56. A(70) took ~15,000 CPU-h on 32-CPU / **only 32 GB RAM** (the method is
  memory-lean). THE engine to study. literature/counting_polyominoes_revisited.pdf ·
  https://barequet.cs.technion.ac.il/papers.html
- **Jensen, I., doctoral thesis** (and "A parallel algorithm for the enumeration of
  self-avoiding polygons," cond-mat/0301468). Origin of the **Motzkin-path state encoding**:
  the boundary "signature" — which boundary cells connect through cells already placed to the
  left — is encoded as a Motzkin-like balanced string; the number of such strings ~ Motzkin
  numbers. THE reference for compression idea #1. [thesis itself: library lookup]

## Context / used-the-encoding

- **Shirakawa, "Enumeration of Polyominoes up to N=59," arXiv:2510.22446 (Oct 2025).**
  Free/one-sided (A000105 / A000988) via Burnside symmetry classes; uses Jensen's Motzkin
  encoding for the mirror-symmetric transfer matrix. CALIBRATION GIFT: hit the **memory limit
  ~n=60 on 512 GB RAM** even with the compact encoding → RAM is the universal frontier wall.
  literature/shirakawa_n59.pdf
- **Counting Polyominoes: A Parallel Implementation for Cluster Computing** (Springer,
  3-540-44863-2_21). Redelmeier on a cluster; cross-machine distribution patterns.
  [paywalled → library]
- **Luther & Mertens, "Counting Lattice Animals in High Dimensions," arXiv:1106.1078.**
  Redelmeier in d≥3. literature/1106.1078.pdf

## Leads these opened (tracked in docs/scheduling-design.md)

- **Compression #1** = adopt Jensen's Motzkin-path boundary encoding → fewer bytes/state →
  moves the RAM cliff (currently a(24)) rightward. Highest-value lead off this search.
- **45°-rotated TM (Barequet–Ben-Shachar)** gave the biggest recent ordinary-polyomino win on
  tiny RAM. OPEN: does it transfer to KING-polyplets? Our earlier "diagonal deflation" (king
  diagonals span n×n) said no — but given the magnitude of that win, **re-derive**, don't trust
  the note.
