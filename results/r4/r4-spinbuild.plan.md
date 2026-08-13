# r4-spinbuild plan

**Question, one sentence:** can the spin-basis parity engine, validated in Python
at small m, be written as a C++20 program that the lead can build and gate
tonight on dalby at m = 1..16 against the 640 recovered B1 oracle cells, with
dense ranking, fail-closed exits, blind harvest, and instrumentation good enough
to yield the measured RSS and ns/slot-op constants for the m = 18..21 pricing?

**Hard constraint on me:** I write source. I do not compile it, I do not run it,
on any machine. Everything I produce is UNCOMPILED and is labelled so.

## Steps

1. Read the spec, in this order, before writing a line of C++:
   `results/triangle-r3-spin.md` (whole), `results/r4/r4-inv.md` §1.1, §1.2,
   §1.3, §3.2, §3.3, §3.4, §4, then the two Python references
   `experiments/tristruct/r3_spin_pipeline.py` and `r3_spin_counts.py` plus
   `r3_spin_pipeline.log`. Produces: a written correspondence table (Python
   function -> intended C++ function) in the deliverable.
2. Read the house style and the oracle: `git show 48ac108:cpp/cutcount_b1.cpp`,
   `cpp/obs.h`, `results/cutcount_b1/PROVENANCE.md`, and one `C<H>.out` row file
   to fix the parse format. Produces: the obs event vocabulary and the exact
   oracle file grammar I will code against.
3. Write `experiments/tristruct/r4_spin_engine.cpp`. Produces: the artifact.
   Order inside the file: header comment, obs include, CLI parse, oracle
   loader, spin transfer step, dense ranker, driver, mutant switch, harvest
   writer + sha256, separate oracle-compare pass, exit contract.
4. Re-read my own source against the Python line by line, hunting for the
   places the two could disagree. Produces: deliverable §3.
5. Write the deliverable's build command and gate sequence. Produces: §4.
6. File, report to lead in two paragraphs.

## What would make me stop

- If the Python reference and `r4-inv.md` disagree about the state space in a
  way I cannot resolve from the Python alone, I stop and ask the lead rather
  than guessing the semantics of the production m = 18..21 run.
- If the recovered oracle rows are not on disk in the stated format, I stop:
  the gate is the deliverable, and an engine with no check is not shippable.
- If dense ranking turns out to be impossible for this state space (as opposed
  to merely awkward), I stop and file that as the finding, because §1.3 makes it
  load-bearing for the whole cost case.
