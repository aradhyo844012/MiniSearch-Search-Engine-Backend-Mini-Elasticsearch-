
import {
  searchDocuments,
  getStats,
  getDocument,
  API_BASE_URL
} from "./api.js";

// --------------------------------------------------
// 1. DOM HELPERS AND APPLICATION STATE
// --------------------------------------------------

const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => [...document.querySelectorAll(selector)];

const state = {
  view: "search",
  mode: "OR",
  limit: 10,
  offset: 0,
  query: "",
  totalHits: 0,
  results: [],
  lastSearch: null,
  stats: null,
  activity: [],
  history: [],
  currentDocument: "",
  suggestedQuery: "",
  originalQuery: ""
};

let searchRequestId = 0;
let documentRequestId = 0;
let statsRequestId = 0;
let lastDocumentTrigger = null;

const landing = $("#landingPage");
const shell = $("#appShell");
const toastRegion = $("#toastRegion");

// --------------------------------------------------
// 2. GENERAL UTILITIES
// --------------------------------------------------

function toast(message, type = "success") {
  if (!toastRegion) return;

  const node = document.createElement("div");
  node.className = `toast ${type === "error" ? "error" : ""}`;
  node.textContent = String(message);

  toastRegion.append(node);

  window.setTimeout(() => {
    node.remove();
  }, 3200);
}

function formatNumber(value) {
  const number = Number(value);

  return Number.isFinite(number)
    ? number.toLocaleString("en-IN")
    : "—";
}

function formatBytes(bytes) {
  const number = Number(bytes);

  if (!Number.isFinite(number) || number < 0) {
    return "—";
  }

  if (number < 1024) {
    return `${number} B`;
  }

  if (number < 1024 ** 2) {
    return `${(number / 1024).toFixed(1)} KB`;
  }

  if (number < 1024 ** 3) {
    return `${(number / 1024 ** 2).toFixed(1)} MB`;
  }

  return `${(number / 1024 ** 3).toFixed(2)} GB`;
}

function safeString(value, fallback = "") {
  if (value === null || value === undefined) {
    return fallback;
  }

  return String(value);
}

function formatLatency(value) {
  const number = Number(value);

  return Number.isFinite(number) && number >= 0
    ? `${number.toFixed(2)} ms`
    : "—";
}

function setText(selector, value) {
  const element = $(selector);

  if (element) {
    element.textContent = safeString(value);
  }
}

// --------------------------------------------------
// 3. LANDING PAGE AND WORKSPACE NAVIGATION
// --------------------------------------------------

function showWorkspace(view = "search") {
  landing.classList.add("hidden");
  shell.classList.remove("hidden");

  // Avoid loading stats twice when entering the workspace.
  switchView(view, { loadStats: false });

  window.scrollTo(0, 0);

  // One request updates both API status and index metrics.
  loadStats();
}

function showLanding() {
  shell.classList.add("hidden");
  landing.classList.remove("hidden");

  $("#sidebar").classList.remove("open");
  $("#sidebarBackdrop").classList.add("hidden");
  $("#mobileMenu").setAttribute("aria-expanded", "false");

  window.scrollTo(0, 0);
}

function switchView(view, options = {}) {
  const validViews = ["search", "index", "analytics"];

  if (!validViews.includes(view)) {
    view = "search";
  }

  state.view = view;

  $$(".view").forEach((element) => {
    element.classList.add("hidden");
  });

  $(`#${view}View`).classList.remove("hidden");

  $$(".nav-item[data-view]").forEach((element) => {
    element.classList.toggle(
      "active",
      element.dataset.view === view
    );
  });

  const names = {
    search: "Search",
    index: "Index status",
    analytics: "Analytics"
  };

  setText("#crumb", names[view]);

  $("#sidebar").classList.remove("open");
  $("#sidebarBackdrop").classList.add("hidden");
  $("#mobileMenu").setAttribute("aria-expanded", "false");

  if (view === "analytics") {
    renderAnalytics();
  }

  if (view === "index" && options.loadStats !== false) {
    loadStats();
  }
}

// --------------------------------------------------
// 4. API CONNECTION AND INDEX STATISTICS
// --------------------------------------------------

function setApiState(online, message = "") {
  const dot = $("#apiDot");

  dot.style.background = online
    ? "#20a879"
    : "#df626d";

  dot.style.boxShadow = online
    ? "0 0 0 3px #20a8791b"
    : "0 0 0 3px #df626d1b";

  setText(
    "#apiStatus",
    online ? "API connected" : "API unavailable"
  );

  setText(
    "#apiBaseLabel",
    API_BASE_URL.replace(/^https?:\/\//, "")
  );

  setText(
    "#searchEngineState",
    online ? "Connected" : "Offline"
  );

  setText("#topStatusLabel", online ? "Backend connected" : "Backend offline");
  const topDot = $("#topStatusDot");
  if (topDot) {
    topDot.style.background = online ? "#20a879" : "#df626d";
    topDot.style.boxShadow = online ? "0 0 0 3px #20a8791b" : "0 0 0 3px #df626d1b";
  }

  $("#healthIndicator").style.background = online
    ? "#20a879"
    : "#df626d";

  setText(
    "#healthTitle",
    online ? "Backend reachable" : "Cannot reach backend"
  );

  setText(
    "#healthDescription",
    message ||
      (online
        ? "The MiniSearch API responded successfully."
        : "Start the backend server and check the API base URL.")
  );
}

async function checkApi() {
  await loadStats();
}

async function loadStats() {
  const requestId = ++statsRequestId;

  try {
    const stats = await getStats();

    // Ignore an outdated response.
    if (requestId !== statsRequestId) return;

    if (!stats || typeof stats !== "object") {
      throw new Error("The backend returned invalid index statistics.");
    }

    state.stats = stats;

    renderStats(stats);
    setApiState(true);

  } catch (error) {
    if (requestId !== statsRequestId) return;

    state.stats = null;

    setApiState(false, error.message);
    renderStats(null);

    if (state.view === "index") {
      toast(error.message, "error");
    }
  }
}

function renderStats(stats) {
  const values = {
    snapshotDocs: stats
      ? formatNumber(stats.totalDocuments)
      : "—",

    snapshotTerms: stats
      ? formatNumber(stats.vocabularySize)
      : "—",

    snapshotSize: stats
      ? formatBytes(stats.indexSizeBytes)
      : "—",

    metricDocs: stats
      ? formatNumber(stats.totalDocuments)
      : "—",

    metricVocab: stats
      ? formatNumber(stats.vocabularySize)
      : "—",

    metricBytes: stats
      ? formatBytes(stats.indexSizeBytes)
      : "—",

    metricBuild:
      stats && Number.isFinite(Number(stats.buildTimeMs))
        ? `${Number(stats.buildTimeMs).toFixed(1)} ms`
        : "—",

    builtAtValue: stats?.builtAt
      ? new Date(stats.builtAt).toLocaleString()
      : "—"
  };

  Object.entries(values).forEach(([id, value]) => {
    const element = $(`#${id}`);

    if (element) {
      element.textContent = value;
    }
  });

  setText("#endpointValue", `${API_BASE_URL}/stats`);
  const hasDocuments = stats && Number(stats.totalDocuments) > 0;
  if (stats && !hasDocuments) {
    setText("#healthTitle", "No indexed documents reported");
    setText("#healthDescription", "The API is reachable, but the statistics report zero documents. Confirm the corpus and index build with the backend owner.");
    const healthDot = $("#healthIndicator");
    if (healthDot) healthDot.style.background = "#d5a044";
  }
}

// --------------------------------------------------
// 5. SEARCH LOADING AND ACTIVITY
// --------------------------------------------------

function setLoading(isLoading) {
  const button = $(".search-submit");

  button.disabled = isLoading;

  button.innerHTML = isLoading
    ? "Searching…"
    : 'Search <span>↵</span>';

  $("#searchStatus").classList.toggle(
    "hidden",
    !isLoading
  );

  setText(
    "#searchStatus",
    isLoading
      ? "Searching your indexed documents…"
      : ""
  );
}

function addActivity(entry) {
  state.activity.unshift(entry);

  if (state.activity.length > 100) {
    state.activity.length = 100;
  }

  if (
    entry.query &&
    !state.history.includes(entry.query)
  ) {
    state.history.unshift(entry.query);
  }

  state.history = state.history.slice(0, 6);

  renderRecent();

  if (state.view === "analytics") {
    renderAnalytics();
  }
}

// --------------------------------------------------
// 6. MAIN SEARCH FUNCTION
// --------------------------------------------------

async function runSearch(query, options = {}) {
  const clean = safeString(query).trim();

  if (!clean) {
    toast("Enter a search query first.", "error");
    $("#queryInput").focus();
    return;
  }

  const requestId = ++searchRequestId;

  const previousOffset = state.offset;

  if (Number.isInteger(options.offset)) {
    state.offset = Math.max(0, options.offset);
  } else if (!options.keepOffset) {
    state.offset = 0;
  }

  const requestedOffset = state.offset;
  const requestedMode = state.mode;
  const requestedLimit = state.limit;

  state.query = clean;
  state.suggestedQuery = "";

  $("#queryInput").value = clean;

  $("#correctionBanner").classList.add("hidden");

  setLoading(true);

  const started = performance.now();

  try {
    const response = await searchDocuments({
      query: clean,
      mode: requestedMode,
      limit: requestedLimit,
      offset: requestedOffset
    });

    // A newer search has already started.
    if (requestId !== searchRequestId) return;

    if (
      !response ||
      typeof response !== "object" ||
      !Array.isArray(response.results) ||
      !Number.isFinite(Number(response.totalHits)) ||
      Number(response.totalHits) < 0
    ) {
      throw new Error(
        "The backend returned an invalid search response."
      );
    }

    const elapsed = performance.now() - started;

    const results = response.results;

    const totalHits = Number(response.totalHits);

    const latencyValue = Number(response.latencyMs);

    const latency =
      Number.isFinite(latencyValue) && latencyValue >= 0
        ? latencyValue
        : elapsed;

    state.lastSearch = response;
    state.results = results;
    state.totalHits = totalHits;

    // Show a correction as a suggestion, not as an action
    // that claims to disable backend correction.
    const corrected = safeString(
      response.correctedQuery
    ).trim();

    if (
      corrected &&
      corrected.toLowerCase() !== clean.toLowerCase()
    ) {
      state.suggestedQuery = corrected;
      state.originalQuery = clean;

      setText("#correctedText", corrected);

      const banner = $("#correctionBanner");
      const description = banner.querySelector("small");
      const button = $("#useSuggestion");

      if (description) {
        description.textContent =
          "Choose a query to run again. Original-text search may still be corrected by the backend.";
      }

      if (button) button.textContent = "Search suggestion";

      banner.classList.remove("hidden");
    }

    addActivity({
      query: clean,
      mode: requestedMode,
      hits: totalHits,
      latency,
      status: totalHits ? "Results" : "No results",
      timestamp: new Date()
    });

    renderResults(response);

    setText(
      "#resultCount",
      `${formatNumber(totalHits)} ${
        totalHits === 1 ? "result" : "results"
      } found`
    );

    const firstResult = totalHits
      ? requestedOffset + 1
      : 0;

    const lastResult = Math.min(
      requestedOffset + requestedLimit,
      totalHits
    );

    setText(
      "#resultMeta",
      `${response.mode || requestedMode} mode · ${formatLatency(latency)} · ${firstResult}–${lastResult}`
    );

    if (state.view !== "search") {
      switchView("search");
    }

  } catch (error) {
    // Ignore errors from searches that are no longer current.
    if (requestId !== searchRequestId) return;

    state.offset = previousOffset;

    addActivity({
      query: clean,
      mode: requestedMode,
      hits: 0,
      latency: null,
      status: "Error",
      timestamp: new Date()
    });

    $("#resultsList").replaceChildren();

    const box = document.createElement("div");
    box.className = "welcome-results";

    const heading = document.createElement("h2");

    heading.textContent =
      error.code === "NETWORK_ERROR"
        ? "Backend connection failed"
        : "Search could not be completed";

    const paragraph = document.createElement("p");
    paragraph.textContent =
      error.message || "An unexpected error occurred.";

    const retryButton = document.createElement("button");
    retryButton.className = "btn btn-light";
    retryButton.textContent = "Retry search";

    retryButton.addEventListener("click", () => {
      runSearch(clean, {
        offset: requestedOffset
      });
    });

    box.append(heading, paragraph, retryButton);

    $("#resultsList").append(box);

    setText("#resultCount", "Search unavailable");
    setText("#resultMeta", error.code || "API error");

    $("#pagination").classList.add("hidden");

    toast(error.message, "error");

  } finally {
    // Only the latest search can change the loading state.
    if (requestId === searchRequestId) {
      setLoading(false);
    }
  }
}

// --------------------------------------------------
// 7. RESULT HIGHLIGHTING
// --------------------------------------------------

function appendHighlighted(parent, text, terms) {
  const source = safeString(text);

  const cleanTerms = [
    ...new Set(
      (Array.isArray(terms) ? terms : [])
        .map((term) => safeString(term).trim())
        .filter(Boolean)
    )
  ].sort((a, b) => b.length - a.length);

  if (!cleanTerms.length) {
    parent.textContent = source;
    return;
  }

  const escaped = cleanTerms
    .map((term) =>
      term.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")
    )
    .join("|");

  let regex;

  try {
    regex = new RegExp(`(${escaped})`, "gi");
  } catch {
    parent.textContent = source;
    return;
  }

  let cursor = 0;

  for (const match of source.matchAll(regex)) {
    const index = match.index ?? 0;

    if (index > cursor) {
      parent.append(
        document.createTextNode(
          source.slice(cursor, index)
        )
      );
    }

    const mark = document.createElement("mark");
    mark.textContent = match[0];

    parent.append(mark);

    cursor = index + match[0].length;
  }

  if (cursor < source.length) {
    parent.append(
      document.createTextNode(source.slice(cursor))
    );
  }
}

// --------------------------------------------------
// 8. RENDER SEARCH RESULTS
// --------------------------------------------------

function renderResults(response) {
  const list = $("#resultsList");

  list.replaceChildren();

  let results = [...state.results];

  // Keep backend relevance order unless the user
  // explicitly chooses title sorting.
  if ($("#sortSelect").value === "title") {
    results.sort((a, b) =>
      safeString(a.title).localeCompare(
        safeString(b.title)
      )
    );
  }

  if ($("#sortSelect").value === "score") {
    results.sort((a, b) => (Number(b.score) || 0) - (Number(a.score) || 0));
  }

  if (!results.length) {
    const empty = document.createElement("div");
    empty.className = "welcome-results";

    const icon = document.createElement("div");
    icon.className = "welcome-symbol";
    icon.textContent = "⌕";

    const heading = document.createElement("h2");
    heading.textContent =
      `No documents match “${safeString(
        response.query || state.query
      )}”`;

    const paragraph = document.createElement("p");
    paragraph.textContent =
      "Try a different phrase, use OR mode, or search for fewer specific terms.";

    const button = document.createElement("button");
    button.className = "btn btn-light";
    button.textContent = "Switch to OR mode";

    button.addEventListener("click", () => {
      state.mode = "OR";
      updateModeButtons();
      runSearch(state.query);
    });

    empty.append(icon, heading, paragraph, button);
    list.append(empty);

  } else {
    results.forEach((result) => {
      const card = document.createElement("article");
      card.className = "result-card";

      const head = document.createElement("div");
      head.className = "result-head";

      const title = document.createElement("a");
      title.href = "#";
      title.className = "result-title";

      const docId = safeString(result.docId);

      title.textContent =
        safeString(result.title) || `Document ${docId}`;

      title.addEventListener("click", (event) => {
        event.preventDefault();
        openDocument(docId);
      });

      const score = document.createElement("span");
      score.className = "score-pill";

      const scoreValue = Number(result.score);

      score.textContent =
        `Score ${
          Number.isFinite(scoreValue)
            ? scoreValue.toFixed(2)
            : "—"
        }`;

      head.append(title, score);

      const path = document.createElement("div");
      path.className = "result-path";
      path.textContent = `DOC ID · ${docId}`;

      const snippet = document.createElement("div");
      snippet.className = "result-snippet";

      appendHighlighted(
        snippet,
        result.snippet || "No preview available.",
        result.matchedTerms || []
      );

      const foot = document.createElement("div");
      foot.className = "result-foot";

      const terms = document.createElement("div");
      terms.className = "matched-terms";

      const matchedTerms = Array.isArray(result.matchedTerms)
        ? result.matchedTerms
        : [];

      matchedTerms.slice(0, 5).forEach((term) => {
        const chip = document.createElement("span");
        chip.className = "term-chip";
        chip.textContent = safeString(term);

        terms.append(chip);
      });

      const open = document.createElement("button");
      open.className = "open-doc";
      open.textContent = "Open document ↗";

      open.addEventListener("click", () => {
        openDocument(docId);
      });

      foot.append(terms, open);

      card.append(head, path, snippet, foot);

      list.append(card);
    });
  }

  const hasPages = state.totalHits > state.limit;

  $("#pagination").classList.toggle(
    "hidden",
    !hasPages
  );

  const firstResult = state.totalHits
    ? state.offset + 1
    : 0;

  const lastResult = Math.min(
    state.offset + state.limit,
    state.totalHits
  );

  setText(
    "#pageSummary",
    `Showing ${firstResult}–${lastResult} of ${formatNumber(state.totalHits)}`
  );

  $("#prevPage").disabled = state.offset <= 0;

  $("#nextPage").disabled =
    state.offset + state.limit >= state.totalHits;
}

// --------------------------------------------------
// 9. SEARCH MODE AND RECENT SEARCHES
// --------------------------------------------------

function updateModeButtons() {
  $$(".mode-btn").forEach((button) => {
    button.classList.toggle(
      "active",
      button.dataset.mode === state.mode
    );
    button.setAttribute("aria-pressed", String(button.dataset.mode === state.mode));
  });
}

function renderRecent() {
  const box = $("#recentSearches");

  box.replaceChildren();

  if (!state.history.length) {
    const paragraph = document.createElement("p");
    paragraph.className = "muted tiny";
    paragraph.textContent =
      "Your searches will appear here.";

    box.append(paragraph);
    return;
  }

  state.history.forEach((query) => {
    const button = document.createElement("button");
    button.className = "recent-item";
    button.textContent = query;

    const arrow = document.createElement("span");
    arrow.textContent = "↗";

    button.append(arrow);

    button.addEventListener("click", () => {
      runSearch(query);
    });

    box.append(button);
  });
}

// --------------------------------------------------
// 10. DOCUMENT MODAL
// --------------------------------------------------

function closeDocument() {
  // Invalidate any pending document request.
  documentRequestId++;

  $("#documentModal").classList.add("hidden");

  state.currentDocument = "";

  if (
    lastDocumentTrigger &&
    document.contains(lastDocumentTrigger)
  ) {
    lastDocumentTrigger.focus();
  }

  lastDocumentTrigger = null;
}

async function openDocument(id) {
  const cleanId = safeString(id).trim();

  if (!cleanId) {
    toast("This result does not have a valid document ID.", "error");
    return;
  }

  const requestId = ++documentRequestId;

  lastDocumentTrigger = document.activeElement;

  state.currentDocument = "";

  setText("#documentTitle", "Loading document…");
  setText("#documentId", `Document ID: ${cleanId}`);
  setText("#documentBody", "Loading document content…");

  $("#documentModal").classList.remove("hidden");

  $("#closeDocument").focus();

  try {
    const doc = await getDocument(cleanId);

    if (requestId !== documentRequestId) return;

    if (!doc || typeof doc !== "object") {
      throw new Error(
        "The backend returned an invalid document."
      );
    }

    const title =
      safeString(doc.title) || `Document ${cleanId}`;

    setText("#documentTitle", title);

    setText(
      "#documentId",
      `Document ID: ${safeString(doc.docId, cleanId)}`
    );

    state.currentDocument = safeString(doc.content);

    setText(
      "#documentBody",
      state.currentDocument || "This document has no content."
    );

  } catch (error) {
    if (requestId !== documentRequestId) return;

    setText("#documentTitle", "Unable to open document");
    setText("#documentBody", error.message);

    toast(error.message, "error");
  }
}

// --------------------------------------------------
// 11. ANALYTICS
// --------------------------------------------------

function renderAnalytics() {
  const rows = state.activity;

  const successfulSearches = rows.filter(
    (row) =>
      row.status === "Results" ||
      row.status === "No results"
  );

  const averageLatency = successfulSearches.length
    ? successfulSearches.reduce(
        (sum, row) => sum + (Number(row.latency) || 0),
        0
      ) / successfulSearches.length
    : null;

  const zeroResults = rows.filter(
    (row) => row.status === "No results"
  ).length;

  const averageHits = successfulSearches.length
    ? successfulSearches.reduce(
        (sum, row) => sum + (Number(row.hits) || 0),
        0
      ) / successfulSearches.length
    : null;

  setText("#analyticsTotal", rows.length);

  setText(
    "#analyticsLatency",
    averageLatency === null
      ? "—"
      : `${averageLatency.toFixed(2)} ms`
  );

  setText("#analyticsZero", zeroResults);

  setText(
    "#analyticsHits",
    averageHits === null
      ? "—"
      : averageHits.toFixed(1)
  );

  // Latency chart
  const chart = $("#latencyChart");
  chart.replaceChildren();

  const latencyRows = successfulSearches
    .filter((row) => Number.isFinite(Number(row.latency)))
    .slice(0, 8)
    .reverse();

  if (!latencyRows.length) {
    const empty = document.createElement("div");
    empty.className = "chart-empty";
    empty.textContent =
      "Run a few searches to build your latency chart.";

    chart.append(empty);

  } else {
    const maximum = Math.max(
      ...latencyRows.map((row) => Number(row.latency)),
      1
    );

    latencyRows.forEach((row, index) => {
      const column = document.createElement("div");
      column.className = "bar-column";

      const value = document.createElement("b");
      value.textContent =
        `${Number(row.latency).toFixed(1)}ms`;

      const bar = document.createElement("i");

      bar.style.height =
        `${Math.max(
          5,
          (Number(row.latency) / maximum) * 105
        )}px`;

      const label = document.createElement("span");
      label.textContent = `Q${index + 1}`;

      column.append(value, bar, label);

      chart.append(column);
    });
  }

  // Popular queries
  const counts = new Map();

  rows.forEach((row) => {
    counts.set(
      row.query,
      (counts.get(row.query) || 0) + 1
    );
  });

  const popular = [...counts.entries()]
    .sort((a, b) => b[1] - a[1])
    .slice(0, 6);

  const popularBox = $("#popularQueries");
  popularBox.replaceChildren();

  if (!popular.length) {
    const empty = document.createElement("div");
    empty.className = "chart-empty";
    empty.textContent =
      "Your popular queries will appear here.";

    popularBox.append(empty);

  } else {
    const maximum = popular[0][1];

    popular.forEach(([query, count]) => {
      const row = document.createElement("div");
      row.className = "popular-row";

      const name = document.createElement("span");
      name.textContent = query;

      const number = document.createElement("b");
      number.textContent = `${count}×`;

      const track = document.createElement("div");
      track.className = "popular-track";

      const fill = document.createElement("i");
      fill.style.width = `${(count / maximum) * 100}%`;

      track.append(fill);
      row.append(name, number, track);

      popularBox.append(row);
    });
  }

  // Recent activity table
  const tbody = $("#activityRows");
  tbody.replaceChildren();

  if (!rows.length) {
    const tr = document.createElement("tr");
    const td = document.createElement("td");

    td.colSpan = 5;
    td.className = "table-empty";
    td.textContent = "No searches recorded yet.";

    tr.append(td);
    tbody.append(tr);

  } else {
    rows.slice(0, 20).forEach((row) => {
      const tr = document.createElement("tr");

      const values = [
        row.query,
        row.mode,
        formatNumber(row.hits),
        row.latency === null
          ? "—"
          : formatLatency(row.latency),
        row.status
      ];

      values.forEach((value, index) => {
        const td = document.createElement("td");

        if (index === 4) {
          const tag = document.createElement("span");

          tag.className =
            `status-tag ${
              row.status === "No results" ? "zero" : ""
            }`;

          tag.textContent = safeString(value);

          td.append(tag);

        } else {
          td.textContent = safeString(value);
        }

        tr.append(td);
      });

      tbody.append(tr);
    });
  }
}

// --------------------------------------------------
// 12. EXPORT ANALYTICS AS CSV
// --------------------------------------------------

function exportCSV() {
  if (!state.activity.length) {
    toast(
      "There is no session activity to export.",
      "error"
    );
    return;
  }

  const rows = [
    [
      "query",
      "mode",
      "hits",
      "latency_ms",
      "status",
      "timestamp"
    ],

    ...state.activity.map((row) => [
      row.query,
      row.mode,
      row.hits,
      row.latency ?? "",
      row.status,
      row.timestamp instanceof Date
        ? row.timestamp.toISOString()
        : ""
    ])
  ];

  const csv = rows
    .map((row) =>
      row
        .map((value) =>
          `"${String(value).replace(/"/g, '""')}"`
        )
        .join(",")
    )
    .join("\n");

  const blob = new Blob(
    [csv],
    { type: "text/csv;charset=utf-8;" }
  );

  const url = URL.createObjectURL(blob);

  const link = document.createElement("a");

  link.href = url;
  link.download = "minisearch-session-analytics.csv";

  document.body.append(link);
  link.click();
  link.remove();

  // Revoke after the browser has started the download.
  window.setTimeout(() => {
    URL.revokeObjectURL(url);
  }, 1000);

  toast("Analytics CSV exported.");
}

// --------------------------------------------------
// 13. EVENT LISTENERS
// --------------------------------------------------

// Landing page
$("#enterWorkspace").addEventListener("click", () => {
  showWorkspace("search");
});

$("#heroSearch").addEventListener("click", () => {
  showWorkspace("search");
});

$("#howLaunch").addEventListener("click", () => {
  showWorkspace("search");
});

$("#backLanding").addEventListener("click", showLanding);

// Workspace navigation
$("#sideHome").addEventListener("click", (event) => {
  event.preventDefault();
  switchView("search");
});

$$(".nav-item[data-view]").forEach((button) => {
  button.addEventListener("click", () => {
    switchView(button.dataset.view);
  });
});

$$("[data-goto]").forEach((button) => {
  button.addEventListener("click", () => {
    switchView(button.dataset.goto);
  });
});

// Search form
$("#searchForm").addEventListener("submit", (event) => {
  event.preventDefault();
  runSearch($("#queryInput").value);
});

$("#clearQuery").addEventListener("click", () => {
  $("#queryInput").value = "";
  state.query = "";
  state.results = [];
  state.totalHits = 0;
  state.offset = 0;
  state.lastSearch = null;
  state.suggestedQuery = "";
  state.originalQuery = "";
  $("#correctionBanner").classList.add("hidden");
  $("#pagination").classList.add("hidden");
  $("#resultsList").replaceChildren();
  setText("#resultCount", "Your results");
  setText("#resultMeta", "Enter a query to begin");
  $("#queryInput").focus();
});

$$(".mode-btn").forEach((button) => {
  button.addEventListener("click", () => {
    state.mode = button.dataset.mode;

    updateModeButtons();

    if (state.query) {
      runSearch(state.query);
    }
  });
});

$("#resultLimit").addEventListener("change", (event) => {
  const newLimit = Number(event.target.value);

  if (!Number.isInteger(newLimit) || newLimit < 1) {
    toast("Please choose a valid result limit.", "error");
    return;
  }

  state.limit = newLimit;

  if (state.query) {
    runSearch(state.query);
  }
});

$("#sortSelect").addEventListener("change", () => {
  if (state.lastSearch) {
    renderResults(state.lastSearch);
  }
});

$$(".query-chip").forEach((button) => {
  button.addEventListener("click", () => {
    runSearch(button.textContent);
  });
});

$("#loadExample").addEventListener("click", () => {
  runSearch("search engine");
});

// Pagination
$("#prevPage").addEventListener("click", () => {
  if (state.offset <= 0 || !state.query) return;

  runSearch(state.query, {
    offset: Math.max(0, state.offset - state.limit)
  });
});

$("#nextPage").addEventListener("click", () => {
  if (
    !state.query ||
    state.offset + state.limit >= state.totalHits
  ) {
    return;
  }

  runSearch(state.query, {
    offset: state.offset + state.limit
  });
});

// Search correction actions
$("#useSuggestion").addEventListener("click", () => {
  if (state.suggestedQuery) runSearch(state.suggestedQuery);
});
$("#useOriginal").addEventListener("click", () => {
  if (state.originalQuery) runSearch(state.originalQuery, { original: true });
});

// Recent searches
$("#clearHistory").addEventListener("click", () => {
  state.history = [];

  renderRecent();

  toast("Recent searches cleared.");
});

// API and index
$("#refreshStats").addEventListener("click", loadStats);
$("#recheckApi").addEventListener("click", checkApi);

// Copy CLI note
$("#copyCommand").addEventListener("click", async () => {
  try {
    await navigator.clipboard.writeText(
      "Use the index-build command documented by your backend project."
    );

    toast("Note copied.");

  } catch {
    toast(
      "Clipboard permission was blocked.",
      "error"
    );
  }
});

// Analytics
$("#exportAnalytics").addEventListener("click", exportCSV);

$("#clearAnalytics").addEventListener("click", () => {
  state.activity = [];

  renderAnalytics();

  toast("Session analytics cleared.");
});

// Document modal
$("#closeDocument").addEventListener("click", closeDocument);
$("#modalBackdrop").addEventListener("click", closeDocument);

$("#copyDocument").addEventListener("click", async () => {
  if (!state.currentDocument) {
    toast("No document content to copy.", "error");
    return;
  }

  try {
    await navigator.clipboard.writeText(
      state.currentDocument
    );

    toast("Document content copied.");

  } catch {
    toast(
      "Clipboard permission was blocked.",
      "error"
    );
  }
});

// Mobile navigation
$("#mobileMenu").addEventListener("click", () => {
  const sidebar = $("#sidebar");

  const isOpen = sidebar.classList.toggle("open");
  $("#sidebarBackdrop").classList.toggle("hidden", !isOpen);

  $("#mobileMenu").setAttribute(
    "aria-expanded",
    String(isOpen)
  );
});

$("#sidebarBackdrop").addEventListener("click", () => {
  $("#sidebar").classList.remove("open");
  $("#sidebarBackdrop").classList.add("hidden");
  $("#mobileMenu").setAttribute("aria-expanded", "false");
});

// Theme and workspace preferences
const storage = {
  get(key, fallback = "") { try { return localStorage.getItem(key) ?? fallback; } catch { return fallback; } },
  set(key, value) { try { localStorage.setItem(key, value); } catch { /* storage may be unavailable */ } }
};
const applyTheme = (dark) => {
  document.body.classList.toggle("dark", dark);
  storage.set("minisearch-theme", dark ? "dark" : "light");
  $("#themeToggle").setAttribute("aria-pressed", String(dark));
  setText("#accountThemeLabel", dark ? "Switch to light mode" : "Switch to dark mode");
};
applyTheme(storage.get("minisearch-theme") === "dark");
$("#themeToggle").addEventListener("click", () => applyTheme(!document.body.classList.contains("dark")));
$("#accountThemeToggle").addEventListener("click", () => {
  applyTheme(!document.body.classList.contains("dark"));
  closeAccountMenu();
});
const accountMenu = $("#accountMenu");
function closeAccountMenu() {
  accountMenu.classList.add("hidden");
  $("#accountMenuToggle").setAttribute("aria-expanded", "false");
}
$("#accountMenuToggle").addEventListener("click", () => {
  const opened = accountMenu.classList.toggle("hidden") === false;
  $("#accountMenuToggle").setAttribute("aria-expanded", String(opened));
});
$("#openWorkspaceSettings").addEventListener("click", () => {
  closeAccountMenu();
  const savedWorkspace = storage.get("minisearch-workspace", "MiniSearch workspace");
  const savedName = storage.get("minisearch-displayname", "MiniSearch user");
  $("#workspaceNameInput").value = savedWorkspace;
  $("#displayNameInput").value = savedName;
  $("#menuWorkspaceName").textContent = savedWorkspace;
  $("#sidebarWorkspaceName").textContent = savedWorkspace;
  $("#sidebarUserName").textContent = savedName;
  $("#sidebarAvatar").textContent = savedName.split(/\s+/).filter(Boolean).slice(0,2).map(x=>x[0].toUpperCase()).join("") || "MS";
  $("#workspaceSettingsModal").classList.remove("hidden");
  $("#workspaceNameInput").focus();
});
$("#workspaceSettingsForm").addEventListener("submit", (event) => {
  event.preventDefault();
  const workspace = $("#workspaceNameInput").value.trim();
  const displayName = $("#displayNameInput").value.trim();
  if (!workspace || !displayName) return;
  storage.set("minisearch-workspace", workspace);
  storage.set("minisearch-displayname", displayName);
  $("#menuWorkspaceName").textContent = workspace;
  $("#sidebarWorkspaceName").textContent = workspace;
  $("#sidebarUserName").textContent = displayName;
  $("#sidebarAvatar").textContent = displayName.split(/\s+/).filter(Boolean).slice(0,2).map(x=>x[0].toUpperCase()).join("") || "MS";
  $("#workspaceSettingsModal").classList.add("hidden");
  toast("Workspace preferences saved in this browser.");
});
const closeSettings = () => $("#workspaceSettingsModal").classList.add("hidden");
$("#closeWorkspaceSettings").addEventListener("click", closeSettings);
$("#cancelWorkspaceSettings").addEventListener("click", closeSettings);
$("#workspaceSettingsBackdrop").addEventListener("click", closeSettings);
const closeShortcuts = () => $("#shortcutsModal").classList.add("hidden");
$("#openShortcuts").addEventListener("click", () => { closeAccountMenu(); $("#shortcutsModal").classList.remove("hidden"); $("#doneShortcuts").focus(); });
$("#closeShortcuts").addEventListener("click", closeShortcuts);
$("#doneShortcuts").addEventListener("click", closeShortcuts);
$("#shortcutsBackdrop").addEventListener("click", closeShortcuts);
document.addEventListener("click", (event) => {
  if (!event.target.closest(".user-mini-wrap")) closeAccountMenu();
});

// Keyboard shortcuts
document.addEventListener("keydown", (event) => {
  if (
    (event.ctrlKey || event.metaKey) &&
    event.key.toLowerCase() === "k"
  ) {
    event.preventDefault();

    if (shell.classList.contains("hidden")) {
      showWorkspace("search");
    }

    $("#queryInput").focus();
  }

  if (event.key === "Escape") {
    if (!$("#documentModal").classList.contains("hidden")) {
      closeDocument();
    }

    $("#sidebar").classList.remove("open");
    $("#sidebarBackdrop").classList.add("hidden");
    $("#workspaceSettingsModal").classList.add("hidden");
    $("#shortcutsModal").classList.add("hidden");
    closeAccountMenu();

    $("#mobileMenu").setAttribute(
      "aria-expanded",
      "false"
    );
  }

  // Basic keyboard focus handling inside the document modal.
  if (
    event.key === "Tab" &&
    !$("#documentModal").classList.contains("hidden")
  ) {
    const modal = $("#documentModal");

    const focusable = [
      ...modal.querySelectorAll(
        'button:not([disabled]), a[href], input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])'
      )
    ].filter((element) => element.offsetParent !== null);

    if (!focusable.length) return;

    const first = focusable[0];
    const last = focusable[focusable.length - 1];

    if (event.shiftKey && document.activeElement === first) {
      event.preventDefault();
      last.focus();

    } else if (
      !event.shiftKey &&
      document.activeElement === last
    ) {
      event.preventDefault();
      first.focus();
    }
  }
});

// --------------------------------------------------
// 14. INITIALIZATION
// --------------------------------------------------

renderRecent();
updateModeButtons();
$("#sidebarUserName").textContent = storage.get("minisearch-displayname", "MiniSearch user");
$("#sidebarWorkspaceName").textContent = storage.get("minisearch-workspace", "MiniSearch workspace");
$("#menuWorkspaceName").textContent = storage.get("minisearch-workspace", "MiniSearch workspace");
$("#mobileMenu").setAttribute("aria-expanded", "false");
