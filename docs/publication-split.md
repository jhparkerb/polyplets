# How the papers in `paper/` are labelled

Every manuscript in `paper/` is one of two kinds, and says which on page 1 in
a fixed block from `paper/shared/disclosure.tex`. No paper is wholly a
human's work.

- **P: the author's prose.** Byline Jason Parker. He wrote every sentence,
  has read every proof it states and is responsible for its correctness; the
  machine did the enumeration, formalization, literature search, tables,
  figures, LaTeX and checking. `paper/technical-report.tex` is the one P
  paper. It is not edited by the machine.
- **L: machine-written.** The six `paper/L*.tex` files were written end to
  end by a large language model, mathematics included. The block on page 1
  lists, for each result, what mechanically warrants it (a Lean proof, an
  exact certificate, or a labelled measurement) and what a person has
  checked. As of this writing that last column reads "none" on every one:
  nobody has read these papers for correctness, and they carry a draft
  banner saying so. The byline is left open; it is the author's decision per
  paper.

Nothing submitted to the OEIS cites an L paper as its warrant. An entry may
cite the technical report; everything OEIS-facing is data and elementary
structure, which is on the P side.
