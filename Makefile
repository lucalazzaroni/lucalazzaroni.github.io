# Maintenance shortcuts. `make` on its own lists them.
#
# The Scopus key is read from the macOS Keychain, so it is never written to this
# repository or to a dotfile. Store it once with `make key`.

SHELL := /bin/bash
PORT  ?= 4173

SCOPUS_API_KEY ?= $(shell security find-generic-password -s scopus-api-key -w 2>/dev/null)
export SCOPUS_API_KEY

.PHONY: help check sync pdf serve publish key

help:
	@echo "make check    validate data/cv.json and data/publications.manual.json"
	@echo "make sync     refresh publications from Scopus, then reprint both PDFs"
	@echo "make pdf      reprint the PDFs only"
	@echo "make serve    preview on http://localhost:$(PORT)"
	@echo "make publish  sync, then commit and push the result"
	@echo "make key      store the Scopus API key in the macOS Keychain"
	@echo
	@echo "Scopus keys are tied to the university's IP range: sync and publish"
	@echo "only work from the UniGe network or VPN."

check:
	@python3 scripts/check_data.py

sync: check
	@python3 scripts/fetch_scholar.py
	@python3 scripts/render_pdf.py

pdf:
	@python3 scripts/render_pdf.py

serve:
	@echo "→ http://localhost:$(PORT)  (add ?lang=it to pin the language)"
	@python3 -m http.server $(PORT)

publish: sync
	@git add data/scholar.json data/.crossref-cache.json assets/*.pdf
	@if git diff --staged --quiet; then \
		echo "Nothing moved."; \
	else \
		git commit -m "build: refresh publications and CV PDFs" && git push; \
	fi

key:
	@security add-generic-password -U -a "$$USER" -s scopus-api-key -w \
		-D "Elsevier Scopus API key" -l "Scopus API key (lucalazzaroni.github.io)" \
		&& echo "Stored. 'make sync' will pick it up."
