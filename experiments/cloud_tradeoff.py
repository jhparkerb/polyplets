#!/usr/bin/env python3
"""cloud_tradeoff.py -- go/no-go in the form "finish a(n) M hours earlier for D dollars".

The wall of a term is floored by its single most-expensive height (a sequential
column sweep) on the fastest box. Cloud accelerates ONLY that height, on one big
node; home boxes sweep the rest for free under the cloud's wall.

  W_home  = top_cpu_s / dalby_eff_cores        (hours; the home floor)
  W_cloud = top_cpu_s / cloud_eff_cores         (hours; cloud runs the top height)
  M = W_home - W_cloud                          (hours the a(n) finish moves earlier)
  D = W_cloud * rate + preflight_$              (dollars; cloud only bills the top run)
  $/hr-saved = D / M  ->  ~ rate / (speedup - 1) in the large-term limit

Because M and D both scale with top_cpu_s, $/hr-saved is ~constant per box:
the bigger the speedup ratio, the cheaper each hour saved. Calibrate cloud_eff
from the preflight a27 run before trusting these; efficiency at high core counts
is unknown until measured (merge-barrier/straggler tail grows with cores).

Usage: cloud_tradeoff.py TOP_CPU_S [--dalby-eff 64] [--preflight-h 0 --preflight-usd 50]
"""
import argparse

# (label, physical_cores, assumed_eff, usd_per_hr). eff is a PLACEHOLDER until
# the preflight a27 calibration measures it on the actual instance.
BOXES = [
    ("dalby (home, 80c)",        80, 0.80, 0.0),   # reference floor
    ("c7i.48xlarge 96c+SMT",     96, 0.85, 8.60),  # ~115 eff via SMT
    ("hpc7a.96xlarge 192c",     192, 0.70, 7.50),  # recommended: 192 real cores
    ("2-socket 256c (if avail)",256, 0.65, 11.0),  # upper end
]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("top_cpu_s", type=float, help="measured/estimated top-height cpu-seconds")
    ap.add_argument("--dalby-eff", type=float, default=64.0, help="dalby effective cores (80*0.80)")
    ap.add_argument("--preflight-h", type=float, default=0.0, help="preflight hours added to cloud wall (0 if done during prior term)")
    ap.add_argument("--preflight-usd", type=float, default=50.0)
    a = ap.parse_args()

    W_home = a.top_cpu_s / a.dalby_eff / 3600.0
    print(f"top-height = {a.top_cpu_s:,.0f} cpu-s   home floor (dalby {a.dalby_eff:.0f} eff cores) = {W_home:.1f} h\n")
    print(f"{'box':<26}{'eff cores':>10}{'cloud wall':>12}{'M earlier':>12}{'D cost':>10}{'$/hr saved':>12}")
    for label, cores, eff, rate in BOXES:
        ec = cores * eff
        w_cloud = a.top_cpu_s / ec / 3600.0
        if rate == 0.0:   # the home reference row
            print(f"{label:<26}{ec:>10.0f}{w_cloud:>11.1f}h{'  (floor)':>12}{'-':>10}{'-':>12}")
            continue
        w_cloud_total = w_cloud + a.preflight_h
        M = W_home - w_cloud_total
        D = w_cloud * rate + a.preflight_usd
        per = D / M if M > 0 else float('inf')
        print(f"{label:<26}{ec:>10.0f}{w_cloud_total:>11.1f}h{M:>11.1f}h{D:>9.0f}${per:>11.0f}$")
    print("\nDecision: pick the row you like — \"finish a(n) M hours earlier for D dollars\".")
    print("$/hr-saved falls with bigger speedup; preflight amortizes on larger terms.")

if __name__ == "__main__":
    main()
