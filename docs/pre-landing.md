# Pre-landing checklist

Written 2026-08-19 against `184664d`. Reviewed 2026-08-22 against `2e1355b`,
working tree clean, `master` == `origin/master`.

Tracked, at the root, since `e0db590` — which contradicts what the first draft
of this header said, so: root-level exempts it from `gate-docs-index` (that gate
scopes to `docs/*.md`, so no `docs/README.md` line is owed), and
`gate-citations` scopes to every tracked `*.md` and does cover it. Both green at
`2e1355b`. If it ever moves under `docs/`, it owes the index line.

**The rule this list defines:** when every box below is either checked or struck
with a one-line reason, the repo is ready to publish. Nothing else is a
prerequisite, and anything not on the list is post-landing work.

**The re-baseline rule.** Section B is green *at a revision*, not in the
abstract. Call it **R** — the revision that actually gets published. Every `[x]`
in section B carries the revision it was measured at. When `HEAD` moves past
that revision, the box is not done, it is **stale**: written `[~]`, with the
measurement kept because it still says what the command does and what it once
found. A `[~]` box re-runs at R like an unticked one. Section B closes only when
every box in it reads `[x]` at one and the same R, and `git rev-parse HEAD`
still returns R when the flip happens.

Sections A and C are jasonp's alone — no machine can close them. Section B is
mine, and every item in it is a command with a green/red answer. Section D is
already closed and is here so that nobody re-opens it during the landing.

---

## A. Decisions with no default (blockers by definition)

- [ ] **Flip `origin` to public.** `git@github.com:jhparkerb/polyplets.git` is
      private today. This is the landing action itself; everything else is
      preparation for it.
- [ ] **Licence.** There is no `LICENSE` file — and **86 Lean files already
      assert one**: `Copyright (c) 2026 Jason H Parker ... Released under
      Apache 2.0 license as described in the file LICENSE`, naming a file that
      does not exist in `polyplets/` or at the root. The tree mixes code (C++, Go,
      Python, Lean), data (banked rows, b-files), and prose (the manuscripts) —
      a single choice may not fit all three. A public repo with no stated terms
      is all-rights-reserved by default, which is a position, but pick it
      deliberately if that is the answer.
- [x] ~~**`triangle-structure` and `half-measure`.**~~ **Closed by inspection
      2026-08-22: both are on `origin` now**, so the decision made itself. 65
      citations across 25 campaign records point into them (21 and 10 by
      declaration count, unchanged since 08-19), and `gate-citations` is green
      at `2e1355b` with its `unmerged branch \`X\`` declarations verified
      against the refs. What is left is not a decision but a wording question
      for C: the gate's own summary line says "a reader who clones only the
      published branch cannot follow them", which is true of a default `git
      clone` and false of a `git fetch origin triangle-structure`. If the
      README does not say the branches are there, they are unfindable.
- [ ] **Does `docs/` go public?** It is the campaign record — plans,
      postmortems, `lessons-learned.md`, the reviewer-tier map, the acceptance
      queue. `README.md` links into it in five places, so excluding it is not a
      no-op edit. (`docs/viva-*.md` and `docs/drill*.md` are gitignored and
      stay local regardless — confirmed: `git ls-files | grep viva` is empty.)
- [ ] **Does `results/ghostship/` go public?** A graded experiment on the
      project's own process, including the grading and the divergence record.
      `docs/lessons-learned.md` decides what it licensed; it does not
      decide whether a stranger reads it.
- [ ] **The L ledgers' "human verification: none".** All nine say it. Either
      you read enough of a paper to replace that with a specific per-result
      line — which is what `docs/publication-split.md` §1 requires the block to
      carry — or the papers ship saying it, which is honest and is what the
      draft banners already announce. Per paper, not in aggregate.
- [ ] **Byline per L paper.** `docs/publication-split.md` §1 makes this a
      per-paper decision, explicitly not a policy. Nine papers, nine answers.
- [ ] **P1.** `paper/technical-report.tex` is ~40% built, and
      `docs/publication.md` holds findings on it that are
      unapplied by design. Publish the repo without it (the current strategy
      doc's Track D says the repo is the publication and P1 is later), or hold
      the landing for it.
- [ ] **Machine names and paths in the tree.** 27 tracked files contain
      `/Users/jasonp`, 10 contain `dalby.jhpb.org` (including
      `scripts/g2_fleet_launch.sh` and `results/ns_a40/dalby-run-evidence/`) —
      both counts one higher than on 08-19, so this drifts upward on its own
      and a scrub decided today needs re-measuring at R. Your email is in
      `paper/technical-report.tex` and `paper/technical-report-draft.tex` by design.
      Fine, or scrub — but decide once rather than per-file after the fact.
- [ ] **The history goes public, not just the tree.** The flip publishes 1475
      commits on `master` and 1585 across all refs, not the 27 files above.
      Scrubbing `HEAD` would leave every one of those strings reachable by
      `git log -S`; the only scrub that works on history rewrites it, which
      breaks every commit hash the campaign records cite (`gate-citations`
      counts 56 history citations). So the realistic answers are "fine" —
      which is a decision about the history, and should be written down as
      one — or "publish a fresh squashed repo and keep this one private",
      which is a different landing than the one this list describes.
- [ ] **The other 44 branches.** `origin` carries 45 refs besides `HEAD`:
      `triangle-structure`, `half-measure`, `lastditch` (where a(41) was
      computed), `even-keel`, `deploy/reach-modp-blocked`, and twenty-odd
      `explore/*`. Flipping the repo publishes all of them. Two are load-bearing
      for citations (see above) and one is a(41)'s provenance; the rest are work
      in whatever state it was abandoned in. Publish all, prune to the cited
      three plus `master`, or leave the rest and say in the README that
      `explore/*` is unmaintained.
- [ ] **OEIS.** Nothing in `oeis/` or `oeis/wave2/` auto-submits, and the
      submission gate is yours and unchanged. This box exists so the list can
      close; it is not a prompt.

## B. Mechanical, and green at the exact published revision

Everything here was green at some revision. What the list wants is green at
**the** revision — R — run once, in this order. See the re-baseline rule above
for what `[~]` means.

**Baseline as of 2026-08-22: every `[x]` below went `[~]`.** They were measured
at `184664d` and `813f4e0`; `HEAD` is `2e1355b`, which is 95 commits, 159 files
and +75,879 lines later — `results/a41/` and the whole Undertow and Skeletonkey
run among them. Nothing here is known-red; it is unmeasured at anything anyone
would publish.

- [~] `/simplify` over `simplified..HEAD` — **run 2026-08-19** (`813f4e0`).
      Two contained cleanups in `scripts/residual_cells.py`: a dead second loop
      in `trigger_lines`' prose widening, and four list comprehensions built
      twice each in `facts()`. Regenerated `results/residual-cells.md` is
      byte-identical and the selftest's 5 green + 15 RED controls all fire.
      Skipped deliberately: the four separate readers of `results/triangle.txt`
      (the reason is already written at `bfile_gate.py`'s loaders), and
      `confetti_prime_check.py`, which the assembly gate runs as delivered.
      **The tag never advanced, and the delta above is no longer the delta.**
      `simplified` is at `4eaa994`, 89 commits behind `2e1355b`; the pass to run
      at R is `4eaa994..R`, of which the two `residual_cells.py` cleanups are
      already landed history. Per the standing rule this pass comes *before* the
      landing, not as part of it.
- [~] `make` — the gate suite. **Was RED on a clean Linux clone** and is now
      green there: 408 s, rc=0, at `813f4e0` on ayr. The `gates` recipe pipes
      its sub-make through `tee` and needs `set -o pipefail`, and make's default
      `SHELL` is `/bin/sh` — bash in sh mode on gympie, dash on Debian. It
      failed in 0 s, before a single gate ran, and the previous clean-clone run
      predates the `tee`/GATELOG block that introduced it. Recipes take
      `/bin/bash` explicitly now (`1864a6b`). **33 gates now**, not the 32 of
      08-19 — `GATE_TARGETS` gained `gate-undertow-congruence`. (`gate-motley-par`
      is a 34th recipe held out of `GATE_TARGETS` on purpose, with the reason
      written at the recipe.) Re-run at R.
- [ ] `make ns-gates` — the production engine's own suite, ~787 s.
- [x] **Nothing secret-shaped is tracked.** Checked 2026-08-22 at `2e1355b`:
      `git grep` for `ghp_`, `github_pat_`, `AKIA…`, `BEGIN … PRIVATE KEY` and
      assigned `api_key` literals returns nothing, and no PDF was ever added in
      the history (`git log --all --diff-filter=A -- '*.pdf'` is empty), so
      `.gitignore`'s first rule held retroactively and not just at `HEAD`. This
      is the one box on the list that is cheap enough to re-run at R for free;
      re-run it there anyway, because it is evidence and not an assumption.
- [~] `python3 paper/verify_l_papers.py` — 336 checks, 23 RED controls, all
      fired. Green at `184664d`; re-run at R.
- [~] `python3 paper/verify_technical_report.py` — 781 checks, 0 failures.
      Green at `184664d`; re-run at R.
- [ ] `make -C paper` — 11 PDFs, ~14 s. They are gitignored, so a visitor
      builds them. If built PDFs should be downloadable without a TeX Live,
      they have to be release assets, which is a separate decision (see C).
- [~] `cd polyplets && lake build` — **was RED, now green** (`79dbc6e`).
      Every one of the 8643 module targets built; the root `Polyplets.lean`,
      which imports them all, failed: `kingConnected_image` was declared
      independently in `Symmetry` and in `GapWalkStacks`, and only the aggregate
      sees both. Red since the Notary piece-B wave, with `PROOF-STATUS.md`
      saying green throughout, because no `make` gate runs Lean — ayr and dalby
      have no toolchain. Renamed the newer one to
      `kingConnected_image_of_adj_iff`; rebuilt 8645 jobs, 0 errors. The build
      note in `PROOF-STATUS.md` now says the aggregate is the only thing that
      catches this, and that it is a human typing the command on gympie.
      Being a human-on-gympie step with no gate behind it, this is the `[~]`
      most likely to have gone red unnoticed: 88 `.lean` files are tracked now.
- [ ] **`scripts/clean_clone_check.sh` re-run at the published revision.** Last
      real run was `0171909` on ayr; `HEAD` is `2e1355b`, 100-odd commits on.
      This is the item most
      likely to find something, because it is the only one that runs on
      evidence a reader actually has — it caught all four defects last time and
      none of them were visible from this working tree.
- [ ] `make && scripts/dalby_term.sh 26` on the clean clone — prints
      `a(26) = 102607513847014153892`, ~23 s on 32 cores. This is the command
      the README puts on the front page, so it is the one that must not lie.
- [ ] Working tree clean, `master` pushed, and the published revision is the
      one every number above was measured at — that is, every box above reads
      `[x]` at R and `git rev-parse HEAD` is R. Clean and pushed are true at
      `2e1355b`; the third clause is what 08-19 got wrong, by ticking boxes at
      a revision that then moved 95 commits.

- [x] **The tracked-PDF invariant is a gate now**, not a printed line.
      `tests/gate_no_copyright_pdfs.py`, in `GATE_TARGETS` (`5a7cf4d`): no PDF
      is tracked anywhere, with a RED control for a tracked PDF and a second
      for a git query that fails and would otherwise read as a clean tree.
      `.gitignore`'s first rule — "copyrighted papers stay local, never
      pushed" — had nothing enforcing it; a `git add -f` would have sat tracked
      until somebody ran the clean-clone script by hand and read a line that set
      no exit code.

## C. Front door — what a stranger touches in ten minutes

- [ ] **README's opening still matches reality at the published rev**: the
      claim, the one reproduce command, the link to
      `results/provenance-table.md`. **It did on 08-19 and does not now** — this
      box went red on its own, which is the argument for the re-baseline rule.
      Three drifts at `2e1355b`:
      - The headline is `a(40)` (line 8) and line 120 says "the sequence closing
        at a(40)", while `results/a41/PROVENANCE.md` is on `master` banking
        `a(41) = 393811462683918679824582849262105`, computed on dalby 08-20 —
        the first term past the enumeration ladder, and got a different way
        (real sweep to H=19 plus the Undertow-pinned tower). The front door
        under-claims the tree by a term, and by the more interesting term.
        Deciding how the README says that is section A work, not a typo fix:
        a(41) rests on the diagonal tower, not on two independent enumerations,
        so it does not belong in the same sentence as a(40) without its tier.
      - "`polyplets/` — the Lean 4 formalization (34 files, sorry-free)". 88
        `.lean` files are tracked.
      - Nothing on the front page says `triangle-structure`, `half-measure` and
        `lastditch` exist on `origin`, which is now the only way a reader
        follows 65 campaign citations and a(41)'s branch of origin.
- [ ] **A citable identifier.** OEIS entries will link here. A moving `master`
      is not a citation target: a tagged release, or a Zenodo DOI, or a
      `CITATION.cff` — none of the three exists now. Cheapest is a tag plus
      `CITATION.cff`; the DOI is the one that survives the repo moving.
- [ ] **Release assets, if any.** The eleven PDFs and possibly the b-files.
      Only worth doing if the answer to "does a visitor need a TeX Live" is no.
- [x] **`literature/` stays local.** Verified at `813f4e0` in the clone itself:
      `literature/ pdfs in the clone: 0 (must be 0), tracked text files: 5`. Five,
      not three — `README.md` and `polyplets-2024-2026.bib` join the three the
      docs named, and three places that said otherwise are corrected
      (`3554c66`). The check in `clean_clone_check.sh` used to ask whether
      `literature/` existed at all and call the clone's honest "yes" the wrong
      answer; it counts PDFs now.
- [ ] **The draft banners stay on.** Every L paper carries one; L6, L8 and L9
      carry a second naming what the priority pass found. They are the reason
      the papers can ship at all with the ledger reading as it does.

## D. Closed — do not re-open during the landing

- Acceptance queue items 1–6: **all closed** (`docs/publication.md`).
- Ticker Tape (H=19): priced at ~197 GB against dalby's 125 and ~26 days,
  declined. The ladder ends at H=18 and `a(n)` is rule-independent for n ≤ 35.
- The k=7 perimeter-defect census: 76–179 days on the 76-way pool. Not
  approved, not launched, and not a publication prerequisite.
- P19 holdout and the cross-ISA a(40) recount: on-demand only, declined.
- The enumeration ladder itself: closed at a(40) on 2026-07-06.

---

## Revisions

- **2026-08-19, `184664d`** — written.
- **2026-08-22, `2e1355b`** — reviewed against the tree, 95 commits on. Added
  the re-baseline rule and demoted five section-B boxes to `[~]`; closed A's
  branch item (`triangle-structure` and `half-measure` are on `origin` now);
  added three A items the first draft did not cover (the history, the other 44
  refs, and the credential scan, which is in B because it is a command); found
  C's README box red on its own (a(41), the Lean file count, the branches);
  corrected the header, which described this file as untracked while it was
  tracked. Wired it into `docs/handoff.md`'s pointer block — nothing referenced it
  before, which is how a landing checklist gets 95 commits out of date.
