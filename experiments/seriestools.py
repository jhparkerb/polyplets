"""Shared plumbing for the series probes in experiments/.

Deliberately narrow: reading a banked terms file, Aitken extrapolation, and
counting agreeing digits. These are file I/O and float bookkeeping, not
mathematics -- the probes in this directory are otherwise independent by
design, and anything that constitutes a re-derivation belongs in the probe
that derives it, not here.

mpmath's `mp` is a process-wide singleton, so agree_digits() reports against
whatever precision the calling probe set.
"""

from mpmath import mp


def read_terms(path):
    """Parse a banked series file into a list of a(n), in file order.

    One 'n a(n)' pair per line, blank lines and '#' comments skipped, the
    value being the trailing field -- the format every results/*_terms_*.txt
    uses. Mirrors tests/common.read_terms_file for the gate side."""
    vals = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                vals.append(int(line.split()[-1]))
    return vals


def aitken(seq):
    """One level of Aitken's delta-squared, leaving a fixed point unchanged."""
    out = []
    for i in range(len(seq) - 2):
        d1 = seq[i + 1] - seq[i]
        d2 = seq[i + 2] - 2 * seq[i + 1] + seq[i]
        out.append(seq[i] - d1 * d1 / d2 if d2 != 0 else seq[i])
    return out


def agree_digits(x, y):
    """Leading decimal digits on which x and y agree, capped at mp.dps."""
    if x == y:
        return mp.dps
    d = abs(x - y) / abs(x) if x != 0 else abs(y)
    return int(-mp.log10(d)) if d > 0 else mp.dps
