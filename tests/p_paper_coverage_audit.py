#!/usr/bin/env python3
"""Which numbers in a P paper does its verifier actually read?  Shardable.

Same measurement tests/gate_p_paper_verifier.py makes, for a verifier too slow
to be a gate.  `paper/verify_claims.py` guards `polyplets-report.tex` with 428
checks and takes 431 s a run, so perturbing all 264 of the paper's numeric
literals is ~32 core-hours -- an audit, not a gate, and sharded across cores.

    python3 tests/p_paper_coverage_audit.py --paper polyplets \\
        --shard 0 --of 24 --out ~/var/p-coverage/shard00.json

Every shard re-runs the GREEN control first: if the unmutated copy does not
pass on this box, the shard exits 2 rather than reporting a wall of false
"guarded" results.  Merge with --merge.

Target: dalby only.  ayr has neither build/g2 nor the runs/sym3x directories
verify_claims reads, and a shard there would fail its green control.
"""
import argparse
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gate_p_paper_verifier import literals, sweep, context  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
PAPERS = {
    "technical": (ROOT / "paper" / "technical-report.tex",
                  ROOT / "paper" / "verify_technical_report.py"),
    "polyplets": (ROOT / "paper" / "polyplets-report.tex",
                  ROOT / "paper" / "verify_claims.py"),
}


def merge(paths, tex):
    src = tex.read_text()
    lits, unguarded = [], []
    for p in paths:
        d = json.loads(Path(p).read_text())
        lits += d["literals"]
        unguarded += d["unguarded"]
    lits, unguarded = sorted(set(lits)), sorted(set(unguarded))
    print(f"{tex.name}: {len(lits)} numeric literals, "
          f"{len(lits) - len(unguarded)} guarded, {len(unguarded)} unguarded")
    for lit in unguarded:
        print(f"  UNGUARDED {lit}: ...{context(src, lit)}...")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--paper", choices=sorted(PAPERS), default="polyplets")
    ap.add_argument("--shard", type=int, default=0)
    ap.add_argument("--of", type=int, default=1)
    ap.add_argument("--out")
    ap.add_argument("--merge", nargs="*")
    a = ap.parse_args()
    tex, verifier = PAPERS[a.paper]

    if a.merge is not None:
        return merge(a.merge, tex)

    src = tex.read_text()
    lits = literals(src)
    mine = [l for i, l in enumerate(lits) if i % a.of == a.shard]
    print(f"shard {a.shard}/{a.of}: {len(mine)} of {len(lits)} literals",
          flush=True)
    with tempfile.TemporaryDirectory() as d:
        unguarded = sweep(verifier, src, mine, d)
    out = {"paper": a.paper, "shard": a.shard, "of": a.of,
           "literals": mine, "unguarded": unguarded}
    if a.out:
        Path(a.out).write_text(json.dumps(out, indent=1))
    print(f"shard {a.shard}: {len(mine) - len(unguarded)} guarded, "
          f"{len(unguarded)} unguarded {unguarded}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
