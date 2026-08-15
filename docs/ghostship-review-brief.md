# Ghost Ship review — panel brief

2026-08-15. Three lanes, one wave, desk-only. Mission in one sentence:
**tear apart the pre-registration in `docs/ghostship-preregistration.md`
before anything is sealed — what survives becomes the protocol.**

## Common rules

- Desk work only; nothing executes anywhere; reads/greps/`git log` fine.
- One output file per lane under `results/ghostship/review/`; write as you
  go; final report = path + three sentences.
- Do not edit any file other than your output. Do not commit.
- Context to read first, in order: `docs/ghostship-preregistration.md`
  (the object under review); `docs/offside-brief.md` and
  `results/offside/B-adversary.md` + `results/offside/C-replay.md` (the
  court flow this experiment is a comparison point for, and the panel
  style); the Li et al. paper at
  `/Users/jasonp/.claude/jobs/fd684800/tmp/gc-paper.pdf` §3–§5 + Table 2
  (the flow being imitated). The operator is a registered skeptic; the
  protocol's job is to produce a verdict he can trust either way.

## Lane R1 — methodologist (output: `review/R1-method.md`)

Attack the experiment's ability to answer its own three questions. At
minimum: confounds between Q1 and Q2 (no-court AND async-steering change
together — can any outcome be attributed?); whether the metrics in §5
actually measure the questions in §1 (e.g. "verified claims" measures the
loop plus the post-run court, not the loop); grading bias (the lead runs
the court, then grades the rival flow — name the blinding fix or declare
it unfixable); baseline validity (king twigs / Offside are different
problems — is per-token comparison meaningful at all, and if not, what
weaker claim IS supportable?); sample size 1 (what can a single run ever
license? phrase the strongest honest conclusion the design can yield);
and the stop rules (do two dry sessions bias toward early failure?).
Separate fixable-with-an-edit from structural-accept-and-scope-down.

## Lane R2 — the Goodhart lane (output: `review/R2-goodhart.md`)

You are a Ghost Ship session that wants to LOOK good. Given only what a
session sees (§2's inputs) and how it will be graded (§5, §7), enumerate
the ways to score well without real progress: claim-splitting to inflate
counts; receipts that technically resolve but carry no content;
direction-restating as reframing to dodge the judgment-failure metric;
caveat-laundering so decay sampling passes; bulletin-fishing. For each
gaming vector: can the grader detect it post-hoc, and what one-line
protocol change closes it? Also the inverse: name any metric that
punishes honest behaviour (e.g. does the claims-per-session incentive
punish a session that spends itself verifying a predecessor's claim?).

## Lane R3 — mechanics and the C4 check (output: `review/R3-mechanics.md`)

Concrete feasibility. (a) The thread: read `results/convex-polyplets.md`
and its cross-references and judge C4 honestly — is Convex Polyplets
too easy (rich banked state to paraphrase), too hard (needs compute the
sandbox bans), or right? If wrong, propose one alternative of the same
shape from the tree, with the same scrutiny applied. (b) The sandbox:
enumerate the exact file list a Ghost Ship session needs for that thread
(corpus slice, filtered git log, tool availability) and what must be
EXCLUDED so re-derivation detection stays meaningful; check the slice is
self-contained (no dangling references that would make sessions flail on
missing files — list any). (c) Session mechanics: what does a session
need to be told about writing reports so 14 of them stay readable
(report format, length cap, claims-block); does 3/day leave real bulletin
windows given the operator's actual hours as visible in git history?
(d) Name anything in the protocol that cannot be built with existing
tooling.

## Stop conditions

One pass; file and stop; padding is a defect. If two lanes converge on
the same fix independently, the lead treats it as adopted.
