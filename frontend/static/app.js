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
  })
);

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

  const rescoreBtn = el("button", { class: "btn", onclick: () => rescore(id, rescoreBtn) },
    state.llm ? "Re-run AI scoring (LLM)" : "Re-run scoring (engine)");
  panel.append(rescoreBtn);

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
  state.leaders.forEach((l) => {
    const p = el("div", {
      class: "pick" + (state.selected.has(l.id) ? " selected" : ""),
      onclick: () => toggleSelect(l.id),
    }, l.name);
    box.append(p);
  });
  renderCompareCharts();
}

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

init();
