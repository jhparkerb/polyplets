CXX ?= c++
CXXFLAGS = -std=c++20 -Wall -Wextra -Werror

.PHONY: gates gate-g1 gate-g2 clean

# All currently existing gates
gates: gate-g1 gate-g2 gate-g3 gate-tma gate-s2 gate-e0 gate-sym

# Gate G1: naive Python oracle vs pinned OEIS fixtures (quick tier, ~3 s)
gate-g1:
	python3 tests/gate_g1.py

# Gate G2: C++ Redelmeier engine vs oracle + fixtures (+ split, + sanitizers)
gate-g2: build/g2 build/g2_asan
	python3 tests/gate_g2.py

build:
	mkdir -p build

build/g2: cpp/g2_redelmeier.cpp | build
	$(CXX) $(CXXFLAGS) -O3 $< -o $@

build/g2_asan: cpp/g2_redelmeier.cpp | build
	$(CXX) $(CXXFLAGS) -g -O1 -fsanitize=address,undefined \
	    -fno-omit-frame-pointer $< -o $@

# Gate TMA: transfer-matrix engine vs fixtures + G2 height marginals
gate-tma: build/tma build/tma_asan build/g2
	python3 tests/gate_tma.py

build/tma: cpp/tma_main.cpp cpp/tma/*.h | build
	$(CXX) $(CXXFLAGS) -O3 cpp/tma_main.cpp -o $@

build/tma_asan: cpp/tma_main.cpp cpp/tma/*.h | build
	$(CXX) $(CXXFLAGS) -g -O1 -fsanitize=address,undefined \
	    -fno-omit-frame-pointer cpp/tma_main.cpp -o $@

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
