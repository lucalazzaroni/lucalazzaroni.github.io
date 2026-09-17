# lucalazzaroni.github.io

Personal academic site — <https://lucalazzaroni.github.io>

Static: no framework, no build step, no dependencies. The page is `index.html`; it
assembles itself at load time from two JSON files.

```
index.html                      markup shell (sections are empty containers)
assets/css/style.css            all styling, light + dark
assets/js/main.js               rendering, i18n, filters, charts
assets/img/                     portrait, favicon
assets/Luca_Lazzaroni_CV_EN.pdf full CV

data/cv.json                    ← EDIT THIS. Static CV content, EN + IT
data/publications.manual.json   ← EDIT THIS. Papers the indexes don't carry
data/sources.json               author identifiers and venue fixes
data/scholar.json               GENERATED — do not edit by hand
data/.crossref-cache.json       GENERATED — cache, keeps reruns fast

scripts/fetch_scholar.py        the sync job
.github/workflows/sync-publications.yml
```

## Editing the CV

Everything that isn't a publication lives in **`data/cv.json`**. Every visible string is
an object with both languages:

```json
"role": { "en": "Assistant Professor in Electronics",
          "it": "Ricercatore a tempo determinato in Elettronica" }
```

Edit, commit, push. The site updates as soon as GitHub Pages redeploys (about a minute).
There is nothing to rebuild.

## How publications stay current

`scripts/fetch_scholar.py` runs **every Monday** (and on demand from the Actions tab),
and rewrites `data/scholar.json`:

| Source | What it provides | Credentials |
|---|---|---|
| **OpenAlex** | the publication list, citation counts, h-index, i10-index, per-year series — resolved from ORCID `0000-0001-8092-5473` | none |
| **Crossref** | metadata repair: publisher-cased titles, and the real conference name behind “Lecture Notes in Electrical Engineering” | none |
| **Scopus** | h-index and citation count, if a key is configured | API key |
| `publications.manual.json` | national-conference and workshop items the indexes miss | — |

Anything you publish shows up automatically once OpenAlex indexes it (typically days
after the DOI is registered). Nothing needs to be typed twice.

### Adding a paper the indexes don't have

Append an entry to `data/publications.manual.json`:

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

`type` is one of `journal`, `conference`, `national`, `workshop`, `preprint`, `other`.
Entries are deduplicated against the automatic ones by DOI, and by title+year — so a
national abstract and the later journal paper with the same title both survive, which
is what the CV does too.

### Fixing a wrong venue

Indexes occasionally mangle a venue name. Add the DOI to `venue_overrides` in
`data/sources.json`; it wins over everything else.

### Turning on Scopus

The site currently shows OpenAlex figures, which run slightly below Scopus (different
coverage of Springer proceedings, mainly). To show the Scopus numbers instead:

1. Register at <https://dev.elsevier.com> and create an API key.
2. Repository → Settings → Secrets and variables → Actions → **New repository secret**,
   named `SCOPUS_API_KEY`.
3. If your institution issued an institutional token, add it as `SCOPUS_INST_TOKEN` too.
4. Actions → *Sync publications* → **Run workflow**.

The metrics block and its footnote switch over on their own. If the key is missing or
Elsevier refuses the request, the job logs it and falls back to OpenAlex — the site
never breaks. Note that Elsevier's author-metrics view often requires an entitlement
tied to an institutional subscription, so a bare key may not be enough; the fallback is
there precisely for that case.

## Running it locally

```bash
python3 scripts/fetch_scholar.py     # refresh data/scholar.json
python3 -m http.server 4173          # then open http://localhost:4173
```

A plain `file://` open will not work: the page fetches its JSON.

## Design notes

Two typefaces (IBM Plex Sans and Mono), one accent, hairline rules, numbered sections.
Light and dark both meet WCAG AA on body and label text. The page prints to a clean
PDF — the chrome, the nav and the charts drop out.
