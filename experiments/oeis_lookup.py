#!/usr/bin/env python3
"""Read-only OEIS lookup by term list -- the novelty check, nothing else.

results/subclasses.md Phase 3 needs a novelty verdict per grid cell, and
the repo's practice is that submission is jasonp's call, gated on the viva.
This script therefore ONLY reads: it GETs oeis.org/search?fmt=json and prints
what came back. It has no write path of any kind.

oeis.org answers 403 to some clients (recorded in results/subclasses.md on
2026-08-05, which is why that note's novelty check is marked unchecked); a
plain curl-style User-Agent gets through, so one is set here.

Usage:
  python3 experiments/oeis_lookup.py 1,4,17,73,314,1351 [more,term,lists ...]
  python3 experiments/oeis_lookup.py --file results/mk_ccdir4_terms_n700.txt
    (--file takes the first --count terms, default 10, of an "n value" file)

stdout: one block per query -- the A-numbers, names, and the stored terms of
every hit, or "NO MATCH" (which is the novelty verdict, subject to the usual
caveat that OEIS search needs the terms to line up with the entry's offset).
"""
import argparse
import json
import sys
import time
import urllib.request

URL = "https://oeis.org/search?q=%s&fmt=json"
UA = "polyomino-research/1.0 (read-only novelty check)"


def read_terms(path, count):
    vals = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                vals.append(line.split()[-1])
            if len(vals) >= count:
                break
    return ",".join(vals)


def lookup(query):
    req = urllib.request.Request(URL % query, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        body = r.read().decode()
    data = json.loads(body) if body.strip() else None
    if data is None:
        return []
    # The JSON endpoint returns a bare list of entries, or {"results": [...]}
    return data.get("results") or [] if isinstance(data, dict) else data


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("queries", nargs="*")
    ap.add_argument("--file", action="append", default=[])
    ap.add_argument("--count", type=int, default=10)
    ap.add_argument("--full", action="store_true",
                    help="also print offset/comment/formula fields")
    args = ap.parse_args()

    queries = list(args.queries)
    for path in args.file:
        queries.append(read_terms(path, args.count))
    if not queries:
        ap.error("nothing to look up")

    for i, q in enumerate(queries):
        if i:
            time.sleep(2)  # be polite to oeis.org
        print(f"=== {q}")
        try:
            hits = lookup(q)
        except Exception as exc:  # network/HTTP failure is a real answer here
            print(f"  LOOKUP FAILED: {exc}")
            continue
        if not hits:
            print("  NO MATCH")
            continue
        for h in hits[:8]:
            print(f"  A{h['number']:06d}  {h['name']}")
            print(f"      offset={h.get('offset')}")
            print(f"      {h['data'][:150]}")
            if args.full:
                for com in h.get("comment", [])[:6]:
                    print(f"      C: {com}")
                for fo in h.get("formula", [])[:4]:
                    print(f"      F: {fo}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
