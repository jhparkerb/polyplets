#!/usr/bin/env python3
r"""Construction-density measurement for the LLM-tic pass, round 2.

Counts marker constructions per 1000 prose words in each L paper and in the
two P papers (jasonp's prose, the human control).  The tell is frequency, not
existence: an individual contrast can be load-bearing while the aggregate
density is still a fingerprint.  Run from the repo root:

    python3 docs/reviews/llm-tics/density.py

Prose extraction is deliberately crude but identical across all files, so the
comparison is fair even where the absolute numbers are approximate: comments,
math ($...$, \[...\], equation-like environments), and LaTeX commands are
stripped before counting.
"""

import re
import sys
from pathlib import Path

PAPER = Path(__file__).resolve().parents[3] / "paper"

# Enumerated, not frozen.  The 2026-08-23 contraction merged four papers into
# their partners and withdrew a fifth, and a hardcoded list turns that into a
# FileNotFoundError rather than a measurement over the corpus that exists.
# Sorted by the number in the stem so L10 would follow L9 rather than L1.
L_PAPERS = [
    f.name
    for f in sorted(
        PAPER.glob("L[0-9]*.tex"),
        key=lambda f: int(f.name.split("-")[0][1:]),
    )
]
CONTROLS = ["technical-report.tex", "polyplets-report.tex"]

MATH_ENVS = r"(equation|align|gather|multline|array|eqnarray|displaymath)\*?"


def prose(path: Path) -> str:
    src = path.read_text()
    src = re.sub(r"(?<!\\)%.*", "", src)                          # comments
    src = re.sub(r"\\begin\{" + MATH_ENVS + r"\}.*?\\end\{" + MATH_ENVS + r"\}",
                 " M ", src, flags=re.S)                          # display math
    src = re.sub(r"\\\[.*?\\\]", " M ", src, flags=re.S)
    src = re.sub(r"\$\$.*?\$\$", " M ", src, flags=re.S)
    src = re.sub(r"\$[^$]*\$", " M ", src)                        # inline math
    src = re.sub(r"\\[a-zA-Z@]+\s*(\[[^\]]*\])?(\{[^{}]*\})*", " ", src)  # commands
    src = re.sub(r"[{}~]", " ", src)
    return src


# name -> compiled regex, counted per occurrence in the prose stream.
MARKERS = {
    # A. contrastive negation / negative parallelism
    "contrast-neg": re.compile(
        r"\bnot\s+(just|merely|only|simply)\b"
        r"|\bis\s+not\s+a[n]?\b[^.;]{0,60}[;,.]\s*[Ii]t\s+is\b"
        r"|,\s*not\s+[a-z][^.;,]{0,40}[.;,]"
        r"|\bno\s+\w+,\s*no\s+\w+", re.I),
    # C. cleft / copula avoidance
    "cleft": re.compile(
        r"\bwhat\s+(it|this|that|the)\b[^.;]{0,50}\b(is|does|makes?)\b"
        r"|\bis\s+what\s+\w+"
        r"|\b(is|are)\s+the\s+(fact|thing|reason|feature)\s+that\b", re.I),
    "serves-as": re.compile(r"\b(serves?|stands?|acts?)\s+as\b|\bmarks\s+the\b", re.I),
    # F. paired-dash aside (LaTeX ---)
    "dash-aside": re.compile(r"---[^-]{3,80}---"),
    # E/H. editorializing and scaffolding
    "scaffold": re.compile(
        r"\bworth\s+noting\b|\bin\s+essence\b|\btaken\s+together\b"
        r"|\bwhat\s+is\s+really\b|\bimportantly\b|\binterestingly\b"
        r"|\bcrucially\b|\bnotably\b", re.I),
    # rhythm: sentence-initial short declarative "X is Y." <= 5 words
    "punch": re.compile(r"(?:^|[.!?]\s+)([A-Z][a-z]+(?:\s+\w+){0,3}\s+(?:is|are|was|stays?|holds?|fails?|survives?|goes)\b[^.!?]{0,25}[.!?])"),
}


def sentences(text: str):
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if len(s.strip()) > 2]


def measure(path: Path):
    p = prose(path)
    words = len(p.split())
    row = {"words": words}
    for name, rx in MARKERS.items():
        row[name] = len(rx.findall(p))
    sl = [len(s.split()) for s in sentences(p)]
    row["sents"] = len(sl)
    row["mean-len"] = sum(sl) / len(sl) if sl else 0
    return row


def main():
    names = list(MARKERS)
    hdr = f"{'paper':28s} {'words':>6s} " + " ".join(f"{n:>13s}" for n in names) + f" {'mean-len':>8s}"
    print(hdr)
    print("-" * len(hdr))
    totals = {}
    for group, files in (("L", L_PAPERS), ("P-control", CONTROLS)):
        gw = 0
        gc = {n: 0 for n in names}
        for f in files:
            r = measure(PAPER / f)
            gw += r["words"]
            for n in names:
                gc[n] += r[n]
            rates = " ".join(f"{1000*r[n]/r['words']:>8.2f}/1k" for n in names)
            print(f"{f:28s} {r['words']:>6d} {rates} {r['mean-len']:>8.1f}")
        totals[group] = (gw, gc)
        rates = " ".join(f"{1000*gc[n]/gw:>8.2f}/1k" for n in names)
        print(f"{'== ' + group + ' overall':28s} {gw:>6d} {rates}")
        print()
    lw, lc = totals["L"]
    pw, pc = totals["P-control"]
    print("ratio L : P-control per construction (1.0 = human-like density)")
    for n in names:
        lr = 1000 * lc[n] / lw
        pr = 1000 * pc[n] / pw
        print(f"  {n:13s} {lr:6.2f} vs {pr:6.2f}  ratio {'inf' if pr == 0 else f'{lr/pr:5.2f}'}")


# --- published-corpus mode: python3 density.py --corpus [dir] -----------------
# Extracts text from every PDF in literature/ (pdftotext) and reports the same
# marker rates, so the control band comes from published, journal-edited
# English rather than two in-house files.  PDF extraction turns math into
# token noise, which inflates word counts and so *deflates* rates slightly;
# the band is therefore generous, and the L-paper targets should sit inside
# it, not at its edge.  Non-English papers in the corpus show near-zero rates
# and are excluded by the English-stopword filter below.

def corpus_mode(d):
    import subprocess, statistics, tempfile
    rows = []
    for pdf in sorted(Path(d).glob("*.pdf")):
        with tempfile.NamedTemporaryFile(suffix=".txt") as t:
            r = subprocess.run(["pdftotext", "-q", str(pdf), t.name])
            if r.returncode != 0:
                continue
            text = Path(t.name).read_text(errors="replace")
        words = text.split()
        if len(words) < 1500:
            continue
        stop = sum(1 for w in words if w.lower() in ("the", "of", "and", "is", "that", "for"))
        if stop / len(words) < 0.08:      # non-English or garbled extraction
            continue
        text = re.sub(r"—|(?<=\w)--(?=\w)| -- ", "---", text)  # normalize dashes
        n = len(words)
        row = {"name": pdf.name[:40], "words": n}
        for name, rx in MARKERS.items():
            row[name] = 1000 * len(rx.findall(text)) / n
        rows.append(row)
    names = list(MARKERS)
    print(f"corpus: {len(rows)} English papers, {sum(r['words'] for r in rows)} words")
    for stat, fn in (("median", statistics.median),
                     ("p75", lambda v: statistics.quantiles(v, n=4)[2]),
                     ("p90", lambda v: statistics.quantiles(v, n=10)[8]),
                     ("max", max)):
        vals = " ".join(f"{fn([r[m] for r in rows]):>8.2f}/1k" for m in names)
        print(f"{stat:>10s}  {vals}")
    print("   markers:", "  ".join(names))


if __name__ == "__main__":
    if "--corpus" in sys.argv:
        i = sys.argv.index("--corpus")
        corpus_mode(sys.argv[i + 1] if len(sys.argv) > i + 1 else "papers")
        sys.exit(0)
    sys.exit(main())
