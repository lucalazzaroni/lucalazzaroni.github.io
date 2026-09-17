# lucalazzaroni.github.io

Personal academic site — <https://lucalazzaroni.github.io>

Static: no framework, no build step, no dependencies. `index.html` is an empty shell that
fills itself from two JSON files at load time. The downloadable PDF is the same page,
printed by headless Chrome — there is no second copy of the CV anywhere.

```
index.html                      markup shell (sections are empty containers)
assets/css/style.css            all styling — screen, light, dark, and print
assets/css/fonts.css            @font-face for the self-hosted IBM Plex
assets/fonts/                   IBM Plex woff2, latin + latin-ext
assets/js/main.js               rendering, i18n, filters, charts
assets/cv-luca-lazzaroni-*.pdf  GENERATED — printed from this page, one per language

data/cv.json                    ← EDIT THIS. Everything that isn't a publication
data/publications.manual.json   ← EDIT THIS. Papers Scopus doesn't index
data/sources.json               author IDs, venue fixes, exclusions
data/scholar.json               GENERATED — never edit
data/.crossref-cache.json       GENERATED — cache, keeps reruns fast

scripts/check_data.py           validates the two files above
scripts/fetch_scholar.py        Scopus → data/scholar.json
scripts/render_pdf.py           page → assets/*.pdf
Makefile                        check / sync / pdf / serve / publish
.github/workflows/build.yml     runs all three, weekly and on every relevant push
```

## Where the numbers come from

Everything bibliometric is **Scopus**, author ID `57220892898`:

| | |
|---|---|
| Scopus Search (`view=COMPLETE`) | the document list, with full author lists, venues, DOIs and per-paper citations |
| Scopus Author Retrieval (`view=METRICS`) | total citations, h-index, co-author count |
| Crossref | metadata repair only — it knows a paper in “Lecture Notes in Electrical Engineering” was presented at APPLEPIES, which Scopus does not say |
| `data/publications.manual.json` | national conferences and workshops Scopus does not index |

Manual items are listed with a **not in Scopus** marker and are excluded from every
indicator. That is why the publications header reads *“72 items · 66 in Scopus”*: the
second number is the one the metric cards are built on.

### The key, and where it works

An Elsevier API key is bound to the **subscribing institution's IP range**. This one
works from the UniGe network (and over the university VPN) and is refused with `401`
from anywhere else — including GitHub's runners. So today:

* `make sync`, run from the university network, is what actually refreshes the numbers.
* The weekly GitHub build still runs; the Scopus step is allowed to fail, the committed
  data is left alone, the PDFs are reprinted anyway, and the run carries a warning.
  Nothing goes stale silently: the page prints its own *synced* date next to the
  indicators.

To make the weekly build do the refresh on its own, ask Elsevier
(apisupport@elsevier.com) for an **institutional token** for the key — that is exactly
what it is for — and add it as the repository secret `SCOPUS_INST_TOKEN`. The script
already sends it when it is present; nothing else has to change.

The key itself lives in the macOS Keychain, not in this repository:

```bash
make key          # prompts for the key, stores it, nothing hits the disk in clear text
```

CI reads it from the repository secret `SCOPUS_API_KEY`.

If Scopus is unreachable the script exits `3`, explains why, and leaves
`data/scholar.json` untouched — the site keeps serving the last good data.

## Keeping it up to date

**A new journal or conference paper: nothing to write.** It arrives from Scopus on its
own, usually within a few weeks of publication — you only have to let it in:

```bash
make publish      # from the UniGe network or VPN
```

Once `SCOPUS_INST_TOKEN` exists, even that goes away and the Monday build picks it up by
itself (**Actions → Build → Run workflow** to do it on demand).

**Everything else** is one file. The most comfortable way to edit it is in the browser:
open the repository and press <kbd>.</kbd> — that opens github.dev, a full VS Code, no
clone, no terminal. Edit, then Source Control → commit. The site rebuilds itself, PDFs
included, in about two minutes.

### A new national conference or workshop paper

Append to `data/publications.manual.json`:

```json
{
  "title": "…",
  "authors": ["L. Lazzaroni", "F. Bellotti"],
  "year": 2026,
  "date": "2026-09-01",
  "type": "national",
  "venue": "57th Annual Meeting of the Italian Society of Electronics (SIE), …"
}
```

`type` is `journal`, `conference`, `national`, `workshop`, `chapter`, `book` or `other`.
Items here are deduplicated against Scopus by DOI and by title+year, so a national
abstract and the journal paper that later carries the same title both survive — which is
how the CV treats them too.

### A new course, project, award, talk…

`data/cv.json`. Every visible string is either plain text or a pair:

```json
"role": { "en": "Assistant Professor in Electronics",
          "it": "Ricercatore a tempo determinato in Elettronica" }
```

A plain string is used for both languages — fine for proper nouns (journal names, course
codes). If you write a pair, write both halves: `check_data.py` fails the build on a
half-translated field, so a missing translation can never reach the site.

### A wrong venue, or an entry you don't want

In `data/sources.json`:

* `venue_overrides` — keyed by DOI, wins over Scopus and Crossref.
* `exclude_scopus_ids` — Scopus IDs to drop from the list entirely. Scopus counts the
  *Preface* Luca wrote as APPLEPIES 2025 volume editor as one of his 66 documents, so it
  is listed too, under the `Editorial` filter. Put `105031702006` in here to hide it —
  the *Scopus documents* figure then drops to 65 and still matches the list.

### From a terminal instead

```bash
make check      # typos, half-translated fields, malformed manual entries
make sync       # Scopus → data/scholar.json, then reprint both PDFs
make serve      # preview on :4173 — add ?lang=it to pin the language
make publish    # sync, commit, push
```

`make sync` and `make publish` need the university network. `?lang=it` is also how the
PDF renderer asks for each edition. A plain `file://` open will not work: the page
fetches its JSON.

## Design notes

Two typefaces (IBM Plex Sans and Mono, self-hosted — the page makes no third-party
request), one accent, hairline rules, numbered sections.
Light and dark both clear WCAG AA on body and label text. The print stylesheet turns the
sidebar into a letterhead and drops the chrome — what headless Chrome prints is a proper
A4 CV, not a screenshot of a web page.
