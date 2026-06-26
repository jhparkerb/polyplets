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

.PHONY: gates gate-g1 gate-g2 gate-euler clean \
        ns-gates ns-gate-arch ns-gate-regression ns-gate-fold ns-gate-resume \
        ns-driver0 build/ns/map_worker build/ns/merge_worker build/ns/driver0

# All currently existing gates
gates: gate-g1 gate-g2 gate-tma gate-s2 gate-e0 gate-sym gate-euler gate-driver

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
build/gf_knight: cpp/gf_knight.cpp | build
	$(CXX) $(CXXFLAGS) -O3 $< -o $@

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

build/ns:
	mkdir -p build/ns

# ns-gates: all new-system gates
ns-gates: ns-gate-arch ns-gate-math ns-gate-regression ns-gate-fold

ns-gate-math: build/ns/gate_math
	./build/ns/gate_math

build/ns/gate_math: test/gate_math.cpp core/signature.h core/transition.h | build/ns
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

build/ns/driver0: test/driver0.cpp core/libenum.h core/run.h core/mapreduce.h \
                  core/counter.h core/classifier.h | build/ns
	$(CXX) $(NSFLAGS) -O2 -I. $< -o $@

build/ns/map_worker: worker/map_worker.cpp core/libenum.h core/run.h core/mapreduce.h \
                     core/counter.h core/classifier.h | build/ns
	$(CXX) $(NSFLAGS) -O3 -I. $< -o $@

build/ns/merge_worker: worker/merge_worker.cpp core/libenum.h core/run.h core/mapreduce.h \
                       core/counter.h core/classifier.h | build/ns
	$(CXX) $(NSFLAGS) -O3 -I. $< -o $@

clean:
	rm -rf build
