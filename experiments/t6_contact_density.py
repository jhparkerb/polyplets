#!/usr/bin/env python3
# T6: the diagonal-contact density of polyplets. The mean number of diagonal (king-not-rook)
# contacts of a uniform random n-cell polyplet grows like c*n; c is a new lattice constant.
# Estimated here from the exact contact totals (experiments/contact_counts.py, n<=9, row sums
# = A006770). The first differences of the mean converge cleanly to c. The RIGOROUS value is
# d/dt log lambda(t) at t=1, lambda(t) = dominant eigenvalue of the diagonal-contact-marked
# column transfer matrix (mark each transition by t^(#diagonal adjacencies it creates)) --
# engine work, noted for later.
tot = [0, 2, 24, 212, 1700, 13050, 97856, 723522, 5300980]   # total diagonal contacts, n=1..9
a = [1, 4, 20, 110, 638, 3832, 23592, 147941, 940982]        # A006770

mean = [tot[i] / a[i] for i in range(len(a))]
diff = [mean[i] - mean[i - 1] for i in range(1, len(a))]
print("n            : " + " ".join(f"{n:7d}" for n in range(1, len(a) + 1)))
print("mean contacts: " + " ".join(f"{m:7.3f}" for m in mean))
print("Delta (-> c) :         " + " ".join(f"{d:7.3f}" for d in diff))
print()
print(f"diagonal-contact density  c = lim Delta(mean) ~ {diff[-1]:.3f}")
print(f"  (monotone, flattening: ...{diff[-3]:.3f}, {diff[-2]:.3f}, {diff[-1]:.3f}; c ~ 0.743 +- 0.002)")
print(f"  mean #contacts ~ {diff[-1]:.2f}*n - O(1); a uniform polyplet is ~3/4-saturated per cell")
print("  in diagonal contacts. Rigorous c via the marked transfer matrix is future work.")
