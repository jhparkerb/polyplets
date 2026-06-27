// predict — a-priori wall/RAM estimate for a target n from a measured cost
// profile, and (optionally) a synthesized reference profile for the live ETA.
//
// The model is deliberately simple so the probe can validate it: total run cost
// scales by a per-term work ratio R, i.e. wall(n) = wall(n0) * R^(n-n0). R is
// either supplied (--ratio) or measured from two profiles (--profile2): a
// stable, measured R is the whole point — we validate by predicting a(20) from
// a(19) and checking the error before trusting the a(21) number.
//
// Usage:
//   predict --profile P19.tsv --to 20 [--ratio R | --profile2 P18.tsv] [--out P20ref.tsv]
//
// Limitation: the synthesized --out profile keeps the source n0's (H,col) set,
// so it omits target-n's new heights/columns (tail cells, small cost). The
// live-ETA online correction absorbs that drift; the headline total already
// accounts for it via R^(n-n0).
package main

import (
	"flag"
	"fmt"
	"math"
	"os"

	"polyominoes/orchestrator"
)

func main() {
	profile := flag.String("profile", "", "cost profile to scale (required)")
	profile2 := flag.String("profile2", "", "second (earlier) profile to measure R from")
	to := flag.Int("to", 0, "target n (required)")
	ratio := flag.Float64("ratio", 0, "per-term work ratio R (overrides --profile2; default 4.4 if neither given)")
	out := flag.String("out", "", "write a synthesized reference profile for the target n")
	flag.Parse()

	if *profile == "" || *to == 0 {
		fmt.Fprintln(os.Stderr, "predict: --profile and --to are required")
		os.Exit(2)
	}

	rows, meta, err := orchestrator.ReadCostProfileFull(*profile)
	if err != nil {
		fmt.Fprintf(os.Stderr, "predict: read %s: %v\n", *profile, err)
		os.Exit(1)
	}
	from := meta.Maxn
	if from == 0 {
		fmt.Fprintln(os.Stderr, "predict: profile has no maxn header")
		os.Exit(1)
	}
	total, peakRSS := summarize(rows)

	R, rbasis := resolveRatio(*ratio, total, from, *profile2)
	delta := *to - from
	scale := math.Pow(R, float64(delta))
	predWall := total * scale
	predRSS := peakRSS * scale // rough: peak state count grows ~R/term

	fmt.Printf("predict from=%d to=%d R=%.4f (%s) delta=%d\n", from, *to, R, rbasis, delta)
	fmt.Printf("  basis_wall_s=%.0f (%s)\n", total, humanDur(total))
	fmt.Printf("  predicted_wall_s=%.0f (%s)\n", predWall, humanDur(predWall))
	fmt.Printf("  predicted_peak_rss_mb=%.0f (%.1f GB)\n", predRSS, predRSS/1024)
	fmt.Printf("  caveat: R^delta scaling; peak-RSS and disk are approximate.\n")

	if *out != "" {
		if err := writeScaled(*out, rows, *to, meta.Cores, scale); err != nil {
			fmt.Fprintf(os.Stderr, "predict: write %s: %v\n", *out, err)
			os.Exit(1)
		}
		fmt.Printf("  wrote reference profile %s (sum=%.0fs)\n", *out, predWall)
	}
}

func summarize(rows []orchestrator.ColumnCost) (totalWall, peakRSS float64) {
	for _, c := range rows {
		totalWall += c.WallS
		if c.RSSMax > peakRSS {
			peakRSS = c.RSSMax
		}
	}
	return
}

// resolveRatio returns the per-term work ratio R and its provenance.
// --ratio wins; else R is measured from the (primary, --profile2) pair as
// (totalHi/totalLo)^(1/(nHi-nLo)); else it falls back to 4.4.
func resolveRatio(ratioFlag, primaryTotal float64, primaryN int, profile2 string) (float64, string) {
	if ratioFlag > 0 {
		return ratioFlag, "flag"
	}
	if profile2 == "" {
		return 4.4, "default"
	}
	rows2, meta2, err := orchestrator.ReadCostProfileFull(profile2)
	if err != nil || meta2.Maxn == 0 || meta2.Maxn == primaryN {
		return 4.4, "default (profile2 unusable)"
	}
	total2, _ := summarize(rows2)
	hiT, hiN, loT, loN := primaryTotal, primaryN, total2, meta2.Maxn
	if meta2.Maxn > primaryN {
		hiT, hiN, loT, loN = total2, meta2.Maxn, primaryTotal, primaryN
	}
	if loT <= 0 {
		return 4.4, "default (zero basis)"
	}
	R := math.Pow(hiT/loT, 1.0/float64(hiN-loN))
	return R, fmt.Sprintf("measured from n=%d,%d", loN, hiN)
}

func writeScaled(path string, rows []orchestrator.ColumnCost, maxn, cores int, scale float64) error {
	f, err := os.Create(path)
	if err != nil {
		return err
	}
	defer f.Close()
	fmt.Fprintf(f, "# cost_profile maxn=%d cores=%d (synthesized, scale=%.4f)\n", maxn, cores, scale)
	fmt.Fprintf(f, "# H\tcol\tfrontier_in\tfrontier_out\twall_s\tcpu_s\trss_max_mb\n")
	for _, c := range rows {
		fmt.Fprintf(f, "%d\t%d\t%d\t%d\t%.3f\t%.3f\t%.1f\n",
			c.H, c.Col, c.FrontierIn, c.FrontierOut, c.WallS*scale, c.CPUS*scale, c.RSSMax*scale)
	}
	return nil
}

func humanDur(s float64) string {
	switch {
	case s < 90:
		return fmt.Sprintf("%.0fs", s)
	case s < 5400:
		return fmt.Sprintf("%.1fm", s/60)
	case s < 172800:
		return fmt.Sprintf("%.1fh", s/3600)
	default:
		return fmt.Sprintf("%.1fd", s/86400)
	}
}
