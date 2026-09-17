#!/usr/bin/env python3
"""
Build data/scholar.json — the publication list and the bibliometrics shown on the site.

Scopus is the spine:

  * Scopus Search  (view=COMPLETE)  -> every indexed document, with the full author
                                       list, venue, DOI and citation count.
  * Scopus Author Retrieval (METRICS) -> citations, h-index, co-author count.
  * Crossref                        -> metadata repair only: it knows that a paper in
                                       "Lecture Notes in Electrical Engineering" was
                                       presented at APPLEPIES, which Scopus does not say.
  * data/publications.manual.json   -> national conferences and workshops, which Scopus
                                       does not index. They appear in the list, flagged
                                       indexed=false, and are excluded from every
                                       bibliometric figure.

Needs SCOPUS_API_KEY in the environment. Fails loudly if Scopus is unreachable: the
previously committed data/scholar.json stays in place and the site keeps working.
"""

from __future__ import annotations

import json
import os
import pathlib
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
CACHE_PATH = DATA / ".crossref-cache.json"
OUT_PATH = DATA / "scholar.json"

USER_AGENT = "lucalazzaroni.github.io publication sync (+https://github.com/lucalazzaroni)"
SCOPUS = "https://api.elsevier.com/content"
TIMEOUT = 40

# Scopus subtype codes -> the categories the CV uses.
SUBTYPE = {
    "ar": "journal",     # article
    "re": "journal",     # review
    "le": "journal",     # letter
    "sh": "journal",     # short survey
    "no": "journal",     # note
    "ip": "journal",     # article in press
    "cp": "conference",  # conference paper
    "ch": "chapter",     # book chapter
    "bk": "book",
    "ed": "editorial",
    "er": "erratum",
}


# --------------------------------------------------------------------------- http


def get_json(url: str, headers: dict | None = None, retries: int = 3) -> dict | None:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, **(headers or {})})
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            if exc.code in (401, 403, 404):
                print(f"  ! HTTP {exc.code} {exc.reason}", file=sys.stderr)
                return None
            if attempt == retries - 1:
                print(f"  ! HTTP {exc.code} for {url}", file=sys.stderr)
                return None
        except Exception as exc:  # noqa: BLE001 - network flakiness is expected
            if attempt == retries - 1:
                print(f"  ! {exc} for {url}", file=sys.stderr)
                return None
        time.sleep(1.5 * (attempt + 1))
    return None


# --------------------------------------------------------------------------- helpers


def norm_title(title: str) -> str:
    """Aggressive normalisation, used only for deduplication."""
    t = unicodedata.normalize("NFKD", title or "").encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "", t.lower())


def clean_doi(doi: str | None) -> str | None:
    if not doi:
        return None
    return doi.lower().replace("https://doi.org/", "").strip()


def as_int(value, default=None):
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return default


def scopus_author_name(author: dict) -> str:
    """{'initials': 'L.', 'surname': 'Lazzaroni'} -> 'L. Lazzaroni'."""
    surname = (author.get("surname") or "").strip()
    initials = (author.get("initials") or "").strip()
    if surname and initials:
        return f"{initials} {surname}"
    return (author.get("authname") or surname or "").strip()


# --------------------------------------------------------------------------- crossref


def load_cache() -> dict:
    if CACHE_PATH.exists():
        try:
            return json.loads(CACHE_PATH.read_text())
        except json.JSONDecodeError:
            pass
    return {}


def crossref_lookup(doi: str, cache: dict, mailto: str) -> dict:
    """Return {title, container, series, event} for a DOI, cached between runs."""
    if doi in cache:
        return cache[doi]
    url = f"https://api.crossref.org/works/{urllib.parse.quote(doi)}?mailto={mailto}"
    msg = (get_json(url) or {}).get("message") or {}
    containers = [c for c in (msg.get("container-title") or []) if c]
    entry = {
        "title": (msg.get("title") or [None])[0],
        # For Springer proceedings the series is [0] and the conference itself is [1].
        "container": containers[-1] if containers else None,
        "series": containers[0] if len(containers) > 1 else None,
        "event": (msg.get("event") or {}).get("name"),
    }
    cache[doi] = entry
    time.sleep(0.05)
    return entry


# --------------------------------------------------------------------------- scopus


def scopus_headers() -> dict:
    key = os.environ.get("SCOPUS_API_KEY", "").strip()
    if not key:
        print(
            "SCOPUS_API_KEY is not set.\n"
            "  locally:  SCOPUS_API_KEY=… python3 scripts/fetch_scholar.py\n"
            "  in CI:    repository secret of the same name",
            file=sys.stderr,
        )
        raise SystemExit(2)
    headers = {"X-ELS-APIKey": key, "Accept": "application/json"}
    token = os.environ.get("SCOPUS_INST_TOKEN", "").strip()
    if token:
        headers["X-ELS-Insttoken"] = token
    return headers


def fetch_scopus_metrics(author_id: str, headers: dict) -> dict:
    payload = get_json(f"{SCOPUS}/author/author_id/{author_id}?view=METRICS", headers)
    try:
        entry = payload["author-retrieval-response"][0]
    except (KeyError, IndexError, TypeError):
        raise SystemExit("Scopus author metrics unavailable — leaving data/scholar.json untouched.")
    core = entry.get("coredata") or {}
    return {
        "author_id": author_id,
        "documents": as_int(core.get("document-count")),
        "citations": as_int(core.get("citation-count")),
        "cited_by": as_int(core.get("cited-by-count")),
        "h_index": as_int(entry.get("h-index")),
        "coauthors": as_int(entry.get("coauthor-count")),
    }


def fetch_scopus_documents(author_id: str, headers: dict) -> list[dict]:
    entries, start, total = [], 0, None
    while total is None or start < total:
        query = urllib.parse.urlencode(
            {"query": f"AU-ID({author_id})", "count": 25, "start": start, "view": "COMPLETE"}
        )
        page = get_json(f"{SCOPUS}/search/scopus?{query}", headers)
        if not page:
            raise SystemExit("Scopus search failed — leaving data/scholar.json untouched.")
        results = page["search-results"]
        total = as_int(results.get("opensearch:totalResults"), 0)
        batch = results.get("entry") or []
        if batch and batch[0].get("error"):
            break
        entries.extend(batch)
        start += 25
        time.sleep(0.15)
    return entries


def record_link(entry: dict, ref: str) -> str | None:
    for link in entry.get("link") or []:
        if link.get("@ref") == ref:
            return link.get("@href")
    return None


def build_publication(entry: dict, cfg: dict, cache: dict) -> dict:
    doi = clean_doi(entry.get("prism:doi"))
    cr = crossref_lookup(doi, cache, cfg["contact_email"]) if doi else {}

    subtype = (entry.get("subtype") or "").lower()
    ptype = SUBTYPE.get(subtype, "other")

    venue = entry.get("prism:publicationName")
    series = None
    if ptype == "conference":
        # Scopus files proceedings under the book series; Crossref knows the conference.
        proceedings = cr.get("event") or cr.get("container")
        if proceedings and proceedings != venue:
            series, venue = venue, proceedings
    elif cr.get("container") and not cr.get("series"):
        # Publisher spelling beats Scopus's: "…Systems II: Express Briefs", "Electronics".
        venue = cr["container"]

    override = (cfg.get("venue_overrides") or {}).get(doi or "", {})
    if override.get("venue"):
        venue = override["venue"]

    haystack = f"{venue or ''} {series or ''}".lower()
    if any(p in haystack for p in cfg.get("national_venue_patterns", [])):
        ptype = "national"

    authors_raw = entry.get("author") or []
    authors = [scopus_author_name(a) for a in authors_raw]
    me = [i for i, a in enumerate(authors_raw) if a.get("authid") == cfg["scopus_author_id"]]

    pages = entry.get("prism:pageRange")
    if pages:
        pages = pages.replace("-", "–")

    volume = entry.get("prism:volume")
    if volume and ptype != "journal":
        # Conference volumes come through as "1553 LNEE"; the series is already shown.
        volume = None

    return {
        "id": (entry.get("dc:identifier") or "").replace("SCOPUS_ID:", ""),
        "eid": entry.get("eid"),
        "title": (cr.get("title") or entry.get("dc:title") or "").strip(),
        "authors": authors,
        "me": me,
        "year": as_int((entry.get("prism:coverDate") or "")[:4]),
        "date": entry.get("prism:coverDate"),
        "type": ptype,
        "venue": venue,
        "series": series,
        "volume": volume,
        "issue": entry.get("prism:issueIdentifier") if ptype == "journal" else None,
        "pages": pages,
        "article_number": entry.get("article-number") if ptype == "journal" and not pages else None,
        "doi": doi,
        "url": f"https://doi.org/{doi}" if doi else record_link(entry, "scopus"),
        "scopus_url": record_link(entry, "scopus"),
        "open_access": bool(entry.get("openaccessFlag")),
        "citations": as_int(entry.get("citedby-count"), 0),
        "indexed": True,
        "source": "scopus",
    }


# --------------------------------------------------------------------------- main


def main() -> int:
    cfg = json.loads((DATA / "sources.json").read_text())
    author_id = cfg["scopus_author_id"]
    headers = scopus_headers()
    cache = load_cache()

    print(f"· Scopus: bibliometrics for author {author_id}")
    metrics = fetch_scopus_metrics(author_id, headers)
    print(f"  {metrics['documents']} documents · {metrics['citations']} citations · h={metrics['h_index']}")

    print("· Scopus: indexed documents")
    entries = fetch_scopus_documents(author_id, headers)
    print(f"  {len(entries)} records")

    excluded = set(cfg.get("exclude_scopus_ids") or [])
    print("· Crossref: metadata repair")
    publications = [
        pub
        for pub in (build_publication(e, cfg, cache) for e in entries)
        if pub["id"] not in excluded
    ]
    CACHE_PATH.write_text(json.dumps(cache, indent=1, ensure_ascii=False, sort_keys=True) + "\n")

    print("· Merging items Scopus does not index")
    seen_doi = {p["doi"] for p in publications if p["doi"]}
    seen_key = {(norm_title(p["title"]), p["year"]) for p in publications}
    for item in json.loads((DATA / "publications.manual.json").read_text()):
        doi = clean_doi(item.get("doi"))
        if (doi and doi in seen_doi) or (norm_title(item["title"]), item.get("year")) in seen_key:
            continue
        authors = item.get("authors", [])
        publications.append(
            {
                "id": "manual-" + norm_title(item["title"])[:40],
                "eid": None,
                "title": item["title"],
                "authors": authors,
                "me": [i for i, a in enumerate(authors) if "lazzaroni" in a.lower()],
                "year": item.get("year"),
                "date": item.get("date"),
                "type": item.get("type", "other"),
                "venue": item.get("venue"),
                "series": None,
                "volume": item.get("volume"),
                "issue": None,
                "pages": item.get("pages"),
                "article_number": None,
                "doi": doi,
                "url": item.get("url"),
                "scopus_url": None,
                "open_access": False,
                "citations": None,
                "indexed": False,
                "source": "manual",
            }
        )

    publications.sort(
        key=lambda p: (p.get("date") or f"{p.get('year') or 0}-00-00", p["title"]), reverse=True
    )

    counts: dict[str, int] = {}
    by_year: dict[str, int] = {}
    cites_by_year: dict[str, int] = {}
    for pub in publications:
        counts[pub["type"]] = counts.get(pub["type"], 0) + 1
        if pub.get("year"):
            key = str(pub["year"])
            by_year[key] = by_year.get(key, 0) + 1
            if pub["indexed"]:
                cites_by_year[key] = cites_by_year.get(key, 0) + (pub["citations"] or 0)
    counts["indexed"] = sum(1 for p in publications if p["indexed"])
    counts["unindexed"] = len(publications) - counts["indexed"]
    counts["total"] = len(publications)

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source": "scopus",
        "metrics": {
            "scopus": metrics,
            "counts": counts,
            "publications_by_year": dict(sorted(by_year.items())),
            "citations_by_publication_year": dict(sorted(cites_by_year.items())),
        },
        "profiles": {
            "scopus": f"https://www.scopus.com/authid/detail.uri?authorId={author_id}",
            "orcid": f"https://orcid.org/{cfg['orcid']}",
        },
        "publications": publications,
    }

    OUT_PATH.write_text(json.dumps(payload, indent=1, ensure_ascii=False) + "\n")
    print(f"→ {OUT_PATH.relative_to(ROOT)}: {counts}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
