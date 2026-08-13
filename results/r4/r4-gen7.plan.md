# r4-gen7 plan

QUESTION: The campaign now owns fast, validated instruments (B1 colour DP H<=16
exact + flood-fill-validated; spin engine m=1..16 in 88.6s byte-identical on two
ISAs; flood-fill brute force n<=10; mutant harness; 640-cell exact oracle) and
has only ever used them as counters. What becomes possible when checking is
cheap, fast, and reproducible that was impossible when every check was rationed?

STEPS
1. Read `docs/triangle-round4.md` (done first), then `results/r4/queue.md` row
   index and the five predecessor generator deliverables (r4-gen..r4-gen5) plus
   r4-gen6's plan/progress, harvesting row ids + one-line titles only.
   PRODUCES: an in-context "already said" list; no file.
2. Read the instrument facts off disk, not off the brief: the spin engine
   timing/sha256 record, the B1 DP validation record, the mutant harness flip
   sets, the 640-cell oracle. PRODUCES: verified premises, or a NOT ESTABLISHED
   note per premise that fails to check out.
3. Generate >=20 rows in four families, each a successor or a kill, never a
   repeat: (A) differential testing as continuous search rather than gate,
   (B) engines as search instruments (sweep instead of prove), (C) what the
   byte-identical cross-ISA determinism licenses, (D) what is now cheap enough
   to be worth doing badly. PRODUCES: `results/r4/r4-gen7.md` rows, filed
   incrementally as written.
4. Kill in place every row I can kill with desk arithmetic (`python3 -c`,
   sub-second) or a read of existing results. The kill is the content.
5. Second pass: what my own rows share — the common structural claim, and the
   one row whose failure would take the most of the others with it.
   PRODUCES: a final section of r4-gen7.md.
6. Append every row as a one-liner to `results/r4/queue.md` (append only).

STOP CONDITIONS
- 20+ rows filed with priors, kill-costs, and entry tickets: stop generating,
  do the second pass, file, report.
- A premise in step 2 fails to verify: do not silently drop it; file it as a
  row of its own (the instrument is not what we think it is) and continue.
- No compute anywhere beyond sub-second desk arithmetic; no jobs; nothing on
  gympie beyond that; ssh to ayr/dalby read-only only if needed.
