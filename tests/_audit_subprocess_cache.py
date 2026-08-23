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


def _key(args, kwargs):
    payload = repr((args, sorted(kwargs.items()), os.getcwd()))
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
