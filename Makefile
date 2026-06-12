.PHONY: gate-g1 gates

# Gate G1: naive Python oracle vs pinned OEIS fixtures (quick tier, ~3 s)
gate-g1:
	python3 tests/gate_g1.py

# All currently existing gates
gates: gate-g1
