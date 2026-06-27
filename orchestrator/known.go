// known.go — load known a(n) values from an OEIS-style b-file fixture.
package orchestrator

import (
	"os"
	"strconv"
	"strings"
)

// LoadKnown parses an OEIS b-file (lines "<n> <a(n)>", '#' comments ignored)
// into a slice indexed by n, with index 0 seeded to 0.  Used by the production
// --compare path and the resume gate to check the computed triangle.
func LoadKnown(path string) ([]uint64, error) {
	data, err := os.ReadFile(path)
	if err != nil {
		return nil, err
	}
	known := []uint64{0}
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
		v, err2 := strconv.ParseUint(parts[1], 10, 64)
		if err1 != nil || err2 != nil || n < 0 {
			continue
		}
		for n >= len(known) {
			known = append(known, 0)
		}
		known[n] = v
	}
	return known, nil
}
