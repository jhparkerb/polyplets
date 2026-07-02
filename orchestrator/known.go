// known.go — load known a(n) values from an OEIS-style b-file fixture.
package orchestrator

import (
	"fmt"
	"math/big"
	"os"
	"strconv"
	"strings"
)

// CompareToKnown prints "n=.. a(n)=.. known=.. OK|FAIL" for n=1..maxn and
// returns whether every entry matched. Shared by the orchestrate --compare path
// and the combine tool; each caller prints its own PASS/FAIL summary line.
func CompareToKnown(maxn int, triangle, known []*big.Int) bool {
	allOK := true
	for n := 1; n <= maxn; n++ {
		got := big.NewInt(0)
		if n < len(triangle) && triangle[n] != nil {
			got = triangle[n]
		}
		want := big.NewInt(0)
		if n < len(known) && known[n] != nil {
			want = known[n]
		}
		status := "OK"
		if got.Cmp(want) != 0 {
			status = "FAIL"
			allOK = false
		}
		fmt.Printf("n=%2d  a(n)=%d  known=%d  %s\n", n, got, want, status)
	}
	return allOK
}

// LoadKnown parses an OEIS b-file (lines "<n> <a(n)>", '#' comments ignored)
// into a slice indexed by n, with index 0 seeded to 0.  Used by the production
// --compare path and the resume gate to check the computed triangle.
func LoadKnown(path string) ([]*big.Int, error) {
	data, err := os.ReadFile(path)
	if err != nil {
		return nil, err
	}
	known := []*big.Int{big.NewInt(0)}
	for _, line := range strings.Split(string(data), "\n") {
		line = strings.TrimSpace(line)
		if line == "" || strings.HasPrefix(line, "#") {
			continue
		}
		parts := strings.Fields(line)
		if len(parts) < 2 {
			continue
		}
		n, err1 := strconv.Atoi(parts[0])
		v, ok := new(big.Int).SetString(parts[1], 10)
		if err1 != nil || !ok || n < 0 {
			continue
		}
		for n >= len(known) {
			known = append(known, big.NewInt(0))
		}
		known[n] = v
	}
	return known, nil
}
