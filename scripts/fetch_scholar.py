#!/usr/bin/env python3
"""
Build data/scholar.json — the publication list and the bibliometrics shown on the site.

Sources, in order of trust:

  1. Scopus  (api.elsevier.com)  — bibliometrics only, and only when SCOPUS_API_KEY is set.
     Scopus is the number the CV quotes, but its API needs a key, so it is optional.
  2. OpenAlex (api.openalex.org) — the publication list plus a full set of metrics.
     No key, no rate limit worth worrying about, resolves the author by ORCID.
  3. Crossref (api.crossref.org) — used only to repair metadata: publisher-cased titles and
     the real proceedings name behind "Lecture Notes in Electrical Engineering".
  4. data/publications.manual.json — items the indexes do not carry (national conferences,
     workshop papers). Merged in, deduplicated on DOI and on normalised title.

Run it with no arguments. Nothing here needs network credentials unless you want Scopus.
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
TIMEOUT = 30


# --------------------------------------------------------------------------- http


def get_json(url: str, headers: dict | None = None, retries: int = 3) -> dict | None:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, **(headers or {})})
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            if exc.code in (404, 401, 403):
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


def initialise(full_name: str) -> str:
    """'Francesco Bellotti' -> 'F. Bellotti'. Leaves already-initialised names alone."""
    parts = [p for p in re.split(r"\s+", (full_name or "").strip()) if p]
    if len(parts) < 2:
        return full_name
    *given, family = parts
    inits = []
    for g in given:
        if g.endswith("."):
            inits.append(g)
        elif "-" in g:
            inits.append("-".join(f"{piece[0]}." for piece in g.split("-") if piece))
        else:
            inits.append(f"{g[0]}.")
    return " ".join(inits + [family])


def is_me(name: str, cfg: dict) -> bool:
    low = unicodedata.normalize("NFKD", name.lower()).encode("ascii", "ignore").decode()
    return any(surname in low for surname in cfg["author_match"])


# --------------------------------------------------------------------------- crossref


def load_cache() -> dict:
    if CACHE_PATH.exists():
        try:
            return json.loads(CACHE_PATH.read_text())
        except json.JSONDecodeError:
            pass
    return {}


def crossref_lookup(doi: str, cache: dict, mailto: str) -> dict:
    """Return {title, container, event} for a DOI, cached on disk between runs."""
    if doi in cache:
        return cache[doi]
    url = f"https://api.crossref.org/works/{urllib.parse.quote(doi)}?mailto={mailto}"
    payload = get_json(url) or {}
    msg = payload.get("message") or {}
    containers = [c for c in (msg.get("container-title") or []) if c]
    entry = {
        "title": (msg.get("title") or [None])[0],
        # For Springer proceedings the series is [0] and the actual conference is [1].
        "container": containers[-1] if containers else None,
        "series": containers[0] if len(containers) > 1 else None,
        "event": ((msg.get("event") or {}).get("name")),
        "type": msg.get("type"),
    }
    cache[doi] = entry
    time.sleep(0.05)
    return entry


# --------------------------------------------------------------------------- openalex


def fetch_openalex_author(cfg: dict) -> dict | None:
    mailto = cfg["contact_email"]
    for ident in (cfg.get("openalex_author_id"), f"https://orcid.org/{cfg['orcid']}"):
        if not ident:
            continue
        data = get_json(f"https://api.openalex.org/authors/{ident}?mailto={mailto}")
        if data:
            return data
    return None


def fetch_openalex_works(author_id: str, mailto: str) -> list[dict]:
    works, cursor = [], "*"
    while cursor:
        url = (
            "https://api.openalex.org/works?"
            + urllib.parse.urlencode(
                {
                    "filter": f"author.id:{author_id}",
                    "per-page": 200,
                    "cursor": cursor,
                    "mailto": mailto,
                }
            )
        )
        page = get_json(url)
        if not page:
            break
        works.extend(page.get("results", []))
        cursor = (page.get("meta") or {}).get("next_cursor")
    return works


def classify(work: dict, crossref: dict, cfg: dict, venue: str | None) -> str:
    """Map an OpenAlex record onto the CV's own categories."""
    haystack = (venue or "").lower()
    for pattern in cfg.get("national_venue_patterns", []):
        if pattern in haystack:
            return "national"

    wtype = (work.get("type") or "").lower()
    source = ((work.get("primary_location") or {}).get("source") or {})
    stype = (source.get("type") or "").lower()
    if wtype == "preprint" or stype == "repository":
        return "preprint"
    if stype == "journal" and wtype in {"article", "review", "letter", "editorial", "erratum"}:
        return "journal"
    if wtype in {"book-chapter", "proceedings-article", "conference-paper"} or stype in {
        "conference",
        "book series",
        "book",
        "proceedings",
    }:
        return "conference"
    if stype == "journal":
        return "journal"
    return "other"


def build_publication(work: dict, cfg: dict, cache: dict) -> dict:
    doi = clean_doi(work.get("doi"))
    cr = crossref_lookup(doi, cache, cfg["contact_email"]) if doi else {}

    source = ((work.get("primary_location") or {}).get("source") or {})
    venue = cr.get("event") or cr.get("container") or source.get("display_name")
    series = cr.get("series") if cr.get("series") != venue else None

    override = (cfg.get("venue_overrides") or {}).get(doi or "", {})
    if override.get("venue"):
        venue = override["venue"]

    biblio = work.get("biblio") or {}
    pages = None
    if biblio.get("first_page"):
        pages = biblio["first_page"]
        if biblio.get("last_page") and biblio["last_page"] != biblio["first_page"]:
            pages += f"–{biblio['last_page']}"

    authors = [initialise(a["author"]["display_name"]) for a in work.get("authorships", [])]
    ptype = classify(work, cr, cfg, venue)

    return {
        "id": (work.get("id") or "").rsplit("/", 1)[-1],
        "title": (cr.get("title") or work.get("title") or "").strip(),
        "authors": authors,
        "me": [i for i, a in enumerate(authors) if is_me(a, cfg)],
        "year": work.get("publication_year"),
        "date": work.get("publication_date"),
        "type": ptype,
        "venue": venue,
        "series": series,
        "volume": biblio.get("volume") or None,
        "issue": biblio.get("issue") or None,
        "pages": pages,
        "doi": doi,
        "url": f"https://doi.org/{doi}" if doi else (work.get("id") or None),
        "oa_url": (work.get("open_access") or {}).get("oa_url"),
        "citations": work.get("cited_by_count", 0),
        "source": "openalex",
    }


# --------------------------------------------------------------------------- scopus


def fetch_scopus(cfg: dict) -> dict | None:
    key = os.environ.get("SCOPUS_API_KEY", "").strip()
    author_id = cfg.get("scopus_author_id")
    if not key or not author_id:
        return None

    headers = {"X-ELS-APIKey": key, "Accept": "application/json"}
    inst_token = os.environ.get("SCOPUS_INST_TOKEN", "").strip()
    if inst_token:
        headers["X-ELS-Insttoken"] = inst_token

    url = f"https://api.elsevier.com/content/author/author_id/{author_id}?view=METRICS"
    payload = get_json(url, headers=headers)
    if not payload:
        print("  ! Scopus call failed — falling back to OpenAlex metrics", file=sys.stderr)
        return None

    try:
        entry = payload["author-retrieval-response"][0]
    except (KeyError, IndexError, TypeError):
        return None

    coredata = entry.get("coredata") or {}

    def as_int(value):
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    return {
        "documents": as_int(coredata.get("document-count")),
        "citations": as_int(coredata.get("citation-count")),
        "cited_by": as_int(coredata.get("cited-by-count")),
        "h_index": as_int(entry.get("h-index")),
        "author_id": author_id,
    }


# --------------------------------------------------------------------------- main


def main() -> int:
    cfg = json.loads((DATA / "sources.json").read_text())
    mailto = cfg["contact_email"]
    cache = load_cache()

    print("· OpenAlex: author profile")
    author = fetch_openalex_author(cfg)
    if not author:
        print("Could not resolve the OpenAlex author — aborting.", file=sys.stderr)
        return 1

    author_id = (author.get("id") or "").rsplit("/", 1)[-1]
    stats = author.get("summary_stats") or {}
    openalex_metrics = {
        "works": author.get("works_count"),
        "citations": author.get("cited_by_count"),
        "h_index": stats.get("h_index"),
        "i10_index": stats.get("i10_index"),
        "author_id": author_id,
    }

    print(f"· OpenAlex: works for {author_id}")
    works = fetch_openalex_works(author_id, mailto)
    print(f"  {len(works)} records")

    print("· Crossref: metadata repair")
    publications = [build_publication(w, cfg, cache) for w in works]
    CACHE_PATH.write_text(json.dumps(cache, indent=1, ensure_ascii=False, sort_keys=True) + "\n")

    print("· Merging manual entries")
    seen_doi = {p["doi"] for p in publications if p["doi"]}
    seen_key = {(norm_title(p["title"]), p.get("year")) for p in publications}
    manual = json.loads((DATA / "publications.manual.json").read_text())
    for item in manual:
        doi = clean_doi(item.get("doi"))
        if (doi and doi in seen_doi) or (norm_title(item["title"]), item.get("year")) in seen_key:
            continue
        authors = item.get("authors", [])
        publications.append(
            {
                "id": "manual-" + norm_title(item["title"])[:40],
                "title": item["title"],
                "authors": authors,
                "me": [i for i, a in enumerate(authors) if is_me(a, cfg)],
                "year": item.get("year"),
                "date": item.get("date"),
                "type": item.get("type", "other"),
                "venue": item.get("venue"),
                "series": None,
                "volume": item.get("volume"),
                "issue": None,
                "pages": item.get("pages"),
                "doi": doi,
                "url": item.get("url"),
                "oa_url": None,
                "citations": item.get("citations", 0),
                "source": "manual",
            }
        )

    publications.sort(key=lambda p: (p.get("date") or f"{p.get('year', 0)}-00-00", p["title"]), reverse=True)

    counts: dict[str, int] = {}
    by_year: dict[str, int] = {}
    for pub in publications:
        counts[pub["type"]] = counts.get(pub["type"], 0) + 1
        if pub.get("year"):
            key = str(pub["year"])
            by_year[key] = by_year.get(key, 0) + 1
    counts["total"] = len(publications)

    citations_by_year = {
        str(row["year"]): row.get("cited_by_count", 0)
        for row in (author.get("counts_by_year") or [])
    }

    print("· Scopus: bibliometrics")
    scopus = fetch_scopus(cfg)
    print("  " + ("ok" if scopus else "skipped (no SCOPUS_API_KEY)"))

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "metrics": {
            "primary": "scopus" if scopus else "openalex",
            "scopus": scopus,
            "openalex": openalex_metrics,
            "counts": counts,
            "publications_by_year": dict(sorted(by_year.items())),
            "citations_by_year": dict(sorted(citations_by_year.items())),
        },
        "profiles": {
            "orcid": f"https://orcid.org/{cfg['orcid']}",
            "scopus": f"https://www.scopus.com/authid/detail.uri?authorId={cfg['scopus_author_id']}",
            "openalex": f"https://openalex.org/{author_id}",
        },
        "publications": publications,
    }

    OUT_PATH.write_text(json.dumps(payload, indent=1, ensure_ascii=False) + "\n")
    print(f"→ {OUT_PATH.relative_to(ROOT)}: {counts['total']} publications, {counts}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
