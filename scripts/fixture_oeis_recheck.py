#!/usr/bin/env python3
"""Re-verify every fixture against OEIS, over the network. NOT a gate.

`docs/engine-record.md` finding F5: `fixtures/` is protected by
`SHA256SUMS`, and `tests/gate_g1.py` checks it before doing anything else --
corrupting `fixtures/b006770.txt` by 1 turns gate-g1, gate-g2 and gate-sym red.
But SHA256SUMS is itself regenerable, so the pinning is against ACCIDENT and not
against a deliberate edit of both, and nothing re-checks a fixture against the
source it came from.

That cannot be fixed inside the gate suite: the gates must run with no network,
on three boxes, in a pre-push hook. So the control is this script, run
deliberately -- before a release, or whenever a fixture is touched.

**The sweep also over-credited the existing mitigation.** It said the b-file
headers record the OEIS revision and date they were checked against. That is
true of exactly ONE fixture, `b006770.txt`. Of the other fourteen, three carry
partial attribution lines copied from OEIS and eleven carry no provenance at
all -- they are bare columns of numbers with nothing saying where they came
from or when anyone last looked.

WHAT IT CHECKS, per fixture:

  * every n present in BOTH our copy and the OEIS b-file must have the same
    value -- a disagreement is the finding this exists for;
  * terms we carry BEYOND the OEIS b-file's range are reported as locally
    sourced, not as errors: `b001168.txt` deliberately carries a(57)-a(66) from
    Barequet and Ben-Shachar (2024), and `b006770.txt` is explicitly "NOT
    uniformly external";
  * terms OEIS carries beyond ours are reported too -- that is the sequence
    having moved on, and it is worth knowing before anyone calls our copy
    current.

It writes nothing. Stamping a verified header is a separate, deliberate edit.

Usage:
    python3 scripts/fixture_oeis_recheck.py            # all fixtures
    python3 scripts/fixture_oeis_recheck.py b006770    # one

Target machine: dalby or ayr (needs outbound network; project code does not run
on gympie). Cost: seconds, one HTTP GET per fixture, read-only.
"""

import os
import re
import sys
import time
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIX = os.path.join(ROOT, "fixtures")
UA = "polyplets-fixture-recheck/1.0 (read-only verification)"


def parse(text):
    out = {}
    for ln in text.splitlines():
        ln = ln.strip()
        if not ln or ln.startswith("#"):
            continue
        f = ln.split()
        if len(f) == 2 and f[0].lstrip("-").isdigit():
            out[int(f[0])] = int(f[1])
    return out


def fetch(anum):
    url = "https://oeis.org/A%06d/b%06d.txt" % (anum, anum)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode("utf-8", "replace")


def main():
    want = sys.argv[1:]
    names = sorted(f for f in os.listdir(FIX)
                   if re.fullmatch(r"b\d{6}\.txt", f))
    if want:
        names = [n for n in names if any(w in n for w in want)]
    if not names:
        print("no fixtures matched")
        return 1

    print("Re-checking %d fixture(s) against OEIS.  Read-only; writes nothing.\n"
          % len(names))
    bad = 0
    for i, name in enumerate(names):
        anum = int(name[1:7])
        ours = parse(open(os.path.join(FIX, name)).read())
        try:
            theirs = parse(fetch(anum))
        except Exception as e:                                  # noqa: BLE001
            print("  %-14s FETCH FAILED: %s" % (name, e))
            bad += 1
            continue
        shared = sorted(set(ours) & set(theirs))
        clash = [n for n in shared if ours[n] != theirs[n]]
        ours_only = sorted(set(ours) - set(theirs))
        theirs_only = sorted(set(theirs) - set(ours))
        status = "OK" if not clash else "**DISAGREES**"
        print("  %-14s A%06d  %s  %d shared terms agree"
              % (name, anum, status, len(shared) - len(clash)))
        if clash:
            bad += 1
            for n in clash[:5]:
                print("      n=%d: ours %s, OEIS %s" % (n, ours[n], theirs[n]))
        if ours_only:
            print("      ours extends past OEIS at n = %s%s  (locally sourced "
                  "-- the file's header must say by whom)"
                  % (", ".join(str(n) for n in ours_only[:8]),
                     " ..." if len(ours_only) > 8 else ""))
        if theirs_only:
            print("      OEIS has %d term(s) we do not, n = %d..%d"
                  % (len(theirs_only), theirs_only[0], theirs_only[-1]))
        if i + 1 < len(names):
            time.sleep(1.0)                                    # be polite

    print("\n%d fixture(s) checked, %d with a problem." % (len(names), bad))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
