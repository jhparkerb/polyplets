#!/usr/bin/env python3
"""RED-modp for LG-JOB-1R: validate cutcount_b1 --modp against the recovered
exact C_H rows, at production state counts.

The recovered run (results/cutcount_b1/rows/C<H>.out, PROVENANCE.md) is an exact
oracle for C_H(n) at every H <= 16. Reducing it mod p gives a per-height check of
the residue path at up to 7.8M frontier states -- 570x the state count of the
deepest check in tests/gate_cutcount_b1.py, which stops at H <= 10.

  usage: r4_a_modp_rowcheck.py <exact_rowdir> <modp_rowdir>

<exact_rowdir> holds C<H>.out with exact values ("n value" lines).
<modp_rowdir>  holds C<H>.p<prime>.out with residues, same line format.

Fail-closed, deliberately: exit 2 on any mismatch, exit 3 if it compared nothing
(an unreadable or misnamed modp dir must not look like a pass -- the same hazard
48ac108 fixed in --assemble), exit 1 on a malformed input. Only exit 0 means the
residues were checked against the oracle and agreed.
"""

import os
import re
import sys

ROWRE = re.compile(r"^C(\d+)\.p(\d+)\.out$")


def load_rows(path):
    """{n: int} from "n value" lines. Raises on a malformed line."""
    out = {}
    with open(path) as f:
        for lineno, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            parts = line.split()
            if len(parts) != 2:
                raise ValueError(f"{path}:{lineno}: expected 'n value', got {line!r}")
            out[int(parts[0])] = int(parts[1])
    return out


def main(argv):
    if len(argv) != 3:
        print(__doc__.strip())
        return 1
    exact_dir, modp_dir = argv[1], argv[2]

    try:
        files = sorted(os.listdir(modp_dir))
    except OSError as e:
        print(f"FAIL cannot read modp dir: {e}")
        return 3

    checked = 0
    mismatches = []
    heights = set()
    for name in files:
        m = ROWRE.match(name)
        if not m:
            continue
        H, p = int(m.group(1)), int(m.group(2))
        exact_path = os.path.join(exact_dir, f"C{H}.out")
        if not os.path.exists(exact_path):
            print(f"skip H={H} p={p}: no exact oracle {exact_path}")
            continue
        try:
            exact = load_rows(exact_path)
            resid = load_rows(os.path.join(modp_dir, name))
        except ValueError as e:
            print(f"FAIL {e}")
            return 1
        if not resid:
            print(f"FAIL {name} is empty -- a row file that compares nothing")
            return 3
        heights.add(H)
        bad_here = 0
        for n, r in sorted(resid.items()):
            if n not in exact:
                print(f"FAIL {name}: n={n} has no exact oracle value")
                return 1
            checked += 1
            if exact[n] % p != r % p:
                bad_here += 1
                if bad_here <= 3:
                    mismatches.append(
                        f"MISMATCH C_{H}({n}) mod {p}: modp={r} exact_mod_p={exact[n] % p}")
        print(f"H={H} p={p}: {len(resid)} values, {bad_here} mismatch")

    for line in mismatches:
        print(line)
    if mismatches:
        print(f"\nFAIL {len(mismatches)} reported mismatch(es) over {checked} values")
        return 2
    if not checked:
        print(f"FAIL compared 0 values (modp dir {modp_dir} has no C<H>.p<prime>.out "
              f"with a matching oracle) -- a check that cannot fail is not a check")
        return 3
    print(f"\nOK {checked} residues match the exact oracle, heights "
          f"{sorted(heights)}, max H={max(heights)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
