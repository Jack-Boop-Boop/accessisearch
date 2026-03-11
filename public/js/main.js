/* ============================================================
   AccessiSearch — Frontend JavaScript
   ============================================================ */
(function () {
  "use strict";

  /* ---- Constants ---- */
  var CATEGORY_IDS = [
    "simplified_language", "dyslexia_friendly", "low_vision",
    "screen_reader", "motor_keyboard", "deaf_hoh",
    "color_blindness", "cognitive_load"
  ];

  var CATEGORY_NAMES = {
    simplified_language: "Simplified Language",
    dyslexia_friendly: "Dyslexia-Friendly",
    low_vision: "Low Vision",
    screen_reader: "Screen Reader Friendly",
    motor_keyboard: "Motor / Keyboard-Only",
    deaf_hoh: "Deaf / Hard of Hearing",
    color_blindness: "Color Blindness",
    cognitive_load: "Cognitive Load"
  };

  var CATEGORY_INFO = {
    simplified_language: {
      title: "Simplified Language",
      text: "Evaluates whether pages use short sentences, common words, and well-structured paragraphs. Helpful for people with cognitive disabilities, non-native speakers, or anyone who benefits from plain language."
    },
    dyslexia_friendly: {
      title: "Dyslexia-Friendly",
      text: "Checks for sans-serif fonts, adequate line spacing, shorter paragraphs, and avoidance of justified text. These features make text easier to track for people with dyslexia."
    },
    low_vision: {
      title: "Low Vision",
      text: "Looks for relative font units (rem/em), zoom support, high-contrast CSS, and appropriately sized touch targets. Important for users who rely on magnification or large text."
    },
    screen_reader: {
      title: "Screen Reader Friendly",
      text: "Checks for image alt text, ARIA landmarks, heading hierarchy, skip links, form labels, and language attributes. Essential for blind or visually impaired users who navigate with screen readers."
    },
    motor_keyboard: {
      title: "Motor / Keyboard-Only",
      text: "Evaluates keyboard navigability, skip navigation links, visible focus indicators, zoom support, and absence of drag-only interactions. Critical for users who cannot use a mouse."
    },
    deaf_hoh: {
      title: "Deaf / Hard of Hearing",
      text: "Checks for video captions, audio transcripts, autoplay prevention, and embedded media accessibility. Important for deaf or hard-of-hearing users who need text alternatives to audio."
    },
    color_blindness: {
      title: "Color Blindness",
      text: "Evaluates whether links have underlines, forms use non-color error indicators, and information is conveyed through text labels rather than color alone. Affects roughly 8% of males and 0.5% of females."
    },
    cognitive_load: {
      title: "Cognitive Load",
      text: "Assesses readability, navigation clarity, heading structure, semantic HTML layout, and absence of auto-refresh. Helps users with ADHD, autism, or other cognitive differences."
    }
  };

  /* ---- DOM References ---- */
  var dom = {
    searchForm: document.getElementById("search-form"),
    searchInput: document.getElementById("main-search"),
    btnSearch: document.getElementById("btn-search"),
    filterAll: document.getElementById("filter-all"),
    resultsList: document.getElementById("results-list"),
    resultsStatus: document.getElementById("results-status"),
    loadingIndicator: document.getElementById("loading-indicator"),
    noResults: document.getElementById("no-results"),
    welcomeMessage: document.getElementById("welcome-message"),
    btnFontDecrease: document.getElementById("btn-font-decrease"),
    btnFontIncrease: document.getElementById("btn-font-increase"),
    btnContrast: document.getElementById("btn-contrast"),
    btnSpacing: document.getElementById("btn-spacing")
  };

  /* ---- State ---- */
  var state = {
    fontScale: parseFloat(localStorage.getItem("as-font-scale")) || 1,
    highContrast: localStorage.getItem("as-high-contrast") === "true",
    spacing: localStorage.getItem("as-spacing") === "true",
    lastResults: null
  };

  /* ============================================================
     Accessibility Controls
     ============================================================ */
  function applyFontScale() {
    document.documentElement.style.setProperty("--font-scale", state.fontScale);
    localStorage.setItem("as-font-scale", state.fontScale);
  }

  function applyContrast() {
    document.body.classList.toggle("high-contrast", state.highContrast);
    dom.btnContrast.setAttribute("aria-pressed", state.highContrast);
    localStorage.setItem("as-high-contrast", state.highContrast);
  }

  function applySpacing() {
    var scale = state.spacing ? 1.6 : 1;
    document.documentElement.style.setProperty("--spacing-scale", scale);
    dom.btnSpacing.setAttribute("aria-pressed", state.spacing);
    localStorage.setItem("as-spacing", state.spacing);
  }

  function initA11yControls() {
    applyFontScale();
    applyContrast();
    applySpacing();

    dom.btnFontDecrease.addEventListener("click", function () {
      state.fontScale = Math.max(0.75, state.fontScale - 0.1);
      applyFontScale();
    });
    dom.btnFontIncrease.addEventListener("click", function () {
      state.fontScale = Math.min(2, state.fontScale + 0.1);
      applyFontScale();
    });
    dom.btnContrast.addEventListener("click", function () {
      state.highContrast = !state.highContrast;
      applyContrast();
    });
    dom.btnSpacing.addEventListener("click", function () {
      state.spacing = !state.spacing;
      applySpacing();
    });
  }

  /* ============================================================
     Filter Logic
     ============================================================ */
  function getFilterCheckboxes() {
    return CATEGORY_IDS.map(function (id) {
      return document.getElementById("filter-" + id);
    }).filter(Boolean);
  }

  function getActiveFilters() {
    if (dom.filterAll.checked) return ["all"];
    var active = [];
    getFilterCheckboxes().forEach(function (cb) {
      if (cb.checked) active.push(cb.value);
    });
    return active.length > 0 ? active : ["all"];
  }

  function initFilters() {
    var categoryCheckboxes = getFilterCheckboxes();

    dom.filterAll.addEventListener("change", function () {
      if (dom.filterAll.checked) {
        categoryCheckboxes.forEach(function (cb) { cb.checked = false; });
      }
      onFiltersChanged();
    });

    categoryCheckboxes.forEach(function (cb) {
      cb.addEventListener("change", function () {
        var anyChecked = categoryCheckboxes.some(function (c) { return c.checked; });
        dom.filterAll.checked = !anyChecked;
        onFiltersChanged();
      });
    });
  }

  function onFiltersChanged() {
    if (state.lastResults) {
      resortAndRender(state.lastResults);
    }
  }

  /* ============================================================
     Info Tooltips
     ============================================================ */
  function initTooltips() {
    document.querySelectorAll(".info-btn").forEach(function (btn) {
      btn.addEventListener("click", function (e) {
        e.stopPropagation();
        var category = btn.getAttribute("data-category");
        toggleTooltip(btn, category);
      });
    });

    document.addEventListener("click", function () { closeAllTooltips(); });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape") closeAllTooltips();
    });
  }

  function toggleTooltip(btn, category) {
    var existing = btn.parentElement.querySelector(".info-tooltip");
    var wasOpen = existing && existing.classList.contains("open");

    closeAllTooltips();

    if (wasOpen) return;

    var info = CATEGORY_INFO[category];
    if (!info) return;

    var tip = document.createElement("div");
    tip.className = "info-tooltip open";
    tip.setAttribute("role", "tooltip");
    tip.innerHTML = "<strong>" + escapeHtml(info.title) + "</strong><p>" + escapeHtml(info.text) + "</p>";
    btn.parentElement.appendChild(tip);
    btn.setAttribute("aria-expanded", "true");
  }

  function closeAllTooltips() {
    document.querySelectorAll(".info-tooltip").forEach(function (tip) { tip.remove(); });
    document.querySelectorAll(".info-btn").forEach(function (btn) {
      btn.setAttribute("aria-expanded", "false");
    });
  }

  /* ============================================================
     Search
     ============================================================ */
  function initSearch() {
    dom.searchForm.addEventListener("submit", function (e) {
      e.preventDefault();
      performSearch();
    });
  }

  function performSearch() {
    var query = dom.searchInput.value.trim();
    if (!query) {
      dom.searchInput.focus();
      return;
    }

    var filters = getActiveFilters();
    var filterParam = filters.join(",");
    var url = "/api/search?q=" + encodeURIComponent(query) + "&filters=" + encodeURIComponent(filterParam);

    showLoading();

    fetch(url)
      .then(function (resp) {
        if (!resp.ok) throw new Error("Search failed: " + resp.status);
        return resp.json();
      })
      .then(function (data) {
        state.lastResults = data.results || [];
        hideLoading();

        if (state.lastResults.length === 0) {
          showNoResults();
        } else {
          renderResults(state.lastResults);
          dom.resultsStatus.textContent = state.lastResults.length + " results found for \"" + data.query + "\"";
        }
      })
      .catch(function (err) {
        hideLoading();
        dom.resultsStatus.textContent = "Search error. Please check your API keys are configured and try again.";
        console.error("Search error:", err);
      });
  }

  /* ============================================================
     UI State Helpers
     ============================================================ */
  function showLoading() {
    dom.loadingIndicator.hidden = false;
    dom.resultsList.innerHTML = "";
    dom.noResults.hidden = true;
    dom.welcomeMessage.hidden = true;
    dom.resultsStatus.textContent = "Searching and analyzing pages...";
  }

  function hideLoading() {
    dom.loadingIndicator.hidden = true;
  }

  function showNoResults() {
    dom.noResults.hidden = false;
    dom.resultsList.innerHTML = "";
    dom.resultsStatus.textContent = "No results found.";
  }

  /* ============================================================
     Resort & Render
     ============================================================ */
  function resortAndRender(results) {
    var filters = getActiveFilters();
    results.forEach(function (r) {
      if (r.scores) {
        r.overall_score = computeOverallScore(r.scores, filters);
      }
    });
    results.sort(function (a, b) { return (b.overall_score || 0) - (a.overall_score || 0); });
    renderResults(results);
  }

  function computeOverallScore(scores, activeFilters) {
    var cats;
    if (activeFilters.indexOf("all") !== -1) {
      cats = CATEGORY_IDS;
    } else {
      cats = activeFilters.filter(function (f) { return CATEGORY_IDS.indexOf(f) !== -1; });
    }
    if (cats.length === 0) return 5.0;
    var total = cats.reduce(function (sum, cat) {
      var s = scores[cat] ? scores[cat].score : 5.0;
      return sum + s;
    }, 0);
    return Math.round((total / cats.length) * 10) / 10;
  }

  /* ============================================================
     Render Results
     ============================================================ */
  function renderResults(results) {
    dom.resultsList.innerHTML = "";
    dom.noResults.hidden = true;
    dom.welcomeMessage.hidden = true;

    results.forEach(function (r) {
      dom.resultsList.appendChild(buildResultCard(r));
    });
  }

  function buildResultCard(result) {
    var li = document.createElement("li");
    li.className = "result-card";

    var overall = result.overall_score || 0;
    var level = getScoreLevel(overall);
    var barColor = getScoreColor(level);

    var activeFilters = getActiveFilters();
    var displayCategories;
    if (activeFilters.indexOf("all") !== -1) {
      displayCategories = CATEGORY_IDS;
    } else {
      displayCategories = activeFilters.filter(function (f) { return CATEGORY_IDS.indexOf(f) !== -1; });
    }

    var breakdownHtml = "";
    if (result.scores) {
      breakdownHtml = displayCategories.map(function (cat) {
        var catData = result.scores[cat];
        if (!catData) return "";
        var catLevel = getScoreLevel(catData.score);
        var catColor = getScoreColor(catLevel);
        var detailsHtml = "";
        if (catData.details && catData.details.length > 0) {
          detailsHtml = '<ul class="score-detail-list">' +
            catData.details.map(function (d) {
              return "<li>" + escapeHtml(d) + "</li>";
            }).join("") + "</ul>";
        }
        return '<li>' +
          '<span class="category-name">' + escapeHtml(CATEGORY_NAMES[cat] || cat) + '</span>' +
          '<span class="score-bar-container"><span class="score-bar-fill" style="width:' + (catData.score * 10) + '%;background:' + catColor + '"></span></span>' +
          '<span class="score-value" data-level="' + catLevel + '">' + catData.score.toFixed(1) + '</span>' +
          detailsHtml +
          '</li>';
      }).join("");
    }

    var statusClass = "status-complete";
    var statusText = "Analyzed";
    if (result.analysis_status === "failed") {
      statusClass = "status-failed";
      statusText = "Fetch Failed";
    } else if (result.analysis_status === "error") {
      statusClass = "status-error";
      statusText = "Error";
    }

    li.innerHTML =
      '<div class="result-header">' +
        '<h3 class="result-title"><a href="' + escapeAttr(result.link) + '" target="_blank" rel="noopener">' + escapeHtml(result.title) + '</a></h3>' +
        '<p class="result-url">' + escapeHtml(result.display_link || result.link) + '</p>' +
      '</div>' +
      '<p class="result-snippet">' + escapeHtml(result.snippet) + '</p>' +
      '<div class="score-section">' +
        '<div class="overall-score">' +
          '<span class="score-label">Accessibility Score</span>' +
          '<span class="score-bar-container"><span class="score-bar-fill" style="width:' + (overall * 10) + '%;background:' + barColor + '"></span></span>' +
          '<span class="score-value" data-level="' + level + '">' + overall.toFixed(1) + '</span>' +
        '</div>' +
        '<details class="score-breakdown">' +
          '<summary>Score breakdown (' + displayCategories.length + ' categories)</summary>' +
          '<ul class="score-list">' + breakdownHtml + '</ul>' +
        '</details>' +
      '</div>' +
      '<div class="analysis-status">' +
        '<span class="status-badge ' + statusClass + '">' + statusText + '</span>' +
      '</div>';

    return li;
  }

  /* ============================================================
     Helpers
     ============================================================ */
  function getScoreLevel(score) {
    if (score >= 7) return "high";
    if (score >= 4) return "mid";
    return "low";
  }

  function getScoreColor(level) {
    if (level === "high") return "var(--color-score-high)";
    if (level === "mid") return "var(--color-score-mid)";
    return "var(--color-score-low)";
  }

  function escapeHtml(str) {
    if (!str) return "";
    return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
  }

  function escapeAttr(str) {
    if (!str) return "";
    return str.replace(/&/g, "&amp;").replace(/"/g, "&quot;").replace(/'/g, "&#39;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  }

  /* ============================================================
     Init
     ============================================================ */
  function init() {
    initA11yControls();
    initFilters();
    initTooltips();
    initSearch();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
