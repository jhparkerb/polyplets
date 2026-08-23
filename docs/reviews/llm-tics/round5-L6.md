# Round 5 — L6, and why the round is not the two remaining ratios

2026-08-23. Executed on jasonp's "everything you can do on your own that is
waiting on me can run". Ruler: `docs/reviews/llm-tics/density.py`, per 1000
prose words, against the two-paper P control (`technical-report.tex`,
`polyplets-report.tex`).

## What the measurement says the round should be

Four of the six tracked constructions are done. Cleft, serves-as and scaffold
are at **zero** across all ten L papers; dash-aside is 0.09 against the
control's 0.40, having been the worst marker in the corpus at 2.20 when the
ruler was frozen. Two are left:

| | L overall | P control | ratio |
|---|---|---|---|
| contrast-neg | 1.00/1k | 0.40/1k | 2.52 |
| punch (short declarative) | 1.06/1k | 0.40/1k | 2.68 |

## Why "reduce those two numbers" is the wrong round

The plan's own warning is that "rewriting to hit numbers produces flat mush,
which is the failure mode this phase exists to avoid", and the numbers that
remain are the case it was written for. Read in context, most of what the two
regexes catch is carrying a value or an epistemic status rather than a habit.

**L1, all six contrast-negs, kept.** They are `proved, not observed`;
`for X, not priority`; `integer, not integer coefficients`; `stated, not
proved`; `a bound on the height, not on the number of animals`; `proved, not
proved in Lean`. Every one is the distinction the sentence exists to make, in
a paper whose subject is which results are theorems and which are measurements.
Round 4 reached the same verdict on L10's short declaratives and logged them
rather than chasing them; the same standard applies here.

**L1, eleven short declaratives, kept.** `It is false.` `The conjecture holds.`
`The proof is five steps.` Terse verdicts in a paper of verdicts. The mean
sentence length that would rise if these were padded is 22.9 against a corpus
28, and closing that gap by inflating one-line results is the mush the plan
names.

So the round is not a sweep. It is the sites where the construction is doing
nothing, and L6 is where they are: nine contrast-negs, the highest in the tree
at 2.05/1k, of which six are habit.

## L6 — the seven edits

| rule | OLD | NEW |
|---|---|---|
| 6 (state the fact) | `$\Phid_4$ is correspondingly absent at $k=6$, tested and not merely assumed` | `... absent at $k=6$, which was tested` |
| 11 (the body does not re-argue warrant) | `so what is reported is the minimal one and not merely one that works` | `so the denominator reported is the minimal one` |
| 12 (novelty is a status) | `this is the known leading diagonal in integer form, not a new fact` | `this is the known leading diagonal in integer form` |
| — (paired construction) | `the collision is not only that the square column reproduces \cite{abz2018}, but that three statements this paper leans on are theirs` | `the square column reproduces \cite{abz2018}, and three statements this paper leans on are theirs` |
| — (scope by negation) | `All four residue classes stabilise here, not just the even ones.` | `All four residue classes stabilise here, the odd ones included.` |
| 12 | `it is a claim about their proof, not a new theorem` | `it is a claim about their proof` |
| 10 (titles name a topic) | `\paragraph{The square column's reach is also not new.}` | `\paragraph{The square column's reach.}` |

`known` in the third row already carries the non-novelty, and the sentence
before the sixth already says "the argument's shape transports, its statements
do not" — both trailing negations were restating their own paragraph.

**Kept in L6, with the reason:** `degree $d$, not $d'$`; `period 6 is 2 and 3
acting independently, not a primitive sixth root`; `a per-tip series, not the
partition numbers`. Each names the value the reader would otherwise assume.

## Result

| | before | after |
|---|---|---|
| L6 contrast-neg | 2.05/1k | **0.69/1k** |
| L6 mean sentence | 25.4 | 25.2 |
| L overall contrast-neg | 1.00/1k (2.52x control) | **0.82/1k (2.06x)** |

## Gates

`paper/verify_l_papers.py` 336 checks green, 23 of them RED controls and every
one fired. `tests/gate_l_paper_verifier.py` green.

`scripts/l_trim_gate.sh check 5` is **RED, and was RED at `HEAD` before this
change** — it reports L5 dropping its last `\cite` of seven keys and L6 of
`abmz2022`. Checked rather than assumed: the same two failures, with the same
key lists, appear when the edit is removed and the gate is run against the
committed text. `abmz2022` appears zero times in L6 both before and after.
That red is a pre-existing finding about the citation baseline and is not this
round's; it is recorded here because a round that commits under a red gate has
to say which red and why it is not its own.
