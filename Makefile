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

.PHONY: gates gate-g1 gate-g2 gate-euler gate-ooc clean

# All currently existing gates
gates: gate-g1 gate-g2 gate-g3 gate-tma gate-s2 gate-e0 gate-sym gate-euler gate-ooc

# Gate G1: naive Python oracle vs pinned OEIS fixtures (quick tier, ~3 s)
gate-g1:
	python3 tests/gate_g1.py

# Gate G2: C++ Redelmeier engine vs oracle + fixtures (+ split, + sanitizers)
gate-g2: build/g2 build/g2_asan
	python3 tests/gate_g2.py

build:
	mkdir -p build

# -Wno-error=restrict on the Redelmeier generator: works around a gcc-12 false
# positive in <bits/char_traits.h> (bogus -Wrestrict on std::string ops; clang and
# gcc-15 don't trip it). Scoped here so -Werror stays strict everywhere else.
build/g2: cpp/g2_redelmeier.cpp | build
	$(CXX) $(CXXFLAGS) -Wno-error=restrict -O3 $< -o $@

# fixed-height transfer matrix over Z/pZ, for generating-function recovery
build/gf_modp: cpp/gf_modp.cpp | build
	$(CXX) $(CXXFLAGS) -O3 $< -o $@

# fixed-height KNIGHT-animal transfer matrix over Z/pZ (horizontal-reach test)
build/gf_knight: cpp/gf_knight.cpp | build
	$(CXX) $(CXXFLAGS) -O3 $< -o $@

build/g2_asan: cpp/g2_redelmeier.cpp | build
	$(CXX) $(CXXFLAGS) -Wno-error=restrict -g -O1 -fsanitize=address,undefined \
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
# in tma_main.cpp). Kept as a separate named binary because the hole drivers
# (gf/hole_recover.py, gf/hole_modp_recover.py) and the exact hole-count runs
# invoke build/tma_holes by name.
build/tma_holes: cpp/tma_main.cpp cpp/tma/*.h | build
	$(CXX) $(CXXFLAGS) -O3 -pthread cpp/tma_main.cpp -o $@

build/tma_asan: cpp/tma_main.cpp cpp/tma/*.h | build
	$(CXX) $(CXXFLAGS) -g -O1 -fsanitize=address,undefined \
	    -fno-omit-frame-pointer -pthread cpp/tma_main.cpp -o $@

# Phase 3.2: blocked drain-and-free store test (tests/gate_blocked.py). Frees each db
# hash-partition as drained -> peak ~1x (next) not ~2x; ~1.94x RSS at N=14.
build/tma_blocked_test: cpp/tma_blocked_test.cpp cpp/tma/*.h | build
	$(CXX) $(CXXFLAGS) -O3 -pthread cpp/tma_blocked_test.cpp -o $@

# Phase 4: out-of-core sweep (tests/gate_ooc.py). db/next live as S disk partitions,
# ~one resident at a time -> RAM ~ peak/S, reach bounded by disk not RAM. Gate: OOC
# a(n) == exact A006770 AND independent of the partition count S.
gate-ooc: build/tma_ooc_test
	python3 tests/gate_ooc.py

build/tma_ooc_test: cpp/tma_ooc_test.cpp cpp/tma/*.h | build
	$(CXX) $(CXXFLAGS) -O3 $< -o $@

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

# Gate G3: Go harness -- format, vet, tests (uses build/g2 where present)
gate-g3: build/g2
	cd harness && test -z "$$(gofmt -l .)" && go vet ./... && go test ./...

harness/harness: harness/*.go
	cd harness && go build -o harness .

clean:
	rm -rf build
