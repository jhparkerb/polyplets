#!/usr/bin/env python3
"""Parallel M(n) = max enclosed empty area over all fixed n-cell polyplets.

Fans `build/g2 square8 N --maxhole` across K workers using the enumerator's own
--split subtree partition, then combines the per-worker outputs by elementwise
MAX (max combines that way -- counts would sum). This supersedes the slow,
RAM-heavy pure-Python sampling/amax_brute.py: the C++ Redelmeier+flood enumerator
is ~100x faster and O(n) memory (no dedup table), so n past 9 becomes tractable.

Background convention: --maxhole (4-connected background, the primary convention,
matches the paper and A389193) by default; pass --bg8 for --maxhole8 (8-connected).

Each worker traverses only the shared size<S prefix plus its OWN size-S subtrees
(non-owned subtrees set descend=false), so total work is ~full-tree/K -- near
linear speedup. Worker 0 additionally records all size<S animals.

Usage:
    python3 scripts/maxhole_split.py N [K] [--split-size S] [--bg8]
      N : maximum size (compute M(1..N))
      K : number of parallel workers (default min(16, cpu_count-2))
      S : split depth (default 8; needs a(S) >> K subtrees for balance)
Prints "n M(n)" for n=1..N and writes results/maxhole.txt.
Sanity: if N>=9 it checks M(1..9) == 0,0,0,1,1,2,3,5,6 and refuses to write on
mismatch (guards against a broken build or a split-combination bug).
"""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
G2 = os.path.join(ROOT, "build", "g2")
KNOWN = [0, 0, 0, 1, 1, 2, 3, 5, 6]            # M(1..9), exact

sys.path.insert(0, ROOT)
import obs  # shared observability/provenance runtime (docs/observability.md)


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    n = int(sys.argv[1])
    k = int(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2].isdigit() else \
        min(16, max(1, (os.cpu_count() or 4) - 2))
    s = 8
    if "--split-size" in sys.argv:
        s = int(sys.argv[sys.argv.index("--split-size") + 1])
    bg8 = "--bg8" in sys.argv
    flag = "--maxhole8" if bg8 else "--maxhole"
    if n < s:                                  # too small to split usefully
        k = 1
    s = min(s, max(1, n))

    job = f"maxhole{'8' if bg8 else ''}-N{n}"
    rep = obs.Reporter(job, script=__file__, total=k, workers=k, N=n,
                       split_size=s, flag=flag)
    # Checkpoint per --split worker: each worker's subtree result is banked the
    # instant it exits, so a kill re-launches only the workers that hadn't
    # finished. (A worker's stdout only materializes on clean exit, so a worker is
    # naturally all-or-nothing -- the right checkpoint unit.)
    ckpt = obs.Checkpoint(os.path.join(ROOT, "runs", "ckpt", f"{job}-k{k}-s{s}"),
                          {"N": n, "k": k, "s": s, "flag": flag})
    worker_out, todo = {}, []
    for idx in range(k):
        cached = ckpt.get_or_none(f"w{idx}")
        if cached is not None:
            worker_out[idx] = cached
        else:
            todo.append(idx)

    # launch only the un-banked workers concurrently (one core each; caller nices us)
    procs = {}
    for idx in todo:
        cmd = [G2, "square8", str(n), flag]
        if k > 1:
            cmd += ["--split", str(s), str(k), str(idx)]
        procs[idx] = subprocess.Popen(cmd, stdout=subprocess.PIPE, text=True)

    done = len(worker_out)
    for idx, p in procs.items():
        out, _ = p.communicate()
        if p.returncode != 0:
            rep.event("worker_failed", idx=idx, exit=p.returncode)
            sys.exit(f"worker {idx} failed (exit {p.returncode})")
        pairs = [[int(t[0]), int(t[1])]
                 for t in (ln.split() for ln in out.splitlines()) if len(t) == 2]
        ckpt.save(f"w{idx}", pairs)          # durable the instant the worker exits
        worker_out[idx] = pairs
        done += 1
        rep.beat(done=done)

    M = [0] * (n + 1)                        # combine all workers by elementwise max
    for idx in range(k):
        for i, m in worker_out[idx]:
            if m > M[i]:
                M[i] = m            # workers complete as their subtree finishes

    # sanity gate against the known prefix (4-connected-background convention)
    if not bg8 and n >= 9 and M[1:10] != KNOWN:
        rep.event("sanity_fail", got=str(M[1:10]), known=str(KNOWN))
        sys.exit(f"FAIL: M(1..9)={M[1:10]} != known {KNOWN} -- not writing")

    lines = [f"{i} {M[i]}" for i in range(1, n + 1)]
    body = "\n".join(lines)
    print(body)
    conv = "8-connected-background" if bg8 else "4-connected-background"
    out_path = os.path.join(ROOT, "results",
                            "maxhole8.txt" if bg8 else "maxhole.txt")
    with open(out_path, "w") as f:
        f.write(obs.file_header("maxhole_split", job, __file__))
        f.write(f"# M(n) = max enclosed empty area over fixed n-cell polyplets "
                f"({conv} convention).\n")
        f.write(f"# build/g2 square8 N --maxhole{'8' if bg8 else ''}, "
                f"{k}-way --split (S={s}), combined by elementwise max.\n")
        f.write(body + "\n")
    print(f"\n-> wrote {out_path}", file=sys.stderr)
    rep.done(result=f"M({n})={M[n]}", out=out_path, resumed=ckpt.n_resumed)
    ckpt.clear()   # result is durable; drop the per-worker scaffolding


if __name__ == "__main__":
    main()
