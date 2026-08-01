#!/usr/bin/env python3
"""Forward citation crawl (OpenAlex) for the non-D-finiteness prior-art check.

papers/MISSING.md's standing next action: everything we have was found by
keyword or by following references BACKWARDS. This asks "who cites this?" for
the seeds that a colliding paper would have to cite -- above all
Bousquet-Melou & Rechnitzer 2002, whose Lemma 9 is the extraction step our
Theorem shares.

No API key needed. Usage:
    python3 experiments/citation_crawl.py [outfile]
Writes a triage dump: every citing work, newest first, flagged when its title
or abstract hits the vocabulary a collision would use.
"""

import json
import sys
import time
import urllib.parse
import urllib.request

MAILTO = "polyplets-citation-crawl"      # OpenAlex politeness pool

SEEDS = [
    ("BM-R 2002 (lattice animals and heaps of dimers)", "10.1016/s0012-365x(02)00352-7"),
    ("Haruspicy 2 (SAP anisotropic GF not D-finite)", None,
     "Haruspicy 2: The anisotropic generating function of self-avoiding polygons is not D-finite"),
    ("Haruspicy 3 (directed bond animals)", None,
     "Haruspicy 3: The anisotropic generating functions of directed bond-animals"),
    ("Chan & Rechnitzer 2018 (corner transfer matrix bounds)", None,
     "Upper bounds on the growth rates of independent sets"),
    ("Bevan-Brignall-Elvey Price-Pantone 2020 (Av(1324) bounds)", None,
     "A structural characterisation of Av(1324) and new bounds on its growth rate"),
]

# vocabulary a colliding paper would use
HOT = [
    "d-finite", "dfinite", "holonomic", "p-recursive", "p-recursiveness",
    "differentiably finite", "northcott", "house", "mahler", "algebraic number",
    "growth constant", "growth rate", "lattice animal", "polyomino", "polycube",
    "anisotropic", "heaps", "transfer matrix", "self-avoiding",
]


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": MAILTO})
    with urllib.request.urlopen(req, timeout=45) as r:
        return json.load(r)


def resolve(doi=None, title=None):
    if doi:
        return get(f"https://api.openalex.org/works/doi:{doi}")
    q = urllib.parse.quote(title)
    res = get(f"https://api.openalex.org/works?filter=title.search:{q}&per-page=5")
    return res["results"][0] if res["results"] else None


def abstract_of(w):
    inv = w.get("abstract_inverted_index")
    if not inv:
        return ""
    pos = {}
    for word, idxs in inv.items():
        for i in idxs:
            pos[i] = word
    return " ".join(pos[i] for i in sorted(pos))


def citing(work_id, cap=400):
    wid = work_id.rsplit("/", 1)[-1]
    out, cursor = [], "*"
    while len(out) < cap:
        url = (f"https://api.openalex.org/works?filter=cites:{wid}"
               f"&per-page=100&cursor={urllib.parse.quote(cursor)}")
        page = get(url)
        out.extend(page["results"])
        cursor = page["meta"].get("next_cursor")
        if not cursor or not page["results"]:
            break
        time.sleep(0.3)
    return out


def s2_citing(ref, cap=1000):
    """Second source: Semantic Scholar. OpenAlex undercounts recent + preprints.
    `ref` is a DOI, or 'arXiv:NNNN.NNNNN'."""
    key = ref if ref.lower().startswith("arxiv:") else f"DOI:{ref}"
    url = (f"https://api.semanticscholar.org/graph/v1/paper/{key}/citations"
           f"?fields=title,year,abstract,venue,externalIds&limit=1000")
    try:
        return get(url).get("data", [])
    except Exception as e:                      # rate limit / transient
        return [{"__error__": str(e)}]


def arxiv_search(query, maxr=60):
    """arXiv API full-text-ish search (title+abstract), newest first."""
    url = ("https://export.arxiv.org/api/query?search_query="
           + urllib.parse.quote(query)
           + f"&sortBy=submittedDate&sortOrder=descending&max_results={maxr}")
    req = urllib.request.Request(url, headers={"User-Agent": MAILTO})
    with urllib.request.urlopen(req, timeout=45) as r:
        xml = r.read().decode("utf-8", "replace")
    out = []
    for entry in xml.split("<entry>")[1:]:
        def field(tag):
            a = entry.find(f"<{tag}>")
            b = entry.find(f"</{tag}>")
            return " ".join(entry[a + len(tag) + 2:b].split()) if a >= 0 else ""
        out.append((field("published")[:10], field("title"), field("id"),
                    field("summary")))
    return out


def main():
    outfile = sys.argv[1] if len(sys.argv) > 1 else "citation_crawl.txt"
    lines = []

    def emit(s=""):
        print(s)
        lines.append(s)

    for seed in SEEDS:
        label, doi = seed[0], seed[1]
        title = seed[2] if len(seed) > 2 else None
        w = resolve(doi, title)
        if not w:
            emit(f"\n### {label}: NOT FOUND in OpenAlex")
            continue
        emit(f"\n{'=' * 78}\n### {label}")
        emit(f"    resolved: {w['display_name']} ({w.get('publication_year')}) "
             f"{w.get('doi')}")
        cites = citing(w["id"])
        emit(f"    cited by {w.get('cited_by_count')} (OpenAlex), fetched {len(cites)}")
        cites.sort(key=lambda c: -(c.get("publication_year") or 0))
        for c in cites:
            abst = abstract_of(c)
            blob = f"{c['display_name']} {abst}".lower()
            hits = [h for h in HOT if h in blob]
            mark = "**" if len(hits) >= 2 else "  "
            venue = ((c.get("primary_location") or {}).get("source") or {}).get(
                "display_name", "?")
            emit(f" {mark} {c.get('publication_year')}  {c['display_name'][:96]}")
            emit(f"        {venue[:70]} | {c.get('doi') or c['id']}")
            if hits:
                emit(f"        hits: {', '.join(hits[:8])}")
        time.sleep(0.3)

    # --- second source: Semantic Scholar (better on preprints and 2025+) ---
    S2_SEEDS = [
        ("BM-R 2002", "10.1016/S0012-365X(02)00352-7"),
        ("Haruspicy 2", "10.1016/j.jcta.2005.04.010"),
        ("Haruspicy 3", "10.1016/j.jcta.2005.09.010"),
        ("Chan-Rechnitzer 2018", "10.1016/j.laa.2018.06.008"),
        ("BBEP 2020 (Av(1324))", "10.1016/j.ejc.2020.103115"),
        ("Klazar 2003 (non-P-recursiveness of matchings)", "10.1016/S0196-8858(02)00529-2"),
        # the arithmetic-flavoured relatives: a colliding paper would cite these
        ("Bell-Hu-Satriano (height gap + D-finiteness)", "arXiv:2003.01255"),
        ("Bell-Gerhold-Klazar-Luca 2008 (non-holonomicity)", "arXiv:math/0605142"),
        # the upper-bound lineage our 9.3153 sits in
        ("Barequet-Shalah 2016 (improved polyomino upper bounds)",
         "10.1016/j.tcs.2021.02.020"),
    ]
    for label, doi in S2_SEEDS:
        emit(f"\n{'=' * 78}\n### [S2] {label}  ({doi})")
        cits = s2_citing(doi)
        if cits and "__error__" in cits[0]:
            emit(f"    ERROR: {cits[0]['__error__']}")
            time.sleep(3)
            continue
        emit(f"    cited by {len(cits)} (Semantic Scholar)")
        rows = [c.get("citingPaper", c) for c in cits]
        rows.sort(key=lambda c: -(c.get("year") or 0))
        for c in rows:
            blob = f"{c.get('title') or ''} {c.get('abstract') or ''}".lower()
            hits = [h for h in HOT if h in blob]
            mark = "**" if len(hits) >= 2 else "  "
            ext = c.get("externalIds") or {}
            ref = ext.get("DOI") or ext.get("ArXiv") or ""
            emit(f" {mark} {c.get('year')}  {(c.get('title') or '')[:96]}")
            emit(f"        {(c.get('venue') or '?')[:60]} | {ref}")
            if hits:
                emit(f"        hits: {', '.join(hits[:8])}")
        time.sleep(2)

    # --- third source: arXiv keyword sweeps, the shapes a collision would take ---
    QUERIES = [
        'all:"not D-finite" AND (all:"lattice animals" OR all:polyominoes)',
        'all:"D-finite" AND all:"anisotropic generating function"',
        'abs:"Northcott" AND (abs:"generating function" OR abs:"growth constant")',
        'all:"non-holonomic" AND all:"generating function" AND all:lattice',
        'abs:"not D-finite"',
        'abs:"P-recursive" AND abs:"combinatorial"',
        'abs:"growth constant" AND (abs:polyomino OR abs:"lattice animal")',
        'abs:"transcendental" AND abs:"generating function" AND abs:enumeration',
    ]
    for q in QUERIES:
        emit(f"\n{'=' * 78}\n### [arXiv] {q}")
        try:
            rows = arxiv_search(q)
        except Exception as e:
            emit(f"    ERROR: {e}")
            continue
        emit(f"    {len(rows)} hits, newest first")
        for date, title, aid, summ in rows[:25]:
            emit(f"    {date}  {title[:96]}")
            emit(f"        {aid}")
        time.sleep(3)

    with open(outfile, "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"\nwrote {outfile}")


if __name__ == "__main__":
    main()
