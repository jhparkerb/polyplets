# Lessons learned — working draft

Distilled 2026-07-06 from the project postmortem conversation (jasonp +
Claude); to be iterated. Caveat (jasonp): somewhat focused on the
submit-many-terms OEIS project shape — generalize before reusing for
other project types. The six failure CLASSES below absorb ~15 specific
incidents; the instances are evidence, not the lesson. Don't overfit to
them: mistakes will happen — the classes are what's addressable at
project START.

## A. Lessons must be encoded as machinery, not advice

Instances: the per-worker RAM OOM that killed a tmux server; the phantom
bisection off filtered diagnostics; the tee-before-mkdir launch failure
(twice, weeks apart). All were "we knew better" — the knowledge existed
as prose, and prose doesn't execute.

Day one: ONE blessed launch path (script computes budgets, mkdirs,
captures PIDs — used even when overkill); one blessed diagnosis path
(full output, never filtered, before theorizing); any operational lesson
is folded into the script that failed, same day, or it will repeat.

## B. Everything that informs a decision carries provenance and an expiry

Instances: the A1 stale-binary incident (fix uncommitted on one host
while production ran); RAM/cost estimates that silently outlived two
engine generations (n=34 dmirror "90-160GB"; M(17) "4-10h" vs the
measured 25min/n=13 -> ~26-30h).

Day one: binaries carry baked revs + clean-tree gates (built here only
AFTER the incident); planning numbers state their derivation basis and
what invalidates them; the launch checklist asks "is this estimate's
basis still true?"

## C. The knowledge base is a repo artifact, human-auditable, with deletion discipline

Instances: the 91bdcdc cleanup deleted load-bearing files (gates, GF
data, a submission-provenance script) — four separate later
restorations, including a silent validation outage; environment
knowledge trapped in AI memory (ayr's old Go, host quirks, budgets) —
invisible to the human; banked conclusions re-derived from scratch at
least twice.

Day one: lab-notebook repo / publication repo SPLIT (kills the
end-of-project big tidy and protects load-bearing paths from cleanup
pressure); MACHINES.md and its kin in the lab repo where the human can
read and correct them; "delete requires a reference sweep" as a standing
rule; the AI checks the index before claiming discovery.

## D. The result store is infrastructure, built first

Instance: pervasive undesigned recomputation — every experiment
re-derived low-n prefixes (distinct from DESIGNED recompute, i.e. the
full-chain regression, which was validation and load-bearing).

Day one: content-addressed banked results; runs verify against stored
hashes instead of recomputing. ~Two days of build that pays the whole
campaign.

## E. The close is designed at the start

Instances (four faces of one failure — publication accretes continuously
or it avalanches): the paper stayed an early-era artifact until close
week, then needed a full restructure + five review rounds + a
claims-checker retarget that caught three real errors in our own tables;
the confidence-tier system was retrofitted and back-propagated; the
human-authorship/understanding debt (%C rewrite, the viva) surfaced days
before intended submission; a(34)'s missing holdout (P_16) was
DISCOVERED at the frontier rather than chosen.

Day one: tiers assigned at birth in PROVENANCE; the paper section is
drafted when the result banks; the human's explain-back paragraph is
part of banking a result; campaign end-conditions analyzed up front
("what does the LAST term's validation story look like?"); and a
mid-project close-rehearsal: "if we had to publish tomorrow, what's
missing?" — asked at a(30), it surfaces P_16, the tier retrofit, and the
authorship debt with weeks in hand.

## F. The collaboration itself gets a written contract, revisited

Instances: working-register norms (verbosity, codenames, menus vs
monologues, artifacts vs conversation) accreted through friction, one
correction at a time — some took five; model tiering never happened
(frontier model babysitting tmux for days).

Day one: an hour writing the contract — register, who drafts what
(human drafts outward prose FROM the data; AI fact-checks — the reverse
of this project), model-tier policy with per-task downshift proposals,
when the AI asks vs acts. Mid-project: a deliberate "how is this
working" retrospective instead of waiting for the yelling.

## Relative weight (Claude's read, to argue)

E is where the most days went; C is where the most trust went; A is the
cheapest to fix.

## Parked for later drill-down

Reference-implementation approaches (from the same conversation):
1. shared-heart — one audited transition function, two shells
   (persuasion-first; forfeits independence);
2. foreign-method — genuinely different algorithm as small-n validator
   (independence-first; persuades nobody about the frontier);
3. refinement-chain — a ladder of implementations, each step a small
   diffable optimization, so auditability transports from naive to fast;
4. machine-checked correctness argument (the Lean thread points here).
Key tension: persuasion wants maximal shared code, independence wants
zero — one program cannot be both.
