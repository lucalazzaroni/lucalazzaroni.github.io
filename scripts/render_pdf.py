#!/usr/bin/env python3
"""
Print the live page to PDF, once per language, into assets/.

The PDF *is* the page: same data files, same print stylesheet. There is no second
copy of the CV to keep in sync — update data/cv.json, and the next run reprints.

Uses headless Chrome directly, so there is nothing to install: Google Chrome on macOS,
google-chrome on the GitHub runner. Run it after scripts/fetch_scholar.py.
"""

from __future__ import annotations

import argparse
import functools
import http.server
import pathlib
import shutil
import socket
import socketserver
import subprocess
import sys
import tempfile
import threading
import time
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "assets"

CHROME_CANDIDATES = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "google-chrome",
    "google-chrome-stable",
    "chromium",
    "chromium-browser",
]

LANGS = {"en": "cv-luca-lazzaroni-en.pdf", "it": "cv-luca-lazzaroni-it.pdf"}


def find_chrome() -> str:
    for candidate in CHROME_CANDIDATES:
        if "/" in candidate:
            if pathlib.Path(candidate).exists():
                return candidate
        elif shutil.which(candidate):
            return shutil.which(candidate)
    sys.exit("No Chrome or Chromium binary found — cannot render the PDF.")


def free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):  # noqa: D102 - silence the request log
        pass


def serve(port: int) -> socketserver.TCPServer:
    handler = functools.partial(QuietHandler, directory=str(ROOT))
    httpd = socketserver.TCPServer(("127.0.0.1", port), handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    for _ in range(50):
        try:
            urllib.request.urlopen(f"http://127.0.0.1:{port}/index.html", timeout=1).read(1)
            return httpd
        except (urllib.error.URLError, ConnectionError):
            time.sleep(0.1)
    sys.exit("Local server did not come up.")


def render(chrome: str, url: str, destination: pathlib.Path, budget: int = 25) -> None:
    """Print one page to PDF.

    Chrome writes the file and then, on a machine with Google Updater installed, keeps
    a child alive so the process never exits. So: watch the file instead of the exit
    code, and stop Chrome once the PDF has stopped growing.
    """
    destination.unlink(missing_ok=True)
    with tempfile.TemporaryDirectory() as profile:
        proc = subprocess.Popen(
            [
                chrome,
                "--headless=new",
                "--disable-gpu",
                "--no-sandbox",
                "--no-first-run",
                "--no-default-browser-check",
                "--disable-background-networking",
                "--disable-component-update",
                "--hide-scrollbars",
                f"--user-data-dir={profile}",
                # Let the fonts load and the page assemble itself before printing.
                "--virtual-time-budget=15000",
                "--no-pdf-header-footer",
                f"--print-to-pdf={destination}",
                url,
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )

        deadline = time.time() + budget + 30
        last_size, stable_since = -1, None
        try:
            while time.time() < deadline:
                if proc.poll() is not None and destination.exists():
                    return
                if destination.exists():
                    size = destination.stat().st_size
                    if size == last_size and size > 0:
                        if stable_since is None:
                            stable_since = time.time()
                        elif time.time() - stable_since > 1.5:
                            return
                    else:
                        last_size, stable_since = size, None
                time.sleep(0.4)
            raise SystemExit(f"Chrome did not produce {destination.name} in time.")
        finally:
            if proc.poll() is None:
                proc.terminate()
                try:
                    proc.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    proc.kill()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--lang", choices=sorted(LANGS), action="append",
                        help="render only this language (repeatable)")
    args = parser.parse_args()
    wanted = args.lang or sorted(LANGS)

    chrome = find_chrome()
    port = free_port()
    httpd = serve(port)
    print(f"· serving {ROOT.name} on :{port}")
    print(f"· chrome  {chrome}")

    try:
        for lang in wanted:
            destination = OUT / LANGS[lang]
            render(chrome, f"http://127.0.0.1:{port}/?lang={lang}", destination)
            size = destination.stat().st_size
            if size < 20_000:
                sys.exit(f"{destination.name} came out at {size} bytes — the page probably did not render.")
            print(f"→ assets/{destination.name}  {size / 1024:.0f} kB")
    finally:
        httpd.shutdown()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
