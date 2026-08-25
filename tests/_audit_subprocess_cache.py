"""Memoize subprocess.run for the P-paper coverage audit.  Import to install.

WHY.  Profiling paper/verify_claims.py: 429 of its 431 s are nine
subprocess.run calls to external binaries -- 352 s of it regenerating the hole
tables from build/g2 -- and not one of them reads the .tex.  Perturbing a
literal in the paper cannot change what those binaries return, so the audit
re-ran 32 core-hours of identical work.  Cached, a run is ~2 s.

WHY IT IS SAFE.  The key is the full argv plus cwd, so a call the audit has not
seen before is a MISS and runs for real.  If a mutation ever did change which
subprocess is invoked -- the thing that would make caching wrong -- the key
changes with it and the cache steps aside.

WHY IT IS NOT IN THE VERIFIER.  A gate that reads yesterday's cached binary
output is not a gate.  This is imported only by the audit harness, and only
into the child interpreter it spawns.
"""
import hashlib
import os
import pickle
import subprocess
from pathlib import Path

CACHE = Path(os.environ["AUDIT_SUBPROC_CACHE"])
CACHE.mkdir(parents=True, exist_ok=True)
_real_run = subprocess.run


# TODO(2026-08-24, /simplify): this shim exists because verify_claims.py spends
# 352 of its 431 s regenerating hole tables from build/g2 on every run -- which
# is also why polyplets-report has an offline audit instead of a gate. Banking
# those tables as results/ files with receipts (this repo's own pattern) would
# delete this shim AND make polyplets gateable like technical-report. Large: it
# restructures verify_claims.
def _fingerprint(args):
    """(path, mtime_ns, size) for every argv token that names an existing file.

    The key used to be argv + kwargs + cwd, which is blind to the THING argv
    points at: rebuild build/g2 and every cached answer -- the green control's
    included -- silently keeps describing yesterday's binary, and the audit
    then reports guarded/unguarded against a world that no longer exists. The
    only invalidation was `rm -rf` on the cache dir, documented nowhere.

    RESIDUAL, stated rather than hidden: this covers what argv NAMES. A child
    that reads a data file it was not passed on the command line (runs/ output,
    a results/ table) is still not fingerprinted. That is why nothing in the
    wired suite sets AUDIT_SUBPROC_CACHE -- a gate that reads yesterday's
    output is not a gate -- and this shim stays an offline-audit tool.
    """
    out = []
    for a in args:
        seq = a if isinstance(a, (list, tuple)) else [a]
        for tok in seq:
            if not isinstance(tok, str):
                continue
            try:
                st = os.stat(tok)
            except OSError:
                continue
            out.append((tok, st.st_mtime_ns, st.st_size))
    return out


def _key(args, kwargs):
    payload = repr((args, sorted(kwargs.items()), os.getcwd(),
                    _fingerprint(args)))
    return hashlib.sha256(payload.encode()).hexdigest()


def run(*args, **kwargs):
    path = CACHE / (_key(args, kwargs) + ".pkl")
    if path.exists():
        return pickle.loads(path.read_bytes())
    result = _real_run(*args, **kwargs)
    try:
        blob = pickle.dumps(result)
    except Exception:
        return result          # unpicklable: never cached, always real
    tmp = path.with_suffix(".tmp")
    tmp.write_bytes(blob)
    tmp.replace(path)
    return result


subprocess.run = run
