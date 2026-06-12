CXX ?= c++
CXXFLAGS = -std=c++20 -Wall -Wextra -Werror

.PHONY: gates gate-g1 gate-g2 clean

# All currently existing gates
gates: gate-g1 gate-g2 gate-g3

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

# Gate G3: Go harness -- format, vet, tests (uses build/g2 where present)
gate-g3: build/g2
	cd harness && test -z "$$(gofmt -l .)" && go vet ./... && go test ./...

harness/harness: harness/*.go
	cd harness && go build -o harness .

clean:
	rm -rf build
