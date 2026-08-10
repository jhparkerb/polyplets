CXX ?= c++
CXXFLAGS = -std=c++20 -Wall -Wextra -Werror

# Provenance baked at BUILD time (docs/observability.md): a compiled binary
# outlives the source state, so it must report the commit it was BUILT at, not
# whatever the tree is now. GIT_REV carries a -dirty suffix when the tree differs
# from HEAD at all (untracked included), matching Python obs.py's porcelain check.
# cpp/obs.h reads these via -D; absent them it falls back to "unknown".
GIT_REV    := $(shell git rev-parse --short HEAD 2>/dev/null || echo unknown)
GIT_DIRTY  := $(shell test -n "$$(git status --porcelain 2>/dev/null)" && echo -dirty)
BUILD_TIME := $(shell date +%Y-%m-%dT%H:%M:%S%z)
CXXFLAGS += -DGIT_REV='"$(GIT_REV)$(GIT_DIRTY)"' -DBUILD_TIME='"$(BUILD_TIME)"'

# -Wno-error=restrict is a gcc-only workaround (gcc-12 false positive on the
# Redelmeier generator, see build/g2 below). clang rejects the unknown flag, so
# apply it only when the compiler is gcc; empty for clang.
RESTRICT_FLAG := $(if $(findstring clang,$(shell $(CXX) --version 2>/dev/null)),,-Wno-error=restrict)

# The Redelmeier kernel (build/g2) is measurably faster built with clang on
# aarch64: ~9% over gcc-15 on Neoverse-N1 (measured, results/terminal-velocity.md),
# and gcc PGO / -mcpu gave nothing. Prefer clang for the OPTIMIZED g2 only, per
# box (clang++-19 on dalby, clang++ on mac/gympie), falling back to $(CXX) where
# clang is absent (e.g. ayr uses g++). g2_asan stays on $(CXX): keeping the two
# builds on different compilers turns gate-g2 check D into a two-compiler count
# cross-check for free.
G2CXX := $(shell command -v clang++-19 2>/dev/null || command -v clang++ 2>/dev/null || echo $(CXX))
G2_RESTRICT := $(if $(findstring clang,$(shell $(G2CXX) --version 2>/dev/null)),,-Wno-error=restrict)

.PHONY: gates gate-g1 gate-g2 gate-euler gate-strip-cert gate-strip-fast \
        gate-king-grid gate-site-perim gate-multidirected gate-convex-dfinite \
        gate-middle-kingdom gate-mk-dir4-perim gate-dir4-perim-alg \
        gate-compile-db gate-citations gate-l-paper-verifier \
        gate-perimeter-min gate-perimeter-defect \
        gate-perimeter-min-shard clean install \
        ns-gates ns-gate-arch ns-gate-regression ns-gate-fold ns-gate-resume \
        ns-gate-parallel ns-gate-resume-boundaries ns-gate-u128 ns-gate-holes \
        ns-gate-verify ns-gate-kink ns-gate-kink-column ns-gate-kink-stage-file \
        ns-gate-kink-worker-cli ns-gate-persistent-worker ns-gate-asan \
        ns-gate-frontier-zstd ns-gate-diag-pins \
        ns-driver0 build/ns/map_worker build/ns/merge_worker build/ns/driver0 \
        build/ns/orchestrate build/ns/runcat build/ns/predict build/ns/combine build/ns/gate_holes build/ns/verify \
        papers papers-verify papers-clean papers-list

# All currently existing gates
GATE_TARGETS = gate-citations gate-l-paper-verifier gate-perimeter-min gate-perimeter-min-shard gate-perimeter-defect gate-g1 gate-g2 gate-tma gate-s2 gate-e0 gate-sym gate-symtm gate-subgroup gate-euler gate-driver gate-strip-cert gate-strip-fast gate-king-grid gate-site-perim gate-multidirected gate-convex-dfinite gate-middle-kingdom gate-mk-dir4-perim gate-dir4-perim-alg gate-compile-db

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

gates:
	@$(MAKE) --no-print-directory -j$(JOBS) $(GATE_TARGETS)

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
# missing animal. Includes a RED control. ~2 s.
gate-perimeter-min: build/perimeter_min build/g2
	./scripts/perimeter_min_gate.sh

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

# Gate G1: naive Python oracle vs pinned OEIS fixtures (quick tier, ~3 s)
gate-g1:
	python3 tests/gate_g1.py

# Gate DRIVER: reach driver/combine reject crashed/raced/corrupt sweeps (no silent zeros)
gate-driver: build/tma
	python3 tests/gate_driver_robust.py

# Gate G2: C++ Redelmeier engine vs oracle + fixtures (+ split, + sanitizers)
gate-g2: build/g2 build/g2_asan
	python3 tests/gate_g2.py

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

# Gate TMA: transfer-matrix engine vs fixtures + G2 height marginals
gate-tma: build/tma build/tma_asan build/tma_holes build/g2
	python3 tests/gate_tma.py

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
	python3 tests/gate_symtm.py

# Gate sym: symmetric-polyplet counters (4 types) + free count vs A030222
gate-sym: build/symcount_fast
	python3 tests/gate_sym.py

# Gate subgroup: per-SUBGROUP invariant counts + the a(n) mod 4 congruence
gate-subgroup: build/symcount_fast build/symtm
	python3 tests/gate_subgroup.py

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
	python3 tests/gate_king_grid.py

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
	python3 tests/gate_multidirected.py

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

# Gate NOTARY: the Lean-ification of the depth-1 closure (campaign Notary,
# docs/notary-lean-plan.md). Fails on any sorry in the Notary modules, then
# builds them; the axiom audits are #guard_msgs blocks inside the modules
# (AuditOutworks pattern), so axiom drift also fails the build. RED until the
# wave-1 agents land their proofs.
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
                  polyplets/Polyplets/DepthOneKernelUnique.lean
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
	  Polyplets.DepthOneKernelUnique

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
gate-mk-dir4-perim: $(if $(GMP_LDFLAGS),build/convex_perim_tm) build/directed_cone_anchor
	$(if $(GMP_LDFLAGS),python3 tests/gate_mk_dir4_perim.py,@echo "*** GATE MK-DIR4-PERIM NOT RUN: no GMP, and this gate has no banked-series fallback -- NOTHING was verified ***")

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
	python3 tests/gate_s2.py

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
ns-gate-fast: ns-gate-closedform ns-gate-math ns-gate-run ns-gate-runfile ns-gate-go ns-gate-kink ns-gate-kink-column ns-gate-kink-stage-file ns-gate-kink-worker-cli ns-gate-persistent-worker gate-strip-cert

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
	./build/ns/gate_kink_worker_cli

build/ns/gate_kink_worker_cli: test/gate_kink_worker_cli.cpp $(NS_HEADERS) | build/ns
	$(CXX) $(NSFLAGS) $(ZSTD_CFLAGS) -O2 -I. $< -o $@ $(ZSTD_LDFLAGS)

# Persistent-worker gate (Bottleneck #5): drives map_worker --persistent
# through a full kink seed/stage/finalize chain over ONE process (stdin-fed
# requests) and byte-matches the column-kernel one-shot path; also checks
# two independent columns replayed through one process don't bleed state.
ns-gate-persistent-worker: build/ns/gate_persistent_worker build/ns/map_worker build/ns/merge_worker
	./build/ns/gate_persistent_worker

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
