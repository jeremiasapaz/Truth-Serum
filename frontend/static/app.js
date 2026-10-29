// Leader Transparency Scoring Platform — frontend
const API = "";
const CATEGORY_ORDER = [
  "Corruption", "Crime", "Environmental Crime", "Male Chauvinism", "Homophobia",
  "Personal Integrity", "Court Proceedings", "Scandals", "Human Rights", "Democratic Integrity",
];

const CLASS_COLORS = {
  "VERIFIED FACT": "#3fb950", "OFFICIAL RECORD": "#3fb950", "COURT RECORD": "#2ea043",
  "GOVERNMENT DATA": "#2ea043", "INTERNATIONAL REPORT": "#4f9cf9", "NGO REPORT": "#4f9cf9",
  "FACT CHECK": "#58a6ff", "ONGOING INVESTIGATION": "#d29922", "POLICY DECISION": "#8b98a8",
  "PUBLIC STATEMENT": "#8b98a8", "MEDIA REPORT": "#8b98a8", "REPORTED ALLEGATION": "#db6d28",
  "DISPUTED CLAIM": "#f85149", "UNVERIFIED CLAIM": "#da3633",
};

// Translations for Brazilian Portuguese
const TRANSLATIONS = {
  en: {
    title: "Truth Serum",
    tagline: "Scores from documented evidence & source weighting — not legal guilt.",
    dashboard: "Dashboard",
    compare: "Compare",
    country: "Public Impact",
    financial: "Financial Transparency",
    videos: "Videos",
    transcripts: "Speech Transcripts",
    sources: "Sources",
    methodology: "Methodology",
    leaders: "Leaders",
    compareLeaders: "Compare Leaders",
    compareSubtitle: "(up to 10)",
    selectLeaders: "Select 2+ leaders to compare.",
    radarScores: "Radar — category scores",
    barTotal: "Bar — total score",
    heatmapScores: "Heatmap — scores by category",
    trendHistory: "Trend — score history",
    countryTitle: "Country Performance & Administration Impact",
    countrySubtitle: "(World Bank + Our World in Data)",
    administrations: "Administrations",
    heatmap: "Heatmap",
    greenEnergy: "Green Energy",
    citizenReality: "Citizen Reality",
    keywordSearch: "Keyword search…",
    confidence: "Confidence",
    indicators: "indicators",
    downloadCSV: "Download CSV",
    indicator: "Indicator",
    baseline: "Baseline",
    admin: "Admin",
    delta: "Δ",
    source: "Source",
    noData: "No data available",
    ingestData: "Ingest World Bank data",
    ingesting: "Ingesting…",
    error: "Error — retry",
    shockContext: "Global context during term:",
    shockNote: ". Impact is estimated, not attributed as direct causation.",
    llmStatus: "LLM scoring status",
    geography: "Geography",
    continent: "Continent",
    region: "Region",
    country: "Country",
    politics: "Politics",
    affiliation: "Affiliation",
    status: "Status",
    all: "All",
    currentLeaders: "Current leaders",
    formerLeaders: "Former leaders",
    overallPolarity: "Overall polarity",
    positive: "Positive",
    neutral: "Neutral",
    negative: "Negative",
    scoreRange: "Total score range",
    confidenceRange: "Confidence range",
    resetFilters: "Reset filters",
    scoringPrinciple: "Scoring principle",
    trustWeights: "Trust & Confidence weights",
    source: "Source",
    rating: "Rating",
    category: "Category",
    evidenceType: "Evidence Type",
    weight: "Weight",
    aiModel: "AI Model",
    endpoint: "Endpoint",
    status: "Status",
    active: "Active",
    inactive: "Inactive",
    keyless: "Keyless",
    keyed: "Keyed",
    countryData: "Country Data",
    liveIndicators: "Live Indicators",
    pluggableIndicators: "Pluggable Indicators",
    dataset: "Dataset",
    sourceUrl: "Source URL",
  },
  pt: {
    title: "Soro da Verdade",
    tagline: "Pontuações baseadas em evidências documentadas e ponderação de fontes — não culpa legal.",
    dashboard: "Painel",
    compare: "Comparar",
    country: "Impacto Público",
    financial: "Transparência Financeira",
    videos: "Vídeos",
    transcripts: "Transcrições de Discursos",
    sources: "Fontes",
    methodology: "Metodologia",
    leaders: "Líderes",
    compareLeaders: "Comparar Líderes",
    compareSubtitle: "(até 10)",
    selectLeaders: "Selecione 2+ líderes para comparar.",
    radarScores: "Radar — pontuações por categoria",
    barTotal: "Barra — pontuação total",
    heatmapScores: "Mapa de calor — pontuações por categoria",
    trendHistory: "Tendência — histórico de pontuações",
    countryTitle: "Desempenho do País e Impacto da Administração",
    countrySubtitle: "(Banco Mundial + Our World in Data)",
    administrations: "Administrações",
    heatmap: "Mapa de Calor",
    greenEnergy: "Energia Verde",
    citizenReality: "Realidade do Cidadão",
    keywordSearch: "Busca por palavra-chave…",
    confidence: "Confiança",
    indicators: "indicadores",
    downloadCSV: "Baixar CSV",
    indicator: "Indicador",
    baseline: "Linha de base",
    admin: "Admin",
    delta: "Δ",
    source: "Fonte",
    noData: "Dados não disponíveis",
    ingestData: "Ingerir dados do Banco Mundial",
    ingesting: "Ingerindo…",
    error: "Erro — tentar novamente",
    shockContext: "Contexto global durante o mandato:",
    shockNote: ". O impacto é estimado, não atribuído como causalidade direta.",
    llmStatus: "Status da pontuação por IA",
    geography: "Geografia",
    continent: "Continente",
    region: "Região",
    country: "País",
    politics: "Política",
    affiliation: "Filiação",
    status: "Status",
    all: "Todos",
    currentLeaders: "Líderes atuais",
    formerLeaders: "Líderes anteriores",
    overallPolarity: "Polaridade geral",
    positive: "Positivo",
    neutral: "Neutro",
    negative: "Negativo",
    scoreRange: "Faixa de pontuação total",
    confidenceRange: "Faixa de confiança",
    resetFilters: "Redefinir filtros",
    scoringPrinciple: "Princípio de pontuação",
    trustWeights: "Pesos de Confiança e Credibilidade",
    source: "Fonte",
    rating: "Avaliação",
    category: "Categoria",
    evidenceType: "Tipo de Evidência",
    weight: "Peso",
    aiModel: "Modelo de IA",
    endpoint: "Endpoint",
    status: "Status",
    active: "Ativo",
    inactive: "Inativo",
    keyless: "Sem chave",
    keyed: "Com chave",
    countryData: "Dados do País",
    liveIndicators: "Indicadores Ativos",
    pluggableIndicators: "Indicadores Conectáveis",
    dataset: "Conjunto de dados",
    sourceUrl: "URL da Fonte",
  },
};

let currentLang = localStorage.getItem("lang") || "en";

function t(key) {
  return TRANSLATIONS[currentLang][key] || TRANSLATIONS.en[key] || key;
}

function setLang(lang) {
  currentLang = lang;
  localStorage.setItem("lang", lang);
  location.reload();
}

const state = {
  options: null,
  leaders: [],
  filters: {},
  selected: new Set(),
  charts: {},
  llm: false,
};

// ---------- helpers ----------
const $ = (s, r = document) => r.querySelector(s);
const $$ = (s, r = document) => [...r.querySelectorAll(s)];
const el = (tag, attrs = {}, ...kids) => {
  const n = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (k === "class") n.className = v;
    else if (k === "html") n.innerHTML = v;
    else if (k.startsWith("on")) n.addEventListener(k.slice(2), v);
    else n.setAttribute(k, v);
  }
  for (const kid of kids) if (kid != null) n.append(kid.nodeType ? kid : document.createTextNode(kid));
  return n;
};
const api = (p) => fetch(API + p).then((r) => r.json());
const scoreClass = (s) => (s > 0 ? "pos" : s < 0 ? "neg" : "neu");
const scoreLabel = (s) => (s > 0 ? "+1" : s < 0 ? "−1" : "0");
const scoreColor = (s) => (s > 0 ? "#3fb950" : s < 0 ? "#f85149" : "#8b98a8");
const totalColor = (t) => (t > 5 ? "#3fb950" : t < -5 ? "#f85149" : "#8b98a8");

// ---------- tabs ----------
$$(".tab").forEach((t) =>
  t.addEventListener("click", () => {
    $$(".tab").forEach((x) => x.classList.remove("active"));
    $$(".view").forEach((x) => x.classList.remove("active"));
    t.classList.add("active");
    $("#view-" + t.dataset.view).classList.add("active");
    if (t.dataset.view === "compare") renderComparePicker();
    if (t.dataset.view === "methodology") renderMethodology();
    if (t.dataset.view === "country") renderCountryTab();
    if (t.dataset.view === "transcripts") renderTranscripts();
    if (t.dataset.view === "financial") renderFinancial();
    if (t.dataset.view === "official") renderOfficial();
    if (t.dataset.view === "videos") renderVideos();
    if (t.dataset.view === "sources") renderSources();
  })
);

// Language switcher
$("#lang-switch").addEventListener("click", () => {
  setLang(currentLang === "en" ? "pt" : "en");
});

// Apply translations on load
function applyTranslations() {
  document.title = t("title");
  $(".brand h1").textContent = t("title");
  $(".tagline").textContent = t("tagline");
  
  // Update tabs by ID to ensure they're updated
  if ($("#tab-country")) $("#tab-country").textContent = t("country");
  if ($("#tab-financial")) $("#tab-financial").textContent = t("financial");
  if ($("#tab-videos")) $("#tab-videos").textContent = t("videos");
  if ($("#tab-transcripts")) $("#tab-transcripts").textContent = t("transcripts");
  if ($("#tab-sources")) $("#tab-sources").textContent = t("sources");
  if ($("#tab-methodology")) $("#tab-methodology").textContent = t("methodology");
  
  $("#lang-switch").textContent = currentLang === "en" ? "🇧🇷 PT" : "🇺🇸 EN";
  
  // Show Portuguese popup if language is Portuguese
  if (currentLang === "pt") {
    const popupShown = localStorage.getItem("ptPopupShown");
    if (!popupShown) {
      $("#pt-popup").style.display = "flex";
    }
  }
  
  // Update dynamic elements
  const leadersTitle = $("#leaders-title");
  if (leadersTitle) {
    const count = $("#result-count").textContent;
    leadersTitle.textContent = `${t("leaders")} ${count}`;
  }
  
  const keywordInput = $("#keyword");
  if (keywordInput) keywordInput.placeholder = t("keywordSearch");
}

// ---------- init ----------
async function init() {
  const health = await api("/api/health");
  state.llm = health.llm_enabled;
  const badge = $("#llm-badge");
  badge.textContent = health.llm_enabled ? "LLM scoring: ON" : "LLM scoring: OFF (engine)";
  badge.classList.add(health.llm_enabled ? "on" : "off");

  state.options = await api("/api/leaders/filters/options");
  buildFilters();
  buildSort();
  await loadLeaders();
  
  // Apply translations
  applyTranslations();
}

// ---------- filters ----------
function buildFilters() {
  const o = state.options;
  const f = $("#filters");
  const mkSelect = (id, label, values) =>
    el("div", {},
      el("label", {}, label),
      el("select", { id, onchange: onFilterChange },
        el("option", { value: "" }, "All"),
        ...values.map((v) => el("option", { value: v }, v))));

  f.append(el("h3", {}, "Geography"));
  f.append(mkSelect("f-continent", "Continent", o.continents));
  f.append(mkSelect("f-region", "Region", o.regions));
  f.append(mkSelect("f-country", "Country", o.countries));

  f.append(el("h3", {}, "Politics"));
  f.append(mkSelect("f-affiliation", "Affiliation", o.affiliations));
  f.append(el("div", {},
    el("label", {}, "Status"),
    el("select", { id: "f-current", onchange: onFilterChange },
      el("option", { value: "" }, "All"),
      el("option", { value: "true" }, "Current leaders"),
      el("option", { value: "false" }, "Former leaders"))));
  f.append(el("div", {},
    el("label", {}, "Overall polarity"),
    el("select", { id: "f-polarity", onchange: onFilterChange },
      el("option", { value: "" }, "All"),
      el("option", { value: "positive" }, "Positive"),
      el("option", { value: "neutral" }, "Neutral"),
      el("option", { value: "negative" }, "Negative"))));

  f.append(el("h3", {}, "Total score range"));
  f.append(el("div", { class: "range-row" },
    el("input", { type: "number", id: "f-score-min", placeholder: "min", oninput: debounce(onFilterChange) }),
    el("input", { type: "number", id: "f-score-max", placeholder: "max", oninput: debounce(onFilterChange) })));

  f.append(el("h3", {}, "Confidence range"));
  f.append(el("div", { class: "range-row" },
    el("input", { type: "number", id: "f-conf-min", placeholder: "min", oninput: debounce(onFilterChange) }),
    el("input", { type: "number", id: "f-conf-max", placeholder: "max", oninput: debounce(onFilterChange) })));

  f.append(el("button", { class: "btn secondary reset-btn", onclick: resetFilters }, "Reset filters"));
}

function buildSort() {
  const labels = {
    total_score_desc: "Most positive", total_score_asc: "Most negative",
    confidence_desc: "Highest confidence", confidence_asc: "Lowest confidence",
    name: "Name (A–Z)", most_evidence: "Most evidence records",
    most_scandals: "Most scandals", most_investigated: "Most investigated",
    most_controversial: "Most controversial", most_court_documents: "Most court documents",
    highest_corruption: "Highest corruption concern", lowest_corruption: "Lowest corruption concern",
    highest_environmental: "Best environmental", lowest_environmental: "Worst environmental",
    most_human_rights: "Best human rights", most_democratic_integrity: "Most democratic concern",
  };
  const sel = $("#sort");
  state.options.sorts.forEach((s) =>
    sel.append(el("option", { value: s }, labels[s] || s)));
  sel.value = "total_score_desc";
  sel.addEventListener("change", onFilterChange);
  $("#keyword").addEventListener("input", debounce(onFilterChange));
}

function onFilterChange() { loadLeaders(); }
function resetFilters() {
  $$("#filters select").forEach((s) => (s.value = ""));
  $$("#filters input").forEach((i) => (i.value = ""));
  $("#keyword").value = "";
  loadLeaders();
}

function debounce(fn, ms = 300) {
  let t;
  return (...a) => { clearTimeout(t); t = setTimeout(() => fn(...a), ms); };
}

async function loadLeaders() {
  const p = new URLSearchParams();
  const add = (id, key) => { const v = $("#" + id)?.value; if (v) p.set(key, v); };
  add("f-continent", "continent");
  add("f-region", "region");
  add("f-country", "country");
  add("f-affiliation", "political_affiliation");
  add("f-current", "current");
  add("f-polarity", "polarity");
  add("f-score-min", "score_min");
  add("f-score-max", "score_max");
  add("f-conf-min", "confidence_min");
  add("f-conf-max", "confidence_max");
  const kw = $("#keyword").value.trim();
  if (kw) p.set("keyword", kw);
  p.set("sort", $("#sort").value);

  state.leaders = await api("/api/leaders?" + p.toString());
  $("#result-count").textContent = `(${state.leaders.length})`;
  renderGrid();
  applyTranslations(); // Re-apply after data loads
}

function renderGrid() {
  const grid = $("#leader-grid");
  grid.innerHTML = "";
  if (!state.leaders.length) { grid.append(el("div", { class: "empty" }, "No leaders match these filters.")); return; }
  state.leaders.forEach((l) => grid.append(leaderCard(l)));
}

function leaderCard(l) {
  const card = el("div", { class: "leader-card", onclick: () => openLeader(l.id) });
  card.append(el("div", { class: "lc-head" },
    el("div", {},
      el("h3", {}, l.name),
      el("div", { class: "sub" }, `${l.country || "—"} · ${l.continent || "—"}`)),
    el("span", { class: "score-pill", style: `color:${totalColor(l.total_score)}` },
      (l.total_score > 0 ? "+" : "") + l.total_score)));
  card.append(el("div", { class: "lc-meta" },
    el("span", { class: "tag " + (l.current ? "current" : "former") }, l.current ? "Current" : "Former"),
    el("span", {}, `${l.evidence_total} evidence`),
    el("span", {}, l.political_affiliation || "")));

  card.append(el("div", { class: "conf-bar" }, el("span", { style: `width:${l.avg_confidence}%` })));
  card.append(el("div", { class: "sub", style: "margin-top:6px" }, `Avg confidence ${l.avg_confidence}%`));
  return card;
}

// ---------- leader detail drawer ----------
async function openLeader(id) {
  const [detail, evidence] = await Promise.all([
    api("/api/leaders/" + id),
    api("/api/evidence/leader/" + id),
  ]);
  const byCat = {};
  evidence.forEach((e) => (byCat[e.category] ||= []).push(e));

  const panel = $("#drawer-panel");
  panel.innerHTML = "";
  panel.append(el("button", { class: "close", onclick: closeDrawer }, "×"));
  panel.append(el("div", { class: "detail-head" },
    el("h2", {}, detail.name),
    el("div", { class: "sub" },
      `${detail.country || "—"} · ${detail.region || "—"} · ${detail.continent || "—"}`),
    el("div", { class: "sub" },
      `${detail.political_affiliation || "—"} · ${detail.current ? "Current leader" : "Former leader"}`)));
  if (detail.bio) panel.append(el("p", { class: "sub", style: "margin-top:10px;line-height:1.5" }, detail.bio));

  panel.append(el("div", { class: "detail-total" },
    el("div", {},
      el("div", { class: "muted" }, "Total score"),
      el("div", { class: "big", style: `color:${totalColor(detail.total_score)}` },
        (detail.total_score > 0 ? "+" : "") + detail.total_score)),
    el("div", {},
      el("div", { class: "muted" }, "Avg confidence"),
      el("div", { class: "big" }, detail.avg_confidence + "%")),
    el("div", {},
      el("div", { class: "muted" }, "Evidence"),
      el("div", { class: "big" }, detail.evidence_total))));

  // Criminal Records section
  const hasCriminalRecord = detail.name.includes("Lula") || detail.name.includes("Bolsonaro");
  if (hasCriminalRecord) {
    panel.append(el("div", { class: "criminal-records", style: "margin-top:16px;padding:12px;background:var(--panel-2);border:1px solid var(--warn);border-radius:8px" },
      el("div", { style: "display:flex;align-items:center;gap:8px;margin-bottom:8px" },
        el("span", { style: "color:var(--warn);font-size:18px" }, "⚠"),
        el("strong", { style: "color:var(--warn)" }, "Criminal Record")),
      el("div", { class: "muted", style: "font-size:13px" },
        detail.name.includes("Lula") 
          ? "Arrested in 2018 on corruption charges (Operation Car Wash). Convicted and sentenced to 12 years, later overturned by Supreme Court."
          : "Jair Bolsonaro: Multiple investigations for corruption, attacks on democracy, and spreading false information. Flávio Bolsonaro: Investigations for corruption and money laundering (crackhead scheme).")));
  }

  const cats = el("div", { style: "margin-top:16px" });
  detail.scores.sort((a, b) => CATEGORY_ORDER.indexOf(a.category) - CATEGORY_ORDER.indexOf(b.category));
  detail.scores.forEach((s) => cats.append(categoryRow(s, byCat[s.category] || [])));
  panel.append(cats);

  $("#drawer").classList.add("show");
  $("#overlay").classList.add("show");
}

function categoryRow(s, evidence) {
  const row = el("div", { class: "cat-row" });
  const head = el("div", { class: "cat-head", onclick: () => row.classList.toggle("open") },
    el("span", { class: "dot " + scoreClass(s.score) }),
    el("span", { class: "cat-name" }, s.category),
    el("span", { class: "cat-conf" }, `${scoreLabel(s.score)} · ${s.confidence}% · ${s.evidence_count} ev`));
  row.append(head);

  const body = el("div", { class: "cat-body" });
  body.append(el("div", { class: "components" },
    comp("Quality", s.source_quality),
    comp("Sources", s.source_count, ""),
    comp("Evidence", s.evidence_count, ""),
    el("span", { class: "scored-by" }, "scored by " + s.scored_by)));
  if (s.reason) body.append(el("div", { class: "cat-reason" }, s.reason));

  if (!evidence.length) body.append(el("div", { class: "sub" }, "No evidence recorded."));
  evidence.forEach((e) => body.append(evidenceItem(e)));
  row.append(body);
  return row;
}
const comp = (label, val, suffix = "%") =>
  el("span", { class: "component" }, `${label}: ${val}${suffix}`);

function evidenceItem(e) {
  const color = CLASS_COLORS[e.classification] || "#8b98a8";
  return el("div", { class: "evidence-item" },
    el("div", { class: "ei-head" },
      el("span", { class: "ei-title", onclick: () => openEvidence(e.id) }, e.title),
      el("span", { class: "class-tag", style: `background:${color};color:#0f1419` }, e.classification)),
    el("div", { class: "sub", style: "margin-top:4px" },
      `${e.source_name} · rating ${e.source_rating.toFixed(2)} · ${e.polarity > 0 ? "+" : ""}${e.polarity}` +
      (e.published_at ? " · " + e.published_at.slice(0, 10) : "")));
}

async function rescore(id, btn) {
  btn.disabled = true;
  const original = btn.textContent;
  btn.textContent = "Scoring…";
  try {
    const res = await fetch(API + "/api/scoring/leader/" + id, { method: "POST" }).then((r) => r.json());
    btn.textContent = `Scored ${res.categories_scored} categories (${res.scored_by})`;
    await openLeader(id);
    await loadLeaders();
  } catch (e) {
    btn.textContent = "Error — retry";
    btn.disabled = false;
  }
}

function closeDrawer() {
  $("#drawer").classList.remove("show");
  $("#overlay").classList.remove("show");
}

function closePtPopup() {
  $("#pt-popup").style.display = "none";
  localStorage.setItem("ptPopupShown", "true");
}
$("#overlay").addEventListener("click", closeDrawer);

// ---------- evidence modal ----------
async function openEvidence(id) {
  const e = await api("/api/evidence/" + id);
  const panel = $("#evidence-panel");
  const color = CLASS_COLORS[e.classification] || "#8b98a8";
  panel.innerHTML = "";
  panel.append(el("button", { class: "close", onclick: closeEvidence }, "×"));
  panel.append(el("h2", {}, e.title));
  panel.append(el("span", { class: "class-tag", style: `background:${color};color:#0f1419` }, e.classification));
  panel.append(el("div", { class: "kv" },
    el("span", { class: "k" }, "Category"), el("span", {}, e.category),
    el("span", { class: "k" }, "Source"), el("span", {}, e.source_name),
    el("span", { class: "k" }, "Source rating"), el("span", {}, e.source_rating.toFixed(2) + " / 1.00"),
    el("span", { class: "k" }, "Polarity"), el("span", { style: `color:${scoreColor(e.polarity)}` }, scoreLabel(e.polarity)),
    el("span", { class: "k" }, "Published"), el("span", {}, e.published_at ? e.published_at.slice(0, 10) : "unknown"),
    el("span", { class: "k" }, "Source URL"),
    el("span", {}, el("a", { href: e.source_url, target: "_blank", style: "color:var(--accent)" }, e.source_url || "—"))));
  panel.append(el("div", { class: "muted", style: "margin-bottom:6px" }, "Extracted text"));
  panel.append(el("div", { class: "extracted" }, e.extracted_text || "(none)"));
  $("#evidence-modal").classList.add("show");
}
function closeEvidence() { $("#evidence-modal").classList.remove("show"); }
$("#evidence-modal").addEventListener("click", (ev) => { if (ev.target.id === "evidence-modal") closeEvidence(); });

// ---------- compare ----------
function renderComparePicker() {
  const box = $("#compare-picker");
  box.innerHTML = "";
  
  // Populate country filter if not already populated
  const countrySelect = $("#compare-country");
  if (countrySelect && countrySelect.options.length === 1) {
    const countries = [...new Set(state.leaders.map(l => l.country))].sort();
    countries.forEach(country => {
      const opt = el("option", { value: country }, country);
      countrySelect.append(opt);
    });
  }
  
  // Filter leaders based on search and country
  const searchTerm = ($("#compare-search")?.value || "").toLowerCase();
  const countryFilter = ($("#compare-country")?.value || "all");
  
  const filteredLeaders = state.leaders.filter(l => {
    const matchesSearch = l.name.toLowerCase().includes(searchTerm);
    const matchesCountry = countryFilter === "all" || l.country === countryFilter;
    return matchesSearch && matchesCountry;
  });
  
  filteredLeaders.forEach((l) => {
    const p = el("div", {
      class: "pick" + (state.selected.has(l.id) ? " selected" : ""),
      onclick: () => toggleSelect(l.id),
    }, l.name);
    box.append(p);
  });
  renderCompareCharts();
}

// Add event listeners for compare filters
$("#compare-search")?.addEventListener("input", renderComparePicker);
$("#compare-country")?.addEventListener("change", renderComparePicker);

function toggleSelect(id) {
  if (state.selected.has(id)) state.selected.delete(id);
  else if (state.selected.size < 10) state.selected.add(id);
  renderComparePicker();
}

async function renderCompareCharts() {
  const ids = [...state.selected];
  const empty = $("#compare-empty");
  const charts = $("#compare-charts");
  if (ids.length < 2) { empty.style.display = "block"; charts.style.display = "none"; return; }
  empty.style.display = "none"; charts.style.display = "grid";

  const data = await api("/api/compare?" + ids.map((i) => "ids=" + i).join("&"));
  const palette = ["#4f9cf9", "#3fb950", "#f85149", "#d29922", "#a371f7", "#39c5cf", "#db6d28", "#ec6cb9", "#8b949e", "#58a6ff"];

  // Radar: category scores
  drawChart("chart-radar", "radar", {
    labels: data.categories,
    datasets: data.leaders.map((l, i) => ({
      label: l.name,
      data: data.categories.map((c) => l.categories[c].score),
      borderColor: palette[i], backgroundColor: palette[i] + "22", borderWidth: 2,
    })),
  }, { scales: { r: { min: -1, max: 1, ticks: { stepSize: 1, color: "#8b98a8", backdropColor: "transparent" },
    grid: { color: "#2d3a48" }, angleLines: { color: "#2d3a48" }, pointLabels: { color: "#e6edf3", font: { size: 10 } } } },
    plugins: { legend: { labels: { color: "#e6edf3" } } } });

  // Bar: total score
  drawChart("chart-bar", "bar", {
    labels: data.leaders.map((l) => l.name),
    datasets: [{ label: "Total score", data: data.leaders.map((l) => l.total_score),
      backgroundColor: data.leaders.map((l) => totalColor(l.total_score)) }],
  }, { scales: { y: { min: -100, max: 100, grid: { color: "#2d3a48" }, ticks: { color: "#8b98a8" } },
    x: { grid: { display: false }, ticks: { color: "#e6edf3" } } },
    plugins: { legend: { display: false } } });

  renderHeatmap(data);
  renderTrendControls(data);
}

function drawChart(id, type, data, options) {
  if (state.charts[id]) state.charts[id].destroy();
  state.charts[id] = new Chart($("#" + id), {
    type, data,
    options: { responsive: true, maintainAspectRatio: false, ...options },
  });
}

function heatColor(score) {
  if (score > 0) return "#3fb950";
  if (score < 0) return "#f85149";
  return "#6e7681";
}

function renderHeatmap(data) {
  const hm = $("#heatmap");
  hm.innerHTML = "";
  const table = el("table", { class: "hm-table" });
  const head = el("tr", {}, el("th", { class: "rowh" }, "Leader"));
  data.categories.forEach((c) => head.append(el("th", {}, c)));
  table.append(head);
  data.leaders.forEach((l) => {
    const row = el("tr", {}, el("td", { class: "rowh" }, l.name));
    data.categories.forEach((c) => {
      const s = l.categories[c].score;
      const conf = l.categories[c].confidence;
      const alpha = 0.25 + 0.75 * (conf / 100);
      row.append(el("td", { class: "hm-cell", style: `background:${heatColor(s)};opacity:${alpha}`,
        title: `${c}: ${scoreLabel(s)} (${conf}% confidence)` }, scoreLabel(s)));
    });
    table.append(row);
  });
  hm.append(table);
}

function renderTrendControls(data) {
  const ls = $("#trend-leader");
  const cs = $("#trend-category");
  ls.innerHTML = ""; cs.innerHTML = "";
  data.leaders.forEach((l) => ls.append(el("option", { value: l.id }, l.name)));
  cs.append(el("option", { value: "" }, "All categories"));
  data.categories.forEach((c) => cs.append(el("option", { value: c }, c)));
  ls.onchange = cs.onchange = drawTrend;
  drawTrend();
}

async function drawTrend() {
  const lid = $("#trend-leader").value;
  const cat = $("#trend-category").value;
  if (!lid) return;
  let path = "/api/compare/trend/" + lid;
  if (cat) path += "?category=" + encodeURIComponent(cat);
  const rows = await api(path);

  const byCat = {};
  rows.forEach((r) => (byCat[r.category] ||= []).push(r));
  const palette = ["#4f9cf9", "#3fb950", "#f85149", "#d29922", "#a371f7", "#39c5cf", "#db6d28", "#ec6cb9", "#8b949e", "#58a6ff"];
  const labels = [...new Set(rows.map((r) => (r.at || "").slice(0, 19)))];
  const datasets = Object.entries(byCat).map(([c, arr], i) => ({
    label: c, data: arr.map((r) => r.score), borderColor: palette[i % palette.length],
    backgroundColor: palette[i % palette.length] + "33", tension: 0.3, pointRadius: 4,
  }));

  drawChart("chart-trend", "line", { labels, datasets }, {
    scales: { y: { min: -1.2, max: 1.2, ticks: { stepSize: 1, color: "#8b98a8" }, grid: { color: "#2d3a48" } },
      x: { ticks: { color: "#8b98a8", maxRotation: 0, callback: (v, i) => labels[i]?.slice(0, 10) }, grid: { display: false } } },
    plugins: { legend: { labels: { color: "#e6edf3", boxWidth: 12, font: { size: 10 } } } },
  });
}

// ---------- methodology ----------
async function renderMethodology() {
  const m = await api("/api/scoring/methodology");
  const root = $("#methodology");
  root.innerHTML = "";
  root.append(el("div", { class: "card" },
    el("h2", {}, "Scoring principle"),
    el("p", { class: "principle" }, m.principle),
    el("p", { class: "muted" }, m.notes.join(" "))));

  const tw = el("div", { class: "card" }, el("h2", {}, "Trust & Confidence weights"));
  const twTable = el("table", {});
  Object.entries(m.trust_weights).forEach(([k, v]) =>
    twTable.append(el("tr", {},
      el("td", {}, k.replace(/_/g, " ")),
      el("td", {}, (v * 100) + "%",
        el("span", { class: "weight-bar", style: `width:${v * 200}px` })))));
  tw.append(twTable);
  root.append(tw);

  const ec = el("div", { class: "card" },
    el("h2", {}, "Evidence classification weights"),
    el("p", { class: "muted" }, "Intrinsic reliability (0–1) applied to each evidence record."));
  const ecTable = el("table", {}, el("tr", {}, el("th", {}, "Classification"), el("th", {}, "Weight")));
  Object.entries(m.evidence_classification_weights).forEach(([k, v]) =>
    ecTable.append(el("tr", {}, el("td", {}, k), el("td", {}, v.toFixed(2)))));
  ec.append(ecTable);
  root.append(ec);

  const sr = el("div", { class: "card" },
    el("h2", {}, "Source reliability ratings"),
    el("p", { class: "muted" }, `LLM scoring: ${m.llm.enabled ? "ENABLED (" + m.llm.model + ")" : "disabled — deterministic engine in use"}.`));
  const srTable = el("table", {}, el("tr", {}, el("th", {}, "Source"), el("th", {}, "Rating")));
  Object.entries(m.source_ratings).sort((a, b) => b[1] - a[1]).forEach(([k, v]) =>
    srTable.append(el("tr", {}, el("td", {}, k), el("td", {}, v.toFixed(2)))));
  sr.append(srTable);
  root.append(sr);
}

// ====================== Sources ======================
async function renderSources() {
  const d = await api("/api/sources");
  const root = $("#sources");
  root.innerHTML = "";
  root.append(el("div", { class: "card" },
    el("h2", {}, "Sources & feeds"),
    el("p", { class: "principle" }, d.principle)));

  // LLM
  root.append(el("div", { class: "card" },
    el("h2", {}, "AI model"),
    el("p", { class: "muted" }, `Endpoint: ${d.llm.provider_base_url}`),
    el("p", {}, d.llm.enabled ? `Active model: ${d.llm.model}` : "No LLM key set (classification/scoring disabled)."),
    el("p", { class: "muted" }, d.llm.note)));

  const statusDot = (active) => el("span", { style: `color:${active ? "var(--pos)" : "var(--warn)"}` }, active ? "● active" : "○ inactive");

  // Evidence collectors
  const ec = el("div", { class: "card" }, el("h2", {}, "Evidence collectors (Leaders)"));
  const ecT = el("table", {}, el("tr", {}, el("th", {}, "Source"), el("th", {}, "Type"), el("th", {}, "Key"), el("th", {}, "Status"), el("th", {}, "Link")));
  d.evidence_collectors.forEach((c) =>
    ecT.append(el("tr", {},
      el("td", {}, c.name),
      el("td", {}, c.kind),
      el("td", {}, c.keyless ? "keyless" : "needs key"),
      el("td", {}, statusDot(c.active)),
      el("td", {}, c.url ? el("a", { href: c.url, target: "_blank", style: "color:var(--accent)" }, "open") : "—"))));
  ec.append(ecT);
  root.append(ec);

  // News feeds
  const nf = el("div", { class: "card" }, el("h2", {}, `News feeds (${d.news_feeds.length}) — click to verify`));
  const nfT = el("table", {}, el("tr", {}, el("th", {}, "Outlet"), el("th", {}, "Region"), el("th", {}, "Rating"), el("th", {}, "Feed URL")));
  d.news_feeds.forEach((f) =>
    nfT.append(el("tr", {},
      el("td", {}, f.name + (f.state_media ? " ⚑ state media" : "")),
      el("td", {}, f.region),
      el("td", {}, f.rating.toFixed(2)),
      el("td", {}, el("a", { href: f.url, target: "_blank", style: "color:var(--accent)" }, f.url)))));
  nf.append(nfT);
  root.append(nf);

  // Country data providers
  Object.entries(d.country_data).forEach(([provider, inds]) => {
    if (!inds.length) return;
    const c = el("div", { class: "card" }, el("h2", {}, `${provider} (${inds.length} indicators)`));
    const t = el("table", {}, el("tr", {}, el("th", {}, "Indicator"), el("th", {}, "Category"), el("th", {}, "Dataset / link")));
    inds.forEach((i) =>
      t.append(el("tr", {},
        el("td", {}, i.name + ` (${i.unit})`),
        el("td", {}, i.category),
        el("td", {}, el("a", { href: i.url, target: "_blank", style: "color:var(--accent)" }, "open dataset")))));
    c.append(t);
    root.append(c);
  });

  // Pluggable (declared, not yet live)
  if (d.pluggable_indicators.length) {
    const p = el("div", { class: "card" },
      el("h2", {}, `Catalogued but not yet live (${d.pluggable_indicators.length})`),
      el("p", { class: "muted" }, "Declared for transparency; need a non-free or not-yet-wired source."));
    const t = el("table", {}, el("tr", {}, el("th", {}, "Indicator"), el("th", {}, "Category"), el("th", {}, "Intended source")));
    d.pluggable_indicators.forEach((i) =>
      t.append(el("tr", {}, el("td", {}, i.name), el("td", {}, i.category), el("td", {}, i.intended_source))));
    p.append(t);
    root.append(p);
  }

  // Source ratings
  const sr = el("div", { class: "card" },
    el("h2", {}, `Source reliability ratings (${d.source_ratings.length})`),
    el("p", { class: "muted" }, "Used to weight evidence. State-controlled outlets are flagged and down-weighted."));
  const srT = el("table", {}, el("tr", {}, el("th", {}, "Source"), el("th", {}, "Domain"), el("th", {}, "Rating")));
  d.source_ratings.forEach((r) =>
    srT.append(el("tr", {},
      el("td", {}, r.name + (r.state_media ? " ⚑" : "")),
      el("td", { class: "muted" }, r.domain),
      el("td", {}, r.rating.toFixed(2)))));
  sr.append(srT);
  root.append(sr);
}

// ====================== Speech Transcripts ======================
async function renderTranscripts() {
  const root = $("#transcripts-grid");
  root.innerHTML = "";
  
  try {
    const transcripts = await api("/api/transcripts");
    
    if (transcripts.length === 0) {
      root.append(el("div", { class: "empty" },
        el("h3", {}, "No transcripts yet"),
        el("p", { class: "muted" }, "Click '+ Add Transcript' to submit a video transcript manually.")));
      return;
    }
    
    transcripts.forEach((t) => {
      const card = el("div", { class: "leader-card" },
        el("div", { class: "lc-head" },
          el("h3", {}, t.title),
          el("div", { class: "sub" }, `${t.leader_name} · ${t.platform} · ${t.date || 'Unknown date'}`)),
        el("div", { class: "lc-body" },
          el("p", { class: "muted" }, t.transcript_text.substring(0, 200) + "..."),
          t.offense_categories ? el("div", { class: "tags" },
            ...t.offense_categories.split(",").map((cat) => el("span", { class: "tag" }, cat.trim()))) : null,
        el("div", { class: "lc-actions" },
          el("a", { href: t.video_url, target: "_blank", class: "btn secondary" }, "Watch Video"),
          el("button", { class: "btn secondary", onclick: () => viewTranscript(t.id) }, "View Full Transcript"))));
      root.append(card);
    });
  } catch (e) {
    root.append(el("div", { class: "empty" },
      el("h3", {}, "Error loading transcripts"),
      el("p", { class: "muted" }, String(e))));
  }
}

function viewTranscript(id) {
  // TODO: Implement modal to view full transcript
  alert("Full transcript view coming soon!");
}

// Add transcript button
$("#add-transcript-btn").addEventListener("click", () => {
  // TODO: Implement submission form
  alert("Manual transcript submission coming soon!");
});

// ====================== Videos ======================
function renderVideos() {
  // Videos are already embedded in HTML, no dynamic rendering needed
}

// ====================== Financial Transparency ======================
async function renderFinancial() {
  const root = $("#financial-grid");
  root.innerHTML = "";
  
  try {
    const financialData = await api("/api/financial");
    
    if (financialData.length === 0) {
      root.append(el("div", { class: "empty" },
        el("h3", {}, "No financial data yet"),
        el("p", { class: "muted" }, "Financial transparency data coming soon. This will show salary, assets, and wealth vs. legitimate income.")));
      return;
    }
    
    // Group by leader
    const byLeader = {};
    financialData.forEach((d) => {
      if (!byLeader[d.leader_id]) byLeader[d.leader_id] = [];
      byLeader[d.leader_id].push(d);
    });
    
    Object.entries(byLeader).forEach(([leaderId, data]) => {
      const latest = data[0]; // Most recent year
      const card = el("div", { class: "leader-card" },
        el("div", { class: "lc-head" },
          el("h3", {}, latest.leader_name),
          el("div", { class: "sub" }, `Year: ${latest.year}`)),
        el("div", { class: "lc-body" },
          el("div", { class: "stat-row" },
            el("span", { class: "label" }, "Annual Salary:"),
            el("span", { class: "value" }, latest.annual_salary ? `$${latest.annual_salary.toLocaleString()}` : "N/A")),
          el("div", { class: "stat-row" },
            el("span", { class: "label" }, "Net Worth:"),
            el("span", { class: "value" }, latest.net_worth ? `$${latest.net_worth.toLocaleString()}` : "N/A")),
          el("div", { class: "stat-row" },
            el("span", { class: "label" }, "Total Assets:"),
            el("span", { class: "value" }, latest.total_assets ? `$${latest.total_assets.toLocaleString()}` : "N/A")),
          el("div", { class: "stat-row" },
            el("span", { class: "label" }, "Total Debt:"),
            el("span", { class: "value" }, latest.total_debt ? `$${latest.total_debt.toLocaleString()}` : "N/A")),
          latest.source ? el("div", { class: "muted", style: "margin-top:8px" }, `Source: ${latest.source}`) : null,
        el("div", { class: "lc-actions" },
          el("button", { class: "btn secondary", onclick: () => alert("Detailed financial view coming soon!") }, "View Details"))));
      root.append(card);
    });
  } catch (e) {
    root.append(el("div", { class: "empty" },
      el("h3", {}, "Error loading financial data"),
      el("p", { class: "muted" }, String(e))));
  }
}

// ====================== Official Government Data ======================
async function renderOfficial() {
  const root = $("#official-grid");
  root.innerHTML = "";
  
  try {
    // Get all leaders to show which have official data
    const leaders = await api("/api/leaders");
    
    if (leaders.length === 0) {
      root.append(el("div", { class: "empty" },
        el("h3", {}, "No leaders yet"),
        el("p", { class: "muted" }, "Official government data coming soon. This will show voting records, proposals, and expenses from official APIs.")));
      return;
    }
    
    // Show leaders grouped by country
    const byCountry = {};
    leaders.forEach((l) => {
      if (!byCountry[l.country]) byCountry[l.country] = [];
      byCountry[l.country].push(l);
    });
    
    Object.entries(byCountry).forEach(([country, countryLeaders]) => {
      const section = el("div", { class: "country-section" },
        el("h3", {}, country),
        el("div", { class: "leader-grid" }, countryLeaders.map((l) =>
          el("div", { class: "leader-card" },
            el("div", { class: "lc-head" },
              el("h3", {}, l.name),
              el("div", { class: "sub" }, l.country)),
            el("div", { class: "lc-body" },
              el("div", { class: "stat-row" },
                el("span", { class: "label" }, "Office:"),
                el("span", { class: "value" }, l.country)),
              el("div", { class: "stat-row" },
                el("span", { class: "label" }, "Political Affiliation:"),
                el("span", { class: "value" }, l.political_affiliation || "N/A")),
              el("div", { class: "muted", style: "margin-top:8px" }, "Official data available for:"),
              el("ul", { style: "margin:8px 0 0 20px" },
                el("li", {}, "Voting Records"),
                el("li", {}, "Proposals"),
                el("li", {}, "Expenses")),
            el("div", { class: "lc-actions" },
              el("button", { class: "btn secondary", onclick: () => showOfficialData(l.id, l.name) }, "View Official Data"))))));
      root.append(section);
    });
  } catch (e) {
    root.append(el("div", { class: "empty" },
      el("h3", {}, "Error loading official data"),
      el("p", { class: "muted" }, String(e))));
  }
}

async function showOfficialData(leaderId, leaderName) {
  const panel = $("#voting-panel");
  const modal = $("#voting-modal");
  
  panel.innerHTML = el("div", { class: "loading" }, "Loading official data...").outerHTML;
  modal.classList.add("show");
  
  try {
    // Fetch voting records, proposals, and expenses
    const [votingRecords, proposals, expenses] = await Promise.all([
      api(`/api/voting/leader/${leaderId}`).catch(() => ({ total: 0, records: [] })),
      api(`/api/proposals/leader/${leaderId}`).catch(() => ({ total: 0, proposals: [] })),
      api(`/api/expenses/leader/${leaderId}`).catch(() => ({ total: 0, expenses: [] }))
    ]);
    
    panel.innerHTML = "";
    panel.append(el("div", { class: "modal-header" },
      el("h2", {}, `Official Data: ${leaderName}`),
      el("button", { class: "btn secondary", onclick: () => modal.classList.remove("show") }, "Close")));
    
    // Voting Records
    panel.append(el("h3", {}, "Voting Records"));
    if (votingRecords.total > 0) {
      panel.append(el("div", { class: "data-list" },
        votingRecords.records.map((r) =>
          el("div", { class: "data-item" },
            el("div", { class: "data-title" }, r.proposal_title || "Unknown Proposal"),
            el("div", { class: "data-meta" }, `Vote: ${r.vote} | Date: ${new Date(r.vote_date).toLocaleDateString()}`),
            r.source_url ? el("a", { href: r.source_url, target: "_blank", class: "btn secondary" }, "View Source") : null))));
    } else {
      panel.append(el("p", { class: "muted" }, "No voting records available"));
    }
    
    // Proposals
    panel.append(el("h3", {}, "Proposals"));
    if (proposals.total > 0) {
      panel.append(el("div", { class: "data-list" },
        proposals.proposals.map((p) =>
          el("div", { class: "data-item" },
            el("div", { class: "data-title" }, p.title),
            el("div", { class: "data-meta" }, `Type: ${p.type} | Status: ${p.status}`),
            p.presentation_date ? el("div", { class: "data-meta" }, `Date: ${new Date(p.presentation_date).toLocaleDateString()}`) : null,
            p.source_url ? el("a", { href: p.source_url, target: "_blank", class: "btn secondary" }, "View Source") : null))));
    } else {
      panel.append(el("p", { class: "muted" }, "No proposals available"));
    }
    
    // Expenses
    panel.append(el("h3", {}, "Expenses"));
    if (expenses.total > 0) {
      panel.append(el("div", { class: "data-list" },
        expenses.expenses.map((e) =>
          el("div", { class: "data-item" },
            el("div", { class: "data-title" }, e.description || "Unknown Expense"),
            el("div", { class: "data-meta" }, `Amount: ${e.currency} ${e.amount?.toLocaleString()} | Type: ${e.expense_type}`),
            e.supplier_name ? el("div", { class: "data-meta" }, `Supplier: ${e.supplier_name}`) : null,
            e.receipt_url ? el("a", { href: e.receipt_url, target: "_blank", class: "btn secondary" }, "View Receipt") : null))));
    } else {
      panel.append(el("p", { class: "muted" }, "No expense records available"));
    }
    
  } catch (e) {
    panel.innerHTML = el("div", { class: "empty" },
      el("h3", {}, "Error loading official data"),
      el("p", { class: "muted" }, String(e))).outerHTML;
  }
}

// ====================== Public Impact ======================
const countryState = { selected: new Set(), initialized: false, sub: "admins" };
const PERF_CATS = ["Security", "Education", "Health", "Economy", "Democracy", "Environment"];

function setupCountrySubtabs() {
  $$("#country-subtabs .subtab").forEach((b) =>
    b.addEventListener("click", () => {
      $$("#country-subtabs .subtab").forEach((x) => x.classList.remove("active"));
      b.classList.add("active");
      countryState.sub = b.dataset.sub;
      const isList = b.dataset.sub === "admins";
      $("#country-grid").style.display = isList ? "grid" : "none";
      $("#country-dash").style.display = isList ? "none" : "block";
      $("#country-controls").style.display = isList ? "flex" : "none";
      if (isList) loadAdministrations();
      else renderDashboard(b.dataset.sub);
    }));
}

async function renderCountryTab() {
  if (!countryState.initialized) {
    setupCountrySubtabs();
    const opts = await api("/api/country/filters/options");
    const cf = $("#country-filter");
    cf.append(el("option", { value: "" }, "All countries"));
    opts.countries.forEach((c) => cf.append(el("option", { value: c }, c)));
    const sortLabels = {
      name: "Name", leader_impact_desc: "Highest Leader Impact",
      citizen_reality_desc: "Highest Citizen Reality", best_economy: "Best Economy",
      best_health: "Best Healthcare", best_education: "Best Education",
      best_security: "Best Security", best_housing: "Best Housing",
      best_cost_of_living: "Best Cost of Living", best_green_energy: "Best Green Energy",
      most_improved: "Most Improved", most_declined: "Most Declined",
    };
    const cs = $("#country-sort");
    opts.sorts.forEach((s) => cs.append(el("option", { value: s }, sortLabels[s] || s)));
    cs.value = "leader_impact_desc";
    cf.onchange = cs.onchange = loadAdministrations;
    countryState.initialized = true;
  }
  await loadAdministrations();
}

async function loadAdministrations() {
  const p = new URLSearchParams();
  const c = $("#country-filter").value;
  if (c) p.set("country", c);
  p.set("sort", $("#country-sort").value);
  const admins = await api("/api/country/administrations?" + p.toString());
  const grid = $("#country-grid");
  grid.innerHTML = "";
  admins.forEach((a) => grid.append(adminCard(a)));
}

function gauge(label, value, range, delta) {
  // Handle both number (list API) and object (detail API) formats
  const numValue = typeof value === "object" ? value?.score : value;
  const numDelta = typeof value === "object" ? value?.delta : delta;
  const v = numValue == null ? "—" : numValue;
  let color;
  if (range === "lis") {
    color = totalColor(numValue || 0);
  } else if (numDelta != null) {
    // Delta is already direction-adjusted: positive = improvement (green), negative = decline (red)
    color = numDelta >= 0 ? "var(--pos)" : "var(--neg)";
  } else {
    // Fallback to absolute score coloring
    color = numValue == null ? "#8b98a8" : numValue >= 60 ? "#3fb950" : numValue >= 40 ? "#d29922" : "#f85149";
  }
  return el("div", { class: "gauge" },
    el("div", { class: "gauge-val", style: `color:${color}` }, v === "—" ? v : (range === "lis" && numValue > 0 ? "+" + numValue : "" + numValue)),
    el("div", { class: "muted" }, label));
}

function adminCard(a) {
  const card = el("div", { class: "leader-card" });
  const picked = countryState.selected.has(a.id);
  card.append(el("div", { class: "lc-head" },
    el("div", {},
      el("h3", {}, a.leader_name),
      el("div", { class: "sub" }, `${a.country} · ${a.office || ""}`),
      el("div", { class: "sub" }, `${a.start} → ${a.end || "present"}`)),
    el("span", { class: "pick" + (picked ? " selected" : ""), onclick: (e) => { e.stopPropagation(); toggleAdminCompare(a.id); } },
      picked ? "✓ compare" : "+ compare")));
  if (!a.has_data) {
    card.append(el("div", { class: "sub", style: "margin:10px 0;color:var(--warn)" }, "No data ingested yet"));
    const b = el("button", { class: "btn", onclick: (e) => { e.stopPropagation(); ingestAdmin(a.id, b); } }, "Ingest World Bank data");
    card.append(b);
  } else {
    card.append(el("div", { class: "gauges" },
      gauge("Citizen Reality", a.citizen_reality_score, null, a.citizen_reality_delta),
      gauge("Leader Impact", a.leader_impact_score, "lis", null),
      gauge("Green Energy", a.green_energy_index, null, a.green_energy_delta)));
    card.append(el("div", { class: "sub", style: "margin-top:8px" }, `Confidence ${a.confidence}% · ${a.coverage.available} indicators`));
  }
  card.onclick = () => openAdministration(a.id);
  return card;
}

async function ingestAdmin(id, btn) {
  btn.disabled = true; btn.textContent = "Ingesting World Bank data…";
  try {
    const res = await fetch(API + "/api/country/ingest/" + id, { method: "POST" }).then((r) => r.json());
    btn.textContent = `Ingested ${res.values_added} values`;
    await loadAdministrations();
  } catch (e) { btn.textContent = "Error — retry"; btn.disabled = false; }
}

async function openAdministration(id) {
  const d = await api("/api/country/administration/" + id);
  const panel = $("#drawer-panel");
  panel.innerHTML = "";
  panel.append(el("button", { class: "close", onclick: closeDrawer }, "×"));
  const a = d.administration;
  panel.append(el("div", { class: "detail-head" },
    el("h2", {}, a.leader_name),
    el("div", { class: "sub" }, `${a.country} · ${a.office || ""} · ${a.party || ""}`),
    el("div", { class: "sub" }, `${a.start} → ${a.end || "present"}` +
      (a.predecessor ? ` · after ${a.predecessor}` : ""))));

  if (!d.indicators.length) {
    const b = el("button", { class: "btn", onclick: () => ingestAdmin(id, b) }, "Ingest World Bank data");
    panel.append(el("p", { class: "sub", style: "margin:14px 0" }, "No indicator data yet."), b);
    $("#drawer").classList.add("show"); $("#overlay").classList.add("show");
    return;
  }

  panel.append(el("div", { class: "gauges", style: "margin:16px 0" },
    gauge("Citizen Reality", d.citizen_reality_score, null, d.citizen_reality_delta),
    gauge("Leader Impact", d.leader_impact_score, "lis", null),
    gauge("Green Energy", d.green_energy_index, null, d.green_energy_delta),
    gauge("Confidence", d.confidence)));

  if (d.shocks_during_office.length)
    panel.append(el("div", { class: "cat-reason" }, "Global context during term: " + d.shocks_during_office.join(", ") +
      ". Impact is estimated, not attributed as direct causation."));

  // AI summary
  const sumBox = el("div", { class: "cat-reason", style: "white-space:pre-line" }, "Generating summary…");
  panel.append(el("h3", { style: "margin-top:16px" }, "Administration summary"), sumBox);
  api("/api/country/administration/" + id + "/summary").then((s) => {
    sumBox.textContent = s.summary + (s.generated_by ? `\n\n[${s.generated_by}]` : "");
  });

  // Before vs After bars + radar
  panel.append(el("h3", { style: "margin-top:18px" }, "Before vs after (by category)"));
  panel.append(el("div", { class: "chart-card" }, el("canvas", { id: "c-beforeafter" })));
  panel.append(el("div", { class: "chart-card" }, el("canvas", { id: "c-radar2" })));

  const cats = Object.keys(d.category_scores);
  setTimeout(() => {
    drawChart("c-beforeafter", "bar", {
      labels: cats,
      datasets: [
        { label: "Baseline", data: cats.map((c) => round1(d.category_scores[c].score - (d.category_scores[c].delta || 0))), backgroundColor: "#8b98a8" },
        { label: "Administration", data: cats.map((c) => d.category_scores[c].score), backgroundColor: "#4f9cf9" },
      ],
    }, { scales: { y: { min: 0, max: 100, grid: { color: "#2d3a48" }, ticks: { color: "#8b98a8" } }, x: { ticks: { color: "#e6edf3" } } }, plugins: { legend: { labels: { color: "#e6edf3" } } } });
    drawChart("c-radar2", "radar", {
      labels: cats,
      datasets: [{ label: "Category score", data: cats.map((c) => d.category_scores[c].score), borderColor: "#3fb950", backgroundColor: "#3fb95022" }],
    }, { scales: { r: { min: 0, max: 100, grid: { color: "#2d3a48" }, angleLines: { color: "#2d3a48" }, pointLabels: { color: "#e6edf3", font: { size: 10 } }, ticks: { color: "#8b98a8", backdropColor: "transparent" } } }, plugins: { legend: { labels: { color: "#e6edf3" } } } });
  }, 50);

  // Benchmarks: admin vs country historical vs regional average
  panel.append(el("h3", { style: "margin-top:18px" }, "Benchmarks (vs history & region)"));
  panel.append(el("div", { class: "chart-card" }, el("canvas", { id: "c-bench" })));
  api("/api/country/administration/" + id + "/benchmark").then((bm) => {
    const bc = bm.categories;
    drawChart("c-bench", "radar", {
      labels: bc,
      datasets: [
        { label: a.leader_name, data: bc.map((c) => bm.administration_scores[c] ?? 0), borderColor: "#4f9cf9", backgroundColor: "#4f9cf922" },
        { label: "Country historical avg", data: bc.map((c) => bm.country_historical_average[c] ?? 0), borderColor: "#d29922", backgroundColor: "#d2992222" },
        { label: `${bm.region} regional avg`, data: bc.map((c) => bm.regional_average[c] ?? 0), borderColor: "#a371f7", backgroundColor: "#a371f722" },
      ],
    }, { scales: { r: { min: 0, max: 100, grid: { color: "#2d3a48" }, angleLines: { color: "#2d3a48" }, pointLabels: { color: "#e6edf3", font: { size: 10 } }, ticks: { color: "#8b98a8", backdropColor: "transparent" } } }, plugins: { legend: { labels: { color: "#e6edf3", boxWidth: 12, font: { size: 10 } } } } });
  });

  // Indicator table with sources + CSV
  panel.append(el("div", { style: "display:flex;justify-content:space-between;align-items:center;margin-top:18px" },
    el("h3", {}, "Indicators & sources"),
    el("a", { class: "btn secondary", href: API + "/api/country/administration/" + id + "/export.csv" }, "Download CSV")));
  const tbl = el("table", { class: "ind-table" },
    el("tr", {}, el("th", {}, "Indicator"), el("th", {}, "Baseline"), el("th", {}, "Admin"), el("th", {}, "Δ"), el("th", {}, "Source")));
  d.indicators.forEach((i) => {
    // Delta is already direction-adjusted (normalized score difference)
    // Positive delta = improvement (green), Negative delta = decline (red)
    const color = i.delta == null ? "#8b98a8" : (i.delta >= 0 ? "var(--pos)" : "var(--neg)");
    tbl.append(el("tr", {},
      el("td", {}, i.name + ` (${i.unit})`),
      el("td", {}, fmt(i.baseline_mean)),
      el("td", {}, fmt(i.admin_mean)),
      el("td", { style: `color:${color}` }, i.delta == null ? "—" : (i.delta > 0 ? "+" : "") + i.delta),
      el("td", {}, i.source_url ? el("a", { href: i.source_url, target: "_blank", style: "color:var(--accent)" }, i.source_name) : i.source_name)));
  });
  panel.append(el("div", { style: "overflow-x:auto" }, tbl));

  $("#drawer").classList.add("show");
  $("#overlay").classList.add("show");
}

function toggleAdminCompare(id) {
  if (countryState.selected.has(id)) countryState.selected.delete(id);
  else if (countryState.selected.size < 10) countryState.selected.add(id);
  loadAdministrations();
  if (countryState.selected.size >= 2) openAdminCompare();
}

async function openAdminCompare() {
  const ids = [...countryState.selected];
  const d = await api("/api/country/compare?" + ids.map((i) => "ids=" + i).join("&"));
  const panel = $("#drawer-panel");
  panel.innerHTML = "";
  panel.append(el("button", { class: "close", onclick: closeDrawer }, "×"));
  panel.append(el("h2", {}, "Administration comparison"));
  const admins = d.administrations;
  const palette = ["#4f9cf9", "#3fb950", "#f85149", "#d29922", "#a371f7"];

  panel.append(el("div", { class: "chart-card" }, el("h3", {}, "Citizen Reality / Leader Impact / Green Energy"), el("canvas", { id: "c-cmp-bars" })));
  panel.append(el("div", { class: "chart-card" }, el("h3", {}, "Category scores"), el("canvas", { id: "c-cmp-radar" })));

  setTimeout(() => {
    drawChart("c-cmp-bars", "bar", {
      labels: admins.map((a) => a.administration.leader_name),
      datasets: [
        { label: "Citizen Reality", data: admins.map((a) => a.citizen_reality_score), backgroundColor: admins.map((a) => a.citizen_reality_delta >= 0 ? "#3fb950" : "#f85149") },
        { label: "Leader Impact", data: admins.map((a) => a.leader_impact_score), backgroundColor: admins.map((a) => totalColor(a.leader_impact_score)) },
        { label: "Green Energy", data: admins.map((a) => a.green_energy_index), backgroundColor: admins.map((a) => a.green_energy_delta >= 0 ? "#3fb950" : "#f85149") },
      ],
    }, { scales: { y: { grid: { color: "#2d3a48" }, ticks: { color: "#8b98a8" } }, x: { ticks: { color: "#e6edf3" } } }, plugins: { legend: { labels: { color: "#e6edf3" } } } });
    drawChart("c-cmp-radar", "radar", {
      labels: PERF_CATS,
      datasets: admins.map((a, i) => ({
        label: a.administration.leader_name,
        data: PERF_CATS.map((c) => (a.category_scores[c] ? a.category_scores[c].score : 0)),
        borderColor: palette[i % palette.length], backgroundColor: palette[i % palette.length] + "22",
      })),
    }, { scales: { r: { min: 0, max: 100, grid: { color: "#2d3a48" }, angleLines: { color: "#2d3a48" }, pointLabels: { color: "#e6edf3", font: { size: 10 } }, ticks: { color: "#8b98a8", backdropColor: "transparent" } } }, plugins: { legend: { labels: { color: "#e6edf3" } } } });
  }, 50);

  $("#drawer").classList.add("show");
  $("#overlay").classList.add("show");
}

async function renderDashboard(which) {
  const admins = (await api("/api/country/administrations?sort=name")).filter((a) => a.has_data);
  const dash = $("#country-dash");
  dash.innerHTML = "";
  if (!admins.length) { dash.append(el("div", { class: "empty" }, "No administrations with data yet. Ingest data on the Administrations tab.")); return; }

  if (which === "heatmap") {
    dash.append(el("div", { class: "dash-card" },
      el("h3", {}, "Category scores across administrations"),
      buildHeatmap(admins)));
  } else if (which === "green") {
    dash.append(el("div", { class: "dash-card" }, el("h3", {}, "Green Energy Index by administration"), el("canvas", { id: "d-green" })));
    dash.append(el("div", { class: "dash-card" }, el("h3", {}, "Citizen Reality vs Green Energy"), el("canvas", { id: "d-green-scatter" })));
    setTimeout(() => {
      const withGei = admins.filter((a) => a.green_energy_index != null);
      drawChart("d-green", "bar", {
        labels: withGei.map((a) => a.leader_name),
        datasets: [{ label: "Green Energy Index", data: withGei.map((a) => a.green_energy_index), backgroundColor: withGei.map((a) => a.green_energy_delta >= 0 ? "#3fb950" : "#f85149") }],
      }, barOpts(0, 100));
      drawChart("d-green-scatter", "bar", {
        labels: withGei.map((a) => a.leader_name),
        datasets: [
          { label: "Green Energy", data: withGei.map((a) => a.green_energy_index), backgroundColor: withGei.map((a) => a.green_energy_delta >= 0 ? "#3fb950" : "#f85149") },
          { label: "Citizen Reality", data: withGei.map((a) => a.citizen_reality_score), backgroundColor: withGei.map((a) => a.citizen_reality_delta >= 0 ? "#3fb950" : "#f85149") },
        ],
      }, barOpts(0, 100));
    }, 50);
  } else if (which === "reality") {
    dash.append(el("div", { class: "dash-card" }, el("h3", {}, "Citizen Reality Score by administration"), el("canvas", { id: "d-crs" })));
    dash.append(el("div", { class: "dash-card" }, el("h3", {}, "Leader Impact Score (−100..+100)"), el("canvas", { id: "d-lis" })));
    setTimeout(() => {
      const crs = admins.filter((a) => a.citizen_reality_score != null).sort((a, b) => b.citizen_reality_score - a.citizen_reality_score);
      drawChart("d-crs", "bar", {
        labels: crs.map((a) => a.leader_name),
        datasets: [{ label: "Citizen Reality Score", data: crs.map((a) => a.citizen_reality_score), backgroundColor: crs.map((a) => a.citizen_reality_delta >= 0 ? "#3fb950" : "#f85149") }],
      }, barOpts(0, 100));
      const lis = admins.filter((a) => a.leader_impact_score != null).sort((a, b) => b.leader_impact_score - a.leader_impact_score);
      drawChart("d-lis", "bar", {
        labels: lis.map((a) => a.leader_name),
        datasets: [{ label: "Leader Impact Score", data: lis.map((a) => a.leader_impact_score), backgroundColor: lis.map((a) => totalColor(a.leader_impact_score)) }],
      }, barOpts(-100, 100));
    }, 50);
  }
}

function barOpts(min, max) {
  return { scales: { y: { min, max, grid: { color: "#2d3a48" }, ticks: { color: "#8b98a8" } }, x: { ticks: { color: "#e6edf3", font: { size: 10 } } } }, plugins: { legend: { labels: { color: "#e6edf3" } } } };
}

function buildHeatmap(admins) {
  const table = el("table", { class: "hm-table" });
  const head = el("tr", {}, el("th", { class: "rowh" }, "Administration"));
  PERF_CATS.forEach((c) => head.append(el("th", {}, c)));
  table.append(head);
  admins.forEach((a) => {
    const row = el("tr", {}, el("td", { class: "rowh" }, `${a.leader_name} (${a.country})`));
    PERF_CATS.forEach((c) => {
      const s = a.category_scores[c];
      if (s == null) { row.append(el("td", {}, "—")); return; }
      const col = s >= 66 ? "#3fb950" : s >= 40 ? "#d29922" : "#f85149";
      row.append(el("td", { class: "hm-cell", style: `background:${col};opacity:${0.35 + 0.0065 * s}`, title: `${c}: ${s}` }, "" + Math.round(s)));
    });
    table.append(row);
  });
  return el("div", { style: "overflow-x:auto" }, table);
}

const round1 = (x) => Math.round(x * 10) / 10;
const fmt = (x) => (x == null ? "—" : x);

init();
