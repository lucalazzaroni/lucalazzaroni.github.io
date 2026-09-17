#!/usr/bin/env python3
"""
Sanity-check the hand-edited data files before they reach the site.

Catches the three mistakes that are actually easy to make when adding a CV entry:
a JSON syntax error, a bilingual field that only got one language, and a manual
publication missing a field the page needs.

    python3 scripts/check_data.py

Exits non-zero and lists every problem. Wired into CI, so a broken edit never
reaches the published page.
"""

from __future__ import annotations

import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
LANGS = {"en", "it"}

REQUIRED_TOP = [
    "person", "links", "summary", "positions", "education", "qualification",
    "projects", "teaching", "service", "talks", "awards", "memberships",
]

MANUAL_REQUIRED = ["title", "authors", "year", "type", "venue"]
MANUAL_TYPES = {"journal", "conference", "national", "workshop", "chapter", "book", "other"}

problems: list[str] = []


def fail(where: str, message: str) -> None:
    problems.append(f"{where}: {message}")


def walk(node, path: str = "") -> None:
    """The renderer takes either a plain string or a {en, it} map.

    So the only thing worth policing is a half-translated field: a map that mentions
    one language and forgets the other.
    """
    if isinstance(node, dict):
        if LANGS & set(node):
            if missing := LANGS - set(node):
                fail(path or "(root)", f"translated into {', '.join(sorted(LANGS & set(node)))} "
                                       f"but missing {', '.join(sorted(missing))}")
                return
            for lang in sorted(LANGS):
                if node[lang] in (None, "", []):
                    fail(f"{path}.{lang}", "is empty")
            return
        for key, value in node.items():
            walk(value, f"{path}.{key}" if path else key)
    elif isinstance(node, list):
        for i, item in enumerate(node):
            walk(item, f"{path}[{i}]")


def check_cv() -> None:
    try:
        cv = json.loads((DATA / "cv.json").read_text())
    except json.JSONDecodeError as exc:
        fail("cv.json", f"invalid JSON — {exc}")
        return

    for key in REQUIRED_TOP:
        if key not in cv:
            fail("cv.json", f"missing top-level key '{key}'")

    walk(cv)

    for i, link in enumerate(cv.get("links", [])):
        for key in ("label", "url", "handle"):
            if not link.get(key):
                fail(f"links[{i}]", f"missing '{key}'")

    for lang, path in (cv.get("person", {}).get("cv") or {}).items():
        if lang in LANGS and not (ROOT / path).exists():
            fail(f"person.cv.{lang}", f"{path} does not exist yet (run scripts/render_pdf.py)")


def check_manual() -> None:
    try:
        items = json.loads((DATA / "publications.manual.json").read_text())
    except json.JSONDecodeError as exc:
        fail("publications.manual.json", f"invalid JSON — {exc}")
        return

    seen = set()
    for i, item in enumerate(items):
        where = f"publications.manual.json[{i}]"
        for key in MANUAL_REQUIRED:
            if not item.get(key):
                fail(where, f"missing '{key}'")
        if item.get("type") not in MANUAL_TYPES:
            fail(where, f"type '{item.get('type')}' is not one of {sorted(MANUAL_TYPES)}")
        if not isinstance(item.get("authors"), list) or not item.get("authors"):
            fail(where, "'authors' must be a non-empty list")
        elif not any("lazzaroni" in a.lower() for a in item["authors"]):
            fail(where, "no author matches 'Lazzaroni' — the name will not be highlighted")
        key = (str(item.get("title", "")).lower().strip(), item.get("year"))
        if key in seen:
            fail(where, "duplicate title+year in this file")
        seen.add(key)


def main() -> int:
    check_cv()
    check_manual()

    if problems:
        print(f"{len(problems)} problem(s):\n", file=sys.stderr)
        for problem in problems:
            print(f"  · {problem}", file=sys.stderr)
        return 1

    print("data files look fine")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
