/* ============================================================================
   lucalazzaroni.github.io — page assembly
   Everything on the page comes from two files:
     data/cv.json      hand-maintained, bilingual
     data/scholar.json regenerated nightly by scripts/fetch_scholar.py
   ==========================================================================*/

(() => {
  'use strict';

  /* --- micro i18n for the chrome -----------------------------------------*/

  const UI = {
    'skip':            { en: 'Skip to content',            it: 'Vai al contenuto' },
    'loading':         { en: 'Loading…',                   it: 'Caricamento…' },
    'sec.profile':     { en: 'Profile',                    it: 'Profilo' },
    'sec.appointments':{ en: 'Appointments & education',   it: 'Incarichi e formazione' },
    'sec.metrics':     { en: 'Bibliometrics',              it: 'Bibliometria' },
    'sec.publications':{ en: 'Publications',               it: 'Pubblicazioni' },
    'sec.projects':    { en: 'Research projects',          it: 'Progetti di ricerca' },
    'sec.teaching':    { en: 'Teaching & academic appointments', it: 'Didattica e incarichi accademici' },
    'sec.service':     { en: 'Editorial & service',        it: 'Curatela e servizio' },
    'sec.talks':       { en: 'Invited & conference talks', it: 'Interventi a convegni' },
    'sec.awards':      { en: 'Awards & memberships',       it: 'Premi e associazioni' },
    'sec.contact':     { en: 'Contact & profiles',         it: 'Contatti e profili' },
    'nav.profile':     { en: 'Profile',       it: 'Profilo' },
    'nav.appointments':{ en: 'Appointments',  it: 'Incarichi' },
    'nav.metrics':     { en: 'Bibliometrics', it: 'Bibliometria' },
    'nav.publications':{ en: 'Publications',  it: 'Pubblicazioni' },
    'nav.projects':    { en: 'Projects',      it: 'Progetti' },
    'nav.teaching':    { en: 'Teaching',      it: 'Didattica' },
    'nav.service':     { en: 'Service',       it: 'Servizio' },
    'nav.talks':       { en: 'Talks',         it: 'Convegni' },
    'nav.awards':      { en: 'Awards',        it: 'Premi' },
    'nav.contact':     { en: 'Contact',       it: 'Contatti' },
    'lbl.sections':    { en: 'Sections',      it: 'Sezioni' },
    'lbl.courses':     { en: 'Courses',       it: 'Corsi' },
    'lbl.appointments':{ en: 'Academic appointments', it: 'Incarichi accademici' },
    'toggle.collapse': { en: 'collapse all',  it: 'comprimi tutto' },
    'toggle.expand':   { en: 'expand all',    it: 'espandi tutto' },
    'lbl.positions':   { en: 'Positions',     it: 'Posizioni' },
    'lbl.education':   { en: 'Education',     it: 'Formazione' },
    'lbl.supervision': { en: 'Supervision',   it: 'Supervisione' },
    'lbl.editorial':   { en: 'Editorial roles', it: 'Ruoli editoriali' },
    'lbl.organization':{ en: 'Conference organisation', it: 'Organizzazione di convegni' },
    'lbl.reviewing':   { en: 'Peer review',   it: 'Attività di revisione' },
    'lbl.journals':    { en: 'Journals',      it: 'Riviste' },
    'lbl.conferences': { en: 'Conferences',   it: 'Conferenze' },
    'lbl.memberships': { en: 'Professional memberships', it: 'Associazioni professionali' },
    'lbl.thesis':      { en: 'Thesis',        it: 'Tesi' },
    'lbl.grade':       { en: 'Grade',         it: 'Voto' },
    'lbl.since':       { en: 'since',         it: 'dal' },

    'm.documents':     { en: 'Documents',    it: 'Documenti' },
    'm.citations':     { en: 'Citations',     it: 'Citazioni' },
    'm.hindex':        { en: 'h-index',       it: 'Indice h' },
    'm.articles5':     { en: 'Articles, 5 yrs', it: 'Articoli, 5 anni' },

    'ch.pubs':         { en: 'Publications per year', it: 'Pubblicazioni per anno' },

    'cv.download':     { en: 'Download CV (PDF)', it: 'Scarica il CV (PDF)' },

    'f.all':           { en: 'All',           it: 'Tutte' },
    'f.journal':       { en: 'Journals',      it: 'Riviste' },
    'f.conference':    { en: 'Conferences',   it: 'Conferenze' },
    'f.national':      { en: 'National',      it: 'Nazionali' },
    'f.workshop':      { en: 'Workshops',     it: 'Workshop' },
    'f.editorial':     { en: 'Editorial',     it: 'Editoriali' },
    'f.chapter':       { en: 'Chapters',      it: 'Capitoli' },
    'f.book':          { en: 'Books',         it: 'Libri' },
    'f.erratum':       { en: 'Errata',        it: 'Errata' },
    'f.other':         { en: 'Other',         it: 'Altro' },

    't.journal':       { en: 'Journal',       it: 'Rivista' },
    't.conference':    { en: 'Conference',    it: 'Conferenza' },
    't.national':      { en: 'National',      it: 'Nazionale' },
    't.workshop':      { en: 'Workshop',      it: 'Workshop' },
    't.editorial':     { en: 'Editorial',     it: 'Editoriale' },
    't.chapter':       { en: 'Chapter',       it: 'Capitolo' },
    't.book':          { en: 'Book',          it: 'Libro' },
    't.erratum':       { en: 'Erratum',       it: 'Erratum' },
    't.other':         { en: 'Other',         it: 'Altro' },

    'p.search':        { en: 'Search title, author, venue', it: 'Cerca titolo, autore, sede' },
    'p.none':          { en: 'Nothing matches that filter.', it: 'Nessun risultato per questo filtro.' },
    'p.cites':         { en: 'cited {n}×',    it: 'citato {n}×' },
    'p.total':         { en: '{n} items · {i} in Scopus', it: '{n} voci · {i} su Scopus' },
    'p.talks':         { en: '{n} talks',     it: '{n} interventi' },
    'p.unindexed':     { en: 'not in Scopus', it: 'non su Scopus' },

    'sync':            { en: 'synced {d}',    it: 'agg. {d}' },
    'lbl.location':  { en: 'Based in', it: 'Sede' },
    'lbl.sector':    { en: 'Sector',   it: 'Settore' },
    'lbl.email':     { en: 'Email',    it: 'Email' }
  };

  const SECTIONS = ['profile','contact','appointments','teaching','service','talks','awards','projects','publications'];

  /* --- state --------------------------------------------------------------*/

  const store = {
    get(key, fallback) { try { return localStorage.getItem(key) ?? fallback; } catch { return fallback; } },
    set(key, value)    { try { localStorage.setItem(key, value); } catch { /* private mode */ } }
  };

  const urlLang = new URLSearchParams(location.search).get('lang');
  let lang = (urlLang === 'en' || urlLang === 'it')
    ? urlLang
    : store.get('ll.lang', (navigator.language || 'en').toLowerCase().startsWith('it') ? 'it' : 'en');
  let cv = null;
  let scholar = null;
  let pubFilter = 'all';
  let pubQuery = '';

  /* --- helpers ------------------------------------------------------------*/

  const $  = (sel, root = document) => root.querySelector(sel);
  const $$ = (sel, root = document) => [...root.querySelectorAll(sel)];
  const target = name => $(`[data-render="${name}"]`);

  /** Resolve a bilingual value: {en,it} -> string, string -> string. */
  const t = v => (v && typeof v === 'object' && !Array.isArray(v)) ? (v[lang] ?? v.en ?? '') : (v ?? '');
  const ui = (key, vars) => {
    let s = t(UI[key]) || key;
    if (vars) for (const [k, v] of Object.entries(vars)) s = s.replace(`{${k}}`, v);
    return s;
  };

  const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({ '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;' }[c]));

  const path = (obj, dotted) => dotted.split('.').reduce((o, k) => (o == null ? o : o[k]), obj);

  const fmtDate = iso => {
    if (!iso) return '';
    const d = new Date(iso);
    return Number.isNaN(+d) ? '' : d.toLocaleDateString(lang === 'it' ? 'it-IT' : 'en-GB', { day: 'numeric', month: 'short', year: 'numeric' });
  };

  const el = (html) => { const tpl = document.createElement('template'); tpl.innerHTML = html.trim(); return tpl.content; };

  /* --- theme --------------------------------------------------------------*/

  function applyTheme(mode) {
    if (mode === 'auto') document.documentElement.removeAttribute('data-theme');
    else document.documentElement.setAttribute('data-theme', mode);
    $$('[data-theme-btn]').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.themeBtn === mode)));
    store.set('ll.theme', mode);
  }

  /* --- renderers ----------------------------------------------------------*/

  function renderChrome() {
    document.documentElement.setAttribute('data-lang', lang);
    document.documentElement.lang = lang;
    $$('[data-t]').forEach(n => { n.textContent = ui(n.dataset.t); });
    $$('[data-lang-btn]').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.langBtn === lang)));
    $$('[data-bind]').forEach(n => { n.textContent = t(path(cv, n.dataset.bind)); });

    SECTIONS.forEach((id, i) => {
      const n = $(`#${id} .section-head .n`);
      if (n) n.textContent = String(i + 1).padStart(2, '0');
    });
  }

  function renderNav() {
    target('nav').innerHTML = SECTIONS.map((id, i) =>
      `<li><a href="#${id}"><span class="n">${String(i + 1).padStart(2, '0')}</span><span>${esc(ui('nav.' + id))}</span></a></li>`
    ).join('');
  }

  function renderIdMeta() {
    const p = cv.person;
    const rows = [
      [ui('lbl.location'), esc(t(p.location))],
      [ui('lbl.sector'),   esc(t(p.roleCode))],
      [ui('lbl.email'),    `<a href="mailto:${esc(p.email)}">${esc(p.email)}</a>`]
    ];
    target('idMeta').innerHTML = rows.map(([k, v]) => `<dt>${esc(k)}</dt><dd>${v}</dd>`).join('');
  }

  function renderCvButton() {
    const href = t(cv.person.cv);
    target('cvDownload').innerHTML =
      `<a class="cv-btn" href="${esc(href)}" download>
         <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3.5v11m0 0 4-4m-4 4-4-4M4.5 17.5v1a2 2 0 0 0 2 2h11a2 2 0 0 0 2-2v-1"/></svg>
         <span>${esc(ui('cv.download'))}</span>
       </a>`;
  }

  function renderSummary() {
    const paras = t(cv.summary) || [];
    target('summary').innerHTML =
      `<p class="lede">${esc(paras[0] ?? '')}</p>` + paras.slice(1).map(p => `<p>${esc(p)}</p>`).join('');
    target('keywords').innerHTML = (t(cv.person.keywords) || []).map(k => `<span class="tag">${esc(k)}</span>`).join('');
  }

  const entry = (when, title, org, note) => `
    <article class="entry">
      <div class="entry__when">${esc(when)}</div>
      <div class="entry__body">
        <h3 class="entry__title">${title}</h3>
        ${org  ? `<p class="entry__org">${org}</p>` : ''}
        ${note ? `<p class="entry__note">${note}</p>` : ''}
      </div>
    </article>`;

  function renderPositions() {
    target('positions').innerHTML = cv.positions
      .map(p => entry(t(p.period), esc(t(p.title)), esc(t(p.org)), esc(t(p.note))))
      .join('');
  }

  function renderEducation() {
    target('education').innerHTML = cv.education.map(e => {
      const bits = [];
      if (e.thesis) bits.push(`<em>${esc(ui('lbl.thesis'))}:</em> “${esc(t(e.thesis))}”`);
      if (e.grade)  bits.push(`<em>${esc(ui('lbl.grade'))}:</em> ${esc(e.grade)}`);
      return entry(e.year, esc(t(e.degree)), esc(t(e.org)), bits.join(' · '));
    }).join('');
  }

  function renderProjects() {
    target('projects').innerHTML = cv.projects.map(p => entry(
      p.acronym,
      `${esc(t(p.title))}`,
      `${esc(t(p.program))} · ${esc(t(p.role))}`,
      esc(t(p.blurb))
    )).join('');
  }

  function renderTeaching() {
    target('courses').innerHTML = cv.teaching.courses.map(c => entry(
      t(c.years),
      esc(t(c.name)),
      `${esc(t(c.role))} · <span class="mono" style="text-transform:none">cod. ${esc(c.code)}</span>`,
      ''
    )).join('');

    target('supervision').innerHTML = cv.teaching.supervision.entries
      .map(x => `<li><b>${x.count}</b><span>${esc(t(x.label))}</span></li>`).join('');

    target('appointments').innerHTML = (cv.teaching.appointments || [])
      .map(a => entry('', esc(t(a)), '', '')).join('');
  }

  function renderService() {
    const link = (label, url) => url ? `<a href="${esc(url)}" rel="noopener">${esc(label)}</a>` : esc(label);

    target('editorial').innerHTML = cv.service.editorial
      .map(e => entry(e.from, esc(t(e.role)), link(e.venue, e.url), esc(t(e.detail)))).join('');

    target('organization').innerHTML = cv.service.organization
      .map(o => entry('', esc(t(o.role)), link(o.venue, o.url), esc(t(o.detail)))).join('');

    const list = items => items.map(r =>
      `<li><span>${esc(r.name)}</span><span>${esc(ui('lbl.since'))} ${esc(r.since)}</span></li>`).join('');
    target('revJournals').innerHTML = list(cv.service.reviewingJournals);
    target('revConferences').innerHTML = list(cv.service.reviewingConferences);
  }

  function renderTalks() {
    target('talks').innerHTML = cv.talks
      .map(k => entry(t(k.date), esc(k.event), esc(t(k.where)), '')).join('');
    target('talkCount').textContent = ui('p.talks', { n: cv.talks.length });
  }

  function renderAwards() {
    target('awards').innerHTML = cv.awards
      .map(a => entry(a.year, esc(t(a.title)), esc(t(a.venue)), esc(a.paper))).join('');
    target('memberships').innerHTML = cv.memberships
      .map(m => entry('', esc(t(m.name)), esc(t(m.detail)), '')).join('');
  }

  /* One coherent set of stroked marks for the profile links — not a mix of logos. */
  const ICONS = {
    mail:        '<path d="M3 6.5h18v11H3z"/><path d="m3 7 9 6.5L21 7"/>',
    institution: '<path d="M3 20h18M4 20V9.5L12 5l8 4.5V20"/><path d="M9 20v-6h6v6"/>',
    id:          '<rect x="3" y="5" width="18" height="14" rx="2"/><circle cx="9" cy="11" r="2"/><path d="M6 16.6c.7-1.4 1.8-2.1 3-2.1s2.3.7 3 2.1M15 10h3M15 13.5h3"/>',
    database:    '<ellipse cx="12" cy="6" rx="7.5" ry="3"/><path d="M4.5 6v6c0 1.7 3.4 3 7.5 3s7.5-1.3 7.5-3V6"/><path d="M4.5 12v6c0 1.7 3.4 3 7.5 3s7.5-1.3 7.5-3v-6"/>',
    scholar:     '<path d="M12 4 1.5 9.2 12 14.5l10.5-5.3L12 4Z"/><path d="M5.5 11.3V16c0 1.7 2.9 3 6.5 3s6.5-1.3 6.5-3v-4.7"/>',
    code:        '<path d="m8.5 8.5-4 3.5 4 3.5M15.5 8.5l4 3.5-4 3.5M13.5 5.5l-3 13"/>',
    network:     '<circle cx="6" cy="17.5" r="2.5"/><circle cx="18" cy="17.5" r="2.5"/><circle cx="12" cy="5.5" r="2.5"/><path d="M10.4 7.6 7.6 15.4M13.6 7.6l2.8 7.8"/>',
    link:        '<path d="M10 13.5a4 4 0 0 0 5.7 0l2.8-2.8a4 4 0 0 0-5.7-5.7l-1.4 1.4"/><path d="M14 10.5a4 4 0 0 0-5.7 0l-2.8 2.8a4 4 0 0 0 5.7 5.7l1.4-1.4"/>'
  };

  const icon = name =>
    `<svg class="contact-cell__i" viewBox="0 0 24 24" aria-hidden="true">${ICONS[name] || ICONS.link}</svg>`;

  function renderContact() {
    target('contact').innerHTML = cv.links.map(l =>
      `<a class="contact-cell" href="${esc(l.url)}" rel="me noopener">
         ${icon(l.icon)}
         <span class="k">${esc(l.label)}</span>
         <span class="v">${esc(l.handle)}</span>
       </a>`
    ).join('');
  }

  /* --- bibliometrics ------------------------------------------------------*/

  function renderMetrics() {
    const m = scholar.metrics;
    const sc = m.scopus;

    const cards = [
      [m.counts.indexed, ui('m.documents')],
      [sc.citations,     ui('m.citations')],
      [sc.h_index,       ui('m.hindex')],
      [m.counts.journal_articles_5y, ui('m.articles5')]
    ].filter(([v]) => v != null);

    target('metrics').innerHTML = cards
      .map(([v, k]) => `<div class="metric"><div class="metric__v">${esc(v)}</div><div class="metric__k">${esc(k)}</div></div>`)
      .join('');

    target('syncStamp').textContent = ui('sync', { d: fmtDate(scholar.generated_at) });
    target('metricsSource').href = scholar.profiles.scopus;
    renderChart();
  }

  /** A bare bar chart: no gridlines, no frame, values on top. */
  function miniBars(series, caption, tone) {
    const years = Object.keys(series).sort();
    if (!years.length) return '';
    const max = Math.max(...years.map(y => series[y]), 1);
    const W = 260, H = 84, pad = 14, slot = (W - pad) / years.length, bw = Math.min(slot * 0.62, 22);

    const bars = years.map((y, i) => {
      const v = series[y];
      const h = Math.max((v / max) * (H - 30), v > 0 ? 2 : 0);
      const x = pad / 2 + i * slot + (slot - bw) / 2;
      return `<g>
        <rect class="bar${tone === 'cite' ? ' bar--cite' : ''}" x="${x.toFixed(1)}" y="${(H - 16 - h).toFixed(1)}" width="${bw.toFixed(1)}" height="${h.toFixed(1)}" rx="1"></rect>
        <text class="val" x="${(x + bw / 2).toFixed(1)}" y="${(H - 20 - h).toFixed(1)}" text-anchor="middle">${v}</text>
        <text class="axis" x="${(x + bw / 2).toFixed(1)}" y="${H - 4}" text-anchor="middle">${y.slice(2)}</text>
      </g>`;
    }).join('');

    const total = years.reduce((s, y) => s + series[y], 0);
    return `<div>
      <p class="mono" style="margin-bottom:.5rem">${esc(caption)}</p>
      <svg class="chart__svg" viewBox="0 0 ${W} ${H}" role="img" aria-label="${esc(caption)}: ${total} total, ${esc(years[0])}–${esc(years.at(-1))}">${bars}</svg>
    </div>`;
  }

  function renderChart() {
    // Only publications per year. Scopus counts citations by the year they were
    // *received*, which its Citation Overview API does not hand out on this key —
    // so rather than show a number that disagrees with the Scopus profile, this
    // chart shows the one series both agree on.
    target('chart').innerHTML = miniBars(scholar.metrics.publications_by_year, ui('ch.pubs'), 'pub');
  }

  /* --- publications -------------------------------------------------------*/

  function pubTypes() {
    const order = ['journal', 'conference', 'national', 'workshop', 'chapter', 'book', 'editorial', 'erratum', 'other'];
    const counts = scholar.metrics.counts;
    return order.filter(k => counts[k]);
  }

  function renderPubFilters() {
    const counts = scholar.metrics.counts;
    const chips = [['all', counts.total], ...pubTypes().map(k => [k, counts[k]])];
    target('pubFilters').innerHTML = chips.map(([k, n]) =>
      `<button type="button" class="filter" data-filter="${k}" aria-pressed="${k === pubFilter}">${esc(ui('f.' + k))}<span class="c">${n}</span></button>`
    ).join('');
    target('pubCount').textContent = ui('p.total', { n: counts.total, i: counts.indexed });
    target('pubSearch').placeholder = ui('p.search');
  }

  function pubCard(p) {
    const authors = p.authors.map((a, i) =>
      p.me.includes(i) ? `<b>${esc(a)}</b>` : esc(a)).join(', ');

    const bits = [];
    if (p.venue)  bits.push(`<span class="pub__venue">${esc(p.venue)}</span>`);
    if (p.series) bits.push(`<span class="pub__series">${esc(p.series)}</span>`);
    const num = [
      p.volume ? `vol. ${esc(p.volume)}` : null,
      p.issue  ? `no. ${esc(p.issue)}`   : null,
      p.pages  ? `pp. ${esc(p.pages)}`   : null,
      p.article_number ? `art. ${esc(p.article_number)}` : null
    ].filter(Boolean).join(', ');
    if (num) bits.push(`<span>${num}</span>`);
    bits.push(`<span class="tag">${esc(ui('t.' + p.type))}</span>`);

    const links = [];
    if (p.doi)      links.push(`<a href="https://doi.org/${esc(p.doi)}" rel="noopener">DOI</a>`);
    else if (p.url) links.push(`<a href="${esc(p.url)}" rel="noopener">Link</a>`);
    if (p.scopus_url) links.push(`<a href="${esc(p.scopus_url)}" rel="noopener">Scopus</a>`);
    if (p.indexed && p.citations > 0) links.push(`<span class="pub__cites">${esc(ui('p.cites', { n: p.citations }))}</span>`);
    if (!p.indexed) links.push(`<span class="pub__flag">${esc(ui('p.unindexed'))}</span>`);

    const head = p.url
      ? `<a href="${esc(p.url)}" rel="noopener">${esc(p.title)}</a>`
      : esc(p.title);

    return `<article class="pub">
      <h3 class="pub__title">${head}</h3>
      <p class="pub__authors">${authors}</p>
      <p class="pub__meta">${bits.join('')}</p>
      ${links.length ? `<p class="pub__links">${links.join('')}</p>` : ''}
      ${p.doi ? `<p class="pub__doi">https://doi.org/${esc(p.doi)}</p>` : ''}
    </article>`;
  }

  function renderPubList() {
    const q = pubQuery.trim().toLowerCase();
    const hits = scholar.publications.filter(p => {
      if (pubFilter !== 'all' && p.type !== pubFilter) return false;
      if (!q) return true;
      return `${p.title} ${p.authors.join(' ')} ${p.venue ?? ''} ${p.year ?? ''}`.toLowerCase().includes(q);
    });

    if (!hits.length) {
      target('pubList').innerHTML = `<p class="pub-empty">${esc(ui('p.none'))}</p>`;
      return;
    }

    const groups = new Map();
    for (const p of hits) {
      const y = p.year ?? '—';
      if (!groups.has(y)) groups.set(y, []);
      groups.get(y).push(p);
    }

    target('pubList').innerHTML = [...groups.entries()]
      .map(([year, items]) =>
        `<section class="pub-year"><h3 class="pub-year__n">${esc(year)}</h3><div>${items.map(pubCard).join('')}</div></section>`)
      .join('');
  }

  /* --- collapsing ---------------------------------------------------------*/

  /** Which sections are folded away. Remembered per visitor, never for print. */
  const collapsed = new Set((store.get('ll.collapsed', '') || '').split(',').filter(Boolean));

  function applyCollapsed() {
    SECTIONS.forEach(id => {
      const section = document.getElementById(id);
      if (!section) return;
      const open = !collapsed.has(id);
      section.classList.toggle('is-collapsed', !open);
      section.querySelector('.section-toggle')?.setAttribute('aria-expanded', String(open));
    });
    const allShut = SECTIONS.every(id => collapsed.has(id));
    const all = target('toggleAll');
    if (all) {
      all.textContent = ui(allShut ? 'toggle.expand' : 'toggle.collapse');
      all.dataset.action = allShut ? 'expand' : 'collapse';
    }
    store.set('ll.collapsed', [...collapsed].join(','));
  }

  function setCollapsed(id, value) {
    value ? collapsed.add(id) : collapsed.delete(id);
    applyCollapsed();
  }

  function wireCollapsing() {
    $$('.section-toggle').forEach(btn => btn.addEventListener('click', () => {
      const id = btn.closest('.section').id;
      setCollapsed(id, !collapsed.has(id));
    }));

    target('toggleAll').addEventListener('click', e => {
      const expanding = e.currentTarget.dataset.action === 'expand';
      collapsed.clear();
      if (!expanding) SECTIONS.forEach(id => collapsed.add(id));
      applyCollapsed();
    });

    // Jumping to a folded section opens it, otherwise the link goes nowhere useful.
    const openTarget = () => {
      const id = location.hash.slice(1);
      if (SECTIONS.includes(id) && collapsed.has(id)) {
        setCollapsed(id, false);
        requestAnimationFrame(() => document.getElementById(id)?.scrollIntoView());
      }
    };
    target('nav').addEventListener('click', e => {
      const link = e.target.closest('a[href^="#"]');
      if (link) setCollapsed(link.getAttribute('href').slice(1), false);
    });
    window.addEventListener('hashchange', openTarget);
    openTarget();
  }

  /* --- scrollspy ----------------------------------------------------------*/

  function spy() {
    const links = new Map($$('.nav a').map(a => [a.getAttribute('href').slice(1), a]));
    const seen = new Set();
    const io = new IntersectionObserver(entries => {
      for (const e of entries) e.isIntersecting ? seen.add(e.target.id) : seen.delete(e.target.id);
      const active = SECTIONS.find(id => seen.has(id));
      links.forEach((a, id) => a.setAttribute('aria-current', String(id === active)));
    }, { rootMargin: '-12% 0px -70% 0px', threshold: 0 });
    SECTIONS.forEach(id => { const n = document.getElementById(id); if (n) io.observe(n); });
  }

  /* --- boot ---------------------------------------------------------------*/

  function renderAll() {
    renderChrome();
    renderNav();
    renderIdMeta();
    renderCvButton();
    renderSummary();
    renderPositions();
    renderEducation();
    renderProjects();
    renderTeaching();
    renderService();
    renderTalks();
    renderAwards();
    renderContact();
    applyCollapsed();
    if (scholar) {
      renderMetrics();
      renderPubFilters();
      renderPubList();
    }
  }

  function wire() {
    $$('[data-lang-btn]').forEach(b => b.addEventListener('click', () => {
      lang = b.dataset.langBtn;
      store.set('ll.lang', lang);
      renderAll();
    }));

    $$('[data-theme-btn]').forEach(b => b.addEventListener('click', () => applyTheme(b.dataset.themeBtn)));

    target('pubFilters').addEventListener('click', e => {
      const btn = e.target.closest('[data-filter]');
      if (!btn) return;
      pubFilter = btn.dataset.filter;
      $$('[data-filter]').forEach(x => x.setAttribute('aria-pressed', String(x === btn)));
      renderPubList();
    });

    let debounce;
    target('pubSearch').addEventListener('input', e => {
      clearTimeout(debounce);
      const v = e.target.value;
      debounce = setTimeout(() => { pubQuery = v; renderPubList(); }, 120);
    });
  }

  async function boot() {
    applyTheme(store.get('ll.theme', 'auto'));

    const load = async url => {
      const r = await fetch(url, { cache: 'no-cache' });
      if (!r.ok) throw new Error(`${url}: ${r.status}`);
      return r.json();
    };

    try {
      [cv, scholar] = await Promise.all([load('data/cv.json'), load('data/scholar.json').catch(() => null)]);
    } catch (err) {
      console.error(err);
      $('#main').insertAdjacentHTML('afterbegin',
        `<div class="noscript"><p>Could not load the CV data files. The full CV is available as a <a href="assets/cv-luca-lazzaroni-en.pdf">PDF</a>.</p></div>`);
      return;
    }

    renderAll();
    wire();
    wireCollapsing();
    spy();

    if (!scholar) {
      target('pubList').innerHTML = `<p class="pub-empty">Publication data is being rebuilt. See <a href="https://www.scopus.com/authid/detail.uri?authorId=57220892898">Scopus</a> meanwhile.</p>`;
      target('metrics').innerHTML = '';
    }

    // The PDF renderer waits for this before printing.
    document.documentElement.dataset.ready = 'true';
  }

  document.addEventListener('DOMContentLoaded', boot);
})();
