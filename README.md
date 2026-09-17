# lucalazzaroni.github.io

Personal academic site — <https://lucalazzaroni.github.io>

Static: no framework, no build step, no dependencies. `index.html` is an empty shell that
fills itself from two JSON files at load time. The downloadable PDF is the same page,
printed by headless Chrome — there is no second copy of the CV anywhere.

```
index.html                      markup shell (sections are empty containers)
assets/css/style.css            all styling — screen, light, dark, and print
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

The key lives in the repository secret `SCOPUS_API_KEY`. Locally:

```bash
SCOPUS_API_KEY=… python3 scripts/fetch_scholar.py
```

If Scopus is unreachable the job fails loudly and leaves `data/scholar.json` alone — the
site keeps serving the last good data rather than silently degrading.

## Keeping it up to date

**A new journal or conference paper: do nothing.** It appears by itself once Scopus
indexes it, usually within a few weeks of publication. To pull it in sooner, go to
**Actions → Build → Run workflow**.

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
* `exclude_scopus_ids` — Scopus IDs to drop from the list entirely. The *Preface* to the
  APPLEPIES 2025 proceedings sits in here as `editorial`; add its ID to hide it.

### Before pushing (optional)

```bash
python3 scripts/check_data.py        # catches typos and half-translated fields
SCOPUS_API_KEY=… python3 scripts/fetch_scholar.py
python3 scripts/render_pdf.py        # needs Chrome; CI does this anyway
python3 -m http.server 4173          # then http://localhost:4173
```

`?lang=it` pins the language — that is how the PDF renderer asks for each edition.
A plain `file://` open will not work: the page fetches its JSON.

## Design notes

Two typefaces (IBM Plex Sans and Mono), one accent, hairline rules, numbered sections.
Light and dark both clear WCAG AA on body and label text. The print stylesheet turns the
sidebar into a letterhead and drops the chrome — what headless Chrome prints is a proper
A4 CV, not a screenshot of a web page.
