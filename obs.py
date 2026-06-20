"""Observability & provenance — the shared runtime for this repo's Python jobs.

One module, imported by every long-running script, so the rules in
`docs/observability.md` are implemented once and emitted identically everywhere:

  - every timestamp ISO-8601 with date *and* timezone offset (never bare clock);
  - a job announces its own START and DONE, so wall time is `done.t - start.t`
    from the log alone;
  - the denominator is stated up front, and each heartbeat carries a
    *self-computed* ETA from measured throughput;
  - one event per line, logfmt (`event=... key=value ...`), newline-terminated
    and flushed, never `\r`-overwritten;
  - provenance (git HEAD + dirty + content hash) captured at startup and
    **anchored to the script's own directory**, not `$CWD`.

Usage (job-like script):

    import os, sys
    ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, ROOT)
    import obs

    with obs.Reporter("h8k1", script=__file__, total=n_units, threads=nproc) as rep:
        for i, unit in enumerate(units):
            ... work ...
            rep.beat(done=i + 1)              # throttled; emits heartbeat+ETA
        rep.result = validated_count         # restated on the done line

And stamp any data/output file with the provenance banner:

    with open(out_path, "w") as f:
        f.write(obs.file_header("hole_modp_recover", "h8k1", __file__))
        f.write(payload)

Stdlib only — no third-party deps, runs identically on gympie (macOS) and ayr
(Linux); the one platform fork (ru_maxrss units) is handled in `_rss_mb`.
"""

import hashlib
import json
import os
import re
import resource
import socket
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone

# Heartbeat cadence: emit at most one heartbeat per this many wall-clock seconds,
# regardless of how tight the work loop is (principle 4 -- liveness and slope, not
# a flood). Override with POLY_HEARTBEAT_S for very long or very short jobs.
HEARTBEAT_S = float(os.environ.get("POLY_HEARTBEAT_S", "45"))


# --------------------------------------------------------------------------- #
# time
# --------------------------------------------------------------------------- #
def now_iso(dt=None):
    """ISO-8601 to the second, *with* local timezone offset: 2026-06-20T15:30:00+10:00.

    The whole point of the standard's principle 1 -- never a bare wall-clock time,
    never a duration without its anchor. `astimezone()` with no arg attaches the
    system's local offset so a reader never has to ask '15:30 which day, which zone?'
    """
    dt = dt or datetime.now().astimezone()
    return dt.isoformat(timespec="seconds")


# --------------------------------------------------------------------------- #
# provenance  (see docs/observability.md "Provenance")
# --------------------------------------------------------------------------- #
def _git(field, script_dir):
    """Run a git query anchored to the script's own dir, not $CWD.

    Anchoring matters: launch a gf/ script from ~/somewhere-else and a bare `git`
    reports whatever repo $CWD sits in. `-C script_dir` pins it to the source that
    is actually running.
    """
    try:
        r = subprocess.run(["git", "-C", script_dir] + field,
                           capture_output=True, text=True, timeout=5)
        return r
    except Exception:
        return None


def provenance(script_path):
    """Capture the running artifact's identity at startup.

    Returns a dict with:
      git   -- `rev-parse --short HEAD` (the PRIMARY anchor: what to check out to
               reproduce this number, including every sibling module/data file the
               script reads -- see the doc's "HEAD vs the commit a file is at").
      dirty -- 1 if the working tree differs from HEAD at all (untracked included).
               For interpreted code there is no compile gate -- you can edit a
               script and run it one second later -- so this flag is the only thing
               between "commit ed2ce1f" and "ed2ce1f plus an uncommitted change."
               Any dirty result is provisional until the tree is clean.
      hash  -- sha256[:12] of the script's bytes; survives when git can't answer.
      host  -- hostname, so cross-machine logs (gympie/ayr) are disambiguated.
    """
    sd = os.path.dirname(os.path.abspath(script_path))
    rev = _git(["rev-parse", "--short", "HEAD"], sd)
    git = rev.stdout.strip() if rev and rev.returncode == 0 else "unknown"
    status = _git(["status", "--porcelain"], sd)
    dirty = 1 if (status and status.returncode == 0 and status.stdout.strip()) else 0
    try:
        with open(os.path.abspath(script_path), "rb") as fh:
            h = hashlib.sha256(fh.read()).hexdigest()[:12]
    except OSError:
        h = "unknown"
    return {"git": git, "dirty": dirty, "hash": h, "host": socket.gethostname()}


def file_header(prog, job, script_path, md=False):
    """The two-line provenance banner stamped at the top of every *.out / data file.

    Human-first and coexists with `#`-comment data formats. Same provenance fields
    as the log stream -- this is the at-rest copy, the log stream the live one:

        # <prog> | commit ed2ce1f-dirty | <host> | 2026-06-20T15:30:00+10:00 | job=<job>
        # source: /abs/path/to/<script>

    `md=True` wraps it in an HTML comment instead, so a Markdown results file is
    stamped without the `#` rendering as a stray heading.
    """
    p = provenance(script_path)
    commit = p["git"] + ("-dirty" if p["dirty"] else "")
    l1 = f"{prog} | commit {commit} | {p['host']} | {now_iso()} | job={job}"
    l2 = f"source: {os.path.abspath(script_path)}"
    if md:
        return f"<!-- {l1}\n     {l2} -->\n"
    return f"# {l1}\n# {l2}\n"


# --------------------------------------------------------------------------- #
# cost metrics for the done line
# --------------------------------------------------------------------------- #
def _cpu_s():
    """CPU seconds, this process + waited-for children (subprocess/Pool workers).

    Most jobs here drive C++ engines via subprocess; RUSAGE_CHILDREN captures the
    work that actually burned the cores, which RUSAGE_SELF alone would miss."""
    s = resource.getrusage(resource.RUSAGE_SELF)
    c = resource.getrusage(resource.RUSAGE_CHILDREN)
    return s.ru_utime + s.ru_stime + c.ru_utime + c.ru_stime


def _rss_mb():
    """Peak resident set in MB, self or children, whichever is larger.

    The one cross-platform fork: ru_maxrss is *bytes* on macOS (gympie) and
    *kilobytes* on Linux (ayr)."""
    m = max(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss)
    return m / (1024 * 1024) if sys.platform == "darwin" else m / 1024


# --------------------------------------------------------------------------- #
# logfmt
# --------------------------------------------------------------------------- #
def _val(v):
    """Render one value: floats trimmed, strings with spaces quoted, rest bare."""
    if isinstance(v, float):
        v = f"{v:.4g}"
    s = str(v)
    return f'"{s}"' if (" " in s or s == "") else s


def _line(event, **kv):
    """One logfmt event line: `event=<event> k=v k=v ...`, leading event= first."""
    parts = [f"event={event}"] + [f"{k}={_val(v)}" for k, v in kv.items()
                                  if v is not None]
    return " ".join(parts)


# --------------------------------------------------------------------------- #
# Reporter
# --------------------------------------------------------------------------- #
class Reporter:
    """Emits the start / heartbeat / done event stream for one run.

    The first line written is `start`, the last is `done` (or `error`); wall time
    is recoverable as done.t - start.t from the log alone, with no stat and no
    "assume it began when the previous unit ended."

    Use as a context manager so DONE is announced even on an exception path:

        with Reporter("h8k1", script=__file__, total=N) as rep:
            ...
            rep.beat(done=i)
            rep.result = value
    """

    def __init__(self, job, *, script, total=None, stream=None, log=None, **extra):
        self.job = job
        self.total = total
        self.result = None
        self.prov = provenance(script)
        # default stream is stderr, keeping stdout clean for any data payload; pass
        # log="path" for a self-managed *.log file (line-buffered) per principle 8.
        if log is not None:
            self.stream = open(log, "a", buffering=1)
            self._own = True
        else:
            self.stream = stream or sys.stderr
            self._own = False
        self._t0 = time.monotonic()
        self._start_dt = datetime.now().astimezone()
        self._last_beat = self._t0
        self._done_emitted = False
        self._emit(_line("start", job=job, t=now_iso(self._start_dt),
                         git=self.prov["git"], dirty=self.prov["dirty"],
                         hash=self.prov["hash"], host=self.prov["host"],
                         total=total, **extra))

    # -- internals --------------------------------------------------------- #
    def _emit(self, text):
        self.stream.write(text + "\n")
        self.stream.flush()                       # principle 6: tail -f is truthful

    def _elapsed(self):
        return time.monotonic() - self._t0

    # -- public ------------------------------------------------------------ #
    def event(self, name, **kv):
        """Escape hatch for a program-specific event (e.g. event=checkpoint)."""
        self._emit(_line(name, job=self.job, t=now_iso(), **kv))

    def beat(self, done=None, force=False, **extra):
        """Heartbeat, throttled to HEARTBEAT_S wall-clock seconds.

        `done` is work completed so far (same units as `total`). When both are
        known the line carries fraction done, measured rate, and a self-computed
        ETA; when `total` is unknown it carries the monotonic counter and rate so a
        watcher can still extrapolate. Returns True if a line was actually emitted.
        """
        t = time.monotonic()
        if not force and (t - self._last_beat) < HEARTBEAT_S:
            return False
        self._last_beat = t
        el = self._elapsed()
        kv = {"elapsed_s": round(el, 1)}
        rate = (done / el) if (done and el > 0) else None
        if rate is not None:
            kv["rate"] = f"{rate:.4g}/s"
        if self.total and done is not None:
            kv["done"] = round(done / self.total, 4)
            if rate and done < self.total:
                eta = datetime.now().astimezone() + timedelta(
                    seconds=(self.total - done) / rate)
                kv["eta"] = now_iso(eta)
        elif done is not None:
            kv["count"] = done
        kv.update(extra)
        self._emit(_line("heartbeat", job=self.job, t=now_iso(), **kv))
        return True

    def done(self, result=None, **metrics):
        """The canonical ledger line: absolute start+end, wall, and cost metrics.

        Self-contained -- restates start so the entry can be pasted into a results
        ledger without re-deriving the wall from anything else."""
        if self._done_emitted:
            return
        self._done_emitted = True
        if result is None:
            result = self.result
        self._emit(_line("done", job=self.job, t=now_iso(),
                        start=now_iso(self._start_dt),
                        wall_s=round(self._elapsed(), 1),
                        cpu_s=round(_cpu_s(), 1),
                        peak_rss_mb=round(_rss_mb(), 1),
                        result=result, **metrics))
        if self._own:
            self.stream.close()

    # -- context manager --------------------------------------------------- #
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        if exc_type is not None:
            # announce a terminal error in-band so the log alone shows the run died
            # rather than going silent mid-stream.
            self._emit(_line("error", job=self.job, t=now_iso(),
                            wall_s=round(self._elapsed(), 1),
                            kind=exc_type.__name__, msg=str(exc)[:200]))
            if self._own:
                self.stream.close()
            return False
        self.done()
        return False


# --------------------------------------------------------------------------- #
# Checkpoint
# --------------------------------------------------------------------------- #
class Checkpoint:
    """A crash-safe, resumable per-unit result cache.

    A long job is a set of independent *units* (a height, a (height, prime)
    sweep, a worker shard). Each finished unit is written to its own file
    ATOMICALLY -- temp file, fsync, `os.replace` (an atomic rename) -- so a file's
    mere existence means "this unit completed and its bytes are whole." A kill can
    never leave a half-written unit; on the next run the job loads what's banked
    and recomputes only the gaps. This is the standard's principle 7 made durable:
    a crash costs one unit, not the whole multi-hour sweep.

    The directory is keyed by the run's defining parameters and a `params`
    meta-guard refuses a resume whose parameters differ (re-running with a smaller
    N, a different prime set, etc. would mix incompatible units into one answer).

    On by default; set POLY_CKPT=0 to disable (every `has` misses, every `save`
    is a no-op -- the job runs straight through with no on-disk cache).
    """

    def __init__(self, ckpt_dir, params=None):
        self.dir = ckpt_dir
        self.enabled = ckpt_dir is not None and os.environ.get("POLY_CKPT", "1") != "0"
        self.n_resumed = 0
        if self.enabled:
            os.makedirs(self.dir, exist_ok=True)
            self._guard(params or {})

    def _guard(self, params):
        # default=str so non-JSON params (e.g. a tuple of big primes) still serialize
        key = json.dumps(params, sort_keys=True, default=str)
        mp = os.path.join(self.dir, "_meta.json")
        if os.path.exists(mp):
            with open(mp) as f:
                old = f.read()
            if old != key:
                raise SystemExit(
                    f"checkpoint dir {self.dir} was built with different params; "
                    f"refuse to resume (would mix incompatible units).\n"
                    f"  cached: {old}\n  now:    {key}\n"
                    f"  -- delete the dir, or run with fresh args / POLY_CKPT=0")
        else:
            self._atomic("_meta.json", key)

    def _fname(self, unit):
        return re.sub(r"[^A-Za-z0-9_.=-]", "_", str(unit)) + ".json"

    def has(self, unit):
        return self.enabled and os.path.exists(os.path.join(self.dir, self._fname(unit)))

    def load(self, unit):
        with open(os.path.join(self.dir, self._fname(unit))) as f:
            return json.load(f)

    def save(self, unit, obj):
        if not self.enabled:
            return
        self._atomic(self._fname(unit), json.dumps(obj))

    def get_or_none(self, unit):
        """Cached object if this unit is banked (and bump the resumed counter),
        else None -- the caller computes and `save`s it."""
        if self.has(unit):
            self.n_resumed += 1
            return self.load(unit)
        return None

    def _atomic(self, name, text):
        p = os.path.join(self.dir, name)
        tmp = p + ".tmp"
        with open(tmp, "w") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())          # durable before the rename, so no torn unit
        os.replace(tmp, p)                # atomic: the unit appears whole or not at all

    def clear(self):
        """Drop the whole checkpoint dir -- call once the final output is safely
        assembled, so a clean rerun doesn't resume a finished job."""
        if self.enabled and os.path.isdir(self.dir):
            for n in os.listdir(self.dir):
                os.remove(os.path.join(self.dir, n))
            os.rmdir(self.dir)


# --------------------------------------------------------------------------- #
# self-test: `python obs.py` exercises the stream without any project compute.
# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    sys.stdout.write(file_header("obs-selftest", "demo", __file__))
    with Reporter("demo", script=__file__, total=3, threads=1,
                 stream=sys.stdout) as rep:
        for i in range(1, 4):
            rep.beat(done=i, force=True)
        rep.result = 151609203011580

    # checkpoint round-trip: miss -> save -> hit (with big ints, as recovery uses)
    import tempfile
    d = tempfile.mkdtemp(prefix="obs_ckpt_")
    ck = Checkpoint(d, {"N": 10, "primes": [2147482951, 1073741789]})
    assert ck.get_or_none("H8-p2147482951") is None
    ck.save("H8-p2147482951", {"0": [0, 0, 2187, 99999999999999999999]})
    assert ck.has("H8-p2147482951")
    assert ck.get_or_none("H8-p2147482951")["0"][3] == 99999999999999999999
    try:
        Checkpoint(d, {"N": 11})          # param drift must be refused
        raise AssertionError("meta-guard did not fire")
    except SystemExit:
        pass
    ck.clear()
    sys.stdout.write("event=selftest checkpoint=ok atomic=1 meta_guard=1\n")
