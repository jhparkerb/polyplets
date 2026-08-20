# Pre-landing checklist

Written 2026-08-19 against `184664d`, working tree clean, `master` == `origin/master`.
Untracked and root-level on purpose: it trips no gate (`gate-docs-index` and
`gate-citations` both scope to `git ls-files`). If it ever gets committed under
`docs/`, it needs a line in `docs/README.md` or `gate-docs-index` goes RED.

**The rule this list defines:** when every box below is either checked or struck
with a one-line reason, the repo is ready to publish. Nothing else is a
prerequisite, and anything not on the list is post-landing work.

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
- [ ] **`triangle-structure` and `half-measure`.** 65 citations across 25
      campaign records point into these two branches; neither is on `origin`.
      `gate-citations` handles it either way (per-file `unmerged branch \`X\``
      declarations, verified against the ref when it is present), so this is a
      publication decision and not a defect: push them, or ship citations into
      refs the reader does not have.
- [ ] **Does `docs/` go public?** It is the campaign record — plans,
      postmortems, `lessons-learned.md`, the reviewer-tier map, the acceptance
      queue. `README.md` links into it in five places, so excluding it is not a
      no-op edit. (`docs/viva-*.md` and `docs/drill*.md` are gitignored and
      stay local regardless — confirmed: `git ls-files | grep viva` is empty.)
- [ ] **Does `results/ghostship/` go public?** A graded experiment on the
      project's own process, including the grading and the divergence record.
      `results/ghostship/DISPOSITION.md` decides what it licensed; it does not
      decide whether a stranger reads it.
- [ ] **The L ledgers' "human verification: none".** All nine say it. Either
      you read enough of a paper to replace that with a specific per-result
      line — which is what `docs/publication-split.md` §1 requires the block to
      carry — or the papers ship saying it, which is honest and is what the
      draft banners already announce. Per paper, not in aggregate.
- [ ] **Byline per L paper.** `docs/publication-split.md` §1 makes this a
      per-paper decision, explicitly not a policy. Nine papers, nine answers.
- [ ] **P1.** `paper/technical-report.tex` is ~40% built, and
      `docs/main-paper-audit-2026-08-18.md` holds findings on it that are
      unapplied by design. Publish the repo without it (the current strategy
      doc's Track D says the repo is the publication and P1 is later), or hold
      the landing for it.
- [ ] **Machine names and paths in the tree.** 26 tracked files contain
      `/Users/jasonp`, 9 contain `dalby.jhpb.org` (including
      `scripts/g2_fleet_launch.sh` and `results/ns_a40/dalby-run-evidence/`).
      Your email is in `paper/technical-report.tex` and
      `paper/polyplets-report.tex` by design. Fine, or scrub — but decide once
      rather than per-file after the fact.
- [ ] **OEIS.** Nothing in `oeis/` or `submissions/oeis/` auto-submits, and the
      submission gate is yours and unchanged. This box exists so the list can
      close; it is not a prompt.

## B. Mechanical, and green at the exact published revision

Everything here was green at some revision. What the list wants is green at
**the** revision, run once, in this order.

- [x] `/simplify` over `simplified..HEAD` — **done 2026-08-19** (`813f4e0`).
      Two contained cleanups in `scripts/residual_cells.py`: a dead second loop
      in `trigger_lines`' prose widening, and four list comprehensions built
      twice each in `facts()`. Regenerated `results/residual-cells.md` is
      byte-identical and the selftest's 5 green + 15 RED controls all fire.
      Skipped deliberately: the four separate readers of `results/triangle.txt`
      (the reason is already written at `bfile_gate.py`'s loaders), and
      `confetti_prime_check.py`, which the assembly gate runs as delivered.
      **Tag advance still pending** — it moves once run7 is green.
- [x] `make` — the gate suite. **Was RED on a clean Linux clone** and is now
      green there: 408 s, rc=0, at `813f4e0` on ayr. The `gates` recipe pipes
      its sub-make through `tee` and needs `set -o pipefail`, and make's default
      `SHELL` is `/bin/sh` — bash in sh mode on gympie, dash on Debian. It
      failed in 0 s, before a single gate ran, and the previous clean-clone run
      predates the `tee`/GATELOG block that introduced it. Recipes take
      `/bin/bash` explicitly now (`1864a6b`). 32 gates: one is new, see below.
      Re-run at the final rev inside run8.
- [ ] `make ns-gates` — the production engine's own suite, ~787 s.
- [x] `python3 paper/verify_l_papers.py` — 336 checks, 23 RED controls, all
      fired. Green at `184664d`; re-run inside run7.
- [x] `python3 paper/verify_technical_report.py` — 781 checks, 0 failures.
      Green at `184664d`; re-run inside run7.
- [ ] `ALLOW_PARTIAL=1 python3 paper/verify_claims.py` — 425 of 428, ~912 s.
      The three skipped read `runs/sym32`, which is run output; the flag is how
      a reader says they know which three.
- [ ] `make -C paper` — 11 PDFs, ~14 s. They are gitignored, so a visitor
      builds them. If built PDFs should be downloadable without a TeX Live,
      they have to be release assets, which is a separate decision (see C).
- [x] `cd polyplets && lake build` — **was RED, now green** (`79dbc6e`).
      Every one of the 8643 module targets built; the root `Polyplets.lean`,
      which imports them all, failed: `kingConnected_image` was declared
      independently in `Symmetry` and in `GapWalkStacks`, and only the aggregate
      sees both. Red since the Notary piece-B wave, with `PROOF-STATUS.md`
      saying green throughout, because no `make` gate runs Lean — ayr and dalby
      have no toolchain. Renamed the newer one to
      `kingConnected_image_of_adj_iff`; rebuilt 8645 jobs, 0 errors. The build
      note in `PROOF-STATUS.md` now says the aggregate is the only thing that
      catches this, and that it is a human typing the command on gympie.
- [ ] **`scripts/clean_clone_check.sh` re-run at the published revision.** Last
      real run was `0171909` on ayr; HEAD is `184664d`. This is the item most
      likely to find something, because it is the only one that runs on
      evidence a reader actually has — it caught all four defects last time and
      none of them were visible from this working tree.
- [ ] `make && scripts/dalby_term.sh 26` on the clean clone — prints
      `a(26) = 102607513847014153892`, ~23 s on 32 cores. This is the command
      the README puts on the front page, so it is the one that must not lie.
- [ ] Working tree clean, `master` pushed, and the published revision is the
      one every number above was measured at. (Both true at `184664d`; they
      stop being true the moment section B starts.)

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
      `results/provenance-table.md`. It does today.
- [ ] **A citable identifier.** OEIS entries will link here. A moving `master`
      is not a citation target: a tagged release, or a Zenodo DOI, or a
      `CITATION.cff` — none of the three exists now. Cheapest is a tag plus
      `CITATION.cff`; the DOI is the one that survives the repo moving.
- [ ] **Release assets, if any.** The eleven PDFs and possibly the b-files.
      Only worth doing if the answer to "does a visitor need a TeX Live" is no.
- [x] **`papers/` stays local.** Verified at `813f4e0` in the clone itself:
      `papers/ pdfs in the clone: 0 (must be 0), tracked text files: 5`. Five,
      not three — `README.md` and `polyplets-2024-2026.bib` join the three the
      docs named, and three places that said otherwise are corrected
      (`3554c66`). The check in `clean_clone_check.sh` used to ask whether
      `papers/` existed at all and call the clone's honest "yes" the wrong
      answer; it counts PDFs now.
- [ ] **The draft banners stay on.** Every L paper carries one; L6, L8 and L9
      carry a second naming what the priority pass found. They are the reason
      the papers can ship at all with the ledger reading as it does.

## D. Closed — do not re-open during the landing

- Acceptance queue items 1–6: **all closed** (`docs/acceptance-queue.md`).
- Ticker Tape (H=19): priced at ~197 GB against dalby's 125 and ~26 days,
  declined. The ladder ends at H=18 and `a(n)` is rule-independent for n ≤ 35.
- The k=7 perimeter-defect census: 76–179 days on the 76-way pool. Not
  approved, not launched, and not a publication prerequisite.
- P19 holdout and the cross-ISA a(40) recount: on-demand only, declined.
- The enumeration ladder itself: closed at a(40) on 2026-07-06.
