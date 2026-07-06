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

.PHONY: gates gate-g1 gate-g2 gate-euler clean install \
        ns-gates ns-gate-arch ns-gate-regression ns-gate-fold ns-gate-resume \
        ns-gate-parallel ns-gate-resume-boundaries ns-gate-u128 ns-gate-holes \
        ns-gate-verify ns-gate-kink ns-gate-kink-column ns-gate-kink-stage-file \
        ns-gate-kink-worker-cli \
        ns-driver0 build/ns/map_worker build/ns/merge_worker build/ns/driver0 \
        build/ns/orchestrate build/ns/runcat build/ns/predict build/ns/combine build/ns/gate_holes build/ns/verify

# All currently existing gates
gates: gate-g1 gate-g2 gate-tma gate-s2 gate-e0 gate-sym gate-symtm gate-euler gate-driver

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
	$(CXX) $(CXXFLAGS) $(RESTRICT_FLAG) -O3 $< -o $@

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

# Gate E0: weighted connected-subgraph counter vs brute force
gate-e0: build/subgraph_count
	python3 tests/gate_e0.py

build/subgraph_count: cpp/sym/subgraph_count.cpp | build
	$(CXX) $(CXXFLAGS) -O3 $< -o $@

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
ns-gates: ns-gate-arch ns-gate-math ns-gate-regression ns-gate-fold ns-gate-spill ns-gate-parallel ns-gate-resume-boundaries ns-gate-u128 ns-gate-go ns-gate-run ns-gate-runfile ns-gate-spill-zstd ns-gate-closedform ns-gate-holes ns-gate-verify ns-gate-split ns-gate-kink ns-gate-kink-column ns-gate-kink-stage-file ns-gate-kink-worker-cli

# Fast gate subset for the pre-push hook (.githooks/pre-push). Targets well under
# 30s: the full Go suite (guards / combine / runcat / closed-form / resume) plus
# the sub-second C++ format+arith gates. The heavy C++ sweeps (spill, parallel,
# holes, maxn=14 regression) stay in `make ns-gates`, run before a release or by
# hand. Order: cheapest, most-targeted tripwires first so a regression fails fast.
ns-gate-fast: ns-gate-closedform ns-gate-math ns-gate-run ns-gate-runfile ns-gate-go ns-gate-kink ns-gate-kink-column ns-gate-kink-stage-file ns-gate-kink-worker-cli

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
	$(CXX) $(NSFLAGS) -O2 -I. $< -o $@

# Kink-carry column-boundary gate (Design 14 Phase 2.2): kinkSeedStage0 +
# kinkFinalizeColumn (core/kink_column.h) vs ground truth (unwindowed,
# no map_shard_stage windowing involved).
ns-gate-kink-column: build/ns/gate_kink_column
	./build/ns/gate_kink_column

build/ns/gate_kink_column: test/gate_kink_column.cpp $(NS_HEADERS) | build/ns
	$(CXX) $(NSFLAGS) -O2 -I. $< -o $@

# Kink-carry file-backed stage gate (Design 14 Phase 2.3): map_shard_stage_file
# (core/kink.h) byte-matches the in-RAM map_shard_stage, both direct-write
# and forced-spill.
ns-gate-kink-stage-file: build/ns/gate_kink_stage_file
	./build/ns/gate_kink_stage_file

build/ns/gate_kink_stage_file: test/gate_kink_stage_file.cpp $(NS_HEADERS) | build/ns
	$(CXX) $(NSFLAGS) -O2 -I. $< -o $@

# Kink-carry map_worker CLI gate (Design 14 Phase 2.4): drives the REAL
# compiled map_worker binary through --kernel kink --stage seed/<r>/finalize
# for one column and byte-matches --kernel column on the same input.
ns-gate-kink-worker-cli: build/ns/gate_kink_worker_cli build/ns/map_worker
	./build/ns/gate_kink_worker_cli

build/ns/gate_kink_worker_cli: test/gate_kink_worker_cli.cpp $(NS_HEADERS) | build/ns
	$(CXX) $(NSFLAGS) -O2 -I. $< -o $@

# Run-file on-disk format gate: atomic publish, sub-CRC, header/.idx magic.
ns-gate-runfile: build/ns/gate_runfile
	./build/ns/gate_runfile

build/ns/gate_runfile: test/gate_runfile.cpp $(NS_HEADERS) | build/ns
	$(CXX) $(NSFLAGS) -O2 -I. $< -o $@

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
ns-gate-resume-boundaries: build/ns/map_worker build/ns/merge_worker
	go test ./orchestrator/ -run TestKillResumeAllBoundaries -v

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

clean:
	rm -rf build
