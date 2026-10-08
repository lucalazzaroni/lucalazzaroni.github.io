#!/usr/bin/env python3
"""
Stamp the CSS and JS links in index.html with a content hash.

GitHub Pages serves assets with its own caching and offers no way to set headers,
so an edited stylesheet or script can keep serving stale to anyone who has already
loaded the page. A `?v=<hash of the file>` query sidesteps that: the URL changes
only when the file changes, so caches stay useful and never go stale.

Idempotent — run it as often as you like. Exits 0 and prints nothing when the
stamps are already correct.
"""

from __future__ import annotations

import hashlib
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGE = ROOT / "index.html"
ASSETS = ["assets/css/fonts.css", "assets/css/style.css", "assets/js/main.js"]


def digest(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:8]


def main() -> int:
    html = PAGE.read_text()
    original = html
    stamped = []

    for asset in ASSETS:
        file = ROOT / asset
        if not file.exists():
            sys.exit(f"{asset} is missing — cannot stamp index.html.")
        version = digest(file)
        # Match the path with or without an existing ?v=…
        pattern = re.compile(rf'({re.escape(asset)})(\?v=[0-9a-f]+)?(")')
        html, n = pattern.subn(rf'\1?v={version}\3', html)
        if not n:
            sys.exit(f"{asset} is not referenced in index.html — nothing to stamp.")
        stamped.append((asset, version))

    if html != original:
        PAGE.write_text(html)
        for asset, version in stamped:
            print(f"  {asset} -> ?v={version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
