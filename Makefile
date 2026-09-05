# Recipes run under bash, explicitly. The `gates` recipe needs `set -o
# pipefail` to see through its `tee`, and make's default SHELL is /bin/sh --
# which is dash on Debian and rejects that option outright. It worked on gympie
# (macOS /bin/sh is bash in sh mode) and broke `make` at step one on a clean
# Linux clone, 2026-08-19.
SHELL := /bin/bash

CXX ?= c++
CXXFLAGS = -std=c++20 -Wall -Wextra -Werror

# Provenance baked at BUILD time (docs/observability.md): a compiled binary
# outlives the source state, so it must report the commit it was BUILT at, not
# whatever the tree is now. GIT_REV carries a -dirty suffix when the tree differs
# from HEAD at all (untracked included), matching Python obs.py's porcelain check.
# cpp/obs.h reads these via -D; absent them it falls back to "unknown".
#
# Probed ONCE, at the top level, and exported. `make gates` is ~40 nested makes
# now (one per gate, so each can be timed), and every Makefile parse used to
# re-run all of this -- including `git status --porcelain`, a full worktree
# walk, and two compiler --version probes below. Sub-makes inherit these from
# the environment; MAKELEVEL is 0 only in the outermost one.
ifeq ($(MAKELEVEL),0)
GIT_REV    := $(shell git rev-parse --short HEAD 2>/dev/null || echo unknown)
GIT_DIRTY  := $(shell test -n "$$(git status --porcelain 2>/dev/null)" && echo -dirty)
BUILD_TIME := $(shell date +%Y-%m-%dT%H:%M:%S%z)
export GIT_REV GIT_DIRTY BUILD_TIME
endif
CXXFLAGS += -DGIT_REV='"$(GIT_REV)$(GIT_DIRTY)"' -DBUILD_TIME='"$(BUILD_TIME)"'

# -Wno-error=restrict is a gcc-only workaround (gcc-12 false positive on the
# Redelmeier generator, see build/g2 below). clang rejects the unknown flag, so
# apply it only when the compiler is gcc; empty for clang.
ifeq ($(MAKELEVEL),0)
RESTRICT_FLAG := $(if $(findstring clang,$(shell $(CXX) --version 2>/dev/null)),,-Wno-error=restrict)
export RESTRICT_FLAG
endif

# The Redelmeier kernel (build/g2) is measurably faster built with clang on
# aarch64: ~9% over gcc-15 on Neoverse-N1 (measured, results/terminal-velocity.md),
# and gcc PGO / -mcpu gave nothing. Prefer clang for the OPTIMIZED g2 only, per
# box (clang++-19 on dalby, clang++ on mac/gympie), falling back to $(CXX) where
# clang is absent (e.g. ayr uses g++). g2_asan stays on $(CXX): keeping the two
# builds on different compilers turns gate-g2 check D into a two-compiler count
# cross-check for free.
ifeq ($(MAKELEVEL),0)
G2CXX := $(shell command -v clang++-19 2>/dev/null || command -v clang++ 2>/dev/null || echo $(CXX))
G2_RESTRICT := $(if $(findstring clang,$(shell $(G2CXX) --version 2>/dev/null)),,-Wno-error=restrict)
export G2CXX G2_RESTRICT
endif

.PHONY: gates gates-deep gates-force timed-% print-% gate-motley-crt gate-g1 gate-g2 gate-euler gate-strip-cert gate-strip-fast \
        gate-sig-fold \
        gate-king-grid gate-site-perim gate-multidirected gate-convex-dfinite \
        gate-middle-kingdom gate-mk-dir4-perim gate-dir4-perim-alg \
        gate-compile-db gate-citations gate-docs-index gate-no-copyright-pdfs \
        gate-l-paper-verifier gate-p-paper-verifier gate-receipts \
        gate-residual-cells gate-cutcount-assembly \
        gate-perimeter-min gate-perimeter-defect \
        gate-perimeter-min-shard clean install \
        ns-gates ns-gate-arch ns-gate-regression ns-gate-fold ns-gate-resume \
        ns-gate-parallel ns-gate-resume-boundaries ns-gate-u128 ns-gate-holes \
        ns-gate-verify ns-gate-kink ns-gate-kink-column ns-gate-kink-stage-file \
        ns-gate-kink-worker-cli ns-gate-persistent-worker ns-gate-asan \
        ns-gate-frontier-zstd ns-gate-diag-pins \
        ns-driver0 \
        build/ns/orchestrate build/ns/runcat build/ns/predict build/ns/combine build/ns/verify \
        papers papers-verify papers-clean papers-list

# The C++ ns binaries used to be on that .PHONY list. They are real files with
# real recipes and complete prerequisites (their source plus every core/ header),
# so declaring them phony did two things, neither wanted: recompiled all four on
# every single make, and told make to ignore the prerequisites that say when they
# actually need it. It also defeated the input gating -- a gate whose declared
# input is the binary it runs can never skip if the binary is rebuilt each time.
# The Go ones stay: build/ns/orchestrate bakes GIT_REV in at link time on
# purpose, and go build is cache-backed anyway.

# All currently existing gates.
# TODO(2026-08-19, from the simplify pass): nothing checks this list is
# complete.  A `gate-foo:` recipe that never reaches GATE_TARGETS is a check
# `make gates` does not run, which is the meta-version of the failure two of
# this week's commits fixed.  A lint wants an allowlist for the deliberate
# exclusions (papers, install-hooks, compile-commands), so it is its own change.
# Push tier vs deep tier. Several gates re-derive, at full size, a fact that is
# settled and does not move -- a fold symmetry, a level-6 DP holdout, a hole
# convention. Those gates take $(GATE_DEEP): empty (the default) runs the push
# tier, --deep restores the full-size derivation. `make gates-deep` is the whole
# suite at full size; run it before a release, and whenever the code under a
# banked or size-limited check changes. Each such gate documents at its own
# recipe what --deep restores and why the push tier is enough.
GATE_DEEP ?=

GATE_TARGETS = gate-motley-crt gate-citations gate-docs-index gate-no-copyright-pdfs gate-receipts gate-provenance gate-residual-cells gate-cutcount-assembly gate-undertow-congruence gate-undertow-pairs gate-kink-oracle gate-severance-w1 gate-severance-w2 gate-severance-w3 gate-severance-depth5 gate-modp gate-makefile-wiring gate-bfiles gate-l-paper-verifier gate-p-paper-verifier gate-perimeter-min gate-perimeter-min-shard gate-perimeter-defect gate-g1 gate-g2 gate-sig-fold gate-tma gate-s2 gate-e0 gate-sym gate-symtm gate-subgroup gate-euler gate-driver gate-strip-cert gate-strip-fast gate-king-grid gate-site-perim gate-multidirected gate-convex-dfinite gate-middle-kingdom gate-mk-dir4-perim gate-dir4-perim-alg gate-compile-db

# The gate suite runs the gates CONCURRENTLY: they are independent processes
# over read-only fixtures, and the only two that write scratch state write to
# paths nobody else touches (gate_tma.py: runs/ckpt/gate_holes + runs/ckpt/gate_ih;
# gate_dir4_perim_alg.py: build/dir4_perim_null199.txt). Measured 2026-08-06 on
# gympie: 624 s serial -> 467 s at -j10, 16/16 GREEN. Parallelism is scoped to
# THIS target via a sub-make rather than MAKEFLAGS, deliberately: the ns-gates
# chain shares fixed scratch paths across targets (/tmp/ns_*, and gate_runfile
# runs twice under different env in ns-gate-frontier-zstd), so it has not been
# cleared for -j and must keep inheriting whatever the caller asked for.
#
# JOBS defaults to the PERFORMANCE core count on Darwin (10 on gympie, the hard
# cap per the box's budget), nproc on Linux. Override with `make JOBS=1 gates`
# to get the old serial run back -- worth doing when a gate goes RED, since 3.81
# has no --output-sync and concurrent gate output can interleave.
ifeq ($(shell uname -s),Darwin)
  JOBS ?= $(shell sysctl -n hw.perflevel0.logicalcpu 2>/dev/null || sysctl -n hw.ncpu)
else
  JOBS ?= $(shell nproc 2>/dev/null || echo 4)
endif

# The parallel run keeps its output live, and also lands in build/gates.log so
# that a RED gate can be NAMED at the end.  make 3.81 -- what macOS ships, and
# there is no gmake on gympie -- has no --output-sync, so the sub-make's
# "*** [gate-foo] Error 1" line is printed several hundred lines above the
# "*** [gates] Error 2" that ends the run.  A pre-push hook failing that way
# reports nothing usable: this recipe pulls the target names back out.
#
# The bracket has TWO formats and the first version of this knew only one.
# 3.81 prints "*** [gate-foo] Error 1"; GNU make 4.x -- 4.3 on ayr, 4.4.1 on
# dalby -- prints "*** [Makefile:2: gate-foo] Error 1", so `\[gate-` matched
# nothing and a red run on either Linux box printed an EMPTY list of red gates:
# the very failure this recipe exists to fix, in the same worked-on-gympie-only
# shape as the SHELL:=/bin/bash line at the top of this file.  The optional
# "file:line: " prefix is part of the pattern now (POSIX BRE, so BSD and GNU
# sed both take it), and a run that names no gate says so rather than printing
# an empty heading -- a red PREREQUISITE ("*** [build/g2]") is named by no
# gate line at all.
#
# A THIRD format now: the targets make runs are timed-gate-foo (see below), so
# the bracket reads "[timed-gate-foo]" or "[Makefile:2: timed-gate-foo]". The
# pattern takes any prefix and anchors on the last "gate-" in the bracket, which
# covers all three. tests/gate_makefile_wiring.py holds it to that.
# Ask make for the value of any variable: `make print-GATE_TARGETS`. Tools that
# need these lists should read them this way rather than sed the Makefile --
# which is how scripts/profile_gates.sh broke the day `ns-gate-fast:` grew a
# prerequisite and its scrape started returning the literal $(NS_FAST_PREREQS).
print-%:
	@echo '$($*)'

GATELOG = build/gates.log

# Every gate at full size -- the deep tier. Same targets, same assertions; the
# ones that bank or bound something re-derive it instead.
# ns-gate-fast is in here because two of its gates take $(GATE_DEEP) as well
# (the worker-CLI H=8 case): running only `gates` left their deep tier with
# nothing that ever restores it. Command-line overrides propagate to sub-makes.
gates-deep:
	$(MAKE) gates ns-gate-fast GATE_DEEP=--deep FORCE_GATES=1

# Every gate, ignoring every stamp -- what to run when you want the suite to
# have actually executed rather than to have decided it did not need to.
gates-force:
	$(MAKE) gates FORCE_GATES=1

# Everything the gates need built, built ONCE before the timed run below.
# The timed run is a sub-make per gate, and two sub-makes that share a binary --
# build/g2 is a prerequisite of three gates -- would otherwise race to compile
# it into the same output file. Building them first in a single make process
# makes that impossible. tests/gate_makefile_wiring.py holds this list to being
# a superset of every gate-*: prerequisite, so it cannot drift out from under
# the gates it protects.
GATE_PREREQS = build/directed_cone_anchor build/euler_unit build/g2 \
  build/g2_asan build/perimeter_defect build/perimeter_min build/prec_guess \
  build/sig_fold_unit build/strip_mu_cert build/strip_mu_fast \
  build/strip_mu_kink build/subgraph_count build/symcount_fast build/symtm \
  build/tma build/tma_asan build/tma_holes build/tma_modp_test \
  build/ns/orchestrate build/ns/map_worker build/ns/merge_worker \
  $(if $(GMP_LDFLAGS),build/convex_perim_tm build/middle_kingdom_tm)

# --- input gating -----------------------------------------------------------
# A gate that re-runs when nothing it reads has changed is pure waiting. A gate
# that does NOT run when something it reads HAS changed is a silent hole, and
# this repo has been bitten by that twice (the sym/symcount.py deletion, the
# four unwired Severance gates). So the default is: every gate runs, every time.
# A gate is skipped only if it is DECLARED here with the full set of things it
# reads, and its stamp is newer than all of them.
#
# Undeclared is the safe state, so forgetting to declare a gate costs time, not
# coverage. Declaring one wrong is caught two ways: tests/gate_makefile_wiring.py
# requires a declared gate's own script to be among its deps, and a dep that has
# gone missing makes the gate run rather than skip.
#
# `make gates-force` ignores every stamp. So does the hook on a new ref.
STAMPS = build/stamps

GO_SRC    = $(wildcard orchestrator/*.go orchestrator/*/*.go \
              orchestrator/*/*/*.go verify/*.go verify/*/*.go \
              verify/*/*/*.go go.mod go.sum)
PAPER_SRC = $(wildcard paper/*.tex paper/*.py paper/*.bib)
DOCS_SRC  = $(wildcard docs/*.md docs/*/*.md docs/*/*/*.md)

# `go test ./orchestrator/... ./verify/...` reads Go packages and nothing else
# in this tree -- it has no Makefile prerequisites and builds nothing. 16 s on
# gympie, serially, on every push including documentation-only ones.
DEPS_ns-gate-go             = $(GO_SRC)
DEPS_gate-p-paper-verifier  = $(PAPER_SRC) tests/gate_p_paper_verifier.py \
                              tests/_audit_subprocess_cache.py
DEPS_gate-l-paper-verifier  = $(PAPER_SRC) tests/gate_l_paper_verifier.py
DEPS_gate-docs-index        = $(DOCS_SRC) tests/gate_docs_index.py
DEPS_gate-no-copyright-pdfs = $(PAPER_SRC) tests/gate_no_copyright_pdfs.py

# The two 20 s gates. Their inputs are exact and small: the binaries they run
# (rebuilt by the GATE_PREREQS pass before this sweep, so a cpp/ or core/ change
# reaches them as a newer binary), the scripts they import, and the fixtures
# they read by name. tests/gate_makefile_wiring.py checks the import side of
# that mechanically -- every repo-local module these scripts import,
# transitively, has to be listed.
DEPS_gate-tma = build/tma build/tma_asan build/tma_holes build/g2 \
                tests/gate_tma.py tests/common.py \
                $(FIXTURES) results/holes_n14.txt
# Every declared gate that reads ANY fixture takes the whole directory. The
# module side of a dependency list is computed (check_gate_imports); the data
# side is hand-written, and naming individual b-files is where it goes wrong --
# a gate that gains a fixture would skip while that fixture changed. Over-broad
# is the safe direction, and fixtures/ changes rarely.
# TODO(2026-08-24): the computed version -- grep each declared script and its
# imports for fixtures/ and results/ literals, require them in DEPS -- is a
# third lint of moderate fragility. Same family as the GATE_TARGETS-completeness
# TODO above.
FIXTURES  = $(wildcard fixtures/*)

# Gates whose recipe just runs a binary: the binary IS the input. Make rebuilds
# it from its own sources before the sweep (GATE_PREREQS / NS_FAST_PREREQS), so
# a change under core/, cpp/ or worker/ reaches these as a newer binary.
DEPS_ns-gate-closedform        = $(GO_SRC)
DEPS_ns-gate-math              = build/ns/gate_math
DEPS_ns-gate-run               = build/ns/gate_run
DEPS_ns-gate-runfile           = build/ns/gate_runfile
DEPS_ns-gate-kink              = build/ns/gate_kink
DEPS_ns-gate-kink-column       = build/ns/gate_kink_column
DEPS_ns-gate-kink-stage-file   = build/ns/gate_kink_stage_file
DEPS_ns-gate-kink-worker-cli   = build/ns/gate_kink_worker_cli build/ns/map_worker
DEPS_ns-gate-persistent-worker = build/ns/gate_persistent_worker \
                build/ns/map_worker build/ns/merge_worker
DEPS_gate-strip-cert           = build/strip_mu_cert

DEPS_gate-strip-fast = build/strip_mu_fast build/strip_mu_kink \
                tests/gate_strip_fast.py tests/common.py $(FIXTURES)
DEPS_gate-king-grid = build/directed_cone_anchor tests/gate_king_grid.py \
                tests/common.py $(FIXTURES)
DEPS_gate-multidirected = build/directed_cone_anchor tests/gate_multidirected.py \
                tests/common.py experiments/multidirected_king.py $(FIXTURES)
DEPS_gate-g1 = tests/gate_g1.py tests/common.py oracle/g1_naive.py $(FIXTURES)

DEPS_gate-s2  = tests/gate_s2.py tests/common.py oracle/g1_naive.py $(FIXTURES)
DEPS_gate-sym = build/symcount_fast tests/gate_sym.py tests/common.py \
                oracle/g1_naive.py sym/symcount.py $(FIXTURES)
DEPS_gate-subgroup = build/symcount_fast build/symtm tests/gate_subgroup.py \
                tests/common.py oracle/g1_naive.py sym/symcount.py $(FIXTURES)
DEPS_gate-symtm = build/symtm build/symcount_fast tests/gate_symtm.py \
                tests/common.py
DEPS_gate-motley-crt = scripts/motley_crt.py \
                $(wildcard results/cutcount_b1/residues/*) \
                results/cutcount_b1/rows/C18.out \
                $(wildcard results/cutcount_b1/residues41/*) \
                results/cutcount_b1/rows41/C19.out
DEPS_gate-modp = build/tma build/tma_modp_test tests/gate_modp.py tests/common.py
DEPS_gate-perimeter-min = build/perimeter_min build/g2 \
                scripts/perimeter_min_gate.sh experiments/diamond_free_removals.py \
                results/siteperim_square8_n14.txt results/siteperim_square4_n20.txt \
                results/siteperim_tri6_n12.txt
DEPS_gate-severance-w1 = build/severance_w1 experiments/severance_w1_gate.py \
                experiments/cluster_weight_dp.py
DEPS_gate-severance-w2 = experiments/severance_w2_gate.py \
                experiments/severance_w2_kernel.py experiments/depth1_recurrence.py \
                experiments/depth1_gap_walk.py experiments/cluster_weight_dp.py \
                experiments/slope2_law_vs_truth.py
DEPS_gate-g2  = build/g2 build/g2_asan \
                tests/gate_g2.py tests/common.py oracle/g1_naive.py $(FIXTURES)
DEPS_gate-kink-oracle = build/ns/orchestrate build/ns/map_worker \
                build/ns/merge_worker tests/gate_kink_oracle.py tests/common.py \
                $(FIXTURES)

# Per-gate wall time, on every run, from the machine that actually ran it.
# -j interleaves output, so a gate that has quietly grown to minutes is
# invisible in the log unless it says so itself -- which is how gate-perimeter-min
# reached 417 s under a comment claiming "~2 s". The wrapper is one sub-make per
# gate: milliseconds against gates measured in seconds. `make gates | grep
# gate-time | sort -rn -k2` is the ranking.
# The stamp holds the sorted dependency LIST, not just a timestamp. Comparing
# mtimes alone would miss a file being deleted or added: the survivors are all
# older than the stamp, so the gate would skip a tree that no longer builds the
# same way. Three ways to run rather than skip -- the list differs, a listed
# file has gone missing, or one is newer -- and all three are the safe direction.
timed-%:
	@deps='$(DEPS_$*)'; stamp=$(STAMPS)/$*; skip=; \
	 list=$$(printf '%s\n' $$deps | sort); \
	 if [ -n "$$deps" ] && [ -z "$(FORCE_GATES)" ] && [ -f "$$stamp" ] && \
	    [ "$$list" = "$$(cat "$$stamp")" ]; then \
	   skip=1; \
	   for f in $$deps; do \
	     if [ ! -e "$$f" ] || [ "$$f" -nt "$$stamp" ]; then skip=; break; fi; \
	   done; \
	 fi; \
	 if [ -n "$$skip" ]; then \
	   echo "gate-time 0s $* (skipped: declared inputs unchanged)"; \
	   exit 0; \
	 fi; \
	 t0=$$(date +%s); \
	 $(MAKE) --no-print-directory $* ; st=$$?; \
	 if [ $$st -eq 0 ] && [ -n "$$deps" ]; then \
	   mkdir -p $(STAMPS); printf '%s\n' "$$list" > "$$stamp"; \
	 fi; \
	 echo "gate-time $$(( $$(date +%s) - t0 ))s $*"; \
	 exit $$st

gates:
	@mkdir -p $(dir $(GATELOG))
	@$(MAKE) --no-print-directory -j$(JOBS) $(GATE_PREREQS)
	@set -o pipefail; \
	 $(MAKE) --no-print-directory -j$(JOBS) $(addprefix timed-,$(GATE_TARGETS)) 2>&1 | tee $(GATELOG); \
	 st=$$?; \
	 if [ $$st -ne 0 ]; then \
	   echo; \
	   echo "=== RED gate(s):"; \
	   named=$$(sed -n 's/^.*\*\*\* \[.*\(gate-[a-z0-9-]*\)\] Error.*/    \1/p' $(GATELOG) | sort -u); \
	   if [ -n "$$named" ]; then echo "$$named"; \
	   else echo "    (none named -- the failure was in a prerequisite; see the log)"; fi; \
	   echo "=== slowest gates:"; \
	   grep '^gate-time ' $(GATELOG) | sort -rn -k2 | head -8 | sed 's/^/    /'; \
	   echo "=== full log: $(GATELOG)"; \
	   echo "=== serial re-run, output no longer interleaved: make gates JOBS=1"; \
	 fi; \
	 exit $$st

# Gate BFILES: every uploaded OEIS b-file term, re-derived from banked data --
# a(n) from the triangle's row sums, the whole symmetry family by Burnside from
# results/sym_counts.txt, non-polyominoes against fixtures/b000105.txt -- plus
# format hygiene (contiguous n, nonnegative values, no duplicates). A wrong
# digit in a b-file is the most embarrassing failure available here and nothing
# re-derived these artifacts before. Three RED controls, each of which must
# fire, including a term dropped from the MIDDLE (a trailing drop is reported
# as staleness, not failure). ~1 s.
gate-bfiles:
	python3 scripts/bfile_gate.py --selftest
	python3 scripts/bfile_gate.py

# Gate PROVENANCE: results/provenance-table.md is generated, and every headline
# share it carries is recomputed here from the banked triangle and compared with
# the note that publishes it. Five notes used to state these figures separately
# and one pair had already drifted (strip cell coverage vs holdout mass). Also
# pins the count of cells carrying ONLY the mod-4 congruence: if that grows,
# something regressed; when Motley reaches H=18 it must shrink, which fires the
# gate and forces the number to be updated deliberately rather than silently.
# Motley's reach is derived from the banked C rows and VERIFIED against the
# triangle (a row that does not assemble caps it, RED control included), and
# the tower-from-Motley source (tag U, experiments/undertow_ri.py run per row)
# is a fourth tier, pinned at 192 cells, so "one tower strategy pinned from
# Motley's data" (AUDIT-2026-09-02 M2/M3) is carried by a check, not prose.
# Three RED controls (--selftest). ~0.5 s, no build needed.
gate-provenance:
	python3 scripts/provenance_table.py --selftest
	python3 scripts/provenance_table.py --check

# Gate RESIDUAL-CELLS: results/residual-cells.md is the one place the "cells
# that still have one source" figures live, and every restatement of them
# anywhere in the tree is checked against it -- count AND cell list, which is
# what gate-provenance did not do.  Written 2026-08-19 after a sweep found four
# accounts of those figures in four notes, three of them right: TWO quantities
# were sharing one name (Q1 congruence-only over all 820 cells; Q2 row 40's
# rule-independence band), and nothing defined either.  A residual claim with no
# `<!--q:fact=value-->` marker fails; so does a marker that disagrees; so does a
# scan that matches nothing at all.  15 RED controls (--selftest), one of them
# for the fail-OPEN that let "**only** the mod-4" past the pattern and one
# for the hatch accepting a wrong cell LIST.  A fourth trigger shape, "N of 40
# cells", added 2026-09-05 after results/confidence.md carried "35 of 40 cells
# ... Now: 40 of 40" past the gate for sixteen days (AUDIT-2026-09-02 M2).
# 17 RED controls.  ~0.3 s.
gate-residual-cells:
	python3 scripts/residual_cells.py --selftest
	python3 scripts/residual_cells.py --check

# Gate CUTCOUNT-ASSEMBLY: Motley's banked rows still make the triangle, and the
# held-out prime still predicts.  T(n,H) = C_H - 2 C_{H-1} + C_{H-2} over
# results/cutcount_b1/rows/, 567 cells H=1..18 against results/triangle.txt;
# then C_18 reconstructed by CRT from four of Confetti's five primes, the fifth
# predicted (40/40) and the reconstruction tied back to the banked exact row.
# Written 2026-08-19: the assembly existed only inside a dalby runner `make`
# never touches, so a corrupted row would have sat in results/ unnoticed, and
# the 40/40 was the runner's word until the residue rows were banked the same
# day.  Coverage is pinned as well as agreement -- a dropped row or prime fails
# rather than shrinking the check.  Three more arms since 2026-09-05
# (AUDIT-2026-09-02 M3): the Nmax-41 ladder's rows41/ assembled against the
# triangle (589 cells) and against the kink engine's own Nmax-41 sweep at
# n = 41 (19 cells -- the two-engine agreement on a(41)'s swept half), and its
# held-out verdict re-derived at every one of the 19 heights from the 171
# residue rows banked in residues41/ (779 cells).  16 RED controls.  ~1.5 s.
gate-cutcount-assembly:
	python3 scripts/cutcount_assembly_gate.py --selftest
	python3 scripts/cutcount_assembly_gate.py

# Undertow's 3-power congruence gate (results/undertow-review-A.md B17).  Every
# below-onset tower cell is an integer, its main term carries 3^-(k+j) and
# D_j(k)'s denominator divides 3^(k+j) -- verified, not assumed -- so
# integrality forces a congruence on each defect mod 3^(k+j).  71 banked cells
# are checked for full equality; the two defects with no banked cell at all,
# D_1(21) and D_2(21), get their congruence.  It fails closed if that free set
# empties.  Four RED controls, including one that catches the single-source
# D_4(21) transitively through the pin it feeds -- for a FRACTIONAL error only.
# An integer shift of a defect passes (its RED 3, by design), and every error a
# real family-table entry can carry is an integer shift: gate-undertow-pairs
# below is what catches those.
#
gate-undertow-congruence:
	python3 experiments/undertow_congruence_gate.py --selftest
	python3 experiments/undertow_congruence_gate.py

# Gate UNDERTOW-PAIRS (AUDIT-2026-09-02 M1).  Level 21 of the a(41) tower had
# one below-onset pin pair at depths j <= 4 and so no check at its own level;
# +9 on sig[3][21] of results/severance_w3_families_K22_e3.txt leaves the
# congruence gate green and moves the depth-4 a(41) by exactly 9 (measured).
# At depth 5 -- results/severance_w3_families_K21_e4.txt, banked 2026-08-23 and
# never wired into the assembler -- level 21 has THREE pin pairs through
# T(38,17), T(39,18), T(40,19), and any single-entry error in that row makes
# them disagree.  The gate builds the depth-5 tower with the pin cells and pair
# counts pinned, requires a(41) from results/a41/h*.out plus the tower to equal
# the banked value, and runs five RED controls, the first being that mutation
# end to end.  Pure Python over tracked files, ~1 s.
gate-undertow-pairs:
	python3 experiments/undertow_pairs_gate.py --selftest
	python3 experiments/undertow_pairs_gate.py

# Gate KINK-ORACLE (AUDIT-2026-09-02, a(23)..a(35)).  The kink-carry kernel
# produced a(30)..a(41)'s swept half, and its only in-make oracle coverage was
# the maxn-14 sweeps where the wired diagonals inject every H >= 8 -- so the
# kernel itself was checked at H <= 7.  --max-diag-k 0 disables the injection
# (orchestrator/maxdiagk_test.go).  Two all-real sweeps: kink at maxn 18, row
# sums against the externally published a(1..18) of fixtures/b006770.txt (the
# whole known sequence, every height enumerated); and kink vs column at maxn
# 16, per-height rows byte-identical.  Both comparisons are done by the script
# from h<H>.out, not read off the orchestrator's --compare line.  Measured on
# gympie 2026-09-05: kink 18 = 68 s at 8 cores / 90 MB, column 16 = 101 s at
# 4 cores / 300 MB, kink 16 = 0.7 s; the recipe runs at 4 cores.  Declared, so
# it is skipped while the binaries and inputs are unchanged.  4 RED controls.
gate-kink-oracle: build/ns/orchestrate build/ns/map_worker build/ns/merge_worker
	python3 tests/gate_kink_oracle.py --selftest
	python3 tests/gate_kink_oracle.py

# The Severance gate family (W1, W2, W3, and W3 at depth 5).  These four were
# outside GATE_TARGETS until 2026-08-24 -- successor row S-A5 in
# results/undertow-review-queue.md, which asked for the decision to be made for
# the family rather than per-file.  It is made here: all four are wired.
#
# The one that had a real reason to stay out was the depth-5 gate, written
# red-first and correctly exiting 1 until a severance_w3_families_K>=19_e4
# table existed.  That table landed 2026-08-23 and the gate is green
# (results/depth5-gate-green.md), so the reason is spent.  The other three had
# no reason beyond nobody having wired them, which is exactly the failure the
# GATE_TARGETS comment above warns about: a gate-foo: recipe that never reaches
# GATE_TARGETS is a check `make gates` does not run.
#
# Each recipe runs the RED control first and the production check second, so a
# gate that has quietly stopped being able to fail is caught before its green
# is believed.  Measured on gympie 2026-08-24, production run: W1 219 s,
# W2 69 s, W3 0.1 s, depth 5 0.1 s.  W1 is the only slow one and it is well
# inside the suite's parallel critical path, so wiring these does not move the
# `make gates` wall.  They are separate targets rather than one gate-severance
# so that -j schedules them independently and a RED one gets NAMED by the
# recipe at the end of `gates`.
gate-severance-w1:
	python3 experiments/severance_w1_gate.py --selftest
	python3 experiments/severance_w1_gate.py $(GATE_DEEP)

gate-severance-w2:
	python3 experiments/severance_w2_gate.py --selftest
	python3 experiments/severance_w2_gate.py $(GATE_DEEP)

gate-severance-w3:
	python3 experiments/severance_w3_gate.py --selftest
	python3 experiments/severance_w3_gate.py

gate-severance-depth5:
	python3 experiments/severance_w3_depth5_gate.py --selftest
	python3 experiments/severance_w3_depth5_gate.py

# Gate MODP: the R3 u32 mod-p sweep.  CRT of sum_H B_H(n) mod p_i over three
# primes must equal the exact a(n) from build/tma, both unfolded and under
# --fold (the R1xR3 composition).  Written 2026-08 and referenced by
# docs/engine-design.md and results/r4/r4-a.md, but never wired -- it was found
# by gate-makefile-wiring below, green and unrun since August.  ~31 s.
gate-modp: build/tma build/tma_modp_test
	python3 tests/gate_modp.py $(GATE_DEEP)

# The mod-p test engine. It used to be compiled INSIDE tests/gate_modp.py, with
# a subprocess c++ call on every single run -- so every push paid an -O3 build
# of it whether or not anything it depends on had changed. As a make target it
# is built once and then skipped, and its rebuild is triggered by the right
# thing (its own source and the headers it includes).
build/tma_modp_test: cpp/tma_modp_test.cpp cpp/tma/*.h | build
	$(CXX) $(CXXFLAGS) -O3 -pthread $< -o $@

# Gate MOTLEY-CRT: scripts/motley_crt.py was extracted out of a runner heredoc
# precisely because a heredoc is code `make` never touches -- and then its own
# --selftest sat in exactly the same position, run by nothing. It reconstructs
# C_18 from the banked residues, requires it to equal the banked row exactly,
# and holds out a prime as a RED control. Every input is tracked and it is
# 0.03 s (dalby, 2026-08-24), so there is no reason for it to be by-hand.
gate-motley-crt:
	python3 scripts/motley_crt.py --selftest

# Gate MAKEFILE-WIRING: the lint the GATE_TARGETS comment above asks for.
# It checks TWO surfaces.  Recipe-vs-GATE_TARGETS is the obvious one.  The
# other -- script-vs-Makefile -- is the one that actually bit us: the four
# Severance gates above had no recipe AT ALL, so a recipe-level check sees a
# consistent Makefile and passes.  Verified against the pre-fix tree: the
# recipe surface alone reports nothing on it.  The script surface reports all
# four, and turned up gate-modp as a fifth.
#
# Both surfaces have an allowlist carrying a written reason per entry, and both
# are red on a stale entry or on an excuse for something now wired, so an
# allowlist cannot rot into a permanent exclusion nobody revisits.  7 RED
# controls.  Instant.
gate-makefile-wiring:
	python3 tests/gate_makefile_wiring.py --selftest
	python3 tests/gate_makefile_wiring.py

# Gate PERIMETER-DEFECT: the pruned max-end search vs g2 --siteperim (A), vs
# its own unpruned control (B), marginal consistency (C), and --split shards
# summing elementwise to the unsplit run (D). D is what makes a sharded
# production run trustworthy -- a shard that drops or double-counts a subtree
# looks perfectly healthy in its own output. ~40 s.
gate-perimeter-defect: build/perimeter_defect build/g2
	./scripts/perimeter_defect_gate.sh

# Gate PERIMETER-MIN: build/perimeter_min enumerates the isoperimetric end of
# the perimeter table by COMPLEMENTATION, which is complete only under a
# hypothesis (every animal's perimeter is at least its filled bounding box's).
# Run with removals unbounded on small boxes it degenerates to a complete brute
# force, so it can be compared cell for cell against build/g2's --siteperim
# census -- a different search entirely. A hypothesis violation shows up as a
# missing animal. Includes a RED control.
#
# The "~2 s" this comment used to claim was the three census cross-checks, which
# really are ~1 s together. The gate measured 417 s (dalby, 2026-08-24): check
# E's W=13 second-source case, run twice. See the script.
gate-perimeter-min: build/perimeter_min build/g2
	./scripts/perimeter_min_gate.sh $(GATE_DEEP)

# Gate PERIMETER-MIN-SHARD: the sharded driver that makes a min-end census
# resumable must be a drop-in for the monolithic run, or a resumed census is a
# different number wearing the same filename. Checks the merged per-frame result
# byte-for-byte against the monolithic one on both lattices, then damages frame
# files the way a kill does (no trailer, empty, missing, wrong geometry) and
# requires each to be redone or refused. The RED control removes the transpose
# multiplicity -- `--only` forces mult=1, so without reapplying it every W<H
# frame is halved and the equivalence check must go red. ~25 s.
gate-perimeter-min-shard: build/perimeter_min
	./scripts/perimeter_min_shard_gate.sh

# Gate COMPILE-DB: clangd's compile_commands.json must be complete and honest.
# A missing or wrong entry is invisible to every other gate (they use the
# Makefile's own flags) but makes the editor report phantom errors in correct
# code -- the failure this gate was written after was cpp/*.cpp missing from
# the DB entirely, so clangd could not find <gmpxx.h> or "obs.h" and cascaded
# fake "unknown type name 'mpz_class'" through every use. Regenerates first,
# so it also catches a .cpp added without rerunning `make compile-commands`.
# Syntax-only: ~11 s.
gate-compile-db: compile-commands
	./scripts/check_compile_commands.sh

# Gate CITATIONS: every repo path cited in a tracked markdown file must exist.
# Written after results/beyond-polyplets.md was found citing a file that has
# never existed -- the name belonged to a memory entry, not to the repo. Paths
# that are templates, marked deleted/planned in the citing line, or present in
# git history are allowed; a name that never existed is not. Sub-second, no
# build deps, so it runs first.
gate-citations:
	python3 tests/gate_citations.py

# Gate NO-COPYRIGHT-PDFS: no PDF is tracked at all.  .gitignore's first rule is
# "copyrighted papers stay local, never pushed" and until 2026-08-19 nothing
# enforced it -- the only check was a printed line in scripts/clean_clone_check.sh,
# a runner make never touches, which set no exit code.  Sub-second, git only.
gate-no-copyright-pdfs:
	python3 tests/gate_no_copyright_pdfs.py

# Gate DOCS-INDEX: docs/README.md names every file under docs/, by path or by
# directory.  The citations gate closes the other direction (an index entry
# pointing at a file that is gone), so between them the map cannot rot.
gate-docs-index:
	python3 tests/gate_docs_index.py

# Gate RECEIPTS: in the rook-parity campaign's deliverables and briefs, a status
# token that says something executed (PROVED/VERIFIED/GREEN/RUN/CONFIRMED/
# PASSED/MATCHED, in a table cell or on a `status:` line) must carry an in-tree,
# non-empty path on the same line.
#
# Written because the round-4 status drift had a sign: every discrepancy
# upgraded a written-but-unrun instrument to a completed one, none went the
# other way (results/r4/INSTRUMENTS.md:4-8). The rule that ended it was
# disciplinary; every disciplinary control in that campaign was waived at least
# once, usually by the lead, so this is the mechanical form. In-tree is
# load-bearing: the campaign's largest result sat only on dalby for two days.
#
# It proves a receipt EXISTS, not that the receipt says what the claim says --
# that is the numbers adversary's job, and the gate exists so the adversary
# spends its pass reading logs instead of hunting for their absence. Red-first:
# --self-test runs before every scan and requires three planted claims (no
# receipt, absent file, remote path) to be rejected. Sub-second, no build deps.
gate-receipts:
	./scripts/check_receipts.sh

# Gate L-PAPER-VERIFIER: mutation-tests paper/verify_l_papers.py, which is the
# only thing standing between the L manuscripts and a wrong printed number.
#
# It exists because that verifier asserted "the paper prints X" with
# `str(X) in src` -- substring containment -- at three sites, and on 2026-08-07
# six of twelve deliberate manuscript corruptions went undetected, wrong-digit
# typos among them. It carried thirteen RED controls and not one of them was on
# a text assertion, so nothing ever established that those checks could fail.
#
# A verifier is trusted silently by everything downstream of it, so it is held
# to a higher standard than the papers it protects, not a lower one. This gate
# corrupts each manuscript twelve ways on a temp copy and requires the verifier
# to go red every time. Sub-second, no build deps.
gate-l-paper-verifier:
	python3 tests/gate_l_paper_verifier.py

# Gate P-PAPER-VERIFIER: the RED control the human-authored paper's verifier
# never had.  verify_technical_report.py reports 781 green checks; this
# perturbs every numeric literal in technical-report.tex, in a copy, and
# requires the verifier to go red for each -- 199 of 200, the exception being
# the year on the title page.  Its --selftest runs the same sweep against a
# stub verifier that always exits 0 and requires every literal to come back
# unguarded, so a harness that cannot see a verifier checking nothing fails
# before it can pass anything.  ~30 s.
gate-p-paper-verifier:
	python3 tests/gate_p_paper_verifier.py --selftest
	python3 tests/gate_p_paper_verifier.py

# Gate G1: naive Python oracle vs pinned OEIS fixtures (quick tier, ~3 s)
gate-g1:
	python3 tests/gate_g1.py

# Gate DRIVER: reach driver/combine reject crashed/raced/corrupt sweeps (no silent zeros)
gate-driver: build/tma
	python3 tests/gate_driver_robust.py

# Gate G2: C++ Redelmeier engine vs oracle + fixtures (+ split, + sanitizers)
gate-g2: build/g2 build/g2_asan
	python3 tests/gate_g2.py $(GATE_DEEP)

build:
	mkdir -p build

# -Wno-error=restrict on the Redelmeier generator: works around a gcc-12 false
# positive in <bits/char_traits.h> (bogus -Wrestrict on std::string ops; clang and
# gcc-15 don't trip it). Scoped here so -Werror stays strict everywhere else.
build/g2: cpp/g2_redelmeier.cpp | build
	$(G2CXX) $(CXXFLAGS) $(G2_RESTRICT) -O3 $< -o $@

# Defect-pruned Redelmeier for the site-perimeter grading. Separate binary
# because the prune changes the search, not the bookkeeping, and it needs
# NMAX far past g2's 40 (docs/perimeter-defect-plan.md, Task B).
build/perimeter_defect: cpp/perimeter_defect.cpp cpp/obs.h | build
	$(G2CXX) $(CXXFLAGS) $(G2_RESTRICT) -O3 $< -o $@

# Minimum-perimeter (isoperimetric-end) enumerator. Complementation, not
# growth: the min-side defect is not monotone under cell addition, so
# Exhaustive minimal-site-perimeter census for king animals: eps(n), |M_n|,
# and the (|B|, c=|P|-|B|) split, n<=25. Written 2026-08-13 for the
# Barequet--Ben-Shachar constant-isomer premise check; the measured failure
# of their Premise 2 (c=9 at inflation-chain roots, 8 elsewhere) and the
# 9/9 |M_n|=|M_{n+eps}| match live in the reading-pass record.
build/kingperim: cpp/kingperim.cpp | build
	$(CXX) $(CXXFLAGS) -O3 $< -o $@

# Companion: does inflation Q -> Q + 3x3 ball preserve perimeter-minimality
# and injectivity on M_n (n<=16)? Cross-checks eps(n) against A235382.
build/kinginflate: cpp/kinginflate.cpp | build
	$(CXX) $(CXXFLAGS) -O3 $< -o $@

# perimeter_defect's prune has no analogue here (cpp/perimeter_min.cpp).
build/perimeter_min: cpp/perimeter_min.cpp cpp/obs.h | build
	$(G2CXX) $(CXXFLAGS) $(G2_RESTRICT) -O3 $< -o $@

# Independent strip transfer-matrix engine (the second source for T(n,H),
# H<=14). -std=c++17 and no $(CXXFLAGS) deliberately: mirrors the build line
# in scripts/run_strip_h14.sh exactly, so the gate binary and the production
# run binary are the same program built the same way.
# results/strip-engine.md's "Reproduce" section documented this target before
# it existed (AUDIT-2026-07-30 S7).
build/strip_tm: cpp/strip_tm.cpp | build
	$(CXX) -O3 -std=c++17 $< -o $@

# Strip growth-constant engines (mu_H, the rigorous lambda lower-bound ladder).
# strip_mu_cert is the CERTIFICATE tool: float power iteration to locate x*, then
# an exact unsigned-__int128 Collatz-Wielandt check that promotes mu_H to a
# machine-checkable rational. Since 2026-07-31 both phases drive the frozen
# stage operators of cpp/strip_stage_ops.h (~240x at H=11/12), so that header is
# a dependency here as well as under build/strip_mu_fast. -I. for core/ and
# cpp/obs.h rides the quoted include.
build/strip_mu: cpp/strip_mu.cpp | build
	$(CXX) $(CXXFLAGS) -O3 $< -o $@

# motley_par: the PARALLEL Motley engine (results/motley-par/README.md).  Same
# frozen rule core as results/cutcount_b1/cutcount_b1.cpp.59e90660; the
# parallelism, the flat arena and the chunked release are accounting.  -fopenmp
# is not optional -- the cell-step is an OpenMP loop -- and scripts/
# gen_compile_commands.sh mirrors that so clangd and gate-compile-db agree.
build/motley_par: cpp/motley_par.cpp cpp/obs.h | build
	$(CXX) $(CXXFLAGS) -O2 -fopenmp -o $@ $<

# Gate the parallel engine against the BANKED exact C_H rows at three payload
# widths, byte-identically against cutcount_b1, and for thread-count
# determinism.
#
# Wired NOWHERE, and this comment used to claim it "lives with the ns-gates",
# which was not true -- ns-gates has never listed it. The real reason is
# -fopenmp: build/motley_par does not compile on gympie (Apple clang, no
# libomp by default) or on dalby (no omp.h), so putting it in any automatic
# chain would make that chain fail on two of the three boxes. It runs on ayr,
# by hand: `make gate-motley-par`. Verified green there 2026-08-24 -- 1200
# cell-comparisons over H=1..10, both RED controls firing.
gate-motley-par: build/motley_par
	python3 tests/gate_motley_par.py --selftest
	python3 tests/gate_motley_par.py 10

build/strip_mu_kink: cpp/strip_mu_kink.cpp core/signature.h core/transition.h | build
	$(CXX) $(CXXFLAGS) -O3 -I. $< -o $@

build/strip_mu_cert: cpp/strip_mu_cert.cpp cpp/strip_stage_ops.h cpp/obs.h \
                     core/signature.h core/transition.h | build
	$(CXX) $(CXXFLAGS) -O3 -I. $< -o $@

# strip_mu_fast is the INDEXED-ARRAY engine: the same cell-at-a-time kink sweep,
# with the per-stage state graph enumerated once and frozen into int32 successor
# arrays (cpp/strip_stage_ops.h), so a matvec is a flat scatter instead of a
# hash-map rebuild. ~200x strip_mu_kink at H=11 (results/strip-mu-fast.md). The
# map engine stays in the tree as the cross-check that gate-strip-fast runs.
build/strip_mu_fast: cpp/strip_mu_fast.cpp cpp/strip_stage_ops.h cpp/obs.h \
                     core/signature.h core/transition.h | build
	$(CXX) $(CXXFLAGS) -O3 -I. $< -o $@

# Gate strip-fast: the fast engine against BOTH the map engine (same mu_H, same
# state counts, H<=8) and the published certificates (the exact kernel must PASS
# the certified numerator and FAIL numerator+1). RED arms are in --selftest: a
# corrupted transition table and a corrupted finalize map must both move mu_6,
# and an over-claim or an all-zero vector must be refused. ~10 s.
gate-strip-fast: build/strip_mu_fast build/strip_mu_kink
	python3 tests/gate_strip_fast.py

# Gate strip-cert: RED-first self-test for the certificate checker. mu_2 =
# 1+sqrt(2), so 24142/10000 must PASS and 24143/10000 must FAIL; a deliberately
# corrupted vector must be rejected with the offending state named. Sub-second.
gate-strip-cert: build/strip_mu_cert
	./build/strip_mu_cert --selftest

# fixed-height transfer matrix over Z/pZ, for generating-function recovery
build/gf_modp: cpp/gf_modp.cpp | build
	$(CXX) $(CXXFLAGS) -O3 $< -o $@

# fixed-height KNIGHT-animal transfer matrix over Z/pZ (horizontal-reach test)
build/g2_asan: cpp/g2_redelmeier.cpp | build
	$(CXX) $(CXXFLAGS) $(RESTRICT_FLAG) -g -O1 -fsanitize=address,undefined \
	    -fno-omit-frame-pointer $< -o $@

# Gate Euler: hole-accounting helper (#28) vs flood oracle, before engine wiring
gate-euler: build/euler_unit
	./build/euler_unit

build/euler_unit: tests/euler_unit.cpp cpp/tma/euler.h | build
	$(CXX) $(CXXFLAGS) -O2 $< -o $@

# Gate SIG-FOLD: the R1 vertical-mirror fold, settled at the SIGNATURE level
# instead of by enumeration.  reflectSig/foldSig are ~40 lines; that reflection
# is a symmetry of the column step is a property of those lines and of
# stepColumnSquare8, and tests/sig_fold_unit.cpp checks it exhaustively over
# every canonical signature at H<=6 (not merely the reachable ones) in well
# under a second, with three mutant folds as RED controls.
#
# It replaces the expensive half of gate-tma check M, which proved the same
# statement by enumerating square8 to n=14 twice -- 391 s of that gate's 429 s
# by its own measurement.  It also restores a check that had gone missing:
# signature.h cites experiments/r1_sym_fold_check.py as the fold's validation
# and that file was deleted in 91bdcdc.
gate-sig-fold: build/sig_fold_unit
	./build/sig_fold_unit --selftest
	./build/sig_fold_unit $(GATE_DEEP)

build/sig_fold_unit: tests/sig_fold_unit.cpp cpp/tma/signature.h cpp/tma/transition_square8.h | build
	$(CXX) $(CXXFLAGS) -O2 $< -o $@

# Gate TMA: transfer-matrix engine vs fixtures + G2 height marginals
gate-tma: build/tma build/tma_asan build/tma_holes build/g2
	python3 tests/gate_tma.py $(GATE_DEEP)


build/tma: cpp/tma_main.cpp cpp/tma/*.h | build
	$(CXX) $(CXXFLAGS) -O3 -pthread cpp/tma_main.cpp -o $@

# Holes + mod-p engine: SAME source as build/tma (the --holes / --modp paths live
# in tma_main.cpp). Kept as a separate named binary because the exact hole-count
# runs invoke build/tma_holes by name.
build/tma_holes: cpp/tma_main.cpp cpp/tma/*.h | build
	$(CXX) $(CXXFLAGS) -O3 -pthread cpp/tma_main.cpp -o $@

build/tma_asan: cpp/tma_main.cpp cpp/tma/*.h | build
	$(CXX) $(CXXFLAGS) -g -O1 -fsanitize=address,undefined \
	    -fno-omit-frame-pointer -pthread cpp/tma_main.cpp -o $@

build/tma_tsan: cpp/tma_main.cpp cpp/tma/*.h | build
	$(CXX) $(CXXFLAGS) -g -O1 -fsanitize=thread \
	    -fno-omit-frame-pointer -pthread cpp/tma_main.cpp -o $@

# Uniform random polyplet sampler / specimen emitter (transfer-matrix completion DP)
build/tma_sample: cpp/tma_sample.cpp cpp/tma/*.h | build
	$(CXX) $(CXXFLAGS) -O3 -pthread cpp/tma_sample.cpp -o $@

build/symcount_fast: cpp/sym/symcount_fast.cpp | build
	$(CXX) $(CXXFLAGS) -O3 $< -o $@

# Symmetric transfer-matrix counter (Hall of Mirrors): symmetric counts to n~34
build/symtm: cpp/sym/symtm.cpp core/signature.h core/transition.h | build
	$(CXX) $(CXXFLAGS) -O3 -pthread -I. cpp/sym/symtm.cpp -o $@

# Gate symtm: TM symmetric counter vs symcount_fast (cross-algorithm, live)
gate-symtm: build/symtm build/symcount_fast
	python3 tests/gate_symtm.py $(GATE_DEEP)

# Gate sym: symmetric-polyplet counters (4 types) + free count vs A030222
gate-sym: build/symcount_fast
	python3 tests/gate_sym.py $(GATE_DEEP)

# Gate subgroup: per-SUBGROUP invariant counts + the a(n) mod 4 congruence
gate-subgroup: build/symcount_fast build/symtm
	python3 tests/gate_subgroup.py $(GATE_DEEP)

# Gate E0: weighted connected-subgraph counter vs brute force
gate-e0: build/subgraph_count
	python3 tests/gate_e0.py

build/subgraph_count: cpp/sym/subgraph_count.cpp | build
	$(CXX) $(CXXFLAGS) -O3 $< -o $@

# Cone anchor: directed king animals by enumerate+filter vs Bacher's closed form
# (results/directed-cone-anchor.md). Also the docs/middle-kingdom-plan.md Phase 0
# 16-cell grid mode ("grid"/"gridbad") and Phase 1c's multi-directed filter
# ("mdir"/"mdirbad", results/multi-directed.md). -Icpp for obs.h.
build/directed_cone_anchor: cpp/directed_cone_anchor.cpp cpp/argparse.h cpp/obs.h | build
	$(CXX) $(CXXFLAGS) -O3 -pthread -Icpp $< -o $@

# Gate KING-GRID: docs/middle-kingdom-plan.md Phase 0 -- the 16-cell grid mode
# vs the plan's reference table + RED controls (existing + gridbad staircase).
gate-king-grid: build/directed_cone_anchor
	python3 tests/gate_king_grid.py $(GATE_DEEP)

# Gate SITE-PERIM: docs/middle-kingdom-followups-plan.md Phase 4a -- the
# grid-mode min-reduce of site perimeter (KING adjacency, minSPKing) vs the
# 4k+4 perfect-square hand check and an independent oracle (build/g2's
# square8 lattice, same population/convention, different code), plus the
# rook-adjacency RED control (minSPRook) which must diverge.
gate-site-perim: build/directed_cone_anchor build/g2
	python3 tests/gate_site_perim.py

# Gate MULTIDIRECTED: docs/middle-kingdom-plan.md Phase 1c -- Bacher's
# Definition 2 brute force ("mdir") vs the Theorem 8 generating function, plus
# the RED controls (keystone condition dropped; "control B") and the
# 6.4752-not-6.118 growth-constant trap. results/multi-directed.md.
gate-multidirected: build/directed_cone_anchor
	python3 tests/gate_multidirected.py $(GATE_DEEP)

# GMP (mpz_class/gmpxx): headers live in /usr/include on Linux, /opt/local on
# macOS/MacPorts. AUTO-DETECTED same as zstd above -- if the dev header is
# absent, convex_area_tm is skipped rather than failing the whole `make`.
ifeq ($(shell uname -s),Darwin)
  GMP_HDR := /opt/local/include/gmpxx.h
else
  GMP_HDR := /usr/include/gmpxx.h
endif
ifneq ($(wildcard $(GMP_HDR)),)
  GMP_CFLAGS := -DPOLY_GMP
  GMP_LDFLAGS := -lgmpxx -lgmp
  ifeq ($(shell uname -s),Darwin)
    # -isystem, not -I: gmpxx.h itself trips -Wdeprecated-literal-operator
    # under -Werror (old-style operator"" _mpz spacing) -- not our code to fix.
    GMP_CFLAGS  += -isystem /opt/local/include
    GMP_LDFLAGS := -L/opt/local/lib -lgmpxx -lgmp
  endif
else
  GMP_CFLAGS :=
  GMP_LDFLAGS :=
  $(info NOTE: gmpxx dev header not found ($(GMP_HDR)); convex_area_tm skipped)
endif

# HV-convex-by-area transfer matrix, C++/GMP port of experiments/convex_tm.py
# (docs/middle-kingdom-plan.md Phase 1a -- Python's N^4-DP-steps x N-digit-bigint
# cost is too slow past n~200; this is a straight translation onto mpz_class).
ifneq ($(GMP_LDFLAGS),)
build/convex_area_tm: cpp/convex_area_tm.cpp cpp/argparse.h cpp/obs.h | build
	$(CXX) $(CXXFLAGS) -O3 -Icpp $(GMP_CFLAGS) $< -o $@ $(GMP_LDFLAGS)

# HV-convex-by-semiperimeter exact-box transfer matrix, C++/GMP port of
# experiments/convex_perimeter.py (docs/middle-kingdom-plan.md Phase 1b).
build/convex_perim_tm: cpp/convex_perim_tm.cpp cpp/argparse.h cpp/obs.h | build
	$(CXX) $(CXXFLAGS) -O3 -Icpp $(GMP_CFLAGS) $< -o $@ $(GMP_LDFLAGS)

# Column transfer matrix for the column-convex cells of the Phase 3 grid
# (docs/middle-kingdom-plan.md, results/middle-kingdom-phase3.md): directedness
# on a column-convex animal is a condition on the bottom profile alone.
build/middle_kingdom_tm: cpp/middle_kingdom_tm.cpp cpp/argparse.h cpp/obs.h | build
	$(CXX) $(CXXFLAGS) -O3 -Icpp $(GMP_CFLAGS) $< -o $@ $(GMP_LDFLAGS)
endif

# Gate MIDDLE-KINGDOM: docs/middle-kingdom-plan.md Phase 3 -- the column
# transfer matrix for every column-convex grid cell vs Phase 0's brute-force
# 16-cell table, the A187077/A007052/convex-polyplet positive controls, and
# the loosened-predicate RED controls. Needs GMP; skipped without it.
gate-middle-kingdom: $(if $(GMP_LDFLAGS),build/middle_kingdom_tm)
	python3 tests/gate_middle_kingdom.py

# P-recurrence / algebraic-relation exclusion mod p (no GMP: the series terms
# are reduced mod p on the way in). docs/middle-kingdom-plan.md Phase 2a.
build/prec_guess: cpp/prec_guess.cpp cpp/argparse.h cpp/obs.h | build
	$(CXX) $(CXXFLAGS) -O3 -Icpp $< -o $@

# Cluster-weight row-transfer DP, C++ port of experiments/cluster_weight_dp.py
# (Severance W1, docs/onset-defect-severance-plan.md section 3): the ab-initio
# interior/boundary/pure weights per composition, levels k = 1..K.
build/severance_w1: cpp/severance_w1.cpp cpp/obs.h | build
	$(CXX) $(CXXFLAGS) -O3 -Icpp -pthread $< -o $@

# Bounded-excess cluster-weight families, C++ port of the row-transfer DP in
# experiments/severance_w3_depths.py (Severance W3): the aggregated interior /
# bottom-edge / pure series by (excess e, surplus k). Feeds the cached table
# results/severance_w3_families_K19_e3.txt that unblocks depth j = 4.
build/severance_w3_families: cpp/severance_w3_families.cpp cpp/obs.h | build
	$(CXX) $(CXXFLAGS) -O3 -Icpp -pthread $< -o $@

# The reach-merged frontier census (A1.1): how many N-key classes at height H,
# measured rather than extrapolated.  Its own --gate reproduces the banked
# class ladder and a rook RED control before it reports any new height.
build/nkey_census: cpp/nkey_census.cpp cpp/obs.h | build
	$(CXX) $(CXXFLAGS) -O3 -Icpp $< -o $@

# The dmirror spine split with a cell budget (A1.3's live half): the hook
# transfer matrix that reaches S = 16, 17, where the Python takes hours at 14.
# Gates against every banked dmirror_strip cell it can reach before reporting.
build/dmirror_spine: cpp/dmirror_spine.cpp cpp/obs.h | build
	$(CXX) $(CXXFLAGS) -O3 -Icpp $< -o $@

# Gate NOTARY: the Lean-ification of the depth-1 closure (campaign Notary,
# docs/notary-lean-plan.md). Fails on any sorry in the Notary modules, then
# builds them; the axiom audits are #guard_msgs blocks inside the modules
# (AuditOutworks pattern), so axiom drift also fails the build. RED until the
# wave-1 agents land their proofs.
#
# TODO(2026-08-19, from the simplify pass): this builds a MODULE LIST, and the
# failure class 79dbc6e fixed is invisible to a module list -- every one of the
# 8643 module targets was green while the root `Polyplets.lean` failed at
# import, because `kingConnected_image` had been declared in two modules and
# only the aggregate sees both.  PROOF-STATUS.md now says in bold "run the
# whole lake build, not a module", which leaves the rule enforced by a human
# remembering a sentence -- the shape a gate exists to replace.  Adding the
# root target `Polyplets` here is the fix; not done in this pass because it
# needs a Lean toolchain to verify (gympie only) and widens what can turn this
# gate red, so it wants its own change with a real build behind it.
NOTARY_MODULES := polyplets/Polyplets/GapWalkBridge.lean \
                  polyplets/Polyplets/DepthOneConstants.lean \
                  polyplets/Polyplets/DepthOneSeries.lean \
                  polyplets/Polyplets/GapWalkRows.lean \
                  polyplets/Polyplets/GapWalkCanon.lean \
                  polyplets/Polyplets/GapWalkTrunc.lean \
                  polyplets/Polyplets/GapWalkStacks.lean \
                  polyplets/Polyplets/GapWalkPeel.lean \
                  polyplets/Polyplets/GapWalkEnds.lean \
                  polyplets/Polyplets/GapWalkBij.lean \
                  polyplets/Polyplets/GapWalkRowVals.lean \
                  polyplets/Polyplets/KernelSeries.lean \
                  polyplets/Polyplets/KernelRoots.lean \
                  polyplets/Polyplets/GapWalkExact.lean \
                  polyplets/Polyplets/GapWalkColumns.lean \
                  polyplets/Polyplets/GapWalkClosing.lean \
                  polyplets/Polyplets/DepthOneKernelSol.lean \
                  polyplets/Polyplets/DepthOneKernelUnique.lean \
                  polyplets/Polyplets/DepthOneKernelPhi.lean
gate-notary:
	@if grep -wn 'sorry\|axiom\|admit' $(NOTARY_MODULES); then \
	  echo 'gate-notary: RED — sorry/axiom/admit present'; exit 1; fi
	cd polyplets && lake build Polyplets.GapWalkBridge \
	  Polyplets.DepthOneConstants Polyplets.DepthOneSeries \
	  Polyplets.GapWalkRows Polyplets.GapWalkCanon Polyplets.GapWalkTrunc \
	  Polyplets.GapWalkStacks Polyplets.GapWalkPeel Polyplets.GapWalkEnds \
	  Polyplets.GapWalkBij Polyplets.GapWalkRowVals \
	  Polyplets.KernelSeries Polyplets.KernelRoots \
	  Polyplets.GapWalkExact Polyplets.GapWalkColumns \
	  Polyplets.GapWalkClosing Polyplets.DepthOneKernelSol \
	  Polyplets.DepthOneKernelUnique Polyplets.DepthOneKernelPhi

# Gate CONVEX-DFINITE: the sharpened order<=20/degree<=20 non-D-finite verdict
# for HV-convex animals by area, king and edge-adjacent, plus the growth
# constants. Deliberately does NOT depend on build/convex_area_tm (GMP is
# optional here): the series files are in the tree, and the gate skips only
# the transfer-matrix oracle when GMP is absent. ~4 s.
gate-convex-dfinite: build/prec_guess
	python3 tests/gate_convex_dfinite.py

# Gate MK-DIR4-PERIM: docs/middle-kingdom-followups-plan.md Phase 2a -- the
# dir4 mode of convex_perim_tm (HV-convex king animals by semiperimeter,
# filtered to half-plane-4-cone-directed, Proposition 2 of
# results/middle-kingdom-phase3.md translated onto the row-built transfer
# matrix) vs directed_cone_anchor's "gridperim" brute force, the RED control
# (dir4bad, the plan's own "non-strict decrease" example), and the termwise
# dir4<=hv sanity check. Needs GMP for convex_perim_tm; skipped without it.
# Unlike its two siblings this gate has NO banked-series fallback -- every check
# in it needs a fresh convex_perim_tm run. Without GMP it would print one skip
# line and return 0, so `make gates` reported a green gate that verified
# nothing. Say so loudly instead; the aggregate still passes, but not quietly.
# Always runs the gate script, even without GMP.  Until 2026-08-22 the no-GMP
# branch was a bare `echo` and `make` exited 0, so this was the one gate that
# could decline to run and still leave the suite green
# (results/gate-class-sweep.md, finding F3).  The script now records the absent
# binary as a SKIPPED CHECK and fails on it, waivable with
# POLY_ALLOW_DEGRADED_GATES=1.
gate-mk-dir4-perim: $(if $(GMP_LDFLAGS),build/convex_perim_tm) build/directed_cone_anchor
	python3 tests/gate_mk_dir4_perim.py

# Gate DIR4-PERIM-ALG: docs/middle-kingdom-followups-plan.md Phase 2b -- the
# (dir4, HV-convex)-by-semiperimeter generating function is ALGEBRAIC of
# degree 4 (results/convex-polyplets.md). Pins the quartic coefficient for
# coefficient, its minimality in both directions, the nullity law a genuine
# minimal relation obeys, and the negative/null controls that keep the
# guesser honest about a positive verdict. Series files only, no GMP. ~8 s.
# The null control is not a file in the tree: the gate re-cuts it into build/
# from results/convex_area_terms_n700_king.txt on every run, and stops RED if
# that source is missing or does not start with its banked prefix.
gate-dir4-perim-alg: build/prec_guess
	python3 tests/gate_dir4_perim_alg.py

# Gate S2: free/one-sided Burnside counts vs A000105/A030222 (oracle-grade)
gate-s2:
	python3 tests/gate_s2.py $(GATE_DEEP)

# ─── Next-system (ns-*) targets ──────────────────────────────────────────────
# All new-system code lives under core/ worker/ orchestrator/ verify/ test/.
# Oracle (build/tma, build/g2) stays in cpp/; both coexist.

NSFLAGS = -std=c++20 -Wall -Wextra -Werror \
          -DGIT_REV='"$(GIT_REV)$(GIT_DIRTY)"' -DBUILD_TIME='"$(BUILD_TIME)"'

# zstd spill compression (POLY_ZSTD): the map/merge workers compress internal
# spill files. libzstd headers live in /usr/include on Linux and /opt/local on
# macOS/MacPorts. Only the C++ workers link it (orchestrate is Go and never
# touches libzstd). AUTO-DETECTED: if the dev header is absent (e.g. ayr, which
# has libzstd runtime but not -dev), POLY_ZSTD is left off and spill files are
# written plain (see core/runfile.h) — the build still compiles cleanly.
ifeq ($(shell uname -s),Darwin)
  ZSTD_HDR := /opt/local/include/zstd.h
else
  ZSTD_HDR := /usr/include/zstd.h
endif
ifneq ($(wildcard $(ZSTD_HDR)),)
  ZSTD_CFLAGS  := -DPOLY_ZSTD
  ZSTD_LDFLAGS := -lzstd
  ifeq ($(shell uname -s),Darwin)
    ZSTD_CFLAGS  += -I/opt/local/include
    ZSTD_LDFLAGS := -L/opt/local/lib -lzstd
  endif
else
  ZSTD_CFLAGS  :=
  ZSTD_LDFLAGS :=
  $(info NOTE: zstd dev header not found ($(ZSTD_HDR)); building without spill compression)
endif

# Every ns binary is header-only against core/; depend on the whole set so an
# edit to any header (incl. the trusted-math copies) triggers the right rebuilds.
NS_HEADERS = $(wildcard core/*.h)

build/ns:
	mkdir -p build/ns

# ns-gates: all new-system gates. Includes the runfile-format, holes, verify,
# height-split, and full-Go-suite gates that existed but were not wired in, so a
# regression in those paths (BUGS-OF-SHAME A4/A5/B*/D6) can't rot undetected.
# gate-g2 is included so the g2 Redelmeier oracle (the independent cross-check
# for T(n,H) and the polyplet totals) has an automatic correctness gate: its hot
# kernel took a burst of perf work (L1..L4, dropped reachedUndo) with no routine
# gate covering it — a miscount would otherwise rely on a dev running `make gates`.
ns-gates: ns-gate-arch ns-gate-math ns-gate-regression ns-gate-fold ns-gate-spill ns-gate-parallel ns-gate-resume-boundaries ns-gate-u128 ns-gate-go ns-gate-run ns-gate-runfile ns-gate-spill-zstd ns-gate-frontier-zstd ns-gate-closedform ns-gate-holes ns-gate-verify ns-gate-split ns-gate-kink ns-gate-kink-column ns-gate-kink-stage-file ns-gate-kink-worker-cli ns-gate-persistent-worker ns-gate-asan ns-gate-diag-pins gate-g2

# Diagonal-pin audit gate (AUDIT-2026-07-30 D4): re-derives nothing, but
# fail-closed checks every wired P_k (k=1..19) against every REAL-swept
# in-onset cell of results/triangle.txt (H <= 21), re-interpolates the levels
# real data alone pins, and prints the per-term conditionality decomposition
# for n=29..40 — the project's circularity map. Wired here so it cannot rot
# again: it had been silently exiting on a parse error since P_17 was wired.
ns-gate-diag-pins:
	python3 scripts/verify_diagonal_pins.py

# Fast gate subset for the pre-push hook (.githooks/pre-push). Targets well under
# 30s: the full Go suite (guards / combine / runcat / closed-form / resume) plus
# the sub-second C++ format+arith gates. The heavy C++ sweeps (spill, parallel,
# holes, maxn=14 regression) stay in `make ns-gates`, run before a release or by
# hand. Order: cheapest, most-targeted tripwires first so a regression fails fast.
# gate-strip-cert rides here (sub-second) because it guards a PUBLISHED rigorous
# bound: a regression that made the exact checker pass unconditionally would turn
# a proof into a wrong number silently. Cheapest possible tripwire for it.
NS_FAST_TARGETS = ns-gate-closedform ns-gate-math ns-gate-run ns-gate-runfile \
  ns-gate-go ns-gate-kink ns-gate-kink-column ns-gate-kink-stage-file \
  ns-gate-kink-worker-cli ns-gate-persistent-worker gate-strip-cert

# Run them one at a time, in this order, each reporting its own wall time -- the
# same 'gate-time Ns target' line `make gates` prints, so the hook's two halves
# are readable the same way. This half is 20 s of a 22 s docs-only push and
# nothing said where it went. Serial by construction (one sub-make at a time),
# so unlike the `gates` sweep there is no shared-prerequisite race to prevent.
# Built before the sweep, for the same reason GATE_PREREQS is: the timed wrapper
# compares a gate's stamp against the BINARY it runs, so the binary has to be
# current before that comparison happens, or an edited source leaves a stale
# binary and the gate skips on it.
NS_FAST_PREREQS = build/ns/gate_math build/ns/gate_run build/ns/gate_runfile \
  build/ns/gate_kink build/ns/gate_kink_column build/ns/gate_kink_stage_file \
  build/ns/gate_kink_worker_cli build/ns/gate_persistent_worker \
  build/ns/map_worker build/ns/merge_worker build/strip_mu_cert

ns-gate-fast: $(NS_FAST_PREREQS)
	@$(MAKE) --no-print-directory -j1 $(addprefix timed-,$(NS_FAST_TARGETS))

# Closed-form invariant gate: assert the engine contributes every KNOWN closed
# form (top strip H=N=3^(N-1); low strips T(n,1)=1, T(n,2) recurrence) DIRECTLY,
# never by enumerating a column — the exact tripwire the H=maxn brute-force
# incident lacked. Add a case here whenever a new closed form or conservation law
# is established (see docs/engineering-standards.md).
ns-gate-closedform:
	go test ./orchestrator/ -run 'TestTopHeight|TestLowHeight|TestPoleHeight|TestHeightNm2' -count=1

# Point git at the committed hooks dir so the pre-push gate runs without copying
# anything into .git. Idempotent; re-run once after cloning.
.PHONY: install-hooks
install-hooks:
	git config core.hooksPath .githooks
	@echo "hooks installed (.githooks); pre-push now runs 'make ns-gate-fast'"

# clangd compile DB (host-specific, git-ignored): resolves project includes and
# gives every header a real TU's flags, killing phantom "core/run.h not found" /
# undeclared-identifier LSP diagnostics. Regenerate after adding/removing a .cpp.
.PHONY: compile-commands
compile-commands:
	./scripts/gen_compile_commands.sh

# Full Go test suite: orchestrator (sweep/guards/combine/runcat/topheight/
# lowheight/resume) + verify (CRC backstop). Locks in the campaign's Go gates,
# including the combine-integrity checks (A5) — no separate ns-gate-combine.
ns-gate-go:
	go test ./orchestrator/... ./verify/...

ns-gate-math: build/ns/gate_math
	./build/ns/gate_math

build/ns/gate_math: test/gate_math.cpp $(NS_HEADERS) | build/ns
	$(CXX) $(NSFLAGS) -O2 -I. $< -o $@

# Run-record gate: serialize round-trip, sort order, combine correctness +
# the combine alloc-churn tripwire (in-window combine must be zero-alloc; A5).
ns-gate-run: build/ns/gate_run
	./build/ns/gate_run

build/ns/gate_run: test/gate_run.cpp $(NS_HEADERS) | build/ns
	$(CXX) $(NSFLAGS) -O2 -I. $< -o $@

# Kink-carry stage kernel gate (Design 14 Phase 1): map_shard_stage (core/kink.h)
# vs ground truth (unwindowed kinkStageTransition) + shard-invariance.
ns-gate-kink: build/ns/gate_kink
	./build/ns/gate_kink

build/ns/gate_kink: test/gate_kink.cpp $(NS_HEADERS) | build/ns
	$(CXX) $(NSFLAGS) $(ZSTD_CFLAGS) -O2 -I. $< -o $@ $(ZSTD_LDFLAGS)

# Kink-carry column-boundary gate (Design 14 Phase 2.2): kinkSeedStage0 +
# kinkFinalizeColumn (core/kink_column.h) vs ground truth (unwindowed,
# no map_shard_stage windowing involved).
ns-gate-kink-column: build/ns/gate_kink_column
	./build/ns/gate_kink_column

build/ns/gate_kink_column: test/gate_kink_column.cpp $(NS_HEADERS) | build/ns
	$(CXX) $(NSFLAGS) $(ZSTD_CFLAGS) -O2 -I. $< -o $@ $(ZSTD_LDFLAGS)

# Kink-carry file-backed stage gate (Design 14 Phase 2.3): map_shard_stage_file
# (core/kink.h) byte-matches the in-RAM map_shard_stage, both direct-write
# and forced-spill.
ns-gate-kink-stage-file: build/ns/gate_kink_stage_file
	./build/ns/gate_kink_stage_file

build/ns/gate_kink_stage_file: test/gate_kink_stage_file.cpp $(NS_HEADERS) | build/ns
	$(CXX) $(NSFLAGS) $(ZSTD_CFLAGS) -O2 -I. $< -o $@ $(ZSTD_LDFLAGS)

# Kink-carry map_worker CLI gate (Design 14 Phase 2.4): drives the REAL
# compiled map_worker binary through --kernel kink --stage seed/<r>/finalize
# for one column and byte-matches --kernel column on the same input.
ns-gate-kink-worker-cli: build/ns/gate_kink_worker_cli build/ns/map_worker
	./build/ns/gate_kink_worker_cli $(GATE_DEEP)

build/ns/gate_kink_worker_cli: test/gate_kink_worker_cli.cpp $(NS_HEADERS) | build/ns
	$(CXX) $(NSFLAGS) $(ZSTD_CFLAGS) -O2 -I. $< -o $@ $(ZSTD_LDFLAGS)

# Persistent-worker gate (Bottleneck #5): drives map_worker --persistent
# through a full kink seed/stage/finalize chain over ONE process (stdin-fed
# requests) and byte-matches the column-kernel one-shot path; also checks
# two independent columns replayed through one process don't bleed state.
ns-gate-persistent-worker: build/ns/gate_persistent_worker build/ns/map_worker build/ns/merge_worker
	./build/ns/gate_persistent_worker $(GATE_DEEP)

build/ns/gate_persistent_worker: test/gate_persistent_worker.cpp $(NS_HEADERS) | build/ns
	$(CXX) $(NSFLAGS) $(ZSTD_CFLAGS) -O2 -I. $< -o $@ $(ZSTD_LDFLAGS)

# Run-file on-disk format gate: atomic publish, sub-CRC, header/.idx magic,
# block-framed frontier compression (compression 2) round-trip + seek.
# Built WITH the zstd flags so it gates the production configuration.
ns-gate-runfile: build/ns/gate_runfile
	./build/ns/gate_runfile

build/ns/gate_runfile: test/gate_runfile.cpp $(NS_HEADERS) | build/ns
	$(CXX) $(NSFLAGS) $(ZSTD_CFLAGS) -O2 -I. $< -o $@ $(ZSTD_LDFLAGS)

# Frontier-compression gate (E3 "Unlit Levers"): the block-framed compression-2
# format that produced the banked a(39)/a(40) frontier had ZERO gate coverage —
# every gate ran with POLY_FRONTIER_ZSTD unset, i.e. plain map/merge outputs, so
# the production configuration was exercised only by the production runs
# themselves. Runs the format gate and the file-backed kink stage gate with
# frontier compression ON at the default frame size AND at a deliberately tiny
# non-power-of-two frame (7 records: many frames, frame boundaries landing
# mid-index-stride, exercising the seek-into-frame path hard), then the
# kink-vs-column sweep equivalence through the REAL worker binaries with
# compression on.
ns-gate-frontier-zstd: build/ns/gate_runfile build/ns/gate_kink_stage_file build/ns/map_worker build/ns/merge_worker
	POLY_FRONTIER_ZSTD=1 ./build/ns/gate_runfile
	POLY_FRONTIER_ZSTD=1 ./build/ns/gate_kink_stage_file
	POLY_FRONTIER_ZSTD=1 POLY_FRONTIER_ZSTD_BLOCK=7 ./build/ns/gate_runfile
	POLY_FRONTIER_ZSTD=1 POLY_FRONTIER_ZSTD_BLOCK=7 ./build/ns/gate_kink_stage_file
	POLY_FRONTIER_ZSTD=1 go test ./orchestrator/ -run TestKinkSweepMatchesColumnSweep -count=1

# Spill-compression gate: zstd round-trip + POLYRUN 2/compression 1 header +
# on-disk shrink; then a NO-POLY_ZSTD build must REJECT the compressed file.
# (The ZSTD binary leaves the compressed file for the noz binary to reject.)
ns-gate-spill-zstd: build/ns/gate_spill_zstd build/ns/gate_spill_zstd_noz
	./build/ns/gate_spill_zstd
	./build/ns/gate_spill_zstd_noz

build/ns/gate_spill_zstd: test/gate_spill_zstd.cpp $(NS_HEADERS) | build/ns
	$(CXX) $(NSFLAGS) $(ZSTD_CFLAGS) -O2 -I. $< -o $@ $(ZSTD_LDFLAGS)

build/ns/gate_spill_zstd_noz: test/gate_spill_zstd_noz.cpp $(NS_HEADERS) | build/ns
	$(CXX) $(NSFLAGS) -O2 -I. $< -o $@

# Architecture fitness: Go boundary tests
ns-gate-arch:
	go test ./verify/arch/... -count=1

# Regression gate (AC-0): driver0 reproduces T(n,H) byte-identical to oracle, n≤14
ns-gate-regression: build/ns/driver0
	./build/ns/driver0 --maxn 14

# Fold gate: fold==unfold byte-identical
ns-gate-fold: build/ns/driver0
	./build/ns/driver0 --maxn 12 --fold-check

build/ns/driver0: test/driver0.cpp $(NS_HEADERS) | build/ns
	$(CXX) $(NSFLAGS) -O2 -I. $< -o $@

build/ns/map_worker: worker/map_worker.cpp $(NS_HEADERS) | build/ns
	$(CXX) $(NSFLAGS) $(ZSTD_CFLAGS) -O3 -I. $< -o $@ $(ZSTD_LDFLAGS)

build/ns/merge_worker: worker/merge_worker.cpp $(NS_HEADERS) | build/ns
	$(CXX) $(NSFLAGS) $(ZSTD_CFLAGS) -O3 -I. $< -o $@ $(ZSTD_LDFLAGS)

# ASan/UBSan builds of the ACTUAL production workers (map_worker/merge_worker,
# both kernels) — see gate-tma/gate-g2 for the same pattern on the oracle
# engines. Separate build dir so --workers-dir can point orchestrate at these
# without disturbing the -O3 production binaries.
build/ns_asan:
	mkdir -p build/ns_asan

build/ns_asan/map_worker: worker/map_worker.cpp $(NS_HEADERS) | build/ns_asan
	$(CXX) $(NSFLAGS) $(ZSTD_CFLAGS) -g -O1 -fsanitize=address,undefined \
	    -fno-omit-frame-pointer -I. $< -o $@ $(ZSTD_LDFLAGS)

build/ns_asan/merge_worker: worker/merge_worker.cpp $(NS_HEADERS) | build/ns_asan
	$(CXX) $(NSFLAGS) $(ZSTD_CFLAGS) -g -O1 -fsanitize=address,undefined \
	    -fno-omit-frame-pointer -I. $< -o $@ $(ZSTD_LDFLAGS)

# ASan/UBSan gate: the real map_worker/merge_worker (both column and kink
# kernels) under sanitizers, small n, --compare against fixtures. This is what
# makes the paper's "engines are ASan/UBSan clean" claim actually cover the
# production pipeline, not just the legacy oracle binaries (build/tma_asan,
# build/g2_asan).
ns-gate-asan: build/ns_asan/map_worker build/ns_asan/merge_worker build/ns/orchestrate
	rm -rf /tmp/ns_asan_column && mkdir -p /tmp/ns_asan_column/spill
	./build/ns/orchestrate --maxn 14 --cores 4 --ram 67108864 --workers-dir build/ns_asan \
	    --run-dir /tmp/ns_asan_column --spill-dir /tmp/ns_asan_column/spill \
	    --checkpoint /tmp/ns_asan_column/POLYCKPT --checkpoint-every 0 --compare
	rm -rf /tmp/ns_asan_kink && mkdir -p /tmp/ns_asan_kink/spill
	./build/ns/orchestrate --maxn 14 --cores 4 --ram 67108864 --kernel kink --workers-dir build/ns_asan \
	    --run-dir /tmp/ns_asan_kink --spill-dir /tmp/ns_asan_kink/spill \
	    --checkpoint /tmp/ns_asan_kink/POLYCKPT --checkpoint-every 0 --compare

build/ns/driver1: test/driver1.cpp $(NS_HEADERS) | build/ns
	$(CXX) $(NSFLAGS) -O2 -I. $< -o $@

# M1 gate: spill-backed driver, n<=14, ram=1 MB forces spill even at this small scale
ns-gate-spill: build/ns/driver1
	mkdir -p /tmp/ns_m1_gate && ./build/ns/driver1 --maxn 14 --ram 1048576 --spill /tmp/ns_m1_gate --compare

build/ns/orchestrate: orchestrator/cmd/orchestrate/main.go orchestrator/*.go | build/ns
	go build -ldflags "-X main.gitRev=$(GIT_REV)$(GIT_DIRTY)" -o $@ ./orchestrator/cmd/orchestrate/

build/ns/runcat: orchestrator/cmd/runcat/main.go orchestrator/*.go | build/ns
	go build -o $@ ./orchestrator/cmd/runcat/

build/ns/predict: orchestrator/cmd/predict/main.go orchestrator/*.go | build/ns
	go build -o $@ ./orchestrator/cmd/predict/

build/ns/combine: orchestrator/cmd/combine/main.go orchestrator/*.go | build/ns
	go build -o $@ ./orchestrator/cmd/combine/

# AC-2a: parallel (cores=4) == serial (cores=1) for n≤14
ns-gate-parallel: build/ns/orchestrate build/ns/map_worker build/ns/merge_worker
	rm -rf /tmp/ns_m2_parallel && mkdir -p /tmp/ns_m2_parallel/spill
	./build/ns/orchestrate --maxn 14 --cores 4 --ram 67108864 \
	    --run-dir /tmp/ns_m2_parallel --spill-dir /tmp/ns_m2_parallel/spill \
	    --checkpoint /tmp/ns_m2_parallel/POLYCKPT --checkpoint-every 0 --compare
	# unit-mult invariance: more units than cores must produce identical totals.
	rm -rf /tmp/ns_m2_parallel && mkdir -p /tmp/ns_m2_parallel/spill
	./build/ns/orchestrate --maxn 14 --cores 4 --unit-mult 4 --ram 67108864 \
	    --run-dir /tmp/ns_m2_parallel --spill-dir /tmp/ns_m2_parallel/spill \
	    --checkpoint /tmp/ns_m2_parallel/POLYCKPT --checkpoint-every 0 --compare

# Multi-machine height-split: two disjoint height subsets, combined, must equal
# the serial total.  Also exercises --per-height-out and combine's coverage check.
ns-gate-split: build/ns/orchestrate build/ns/combine build/ns/map_worker build/ns/merge_worker
	rm -rf /tmp/ns_split && mkdir -p /tmp/ns_split/A/spill /tmp/ns_split/B/spill
	./build/ns/orchestrate --maxn 14 --cores 4 --heights 1-7 --per-height-out /tmp/ns_split/outA \
	    --run-dir /tmp/ns_split/A --spill-dir /tmp/ns_split/A/spill --checkpoint /tmp/ns_split/A/CK --checkpoint-every 0
	./build/ns/orchestrate --maxn 14 --cores 4 --heights 8-14 --per-height-out /tmp/ns_split/outB \
	    --run-dir /tmp/ns_split/B --spill-dir /tmp/ns_split/B/spill --checkpoint /tmp/ns_split/B/CK --checkpoint-every 0
	./build/ns/combine --in /tmp/ns_split/outA,/tmp/ns_split/outB --maxn 14 --compare --require-cover

# AC-2b: resume from EVERY checkpoint boundary reproduces the serial result.
# Exhaustive (not random): the test enumerates each (H,col) checkpoint, cancels
# there via an in-package test seam, resumes, and compares. See resume_test.go.
# TestKinkResumeMidColumn additionally covers a MID-column kill on the kink
# kernel (the seed-contribution double-count regression, kink_resume_midcolumn_test.go).
ns-gate-resume-boundaries: build/ns/map_worker build/ns/merge_worker
	go test ./orchestrator/ -run 'TestKillResumeAllBoundaries|TestKinkResumeMidColumn' -v

# T3.1 gate (AC-3 prerequisite): u128 counter produces byte-identical totals to u64 for n<=14.
# Runs the full orchestrator with --counter u128 and compares against known a(n) fixtures.
ns-gate-u128: build/ns/orchestrate build/ns/map_worker build/ns/merge_worker
	rm -rf /tmp/ns_m3_u128 && mkdir -p /tmp/ns_m3_u128/spill
	./build/ns/orchestrate --maxn 14 --counter u128 --cores 4 --ram 67108864 \
	    --run-dir /tmp/ns_m3_u128 --spill-dir /tmp/ns_m3_u128/spill \
	    --checkpoint /tmp/ns_m3_u128/POLYCKPT --checkpoint-every 0 --compare

# T5.4 gate: holes distribution byte-identical to tma_holes oracle for n<=12
ns-gate-holes: build/ns/gate_holes build/tma_holes
	python3 tests/gate_holes.py 12

# T5.3 gate (AC-5): verifier passes on published dataset; catches deliberate corruption.
ns-gate-verify: build/ns/verify build/ns/orchestrate build/ns/map_worker build/ns/merge_worker
	python3 tests/gate_verify.py

build/ns/verify: verify/cmd/verify/main.go verify/*.go | build/ns
	go build -o $@ ./verify/cmd/verify/

# ─── install ─────────────────────────────────────────────────────────────────
# Copy the ns binaries to $(PREFIX) (default ~/bin) with this build's git
# short-rev appended: orchestrate-<rev>, map_worker-<rev>, merge_worker-<rev>, …
# Rev-suffixed names mean a rebuild at a NEW commit writes new files and never
# clobbers a binary an in-flight run is still spawning (workers respawn every
# column). Discipline: launch real runs from the installed ~/bin/<name>-<rev>
# paths and treat build/ns/ as scratch; then `make install` of a newer rev,
# even mid-run, only touches scratch + new files. An installed orchestrate-<rev>
# auto-finds its same-rev map_worker/merge_worker siblings — no --workers-dir.
PREFIX ?= $(HOME)/bin
INSTALL_REV := $(GIT_REV)$(GIT_DIRTY)
NS_INSTALL_BINS := orchestrate map_worker merge_worker runcat predict combine verify

install: $(addprefix build/ns/,$(NS_INSTALL_BINS))
	mkdir -p $(PREFIX)
	@for b in $(NS_INSTALL_BINS); do \
	    cp -f build/ns/$$b $(PREFIX)/$$b-$(INSTALL_REV) && \
	    echo "installed $(PREFIX)/$$b-$(INSTALL_REV)"; \
	done

build/ns/gate_holes: test/gate_holes.cpp $(NS_HEADERS) | build/ns
	$(CXX) $(NSFLAGS) -O2 -I. $< -o $@

# AC-1 long-run gate (manual invocation; hours to days depending on maxn and box):
#   ./build/ns/driver1 --maxn 18 --ram 67108864 --spill /some/nvme/dir --compare
ns-gate-resume:
	@echo "AC-1 gate (long): ./build/ns/driver1 --maxn 18 --ram 67108864 --spill /tmp/ns_ac1 --compare"

# ─── manuscripts ─────────────────────────────────────────────────────────────
# paper/ holds the manuscripts; papers/ holds the literature this project reads.
# The two are told apart in paper/README.md, which is also where the P/L
# authorship split is spelled out.
#
#   make papers              every manuscript to PDF
#   make paper-L3-lambda-bounds   one, by file stem
#   make papers-verify       the numeric verifiers over the manuscripts
#
# Deliberately NOT in GATE_TARGETS: `make gates` must stay runnable on a box
# with no TeX installed (dalby and ayr are compute boxes and have none).
papers:
	@$(MAKE) --no-print-directory -C paper

paper-%:
	@$(MAKE) --no-print-directory -C paper $*.pdf

papers-verify:
	@$(MAKE) --no-print-directory -C paper verify

papers-list:
	@$(MAKE) --no-print-directory -C paper list

papers-clean:
	@$(MAKE) --no-print-directory -C paper clean

clean:
	rm -rf build
