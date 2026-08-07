#!/usr/bin/env python3
"""Merge per-frame perimeter_min runs into the monolithic run's output format.

The monolithic `perimeter_min LAT PMAX RMAX` enumerates every frame whose
filled-box perimeter is <= PMAX, applies each frame's transpose multiplicity,
and prints one accumulated tally at exit.  `--only W H PARITY` runs a single
frame -- but pushes it with **mult forced to 1** (cpp/perimeter_min.cpp:465),
so the multiplicity has to be reapplied here, from the plan the binary itself
emitted.  Getting that wrong silently halves every W<H frame, which is exactly
the kind of error a merge step exists to make impossible rather than unlikely.

No filtering by PMAX: the monolithic run does not filter either (PMAX selects
frames, not rows), so its output carries partial rows above PMAX under the
"COMPLETE only for" banner.  Merging must reproduce that byte for byte or the
sharded path is not a drop-in replacement for the banked p40/p44 files.

Usage:  perimeter_min_merge.py FRAMEDIR LATTICE PMAX RMAX > merged.txt
"""
import re
import sys
from collections import defaultdict
from pathlib import Path

BOX = re.compile(
    r"^# box W=(-?\d+) H=(-?\d+) parity=(-?\d+) slo=(-?\d+) shi=(-?\d+) "
    r"pbox=(-?\d+) cells=(-?\d+) mult=(-?\d+) free:"
)
TRAILER = re.compile(r"^# perimeter_min lattice=(\S+) pmax=(\d+) rmax=(-?\d+) git=(\S+)")


def die(msg):
    sys.exit("perimeter_min_merge: " + msg)


def read_plan(path):
    """The frame list, as measured by the binary at RMAX=0."""
    frames = []
    for line in path.read_text().splitlines():
        m = BOX.match(line)
        if m:
            w, h, par, slo, shi, pbox, cells, mult = (int(g) for g in m.groups())
            frames.append(dict(W=w, H=h, parity=par, pbox=pbox, cells=cells, mult=mult))
    if not frames:
        die("plan %s has no '# box' lines" % path)
    return frames


def read_frame(path):
    """One --only run: its tally, and the box line it measured for itself."""
    tally, box, trailer, git = defaultdict(int), None, None, None
    for line in path.read_text().splitlines():
        m = BOX.match(line)
        if m:
            if box is not None:
                die("%s has more than one '# box' line" % path)
            w, h, par, slo, shi, pbox, cells, mult = (int(g) for g in m.groups())
            box = dict(W=w, H=h, parity=par, pbox=pbox, cells=cells, mult=mult)
            continue
        t = TRAILER.match(line)
        if t:
            trailer, git = t, t.group(4)
            continue
        if line.startswith("#") or not line.strip():
            continue
        n, p, c = (int(f) for f in line.split())
        tally[(n, p)] += c
    if box is None or trailer is None:
        die("%s is incomplete (box=%s trailer=%s) -- it must never have been "
            "published; the driver's completeness check is broken"
            % (path, box is not None, trailer is not None))
    return tally, box, git


def main():
    if len(sys.argv) != 5:
        die("usage: perimeter_min_merge.py FRAMEDIR LATTICE PMAX RMAX")
    d, lat, pmax, rmax = Path(sys.argv[1]), sys.argv[2], int(sys.argv[3]), int(sys.argv[4])

    frames = read_plan(d / "plan.txt")
    total = defaultdict(int)
    revs = set()

    for f in frames:
        path = d / ("f_%d_%d_%d.txt" % (f["W"], f["H"], f["parity"]))
        if not path.exists():
            die("frame %s missing -- the run is not finished, refusing to merge "
                "a partial census" % path.name)
        tally, box, git = read_frame(path)
        # The frame file must be the frame the plan asked for. A stale file from
        # a different geometry would otherwise merge in silently.
        for k in ("W", "H", "parity", "pbox", "cells"):
            if box[k] != f[k]:
                die("frame %s disagrees with the plan on %s (%s vs %s)"
                    % (path.name, k, box[k], f[k]))
        if box["mult"] != 1:
            die("frame %s reports mult=%d; --only is supposed to force mult=1, so "
                "the multiplicity below would double-count" % (path.name, box["mult"]))
        revs.add(git)
        for key, v in tally.items():
            total[key] += v * f["mult"]

    if len(revs) > 1:
        die("frames were produced by more than one build (%s); a census must come "
            "from one revision" % ", ".join(sorted(revs)))
    git = revs.pop()

    out = sys.stdout
    out.write("# perimeter_min lattice=%s pmax=%d rmax=%d git=%s\n" % (lat, pmax, rmax, git))
    out.write("# COMPLETE only for animals with perimeter <= %d AND area\n"
              "# deficit i = nmax(p) - n at most %d. Rows outside that domain\n"
              "# are present but partial -- do not read them as counts.\n" % (pmax, rmax))
    for (n, p) in sorted(total):
        out.write("%d %d %d\n" % (n, p, total[(n, p)]))


if __name__ == "__main__":
    main()
